"""
Tests for the Janggi board implementation.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from game.board import JanggiBoard, Piece, PieceType, Player


class TestJanggiBoard:
    """Test cases for the JanggiBoard class."""
    
    def test_board_initialization(self):
        """Test that the board initializes correctly."""
        board = JanggiBoard()
        
        assert board.width == 9
        assert board.height == 10
        assert board.current_player == Player.RED
        assert not board.game_over
        assert board.winner is None
    
    def test_piece_placement(self):
        """Test that pieces are placed correctly on initialization."""
        board = JanggiBoard()
        
        # Check that generals are placed
        red_general = board.get_piece((4, 9))
        blue_general = board.get_piece((4, 0))
        
        assert red_general is not None
        assert red_general.piece_type == PieceType.GENERAL
        assert red_general.player == Player.RED
        
        assert blue_general is not None
        assert blue_general.piece_type == PieceType.GENERAL
        assert blue_general.player == Player.BLUE
    
    def test_valid_position_check(self):
        """Test position validation."""
        board = JanggiBoard()
        
        # Valid positions
        assert board.is_valid_position((0, 0))
        assert board.is_valid_position((4, 4))
        assert board.is_valid_position((8, 9))
        
        # Invalid positions
        assert not board.is_valid_position((-1, 0))
        assert not board.is_valid_position((0, -1))
        assert not board.is_valid_position((9, 0))
        assert not board.is_valid_position((0, 10))
    
    def test_palace_check(self):
        """Test palace area detection."""
        board = JanggiBoard()
        
        # Palace positions (3-5 x, 0-2 or 7-9 y)
        assert board.is_palace((3, 0))
        assert board.is_palace((4, 1))
        assert board.is_palace((5, 2))
        assert board.is_palace((3, 7))
        assert board.is_palace((4, 8))
        assert board.is_palace((5, 9))
        
        # Non-palace positions
        assert not board.is_palace((0, 0))
        assert not board.is_palace((8, 4))
        assert not board.is_palace((2, 5))
        assert not board.is_palace((6, 3))
    
    def test_piece_symbols(self):
        """Test that pieces have correct symbols."""
        # Test red pieces
        red_general = Piece(PieceType.GENERAL, Player.RED, (0, 0))
        red_soldier = Piece(PieceType.SOLDIER, Player.RED, (0, 0))
        
        assert red_general.get_symbol() == "帥"
        assert red_soldier.get_symbol() == "兵"
        
        # Test blue pieces
        blue_general = Piece(PieceType.GENERAL, Player.BLUE, (0, 0))
        blue_soldier = Piece(PieceType.SOLDIER, Player.BLUE, (0, 0))
        
        assert blue_general.get_symbol() == "將"
        assert blue_soldier.get_symbol() == "卒"
    
    def test_board_state(self):
        """Test board state representation."""
        board = JanggiBoard()
        state = board.get_board_state()
        
        assert len(state) == 10  # height
        assert len(state[0]) == 9  # width
        
        # Check that generals are in the state
        assert state[9][4] == "帥"  # Red general
        assert state[0][4] == "將"  # Blue general


if __name__ == "__main__":
    pytest.main([__file__]) 