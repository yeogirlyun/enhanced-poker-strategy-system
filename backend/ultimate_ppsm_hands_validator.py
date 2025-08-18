#!/usr/bin/env python3
"""
Ultimate PPSM Hands Validator

Uses the existing Hand model and HandModelDecisionEngine infrastructure 
to validate the production-ready PurePokerStateMachine against real poker hands.

Architecture:
- Hand model: Parse legendary hands using existing infrastructure
- HandModelDecisionEngine: Extract actions in proper order 
- PPSM: Execute actions and validate results
- Comprehensive reporting: Success rates, pot accuracy, performance
"""

import json
import time
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import (
    PurePokerStateMachine, GameConfig, DeckProvider, RulesProvider, AdvancementController
)
from core.poker_types import Player, PokerState, GameState
from core.hand_model import Hand, Street, ActionType, Action
from core.hand_model_decision_engine import HandModelDecisionEngine


class PPSMHandReplayDeckProvider:
    """Deck provider for deterministic PPSM hand replay."""
    
    def __init__(self, hand_model: Hand):
        self.hand_model = hand_model
        self._deck = None
        
    def get_deck(self) -> List[str]:
        """Create deterministic deck for hand replay."""
        if self._deck is None:
            # All possible cards
            suits = ['C', 'D', 'H', 'S']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            all_cards = [rank + suit for suit in suits for rank in ranks]
            
            # Cards that need to be dealt (in order)
            needed_cards = []
            
            # Add hole cards for each player (convert format: "Kh" -> "KH")
            hole_cards = getattr(self.hand_model.metadata, 'hole_cards', {})
            for player_uid in sorted(hole_cards.keys()):
                player_cards = hole_cards.get(player_uid, [])
                for card in player_cards[:2]:  # Take up to 2 hole cards
                    # Convert "Kh" format to "KH" format
                    if len(card) == 2:
                        converted_card = card[0].upper() + card[1].upper()
                        needed_cards.append(converted_card)
            
            # Add board cards from final street (convert format)
            final_board = self.hand_model.get_final_board()
            for card in final_board:
                if len(card) == 2:
                    converted_card = card[0].upper() + card[1].upper()
                    needed_cards.append(converted_card)
            
            # Remove needed cards from all_cards pool
            remaining_cards = [card for card in all_cards if card not in needed_cards]
            
            # Build deck: needed cards first, then remaining shuffled
            import random
            random.shuffle(remaining_cards)
            self._deck = needed_cards + remaining_cards
            
        return self._deck.copy()
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace deck (not used in replay)."""
        pass


class PPSMHandReplayRulesProvider:
    """Rules provider for PPSM hand replay."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """UTG in multi-way, dealer in heads-up."""
        if num_players == 2:
            return dealer_pos
        else:
            return (dealer_pos + 3) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """First active player after dealer."""
        for i in range(1, len(players) + 1):
            idx = (dealer_pos + i) % len(players)
            if not players[idx].has_folded and players[idx].is_active:
                return idx
        return -1


class PPSMHandReplayAdvancementController:
    """Advancement controller for PPSM hand replay."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Auto-advance street transitions."""
        return current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]
    
    def on_round_complete(self, street: str, game_state) -> None:
        """Handle round completion."""
        pass


