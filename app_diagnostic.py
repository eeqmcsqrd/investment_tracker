# app_diagnostic.py - Test each component individually

import streamlit as st
import sys
import traceback

# Initialize database
try:
    import init_database
    init_database.init_database_from_snapshot()
except Exception as e:
    st.error(f"DB Init Error: {e}")

# Authentication
try:
    import auth_wrapper
    if not auth_wrapper.check_password():
        st.stop()
    auth_wrapper.add_logout_button()
except Exception as e:
    st.warning(f"Auth bypassed: {e}")

st.title("🔍 Investment Tracker - Component Diagnostic")

# Test 1: Data Loading
st.header("Test 1: Data Loading")
try:
    from data_handler_db import load_data
    df = load_data()
    st.success(f"✅ Loaded {len(df)} records")
    st.write(f"Columns: {list(df.columns)}")
except Exception as e:
    st.error(f"❌ Data loading failed: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Test 2: Date Range Filtering
st.header("Test 2: Date Range Filtering")
try:
    from datetime import timedelta
    end_date = df['Date'].max()
    start_date = end_date - timedelta(days=30)
    filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    st.success(f"✅ Filtered to {len(filtered)} records")
except Exception as e:
    st.error(f"❌ Filtering failed: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Test 3: Currency Conversion
st.header("Test 3: Currency Conversion")
try:
    from currency_service import get_conversion_rate
    rate = get_conversion_rate('USD')
    st.success(f"✅ Currency service works (USD rate: {rate})")
    
    if 'ValueUSD' not in df.columns:
        df['ValueUSD'] = df.apply(lambda row: row['Value'] * get_conversion_rate(row['Currency']), axis=1)
        st.info("Added ValueUSD column")
except Exception as e:
    st.error(f"❌ Currency conversion failed: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Test 4: Dashboard Components
st.header("Test 4: Dashboard Components")
try:
    from dashboard_components import create_portfolio_performance_chart
    st.write("Testing portfolio performance chart...")

    # Prepare data with latest_date
    latest_date = df['Date'].max()

    # This function displays directly, doesn't return a figure
    # Correct signature: df, latest_date, start_date, end_date
    create_portfolio_performance_chart(df, latest_date, start_date, end_date)
    st.success("✅ Dashboard component works!")
except Exception as e:
    st.error(f"❌ Dashboard component failed: {e}")
    st.code(traceback.format_exc())
    sys.stderr.write(f"DASHBOARD ERROR: {e}\n")
    traceback.print_exc(file=sys.stderr)

# Test 5: Simple Plotly Chart
st.header("Test 5: Simple Plotly Chart")
try:
    import plotly.express as px

    # Ensure filtered dataframe has ValueUSD column
    if 'ValueUSD' not in filtered.columns:
        from currency_service import get_conversion_rate
        filtered['ValueUSD'] = filtered.apply(lambda row: row['Value'] * get_conversion_rate(row['Currency']), axis=1)

    daily_totals = filtered.groupby('Date')['ValueUSD'].sum().reset_index()
    fig = px.line(daily_totals, x='Date', y='ValueUSD', title='Simple Test Chart')
    st.plotly_chart(fig, use_container_width=True)
    st.success("✅ Plotly charts work!")
except Exception as e:
    st.error(f"❌ Plotly chart failed: {e}")
    st.code(traceback.format_exc())

st.success("🎉 Diagnostic complete!")
