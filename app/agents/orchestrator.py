"""Orchestrator — LangGraph-based composition of Input Ingestion and Architecture Context agents."""

import logging
from typing import Any, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from app.agents.architecture_context_agent import run_architecture_context
from app.agents.backend_client import fetch_team_capability_model_sync
from app.agents.clarification_agent import run_clarification
from app.agents.input_ingestion_agent import run_input_ingestion
from app.agents.langfuse_integration import flush, get_runnable_config, observe
from app.agents.role_task_matching_agent import run_role_task_matching
from app.agents.task_decomposition_agent import run_task_decomposition
from app.agents.validation_risk_agent import run_validation_risk

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict, total=False):
    project_name: str
    text_description: str | None
    markdown_content: str | None
    organization_name: str | None
    auth_token: str | None
    ingestion_output: dict[str, Any]
    ingestion_status: str
    ingestion_confidence: float
    arch_output: dict[str, Any]
    arch_status: str
    clarification_output: dict[str, Any]
    clarification_status: str
    clarification_answers: dict[str, Any]
    team_capability_model: dict[str, Any]
    task_output: dict[str, Any]
    task_status: str
    matching_output: dict[str, Any]
    matching_status: str
    risk_output: dict[str, Any]
    risk_status: str
    stages: list[dict[str, Any]]
    final_status: str


def _input_ingestion_node(state: OrchestratorState) -> OrchestratorState:
    config = get_runnable_config("input_ingestion")
    result = run_input_ingestion(
        project_name=state.get("project_name", ""),
        text_description=state.get("text_description"),
        markdown_content=state.get("markdown_content"),
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")
    confidence = float(output.get("overall_confidence", 0))

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "input_ingestion",
        "status": status,
        "confidence": confidence,
        "output": output,
    })

    return {
        **state,
        "ingestion_output": output,
        "ingestion_status": status,
        "ingestion_confidence": confidence,
        "stages": stages,
    }


def _architecture_context_node(state: OrchestratorState) -> OrchestratorState:
    config = get_runnable_config("architecture_context")
    result = run_architecture_context(
        structured_project_context=state.get("ingestion_output", {}),
        ingestion_confidence=state.get("ingestion_confidence", 0),
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "architecture_context",
        "status": status,
        "confidence": output.get("confidence", 0),
        "output": output,
    })

    return {
        **state,
        "arch_output": output,
        "arch_status": status,
        "stages": stages,
    }


def _clarification_generate_node(state: OrchestratorState) -> OrchestratorState:
    """Generate clarification questions (LLM)."""
    config = get_runnable_config("clarification")
    result = run_clarification(
        ingestion_output=state.get("ingestion_output", {}),
        arch_output=state.get("arch_output", {}),
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "clarification",
        "status": status,
        "confidence": result.get("confidence", 0),
        "output": output,
    })

    return {
        **state,
        "clarification_output": output,
        "clarification_status": status,
        "stages": stages,
    }


def _clarification_wait_node(state: OrchestratorState) -> OrchestratorState:
    """Human-in-the-loop: interrupt for user answers, then continue."""
    output = state.get("clarification_output", {})
    questions = output.get("questions", [])

    if not questions:
        # No questions, continue to task decomposition
        return {**state}

    payload = {"questions": questions, "ready_to_proceed": output.get("ready_to_proceed", False)}
    answers = interrupt(payload)

    return {
        **state,
        "clarification_answers": answers or {},
        "clarification_output": {**output, "user_answers": answers or {}},
    }


def _task_decomposition_node(state: OrchestratorState) -> OrchestratorState:
    """Generate team-realistic tasks."""
    # Fetch team capability model if not already in state
    team_capability_model = state.get("team_capability_model")
    if not team_capability_model:
        organization_name = state.get("organization_name")
        auth_token = state.get("auth_token")
        if organization_name:
            logger.info("TaskDecompositionNode:fetching_team_model org=%s", organization_name)
            team_capability_model = fetch_team_capability_model_sync(
                organization_name=organization_name,
                auth_token=auth_token,
            )
        else:
            logger.warning("TaskDecompositionNode:no_org_name using_empty_model")
            team_capability_model = {
                "team_size": 0,
                "capabilities": [],
                "missing_capabilities": [],
                "load_capacity": {},
            }

    config = get_runnable_config("task_decomposition")
    result = run_task_decomposition(
        project_context=state.get("ingestion_output", {}),
        architecture_context=state.get("arch_output", {}),
        team_capability_model=team_capability_model,
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "task_decomposition",
        "status": status,
        "confidence": result.get("confidence", 0),
        "output": output,
    })

    # Determine final status
    ingestion_status = state.get("ingestion_status", "")
    arch_status = state.get("arch_status", "")
    clarification_status = state.get("clarification_status", "")
    
    if status == "failed" or arch_status == "failed" or clarification_status == "failed":
        final_status: str = "failed"
    elif status == "blocked":
        final_status = "blocked"
    elif status == "needs_clarification" or arch_status == "needs_clarification" or clarification_status == "needs_clarification" or ingestion_status == "needs_clarification":
        final_status = "needs_clarification"
    else:
        final_status = "success"

    return {
        **state,
        "team_capability_model": team_capability_model,
        "task_output": output,
        "task_status": status,
        "stages": stages,
        "final_status": final_status,
    }


