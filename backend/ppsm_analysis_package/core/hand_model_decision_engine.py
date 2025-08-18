#!/usr/bin/env python3
"""
Decision engine based on the standardized Hand model format.

This replaces PreloadedDecisionEngine with a much more robust implementation
that uses the comprehensive Hand model for perfect action replay.
"""

import sys
import os
from typing import Dict, Any, Optional, List

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.core.hand_model import Hand, Street, ActionType, Action
from backend.core.decision_engine_v2 import DecisionEngine

class HandModelDecisionEngine(DecisionEngine):
    """
    Decision engine that replays actions from a standardized Hand model.
    
    This provides much more reliable action replay than PreloadedDecisionEngine
    by using the comprehensive Hand data structure with proper action ordering,
    street organization, and complete metadata.
    """
    
    @staticmethod
    def _canon(player_id: str) -> str:
        """Canonicalize player ID for matching. Handles both 'Player1' and 'Player 1' formats."""
        if not player_id:
            return ""
        # Remove spaces and convert to lowercase for comparison
        return player_id.replace(' ', '').lower()
    
    def __init__(self, hand: Hand, fpsm=None):
        """
        Initialize with a Hand model object.
        
        Args:
            hand: Complete Hand object with all actions and metadata
            fpsm: Optional FPSM reference for hands review street advancement
        """
        self.hand = hand
        self.fpsm = fpsm  # Optional FPSM reference for street advancement
        self.actions_by_street = self._organize_actions_by_street()
        self.current_action_index = 0
        self.current_street = Street.PREFLOP
        # Get all actions for replay (excluding system actions like DEAL_HOLE)
        self.actions_for_replay = self._get_player_actions()
        self.total_actions = len(self.actions_for_replay)
        
        print(f"🎯 HAND_MODEL_ENGINE: Initialized with {self.total_actions} player actions")
    
    def _get_player_actions(self) -> List[Action]:
        """Get all player actions (excluding system actions like DEAL_HOLE)."""
        player_actions = []
        
        # Get all actions from all streets
        all_actions = self.hand.get_all_actions()
        
        # Filter out system actions and blind actions (since blinds are posted automatically)
        # Keep only actual betting decisions
        betting_action_types = {
            ActionType.CHECK, ActionType.BET, 
            ActionType.CALL, ActionType.RAISE, ActionType.FOLD
        }
        
        for action in all_actions:
            if action.action in betting_action_types and action.actor_uid:
                player_actions.append(action)
            elif action.action == ActionType.POST_BLIND:
                print(f"🔄 HAND_MODEL_ENGINE: Skipping POST_BLIND action (blinds already posted)")
        
        print(f"🎯 HAND_MODEL_ENGINE: Found {len(player_actions)} player actions out of {len(all_actions)} total actions")
        
        # Sort by street first (preflop, flop, turn, river), then by order within street
        street_order = {Street.PREFLOP: 0, Street.FLOP: 1, Street.TURN: 2, Street.RIVER: 3}
        sorted_actions = sorted(player_actions, key=lambda a: (street_order.get(a.street, 99), a.order))
        
        # Debug: Verify chronological order is correct
        print(f"🎯 HAND_MODEL_ENGINE: Actions now in chronological order (first 4):")
        for i, action in enumerate(sorted_actions[:4]):
            print(f"  {i}: {action.actor_uid} {action.action.value} {action.amount} (street: {action.street})")
        
        return sorted_actions
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current decision session."""
        return {
            "hand_id": getattr(self.hand.metadata, 'hand_id', 'Unknown'),
            "total_actions": self.total_actions,
            "current_action": self.current_action_index,
            "current_street": self.current_street.name if hasattr(self.current_street, 'name') else str(self.current_street),
            "engine_type": "HandModelDecisionEngine",
            "session_complete": self.is_session_complete()
        }
        print(f"   Hand ID: {self.hand.metadata.hand_id}")
        print(f"   Players: {len(self.hand.seats)}")
        self._log_action_summary()
    
    def _organize_actions_by_street(self) -> Dict[Street, List[Action]]:
        """Organize actions by street for easy access."""
        return {
            street: street_state.actions
            for street, street_state in self.hand.streets.items()
        }
    
    def _get_betting_actions(self) -> List[Action]:
        """Get only the betting actions (exclude blind postings and deal markers)."""
        betting_actions = []
        
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            for action in self.actions_by_street.get(street, []):
                # Include only actual betting decisions, not postings or deals
                if action.action in [ActionType.CHECK, ActionType.BET, ActionType.CALL, 
                                   ActionType.RAISE, ActionType.FOLD]:
                    betting_actions.append(action)
        
        # Sort by street first (preflop, flop, turn, river), then by order within street
        street_order = {Street.PREFLOP: 0, Street.FLOP: 1, Street.TURN: 2, Street.RIVER: 3}
        return sorted(betting_actions, key=lambda a: (street_order.get(a.street, 99), a.order))
    
    def _log_action_summary(self):
        """Log summary of actions for debugging."""
        street_counts = {}
        for action in self.actions_for_replay:
            street = action.street
            if street not in street_counts:
                street_counts[street] = 0
            street_counts[street] += 1
        
        print(f"🎯 ACTION_SUMMARY: {street_counts}")
    
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the next decision for the specified player.
        
        Args:
            player_index: Index of player who needs to act
            game_state: Current game state
            
        Returns:
            Dictionary with action details
        """
        # Check if we've exhausted all actions
        if self.current_action_index >= self.total_actions:
            print(f"🛡️ HAND_MODEL_ENGINE: No more actions ({self.current_action_index}/{self.total_actions})")
            return self._default_action(player_index)
        
        # Get current player's UID and street from game state
        current_player_uid = None
        current_street = None
        try:
            # game_state['players'] is a list of dicts, not Player objects
            players = game_state.get('players', [])
            if player_index < len(players):
                # Try to get player_uid from the dict, fallback to name/position
                player_dict = players[player_index]
                current_player_uid = (
                    player_dict.get('player_uid') or 
                    player_dict.get('name') or 
                    f"seat{player_dict.get('position', player_index + 1)}"
                )
            
            # Get current street from game state
            current_street = str(game_state.get('state', 'preflop')).lower()
            # Map FPSM state names to street names
            street_mapping = {
                'preflop': 'preflop',
                'preflop_betting': 'preflop',
                'flop': 'flop', 
                'flop_betting': 'flop',
                'turn': 'turn',
                'turn_betting': 'turn', 
                'river': 'river',
                'river_betting': 'river',
                'deal_flop': 'flop',
                'deal_turn': 'turn', 
                'deal_river': 'river'
            }
            current_street = street_mapping.get(current_street, current_street)
            
        except Exception as e:
            print(f"❌ HAND_MODEL_ENGINE: Error getting current player/street: {e}")
            pass
        
        # Find the next action for the current player on the current street
        original_index = self.current_action_index
        while self.current_action_index < self.total_actions:
            next_action = self.actions_for_replay[self.current_action_index]
            actor_uid = getattr(next_action, 'actor_uid', None)
            action_street = str(getattr(next_action, 'street', 'preflop')).lower()
            
            # Normalize action street names (handle Street.PREFLOP -> street.preflop)
            if action_street.startswith('street.'):
                action_street = action_street.replace('street.', '')
            elif '.' in action_street:
                action_street = action_street.split('.')[-1]
            
            print(f"🔍 HAND_MODEL_ENGINE: Action {self.current_action_index + 1}/{self.total_actions}")
            print(f"   Action player: {actor_uid}")
            print(f"   Current player: {current_player_uid} (index {player_index})")
            print(f"   Action street: {action_street}")
            print(f"   Current street: {current_street}")
            print(f"   Action: {next_action.action.value}, Amount: {next_action.amount}")
            
            # Check if this action belongs to the current player AND current street
            player_match = str(actor_uid).lower() == str(current_player_uid).lower()
            street_match = action_street == current_street
            
            if player_match and street_match:
                # Found matching action
                decision = self._convert_action_to_decision(next_action, player_index)
                decision['actor_index'] = player_index
                decision['actor_uid'] = actor_uid
                
                # Advance to next action
                self.current_action_index += 1
                return decision
            else:
                # Skip this action, it's for a different player or street
                if not player_match:
                    print(f"🔄 HAND_MODEL_ENGINE: Skipping action for {actor_uid}, looking for {current_player_uid}")
                elif not street_match:
                    print(f"🔄 HAND_MODEL_ENGINE: Street mismatch - action is {action_street}, FPSM is on {current_street}")
                    
                    # HANDS REVIEW: Manually advance FPSM street if needed
                    if hasattr(self, '_advance_fpsm_street_if_needed'):
                        street_advanced = self._advance_fpsm_street_if_needed(current_street, action_street, game_state)
                        if street_advanced:
                            print(f"🔧 HAND_MODEL_ENGINE: Advanced FPSM from {current_street} to {action_street}")
                            # Retry this action with the updated street
                            continue
                    
                    print(f"🔄 HAND_MODEL_ENGINE: Skipping {action_street} action, currently on {current_street}")
                self.current_action_index += 1
        
        # No matching action found
        print(f"🛡️ HAND_MODEL_ENGINE: No action found for player {current_player_uid} (index {player_index})")
        return self._default_action(player_index)
    
    def _convert_action_to_decision(self, action: Action, player_index: int) -> Dict[str, Any]:
        """Convert Hand model Action to decision engine format."""
        
        # Map ActionType to our decision format
        action_type_map = {
            ActionType.FOLD: 'fold',
            ActionType.CHECK: 'check', 
            ActionType.CALL: 'call',
            ActionType.BET: 'bet',
            ActionType.RAISE: 'raise'
        }
        
        action_str = action_type_map.get(action.action, 'fold')
        
        return {
            'action': action.action,  # Keep ActionType enum
            'amount': float(action.amount),
            'explanation': f"[Hand Model] {action_str.title()} from {getattr(action,'actor_uid',None)}. {action.note or 'Replaying recorded action.'}",
            'confidence': 1.0,
            'decision_number': self.current_action_index + 1,
            'street': action.street.value,
            'original_order': action.order
        }
    
    def _default_action(self, player_index: int) -> Dict[str, Any]:
        """Return a default action when no more actions available."""
        return {
            'action': ActionType.CHECK,
            'amount': 0.0,
            'explanation': f"[Hand Model] No more preloaded actions available for Player {str(player_index + 1)}",
            'confidence': 0.0,
            'decision_number': self.current_action_index + 1
        }
    
    def is_session_complete(self) -> bool:
        """Check if all actions have been replayed."""
        return self.current_action_index >= self.total_actions
    
    def get_progress(self) -> Dict[str, Any]:
        """Get replay progress information."""
        return {
            'current_action': self.current_action_index,
            'total_actions': self.total_actions,
            'progress_percent': (self.current_action_index / max(1, self.total_actions)) * 100,
            'actions_remaining': max(0, self.total_actions - self.current_action_index)
        }
    
    def reset(self):
        """Reset the engine to the beginning of the hand."""
        self.current_action_index = 0
        self.current_street = Street.PREFLOP
        print(f"🔄 HAND_MODEL_ENGINE: Reset to beginning ({self.total_actions} actions available)")
    
    def _advance_fpsm_street_if_needed(self, current_street: str, target_street: str, game_state: dict) -> bool:
        """
        Manually advance FPSM street for hands review mode.
        
        Args:
            current_street: Current FPSM street (e.g., 'preflop')
            target_street: Target street from action (e.g., 'flop')
            game_state: Current game state
            
        Returns:
            True if street was advanced, False otherwise
        """
        if not self.fpsm:
            return False
            
        # Define street progression
        street_progression = ['preflop', 'flop', 'turn', 'river']
        
        try:
            current_idx = street_progression.index(current_street)
            target_idx = street_progression.index(target_street)
        except ValueError:
            print(f"❌ STREET_ADVANCE: Unknown street - current: {current_street}, target: {target_street}")
            return False
        
        # Only advance forward, not backward
        if target_idx <= current_idx:
            return False
            
        print(f"🔧 STREET_ADVANCE: Advancing FPSM from {current_street} to {target_street}")
        
        # Manually update FPSM state for hands review
        try:
            # Update the street directly
            self.fpsm.game_state.street = target_street
            
            # Update the FPSM state to the appropriate betting state
            state_mapping = {
                'preflop': 'PREFLOP_BETTING',
                'flop': 'FLOP_BETTING', 
                'turn': 'TURN_BETTING',
                'river': 'RIVER_BETTING'
            }
            
            if target_street in state_mapping:
                from .poker_types import PokerState
                new_state = getattr(PokerState, state_mapping[target_street])
                self.fpsm.current_state = new_state
                print(f"🔧 STREET_ADVANCE: Set FPSM state to {new_state}")
            
            # Reset betting for new street (but preserve pot)
            self.fpsm.game_state.current_bet = 0.0
            for player in self.fpsm.game_state.players:
                player.current_bet = 0.0
            
            print(f"🔧 STREET_ADVANCE: Successfully advanced to {target_street}")
            return True
            
        except Exception as e:
            print(f"❌ STREET_ADVANCE: Failed to advance street: {e}")
            return False

