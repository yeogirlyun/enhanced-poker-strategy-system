#!/usr/bin/env python3
"""
Comprehensive Legendary Hands JSON Generator

This script creates a complete JSON format for all legendary hands that includes:
1. Full hand metadata and configuration 
2. Step-by-step action simulation with FPSM
3. Stack and pot progression at every step
4. Board card reveals by street
5. Winner determination and showdown data
6. Complete game state at each decision point

This JSON format will be machine-readable and eliminate all PHH parsing issues.
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.hands_database import LegendaryHandsPHHLoader
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player, ActionType, PokerState
from core.position_mapping import UniversalPosition

class ComprehensiveLegendaryHandsJSONGenerator:
    """Generates comprehensive JSON format for all legendary hands with full simulation data."""
    
    def __init__(self):
        self.loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
        self.hands = []
        self.comprehensive_hands = []
        self.simulation_results = []
        self.total_hands = 0
        self.successful_simulations = 0
        self.errors = []
        
    def generate_comprehensive_json(self):
        """Generate the complete comprehensive JSON file."""
        print("🎯 COMPREHENSIVE LEGENDARY HANDS JSON GENERATOR")
        print("=" * 70)
        
        # Step 1: Load all legendary hands
        self.load_legendary_hands()
        
        # Step 2: Simulate each hand with FPSM to get full data
        self.simulate_all_hands()
        
        # Step 3: Save comprehensive JSON file
        json_file_path = self.save_comprehensive_json()
        
        # Step 4: Generate summary report
        self.generate_summary_report(json_file_path)
        
        return json_file_path
    
    def load_legendary_hands(self):
        """Load all legendary hands from PHH file."""
        print("📚 Loading legendary hands...")
        
        self.hands = self.loader.load_hands()
        self.total_hands = len(self.hands)
        
        # Filter only complete hands (hands with actions)
        complete_hands = [hand for hand in self.hands if hand.actions]
        complete_count = len(complete_hands)
        incomplete_count = self.total_hands - complete_count
        
        print(f"✅ Loaded {self.total_hands} total hands")
        print(f"   📋 Complete hands: {complete_count}")
        print(f"   ⚠️  Incomplete hands: {incomplete_count}")
        
        # Use only complete hands
        self.hands = complete_hands
        self.total_hands = len(self.hands)
        
    def simulate_all_hands(self):
        """Simulate all hands with FPSM to generate comprehensive data."""
        print(f"🎮 Simulating {self.total_hands} hands with FPSM...")
        
        for i, hand in enumerate(self.hands):
            hand_id = hand.metadata.id
            hand_name = hand.metadata.name
            
            print(f"  [{i+1:2d}/{self.total_hands}] Simulating: {hand_name}")
            
            try:
                comprehensive_data = self.simulate_single_hand(hand)
                self.comprehensive_hands.append(comprehensive_data)
                self.successful_simulations += 1
                
            except Exception as e:
                error_msg = f"Simulation failed for {hand_id}: {str(e)}"
                print(f"    ❌ {error_msg}")
                self.errors.append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'error': error_msg
                })
        
        print(f"✅ Successfully simulated {self.successful_simulations}/{self.total_hands} hands")
    
    def simulate_single_hand(self, hand) -> Dict[str, Any]:
        """Simulate a single hand to generate comprehensive data."""
        # Extract basic hand info
        hand_id = hand.metadata.id
        hand_name = hand.metadata.name
        players_data = hand.players
        actions_data = hand.actions
        
        # Create FPSM configuration
        num_players = len(players_data)
        config = GameConfig(
            num_players=num_players,
            big_blind=2000.0,   # Standard for legendary hands
            small_blind=1000.0,
            starting_stack=1000000.0,  # Default (will be overridden)
            test_mode=True
        )
        
        # Create FPSM instance
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players with actual starting stacks
        players = []
        for i, player_data in enumerate(players_data):
            if isinstance(player_data, dict):
                player_name = player_data.get('name', f'Player_{i}')
                starting_stack = player_data.get('starting_stack_chips', config.starting_stack)
                seat = player_data.get('seat', i + 1)
                cards = player_data.get('cards', [])
            else:
                player_name = getattr(player_data, 'name', f'Player_{i}')
                starting_stack = getattr(player_data, 'starting_stack_chips', config.starting_stack)
                seat = getattr(player_data, 'seat', i + 1)
                cards = getattr(player_data, 'cards', [])
            
            player = Player(
                name=player_name,
                stack=starting_stack,
                position=UniversalPosition.BB.value,  # Will be set correctly by FPSM
                is_human=False,
                is_active=True,
                cards=cards
            )
            players.append(player)
        
        # Initialize the hand
        fpsm.start_hand(players)
        
        # Build actor mapping (PHH actor ID -> FPSM player index)
        actor_to_fpsm = self._build_actor_mapping(players_data, fpsm.game_state.players)
        
        # Prepare comprehensive data structure
        comprehensive_data = {
            'metadata': {
                'id': hand_id,
                'name': hand_name,
                'event': getattr(hand.metadata, 'event', ''),
                'note': getattr(hand.metadata, 'note', ''),
                'variant': "No-Limit Hold'em",
                'simulation_timestamp': datetime.now().isoformat()
            },
            'initial_config': {
                'num_players': num_players,
                'big_blind': config.big_blind,
                'small_blind': config.small_blind,
                'button_position': fpsm.dealer_position
            },
            'players': self._get_initial_player_data(fpsm.game_state.players),
            'simulation_steps': [],
            'streets': {
                'preflop': {'actions': [], 'board_cards': []},
                'flop': {'actions': [], 'board_cards': []},
                'turn': {'actions': [], 'board_cards': []},
                'river': {'actions': [], 'board_cards': []}
            },
            'final_result': {},
            'actor_mapping': actor_to_fpsm
        }
        
        # Simulate all actions step by step
        step_number = 0
        
        # Get all actions in chronological order
        all_actions = []
        for street in ['preflop', 'flop', 'turn', 'river']:
            if street in actions_data:
                street_actions = actions_data[street]
                if isinstance(street_actions, list):
                    for action in street_actions:
                        all_actions.append((street, action))
        
        # Execute each action and record game state
        action_index = 0
        max_actions = 200
        current_street = 'preflop'
        
        while not self._is_hand_complete(fpsm) and action_index < len(all_actions) and step_number < max_actions:
            # Get current game state before action
            pre_action_state = self._capture_game_state(fpsm, step_number, 'pre_action')
            
            # Get current action player
            current_player = fpsm.get_action_player()
            if not current_player:
                break
            
            # Get next historical action
            if action_index < len(all_actions):
                street, action_data = all_actions[action_index]
                current_street = street
                action_index += 1
                
                # Verify actor mapping
                phh_actor_id = action_data.get('actor') if isinstance(action_data, dict) else None
                if phh_actor_id:
                    expected_fpsm_index = actor_to_fpsm.get(phh_actor_id)
                    if expected_fpsm_index is not None:
                        expected_player = fpsm.game_state.players[expected_fpsm_index]
                        current_fpsm_index = fpsm.game_state.players.index(current_player) if current_player in fpsm.game_state.players else -1
                        
                        if expected_fpsm_index != current_fpsm_index:
                            # Skip mismatched actions and let FPSM natural order continue
                            continue
                
                # Parse and execute action
                action_type, amount = self._parse_action(action_data)
                if action_type:
                    # Execute the action
                    success = fpsm.execute_action(current_player, action_type, amount)
                    
                    # Capture game state after action
                    post_action_state = self._capture_game_state(fpsm, step_number, 'post_action')
                    
                    # Record the simulation step
                    step_data = {
                        'step_number': step_number,
                        'street': current_street,
                        'action': {
                            'player_name': current_player.name,
                            'player_index': fpsm.game_state.players.index(current_player),
                            'action_type': action_type.value,
                            'amount': amount,
                            'success': success
                        },
                        'pre_action_state': pre_action_state,
                        'post_action_state': post_action_state
                    }
                    
                    comprehensive_data['simulation_steps'].append(step_data)
                    comprehensive_data['streets'][current_street]['actions'].append(step_data['action'])
                    
                    step_number += 1
                    
                    if not success:
                        break
            else:
                break
        
        # Record final hand result
        comprehensive_data['final_result'] = {
            'hand_complete': self._is_hand_complete(fpsm),
            'final_state': fpsm.current_state.name if fpsm.current_state else 'UNKNOWN',
            'total_steps': step_number,
            'total_pot': fpsm.game_state.pot,
            'final_players': self._get_final_player_data(fpsm.game_state.players),
            'simulation_success': step_number > 0 and self._is_hand_complete(fpsm)
        }
        
        return comprehensive_data
    
    def _build_actor_mapping(self, players_data, fpsm_players):
        """Build mapping from PHH actor ID to FPSM player index."""
        actor_to_fpsm = {}
        
        for fpsm_index, fpsm_player in enumerate(fpsm_players):
            # First, try exact name matching
            matched = False
            for i, player_data in enumerate(players_data):
                if isinstance(player_data, dict):
                    hand_name = player_data.get('name', f'Player_{i}')
                    hand_seat = player_data.get('seat', i + 1)
                else:
                    hand_name = getattr(player_data, 'name', f'Player_{i}')
                    hand_seat = getattr(player_data, 'seat', i + 1)
                
                if fpsm_player.name == hand_name:
                    actor_to_fpsm[hand_seat] = fpsm_index
                    matched = True
                    break
            
            # If no name match, map by position order
            if not matched and fpsm_index < len(players_data):
                if isinstance(players_data[fpsm_index], dict):
                    hand_seat = players_data[fpsm_index].get('seat', fpsm_index + 1)
                else:
                    hand_seat = getattr(players_data[fpsm_index], 'seat', fpsm_index + 1)
                actor_to_fpsm[hand_seat] = fpsm_index
        
        return actor_to_fpsm
    
    def _parse_action(self, action_data) -> Tuple[Optional[ActionType], float]:
        """Parse action data into ActionType and amount."""
        if not action_data:
            return None, 0.0
        
        if isinstance(action_data, dict):
            action_str = action_data.get('type', '').upper()
            
            # For RAISE actions, use 'to' field if available
            if action_str in ['RAISE', 'RERAISE', '3BET', '4BET', '5BET'] and 'to' in action_data:
                amount = action_data.get('to', 0.0)
            else:
                amount = action_data.get('amount', 0.0)
        elif isinstance(action_data, str):
            parts = action_data.split()
            action_str = parts[0].upper() if parts else ''
            amount = float(parts[1]) if len(parts) > 1 else 0.0
        else:
            return None, 0.0
        
        # Map action strings to ActionType
        action_mapping = {
            'FOLD': ActionType.FOLD,
            'CHECK': ActionType.CHECK,
            'CALL': ActionType.CALL,
            'BET': ActionType.BET,
            'RAISE': ActionType.RAISE,
            'RERAISE': ActionType.RAISE,
            '3BET': ActionType.RAISE,
            '4BET': ActionType.RAISE,
            '5BET': ActionType.RAISE,
            'ALL-IN': ActionType.RAISE,
            'ALL_IN': ActionType.RAISE,
            'ALLIN': ActionType.RAISE,
        }
        
        action_type = action_mapping.get(action_str)
        return action_type, amount
    
    def _capture_game_state(self, fpsm, step_number: int, phase: str) -> Dict[str, Any]:
        """Capture complete game state at a specific point."""
        return {
            'step_number': step_number,
            'phase': phase,
            'poker_state': fpsm.current_state.name if fpsm.current_state else 'UNKNOWN',
            'street': fpsm.game_state.street,
            'pot': fpsm.game_state.pot,
            'current_bet': fpsm.game_state.current_bet,
            'board_cards': fpsm.game_state.board[:],
            'action_player_index': fpsm.action_player_index,
            'action_player_name': fpsm.get_action_player().name if fpsm.get_action_player() else None,
            'players': [
                {
                    'name': player.name,
                    'stack': player.stack,
                    'current_bet': player.current_bet,
                    'has_folded': player.has_folded,
                    'is_active': player.is_active,
                    'cards': player.cards[:]
                }
                for player in fpsm.game_state.players
            ]
        }
    
    def _get_initial_player_data(self, players) -> List[Dict[str, Any]]:
        """Get initial player data."""
        return [
            {
                'name': player.name,
                'starting_stack': player.stack,
                'position': player.position,
                'cards': player.cards[:]
            }
            for player in players
        ]
    
    def _get_final_player_data(self, players) -> List[Dict[str, Any]]:
        """Get final player data."""
        return [
            {
                'name': player.name,
                'final_stack': player.stack,
                'final_bet': player.current_bet,
                'total_invested': getattr(player, 'total_invested', 0.0),
                'has_folded': player.has_folded,
                'cards': player.cards[:]
            }
            for player in players
        ]
    
    def _is_hand_complete(self, fpsm) -> bool:
        """Check if the hand simulation is complete."""
        if not fpsm or not hasattr(fpsm, 'current_state'):
            return True
        
        terminal_states = [PokerState.END_HAND, PokerState.SHOWDOWN]
        return fpsm.current_state in terminal_states
    
    def save_comprehensive_json(self) -> str:
        """Save the comprehensive hands data to JSON file."""
        json_file_path = "data/legendary_hands_comprehensive.json"
        
        print(f"💾 Saving comprehensive data for {len(self.comprehensive_hands)} hands...")
        
        # Create the complete JSON structure
        json_data = {
            'format_version': '2.0',
            'format_name': 'Comprehensive Legendary Hands',
            'description': 'Complete machine-readable format with full FPSM simulation data',
            'creation_date': datetime.now().isoformat(),
            'source': 'PHH format converted via FPSM simulation',
            'statistics': {
                'total_hands': self.total_hands,
                'successful_simulations': self.successful_simulations,
                'failed_simulations': len(self.errors),
                'success_rate': (self.successful_simulations / max(1, self.total_hands)) * 100
            },
            'hands': self.comprehensive_hands,
            'errors': self.errors
        }
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        file_size_kb = os.path.getsize(json_file_path) / 1024
        print(f"✅ Comprehensive JSON saved: {json_file_path} ({file_size_kb:.1f} KB)")
        
        return json_file_path
    
    def generate_summary_report(self, json_file_path: str):
        """Generate a summary report of the conversion process."""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE JSON GENERATION REPORT")
        print("=" * 70)
        
        success_rate = (self.successful_simulations / max(1, self.total_hands)) * 100
        
        print(f"📊 STATISTICS:")
        print(f"  Total hands processed: {self.total_hands}")
        print(f"  Successful simulations: {self.successful_simulations}")
        print(f"  Failed simulations: {len(self.errors)}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n❌ SIMULATION ERRORS:")
            for error in self.errors:
                print(f"  - {error['hand_name']}: {error['error']}")
        
        print(f"\n💾 OUTPUT:")
        print(f"  File: {json_file_path}")
        print(f"  Size: {os.path.getsize(json_file_path) / 1024:.1f} KB")
        
        if success_rate == 100.0:
            print("\n🎉 PERFECT! All hands simulated successfully!")
        elif success_rate >= 95.0:
            print("\n✅ EXCELLENT! Simulation quality is very high")
        elif success_rate >= 90.0:
            print("\n🟡 GOOD: Most hands simulated successfully")
        else:
            print("\n🔴 NEEDS WORK: Significant simulation issues detected")

def main():
    """Main function to generate comprehensive legendary hands JSON."""
    generator = ComprehensiveLegendaryHandsJSONGenerator()
    
    try:
        json_file_path = generator.generate_comprehensive_json()
        return 0 if generator.successful_simulations == generator.total_hands else 1
        
    except Exception as e:
        print(f"❌ Generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