def _role_task_matching_node(state: OrchestratorState) -> OrchestratorState:
    """Validate feasibility and balance workload."""
    task_output = state.get("task_output", {})
    task_groups = task_output.get("task_groups", [])
    team_capability_model = state.get("team_capability_model", {})

    config = get_runnable_config("role_task_matching")
    result = run_role_task_matching(
        task_groups=task_groups,
        team_capability_model=team_capability_model,
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "role_task_matching",
        "status": status,
        "confidence": result.get("confidence", 0),
        "output": output,
    })

    return {
        **state,
        "matching_output": output,
        "matching_status": status,
        "stages": stages,
    }


def _validation_risk_node(state: OrchestratorState) -> OrchestratorState:
    """Independent audit of the plan — validate and flag risks."""
    arch_output = state.get("arch_output", {})
    task_output = state.get("task_output", {})
    task_groups = task_output.get("task_groups", [])
    matching_output = state.get("matching_output", {})

    config = get_runnable_config("validation_risk")
    result = run_validation_risk(
        architecture_context=arch_output,
        task_groups=task_groups,
        matching_output=matching_output,
        config=config,
    )
    output = result.get("output", {})
    status = result.get("status", "unknown")

    stages = list(state.get("stages", []))
    stages.append({
        "agent_name": "validation_risk",
        "status": status,
        "confidence": result.get("confidence", 0),
        "output": output,
    })

    # Determine final status based on all agents
    ingestion_status = state.get("ingestion_status", "")
    arch_status = state.get("arch_status", "")
    clarification_status = state.get("clarification_status", "")
    task_status = state.get("task_status", "")
    matching_status = state.get("matching_status", "")
    
    if status == "failed" or matching_status == "failed" or task_status == "failed" or arch_status == "failed" or clarification_status == "failed":
        final_status: str = "failed"
    elif status == "blocked" or matching_status == "blocked" or task_status == "blocked":
        final_status = "blocked"
    elif status == "needs_clarification" or matching_status == "needs_clarification" or task_status == "needs_clarification" or arch_status == "needs_clarification" or clarification_status == "needs_clarification" or ingestion_status == "needs_clarification":
        final_status = "needs_clarification"
    else:
        final_status = "success"

    return {
        **state,
        "risk_output": output,
        "risk_status": status,
        "stages": stages,
        "final_status": final_status,
    }


def _route_after_ingestion(state: OrchestratorState) -> Literal["architecture_context", "__end__"]:
    if state.get("ingestion_status") in ("blocked", "failed"):
        return "__end__"
    return "architecture_context"


def _route_after_architecture(state: OrchestratorState) -> Literal["clarification_generate", "__end__"]:
    if state.get("arch_status") in ("blocked", "failed"):
        return "__end__"
    return "clarification_generate"


def _build_graph():
    builder = StateGraph(OrchestratorState)
    builder.add_node("input_ingestion", _input_ingestion_node)
    builder.add_node("architecture_context", _architecture_context_node)
    builder.add_node("clarification_generate", _clarification_generate_node)
    builder.add_node("clarification_wait", _clarification_wait_node)
    builder.add_node("task_decomposition", _task_decomposition_node)
    builder.add_node("role_task_matching", _role_task_matching_node)
    builder.add_node("validation_risk", _validation_risk_node)
    builder.set_entry_point("input_ingestion")
    builder.add_conditional_edges(
        "input_ingestion",
        _route_after_ingestion,
        {"architecture_context": "architecture_context", "__end__": END},
    )
    builder.add_conditional_edges(
        "architecture_context",
        _route_after_architecture,
        {"clarification_generate": "clarification_generate", "__end__": END},
    )
    builder.add_edge("clarification_generate", "clarification_wait")
    builder.add_edge("clarification_wait", "task_decomposition")
    builder.add_edge("task_decomposition", "role_task_matching")
    builder.add_edge("role_task_matching", "validation_risk")
    builder.add_edge("validation_risk", END)
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


