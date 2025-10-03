# app_simple.py - Simplified main app without problematic components

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
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
    st.warning(f"Auth bypassed")

# Page config
st.set_page_config(
    page_title="Investment Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Investment Tracker")

# Load data
try:
    from data_handler_db import load_data
    from currency_service import get_conversion_rate
    
    df = load_data()
    
    # Add ValueUSD if missing
    if 'ValueUSD' not in df.columns:
        df['ValueUSD'] = df.apply(lambda row: row['Value'] * get_conversion_rate(row['Currency']), axis=1)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Sidebar - Time Range Selection
st.sidebar.header("📅 Time Range")
time_option = st.sidebar.selectbox(
    "Select Period:",
    ["1 Month", "3 Months", "6 Months", "1 Year", "All Time"]
)

# Calculate date range
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

# Filter data
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

st.sidebar.success(f"📊 {len(filtered_df)} records")
st.sidebar.info(f"From: {start_date.date()}\nTo: {end_date.date()}")

# Main Dashboard
col1, col2, col3 = st.columns(3)

with col1:
    current_value = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]['ValueUSD'].sum()
    st.metric("💵 Current Value", f"${current_value:,.2f}")

with col2:
    start_value = filtered_df[filtered_df['Date'] == filtered_df['Date'].min()]['ValueUSD'].sum()
    change = current_value - start_value
    change_pct = (change / start_value * 100) if start_value > 0 else 0
    st.metric("📈 Change", f"${change:,.2f}", f"{change_pct:+.2f}%")

with col3:
    num_investments = filtered_df['Investment'].nunique()
    st.metric("🏦 Investments", num_investments)

# Portfolio Performance Chart
st.subheader("📊 Portfolio Performance")
try:
    daily_totals = filtered_df.groupby('Date')['ValueUSD'].sum().reset_index()
    fig = px.line(daily_totals, x='Date', y='ValueUSD', 
                  title=f'Portfolio Value - {time_option}')
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        hovermode='x unified',
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Chart error: {e}")
    st.code(traceback.format_exc())

# Investment Breakdown
st.subheader("🏦 Investment Breakdown")
try:
    latest = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
    breakdown = latest.groupby('Investment')['ValueUSD'].sum().sort_values(ascending=False)
    
    fig = px.pie(values=breakdown.values, names=breakdown.index,
                 title='Current Allocation')
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Breakdown error: {e}")

# Recent Data
st.subheader("📋 Recent Data")
st.dataframe(
    filtered_df.sort_values('Date', ascending=False).head(50),
    use_container_width=True,
    hide_index=True
)

st.success("✅ App loaded successfully!")
