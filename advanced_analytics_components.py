# advanced_analytics_components.py
"""
Advanced analytics components for the investment tracker.
Includes risk metrics, correlation analysis, and cash flow tracking.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from risk_metrics import calculate_comprehensive_risk_metrics, get_risk_category
from correlation_analysis import (
    calculate_correlation_matrix,
    create_correlation_heatmap,
    identify_diversification_opportunities,
    calculate_portfolio_diversification_score
)
from cash_flow_tracker import (
    infer_cash_flows,
    create_cash_flow_waterfall,
    analyze_contribution_vs_growth,
    create_contribution_growth_pie
)


def create_risk_metrics_section(df, start_date, end_date):
    """
    Create comprehensive risk metrics section.

    Args:
        df (pd.DataFrame): Investment data
        start_date (datetime): Start date
        end_date (datetime): End date
    """
    st.subheader("📊 Risk & Volatility Analysis")

    # Filter data
    period_df = df[
        (df['Date'] >= pd.Timestamp(start_date)) &
        (df['Date'] <= pd.Timestamp(end_date))
    ].copy()

    if period_df.empty:
        st.warning("No data available for the selected period.")
        return

    # Calculate portfolio total values over time
    portfolio_values = period_df.groupby('Date')['ValueUSD'].sum().reset_index()
    portfolio_values.columns = ['Date', 'Value']

    # Calculate risk metrics
    risk_metrics = calculate_comprehensive_risk_metrics(portfolio_values)

    if not risk_metrics:
        st.warning("Not enough data to calculate risk metrics.")
        return

    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        st.metric(
            "Sharpe Ratio",
            f"{sharpe:.2f}",
            help="Risk-adjusted return. Higher is better. >1 is good, >2 is excellent."
        )
        st.caption(get_risk_category(sharpe))

    with col2:
        volatility = risk_metrics.get('volatility_annual', 0)
        st.metric(
            "Annual Volatility",
            f"{volatility:.1f}%",
            help="Annualized standard deviation of returns. Lower means more stable."
        )

    with col3:
        max_dd = risk_metrics.get('max_drawdown', 0)
        st.metric(
            "Max Drawdown",
            f"{max_dd:.1f}%",
            delta=f"{max_dd:.1f}%",
            delta_color="inverse",
            help="Largest peak-to-trough decline. Lower is better."
        )

    with col4:
        annual_return = risk_metrics.get('annualized_return', 0)
        st.metric(
            "Annualized Return",
            f"{annual_return:.1f}%",
            help="Compound annual growth rate over the period."
        )

    # Detailed metrics in expander
    with st.expander("📈 Detailed Risk Metrics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Return Metrics**")
            st.write(f"• Annualized Return: {risk_metrics.get('annualized_return', 0):.2f}%")
            st.write(f"• Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}")
            st.write(f"• Sortino Ratio: {risk_metrics.get('sortino_ratio', 0):.2f}")

            if 'beta' in risk_metrics:
                st.write(f"• Beta: {risk_metrics['beta']:.2f}")
            if 'alpha' in risk_metrics:
                st.write(f"• Alpha: {risk_metrics['alpha']:.2f}%")

        with col2:
            st.markdown("**Risk Metrics**")
            st.write(f"• Daily Volatility: {risk_metrics.get('volatility_daily', 0):.2f}%")
            st.write(f"• Annual Volatility: {risk_metrics.get('volatility_annual', 0):.2f}%")
            st.write(f"• Value at Risk (95%): {risk_metrics.get('var_95', 0):.2f}%")
            st.write(f"• CVaR (95%): {risk_metrics.get('cvar_95', 0):.2f}%")

        # Drawdown details
        if risk_metrics.get('max_drawdown') and risk_metrics.get('drawdown_start'):
            st.markdown("**Drawdown Analysis**")
            st.write(f"• Maximum Drawdown: {risk_metrics['max_drawdown']:.2f}%")
            st.write(f"• Drawdown Start: {risk_metrics['drawdown_start'].strftime('%Y-%m-%d')}")
            st.write(f"• Drawdown End: {risk_metrics['drawdown_end'].strftime('%Y-%m-%d')}")

            if risk_metrics.get('recovery_date'):
                st.write(f"• Recovery Date: {risk_metrics['recovery_date'].strftime('%Y-%m-%d')}")
                st.write(f"• Days to Recover: {risk_metrics['days_to_recover']} days")
            else:
                st.write("• Recovery: Not yet recovered")


def create_correlation_section(df, start_date, end_date):
    """
    Create correlation analysis section.

    Args:
        df (pd.DataFrame): Investment data
        start_date (datetime): Start date
        end_date (datetime): End date
    """
    st.subheader("🔗 Investment Correlation Analysis")

    # Calculate correlation matrix
    corr_matrix = calculate_correlation_matrix(df, start_date, end_date)

    if corr_matrix.empty:
        st.warning("Not enough data to calculate correlations.")
        return

    # Calculate diversification score
    div_score = calculate_portfolio_diversification_score(corr_matrix)

    st.metric(
        "Portfolio Diversification Score",
        f"{div_score:.0f}/100",
        help="Higher scores indicate better diversification. 70+ is good."
    )

    # Display correlation heatmap
    fig = create_correlation_heatmap(corr_matrix)
    st.plotly_chart(fig, use_container_width=True)

    # Identify highly correlated pairs
    high_corr = identify_diversification_opportunities(corr_matrix, threshold=0.7)

    if high_corr:
        with st.expander("⚠️ Highly Correlated Investments (Potential Risk)"):
            st.write("These investments tend to move together, reducing diversification benefits:")
            for pair in high_corr[:5]:  # Show top 5
                st.write(
                    f"• **{pair['investment_1']}** ↔ **{pair['investment_2']}**: "
                    f"{pair['correlation']:.2f} ({pair['relationship']})"
                )

    # Show well-diversified pairs
    from correlation_analysis import get_uncorrelated_pairs
    low_corr = get_uncorrelated_pairs(corr_matrix, threshold=0.3)

    if low_corr:
        with st.expander("✅ Well-Diversified Pairs"):
            st.write("These investments provide good diversification:")
            for pair in low_corr[:5]:  # Show top 5
                st.write(
                    f"• **{pair['investment_1']}** ↔ **{pair['investment_2']}**: "
                    f"{pair['correlation']:.2f} ({pair['diversification_benefit']})"
                )


def create_cash_flow_section(df, start_date, end_date):
    """
    Create cash flow analysis section.

    Args:
        df (pd.DataFrame): Investment data
        start_date (datetime): Start date
        end_date (datetime): End date
    """
    st.subheader("💰 Cash Flow & Contribution Analysis")

    # Filter data
    period_df = df[
        (df['Date'] >= pd.Timestamp(start_date)) &
        (df['Date'] <= pd.Timestamp(end_date))
    ].copy()

    if period_df.empty:
        st.warning("No data available for the selected period.")
        return

    # Infer cash flows
    cash_flows = infer_cash_flows(period_df)

    if cash_flows.empty:
        st.warning("Unable to calculate cash flows.")
        return

    # Analyze contribution vs growth
    portfolio_totals = period_df.groupby('Date')['ValueUSD'].sum().reset_index()
    portfolio_totals.columns = ['Date', 'ValueUSD']

    analysis = analyze_contribution_vs_growth(portfolio_totals, cash_flows)

    # Display summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Contributions",
            f"${analysis['total_contributions']:,.0f}",
            help="Total amount invested"
        )

    with col2:
        st.metric(
            "Investment Growth",
            f"${analysis['total_growth']:,.0f}",
            delta=f"{analysis['growth_percentage']:.1f}%",
            help="Profit from investments"
        )

    with col3:
        st.metric(
            "Current Value",
            f"${analysis['current_value']:,.0f}",
            help="Total portfolio value"
        )

    # Show contribution vs growth chart
    col1, col2 = st.columns([1, 1])

    with col1:
        fig_pie = create_contribution_growth_pie(analysis)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Show cash flow waterfall
        fig_waterfall = create_cash_flow_waterfall(cash_flows)
        st.plotly_chart(fig_waterfall, use_container_width=True)

    # Investment-specific analysis
    with st.expander("💼 Cash Flows by Investment"):
        investments = sorted(df['Investment'].unique())
        selected_inv = st.selectbox(
            "Select Investment",
            investments,
            key="cash_flow_investment"
        )

        if selected_inv:
            fig_inv = create_cash_flow_waterfall(cash_flows, investment=selected_inv)
            st.plotly_chart(fig_inv, use_container_width=True)


def create_advanced_analytics_tab(df, start_date, end_date):
    """
    Create the complete advanced analytics tab.

    Args:
        df (pd.DataFrame): Investment data with Date, Investment, and ValueUSD columns
        start_date (datetime): Start date for analysis
        end_date (datetime): End date for analysis
    """
    st.title("📊 Advanced Analytics")

    if df.empty:
        st.warning("No data available for analysis.")
        return

    # Add date range info
    st.info(f"📅 Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Risk Metrics Section
    create_risk_metrics_section(df, start_date, end_date)

    st.divider()

    # Correlation Section
    create_correlation_section(df, start_date, end_date)

    st.divider()

    # Cash Flow Section
    create_cash_flow_section(df, start_date, end_date)
