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

    # Remove the entire st.set_page_config block (including multiline params)
    # Using a more robust approach: find the call and count parentheses
    lines = app_code.split('\n')
    new_lines = []
    in_config = False
    paren_count = 0

    for line in lines:
        if 'st.set_page_config' in line and not in_config:
            in_config = True
            paren_count = line.count('(') - line.count(')')
            new_lines.append('# set_page_config already called in wrapper')
            if paren_count <= 0:
                in_config = False
        elif in_config:
            paren_count += line.count('(') - line.count(')')
            # Skip this line (it's part of set_page_config)
            if paren_count <= 0:
                in_config = False
        else:
            new_lines.append(line)

    app_code = '\n'.join(new_lines)

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
