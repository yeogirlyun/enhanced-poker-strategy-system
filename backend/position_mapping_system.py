#!/usr/bin/env python3
"""
Comprehensive Position Mapping System for Poker Application

Handles position mapping across different table sizes and naming conventions.
Provides intelligent fallback mechanisms and strategy integration.

REVISION HISTORY:
================
Version 1.0 (2025-01-27) - Initial Version
- Created comprehensive position mapping system
- Handles different table sizes (2-9 players)
- Provides strategy integration with fallback mechanisms
- Supports multiple naming conventions
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class UniversalPosition(Enum):
    """Universal position identifiers that work across all table sizes."""
    BTN = "BTN"      # Button/Dealer
    SB = "SB"        # Small Blind
    BB = "BB"        # Big Blind
    UTG = "UTG"      # Under the Gun (first to act preflop after blinds)
    UTG1 = "UTG+1"   # UTG+1
    UTG2 = "UTG+2"   # UTG+2
    MP = "MP"        # Middle Position
    MP1 = "MP+1"     # MP+1
    MP2 = "MP+2"     # MP+2
    LJ = "LJ"        # Lojack
    HJ = "HJ"        # Hijack
    CO = "CO"        # Cutoff


class PositionMapper:
    """Handles position mapping across different table sizes and naming conventions."""
    
    # Define canonical position orders for each table size
    CANONICAL_POSITIONS = {
        2: ["BTN", "BB"],  # Heads-up: BTN is SB
        3: ["BTN", "SB", "BB"],
        4: ["BTN", "SB", "BB", "UTG"],
        5: ["BTN", "SB", "BB", "UTG", "CO"],
        6: ["BTN", "SB", "BB", "UTG", "MP", "CO"],
        7: ["BTN", "SB", "BB", "UTG", "MP", "LJ", "CO"],
        8: ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "LJ", "CO"],
        9: ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "LJ", "HJ", "CO"]
    }
    
    # Strategy position aliases (what the strategy files might use)
    STRATEGY_ALIASES = {
        "UTG+1": ["MP"],      # In 6-max, MP might be called UTG+1
        "MP": ["UTG+1"],      # And vice versa
        "MP+1": ["LJ"],       # Lojack might be called MP+1
        "MP+2": ["HJ"],       # Hijack might be called MP+2
    }
    
    # Position similarity groups for fallback logic
    POSITION_GROUPS = {
        "EARLY": ["UTG", "UTG+1", "UTG+2"],
        "MIDDLE": ["MP", "MP+1", "MP+2", "LJ"],
        "LATE": ["HJ", "CO", "BTN"],
        "BLINDS": ["SB", "BB"]
    }
    
    # Fallback chains for each position
    FALLBACK_CHAINS = {
        "UTG": ["UTG", "UTG+1", "MP", "EP", "EARLY"],
        "UTG+1": ["UTG+1", "MP", "UTG", "EARLY"],
        "UTG+2": ["UTG+2", "MP", "UTG+1", "EARLY"],
        "MP": ["MP", "UTG+1", "LJ", "MIDDLE"],
        "MP+1": ["MP+1", "LJ", "MP", "MIDDLE"],
        "MP+2": ["MP+2", "HJ", "LJ", "MIDDLE"],
        "LJ": ["LJ", "MP+1", "HJ", "MIDDLE"],
        "HJ": ["HJ", "MP+2", "CO", "LATE"],
        "CO": ["CO", "HJ", "BTN", "LATE"],
        "BTN": ["BTN", "CO", "LATE"],
        "SB": ["SB", "BLINDS"],
        "BB": ["BB", "BLINDS"]
    }
    
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.positions = self.CANONICAL_POSITIONS.get(num_players, [])
        self._build_position_index()
    
    def _build_position_index(self):
        """Build an index for quick position lookups."""
        self.position_to_index = {pos: idx for idx, pos in enumerate(self.positions)}
        self.index_to_position = {idx: pos for idx, pos in enumerate(self.positions)}
    
    def get_position_for_seat(self, seat_index: int, dealer_position: int) -> str:
        """Get the position name for a given seat relative to the dealer."""
        offset = (seat_index - dealer_position) % self.num_players
        if offset < len(self.positions):
            return self.positions[offset]
        return f"SEAT{seat_index}"  # Fallback for unexpected cases
    
    def map_strategy_position(self, actual_position: str, strategy_positions: List[str]) -> Optional[str]:
        """
        Map an actual table position to a strategy position.
        Returns the best matching position from strategy_positions.
        """
        # Direct match
        if actual_position in strategy_positions:
            return actual_position
        
        # Check aliases
        for alias in self.STRATEGY_ALIASES.get(actual_position, []):
            if alias in strategy_positions:
                return alias
        
        # Use fallback chain
        fallback_chain = self.FALLBACK_CHAINS.get(actual_position, [])
        for fallback in fallback_chain:
            if fallback in strategy_positions:
                return fallback
        
        # Group-based fallback
        actual_group = self._get_position_group(actual_position)
        if actual_group:
            for pos in strategy_positions:
                if self._get_position_group(pos) == actual_group:
                    return pos
        
        # Last resort: return first available position
        return strategy_positions[0] if strategy_positions else None
    
    def _get_position_group(self, position: str) -> Optional[str]:
        """Get the group a position belongs to."""
        for group, positions in self.POSITION_GROUPS.items():
            if position in positions:
                return group
        return None
    
    def get_relative_position(self, position: str) -> float:
        """
        Get a normalized position value (0.0 = UTG, 1.0 = BTN).
        Useful for position-aware calculations.
        """
        if position not in self.position_to_index:
            return 0.5  # Default to middle
        
        # Exclude blinds from the calculation
        non_blind_positions = [p for p in self.positions if p not in ["SB", "BB"]]
        if position in ["SB", "BB"]:
            return 0.0  # Treat blinds as early position
        
        try:
            pos_index = non_blind_positions.index(position)
            return pos_index / (len(non_blind_positions) - 1)
        except (ValueError, ZeroDivisionError):
            return 0.5


class EnhancedStrategyIntegration:
    """Integrates position mapping with strategy lookup."""
    
    def __init__(self, strategy_data, num_players: int):
        self.strategy_data = strategy_data
        self.position_mapper = PositionMapper(num_players)
        self._validate_strategy_positions()
    
    def _validate_strategy_positions(self):
        """Validate and log available strategy positions."""
        self.available_positions = set()
        
        # Check preflop positions
        preflop = self.strategy_data.get("preflop", {})
        for section in ["open_rules", "vs_raise"]:
            if section in preflop:
                self.available_positions.update(preflop[section].keys())
        
        # Check postflop positions
        postflop = self.strategy_data.get("postflop", {})
        for action_type in ["pfa", "caller"]:
            if action_type in postflop:
                for street in ["flop", "turn", "river"]:
                    if street in postflop[action_type]:
                        self.available_positions.update(postflop[action_type][street].keys())
        
        print(f"Available strategy positions: {sorted(self.available_positions)}")
    
    def get_strategy_for_position(self, actual_position: str, street: str, 
                                  action_context: str = "open") -> Dict:
        """
        Get strategy parameters for a position with intelligent fallback.
        
        Args:
            actual_position: The actual table position (e.g., "MP" in 6-max)
            street: Current betting round
            action_context: "open", "vs_raise", "pfa", "caller"
        """
        # Map to available strategy position
        strategy_positions = list(self.available_positions)
        mapped_position = self.position_mapper.map_strategy_position(
            actual_position, strategy_positions
        )
        
        if not mapped_position:
            print(f"WARNING: No mapping found for {actual_position}, using defaults")
            return self._get_default_strategy(street, action_context)
        
        # Retrieve strategy
        if street == "preflop":
            if action_context == "open":
                return self.strategy_data["preflop"]["open_rules"].get(
                    mapped_position, self._get_default_strategy(street, action_context)
                )
            else:  # vs_raise
                return self.strategy_data["preflop"]["vs_raise"].get(
                    mapped_position, self._get_default_strategy(street, action_context)
                )
        else:  # postflop
            action_type = "pfa" if action_context == "pfa" else "caller"
            return self.strategy_data["postflop"][action_type][street].get(
                mapped_position, self._get_default_strategy(street, action_context)
            )
    
    def _get_default_strategy(self, street: str, action_context: str) -> Dict:
        """Provide sensible defaults based on context."""
        if street == "preflop":
            if action_context == "open":
                return {"threshold": 50, "sizing": 3.0}
            else:  # vs_raise
                return {"value_thresh": 70, "call_thresh": 60, "sizing": 3.0}
        else:  # postflop
            return {"val_thresh": 30, "check_thresh": 15, "sizing": 0.75}


class HandHistoryManager:
    """Separate class to manage hand history without test corruption."""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.hand_history = []
        self.action_log = []
    
    def log_action(self, player, action, amount: float, game_state):
        """Log action with proper handling for test mode."""
        from dataclasses import dataclass
        from datetime import datetime
        
        @dataclass
        class HandHistoryLog:
            timestamp: float
            street: str
            player_name: str
            action: str
            amount: float
            pot_size: float
            board: List[str]
            player_states: List[dict]
        
        log_entry = HandHistoryLog(
            timestamp=time.time(),
            street=game_state.street,
            player_name=player.name,
            action=action.value if hasattr(action, 'value') else str(action),
            amount=amount,
            pot_size=game_state.pot,
            board=game_state.board.copy(),
            player_states=self._capture_player_states(game_state)
        )
        
        # Normal logging
        self.hand_history.append(log_entry)
        
        # Test mode handling (if needed)
        if self.test_mode and hasattr(action, 'value') and action.value == "raise":
            self._handle_test_raise(log_entry)
    
    def _capture_player_states(self, game_state):
        """Capture simplified player states for logging."""
        return [
            {
                "name": p.name,
                "stack": p.stack,
                "current_bet": p.current_bet,
                "is_active": p.is_active,
                "is_all_in": p.is_all_in
            }
            for p in game_state.players
        ]
    
    def _handle_test_raise(self, raise_entry):
        """Handle raise actions in test mode without corrupting production data."""
        # Create a separate test history if needed
        if not hasattr(self, 'test_history'):
            self.test_history = []
        self.test_history.append(raise_entry)
    
    def get_hand_history(self):
        """Get the current hand history."""
        return self.hand_history
    
    def clear_history(self):
        """Clear the hand history."""
        self.hand_history = []
        if hasattr(self, 'test_history'):
            self.test_history = [] 