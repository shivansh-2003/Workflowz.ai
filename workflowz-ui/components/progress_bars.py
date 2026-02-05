import streamlit as st


def render_progress(label: str, value: int) -> None:
    st.markdown(f"**{label}**")
    st.progress(int(value))
