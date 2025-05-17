# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from data_handler import (
    load_data, 
    save_data, 
    add_entry, 
    add_bulk_entries,
    get_historical_performance,
    get_relative_performance,
    get_previous_values
)
from currency_service import get_conversion_rate, refresh_rates
from config import INVESTMENT_ACCOUNTS, INVESTMENT_CATEGORIES

# Page configuration
st.set_page_config(
    page_title="Advanced Investment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    /* Improved tab styling for better visibility */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #1e1e2e;
        padding: 0;
        border-radius: 8px;
        display: flex;
        overflow: hidden;
        border: 1px solid #3d3d54;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2c2c40;
        border-radius: 0;
        gap: 0;
        padding: 10px 20px;
        font-weight: 600;
        color: white;
        min-width: 140px;
        text-align: center;
        border-right: 1px solid #3d3d54;
        transition: background-color 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3d3d60;
    }
    .stTabs [data-baseweb="tab"]:last-child {
        border-right: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
        font-weight: 700;
    }
    /* Adding a subtle border to improve visibility */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
    /* Make icons more visible */
    .stTabs [data-baseweb="tab"] svg {
        fill: white;
        height: 22px;
        width: 22px;
        margin-right: 8px;
    }
    
    /* Improved styling for charts */
    .js-plotly-plot, .plotly, .plot-container {
        height: 100%;
    }
    [data-testid="stMetric"] {
        background-color: #1e1e2e;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    [data-testid="stMetric"] label {
        color: #e0e0e0 !important;
    }
    [data-testid="stMetric"] > div {
        justify-content: center;
    }
    [data-testid="column"] > div {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Advanced Investment Tracker")
st.markdown("""
Track your investments across multiple currencies, analyze performance, and visualize your portfolio.
""")

# Initialize session state for holding our application state
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Load data
df = load_data()
if df is not None and not df.empty:
    # Ensure Date column is datetime - using a more flexible approach
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)
    
    # Ensure Investment column contains only strings
    df['Investment'] = df['Investment'].astype(str)
    
    # Add helper columns
    df['ValueUSD'] = df.apply(
        lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
        axis=1
    )
    
    # Get latest date
    latest_date = df['Date'].max()
    earliest_date = df['Date'].min()
    
    # Get latest snapshot
    latest_df = df[df['Date'] == latest_date]
else:
    latest_date = datetime.now().date()
    earliest_date = latest_date
    latest_df = pd.DataFrame()

# Create string-only version of INVESTMENT_ACCOUNTS for use throughout the app
investment_accounts = {str(k): v for k, v in INVESTMENT_ACCOUNTS.items()}

# Function to reset success message
def reset_success():
    st.session_state.show_success = False

