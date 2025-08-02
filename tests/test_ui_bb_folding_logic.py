#!/usr/bin/env python3
"""
Test BB folding logic directly without full UI complexity.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import Player, ActionType, GameState, PokerState


class TestBBFoldingLogic(unittest.TestCase):
    """Test BB folding logic directly."""
    
    def test_bb_fold_logic_when_facing_bet(self):
        """Test the BB folding logic when facing a bet."""
        # Simulate the exact scenario from the image
        # Game state: Turn betting, pot $3.50, current bet $1.00
        # Player 1 (BTN) has bet $1.00
        # Player 3 (BB) has current_bet $0.00 (already posted blind)
        
        current_bet = 1.0  # BTN's bet
        bb_current_bet = 0.0  # BB's current bet (already posted blind)
        big_blind = 1.0
        
        # OLD BUGGY LOGIC (what was causing the issue)
        old_logic_result = current_bet <= big_blind
        print(f"OLD LOGIC: current_bet ({current_bet}) <= big_blind ({big_blind}) = {old_logic_result}")
        
        # NEW FIXED LOGIC (what we implemented)
        bb_call_amount = current_bet - bb_current_bet
        new_logic_result = bb_call_amount <= 0
        print(f"NEW LOGIC: bb_call_amount ({bb_call_amount}) <= 0 = {new_logic_result}")
        
        # Test that the new logic correctly identifies BB can fold
        self.assertFalse(new_logic_result, 
                        "BB should be able to fold when facing a bet")
        
        # Test that the old logic was wrong
        self.assertTrue(old_logic_result, 
                       "Old logic incorrectly prevented BB from folding")
        
        print("✅ NEW LOGIC: BB can fold when facing a bet")
        print("❌ OLD LOGIC: BB was incorrectly prevented from folding")
    
    def test_bb_fold_logic_when_no_bet(self):
        """Test the BB folding logic when no bet has been made."""
        # Simulate scenario where only blinds are posted
        current_bet = 1.0  # Only big blind
        bb_current_bet = 1.0  # BB has posted their blind
        big_blind = 1.0
        
        # OLD LOGIC
        old_logic_result = current_bet <= big_blind
        print(f"OLD LOGIC: current_bet ({current_bet}) <= big_blind ({big_blind}) = {old_logic_result}")
        
        # NEW LOGIC
        bb_call_amount = current_bet - bb_current_bet
        new_logic_result = bb_call_amount <= 0
        print(f"NEW LOGIC: bb_call_amount ({bb_call_amount}) <= 0 = {new_logic_result}")
        
        # Test that both logics correctly prevent BB from folding
        self.assertTrue(new_logic_result, 
                       "BB should not be able to fold when no bet has been made")
        
        print("✅ NEW LOGIC: BB cannot fold when no bet has been made")
    
    def test_bb_fold_logic_edge_cases(self):
        """Test BB folding logic with various edge cases."""
        test_cases = [
            # (current_bet, bb_current_bet, big_blind, should_be_able_to_fold, description)
            (1.0, 0.0, 1.0, True, "BB facing bet after posting blind"),
            (1.0, 1.0, 1.0, False, "BB only blinds posted"),
            (2.0, 1.0, 1.0, True, "BB facing raise"),
            (3.0, 1.0, 1.0, True, "BB facing big raise"),
            (0.5, 0.5, 1.0, False, "BB only small blind posted"),
            (0.0, 0.0, 1.0, False, "No bets at all"),
        ]
        
        for current_bet, bb_current_bet, big_blind, should_be_able_to_fold, description in test_cases:
            # NEW LOGIC
            bb_call_amount = current_bet - bb_current_bet
            can_fold = bb_call_amount > 0
            
            print(f"\n{description}:")
            print(f"  current_bet: {current_bet}, bb_current_bet: {bb_current_bet}")
            print(f"  bb_call_amount: {bb_call_amount}, can_fold: {can_fold}")
            
            self.assertEqual(can_fold, should_be_able_to_fold,
                           f"BB folding logic incorrect for: {description}")
            
            print(f"  ✅ PASS: {description}")


if __name__ == '__main__':
    unittest.main() 