# app_db_authenticated.py
# Wrapper for app_db.py with authentication enabled
# Use this as your main file for Streamlit Cloud deployment

import auth_wrapper

# Check authentication before loading the app
if not auth_wrapper.check_password():
    import streamlit as st
    st.stop()

# Import and run the main app
from app_db import *

# Add logout button to sidebar
auth_wrapper.add_logout_button()
