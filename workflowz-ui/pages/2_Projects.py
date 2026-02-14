import streamlit as st
import time

from components.navigation import render_sidebar
from components.progress_bars import render_progress
from services.ai_service import (
    approve_plan,
    get_ai_plan,
    get_ai_status,
    reject_plan,
    start_ai_pipeline,
    submit_clarification,
)
from services.project_service import create_project, delete_project, list_projects, update_project
from utils.state import get_user_context, require_auth

st.set_page_config(page_title="Projects", page_icon="📁", layout="wide")

if not require_auth():
    st.switch_page("app.py")

render_sidebar()
user = get_user_context() or {}
role = user.get("role")
org_name = st.session_state.get("org_name_input") if role == "superuser" else None

st.title("Projects")

if role == "superuser" and not org_name:
    st.warning("Enter an organization name in the sidebar.")
    st.stop()


@st.cache_data(ttl=120)
def fetch_projects(org_name_value: str | None) -> list[dict]:
    return list_projects(org_name_value)


def _render_ai_section(project: dict, org_name_val: str | None) -> None:
    """Render AI Assistant: generate, status, clarification, plan, approve."""
    pid = project["project_id"]
    proj_name = project.get("project_name", "")

    if "ai_status" not in st.session_state or st.session_state.get("ai_project_id") != pid:
        st.session_state.ai_status = None
        st.session_state.ai_project_id = pid

    st.subheader("🤖 AI Assistant")
    st.caption(
        "Generate a task plan from the project description. Input Ingestion → Architecture → Clarification → Task Decomposition → Role Matching → Validation → Approval."
    )

    # Generate form
    with st.expander("Generate plan", expanded=st.session_state.ai_status is None):
        with st.form("ai_generate"):
            text_desc = st.text_area(
                "Text description (optional override)",
                value=project.get("project_description") or "",
                height=80,
                placeholder="Override project description for this run.",
            )
            markdown = st.text_area(
                "Markdown / doc (optional)",
                height=120,
                placeholder="Paste README, PRD, or architecture doc...",
            )
            if st.form_submit_button("Start AI pipeline"):
                try:
                    res = start_ai_pipeline(
                        pid,
                        text_description=text_desc or None,
                        markdown_content=markdown or None,
                        organization_name=org_name_val,
                    )
                    st.session_state.ai_status = {"current_state": "INPUT_INGESTION", "workflow_id": res.get("workflow_id")}
                    st.success("Pipeline started. Polling status...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start: {e}")

    # Poll status and show state
    if st.session_state.ai_status:
        try:
            status = get_ai_status(pid, org_name_val)
            st.session_state.ai_status = status
        except Exception as e:
            st.warning(f"Could not fetch status: {e}")

        cs = status.get("current_state", "UNKNOWN")
        locked = status.get("locked", False)
        err = status.get("error")

        status_icon = {"HUMAN_APPROVAL": "🟢", "WAIT_FOR_USER": "🟡", "ERROR_STATE": "🔴", "TERMINATED": "⚫"}.get(
            cs, "🔄"
        )
        st.markdown(f"**Status:** {status_icon} `{cs}`")

        if err:
            st.error(err)

        # Clarification form (WAIT_FOR_USER)
        ao = status.get("agent_outputs") or {}
        questions = ao.get("questions") or (ao.get("clarification_output") or {}).get("questions") or []
        if cs == "WAIT_FOR_USER" and locked and questions:
            st.subheader("Clarification questions")
            answers = {}
            for q in questions:
                opts = q.get("options", [])
                ans_type = q.get("answer_type", "single")
                blocking = "🔒 " if q.get("blocking") else ""
                key = f"clar_{q.get('id', '')}"
                if ans_type == "multiple":
                    labels = [o.get("label", "") for o in opts]
                    ids = [o.get("id", "") for o in opts]
                    sel = st.multiselect(f"{blocking}{q.get('question', '')}", options=labels, key=key)
                    answers[q.get("id", "")] = [ids[labels.index(l)] for l in sel]
                else:
                    options = [f"{o.get('id', '')}: {o.get('label', '')}" for o in opts]
                    idx = st.radio(f"{blocking}{q.get('question', '')}", options=options, key=key)
                    if idx:
                        answers[q.get("id", "")] = idx.split(": ")[0] if ": " in idx else idx
            if st.button("Submit answers"):
                try:
                    submit_clarification(pid, answers, org_name_val)
                    st.success("Answers submitted. Pipeline resuming...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        # Plan view & approve/reject (HUMAN_APPROVAL)
        if cs == "HUMAN_APPROVAL":
            try:
                plan = get_ai_plan(pid, org_name_val)
            except Exception as e:
                st.error(f"Could not load plan: {e}")
                plan = {}

            task_groups = plan.get("task_groups", [])
            assignments = plan.get("assignments", [])
            unassigned = plan.get("unassigned_tasks", [])
            risk_report = plan.get("risk_report") or {}
            warnings = plan.get("warnings", [])

            if task_groups:
                st.subheader("📋 Task Groups")
                for grp in task_groups:
                    domain = grp.get("domain", "General")
                    tasks_list = grp.get("tasks", [])
                    with st.expander(f"**{domain}** ({len(tasks_list)} tasks)", expanded=True):
                        for t in tasks_list:
                            icon = {"ready": "✅", "adapted": "🔄", "blocked": "🚫"}.get(t.get("status", ""), "⚪")
                            st.markdown(f"{icon} **{t.get('description', 'N/A')}**")
                            st.caption(
                                f"Capability: {t.get('required_capability', 'N/A')} | Status: {t.get('status', 'N/A')}"
                            )

            if assignments:
                st.subheader("👥 Assignments")
                for a in assignments:
                    st.markdown(f"**{a.get('task_id')}** → `{a.get('assigned_to')}`")
            if unassigned:
                st.warning(f"Unassigned: {len(unassigned)} tasks")
            if warnings:
                for w in warnings:
                    st.warning(w)

            risk_level = risk_report.get("risk_level", "")
            risk_score = risk_report.get("risk_score", 0)
            if risk_level:
                st.markdown(f"**Risk:** {risk_level} ({risk_score}/100)")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve & create tasks"):
                    try:
                        res = approve_plan(pid, approved=True, organization_name=org_name_val)
                        st.success(
                            f"Created {res.get('tasks_created', 0)} tasks. Progress: {res.get('project_progress', 0)}%"
                        )
                        st.session_state.ai_status = None
                        fetch_projects.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Approve failed: {e}")
            with col2:
                if st.button("❌ Reject plan"):
                    try:
                        reject_plan(pid, org_name_val)
                        st.info("Plan rejected.")
                        st.session_state.ai_status = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Reject failed: {e}")

        # Auto-refresh when pipeline is running (not terminal states)
        if cs not in ("HUMAN_APPROVAL", "WAIT_FOR_USER", "COMPLETED", "ERROR_STATE", "TERMINATED"):
            time.sleep(2)
            st.rerun()


projects = fetch_projects(org_name)

left, right = st.columns([1, 2])

with left:
    st.subheader("Project list")
    project_options = {p["project_name"]: p for p in projects}
    selected_name = st.selectbox(
        "Select project", options=[""] + list(project_options.keys())
    )

    if role in {"head", "superuser"}:
        st.divider()
        st.subheader("Create project")
        with st.form("create_project"):
            name = st.text_input("Name")
            description = st.text_area("Description")
            submit = st.form_submit_button("Create")
        if submit:
            if not name:
                st.error("Project name is required.")
            else:
                try:
                    create_project(name, description or None, org_name)
                except Exception as exc:
                    st.error(f"Create failed: {exc}")
                else:
                    fetch_projects.clear()
                    st.success("Project created.")
                    st.rerun()

with right:
    if not selected_name:
        st.info("Select a project to view details.")
    else:
        project = project_options[selected_name]
        st.subheader(project["project_name"])
        st.write(project.get("project_description") or "No description.")
        render_progress("Progress", int(project.get("project_progress", 0)))

        if role in {"head", "superuser"}:
            st.divider()
            st.subheader("Edit project")
            with st.form("edit_project"):
                new_name = st.text_input("Name", value=project["project_name"])
                new_desc = st.text_area(
                    "Description", value=project.get("project_description") or ""
                )
                submit_edit = st.form_submit_button("Update")
            if submit_edit:
                update_project(
                    project["project_id"],
                    {"project_name": new_name, "project_description": new_desc},
                    org_name,
                )
                fetch_projects.clear()
                st.success("Project updated.")
                st.rerun()

            st.divider()
            if st.button("Delete project", type="secondary"):
                delete_project(project["project_id"], org_name)
                fetch_projects.clear()
                st.success("Project deleted.")
                st.rerun()

            st.divider()
            _render_ai_section(project, org_name)
