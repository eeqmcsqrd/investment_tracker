# correlation_analysis.py
"""
Correlation analysis for investment portfolios.
Shows how different investments move together and diversification benefits.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def calculate_correlation_matrix(df, start_date=None, end_date=None):
    """
    Calculate correlation matrix for all investments.

    Args:
        df (pd.DataFrame): DataFrame with Date, Investment, and ValueUSD columns
        start_date (datetime, optional): Start date for analysis
        end_date (datetime, optional): End date for analysis

    Returns:
        pd.DataFrame: Correlation matrix
    """
    if df.empty:
        return pd.DataFrame()

    # Filter by date range if provided (convert to pd.Timestamp for comparison)
    if start_date:
        df = df[df['Date'] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.Timestamp(end_date)]

    # Pivot to get investments as columns
    pivot_df = df.pivot_table(
        index='Date',
        columns='Investment',
        values='ValueUSD',
        aggfunc='sum'
    )

    # Forward fill missing values (for investments added later)
    pivot_df = pivot_df.ffill()

    # Calculate percentage returns
    returns_df = pivot_df.pct_change().dropna()

    if returns_df.empty or len(returns_df) < 2:
        return pd.DataFrame()

    # Calculate correlation matrix
    corr_matrix = returns_df.corr()

    return corr_matrix


def create_correlation_heatmap(corr_matrix, title="Investment Correlation Matrix"):
    """
    Create an interactive correlation heatmap.

    Args:
        corr_matrix (pd.DataFrame): Correlation matrix
        title (str): Chart title

    Returns:
        plotly.graph_objects.Figure: Heatmap figure
    """
    if corr_matrix.empty:
        # Return empty figure
        fig = go.Figure()
        fig.update_layout(
            title=title,
            annotations=[dict(
                text="Not enough data for correlation analysis",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )]
        )
        return fig

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(
            title="Correlation",
            titleside="right",
            tickmode="linear",
            tick0=-1,
            dtick=0.5
        )
    ))

    fig.update_layout(
        title=title,
        xaxis={'side': 'bottom'},
        yaxis={'side': 'left'},
        height=600,
        margin=dict(l=150, r=50, t=80, b=150),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    # Rotate x-axis labels
    fig.update_xaxes(tickangle=-45)

    return fig


def identify_diversification_opportunities(corr_matrix, threshold=0.7):
    """
    Identify pairs of highly correlated investments (poor diversification).

    Args:
        corr_matrix (pd.DataFrame): Correlation matrix
        threshold (float): Correlation threshold (default 0.7)

    Returns:
        list: List of dictionaries with correlated pairs
    """
    if corr_matrix.empty:
        return []

    opportunities = []

    # Iterate through upper triangle of matrix (avoid duplicates)
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]

            if abs(corr_value) >= threshold:
                opportunities.append({
                    'investment_1': corr_matrix.columns[i],
                    'investment_2': corr_matrix.columns[j],
                    'correlation': corr_value,
                    'relationship': 'Highly Positive' if corr_value > 0 else 'Highly Negative'
                })

    # Sort by absolute correlation
    opportunities.sort(key=lambda x: abs(x['correlation']), reverse=True)

    return opportunities


def calculate_portfolio_diversification_score(corr_matrix, weights=None):
    """
    Calculate a diversification score for the portfolio (0-100, higher is better).

    Args:
        corr_matrix (pd.DataFrame): Correlation matrix
        weights (dict, optional): Dictionary of investment weights

    Returns:
        float: Diversification score (0-100)
    """
    if corr_matrix.empty or len(corr_matrix) < 2:
        return 0.0

    # If no weights provided, use equal weights
    if weights is None:
        n = len(corr_matrix)
        weights = {inv: 1/n for inv in corr_matrix.columns}

    # Calculate weighted average correlation
    total_weight = 0
    weighted_corr = 0

    for i, inv1 in enumerate(corr_matrix.columns):
        for j, inv2 in enumerate(corr_matrix.columns):
            if i != j:  # Exclude self-correlation
                w1 = weights.get(inv1, 0)
                w2 = weights.get(inv2, 0)
                weighted_corr += w1 * w2 * corr_matrix.iloc[i, j]
                total_weight += w1 * w2

    if total_weight == 0:
        return 0.0

    avg_corr = weighted_corr / total_weight

    # Convert to score (1 = no diversification, -1 = perfect negative correlation)
    # Map [-1, 1] to [100, 0]
    diversification_score = (1 - avg_corr) * 50

    return max(0, min(100, diversification_score))


def get_uncorrelated_pairs(corr_matrix, threshold=0.3):
    """
    Find pairs of investments with low correlation (good diversification).

    Args:
        corr_matrix (pd.DataFrame): Correlation matrix
        threshold (float): Correlation threshold (default 0.3)

    Returns:
        list: List of dictionaries with uncorrelated pairs
    """
    if corr_matrix.empty:
        return []

    uncorrelated = []

    # Iterate through upper triangle of matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]

            if abs(corr_value) <= threshold:
                uncorrelated.append({
                    'investment_1': corr_matrix.columns[i],
                    'investment_2': corr_matrix.columns[j],
                    'correlation': corr_value,
                    'diversification_benefit': 'Excellent' if abs(corr_value) < 0.1 else 'Good'
                })

    # Sort by absolute correlation (lowest first)
    uncorrelated.sort(key=lambda x: abs(x['correlation']))

    return uncorrelated


def calculate_rolling_correlation(df, investment1, investment2, window=30):
    """
    Calculate rolling correlation between two investments over time.

    Args:
        df (pd.DataFrame): DataFrame with Date, Investment, and ValueUSD columns
        investment1 (str): First investment name
        investment2 (str): Second investment name
        window (int): Rolling window size in days

    Returns:
        pd.DataFrame: DataFrame with Date and rolling correlation
    """
    if df.empty:
        return pd.DataFrame()

    # Filter for the two investments
    df1 = df[df['Investment'] == investment1].set_index('Date')['ValueUSD']
    df2 = df[df['Investment'] == investment2].set_index('Date')['ValueUSD']

    # Align dates and calculate returns
    combined = pd.DataFrame({
        'inv1': df1,
        'inv2': df2
    }).ffill()

    if len(combined) < window:
        return pd.DataFrame()

    combined['ret1'] = combined['inv1'].pct_change()
    combined['ret2'] = combined['inv2'].pct_change()

    # Calculate rolling correlation
    rolling_corr = combined['ret1'].rolling(window=window).corr(combined['ret2'])

    result = pd.DataFrame({
        'Date': rolling_corr.index,
        'Correlation': rolling_corr.values
    })

    return result.dropna()


def create_rolling_correlation_chart(rolling_corr_df, investment1, investment2):
    """
    Create a line chart showing rolling correlation over time.

    Args:
        rolling_corr_df (pd.DataFrame): DataFrame with Date and Correlation
        investment1 (str): First investment name
        investment2 (str): Second investment name

    Returns:
        plotly.graph_objects.Figure: Line chart
    """
    if rolling_corr_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Rolling Correlation: {investment1} vs {investment2}",
            annotations=[dict(
                text="Not enough data for rolling correlation",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )]
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=rolling_corr_df['Date'],
        y=rolling_corr_df['Correlation'],
        mode='lines',
        name='Correlation',
        line=dict(color='#4361ee', width=2),
        fill='tozeroy',
        fillcolor='rgba(67, 97, 238, 0.2)'
    ))

    # Add reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=0.7, line_dash="dot", line_color="red", opacity=0.3,
                  annotation_text="High Correlation", annotation_position="right")
    fig.add_hline(y=-0.7, line_dash="dot", line_color="green", opacity=0.3,
                  annotation_text="High Negative Correlation", annotation_position="right")

    fig.update_layout(
        title=f"Rolling Correlation (30-day): {investment1} vs {investment2}",
        xaxis_title="Date",
        yaxis_title="Correlation",
        height=400,
        margin=dict(l=20, r=20, t=50, b=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(range=[-1, 1]),
        hovermode="x unified"
    )

    return fig
