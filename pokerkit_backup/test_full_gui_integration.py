#!/usr/bin/env python3
"""
Comprehensive test to simulate full GUI environment and identify console errors.
"""

import tkinter as tk
from practice_session_ui import PracticeSessionUI
from gui_models import StrategyData
import os
import traceback

def test_full_gui_integration():
    """Test the full GUI integration with error handling."""
    try:
        print("=== Full GUI Integration Test ===")
        
        # Create root window (simulating main GUI)
        print("1. Creating root window...")
        root = tk.Tk()
        root.title("Test GUI")
        
        # Load strategy data (simulating main GUI)
        print("2. Loading strategy data...")
        strategy_data = StrategyData()
        if os.path.exists("modern_strategy.json"):
            strategy_data.load_strategy_from_file("modern_strategy.json")
        print("✓ Strategy data loaded")
        
        # Create practice session UI (simulating main GUI integration)
        print("3. Creating PracticeSessionUI...")
        ps = PracticeSessionUI(root, strategy_data)
        print("✓ PracticeSessionUI created")
        
        # Simulate GUI event loop
        print("4. Starting GUI event loop...")
        root.update()
        print("✓ GUI event loop started")
        
        # Test starting a new hand
        print("5. Testing start_new_hand...")
        ps.start_new_hand()
        print("✓ New hand started")
        
        # Test getting game info
        print("6. Testing get_game_info...")
        game_info = ps.state_machine.get_game_info()
        print(f"✓ Game info: {len(game_info['players'])} players")
        
        # Test updating display
        print("7. Testing update_display...")
        ps.update_display()
        print("✓ Display updated")
        
        # Test GUI event loop again
        print("8. Testing GUI event loop...")
        root.update()
        print("✓ GUI event loop updated")
        
        # Clean up
        print("9. Cleaning up...")
        root.destroy()
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_full_gui_integration()
    if success:
        print("\n🎯 Full GUI integration test PASSED!")
    else:
        print("\n💥 Full GUI integration test FAILED!") 