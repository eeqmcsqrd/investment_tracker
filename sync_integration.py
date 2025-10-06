"""
Sync Integration Module
Provides hooks for auto-syncing data changes throughout the application
"""

import json
import os
from pathlib import Path
from typing import Optional

# Configuration
CONFIG_FILE = 'sync_config.json'

def load_sync_config() -> dict:
    """Load sync configuration from file"""
    config_path = Path(__file__).parent / CONFIG_FILE
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        'auto_sync_enabled': False,
        'sync_mode': 'manual',
        'sync_on_data_change': False
    }

def is_auto_sync_enabled() -> bool:
    """Check if auto-sync is enabled"""
    config = load_sync_config()
    return config.get('auto_sync_enabled', False)

def trigger_sync_if_enabled(verbose: bool = False) -> bool:
    """
    Trigger sync if auto-sync is enabled
    Returns True if sync was triggered, False otherwise
    """
    if not is_auto_sync_enabled():
        return False

    try:
        # Import here to avoid circular dependencies
        from auto_sync import sync_to_github

        # Run sync in background (non-blocking)
        import threading
        sync_thread = threading.Thread(
            target=sync_to_github,
            args=(verbose,),
            daemon=True
        )
        sync_thread.start()
        return True
    except Exception as e:
        if verbose:
            print(f"Sync trigger failed: {e}")
        return False

def sync_hook_decorator(func):
    """
    Decorator to add auto-sync after data modifications
    Usage: @sync_hook_decorator
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Trigger sync after successful operation
        if result:  # Only sync if operation succeeded
            trigger_sync_if_enabled(verbose=False)

        return result

    return wrapper
