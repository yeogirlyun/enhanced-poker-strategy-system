#!/usr/bin/env python3
"""
Dynamic Position Management System

This module provides dynamic position calculation based on dealer button location,
replacing hardcoded position lists with flexible, table-size-aware logic.
"""

from typing import List, Dict, Optional
from enum import Enum


class Position(Enum):
    """Poker positions."""
    BTN = "BTN"  # Button/Dealer
    SB = "SB"    # Small Blind
    BB = "BB"    # Big Blind
    UTG = "UTG"  # Under the Gun
    MP = "MP"    # Middle Position
    CO = "CO"    # Cutoff
    LJ = "LJ"    # LoJack (for 8+ players)
    HJ = "HJ"    # Hijack (for 9 players)


class DynamicPositionManager:
    """Manages dynamic position calculation based on table size and dealer location."""
    
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.dealer_seat = 0  # Current dealer position
        self._validate_table_size()
        self._setup_position_mappings()
    
    def _validate_table_size(self):
        """Validate that table size is supported."""
        if not 3 <= self.num_players <= 9:
            raise ValueError(f"Table size {self.num_players} not supported. Must be 3-9 players.")
    
    def _setup_position_mappings(self):
        """Setup position mappings for different table sizes."""
        self.position_mappings = {
            3: [Position.BTN, Position.SB, Position.BB],
            4: [Position.BTN, Position.SB, Position.BB, Position.UTG],
            5: [Position.BTN, Position.SB, Position.BB, Position.UTG, Position.MP],
            6: [Position.BTN, Position.SB, Position.BB, Position.UTG, Position.MP, Position.CO],
            7: [Position.BTN, Position.SB, Position.BB, Position.UTG, Position.MP, Position.LJ, Position.CO],
            8: [Position.BTN, Position.SB, Position.BB, Position.UTG, Position.MP, Position.LJ, Position.CO, Position.HJ],
            9: [Position.BTN, Position.SB, Position.BB, Position.UTG, Position.MP, Position.LJ, Position.HJ, Position.CO, Position.BTN]
        }
    
    def move_dealer_button(self):
        """Move dealer button to next position."""
        self.dealer_seat = (self.dealer_seat + 1) % self.num_players
    
    def get_position_for_seat(self, seat_number: int) -> str:
        """
        Get position name for a given seat based on dealer location.
        
        Args:
            seat_number: Seat number (0-based)
            
        Returns:
            Position name as string
        """
        if not 0 <= seat_number < self.num_players:
            return "INVALID"
        
        # Calculate offset from dealer
        offset = (seat_number - self.dealer_seat + self.num_players) % self.num_players
        position_list = self.position_mappings[self.num_players]
        
        if offset < len(position_list):
            return position_list[offset].value
        else:
            return "UNKNOWN"
    
    def get_action_order(self, street: str = 'preflop') -> List[int]:
        """
        Get action order for current street.
        
        Args:
            street: Street name ('preflop', 'flop', 'turn', 'river')
            
        Returns:
            List of seat numbers in action order
        """
        if street == 'preflop':
            # Preflop: UTG first (3 seats after button)
            start_seat = (self.dealer_seat + 3) % self.num_players
        else:
            # Postflop: SB first (1 seat after button)
            start_seat = (self.dealer_seat + 1) % self.num_players
        
        action_order = []
        for i in range(self.num_players):
            seat = (start_seat + i) % self.num_players
            action_order.append(seat)
        
        return action_order
    
    def get_blind_positions(self) -> Dict[str, int]:
        """
        Get small blind and big blind positions.
        
        Returns:
            Dictionary with 'sb' and 'bb' seat numbers
        """
        sb_seat = (self.dealer_seat + 1) % self.num_players
        bb_seat = (self.dealer_seat + 2) % self.num_players
        
        return {
            'sb': sb_seat,
            'bb': bb_seat
        }
    
    def get_all_positions(self) -> List[str]:
        """
        Get all positions for current table state.
        
        Returns:
            List of position names in seat order
        """
        positions = []
        for seat in range(self.num_players):
            positions.append(self.get_position_for_seat(seat))
        return positions
    
    def get_position_info(self) -> Dict[str, Dict]:
        """
        Get comprehensive position information.
        
        Returns:
            Dictionary with position details
        """
        info = {
            'dealer_seat': self.dealer_seat,
            'table_size': self.num_players,
            'positions': self.get_all_positions(),
            'blinds': self.get_blind_positions(),
            'preflop_action_order': self.get_action_order('preflop'),
            'postflop_action_order': self.get_action_order('flop')
        }
        return info
    
    def is_valid_position(self, position: str) -> bool:
        """
        Check if a position name is valid for current table size.
        
        Args:
            position: Position name to validate
            
        Returns:
            True if position is valid for current table
        """
        valid_positions = [pos.value for pos in self.position_mappings[self.num_players]]
        return position in valid_positions
    
    def get_seat_for_position(self, position: str) -> Optional[int]:
        """
        Get seat number for a specific position.
        
        Args:
            position: Position name
            
        Returns:
            Seat number or None if position not found
        """
        for seat in range(self.num_players):
            if self.get_position_for_seat(seat) == position:
                return seat
        return None


# Example usage and testing
if __name__ == "__main__":
    # Test with 6-max table
    pos_manager = DynamicPositionManager(6)
    
    print("=== 6-Max Table Position Test ===")
    print(f"Initial positions: {pos_manager.get_all_positions()}")
    print(f"Dealer seat: {pos_manager.dealer_seat}")
    print(f"Blind positions: {pos_manager.get_blind_positions()}")
    print(f"Preflop action order: {pos_manager.get_action_order('preflop')}")
    
    # Move dealer button
    pos_manager.move_dealer_button()
    print(f"\nAfter moving dealer:")
    print(f"Positions: {pos_manager.get_all_positions()}")
    print(f"Dealer seat: {pos_manager.dealer_seat}") 