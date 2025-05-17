#!/usr/bin/env python
# migrate_to_db.py
"""
Script to migrate investment data from CSV to SQLite database.
This is a standalone utility that can be run to perform the initial migration.
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

def create_database():
    """Create the SQLite database and required tables"""
    conn = sqlite3.connect('investment_data.db')
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
    
    conn.commit()
    conn.close()
    
    print("Database structure created successfully")

def import_csv_to_db(csv_filepath):
    """Import data from CSV file to database"""
    # Check if file exists
    if not os.path.exists(csv_filepath):
        print(f"Error: File '{csv_filepath}' not found")
        return False
    
    try:
        # Load CSV file
        print(f"Loading data from {csv_filepath}...")
        df = pd.read_csv(csv_filepath)
        
        # Check for required columns
        required_columns = ['Date', 'Investment', 'Currency', 'Value']
        if not all(col in df.columns for col in required_columns):
            print(f"CSV file missing required columns. Required: {required_columns}")
            print(f"Found: {df.columns.tolist()}")
            return False
        
        # Process data types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Check for invalid dates
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            print(f"Warning: {invalid_dates} rows with invalid dates found")
            # Remove rows with invalid dates
            df = df.dropna(subset=['Date'])
        
        # Convert dates to string format for SQLite
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        # Ensure Investment is string
        df['investment'] = df['Investment'].astype(str)
        
        # Ensure Currency is string
        df['currency'] = df['Currency'].astype(str)
        
        # Ensure Value is numeric
        df['value'] = pd.to_numeric(df['Value'], errors='coerce')
        
        # Check for invalid values
        invalid_values = df['value'].isna().sum()
        if invalid_values > 0:
            print(f"Warning: {invalid_values} rows with invalid values found")
            # Remove rows with invalid values
            df = df.dropna(subset=['value'])
        
        # Keep only the columns we need
        df = df[['date', 'investment', 'currency', 'value']]
        
        # Connect to database
        conn = sqlite3.connect('investment_data.db')
        cursor = conn.cursor()
        
        # Check if database already has data
        cursor.execute("SELECT COUNT(*) FROM investments")
        row_count = cursor.fetchone()[0]
        
        if row_count > 0:
            response = input("Database already contains data. Replace all data? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled")
                conn.close()
                return False
            
            # Clear existing data
            print("Clearing existing data...")
            cursor.execute("DELETE FROM investments")
        
        # Insert data into database
        print(f"Importing {len(df)} records...")
        for _, row in df.iterrows():
            cursor.execute('''
            INSERT OR REPLACE INTO investments (date, investment, currency, value)
            VALUES (?, ?, ?, ?)
            ''', (row['date'], row['investment'], row['currency'], row['value']))
        
        # Commit changes and close connection
        conn.commit()
        
        # Verify import
        cursor.execute("SELECT COUNT(*) FROM investments")
        final_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Import completed. {final_count} records imported.")
        return True
    
    except Exception as e:
        print(f"Error importing data: {e}")
        return False

def main():
    """Main function"""
    print("Investment Data Migration Utility")
    print("=================================")
    
    # Create database structure
    create_database()
    
    # Determine CSV file to import
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Check for default file
        if os.path.exists('investment_data.csv'):
            csv_file = 'investment_data.csv'
        else:
            csv_file = input("Enter path to CSV file: ")
    
    # Import data
    success = import_csv_to_db(csv_file)
    
    if success:
        # Create backup of original CSV
        try:
            import shutil
            backup_name = f"investment_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            shutil.copy2(csv_file, backup_name)
            print(f"Created backup of original CSV as {backup_name}")
        except Exception as e:
            print(f"Warning: Failed to create backup of original CSV: {e}")
        
        print("\nMigration completed successfully.")
        print("You can now use the database version of the application.")
    else:
        print("\nMigration failed.")

if __name__ == "__main__":
    main()