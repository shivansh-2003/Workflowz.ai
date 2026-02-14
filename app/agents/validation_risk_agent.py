"""Validation & Risk Agent — independent AI auditor for plan review."""

import json
import logging
from typing import Any

from app.agents.langfuse_integration import observe
from app.agents.llm_config import get_chat_model
from app.agents.prompts import VALIDATION_RISK_SYSTEM
from app.agents.utils import run_json_prompt

logger = logging.getLogger(__name__)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields for risk report."""
    risk_score = raw.get("risk_score", 0)
    if not isinstance(risk_score, (int, float)):
        risk_score = 0
    risk_score = max(0, min(100, int(risk_score)))
    
    risk_level = raw.get("risk_level", "low")
    if risk_level not in ("low", "medium", "high"):
        if risk_score <= 30:
            risk_level = "low"
        elif risk_score <= 60:
            risk_level = "medium"
        else:
            risk_level = "high"
    
    top_risks = raw.get("top_risks")
    if not isinstance(top_risks, list):
        top_risks = []
    top_risks = [str(r) for r in top_risks if r][:5]  # Max 5 risks
    
    blocking_issues = raw.get("blocking_issues")
    if not isinstance(blocking_issues, list):
        blocking_issues = []
    blocking_issues = [str(b) for b in blocking_issues if b]
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "top_risks": top_risks,
        "blocking_issues": blocking_issues,
    }


@observe()
def run_validation_risk(
    architecture_context: dict[str, Any],
    task_groups: list[dict[str, Any]],
    matching_output: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Independent audit of the plan — validate feasibility and flag risks.

    Inputs:
        architecture_context: Output from Architecture Context Agent
        task_groups: Output from Task Decomposition Agent
        matching_output: Output from Role → Task Matching Agent (assignments, unassigned, warnings)

    Outputs:
        risk_score, risk_level, top_risks, blocking_issues
    """
    logger.info("ValidationRiskAgent:start")

    if not architecture_context or not task_groups or not matching_output:
        logger.warning("ValidationRiskAgent:missing_input")
        return {
            "agent_name": "validation_risk",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({"risk_score": 100, "risk_level": "high", "top_risks": ["Missing required inputs"], "blocking_issues": ["Cannot perform validation without complete inputs"]}),
            "assumptions": [],
            "flags": ["Missing architecture_context, task_groups, or matching_output"],
            "errors": ["All inputs are required for validation."],
        }

    # Flatten tasks for easier analysis
    all_tasks = []
    for grp in task_groups:
        tasks = grp.get("tasks", [])
        for t in tasks:
            all_tasks.append({
                "task_id": t.get("task_id"),
                "description": t.get("description"),
                "required_capability": t.get("required_capability"),
                "status": t.get("status"),
                "domain": grp.get("domain"),
            })

    user_prompt = f"""Perform independent audit of the project plan.

## Architecture Context
```json
{json.dumps(architecture_context, indent=2)}
```

## All Tasks ({len(all_tasks)} total)
```json
{json.dumps(all_tasks, indent=2)}
```

## Task Assignments & Matching Results
```json
{json.dumps(matching_output, indent=2)}
```

Validate architectural completeness, task feasibility, capability gaps, load imbalance, and security/workflow invariants.
Calculate risk score (0-100) and identify top risks. Flag blocking issues if critical problems exist.

Return JSON with: risk_score, risk_level, top_risks, blocking_issues."""

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, VALIDATION_RISK_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("ValidationRiskAgent:parse_error %s", e)
        return {
            "agent_name": "validation_risk",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({"risk_score": 100, "risk_level": "high", "top_risks": ["Failed to generate risk report"], "blocking_issues": []}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("ValidationRiskAgent:error")
        return {
            "agent_name": "validation_risk",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({"risk_score": 100, "risk_level": "high", "top_risks": ["Failed to generate risk report"], "blocking_issues": []}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    risk_score = output["risk_score"]
    risk_level = output["risk_level"]
    top_risks = output.get("top_risks", [])
    blocking_issues = output.get("blocking_issues", [])

    # Determine status based on blocking issues
    if blocking_issues:
        status = "blocked"
        confidence = 0.0
    elif risk_level == "high":
        status = "needs_clarification"
        confidence = 0.4
    elif risk_level == "medium":
        status = "success"
        confidence = 0.7
    else:  # low
        status = "success"
        confidence = 0.9

    logger.info(
        "ValidationRiskAgent:%s risk_score=%d risk_level=%s blocking=%d",
        status,
        risk_score,
        risk_level,
        len(blocking_issues),
    )

    flags = []
    if blocking_issues:
        flags.append(f"{len(blocking_issues)} blocking issues found")
    if top_risks:
        flags.append(f"{len(top_risks)} risks identified")

    return {
        "agent_name": "validation_risk",
        "status": status,
        "confidence": confidence,
        "output": output,
        "assumptions": [],
        "flags": flags,
        "errors": [],
    }
