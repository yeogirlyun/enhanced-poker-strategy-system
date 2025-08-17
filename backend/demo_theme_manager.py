#!/usr/bin/env python3
"""
Demo script to showcase the Theme Manager.
Run this to see the Theme Manager in action.

NOTE: This GUI app should be run from an external terminal (macOS Terminal app),
not from VS Code's integrated terminal, to avoid crashes.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Safety check for VS Code integrated terminal
def check_terminal_compatibility():
    """Check if we're running in VS Code integrated terminal and warn user."""
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        print("⚠️  WARNING: Running GUI in VS Code integrated terminal may cause crashes!")
        print("💡 RECOMMENDED: Run this from macOS Terminal app instead:")
        print(f"   cd {os.getcwd()}")
        print(f"   python3 {os.path.basename(__file__)}")
        print()
        
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Exiting safely. Run from external terminal for best experience.")
            sys.exit(0)

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from ui.theme_manager import ThemeManager
from ui.services.theme_loader_consolidated import get_consolidated_theme_loader


class ThemeManagerDemo:
    """Simple demo app to showcase the Theme Manager."""
    
    def __init__(self):
        # Check terminal compatibility before creating GUI
        check_terminal_compatibility()
        
        self.root = tk.Tk()
        self.root.title("🎨 Theme Manager Demo - Poker Pro Trainer")
        self.root.geometry("600x400")
        
        # Load themes
        self.theme_loader = get_consolidated_theme_loader()
        self.config = self.theme_loader.load_themes()
        
        self.create_ui()
        
    def create_ui(self):
        """Create the demo UI."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎨 Theme Manager Demo", 
            font=("Inter", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Info
        info_text = """This demo showcases the consolidated Theme Manager for Poker Pro Trainer.

Features:
✅ Uses existing poker_themes.json as default (16 luxury themes)
✅ Live color picking and HSL nudging
✅ Save/Load theme files from anywhere
✅ Export themes to share with others
✅ Robust fallbacks - app always boots

Click "Open Theme Manager" to try it out!"""
        
        info_label = ttk.Label(main_frame, text=info_text, justify="left")
        info_label.pack(pady=(0, 20))
        
        # Current theme info
        current_file = self.theme_loader.get_current_file()
        file_info = f"Current theme file: {current_file.name if current_file else 'embedded fallback'}"
        theme_count = len(self.config.get("themes", []))
        
        status_text = f"{file_info}\nLoaded {theme_count} themes"
        status_label = ttk.Label(main_frame, text=status_text, foreground="blue")
        status_label.pack(pady=(0, 30))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        # Open Theme Manager button
        open_btn = ttk.Button(
            button_frame,
            text="🎨 Open Theme Manager",
            command=self.open_theme_manager,
            width=25
        )
        open_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_info,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Quit button
        quit_btn = ttk.Button(
            button_frame,
            text="❌ Quit",
            command=self.root.quit,
            width=15
        )
        quit_btn.pack(side="left", padx=(10, 0))
        
    def open_theme_manager(self):
        """Open the Theme Manager dialog."""
        def on_theme_change():
            """Called when theme is saved."""
            print("🎨 Theme changed - would refresh UI in real app")
            self.refresh_info()
            
        # Open modal Theme Manager
        theme_manager = ThemeManager(self.root, on_theme_change=on_theme_change)
        self.root.wait_window(theme_manager)
        
    def refresh_info(self):
        """Refresh the theme info display."""
        # Reload theme config
        self.config = self.theme_loader.reload()
        
        # Update display (in a real app you'd refresh the entire UI)
        current_file = self.theme_loader.get_current_file()
        theme_count = len(self.config.get("themes", []))
        print(f"📊 Refreshed: {theme_count} themes from {current_file.name if current_file else 'fallback'}")
        
    def run(self):
        """Run the demo."""
        print("🎨 Starting Theme Manager Demo...")
        print("💡 Try loading different theme files, editing colors, and using HSL nudges!")
        self.root.mainloop()


if __name__ == "__main__":
    demo = ThemeManagerDemo()
    demo.run()
