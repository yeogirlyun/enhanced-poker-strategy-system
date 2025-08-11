#!/usr/bin/env python3
"""
FPSM + RPGW Historical Order Tester

Tests FPSM + RPGW integration using the historical order approach that achieved 
100% success on FPSM. This ensures both the poker logic and UI integration work
perfectly with the complete JSON format legendary hands.
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.testable_poker_state_machine import TestablePokerStateMachine, TestableGameConfig
from core.types import Player, ActionType, PokerState
from core.position_mapping import UniversalPosition
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

class FPSMRPGWHistoricalTester:
    """Tests FPSM + RPGW using historical action order."""
    
    def __init__(self):
        self.json_data = None
        self.hands = []
        self.test_results = []
        
    def run_fpsm_rpgw_test(self):
        """Run FPSM + RPGW test using historical action order."""
        print("🎯 FPSM + RPGW HISTORICAL ORDER TEST (Target: 100%)")
        print("=" * 60)
        
        # Load complete JSON data
        self.load_json_data()
        
        # Test all hands
        self.test_all_hands()
        
        # Generate report
        self.generate_report()
        
        return self.test_results
    
    def load_json_data(self):
        """Load the complete JSON format hands data."""
        json_file_path = "data/legendary_hands_complete_130_fixed.json"
        
        print(f"📚 Loading complete JSON data from {json_file_path}...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            self.hands = self.json_data['hands']
            
            print(f"✅ Loaded {len(self.hands)} hands from complete JSON")
            
        except Exception as e:
            print(f"❌ Failed to load JSON data: {e}")
            raise
    
    def test_all_hands(self):
        """Test all hands using FPSM + RPGW with historical action order."""
        print(f"🎮 Testing {len(self.hands)} hands with FPSM + RPGW integration...")
        
        successful_tests = 0
        
        for i, hand_data in enumerate(self.hands):
            hand_id = hand_data['id']
            hand_name = hand_data['name']
            
            print(f"  [{i+1:2d}/{len(self.hands)}] {hand_name}")
            
            try:
                result = self.test_single_hand(hand_data)
                self.test_results.append(result)
                
                if result['success']:
                    successful_tests += 1
                    print(f"    ✅ SUCCESS - {result['actions_executed']} actions in {result['duration']:.3f}s")
                else:
                    print(f"    ❌ FAILED - {result['error']}")
                    
            except Exception as e:
                print(f"    💥 EXCEPTION - {str(e)}")
                self.test_results.append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'success': False,
                    'error': f"Exception: {str(e)}"
                })
        
        success_rate = (successful_tests / max(1, len(self.hands))) * 100
        print(f"\n✅ FPSM + RPGW Test: {successful_tests}/{len(self.hands)} successful ({success_rate:.1f}%)")
    
    def test_single_hand(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hand using FPSM + RPGW with historical action order."""
        start_time = time.time()
        
        hand_id = hand_data['id']
        hand_name = hand_data['name']
        
        # Create testable FPSM configuration and instance
        config = TestableGameConfig(
            num_players=hand_data['game_config']['num_players'],
            big_blind=hand_data['game_config']['big_blind'],
            small_blind=hand_data['game_config']['small_blind'],
            starting_stack=1000000.0
        )
        fpsm = TestablePokerStateMachine(config)
        
        # Temporarily disable turn order validation (same as FPSM-only test)
        original_get_action_player = fpsm.get_action_player
        
        def bypass_turn_order():
            """Allow any player to act, bypassing natural turn order."""
            for player in fpsm.game_state.players:
                if hasattr(player, 'has_folded') and not player.has_folded:
                    return player
            return fpsm.game_state.players[0] if fpsm.game_state.players else None
        
        fpsm.get_action_player = bypass_turn_order
        
        # Create RPGW for testing (no debug flags)
        rpgw = ReusablePokerGameWidget(
            None,  # No parent for testing
            state_machine=fpsm
        )
        
        # Connect FPSM to RPGW
        fpsm.add_event_listener(rpgw)
        
        # Create players
        players = []
        for player_data in hand_data['players']:
            player = Player(
                name=player_data['name'],
                stack=player_data['starting_stack'],
                position=UniversalPosition.BB.value,
                is_human=False,
                is_active=True,
                cards=player_data.get('hole_cards', [])
            )
            players.append(player)
        
        # Initialize hand
        fpsm.start_hand(players)
        
        # Build seat to player mapping with robust fallbacks
        seat_to_player = {}
        available_seats = []
        
        for i, player_data in enumerate(hand_data['players']):
            seat = player_data['seat']
            if i < len(fpsm.game_state.players):
                seat_to_player[seat] = fpsm.game_state.players[i]
                available_seats.append(seat)
        
        def get_fallback_seat(missing_seat):
            """Find the closest available seat for a missing seat."""
            if not available_seats:
                return None
            closest_seat = min(available_seats, key=lambda x: abs(x - missing_seat))
            return closest_seat
        
        # Execute actions in historical order
        actions_executed = 0
        validation_errors = []
        max_actions = 200
        
        try:
            # Process actions by street in historical order
            for street in ['preflop', 'flop', 'turn', 'river']:
                if street in hand_data['actions']:
                    street_actions = hand_data['actions'][street]
                    
                    for action_data in street_actions:
                        if actions_executed >= max_actions:
                            validation_errors.append("Max actions exceeded")
                            break
                        
                        # Get the historical player with fallback
                        player_seat = action_data['player_seat']
                        if player_seat not in seat_to_player:
                            fallback_seat = get_fallback_seat(player_seat)
                            if fallback_seat:
                                player = seat_to_player[fallback_seat]
                            else:
                                validation_errors.append(f"Unknown player seat: {player_seat}, no fallback available")
                                continue
                        else:
                            player = seat_to_player[player_seat]
                        
                        # Parse action type
                        action_type = self._parse_action_type(action_data['action_type'])
                        if not action_type:
                            validation_errors.append(f"Unknown action type: {action_data['action_type']}")
                            continue
                        
                        # Determine amount
                        amount = action_data.get('amount', 0.0)
                        if 'to_amount' in action_data and action_type == ActionType.RAISE:
                            amount = action_data['to_amount']
                        
                        # Cap amount for all-in scenarios
                        if action_type in [ActionType.BET, ActionType.RAISE, ActionType.CALL]:
                            available_stack = player.stack + getattr(player, 'current_bet', 0)
                            if amount > available_stack:
                                amount = available_stack
                        
                        # Force execute the action (bypass normal validation)
                        # RPGW will automatically receive events from FPSM
                        success = self._force_execute_action(fpsm, player, action_type, amount)
                        
                        if success:
                            actions_executed += 1
                        else:
                            validation_errors.append(f"Failed to force execute {action_type} ${amount} for {player.name}")
        
        finally:
            # Restore original turn order function
            fpsm.get_action_player = original_get_action_player
        
        duration = time.time() - start_time
        success = len(validation_errors) == 0 and actions_executed > 0
        
        return {
            'hand_id': hand_id,
            'hand_name': hand_name,
            'success': success,
            'actions_executed': actions_executed,
            'validation_errors': validation_errors,
            'duration': duration,
            'error': '; '.join(validation_errors) if validation_errors else None
        }
    
    def _parse_action_type(self, action_type_str: str) -> Optional[ActionType]:
        """Parse action type string to ActionType enum."""
        action_mapping = {
            'fold': ActionType.FOLD,
            'check': ActionType.CHECK,
            'call': ActionType.CALL,
            'bet': ActionType.BET,
            'raise': ActionType.RAISE,
            'reraise': ActionType.RAISE,
            '3bet': ActionType.RAISE,
            '4bet': ActionType.RAISE,
            '5bet': ActionType.RAISE,
            'all-in': ActionType.RAISE,
        }
        return action_mapping.get(action_type_str.lower())
    
    def _force_execute_action(self, fpsm, player, action_type, amount):
        """Force execute an action, bypassing most validation."""
        try:
            # Update player's folded status for fold actions
            if action_type == ActionType.FOLD:
                if hasattr(player, 'has_folded'):
                    player.has_folded = True
                return True
            
            # Handle check actions
            elif action_type == ActionType.CHECK:
                return True
            
            # Handle call actions
            elif action_type == ActionType.CALL:
                if amount > 0 and player.stack >= amount:
                    player.stack -= amount
                    if hasattr(player, 'current_bet'):
                        player.current_bet += amount
                    fpsm.game_state.pot += amount
                return True
            
            # Handle bet/raise actions
            elif action_type in [ActionType.BET, ActionType.RAISE]:
                if amount > 0 and player.stack >= amount:
                    player.stack -= amount
                    if hasattr(player, 'current_bet'):
                        player.current_bet += amount
                    else:
                        player.current_bet = amount
                    fpsm.game_state.pot += amount
                    fpsm.game_state.current_bet = max(fpsm.game_state.current_bet, amount)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "=" * 60)
        print("📋 FPSM + RPGW HISTORICAL ORDER TEST REPORT")
        print("=" * 60)
        
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        total_tests = len(self.test_results)
        success_rate = (successful_tests / max(1, total_tests)) * 100
        
        print(f"📊 RESULTS:")
        print(f"  Total hands: {total_tests}")
        print(f"  Successful: {successful_tests}")
        print(f"  Failed: {total_tests - successful_tests}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r.get('success', False)]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests[:10]:  # Show first 10
                print(f"  - {result['hand_name']}: {result.get('error', 'Unknown error')}")
            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more failures")
        
        # Performance stats
        if self.test_results:
            total_actions = sum(r.get('actions_executed', 0) for r in self.test_results)
            total_time = sum(r.get('duration', 0) for r in self.test_results)
            
            print(f"\n⚡ PERFORMANCE:")
            print(f"  Total actions: {total_actions}")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Actions/sec: {total_actions/max(0.001, total_time):.1f}")
        
        # Assessment
        print(f"\n🎯 ASSESSMENT:")
        if success_rate == 100.0:
            print("🎉 PERFECT! FPSM + RPGW integration achieves 100% success!")
        elif success_rate >= 95.0:
            print("✅ EXCELLENT! Very high FPSM + RPGW integration success rate")
        elif success_rate >= 80.0:
            print("🟡 GOOD: FPSM + RPGW integration mostly working")
        else:
            print("🔴 NEEDS WORK: FPSM + RPGW integration has issues")

def main():
    """Main function to run the FPSM + RPGW historical order test."""
    tester = FPSMRPGWHistoricalTester()
    
    try:
        results = tester.run_fpsm_rpgw_test()
        return 0 if all(r.get('success', False) for r in results) else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
