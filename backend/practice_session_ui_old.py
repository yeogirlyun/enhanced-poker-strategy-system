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
        # Set up callbacks for state machine events
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_state_change = self.update_display
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
        
        # Table size control - calculate initial scale for 70% of game pane
        self.min_scale = 0.5
        self.max_scale = 2.0
        # Initial scale will be calculated based on canvas size to take 70% of available space
        self.table_scale = 1.0  # Will be recalculated in _calculate_initial_scale()
        
        # UI components
        self.player_seats = []
        self.community_card_labels = []
        self.human_action_controls = {}
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        print(f"🔊 Sound manager initialized: {self.sound_manager.sound_enabled}")
        
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main UI components for the practice session."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main canvas for the poker table
        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Bind canvas resize to redraw table
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Schedule initial redraw after canvas is properly sized
        self.after(100, self._calculate_initial_scale_and_redraw)
        self._create_human_action_controls()
        
        # Don't automatically start a hand - let user do it manually
        # self.after(500, self.start_new_hand)

    def _calculate_initial_scale_and_redraw(self):
        """Calculate initial scale based on canvas size and redraw the table."""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 0 and canvas_height > 0:
            # Calculate scale to fit table in 70% of available space
            # Base table size is 900x600
            # Use the smaller dimension to ensure table fits in both directions
            scale_x = (canvas_width * 0.7) / 900
            scale_y = (canvas_height * 0.7) / 600
            # Use the larger scale to maximize table size while fitting
            self.table_scale = min(max(scale_x, scale_y), self.max_scale)
            self.table_scale = max(self.table_scale, self.min_scale)
            
            # Ensure minimum reasonable scale for better visibility
            if self.table_scale < 0.8:
                self.table_scale = 0.8
        else:
            # Fallback scale if canvas not yet sized
            self.table_scale = 1.0
        
        # Redraw the table with calculated scale
        self._redraw_table_with_scale()
        
        # Update display after table is created
        self.update_display()

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

        # Start hand button
        self.human_action_controls['start_hand'] = ttk.Button(
            controls_frame, 
            text="Start Hand", 
            command=self.start_new_hand,
            style="Success.TButton"
        )
        ToolTip(self.human_action_controls['start_hand'], "Start a new poker hand")

        # Initially hide all controls except start hand
        for widget in self.human_action_controls.values():
            widget.pack_forget()
        
        # Show start hand button initially
        self.human_action_controls['start_hand'].pack(side=tk.LEFT, padx=5)

    def update_display(self, new_state=None):
        """Updates the entire UI based on the current game state from the state machine."""
        game_info = self.state_machine.get_game_info()
        if not game_info or not game_info.get('players'):
            print(f"❌ No game info available from state machine")
            # Initialize with default values
            self._update_display_with_defaults()
            return

        print(f"🎮 Updating display with game info: {game_info}")

        # Update pot and community cards
        self.pot_label.config(text=f"Pot: ${game_info['pot']:.2f}")
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
                    cards_text = " ".join(self._format_card(c) for c in player_info['cards'])
                    seat['cards'].config(text=cards_text)
                else:
                    seat['cards'].config(text="🂠 🂠" if player_info['is_active'] else "")

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
        
        # Set default player info
        for i, seat in enumerate(self.player_seats):
            if i < len(self.player_stacks):
                seat['stack'].config(text=f"${self.player_stacks[i]:.2f}")
                seat['cards'].config(text="")
                seat['frame'].config(bg=THEME["secondary_bg"])
                seat['name'].config(fg=THEME["text"])
        
        self._update_info_panel()

    def handle_hand_complete(self):
        """Handles the completion of a hand."""
        print(f"🏆 Hand complete!")
        winner_info = self.state_machine.determine_winner()
        if winner_info:
            winner_names = ", ".join(p.name for p in winner_info)
            messagebox.showinfo("Hand Over", f"Winner is: {winner_names}")
        
        # Show start hand button again
        for widget in self.human_action_controls.values():
            widget.pack_forget()
        self.human_action_controls['start_hand'].pack(side=tk.LEFT, padx=5)
        
        # Ask to start a new hand
        if messagebox.askyesno("New Hand", "Start a new hand?"):
            self.start_new_hand()

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
        """Starts a new hand using the state machine."""
        print(f"🎮 Starting new hand with state machine")
        
        # Initialize the state machine properly
        self.state_machine.start_hand()
        
        # Wait a moment for state machine to initialize
        self.after(100, self._continue_hand_start)
    
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

    def prompt_human_action(self):
        """Shows the action controls for the human player."""
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            print(f"❌ No human player to act or player is not human")
            return
        
        print(f"✅ Showing action controls for human player: {player.name}")
        
        # Hide all controls first (including start hand button)
        for widget in self.human_action_controls.values():
            widget.pack_forget()

        # Show relevant controls based on current situation
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        
        # Check if player can check (no current bet) or must call
        current_bet = self.state_machine.game_state.current_bet
        if current_bet == 0:
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        else:
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        
        self.human_action_controls['bet'].pack(side=tk.LEFT, padx=5)
        self.human_action_controls['raise'].pack(side=tk.LEFT, padx=5)
        self.human_action_controls['amount_entry'].pack(side=tk.LEFT, padx=5)

    def _submit_human_action(self, action_str):
        """Submits the human's chosen action to the state machine."""
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            print(f"❌ No human player to act or player is not human")
            return

        action_map = {
            "fold": ActionType.FOLD,
            "check": ActionType.CHECK,
            "call": ActionType.CALL,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE
        }
        action = action_map.get(action_str)
        
        if not action:
            print(f"❌ Invalid action: {action_str}")
            return

        amount = 0
        if action in [ActionType.BET, ActionType.RAISE]:
            try:
                amount = float(self.amount_var.get())
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number.")
                return

        # Play sound effect based on action
        if action == ActionType.FOLD:
            self.sound_manager.play("player_fold")
        elif action == ActionType.CHECK:
            self.sound_manager.play("player_check")
        elif action == ActionType.CALL:
            self.sound_manager.play("player_call")
        elif action in [ActionType.BET, ActionType.RAISE]:
            self.sound_manager.play("chip_bet")
            if action == ActionType.RAISE:
                self.sound_manager.play("player_raise")

        # Use the state machine to execute the action
        print(f"🎮 Executing action: {action_str} with amount: {amount}")
        self.state_machine.execute_action(player, action, amount)
        self.update_display()

        # Hide controls after action
        for widget in self.human_action_controls.values():
            widget.pack_forget()

    def _ai_turn(self):
        """Simulates AI player turns."""
        print(f"🎮 _ai_turn called - current_player: {self.current_player}")
        print(f"🎮 player_acted status: {self.player_acted}")
        
        # Find next player who hasn't acted
        original_player = self.current_player
        attempts = 0
        while attempts < self.num_players:
            self.current_player = (self.current_player + 1) % self.num_players
            attempts += 1
            print(f"🎮 Checking player {self.current_player}, acted: {self.player_acted[self.current_player]}")
            
            if not self.player_acted[self.current_player]:
                print(f"✅ Found player {self.current_player} who hasn't acted")
                break
            
            if self.current_player == original_player:
                print(f"🔄 All players have acted, starting new round")
                # All players have acted, start new round or end hand
                self._start_new_round()
                return
        
        if attempts >= self.num_players:
            print(f"❌ No players found who haven't acted, starting new round")
            self._start_new_round()
            return
        
        if self.current_player == 0:  # Back to human
            print(f"👤 Back to human player")
            self.prompt_human_action()
        else:
            print(f"🤖 AI player {self.current_player} taking action")
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
                self.sound_manager.play("chip_bet")
            elif action == "call":
                call_amount = self.current_bet
                self.player_stacks[self.current_player] -= call_amount
                self.pot += call_amount
                self.player_seats[self.current_player]['action'].config(text=f"Called ${call_amount:.2f}")
                self.sound_manager.play("player_call")
            else:  # fold
                self.player_seats[self.current_player]['action'].config(text="Folded")
                self.sound_manager.play("player_fold")
            
            # Mark AI player as having acted
            self.player_acted[self.current_player] = True
            
            # Continue to next player after a short delay
            self.after(1000, self._ai_turn)
        
        self.update_display()

    def _start_new_round(self):
        """Starts a new betting round (flop, turn, river)."""
        print(f"🔄 Starting new round - resetting action tracking")
        
        # Reset player action tracking for new round
        # Players who folded in previous rounds should stay folded
        for i in range(self.num_players):
            if "Folded" in self.player_seats[i]['action'].cget("text"):
                # Keep folded players marked as acted
                self.player_acted[i] = True
                print(f"🎯 Player {i} stays folded")
            else:
                # Reset action tracking for active players
                self.player_acted[i] = False
                print(f"🔄 Player {i} action reset for new round")
        
        self.current_bet = 0.0
        
        # Deal community cards based on current round
        if len(self.community_cards) == 0:
            # Deal flop (3 cards)
            import random
            ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
            suits = ['s', 'h', 'd', 'c']
            all_cards = []
            for rank in ranks:
                for suit in suits:
                    all_cards.append(f"{rank}{suit}")
            random.shuffle(all_cards)
            
            # Remove cards already dealt to players
            for player_cards in self.player_cards:
                for card in player_cards:
                    if card in all_cards:
                        all_cards.remove(card)
            
            # Deal flop with sound effects
            for i in range(3):
                if all_cards:
                    self.community_cards.append(all_cards.pop())
                    self.sound_manager.play("card_deal")
        elif len(self.community_cards) == 3:
            # Deal turn
            import random
            ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
            suits = ['s', 'h', 'd', 'c']
            all_cards = []
            for rank in ranks:
                for suit in suits:
                    all_cards.append(f"{rank}{suit}")
            
            # Remove cards already dealt
            for player_cards in self.player_cards:
                for card in player_cards:
                    if card in all_cards:
                        all_cards.remove(card)
            for card in self.community_cards:
                if card in all_cards:
                    all_cards.remove(card)
            
            if all_cards:
                self.community_cards.append(all_cards.pop())
        elif len(self.community_cards) == 4:
            # Deal river
            import random
            ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
            suits = ['s', 'h', 'd', 'c']
            all_cards = []
            for rank in ranks:
                for suit in suits:
                    all_cards.append(f"{rank}{suit}")
            
            # Remove cards already dealt
            for player_cards in self.player_cards:
                for card in player_cards:
                    if card in all_cards:
                        all_cards.remove(card)
            for card in self.community_cards:
                if card in all_cards:
                    all_cards.remove(card)
            
            if all_cards:
                self.community_cards.append(all_cards.pop())
                self.sound_manager.play("card_deal")
        else:
            # Hand is complete, show results
            self._show_hand_results()
            return
        
        # Start with first player after dealer
        self.current_player = 0
        self.update_display()
        self.prompt_human_action()

    def _show_hand_results(self):
        """Shows the results of the completed hand."""
        # Simple result display
        messagebox.showinfo("Hand Complete", f"Hand finished! Final pot: ${self.pot:.2f}")
        self.start_new_hand()

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
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=int(3 * self.table_scale), relief="ridge")
        
        # Scale font sizes with better minimums for visibility
        name_font_size = max(10, int(FONTS["header"][1] * self.table_scale))
        main_font_size = max(8, int(FONTS["main"][1] * self.table_scale))
        small_font_size = max(6, int(FONTS["small"][1] * self.table_scale))
        card_font_size = max(16, int(24 * self.table_scale))
        
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
        
        # Create scaled community card area with better sizing
        card_width = int(70 * self.table_scale)
        card_height = int(100 * self.table_scale)
        card_spacing = int(80 * self.table_scale)
        
        for i in range(5):
            x = center_x - (card_spacing * 2) + (i * card_spacing)
            y = center_y
            card_label = tk.Label(
                self.canvas, 
                text="", 
                bg="#015939", 
                fg="white", 
                font=("Arial", max(16, int(28 * self.table_scale)), "bold"), 
                bd=int(3 * self.table_scale), 
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
            font=(FONTS["title"][0], max(12, int(FONTS["title"][1] * self.table_scale)))
        )
        self.canvas.create_window(center_x, center_y + int(150 * self.table_scale), window=self.pot_label)
    
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
        # Scale panel size more aggressively for better visibility
        panel_width = int(350 * self.table_scale)
        panel_height = int(300 * self.table_scale)
        
        self.info_panel = tk.Frame(
            self.canvas, 
            bg=THEME["secondary_bg"], 
            bd=int(3 * self.table_scale), 
            relief="ridge"
        )
        
        # Scale title font with better scaling
        title_font_size = max(12, int(FONTS["header"][1] * self.table_scale))
        title_label = tk.Label(
            self.info_panel, 
            text="Game Information", 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            font=(FONTS["header"][0], title_font_size, "bold")
        )
        title_label.pack(pady=int(10 * self.table_scale))
        
        # Scale text widget with larger dimensions and better font scaling
        text_height = int(18 * self.table_scale)
        text_width = int(40 * self.table_scale)
        text_font_size = max(10, int(16 * self.table_scale))
        
        self.info_text = tk.Text(
            self.info_panel,
            height=text_height,
            width=text_width,
            font=("Consolas", text_font_size),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=int(10 * self.table_scale),
            pady=int(10 * self.table_scale)
        )
        self.info_text.pack(padx=int(10 * self.table_scale), pady=int(10 * self.table_scale))
        
        # Position info panel in top-right with scaled positioning
        panel_x = canvas_width - int(370 * self.table_scale)
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

    def _on_canvas_resize(self, event):
        """Handle canvas resize events to keep table centered."""
        # Only redraw if the canvas size actually changed significantly
        if hasattr(self, '_last_canvas_size'):
            last_width, last_height = self._last_canvas_size
            if abs(event.width - last_width) > 10 or abs(event.height - last_height) > 10:
                self._redraw_table_with_scale()
        else:
            self._redraw_table_with_scale()
        
        self._last_canvas_size = (event.width, event.height)

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