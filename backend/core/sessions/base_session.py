"""
Base Session Controller

Abstract base class for all poker session types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..pure_poker_state_machine import PurePokerStateMachine, GameConfig
from ..poker_types import Player
from ..hand_model import ActionType


class BasePokerSession(ABC):
    """
    Abstract base class for poker sessions.
    
    Each session type (Practice, GTO, HandsReview, Live) inherits from this
    and implements its own specific logic while using the pure FPSM core.
    """
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.fpsm: Optional[PurePokerStateMachine] = None
        self.session_active = False
        self.session_type = self.__class__.__name__
        
    @abstractmethod
    def initialize_session(self) -> bool:
        """Initialize the session with appropriate providers."""
        pass
    
    @abstractmethod
    def start_hand(self, **kwargs) -> bool:
        """Start a new hand."""
        pass
    
    @abstractmethod
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute a player action."""
        pass
    
    @abstractmethod
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions for a player."""
        pass
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information."""
        if not self.fpsm:
            return {}
        
        game_info = self.fpsm.get_game_info()
        game_info['session_type'] = self.session_type
        game_info['session_active'] = self.session_active
        return game_info
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        if not self.fpsm or not self.fpsm.game_state.players:
            return None
        
        if 0 <= self.fpsm.action_player_index < len(self.fpsm.game_state.players):
            return self.fpsm.game_state.players[self.fpsm.action_player_index]
        
        return None
    
    def is_session_complete(self) -> bool:
        """Check if the session is complete."""
        return not self.session_active
    
    def end_session(self):
        """End the current session."""
        self.session_active = False
        print(f"🏁 {self.session_type}: Session ended")
    
    def get_display_state(self) -> Dict[str, Any]:
        """Get display state for UI."""
        game_info = self.get_game_info()
        
        # Add session-specific display information
        game_info.update({
            'action_player_highlight': [
                i == self.fpsm.action_player_index if self.fpsm else False
                for i in range(len(game_info.get('players', [])))
            ]
        })
        
        return game_info
