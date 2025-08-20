#!/usr/bin/env python3
"""
Test MVU Multiple Button Clicks
Automatically clicks Next button multiple times to test the sequence
"""

import tkinter as tk
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUHandsReviewTab


def main():
    """Test multiple button clicks"""
    print("🧪 Testing MVU Multiple Button Clicks...")
    
    # Create root window
    root = tk.Tk()
    root.title("MVU Multiple Clicks Test")
    root.geometry("1200x800")
    
    # Create services mock
    class MockServices:
        def __init__(self):
            self._services = {}
        
        def get_app(self, name):
            return self._services.get(name)
        
        def provide_app(self, name, service):
            self._services[name] = service
    
    services = MockServices()
    
    # Create MVU Hands Review Tab
    try:
        review_tab = MVUHandsReviewTab(root, services=services)
        review_tab.pack(fill="both", expand=True)
        
        print("✅ MVU HandsReviewTab created successfully!")
        
        # Function to click Next button multiple times
        def auto_click_next():
            print("\n🔄 Auto-clicking Next button...")
            
            # Find the Next button
            next_btn = None
            for widget in review_tab.table_renderer.winfo_children():
                if isinstance(widget, tk.Frame):  # controls_frame
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Button) and child['text'] == 'Next':
                            next_btn = child
                            break
            
            if next_btn:
                # Click Next button 5 times with delays
                def click_sequence(count=0):
                    if count < 5:
                        print(f"\n🖱️ Clicking Next button #{count + 1}")
                        next_btn.invoke()  # Simulate button click
                        # Schedule next click after 2 seconds
                        root.after(2000, lambda: click_sequence(count + 1))
                    else:
                        print("\n✅ Finished clicking sequence")
                
                # Start clicking sequence after 3 seconds
                root.after(3000, click_sequence)
            else:
                print("⚠️ Could not find Next button")
        
        # Start auto-clicking
        auto_click_next()
        
        # Add cleanup on close
        def on_closing():
            review_tab.dispose()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the UI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
