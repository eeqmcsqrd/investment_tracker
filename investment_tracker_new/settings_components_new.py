


# settings_components_new.py

import streamlit as st

import pandas as pd

import data_handler_new as db

from config import INVESTMENT_ACCOUNTS, INVESTMENT_CATEGORIES, write_config



def create_data_management_section():

    """Creates the data management section in the settings tab.""" 

    st.header("Data Management")



    # Backup

    st.subheader("Backup Data")

    if st.button("Backup to CSV"):

        df = db.load_data()

        csv = df.to_csv(index=False)

        st.download_button("Download Backup", csv, "investment_data_backup.csv", "text/csv")



    # Restore

    st.subheader("Restore Data")

    uploaded_file = st.file_uploader("Choose a file to restore from")

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        if st.button("Restore"):

            db.save_data(df)

            st.success("Data restored successfully!")



def create_import_section():

    """Creates the import section in the settings tab."""

    st.header("Import Data")

    uploaded_file = st.file_uploader("Choose a file to import from", key="import_file")

    if uploaded_file is not None:

        file_extension = uploaded_file.name.split('.')[-1]

        if file_extension == 'csv':

            df = pd.read_csv(uploaded_file)

        elif file_extension in ['xls', 'xlsx']:

            df = pd.read_excel(uploaded_file)

        elif file_extension == 'json':

            df = pd.read_json(uploaded_file)

        else:

            st.error("Unsupported file format")

            return



        if st.button("Import"):

            db.add_bulk_entries(df.to_dict('records'))

            st.success("Data imported successfully!")



def create_investment_management_section():

    """Creates the investment management section in the settings tab."""

    st.header("Investment Management")



    st.subheader("Accounts")

    for investment, currency in INVESTMENT_ACCOUNTS.items():

        st.write(f"{investment}: {currency}")



    st.subheader("Categories")

    for investment, category in INVESTMENT_CATEGORIES.items():

        st.write(f"{investment}: {category}")



    st.subheader("Add/Edit Investment")

    investment_name = st.text_input("Investment Name")

    currency = st.text_input("Currency")

    category = st.text_input("Category")

    if st.button("Save Investment"):

        INVESTMENT_ACCOUNTS[investment_name] = currency

        INVESTMENT_CATEGORIES[investment_name] = category

        # This is a simplified example. In a real app, you'd want to

        # write these back to the config file.

        st.success(f"Investment {investment_name} saved!")



def create_exchange_rate_section():

    """Creates the exchange rate section in the settings tab."""

    st.header("Exchange Rates")

    st.write("Exchange rate management will be implemented here.")


