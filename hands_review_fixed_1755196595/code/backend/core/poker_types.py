"""
Shared types for the poker state machine components.

This module contains the shared data structures and enums
to avoid circular imports between components.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Set


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
    has_folded: bool = False  # NEW: Track folded state for accurate counting
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
    big_blind: float = 1.0
    # NEW: Track the size of the last raise for under-raise validation
    last_raise_amount: float = 0.0
    # NEW: Track the amount of the last valid, action-reopening raise
    last_full_raise_amount: float = 0.0
    last_action_details: str = ""  # NEW: Track the last action for UI feedback
