"""Streamlit app to manually test the Input Ingestion Agent."""

import json
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from app.agents.input_ingestion_agent import run_input_ingestion

st.set_page_config(page_title="Input Ingestion Agent", page_icon="📥", layout="wide")

st.title("Input Ingestion Agent — Manual Test")

st.caption("Normalize messy human input into clean structured context.")

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

if st.button("Run Input Ingestion"):
    result = run_input_ingestion(
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

    st.subheader(f"{status_color} Status: {status}")
    st.write(f"**Confidence:** {result.get('overall_confidence', 0):.2f}")

    output = result.get("output", {})
    if output:
        st.divider()
        st.subheader("Structured output")
        st.json(output)

    if result.get("errors"):
        st.error("Errors: " + ", ".join(result["errors"]))

    with st.expander("Raw result"):
        st.json(result)
