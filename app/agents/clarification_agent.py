"""Clarification Agent — risk-based questioning, human-in-the-loop."""

import json
import logging
from typing import Any

from app.agents.langfuse_integration import observe
from app.agents.llm_config import get_chat_model
from app.agents.prompts import CLARIFICATION_SYSTEM
from app.agents.utils import build_clarification_context, run_json_prompt

logger = logging.getLogger(__name__)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields and options exist."""
    questions = raw.get("questions")
    if not isinstance(questions, list):
        questions = []
    validated = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict) or not q.get("question"):
            continue
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) < 2:
            opts = [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}]
        answer_type = q.get("answer_type", "single")
        if answer_type not in ("single", "multiple", "boolean"):
            answer_type = "single"
        validated.append({
            "id": q.get("id") or f"q{i + 1}",
            "question": q["question"],
            "risk_addressed": q.get("risk_addressed", ""),
            "blocking": bool(q.get("blocking", True)),
            "answer_type": answer_type,
            "options": [{"id": o.get("id", str(j)), "label": o.get("label", str(o))} for j, o in enumerate(opts) if isinstance(o, dict)],
        })
    return {
        "questions": validated,
        "risk_reduction_estimate": max(0.0, min(1.0, float(raw.get("risk_reduction_estimate", 0)))),
        "residual_risk_estimate": max(0.0, min(1.0, float(raw.get("residual_risk_estimate", 0)))),
        "ready_to_proceed": bool(raw.get("ready_to_proceed", False)),
    }


@observe()
def run_clarification(
    ingestion_output: dict[str, Any],
    arch_output: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate risk-based clarification questions from Ingestion + Architecture outputs.

    Inputs:
        ingestion_output: Output from Input Ingestion Agent
        arch_output: Output from Architecture Context Agent

    Outputs:
        questions, risk_reduction_estimate, residual_risk_estimate, ready_to_proceed
    """
    logger.info("ClarificationAgent:start")

    if not ingestion_output or not arch_output:
        logger.warning("ClarificationAgent:missing_upstream")
        return {
            "agent_name": "clarification",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({"ready_to_proceed": False}),
            "assumptions": [],
            "flags": ["Missing ingestion or architecture output"],
            "errors": ["Upstream outputs required."],
        }

    ctx = build_clarification_context(ingestion_output, arch_output)
    user_prompt = f"""## Context from Ingestion + Architecture

```json
{json.dumps(ctx, indent=2)}
```

Compare assumptions vs evidence. Identify which missing_signals create irreversible risk.
Generate minimum necessary questions. Group logically. Stop when residual risk ≤ threshold."""

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, CLARIFICATION_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("ClarificationAgent:parse_error %s", e)
        return {
            "agent_name": "clarification",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("ClarificationAgent:error")
        return {
            "agent_name": "clarification",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    ready = output["ready_to_proceed"]
    questions = output["questions"]
    has_blocking = any(q.get("blocking") for q in questions)

    if ready and not questions:
        status = "success"
        logger.info("ClarificationAgent:success no_questions_needed")
    elif has_blocking or questions:
        status = "needs_clarification"
        logger.info("ClarificationAgent:needs_clarification questions=%d", len(questions))
    else:
        status = "success"
        logger.info("ClarificationAgent:success")

    return {
        "agent_name": "clarification",
        "status": status,
        "confidence": 1.0 - output["residual_risk_estimate"],
        "output": output,
        "assumptions": [],
        "flags": [q["risk_addressed"] for q in questions if q.get("risk_addressed")],
        "errors": [],
    }
