import streamlit as st

from utils.state import get_user_context, logout


def render_sidebar() -> None:
    st.sidebar.title("Workflowz.ai")
    user = get_user_context()
    if user:
        st.sidebar.caption(user.get("email", ""))
        st.sidebar.caption(user.get("role_label", ""))
        if user.get("role") == "superuser":
            st.sidebar.text_input(
                "Organization name",
                key="org_name_input",
                placeholder="e.g. Acme Corp",
            )
    st.sidebar.divider()

    st.sidebar.page_link("app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/2_Projects.py", label="Projects", icon="📁")
    st.sidebar.page_link("pages/3_Tasks.py", label="Tasks", icon="✅")
    st.sidebar.page_link("pages/4_Team.py", label="Team", icon="👥")
    st.sidebar.page_link("pages/5_Settings.py", label="Settings", icon="⚙️")

    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
