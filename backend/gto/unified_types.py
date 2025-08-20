from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Protocol, FrozenSet
from enum import Enum

# Import the comprehensive ActionType from hand_model for consistency
from backend.core.hand_model import ActionType

@dataclass(frozen=True)
class PlayerState:
    name: str
    stack: int
    position: str
    cards: Tuple[str, ...]
    current_bet: int
    is_active: bool
    has_acted: bool

@dataclass(frozen=True)
class StandardGameState:
    pot: int
    street: str
    board: Tuple[str, ...]
    players: Tuple[PlayerState, ...]
    current_bet_to_call: int
    to_act_player_index: int
    legal_actions: FrozenSet[ActionType]

class UnifiedDecisionEngineProtocol(Protocol):
    def get_decision(self, player_name: str, game_state: StandardGameState) -> Tuple[ActionType, Optional[float]]:
        ...
    def has_decision_for_player(self, player_name: str) -> bool:
        ...
    def reset_for_new_hand(self) -> None:
        ...