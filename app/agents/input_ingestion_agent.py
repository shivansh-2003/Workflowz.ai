"""Input Ingestion Agent — context gatekeeper for the AI system."""

import logging
import re
from typing import Any

from app.agents.llm_config import get_chat_model
from app.agents.prompts import INPUT_INGESTION_SYSTEM
from app.agents.utils import run_json_prompt

logger = logging.getLogger(__name__)

# Vagueness thresholds per design
THRESHOLD_SAFE = 0.7
THRESHOLD_CLARIFY = 0.4

# Signals that suggest high-quality structured input
STRUCTURED_SECTION_PATTERNS = [
    r"#{1,3}\s*(overview|architecture|requirements|features|getting started)",
    r"#{1,3}\s*(design|setup|installation|usage)",
    r"\*\*[^*]+\*\*:",
    r"^\s*-\s+.+",
    r"^\s*\d+\.\s+.+",
    r"\|.+\|",
]


def _is_structured_input(text: str) -> tuple[bool, float]:
    """Detect if input appears to be well-structured (README, PRD, etc.)."""
    if not text or not text.strip():
        return False, 0.0
    text_lower = text.lower()
    matches = 0
    for pattern in STRUCTURED_SECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
            matches += 1
    # More patterns matched = higher structure confidence
    density = min(1.0, matches / len(STRUCTURED_SECTION_PATTERNS) * 2)
    return matches >= 2, density


def _build_user_prompt(
    project_name: str,
    text_description: str | None,
    markdown_content: str | None,
) -> str:
    """Build the user prompt from available inputs."""
    parts = []
    if project_name:
        parts.append(f"## Project Name\n{project_name}")
    if text_description:
        parts.append(f"## Text Description\n{text_description}")
    if markdown_content:
        parts.append(f"## Markdown / Document Content\n{markdown_content}")
    if not parts:
        return "No project name, description, or markdown provided."
    return "\n\n".join(parts)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields exist and enforce schema."""
    core = {
        "project_goal": raw.get("project_goal") or "",
        "primary_users": raw.get("primary_users") if isinstance(raw.get("primary_users"), list) else [],
        "system_type": raw.get("system_type") or "",
        "core_domains": raw.get("core_domains") if isinstance(raw.get("core_domains"), list) else [],
        "constraints": raw.get("constraints") if isinstance(raw.get("constraints"), list) else [],
        "assumptions": raw.get("assumptions") if isinstance(raw.get("assumptions"), list) else [],
        "non_goals": raw.get("non_goals") if isinstance(raw.get("non_goals"), list) else [],
        "features": raw.get("features") if isinstance(raw.get("features"), list) else [],
    }
    confidence = float(raw.get("overall_confidence", raw.get("confidence", 0)))
    core["overall_confidence"] = max(0.0, min(1.0, confidence))
    core["too_vague"] = bool(raw.get("too_vague", False))
    core["block_message"] = raw.get("block_message") or ""
    core["needs_clarification"] = bool(raw.get("needs_clarification", False))
    core["missing_signals"] = raw.get("missing_signals") if isinstance(raw.get("missing_signals"), list) else []

    # Preserve structure metadata if present
    if raw.get("source"):
        core["source"] = raw["source"]
    if "structure_confidence" in raw:
        core["structure_confidence"] = raw["structure_confidence"]
    if raw.get("mapped_sections"):
        core["mapped_sections"] = raw["mapped_sections"]
    if raw.get("agent_notes"):
        core["agent_notes"] = raw["agent_notes"]

    # Flexible extensions
    for key in ("ai_components", "integrations", "regulatory_constraints", "non_functional_requirements"):
        if key in raw and raw[key]:
            core[key] = raw[key]

    return core


def run_input_ingestion(
    project_name: str = "",
    text_description: str | None = None,
    markdown_content: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Normalize messy human input into clean structured context.

    Inputs:
        project_name: Project name
        text_description: Plain text or short description
        markdown_content: README, PRD, architecture doc, etc.

    Outputs:
        Structured context with goals, features, constraints, non-goals,
        confidence scores, and block/clarify flags.
    """
    logger.info("InputIngestionAgent:start project_name=%s", project_name or "(none)")

    combined = (text_description or "") + "\n\n" + (markdown_content or "")
    is_structured, structure_density = _is_structured_input(combined)

    user_prompt = _build_user_prompt(project_name, text_description, markdown_content)
    if not user_prompt.strip() or user_prompt == "No project name, description, or markdown provided.":
        logger.warning("InputIngestionAgent:no_input")
        return {
            "agent_name": "input_ingestion",
            "status": "blocked",
            "overall_confidence": 0.0,
            "output": _normalize_output({
                "too_vague": True,
                "block_message": "This description is too vague to infer architecture.",
                "missing_signals": ["project description", "markdown content"],
            }),
            "assumptions": [],
            "flags": [],
            "errors": ["No project description or markdown provided."],
        }

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, INPUT_INGESTION_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("InputIngestionAgent:parse_error %s", e)
        return {
            "agent_name": "input_ingestion",
            "status": "failed",
            "overall_confidence": 0.0,
            "output": _normalize_output({"too_vague": True, "block_message": str(e)}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("InputIngestionAgent:error")
        return {
            "agent_name": "input_ingestion",
            "status": "failed",
            "overall_confidence": 0.0,
            "output": _normalize_output({"too_vague": True, "block_message": str(e)}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    confidence = output.get("overall_confidence", 0.0)

    if output.get("too_vague") or confidence < THRESHOLD_CLARIFY:
        status = "blocked"
        logger.info("InputIngestionAgent:blocked confidence=%.2f", confidence)
    elif confidence < THRESHOLD_SAFE:
        status = "needs_clarification"
        output["needs_clarification"] = True
        logger.info("InputIngestionAgent:needs_clarification confidence=%.2f", confidence)
    else:
        status = "success"
        logger.info("InputIngestionAgent:success confidence=%.2f", confidence)

    return {
        "agent_name": "input_ingestion",
        "status": status,
        "overall_confidence": confidence,
        "output": output,
        "assumptions": output.get("assumptions", []),
        "flags": output.get("missing_signals", []),
        "errors": [],
    }
