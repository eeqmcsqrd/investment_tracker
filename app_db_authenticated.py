# app_db_authenticated.py
# Wrapper for app_db.py with authentication enabled
# Use this as your main file for Streamlit Cloud deployment

import streamlit as st
import sys
import traceback

# Initialize database from snapshot if needed (for cloud deployment)
try:
    import init_database
    init_database.init_database_from_snapshot()
except Exception as e:
    st.error(f"❌ Database initialization error: {e}")
    st.code(traceback.format_exc())
    sys.stderr.write(f"INIT ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)

# Authentication
try:
    import auth_wrapper
    if not auth_wrapper.check_password():
        st.stop()
except Exception as e:
    st.error(f"❌ Authentication error: {e}")
    st.code(traceback.format_exc())
    sys.stderr.write(f"AUTH ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)
    st.stop()

# Main app with error handling
try:
    from app_db import *
    auth_wrapper.add_logout_button()
except Exception as e:
    st.error(f"❌ Application Error")
    st.error(f"Error: {e}")
    st.code(traceback.format_exc())
    sys.stderr.write(f"APP ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)
    st.stop()
