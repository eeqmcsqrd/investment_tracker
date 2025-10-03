#!/usr/bin/env python3
"""
Bulk File and Directory Renamer
Recursively searches for files and directories containing a specified string
and replaces it with a new string in their names.
"""

import os
import sys
from pathlib import Path


def get_user_input():
    """Get directory path and replacement strings from user."""
    while True:
        directory = input("\nEnter the directory path: ").strip()
        if not directory:
            print("Please enter a valid directory path.")
            continue
        
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.exists():
            print(f"Directory '{dir_path}' does not exist.")
            continue
        if not dir_path.is_dir():
            print(f"'{dir_path}' is not a directory.")
            continue
        break
    
    while True:
        search_string = input("Enter the string to search for: ").strip()
        if search_string:
            break
        print("Search string cannot be empty.")
    
    replace_string = input("Enter the replacement string (can be empty): ").strip()
    
    return dir_path, search_string, replace_string


def find_items_to_rename(directory, search_string, replace_string):
    """Find all files and directories that contain the search string (case-insensitive)."""
    items_to_rename = []
    search_lower = search_string.lower()
    
    # First pass: collect all items (files and directories)
    all_items = []
    
    # Walk through directory tree to find all items
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        
        # Add files
        for file in files:
            if search_lower in file.lower():
                file_path = root_path / file
                # Preserve original case in replacement
                new_name = replace_case_insensitive(file, search_string, replace_string)
                all_items.append(('file', file_path, new_name, file_path.stat().st_mtime))
        
        # Add directories (including the current root if it matches)
        for dir_name in dirs:
            if search_lower in dir_name.lower():
                dir_path = root_path / dir_name
                new_name = replace_case_insensitive(dir_name, search_string, replace_string)
                all_items.append(('dir', dir_path, new_name, dir_path.stat().st_mtime))
    
    # Also check if any parent directories in the path contain the search string
    current_path = Path(directory)
    while current_path != current_path.parent:
        if search_lower in current_path.name.lower():
            new_name = replace_case_insensitive(current_path.name, search_string, replace_string)
            all_items.append(('dir', current_path, new_name, current_path.stat().st_mtime))
        current_path = current_path.parent
    
    # Sort by depth (deepest first) to avoid path conflicts during renaming
    # For directories, we want to rename the deepest ones first
    all_items.sort(key=lambda x: (x[1].parts.__len__(), x[0] == 'file'), reverse=True)
    
    return all_items


def replace_case_insensitive(text, search_string, replace_string):
    """Replace search_string in text while preserving case pattern where possible."""
    if not search_string:
        return text
    
    result = ""
    text_lower = text.lower()
    search_lower = search_string.lower()
    start = 0
    
    while True:
        # Find next occurrence (case-insensitive)
        pos = text_lower.find(search_lower, start)
        if pos == -1:
            # No more matches, add the rest of the string
            result += text[start:]
            break
        
        # Add the part before the match
        result += text[start:pos]
        
        # Add the replacement string
        result += replace_string
        
        # Move past this match
        start = pos + len(search_string)
    
    return result


def preview_changes(items_to_rename):
    """Show user what changes will be made."""
    if not items_to_rename:
        print("\nNo files or directories found containing the search string.")
        return False
    
    print(f"\nFound {len(items_to_rename)} items to rename:")
    print("-" * 80)
    
    for item_type, old_path, new_name, _ in items_to_rename:
        if old_path.name != new_name:  # Only show items that will actually change
            print(f"{item_type.upper()}: {old_path}")
            print(f"  -> {old_path.parent / new_name}")
            print()
    
    while True:
        confirm = input("Do you want to proceed with these changes? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no']:
            return False
        print("Please enter 'y' for yes or 'n' for no.")


def rename_items(items_to_rename):
    """Perform the actual renaming operations."""
    success_count = 0
    error_count = 0
    
    print("\nRenaming items...")
    
    for item_type, old_path, new_name, _ in items_to_rename:
        try:
            new_path = old_path.parent / new_name
            
            # Skip if the new name is the same as the old name
            if old_path.name == new_name:
                continue
                
            # Check if target already exists
            if new_path.exists() and new_path != old_path:
                print(f"⚠ Skipping {old_path}: Target '{new_name}' already exists")
                continue
                
            old_path.rename(new_path)
            print(f"✓ Renamed {item_type}: {old_path.name} -> {new_name}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error renaming {old_path}: {e}")
            error_count += 1
    
    print(f"\nOperation completed:")
    print(f"  Successfully renamed: {success_count}")
    print(f"  Errors: {error_count}")


def main():
    """Main function to run the renaming tool."""
    print("=== Bulk File and Directory Renamer ===")
    print("This tool will recursively rename files and directories")
    print("that contain a specified search string.\n")
    
    try:
        # Get user input
        directory, search_string, replace_string = get_user_input()
        
        print(f"\nSearching in: {directory}")
        print(f"Looking for: '{search_string}' (case-insensitive, anywhere in name)")
        print(f"Replacing with: '{replace_string}'")
        
        # Find items to rename
        items_to_rename = find_items_to_rename(directory, search_string, replace_string)
        
        # Preview and confirm changes
        if preview_changes(items_to_rename):
            rename_items(items_to_rename)
        else:
            print("Operation cancelled.")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()