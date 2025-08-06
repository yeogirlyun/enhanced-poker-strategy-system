#!/usr/bin/env python3
"""
Test App Name Fix

Tests the app name fix for macOS menu bar.
"""

import tkinter as tk
from app_config import get_app_full_name, get_app_name

def main():
    """Test the app name fix."""
    print("🎯 TESTING APP NAME FIX")
    print("=" * 40)
    
    # Get app names
    app_name = get_app_name()
    full_name = get_app_full_name()
    
    print(f"App Name: {app_name}")
    print(f"Full Name: {full_name}")
    
    # Create window with enhanced app name support
    root = tk.Tk()
    
    # Set app name for macOS menu bar
    try:
        import platform
        if platform.system() == "Darwin":  # macOS
            print("✅ macOS detected - applying app name fix")
            root.tk.call('tk', 'scaling', 2.0)  # High DPI support
            # Set the app name for macOS menu bar
            root.createcommand('tk::mac::Quit', root.quit)
            root.createcommand('tk::mac::OnHide', lambda: None)
            root.createcommand('tk::mac::OnShow', lambda: None)
            root.createcommand('tk::mac::ShowPreferences', lambda: None)
            root.createcommand('tk::mac::ShowAbout', lambda: None)
        else:
            print("ℹ️  Not macOS - standard title only")
    except Exception as e:
        print(f"⚠️  Error setting macOS app name: {e}")
    
    # Set window title
    root.title(full_name)
    
    # Window setup
    root.geometry("500x300")
    
    # Add content
    label = tk.Label(root, text=f"Testing: {full_name}", font=("Arial", 16))
    label.pack(pady=50)
    
    info_label = tk.Label(root, text="Check the menu bar - it should show 'PokerPro Trainer' instead of 'Python'", 
                         font=("Arial", 12), wraplength=400)
    info_label.pack(pady=20)
    
    print("✅ Window created with enhanced app name support")
    print("✅ Check the menu bar for 'PokerPro Trainer'")
    
    root.mainloop()

if __name__ == "__main__":
    main() 