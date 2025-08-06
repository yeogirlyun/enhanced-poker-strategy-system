#!/usr/bin/env python3
"""
Test About Dialog

Tests the custom About dialog to ensure it shows the correct app name.
"""

import tkinter as tk
from tkinter import messagebox
from app_config import get_app_full_name, get_app_name

def show_custom_about():
    """Show custom about dialog."""
    app_name = get_app_name()
    full_name = get_app_full_name()
    
    about_text = f"{full_name}\n\n"
    about_text += "A comprehensive tool for developing and testing poker strategies.\n\n"
    about_text += "Features:\n"
    about_text += "• Hand strength tier management\n"
    about_text += "• Visual hand grid with tier highlighting\n"
    about_text += "• Decision table editing\n"
    about_text += "• Strategy optimization tools\n"
    about_text += "• Practice session integration\n"
    about_text += "• Professional theme and status bar\n"
    about_text += "• Enhanced sound system\n"
    about_text += "• Voice announcements\n\n"
    about_text += f"Version 3.0 - {app_name}"
    
    messagebox.showinfo(f"About {app_name}", about_text)

def main():
    """Test the About dialog."""
    print("🎯 TESTING ABOUT DIALOG")
    print("=" * 40)
    
    app_name = get_app_name()
    full_name = get_app_full_name()
    
    print(f"App Name: {app_name}")
    print(f"Full Name: {full_name}")
    
    # Create window
    root = tk.Tk()
    root.title(full_name)
    root.geometry("400x200")
    
    # Add content
    label = tk.Label(root, text=f"Testing About Dialog", font=("Arial", 16))
    label.pack(pady=30)
    
    info_label = tk.Label(root, text="Click the button to test the custom About dialog", 
                         font=("Arial", 12), wraplength=350)
    info_label.pack(pady=20)
    
    about_button = tk.Button(root, text="Show About Dialog", command=show_custom_about)
    about_button.pack(pady=10)
    
    print("✅ Window created")
    print("✅ Click 'Show About Dialog' to test")
    print("✅ The About dialog should show 'About PokerPro Trainer'")
    
    root.mainloop()

if __name__ == "__main__":
    main() 