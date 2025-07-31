#!/usr/bin/env python3
"""
Enhanced Visual Poker Table with Perfect Centering

A professional poker table with perfect centering, improved layout,
and state-of-the-art visual design based on professional poker applications.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading
import time
import random

from enhanced_poker_engine import (
    EnhancedPokerEngine,
    Player,
    GameState,
    Action,
    Position,
)
from gui_models import StrategyData


class ProfessionalPokerTable:
    """Professional poker table with perfect centering and realistic game flow."""

    def __init__(self, parent_frame, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.engine = EnhancedPokerEngine(strategy_data)
        self.current_game_state = None

        # MUCH LARGER table - 80% of pane
        self.canvas_width = 1600  # Increased from 1200
        self.canvas_height = 1000  # Increased from 800
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # Professional table ratios - 80% of canvas
        self.table_width = int(self.canvas_width * 0.80)  # 80% of canvas width
        self.table_height = int(self.canvas_height * 0.80)  # 80% of canvas height
        self.player_radius = (
            min(self.table_width, self.table_height) * 0.35
        )  # 35% to ensure 10% margin within table

        # Card dimensions - smaller for better fit
        self.card_width = 60  # Smaller cards
        self.card_height = 85  # Smaller cards

        # Game state tracking
        self.current_hand_phase = "preflop"  # preflop, flop, turn, river
        self.current_action_player = 0  # Index of player whose turn it is
        self.dealer_position = 0  # Dealer position
        self.small_blind_position = 1  # Small blind position
        self.big_blind_position = 2  # Big blind position
        self.hand_started = False
        self.community_cards_dealt = 0  # 0=preflop, 3=flop, 4=turn, 5=river

        # Action log and sound effects
        self.action_log = []
        self.bot_action_delay = 1.5  # Seconds between bot actions
        self.action_sound_delay = 0.5  # Delay for sound effects

        # Create controls first (they will contain the canvas)
        self._create_professional_controls(parent_frame)

        # Create canvas in the right frame
        self.canvas = tk.Canvas(
            self.table_frame,  # Use table_frame instead of parent_frame
            width=self.canvas_width,
            height=self.canvas_height,
            bg="SystemButtonFace",  # Use system default background
            highlightthickness=0,
        )
        self.canvas.pack(
            fill=tk.BOTH, expand=True, padx=0, pady=0
        )  # No padding for perfect centering

        # Draw table
        self._draw_professional_table()

    def _create_professional_controls(self, parent_frame):
        """Create professional game controls."""
        # Create main container frame
        main_container = ttk.Frame(parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Action log frame - LEFT SIDE (FIXED WIDTH, NO EXPAND)
        log_frame = ttk.Frame(main_container)
        log_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Action log label
        ttk.Label(log_frame, text="Action Log:", font=("Arial", 14, "bold")).pack(
            anchor=tk.W
        )

        # Action log text area - FIXED WIDTH with scrollbar
        self.action_log_text = tk.Text(
            log_frame,
            width=50,  # Fixed width, never changes
            height=25,  # Much taller
            font=("Arial", 14),  # Default font size
            bg="SystemButtonFace",  # Match app background
            fg="black",
            relief="sunken",
            bd=2,
            wrap=tk.NONE,  # No word wrapping to enable horizontal scroll
        )

        # Add scrollbars
        log_scrollbar_v = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.action_log_text.yview
        )
        log_scrollbar_h = ttk.Scrollbar(
            log_frame, orient=tk.HORIZONTAL, command=self.action_log_text.xview
        )
        self.action_log_text.configure(
            yscrollcommand=log_scrollbar_v.set, xscrollcommand=log_scrollbar_h.set
        )

        # Pack with scrollbars
        log_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        log_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.action_log_text.pack(fill=tk.BOTH, expand=True)

        # Table frame - RIGHT SIDE (for canvas and controls)
        self.table_frame = ttk.Frame(main_container)
        self.table_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # Bottom action controls - INSIDE TABLE FRAME
        action_frame = ttk.Frame(self.table_frame)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        # Center the action controls
        center_frame = ttk.Frame(action_frame)
        center_frame.pack(expand=True)

        # Center the action controls
        center_frame = ttk.Frame(action_frame)
        center_frame.pack(expand=True)

        # Player count dropdown - same size as action buttons
        self.player_count_var = tk.StringVar(value="6")
        player_count_frame = ttk.Frame(center_frame)
        player_count_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(player_count_frame, text="Players:", font=("Arial", 14, "bold")).pack(
            side=tk.LEFT, padx=2
        )
        player_combo = ttk.Combobox(
            player_count_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly",
            width=5,
            font=("Arial", 14),
        )
        player_combo.pack(side=tk.LEFT, padx=2)

        # Professional start button - same size as action buttons
        start_button = tk.Button(
            center_frame,
            text="🎯 Start Hand",
            command=self._start_professional_hand,
            bg="#CCCCCC",  # Gray background
            fg="black",  # Black font
            font=("Arial", 16, "bold"),
            relief="raised",
            bd=4,
            width=12,  # Same width as action buttons
            height=2,  # Same height as action buttons
        )
        start_button.pack(side=tk.LEFT, padx=5)

        # Turn info will be displayed in action log instead of separate button

        # Action buttons with clear labels - ALL CONSISTENT SIZE
        self.action_var = tk.StringVar(value="check")
        self.action_buttons = {}  # Store button references
        actions = [
            ("FOLD", "fold", True),  # Immediate action
            ("CHECK", "check", True),  # Immediate action
            ("CALL", "call", True),  # Immediate action
            ("BET", "bet", False),  # Requires submit
            ("RAISE", "raise", False),  # Requires submit
        ]

        for text, value, immediate in actions:
            if immediate:
                # Immediate action buttons with 3D effect
                btn = tk.Button(
                    center_frame,
                    text=text,
                    command=lambda v=value: self._execute_immediate_action(v),
                    bg="#E8E8E8",  # Light gray background
                    fg="black",  # Black font
                    font=("Arial", 16, "bold"),  # Consistent font
                    relief="raised",
                    bd=3,  # 3D border effect
                    width=12,  # ALL CONSISTENT SIZE
                    height=2,  # ALL CONSISTENT SIZE
                    activebackground="#4CAF50",  # Green when pressed
                    activeforeground="white",  # White text when pressed
                )
            else:
                # Action buttons that require submit with 3D effect
                btn = tk.Button(
                    center_frame,
                    text=text,
                    command=lambda v=value: self._set_action(v),
                    bg="#E8E8E8",  # Light gray background
                    fg="black",  # Black font
                    font=("Arial", 16, "bold"),  # Consistent font
                    relief="raised",
                    bd=3,  # 3D border effect
                    width=12,  # ALL CONSISTENT SIZE
                    height=2,  # ALL CONSISTENT SIZE
                    activebackground="#FF9800",  # Orange when pressed
                    activeforeground="white",  # White text when pressed
                )
            self.action_buttons[value] = btn  # Store reference
            btn.pack(side=tk.LEFT, padx=5)  # Consistent spacing

        # Bet input - next to action buttons
        bet_frame = ttk.Frame(center_frame)
        bet_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(bet_frame, text="Bet:", font=("Arial", 14, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        self.bet_size_var = tk.StringVar(value="0")
        bet_entry = ttk.Entry(
            bet_frame, textvariable=self.bet_size_var, width=8, font=("Arial", 14)
        )
        bet_entry.pack(side=tk.LEFT, padx=5)

        # Professional submit button - MORE PROMINENT
        self.submit_button = tk.Button(
            center_frame,
            text="SUBMIT",
            command=self._submit_professional_action,
            bg="#4CAF50",  # Green background to make it stand out
            fg="black",  # Black font for better readability
            font=("Arial", 16, "bold"),
            relief="raised",
            bd=4,
            width=12,  # Consistent size
            height=2,  # Consistent size
        )
        self.submit_button.pack(side=tk.LEFT, padx=5)

    def update_font_size(self, font_size: int):
        """Update the action log font size to match the app's font size."""
        # Update action log font size only - width stays fixed
        self.action_log_text.configure(font=("Arial", font_size))

    def _execute_immediate_action(self, action):
        """Execute an action immediately (FOLD, CHECK, CALL)."""
        if not self.current_game_state:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return

        try:
            # Execute action for current player
            current_player = self.current_game_state.players[self.current_action_player]

            # Execute the action
            self._execute_action(current_player, action, 0)

            # Log the action (sound will be played by _log_action)
            self._log_action(current_player.name, action.upper(), 0)

            # Move to next player
            self._advance_to_next_player()

            # Check if round is complete
            if self._is_round_complete():
                # Check for all-fold scenario first
                if not self._handle_all_fold_scenario():
                    self._advance_to_next_street()

            # Redraw table
            self._redraw_professional_table()

            # Update turn indicator
            self._update_turn_indicator()

            # Start bot actions if next player is bot
            if self.current_game_state:
                next_player = self.current_game_state.players[
                    self.current_action_player
                ]
                if not next_player.is_human:
                    threading.Timer(self.bot_action_delay, self._bot_action).start()

            # Show professional feedback
            self._show_professional_feedback(action, 0)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute action: {str(e)}")

    def _set_action(self, action):
        """Set the selected action (for BET/RAISE that require submit)."""
        self.action_var.set(action)
        print(f"Action selected: {action}")  # Debug info
        # Log the selected action
        self._log_action("SYSTEM", f"Action selected: {action.upper()}", 0, play_sound=False)
        # Make submit button more prominent when action is selected
        self.submit_button.config(bg="#FF6B35", text="SUBMIT NOW!")  # Orange background

    def _activate_buttons_for_human_turn(self):
        """Activate buttons when it's the human player's turn."""
        for btn in self.action_buttons.values():
            btn.config(state=tk.NORMAL, bg="#4CAF50", fg="white")  # Green when active
        # Log turn info to action log
        self._log_action("SYSTEM", "YOUR TURN - Action buttons activated", 0, play_sound=False)
        # Play special sound for human turn
        self._play_sound_effect("your_turn")

    def _deactivate_buttons_for_bot_turn(self):
        """Deactivate buttons when it's a bot player's turn."""
        for btn in self.action_buttons.values():
            btn.config(state=tk.DISABLED, bg="#E0E0E0", fg="gray")  # Gray when disabled
        # Log turn info to action log
        self._log_action("SYSTEM", "BOT TURN - Action buttons deactivated", 0, play_sound=False)

    def _log_action(
        self, player_name: str, action: str, amount: float = 0, play_sound: bool = True
    ):
        """Log an action to the action log."""
        timestamp = time.strftime("%H:%M:%S")
        if amount > 0:
            log_entry = f"[{timestamp}] {player_name}: {action} ${amount:.2f}\n"
        else:
            log_entry = f"[{timestamp}] {player_name}: {action}\n"

        self.action_log.append(log_entry)
        self.action_log_text.insert(tk.END, log_entry)
        self.action_log_text.see(tk.END)  # Auto-scroll to bottom

        # Play sound effect only for actual player actions, not system messages
        if play_sound and player_name not in ["DEALER", "SYSTEM"]:
            self._play_sound_effect(action)

    def _play_sound_effect(self, action: str):
        """Play professional poker sound effects based on major poker apps."""
        try:
            import winsound

            # Windows sound effects - Professional poker app style
            sound_effects = {
                # Player actions (like PokerStars)
                "fold": "SystemHand",  # Soft, quick sound
                "check": "SystemQuestion",  # Gentle notification
                "call": "SystemExclamation",  # Medium notification
                "bet": "SystemAsterisk",  # Attention sound
                "raise": "SystemAsterisk",  # Same as bet
                "all_in": "SystemExclamation",  # Dramatic sound
                # Game events (like 888 Poker)
                "deal": "SystemStart",  # Card dealing sound
                "shuffle": "SystemStart",  # Shuffle sound
                "your_turn": "SystemQuestion",  # Turn notification
                "hand_start": "SystemStart",  # Hand beginning
                "street_change": "SystemExclamation",  # Street change
                "showdown": "SystemAsterisk",  # Showdown sound
                "winner": "SystemExclamation",  # Winner announcement
                "chips": "SystemAsterisk",  # Chip movement
            }
            winsound.PlaySound(
                sound_effects.get(action.lower(), "SystemAsterisk"), winsound.SND_ALIAS
            )
        except ImportError:
            try:
                import os

                # macOS/Linux sound effects - Professional poker app style
                sound_effects = {
                    # Player actions (like PokerStars)
                    "fold": "afplay /System/Library/Sounds/Tink.aiff",  # Soft fold
                    "check": "afplay /System/Library/Sounds/Tink.aiff",  # Gentle check
                    "call": "afplay /System/Library/Sounds/Glass.aiff",  # Medium call
                    "bet": "afplay /System/Library/Sounds/Glass.aiff",  # Attention bet
                    "raise": "afplay /System/Library/Sounds/Glass.aiff",  # Same as bet
                    "all_in": "afplay /System/Library/Sounds/Glass.aiff",  # Dramatic
                    # Game events (like 888 Poker)
                    "deal": "afplay /System/Library/Sounds/Pop.aiff",  # Card dealing
                    "shuffle": "afplay /System/Library/Sounds/Pop.aiff",  # Shuffle
                    "your_turn": "afplay /System/Library/Sounds/Glass.aiff",  # Turn
                    "hand_start": "afplay /System/Library/Sounds/Pop.aiff",  # Start
                    "street_change": "afplay /System/Library/Sounds/Glass.aiff",  # Street
                    "showdown": "afplay /System/Library/Sounds/Glass.aiff",  # Showdown
                    "winner": "afplay /System/Library/Sounds/Glass.aiff",  # Winner
                    "chips": "afplay /System/Library/Sounds/Tink.aiff",  # Chips
                }
                os.system(
                    sound_effects.get(
                        action.lower(), "afplay /System/Library/Sounds/Tink.aiff"
                    )
                )
            except:
                # Fallback to console output with emoji indicators
                sound_effects = {
                    # Player actions
                    "fold": "🔇 Fold (soft)",
                    "check": "🔊 Check (gentle)",
                    "call": "💰 Call (medium)",
                    "bet": "💰 Bet (attention)",
                    "raise": "💰 Raise (attention)",
                    "all_in": "🎰 All-in (dramatic)",
                    # Game events
                    "deal": "🃏 Deal cards",
                    "shuffle": "🔀 Shuffle deck",
                    "your_turn": "🔔 Your turn",
                    "hand_start": "🎮 Hand start",
                    "street_change": "🔄 Street change",
                    "showdown": "⚡ Showdown",
                    "winner": "🏆 Winner",
                    "chips": "🪙 Chips",
                }
                effect = sound_effects.get(action.lower(), f"🔊 {action}")
                print(f"{effect}")

    def _bot_action(self):
        """Simulate bot player action with realistic timing and sound effects."""
        if not self.current_game_state:
            return

        current_player = self.current_game_state.players[self.current_action_player]
        if current_player.is_human:
            return  # Not a bot player

        # Simulate bot thinking time
        time.sleep(self.bot_action_delay)

        # Bot decision logic with realistic actions (less aggressive folding)
        if self.current_game_state.current_bet == 0:
            # No bet to call - more likely to check or bet
            actions = ["check", "check", "check", "bet"]  # 75% check, 25% bet
        else:
            # There's a bet to call - more realistic distribution
            actions = [
                "fold",
                "fold",
                "call",
                "call",
                "call",
                "raise",
            ]  # 33% fold, 50% call, 17% raise

        action = random.choice(actions)
        bet_size = 0
        if action in ["bet", "raise"]:
            bet_size = random.randint(
                1, min(10, int(self.current_game_state.current_bet * 2))
            )
        elif action == "call":
            bet_size = self.current_game_state.current_bet

        # Execute bot action
        self._execute_action(current_player, action, bet_size)

        # Log bot action (sound will be played by _log_action)
        self._log_action(current_player.name, action.upper(), bet_size)

        # Move to next player
        self._advance_to_next_player()

        # Redraw table
        self._redraw_professional_table()
        self._update_turn_indicator()

        # Schedule next bot action if needed
        if self.current_game_state:
            next_player = self.current_game_state.players[self.current_action_player]
            if not next_player.is_human:
                threading.Timer(self.bot_action_delay, self._bot_action).start()

    def _execute_action(self, player: Player, action: str, bet_size: float = 0):
        """Execute an action for a player."""
        if action == "fold":
            player.is_active = False
            player.current_bet = 0
        elif action in ["call", "bet", "raise"]:
            # Update pot and stacks
            call_amount = self.current_game_state.current_bet
            if action == "bet":
                call_amount = bet_size
            elif action == "raise":
                call_amount = bet_size

            player.stack -= call_amount
            self.current_game_state.pot += call_amount
            self.current_game_state.current_bet = call_amount
            player.current_bet = call_amount
        elif action == "check":
            player.current_bet = 0

        # Note: Sound effects are handled by _log_action to avoid duplicates

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

        # Draw professional felt pattern with poker suit symbols
        suit_symbols = ["♠", "♥", "♦", "♣"]
        pattern_spacing = 40  # Larger spacing for better visibility

        for i in range(0, self.table_width, pattern_spacing):
            for j in range(0, self.table_height, pattern_spacing):
                pattern_x = table_x + i
                pattern_y = table_y + j

                # Check if pattern is within the table area
                if (pattern_x - self.center_x) ** 2 + (
                    pattern_y - self.center_y
                ) ** 2 < (self.player_radius - 50) ** 2:
                    # Alternate suit symbols for variety
                    suit_index = (i + j) // pattern_spacing % len(suit_symbols)
                    suit_symbol = suit_symbols[suit_index]

                    # Use darker green for subtle pattern
                    self.canvas.create_text(
                        pattern_x,
                        pattern_y,
                        text=suit_symbol,
                        font=("Arial", 12),
                        fill="#1B4D2E",  # Darker green for subtle pattern
                    )

        # Draw professional pot area - PERFECTLY CENTERED
        pot_radius = 45  # Larger pot
        self.canvas.create_oval(
            self.center_x - pot_radius,
            self.center_y - pot_radius,  # FIXED: Use center_y for perfect centering
            self.center_x + pot_radius,
            self.center_y + pot_radius,  # FIXED: Use center_y for perfect centering
            fill="#FFD700",  # Gold pot
            outline="#B8860B",  # Dark gold border
            width=3,
        )

        # Pot text with black font
        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="POT",
            font=("Arial", 16, "bold"),
            fill="black",
        )

        # Draw professional dealer button
        dealer_radius = 22  # Larger dealer button
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
            font=("Arial", 16, "bold"),
            fill="black",
        )

    def _get_player_position(
        self, player_index: int, total_players: int
    ) -> tuple[int, int]:
        """Calculate perfect player position around the table."""
        # Start from bottom (south) and go clockwise
        angle = (player_index * 2 * math.pi / total_players) - math.pi / 2
        x = self.center_x + int(self.player_radius * math.cos(angle))
        y = self.center_y + int(self.player_radius * math.sin(angle))
        return x, y

    def _draw_professional_player(
        self, player: Player, position: tuple[int, int], is_current_player: bool = False
    ):
        """Draw a professional player with perfect positioning."""
        x, y = position

        # Professional player circle
        if player.is_human:
            color = "#F4A460"  # Human skin color for human player
        elif not player.is_active:
            color = "#95A5A6"  # Gray for folded players
        else:
            color = "#C0C0C0"  # Silver titanium for AI players

        player_radius = 50  # MUCH BIGGER player radius

        # Highlight current player's turn
        if is_current_player:
            # Draw highlight ring
            self.canvas.create_oval(
                x - player_radius - 8,
                y - player_radius - 8,
                x + player_radius + 8,
                y + player_radius + 8,
                fill="",
                outline="#FFD700",  # Gold highlight
                width=4,
            )
        self.canvas.create_oval(
            x - player_radius,
            y - player_radius,
            x + player_radius,
            y + player_radius,
            fill=color,
            outline="black",
            width=3,
        )

        # Professional player name - MUCH BIGGER with 10% margin
        name = "You" if player.is_human else f"P{player.name.split()[-1]}"
        text_color = (
            "#000080" if player.is_human else "black"
        )  # Deep ocean blue for human, black for bots

        # Calculate 10% margin from circle edge
        margin = int(player_radius * 0.1)
        text_radius = player_radius - margin

        # Player name - positioned within 10% margin
        self.canvas.create_text(
            x,
            y - text_radius * 0.6,
            text=name,
            font=("Arial", 16, "bold"),
            fill=text_color,
        )

        # Professional position indicator - within 10% margin
        self.canvas.create_text(
            x,
            y + text_radius * 0.1,
            text=player.position.value,
            font=("Arial", 14, "bold"),
            fill=text_color,
        )

        # Professional stack size - within 10% margin
        self.canvas.create_text(
            x,
            y + text_radius * 0.6,
            text=f"${player.stack:.0f}",
            font=("Arial", 14, "bold"),
            fill=text_color,
        )

        # Betting amount - below player circle
        if hasattr(player, "current_bet") and player.current_bet > 0:
            bet_text = f"Bet: ${player.current_bet:.0f}"
            self.canvas.create_text(
                x,
                y + player_radius + 25,
                text=bet_text,
                font=("Arial", 12, "bold"),
                fill="red",
            )

        # Draw professional hole cards - only show human cards or folded players
        if player.cards and (player.is_human or not player.is_active):
            self._draw_professional_hole_cards(player, position)

    def _draw_professional_hole_cards(self, player: Player, position: tuple[int, int]):
        """Draw professional hole cards with perfect spacing and card mucking."""
        x, y = position

        # Position cards below player with professional spacing
        card_y = y + 100  # Further below player

        # Calculate proper spacing to show both cards fully
        gap = 8  # 0.1 cm equivalent gap (approximately 8 pixels)
        total_card_width = self.card_width + gap

        # Center the two cards around the player position
        first_card_x = x - (total_card_width + self.card_width) // 2

        for i, card in enumerate(player.cards):
            card_x = first_card_x + (i * total_card_width)

            # Determine card appearance based on player status
            if player.is_human:
                # Human player - always show cards
                card_color = "#F5F5F5"  # Very light gray
                show_card_text = True
            elif not player.is_active:
                # Folded player - show mucked cards (face down with "MUCKED" text)
                card_color = "#2C3E50"  # Dark gray for mucked cards
                show_card_text = False
            else:
                # Active bot player - show face down cards
                card_color = "#F5F5F5"  # Very light gray
                show_card_text = False

            # Draw card background
            self.canvas.create_rectangle(
                card_x,
                card_y,
                card_x + self.card_width,
                card_y + self.card_height,
                fill=card_color,
                outline="black",
                width=3,  # Thicker border
            )

            if show_card_text:
                # Show card text for human player
                rank, suit = card[0], card[1]
                suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
                color = "red" if suit in ["h", "d"] else "black"

                # Calculate font size as 60% of card height
                font_size = int(self.card_height * 0.6)

                self.canvas.create_text(
                    card_x + self.card_width // 2,
                    card_y + self.card_height // 2,
                    text=f"{rank}{suit_symbol}",
                    font=("Arial", font_size, "bold"),
                    fill=color,
                )
            elif not player.is_active:
                # Show "MUCKED" text for folded players
                self.canvas.create_text(
                    card_x + self.card_width // 2,
                    card_y + self.card_height // 2,
                    text="MUCKED",
                    font=("Arial", 10, "bold"),
                    fill="white",
                )
            else:
                # Show "XX" for active bot players (face down)
                self.canvas.create_text(
                    card_x + self.card_width // 2,
                    card_y + self.card_height // 2,
                    text="XX",
                    font=("Arial", 12, "bold"),
                    fill="gray",
                )

    def _draw_professional_community_cards(self):
        """Draw professional community cards with perfect centering."""
        if not self.current_game_state:
            return

        # Only show community cards as they're dealt
        cards_to_show = self.current_game_state.board[: self.community_cards_dealt]
        if not cards_to_show:
            return

        # Professional card spacing and positioning
        card_spacing = 80  # Increased spacing for larger cards
        start_x = self.center_x - (len(cards_to_show) * card_spacing // 2)

        for i, card in enumerate(cards_to_show):
            card_x = start_x + (i * card_spacing)
            card_y = self.center_y + 60  # Positioned well below pot info

            # Professional card background - SAME AS HOLE CARDS
            self.canvas.create_rectangle(
                card_x,
                card_y,
                card_x + self.card_width,
                card_y + self.card_height,
                fill="#F5F5F5",  # Very light gray background
                outline="black",
                width=3,  # Thicker border like hole cards
            )

            # Professional card text - SAME SIZE AS HOLE CARDS
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            color = "red" if suit in ["h", "d"] else "black"

            # Calculate font size as 60% of card height (same as hole cards)
            font_size = int(self.card_height * 0.6)

            self.canvas.create_text(
                card_x + self.card_width // 2,
                card_y + self.card_height // 2,
                text=f"{rank}{suit_symbol}",
                font=("Arial", font_size, "bold"),  # Same size as hole cards
                fill=color,
            )

    def _draw_professional_pot_info(self):
        """Draw professional pot information."""
        if not self.current_game_state:
            return

        # Professional pot amount - POSITIONED ABOVE COMMUNITY CARDS
        self.canvas.create_text(
            self.center_x,
            self.center_y - 60,  # Higher position, above community cards
            text=f"${self.current_game_state.pot:.0f}",
            font=("Arial", 20, "bold"),  # MUCH BIGGER font
            fill="black",
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
            positions = [
                Position.UTG,
                Position.MP,
                Position.CO,
                Position.BTN,
                Position.SB,
                Position.BB,
            ]

            for i in range(num_players):
                is_human = i == 0  # First player is human
                position = positions[i % len(positions)]
                player = Player(
                    name=f"Player {i+1}",
                    stack=100.0,
                    position=position,
                    is_human=is_human,
                    is_active=True,
                    cards=[],  # Cards will be dealt by dealer
                )
                # Add current_bet attribute
                player.current_bet = 0.0
                players.append(player)

            # Dealer deals hole cards (but don't show AI cards yet)
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
                street="preflop",
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

            # Play hand start sound
            self._play_sound_effect("hand_start")

            # Log hand start
            self._log_action("DEALER", "Hand Started", 0, play_sound=False)

            # Start bot actions if first player is bot
            if self.current_game_state:
                first_player = self.current_game_state.players[
                    self.current_action_player
                ]
                if not first_player.is_human:
                    threading.Timer(self.bot_action_delay, self._bot_action).start()

            # Log detailed hand start info instead of popup
            self._log_action(
                "SYSTEM",
                f"New hand started with {num_players} players!",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                f"Dealer: {self.current_game_state.players[self.dealer_position].name}",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                f"Your position: {self.current_game_state.players[0].position.value}",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                f"Action starts with: {self.current_game_state.players[self.current_action_player].name}",
                0,
                play_sound=False,
            )
            # Add helpful instructions
            self._log_action(
                "SYSTEM",
                "INSTRUCTIONS: FOLD, CHECK, CALL execute immediately. BET/RAISE require SUBMIT!",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                "TIP: For betting actions, enter amount and click SUBMIT!",
                0,
                play_sound=False,
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start hand: {str(e)}")

    def _create_deck(self):
        """Create a standard 52-card deck."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        suits = ["h", "d", "c", "s"]
        deck = []
        for rank in ranks:
            for suit in suits:
                deck.append(f"{rank}{suit}")
        return deck

    def _update_turn_indicator(self):
        """Update button states based on whose turn it is."""
        if not self.current_game_state:
            self._deactivate_buttons_for_bot_turn()
            self._log_action("SYSTEM", "NO ACTIVE HAND", 0, play_sound=False)
            return

        current_player = self.current_game_state.players[self.current_action_player]
        if current_player.is_human:
            self._activate_buttons_for_human_turn()
        else:
            self._deactivate_buttons_for_bot_turn()

    def _submit_professional_action(self):
        """Submit action with proper turn progression and logging."""
        if not self.current_game_state:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return

        try:
            # Get action from UI
            action_str = self.action_var.get()
            bet_size = float(self.bet_size_var.get())

            # Execute action for current player
            current_player = self.current_game_state.players[self.current_action_player]

            # Execute the action
            self._execute_action(current_player, action_str, bet_size)

            # Play sound effect for the action
            self._play_sound_effect(action_str)

            # Log the action
            self._log_action(current_player.name, action_str.upper(), bet_size)

            # Move to next player
            self._advance_to_next_player()

            # Check if round is complete
            if self._is_round_complete():
                # Check for all-fold scenario first
                if not self._handle_all_fold_scenario():
                    self._advance_to_next_street()

            # Redraw table
            self._redraw_professional_table()

            # Update turn indicator
            self._update_turn_indicator()

            # Start bot actions if next player is bot
            if self.current_game_state:
                next_player = self.current_game_state.players[
                    self.current_action_player
                ]
                if not next_player.is_human:
                    threading.Timer(self.bot_action_delay, self._bot_action).start()

            # Show professional feedback
            self._show_professional_feedback(action_str, bet_size)

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

        # If only one player remains, hand is complete
        if len(active_players) <= 1:
            return True

        # Check if all active players have acted and bets are equal
        for player in active_players:
            if player.stack < self.current_game_state.current_bet:
                return False
        return True

    def _handle_all_fold_scenario(self):
        """Handle scenario when all players fold except one."""
        active_players = [p for p in self.current_game_state.players if p.is_active]

        if len(active_players) == 1:
            winner = active_players[0]
            self.current_game_state.pot += winner.current_bet  # Add any remaining bet
            winner.stack += self.current_game_state.pot

            # Log the result
            self._log_action(
                "SYSTEM",
                f"All players folded! {winner.name} wins ${self.current_game_state.pot:.2f}",
                0,
                play_sound=False,
            )

            # Play winner sound
            self._play_sound_effect("winner")

            # Show results and start new hand
            self._show_hand_results()
            return True
        return False

    def _advance_to_next_street(self):
        """Advance to the next street (flop, turn, river)."""
        if self.current_hand_phase == "preflop":
            self.current_hand_phase = "flop"
            self.community_cards_dealt = 3
            self._deal_community_cards(3)
            self._play_sound_effect("street_change")  # Flop sound
        elif self.current_hand_phase == "flop":
            self.current_hand_phase = "turn"
            self.community_cards_dealt = 4
            self._deal_community_cards(1)
            self._play_sound_effect("street_change")  # Turn sound
        elif self.current_hand_phase == "turn":
            self.current_hand_phase = "river"
            self.community_cards_dealt = 5
            self._deal_community_cards(1)
            self._play_sound_effect("street_change")  # River sound
        elif self.current_hand_phase == "river":
            # Hand is complete
            self._play_sound_effect("showdown")  # Showdown sound
            self._show_hand_results()
            return

        # Reset betting for new street
        self.current_game_state.current_bet = 0.0
        self.current_action_player = (self.big_blind_position + 1) % len(
            self.current_game_state.players
        )

    def _deal_community_cards(self, num_cards):
        """Deal community cards."""
        if not hasattr(self, "_deck"):
            self._deck = self._create_deck()
            import random

            random.shuffle(self._deck)

        for _ in range(num_cards):
            if self._deck:
                card = self._deck.pop()
                self.current_game_state.board.append(card)
                self._redraw_professional_table()
                self._play_sound_effect("deal")  # Deal sound for each card
                time.sleep(0.3)  # Deal cards with delay

    def _show_hand_results(self):
        """Show the results of the hand."""
        messagebox.showinfo(
            "Hand Complete",
            f"Hand completed!\nFinal pot: ${self.current_game_state.pot:.2f}\n"
            f"Winner: {self._determine_winner()}",
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
                is_current = i == self.current_action_player
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

        # Create professional main window - much larger to accommodate 80% table
        self.root = tk.Tk()
        self.root.title("Professional Poker Table")
        self.root.geometry("1800x1400")  # Taller window for bottom controls
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
