# app.py
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from datetime import datetime, timedelta
import numpy as np # type: ignore
from data_handler import (
    load_data, 
    save_data, 
    add_entry, 
    add_bulk_entries,
    get_historical_performance,
    get_relative_performance,
    get_previous_values
)
from dashboard_components import (
    create_dashboard_header,
    create_themed_metrics,
    create_enhanced_asset_allocation,
    create_enhanced_currency_breakdown,
    create_enhanced_category_breakdown,
    create_investment_change_table,
    create_portfolio_performance_chart,
    create_enhanced_css,
    apply_theme_mode_toggle,
    create_enhanced_dashboard
)


from currency_service import get_conversion_rate, refresh_rates
from config import INVESTMENT_ACCOUNTS, INVESTMENT_CATEGORIES
import time
import base64
import os
from io import BytesIO
from utils import (
    svg_to_base64,
    get_icon,
    animated_process,
    create_date_picker,
    create_export_buttons,
    apply_chart_styling,
    create_progress_animation,
    get_date_range,
    filter_dataframe,
    create_date_filter_ui,
    update_investment_config  # Add this new import
)

# Ensure icon directory exists
os.makedirs("icons/tabs", exist_ok=True)
os.makedirs("icons/actions", exist_ok=True)
os.makedirs("icons/filters", exist_ok=True)
os.makedirs("icons/categories", exist_ok=True)
os.makedirs("icons/status", exist_ok=True)


# Initialize icons
ICONS = {
    # Tab icons - make all tab icons consistently large
    "dashboard": get_icon("icons/tabs/dashboard.svg", "📊", width=32, height=32),
    "performance": get_icon("icons/tabs/performance.svg", "📈", width=32, height=32),
    "data": get_icon("icons/tabs/data.svg", "📋", width=32, height=32),
    "settings": get_icon("icons/tabs/settings.svg", "⚙️", width=32, height=32),
    
    # Action icons - give these sufficient size too
    "add_entry": get_icon("icons/actions/add_entry.svg", "💾", width=28, height=28),
    "bulk_update": get_icon("icons/actions/bulk_update.svg", "💾", width=28, height=28),
    "update_all": get_icon("icons/actions/update_all.svg", "💾", width=28, height=28),
    "refresh": get_icon("icons/actions/refresh.svg", "🔄", width=28, height=28),
    "download": get_icon("icons/actions/download.svg", "📥", width=28, height=28),
    "save": get_icon("icons/actions/save.svg", "💾", width=28, height=28),
    "import": get_icon("icons/actions/import.svg", "📤", width=28, height=28),
    "export": get_icon("icons/actions/export.svg", "📥", width=28, height=28),
    
    # Filter icons - slightly smaller but consistent
    "search": get_icon("icons/filters/search.svg", "🔍", width=24, height=24),
    "sort": get_icon("icons/filters/sort.svg", "↕️", width=24, height=24),
    "filter": get_icon("icons/filters/filter.svg", "📋", width=24, height=24),
    
    # Category icons
    "folder": get_icon("icons/categories/folder.svg", "📁", width=24, height=24),
    
    # Status icons
    "info": get_icon("icons/status/info.svg", "ℹ️", width=24, height=24),
    "success": get_icon("icons/status/success.svg", "✅", width=24, height=24),
    "warning": get_icon("icons/status/warning.svg", "⚠️", width=24, height=24),
    "error": get_icon("icons/status/error.svg", "❌", width=24, height=24),
}

