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


# Import unified ActionType from hand_model to avoid enum mismatch issues
from .hand_model import ActionType


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
    # NEW: explicit driver for betting flow & termination
    need_action_from: Set[int] = field(default_factory=set)


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
    # *** FIX: Add action_player for GTO adapter compatibility ***
    action_player: Optional[int] = None

    def displayed_pot(self) -> float:
        """What the UI should show right now."""
        return self.committed_pot + sum(p.current_bet for p in self.players)

    @property
    def round_state(self) -> RoundState:
        return self._round_state

    @round_state.setter
    def round_state(self, rs: RoundState) -> None:
        self._round_state = rs

    def get_legal_actions(self) -> Set[ActionType]:
        """
        *** FIX: Get legal actions for GTO adapter compatibility ***
        
        This is a simplified implementation that returns basic legal actions.
        For full validation, the PPSM's _is_valid_action method should be used.
        """
        if self.action_player is None or self.action_player < 0:
            return set()  # No one to act
        
        if self.action_player >= len(self.players):
            return set()  # Invalid player index
        
        player = self.players[self.action_player]
        
        # Basic checks
        if player.has_folded or not player.is_active or player.stack == 0:
            return set()
        
        legal_actions = set()
        
        # FOLD is always legal when facing action
        legal_actions.add(ActionType.FOLD)
        
        # CHECK: only if player has matched the current bet
        current_bet = player.current_bet if player.current_bet is not None else 0.0
        game_current_bet = self.current_bet if self.current_bet is not None else 0.0
        
        if current_bet == game_current_bet:
            legal_actions.add(ActionType.CHECK)
        else:
            # CALL: if player is behind the current bet
            legal_actions.add(ActionType.CALL)
        
        # BET/RAISE: if player has chips remaining
        if player.stack > 0:
            if game_current_bet == 0:
                legal_actions.add(ActionType.BET)
            else:
                legal_actions.add(ActionType.RAISE)
        
        return legal_actions
