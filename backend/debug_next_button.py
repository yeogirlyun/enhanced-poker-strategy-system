#!/usr/bin/env python3
"""
Debug Next Button Issues
========================

This script will help debug why the Next button isn't working by:
1. Loading a hand
2. Checking if actions are properly loaded
3. Testing the get_current_action method
4. Simulating what happens when Next is pressed
"""

import sys
import os
import tkinter as tk

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.json_hands_database import JSONHandsDatabase
from ui.components.enhanced_fpsm_hands_review_panel import EnhancedFPSMHandsReviewPanel

class NextButtonDebugger:
    def __init__(self):
        self.panel = None
        
    def debug_next_button(self):
        """Debug the next button functionality."""
        print("🔍 Debugging Next Button Issues")
        print("=" * 40)
        
        # Create GUI
        root = tk.Tk()
        root.title("Next Button Debug")
        root.geometry("1400x900")
        
        self.panel = EnhancedFPSMHandsReviewPanel(root)
        self.panel.pack(fill=tk.BOTH, expand=True)
        
        # Wait for GUI to initialize
        root.update()
        
        # Load a specific hand for testing
        self.debug_hand_loading()
        
        # Override the next_action method to add debug info
        self.override_next_action()
        
        print("\n🎯 GUI ready for testing")
        print("📋 Instructions:")
        print("   1. Select hand GEN-001 from the list")
        print("   2. Click 'Load Selected Hand'")  
        print("   3. Click 'Next' - watch console for debug output")
        print("   4. Close window when done")
        
        root.mainloop()
        
    def debug_hand_loading(self):
        """Load a hand and check if actions are properly initialized."""
        try:
            # Load database
            db = JSONHandsDatabase("data/legendary_hands_complete_130_fixed.json")
            hands = db.get_hands()
            
            # Find GEN-001
            test_hand = None
            for hand in hands:
                if hand.metadata.hand_id == "GEN-001":
                    test_hand = hand
                    break
                    
            if not test_hand:
                print("❌ Could not find GEN-001 for testing")
                return
                
            print(f"✅ Found test hand: {test_hand.metadata.hand_id}")
            print(f"📝 Description: {test_hand.metadata.description}")
            
            # Check actions structure
            actions = test_hand.parsed_hand.actions
            print(f"📊 Total actions in parsed_hand: {len(actions)}")
            
            # Check if actions are organized by street
            streets = set()
            for action in actions:
                street = action.get('street', 'unknown')
                streets.add(street)
                
            print(f"🎯 Streets with actions: {sorted(streets)}")
            
            # Show first few actions
            print("\n🎮 First 5 actions:")
            for i, action in enumerate(actions[:5]):
                player_name = action.get('player_name', 'Unknown')
                action_type = action.get('action_type', 'Unknown')
                amount = action.get('amount', 0)
                street = action.get('street', 'Unknown')
                print(f"   {i+1}. {player_name} {action_type} {amount} on {street}")
                
        except Exception as e:
            print(f"💥 Error loading hand: {e}")
            import traceback
            traceback.print_exc()
            
    def override_next_action(self):
        """Override the next_action method to add debug output."""
        original_next_action = self.panel.next_action
        original_get_current_action = self.panel.get_current_action
        original_execute_action = self.panel.execute_action
        
        def debug_get_current_action():
            """Debug wrapper for get_current_action."""
            print(f"\n🔍 DEBUG get_current_action:")
            print(f"   current_action_index: {self.panel.current_action_index}")
            print(f"   hand_actions keys: {list(self.panel.hand_actions.keys()) if hasattr(self.panel, 'hand_actions') else 'None'}")
            
            if hasattr(self.panel, 'hand_actions'):
                total_actions = sum(len(actions) for actions in self.panel.hand_actions.values())
                print(f"   total actions available: {total_actions}")
                
                # Show actions by street
                for street, actions in self.panel.hand_actions.items():
                    print(f"   {street}: {len(actions)} actions")
                    
            result = original_get_current_action()
            print(f"   → Returned: {result}")
            return result
            
        def debug_execute_action(*args, **kwargs):
            """Debug wrapper for execute_action."""
            print(f"\n🎮 DEBUG execute_action called with:")
            print(f"   args: {args}")
            print(f"   kwargs: {kwargs}")
            
            result = original_execute_action(*args, **kwargs)
            print(f"   → execute_action completed")
            return result
            
        def debug_next_action():
            """Debug wrapper for next_action."""
            print(f"\n▶️  NEXT BUTTON PRESSED")
            print(f"   Current state:")
            print(f"   - current_action_index: {getattr(self.panel, 'current_action_index', 'Not set')}")
            print(f"   - hand_actions exists: {hasattr(self.panel, 'hand_actions')}")
            print(f"   - fpsm exists: {hasattr(self.panel, 'fpsm') and self.panel.fpsm is not None}")
            
            if not hasattr(self.panel, 'hand_actions') or not self.panel.hand_actions:
                print("❌ No hand_actions found - hand might not be loaded properly")
                return
                
            print("✅ Calling original next_action...")
            result = original_next_action()
            print(f"   → next_action completed")
            return result
            
        # Replace methods
        self.panel.next_action = debug_next_action
        self.panel.get_current_action = debug_get_current_action  
        self.panel.execute_action = debug_execute_action

def main():
    """Run the next button debugger."""
    debugger = NextButtonDebugger()
    debugger.debug_next_button()

if __name__ == "__main__":
    main()
