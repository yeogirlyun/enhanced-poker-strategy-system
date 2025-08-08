#!/usr/bin/env python3
"""
Flexible Poker State Machine - Modular and Reusable Design

This version is designed to be:
1. Modular - Separate concerns into different components
2. Flexible - Can be used for practice sessions, simulations, and other contexts
3. Reusable - Clean interfaces that work with different UI components
4. Extensible - Easy to add new features and modes
"""

from enum import Enum
from typing import List, Optional, Set, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
import time
import random
import sys
import uuid
from datetime import datetime
import math

# Import shared types
from .types import ActionType, Player, GameState, PokerState

# Import utilities
from .hand_evaluation import EnhancedHandEvaluator
from .position_mapping import EnhancedStrategyIntegration, HandHistoryManager

# Import sound manager
from utils.sound_manager import SoundManager


@dataclass
class GameConfig:
    """Configuration for the poker game."""
    num_players: int = 6
    big_blind: float = 1.0
    small_blind: float = 0.5
    starting_stack: float = 100.0
    test_mode: bool = False
    show_all_cards: bool = False  # For simulation mode
    auto_advance: bool = False  # For simulation mode


@dataclass
class GameEvent:
    """Represents a game event that can be handled by listeners."""
    event_type: str
    timestamp: float
    player_name: Optional[str] = None
    action: Optional[ActionType] = None
    amount: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)


class EventListener:
    """Base class for event listeners."""
    
    def on_event(self, event: GameEvent):
        """Handle a game event."""
        pass


