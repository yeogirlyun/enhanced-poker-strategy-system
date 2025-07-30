"""
Janggi Board Implementation

This module contains the Janggi board class and related game logic.
"""

from typing import List, Optional, Tuple
from enum import Enum


class PieceType(Enum):
    """Enumeration of Janggi piece types."""
    GENERAL = "general"      # King
    ADVISOR = "advisor"      # Advisor
    ELEPHANT = "elephant"    # Elephant
    HORSE = "horse"          # Horse
    CHARIOT = "chariot"      # Chariot
    CANNON = "cannon"        # Cannon
    SOLDIER = "soldier"      # Soldier


class Player(Enum):
    """Enumeration of players."""
    RED = "red"
    BLUE = "blue"


class Piece:
    """Represents a Janggi piece."""
    
    def __init__(self, piece_type: PieceType, player: Player, position: Tuple[int, int]):
        self.piece_type = piece_type
        self.player = player
        self.position = position
        self.has_moved = False
    
    def __str__(self) -> str:
        return f"{self.player.value}_{self.piece_type.value}"
    
    def get_symbol(self) -> str:
        """Get the Unicode symbol for this piece."""
        symbols = {
            (Player.RED, PieceType.GENERAL): "帥",
            (Player.BLUE, PieceType.GENERAL): "將",
            (Player.RED, PieceType.ADVISOR): "仕",
            (Player.BLUE, PieceType.ADVISOR): "士",
            (Player.RED, PieceType.ELEPHANT): "相",
            (Player.BLUE, PieceType.ELEPHANT): "象",
            (Player.RED, PieceType.HORSE): "傌",
            (Player.BLUE, PieceType.HORSE): "馬",
            (Player.RED, PieceType.CHARIOT): "俥",
            (Player.BLUE, PieceType.CHARIOT): "車",
            (Player.RED, PieceType.CANNON): "炮",
            (Player.BLUE, PieceType.CANNON): "砲",
            (Player.RED, PieceType.SOLDIER): "兵",
            (Player.BLUE, PieceType.SOLDIER): "卒",
        }
        return symbols.get((self.player, self.piece_type), "?")


