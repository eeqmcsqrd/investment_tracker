
# performance_components_new.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_performance_date_filter(df):
    """Creates the date filter for the performance tab."""
    st.header("Select Time Range")
    
    if not df.empty:
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        return start_date, end_date
    else:
        return None, None

def create_portfolio_value_chart(df, start_date, end_date):
    """Creates the portfolio value over time chart."""
    st.subheader("Portfolio Value Over Time")
    
    if not df.empty and start_date and end_date:
        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
        filtered_df = df.loc[mask]
        
        if not filtered_df.empty:
            performance_df = filtered_df.groupby('date')['value'].sum().reset_index()
            fig = px.line(performance_df, x='date', y='value', title='Portfolio Value Over Time')
            st.plotly_chart(fig, use_container_width=True)

def create_investment_comparison_chart(df, start_date, end_date):
    """Creates the investment performance comparison chart."""
    st.subheader("Investment Performance Comparison")
    
    if not df.empty and start_date and end_date:
        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
        filtered_df = df.loc[mask]
        
        if not filtered_df.empty:
            # Pivot the dataframe to have investments as columns
            pivot_df = filtered_df.pivot(index='date', columns='investment', values='value')
            
            # Calculate percentage change
            pct_change_df = pivot_df.div(pivot_df.iloc[0]).subtract(1).multiply(100)
            
            fig = px.line(pct_change_df, title='Investment Performance Comparison (% change)')
            st.plotly_chart(fig, use_container_width=True)

def create_performance_metrics_table(df, start_date, end_date):
    """Creates the performance metrics table."""
    st.subheader("Performance Metrics")
    
    if not df.empty and start_date and end_date:
        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
        filtered_df = df.loc[mask]
        
        if not filtered_df.empty:
            start_df = filtered_df[filtered_df['date'] == filtered_df['date'].min()]
            end_df = filtered_df[filtered_df['date'] == filtered_df['date'].max()]

            merged_df = pd.merge(start_df, end_df, on='investment', suffixes=['_start', '_end'])
            merged_df['change'] = merged_df['value_end'] - merged_df['value_start']
            merged_df['pct_change'] = (merged_df['change'] / merged_df['value_start']) * 100

            st.dataframe(merged_df[['investment', 'value_start', 'value_end', 'change', 'pct_change']])
