#!/usr/bin/env python3
"""
Ultimate PPSM Validation Tester

Tests the production-ready PurePokerStateMachine against real poker hand histories
from legendary games. This is the final validation that proves PPSM is ready
for production poker applications.

Architecture:
- Direct PPSM testing (no sessions/wrappers)
- Real poker hand data from legendary_hands_normalized.json
- Deterministic deck replay
- Comprehensive validation (pot, actions, states)
"""

import json
import time
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import (
    PurePokerStateMachine, GameConfig, DeckProvider, RulesProvider, AdvancementController
)
from core.poker_types import Player, PokerState, GameState
from core.hand_model import ActionType


class HandReplayDeckProvider:
    """Deterministic deck provider for replaying specific hands."""
    
    def __init__(self, board_cards: List[str], hole_cards: Dict[str, List[str]]):
        self.board_cards = board_cards or []
        self.hole_cards = hole_cards or {}
        self._deck = None
        
    def get_deck(self) -> List[str]:
        """Create deterministic deck for hand replay."""
        if self._deck is None:
            # All possible cards
            suits = ['C', 'D', 'H', 'S']  
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            all_cards = [rank + suit for suit in suits for rank in ranks]
            
            # Cards that will be dealt (in order needed)
            needed_cards = []
            
            # First, add hole cards (2 per player)
            for player_uid in sorted(self.hole_cards.keys()):
                player_cards = self.hole_cards.get(player_uid, [])
                needed_cards.extend(player_cards[:2])  # Take up to 2 cards
            
            # Then add board cards  
            needed_cards.extend(self.board_cards[:5])  # Take up to 5 board cards
            
            # Remove known cards from all_cards
            remaining_cards = [card for card in all_cards if card not in needed_cards]
            
            # Build deck: needed cards first, then remaining shuffled
            import random
            random.shuffle(remaining_cards)
            self._deck = needed_cards + remaining_cards
            
        return self._deck.copy()
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace deck (not used in replay)."""
        pass


class HandReplayRulesProvider:
    """Rules provider optimized for hand replay."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """UTG in multi-way, dealer in heads-up."""
        if num_players == 2:
            return dealer_pos  # Dealer acts first preflop in heads-up
        else:
            return (dealer_pos + 3) % num_players  # UTG
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """First active player after dealer."""
        for i in range(1, len(players) + 1):
            idx = (dealer_pos + i) % len(players)
            if not players[idx].has_folded and players[idx].is_active:
                return idx
        return -1


class HandReplayAdvancementController:
    """Advancement controller for deterministic replay."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Auto-advance street transitions."""
        return current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]
    
    def on_round_complete(self, street: str, game_state) -> None:
        """Handle round completion."""
        pass


