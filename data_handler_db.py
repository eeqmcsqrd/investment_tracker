# data_handler_db.py data_handler_db.py (Part 1: Imports and Database Setup)
import pandas as pd # type: ignore
import sqlite3
import os
from datetime import datetime
from currency_service import get_conversion_rate
from config import INVESTMENT_ACCOUNTS

# Database file path
DB_FILE = 'investment_data.db'

def create_tables():
    """
    Create necessary database tables if they don't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create investments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        investment TEXT NOT NULL,
        currency TEXT NOT NULL,
        value REAL NOT NULL,
        UNIQUE(date, investment)
    )
    ''')
    
    # Create indexes for frequently queried columns
    # Index for date queries (e.g., filtering by date range)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_investments_date ON investments(date)')
    
    # Index for investment queries (for specific investment lookups)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_investments_investment ON investments(investment)')
    
    conn.commit()
    conn.close()
# data_handler_db.py (Part 2: Basic Data Loading & Saving)
def load_data(filepath=None):
    """
    Load investment data from SQLite database.
    
    Args:
        filepath (str): Not used, kept for compatibility with original function
        
    Returns:
        pandas.DataFrame: DataFrame containing investment data
    """
    try:
        # Ensure tables exist
        create_tables()
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        
        # Load all data from investments table
        query = "SELECT date, investment, currency, value FROM investments"
        df = pd.read_sql_query(query, conn, parse_dates=['date'])
        
        # Rename columns to match original CSV format
        df.rename(columns={'date': 'Date', 'investment': 'Investment', 
                          'currency': 'Currency', 'value': 'Value'}, inplace=True)
        
        conn.close()
        
        # If DataFrame is empty, return empty DataFrame with correct columns
        if df.empty:
            return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])
        
        return df
    except Exception as e:
        print(f"Error loading data from database: {e}")
        return pd.DataFrame(columns=['Date', 'Investment', 'Currency', 'Value'])

def save_data(df, filepath=None):
    """
    Save investment data to SQLite database. This function REPLACES all existing data.

    Args:
        df (pandas.DataFrame): DataFrame containing investment data
        filepath (str): Not used, kept for compatibility with original function

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Ensure tables exist
        create_tables()

        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Begin transaction for faster bulk operations
        conn.execute("BEGIN TRANSACTION")

        # Standardize column names
        df_to_save = df.copy()
        df_to_save.rename(columns={
            'Date': 'date',
            'Investment': 'investment',
            'Currency': 'currency',
            'Value': 'value'
        }, inplace=True)

        # Ensure only necessary columns are saved
        columns_to_save = ['date', 'investment', 'currency', 'value']
        # Handle potential extra columns gracefully
        df_to_save = df_to_save[[col for col in columns_to_save if col in df_to_save.columns]]

        # Ensure 'date' column exists and convert dates to strings in ISO format for SQLite storage
        if 'date' not in df_to_save.columns:
            print("Error: 'date' column not found in DataFrame.")
            conn.rollback()
            conn.close()
            return False
            
        # Convert Timestamp to datetime objects and then to strings in a single operation if possible
        try:
            if pd.api.types.is_datetime64_any_dtype(df_to_save['date']):
                df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
            else:
                df_to_save['date'] = pd.to_datetime(df_to_save['date']).dt.strftime('%Y-%m-%d')
        except Exception as date_err:
            print(f"Warning: Could not convert 'date' column to string format: {date_err}")
            conn.rollback()
            conn.close()
            return False

        # Clear existing data using DELETE with index optimization
        cursor.execute("DELETE FROM investments")

        # Convert DataFrame to list of tuples for bulk insertion
        # This is much faster than iterating row by row
        data_tuples = list(df_to_save.itertuples(index=False, name=None))

        # Insert data using executemany for efficiency
        cursor.executemany('''
        INSERT INTO investments (date, investment, currency, value)
        VALUES (?, ?, ?, ?)
        ''', data_tuples)

        # Commit the transaction
        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error saving data to database: {e}")
        # Ensure connection is closed even if error occurs
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False
# data_handler_db.py (Part 3: Legacy Add Entry Methods)
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
    import pandas as pd # type: ignore
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
    
    # Save to database
    save_data(result_df)
    
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
    # Use pandas operations for compatibility
    result_df = df.copy()
    
    # Process each investment
    for investment, value in investment_values.items():
        result_df = add_entry(result_df, date, investment, value)
    
    # Save to database
    save_data(result_df)
    
    return result_df
