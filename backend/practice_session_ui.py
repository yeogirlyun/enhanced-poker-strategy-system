#!/usr/bin/env python3
"""
Practice Session UI Module for Enhanced Poker Strategy GUI (Corrected)

This version resolves the game stall bug by making the UI a pure renderer
and letting the state machine control the entire game flow.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading # Still needed for bot action delays in the state machine
import time

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType, PokerState
from sound_manager import SoundManager
from gui_models import THEME, FONTS
from tooltips import ToolTip

class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that correctly follows the
    state machine's flow.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.strategy_data = strategy_data
        
        self.state_machine = ImprovedPokerStateMachine(
            num_players=6, 
            strategy_data=self.strategy_data, 
            root_tk=self.winfo_toplevel()
        )
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_state_change = self.update_display
        self.state_machine.on_log_entry = self.add_game_message
        self.state_machine.on_action_executed = self._animate_player_action  # NEW: Connect action animations
        
        self.sfx = SoundManager()
        self.player_seats = []
        self.community_card_labels = []
        self.human_action_controls = {}
        self.num_players = 6
        
        # NEW: Track action indicators for each player
        self.action_indicators = {}  # player_index -> action_label
        self.last_action_player = None  # Track who last acted
        
        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI layout with a responsive grid."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        right_panel_frame = ttk.Frame(self)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Session Info Area (Upper) with Scrollbar
        session_frame = ttk.LabelFrame(right_panel_frame, text="Session Information", padding=10)
        session_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create frame for session text and scrollbar
        session_text_frame = tk.Frame(session_frame)
        session_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Session text widget
        self.session_text = tk.Text(
            session_text_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=FONTS["main"],  # Use main font instead of small
            height=8,
            wrap=tk.WORD  # Enable word wrapping
        )
        self.session_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Session scrollbar
        self.session_scrollbar = ttk.Scrollbar(
            session_text_frame, 
            orient=tk.VERTICAL, 
            command=self.session_text.yview
        )
        self.session_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_text.config(yscrollcommand=self.session_scrollbar.set)
        
        # Action Messages Area (Lower) with Scrollbar
        action_frame = ttk.LabelFrame(right_panel_frame, text="Action Messages", padding=10)
        action_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create frame for action text and scrollbar
        action_text_frame = tk.Frame(action_frame)
        action_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Action text widget
        self.info_text = tk.Text(
            action_text_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=FONTS["main"],  # Use main font instead of small
            height=6,
            wrap=tk.WORD  # Enable word wrapping
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Action scrollbar
        self.action_scrollbar = ttk.Scrollbar(
            action_text_frame, 
            orient=tk.VERTICAL, 
            command=self.info_text.yview
        )
        self.action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=self.action_scrollbar.set)

        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        self._create_human_action_controls(controls_frame)

        self.canvas.bind("<Configure>", self._on_resize)
        
        # Initialize table felt colors
        self.table_felt_colors = {
            "classic_green": {
                "outer": "#013f28",
                "inner": "#015939", 
                "pattern": "#014a2f",
                "community_bg": "#015939"
            },
            "royal_blue": {
                "outer": "#1a365d",
                "inner": "#2d5aa0",
                "pattern": "#1e4a8a",
                "community_bg": "#2d5aa0"
            },
            "burgundy_red": {
                "outer": "#4a1a1a",
                "inner": "#8b2d2d",
                "pattern": "#6b1e1e",
                "community_bg": "#8b2d2d"
            },
            "deep_purple": {
                "outer": "#2d1a4a",
                "inner": "#5a2d8b",
                "pattern": "#4a1e6b",
                "community_bg": "#5a2d8b"
            },
            "golden_brown": {
                "outer": "#4a3a1a",
                "inner": "#8b6b2d",
                "pattern": "#6b4a1e",
                "community_bg": "#8b6b2d"
            },
            "ocean_blue": {
                "outer": "#1a4a4a",
                "inner": "#2d8b8b",
                "pattern": "#1e6b6b",
                "community_bg": "#2d8b8b"
            },
            "forest_green": {
                "outer": "#1a4a1a",
                "inner": "#2d8b2d",
                "pattern": "#1e6b1e",
                "community_bg": "#2d8b2d"
            },
            "midnight_black": {
                "outer": "#1a1a1a",
                "inner": "#2d2d2d",
                "pattern": "#1e1e1e",
                "community_bg": "#2d2d2d"
            }
        }
        
        # Set default felt color
        self.current_felt_color = "classic_green"
    
    # --- All _draw methods remain the same ---
    def _on_resize(self, event=None):
        self.canvas.delete("all")
        self._draw_table()
        self._draw_player_seats()
        self._draw_community_card_area()
        self._draw_pot_display()
        self.update_display()

    def _draw_table(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Get current felt colors
        felt_colors = self.table_felt_colors[self.current_felt_color]
        
        self.canvas.create_oval(width*0.05, height*0.1, width*0.95, height*0.9, fill=felt_colors["outer"], outline=THEME["border"], width=10)
        self.canvas.create_oval(width*0.06, height*0.11, width*0.94, height*0.89, fill=felt_colors["inner"], outline="#222222", width=2)
        x_start, x_end = int(width * 0.1), int(width * 0.9)
        y_start, y_end = int(height * 0.15), int(height * 0.85)
        for i in range(x_start, x_end, 20):
            for j in range(y_start, y_end, 20):
                if (((i - width/2)**2 / (width*0.4)**2) + ((j - height/2)**2 / (height*0.35)**2)) < 1:
                    if (i + j) % 40 == 0:
                        self.canvas.create_oval(i, j, i + 15, j + 15, fill=felt_colors["pattern"], outline="")

    def _draw_player_seats(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        radius_x, radius_y = width * 0.42, height * 0.35
        self.player_seats = [{} for _ in range(self.num_players)]
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        for i in range(self.num_players):
            angle = (2 * math.pi / self.num_players) * i - (math.pi / 2)
            seat_x = center_x + radius_x * math.cos(angle)
            seat_y = center_y + radius_y * math.sin(angle)
            self._create_player_seat_widget(seat_x, seat_y, f"Player {i+1}", positions[i], i)
            bet_radius_x, bet_radius_y = radius_x * 0.7, radius_y * 0.7
            bet_x = center_x + bet_radius_x * math.cos(angle)
            bet_y = center_y + bet_radius_y * math.sin(angle)
            felt_colors = self.table_felt_colors[self.current_felt_color]
            bet_label = tk.Label(self.canvas, text="", bg=felt_colors["community_bg"], fg="yellow", font=FONTS["stack_bet"])
            bet_window = self.canvas.create_window(bet_x, bet_y, window=bet_label, anchor="center", state="hidden")
            self.player_seats[i]["bet_label_widget"] = bet_label
            self.player_seats[i]["bet_label_window"] = bet_window

    def _create_player_seat_widget(self, x, y, name, position, index):
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=2, relief="ridge")
        
        # Create name and position labels with proper font scaling
        name_label = tk.Label(
            seat_frame, 
            text=name, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            font=FONTS["player_name"]
        )
        name_label.pack()
        
        position_label = tk.Label(
            seat_frame, 
            text=position, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text_dark"], 
            font=FONTS["small"]
        )
        position_label.pack()
        
        # Cards area
        cards_label = tk.Label(
            seat_frame, 
            text="🂠 🂠", 
            bg=THEME["secondary_bg"], 
            fg="#CCCCCC", 
            font=FONTS["cards"]
        )
        cards_label.pack(pady=5)
        
        # Bet information (current bet amount)
        bet_label = tk.Label(
            seat_frame, 
            text="", 
            bg=THEME["secondary_bg"], 
            fg="orange", 
            font=FONTS["stack_bet"]
        )
        bet_label.pack()
        
        # Store references for updates
        self.player_seats[index] = {
            "frame": seat_frame, 
            "name_label": name_label, 
            "position_label": position_label,
            "cards_label": cards_label, 
            "bet_label": bet_label
        }
        self.canvas.create_window(x, y, window=seat_frame, anchor="center")
        
        # Create separate stack graphics area in front of player
        self._create_stack_graphics(index, x, y)
    
    def _create_stack_graphics(self, player_index, seat_x, seat_y):
        """Create a separate stack graphics area positioned in front of the player."""
        # Calculate position for stack graphics (in front of player, closer to table center)
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        
        # Position stack graphics closer to table center than player seat
        stack_radius_x = width * 0.35  # Closer to center than player seats
        stack_radius_y = height * 0.28
        
        # Calculate angle for this player
        angle = (2 * math.pi / self.num_players) * player_index - (math.pi / 2)
        stack_x = center_x + stack_radius_x * math.cos(angle)
        stack_y = center_y + stack_radius_y * math.sin(angle)
        
        # Create stack graphics frame
        stack_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=1, relief="solid")
        
        # Stack amount label
        stack_amount_label = tk.Label(
            stack_frame,
            text="$100.00",
            bg=THEME["secondary_bg"],
            fg="yellow",
            font=FONTS["stack_bet"]
        )
        stack_amount_label.pack(pady=2)
        
        # Stack chips visualization (using Unicode chip symbols)
        chips_label = tk.Label(
            stack_frame,
            text="🟡🟡🟡",  # Yellow chips
            bg=THEME["secondary_bg"],
            fg="yellow",
            font=FONTS["small"]
        )
        chips_label.pack()
        
        # Store stack graphics references
        if "stack_graphics" not in self.player_seats[player_index]:
            self.player_seats[player_index]["stack_graphics"] = {}
        
        self.player_seats[player_index]["stack_graphics"] = {
            "frame": stack_frame,
            "amount_label": stack_amount_label,
            "chips_label": chips_label
        }
        
        # Create window for stack graphics
        stack_window = self.canvas.create_window(
            stack_x, stack_y, 
            window=stack_frame, 
            anchor="center"
        )
        self.player_seats[player_index]["stack_graphics"]["window"] = stack_window

    def _draw_community_card_area(self):
        center_x, center_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        felt_colors = self.table_felt_colors[self.current_felt_color]
        community_frame = tk.Frame(self.canvas, bg=felt_colors["community_bg"], bd=2, relief="groove")
        self.community_card_labels = []
        for i in range(5):
            # Use responsive font sizing for community cards
            card_font_size = max(16, int(self.canvas.winfo_height() / 25))
            card_font = (THEME["font_family"], card_font_size, "bold")
            card_label = tk.Label(
                community_frame, 
                text="", 
                bg="#015939", 
                fg="white", 
                font=card_font, 
                width=4
            )
            card_label.pack(side=tk.LEFT, padx=3)
            self.community_card_labels.append(card_label)
        self.canvas.create_window(center_x, center_y, window=community_frame)

    def _draw_pot_display(self):
        center_x, center_y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        # Use responsive font sizing for pot display
        pot_font_size = max(14, int(self.canvas.winfo_height() / 30))
        pot_font = (THEME["font_family"], pot_font_size, "bold")
        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            bg="#013f28", 
            fg="yellow", 
            font=pot_font
        )
        self.canvas.create_window(center_x, center_y + 130, window=self.pot_label)
    
    # --- UI Update and Action Handling (Corrected) ---

    def _submit_human_action(self, action_str):
        """
        Submits the human's action to the state machine and does nothing else.
        The state machine will control all subsequent game flow via callbacks.
        """
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            return

        action_map = { "fold": ActionType.FOLD, "check": ActionType.CHECK, "call": ActionType.CALL, "bet": ActionType.BET, "raise": ActionType.RAISE }
        action = action_map.get(action_str)
        
        # FIX: Only get an amount for a bet or raise.
        amount = 0
        if action in [ActionType.BET, ActionType.RAISE]:
            amount = self.bet_size_var.get()

        # Play sound
        sound_to_play = {"fold": "card_fold", "check": "player_check", "call": "player_call", "bet": "player_bet", "raise": "player_raise"}.get(action_str)
        if sound_to_play:
            self.sfx.play(sound_to_play)

        # Hide the controls immediately. The state machine will show them again when it's our turn.
        self._show_game_control_buttons()
        
        # Let the state machine handle EVERYTHING from here.
        self.state_machine.execute_action(player, action, amount)

    def prompt_human_action(self, player):
        """Shows and configures the action controls for the human player."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return

        self._show_action_buttons()
        
        # --- FIXED: Use state machine's valid actions instead of duplicating logic ---
        valid_actions = self.state_machine.get_valid_actions_for_player(player)
        
        # Configure fold button based on state machine's validation
        if valid_actions.get('fold', False):
            self.human_action_controls['fold'].config(state='normal')
            self.human_action_controls['fold'].config(text="Fold")
        else:
            self.human_action_controls['fold'].config(state='disabled')
            self.human_action_controls['fold'].config(text="Fold (Invalid)")
        
        # Get call amount from state machine
        call_amount = valid_actions.get('call_amount', 0)
        # --- End of proper separation of concerns ---
        
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        if call_amount > 0:
            self.human_action_controls['check'].pack_forget()
            self.human_action_controls['call'].config(text=f"Call ${call_amount:.2f}")
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
            self.human_action_controls['bet_raise'].config(text="Raise To")
        else:
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
            self.human_action_controls['call'].pack_forget()
            self.human_action_controls['bet_raise'].config(text="Bet")
        
        self.human_action_controls['bet_raise'].pack(side=tk.RIGHT, padx=5)

        # Use state machine's values for bet/raise slider
        min_bet_or_raise = valid_actions.get('min_raise', self.state_machine.game_state.min_raise)
        max_bet = valid_actions.get('max_bet', player.stack + player.current_bet)
        
        self.bet_slider.config(from_=min_bet_or_raise, to=max_bet)
        self.bet_size_var.set(min_bet_or_raise)
        self._update_bet_size_label()

    def start_new_hand(self):
        """Starts a new hand using the state machine."""
        self.add_game_message("🎮 Starting new hand...")
        
        # FIX: Clear community cards when starting a new hand
        for card_label in self.community_card_labels:
            card_label.config(text="")
        
        self.state_machine.start_hand()
        # The state machine will automatically determine who acts first
        # and call prompt_human_action if it's the human's turn.
        self.update_session_info()

    def handle_hand_complete(self, winner_info=None):
        """
        Handles hand completion by displaying the winner info received from the state machine.
        """
        print(f"🎯 UI: handle_hand_complete called with: {winner_info}")  # Debug
        
        self.sfx.play("winner_announce")
        
        if winner_info and winner_info.get("name"):
            winner_names = winner_info["name"]
            pot_amount = winner_info["amount"]
            winning_hand = winner_info.get("hand", "")
            final_board = winner_info.get("board", [])

            print(f"🎯 UI: Winner: {winner_names}, Amount: ${pot_amount}, Board: {final_board}")  # Debug

            # --- ENHANCED: Better winner announcement and animation ---
            # Display the final community cards
            for i, card_label in enumerate(self.community_card_labels):
                if i < len(final_board):
                    card_text = self._format_card(final_board[i])
                    card_label.config(text=card_text)
                    print(f"🎯 UI: Set card {i} to: {card_text}")  # Debug
                    # Force the card label to update
                    card_label.update()
                else:
                    card_label.config(text="")
            
            # Force the canvas to refresh
            self.canvas.update()

            # Create a more descriptive announcement with proper formatting
            if pot_amount > 0:
                announcement = f"🏆 {winner_names} wins ${pot_amount:.2f}!"
                if winning_hand and winning_hand != "Unknown":
                    announcement += f" ({winning_hand})"
                
                # Update pot label with winner info
                self.pot_label.config(text=f"Winner: {winner_names}!", fg=THEME["accent_secondary"])
                self.pot_label.update()  # Force pot label update
                self.add_game_message(announcement)
                
                # Start pot animation to winner
                self._animate_pot_to_winner(winner_info)
            else:
                # Handle edge case where pot is $0 (shouldn't happen with our fix)
                self.add_game_message("🏁 Hand complete - no pot to award")
                self.pot_label.config(text="Hand Complete", fg=THEME["text_primary"])
        else:
            self.add_game_message("🏁 Hand complete!")
            self.pot_label.config(text="Hand Complete", fg=THEME["text_primary"])

        # Show game controls after a delay
        self.after(3000, self._show_game_control_buttons)

    def _animate_pot_to_winner(self, winner_info):
        """Animate pot money moving to the winner's stack."""
        print(f"🎬 Starting animation for winner: {winner_info}")  # Debug
        
        # Handle multiple winners (comma-separated names)
        winner_names = winner_info['name'].split(', ')
        print(f"🎯 Winner names: {winner_names}")  # Debug
        
        # Find the first winner's seat (or any winner if multiple)
        winner_seat = None
        for winner_name in winner_names:
            for i, seat in enumerate(self.player_seats):
                if seat and seat.get("name_label"):
                    player_name = seat["name_label"].cget("text").split('\n')[0]
                    print(f"🔍 Checking seat {i}: {player_name} vs {winner_name}")  # Debug
                    if player_name == winner_name:
                        winner_seat = i
                        print(f"✅ Found winner at seat {i}")  # Debug
                        break
            if winner_seat is not None:
                break
        
        # FIX: If we can't find the winner seat, use seat 0 as fallback
        if winner_seat is None:
            print(f"⚠️ Could not find winner seat, using seat 0 as fallback")
            winner_seat = 0
        
        if winner_seat is not None:
            print(f"🎯 Animating to seat {winner_seat}")  # Debug
            
            # Get pot center position
            pot_x = self.canvas.winfo_width() / 2
            pot_y = self.canvas.winfo_height() / 2 + 130  # Pot label position
            
            # Get winner's position
            seat_positions = [
                (self.canvas.winfo_width() * 0.5, self.canvas.winfo_height() * 0.1),  # Top
                (self.canvas.winfo_width() * 0.8, self.canvas.winfo_height() * 0.2),  # Top-right
                (self.canvas.winfo_width() * 0.9, self.canvas.winfo_height() * 0.5),  # Right
                (self.canvas.winfo_width() * 0.8, self.canvas.winfo_height() * 0.8),  # Bottom-right
                (self.canvas.winfo_width() * 0.5, self.canvas.winfo_height() * 0.9),  # Bottom
                (self.canvas.winfo_width() * 0.2, self.canvas.winfo_height() * 0.8),  # Bottom-left
            ]
            
            winner_x, winner_y = seat_positions[winner_seat]
            print(f"📍 From ({pot_x:.0f}, {pot_y:.0f}) to ({winner_x:.0f}, {winner_y:.0f})")  # Debug
            
            # Create enhanced animated money object with glow effect
            money_obj = self.canvas.create_text(
                pot_x, pot_y, 
                text=f"${winner_info['amount']:.2f}", 
                fill="#FFD700",  # Bright gold
                font=("Arial", 18, "bold"),
                tags="money_animation"
            )
            
            # Add glow effect
            glow_obj = self.canvas.create_text(
                pot_x, pot_y, 
                text=f"${winner_info['amount']:.2f}", 
                fill="#FFA500",  # Orange glow
                font=("Arial", 20, "bold"),
                tags="money_animation_glow"
            )
            
            print(f"💰 Created enhanced money animation: ${winner_info['amount']:.2f}")  # Debug
            
            # Enhanced animation with multiple effects
            def animate_money(step=0):
                if step <= 30:  # 30 steps for smoother animation
                    progress = step / 30
                    # Enhanced easing function
                    ease = 1 - (1 - progress) ** 2
                    
                    current_x = pot_x + (winner_x - pot_x) * ease
                    current_y = pot_y + (winner_y - pot_y) * ease
                    
                    # Update both objects
                    self.canvas.coords(money_obj, current_x, current_y)
                    self.canvas.coords(glow_obj, current_x, current_y)
                    
                    # Scale effect - money gets bigger as it moves
                    scale = 1.0 + (progress * 0.5)
                    font_size = int(18 * scale)
                    glow_font_size = int(20 * scale)
                    
                    self.canvas.itemconfig(money_obj, font=("Arial", font_size, "bold"))
                    self.canvas.itemconfig(glow_obj, font=("Arial", glow_font_size, "bold"))
                    
                    # Color transition effect
                    if progress > 0.5:
                        # Transition from gold to green (success color)
                        green_intensity = int(255 * (progress - 0.5) * 2)
                        color = f"#00{green_intensity:02x}00"  # Green with increasing intensity
                        self.canvas.itemconfig(money_obj, fill=color)
                    
                    # Fade out glow as it approaches
                    if progress > 0.7:
                        alpha = int(255 * (1 - (progress - 0.7) / 0.3))
                        glow_color = f"#{alpha:02x}ff{alpha:02x}"
                        self.canvas.itemconfig(glow_obj, fill=glow_color)
                    
                    self.canvas.after(40, lambda: animate_money(step + 1))  # Faster animation
                else:
                    # Remove the animated objects
                    self.canvas.delete(money_obj)
                    self.canvas.delete(glow_obj)
                    print("🎬 Enhanced animation complete")  # Debug
                    # Update the winner's stack display
                    self.update_display()
            
            # Start the animation
            animate_money()
        else:
            print(f"❌ Could not find winner seat for: {winner_info['name']}")  # Debug
            print(f"🔍 Available seats: {[seat.get('name_label').cget('text').split('\n')[0] if seat and seat.get('name_label') else 'None' for seat in self.player_seats]}")  # Debug
    
    def add_game_message(self, message):
        """Add a message to the action messages area."""
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.insert(tk.END, f"{message}\n")
            self.info_text.see(tk.END)
            self.info_text.config(state=tk.DISABLED)
    
    def update_session_info(self):
        """Update the session information display."""
        if not self.state_machine.session_state:
            return
        
        session_info = self.state_machine.get_session_info()
        comprehensive_data = self.state_machine.get_comprehensive_session_data()
        
        self.session_text.config(state=tk.NORMAL)
        self.session_text.delete(1.0, tk.END)
        
        # Display session information
        display_text = "📊 SESSION INFORMATION\n"
        display_text += "=" * 40 + "\n\n"
        
        # Basic session info
        display_text += f"Session ID: {session_info.get('session_id', 'N/A')}\n"
        display_text += f"Duration: {session_info.get('session_duration', 0):.1f}s\n"
        display_text += f"Hands Played: {session_info.get('hands_played', 0)}\n"
        display_text += f"Human Wins: {session_info.get('human_wins', 0)}\n"
        display_text += f"Human Losses: {session_info.get('human_losses', 0)}\n"
        display_text += f"Big Blind: ${session_info.get('big_blind_amount', 1.0)}\n\n"
        
        # Current hand info
        game_info = self.state_machine.get_game_info()
        if game_info:
            display_text += "🎯 CURRENT HAND\n"
            display_text += "-" * 20 + "\n"
            display_text += f"State: {game_info.get('state', 'Unknown')}\n"
            display_text += f"Pot: ${game_info.get('pot', 0):.2f}\n"
            display_text += f"Current Bet: ${game_info.get('current_bet', 0):.2f}\n"
            display_text += f"Board: {game_info.get('board', [])}\n\n"
            
            # Valid actions
            valid_actions = game_info.get('valid_actions', {})
            if valid_actions:
                display_text += "✅ VALID ACTIONS\n"
                display_text += "-" * 15 + "\n"
                for action, is_valid in valid_actions.items():
                    if isinstance(is_valid, bool) and is_valid:
                        display_text += f"• {action.title()}\n"
                    elif isinstance(is_valid, dict) and is_valid.get('amount'):
                        display_text += f"• {action.title()}: ${is_valid['amount']:.2f}\n"
                display_text += "\n"
        
        # Session statistics
        if comprehensive_data:
            stats = comprehensive_data.get('session_statistics', {})
            if stats:
                display_text += "📈 SESSION STATS\n"
                display_text += "-" * 15 + "\n"
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        display_text += f"• {key.replace('_', ' ').title()}: {value}\n"
        
        # Table size information
        table_size_info = self.get_table_size_info()
        display_text += "\n🎮 TABLE LAYOUT\n"
        display_text += "-" * 15 + "\n"
        display_text += f"• Table Area: {table_size_info['table_percentage']:.1f}%\n"
        display_text += f"• Message Area: {table_size_info['message_percentage']:.1f}%\n"
        display_text += f"• Table Weight: {table_size_info['table_weight']}\n"
        display_text += f"• Message Weight: {table_size_info['message_weight']}\n"
        display_text += f"• Felt Color: {self.current_felt_color.replace('_', ' ').title()}\n"
        
        self.session_text.insert(1.0, display_text)
        self.session_text.config(state=tk.DISABLED)

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

        # --- NEW: Game Control Buttons (Left Side) ---
        control_frame = ttk.Frame(self.action_bar_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create larger buttons (150% size increase)
        button_style = ttk.Style()
        button_style.configure('Large.TButton', padding=(15, 8))  # Increased padding for 150% size
        
        self.start_button = ttk.Button(
            control_frame, 
            text="🚀 Start New Hand", 
            style="Large.TButton", 
            command=self.start_new_hand
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.start_button, "Start a new poker hand")
        
        self.reset_button = ttk.Button(
            control_frame, 
            text="🔄 Reset Game", 
            style="Large.TButton",
            command=self._reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.reset_button, "Reset the entire game state")
        # --- END NEW ---

        # --- Action Buttons (Center) ---
        action_frame = ttk.Frame(self.action_bar_frame)
        action_frame.pack(side=tk.LEFT, padx=10)
        
        # Configure large button style for action buttons
        button_style.configure('LargeAction.TButton', padding=(12, 6))
        
        self.human_action_controls['fold'] = ttk.Button(
            action_frame, 
            text="Fold", 
            style="LargeAction.TButton", 
            command=lambda: self._submit_human_action("fold")
        )
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['fold'], "Fold your hand and exit the current round")

        self.human_action_controls['check'] = ttk.Button(
            action_frame, 
            text="Check", 
            style="LargeAction.TButton",
            command=lambda: self._submit_human_action("check")
        )
        self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['check'], "Check (pass) if no bet to call")
        
        self.human_action_controls['call'] = ttk.Button(
            action_frame, 
            text="Call", 
            style="LargeAction.TButton",
            command=lambda: self._submit_human_action("call")
        )
        self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['call'], "Call the current bet")

        # --- Bet Sizing Slider (Center-Right) ---
        self.sizing_frame = ttk.Frame(self.action_bar_frame)
        self.sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.bet_size_var = tk.DoubleVar()
        # Configure larger slider and label
        self.bet_slider = ttk.Scale(
            self.sizing_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.bet_size_var, 
            length=300  # Increased from 200 to 300 (150% size)
        )
        self.bet_slider.pack(fill=tk.X)
        self.bet_slider.bind("<B1-Motion>", self._update_bet_size_label)
        
        # Use larger font for bet size label
        large_font = (THEME["font_family"], FONTS["main"][1] + 2)  # Increase font size by 2
        self.bet_size_label = ttk.Label(
            self.sizing_frame, 
            text="$0.00", 
            font=large_font
        )
        self.bet_size_label.pack()

        # --- Bet/Raise Button (Right) ---
        self.human_action_controls['bet_raise'] = ttk.Button(
            self.action_bar_frame, 
            text="Bet", 
            style="LargeAction.TButton", 
            command=self._submit_bet_raise
        )
        self.human_action_controls['bet_raise'].pack(side=tk.RIGHT, padx=5)
        ToolTip(self.human_action_controls['bet_raise'], "Make a bet or raise")

        # Initially show only game control buttons
        self._show_game_control_buttons()

    def _show_game_control_buttons(self):
        """Shows only the game control buttons (Start/Reset)."""
        # Hide all action buttons
        for widget in self.human_action_controls.values():
            if hasattr(widget, 'pack_forget'):
                widget.pack_forget()
        
        # Show game control buttons
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Hide bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.pack_forget()
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.pack_forget()
        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack_forget()

    def _show_action_buttons(self):
        """Shows the action buttons and hides game control buttons."""
        # Hide game control buttons
        self.start_button.pack_forget()
        self.reset_button.pack_forget()
        
        # Show bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.pack(fill=tk.X)
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.pack()
        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def _reset_game(self):
        """Resets the game state and UI."""
        try:
            from tkinter import messagebox
            if messagebox.askyesno("Reset Game", "Are you sure you want to reset the game?"):
                self._log_message("🔄 Resetting game state...")
                
                # Reinitialize the state machine
                self.state_machine = ImprovedPokerStateMachine(
                    num_players=6, 
                    strategy_data=self.strategy_data
                )
                
                # Re-assign callbacks
                self.state_machine.on_action_required = self.prompt_human_action
                self.state_machine.on_hand_complete = self.handle_hand_complete
                self.state_machine.on_state_change = self.update_display
                self.state_machine.on_log_entry = self.add_game_message
                
                # Reset UI
                self._reset_ui_for_new_hand()
                self.add_game_message("🔄 Game has been reset!")
                self._log_message("✅ Game reset completed")
                self.update_session_info()
        except Exception as e:
            self._log_message(f"❌ Error resetting game: {e}")

    def _reset_ui_for_new_hand(self):
        """Resets the UI for a new hand."""
        # Clear game messages
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
        
        # Clear session info
        if hasattr(self, 'session_text'):
            self.session_text.config(state=tk.NORMAL)
            self.session_text.delete(1.0, tk.END)
            self.session_text.config(state=tk.DISABLED)
        
        # Reset pot display
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text="Pot: $0.00", fg="yellow")
        
        # FIX: Don't clear community cards immediately - let them stay visible during showdown
        # Community cards will be cleared when the next hand starts
        # for card_label in self.community_card_labels:
        #     card_label.config(text="")
        
        # NEW: Clear all action indicators for new hand
        for player_index, action_label in self.action_indicators.items():
            if action_label and action_label.winfo_exists():
                action_label.destroy()
        self.action_indicators.clear()
        self.last_action_player = None
        
        # Reset player displays
        for player_seat in self.player_seats:
            if player_seat:
                frame = player_seat.get("frame")
                if frame:
                    frame.config(bg=THEME["secondary_bg"])
                
                cards_label = player_seat.get("cards_label")
                if cards_label:
                    cards_label.config(text="")
                
                bet_label = player_seat.get("bet_label")
                if bet_label:
                    bet_label.config(text="")
                
                # Hide prominent bet displays
                bet_label_widget = player_seat.get("bet_label_widget")
                bet_label_window = player_seat.get("bet_label_window")
                if bet_label_widget and bet_label_window:
                    self.canvas.itemconfig(bet_label_window, state="hidden")
        
        # Show game control buttons
        self._show_game_control_buttons()
    
    def update_display(self, new_state=None):
        """Updates the UI and logs detailed debugging information."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            self._log_message("DEBUG: update_display called but no game_info available.")
            return

        # (Existing logging...)

        # Update pot and current bet display
        pot_text = f"Pot: ${game_info['pot']:.2f}"
        if game_info['current_bet'] > 0:
            pot_text += f"  |  Current Bet: ${game_info['current_bet']:.2f}"
        self.pot_label.config(text=pot_text)

        # --- THIS IS THE CRITICAL BUG FIX ---
        # Always display the community cards that are available on the board.
        for i, card_label in enumerate(self.community_card_labels):
            if i < len(game_info['board']):
                card_label.config(text=self._format_card(game_info['board'][i]))
            else:
                card_label.config(text="")
        # --- End of Bug Fix ---

        # NEW: Only clear action indicators when the next player actually takes an action
        # Don't clear just because highlighting changes - wait for actual action
        current_action_player = game_info['action_player']
        # We'll clear action indicators in _animate_player_action when a new action is taken
        
        # Update player info
        for i, player_seat in enumerate(self.player_seats):
            if not player_seat:
                continue

            player_info = game_info['players'][i]
            frame = player_seat["frame"]
            name_label = player_seat["name_label"]
            stack_label = player_seat["stack_label"]
            cards_label = player_seat["cards_label"]
            
            # FIXED: Highlight based on action_player index, not is_active status
            # Players should be highlighted when it's their turn, even if they fold
            if i == game_info['action_player']:
                frame.config(bg=THEME["accent_primary"])
            else:
                frame.config(bg=THEME["secondary_bg"])

            # Update name and position
            name_label.config(text=f"{player_info['name']} ({player_info['position']})")
            
            # Update stack and bet info
            stack_label.config(text=f"${player_info['stack']:.2f}")

            # Update the prominent bet display on the table
            bet_label_widget = player_seat.get("bet_label_widget")
            bet_label_window = player_seat.get("bet_label_window")
            if bet_label_widget and bet_label_window:
                current_bet = player_info.get("current_bet", 0.0)
                if current_bet > 0 and player_info['is_active']:
                    bet_label_widget.config(text=f"💰 ${current_bet:.2f}")
                    self.canvas.itemconfig(bet_label_window, state="normal")
                else:
                    self.canvas.itemconfig(bet_label_window, state="hidden")

            # Update player card display
            if player_info['is_active']:
                # Show cards only if the player is human or if it's showdown
                if player_info['is_human'] or self.state_machine.get_current_state() == PokerState.SHOWDOWN:
                    cards_text = " ".join(self._format_card(c) for c in player_info['cards'])
                    cards_label.config(text=cards_text)
                else: # Bot's cards are hidden during play
                    cards_label.config(text="🂠 🂠")
            else: # Player has folded
                cards_label.config(text="Folded")
        
        # Update session information display
        self.update_session_info()
    
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
    
    def _animate_player_action(self, player_index: int, action: str, amount: float = 0):
        """Animate a player's action with visual feedback that persists until next player acts."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        frame = player_seat.get("frame")
        name_label = player_seat.get("name_label")
        
        if not frame or not name_label:
            return
            
        # Clear any existing action indicator for this player
        if player_index in self.action_indicators:
            old_label = self.action_indicators[player_index]
            if old_label and old_label.winfo_exists():
                old_label.destroy()
        
        # Clear the previous player's action indicator when a new action is taken
        if (self.last_action_player is not None and 
            self.last_action_player != player_index and
            self.last_action_player in self.action_indicators):
            # Clear the previous player's action indicator
            old_label = self.action_indicators[self.last_action_player]
            if old_label and old_label.winfo_exists():
                old_label.destroy()
                del self.action_indicators[self.last_action_player]
        
        # Create action indicator
        action_text = action.upper()
        if amount > 0:
            action_text += f" ${amount:.2f}"
        elif action.upper() == "CHECK":
            action_text = "CHECK"  # Keep it simple for check
            
        # Create persistent action label (doesn't fade out)
        action_label = tk.Label(
            frame,
            text=action_text,
            bg=THEME["accent_secondary"],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2
        )
        action_label.pack(side=tk.TOP, pady=2)
        
        # Force the label to be visible and properly configured
        action_label.lift()  # Bring to front
        action_label.update()  # Force update
        action_label.config(state="normal")  # Ensure it's enabled
        frame.update()  # Update the parent frame
        
        # Force a complete UI refresh
        self.canvas.update()
        self.update()
        
        # Store the action indicator for this player
        self.action_indicators[player_index] = action_label
        self.last_action_player = player_index
        
        # Also update the player's display immediately
        if action.upper() == "FOLD":
            # Show "Folded" status immediately
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text="Folded", fg="red")
        elif action.upper() == "CHECK":
            # Show check text
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text="Check", fg="green")
        elif action.upper() in ["CALL", "BET", "RAISE"]:
            # Show bet amount
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text=f"${amount:.2f}", fg="blue")
    
    def _format_card(self, card_str: str) -> str:
        """Formats a card string for display."""
        if not card_str or card_str == "**":
            return "🂠"
        
        rank = card_str[0]
        suit = card_str[1]
        
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_symbol = suit_symbols.get(suit, suit)
        
        return f"{rank}{suit_symbol}"

    def update_font_size(self, font_size: int):
        """Updates the font size for all components in the practice session."""
        # Create font configurations for different component types
        main_font = (THEME["font_family"], font_size)
        small_font = (THEME["font_family"], max(font_size - 2, 8))  # Ensure minimum size
        large_font = (THEME["font_family"], font_size + 2)
        bold_font = (THEME["font_family"], font_size, "bold")
        
        # Update session information text area
        if hasattr(self, 'session_text'):
            self.session_text.config(font=main_font)
        
        # Update action messages text area
        if hasattr(self, 'info_text'):
            self.info_text.config(font=main_font)
        
        # Update scrollbars to match the new font size
        if hasattr(self, 'session_scrollbar'):
            # Scrollbar size can be adjusted if needed
            pass
        if hasattr(self, 'action_scrollbar'):
            # Scrollbar size can be adjusted if needed
            pass
        
        # Update player seat labels and information
        for player_seat in self.player_seats:
            if player_seat:
                frame = player_seat.get("frame")
                if frame:
                    # Update player name label
                    name_label = player_seat.get("name_label")
                    if name_label:
                        name_label.config(font=bold_font)
                    
                    # Update position label
                    position_label = player_seat.get("position_label")
                    if position_label:
                        position_label.config(font=small_font)
                    
                    # Update cards label
                    cards_label = player_seat.get("cards_label")
                    if cards_label:
                        cards_label.config(font=main_font)
                    
                    # Update bet label
                    bet_label = player_seat.get("bet_label")
                    if bet_label:
                        bet_label.config(font=main_font)
                
                # Update stack graphics
                stack_graphics = player_seat.get("stack_graphics")
                if stack_graphics:
                    amount_label = stack_graphics.get("amount_label")
                    if amount_label:
                        amount_label.config(font=main_font)
                    
                    chips_label = stack_graphics.get("chips_label")
                    if chips_label:
                        chips_label.config(font=small_font)
        
        # Update community card labels
        for card_label in self.community_card_labels:
            if card_label:
                card_label.config(font=large_font)
        
        # Update pot display
        if hasattr(self, 'pot_label'):
            self.pot_label.config(font=large_font)
        
        # Update action buttons
        for control_name, control_dict in self.human_action_controls.items():
            if isinstance(control_dict, dict):
                button = control_dict.get("button")
                if button:
                    button.config(font=main_font)
        
        # Update bet size entry and label
        if hasattr(self, 'bet_size_entry'):
            self.bet_size_entry.config(font=main_font)
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.config(font=main_font)
        
        # Update game control buttons
        if hasattr(self, 'start_hand_btn'):
            self.start_hand_btn.config(font=main_font)
        if hasattr(self, 'reset_game_btn'):
            self.reset_game_btn.config(font=main_font)
        
        # Force a complete UI refresh
        self.update()
    
    def increase_table_size(self):
        """Increase the table size by adjusting column weights."""
        # Get current weights
        current_table_weight = self.grid_columnconfigure(0)['weight']
        current_message_weight = self.grid_columnconfigure(1)['weight']
        
        # Increase table weight (make it larger)
        new_table_weight = min(current_table_weight + 1, 8)  # Cap at 8
        new_message_weight = max(current_message_weight - 0.5, 0.5)  # Don't go below 0.5
        
        # Update column weights
        self.grid_columnconfigure(0, weight=new_table_weight)
        self.grid_columnconfigure(1, weight=new_message_weight)
        
        # Force a complete redraw
        self._on_resize()
        
        # Update session info to reflect the change
        self.update_session_info()
    
    def decrease_table_size(self):
        """Decrease the table size by adjusting column weights."""
        # Get current weights
        current_table_weight = self.grid_columnconfigure(0)['weight']
        current_message_weight = self.grid_columnconfigure(1)['weight']
        
        # Decrease table weight (make it smaller)
        new_table_weight = max(current_table_weight - 1, 3)  # Don't go below 3
        new_message_weight = min(current_message_weight + 0.5, 2)  # Cap at 2
        
        # Update column weights
        self.grid_columnconfigure(0, weight=new_table_weight)
        self.grid_columnconfigure(1, weight=new_message_weight)
        
        # Force a complete redraw
        self._on_resize()
        
        # Update session info to reflect the change
        self.update_session_info()
    
    def get_table_size_info(self):
        """Get current table size information for display."""
        table_weight = self.grid_columnconfigure(0)['weight']
        message_weight = self.grid_columnconfigure(1)['weight']
        
        # Calculate relative sizes
        total_weight = table_weight + message_weight
        table_percentage = (table_weight / total_weight) * 100
        message_percentage = (message_weight / total_weight) * 100
        
        return {
            'table_weight': table_weight,
            'message_weight': message_weight,
            'table_percentage': table_percentage,
            'message_percentage': message_percentage
        }
    
    def change_table_felt(self, felt_color):
        """Change the table felt color and redraw immediately."""
        if felt_color in self.table_felt_colors:
            self.current_felt_color = felt_color
            # Force a complete redraw to apply the new felt color
            self._on_resize()
            # Update session info to reflect the change
            self.update_session_info()
        else:
            print(f"Warning: Unknown felt color '{felt_color}'")
    
    def update_stack_amount(self, player_index, new_amount):
        """Update the stack amount for a specific player."""
        if player_index < len(self.player_seats):
            player_seat = self.player_seats[player_index]
            if player_seat and "stack_graphics" in player_seat:
                stack_graphics = player_seat["stack_graphics"]
                amount_label = stack_graphics.get("amount_label")
                chips_label = stack_graphics.get("chips_label")
                
                if amount_label:
                    amount_label.config(text=f"${new_amount:.2f}")
                
                if chips_label:
                    # Create visual chip representation based on amount
                    chip_count = self._calculate_chip_count(new_amount)
                    chip_symbols = self._get_chip_symbols(new_amount)
                    chips_label.config(text=chip_symbols)
    
    def _calculate_chip_count(self, amount):
        """Calculate how many chip symbols to display based on amount."""
        if amount <= 10:
            return 1
        elif amount <= 50:
            return 2
        elif amount <= 100:
            return 3
        elif amount <= 200:
            return 4
        else:
            return 5
    
    def _get_chip_symbols(self, amount):
        """Get appropriate chip symbols based on amount."""
        chip_count = self._calculate_chip_count(amount)
        
        # Different chip colors based on amount ranges
        if amount <= 25:
            return "🟡" * chip_count  # Yellow chips for small amounts
        elif amount <= 100:
            return "🟢" * chip_count  # Green chips for medium amounts
        elif amount <= 500:
            return "🔴" * chip_count  # Red chips for larger amounts
        else:
            return "🟣" * chip_count  # Purple chips for very large amounts