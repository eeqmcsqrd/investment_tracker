# data_handler.py
import pandas as pd
import os
from currency_service import get_conversion_rate
from config import INVESTMENT_ACCOUNTS

def load_data(filepath='investment_data.csv'):
    """
    Load investment data from CSV file.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing investment data
    """
    try:
        # First, try to load the CSV as a standard format
        try:
            df = pd.read_csv(filepath)
            
            # Check if this is our expected app format with proper column names
            expected_columns = set(['Date', 'Investment', 'Currency', 'Value'])
            
            # If not all expected columns are present, this might be a different format
            if not expected_columns.issubset(set(df.columns)):
                # Try loading as a custom format (Date,Investment,Currency,Value per row)
                df = pd.read_csv(filepath, header=None)
                
                # If it has 4 columns, assume it's in the Date,Investment,Currency,Value format
                if df.shape[1] == 4:
                    df.columns = ['Date', 'Investment', 'Currency', 'Value']
                    
        except Exception as e:
            print(f"Standard CSV loading failed, trying alternative format: {e}")
            # If that failed, try loading without headers
            df = pd.read_csv(filepath, header=None)
            
            # If it has 4 columns, assume it's in the Date,Investment,Currency,Value format
            if df.shape[1] == 4:
                df.columns = ['Date', 'Investment', 'Currency', 'Value']
            else:
                # If we can't determine the format, create an empty DataFrame
                raise ValueError(f"Unable to determine CSV format. Found {df.shape[1]} columns, expected 4.")
        
        # Convert Date column to datetime with flexible parsing
        if 'Date' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)
            except Exception as e:
                print(f"Date conversion error, trying common formats: {e}")
                # Try common date formats if the flexible parsing fails
                date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y']
                for date_format in date_formats:
                    try:
                        df['Date'] = pd.to_datetime(df['Date'], format=date_format, errors='coerce')
                        # If we have valid dates, break the loop
                        if not df['Date'].isna().all():
                            break
                    except:
                        continue
        
        # Ensure Investment column is string type
        if 'Investment' in df.columns:
            df['Investment'] = df['Investment'].astype(str)
        
        # Ensure Currency column is string type
        if 'Currency' in df.columns:
            df['Currency'] = df['Currency'].astype(str)
        
        # Ensure Value column is numeric
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        
        return df
    except FileNotFoundError:
        # Create empty DataFrame with the correct columns
        return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])

def save_data(df, filepath='investment_data.csv'):
    """
    Save investment data to CSV file.
    
    Args:
        df (pandas.DataFrame): DataFrame containing investment data
        filepath (str): Path to the CSV file
    """
    try:
        # Ensure only necessary columns are saved
        columns_to_save = ['Date', 'Investment', 'Currency', 'Value']
        df = df[columns_to_save]
        
        # Sort by date descending before saving
        df = df.sort_values('Date', ascending=False)
        
        # Create backup if file exists
        if os.path.exists(filepath):
            backup_filepath = f"{filepath}.bak"
            os.rename(filepath, backup_filepath)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def add_entry(df, date, investment, value):
    """
    Add a single investment entry while preserving values of other investments.
    
    Parameters:
    df (pandas.DataFrame): The existing investment data
    date (datetime.date): Date of the entry
    investment (str): Name of the investment
    value (float): Value of the investment
    
    Returns:
    pandas.DataFrame: Updated DataFrame with the new entry
    """
    import pandas as pd
    from datetime import datetime
    
    # Convert date to datetime if it's not already
    if not isinstance(date, pd.Timestamp):
        date = pd.Timestamp(date)
    
    # Get the currency for this investment
    from config import INVESTMENT_ACCOUNTS
    currency = INVESTMENT_ACCOUNTS.get(investment, 'USD')
    
    # Check if we already have any entries for this date
    same_date_entries = df[df['Date'] == date]
    
    if same_date_entries.empty:
        # If no entries exist for this date, we need to get the most recent values
        # for all other investments and create entries for them on this date
        
        # Get the most recent date before the current one
        recent_dates = df[df['Date'] < date]['Date'].unique()
        
        if len(recent_dates) > 0:
            most_recent_date = max(recent_dates)
            recent_entries = df[df['Date'] == most_recent_date].copy()
            
            # Create a new DataFrame for this date with all recent values
            new_entries = recent_entries.copy()
            new_entries['Date'] = date
            
            # Update the value of our specific investment
            mask = new_entries['Investment'] == investment
            if mask.any():
                # Update existing investment
                new_entries.loc[mask, 'Value'] = value
            else:
                # Add this investment if it doesn't exist in previous entries
                new_row = pd.DataFrame({
                    'Date': [date],
                    'Investment': [investment],
                    'Currency': [currency],
                    'Value': [value]
                })
                new_entries = pd.concat([new_entries, new_row], ignore_index=True)
            
            # Combine with existing data
            result_df = pd.concat([df, new_entries], ignore_index=True)
        else:
            # No previous data exists, just add this single entry
            new_row = pd.DataFrame({
                'Date': [date],
                'Investment': [investment],
                'Currency': [currency],
                'Value': [value]
            })
            result_df = pd.concat([df, new_row], ignore_index=True)
    else:
        # Entries already exist for this date
        # Check if this specific investment already has an entry
        existing_entry = same_date_entries[same_date_entries['Investment'] == investment]
        
        if existing_entry.empty:
            # This investment doesn't have an entry for this date, add it
            new_row = pd.DataFrame({
                'Date': [date],
                'Investment': [investment],
                'Currency': [currency],
                'Value': [value]
            })
            result_df = pd.concat([df, new_row], ignore_index=True)
        else:
            # This investment already has an entry for this date, update it
            result_df = df.copy()
            mask = (result_df['Date'] == date) & (result_df['Investment'] == investment)
            result_df.loc[mask, 'Value'] = value
    
    # Remove duplicate entries if any
    result_df = result_df.drop_duplicates(subset=['Date', 'Investment'], keep='last')
    
    return result_df

