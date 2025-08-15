#!/usr/bin/env python3
"""
Test the new integrated hands review panel with actual poker table widget.
"""

import sys
import os
sys.path.append('backend')

import tkinter as tk
from backend.ui.components.hands_review_panel_unified import UnifiedHandsReviewPanel
from backend.core.session_logger import SessionLogger

def test_integrated_hands_review():
    """Test the integrated hands review panel with poker table."""
    print("🧪 Testing Integrated Hands Review Panel with Poker Table")
    print("=" * 60)
    
    # Create session logger
    logger = SessionLogger("test_integrated_hands_review")
    print("✅ Session logger created")
    
    # Create root window
    root = tk.Tk()
    root.title("Integrated Hands Review Test")
    root.geometry("1400x900")  # Larger window for poker table
    
    try:
        # Create panel
        print("📋 Creating UnifiedHandsReviewPanel with poker table integration...")
        panel = UnifiedHandsReviewPanel(root, session_logger=logger)
        panel.pack(fill="both", expand=True)
        print("✅ Panel created successfully")
        
        # Check hands loaded
        hands_count = len(panel.available_hands)
        print(f"📊 Found {hands_count} hands available")
        
        if hands_count > 0:
            print("🎯 Panel ready for testing!")
            print("👉 Instructions:")
            print("   1. Select a hand from the left panel")
            print("   2. Click 'Load Selected Hand'")
            print("   3. You should see the full poker table appear")
            print("   4. Click 'Next' to step through actions")
            print("   5. Observe cards, chips, and game state updates")
            
            # Test font sizing
            print("🔤 Testing font size control...")
            panel.update_font_size(12)  # Test font update
            print("✅ Font sizing works")
            
        else:
            print("⚠️ No hands available for testing")
        
        print("\n🎉 Integrated test setup complete!")
        print("👉 Use the GUI to test poker table integration")
        print("   Close the window when done testing")
        
        # Run GUI for manual testing
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_integrated_hands_review()
