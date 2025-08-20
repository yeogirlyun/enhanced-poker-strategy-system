#!/usr/bin/env python3
"""
Test MVU Implementation
Simple test to verify our MVU poker table architecture works
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUHandsReviewTab


def main():
    """Test the MVU implementation"""
    print("🧪 Testing MVU Implementation...")
    
    # Create root window
    root = tk.Tk()
    root.title("MVU Poker Table Test")
    root.geometry("1200x800")
    
    # Create a simple services mock
    class MockServices:
        def __init__(self):
            self._services = {}
        
        def get_app(self, name):
            return self._services.get(name)
        
        def provide_app(self, name, service):
            self._services[name] = service
    
    services = MockServices()
    
    # Create MVU Hands Review Tab
    try:
        review_tab = MVUHandsReviewTab(root, services=services)
        review_tab.pack(fill="both", expand=True)
        
        print("✅ MVU HandsReviewTab created successfully!")
        print("🎮 Use the UI to test the MVU architecture")
        
        # Add cleanup on close
        def on_closing():
            review_tab.dispose()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the UI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error creating MVU tab: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
