import streamlit as st

from components.navigation import render_sidebar
from services.auth_service import register_user
from services.superuser_service import (
    change_organization_head,
    create_organization,
    list_organizations,
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

    st.markdown("### Organizations")
    try:
        orgs = list_organizations()
        if orgs:
            for org in orgs:
                st.markdown(
                    f"**{org['organization_name']}** — Head: {org.get('head_name', 'N/A')} "
                    f"({org.get('head_email', 'N/A')}) — {org.get('member_count', 0)} members"
                )
        else:
            st.info("No organizations created yet.")
    except Exception as exc:
        st.error(f"Unable to load organizations: {exc}")

    st.divider()

    with st.expander("Create organization"):
        st.info("Note: The head user must exist before creating an organization. Create the user first using 'Create user' below if needed.")
        with st.form("create_org"):
            org_name = st.text_input("Organization name")
            head_email = st.text_input("Head email")
            head_name = st.text_input("Head name")
            head_designation = st.text_input("Head designation")
            submit = st.form_submit_button("Create")
        if submit:
            if not org_name or not head_email or not head_name:
                st.error("Organization name, head email, and head name are required.")
            else:
                try:
                    payload = {
                        "organization_name": org_name,
                        "head_email": head_email,
                        "head_name": head_name,
                        "head_designation": head_designation or None,
                    }
                    create_organization(payload)
                    st.success("Organization created.")
                    st.rerun()
                except Exception as exc:
                    error_msg = str(exc)
                    if "Head user does not exist" in error_msg or "does not exist" in error_msg:
                        st.error(
                            f"User '{head_email}' does not exist. Please create the user first using the 'Create user' form below."
                        )
                    else:
                        st.error(f"Failed to create organization: {exc}")

    with st.expander("Create user"):
        st.caption("Create a new user account. This user can then be assigned as an organization head.")
        with st.form("create_user"):
            user_email = st.text_input("Email", key="create_user_email")
            user_password = st.text_input("Password", type="password", key="create_user_password")
            is_superuser = st.checkbox("Make superuser", key="create_user_superuser")
            submit_user = st.form_submit_button("Create user")
        if submit_user:
            if not user_email or not user_password:
                st.error("Email and password are required.")
            elif len(user_password) < 8:
                st.error("Password must be at least 8 characters.")
            elif len(user_password) > 72:
                st.error("Password must be no more than 72 characters.")
            else:
                try:
                    register_user(user_email, user_password, is_superuser)
                    st.success(f"User '{user_email}' created successfully.")
                    st.rerun()
                except Exception as exc:
                    error_msg = str(exc)
                    if "already exists" in error_msg.lower():
                        st.error(f"User '{user_email}' already exists.")
                    else:
                        st.error(f"Failed to create user: {exc}")

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
