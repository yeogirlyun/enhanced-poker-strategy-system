#!/usr/bin/env python3
"""
Test suite to validate the hand evaluation fix.
This specifically tests the bug scenario where Full House should beat Two Pair.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from enhanced_hand_evaluation import EnhancedHandEvaluator
from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine


def test_hand_evaluation_fix():
    """Test the specific bug scenario: Full House vs Two Pair."""
    print("🧪 Testing Hand Evaluation Fix...")
    
    # Create evaluator and state machine
    evaluator = EnhancedHandEvaluator()
    state_machine = ImprovedPokerStateMachine(num_players=6)
    
    # The bug scenario from the user's screenshot
    community_cards = ['Ad', 'Ac', 'Ks', 'Kh', 'Qc']  # Board: A♦ A♣ K♠ K♥ Q♣
    player1_cards = ['Ah', '2d']  # Player 1: A♥ 2♦ (Full House: Aces full of Kings)
    player3_cards = ['5h', '6d']  # Player 3: 5♥ 6♦ (Two Pair: Aces and Kings)
    
    print(f"🎴 Board: {' '.join(community_cards)}")
    print(f"👤 Player 1: {' '.join(player1_cards)}")
    print(f"👤 Player 3: {' '.join(player3_cards)}")
    
    # Evaluate both hands
    player1_eval = evaluator.evaluate_hand(player1_cards, community_cards)
    player3_eval = evaluator.evaluate_hand(player3_cards, community_cards)
    
    print(f"\n📊 Player 1 Evaluation:")
    print(f"   Hand Rank: {player1_eval['hand_rank'].name}")
    print(f"   Description: {player1_eval['hand_description']}")
    print(f"   Strength Score: {player1_eval['strength_score']}")
    
    print(f"\n📊 Player 3 Evaluation:")
    print(f"   Hand Rank: {player3_eval['hand_rank'].name}")
    print(f"   Description: {player3_eval['hand_description']}")
    print(f"   Strength Score: {player3_eval['strength_score']}")
    
    # Test winner determination
    player1_strength = player1_eval['strength_score']
    player3_strength = player3_eval['strength_score']
    
    print(f"\n🏆 Winner Determination:")
    if player1_strength > player3_strength:
        print("✅ Player 1 wins (CORRECT - Full House beats Two Pair)")
        winner_correct = True
    elif player3_strength > player1_strength:
        print("❌ Player 3 wins (INCORRECT - Two Pair should not beat Full House)")
        winner_correct = False
    else:
        print("❌ Tie (INCORRECT - Full House should beat Two Pair)")
        winner_correct = False
    
    # Test best 5 cards identification
    print(f"\n🎯 Best 5 Cards Test:")
    player1_best_cards = evaluator.get_best_five_cards(player1_cards, community_cards)
    player3_best_cards = evaluator.get_best_five_cards(player3_cards, community_cards)
    
    print(f"Player 1 best 5 cards: {' '.join(player1_best_cards)}")
    print(f"Player 3 best 5 cards: {' '.join(player3_best_cards)}")
    
    # Validate that Player 1's best cards include the Aces and Kings that form the Full House
    expected_player1_cards = ['Ah', 'Ad', 'Ac', 'Ks', 'Kh']  # Aces full of Kings
    cards_correct = set(player1_best_cards) == set(expected_player1_cards)
    
    if cards_correct:
        print("✅ Player 1's best 5 cards are correct (Full House cards)")
    else:
        print(f"❌ Player 1's best 5 cards are incorrect")
        print(f"   Expected: {' '.join(expected_player1_cards)}")
        print(f"   Got: {' '.join(player1_best_cards)}")
    
    # Test state machine's hand evaluation
    print(f"\n🤖 State Machine Test:")
    state_machine.hand_evaluator = evaluator
    
    # Simulate the showdown scenario
    player1 = state_machine.game_state.players[0]
    player3 = state_machine.game_state.players[2]
    
    player1.cards = player1_cards
    player3.cards = player3_cards
    state_machine.game_state.board = community_cards
    
    # Determine winner using state machine
    winners = state_machine.determine_winner([player1, player3])
    
    if len(winners) == 1 and winners[0] == player1:
        print("✅ State machine correctly determines Player 1 as winner")
        state_machine_correct = True
    else:
        print("❌ State machine incorrectly determines winner")
        print(f"   Winners: {[w.name for w in winners]}")
        state_machine_correct = False
    
    # Overall test result
    print(f"\n📋 Test Summary:")
    print(f"   Winner determination: {'✅ PASS' if winner_correct else '❌ FAIL'}")
    print(f"   Best 5 cards: {'✅ PASS' if cards_correct else '❌ FAIL'}")
    print(f"   State machine: {'✅ PASS' if state_machine_correct else '❌ FAIL'}")
    
    all_passed = winner_correct and cards_correct and state_machine_correct
    print(f"\n🎉 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


def test_additional_hand_comparisons():
    """Test additional hand comparisons to ensure robustness."""
    print("\n🧪 Testing Additional Hand Comparisons...")
    
    evaluator = EnhancedHandEvaluator()
    
    test_cases = [
        {
            'name': 'Pair vs Pair',
            'board': ['2d', '5c', '7h', '9s', 'Jh'],
            'player1': ['As', 'Ad'],  # Pair of Aces
            'player2': ['Ks', 'Kd'],  # Pair of Kings
            'expected_winner': 1
        },
        {
            'name': 'Two Pair vs Two Pair',
            'board': ['Ad', 'Kc', '5h', 'Qs', '2d'],
            'player1': ['As', '5d'],  # Two pair, Aces and Fives
            'player2': ['Ks', 'Qd'],  # Two pair, Kings and Queens
            'expected_winner': 1
        },
        {
            'name': 'Full House vs Flush',
            'board': ['Ad', 'Ac', 'Kh', '5d', '8d'],
            'player1': ['As', 'Kd'],  # Full House (Aces full of Kings)
            'player2': ['Jd', '9d'],  # King-high Flush
            'expected_winner': 1
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n📊 Testing: {test_case['name']}")
        
        player1_eval = evaluator.evaluate_hand(test_case['player1'], test_case['board'])
        player2_eval = evaluator.evaluate_hand(test_case['player2'], test_case['board'])
        
        player1_strength = player1_eval['strength_score']
        player2_strength = player2_eval['strength_score']
        
        if player1_strength > player2_strength:
            winner = 1
        elif player2_strength > player1_strength:
            winner = 2
        else:
            winner = 0  # Tie
        
        expected = test_case['expected_winner']
        passed = winner == expected
        
        print(f"   Player 1: {player1_eval['hand_rank'].name} (strength: {player1_strength})")
        print(f"   Player 2: {player2_eval['hand_rank'].name} (strength: {player2_strength})")
        print(f"   Winner: Player {winner}")
        print(f"   Expected: Player {expected}")
        print(f"   Result: {'✅ PASS' if passed else '❌ FAIL'}")
        
        if not passed:
            all_passed = False
    
    print(f"\n🎉 Additional Tests: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    return all_passed


if __name__ == '__main__':
    print("🚀 Starting Hand Evaluation Fix Tests...\n")
    
    # Run the main bug fix test
    main_test_passed = test_hand_evaluation_fix()
    
    # Run additional comparison tests
    additional_tests_passed = test_additional_hand_comparisons()
    
    # Final result
    all_tests_passed = main_test_passed and additional_tests_passed
    
    print(f"\n🎯 FINAL RESULT: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("🎉 The hand evaluation fix is working correctly!")
        print("   - Full House correctly beats Two Pair")
        print("   - Best 5 cards are correctly identified")
        print("   - State machine correctly determines winners")
    else:
        print("⚠️  Some tests failed. The fix may need further refinement.")
    
    sys.exit(0 if all_tests_passed else 1) 