# app_stable.py - Stable version using simple components from app_simple but auth from main app

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
except:
    pass

# Page config
st.set_page_config(
    page_title="Investment Tracker",
    page_icon="💰",
    layout="wide"
)

# Load data
try:
    from data_handler_db import load_data
    from currency_service import get_conversion_rate
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please add investment data.")
        st.stop()
    
    # Add ValueUSD
    if 'ValueUSD' not in df.columns:
        df['ValueUSD'] = df.apply(lambda row: row['Value'] * get_conversion_rate(row['Currency']), axis=1)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Title
st.title("💰 Investment Tracker")

# Sidebar - Time Range Selection (using session state like main app)
if 'start_date' not in st.session_state:
    st.session_state.start_date = df['Date'].min()
if 'end_date' not in st.session_state:
    st.session_state.end_date = df['Date'].max()

with st.sidebar:
    st.header("📅 Date Range")
    
    time_option = st.selectbox(
        "Select Period:",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All Time"],
        index=1  # Default to 1 Month
    )
    
    # Calculate date range based on selection
    end_date = df['Date'].max()
    if time_option == "1 Week":
        start_date = end_date - timedelta(days=7)
    elif time_option == "1 Month":
        start_date = end_date - timedelta(days=30)
    elif time_option == "3 Months":
        start_date = end_date - timedelta(days=90)
    elif time_option == "6 Months":
        start_date = end_date - timedelta(days=180)
    elif time_option == "1 Year":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = df['Date'].min()
    
    # Update session state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    
    st.success(f"📊 {time_option}")
    st.info(f"From: {start_date.date()}\nTo: {end_date.date()}")

# Filter data
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

st.info(f"📊 Showing {len(filtered_df)} records from {start_date.date()} to {end_date.date()}")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Data", "⚙️ Settings"])

with tab1:
    # Metrics
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
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")
    
    # Investment Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏦 Investment Breakdown")
        try:
            latest = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
            breakdown = latest.groupby('Investment')['ValueUSD'].sum().sort_values(ascending=False)
            
            fig = px.pie(values=breakdown.values, names=breakdown.index,
                         title='Current Allocation')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Breakdown error: {e}")
    
    with col2:
        st.subheader("📈 Top Investments")
        try:
            latest = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
            top = latest.groupby('Investment')['ValueUSD'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(x=top.values, y=top.index, orientation='h',
                         labels={'x': 'Value (USD)', 'y': 'Investment'},
                         title='Top 10 by Value')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Top investments error: {e}")

with tab2:
    st.header("📋 Investment Data")
    
    # Show recent data
    st.dataframe(
        filtered_df.sort_values('Date', ascending=False).head(100),
        use_container_width=True,
        hide_index=True
    )
    
    # Summary stats
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Date Range", f"{(filtered_df['Date'].max() - filtered_df['Date'].min()).days} days")
    with col3:
        st.metric("Avg Daily Value", f"${filtered_df.groupby('Date')['ValueUSD'].sum().mean():,.2f}")
    with col4:
        st.metric("Unique Investments", filtered_df['Investment'].nunique())

with tab3:
    st.header("⚙️ Settings")
    st.info("Settings and data management features coming soon!")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

st.success("✅ App loaded successfully!")
