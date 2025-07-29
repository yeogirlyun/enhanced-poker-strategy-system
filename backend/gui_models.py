# filename: gui_models.py
"""
Data Models and Structures for Strategy Development GUI

Contains all data classes and core business logic without UI dependencies.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created as part of a major refactoring of the GUI.
- Centralizes all non-UI data structures like HandStrengthTier and StrategyData.
- Decouples the core application state from the view components.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# --- GTO Theme Definition ---
THEME = {
    "bg": "#2E2E2E",
    "fg": "#E0E0E0",
    "bg_light": "#3C3C3C",
    "bg_dark": "#252525",
    "accent": "#007ACC",
    "font_family": "Helvetica",
    "font_size": 10,
    "tier_colors": {
        "Elite": "#00FF00",   # Bright Green (Value)
        "Premium": "#00BFFF", # Deep Sky Blue (Strong Value)
        "Gold": "#FF69B4",    # Hot Pink (Bluff/Mixed)
        "Silver": "#FF8C00",  # Dark Orange (Thin Value/Call)
        "Bronze": "#808080"   # Gray (Fold/Marginal)
    },
    "highlight_color": "white"
}

@dataclass
class HandStrengthTier:
    """
    Represents a single tier of hands with a name, HS range, and color.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to model a hand tier as a dataclass.
    - Stores name, HS range, color, and a list of associated poker hands.
    """
    name: str
    min_hs: int
    max_hs: int
    color: str
    hands: List[str] = field(default_factory=list)

@dataclass
class StrategyData:
    """
    A central data model to hold the entire state of a strategy.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to act as a single source of truth for the application's state.
    - Manages the list of tiers and the full strategy dictionary.
    """
    tiers: List[HandStrengthTier] = field(default_factory=list)
    strategy_dict: Dict[str, Any] = field(default_factory=dict)

    def add_tier(self, tier: HandStrengthTier):
        """Adds a new tier and sorts the list by strength."""
        self.tiers.append(tier)
        self.tiers.sort(key=lambda t: t.min_hs, reverse=True)

    def remove_tier(self, index: int):
        """Removes a tier by its index."""
        if 0 <= index < len(self.tiers):
            self.tiers.pop(index)

    def load_default_tiers(self):
        """Loads a default set of tiers for a new strategy."""
        self.tiers = [
            HandStrengthTier("Elite", 40, 50, THEME["tier_colors"]["Elite"], ["AA", "KK", "QQ", "AKs"]),
            HandStrengthTier("Premium", 30, 39, THEME["tier_colors"]["Premium"], ["JJ", "AKo", "AQs", "AJs", "KQs"]),
            HandStrengthTier("Gold", 20, 29, THEME["tier_colors"]["Gold"], ["TT", "99", "AQo", "AJo", "KJs", "QJs", "JTs"]),
            HandStrengthTier("Silver", 10, 19, THEME["tier_colors"]["Silver"], ["88", "77", "KJo", "QJo", "JTo", "A9s", "A8s"]),
            HandStrengthTier("Bronze", 1, 9, THEME["tier_colors"]["Bronze"], ["66", "55", "44", "33", "22", "A7s", "A6s", "A5s"])
        ]

class GridSettings:
    """
    Static class to manage grid size configurations.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Centralizes grid size settings to be accessible by any UI component.
    """
    _SIZES = ["Small", "Medium", "Large", "Extra Large"]
    _CONFIGS = {
        "Small": {'font': ('Helvetica', 8), 'button_width': 4, 'button_height': 1, 'label_width': 4},
        "Medium": {'font': ('Helvetica', 9), 'button_width': 5, 'button_height': 1, 'label_width': 5},
        "Large": {'font': ('Helvetica', 10), 'button_width': 6, 'button_height': 2, 'label_width': 6},
        "Extra Large": {'font': ('Helvetica', 12), 'button_width': 7, 'button_height': 2, 'label_width': 7}
    }
    HIGHLIGHT_COLORS = ['#FFFF00', '#00FFFF', '#FF00FF', '#00FF00', '#FFA500']

    @staticmethod
    def get_all_sizes() -> List[str]:
        return GridSettings._SIZES

    @staticmethod
    def get_size_config(size: str) -> Dict:
        return GridSettings._CONFIGS.get(size, GridSettings._CONFIGS["Medium"])

class HandFormatHelper:
    """
    Static class with helper methods for poker hand notations.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to handle conversions between different hand notations (e.g., AKs vs KAs).
    """
    @staticmethod
    def get_alternative_formats(hand: str) -> List[str]:
        """Gets alternative formats for a hand (e.g., AKs -> KAs)."""
        if len(hand) < 2: 
            return [hand]
        
        # Handle pocket pairs
        if len(hand) == 2 and hand[0] == hand[1]:
            return [hand]
        
        # Handle suited/offsuit hands
        if len(hand) >= 3:
            rank1, rank2 = hand[0], hand[1]
            suffix = hand[2:]
            return [f"{rank1}{rank2}{suffix}", f"{rank2}{rank1}{suffix}"]
        
        return [hand]
    
    @staticmethod
    def normalize_hand_format(hand: str) -> str:
        """Normalizes hand format to standard notation."""
        if len(hand) < 2:
            return hand
        
        # Pocket pairs
        if len(hand) == 2 and hand[0] == hand[1]:
            return hand
        
        # Suited/offsuit hands
        if len(hand) >= 3:
            rank1, rank2 = hand[0], hand[1]
            suffix = hand[2:]
            
            # Ensure ranks are in correct order (A > K > Q > J > T > 9...)
            rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                         '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
            
            if rank_order.get(rank1, 0) >= rank_order.get(rank2, 0):
                return f"{rank1}{rank2}{suffix}"
            else:
                return f"{rank2}{rank1}{suffix}"
        
        return hand

class FileOperations:
    """
    Static class for handling file loading and saving logic.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Extracts file I/O logic to keep other classes clean.
    """
    @staticmethod
    def load_strategy(filename: str) -> Optional[Dict]:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
            return None

    @staticmethod
    def save_strategy(strategy: Dict, filename: str) -> bool:
        try:
            with open(filename, 'w') as f:
                json.dump(strategy, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
            return False