"""Role → Task Matching Agent — feasibility validator & workload balancer."""

import json
import logging
from typing import Any

from app.agents.langfuse_integration import observe
from app.agents.llm_config import get_chat_model
from app.agents.prompts import ROLE_TASK_MATCHING_SYSTEM
from app.agents.utils import run_json_prompt

logger = logging.getLogger(__name__)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    """Ensure fixed core fields for assignments and warnings."""
    assignments = raw.get("assignments")
    if not isinstance(assignments, list):
        assignments = []
    
    validated_assignments = []
    for i, a in enumerate(assignments):
        if not isinstance(a, dict):
            continue
        validated_assignments.append({
            "task_id": a.get("task_id") or f"unknown_task_{i}",
            "assigned_to": a.get("assigned_to") or "unassigned",
            "confidence": max(0.0, min(1.0, float(a.get("confidence", 0)))),
            "overload_risk": bool(a.get("overload_risk", False)),
        })
    
    unassigned_tasks = raw.get("unassigned_tasks")
    if not isinstance(unassigned_tasks, list):
        unassigned_tasks = []
    
    validated_unassigned = []
    for u in unassigned_tasks:
        if not isinstance(u, dict):
            continue
        validated_unassigned.append({
            "task_id": u.get("task_id") or "unknown_task",
            "reason": u.get("reason") or "No suitable capability found",
        })
    
    warnings = raw.get("warnings")
    if not isinstance(warnings, list):
        warnings = []
    warnings = [str(w) for w in warnings if w]
    
    return {
        "assignments": validated_assignments,
        "unassigned_tasks": validated_unassigned,
        "warnings": warnings,
    }


@observe()
def run_role_task_matching(
    task_groups: list[dict[str, Any]],
    team_capability_model: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validate task feasibility and balance workload across team.

    Inputs:
        task_groups: Output from Task Decomposition Agent (list of domains with tasks)
        team_capability_model: { team_size, capabilities, missing_capabilities, load_capacity }

    Outputs:
        assignments, unassigned_tasks, warnings
    """
    logger.info("RoleTaskMatchingAgent:start")

    if not task_groups or not team_capability_model:
        logger.warning("RoleTaskMatchingAgent:missing_input")
        return {
            "agent_name": "role_task_matching",
            "status": "blocked",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": ["Missing task_groups or team_capability_model"],
            "errors": ["task_groups and team_capability_model are required."],
        }

    # Flatten tasks from task_groups for easier processing
    all_tasks = []
    for grp in task_groups:
        tasks = grp.get("tasks", [])
        for t in tasks:
            all_tasks.append({
                "task_id": t.get("task_id"),
                "description": t.get("description"),
                "required_capability": t.get("required_capability"),
                "status": t.get("status"),
                "assumption": t.get("assumption"),
                "domain": grp.get("domain"),
            })

    user_prompt = f"""Assign tasks to team members based on capability and workload balance.

## Tasks to Assign
```json
{json.dumps(all_tasks, indent=2)}
```

## Team Capability Model
```json
{json.dumps(team_capability_model, indent=2)}
```

Validate feasibility, balance workload, and flag risks. Return JSON with: assignments, unassigned_tasks, warnings."""

    try:
        model = get_chat_model()
        raw = run_json_prompt(model, ROLE_TASK_MATCHING_SYSTEM, user_prompt, config=config)
    except ValueError as e:
        logger.error("RoleTaskMatchingAgent:parse_error %s", e)
        return {
            "agent_name": "role_task_matching",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }
    except Exception as e:
        logger.exception("RoleTaskMatchingAgent:error")
        return {
            "agent_name": "role_task_matching",
            "status": "failed",
            "confidence": 0.0,
            "output": _normalize_output({}),
            "assumptions": [],
            "flags": [],
            "errors": [str(e)],
        }

    output = _normalize_output(raw)
    assignments = output.get("assignments", [])
    unassigned = output.get("unassigned_tasks", [])
    warnings = output.get("warnings", [])

    # Determine status and confidence
    total_tasks = len(all_tasks)
    assigned_count = len(assignments)
    unassigned_count = len(unassigned)
    overload_count = sum(1 for a in assignments if a.get("overload_risk"))

    if total_tasks == 0:
        confidence = 0.0
        status = "blocked"
    elif assigned_count == 0:
        confidence = 0.0
        status = "blocked"
    elif unassigned_count > total_tasks / 2:
        # More than half unassigned
        confidence = 0.3
        status = "needs_clarification"
    elif overload_count > assigned_count / 2:
        # More than half have overload risk
        confidence = 0.5
        status = "needs_clarification"
    elif warnings:
        confidence = 0.7
        status = "success"
    else:
        confidence = 0.9
        status = "success"

    logger.info(
        "RoleTaskMatchingAgent:%s assigned=%d unassigned=%d overload=%d warnings=%d",
        status,
        assigned_count,
        unassigned_count,
        overload_count,
        len(warnings),
    )

    flags = []
    if unassigned_count > 0:
        flags.append(f"{unassigned_count} tasks unassigned")
    if overload_count > 0:
        flags.append(f"{overload_count} assignments have overload risk")
    if warnings:
        flags.extend(warnings)

    return {
        "agent_name": "role_task_matching",
        "status": status,
        "confidence": confidence,
        "output": output,
        "assumptions": [],
        "flags": flags,
        "errors": [],
    }
