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
        
        # Table size control
        self.table_scale = 1.0  # Default scale
        self.min_scale = 0.7
        self.max_scale = 2.0
        
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

        # Use scaled drawing from the start to ensure centering
        self._redraw_table_with_scale()
        self._create_human_action_controls()

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
        # Get player position name
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        current_position = positions[self.current_player] if self.current_player < len(positions) else "Unknown"
        
        info_text = f"""🎮 GAME STATE
{'='*30}

👤 Current Player: Player {self.current_player + 1}
📍 Position: {current_position}
💰 Current Bet: ${self.current_bet:.2f}
🎯 Min Bet: ${self.min_bet:.2f}

🃏 Community Cards: {len(self.community_cards)}/5
🏆 Pot Size: ${self.pot:.2f}

📊 Strategy: {self.strategy_data.get_strategy_file_display_name()}

🎯 Your Turn: {'Yes' if self.current_player == 0 else 'No'}
"""
        
        # Only update if info_text widget exists
        if hasattr(self, 'info_text'):
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
        
        # Update game info panel instead of popup
        self._update_info_panel()
        
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

    def increase_table_size(self):
        """Increase the table size."""
        if self.table_scale < self.max_scale:
            self.table_scale += 0.1
            self._redraw_table_with_scale()
    
    def decrease_table_size(self):
        """Decrease the table size."""
        if self.table_scale > self.min_scale:
            self.table_scale -= 0.1
            self._redraw_table_with_scale()
    
    def _redraw_table_with_scale(self):
        """Redraw the table with current scale."""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, use default
            canvas_width, canvas_height = 1000, 700
        
        # Calculate centered table dimensions
        table_width = int(900 * self.table_scale)
        table_height = int(600 * self.table_scale)
        
        # Center the table
        x1 = (canvas_width - table_width) // 2
        y1 = (canvas_height - table_height) // 2
        x2 = x1 + table_width
        y2 = y1 + table_height
        
        # Draw scaled table
        self.canvas.create_oval(x1, y1, x2, y2, fill="#013f28", outline=THEME["border"], width=int(10 * self.table_scale))
        self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="#015939", outline="#222222", width=int(2 * self.table_scale))
        
        # Add table felt texture effect (scaled)
        texture_spacing = int(20 * self.table_scale)
        for i in range(0, table_width - 20, texture_spacing):
            for j in range(0, table_height - 20, texture_spacing):
                if (i + j) % (texture_spacing * 2) == 0:
                    dot_size = int(15 * self.table_scale)
                    self.canvas.create_oval(
                        x1 + 20 + i, y1 + 20 + j, 
                        x1 + 20 + i + dot_size, y1 + 20 + j + dot_size, 
                        fill="#014a2f", outline=""
                    )
        
        # Redraw all UI elements with new scale
        self._setup_player_seats_scaled(self.num_players)
        self._setup_community_card_area_scaled()
        self._setup_pot_display_scaled()
        self._setup_info_panel_scaled()
    
    def _setup_player_seats_scaled(self, num_players):
        """Creates and positions the player seats around the table with scaling."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 1000, 700
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
        radius_x = int(400 * self.table_scale)
        radius_y = int(250 * self.table_scale)
        
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(num_players):
            angle = (2 * math.pi / num_players) * i - (math.pi / 2)
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            self._create_player_seat_scaled(x, y, f"Player {i+1}", positions[i], i)
    
    def _create_player_seat_scaled(self, x, y, name, position, index):
        """Creates the widgets for a single player seat with scaling."""
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=int(2 * self.table_scale), relief="ridge")
        
        # Scale font sizes
        name_font_size = int(FONTS["header"][1] * self.table_scale)
        main_font_size = int(FONTS["main"][1] * self.table_scale)
        small_font_size = int(FONTS["small"][1] * self.table_scale)
        card_font_size = int(24 * self.table_scale)
        
        # Player name and position
        name_label = tk.Label(
            seat_frame, 
            text=f"{name} ({position})", 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            font=(FONTS["header"][0], name_font_size, "bold")
        )
        name_label.pack(pady=(5, 2))
        
        # Stack display
        stack_label = tk.Label(
            seat_frame, 
            text="$1000.00", 
            bg=THEME["secondary_bg"], 
            fg=THEME["accent_secondary"], 
            font=(FONTS["main"][0], main_font_size)
        )
        stack_label.pack()
        
        # Cards display
        cards_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg="#CCCCCC", 
            font=("Arial", card_font_size)
        )
        cards_label.pack(pady=5)
        
        # Action display
        action_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg="yellow", 
            font=(FONTS["small"][0], small_font_size)
        )
        action_label.pack(pady=(2, 5))
        
        # Bet amount display
        bet_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg=THEME["accent_primary"], 
            font=(FONTS["small"][0], small_font_size)
        )
        bet_label.pack(pady=(0, 5))
        
        self.canvas.create_window(x, y, window=seat_frame)
        
        # Update existing seat or add new one
        if index < len(self.player_seats):
            self.player_seats[index] = {
                "frame": seat_frame, 
                "name": name_label, 
                "stack": stack_label, 
                "cards": cards_label, 
                "action": action_label, 
                "bet": bet_label, 
                "index": index
            }
        else:
            self.player_seats.append({
                "frame": seat_frame, 
                "name": name_label, 
                "stack": stack_label, 
                "cards": cards_label, 
                "action": action_label, 
                "bet": bet_label, 
                "index": index
            })
    
    def _setup_community_card_area_scaled(self):
        """Creates labels for the community cards with scaling."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 1000, 700
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
        
        # Clear existing community card labels
        for label in self.community_card_labels:
            label.destroy()
        self.community_card_labels = []
        
        # Create scaled community card area
        card_width = int(60 * self.table_scale)
        card_height = int(90 * self.table_scale)
        card_spacing = int(70 * self.table_scale)
        
        for i in range(5):
            x = center_x - (card_spacing * 2) + (i * card_spacing)
            y = center_y
            card_label = tk.Label(
                self.canvas, 
                text="", 
                bg="#015939", 
                fg="white", 
                font=("Arial", int(28 * self.table_scale), "bold"), 
                bd=int(2 * self.table_scale), 
                relief="groove"
            )
            self.canvas.create_window(x, y, window=card_label, width=card_width, height=card_height)
            self.community_card_labels.append(card_label)
    
    def _setup_pot_display_scaled(self):
        """Creates the text display for the pot with scaling."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 1000, 700
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
        
        # Remove existing pot label if it exists
        if hasattr(self, 'pot_label'):
            self.pot_label.destroy()
        
        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            bg="#013f28", 
            fg="yellow", 
            font=(FONTS["title"][0], int(FONTS["title"][1] * self.table_scale))
        )
        self.canvas.create_window(center_x, center_y + int(130 * self.table_scale), window=self.pot_label)
    
    def _setup_info_panel_scaled(self):
        """Creates the game information panel with scaling."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 1000, 700
        
        # Remove existing info panel if it exists
        if hasattr(self, 'info_panel'):
            self.info_panel.destroy()
        
        # Create scaled info panel with larger dimensions
        panel_width = int(250 * self.table_scale)
        panel_height = int(200 * self.table_scale)
        
        self.info_panel = tk.Frame(
            self.canvas, 
            bg=THEME["secondary_bg"], 
            bd=int(2 * self.table_scale), 
            relief="ridge"
        )
        
        # Scale title font
        title_font_size = int(FONTS["header"][1] * self.table_scale)
        title_label = tk.Label(
            self.info_panel, 
            text="Game Information", 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            font=(FONTS["header"][0], title_font_size, "bold")
        )
        title_label.pack(pady=int(5 * self.table_scale))
        
        # Scale text widget with larger dimensions
        text_height = int(12 * self.table_scale)
        text_width = int(30 * self.table_scale)
        text_font_size = int(12 * self.table_scale)
        
        self.info_text = tk.Text(
            self.info_panel,
            height=text_height,
            width=text_width,
            font=("Consolas", text_font_size),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.info_text.pack(padx=int(5 * self.table_scale), pady=int(5 * self.table_scale))
        
        # Position info panel in top-left with scaled positioning
        panel_x = int(50 * self.table_scale)
        panel_y = int(50 * self.table_scale)
        self.canvas.create_window(
            panel_x, 
            panel_y, 
            window=self.info_panel, 
            width=panel_width, 
            height=panel_height
        )
        
        # Update the info panel with current game state
        self._update_info_panel()

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