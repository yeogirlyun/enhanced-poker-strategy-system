"""
MVU (Model-View-Update) Architecture Types
Based on PokerPro UI Implementation Handbook v2
"""

from dataclasses import dataclass, replace
from typing import Literal, Optional, Dict, List, Set, Any, Protocol, Callable, FrozenSet, Mapping
from abc import ABC, abstractmethod

# Helper types for immutable collections
ImmutableSeats = Mapping[int, "SeatState"]
ImmutableStacks = Mapping[int, int]

@dataclass(frozen=True, slots=True)
class SeatState:
    """State for a single seat at the poker table - FULLY IMMUTABLE"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int
    folded: bool
    all_in: bool
    cards: tuple[str, ...]
    position: int
    acting: bool = False
    
    def __eq__(self, other):
        if not isinstance(other, SeatState):
            return False
        return (
            self.player_uid == other.player_uid and
            self.name == other.name and
            self.stack == other.stack and
            self.chips_in_front == other.chips_in_front and
            self.folded == other.folded and
            self.all_in == other.all_in and
            self.cards == other.cards and
            self.position == other.position and
            self.acting == other.acting
        )

@dataclass(frozen=True)
class Action:
    seat: int
    action: str
    amount: Optional[int] = None
    street: str = "PREFLOP"

@dataclass(frozen=True)
class Model:
    hand_id: str
    street: Literal["PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "DONE"]
    to_act_seat: Optional[int]
    stacks: ImmutableStacks
    pot: int
    board: tuple[str, ...]
    seats: ImmutableSeats
    legal_actions: FrozenSet[str]
    last_action: Optional[Action]
    session_mode: Literal["PRACTICE", "GTO", "REVIEW"]
    autoplay_on: bool
    step_delay_ms: int
    waiting_for: Literal["HUMAN_DECISION", "BOT_DECISION", "ANIMATION", "NONE"]
    review_cursor: int
    review_len: int
    review_paused: bool
    theme_id: str
    tx_id: int
    
    @classmethod
    def initial(cls, session_mode: Literal["PRACTICE", "GTO", "REVIEW"] = "REVIEW") -> "Model":
        return cls(
            hand_id="", street="PREFLOP", to_act_seat=None, stacks={}, pot=0,
            board=(), seats={}, legal_actions=frozenset(), last_action=None,
            session_mode=session_mode, autoplay_on=False, step_delay_ms=1000,
            waiting_for="NONE", review_cursor=0, review_len=0, review_paused=False,
            theme_id="forest-green-pro", tx_id=0
        )

# Messages
class Msg(ABC):
    pass

class NextPressed(Msg):
    pass

@dataclass
class LoadHand(Msg):
    hand_data: Dict[str, Any]

# Commands  
class Cmd(ABC):
    pass

@dataclass
class PlaySound(Cmd):
    name: str

# Props for rendering
@dataclass(frozen=True, slots=True)
class TableRendererProps:
    seats: ImmutableSeats
    board: tuple[str, ...]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: FrozenSet[str]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    review_cursor: int
    review_len: int
    session_mode: str
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        return cls(
            seats=model.seats, board=model.board, pot=model.pot,
            to_act_seat=model.to_act_seat, legal_actions=model.legal_actions,
            theme_id=model.theme_id, autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for, review_cursor=model.review_cursor,
            review_len=model.review_len, session_mode=model.session_mode
        )

class IntentHandler(Protocol):
    def on_click_next(self) -> None: pass