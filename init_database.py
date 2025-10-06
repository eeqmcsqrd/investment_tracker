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
    Uses proper database schema instead of generic TEXT columns.
    """
    # Check if force reset is requested
    if os.path.exists('force_db_reset.txt') and os.path.exists(DB_FILE):
        sys.stderr.write(f"🔄 Force reset requested - deleting old database...\n")
        sys.stderr.flush()
        try:
            os.remove(DB_FILE)
            os.remove('force_db_reset.txt')  # Remove trigger file
            sys.stderr.write(f"✅ Old database deleted\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"⚠️  Could not delete old database: {e}\n")
            sys.stderr.flush()

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

        # Create database with proper schema
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create investments table with correct schema (lowercase columns)
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

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_investments_date ON investments(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_investments_investment ON investments(investment)')

        # Create sustainability_daily table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sustainability_daily (
            date TEXT PRIMARY KEY,
            total_income_usd REAL NOT NULL DEFAULT 0,
            total_expenses_usd REAL NOT NULL DEFAULT 0,
            delta_usd REAL NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sustainability_date ON sustainability_daily(date)')

        # Create expenses table if needed
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            currency TEXT NOT NULL
        )
        ''')

        # Import data from snapshot - support both old and new formats
        # New format: snapshot['investments'], snapshot['sustainability']
        # Old format: snapshot['tables']['investments'], etc.

        # Detect format
        if 'tables' in snapshot:
            # Old format
            tables_data = snapshot['tables']
        else:
            # New format from auto_sync.py
            tables_data = {
                'investments': snapshot.get('investments', []),
                'sustainability_daily': snapshot.get('sustainability', [])
            }

        for table_name, rows in tables_data.items():
            if not rows:
                sys.stderr.write(f"  ⏭️  Skipping empty table: {table_name}\n")
                continue

            # Handle table-specific imports with column name mapping
            if table_name == 'investments':
                for row in rows:
                    # Map capitalized JSON keys to lowercase DB columns
                    date_val = row.get('Date') or row.get('date')
                    investment_val = row.get('Investment') or row.get('investment')
                    currency_val = row.get('Currency') or row.get('currency')
                    value_val = row.get('Value') or row.get('value')

                    if date_val and investment_val:  # Only insert if required fields exist
                        cursor.execute(
                            'INSERT OR IGNORE INTO investments (date, investment, currency, value) VALUES (?, ?, ?, ?)',
                            (date_val, investment_val, currency_val, value_val)
                        )

            elif table_name == 'sustainability_daily':
                for row in rows:
                    date_val = row.get('date')
                    if date_val:
                        cursor.execute(
                            '''INSERT OR REPLACE INTO sustainability_daily
                               (date, total_income_usd, total_expenses_usd, delta_usd)
                               VALUES (?, ?, ?, ?)''',
                            (date_val, row.get('total_income_usd', 0),
                             row.get('total_expenses_usd', 0), row.get('delta_usd', 0))
                        )

            elif table_name == 'expenses':
                for row in rows:
                    date_val = row.get('date')
                    if date_val:
                        cursor.execute(
                            '''INSERT INTO expenses (date, category, description, amount, currency)
                               VALUES (?, ?, ?, ?, ?)''',
                            (date_val, row.get('category', ''), row.get('description', ''),
                             row.get('amount', 0), row.get('currency', 'USD'))
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
