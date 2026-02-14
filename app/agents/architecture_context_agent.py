"""Architecture Context Agent — system classification and invariant detection."""

import json
import logging
from typing import Any

from app.agents.llm_config import get_chat_model
from app.agents.prompts import ARCH_CONTEXT_SYSTEM
from app.agents.utils import run_json_prompt

logger = logging.getLogger(__name__)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields exist and enforce schema."""
    return {
        "system_class": raw.get("system_class") or "",
        "primary_patterns": (
            raw["primary_patterns"]
            if isinstance(raw.get("primary_patterns"), list)
            else []
        ),
        "required_subsystems": (
            raw["required_subsystems"]
            if isinstance(raw.get("required_subsystems"), list)
            else []
        ),
        "assumptions": (
            raw["assumptions"]
            if isinstance(raw.get("assumptions"), list)
            else []
        ),
        "missing_signals": (
            raw["missing_signals"]
            if isinstance(raw.get("missing_signals"), list)
            else []
        ),
        "confidence": max(
            0.0,
            min(1.0, float(raw.get("confidence", raw.get("overall_confidence", 0)))),
        ),
    }


def run_architecture_context(
    structured_project_context: dict[str, Any],
    ingestion_confidence: float = 0.0,    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Classify system and identify architectural invariants.

    Inputs:
        structured_project_context: Output from Input Ingestion Agent
        ingestion_confidence: Confidence from upstream (0–1)

    Outputs:
        system_class, primary_patterns, required_subsystems,
        assumptions, missing_signals, confidence
    """
    logger.info(
        "ArchitectureContextAgent:start ingestion_confidence=%.2f",
        ingestion_confidence,
    )

    if not structured_project_context:
        logger.warning("ArchitectureContextAgent:empty_context")
        return {
            "agent_name": "architecture_context",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({
                "missing_signals": ["structured_project_context"],
                "confidence": 0.0,
            }),
            "assumptions": [],
            "flags": ["No structured project context provided."],
            "errors": ["structured_project_context is required."],
        }

    user_prompt = f"""Classify the system and identify architectural invariants from this structured project context.

## Structured Project Context
```json
{json.dumps(structured_project_context, indent=2)}
```

## Upstream Confidence
{ingestion_confidence:.2f}

Return JSON with: system_class, primary_patterns, required_subsystems, assumptions, missing_signals, confidence."""

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, ARCH_CONTEXT_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("ArchitectureContextAgent:parse_error %s", e)
        return {
            "agent_name": "architecture_context",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({"confidence": 0.0}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("ArchitectureContextAgent:error")
        return {
            "agent_name": "architecture_context",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({"confidence": 0.0}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    confidence = output["confidence"]
    missing = output.get("missing_signals", [])

    if missing and confidence < 0.7:
        status = "needs_clarification"
        logger.info("ArchitectureContextAgent:needs_clarification missing=%s", missing)
    else:
        status = "success"
        logger.info("ArchitectureContextAgent:success confidence=%.2f", confidence)

    return {
        "agent_name": "architecture_context",
        "status": status,
        "confidence": confidence,
        "output": output,
        "assumptions": output.get("assumptions", []),
        "flags": missing,
        "errors": [],
    }
