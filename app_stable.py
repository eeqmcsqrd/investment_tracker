# app_stable.py - Stable version using simple components from app_simple but auth from main app

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import traceback

# Initialize database
try:
    import init_database
    init_database.init_database_from_snapshot()
except Exception as e:
    st.error(f"DB Init Error: {e}")

# Authentication
try:
    import auth_wrapper
    if not auth_wrapper.check_password():
        st.stop()
    auth_wrapper.add_logout_button()
except:
    pass

# Page config
st.set_page_config(
    page_title="Investment Tracker",
    page_icon="💰",
    layout="wide"
)

# Load data
try:
    from data_handler_db import load_data
    from currency_service import get_conversion_rate
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please add investment data.")
        st.stop()
    
    # Add ValueUSD
    if 'ValueUSD' not in df.columns:
        df['ValueUSD'] = df.apply(lambda row: row['Value'] * get_conversion_rate(row['Currency']), axis=1)
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Title
st.title("💰 Investment Tracker")

# Sidebar - Time Range Selection (using session state like main app)
if 'start_date' not in st.session_state:
    st.session_state.start_date = df['Date'].min()
if 'end_date' not in st.session_state:
    st.session_state.end_date = df['Date'].max()

with st.sidebar:
    st.header("📅 Date Range")
    
    time_option = st.selectbox(
        "Select Period:",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All Time"],
        index=1  # Default to 1 Month
    )
    
    # Calculate date range based on selection
    end_date = df['Date'].max()
    if time_option == "1 Week":
        start_date = end_date - timedelta(days=7)
    elif time_option == "1 Month":
        start_date = end_date - timedelta(days=30)
    elif time_option == "3 Months":
        start_date = end_date - timedelta(days=90)
    elif time_option == "6 Months":
        start_date = end_date - timedelta(days=180)
    elif time_option == "1 Year":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = df['Date'].min()
    
    # Update session state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    
    st.success(f"📊 {time_option}")
    st.info(f"From: {start_date.date()}\nTo: {end_date.date()}")

    # Data Entry Section
    st.divider()
    st.subheader("💾 Update Investment")

    with st.form("add_entry_form", clear_on_submit=True):
        # Load config
        from config import INVESTMENT_ACCOUNTS

        # Get list of investments
        investments = sorted(INVESTMENT_ACCOUNTS.keys())

        entry_date = st.date_input("Date", value=datetime.now().date())
        investment = st.selectbox("Investment", investments)
        value = st.number_input("Value", min_value=0.0, value=0.0, step=100.0)

        # Get currency for selected investment
        currency = INVESTMENT_ACCOUNTS.get(investment, "USD")
        st.caption(f"Currency: {currency}")

        submitted = st.form_submit_button("💾 Add Entry", use_container_width=True)

        if submitted:
            if value > 0:
                try:
                    from data_handler_db import add_entry_db

                    # Add entry (function looks up currency automatically)
                    add_entry_db(entry_date, investment, value)

                    st.success(f"✅ Added {investment}: {currency} {value:,.2f}")
                    st.balloons()

                    # Wait a moment then rerun to refresh data
                    import time
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error adding entry: {e}")
            else:
                st.warning("⚠️ Please enter a value greater than 0")

# Filter data
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

st.info(f"📊 Showing {len(filtered_df)} records from {start_date.date()} to {end_date.date()}")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Data", "⚙️ Settings"])

