# risk_metrics.py
"""
Risk and volatility analysis for investment portfolios.
Provides metrics like Sharpe ratio, Sortino ratio, max drawdown, and volatility.
"""

import pandas as pd
import numpy as np
from datetime import datetime


def calculate_returns(df, period='daily'):
    """
    Calculate returns for a DataFrame with Date and Value columns.

    Args:
        df (pd.DataFrame): DataFrame with Date and Value columns
        period (str): 'daily', 'weekly', 'monthly', or 'yearly'

    Returns:
        pd.Series: Returns for the specified period
    """
    if df.empty or 'Value' not in df.columns:
        return pd.Series()

    df = df.sort_values('Date').copy()

    if period == 'daily':
        returns = df['Value'].pct_change()
    elif period == 'weekly':
        df_resampled = df.set_index('Date').resample('W')['Value'].last()
        returns = df_resampled.pct_change()
    elif period == 'monthly':
        df_resampled = df.set_index('Date').resample('M')['Value'].last()
        returns = df_resampled.pct_change()
    elif period == 'yearly':
        df_resampled = df.set_index('Date').resample('Y')['Value'].last()
        returns = df_resampled.pct_change()
    else:
        returns = df['Value'].pct_change()

    return returns.dropna()


def calculate_volatility(returns, annualize=True, periods_per_year=252):
    """
    Calculate volatility (standard deviation of returns).

    Args:
        returns (pd.Series): Series of returns
        annualize (bool): Whether to annualize the volatility
        periods_per_year (int): Number of periods per year (252 for daily, 52 for weekly, etc.)

    Returns:
        float: Volatility as a percentage
    """
    if returns.empty or len(returns) < 2:
        return 0.0

    volatility = returns.std()

    if annualize:
        volatility *= np.sqrt(periods_per_year)

    return volatility * 100  # Convert to percentage


def calculate_sharpe_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
    """
    Calculate Sharpe ratio (risk-adjusted return).

    Args:
        returns (pd.Series): Series of returns
        risk_free_rate (float): Annual risk-free rate (default 2%)
        periods_per_year (int): Number of periods per year

    Returns:
        float: Sharpe ratio
    """
    if returns.empty or len(returns) < 2:
        return 0.0

    # Annualized return
    excess_returns = returns - (risk_free_rate / periods_per_year)

    if excess_returns.std() == 0:
        return 0.0

    sharpe = np.sqrt(periods_per_year) * (excess_returns.mean() / excess_returns.std())

    return sharpe


def calculate_sortino_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
    """
    Calculate Sortino ratio (like Sharpe but only penalizes downside volatility).

    Args:
        returns (pd.Series): Series of returns
        risk_free_rate (float): Annual risk-free rate (default 2%)
        periods_per_year (int): Number of periods per year

    Returns:
        float: Sortino ratio
    """
    if returns.empty or len(returns) < 2:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)

    # Only consider negative returns for downside deviation
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    downside_std = downside_returns.std()
    sortino = np.sqrt(periods_per_year) * (excess_returns.mean() / downside_std)

    return sortino


def calculate_max_drawdown(df):
    """
    Calculate maximum drawdown (largest peak-to-trough decline).

    Args:
        df (pd.DataFrame): DataFrame with Date and Value columns

    Returns:
        dict: Dictionary with max_drawdown (%), drawdown_start, drawdown_end, recovery_date
    """
    if df.empty or 'Value' not in df.columns or len(df) < 2:
        return {
            'max_drawdown': 0.0,
            'drawdown_start': None,
            'drawdown_end': None,
            'recovery_date': None,
            'days_to_recover': None
        }

    df = df.sort_values('Date').copy()

    # Calculate running maximum
    df['Running_Max'] = df['Value'].cummax()

    # Calculate drawdown
    df['Drawdown'] = (df['Value'] - df['Running_Max']) / df['Running_Max'] * 100

    # Find maximum drawdown
    max_dd_idx = df['Drawdown'].idxmin()
    max_drawdown = df.loc[max_dd_idx, 'Drawdown']
    drawdown_end = df.loc[max_dd_idx, 'Date']

    # Find the peak before the drawdown
    peak_df = df[df['Date'] <= drawdown_end]
    peak_idx = peak_df[peak_df['Value'] == peak_df['Running_Max'].iloc[-1]].index[0]
    drawdown_start = df.loc[peak_idx, 'Date']

    # Find recovery date (when value exceeds the peak again)
    recovery_df = df[(df['Date'] > drawdown_end) & (df['Value'] >= df.loc[peak_idx, 'Value'])]

    if not recovery_df.empty:
        recovery_date = recovery_df.iloc[0]['Date']
        days_to_recover = (recovery_date - drawdown_end).days
    else:
        recovery_date = None
        days_to_recover = None

    return {
        'max_drawdown': max_drawdown,
        'drawdown_start': drawdown_start,
        'drawdown_end': drawdown_end,
        'recovery_date': recovery_date,
        'days_to_recover': days_to_recover
    }


def calculate_var(returns, confidence_level=0.95):
    """
    Calculate Value at Risk (VaR) - maximum expected loss at a given confidence level.

    Args:
        returns (pd.Series): Series of returns
        confidence_level (float): Confidence level (default 95%)

    Returns:
        float: VaR as a percentage (negative value indicates loss)
    """
    if returns.empty or len(returns) < 2:
        return 0.0

    var = np.percentile(returns, (1 - confidence_level) * 100)

    return var * 100  # Convert to percentage


