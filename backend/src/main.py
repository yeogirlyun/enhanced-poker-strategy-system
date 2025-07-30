#!/usr/bin/env python3
"""
Janggi (Korean Chess) Game - Main Entry Point

This is the main entry point for the Janggi game application.
"""

import sys
import tkinter as tk
from tkinter import messagebox

# Add src to path for imports
sys.path.append('src')

from gui.main_window import JanggiMainWindow


def main():
    """Main entry point for the Janggi game."""
    try:
        # Create the main application window
        root = tk.Tk()
        root.title("Janggi - Korean Chess")
        root.geometry("800x600")
        
        # Initialize the main window
        app = JanggiMainWindow(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Janggi: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 