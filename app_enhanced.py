# app_enhanced.py
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
from currency_service import get_conversion_rate, refresh_rates
from config import INVESTMENT_ACCOUNTS, INVESTMENT_CATEGORIES
import time
import base64
import os

# Function to encode SVG images for embedding
def svg_to_base64(file_path):
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/svg+xml;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading SVG {file_path}: {e}")
        return None

# Function to get an icon (SVG or emoji fallback)
def get_icon(icon_path, emoji_fallback, width=24, height=24, style=""):
    base_icon = svg_to_base64(icon_path)
    if base_icon:
        return f'<img src="{base_icon}" width="{width}" height="{height}" style="vertical-align: middle; {style}">'
    else:
        return emoji_fallback

# Ensure icon directory exists
os.makedirs("icons/tabs", exist_ok=True)
os.makedirs("icons/actions", exist_ok=True)
os.makedirs("icons/filters", exist_ok=True)
os.makedirs("icons/categories", exist_ok=True)
os.makedirs("icons/status", exist_ok=True)


# Initialize icons
ICONS = {
    # Tab icons
    "dashboard": get_icon("icons/tabs/dashboard.svg", "📊", width=32, height=32),
    "performance": get_icon("icons/tabs/performance.svg", "📈", width=32, height=32),
    "data": get_icon("icons/tabs/data.svg", "📋", width=32, height=32),
    "settings": get_icon("icons/tabs/settings.svg", "⚙️", width=32, height=32),
    
    # Action icons
    "add_entry": get_icon("icons/actions/add_entry.svg", "💾"),
    "bulk_update": get_icon("icons/actions/bulk_update.svg", "💾"),
    "update_all": get_icon("icons/actions/update_all.svg", "💾"),
    "refresh": get_icon("icons/actions/refresh.svg", "🔄"),
    "download": get_icon("icons/actions/download.svg", "📥"),
    "save": get_icon("icons/actions/save.svg", "💾"),
    "import": get_icon("icons/actions/import.svg", "📤"),
    "export": get_icon("icons/actions/export.svg", "📥"),
    
    # Filter icons
    "search": get_icon("icons/filters/search.svg", "🔍"),
    "sort": get_icon("icons/filters/sort.svg", "↕️"),
    "filter": get_icon("icons/filters/filter.svg", "📋"),
    
    # Category icons
    "folder": get_icon("icons/categories/folder.svg", "📁"),
    
    # Status icons
    "info": get_icon("icons/status/info.svg", "ℹ️"),
    "success": get_icon("icons/status/success.svg", "✅"),
    "warning": get_icon("icons/status/warning.svg", "⚠️"),
    "error": get_icon("icons/status/error.svg", "❌"),
}

