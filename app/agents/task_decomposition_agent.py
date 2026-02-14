"""Task Decomposition Agent — constraint-aware, team-realistic task generation."""

import json
import logging
from typing import Any

from app.agents.langfuse_integration import observe
from app.agents.llm_config import get_chat_model
from app.agents.prompts import TASK_DECOMPOSITION_SYSTEM
from app.agents.utils import run_json_prompt

logger = logging.getLogger(__name__)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields and task structure."""
    task_groups = raw.get("task_groups")
    if not isinstance(task_groups, list):
        task_groups = []
    
    validated_groups = []
    for grp in task_groups:
        if not isinstance(grp, dict):
            continue
        tasks = grp.get("tasks")
        if not isinstance(tasks, list):
            tasks = []
        validated_tasks = []
        for i, t in enumerate(tasks):
            if not isinstance(t, dict):
                continue
            validated_tasks.append({
                "task_id": t.get("task_id") or f"task_{i+1}",
                "description": t.get("description") or "",
                "required_capability": t.get("required_capability") or "backend",
                "status": t.get("status") if t.get("status") in ("ready", "adapted", "blocked") else "ready",
                "assumption": t.get("assumption") or "",
            })
        validated_groups.append({
            "domain": grp.get("domain") or "general",
            "tasks": validated_tasks,
        })
    
    return {
        "task_groups": validated_groups,
        "confidence": max(0.0, min(1.0, float(raw.get("confidence", 0)))),
    }


@observe()
def run_task_decomposition(
    project_context: dict[str, Any],
    architecture_context: dict[str, Any],
    team_capability_model: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate team-realistic tasks from project + architecture + team context.

    Inputs:
        project_context: Output from Input Ingestion Agent
        architecture_context: Output from Architecture Context Agent
        team_capability_model: { team_size, capabilities, missing_capabilities, load_capacity }

    Outputs:
        task_groups, confidence
    """
    logger.info("TaskDecompositionAgent:start")

    if not project_context or not architecture_context:
        logger.warning("TaskDecompositionAgent:missing_context")
        return {
            "agent_name": "task_decomposition",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": ["Missing project or architecture context"],
            "errors": ["project_context and architecture_context are required."],
        }

    if not team_capability_model:
        logger.warning("TaskDecompositionAgent:missing_team_model")
        return {
            "agent_name": "task_decomposition",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": ["Missing team capability model"],
            "errors": ["team_capability_model is required."],
        }

    user_prompt = f"""Generate team-realistic tasks from the following context.

## Project Context
```json
{json.dumps(project_context, indent=2)}
```

## Architecture Context
```json
{json.dumps(architecture_context, indent=2)}
```

## Team Capability Model
```json
{json.dumps(team_capability_model, indent=2)}
```

Generate tasks that match team capabilities. Use compression, escalation, or explicit blocking.
Group tasks by domain. Return JSON with: task_groups, confidence."""

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, TASK_DECOMPOSITION_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("TaskDecompositionAgent:parse_error %s", e)
        return {
            "agent_name": "task_decomposition",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("TaskDecompositionAgent:error")
        return {
            "agent_name": "task_decomposition",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    confidence = output["confidence"]
    task_groups = output.get("task_groups", [])
    blocked_count = sum(1 for grp in task_groups for t in grp.get("tasks", []) if t.get("status") == "blocked")

    if not task_groups:
        status = "blocked"
        logger.info("TaskDecompositionAgent:blocked no_tasks")
    elif blocked_count > len([t for grp in task_groups for t in grp.get("tasks", [])]) / 2:
        status = "needs_clarification"
        logger.info("TaskDecompositionAgent:needs_clarification blocked=%d", blocked_count)
    else:
        status = "success"
        logger.info("TaskDecompositionAgent:success confidence=%.2f", confidence)

    return {
        "agent_name": "task_decomposition",
        "status": status,
        "confidence": confidence,
        "output": output,
        "assumptions": [],
        "flags": [f"{blocked_count} tasks blocked"] if blocked_count > 0 else [],
        "errors": [],
    }
