import streamlit as st

from components.navigation import render_sidebar
from components.progress_bars import render_progress
from services.project_service import list_projects
from utils.state import get_user_context, require_auth

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if not require_auth():
    st.switch_page("app.py")

render_sidebar()
user = get_user_context() or {}
org_name = st.session_state.get("org_name_input") if user.get("role") == "superuser" else None

if user.get("role") == "superuser" and not org_name:
    st.warning("Enter an organization name in the sidebar.")
    st.stop()

st.title("Dashboard")


@st.cache_data(ttl=120)
def fetch_projects(org_name_value: str | None) -> list[dict]:
    return list_projects(org_name_value)


projects = fetch_projects(org_name)

total_projects = len(projects)
avg_progress = (
    sum(project.get("project_progress", 0) for project in projects) / total_projects
    if total_projects
    else 0
)

col1, col2 = st.columns(2)
col1.metric("Projects", total_projects)
col2.metric("Avg progress", f"{avg_progress:.0f}%")

st.subheader("Projects")
if not projects:
    st.info("No projects yet.")
else:
    for project in projects:
        st.markdown(
            f"**{project['project_name']}** — {project.get('project_description') or ''}"
        )
        render_progress("Progress", int(project.get("project_progress", 0)))
