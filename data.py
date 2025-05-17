import pandas as pd
from currency import get_conversion_rate
from config import INVESTMENT_ACCOUNTS

def load_data(filepath='investment_data.csv'):
    try:
        return pd.read_csv(filepath, parse_dates=['Date'])
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])

def save_data(df, filepath='investment_data.csv'):
    df.to_csv(filepath, index=False)

def add_entry(df, date, investment, value):
    currency = INVESTMENT_ACCOUNTS[investment]
    new_entry = pd.DataFrame([[date, investment, currency, value]], columns=['Date', 'Investment', 'Currency', 'Value'])
    return pd.concat([df, new_entry], ignore_index=True)

def convert_to_usd(row):
    return row['Value'] * get_conversion_rate(row['Currency'])