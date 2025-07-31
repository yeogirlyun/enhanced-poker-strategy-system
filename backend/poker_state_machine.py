#!/usr/bin/env python3
"""
Texas Hold'em Poker State Machine

A proper state machine implementation for Texas Hold'em poker game flow.
This replaces the ad-hoc logic with a standardized, predictable approach.
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time
import threading


class PokerState(Enum):
    """Poker game states following standard Texas Hold'em flow."""
    START_HAND = "start_hand"
    PREFLOP_BETTING = "preflop_betting"
    DEAL_FLOP = "deal_flop"
    FLOP_BETTING = "flop_betting"
    DEAL_TURN = "deal_turn"
    TURN_BETTING = "turn_betting"
    DEAL_RIVER = "deal_river"
    RIVER_BETTING = "river_betting"
    SHOWDOWN = "showdown"
    END_HAND = "end_hand"


class ActionType(Enum):
    """Valid poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"


@dataclass
class Player:
    """Player data structure."""
    name: str
    stack: float
    position: str
    is_human: bool
    is_active: bool
    cards: List[str]
    current_bet: float = 0.0


@dataclass
class GameState:
    """Game state data structure."""
    players: List[Player]
    board: List[str]
    pot: float
    current_bet: float
    street: str


class PokerStateMachine:
    """Proper Texas Hold'em state machine implementation."""
    
    # Valid state transitions
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
        PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING],
        PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
        PokerState.DEAL_TURN: [PokerState.TURN_BETTING],
        PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
        PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING],
        PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }
    
    def __init__(self, num_players: int = 6):
        self.current_state = PokerState.START_HAND
        self.game_state = None
        self.action_player_index = 0
        self.num_players = num_players
        
        # Position tracking
        self.dealer_position = 0
        self.small_blind_position = 1
        self.big_blind_position = 2
        
        # Callbacks for UI updates
        self.on_state_change = None
        self.on_action_required = None
        self.on_round_complete = None
        self.on_hand_complete = None
        
        # Logging
        self.action_log = []
    
    def log_action(self, message: str):
        """Log an action with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.action_log.append(log_entry)
        print(log_entry)
    
    def transition_to(self, new_state: PokerState):
        """Transition to a new state with validation."""
        if new_state in self.STATE_TRANSITIONS[self.current_state]:
            old_state = self.current_state
            self.current_state = new_state
            self.log_action(f"STATE TRANSITION: {old_state.value} → {new_state.value}")
            self.handle_state_entry()
        else:
            raise ValueError(f"Invalid state transition: {self.current_state.value} → {new_state.value}")
    
    def handle_state_entry(self):
        """Handle specific logic for each state entry."""
        if self.current_state == PokerState.START_HAND:
            self.handle_start_hand()
        elif self.current_state == PokerState.PREFLOP_BETTING:
            self.handle_preflop_betting()
        elif self.current_state == PokerState.DEAL_FLOP:
            self.handle_deal_flop()
        elif self.current_state == PokerState.FLOP_BETTING:
            self.handle_flop_betting()
        elif self.current_state == PokerState.DEAL_TURN:
            self.handle_deal_turn()
        elif self.current_state == PokerState.TURN_BETTING:
            self.handle_turn_betting()
        elif self.current_state == PokerState.DEAL_RIVER:
            self.handle_deal_river()
        elif self.current_state == PokerState.RIVER_BETTING:
            self.handle_river_betting()
        elif self.current_state == PokerState.SHOWDOWN:
            self.handle_showdown()
        elif self.current_state == PokerState.END_HAND:
            self.handle_end_hand()
    
    def handle_start_hand(self):
        """Initialize a new hand."""
        self.log_action("Starting new hand")
        
        # Create players
        players = []
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(self.num_players):
            is_human = i == 0
            position = positions[i % len(positions)]
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position=position,
                is_human=is_human,
                is_active=True,
                cards=[],
                current_bet=0.0
            )
            players.append(player)
        
        # Post blinds
        players[self.small_blind_position].stack -= 0.5
        players[self.small_blind_position].current_bet = 0.5
        players[self.big_blind_position].stack -= 1.0
        players[self.big_blind_position].current_bet = 1.0
        
        # Create game state
        self.game_state = GameState(
            players=players,
            board=[],
            pot=1.5,
            current_bet=1.0,
            street="preflop"
        )
        
        # Set action player (UTG)
        self.action_player_index = (self.big_blind_position + 1) % len(players)
        
        # Transition to preflop betting
        self.transition_to(PokerState.PREFLOP_BETTING)
    
    def handle_preflop_betting(self):
        """Handle preflop betting round."""
        self.log_action("Preflop betting round")
        self.game_state.current_bet = 1.0  # BB amount
        self.game_state.street = "preflop"
        
        # Check if round is already complete (all players called BB)
        if self.is_round_complete():
            self.transition_to(PokerState.DEAL_FLOP)
        else:
            self.handle_current_player_action()
    
    def handle_deal_flop(self):
        """Deal the flop."""
        self.log_action("Dealing flop")
        
        # Reset betting
        self.game_state.current_bet = 0.0
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Deal 3 community cards (simplified)
        self.game_state.board = ["5h", "7c", "9h"]  # Example cards
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % len(self.game_state.players)
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % len(self.game_state.players)
        
        self.transition_to(PokerState.FLOP_BETTING)
    
    def handle_flop_betting(self):
        """Handle flop betting round."""
        self.log_action("Flop betting round")
        self.game_state.street = "flop"
        
        if self.is_round_complete():
            self.transition_to(PokerState.DEAL_TURN)
        else:
            self.handle_current_player_action()
    
    def handle_deal_turn(self):
        """Deal the turn."""
        self.log_action("Dealing turn")
        
        # Reset betting
        self.game_state.current_bet = 0.0
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Deal 1 more community card
        self.game_state.board.append("Ts")  # Example card
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % len(self.game_state.players)
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % len(self.game_state.players)
        
        self.transition_to(PokerState.TURN_BETTING)
    
    def handle_turn_betting(self):
        """Handle turn betting round."""
        self.log_action("Turn betting round")
        self.game_state.street = "turn"
        
        if self.is_round_complete():
            self.transition_to(PokerState.DEAL_RIVER)
        else:
            self.handle_current_player_action()
    
    def handle_deal_river(self):
        """Deal the river."""
        self.log_action("Dealing river")
        
        # Reset betting
        self.game_state.current_bet = 0.0
        for player in self.game_state.players:
            player.current_bet = 0.0
        
        # Deal 1 more community card
        self.game_state.board.append("3c")  # Example card
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % len(self.game_state.players)
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % len(self.game_state.players)
        
        self.transition_to(PokerState.RIVER_BETTING)
    
    def handle_river_betting(self):
        """Handle river betting round."""
        self.log_action("River betting round")
        self.game_state.street = "river"
        
        if self.is_round_complete():
            self.transition_to(PokerState.SHOWDOWN)
        else:
            self.handle_current_player_action()
    
    def handle_showdown(self):
        """Handle showdown."""
        self.log_action("Showdown")
        
        # Determine winner (simplified)
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.game_state.pot
            self.log_action(f"{winner.name} wins ${self.game_state.pot:.2f}")
        else:
            # Simplified winner determination
            winner = active_players[0]  # First active player wins
            winner.stack += self.game_state.pot
            self.log_action(f"{winner.name} wins ${self.game_state.pot:.2f}")
        
        self.transition_to(PokerState.END_HAND)
    
    def handle_end_hand(self):
        """Handle hand completion."""
        self.log_action("Hand complete")
        if self.on_hand_complete:
            self.on_hand_complete()
    
    def handle_current_player_action(self):
        """Handle the current player's action."""
        current_player = self.game_state.players[self.action_player_index]
        
        if current_player.is_human:
            # Human player's turn
            self.log_action(f"Human turn: {current_player.name}")
            if self.on_action_required:
                self.on_action_required(current_player)
        else:
            # Bot player's turn
            self.log_action(f"Bot turn: {current_player.name}")
            self.execute_bot_action(current_player)
    
    def execute_bot_action(self, player: Player):
        """Execute a bot action."""
        # Simplified bot logic
        if self.game_state.current_bet == 0:
            # No bet to call - check or bet
            action = ActionType.CHECK if player.stack < 5 else ActionType.BET
            amount = 2 if action == ActionType.BET else 0
        else:
            # There's a bet to call
            action = ActionType.CALL if player.stack >= self.game_state.current_bet else ActionType.FOLD
            amount = self.game_state.current_bet if action == ActionType.CALL else 0
        
        self.execute_action(player, action, amount)
    
    def execute_action(self, player: Player, action: ActionType, amount: float = 0):
        """Execute a player action."""
        self.log_action(f"{player.name}: {action.value.upper()} ${amount:.2f}")
        
        if action == ActionType.FOLD:
            player.is_active = False
            player.current_bet = 0
        elif action in [ActionType.CALL, ActionType.BET, ActionType.RAISE]:
            call_amount = amount if action == ActionType.BET else self.game_state.current_bet
            player.stack -= call_amount
            self.game_state.pot += call_amount
            self.game_state.current_bet = call_amount
            player.current_bet = call_amount
        elif action == ActionType.CHECK:
            player.current_bet = 0
        
        # Move to next player
        self.advance_to_next_player()
        
        # Check if round is complete
        if self.is_round_complete():
            self.handle_round_complete()
        else:
            # Continue with next player
            self.handle_current_player_action()
    
    def advance_to_next_player(self):
        """Move to the next active player."""
        num_players = len(self.game_state.players)
        self.action_player_index = (self.action_player_index + 1) % num_players
        
        # Skip folded players
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % num_players
    
    def is_round_complete(self):
        """Check if the current betting round is complete."""
        active_players = [p for p in self.game_state.players if p.is_active]
        
        # If only one player remains, round is complete
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have equal bets
        target_bet = self.game_state.current_bet
        for player in active_players:
            if player.current_bet != target_bet:
                return False
        
        return True
    
    def handle_round_complete(self):
        """Handle round completion."""
        self.log_action("Round complete")
        
        if self.current_state == PokerState.PREFLOP_BETTING:
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.current_state == PokerState.FLOP_BETTING:
            self.transition_to(PokerState.DEAL_TURN)
        elif self.current_state == PokerState.TURN_BETTING:
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.current_state == PokerState.RIVER_BETTING:
            self.transition_to(PokerState.SHOWDOWN)
    
    def is_valid_action(self, player: Player, action: ActionType, amount: float = 0) -> bool:
        """Check if an action is valid for the current state."""
        if self.current_state == PokerState.PREFLOP_BETTING:
            return action in [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
        elif self.current_state in [PokerState.FLOP_BETTING, PokerState.TURN_BETTING, PokerState.RIVER_BETTING]:
            if self.game_state.current_bet == 0:
                return action in [ActionType.CHECK, ActionType.BET]
            else:
                return action in [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
        return False
    
    def start_hand(self):
        """Start a new hand."""
        self.current_state = PokerState.START_HAND
        self.handle_state_entry()
    
    def get_current_state(self) -> PokerState:
        """Get the current state."""
        return self.current_state
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        if self.game_state and 0 <= self.action_player_index < len(self.game_state.players):
            return self.game_state.players[self.action_player_index]
        return None


# Example usage
if __name__ == "__main__":
    # Create state machine
    poker_machine = PokerStateMachine(num_players=6)
    
    # Start a hand
    poker_machine.start_hand()
    
    # Simulate some actions
    current_player = poker_machine.get_action_player()
    if current_player:
        poker_machine.execute_action(current_player, ActionType.CALL, 1.0) 