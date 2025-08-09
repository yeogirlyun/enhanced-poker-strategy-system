#!/usr/bin/env python3
"""
Complete JSON Format Comprehensive Tester

Tests FPSM, FPSM + RPGW, and Hands Review Panel using the complete JSON format
that preserves 100% of the original PHH information including stakes, events,
board cards, positions, and all metadata.
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player, ActionType, PokerState
from core.position_mapping import UniversalPosition
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

class CompleteJSONTester:
    """Comprehensive tester using complete JSON format."""
    
    def __init__(self):
        self.json_data = None
        self.hands = []
        self.test_results = {
            'fpsm_only': [],
            'fpsm_rpgw': [],
            'summary': {}
        }
        
    def run_comprehensive_tests(self):
        """Run all tests using complete JSON format."""
        print("🎯 COMPREHENSIVE TESTS USING COMPLETE JSON FORMAT")
        print("=" * 70)
        
        # Step 1: Load complete JSON data
        self.load_pure_json_data()
        
        # Step 2: Test FPSM only
        self.test_fpsm_only()
        
        # Step 3: Test FPSM + RPGW
        self.test_fpsm_rpgw()
        
        # Step 4: Generate comprehensive report
        self.generate_comprehensive_report()
        
        return self.test_results
    
    def load_pure_json_data(self):
        """Load the complete JSON format hands data."""
        json_file_path = "data/legendary_hands_complete.json"
        
        print(f"📚 Loading pure JSON data from {json_file_path}...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            self.hands = self.json_data['hands']
            
            print(f"✅ Loaded {len(self.hands)} hands from complete JSON")
            print(f"   Format: {self.json_data['format_version']}")
            print(f"   Source: {self.json_data['data_source']}")
            print(f"   Features: {len(self.json_data.get('features', []))} data preservation features")
            
        except Exception as e:
            print(f"❌ Failed to load pure JSON data: {e}")
            raise
    
    def test_fpsm_only(self):
        """Test pure FPSM logic using the complete JSON format."""
        print(f"\n🎮 TESTING FPSM ONLY (Complete JSON)")
        print("=" * 50)
        
        successful_tests = 0
        total_hands = len(self.hands)
        
        for i, hand_data in enumerate(self.hands):
            hand_id = hand_data['id']
            hand_name = hand_data['name']
            
            print(f"  [{i+1:2d}/{total_hands}] {hand_name}")
            
            try:
                result = self.test_single_hand_fpsm(hand_data)
                self.test_results['fpsm_only'].append(result)
                
                if result['success']:
                    successful_tests += 1
                    print(f"    ✅ SUCCESS - {result['actions_executed']} actions")
                else:
                    print(f"    ❌ FAILED - {result['error']}")
                    
            except Exception as e:
                print(f"    💥 EXCEPTION - {str(e)}")
                self.test_results['fpsm_only'].append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'success': False,
                    'error': f"Exception: {str(e)}"
                })
        
        success_rate = (successful_tests / max(1, total_hands)) * 100
        print(f"\n✅ FPSM Only: {successful_tests}/{total_hands} successful ({success_rate:.1f}%)")
        self.test_results['summary']['fpsm_only'] = {
            'successful': successful_tests,
            'total': total_hands,
            'success_rate': success_rate
        }
    
    def test_fpsm_rpgw(self):
        """Test FPSM + RPGW integration using the complete JSON format."""
        print(f"\n🎮 TESTING FPSM + RPGW (Complete JSON)")
        print("=" * 50)
        
        successful_tests = 0
        total_hands = len(self.hands)
        
        for i, hand_data in enumerate(self.hands):
            hand_id = hand_data['id']
            hand_name = hand_data['name']
            
            print(f"  [{i+1:2d}/{total_hands}] {hand_name}")
            
            try:
                result = self.test_single_hand_fpsm_rpgw(hand_data)
                self.test_results['fpsm_rpgw'].append(result)
                
                if result['success']:
                    successful_tests += 1
                    print(f"    ✅ SUCCESS - {result['actions_executed']} actions")
                else:
                    print(f"    ❌ FAILED - {result['error']}")
                    
            except Exception as e:
                print(f"    💥 EXCEPTION - {str(e)}")
                self.test_results['fpsm_rpgw'].append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'success': False,
                    'error': f"Exception: {str(e)}"
                })
        
        success_rate = (successful_tests / max(1, total_hands)) * 100
        print(f"\n✅ FPSM + RPGW: {successful_tests}/{total_hands} successful ({success_rate:.1f}%)")
        self.test_results['summary']['fpsm_rpgw'] = {
            'successful': successful_tests,
            'total': total_hands,
            'success_rate': success_rate
        }
    
    def test_single_hand_fpsm(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hand with pure FPSM logic."""
        start_time = time.time()
        
        hand_id = hand_data['id']
        hand_name = hand_data['name']
        
        # Create FPSM configuration from complete JSON
        config = GameConfig(
            num_players=hand_data['game_config']['num_players'],
            big_blind=hand_data['game_config']['big_blind'],
            small_blind=hand_data['game_config']['small_blind'],
            starting_stack=1000000.0,  # Will be overridden per player
            test_mode=True
        )
        
        # Create FPSM instance
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players from complete JSON
        players = []
        for player_data in hand_data['players']:
            player = Player(
                name=player_data['name'],
                stack=player_data['starting_stack'],
                position=UniversalPosition.BB.value,  # Will be set by FPSM
                is_human=False,
                is_active=True,
                cards=player_data.get('hole_cards', [])
            )
            players.append(player)
        
        # Initialize the hand
        fpsm.start_hand(players)
        
        # Build seat to player mapping with validation
        seat_to_player = {}
        for i, player_data in enumerate(hand_data['players']):
            seat = player_data['seat']
            if i < len(fpsm.game_state.players):
                seat_to_player[seat] = fpsm.game_state.players[i]
            else:
                validation_errors.append(f"Player index {i} exceeds FPSM players list")
        
        # Add fallback mapping for missing seats (map to closest valid player)
        max_seat = max(seat_to_player.keys()) if seat_to_player else 1
        
        # Execute actions from complete JSON
        actions_executed = 0
        validation_errors = []
        max_actions = 100
        
        # Process actions by street
        for street in ['preflop', 'flop', 'turn', 'river']:
            if street in hand_data['actions']:
                street_actions = hand_data['actions'][street]
                
                for action_data in street_actions:
                    if actions_executed >= max_actions:
                        validation_errors.append("Max actions exceeded")
                        break
                    
                    # Get player from seat mapping with fallback
                    player_seat = action_data['player_seat']
                    if player_seat not in seat_to_player:
                        # Try to find a fallback player or skip this action
                        if seat_to_player:
                            # Use the first available player as fallback
                            fallback_seat = min(seat_to_player.keys())
                            player = seat_to_player[fallback_seat]
                            validation_errors.append(f"Seat {player_seat} not found, using fallback seat {fallback_seat}")
                        else:
                            validation_errors.append(f"Unknown player seat: {player_seat}, no fallback available")
                            continue
                    else:
                        player = seat_to_player[player_seat]
                    
                    # Parse action
                    action_type = self._parse_action_type(action_data['action_type'])
                    if not action_type:
                        validation_errors.append(f"Unknown action type: {action_data['action_type']}")
                        continue
                    
                    # Determine amount with better handling
                    amount = action_data.get('amount', 0.0)
                    if 'to_amount' in action_data and action_type == ActionType.RAISE:
                        amount = action_data['to_amount']
                    
                    # Cap amount at player's available stack for all-in handling
                    if action_type in [ActionType.BET, ActionType.RAISE, ActionType.CALL]:
                        max_available = player.stack + getattr(player, 'current_bet', 0)
                        if amount > max_available:
                            original_amount = amount
                            amount = max_available
                            validation_errors.append(f"Capped {action_type} from ${original_amount} to ${amount} (all-in) for {player.name}")
                    
                    # Execute action
                    success = fpsm.execute_action(player, action_type, amount)
                    if success:
                        actions_executed += 1
                    else:
                        # Try to diagnose why the action failed
                        error_reason = f"Failed to execute {action_type} ${amount} for {player.name}"
                        if hasattr(player, 'stack'):
                            error_reason += f" (stack: ${player.stack})"
                        if hasattr(player, 'current_bet'):
                            error_reason += f" (current_bet: ${getattr(player, 'current_bet', 0)})"
                        validation_errors.append(error_reason)
        
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
    
    def test_single_hand_fpsm_rpgw(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hand with FPSM + RPGW integration."""
        start_time = time.time()
        
        hand_id = hand_data['id']
        hand_name = hand_data['name']
        
        # Create FPSM configuration
        config = GameConfig(
            num_players=hand_data['game_config']['num_players'],
            big_blind=hand_data['game_config']['big_blind'],
            small_blind=hand_data['game_config']['small_blind'],
            starting_stack=1000000.0,
            test_mode=True
        )
        
        # Create FPSM instance
        fpsm = FlexiblePokerStateMachine(config)
        
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
        
        # Initialize the hand
        fpsm.start_hand(players)
        
        # Create RPGW in debug mode
        rpgw = ReusablePokerGameWidget(
            None,  # No parent for testing
            state_machine=fpsm,
            debug_mode=True  # Skip animations and delays
        )
        
        # Connect FPSM to RPGW
        fpsm.add_event_listener(rpgw)
        
        # Build seat to player mapping with validation
        seat_to_player = {}
        for i, player_data in enumerate(hand_data['players']):
            seat = player_data['seat']
            if i < len(fpsm.game_state.players):
                seat_to_player[seat] = fpsm.game_state.players[i]
            else:
                validation_errors.append(f"Player index {i} exceeds FPSM players list")
        
        # Execute actions (similar to FPSM-only test)
        actions_executed = 0
        validation_errors = []
        max_actions = 100
        
        for street in ['preflop', 'flop', 'turn', 'river']:
            if street in hand_data['actions']:
                for action_data in hand_data['actions'][street]:
                    if actions_executed >= max_actions:
                        break
                    
                    player_seat = action_data['player_seat']
                    if player_seat not in seat_to_player:
                        # Use fallback for missing seats
                        if seat_to_player:
                            fallback_seat = min(seat_to_player.keys())
                            player = seat_to_player[fallback_seat]
                            validation_errors.append(f"Seat {player_seat} not found, using fallback seat {fallback_seat}")
                        else:
                            validation_errors.append(f"Unknown player seat: {player_seat}, no fallback available")
                            continue
                    else:
                        player = seat_to_player[player_seat]
                    
                    action_type = self._parse_action_type(action_data['action_type'])
                    
                    if not action_type:
                        validation_errors.append(f"Unknown action type: {action_data['action_type']}")
                        continue
                    
                    amount = action_data.get('amount', 0.0)
                    if 'to_amount' in action_data and action_type == ActionType.RAISE:
                        amount = action_data['to_amount']
                    
                    # Cap amount at player's available stack for all-in handling
                    if action_type in [ActionType.BET, ActionType.RAISE, ActionType.CALL]:
                        max_available = player.stack + getattr(player, 'current_bet', 0)
                        if amount > max_available:
                            original_amount = amount
                            amount = max_available
                            validation_errors.append(f"Capped {action_type} from ${original_amount} to ${amount} (all-in) for {player.name}")
                    
                    # Execute through FPSM (RPGW receives events automatically)
                    success = fpsm.execute_action(player, action_type, amount)
                    if success:
                        actions_executed += 1
                    else:
                        error_reason = f"Failed to execute {action_type} ${amount} for {player.name}"
                        if hasattr(player, 'stack'):
                            error_reason += f" (stack: ${player.stack})"
                        validation_errors.append(error_reason)
        
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
            'reraise': ActionType.RAISE,  # Reraise is a raise
            '3bet': ActionType.RAISE,     # 3bet is a raise
            '4bet': ActionType.RAISE,     # 4bet is a raise
            '5bet': ActionType.RAISE,     # 5bet is a raise
            'all-in': ActionType.RAISE,  # All-in is treated as raise
        }
        return action_mapping.get(action_type_str.lower())
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE TEST REPORT (Complete JSON Format)")
        print("=" * 70)
        
        # Overall summary
        fpsm_summary = self.test_results['summary']['fpsm_only']
        rpgw_summary = self.test_results['summary']['fpsm_rpgw']
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Complete JSON Hands: {len(self.hands)}")
        print(f"   FPSM Only:       {fpsm_summary['successful']}/{fpsm_summary['total']} ({fpsm_summary['success_rate']:.1f}%)")
        print(f"   FPSM + RPGW:     {rpgw_summary['successful']}/{rpgw_summary['total']} ({rpgw_summary['success_rate']:.1f}%)")
        
        # Performance stats
        fpsm_results = self.test_results['fpsm_only']
        rpgw_results = self.test_results['fpsm_rpgw']
        
        if fpsm_results:
            fpsm_actions = sum(r.get('actions_executed', 0) for r in fpsm_results)
            fpsm_time = sum(r.get('duration', 0) for r in fpsm_results)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   FPSM Total Actions: {fpsm_actions}")
            print(f"   FPSM Total Time:    {fpsm_time:.3f}s")
            print(f"   FPSM Actions/sec:   {fpsm_actions/max(0.001, fpsm_time):.1f}")
        
        if rpgw_results:
            rpgw_actions = sum(r.get('actions_executed', 0) for r in rpgw_results)
            rpgw_time = sum(r.get('duration', 0) for r in rpgw_results)
            print(f"   RPGW Total Actions: {rpgw_actions}")
            print(f"   RPGW Total Time:    {rpgw_time:.3f}s")
            print(f"   RPGW Actions/sec:   {rpgw_actions/max(0.001, rpgw_time):.1f}")
        
        # Failed tests summary
        fpsm_failed = [r for r in fpsm_results if not r.get('success', False)]
        rpgw_failed = [r for r in rpgw_results if not r.get('success', False)]
        
        if fpsm_failed:
            print(f"\n❌ FPSM FAILURES ({len(fpsm_failed)}):")
            for result in fpsm_failed[:5]:  # Show first 5
                print(f"   - {result['hand_name']}: {result.get('error', 'Unknown error')}")
            if len(fpsm_failed) > 5:
                print(f"   ... and {len(fpsm_failed) - 5} more")
        
        if rpgw_failed:
            print(f"\n❌ RPGW FAILURES ({len(rpgw_failed)}):")
            for result in rpgw_failed[:5]:  # Show first 5
                print(f"   - {result['hand_name']}: {result.get('error', 'Unknown error')}")
            if len(rpgw_failed) > 5:
                print(f"   ... and {len(rpgw_failed) - 5} more")
        
        # Assessment
        avg_success = (fpsm_summary['success_rate'] + rpgw_summary['success_rate']) / 2
        print(f"\n🎯 ASSESSMENT:")
        if avg_success >= 95.0:
            print("🎉 EXCELLENT! Pure JSON format provides very high success rates")
        elif avg_success >= 85.0:
            print("✅ GOOD! Pure JSON format works well with minor issues")
        elif avg_success >= 70.0:
            print("🟡 FAIR: Pure JSON format mostly works, some integration issues")
        else:
            print("🔴 NEEDS WORK: Significant issues even with pure JSON format")
        
        print(f"\n📝 COMPLETE JSON FORMAT BENEFITS:")
        print(f"   ✅ 100% PHH information preserved")
        print(f"   ✅ Complete game metadata (stakes, event, date)")
        print(f"   ✅ Full board cards (flop, turn, river)")
        print(f"   ✅ Enhanced actor mapping")
        print(f"   ✅ Accurate position assignments")
        print(f"   ✅ Machine-readable format")
        print(f"   ✅ No simulation artifacts")

def main():
    """Main function to run the complete JSON format tests."""
    tester = CompleteJSONTester()
    
    try:
        results = tester.run_comprehensive_tests()
        
        # Return 0 if both tests have high success rates
        fpsm_rate = results['summary']['fpsm_only']['success_rate']
        rpgw_rate = results['summary']['fpsm_rpgw']['success_rate']
        
        return 0 if (fpsm_rate >= 90.0 and rpgw_rate >= 90.0) else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
