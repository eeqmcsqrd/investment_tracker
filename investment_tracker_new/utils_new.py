
# utils_new.py
import streamlit as st

def apply_theme(theme):
    """Applies the selected theme."""
    if theme == "Dark":
        st.markdown("<style>body {background-color: #1E1E1E; color: white;}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>body {background-color: white; color: black;}</style>", unsafe_allow_html=True)
