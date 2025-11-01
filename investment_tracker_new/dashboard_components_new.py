
# dashboard_components_new.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_dashboard_header(df):
    """Creates the header metrics for the dashboard."""
    st.header("Dashboard")
    
    if not df.empty:
        # Calculate metrics
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        total_usd = latest_df['value'].sum() # Assuming all values are in USD for now

        one_month_ago = latest_date - timedelta(days=30)
        month_ago_df = df[df['date'] <= one_month_ago]
        
        if not month_ago_df.empty:
            month_ago_total = month_ago_df[month_ago_df['date'] == month_ago_df['date'].max()]['value'].sum()
            month_change = total_usd - month_ago_total
        else:
            month_change = 0

        three_months_ago = latest_date - timedelta(days=90)
        three_months_ago_df = df[df['date'] <= three_months_ago]

        if not three_months_ago_df.empty:
            three_months_ago_total = three_months_ago_df[three_months_ago_df['date'] == three_months_ago_df['date'].max()]['value'].sum()
            three_month_change = total_usd - three_months_ago_total
        else:
            three_month_change = 0

        ytd_start = datetime(latest_date.year, 1, 1).date()
        ytd_df = df[df['date'] < pd.to_datetime(ytd_start)]

        if not ytd_df.empty:
            ytd_total = ytd_df[ytd_df['date'] == ytd_df['date'].max()]['value'].sum()
            ytd_change = total_usd - ytd_total
        else:
            ytd_change = 0

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Portfolio Value", f"${total_usd:,.2f}")
        col2.metric("1 Month Change", f"${month_change:,.2f}")
        col3.metric("3 Month Change", f"${three_month_change:,.2f}")
        col4.metric("YTD Change", f"${ytd_change:,.2f}")

        # Export button
        html = "<h1>Investment Dashboard</h1>"
        st.download_button("Export as HTML", html, "dashboard.html", "text/html")

def create_asset_allocation_chart(df):
    """Creates the asset allocation chart."""
    st.subheader("Asset Allocation")
    if not df.empty:
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        fig = px.pie(latest_df, values='value', names='investment', title='Asset Allocation')
        st.plotly_chart(fig, use_container_width=True)

def create_currency_breakdown_chart(df):
    """Creates the currency breakdown chart."""
    st.subheader("Currency Breakdown")
    if not df.empty:
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        fig = px.pie(latest_df, values='value', names='currency', title='Currency Breakdown')
        st.plotly_chart(fig, use_container_width=True)

def create_category_breakdown_chart(df, investment_categories):
    """Creates the category breakdown chart."""
    st.subheader("Category Breakdown")
    if not df.empty:
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date].copy()
        latest_df['category'] = latest_df['investment'].map(investment_categories)
        fig = px.pie(latest_df, values='value', names='category', title='Category Breakdown')
        st.plotly_chart(fig, use_container_width=True)

def create_investment_change_table(df):
    """Creates the investment change table."""
    st.subheader("Investment Value Changes")
    if not df.empty:
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        
        # Get previous values
        prev_date = df[df['date'] < latest_date]['date'].max()
        prev_df = df[df['date'] == prev_date]

        merged_df = pd.merge(latest_df, prev_df, on='investment', suffixes=['_latest', '_prev'])
        merged_df['change'] = merged_df['value_latest'] - merged_df['value_prev']

        st.dataframe(merged_df[['investment', 'value_latest', 'value_prev', 'change']])

def create_portfolio_performance_chart(df):
    """Creates the portfolio performance chart."""
    st.subheader("Portfolio Performance Over Time")
    if not df.empty:
        performance_df = df.groupby('date')['value'].sum().reset_index()
        fig = px.line(performance_df, x='date', y='value', title='Portfolio Performance')
        st.plotly_chart(fig, use_container_width=True)
