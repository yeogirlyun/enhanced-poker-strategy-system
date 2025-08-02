#!/usr/bin/env python3
"""
PokerKit Direct GUI

A clean, simple GUI that uses PokerKit APIs directly without any wrapper.
This provides a more reliable and straightforward poker experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
from typing import List, Optional

from pokerkit import (
    NoLimitTexasHoldem, Automation, State, Card
)
from gui_models import StrategyData, THEME, FONTS
from sound_manager import SoundManager

class PokerKitDirectGUI:
    """Direct PokerKit GUI without wrapper complexity."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PokerKit Direct GUI")
        
        # Set window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize components
        self.strategy_data = StrategyData()
        if hasattr(self.strategy_data, 'load_strategy_from_file'):
            try:
                self.strategy_data.load_strategy_from_file("modern_strategy.json")
            except:
                pass
        
        self.sfx = SoundManager()
        self.num_players = 6
        self.player_seats = []
        self.community_card_labels = []
        self.action_controls = {}
        
        # Initialize PokerKit state
        self._initialize_pokerkit_state()
        
        # Setup UI
        self._setup_ui()
        
    def _initialize_pokerkit_state(self):
        """Initialize the PokerKit state."""
        # Create starting stacks
        starting_stacks = [100.0] * self.num_players
        
        # Create blinds
        blinds = [0.5, 1.0]  # Small blind, big blind
        
        # Create PokerKit state
        self.pokerkit_state = NoLimitTexasHoldem.create_state(
            automations=(),  # No automations
            raw_starting_stacks=starting_stacks,
            raw_blinds_or_straddles=blinds,
            raw_antes=(),  # No antes
            min_bet=1.0,  # Minimum bet
            player_count=self.num_players,
            ante_trimming_status=False
        )
        
        # Player names and positions
        self.player_names = [f"Player {i+1}" for i in range(self.num_players)]
        self.positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
    def _setup_ui(self):
        """Setup the UI layout."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start new hand button
        self.start_button = ttk.Button(
            controls_frame, 
            text="Start New Hand", 
            command=self.start_new_hand
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        self.reset_button = ttk.Button(
            controls_frame, 
            text="Reset Game", 
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Game info
        self.game_info_label = ttk.Label(controls_frame, text="Game: Ready")
        self.game_info_label.pack(side=tk.RIGHT, padx=5)
        
        # Game area
        game_frame = ttk.Frame(main_frame)
        game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Poker table
        self.table_canvas = tk.Canvas(
            game_frame, 
            bg=THEME["primary_bg"], 
            highlightthickness=0
        )
        self.table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel - Game info and controls
        right_panel = ttk.Frame(game_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Game messages
        messages_frame = ttk.LabelFrame(right_panel, text="Game Messages")
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.messages_text = tk.Text(
            messages_frame,
            height=15,
            width=40,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=FONTS["small"]
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action controls
        action_frame = ttk.LabelFrame(right_panel, text="Your Action")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._create_action_controls(action_frame)
        
        # Bind canvas resize
        self.table_canvas.bind("<Configure>", self._on_resize)
        
        # Initial draw
        self._draw_table()
        
    def _create_action_controls(self, parent):
        """Create action control buttons."""
        # Action buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=10)
        
        # Action buttons
        actions = [
            ("Fold", "fold", self._fold),
            ("Check", "check", self._check),
            ("Call", "call", self._call),
            ("Bet", "bet", self._bet),
            ("Raise", "raise", self._raise)
        ]
        
        for text, action, command in actions:
            btn = ttk.Button(buttons_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2)
            self.action_controls[action] = btn
        
        # Bet size entry
        bet_frame = ttk.Frame(parent)
        bet_frame.pack(pady=5)
        
        ttk.Label(bet_frame, text="Amount:").pack(side=tk.LEFT)
        self.bet_amount_var = tk.StringVar(value="0")
        self.bet_entry = ttk.Entry(bet_frame, textvariable=self.bet_amount_var, width=10)
        self.bet_entry.pack(side=tk.LEFT, padx=5)
        
        # Initially disable all action buttons
        self._update_action_controls()
        
    def _draw_table(self):
        """Draw the poker table."""
        self.table_canvas.delete("all")
        
        width = self.table_canvas.winfo_width()
        height = self.table_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Draw table
        self.table_canvas.create_oval(
            width*0.05, height*0.1, 
            width*0.95, height*0.9, 
            fill="#013f28", outline=THEME["border"], width=10
        )
        self.table_canvas.create_oval(
            width*0.06, height*0.11, 
            width*0.94, height*0.89, 
            fill="#015939", outline="#222222", width=2
        )
        
        # Draw pot
        pot_text = f"Pot: ${self._get_pot_amount():.2f}"
        self.table_canvas.create_text(
            width/2, height/2 + 50,
            text=pot_text,
            fill="yellow",
            font=("Arial", 16, "bold")
        )
        
        # Draw community cards
        self._draw_community_cards(width, height)
        
        # Draw player seats
        self._draw_player_seats(width, height)
        
    def _draw_community_cards(self, width, height):
        """Draw community cards."""
        center_x, center_y = width/2, height/2
        
        # Community cards area
        card_width = 60
        card_height = 80
        total_width = card_width * 5 + 20  # 5 cards + spacing
        
        start_x = center_x - total_width/2
        
        for i in range(5):
            x = start_x + i * (card_width + 5)
            y = center_y - card_height/2
            
            # Card background
            self.table_canvas.create_rectangle(
                x, y, x + card_width, y + card_height,
                fill="white", outline="black", width=2
            )
            
            # Card text
            card_text = self._get_community_card_text(i)
            self.table_canvas.create_text(
                x + card_width/2, y + card_height/2,
                text=card_text,
                font=("Arial", 12, "bold")
            )
            
    def _draw_player_seats(self, width, height):
        """Draw player seats around the table."""
        center_x, center_y = width/2, height/2
        radius_x, radius_y = width * 0.35, height * 0.25
        
        self.player_seats = []
        
        for i in range(self.num_players):
            angle = (2 * math.pi / self.num_players) * i - (math.pi / 2)
            seat_x = center_x + radius_x * math.cos(angle)
            seat_y = center_y + radius_y * math.sin(angle)
            
            # Player seat
            seat_frame = tk.Frame(
                self.table_canvas,
                bg=THEME["secondary_bg"],
                bd=2, relief="ridge"
            )
            
            # Player info
            name_label = tk.Label(
                seat_frame,
                text=f"{self.player_names[i]}\n{self.positions[i]}",
                bg=THEME["secondary_bg"],
                fg=THEME["text"],
                font=FONTS["player_name"]
            )
            name_label.pack()
            
            # Stack info
            stack_label = tk.Label(
                seat_frame,
                text=f"${self._get_player_stack(i):.2f}",
                bg=THEME["secondary_bg"],
                fg="yellow",
                font=FONTS["stack_bet"]
            )
            stack_label.pack()
            
            # Cards
            cards_label = tk.Label(
                seat_frame,
                text="🂠 🂠",
                bg=THEME["secondary_bg"],
                fg="#CCCCCC",
                font=("Arial", 12, "bold")
            )
            cards_label.pack(pady=5)
            
            # Create window on canvas
            window = self.table_canvas.create_window(
                seat_x, seat_y,
                window=seat_frame,
                anchor="center"
            )
            
            self.player_seats.append({
                "frame": seat_frame,
                "name_label": name_label,
                "stack_label": stack_label,
                "cards_label": cards_label,
                "window": window
            })
            
    def _on_resize(self, event=None):
        """Handle canvas resize."""
        self._draw_table()
        
    def _get_pot_amount(self) -> float:
        """Get current pot amount."""
        try:
            return sum(pot.amount for pot in self.pokerkit_state.pots)
        except:
            return 0.0
            
    def _get_player_stack(self, player_index: int) -> float:
        """Get player stack amount."""
        try:
            return self.pokerkit_state.stacks[player_index]
        except:
            return 100.0
            
    def _get_community_card_text(self, index: int) -> str:
        """Get community card text."""
        try:
            if index < len(self.pokerkit_state.board):
                card = self.pokerkit_state.board[index]
                return str(card)
            else:
                return ""
        except:
            return ""
            
    def _update_action_controls(self):
        """Update action control buttons."""
        # For now, enable all buttons
        for btn in self.action_controls.values():
            btn.config(state="normal")
            
    def _add_message(self, message: str):
        """Add message to the game log."""
        timestamp = time.strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}\n"
        
        self.messages_text.insert(tk.END, full_message)
        self.messages_text.see(tk.END)
        
    def start_new_hand(self):
        """Start a new hand."""
        try:
            self._add_message("Starting new hand...")
            
            # Create new PokerKit state
            self._initialize_pokerkit_state()
            
            # Update display
            self._draw_table()
            self._update_action_controls()
            
            self._add_message("New hand started!")
            self.game_info_label.config(text="Game: Active")
            
        except Exception as e:
            self._add_message(f"Error starting hand: {e}")
            
    def reset_game(self):
        """Reset the game."""
        self._add_message("Resetting game...")
        self._initialize_pokerkit_state()
        self._draw_table()
        self._update_action_controls()
        self.game_info_label.config(text="Game: Ready")
        self._add_message("Game reset complete!")
        
    def _fold(self):
        """Player folds."""
        self._add_message("You fold")
        self.sfx.play("player_fold")
        
    def _check(self):
        """Player checks."""
        self._add_message("You check")
        self.sfx.play("player_check")
        
    def _call(self):
        """Player calls."""
        self._add_message("You call")
        self.sfx.play("player_call")
        
    def _bet(self):
        """Player bets."""
        try:
            amount = float(self.bet_amount_var.get())
            self._add_message(f"You bet ${amount:.2f}")
            self.sfx.play("player_bet")
        except ValueError:
            self._add_message("Invalid bet amount")
            
    def _raise(self):
        """Player raises."""
        try:
            amount = float(self.bet_amount_var.get())
            self._add_message(f"You raise to ${amount:.2f}")
            self.sfx.play("player_raise")
        except ValueError:
            self._add_message("Invalid raise amount")
            
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

def main():
    """Main entry point."""
    app = PokerKitDirectGUI()
    app.run()

if __name__ == "__main__":
    main() 