#!/usr/bin/env python3
"""
Debug script to check canvas creation in ReusablePokerGameWidget
"""

import tkinter as tk
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

def main():
    print("🧪 Testing ReusablePokerGameWidget canvas creation...")
    
    root = tk.Tk()
    root.title("Canvas Debug Test")
    root.geometry("800x600")
    
    # Create a frame to hold the widget
    container = tk.Frame(root, bg="red")  # Red background to see the container
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create the poker widget
    print("🔄 Creating ReusablePokerGameWidget...")
    widget = ReusablePokerGameWidget(container, state_machine=None, debug_mode=True)
    widget.pack(fill=tk.BOTH, expand=True)
    
    # Check canvas immediately
    def check_canvas():
        print(f"🔍 Canvas attribute exists: {hasattr(widget, 'canvas')}")
        if hasattr(widget, 'canvas'):
            print(f"🔍 Canvas is None: {widget.canvas is None}")
            if widget.canvas:
                print(f"🔍 Canvas type: {type(widget.canvas)}")
                print(f"🔍 Canvas size: {widget.canvas.winfo_width()}x{widget.canvas.winfo_height()}")
                print("✅ Canvas created successfully!")
            else:
                print("❌ Canvas is None")
        else:
            print("❌ Canvas attribute doesn't exist")
    
    # Check immediately
    root.after(50, check_canvas)
    
    # Check again after a delay
    root.after(200, check_canvas)
    
    # Check after longer delay
    root.after(500, check_canvas)
    
    # Auto-close after testing
    root.after(2000, root.destroy)
    
    print("🚀 Starting GUI test...")
    root.mainloop()
    print("✅ Canvas debug test completed")

if __name__ == "__main__":
    main()