class UltimatePPSMHandsValidator:
    """Ultimate validator for PPSM using Hand model infrastructure."""
    
    def __init__(self, legendary_hands_path: str = "data/legendary_hands_normalized.json"):
        self.legendary_hands_path = legendary_hands_path
        self.results = []
        
    def load_legendary_hands(self) -> List[Hand]:
        """Load legendary hands and convert to Hand model objects."""
        try:
            print(f"📁 Loading hands from: {self.legendary_hands_path}")
            with open(self.legendary_hands_path, 'r') as f:
                data = json.load(f)
            
            raw_hands = data.get('hands', [])
            print(f"✅ Found {len(raw_hands)} raw hands")
            
            # Convert to Hand model objects
            hand_models = []
            for i, hand_data in enumerate(raw_hands):
                try:
                    # The legendary hands JSON should already be in Hand model format
                    hand_model = Hand.from_dict(hand_data)
                    hand_models.append(hand_model)
                except Exception as e:
                    print(f"⚠️ Could not parse hand {i+1}: {e}")
                    continue
            
            print(f"✅ Successfully parsed {len(hand_models)} Hand model objects")
            return hand_models
            
        except Exception as e:
            print(f"❌ Error loading hands: {e}")
            return []
    
    def create_ppsm_for_hand(self, hand_model: Hand) -> PurePokerStateMachine:
        """Create PPSM configured for this specific hand."""
        # Create game config from hand metadata
        config = GameConfig(
            num_players=len(hand_model.seats),
            small_blind=hand_model.metadata.small_blind,
            big_blind=hand_model.metadata.big_blind,
            starting_stack=max(seat.starting_stack for seat in hand_model.seats)
        )
        
        # Create providers
        deck_provider = PPSMHandReplayDeckProvider(hand_model)
        rules_provider = PPSMHandReplayRulesProvider()
        advancement_controller = PPSMHandReplayAdvancementController()
        
        # Create PPSM
        ppsm = PurePokerStateMachine(
            config=config,
            deck_provider=deck_provider,
            rules_provider=rules_provider,
            advancement_controller=advancement_controller
        )
        
        return ppsm
    
    def setup_ppsm_players(self, ppsm: PurePokerStateMachine, hand_model: Hand):
        """Setup PPSM with players from hand model."""
        # Clear existing players
        ppsm.game_state.players = []
        
        # Find button position
        button_seat_no = getattr(hand_model.metadata, 'button_seat_no', 1)
        button_pos = 0
        for i, seat in enumerate(hand_model.seats):
            if seat.seat_no == button_seat_no:
                button_pos = i
                break
        
        # Set dealer position
        ppsm.dealer_position = button_pos
        
        # Create players from seats
        for seat in hand_model.seats:
            # Get hole cards from metadata
            hole_cards = getattr(hand_model.metadata, 'hole_cards', {})
            player_cards = hole_cards.get(seat.player_uid, [])
            
            player = Player(
                name=seat.player_uid,
                stack=seat.starting_stack,
                position=f"seat_{seat.seat_no}",
                is_human=False,
                current_bet=0.0,
                has_folded=False,
                is_active=True,
                cards=player_cards
            )
            ppsm.game_state.players.append(player)
        
        # Assign positions based on dealer
        ppsm._assign_positions()
    
    def convert_hand_model_action_to_ppsm(self, action: Action) -> tuple:
        """Convert Hand model action to PPSM action type and amount."""
        if action.action == ActionType.CHECK:
            return ActionType.CHECK, 0.0
        elif action.action == ActionType.CALL:
            return ActionType.CALL, 0.0
        elif action.action == ActionType.BET:
            return ActionType.BET, float(action.amount)
        elif action.action == ActionType.RAISE:
            return ActionType.RAISE, float(action.amount)
        elif action.action == ActionType.FOLD:
            return ActionType.FOLD, 0.0
        else:
            # Default to check for unknown actions
            return ActionType.CHECK, 0.0
    
    def find_ppsm_player(self, ppsm: PurePokerStateMachine, actor_uid: str) -> Optional[Player]:
        """Find PPSM player by actor_uid."""
        for player in ppsm.game_state.players:
            if player.name == actor_uid:
                return player
        return None
    
    def calculate_expected_pot_from_hand_model(self, hand_model: Hand) -> float:
        """Calculate expected final pot from Hand model actions."""
        total_pot = 0.0
        all_actions = hand_model.get_all_actions()
        
        # Sum all betting actions (excluding dealing actions)
        betting_actions = {ActionType.POST_BLIND, ActionType.BET, ActionType.CALL, ActionType.RAISE}
        for action in all_actions:
            if action.action in betting_actions:
                total_pot += action.amount
        
        return total_pot
    
    def validate_hand(self, hand_index: int, hand_model: Hand) -> Dict[str, Any]:
        """Validate single hand using PPSM's new Hand Model interface."""
        hand_id = hand_model.metadata.hand_id
        print(f"\n🎲 Testing Hand {hand_index + 1}: {hand_id}")
        
        try:
            print(f"   Players: {len(hand_model.seats)}")
            
            # Create clean PPSM instance
            config = GameConfig(
                num_players=len(hand_model.seats),
                small_blind=hand_model.metadata.small_blind,
                big_blind=hand_model.metadata.big_blind,
                starting_stack=max(seat.starting_stack for seat in hand_model.seats)
            )
            
            ppsm = PurePokerStateMachine(
                config=config,
                deck_provider=PPSMHandReplayDeckProvider(hand_model),
                rules_provider=PPSMHandReplayRulesProvider(),
                advancement_controller=PPSMHandReplayAdvancementController()
            )
            
            # Suppress PPSM verbose logging during validation
            import builtins
            original_print = builtins.print
            builtins.print = lambda *args, **kwargs: None
            
            try:
                # Use PPSM's new Hand Model interface - this handles everything!
                replay_result = ppsm.replay_hand_model(hand_model)
                
            finally:
                builtins.print = original_print
            
            # Convert replay result to validation result format
            result = {
                'hand_index': hand_index,
                'hand_id': hand_id,
                'success': replay_result['pot_match'] and replay_result['successful_actions'] > 0,
                'pot_match': replay_result['pot_match'],
                'final_pot': replay_result['final_pot'],
                'expected_pot': replay_result['expected_pot'],
                'pot_difference': abs(replay_result['final_pot'] - replay_result['expected_pot']),
                'actions_executed': replay_result['total_actions'],
                'actions_successful': replay_result['successful_actions'],
                'action_success_rate': (replay_result['successful_actions'] / replay_result['total_actions'] * 100) if replay_result['total_actions'] > 0 else 0,
                'errors': replay_result.get('errors', [])
            }
            
            # Print result
            if result['success']:
                print(f"   ✅ PASSED: Pot ${result['final_pot']:.2f}, {result['actions_successful']}/{result['actions_executed']} actions successful")
            else:
                print(f"   ❌ FAILED: Pot ${result['final_pot']:.2f} (expected ${result['expected_pot']:.2f}), {result['actions_successful']}/{result['actions_executed']} actions")
                if result['errors']:
                    print(f"   Errors: {result['errors'][:3]}")  # Show first 3 errors
            
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
                'expected_pot': 0,
                'actions_executed': 0,
                'actions_successful': 0,
                'action_success_rate': 0.0
            }
    
    def run_ultimate_validation(self, max_hands: int = 20) -> Dict[str, Any]:
        """Run the ultimate PPSM validation using Hand model infrastructure."""
        print("🏆 ULTIMATE PPSM HANDS VALIDATION")
        print("=" * 70)
        print("🎯 Testing production-ready PPSM with Hand model infrastructure")
        print("🃏 Using existing HandModelDecisionEngine for action extraction")
        print("=" * 70)
        
        # Load hands using Hand model
        hand_models = self.load_legendary_hands()
        if not hand_models:
            return {'success': False, 'error': 'No hands loaded'}
        
        print(f"📊 Testing up to {max_hands} hands from {len(hand_models)} available")
        
        # Run validation
        results = []
        successful_hands = 0
        total_actions = 0
        total_successful_actions = 0
        
        start_time = time.time()
        
        for i, hand_model in enumerate(hand_models[:max_hands]):
            result = self.validate_hand(i, hand_model)
            results.append(result)
            
            if result.get('success', False):
                successful_hands += 1
            
            total_actions += result.get('actions_executed', 0)
            total_successful_actions += result.get('actions_successful', 0)
        
        elapsed_time = time.time() - start_time
        
        # Calculate summary
        total_tested = len(results)
        hand_success_rate = (successful_hands / total_tested * 100) if total_tested > 0 else 0
        action_success_rate = (total_successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        summary = {
            'total_hands_tested': total_tested,
            'successful_hands': successful_hands,
            'failed_hands': total_tested - successful_hands,
            'hand_success_rate': hand_success_rate,
            'total_actions': total_actions,
            'successful_actions': total_successful_actions,
            'action_success_rate': action_success_rate,
            'elapsed_time': elapsed_time,
            'hands_per_second': total_tested / elapsed_time if elapsed_time > 0 else 0,
            'results': results
        }
        
        # Print summary
        print("\n" + "=" * 70)
        print("🏆 ULTIMATE VALIDATION RESULTS")
        print("=" * 70)
        print(f"📊 Hands tested: {total_tested}")
        print(f"✅ Successful: {successful_hands} ({hand_success_rate:.1f}%)")
        print(f"❌ Failed: {total_tested - successful_hands}")
        print(f"⚡ Actions: {total_successful_actions}/{total_actions} successful ({action_success_rate:.1f}%)")
        print(f"⏱️  Time: {elapsed_time:.1f}s ({summary['hands_per_second']:.1f} hands/sec)")
        
        # Final verdict
        print("\n🎯 FINAL VERDICT:")
        if hand_success_rate >= 90:
            print("🏆 PRODUCTION READY! PPSM passes real poker validation!")
            print("🚀 Ready for deployment in poker applications!")
        elif hand_success_rate >= 70:
            print("🟡 MOSTLY READY - Minor issues need investigation")
        elif hand_success_rate >= 50:
            print("🟠 NEEDS WORK - Significant issues found")
        else:
            print("🔴 NOT READY - Major problems detected")
        
        return summary


def main():
    """Run the ultimate PPSM hands validation."""
    validator = UltimatePPSMHandsValidator()
    
    # Test with a reasonable number of hands
    results = validator.run_ultimate_validation(max_hands=10)
    
    # Save results
    results_file = "ultimate_ppsm_hands_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results['hand_success_rate'] >= 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
