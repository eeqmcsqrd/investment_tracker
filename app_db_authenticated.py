# app_db_authenticated.py
# Wrapper for app_db.py with authentication enabled
# Use this as your main file for Streamlit Cloud deployment

import streamlit as st
import sys
import traceback
import os
import re

# Set page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="Investment Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    auth_wrapper.add_logout_button()
except Exception as e:
    st.error(f"❌ Authentication error: {e}")
    st.code(traceback.format_exc())
    sys.stderr.write(f"AUTH ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)
    st.stop()

# Main app with error handling
# CRITICAL FIX: Read and execute app_db.py code instead of importing
# This prevents the duplicate st.set_page_config() error
try:
    app_db_path = os.path.join(os.path.dirname(__file__) or '.', 'app_db.py')

    with open(app_db_path, 'r', encoding='utf-8') as f:
        app_code = f.read()

    # Remove the st.set_page_config call completely (including multiline params)
    # This regex handles multiline set_page_config calls
    app_code = re.sub(
        r'st\.set_page_config\s*\([^)]*\)',
        '# set_page_config already called in wrapper',
        app_code,
        flags=re.DOTALL,
        count=1
    )

    # Execute the app code in the current namespace
    exec(app_code, globals())

except FileNotFoundError:
    st.error("❌ app_db.py not found!")
    st.info("Make sure app_db.py is in the same directory.")
    st.stop()
except Exception as e:
    st.error(f"❌ Application Error")
    st.error(f"Error: {e}")
    with st.expander("Show full error details"):
        st.code(traceback.format_exc())
    sys.stderr.write(f"APP ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)
    # Don't stop - show what we can
