from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class PokerTableState:
    table: Dict[str, Any]
    seats: List[Dict[str, Any]]
    board: List[str]
    pot: Dict[str, Any]
    dealer: Dict[str, Any]
    action: Dict[str, Any]
    animation: Dict[str, Any]
    effects: List[Dict[str, Any]]
    street: str = "PREFLOP"  # Current street for community card rendering

