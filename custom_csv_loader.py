# custom_csv_loader.py
import pandas as pd
import os
from datetime import datetime

def load_custom_csv(filepath):
    """
    Load and transform a CSV file with the format:
    Date, Investment, Currency, Value
    where each row is a single entry.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: Transformed DataFrame in the format expected by the app
    """
    try:
        # Read the CSV file without assuming header
        df = pd.read_csv(filepath, header=None)
        
        # Check if this is the expected format (4 columns)
        if df.shape[1] == 4:
            # Assign column names
            df.columns = ['Date', 'Investment', 'Currency', 'Value']
            
            # Ensure types
            df['Investment'] = df['Investment'].astype(str)
            df['Currency'] = df['Currency'].astype(str)
            
            # Try to convert the Date column to datetime
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)
            except Exception as e:
                print(f"Warning: Date conversion error: {e}")
                # If conversion fails, try some common formats
                try:
                    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
                except:
                    pass
                
            # Ensure Value is numeric
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            
            return df
        else:
            print(f"CSV file doesn't have the expected 4 columns. Found {df.shape[1]} columns.")
            return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])
    except Exception as e:
        print(f"Error loading custom CSV: {e}")
        return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])