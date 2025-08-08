#!/usr/bin/env python3
"""
Demo of the Redesigned Hands Review Panel

This demo showcases the new two-pane layout and features:
- Left pane: Hand selection and categorization  
- Right pane: Interactive study and step-by-step simulation
"""

import tkinter as tk
from ui.components.redesigned_hands_review_panel import RedesignedHandsReviewPanel

def main():
    """Demo the redesigned hands review panel."""
    print("🎯 Redesigned Hands Review Panel Demo")
    print("=" * 50)
    
    # Create demo window
    root = tk.Tk()
    root.title("Hands Review Panel Demo")
    root.geometry("1200x800")
    
    # Create the redesigned panel
    panel = RedesignedHandsReviewPanel(root)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    print("✅ Demo window created with new two-pane layout:")
    print("   📋 Left Pane: Hand selection and categorization")
    print("   🎮 Right Pane: Interactive simulation and study tools")
    print()
    print("🚀 Features:")
    print("   • Two-pane layout (30% left, 70% right)")
    print("   • Category filtering (Legendary vs Practice hands)")
    print("   • Subcategory filtering for legendary hands")
    print("   • Hand preview with player information")
    print("   • Step-by-step hand simulation")
    print("   • Interactive study analysis with multiple tabs")
    print("   • Next/Previous/Reset simulation controls")
    print("   • Simulation mode vs Study mode toggle")
    print()
    print("📚 Study Mode Features:")
    print("   • Equity Analysis: Pre-flop and post-flop equity calculations")
    print("   • Strategy Analysis: Key strategic concepts and guidelines")
    print("   • Key Decisions: Critical decision points and learning objectives")
    print()
    print("🎮 Simulation Mode Features:")
    print("   • Step-by-step hand progression")
    print("   • Game state display (pot, street, board)")
    print("   • Player status and hole cards")
    print("   • Action descriptions for each step")
    print("   • Navigation controls (Next, Previous, Reset)")
    print()
    print("🎨 UI Improvements:")
    print("   • Clean, modern interface design")
    print("   • Proper font scaling integration")
    print("   • Responsive pane resizing")
    print("   • Clear visual separation of functions")
    print()
    print("👆 Click on hands in the left pane to see them in action!")
    print("🎮 Use Simulation Mode for step-by-step replay")
    print("📚 Use Study Mode for in-depth analysis")
    
    # Start the demo
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()
