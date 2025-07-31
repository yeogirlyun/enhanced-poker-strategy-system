#!/usr/bin/env python3
"""
Test script for the enhanced hand evaluator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from enhanced_hand_evaluation import hand_evaluator, HandRank


def test_hand_evaluation():
    """Test various hand evaluations."""
    print("=== Enhanced Hand Evaluator Test ===\n")
    
    # Test cases
    test_cases = [
        {
            'name': 'Royal Flush',
            'hole': ['Ah', 'Kh'],
            'board': ['Qh', 'Jh', 'Th'],
            'expected_rank': HandRank.STRAIGHT_FLUSH
        },
        {
            'name': 'Four of a Kind',
            'hole': ['As', 'Ad'],
            'board': ['Ah', 'Ac', '7c'],
            'expected_rank': HandRank.FOUR_OF_A_KIND
        },
        {
            'name': 'Full House',
            'hole': ['As', 'Ad'],
            'board': ['Ah', '7c', '7d'],
            'expected_rank': HandRank.FULL_HOUSE
        },
        {
            'name': 'Flush',
            'hole': ['Ah', 'Kh'],
            'board': ['Qh', 'Jh', '2c'],
            'expected_rank': HandRank.FLUSH
        },
        {
            'name': 'Straight',
            'hole': ['9h', '8d'],
            'board': ['7c', '6s', '5h'],
            'expected_rank': HandRank.STRAIGHT
        },
        {
            'name': 'Three of a Kind',
            'hole': ['As', 'Ad'],
            'board': ['Ah', '7c', '2d'],
            'expected_rank': HandRank.THREE_OF_A_KIND
        },
        {
            'name': 'Two Pair',
            'hole': ['As', 'Kd'],
            'board': ['Ah', 'Kc', '2d'],
            'expected_rank': HandRank.TWO_PAIR
        },
        {
            'name': 'Pair',
            'hole': ['As', 'Kd'],
            'board': ['Ah', '7c', '2d'],
            'expected_rank': HandRank.PAIR
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        result = hand_evaluator.evaluate_hand(test_case['hole'], test_case['board'])
        
        print(f"  Hole: {test_case['hole']}")
        print(f"  Board: {test_case['board']}")
        print(f"  Result: {result['hand_description']}")
        print(f"  Strength: {result['strength_score']}")
        print(f"  Expected: {test_case['expected_rank'].name}")
        
        if result['hand_rank'] == test_case['expected_rank']:
            print("  ✅ PASS")
        else:
            print(f"  ❌ FAIL - Got {result['hand_rank'].name}")
        print()


def test_preflop_strengths():
    """Test preflop hand strength calculations."""
    print("=== Preflop Hand Strength Test ===\n")
    
    test_hands = [
        ('AA', ['Ah', 'Ad']),
        ('KK', ['Kh', 'Kd']),
        ('AKs', ['Ah', 'Kh']),
        ('AKo', ['Ah', 'Kd']),
        ('72o', ['7h', '2d']),
    ]
    
    for hand_name, cards in test_hands:
        strength = hand_evaluator.get_preflop_hand_strength(cards)
        print(f"{hand_name}: {strength}")


if __name__ == "__main__":
    test_hand_evaluation()
    test_preflop_strengths() 