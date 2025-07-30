#!/usr/bin/env python3
"""
Visual Poker Table Simulation

A graphical poker table that shows:
- Players positioned around the table
- Dealer button
- Hole cards for each player
- Community cards (flop, turn, river)
- Pot and betting information
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from poker_practice_simulator import PokerPracticeSimulator, Player, GameState, Action, Position
from gui_models import StrategyData, THEME


class VisualPokerTable:
    """Visual poker table with graphical representation."""
    
    def __init__(self, parent_frame, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.simulator = PokerPracticeSimulator(strategy_data)
        self.current_game_state: Optional[GameState] = None
        
        # Table dimensions
        self.table_width = 600
        self.table_height = 400
        self.player_radius = 150
        self.center_x = self.table_width // 2
        self.center_y = self.table_height // 2
        
        # Card dimensions
        self.card_width = 40
        self.card_height = 60
        
        # Create canvas
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.table_width,
            height=self.table_height,
            bg="#0B6623",  # Green felt
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game controls
        self._create_controls(parent_frame)
        
        # Initialize table
        self._draw_table()
        
    def _create_controls(self, parent_frame):
        """Create game control buttons."""
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Player count
        ttk.Label(control_frame, text="Players:").pack(side=tk.LEFT, padx=5)
        self.player_count_var = tk.StringVar(value="6")
        player_combo = ttk.Combobox(
            control_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly",
            width=5
        )
        player_combo.pack(side=tk.LEFT, padx=5)
        
        # Start hand button
        start_button = ttk.Button(
            control_frame,
            text="🎯 Start New Hand",
            command=self._start_visual_hand
        )
        start_button.pack(side=tk.LEFT, padx=10)
        
        # Action controls
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.RIGHT, padx=10)
        
        self.action_var = tk.StringVar(value="check")
        actions = [("Fold", "fold"), ("Check", "check"), ("Call", "call"), ("Bet", "bet"), ("Raise", "raise")]
        
        for text, value in actions:
            ttk.Radiobutton(
                action_frame,
                text=text,
                variable=self.action_var,
                value=value
            ).pack(side=tk.LEFT, padx=2)
        
        # Bet size
        ttk.Label(action_frame, text="Bet:").pack(side=tk.LEFT, padx=5)
        self.bet_size_var = tk.StringVar(value="0")
        bet_entry = ttk.Entry(action_frame, textvariable=self.bet_size_var, width=8)
        bet_entry.pack(side=tk.LEFT, padx=2)
        
        # Submit action
        submit_button = ttk.Button(
            action_frame,
            text="Submit",
            command=self._submit_visual_action
        )
        submit_button.pack(side=tk.LEFT, padx=5)
        
    def _draw_table(self):
        """Draw the poker table."""
        # Draw table outline
        self.canvas.create_oval(
            50, 50, self.table_width - 50, self.table_height - 50,
            fill="#0B6623", outline="#8B4513", width=3
        )
        
        # Draw table felt pattern
        for i in range(0, self.table_width, 20):
            for j in range(0, self.table_height, 20):
                if (i - self.center_x) ** 2 + (j - self.center_y) ** 2 < (self.player_radius - 20) ** 2:
                    self.canvas.create_oval(i, j, i + 2, j + 2, fill="#228B22", outline="")
        
        # Draw pot area
        self.canvas.create_oval(
            self.center_x - 30, self.center_y - 30,
            self.center_x + 30, self.center_y + 30,
            fill="#FFD700", outline="#B8860B", width=2
        )
        
        # Draw dealer button
        self.canvas.create_oval(
            self.center_x - 15, self.center_y - 15,
            self.center_x + 15, self.center_y + 15,
            fill="white", outline="black", width=2
        )
        self.canvas.create_text(
            self.center_x, self.center_y,
            text="D", font=("Arial", 12, "bold"), fill="black"
        )
        
    def _get_player_position(self, player_index: int, total_players: int) -> Tuple[int, int]:
        """Calculate player position around the table."""
        # Start from bottom (south) and go clockwise
        angle = (player_index * 2 * math.pi / total_players) - math.pi / 2
        x = self.center_x + int(self.player_radius * math.cos(angle))
        y = self.center_y + int(self.player_radius * math.sin(angle))
        return x, y
        
    def _draw_player(self, player: Player, position: Tuple[int, int], is_current_player: bool = False):
        """Draw a player at the given position."""
        x, y = position
        
        # Player circle
        color = "#FF6B6B" if player.is_human else "#4ECDC4"
        if not player.is_active:
            color = "#95A5A6"  # Gray for folded players
        
        self.canvas.create_oval(
            x - 25, y - 25, x + 25, y + 25,
            fill=color, outline="black", width=2
        )
        
        # Player name
        name = "You" if player.is_human else f"P{player.name.split()[-1]}"
        self.canvas.create_text(
            x, y - 5,
            text=name,
            font=("Arial", 10, "bold"),
            fill="white"
        )
        
        # Position
        self.canvas.create_text(
            x, y + 10,
            text=player.position.value,
            font=("Arial", 8),
            fill="white"
        )
        
        # Stack size
        self.canvas.create_text(
            x, y + 35,
            text=f"${player.stack:.0f}",
            font=("Arial", 8),
            fill="white"
        )
        
        # Draw hole cards if player has them
        if player.cards and (player.is_human or not player.is_active):
            self._draw_hole_cards(player, position)
            
    def _draw_hole_cards(self, player: Player, position: Tuple[int, int]):
        """Draw player's hole cards."""
        x, y = position
        
        # Position cards below player
        card_y = y + 50
        
        for i, card in enumerate(player.cards):
            card_x = x - 25 + (i * 30)
            
            # Card background
            card_color = "#FFD700" if player.is_human else "#FFFFFF"
            self.canvas.create_rectangle(
                card_x, card_y,
                card_x + self.card_width, card_y + self.card_height,
                fill=card_color, outline="black", width=2
            )
            
            # Card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"
            
            self.canvas.create_text(
                card_x + self.card_width // 2, card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 12, "bold"),
                fill=color
            )
            
    def _draw_community_cards(self):
        """Draw community cards in the center."""
        if not self.current_game_state or not self.current_game_state.board:
            return
            
        # Position cards in center
        start_x = self.center_x - (len(self.current_game_state.board) * 25)
        
        for i, card in enumerate(self.current_game_state.board):
            card_x = start_x + (i * 50)
            card_y = self.center_y - 30
            
            # Card background
            self.canvas.create_rectangle(
                card_x, card_y,
                card_x + self.card_width, card_y + self.card_height,
                fill="#FFFFFF", outline="black", width=2
            )
            
            # Card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"
            
            self.canvas.create_text(
                card_x + self.card_width // 2, card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 12, "bold"),
                fill=color
            )
            
    def _draw_pot_info(self):
        """Draw pot and betting information."""
        if not self.current_game_state:
            return
            
        # Pot amount
        self.canvas.create_text(
            self.center_x, self.center_y,
            text=f"${self.current_game_state.pot:.0f}",
            font=("Arial", 14, "bold"),
            fill="black"
        )
        
        # Current bet
        if self.current_game_state.current_bet > 0:
            self.canvas.create_text(
                self.center_x, self.center_y + 20,
                text=f"Bet: ${self.current_game_state.current_bet:.0f}",
                font=("Arial", 10),
                fill="white"
            )
            
    def _draw_street_info(self):
        """Draw current street information."""
        if not self.current_game_state:
            return
            
        # Street name
        street_text = self.current_game_state.street.upper()
        self.canvas.create_text(
            self.center_x, 30,
            text=street_text,
            font=("Arial", 16, "bold"),
            fill="white"
        )
        
    def _start_visual_hand(self):
        """Start a new visual hand."""
        try:
            num_players = int(self.player_count_var.get())
            result = self.simulator.play_hand(num_players)
            
            # Get current game state
            self.current_game_state = self.simulator.current_game_state
            
            # Redraw the table
            self._redraw_table()
            
            messagebox.showinfo(
                "Hand Started",
                f"New hand started with {num_players} players!\n"
                f"Your position: {self.current_game_state.players[0].position.value}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start hand: {str(e)}")
            
    def _submit_visual_action(self):
        """Submit action in visual mode."""
        if not self.current_game_state:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return
            
        try:
            # Get action from UI
            action_str = self.action_var.get()
            bet_size = float(self.bet_size_var.get())
            
            action_map = {
                "fold": Action.FOLD,
                "check": Action.CHECK,
                "call": Action.CALL,
                "bet": Action.BET,
                "raise": Action.RAISE
            }
            
            action = action_map.get(action_str, Action.CHECK)
            
            # Execute action
            human_player = next(p for p in self.current_game_state.players if p.is_human)
            self.simulator.execute_action(human_player, action, bet_size, self.current_game_state)
            
            # Redraw table
            self._redraw_table()
            
            # Show feedback
            self._show_action_feedback(action, bet_size)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit action: {str(e)}")
            
    def _show_action_feedback(self, action: Action, bet_size: float):
        """Show feedback for the submitted action."""
        if not self.simulator.deviation_logs:
            return
            
        latest_deviation = self.simulator.deviation_logs[-1]
        feedback = self.simulator.get_feedback_message(latest_deviation)
        
        # Create feedback window
        feedback_window = tk.Toplevel()
        feedback_window.title("Action Feedback")
        feedback_window.geometry("400x200")
        
        feedback_text = tk.Text(
            feedback_window,
            font=("Arial", 12),
            wrap="word",
            padx=10,
            pady=10
        )
        feedback_text.pack(fill=tk.BOTH, expand=True)
        
        feedback_text.insert(tk.END, f"Your Action: {action.value}\n")
        if bet_size > 0:
            feedback_text.insert(tk.END, f"Bet Size: ${bet_size:.2f}\n\n")
        feedback_text.insert(tk.END, f"Strategy Feedback:\n{feedback}")
        
        # Close button
        ttk.Button(
            feedback_window,
            text="OK",
            command=feedback_window.destroy
        ).pack(pady=10)
        
    def _redraw_table(self):
        """Redraw the entire table with current game state."""
        # Clear canvas
        self.canvas.delete("all")
        
        # Redraw table
        self._draw_table()
        
        if self.current_game_state:
            # Draw players
            for i, player in enumerate(self.current_game_state.players):
                position = self._get_player_position(i, len(self.current_game_state.players))
                self._draw_player(player, position, i == 0)  # First player is current
                
            # Draw community cards
            self._draw_community_cards()
            
            # Draw pot info
            self._draw_pot_info()
            
            # Draw street info
            self._draw_street_info()


class VisualPokerTableGUI:
    """GUI wrapper for the visual poker table."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Visual Poker Table")
        self.root.geometry("800x600")
        self.root.configure(bg=THEME["bg"])
        
        # Create visual table
        self.visual_table = VisualPokerTable(self.root, strategy_data)
        
    def run(self):
        """Run the visual poker table GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    # Create and run visual table
    visual_gui = VisualPokerTableGUI(strategy_data)
    visual_gui.run() 