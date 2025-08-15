#!/usr/bin/env python3
"""
Comprehensive Hands Review Simulation Test

This test simulates the exact user flow:
1. Load a hand from the UI (like clicking "Load Selected Hand")
2. Simulate clicking "Next" button repeatedly
3. Verify hole cards are visible
4. Verify actions match the original hand
5. Verify the hand completes correctly

This will help identify why hole cards aren't showing and why sessions complete immediately.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from typing import List, Dict, Any
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.bot_session_state_machine import HandsReviewBotSession
from backend.core.flexible_poker_state_machine import GameConfig
from backend.core.session_logger import SessionLogger

class HandsReviewSimulator:
    """Simulates the complete Hands Review user experience."""
    
    def __init__(self):
        self.logger = SessionLogger()
        self.hands_review_session = None
        self.original_hand_data = None
        self.hand_model = None
        self.action_sequence = []
        self.replay_sequence = []
        
    def load_original_hand(self, hand_data: Dict[str, Any]) -> bool:
        """Step 1: Load and analyze the original hand data."""
        try:
            self.original_hand_data = hand_data
            print(f"📁 ORIGINAL HAND: {hand_data.get('id', 'Unknown')}")
            
            # Extract original actions for comparison
            original_actions = hand_data.get('actions', [])
            print(f"📊 ORIGINAL ACTIONS: {len(original_actions)} total")
            
            for i, action in enumerate(original_actions):
                player_idx = action.get('player_index', -1)
                action_type = action.get('action', 'unknown')
                amount = action.get('amount', 0)
                street = action.get('street', 'unknown')
                
                action_desc = f"Player{player_idx + 1} {action_type}"
                if amount > 0:
                    action_desc += f" ${amount}"
                action_desc += f" ({street})"
                
                self.action_sequence.append({
                    'order': i + 1,
                    'player_index': player_idx,
                    'action': action_type,
                    'amount': amount,
                    'street': street,
                    'description': action_desc
                })
                print(f"  {i+1:2d}. {action_desc}")
            
            # Extract original players with hole cards
            initial_state = hand_data.get('initial_state', {})
            players_data = initial_state.get('players', [])
            print(f"👥 ORIGINAL PLAYERS: {len(players_data)}")
            
            for i, player in enumerate(players_data):
                name = player.get('name', f'Player{i+1}')
                cards = player.get('hole_cards', player.get('cards', []))
                stack = player.get('stack', 0)
                print(f"  {name}: {cards} (${stack})")
                
                if not cards or cards == ['**', '**']:
                    print(f"  ⚠️  WARNING: {name} has no/hidden hole cards!")
            
            return True
            
        except Exception as e:
            print(f"❌ LOAD_ORIGINAL_ERROR: {e}")
            return False
    
    def convert_to_hand_model(self) -> bool:
        """Step 2: Convert to Hand Model format (like the UI does)."""
        try:
            print(f"\n🔄 CONVERTING TO HAND MODEL...")
            
            # Use the same converter as the UI
            self.hand_model = GTOToHandConverter.convert_gto_hand(self.original_hand_data)
            
            print(f"✅ HAND MODEL CREATED: {self.hand_model.metadata.hand_id}")
            print(f"   Players: {len(self.hand_model.seats)}")
            
            # Check if hole cards are in the Hand Model
            for seat in self.hand_model.seats:
                print(f"   {seat.player_id}: stack=${seat.starting_stack}")
                
                # Check if hole cards are in metadata
                if hasattr(self.hand_model.metadata, 'hole_cards'):
                    hole_cards = getattr(self.hand_model.metadata, 'hole_cards', {})
                    player_cards = hole_cards.get(seat.player_id, [])
                    print(f"     hole_cards: {player_cards}")
                else:
                    print(f"     ⚠️  No hole_cards in metadata!")
            
            # Check actions in Hand Model
            total_actions = sum(len(street_state.actions) for street_state in self.hand_model.streets.values())
            print(f"   Actions: {total_actions}")
            
            # Show action breakdown by street
            for street, street_state in self.hand_model.streets.items():
                if street_state.actions:
                    print(f"     {street.value}: {len(street_state.actions)} actions")
            
            return True
            
        except Exception as e:
            print(f"❌ CONVERSION_ERROR: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def create_hands_review_session(self) -> bool:
        """Step 3: Create the Hands Review session (like UI does)."""
        try:
            print(f"\n🎮 CREATING HANDS REVIEW SESSION...")
            
            # Create decision engine
            decision_engine = HandModelDecisionEngine(self.hand_model)
            print(f"🧠 Decision engine: {decision_engine.total_actions} actions")
            
            # Create game config
            config = GameConfig(
                num_players=len(self.hand_model.seats),
                starting_stack=1000,
                small_blind=5,
                big_blind=10
            )
            
            # Create session
            self.hands_review_session = HandsReviewBotSession(
                config=config, 
                decision_engine=decision_engine
            )
            
            # Set preloaded hand data (exactly like UI does)
            hand_data_for_session = {'hand_model': self.hand_model}
            self.hands_review_session.set_preloaded_hand_data(hand_data_for_session)
            
            print(f"✅ Session created for {len(self.hand_model.seats)} players")
            return True
            
        except Exception as e:
            print(f"❌ SESSION_CREATION_ERROR: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def start_session_and_check_cards(self) -> bool:
        """Step 4: Start session and verify hole cards are visible."""
        try:
            print(f"\n🚀 STARTING SESSION...")
            
            # Start the session
            success = self.hands_review_session.start_session()
            if not success:
                print(f"❌ Session start returned False")
                return False
            
            print(f"✅ Session started")
            
            # Get game info to check cards
            game_info = self.hands_review_session.get_game_info()
            players = game_info.get('players', [])
            
            print(f"🃏 HOLE CARDS CHECK:")
            cards_visible = True
            
            for i, player in enumerate(players):
                name = player.get('name', f'Player{i+1}')
                cards = player.get('cards', [])
                stack = player.get('stack', 0)
                
                print(f"   {name}: {cards} (${stack})")
                
                if not cards or cards == ['**', '**'] or cards == []:
                    print(f"   ❌ {name} cards not visible!")
                    cards_visible = False
                else:
                    print(f"   ✅ {name} cards visible")
            
            if not cards_visible:
                print(f"❌ HOLE CARDS NOT VISIBLE!")
                # Try to get display state
                display_state = self.hands_review_session.get_display_state()
                print(f"🔍 Display state card_visibilities: {display_state.get('card_visibilities', 'None')}")
                return False
            
            print(f"✅ All hole cards are visible")
            return True
            
        except Exception as e:
            print(f"❌ SESSION_START_ERROR: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def simulate_next_button_clicks(self) -> bool:
        """Step 5: Simulate clicking 'Next' button repeatedly."""
        try:
            print(f"\n▶️  SIMULATING NEXT BUTTON CLICKS...")
            
            max_actions = len(self.action_sequence)
            print(f"📊 Expecting {max_actions} actions to replay")
            
            action_count = 0
            
            while action_count < max_actions + 5:  # Safety buffer
                print(f"\n🔘 CLICK {action_count + 1}:")
                
                # Check if session is complete before trying to execute
                if hasattr(self.hands_review_session.decision_engine, 'is_session_complete'):
                    if self.hands_review_session.decision_engine.is_session_complete():
                        print(f"✅ Session marked as complete")
                        break
                
                # Get game state before action for debugging
                game_info_before = self.hands_review_session.get_game_info()
                current_player_idx = game_info_before.get('action_player_index', -1)
                current_player_name = "Unknown"
                if 0 <= current_player_idx < len(game_info_before.get('players', [])):
                    current_player_name = game_info_before['players'][current_player_idx].get('name', 'Unknown')
                
                print(f"   Before action: {current_player_name} (idx {current_player_idx}) to act")
                print(f"   Current bet: ${game_info_before.get('current_bet', 0)}")
                print(f"   Pot: ${game_info_before.get('pot', 0)}")
                
                # Get valid actions for debugging
                if current_player_idx >= 0:
                    valid_actions = self.hands_review_session.get_valid_actions()
                    print(f"   Valid actions: {valid_actions}")
                    
                    # Get current player bet for debugging
                    current_player = game_info_before['players'][current_player_idx]
                    print(f"   Player current bet: ${current_player.get('current_bet', 0)}")
                    print(f"   Player stack: ${current_player.get('stack', 0)}")
                
                # Execute next action (like clicking Next button)
                success = self.hands_review_session.execute_next_bot_action()
                
                if not success:
                    print(f"❌ execute_next_bot_action returned False")
                    break
                
                # Get the last decision from history
                decision_history = self.hands_review_session.get_decision_history()
                if decision_history:
                    last_decision = decision_history[-1]
                    player_name = last_decision.get('player_name', 'Unknown')
                    action = last_decision.get('action', 'unknown')
                    amount = last_decision.get('amount', 0)
                    
                    replay_desc = f"{player_name} {action}"
                    if amount > 0:
                        replay_desc += f" ${amount}"
                    
                    self.replay_sequence.append({
                        'order': action_count + 1,
                        'player_name': player_name,
                        'action': action,
                        'amount': amount,
                        'description': replay_desc
                    })
                    
                    print(f"   ✅ {replay_desc}")
                else:
                    print(f"   ⚠️  No decision history found")
                
                action_count += 1
                
                # Get current game state
                game_info = self.hands_review_session.get_game_info()
                current_state = game_info.get('current_state', 'unknown')
                pot = game_info.get('pot', 0)
                
                print(f"   State: {current_state}, Pot: ${pot}")
            
            print(f"\n📊 REPLAY SUMMARY:")
            print(f"   Actions executed: {len(self.replay_sequence)}")
            print(f"   Expected actions: {len(self.action_sequence)}")
            
            return True
            
        except Exception as e:
            print(f"❌ NEXT_BUTTON_ERROR: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def compare_sequences(self) -> bool:
        """Step 6: Compare original vs replay sequences."""
        try:
            print(f"\n🔍 COMPARING SEQUENCES...")
            
            print(f"\n📋 ORIGINAL SEQUENCE ({len(self.action_sequence)} actions):")
            for action in self.action_sequence:
                print(f"   {action['order']:2d}. {action['description']}")
            
            print(f"\n📋 REPLAY SEQUENCE ({len(self.replay_sequence)} actions):")
            for action in self.replay_sequence:
                print(f"   {action['order']:2d}. {action['description']}")
            
            print(f"\n🎯 SEQUENCE COMPARISON:")
            
            # Compare lengths
            if len(self.replay_sequence) != len(self.action_sequence):
                print(f"❌ LENGTH MISMATCH: Expected {len(self.action_sequence)}, got {len(self.replay_sequence)}")
                return False
            
            # Compare each action
            mismatches = 0
            for i in range(min(len(self.action_sequence), len(self.replay_sequence))):
                original = self.action_sequence[i]
                replay = self.replay_sequence[i]
                
                # Compare action type and amount
                orig_action = original['action'].upper()
                replay_action = replay['action'].upper()
                orig_amount = original['amount']
                replay_amount = replay['amount']
                
                if orig_action == replay_action and orig_amount == replay_amount:
                    print(f"   ✅ {i+1:2d}. {original['description']} == {replay['description']}")
                else:
                    print(f"   ❌ {i+1:2d}. {original['description']} != {replay['description']}")
                    mismatches += 1
            
            if mismatches == 0:
                print(f"\n🎉 PERFECT MATCH: All {len(self.action_sequence)} actions matched!")
                return True
            else:
                print(f"\n❌ MISMATCHES: {mismatches} out of {len(self.action_sequence)} actions didn't match")
                return False
            
        except Exception as e:
            print(f"❌ COMPARISON_ERROR: {e}")
            return False
    
    def run_full_simulation(self, hand_data: Dict[str, Any]) -> bool:
        """Run the complete simulation."""
        print(f"🎮 HANDS REVIEW FULL SIMULATION TEST")
        print(f"=" * 60)
        
        steps = [
            ("Load Original Hand", lambda: self.load_original_hand(hand_data)),
            ("Convert to Hand Model", self.convert_to_hand_model),
            ("Create Hands Review Session", self.create_hands_review_session),
            ("Start Session & Check Cards", self.start_session_and_check_cards),
            ("Simulate Next Button Clicks", self.simulate_next_button_clicks),
            ("Compare Sequences", self.compare_sequences)
        ]
        
        for step_name, step_func in steps:
            print(f"\n" + "=" * 60)
            print(f"🔄 STEP: {step_name}")
            print(f"=" * 60)
            
            if not step_func():
                print(f"\n❌ SIMULATION FAILED at step: {step_name}")
                return False
        
        print(f"\n" + "=" * 60)
        print(f"🎉 SIMULATION SUCCESSFUL!")
        print(f"   All steps completed without errors")
        print(f"   Hole cards were visible")
        print(f"   All actions matched perfectly")
        print(f"=" * 60)
        
        return True

def test_with_sample_hand():
    """Test with a sample GTO hand."""
    try:
        # Load a GTO hand file
        hand_files = ['cycle_test_hand.json', 'gto_hand_for_verification.json']
        
        for filename in hand_files:
            if os.path.exists(filename):
                print(f"📁 Loading test hand: {filename}")
                with open(filename, 'r') as f:
                    hand_data = json.load(f)
                
                simulator = HandsReviewSimulator()
                success = simulator.run_full_simulation(hand_data)
                
                if success:
                    print(f"✅ Test passed with {filename}")
                    return True
                else:
                    print(f"❌ Test failed with {filename}")
        
        print(f"❌ No suitable test files found")
        return False
        
    except Exception as e:
        print(f"❌ TEST_ERROR: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_with_sample_hand()
    sys.exit(0 if success else 1)