# data_handler_db.py (Part 4: DB-Native Entry Methods)
def add_entry_db(date, investment, value):
    """
    Add a single investment entry directly to the database.
    
    Parameters:
    date (datetime.date): Date of the entry
    investment (str): Name of the investment
    value (float): Value of the investment
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        # Ensure tables exist
        create_tables()
        
        # Convert date to string format for SQLite
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = pd.Timestamp(date).strftime('%Y-%m-%d')
        
        # Get the currency for this investment
        from config import INVESTMENT_ACCOUNTS
        currency = INVESTMENT_ACCOUNTS.get(investment, 'USD')
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if we already have entries for this date
        cursor.execute(
            "SELECT COUNT(*) FROM investments WHERE date = ?", 
            (date_str,)
        )
        entries_count = cursor.fetchone()[0]
        
        if entries_count == 0:
            # No entries for this date, get most recent entries
            cursor.execute(
                "SELECT MAX(date) FROM investments WHERE date < ?", 
                (date_str,)
            )
            most_recent_date = cursor.fetchone()[0]
            
            if most_recent_date:
                # Get all investments from most recent date
                cursor.execute(
                    "SELECT investment, currency, value FROM investments WHERE date = ?",
                    (most_recent_date,)
                )
                recent_entries = cursor.fetchall()
                
                # Insert all recent entries with new date
                for inv, curr, val in recent_entries:
                    if inv == investment:
                        # Update this specific investment with new value
                        cursor.execute('''
                        INSERT OR REPLACE INTO investments (date, investment, currency, value)
                        VALUES (?, ?, ?, ?)
                        ''', (date_str, inv, curr, value))
                    else:
                        # Copy over other investments with previous values
                        cursor.execute('''
                        INSERT OR REPLACE INTO investments (date, investment, currency, value)
                        VALUES (?, ?, ?, ?)
                        ''', (date_str, inv, curr, val))
                
                # Check if our investment was in the previous entries
                cursor.execute(
                    "SELECT COUNT(*) FROM investments WHERE date = ? AND investment = ?",
                    (date_str, investment)
                )
                if cursor.fetchone()[0] == 0:
                    # Investment wasn't in previous entries, add it
                    cursor.execute('''
                    INSERT INTO investments (date, investment, currency, value)
                    VALUES (?, ?, ?, ?)
                    ''', (date_str, investment, currency, value))
            else:
                # No previous entries, just add this one
                cursor.execute('''
                INSERT INTO investments (date, investment, currency, value)
                VALUES (?, ?, ?, ?)
                ''', (date_str, investment, currency, value))
        else:
            # Entries exist for this date, check if this investment exists
            cursor.execute(
                "SELECT COUNT(*) FROM investments WHERE date = ? AND investment = ?",
                (date_str, investment)
            )
            if cursor.fetchone()[0] == 0:
                # Investment doesn't exist for this date, add it
                cursor.execute('''
                INSERT INTO investments (date, investment, currency, value)
                VALUES (?, ?, ?, ?)
                ''', (date_str, investment, currency, value))
            else:
                # Investment exists, update it
                cursor.execute('''
                UPDATE investments 
                SET value = ?
                WHERE date = ? AND investment = ?
                ''', (value, date_str, investment))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding entry to database: {e}")
        return False
# data_handler_db.py (Part 5: Bulk DB Entry Method)
def add_bulk_entries_db(date, investment_values):
    """
    Add multiple investment entries directly to the database.
    
    Parameters:
    date (datetime.date): Date of the entries
    investment_values (dict): Dictionary mapping investment names to values
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        # Convert date to string format for SQLite
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = pd.Timestamp(date).strftime('%Y-%m-%d')
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if we already have entries for this date
        cursor.execute(
            "SELECT COUNT(*) FROM investments WHERE date = ?", 
            (date_str,)
        )
        entries_count = cursor.fetchone()[0]
        
        if entries_count == 0:
            # No entries for this date, get most recent entries
            cursor.execute(
                "SELECT MAX(date) FROM investments WHERE date < ?", 
                (date_str,)
            )
            most_recent_date = cursor.fetchone()[0]
            
            if most_recent_date:
                # Get all investments from most recent date
                cursor.execute(
                    "SELECT investment, currency, value FROM investments WHERE date = ?",
                    (most_recent_date,)
                )
                recent_entries = cursor.fetchall()
                
                # Insert all recent entries with new date
                for inv, curr, val in recent_entries:
                    if inv in investment_values:
                        # Update this investment with new value
                        cursor.execute('''
                        INSERT OR REPLACE INTO investments (date, investment, currency, value)
                        VALUES (?, ?, ?, ?)
                        ''', (date_str, inv, curr, investment_values[inv]))
                    else:
                        # Copy over other investments with previous values
                        cursor.execute('''
                        INSERT OR REPLACE INTO investments (date, investment, currency, value)
                        VALUES (?, ?, ?, ?)
                        ''', (date_str, inv, curr, val))
                
                # Add any investments in our values that weren't in previous entries
                for inv, val in investment_values.items():
                    cursor.execute(
                        "SELECT COUNT(*) FROM investments WHERE date = ? AND investment = ?",
                        (date_str, inv)
                    )
                    if cursor.fetchone()[0] == 0:
                        # This investment wasn't in previous entries
                        currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                        cursor.execute('''
                        INSERT INTO investments (date, investment, currency, value)
                        VALUES (?, ?, ?, ?)
                        ''', (date_str, inv, currency, val))
            else:
                # No previous entries, add all investments
                for inv, val in investment_values.items():
                    currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                    cursor.execute('''
                    INSERT INTO investments (date, investment, currency, value)
                    VALUES (?, ?, ?, ?)
                    ''', (date_str, inv, currency, val))
        else:
            # Entries exist for this date, update each investment
            for inv, val in investment_values.items():
                cursor.execute(
                    "SELECT COUNT(*) FROM investments WHERE date = ? AND investment = ?",
                    (date_str, inv)
                )
                if cursor.fetchone()[0] == 0:
                    # Investment doesn't exist for this date, add it
                    currency = INVESTMENT_ACCOUNTS.get(inv, 'USD')
                    cursor.execute('''
                    INSERT INTO investments (date, investment, currency, value)
                    VALUES (?, ?, ?, ?)
                    ''', (date_str, inv, currency, val))
                else:
                    # Investment exists, update it
                    cursor.execute('''
                    UPDATE investments 
                    SET value = ?
                    WHERE date = ? AND investment = ?
                    ''', (val, date_str, inv))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding bulk entries to database: {e}")
        return False
