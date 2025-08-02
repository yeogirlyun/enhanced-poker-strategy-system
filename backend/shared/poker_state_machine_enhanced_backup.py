#!/usr/bin/env python3
"""
Reliable Poker State Machine

A simple, reliable implementation that uses Treys for hand evaluation
and focuses on core functionality without complex edge cases.
"""

from enum import Enum
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass, field
import time
import random
import sys
import os

# Try to import Treys for hand evaluation
try:
    import treys
    TREYS_AVAILABLE = True
except ImportError:
    TREYS_AVAILABLE = False
    print("Warning: Treys not available, using basic hand evaluation")


class PokerState(Enum):
    """Poker game states."""
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
    has_acted_this_round: bool = False
    is_all_in: bool = False
    total_invested: float = 0.0


@dataclass
class GameState:
    """Game state."""
    players: List[Player]
    board: List[str]
    pot: float
    current_bet: float
    street: str
    players_acted: Set[int] = field(default_factory=set)
    round_complete: bool = False
    deck: List[str] = field(default_factory=list)
    min_raise: float = 1.0
    big_blind: float = 1.0


class ReliablePokerStateMachine:
    """Simple, reliable poker state machine."""
    
    def __init__(self, num_players: int = 6, strategy_data=None, root_tk=None):
        """Initialize the state machine."""
        self.num_players = num_players
        self.strategy_data = strategy_data
        self.root_tk = root_tk
        
        # Game state
        self.current_state = PokerState.END_HAND  # Start in END_HAND so we can transition to START_HAND
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[]
        )
        
        # Callbacks
        self.on_state_change = None
        self.on_action_required = None
        self.on_hand_complete = None
        self.on_log_entry = None
        
        # Hand history
        self.hand_history = []
        
        # Sound effects
        self.sfx = None
        
        # Initialize players
        self._initialize_players()
        
        # Dealer and blind positions
        self.dealer_position = 0
        self.small_blind_position = 1
        self.big_blind_position = 2
        
        # Action tracking
        self.action_player_index = 0
        
        # Logging
        self._log_enabled = True
    
    def _initialize_players(self):
        """Initialize players with proper positions."""
        positions = self._get_position_names()
        
        for i in range(self.num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position=positions[i] if i < len(positions) else f"P{i+1}",
                is_human=(i == 0),
                is_active=True,
                cards=[],
                current_bet=0.0,
                has_acted_this_round=False,
                is_all_in=False,
                total_invested=0.0
            )
            self.game_state.players.append(player)
    
    def _get_position_names(self) -> List[str]:
        """Get position names based on number of players."""
        if self.num_players == 2:
            return ["BTN/SB", "BB"]
        elif self.num_players == 3:
            return ["BTN", "SB", "BB"]
        elif self.num_players == 6:
            return ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        elif self.num_players == 9:
            return ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "MP+1", "CO", "LJ"]
        else:
            positions = ["BTN", "SB", "BB"]
            for i in range(3, self.num_players):
                positions.append(f"P{i+1}")
            return positions
    
    def _log_action(self, message: str):
        """Log an action message."""
        if self._log_enabled:
            timestamp = time.strftime("[%H:%M:%S]")
            log_entry = f"{timestamp} {message}"
            print(log_entry)
            if self.on_log_entry:
                self.on_log_entry(log_entry)
    
    def transition_to(self, new_state: PokerState):
        """Transition to a new state."""
        old_state = self.current_state
        self.current_state = new_state
        self._log_action(f"STATE TRANSITION: {old_state.value} → {new_state.value}")
        if self.on_state_change:
            self.on_state_change(new_state)
        self.handle_state_entry()
    
    def handle_state_entry(self):
        """Handle state entry logic."""
        handlers = {
            PokerState.START_HAND: self.handle_start_hand,
            PokerState.PREFLOP_BETTING: self.handle_preflop_betting,
            PokerState.DEAL_FLOP: self.handle_deal_flop,
            PokerState.FLOP_BETTING: self.handle_flop_betting,
            PokerState.DEAL_TURN: self.handle_deal_turn,
            PokerState.TURN_BETTING: self.handle_turn_betting,
            PokerState.DEAL_RIVER: self.handle_deal_river,
            PokerState.RIVER_BETTING: self.handle_river_betting,
            PokerState.SHOWDOWN: self.handle_showdown,
            PokerState.END_HAND: self.handle_end_hand,
        }
        
        handler = handlers.get(self.current_state)
        if handler:
            handler()
    
    def create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        suits = ["h", "d", "c", "s"]
        deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck
    
    def deal_card(self) -> str:
        """Deal a single card from the deck."""
        if not self.game_state.deck:
            raise ValueError("No cards left in deck!")
        return self.game_state.deck.pop()
    
    def handle_start_hand(self):
        """Initialize a new hand."""
        self._log_action("Starting new hand")
        
        # Clear hand history
        self.hand_history.clear()
        
        # Create deck
        self.game_state.deck = self.create_deck()
        
        # Reset game state
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.board = []
        self.game_state.street = "preflop"
        self.game_state.players_acted.clear()
        self.game_state.round_complete = False
        
        # Reset players
        for player in self.game_state.players:
            player.is_active = True
            player.cards = []
            player.current_bet = 0.0
            player.has_acted_this_round = False
            player.is_all_in = False
            player.total_invested = 0.0
        
        # Deal hole cards
        for player in self.game_state.players:
            player.cards = [self.deal_card(), self.deal_card()]
        
        # Post blinds
        sb_player = self.game_state.players[self.small_blind_position]
        bb_player = self.game_state.players[self.big_blind_position]
        
        sb_amount = self.game_state.big_blind / 2
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        sb_player.total_invested = sb_amount
        self.game_state.pot += sb_amount
        
        bb_amount = self.game_state.big_blind
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        bb_player.total_invested = bb_amount
        self.game_state.pot += bb_amount
        
        # Set current bet to BB
        self.game_state.current_bet = bb_amount
        self.game_state.min_raise = bb_amount
        
        # Set action to first player after BB
        self.action_player_index = (self.big_blind_position + 1) % self.num_players
        
        # Transition to preflop betting
        self.transition_to(PokerState.PREFLOP_BETTING)
    
    def handle_preflop_betting(self):
        """Handle preflop betting round."""
        self._log_action("Preflop betting round")
        self.game_state.street = "preflop"
    
    def handle_deal_flop(self):
        """Deal the flop."""
        self._log_action("Dealing flop")
        self.game_state.board = [self.deal_card(), self.deal_card(), self.deal_card()]
        self.game_state.street = "flop"
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = self.game_state.big_blind
        self.game_state.players_acted.clear()
        
        # Reset player bets and action flags
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_acted_this_round = False
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % self.num_players
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % self.num_players
        
        self.transition_to(PokerState.FLOP_BETTING)
    
    def handle_flop_betting(self):
        """Handle flop betting round."""
        self._log_action("Flop betting round")
        self.game_state.street = "flop"
    
    def handle_deal_turn(self):
        """Deal the turn."""
        self._log_action("Dealing turn")
        self.game_state.board.append(self.deal_card())
        self.game_state.street = "turn"
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = self.game_state.big_blind
        self.game_state.players_acted.clear()
        
        # Reset player bets and action flags
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_acted_this_round = False
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % self.num_players
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % self.num_players
        
        self.transition_to(PokerState.TURN_BETTING)
    
    def handle_turn_betting(self):
        """Handle turn betting round."""
        self._log_action("Turn betting round")
        self.game_state.street = "turn"
    
    def handle_deal_river(self):
        """Deal the river."""
        self._log_action("Dealing river")
        self.game_state.board.append(self.deal_card())
        self.game_state.street = "river"
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = self.game_state.big_blind
        self.game_state.players_acted.clear()
        
        # Reset player bets and action flags
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_acted_this_round = False
        
        # Set action to first active player after BTN
        self.action_player_index = (self.dealer_position + 1) % self.num_players
        while not self.game_state.players[self.action_player_index].is_active:
            self.action_player_index = (self.action_player_index + 1) % self.num_players
        
        self.transition_to(PokerState.RIVER_BETTING)
    
    def handle_river_betting(self):
        """Handle river betting round."""
        self._log_action("River betting round")
        self.game_state.street = "river"
    
    def handle_showdown(self):
        """Handle showdown."""
        self._log_action("Showdown")
        self.game_state.street = "showdown"
        
        # Determine winner
        winners = self.determine_winner()
        
        # Award pot
        if winners:
            pot_per_winner = self.game_state.pot / len(winners)
            for winner in winners:
                winner.stack += pot_per_winner
                self._log_action(f"{winner.name} wins ${pot_per_winner:.2f}")
        
        self.transition_to(PokerState.END_HAND)
    
    def handle_end_hand(self):
        """Handle end of hand."""
        self._log_action("Hand complete")
        self.game_state.street = "end_hand"
        
        # Reset pot
        self.game_state.pot = 0.0
        
        # Move dealer button
        self.dealer_position = (self.dealer_position + 1) % self.num_players
        self.small_blind_position = (self.dealer_position + 1) % self.num_players
        self.big_blind_position = (self.dealer_position + 2) % self.num_players
        
        # Update player positions
        positions = self._get_position_names()
        for i, player in enumerate(self.game_state.players):
            seat_offset = (i - self.dealer_position) % self.num_players
            if seat_offset < len(positions):
                player.position = positions[seat_offset]
            else:
                player.position = f"P{seat_offset+1}"
        
        if self.on_hand_complete:
            self.on_hand_complete()
    
    def execute_action(self, player: Player, action: ActionType, amount: float = 0):
        """Execute a player action."""
        if not player or not isinstance(action, ActionType) or amount < 0:
            self._log_action(f"ERROR: Invalid action parameters")
            return
        
        # Log the action
        self._log_action(f"{player.name}: {action.value.upper()} ${amount:.2f}")
        
        # Play sound if available
        if self.sfx:
            if action == ActionType.FOLD:
                self.sfx.play("player_fold")
            elif action == ActionType.CHECK:
                self.sfx.play("player_check")
            elif action == ActionType.CALL:
                self.sfx.play("player_call")
            elif action == ActionType.BET or action == ActionType.RAISE:
                self.sfx.play("player_bet")
        
        if action == ActionType.FOLD:
            player.is_active = False
        
        elif action == ActionType.CHECK:
            if self.game_state.current_bet > player.current_bet:
                self._log_action(f"ERROR: {player.name} cannot check when bet is ${self.game_state.current_bet}")
                return
            player.current_bet = 0
        
        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            actual_call = min(call_amount, player.stack)
            
            # Handle all-in
            if actual_call < call_amount:
                player.is_all_in = True
                self._log_action(f"{player.name} ALL-IN for ${actual_call:.2f}")
            
            player.stack -= actual_call
            player.current_bet += actual_call
            player.total_invested += actual_call
            self.game_state.pot += actual_call
            
            if player.stack == 0:
                player.is_all_in = True
        
        elif action == ActionType.BET:
            if self.game_state.current_bet > 0:
                self._log_action(f"ERROR: {player.name} cannot bet when current bet is ${self.game_state.current_bet}")
                return
            
            actual_bet = min(amount, player.stack)
            player.stack -= actual_bet
            player.current_bet = actual_bet
            player.total_invested += actual_bet
            self.game_state.pot += actual_bet
            self.game_state.current_bet = actual_bet
            
            if player.stack == 0:
                player.is_all_in = True
        
        elif action == ActionType.RAISE:
            min_raise_total = self.game_state.current_bet + self.game_state.min_raise
            if amount < min_raise_total:
                self._log_action(f"ERROR: Minimum raise is ${min_raise_total:.2f}")
                return
            
            total_bet = min(amount, player.current_bet + player.stack)
            additional_amount = total_bet - player.current_bet
            
            player.stack -= additional_amount
            player.current_bet = total_bet
            player.total_invested += additional_amount
            self.game_state.pot += additional_amount
            
            # Update game state
            old_bet = self.game_state.current_bet
            self.game_state.current_bet = total_bet
            self.game_state.min_raise = total_bet - old_bet
            
            # Clear acted players and reset flags
            self.game_state.players_acted.clear()
            for p in self.game_state.players:
                if p.is_active and p != player:
                    p.has_acted_this_round = False
        
        # Mark player as acted
        player.has_acted_this_round = True
        self.game_state.players_acted.add(self.game_state.players.index(player))
        
        # Check for round completion
        if self.is_round_complete():
            self.handle_round_complete()
    
    def is_round_complete(self) -> bool:
        """Check if the current betting round is complete."""
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have equal bets
        first_bet = active_players[0].current_bet
        for player in active_players:
            if player.current_bet != first_bet:
                return False
        
        # Check if all active players have acted
        for player in active_players:
            if not player.has_acted_this_round:
                return False
        
        return True
    
    def handle_round_complete(self):
        """Handle round completion."""
        self._log_action("Round complete")
        self.game_state.round_complete = True
        
        # Check for winner (all but one folded)
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.game_state.pot
            self._log_action(f"{winner.name} wins ${self.game_state.pot:.2f} (all others folded)")
            self.transition_to(PokerState.END_HAND)
            return
        
        # Move to next street
        if self.current_state == PokerState.PREFLOP_BETTING:
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.current_state == PokerState.FLOP_BETTING:
            self.transition_to(PokerState.DEAL_TURN)
        elif self.current_state == PokerState.TURN_BETTING:
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.current_state == PokerState.RIVER_BETTING:
            self.transition_to(PokerState.SHOWDOWN)
    
    def determine_winner(self) -> List[Player]:
        """Determine the winner(s) of the hand."""
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) == 1:
            return active_players
        
        if TREYS_AVAILABLE:
            return self._determine_winner_with_treys(active_players)
        else:
            return self._determine_winner_basic(active_players)
    
    def _determine_winner_with_treys(self, active_players: List[Player]) -> List[Player]:
        """Determine winner using Treys library."""
        evaluator = treys.Evaluator()
        best_hand = None
        winners = []
        
        for player in active_players:
            if not player.cards:
                continue
            
            # Convert cards to Treys format
            hole_cards = [self._card_to_treys(card) for card in player.cards]
            board_cards = [self._card_to_treys(card) for card in self.game_state.board]
            
            # Evaluate hand
            hand_score = evaluator.evaluate(board_cards, hole_cards)
            hand_class = evaluator.get_rank_class(hand_score)
            
            if best_hand is None or hand_score < best_hand:
                best_hand = hand_score
                winners = [player]
            elif hand_score == best_hand:
                winners.append(player)
        
        return winners
    
    def _card_to_treys(self, card: str) -> int:
        """Convert card string to Treys format."""
        rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                   'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        suit_map = {'h': 1, 'd': 2, 'c': 4, 's': 8}
        
        rank = rank_map[card[0]]
        suit = suit_map[card[1]]
        return rank + suit * 13
    
    def _determine_winner_basic(self, active_players: List[Player]) -> List[Player]:
        """Basic winner determination without Treys."""
        # Simple implementation for testing
        return [active_players[0]]  # Just return first player for now
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        if self.current_state == PokerState.END_HAND:
            return None
        
        # Find next active player
        for i in range(self.num_players):
            player_index = (self.action_player_index + i) % self.num_players
            player = self.game_state.players[player_index]
            
            if player.is_active and not player.has_acted_this_round:
                return player
        
        return None
    
    def get_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get strategy-based action for a bot player."""
        if not self.strategy_data:
            return ActionType.FOLD, 0
        
        # Simple strategy: call if we have a hand, fold otherwise
        if player.cards and len(player.cards) == 2:
            # Basic hand strength check
            if player.cards[0][0] == player.cards[1][0]:  # Pair
                return ActionType.CALL, 0
            elif player.cards[0][0] in ['A', 'K', 'Q'] or player.cards[1][0] in ['A', 'K', 'Q']:
                return ActionType.CALL, 0
        
        return ActionType.FOLD, 0
    
    def execute_bot_action(self, player: Player):
        """Execute a bot action."""
        if player.is_human:
            return
        
        action, amount = self.get_strategy_action(player)
        self.execute_action(player, action, amount)
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand."""
        if existing_players:
            self.game_state.players = existing_players
        
        self.transition_to(PokerState.START_HAND)
    
    def get_current_state(self) -> PokerState:
        """Get the current state."""
        return self.current_state
    
    def get_game_info(self) -> dict:
        """Get comprehensive game information."""
        return {
            "state": self.current_state.value,
            "street": self.game_state.street,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board.copy(),
            "players": [
                {
                    "name": p.name,
                    "stack": p.stack,
                    "position": p.position,
                    "is_human": p.is_human,
                    "is_active": p.is_active,
                    "current_bet": p.current_bet,
                    "is_all_in": p.is_all_in,
                    "cards": p.cards if p.is_human else []
                }
                for p in self.game_state.players
            ]
        }
    
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate an action."""
        errors = []
        
        if not player:
            errors.append("Player cannot be None")
            return errors
        
        if not isinstance(action, ActionType):
            errors.append("Invalid action type")
            return errors
        
        if amount < 0:
            errors.append("Amount cannot be negative")
            return errors
        
        if action == ActionType.CHECK and self.game_state.current_bet > player.current_bet:
            errors.append("Cannot check when there's a bet")
        
        if action == ActionType.BET and self.game_state.current_bet > 0:
            errors.append("Cannot bet when there's already a bet")
        
        if action == ActionType.RAISE:
            min_raise_total = self.game_state.current_bet + self.game_state.min_raise
            if amount < min_raise_total:
                errors.append(f"Minimum raise is ${min_raise_total:.2f}")
        
        return errors
    
    def is_valid_action(self, player: Player, action: ActionType, amount: float = 0) -> bool:
        """Check if an action is valid."""
        return len(self.validate_action(player, action, amount)) == 0 