# Page configuration
st.set_page_config(
    page_title="Advanced Investment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Apply custom styling with animations
st.markdown("""
<style>
    /* Page styling */
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
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"] {
        height: 70px; /* Increased height to accommodate larger icons */
        white-space: pre-wrap;
        background-color: #2c2c40;
        border-radius: 0;
        padding: 10px 20px;
        font-weight: 600;
        color: white;
        min-width: 150px; /* Increased width for better spacing */
        text-align: center;
        border-right: 1px solid #3d3d54;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column; /* Stack icon and text vertically */
        align-items: center;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] span {
        font-size: 32px !important; /* Force larger icons */
        margin-bottom: 8px; /* Increased space between icon and text */
        display: block; /* Make icon a block element */
        line-height: 1.2; /* Better line height for emoji */
    }
    
    /* [Keep the rest of your CSS with these added styles] */
    
    /* Improved styling for icon spans */
    span[style*="font-size"] {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    
    /* Icon alignment in page title and header */
    .main .block-container h1, .main .block-container h2, .main .block-container h3 {
        display: flex;
        align-items: center;
    }
    
    /* Make page icon match other icons */
    [data-testid="stSidebarUserContent"] {
        display: flex;
        align-items: center;
    }
    [data-testid="stSidebarUserContent"] > div {
        font-size: 32px !important;
    }
    
    /* Ensure proper sizing for title emoji */
    h1 span[style*="font-size"], h2 span[style*="font-size"], h3 span[style*="font-size"] {
        min-width: 32px !important;
    }
    /* Styling for tab icons */
    .tab-icon {
        font-size: 32px;
        display: inline-block;
        width: 32px;
        text-align: center;
        line-height: 32px;
        margin-right: 8px;
    }

    /* Styling for action icons */
    .action-icon {
        font-size: 28px;
        display: inline-block;
        width: 28px;
        text-align: center;
        line-height: 28px;
        margin-right: 8px;
    }

    /* Styling for smaller icons */
    .small-icon {
        font-size: 24px;
        display: inline-block;
        width: 24px;
        text-align: center;
        line-height: 24px;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
// This JavaScript would enable scroll animations, but it's for illustration.
// Streamlit's sandboxed environment limits custom JS execution.
// For production, these effects would need to be implemented via Streamlit Components.
</script>
""", unsafe_allow_html=True)

# Function to add entry with animation
# To this:
def add_entry_with_animation(df, date, investment, value):
    spinner_message = "Adding entry..."
    
    def process_func():
        # Just use the parameters without nonlocal
        result_df = add_entry(df, date, investment, value)
        save_data(result_df)
        return result_df
        
    return animated_process(process_func, spinner_message)

# Indentation level: 0 (no indentation)

# Title and description with animation effect
st.markdown('<div class="animate-in">', unsafe_allow_html=True)
st.title("💰 Advanced Investment Tracker")
st.markdown("""
Track your investments across multiple currencies, analyze performance, and visualize your portfolio.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for holding our application state
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = True
if 'animation_complete' not in st.session_state:
    st.session_state.animation_complete = False

# Animated loading of data
if st.session_state.show_loading:
    with st.spinner("Loading your investment data..."):
        create_progress_animation()
    st.session_state.show_loading = False
    st.session_state.animation_complete = True

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
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.header("Add Investment Data")
    
    # Add tab selection for different entry methods
    entry_tab = st.radio(
        "Entry Method",
        ["Single Entry", "Bulk Update", "Update All"],
        key="entry_method",
        horizontal=True  # Make radio buttons horizontal for better UX
    )
    st.markdown('</div>', unsafe_allow_html=True)
        # Add theme mode toggle
    st.markdown("---")
    apply_theme_mode_toggle()
    st.markdown("---")
    
    if entry_tab == "Single Entry":
        # Single entry form with animations
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        st.subheader("Add Single Entry")
        # Sort investments by value in descending order
        if not df.empty:
            # Get the latest values for each investment
            latest_df = df[df['Date'] == df['Date'].max()]
            
            # Create a dict mapping investments to their latest values
            investment_values = {}
            for inv in investment_accounts.keys():
                inv_data = latest_df[latest_df['Investment'] == inv]
                if not inv_data.empty:
                    investment_values[inv] = inv_data.iloc[0]['ValueUSD']
                else:
                    investment_values[inv] = 0  # Default to 0 if no data exists
            
            # Sort investments by their values in descending order
            sorted_investments = sorted(
                list(investment_accounts.keys()),
                key=lambda x: investment_values.get(x, 0),
                reverse=True
            )
        else:
            # If no data exists yet, fall back to alphabetical sorting
            sorted_investments = sorted(list(investment_accounts.keys()))
        
        investment_name = st.selectbox(
            "Investment Account", 
            sorted_investments,
            key="single_investment"
        )
        
        # Get currency from the investment name for better UX
        currency = investment_accounts.get(investment_name, "USD")
        
        investment_value = st.number_input(
            f"Value ({currency})", 
            min_value=0.0, 
            format="%.2f",
            key="single_value"
        )
        
        # Improved date picker with default to today
        entry_date = create_date_picker("use_today", "single_date")
        
        # Animated button with updated icon
        if st.button(f"{get_icon('add_entry', '➕')} Add Entry", key="add_single", use_container_width=True):
            df = add_entry_with_animation(df, entry_date, investment_name, investment_value)
            st.session_state.show_success = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    elif entry_tab == "Bulk Update":
        # Bulk update form with enhanced UI
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
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
        
        # Enhanced multi-select with better styling
        selected_investments = st.multiselect(
            "Select Investments",
            selectable_investments,
            key="bulk_investments"
        )
        
        # Improved date picker with default to today
        bulk_date = create_date_picker("use_today_bulk", "bulk_date")
        
        # Dynamic form generation based on selected investments
        investment_values = {}
        
        if selected_investments:
            st.markdown("### Enter Values")
            # More columns for better space utilization
            num_cols = 3 if len(selected_investments) > 5 else 2
            cols = st.columns(num_cols)
            
            for i, inv in enumerate(selected_investments):
                col_idx = i % num_cols
                with cols[col_idx]:
                    currency = INVESTMENT_ACCOUNTS[inv]
                    investment_values[inv] = st.number_input(
                        f"{inv} ({currency})",
                        min_value=0.0,
                        format="%.2f",
                        key=f"value_{inv}"
                    )
            
            # Animated button with updated icon
            if st.button(f"{ICONS['bulk_update']} Submit All Values", key="add_bulk", use_container_width=True):
                # Use the current value of df directly
                def process_bulk_update():
                    result_df = add_bulk_entries(df, bulk_date, investment_values)
                    save_data(result_df)
                    return result_df
                
                df = animated_process(process_bulk_update, "Processing bulk update...")
                st.session_state.show_success = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
# Indentation level: 1 (inside the "with st.sidebar:" block)

    elif entry_tab == "Update All":
        # Update all form with enhanced UI and animations
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        st.subheader("Update All Investments")
        
        # Improved date picker with default to today
        update_all_date = create_date_picker("use_today_all", "update_all_date")
        
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
            
            # Add a search filter for easier navigation (updated with icon)
            search_term = st.text_input(f"{ICONS['search']} Search investments", key="search_investments")
            
            categories = sorted(list(set(
                [cat for inv, cat in INVESTMENT_CATEGORIES.items()]
            )))
            
            investment_values = {}
            
            # For each category, create an expandable section
            for category in categories:
                # Get investments for this category
                category_investments = sorted([
                    str(inv) for inv, cat in INVESTMENT_CATEGORIES.items() 
                    if cat == category
                ])
                
                # Filter by search term if provided
                if search_term:
                    category_investments = [
                        inv for inv in category_investments 
                        if search_term.lower() in inv.lower()
                    ]
                
                # Only show categories with matching investments if searching
                if not category_investments and search_term:
                    continue
                
                # Use expander for cleaner UI (updated with icon)
                with st.expander(f"{ICONS['folder']} {category} ({len(category_investments)} investments)", expanded=not search_term):
                    # Create three columns layout
                    cols = st.columns(3)
                    
                    for i, inv in enumerate(category_investments):
                        col_idx = i % 3
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
            
            # Animated button with updated icon
            if st.button(f"{ICONS['update_all']} Submit All Investments", key="update_all", use_container_width=True):
                def process_update_all():
                    result_df = add_bulk_entries(df, update_all_date, investment_values)
                    save_data(result_df)
                    return result_df
                
                df = animated_process(process_update_all, "Processing all investments...")
                st.session_state.show_success = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    refresh_col1, refresh_col2 = st.columns([3, 1])
    
    with refresh_col1:
        if st.button(f"{ICONS['refresh']} Refresh Exchange Rates", key="refresh_rates", use_container_width=True):
            animated_process(refresh_rates, "Refreshing rates...")
            st.success(f"{ICONS['success']} Exchange rates refreshed!")
            st.session_state.last_refresh = datetime.now()
    
    with refresh_col2:
        st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M')}")

# Display success message if needed
if st.session_state.show_success:
    st.success(f"{ICONS['success']} Data saved successfully!")
    # Auto-clear the success message after 3 seconds
    time.sleep(2)
    st.session_state.show_success = False

# Main content - Tabbed interface with icons and animations
tab1, tab2, tab3, tab4 = st.tabs([
    f"# {ICONS['dashboard']} Dashboard", 
    f"# {ICONS['performance']} Performance", 
    f"# {ICONS['data']} Data", 
    f"# {ICONS['settings']} Settings"
])
with tab1:
    # Enhanced dashboard tab with thematic colors and advanced visualizations
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    
    # Use the enhanced dashboard component
    if not latest_df.empty:
        create_enhanced_dashboard(df, latest_df, latest_date, INVESTMENT_CATEGORIES, INVESTMENT_ACCOUNTS)
    else:
        st.info(f"{ICONS['info']} No data available. Please add investment entries.")
    
    st.markdown('</div>', unsafe_allow_html=True)
with tab2:
    # Performance tab with enhanced animations and interactivity
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.header("Investment Performance")
    
    if not df.empty:
        # Ensure Investment column contains only strings
        df['Investment'] = df['Investment'].astype(str)
        
        # Date range filters with improved UI
        st.subheader("Select Time Range")
        
        # Add preset date ranges for quick selection
        preset_ranges = st.radio(
            "Preset Ranges",
            ["Custom", "1 Month", "3 Months", "6 Months", "1 Year", "YTD", "All Time"],
            horizontal=True,
            key="preset_date_range"
        )
        
        # Use utility function to get date range based on preset
        if preset_ranges == "Custom":
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
        else:
            # Use our utility function to get date range based on preset
            perf_start, perf_end = get_date_range(preset_ranges, latest_date, earliest_date)
            st.info(f"{ICONS['info']} Date range: {perf_start.strftime('%Y-%m-%d')} to {perf_end.strftime('%Y-%m-%d')}")
        
        # Convert to datetime for filtering
        perf_start_dt = pd.Timestamp(perf_start)
        perf_end_dt = pd.Timestamp(perf_end)
        
        # Get performance data with loading animation
        with st.spinner("Calculating performance data..."):
            performance_data = get_historical_performance(df, perf_start_dt, perf_end_dt)
            time.sleep(0.5)  # Add slight delay for animation
            
# Indentation level: 2 (inside Performance tab, after loading performance data)

        if not performance_data.empty:
            # Total value over time with enhanced visualizations
            st.subheader("Portfolio Value Over Time")
            
            # Group by date and sum values
            total_over_time = performance_data.groupby('Date')['ValueUSD'].sum().reset_index()
            
            # Add visualization options
            value_chart_type = st.radio(
                "Chart Type",
                ["Line", "Area", "Bar", "Candlestick-like"],
                horizontal=True,
                key="value_chart_type"
            )
            
            # Add aggregation options
            if len(total_over_time) > 30:
                show_aggregation = st.checkbox("Aggregate data for smoother visualization", value=False)
                if show_aggregation:
                    agg_method = st.radio(
                        "Aggregation Method",
                        ["Weekly", "Monthly", "Quarterly"],
                        horizontal=True
                    )
                    
                    # Apply aggregation
                    total_over_time['Period'] = total_over_time['Date']
                    if agg_method == "Weekly":
                        total_over_time['Period'] = total_over_time['Date'].dt.to_period('W').dt.start_time
                    elif agg_method == "Monthly":
                        total_over_time['Period'] = total_over_time['Date'].dt.to_period('M').dt.start_time
                    elif agg_method == "Quarterly":
                        total_over_time['Period'] = total_over_time['Date'].dt.to_period('Q').dt.start_time
                    
                    # Group by period and calculate aggregates
                    total_over_time = total_over_time.groupby('Period').agg({
                        'Date': 'last',  # Use last date in period
                        'ValueUSD': 'mean'  # Use average value in period
                    }).reset_index()
            
            # Show annotations option
            show_annotations = st.checkbox("Show trend annotations", value=False)
            
            # Create visualization based on type
            if value_chart_type == "Line":
                fig = px.line(
                    total_over_time,
                    x='Date',
                    y='ValueUSD',
                    labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                    title=''
                )
                fig.update_traces(line=dict(width=3))

            elif value_chart_type == "Area":
                fig = px.area(
                    total_over_time,
                    x='Date',
                    y='ValueUSD',
                    labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                    title=''
                )

            elif value_chart_type == "Bar":
                fig = px.bar(
                    total_over_time,
                    x='Date',
                    y='ValueUSD',
                    labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                    title=''
                )
            else:  # Candlestick-like
                # Create a candlestick-like visualization
                # First, calculate some additional metrics
                if len(total_over_time) > 1:
                    # For each date, calculate high/low based on neighboring points
                    candlestick_data = []
                    for i in range(len(total_over_time)):
                        row = total_over_time.iloc[i]
                        # Base value
                        base_value = row['ValueUSD']
                        
                        # Add some variation for high/low to simulate candlestick
                        if i > 0:
                            prev_value = total_over_time.iloc[i-1]['ValueUSD']
                            change = base_value - prev_value
                            high = base_value + abs(change) * 0.1
                            low = base_value - abs(change) * 0.1
                        else:
                            # For the first point
                            high = base_value * 1.02
                            low = base_value * 0.98
                        
                        candlestick_data.append({
                            'Date': row['Date'],
                            'Open': base_value * 0.99 if i > 0 else base_value,
                            'High': high,
                            'Low': low,
                            'Close': base_value,
                        })

                    candlestick_df = pd.DataFrame(candlestick_data)
                    
                    # Create the figure manually
                    fig = go.Figure()
                    
                    # Add candlestick
                    fig.add_trace(go.Candlestick(
                        x=candlestick_df['Date'],
                        open=candlestick_df['Open'],
                        high=candlestick_df['High'],
                        low=candlestick_df['Low'],
                        close=candlestick_df['Close'],
                        name='Portfolio Value',
                        increasing_line_color='#26a69a', 
                        decreasing_line_color='#ef5350'
                    ))

                    # Add a line trace for the closing values
                    fig.add_trace(go.Scatter(
                        x=candlestick_df['Date'],
                        y=candlestick_df['Close'],
                        line=dict(color='rgba(255, 255, 255, 0.5)', width=1),
                        name='Trend Line'
                    ))
                else:
                    # Fall back to line chart if not enough data points
                    fig = px.line(
                        total_over_time,
                        x='Date',
                        y='ValueUSD',
                        labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                        title=''
                    )
                    
# Indentation level: 3 (inside Performance tab, chart selection conditions)
                
            # Add annotations if requested
            if show_annotations and len(total_over_time) > 1:
                # Identify significant trends
                total_over_time['PctChange'] = total_over_time['ValueUSD'].pct_change() * 100
                
                # Find significant changes (more than 5%)
                significant_changes = total_over_time[abs(total_over_time['PctChange']) > 5].copy()
                
                # Add annotations for significant changes
                annotations = []
                for _, row in significant_changes.iterrows():
                    if pd.notna(row['PctChange']):
                        direction = "↑" if row['PctChange'] > 0 else "↓"
                        annotations.append(dict(
                            x=row['Date'],
                            y=row['ValueUSD'],
                            xref="x",
                            yref="y",
                            text=f"{direction} {abs(row['PctChange']):.1f}%",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor="#ffffff" if row['PctChange'] > 0 else "#ff5555",
                            ax=0,
                            ay=-40 if row['PctChange'] > 0 else 40
                        ))
                
                fig.update_layout(annotations=annotations)
                
            # Apply standard styling with custom parameters
            apply_chart_styling(
                fig, 
                height=400,
                x_title="Date",
                y_title="Value (USD)",
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

            # Investment performance comparison with enhanced UI
            st.subheader("Investment Performance Comparison")
            
            # Get unique investments and ensure they are strings
            investments = [str(inv) for inv in performance_data['Investment'].unique()]
            
            # Set default reference investment to Binance if available
            default_reference = "Binance" if "Binance" in investments else investments[0] if investments else None

            # Add reference investment selection with better UI
            col1, col2 = st.columns([1, 2])
            
            with col1:
                reference_investment = st.selectbox(
                    "Reference Investment (Baseline)",
                    sorted(investments),
                    index=sorted(investments).index(default_reference) if default_reference in sorted(investments) else 0,
                    key="reference_investment"
                )

            # Set default comparison investments
            default_comparisons = []
            for inv in ["401k", "Trade Republic", "RBC"]:
                if inv in investments and inv != reference_investment:
                    default_comparisons.append(inv)
            
            with col2:
                # Let user select investments to compare with checkbox UI
                comparison_investments = st.multiselect(
                    "Select Investments to Compare",
                    sorted(investments),
                    default=default_comparisons,
                    key="performance_investments"
                )
                
# Indentation level: 3 (inside Performance tab, after comparison investments selection)
                
            if reference_investment and comparison_investments:
                # Include reference investment if not already in comparison list
                all_investments = comparison_investments.copy()
                if reference_investment not in all_investments:
                    all_investments.append(reference_investment)

                # Get relative performance data with loading animation
                with st.spinner("Calculating comparison data..."):
                    relative_data = get_relative_performance(
                        df, 
                        perf_start_dt, 
                        perf_end_dt, 
                        reference_investment, 
                        all_investments
                    )
                    time.sleep(0.3)  # Small delay for animation

                if not relative_data.empty:
                    # Create a selection for what to display with improved UI
                    display_opts_col1, display_opts_col2 = st.columns([1, 2])
                    
                    with display_opts_col1:
                        chart_mode = st.radio(
                            "Display mode",
                            ["Relative to Baseline", "Absolute % Change"],
                            horizontal=True,
                            key="performance_mode"
                        )
                    
                    with display_opts_col2:
                        # Add smooth lines option
                        smoothing = st.slider(
                            "Line Smoothing",
                            min_value=0,
                            max_value=10,
                            value=0,
                            help="Higher values create smoother lines"
                        )

# Indentation level: 5 (inside Performance tab, inside relative data display)

                    # Create line chart for comparison based on mode
                    if chart_mode == "Relative to Baseline":
                        y_column = "RelativePct"
                        title = f"Performance Relative to {reference_investment}"
                        y_title = f"% Difference vs {reference_investment}"
                    else:
                        y_column = "PctChange"
                        title = "Absolute Performance (% Change)"
                        y_title = "% Change from Start"
                    
                    # Create enhanced interactive chart
                    fig = px.line(
                        relative_data,
                        x='Date',
                        y=y_column,
                        color='Investment',
                        labels={y_column: y_title, 'Date': 'Date'},
                        title=title,
                        line_shape='spline' if smoothing > 0 else 'linear',  # Smooth lines if requested
                    )

                    # Apply smoothing if requested
                    if smoothing > 0:
                        for trace in fig.data:
                            trace.line.smoothing = smoothing / 10  # Scale to 0-1 range

                    # Add zero line for reference
                    fig.add_hline( 
                        y=0, 
                        line_dash="dash", 
                        line_color="white",
                        opacity=0.5,
                        annotation_text="Baseline" if chart_mode == "Relative to Baseline" else "No Change",
                        annotation_position="bottom right"
                    )

                    # Add markers for data points
                    show_markers = st.checkbox("Show data points", value=False)
                    if show_markers:
                        for trace in fig.data:
                            trace.mode = 'lines+markers'
                            
                    # Update styling with enhanced interactivity
                    fig.update_traces(line=dict(width=2.5))
                    
                    # Apply our standard styling function with custom parameters
                    apply_chart_styling(
                        fig,
                        height=500,
                        x_title="Date",
                        y_title=y_title,
                        margin=dict(l=20, r=20, t=50, b=50),
                        hovermode="x unified"
                    )
                    
                    # Add custom legend positioning
                    fig.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                        # Add animations for line transitions
                        transition_duration=500
                    )

                    # Make the reference investment line stand out
                    for i, trace in enumerate(fig.data):
                        if trace.name == reference_investment:
                            trace.line.width = 4
                            trace.line.dash = 'solid'
                        else:
                            trace.line.width = 2.5

                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
# Indentation level: 5 (inside Performance tab, inside relative data display)

                    # Calculate and display performance metrics with enhanced styling
                    st.subheader("Performance Metrics")

                    # Option to show detailed analysis
                    show_detailed = st.checkbox("Show detailed analysis", value=False)
                    
                    # Prepare metrics data
                    metrics_data = []
                    for inv in all_investments:
                        inv_data = relative_data[relative_data['Investment'] == inv]
                        if not inv_data.empty:
                            start_date = inv_data['Date'].min()
                            end_date = inv_data['Date'].max()

                            start_row = inv_data[inv_data['Date'] == start_date].iloc[0]
                            end_row = inv_data[inv_data['Date'] == end_date].iloc[0]
                            
                            # Calculate additional metrics
                            days_between = (end_date - start_date).days
                            
                            # Calculate compounded annual growth rate (CAGR)
                            if days_between > 0:
                                years = days_between / 365
                                cagr = ((1 + end_row['PctChange']/100) ** (1/years) - 1) * 100 if years > 0 else 0
                            else:
                                cagr = 0
                                
                            # Add standard metrics
                            metric_row = { 
                                'Investment': inv,
                                'Start Value': start_row['Value'],
                                'End Value': end_row['Value'],
                                'Absolute Change %': end_row['PctChange'],
                                'Relative Change %': end_row['RelativePct'],
                                'Is Reference': inv == reference_investment
                            }
                            
                            # Add detailed metrics if requested
                            if show_detailed:
                                # Calculate more metrics
                                if days_between > 30:
                                    # Calculate volatility (standard deviation of percentage changes)
                                    # First, we need daily percentage changes
                                    if len(inv_data) > 1:
                                        pct_changes = inv_data['Value'].pct_change().dropna() * 100
                                        volatility = pct_changes.std()
                                    else:
                                        volatility = 0
                                        
                                    # Add to metrics
                                    metric_row.update({
                                        'CAGR': cagr,
                                        'Volatility': volatility,
                                        'Days': days_between
                                    })
                            
                            metrics_data.append(metric_row)

                    # Convert to DataFrame
# REPLACE THE EXISTING DATAFRAME DISPLAY CODE BELOW THIS LINE
                    # Create a style function for the metrics table
                    def apply_metrics_styling(df_to_style):
                        # Function to determine color based on investment performance
                        def style_row(row):
                            is_reference = row.get('Is Reference', False)
                            
                            if is_reference:
                                # Reference investment gets a distinct blue styling
                                return ['background-color: rgba(59, 130, 246, 0.1); color: #60a5fa;'] * len(df_to_style.columns)
                            
                            # For non-reference investments, style based on relative performance
                            if "Absolute Change %" in row and pd.notna(row["Absolute Change %"]):
                                # We need to check if row still contains numeric value or formatted string
                                try:
                                    if isinstance(row["Absolute Change %"], str):
                                        # Try to extract number from formatted string like "+5.20%"
                                        change_text = row["Absolute Change %"].replace("%", "").replace("+", "")
                                        change_value = float(change_text)
                                    else:
                                        change_value = row["Absolute Change %"]
                                    
                                    if change_value > 0:
                                        # Green for positive performance
                                        return ['background-color: rgba(74, 222, 128, 0.1); color: #4ade80;'] * len(df_to_style.columns)
                                    elif change_value < 0:
                                        # Red for negative performance
                                        return ['background-color: rgba(248, 113, 113, 0.1); color: #f87171;'] * len(df_to_style.columns)
                                except (ValueError, TypeError):
                                    # If we can't parse the value, use neutral styling
                                    pass
                            
                            # Default/neutral styling
                            return ['background-color: rgba(156, 163, 175, 0.1); color: #9ca3af;'] * len(df_to_style.columns)
                        
                        # Apply the styling to each row
                        return df_to_style.style.apply(style_row, axis=1)
                    
                    # Convert to DataFrame
                    metrics_df = pd.DataFrame(metrics_data)
                    
                    # Prepare display dataframe (dropping internal columns)
                    display_columns = [col for col in metrics_df.columns if not col.startswith('_') and col != 'Is Reference']
                    display_df = metrics_df[display_columns].copy()
                    
                    # Format for display
                    display_df['Start Value'] = display_df['Start Value'].map('${:,.2f}'.format)
                    display_df['End Value'] = display_df['End Value'].map('${:,.2f}'.format)
                    display_df['Absolute Change %'] = display_df['Absolute Change %'].map('{:+.2f}%'.format)
                    display_df['Relative Change %'] = display_df['Relative Change %'].map('{:+.2f}%'.format)
# END OF REPLACEMENT BLOCK                    
                    # Add detailed columns if present
                    if show_detailed and 'CAGR' in display_df.columns:
                        display_df['CAGR'] = display_df['CAGR'].map('{:+.2f}%'.format)
                        display_df['Volatility'] = display_df['Volatility'].map('{:.2f}%'.format)
                        display_df['Days'] = display_df['Days'].astype(int)
                        
                    # Display metrics with enhanced styling
                    # Display metrics with enhanced styling
                    st.dataframe(
                        apply_metrics_styling(display_df),
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
                    
# Indentation level: 5 (inside Performance tab, inside relative data display)

                    # Add a visualization of the metrics
                    if st.checkbox("Show metrics visualization", value=False):
                        metric_to_plot = "Absolute Change %" if chart_mode == "Absolute % Change" else "Relative Change %"
                        
                        # Create a horizontal bar chart
                        bar_fig = px.bar(
                            metrics_df,
                            y='Investment',
                            x='Absolute Change %' if metric_to_plot == "Absolute Change %" else 'Relative Change %',
                            color='Investment',
                            orientation='h',
                            title=f"{metric_to_plot} by Investment"
                        )
                        
                        # Apply our standard styling
                        apply_chart_styling(
                            bar_fig,
                            height=300,
                            x_title=metric_to_plot,
                            y_title=""
                        )
                        
                        st.plotly_chart(bar_fig, use_container_width=True)
                else:
                    st.warning(f"{ICONS['warning']} Insufficient data for comparative analysis. Ensure the reference investment has data for the selected date range.")
            else:
                st.info(f"{ICONS['info']} Select a reference investment and comparison investments to view relative performance.")
        else:
            st.warning(f"{ICONS['warning']} No data available for the selected date range.")
    else:
        st.info(f"{ICONS['info']} No data available. Please add investment entries.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    # Data tab with enhanced filtering and visualization
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.header("Investment Data")
    
    if not df.empty:
        # Enhanced date filter with preset options
        st.subheader("Date Filter")
        
        # Use our utility function to create a date filter UI component
        start_date, end_date = create_date_filter_ui(
            earliest_date, 
            latest_date, 
            filter_type_key="data_filter_type",
            preset_key="data_preset", 
            start_key="data_start", 
            end_key="data_end",
            specific_date_type_key="data_specific_date_type", 
            specific_date_key="data_specific_date"
        )
        
        # Ensure Investment column contains only strings
        df['Investment'] = df['Investment'].astype(str)
        
        # Get unique investment values and convert to strings before sorting
        unique_investments = [str(inv) for inv in df['Investment'].unique()]
        
        # Enhanced investment filter with better UI
        st.subheader("Investment Filter")
        
        # Group investments by category
        investments_by_category = {}
        for inv in unique_investments:
            category = INVESTMENT_CATEGORIES.get(inv, "Uncategorized")
            if category not in investments_by_category:
                investments_by_category[category] = []
            investments_by_category[category].append(inv)
        
        # Sort categories and investments
        sorted_categories = sorted(investments_by_category.keys())
        
# Indentation level: 2 (inside Data tab, after sorted_categories)

        # Create grouped investment filter
        filter_mode = st.radio(
            "Filter Mode",
            ["All", "By Category", "Custom Selection"],
            horizontal=True,
            key="investment_filter_mode"
        )
        
        if filter_mode == "All":
            investment_filter = ["All"]
        elif filter_mode == "By Category":
            selected_categories = st.multiselect(
                "Select Categories",
                sorted_categories,
                default=[sorted_categories[0]] if sorted_categories else [],
                key="category_filter"
            )
            
            # Get all investments for selected categories
            investment_filter = []
            for cat in selected_categories:
                investment_filter.extend(investments_by_category.get(cat, []))
        else:  # Custom Selection
            investment_filter = st.multiselect(
                "Select Investments",
                ["All"] + sorted(unique_investments),
                default=["All"],
                key="investment_filter"
            )
            
        # Apply filters with animation
        with st.spinner("Filtering data..."):
            # Use our utility function to filter the dataframe
            filtered_df = filter_dataframe(df, start_date, end_date, investment_filter)
            
            # Sort by date descending
            filtered_df = filtered_df.sort_values('Date', ascending=False)
            
            # Save to session state for potential export
            st.session_state.filtered_df = filtered_df
            
            # Add a small delay for animation effect
            time.sleep(0.3)
        
        # Display data with enhanced controls
        st.subheader("Investment Data")
        
        # Add search functionality (updated with icon)
        search_query = st.text_input(f"{ICONS['search']} Search in data", key="data_search")
        if search_query:
            filtered_df = filtered_df[
                filtered_df.astype(str).apply(
                    lambda row: row.str.contains(search_query, case=False).any(), 
                    axis=1
                )
            ]
        
        # Add view options
        view_options_col1, view_options_col2, view_options_col3 = st.columns(3)
        
        with view_options_col1:
            rows_per_page = st.selectbox(
                "Rows per page",
                [10, 25, 50, 100, "All"],
                index=1,  # Default to 25
                key="rows_per_page"
            )
        
        with view_options_col2:
            sort_column = st.selectbox(
                f"{ICONS['sort']} Sort by",
                ["Date", "Investment", "Currency", "Value", "Value (USD)"],
                index=0,  # Default to Date
                key="sort_column"
            )
        
        with view_options_col3:
            sort_order = st.radio(
                "Order",
                ["Descending", "Ascending"],
                horizontal=True,
                key="sort_order"
            )
            
# Indentation level: 2 (inside Data tab, after view options)

        # Apply view options
        # Apply sorting
        if sort_column == "Date":
            sorted_df = filtered_df.sort_values('Date', ascending=(sort_order == "Ascending"))
        elif sort_column == "Investment":
            sorted_df = filtered_df.sort_values('Investment', ascending=(sort_order == "Ascending"))
        elif sort_column == "Currency":
            sorted_df = filtered_df.sort_values('Currency', ascending=(sort_order == "Ascending"))
        elif sort_column == "Value":
            sorted_df = filtered_df.sort_values('Value', ascending=(sort_order == "Ascending"))
        elif sort_column == "Value (USD)":
            sorted_df = filtered_df.sort_values('ValueUSD', ascending=(sort_order == "Ascending"))
        else:
            sorted_df = filtered_df
        
        # Pagination
        if rows_per_page != "All":
            total_pages = max(1, int(np.ceil(len(sorted_df) / rows_per_page)))
            page = st.number_input(
                f"Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="data_page"
            )
            
            # Calculate start and end indices
            start_idx = (page - 1) * rows_per_page
            end_idx = min(start_idx + rows_per_page, len(sorted_df))
            
            # Get data for current page
            display_df = sorted_df.iloc[start_idx:end_idx]
            
            # Show pagination info
            st.caption(f"Showing {start_idx+1}-{end_idx} of {len(sorted_df)} entries")
        else:
            display_df = sorted_df
        
        # Display data with enhanced styling
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Investment": st.column_config.TextColumn("Investment"),
                "Current Value (USD)": st.column_config.TextColumn("Current Value (USD)", help="Value in USD"),
                "Change (USD)": st.column_config.TextColumn("Change (USD)", help="Change in USD"),
                "Current Value": st.column_config.TextColumn("Current Value"),
                "Change": st.column_config.TextColumn("Change")
            }
        )
        
        # Summary statistics
        if st.checkbox("Show summary statistics", value=False):
            st.subheader("Summary Statistics")
            
            # Calculate statistics
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("Total Entries", len(filtered_df))
                st.metric("Date Range", f"{filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}")
            
            with stats_col2:
                st.metric("Unique Investments", filtered_df['Investment'].nunique())
                st.metric("Currencies", ", ".join(filtered_df['Currency'].unique()))
            
            # Prepare summary stats by investment
            investment_summary = filtered_df.groupby('Investment').agg({
                'Value': ['count', 'min', 'max', 'mean'],
                'ValueUSD': ['min', 'max', 'mean', 'sum']
            }).reset_index()
            
            # Flatten multi-level columns
            investment_summary.columns = ['Investment', 'Count', 'Min', 'Max', 'Avg', 'Min (USD)', 'Max (USD)', 'Avg (USD)', 'Total (USD)']
            
            # Format for display
            for col in ['Min', 'Max', 'Avg']:
                investment_summary[col] = investment_summary[col].map('{:.2f}'.format)
            
            for col in ['Min (USD)', 'Max (USD)', 'Avg (USD)', 'Total (USD)']:
                investment_summary[col] = investment_summary[col].map('${:.2f}'.format)
            
            # Display summary
            st.dataframe(
                investment_summary,
                use_container_width=True,
                hide_index=True
            )
        
        # Download button with options
        st.subheader("Export Data")
        export_options_col1, export_options_col2 = st.columns(2)
        
        with export_options_col1:
            export_format = st.radio(
                "Export Format",
                ["CSV", "Excel", "JSON"],
                horizontal=True,
                key="export_format"
            )
        
        with export_options_col2:
            export_scope = st.radio(
                "Export Scope",
                ["Filtered Data", "Current Page", "All Data"],
                horizontal=True,
                key="export_scope"
            )
            
# Indentation level: 2 (inside Data tab, after export options)
        
        # Determine what to export
        if export_scope == "Filtered Data":
            export_df = filtered_df
        elif export_scope == "Current Page":
            export_df = display_df
        else:  # All Data
            export_df = df
        
        # Use our utility function to create export buttons
        create_export_buttons(
            export_df=export_df,
            export_format=export_format,
            filename_prefix="investment_data_export",
            button_label="Download Data",
            icon=ICONS['export']
        )
    else:
        st.info(f"{ICONS['info']} No data available. Please add investment entries.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    # Settings tab with enhanced UI and animations
    
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.header("Settings")

    settings_tab1, settings_tab2 = st.tabs(["Data Management", "Configuration"])
    
    with settings_tab1:
        st.subheader("Data Backup and Restore")
        
        # Export full data with enhanced options
        if not df.empty:
            backup_col1, backup_col2 = st.columns(2)
            
            with backup_col1:
                backup_format = st.radio(
                    "Backup Format",
                    ["CSV", "Excel", "JSON"],
                    horizontal=True,
                    key="backup_format"
                )
            
            with backup_col2:
                backup_name = st.text_input(
                    "Backup File Name",
                    value=f"investment_data_backup_{datetime.now().strftime('%Y%m%d')}",
                    key="backup_name"
                )
            
            # Use our utility function to create export buttons
            create_export_buttons(
                export_df=df,
                export_format=backup_format,
                filename_prefix=backup_name,
                button_label="Export All Data",
                icon=ICONS['save']
            )
            
        # Import data with enhanced UI
        st.subheader("Import Data")
        
        import_col1, import_col2 = st.columns(2)
        
        with import_col1:
            st.write("Upload data file:")
            uploaded_file = st.file_uploader("Upload CSV", type=['csv', 'xlsx', 'json'], key="data_upload")
        
        with import_col2:
            st.write("Example file format:")
            st.code("""
            Date,Investment,Currency,Value
            2023-01-01,Binance,USD,10000.00
            2023-01-01,Trade Republic,EUR,5000.00
            ...
            """)
            
# Indentation level: 2 (inside Settings tab, inside settings_tab1)
        
        if uploaded_file is not None:
            try:
                # Determine file type by extension
                file_ext = uploaded_file.name.split('.')[-1].lower()
                
                if file_ext == 'csv':
                    # Try to read CSV
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
                
                elif file_ext == 'xlsx':
                    # Read Excel file
                    import_df = pd.read_excel(uploaded_file)
                
                else:  # JSON
                    # Read JSON file
                    import_df = pd.read_json(uploaded_file)
                
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
                
                # Preview imported data with animated loader
                st.subheader("Preview Imported Data")
                
                with st.spinner("Processing data..."):
                    time.sleep(0.5)  # Short delay for animation
                
                st.dataframe(
                    import_df.head(5),
                    use_container_width=True
                )
                
                # Data import options
                import_action = st.radio(
                    "Import Action",
                    ["Replace all data", "Append to existing data", "Update existing entries"],
                    key="import_action"
                )
                
                if st.button(f"{ICONS['import']} Confirm Import", key="confirm_import", use_container_width=True):
                    def process_import():
                        if import_action == "Replace all data":
                            df_result = import_df
                            save_data(df_result)
                            return df_result
                        elif import_action == "Append to existing data":
                            combined_df = pd.concat([df, import_df], ignore_index=True)
                            # Remove potential duplicates
                            combined_df = combined_df.drop_duplicates(
                                subset=['Date', 'Investment', 'Currency', 'Value']
                            )
                            save_data(combined_df)
                            return combined_df
                        else:  # Update existing entries
                            # For each row in import_df, update if it exists, append if not
                            result_df = df.copy()
                            
                            for _, row in import_df.iterrows():
                                # Check if entry exists
                                mask = (
                                    (result_df['Date'] == row['Date']) & 
                                    (result_df['Investment'] == row['Investment'])
                                )
                                
                                if mask.any():
                                    # Update existing entry
                                    result_df.loc[mask, 'Value'] = row['Value']
                                    result_df.loc[mask, 'Currency'] = row['Currency']
                                else:
                                    # Append new entry
                                    result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)
                            
                            save_data(result_df)
                            return result_df
                    
                    # Use our animated process function
                    df = animated_process(process_import, "Processing import...")
                    st.success(f"{ICONS['success']} Data imported successfully!")
                    st.session_state.show_success = True
                    st.rerun()
            except Exception as e:
                st.error(f"{ICONS['error']} Error importing data: {e}")
                
# Indentation level: 1 (inside the settings_tab2)

    with settings_tab2:
        st.subheader("Investment Accounts and Categories")
        
        # Display configured accounts with improved styling
        accounts_df = pd.DataFrame({
            'Investment': list(INVESTMENT_ACCOUNTS.keys()),
            'Currency': list(INVESTMENT_ACCOUNTS.values()),
            'Category': [INVESTMENT_CATEGORIES.get(inv, 'Uncategorized') for inv in INVESTMENT_ACCOUNTS.keys()]
        })
        
        # Allow filtering
        filter_accounts = st.text_input(f"{ICONS['search']} Filter accounts", key="account_filter")
        if filter_accounts:
            accounts_df = accounts_df[
                accounts_df.astype(str).apply(
                    lambda row: row.str.contains(filter_accounts, case=False).any(), 
                    axis=1
                )
            ]
        
        # Group by category for better presentation
        category_filter = st.multiselect(
            "Filter by Category",
            ["All"] + sorted(set(accounts_df['Category'].tolist())),
            default=["All"],
            key="config_category_filter"
        )
        
        if "All" not in category_filter:
            accounts_df = accounts_df[accounts_df['Category'].isin(category_filter)]
        
        # Sort by category and name
        accounts_df = accounts_df.sort_values(['Category', 'Investment'])
        
        st.dataframe(
            accounts_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Investment": st.column_config.TextColumn("Investment Account"),
                "Currency": st.column_config.TextColumn("Currency"),
                "Category": st.column_config.TextColumn("Category")
            }
        )
        
        # Replace the static info message with a dynamic investment creation section
        st.markdown("---")
        st.subheader("Add New Investment")
        
        with st.form(key="add_investment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_investment_name = st.text_input("Investment Name", key="new_investment_name")
                
                # Get unique categories from existing investments
                existing_categories = sorted(set(INVESTMENT_CATEGORIES.values()))
                
                new_investment_category = st.selectbox(
                    "Category",
                    existing_categories + ["Add New Category"],
                    key="new_investment_category"
                )
                
                # Option to add a new category if selected
                if new_investment_category == "Add New Category":
                    new_investment_category = st.text_input("Enter New Category Name", key="custom_category")
            
            with col2:
                # Available currencies
                available_currencies = sorted(set(INVESTMENT_ACCOUNTS.values()))
                new_investment_currency = st.selectbox(
                    "Currency",
                    available_currencies,
                    key="new_investment_currency"
                )
                
                # Option to add this investment to tracked investments
                add_to_tracked = st.checkbox("Add to Tracked Investments", value=False, key="add_to_tracked")
            
            submit_button = st.form_submit_button(f"{ICONS['save']} Add Investment", use_container_width=True)
            
            if submit_button:
                if new_investment_name and new_investment_category:
                    try:
                        # Update the config file
                        update_investment_config(
                            new_investment_name, 
                            new_investment_currency, 
                            new_investment_category,
                            add_to_tracked
                        )
                        st.success(f"{ICONS['success']} Investment '{new_investment_name}' added successfully! Refresh the page to see it in the lists.")
                        # Add refresh button
                        if st.button(f"{ICONS['refresh']} Refresh Page", key="refresh_after_add"):
                            st.experimental_rerun()
                        st.info("You may need to restart the application to apply all changes.")
                    except Exception as e:
                        st.error(f"{ICONS['error']} Error adding investment: {str(e)}")
                else:
                    st.warning(f"{ICONS['warning']} Please provide both an investment name and category.")
        
        # Exchange rate settings
        st.subheader("Exchange Rate Settings")
        
        # Load current exchange rates
        from currency_service import get_all_rates, load_cache
        
        cache = load_cache()
        
        # Display last update time
        last_updated = cache.get('last_updated', 'Never')
        st.write(f"Exchange rates last updated: {last_updated}")
        
        # Display current rates
        if 'rates' in cache and cache['rates']:
            rates_df = pd.DataFrame({
                'Currency': list(cache['rates'].keys()),
                'Rate to USD': list(cache['rates'].values())
            })
            
            # Sort by currency
            rates_df = rates_df.sort_values('Currency')
            
            st.dataframe(
                rates_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Add refresh button
            if st.button(f"{ICONS['refresh']} Force Refresh Exchange Rates", key="force_refresh", use_container_width=True):
                with st.spinner("Refreshing exchange rates..."):
                    refresh_rates()
                    time.sleep(0.5)  # Wait for refresh to complete
                    st.success(f"{ICONS['success']} Exchange rates refreshed successfully!")
                    st.rerun()
        else:
            st.warning(f"{ICONS['warning']} No exchange rates found. Click refresh to fetch current rates.")
            
            if st.button(f"{ICONS['refresh']} Fetch Exchange Rates", key="fetch_rates", use_container_width=True):
                with st.spinner("Fetching exchange rates..."):
                    refresh_rates()
                    time.sleep(0.5)  # Wait for refresh to complete
                    st.success(f"{ICONS['success']} Exchange rates fetched successfully!")
                    st.rerun()
                    
        # App information
        st.subheader("About This App")
        
        st.markdown("""
        ### Enhanced Investment Tracker

        A comprehensive application for tracking investments across multiple currencies, visualizing performance, and analyzing your financial portfolio.

        **Features:**
        - Multi-Currency Support with automatic exchange rate updates
        - Historical Performance Tracking with animated visualizations
        - Interactive dashboards with filtering capabilities
        - Flexible data management with import/export options
        - Category-based organization of investments

        **App Version:** 2.0 (Enhanced UI & Animations)
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)