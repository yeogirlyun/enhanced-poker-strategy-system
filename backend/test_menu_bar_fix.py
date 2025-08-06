#!/usr/bin/env python3
"""
Test Menu Bar Fix

Tests the menu bar app name fix for macOS.
"""

import tkinter as tk
from app_config import get_app_full_name, get_app_name

def main():
    """Test the menu bar app name fix."""
    print("🎯 TESTING MENU BAR FIX")
    print("=" * 40)
    
    # Get app names
    app_name = get_app_name()
    full_name = get_app_full_name()
    
    print(f"App Name: {app_name}")
    print(f"Full Name: {full_name}")
    
    # Create window with enhanced app name support
    root = tk.Tk()
    
    # Set process name for macOS before creating the window
    try:
        import platform
        if platform.system() == "Darwin":  # macOS
            import sys
            # Try to set the process name
            try:
                import setproctitle
                setproctitle.setproctitle("PokerPro Trainer")
                print("✅ Set process name to 'PokerPro Trainer'")
            except ImportError:
                # Fallback: try to set argv[0]
                if len(sys.argv) > 0:
                    sys.argv[0] = "PokerPro Trainer"
                print("✅ Modified argv[0]")
    except Exception as e:
        print(f"⚠️  Error setting process name: {e}")
    
    # Set app name for macOS menu bar
    try:
        import platform
        if platform.system() == "Darwin":  # macOS
            print("✅ macOS detected - applying menu bar fix")
            root.tk.call('tk', 'scaling', 2.0)  # High DPI support
            # Set the app name for macOS menu bar
            root.createcommand('tk::mac::Quit', root.quit)
            root.createcommand('tk::mac::OnHide', lambda: None)
            root.createcommand('tk::mac::OnShow', lambda: None)
            root.createcommand('tk::mac::ShowPreferences', lambda: None)
            # Override the system About dialog
            root.createcommand('tk::mac::ShowAbout', lambda: show_about())
            
            # Force menu bar to show our app name
            try:
                root.tk.call('tk', 'mac::setAppName', 'PokerPro Trainer')
                print("✅ Set menu bar app name to 'PokerPro Trainer'")
            except:
                print("⚠️  Could not set menu bar app name")
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
    label.pack(pady=30)
    
    info_label = tk.Label(root, text="Check the menu bar - it should show 'PokerPro Trainer' instead of 'Python'", 
                         font=("Arial", 12), wraplength=400)
    info_label.pack(pady=20)
    
    about_button = tk.Button(root, text="Test About Dialog", command=lambda: show_about())
    about_button.pack(pady=10)
    
    print("✅ Window created with enhanced menu bar support")
    print("✅ Check the menu bar for 'PokerPro Trainer'")
    print("✅ Click 'Test About Dialog' to test the About dialog")
    
    def show_about():
        """Show custom about dialog."""
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
        
        tk.messagebox.showinfo(f"About {app_name}", about_text)
    
    root.mainloop()

if __name__ == "__main__":
    main() 