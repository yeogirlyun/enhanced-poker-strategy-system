#!/usr/bin/env python3
"""
Test Simple Hands Review System

This script demonstrates the new simple hands review approach
that replicates the practice session UI without complex game logic.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our simple components
from ui.components.simple_hands_review_panel import SimpleHandsReviewPanel


def main():
    """Main test function."""
    # Create main window
    root = tk.Tk()
    root.title("Simple Hands Review - Test")
    root.geometry("1000x800")
    
    # Create simple hands review panel
    panel = SimpleHandsReviewPanel(root)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add some test info
    info_label = ttk.Label(
        root, 
        text="🎯 Simple Hands Review System - No FPSM, No Game Logic, Just Data Rendering",
        font=('Arial', 12, 'bold')
    )
    info_label.pack(pady=(0, 10))
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
