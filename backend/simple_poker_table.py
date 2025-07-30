#!/usr/bin/env python3
"""
Simple Professional Poker Table with Perfect Centering

A clean, working poker table with perfect centering and clear action buttons.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

from enhanced_poker_engine import EnhancedPokerEngine, Player, GameState, Action, Position
from gui_models import StrategyData


class SimplePokerTable:
    """Simple poker table with perfect centering and clear action buttons."""
    
    def __init__(self, parent_frame, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.engine = EnhancedPokerEngine(strategy_data)
        self.current_game_state = None
        
        # Perfect centering dimensions
        self.canvas_width = 900
        self.canvas_height = 600
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2
        
        # Professional table ratios
        self.table_width = int(self.canvas_width * 0.75)
        self.table_height = int(self.canvas_height * 0.65)
        self.player_radius = min(self.table_width, self.table_height) * 0.4
        
        # Card dimensions
        self.card_width = 45
        self.card_height = 65
        
        # Create canvas
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#0B6623",  # Professional green felt
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create controls
        self._create_controls(parent_frame)
        
        # Draw table
        self._draw_table()
        
    def _create_controls(self, parent_frame):
        """Create clear, functional controls."""
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Player count
        ttk.Label(left_frame, text="Players:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.player_count_var = tk.StringVar(value="6")
        player_combo = ttk.Combobox(
            left_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly",
            width=5,
        )
        player_combo.pack(side=tk.LEFT, padx=5)
        
        # Start button
        start_button = ttk.Button(
            left_frame,
            text="🎯 Start New Hand",
            command=self._start_hand,
        )
        start_button.pack(side=tk.LEFT, padx=10)
        
        # Right side - Action buttons
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.X)
        
        # Turn indicator
        self.turn_label = tk.Label(
            right_frame,
            text="YOUR TURN",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#FF6B6B",
            relief="raised",
            bd=2
        )
        self.turn_label.pack(side=tk.LEFT, padx=5)
        
        # Action buttons with clear labels
        self.action_var = tk.StringVar(value="check")
        actions = [
            ("FOLD", "fold", "#FF4444"),
            ("CHECK", "check", "#4488FF"),
            ("CALL", "call", "#44AA44"),
            ("BET", "bet", "#FFAA44"),
            ("RAISE", "raise", "#AA44FF"),
        ]
        
        for text, value, color in actions:
            btn = tk.Button(
                right_frame,
                text=text,
                command=lambda v=value: self._set_action(v),
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                relief="raised",
                bd=3,
                width=10,
                height=2,
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # Bet size
        ttk.Label(right_frame, text="Bet:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.bet_size_var = tk.StringVar(value="0")
        bet_entry = ttk.Entry(right_frame, textvariable=self.bet_size_var, width=8)
        bet_entry.pack(side=tk.LEFT, padx=2)
        
        # Submit button
        submit_button = tk.Button(
            right_frame,
            text="SUBMIT ACTION",
            command=self._submit_action,
            bg="#22AA22",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=3,
            width=12,
            height=2,
        )
        submit_button.pack(side=tk.LEFT, padx=5)
        
    def _set_action(self, action):
        """Set the selected action."""
        self.action_var.set(action)
        print(f"Action selected: {action}")
        
    def _start_hand(self):
        """Start a new hand."""
        try:
            num_players = int(self.player_count_var.get())
            result = self.engine.play_hand(num_players)
            self.current_game_state = self.engine.current_game_state
            
            # Redraw table
            self._redraw_table()
            
            messagebox.showinfo(
                "Hand Started",
                f"New hand started with {num_players} players!\n"
                f"Your position: {self.current_game_state.players[0].position.value}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start hand: {str(e)}")
            
    def _submit_action(self):
        """Submit action."""
        if not self.current_game_state:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return
            
        try:
            action_str = self.action_var.get()
            bet_size = float(self.bet_size_var.get())
            
            action_map = {
                "fold": Action.FOLD,
                "check": Action.CHECK,
                "call": Action.CALL,
                "bet": Action.BET,
                "raise": Action.RAISE,
            }
            
            action = action_map.get(action_str, Action.CHECK)
            
            # Execute action
            human_player = next(p for p in self.current_game_state.players if p.is_human)
            self.engine.execute_action(human_player, action, bet_size, self.current_game_state)
            
            # Redraw table
            self._redraw_table()
            
            # Show feedback
            self._show_feedback(action, bet_size)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit action: {str(e)}")
            
    def _show_feedback(self, action: Action, bet_size: float):
        """Show feedback for the action."""
        if not self.engine.deviation_logs:
            return
            
        latest_deviation = self.engine.deviation_logs[-1]
        feedback = self.engine.get_feedback_message(latest_deviation)
        
        feedback_window = tk.Toplevel()
        feedback_window.title("Action Feedback")
        feedback_window.geometry("500x250")
        feedback_window.configure(bg="#2C3E50")
        
        feedback_text = tk.Text(
            feedback_window,
            font=("Arial", 12),
            wrap="word",
            padx=15,
            pady=15,
            bg="#34495E",
            fg="white",
            relief="flat",
        )
        feedback_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        feedback_text.insert(tk.END, f"🎯 Your Action: {action.value}\n")
        if bet_size > 0:
            feedback_text.insert(tk.END, f"💰 Bet Size: ${bet_size:.2f}\n\n")
        feedback_text.insert(tk.END, f"📊 Strategy Feedback:\n{feedback}")
        
        close_button = tk.Button(
            feedback_window,
            text="OK",
            command=feedback_window.destroy,
            bg="#27AE60",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=2,
            width=10,
        )
        close_button.pack(pady=10)
        
    def _draw_table(self):
        """Draw the poker table with perfect centering."""
        # Calculate table position for perfect centering
        table_x = self.center_x - self.table_width // 2
        table_y = self.center_y - self.table_height // 2
        
        # Draw table outline
        self.canvas.create_oval(
            table_x, table_y,
            table_x + self.table_width, table_y + self.table_height,
            fill="#0B6623",  # Professional green felt
            outline="#8B4513",  # Brown border
            width=4,
        )
        
        # Draw pot area - PERFECTLY CENTERED
        pot_radius = 35
        self.canvas.create_oval(
            self.center_x - pot_radius, self.center_y - pot_radius,
            self.center_x + pot_radius, self.center_y + pot_radius,
            fill="#FFD700",  # Gold pot
            outline="#B8860B",  # Dark gold border
            width=3,
        )
        
        # Draw dealer button
        dealer_radius = 18
        self.canvas.create_oval(
            self.center_x - dealer_radius, self.center_y - dealer_radius,
            self.center_x + dealer_radius, self.center_y + dealer_radius,
            fill="white", outline="black", width=2,
        )
        self.canvas.create_text(
            self.center_x, self.center_y,
            text="D", font=("Arial", 14, "bold"), fill="black",
        )
        
    def _get_player_position(self, player_index: int, total_players: int):
        """Calculate perfect player position."""
        angle = (player_index * 2 * math.pi / total_players) - math.pi / 2
        x = self.center_x + int(self.player_radius * math.cos(angle))
        y = self.center_y + int(self.player_radius * math.sin(angle))
        return x, y
        
    def _draw_player(self, player: Player, position, is_current_player=False):
        """Draw a player."""
        x, y = position
        
        # Player circle
        if player.is_human:
            color = "#FF6B6B"  # Red for human
        elif not player.is_active:
            color = "#95A5A6"  # Gray for folded
        else:
            color = "#4ECDC4"  # Teal for AI
        
        # Highlight current player
        if is_current_player:
            self.canvas.create_oval(
                x - 35, y - 35, x + 35, y + 35,
                fill="", outline="#FFD700", width=3,
            )
        
        player_radius = 30
        self.canvas.create_oval(
            x - player_radius, y - player_radius,
            x + player_radius, y + player_radius,
            fill=color, outline="black", width=2,
        )
        
        # Player name
        name = "You" if player.is_human else f"P{player.name.split()[-1]}"
        self.canvas.create_text(
            x, y - 8, text=name,
            font=("Arial", 11, "bold"), fill="white",
        )
        
        # Position
        self.canvas.create_text(
            x, y + 8, text=player.position.value,
            font=("Arial", 9, "bold"), fill="white",
        )
        
        # Stack
        self.canvas.create_text(
            x, y + 35, text=f"${player.stack:.0f}",
            font=("Arial", 9, "bold"), fill="white",
        )
        
        # Hole cards
        if player.cards and (player.is_human or not player.is_active):
            self._draw_hole_cards(player, position)
            
    def _draw_hole_cards(self, player: Player, position):
        """Draw hole cards."""
        x, y = position
        card_y = y + 60
        
        for i, card in enumerate(player.cards):
            card_x = x - 35 + (i * 40)
            
            # Card background
            card_color = "#FFD700" if player.is_human else "#FFFFFF"
            self.canvas.create_rectangle(
                card_x, card_y,
                card_x + self.card_width, card_y + self.card_height,
                fill=card_color, outline="black", width=2,
            )
            
            # Card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"
            
            self.canvas.create_text(
                card_x + self.card_width // 2, card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 14, "bold"), fill=color,
            )
            
    def _draw_community_cards(self):
        """Draw community cards."""
        if not self.current_game_state or not self.current_game_state.board:
            return
            
        card_spacing = 60
        start_x = self.center_x - (len(self.current_game_state.board) * card_spacing // 2)
        
        for i, card in enumerate(self.current_game_state.board):
            card_x = start_x + (i * card_spacing)
            card_y = self.center_y - 50  # Above pot
            
            # Card background
            self.canvas.create_rectangle(
                card_x, card_y,
                card_x + self.card_width, card_y + self.card_height,
                fill="#FFFFFF", outline="black", width=2,
            )
            
            # Card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"
            
            self.canvas.create_text(
                card_x + self.card_width // 2, card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 14, "bold"), fill=color,
            )
            
    def _draw_pot_info(self):
        """Draw pot information."""
        if not self.current_game_state:
            return
            
        # Pot amount - PERFECTLY CENTERED
        self.canvas.create_text(
            self.center_x, self.center_y,
            text=f"${self.current_game_state.pot:.0f}",
            font=("Arial", 16, "bold"), fill="black",
        )
        
        # Current bet
        if self.current_game_state.current_bet > 0:
            self.canvas.create_text(
                self.center_x, self.center_y + 25,
                text=f"Bet: ${self.current_game_state.current_bet:.0f}",
                font=("Arial", 12, "bold"), fill="white",
            )
            
    def _draw_street_info(self):
        """Draw street information."""
        if not self.current_game_state:
            return
            
        street_text = self.current_game_state.street.upper()
        self.canvas.create_text(
            self.center_x, 40,
            text=street_text,
            font=("Arial", 18, "bold"), fill="white",
        )
        
    def _redraw_table(self):
        """Redraw the entire table."""
        self.canvas.delete("all")
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


class SimplePokerTableGUI:
    """Simple poker table GUI wrapper."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple Professional Poker Table")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2C3E50")
        
        # Create poker table
        self.poker_table = SimplePokerTable(self.root, strategy_data)
        
    def run(self):
        """Run the poker table GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    # Create and run simple table
    simple_gui = SimplePokerTableGUI(strategy_data)
    simple_gui.run() 