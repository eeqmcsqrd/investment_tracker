# benchmark_components.py
# Dashboard components for benchmark comparisons

import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from datetime import datetime, timedelta
import numpy as np # type: ignore
from benchmark_service import get_all_benchmarks
from utils import apply_chart_styling

def create_benchmark_comparison_section(portfolio_returns, benchmark_returns, comparison_metrics, benchmark_name):
    """
    Create a dashboard section for benchmark comparison.
    
    Args:
        portfolio_returns (pandas.DataFrame): Portfolio returns data
        benchmark_returns (pandas.DataFrame): Benchmark returns data
        comparison_metrics (dict): Comparison metrics
        benchmark_name (str): Name of the benchmark
    """
    if portfolio_returns.empty or benchmark_returns.empty:
        st.warning("Insufficient data for benchmark comparison. Please ensure both portfolio and benchmark data are available for the selected date range.")
        return
    
    # Create a subheader for the benchmark comparison
    st.subheader(f"Portfolio vs {benchmark_name}")
    
    # Create charts for the comparison
    create_benchmark_comparison_chart(portfolio_returns, benchmark_returns, benchmark_name)
    
    # Display metrics
    create_benchmark_metrics_display(comparison_metrics, benchmark_name)
    
    # Add relative strength chart
    create_relative_strength_chart(portfolio_returns, benchmark_returns, benchmark_name)
    
    # Add detailed metrics explanation
    if st.checkbox("Show detailed metrics explanation", key="benchmark_metrics_explanation"):
        st.markdown("""
        ### Benchmark Comparison Metrics Explained
        
        - **Total Return**: The percentage change in value over the selected time period.
        - **Excess Return (Alpha)**: The return of your portfolio above (or below) the benchmark return.
        - **Volatility**: A measure of the dispersion of returns, shown as annualized standard deviation.
        - **Beta**: A measure of your portfolio's sensitivity to market movements. A beta of 1.0 means your portfolio moves with the market, >1.0 means more volatile than the market, <1.0 means less volatile.
        - **Tracking Error**: The standard deviation of the difference between your portfolio returns and the benchmark returns. Lower values indicate your portfolio follows the benchmark more closely.
        - **Information Ratio**: The excess return divided by tracking error. A higher ratio indicates better risk-adjusted performance relative to the benchmark.
        """)

