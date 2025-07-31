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

    def __init__(self, num_players: int = 6, strategy_data=None):
        self.current_state = PokerState.START_HAND
        self.game_state = None
        self.action_player_index = 0
        self.num_players = num_players
        self.strategy_data = strategy_data  # NEW: Strategy integration

        # FIX 1: Dynamic position tracking
        self.dealer_position = 0
        self.update_blind_positions()  # Calculate blind positions based on num_players
        self.position_names = self._get_position_names()

        # Callbacks for UI updates
        self.on_state_change = None
        self.on_action_required = None
        self.on_round_complete = None
        self.on_hand_complete = None

        # Logging with size limit
        self.action_log = []
        self.max_log_size = 1000  # Limit log size
        
        # Add caching for performance
        self._hand_eval_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._max_cache_size = 10000

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

    def log_action(self, message: str):
        """Log an action with timestamp and size limit."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.action_log.append(log_entry)
        
        # Prevent unbounded growth
        if len(self.action_log) > self.max_log_size:
            self.action_log = self.action_log[-self.max_log_size:]
        
        print(log_entry)

    def transition_to(self, new_state: PokerState):
        """Transition to a new state with validation."""
        if new_state in self.STATE_TRANSITIONS[self.current_state]:
            old_state = self.current_state
            self.current_state = new_state
            self.log_action(f"STATE TRANSITION: {old_state.value} → {new_state.value}")
            if self.on_state_change:
                self.on_state_change(new_state)
            self.handle_state_entry()
        else:
            raise ValueError(
                f"Invalid state transition: {self.current_state.value} → {new_state.value}"
            )

    def handle_state_entry(self, existing_players: Optional[List[Player]] = None):
        """Handle specific logic for each state entry."""
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
        self.log_action("Starting new hand")

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
            self.log_action("Insufficient stacks for blinds; ending game")
            self.transition_to(PokerState.END_HAND)
            return

        sb_player.stack -= sb_amount
        sb_player.current_bet = sb_amount
        sb_player.total_invested = sb_amount

        bb_player.stack -= bb_amount
        bb_player.current_bet = bb_amount
        bb_player.total_invested = bb_amount

        self.game_state.pot = sb_amount + bb_amount
        self.game_state.current_bet = bb_amount
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

    def handle_preflop_betting(self):
        """Handle preflop betting round."""
        self.log_action("Preflop betting round")
        self.game_state.street = "preflop"
        self.reset_round_tracking()

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
        self.log_action("Dealing flop")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        # Deal 3 community cards
        for _ in range(3):
            self.game_state.board.append(self.deal_card())

        self.prepare_new_betting_round()
        self.transition_to(PokerState.FLOP_BETTING)

    def handle_deal_turn(self):
        """Deal the turn."""
        self.log_action("Dealing turn")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        self.game_state.board.append(self.deal_card())
        self.prepare_new_betting_round()
        self.transition_to(PokerState.TURN_BETTING)

    def handle_deal_river(self):
        """Deal the river."""
        self.log_action("Dealing river")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        self.game_state.board.append(self.deal_card())
        self.prepare_new_betting_round()
        self.transition_to(PokerState.RIVER_BETTING)

    def prepare_new_betting_round(self):
        """Prepare for new betting round."""
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = 1.0
        self.reset_round_tracking()

        # Reset current bets (but keep total invested)
        for player in self.game_state.players:
            player.current_bet = 0.0

        # Set action to first active player after button
        self.set_action_to_first_active_after_button()

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
        self.log_action("Flop betting round")
        self.game_state.street = "flop"
        self._handle_betting_round(PokerState.DEAL_TURN)

    def handle_turn_betting(self):
        """Handle turn betting round."""
        self.log_action("Turn betting round")
        self.game_state.street = "turn"
        self._handle_betting_round(PokerState.DEAL_RIVER)

    def handle_river_betting(self):
        """Handle river betting round."""
        self.log_action("River betting round")
        self.game_state.street = "river"
        self._handle_betting_round(PokerState.SHOWDOWN)

    def _handle_betting_round(self, next_state: PokerState):
        """Generic betting round handler."""
        if self.is_round_complete():
            self.transition_to(next_state)
        else:
            self.handle_current_player_action()

    # FIX 4: Improved Round Completion Logic
    def is_round_complete(self) -> bool:
        """Check if betting round is complete with all-in handling."""
        active_players = [p for p in self.game_state.players if p.is_active]
        
        # Only one player left
        if len(active_players) <= 1:
            return True

        # Players who can still act (not folded, not all-in)
        can_act_players = [p for p in active_players if not p.is_all_in]
        
        # Everyone is all-in - go to showdown
        if len(can_act_players) == 0:
            return True

        # Only one player can act and they've acted - round complete
        if len(can_act_players) == 1:
            player_index = next(i for i, p in enumerate(self.game_state.players) 
                              if p.is_active and not p.is_all_in)
            return player_index in self.game_state.players_acted

        # Check if all players who can act have acted and bets are equal
        can_act_indices = [i for i, p in enumerate(self.game_state.players) 
                          if p.is_active and not p.is_all_in]
        
        all_acted = all(i in self.game_state.players_acted for i in can_act_indices)
        
        # Special case for preflop: BB gets option to raise if everyone just called
        if (self.game_state.street == "preflop" and 
            self.big_blind_position not in self.game_state.players_acted and
            self.game_state.current_bet == 1.0):  # Only calls, no raises
            # Check if BB can actually raise (has sufficient stack)
            bb_player = self.game_state.players[self.big_blind_position]
            if bb_player.stack >= self.game_state.min_raise:
                return False
            # BB can't raise, so round is complete
            return True

        # Check if bets are equal among players who can act
        target_bet = self.game_state.current_bet
        bets_equal = all(p.current_bet == target_bet for p in can_act_players)
        
        return all_acted and bets_equal

    def handle_current_player_action(self):
        """Handle the current player's action."""
        if self.action_player_index == -1:
            return

        current_player = self.game_state.players[self.action_player_index]

        if current_player.is_human:
            self.log_action(f"Human turn: {current_player.name}")
            if self.on_action_required:
                self.on_action_required(current_player)
        else:
            self.log_action(f"Bot turn: {current_player.name}")
            self.execute_bot_action(current_player)

    # FIX 5: Strategy Integration for Bots
    def execute_bot_action(self, player: Player):
        """Execute bot action using strategy data."""
        if self.strategy_data:
            action, amount = self.get_strategy_action(player)
        else:
            action, amount = self.get_basic_bot_action(player)
        
        self.execute_action(player, action, amount)

    def get_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get bot action using strategy data with proper hand strength calculation."""
        street = self.game_state.street
        position = player.position
        
        try:
            if street == "preflop":
                # Use preflop hand strength table from strategy
                hand_strength = self.get_preflop_hand_strength(player.cards)
                thresholds = self.strategy_data.strategy_dict.get("preflop", {}).get("open_rules", {})
                threshold = thresholds.get(position, {}).get("threshold", 20)
                sizing = thresholds.get(position, {}).get("sizing", 3.0)
                
                if hand_strength >= threshold:
                    if self.game_state.current_bet == 0:
                        return ActionType.BET, min(sizing, player.stack)
                    else:
                        call_amount = self.game_state.current_bet - player.current_bet
                        if call_amount <= player.stack * 0.2:  # Don't call too much
                            return ActionType.CALL, call_amount
                        else:
                            return ActionType.FOLD, 0
                else:
                    return ActionType.FOLD, 0
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
                
                if hand_strength >= val_thresh:
                    if self.game_state.current_bet == 0:
                        bet_amount = min(self.game_state.pot * sizing, player.stack)
                        return ActionType.BET, bet_amount
                    else:
                        return ActionType.CALL, call_amount
                elif hand_strength >= check_thresh:
                    if self.game_state.current_bet == 0:
                        return ActionType.CHECK, 0
                    else:
                        if call_amount <= player.stack * 0.1:
                            return ActionType.CALL, call_amount
                        else:
                            return ActionType.FOLD, 0
                else:
                    if self.game_state.current_bet == 0:
                        return ActionType.CHECK, 0
                    else:
                        return ActionType.FOLD, 0
        except (KeyError, AttributeError):
            # Fall back to basic logic if strategy data is malformed
            pass
        
        return self.get_basic_bot_action(player)

    def get_preflop_hand_strength(self, cards: List[str]) -> int:
        """Get preflop hand strength using strategy table."""
        if not self.strategy_data or not hasattr(self.strategy_data, 'strategy_dict'):
            # BUG FIX: evaluate_hand returns tuple, so unpack it
            hand_strength, _ = self.evaluate_hand(cards, [])
            return hand_strength
        
        # Convert cards to hand notation (e.g., "AA", "AKs", "72o")
        # Sort by poker rank, not alphabetically
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                       '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                       '4': 4, '3': 3, '2': 2}
        ranks = sorted([card[0] for card in cards], 
                      key=lambda r: rank_values.get(r, 0), reverse=True)
        suited = cards[0][1] == cards[1][1]
        
        # BUG FIX: Pocket pairs don't need 's' or 'o' suffix
        if ranks[0] == ranks[1]:
            hand_notation = f"{ranks[0]}{ranks[1]}"  # e.g., "AA", "KK"
        else:
            hand_notation = f"{ranks[0]}{ranks[1]}{'s' if suited else 'o'}"  # e.g., "AKs", "AKo"
        
        # Look up in preflop table (correct path)
        preflop_table = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("preflop", {})
        return preflop_table.get(hand_notation, 0)

    def get_postflop_hand_strength(self, cards: List[str], board: List[str]) -> int:
        """Get postflop hand strength using strategy table."""
        if not self.strategy_data or not hasattr(self.strategy_data, 'strategy_dict'):
            # BUG FIX: Unpack the tuple
            score, _ = self.evaluate_hand(cards, board)
            return score
        
        # Classify hand type and look up in postflop table
        hand_type = self.classify_hand(cards, board)
        postflop_table = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("postflop", {})
        
        # BUG FIX: Provide default values for missing hand types
        default_strengths = {
            "top_pair_good_kicker": 35,
            "top_pair_bad_kicker": 25, 
            "second_pair": 20,
            "bottom_pair": 10,
            "pair": 15  # Fallback
        }
        
        strength = postflop_table.get(hand_type, default_strengths.get(hand_type, 0))
        return strength

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
        hand_strength, _ = self.evaluate_hand(player.cards, self.game_state.board)
        
        if self.game_state.current_bet == 0:
            if hand_strength > 20:
                return ActionType.BET, min(3.0, player.stack)
            else:
                return ActionType.CHECK, 0
        else:
            call_amount = self.game_state.current_bet - player.current_bet
            if hand_strength > 30 and call_amount < player.stack * 0.5:
                raise_amount = min(self.game_state.current_bet * 2, player.stack)
                return ActionType.RAISE, raise_amount
            elif hand_strength > 15 and call_amount <= player.stack * 0.2:
                return ActionType.CALL, call_amount
            else:
                return ActionType.FOLD, 0

    # FIX 2 & 3: Correct Raise Logic and All-In Detection
    def execute_action(self, player: Player, action: ActionType, amount: float = 0):
        """Execute a player action with all fixes."""
        try:
            # Validate inputs
            if not player:
                raise ValueError("Player cannot be None")
            if not isinstance(action, ActionType):
                raise ValueError(f"Invalid action type: {action}")
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            
            # Validate action is valid for current state
            errors = self.validate_action(player, action, amount)
            if errors:
                raise ValueError(f"Invalid action: {'; '.join(errors)}")
            
            self.log_action(f"{player.name}: {action.value.upper()} ${amount:.2f}")
            
        except Exception as e:
            self.log_action(f"ERROR in execute_action: {e}")
            return

        if action == ActionType.FOLD:
            player.is_active = False
            player.current_bet = 0

        elif action == ActionType.CHECK:
            # Only valid when current_bet is 0
            if self.game_state.current_bet != 0:
                self.log_action(f"ERROR: {player.name} cannot check when bet is ${self.game_state.current_bet}")
                return
            player.current_bet = 0

        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            actual_call = min(call_amount, player.stack)
            
            # BUG FIX: Track partial calls for side pot calculations
            if actual_call < call_amount:
                # Player can't make full call - this creates a side pot situation
                player.is_all_in = True
                player.partial_call_amount = actual_call
                player.full_call_amount = call_amount
                self.log_action(f"{player.name} ALL-IN for ${actual_call:.2f} (${call_amount - actual_call:.2f} short)")
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
                self.log_action(f"{player.name} is ALL-IN!")

        elif action == ActionType.BET:
            if self.game_state.current_bet > 0:
                self.log_action(f"ERROR: {player.name} cannot bet when current bet is ${self.game_state.current_bet}")
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
                self.log_action(f"{player.name} is ALL-IN!")

        elif action == ActionType.RAISE:
            if amount <= self.game_state.current_bet:
                min_raise_total = self.game_state.current_bet + self.game_state.min_raise
                self.log_action(f"ERROR: Minimum raise is ${min_raise_total:.2f}")
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
            
            # Clear acted players (they get another chance after raise)
            self.game_state.players_acted.clear()
            
            if player.stack == 0:
                player.is_all_in = True
                self.log_action(f"{player.name} is ALL-IN!")

        # Mark player as acted
        player.has_acted_this_round = True
        self.game_state.players_acted.add(self.action_player_index)

        # Move to next player or check round completion
        if not self.is_round_complete():
            self.advance_to_next_player()
            self.handle_current_player_action()
        else:
            self.handle_round_complete()

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
                return
            
            attempts += 1
        
        # No one can act - round is complete
        self.action_player_index = -1

    def handle_round_complete(self):
        """Handle round completion."""
        self.log_action("Round complete")
        if self.on_round_complete:
            self.on_round_complete()

        state_transitions = {
            PokerState.PREFLOP_BETTING: PokerState.DEAL_FLOP,
            PokerState.FLOP_BETTING: PokerState.DEAL_TURN,
            PokerState.TURN_BETTING: PokerState.DEAL_RIVER,
            PokerState.RIVER_BETTING: PokerState.SHOWDOWN,
        }
        
        next_state = state_transitions.get(self.current_state)
        if next_state:
            self.transition_to(next_state)

    def evaluate_hand_cached(self, player_cards: List[str], board: List[str]) -> Tuple[int, List[int]]:
        """Cached version of hand evaluation."""
        # Create cache key
        cache_key = tuple(sorted(player_cards + board))
        
        # Check cache
        if cache_key in self._hand_eval_cache:
            self._cache_hits += 1
            return self._hand_eval_cache[cache_key]
        
        # Cache miss - evaluate
        self._cache_misses += 1
        result = self.evaluate_hand(player_cards, board)
        
        # Add to cache if not too big
        if len(self._hand_eval_cache) < self._max_cache_size:
            self._hand_eval_cache[cache_key] = result
        else:
            # Simple cache eviction - remove oldest entries
            if len(self._hand_eval_cache) > 0:
                # Remove first 10% of cache
                keys_to_remove = list(self._hand_eval_cache.keys())[:self._max_cache_size // 10]
                for key in keys_to_remove:
                    del self._hand_eval_cache[key]
            self._hand_eval_cache[cache_key] = result
        
        return result

    def evaluate_hand(self, player_cards: List[str], board: List[str]) -> Tuple[int, List[int]]:
        """Enhanced hand evaluation with kickers for proper tiebreaking."""
        all_cards = player_cards + board
        
        # Count cards by rank and suit
        rank_counts = {}
        suit_counts = {}
        
        for card in all_cards:
            rank, suit = card[0], card[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        score = 0
        
        # Hand rankings
        rank_values = sorted(rank_counts.values(), reverse=True)
        
        # Get top 5 cards for kickers (including board)
        rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                      '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                      '4': 4, '3': 3, '2': 2}
        kickers = []
        for c in all_cards:
            if c[0] in rank_order:
                kickers.append(rank_order[c[0]])
            else:
                try:
                    kickers.append(int(c[0]))
                except ValueError:
                    continue  # Skip invalid cards
        kickers = sorted(kickers, reverse=True)[:5]
        
        # Four of a kind
        if 4 in rank_values:
            score += 800
        # Full house
        elif 3 in rank_values and 2 in rank_values:
            score += 700
        # Flush
        elif max(suit_counts.values()) >= 5:
            score += 600
        # Straight (simplified check)
        elif self._has_straight(list(rank_counts.keys())):
            score += 500
        # Three of a kind
        elif 3 in rank_values:
            score += 300
        # Two pair
        elif rank_values.count(2) >= 2:
            score += 200
        # One pair
        elif 2 in rank_values:
            score += 100
        
        return max(score, 1), kickers

    def get_hand_strength_percentile(self, hand_strength: int) -> float:
        """Convert raw hand strength to percentile (0-100)."""
        # Define strength brackets based on hand rankings
        strength_brackets = {
            0: 0,      # No hand
            100: 20,   # One pair
            200: 40,   # Two pair  
            300: 60,   # Three of a kind
            500: 75,   # Straight
            600: 85,   # Flush
            700: 95,   # Full house
            800: 99,   # Four of a kind
            1000: 100  # Straight flush
        }
        
        # Find the appropriate bracket
        for min_strength, percentile in sorted(strength_brackets.items()):
            if hand_strength <= min_strength:
                return percentile
        
        return 100  # Royal flush territory

    def calculate_pot_odds(self, call_amount: float) -> float:
        """Calculate pot odds for a call decision."""
        if call_amount <= 0:
            return float('inf')  # Can check for free
        
        # Pot odds = (pot + opponent bets) : call_amount
        total_pot = self.game_state.pot + call_amount
        pot_odds = total_pot / call_amount
        return pot_odds

    def estimate_hand_equity(self, player_cards: List[str], board: List[str], 
                            num_opponents: int) -> float:
        """Estimate winning probability against opponents."""
        # This is a simplified equity calculation
        # In a real implementation, you'd use Monte Carlo simulation
        
        # Get base hand strength
        hand_strength, _ = self.evaluate_hand(player_cards, board)
        
        # Convert to rough win probability (0-1)
        base_equity = hand_strength / 1000.0
        
        # Adjust for number of opponents
        # More opponents = lower chance of winning
        equity = base_equity ** (0.8 + (num_opponents * 0.2))
        
        # Add some adjustments based on board texture
        if board:
            # Check for dangerous boards
            suits = [card[1] for card in board]
            ranks = [card[0] for card in board]
            
            # Flush-heavy board
            if max(suits.count(s) for s in set(suits)) >= 3:
                equity *= 0.9  # Reduce equity on flush boards
            
            # Straight-heavy board  
            if self._is_board_connected(ranks):
                equity *= 0.9  # Reduce equity on connected boards
            
            # Paired board
            if len(set(ranks)) < len(ranks):
                equity *= 0.95  # Slightly reduce on paired boards
        
        return max(0.05, min(0.95, equity))  # Cap between 5% and 95%

    def should_call_by_pot_odds(self, player: Player, call_amount: float) -> bool:
        """Determine if calling is profitable based on pot odds."""
        pot_odds = self.calculate_pot_odds(call_amount)
        
        # Estimate our equity
        active_opponents = len([p for p in self.game_state.players 
                              if p.is_active and p != player])
        equity = self.estimate_hand_equity(player.cards, self.game_state.board, 
                                          active_opponents)
        
        # Need equity > 1/(pot_odds + 1) to make calling profitable
        required_equity = 1 / (pot_odds + 1)
        
        return equity >= required_equity

    def _has_straight(self, ranks: List[str]) -> bool:
        """Fixed straight detection with proper duplicate handling."""
        rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                      '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        
        # BUG FIX: Use set to remove duplicates
        values = sorted(set(rank_values[rank] for rank in ranks if rank in rank_values))
        
        # Check for regular straights
        for i in range(len(values) - 4):
            # Check if we have 5 consecutive values
            consecutive = True
            for j in range(4):
                if values[i+j+1] - values[i+j] != 1:
                    consecutive = False
                    break
            if consecutive:
                return True
        
        # Check for A-2-3-4-5 straight (wheel)
        if set([14, 2, 3, 4, 5]).issubset(set(values)):
            return True
        
        return False

    def determine_winner(self) -> List[Player]:
        """Determine winners with proper tie handling using kickers."""
        active_players = [p for p in self.game_state.players if p.is_active]
        
        if len(active_players) == 1:
            return active_players
        
        best_score = (-1, [])
        winners = []
        
        for player in active_players:
            score, kickers = self.evaluate_hand(player.cards, self.game_state.board)
            if (score, kickers) > best_score:
                best_score = (score, kickers)
                winners = [player]
            elif (score, kickers) == best_score:
                winners.append(player)
        
        return winners

    def handle_showdown(self):
        """Handle showdown with tie handling and side pots."""
        self.log_action("Showdown")
        
        # Create side pots if needed
        side_pots = self.create_side_pots()
        
        if side_pots:
            # Handle side pots
            for pot_info in side_pots:
                eligible_players = pot_info['eligible_players']
                pot_amount = pot_info['amount']
                
                if len(eligible_players) == 1:
                    winner = eligible_players[0]
                    winner.stack += pot_amount
                    self.log_action(f"{winner.name} wins side pot ${pot_amount:.2f}")
                else:
                    # Determine winners for this pot
                    pot_winners = self.determine_winner()
                    pot_winners = [w for w in pot_winners if w in eligible_players]
                    
                    if pot_winners:
                        split_amount = pot_amount / len(pot_winners)
                        for winner in pot_winners:
                            winner.stack += split_amount
                            self.log_action(f"{winner.name} wins ${split_amount:.2f} from side pot")
        else:
            # No side pots, normal showdown
            winners = self.determine_winner()
            if winners:
                split_amount = self.game_state.pot / len(winners)
                for winner in winners:
                    winner.stack += split_amount
                    self.log_action(f"{winner.name} wins ${split_amount:.2f}")
        
        self.transition_to(PokerState.END_HAND)

    def create_side_pots(self) -> List[dict]:
        """Create side pots for all-in scenarios with proper tracking."""
        active_players = [p for p in self.game_state.players if p.is_active and p.total_invested > 0]
        all_in_players = [p for p in active_players if p.is_all_in]
        
        if not all_in_players:
            return []  # No side pots needed
        
        # Sort players by their total investment (ascending)
        sorted_players = sorted(active_players, key=lambda p: p.total_invested)
        
        side_pots = []
        previous_investment = 0
        
        for i, player in enumerate(sorted_players):
            current_investment = player.total_invested
            
            # BUG FIX: Consider partial calls in side pot calculations
            if player.partial_call_amount is not None:
                effective_investment = player.partial_call_amount
            else:
                effective_investment = current_investment
            
            if effective_investment > previous_investment:
                pot_amount = 0
                eligible_players = []
                
                # Calculate pot amount for this level
                for p in active_players:
                    # Use partial call amount if available
                    p_effective_investment = (p.partial_call_amount if p.partial_call_amount is not None 
                                           else p.total_invested)
                    
                    if p_effective_investment >= effective_investment:
                        # Player contributes to this pot level
                        contribution = min(effective_investment - previous_investment, 
                                        p_effective_investment - previous_investment)
                        pot_amount += contribution
                        eligible_players.append(p)
                
                if pot_amount > 0:
                    side_pots.append({
                        'amount': pot_amount,
                        'eligible_players': eligible_players,
                        'level': effective_investment,
                        'partial_call': player.partial_call_amount is not None
                    })
                previous_investment = effective_investment
        
        # BUG FIX: Reset partial call amounts after creating side pots
        for player in self.game_state.players:
            player.partial_call_amount = None
            player.full_call_amount = None
        
        return side_pots

    def handle_end_hand(self):
        """Handle hand completion."""
        self.log_action("Hand complete")
        
        # Advance dealer position for next hand
        self.advance_dealer_position()
        
        if self.on_hand_complete:
            self.on_hand_complete()

    # FIX 6: Better Input Validation
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate action and return list of errors."""
        errors = []
        
        # Add check for current player
        current_player = self.get_action_player()
        if current_player != player:
            errors.append(f"It's not {player.name}'s turn")
        
        if amount < 0:
            errors.append("Amount cannot be negative")
        
        if action == ActionType.CHECK:
            if self.game_state.current_bet > 0:
                errors.append(f"Cannot check when bet is ${self.game_state.current_bet:.2f}")
        
        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount <= 0:
                errors.append("Nothing to call")
            elif call_amount > player.stack:
                errors.append(f"Call amount ${call_amount:.2f} exceeds stack ${player.stack:.2f}")
            # Note: amount parameter is ignored for CALL - it's calculated automatically
        
        elif action == ActionType.BET:
            if self.game_state.current_bet > 0:
                errors.append("Cannot bet when there's already a bet - use raise instead")
            elif amount <= 0:
                errors.append("Bet amount must be greater than 0")
            elif amount > player.stack:
                errors.append(f"Bet amount ${amount:.2f} exceeds stack ${player.stack:.2f}")
        
        elif action == ActionType.RAISE:
            min_raise_total = self.game_state.current_bet + self.game_state.min_raise
            if amount <= self.game_state.current_bet:
                errors.append(f"Raise must be more than current bet ${self.game_state.current_bet:.2f}")
            elif amount < min_raise_total:
                errors.append(f"Minimum raise is ${min_raise_total:.2f}")
            elif amount > player.current_bet + player.stack:
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
                    "cards": p.cards if p.is_human else ["**", "**"],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
        }


# Maintain compatibility with existing code
PokerStateMachine = ImprovedPokerStateMachine

print("🚀 Improved Poker State Machine loaded!")
print("✅ All critical fixes implemented:")
print("  1. Dynamic position tracking")
print("  2. Correct raise logic")
print("  3. All-in state tracking") 
print("  4. Improved round completion")
print("  5. Strategy integration for bots")
print("  6. Better input validation")
