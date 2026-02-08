"""Shared utilities for agents."""

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage


def build_clarification_context(
    ingestion_output: dict[str, Any],
    arch_output: dict[str, Any],
) -> dict[str, Any]:
    """Build context for Clarification Agent from Ingestion + Architecture outputs."""
    ing_assumptions = ingestion_output.get("assumptions") or []
    arch_assumptions = arch_output.get("assumptions") or []
    ing_missing = ingestion_output.get("missing_signals") or []
    arch_missing = arch_output.get("missing_signals") or []
    ing_conf = float(ingestion_output.get("overall_confidence", ingestion_output.get("confidence", 0)))
    arch_conf = float(arch_output.get("confidence", 0))
    return {
        "assumptions": list(dict.fromkeys(ing_assumptions + arch_assumptions)),
        "missing_signals": list(dict.fromkeys(ing_missing + arch_missing)),
        "ingestion_confidence": ing_conf,
        "architecture_confidence": arch_conf,
        "current_confidence": min(ing_conf, arch_conf),
    }


def extract_json(text: str) -> dict[str, Any]:
    """Extract first JSON object from text."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    payload = text[start : end + 1]
    return json.loads(payload)


def run_json_prompt(
    model: Any,
    system_prompt: str,
    user_prompt: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Invoke model and parse response as JSON."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    invoke_kw: dict[str, Any] = {}
    if config:
        invoke_kw["config"] = config
    response = model.invoke(messages, **invoke_kw)
    return extract_json(response.content)