def calculate_cvar(returns, confidence_level=0.95):
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
    Average loss in worst cases beyond VaR.

    Args:
        returns (pd.Series): Series of returns
        confidence_level (float): Confidence level (default 95%)

    Returns:
        float: CVaR as a percentage (negative value indicates loss)
    """
    if returns.empty or len(returns) < 2:
        return 0.0

    var = np.percentile(returns, (1 - confidence_level) * 100)
    cvar = returns[returns <= var].mean()

    return cvar * 100  # Convert to percentage


def calculate_beta(asset_returns, benchmark_returns):
    """
    Calculate beta (sensitivity to benchmark movements).

    Args:
        asset_returns (pd.Series): Returns of the asset
        benchmark_returns (pd.Series): Returns of the benchmark

    Returns:
        float: Beta value
    """
    if asset_returns.empty or benchmark_returns.empty or len(asset_returns) < 2:
        return 0.0

    # Align the series
    combined = pd.DataFrame({
        'asset': asset_returns,
        'benchmark': benchmark_returns
    }).dropna()

    if len(combined) < 2:
        return 0.0

    covariance = combined['asset'].cov(combined['benchmark'])
    benchmark_variance = combined['benchmark'].var()

    if benchmark_variance == 0:
        return 0.0

    beta = covariance / benchmark_variance

    return beta


def calculate_alpha(asset_returns, benchmark_returns, risk_free_rate=0.02, periods_per_year=252):
    """
    Calculate alpha (excess return over what CAPM predicts).

    Args:
        asset_returns (pd.Series): Returns of the asset
        benchmark_returns (pd.Series): Returns of the benchmark
        risk_free_rate (float): Annual risk-free rate
        periods_per_year (int): Number of periods per year

    Returns:
        float: Annualized alpha as a percentage
    """
    if asset_returns.empty or benchmark_returns.empty or len(asset_returns) < 2:
        return 0.0

    # Calculate beta
    beta = calculate_beta(asset_returns, benchmark_returns)

    # Align the series
    combined = pd.DataFrame({
        'asset': asset_returns,
        'benchmark': benchmark_returns
    }).dropna()

    if len(combined) < 2:
        return 0.0

    # Calculate average returns
    asset_return = combined['asset'].mean() * periods_per_year
    benchmark_return = combined['benchmark'].mean() * periods_per_year

    # Alpha = Asset Return - (Risk Free Rate + Beta * (Benchmark Return - Risk Free Rate))
    alpha = asset_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))

    return alpha * 100  # Convert to percentage


def calculate_comprehensive_risk_metrics(df, benchmark_df=None, risk_free_rate=0.02):
    """
    Calculate a comprehensive set of risk metrics for a portfolio.

    Args:
        df (pd.DataFrame): DataFrame with Date and Value columns
        benchmark_df (pd.DataFrame, optional): Benchmark data for comparison
        risk_free_rate (float): Annual risk-free rate (default 2%)

    Returns:
        dict: Dictionary of risk metrics
    """
    if df.empty or 'Value' not in df.columns:
        return {}

    # Calculate returns
    returns = calculate_returns(df, period='daily')

    if returns.empty or len(returns) < 2:
        return {}

    metrics = {
        'volatility_daily': calculate_volatility(returns, annualize=False),
        'volatility_annual': calculate_volatility(returns, annualize=True, periods_per_year=252),
        'sharpe_ratio': calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year=252),
        'sortino_ratio': calculate_sortino_ratio(returns, risk_free_rate, periods_per_year=252),
        'var_95': calculate_var(returns, confidence_level=0.95),
        'cvar_95': calculate_cvar(returns, confidence_level=0.95),
    }

    # Add drawdown metrics
    drawdown_metrics = calculate_max_drawdown(df)
    metrics.update(drawdown_metrics)

    # Calculate annualized return
    if len(df) >= 2:
        days = (df['Date'].max() - df['Date'].min()).days
        if days > 0:
            total_return = (df['Value'].iloc[-1] / df['Value'].iloc[0]) - 1
            annualized_return = (1 + total_return) ** (365.25 / days) - 1
            metrics['annualized_return'] = annualized_return * 100
        else:
            metrics['annualized_return'] = 0.0

    # Add benchmark comparison if provided
    if benchmark_df is not None and not benchmark_df.empty:
        benchmark_returns = calculate_returns(benchmark_df, period='daily')
        if not benchmark_returns.empty and len(benchmark_returns) >= 2:
            metrics['beta'] = calculate_beta(returns, benchmark_returns)
            metrics['alpha'] = calculate_alpha(returns, benchmark_returns, risk_free_rate, periods_per_year=252)

    return metrics


def get_risk_category(sharpe_ratio):
    """
    Categorize investment based on Sharpe ratio.

    Args:
        sharpe_ratio (float): Sharpe ratio value

    Returns:
        str: Risk category description
    """
    if sharpe_ratio < 0:
        return "Poor (Negative Risk-Adjusted Return)"
    elif sharpe_ratio < 0.5:
        return "Below Average"
    elif sharpe_ratio < 1.0:
        return "Good"
    elif sharpe_ratio < 2.0:
        return "Very Good"
    else:
        return "Excellent"
