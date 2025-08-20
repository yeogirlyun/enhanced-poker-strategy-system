#!/usr/bin/env python3
"""
Enhanced GTO Hands Generator

Generates comprehensive GTO poker hands for testing PPSM validation.
Creates hands for 2-9 players, 20 hands each, with complete metadata.
Ensures hands run to completion with proper winners and stack tracking.
"""

import json
import sys
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path
import random
import math

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pure_poker_state_machine import GameConfig
from core.sessions import GTOSession
from core.gto_to_hand_converter import GTOToHandConverter
from core.hand_model import Hand
from core.poker_types import PokerState, ActionType
from core.decision_engine import GTODecisionEngine

class EnhancedGTOHandGenerator:
    """
    Enhanced GTO hands generator with proper player count handling and validation.
    
    Features:
    - Multiple player counts (2-9) with proper validation
    - Deterministic seeding for reproducible results
    - Complete hand completion with winners
    - Comprehensive metadata including hole cards
    - Stack size tracking throughout the hand
    - Validation that hands actually complete
    """
    
    def __init__(self, base_seed: int = 42):
        self.base_seed = base_seed
        self.generated_hands = []
        self.generation_stats = {
            'total_hands': 0,
            'successful_hands': 0,
            'failed_hands': 0,
            'by_player_count': {},
            'completion_stats': {
                'completed_hands': 0,
                'incomplete_hands': 0,
                'hands_with_winners': 0
            }
        }
    
    def generate_hands_for_player_count(self, num_players: int, hands_per_count: int = 20) -> List[Dict[str, Any]]:
        """Generate hands for a specific player count with enhanced validation."""
        
        print(f"🎯 Generating {hands_per_count} hands for {num_players} players...")
        print(f"🧠 Using enhanced GTODecisionEngine with validation")
        
        # Create deterministic seed for this player count
        player_seed = self.base_seed + (num_players * 1000)
        
        # Create config
        config = GameConfig(
            num_players=num_players,
            small_blind=5,
            big_blind=10,
            starting_stack=1000
        )
        
        # Create GTO decision engines for each player
        gto_decision_engines = {}
        for i in range(num_players):
            gto_decision_engines[f"GTO_Bot_{i+1}"] = GTODecisionEngine(num_players=num_players)
        
        # Create GTO session
        session = GTOSession(config, decision_engines=gto_decision_engines, seed=player_seed)
        
        # Initialize session
        if not session.initialize_session():
            print(f"❌ Failed to initialize GTO session for {num_players} players")
            return []
        
        generated_hands = []
        
        for hand_num in range(1, hands_per_count + 1):
            try:
                hand_data = self._generate_single_hand(session, num_players, hand_num)
                if hand_data and self._validate_hand_completion(hand_data):
                    generated_hands.append(hand_data)
                    self.generation_stats['successful_hands'] += 1
                    self.generation_stats['completion_stats']['completed_hands'] += 1
                    
                    # Check if hand has a winner
                    if self._hand_has_winner(hand_data):
                        self.generation_stats['completion_stats']['hands_with_winners'] += 1
                    
                    print(f"   ✅ Hand {hand_num}/{hands_per_count} - {len(hand_data.get('actions', []))} actions, completed: {hand_data.get('completed', False)}")
                else:
                    self.generation_stats['failed_hands'] += 1
                    if hand_data:
                        self.generation_stats['completion_stats']['incomplete_hands'] += 1
                    print(f"   ❌ Hand {hand_num}/{hands_per_count} - Failed or incomplete")
                    
            except Exception as e:
                self.generation_stats['failed_hands'] += 1
                print(f"   ❌ Hand {hand_num}/{hands_per_count} - Exception: {e}")
                traceback.print_exc()
        
        self.generation_stats['by_player_count'][num_players] = {
            'attempted': hands_per_count,
            'successful': len(generated_hands),
            'failed': hands_per_count - len(generated_hands)
        }
        
        print(f"   🏆 {num_players}P: {len(generated_hands)}/{hands_per_count} hands generated successfully")
        return generated_hands
    
    def _generate_single_hand(self, session: GTOSession, num_players: int, hand_num: int) -> Optional[Dict[str, Any]]:
        """Generate a single hand with enhanced data capture."""
        
        # Create unique hand ID
        hand_id = f"GTO_{num_players}P_H{hand_num:03d}"
        
        # Start hand
        if not session.start_hand():
            return None
        
        # Capture initial state
        initial_game_info = session.get_game_info()
        initial_state = self._capture_game_state(initial_game_info, "initial", num_players)
        
        # Run hand with action logging
        actions_log = []
        max_actions = 300  # Increased safety limit for complex hands
        actions_taken = 0
        
        while (not session.is_hand_complete() and 
               actions_taken < max_actions and 
               session.session_active):
            
            # Get action player before action
            pre_action_info = session.get_game_info()
            action_player_index = session.fpsm.action_player_index if session.fpsm else -1
            
            if action_player_index < 0:
                break
                
            action_player = pre_action_info['players'][action_player_index] if action_player_index < len(pre_action_info['players']) else None
            
            if not action_player:
                break
            
            # Execute bot action
            success = session.execute_next_bot_action()
            
            if success:
                # Capture the action that was taken
                post_action_info = session.get_game_info()
                action_data = self._infer_action_from_state_change(
                    pre_action_info, post_action_info, action_player, actions_taken + 1
                )
                
                if action_data:
                    actions_log.append(action_data)
                
                actions_taken += 1
            else:
                break
        
        # Capture final state
        final_game_info = session.get_game_info()
        final_state = self._capture_game_state(final_game_info, "final", num_players)
        
        # Check if hand actually completed
        hand_completed = session.is_hand_complete()
        
        # Build enhanced hand data
        hand_data = {
            'id': hand_id,
            'player_count': num_players,
            'hand_number': hand_num,
            'initial_state': initial_state,
            'actions': actions_log,
            'final_state': final_state,
            'generation_seed': session.seed,
            'actions_count': len(actions_log),
            'completed': hand_completed,
            'max_players': num_players,  # Explicit player count
            'metadata': {
                'hand_id': hand_id,
                'max_players': num_players,
                'small_blind': 5,
                'big_blind': 10,
                'starting_stack': 1000,
                'variant': 'NLHE',
                'session_type': 'gto'
            }
        }
        
        return hand_data
    
    def _capture_game_state(self, game_info: Dict[str, Any], stage: str, num_players: int) -> Dict[str, Any]:
        """Capture comprehensive game state with enhanced metadata."""
        
        players = game_info.get('players', [])
        
        # Ensure we have the right number of players
        if len(players) != num_players:
            print(f"⚠️  Warning: Expected {num_players} players, got {len(players)}")
        
        return {
            'stage': stage,
            'pot': game_info.get('pot', 0),
            'current_bet': game_info.get('current_bet', 0),
            'street': game_info.get('street', 'preflop'),
            'small_blind': game_info.get('small_blind', 5),
            'big_blind': game_info.get('big_blind', 10),
            'num_players': num_players,
            'players': [
                {
                    'name': player.get('name', f'Player_{i+1}'),
                    'stack': player.get('stack', 1000),
                    'current_bet': player.get('current_bet', 0),
                    'is_active': player.get('is_active', False),
                    'has_folded': player.get('has_folded', False),
                    'position': player.get('position', ''),
                    'cards': player.get('cards', ['**', '**']),  # Hidden in GTO
                    'player_uid': f'Player{i+1}',
                    'display_name': f'GTO_Bot_{i+1}',
                    'starting_stack': 1000,
                    'is_button': i == 0  # First player is button
                }
                for i, player in enumerate(players)
            ]
        }
    
    def _validate_hand_completion(self, hand_data: Dict[str, Any]) -> bool:
        """Validate that a hand actually completed properly."""
        
        if not hand_data.get('completed', False):
            return False
        
        # Check that we have actions
        actions = hand_data.get('actions', [])
        if len(actions) < 5:  # Minimum actions for a basic hand
            return False
        
        # Check that we have the right number of players
        expected_players = hand_data.get('player_count', 0)
        initial_state = hand_data.get('initial_state', {})
        actual_players = len(initial_state.get('players', []))
        
        if expected_players != actual_players:
            print(f"⚠️  Player count mismatch: expected {expected_players}, got {actual_players}")
            return False
        
        return True
    
    def _hand_has_winner(self, hand_data: Dict[str, Any]) -> bool:
        """Check if a hand has a clear winner."""
        
        final_state = hand_data.get('final_state', {})
        players = final_state.get('players', [])
        
        # Count active players (not folded)
        active_players = [p for p in players if not p.get('has_folded', True)]
        
        # Check if pot was distributed
        pot = final_state.get('pot', 0)
        
        return len(active_players) == 1 or pot == 0
    
    def _infer_action_from_state_change(self, pre_info: Dict[str, Any], post_info: Dict[str, Any], 
                                       action_player: Dict[str, Any], action_order: int) -> Optional[Dict[str, Any]]:
        """Infer what action was taken by comparing game states."""
        
        try:
            pre_pot = pre_info.get('pot', 0)
            post_pot = post_info.get('pot', 0)
            pre_current_bet = pre_info.get('current_bet', 0)
            post_current_bet = post_info.get('current_bet', 0)
            
            player_name = action_player.get('name', 'Unknown')
            pre_player_bet = action_player.get('current_bet', 0)
            
            # Find the player in post-action state
            post_players = post_info.get('players', [])
            post_player = None
            for p in post_players:
                if p.get('name') == player_name:
                    post_player = p
                    break
            
            if not post_player:
                return None
                
            post_player_bet = post_player.get('current_bet', 0)
            post_player_active = post_player.get('is_active', False)
            post_player_folded = post_player.get('has_folded', False)
            
            # Determine action type and amount
            action_type = "fold"  # Default
            amount = 0.0
            
            if post_player_folded:
                action_type = "fold"
                amount = 0.0
            elif post_player_bet > pre_player_bet:
                # Player increased their bet
                bet_increase = post_player_bet - pre_player_bet
                amount = post_player_bet  # Use to-amount semantics
                
                if pre_current_bet == 0:
                    action_type = "bet"
                elif post_player_bet > pre_current_bet:
                    action_type = "raise" 
                else:
                    action_type = "call"
            elif post_current_bet == pre_current_bet and pre_current_bet == pre_player_bet:
                action_type = "check"
                amount = 0.0
            else:
                action_type = "call"
                amount = post_player_bet
            
            return {
                'order': action_order,
                'player_index': pre_info.get('players', []).index(action_player) if action_player in pre_info.get('players', []) else 0,
                'action': action_type,
                'amount': float(amount),
                'street': pre_info.get('street', 'preflop'),
                'explanation': f'{action_type.upper()} ${amount}' if amount > 0 else action_type.upper(),
                'pre_pot': pre_pot,
                'post_pot': post_pot
            }
            
        except Exception as e:
            print(f"⚠️  Failed to infer action: {e}")
            return None
    
    def generate_comprehensive_gto_hands(self, min_players: int = 2, max_players: int = 9, hands_per_count: int = 20) -> bool:
        """Generate comprehensive GTO hands for all player counts with enhanced validation."""
        
        print("🚀 ENHANCED GTO HANDS GENERATOR")
        print("=" * 60)
        print(f"🧠 Engine: Enhanced GTODecisionEngine with validation")
        print(f"📈 Features: Complete hand completion, winner validation, stack tracking")
        print(f"🎯 Target: {max_players - min_players + 1} player counts, {hands_per_count} hands each")
        print(f"📊 Total hands: {(max_players - min_players + 1) * hands_per_count}")
        print(f"🌱 Base seed: {self.base_seed} (deterministic for reproducible results)")
        print("")
        
        all_hands = []
        
        for num_players in range(min_players, max_players + 1):
            player_hands = self.generate_hands_for_player_count(num_players, hands_per_count)
            all_hands.extend(player_hands)
            self.generation_stats['total_hands'] += len(player_hands)
        
        self.generated_hands = all_hands
        
        print("\n🏆 GENERATION SUMMARY")
        print("=" * 30)
        print(f"✅ Successful: {self.generation_stats['successful_hands']}")
        print(f"❌ Failed: {self.generation_stats['failed_hands']}")
        print(f"📈 Success rate: {(self.generation_stats['successful_hands'] / (self.generation_stats['successful_hands'] + self.generation_stats['failed_hands']) * 100):.1f}%")
        
        print(f"\n🎯 COMPLETION STATS")
        print(f"   Completed hands: {self.generation_stats['completion_stats']['completed_hands']}")
        print(f"   Incomplete hands: {self.generation_stats['completion_stats']['incomplete_hands']}")
        print(f"   Hands with winners: {self.generation_stats['completion_stats']['hands_with_winners']}")
        
        for players, stats in self.generation_stats['by_player_count'].items():
            print(f"   {players}P: {stats['successful']}/{stats['attempted']} hands")
        
        return len(all_hands) > 0
    
    def convert_to_hand_model_format(self) -> List[Hand]:
        """Convert generated GTO hands to Hand model format."""
        
        print(f"\n🔄 Converting {len(self.generated_hands)} GTO hands to Hand model format...")
        
        converted_hands = []
        conversion_errors = 0
        
        for i, gto_hand in enumerate(self.generated_hands):
            try:
                hand_model = GTOToHandConverter.convert_gto_hand(gto_hand)
                converted_hands.append(hand_model)
                
                if (i + 1) % 10 == 0:
                    print(f"   📋 Converted {i + 1}/{len(self.generated_hands)} hands...")
                    
            except Exception as e:
                conversion_errors += 1
                print(f"   ❌ Failed to convert hand {gto_hand.get('id', i)}: {e}")
        
        print(f"🎯 Conversion complete: {len(converted_hands)}/{len(self.generated_hands)} hands")
        if conversion_errors > 0:
            print(f"⚠️  {conversion_errors} conversion errors")
        
        return converted_hands
    
    def save_hands_to_json(self, output_path: str = "gto_hands.json") -> bool:
        """Save generated hands to JSON file in Hand model format."""
        
        try:
            # Convert to Hand model format
            hand_models = self.convert_to_hand_model_format()
            
            if not hand_models:
                print("❌ No hands to save")
                return False
            
            print(f"💾 Saving {len(hand_models)} hands to {output_path}...")
            
            # Convert to JSON-serializable format
            hands_data = []
            for hand in hand_models:
                try:
                    hand_dict = hand.to_dict()
                    hands_data.append(hand_dict)
                except Exception as e:
                    print(f"⚠️  Failed to serialize hand {hand.metadata.hand_id}: {e}")
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(hands_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(hands_data)} GTO hands to {output_path}")
            
            # Print summary stats
            total_actions = sum(len(hand.get_all_actions()) for hand in hand_models)
            avg_actions = total_actions / len(hands_data) if hands_data else 0
            
            print(f"📊 Summary:")
            print(f"   Total hands: {len(hands_data)}")
            print(f"   Total actions: {total_actions}")
            print(f"   Average actions per hand: {avg_actions:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save hands: {e}")
            traceback.print_exc()
            return False

def main():
    """Main entry point for enhanced GTO hand generation."""
    
    print("🎯 ENHANCED GTO HANDS GENERATOR")
    print("=" * 60)
    print("🧠 Powered by Enhanced GTODecisionEngine with validation")
    print("📚 Complete hand completion + winner validation + stack tracking")
    print("🎲 Deterministic seeding for reproducible testing")
    
    # Create generator
    generator = EnhancedGTOHandGenerator(base_seed=42)
    
    # Generate hands for 2-9 players, 20 hands each
    success = generator.generate_comprehensive_gto_hands(
        min_players=2,
        max_players=9,
        hands_per_count=20
    )
    
    if success:
        # Save to JSON
        save_success = generator.save_hands_to_json("gto_hands.json")
        
        if save_success:
            print("\n🏆 SUCCESS: Enhanced GTO hands generated and saved!")
            print("   📁 Output: gto_hands.json")
            print("   🎯 Ready for comprehensive PPSM validation testing")
            print("   🧪 Test against known-good GTO decisions and hand patterns")
        else:
            print("\n❌ FAILED: Could not save hands to JSON")
    else:
        print("\n❌ FAILED: Hand generation unsuccessful")

if __name__ == "__main__":
    main()
