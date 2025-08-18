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

    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"


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
class RoundState:
    """Per-street betting state (reset on each street)."""
    last_full_raise_size: float = 0.0
    last_aggressor_idx: Optional[int] = None
    reopen_available: bool = True   # becomes False after short all-in that doesn't meet full-raise size


@dataclass
class GameState:
    """Enhanced game state with proper pot accounting."""

    players: List[Player]
    board: List[str]
    # Pot accounting is split:
    # - committed_pot: sum of completed streets (finalized at street end)
    # - current_bet: highest per-player commitment on THIS street
    committed_pot: float = 0.0
    current_bet: float = 0.0
    street: str = "preflop"
    players_acted: Set[int] = field(default_factory=set)
    round_complete: bool = False
    deck: List[str] = field(default_factory=list)
    big_blind: float = 1.0
    _round_state: RoundState = field(default_factory=RoundState)

    def displayed_pot(self) -> float:
        """What the UI should show right now."""
        return self.committed_pot + sum(p.current_bet for p in self.players)

    @property
    def round_state(self) -> RoundState:
        return self._round_state

    @round_state.setter
    def round_state(self, rs: RoundState) -> None:
        self._round_state = rs
