from abc import ABC, abstractmethod
from typing import List
from ..core.poker_types import Player


class RulesProvider(ABC):
    """Protocol for defining poker rules like first-to-act order."""
    
    @abstractmethod
    def get_first_to_act(self, players: List[Player], street: str) -> int:
        """Return the index of the first player to act on the given street."""
        pass
    
    @abstractmethod
    def get_action_order(
        self, players: List[Player], street: str
    ) -> List[int]:
        """Return the order of players to act on the given street."""
        pass
