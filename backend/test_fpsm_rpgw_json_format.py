#!/usr/bin/env python3
"""
FPSM + RPGW JSON Format Tester

Tests FPSM + RPGW integration using JSON format hands and the original action data
instead of simulation steps to avoid turn order issues.
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player, ActionType, PokerState
from core.position_mapping import UniversalPosition
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

class FPSMRPGWJSONTester:
    """Tests FPSM + RPGW integration using JSON format legendary hands."""
    
    def __init__(self):
        self.json_data = None
        self.hands = []
        self.test_results = []
        self.total_hands = 0
        self.successful_tests = 0
        self.errors = []
        
    def run_comprehensive_test(self):
        """Run comprehensive FPSM + RPGW tests using JSON format."""
        print("🎯 FPSM + RPGW JSON FORMAT COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Step 1: Load JSON data
        self.load_json_data()
        
        # Step 2: Test each hand
        self.test_all_hands()
        
        # Step 3: Generate report
        self.generate_test_report()
        
        return self.test_results
    
    def load_json_data(self):
        """Load the comprehensive JSON legendary hands data."""
        json_file_path = "data/legendary_hands_comprehensive.json"
        
        print(f"📚 Loading JSON data from {json_file_path}...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            self.hands = self.json_data['hands']
            self.total_hands = len(self.hands)
            
            print(f"✅ Loaded {self.total_hands} hands from JSON")
            print(f"   Format version: {self.json_data['format_version']}")
            
        except Exception as e:
            print(f"❌ Failed to load JSON data: {e}")
            raise
    
    def test_all_hands(self):
        """Test all hands with FPSM + RPGW."""
        print(f"🎮 Testing {self.total_hands} hands with FPSM + RPGW...")
        
        for i, hand_data in enumerate(self.hands):
            hand_id = hand_data['metadata']['id']
            hand_name = hand_data['metadata']['name']
            
            print(f"  [{i+1:2d}/{self.total_hands}] Testing: {hand_name}")
            
            try:
                result = self.test_single_hand(hand_data)
                self.test_results.append(result)
                
                if result['success']:
                    self.successful_tests += 1
                    print(f"    ✅ SUCCESS - {result['actions_executed']} actions in {result['duration']:.3f}s")
                else:
                    print(f"    ❌ FAILED - {result['error']}")
                    
            except Exception as e:
                error_msg = f"Exception during test: {str(e)}"
                print(f"    💥 EXCEPTION - {error_msg}")
                self.errors.append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'error': error_msg
                })
        
        print(f"✅ Completed testing: {self.successful_tests}/{self.total_hands} successful")
    
    def test_single_hand(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hand using FPSM + RPGW in headless mode."""
        start_time = time.time()
        
        hand_id = hand_data['metadata']['id']
        hand_name = hand_data['metadata']['name']
        
        # Create FPSM configuration from JSON data
        config_data = hand_data['initial_config']
        config = GameConfig(
            num_players=config_data['num_players'],
            big_blind=config_data['big_blind'],
            small_blind=config_data['small_blind'],
            starting_stack=1000000.0,  # Default, will be overridden per player
            test_mode=True
        )
        
        # Create FPSM instance
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players from JSON data
        players = []
        for player_data in hand_data['players']:
            player = Player(
                name=player_data['name'],
                stack=player_data['starting_stack'],
                position=UniversalPosition.BB.value,  # Will be set correctly by FPSM
                is_human=False,
                is_active=True,
                cards=player_data.get('cards', [])
            )
            players.append(player)
        
        # Initialize the hand
        fpsm.start_hand(players)
        
        # Create RPGW in debug mode for testing (no headless mode available)
        rpgw = ReusablePokerGameWidget(
            None,  # No parent for testing
            state_machine=fpsm,
            debug_mode=True  # Skip animations and delays
        )
        
        # Connect FPSM to RPGW
        rpgw.fpsm = fpsm
        fpsm.add_event_listener(rpgw)
        
        # Build actor mapping from JSON
        actor_to_fpsm = hand_data.get('actor_mapping', {})
        
        # Get actions by street from JSON (original action data, not simulation steps)
        actions_by_street = hand_data.get('streets', {})
        
        # Execute actions step by step
        actions_executed = 0
        validation_errors = []
        max_actions = 200
        timeout_seconds = 30
        
        # Process all actions in chronological order
        all_actions = []
        for street in ['preflop', 'flop', 'turn', 'river']:
            if street in actions_by_street:
                street_actions = actions_by_street[street].get('actions', [])
                for action in street_actions:
                    all_actions.append((street, action))
        
        action_index = 0
        while (action_index < len(all_actions) and 
               actions_executed < max_actions and 
               not self._is_hand_complete(fpsm) and
               time.time() - start_time < timeout_seconds):
            
            # Get current action player
            current_player = fpsm.get_action_player()
            if not current_player:
                validation_errors.append(f"Action {action_index}: No action player available")
                break
            
            # Get next action
            street, action_data = all_actions[action_index]
            action_index += 1
            
            # Parse action
            action_type = self._parse_action_type(action_data.get('action_type', ''))
            action_amount = action_data.get('amount', 0.0)
            
            if not action_type:
                validation_errors.append(f"Action {action_index}: Unknown action type {action_data.get('action_type')}")
                continue
            
            # Execute action through FPSM (RPGW will receive events automatically)
            success = fpsm.execute_action(current_player, action_type, action_amount)
            
            if success:
                actions_executed += 1
            else:
                validation_errors.append(f"Action {action_index}: Failed to execute {action_type} ${action_amount}")
                # Don't break, let it continue to see how far it gets
        
        # Check completion status
        is_complete = self._is_hand_complete(fpsm)
        reached_timeout = time.time() - start_time >= timeout_seconds
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Determine success criteria
        success = (
            len(validation_errors) == 0 and 
            actions_executed > 0 and 
            not reached_timeout
        )
        
        # Compile error message
        error_parts = []
        if validation_errors:
            error_parts.append(f"{len(validation_errors)} validation errors")
        if reached_timeout:
            error_parts.append("timeout")
        if actions_executed == 0:
            error_parts.append("no actions executed")
        
        error_msg = "; ".join(error_parts) if error_parts else None
        
        return {
            'hand_id': hand_id,
            'hand_name': hand_name,
            'success': success,
            'actions_executed': actions_executed,
            'expected_actions': len(all_actions),
            'validation_errors': validation_errors,
            'duration': duration,
            'is_complete': is_complete,
            'reached_timeout': reached_timeout,
            'error': error_msg
        }
    
    def _parse_action_type(self, action_type_str: str) -> Optional[ActionType]:
        """Parse action type string to ActionType enum."""
        action_mapping = {
            'fold': ActionType.FOLD,
            'check': ActionType.CHECK,
            'call': ActionType.CALL,
            'bet': ActionType.BET,
            'raise': ActionType.RAISE,
        }
        return action_mapping.get(action_type_str.lower())
    
    def _is_hand_complete(self, fpsm) -> bool:
        """Check if the hand simulation is complete."""
        if not fpsm or not hasattr(fpsm, 'current_state'):
            return True
        
        terminal_states = [PokerState.END_HAND, PokerState.SHOWDOWN]
        return fpsm.current_state in terminal_states
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 60)
        print("📋 FPSM + RPGW JSON FORMAT TEST REPORT")
        print("=" * 60)
        
        success_rate = (self.successful_tests / max(1, self.total_hands)) * 100
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"  Total hands tested: {self.total_hands}")
        print(f"  Successful tests: {self.successful_tests}")
        print(f"  Failed tests: {self.total_hands - self.successful_tests}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        # Completion statistics
        completed_hands = sum(1 for r in self.test_results if r['is_complete'])
        timeout_hands = sum(1 for r in self.test_results if r['reached_timeout'])
        
        print(f"\n📈 COMPLETION STATISTICS:")
        print(f"  Hands completed: {completed_hands}/{self.total_hands}")
        print(f"  Hands with timeout: {timeout_hands}")
        
        # Show failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests[:10]:  # Show first 10
                print(f"  - {result['hand_name']}: {result['error']}")
            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more failures")
        
        # Show exceptions
        if self.errors:
            print(f"\n💥 EXCEPTIONS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error['hand_name']}: {error['error']}")
        
        # Performance statistics
        if self.test_results:
            total_actions = sum(r['actions_executed'] for r in self.test_results)
            total_time = sum(r['duration'] for r in self.test_results)
            avg_time = total_time / len(self.test_results)
            
            print(f"\n⚡ PERFORMANCE:")
            print(f"  Total actions executed: {total_actions}")
            print(f"  Total test time: {total_time:.3f}s")
            print(f"  Average time per hand: {avg_time:.3f}s")
            print(f"  Actions per second: {total_actions/max(0.001, total_time):.1f}")
        
        # Success rate assessment
        print(f"\n🎯 ASSESSMENT:")
        if success_rate == 100.0:
            print("🎉 PERFECT! All hands tested successfully with FPSM + RPGW!")
        elif success_rate >= 95.0:
            print("✅ EXCELLENT! FPSM + RPGW integration works very well")
        elif success_rate >= 90.0:
            print("🟡 GOOD: Most hands successful, minor integration issues")
        else:
            print("🔴 NEEDS WORK: Significant FPSM + RPGW integration issues")

def main():
    """Main function to run the FPSM + RPGW JSON format test."""
    tester = FPSMRPGWJSONTester()
    
    try:
        results = tester.run_comprehensive_test()
        return 0 if tester.successful_tests == tester.total_hands else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
