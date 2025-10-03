# init_database.py
# Automatically initialize database from JSON snapshot on startup

import os
import json
import sqlite3
import sys

DB_FILE = 'investment_data.db'
SNAPSHOT_FILE = 'db_snapshot.json'

def init_database_from_snapshot():
    """
    Create database from JSON snapshot if database doesn't exist.
    This runs automatically on Streamlit Cloud startup.
    """
    # Skip if database already exists
    if os.path.exists(DB_FILE):
        sys.stderr.write(f"✅ Database exists at {DB_FILE}\n")
        sys.stderr.flush()
        return True

    # Check if snapshot exists
    if not os.path.exists(SNAPSHOT_FILE):
        sys.stderr.write(f"⚠️  No snapshot file found at {SNAPSHOT_FILE}\n")
        sys.stderr.write(f"   Current directory: {os.getcwd()}\n")
        sys.stderr.write(f"   Files: {os.listdir('.')}\n")
        sys.stderr.flush()
        return False

    try:
        sys.stderr.write(f"📦 Initializing database from {SNAPSHOT_FILE}...\n")
        sys.stderr.flush()
        
        # Load snapshot
        with open(SNAPSHOT_FILE, 'r') as f:
            snapshot = json.load(f)
        
        # Create database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Import each table
        for table_name, rows in snapshot['tables'].items():
            if not rows:
                print(f"  ⏭️  Skipping empty table: {table_name}")
                continue
            
            # Get columns from first row
            columns = list(rows[0].keys())

            # Create table (simple approach - you may need to adjust types)
            col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
            cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs})')

            # Insert data
            placeholders = ','.join(['?' for _ in columns])
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(
                    f'INSERT INTO "{table_name}" ({",".join([f'"{col}"' for col in columns])}) VALUES ({placeholders})',
                    values
                )

            sys.stderr.write(f"  ✅ Imported {len(rows)} rows into {table_name}\n")
            sys.stderr.flush()

        conn.commit()
        conn.close()

        sys.stderr.write(f"✅ Database successfully created at {DB_FILE}\n")
        sys.stderr.flush()
        return True

    except Exception as e:
        sys.stderr.write(f"❌ Error initializing database: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return False

# Run automatically when imported
if __name__ == "__main__" or True:  # Always run on import
    init_database_from_snapshot()
