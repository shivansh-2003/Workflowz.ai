import streamlit as st

from components.navigation import render_sidebar
from services.project_service import list_projects
from services.task_service import complete_task, create_task, delete_task, list_tasks, update_task
from utils.formatters import format_date
from utils.state import get_user_context, require_auth

st.set_page_config(page_title="Tasks", page_icon="✅", layout="wide")

if not require_auth():
    st.switch_page("app.py")

render_sidebar()
user = get_user_context() or {}
role = user.get("role")
org_name = st.session_state.get("org_name_input") if role == "superuser" else None

st.title("Tasks")

if role == "superuser" and not org_name:
    st.warning("Enter an organization name in the sidebar.")
    st.stop()


@st.cache_data(ttl=120)
def fetch_projects(org_name_value: str | None) -> list[dict]:
    return list_projects(org_name_value)


projects = fetch_projects(org_name)
project_map = {p["project_name"]: p for p in projects}
project_name = st.selectbox("Project", options=[""] + list(project_map.keys()))

if not project_name:
    st.info("Select a project to view tasks.")
    st.stop()

project = project_map[project_name]
project_id = project["project_id"]


@st.cache_data(ttl=120)
def fetch_tasks(project_id_value: int, org_name_value: str | None) -> list[dict]:
    return list_tasks(project_id_value, org_name_value)


tasks = fetch_tasks(project_id, org_name)

if role in {"head", "superuser"}:
    with st.expander("Create task"):
        with st.form("create_task"):
            description = st.text_area("Description")
            assignee_id = st.number_input("Assignee member_id", min_value=1, step=1)
            importance = st.selectbox("Priority", ["high", "medium", "low"])
            deadline = st.date_input("Deadline")
            submit = st.form_submit_button("Create")
        if submit:
            payload = {
                "task_description": description,
                "task_assigned_to": int(assignee_id),
                "task_importance": importance,
                "task_deadline": str(deadline) if deadline else None,
            }
            create_task(project_id, payload, org_name)
            fetch_tasks.clear()
            st.success("Task created.")
            st.rerun()

st.subheader("Task list")

if not tasks:
    st.info("No tasks found.")
else:
    for task in tasks:
        cols = st.columns([4, 2, 2, 2, 1, 1, 1])
        cols[0].markdown(f"**{task['task_description']}**")
        cols[1].write(task.get("task_importance", "-"))
        cols[2].write(format_date(task.get("task_deadline")))
        cols[3].write("✅" if task.get("task_completed") else "⏳")

        if role in {"member", "head", "superuser"}:
            completed = cols[4].checkbox(
                "Done",
                value=task.get("task_completed", False),
                key=f"complete-{task['task_id']}",
            )
            if completed != task.get("task_completed"):
                complete_task(project_id, task["task_id"], completed, org_name)
                fetch_tasks.clear()
                st.rerun()

        if role in {"head", "superuser"}:
            if cols[5].button("Edit", key=f"edit-{task['task_id']}"):
                st.session_state["edit_task_id"] = task["task_id"]
            if cols[6].button("Delete", key=f"delete-{task['task_id']}"):
                delete_task(project_id, task["task_id"], org_name)
                fetch_tasks.clear()
                st.rerun()

edit_id = st.session_state.get("edit_task_id")
if edit_id:
    editable = next((t for t in tasks if t["task_id"] == edit_id), None)
    if editable:
        st.divider()
        st.subheader("Edit task")
        with st.form("edit_task"):
            new_desc = st.text_area("Description", value=editable["task_description"])
            priorities = ["high", "medium", "low"]
            current_priority = editable.get("task_importance") or "medium"
            new_importance = st.selectbox(
                "Priority",
                priorities,
                index=priorities.index(current_priority)
                if current_priority in priorities
                else 1,
            )
            new_deadline = st.date_input("Deadline")
            submit_edit = st.form_submit_button("Update")
        if submit_edit:
            payload = {
                "task_description": new_desc,
                "task_importance": new_importance,
                "task_deadline": str(new_deadline) if new_deadline else None,
            }
            update_task(project_id, edit_id, payload, org_name)
            st.session_state["edit_task_id"] = None
            fetch_tasks.clear()
            st.success("Task updated.")
            st.rerun()
