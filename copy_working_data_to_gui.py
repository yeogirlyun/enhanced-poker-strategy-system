#!/usr/bin/env python3
"""
Copy my working test data to the GUI data location so the GUI uses the known-working format.
"""

import json
import shutil

def copy_working_data():
    """Copy working test data to GUI location."""
    print("🔄 COPYING WORKING DATA TO GUI LOCATION")
    
    # Load my working test data
    with open('cycle_test_hand.json', 'r') as f:
        working_hand = json.load(f)
    
    print(f"✅ Loaded working hand: {working_hand.get('id')}")
    
    # Create the GUI format (with hands array)
    gui_format = {
        "metadata": {
            "generated_at": "2025-08-15T02:20:00.000000",
            "total_hands": 1,
            "format": "working_test_hands",
            "version": "1.0"
        },
        "hands": [working_hand]
    }
    
    # Write to GUI data location
    gui_path = "/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json"
    backup_path = "/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json.backup"
    
    # Backup original
    shutil.copy(gui_path, backup_path)
    print(f"✅ Backed up original to: {backup_path}")
    
    # Write working data
    with open(gui_path, 'w') as f:
        json.dump(gui_format, f, indent=2)
    
    print(f"✅ Wrote working data to: {gui_path}")
    print(f"   Now the GUI will use the known-working hand format")

if __name__ == "__main__":
    copy_working_data()
