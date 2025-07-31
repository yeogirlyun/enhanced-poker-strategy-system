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
from poker_state_machine import PokerStateMachine, PokerState, ActionType


class ProfessionalPokerTable:
    """Professional poker table with perfect centering and realistic game flow."""

    def __init__(self, parent_frame, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.engine = EnhancedPokerEngine(strategy_data)

        # Initialize state machine
        self.state_machine = PokerStateMachine(num_players=6)
        self.state_machine.on_action_required = self._handle_human_action_required
        self.state_machine.on_hand_complete = self._handle_hand_complete
        self.state_machine.on_round_complete = self._handle_round_complete

        # Game state from state machine
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

        # Game state tracking (now managed by state machine)
        self.hand_started = False

        # Action log and sound effects
        self.action_log = []
        self.bot_action_delay = 0.75  # Seconds between bot actions (reduced from 1.5)
        self.action_sound_delay = 0.25  # Delay for sound effects (reduced from 0.5)

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
        """Execute an action immediately using state machine (FOLD, CHECK, CALL)."""
        if not self.current_game_state or not self.hand_started:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return

        try:
            # Get current player from state machine
            current_player = self.state_machine.get_action_player()
            if not current_player or not current_player.is_human:
                return

            # Convert action to ActionType
            action_type = None
            if action == "fold":
                action_type = ActionType.FOLD
            elif action == "check":
                action_type = ActionType.CHECK
            elif action == "call":
                action_type = ActionType.CALL

            # Execute action through state machine
            if action_type and self.state_machine.is_valid_action(
                current_player, action_type
            ):
                self.state_machine.execute_action(current_player, action_type)

                # Update game state
                self.current_game_state = self.state_machine.game_state

                # Redraw table
                self._redraw_professional_table()

                # Show professional feedback
                self._show_professional_feedback(action, 0)
            else:
                self._log_action(
                    "SYSTEM", f"Invalid action: {action}", 0, play_sound=False
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute action: {str(e)}")

    def _set_action(self, action):
        """Set the selected action (for BET/RAISE that require submit)."""
        self.action_var.set(action)
        print(f"Action selected: {action}")  # Debug info
        # Log the selected action
        self._log_action(
            "SYSTEM", f"Action selected: {action.upper()}", 0, play_sound=False
        )
        # Make submit button more prominent when action is selected
        self.submit_button.config(bg="#FF6B35", text="SUBMIT NOW!")  # Orange background

    def _activate_buttons_for_human_turn(self):
        """Activate buttons when it's the human player's turn."""
        for btn in self.action_buttons.values():
            btn.config(
                state=tk.NORMAL,
                bg="white",  # White background when active
                fg="black",  # Black text when user can act
                relief="raised",
                bd=3,
            )  # White background with black text when active
        # Log turn info to action log
        self._log_action(
            "SYSTEM", "🎯 YOUR TURN - Action buttons active!", 0, play_sound=False
        )
        # Play special sound for human turn
        self._play_sound_effect("your_turn")

    def _deactivate_buttons_for_bot_turn(self):
        """Deactivate buttons when it's a bot player's turn."""
        for btn in self.action_buttons.values():
            btn.config(
                state=tk.DISABLED,
                bg="white",  # White background when inactive
                fg="gray",  # Dim gray text when user cannot act
                relief="sunken",
                bd=1,
            )  # White background with dim text when inactive
        # Log turn info to action log
        self._log_action(
            "SYSTEM", "🤖 BOT TURN - Action buttons inactive", 0, play_sound=False
        )

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
        """Simulate bot player action using state machine."""
        if not self.current_game_state:
            return

        current_player = self.state_machine.get_action_player()
        if not current_player or current_player.is_human:
            return  # Not a bot player

        # Simulate bot thinking time
        time.sleep(self.bot_action_delay)

        # Get strategy-based decision with detailed logging
        action, bet_size, rationale = self._get_strategy_based_decision(current_player)

        # Log detailed bot decision rationale
        self._log_action(
            "SYSTEM",
            f"BOT DECISION: {current_player.name} ({current_player.position})",
            0,
            play_sound=False,
        )
        self._log_action(
            "SYSTEM",
            f"  Hand: {self._format_cards(current_player.cards)}",
            0,
            play_sound=False,
        )
        self._log_action(
            "SYSTEM",
            f"  Community: {self._format_cards(self.current_game_state.board)}",
            0,
            play_sound=False,
        )
        self._log_action(
            "SYSTEM", f"  HS Score: {rationale['hs_score']}", 0, play_sound=False
        )
        self._log_action(
            "SYSTEM",
            f"  Street: {self.state_machine.get_current_state()}",
            0,
            play_sound=False,
        )
        self._log_action(
            "SYSTEM",
            f"  Decision Table: {rationale['decision_table']}",
            0,
            play_sound=False,
        )
        self._log_action(
            "SYSTEM", f"  Thresholds: {rationale['thresholds']}", 0, play_sound=False
        )
        self._log_action(
            "SYSTEM", f"  Action: {action.upper()} ${bet_size:.2f}", 0, play_sound=False
        )
        self._log_action(
            "SYSTEM", f"  Reason: {rationale['reason']}", 0, play_sound=False
        )

        # Convert action to ActionType and execute through state machine
        action_type = None
        if action == "fold":
            action_type = ActionType.FOLD
        elif action == "check":
            action_type = ActionType.CHECK
        elif action == "call":
            action_type = ActionType.CALL
        elif action == "bet":
            action_type = ActionType.BET
        elif action == "raise":
            action_type = ActionType.RAISE

        if action_type:
            self.state_machine.execute_action(current_player, action_type, bet_size)
            self.current_game_state = self.state_machine.game_state

        # Log bot action
        self._log_action(current_player.name, action.upper(), bet_size)

        # Redraw table
        self._redraw_professional_table()

    def _get_strategy_based_decision(self, player: Player) -> tuple[str, float, dict]:
        """Get strategy-based decision for a bot player with detailed rationale."""
        # Get player's hand strength
        hs_score = self._evaluate_hand_strength(
            player.cards, self.current_game_state.board
        )

        # Get current street and position
        street = self.state_machine.get_current_state()
        position = player.position

        # Determine if this is a PFA (Pot First Action) or Caller situation
        is_pfa = self.current_game_state.current_bet == 0

        # Get decision table entry
        decision_table = "pfa" if is_pfa else "caller"
        table_entry = self._get_decision_table_entry(street, position, decision_table)

        # Determine action based on strategy
        action, bet_size, reason = self._determine_action_from_strategy(
            hs_score, table_entry, is_pfa, self.current_game_state.current_bet
        )

        rationale = {
            "hs_score": hs_score,
            "decision_table": decision_table,
            "thresholds": table_entry,
            "reason": reason,
        }

        return action, bet_size, rationale

    def _evaluate_hand_strength(self, hole_cards: list, community_cards: list) -> int:
        """Evaluate hand strength based on strategy file."""
        if not self.strategy_data or not self.strategy_data.strategy_dict:
            return 25  # Default fallback

        # Get hand strength tables
        hand_strength_tables = self.strategy_data.strategy_dict.get(
            "hand_strength_tables", {}
        )

        if not community_cards:
            # Preflop - use preflop hand strength table
            preflop_table = hand_strength_tables.get("preflop", {})
            hand_key = self._format_hand_for_strategy(hole_cards)
            return preflop_table.get(hand_key, 15)  # Default to 15 if not found
        else:
            # Postflop - evaluate based on hand type
            hand_type = self._evaluate_postflop_hand_type(hole_cards, community_cards)
            postflop_table = hand_strength_tables.get("postflop", {})
            return postflop_table.get(hand_type, 15)  # Default to 15 if not found

    def _format_hand_for_strategy(self, cards: list) -> str:
        """Format cards for strategy lookup (e.g., ['Ah', 'Ks'] -> 'AKs')."""
        if len(cards) != 2:
            return "XX"

        # Extract ranks and suits
        rank1, suit1 = cards[0][0], cards[0][1]
        rank2, suit2 = cards[1][0], cards[1][1]

        # Determine if suited
        is_suited = suit1 == suit2

        # Create hand key (e.g., "AKs" for suited, "AKo" for offsuit)
        if rank1 == rank2:
            return f"{rank1}{rank1}"  # Pair
        else:
            # Sort ranks (higher first)
            ranks = sorted(
                [rank1, rank2], key=lambda x: "AKQJT98765432".index(x), reverse=True
            )
            hand_key = f"{ranks[0]}{ranks[1]}"
            return f"{hand_key}s" if is_suited else f"{hand_key}o"

    def _evaluate_postflop_hand_type(
        self, hole_cards: list, community_cards: list
    ) -> str:
        """Evaluate postflop hand type for strategy lookup."""
        # Simple evaluation - in a real implementation, you'd use treys or similar
        # For now, return a basic hand type based on card analysis
        all_cards = hole_cards + community_cards

        # Count ranks and suits
        ranks = [card[0] for card in all_cards]
        suits = [card[1] for card in all_cards]

        # Check for flush
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1

        max_suit_count = max(suit_counts.values()) if suit_counts else 0

        # Check for pairs/three of a kind
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        max_rank_count = max(rank_counts.values()) if rank_counts else 0

        # Determine hand type
        if max_suit_count >= 5:
            return "flush"
        elif max_rank_count >= 4:
            return "quads"
        elif max_rank_count == 3:
            # Check for full house
            if len([c for c in rank_counts.values() if c >= 2]) >= 2:
                return "full_house"
            else:
                return "set"
        elif max_rank_count == 2:
            # Check for two pair
            pairs = [c for c in rank_counts.values() if c >= 2]
            if len(pairs) >= 2:
                return "two_pair"
            else:
                return "pair"
        else:
            return "high_card"

    def _get_decision_table_entry(
        self, street: str, position: str, table_type: str
    ) -> dict:
        """Get decision table entry for current situation."""
        if not self.strategy_data or not self.strategy_data.strategy_dict:
            return {"val_thresh": 25, "check_thresh": 10, "sizing": 0.75}

        postflop_strategy = self.strategy_data.strategy_dict.get("postflop", {})
        table = postflop_strategy.get(table_type, {})
        street_table = table.get(street, {})
        return street_table.get(
            position, {"val_thresh": 25, "check_thresh": 10, "sizing": 0.75}
        )

    def _determine_action_from_strategy(
        self, hs_score: int, table_entry: dict, is_pfa: bool, current_bet: float
    ) -> tuple[str, float, str]:
        """Determine action based on strategy thresholds."""
        val_thresh = table_entry.get("val_thresh", 25)
        check_thresh = table_entry.get("check_thresh", 10)
        sizing = table_entry.get("sizing", 0.75)

        if is_pfa:
            # Pot First Action (no bet to call)
            if hs_score >= val_thresh:
                # Value bet
                bet_size = max(1, int(current_bet * sizing)) if current_bet > 0 else 2
                return "bet", bet_size, f"Value bet (HS {hs_score} >= {val_thresh})"
            elif hs_score >= check_thresh:
                # Check-call
                return "check", 0, f"Check-call (HS {hs_score} >= {check_thresh})"
            else:
                # Check-fold
                return "check", 0, f"Check-fold (HS {hs_score} < {check_thresh})"
        else:
            # Caller situation (there's a bet to call)
            if hs_score >= val_thresh:
                # Raise
                raise_size = max(current_bet * 2, current_bet + 2)
                return "raise", raise_size, f"Raise (HS {hs_score} >= {val_thresh})"
            elif hs_score >= check_thresh:
                # Call
                return "call", current_bet, f"Call (HS {hs_score} >= {check_thresh})"
            else:
                # Fold
                return "fold", 0, f"Fold (HS {hs_score} < {check_thresh})"

    def _format_cards(self, cards: list) -> str:
        """Format cards for display in logs."""
        if not cards:
            return "None"

        formatted = []
        for card in cards:
            rank, suit = card[0], card[1]
            suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
            formatted.append(f"{rank}{suit_symbol}")

        return " ".join(formatted)

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
            # Check action: player bets 0 (no additional bet)
            player.current_bet = 0

        # Note: Sound effects are handled by _log_action to avoid duplicates

    def _is_showdown(self):
        """Check if we're in showdown phase (river betting complete)."""
        if not self.current_game_state or self.current_hand_phase != "river":
            return False

        # Check if river betting is complete
        active_players = [p for p in self.current_game_state.players if p.is_active]
        if len(active_players) <= 1:
            return False

        # If all active players have acted and bets are equal, it's showdown
        for player in active_players:
            if player.current_bet != self.current_game_state.current_bet:
                return False
        return True

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
            text=player.position,
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

        # Betting amount - below player circle (only show during active betting)
        if hasattr(player, "current_bet") and player.current_bet > 0:
            # Determine if this is a bet or call based on game state
            if self.current_game_state and self.current_game_state.current_bet > 0:
                # There's a bet to call - this is a call
                bet_text = f"Call: ${player.current_bet:.0f}"
            else:
                # No bet to call - this is a bet
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

            # Determine card appearance based on player status and game phase
            if player.is_human:
                # Human player - always show cards
                card_color = "#F5F5F5"  # Very light gray
                show_card_text = True
            elif not player.is_active:
                # Folded player - show mucked cards (face down with "MUCKED" text)
                card_color = "#2C3E50"  # Dark gray for mucked cards
                show_card_text = False
            elif self.current_hand_phase == "river" and self._is_showdown():
                # Showdown - reveal all active players' cards
                card_color = "#F5F5F5"  # Very light gray
                show_card_text = True
            else:
                # Active bot player during play - show card backs
                card_color = "#2C3E50"  # Dark gray for card backs
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
            elif self.current_hand_phase == "river" and self._is_showdown():
                # Showdown - reveal card text for active players
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
            else:
                # Show card back pattern for active bot players
                self.canvas.create_text(
                    card_x + self.card_width // 2,
                    card_y + self.card_height // 2,
                    text="🂠",  # Card back symbol
                    font=("Arial", 16, "bold"),
                    fill="white",
                )

    def _draw_professional_community_cards(self):
        """Draw professional community cards with perfect centering."""
        if not self.current_game_state:
            return

        # Show all community cards (state machine handles dealing)
        cards_to_show = self.current_game_state.board
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

        # Professional street name - use current hand phase
        street_text = self.current_hand_phase.upper()
        self.canvas.create_text(
            self.center_x,
            40,
            text=street_text,
            font=("Arial", 18, "bold"),
            fill="white",
        )

    def _start_professional_hand(self):
        """Start a new professional hand using state machine."""
        try:
            num_players = int(self.player_count_var.get())

            # Initialize hand state
            self.hand_started = True

            # Start the state machine
            self.state_machine.start_hand()

            # Get the initial game state from state machine
            self.current_game_state = self.state_machine.game_state

            # Deal hole cards
            deck = self._create_deck()
            random.shuffle(deck)
            for player in self.current_game_state.players:
                player.cards = [deck.pop(), deck.pop()]

            # Redraw table
            self._redraw_professional_table()

            # Update turn indicator
            self._update_turn_indicator()

            # Log hand start with sound
            self._log_action("DEALER", "Hand Started", 0, play_sound=True)

            # Let the state machine handle the first action
            self.state_machine.handle_current_player_action()

            # Log detailed hand start info
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
                f"Your position: {self.current_game_state.players[0].position}",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                "INSTRUCTIONS: Click an action button (FOLD, CHECK, etc.), then click SUBMIT!",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                "TIP: The SUBMIT button executes your selected action!",
                0,
                play_sound=False,
            )
            self._log_action(
                "SYSTEM",
                f"Your position: {self.current_game_state.players[0].position}",
                0,
                play_sound=False,
            )
            current_player = self.state_machine.get_action_player()
            if current_player:
                self._log_action(
                    "SYSTEM",
                    f"Action starts with: {current_player.name}",
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
        """Update button states based on whose turn it is using state machine."""
        if not self.current_game_state:
            self._deactivate_buttons_for_bot_turn()
            self._log_action("SYSTEM", "NO ACTIVE HAND", 0, play_sound=False)
            return

        # Get current player from state machine
        current_player = self.state_machine.get_action_player()

        if current_player:
            # Only update button states if they need to change
            if current_player.is_human:
                # Check if buttons are currently deactivated
                if self.action_buttons["fold"].cget("state") == "disabled":
                    self._activate_buttons_for_human_turn()
            else:
                # Check if buttons are currently activated
                if self.action_buttons["fold"].cget("state") == "normal":
                    self._deactivate_buttons_for_bot_turn()

    def _submit_professional_action(self):
        """Submit action with proper turn progression using state machine."""
        if not self.current_game_state or not self.hand_started:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return

        try:
            # Get action from UI
            action_str = self.action_var.get()
            bet_size = float(self.bet_size_var.get())

            # Get current player from state machine
            current_player = self.state_machine.get_action_player()
            if not current_player or not current_player.is_human:
                return

            # Convert action to ActionType
            action_type = None
            if action_str == "bet":
                action_type = ActionType.BET
            elif action_str == "raise":
                action_type = ActionType.RAISE

            # Execute action through state machine
            if action_type and self.state_machine.is_valid_action(
                current_player, action_type, bet_size
            ):
                self.state_machine.execute_action(current_player, action_type, bet_size)

                # Update game state
                self.current_game_state = self.state_machine.game_state

                # Play sound effect for the action
                self._play_sound_effect(action_str)

                # Log the action
                self._log_action(current_player.name, action_str.upper(), bet_size)

                # Redraw table
                self._redraw_professional_table()

                # Show professional feedback
                self._show_professional_feedback(action_str, bet_size)
            else:
                self._log_action(
                    "SYSTEM", f"Invalid action: {action_str}", 0, play_sound=False
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit action: {str(e)}")

    def _advance_to_next_player(self):
        """Move to the next active player."""
        num_players = len(self.current_game_state.players)
        self.current_action_player = (self.current_action_player + 1) % num_players

        # Skip folded players
        while not self.current_game_state.players[self.current_action_player].is_active:
            self.current_action_player = (self.current_action_player + 1) % num_players

        # Update turn indicator when player changes
        self._update_turn_indicator()

    def _is_round_complete(self):
        """Check if the current betting round is complete."""
        active_players = [p for p in self.current_game_state.players if p.is_active]

        # If only one player remains, hand is complete
        if len(active_players) <= 1:
            return True

        # Check if all active players have acted and bets are equal
        # A round is complete when all active players have the same bet amount
        target_bet = self.current_game_state.current_bet

        # Debug logging
        self._log_action(
            "SYSTEM",
            f"Round check - Target bet: {target_bet}, Active players: {len(active_players)}",
            0,
            play_sound=False,
        )

        # Special case: if no bet to call (PFA situation) and all players have bet 0, round is complete
        if target_bet == 0:
            all_checked = True
            for player in active_players:
                if player.current_bet != 0:
                    all_checked = False
                    break
            if all_checked:
                self._log_action(
                    "SYSTEM",
                    f"Round complete - all players checked (no bet to call)",
                    0,
                    play_sound=False,
                )
                return True

        # Normal case: check if all players have matched the current bet
        for player in active_players:
            if player.current_bet != target_bet:
                self._log_action(
                    "SYSTEM",
                    f"  {player.name}: bet={player.current_bet} != target={target_bet}",
                    0,
                    play_sound=False,
                )
                return False

        self._log_action(
            "SYSTEM",
            f"Round complete - all players have bet {target_bet}",
            0,
            play_sound=False,
        )
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
        """Advance to the next street using state machine."""
        # State machine handles all street progression
        # This method is now a placeholder for compatibility
        pass

    def _deal_community_cards(self, num_cards):
        """Deal community cards."""
        if not hasattr(self, "_deck"):
            self._deck = self._create_deck()
            import random

            random.shuffle(self._deck)

        for i in range(num_cards):
            if self._deck:
                card = self._deck.pop()
                self.current_game_state.board.append(card)
                self._redraw_professional_table()
                # Log each card dealt
                rank, suit = card[0], card[1]
                suit_symbol = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}[suit]
                self._log_action(
                    "DEALER", f"Dealt: {rank}{suit_symbol}", 0, play_sound=True
                )
                time.sleep(0.15)  # Deal cards with delay (reduced from 0.3)

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

        feedback_text.insert(tk.END, f"🎯 Your Action: {action}\n")
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
                current_player = self.state_machine.get_action_player()
                is_current = current_player and player == current_player
                self._draw_professional_player(player, position, is_current)

            # Draw professional community cards
            self._draw_professional_community_cards()

            # Draw professional pot info
            self._draw_professional_pot_info()

            # Draw professional street info
            self._draw_professional_street_info()

    def _handle_human_action_required(self, player):
        """Handle when the state machine requires a human action."""
        self.current_game_state = self.state_machine.game_state
        self._update_turn_indicator()
        self._activate_buttons_for_human_turn()

    def _handle_hand_complete(self):
        """Handle when the hand is complete."""
        self.current_game_state = self.state_machine.game_state
        self._show_hand_results()
        self.hand_started = False

    def _handle_round_complete(self):
        """Handle when the betting round is complete."""
        self.current_game_state = self.state_machine.game_state
        self._redraw_professional_table()


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
