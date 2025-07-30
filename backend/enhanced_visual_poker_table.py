#!/usr/bin/env python3
"""
Enhanced Visual Poker Table with Perfect Centering

A professional poker table with perfect centering, improved layout,
and state-of-the-art visual design based on professional poker applications.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from enhanced_poker_engine import (
    EnhancedPokerEngine,
    Player,
    GameState,
    Action,
    Position,
)
from gui_models import StrategyData, THEME


class ProfessionalPokerTable:
    """Professional poker table with perfect centering and layout."""

    def __init__(self, parent_frame, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.engine = EnhancedPokerEngine(strategy_data)
        self.current_game_state = None
        
        # MUCH LARGER table - 80% of pane
        self.canvas_width = 1200  # Increased from 900
        self.canvas_height = 800   # Increased from 600
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2
        
        # Professional table ratios - 80% of canvas
        self.table_width = int(self.canvas_width * 0.80)   # 80% of canvas width
        self.table_height = int(self.canvas_height * 0.80)  # 80% of canvas height
        self.player_radius = min(self.table_width, self.table_height) * 0.45  # Larger player radius
        
        # Card dimensions - larger for better visibility
        self.card_width = 55  # Increased from 45
        self.card_height = 75  # Increased from 65
        
        # Game state tracking
        self.current_hand_phase = "preflop"  # preflop, flop, turn, river
        self.current_action_player = 0  # Index of player whose turn it is
        self.dealer_position = 0  # Dealer position
        self.small_blind_position = 1  # Small blind position
        self.big_blind_position = 2  # Big blind position
        self.hand_started = False
        self.community_cards_dealt = 0  # 0=preflop, 3=flop, 4=turn, 5=river
        
        # Create canvas
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#0B6623",  # Professional green felt
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create controls
        self._create_professional_controls(parent_frame)
        
        # Draw table
        self._draw_professional_table()

    def _create_professional_controls(self, parent_frame):
        """Create professional game controls."""
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Left side - Game controls
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Player count with professional styling
        ttk.Label(left_frame, text="Players:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        self.player_count_var = tk.StringVar(value="6")
        player_combo = ttk.Combobox(
            left_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly",
            width=5,
            font=("Arial", 10),
        )
        player_combo.pack(side=tk.LEFT, padx=5)

        # Professional start button
        start_button = ttk.Button(
            left_frame,
            text="🎯 Start New Hand",
            command=self._start_professional_hand,
            style="Accent.TButton",
        )
        start_button.pack(side=tk.LEFT, padx=10)

        # Right side - Action controls
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.X)

        # Professional action buttons with clear labels
        self.action_var = tk.StringVar(value="check")
        actions = [
            ("FOLD", "fold", "#FF4444"),  # Red
            ("CHECK", "check", "#4488FF"),  # Blue
            ("CALL", "call", "#44AA44"),  # Green
            ("BET", "bet", "#FFAA44"),  # Orange
            ("RAISE", "raise", "#AA44FF"),  # Purple
        ]

        # Add turn indicator
        turn_label = tk.Label(
            right_frame,
            text="YOUR TURN",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#FF6B6B",
        )
        turn_label.pack(side=tk.LEFT, padx=5)

        for text, value, color in actions:
            btn = tk.Button(
                right_frame,
                text=text,
                command=lambda v=value: self._set_action(v),
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                relief="raised",
                bd=2,
                width=8,
                height=1,
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Bet size entry
        ttk.Label(right_frame, text="Bet:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        self.bet_size_var = tk.StringVar(value="0")
        bet_entry = ttk.Entry(
            right_frame, textvariable=self.bet_size_var, width=8, font=("Arial", 10)
        )
        bet_entry.pack(side=tk.LEFT, padx=2)

        # Professional submit button
        submit_button = tk.Button(
            right_frame,
            text="Submit Action",
            command=self._submit_professional_action,
            bg="#22AA22",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
        )
        submit_button.pack(side=tk.LEFT, padx=5)

    def _set_action(self, action):
        """Set the selected action."""
        self.action_var.set(action)

    def _draw_professional_table(self):
        """Draw a professional poker table with perfect centering."""
        # Calculate table position for perfect centering
        table_x = self.center_x - self.table_width // 2
        table_y = self.center_y - self.table_height // 2

        # Draw professional table outline
        self.canvas.create_oval(
            table_x,
            table_y,
            table_x + self.table_width,
            table_y + self.table_height,
            fill="#0B6623",  # Professional green felt
            outline="#8B4513",  # Brown border
            width=4,
        )

        # Draw professional felt pattern
        for i in range(0, self.table_width, 25):
            for j in range(0, self.table_height, 25):
                pattern_x = table_x + i
                pattern_y = table_y + j
                if (pattern_x - self.center_x) ** 2 + (
                    pattern_y - self.center_y
                ) ** 2 < (self.player_radius - 30) ** 2:
                    self.canvas.create_oval(
                        pattern_x,
                        pattern_y,
                        pattern_x + 3,
                        pattern_y + 3,
                        fill="#228B22",
                        outline="",
                    )

        # Draw professional pot area - PERFECTLY CENTERED
        pot_radius = 35
        self.canvas.create_oval(
            self.center_x - pot_radius,
            self.center_y - pot_radius,  # FIXED: Use center_y for perfect centering
            self.center_x + pot_radius,
            self.center_y + pot_radius,  # FIXED: Use center_y for perfect centering
            fill="#FFD700",  # Gold pot
            outline="#B8860B",  # Dark gold border
            width=3,
        )

        # Draw professional dealer button
        dealer_radius = 18
        self.canvas.create_oval(
            self.center_x - dealer_radius,
            self.center_y - dealer_radius,
            self.center_x + dealer_radius,
            self.center_y + dealer_radius,
            fill="white",
            outline="black",
            width=2,
        )
        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="D",
            font=("Arial", 14, "bold"),
            fill="black",
        )

    def _get_player_position(
        self, player_index: int, total_players: int
    ) -> Tuple[int, int]:
        """Calculate perfect player position around the table."""
        # Start from bottom (south) and go clockwise
        angle = (player_index * 2 * math.pi / total_players) - math.pi / 2
        x = self.center_x + int(self.player_radius * math.cos(angle))
        y = self.center_y + int(self.player_radius * math.sin(angle))
        return x, y

    def _draw_professional_player(
        self, player: Player, position: Tuple[int, int], is_current_player: bool = False
    ):
        """Draw a professional player with perfect positioning."""
        x, y = position

        # Professional player circle
        if player.is_human:
            color = "#FF6B6B"  # Red for human player
        elif not player.is_active:
            color = "#95A5A6"  # Gray for folded players
        else:
            color = "#4ECDC4"  # Teal for AI players

        player_radius = 30

        # Highlight current player's turn
        if is_current_player:
            # Draw highlight ring
            self.canvas.create_oval(
                x - player_radius - 5,
                y - player_radius - 5,
                x + player_radius + 5,
                y + player_radius + 5,
                fill="",
                outline="#FFD700",  # Gold highlight
                width=3,
            )
        self.canvas.create_oval(
            x - player_radius,
            y - player_radius,
            x + player_radius,
            y + player_radius,
            fill=color,
            outline="black",
            width=2,
        )

        # Professional player name
        name = "You" if player.is_human else f"P{player.name.split()[-1]}"
        self.canvas.create_text(
            x, y - 8, text=name, font=("Arial", 11, "bold"), fill="white"
        )

        # Professional position indicator
        self.canvas.create_text(
            x,
            y + 8,
            text=player.position.value,
            font=("Arial", 9, "bold"),
            fill="white",
        )

        # Professional stack size
        self.canvas.create_text(
            x,
            y + 35,
            text=f"${player.stack:.0f}",
            font=("Arial", 9, "bold"),
            fill="white",
        )

        # Draw professional hole cards - only show human cards or folded players
        if player.cards and (player.is_human or not player.is_active):
            self._draw_professional_hole_cards(player, position)

    def _draw_professional_hole_cards(self, player: Player, position: Tuple[int, int]):
        """Draw professional hole cards with perfect spacing."""
        x, y = position

        # Position cards below player with professional spacing
        card_y = y + 60

        for i, card in enumerate(player.cards):
            card_x = x - 35 + (i * 40)  # Professional card spacing

            # Professional card background
            card_color = "#FFD700" if player.is_human else "#FFFFFF"
            self.canvas.create_rectangle(
                card_x,
                card_y,
                card_x + self.card_width,
                card_y + self.card_height,
                fill=card_color,
                outline="black",
                width=2,
            )

            # Professional card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"

            self.canvas.create_text(
                card_x + self.card_width // 2,
                card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 14, "bold"),
                fill=color,
            )

    def _draw_professional_community_cards(self):
        """Draw professional community cards with perfect centering."""
        if not self.current_game_state:
            return
            
        # Only show community cards as they're dealt
        cards_to_show = self.current_game_state.board[:self.community_cards_dealt]
        if not cards_to_show:
            return
            
        # Professional card spacing and positioning
        card_spacing = 80  # Increased spacing for larger cards
        start_x = self.center_x - (len(cards_to_show) * card_spacing // 2)
        
        for i, card in enumerate(cards_to_show):
            card_x = start_x + (i * card_spacing)
            card_y = self.center_y - 80  # Positioned above pot
            
            # Professional card background
            self.canvas.create_rectangle(
                card_x,
                card_y,
                card_x + self.card_width,
                card_y + self.card_height,
                fill="#FFFFFF",  # White background
                outline="black",
                width=2,
            )
            
            # Professional card text
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"
            
            self.canvas.create_text(
                card_x + self.card_width // 2,
                card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", 16, "bold"),  # Larger font
                fill=color,
            )

    def _draw_professional_pot_info(self):
        """Draw professional pot information."""
        if not self.current_game_state:
            return

            # Professional pot amount - PERFECTLY CENTERED
        self.canvas.create_text(
            self.center_x,
            self.center_y,  # FIXED: Use center_y for perfect centering
            text=f"${self.current_game_state.pot:.0f}",
            font=("Arial", 16, "bold"),
            fill="black",
        )

        # Professional current bet
        if self.current_game_state.current_bet > 0:
            self.canvas.create_text(
                self.center_x,
                self.center_y + 25,  # FIXED: Position below pot
                text=f"Bet: ${self.current_game_state.current_bet:.0f}",
                font=("Arial", 12, "bold"),
                fill="white",
            )

    def _draw_professional_street_info(self):
        """Draw professional street information."""
        if not self.current_game_state:
            return

        # Professional street name
        street_text = self.current_game_state.street.upper()
        self.canvas.create_text(
            self.center_x,
            40,
            text=street_text,
            font=("Arial", 18, "bold"),
            fill="white",
        )

    def _start_professional_hand(self):
        """Start a new professional hand with proper dealer sequence."""
        try:
            num_players = int(self.player_count_var.get())
            
            # Initialize hand state
            self.hand_started = True
            self.current_hand_phase = "preflop"
            self.community_cards_dealt = 0
            self.current_action_player = 0  # UTG starts
            
            # Create players with proper positions
            players = []
            positions = [Position.UTG, Position.MP, Position.CO, Position.BTN, Position.SB, Position.BB]
            
            for i in range(num_players):
                is_human = (i == 0)  # First player is human
                position = positions[i % len(positions)]
                player = Player(
                    name=f"Player {i+1}",
                    stack=100.0,
                    position=position,
                    is_human=is_human,
                    is_active=True,
                    cards=[]  # Cards will be dealt by dealer
                )
                players.append(player)
            
            # Dealer deals hole cards (but don't show AI cards yet)
            import random
            deck = self._create_deck()
            random.shuffle(deck)
            
            # Deal hole cards
            for player in players:
                player.cards = [deck.pop(), deck.pop()]
            
            # Create game state
            self.current_game_state = GameState(
                players=players,
                board=[],  # No community cards yet
                pot=0.0,
                current_bet=0.0,
                street="preflop"
            )
            
            # Post blinds
            if num_players >= 2:
                self.current_game_state.players[self.small_blind_position].stack -= 0.5
                self.current_game_state.players[self.big_blind_position].stack -= 1.0
                self.current_game_state.pot = 1.5
                self.current_game_state.current_bet = 1.0
            
            # Redraw table
            self._redraw_professional_table()
            
            # Update turn indicator
            self._update_turn_indicator()
            
            messagebox.showinfo(
                "Hand Started",
                f"New hand started with {num_players} players!\n"
                f"Dealer: {self.current_game_state.players[self.dealer_position].name}\n"
                f"Your position: {self.current_game_state.players[0].position.value}\n"
                f"Action starts with: {self.current_game_state.players[self.current_action_player].name}",
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start hand: {str(e)}")
            
    def _create_deck(self):
        """Create a standard 52-card deck."""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['h', 'd', 'c', 's']
        deck = []
        for rank in ranks:
            for suit in suits:
                deck.append(f"{rank}{suit}")
        return deck
        
    def _update_turn_indicator(self):
        """Update the turn indicator to show whose turn it is."""
        if not self.current_game_state:
            self.turn_label.config(text="NO ACTIVE HAND", bg="#95A5A6")
            return
            
        current_player = self.current_game_state.players[self.current_action_player]
        if current_player.is_human:
            self.turn_label.config(text="YOUR TURN", bg="#FF6B6B")
        else:
            self.turn_label.config(text=f"{current_player.name}'s TURN", bg="#4ECDC4")

    def _submit_professional_action(self):
        """Submit action with proper turn progression."""
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
                "raise": Action.RAISE,
            }

            action = action_map.get(action_str, Action.CHECK)

            # Execute action for current player
            current_player = self.current_game_state.players[self.current_action_player]
            
            # Apply action
            if action == Action.FOLD:
                current_player.is_active = False
            elif action in [Action.CALL, Action.BET, Action.RAISE]:
                # Update pot and stacks
                call_amount = self.current_game_state.current_bet
                if action == Action.BET:
                    call_amount = bet_size
                elif action == Action.RAISE:
                    call_amount = bet_size
                
                current_player.stack -= call_amount
                self.current_game_state.pot += call_amount
                self.current_game_state.current_bet = call_amount

            # Move to next player
            self._advance_to_next_player()
            
            # Check if round is complete
            if self._is_round_complete():
                self._advance_to_next_street()

            # Redraw table
            self._redraw_professional_table()
            
            # Update turn indicator
            self._update_turn_indicator()

            # Show professional feedback
            self._show_professional_feedback(action, bet_size)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit action: {str(e)}")
            
    def _advance_to_next_player(self):
        """Move to the next active player."""
        num_players = len(self.current_game_state.players)
        self.current_action_player = (self.current_action_player + 1) % num_players
        
        # Skip folded players
        while not self.current_game_state.players[self.current_action_player].is_active:
            self.current_action_player = (self.current_action_player + 1) % num_players
            
    def _is_round_complete(self):
        """Check if the current betting round is complete."""
        active_players = [p for p in self.current_game_state.players if p.is_active]
        if len(active_players) <= 1:
            return True
            
        # Check if all active players have acted and bets are equal
        for player in active_players:
            if player.stack < self.current_game_state.current_bet:
                return False
        return True
        
    def _advance_to_next_street(self):
        """Advance to the next street (flop, turn, river)."""
        if self.current_hand_phase == "preflop":
            self.current_hand_phase = "flop"
            self.community_cards_dealt = 3
            self._deal_community_cards(3)
        elif self.current_hand_phase == "flop":
            self.current_hand_phase = "turn"
            self.community_cards_dealt = 4
            self._deal_community_cards(1)
        elif self.current_hand_phase == "turn":
            self.current_hand_phase = "river"
            self.community_cards_dealt = 5
            self._deal_community_cards(1)
        elif self.current_hand_phase == "river":
            # Hand is complete
            self._show_hand_results()
            return
            
        # Reset betting for new street
        self.current_game_state.current_bet = 0.0
        self.current_action_player = (self.big_blind_position + 1) % len(self.current_game_state.players)
        
    def _deal_community_cards(self, num_cards):
        """Deal community cards."""
        if not hasattr(self, '_deck'):
            self._deck = self._create_deck()
            import random
            random.shuffle(self._deck)
            
        for _ in range(num_cards):
            if self._deck:
                self.current_game_state.board.append(self._deck.pop())
                
    def _show_hand_results(self):
        """Show the results of the hand."""
        messagebox.showinfo(
            "Hand Complete",
            f"Hand completed!\nFinal pot: ${self.current_game_state.pot:.2f}\n"
            f"Winner: {self._determine_winner()}"
        )
        self.hand_started = False
        
    def _determine_winner(self):
        """Determine the winner of the hand."""
        active_players = [p for p in self.current_game_state.players if p.is_active]
        if len(active_players) == 1:
            return active_players[0].name
        else:
            # Simple winner determination (could be enhanced with hand evaluation)
            return "Showdown - Multiple players"

    def _show_professional_feedback(self, action: Action, bet_size: float):
        """Show professional feedback for the submitted action."""
        if not self.engine.deviation_logs:
            return

        latest_deviation = self.engine.deviation_logs[-1]
        feedback = self.engine.get_feedback_message(latest_deviation)

        # Create professional feedback window
        feedback_window = tk.Toplevel()
        feedback_window.title("Professional Action Feedback")
        feedback_window.geometry("500x250")
        feedback_window.configure(bg="#2C3E50")

        # Professional feedback text
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

        # Professional close button
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

    def _redraw_professional_table(self):
        """Redraw the entire table with professional layout."""
        # Clear canvas
        self.canvas.delete("all")

        # Redraw professional table
        self._draw_professional_table()

        if self.current_game_state:
            # Draw professional players
            for i, player in enumerate(self.current_game_state.players):
                position = self._get_player_position(
                    i, len(self.current_game_state.players)
                )
                # Highlight current action player
                is_current = (i == self.current_action_player)
                self._draw_professional_player(player, position, is_current)

            # Draw professional community cards
            self._draw_professional_community_cards()

            # Draw professional pot info
            self._draw_professional_pot_info()

            # Draw professional street info
            self._draw_professional_street_info()


class ProfessionalPokerTableGUI:
    """Professional poker table GUI wrapper."""

    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data

        # Create professional main window
        self.root = tk.Tk()
        self.root.title("Professional Poker Table")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2C3E50")

        # Create professional poker table
        self.professional_table = ProfessionalPokerTable(self.root, strategy_data)

    def run(self):
        """Run the professional poker table GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")

    # Create and run professional table
    professional_gui = ProfessionalPokerTableGUI(strategy_data)
    professional_gui.run()