# Ensure icon directory exists
os.makedirs("icons/tabs", exist_ok=True)
os.makedirs("icons/actions", exist_ok=True)
os.makedirs("icons/filters", exist_ok=True)
os.makedirs("icons/categories", exist_ok=True)
os.makedirs("icons/status", exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Advanced Investment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)# Apply custom styling with animations
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
        height: 60px; /* Increased height */
        white-space: pre-wrap;
        background-color: #2c2c40;
        border-radius: 0;
        padding: 10px 20px;
        font-weight: 600;
        color: white;
        min-width: 140px;
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
        margin-bottom: 5px; /* Add space between icon and text */
        display: block; /* Make icon a block element */
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3d3d60;
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab"]:last-child {
        border-right: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
        font-weight: 700;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Animation for cards and containers */
    .animate-in {
        animation: fadeIn 0.5s ease-in-out forwards;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Rest of your CSS... */
""", unsafe_allow_html=True)
st.markdown("""
<script>
// This JavaScript would enable scroll animations, but it's for illustration.
// Streamlit's sandboxed environment limits custom JS execution.
// For production, these effects would need to be implemented via Streamlit Components.
</script>
""", unsafe_allow_html=True)

# Title and description with animation effect
st.markdown('<div class="animate-in">', unsafe_allow_html=True)
st.title("💰 Advanced Investment Tracker")
st.markdown("""
Track your investments across multiple currencies, analyze performance, and visualize your portfolio.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Progress animation function for loading data
def load_with_animation():
    progress_bar = st.progress(0)
    for i in range(101):
        # Update progress bar
        progress_bar.progress(i)
        time.sleep(0.01)  # Small delay for animation effect
    return

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
        load_with_animation()
    st.session_state.show_loading = False
    st.session_state.animation_complete = True# Load data
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

# Function to add entry with animation
def add_entry_with_animation(df, date, investment, value):
    with st.spinner("Adding entry..."):
        progress_bar = st.progress(0)
        for i in range(101):
            progress_bar.progress(i)
            time.sleep(0.005)  # Faster animation
            
        df = add_entry(df, date, investment, value)
        save_data(df)
    return df# Sidebar: Data Entry Section
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
    
    if entry_tab == "Single Entry":
        # Single entry form with animations
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        st.subheader("Add Single Entry")
        investment_name = st.selectbox(
            "Investment Account", 
            sorted(list(investment_accounts.keys())),
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
        col1, col2 = st.columns(2)
        with col1:
            use_today = st.checkbox("Use today's date", value=True, key="use_today")
        
        with col2:
            if use_today:
                entry_date = datetime.now().date()
                st.info(f"Using: {entry_date.strftime('%Y-%m-%d')}")
            else:
                entry_date = st.date_input(
                    "Entry Date", 
                    value=datetime.now(),
                    key="single_date"
                )
        
        # Animated button
        if st.button("💾 Add Entry", key="add_single"):
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
        col1, col2 = st.columns(2)
        with col1:
            use_today_bulk = st.checkbox("Use today's date", value=True, key="use_today_bulk")
        
        with col2:
            if use_today_bulk:
                bulk_date = datetime.now().date()
                st.info(f"Using: {bulk_date.strftime('%Y-%m-%d')}")
            else:
                bulk_date = st.date_input(
                    "Entry Date",
                    value=datetime.now(),
                    key="bulk_date"
                )
        
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
            
            # Animated button with icon
            if st.button("💾 Submit All Values", key="add_bulk"):
                with st.spinner("Processing bulk update..."):
                    progress_bar = st.progress(0)
                    for i in range(101):
                        progress_bar.progress(i)
                        time.sleep(0.01)
                        
                    df = add_bulk_entries(df, bulk_date, investment_values)
                    save_data(df)
                    
                st.session_state.show_success = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif entry_tab == "Update All":
        # Update all form with enhanced UI and animations
        st.markdown('<div class="animate-in">', unsafe_allow_html=True)
        st.subheader("Update All Investments")
        
        # Improved date picker with default to today
        col1, col2 = st.columns(2)
        with col1:
            use_today_all = st.checkbox("Use today's date", value=True, key="use_today_all")
        
        with col2:
            if use_today_all:
                update_all_date = datetime.now().date()
                st.info(f"Using: {update_all_date.strftime('%Y-%m-%d')}")
            else:
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
            
            # Add a search filter for easier navigation
            search_term = st.text_input("🔍 Search investments", key="search_investments")
            
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
                
                # Use expander for cleaner UI
                with st.expander(f"📁 {category} ({len(category_investments)} investments)", expanded=not search_term):
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
            
            # Animated button with icon
            if st.button("💾 Submit All Investments", key="update_all"):
                with st.spinner("Processing all investments..."):
                    progress_bar = st.progress(0)
                    for i in range(101):
                        progress_bar.progress(i)
                        time.sleep(0.01)
                        
                    df = add_bulk_entries(df, update_all_date, investment_values)
                    save_data(df)
                    
                st.session_state.show_success = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    refresh_col1, refresh_col2 = st.columns([3, 1])
    
    with refresh_col1:
        if st.button("🔄 Refresh Exchange Rates"):
            with st.spinner("Refreshing rates..."):
                progress_bar = st.progress(0)
                for i in range(101):
                    progress_bar.progress(i)
                    time.sleep(0.01)
                    
                refresh_rates()
                
            st.success("Exchange rates refreshed!")
            st.session_state.last_refresh = datetime.now()
    
    with refresh_col2:
        st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M')}")

# Display success message if needed
if st.session_state.show_success:
    st.success("✅ Data saved successfully!")
    # Auto-clear the success message after 3 seconds
    time.sleep(2)
    st.session_state.show_success = False # Main content - Tabbed interface with icons and animations
tab1, tab2, tab3, tab4 = st.tabs([
    "📊📊📊 Dashboard", 
    "📈📈📈 Performance", 
    "📋📋📋 Data", 
    "⚙️⚙️⚙️ Settings"
])

with tab1:
    # Dashboard tab with animations
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.header("Portfolio Dashboard")
    
    if not latest_df.empty:
        # Top metrics row with enhanced animations
        total_usd = latest_df['ValueUSD'].sum()
        
        # Add a loading effect
        with st.spinner("Loading dashboard metrics..."):
            time.sleep(0.5)  # Short delay for animation effect
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric(
                "Total Portfolio Value", 
                f"${total_usd:,.2f} USD"
            )
        
        # Calculate 1 month change with improved error handling
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
            else:
                with metrics_col2:
                    st.metric("1 Month Change", "N/A")
        except Exception as e:
            with metrics_col2:
                st.metric("1 Month Change", "N/A")# Calculate 3 month change
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
            else:
                with metrics_col3:
                    st.metric("3 Month Change", "N/A")
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
            else:
                with metrics_col4:
                    st.metric("YTD Change", "N/A")
        except Exception as e:
            with metrics_col4:
                st.metric("YTD Change", "N/A")
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
                            "_sort_value": abs(change_usd),  # For sorting
                            "_change_pct": change_usd_pct,   # For conditional formatting
                            # Add these numeric columns for sorting
                            "Current Value Num": current_value_usd,
                            "Change Num": change_usd,
                            "Change Pct Num": change_usd_pct
                        })
                    else:
                        # No previous data for this investment
                        changes_data.append({
                            "Investment": inv,
                            "Current Value": f"{current_value:,.2f} {currency}",
                            "Current Value (USD)": f"${current_value_usd:,.2f}",
                            "Change": f"{change:+,.2f} {currency} ({change_pct:+.2f}%)",
                            "Change (USD)": f"${change_usd:+,.2f} ({change_usd_pct:+.2f}%)",
                            "Previous Update": f"{days_between} days ago",
                            "_sort_value": abs(change_usd),  # For sorting
                            "_change_pct": change_usd_pct,   # For conditional formatting
                            # Add these numeric columns for sorting
                            "Current Value Num": current_value_usd,
                            "Change Num": change_usd,
                            "Change Pct Num": change_usd_pct
                        })
                
                # Create DataFrame and sort by magnitude of change
                if changes_data:
                    changes_df = pd.DataFrame(changes_data)
                    
                    # Add filter options
                    filter_col1, filter_col2, filter_col3 = st.columns(3)
                    
                    with filter_col1:
                        sort_by = st.selectbox(
                            "Sort by",
                            ["Change (Abs)", "Change (%)", "Value (High to Low)"],
                            key="changes_sort"
                        )
                    
                    with filter_col2:
                        show_only = st.selectbox(
                            "Show",
                            ["All", "Positive Changes", "Negative Changes"],
                            key="changes_filter"
                        )
                    
                    with filter_col3:
                        search_inv = st.text_input("🔍 Search", key="changes_search")
                    
                    # Apply sorting
                    if sort_by == "Change (Abs)":
                        changes_df = changes_df.sort_values("_sort_value", ascending=False)
                    elif sort_by == "Change (%)":
                        changes_df = changes_df.sort_values("_change_pct", ascending=False)
                    else:  # Value (High to Low)
                        changes_df = changes_df.sort_values("Current Value (USD)", ascending=False, key=lambda x: x.str.replace('$', '').str.replace(',', '').astype(float))
                    
                    # Apply filtering
                    if show_only == "Positive Changes":
                        changes_df = changes_df[changes_df["_change_pct"] > 0]
                    elif show_only == "Negative Changes":
                        changes_df = changes_df[changes_df["_change_pct"] < 0]
                    
                    # Apply search
                    if search_inv:
                        changes_df = changes_df[changes_df["Investment"].str.contains(search_inv, case=False)]
                    
                    # Apply sorting and filtering to the DataFrame
                    # (Your existing code for this)

                    # Final step: Before displaying, create a display copy that keeps the sorting columns
                    # but renames them to hidden versions that can be used for sorting
                    display_df = changes_df.rename(columns={
                        "Current Value Num": "_Current Value Num", 
                        "Change Num": "_Change Num", 
                        "Change Pct Num": "_Change Pct Num"
                    })

                    # Display the filtered and sorted dataframe
                    # Remove the problematic column configuration options
                    st.dataframe(
                        display_df,
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
        st.markdown("---")
        # Charts row with improved visualizations
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Asset Allocation")
            
            # Group by investment and calculate percentages
            allocation = latest_df.groupby('Investment')['ValueUSD'].sum().reset_index()
            allocation['Percentage'] = (allocation['ValueUSD'] / allocation['ValueUSD'].sum() * 100).round(2)
            
            # Add category information
            allocation['Category'] = allocation['Investment'].map(INVESTMENT_CATEGORIES)
            
            # Allow filtering by threshold percentage
            min_pct = st.slider(
                "Minimum percentage to display (smaller holdings grouped as 'Other')", 
                min_value=0.0, 
                max_value=10.0, 
                value=1.0,
                step=0.5,
                key="pie_threshold"
            )
            
            # Group small investments as "Other"
            if min_pct > 0:
                small_investments = allocation[allocation['Percentage'] < min_pct]
                if not small_investments.empty:
                    other_row = {
                        'Investment': 'Other',
                        'ValueUSD': small_investments['ValueUSD'].sum(),
                        'Percentage': small_investments['Percentage'].sum(),
                        'Category': 'Other'
                    }
                    allocation = allocation[allocation['Percentage'] >= min_pct]
                    allocation = pd.concat([allocation, pd.DataFrame([other_row])], ignore_index=True)
            # Add checkbox to control pie explosion
            exploded_view = st.checkbox("Show exploded view", value=False, key="exploded_pie")

            # Create improved pie chart with animation
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
            
            # Enhanced styling for interactive pie chart
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12,
                pull=[0.15 if exploded_view else 0.05] * len(allocation),  # More pull when exploded view is active
                marker=dict(line=dict(color='#1e1e2e', width=1)),
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.2f}%<extra></extra>'
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
                # Removed the non-functioning updatemenus section
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with chart_col2:
            st.subheader("Currency Breakdown")
            
            # Group by currency
            currency_breakdown = latest_df.groupby('Currency')['ValueUSD'].sum().reset_index()
            currency_breakdown['Percentage'] = (currency_breakdown['ValueUSD'] / currency_breakdown['ValueUSD'].sum() * 100).round(2)
            
            # Add visualization options
            chart_type = st.radio(
                "Chart Type",
                ["Bar Chart", "Pie Chart", "Treemap"],
                horizontal=True,
                key="currency_chart_type"
            )
            
            if chart_type == "Bar Chart":
                # Create enhanced bar chart with animations
                fig = px.bar(
                    currency_breakdown.sort_values('ValueUSD', ascending=False),
                    x='Currency',
                    y='ValueUSD',
                    text='Percentage',
                    color='Currency',
                    labels={'ValueUSD': 'Value (USD)', 'Currency': 'Currency'},
                    title='',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f}%', 
                    textposition='outside',
                    marker_line_color='rgba(255,255,255,0.2)',
                    marker_line_width=1,
                    hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
                )
                
                # Add animation effect
                for i, bar in enumerate(fig.data):
                    bar.width = 0.6  # Make bars thinner for better appearance
                
                # Add drop shadow for better visual effect
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
                    ),
                    # Animation setup
                    updatemenus=[{
                        'type': 'buttons',
                        'showactive': False,
                        'buttons': [
                            {
                                'method': 'animate',
                                'label': 'Reset View',
                                'args': [None]
                            }
                        ],
                        'x': 0.05,
                        'y': 1.05,
                    }]
                )
                
            elif chart_type == "Pie Chart":
                # Create pie chart for currencies
                fig = px.pie(
                    currency_breakdown,
                    values='ValueUSD',
                    names='Currency',
                    hover_data=['Percentage'],
                    title=''
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#1e1e2e', width=1)),
                    hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
                )
                
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
            else:  # Treemap
                # Create treemap for currencies
                fig = px.treemap(
                    currency_breakdown,
                    path=['Currency'],
                    values='ValueUSD',
                    color='Currency',
                    hover_data=['Percentage'],
                    title=''
                )
                
                fig.update_traces(
                    textinfo='label+value+percent root',
                    hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
                )
                
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})# Bottom charts row with enhanced category visualization
        st.subheader("Category Breakdown")
        
        # Group by category
        category_data = latest_df.copy()
        category_data['Category'] = category_data['Investment'].map(INVESTMENT_CATEGORIES)
        category_breakdown = category_data.groupby('Category')['ValueUSD'].sum().reset_index()
        category_breakdown['Percentage'] = (category_breakdown['ValueUSD'] / category_breakdown['ValueUSD'].sum() * 100).round(2)
        
        # Add visualization options
        category_chart_type = st.radio(
            "Visualization Type",
            ["Horizontal Bar", "Vertical Bar", "Treemap", "Sunburst"],
            horizontal=True,
            key="category_chart_type"
        )
        
        if category_chart_type == "Horizontal Bar":
            # Create horizontal bar chart with improved styling
            fig = px.bar(
                category_breakdown.sort_values('ValueUSD', ascending=True),
                y='Category',
                x='ValueUSD',
                text='Percentage',
                color='Category',
                orientation='h',
                labels={'ValueUSD': 'Value (USD)', 'Category': 'Category'},
                title=''
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='inside',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1,
                hovertemplate='<b>%{y}</b><br>Value: $%{x:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
            )
            
            # Animation settings
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
                ),
                # Add transition effect
                transition_duration=500
            )
            
        elif category_chart_type == "Vertical Bar":
            # Create vertical bar chart for categories
            fig = px.bar(
                category_breakdown.sort_values('ValueUSD', ascending=False),
                x='Category',
                y='ValueUSD',
                text='Percentage',
                color='Category',
                labels={'ValueUSD': 'Value (USD)', 'Category': 'Category'},
                title=''
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='outside',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1,
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
            )
            
            fig.update_layout(
                height=350,
                xaxis_title="Category",
                yaxis_title="Value (USD)",
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
                ),
                # Add animation effect
                transition_duration=500
            )
            
        elif category_chart_type == "Treemap":
            # Create treemap for categories
            fig = px.treemap(
                category_breakdown,
                path=['Category'],
                values='ValueUSD',
                color='Category',
                hover_data=['Percentage'],
                title=''
            )
            
            fig.update_traces(
                textinfo='label+value+percent',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
            )
            
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
        else:  # Sunburst
            # Create a more detailed dataset for the sunburst chart
            sunburst_data = latest_df.copy()
            sunburst_data['Category'] = sunburst_data['Investment'].map(INVESTMENT_CATEGORIES)
            
            # Create sunburst chart for category > investment hierarchy
            fig = px.sunburst(
                sunburst_data,
                path=['Category', 'Investment'],
                values='ValueUSD',
                color='Category',
                hover_data=['Currency', 'Value'],
                title=''
            )
            
            fig.update_traces(
                textinfo='label+percent entry',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Currency: %{customdata[0]}<br>Original Value: %{customdata[1]:,.2f}<extra></extra>'
            )
            
            fig.update_layout(
                height=500,  # Taller for better visibility
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    else:
        st.info("No data available. Please add investment entries.")
    st.markdown('</div>', unsafe_allow_html=True)
with tab2:
    # Performance tab with enhanced animations and interactivity;
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
        
        # Calculate preset date ranges
        now = datetime.now().date()
        if preset_ranges == "1 Month":
            preset_start = (now - timedelta(days=30))
            preset_end = now
        elif preset_ranges == "3 Months":
            preset_start = (now - timedelta(days=90))
            preset_end = now
        elif preset_ranges == "6 Months":
            preset_start = (now - timedelta(days=180))
            preset_end = now
        elif preset_ranges == "1 Year":
            preset_start = (now - timedelta(days=365))
            preset_end = now
        elif preset_ranges == "YTD":
            preset_start = datetime(now.year, 1, 1).date()
            preset_end = now
        elif preset_ranges == "All Time":
            preset_start = earliest_date
            preset_end = latest_date
        else:  # Custom
            preset_start = earliest_date
            preset_end = latest_date
        
        # Show date pickers only if Custom is selected
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
            # Use preset dates
            perf_start = preset_start
            perf_end = preset_end
            st.info(f"Date range: {perf_start.strftime('%Y-%m-%d')} to {perf_end.strftime('%Y-%m-%d')}")
        
        # Convert to datetime for filtering
        perf_start_dt = pd.Timestamp(perf_start)
        perf_end_dt = pd.Timestamp(perf_end)
        
        # Get performance data with loading animation
        with st.spinner("Calculating performance data..."):
            performance_data = get_historical_performance(df, perf_start_dt, perf_end_dt)
            time.sleep(0.5)  # Add slight delay for animationif not performance_data.empty:
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
                
            # Add annotations if requested;
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

            # Enhanced styling for all chart types
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Value (USD)",
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
                ),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})# Investment performance comparison with enhanced UI
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
                            trace.mode = 'lines+markers'# Update styling with enhanced interactivity
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

                    # Calculate and display performance metrics with enhanced styling
                    st.subheader("Performance Metrics") ;

                    # Option to show detailed analysis;
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
                    metrics_df = pd.DataFrame(metrics_data)

                    # Add a column for highlighting the reference investment;
                    metrics_df['_style'] = metrics_df['Is Reference'].apply(
                        lambda x: 'background-color: rgba(78, 141, 245, 0.2)' if x else ''
                    )
                    
                    # Format for display
                    display_df = metrics_df.drop(columns=['Is Reference', '_style']).copy()
                    display_df['Start Value'] = display_df['Start Value'].map('${:,.2f}'.format)
                    display_df['End Value'] = display_df['End Value'].map('${:,.2f}'.format)
                    display_df['Absolute Change %'] = display_df['Absolute Change %'].map('{:+.2f}%'.format)
                    display_df['Relative Change %'] = display_df['Relative Change %'].map('{:+.2f}%'.format)
                    
                    # Add detailed columns if present;
                    if show_detailed and 'CAGR' in display_df.columns:
                        display_df['CAGR'] = display_df['CAGR'].map('{:+.2f}%'.format)
                        display_df['Volatility'] = display_df['Volatility'].map('{:.2f}%'.format)
                        display_df['Days'] = display_df['Days'].astype(int)
                    
                    # Display metrics with enhanced styling
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
                        
                        bar_fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=50, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            xaxis_title=metric_to_plot,
                            yaxis_title="",
                            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
                        )
                        
                        st.plotly_chart(bar_fig, use_container_width=True);
                else:
                    st.warning("Insufficient data for comparative analysis. Ensure the reference investment has data for the selected date range.")
            else:
                st.info("Select a reference investment and comparison investments to view relative performance.")
        else:
            st.warning("No data available for the selected date range.")
    else:
        st.info("No data available. Please add investment entries.")
    st.markdown('</div>', unsafe_allow_html=True)
    
