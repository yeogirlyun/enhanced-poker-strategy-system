"""
Pure Poker State Machine - Clean Architecture

This is a pure poker rules engine that:
- Manages only poker state transitions
- Has no knowledge of human vs bot players
- Has no application-specific logic
- Uses dependency injection for all external concerns
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Protocol
from enum import Enum
import time

from .poker_types import Player, PokerState, GameState
from .hand_model import ActionType
from .session_logger import get_session_logger


class DeckProvider(Protocol):
    """Protocol for deck management."""
    def get_deck(self) -> List[str]:
        """Get a fresh deck of cards."""
        pass
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace the current deck."""
        pass


class RulesProvider(Protocol):
    """Protocol for poker rules."""
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """Get first player to act preflop."""
        pass
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """Get first active player to act postflop."""
        pass


class AdvancementController(Protocol):
    """Protocol for controlling game advancement."""
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Determine if the game should advance automatically."""
        pass
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion."""
        pass


@dataclass
class GameConfig:
    """Pure game configuration without application context."""
    num_players: int = 2
    small_blind: float = 1.0
    big_blind: float = 2.0
    starting_stack: float = 200.0


class PurePokerStateMachine:
    """
    Pure poker state machine that only handles poker rules and state transitions.
    
    All application-specific concerns (human vs bot, auto-advance, deck management)
    are handled through injected providers and controllers.
    """
    
    # Valid state transitions (pure poker rules)
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
        PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING, PokerState.END_HAND],
        PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
        PokerState.DEAL_TURN: [PokerState.TURN_BETTING, PokerState.END_HAND],
        PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
        PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING, PokerState.END_HAND],
        PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }
    
    def __init__(
        self, 
        config: GameConfig,
        deck_provider: Optional[DeckProvider] = None,
        rules_provider: Optional[RulesProvider] = None,
        advancement_controller: Optional[AdvancementController] = None
    ):
        """Initialize pure poker state machine with injected dependencies."""
        self.config = config
        self.deck_provider = deck_provider
        self.rules_provider = rules_provider
        self.advancement_controller = advancement_controller
        
        # Pure poker state
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop"
        )
        self.current_state = PokerState.START_HAND
        self.hand_number = 0
        self.action_player_index = 0
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 1
        
        # Round tracking - FIXED: Better tracking
        self.actions_this_round = 0
        self.players_acted_this_round: set = set()
        self.last_raiser_name: Optional[str] = None  # Track who made the last raise
        self.last_bet_size = 0.0  # Track last bet/raise size for min raise
        
        # Logging
        self.session_logger = get_session_logger()
        
        # Initialize players
        self._initialize_players()
        
        print(f"🔧 FIXED_PPSM: Initialized with {config.num_players} players")
    
    def _initialize_players(self):
        """Initialize players with pure poker data (no human/bot distinction)."""
        self.game_state.players = []
        for i in range(self.config.num_players):
            player = Player(
                name=f"Seat{i + 1}",
                stack=self.config.starting_stack,
                position="",
                is_human=False,  # Pure FPSM doesn't care about this
                is_active=True,
                cards=[],
            )
            self.game_state.players.append(player)
        
        # Assign positions
        self._assign_positions()
    
    def _assign_positions(self):
        """Assign poker positions relative to dealer."""
        num_players = len(self.game_state.players)
        if num_players == 2:
            # Heads-up: dealer is small blind
            positions = ["SB", "BB"]
        else:
            # Multi-way: standard positions
            positions = self._get_standard_positions(num_players)
        
        for i, player in enumerate(self.game_state.players):
            position_offset = (i - self.dealer_position) % num_players
            if position_offset < len(positions):
                player.position = positions[position_offset]
            else:
                player.position = f"Seat{i + 1}"
    
    def _get_standard_positions(self, num_players: int) -> List[str]:
        """Get standard poker position names."""
        if num_players <= 2:
            return ["SB", "BB"]
        elif num_players <= 6:
            return ["SB", "BB", "UTG", "MP", "CO", "BTN"][:num_players]
        else:
            # For larger games, add MP positions
            positions = ["SB", "BB", "UTG"]
            mp_count = num_players - 5  # Subtract SB, BB, UTG, CO, BTN
            for i in range(1, mp_count + 1):
                positions.append(f"MP{i}")
            positions.extend(["CO", "BTN"])
            return positions
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand with pure poker logic."""
        self.hand_number += 1
        self.current_state = PokerState.START_HAND

        # --- NEW: rotate dealer starting on the 2nd hand ---
        if self.hand_number > 1:
            self.dealer_position = (self.dealer_position + 1) % self.config.num_players

        # Reset game state for the new hand
        self.game_state.board = []
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.street = "preflop"

        # Use existing players if provided, otherwise the initialized ones
        if existing_players:
            self.game_state.players = existing_players
            if len(self.game_state.players) != self.config.num_players:
                raise ValueError(
                    f"Expected {self.config.num_players} players, got {len(self.game_state.players)}"
                )

        # Reset per-player state
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_folded = False
            player.is_active = True
            player.cards = []

        # --- NEW: compute blind seats from current dealer ---
        if self.config.num_players == 2:
            # Heads-up: dealer is SB
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
        else:
            # 3+ players: SB is next seat; BB is the one after
            self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.config.num_players

        # --- NEW: update human-readable positions relative to dealer each hand ---
        self._assign_positions()

        # Initialize/refresh deck
        if self.deck_provider:
            self.game_state.deck = self.deck_provider.get_deck()
        else:
            self.game_state.deck = self._create_standard_deck()

        # Deal hole cards, post blinds, and set first to act (your existing logic)
        self._deal_hole_cards()
        self._post_blinds()

        if self.rules_provider:
            self.action_player_index = self.rules_provider.get_first_to_act_preflop(
                self.dealer_position, self.config.num_players
            )
        else:
            if self.config.num_players == 2:
                self.action_player_index = self.small_blind_position
            else:
                self.action_player_index = (self.big_blind_position + 1) % self.config.num_players

        self.transition_to(PokerState.PREFLOP_BETTING)
        print(f"🃏 FIXED_PPSM: Hand {self.hand_number} started, action on {self.game_state.players[self.action_player_index].name}")
    
    def _create_standard_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        return [rank + suit for suit in suits for rank in ranks]
    
    def _deal_hole_cards(self):
        """Deal 2 hole cards to each player."""
        for player in self.game_state.players:
            player.cards = self._deal_cards(2)
    
    def _deal_cards(self, num_cards: int) -> List[str]:
        """Deal cards from the deck."""
        if len(self.game_state.deck) < num_cards:
            raise ValueError(f"Not enough cards in deck: need {num_cards}, have {len(self.game_state.deck)}")
        
        cards = self.game_state.deck[:num_cards]
        self.game_state.deck = self.game_state.deck[num_cards:]
        return cards
    
    def _post_blinds(self):
        """Post small and big blinds."""
        # Small blind
        sb_player = self.game_state.players[self.small_blind_position]
        sb_amount = min(self.config.small_blind, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.current_bet = sb_amount
        # Note: Blind amounts stay in current_bet until round completes
        
        # Big blind
        bb_player = self.game_state.players[self.big_blind_position]
        bb_amount = min(self.config.big_blind, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.current_bet = bb_amount
        # Note: Blind amounts stay in current_bet until round completes
        self.game_state.current_bet = bb_amount
        
        print(f"🃏 PURE_FPSM: Posted blinds - SB: ${sb_amount}, BB: ${bb_amount}")
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute a poker action with pure poker logic."""
        try:
            # Validate action
            if not self._is_valid_action(player, action_type, amount):
                print(f"❌ PURE_FPSM: Invalid action {action_type.value} ${amount} for {player.name}")
                return False
            
            # Execute the action
            success = self._apply_action(player, action_type, amount)
            if not success:
                return False
            
            # Track that this player acted
            self.actions_this_round += 1
            self.players_acted_this_round.add(player.name)
            
            # If this was a raise, reset who has acted (except the raiser)
            if action_type == ActionType.RAISE:
                # Everyone needs to respond to the raise
                self.players_acted_this_round = {player.name}
            
            # Check if round is complete
            if self._is_round_complete():
                self._handle_round_complete()
            else:
                self._advance_to_next_player()
            
            return True
            
        except Exception as e:
            print(f"❌ PURE_FPSM: Error executing action: {e}")
            return False
    
    def _is_valid_action(self, player: Player, action_type: ActionType, amount: float) -> bool:
        """Validate if an action is legal - FIXED version."""
        
        if player.has_folded or not player.is_active:
            return False
        
        # All-in players cannot act
        if player.stack == 0:
            return False
        
        if action_type == ActionType.FOLD:
            return True
            
        elif action_type == ActionType.CHECK:
            return player.current_bet == self.game_state.current_bet
            
        elif action_type == ActionType.CALL:
            return player.current_bet < self.game_state.current_bet
            
        elif action_type == ActionType.BET:
            # First wager of the street only
            if self.game_state.current_bet != 0:
                return False
            # Minimum bet is usually 1 big blind
            min_bet = self.config.big_blind
            additional_needed = amount - player.current_bet
            return amount >= min_bet and additional_needed <= player.stack
            
        elif action_type == ActionType.RAISE:
            # Only legal if there is an existing bet
            if self.game_state.current_bet == 0:
                return False
            
            # Calculate minimum raise
            # Min raise = current_bet + max(big_blind, last_raise_size)
            if self.last_bet_size > 0:
                min_raise_size = self.last_bet_size
            else:
                min_raise_size = self.config.big_blind
            
            min_raise_to = self.game_state.current_bet + min_raise_size
            additional_needed = amount - player.current_bet
            
            # Allow all-in even if less than min raise
            if additional_needed == player.stack:
                return amount > self.game_state.current_bet
            
            # Otherwise must meet minimum
            return amount >= min_raise_to and additional_needed <= player.stack
        
        return False
    
    def _apply_action(self, player: Player, action_type: ActionType, amount: float) -> bool:
        """Apply the action to game state."""
        if action_type == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
            
        elif action_type == ActionType.CHECK:
            pass  # No state change needed
            
        elif action_type == ActionType.CALL:
            call_amount = min(
                self.game_state.current_bet - player.current_bet,
                player.stack
            )
            player.stack -= call_amount
            player.current_bet += call_amount
            # Note: Call amount stays in current_bet until round completes
            
        elif action_type in [ActionType.BET, ActionType.RAISE]:
            # Track raise size for minimum raise calculations
            if action_type == ActionType.RAISE:
                self.last_bet_size = amount - self.game_state.current_bet
                self.last_raiser_name = player.name
            else:  # BET
                self.last_bet_size = amount
                self.last_raiser_name = player.name
            
            additional_bet = amount - player.current_bet
            if additional_bet > 0:
                player.stack -= additional_bet
                player.current_bet = amount
                # Note: Bet amount stays in current_bet until round completes
                self.game_state.current_bet = amount
        
        print(f"🃏 FIXED_PPSM: {player.name} {action_type.value} ${amount} (pot: ${self.game_state.pot})")
        return True
    
    def _is_round_complete(self) -> bool:
        """Check if the current betting round is complete - FIXED version."""
        active_players = [p for p in self.game_state.players if not p.has_folded and p.is_active]
        
        # If only one player left, round is complete
        if len(active_players) <= 1:
            return True
        
        # Get players who can still act (not all-in)
        actionable_players = [p for p in active_players if p.stack > 0]
        
        # If no one can act (all players all-in or folded), round is complete
        if len(actionable_players) == 0:
            return True
        
        # Check if all active players have matched the current bet
        for player in active_players:
            # Skip all-in players (they've contributed all they can)
            if player.stack == 0:
                continue
            # If someone hasn't matched the bet, round continues
            if player.current_bet < self.game_state.current_bet:
                return False
        
        # Special case: if there was a raise, everyone needs to act after it
        if self.last_raiser_name:
            # Everyone after the raiser must have acted
            for player in actionable_players:
                if player.name == self.last_raiser_name:
                    continue
                if player.name not in self.players_acted_this_round:
                    return False
        else:
            # No raises - just check everyone has acted at least once
            for player in actionable_players:
                if player.name not in self.players_acted_this_round:
                    # Exception: BB preflop gets option even if no raise
                    if (self.game_state.street == "preflop" and 
                        player == self.game_state.players[self.big_blind_position] and
                        self.game_state.current_bet == self.config.big_blind):
                        # BB hasn't acted yet but needs option
                        return False
                    # Otherwise, if they match current bet, they don't need to act
                    if player.current_bet != self.game_state.current_bet:
                        return False
        
        return True
    
    def _handle_round_complete(self):
        """Handle completion of a betting round - FIXED version."""
        print(f"🃏 FIXED_PPSM: Round complete on {self.game_state.street}")
        
        # Reset round tracking
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        self.last_raiser_name = None
        self.last_bet_size = 0.0
        
        # Notify advancement controller
        if self.advancement_controller:
            self.advancement_controller.on_round_complete(self.game_state.street, self.game_state)
        
        # Determine next state
        if self.current_state == PokerState.PREFLOP_BETTING:
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.current_state == PokerState.FLOP_BETTING:
            self.transition_to(PokerState.DEAL_TURN)
        elif self.current_state == PokerState.TURN_BETTING:
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.current_state == PokerState.RIVER_BETTING:
            self.transition_to(PokerState.SHOWDOWN)
        else:
            self.transition_to(PokerState.END_HAND)
    
    def _advance_to_next_player(self):
        """Advance to the next active player - FIXED version."""
        original_index = self.action_player_index
        
        for _ in range(len(self.game_state.players)):
            self.action_player_index = (self.action_player_index + 1) % len(self.game_state.players)
            next_player = self.game_state.players[self.action_player_index]
            
            # Skip folded players
            if next_player.has_folded:
                continue
            
            # Skip inactive players
            if not next_player.is_active:
                continue
            
            # Skip all-in players (stack == 0)
            if next_player.stack == 0:
                continue
            
            # Found valid next player
            print(f"🃏 FIXED_PPSM: Action advances to {next_player.name}")
            return
        
        # No actionable players found, round should be complete
        print(f"🃏 FIXED_PPSM: No actionable players found, completing round")
        self._handle_round_complete()
    
    def transition_to(self, new_state: PokerState):
        """Transition to a new poker state."""
        if new_state not in self.STATE_TRANSITIONS.get(self.current_state, []):
            raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        print(f"🃏 PURE_FPSM: {old_state} → {new_state}")
        
        # Handle state-specific logic
        if new_state == PokerState.DEAL_FLOP:
            self.game_state.board.extend(self._deal_cards(3))
            self.game_state.street = "flop"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
            
        elif new_state == PokerState.DEAL_TURN:
            self.game_state.board.extend(self._deal_cards(1))
            self.game_state.street = "turn"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
            
        elif new_state == PokerState.DEAL_RIVER:
            self.game_state.board.extend(self._deal_cards(1))
            self.game_state.street = "river"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
        
        # Check if advancement controller wants to auto-advance
        if (self.advancement_controller and 
            self.advancement_controller.should_advance_automatically(new_state, self.game_state.players)):
            
            if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                # Auto-advance to betting round
                betting_states = {
                    PokerState.DEAL_FLOP: PokerState.FLOP_BETTING,
                    PokerState.DEAL_TURN: PokerState.TURN_BETTING,
                    PokerState.DEAL_RIVER: PokerState.RIVER_BETTING,
                }
                self.transition_to(betting_states[new_state])
    
    def _reset_bets_for_new_round(self):
        """Reset bets for a new betting round."""
        # First, collect all current bets into the pot
        for player in self.game_state.players:
            self.game_state.pot += player.current_bet
            player.current_bet = 0.0
        self.game_state.current_bet = 0.0
    
    def _set_first_to_act_postflop(self):
        """Set first to act for postflop rounds."""
        if self.rules_provider:
            self.action_player_index = self.rules_provider.get_first_to_act_postflop(
                self.dealer_position, self.game_state.players
            )
        else:
            # Default: first active player after dealer
            self.action_player_index = self._find_first_active_after_dealer()
    
    def _find_first_active_after_dealer(self) -> int:
        """Find first active player after dealer."""
        for i in range(1, len(self.game_state.players) + 1):
            idx = (self.dealer_position + i) % len(self.game_state.players)
            player = self.game_state.players[idx]
            if not player.has_folded and player.is_active:
                return idx
        return -1  # No active players
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information."""
        return {
            "players": [
                {
                    "name": p.name,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "has_folded": p.has_folded,
                    "position": p.position,
                    "cards": p.cards,
                }
                for p in self.game_state.players
            ],
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board,
            "street": self.game_state.street,
            "current_state": self.current_state.value,
            "action_player_index": self.action_player_index,
            "hand_number": self.hand_number,
            "dealer_position": self.dealer_position,
        }
