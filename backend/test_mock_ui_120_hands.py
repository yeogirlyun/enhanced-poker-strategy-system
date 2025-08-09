#!/usr/bin/env python3
"""
Mock UI Testing for All 120 Legendary Hands
==========================================

Comprehensive test to replicate GUI issues and validate all 120 hands
using mock UI testing without requiring actual GUI interaction.

This test will:
✅ Replicate street transition issues (preflop stuck)
✅ Test player highlighting logic
✅ Validate all 120 hands through complete simulation
✅ Identify any street progression bugs
✅ Provide detailed debugging output
"""

import sys
import os
import time
import traceback
import tkinter as tk
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, Player, ActionType, PokerState
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget


class MockUI120HandsTester:
    """Mock UI tester to validate all 120 hands and debug GUI issues."""
    
    def __init__(self):
        self.results = {
            'total_hands': 0,
            'successful_simulations': 0,
            'street_transition_issues': 0,
            'highlighting_tests': 0,
            'failed_hands': [],
            'street_progression_data': [],
            'debugging_info': []
        }
        
        # Load all hands
        self.db = ComprehensiveHandsDatabase()
        self.all_hands = self.db.load_all_hands()
        
    def test_all_120_hands_mock_ui(self):
        """Test all 120 hands using mock UI simulation."""
        print("🎯 MOCK UI TESTING FOR ALL 120 LEGENDARY HANDS")
        print("=" * 60)
        print("Replicating GUI issues and validating street transitions")
        print()
        
        # Get all hands for testing
        legendary_hands = self.all_hands.get(HandCategory.LEGENDARY, [])
        practice_hands = self.all_hands.get(HandCategory.PRACTICE, [])
        
        all_hands = legendary_hands + practice_hands
        self.results['total_hands'] = len(all_hands)
        
        print(f"📋 Testing {len(all_hands)} hands:")
        print(f"   • Legendary: {len(legendary_hands)}")
        print(f"   • Practice: {len(practice_hands)}")
        print()
        
        # Test in categories
        print("🎮 CATEGORY 1: LEGENDARY HANDS")
        self._test_hand_category(legendary_hands, "Legendary")
        
        print(f"\n🎮 CATEGORY 2: PRACTICE HANDS")
        self._test_hand_category(practice_hands, "Practice")
        
        # Special tests for street transitions
        print(f"\n🔧 CATEGORY 3: STREET TRANSITION DEBUG")
        self._debug_street_transitions(legendary_hands[:5])  # Test first 5 thoroughly
        
        # Player highlighting test
        print(f"\n🎨 CATEGORY 4: PLAYER HIGHLIGHTING TEST")
        self._test_player_highlighting(legendary_hands[:3])
        
        # Print comprehensive results
        self._print_comprehensive_results()
    
    def _test_hand_category(self, hands: List, category_name: str):
        """Test a category of hands."""
        print(f"------ {category_name} Hands ------")
        
        success_count = 0
        issue_count = 0
        
        for i, hand in enumerate(hands):
            hand_id = getattr(hand.metadata, 'id', f'{category_name}_{i+1}')
            
            try:
                result = self._simulate_hand_mock_ui(hand, hand_id)
                
                if result['success']:
                    success_count += 1
                    print(f"✅ {hand_id}: Simulation successful")
                else:
                    issue_count += 1
                    print(f"❌ {hand_id}: {result['error']}")
                    self.results['failed_hands'].append({
                        'hand_id': hand_id,
                        'error': result['error'],
                        'category': category_name
                    })
                
                # Track street progression data
                if 'street_progression' in result:
                    self.results['street_progression_data'].append({
                        'hand_id': hand_id,
                        'progression': result['street_progression']
                    })
                    
            except Exception as e:
                issue_count += 1
                error_msg = f"Exception: {str(e)}"
                print(f"❌ {hand_id}: {error_msg}")
                self.results['failed_hands'].append({
                    'hand_id': hand_id,
                    'error': error_msg,
                    'category': category_name
                })
        
        print(f"📊 {category_name} Results: {success_count}/{len(hands)} successful")
        self.results['successful_simulations'] += success_count
    
    def _simulate_hand_mock_ui(self, hand, hand_id: str) -> Dict:
        """Simulate a hand using mock UI components."""
        try:
            # Extract hand data
            players = getattr(hand, 'players', [])
            actions = getattr(hand, 'actions', {})
            board = getattr(hand, 'board', {})
            
            if len(players) < 2:
                return {'success': False, 'error': 'Insufficient players'}
            
            # Create FPSM configuration
            config = GameConfig(
                num_players=len(players),
                big_blind=1000,
                small_blind=500,
                test_mode=False,  # Use real simulation
                show_all_cards=True
            )
            
            # Initialize FPSM
            fpsm = FlexiblePokerStateMachine(config)
            
            # Create FPSM players from hand data
            fpsm_players = []
            for i, player_data in enumerate(players):
                name = player_data.get('name', f'Player_{i+1}')
                stack = player_data.get('starting_stack_chips', 100000)
                cards = player_data.get('cards', ['**', '**'])
                
                fpsm_player = Player(
                    name=name,
                    stack=stack,
                    position="",
                    is_human=False,
                    is_active=True,
                    cards=cards
                )
                fpsm_players.append(fpsm_player)
            
            # Start hand
            fpsm.start_hand(existing_players=fpsm_players)
            
            # Track street progression
            street_progression = []
            
            # Simulate basic actions to test street transitions
            max_actions = 20  # Prevent infinite loops
            action_count = 0
            
            while (fpsm.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN] and 
                   action_count < max_actions):
                
                current_street = fpsm.game_state.street
                current_state = fpsm.current_state
                
                # Record street progression
                street_progression.append({
                    'action_count': action_count,
                    'street': current_street,
                    'state': current_state.name,
                    'action_player': fpsm.action_player_index
                })
                
                # Get current action player
                if fpsm.action_player_index >= 0 and fpsm.action_player_index < len(fpsm.game_state.players):
                    current_player = fpsm.game_state.players[fpsm.action_player_index]
                    
                    # Get valid actions
                    valid_actions = fpsm.get_valid_actions_for_player(current_player)
                    
                    # Choose a simple action (check/call or fold)
                    if valid_actions.get('check', False):
                        action = ActionType.CHECK
                        amount = 0.0
                    elif valid_actions.get('call', False):
                        action = ActionType.CALL
                        amount = valid_actions.get('call_amount', 0.0)
                    elif valid_actions.get('fold', False):
                        action = ActionType.FOLD
                        amount = 0.0
                    else:
                        # If no valid actions, something is wrong
                        break
                    
                    # Execute action
                    success = fpsm.execute_action(current_player, action, amount)
                    if not success:
                        break
                        
                else:
                    # No valid action player
                    break
                
                action_count += 1
            
            # Check if we made progress through streets
            streets_visited = set(sp['street'] for sp in street_progression)
            
            result = {
                'success': True,
                'street_progression': street_progression,
                'streets_visited': list(streets_visited),
                'final_state': fpsm.current_state.name,
                'action_count': action_count
            }
            
            # Check for street transition issues
            if len(streets_visited) == 1 and 'preflop' in streets_visited:
                self.results['street_transition_issues'] += 1
                result['success'] = False
                result['error'] = 'Stuck on preflop - street transition issue'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Simulation exception: {str(e)}',
                'traceback': traceback.format_exc()
            }
    
    def _debug_street_transitions(self, hands: List):
        """Debug street transition issues in detail."""
        print("------ Street Transition Debug ------")
        
        for i, hand in enumerate(hands):
            hand_id = getattr(hand.metadata, 'id', f'Debug_{i+1}')
            print(f"\n🔍 Debugging {hand_id}:")
            
            try:
                # Create detailed FPSM simulation
                players = getattr(hand, 'players', [])
                
                config = GameConfig(
                    num_players=len(players),
                    big_blind=1000,
                    small_blind=500
                )
                
                fpsm = FlexiblePokerStateMachine(config)
                
                # Create players
                fpsm_players = []
                for j, player_data in enumerate(players):
                    name = player_data.get('name', f'Player_{j+1}')
                    fpsm_player = Player(
                        name=name,
                        stack=100000,
                        position="",
                        is_human=False,
                        is_active=True,
                        cards=['As', 'Kd'] if j == 0 else ['**', '**']
                    )
                    fpsm_players.append(fpsm_player)
                
                # Start hand
                fpsm.start_hand(existing_players=fpsm_players)
                
                print(f"   Initial state: {fpsm.current_state.name}")
                print(f"   Initial street: {fpsm.game_state.street}")
                print(f"   Action player: {fpsm.action_player_index}")
                print(f"   Players: {len(fpsm.game_state.players)}")
                
                # Test a few actions to see progression
                for action_num in range(5):
                    if fpsm.action_player_index >= 0:
                        current_player = fpsm.game_state.players[fpsm.action_player_index]
                        valid_actions = fpsm.get_valid_actions_for_player(current_player)
                        
                        print(f"   Action {action_num + 1}: Player {current_player.name}")
                        print(f"      Valid actions: {list(valid_actions.keys())}")
                        
                        # Execute check or call
                        if valid_actions.get('check', False):
                            success = fpsm.execute_action(current_player, ActionType.CHECK, 0.0)
                            print(f"      Executed: CHECK -> Success: {success}")
                        elif valid_actions.get('call', False):
                            call_amount = valid_actions.get('call_amount', 0.0)
                            success = fpsm.execute_action(current_player, ActionType.CALL, call_amount)
                            print(f"      Executed: CALL {call_amount} -> Success: {success}")
                        
                        print(f"      New state: {fpsm.current_state.name}")
                        print(f"      New street: {fpsm.game_state.street}")
                        print(f"      Next action player: {fpsm.action_player_index}")
                        
                        # Check if state changed
                        if fpsm.current_state in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                            print(f"      Hand ended, final state: {fpsm.current_state.name}")
                            break
                    else:
                        print(f"   Action {action_num + 1}: No valid action player")
                        break
                
            except Exception as e:
                print(f"   ❌ Debug exception: {str(e)}")
    
    def _test_player_highlighting(self, hands: List):
        """Test player highlighting logic."""
        print("------ Player Highlighting Test ------")
        
        for i, hand in enumerate(hands[:3]):  # Test first 3
            hand_id = getattr(hand.metadata, 'id', f'Highlight_{i+1}')
            print(f"\n🎨 Testing highlighting for {hand_id}:")
            
            try:
                # Create minimal UI environment
                root = tk.Tk()
                root.withdraw()  # Hide window
                
                # Create FPSM
                players = getattr(hand, 'players', [])
                config = GameConfig(num_players=len(players), big_blind=1000, small_blind=500)
                fpsm = FlexiblePokerStateMachine(config)
                
                # Create RPGW widget for highlighting test
                rpgw = ReusablePokerGameWidget(root, state_machine=fpsm)
                
                # Test highlighting logic
                for player_idx in range(min(3, len(players))):
                    print(f"   Testing highlight for player {player_idx}")
                    
                    # This would normally be called during action
                    try:
                        rpgw._highlight_current_player(player_idx)
                        print(f"      ✅ Highlighting player {player_idx} successful")
                        self.results['highlighting_tests'] += 1
                    except Exception as e:
                        print(f"      ❌ Highlighting failed: {str(e)}")
                
                # Cleanup
                root.destroy()
                
            except Exception as e:
                print(f"   ❌ Highlighting test exception: {str(e)}")
    
    def _print_comprehensive_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 60)
        print("🏆 MOCK UI TESTING COMPREHENSIVE RESULTS")
        print("=" * 60)
        
        total_hands = self.results['total_hands']
        successful = self.results['successful_simulations']
        failed = len(self.results['failed_hands'])
        success_rate = (successful / total_hands * 100) if total_hands > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   • Total hands tested: {total_hands}")
        print(f"   • Successful simulations: {successful}")
        print(f"   • Failed simulations: {failed}")
        print(f"   • Success rate: {success_rate:.1f}%")
        print(f"   • Street transition issues: {self.results['street_transition_issues']}")
        print(f"   • Highlighting tests: {self.results['highlighting_tests']}")
        print()
        
        # Failed hands analysis
        if self.results['failed_hands']:
            print("❌ FAILED HANDS:")
            for failure in self.results['failed_hands'][:10]:  # Show first 10
                print(f"   • {failure['hand_id']}: {failure['error']}")
            if len(self.results['failed_hands']) > 10:
                print(f"   ... and {len(self.results['failed_hands']) - 10} more")
            print()
        
        # Street progression analysis
        if self.results['street_progression_data']:
            print("🔄 STREET PROGRESSION ANALYSIS:")
            preflop_stuck = 0
            full_progression = 0
            
            for progression in self.results['street_progression_data']:
                streets = set(sp['street'] for sp in progression['progression'])
                if len(streets) == 1 and 'preflop' in streets:
                    preflop_stuck += 1
                elif len(streets) >= 2:
                    full_progression += 1
            
            print(f"   • Hands stuck on preflop: {preflop_stuck}")
            print(f"   • Hands with street progression: {full_progression}")
            print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT! Mock UI testing highly successful")
            if self.results['street_transition_issues'] == 0:
                print("✅ No street transition issues detected")
            else:
                print(f"⚠️  {self.results['street_transition_issues']} street transition issues need fixing")
        elif success_rate >= 70:
            print("✅ GOOD! Most hands simulate successfully")
            print("🔧 Some issues to address for full compatibility")
        else:
            print("⚠️  NEEDS WORK! Significant simulation issues detected")
            print("🔧 Review failed hands and street transition logic")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if self.results['street_transition_issues'] > 0:
            print("   1. Fix street transition logic in FPSM")
            print("   2. Debug round completion detection")
            print("   3. Ensure proper action player advancement")
        
        if self.results['highlighting_tests'] < 5:
            print("   4. Test player highlighting in actual GUI")
            print("   5. Verify visual indicators are working")
        
        print("   6. Test specific failed hands in GUI")
        print("   7. Validate enhanced highlighting visibility")


def main():
    """Run the comprehensive mock UI test for all 120 hands."""
    print("🚀 MOCK UI TESTING - ALL 120 LEGENDARY HANDS")
    print("Debugging GUI issues and validating street transitions")
    print()
    
    tester = MockUI120HandsTester()
    tester.test_all_120_hands_mock_ui()


if __name__ == "__main__":
    main()