with tab3:
    # Data tab with enhanced filtering and visualization

    st.markdown('<div class="animate-in">', unsafe_allow_html=True) ;
    st.header("Investment Data")
    
    if not df.empty:
        # Enhanced date filter with preset options
        st.subheader("Date Filter")
        
        date_filter_type = st.radio(
            "Filter Type",
            ["Range", "Specific Date"],
            horizontal=True,
            key="date_filter_type"
        )
        
        if date_filter_type == "Range":
            # Date range selection with presets
            date_preset = st.selectbox(
                "Preset Ranges",
                ["Custom", "Last 30 Days", "Last 90 Days", "Last 180 Days", "This Year", "Last Year", "All Time"],
                key="date_preset"
            )
            
            if date_preset == "Custom":
                # Custom date range
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
            else:
                # Calculate preset ranges
                if date_preset == "Last 30 Days":
                    start_date = latest_date - timedelta(days=30)
                    end_date = latest_date
                elif date_preset == "Last 90 Days":
                    start_date = latest_date - timedelta(days=90)
                    end_date = latest_date
                elif date_preset == "Last 180 Days":
                    start_date = latest_date - timedelta(days=180)
                    end_date = latest_date
                elif date_preset == "This Year":
                    start_date = datetime(latest_date.year, 1, 1).date()
                    end_date = latest_date
                elif date_preset == "Last Year":
                    start_date = datetime(latest_date.year - 1, 1, 1).date()
                    end_date = datetime(latest_date.year - 1, 12, 31).date()
                else:  # All Time
                    start_date = earliest_date
                    end_date = latest_date
                
                st.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        else:
            # Specific date selection
            data_cols = st.columns([1, 3])
            with data_cols[0]:
                specific_date_type = st.radio(
                    "Date Selection",
                    ["Specific Date", "Latest Available"],
                    key="specific_date_type"
                )
            
            with data_cols[1]:
                if specific_date_type == "Specific Date":
                    specific_date = st.date_input(
                        "Select Date",
                        value=latest_date,
                        min_value=earliest_date,
                        max_value=latest_date,
                        key="specific_date"
                    )
                    start_date = end_date = specific_date
                else:
                    start_date = end_date = latest_date
                    st.info(f"Using latest date: {latest_date.strftime('%Y-%m-%d')}")
        
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
            filtered_df = df.copy()
            
            # Date filter
            filtered_df = filtered_df[
                (filtered_df['Date'] >= pd.Timestamp(start_date)) &
                (filtered_df['Date'] <= pd.Timestamp(end_date))
            ]
            
            # Investment filter
            if filter_mode == "All" or "All" in investment_filter:
                pass  # No filtering needed
            else:
                filtered_df = filtered_df[filtered_df['Investment'].isin(investment_filter)]
            
            # Sort by date descending
            filtered_df = filtered_df.sort_values('Date', ascending=False)
            
            # Save to session state for potential export
            st.session_state.filtered_df = filtered_df
            
            # Add a small delay for animation effect
            time.sleep(0.3)
        
        # Display data with enhanced controls
        st.subheader("Investment Data")
        
        # Add search functionality
        search_query = st.text_input("🔍 Search in data", key="data_search")
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
                "Sort by",
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
            # For formatted columns, use the numeric columns for sorting
            sorted_df = filtered_df.sort_values('Current Value Num', ascending=(sort_order == "Ascending"))
        elif sort_column == "Change (USD)":
            sorted_df = filtered_df.sort_values('Change Num', ascending=(sort_order == "Ascending"))
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
        
        # Determine what to export
        if export_scope == "Filtered Data":
            export_df = filtered_df
        elif export_scope == "Current Page":
            export_df = display_df
        else:  # All Data
            export_df = df
        
        # Create export button based on format
        if export_format == "CSV":
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Data",
                data=csv,
                file_name="investment_data_export.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            # For Excel, we need to use BytesIO
            from io import BytesIO
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, sheet_name='Investment Data', index=False)
                
                # Auto-adjust column width
                worksheet = writer.sheets['Investment Data']
                for i, col in enumerate(export_df.columns):
                    column_len = max(export_df[col].astype(str).str.len().max(), len(col) + 2)
                    worksheet.set_column(i, i, column_len)
            
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="investment_data_export.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:  # JSON
            json_str = export_df.to_json(orient='records', date_format='iso')
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="investment_data_export.json",
                mime="application/json"
            )
    else:
        st.info("No data available. Please add investment entries.")
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
                
                # Create backup button based on format
                if backup_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Export All Data",
                        data=csv,
                        file_name=f"{backup_name}.csv",
                        mime="text/csv",
                        key="export_all"
                    )
                elif backup_format == "Excel":
                    # For Excel, we need to use BytesIO
                    from io import BytesIO
                    
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Investment Data', index=False)
                        
                        # Auto-adjust column width
                        worksheet = writer.sheets['Investment Data']
                        for i, col in enumerate(df.columns):
                            column_len = max(df[col].astype(str).str.len().max(), len(col) + 2)
                            worksheet.set_column(i, i, column_len)
                    
                    excel_data = buffer.getvalue()
                    
                    st.download_button(
                        label="💾 Export All Data",
                        data=excel_data,
                        file_name=f"{backup_name}.xlsx",
                        mime="application/vnd.ms-excel",
                        key="export_all_excel"
                    )
                else:  # JSON
                    json_str = df.to_json(orient='records', date_format='iso')
                    st.download_button(
                        label="💾 Export All Data",
                        data=json_str,
                        file_name=f"{backup_name}.json",
                        mime="application/json",
                        key="export_all_json"
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
                    
                    if st.button("✅ Confirm Import", key="confirm_import"):
                        with st.spinner("Processing import..."):
                            progress_bar = st.progress(0)
                            for i in range(101):
                                progress_bar.progress(i)
                                time.sleep(0.01)
                        
                            if import_action == "Replace all data":
                                save_data(import_df)
                                st.success("Data replaced successfully!")
                                st.session_state.show_success = True
                                st.rerun()
                            elif import_action == "Append to existing data":
                                combined_df = pd.concat([df, import_df], ignore_index=True)
                                # Remove potential duplicates
                                combined_df = combined_df.drop_duplicates(
                                    subset=['Date', 'Investment', 'Currency', 'Value']
                                )
                                save_data(combined_df)
                                st.success("Data appended successfully!")
                                st.session_state.show_success = True
                                st.rerun()
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
                                st.success("Data updated successfully!")
                                st.session_state.show_success = True
                                st.rerun()
                except Exception as e:
                    st.error(f"Error importing data: {e}")
                
    with settings_tab2:
        st.subheader("Investment Accounts and Categories")
        
        # Display configured accounts with improved styling
        accounts_df = pd.DataFrame({
            'Investment': list(INVESTMENT_ACCOUNTS.keys()),
            'Currency': list(INVESTMENT_ACCOUNTS.values()),
            'Category': [INVESTMENT_CATEGORIES.get(inv, 'Uncategorized') for inv in INVESTMENT_ACCOUNTS.keys()]
        })
        
        # Allow filtering
        filter_accounts = st.text_input("🔍 Filter accounts", key="account_filter")
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
        
        st.info(
            "To add or modify investment accounts and categories, update the INVESTMENT_ACCOUNTS "
            "and INVESTMENT_CATEGORIES dictionaries in config.py."
        )
        
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
            if st.button("🔄 Force Refresh Exchange Rates", key="force_refresh"):
                with st.spinner("Refreshing exchange rates..."):
                    refresh_rates()
                    time.sleep(0.5)  # Wait for refresh to complete
                    st.success("Exchange rates refreshed successfully!")
                    st.rerun()
        else:
            st.warning("No exchange rates found. Click refresh to fetch current rates.")
            
            if st.button("🔄 Fetch Exchange Rates", key="fetch_rates"):
                with st.spinner("Fetching exchange rates..."):
                    refresh_rates()
                    time.sleep(0.5)  # Wait for refresh to complete
                    st.success("Exchange rates fetched successfully!")
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
