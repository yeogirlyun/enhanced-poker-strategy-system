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
Version 2.0 (2025-07-29) - Professional Theme Enhancement
- Updated with professional color scheme and improved visual hierarchy.
- Enhanced tier colors for better distinction and accessibility.
- Improved font definitions and theme consistency.
"""

import json
import os
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

# --- Professional Theme Definition ---
THEME = {
    "primary_bg": "#1e1e1e",      # A slightly softer black for the main background
    "secondary_bg": "#2d2d2d",    # For panels and frames
    "widget_bg": "#3c3c3c",       # For buttons, entries, etc.
    "text": "#d4d4d4",           # A softer white for text
    "text_dark": "#a0a0a0",       # For less important text
    "accent_primary": "#0e639c",  # A strong blue for primary actions
    "accent_secondary": "#4CAF50",# Green for success or positive feedback
    "accent_danger": "#d13438",   # Red for warnings or negative actions
    "border": "#555555",
    
    # Legacy compatibility
    "bg": "#1e1e1e",          # Dark background
    "bg_dark": "#2d2d2d",      # Slightly lighter dark
    "bg_light": "#3c3c3c",     # Light gray for buttons
    "fg": "#d4d4d4",           # White text
    "accent": "#4CAF50",       # Green accent
    "font_family": "Arial",
    "font_size": 11,
    "tier_colors": {
        "Elite": "#D13438",     # Strong Red
        "Premium": "#0E639C",   # Strong Blue
        "Gold": "#FF8C00",      # Dark Orange
        "Silver": "#4CAF50",    # Green
        "Bronze": "#8A3FFC",    # Purple
    },
}

FONTS = {
    "main": ("Arial", 11),
    "title": ("Arial", 16, "bold"),
    "header": ("Arial", 12, "bold"),
    "small": ("Arial", 9),
    "player_name": ("Arial", 14, "bold"),  # Bigger font for player names
    "stack_bet": ("Arial", 16, "bold"),    # Much bigger font for stack and betting amounts
    "cards": ("Arial", 12, "bold"),        # Font for card display
}

# --- COMPREHENSIVE PREFLOP EQUITY TABLE ---
PREFLOP_EQUITY_TABLE = {
    'AA': 85, 'KK': 82, 'QQ': 80, 'JJ': 77, 'TT': 75,
    '99': 72, '88': 70, '77': 68, '66': 66, '55': 64,
    '44': 62, '33': 60, '22': 58,
    'AKs': 67, 'AQs': 66, 'AJs': 65, 'ATs': 64, 'A9s': 61, 'A8s': 60, 'A7s': 59, 'A6s': 58, 'A5s': 57, 'A4s': 56, 'A3s': 55, 'A2s': 54,
    'AKo': 65, 'AQo': 64, 'AJo': 63, 'ATo': 62, 'A9o': 58, 'A8o': 57, 'A7o': 56, 'A6o': 55, 'A5o': 54, 'A4o': 53, 'A3o': 52, 'A2o': 51,
    'KQs': 63, 'KJs': 62, 'KTs': 61, 'K9s': 58, 'K8s': 57, 'K7s': 56, 'K6s': 55, 'K5s': 54, 'K4s': 53, 'K3s': 52, 'K2s': 51,
    'KQo': 61, 'KJo': 60, 'KTo': 59, 'K9o': 55, 'K8o': 54, 'K7o': 53, 'K6o': 52, 'K5o': 51, 'K4o': 50, 'K3o': 49, 'K2o': 48,
    'QJs': 60, 'QTs': 59, 'Q9s': 57, 'Q8s': 56, 'Q7s': 55, 'Q6s': 54, 'Q5s': 53, 'Q4s': 52, 'Q3s': 51, 'Q2s': 50,
    'QJo': 58, 'QTo': 57, 'Q9o': 54, 'Q8o': 53, 'Q7o': 52, 'Q6o': 51, 'Q5o': 50, 'Q4o': 49, 'Q3o': 48, 'Q2o': 47,
    'JTs': 58, 'J9s': 56, 'J8s': 55, 'J7s': 54, 'J6s': 53, 'J5s': 52, 'J4s': 51, 'J3s': 50, 'J2s': 49,
    'JTo': 57, 'J9o': 53, 'J8o': 52, 'J7o': 51, 'J6o': 50, 'J5o': 49, 'J4o': 48, 'J3o': 47, 'J2o': 46,
    'T9s': 55, 'T8s': 54, 'T7s': 53, 'T6s': 52, 'T5s': 51, 'T4s': 50, 'T3s': 49, 'T2s': 48,
    'T9o': 52, 'T8o': 51, 'T7o': 50, 'T6o': 49, 'T5o': 48, 'T4o': 47, 'T3o': 46, 'T2o': 45,
    '98s': 54, '97s': 53, '96s': 52, '95s': 51, '94s': 50, '93s': 49, '92s': 48,
    '98o': 51, '97o': 50, '96o': 49, '95o': 48, '94o': 47, '93o': 46, '92o': 45,
    '87s': 53, '86s': 52, '85s': 51, '84s': 50, '83s': 49, '82s': 48,
    '87o': 50, '86o': 49, '85o': 48, '84o': 47, '83o': 46, '82o': 45,
    '76s': 52, '75s': 51, '74s': 50, '73s': 49, '72s': 48,
    '76o': 49, '75o': 48, '74o': 47, '73o': 46, '72o': 45,
    '65s': 51, '64s': 50, '63s': 49, '62s': 48,
    '65o': 48, '64o': 47, '63o': 46, '62o': 45,
    '54s': 50, '53s': 49, '52s': 48,
    '54o': 47, '53o': 46, '52o': 45,
    '43s': 49, '42s': 48,
    '43o': 46, '42o': 45,
    '32s': 48,
    '32o': 45,
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
    hands: Set[str] = field(default_factory=set)


@dataclass
class StrategyData:
    """
    A central data model to hold the entire state of a strategy.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to act as a single source of truth for the application's state.
    - Manages the list of tiers and the full strategy dictionary.
    Version 1.1 (2025-07-29) - Strategy File Support
    - Added support for loading strategy data from JSON files.
    - Added current strategy file tracking.
    Version 2.0 (2025-07-29) - Professional Theme Enhancement
    - Updated with professional color scheme and improved visual hierarchy.
    - Enhanced tier colors for better distinction and accessibility.
    """

    tiers: List[HandStrengthTier] = field(default_factory=list)
    strategy_dict: Dict[str, Any] = field(default_factory=dict)
    current_strategy_file: Optional[str] = None

    def add_tier(self, tier: HandStrengthTier):
        """Adds a new tier and sorts the list by strength."""
        self.tiers.append(tier)
        self.tiers.sort(key=lambda t: t.min_hs, reverse=True)

    def remove_tier(self, index: int):
        """Removes a tier by its index."""
        if 0 <= index < len(self.tiers):
            self.tiers.pop(index)

    def load_default_tiers(self):
        """Loads modern 5-tier system with memorable boundaries."""
        tier_colors = {
            "Premium": "#FF0000",    # Bright Red - The Monsters
            "Strong": "#FFA500",     # Orange - The Workhorses  
            "Playable": "#FFD700",   # Gold - The Bread & Butter
            "Speculative": "#00FF00", # Green - The Connectors
            "Marginal": "#87CEEB"    # Sky Blue - The Situational
        }
        
        self.tiers = [
            HandStrengthTier(
                "Premium", 80, 100, tier_colors["Premium"], 
                {"AA", "KK", "QQ", "AKs", "JJ", "AKo", "AQs", "TT"}
            ),
            HandStrengthTier(
                "Strong", 65, 79, tier_colors["Strong"], 
                {"AQo", "AJs", "KQs", "99", "AJo", "KJs", "ATs", "88", "KQo", "QJs", "KTs"}
            ),
            HandStrengthTier(
                "Playable", 50, 64, tier_colors["Playable"], 
                {"77", "A9s", "A8s", "JTs", "66", "KJo", "QTs", "A7s", "A5s", "55", "A6s", "A4s", "T9s"}
            ),
            HandStrengthTier(
                "Speculative", 35, 49, tier_colors["Speculative"], 
                {"44", "A3s", "A2s", "K9s", "33", "Q9s", "J9s", "98s", "22", "87s"}
            ),
            HandStrengthTier(
                "Marginal", 20, 34, tier_colors["Marginal"], 
                {"K8s", "76s", "65s", "54s", "T8s"}
            ),
        ]
        self.current_strategy_file = None
        self.strategy_dict = self._create_strategy_from_tiers()

    def load_strategy_from_file(self, filename: str = None) -> bool:
        """Loads strategy data from a JSON file or generates and saves default strategy."""
        try:
            # If no filename provided or file doesn't exist, generate and save default
            if filename is None or not os.path.exists(filename):
                print(f"📁 Generating default strategy (file not found: {filename})")
                self.load_default_tiers()
                
                # Save the default strategy to modern_strategy.json
                default_filename = "modern_strategy.json"
                self.save_strategy_to_file(default_filename)
                self.current_strategy_file = default_filename
                print(f"💾 Saved default strategy to {default_filename}")
                return True

            with open(filename, "r") as f:
                strategy_data = json.load(f)

            self.strategy_dict = strategy_data
            self._create_tiers_from_strategy(strategy_data)
            self.current_strategy_file = filename
            return True
        except Exception as e:
            print(f"⚠️ Error loading strategy file, generating default: {e}")
            self.load_default_tiers()
            
            # Save the default strategy to modern_strategy.json
            default_filename = "modern_strategy.json"
            self.save_strategy_to_file(default_filename)
            self.current_strategy_file = default_filename
            print(f"💾 Saved default strategy to {default_filename}")
            return True

    def _create_tiers_from_strategy(self, strategy_data: Dict[str, Any]):
        """Creates tiers from strategy data."""
        self.tiers.clear()
        hand_strength_table = strategy_data.get("hand_strength_tables", {}).get("preflop", {})
        if not hand_strength_table:
            self.load_default_tiers()
            return

        tier_colors = {
            "Premium": "#FF0000", "Strong": "#FFA500", "Playable": "#FFD700",
            "Speculative": "#00FF00", "Marginal": "#87CEEB"
        }
        strength_groups = {}
        for hand, strength in hand_strength_table.items():
            if strength >= 80: tier_name, min_hs, max_hs = "Premium", 80, 100
            elif strength >= 65: tier_name, min_hs, max_hs = "Strong", 65, 79
            elif strength >= 50: tier_name, min_hs, max_hs = "Playable", 50, 64
            elif strength >= 35: tier_name, min_hs, max_hs = "Speculative", 35, 49
            elif strength >= 20: tier_name, min_hs, max_hs = "Marginal", 20, 34
            else: continue  # Skip unplayable hands
            
            if tier_name not in strength_groups:
                strength_groups[tier_name] = {"hands": set(), "min_hs": min_hs, "max_hs": max_hs, "color": tier_colors[tier_name]}
            strength_groups[tier_name]["hands"].add(hand)

        for tier_name, data in strength_groups.items():
            self.tiers.append(HandStrengthTier(name=tier_name, **data))
        self.tiers.sort(key=lambda t: t.min_hs, reverse=True)

    def save_strategy_to_file(self, filename: str) -> bool:
        """Saves current strategy data to a JSON file."""
        try:
            strategy_data = self._create_strategy_from_tiers()
            with open(filename, "w") as f:
                json.dump(strategy_data, f, indent=2)
            self.current_strategy_file = filename
            return True
        except Exception as e:
            return False

    def _create_strategy_from_tiers(self) -> Dict[str, Any]:
        """Creates strategy data from tiers with improved GTO hand strength scores."""
        # Use improved GTO hand strength scores for default strategy
        improved_hand_strength = {
            "AA": 100, "KK": 95, "QQ": 90, "AKs": 85, "JJ": 80, "AKo": 80, "AQs": 80, "TT": 80,
            "AQo": 75, "AJs": 75, "KQs": 75, "99": 70, "AJo": 70, "KJs": 70, "ATs": 70,
            "88": 65, "KQo": 65, "QJs": 65, "KTs": 65, "77": 60, "A9s": 60, "A8s": 60, "JTs": 60,
            "66": 55, "KJo": 55, "QTs": 55, "A7s": 55, "A5s": 55, "55": 50, "A6s": 50, "A4s": 50, "T9s": 50,
            "44": 45, "A3s": 45, "A2s": 45, "K9s": 45, "33": 40, "Q9s": 40, "J9s": 40, "98s": 40,
            "22": 35, "87s": 35, "K8s": 30, "76s": 30, "65s": 25, "54s": 25, "T8s": 20
        }
        
        hand_strength_table = {}
        
        # Use existing strategy data if available, otherwise use improved scores
        existing_hand_strength = self.strategy_dict.get("hand_strength_tables", {}).get("preflop", {})
        
        for tier in self.tiers:
            for hand in tier.hands:
                # Use existing HS score if available, otherwise use improved scores
                if hand in existing_hand_strength:
                    hand_strength_table[hand] = existing_hand_strength[hand]
                elif hand in improved_hand_strength:
                    hand_strength_table[hand] = improved_hand_strength[hand]
                elif hand in PREFLOP_EQUITY_TABLE:
                    hand_strength_table[hand] = PREFLOP_EQUITY_TABLE[hand]

        # Complete postflop strategy with all positions and streets
        postflop_strategy = {
            "pfa": {
                "flop": {
                    "UTG": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75},
                    "MP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.75},
                    "CO": {"val_thresh": 25, "check_thresh": 10, "sizing": 0.75},
                    "BTN": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.75},
                    "SB": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.75},
                },
                "turn": {
                    "UTG": {"val_thresh": 40, "check_thresh": 20, "sizing": 0.8},
                    "MP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.8},
                    "CO": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.8},
                    "BTN": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.8},
                    "SB": {"val_thresh": 30, "check_thresh": 20, "sizing": 0.8},
                },
                "river": {
                    "UTG": {"val_thresh": 45, "check_thresh": 25, "sizing": 1.0},
                    "MP": {"val_thresh": 40, "check_thresh": 25, "sizing": 1.0},
                    "CO": {"val_thresh": 35, "check_thresh": 20, "sizing": 1.0},
                    "BTN": {"val_thresh": 30, "check_thresh": 20, "sizing": 1.0},
                    "SB": {"val_thresh": 35, "check_thresh": 25, "sizing": 1.0},
                },
            },
            "caller": {
                "flop": {
                    "UTG": {"val_thresh": 25, "check_thresh": 10, "sizing": 0.75},
                    "MP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.75},
                    "CO": {"val_thresh": 15, "check_thresh": 5, "sizing": 0.75},
                    "BTN": {"val_thresh": 15, "check_thresh": 5, "sizing": 0.75},
                    "SB": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.75},
                },
                "turn": {
                    "UTG": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.8},
                    "MP": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.8},
                    "CO": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.8},
                    "BTN": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.8},
                    "SB": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.8},
                },
                "river": {
                    "UTG": {"val_thresh": 35, "check_thresh": 20, "sizing": 1.0},
                    "MP": {"val_thresh": 30, "check_thresh": 20, "sizing": 1.0},
                    "CO": {"val_thresh": 25, "check_thresh": 15, "sizing": 1.0},
                    "BTN": {"val_thresh": 25, "check_thresh": 15, "sizing": 1.0},
                    "SB": {"val_thresh": 30, "check_thresh": 20, "sizing": 1.0},
                },
            },
        }

        # Create complete strategy structure
        strategy_data = {
            "hand_strength_tables": {
                "preflop": hand_strength_table,
                "postflop": {
                    # Made Hands
                    "high_card": 5,
                    "pair": 15,
                    "top_pair": 30,
                    "over_pair": 35,
                    "two_pair": 45,
                    "set": 60,
                    "straight": 70,
                    "flush": 80,
                    "full_house": 90,
                    "quads": 100,
                    "straight_flush": 120,
                    # Draws
                    "gutshot_draw": 12,
                    "open_ended_draw": 18,
                    "flush_draw": 20,
                    "combo_draw": 35,
                    # Special Situations
                    "nut_flush_draw": 25,
                    "nut_straight_draw": 22,
                    "overcard_draw": 8,
                    "backdoor_flush": 3,
                    "backdoor_straight": 2,
                    "pair_plus_draw": 28,
                    "set_plus_draw": 65,
                },
            },
            "preflop": {
                "open_rules": {
                    "UTG": {"threshold": 60, "sizing": 3.0},  # Tighter: Only plays hands like AJ+ / KQ / 77+
                    "MP": {"threshold": 55, "sizing": 3.0},   # Opens up slightly to include hands like A8s+ / KJs / 55+
                    "CO": {"threshold": 48, "sizing": 2.5},   # Wider range, includes suited connectors and more broadways
                    "BTN": {"threshold": 40, "sizing": 2.5},  # Very wide range, plays most suited hands and any pair
                    "SB": {"threshold": 50, "sizing": 3.0},   # A bit tighter than the button due to being out of position
                },
                "vs_raise": {
                    "UTG": {"value_thresh": 75, "call_thresh": 65, "sizing": 3.0},  # 3-bet only with premium hands like TT+ / AQ+
                    "MP": {"value_thresh": 72, "call_thresh": 62, "sizing": 3.0},   # Call with strong hands like AJ / KQ / 99
                    "CO": {"value_thresh": 70, "call_thresh": 60, "sizing": 2.5},   # Can call with a wider range in position
                    "BTN": {"value_thresh": 68, "call_thresh": 55, "sizing": 2.5},  # Very wide calling range in position
                    "SB": {"value_thresh": 70, "call_thresh": 60, "sizing": 3.0},   # Balanced approach from small blind
                }
            },
            "postflop": postflop_strategy,
        }

        return strategy_data

    def get_current_strategy_file(self) -> Optional[str]:
        """Returns the current strategy file name."""
        return self.current_strategy_file

    def get_strategy_file_display_name(self) -> str:
        """Returns a display name for the current strategy file."""
        if self.current_strategy_file:
            return os.path.basename(self.current_strategy_file)
        return "Default Strategy"

    def get_available_strategy_files(self) -> List[str]:
        """Returns a list of available strategy files in the current directory."""
        strategy_files = []
        for file in os.listdir("."):
            if file.endswith(".json") and "strategy" in file.lower():
                strategy_files.append(file)
        return sorted(strategy_files)


class GridSettings:
    """
    Static class to manage grid size configurations.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Centralizes grid size settings to be accessible by any UI component.
    """

    _SIZES = ["1", "2", "3", "4", "5", "6", "7", "8"]
    _CONFIGS = {
        "1": {
            "font": ("Helvetica", 10),  # Was size 3
            "button_width": 35,
            "button_height": 35,
            "label_width": 10,
        },
        "2": {
            "font": ("Helvetica", 12),  # Was size 4
            "button_width": 40,
            "button_height": 40,
            "label_width": 11,
        },
        "3": {
            "font": ("Helvetica", 14),  # Was size 5
            "button_width": 45,
            "button_height": 45,
            "label_width": 12,
        },
        "4": {
            "font": ("Helvetica", 16),  # Was size 6
            "button_width": 60,
            "button_height": 60,
            "label_width": 13,
        },
        "5": {
            "font": ("Helvetica", 18),  # Was size 7
            "button_width": 65,
            "button_height": 65,
            "label_width": 14,
        },
        "6": {
            "font": ("Helvetica", 20),  # Was size 8
            "button_width": 70,
            "button_height": 70,
            "label_width": 15,
        },
        "7": {
            "font": ("Helvetica", 22),  # New larger size
            "button_width": 75,
            "button_height": 75,
            "label_width": 16,
        },
        "8": {
            "font": ("Helvetica", 24),  # New largest size
            "button_width": 80,
            "button_height": 80,
            "label_width": 17,
        },
    }
    HIGHLIGHT_COLORS = [
        "#FF4444",  # Red
        "#44AAFF",  # Blue
        "#FFAA44",  # Orange
        "#44FF44",  # Green
        "#FF8844",  # Orange-Red
    ]

    @staticmethod
    def get_all_sizes() -> List[str]:
        """Returns all available grid sizes."""
        return GridSettings._SIZES.copy()

    @staticmethod
    def get_size_config(size: str) -> Dict:
        """Returns the configuration for a given size."""
        return GridSettings._CONFIGS.get(size, GridSettings._CONFIGS["4"])

    @staticmethod
    def calculate_button_size_for_grid(
        grid_width: int, grid_height: int, size: str
    ) -> Dict:
        """Calculate optimal button size for a given grid size."""
        config = GridSettings.get_size_config(size)
        max_width = grid_width // 13  # 13 columns
        max_height = grid_height // 13  # 13 rows

        # Use the smaller of the calculated size or the config size
        button_width = min(config["button_width"], max_width)
        button_height = min(config["button_height"], max_height)

        return {
            "button_width": button_width,
            "button_height": button_height,
            "font": config["font"],
        }


class HandFormatHelper:
    """
    Helper class for hand format conversions and validations.
    """

    @staticmethod
    def get_alternative_formats(hand: str) -> List[str]:
        """Get alternative formats for a hand (e.g., AhKs -> AKs, AKs -> AhKs)."""
        if len(hand) == 4 and hand.endswith(("h", "d", "c", "s")):
            # Convert AhKs to AKs
            return [hand[0] + hand[2] + hand[3]]
        elif len(hand) == 3 and hand.endswith(("s", "o")):
            # Convert AKs to AhKs (example)
            return [hand[0] + "h" + hand[1] + hand[2]]
        return [hand]

    @staticmethod
    def normalize_hand_format(hand: str) -> str:
        """Normalize hand format to standard notation."""
        # Remove any extra spaces and convert to uppercase
        hand = hand.strip().upper()
        
        # Handle different input formats
        if len(hand) == 4 and hand.endswith(("H", "D", "C", "S")):
            # AhKs format
            return hand[0] + hand[2] + hand[3].lower()
        elif len(hand) == 3 and hand.endswith(("S", "O")):
            # AKs format
            return hand
        elif len(hand) == 2:
            # AA format (pocket pair)
            return hand
        else:
            # Unknown format, return as is
            return hand


class FileOperations:
    """
    Helper class for file operations.
    """

    @staticmethod
    def load_strategy(filename: str) -> Optional[Dict]:
        """Load strategy from file."""
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            return None

    @staticmethod
    def save_strategy(strategy: Dict, filename: str) -> bool:
        """Save strategy to file."""
        try:
            with open(filename, "w") as f:
                json.dump(strategy, f, indent=2)
            return True
        except Exception as e:
            return False