def add_bulk_entries(df, date, investment_values):
    """
    Add multiple investment entries for a single date while preserving other values.
    
    Parameters:
    df (pandas.DataFrame): The existing investment data
    date (datetime.date): Date of the entries
    investment_values (dict): Dictionary mapping investment names to values
    
    Returns:
    pandas.DataFrame: Updated DataFrame with the new entries
    """
    import pandas as pd
    from datetime import datetime
    from config import INVESTMENT_ACCOUNTS
    
    # Convert date to timestamp if it's not already
    if not isinstance(date, pd.Timestamp):
        date = pd.Timestamp(date)
    
    # Check if we already have any entries for this date
    same_date_entries = df[df['Date'] == date]
    
    if same_date_entries.empty:
        # If no entries exist for this date, get the most recent values
        # for all other investments and create entries for them
        
        # Get the most recent date before the current one
        recent_dates = df[df['Date'] < date]['Date'].unique()
        
        if len(recent_dates) > 0:
            most_recent_date = max(recent_dates)
            recent_entries = df[df['Date'] == most_recent_date].copy()
            
            # Create a new DataFrame for this date with all recent values
            new_entries = recent_entries.copy()
            new_entries['Date'] = date
            
            # Update the values of our specific investments
            for inv, value in investment_values.items():
                mask = new_entries['Investment'] == inv
                if mask.any():
                    # Update existing investment
                    new_entries.loc[mask, 'Value'] = value
                else:
                    # Add this investment if it doesn't exist in previous entries
                    currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                    new_row = pd.DataFrame({
                        'Date': [date],
                        'Investment': [inv],
                        'Currency': [currency],
                        'Value': [value]
                    })
                    new_entries = pd.concat([new_entries, new_row], ignore_index=True)
            
            # Combine with existing data
            result_df = pd.concat([df, new_entries], ignore_index=True)
        else:
            # No previous data exists, just add these entries
            new_entries = []
            for inv, value in investment_values.items():
                currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                new_entries.append({
                    'Date': date,
                    'Investment': inv,
                    'Currency': currency,
                    'Value': value
                })
            
            new_entries_df = pd.DataFrame(new_entries)
            result_df = pd.concat([df, new_entries_df], ignore_index=True)
    else:
        # Entries already exist for this date, update only the specified investments
        result_df = df.copy()
        
        for inv, value in investment_values.items():
            existing_entry = same_date_entries[same_date_entries['Investment'] == inv]
            
            if existing_entry.empty:
                # This investment doesn't have an entry for this date, add it
                currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                new_row = pd.DataFrame({
                    'Date': [date],
                    'Investment': [inv],
                    'Currency': [currency],
                    'Value': [value]
                })
                result_df = pd.concat([result_df, new_row], ignore_index=True)
            else:
                # This investment already has an entry for this date, update it
                mask = (result_df['Date'] == date) & (result_df['Investment'] == inv)
                result_df.loc[mask, 'Value'] = value
    
    # Remove duplicate entries if any
    result_df = result_df.drop_duplicates(subset=['Date', 'Investment'], keep='last')
    
    return result_df

