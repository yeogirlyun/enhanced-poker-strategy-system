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
from tkinter import ttk
import math

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType, PokerState
from sound_manager import SoundManager
from gui_models import THEME, FONTS
from tooltips import ToolTip

class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that integrates the poker state machine.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.strategy_data = strategy_data
        
        # Initialize State Machine and Sound Manager
        self.state_machine = ImprovedPokerStateMachine(num_players=6, strategy_data=self.strategy_data, root_tk=self.winfo_toplevel())
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_state_change = self.update_display
        self.state_machine.on_log_entry = self.add_game_message  # NEW: Connect detailed logging
        self.sfx = SoundManager()

        # UI components
        self.num_players = 6
        self.player_seats = []  # Store player seat widget dictionaries
        self.community_card_labels = []
        self.human_action_controls = {}
        
        self._setup_ui()
        # Don't automatically start a hand - let user click button

    def _setup_ui(self):
        """Sets up the UI layout with a responsive grid."""
        self.grid_rowconfigure(0, weight=1)
        # --- CHANGE THIS LINE FOR THE FINAL TIME ---
        self.grid_columnconfigure(0, weight=5) # Canvas now takes 5/6 of the space ( ~83%)
        # --- END CHANGE ---
        self.grid_columnconfigure(1, weight=1) # Info panel takes 1/6 of the space ( ~17%)

        # Main canvas for the poker table
        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Right-side panel for messages
        right_panel_frame = ttk.Frame(self)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame = ttk.LabelFrame(right_panel_frame, text="Game Messages", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        self.info_text = tk.Text(
            info_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=FONTS["small"]  # Use the default font from your theme
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Human Action Controls (placed at the bottom)
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        self._create_human_action_controls(controls_frame)

        # Bind the resize event
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """Redraws all canvas elements when the window is resized."""
        self.canvas.delete("all")
        self._draw_table()
        self._draw_player_seats()
        self._draw_community_card_area()
        self._draw_pot_display()
        self.update_display() # Refresh data after redraw

    def _draw_table(self):
        """Draws the main poker table shape with correctly contained texture."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Main table oval
        self.canvas.create_oval(width*0.05, height*0.1, width*0.95, height*0.9, fill="#013f28", outline=THEME["border"], width=10)
        self.canvas.create_oval(width*0.06, height*0.11, width*0.94, height*0.89, fill="#015939", outline="#222222", width=2)
        
        # --- CORRECTED FELT TEXTURE LOGIC ---
        # Adjust the loop bounds to be tighter and inside the table border
        x_start = int(width * 0.1)
        x_end = int(width * 0.9)
        y_start = int(height * 0.15)
        y_end = int(height * 0.85)

        for i in range(x_start, x_end, 20):
            for j in range(y_start, y_end, 20):
                # Check if the point is inside the oval before drawing
                # This prevents the texture from spilling outside the table
                if (((i - width/2)**2 / (width*0.4)**2) + ((j - height/2)**2 / (height*0.35)**2)) < 1:
                    if (i + j) % 40 == 0:
                        self.canvas.create_oval(i, j, i + 15, j + 15, fill="#014a2f", outline="")
        # --- END CORRECTION ---

    def _draw_player_seats(self):
        """Calculates positions and draws player seats and their bet displays."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        radius_x, radius_y = width * 0.42, height * 0.35
        
        # --- NEW: Initialize the list to store widget dictionaries ---
        self.player_seats = [{} for _ in range(self.num_players)]
        # --- END NEW ---

        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        for i in range(self.num_players):
            angle = (2 * math.pi / self.num_players) * i - (math.pi / 2)
            
            # Player Seat Position
            seat_x = center_x + radius_x * math.cos(angle)
            seat_y = center_y + radius_y * math.sin(angle)
            self._create_player_seat_widget(seat_x, seat_y, f"Player {i+1}", positions[i], i)

            # --- NEW: Create a Bet Label in front of the player ---
            bet_radius_x, bet_radius_y = radius_x * 0.7, radius_y * 0.7
            bet_x = center_x + bet_radius_x * math.cos(angle)
            bet_y = center_y + bet_radius_y * math.sin(angle)

            bet_label = tk.Label(self.canvas, text="", bg="#015939", fg="yellow", font=FONTS["header"])
            bet_window = self.canvas.create_window(bet_x, bet_y, window=bet_label, anchor="center", state="hidden")
            
            self.player_seats[i]["bet_label_widget"] = bet_label
            self.player_seats[i]["bet_label_window"] = bet_window
            # --- END NEW ---

    def _create_player_seat_widget(self, x, y, name, position, index):
        """Creates and stores all Tkinter widgets for a single player seat."""
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=2, relief="ridge")
        
        # Player name and position
        name_label = tk.Label(seat_frame, text=f"{name}\n{position}", bg=THEME["secondary_bg"], fg=THEME["text"], font=FONTS["small"])
        name_label.pack()
        
        # --- NEW: Dedicated frame for stack and bet info ---
        info_frame = tk.Frame(seat_frame, bg=THEME["secondary_bg"])
        info_frame.pack(pady=(2, 0))
        
        # Stack amount with better formatting
        stack_label = tk.Label(info_frame, text="$100.00", bg=THEME["secondary_bg"], fg="yellow", font=FONTS["small"])
        stack_label.pack(side=tk.LEFT, padx=5)
        
        # Bet amount (initially empty)
        bet_label = tk.Label(info_frame, text="", bg=THEME["secondary_bg"], fg="orange", font=FONTS["small"])
        bet_label.pack(side=tk.LEFT, padx=5)
        # --- END NEW ---
        
        # --- NEW: Dynamic font size for cards ---
        card_font_size = max(12, int(self.canvas.winfo_height() / 35))
        card_font = ("Arial", card_font_size, "bold")
        # --- END NEW ---

        # Cards
        cards_label = tk.Label(
            seat_frame, 
            text="🂠 🂠", 
            bg=THEME["secondary_bg"], 
            fg="#CCCCCC", 
            font=card_font  # Use the new dynamic font
        )
        cards_label.pack(pady=5)
        
        # --- NEW: Store all widgets in the player_seats list ---
        self.player_seats[index] = {
            "frame": seat_frame,
            "name_label": name_label,
            "stack_label": stack_label,
            "bet_label": bet_label,  # NEW: Add bet label
            "cards_label": cards_label,
        }
        # --- END NEW ---
        
        self.canvas.create_window(x, y, window=seat_frame, anchor="center")

    def _draw_community_card_area(self):
        """Draws the community card area in the center of the table."""
        center_x, center_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        community_frame = tk.Frame(self.canvas, bg="#015939", bd=2, relief="groove")
        
        # Create labels for community cards
        self.community_card_labels = []
        for i in range(5):
            # --- FIX: Larger font for community cards ---
            card_font_size = max(16, int(self.canvas.winfo_height() / 25))
            card_font = ("Arial", card_font_size, "bold")
            card_label = tk.Label(community_frame, text="", bg="#015939", fg="white", font=card_font, width=4)
            card_label.pack(side=tk.LEFT, padx=3)
            self.community_card_labels.append(card_label)
            # --- END FIX ---
        
        self.canvas.create_window(center_x, center_y, window=community_frame)

    def _draw_pot_display(self):
        """Draws the pot display."""
        center_x, center_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        self.pot_label = tk.Label(self.canvas, text="Pot: $0.00", bg="#013f28", fg="yellow", font=FONTS["title"])
        self.canvas.create_window(center_x, center_y + 130, window=self.pot_label)

    def update_display(self, new_state=None):
        """Updates the UI and logs detailed debugging information."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            self._log_message("DEBUG: update_display called but no game_info available.")
            return

        self._log_message("\n--- UI UPDATE ---")
        self._log_message(f"Action Player Index from State Machine: {game_info['action_player']}")
        self._log_message(f"Total Player Seats in UI: {len(self.player_seats)}")
        self._log_message(f"Current State: {self.state_machine.get_current_state()}")
        
        # --- ENHANCED: Community Card Debugging ---
        self._log_message(f"Community Cards: {game_info['board']}")
        self._log_message(f"Pot: ${game_info['pot']:.2f}, Current Bet: ${game_info['current_bet']:.2f}")
        # --- END ENHANCED ---

        # Update pot and community cards
        pot_text = f"Pot: ${game_info['pot']:.2f}"
        if game_info['current_bet'] > 0:
            pot_text += f"  |  Current Bet: ${game_info['current_bet']:.2f}"
        self.pot_label.config(text=pot_text)

        for i, card_label in enumerate(self.community_card_labels):
            card_label.config(text=self._format_card(game_info['board'][i]) if i < len(game_info['board']) else "")

        # Update player info
        for i, player_seat in enumerate(self.player_seats):
            if not player_seat:  # Skip if player seat is empty
                self._log_message(f"DEBUG: ERROR - Player seat at index {i} is empty!")
                continue

            player_info = game_info['players'][i]
            frame = player_seat["frame"]
            name_label = player_seat["name_label"]
            stack_label = player_seat["stack_label"]
            bet_label = player_seat["bet_label"]  # NEW: Get bet label
            cards_label = player_seat["cards_label"]
            
            # Highlight current player
            if i == game_info['action_player'] and player_info['is_active']:
                frame.config(bg=THEME["accent_primary"])
                self._log_message(f"HIGHLIGHTING Player at index {i} ({player_info['name']})")
                self._log_message(f"DEBUG: Frame {i} position: {frame.winfo_x()}, {frame.winfo_y()}")
            else:
                frame.config(bg=THEME["secondary_bg"])

            # Update name and position
            name_label.config(text=f"{player_info['name']} ({player_info['position']})")
            
            # Update stack and bet info
            stack_label.config(text=f"${player_info['stack']:.2f}")
            
            # --- ENHANCED: Update bet amount display with chip emoji ---
            if player_info['current_bet'] > 0:
                bet_label.config(text=f"💰 ${player_info['current_bet']:.2f}")
                self._log_message(f"DEBUG: Updated bet display for {player_info['name']}: ${player_info['current_bet']:.2f}")
            else:
                bet_label.config(text="")
            # --- END ENHANCED ---

            # --- NEW: Update the prominent bet display on the table ---
            bet_label_widget = player_seat.get("bet_label_widget")
            bet_label_window = player_seat.get("bet_label_window")
            if bet_label_widget and bet_label_window:
                current_bet = player_info.get("current_bet", 0.0)
                if current_bet > 0 and player_info['is_active']:
                    bet_label_widget.config(text=f"💰 ${current_bet:.2f}")
                    self.canvas.itemconfig(bet_label_window, state="normal")  # Show the bet
                    self._log_message(f"DEBUG: Showing prominent bet display for {player_info['name']}: ${current_bet:.2f}")
                else:
                    self.canvas.itemconfig(bet_label_window, state="hidden")  # Hide the bet
                    self._log_message(f"DEBUG: Hiding bet display for {player_info['name']} (bet: ${current_bet:.2f}, active: {player_info['is_active']})")
            # --- END NEW ---

            if player_info['is_active']:
                if player_info['is_human'] or self.state_machine.get_current_state() == PokerState.SHOWDOWN:
                    cards_text = " ".join(self._format_card(c) for c in player_info['cards'])
                    cards_label.config(text=cards_text)
                else:
                    cards_label.config(text="🂠 🂠")
            else:
                cards_label.config(text="Folded")

    def add_game_message(self, message):
        """Add a message to the game message area."""
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.insert(tk.END, f"{message}\n")
            self.info_text.see(tk.END)
            self.info_text.config(state=tk.DISABLED)

    def _log_message(self, message: str):
        """Logs a message to the Game Messages panel."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END) # Auto-scroll to the bottom
        self.info_text.config(state=tk.DISABLED)

    def _create_human_action_controls(self, parent_frame):
        """Creates a modern, dynamic action bar for the human player."""
        parent_frame.grid_columnconfigure(0, weight=1)
        self.action_bar_frame = ttk.Frame(parent_frame)  # Store reference
        self.action_bar_frame.grid(row=0, column=0, pady=5)

        # --- Action Buttons ---
        self.human_action_controls['fold'] = ttk.Button(
            self.action_bar_frame, 
            text="Fold", 
            style="Danger.TButton", 
            command=lambda: self._submit_human_action("fold")
        )
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['fold'], "Fold your hand and exit the current round")

        self.human_action_controls['check'] = ttk.Button(
            self.action_bar_frame, 
            text="Check", 
            command=lambda: self._submit_human_action("check")
        )
        self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['check'], "Check (pass) if no bet to call")
        
        self.human_action_controls['call'] = ttk.Button(
            self.action_bar_frame, 
            text="Call", 
            command=lambda: self._submit_human_action("call")
        )
        self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['call'], "Call the current bet")

        # --- Bet Sizing Slider ---
        sizing_frame = ttk.Frame(self.action_bar_frame)
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
            self.action_bar_frame, 
            text="Bet", 
            style="Primary.TButton", 
            command=self._submit_bet_raise
        )
        self.human_action_controls['bet_raise'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['bet_raise'], "Make a bet or raise")

        # --- Start Hand Button ---
        self.human_action_controls['start_hand'] = ttk.Button(
            self.action_bar_frame, 
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

    def prompt_human_action(self, player):
        """Shows and configures the action controls for the human player."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return

        # --- ENHANCED: Add detailed debugging ---
        self._log_message(f"🎯 CONFIGURING ACTION BAR for {player.name}")
        self._log_message(f"📊 Game state - Current bet: ${game_info['current_bet']:.2f}, Player bet: ${player.current_bet:.2f}")
        self._log_message(f"💰 Player stack: ${player.stack:.2f}, Min raise: ${self.state_machine.game_state.min_raise:.2f}")
        # --- END ENHANCED ---

        # Hide all action buttons initially
        self.human_action_controls['fold'].pack_forget()
        self.human_action_controls['check'].pack_forget()
        self.human_action_controls['call'].pack_forget()
        self.human_action_controls['bet_raise'].pack_forget()

        # Show Fold button
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)

        # Show Check or Call button
        call_amount = game_info['current_bet'] - player.current_bet
        self._log_message(f"🔍 CALL AMOUNT CALCULATION:")
        self._log_message(f"   Current bet from game state: ${game_info['current_bet']:.2f}")
        self._log_message(f"   Player's current bet: ${player.current_bet:.2f}")
        self._log_message(f"   Calculated call amount: ${call_amount:.2f}")
        
        if call_amount > 0:
            self.human_action_controls['call'].config(text=f"Call ${call_amount:.2f}")
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
            self._log_message(f"📞 Call button configured with amount: ${call_amount:.2f}")
        else:
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
            self._log_message(f"✅ Check button shown (no call needed)")

        # Configure the bet/raise slider and button
        if game_info['current_bet'] > 0:
            # For raises, minimum is current bet + min raise
            min_bet = game_info['current_bet'] + self.state_machine.game_state.min_raise
        else:
            # For bets, minimum is min raise
            min_bet = self.state_machine.game_state.min_raise
        
        max_bet = player.stack + player.current_bet

        self.bet_slider.config(from_=min_bet, to=max_bet)
        self.bet_size_var.set(min_bet)
        self._update_bet_size_label()

        # Show the bet/raise button
        if game_info['current_bet'] > 0:
            self.human_action_controls['bet_raise'].config(text="Raise To")
            self._log_message(f"📈 Raise button configured - Min: ${min_bet:.2f}, Max: ${max_bet:.2f}")
        else:
            self.human_action_controls['bet_raise'].config(text="Bet")
            self._log_message(f"💰 Bet button configured - Min: ${min_bet:.2f}, Max: ${max_bet:.2f}")
        self.human_action_controls['bet_raise'].pack(side=tk.LEFT, padx=5)
        
        # --- ENHANCED: Ensure all action bar elements are visible ---
        # Make sure the action bar frame itself is visible
        if hasattr(self, 'action_bar_frame'):
            self.action_bar_frame.grid()  # Ensure it's visible in the grid
            self._log_message(f"DEBUG: Action bar frame grid info: {self.action_bar_frame.grid_info()}")
        
        # Ensure slider and label are visible
        if hasattr(self, 'bet_slider') and hasattr(self, 'bet_size_label'):
            self.bet_slider.pack(fill=tk.X)
            self.bet_size_label.pack()
        
        # Add debug message
        self._log_message(f"DEBUG: Action bar configured - Current bet: ${game_info['current_bet']:.2f}, Player bet: ${player.current_bet:.2f}")
        self._log_message(f"DEBUG: Action bar frame visible: {self.action_bar_frame.winfo_viewable()}")
        self._log_message(f"DEBUG: Buttons packed - Fold: {self.human_action_controls['fold'].winfo_viewable()}, Call: {self.human_action_controls['call'].winfo_viewable()}, Bet: {self.human_action_controls['bet_raise'].winfo_viewable()}")
        # --- END ENHANCED ---

    def _submit_human_action(self, action_str):
        """Submits the human's chosen action to the state machine."""
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            return

        action_map = { "fold": ActionType.FOLD, "check": ActionType.CHECK, "call": ActionType.CALL, "bet": ActionType.BET, "raise": ActionType.RAISE }
        action = action_map.get(action_str)
        
        # --- ENHANCED: Get amount from the slider for bets/raises ---
        amount = 0
        if action in [ActionType.BET, ActionType.RAISE]:
            amount = self.bet_size_var.get()
            self._log_message(f"🎯 SUBMITTING ACTION: {action_str.upper()} ${amount:.2f}")
            self._log_message(f"📊 Current bet: ${self.state_machine.game_state.current_bet:.2f}, Min raise: ${self.state_machine.game_state.min_raise:.2f}")
        elif action == ActionType.CALL:
            # For calls, calculate the amount needed
            call_amount = self.state_machine.game_state.current_bet - player.current_bet
            self._log_message(f"🎯 SUBMITTING ACTION: {action_str.upper()} ${call_amount:.2f}")
            self._log_message(f"📊 Call calculation - Current bet: ${self.state_machine.game_state.current_bet:.2f}, Player bet: ${player.current_bet:.2f}")
        else:
            self._log_message(f"🎯 SUBMITTING ACTION: {action_str.upper()}")
        # --- END ENHANCED ---

        sound_to_play = {"fold": "card_fold", "check": "player_check", "call": "player_call", "bet": "player_bet", "raise": "player_raise"}.get(action_str)
        if sound_to_play:
            self.sfx.play(sound_to_play)

        # --- NEW: Animate betting actions ---
        if action in [ActionType.BET, ActionType.RAISE, ActionType.CALL]:
            player_index = self.state_machine.game_state.players.index(player)
            self._animate_bet(player_index)  # Trigger the animation
        # --- END NEW ---

        self.state_machine.execute_action(player, action, amount)
        
        # Hide controls
        for widget in self.human_action_controls.values():
            if isinstance(widget, ttk.Button): # Check if it's a button before packing
                widget.pack_forget()
        
        # --- ENHANCED: Continue the game after human action ---
        self._log_message(f"🎮 Human action completed: {action_str}")
        self._log_message(f"🔄 Continuing game with next player...")
        
        # Update display to show the action
        self.update_display()
        
        # Continue the game loop after a short delay
        self.after(500, self._continue_game_loop)
        # --- END ENHANCED ---

    def _continue_game_loop(self):
        """Continues the game loop after a human action."""
        self._log_message(f"🔄 Game loop continuation started")
        
        # Check if the game is still active
        if self.state_machine.get_current_state() == PokerState.END_HAND:
            self._log_message(f"🏁 Game ended, no continuation needed")
            return
        
        # Get the current action player
        current_player = self.state_machine.get_action_player()
        if not current_player:
            self._log_message(f"❌ No action player found, stopping game loop")
            return
        
        self._log_message(f"🎯 Current action player: {current_player.name} (Human: {current_player.is_human})")
        
        # If it's a bot's turn, let the state machine handle it
        if not current_player.is_human:
            self._log_message(f"🤖 Bot turn: {current_player.name}")
            # The state machine will handle bot actions automatically via callbacks
            # Just update the display to show the current state
            self.update_display()
        else:
            self._log_message(f"👤 Human turn: {current_player.name}")
            # Human turn - the state machine will call prompt_human_action via callback
            self.update_display()

    def start_new_hand(self):
        """Starts a new hand using the state machine."""
        self.sfx.play("card_deal")
        self.add_game_message("🎮 Starting new hand...")
        
        # Add debugging before starting the hand
        self._log_message("\n=== BEFORE HAND START ===")
        self._log_message(f"Number of players: {self.num_players}")
        
        self.state_machine.start_hand()
        
        # Add debugging after starting the hand
        game_info = self.state_machine.get_game_info()
        if game_info:
            self._log_message("\n=== AFTER HAND START ===")
            self._log_message(f"Action player index: {game_info['action_player']}")
            for i, player in enumerate(game_info['players']):
                self._log_message(f"Player {i}: {player['name']}, Position: {player['position']}, Active: {player['is_active']}")
            
            # Check who should act first
            self._log_message(f"\nFirst to act should be UTG (Under the Gun)")
            for i, player in enumerate(game_info['players']):
                if player['position'] == 'UTG':
                    self._log_message(f"UTG is Player {i+1} at index {i}")
                    self._log_message(f"But action_player is set to index {game_info['action_player']}")
                    break
        # The state machine will now automatically call prompt_human_action via its callback

    def handle_hand_complete(self, winner_info=None):
        """Handles the completion of a hand by displaying the winner on the UI."""
        self.sfx.play("winner_announce")
        
        # --- NEW: Get the final game state to ensure we have the correct winner ---
        game_info = self.state_machine.get_game_info()
        winner_players = self.state_machine.determine_winner()
        
        self._log_message(f"🔍 HAND COMPLETE DEBUG:")
        self._log_message(f"   Game info available: {game_info is not None}")
        self._log_message(f"   Winner players: {[p.name for p in winner_players] if winner_players else 'None'}")
        self._log_message(f"   Parameter winner_info: {winner_info}")
        # --- END NEW ---

        # --- ENHANCED: Prioritize state machine winner over parameter ---
        winner_name = None
        winner_amount = 0
        
        # First priority: Use winner from state machine (most accurate)
        if winner_players:
            winner_name = winner_players[0].name
            winner_amount = self.state_machine.game_state.pot
            self._log_message(f"🏆 Winner from state machine: {winner_name} wins ${winner_amount:.2f}")
        
        # Second priority: Use parameter winner_info (fallback)
        elif winner_info and isinstance(winner_info, dict):
            winner_name = winner_info.get("name")
            winner_amount = winner_info.get("amount", 0)
            self._log_message(f"🏆 Winner from parameter: {winner_name} wins ${winner_amount:.2f}")
        
        # Third priority: Check last winner from state machine
        elif hasattr(self.state_machine, '_last_winner') and self.state_machine._last_winner:
            last_winner = self.state_machine._last_winner
            winner_name = last_winner.get("name")
            winner_amount = last_winner.get("amount", 0)
            self._log_message(f"🏆 Winner from last winner: {winner_name} wins ${winner_amount:.2f}")
        
        # Display winner information
        if winner_name:
            self.add_game_message(f"🏆 {winner_name} wins ${winner_amount:.2f}!")
            
            # --- ENHANCED: Visual feedback for winner ---
            # Find and highlight the winning player's seat
            winner_seat = None
            for i, player_seat in enumerate(self.player_seats):
                if i < len(self.state_machine.game_state.players):
                    player = self.state_machine.game_state.players[i]
                    if player.name == winner_name:
                        frame = player_seat["frame"]
                        frame.config(bg=THEME["accent_secondary"])  # Winner highlight
                        winner_seat = player_seat
                        self._log_message(f"🎯 Highlighting winner seat {i}: {player.name}")
                        break
            
            # --- NEW: Animate pot collection ---
            if hasattr(self, 'pot_label') and winner_seat:
                # Get winner seat position
                winner_x = winner_seat["frame"].winfo_x()
                winner_y = winner_seat["frame"].winfo_y()
                
                # Create animated pot collection effect
                self.pot_label.config(text=f"🏆 {winner_name} wins ${winner_amount:.2f}!", fg="gold")
                
                # Animate pot collection
                self._animate_pot_collection(winner_name, winner_x, winner_y)
                
                # Flash the winner's seat multiple times
                def flash_winner(count=0):
                    if count < 6:  # Flash 3 times (6 state changes)
                        if count % 2 == 0:
                            winner_seat["frame"].config(bg=THEME["accent_primary"])
                        else:
                            winner_seat["frame"].config(bg=THEME["accent_secondary"])
                        self.after(300, lambda: flash_winner(count + 1))
                    else:
                        # Reset to normal after flashing
                        winner_seat["frame"].config(bg=THEME["secondary_bg"])
                        self.pot_label.config(text="Pot: $0.00", fg="yellow")
                
                # Start the flashing animation
                self.after(500, flash_winner)
            else:
                # Fallback if no winner seat found
                if hasattr(self, 'pot_label'):
                    self.pot_label.config(text=f"🏆 {winner_name} wins ${winner_amount:.2f}!", fg="gold")
                    self.after(3000, lambda: self.pot_label.config(text="Pot: $0.00", fg="yellow"))
        else:
            self.add_game_message("🏁 Hand complete!")
        
        # Hide all action buttons
        for widget in self.human_action_controls.values():
            if hasattr(widget, 'pack_forget'):
                widget.pack_forget()
        
        # Add message about starting new hand
        self.add_game_message("💡 Click 'Start New Hand' to begin a new game!")
        
        # Play winner sound
        self.sfx.play("winner_announce")

    def _animate_pot_collection(self, winner_name, winner_x, winner_y):
        """Animates the pot moving to the winner."""
        # Create a temporary label to represent the pot
        pot_anim_label = tk.Label(
            self.canvas, 
            text="💰", 
            font=("Arial", 30), 
            bg=THEME["primary_bg"], 
            fg="yellow"
        )
        
        # Position at center of table (where pot is)
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2 + 130
        
        pot_window = self.canvas.create_window(
            center_x, center_y, 
            window=pot_anim_label
        )

        # Animate the movement
        self._move_widget(
            pot_window, winner_x, winner_y, 20, 
            callback=lambda: pot_anim_label.destroy()
        )

    def _animate_bet(self, player_index):
        """Animates chips moving from the player to the pot area."""
        player_frame = self.player_seats[player_index]["frame"]
        start_x, start_y = player_frame.winfo_x(), player_frame.winfo_y()
        
        # Target is near the center of the table
        target_x = self.canvas.winfo_width() / 2
        target_y = self.canvas.winfo_height() / 2 + 100

        # Create temporary chip labels for the animation
        for i in range(3):  # Animate 3 chips
            chip_label = tk.Label(
                self.canvas, 
                text="💰", 
                font=("Arial", 12), 
                bg=THEME["primary_bg"]
            )
            chip_window = self.canvas.create_window(start_x, start_y, window=chip_label)
            
            # Stagger the animation start time for a nice effect
            self.after(
                i * 50, 
                lambda w=chip_window: self._move_widget(
                    w, target_x, target_y, 15, 
                    callback=lambda: chip_label.destroy()
                )
            )

    def _move_widget(self, widget, target_x, target_y, steps=20, callback=None):
        """Helper function for smooth animation."""
        start_x, start_y = self.canvas.coords(widget)
        dx = (target_x - start_x) / steps
        dy = (target_y - start_y) / steps

        def step(i):
            if i < steps:
                self.canvas.move(widget, dx, dy)
                self.after(20, lambda: step(i+1))
            elif callback:
                callback()
        step(0)

    def update_font_size(self, font_size: int):
        """Updates the font size for all components in the practice session."""
        new_font = (THEME["font_family"], font_size)
        self.info_text.config(font=new_font)
        # You can add other component font updates here if needed

    def _format_card(self, card_str: str) -> str:
        """Formats a card string for display."""
        if not card_str or card_str == "**":
            return "🂠"
        
        rank = card_str[0]
        suit = card_str[1]
        
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_symbol = suit_symbols.get(suit, suit)
        
        return f"{rank}{suit_symbol}"

    def run(self):
        """Main run method for the practice session."""
        self.add_game_message("Welcome to Poker Practice Session!\nClick 'Start New Hand' to begin.") 