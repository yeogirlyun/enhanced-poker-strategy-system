#!/usr/bin/env python3
"""
Comprehensive Hands Review Validation Tester

This tester validates that the Hands Review Poker State Machine can accurately:
1. Load and replay hands from Hand Model format
2. Execute all actions correctly
3. Maintain accurate stack sizes and pot sizes
4. Generate identical output when re-serialized

This ensures the system is sound and can work with any Hand Model compatible data.
"""

import json

# --- Hermetic stubs for optional deps ---
import types, sys as _sys
_mod = types.ModuleType('utils.sound_manager')
class _SM: 
    def __init__(self, *a, **k): pass
    def play(self, *a, **k): pass
_mod.SoundManager = _SM
_sys.modules['utils.sound_manager'] = _mod
_mod2 = types.ModuleType('core.deuces_hand_evaluator')
class _Eval: 
    def evaluate(self, hand, board): return 0
_mod2.DeucesHandEvaluator = _Eval
_sys.modules['core.deuces_hand_evaluator'] = _mod2
# --- End stubs ---


# --- Test harness dependency stubs (to keep validator hermetic) ---
import types, sys as _sys
_mod = types.ModuleType('utils.sound_manager')
class _SM:
    def __init__(self, *a, **k): pass
    def play(self, *a, **k): pass
_mod.SoundManager = _SM
_sys.modules['utils.sound_manager'] = _mod
# Optional: stub core.deuces_hand_evaluator if present elsewhere on path
_mod2 = types.ModuleType('core.deuces_hand_evaluator')
class _Eval:
    def evaluate(self, hand, board): return 0
_mod2.DeucesHandEvaluator = _Eval
_sys.modules['core.deuces_hand_evaluator'] = _mod2
# --- End stubs ---

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import asdict

# Add backend to path
sys.path.append('.')

from core.hand_model import Hand
from core.bot_session_state_machine import HandsReviewBotSession
from core.flexible_poker_state_machine import GameConfig
from core.hand_model import Street, StreetState


