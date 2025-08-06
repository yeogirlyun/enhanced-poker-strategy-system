#!/usr/bin/env python3
"""
Test App Title

Simple test to verify the app title is working correctly.
"""

import tkinter as tk
from app_config import get_app_full_name

def main():
    """Test the app title."""
    print("🎯 TESTING APP TITLE")
    print("=" * 30)
    
    # Get the full app name
    app_title = get_app_full_name()
    print(f"App Title: {app_title}")
    
    # Create a simple window to test
    root = tk.Tk()
    root.title(app_title)
    root.geometry("400x200")
    
    # Add a label
    label = tk.Label(root, text=f"Testing: {app_title}", font=("Arial", 14))
    label.pack(pady=50)
    
    print("✅ Window created with title:", app_title)
    print("✅ If you see 'PokerPro Trainer' in the title bar, it's working!")
    
    root.mainloop()

if __name__ == "__main__":
    main() 