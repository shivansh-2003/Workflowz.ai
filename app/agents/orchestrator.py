"""Orchestrator — LangGraph-based composition of Input Ingestion and Architecture Context agents."""

import logging
from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.architecture_context_agent import run_architecture_context
from app.agents.input_ingestion_agent import run_input_ingestion
from langfuse.decorators import observe

from app.agents.langfuse_integration import flush, get_runnable_config

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict, total=False):
    project_name: str
    text_description: str | None
    markdown_content: str | None
    config: dict[str, Any]
    ingestion_output: dict[str, Any]
    ingestion_status: str
    ingestion_confidence: float
    arch_output: dict[str, Any]
    arch_status: str
    stages: list[dict[str, Any]]
    final_status: str


def _input_ingestion_node(state: OrchestratorState) -> OrchestratorState:
    config = state.get("config") or {}
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
    config = state.get("config") or {}
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

    ingestion_status = state.get("ingestion_status", "")
    if status == "failed":
        final_status: str = "failed"
    elif status == "needs_clarification" or ingestion_status == "needs_clarification":
        final_status = "needs_clarification"
    else:
        final_status = "success"

    return {
        **state,
        "arch_output": output,
        "arch_status": status,
        "stages": stages,
        "final_status": final_status,
    }


def _route_after_ingestion(state: OrchestratorState) -> Literal["architecture_context", "__end__"]:
    if state.get("ingestion_status") in ("blocked", "failed"):
        return "__end__"
    return "architecture_context"


def _build_graph() -> StateGraph:
    builder = StateGraph(OrchestratorState)
    builder.add_node("input_ingestion", _input_ingestion_node)
    builder.add_node("architecture_context", _architecture_context_node)
    builder.set_entry_point("input_ingestion")
    builder.add_conditional_edges(
        "input_ingestion",
        _route_after_ingestion,
        {"architecture_context": "architecture_context", "__end__": END},
    )
    builder.add_edge("architecture_context", END)
    return builder.compile()


_GRAPH = _build_graph()


@observe()
def run_orchestrator(
    project_name: str = "",
    text_description: str | None = None,
    markdown_content: str | None = None,
) -> dict[str, Any]:
    """
    Run Input Ingestion → Architecture Context via LangGraph.

    Inputs:
        project_name: Project name
        text_description: Plain text or short description
        markdown_content: README, PRD, architecture doc, etc.

    Outputs:
        final_output: Architecture context output (or last successful stage)
        stages: list of { agent_name, status, output } for each stage
        status: success | needs_clarification | blocked | failed
    """
    logger.info("Orchestrator:start")

    runnable_config = get_runnable_config()

    initial_state: OrchestratorState = {
        "project_name": project_name,
        "text_description": text_description,
        "markdown_content": markdown_content,
        "config": runnable_config,
        "stages": [],
    }

    final_state = _GRAPH.invoke(initial_state, config=runnable_config)

    ingestion_status = final_state.get("ingestion_status", "")
    stages = final_state.get("stages", [])

    if ingestion_status in ("blocked", "failed"):
        status = ingestion_status
        final_output = final_state.get("ingestion_output", {})
    else:
        status = final_state.get("final_status", "success")
        final_output = final_state.get("arch_output", {})

    logger.info("Orchestrator:done status=%s", status)

    flush()

    return {
        "status": status,
        "final_output": final_output,
        "stages": stages,
    }