# Sidebar: Data Entry Section
with st.sidebar:
    st.header("Add Investment Data")
    
    # Add tab selection for different entry methods
    entry_tab = st.radio(
        "Entry Method",
        ["Single Entry", "Bulk Update", "Update All"]
    )
    
    if entry_tab == "Single Entry":
        # Single entry form
        st.subheader("Add Single Entry")
        investment_name = st.selectbox(
            "Investment Account", 
            sorted(list(investment_accounts.keys())),
            key="single_investment"
        )
        investment_value = st.number_input(
            f"Value ({investment_accounts[investment_name]})", 
            min_value=0.0, 
            format="%.2f",
            key="single_value"
        )
        entry_date = st.date_input(
            "Entry Date", 
            value=datetime.now(),
            key="single_date"
        )
        
        if st.button("Add Entry", key="add_single"):
            df = add_entry(df, entry_date, investment_name, investment_value)
            save_data(df)
            st.session_state.show_success = True
            st.rerun()
    
    elif entry_tab == "Bulk Update":
        # Bulk update form
        st.subheader("Update Multiple Investments")
        
        # Extract unique investment categories
        categories = sorted(list(set(
            [cat for inv, cat in INVESTMENT_CATEGORIES.items()]
        )))
        
        selected_category = st.selectbox(
            "Filter by Category", 
            ["All"] + categories,
            key="bulk_category"
        )
        
        # Filter investments by category
        if selected_category == "All":
            selectable_investments = sorted(list(investment_accounts.keys()))
        else:
            selectable_investments = sorted([
                str(inv) for inv, cat in INVESTMENT_CATEGORIES.items() 
                if cat == selected_category
            ])
        
        selected_investments = st.multiselect(
            "Select Investments",
            selectable_investments,
            key="bulk_investments"
        )
        
        bulk_date = st.date_input(
            "Entry Date",
            value=datetime.now(),
            key="bulk_date"
        )
        
        # Dynamic form generation based on selected investments
        investment_values = {}
        
        if selected_investments:
            st.markdown("### Enter Values")
            cols = st.columns(2)
            
            for i, inv in enumerate(selected_investments):
                col_idx = i % 2
                with cols[col_idx]:
                    currency = INVESTMENT_ACCOUNTS[inv]
                    investment_values[inv] = st.number_input(
                        f"{inv} ({currency})",
                        min_value=0.0,
                        format="%.2f",
                        key=f"value_{inv}"
                    )
            
            if st.button("Submit All Values", key="add_bulk"):
                df = add_bulk_entries(df, bulk_date, investment_values)
                save_data(df)
                st.session_state.show_success = True
                st.rerun()
    
    elif entry_tab == "Update All":
        # Update all form with previous values
        st.subheader("Update All Investments")
        
        update_all_date = st.date_input(
            "Entry Date",
            value=datetime.now(),
            key="update_all_date"
        )
        
        # Get the most recent values for all investments
        if not df.empty:
            # Sort by date descending
            temp_df = df.sort_values('Date', ascending=False)
            
            # Get most recent entry for each investment
            recent_values = {}
            for inv in INVESTMENT_ACCOUNTS.keys():
                inv_data = temp_df[temp_df['Investment'] == inv]
                if not inv_data.empty:
                    recent_values[inv] = inv_data.iloc[0]['Value']
                else:
                    recent_values[inv] = 0.0
            
            # Display form with previous values
            st.markdown("### Enter New Values")
            categories = sorted(list(set(
                [cat for inv, cat in INVESTMENT_CATEGORIES.items()]
            )))
            
            investment_values = {}
            
            for category in categories:
                st.markdown(f"#### {category}")
                
                # Get investments for this category
                category_investments = sorted([
                    str(inv) for inv, cat in INVESTMENT_CATEGORIES.items() 
                    if cat == category
                ])
                
                # Create two-column layout
                cols = st.columns(2)
                
                for i, inv in enumerate(category_investments):
                    col_idx = i % 2
                    with cols[col_idx]:
                        currency = investment_accounts.get(inv, 'USD')
                        prev_value = recent_values.get(inv, 0.0)
                        investment_values[inv] = st.number_input(
                            f"{inv} ({currency})",
                            min_value=0.0,
                            value=prev_value,
                            format="%.2f",
                            key=f"all_value_{inv}"
                        )
            
            if st.button("Submit All Investments", key="update_all"):
                df = add_bulk_entries(df, update_all_date, investment_values)
                save_data(df)
                st.session_state.show_success = True
                st.rerun()
    
    # Currency refresh button 
    st.markdown("---")
    if st.button("Refresh Exchange Rates"):
        refresh_rates()
        st.success("Exchange rates refreshed!")
        st.session_state.last_refresh = datetime.now()
    
    st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M')}")

# Display success message if needed
if st.session_state.show_success:
    st.success("Data saved successfully!")
    st.session_state.show_success = False

# Main content - Tabbed interface
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard", 
    "📈 Performance", 
    "📋 Data", 
    "⚙️ Settings"
])

