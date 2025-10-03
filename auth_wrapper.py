# auth_wrapper.py
# Optional authentication wrapper for Streamlit Cloud deployment
# Protects your investment tracker with password authentication

import streamlit as st
import hashlib
import os

def check_password():
    """
    Returns `True` if the user has entered the correct password.
    """
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from Streamlit secrets or environment variable
        correct_password = st.secrets.get("AUTH_PASSWORD", os.getenv("AUTH_PASSWORD", ""))
        
        if not correct_password:
            # No password configured - allow access
            st.session_state["password_correct"] = True
            return
        
        # Hash the entered password for comparison
        entered_password = st.session_state["password"]
        
        if entered_password == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run - check if already authenticated
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # Return True if already authenticated
    if st.session_state["password_correct"]:
        return True

    # Show password input
    st.markdown("### 🔐 Investment Tracker - Authentication Required")
    st.text_input(
        "Enter Password", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Incorrect password")
    
    st.info("💡 **First time setup**: Add `AUTH_PASSWORD` to Streamlit Cloud Secrets")
    
    with st.expander("📖 How to set up authentication"):
        st.markdown("""
        1. Go to your app dashboard on Streamlit Cloud
        2. Click on **Settings** → **Secrets**
        3. Add the following line:
        ```toml
        AUTH_PASSWORD = "your_secure_password_here"
        ```
        4. Save and reboot your app
        5. Now only people with the password can access your data
        
        **Security Tip**: Use a strong, unique password that you don't use elsewhere.
        """)
    
    return False


def add_logout_button():
    """
    Add a logout button to the sidebar.
    """
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()


# Example usage in your main app:
# 
# import auth_wrapper
# 
# if not auth_wrapper.check_password():
#     st.stop()
# 
# # Your app code here
# auth_wrapper.add_logout_button()
