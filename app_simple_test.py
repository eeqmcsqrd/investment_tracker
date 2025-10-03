# app_simple_test.py
# Minimal test app to diagnose the crash

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("🧪 Simple Test App")

# Test 1: Basic functionality
st.header("Test 1: Basic Display")
st.write("If you see this, Streamlit is working!")

# Test 2: Date selection
st.header("Test 2: Date Selection")
time_range = st.selectbox("Select Time Range:", ["1 Week", "1 Month", "3 Months", "All Time"])
st.write(f"You selected: {time_range}")

# Test 3: Simple chart
st.header("Test 3: Simple Chart")
if st.button("Generate Simple Chart"):
    # Create simple data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    values = pd.Series(range(len(dates)), index=dates)
    
    st.line_chart(values)
    st.success("Chart rendered successfully!")

# Test 4: Database check
st.header("Test 4: Database Check")
import os
if os.path.exists('investment_data.db'):
    st.success("✅ Database file found!")
    
    # Try to read from it
    try:
        import sqlite3
        conn = sqlite3.connect('investment_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        st.write(f"Tables found: {tables}")
        conn.close()
    except Exception as e:
        st.error(f"Error reading database: {e}")
else:
    st.warning("⚠️ Database file NOT found - this is why the main app crashes!")
    st.info("Upload your investment_data.db file to fix the main app")

st.success("✅ All tests completed without crashing!")
