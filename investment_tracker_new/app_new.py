
# app_new.py
import streamlit as st
import pandas as pd
from datetime import datetime
import data_handler_new as db
import dashboard_components_new as dc
import performance_components_new as pc
import data_components_new as dac
import settings_components_new as sc
import utils_new as ut
import benchmark_components_new as bc
from config import INVESTMENT_CATEGORIES

def main():
    st.set_page_config(
        page_title="Modern Investment Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Theme toggle
    theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
    ut.apply_theme(theme)

    st.title("Modern Investment and Expense Tracker")

    # Initialize the database
    db.init_database()

    # Sidebar for data entry
    st.sidebar.header("Add New Entry")
    date = st.sidebar.date_input("Date", datetime.today())
    investment = st.sidebar.text_input("Investment")
    value = st.sidebar.number_input("Value")
    currency = st.sidebar.text_input("Currency")

    if st.sidebar.button("Add Entry"):
        if investment and value and currency:
            db.add_entry(date, investment, value, currency)
            st.sidebar.success("Entry added successfully!")
        else:
            st.sidebar.error("Please fill in all fields.")

    # Main area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Performance", "Benchmark", "Data", "Settings"])
    df = db.load_data()

    with tab1:
        dc.create_dashboard_header(df)
        dc.create_investment_change_table(df)
        dc.create_portfolio_performance_chart(df)
        
        col1, col2 = st.columns(2)
        with col1:
            dc.create_asset_allocation_chart(df)
            dc.create_currency_breakdown_chart(df)
        with col2:
            dc.create_category_breakdown_chart(df, INVESTMENT_CATEGORIES)
            
    with tab2:
        start_date, end_date = pc.create_performance_date_filter(df)
        pc.create_portfolio_value_chart(df, start_date, end_date)
        pc.create_investment_comparison_chart(df, start_date, end_date)
        pc.create_performance_metrics_table(df, start_date, end_date)

    with tab3:
        st.header("Benchmark Comparison")
        benchmark = st.selectbox("Select Benchmark", ["^GSPC", "^IXIC", "^DJI"])
        start_date, end_date = pc.create_performance_date_filter(df)
        bc.create_benchmark_comparison_chart(df, benchmark, start_date, end_date)

    with tab4:
        data_start_date, data_end_date, selected_investments = dac.create_data_filters(df)
        dac.create_data_table(df, data_start_date, data_end_date, selected_investments)

    with tab5:
        sc.create_data_management_section()
        sc.create_import_section()
        sc.create_investment_management_section()
        sc.create_exchange_rate_section()

if __name__ == "__main__":
    main()
