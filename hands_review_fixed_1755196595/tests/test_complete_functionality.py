#!/usr/bin/env python3
"""
Complete functionality test for the Hands Review tab.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
import tkinter as tk
from tkinter import ttk
from backend.ui.components.hands_review_panel_unified import UnifiedHandsReviewPanel
from backend.core.session_logger import SessionLogger

def test_complete_functionality():
    """Test the complete Hands Review functionality end-to-end."""
    print("🧪 COMPLETE FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Create a minimal GUI window
    root = tk.Tk()
    root.title("Complete Functionality Test")
    root.geometry("1200x800")
    root.withdraw()  # Hide window for automated testing
    
    # Create logger
    logger = SessionLogger()
    
    # Create the hands review panel
    panel = UnifiedHandsReviewPanel(root, logger)
    panel.pack(fill="both", expand=True)
    
    print("✅ Panel created")
    root.update()
    
    print(f"📊 Available hands: {len(panel.available_hands)}")
    
    if panel.available_hands:
        # Select and load first hand
        panel.hand_listbox.selection_set(0)
        panel.hand_listbox.activate(0)
        panel.current_hand_index = 0
        
        first_hand = panel.available_hands[0]
        hand_id = first_hand.get('hand_id', 'unknown')
        print(f"🎯 Testing with hand: {hand_id}")
        
        # Load the hand
        try:
            panel._load_selected_hand()
            print("✅ Hand loaded successfully")
            
            print(f"🎮 Session active: {panel.session_active}")
            print(f"🎮 Has widget: {panel.hands_review_widget is not None}")
            
            if panel.session_active and panel.hands_review_widget:
                print("\n▶️  Testing Next button functionality...")
                
                # Test multiple Next button clicks
                actions_executed = 0
                max_actions = 10  # Limit to prevent infinite loops
                
                for i in range(max_actions):
                    try:
                        print(f"   Click {i+1}...")
                        
                        # Call the Next button method directly
                        panel._next_action()
                        
                        # Update GUI
                        root.update()
                        
                        # Check if session is still active
                        if not panel.session_active:
                            print(f"   ✅ Session completed after {i+1} actions")
                            actions_executed = i + 1
                            break
                        else:
                            print(f"   ✅ Action {i+1} executed successfully")
                            actions_executed = i + 1
                            
                    except Exception as e:
                        print(f"   ❌ Error on action {i+1}: {e}")
                        break
                
                print(f"\n📊 Test Results:")
                print(f"   Actions executed: {actions_executed}")
                print(f"   Session completed: {not panel.session_active}")
                
                if actions_executed > 0:
                    print("✅ Next button functionality: WORKING")
                else:
                    print("❌ Next button functionality: FAILED")
                    
            else:
                print("❌ Session or widget not properly initialized")
                
        except Exception as e:
            print(f"❌ Error loading hand: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    else:
        print("❌ No hands available for testing")
    
    root.destroy()
    print(f"\n🎯 Complete functionality test finished")

if __name__ == "__main__":
    test_complete_functionality()