def get_historical_performance(df, start_date, end_date):
    """
    Get historical performance data for a date range.
    
    Args:
        df (pandas.DataFrame): Investment data
        start_date (datetime): Start date for performance analysis
        end_date (datetime): End date for performance analysis
        
    Returns:
        pandas.DataFrame: Performance data for the specified date range
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filter by date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    # Add USD values if not already present
    if 'ValueUSD' not in filtered_df.columns:
        filtered_df['ValueUSD'] = filtered_df.apply(
            lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
            axis=1
        )
    
    # Get unique dates in the range
    unique_dates = filtered_df['Date'].sort_values().unique()
    
    # Get unique investments
    investments = filtered_df['Investment'].unique()
    
    # For each date, get the latest values for each investment
    performance_data = []
    
    for date in unique_dates:
        date_df = filtered_df[filtered_df['Date'] == date]
        
        for investment in investments:
            inv_data = date_df[date_df['Investment'] == investment]
            
            if not inv_data.empty:
                performance_data.append({
                    'Date': date,
                    'Investment': investment,
                    'Currency': inv_data.iloc[0]['Currency'],
                    'Value': inv_data.iloc[0]['Value'],
                    'ValueUSD': inv_data.iloc[0]['ValueUSD']
                })
    
    return pd.DataFrame(performance_data)

def get_relative_performance(df, start_date, end_date, reference_investment, comparison_investments):
    """
    Calculate relative performance of investments compared to a reference investment.
    
    Args:
        df (pandas.DataFrame): Investment data
        start_date (datetime): Start date for performance comparison
        end_date (datetime): End date for performance comparison
        reference_investment (str): Name of the reference investment
        comparison_investments (list): List of investments to compare
        
    Returns:
        pandas.DataFrame: Relative performance data for plotting
    """
    if df.empty:
        return pd.DataFrame()
    
    # Ensure all investments are strings
    reference_investment = str(reference_investment)
    comparison_investments = [str(inv) for inv in comparison_investments]
    
    # Add reference investment to comparison set if not already there
    if reference_investment not in comparison_investments:
        all_investments = [reference_investment] + comparison_investments
    else:
        all_investments = comparison_investments.copy()
    
    # Filter data by date range and investments
    filtered_df = df[
        (df['Date'] >= start_date) & 
        (df['Date'] <= end_date) & 
        (df['Investment'].isin(all_investments))
    ].copy()
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    # Add USD values if not already present
    if 'ValueUSD' not in filtered_df.columns:
        filtered_df['ValueUSD'] = filtered_df.apply(
            lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
            axis=1
        )
    
    # Get unique dates in the range
    unique_dates = sorted(filtered_df['Date'].unique())
    
    # Create a dict to hold investment values by date
    investment_values = {inv: {} for inv in all_investments}
    
    # Extract values for each investment at each date
    for date in unique_dates:
        date_df = filtered_df[filtered_df['Date'] == date]
        
        for inv in all_investments:
            inv_data = date_df[date_df['Investment'] == inv]
            
            if not inv_data.empty:
                # Store the USD value for this investment on this date
                investment_values[inv][date] = inv_data.iloc[0]['ValueUSD']
    
    # Check if we have data for the reference investment
    if reference_investment not in investment_values or not investment_values[reference_investment]:
        return pd.DataFrame()
    
    # Get the first date where we have data for the reference investment
    reference_dates = sorted(investment_values[reference_investment].keys())
    if not reference_dates:
        return pd.DataFrame()
    
    first_date = reference_dates[0]
    reference_start_value = investment_values[reference_investment][first_date]
    
    if reference_start_value == 0:
        # Can't use zero as a base for percentage calculation
        return pd.DataFrame()
    
    # Calculate relative performance
    result_data = []
    
    for date in unique_dates:
        # Skip dates before the first available reference date
        if date < first_date:
            continue
            
        # For each investment, calculate relative performance if we have data
        for inv in all_investments:
            if date in investment_values[inv] and first_date in investment_values[inv]:
                # Starting value for this investment
                inv_start_value = investment_values[inv][first_date]
                
                if inv_start_value > 0:
                    # Current value
                    current_value = investment_values[inv][date]
                    
                    # Calculate percentage change from start for this investment
                    pct_change = ((current_value / inv_start_value) - 1) * 100
                    
                    # If this is the reference investment, the relative performance is always 0
                    if inv == reference_investment:
                        relative_pct = 0
                    else:
                        # Calculate reference change (so we can normalize against it)
                        if date in investment_values[reference_investment]:
                            ref_current = investment_values[reference_investment][date]
                            ref_pct_change = ((ref_current / reference_start_value) - 1) * 100
                            # Relative performance is this investment's change minus reference change
                            relative_pct = pct_change - ref_pct_change
                        else:
                            # Skip if we don't have reference data for this date
                            continue
                    
                    # Add data point
                    result_data.append({
                        'Date': date,
                        'Investment': inv,
                        'Value': current_value,
                        'PctChange': pct_change,
                        'RelativePct': relative_pct
                    })
    
    return pd.DataFrame(result_data)

def get_previous_values(df):
    """
    For each investment in the most recent date, find the previous value
    and calculate the delta.
    
    Args:
        df (pandas.DataFrame): Investment data
        
    Returns:
        pandas.DataFrame: DataFrame with previous values and deltas
    """
    if df.empty:
        return pd.DataFrame()
    
    # Get the latest date
    latest_date = df['Date'].max()
    
    # Get all investments from the latest date
    latest_df = df[df['Date'] == latest_date].copy()
    
    # Sort the remaining data by date (descending)
    prev_df = df[df['Date'] < latest_date].sort_values('Date', ascending=False)
    
    results = []
    
    # For each investment in the latest snapshot
    for _, row in latest_df.iterrows():
        investment = row['Investment']
        current_value = row['Value']
        current_value_usd = row['ValueUSD'] if 'ValueUSD' in row else row['Value'] * get_conversion_rate(row['Currency'])
        
        # Find the previous entry for this investment
        prev_entries = prev_df[prev_df['Investment'] == investment]
        
        if not prev_entries.empty:
            # Get the most recent previous entry
            prev_entry = prev_entries.iloc[0]
            prev_date = prev_entry['Date']
            prev_value = prev_entry['Value']
            prev_value_usd = prev_entry['ValueUSD'] if 'ValueUSD' in prev_entry else prev_entry['Value'] * get_conversion_rate(prev_entry['Currency'])
            
            # Calculate deltas
            delta = current_value - prev_value
            delta_pct = (delta / prev_value * 100) if prev_value != 0 else 0
            
            delta_usd = current_value_usd - prev_value_usd
            delta_usd_pct = (delta_usd / prev_value_usd * 100) if prev_value_usd != 0 else 0
            
            # Add to results
            results.append({
                'Investment': investment,
                'Currency': row['Currency'],
                'CurrentValue': current_value,
                'CurrentValueUSD': current_value_usd,
                'PreviousDate': prev_date,
                'PreviousValue': prev_value,
                'PreviousValueUSD': prev_value_usd,
                'Delta': delta,
                'DeltaPercent': delta_pct,
                'DeltaUSD': delta_usd,
                'DeltaUSDPercent': delta_usd_pct
            })
        else:
            # No previous entry found
            results.append({
                'Investment': investment,
                'Currency': row['Currency'],
                'CurrentValue': current_value,
                'CurrentValueUSD': current_value_usd,
                'PreviousDate': None,
                'PreviousValue': None,
                'PreviousValueUSD': None,
                'Delta': None,
                'DeltaPercent': None,
                'DeltaUSD': None,
                'DeltaUSDPercent': None
            })
    
    return pd.DataFrame(results)

def get_investment_history(df, investment):
    """
    Get historical data for a specific investment.
    
    Args:
        df (pandas.DataFrame): Investment data
        investment (str): Name of the investment
        
    Returns:
        pandas.DataFrame: Historical data for the specified investment
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filter by investment
    history = df[df['Investment'] == investment].copy()
    
    # Sort by date
    history = history.sort_values('Date')
    
    # Add USD values if not already present
    if 'ValueUSD' not in history.columns:
        history['ValueUSD'] = history.apply(
            lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
            axis=1
        )
    
    return history

def get_portfolio_snapshot(df, date=None):
    """
    Get a snapshot of the portfolio for a specific date.
    
    Args:
        df (pandas.DataFrame): Investment data
        date (datetime, optional): Date for the snapshot. 
                                  If None, the latest date is used.
        
    Returns:
        pandas.DataFrame: Portfolio snapshot for the specified date
    """
    if df.empty:
        return pd.DataFrame()
    
    # If no date specified, use the latest date
    if date is None:
        date = df['Date'].max()
    
    # Get data for the specified date
    snapshot = df[df['Date'] == date].copy()
    
    # Add USD values if not already present
    if 'ValueUSD' not in snapshot.columns:
        snapshot['ValueUSD'] = snapshot.apply(
            lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
            axis=1
        )
    
    return snapshot