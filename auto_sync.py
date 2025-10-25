#!/usr/bin/env python3
"""
Auto-Sync System for Investment Tracker
Automatically syncs database changes to GitHub and triggers Streamlit Cloud updates

This script monitors the database for changes and automatically:
1. Exports database to JSON snapshot
2. Commits changes to GitHub
3. Pushes to remote repository
4. Optionally triggers Streamlit Cloud reboot

Usage:
    # Run as daemon (monitors continuously)
    python auto_sync.py --daemon

    # Run once (sync immediately)
    python auto_sync.py --once

    # Sync on every data change (integrate with app)
    from auto_sync import sync_to_github
    sync_to_github()
"""

import os
import sys
import time
import json
import hashlib
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

# Configuration is now loaded from sync_config.json
CONFIG_FILE = 'sync_config.json'

class AutoSync:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.repo_path = Path(__file__).parent
        self.config = self.load_config()
        self.db_file = self.config.get('files_to_sync', ['investment_data.db'])[0] # First file is the main db
        self.snapshot_file = 'db_snapshot.json' # this is still hardcoded, but now files_to_sync is used for commit
        self.sync_marker_file = '.last_sync_hash'


    def load_config(self):
        """Load configuration from JSON file"""
        config_path = self.repo_path / CONFIG_FILE
        if not config_path.exists():
            self.log(f"⚠️ Configuration file not found: {CONFIG_FILE}. Using default settings.")
            return {
                "auto_sync_enabled": False,
                "files_to_sync": ["investment_data.db", "db_snapshot.json"],
                "daemon_check_interval": 60,
                "commit_message_template": "Auto-sync: Update investment data - {timestamp}"
            }
        with open(config_path, 'r') as f:
            return json.load(f)

    def log(self, message):
        """Print log message if verbose"""
        if self.verbose:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {message}")

    def get_db_hash(self):
        """Calculate hash of database file to detect changes"""
        db_path = self.repo_path / self.db_file
        if not db_path.exists():
            return None

        hasher = hashlib.md5()
        with open(db_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def get_last_sync_hash(self):
        """Get the hash from last sync"""
        marker_path = self.repo_path / self.sync_marker_file
        if marker_path.exists():
            return marker_path.read_text().strip()
        return None

    def save_sync_hash(self, hash_value):
        """Save the current hash after successful sync"""
        marker_path = self.repo_path / self.sync_marker_file
        marker_path.write_text(hash_value)

    def has_changes(self):
        """Check if database has changed since last sync"""
        current_hash = self.get_db_hash()
        last_hash = self.get_last_sync_hash()
        return current_hash != last_hash and current_hash is not None

    def export_db_to_json(self):
        """Export database to JSON snapshot for cloud deployment"""
        try:
            db_path = self.repo_path / self.db_file
            snapshot_path = self.repo_path / self.snapshot_file

            if not db_path.exists():
                self.log(f"❌ Database file not found: {self.db_file}")
                return False

            # Connect to database and export
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Export investments table
            cursor.execute("SELECT date, investment, currency, value FROM investments ORDER BY date DESC")
            investments = [
                {
                    'date': row[0],
                    'investment': row[1],
                    'currency': row[2],
                    'value': row[3]
                }
                for row in cursor.fetchall()
            ]

            # Export sustainability data if exists
            sustainability = []
            try:
                cursor.execute("SELECT date, total_income_usd, total_expenses_usd, delta_usd FROM sustainability_daily ORDER BY date")
                sustainability = [
                    {
                        'date': row[0],
                        'total_income_usd': row[1],
                        'total_expenses_usd': row[2],
                        'delta_usd': row[3]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                pass  # Table might not exist

            conn.close()

            # Create snapshot
            snapshot = {
                'last_updated': datetime.now().isoformat(),
                'version': '1.0',
                'investments': investments,
                'sustainability': sustainability
            }

            # Write to file
            with open(snapshot_path, 'w') as f:
                json.dump(snapshot, f, indent=2)

            self.log(f"✅ Exported {len(investments)} entries to {self.snapshot_file}")
            return True

        except Exception as e:
            self.log(f"❌ Error exporting database: {e}")
            return False

    def git_add_and_commit(self):
        """Add and commit changes to git"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.log("❌ Not a git repository")
                return False

            # Add files
            files_to_add = self.config.get('files_to_sync', [])
            for file in files_to_add:
                file_path = self.repo_path / file
                if file_path.exists():
                    subprocess.run(
                        ['git', 'add', file],
                        cwd=self.repo_path,
                        check=True
                    )

            # Create commit message
            commit_message_template = self.config.get('commit_message_template', "Auto-sync: Update data - {timestamp}")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = commit_message_template.format(timestamp=timestamp)


            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log("✅ Changes committed to git")
                return True
            elif 'nothing to commit' in result.stdout.lower():
                self.log("ℹ️  No changes to commit")
                return True
            else:
                self.log(f"❌ Git commit failed: {result.stderr}")
                return False

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Git command failed: {e}")
            return False
        except Exception as e:
            self.log(f"❌ Error in git operations: {e}")
            return False

    def git_push(self):
        """Push changes to remote repository"""
        try:
            self.log("🚀 Pushing to GitHub...")
            result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("✅ Successfully pushed to GitHub")
                return True
            else:
                self.log(f"❌ Push failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log("❌ Push timed out")
            return False
        except Exception as e:
            self.log(f"❌ Error pushing to GitHub: {e}")
            return False

    def trigger_streamlit_reboot(self):
        """
        Trigger Streamlit Cloud reboot (optional)
        Note: Streamlit Cloud auto-detects changes, so this is usually not needed
        """
        self.log("ℹ️  Streamlit Cloud will auto-detect the changes")
        self.log("ℹ️  Changes will appear within 1-2 minutes")
        return True

    def sync(self):
        """Perform complete sync operation"""
        self.log("=" * 60)
        self.log("🔄 Starting auto-sync process...")

        # Check for changes
        if not self.has_changes():
            self.log("ℹ️  No database changes detected")
            return True

        self.log("📊 Database changes detected")

        # Step 1: Export to JSON
        if not self.export_db_to_json():
            self.log("❌ Sync failed at export step")
            return False

        # Step 2: Commit to git
        if not self.git_add_and_commit():
            self.log("❌ Sync failed at commit step")
            return False

        # Step 3: Push to GitHub
        if not self.git_push():
            self.log("❌ Sync failed at push step")
            return False

        # Step 4: Mark as synced
        current_hash = self.get_db_hash()
        self.save_sync_hash(current_hash)

        # Step 5: Notify about Streamlit Cloud
        self.trigger_streamlit_reboot()

        self.log("✅ Sync completed successfully!")
        self.log("=" * 60)
        return True

    def daemon_mode(self):
        """Run in daemon mode, continuously monitoring for changes"""
        if not self.config.get('auto_sync_enabled', False):
            self.log("ℹ️ Auto-sync is disabled in the configuration. Daemon will not start.")
            return

        check_interval = self.config.get('daemon_check_interval', 60)
        self.log("🚀 Starting auto-sync daemon...")
        self.log(f"📁 Monitoring: {self.db_file}")
        self.log(f"⏱️  Check interval: {check_interval} seconds")
        self.log("Press Ctrl+C to stop")
        self.log("")

        try:
            while True:
                self.sync()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.log("
👋 Auto-sync daemon stopped")


def sync_to_github(verbose=False):
    """
    Convenience function for integration with the main app
    Call this after data modifications to trigger sync
    """
    syncer = AutoSync(verbose=verbose)
    if syncer.config.get('auto_sync_enabled', False) and syncer.config.get('sync_on_data_change', False):
        return syncer.sync()
    return True


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Auto-sync investment tracker data to GitHub'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run in daemon mode (continuous monitoring)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run sync once and exit'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output messages'
    )

    args = parser.parse_args()

    syncer = AutoSync(verbose=not args.quiet)

    if args.daemon:
        syncer.daemon_mode()
    else:
        success = syncer.sync()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()