_GRAPH = _build_graph()


def _merge_config(base: dict[str, Any], thread_id: str) -> dict[str, Any]:
    return {
        **base,
        "configurable": {**(base.get("configurable") or {}), "thread_id": thread_id},
    }


@observe()
def run_orchestrator(
    project_name: str = "",
    text_description: str | None = None,
    markdown_content: str | None = None,
    organization_name: str | None = None,
    auth_token: str | None = None,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """
    Run full agentic pipeline: Input Ingestion → Architecture Context → Clarification → Task Decomposition.

    Inputs:
        project_name: Project name
        text_description: Plain text or short description
        markdown_content: README, PRD, architecture doc, etc.
        organization_name: Organization name to fetch team members (for task decomposition)
        auth_token: Optional JWT token for backend authentication
        thread_id: Required for human-in-the-loop. Use same ID to resume after answers.

    Outputs:
        status, final_output, stages
        OR __interrupt__ when waiting for clarification answers (human-in-the-loop)
    """
    import uuid

    logger.info("Orchestrator:start org=%s", organization_name)
    runnable_config = get_runnable_config()
    tid = thread_id or str(uuid.uuid4())
    config = _merge_config(runnable_config, tid)

    initial_state: OrchestratorState = {
        "project_name": project_name,
        "text_description": text_description,
        "markdown_content": markdown_content,
        "organization_name": organization_name,
        "auth_token": auth_token,
        "stages": [],
    }

    result = _GRAPH.invoke(initial_state, config=config)

    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value if result["__interrupt__"] else {}
        flush()
        return {
            "__interrupt__": True,
            "thread_id": tid,
            "questions": payload.get("questions", []),
            "stages": result.get("stages", []),
        }

    final_state = result
    ingestion_status = final_state.get("ingestion_status", "")
    stages = final_state.get("stages", [])

    if ingestion_status in ("blocked", "failed"):
        status = ingestion_status
        final_output = final_state.get("ingestion_output", {})
    elif final_state.get("arch_status") in ("blocked", "failed"):
        status = final_state.get("arch_status", "failed")
        final_output = final_state.get("arch_output", {})
    elif final_state.get("task_status") in ("blocked", "failed"):
        status = final_state.get("task_status", "failed")
        final_output = final_state.get("task_output", {})
    else:
        status = final_state.get("final_status", "success")
        final_output = final_state.get("task_output") or final_state.get("clarification_output") or final_state.get("arch_output", {})

    logger.info("Orchestrator:done status=%s", status)
    flush()
    return {
        "status": status,
        "final_output": final_output,
        "stages": stages,
        "task_output": final_state.get("task_output"),
        "team_capability_model": final_state.get("team_capability_model"),
        "matching_output": final_state.get("matching_output"),
        "risk_output": final_state.get("risk_output"),
    }


def run_orchestrator_resume(thread_id: str, answers: dict[str, Any]) -> dict[str, Any]:
    """Resume orchestrator after user submits clarification answers."""
    logger.info("Orchestrator:resume thread_id=%s", thread_id)
    runnable_config = get_runnable_config("clarification_resume")
    config = _merge_config(runnable_config, thread_id)

    result = _GRAPH.invoke(Command(resume=answers), config=config)

    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value if result["__interrupt__"] else {}
        flush()
        return {
            "__interrupt__": True,
            "thread_id": thread_id,
            "questions": payload.get("questions", []),
            "stages": result.get("stages", []),
        }

    final_state = result
    stages = final_state.get("stages", [])
    final_output = final_state.get("task_output") or final_state.get("clarification_output") or final_state.get("arch_output", {})
    status = final_state.get("final_status", "success")
    logger.info("Orchestrator:resume_done status=%s", status)
    flush()
    return {
        "status": status,
        "final_output": final_output,
        "stages": stages,
        "task_output": final_state.get("task_output"),
        "team_capability_model": final_state.get("team_capability_model"),
        "matching_output": final_state.get("matching_output"),
        "risk_output": final_state.get("risk_output"),
    }
