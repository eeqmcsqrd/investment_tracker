# import_csv.py
import pandas as pd
import streamlit as st
import datetime
from config import INVESTMENT_ACCOUNTS

def import_csv_file(uploaded_file):
    """
    Import data from a CSV file. Handles different CSV formats.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Processed DataFrame ready for the app
    """
    try:
        # First try to read with headers
        df = pd.read_csv(uploaded_file)
        
        # Check if this is our expected app format
        expected_columns = set(['Date', 'Investment', 'Currency', 'Value'])
        
        # If not all expected columns are present, try different format
        if not expected_columns.issubset(set(df.columns)):
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Try loading without headers
            df = pd.read_csv(uploaded_file, header=None)
            
            # If it has 4 columns, assume it's in the Date,Investment,Currency,Value format
            if df.shape[1] == 4:
                df.columns = ['Date', 'Investment', 'Currency', 'Value']
            elif df.shape[1] == 2:
                # It might be a simpler format with just investment name and value
                date_today = datetime.datetime.now().strftime('%Y-%m-%d')
                
                # Assume column 0 is Investment and column 1 is Value
                df.columns = ['Investment', 'Value']
                
                # Add Date and determine Currency
                df['Date'] = date_today
                
                # Try to determine currency from investment name
                def get_currency(investment):
                    investment_str = str(investment)
                    return INVESTMENT_ACCOUNTS.get(investment_str, 'USD')
                
                df['Currency'] = df['Investment'].apply(get_currency)
                
                # Reorder columns to match the expected format
                df = df[['Date', 'Investment', 'Currency', 'Value']]
            else:
                st.error(f"Unrecognized CSV format with {df.shape[1]} columns. Expected 2 or 4 columns.")
                return None
        
        # Process data types
        try:
            # Try to convert Date column
            df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
            
            # Fill missing dates with today
            if df['Date'].isna().any():
                today = pd.Timestamp(datetime.datetime.now().date())
                df['Date'] = df['Date'].fillna(today)
                
            # Ensure Investment is string
            df['Investment'] = df['Investment'].astype(str)
            
            # Ensure Currency is string and defaulted if missing
            df['Currency'] = df['Currency'].astype(str)
            
            # Fix any missing currencies by looking up in INVESTMENT_ACCOUNTS
            for idx, row in df.iterrows():
                if row['Currency'] == 'nan' or pd.isna(row['Currency']):
                    inv = str(row['Investment'])
                    df.at[idx, 'Currency'] = INVESTMENT_ACCOUNTS.get(inv, 'USD')
            
            # Ensure Value is numeric
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            df = df.dropna(subset=['Value'])
            
            return df
            
        except Exception as e:
            st.error(f"Error processing data types: {e}")
            return None
            
    except Exception as e:
        st.error(f"Error importing CSV: {e}")
        return None