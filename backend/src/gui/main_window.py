"""
Janggi Main Window

This module contains the main GUI window for the Janggi game.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple

from game.board import JanggiBoard, Player


class JanggiMainWindow:
    """Main window for the Janggi game."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.board = JanggiBoard()
        self.selected_position: Optional[Tuple[int, int]] = None
        self.cell_size = 60
        self.board_frame = None
        self.status_label = None
        
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Configure the main window
        self.root.title("Janggi - Korean Chess")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create title
        title_label = ttk.Label(main_frame, text="Janggi (Korean Chess)", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Create board frame
        self.board_frame = ttk.Frame(main_frame)
        self.board_frame.grid(row=1, column=0, padx=(0, 10))
        
        # Create control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # New game button
        new_game_btn = ttk.Button(control_frame, text="New Game", 
                                 command=self._new_game)
        new_game_btn.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Red's turn", 
                                     font=("Arial", 12))
        self.status_label.pack(pady=(0, 10))
        
        # Game info
        info_frame = ttk.LabelFrame(control_frame, text="Game Info", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Red: 帥 (General)").pack(anchor=tk.W)
        ttk.Label(info_frame, text="Blue: 將 (General)").pack(anchor=tk.W)
        
        # Rules info
        rules_frame = ttk.LabelFrame(control_frame, text="Rules", padding="5")
        rules_frame.pack(fill=tk.X)
        
        rules_text = """• Click a piece to select it
• Click a valid square to move
• Capture the enemy general to win
• Pieces move according to Janggi rules"""
        
        ttk.Label(rules_frame, text=rules_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Bind board clicks
        self._create_board()
    
    def _create_board(self):
        """Create the visual board with clickable squares."""
        # Create board squares
        for y in range(self.board.height):
            for x in range(self.board.width):
                # Create frame for each square
                square_frame = tk.Frame(self.board_frame, 
                                      width=self.cell_size, 
                                      height=self.cell_size,
                                      relief=tk.RAISED, 
                                      borderwidth=1)
                square_frame.grid(row=y, column=x)
                square_frame.grid_propagate(False)
                
                # Create label for piece display
                piece_label = tk.Label(square_frame, text="", 
                                     font=("Arial", 20),
                                     bg="white")
                piece_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                # Store reference to label
                square_frame.piece_label = piece_label
                
                # Bind click events
                square_frame.bind("<Button-1>", 
                                lambda e, pos=(x, y): self._on_square_click(pos))
                piece_label.bind("<Button-1>", 
                               lambda e, pos=(x, y): self._on_square_click(pos))
                
                # Color alternating squares
                if (x + y) % 2 == 0:
                    square_frame.configure(bg="lightgray")
                    piece_label.configure(bg="lightgray")
    
    def _on_square_click(self, position: Tuple[int, int]):
        """Handle square click events."""
        if self.board.game_over:
            return
        
        if self.selected_position is None:
            # Select a piece
            piece = self.board.get_piece(position)
            if piece and piece.player == self.board.current_player:
                self.selected_position = position
                self._highlight_square(position, "yellow")
        else:
            # Try to make a move
            if self.board.make_move(self.selected_position, position):
                # Move successful
                self._clear_highlights()
                self.selected_position = None
                self._update_display()
                
                # Check for game over
                if self.board.game_over:
                    winner = "Red" if self.board.winner == Player.RED else "Blue"
                    messagebox.showinfo("Game Over", f"{winner} wins!")
                else:
                    # Update status
                    current_player = "Red" if self.board.current_player == Player.RED else "Blue"
                    self.status_label.config(text=f"{current_player}'s turn")
            else:
                # Invalid move, try to select different piece
                piece = self.board.get_piece(position)
                if piece and piece.player == self.board.current_player:
                    self._clear_highlights()
                    self.selected_position = position
                    self._highlight_square(position, "yellow")
                else:
                    # Clear selection
                    self._clear_highlights()
                    self.selected_position = None
    
    def _highlight_square(self, position: Tuple[int, int], color: str):
        """Highlight a square with the given color."""
        x, y = position
        square_frame = self.board_frame.grid_slaves(row=y, column=x)[0]
        square_frame.configure(bg=color)
        square_frame.piece_label.configure(bg=color)
    
    def _clear_highlights(self):
        """Clear all square highlights."""
        for y in range(self.board.height):
            for x in range(self.board.width):
                square_frame = self.board_frame.grid_slaves(row=y, column=x)[0]
                bg_color = "lightgray" if (x + y) % 2 == 0 else "white"
                square_frame.configure(bg=bg_color)
                square_frame.piece_label.configure(bg=bg_color)
    
    def _update_display(self):
        """Update the visual display of the board."""
        for y in range(self.board.height):
            for x in range(self.board.width):
                piece = self.board.get_piece((x, y))
                square_frame = self.board_frame.grid_slaves(row=y, column=x)[0]
                piece_label = square_frame.piece_label
                
                if piece:
                    piece_label.config(text=piece.get_symbol())
                    # Color pieces based on player
                    if piece.player == Player.RED:
                        piece_label.config(fg="red")
                    else:
                        piece_label.config(fg="blue")
                else:
                    piece_label.config(text="")
    
    def _new_game(self):
        """Start a new game."""
        self.board = JanggiBoard()
        self.selected_position = None
        self._clear_highlights()
        self._update_display()
        self.status_label.config(text="Red's turn") 