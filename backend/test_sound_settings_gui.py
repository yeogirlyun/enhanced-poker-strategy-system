#!/usr/bin/env python3
"""
Test Sound Settings GUI

Tests the sound settings GUI to ensure file browsing works.
"""

import tkinter as tk
from sound_settings_gui import create_sound_settings_window

def main():
    """Test the sound settings GUI."""
    print("🎵 TESTING SOUND SETTINGS GUI")
    print("=" * 40)
    
    # Create root window
    root = tk.Tk()
    root.title("Sound Settings Test")
    root.geometry("800x600")
    
    # Create sound settings window
    print("🔧 Creating sound settings window...")
    sound_window = create_sound_settings_window(root)
    
    print("✅ Sound settings window created")
    print("📋 Instructions:")
    print("  1. Click on any sound entry")
    print("  2. Click 'Browse' button")
    print("  3. Select a sound file")
    print("  4. Click 'Replace Sound' to test")
    print("  5. Check console for debug output")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 