#!/usr/bin/env python3
"""
Test to verify that ATs and KQo are properly included in the Premium tier
"""

from gui_models import StrategyData

def test_missing_hands():
    """Test that ATs and KQo are included in the Premium tier."""
    print("="*60)
    print("TESTING MISSING HANDS: ATs and KQo")
    print("="*60)
    
    # Create strategy data
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Find Premium tier
    premium_tier = None
    for tier in strategy_data.tiers:
        if tier.name == "Premium":
            premium_tier = tier
            break
    
    if premium_tier:
        print(f"Premium tier found with {len(premium_tier.hands)} hands:")
        for hand in sorted(premium_tier.hands):
            print(f"  - {hand}")
        
        # Check for ATs and KQo
        ats_included = "ATs" in premium_tier.hands
        kqo_included = "KQo" in premium_tier.hands
        
        print(f"\nVerification:")
        print(f"  ATs included: {ats_included}")
        print(f"  KQo included: {kqo_included}")
        
        if ats_included and kqo_included:
            print("✅ SUCCESS: Both ATs and KQo are included in Premium tier")
        else:
            print("❌ FAILURE: Missing hands in Premium tier")
            if not ats_included:
                print("  - ATs is missing")
            if not kqo_included:
                print("  - KQo is missing")
    else:
        print("❌ ERROR: Premium tier not found")
    
    # Show total hands count
    total_hands = sum(len(tier.hands) for tier in strategy_data.tiers)
    print(f"\nTotal hands across all tiers: {total_hands}")
    
    # Show hands per tier
    print(f"\nHands per tier:")
    for tier in strategy_data.tiers:
        print(f"  {tier.name}: {len(tier.hands)} hands")

if __name__ == "__main__":
    test_missing_hands() 