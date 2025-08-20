"""
Centralized Sizing System for Poker Table Elements
==================================================

Provides proportional sizing for all poker table elements based on:
- Number of players (2-3, 4-6, 7-9)
- Table dimensions (width/height)
- Element type (cards, chips, text, etc.)

Sizing Guidelines:
- 2-3 players: 6% of table size for cards
- 4-6 players: 5% of table size for cards  
- 7-9 players: 4% of table size for cards

Element Proportions:
- Pot chips: 50% of card size
- Player stack chips: 30% of card size
- Bet/call chips: 30% of card size
- Animation chips: 30% for bet->pot, 40% for pot->winner
- Text: Proportional to card size
- Spacing: Proportional to card size
"""

import math
from typing import Tuple, Dict, Any


class PokerTableSizing:
    """Centralized sizing system for poker table elements."""
    
    def __init__(self, table_width: int, table_height: int, num_players: int):
        """
        Initialize sizing system.
        
        Args:
            table_width: Table width in pixels
            table_height: Table height in pixels
            num_players: Number of players at the table
        """
        self.table_width = table_width
        self.table_height = table_height
        self.num_players = num_players
        
        # Calculate base card size based on player count
        self.card_size = self._calculate_card_size()
        
        # Calculate all other element sizes
        self._calculate_element_sizes()
    
    def _calculate_card_size(self) -> Tuple[int, int]:
        """Calculate card size based on player count and table dimensions."""
        # Use smaller dimension for proportional scaling
        table_size = min(self.table_width, self.table_height)
        
        # Determine card scale based on player count
        if self.num_players <= 3:
            card_scale = 0.06  # 6% for 2-3 players
        elif self.num_players <= 6:
            card_scale = 0.05  # 5% for 4-6 players
        else:
            card_scale = 0.04  # 4% for 7-9 players
        
        # Calculate card dimensions (maintain 2:3 aspect ratio)
        # Remove the 0.7 multiplier to get exact percentage of table size
        card_width = int(table_size * card_scale)          # Exact percentage of table size
        card_height = int(card_width * 1.5)                # Height ratio (2:3 aspect)
        
        # Ensure minimum sizes for readability
        card_width = max(40, card_width)                   # Increased minimum
        card_height = max(60, card_height)                 # Increased minimum
        
        return card_width, card_height
    
    def _calculate_element_sizes(self):
        """Calculate sizes for all poker table elements."""
        card_w, card_h = self.card_size
        
        # Chip sizes (based on card size)
        self.chip_sizes = {
            'pot': int(min(card_w, card_h) * 0.5),      # 50% of card size
            'stack': int(min(card_w, card_h) * 0.3),    # 30% of card size
            'bet': int(min(card_w, card_h) * 0.3),      # 30% of card size
            'animation_bet': int(min(card_w, card_h) * 0.3),  # 30% for bet->pot
            'animation_pot': int(min(card_w, card_h) * 0.4),  # 40% for pot->winner
        }
        
        # Text sizes (proportional to card size)
        self.text_sizes = {
            'card_rank': int(min(card_w, card_h) * 0.6),      # 60% of card size
            'card_suit': int(min(card_w, card_h) * 0.4),      # 40% of card size
            'bet_amount': int(min(card_w, card_h) * 0.5),     # 50% of card size
            'stack_amount': int(min(card_w, card_h) * 0.4),   # 40% of card size
            'player_name': int(min(card_w, card_h) * 0.35),   # 35% of card size
            'action_label': int(min(card_w, card_h) * 0.3),   # 30% of card size
            'blind_label': int(min(card_w, card_h) * 0.25),   # 25% of card size
        }
        
        # Spacing sizes (proportional to card size)
        self.spacing = {
            'card_gap': max(4, card_w // 8),           # Between community cards
            'seat_gap': max(8, card_w // 6),           # Between seats
            'chip_stack_gap': max(3, card_w // 12),    # Between stacked chips
            'text_margin': max(2, card_w // 16),       # Text margins
            'element_padding': max(4, card_w // 10),   # Element padding
        }
        
        # Animation timing (proportional to table size)
        table_size = min(self.table_width, self.table_height)
        self.animation_timing = {
            'frame_delay': max(40, table_size // 40),  # Animation frame delay (ms)
            'total_frames': max(20, table_size // 50), # Total animation frames
        }
    
    def get_card_size(self) -> Tuple[int, int]:
        """Get the calculated card size."""
        return self.card_size
    
    def get_chip_size(self, chip_type: str) -> int:
        """Get chip size for specific type."""
        return self.chip_sizes.get(chip_type, self.chip_sizes['bet'])
    
    def get_text_size(self, text_type: str) -> int:
        """Get text size for specific type."""
        return self.text_sizes.get(text_type, self.text_sizes['action_label'])
    
    def get_spacing(self, spacing_type: str) -> int:
        """Get spacing for specific type."""
        return self.spacing.get(spacing_type, self.spacing['element_padding'])
    
    def get_animation_timing(self, timing_type: str) -> int:
        """Get animation timing for specific type."""
        return self.animation_timing.get(timing_type, self.animation_timing['frame_delay'])
    
    def get_all_sizes(self) -> Dict[str, Any]:
        """Get all calculated sizes for debugging."""
        return {
            'card_size': self.card_size,
            'chip_sizes': self.chip_sizes,
            'text_sizes': self.text_sizes,
            'spacing': self.spacing,
            'animation_timing': self.animation_timing,
            'table_dimensions': (self.table_width, self.table_height),
            'num_players': self.num_players,
        }
    
    def print_sizing_info(self):
        """Print sizing information for debugging."""
        print(f"🎯 Poker Table Sizing System:")
        print(f"   Table: {self.table_width}x{self.table_height}")
        print(f"   Players: {self.num_players}")
        print(f"   Card size: {self.card_size[0]}x{self.card_size[1]}")
        print(f"   Chip sizes: {self.chip_sizes}")
        print(f"   Text sizes: {self.text_sizes}")
        print(f"   Spacing: {self.spacing}")
        print(f"   Animation timing: {self.animation_timing}")


def create_sizing_system(table_width: int, table_height: int, num_players: int) -> PokerTableSizing:
    """Factory function to create a sizing system."""
    return PokerTableSizing(table_width, table_height, num_players)
