#!/usr/bin/env python3
"""
Practice Session UI Module for Enhanced Poker Strategy GUI

Provides a graphical, interactive practice session interface with a visual poker table.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created graphical poker table interface
- Integrated with poker state machine
- Added professional styling and tooltips
- Enhanced user interaction and feedback
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import Optional

from gui_models import THEME, FONTS
from tooltips import ToolTip


class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that integrates the poker state machine.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.strategy_data = strategy_data
        
        # Initialize game state
        self.num_players = 6
        self.current_player = 0
        self.pot = 0.0
        self.community_cards = []
        self.player_stacks = [1000.0] * self.num_players
        self.player_cards = [[] for _ in range(self.num_players)]
        self.current_bet = 0.0
        self.min_bet = 20.0  # Big blind
        
        # UI components
        self.player_seats = []
        self.community_card_labels = []
        self.human_action_controls = {}
        
        self._setup_ui()
        self.update_display()

    def _setup_ui(self):
        """Sets up the main UI components for the practice session."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main canvas for the poker table
        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self._draw_table()
        self._setup_player_seats(self.num_players)
        self._setup_community_card_area()
        self._setup_pot_display()
        self._create_human_action_controls()
        self._setup_info_panel()

    def _draw_table(self):
        """Draws the main poker table shape."""
        # Create a professional-looking poker table
        self.canvas.create_oval(50, 50, 950, 650, fill="#013f28", outline=THEME["border"], width=10)
        self.canvas.create_oval(60, 60, 940, 640, fill="#015939", outline="#222222", width=2)
        
        # Add table felt texture effect
        for i in range(0, 880, 20):
            for j in range(0, 580, 20):
                if (i + j) % 40 == 0:
                    self.canvas.create_oval(70 + i, 70 + j, 85 + i, 85 + j, fill="#014a2f", outline="")

    def _setup_player_seats(self, num_players):
        """Creates and positions the player seats around the table."""
        center_x, center_y = 500, 350
        radius_x, radius_y = 400, 250
        
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(num_players):
            angle = (2 * math.pi / num_players) * i - (math.pi / 2)
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            self._create_player_seat(x, y, f"Player {i+1}", positions[i], i)

    def _create_player_seat(self, x, y, name, position, index):
        """Creates the widgets for a single player seat."""
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=2, relief="ridge")
        
        # Player name and position
        name_label = tk.Label(
            seat_frame, 
            text=f"{name} ({position})", 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            font=FONTS["header"]
        )
        name_label.pack(pady=(5, 2))
        
        # Stack display
        stack_label = tk.Label(
            seat_frame, 
            text="$1000.00", 
            bg=THEME["secondary_bg"], 
            fg=THEME["accent_secondary"], 
            font=FONTS["main"]
        )
        stack_label.pack()
        
        # Cards display
        cards_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg="#CCCCCC", 
            font=("Arial", 24)
        )
        cards_label.pack(pady=5)
        
        # Action display
        action_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg="yellow", 
            font=FONTS["small"]
        )
        action_label.pack(pady=(2, 5))
        
        # Bet amount display
        bet_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg=THEME["accent_primary"], 
            font=FONTS["small"]
        )
        bet_label.pack(pady=(0, 5))
        
        self.canvas.create_window(x, y, window=seat_frame)
        self.player_seats.append({
            "frame": seat_frame, 
            "name": name_label, 
            "stack": stack_label, 
            "cards": cards_label, 
            "action": action_label,
            "bet": bet_label,
            "index": index,
            "position": position
        })

    def _setup_community_card_area(self):
        """Creates labels for the community cards."""
        # Create a frame for community cards
        community_frame = tk.Frame(self.canvas, bg="#015939", bd=2, relief="groove")
        self.canvas.create_window(500, 350, window=community_frame)
        
        # Add community cards label
        community_label = tk.Label(
            community_frame, 
            text="Community Cards", 
            bg="#015939", 
            fg="white", 
            font=FONTS["header"]
        )
        community_label.pack(pady=(5, 10))
        
        # Create card labels
        cards_frame = tk.Frame(community_frame, bg="#015939")
        cards_frame.pack()
        
        for i in range(5):
            card_label = tk.Label(
                cards_frame, 
                text="", 
                bg="#013f28", 
                fg="white", 
                font=("Arial", 28, "bold"), 
                bd=2, 
                relief="groove",
                width=3,
                height=2
            )
            card_label.pack(side=tk.LEFT, padx=5)
            self.community_card_labels.append(card_label)
            
    def _setup_pot_display(self):
        """Creates the text display for the pot."""
        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            bg="#013f28", 
            fg="yellow", 
            font=FONTS["title"]
        )
        self.canvas.create_window(500, 480, window=self.pot_label)

    def _setup_info_panel(self):
        """Creates an information panel for game details."""
        info_frame = ttk.LabelFrame(self, text="Game Information", padding=10)
        info_frame.place(relx=0.02, rely=0.02, anchor="nw")
        
        self.info_text = tk.Text(
            info_frame,
            height=8,
            width=30,
            font=FONTS["small"],
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED
        )
        self.info_text.pack()
        
        ToolTip(info_frame, "Current game information and status")

    def _create_human_action_controls(self):
        """Creates the buttons and entry for human player actions."""
        controls_frame = ttk.Frame(self, style="TFrame")
        controls_frame.place(relx=0.5, rely=0.95, anchor="center")

        # Action buttons
        self.human_action_controls['fold'] = ttk.Button(
            controls_frame, 
            text="Fold", 
            command=lambda: self._submit_human_action("fold"),
            style="Danger.TButton"
        )
        ToolTip(self.human_action_controls['fold'], "Fold your hand and exit the current round")
        
        self.human_action_controls['check'] = ttk.Button(
            controls_frame, 
            text="Check", 
            command=lambda: self._submit_human_action("check")
        )
        ToolTip(self.human_action_controls['check'], "Check (pass) if no bet to call")
        
        self.human_action_controls['call'] = ttk.Button(
            controls_frame, 
            text="Call", 
            command=lambda: self._submit_human_action("call")
        )
        ToolTip(self.human_action_controls['call'], "Call the current bet")
        
        self.human_action_controls['bet'] = ttk.Button(
            controls_frame, 
            text="Bet", 
            command=lambda: self._submit_human_action("bet"),
            style="Primary.TButton"
        )
        ToolTip(self.human_action_controls['bet'], "Make a bet")
        
        self.human_action_controls['raise'] = ttk.Button(
            controls_frame, 
            text="Raise", 
            command=lambda: self._submit_human_action("raise"),
            style="Primary.TButton"
        )
        ToolTip(self.human_action_controls['raise'], "Raise the current bet")
        
        # Amount entry
        self.amount_var = tk.StringVar(value="20")
        self.human_action_controls['amount_entry'] = ttk.Entry(
            controls_frame, 
            textvariable=self.amount_var, 
            width=10
        )
        ToolTip(self.human_action_controls['amount_entry'], "Enter bet/raise amount")

        # Initially hide all controls
        for widget in self.human_action_controls.values():
            widget.pack_forget()

    def update_display(self):
        """Updates the entire UI based on the current game state."""
        # Update pot display
        self.pot_label.config(text=f"Pot: ${self.pot:.2f}")
        
        # Update community cards
        for i, card in enumerate(self.community_cards):
            if i < len(self.community_card_labels):
                self.community_card_labels[i].config(text=self._format_card(card))
        
        # Update player seats
        for i, seat in enumerate(self.player_seats):
            # Update stack
            seat['stack'].config(text=f"${self.player_stacks[i]:.2f}")
            
            # Update cards (show human cards, hide others)
            if i == 0:  # Human player
                if self.player_cards[i]:
                    cards_text = " ".join(self._format_card(c) for c in self.player_cards[i])
                    seat['cards'].config(text=cards_text)
                else:
                    seat['cards'].config(text="")
            else:  # AI players
                if self.player_cards[i]:
                    seat['cards'].config(text="🂠 🂠")  # Card back emoji
                else:
                    seat['cards'].config(text="")
            
            # Highlight current player
            if i == self.current_player:
                seat['frame'].config(bg=THEME["accent_primary"])
                seat['name'].config(fg="white")
            else:
                seat['frame'].config(bg=THEME["secondary_bg"])
                seat['name'].config(fg=THEME["text"])
        
        # Update info panel
        self._update_info_panel()

    def _update_info_panel(self):
        """Updates the information panel with current game state."""
        info_text = f"""GAME STATE
{'='*20}

Current Player: Player {self.current_player + 1}
Position: {self.player_seats[self.current_player]['position']}
Current Bet: ${self.current_bet:.2f}
Min Bet: ${self.min_bet:.2f}

Community Cards: {len(self.community_cards)}/5
Pot Size: ${self.pot:.2f}

Strategy: {self.strategy_data.get_strategy_file_display_name()}
"""
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state=tk.DISABLED)

    def start_new_hand(self):
        """Starts a new hand."""
        # Reset game state
        self.pot = 0.0
        self.community_cards = []
        self.current_bet = 0.0
        self.min_bet = 20.0
        
        # Reset player actions
        for seat in self.player_seats:
            seat['action'].config(text="")
        
        # Deal cards (simplified)
        import random
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        suits = ['s', 'h', 'd', 'c']
        
        # Deal 2 cards to each player
        all_cards = []
        for rank in ranks:
            for suit in suits:
                all_cards.append(f"{rank}{suit}")
        
        random.shuffle(all_cards)
        
        # Deal cards to players
        for i in range(self.num_players):
            self.player_cards[i] = [all_cards.pop(), all_cards.pop()]
        
        # Set blinds
        self.player_stacks[4] -= 10  # Small blind
        self.player_stacks[5] -= 20  # Big blind
        self.pot = 30.0
        
        # Update blinds display
        self.player_seats[4]['action'].config(text="SB $10")
        self.player_seats[5]['action'].config(text="BB $20")
        
        # Start with first player after big blind
        self.current_player = 0
        
        self.update_display()
        
        # Show message that hand has started
        messagebox.showinfo("New Hand", "🎯 New poker hand started!\n\nYou are Player 1 (UTG).\nYour cards are displayed on your seat.\n\nClick 'OK' to begin your turn.")
        
        self.prompt_human_action()

    def prompt_human_action(self):
        """Shows the action controls for the human player."""
        if self.current_player != 0:  # Not human's turn
            return
        
        # Hide all controls first
        for widget in self.human_action_controls.values():
            widget.pack_forget()

        # Show relevant controls based on current situation
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        
        if self.current_bet == 0:
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        else:
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        
        self.human_action_controls['bet'].pack(side=tk.LEFT, padx=5)
        self.human_action_controls['raise'].pack(side=tk.LEFT, padx=5)
        self.human_action_controls['amount_entry'].pack(side=tk.LEFT, padx=5)

    def _submit_human_action(self, action):
        """Submits the human's chosen action."""
        amount = 0
        if action in ["bet", "raise"]:
            try:
                amount = float(self.amount_var.get())
                if amount < self.min_bet:
                    messagebox.showerror("Invalid Amount", f"Minimum bet is ${self.min_bet:.2f}")
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number for the amount.")
                return
        
        # Execute action
        if action == "fold":
            self.player_seats[0]['action'].config(text="Folded")
        elif action == "check":
            self.player_seats[0]['action'].config(text="Checked")
        elif action == "call":
            call_amount = self.current_bet
            self.player_stacks[0] -= call_amount
            self.pot += call_amount
            self.player_seats[0]['action'].config(text=f"Called ${call_amount:.2f}")
        elif action in ["bet", "raise"]:
            self.player_stacks[0] -= amount
            self.pot += amount
            self.current_bet = amount
            self.player_seats[0]['action'].config(text=f"{action.title()} ${amount:.2f}")
        
        # Hide controls after action
        for widget in self.human_action_controls.values():
            widget.pack_forget()
        
        # Move to next player (simplified AI)
        self._ai_turn()

    def _ai_turn(self):
        """Simulates AI player turns."""
        self.current_player = (self.current_player + 1) % self.num_players
        
        if self.current_player == 0:  # Back to human
            self.prompt_human_action()
        else:
            # Simple AI logic
            import random
            actions = ["fold", "call", "bet"]
            action = random.choice(actions)
            
            if action == "bet":
                bet_amount = random.randint(20, 100)
                self.player_stacks[self.current_player] -= bet_amount
                self.pot += bet_amount
                self.current_bet = bet_amount
                self.player_seats[self.current_player]['action'].config(text=f"Bet ${bet_amount:.2f}")
            elif action == "call":
                call_amount = self.current_bet
                self.player_stacks[self.current_player] -= call_amount
                self.pot += call_amount
                self.player_seats[self.current_player]['action'].config(text=f"Called ${call_amount:.2f}")
            else:  # fold
                self.player_seats[self.current_player]['action'].config(text="Folded")
            
            # Continue to next player after a short delay
            self.after(1000, self._ai_turn)
        
        self.update_display()

    def _format_card(self, card_str: str) -> str:
        """Formats a card string for display (e.g., 'As' -> 'A♠')."""
        if not card_str or len(card_str) < 2: 
            return ""
        rank, suit = card_str[0], card_str[1]
        suit_map = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
        return f"{rank}{suit_map.get(suit, '')}"

    def run(self):
        """Starts the UI main loop."""
        self.start_new_hand()
        self.mainloop() 