# data_handler_db.py (Part 6: Historical Performance Methods)
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
    
    return filtered_df

def get_historical_performance_db(start_date, end_date):
    """
    Get historical performance data directly from the database.
    
    Args:
        start_date (datetime): Start date for performance analysis
        end_date (datetime): End date for performance analysis
        
    Returns:
        pandas.DataFrame: Performance data for the specified date range
    """
    try:
        # Convert dates to string format for SQLite
        if isinstance(start_date, datetime):
            start_date_str = start_date.strftime('%Y-%m-%d')
        else:
            start_date_str = pd.Timestamp(start_date).strftime('%Y-%m-%d')
            
        if isinstance(end_date, datetime):
            end_date_str = end_date.strftime('%Y-%m-%d')
        else:
            end_date_str = pd.Timestamp(end_date).strftime('%Y-%m-%d')
        
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        
        # Query data for the date range
        query = """
        SELECT date, investment, currency, value 
        FROM investments 
        WHERE date >= ? AND date <= ?
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date_str, end_date_str))
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
        
        # Rename columns to match expected format
        df.rename(columns={'date': 'Date', 'investment': 'Investment', 
                           'currency': 'Currency', 'value': 'Value'}, inplace=True)
        
        # Convert date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Add USD values
        df['ValueUSD'] = df.apply(
            lambda row: row['Value'] * get_conversion_rate(row['Currency']), 
            axis=1
        )
        
        return df
    except Exception as e:
        print(f"Error getting historical performance from database: {e}")
        return pd.DataFrame()
# data_handler_db.py (Part 7: Relative Performance Methods)
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

def get_relative_performance_db(start_date, end_date, reference_investment, comparison_investments):
    """
    Calculate relative performance directly from the database.
    
    Args:
        start_date (datetime): Start date for performance comparison
        end_date (datetime): End date for performance comparison
        reference_investment (str): Name of the reference investment
        comparison_investments (list): List of investments to compare
        
    Returns:
        pandas.DataFrame: Relative performance data for plotting
    """
    # Get historical data from database
    df = get_historical_performance_db(start_date, end_date)
    
    # Use existing function with the DataFrame
    return get_relative_performance(df, start_date, end_date, reference_investment, comparison_investments)
# data_handler_db.py (Part 8: Previous Values Methods)
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
# data_handler_db.py (Part 9: DB-Native Previous Values Method)

def get_previous_values_db():
    """
    For each investment in the most recent date, find the previous value
    and calculate the delta, directly from the database using SQL window functions.

    Returns:
        pandas.DataFrame: DataFrame with previous values and deltas
    """
    try:
        conn = sqlite3.connect(DB_FILE)

        # Use a single optimized query with window functions to get all data needed
        query = """
        WITH LatestDate AS (
            SELECT MAX(date) as max_date FROM investments
        ),
        InvestmentData AS (
            SELECT
                investment,
                currency,
                value,
                date
            FROM investments
            WHERE date = (SELECT max_date FROM LatestDate)
        ),
        PreviousValues AS (
            SELECT
                i.investment,
                i.currency,
                i.value as current_value,
                i.date as current_date,
                (
                    SELECT value
                    FROM investments p
                    WHERE p.investment = i.investment
                    AND p.date < i.date
                    ORDER BY p.date DESC
                    LIMIT 1
                ) as previous_value,
                (
                    SELECT date
                    FROM investments p
                    WHERE p.investment = i.investment
                    AND p.date < i.date
                    ORDER BY p.date DESC
                    LIMIT 1
                ) as previous_date
            FROM InvestmentData i
        )
        SELECT
            investment AS Investment,
            currency AS Currency,
            current_value AS CurrentValue,
            previous_value AS PreviousValue,
            previous_date AS PreviousDate
        FROM PreviousValues
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return pd.DataFrame()

        # Process the results using vectorized operations instead of row-by-row processing
        # Create a copy to avoid pandas SettingWithCopyWarning
        result_df = df.copy()
        
        # Add USD conversion for all values at once
        conversion_rates = {row['Currency']: get_conversion_rate(row['Currency']) for _, row in result_df.iterrows()}
        result_df['rate'] = result_df['Currency'].map(conversion_rates)
        
        # Calculate USD values
        result_df['CurrentValueUSD'] = result_df['CurrentValue'] * result_df['rate']
        result_df['PreviousValueUSD'] = result_df['PreviousValue'] * result_df['rate']
        
        # Calculate deltas where previous values exist
        has_prev = result_df['PreviousValue'].notna()
        
        # Initialize all columns to handle both cases (with/without previous values)
        result_df['Delta'] = None
        result_df['DeltaPercent'] = None
        result_df['DeltaUSD'] = None
        result_df['DeltaUSDPercent'] = None
        
        # Calculate deltas only where previous values exist
        if has_prev.any():
            mask = has_prev
            result_df.loc[mask, 'Delta'] = result_df.loc[mask, 'CurrentValue'] - result_df.loc[mask, 'PreviousValue']
            
            # Avoid division by zero for percentage calculations
            non_zero_prev = (mask) & (result_df['PreviousValue'] != 0)
            if non_zero_prev.any():
                result_df.loc[non_zero_prev, 'DeltaPercent'] = (
                    result_df.loc[non_zero_prev, 'Delta'] / result_df.loc[non_zero_prev, 'PreviousValue'] * 100
                )
            
            # USD deltas
            result_df.loc[mask, 'DeltaUSD'] = result_df.loc[mask, 'CurrentValueUSD'] - result_df.loc[mask, 'PreviousValueUSD']
            
            # USD percentage deltas (avoiding division by zero)
            non_zero_prev_usd = (mask) & (result_df['PreviousValueUSD'] != 0)
            if non_zero_prev_usd.any():
                result_df.loc[non_zero_prev_usd, 'DeltaUSDPercent'] = (
                    result_df.loc[non_zero_prev_usd, 'DeltaUSD'] / 
                    result_df.loc[non_zero_prev_usd, 'PreviousValueUSD'] * 100
                )
        
        # Drop the temporary rate column
        result_df = result_df.drop(columns=['rate'])
        
        return result_df

    except Exception as e:
        print(f"Error getting previous values from database: {e}")
        # Ensure connection is closed in case of error during query
        if 'conn' in locals() and conn:
            conn.close()
        return pd.DataFrame()
        
