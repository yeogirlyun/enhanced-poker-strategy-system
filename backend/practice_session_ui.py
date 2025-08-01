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
import threading
import time
from typing import Optional

from gui_models import THEME, FONTS
from tooltips import ToolTip
from sound_manager import SoundManager
from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType, PokerState


class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that integrates the poker state machine.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.strategy_data = strategy_data
        
        # --- NEW: Initialize the State Machine ---
        self.state_machine = ImprovedPokerStateMachine(num_players=6, strategy_data=self.strategy_data)
        # Pass root window for delayed bot actions
        self.state_machine.root_tk = self.winfo_toplevel()
        # Set up callbacks for state machine events
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_state_change = self.update_display
        # Connect hand log callback
        self.state_machine.on_log_entry = self._log_hand_action
        # --- END NEW ---
        
        # Initialize game state (keep for backward compatibility)
        self.num_players = 6
        self.current_player = 0
        self.pot = 0.0
        self.community_cards = []
        self.player_stacks = [1000.0] * self.num_players
        self.player_cards = [[] for _ in range(self.num_players)]
        self.current_bet = 0.0
        self.min_bet = 20.0  # Big blind
        self.player_acted = [False] * self.num_players  # Track if each player has acted
        
        # Table size control - calculate initial scale for 50% of game pane
        self.min_scale = 0.3
        self.max_scale = 2.0
        # Initial scale will be calculated based on canvas size to take 50% of available space
        self.table_scale = 0.8  # Start smaller for better card visibility
        
        # UI components
        self.player_seats = []
        self.community_card_labels = []
        self.human_action_controls = {}
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        print(f"🔊 Sound manager initialized: {self.sound_manager.sound_enabled}")
        
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main UI components with a proper two-column grid layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)  # Canvas takes 3/4 of the space
        self.grid_columnconfigure(1, weight=1)  # Info panel takes 1/4 of the space

        # Main canvas for the poker table
        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Right-side panel for messages
        right_panel_frame = ttk.Frame(self)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        info_frame = ttk.LabelFrame(right_panel_frame, text="Game Messages", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, state=tk.DISABLED, bg=THEME["secondary_bg"], fg=THEME["text"])
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Human Action Controls (placed below the main canvas)
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self._create_human_action_controls(controls_frame)

        # Bind the resize event
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Add initial message
        self.add_game_message("Welcome to Poker Practice Session!\nClick 'Start New Hand' to begin.")
        
        # Initial draw only - don't initialize state machine automatically
        self.after(100, self._on_resize, None)
        
        # Force initial table sizing
        self.after(200, self._calculate_initial_scale_and_redraw)

    def _on_resize(self, event):
        """Redraws the entire table and its elements when the window is resized."""
        self.canvas.delete("all")  # Clear the canvas
        self._draw_table()
        self._setup_player_seats_scaled(self.num_players)
        self._setup_community_card_area_scaled()
        self._setup_pot_display_scaled()

    def _calculate_initial_scale_and_redraw(self):
        """Calculate initial scale based on canvas size and redraw the table."""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 0 and canvas_height > 0:
            # Calculate scale to fit table in 50% of available space
            # Base table size is 900x600
            # Use the smaller dimension to ensure table fits in both directions
            scale_x = (canvas_width * 0.5) / 900
            scale_y = (canvas_height * 0.5) / 600
            # Use the smaller scale to ensure table fits comfortably
            self.table_scale = min(min(scale_x, scale_y), self.max_scale)
            self.table_scale = max(self.table_scale, self.min_scale)
            # Ensure minimum visibility
            if self.table_scale < 0.6:
                self.table_scale = 0.6
        else:
            self.table_scale = 0.8
        
        self._redraw_table_with_scale()
        self.update_display()

    def _draw_table(self):
        """Draws the main poker table shape based on canvas size."""
        # --- NEW: Get canvas dimensions dynamically ---
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        # --- END NEW ---

        # Create a professional-looking poker table
        self.canvas.create_oval(width*0.05, height*0.05, width*0.95, height*0.9, fill="#013f28", outline=THEME["border"], width=10)
        self.canvas.create_oval(width*0.06, height*0.06, width*0.94, height*0.89, fill="#015939", outline="#222222", width=2)
        
        # --- RE-IMPLEMENTED: Add table felt texture effect ---
        for i in range(0, int(width * 0.88), 20):
            for j in range(0, int(height * 0.78), 20):
                if (i + j) % 40 == 0:
                    self.canvas.create_oval(width*0.07 + i, height*0.07 + j, width*0.085 + i, height*0.085 + j, fill="#014a2f", outline="")

    def _setup_player_seats(self, num_players):
        """Creates and positions the player seats around the table dynamically."""
        # --- NEW: Get canvas dimensions dynamically ---
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        radius_x, radius_y = width * 0.4, height * 0.35
        # --- END NEW ---
        
        self.player_seats = []  # Clear old seat references
        
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(num_players):
            angle = (2 * math.pi / num_players) * i - (math.pi / 2)
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            self._create_player_seat(x, y, f"Player {i+1}", positions[i], i)

    def _create_player_seat(self, x, y, name, position, index):
        """Create a player seat with dynamic positioning."""
        # Seat frame
        seat_width = 120
        seat_height = 80
        seat_x = x - seat_width // 2
        seat_y = y - seat_height // 2
        
        # Create seat frame
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], relief="raised", bd=2)
        self.canvas.create_window(seat_x, seat_y, window=seat_frame, anchor="nw", width=seat_width, height=seat_height)
        
        # Player name
        name_label = tk.Label(seat_frame, text=f"{name}\n({position})", bg=THEME["secondary_bg"], fg=THEME["text"], font=FONTS["small"])
        name_label.pack(pady=2)
        
        # Stack display
        stack_label = tk.Label(seat_frame, text="$1000.00", bg=THEME["secondary_bg"], fg="green", font=FONTS["small"])
        stack_label.pack()
        
        # Cards display - use larger font for better visibility
        cards_label = tk.Label(seat_frame, text="🂠 🂠", bg=THEME["secondary_bg"], fg=THEME["text"], 
                              font=("Arial", 14, "bold"))
        cards_label.pack()
        
        # Store seat info
        self.player_seats.append({
            "frame": seat_frame,
            "name": name_label,
            "stack": stack_label,
            "cards": cards_label,
            "index": index
        })

    def _setup_community_card_area(self):
        """Creates labels for the community cards at the center of the canvas."""
        # --- NEW: Get canvas dimensions dynamically ---
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        # --- END NEW ---

        # Community cards frame
        community_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"])
        self.canvas.create_window(center_x, center_y, window=community_frame)
        
        # Create 5 card slots
        self.community_card_labels = []
        for i in range(5):
            card_label = tk.Label(community_frame, text="", width=3, height=2, 
                                bg=THEME["secondary_bg"], fg=THEME["text"], 
                                relief="raised", bd=1, font=FONTS["small"])
            card_label.pack(side=tk.LEFT, padx=2)
            self.community_card_labels.append(card_label)

    def _setup_pot_display(self):
        """Creates the text display for the pot below the community cards."""
        # --- NEW: Get canvas dimensions dynamically ---
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        # --- END NEW ---

        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            bg="#013f28", 
            fg="yellow", 
            font=FONTS["title"]
        )
        self.canvas.create_window(center_x, center_y + 130, window=self.pot_label)  # Position below cards

    def _setup_player_seats_scaled(self, num_players):
        """Setup player seats around the table with scaling."""
        table_center_x = self.canvas.winfo_width() // 2
        table_center_y = self.canvas.winfo_height() // 2
        table_radius = int(300 * self.table_scale)
        
        # Position players around the table
        positions = [
            (0, -1),      # Top (UTG)
            (0.5, -0.87), # Top-right (MP)
            (0.87, -0.5), # Right (CO)
            (1, 0),       # Bottom-right (BTN)
            (0.87, 0.5),  # Bottom (SB)
            (0.5, 0.87),  # Bottom-left (BB)
        ]
        
        names = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]
        position_names = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(num_players):
            x_offset, y_offset = positions[i]
            x = table_center_x + int(x_offset * table_radius)
            y = table_center_y + int(y_offset * table_radius)
            
            self._create_player_seat_scaled(x, y, names[i], position_names[i], i)

    def _create_player_seat_scaled(self, x, y, name, position, index):
        """Create a player seat with scaling."""
        # Seat frame
        seat_width = int(120 * self.table_scale)
        seat_height = int(80 * self.table_scale)
        seat_x = x - seat_width // 2
        seat_y = y - seat_height // 2
        
        frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=3, relief="raised")
        self.canvas.create_window(seat_x, seat_y, window=frame, anchor="nw", 
                                width=seat_width, height=seat_height)
        
        # Player name
        name_font_size = min(10, int(10 * self.table_scale))
        name_label = tk.Label(frame, text=f"{name}\n({position})", 
                            font=(FONTS["main"], name_font_size), 
                            bg=THEME["secondary_bg"], fg=THEME["text"])
        name_label.pack(pady=2)
        
        # Stack
        main_font_size = min(8, int(8 * self.table_scale))
        stack_label = tk.Label(frame, text=f"${self.player_stacks[index]:.2f}", 
                             font=(FONTS["main"], main_font_size), 
                             bg=THEME["secondary_bg"], fg=THEME["text"])
        stack_label.pack()
        
        # Cards - use larger font for better visibility
        card_font_size = max(12, int(14 * self.table_scale))
        cards_label = tk.Label(frame, text="🂠 🂠", 
                             font=("Arial", card_font_size, "bold"), 
                             bg=THEME["secondary_bg"], fg=THEME["text"])
        cards_label.pack()
        
        # Action
        action_font_size = min(8, int(8 * self.table_scale))
        action_label = tk.Label(frame, text="", 
                              font=(FONTS["main"], action_font_size), 
                              bg=THEME["secondary_bg"], fg=THEME["accent_primary"])
        action_label.pack()
        
        self.player_seats.append({
            'frame': frame,
            'name': name_label,
            'stack': stack_label,
            'cards': cards_label,
            'action': action_label
        })

    def _setup_community_card_area_scaled(self):
        """Setup community card area with scaling."""
        table_center_x = self.canvas.winfo_width() // 2
        table_center_y = self.canvas.winfo_height() // 2
        
        # Community card area
        card_width = int(70 * self.table_scale)
        card_height = int(100 * self.table_scale)
        card_spacing = int(80 * self.table_scale)
        
        start_x = table_center_x - (card_spacing * 2) // 2
        
        self.community_card_labels = []
        for i in range(5):
            card_x = start_x + i * card_spacing
            card_y = table_center_y - card_height // 2
            
            # Card background
            card_frame = tk.Frame(self.canvas, bg="white", bd=3, relief="raised")
            self.canvas.create_window(card_x, card_y, window=card_frame, 
                                    width=card_width, height=card_height)
            
            # Card label - use larger font for better visibility
            card_font_size = max(16, int(20 * self.table_scale))
            card_label = tk.Label(card_frame, text="", 
                                font=("Arial", card_font_size, "bold"), 
                                bg="white", fg="black")
            card_label.pack(expand=True, fill="both")
            
            self.community_card_labels.append(card_label)

    def _setup_pot_display_scaled(self):
        """Setup pot display with scaling."""
        table_center_x = self.canvas.winfo_width() // 2
        table_center_y = self.canvas.winfo_height() // 2
        
        # Pot label
        pot_font_size = min(12, int(12 * self.table_scale))
        self.pot_label = tk.Label(self.canvas, text="Pot: $0.00", 
                                font=(FONTS["main"], pot_font_size, "bold"), 
                                bg=THEME["primary_bg"], fg=THEME["accent_primary"])
        self.canvas.create_window(table_center_x, table_center_y + 150, 
                                window=self.pot_label)

    def _setup_info_panel_scaled(self):
        """Setup information panel with scaling."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Info panel
        panel_width = int(350 * self.table_scale)
        panel_height = int(300 * self.table_scale)
        panel_x = canvas_width - int(370 * self.table_scale)
        panel_y = 20
        
        info_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=2, relief="raised")
        self.canvas.create_window(panel_x, panel_y, window=info_frame, 
                                width=panel_width, height=panel_height, anchor="nw")
        
        # Title
        title_font_size = min(12, int(12 * self.table_scale))
        title_label = tk.Label(info_frame, text="Game Information", 
                             font=(FONTS["main"], title_font_size, "bold"), 
                             bg=THEME["secondary_bg"], fg=THEME["text"])
        title_label.pack(pady=5)
        
        # Info text
        text_height = 18
        text_width = 40
        text_font_size = min(10, int(10 * self.table_scale))
        self.info_text = tk.Text(info_frame, height=text_height, width=text_width,
                               font=(FONTS["main"], text_font_size),
                               bg=THEME["secondary_bg"], fg=THEME["text"],
                               state=tk.DISABLED, wrap=tk.WORD)
        self.info_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        ToolTip(info_frame, "Current game information and status")

    def add_game_message(self, message):
        """Add a message to the game message area."""
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.insert(tk.END, f"{message}\n")
            self.info_text.see(tk.END)
            self.info_text.config(state=tk.DISABLED)

    def _create_human_action_controls(self, parent_frame):
        """Creates a modern, dynamic action bar for the human player."""
        parent_frame.grid_columnconfigure(0, weight=1)
        action_bar_frame = ttk.Frame(parent_frame)
        action_bar_frame.grid(row=0, column=0, pady=5)

        # --- Action Buttons ---
        self.human_action_controls['fold'] = ttk.Button(
            action_bar_frame, 
            text="Fold", 
            style="Danger.TButton", 
            command=lambda: self._submit_human_action("fold")
        )
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['fold'], "Fold your hand and exit the current round")

        self.human_action_controls['check'] = ttk.Button(
            action_bar_frame, 
            text="Check", 
            command=lambda: self._submit_human_action("check")
        )
        self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['check'], "Check (pass) if no bet to call")
        
        self.human_action_controls['call'] = ttk.Button(
            action_bar_frame, 
            text="Call", 
            command=lambda: self._submit_human_action("call")
        )
        self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['call'], "Call the current bet")

        # --- Bet Sizing Slider ---
        sizing_frame = ttk.Frame(action_bar_frame)
        sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.bet_size_var = tk.DoubleVar()
        self.bet_slider = ttk.Scale(
            sizing_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.bet_size_var, 
            length=200
        )
        self.bet_slider.pack(fill=tk.X)
        self.bet_slider.bind("<B1-Motion>", self._update_bet_size_label)
        
        self.bet_size_label = ttk.Label(sizing_frame, text="$0.00", font=FONTS["main"])
        self.bet_size_label.pack()

        # --- Bet/Raise Button ---
        self.human_action_controls['bet_raise'] = ttk.Button(
            action_bar_frame, 
            text="Bet", 
            style="Primary.TButton", 
            command=self._submit_bet_raise
        )
        self.human_action_controls['bet_raise'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['bet_raise'], "Make a bet or raise")

        # --- Start Hand Button ---
        self.human_action_controls['start_hand'] = ttk.Button(
            action_bar_frame, 
            text="Start Hand", 
            command=self.start_new_hand,
            style="Success.TButton"
        )
        ToolTip(self.human_action_controls['start_hand'], "Start a new poker hand")

        # Initially hide all controls except start hand
        for widget in self.human_action_controls.values():
            widget.pack_forget()
        self.human_action_controls['start_hand'].pack(side=tk.LEFT, padx=5)

    def _update_bet_size_label(self, event=None):
        """Updates the label for the bet sizing slider."""
        self.bet_size_label.config(text=f"${self.bet_size_var.get():.2f}")

    def _submit_bet_raise(self):
        """Submits a bet or raise action based on context."""
        game_info = self.state_machine.get_game_info()
        if game_info and game_info.get('current_bet', 0) > 0:
            self._submit_human_action("raise")
        else:
            self._submit_human_action("bet")

    def update_display(self, new_state=None):
        """Updates the entire UI based on the current game state from the state machine."""
        game_info = self.state_machine.get_game_info()
        if not game_info or not game_info.get('players'):
            print(f"❌ No game info available from state machine")
            # Initialize with default values
            self._update_display_with_defaults()
            return

        print(f"🎮 Updating display with game info: {game_info}")
        
        # Debug: Check human player cards
        human_players = [p for p in game_info['players'] if p['is_human']]
        if human_players:
            human = human_players[0]
            print(f"🎯 Human player found: {human['name']}, cards: {human['cards']}, is_human: {human['is_human']}")
        else:
            print(f"❌ No human player found in game info")

        # --- NEW: Enhanced Pot and Bet Display ---
        pot_text = f"Pot: ${game_info['pot']:.2f}"
        if game_info.get('current_bet', 0) > 0:
            pot_text += f"  |  Current Bet: ${game_info['current_bet']:.2f}"
        self.pot_label.config(text=pot_text)
        # --- END NEW ---
        
        for i, card in enumerate(game_info['board']):
            if i < len(self.community_card_labels):
                self.community_card_labels[i].config(text=self._format_card(card))

        # Update player info
        for i, seat in enumerate(self.player_seats):
            if i < len(game_info['players']):
                player_info = game_info['players'][i]
                seat['stack'].config(text=f"${player_info['stack']:.2f}")
                
                # Show cards for all players at showdown, otherwise only for the human
                if (self.state_machine.get_current_state() == PokerState.SHOWDOWN or 
                    player_info['is_human']):
                    # Format cards properly and ensure they display
                    if player_info['cards'] and player_info['cards'] != ['**', '**']:
                        cards_text = " ".join(self._format_card(c) for c in player_info['cards'])
                        seat['cards'].config(text=cards_text)
                        # Force update and debug
                        seat['cards'].update()
                        print(f"🎴 Showing cards for {player_info['name']}: {cards_text}")
                        print(f"🔍 Card label text after update: {seat['cards'].cget('text')}")
                    else:
                        seat['cards'].config(text="🂠 🂠")
                        print(f"🂠 No cards for {player_info['name']}")
                else:
                    seat['cards'].config(text="🂠 🂠" if player_info['is_active'] else "")
                    print(f"🂠 Hiding cards for {player_info['name']}")

                # Highlight the current player to act
                if i == game_info['action_player'] and player_info['is_active']:
                    seat['frame'].config(bg=THEME["accent_primary"])
                    seat['name'].config(fg="white")
                else:
                    seat['frame'].config(bg=THEME["secondary_bg"])
                    seat['name'].config(fg=THEME["text"])
        
        self._update_info_panel()

    def _update_display_with_defaults(self):
        """Update display with default values when state machine is not ready."""
        print(f"🎮 Using default display values")
        
        # Set default pot
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text="Pot: $0.00")
        
        # Set default community cards
        for label in self.community_card_labels:
            label.config(text="")
        
        # Set default player info - show ready state
        for i, seat in enumerate(self.player_seats):
            if i < len(self.player_stacks):
                seat['stack'].config(text=f"${self.player_stacks[i]:.2f}")
                # Show ready state - no cards until hand starts
                seat['cards'].config(text="Ready" if i == 0 else "")
                seat['frame'].config(bg=THEME["secondary_bg"])
                seat['name'].config(fg=THEME["text"])
        
        self._update_info_panel()

    def handle_hand_complete(self):
        """Handles the completion of a hand by displaying the winner on the UI."""
        self.sound_manager.play("winner_announce")
        winner_info = self.state_machine.determine_winner()

        if winner_info:
            winner_names = ", ".join(p.name for p in winner_info)
            self.pot_label.config(text=f"Winner: {winner_names}!", fg=THEME["accent_secondary"])

            # Highlight winning players
            for seat in self.player_seats:
                if seat["name"].cget("text").split(" ")[0] in winner_names:
                    seat["frame"].config(bg=THEME["accent_secondary"])

        self.sound_manager.play("pot_rake")
        
        # Show start hand button again
        for widget in self.human_action_controls.values():
            widget.pack_forget()
        self.human_action_controls['start_hand'].pack(side=tk.LEFT, padx=5)
        
        # Ask to start a new hand after a delay
        self.after(3000, self._prompt_new_hand)

    def _prompt_new_hand(self):
        """Asks the user to start a new hand."""
        if messagebox.askyesno("New Hand", "Start a new hand?"):
            self.start_new_hand()

    def _update_info_panel(self):
        """Updates the information panel with current game state."""
        # Get game info from state machine
        game_info = self.state_machine.get_game_info()
        
        if game_info and game_info.get('players'):
            # Use state machine data
            action_player = game_info.get('action_player', 0)
            current_player = game_info['players'][action_player] if action_player < len(game_info['players']) else None
            
            if current_player:
                current_position = current_player.get('position', 'Unknown')
                current_bet = game_info.get('current_bet', 0.0)
                pot_size = game_info.get('pot', 0.0)
                board = game_info.get('board', [])
                is_human_turn = current_player.get('is_human', False)
            else:
                current_position = "Unknown"
                current_bet = 0.0
                pot_size = 0.0
                board = []
                is_human_turn = False
        else:
            # Use default values
            current_position = "Unknown"
            current_bet = 0.0
            pot_size = 0.0
            board = []
            is_human_turn = False
        
        info_text = f"""🎮 GAME STATE
{'='*30}

