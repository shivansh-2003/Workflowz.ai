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
st.caption("Input Ingestion → Architecture Context → Clarification (HITL) → Task Decomposition → Role → Task Matching → Validation & Risk → Human Approval")
st.success("Langfuse tracing enabled")

# Session state for HITL
if "hitl_thread_id" not in st.session_state:
    st.session_state.hitl_thread_id = None
if "hitl_questions" not in st.session_state:
    st.session_state.hitl_questions = []
if "hitl_result" not in st.session_state:
    st.session_state.hitl_result = None

project_name = st.text_input("Project name", placeholder="e.g. SecureFlow AI")
organization_name = st.text_input(
    "Organization name (for team capability model)",
    placeholder="e.g. TechCorp",
    help="Required for task decomposition. Leave empty to skip team fetching.",
)
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
    
    # Show task decomposition if available
    if result.get("task_output"):
        st.subheader("📋 Task Groups")
        task_output = result["task_output"]
        task_groups = task_output.get("task_groups", [])
        if task_groups:
            for grp in task_groups:
                domain = grp.get("domain", "General")
                tasks = grp.get("tasks", [])
                with st.expander(f"**{domain}** ({len(tasks)} tasks)", expanded=True):
                    for t in tasks:
                        status_icon = {"ready": "✅", "adapted": "🔄", "blocked": "🚫"}.get(t.get("status", ""), "⚪")
                        st.markdown(f"{status_icon} **{t.get('description', 'N/A')}**")
                        st.caption(f"Capability: {t.get('required_capability', 'N/A')} | Status: {t.get('status', 'N/A')}")
                        if t.get("assumption"):
                            st.caption(f"_Assumption: {t['assumption']}_")
                        st.divider()
        else:
            st.info("No task groups generated")
        
        # Show team capability model
        if result.get("team_capability_model"):
            with st.expander("Team Capability Model"):
                st.json(result["team_capability_model"])
    
    # Show task assignments if available
    if result.get("matching_output"):
        st.subheader("👥 Task Assignments & Workload Balance")
        matching_output = result["matching_output"]
        
        # Show warnings first
        warnings = matching_output.get("warnings", [])
        if warnings:
            st.warning("**Warnings:**")
            for w in warnings:
                st.markdown(f"⚠️ {w}")
            st.divider()
        
        # Show assignments
        assignments = matching_output.get("assignments", [])
        if assignments:
            st.success(f"**{len(assignments)} tasks assigned**")
            for a in assignments:
                task_id = a.get("task_id", "N/A")
                assigned_to = a.get("assigned_to", "Unassigned")
                confidence = a.get("confidence", 0)
                overload_risk = a.get("overload_risk", False)
                
                risk_icon = "⚠️" if overload_risk else "✓"
                confidence_color = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
                
                st.markdown(f"{risk_icon} **{task_id}** → `{assigned_to}` {confidence_color} (confidence: {confidence:.2f})")
                if overload_risk:
                    st.caption("⚠️ _Overload risk detected_")
            st.divider()
        
        # Show unassigned tasks
        unassigned = matching_output.get("unassigned_tasks", [])
        if unassigned:
            st.error(f"**{len(unassigned)} tasks unassigned**")
            for u in unassigned:
                task_id = u.get("task_id", "N/A")
                reason = u.get("reason", "No reason provided")
                st.markdown(f"🚫 **{task_id}**")
                st.caption(f"_Reason: {reason}_")
    
    # Show risk report if available
    if result.get("risk_output"):
        st.subheader("🛡️ Validation & Risk Report")
        risk_output = result["risk_output"]
        
        risk_score = risk_output.get("risk_score", 0)
        risk_level = risk_output.get("risk_level", "unknown")
        top_risks = risk_output.get("top_risks", [])
        blocking_issues = risk_output.get("blocking_issues", [])
        
        # Risk level indicator
        risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")
        st.markdown(f"**Risk Level:** {risk_color} {risk_level.upper()} (Score: {risk_score}/100)")
        
        # Blocking issues (critical)
        if blocking_issues:
            st.error("**⛔ Blocking Issues (Must be resolved before proceeding)**")
            for issue in blocking_issues:
                st.markdown(f"- {issue}")
            st.divider()
        
        # Top risks
        if top_risks:
            st.warning("**⚠️ Top Risks Identified:**")
            for risk in top_risks:
                st.markdown(f"- {risk}")
            st.divider()
        
        # Risk gauge
        if risk_score <= 30:
            st.success("✅ Plan is solid with minor issues")
        elif risk_score <= 60:
            st.warning("⚠️ Significant concerns detected — review recommended")
        else:
            st.error("🚨 Critical issues found — plan may fail")
    
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
        organization_name=organization_name or None,
        auth_token=None,  # TODO: Add auth token input if needed
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
    
    # Show task decomposition if available
    if result.get("task_output"):
        st.subheader("📋 Task Groups")
        task_output = result["task_output"]
        task_groups = task_output.get("task_groups", [])
        if task_groups:
            for grp in task_groups:
                domain = grp.get("domain", "General")
                tasks = grp.get("tasks", [])
                with st.expander(f"**{domain}** ({len(tasks)} tasks)", expanded=True):
                    for t in tasks:
                        status_icon = {"ready": "✅", "adapted": "🔄", "blocked": "🚫"}.get(t.get("status", ""), "⚪")
                        st.markdown(f"{status_icon} **{t.get('description', 'N/A')}**")
                        st.caption(f"Capability: {t.get('required_capability', 'N/A')} | Status: {t.get('status', 'N/A')}")
                        if t.get("assumption"):
                            st.caption(f"_Assumption: {t['assumption']}_")
                        st.divider()
        else:
            st.info("No task groups generated")
        
        # Show team capability model
        if result.get("team_capability_model"):
            with st.expander("Team Capability Model"):
                st.json(result["team_capability_model"])
    
    st.subheader("Final output")
    st.json(result.get("final_output", {}))

    with st.expander("Raw result"):
        st.json(result)