class JanggiBoard:
    """Represents a Janggi game board."""
    
    def __init__(self):
        self.width = 9
        self.height = 10
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.current_player = Player.RED
        self.game_over = False
        self.winner = None
        
        self._initialize_board()
    
    def _initialize_board(self):
        """Initialize the board with pieces in their starting positions."""
        # Red pieces (bottom)
        self._place_piece(Piece(PieceType.CHARIOT, Player.RED, (0, 9)), (0, 9))
        self._place_piece(Piece(PieceType.HORSE, Player.RED, (1, 9)), (1, 9))
        self._place_piece(Piece(PieceType.ELEPHANT, Player.RED, (2, 9)), (2, 9))
        self._place_piece(Piece(PieceType.ADVISOR, Player.RED, (3, 9)), (3, 9))
        self._place_piece(Piece(PieceType.GENERAL, Player.RED, (4, 9)), (4, 9))
        self._place_piece(Piece(PieceType.ADVISOR, Player.RED, (5, 9)), (5, 9))
        self._place_piece(Piece(PieceType.ELEPHANT, Player.RED, (6, 9)), (6, 9))
        self._place_piece(Piece(PieceType.HORSE, Player.RED, (7, 9)), (7, 9))
        self._place_piece(Piece(PieceType.CHARIOT, Player.RED, (8, 9)), (8, 9))
        self._place_piece(Piece(PieceType.CANNON, Player.RED, (1, 7)), (1, 7))
        self._place_piece(Piece(PieceType.CANNON, Player.RED, (7, 7)), (7, 7))
        self._place_piece(Piece(PieceType.SOLDIER, Player.RED, (0, 6)), (0, 6))
        self._place_piece(Piece(PieceType.SOLDIER, Player.RED, (2, 6)), (2, 6))
        self._place_piece(Piece(PieceType.SOLDIER, Player.RED, (4, 6)), (4, 6))
        self._place_piece(Piece(PieceType.SOLDIER, Player.RED, (6, 6)), (6, 6))
        self._place_piece(Piece(PieceType.SOLDIER, Player.RED, (8, 6)), (8, 6))
        
        # Blue pieces (top)
        self._place_piece(Piece(PieceType.CHARIOT, Player.BLUE, (0, 0)), (0, 0))
        self._place_piece(Piece(PieceType.HORSE, Player.BLUE, (1, 0)), (1, 0))
        self._place_piece(Piece(PieceType.ELEPHANT, Player.BLUE, (2, 0)), (2, 0))
        self._place_piece(Piece(PieceType.ADVISOR, Player.BLUE, (3, 0)), (3, 0))
        self._place_piece(Piece(PieceType.GENERAL, Player.BLUE, (4, 0)), (4, 0))
        self._place_piece(Piece(PieceType.ADVISOR, Player.BLUE, (5, 0)), (5, 0))
        self._place_piece(Piece(PieceType.ELEPHANT, Player.BLUE, (6, 0)), (6, 0))
        self._place_piece(Piece(PieceType.HORSE, Player.BLUE, (7, 0)), (7, 0))
        self._place_piece(Piece(PieceType.CHARIOT, Player.BLUE, (8, 0)), (8, 0))
        self._place_piece(Piece(PieceType.CANNON, Player.BLUE, (1, 2)), (1, 2))
        self._place_piece(Piece(PieceType.CANNON, Player.BLUE, (7, 2)), (7, 2))
        self._place_piece(Piece(PieceType.SOLDIER, Player.BLUE, (0, 3)), (0, 3))
        self._place_piece(Piece(PieceType.SOLDIER, Player.BLUE, (2, 3)), (2, 3))
        self._place_piece(Piece(PieceType.SOLDIER, Player.BLUE, (4, 3)), (4, 3))
        self._place_piece(Piece(PieceType.SOLDIER, Player.BLUE, (6, 3)), (6, 3))
        self._place_piece(Piece(PieceType.SOLDIER, Player.BLUE, (8, 3)), (8, 3))
    
    def _place_piece(self, piece: Piece, position: Tuple[int, int]):
        """Place a piece on the board."""
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            self.board[y][x] = piece
            piece.position = position
    
    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        """Get the piece at the given position."""
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.board[y][x]
        return None
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is valid on the board."""
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_palace(self, position: Tuple[int, int]) -> bool:
        """Check if a position is in the palace area."""
        x, y = position
        return 3 <= x <= 5 and (y <= 2 or y >= 7)
    
    def get_valid_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all valid moves for a piece at the given position."""
        piece = self.get_piece(position)
        if not piece or piece.player != self.current_player:
            return []
        
        # TODO: Implement move validation logic for each piece type
        # This is a placeholder - actual implementation will be more complex
        moves = []
        
        # For now, return all adjacent positions as valid moves
        x, y = position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_pos = (x + dx, y + dy)
                if self.is_valid_position(new_pos):
                    target_piece = self.get_piece(new_pos)
                    if not target_piece or target_piece.player != piece.player:
                        moves.append(new_pos)
        
        return moves
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Make a move on the board."""
        piece = self.get_piece(from_pos)
        if not piece or piece.player != self.current_player:
            return False
        
        valid_moves = self.get_valid_moves(from_pos)
        if to_pos not in valid_moves:
            return False
        
        # Capture piece if present
        captured_piece = self.get_piece(to_pos)
        if captured_piece and captured_piece.piece_type == PieceType.GENERAL:
            self.game_over = True
            self.winner = self.current_player
        
        # Move the piece
        self.board[from_pos[1]][from_pos[0]] = None
        self.board[to_pos[1]][to_pos[0]] = piece
        piece.position = to_pos
        piece.has_moved = True
        
        # Switch players
        self.current_player = Player.BLUE if self.current_player == Player.RED else Player.RED
        
        return True
    
    def get_board_state(self) -> List[List[Optional[str]]]:
        """Get the current board state as a 2D array of piece symbols."""
        state = []
        for row in self.board:
            state_row = []
            for piece in row:
                if piece:
                    state_row.append(piece.get_symbol())
                else:
                    state_row.append("")
            state.append(state_row)
        return state
    
    def __str__(self) -> str:
        """String representation of the board."""
        result = "  " + " ".join(str(i) for i in range(self.width)) + "\n"
        for y in range(self.height):
            result += f"{y} "
            for x in range(self.width):
                piece = self.board[y][x]
                if piece:
                    result += piece.get_symbol() + " "
                else:
                    result += ". "
            result += "\n"
        return result 