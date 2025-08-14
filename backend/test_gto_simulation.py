#!/usr/bin/env python3
"""
Test script for GTO Simulation System

This script tests the GTO poker state machine, game widget, and simulation panel
to ensure they work correctly together.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add backend directory to path
sys.path.append('.')

from ui.components.gto_simulation_panel import GTOSimulationPanel
from core.session_logger import SessionLogger


def main():
    """Main test function."""
    print("🚀 Testing GTO Simulation System")
    print("=" * 50)
    
    # Create root window
    root = tk.Tk()
    root.title("GTO Simulation Test")
    root.geometry("1400x900")
    
    # Initialize logger
    logger = SessionLogger()
    
    # Create GTO simulation panel
    gto_panel = GTOSimulationPanel(root, logger=logger)
    gto_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add some test controls
    test_frame = ttk.LabelFrame(root, text="Test Controls", padding=10)
    test_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Test buttons
    def test_start_session():
        print("🧪 Testing session start...")
        gto_panel._start_session()
    
    def test_new_hand():
        print("🧪 Testing new hand...")
        gto_panel._start_new_hand()
    
    def test_session_summary():
        print("🧪 Testing session summary...")
        summary = gto_panel.get_session_summary()
        print(f"Session Summary: {summary}")
    
    def test_statistics():
        print("🧪 Testing statistics update...")
        gto_panel.update_statistics(5, 25.50)
        print("Statistics updated with 5 decisions, $25.50 pot")
    
    ttk.Button(test_frame, text="Test Start Session", 
               command=test_start_session).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(test_frame, text="Test New Hand", 
               command=test_new_hand).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(test_frame, text="Test Session Summary", 
               command=test_session_summary).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(test_frame, text="Test Statistics", 
               command=test_statistics).pack(side=tk.LEFT, padx=(0, 5))
    
    print("✅ GTO Simulation Panel created successfully")
    print("🎮 Use the panel controls to test the system")
    print("🧪 Use test buttons for automated testing")
    
    # Start the GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🔄 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        print("👋 GTO Simulation test completed")


if __name__ == "__main__":
    main()
