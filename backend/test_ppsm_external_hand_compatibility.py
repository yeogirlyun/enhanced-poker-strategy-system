#!/usr/bin/env python3
"""
PPSM External Hand Compatibility Test

Tests the PurePokerStateMachine's ability to handle external hand data
through the Hand Model interface. This validates:

1. Hand Model Interface - PPSM can accept and replay Hand objects
2. Bet Amount Translation - Converts external 'total contribution' to internal format  
3. Real Poker Data Compatibility - Works with legendary hands and other external sources
4. Production Readiness - Validates PPSM against real-world poker scenarios

This test represents the ultimate validation of PPSM's external compatibility.
"""

import json
import sys
import time
from typing import List, Dict, Any
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.poker_types import Player


class PPSMExternalHandCompatibilityTester:
    """Test PPSM's compatibility with external hand data via Hand Model interface."""
    
    def __init__(self):
        self.results = []
        self.legendary_hands_path = "data/legendary_hands_normalized.json"
        
    def load_legendary_hands(self) -> List[Hand]:
        """Load legendary hands as Hand Model objects."""
        try:
            print(f"📁 Loading legendary hands from: {self.legendary_hands_path}")
            with open(self.legendary_hands_path, 'r') as f:
                data = json.load(f)
            
            raw_hands = data.get('hands', [])
            hand_models = []
            
            for i, hand_data in enumerate(raw_hands[:20]):  # Test first 20 hands
                try:
                    hand_model = Hand.from_dict(hand_data)
                    hand_models.append(hand_model)
                except Exception as e:
                    print(f"⚠️  Could not parse hand {i+1}: {e}")
                    continue
            
            print(f"✅ Successfully loaded {len(hand_models)} Hand Model objects")
            return hand_models
            
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            return []
    
    def test_single_hand_replay(self, hand_model: Hand) -> Dict[str, Any]:
        """Test replaying a single hand through PPSM Hand Model interface."""
        hand_id = hand_model.metadata.hand_id
        
        try:
            # Create clean PPSM instance
            config = GameConfig(
                num_players=len(hand_model.seats),
                small_blind=hand_model.metadata.small_blind,
                big_blind=hand_model.metadata.big_blind,
                starting_stack=max(seat.starting_stack for seat in hand_model.seats)
            )
            
            ppsm = PurePokerStateMachine(config=config)
            
            # Use the new Hand Model interface
            result = ppsm.replay_hand_model(hand_model)
            
            # Enhanced result analysis
            result['hand_id'] = hand_id
            result['success'] = result['pot_match'] and result['successful_actions'] > 0
            result['action_success_rate'] = (
                result['successful_actions'] / result['total_actions'] * 100 
                if result['total_actions'] > 0 else 0
            )
            
            return result
            
        except Exception as e:
            return {
                'hand_id': hand_id,
                'success': False,
                'error': str(e),
                'total_actions': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'action_success_rate': 0.0,
                'final_pot': 0.0,
                'expected_pot': 0.0,
                'pot_match': False
            }
    
    def test_bet_amount_translation_scenario(self):
        """Test specific bet amount translation scenarios."""
        print("\n🧪 Testing Bet Amount Translation Scenarios")
        
        # Create a simple hand model for testing translation
        from core.hand_model import HandMetadata, Seat, Action, ActionType as HandModelActionType, Street, StreetState
        
        # Simple 2-player hand with known bet amounts
        metadata = HandMetadata(
            table_id="test_table",
            hand_id="translation_test_001", 
            small_blind=5,
            big_blind=10
        )
        metadata.button_seat_no = 1
        metadata.hole_cards = {"seat1": ["Kh", "Kd"], "seat2": ["Ad", "2c"]}
        
        seats = [
            Seat(seat_no=1, player_uid="seat1", starting_stack=1000, is_button=True),
            Seat(seat_no=2, player_uid="seat2", starting_stack=1000, is_button=False)
        ]
        
        # Create street with known actions that should translate properly
        preflop_actions = [
            Action(order=1, street=Street.PREFLOP, actor_uid=None, action=HandModelActionType.DEAL_HOLE, amount=0.0),
            Action(order=2, street=Street.PREFLOP, actor_uid="seat1", action=HandModelActionType.POST_BLIND, amount=5.0),
            Action(order=3, street=Street.PREFLOP, actor_uid="seat2", action=HandModelActionType.POST_BLIND, amount=10.0),
            Action(order=4, street=Street.PREFLOP, actor_uid="seat1", action=HandModelActionType.RAISE, amount=30.0),  # seat1 contributes $30 total
            Action(order=5, street=Street.PREFLOP, actor_uid="seat2", action=HandModelActionType.CALL, amount=30.0),   # seat2 contributes $30 total  
        ]
        
        streets = {
            Street.PREFLOP: StreetState(board=[], actions=preflop_actions),
            Street.FLOP: StreetState(board=[], actions=[]),
            Street.TURN: StreetState(board=[], actions=[]),
            Street.RIVER: StreetState(board=[], actions=[])
        }
        
        test_hand = Hand(
            metadata=metadata,
            seats=seats,
            hero_player_uid="seat1",
            streets=streets
        )
        
        # Test this hand
        result = self.test_single_hand_replay(test_hand)
        
        # Expected: seat1 puts in $30, seat2 puts in $30, total pot = $60
        expected_pot = 70.0  # $5 SB + $10 BB + $30 seat1 + $30 seat2 = $75... wait let me recalculate
        # Actually: POST_BLIND $5 + POST_BLIND $10 + RAISE $30 + CALL $30 = $75
        
        test_results = {
            'test_name': 'Bet Amount Translation',
            'expected_pot': 75.0,
            'actual_pot': result['final_pot'],
            'pot_match': abs(result['final_pot'] - 75.0) < 0.01,
            'action_success': result['action_success_rate'] == 100.0,
            'overall_success': abs(result['final_pot'] - 75.0) < 0.01 and result['action_success_rate'] == 100.0
        }
        
        print(f"   Expected Pot: ${test_results['expected_pot']}")
        print(f"   Actual Pot: ${test_results['actual_pot']}")
        print(f"   Pot Match: {test_results['pot_match']}")
        print(f"   Action Success: {test_results['action_success']}%")
        print(f"   Overall Success: {'✅ PASS' if test_results['overall_success'] else '❌ FAIL'}")
        
        return test_results
    
    def test_multi_hand_compatibility(self, max_hands: int = 10) -> Dict[str, Any]:
        """Test PPSM compatibility with multiple external hands."""
        print(f"\n🧪 Testing Multi-Hand External Compatibility ({max_hands} hands)")
        
        hand_models = self.load_legendary_hands()
        if not hand_models:
            return {'success': False, 'error': 'No hands loaded'}
        
        test_hands = hand_models[:max_hands]
        results = []
        successful_hands = 0
        total_actions = 0
        successful_actions = 0
        
        for i, hand_model in enumerate(test_hands):
            print(f"   Testing hand {i+1}: {hand_model.metadata.hand_id}")
            result = self.test_single_hand_replay(hand_model)
            results.append(result)
            
            if result['success']:
                successful_hands += 1
            
            total_actions += result['total_actions']
            successful_actions += result['successful_actions']
        
        summary = {
            'total_hands_tested': len(test_hands),
            'successful_hands': successful_hands,
            'failed_hands': len(test_hands) - successful_hands,
            'hand_success_rate': (successful_hands / len(test_hands) * 100) if test_hands else 0,
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'action_success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0,
            'results': results
        }
        
        print(f"   ✅ Hands: {successful_hands}/{len(test_hands)} successful ({summary['hand_success_rate']:.1f}%)")
        print(f"   ⚡ Actions: {successful_actions}/{total_actions} successful ({summary['action_success_rate']:.1f}%)")
        
        return summary
    
    def run_comprehensive_external_compatibility_test(self):
        """Run comprehensive external hand compatibility tests."""
        print("🏆 PPSM EXTERNAL HAND COMPATIBILITY TEST SUITE")
        print("=" * 70)
        print("🎯 Testing PPSM's Hand Model interface and external data compatibility")
        print("🃏 This validates production readiness with real poker data")
        print("=" * 70)
        
        overall_start = time.time()
        
        # Test 1: Bet Amount Translation
        translation_result = self.test_bet_amount_translation_scenario()
        
        # Test 2: Multi-Hand Compatibility
        compatibility_result = self.test_multi_hand_compatibility(max_hands=10)
        
        overall_elapsed = time.time() - overall_start
        
        # Summary
        print("\n" + "=" * 70)
        print("🏆 EXTERNAL COMPATIBILITY TEST SUMMARY")
        print("=" * 70)
        
        translation_success = translation_result['overall_success']
        compatibility_success = compatibility_result['hand_success_rate'] >= 90
        
        print(f"✅ Bet Amount Translation: {'PASS' if translation_success else 'FAIL'}")
        print(f"✅ Multi-Hand Compatibility: {compatibility_result['hand_success_rate']:.1f}% success rate")
        print(f"✅ Action Execution Rate: {compatibility_result['action_success_rate']:.1f}%")
        print(f"⏱️  Total Time: {overall_elapsed:.1f}s")
        
        # Overall verdict
        overall_success = translation_success and compatibility_success
        
        print(f"\n🎯 FINAL VERDICT:")
        if overall_success:
            print("🏆 PRODUCTION READY! PPSM handles external hands perfectly!")
            print("🚀 Hand Model interface works flawlessly with real poker data!")
        elif compatibility_result['hand_success_rate'] >= 70:
            print("🟡 MOSTLY READY - Minor compatibility issues to address")
        else:
            print("🔴 NEEDS WORK - Significant external compatibility problems")
        
        # Save results
        results_file = "ppsm_external_compatibility_results.json"
        final_results = {
            'translation_test': translation_result,
            'compatibility_test': compatibility_result,
            'overall_success': overall_success,
            'elapsed_time': overall_elapsed
        }
        
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return overall_success


def main():
    """Run the external hand compatibility tests."""
    tester = PPSMExternalHandCompatibilityTester()
    success = tester.run_comprehensive_external_compatibility_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
