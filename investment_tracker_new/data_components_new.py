
# data_components_new.py
import streamlit as st
import pandas as pd

def create_data_filters(df):
    """Creates the filters for the data tab."""
    st.header("Filters")
    
    if not df.empty:
        # Date filter
        min_date = df['date'].min()
        max_date = df['date'].max()
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

        # Investment filter
        investments = df['investment'].unique()
        selected_investments = st.multiselect("Investments", investments, default=investments)

        return start_date, end_date, selected_investments
    else:
        return None, None, None

def create_data_table(df, start_date, end_date, selected_investments):
    """Creates the data table with sorting and export options."""
    st.header("Data")
    
    if not df.empty and start_date and end_date and selected_investments:
        mask = (
            (df['date'] >= pd.to_datetime(start_date)) & 
            (df['date'] <= pd.to_datetime(end_date)) & 
            (df['investment'].isin(selected_investments))
        )
        filtered_df = df.loc[mask]

        # Sorting
        sort_column = st.selectbox("Sort by", filtered_df.columns)
        sort_order = st.radio("Sort order", ["ASC", "DESC"])
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == "ASC"))

        st.dataframe(sorted_df)

        # Export
        csv = sorted_df.to_csv(index=False)
        st.download_button("Download as CSV", csv, "investment_data.csv", "text/csv")
