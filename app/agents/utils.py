"""Shared utilities for agents."""

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage


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
