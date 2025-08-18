"""
Hands Review Validation Tester - Clean Architecture Version

Tests the new clean architecture with HandsReviewSession.
"""

import json
import time
from typing import Dict, Any, List
from pathlib import Path

import sys
sys.path.append('.')

from core.pure_poker_state_machine import GameConfig
from core.sessions import HandsReviewSession
from core.hand_model import Hand, Street, StreetState
from core.hand_model_decision_engine import HandModelDecisionEngine


class HandsReviewValidatorV2:
    """Validator using the new clean architecture."""
    
    def __init__(self, legendary_hands_path: str = "data/legendary_hands_normalized.json"):
        self.legendary_hands_path = legendary_hands_path
        
    def load_legendary_hands(self) -> List[Dict[str, Any]]:
        """Load legendary hands data."""
        try:
            with open(self.legendary_hands_path, 'r') as f:
                data = json.load(f)
            return data.get('hands', [])
        except Exception as e:
            print(f"❌ Error loading hands: {e}")
            return []
    
    def load_hand_model(self, hand_data: Dict[str, Any]) -> Hand:
        """Convert legendary hand data to Hand model."""
        try:
            # Extract metadata
            metadata = hand_data.get('metadata', {})
            
            # Extract seats
            seats_data = hand_data.get('seats', [])
            
            # Extract streets and actions
            streets_data = hand_data.get('streets', {})
            
            # Create Hand model with required parameters
            from core.hand_model import HandMetadata, Seat
            
            # Create metadata
            hand_metadata = HandMetadata(
                table_id=metadata.get('table_id', 'table1'),
                hand_id=metadata.get('hand_id', 'unknown'),
                big_blind=int(metadata.get('big_blind', 2.0)),
                small_blind=int(metadata.get('small_blind', 1.0))
            )
            
            # Create seats
            seats = []
            button_seat_no = metadata.get('button_seat_no', 1)
            for seat_data in seats_data:
                seat = Seat(
                    seat_no=seat_data.get('seat_no', 1),
                    player_uid=seat_data.get('player_uid', ''),
                    starting_stack=seat_data.get('starting_stack', 1000.0),
                    is_button=(seat_data.get('seat_no', 1) == button_seat_no)
                )
                seats.append(seat)
            
            # Create Hand with required parameters
            hand = Hand(metadata=hand_metadata, seats=seats)
            
            # Add actions from streets
            from core.hand_model import Action, ActionType
            for street_name, street_data in streets_data.items():
                if isinstance(street_data, dict) and 'actions' in street_data:
                    street_enum = getattr(Street, street_name.upper(), Street.PREFLOP)
                    for action_data in street_data['actions']:
                        action = Action(
                            order=action_data.get('order', 0),
                            street=street_enum,
                            actor_uid=action_data.get('actor_uid', ''),
                            action=ActionType(action_data.get('action', 'CHECK')),
                            amount=int(action_data.get('amount', 0.0))
                        )
                        hand.streets[street_enum].actions.append(action)
            
            return hand
            
        except Exception as e:
            print(f"❌ Error converting hand model: {e}")
            raise
    
    def create_hands_review_session(self, hand_model: Hand) -> HandsReviewSession:
        """Create a hands review session for the given hand."""
        try:
            # Create game config
            config = GameConfig(
                num_players=len(hand_model.seats),
                small_blind=getattr(hand_model.metadata, 'small_blind', 1.0),
                big_blind=getattr(hand_model.metadata, 'big_blind', 2.0),
                starting_stack=getattr(hand_model.metadata, 'starting_stack', 1000.0)
            )
            
            # Create decision engine
            decision_engine = HandModelDecisionEngine(hand_model)
            
            # Create hands review session
            session = HandsReviewSession(config, decision_engine)
            
            # Initialize session
            if not session.initialize_session():
                raise Exception("Failed to initialize session")
            
            # Link decision engine to FPSM
            decision_engine.fpsm = session.fpsm
            
            # Prepare initial state for the session
            initial_state = {
                'players': [],
                'pot': 0.0,
                'current_bet': 0.0,
                'street': 'preflop',
                'board': [],
                'dealer_position': next((i for i, seat in enumerate(hand_model.seats) if seat.is_button), 0)
            }
            
            # Add players from hand model
            for seat in hand_model.seats:
                player_data = {
                    'name': seat.player_uid or f'seat{seat.seat_no}',
                    'stack': seat.starting_stack,
                    'position': f'seat{seat.seat_no}',
                    'is_human': False,
                    'is_active': True,
                    'cards': hand_model.metadata.hole_cards.get(seat.player_uid, []),
                    'current_bet': 0.0
                }
                initial_state['players'].append(player_data)
            
            # Calculate initial pot and current_bet from blind actions
            try:
                preflop = hand_model.streets.get(Street.PREFLOP, StreetState())
                for action in preflop.actions:
                    if action.action.value == 'POST_BLIND':
                        initial_state['pot'] += action.amount
                        initial_state['current_bet'] = max(initial_state['current_bet'], action.amount)
            except Exception as e:
                print(f"⚠️ Warning: Could not calculate initial blinds: {e}")
            
            # Load hand data into session
            session.set_preloaded_hand_data({'initial_state': initial_state})
            session.load_hand_for_review({'initial_state': initial_state})
            
            return session
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            raise
    
    def validate_hand(self, hand_index: int, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single hand using the new architecture."""
        hand_id = hand_data.get('metadata', {}).get('hand_id', f'hand_{hand_index}')
        
        try:
            print(f"🔍 Validating hand {hand_index + 1}: {hand_id}")
            
            # Convert to Hand model
            hand_model = self.load_hand_model(hand_data)
            print(f"   ✅ Converted to Hand Model: {len(hand_model.seats)} players, {len(hand_model.streets)} streets")
            
            # Create session
            session = self.create_hands_review_session(hand_model)
            print(f"   ✅ Created hands review session")
            
            # Start the hand
            if not session.start_hand():
                raise Exception("Failed to start hand")
            
            # Run through all actions
            max_actions = 20  # Reduced safety limit for debugging
            actions_executed = 0
            
            import time
            start_time = time.time()
            timeout_seconds = 10  # 10 second timeout per hand
            
            while (not session.is_replay_complete() and 
                   actions_executed < max_actions and 
                   session.session_active):
                
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"⏰ TIMEOUT: Hand took longer than {timeout_seconds} seconds")
                    break
                
                if not session.step_forward():
                    break
                
                actions_executed += 1
                
                # Progress indicator every 5 actions
                if actions_executed % 5 == 0:
                    print(f"   ... {actions_executed} actions executed")
            
            # Get final state
            final_game_info = session.get_game_info()
            
            # Compare with original hand data
            original_final_pot = hand_data.get('metadata', {}).get('final_pot', 0)
            final_pot = final_game_info.get('pot', 0)
            
            # Determine success
            pot_match = abs(final_pot - original_final_pot) < 0.01
            success = pot_match
            
            result = {
                'hand_index': hand_index,
                'hand_id': hand_id,
                'success': success,
                'actions_executed': actions_executed,
                'final_pot': final_pot,
                'original_pot': original_final_pot,
                'pot_match': pot_match,
                'errors': [] if success else [f"Pot mismatch: expected {original_final_pot}, got {final_pot}"]
            }
            
            if success:
                print(f"   ✅ PASSED: {actions_executed} actions, pot: ${final_pot}")
            else:
                print(f"   ❌ FAILED: Pot mismatch - expected ${original_final_pot}, got ${final_pot}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'hand_index': hand_index,
                'hand_id': hand_id,
                'success': False,
                'actions_executed': 0,
                'final_pot': 0,
                'original_pot': 0,
                'pot_match': False,
                'errors': [str(e)]
            }
    
    def run_validation(self, max_hands: int = 100) -> Dict[str, Any]:
        """Run validation on multiple hands."""
        print("🧪 Hands Review Validation Tester V2 (Clean Architecture)")
        print("=" * 60)
        print("🚀 Starting Hands Review Validation")
        print(f"📁 Loading hands from: {self.legendary_hands_path}")
        print(f"🎯 Target: Validate up to {max_hands} hands")
        print("=" * 60)
        
        # Load hands
        hands = self.load_legendary_hands()
        if not hands:
            return {'success': False, 'error': 'No hands loaded'}
        
        print(f"📊 Loaded {len(hands)} hands")
        
        # Validate hands
        results = []
        successful_hands = 0
        
        for i, hand_data in enumerate(hands[:max_hands]):
            result = self.validate_hand(i, hand_data)
            results.append(result)
            
            if result['success']:
                successful_hands += 1
        
        # Calculate summary
        total_hands = len(results)
        success_rate = (successful_hands / total_hands * 100) if total_hands > 0 else 0
        
        summary = {
            'total_hands': total_hands,
            'successful_hands': successful_hands,
            'failed_hands': total_hands - successful_hands,
            'success_rate': success_rate,
            'results': results
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total hands tested: {total_hands}")
        print(f"Successful: {successful_hands}")
        print(f"Failed: {total_hands - successful_hands}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print("🎉 ALL HANDS PASSED! Clean architecture working perfectly!")
        elif success_rate > 0:
            print(f"🔧 {success_rate:.1f}% success - some issues remain")
        else:
            print("❌ All hands failed - major issues to resolve")
        
        return summary


def main():
    """Run the validation test."""
    validator = HandsReviewValidatorV2()
    results = validator.run_validation(max_hands=3)  # Test 3 hands first
    
    # Save results
    results_file = "hands_review_validation_results_v2.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
