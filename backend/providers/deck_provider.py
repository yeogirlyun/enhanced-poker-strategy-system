from abc import ABC, abstractmethod
from typing import List


class DeckProvider(ABC):
    """Protocol for deck initialization and replacement."""
    
    @abstractmethod
    def get_deck(self) -> List[str]:
        """Return a deck of cards in the specified order."""
        pass
    
    @abstractmethod
    def replace_deck(self, cards: List[str]) -> None:
        """Replace the current deck with the specified cards."""
        pass
    
    @abstractmethod
    def is_deterministic(self) -> bool:
        """Return True if this deck provider guarantees deterministic order."""
        pass
