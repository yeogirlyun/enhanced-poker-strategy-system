#!/usr/bin/env python3
"""
Poker State Machine Adapter - Backward Compatibility Layer

This adapter provides backward compatibility with the existing ImprovedPokerStateMachine
interface while using the new FlexiblePokerStateMachine internally.
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass

from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, GameEvent, EventListener
from .types import ActionType, Player, GameState, PokerState


class PokerStateMachineAdapter(EventListener):
    """
    Adapter class that provides backward compatibility with the existing
    ImprovedPokerStateMachine interface.
    """
    
    def __init__(self, num_players: int = 6, strategy_data=None, root_tk=None, test_mode: bool = False):
        """Initialize the adapter with backward compatibility."""
        # Create configuration for the flexible state machine
        config = GameConfig(
            num_players=num_players,
            test_mode=test_mode,
            show_all_cards=False,  # Will be set based on usage
            auto_advance=False
        )
        
        # Create the flexible state machine
        self.flexible_sm = FlexiblePokerStateMachine(config)
        
        # Add this adapter as an event listener
        self.flexible_sm.add_event_listener(self)
        
        # Store legacy parameters for compatibility
        self.num_players = num_players
        self.strategy_data = strategy_data
        self.root_tk = root_tk
        self.test_mode = test_mode
        
        # Legacy attributes for backward compatibility
        self.current_state = self.flexible_sm.current_state
        self.game_state = self.flexible_sm.game_state
        self.action_player_index = self.flexible_sm.action_player_index
        self.players = self.flexible_sm.game_state.players
        
        # Legacy callbacks
        self.on_action_required = None
        self.on_hand_complete = None
        self.on_state_change = None
        self.on_action_executed = None
        self.on_round_complete = None
        self.on_action_player_changed = None
        self.on_log_entry = None
        
        # Session tracking (simplified)
        self.session_state = None
        self.hand_history = []
        self.hand_number = 0
    
    def on_event(self, event: GameEvent):
        """Handle events from the flexible state machine."""
        # Update legacy attributes
        self.current_state = self.flexible_sm.current_state
        self.game_state = self.flexible_sm.game_state
        self.action_player_index = self.flexible_sm.action_player_index
        self.players = self.flexible_sm.game_state.players
        
        # Call legacy callbacks
        if event.event_type == "action_executed" and self.on_action_executed:
            try:
                self.on_action_executed(
                    event.data.get('player_index', 0),
                    event.action.value if event.action else "unknown",
                    event.amount
                )
            except Exception as e:
                print(f"Error in legacy callback: {e}")
        
        elif event.event_type == "state_change" and self.on_state_change:
            try:
                self.on_state_change(event.data.get('new_state'))
            except Exception as e:
                print(f"Error in legacy callback: {e}")
        
        elif event.event_type == "hand_complete" and self.on_hand_complete:
            try:
                self.on_hand_complete(event.data.get('winner_info'))
            except Exception as e:
                print(f"Error in legacy callback: {e}")
        
        elif event.event_type == "round_complete" and self.on_round_complete:
            try:
                self.on_round_complete()
            except Exception as e:
                print(f"Error in legacy callback: {e}")
    
    # Legacy method compatibility
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand (legacy compatibility)."""
        # Configure for simulation mode if existing players provided
        if existing_players:
            self.flexible_sm.config.show_all_cards = True
        
        self.flexible_sm.start_hand(existing_players)
        self.hand_number = self.flexible_sm.hand_number
    
    def execute_action(self, player: Player, action: ActionType, amount: float = 0, _is_fallback: bool = False):
        """Execute a player action (legacy compatibility)."""
        try:
            self.flexible_sm.execute_action(player, action, amount)
        except ValueError as e:
            if _is_fallback:
                raise e
            # Try fallback actions for bots
            if not player.is_human:
                self._try_fallback_actions(player)
    
    def _try_fallback_actions(self, player: Player):
        """Try fallback actions for bot players."""
        call_amount = self.game_state.current_bet - player.current_bet
        
        # Try CALL first
        if call_amount > 0 and call_amount <= player.stack:
            try:
                self.flexible_sm.execute_action(player, ActionType.CALL, call_amount)
                return
            except ValueError:
                pass
        
        # Try CHECK
        if call_amount == 0:
            try:
                self.flexible_sm.execute_action(player, ActionType.CHECK, 0)
                return
            except ValueError:
                pass
        
        # Try FOLD
        try:
            self.flexible_sm.execute_action(player, ActionType.FOLD, 0)
        except ValueError:
            print(f"Critical error: Bot {player.name} cannot make any valid action")
    
    def get_action_player(self) -> Optional[Player]:
        """Get current action player (legacy compatibility)."""
        return self.flexible_sm.get_action_player()
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get game information (legacy compatibility)."""
        return self.flexible_sm.get_game_info()
    
    def get_valid_actions_for_player(self, player: Player) -> Dict[str, Any]:
        """Get valid actions for a player (legacy compatibility)."""
        return self.flexible_sm.get_valid_actions_for_player(player)
    
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate a player action (legacy compatibility)."""
        return self.flexible_sm.validate_action(player, action, amount)
    
    def is_valid_action(self, player: Player, action: ActionType, amount: float = 0) -> bool:
        """Check if action is valid (legacy compatibility)."""
        errors = self.flexible_sm.validate_action(player, action, amount)
        return len(errors) == 0
    
    def get_current_state(self) -> PokerState:
        """Get current state (legacy compatibility)."""
        return self.flexible_sm.current_state
    
    def get_hand_history(self) -> List[Dict[str, Any]]:
        """Get hand history (legacy compatibility)."""
        return self.flexible_sm.hand_history
    
    # Simulation-specific methods
    
    def set_player_cards(self, player_index: int, cards: List[str]):
        """Set cards for a specific player (simulation mode)."""
        self.flexible_sm.set_player_cards(player_index, cards)
    
    def set_board_cards(self, cards: List[str]):
        """Set board cards (simulation mode)."""
        self.flexible_sm.set_board_cards(cards)
    
    def set_player_folded(self, player_index: int, folded: bool):
        """Set folded status for a player (simulation mode)."""
        self.flexible_sm.set_player_folded(player_index, folded)
    
    # Property accessors for backward compatibility
    
    @property
    def state(self) -> str:
        """Get current state as string (legacy compatibility)."""
        return self.flexible_sm.current_state.value
    
    @property
    def players(self) -> List[Player]:
        """Get players (legacy compatibility)."""
        return self.flexible_sm.game_state.players
    
    @players.setter
    def players(self, value: List[Player]):
        """Set players (legacy compatibility)."""
        self.flexible_sm.game_state.players = value