def create_benchmark_comparison_chart(portfolio_returns, benchmark_returns, benchmark_name):
    """
    Create a chart comparing portfolio to benchmark performance.
    
    Args:
        portfolio_returns (pandas.DataFrame): Portfolio returns data
        benchmark_returns (pandas.DataFrame): Benchmark returns data
        benchmark_name (str): Name of the benchmark
    """
    # Create tabs for different chart views
    chart_tabs = st.tabs(["Cumulative Return", "Growth of $10,000", "Periodic Returns"])
    
    # Cumulative Return Tab
    with chart_tabs[0]:
        # Prepare data for cumulative return chart
        chart_data = []
        
        # Add portfolio data
        for _, row in portfolio_returns.iterrows():
            chart_data.append({
                'Date': row['Date'],
                'Cumulative Return (%)': row['CumulativeReturn'],
                'Source': 'Your Portfolio'
            })
        
        # Add benchmark data
        for _, row in benchmark_returns.iterrows():
            chart_data.append({
                'Date': row['Date'],
                'Cumulative Return (%)': row['CumulativeReturn'],
                'Source': benchmark_name
            })
        
        # Convert to DataFrame
        chart_df = pd.DataFrame(chart_data)
        
        # Create line chart
        fig = px.line(
            chart_df, 
            x='Date', 
            y='Cumulative Return (%)', 
            color='Source',
            title=f'Cumulative Return: Your Portfolio vs {benchmark_name}',
            color_discrete_map={'Your Portfolio': '#4361ee', benchmark_name: '#ff6b6b'}
        )
        
        # Enhance line styling
        fig.update_traces(
            line=dict(width=2.5)
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        
        # Apply styling with smart date formatting
        date_range = (chart_df['Date'].min(), chart_df['Date'].max())
        apply_chart_styling(
            fig,
            height=400,
            x_title="Date",
            y_title="Cumulative Return (%)",
            margin=dict(l=20, r=20, t=50, b=100),
            hovermode="x unified",
            date_range=date_range
        )
        
        # Add custom hover template
        fig.update_traces(
            hovertemplate='<b>%{y:.2f}%</b><br>%{x|%b %d, %Y}<extra></extra>'
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Growth of $10,000 Tab
    with chart_tabs[1]:
        # Prepare data for growth chart
        growth_data = []
        initial_investment = 10000
        
        # Add portfolio data
        for _, row in portfolio_returns.iterrows():
            growth_data.append({
                'Date': row['Date'],
                'Value ($)': initial_investment * (1 + row['CumulativeReturn']/100),
                'Source': 'Your Portfolio'
            })
        
        # Add benchmark data
        for _, row in benchmark_returns.iterrows():
            growth_data.append({
                'Date': row['Date'],
                'Value ($)': initial_investment * (1 + row['CumulativeReturn']/100),
                'Source': benchmark_name
            })
        
        # Convert to DataFrame
        growth_df = pd.DataFrame(growth_data)
        
        # Create line chart
        fig = px.line(
            growth_df, 
            x='Date', 
            y='Value ($)', 
            color='Source',
            title=f'Growth of $10,000: Your Portfolio vs {benchmark_name}',
            color_discrete_map={'Your Portfolio': '#4361ee', benchmark_name: '#ff6b6b'}
        )
        
        # Enhance line styling
        fig.update_traces(
            line=dict(width=2.5)
        )
        
        # Add initial investment line
        fig.add_hline(y=initial_investment, line_dash="dash", line_color="white", opacity=0.5)
        
        # Apply styling with smart date formatting
        date_range = (growth_df['Date'].min(), growth_df['Date'].max())
        apply_chart_styling(
            fig,
            height=400,
            x_title="Date",
            y_title="Value ($)",
            margin=dict(l=20, r=20, t=50, b=100),
            hovermode="x unified",
            date_range=date_range
        )
        
        # Add custom hover template
        fig.update_traces(
            hovertemplate='<b>$%{y:.2f}</b><br>%{x|%b %d, %Y}<extra></extra>'
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Periodic Returns Tab
    with chart_tabs[2]:
        # Allow user to select period
        period = st.radio(
            "Select period",
            ["Monthly", "Quarterly", "Yearly"],
            horizontal=True,
            key="periodic_returns_period"
        )
        
        # Optimized: determine period conversion once
        period_freq = {'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'Y'}[period]

        # Create periodic returns for portfolio (avoid redundant copy)
        portfolio_periodic = portfolio_returns.copy()
        portfolio_periodic['Period'] = portfolio_periodic['Date'].dt.to_period(period_freq).dt.to_timestamp()

        # Group by period
        portfolio_grouped = portfolio_periodic.groupby('Period')['Value'].last().reset_index()
        portfolio_grouped['Return'] = (
            portfolio_grouped['Value'].pct_change()
            .fillna(0) * 100        # ensures at least one bar
        )

        # Create periodic returns for benchmark (avoid redundant copy)
        benchmark_periodic = benchmark_returns.copy()
        benchmark_periodic['Period'] = benchmark_periodic['Date'].dt.to_period(period_freq).dt.to_timestamp()

        # Group by period
        benchmark_grouped = benchmark_periodic.groupby('Period')['Value'].last().reset_index()
        benchmark_grouped['Return'] = (
            benchmark_grouped['Value'].pct_change()
            .fillna(0) * 100
        )

        # Optimized: use concat instead of iterrows for better performance
        portfolio_grouped['Source'] = 'Your Portfolio'
        benchmark_grouped['Source'] = benchmark_name

        # Combine data
        portfolio_df = portfolio_grouped[['Period', 'Return', 'Source']].rename(columns={'Return': 'Return (%)'})
        benchmark_df = benchmark_grouped[['Period', 'Return', 'Source']].rename(columns={'Return': 'Return (%)'})

        periodic_df = pd.concat([portfolio_df, benchmark_df], ignore_index=True)
        
        if not periodic_df.empty:
            # Create bar chart
            fig = px.bar(
                periodic_df, 
                x='Period', 
                y='Return (%)', 
                color='Source',
                barmode='group',
                title=f'{period} Returns: Your Portfolio vs {benchmark_name}',
                color_discrete_map={'Your Portfolio': '#4361ee', benchmark_name: '#ff6b6b'}
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
            
            # Apply styling (no date_range for Period-based chart)
            apply_chart_styling(
                fig,
                height=400,
                x_title="Period",
                y_title="Return (%)",
                margin=dict(l=20, r=20, t=50, b=100),
                hovermode="closest"
            )
            
            # Add custom hover template
            fig.update_traces(
                hovertemplate='<b>%{y:.2f}%</b><br>%{x|%b %Y}<extra></extra>'
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info(f"Insufficient data for {period.lower()} returns analysis.")

def create_benchmark_metrics_display(comparison_metrics, benchmark_name):
    """
    Create a display of comparison metrics.
    
    Args:
        comparison_metrics (dict): Comparison metrics
        benchmark_name (str): Name of the benchmark
    """
    if not comparison_metrics:
        st.warning("Unable to calculate comparison metrics.")
        return
    
    st.subheader("Performance Summary")
    
    # Create three columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Portfolio return
        portfolio_return = comparison_metrics.get('portfolio_return', 0)
        portfolio_color = "green" if portfolio_return >= 0 else "red"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Your Portfolio</p>
            <p style="font-size: 1.5rem; color: {portfolio_color};">{portfolio_return:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Benchmark return
        benchmark_return = comparison_metrics.get('benchmark_return', 0)
        benchmark_color = "green" if benchmark_return >= 0 else "red"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">{benchmark_name}</p>
            <p style="font-size: 1.5rem; color: {benchmark_color};">{benchmark_return:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Excess return (alpha)
        excess_return = comparison_metrics.get('excess_return', 0)
        excess_color = "green" if excess_return >= 0 else "red"
        excess_sign = "+" if excess_return >= 0 else ""
        
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Excess Return</p>
            <p style="font-size: 1.5rem; color: {excess_color};">{excess_sign}{excess_return:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a separator
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Create a table for detailed metrics
    metrics_data = {
        'Metric': ['Volatility', 'Beta', 'Tracking Error', 'Information Ratio'],
        'Your Portfolio': [
            f"{comparison_metrics.get('portfolio_volatility', 0):.2f}%",
            f"{comparison_metrics.get('beta', 0):.2f}",
            "N/A",
            "N/A"
        ],
        benchmark_name: [
            f"{comparison_metrics.get('benchmark_volatility', 0):.2f}%",
            "1.00",
            "N/A",
            "N/A"
        ],
        'Comparison': [
            f"{(comparison_metrics.get('portfolio_volatility', 0) - comparison_metrics.get('benchmark_volatility', 0)):.2f}%",
            f"{comparison_metrics.get('beta', 0) - 1.0:.2f}",
            f"{comparison_metrics.get('tracking_error', 0):.2f}%",
            f"{comparison_metrics.get('information_ratio', 0):.2f}"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Add custom styling to the table
    # In a real app, you might want to add green/red coloring based on values
    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True
    )

def create_relative_strength_chart(portfolio_returns, benchmark_returns, benchmark_name):
    """
    Create a relative strength chart (portfolio/benchmark).
    
    Args:
        portfolio_returns (pandas.DataFrame): Portfolio returns data
        benchmark_returns (pandas.DataFrame): Benchmark returns data
        benchmark_name (str): Name of the benchmark
    """
    # Create a section for relative strength
    st.subheader("Relative Strength Analysis")
    
    # Create common date range
    common_dates = sorted(set(portfolio_returns['Date']).intersection(set(benchmark_returns['Date'])))
    
    if not common_dates:
        st.warning("Insufficient data for relative strength analysis.")
        return
    
    # Filter to common dates
    portfolio_filtered = portfolio_returns[portfolio_returns['Date'].isin(common_dates)].sort_values('Date')
    benchmark_filtered = benchmark_returns[benchmark_returns['Date'].isin(common_dates)].sort_values('Date')
    
    # Calculate relative strength (portfolio/benchmark)
    relative_strength_data = []
    
    for i in range(len(common_dates)):
        date = common_dates[i]
        
        # Get portfolio and benchmark values
        portfolio_value = portfolio_filtered[portfolio_filtered['Date'] == date]['Value'].iloc[0]
        benchmark_value = benchmark_filtered[benchmark_filtered['Date'] == date]['Value'].iloc[0]
        
        # Get initial values
        if i == 0:
            initial_portfolio = portfolio_value
            initial_benchmark = benchmark_value
        
        # Calculate normalized values (indexed to 100)
        normalized_portfolio = (portfolio_value / initial_portfolio) * 100
        normalized_benchmark = (benchmark_value / initial_benchmark) * 100
        
        # Calculate relative strength
        relative_strength = (normalized_portfolio / normalized_benchmark) * 100
        
        relative_strength_data.append({
            'Date': date,
            'Relative Strength': relative_strength,
            'Normalized Portfolio': normalized_portfolio,
            'Normalized Benchmark': normalized_benchmark
        })
    
    # Convert to DataFrame
    rs_df = pd.DataFrame(relative_strength_data)
    
    # Create tabs for different chart views
    rs_tabs = st.tabs(["Relative Strength", "Ratio Chart", "Performance Comparison"])
    
    # Relative Strength Tab
    with rs_tabs[0]:
        # Create relative strength chart
        fig = px.line(
            rs_df, 
            x='Date', 
            y='Relative Strength',
            title=f'Relative Strength: Your Portfolio vs {benchmark_name}',
            line_shape='spline'
        )
        
        # Add 100 line (equal performance)
        fig.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.5,
                    annotation_text="Equal Performance", annotation_position="bottom right")
        
        # Enhance line styling
        fig.update_traces(
            line=dict(width=2.5, color='#4361ee')
        )
        
        # Apply styling with smart date formatting
        date_range = (rs_df['Date'].min(), rs_df['Date'].max())
        apply_chart_styling(
            fig,
            height=400,
            x_title="Date",
            y_title="Relative Strength (Base=100)",
            margin=dict(l=20, r=20, t=50, b=100),
            hovermode="x unified",
            date_range=date_range
        )
        
        # Add custom hover template
        fig.update_traces(
            hovertemplate='<b>%{y:.2f}</b><br>%{x|%b %d, %Y}<extra></extra>'
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Add explanation
        st.markdown("""
        **How to interpret this chart:**
        - Values above 100 mean your portfolio is outperforming the benchmark.
        - Values below 100 mean your portfolio is underperforming the benchmark.
        - A rising line means your portfolio is gaining strength relative to the benchmark.
        - A falling line means your portfolio is losing strength relative to the benchmark.
        """)
    
    # Ratio Chart Tab
    with rs_tabs[1]:
        # Create normalized values chart
        fig = px.line(
            rs_df, 
            x='Date', 
            y=['Normalized Portfolio', 'Normalized Benchmark'],
            title=f'Normalized Performance: Your Portfolio vs {benchmark_name}',
            line_shape='spline',
            color_discrete_map={
                'Normalized Portfolio': '#4361ee',
                'Normalized Benchmark': '#ff6b6b'
            }
        )
        
        # Add 100 line (starting point)
        fig.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.5,
                    annotation_text="Starting Value", annotation_position="bottom right")
        
        # Enhance line styling
        fig.update_traces(
            line=dict(width=2.5)
        )
        
        # Apply styling with smart date formatting
        date_range = (rs_df['Date'].min(), rs_df['Date'].max())
        apply_chart_styling(
            fig,
            height=400,
            x_title="Date",
            y_title="Normalized Value (Base=100)",
            margin=dict(l=20, r=20, t=50, b=100),
            hovermode="x unified",
            date_range=date_range
        )
        
        # Add custom hover template
        fig.update_traces(
            hovertemplate='<b>%{y:.2f}</b><br>%{x|%b %d, %Y}<extra></extra>'
        )
        
        # Update legend name
        fig.update_layout(
            legend_title_text='',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Performance Comparison Tab
    with rs_tabs[2]:
        # Calculate the percentage of time portfolio outperforms benchmark
        rs_df['Outperforming'] = rs_df['Relative Strength'] > 100
        outperform_pct = (rs_df['Outperforming'].sum() / len(rs_df)) * 100
        
        # Calculate max outperformance and underperformance
        max_outperform = (rs_df['Relative Strength'].max() - 100) if rs_df['Relative Strength'].max() > 100 else 0
        max_underperform = (100 - rs_df['Relative Strength'].min()) if rs_df['Relative Strength'].min() < 100 else 0
        
        # Calculate average outperformance/underperformance
        avg_outperform = (rs_df[rs_df['Outperforming']]['Relative Strength'] - 100).mean() if not rs_df[rs_df['Outperforming']].empty else 0
        avg_underperform = (100 - rs_df[~rs_df['Outperforming']]['Relative Strength']).mean() if not rs_df[~rs_df['Outperforming']].empty else 0
        
        # Create summary metrics
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Time Outperforming</p>
                <p style="font-size: 1.5rem; color: {'green' if outperform_pct >= 50 else 'red'};">{outperform_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Maximum Outperformance</p>
                <p style="font-size: 1.5rem; color: green;">+{max_outperform:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Time Underperforming</p>
                <p style="font-size: 1.5rem; color: {'green' if outperform_pct < 50 else 'red'};">{100 - outperform_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem;">Maximum Underperformance</p>
                <p style="font-size: 1.5rem; color: red;">-{max_underperform:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add a chart to show outperformance periods
        # Create a column for coloring
        rs_df['Performance'] = rs_df['Relative Strength'].apply(
            lambda x: 'Outperforming' if x > 100 else 'Underperforming'
        )
        
        # Create a chart
        fig = px.scatter(
            rs_df,
            x='Date',
            y='Relative Strength',
            color='Performance',
            title='Performance Periods',
            color_discrete_map={
                'Outperforming': '#4ade80',
                'Underperforming': '#f87171'
            }
        )
        
        # Add the relative strength line
        fig.add_trace(
            go.Scatter(
                x=rs_df['Date'],
                y=rs_df['Relative Strength'],
                mode='lines',
                line=dict(color='#9ca3af', width=1),
                showlegend=False
            )
        )
        
        # Add 100 line (equal performance)
        fig.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.5,
                    annotation_text="Equal Performance", annotation_position="bottom right")
        
        # Apply styling with smart date formatting
        date_range = (rs_df['Date'].min(), rs_df['Date'].max())
        apply_chart_styling(
            fig,
            height=400,
            x_title="Date",
            y_title="Relative Strength (Base=100)",
            margin=dict(l=20, r=20, t=50, b=100),
            hovermode="closest",
            date_range=date_range
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

def create_benchmark_selector():
    """
    Create a benchmark selector with available benchmarks.
    
    Returns:
        str: Selected benchmark name
    """
    # Get all available benchmarks
    available_benchmarks = get_all_benchmarks()
    
    # Select benchmark
    benchmark_name = st.selectbox(
        "Select Benchmark",
        available_benchmarks,
        index=0 if available_benchmarks else 0,
        key="benchmark_selector"
    )
    
    return benchmark_name

def create_multi_benchmark_comparison(df, start_date, end_date, selected_benchmarks):
    """
    Create a comparison chart with multiple benchmarks.
    
    Args:
        df (pandas.DataFrame): Investment data
        start_date (datetime): Start date for comparison
        end_date (datetime): End date for comparison
        selected_benchmarks (list): List of benchmark names to compare against
    """
    from data_handler_db import get_benchmark_comparison
    
    if not selected_benchmarks:
        st.warning("Please select at least one benchmark for comparison.")
        return
    
    # Create portfolio data
    portfolio_df = None
    benchmark_dfs = []
    
    for benchmark in selected_benchmarks:
        portfolio_returns, benchmark_returns, _ = get_benchmark_comparison(df, benchmark, start_date, end_date)
        
        if portfolio_returns is not None and not portfolio_returns.empty:
            portfolio_df = portfolio_returns
        
        if benchmark_returns is not None and not benchmark_returns.empty:
            benchmark_dfs.append((benchmark, benchmark_returns))
    
    if portfolio_df is None or not benchmark_dfs:
        st.warning("Insufficient data for multi-benchmark comparison.")
        return
    
    # Create chart data
    chart_data = []
    
    # Add portfolio data
    for _, row in portfolio_df.iterrows():
        chart_data.append({
            'Date': row['Date'],
            'Cumulative Return (%)': row['CumulativeReturn'],
            'Source': 'Your Portfolio'
        })
    
    # Add benchmark data
    for benchmark_name, benchmark_df in benchmark_dfs:
        for _, row in benchmark_df.iterrows():
            chart_data.append({
                'Date': row['Date'],
                'Cumulative Return (%)': row['CumulativeReturn'],
                'Source': benchmark_name
            })
    
    # Convert to DataFrame
    chart_df = pd.DataFrame(chart_data)
    
    # Create line chart
    fig = px.line(
        chart_df, 
        x='Date', 
        y='Cumulative Return (%)', 
        color='Source',
        title='Portfolio vs Multiple Benchmarks',
        line_shape='spline'
    )
    
    # Highlight the portfolio line
    for trace in fig.data:
        if trace.name == 'Your Portfolio':
            trace.line.width = 3
            trace.line.color = '#4361ee'
            trace.line.dash = 'solid'
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    
    # Apply styling with smart date formatting
    date_range = (chart_df['Date'].min(), chart_df['Date'].max())
    apply_chart_styling(
        fig,
        height=500,
        x_title="Date",
        y_title="Cumulative Return (%)",
        margin=dict(l=20, r=20, t=50, b=100),
        hovermode="x unified",
        date_range=date_range
    )
    
    # Add custom hover template
    fig.update_traces(
        hovertemplate='<b>%{y:.2f}%</b><br>%{x|%b %d, %Y}<extra></extra>'
    )
    
    # Update legend
    fig.update_layout(
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})