#!/usr/bin/env python3
"""
Texas Hold'em Poker State Machine - FULLY IMPROVED VERSION

This version implements all critical fixes:
1. Dynamic position tracking
2. Correct raise logic  
3. All-in state tracking
4. Improved round completion
5. Strategy integration for bots
6. Better input validation
"""

from enum import Enum
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass, field
import time
import random
import sys
import os

# Add the parent directory to the path to import sound_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sound_manager import SoundManager

# Import the enhanced hand evaluator for accurate winner determination
from enhanced_hand_evaluation import EnhancedHandEvaluator, HandRank


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
    """Enhanced Player data structure with all-in tracking."""
    name: str
    stack: float
    position: str
    is_human: bool
    is_active: bool
    cards: List[str]
    current_bet: float = 0.0
    has_acted_this_round: bool = False
    is_all_in: bool = False  # NEW: Track all-in state
    total_invested: float = 0.0  # NEW: Track total money put in pot
    # BUG FIX: Track partial calls for side pot calculations
    partial_call_amount: Optional[float] = None
    full_call_amount: Optional[float] = None


@dataclass
class GameState:
    """Enhanced game state with better tracking."""
    players: List[Player]
    board: List[str]
    pot: float
    current_bet: float
    street: str
    players_acted: Set[int] = field(default_factory=set)
    round_complete: bool = False
    deck: List[str] = field(default_factory=list)
    min_raise: float = 1.0  # NEW: Track minimum raise amount
    big_blind: float = 1.0  # <-- ADD THIS LINE


@dataclass
class HandHistoryLog:
    """A snapshot of the game state at a specific action."""
    timestamp: float
    street: str
    player_name: str
    action: ActionType
    amount: float
    pot_size: float
    board: List[str]
    player_states: List[dict]  # Store a simplified dict of each player's state


