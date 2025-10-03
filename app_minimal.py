# app_minimal.py - Absolute minimum app to test functionality

import streamlit as st
import sys

# Initialize database
try:
    import init_database
    result = init_database.init_database_from_snapshot()
    st.sidebar.success(f"✅ Database initialized: {result}")
except Exception as e:
    st.sidebar.error(f"DB Error: {e}")
    import traceback
    st.sidebar.code(traceback.format_exc())

# Authentication
try:
    import auth_wrapper
    if not auth_wrapper.check_password():
        st.stop()
    auth_wrapper.add_logout_button()
except Exception as e:
    st.sidebar.warning(f"Auth bypassed: {e}")

# Minimal app
st.title("🧪 Minimal Investment Tracker Test")

try:
    import pandas as pd
    import sqlite3
    
    # Load data
    conn = sqlite3.connect('investment_data.db')
    df = pd.read_sql_query("SELECT * FROM investments", conn, parse_dates=['Date'])
    conn.close()
    
    st.success(f"✅ Loaded {len(df)} records from database")
    
    # Time range selector
    st.subheader("Select Time Range")
    time_option = st.radio(
        "Choose period:",
        ["1 Month", "3 Months", "6 Months", "1 Year", "All Time"],
        horizontal=True
    )
    
    st.write(f"Selected: **{time_option}**")
    
    # Filter data based on selection
    from datetime import datetime, timedelta
    end_date = df['Date'].max()
    
    if time_option == "1 Month":
        start_date = end_date - timedelta(days=30)
    elif time_option == "3 Months":
        start_date = end_date - timedelta(days=90)
    elif time_option == "6 Months":
        start_date = end_date - timedelta(days=180)
    elif time_option == "1 Year":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = df['Date'].min()
    
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    st.info(f"📊 Showing {len(filtered_df)} records from {start_date.date()} to {end_date.date()}")
    
    # Show simple data
    st.dataframe(filtered_df.head(20), use_container_width=True)
    
    # Try simple chart
    st.subheader("Simple Line Chart Test")
    daily_totals = filtered_df.groupby('Date')['ValueUSD'].sum().reset_index()
    st.line_chart(daily_totals.set_index('Date'))
    
    st.success("✅ All tests passed! No crashes!")
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    st.code(traceback.format_exc())
    sys.stderr.write(f"ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)
