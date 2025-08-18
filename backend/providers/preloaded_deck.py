from typing import List
from .deck_provider import DeckProvider


class PreloadedDeck(DeckProvider):
    """Provides preloaded, deterministic decks for replay scenarios."""
    
    def __init__(self, cards: List[str]):
        self._cards = cards.copy()
    
    def get_deck(self) -> List[str]:
        """Return the preloaded deck in the exact order specified."""
        return self._cards.copy()
    
    def replace_deck(self, cards: List[str]) -> None:
        """Replace the current deck with the specified cards."""
        self._cards = cards.copy()
    
    def is_deterministic(self) -> bool:
        """Return True for preloaded decks."""
        return True
    
    def set_board_cards(self, board_cards: List[str]) -> None:
        """Set specific board cards at the top of the deck for deterministic dealing."""
        if not board_cards:
            return
            
        # Create a full deck using the same logic as FPSM
        suits = ["h", "d", "c", "s"]
        ranks = [
            "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"
        ]
        full_deck = [rank + suit for suit in suits for rank in ranks]
        
        # Remove used cards and prepend board cards
        used_cards = set(board_cards)
        remaining = [
            c for c in full_deck if c not in used_cards
        ]
        self._cards = board_cards + remaining
    
    def get_next_cards(self, num_cards: int) -> List[str]:
        """Get the next cards from the deck."""
        if num_cards <= len(self._cards):
            next_cards = self._cards[:num_cards]
            self._cards = self._cards[num_cards:]
            return next_cards
        return []