class FlexiblePokerStateMachine:
    """
    Flexible and modular poker state machine.
    
    This state machine can be used for:
    - Practice sessions (interactive play)
    - Simulations (replaying hands)
    - Analysis (studying hands)
    - Testing (automated scenarios)
    """
    
    def __init__(self, config: GameConfig = None):
        """Initialize the flexible poker state machine."""
        self.config = config or GameConfig()
        
        # Core game state
        self.current_state = PokerState.START_HAND
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[]
        )
        
        # Player management
        self.action_player_index = 0
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 0
        
        # Event system
        self.event_listeners: List[EventListener] = []
        self.event_history: List[GameEvent] = []
        
        # Hand tracking
        self.hand_number = 0
        self.hand_history: List[Dict[str, Any]] = []
        
        # Utilities
        self.hand_evaluator = EnhancedHandEvaluator()
        self.sound_manager = SoundManager(test_mode=self.config.test_mode)
        
        # Strategy integration (optional)
        self.strategy_integration = None
        self.hand_history_manager = HandHistoryManager()
        
        # Callbacks (for backward compatibility)
        self.on_action_required: Optional[Callable] = None
        self.on_hand_complete: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_action_executed: Optional[Callable] = None
        self.on_round_complete: Optional[Callable] = None
        
        # Initialize players
        self._initialize_players()
    
    def _initialize_players(self):
        """Initialize players for the game."""
        self.game_state.players = []
        for i in range(self.config.num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=self.config.starting_stack,
                position="",
                is_human=False,
                is_active=True,
                cards=[]
            )
            self.game_state.players.append(player)
        
        # Assign positions
        self.assign_positions()
    
    def assign_positions(self):
        """Assign positions to players."""
        positions = self._get_position_names()
        for i, player in enumerate(self.game_state.players):
            player.position = positions[i]
    
    def _get_position_names(self) -> List[str]:
        """Get position names for the current number of players."""
        if self.config.num_players == 2:
            return ["BB", "SB"]
        elif self.config.num_players == 3:
            return ["BB", "SB", "BTN"]
        elif self.config.num_players == 4:
            return ["BB", "SB", "BTN", "UTG"]
        elif self.config.num_players == 5:
            return ["BB", "SB", "BTN", "UTG", "MP"]
        else:  # 6+ players
            return ["BB", "SB", "BTN", "UTG", "MP", "CO"]
    
    def add_event_listener(self, listener: EventListener):
        """Add an event listener."""
        self.event_listeners.append(listener)
    
    def remove_event_listener(self, listener: EventListener):
        """Remove an event listener."""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
    
    def _emit_event(self, event: GameEvent):
        """Emit an event to all listeners."""
        self.event_history.append(event)
        
        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                print(f"Error in event listener: {e}")
        
        # Call legacy callbacks for backward compatibility
        self._call_legacy_callbacks(event)
    
    def _call_legacy_callbacks(self, event: GameEvent):
        """Call legacy callbacks for backward compatibility."""
        if event.event_type == "action_executed" and self.on_action_executed:
            try:
                self.on_action_executed(event.data.get('player_index', 0), 
                                      event.action.value if event.action else "unknown", 
                                      event.amount)
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
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand."""
        self.hand_number += 1
        self.current_state = PokerState.START_HAND
        
        # Use existing players if provided (for simulation mode)
        if existing_players:
            self.game_state.players = existing_players.copy()
            # Ensure all players have the required attributes
            for player in self.game_state.players:
                if not hasattr(player, 'is_human'):
                    player.is_human = self.config.show_all_cards
                if not hasattr(player, 'has_folded'):
                    player.has_folded = False
                if not hasattr(player, 'is_active'):
                    player.is_active = True
        else:
            # Reset players for new hand
            for player in self.game_state.players:
                player.cards = []
                player.current_bet = 0.0
                player.has_folded = False
                player.is_active = True
                player.is_all_in = False
                player.total_invested = 0.0
        
        # Reset game state
        self.game_state.board = []
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.street = "preflop"
        self.game_state.deck = self.create_deck()
        
        # Assign positions
        self.assign_positions()
        
        # Emit event
        self._emit_event(GameEvent(
            event_type="hand_started",
            timestamp=time.time(),
            data={"hand_number": self.hand_number}
        ))
        
        # Transition to preflop betting
        self.transition_to(PokerState.PREFLOP_BETTING)
    
    def create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['h', 'd', 'c', 's']
        deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck
    
    def deal_card(self) -> str:
        """Deal a card from the deck."""
        if not self.game_state.deck:
            return None
        return self.game_state.deck.pop()
    
    def transition_to(self, new_state: PokerState):
        """Transition to a new state."""
        old_state = self.current_state
        self.current_state = new_state
        
        # Emit state change event
        self._emit_event(GameEvent(
            event_type="state_change",
            timestamp=time.time(),
            data={"old_state": old_state.value, "new_state": new_state.value}
        ))
        
        # Handle state-specific logic
        if new_state == PokerState.PREFLOP_BETTING:
            self._handle_preflop_start()
        elif new_state == PokerState.DEAL_FLOP:
            self._handle_deal_flop()
        elif new_state == PokerState.DEAL_TURN:
            self._handle_deal_turn()
        elif new_state == PokerState.DEAL_RIVER:
            self._handle_deal_river()
        elif new_state == PokerState.SHOWDOWN:
            self._handle_showdown()
        elif new_state == PokerState.END_HAND:
            self._handle_end_hand()
    
    def _handle_preflop_start(self):
        """Handle the start of preflop betting."""
        # Deal hole cards
        for player in self.game_state.players:
            if not player.cards:  # Only deal if cards not already set (for simulation)
                player.cards = [self.deal_card(), self.deal_card()]
        
        # Set blinds
        self._set_blinds()
        
        # Set action to first player after big blind
        self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
        
        # Emit dealing event
        self._emit_event(GameEvent(
            event_type="cards_dealt",
            timestamp=time.time(),
            data={"street": "preflop"}
        ))
    
    def _set_blinds(self):
        """Set the small and big blinds."""
        # Small blind
        sb_player = self.game_state.players[self.small_blind_position]
        sb_amount = min(self.config.small_blind, sb_player.stack)
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        self.game_state.pot += sb_amount
        
        # Big blind
        bb_player = self.game_state.players[self.big_blind_position]
        bb_amount = min(self.config.big_blind, bb_player.stack)
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        self.game_state.pot += bb_amount
        self.game_state.current_bet = bb_amount
    
    def _handle_deal_flop(self):
        """Handle dealing the flop."""
        self.game_state.board = [self.deal_card(), self.deal_card(), self.deal_card()]
        self.game_state.street = "flop"
        self.game_state.current_bet = 0.0
        
        # Reset player bets for new street
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Set action to first active player after button
        self.action_player_index = (self.dealer_position + 1) % self.config.num_players
        
        self._emit_event(GameEvent(
            event_type="flop_dealt",
            timestamp=time.time(),
            data={"board": self.game_state.board.copy()}
        ))
    
    def _handle_deal_turn(self):
        """Handle dealing the turn."""
        self.game_state.board.append(self.deal_card())
        self.game_state.street = "turn"
        self.game_state.current_bet = 0.0
        
        # Reset player bets for new street
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Set action to first active player after button
        self.action_player_index = (self.dealer_position + 1) % self.config.num_players
        
        self._emit_event(GameEvent(
            event_type="turn_dealt",
            timestamp=time.time(),
            data={"board": self.game_state.board.copy()}
        ))
    
    def _handle_deal_river(self):
        """Handle dealing the river."""
        self.game_state.board.append(self.deal_card())
        self.game_state.street = "river"
        self.game_state.current_bet = 0.0
        
        # Reset player bets for new street
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Set action to first active player after button
        self.action_player_index = (self.dealer_position + 1) % self.config.num_players
        
        self._emit_event(GameEvent(
            event_type="river_dealt",
            timestamp=time.time(),
            data={"board": self.game_state.board.copy()}
        ))
    
    def _handle_showdown(self):
        """Handle showdown."""
        # Determine winners
        active_players = [p for p in self.game_state.players if not p.has_folded]
        winners = self.determine_winners(active_players)
        
        # Emit showdown event
        self._emit_event(GameEvent(
            event_type="showdown",
            timestamp=time.time(),
            data={"winners": [w.name for w in winners], "board": self.game_state.board.copy()}
        ))
    
    def _handle_end_hand(self):
        """Handle end of hand."""
        self._emit_event(GameEvent(
            event_type="hand_complete",
            timestamp=time.time(),
            data={"hand_number": self.hand_number}
        ))
    
    def execute_action(self, player: Player, action: ActionType, amount: float = 0):
        """Execute a player action."""
        # Validate action
        errors = self.validate_action(player, action, amount)
        if errors:
            raise ValueError(f"Invalid action: {'; '.join(errors)}")
        
        # Execute the action
        old_pot = self.game_state.pot
        old_stack = player.stack
        
        if action == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
        
        elif action == ActionType.CHECK:
            # Check is only valid if no bet to call
            if self.game_state.current_bet > player.current_bet:
                raise ValueError("Cannot check when there is a bet to call")
        
        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount > 0:
                actual_call = min(call_amount, player.stack)
                player.stack -= actual_call
                player.current_bet += actual_call
                self.game_state.pot += actual_call
        
        elif action == ActionType.BET:
            if amount <= 0:
                raise ValueError("Bet amount must be positive")
            if amount > player.stack:
                raise ValueError("Cannot bet more than stack")
            player.stack -= amount
            player.current_bet += amount
            self.game_state.pot += amount
            self.game_state.current_bet = player.current_bet
        
        elif action == ActionType.RAISE:
            if amount <= self.game_state.current_bet:
                raise ValueError("Raise must be more than current bet")
            if amount > player.stack:
                raise ValueError("Cannot raise more than stack")
            player.stack -= amount
            player.current_bet += amount
            self.game_state.pot += amount
            self.game_state.current_bet = player.current_bet
        
        # Emit action event
        self._emit_event(GameEvent(
            event_type="action_executed",
            timestamp=time.time(),
            player_name=player.name,
            action=action,
            amount=amount,
            data={
                "player_index": self.game_state.players.index(player),
                "old_pot": old_pot,
                "new_pot": self.game_state.pot,
                "old_stack": old_stack,
                "new_stack": player.stack
            }
        ))
        
        # Advance to next player
        self.advance_to_next_player()
        
        # Check if round is complete
        if self.is_round_complete():
            self._handle_round_complete()
    
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate a player action."""
        errors = []
        
        # Check if player is active
        if player.has_folded:
            errors.append("Player has already folded")
        
        # Check if it's player's turn
        if self.game_state.players[self.action_player_index] != player:
            errors.append("Not player's turn")
        
        # Action-specific validation
        if action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount > player.stack:
                errors.append("Cannot call: insufficient stack")
        
        elif action == ActionType.BET:
            if amount <= 0:
                errors.append("Bet amount must be positive")
            if amount > player.stack:
                errors.append("Cannot bet more than stack")
            if amount < self.game_state.current_bet:
                errors.append("Bet must be at least current bet")
        
        elif action == ActionType.RAISE:
            if amount <= self.game_state.current_bet:
                errors.append("Raise must be more than current bet")
            if amount > player.stack:
                errors.append("Cannot raise more than stack")
        
        return errors
    
    def advance_to_next_player(self):
        """Advance to the next active player."""
        start_index = self.action_player_index
        
        while True:
            self.action_player_index = (self.action_player_index + 1) % self.config.num_players
            
            # If we've gone around the table, we're done
            if self.action_player_index == start_index:
                break
            
            # Check if this player is active
            player = self.game_state.players[self.action_player_index]
            if not player.has_folded and player.is_active:
                break
    
    def is_round_complete(self) -> bool:
        """Check if the current betting round is complete."""
        active_players = [p for p in self.game_state.players if not p.has_folded]
        
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have acted and bets are equal
        for player in active_players:
            if player.current_bet != self.game_state.current_bet:
                return False
        
        return True
    
    def _handle_round_complete(self):
        """Handle completion of a betting round."""
        # Emit round complete event
        self._emit_event(GameEvent(
            event_type="round_complete",
            timestamp=time.time(),
            data={"street": self.game_state.street}
        ))
        
        # Transition to next state
        if self.game_state.street == "preflop":
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.game_state.street == "flop":
            self.transition_to(PokerState.DEAL_TURN)
        elif self.game_state.street == "turn":
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.game_state.street == "river":
            self.transition_to(PokerState.SHOWDOWN)
    
    def determine_winners(self, players: List[Player]) -> List[Player]:
        """Determine the winners among the given players."""
        if not players:
            return []
        
        if len(players) == 1:
            return players
        
        # Evaluate hands
        player_hands = []
        for player in players:
            if len(player.cards) == 2:
                hand_eval = self.hand_evaluator.evaluate_hand(player.cards, self.game_state.board)
                # Extract the hand rank value from the evaluation result
                if isinstance(hand_eval, dict) and 'hand_rank' in hand_eval:
                    hand_rank = hand_eval['hand_rank']
                    # Convert HandRank enum to integer value for comparison
                    rank_value = hand_rank.value if hasattr(hand_rank, 'value') else hand_rank
                else:
                    rank_value = hand_eval if isinstance(hand_eval, (int, float)) else 0
                player_hands.append((player, rank_value))
        
        # Sort by hand rank (best first)
        player_hands.sort(key=lambda x: x[1], reverse=True)
        
        # Find winners (players with the same best hand rank)
        best_rank = player_hands[0][1]
        winners = [player for player, rank in player_hands if rank == best_rank]
        
        return winners
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        if 0 <= self.action_player_index < len(self.game_state.players):
            return self.game_state.players[self.action_player_index]
        return None
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get comprehensive game information."""
        action_player = self.get_action_player()
        
        return {
            "state": self.current_state.value,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board.copy(),
            "players": [
                {
                    "name": p.name,
                    "position": p.position,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "has_folded": p.has_folded,
                    "is_human": p.is_human,
                    "cards": p.cards if (p.is_human or self.config.show_all_cards or 
                                       self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND]) 
                           else ["**", "**"],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
            "street": self.game_state.street,
            "hand_number": self.hand_number
        }
    
    def get_valid_actions_for_player(self, player: Player) -> Dict[str, Any]:
        """Get valid actions for a player."""
        if not player or player.has_folded:
            return {}
        
        call_amount = self.game_state.current_bet - player.current_bet
        min_bet = max(self.game_state.current_bet, self.config.big_blind)
        
        valid_actions = {
            "fold": True,
            "check": call_amount == 0,
            "call": call_amount > 0 and call_amount <= player.stack,
            "bet": player.stack > 0,
            "raise": player.stack > min_bet,
            "call_amount": call_amount,
            "min_bet": min_bet,
            "max_bet": player.stack
        }
        
        return valid_actions
    
    def set_player_cards(self, player_index: int, cards: List[str]):
        """Set cards for a specific player (for simulation mode)."""
        if 0 <= player_index < len(self.game_state.players):
            self.game_state.players[player_index].cards = cards.copy()
    
    def set_board_cards(self, cards: List[str]):
        """Set board cards (for simulation mode)."""
        self.game_state.board = cards.copy()
    
    def set_player_folded(self, player_index: int, folded: bool):
        """Set folded status for a player (for simulation mode)."""
        if 0 <= player_index < len(self.game_state.players):
            self.game_state.players[player_index].has_folded = folded
            self.game_state.players[player_index].is_active = not folded