with tab1:
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_value = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]['ValueUSD'].sum()
        st.metric("💵 Current Value", f"${current_value:,.2f}")
    
    with col2:
        start_value = filtered_df[filtered_df['Date'] == filtered_df['Date'].min()]['ValueUSD'].sum()
        change = current_value - start_value
        change_pct = (change / start_value * 100) if start_value > 0 else 0
        st.metric("📈 Change", f"${change:,.2f}", f"{change_pct:+.2f}%")
    
    with col3:
        num_investments = filtered_df['Investment'].nunique()
        st.metric("🏦 Investments", num_investments)
    
    # Portfolio Performance Chart
    st.subheader("📊 Portfolio Performance")
    try:
        from utils import calculate_smart_date_format

        daily_totals = filtered_df.groupby('Date')['ValueUSD'].sum().reset_index()
        fig = px.line(daily_totals, x='Date', y='ValueUSD',
                      title=f'Portfolio Value - {time_option}')

        # Calculate smart date formatting
        num_days = (daily_totals['Date'].max() - daily_totals['Date'].min()).days
        date_settings = calculate_smart_date_format(num_days)

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Value (USD)",
            hovermode='x unified',
            height=500,
            margin=dict(l=20, r=20, t=40, b=100),
            xaxis=dict(
                tickangle=-45,
                automargin=True,
                tickfont=dict(size=10),
                **date_settings
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")
    
    # Investment Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏦 Investment Breakdown")
        try:
            latest = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
            breakdown = latest.groupby('Investment')['ValueUSD'].sum().sort_values(ascending=False)
            
            fig = px.pie(values=breakdown.values, names=breakdown.index,
                         title='Current Allocation')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Breakdown error: {e}")
    
    with col2:
        st.subheader("📈 Top Investments")
        try:
            latest = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
            top = latest.groupby('Investment')['ValueUSD'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(x=top.values, y=top.index, orientation='h',
                         labels={'x': 'Value (USD)', 'y': 'Investment'},
                         title='Top 10 by Value')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Top investments error: {e}")

with tab2:
    st.header("📋 Investment Data")
    
    # Show recent data
    st.dataframe(
        filtered_df.sort_values('Date', ascending=False).head(100),
        use_container_width=True,
        hide_index=True
    )
    
    # Summary stats
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Date Range", f"{(filtered_df['Date'].max() - filtered_df['Date'].min()).days} days")
    with col3:
        st.metric("Avg Daily Value", f"${filtered_df.groupby('Date')['ValueUSD'].sum().mean():,.2f}")
    with col4:
        st.metric("Unique Investments", filtered_df['Investment'].nunique())

with tab3:
    st.header("⚙️ Settings")

    # Bulk Update Section
    st.subheader("📝 Bulk Update All Investments")
    st.info("Update all investment values for a specific date")

    with st.form("bulk_update_form"):
        from config import INVESTMENT_ACCOUNTS

        bulk_date = st.date_input("Update Date", value=datetime.now().date())

        st.write("**Enter new values for each investment:**")

        # Get most recent values as defaults
        latest_values = {}
        if not df.empty:
            latest_data = df[df['Date'] == df['Date'].max()]
            for inv in INVESTMENT_ACCOUNTS.keys():
                inv_data = latest_data[latest_data['Investment'] == inv]
                if not inv_data.empty:
                    latest_values[inv] = float(inv_data['Value'].iloc[0])
                else:
                    latest_values[inv] = 0.0

        # Create input fields for each investment
        values_dict = {}
        for investment in sorted(INVESTMENT_ACCOUNTS.keys()):
            currency = INVESTMENT_ACCOUNTS[investment]
            default_val = latest_values.get(investment, 0.0)

            col1, col2 = st.columns([3, 1])
            with col1:
                values_dict[investment] = st.number_input(
                    f"{investment}",
                    min_value=0.0,
                    value=default_val,
                    step=100.0,
                    key=f"bulk_{investment}"
                )
            with col2:
                st.caption(currency)

        bulk_submitted = st.form_submit_button("💾 Update All", use_container_width=True)

        if bulk_submitted:
            try:
                from data_handler_db import add_entry_db

                added_count = 0
                for investment, value in values_dict.items():
                    if value > 0:  # Only add non-zero values
                        add_entry_db(bulk_date, investment, value)
                        added_count += 1

                st.success(f"✅ Updated {added_count} investments for {bulk_date}")
                st.balloons()

                import time
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during bulk update: {e}")
                st.code(traceback.format_exc())

    st.divider()

    # Data Management
    st.subheader("🔧 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    with col2:
        from currency_service import refresh_rates
        if st.button("💱 Refresh Exchange Rates", use_container_width=True):
            try:
                refresh_rates()
                st.success("✅ Exchange rates refreshed!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # Database Sync
    st.subheader("🔄 Database Synchronization")
    st.info("💡 Keep your laptop and cloud databases in sync")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**📥 Download Database**")
        st.caption("Download the current cloud database to your laptop")

        # Export database as downloadable file
        try:
            import sqlite3
            import io

            # Read database file
            with open('investment_data.db', 'rb') as f:
                db_bytes = f.read()

            # Create download button
            st.download_button(
                label="⬇️ Download Database (.db)",
                data=db_bytes,
                file_name=f"investment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/octet-stream",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error preparing download: {e}")

    with col2:
        st.write("**📤 Upload Database**")
        st.caption("Upload your laptop database to replace cloud database")

        uploaded_file = st.file_uploader(
            "Choose database file",
            type=['db'],
            key="db_upload"
        )

        if uploaded_file is not None:
            if st.button("⬆️ Replace Cloud Database", use_container_width=True, type="primary"):
                try:
                    # Backup current database
                    import shutil
                    import os
                    backup_name = f"investment_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2('investment_data.db', backup_name)
                    st.info(f"✅ Backup created: {backup_name}")

                    # Write uploaded file
                    with open('investment_data.db', 'wb') as f:
                        f.write(uploaded_file.getvalue())

                    st.success("✅ Database replaced successfully!")
                    st.balloons()

                    import time
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error uploading database: {e}")
                    st.code(traceback.format_exc())

    st.divider()

    # Export to CSV/JSON for backup
    st.subheader("💾 Export Data (Backup)")

    col1, col2 = st.columns(2)

    with col1:
        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"investment_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # Export to JSON
        json_str = df.to_json(orient='records', date_format='iso', indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_str,
            file_name=f"investment_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.divider()

    # App Info
    st.subheader("ℹ️ App Information")
    st.write(f"**Total Records in Database:** {len(df)}")
    st.write(f"**Date Range:** {df['Date'].min().date()} to {df['Date'].max().date()}")
    st.write(f"**Number of Investments:** {df['Investment'].nunique()}")

st.success("✅ App loaded successfully!")