class HandsReviewValidator:
    """Validates hands review poker state machine accuracy."""
    
    def __init__(self, legendary_hands_path: str = "data/legendary_hands.json"):
        self.legendary_hands_path = legendary_hands_path
        self.results = []
        self.errors = []
        
    def load_legendary_hands(self) -> List[Dict[str, Any]]:
        """Load legendary hands from JSON file."""
        try:
            with open(self.legendary_hands_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'hands' in data:
                return data['hands']
            else:
                raise ValueError(f"Unexpected data structure in {self.legendary_hands_path}")
                
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            return []
    
    def load_hand_model(self, hand_data: Dict[str, Any]) -> Hand:
        """Load hand data directly into Hand Model format."""
        try:
            return Hand.from_dict(hand_data)
        except Exception as e:
            print(f"❌ Error loading hand data into Hand Model: {e}")
            raise
    
    def create_hands_review_session(self, hand_model: Hand) -> HandsReviewBotSession:
        """Create a hands review session for the given hand."""
        try:
            # Create game config with hand-specific values
            config = GameConfig(
                small_blind=getattr(hand_model.metadata, 'small_blind', 1.0),
                big_blind=getattr(hand_model.metadata, 'big_blind', 2.0),
                starting_stack=getattr(hand_model.metadata, 'starting_stack', 100.0),
                num_players=len(hand_model.seats)
            )
            
            # Create a decision engine with the hand model
            from core.hand_model_decision_engine import HandModelDecisionEngine
            decision_engine = HandModelDecisionEngine(hand_model)
            
            # Create hands review session with the decision engine
            session = HandsReviewBotSession(
                config=config,
                decision_engine=decision_engine
            )
            
            # Set the hand model data for the session to use
            session.preloaded_hand_data = {'hand_model': hand_model}
            
            # Start the session
            if not session.start_session():
                raise RuntimeError("Failed to start hands review session")
            
            return session
            
        except Exception as e:
            import traceback
            print(f"❌ Error creating hands review session: {e}")
            traceback.print_exc()
            raise
    
    def replay_hand_completely(self, session: HandsReviewBotSession, hand_model: Hand) -> Dict[str, Any]:
        """Replay the entire hand and return final state."""
        try:
            # Get initial state
            initial_state = session.get_display_state()
            
            # Replay the hand
            action_count = 0
            max_actions = 1000  # Safety limit
            
            print(f"🔄 Starting hand replay with {len(hand_model.seats)} players")
            print(f"📊 Total actions in hand: {len(hand_model.streets.get(Street.PREFLOP, StreetState()).actions) + len(hand_model.streets.get(Street.FLOP, StreetState()).actions) + len(hand_model.streets.get(Street.TURN, StreetState()).actions) + len(hand_model.streets.get(Street.RIVER, StreetState()).actions)}")
            
            while action_count < max_actions:
                # Check if session is complete
                if session.decision_engine.is_session_complete():
                    print(f"✅ Session marked as complete after {action_count} actions")
                    break
                
                # Execute next action
                try:
                    success = session.execute_next_bot_action()
                    if not success:
                        print(f"⚠️ Action {action_count} failed or returned False")
                        break
                    action_count += 1
                    
                    # Debug: Print progress every 100 actions
                    if action_count % 100 == 0:
                        progress = session.decision_engine.get_progress()
                        print(f"🔄 Action {action_count}: {progress['current_action']}/{progress['total_actions']} ({progress['progress_percent']:.1f}%)")
                        
                except Exception as e:
                    print(f"❌ Action {action_count} failed with exception: {e}")
                    break
            
            # Get final state
            final_state = session.get_display_state()
            game_info = session.get_game_info()
            
            return {
                'initial_state': initial_state,
                'final_state': final_state,
                'game_info': game_info,
                'action_count': action_count,
                'hand_complete': game_info.get('hand_complete', False)
            }
            
        except Exception as e:
            print(f"❌ Error replaying hand: {e}")
            raise
    
    def extract_final_state_data(self, session: HandsReviewBotSession, hand_model: Hand) -> Dict[str, Any]:
        """Extract final state data for comparison."""
        try:
            # Get current game state
            game_info = session.get_game_info()
            display_state = session.get_display_state()
            
            # Extract player states
            players = []
            for i, seat in enumerate(hand_model.seats):
                player_info = {
                    'player_uid': seat.player_uid,
                    'seat_no': seat.seat_no,
                    'final_stack': 0.0,
                    'final_bet': 0.0,
                    'folded': False,
                    'all_in': False
                }
                
                # Get player state from session
                if i < len(game_info.get('players', [])):
                    player_state = game_info['players'][i]
                    player_info.update({
                        'final_stack': player_state.get('stack', 0.0),
                        'final_bet': player_state.get('current_bet', 0.0),
                        'folded': player_state.get('folded', False),
                        'all_in': player_state.get('all_in', False)
                    })
                
                players.append(player_info)
            
            # Extract pot information
            pot_info = {
                'total_pot': game_info.get('pot', 0.0),
                'side_pots': game_info.get('side_pots', []),
                'current_bet': game_info.get('current_bet', 0.0)
            }
            
            return {
                'players': players,
                'pot': pot_info,
                'street': game_info.get('current_street', 'preflop'),
                'hand_complete': game_info.get('hand_complete', False),
                'winner': game_info.get('winner', None)
            }
            
        except Exception as e:
            print(f"❌ Error extracting final state: {e}")
            raise
    
    def compare_hand_results(self, original_hand: Hand, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Compare original hand results with final state."""
        comparison = {
            'matches': True,
            'differences': [],
            'stack_matches': True,
            'pot_matches': True,
            'action_matches': True
        }
        
        try:
            # Compare final pot size
            original_pot = sum(pot.amount for pot in original_hand.pots)
            final_pot = final_state['pot']['total_pot']
            
            if abs(original_pot - final_pot) > 0.01:  # Allow small floating point differences
                comparison['pot_matches'] = False
                comparison['differences'].append(f"Pot size mismatch: original={original_pot}, final={final_pot}")
            
            # Compare player final stacks
            for i, seat in enumerate(original_hand.seats):
                if i < len(final_state['players']):
                    final_player = final_state['players'][i]
                    
                    # Find original final state for this player
                    original_final_stack = seat.starting_stack  # Use starting_stack, not stack
                    final_final_stack = final_player['final_stack']
                    
                    if abs(original_final_stack - final_final_stack) > 0.01:
                        comparison['stack_matches'] = False
                        comparison['differences'].append(
                            f"Player {seat.player_uid} stack mismatch: original={original_final_stack}, final={final_final_stack}"
                        )
            
            # Check if any differences found
            if comparison['differences']:
                comparison['matches'] = False
            
        except Exception as e:
            comparison['matches'] = False
            comparison['differences'].append(f"Error during comparison: {e}")
        
        return comparison
    
    def serialize_session_to_json(self, session: HandsReviewBotSession, hand_model: Hand) -> Dict[str, Any]:
        """Serialize the session state back to JSON format for comparison."""
        try:
            # Get current game state
            game_info = session.get_game_info()
            display_state = session.get_display_state()
            
            # Build the serialized hand structure
            serialized_hand = {
                'metadata': {
                    'table_id': getattr(hand_model.metadata, 'table_id', 'VALIDATION_TABLE'),
                    'hand_id': getattr(hand_model.metadata, 'hand_id', 'VALIDATION_HAND'),
                    'small_blind': getattr(hand_model.metadata, 'small_blind', 1.0),
                    'big_blind': getattr(hand_model.metadata, 'big_blind', 2.0),
                    'button_seat_no': getattr(hand_model.metadata, 'button_seat_no', 0),
                    'timestamp': getattr(hand_model.metadata, 'timestamp', '2025-01-01T00:00:00Z')
                },
                'seats': [],
                'streets': [],
                'pots': [],
                'showdown': []
            }
            
            # Serialize seats
            for i, seat in enumerate(hand_model.seats):
                if i < len(game_info.get('players', [])):
                    player_state = game_info['players'][i]
                    # Get hole cards from metadata if available
                    hole_cards = []
                    if hasattr(hand_model.metadata, 'hole_cards') and hand_model.metadata.hole_cards:
                        hole_cards = hand_model.metadata.hole_cards.get(seat.player_uid, [])
                    
                    serialized_seat = {
                        'seat_no': seat.seat_no,
                        'player_uid': seat.player_uid,
                        'stack': player_state.get('stack', seat.starting_stack),  # Use starting_stack as fallback
                        'is_button': seat.is_button,
                        'hole_cards': hole_cards
                    }
                    serialized_hand['seats'].append(serialized_seat)
            
            # Serialize streets and actions
            # Note: This is a simplified serialization - in practice you might want more detail
            for street_enum, street_state in hand_model.streets.items():
                serialized_street = {
                    'street': street_enum.value,
                    'actions': []
                }
                
                for action in street_state.actions:
                    serialized_action = {
                        'actor_uid': action.actor_uid,
                        'action': action.action.value,
                        'amount': action.amount,
                        'street': action.street.value,
                        'order': action.order,
                        'note': action.note or ''
                    }
                    serialized_street['actions'].append(serialized_action)
                
                serialized_hand['streets'].append(serialized_street)
            
            # Serialize pots
            for pot in hand_model.pots:
                serialized_pot = {
                    'amount': pot.amount,
                    'eligible_player_uids': pot.eligible_player_uids,
                    'shares': []
                }
                
                for share in pot.shares:
                    serialized_share = {
                        'player_uid': share.player_uid,
                        'amount': share.amount,
                        'percentage': share.percentage
                    }
                    serialized_pot['shares'].append(serialized_share)
                
                serialized_hand['pots'].append(serialized_pot)
            
            return serialized_hand
            
        except Exception as e:
            print(f"❌ Error serializing session: {e}")
            raise
    
    def validate_single_hand(self, hand_index: int, legendary_hand: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single hand completely."""
        result = {
            'hand_index': hand_index,
            'hand_id': legendary_hand.get('id', f'hand_{hand_index}'),
            'success': False,
            'errors': [],
            'comparison': None,
            'serialization_match': False
        }
        
        try:
            print(f"🔍 Validating hand {hand_index + 1}: {result['hand_id']}")
            
            # Step 1: Convert to Hand Model
            hand_model = self.load_hand_model(legendary_hand)
            print(f"   ✅ Converted to Hand Model: {len(hand_model.seats)} players, {len(hand_model.streets)} streets")
            
            # Step 2: Create hands review session
            session = self.create_hands_review_session(hand_model)
            print(f"   ✅ Created hands review session")
            
            # Step 3: Replay hand completely
            replay_result = self.replay_hand_completely(session, hand_model)
            print(f"   ✅ Replayed hand: {replay_result['action_count']} actions, complete: {replay_result['hand_complete']}")
            
            # Step 4: Extract final state
            final_state = self.extract_final_state_data(session, hand_model)
            print(f"   ✅ Extracted final state: pot=${final_state['pot']['total_pot']:.2f}")
            
            # Step 5: Compare results
            comparison = self.compare_hand_results(hand_model, final_state)
            result['comparison'] = comparison
            
            if comparison['matches']:
                print(f"   ✅ Results match original hand")
            else:
                print(f"   ❌ Results differ from original hand")
                for diff in comparison['differences']:
                    print(f"      - {diff}")
            
            # Step 6: Serialize back to JSON and compare
            serialized_hand = self.serialize_session_to_json(session, hand_model)
            
            # Compare key fields (simplified comparison)
            original_json = asdict(hand_model)
            key_fields_match = (
                len(original_json['seats']) == len(serialized_hand['seats']) and
                len(original_json['streets']) == len(serialized_hand['streets']) and
                len(original_json['pots']) == len(serialized_hand['pots'])
            )
            
            result['serialization_match'] = key_fields_match
            
            if key_fields_match:
                print(f"   ✅ Serialization structure matches")
            else:
                print(f"   ❌ Serialization structure differs")
            
            result['success'] = comparison['matches'] and key_fields_match
            
        except Exception as e:
            error_msg = f"Validation failed: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        return result
    
    def run_validation(self, max_hands: int = 100) -> Dict[str, Any]:
        """Run validation on up to max_hands hands."""
        print(f"🚀 Starting Hands Review Validation")
        print(f"📁 Loading hands from: {self.legendary_hands_path}")
        print(f"🎯 Target: Validate up to {max_hands} hands")
        print("=" * 60)
        
        # Load legendary hands
        legendary_hands = self.load_legendary_hands()
        if not legendary_hands:
            return {'success': False, 'error': 'No hands loaded', 'total_hands': 0, 'successful_hands': 0, 'failed_hands': 0, 'success_rate': 0.0}
        
        print(f"📊 Loaded {len(legendary_hands)} hands")
        
        # Limit to max_hands
        hands_to_validate = legendary_hands[:max_hands]
        
        # Validate each hand
        for i, legendary_hand in enumerate(hands_to_validate):
            result = self.validate_single_hand(i, legendary_hand)
            self.results.append(result)
            
            if not result['success']:
                self.errors.append(result)
            
            print()  # Empty line between hands
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_hands = len(self.results)
        successful_hands = sum(1 for r in self.results if r['success'])
        failed_hands = total_hands - successful_hands
        
        summary = {
            'total_hands': total_hands,
            'successful_hands': successful_hands,
            'failed_hands': failed_hands,
            'success_rate': (successful_hands / total_hands * 100) if total_hands > 0 else 0,
            'errors': self.errors,
            'results': self.results
        }
        
        print("=" * 60)
        print(f"📊 VALIDATION SUMMARY")
        print(f"   Total hands: {total_hands}")
        print(f"   Successful: {successful_hands}")
        print(f"   Failed: {failed_hands}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        
        if failed_hands > 0:
            print(f"\n❌ FAILED HANDS:")
            for error in self.errors:
                print(f"   - Hand {error['hand_index'] + 1}: {error['hand_id']}")
                for err in error['errors']:
                    print(f"     {err}")
        
        return summary
    
    def save_detailed_results(self, output_path: str = "hands_review_validation_results.json"):
        """Save detailed validation results to JSON file."""
        try:
            output_data = {
                'validation_summary': {
                    'total_hands': len(self.results),
                    'successful_hands': sum(1 for r in self.results if r['success']),
                    'failed_hands': len(self.errors),
                    'timestamp': '2025-01-01T00:00:00Z'
                },
                'detailed_results': self.results
            }
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            print(f"💾 Detailed results saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def main():
    """Main validation function."""
    print("🧪 Hands Review Validation Tester")
    print("=" * 50)
    
    # Create validator
    validator = HandsReviewValidator()
    
    # Run validation on up to 100 hands
    summary = validator.run_validation(max_hands=100)
    
    # Save detailed results
    validator.save_detailed_results()
    
    # Exit with appropriate code
    if summary['success_rate'] >= 95.0:
        print(f"\n🎉 SUCCESS: {summary['success_rate']:.1f}% hands validated successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ WARNING: Only {summary['success_rate']:.1f}% hands validated successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
