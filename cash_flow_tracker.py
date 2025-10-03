# cash_flow_tracker.py
"""
Cash flow and contribution tracking for investment portfolios.
Distinguishes between investment returns and new contributions/withdrawals.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime


def infer_cash_flows(df):
    """
    Infer cash flows (deposits/withdrawals) by comparing actual value changes
    to expected value changes based on returns.

    This is an approximation when actual transaction data is not available.

    Args:
        df (pd.DataFrame): DataFrame with Date, Investment, and ValueUSD columns

    Returns:
        pd.DataFrame: DataFrame with Date, Investment, InferredCashFlow, and TotalValue
    """
    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(['Investment', 'Date']).copy()

    # Group by investment
    cash_flows = []

    for investment in df['Investment'].unique():
        inv_df = df[df['Investment'] == investment].copy()

        if len(inv_df) < 2:
            continue

        # Calculate daily value changes
        inv_df['PrevValue'] = inv_df['ValueUSD'].shift(1)
        inv_df['ValueChange'] = inv_df['ValueUSD'] - inv_df['PrevValue']

        # Calculate expected value change based on portfolio return
        # (approximation: assumes all investments have similar returns)
        total_values = df.groupby('Date')['ValueUSD'].sum().reset_index()
        total_values['TotalReturn'] = total_values['ValueUSD'].pct_change()

        # Merge total returns
        inv_df = inv_df.merge(
            total_values[['Date', 'TotalReturn']],
            on='Date',
            how='left'
        )

        # Expected change = previous value * portfolio return
        inv_df['ExpectedChange'] = inv_df['PrevValue'] * inv_df['TotalReturn']

        # Cash flow = actual change - expected change
        inv_df['InferredCashFlow'] = inv_df['ValueChange'] - inv_df['ExpectedChange']

        # First entry is treated as initial deposit
        inv_df.loc[inv_df.index[0], 'InferredCashFlow'] = inv_df.iloc[0]['ValueUSD']

        # Add to results
        for _, row in inv_df.iterrows():
            if pd.notna(row['InferredCashFlow']):
                cash_flows.append({
                    'Date': row['Date'],
                    'Investment': investment,
                    'InferredCashFlow': row['InferredCashFlow'],
                    'TotalValue': row['ValueUSD']
                })

    return pd.DataFrame(cash_flows)


def calculate_money_weighted_return(cash_flows_df):
    """
    Calculate money-weighted return (IRR) for the portfolio.

    Args:
        cash_flows_df (pd.DataFrame): DataFrame with Date and InferredCashFlow

    Returns:
        float: Money-weighted return as a percentage
    """
    if cash_flows_df.empty or len(cash_flows_df) < 2:
        return 0.0

    # Sort by date
    cash_flows_df = cash_flows_df.sort_values('Date')

    # Get start and end dates
    start_date = cash_flows_df['Date'].min()
    end_date = cash_flows_df['Date'].max()

    # Calculate days from start for each cash flow
    cash_flows_df['DaysFromStart'] = (cash_flows_df['Date'] - start_date).dt.days

    # Prepare cash flows for IRR calculation
    # Positive = inflow (deposit), Negative = outflow (withdrawal)
    # We need to negate since we're the investor
    cf_list = []
    for _, row in cash_flows_df.iterrows():
        cf_list.append({
            'date': row['Date'],
            'days': row['DaysFromStart'],
            'amount': -row['InferredCashFlow']  # Negative because deposits are outflows for us
        })

    # Add final value as positive cash flow
    final_value = cash_flows_df['TotalValue'].iloc[-1]
    total_days = (end_date - start_date).days

    cf_list.append({
        'date': end_date,
        'days': total_days,
        'amount': final_value
    })

    # Use numpy's IRR approximation
    try:
        # Simple approximation using XIRR-like calculation
        # For proper XIRR, you'd need scipy.optimize
        total_invested = cash_flows_df['InferredCashFlow'].sum()
        if total_invested <= 0:
            return 0.0

        simple_return = (final_value / total_invested - 1) * 100
        years = total_days / 365.25
        if years > 0:
            annualized_return = ((final_value / total_invested) ** (1 / years) - 1) * 100
            return annualized_return
        else:
            return simple_return
    except Exception:
        return 0.0


def calculate_time_weighted_return(df):
    """
    Calculate time-weighted return (TWRR) for the portfolio.
    This removes the impact of cash flows and shows pure investment performance.

    Args:
        df (pd.DataFrame): DataFrame with Date and ValueUSD

    Returns:
        float: Time-weighted return as a percentage
    """
    if df.empty or len(df) < 2:
        return 0.0

    df = df.sort_values('Date')

    # Calculate daily returns
    daily_returns = df['ValueUSD'].pct_change().dropna()

    if daily_returns.empty:
        return 0.0

    # Compound the returns
    cumulative_return = (1 + daily_returns).prod() - 1

    # Annualize based on time period
    days = (df['Date'].max() - df['Date'].min()).days
    if days > 0:
        years = days / 365.25
        annualized_return = ((1 + cumulative_return) ** (1 / years) - 1) * 100
        return annualized_return
    else:
        return cumulative_return * 100


def create_cash_flow_waterfall(cash_flows_df, investment=None):
    """
    Create a waterfall chart showing cash flows over time.

    Args:
        cash_flows_df (pd.DataFrame): DataFrame with Date and InferredCashFlow
        investment (str, optional): Specific investment to show, or None for all

    Returns:
        plotly.graph_objects.Figure: Waterfall chart
    """
    if cash_flows_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Cash Flow Analysis",
            annotations=[dict(
                text="No cash flow data available",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )]
        )
        return fig

    # Filter by investment if specified
    if investment:
        plot_df = cash_flows_df[cash_flows_df['Investment'] == investment].copy()
        title = f"Cash Flows: {investment}"
    else:
        # Aggregate all investments by date
        plot_df = cash_flows_df.groupby('Date').agg({
            'InferredCashFlow': 'sum',
            'TotalValue': 'sum'
        }).reset_index()
        title = "Portfolio Cash Flows"

    plot_df = plot_df.sort_values('Date')

    # Create cumulative cash flow
    plot_df['CumulativeCashFlow'] = plot_df['InferredCashFlow'].cumsum()

    # Create waterfall chart
    fig = go.Figure()

    # Add bars for each period
    colors = ['green' if x >= 0 else 'red' for x in plot_df['InferredCashFlow']]

    fig.add_trace(go.Bar(
        x=plot_df['Date'],
        y=plot_df['InferredCashFlow'],
        marker_color=colors,
        name='Cash Flow',
        text=plot_df['InferredCashFlow'].apply(lambda x: f"${x:,.0f}"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Cash Flow: $%{y:,.2f}<extra></extra>'
    ))

    # Add cumulative line
    fig.add_trace(go.Scatter(
        x=plot_df['Date'],
        y=plot_df['CumulativeCashFlow'],
        mode='lines+markers',
        name='Cumulative',
        line=dict(color='#4361ee', width=2),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Cumulative: $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Cash Flow ($)",
        yaxis2=dict(
            title="Cumulative ($)",
            overlaying='y',
            side='right'
        ),
        height=500,
        margin=dict(l=20, r=80, t=50, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def analyze_contribution_vs_growth(df, cash_flows_df):
    """
    Analyze how much of current value comes from contributions vs investment growth.

    Args:
        df (pd.DataFrame): DataFrame with Date and ValueUSD
        cash_flows_df (pd.DataFrame): DataFrame with Date and InferredCashFlow

    Returns:
        dict: Dictionary with total_contributions, total_growth, and current_value
    """
    if df.empty or cash_flows_df.empty:
        return {
            'total_contributions': 0.0,
            'total_growth': 0.0,
            'current_value': 0.0,
            'growth_percentage': 0.0
        }

    # Calculate total contributions
    total_contributions = cash_flows_df['InferredCashFlow'].sum()

    # Get current value
    current_value = df[df['Date'] == df['Date'].max()]['ValueUSD'].sum()

    # Calculate growth
    total_growth = current_value - total_contributions

    # Calculate growth percentage
    if total_contributions > 0:
        growth_percentage = (total_growth / total_contributions) * 100
    else:
        growth_percentage = 0.0

    return {
        'total_contributions': total_contributions,
        'total_growth': total_growth,
        'current_value': current_value,
        'growth_percentage': growth_percentage
    }


def create_contribution_growth_pie(analysis_result):
    """
    Create a pie chart showing contribution vs growth.

    Args:
        analysis_result (dict): Result from analyze_contribution_vs_growth

    Returns:
        plotly.graph_objects.Figure: Pie chart
    """
    if not analysis_result or analysis_result['current_value'] == 0:
        fig = go.Figure()
        fig.update_layout(
            title="Contribution vs Growth",
            annotations=[dict(
                text="No data available",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )]
        )
        return fig

    contributions = max(0, analysis_result['total_contributions'])
    growth = max(0, analysis_result['total_growth'])

    fig = go.Figure(data=[go.Pie(
        labels=['Contributions', 'Investment Growth'],
        values=[contributions, growth],
        marker=dict(colors=['#4361ee', '#4ade80']),
        textinfo='label+percent',
        textfont_size=14,
        hole=0.3,
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=f"Portfolio Composition: ${analysis_result['current_value']:,.0f} Total",
        height=400,
        margin=dict(l=20, r=20, t=80, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )

    return fig