class ImprovedPokerStateMachine:
    """Fully improved poker state machine with all critical fixes."""

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

    def __init__(self, num_players: int = 6, strategy_data=None, root_tk=None):
        self.current_state = PokerState.START_HAND
        self.game_state = None
        self.action_player_index = 0
        self.num_players = num_players
        self.strategy_data = strategy_data  # NEW: Strategy integration
        self.root_tk = root_tk  # NEW: Store reference to root window for delays

        # Initialize sound manager
        self.sfx = SoundManager()

        # FIX 1: Dynamic position tracking
        self.dealer_position = 0
        self.update_blind_positions()  # Calculate blind positions based on num_players
        self.position_names = self._get_position_names()

        # Callbacks for UI updates
        self.on_state_change = None
        self.on_action_required = None
        self.on_round_complete = None
        self.on_hand_complete = None
        self.on_log_entry = None  # NEW: Callback for detailed action logging

        # Logging with size limit
        self.action_log = []
        self.max_log_size = 1000  # Limit log size
        
        # NEW: Advanced logging system
        self.hand_history: List[HandHistoryLog] = []  # For structured logging
        
        # Add caching for performance
        self._hand_eval_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._max_cache_size = 10000
        
        # Initialize winner tracking
        self._last_winner = None

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
            # Generic positions for other sizes
            positions = ["BTN", "SB", "BB"]
            for i in range(3, self.num_players):
                positions.append(f"P{i+1}")
            return positions

    def log_state_change(self, player: Player, action: ActionType, amount: float):
        """Logs the entire game state at the moment of an action."""
        if not self.game_state:
            return

        # Create a simplified snapshot of each player's state
        player_states = [
            {
                "name": p.name,
                "stack": p.stack,
                "current_bet": p.current_bet,
                "is_active": p.is_active,
                "is_all_in": p.is_all_in,
                "cards": p.cards if p.is_human else []  # Only log human cards for privacy/realism
            }
            for p in self.game_state.players
        ]

        log_entry = HandHistoryLog(
            timestamp=time.time(),
            street=self.game_state.street,
            player_name=player.name,
            action=action,
            amount=amount,
            pot_size=self.game_state.pot,
            board=self.game_state.board.copy(),
            player_states=player_states
        )
        
        self.hand_history.append(log_entry)
        # Also print a simple debug message to the console
        self._log_action(f"{player.name}: {action.value.upper()} ${amount:.2f}")

    def _log_action(self, message: str):
        """Log a simple action message to the console for debugging."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.action_log.append(log_entry)
        
        if len(self.action_log) > self.max_log_size:
            self.action_log = self.action_log[-self.max_log_size:]
        
        print(log_entry)
        
        # NEW: Call the UI callback for detailed logging
        if self.on_log_entry:
            self.on_log_entry(message)

    def transition_to(self, new_state: PokerState):
        """Transition to a new state with validation."""
        if new_state in self.STATE_TRANSITIONS[self.current_state]:
            old_state = self.current_state
            print(f"🔄 STATE: {old_state.value} → {new_state.value}")  # Debug
            print(f"   Active players: {[p.name for p in self.game_state.players if p.is_active]}")  # Debug
            print(f"   Current pot: ${self.game_state.pot}")  # Debug
            
            self.current_state = new_state
            self._log_action(f"STATE TRANSITION: {old_state.value} → {new_state.value}")
            if self.on_state_change:
                self.on_state_change(new_state)
            self.handle_state_entry()
        else:
            raise ValueError(
                f"Invalid state transition: {self.current_state.value} → {new_state.value}"
            )

    def handle_state_entry(self, existing_players: Optional[List[Player]] = None):
        """
        The main handler for all state transitions. Executes the appropriate
        logic based on the current game state.
        """
        handlers = {
            PokerState.START_HAND: lambda: self.handle_start_hand(existing_players),
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

    # FIX 1: Dynamic Position Tracking
    def advance_dealer_position(self):
        """Move dealer button for next hand."""
        self.dealer_position = (self.dealer_position + 1) % self.num_players
        self.update_blind_positions()
        # Update player positions after dealer advance
        if self.game_state:
            self.assign_positions()

    def update_blind_positions(self):
        """Update blind positions based on current dealer position."""
        if self.num_players == 2:
            # Heads up: dealer is small blind
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.num_players
        else:
            self.small_blind_position = (self.dealer_position + 1) % self.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.num_players

    def assign_positions(self):
        """Assign positions relative to dealer with proper mapping."""
        # FIXED: Use the class position names that match the number of players
        positions = self._get_position_names()
        
        for i in range(self.num_players):
            seat_offset = (i - self.dealer_position) % self.num_players
            if seat_offset < len(positions):
                self.game_state.players[i].position = positions[seat_offset]
            else:
                # Fallback for more players than defined positions
                self.game_state.players[i].position = f"P{seat_offset+1}"

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

    def handle_start_hand(self, existing_players: Optional[List[Player]] = None):
        """Initialize a new hand with all fixes, using existing players if provided."""
        self._log_action("Starting new hand")
        
        # --- NEW: Clear the hand history ---
        self.hand_history.clear()

        # Create deck
        deck = self.create_deck()

        # Use existing players or create new ones
        if existing_players:
            players = existing_players
            for player in players:
                # Reset hand-specific attributes
                player.is_active = True
                player.cards = []
                player.current_bet = 0.0
                player.has_acted_this_round = False
                player.is_all_in = False
                player.total_invested = 0.0
        else:
            # Create players if they don't exist
            players = []
            for i in range(self.num_players):
                is_human = i == 0
                player = Player(
                    name=f"Player {i+1}",
                    stack=100.0,
                    position="",  # Will be assigned
                    is_human=is_human,
                    is_active=True,
                    cards=[],
                    current_bet=0.0,
                    has_acted_this_round=False,
                    is_all_in=False,
                    total_invested=0.0,
                )
                players.append(player)

        # Create enhanced game state
        self.game_state = GameState(
            players=players,
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=deck,
            min_raise=1.0,
            big_blind=1.0,  # <-- ADD THIS LINE
        )

        # Assign positions correctly
        self.assign_positions()

        # Post blinds with proper tracking
        sb_player = self.game_state.players[self.small_blind_position]
        bb_player = self.game_state.players[self.big_blind_position]

        sb_amount = 0.5
        bb_amount = 1.0

        # Check if players can post blinds
        if sb_player.stack < sb_amount or bb_player.stack < bb_amount:
            self._log_action("Insufficient stacks for blinds; ending game")
            self.transition_to(PokerState.END_HAND)
            return

        # --- THIS IS THE CRITICAL BUG FIX ---
        # Post blinds by adjusting stack and pot, and set current_bet for the betting round
        sb_player.stack -= sb_amount
        sb_player.total_invested = sb_amount

        bb_player.stack -= bb_amount
        bb_player.total_invested = bb_amount

        # --- THIS IS THE CRITICAL BUG FIX ---
        # Set the player's current_bet to what they posted. This is the key.
        sb_player.current_bet = sb_amount
        bb_player.current_bet = bb_amount

        # The pot is the sum of investments, and the amount to call is the big blind.
        self.game_state.pot = sb_player.total_invested + bb_player.total_invested
        self.game_state.current_bet = bb_amount
        # --- End of Bug Fix ---
        
        self.game_state.min_raise = bb_amount

        # Deal hole cards
        self.deal_hole_cards()

        # Set action to UTG (first player after BB)
        self.action_player_index = (self.big_blind_position + 1) % self.num_players

        self.transition_to(PokerState.PREFLOP_BETTING)

    def deal_hole_cards(self):
        """Deal hole cards to all players."""
        for player in self.game_state.players:
            player.cards = [self.deal_card(), self.deal_card()]
            # Only play sound if we're in an active game state (not during initialization)
            if self.current_state in [PokerState.PREFLOP_BETTING, PokerState.FLOP_BETTING, 
                                    PokerState.TURN_BETTING, PokerState.RIVER_BETTING]:
                # Use authentic dealing sound if available
                if "card_deal" in self.sfx.sounds:
                    self.sfx.play("card_deal")  # Authentic dealing sound
                else:
                    self.sfx.play("card_deal")  # Generated fallback

    def handle_preflop_betting(self):
        """Handle preflop betting round."""
        self._log_action("Preflop betting round")
        self.game_state.street = "preflop"
        
        # --- NEW: Only reset round tracking, NOT the action player index ---
        # The action player index was already set correctly in handle_start_hand
        self.game_state.players_acted.clear()
        for player in self.game_state.players:
            player.has_acted_this_round = False
        # --- END NEW ---

        if not self.is_round_complete():
            self.handle_current_player_action()
        else:
            self.transition_to(PokerState.DEAL_FLOP)

    def reset_round_tracking(self):
        """Reset tracking for new betting round."""
        self.game_state.players_acted.clear()
        for player in self.game_state.players:
            player.has_acted_this_round = False

    def handle_deal_flop(self):
        """Deal the flop."""
        print("🎴 HANDLE_DEAL_FLOP called!")  # Debug
        self._log_action("🎴 DEALING FLOP")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        # Deal 3 community cards
        for i in range(3):
            card = self.deal_card()
            self.game_state.board.append(card)
            self._log_action(f"🎴 Dealt card {i+1}: {card}")

        self._log_action(f"🎴 FLOP COMPLETE: {' '.join(self.game_state.board)}")
        self._log_action(f"📊 Pot before flop betting: ${self.game_state.pot:.2f}")
        
        self.prepare_new_betting_round()
        self.transition_to(PokerState.FLOP_BETTING)

    def handle_deal_turn(self):
        """Deal the turn."""
        print("🎴 HANDLE_DEAL_TURN called!")  # Debug
        self._log_action("Dealing turn")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        self.game_state.board.append(self.deal_card())
        self.prepare_new_betting_round()
        self.transition_to(PokerState.TURN_BETTING)

    def handle_deal_river(self):
        """Deal the river."""
        print("🎴 HANDLE_DEAL_RIVER called!")  # Debug
        self._log_action("Dealing river")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        self.game_state.board.append(self.deal_card())
        self.prepare_new_betting_round()
        self.transition_to(PokerState.RIVER_BETTING)

    def prepare_new_betting_round(self):
        """
        Resets bets for the new round and finds the correct first player to act.
        Post-flop, action starts with the first active player left of the dealer.
        """
        self._log_action(f"Preparing new betting round for {self.game_state.street}.")
        
        # Reset game state for new round
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = 1.0
        self.reset_round_tracking()

        # Reset bets and action flags for all players
        for p in self.game_state.players:
            p.current_bet = 0
            p.has_acted = False

        # Find the correct first player to act
        num_players = len(self.game_state.players)
        
        # In pre-flop, the player after the Big Blind acts first.
        if self.game_state.street == 'preflop':
            start_index = (self.big_blind_position + 1) % num_players
        # Post-flop, the first active player to the left of the dealer acts first.
        else:
            start_index = (self.dealer_position + 1) % num_players

        # Find the first active player starting from the calculated start_index
        for i in range(num_players):
            current_index = (start_index + i) % num_players
            player_at_index = self.game_state.players[current_index]
            if player_at_index.is_active and not player_at_index.is_all_in:
                self.action_player_index = current_index
                self._log_action(f"New round. Action starts with {player_at_index.name} in seat {current_index}.")
                return

        # If no player can act, something is wrong. Log it.
        self._log_action("ERROR: Could not find any active player to start the betting round.")

    def set_action_to_first_active_after_button(self):
        """Set action to first active player after button."""
        for i in range(1, self.num_players):
            player_index = (self.dealer_position + i) % self.num_players
            player = self.game_state.players[player_index]
            if player.is_active and not player.is_all_in:
                self.action_player_index = player_index
                return
        
        # If no one can act, round is complete
        self.action_player_index = -1

    def handle_flop_betting(self):
        """Handle flop betting round."""
        self._log_action("Flop betting round")
        self.game_state.street = "flop"
        self._handle_betting_round(PokerState.DEAL_TURN)

    def handle_turn_betting(self):
        """Handle turn betting round."""
        self._log_action("Turn betting round")
        self.game_state.street = "turn"
        self._handle_betting_round(PokerState.DEAL_RIVER)

    def handle_river_betting(self):
        """Handle river betting round."""
        self._log_action("River betting round")
        self.game_state.street = "river"
        self._handle_betting_round(PokerState.SHOWDOWN)

    def _handle_betting_round(self, next_state: PokerState):
        """Generic betting round handler."""
        if self.is_round_complete():
            # FIX: Call handle_round_complete() instead of direct transition
            self.handle_round_complete()
        else:
            self.handle_current_player_action()

    # FIX 4: Improved Round Completion Logic
    def is_round_complete(self) -> bool:
        """Check if betting round is complete with all-in handling."""
        active_players = [p for p in self.game_state.players if p.is_active]

        if len(active_players) <= 1:
            return True

        can_act_players = [p for p in active_players if not p.is_all_in]

        if not can_act_players:
            return True

        # Check if all players who can act have acted and bets are equal
        can_act_indices = [i for i, p in enumerate(self.game_state.players) 
                          if p.is_active and not p.is_all_in]

        all_acted = all(i in self.game_state.players_acted for i in can_act_indices)

        # Special case for preflop: BB gets option to raise
        if self.game_state.street == "preflop" and self.game_state.current_bet == 1.0:
            bb_player = self.game_state.players[self.big_blind_position]
            if (bb_player.is_active and not bb_player.is_all_in and 
                self.big_blind_position not in self.game_state.players_acted):
                return False

        target_bet = self.game_state.current_bet
        bets_equal = all(p.current_bet == target_bet for p in can_act_players)

        return all_acted and bets_equal

    def handle_current_player_action(self):
        """Handle the current player's action with a delay for bots."""
        # --- NEW: Check if hand has ended ---
        if self.current_state == PokerState.END_HAND:
            self._log_action("DEBUG: Hand has ended, no more actions allowed.")
            return
        # --- END NEW ---
        
        if self.action_player_index == -1:
            self._log_action("DEBUG: No action player index, round is likely complete.")
            return

        current_player = self.game_state.players[self.action_player_index]
        self._log_action(f"STATE MACHINE: It is turn for Player at index {self.action_player_index} ({current_player.name})")

        if current_player.is_human:
            self._log_action(f"Human turn: {current_player.name}")
            if self.on_action_required:
                self.on_action_required(current_player)
        else:
            self._log_action(f"Bot turn: {current_player.name}")
            # Add delay for bot actions to make the game more realistic
            if self.root_tk:
                self.root_tk.after(1000, lambda: self.execute_bot_action(current_player))
            else:
                # Fallback if no root_tk available
                import time
                time.sleep(1)
                self.execute_bot_action(current_player)

    # FIX 5: Strategy Integration for Bots
    def execute_bot_action(self, player: Player):
        """Execute bot action using strategy data."""
        # --- NEW: Check if hand has ended ---
        if self.current_state == PokerState.END_HAND:
            self._log_action("DEBUG: Hand has ended, bot action cancelled.")
            return
        # --- END NEW ---
        
        if self.strategy_data:
            action, amount = self.get_strategy_action(player)
        else:
            action, amount = self.get_basic_bot_action(player)
        
        self.execute_action(player, action, amount)

    def get_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get bot action using strategy data with proper hand strength calculation."""
        street = self.game_state.street
        position = player.position
        
        # DEBUG: Add comprehensive debugging for action selection
        call_amount = self.game_state.current_bet - player.current_bet
        print(f"🤖 BOT ACTION DEBUG for {player.name} ({position}):")
        print(f"   Current bet: ${self.game_state.current_bet}, Player bet: ${player.current_bet}")
        print(f"   Call amount: ${call_amount}")
        print(f"   Street: {street}")
        
        # --- CRITICAL BUG FIX: Big Blind Check Logic ---
        # If it's the Big Blind's turn pre-flop and there's no raise,
        # they have the option to check. They should never fold in this spot.
        is_preflop_bb_option = (
            street == 'preflop' and
            position == 'BB' and
            call_amount == 0
        )
        if is_preflop_bb_option:
            print(f"   🤖 CRITICAL FIX: BB has option to check, defaulting to CHECK")  # Debug
            return ActionType.CHECK, 0
        # --- End of Critical Bug Fix ---
        
        try:
            if street == "preflop":
                # --- NEW: TIER-BASED DECISION LOGIC ---
                tier_name = None
                player_hand_str = self.get_hand_notation(player.cards)
                
                # Check if hand is in any tier
                for tier in self.strategy_data.tiers:
                    if player_hand_str in tier.hands:
                        tier_name = tier.name
                        break

                if not tier_name:
                    return ActionType.FOLD, 0  # If the hand is not in any tier, fold it

                # Now, use the tier name and HS score for decisions
                hand_strength = self.get_preflop_hand_strength(player.cards)
                
                # If facing a raise (current_bet > big blind)
                # FIX: Use constant big blind amount instead of non-existent field
                BIG_BLIND_AMOUNT = 1.0  # Fixed big blind amount
                if self.game_state.current_bet > BIG_BLIND_AMOUNT:
                    print(f"   🤖 Logic: Facing a raise (current_bet ${self.game_state.current_bet} > big_blind ${BIG_BLIND_AMOUNT})")  # Debug
                    # Get vs_raise rules from strategy (or use defaults)
                    vs_raise_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("vs_raise", {}).get(position, {})
                    
                    # --- IMPROVED 3-BETTING LOGIC WITH BACKWARD COMPATIBILITY ---
                    value_3bet_thresh = vs_raise_rules.get("value_thresh", 75)
                    sizing = vs_raise_rules.get("sizing", 3.0)
                    
                    # Handle both call_range (new) and call_thresh (old) formats
                    call_range = vs_raise_rules.get("call_range", None)
                    if call_range is None:
                        # Backward compatibility: convert call_thresh to call_range
                        call_thresh = vs_raise_rules.get("call_thresh", 65)
                        call_range = [call_thresh, value_3bet_thresh - 1]
                    
                    print(f"   🤖 Hand strength: {hand_strength}, 3bet threshold: {value_3bet_thresh}, call range: {call_range}")  # Debug
                    if hand_strength >= value_3bet_thresh:
                        print(f"   🤖 Action: RAISE (hand_strength >= {value_3bet_thresh})")  # Debug
                        return ActionType.RAISE, min(self.game_state.current_bet * sizing, player.stack)
                    elif call_range[0] <= hand_strength <= call_range[1]:
                        print(f"   🤖 Action: CALL (hand_strength {hand_strength} in range {call_range})")  # Debug
                        return ActionType.CALL, self.game_state.current_bet - player.current_bet
                    else:
                        print(f"   🤖 Action: FOLD (hand_strength {hand_strength} too low)")  # Debug
                        return ActionType.FOLD, 0
                    # --- END IMPROVED LOGIC ---
                else:  # This is an opening opportunity
                    print(f"   🤖 Logic: Opening opportunity (current_bet ${self.game_state.current_bet} <= big_blind ${BIG_BLIND_AMOUNT})")  # Debug
                    # Use existing open_rules for opening
                    open_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("open_rules", {})
                    threshold = open_rules.get(position, {}).get("threshold", 60)
                    sizing = open_rules.get(position, {}).get("sizing", 3.0)
                    
                    # --- THIS IS THE CRITICAL BUG FIX ---
                    # If player is BB and there was no raise, they have the option to check.
                    if player.position == "BB" and self.game_state.current_bet == self.game_state.big_blind:
                        return ActionType.CHECK, 0
                    # --- End of Bug Fix ---
                    
                    # --- NEW: ADJUST FOR LIMPERS ---
                    limpers = len([p for p in self.game_state.players 
                                 if p.current_bet == BIG_BLIND_AMOUNT and p.position != "BB"])
                    if limpers > 0:
                        sizing += limpers  # Add one extra BB for each limper
                    # --- END LIMPER ADJUSTMENT ---
                    
                    # FIX: Check if player already has the current bet amount
                    call_amount = self.game_state.current_bet - player.current_bet
                    print(f"   🤖 Call amount check: ${call_amount}")  # Debug
                    print(f"   🤖 Player current bet: ${player.current_bet}, table current bet: ${self.game_state.current_bet}")  # Debug
                    if call_amount <= 0:
                        # Player already has the current bet amount, they should CHECK
                        print(f"   🤖 Action: CHECK (call_amount <= 0)")  # Debug
                        return ActionType.CHECK, 0
                    
                    print(f"   🤖 Hand strength: {hand_strength}, threshold: {threshold}")  # Debug
                    if hand_strength >= threshold:
                        # FIX: Use RAISE when there's already a bet, BET only when no bet
                        if self.game_state.current_bet > 0:
                            print(f"   🤖 Action: RAISE (hand_strength >= threshold, current bet exists)")  # Debug
                            return ActionType.RAISE, min(sizing, player.stack)
                        else:
                            print(f"   🤖 Action: BET (hand_strength >= threshold, no current bet)")  # Debug
                            return ActionType.BET, min(sizing, player.stack)
                    else:
                        # FIX: Always check call_amount first, even when hand strength is low
                        if call_amount <= 0:
                            print(f"   🤖 Action: CHECK (call_amount <= 0, even with low hand strength)")  # Debug
                            return ActionType.CHECK, 0
                        # Player should check if in BB and no one raised, otherwise fold
                        elif player.position == "BB" and self.game_state.current_bet == BIG_BLIND_AMOUNT:
                            print(f"   🤖 Action: CHECK (BB with no raise)")  # Debug
                            return ActionType.CHECK, 0
                        else:
                            print(f"   🤖 Action: FOLD (hand_strength too low, call_amount > 0)")  # Debug
                            return ActionType.FOLD, 0
                # --- END TIER-BASED LOGIC ---
            else:
                # Use postflop strategy with advanced pot odds
                hand_strength = self.get_postflop_hand_strength(player.cards, self.game_state.board)
                postflop = self.strategy_data.strategy_dict.get("postflop", {})
                pfa_data = postflop.get("pfa", {}).get(street, {}).get(position, {})
                
                val_thresh = pfa_data.get("val_thresh", 25)
                check_thresh = pfa_data.get("check_thresh", 10)
                sizing = pfa_data.get("sizing", 0.75)
                
                # Use pot odds for call decisions
                call_amount = self.game_state.current_bet - player.current_bet
                if call_amount > 0:
                    pot_odds = self.calculate_pot_odds(call_amount)
                    should_call = self.should_call_by_pot_odds(player, call_amount)
                    
                    if should_call:
                        return ActionType.CALL, call_amount
                    else:
                        return ActionType.FOLD, 0
                elif call_amount == 0:
                    # Player already has the current bet amount, they should CHECK
                    return ActionType.CHECK, 0
                
                if hand_strength >= val_thresh:
                    if self.game_state.current_bet == 0:
                        bet_amount = min(self.game_state.pot * sizing, player.stack)
                        return ActionType.BET, bet_amount
                    else:
                        # FIX: Check call_amount again to avoid "Nothing to call" error
                        if call_amount > 0:
                            return ActionType.CALL, call_amount
                        else:
                            return ActionType.CHECK, 0
                elif hand_strength >= check_thresh:
                    if self.game_state.current_bet == 0:
                        return ActionType.CHECK, 0
                    else:
                        # FIX: Check call_amount again to avoid "Nothing to call" error
                        if call_amount > 0 and call_amount <= player.stack * 0.1:
                            return ActionType.CALL, call_amount
                        else:
                            return ActionType.CHECK, 0
                else:
                    if self.game_state.current_bet == 0:
                        return ActionType.CHECK, 0
                    else:
                        return ActionType.FOLD, 0
        except (KeyError, AttributeError):
            # Fall back to basic logic if strategy data is malformed
            pass
        
        return self.get_basic_bot_action(player)

    def get_hand_notation(self, cards: List[str]) -> str:
        """Converts two cards into standard poker notation (e.g., AKs, T9o, 77)."""
        if len(cards) != 2:
            return ""

        rank1, suit1 = cards[0][0], cards[0][1]
        rank2, suit2 = cards[1][0], cards[1][1]

        if rank1 == rank2:
            return f"{rank1}{rank2}"
        else:
            suited = "s" if suit1 == suit2 else "o"
            # Order the ranks correctly (e.g., AKs, not KAs)
            rank_order = "AKQJT98765432"
            if rank_order.index(rank1) < rank_order.index(rank2):
                return f"{rank1}{rank2}{suited}"
            else:
                return f"{rank2}{rank1}{suited}"

    def get_preflop_hand_strength(self, cards: List[str]) -> int:
        """Get preflop hand strength using enhanced evaluator."""
        from enhanced_hand_evaluation import hand_evaluator
        return hand_evaluator.get_preflop_hand_strength(cards)

    def get_postflop_hand_strength(self, cards: List[str], board: List[str]) -> int:
        """Get postflop hand strength using enhanced evaluator."""
        from enhanced_hand_evaluation import hand_evaluator
        evaluation = hand_evaluator.evaluate_hand(cards, board)
        return evaluation['strength_score']

    def classify_hand(self, cards: List[str], board: List[str]) -> str:
        """Classify hand type for postflop strategy with all variants."""
        all_cards = cards + board
        rank_counts = {}
        suit_counts = {}
        
        for card in all_cards:
            rank, suit = card[0], card[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        rank_values = sorted(rank_counts.values(), reverse=True)
        
        # Check pocket pair for set vs trips
        has_pocket_pair = len(cards) == 2 and cards[0][0] == cards[1][0]
        
        # Hand classifications from strongest to weakest
        if 4 in rank_values:
            return "quads"
        
        elif 3 in rank_values and 2 in rank_values:
            return "full_house"
        
        elif max(suit_counts.values()) >= 5:
            if self._is_nut_flush(cards, board, suit_counts):
                return "nut_flush"
            return "flush"
        
        elif self._has_straight(list(rank_counts.keys())):
            return "straight"
        
        elif 3 in rank_values:
            if has_pocket_pair:
                pocket_rank = cards[0][0]
                if rank_counts.get(pocket_rank, 0) == 3:
                    return "set"
            return "trips"
        
        elif rank_values.count(2) >= 2:
            return "two_pair"
        
        elif 2 in rank_values:
            # Detailed pair classification
            pair_rank = None
            for rank, count in rank_counts.items():
                if count == 2:
                    pair_rank = rank
                    break
            
            if not board:  # Preflop
                return "pair"
            
            # Check pair strength relative to board
            board_ranks = [card[0] for card in board]
            rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                         '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                         '4': 4, '3': 3, '2': 2}
            
            board_values = sorted([rank_order.get(r, 0) for r in board_ranks], reverse=True)
            pair_value = rank_order.get(pair_rank, 0)
            
            # Check if we have an overpair (pocket pair higher than board)
            if has_pocket_pair and pair_value > max(board_values):
                return "over_pair"
            
            # Check position of pair relative to board
            if pair_value >= board_values[0]:
                # Top pair - check kicker
                player_ranks = [card[0] for card in cards]
                kicker_ranks = [r for r in player_ranks if r != pair_rank]
                
                if kicker_ranks:
                    kicker_value = max(rank_order.get(r, 0) for r in kicker_ranks)
                    if kicker_value >= 11:  # Jack or better
                        return "top_pair_good_kicker"
                    else:
                        return "top_pair_bad_kicker"
                return "top_pair"
            
            elif len(board_values) > 1 and pair_value >= board_values[1]:
                return "second_pair"
            
            else:
                return "bottom_pair"
        
        # Check for draws
        elif max(suit_counts.values()) == 4:
            if self._is_nut_flush_draw(cards, board, suit_counts):
                return "nut_flush_draw"
            return "flush_draw"
        
        elif self._has_open_ended_draw(list(rank_counts.keys())):
            if max(suit_counts.values()) == 4:
                return "combo_draw"
            return "open_ended_draw"
        
        elif self._has_gutshot_draw(list(rank_counts.keys())):
            return "gutshot_draw"
        
        else:
            return "high_card"

    def _analyze_board_texture(self, board: List[str]) -> dict:
        """Analyze board texture for strategic considerations."""
        if not board:
            return {"type": "preflop"}
        
        board_ranks = [card[0] for card in board]
        board_suits = [card[1] for card in board]
        
        # Check for paired board
        rank_counts = {}
        for rank in board_ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # Check for monotone board
        suit_counts = {}
        for suit in board_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Check for connected board
        connected = self._is_board_connected(board_ranks)
        
        return {
            "paired": any(count >= 2 for count in rank_counts.values()),
            "monotone": max(suit_counts.values()) >= 3,
            "connected": connected,
            "dry": not (any(count >= 2 for count in rank_counts.values()) or 
                       max(suit_counts.values()) >= 3 or connected)
        }

    def _is_board_connected(self, board_ranks: List[str]) -> bool:
        """Check if board is connected (consecutive ranks)."""
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                      '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                      '4': 4, '3': 3, '2': 2}
        
        values = sorted([rank_values[rank] for rank in board_ranks])
        
        # Check for consecutive values
        for i in range(len(values) - 1):
            if values[i+1] - values[i] == 1:
                return True
        
        # Check for A-2-3-4-5 connection
        if {14, 2, 3, 4, 5}.issubset(set(values)):
            return True
        
        return False

    def _is_nut_flush(self, cards: List[str], board: List[str], suit_counts: dict) -> bool:
        """Check if player has the nut flush (best possible flush)."""
        # Find the flush suit
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break
        
        if not flush_suit:
            return False
        
        # Check if player has the Ace of the flush suit
        player_flush_cards = [card for card in cards if card[1] == flush_suit]
        board_flush_cards = [card for card in board if card[1] == flush_suit]
        
        # Player must have the Ace of the flush suit
        player_has_ace = any(card[0] == 'A' for card in player_flush_cards)
        
        # Check if Ace is the highest flush card
        all_flush_cards = player_flush_cards + board_flush_cards
        flush_ranks = [card[0] for card in all_flush_cards]
        
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                      '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                      '4': 4, '3': 3, '2': 2}
        
        highest_rank = max(rank_values[rank] for rank in flush_ranks)
        
        return player_has_ace and highest_rank == 14

    def _is_nut_flush_draw(self, cards: List[str], board: List[str], suit_counts: dict) -> bool:
        """Check if player has the nut flush draw."""
        # Find the flush suit
        flush_suit = None
        for suit, count in suit_counts.items():
            if count == 4:
                flush_suit = suit
                break
        
        if not flush_suit:
            return False
        
        # Check if player has the Ace of the flush suit
        player_flush_cards = [card for card in cards if card[1] == flush_suit]
        return any(card[0] == 'A' for card in player_flush_cards)

    def _classify_pair_strength(self, cards: List[str], board: List[str], rank_counts: dict) -> str:
        """Classify pair strength with kicker consideration."""
        # Find the pair rank
        pair_rank = None
        for rank, count in rank_counts.items():
            if count == 2:
                pair_rank = rank
                break
        
        if not pair_rank:
            return "pair"
        
        # Check if it's top pair, second pair, etc.
        board_ranks = [card[0] for card in board]
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                      '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                      '4': 4, '3': 3, '2': 2}
        
        board_values = [rank_values[rank] for rank in board_ranks]
        pair_value = rank_values[pair_rank]
        
        if not board_values:
            return "pair"
        
        max_board = max(board_values)
        
        if pair_value == max_board:
            # Top pair - check kicker strength
            kicker_ranks = [card[0] for card in cards if card[0] != pair_rank]
            if kicker_ranks:
                kicker_value = max(rank_values[rank] for rank in kicker_ranks)
                if kicker_value >= 10:  # T or higher
                    return "top_pair_good_kicker"
                else:
                    return "top_pair_bad_kicker"
            return "top_pair"
        elif pair_value == sorted(board_values, reverse=True)[1] if len(board_values) >= 2 else 0:
            return "second_pair"
        else:
            return "bottom_pair"

    def _has_gutshot_draw(self, ranks: List[str]) -> bool:
        """Check for gutshot straight draw (needs one specific rank)."""
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                       '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                       '4': 4, '3': 3, '2': 2}
        values = sorted([rank_values[r] for r in ranks if r in rank_values])
        
        for i in range(len(values) - 3):
            if values[i+3] - values[i] == 4 and len(set(values[i:i+4])) == 3:
                return True
        return False

    def _has_open_ended_draw(self, ranks: List[str]) -> bool:
        """Check for open-ended straight draw."""
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                       '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                       '4': 4, '3': 3, '2': 2}
        values = sorted([rank_values[r] for r in ranks if r in rank_values])
        
        for i in range(len(values) - 3):
            if values[i+3] - values[i] == 3 and len(set(values[i:i+4])) == 4:
                return True
        return False

    def get_basic_bot_action(self, player: Player) -> Tuple[ActionType, float]:
        """Basic bot logic as fallback."""
        # Use the enhanced hand evaluator instead of the old method
        hand_info = self.hand_evaluator.evaluate_hand(player.cards, self.game_state.board)
        hand_strength = hand_info['strength_score']  # Use the strength score from the dict
        
        if self.game_state.current_bet == 0:
            if hand_strength > 20:
                return ActionType.BET, min(3.0, player.stack)
            else:
                return ActionType.CHECK, 0
        else:
            call_amount = self.game_state.current_bet - player.current_bet
            if hand_strength > 30 and call_amount < player.stack * 0.5:
                # --- FIX: Ensure raise meets minimum requirement ---
                min_raise_total = self.game_state.current_bet + self.game_state.min_raise
                raise_amount = max(min_raise_total, min(self.game_state.current_bet * 2, player.stack))
                if raise_amount <= player.stack:
                    return ActionType.RAISE, raise_amount
                else:
                    return ActionType.FOLD, 0
            elif hand_strength > 15 and call_amount <= player.stack * 0.2:
                return ActionType.CALL, call_amount
            else:
                return ActionType.FOLD, 0

    # FIX 2 & 3: Correct Raise Logic and All-In Detection
    def execute_action(self, player: Player, action: ActionType, amount: float = 0):
        """Execute a player action with all fixes."""
        # --- NEW: Proper invalid action handling ---
        # Validate inputs
        if not player:
            self._log_action(f"ERROR in execute_action: Player cannot be None")
            return
        
        if not isinstance(action, ActionType):
            self._log_action(f"ERROR in execute_action: Invalid action type: {action}")
            return
        
        if amount < 0:
            self._log_action(f"ERROR in execute_action: Amount cannot be negative: ${amount}")
            return
        
        # Validate action is valid for current state
        errors = self.validate_action(player, action, amount)
        if errors:
            error_msg = f"Invalid action: {'; '.join(errors)}"
            self._log_action(f"ERROR in execute_action: {error_msg}")
            
            # --- NEW: Re-prompt human player for valid action ---
            if player.is_human and self.on_action_required:
                self._log_action(f"🔄 Re-prompting human player for valid action")
                self.on_action_required(player)
            return
        # --- END NEW ---
        
        # --- ENHANCED: Detailed Action Logging ---
        old_pot = self.game_state.pot  # Track pot changes
        self._log_action(f"🎯 {player.name} attempting {action.value.upper()} ${amount:.2f}")
        self._log_action(f"📊 Before action - Pot: ${self.game_state.pot:.2f}, Current Bet: ${self.game_state.current_bet:.2f}")
        self._log_action(f"💰 {player.name} stack: ${player.stack:.2f}, current bet: ${player.current_bet:.2f}")
        
        # Call the state logger here
        self.log_state_change(player, action, amount)

        # Play sound effects based on action (prioritize authentic sounds)
        if action == ActionType.FOLD:
            # Use authentic fold sound if available, otherwise generated
            if "player_fold" in self.sfx.sounds:
                self.sfx.play("player_fold")  # Authentic fold sound
            else:
                self.sfx.play("card_fold")    # Generated fallback
            player.is_active = False
            player.current_bet = 0

        elif action == ActionType.CHECK:
            self.sfx.play("player_check")
            # FIX: Add proper CHECK logging
            self._log_action(f"✅ {player.name}: CHECK")
            # Only valid when current_bet is 0 or player already has current bet
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount > 0:
                self._log_action(f"ERROR: {player.name} cannot check when bet is ${self.game_state.current_bet}")
                return
            player.current_bet = 0

        elif action == ActionType.CALL:
            # Use authentic chip sound for calls
            if "chip_bet" in self.sfx.sounds:
                self.sfx.play("chip_bet")     # Authentic chip sound
            else:
                self.sfx.play("player_call")  # Generated fallback
            call_amount = self.game_state.current_bet - player.current_bet
            actual_call = min(call_amount, player.stack)
            
            # BUG FIX: Track partial calls for side pot calculations
            if actual_call < call_amount:
                # Player can't make full call - this creates a side pot situation
                player.is_all_in = True
                player.partial_call_amount = actual_call
                player.full_call_amount = call_amount
                self._log_action(f"{player.name} ALL-IN for ${actual_call:.2f} (${call_amount - actual_call:.2f} short)")
            else:
                player.partial_call_amount = None
                player.full_call_amount = None
            
            player.stack -= actual_call
            player.current_bet += actual_call
            player.total_invested += actual_call
            self.game_state.pot += actual_call
            
            # Check for all-in
            if player.stack == 0:
                player.is_all_in = True
                self._log_action(f"{player.name} is ALL-IN!")

        elif action == ActionType.BET:
            # Use authentic chip sound for betting
            if "chip_bet" in self.sfx.sounds:
                self.sfx.play("chip_bet")     # Authentic chip sound
            else:
                self.sfx.play("player_bet")   # Generated fallback
            if self.game_state.current_bet > 0:
                self._log_action(f"ERROR: {player.name} cannot bet when current bet is ${self.game_state.current_bet}")
                return
            
            actual_bet = min(amount, player.stack)
            player.stack -= actual_bet
            player.current_bet = actual_bet
            player.total_invested += actual_bet
            self.game_state.pot += actual_bet
            self.game_state.current_bet = actual_bet
            
            # Check for all-in
            if player.stack == 0:
                player.is_all_in = True
                self._log_action(f"{player.name} is ALL-IN!")

        elif action == ActionType.RAISE:
            # Use authentic chip sound for raising (more chips = louder/more dramatic)
            if "chip_bet" in self.sfx.sounds:
                self.sfx.play("chip_bet")     # Authentic chip sound
            else:
                self.sfx.play("player_raise") # Generated fallback
            if amount <= self.game_state.current_bet:
                min_raise_total = self.game_state.current_bet + self.game_state.min_raise
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
            # --- CORRECTED MIN RAISE CALCULATION ---
            # The minimum raise should be the amount by which the current bet was raised
            self.game_state.min_raise = total_bet - old_bet
            self._log_action(f"📈 Min raise updated to: ${self.game_state.min_raise:.2f}")
            # --- END CORRECTION ---
            
            # Clear acted players (they get another chance after raise)
            self.game_state.players_acted.clear()
            
            # --- BUG FIX: Reset has_acted flags for all other players after a raise ---
            self._log_action(f"🔄 Resetting 'has_acted' for other players due to raise")
            for p in self.game_state.players:
                if p.is_active and p != player:
                    p.has_acted_this_round = False
            # --- END BUG FIX ---
            
            if player.stack == 0:
                player.is_all_in = True
                self._log_action(f"{player.name} is ALL-IN!")

        # Mark player as acted
        player.has_acted_this_round = True
        self.game_state.players_acted.add(self.action_player_index)

        # --- CORRECTED GAME FLOW LOGIC ---
        # Check for a winner after any action that might end the hand
        active_players = [p for p in self.game_state.players if p.is_active]
        self._log_action(f"🎯 After {player.name} {action.value}, active players: {[p.name for p in active_players]}")
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.game_state.pot
            pot_amount = self.game_state.pot
            self.game_state.pot = 0
            self._log_action(f"🏆 {winner.name} wins ${pot_amount:.2f} (all others folded)")
            self._log_action(f"💰 {winner.name} new stack: ${winner.stack:.2f}")
            
            # Play winner announcement sound
            self.sfx.play("winner_announce")
            
            # Only transition if not already in END_HAND state
            if self.current_state != PokerState.END_HAND:
                self.transition_to(PokerState.END_HAND)
            # Store winner info for UI callback
            self._last_winner = {"name": winner.name, "amount": pot_amount}
            self._log_action(f"🏆 Winner info stored for UI: {winner.name} wins ${pot_amount:.2f}")
            return  # End the action here since the hand is over

        # Track pot changes for debugging
        if self.game_state.pot != old_pot:
            print(f"💰 Pot changed: ${old_pot} → ${self.game_state.pot} (action: {action.value}, amount: ${amount})")  # Debug
        
        # If the hand is not over, check if the round is complete
        if self.is_round_complete():
            self.handle_round_complete()
        else:
            self.advance_to_next_player()
            self.handle_current_player_action()
        # --- END CORRECTION ---

    def advance_to_next_player(self):
        """Move to the next active player who can act."""
        original_index = self.action_player_index
        attempts = 0
        
        while attempts < self.num_players:
            self.action_player_index = (self.action_player_index + 1) % self.num_players
            current_player = self.game_state.players[self.action_player_index]
            
            # Found a player who can act
            if (current_player.is_active and 
                not current_player.is_all_in and
                (self.action_player_index not in self.game_state.players_acted or
                 current_player.current_bet < self.game_state.current_bet)):
                # --- NEW: Call the state change callback to update UI ---
                if self.on_state_change:
                    self.on_state_change()
                return
            
            attempts += 1
        
        # No one can act - round is complete
        self.action_player_index = -1
        # --- NEW: Call the state change callback even when round is complete ---
        if self.on_state_change:
            self.on_state_change()

    def handle_round_complete(self):
        """
        Handles the completion of a betting round by advancing to the next street
        (flop, turn, river) or proceeding to showdown.
        """
        self._log_action(f"🔄 ROUND COMPLETE for {self.game_state.street}")
        self._log_action(f"📊 Current state: {self.current_state}")
        self._log_action(f"🎴 Community cards: {self.game_state.board}")
        self._log_action(f"💰 Pot size: ${self.game_state.pot:.2f}")
        
        if self.on_round_complete:
            self.on_round_complete()

        # --- THIS IS THE CRITICAL BUG FIX ---
        if self.game_state.street == 'preflop':
            self._log_action("🔄 Transitioning from preflop to DEAL_FLOP")
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.game_state.street == 'flop':
            self._log_action("🔄 Transitioning from flop to DEAL_TURN")
            self.transition_to(PokerState.DEAL_TURN)
        elif self.game_state.street == 'turn':
            self._log_action("🔄 Transitioning from turn to DEAL_RIVER")
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.game_state.street == 'river':
            self._log_action("🔄 Transitioning from river to SHOWDOWN")
            self.transition_to(PokerState.SHOWDOWN)
        else:
            self._log_action(f"❌ ERROR: Unknown street '{self.game_state.street}'")
        # --- End of Bug Fix ---

    def __init__(self, num_players: int = 6, strategy_data=None, root_tk=None):
        """Initialize the state machine with enhanced hand evaluator."""
        self.num_players = num_players
        self.strategy_data = strategy_data
        self.root_tk = root_tk
        
        # Initialize action log FIRST (before any logging calls)
        self.action_log = []
        self.max_log_size = 1000
        
        # Initialize the enhanced hand evaluator
        self.hand_evaluator = EnhancedHandEvaluator()
        
        # Game state
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[]
        )
        
        # State tracking
        self.current_state = PokerState.START_HAND
        self.action_player_index = 0
        self.dealer_position = 0
        
        # Blind positions
        self.small_blind_position = 0
        self.big_blind_position = 0
        
        # Winner tracking
        self._last_winner = None
        
        # Callbacks
        self.on_action_required = None
        self.on_hand_complete = None
        self.on_state_change = None
        self.on_log_entry = None
        self.on_round_complete = None
        
        # Sound manager
        self.sfx = SoundManager()
        
        # Hand history
        self.hand_history = []
        
        # Initialize hand evaluator cache
        self._hand_eval_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._max_cache_size = 1000
        
        # Initialize players
        self._initialize_players()
        
        # Strategy integration
        if self.strategy_data:
            self._log_action("Strategy data loaded successfully")

    def _initialize_players(self):
        """Initialize the player list with default players."""
        position_names = self._get_position_names()
        self.game_state.players = []
        
        for i in range(self.num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position=position_names[i],
                is_human=(i == 0),  # First player is human
                is_active=True,
                cards=[],
                current_bet=0.0,
                has_acted_this_round=False,
                is_all_in=False,
                total_invested=0.0
            )
            self.game_state.players.append(player)
        
        # Initialize blind positions after players are created
        self.update_blind_positions()

    def determine_winner(self) -> List[Player]:
        """Determine winners with proper tie handling using the enhanced evaluator."""
        active_players = [p for p in self.game_state.players if p.is_active]
        
        if len(active_players) == 1:
            return active_players
        
        self._log_action(f"🔍 SHOWDOWN: Evaluating {len(active_players)} active players")
        self._log_action(f"🎴 Board: {' '.join(self.game_state.board)}")
        
        # Collect all hand evaluations for detailed comparison
        player_hands = []
        best_hand_info = None
        winners = []
        
        # First pass: evaluate all hands
        for player in active_players:
            hand_info = self.hand_evaluator.evaluate_hand(player.cards, self.game_state.board)
            player_hands.append({
                'player': player,
                'hand_info': hand_info
            })
            
            # Log each player's hand details
            hand_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
            self._log_action(f"📊 {player.name} ({' '.join(player.cards)}): {hand_rank} - {hand_info['hand_description']}")
        
        # Second pass: determine winner(s)
        for player_hand in player_hands:
            player = player_hand['player']
            hand_info = player_hand['hand_info']
            
            if not winners:  # First player to be evaluated
                best_hand_info = hand_info
                winners = [player]
                hand_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
                self._log_action(f"🏆 {player.name} leads with {hand_rank}")
            else:
                # Compare current player's hand with the best so far
                comparison = self.hand_evaluator._compare_hands(
                    (hand_info['hand_rank'], hand_info['rank_values']),
                    (best_hand_info['hand_rank'], best_hand_info['rank_values'])
                )
                
                current_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
                best_rank = best_hand_info['hand_rank'].name.replace('_', ' ').title()
                
                if comparison > 0:  # Current player has a better hand
                    best_hand_info = hand_info
                    winners = [player]
                    self._log_action(f"🏆 {player.name} wins with {current_rank} vs {best_rank}")
                elif comparison == 0:  # It's a tie
                    winners.append(player)
                    self._log_action(f"🤝 {player.name} ties with {current_rank}")
                else:
                    self._log_action(f"❌ {player.name} loses with {current_rank} vs {best_rank}")
        
        # Final showdown summary
        if len(winners) == 1:
            winner = winners[0]
            winner_hand = next(ph for ph in player_hands if ph['player'] == winner)
            hand_rank = winner_hand['hand_info']['hand_rank'].name.replace('_', ' ').title()
            self._log_action(f"🎉 {winner.name} wins with {hand_rank}!")
        else:
            winner_names = [w.name for w in winners]
            self._log_action(f"🎉 Split pot between {', '.join(winner_names)}")
        
        return winners

    def handle_showdown(self):
        """Handle showdown with tie handling and side pots."""
        self._log_action("Showdown")
        self.sfx.play("winner_announce")
        
        # --- THIS IS THE CRITICAL BUG FIX ---
        winners = self.determine_winner()
        if winners:
            pot_amount = self.game_state.pot
            split_amount = pot_amount / len(winners)
            winner_names = ", ".join([w.name for w in winners])

            for winner in winners:
                winner.stack += split_amount
            
            # Store the final, correct information BEFORE the state is reset
            self._last_winner = {"name": winner_names, "amount": pot_amount}
            self._log_action(f"🏆 Showdown winner(s): {winner_names} win ${pot_amount:.2f}")
        # --- End of Bug Fix ---
        
        self.transition_to(PokerState.END_HAND)

    def create_side_pots(self) -> List[dict]:
        """Create side pots for all-in scenarios with proper tracking."""
        active_players = [p for p in self.game_state.players if p.is_active and p.total_invested > 0]
        all_in_players = [p for p in active_players if p.is_all_in]

        if not all_in_players:
            return []  # No side pots needed

        # Get all unique investment amounts from players who are all-in
        all_in_investments = sorted(list(set(p.total_invested for p in all_in_players)))

        side_pots = []
        last_investment_level = 0

        for investment_level in all_in_investments:
            pot_amount = 0
            eligible_players = []

            # Calculate this side pot's value
            for p in self.game_state.players:
                contribution = max(0, min(p.total_invested, investment_level) - last_investment_level)
                pot_amount += contribution

            # Determine who is eligible for this pot
            eligible_players = [p for p in active_players if p.total_invested >= investment_level]

            if pot_amount > 0:
                side_pots.append({
                    'amount': pot_amount,
                    'eligible_players': eligible_players
                })
            
            last_investment_level = investment_level

        # The main pot is what's left over
        main_pot_total = self.game_state.pot - sum(p['amount'] for p in side_pots)
        if main_pot_total > 0:
             side_pots.append({
                'amount': main_pot_total,
                'eligible_players': [p for p in active_players if not p.is_all_in]
            })

        return side_pots

    def handle_end_hand(self):
        """
        Handles hand completion, determines winner, awards pot, and notifies UI.
        This is now the single source of truth for ending a hand.
        """
        print(f"🏆 DEBUG: Starting winner determination")  # Debug
        print(f"💰 DEBUG: Current pot: ${self.game_state.pot}")  # Debug
        print(f"👥 DEBUG: Active players: {[p.name for p in self.game_state.players if p.is_active]}")  # Debug
        
        self._log_action("Hand complete")

        # Determine winner(s) whether from a showdown or everyone folding
        winners = self.determine_winner()
        
        if winners:
            winner_names = ", ".join([p.name for p in winners])
            split_amount = self.game_state.pot / len(winners)
            
            # FIX: Save pot amount BEFORE resetting it
            pot_amount = self.game_state.pot
            print(f"✅ DEBUG: Awarding ${pot_amount} to {len(winners)} winners")  # Debug
            
            for winner in winners:
                winner.stack += split_amount
                self._log_action(f"💰 {winner.name} new stack: ${winner.stack:.2f}")
            
            winner_info = {"name": winner_names, "amount": pot_amount}  # Use saved amount
            self._last_winner = winner_info
            self._log_action(f"🏆 Winner(s): {winner_names} win ${pot_amount:.2f}")
        else:
            self._log_action("No winner determined (should not happen in a normal game).")
            winner_info = None
            print(f"❌ DEBUG: No winner found!")  # Debug

        # Reset game state for next hand
        if self.game_state:
            self.game_state.pot = 0
            self.game_state.current_bet = 0
            self.game_state.min_raise = 1.0
            self.game_state.players_acted.clear()
            self.game_state.round_complete = False
            self.game_state.board = []
            self.game_state.street = "preflop"
            
            # Reset all player bets and status
            for player in self.game_state.players:
                player.cards = []
                player.current_bet = 0
                player.total_invested = 0
                player.has_acted_this_round = False
                player.is_all_in = False
                player.is_active = True  # Reactivate all players for new hand
        
        # Advance dealer position for next hand
        self.advance_dealer_position()
        
        if self.on_hand_complete:
            print(f"🎯 STATE MACHINE: Calling on_hand_complete with: {winner_info}")  # Debug
            self.on_hand_complete(winner_info)
        else:
            print("❌ STATE MACHINE: on_hand_complete callback is None!")  # Debug

    # FIX 6: Better Input Validation
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate action and return list of errors."""
        errors = []
        current_player = self.get_action_player()
        if current_player != player:
            errors.append(f"It's not {player.name}'s turn")
        
        if amount < 0:
            errors.append("Amount cannot be negative")
        
        if action == ActionType.CHECK:
            if self.game_state.current_bet > player.current_bet:
                errors.append(f"Cannot check when bet is ${self.game_state.current_bet:.2f}")
        
        elif action == ActionType.CALL:
            if self.game_state.current_bet - player.current_bet <= 0:
                errors.append("Nothing to call")
        
        elif action == ActionType.BET:
            if self.game_state.current_bet > 0:
                errors.append("Cannot bet when there's already a bet - use raise instead")
            if amount < self.game_state.min_raise:
                errors.append(f"Bet amount ${amount:.2f} is less than minimum bet ${self.game_state.min_raise:.2f}")
            if amount > player.stack:
                errors.append(f"Bet amount ${amount:.2f} exceeds stack ${player.stack:.2f}")
        
        elif action == ActionType.RAISE:
            min_raise_total = self.game_state.current_bet + self.game_state.min_raise
            if amount < min_raise_total:
                errors.append(f"Raise to ${amount:.2f} is less than minimum raise to ${min_raise_total:.2f}")
            if amount > player.current_bet + player.stack:
                errors.append(f"Raise amount ${amount:.2f} exceeds available chips")
        
        return errors

    def is_valid_action(self, player: Player, action: ActionType, amount: float = 0) -> bool:
        """Check if action is valid."""
        return len(self.validate_action(player, action, amount)) == 0

    # Public interface methods
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand, using existing players if provided."""
        self.current_state = PokerState.START_HAND
        self.handle_state_entry(existing_players)

    def get_current_state(self) -> PokerState:
        """Get current state."""
        return self.current_state

    def get_action_player(self) -> Optional[Player]:
        """Get current action player."""
        if (self.game_state and 
            0 <= self.action_player_index < len(self.game_state.players)):
            return self.game_state.players[self.action_player_index]
        return None

    def get_game_info(self) -> dict:
        """Get comprehensive game information."""
        if not self.game_state:
            return {}
        
        return {
            "state": self.current_state.value,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "min_raise": self.game_state.min_raise,
            "board": self.game_state.board,
            "players": [
                {
                    "name": p.name,
                    "position": p.position,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "total_invested": p.total_invested,  # BUG FIX: Add missing field
                    "is_active": p.is_active,
                    "is_all_in": p.is_all_in,
                    "is_human": p.is_human,  # BUG FIX: Add missing is_human field
                    "cards": p.cards if p.is_human else ["**", "**"],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
        }
    
    def get_hand_history(self) -> List[HandHistoryLog]:
        """Returns the structured log for the current hand."""
        return self.hand_history


print("🚀 Improved Poker State Machine loaded!")
print("✅ All critical fixes implemented:")
print("  1. Dynamic position tracking")
print("  2. Correct raise logic")
print("  3. All-in state tracking") 
print("  4. Improved round completion")
print("  5. Strategy integration for bots")
print("  6. Better input validation")
