#!/usr/bin/env python3
"""
Debug the PHH parser to see why it's not reading the actions correctly.
"""

import sys
import os
from core.hands_database import ComprehensiveHandsDatabase

def debug_phh_parser():
    """Debug PHH parsing for the Holz-Smith hand."""
    print("🔍 DEBUGGING PHH PARSER")
    print("=" * 50)
    
    # Load the hands database
    hands_db = ComprehensiveHandsDatabase()
    hands_db.load_all_hands()
    
    # Find the Holz-Smith hand
    target_hand = None
    for hand_id, hand in hands_db.all_hands.items():
        if "Holz Smith Triton" in hand.metadata.name:
            target_hand = hand
            break
    
    if not target_hand:
        print("❌ Failed to find target hand")
        return
        
    print(f"🎯 Found target hand: {target_hand.metadata.name}")
    print(f"📊 Hand ID: {target_hand.metadata.id}")
    print(f"📋 Source: {target_hand.metadata.source_file}")
    
    # Debug the actions parsing
    print(f"\n🎴 Actions Debug:")
    print(f"  Type: {type(target_hand.actions)}")
    print(f"  Length: {len(target_hand.actions) if target_hand.actions else 'None'}")
    
    if target_hand.actions:
        print(f"  Raw actions data:")
        for i, action in enumerate(target_hand.actions):
            print(f"    [{i}] {type(action).__name__}: {action}")
    else:
        print(f"  ❌ No actions found!")
        
    # Let's also manually check the PHH loader
    print(f"\n🔍 Debugging PHH Loader directly...")
    legendary_loader = hands_db.legendary_loader
    
    # Check if the loader has the raw data
    print(f"📂 Legendary loader loaded {len(legendary_loader.hands)} hands")
    
    # Find the specific hand in the loader
    target_loader_hand = None
    for hand in legendary_loader.hands:
        if hasattr(hand, 'metadata') and "Holz Smith Triton" in hand.metadata.name:
            target_loader_hand = hand
            break
            
    if target_loader_hand:
        print(f"✅ Found hand in loader: {target_loader_hand.metadata.name}")
        print(f"📋 Actions in loader:")
        actions = target_loader_hand.actions
        print(f"  Type: {type(actions)}")
        print(f"  Length: {len(actions) if actions else 'None'}")
        if actions:
            print(f"  Sample actions:")
            for i, action in enumerate(list(actions.items())[:10] if isinstance(actions, dict) else actions[:10]):  # Show first 10
                print(f"    [{i}] {action}")
        else:
            print(f"  ❌ No actions in loader either!")
    else:
        print(f"❌ Hand not found in loader")
        
    # Also check what happens during the parsing process
    print(f"\n🔧 Manual parsing test...")
    
    # Let's look at the raw PHH content for this hand
    phh_path = "data/legendary_hands.phh"
    try:
        with open(phh_path, 'r') as f:
            content = f.read()
            
        # Find the section for the Holz-Smith hand
        if "Holz Smith Triton" in content:
            print(f"✅ Found hand in PHH file")
            
            # Extract the relevant section
            start = content.find("# Hand GEN-036 — Holz Smith Triton")
            if start == -1:
                start = content.find("Holz Smith Triton")
            end = content.find("# Hand GEN-037", start)
            if end == -1:
                end = start + 2000  # Get next 2000 chars
                
            hand_section = content[start:end]
            
            # Count actions in the raw text
            action_count = hand_section.count("[[actions.")
            print(f"📊 Raw action count in PHH: {action_count}")
            
            # Show sample actions from raw text
            print(f"📋 Sample raw actions:")
            lines = hand_section.split('\n')
            for i, line in enumerate(lines):
                if '[[actions.' in line:
                    # Show this line and next few
                    for j in range(5):
                        if i+j < len(lines):
                            print(f"    {lines[i+j]}")
                    print(f"    ...")
                    break
        else:
            print(f"❌ Hand not found in PHH file")
            
    except Exception as e:
        print(f"❌ Error reading PHH file: {e}")

if __name__ == "__main__":
    debug_phh_parser()
