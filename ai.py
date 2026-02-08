"""Streamlit app to manually test the Orchestrator (Input Ingestion → Architecture Context → Clarification)."""

import sys
import uuid
from pathlib import Path

# Ensure project root is on path
_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root))

from dotenv import load_dotenv
load_dotenv(_root / ".env")

import streamlit as st

from app.agents.langfuse_integration import get_langfuse_client
from app.agents.orchestrator import run_orchestrator, run_orchestrator_resume

st.set_page_config(page_title="Agent Orchestrator", page_icon="🔀", layout="wide")

st.title("Orchestrator — Manual Test")
st.caption("Input Ingestion → Architecture Context → Clarification (Human-in-the-loop)")
st.success("Langfuse tracing enabled")

# Session state for HITL
if "hitl_thread_id" not in st.session_state:
    st.session_state.hitl_thread_id = None
if "hitl_questions" not in st.session_state:
    st.session_state.hitl_questions = []
if "hitl_result" not in st.session_state:
    st.session_state.hitl_result = None

project_name = st.text_input("Project name", placeholder="e.g. SecureFlow AI")
text_description = st.text_area(
    "Text description",
    placeholder="e.g. Internal tool for engineering teams to manage projects and tasks with AI support.",
    height=120,
)
markdown_content = st.text_area(
    "Markdown / document content (optional)",
    placeholder="Paste README, PRD, or architecture doc here...",
    height=200,
)

# HITL: show answer form when waiting for clarification
if st.session_state.hitl_thread_id and st.session_state.hitl_questions:
    st.subheader("Clarification questions — select your answers")
    answers = {}
    for q in st.session_state.hitl_questions:
        opts = q.get("options", [])
        answer_type = q.get("answer_type", "single")
        blocking = "🔒 " if q.get("blocking") else ""
        key = f"hitl_{q.get('id', '')}"
        if answer_type == "multiple":
            labels = [o.get("label", "") for o in opts]
            ids = [o.get("id", "") for o in opts]
            selected = st.multiselect(
                f"{blocking}{q.get('question', '')}",
                options=labels,
                key=key,
            )
            answers[q.get("id", "")] = [ids[labels.index(l)] for l in selected]
        else:
            options = [f"{o.get('id', '')}: {o.get('label', '')}" for o in opts]
            idx = st.radio(
                f"{blocking}{q.get('question', '')}",
                options=options,
                key=key,
            )
            if idx:
                answers[q.get("id", "")] = idx.split(": ")[0] if ": " in idx else idx
        if q.get("risk_addressed"):
            st.caption(f"Risk: {q['risk_addressed']}")

    if st.button("Submit answers"):
        result = run_orchestrator_resume(st.session_state.hitl_thread_id, answers)
        st.session_state.hitl_thread_id = None
        st.session_state.hitl_questions = []
        st.session_state.hitl_result = result
        st.rerun()

# Show result from resume (after HITL)
if st.session_state.hitl_result:
    result = st.session_state.hitl_result
    st.session_state.hitl_result = None
    status = result.get("status", "unknown")
    status_color = {"success": "🟢", "needs_clarification": "🟡", "blocked": "🔴", "failed": "❌"}.get(status, "⚪")
    st.subheader(f"{status_color} Final status: {status}")
    for i, stage in enumerate(result.get("stages", []), 1):
        with st.expander(f"Stage {i}: {stage.get('agent_name', 'unknown')} — {stage.get('status')}"):
            st.json(stage.get("output", {}))
    st.divider()
    st.subheader("Final output")
    st.json(result.get("final_output", {}))
    with st.expander("Raw result"):
        st.json(result)

if st.button("Run Orchestrator"):
    thread_id = str(uuid.uuid4())
    result = run_orchestrator(
        project_name=project_name or "",
        text_description=text_description or None,
        markdown_content=markdown_content or None,
        thread_id=thread_id,
    )

    if result.get("__interrupt__"):
        st.session_state.hitl_thread_id = result.get("thread_id", thread_id)
        st.session_state.hitl_questions = result.get("questions", [])
        st.rerun()

    status = result.get("status", "unknown")
    status_color = {"success": "🟢", "needs_clarification": "🟡", "blocked": "🔴", "failed": "❌"}.get(status, "⚪")
    st.subheader(f"{status_color} Final status: {status}")

    stages = result.get("stages", [])
    for i, stage in enumerate(stages, 1):
        with st.expander(f"Stage {i}: {stage.get('agent_name', 'unknown')} — {stage.get('status')} (conf: {stage.get('confidence', 0):.2f})", expanded=(i == len(stages))):
            st.json(stage.get("output", {}))

    st.divider()
    st.subheader("Final output")
    st.json(result.get("final_output", {}))

    with st.expander("Raw result"):
        st.json(result)
