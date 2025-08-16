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
    
    def __init__(self, hand: Hand):
        """
        Initialize with a Hand model object.
        
        Args:
            hand: Complete Hand object with all actions and metadata
        """
        self.hand = hand
        self.actions_by_street = self._organize_actions_by_street()
        self.current_action_index = 0
        self.current_street = Street.PREFLOP
        self.actions_for_replay = self._get_betting_actions()
        self.total_actions = len(self.actions_for_replay)
        
        print(f"🎯 HAND_MODEL_ENGINE: Initialized with {self.total_actions} betting actions")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current decision session."""
        return {
            "hand_id": getattr(self.hand, 'hand_id', 'Unknown'),
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
        
        return sorted(betting_actions, key=lambda a: a.order)
    
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
        
        # Get the next action
        next_action = self.actions_for_replay[self.current_action_index]
        
        # Convert player index to expected canonical seat uid (lowercase)
        expected_player_id = f"seat{player_index + 1}"
        # Try to map by seat order: find seat with seat_no == player_index+1
        try:
            seat_ids_by_order = {}
            for seat in self.hand.seats:
                # hand.seats may be list of dataclasses; extract seat_no and canonical id
                sid = getattr(seat, 'seat_no', None)
                pid = getattr(seat, 'player_id', None)
                if sid is not None and pid:
                    seat_ids_by_order[int(sid)] = pid
            if (player_index + 1) in seat_ids_by_order:
                expected_player_id = str(seat_ids_by_order[player_index + 1]).lower()
        except Exception:
            pass
        
        print(f"🔍 HAND_MODEL_ENGINE: Action {self.current_action_index + 1}/{self.total_actions}")
        print(f"   Expected player: {expected_player_id}, Action player: {getattr(next_action,'actor_uid',None)}")
        print(f"   Action: {next_action.action.value}, Amount: {next_action.amount}")
        
        # Verify this action is for the current player (canonical Seat*)
        if self._canon(getattr(next_action,'actor_uid',None)) != self._canon(expected_player_id):
            print(f"⚠️  HAND_MODEL_ENGINE: Player mismatch - expected {expected_player_id}, got {next_action.actor_id}")
            
            # Try to find the correct action for this player in the next 20 actions (increased look-ahead)
            for look_ahead in range(min(20, self.total_actions - self.current_action_index)):
                candidate_action = self.actions_for_replay[self.current_action_index + look_ahead]
                if self._canon(getattr(candidate_action,'actor_uid',None)) == self._canon(expected_player_id):
                    print(f"🔧 HAND_MODEL_ENGINE: Found correct action {look_ahead} steps ahead")
                    self.current_action_index += look_ahead
                    next_action = candidate_action
                    break
            else:
                # No matching action found — this is invalid in canonical mode.
                raise ValueError(f"Canonical mapping failed: expected {expected_player_id}, got {getattr(next_action,'actor_uid',None)}")
        
        # Convert Hand model action to decision engine format
        decision = self._convert_action_to_decision(next_action, player_index)
        
        # Advance to next action
        self.current_action_index += 1
        
        return decision
    
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
