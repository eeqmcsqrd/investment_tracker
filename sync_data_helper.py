# sync_data_helper.py
# Helper script for syncing investment data with cloud deployment
# Run this locally to update your Streamlit Cloud app data

import os
import sys
import sqlite3
import json
from datetime import datetime

def export_database_snapshot(db_path='investment_data.db', output_path='db_snapshot.json'):
    """
    Export database to JSON for easy syncing.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        snapshot = {
            'exported_at': datetime.now().isoformat(),
            'tables': {}
        }
        
        for table_name in tables:
            table_name = table_name[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Convert to list of dicts
            snapshot['tables'][table_name] = [
                dict(zip(columns, row)) for row in rows
            ]
        
        conn.close()
        
        # Write to JSON
        with open(output_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        print(f"✅ Database exported to {output_path}")
        print(f"   Tables: {', '.join(snapshot['tables'].keys())}")
        print(f"   Total records: {sum(len(v) for v in snapshot['tables'].values())}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting database: {e}")
        return False


def import_database_snapshot(snapshot_path='db_snapshot.json', db_path='investment_data.db'):
    """
    Import database from JSON snapshot.
    WARNING: This will replace existing data!
    """
    try:
        # Backup existing database
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"📦 Backed up existing database to {backup_path}")
        
        # Load snapshot
        with open(snapshot_path, 'r') as f:
            snapshot = json.load(f)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Import each table
        for table_name, rows in snapshot['tables'].items():
            if not rows:
                continue
            
            # Get columns
            columns = list(rows[0].keys())
            placeholders = ','.join(['?' for _ in columns])
            
            # Clear existing data
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Insert new data
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(
                    f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})",
                    values
                )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database imported from {snapshot_path}")
        print(f"   Imported at: {snapshot['exported_at']}")
        return True
        
    except Exception as e:
        print(f"❌ Error importing database: {e}")
        return False


def compare_databases(local_db='investment_data.db', remote_snapshot='db_snapshot.json'):
    """
    Compare local database with remote snapshot to see what changed.
    """
    try:
        # Export local to temp snapshot
        export_database_snapshot(local_db, 'temp_local_snapshot.json')
        
        # Load both snapshots
        with open('temp_local_snapshot.json', 'r') as f:
            local_snapshot = json.load(f)
        
        with open(remote_snapshot, 'r') as f:
            remote_snapshot_data = json.load(f)
        
        print("\n📊 Database Comparison")
        print("=" * 60)
        print(f"Local:  Exported at {local_snapshot['exported_at']}")
        print(f"Remote: Exported at {remote_snapshot_data['exported_at']}")
        print("=" * 60)
        
        for table_name in local_snapshot['tables'].keys():
            local_count = len(local_snapshot['tables'].get(table_name, []))
            remote_count = len(remote_snapshot_data['tables'].get(table_name, []))
            
            diff = local_count - remote_count
            symbol = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            
            print(f"{symbol} {table_name}: Local={local_count}, Remote={remote_count}, Diff={diff:+d}")
        
        # Clean up temp file
        os.remove('temp_local_snapshot.json')
        return True
        
    except Exception as e:
        print(f"❌ Error comparing databases: {e}")
        return False


def create_gitignore():
    """
    Create a comprehensive .gitignore file for the project.
    """
    gitignore_content = """# Environment and secrets
.env
*.env
.streamlit/secrets.toml

# Data files (sync separately for security)
investment_data.db
investment_data.csv
backups/
benchmarks_cache.json
*.backup_*

# Snapshots (optional - exclude if contains sensitive data)
db_snapshot.json
temp_local_snapshot.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
.Spotlight-V100
.Trashes

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Logs
*.log
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Created .gitignore file")


if __name__ == '__main__':
    print("🔄 Investment Tracker - Data Sync Helper")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python sync_data_helper.py export          # Export local DB to JSON")
        print("  python sync_data_helper.py import          # Import JSON to local DB")
        print("  python sync_data_helper.py compare         # Compare local vs remote")
        print("  python sync_data_helper.py gitignore       # Create .gitignore file")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'export':
        export_database_snapshot()
    elif command == 'import':
        response = input("⚠️  This will replace your local database. Continue? (yes/no): ")
        if response.lower() == 'yes':
            import_database_snapshot()
        else:
            print("❌ Import cancelled")
    elif command == 'compare':
        compare_databases()
    elif command == 'gitignore':
        create_gitignore()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
