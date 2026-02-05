import streamlit as st

from components.navigation import render_sidebar
from services.team_service import add_member, list_members
from utils.state import get_user_context, require_auth

st.set_page_config(page_title="Team", page_icon="👥", layout="wide")

if not require_auth():
    st.switch_page("app.py")

render_sidebar()
user = get_user_context() or {}
role = user.get("role")
org_name = st.session_state.get("org_name_input") if role == "superuser" else None

st.title("Team")

if role == "superuser" and not org_name:
    st.warning("Enter an organization name in the sidebar.")
    st.stop()


@st.cache_data(ttl=120)
def fetch_members(org_name_value: str | None) -> list[dict]:
    return list_members(org_name_value)


try:
    members = fetch_members(org_name)
except Exception as exc:
    st.error(f"Unable to load team members: {exc}")
    members = []

if role in {"head", "superuser"}:
    with st.expander("Add team member"):
        with st.form("add_member"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            designation = st.text_input("Designation")
            position = st.selectbox("Position", ["member", "head"])
            submit = st.form_submit_button("Add")
        if submit:
            payload = {
                "name": name,
                "email": email,
                "designation": designation or None,
                "position": position,
            }
            add_member(payload, org_name)
            fetch_members.clear()
            st.success("Member added.")
            st.rerun()

st.subheader("Members")
if not members:
    st.info("No team members found.")
else:
    for member in members:
        st.markdown(
            f"**{member['name']}** — {member['position']} — {member['email']}"
        )
