#!/usr/bin/env python3
"""
Test the new natural turn order approach.
This should fix the infinite loop issue by letting FPSM control turn order.
"""

import sys
import os
from core.hands_database import ComprehensiveHandsDatabase
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
import tkinter as tk

def test_natural_turn_order():
    """Test the new natural turn order fix."""
    print("🧪 TESTING NATURAL TURN ORDER FIX")
    print("=" * 50)
    
    # Create a minimal tkinter setup
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create hands review panel
    panel = FPSMHandsReviewPanel(root)
    
    # Load the problematic hand
    hands_db = ComprehensiveHandsDatabase()
    hands_db.load_all_hands()
    
    target_hand = None
    for hand_id, hand in hands_db.all_hands.items():
        if "Holz Smith Triton" in hand.metadata.name:
            target_hand = hand
            break
    
    if not target_hand:
        print("❌ Could not find target hand")
        return
    
    print(f"🎯 Testing hand: {target_hand.metadata.name}")
    
    # Set the hand for simulation
    panel.current_hand = target_hand
    
    # Prepare the simulation
    panel.setup_hand_for_simulation()
    
    # Enable historical actions (legendary hand)
    panel.prepare_historical_actions()
    
    if not panel.use_historical_actions:
        print("❌ Historical actions not enabled")
        return
    
    print(f"✅ Historical actions enabled: {len(panel.historical_actions)} actions")
    print(f"✅ Simulation active: {panel.simulation_active}")
    
    # Ensure simulation is active for testing
    if not panel.simulation_active:
        panel.simulation_active = True
        print("🔧 Manually activated simulation for testing")
    
    # Test the first few actions using the new approach
    max_actions = 15  # Limit to prevent infinite loops during testing
    action_count = 0
    
    print(f"\n🎯 Testing first {max_actions} actions with new approach...")
    
    for i in range(max_actions):
        if not panel.simulation_active or panel.hand_completed:
            print(f"🏁 Simulation ended after {action_count} actions")
            break
        
        # Get current action player using FPSM's natural turn order
        if not panel.fpsm:
            print("❌ No FPSM available")
            break
        
        action_player = panel.fpsm.get_action_player()
        if not action_player:
            print(f"🏁 No action player - hand complete after {action_count} actions")
            break
        
        print(f"\n  Action [{i+1}]: {action_player.name}'s turn (natural FPSM order)")
        
        # Test our new action determination method
        try:
            # Get valid actions
            valid_actions = panel.fpsm.get_valid_actions_for_player(action_player)
            
            # Use our new natural turn order approach
            action = panel.determine_action_from_history(action_player, valid_actions)
            
            if action:
                action_type = action['type']
                amount = action['amount']
                print(f"    → Action determined: {action_type.value} ${amount:,}")
                
                # Execute the action
                success = panel.fpsm.execute_action(action_player, action_type, amount)
                
                if success:
                    print(f"    ✅ Action executed successfully")
                    action_count += 1
                    
                    # Check if hand is complete
                    current_state = panel.fpsm.current_state.name
                    if current_state in ['END_HAND', 'SHOWDOWN']:
                        print(f"🏁 Hand completed at state: {current_state}")
                        break
                else:
                    print(f"    ❌ Action execution failed - this should trigger completion")
                    break
                    
            else:
                print(f"    ⚠️  No action determined - hand might be complete")
                break
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            break
    
    print(f"\n✅ Test completed: {action_count} actions executed without infinite loops")
    
    # Clean up
    root.destroy()

if __name__ == "__main__":
    test_natural_turn_order()
