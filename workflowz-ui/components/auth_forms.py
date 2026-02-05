import streamlit as st

from services.auth_service import login, signup
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


def render_signup_form() -> None:
    st.markdown("## Sign up")
    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="user@example.com", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        submitted = st.form_submit_button("Sign up")

    if submitted:
        if not email or not password or not password_confirm:
            st.error("All fields are required.")
            return
        if password != password_confirm:
            st.error("Passwords do not match.")
            return
        if len(password) < 8:
            st.error("Password must be at least 8 characters.")
            return
        if len(password) > 72:
            st.error("Password must be no more than 72 characters (bcrypt limitation).")
            return
        try:
            user = signup(email, password)
            st.success(f"Account created! Email: {user.get('email')}. Please log in.")
            st.info("Note: The first user becomes a superuser automatically.")
        except Exception as exc:
            error_msg = str(exc)
            if "already exists" in error_msg.lower():
                st.error("An account with this email already exists. Please log in instead.")
            else:
                st.error(f"Signup failed: {exc}")
