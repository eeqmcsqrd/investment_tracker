
# benchmark_components_new.py
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

def get_benchmark_data(benchmark, start_date, end_date):
    """Fetches benchmark data from Yahoo Finance."""
    ticker = yf.Ticker(benchmark)
    data = ticker.history(start=start_date, end=end_date)
    return data

def create_benchmark_comparison_chart(df, benchmark, start_date, end_date):
    """Creates the benchmark comparison chart."""
    st.subheader(f"Portfolio vs. {benchmark}")

    # Get portfolio data
    portfolio_df = df.groupby('date')['value'].sum().reset_index()
    portfolio_df = portfolio_df.rename(columns={'value': 'Portfolio'})
    portfolio_df['Portfolio_pct_change'] = portfolio_df['Portfolio'].pct_change().cumsum() * 100

    # Get benchmark data
    benchmark_df = get_benchmark_data(benchmark, start_date, end_date)
    benchmark_df = benchmark_df[['Close']].rename(columns={'Close': benchmark})
    benchmark_df[f'{benchmark}_pct_change'] = benchmark_df[benchmark].pct_change().cumsum() * 100

    # Merge dataframes
    merged_df = pd.merge(portfolio_df, benchmark_df, on='date', how='inner')

    # Create chart
    fig = px.line(merged_df, x='date', y=['Portfolio_pct_change', f'{benchmark}_pct_change'], title=f"Portfolio vs. {benchmark}")
    st.plotly_chart(fig, use_container_width=True)
