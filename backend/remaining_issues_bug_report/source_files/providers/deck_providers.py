"""
Deck Provider Implementations

Different deck management strategies for different session types.
"""

import random
from typing import List
from ..pure_poker_state_machine import DeckProvider


class StandardDeck(DeckProvider):
    """Standard shuffled deck for live play."""
    
    def __init__(self, shuffle: bool = True):
        self.shuffle = shuffle
        self._deck = None
    
    def get_deck(self) -> List[str]:
        """Get a fresh shuffled deck."""
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        deck = [rank + suit for suit in suits for rank in ranks]
        
        if self.shuffle:
            random.shuffle(deck)
        
        self._deck = deck.copy()
        return deck
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace the current deck."""
        self._deck = deck.copy()


class DeterministicDeck(DeckProvider):
    """Deterministic deck for hands review with known board cards."""
    
    def __init__(self, board_cards: List[str] = None, hole_cards: dict = None):
        """
        Initialize with known cards.
        
        Args:
            board_cards: List of board cards in deal order [flop1, flop2, flop3, turn, river]
            hole_cards: Dict mapping player names to their hole cards
        """
        self.board_cards = board_cards or []
        self.hole_cards = hole_cards or {}
        self._deck = None
    
    def get_deck(self) -> List[str]:
        """Get deterministic deck with known cards on top."""
        # Create full deck
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        full_deck = [rank + suit for suit in suits for rank in ranks]
        
        # Collect all known cards
        used_cards = set()
        
        # Add hole cards (will be dealt first)
        hole_sequence = []
        for player_name in sorted(self.hole_cards.keys()):
            player_cards = self.hole_cards[player_name]
            for card in player_cards:
                normalized_card = self._normalize_card(card)
                hole_sequence.append(normalized_card)
                used_cards.add(normalized_card)
        
        # Add board cards (will be dealt after hole cards)
        board_sequence = []
        for card in self.board_cards:
            normalized_card = self._normalize_card(card)
            board_sequence.append(normalized_card)
            used_cards.add(normalized_card)
        
        # Create remaining deck
        remaining_cards = [card for card in full_deck if card not in used_cards]
        
        # Construct deterministic deck: hole cards, then board cards, then remaining
        deterministic_deck = hole_sequence + board_sequence + remaining_cards
        
        self._deck = deterministic_deck.copy()
        print(f"🃏 DETERMINISTIC_DECK: Created with {len(hole_sequence)} hole + {len(board_sequence)} board + {len(remaining_cards)} remaining")
        print(f"🃏 DETERMINISTIC_DECK: First 10 cards: {deterministic_deck[:10]}")
        
        return deterministic_deck
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace the current deck."""
        self._deck = deck.copy()
    
    def _normalize_card(self, card: str) -> str:
        """Normalize card representation (handle 10 -> T)."""
        return str(card).upper().replace("10", "T")
    
    def set_board_cards(self, board_cards: List[str]):
        """Update board cards and regenerate deck."""
        self.board_cards = board_cards
    
    def set_hole_cards(self, hole_cards: dict):
        """Update hole cards and regenerate deck."""
        self.hole_cards = hole_cards


class GTODeck(DeckProvider):
    """Shuffled deck for GTO sessions (random but can be seeded for reproducibility)."""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self._deck = None
    
    def get_deck(self) -> List[str]:
        """Get a shuffled deck with optional seed."""
        if self.seed is not None:
            random.seed(self.seed)
        
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        deck = [rank + suit for suit in suits for rank in ranks]
        
        random.shuffle(deck)
        self._deck = deck.copy()
        
        if self.seed is not None:
            print(f"🃏 GTO_DECK: Seeded shuffle with seed {self.seed}")
        
        return deck
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace the current deck."""
        self._deck = deck.copy()