class UltimatePPSMValidator:
    """Ultimate validator for PPSM using real poker hand data."""
    
    def __init__(self, legendary_hands_path: str = "data/legendary_hands_normalized.json"):
        self.legendary_hands_path = legendary_hands_path
        self.results = []
        
    def load_legendary_hands(self) -> List[Dict[str, Any]]:
        """Load legendary poker hands."""
        try:
            print(f"📁 Loading hands from: {self.legendary_hands_path}")
            with open(self.legendary_hands_path, 'r') as f:
                data = json.load(f)
            hands = data.get('hands', [])
            print(f"✅ Loaded {len(hands)} legendary poker hands")
            return hands
        except Exception as e:
            print(f"❌ Error loading hands: {e}")
            return []
    
    def parse_legendary_hand(self, hand_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse legendary hand data into PPSM format."""
        try:
            metadata = hand_data.get('metadata', {})
            seats = hand_data.get('seats', [])
            streets = hand_data.get('streets', {})
            
            # Extract basic info
            hand_info = {
                'hand_id': metadata.get('hand_id', 'unknown'),
                'num_players': len(seats),
                'small_blind': float(metadata.get('small_blind', 1.0)),
                'big_blind': float(metadata.get('big_blind', 2.0)),
                'button_seat': metadata.get('button_seat_no', 1),
                'final_pot': 0.0,  # Will calculate from actions
                'players': [],
                'actions': [],
                'board_cards': [],  # Will extract from final street
                'hole_cards': metadata.get('hole_cards', {})
            }
            
            # Parse players
            for seat in seats:
                player = {
                    'name': seat.get('player_uid', f"seat_{seat.get('seat_no', 1)}"),
                    'seat_no': seat.get('seat_no', 1),
                    'starting_stack': float(seat.get('starting_stack', 1000.0)),
                    'is_button': seat.get('seat_no', 1) == hand_info['button_seat']
                }
                hand_info['players'].append(player)
            
            # Parse actions from all streets
            all_actions = []
            street_order = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
            
            for street_name in street_order:
                street_data = streets.get(street_name, {})
                if isinstance(street_data, dict) and 'actions' in street_data:
                    for action_data in street_data['actions']:
                        action = {
                            'street': street_name,
                            'order': action_data.get('order', 0),
                            'actor': action_data.get('actor_uid', ''),
                            'action': action_data.get('action', 'CHECK'),
                            'amount': float(action_data.get('amount', 0.0))
                        }
                        all_actions.append(action)
            
            # Sort actions by street order and then by order within street
            all_actions.sort(key=lambda x: (street_order.index(x['street']), x['order']))
            hand_info['actions'] = all_actions
            
            # Calculate final pot from all actions (excluding DEAL_HOLE actions)
            final_pot = 0.0
            for action in all_actions:
                if action['action'] not in ['DEAL_HOLE']:
                    final_pot += action['amount']
            hand_info['final_pot'] = final_pot
            
            # Extract board cards from the final available street
            for street_name in reversed(street_order):  # Start from RIVER, work backwards
                street_data = streets.get(street_name, {})
                if isinstance(street_data, dict) and 'board' in street_data:
                    board = street_data.get('board', [])
                    if board:  # If this street has board cards
                        hand_info['board_cards'] = board
                        break
            
            return hand_info
            
        except Exception as e:
            print(f"❌ Error parsing hand data: {e}")
            return None
    
    def create_ppsm_for_hand(self, hand_info: Dict[str, Any]) -> PurePokerStateMachine:
        """Create PPSM configured for this specific hand."""
        # Create game config
        config = GameConfig(
            num_players=hand_info['num_players'],
            small_blind=hand_info['small_blind'],
            big_blind=hand_info['big_blind'],
            starting_stack=max(p['starting_stack'] for p in hand_info['players'])  # Use max stack
        )
        
        # Create providers
        deck_provider = HandReplayDeckProvider(
            board_cards=hand_info['board_cards'],
            hole_cards=hand_info['hole_cards']
        )
        rules_provider = HandReplayRulesProvider()
        advancement_controller = HandReplayAdvancementController()
        
        # Create PPSM
        ppsm = PurePokerStateMachine(
            config=config,
            deck_provider=deck_provider, 
            rules_provider=rules_provider,
            advancement_controller=advancement_controller
        )
        
        return ppsm
    
    def setup_ppsm_players(self, ppsm: PurePokerStateMachine, hand_info: Dict[str, Any]):
        """Setup PPSM with players from hand data."""
        # Clear existing players
        ppsm.game_state.players = []
        
        # Find button position (0-indexed)
        button_pos = 0
        for i, player_data in enumerate(hand_info['players']):
            if player_data['is_button']:
                button_pos = i
                break
        
        # Set dealer position
        ppsm.dealer_position = button_pos
        
        # Create players in seat order
        for i, player_data in enumerate(hand_info['players']):
            player = Player(
                name=player_data['name'],
                stack=player_data['starting_stack'],
                position=f"seat_{player_data['seat_no']}",
                is_human=False,
                current_bet=0.0,
                has_folded=False,
                is_active=True,
                cards=hand_info['hole_cards'].get(player_data['name'], [])
            )
            ppsm.game_state.players.append(player)
        
        # Assign positions based on dealer
        ppsm._assign_positions()
    
    def convert_action_to_ppsm(self, action_str: str, amount: float) -> Tuple[ActionType, float]:
        """Convert action string to PPSM ActionType."""
        action_map = {
            'CHECK': (ActionType.CHECK, 0.0),
            'CALL': (ActionType.CALL, 0.0),
            'BET': (ActionType.BET, amount),
            'RAISE': (ActionType.RAISE, amount),
            'FOLD': (ActionType.FOLD, 0.0),
            'ALL_IN': (ActionType.BET if amount > 0 else ActionType.CALL, amount),
            'POST_BLIND': (ActionType.CALL, 0.0)  # Blinds handled automatically
        }
        
        return action_map.get(action_str, (ActionType.CHECK, 0.0))
    
    def find_player_by_name(self, ppsm: PurePokerStateMachine, actor_name: str) -> Optional[Player]:
        """Find player by name in PPSM."""
        for player in ppsm.game_state.players:
            if player.name == actor_name:
                return player
        return None
    
    def validate_hand(self, hand_index: int, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single hand against PPSM."""
        # Parse hand data
        hand_info = self.parse_legendary_hand(hand_data)
        if not hand_info:
            return {
                'hand_index': hand_index,
                'hand_id': 'unknown',
                'success': False,
                'error': 'Failed to parse hand data'
            }
        
        hand_id = hand_info['hand_id']
        print(f"\n🎲 Testing Hand {hand_index + 1}: {hand_id}")
        print(f"   Players: {hand_info['num_players']}, Actions: {len(hand_info['actions'])}")
        print(f"   Expected final pot: ${hand_info['final_pot']}")
        
        try:
            # Suppress PPSM verbose logging during validation
            import builtins
            original_print = builtins.print
            builtins.print = lambda *args, **kwargs: None
            
            try:
                # Create PPSM for this hand
                ppsm = self.create_ppsm_for_hand(hand_info)
                
                # Setup players
                self.setup_ppsm_players(ppsm, hand_info)
                
                # Start hand
                ppsm.start_hand()
                
                # Track validation metrics
                actions_executed = 0
                actions_successful = 0
                street_transitions = 0
                last_street = ppsm.game_state.street
                
                # Execute actions from the legendary hand
                for action_data in hand_info['actions']:
                    if action_data['action'] == 'POST_BLIND':
                        continue  # Blinds handled automatically by PPSM
                    
                    # Find actor
                    actor_name = action_data['actor']
                    player = self.find_player_by_name(ppsm, actor_name)
                    
                    if not player:
                        builtins.print = original_print
                        print(f"   ⚠️  Could not find player: {actor_name}")
                        builtins.print = lambda *args, **kwargs: None
                        continue
                    
                    # Check if this player should be acting
                    if ppsm.action_player_index >= 0:
                        current_actor = ppsm.game_state.players[ppsm.action_player_index]
                        if current_actor.name != actor_name:
                            builtins.print = original_print 
                            print(f"   ⚠️  Action order mismatch: expected {current_actor.name}, got {actor_name}")
                            builtins.print = lambda *args, **kwargs: None
                    
                    # Convert action
                    action_type, amount = self.convert_action_to_ppsm(
                        action_data['action'], 
                        action_data['amount']
                    )
                    
                    # Execute action
                    try:
                        if ppsm._is_valid_action(player, action_type, amount):
                            ppsm.execute_action(player, action_type, amount)
                            actions_successful += 1
                        else:
                            builtins.print = original_print
                            print(f"   ⚠️  Invalid action: {player.name} {action_type.value} {amount}")
                            builtins.print = lambda *args, **kwargs: None
                        
                        actions_executed += 1
                        
                        # Track street transitions
                        if ppsm.game_state.street != last_street:
                            street_transitions += 1
                            last_street = ppsm.game_state.street
                            
                    except Exception as e:
                        builtins.print = original_print
                        print(f"   ❌ Error executing action: {e}")
                        builtins.print = lambda *args, **kwargs: None
                        break
                    
                    # Safety check
                    if actions_executed > 100:
                        builtins.print = original_print
                        print(f"   ⚠️  Too many actions, stopping at {actions_executed}")
                        builtins.print = lambda *args, **kwargs: None
                        break
                
            finally:
                builtins.print = original_print
            
            # Get final state
            final_pot = ppsm.game_state.pot
            
            # Add current bets to pot (if hand ended mid-round)
            for player in ppsm.game_state.players:
                final_pot += player.current_bet
            
            expected_pot = hand_info['final_pot']
            pot_match = abs(final_pot - expected_pot) < 0.01
            
            # Calculate success metrics
            action_success_rate = (actions_successful / actions_executed * 100) if actions_executed > 0 else 0
            overall_success = pot_match and action_success_rate > 80
            
            result = {
                'hand_index': hand_index,
                'hand_id': hand_id,
                'success': overall_success,
                'pot_match': pot_match,
                'final_pot': final_pot,
                'expected_pot': expected_pot,
                'pot_difference': abs(final_pot - expected_pot),
                'actions_executed': actions_executed,
                'actions_successful': actions_successful,
                'action_success_rate': action_success_rate,
                'street_transitions': street_transitions,
                'final_state': ppsm.current_state.value,
                'players_remaining': len([p for p in ppsm.game_state.players if not p.has_folded])
            }
            
            # Print result
            if overall_success:
                print(f"   ✅ PASSED: Pot ${final_pot:.2f}, {actions_successful}/{actions_executed} actions successful")
            else:
                print(f"   ❌ FAILED: Pot ${final_pot:.2f} (expected ${expected_pot:.2f}), {actions_successful}/{actions_executed} actions")
            
            return result
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return {
                'hand_index': hand_index,
                'hand_id': hand_id,
                'success': False,
                'error': str(e),
                'final_pot': 0,
                'expected_pot': hand_info.get('final_pot', 0)
            }
    
    def run_ultimate_validation(self, max_hands: int = 10) -> Dict[str, Any]:
        """Run the ultimate PPSM validation test."""
        print("🏆 ULTIMATE PPSM VALIDATION TEST")
        print("=" * 70)
        print("🎯 Testing production-ready PurePokerStateMachine against real poker data")
        print("🃏 This is the final exam - if PPSM passes this, it's production ready!")
        print("=" * 70)
        
        # Load legendary hands
        hands = self.load_legendary_hands()
        if not hands:
            return {'success': False, 'error': 'No hands to test'}
        
        print(f"📊 Testing up to {max_hands} hands from {len(hands)} available")
        
        # Run validation on hands
        results = []
        successful_hands = 0
        total_actions = 0
        total_successful_actions = 0
        
        start_time = time.time()
        
        for i, hand_data in enumerate(hands[:max_hands]):
            result = self.validate_hand(i, hand_data)
            results.append(result)
            
            if result.get('success', False):
                successful_hands += 1
            
            total_actions += result.get('actions_executed', 0)
            total_successful_actions += result.get('actions_successful', 0)
        
        elapsed_time = time.time() - start_time
        
        # Calculate summary statistics
        total_tested = len(results)
        success_rate = (successful_hands / total_tested * 100) if total_tested > 0 else 0
        action_success_rate = (total_successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        summary = {
            'total_hands_tested': total_tested,
            'successful_hands': successful_hands,
            'failed_hands': total_tested - successful_hands,
            'hand_success_rate': success_rate,
            'total_actions': total_actions,
            'successful_actions': total_successful_actions,
            'action_success_rate': action_success_rate,
            'elapsed_time': elapsed_time,
            'hands_per_second': total_tested / elapsed_time if elapsed_time > 0 else 0,
            'results': results
        }
        
        # Print final summary
        print("\n" + "=" * 70)
        print("🏆 ULTIMATE VALIDATION RESULTS")
        print("=" * 70)
        print(f"📊 Hands tested: {total_tested}")
        print(f"✅ Successful: {successful_hands} ({success_rate:.1f}%)")
        print(f"❌ Failed: {total_tested - successful_hands}")
        print(f"⚡ Actions: {total_successful_actions}/{total_actions} successful ({action_success_rate:.1f}%)")
        print(f"⏱️  Time: {elapsed_time:.1f}s ({summary['hands_per_second']:.1f} hands/sec)")
        
        # Final verdict
        print("\n" + "🎯 FINAL VERDICT:")
        if success_rate >= 90:
            print("🏆 PRODUCTION READY! PPSM passes real poker data validation!")
            print("🚀 Ready for deployment in poker applications!")
        elif success_rate >= 70:
            print("🟡 MOSTLY READY - Minor issues need investigation")
        elif success_rate >= 50:
            print("🟠 NEEDS WORK - Significant issues found")
        else:
            print("🔴 NOT READY - Major problems detected")
        
        return summary


def main():
    """Run the ultimate PPSM validation."""
    validator = UltimatePPSMValidator()
    
    # Test with a reasonable number of hands
    results = validator.run_ultimate_validation(max_hands=20)
    
    # Save results
    results_file = "ultimate_ppsm_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results['hand_success_rate'] >= 90  # Return True if validation passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
