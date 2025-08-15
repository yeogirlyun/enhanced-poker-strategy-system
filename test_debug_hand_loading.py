#!/usr/bin/env python3
"""
Debug test to see exactly what happens during hand loading.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
import tkinter as tk
from tkinter import ttk
from backend.ui.components.hands_review_panel_unified import UnifiedHandsReviewPanel
from backend.core.session_logger import SessionLogger

def test_debug_hand_loading():
    """Debug the hand loading process step by step."""
    print("🔍 DEBUG HAND LOADING")
    print("=" * 50)
    
    # Create a minimal GUI window
    root = tk.Tk()
    root.title("Debug Hand Loading")
    root.geometry("1200x800")
    root.withdraw()  # Hide the window
    
    # Create logger
    logger = SessionLogger()
    
    # Create the hands review panel
    panel = UnifiedHandsReviewPanel(root, logger)
    panel.pack(fill="both", expand=True)
    
    print("✅ Panel created")
    
    # Wait for initialization
    root.update()
    
    print(f"📊 Available hands: {len(panel.available_hands)}")
    
    if panel.available_hands:
        first_hand = panel.available_hands[0]
        print(f"🎯 First hand: {first_hand.get('hand_id', 'unknown')}")
        print(f"   Keys: {list(first_hand.keys())}")
        
        # Manually call the load process step by step
        try:
            # Simulate hand selection
            panel.hand_listbox.selection_set(0)
            panel.hand_listbox.activate(0)
            panel.current_hand_index = 0
            
            print("✅ Hand selected in listbox")
            
            # Get the selected hand data
            selection = panel.hand_listbox.curselection()
            print(f"📋 Selection: {selection}")
            
            if selection:
                hand_index = selection[0]
                hand_to_review = panel.available_hands[hand_index]
                hand_id = hand_to_review.get('hand_id') or hand_to_review.get('id', 'Unknown')
                
                print(f"🎯 Hand to review: {hand_id}")
                print(f"   Has hand_model: {'hand_model' in hand_to_review}")
                
                # Check if conversion worked
                if 'hand_model' not in hand_to_review:
                    print("❌ No hand_model in hand data - conversion may have failed")
                else:
                    print("✅ Hand model found")
                
                # Call the actual load method
                print("📥 Calling _load_selected_hand()...")
                
                # Temporarily capture the session creation
                original_hands_review_session = panel.hands_review_session
                
                try:
                    panel._load_selected_hand()
                    print("✅ _load_selected_hand completed")
                    
                    # Check session state
                    print(f"🎮 Session active: {panel.session_active}")
                    print(f"🎮 Has session: {panel.hands_review_session is not None}")
                    
                    if panel.hands_review_session:
                        print(f"🎮 Session type: {type(panel.hands_review_session)}")
                        print(f"🎮 Session state: {getattr(panel.hands_review_session, 'session_active', 'unknown')}")
                    
                    if panel.hands_review_widget:
                        print(f"🖼️  Has widget: {type(panel.hands_review_widget)}")
                        
                except Exception as e:
                    print(f"❌ Error in _load_selected_hand: {e}")
                    import traceback
                    print(f"   Traceback: {traceback.format_exc()}")
            else:
                print("❌ No selection in listbox")
                
        except Exception as e:
            print(f"❌ Error during debug: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    else:
        print("❌ No hands available")
    
    root.destroy()
    print(f"\n🎯 Debug completed")

if __name__ == "__main__":
    test_debug_hand_loading()
