"""
GTO Decision Engine Adapter for PPSM Integration

This adapter bridges the GTODecisionEngine to the DecisionEngineProtocol
interface that PPSM expects, enabling GTO-based hand generation.
"""

from typing import Optional, Tuple
from .pure_poker_state_machine import DecisionEngineProtocol
from .hand_model import ActionType
from .poker_types import GameState
from .decision_engine_v2 import GTODecisionEngine


class GTODecisionEngineAdapter(DecisionEngineProtocol):
    """
    Adapter that wraps GTODecisionEngine to implement DecisionEngineProtocol.
    
    This bridges the interface differences:
    - GTODecisionEngine: get_decision(player_index, game_state) -> Dict[str, Any]
    - DecisionEngineProtocol: get_decision(player_name, game_state) -> tuple(ActionType, amount)
    """
    
    def __init__(self, num_players: int = 6):
        """Initialize the GTO adapter with specified number of players."""
        self.gto_engine = GTODecisionEngine(num_players)
        self.num_players = num_players
        self.current_hand = 0
        
    def get_decision(self, player_name: str, game_state: GameState) -> Optional[Tuple[ActionType, Optional[float]]]:
        """
        Get GTO decision for a player, converting to PPSM format.
        
        Args:
            player_name: Name/UID of the player making the decision
            game_state: Current game state from PPSM
            
        Returns:
            Tuple of (ActionType, amount) or None if no decision available
        """
        try:
            # Convert game_state to dict format that GTODecisionEngine expects
            game_state_dict = self._convert_game_state_to_dict(game_state)
            
            # Find player index from player_name
            player_index = self._find_player_index(player_name, game_state)
            if player_index is None:
                print(f"⚠️ GTO Adapter: Player {player_name} not found in game state")
                return None
            
            # Get decision from GTO engine
            decision = self.gto_engine.get_decision(player_index, game_state_dict)
            if not decision:
                print(f"⚠️ GTO Adapter: No decision available for player {player_name}")
                return None
            
            # Convert GTO decision format to PPSM format
            action_type = self._convert_action_type(decision.get('action'))
            amount = decision.get('amount', 0.0)
            
            print(f"🎯 GTO Adapter: {player_name} -> {action_type} {amount if amount else ''}")
            return (action_type, amount if amount > 0 else None)
            
        except Exception as e:
            print(f"❌ GTO Adapter error: {e}")
            return None
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if GTO engine has a decision for the specified player."""
        # GTO engine always has decisions available
        return True
    
    def reset_for_new_hand(self) -> None:
        """Reset GTO engine state for a new hand."""
        self.gto_engine.reset()
        self.current_hand += 1
        print(f"🔄 GTO Adapter: Reset for hand {self.current_hand}")
    
    def _convert_game_state_to_dict(self, game_state: GameState) -> dict:
        """Convert PPSM GameState to dict format for GTODecisionEngine."""
        try:
            # Extract relevant information from GameState
            return {
                'street': getattr(game_state, 'street', 'preflop'),
                'pot': getattr(game_state, 'pot', 0.0),
                'current_bet': getattr(game_state, 'current_bet', 0.0),
                'players': getattr(game_state, 'players', []),
                'board_cards': getattr(game_state, 'board_cards', []),
                'dealer_position': getattr(game_state, 'dealer_position', 0),
                'small_blind': getattr(game_state, 'small_blind', 1.0),
                'big_blind': getattr(game_state, 'big_blind', 2.0)
            }
        except Exception as e:
            print(f"⚠️ GTO Adapter: Error converting game state: {e}")
            return {}
    
    def _find_player_index(self, player_name: str, game_state: GameState) -> Optional[int]:
        """Find player index by name/UID in the game state."""
        try:
            players = getattr(game_state, 'players', [])
            for i, player in enumerate(players):
                if (hasattr(player, 'name') and player.name == player_name) or \
                   (hasattr(player, 'player_uid') and player.player_uid == player_name):
                    return i
            return None
        except Exception as e:
            print(f"⚠️ GTO Adapter: Error finding player index: {e}")
            return None
    
    def _convert_action_type(self, action) -> ActionType:
        """Convert action to PPSM ActionType enum."""
        try:
            # Handle both string and ActionType inputs
            if isinstance(action, ActionType):
                return action
            
            action_str = str(action or "").upper()
            if action_str == "FOLD":
                return ActionType.FOLD
            elif action_str == "CHECK":
                return ActionType.CHECK
            elif action_str == "CALL":
                return ActionType.CALL
            elif action_str == "BET":
                return ActionType.BET
            elif action_str == "RAISE":
                return ActionType.RAISE
            elif action_str == "ALL_IN":
                return ActionType.ALL_IN
            else:
                print(f"⚠️ GTO Adapter: Unknown action type: {action_str}, defaulting to CHECK")
                return ActionType.CHECK
        except Exception as e:
            print(f"⚠️ GTO Adapter: Error converting action type: {e}")
            return ActionType.CHECK


def create_gto_decision_engine(num_players: int = 6) -> GTODecisionEngineAdapter:
    """Factory function to create a GTO decision engine adapter."""
    return GTODecisionEngineAdapter(num_players)