# data_handler_db.py (Part 10: Investment History Methods)
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

def get_investment_history_db(investment):
    """
    Get historical data for a specific investment directly from the database.
    
    Args:
        investment (str): Name of the investment
        
    Returns:
        pandas.DataFrame: Historical data for the specified investment
    """
    try:
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        
        # Query investment history
        query = """
        SELECT date, currency, value
        FROM investments
        WHERE investment = ?
        ORDER BY date
        """
        
        df = pd.read_sql_query(query, conn, params=(investment,))
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
            
        # Rename columns to match expected format
        df.rename(columns={'date': 'Date'}, inplace=True)
        
        # Convert date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Add Investment column
        df['Investment'] = investment
        
        # Add USD values
        df['ValueUSD'] = df.apply(
            lambda row: row['value'] * get_conversion_rate(row['currency']), 
            axis=1
        )
        
        # Rename remaining columns to match expected format
        df.rename(columns={'currency': 'Currency', 'value': 'Value'}, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error getting investment history from database: {e}")
        return pd.DataFrame()

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
# data_handler_db.py (Part 11: DB-Native Portfolio Methods)
def get_portfolio_snapshot_db(date=None):
    """
    Get a snapshot of the portfolio for a specific date directly from the database.
    
    Args:
        date (datetime, optional): Date for the snapshot. 
                                  If None, the latest date is used.
        
    Returns:
        pandas.DataFrame: Portfolio snapshot for the specified date
    """
    try:
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # If no date specified, use the latest date
        if date is None:
            cursor.execute("SELECT MAX(date) FROM investments")
            date_str = cursor.fetchone()[0]
        else:
            # Convert date to string format for SQLite
            if isinstance(date, datetime):
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = pd.Timestamp(date).strftime('%Y-%m-%d')
        
        # Get data for the specified date
        query = """
        SELECT investment, currency, value
        FROM investments
        WHERE date = ?
        """
        
        df = pd.read_sql_query(query, conn, params=(date_str,))
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
            
        # Add Date column
        df['Date'] = pd.to_datetime(date_str)
        
        # Add USD values
        df['ValueUSD'] = df.apply(
            lambda row: row['value'] * get_conversion_rate(row['currency']), 
            axis=1
        )
        
        # Rename columns to match expected format
        df.rename(columns={'investment': 'Investment', 'currency': 'Currency', 'value': 'Value'}, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error getting portfolio snapshot from database: {e}")
        return pd.DataFrame()
# data_handler_db.py (Part 12: Import/Export Methods)
def import_csv_to_db(csv_filepath):
    """
    Import data from a CSV file to the SQLite database.
    
    Args:
        csv_filepath (str): Path to the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load CSV file
        df = pd.read_csv(csv_filepath)
        
        # Verify columns
        required_columns = ['Date', 'Investment', 'Currency', 'Value']
        if not all(col in df.columns for col in required_columns):
            print(f"CSV file missing required columns. Required: {required_columns}")
            return False
        
        # Convert to database format and save
        return save_data(df)
    except Exception as e:
        print(f"Error importing CSV to database: {e}")
        return False

def export_db_to_csv(csv_filepath):
    """
    Export data from the SQLite database to a CSV file.
    
    Args:
        csv_filepath (str): Path to save the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load all data from database
        df = load_data()
        
        # Save to CSV
        df.to_csv(csv_filepath, index=False)
        return True
    except Exception as e:
        print(f"Error exporting database to CSV: {e}")
        return False

def migrate_from_csv(csv_filepath):
    """
    Migrate data from an existing CSV file to the SQLite database.
    
    Args:
        csv_filepath (str): Path to the existing CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if database already exists and has data
        if os.path.exists(DB_FILE):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='investments'")
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM investments")
                row_count = cursor.fetchone()[0]
                conn.close()
                
                if row_count > 0:
                    # Removed the message "Database already contains data. Migration skipped."
                    return True
        
        # Database doesn't exist or is empty, proceed with migration
        return import_csv_to_db(csv_filepath)
    except Exception as e:
        print(f"Error during migration from CSV: {e}")
        return False
# Add benchmark comparison functionality
from benchmark_service import get_benchmark_performance, calculate_benchmark_returns

def get_benchmark_comparison(df, benchmark_name, start_date, end_date):
    """
    Compare portfolio performance to a benchmark over a specified time period.
    
    Args:
        df (pandas.DataFrame): Investment data
        benchmark_name (str): Name of the benchmark to compare against
        start_date (datetime): Start date for comparison
        end_date (datetime): End date for comparison
        
    Returns:
        tuple: (portfolio_performance_df, benchmark_performance_df, comparison_metrics)
    """
    # Get portfolio performance data
    portfolio_data = get_historical_performance_db(start_date, end_date)
    
    if portfolio_data.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    
    # Group by date and calculate total portfolio value for each date
    portfolio_by_date = portfolio_data.groupby('Date')['ValueUSD'].sum().reset_index()
    portfolio_by_date.rename(columns={'ValueUSD': 'Value'}, inplace=True)
    
    # Calculate portfolio returns
    portfolio_returns = calculate_portfolio_returns(portfolio_by_date)
    
    # Get benchmark data
    benchmark_data = get_benchmark_performance(benchmark_name, start_date, end_date)
    
    if benchmark_data.empty:
        return portfolio_returns, pd.DataFrame(), {}
    
    # Calculate benchmark returns
    benchmark_returns = calculate_benchmark_returns(benchmark_data)
    
    # Calculate comparison metrics
    comparison_metrics = calculate_comparison_metrics(portfolio_returns, benchmark_returns)
    
    return portfolio_returns, benchmark_returns, comparison_metrics

def calculate_portfolio_returns(portfolio_data):
    """
    Calculate returns for portfolio data.
    
    Args:
        portfolio_data (pandas.DataFrame): Portfolio data with Date and Value columns
        
    Returns:
        pandas.DataFrame: Portfolio data with added returns columns
    """
    if portfolio_data.empty or 'Value' not in portfolio_data.columns:
        return portfolio_data
    
    # Sort by date
    portfolio_data = portfolio_data.sort_values('Date')
    
    # Calculate daily returns
    portfolio_data['DailyReturn'] = portfolio_data['Value'].pct_change() * 100
    
    # Calculate cumulative returns (indexed to 100 at start)
    first_value = portfolio_data['Value'].iloc[0]
    portfolio_data['CumulativeReturn'] = (portfolio_data['Value'] / first_value - 1) * 100
    
    return portfolio_data

def calculate_comparison_metrics(portfolio_returns, benchmark_returns):
    """
    Calculate comparison metrics between portfolio and benchmark.
    
    Args:
        portfolio_returns (pandas.DataFrame): Portfolio returns data
        benchmark_returns (pandas.DataFrame): Benchmark returns data
        
    Returns:
        dict: Comparison metrics
    """
    if portfolio_returns.empty or benchmark_returns.empty:
        return {}
    
    # Create common date range
    common_dates = set(portfolio_returns['Date']).intersection(set(benchmark_returns['Date']))
    
    if not common_dates:
        return {}
    
    # Filter to common dates
    portfolio_filtered = portfolio_returns[portfolio_returns['Date'].isin(common_dates)]
    benchmark_filtered = benchmark_returns[benchmark_returns['Date'].isin(common_dates)]
    
    # Ensure both dataframes are sorted by date
    portfolio_filtered = portfolio_filtered.sort_values('Date')
    benchmark_filtered = benchmark_filtered.sort_values('Date')
    
    # Calculate total return
    portfolio_total_return = portfolio_filtered['CumulativeReturn'].iloc[-1]
    benchmark_total_return = benchmark_filtered['CumulativeReturn'].iloc[-1]
    
    # Calculate excess return (alpha)
    excess_return = portfolio_total_return - benchmark_total_return
    
        # ------ robust volatility / risk statistics (no RuntimeWarnings) ------
    if 'DailyReturn' in portfolio_filtered.columns and 'DailyReturn' in benchmark_filtered.columns:
        # Drop NaNs first
        p_ret = portfolio_filtered['DailyReturn'].dropna()
        b_ret = benchmark_filtered['DailyReturn'].dropna()
        n_obs = min(len(p_ret), len(b_ret))

        if n_obs >= 2:  # need at least two observations for stdev / cov
            # Annualised stdev (population, ddof=0, avoids “dof <= 0” warning)
            portfolio_volatility  = p_ret.std(ddof=0) * (252 ** 0.5)
            benchmark_volatility  = b_ret.std(ddof=0) * (252 ** 0.5)

            # Beta
            cov_pb = p_ret.cov(b_ret)
            var_b  = b_ret.var(ddof=0)
            beta = cov_pb / var_b if var_b != 0 else float("nan")

            # Tracking error
            tracking_error = (p_ret - b_ret).std(ddof=0) * (252 ** 0.5)

            # Information ratio
            info_ratio = excess_return / tracking_error if tracking_error != 0 else float("nan")
        else:
            # not enough data – flag as NaN so the UI shows “N/A”
            portfolio_volatility = benchmark_volatility = beta = tracking_error = info_ratio = float("nan")
    else:
        portfolio_volatility = benchmark_volatility = beta = tracking_error = info_ratio = float("nan")

    
    # Compile metrics
    metrics = {
        'portfolio_return': portfolio_total_return,
        'benchmark_return': benchmark_total_return,
        'excess_return': excess_return,
        'portfolio_volatility': portfolio_volatility,
        'benchmark_volatility': benchmark_volatility,
        'beta': beta,
        'tracking_error': tracking_error,
        'information_ratio': info_ratio,
    }
    
    return metrics

def get_benchmark_comparison_db(benchmark_name, start_date, end_date):
    """
    Get benchmark comparison directly from the database.
    
    Args:
        benchmark_name (str): Name of the benchmark to compare against
        start_date (datetime): Start date for comparison
        end_date (datetime): End date for comparison
        
    Returns:
        tuple: (portfolio_performance_df, benchmark_performance_df, comparison_metrics)
    """
    # Get all data for the period
    df = get_historical_performance_db(start_date, end_date)
    
    # Use the regular function with the retrieved data
    return get_benchmark_comparison(df, benchmark_name, start_date, end_date)