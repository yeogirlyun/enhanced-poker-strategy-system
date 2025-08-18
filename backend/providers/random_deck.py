import random
from typing import List, Optional
from .deck_provider import DeckProvider


class RandomDeck(DeckProvider):
    """Provides randomly shuffled decks for normal gameplay."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self._current_deck = self._create_standard_deck()
    
    def get_deck(self) -> List[str]:
        """Return a shuffled deck of cards."""
        deck = self._current_deck.copy()
        random.shuffle(deck)
        return deck
    
    def replace_deck(self, cards: List[str]) -> None:
        """Replace the current deck with the specified cards."""
        self._current_deck = cards.copy()
    
    def is_deterministic(self) -> bool:
        """Return False for random decks."""
        return False
    
    def _create_standard_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        suits = ["h", "d", "c", "s"]
        ranks = [
            "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"
        ]
        return [rank + suit for suit in suits for rank in ranks]
