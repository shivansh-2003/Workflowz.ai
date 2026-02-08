"""Streamlit app to manually test the Orchestrator (Input Ingestion → Architecture Context)."""

import sys
from pathlib import Path

# Ensure project root is on path
_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root))

from dotenv import load_dotenv
load_dotenv(_root / ".env")

import streamlit as st

from app.agents.langfuse_integration import get_langfuse_client
from app.agents.orchestrator import run_orchestrator

st.set_page_config(page_title="Agent Orchestrator", page_icon="🔀", layout="wide")

st.title("Orchestrator — Manual Test")
st.caption("Input Ingestion → Architecture Context")
st.success("Langfuse tracing enabled")

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

if st.button("Run Orchestrator"):
    result = run_orchestrator(
        project_name=project_name or "",
        text_description=text_description or None,
        markdown_content=markdown_content or None,
    )

    status = result.get("status", "unknown")
    status_color = {
        "success": "🟢",
        "needs_clarification": "🟡",
        "blocked": "🔴",
        "failed": "❌",
    }.get(status, "⚪")

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
