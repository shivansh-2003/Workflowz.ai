import streamlit as st

from components.auth_forms import render_login_form
from components.navigation import render_sidebar
from utils.state import init_state, require_auth

st.set_page_config(page_title="Workflowz.ai", page_icon="✅", layout="wide")

init_state()

if not require_auth():
    st.title("Workflowz.ai")
    st.caption("Sign in to manage projects, tasks, and teams.")
    render_login_form()
    st.stop()

render_sidebar()
st.success("You are logged in. Use the sidebar to navigate.")
