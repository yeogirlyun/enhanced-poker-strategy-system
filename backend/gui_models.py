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
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# --- GTO Theme Definition ---
THEME = {
    "bg": "#1a1a1a",  # Dark background
    "bg_dark": "#2d2d2d",  # Slightly lighter dark
    "bg_light": "#404040",  # Light gray for buttons
    "fg": "#ffffff",  # White text
    "accent": "#4CAF50",  # Green accent
    "font_family": "Arial",
    "font_size": 10,
    "tier_colors": {
        "Elite": "#FF4444",  # Bright Red (Premium hands)
        "Premium": "#44AAFF",  # Bright Blue (Strong hands)
        "Gold": "#FFAA44",  # Orange (Medium hands)
        "Silver": "#44FF44",  # Bright Green (Weak hands)
        "Bronze": "#FF8844",  # Orange-Red (Marginal hands)
    },
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
    Version 1.1 (2025-07-29) - Strategy File Support
    - Added support for loading strategy data from JSON files.
    - Added current strategy file tracking.
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
        """Loads a default set of tiers for a new strategy."""
        self.tiers = [
            HandStrengthTier(
                "Elite",
                40,
                50,
                THEME["tier_colors"]["Elite"],
                ["AA", "KK", "QQ", "JJ", "AKs", "AKo", "AQs"],
            ),
            HandStrengthTier(
                "Premium",
                30,
                39,
                THEME["tier_colors"]["Premium"],
                ["TT", "99", "AJo", "KQs", "AJs", "KJs", "QJs", "JTs", "ATs", "KQo"],
            ),
            HandStrengthTier(
                "Gold",
                20,
                29,
                THEME["tier_colors"]["Gold"],
                ["88", "77", "AQo", "KJo", "A9s", "A8s", "KTs", "QTs", "J9s"],
            ),
            HandStrengthTier(
                "Silver",
                10,
                19,
                THEME["tier_colors"]["Silver"],
                ["66", "55", "44", "A7s", "A6s", "A5s", "K9s", "Q9s", "J8s", "T9s"],
            ),
            HandStrengthTier(
                "Bronze",
                1,
                9,
                THEME["tier_colors"]["Bronze"],
                ["33", "22", "A4s", "A3s", "A2s", "K8s", "Q8s", "J7s", "T8s", "98s"],
            ),
        ]
        self.current_strategy_file = None

        # Create strategy dictionary from default tiers for HS score display
        self.strategy_dict = self._create_strategy_from_tiers()

    def load_strategy_from_file(self, filename: str) -> bool:
        """Loads strategy data from a JSON file."""
        try:
            if not os.path.exists(filename):
                print(f"ERROR: Strategy file '{filename}' not found")
                return False

            with open(filename, "r") as f:
                strategy_data = json.load(f)

            # Store the full strategy data
            self.strategy_dict = strategy_data

            # Extract hand strength data and create tiers
            self._create_tiers_from_strategy(strategy_data)

            # Set current strategy file
            self.current_strategy_file = filename

            print(f"SUCCESS: Loaded strategy from '{filename}'")
            print(f"  - Total hands: {sum(len(tier.hands) for tier in self.tiers)}")
            print(f"  - Tiers: {len(self.tiers)}")

            return True

        except Exception as e:
            print(f"ERROR: Failed to load strategy from '{filename}': {e}")
            return False

    def _create_tiers_from_strategy(self, strategy_data: Dict[str, Any]):
        """Creates tiers from strategy data."""
        self.tiers.clear()

        # Get hand strength table
        hand_strength_table = strategy_data.get("hand_strength_tables", {}).get(
            "preflop", {}
        )

        if not hand_strength_table:
            print("WARNING: No preflop hand strength table found, using default tiers")
            self.load_default_tiers()
            return

        # Group hands by strength ranges
        strength_groups = {}
        for hand, strength in hand_strength_table.items():
            # Determine tier based on strength
            if strength >= 40:
                tier_name = "Elite"
                tier_color = THEME["tier_colors"]["Elite"]
                min_hs, max_hs = 40, 50
            elif strength >= 30:
                tier_name = "Premium"
                tier_color = THEME["tier_colors"]["Premium"]
                min_hs, max_hs = 30, 39
            elif strength >= 20:
                tier_name = "Gold"
                tier_color = THEME["tier_colors"]["Gold"]
                min_hs, max_hs = 20, 29
            elif strength >= 10:
                tier_name = "Silver"
                tier_color = THEME["tier_colors"]["Silver"]
                min_hs, max_hs = 10, 19
            else:
                tier_name = "Bronze"
                tier_color = THEME["tier_colors"]["Bronze"]
                min_hs, max_hs = 1, 9

            # Add to strength group
            if tier_name not in strength_groups:
                strength_groups[tier_name] = {
                    "hands": [],
                    "min_hs": min_hs,
                    "max_hs": max_hs,
                    "color": tier_color,
                }
            strength_groups[tier_name]["hands"].append(hand)

        # Create tiers
        for tier_name, data in strength_groups.items():
            tier = HandStrengthTier(
                name=tier_name,
                min_hs=data["min_hs"],
                max_hs=data["max_hs"],
                color=data["color"],
                hands=sorted(data["hands"]),
            )
            self.tiers.append(tier)

        # Sort tiers by strength
        self.tiers.sort(key=lambda t: t.min_hs, reverse=True)

    def save_strategy_to_file(self, filename: str) -> bool:
        """Saves current strategy data to a JSON file."""
        try:
            # Create strategy data from current tiers
            strategy_data = self._create_strategy_from_tiers()

            with open(filename, "w") as f:
                json.dump(strategy_data, f, indent=2)

            self.current_strategy_file = filename
            print(f"SUCCESS: Saved strategy to '{filename}'")
            return True

        except Exception as e:
            print(f"ERROR: Failed to save strategy to '{filename}': {e}")
            return False

    def _create_strategy_from_tiers(self) -> Dict[str, Any]:
        """Creates strategy data from current tiers with modern PFA/Caller postflop strategy."""
        # Create hand strength table from tiers
        hand_strength_table = {}

        for tier in self.tiers:
            # Assign strength values based on tier
            if tier.name == "Elite":
                base_strength = 45
            elif tier.name == "Premium":
                base_strength = 35
            elif tier.name == "Gold":
                base_strength = 25
            elif tier.name == "Silver":
                base_strength = 15
            else:  # Bronze
                base_strength = 5

            # Assign strength to each hand in the tier
            for i, hand in enumerate(tier.hands):
                # Slightly vary strength within tier
                strength = base_strength - (i * 2)
                hand_strength_table[hand] = max(strength, 1)

        # Modern postflop strategy using PFA/Caller concept
        postflop_strategy = {
            "pfa": {
                "flop": {
                    "UTG": {
                        "val_thresh": 35,  # Strong hands only from UTG
                        "check_thresh": 15,  # Check with medium hands
                        "sizing": 0.75,  # 75% pot sizing
                    },
                    "MP": {
                        "val_thresh": 30,  # Slightly more aggressive
                        "check_thresh": 15,
                        "sizing": 0.7,
                    },
                    "CO": {
                        "val_thresh": 30,  # Cutoff can be more aggressive
                        "check_thresh": 15,
                        "sizing": 0.6,
                    },
                    "BTN": {
                        "val_thresh": 20,  # Button can bet wider
                        "check_thresh": 10,
                        "sizing": 0.5,
                    },
                },
                "turn": {
                    "UTG": {
                        "val_thresh": 40,  # Turn requires stronger hands
                        "check_thresh": 25,
                        "sizing": 0.75,
                    },
                    "MP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75},
                    "CO": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7},
                    "BTN": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.55},
                },
                "river": {
                    "UTG": {
                        "val_thresh": 45,  # River requires strongest hands
                        "check_thresh": 30,
                        "sizing": 1.0,
                    },
                    "MP": {"val_thresh": 45, "check_thresh": 30, "sizing": 1.0},
                    "CO": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.8},
                    "BTN": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7},
                },
            },
            "caller": {
                "flop": {
                    "UTG": {
                        "val_thresh": 40,  # Caller needs stronger hands
                        "check_thresh": 20,
                        "sizing": 0.8,
                    },
                    "MP": {"val_thresh": 40, "check_thresh": 20, "sizing": 0.8},
                    "CO": {"val_thresh": 35, "check_thresh": 18, "sizing": 0.7},
                    "BTN": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6},
                },
                "turn": {
                    "UTG": {"val_thresh": 45, "check_thresh": 30, "sizing": 0.9},
                    "MP": {"val_thresh": 45, "check_thresh": 30, "sizing": 0.9},
                    "CO": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.8},
                    "BTN": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7},
                },
                "river": {
                    "UTG": {"val_thresh": 50, "check_thresh": 35, "sizing": 1.2},
                    "MP": {"val_thresh": 50, "check_thresh": 35, "sizing": 1.2},
                    "CO": {"val_thresh": 45, "check_thresh": 30, "sizing": 1.0},
                    "BTN": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.9},
                },
            },
        }

        # Create strategy structure
        strategy_data = {
            "hand_strength_tables": {
                "preflop": hand_strength_table,
                "postflop": {
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
                },
            },
            "preflop": {
                "open_rules": {
                    "UTG": {"threshold": 30, "sizing": 3.0},
                    "MP": {"threshold": 20, "sizing": 3.0},
                    "CO": {"threshold": 15, "sizing": 2.5},
                    "BTN": {"threshold": 10, "sizing": 2.5},
                    "SB": {"threshold": 20, "sizing": 3.0},
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
        "#FF4444",
        "#44AAFF",
        "#FFAA44",
        "#44FF44",
        "#FF8844",
        "#FF66CC",
        "#66CCFF",
        "#FFFF44",
    ]

    @staticmethod
    def get_all_sizes() -> List[str]:
        return GridSettings._SIZES

    @staticmethod
    def get_size_config(size: str) -> Dict:
        return GridSettings._CONFIGS.get(size, GridSettings._CONFIGS["3"])

    @staticmethod
    def calculate_button_size_for_grid(
        grid_width: int, grid_height: int, size: str
    ) -> Dict:
        """Calculate button size to fill 75% of the grid pane."""
        # Get base config
        base_config = GridSettings.get_size_config(size)

        # Calculate available space for the grid (13x13 grid)
        grid_cells_width = 13
        grid_cells_height = 13

        # Calculate button size to fill 75% of available space
        target_width = int((grid_width * 0.75) / grid_cells_width)
        target_height = int((grid_height * 0.75) / grid_cells_height)

        # Ensure minimum size
        min_width = base_config["button_width"]
        min_height = base_config["button_height"]

        button_width = max(target_width, min_width)
        button_height = max(target_height, min_height)

        return {
            "font": base_config["font"],
            "button_width": button_width,
            "button_height": button_height,
            "label_width": base_config["label_width"],
        }


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
            rank_order = {
                "A": 14,
                "K": 13,
                "Q": 12,
                "J": 11,
                "T": 10,
                "9": 9,
                "8": 8,
                "7": 7,
                "6": 6,
                "5": 5,
                "4": 4,
                "3": 3,
                "2": 2,
            }

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
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
            return None

    @staticmethod
    def save_strategy(strategy: Dict, filename: str) -> bool:
        try:
            with open(filename, "w") as f:
                json.dump(strategy, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
            return False
