#!/usr/bin/env python3
"""
Test to verify that strategy file loading works correctly
"""

from gui_models import StrategyData

def test_strategy_file_loading():
    """Test strategy file loading functionality."""
    print("="*60)
    print("TESTING STRATEGY FILE LOADING")
    print("="*60)
    
    # Create strategy data
    strategy_data = StrategyData()
    
    # Test default strategy
    print("\n1. Testing Default Strategy:")
    strategy_data.load_default_tiers()
    print(f"   Strategy: {strategy_data.get_strategy_file_display_name()}")
    print(f"   Total hands: {sum(len(tier.hands) for tier in strategy_data.tiers)}")
    print(f"   Tiers: {len(strategy_data.tiers)}")
    
    # Test available strategy files
    print("\n2. Available Strategy Files:")
    available_files = strategy_data.get_available_strategy_files()
    for file in available_files:
        print(f"   - {file}")
    
    # Test loading baseline strategy
    print("\n3. Testing Baseline Strategy Loading:")
    if "baseline_strategy.json" in available_files:
        success = strategy_data.load_strategy_from_file("baseline_strategy.json")
        print(f"   Load success: {success}")
        if success:
            print(f"   Strategy: {strategy_data.get_strategy_file_display_name()}")
            print(f"   Total hands: {sum(len(tier.hands) for tier in strategy_data.tiers)}")
            print(f"   Tiers: {len(strategy_data.tiers)}")
            
            # Show tier details
            for tier in strategy_data.tiers:
                print(f"     {tier.name} ({tier.min_hs}-{tier.max_hs}): {len(tier.hands)} hands")
                print(f"       Hands: {', '.join(tier.hands)}")
    else:
        print("   baseline_strategy.json not found")
    
    # Test loading main strategy
    print("\n4. Testing Main Strategy Loading:")
    if "strategy.json" in available_files:
        success = strategy_data.load_strategy_from_file("strategy.json")
        print(f"   Load success: {success}")
        if success:
            print(f"   Strategy: {strategy_data.get_strategy_file_display_name()}")
            print(f"   Total hands: {sum(len(tier.hands) for tier in strategy_data.tiers)}")
            print(f"   Tiers: {len(strategy_data.tiers)}")
            
            # Show tier details
            for tier in strategy_data.tiers:
                print(f"     {tier.name} ({tier.min_hs}-{tier.max_hs}): {len(tier.hands)} hands")
                print(f"       Hands: {', '.join(tier.hands)}")
    else:
        print("   strategy.json not found")
    
    # Test saving strategy
    print("\n5. Testing Strategy Saving:")
    test_filename = "test_strategy_output.json"
    success = strategy_data.save_strategy_to_file(test_filename)
    print(f"   Save success: {success}")
    if success:
        print(f"   Saved to: {test_filename}")
        
        # Test loading the saved file
        print("\n6. Testing Loading Saved Strategy:")
        new_strategy = StrategyData()
        load_success = new_strategy.load_strategy_from_file(test_filename)
        print(f"   Load saved file success: {load_success}")
        if load_success:
            print(f"   Strategy: {new_strategy.get_strategy_file_display_name()}")
            print(f"   Total hands: {sum(len(tier.hands) for tier in new_strategy.tiers)}")
    
    print("\n" + "="*60)
    print("STRATEGY FILE TESTING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_strategy_file_loading() 