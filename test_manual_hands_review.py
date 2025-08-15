#!/usr/bin/env python3
"""
Manual test script that simulates a user clicking through the Hands Review tab.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
import tkinter as tk
from tkinter import ttk
from backend.ui.components.hands_review_panel_unified import UnifiedHandsReviewPanel
from backend.core.session_logger import SessionLogger

def test_manual_hands_review():
    """Test the hands review tab like a user would."""
    print("🧪 MANUAL HANDS REVIEW TEST")
    print("=" * 50)
    
    # Create a minimal GUI window
    root = tk.Tk()
    root.title("Hands Review Manual Test")
    root.geometry("1200x800")
    
    # Create logger
    logger = SessionLogger()
    
    # Create the hands review panel
    panel = UnifiedHandsReviewPanel(root, logger)
    panel.pack(fill="both", expand=True)
    
    print("✅ Hands Review panel created")
    
    # Wait a moment for initialization
    root.update()
    
    # Check if hands are loaded
    print(f"📊 Available hands: {len(panel.available_hands)}")
    
    if panel.available_hands:
        # Simulate selecting the first hand
        panel.hand_listbox.selection_set(0)
        panel.hand_listbox.activate(0)
        print(f"✅ Selected first hand: {panel.available_hands[0].get('hand_id', 'unknown')}")
        
        # Simulate clicking "Load Selected Hand"
        try:
            panel._load_selected_hand()
            print("✅ Load selected hand called")
            
            # Check if session is active
            print(f"🎮 Session active: {panel.session_active}")
            
            # Test Next button functionality
            if panel.session_active:
                print("\n▶️  Testing Next button clicks...")
                for i in range(5):
                    try:
                        panel._next_action()
                        print(f"   Click {i+1}: ✅ Executed")
                        root.update()  # Process GUI updates
                    except Exception as e:
                        print(f"   Click {i+1}: ❌ Error: {e}")
                        break
                    
                    # Check if session is still active
                    if not panel.session_active:
                        print(f"   Session completed after {i+1} clicks")
                        break
            else:
                print("❌ Session not active - cannot test Next button")
                
        except Exception as e:
            print(f"❌ Error loading hand: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    else:
        print("❌ No hands available for testing")
    
    # Don't show GUI for automated testing
    root.destroy()
    
    print(f"\n🎯 Manual test completed")

if __name__ == "__main__":
    test_manual_hands_review()