with tab1:
    # Dashboard tab
    st.header("Portfolio Dashboard")
    
    if not latest_df.empty:
        # Top metrics row
        total_usd = latest_df['ValueUSD'].sum()
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric(
                "Total Portfolio Value", 
                f"${total_usd:,.2f} USD"
            )
        
        # Calculate 1 month change
        try:
            one_month_ago = latest_date - timedelta(days=30)
            closest_date = df[df['Date'] <= one_month_ago]['Date'].max()
            
            if pd.notna(closest_date):
                month_df = df[df['Date'] == closest_date]
                month_total = month_df['ValueUSD'].sum()
                month_change = total_usd - month_total
                month_percent = (month_change / month_total) * 100 if month_total > 0 else 0
                
                with metrics_col2:
                    st.metric(
                        "1 Month Change", 
                        f"${month_change:,.2f}", 
                        f"{month_percent:.2f}%",
                        delta_color="normal" if month_change >= 0 else "inverse"
                    )
        except Exception as e:
            with metrics_col2:
                st.metric("1 Month Change", "N/A")
        
        # Calculate 3 month change
        try:
            three_months_ago = latest_date - timedelta(days=90)
            closest_date = df[df['Date'] <= three_months_ago]['Date'].max()
            
            if pd.notna(closest_date):
                quarter_df = df[df['Date'] == closest_date]
                quarter_total = quarter_df['ValueUSD'].sum()
                quarter_change = total_usd - quarter_total
                quarter_percent = (quarter_change / quarter_total) * 100 if quarter_total > 0 else 0
                
                with metrics_col3:
                    st.metric(
                        "3 Month Change", 
                        f"${quarter_change:,.2f}", 
                        f"{quarter_percent:.2f}%",
                        delta_color="normal" if quarter_change >= 0 else "inverse"
                    )
        except Exception as e:
            with metrics_col3:
                st.metric("3 Month Change", "N/A")
        
        # Calculate YTD change
        try:
            start_of_year = datetime(latest_date.year, 1, 1).date()
            closest_date = df[df['Date'] >= start_of_year]['Date'].min()
            
            if pd.notna(closest_date):
                ytd_df = df[df['Date'] == closest_date]
                ytd_total = ytd_df['ValueUSD'].sum()
                ytd_change = total_usd - ytd_total
                ytd_percent = (ytd_change / ytd_total) * 100 if ytd_total > 0 else 0
                
                with metrics_col4:
                    st.metric(
                        "YTD Change", 
                        f"${ytd_change:,.2f}", 
                        f"{ytd_percent:.2f}%",
                        delta_color="normal" if ytd_change >= 0 else "inverse"
                    )
        except Exception as e:
            with metrics_col4:
                st.metric("YTD Change", "N/A")
                # Investment Value Changes Section
        st.markdown("---")
        st.subheader("Investment Value Changes")
        
        try:
            # Get the latest date data
            latest_date = df['Date'].max()
            latest_values = df[df['Date'] == latest_date].copy()
            
            # Get all dates except the latest one
            previous_dates = df[df['Date'] < latest_date]['Date'].unique()
            
            if len(previous_dates) > 0:
                # Find changes for each investment
                changes_data = []
                
                for _, row in latest_values.iterrows():
                    inv = row['Investment']
                    current_value = row['Value']
                    currency = row['Currency']
                    current_value_usd = row['ValueUSD']
                    
                    # Find the most recent previous entry for this investment
                    prev_entries = df[(df['Date'] < latest_date) & (df['Investment'] == inv)].sort_values('Date', ascending=False)
                    
                    if not prev_entries.empty:
                        # Get the most recent previous entry
                        prev_row = prev_entries.iloc[0]
                        prev_date = prev_row['Date']
                        prev_value = prev_row['Value']
                        prev_value_usd = prev_row['ValueUSD']
                        
                        # Calculate days between dates
                        days_between = (latest_date - prev_date).days
                        
                        # Calculate changes
                        change = current_value - prev_value
                        change_pct = ((current_value / prev_value) - 1) * 100 if prev_value > 0 else 0
                        
                        change_usd = current_value_usd - prev_value_usd
                        change_usd_pct = ((current_value_usd / prev_value_usd) - 1) * 100 if prev_value_usd > 0 else 0
                        
                        # Add to results with formatted strings
                        changes_data.append({
                            "Investment": inv,
                            "Current Value": f"{current_value:,.2f} {currency}",
                            "Current Value (USD)": f"${current_value_usd:,.2f}",
                            "Change": f"{change:+,.2f} {currency} ({change_pct:+.2f}%)",
                            "Change (USD)": f"${change_usd:+,.2f} ({change_usd_pct:+.2f}%)",
                            "Previous Update": f"{days_between} days ago",
                            "_sort_value": abs(change_usd)  # For sorting
                        })
                    else:
                        # No previous data for this investment
                        changes_data.append({
                            "Investment": inv,
                            "Current Value": f"{current_value:,.2f} {currency}",
                            "Current Value (USD)": f"${current_value_usd:,.2f}",
                            "Change": "N/A",
                            "Change (USD)": "N/A",
                            "Previous Update": "No prior data",
                            "_sort_value": 0  # For sorting
                        })
                
                # Create DataFrame and sort by magnitude of change
                if changes_data:
                    changes_df = pd.DataFrame(changes_data)
                    changes_df = changes_df.sort_values("_sort_value", ascending=False).drop(columns=["_sort_value"])
                    
                    # Display the table
                    st.dataframe(
                        changes_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No investment changes to display.")
            else:
                st.info("No historical data available for comparison.")
        except Exception as e:
            st.error(f"Error calculating investment changes: {str(e)}")
            
        st.markdown("---")
        
        # Charts row
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Asset Allocation")
            
            # Group by investment and calculate percentages
            allocation = latest_df.groupby('Investment')['ValueUSD'].sum().reset_index()
            allocation['Percentage'] = (allocation['ValueUSD'] / allocation['ValueUSD'].sum() * 100).round(2)
            
            # Add category information
            allocation['Category'] = allocation['Investment'].map(INVESTMENT_CATEGORIES)
            
            # Create improved pie chart
            fig = px.pie(
                allocation, 
                values='ValueUSD', 
                names='Investment',
                hover_data=['Percentage'],
                labels={'ValueUSD': 'Value (USD)'},
                title='',
                color='Category',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12,
                pull=[0.02] * len(allocation),  # Slight pull for all slices
                marker=dict(line=dict(color='#1e1e2e', width=1))
            )
            fig.update_layout(
                height=450,  # Increased height
                margin=dict(l=20, r=20, t=30, b=100),  # Increased bottom margin for legend
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.30,  # Moved much further down
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0.1)",
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with chart_col2:
            st.subheader("Currency Breakdown")
            
            # Group by currency
            currency_breakdown = latest_df.groupby('Currency')['ValueUSD'].sum().reset_index()
            currency_breakdown['Percentage'] = (currency_breakdown['ValueUSD'] / currency_breakdown['ValueUSD'].sum() * 100).round(2)
            
            # Create bar chart with improved styling
            fig = px.bar(
                currency_breakdown.sort_values('ValueUSD', ascending=False),
                x='Currency',
                y='ValueUSD',
                text='Percentage',
                color='Currency',
                labels={'ValueUSD': 'Value (USD)'},
                title=''
            )
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='outside',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1
            )
            fig.update_layout(
                height=450,  # Match pie chart height
                xaxis_title="Currency",
                yaxis_title="Value (USD)",
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.2)'
                ),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.2)'
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Bottom charts row
        st.subheader("Category Breakdown")
        
        # Group by category
        category_data = latest_df.copy()
        category_data['Category'] = category_data['Investment'].map(INVESTMENT_CATEGORIES)
        category_breakdown = category_data.groupby('Category')['ValueUSD'].sum().reset_index()
        category_breakdown['Percentage'] = (category_breakdown['ValueUSD'] / category_breakdown['ValueUSD'].sum() * 100).round(2)
        
        # Create horizontal bar chart with improved styling
        fig = px.bar(
            category_breakdown.sort_values('ValueUSD', ascending=True),
            y='Category',
            x='ValueUSD',
            text='Percentage',
            color='Category',
            orientation='h',
            labels={'ValueUSD': 'Value (USD)'},
            title=''
        )
        fig.update_traces(
            texttemplate='%{text:.1f}%', 
            textposition='inside',
            marker_line_color='rgba(255,255,255,0.2)',
            marker_line_width=1
        )
        fig.update_layout(
            height=350,
            yaxis_title="",
            xaxis_title="Value (USD)",
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                zerolinecolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                zerolinecolor='rgba(255,255,255,0.2)'
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No data available. Please add investment entries.")

with tab2:
    # Performance tab
    st.header("Investment Performance")
    
    if not df.empty:
        # Ensure Investment column contains only strings
        df['Investment'] = df['Investment'].astype(str)
        
        # Date range filters
        performance_cols = st.columns([1, 1, 2])
        with performance_cols[0]:
            perf_start = st.date_input(
                "From Date",
                value=earliest_date,
                min_value=earliest_date,
                max_value=latest_date,
                key="perf_start"
            )
        with performance_cols[1]:
            perf_end = st.date_input(
                "To Date",
                value=latest_date,
                min_value=earliest_date,
                max_value=latest_date,
                key="perf_end"
            )
        
        # Convert to datetime for filtering
        perf_start_dt = pd.Timestamp(perf_start)
        perf_end_dt = pd.Timestamp(perf_end)
        
        # Get performance data
        performance_data = get_historical_performance(df, perf_start_dt, perf_end_dt)
        
        if not performance_data.empty:
            # Total value over time
            st.subheader("Portfolio Value Over Time")
            
            # Group by date and sum values
            total_over_time = performance_data.groupby('Date')['ValueUSD'].sum().reset_index()
            
            # Create line chart
            fig = px.line(
                total_over_time,
                x='Date',
                y='ValueUSD',
                labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                title=''
            )
            fig.update_traces(line=dict(width=3))
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Value (USD)",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Investment performance comparison
            st.subheader("Investment Performance Comparison")
            
            # Get unique investments and ensure they are strings
            investments = [str(inv) for inv in performance_data['Investment'].unique()]
            
            # Set default reference investment to Binance if available
            default_reference = "Binance" if "Binance" in investments else investments[0] if investments else None
            
            # Add reference investment selection
            reference_investment = st.selectbox(
                "Reference Investment (Baseline)",
                sorted(investments),
                index=sorted(investments).index(default_reference) if default_reference in sorted(investments) else 0,
                key="reference_investment"
            )
            
            # Set default comparison investments to 401k, Trade Republic, and RBC if available
            default_comparisons = []
            for inv in ["401k", "Trade Republic", "RBC"]:
                if inv in investments and inv != reference_investment:
                    default_comparisons.append(inv)
            
            # Let user select investments to compare
            comparison_investments = st.multiselect(
                "Select Investments to Compare",
                sorted(investments),
                default=default_comparisons,
                key="performance_investments"
            )
            
            if reference_investment and comparison_investments:
                # Include reference investment if not already in comparison list
                all_investments = comparison_investments.copy()
                if reference_investment not in all_investments:
                    all_investments.append(reference_investment)
                
                # Get relative performance data
                from data_handler import get_relative_performance
                relative_data = get_relative_performance(
                    df, 
                    perf_start_dt, 
                    perf_end_dt, 
                    reference_investment, 
                    all_investments
                )
                
                if not relative_data.empty:
                    # Create a selection for what to display
                    chart_mode = st.radio(
                        "Display mode",
                        ["Relative to Baseline", "Absolute % Change"],
                        horizontal=True,
                        key="performance_mode"
                    )
                    
                    # Create line chart for comparison based on mode
                    if chart_mode == "Relative to Baseline":
                        y_column = "RelativePct"
                        title = f"Performance Relative to {reference_investment}"
                        y_title = f"% Difference vs {reference_investment}"
                    else:
                        y_column = "PctChange"
                        title = "Absolute Performance (% Change)"
                        y_title = "% Change from Start"
                    
                    # Create the chart
                    fig = px.line(
                        relative_data,
                        x='Date',
                        y=y_column,
                        color='Investment',
                        labels={y_column: y_title, 'Date': 'Date'},
                        title=title
                    )
                    
                    # Add zero line for reference
                    fig.add_hline(
                        y=0, 
                        line_dash="dash", 
                        line_color="white",
                        opacity=0.5,
                        annotation_text="Baseline" if chart_mode == "Relative to Baseline" else "No Change",
                        annotation_position="bottom right"
                    )
                    
                    # Update styling
                    fig.update_traces(line=dict(width=2.5))
                    fig.update_layout(
                        height=500,
                        xaxis_title="Date",
                        yaxis_title=y_title,
                        margin=dict(l=20, r=20, t=50, b=50),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(
                            gridcolor='rgba(255,255,255,0.1)',
                            zerolinecolor='rgba(255,255,255,0.2)'
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255,255,255,0.1)',
                            zerolinecolor='rgba(255,255,255,0.2)'
                        ),
                        hovermode="x unified",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    
                    # Calculate performance metrics
                    st.subheader("Performance Metrics")
                    
                    # Prepare metrics data
                    metrics_data = []
                    for inv in all_investments:
                        inv_data = relative_data[relative_data['Investment'] == inv]
                        if not inv_data.empty:
                            start_date = inv_data['Date'].min()
                            end_date = inv_data['Date'].max()
                            
                            start_row = inv_data[inv_data['Date'] == start_date].iloc[0]
                            end_row = inv_data[inv_data['Date'] == end_date].iloc[0]
                            
                            metrics_data.append({
                                'Investment': inv,
                                'Start Value': start_row['Value'],
                                'End Value': end_row['Value'],
                                'Absolute Change %': end_row['PctChange'],
                                'Relative Change %': end_row['RelativePct'],
                                'Is Reference': inv == reference_investment
                            })
                    
                    # Convert to DataFrame
                    metrics_df = pd.DataFrame(metrics_data)
                    
                    # Add a column for highlighting the reference investment
                    metrics_df['_style'] = metrics_df['Is Reference'].apply(
                        lambda x: 'background-color: rgba(78, 141, 245, 0.2)' if x else ''
                    )
                    
                    # Format for display
                    display_df = metrics_df.drop(columns=['Is Reference', '_style']).copy()
                    display_df['Start Value'] = display_df['Start Value'].map('${:,.2f}'.format)
                    display_df['End Value'] = display_df['End Value'].map('${:,.2f}'.format)
                    display_df['Absolute Change %'] = display_df['Absolute Change %'].map('{:+.2f}%'.format)
                    display_df['Relative Change %'] = display_df['Relative Change %'].map('{:+.2f}%'.format)
                    
                    # Display metrics
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Investment": st.column_config.TextColumn("Investment"),
                            "Start Value": st.column_config.TextColumn("Start Value"),
                            "End Value": st.column_config.TextColumn("End Value"),
                            "Absolute Change %": st.column_config.TextColumn("Absolute Change %"),
                            "Relative Change %": st.column_config.TextColumn("Relative Change %"),
                        }
                    )
                else:
                    st.warning("Insufficient data for comparative analysis. Ensure the reference investment has data for the selected date range.")
            else:
                st.info("Select a reference investment and comparison investments to view relative performance.")
        else:
            st.warning("No data available for the selected date range.")
    else:
        st.info("No data available. Please add investment entries.")

