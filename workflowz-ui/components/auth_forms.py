import streamlit as st

from services.auth_service import login
from utils.state import set_auth_session


def render_login_form() -> None:
    st.markdown("## Sign in")
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="user@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
            return
        try:
            token = login(email, password)
            set_auth_session(token)
            st.success("Logged in.")
            st.rerun()
        except Exception as exc:
            st.error(f"Login failed: {exc}")
