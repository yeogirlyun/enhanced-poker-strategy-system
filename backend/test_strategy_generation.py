#!/usr/bin/env python3
"""
Test script to verify strategy file generation functionality.
"""

import os
import sys
from gui_models import StrategyData

def test_strategy_generation():
    """Test the strategy file generation functionality."""
    print("🧪 Testing strategy file generation...")
    
    # Create StrategyData instance with default tiers
    default_strategy = StrategyData()
    default_strategy.load_default_tiers()
    
    # Test file generation
    test_filename = "test_strategy.json"
    
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print(f"📝 Attempting to save strategy to {test_filename}...")
    
    if default_strategy.save_strategy_to_file(test_filename):
        print(f"✅ Successfully generated {test_filename}")
        
        # Verify the file was created
        if os.path.exists(test_filename):
            print(f"✅ File {test_filename} exists and is readable")
            
            # Clean up
            os.remove(test_filename)
            print(f"🧹 Cleaned up {test_filename}")
        else:
            print(f"❌ File {test_filename} was not created")
    else:
        print(f"❌ Failed to generate {test_filename}")
    
    print("🎯 Strategy generation test complete!")

if __name__ == "__main__":
    test_strategy_generation() 