with tab3:
    # Data tab
    st.header("Investment Data")
    
    if not df.empty:
        # Date filter
        data_cols = st.columns([1, 1, 2])
        with data_cols[0]:
            start_date = st.date_input(
                "From", 
                value=earliest_date,
                min_value=earliest_date,
                max_value=latest_date,
                key="data_start"
            )
        with data_cols[1]:
            end_date = st.date_input(
                "To", 
                value=latest_date,
                min_value=earliest_date,
                max_value=latest_date,
                key="data_end"
            )
        
        # Ensure Investment column contains only strings
        df['Investment'] = df['Investment'].astype(str)
        
        # Get unique investment values and convert to strings before sorting
        unique_investments = [str(inv) for inv in df['Investment'].unique()]
        
        # Investment filter
        investment_filter = st.multiselect(
            "Filter by Investment",
            ["All"] + sorted(unique_investments),
            default=["All"],
            key="investment_filter"
        )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Date filter
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.Timestamp(start_date)) &
            (filtered_df['Date'] <= pd.Timestamp(end_date))
        ]
        
        # Investment filter
        if "All" not in investment_filter:
            filtered_df = filtered_df[filtered_df['Investment'].isin(investment_filter)]
        
        # Sort by date descending
        filtered_df = filtered_df.sort_values('Date', ascending=False)
        
        # Save to session state for potential export
        st.session_state.filtered_df = filtered_df
        
        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("Date"),
                "Investment": st.column_config.TextColumn("Investment"),
                "Currency": st.column_config.TextColumn("Currency"),
                "Value": st.column_config.NumberColumn(
                    "Value",
                    format="%.2f"
                ),
                "ValueUSD": st.column_config.NumberColumn(
                    "Value (USD)",
                    format="$%.2f"
                )
            }
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data",
            data=csv,
            file_name="investment_data_export.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available. Please add investment entries.")

