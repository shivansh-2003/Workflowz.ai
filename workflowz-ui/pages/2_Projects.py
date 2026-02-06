import streamlit as st

from components.navigation import render_sidebar
from components.progress_bars import render_progress
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