👤 Current Player: Player {action_player + 1 if 'action_player' in locals() else 'Unknown'}
📍 Position: {current_position}
💰 Current Bet: ${current_bet:.2f}
🎯 Min Bet: ${self.min_bet:.2f}

🃏 Community Cards: {len(board)}/5
🏆 Pot Size: ${pot_size:.2f}

📊 Strategy: {self.strategy_data.get_strategy_file_display_name()}

🎯 Your Turn: {'Yes' if is_human_turn else 'No'}
"""
        
        # Only update if info_text widget exists
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)

    def _initialize_state_machine(self):
        """Initialize the state machine without starting the game flow."""
        print(f"🎮 Initializing state machine")
        # Don't start the hand automatically - let user click "Start New Hand"
        self.update_display()
        print(f"✅ State machine initialized")

    def start_new_hand(self):
        """Starts a new hand using the state machine."""
        self.sound_manager.play("card_deal")
        self.add_game_message("🎮 Starting new hand...")
        self.state_machine.start_hand()
        # The state machine will now automatically call prompt_human_action via its callback
    
    def _continue_hand_start(self):
        """Continue hand start after state machine is initialized."""
        print(f"🎮 Continuing hand start")
        self.update_display()
        
        # Check if we have a valid game state
        game_info = self.state_machine.get_game_info()
        if game_info and game_info.get('players'):
            print(f"✅ Game state initialized successfully")
            self.state_machine.handle_current_player_action()
        else:
            print(f"❌ Game state not properly initialized, retrying...")
            self.after(200, self._continue_hand_start)

    def prompt_human_action(self, player):
        """Shows and configures the action controls for the human player."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return

        # Hide all action buttons initially
        self.human_action_controls['fold'].pack_forget()
        self.human_action_controls['check'].pack_forget()
        self.human_action_controls['call'].pack_forget()

        # Show Fold button
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)

        # Show Check or Call button
        call_amount = game_info['current_bet'] - player.current_bet
        if call_amount > 0:
            self.human_action_controls['call'].config(text=f"Call ${call_amount:.2f}")
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        else:
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)

        # Configure the bet/raise slider and button
        min_bet = self.state_machine.game_state.min_raise
        max_bet = player.stack + player.current_bet

        self.bet_slider.config(from_=min_bet, to=max_bet)
        self.bet_size_var.set(min_bet)
        self._update_bet_size_label()

        if game_info['current_bet'] > 0:
            self.human_action_controls['bet_raise'].config(text="Raise To")
        else:
            self.human_action_controls['bet_raise'].config(text="Bet")

    def _submit_human_action(self, action_str):
        """Submits the human's chosen action to the state machine."""
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            return

        action_map = { "fold": ActionType.FOLD, "check": ActionType.CHECK, "call": ActionType.CALL, "bet": ActionType.BET, "raise": ActionType.RAISE }
        action = action_map.get(action_str)
        
        # --- NEW: Get amount from the slider for bets/raises ---
        amount = 0
        if action in [ActionType.BET, ActionType.RAISE]:
            amount = self.bet_size_var.get()
        # --- END NEW ---

        sound_to_play = {"fold": "card_fold", "check": "player_check", "call": "player_call", "bet": "player_bet", "raise": "player_raise"}.get(action_str)
        if sound_to_play:
            self.sfx.play(sound_to_play)

        self.state_machine.execute_action(player, action, amount)
        self.update_display()
        
        # Hide controls and let the state machine continue
        for widget in self.human_action_controls.values():
            if isinstance(widget, ttk.Button): # Check if it's a button before packing
                widget.pack_forget()
        self.state_machine.handle_current_player_action()

    def run_game_loop(self):
        """Handles the game flow for all non-human players."""
        while True:
            current_player = self.state_machine.get_action_player()
            if not current_player or self.state_machine.get_current_state() == PokerState.END_HAND:
                break  # End the loop if the hand is over or no one can act

            if not current_player.is_human:
                time.sleep(1.0)  # Artificial delay for bot "thinking"
                self.state_machine.execute_bot_action(current_player)
                self.winfo_toplevel().after(0, self.update_display)  # Schedule UI update on the main thread
            else:
                # It's the human's turn again, break the loop and wait for input
                break

    def show_action_animation(self, player_index, action_text, color="yellow"):
        """Displays a temporary action message over a player's seat."""
        if player_index < len(self.player_seats):
            player_seat = self.player_seats[player_index]
            x, y = player_seat["frame"].winfo_x(), player_seat["frame"].winfo_y()

            action_label = tk.Label(self.canvas, text=action_text, bg=color, fg="black", 
                                  font=(FONTS["main"], 12, "bold"))
            self.canvas.create_window(x, y - 40, window=action_label, anchor="s")

            # Fade out the label after 1.5 seconds
            self.after(1500, lambda: action_label.destroy())

    def _log_hand_action(self, log_entry):
        """Log hand actions to the main GUI hand log."""
        # Find the main GUI window and update its hand log
        root = self.winfo_toplevel()
        if hasattr(root, 'update_hand_log'):
            root.update_hand_log(log_entry)

    def increase_table_size(self):
        """Increase table size."""
        self.table_scale = min(self.table_scale + 0.1, self.max_scale)
        self._redraw_table_with_scale()

    def decrease_table_size(self):
        """Decrease table size."""
        self.table_scale = max(self.table_scale - 0.1, self.min_scale)
        self._redraw_table_with_scale()

    def _redraw_table_with_scale(self):
        """Redraw the table with current scale."""
        self.canvas.delete("all")  # Clear the canvas
        self._draw_table()
        self._setup_player_seats_scaled(self.num_players)
        self._setup_community_card_area_scaled()
        self._setup_pot_display_scaled()
        self.update_display()

    def _on_canvas_resize(self, event):
        """Handle canvas resize events."""
        self._redraw_table_with_scale()

    def _format_card(self, card_str: str) -> str:
        """Format card string for display."""
        if not card_str or card_str == "**":
            return "🂠"
        
        # Convert card format (e.g., "As" -> "A♠")
        rank = card_str[0]
        suit = card_str[1]
        suit_symbols = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
        return f"{rank}{suit_symbols.get(suit, suit)}"

    def run(self):
        """Start the practice session."""
        print("🎮 Practice session started")
        self.update_display() 