# Test the engine with our converted data
if __name__ == "__main__":
    from backend.core.hand_model import Hand
    
    # Test with converted hand data
    test_files = [
        "cycle_test_hand_hand_model.json",
        "gto_hand_for_verification_hand_model.json"
    ]
    
    for test_file in test_files:
        try:
            print(f"\n🧪 Testing HandModelDecisionEngine with {test_file}")
            print("=" * 60)
            
            hand = Hand.load_json(test_file)
            engine = HandModelDecisionEngine(hand)
            
            print(f"Hand loaded: {hand.metadata.hand_id}")
            print(f"Total actions for replay: {engine.total_actions}")
            
            # Test getting a few decisions
            for i in range(min(3, engine.total_actions)):
                decision = engine.get_decision(0, {})  # Test with player 0
                print(f"Decision {i+1}: {decision['action'].value} ${decision['amount']:.2f}")
                
                if engine.is_session_complete():
                    break
            
            progress = engine.get_progress()
            print(f"Progress: {progress['current_action']}/{progress['total_actions']} ({progress['progress_percent']:.1f}%)")
            
        except FileNotFoundError:
            print(f"⚠️  Test file {test_file} not found - run converter first")
        except Exception as e:
            print(f"❌ Test failed for {test_file}: {e}")
    
    print("\n✅ HandModelDecisionEngine test complete!")
