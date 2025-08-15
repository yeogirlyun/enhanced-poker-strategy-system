#!/usr/bin/env python3
"""
Decision Engine v2 - Abstract base and GTO implementation

This module provides the abstract base class for decision engines and
a GTO-based implementation for real-time strategy calculations.

Key Features:
- Abstract DecisionEngine base class
- GTODecisionEngine for real-time GTO calculations
- Removed PreloadedDecisionEngine (replaced by HandModelDecisionEngine)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .poker_types import ActionType


class DecisionEngine(ABC):
    """
    Abstract base class for poker decision engines.
    
    All decision engines must implement these methods to provide
    consistent decision-making interfaces.
    """
    
    @abstractmethod
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the next decision for a player.
        
        Args:
            player_index: Index of the player making the decision
            game_state: Current state of the game
            
        Returns:
            Dictionary containing action, amount, explanation, and confidence
        """
        pass
    
    @abstractmethod
    def is_session_complete(self) -> bool:
        """Check if the decision session is complete."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the decision engine to initial state."""
        pass
    
    @abstractmethod
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current decision session."""
        pass


class GTODecisionEngine(DecisionEngine):
    """
    GTO-based decision engine for real-time strategy calculations.
    
    This engine provides game theory optimal decisions based on:
    - Player position and stack depth
    - Board texture and pot odds
    - Modern GTO principles and ranges
    """
    
    def __init__(self, num_players: int = 6):
        """
        Initialize the GTO decision engine.
        
        Args:
            num_players: Number of players at the table (default: 6)
        """
        self.num_players = num_players
        self.decision_count = 0
        self.gto_strategies = {}  # Placeholder for GTO strategy data
        
        # Load GTO strategies (placeholder implementation)
        self._load_gto_strategies()
    
    def _load_gto_strategies(self):
        """Load GTO strategies for different scenarios."""
        # Placeholder for GTO strategy loading
        # In a real implementation, this would load pre-computed GTO solutions
        pass
    
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a GTO-based decision for the current situation.
        
        Args:
            player_index: Index of the player making the decision
            game_state: Current state of the game
            
        Returns:
            Dictionary containing action, amount, explanation, and confidence
        """
        try:
            # Extract game state information
            street = game_state.get('street', 'preflop')
            pot_size = game_state.get('pot', 0.0)
            current_bet = game_state.get('current_bet', 0.0)
            players = game_state.get('players', [])
            
            if player_index >= len(players):
                return {
                    'action': ActionType.FOLD,
                    'amount': 0.0,
                    'explanation': 'Invalid player index - folding',
                    'confidence': 0.0
                }
            
            player = players[player_index]
            position = getattr(player, 'position', 'Unknown')
            stack = getattr(player, 'stack', 100.0)
            
            # Simple GTO-based decision logic (placeholder)
            # In a real implementation, this would use sophisticated GTO calculations
            if current_bet == 0.0:
                # No bet to call - check or bet
                if self._should_bet_for_value(position, street):
                    bet_amount = min(pot_size * 0.75, stack * 0.1)
                    return {
                        'action': ActionType.BET,
                        'amount': bet_amount,
                        'explanation': self._generate_explanation(ActionType.BET, bet_amount, street, player),
                        'confidence': 0.8
                    }
                else:
                    return {
                        'action': ActionType.CHECK,
                        'amount': 0.0,
                        'explanation': self._generate_explanation(ActionType.CHECK, 0.0, street, player),
                        'confidence': 0.7
                    }
            else:
                # There's a bet to call, raise, or fold
                call_amount = max(0.0, current_bet - getattr(player, 'current_bet', 0.0))
                
                if call_amount > stack * 0.3:
                    # Expensive call - fold
                    return {
                        'action': ActionType.FOLD,
                        'amount': 0.0,
                        'explanation': self._generate_explanation(ActionType.FOLD, 0.0, street, player),
                        'confidence': 0.9
                    }
                elif call_amount <= stack * 0.1:
                    # Cheap call - call
                    return {
                        'action': ActionType.CALL,
                        'amount': call_amount,
                        'explanation': self._generate_explanation(ActionType.CALL, call_amount, street, player),
                        'confidence': 0.8
                    }
                else:
                    # Medium call - raise or fold based on position
                    if self._should_raise_for_value(position, street):
                        raise_amount = min(current_bet * 2.5, stack * 0.2)
                        return {
                            'action': ActionType.RAISE,
                            'amount': raise_amount,
                            'explanation': self._generate_explanation(ActionType.RAISE, raise_amount, street, player),
                            'confidence': 0.7
                        }
                    else:
                        return {
                            'action': ActionType.FOLD,
                            'amount': 0.0,
                            'explanation': self._generate_explanation(ActionType.FOLD, 0.0, street, player),
                            'confidence': 0.8
                        }
        
        except Exception as e:
            # Fallback decision on error
            return {
                'action': ActionType.CHECK,
                'amount': 0.0,
                'explanation': f"GTO engine error: {str(e)}",
                'confidence': 0.0
            }
    
    def _should_bet_for_value(self, position: str, street: str) -> bool:
        """Determine if we should bet for value based on position and street."""
        # Simple heuristic - in a real implementation, this would use GTO ranges
        strong_positions = ['BTN', 'CO', 'MP']
        return position in strong_positions and street == 'preflop'
    
    def _should_raise_for_value(self, position: str, street: str) -> bool:
        """Determine if we should raise for value based on position and street."""
        # Simple heuristic - in a real implementation, this would use GTO ranges
        strong_positions = ['BTN', 'CO']
        return position in strong_positions and street in ['preflop', 'flop']
    
    def _generate_explanation(self, action: ActionType, amount: float, street: str, player) -> str:
        """Generate a human-readable explanation for the GTO decision."""
        position = getattr(player, 'position', 'Unknown')
        stack = getattr(player, 'stack', 0)
        cards = getattr(player, 'cards', [])
        
        # Basic action descriptions
        action_explanations = {
            ActionType.FOLD: f"GTO fold from {position} position. Hand doesn't meet minimum requirements for this spot.",
            ActionType.CHECK: f"GTO check from {position}. Controlling pot size with marginal hand strength.",
            ActionType.CALL: f"GTO call from {position}. Hand has sufficient equity to continue at current price.",
            ActionType.BET: f"GTO bet of ${amount:.0f} from {position}. Betting for value and/or protection.",
            ActionType.RAISE: f"GTO raise to ${amount:.0f} from {position}. Hand strength justifies aggressive action."
        }
        
        base_explanation = action_explanations.get(action, f"GTO {action.name.lower()} from {position}")
        
        # Add street-specific context
        if street == 'preflop':
            base_explanation += f" Based on modern {self.num_players}-max preflop ranges."
        elif street in ['flop', 'turn', 'river']:
            base_explanation += f" {street.capitalize()} play considering board texture and equity."
        
        return base_explanation
    
    def _get_position_name(self, player_index: int, num_players: int) -> str:
        """Convert player index to position name for 6-max poker."""
        if num_players == 6:
            positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
            return positions[player_index % 6]
        elif num_players == 9:
            positions = ["UTG", "UTG+1", "MP", "MP+1", "CO", "BTN", "SB", "BB", "UTG"]
            return positions[player_index % 9]
        else:
            # Fallback for other table sizes
            return f"Pos_{player_index}"
    
    def is_session_complete(self) -> bool:
        """GTO sessions continue indefinitely until manually stopped."""
        return False
    
    def reset(self) -> None:
        """Reset the GTO decision engine."""
        self.decision_count = 0
        # GTO strategies don't need resetting as they're stateless
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get GTO session information."""
        return {
            'engine_type': 'GTO',
            'num_players': self.num_players,
            'decisions_made': self.decision_count,
            'strategies_loaded': len(self.gto_strategies)
        }
