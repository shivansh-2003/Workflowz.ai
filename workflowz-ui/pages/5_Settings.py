import streamlit as st

from components.navigation import render_sidebar
from services.superuser_service import (
    change_organization_head,
    create_organization,
    rename_organization,
)
from utils.state import get_user_context, require_auth

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

if not require_auth():
    st.switch_page("app.py")

render_sidebar()
user = get_user_context() or {}
role = user.get("role")

st.title("Settings")

st.subheader("Profile")
st.write(f"Email: {user.get('email')}")
st.write(f"Role: {user.get('role_label')}")

if role == "superuser":
    st.divider()
    st.subheader("Superuser controls")

    with st.expander("Create organization"):
        with st.form("create_org"):
            org_name = st.text_input("Organization name")
            head_email = st.text_input("Head email")
            head_name = st.text_input("Head name")
            head_designation = st.text_input("Head designation")
            submit = st.form_submit_button("Create")
        if submit:
            payload = {
                "organization_name": org_name,
                "head_email": head_email,
                "head_name": head_name,
                "head_designation": head_designation or None,
            }
            create_organization(payload)
            st.success("Organization created.")

    with st.expander("Rename organization"):
        with st.form("rename_org"):
            current_name = st.text_input("Current name")
            new_name = st.text_input("New name")
            submit = st.form_submit_button("Rename")
        if submit:
            rename_organization(current_name, new_name)
            st.success("Organization renamed.")

    with st.expander("Change organization head"):
        with st.form("change_head"):
            org_name = st.text_input("Organization name", key="change_head_org")
            new_head_email = st.text_input("New head email")
            submit = st.form_submit_button("Update")
        if submit:
            change_organization_head(org_name, new_head_email)
            st.success("Head updated.")