with tab4:
    # Settings tab
    st.header("Settings")
    
    settings_tab1, settings_tab2 = st.tabs(["Data Management", "Configuration"])
    
    with settings_tab1:
        st.subheader("Data Backup and Restore")
        
        # Export full data
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Export All Data",
                data=csv,
                file_name="investment_data_backup.csv",
                mime="text/csv",
                key="export_all"
            )
        
        # Import data
        st.subheader("Import Data")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                import_df = pd.read_csv(uploaded_file, header=None)
                
                # Try to determine the format
                if import_df.shape[1] == 4:
                    # Likely Date, Investment, Currency, Value format
                    import_df.columns = ['Date', 'Investment', 'Currency', 'Value']
                elif import_df.shape[1] == 2:
                    # Likely Investment, Value format
                    import_df.columns = ['Investment', 'Value']
                    import_df['Date'] = pd.Timestamp(datetime.now().date())
                    import_df['Currency'] = import_df['Investment'].apply(
                        lambda inv: investment_accounts.get(str(inv), 'USD')
                    )
                    import_df = import_df[['Date', 'Investment', 'Currency', 'Value']]
                else:
                    # Try with header
                    uploaded_file.seek(0)
                    import_df = pd.read_csv(uploaded_file)
                
                # Process data types
                if 'Date' in import_df.columns:
                    import_df['Date'] = pd.to_datetime(import_df['Date'], format='mixed', errors='coerce')
                    import_df['Date'] = import_df['Date'].fillna(pd.Timestamp(datetime.now().date()))
                
                if 'Investment' in import_df.columns:
                    import_df['Investment'] = import_df['Investment'].astype(str)
                
                if 'Currency' in import_df.columns:
                    import_df['Currency'] = import_df['Currency'].astype(str)
                    # Fix any missing currencies
                    for idx, row in import_df.iterrows():
                        if row['Currency'] == 'nan' or pd.isna(row['Currency']):
                            inv = str(row['Investment'])
                            import_df.at[idx, 'Currency'] = investment_accounts.get(inv, 'USD')
                
                if 'Value' in import_df.columns:
                    import_df['Value'] = pd.to_numeric(import_df['Value'], errors='coerce')
                    import_df = import_df.dropna(subset=['Value'])
                
                # Preview imported data
                st.subheader("Preview Imported Data")
                st.dataframe(
                    import_df.head(5),
                    use_container_width=True
                )
                
                import_action = st.radio(
                    "Import Action",
                    ["Replace all data", "Append to existing data"],
                    key="import_action"
                )
                
                if st.button("Confirm Import"):
                    if import_action == "Replace all data":
                        save_data(import_df)
                        st.success("Data replaced successfully!")
                        st.session_state.show_success = True
                        st.rerun()
                    else:
                        combined_df = pd.concat([df, import_df], ignore_index=True)
                        # Remove potential duplicates
                        combined_df = combined_df.drop_duplicates(
                            subset=['Date', 'Investment', 'Currency', 'Value']
                        )
                        save_data(combined_df)
                        st.success("Data appended successfully!")
                        st.session_state.show_success = True
                        st.rerun()
            except Exception as e:
                st.error(f"Error importing data: {e}")
    
    with settings_tab2:
        st.subheader("Investment Accounts")
        
        # Display configured accounts
        accounts_df = pd.DataFrame({
            'Investment': list(INVESTMENT_ACCOUNTS.keys()),
            'Currency': list(INVESTMENT_ACCOUNTS.values()),
            'Category': [INVESTMENT_CATEGORIES.get(inv, 'Uncategorized') for inv in INVESTMENT_ACCOUNTS.keys()]
        })
        
        # Sort by category and name
        accounts_df = accounts_df.sort_values(['Category', 'Investment'])
        
        st.dataframe(
            accounts_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.info(
            "To add or modify investment accounts and categories, update the INVESTMENT_ACCOUNTS "
            "and INVESTMENT_CATEGORIES dictionaries in config.py."
        )