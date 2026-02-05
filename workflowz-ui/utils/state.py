from __future__ import annotations

import streamlit as st

from utils.jwt import decode_jwt


def init_state() -> None:
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("user_context", None)
    st.session_state.setdefault("org_name_input", "")


def set_auth_session(token: str) -> None:
    payload = decode_jwt(token)
    is_superuser = bool(payload.get("is_superuser", False))
    email = payload.get("sub")
    role = "superuser" if is_superuser else "member"

    if not is_superuser:
        # Best-effort role detection: if /teams works, user is likely head.
        # Import lazily to avoid circular import
        try:
            from services.team_service import list_members

            _ = list_members()
            role = "head"
        except Exception:
            role = "member"

    st.session_state["access_token"] = token
    st.session_state["user_context"] = {
        "email": email,
        "is_superuser": is_superuser,
        "role": role,
        "role_label": role.title(),
    }


def logout() -> None:
    st.session_state["access_token"] = None
    st.session_state["user_context"] = None


def get_access_token() -> str | None:
    return st.session_state.get("access_token")


def get_user_context() -> dict | None:
    return st.session_state.get("user_context")


def require_auth() -> bool:
    return bool(get_access_token())
