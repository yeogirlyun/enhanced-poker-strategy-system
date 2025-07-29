#!/usr/bin/env python3
"""
Test script to check hand format matching between tiers and grid
"""

from gui_models import StrategyData, HandFormatHelper

def test_hand_matching():
    """Test if hands in tiers match the grid format."""
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    print("Testing hand format matching:")
    print("=" * 50)
    
    # Get all hands that should be in the grid
    grid_hands = set()
    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    
    for i, rank1 in enumerate(ranks):
        for j, rank2 in enumerate(ranks):
            if i == j:
                hand = rank1 + rank2  # Pocket pairs
            elif i < j:
                hand = rank1 + rank2 + 's'  # Suited
            else:
                hand = rank2 + rank1 + 'o'  # Offsuit
            grid_hands.add(hand)
    
    print(f"Grid contains {len(grid_hands)} hands")
    print("Sample grid hands:", sorted(list(grid_hands))[:20])
    
    print("\nTier hands vs Grid hands:")
    print("=" * 50)
    
    for tier in strategy_data.tiers:
        print(f"\n{tier.name} Tier ({len(tier.hands)} hands):")
        print(f"  Color: {tier.color}")
        print(f"  Hands: {tier.hands}")
        
        # Check which hands match the grid
        matching_hands = []
        non_matching_hands = []
        
        for hand in tier.hands:
            # Check direct match
            if hand in grid_hands:
                matching_hands.append(hand)
            else:
                # Check alternative formats
                alternatives = HandFormatHelper.get_alternative_formats(hand)
                found = False
                for alt in alternatives:
                    if alt in grid_hands:
                        matching_hands.append(f"{hand} -> {alt}")
                        found = True
                        break
                if not found:
                    non_matching_hands.append(hand)
        
        print(f"  Matching grid hands: {matching_hands}")
        if non_matching_hands:
            print(f"  NON-MATCHING hands: {non_matching_hands}")
        else:
            print(f"  All hands match grid format ✓")

if __name__ == "__main__":
    test_hand_matching() 