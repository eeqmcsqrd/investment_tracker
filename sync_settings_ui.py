"""
Sync Settings UI Component
Provides a user interface for configuring auto-sync settings
"""

import streamlit as st
import json
from pathlib import Path
from sync_integration import load_sync_config
from auto_sync import AutoSync

CONFIG_FILE = 'sync_config.json'

def save_sync_config(config: dict):
    """Save sync configuration to file"""
    config_path = Path(__file__).parent / CONFIG_FILE
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def render_sync_settings():
    """Render sync settings UI in Streamlit"""
    st.subheader("🔄 Auto-Sync Settings")

    st.markdown("""
    Configure automatic synchronization between your local database and GitHub/Streamlit Cloud.
    """)

    # Load current config
    config = load_sync_config()

    # Create columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Main toggle
        auto_sync_enabled = st.toggle(
            "Enable Auto-Sync",
            value=config.get('auto_sync_enabled', False),
            help="When enabled, changes will automatically sync to GitHub",
            key="auto_sync_toggle"
        )

        if auto_sync_enabled:
            st.info("✅ Auto-sync is **enabled**. Changes will sync automatically.")

            # Sync mode
            sync_mode = st.radio(
                "Sync Mode",
                options=["immediate", "manual", "scheduled"],
                index=["immediate", "manual", "scheduled"].index(config.get('sync_mode', 'manual')),
                help="Choose when to sync changes",
                horizontal=True,
                key="sync_mode_radio"
            )

            if sync_mode == "immediate":
                st.success("📤 Changes sync immediately after each update")
            elif sync_mode == "manual":
                st.info("🖱️ Sync when you click the sync button")
            else:
                st.warning("⏰ Scheduled sync not yet implemented")

            # Additional options
            with st.expander("Advanced Options"):
                verbose_logging = st.checkbox(
                    "Verbose Logging",
                    value=config.get('verbose_logging', True),
                    help="Show detailed sync logs",
                    key="verbose_logging_cb"
                )

                notification_on_sync = st.checkbox(
                    "Show Notifications",
                    value=config.get('notification_on_sync', True),
                    help="Show notification when sync completes",
                    key="notification_sync_cb"
                )

        else:
            st.warning("⚠️ Auto-sync is **disabled**. You'll need to sync manually.")
            sync_mode = "manual"
            verbose_logging = config.get('verbose_logging', True)
            notification_on_sync = config.get('notification_on_sync', True)

    with col2:
        st.markdown("### Quick Actions")

        # Manual sync button
        if st.button("🚀 Sync Now", use_container_width=True, type="primary"):
            with st.spinner("Syncing to GitHub..."):
                syncer = AutoSync(verbose=True)
                success = syncer.sync()

                if success:
                    st.success("✅ Synced successfully!")
                    st.info("Changes will appear in Streamlit Cloud within 1-2 minutes")
                else:
                    st.error("❌ Sync failed. Check logs for details.")

        # Check sync status
        if st.button("📊 Check Status", use_container_width=True):
            syncer = AutoSync(verbose=False)
            if syncer.has_changes():
                st.warning("⚠️ Unsynced changes detected")
            else:
                st.success("✅ Everything synced")

    # Save configuration
    if st.button("💾 Save Settings", type="secondary"):
        new_config = {
            'auto_sync_enabled': auto_sync_enabled,
            'sync_mode': sync_mode,
            'sync_on_data_change': auto_sync_enabled and sync_mode == 'immediate',
            'daemon_check_interval': config.get('daemon_check_interval', 60),
            'files_to_sync': config.get('files_to_sync', ['investment_data.db', 'db_snapshot.json']),
            'git_remote': config.get('git_remote', 'origin'),
            'git_branch': config.get('git_branch', 'main'),
            'commit_message_template': config.get('commit_message_template', 'Auto-sync: Update investment data - {timestamp}'),
            'verbose_logging': verbose_logging,
            'notification_on_sync': notification_on_sync,
            'description': config.get('description', 'Auto-sync configuration for Investment Tracker')
        }

        save_sync_config(new_config)
        st.success("✅ Settings saved!")
        st.rerun()

    # Information section
    with st.expander("ℹ️ How Auto-Sync Works"):
        st.markdown("""
        ### Sync Process

        1. **Database Changes**: When you update investments on your laptop
        2. **Export to JSON**: Data is exported to `db_snapshot.json`
        3. **Git Commit**: Changes are committed to your local git repository
        4. **Push to GitHub**: Changes are pushed to your GitHub repository
        5. **Streamlit Cloud**: Detects changes and updates automatically (1-2 minutes)

        ### Sync Modes

        - **Immediate**: Syncs automatically after each change
        - **Manual**: Sync only when you click "Sync Now"
        - **Scheduled**: (Coming soon) Sync at regular intervals

        ### Important Notes

        - Requires active internet connection
        - GitHub authentication must be configured
        - Streamlit Cloud auto-detects changes from GitHub
        - Large datasets may take longer to sync
        """)

    # Sync status display
    st.markdown("---")
    st.markdown("### 📈 Sync Status")

    syncer = AutoSync(verbose=False)
    current_hash = syncer.get_db_hash()
    last_hash = syncer.get_last_sync_hash()

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        st.metric("Database Hash", f"{current_hash[:8] if current_hash else 'N/A'}...")

    with status_col2:
        st.metric("Last Sync Hash", f"{last_hash[:8] if last_hash else 'Never'}...")

    with status_col3:
        if current_hash and last_hash and current_hash == last_hash:
            st.metric("Status", "✅ Synced", delta=None)
        elif current_hash and last_hash:
            st.metric("Status", "⚠️ Pending", delta=None)
        else:
            st.metric("Status", "❓ Unknown", delta=None)
