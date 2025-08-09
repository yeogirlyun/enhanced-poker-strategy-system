#!/usr/bin/env python3
"""
Debug script to understand exactly what's happening with actor mapping.
"""

import sys
import os
import tkinter as tk

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

def debug_first_hand():
    """Debug the first hand to understand the mapping issue."""
    print("🔍 ACTOR MAPPING DEBUG")
    print("=" * 50)
    
    try:
        # Create minimal UI
        root = tk.Tk()
        root.geometry("1x1")
        root.withdraw()
        root.update_idletasks()
        
        # Create panel
        panel = FPSMHandsReviewPanel(root)
        root.update_idletasks()
        
        if not hasattr(panel, 'legendary_hands') or len(panel.legendary_hands) == 0:
            print("❌ No legendary hands found!")
            return
        
        # Get first hand
        hand = panel.legendary_hands[0]
        hand_id = getattr(hand.metadata, 'id', 'Unknown')
        
        print(f"📊 HAND: {hand_id}")
        print(f"Players in PHH data: {len(hand.players)}")
        
        # Show PHH data
        print(f"\n📋 PHH PLAYER DATA:")
        for i, player in enumerate(hand.players):
            seat = player.get('seat', 'Unknown')
            name = player.get('name', 'Unknown')
            print(f"   PHH Player {i}: Seat {seat}, Name: {name}")
        
        # Show historical actions
        print(f"\n📋 HISTORICAL ACTIONS:")
        if hasattr(hand, 'actions'):
            actions_list = []
            for street_name, street_actions in hand.actions.items():
                for action in street_actions:
                    actor = action.get('actor', 'Unknown')
                    action_type = action.get('type', 'Unknown')
                    actions_list.append(f"{street_name}: Actor {actor} {action_type}")
            
            for i, action in enumerate(actions_list[:10]):  # Show first 10 actions
                print(f"   Action {i}: {action}")
        
        # Set up the hand for simulation
        panel.current_hand = hand
        panel.current_hand_index = 0
        
        print(f"\n🎯 SETTING UP SIMULATION...")
        panel.setup_hand_for_simulation()
        
        if panel.fpsm:
            fpsm_players = panel.fpsm.game_state.players
            print(f"\n📋 FPSM PLAYERS ({len(fpsm_players)} total):")
            for i, fpsm_player in enumerate(fpsm_players):
                print(f"   FPSM Player {i}: {fpsm_player.name}")
        
        # Show actor mapping
        print(f"\n🎯 ACTOR MAPPING:")
        panel.build_actor_mapping()
        mapping = panel.fpsm_to_actor_mapping
        for fpsm_idx, actor_id in mapping.items():
            fpsm_name = fpsm_players[fpsm_idx].name if fpsm_idx < len(fpsm_players) else "Unknown"
            print(f"   FPSM Player {fpsm_idx} ({fpsm_name}) → Actor {actor_id}")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_first_hand()
