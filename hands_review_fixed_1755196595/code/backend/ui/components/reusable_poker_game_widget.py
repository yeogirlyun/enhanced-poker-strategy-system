#!/usr/bin/env python3
"""
Reusable Poker Game Widget

This widget provides a complete poker table interface that is solely driven
by the FPSM's display state. It's designed to be used for both simulation
and practice sessions, with no independent decision-making.
"""

from backend.core.session_logger import get_session_logger
from backend.core.flexible_poker_state_machine import EventListener, GameEvent
from backend.utils.sound_manager import SoundManager
import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, Any, List
import time as _time

# Import shared components
from .card_widget import CardWidget

# Import theme and modern widgets
from backend.core.gui_models import THEME
from .modern_poker_widgets import ChipStackDisplay

# Import types
from backend.core.poker_types import ActionType, PokerState


def debug_log(message: str, category: str = "UI_DEBUG"):
    """Log debug messages to file instead of console."""
    try:
        from backend.core.session_logger import get_session_logger

        logger = get_session_logger()
        logger.log_system("DEBUG", category, message, {})
    except BaseException:
        # Fallback to silent operation if logger not available
        pass


# Import sound manager

# Import FPSM components

# Import session logger for comprehensive logging


class ReusablePokerGameWidget(ttk.Frame, EventListener):
    """
    A reusable poker game widget that provides a complete poker table interface
    that is solely driven by the FPSM's display state.
    It's designed to be used for both simulation and practice sessions,
    with no independent decision-making.
    """

    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the reusable poker game widget."""
        # Extract widget-specific options that ttk.Frame doesn't understand
        self.debug_mode = kwargs.pop("debug_mode", False)
        ttk.Frame.__init__(self, parent, **kwargs)
        EventListener.__init__(self)

        # Store the state machine
        self.state_machine = state_machine

        # GameDirector integration
        self.game_director = None

        # Event loop detection to prevent infinite loops
        self.event_history = []
        self.max_event_history = 100
        self.last_round_complete_time = 0
        # Minimum 100ms between round_complete events
        self.min_round_complete_interval = 0.1

        # Initialize UI components
        self.canvas = None
        self.player_seats = []
        self.community_card_widgets = []
        self.pot_label = None
        self.layout_manager = self.LayoutManager()
        self.bet_labels = {}  # Store bet display labels for cleanup

        # Change tracking to prevent unnecessary redraws (FLICKER-FREE)
        self.last_player_states = {}  # Track each player's last state
        self.last_pot_amount = 0.0

        # Bet display system (money graphics in front of players)
        self.bet_displays = {}  # Store bet display widgets for each player

        # Sound manager
        self.sound_manager = SoundManager()

        # Animation protection flag
        self.animating_bets_to_pot = False

        # Display state tracking for lazy redrawing
        self.last_display_state = None
        self.last_action_player = -1
        self.table_drawn = False

        # Hand-complete animation coordination
        self._pot_animation_scheduled = False
        self._bet_animation_total_delay_ms = 0

        # Highlight timing control to make actions visually clearer
        # Keep highlight on the acting player for 1000ms after an action,
        # then move to the next player. With bot delay set to 1.0s,
        # this yields a 1.0s post-action hold for better user comprehension.
        self._highlight_delay_ms = 1000
        self._suppress_highlight_until = 0.0  # epoch seconds
        self._pending_highlight_index = None
        self._highlight_timer_active = False

        # Store poker game configuration for dynamic positioning
        self.poker_game_config = None

        # Session logger for comprehensive logging
        self.session_logger = get_session_logger()

        # Logging state tracking
        self.current_hand_id = None
        self.last_player_stacks = {}
        self.last_player_bets = {}
        self.current_street = "preflop"

        # Setup the UI components
        self._setup_ui()

        # If state machine is provided, add this widget as a listener
        if self.state_machine:
            self.state_machine.add_event_listener(self)
            # Wait for UI to be ready, then create seats and update
            self.after(100, self._ensure_seats_created_and_update)

    # ==============================
    # EXTENSIBILITY HOOK METHODS
    # Override these in child classes for customization
    # ==============================

    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Hook: Determine if a card should be visible to the user.

        Args:
            player_index: Index of the player (0-based)
            card: Card string (e.g., "As", "**", "")

        Returns:
            bool: True if card should be shown, False if hidden

        Default behavior: Hide placeholder cards ("**")
        Override in child classes for different visibility policies.
        """
        return card != "**" and card != ""

    def _transform_card_data(
        self, player_index: int, card: str, card_index: int = 0
    ) -> str:
        """
        Hook: Transform card data before display.

        Args:
            player_index: Index of the player (0-based)
            card: Original card string
            card_index: Index of the card (0 or 1 for hole cards)

        Returns:
            str: Transformed card string to display

        Default behavior: Return card as-is
        Override in child classes to fetch actual cards, add annotations, etc.
        """
        return card

    def _should_update_display(
        self, player_index: int, old_cards: list, new_cards: list
    ) -> bool:
        """
        Hook: Determine if player card display should be updated.

        Args:
            player_index: Index of the player (0-based)
            old_cards: Previous card list
            new_cards: New card list

        Returns:
            bool: True if display should update, False to skip

        Default behavior: Update when cards change
        Override in child classes for different update policies.
        """
        return old_cards != new_cards

    def _should_update_community_cards(
        self, old_cards: list, new_cards: list
    ) -> bool:
        """
        Hook: Determine if community card display should be updated.

        Args:
            old_cards: Previous community card list
            new_cards: New community card list

        Returns:
            bool: True if display should update, False to skip

        Default behavior: Update when cards change
        Override in child classes for different update policies.
        """
        return old_cards != new_cards

    def _customize_player_styling(
        self, player_index: int, player_info: dict
    ) -> dict:
        """
        Hook: Customize player appearance based on game state.

        Args:
            player_index: Index of the player (0-based)
            player_info: Player information from display state

        Returns:
            dict: Styling information (colors, highlights, etc.)

        Default behavior: Standard styling
        Override in child classes for custom player appearance.
        """
        return {
            "highlight": False,
            "background": None,
            "border_color": None,
            "text_color": None,
        }

    def _handle_card_interaction(
        self, player_index: int, card_index: int, card: str
    ):
        """
        Hook: Handle card-specific interactions or annotations.

        Args:
            player_index: Index of the player (0-based)
            card_index: Index of the card (0 or 1 for hole cards)
            card: Card string

        Default behavior: No action
        Override in child classes for educational features, analysis, etc.
        """
        pass

    def reset_change_tracking(self):
        """Reset all change tracking for a new hand (prevents false change detection)."""
        # Hand reset debug removed to reduce log spam
        self.last_player_states.clear()
        self.last_pot_amount = 0.0
        if hasattr(self, "last_board_cards"):
            self.last_board_cards.clear()

        # Reset display state tracking
        self.last_display_state = None
        self.last_action_player = -1

        # Clear bet displays for new hand
        self._clear_all_bet_displays_permanent()

    def set_poker_game_config(self, config):
        """Set poker game configuration for dynamic positioning."""
        self.poker_game_config = config
        # Log configuration change to session logger instead of console
        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "CONFIG_CHANGE",
                f"Poker game config updated: "
                f"{getattr(config, 'num_players', 'unknown')} players",
                {"config": str(config)},
            )

    def _display_state_changed(self, new_state: Dict[str, Any]) -> bool:
        """Check if display state has meaningfully changed (LAZY REDRAW OPTIMIZATION)."""
        if self.last_display_state is None:
            return True  # First time, must render

        # Compare key elements that affect display
        last = self.last_display_state
        current = new_state

        # Check if player count changed
        if len(last.get("players", [])) != len(current.get("players", [])):
            return True

        # Check if pot changed
        if last.get("pot", 0) != current.get("pot", 0):
            return True

        # Check if board cards changed
        if last.get("board", []) != current.get("board", []):
            return True

        # Check if action player changed
        if last.get("action_player", -1) != current.get("action_player", -1):
            return True

        # Check if any player data changed significantly
        last_players = last.get("players", [])
        current_players = current.get("players", [])

        for i, (last_player, current_player) in enumerate(
            zip(last_players, current_players)
        ):
            # Check key player attributes
            if (
                last_player.get("name") != current_player.get("name")
                or last_player.get("stack") != current_player.get("stack")
                or last_player.get("current_bet")
                != current_player.get("current_bet")
                or last_player.get("has_folded")
                != current_player.get("has_folded")
            ):
                return True

            # Special handling for cards - don't trigger redraw if cards go
            # from real to hidden
            last_cards = last_player.get("cards", [])
            current_cards = current_player.get("cards", [])

            # Only consider it a change if cards go from hidden/empty to real cards
            # Don't redraw when real cards become hidden (preserve visual
            # state)
            if last_cards != current_cards and not (
                last_cards and current_cards == ["**", "**"]
            ):  # Don't trigger on real→hidden
                return True

        return False  # No meaningful changes detected

    def _create_bet_display_for_player(self, player_index: int):
        """Create a bet display widget positioned in front of a player."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        # Calculate position between player and center of table
        player_seat = self.player_seats[player_index]
        player_x, player_y = player_seat["position"]

        # Position bet display closer to player (much further from center to
        # avoid community cards)
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2

        # Bet display positioned only 25% toward center from player (was 60%, too close to community cards)
        # For Player 1 (bottom), move bet display even lower to avoid seat
        # overlap
        if player_index == 0:  # Player 1 (bottom position)
            # Move bet display much lower for Player 1 to avoid seat overlap
            bet_x = (
                player_x + (center_x - player_x) * 0.15
            )  # Only 15% toward center
            bet_y = player_y + 80  # Move 80 pixels lower to avoid seat overlap
        else:
            # Other players: standard positioning
            bet_x = player_x + (center_x - player_x) * 0.25
            bet_y = player_y + (center_y - player_y) * 0.25

        # Create modern chip stack display for bets
        chip_display = ChipStackDisplay(self.canvas, amount=0.0, title="Bet")

        # Position the chip display using canvas create_window for proper
        # positioning
        bet_window = self.canvas.create_window(
            bet_x, bet_y, window=chip_display, anchor="center"
        )

        # Initially hide the bet display
        self.canvas.itemconfig(bet_window, state="hidden")

        # Store reference to bet display
        if not hasattr(self, "bet_displays"):
            self.bet_displays = {}
        self.bet_displays[player_index] = {
            "chip_display": chip_display,
            "window": bet_window,
            "visible": False,
        }

    def _show_bet_display_for_player(
        self, player_index: int, action: str, amount: float
    ):
        """Show bet display for a player with the given action and amount."""
        # Create bet display if it doesn't exist
        if not hasattr(self, "bet_displays"):
            self.bet_displays = {}
        if player_index not in self.bet_displays:
            self._create_bet_display_for_player(player_index)

        if player_index not in self.bet_displays:
            return

        bet_display = self.bet_displays[player_index]

        # Update the chip display with the new amount and action
        chip_display = bet_display["chip_display"]
        chip_display.set_amount(amount)
        chip_display.set_title(action.title() if action else "Bet")

        # Show the bet display
        self.canvas.itemconfig(bet_display["window"], state="normal")
        bet_display["visible"] = True

        # Do not auto-fade during the street; bet displays are cleared on
        # round_complete

    def _clear_all_bet_displays_permanent(self):
        """Clear all bet displays for new hand."""
        # Bet display clearing debug removed
        if hasattr(self, "bet_displays"):
            for player_index, bet_display in self.bet_displays.items():
                if bet_display["visible"]:
                    self.canvas.itemconfig(
                        bet_display["window"], state="hidden"
                    )
                    bet_display["visible"] = False

    def on_event(self, event: GameEvent):
        """Handle events from the FPSM."""
        # Event logging is handled by specific event handlers, no console
        # output needed

        # ENHANCED Event deduplication to prevent infinite loops
        if not hasattr(self, "last_processed_events"):
            self.last_processed_events = {}
        if not hasattr(self, "rapid_event_count"):
            self.rapid_event_count = {}

        # Create a more comprehensive unique key for this event
        event_data = getattr(event, "data", {})
        player_name = event_data.get(
            "player_name", getattr(event, "player_name", "")
        )
        action = event_data.get("action", getattr(event, "action", ""))
        amount = event_data.get("amount", getattr(event, "amount", 0))

        event_key = f"{event.event_type}_{player_name}_{action}_{amount}"
        current_time = _time.time()

        # Track rapid-fire events and block excessive duplicates
        if event_key in self.last_processed_events:
            time_diff = current_time - self.last_processed_events[event_key]
            if time_diff < 0.2:  # 200ms threshold
                # Count rapid events
                if event_key not in self.rapid_event_count:
                    self.rapid_event_count[event_key] = 1
                else:
                    self.rapid_event_count[event_key] += 1

                # Block if too many rapid events
                if self.rapid_event_count[event_key] > 2:
                    # Event filtering debug removed
                    return
                else:
                    debug_log(
                        f"Skipping duplicate event: {
                            event.event_type} (within {
                            time_diff * 1000:.1f}ms)",
                        "UI_EVENT_FILTER",
                    )
                    return
        else:
            # Reset rapid event count for new events
            if event_key in self.rapid_event_count:
                del self.rapid_event_count[event_key]

        self.last_processed_events[event_key] = current_time

        # Log the event for debugging and analysis
        self._log_event(event)

        if event.event_type == "display_state_update":
            display_state = event.data.get("display_state", {})

            # CRITICAL DEBUGGING: Log display state updates that might cause
            # highlighting
            if self.session_logger:
                current_state = display_state.get("current_state", "UNKNOWN")
                action_player_index = display_state.get(
                    "action_player_index", -1
                )

                self.session_logger.log_system(
                    "DEBUG",
                    "HIGHLIGHT_DEBUG",
                    "📺 display_state_update received",
                    {
                        "current_state": str(current_state),
                        "action_player_index": action_player_index,
                        "timestamp": _time.time(),
                        "hand_complete": display_state.get(
                            "hand_complete", False
                        ),
                    },
                )

            self._render_from_display_state(display_state)

        elif event.event_type == "action_executed":
            # Handle action execution - play sounds and animations
            self._handle_action_executed(event)

        elif event.event_type == "state_change":
            # Handle state changes - play sounds for street progression
            self._handle_state_change(event)

        elif event.event_type == "round_complete":
            # Handle round completion - play sounds and animations
            self._handle_round_complete(event)

        elif event.event_type == "hand_complete":
            # Handle hand completion - pot to winner animation
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO",
                    "HIGHLIGHT_DEBUG",
                    "🏁 hand_complete event received - HAND IS OVER!",
                    {
                        "event_source": "FPSM",
                        "widget_class": "ReusablePokerGameWidget",
                        "timestamp": _time.time(),
                        "winners": event.data.get("winners", []),
                        "pot_amount": event.data.get("pot_amount", 0),
                    },
                )
            self._handle_hand_complete(event)

    def _handle_action_executed(self, event: GameEvent):
        """Handle action execution events - show bet amounts and play sounds."""
        # Handle both data dict format and direct attribute format
        if hasattr(event, "data") and event.data:
            action_type = event.data.get("action_type")
            amount = event.data.get("amount", 0.0)
            player_name = event.data.get("player_name", "Unknown")
        else:
            # Direct attribute format (FPSM style)
            action_type = getattr(event, "action", None)
            amount = getattr(event, "amount", 0.0)
            player_name = getattr(event, "player_name", "Unknown")

            # Convert ActionType enum to string if needed
            if hasattr(action_type, "value"):
                action_type = action_type.value.lower()

        # Find player index by name
        player_index = -1
        if (
            hasattr(self, "state_machine")
            and self.state_machine
            and hasattr(self.state_machine, "game_state")
        ):
            for i, player in enumerate(self.state_machine.game_state.players):
                if player.name == player_name:
                    player_index = i
                    break

        # TIMING FIX: Keep highlight on acting player during sound + delay
        if player_index >= 0 and player_index < len(self.player_seats):
            if isinstance(action_type, str):
                # Convert string to ActionType enum
                try:
                    action_enum = ActionType[action_type.upper()]
                except BaseException:
                    action_enum = ActionType.CHECK  # fallback
            else:
                action_enum = action_type or ActionType.CHECK

            self._maintain_highlight_during_action(
                player_index, action_enum, amount
            )

        # Action execution logging handled by session logger, no console output
        # needed

        # Show bet amount for betting actions
        if (
            action_type in ["bet", "raise", "call"]
            and amount > 0
            and player_index >= 0
        ):
            # Bet display debug removed
            self.show_bet_display(player_index, action_type, amount)

        # Clear any existing action indicator for this player
        if player_index >= 0:
            # Player found, proceed with action indicator clearing
            # Action indicator cleared for player
            # Clear action indicator (you can enhance this later)
            pass

        # Play sound for the action (only if this widget should handle sounds)
        if action_type and hasattr(self, "play_sound") and self._should_play_action_sounds():
            sound_map = {
                "bet": "bet",
                "raise": "bet",
                "call": "call",
                "check": "check",
                "fold": "fold",
                "all_in": "all_in",
            }
            if action_type.lower() in sound_map:
                self.play_sound(sound_map[action_type.lower()])

    def _should_play_action_sounds(self) -> bool:
        """
        Determine if this widget should play action sounds.
        
        Override this in subclasses to prevent duplicate sounds when multiple 
        poker widgets are active simultaneously.
        """
        return True  # Base widget plays sounds by default
    
    def _apply_pending_highlight(self):
        """Apply a deferred highlight update after the brief suppression window."""
        self._highlight_timer_active = False
        if self._pending_highlight_index is not None:
            self._highlight_current_player(self._pending_highlight_index)
            self._pending_highlight_index = None

    def _maintain_highlight_during_action(
        self, acting_player_index: int, action_type: ActionType, amount: float
    ):
        """Keep highlight on acting player during action sound + delay before moving to next player."""
        # Calculate sound duration and delay
        sound_duration_ms = self._estimate_action_sound_duration(
            action_type, amount
        )
        additional_delay_ms = (
            1000  # Additional 1.0s for user to process who acted
        )
        total_delay_ms = sound_duration_ms + additional_delay_ms

        # Log the timing for debugging
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "TIMING_COORDINATION",
                "Maintaining highlight during action",
                {
                    "acting_player": acting_player_index + 1,
                    "action": action_type.value,
                    "sound_duration_ms": sound_duration_ms,
                    "additional_delay_ms": additional_delay_ms,
                    "total_delay_ms": total_delay_ms,
                    "component": "ReusablePokerGameWidget",
                },
            )

        # Ensure this player stays highlighted
        self._highlight_current_player(acting_player_index)

        # Store the current acting player to suppress immediate highlight
        # changes
        self._action_in_progress = {
            "player_index": acting_player_index,
            "end_time": _time.time() + (total_delay_ms / 1000.0),
        }

        # Schedule highlight transition after sound + delay
        self.after(total_delay_ms, self._complete_action_timing)

    def _estimate_action_sound_duration(
        self, action_type: ActionType, amount: float
    ) -> int:
        """Estimate the duration of action sound in milliseconds."""
        # Voice sound durations (estimated based on typical speech)
        voice_durations = {
            ActionType.CHECK: 800,  # "Check" - short
            ActionType.CALL: 800,  # "Call" - short
            ActionType.FOLD: 800,  # "Fold" - short
            ActionType.BET: 800,  # "Bet" - short
            # "Raise" - slightly longer (includes all-in)
            ActionType.RAISE: 1000,
        }

        base_duration = voice_durations.get(action_type, 800)

        # Add small buffer for sound effect that might play after voice
        sound_effect_buffer = 200

        return base_duration + sound_effect_buffer

    def _complete_action_timing(self):
        """Complete the action timing sequence and allow highlight to move."""
        # Clear the action in progress
        if hasattr(self, "_action_in_progress"):
            delattr(self, "_action_in_progress")

        # Force a display state update to move highlight to next player
        if hasattr(self, "state_machine") and self.state_machine:
            try:
                game_info = self.state_machine.get_display_state()
                if game_info:
                    self._update_from_game_info(game_info)
                    # Log the highlight transition
                    if self.session_logger:
                        self.session_logger.log_system(
                            "DEBUG",
                            "TIMING_COORDINATION",
                            "Action timing completed - allowing highlight transition",
                            {"component": "ReusablePokerGameWidget"},
                        )
            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR",
                        "TIMING_COORDINATION",
                        f"Error completing action timing: {e}",
                        {"component": "ReusablePokerGameWidget"},
                    )

    def _log_event(self, event: GameEvent):
        """Log all events for debugging and analysis."""
        if not self.session_logger:
            return

        # Extract event data for logging
        event_data = {
            "event_type": event.event_type,
            "timestamp": _time.time(),
            "player_name": getattr(event, "player_name", None),
            "action": getattr(event, "action", None),
            "amount": getattr(event, "amount", 0.0),
            "data": event.data if hasattr(event, "data") else {},
        }

        # Log system event
        self.session_logger.log_system(
            "INFO",
            "GUI_EVENT",
            f"GUI received {event.event_type} event",
            event_data,
        )

        # Log specific event types for detailed tracking
        if event.event_type == "action_executed":
            self._log_player_action(event)
        elif event.event_type == "state_change":
            self._log_state_change(event)
        elif event.event_type == "display_state_update":
            self._log_display_state_update(event)

    def _log_player_action(self, event: GameEvent):
        """Log detailed player action information."""
        if not self.session_logger or not self.state_machine:
            return

        player_name = getattr(event, "player_name", "Unknown")
        action = getattr(event, "action", None)
        amount = getattr(event, "amount", 0.0)

        # Get current game state for accurate logging
        try:
            game_info = self.state_machine.get_game_info()
            players = game_info.get("players", [])
            pot_amount = game_info.get("pot", 0.0)

            # Find player information
            player_index = -1
            stack_before = 0.0
            stack_after = 0.0
            current_bet = 0.0
            position = ""

            for i, player in enumerate(players):
                if player.get("name") == player_name:
                    player_index = i
                    stack_before = player.get("stack", 0.0)
                    current_bet = player.get("current_bet", 0.0)
                    position = player.get("position", "")

                    # Calculate stack after action
                    if action and hasattr(action, "value"):
                        if action.value in ["bet", "raise"]:
                            stack_after = stack_before - amount
                        elif action.value == "call":
                            stack_after = stack_before - amount
                        elif action.value in ["fold", "check"]:
                            stack_after = stack_before
                        else:
                            stack_after = stack_before
                    break

            # Log the action with comprehensive details
            self.session_logger.log_action(
                player_name=player_name,
                player_index=player_index,
                action=action.value if action else "unknown",
                amount=amount,
                stack_before=stack_before,
                stack_after=stack_after,
                pot_before=self.last_pot_amount,
                pot_after=pot_amount,
                current_bet=current_bet,
                street=self.current_street,
                position=position,
                # Assuming Player 1 is human
                is_human=player_name == "Player 1",
            )

            # Update tracking variables
            self.last_pot_amount = pot_amount
            if player_name in self.last_player_stacks:
                self.last_player_stacks[player_name] = stack_after
            if player_name in self.last_player_bets:
                self.last_player_bets[player_name] = current_bet

        except Exception as e:
            print(f"⚠️ Error logging player action: {e}")

    def _log_state_change(self, event: GameEvent):
        """Log state change events."""
        if not self.session_logger:
            return

        new_state = event.data.get("new_state", "")
        old_state = event.data.get("old_state", "")

        # Update current street tracking
        if "DEAL_FLOP" in new_state:
            self.current_street = "flop"
        elif "DEAL_TURN" in new_state:
            self.current_street = "turn"
        elif "DEAL_RIVER" in new_state:
            self.current_street = "river"
        elif "SHOWDOWN" in new_state:
            self.current_street = "showdown"

        # Log state change
        self.session_logger.log_system(
            "INFO",
            "STATE_CHANGE",
            f"State changed from {old_state} to {new_state}",
            {
                "old_state": old_state,
                "new_state": new_state,
                "current_street": self.current_street,
            },
        )

    def _log_display_state_update(self, event: GameEvent):
        """Log display state updates for tracking UI changes."""
        if not self.session_logger:
            return

        display_state = event.data.get("display_state", {})

        # Log pot changes
        pot_amount = display_state.get("pot", 0.0)
        if pot_amount != self.last_pot_amount:
            pot_msg = (
                f"Pot updated from ${self.last_pot_amount:.2f} "
                f"to ${pot_amount:.2f}"
            )
            self.session_logger.log_system(
                "INFO",
                "POT_UPDATE",
                pot_msg,
                {
                    "old_pot": self.last_pot_amount,
                    "new_pot": pot_amount,
                    "pot_change": pot_amount - self.last_pot_amount,
                },
            )
            self.last_pot_amount = pot_amount

        # Log player stack changes
        players = display_state.get("players", [])
        for player in players:
            player_name = player.get("name", "")
            stack_amount = player.get("stack", 0.0)
            current_bet = player.get("current_bet", 0.0)

            # Track stack changes
            if player_name in self.last_player_stacks:
                old_stack = self.last_player_stacks[player_name]
                if stack_amount != old_stack:
                    stack_msg = (
                        f"{player_name} stack changed from "
                        f"${old_stack:.2f} to ${stack_amount:.2f}"
                    )
                    self.session_logger.log_system(
                        "INFO",
                        "STACK_UPDATE",
                        stack_msg,
                        {
                            "player_name": player_name,
                            "old_stack": old_stack,
                            "new_stack": stack_amount,
                            "stack_change": stack_amount - old_stack,
                        },
                    )

            self.last_player_stacks[player_name] = stack_amount

            # Track bet changes
            if player_name in self.last_player_bets:
                old_bet = self.last_player_bets[player_name]
                if current_bet != old_bet:
                    bet_msg = (
                        f"{player_name} bet changed from "
                        f"${old_bet:.2f} to ${current_bet:.2f}"
                    )
                    self.session_logger.log_system(
                        "INFO",
                        "BET_UPDATE",
                        bet_msg,
                        {
                            "player_name": player_name,
                            "old_bet": old_bet,
                            "new_bet": current_bet,
                            "bet_change": current_bet - old_bet,
                        },
                    )

            self.last_player_bets[player_name] = current_bet

    def _log_card_reveal(
        self, player_name: str, cards: List[str], is_hole_cards: bool = True
    ):
        """Log card reveal events."""
        if not self.session_logger:
            return

        card_type = "hole cards" if is_hole_cards else "community cards"
        msg = f"{player_name} {card_type} revealed: {cards}"
        self.session_logger.log_system(
            "INFO",
            "CARD_REVEAL",
            msg,
            {
                "player_name": player_name,
                "cards": cards,
                "card_type": card_type,
                "street": self.current_street,
            },
        )

    def _log_hand_completion(
        self,
        winner: str,
        winning_hand: str,
        pot_size: float,
        showdown: bool = False,
    ):
        """Log hand completion events."""
        if not self.session_logger:
            return

        hand_msg = (
            f"Hand completed - Winner: {winner}, Hand: {winning_hand}, "
            f"Pot: ${pot_size:.2f}"
        )
        self.session_logger.log_system(
            "INFO",
            "HAND_COMPLETE",
            hand_msg,
            {
                "winner": winner,
                "winning_hand": winning_hand,
                "pot_size": pot_size,
                "showdown": showdown,
                "street": self.current_street,
            },
        )

    def _log_session_event(
        self, event_type: str, message: str, data: Dict[str, Any] = None
    ):
        """Log general session events."""
        if not self.session_logger:
            return

        self.session_logger.log_system(
            "INFO", "SESSION_EVENT", message, data or {}
        )

    def _render_from_display_state(self, display_state: Dict[str, Any]):
        """Render the widget based on the FPSM's display state (LAZY REDRAW OPTIMIZATION)."""

        # Note: Bet animations are now protected selectively in individual update methods
        # rather than blocking all updates here

        # Rendering from FPSM display state with lazy redraw optimization

        # Only redraw table if needed (lazy optimization to prevent flicker)
        if not hasattr(self, "_table_drawn") or not self._table_drawn:
            self._draw_table()
            self._table_drawn = True

        # Update all players
        for i, player_info in enumerate(display_state.get("players", [])):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_from_display_state(i, player_info)

        # LAZY redraw community cards (only when changed)
        board_cards = display_state.get("board", [])
        # Log to structured logger instead of console
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "CARD_DISPLAY",
                "Board cards update",
                {
                    "raw_board_cards": board_cards,
                    "component": "ReusablePokerGameWidget",
                },
            )
        # Filter out placeholder cards ("**") and ensure we have valid cards
        filtered_board_cards = [
            card
            for card in board_cards
            if card and card != "**" and len(card) >= 2
        ]
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "CARD_DISPLAY",
                "Board cards filtered",
                {
                    "filtered_board_cards": filtered_board_cards,
                    "filter_removed": len(board_cards)
                    - len(filtered_board_cards),
                },
            )

        # Only update if cards actually changed
        if (
            not hasattr(self, "_last_board_cards")
            or self._last_board_cards != filtered_board_cards
        ):
            # Card display update debug removed
            if (
                not hasattr(self, "_community_area_drawn")
                or not self._community_area_drawn
            ):
                self._draw_community_card_area()
                self._community_area_drawn = True
            self._update_community_cards_from_display_state(
                filtered_board_cards
            )
            self._last_board_cards = filtered_board_cards[:]

        # LAZY redraw pot (only when changed)
        pot_amount = display_state.get("pot", 0.0)
        # Log to structured logger instead of console
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "POT_DISPLAY",
                "Pot amount update",
                {
                    "pot_amount": pot_amount,
                    "component": "ReusablePokerGameWidget",
                },
            )
        if (
            not hasattr(self, "_last_pot_amount")
            or self._last_pot_amount != pot_amount
        ):
            # Pot display update debug removed
            if (
                not hasattr(self, "_pot_area_drawn")
                or not self._pot_area_drawn
            ):
                self._draw_pot_display()
                self._pot_area_drawn = True
            self.update_pot_amount(pot_amount)
            self._last_pot_amount = pot_amount

        # Update current action player with a short delay if a bet just
        # occurred
        import time as _time

        action_player_index = display_state.get("action_player", -1)
        if action_player_index >= 0 and action_player_index < len(
            self.player_seats
        ):
            # CRITICAL: Don't call _highlight_current_player when hand is over
            # to preserve winner highlighting
            current_state = (
                getattr(self.state_machine, "current_state", None)
                if hasattr(self, "state_machine")
                else None
            )
            if current_state and current_state in [
                PokerState.END_HAND,
                PokerState.SHOWDOWN,
            ]:
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "HIGHLIGHT_DEBUG",
                        "🚨 BLOCKING _highlight_current_player call - hand is over!",
                        {
                            "action_player_index": action_player_index,
                            "current_state": str(current_state),
                            "reason": "Preserving winner highlighting",
                        },
                    )
                return  # Skip player highlighting to preserve winner highlights

            now = _time.time()
            if now < getattr(self, "_suppress_highlight_until", 0.0):
                # Defer highlight until suppression expires
                self._pending_highlight_index = action_player_index
                if not getattr(self, "_highlight_timer_active", False):
                    delay_ms = int(
                        max(0, (self._suppress_highlight_until - now) * 1000)
                    )
                    self._highlight_timer_active = True
                    self.after(delay_ms, self._apply_pending_highlight)
            else:
                self._highlight_current_player(action_player_index)

    def _update_player_from_display_state(
        self, player_index: int, player_info: Dict[str, Any]
    ):
        """Update a single player based on display state (FLICKER-FREE VERSION)."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        player_seat = self.player_seats[player_index]

        # Get current state for comparison
        last_state = self.last_player_states.get(player_index, {})

        # Extract new state
        name = player_info.get("name", f"Player {player_index + 1}")
        position = player_info.get("position", "")
        # UI should not set defaults - data comes from state machine
        stack_amount = player_info.get("stack", 0.0)
        # Stack debug routed to logger if needed - removed console output
        bet_amount = player_info.get("current_bet", 0.0)
        cards = player_info.get("cards", [])
        has_folded = player_info.get("has_folded", False)

        # Only update name if it changed
        name_text = f"{name} ({position})"
        if last_state.get("name_text") != name_text:
            player_seat["name_label"].config(text=name_text)
            # Player name updated successfully

        # Only update stack if it changed
        if last_state.get("stack", 0.0) != stack_amount:
            player_seat["stack_label"].config(text=f"${int(stack_amount):,}")
            debug_log(
                f"Updated player {player_index + 1} stack: ${int(stack_amount):,}",
                "STACK_DISPLAY",
            )
            # Log to structured logger instead of console
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "STACK_DISPLAY",
                    "Player stack updated",
                    {
                        "player_index": player_index + 1,
                        "new_stack": int(stack_amount),
                        "component": "ReusablePokerGameWidget",
                    },
                )
        else:
            # Log to structured logger instead of console
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "STACK_DISPLAY",
                    "Player stack unchanged",
                    {
                        "player_index": player_index + 1,
                        "stack_amount": stack_amount,
                        "last_amount": last_state.get("stack", 0.0),
                    },
                )

        # Only update bet if it changed (but preserve bet displays during
        # animations)
        bet_text = f"Bet: ${int(bet_amount):,}" if bet_amount > 0 else ""

        # Don't clear bet displays if we're in the middle of bet-to-pot
        # animations
        is_animating_bets = getattr(self, "animating_bets_to_pot", False)

        if last_state.get("bet_text") != bet_text:
            # Only clear bet text if we're not animating (preserve SB/BB during
            # animations)
            if bet_amount > 0 or not is_animating_bets:
                player_seat["bet_label"].config(text=bet_text)
                # Log to structured logger instead of console
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "BET_DISPLAY",
                        "Player bet text updated",
                        {
                            "player_index": player_index + 1,
                            "bet_text": bet_text,
                            "is_animating": is_animating_bets,
                            "component": "ReusablePokerGameWidget",
                        },
                    )
            else:
                # Log to structured logger instead of console
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "BET_DISPLAY",
                        "Bet protected during animation",
                        {
                            "player_index": player_index + 1,
                            "bet_amount": bet_amount,
                            "component": "ReusablePokerGameWidget",
                        },
                    )

            if bet_amount > 0:
                debug_log(
                    f"Updated player {player_index} bet: ${
                        bet_amount:,.2f}",
                    "BET_DISPLAY",
                )
                # Also show graphical money display for existing bets (like
                # blinds)
                self._show_bet_display_for_player(
                    player_index, "bet", bet_amount
                )
                # Log to structured logger instead of console
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "BET_DISPLAY",
                        "Bet display shown",
                        {
                            "player_index": player_index + 1,
                            "bet_amount": bet_amount,
                            "component": "ReusablePokerGameWidget",
                        },
                    )

        # Always call card update method - let specialized widgets decide how
        # to handle **
        last_cards = last_state.get("cards", [])
        if last_cards != cards:
            self._set_player_cards_from_display_state(player_index, cards)
            debug_log(
                f"Updated player {player_index} cards: {last_cards} → {cards}",
                "CARD_DISPLAY",
            )
        elif last_cards and cards == ["**", "**"]:
            # Still call the method - specialized widgets may want to override
            # ** behavior
            self._set_player_cards_from_display_state(player_index, cards)
            debug_log(
                f"Calling card update with hidden data: {cards} (specialized widgets may override)",
                "CARD_DISPLAY",
            )

        # Only update folded status if it changed
        if last_state.get("has_folded", False) != has_folded:
            if has_folded:
                self._mark_player_folded(player_index)
                print(f"❌ Player {player_index} folded")
            else:
                # Player is no longer folded (new hand), restore normal card
                # display
                self._restore_player_cards(player_index)

        # Store the current state for next comparison
        self.last_player_states[player_index] = {
            "name_text": name_text,
            "stack": stack_amount,
            "bet_text": bet_text,
            "cards": cards.copy() if cards else [],
            "has_folded": has_folded,
        }

    def _set_player_cards_from_display_state(
        self, player_index: int, cards: List[str]
    ):
        """Set player cards based on display state using extensibility hooks."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        card_widgets = self.player_seats[player_index]["card_widgets"]

        # Get current cards for change detection
        old_cards = [
            getattr(card_widgets[i], "_current_card", "")
            for i in range(min(2, len(card_widgets)))
        ]

        # Ask child class if we should update
        if not self._should_update_display(player_index, old_cards, cards):
            debug_log(
                f"HOOK: Child class blocked card update for player {player_index}",
                "CARD_HOOK",
            )
            return

        if len(cards) >= 2 and len(card_widgets) >= 2:
            # Process each card through the hook system
            for i in range(2):
                original_card = cards[i] if i < len(cards) else ""

                # Transform card data through hook
                display_card = self._transform_card_data(
                    player_index, original_card, i
                )

                # Check if card should be shown through hook
                should_show = self._should_show_card(
                    player_index, display_card
                )

                # Get current card for change detection
                current_card = getattr(card_widgets[i], "_current_card", "")

                # Only update if changed
                if current_card != display_card:
                    try:
                        if (
                            should_show
                            and display_card
                            and display_card not in ["**", ""]
                        ):
                            # Show actual card
                            player_has_folded = False
                            if (
                                player_index < len(self.last_player_states)
                                and self.last_player_states[player_index]
                            ):
                                player_has_folded = self.last_player_states[
                                    player_index
                                ].get("has_folded", False)

                            card_widgets[i].set_card(
                                display_card, is_folded=player_has_folded
                            )
                            card_widgets[i]._current_card = display_card
                            debug_log(
                                f"HOOK: Player {player_index} card {i}: {current_card} → {display_card} (shown)",
                                "CARD_HOOK",
                            )

                            # Call interaction hook
                            self._handle_card_interaction(
                                player_index, i, display_card
                            )

                        elif display_card == "**":
                            # Show card back (hook decided to keep as hidden)
                            player_has_folded = False
                            if (
                                player_index < len(self.last_player_states)
                                and self.last_player_states[player_index]
                            ):
                                player_has_folded = self.last_player_states[
                                    player_index
                                ].get("has_folded", False)

                            card_widgets[i].set_card(
                                "**", is_folded=player_has_folded
                            )
                            card_widgets[i]._current_card = "**"
                            color = "GRAY" if player_has_folded else "RED"
                            debug_log(
                                f"HOOK: Player {player_index} card {i}: {current_card} → {color} card back",
                                "CARD_HOOK",
                            )

                        else:
                            # Empty card or hook decided to hide
                            card_widgets[i].set_card("", is_folded=False)
                            card_widgets[i]._current_card = ""
                            debug_log(
                                f"HOOK: Player {player_index} card {i}: {current_card} → empty",
                                "CARD_HOOK",
                            )

                    except tk.TclError:
                        # Widget was destroyed, skip
                        pass
                elif current_card and not should_show:
                    # Hook wants to hide a previously visible card
                    try:
                        card_widgets[i].set_card("", is_folded=False)
                        card_widgets[i]._current_card = ""
                        debug_log(
                            f"HOOK: Player {player_index} card {i}: {current_card} → hidden by hook",
                            "CARD_HOOK",
                        )
                    except tk.TclError:
                        pass

    def _update_community_cards_from_display_state(
        self, board_cards: List[str]
    ):
        """Update community cards based on display state (FLICKER-FREE VERSION)."""
        # Log to structured logger instead of console
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "CARD_DISPLAY",
                "Community cards update called",
                {
                    "board_cards": board_cards,
                    "component": "ReusablePokerGameWidget",
                },
            )
        debug_log(
            f"COMMUNITY CARD UPDATE: Input cards: {board_cards}",
            "CARD_DISPLAY",
        )
        # Board cards debug routed to logger via debug_log above

        # Ensure community card widgets are created
        if not self.community_card_widgets:
            debug_log(
                "No community card widgets, creating them...", "CARD_DISPLAY"
            )
            self._draw_community_card_area()

        if not self.community_card_widgets:
            debug_log(
                "COMMUNITY CARD WIDGETS STILL NOT CREATED!", "CARD_DISPLAY"
            )
            return

        debug_log(
            f"Community card widgets exist: {
                len(
                    self.community_card_widgets)} widgets",
            "CARD_DISPLAY",
        )

        # Initialize tracking if not exists
        if not hasattr(self, "last_board_cards"):
            self.last_board_cards = []

        # Check game state - don't show community cards during preflop
        current_state = None
        if hasattr(self, "state_machine") and self.state_machine:
            if hasattr(self.state_machine, "current_state"):
                current_state = str(self.state_machine.current_state)
            elif hasattr(self.state_machine, "get_current_state"):
                current_state = str(self.state_machine.get_current_state())

        # Determine how many cards to show based on current state
        cards_to_show = 0
        if current_state:
            if "PREFLOP_BETTING" in current_state:
                cards_to_show = 0  # No community cards during preflop
                debug_log(
                    f"Preflop: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )
            elif "FLOP" in current_state or "DEAL_FLOP" in current_state:
                cards_to_show = 3  # Show first 3 cards during flop
                debug_log(
                    f"Flop: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )
            elif "TURN" in current_state or "DEAL_TURN" in current_state:
                cards_to_show = 4  # Show first 4 cards during turn
                debug_log(
                    f"Turn: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )
            elif "RIVER" in current_state or "DEAL_RIVER" in current_state:
                cards_to_show = 5  # Show all 5 cards during river
                debug_log(
                    f"River: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )
            elif "END_HAND" in current_state or "SHOWDOWN" in current_state:
                cards_to_show = (
                    5  # Show only 5 community cards during showdown/end
                )
                debug_log(
                    f"Showdown/End: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )
            else:
                # Max 5 community cards for unknown states
                cards_to_show = min(5, len(board_cards))
                debug_log(
                    f"Other state: Showing {cards_to_show} community cards (state: {current_state})",
                    "CARD_DISPLAY",
                )

        # BRUTE FORCE FIX: If we have board cards, always show them (overrides
        # state-based logic)
        if board_cards and len(board_cards) > 0:
            cards_to_show = max(cards_to_show, len(board_cards))
            debug_log(
                f"FORCE OVERRIDE: Board has {
                    len(board_cards)} cards, showing {cards_to_show}",
                "CARD_DISPLAY",
            )

        # Limit board cards to only the first N cards that should be visible
        visible_board_cards = (
            board_cards[:cards_to_show] if board_cards else []
        )
        debug_log(
            f"Board visibility: {
                len(board_cards)} total → {
                len(visible_board_cards)} visible | Cards: {visible_board_cards}",
            "CARD_DISPLAY",
        )

        # Hide cards that shouldn't be shown yet
        if cards_to_show == 0:
            for i, card_widget in enumerate(self.community_card_widgets):
                try:
                    card_widget.set_card("", is_folded=False)
                    card_widget._current_card = ""
                except tk.TclError:
                    pass
            self.last_board_cards = []
            return

        # Use hook to determine if community cards should update
        debug_log(
            f"CHANGE CHECK: visible_board_cards={visible_board_cards}, last_board_cards={
                self.last_board_cards}",
            "CARD_DISPLAY",
        )
        if not self._should_update_community_cards(
            self.last_board_cards, visible_board_cards
        ):
            debug_log(
                "HOOK: Child class blocked community card update", "CARD_HOOK"
            )
            return  # Child class decided not to update

        debug_log(
            f"Board changed: {
                self.last_board_cards} → {visible_board_cards} (showing {cards_to_show}/{
                len(board_cards)} cards)",
            "CARD_DISPLAY",
        )

        # EFFICIENT UPDATE: Only change cards that are different
        for i, card_widget in enumerate(self.community_card_widgets):
            try:
                current_card = getattr(card_widget, "_current_card", "")
                new_card = (
                    visible_board_cards[i]
                    if i < len(visible_board_cards)
                    else ""
                )

                # Only update if the card has actually changed
                if current_card != new_card:
                    if new_card and new_card != "**":
                        # Community cards should always be visible when they
                        # exist
                        card_widget.set_card(new_card, is_folded=False)
                        card_widget._current_card = new_card
                        debug_log(
                            f"✅ SET community card {i}: {current_card} → {new_card}",
                            "CARD_DISPLAY",
                        )

                        # Apply teal highlighting for newly dealt cards
                        if (
                            current_card == "" or current_card == "**"
                        ):  # This is a newly dealt card
                            self._highlight_new_community_card(card_widget, i)
                    else:
                        # Show card back for hidden cards (instead of empty)
                        card_widget.set_card("**", is_folded=False)
                        card_widget._current_card = "**"
                        debug_log(
                            f"Card back set for community card {i}",
                            "CARD_DISPLAY",
                        )
            except tk.TclError:
                # Widget was destroyed, skip
                pass

        # Update the tracking
        self.last_board_cards = visible_board_cards.copy()

    def _highlight_new_community_card(self, card_widget, card_index):
        """Apply teal highlighting to a newly dealt community card."""
        try:
            # Apply teal border highlighting
            original_bg = card_widget.cget("highlightbackground")
            original_thickness = card_widget.cget("highlightthickness")

            # Set teal highlighting
            teal_color = "#008B8B"  # Dark cyan/teal
            card_widget.config(
                highlightbackground=teal_color,
                highlightthickness=4,
                relief="solid",
            )

            debug_log(
                f"Applied teal highlighting to community card {card_index}",
                "CARD_HIGHLIGHT",
            )

            # Schedule removal of highlighting after 2 seconds
            def remove_highlight():
                try:
                    card_widget.config(
                        highlightbackground=original_bg,
                        highlightthickness=original_thickness,
                        relief="flat",
                    )
                    debug_log(
                        f"Removed teal highlighting from community card {card_index}",
                        "CARD_HIGHLIGHT",
                    )
                except tk.TclError:
                    pass  # Widget was destroyed

            # Use after() for delayed highlight removal
            self.after(2000, remove_highlight)  # Remove after 2 seconds

        except tk.TclError:
            pass  # Widget was destroyed

    def _highlight_current_player(self, player_index):
        """Highlight the current action player with strong visual indication."""

        # CRITICAL DEBUGGING: Log all calls to this method
        if self.session_logger:
            # Get the current state machine state
            current_state = (
                getattr(self.state_machine, "current_state", "UNKNOWN")
                if hasattr(self, "state_machine")
                else "NO_SM"
            )

            self.session_logger.log_system(
                "WARNING",
                "HIGHLIGHT_DEBUG",
                "⚠️ _highlight_current_player called",
                {
                    "player_index": player_index,
                    "current_state": str(current_state),
                    "timestamp": _time.time(),
                    # Last 2 stack frames
                    "stack_trace": "".join(
                        __import__("traceback").format_stack()[-3:-1]
                    ),
                },
            )

        # CRITICAL: Block ALL highlighting when hand is over to preserve winner
        # highlighting
        current_state = (
            getattr(self.state_machine, "current_state", None)
            if hasattr(self, "state_machine")
            else None
        )
        if current_state and hasattr(self, "state_machine"):
            if current_state in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR",
                        "HIGHLIGHT_DEBUG",
                        "🚨 BLOCKING ALL player highlighting - hand is over!",
                        {
                            "player_index": player_index,
                            "current_state": str(current_state),
                            "action": "BLOCKED_ALL_HIGHLIGHTING",
                        },
                    )
                return  # Skip ALL highlighting when hand is over

        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]

                # Check if this player has folded by looking for existing
                # folded indicator
                has_folded_indicator = False
                for widget in player_frame.winfo_children():
                    if (
                        hasattr(widget, "_action_indicator")
                        and hasattr(widget, "cget")
                        and "FOLDED" in widget.cget("text")
                    ):
                        has_folded_indicator = True
                        break

                if i == player_index and not has_folded_indicator:

                    # STRONG highlighting for active player (only if not
                    # folded)
                    if self.session_logger:
                        self.session_logger.log_system(
                            "WARNING",
                            "HIGHLIGHT_DEBUG",
                            f"🟡 Applying GOLD highlight to player {player_index}",
                            {
                                "highlightbackground": THEME["text_gold"],
                                "highlightthickness": 6,
                                "bg": THEME["primary_bg"],
                            },
                        )

                    player_frame.config(
                        highlightbackground=THEME["text_gold"],  # Gold
                        highlightthickness=6,  # Much thicker border
                        # Dark Charcoal background
                        bg=THEME["primary_bg"],
                    )

                    # 🔍 BORDER LOGGING: Track all player frame styling changes
                    self.session_logger.log_system(
                        "DEBUG",
                        "BORDER_TRACKING",
                        f"🎯 GOLD highlighting applied to player {player_index}",
                        {
                            "player_index": player_index,
                            "method": "_highlight_current_player",
                            "border_color": THEME["text_gold"],
                            "border_thickness": 6,
                            "background": THEME["primary_bg"],
                            "current_state": (
                                str(current_state)
                                if current_state
                                else "unknown"
                            ),
                        },
                    )
                    # Add blinking effect for extra visibility
                    self._add_action_indicator(player_frame)
                elif not has_folded_indicator:
                    # Normal appearance for inactive players (only if not
                    # folded)
                    player_frame.config(
                        # Emerald Green
                        highlightbackground=THEME["table_felt"],
                        highlightthickness=2,
                        # Deep Navy Slate background
                        bg=THEME["secondary_bg"],
                    )

                    # 🔍 BORDER LOGGING: Track all player frame styling changes
                    self.session_logger.log_system(
                        "DEBUG",
                        "BORDER_TRACKING",
                        f"🔄 NORMAL styling applied to player {player_index}",
                        {
                            "player_index": player_index,
                            "method": "_highlight_current_player",
                            "border_color": THEME["table_felt"],
                            "border_thickness": 2,
                            "background": THEME["secondary_bg"],
                            "current_state": (
                                str(current_state)
                                if current_state
                                else "unknown"
                            ),
                        },
                    )
                # Note: Folded players keep their gray styling set by
                # _mark_player_folded

    def _add_action_indicator(self, player_frame):
        """Add a visual action indicator to the player frame."""
        # Create or update action indicator text
        for widget in player_frame.winfo_children():
            if hasattr(widget, "_action_indicator"):
                widget.destroy()  # Remove old indicator

        # Add "ACTIVE" indicator
        action_label = tk.Label(
            player_frame,
            text="⚡ ACTIVE ⚡",
            bg=THEME["text_gold"],
            fg=THEME["primary_bg"],
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
        )
        action_label._action_indicator = True
        action_label.pack(side=tk.TOP, pady=2)

        # Start blinking animation
        self._blink_action_indicator(action_label, True)

    def _blink_action_indicator(self, label, visible=True):
        """Create a blinking effect for the action indicator."""
        if label.winfo_exists():
            if visible:
                label.config(bg=THEME["text_gold"], fg=THEME["primary_bg"])
            else:
                label.config(
                    bg=THEME["button_allin"], fg="white"
                )  # Orange flash

            # Continue blinking every 500ms
            self.after(
                500, lambda: self._blink_action_indicator(label, not visible)
            )

    def _clear_action_indicators(self, player_index=None):
        """Clear action indicators for a specific player or all players."""
        if player_index is not None:
            # Clear for specific player
            if (
                player_index < len(self.player_seats)
                and self.player_seats[player_index]
            ):
                player_frame = self.player_seats[player_index]["frame"]
                for widget in player_frame.winfo_children():
                    if hasattr(widget, "_action_indicator"):
                        # Action indicator cleared for player
                        widget.destroy()
        else:
            # Clear for all players
            for i, player_seat in enumerate(self.player_seats):
                if player_seat:
                    self._clear_action_indicators(i)

    def _mark_player_folded(self, player_index):
        """Mark a player as folded."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        # Mark cards as folded
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            card_widget.set_folded()

        # Remove any "ACTIVE" indicator and add "FOLDED" indicator
        player_frame = self.player_seats[player_index]["frame"]

        # Remove any existing action indicators
        for widget in player_frame.winfo_children():
            if hasattr(widget, "_action_indicator"):
                widget.destroy()

        # Add "FOLDED" indicator with gray background
        folded_label = tk.Label(
            player_frame,
            text="💤 FOLDED 💤",
            bg=THEME["button_fold"],  # Gray background
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief="sunken",
            bd=2,
        )
        folded_label._action_indicator = True
        folded_label.pack(side=tk.TOP, pady=2)

        # Change player frame to gray background to indicate folded
        player_frame.config(
            highlightbackground="#696969",  # Dark gray
            highlightthickness=2,
            bg="#404040",  # Dark gray background
        )

        # 🔍 BORDER LOGGING: Track all player frame styling changes
        self.session_logger.log_system(
            "DEBUG",
            "BORDER_TRACKING",
            f"💤 FOLDED styling applied to player {player_index}",
            {
                "player_index": player_index,
                "method": "_mark_player_folded",
                "border_color": "#696969",
                "border_thickness": 2,
                "background": "#404040",
            },
        )

    def _unmark_player_folded(self, player_index):
        """Unmark a player as folded (restore to normal state)."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        # Restore cards to normal display
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            if hasattr(card_widget, 'set_unfolded'):
                card_widget.set_unfolded()
            elif hasattr(card_widget, 'config'):
                # Basic restoration - remove any folded styling
                card_widget.config(state='normal')

        # Remove any "FOLDED" indicators
        player_frame = self.player_seats[player_index]["frame"]
        for widget in player_frame.winfo_children():
            if hasattr(widget, "_action_indicator") and widget.cget("text") and "FOLDED" in widget.cget("text"):
                widget.destroy()

        # Restore normal player frame styling
        player_frame.config(
            highlightbackground=THEME["border_inactive"],
            highlightthickness=1,
            bg=THEME["widget_bg"],
        )

        # 🔍 BORDER LOGGING: Track restoration
        if hasattr(self, 'session_logger') and self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "BORDER_TRACKING",
                f"✅ UNFOLDED styling applied to player {player_index}",
                {
                    "player_index": player_index,
                    "method": "_unmark_player_folded",
                    "border_color": THEME["border_inactive"],
                    "background": THEME["widget_bg"],
                },
            )

    def _restore_player_cards(self, player_index):
        """Restore player cards to normal display (unfold them)."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            # Restore the card to unfolded state if it has a card
            current_card = getattr(card_widget, "_current_card", "")
            if current_card:
                card_widget.set_card(current_card, is_folded=False)

    def update_display(self, update_type: str, **kwargs):
        """Update the display based on FPSM events."""
        # Display update requested

        if update_type == "full_update":
            self._update_from_fpsm_state()
        elif update_type == "player_cards":
            player_index = kwargs.get("player_index")
            cards = kwargs.get("cards", [])
            if player_index is not None:
                self._set_player_cards_from_display_state(player_index, cards)
        elif update_type == "community_cards":
            board_cards = kwargs.get("board_cards", [])
            self._update_community_cards_from_display_state(board_cards)
        elif update_type == "pot":
            pot_amount = kwargs.get("pot_amount", 0.0)
            self.update_pot_amount(pot_amount)
        elif update_type == "player_action":
            self._handle_player_action(**kwargs)

    def _handle_state_change(self, event: GameEvent):
        """Handle state change events."""
        new_state = event.data.get("new_state", "")
        # State change event handled

        # Sounds for state transitions
        if "START_HAND" in new_state:
            # Shuffle at the beginning of each hand
            self.play_sound("shuffle")
        elif "DEAL_FLOP" in new_state:
            # Dealer deals the flop
            self.play_sound("deal")
        elif "DEAL_TURN" in new_state:
            # Dealer deals the turn
            self.play_sound("deal")
        elif "DEAL_RIVER" in new_state:
            # Dealer deals the river
            self.play_sound("deal")
        elif "SHOWDOWN" in new_state:
            self.play_sound("winner")

    def _handle_round_complete(self, event: GameEvent):
        """Handle round completion events."""
        street = event.data.get("street", "")

        # Loop detection: prevent rapid-fire round_complete events
        current_time = _time.time()
        if (
            current_time - self.last_round_complete_time
            < self.min_round_complete_interval
        ):
            print(
                f"⚠️  Ignoring rapid round_complete event (street={street}) - too soon after last one"
            )
            return

        self.last_round_complete_time = current_time

        # Track event history for loop detection
        self.event_history.append(
            {"type": "round_complete", "street": street, "time": current_time}
        )
        if len(self.event_history) > self.max_event_history:
            self.event_history.pop(0)

        # Check for infinite loop (same street repeated too many times)
        recent_street_events = [
            e
            for e in self.event_history[-10:]
            if e["type"] == "round_complete" and e["street"] == street
        ]
        if len(recent_street_events) >= 5:
            print(
                f"🛑 INFINITE LOOP DETECTED: {street} round_complete repeated {
                    len(recent_street_events)} times - STOPPING"
            )
            return

        # Round complete event handled

        # Log round completion
        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                f"Round completed: {street}",
                {"street": street, "current_street": self.current_street},
            )

        # Play sound for round completion
        self.play_sound("dealing")

        # Animate all player bets to pot during street transition using
        # snapshot from event
        snapshot = (
            event.data.get("player_bets", []) if hasattr(event, "data") else []
        )
        if snapshot:
            self.animating_bets_to_pot = True
            animation_delay = 0
            for item in snapshot:
                idx = item.get("index", -1)
                amt = item.get("amount", 0.0)
                if idx >= 0 and amt > 0:
                    self.after(
                        animation_delay,
                        lambda pidx=idx, pam=amt: self._animate_bet_to_pot(
                            pidx, pam
                        ),
                    )
                    animation_delay += 280
            # Add a small delay after animations complete so users can perceive
            # completion
            total_delay = animation_delay + 800
            # Remember total delay so hand-complete can start pot animation
            # AFTER this
            self._bet_animation_total_delay_ms = total_delay
            self.after(total_delay, lambda: self._finish_bet_animations())
            debug_log(
                f"Round complete bet-to-pot animation scheduled; total_delay={total_delay}ms",
                "BET_ANIMATION",
            )

        # Animate street progression
        if street in ["flop", "turn", "river"]:
            # Get current board cards from display state
            if hasattr(self, "state_machine") and self.state_machine:
                display_state = self.state_machine.get_game_info()
                board_cards = display_state.get("board", [])
                self.play_animation(
                    "street_progression",
                    street_name=street,
                    board_cards=board_cards,
                )

    def _handle_hand_complete(self, event: GameEvent):
        """Handle hand completion events with pot-to-winner animation."""
        winner_info = event.data.get("winner_info", {})
        pot_amount = event.data.get("pot_amount", 0.0)

        # Extract winner indices for highlighting
        winners_list = (
            event.data.get("winners", []) if hasattr(event, "data") else []
        )
        winner_indices = []

        # Convert winner names to indices
        if winners_list and hasattr(self, "player_seats"):
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "HIGHLIGHT_DEBUG",
                    "Converting winner names to indices",
                    {
                        "winners_list": winners_list,
                        "num_seats": len(self.player_seats),
                    },
                )

            for winner_name in winners_list:
                for i, seat in enumerate(self.player_seats):
                    if seat and hasattr(self, "state_machine"):
                        game_info = self.state_machine.get_game_info()
                        players = game_info.get("players", [])
                        if (
                            i < len(players)
                            and players[i].get("name") == winner_name
                        ):
                            winner_indices.append(i)
                            if self.session_logger:
                                self.session_logger.log_system(
                                    "DEBUG",
                                    "HIGHLIGHT_DEBUG",
                                    f"Found winner index: {winner_name} -> {i}",
                                    {},
                                )
                            break

        # Highlight winners in burgundy color
        if winner_indices:
            self._highlight_winners(winner_indices)
            debug_log(
                f"Highlighted winners: {winner_indices} in burgundy",
                "WINNER_HIGHLIGHT",
            )

        # STRUCTURED DEBUG: Log pot animation debugging with full context
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "POT_ANIMATION_DEBUG",
                "_handle_hand_complete called",
                {
                    "winner_info": winner_info,
                    "pot_amount": pot_amount,
                    "event_data": event.data,
                    "last_pot_amount": self.last_pot_amount,
                    "animation_context": "hand_completion_pot_transfer",
                    "winner_indices": winner_indices,
                },
            )

        debug_log(
            f"Hand complete: {
                winner_info.get(
                    'name',
                    'Unknown')} wins ${
                pot_amount:.2f}",
            "HAND_COMPLETE",
        )
        debug_log(
            f"winner_info={winner_info}, pot_amount={pot_amount}",
            "HAND_COMPLETE",
        )
        debug_log(
            f"event.data keys: {
                list(
                    event.data.keys()) if hasattr(
                    event,
                    'data') and event.data else 'No data'}",
            "HAND_COMPLETE",
        )
        debug_log(
            f"Current pot display amount: ${
                self.last_pot_amount:.2f}",
            "HAND_COMPLETE",
        )

        # Check if pot amount is actually available and valid
        if pot_amount == 0.0:
            # Try to get pot from display state as fallback
            if hasattr(self, "state_machine") and self.state_machine:
                game_info = self.state_machine.get_game_info()
                fallback_pot = game_info.get("pot", 0.0)
                debug_log(
                    f"Pot amount is 0, checking fallback from game_info: ${
                        fallback_pot:.2f}",
                    "HAND_COMPLETE",
                )
                if fallback_pot > 0:
                    pot_amount = fallback_pot
                    debug_log(
                        f"Using fallback pot amount: ${
                            pot_amount:.2f}",
                        "HAND_COMPLETE",
                    )

        # Additional fallback: use last displayed pot amount if available
        if (
            pot_amount == 0.0
            and hasattr(self, "last_pot_amount")
            and self.last_pot_amount > 0
        ):
            pot_amount = self.last_pot_amount
            debug_log(
                f"Using last displayed pot amount as final fallback: ${
                    pot_amount:.2f}",
                "HAND_COMPLETE",
            )

        # Note: Don't clear highlights here - winner highlighting should
        # persist

        # Log hand completion
        if self.session_logger:
            winner_name = winner_info.get("name", "Unknown")
            winning_hand = winner_info.get("hand_description", "Unknown")

            self._log_hand_completion(
                winner=winner_name,
                winning_hand=winning_hand,
                pot_size=pot_amount,
                showdown=True,
            )

        # Ensure we have valid winner info for animation
        if not winner_info or not winner_info.get("name"):
            # Try to get winner from winners list as fallback
            winners_list = (
                event.data.get("winners", []) if hasattr(event, "data") else []
            )
            if winners_list and len(winners_list) > 0:
                winner_info = {"name": winners_list[0], "amount": pot_amount}
                debug_log(
                    f"Using winners list fallback for animation: {winner_info}",
                    "HAND_COMPLETE",
                )

        # Wait for any ongoing bet-to-pot animations to finish before starting pot-to-winner
        # This prevents visual confusion of money moving in multiple directions
        # STRUCTURED DEBUG: Animation condition analysis
        animation_conditions = {
            "winner_info_valid": bool(winner_info),
            "pot_amount_positive": pot_amount > 0,
            "combined_condition": bool(winner_info and pot_amount > 0),
            "pot_amount": pot_amount,
            "winner_name": (
                winner_info.get("name", "Unknown") if winner_info else None
            ),
        }

        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "POT_ANIMATION_DEBUG",
                "Animation condition check",
                animation_conditions,
            )

        if winner_info and pot_amount > 0:
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO",
                    "POT_ANIMATION_DEBUG",
                    "✅ STARTING POT ANIMATION!",
                    {
                        "winner": winner_info.get("name", "Unknown"),
                        "pot_amount": pot_amount,
                        "animation_type": "pot_to_winner",
                    },
                )
            debug_log(
                f"Starting pot animation sequence for {
                    winner_info.get(
                        'name',
                        'Unknown')} with ${pot_amount}",
                "POT_ANIMATION",
            )

            # Update pot display to ensure it shows the correct amount before
            # animation
            self.update_pot_amount(pot_amount)
            # Check if bet animations are currently running and schedule
            # strictly after they finish
            is_animating_bets = getattr(self, "animating_bets_to_pot", False)
            if is_animating_bets:
                delay_for_pot_animation = max(
                    300,
                    getattr(self, "_bet_animation_total_delay_ms", 1200) + 200,
                )
            else:
                # Increase delay for fold wins to give users time to see winner
                # highlighting
                delay_for_pot_animation = (
                    2000  # 2 seconds to see the burgundy border
                )
            debug_log(
                f"is_animating_bets={is_animating_bets}, scheduled_after={delay_for_pot_animation}ms",
                "POT_ANIMATION",
            )
            # Mark that a pot animation is about to run so we can defer heavy
            # redraws
            self._pot_animation_scheduled = True

            # Schedule pot-to-winner animation after bet animations complete
            winners_list = (
                event.data.get("winners", []) if hasattr(event, "data") else []
            )
            self.after(
                delay_for_pot_animation,
                lambda: self._start_pot_to_winner_animation_multi(
                    winner_info, winners_list, pot_amount
                ),
            )
        else:
            if self.session_logger:
                self.session_logger.log_system(
                    "WARNING",
                    "POT_ANIMATION_DEBUG",
                    "❌ NO POT ANIMATION - Condition failed",
                    {
                        "failure_reason": "pot_animation_condition_not_met",
                        "winner_info": winner_info,
                        "pot_amount": pot_amount,
                        "conditions": animation_conditions,
                    },
                )
            debug_log(
                f"No pot animation - winner_info valid: {
                    bool(winner_info)}, pot_amount: {pot_amount}",
                "POT_ANIMATION",
            )
            debug_log(
                f"Current display pot: ${
                    self.last_pot_amount:.2f}, Event pot: ${
                    pot_amount:.2f}",
                "POT_ANIMATION",
            )
            # Log to session logger instead of console
            if self.session_logger:
                self.session_logger.log_system(
                    "WARNING",
                    "HAND_COMPLETE",
                    "No valid winner info or pot amount for animation",
                    {
                        "winner_info": winner_info,
                        "pot_amount": pot_amount,
                        "event_data": event.data,
                    },
                )

    def _start_pot_to_winner_animation(self, winner_info, pot_amount):
        """Wrapper to begin single-winner pot animation and schedule cleanup."""
        try:
            # Ensure pot display is on top during pot-to-winner animation
            if (
                hasattr(self, "pot_display_canvas_id")
                and self.pot_display_canvas_id
            ):
                self.canvas.tag_raise(self.pot_display_canvas_id)
            # Determine approximate animation duration for cleanup scheduling
            num_chips = min(max(1, int(pot_amount / 50)), 6)
            total_duration_ms = (num_chips - 1) * 100 + 30 * 20 + 300
            # Start animation
            self.animate_pot_to_winner(winner_info, pot_amount)
            # Cleanup after animation completes
            self.after(total_duration_ms, self._on_pot_animation_complete)
        except Exception as e:
            debug_log(
                f"Error in _start_pot_to_winner_animation: {e}",
                "POT_ANIMATION",
            )
            # Fallback cleanup to avoid stuck UI
            self.after(800, self._on_pot_animation_complete)

    def _start_pot_to_winner_animation_multi(
        self, winner_info, winners_list, pot_amount
    ):
        """Support split pots: animate chips to multiple winners if needed."""
        try:
            # FIXED: Use winners_list from event data as the authoritative source
            # This is passed from the state machine's hand_complete event:
            # "winners": [w.name for w in winners]
            names = []
            if isinstance(winners_list, list) and winners_list:
                # Convert to strings and clean
                names = [str(name).strip() for name in winners_list if name]
                debug_log(
                    f"Using event winners list: {names}", "POT_ANIMATION"
                )
            else:
                # Only fallback to winner_info if winners_list is unavailable
                # (shouldn't happen)
                raw = (
                    winner_info.get("name", "")
                    if isinstance(winner_info, dict)
                    else ""
                )
                if raw:
                    names = [raw.strip()]
                debug_log(
                    f"Fallback to winner_info name: {names}", "POT_ANIMATION"
                )

            # Check if we truly have multiple winners
            if not names:
                debug_log(
                    "No winners found - skipping animation", "POT_ANIMATION"
                )
                return
            elif len(names) == 1:
                debug_log(f"Single winner: {names[0]}", "POT_ANIMATION")
                self._start_pot_to_winner_animation(winner_info, pot_amount)
                return

            # TRUE SPLIT POT: Multiple winners detected
            debug_log(
                f"Split pot: {
                    len(names)} winners sharing ${
                    pot_amount:.2f}",
                "POT_ANIMATION",
            )
            share = pot_amount / max(1, len(names))
            debug_log(f"Each winner gets: ${share:.2f}", "POT_ANIMATION")

            # Determine final duration across all winners for cleanup
            # scheduling
            try:
                # Conservative estimate: 4 chips per winner, staggered by 120ms
                # per winner
                chips_per = min(max(1, int(share / 50)), 4)
                max_delay = (len(names) - 1) * 120 + (chips_per - 1) * 100
                total_duration_ms = max_delay + 30 * 20 + 400
            except Exception:
                total_duration_ms = 1300
            self.animate_pot_to_multiple_winners(names, share, pot_amount)
            self.after(total_duration_ms, self._on_pot_animation_complete)
        except Exception as e:
            debug_log(f"Error in split-pot start: {e}", "POT_ANIMATION")
            # Fallback to single-winner animation
            self._start_pot_to_winner_animation(winner_info, pot_amount)

    def _reset_all_highlights(self):
        """Clear any active highlights and reset internal state."""
        debug_log("_reset_all_highlights called", "HIGHLIGHT")
        try:
            cleared_count = 0
            for i, seat in enumerate(getattr(self, "player_seats", [])):
                if seat and seat.get("frame"):
                    # Force clear highlight
                    seat["frame"].configure(
                        highlightbackground=THEME["border_inactive"],
                        highlightthickness=2,
                        bg=THEME["secondary_bg"],  # Reset background too
                    )
                    cleared_count += 1
                    debug_log(f"Cleared highlight for seat {i}", "HIGHLIGHT")

                    # Also remove any blinking "ACTIVE" indicators that
                    # might persist
                    for widget in seat["frame"].winfo_children():
                        if hasattr(widget, "_action_indicator"):
                            debug_log(
                                f"Removing action indicator from seat {i}",
                                "HIGHLIGHT",
                            )
                            widget.destroy()

            # Reset all internal state variables
            self.last_action_player = -1
            self._pending_highlight_index = None
            self._suppress_highlight_until = 0.0
            self._highlight_timer_active = False

            # Cancel any pending highlight timers
            if hasattr(self, "_pending_after_ids"):
                for after_id in self._pending_after_ids:
                    try:
                        self.after_cancel(after_id)
                    except BaseException:
                        pass
                self._pending_after_ids = []

            debug_log(
                f"All highlights cleared ({cleared_count} seats) and state reset",
                "HIGHLIGHT",
            )
        except Exception as e:
            debug_log(f"ERROR in _reset_all_highlights: {e}", "HIGHLIGHT")

    def _highlight_winners(self, winner_indices):
        """Highlight winner(s) with sapphire color and winner indicator."""
        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "HIGHLIGHT_DEBUG",
                "🏆 _highlight_winners called",
                {"winner_indices": winner_indices, "timestamp": _time.time()},
            )

        debug_log(
            f"_highlight_winners called for indices: {winner_indices} (burgundy style)",
            "WINNER_HIGHLIGHT",
        )

        # First, clear all action highlights to remove yellow borders
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "HIGHLIGHT_DEBUG",
                "Clearing all highlights before winner highlighting",
                {},
            )
        self._reset_all_highlights()

        # Remove any existing action indicator widgets
        removed_count = 0
        for i, seat in enumerate(getattr(self, "player_seats", [])):
            if seat and seat.get("frame"):
                for widget in seat["frame"].winfo_children():
                    if (
                        hasattr(widget, "_action_indicator")
                        or widget.winfo_class() == "Label"
                    ):
                        # Check if it's an action indicator by text content
                        try:
                            if hasattr(
                                widget, "cget"
                            ) and "ACTIVE" in widget.cget("text"):
                                debug_log(
                                    f"Removing action indicator from seat {i}",
                                    "WINNER_HIGHLIGHT",
                                )
                                if self.session_logger:
                                    self.session_logger.log_system(
                                        "DEBUG",
                                        "HIGHLIGHT_DEBUG",
                                        f"Removing action indicator from seat {i}",
                                        {},
                                    )
                                widget.destroy()
                                removed_count += 1
                        except BaseException:
                            pass

        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "HIGHLIGHT_DEBUG",
                f"Removed {removed_count} action indicators",
                {},
            )

        # Apply sapphire highlighting to winners
        success_count = 0
        for winner_index in winner_indices:
            if winner_index < len(getattr(self, "player_seats", [])):
                seat = self.player_seats[winner_index]
                if seat and seat.get("frame"):
                    player_frame = seat["frame"]

                    # Apply VIVID burgundy winner border - VERY BOLD AND
                    # NOTICEABLE
                    player_frame.configure(
                        highlightbackground="#8B0000",  # Dark red / burgundy border - VERY VISIBLE
                        highlightthickness=8,  # MUCH thicker border for winners
                        # Note: Removed bg color to keep only border
                        # highlighting
                    )

                    # 🔍 BORDER LOGGING: Track all player frame styling changes
                    self.session_logger.log_system(
                        "DEBUG",
                        "BORDER_TRACKING",
                        f"🏆 BURGUNDY WINNER styling applied to player {winner_index}",
                        {
                            "player_index": winner_index,
                            "method": "_highlight_winners",
                            "border_color": "#8B0000",
                            "border_thickness": 8,
                            "background": "unchanged",
                        },
                    )

                    # Add winner indicator
                    self._add_winner_indicator(player_frame)
                    success_count += 1

                    debug_log(
                        f"Applied burgundy highlighting to winner seat {winner_index}",
                        "WINNER_HIGHLIGHT",
                    )
                    if self.session_logger:
                        self.session_logger.log_system(
                            "INFO",
                            "HIGHLIGHT_DEBUG",
                            f"✅ Applied burgundy highlighting to winner seat {winner_index}",
                            {
                                "player_frame_id": id(player_frame),
                                "highlightbackground": "#8B0000",
                                "highlightthickness": 8,
                                "bg": "#A0002A",
                            },
                        )

        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "HIGHLIGHT_DEBUG",
                "🏆 Winner highlighting completed",
                {
                    "requested_winners": len(winner_indices),
                    "successfully_highlighted": success_count,
                },
            )

    def _add_winner_indicator(self, player_frame):
        """Add winner indicator label to player frame."""
        try:
            # Create winner indicator label
            winner_label = tk.Label(
                player_frame,
                text="🏆 WINNER! 🏆",
                font=("Arial", 12, "bold"),
                fg="#8B0000",  # Burgundy text to match border
                bg="white",  # White background for clean contrast
                relief="raised",
                bd=2,
            )
            winner_label.pack(side="top", pady=2)
            debug_log("Added winner indicator label", "WINNER_HIGHLIGHT")
        except Exception as e:
            debug_log(
                f"Error adding winner indicator: {e}", "WINNER_HIGHLIGHT"
            )

    def _handle_player_action(self, **kwargs):
        """Handle player action updates from FPSM."""
        player_name = kwargs.get("player_name", "")
        action = kwargs.get("action", "")
        amount = kwargs.get("amount", 0.0)

        # Player action event handled

        # Log player action
        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "PLAYER_ACTION",
                f"Player action: {player_name} {action} ${amount}",
                {
                    "player_name": player_name,
                    "action": action,
                    "amount": amount,
                    "street": self.current_street,
                },
            )

        # Find player index by name
        if self.state_machine:
            for i, player in enumerate(self.state_machine.game_state.players):
                if player.name == player_name:
                    self._animate_player_action(i, action, amount)
                    break

    def _animate_player_action(self, player_index, action, amount):
        """Animate a player action."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return

        # Play sound using the GUI's play_sound method (which uses configurable
        # system)
        if self.sound_manager:
            self.play_sound(action.lower())

        # Show bet display
        if amount > 0:
            self.show_bet_display(player_index, action, amount)

    def show_bet_display(self, player_index, action, amount):
        """Show bet using modern chip display only (no text labels)."""
        # Use the chip stack display pipeline
        self._show_bet_display_for_player(player_index, action, amount)

    def _fade_bet_display(self, player_index: int):
        """Fade out bet display for a player."""
        if player_index in self.bet_displays:
            bet_display = self.bet_displays[player_index]
            if bet_display["visible"]:
                self.canvas.itemconfig(bet_display["window"], state="hidden")
                bet_display["visible"] = False

    def _clear_all_bet_displays(self):
        """Clear all bet displays."""
        if hasattr(self, "bet_displays"):
            for player_index in self.bet_displays:
                bet_display = self.bet_displays[player_index]
                if bet_display["visible"]:
                    self.canvas.itemconfig(
                        bet_display["window"], state="hidden"
                    )
                    bet_display["visible"] = False

    def _finish_bet_animations(self):
        """Finish bet animations and clear displays."""
        debug_log(
            "Finishing bet animations - clearing displays", "BET_ANIMATION"
        )
        self.animating_bets_to_pot = False

        # Re-enable voice after animations
        if self.sound_manager:
            self.sound_manager.set_animation_mode(False)

        self._clear_all_bet_displays()
        self._clear_all_bet_displays_permanent()

        # If a pot animation is queued, do not force a redraw now (it would
        # clear chips)
        if not getattr(self, "_pot_animation_scheduled", False):
            debug_log(
                "Forcing display update after bet animation completion",
                "DISPLAY_UPDATE",
            )
            self.after_idle(self._force_display_refresh)

    def _remove_bet_display(self, player_index: int):
        """Remove bet display for a specific player."""
        if player_index in self.bet_labels:
            try:
                self.canvas.delete(self.bet_labels[player_index])
                del self.bet_labels[player_index]
            except Exception as e:
                debug_log(
                    f"Error removing bet display for player {player_index}: {e}",
                    "BET_DISPLAY",
                )

    def _update_from_game_info(self, game_info: dict):
        """Update the widget display from game info."""
        try:
            # Update player information
            if "players" in game_info:
                for i, player_info in enumerate(game_info["players"]):
                    if i < len(self.player_seats):
                        self._update_player_display(i, player_info)

            # Update pot and board information
            if "pot" in game_info:
                self._update_pot_display(game_info["pot"])

            if "board" in game_info:
                self._update_board_display(game_info["board"])

        except Exception as e:
            debug_log(f"Error updating from game info: {e}", "DISPLAY_UPDATE")

    def _force_display_refresh(self):
        """Force a complete display refresh after animations."""
        debug_log("Forcing complete display refresh", "DISPLAY_UPDATE")
        if hasattr(self, "state_machine") and self.state_machine:
            # Force a complete canvas refresh
            debug_log("Forcing canvas update and refresh", "DISPLAY_UPDATE")
            self.canvas.update()
            self.canvas.update_idletasks()

            # Force redraw all table components - reset all lazy redraw flags
            debug_log(
                "Force redrawing all components with complete table refresh",
                "DISPLAY_UPDATE",
            )

            # Reset ALL drawing flags to force complete redraw
            self.table_drawn = False

            # Reset lazy redraw tracking for ALL components
            if hasattr(self, "last_canvas_size"):
                delattr(self, "last_canvas_size")
            if hasattr(self, "last_community_canvas_size"):
                delattr(self, "last_community_canvas_size")
            if hasattr(self, "last_pot_canvas_size"):
                delattr(self, "last_pot_canvas_size")

            # Preserve community cards through showdown/end-hand. Do NOT clear here.
            # They will be cleared naturally when a new hand starts and the
            # preflop state renders with cards_to_show == 0.
            if hasattr(self, "pot_label"):
                debug_log(
                    "Clearing pot label for forced redraw", "DISPLAY_UPDATE"
                )
                self.pot_label = None
            if hasattr(self, "last_seats_canvas_size"):
                delattr(self, "last_seats_canvas_size")

            # Minimal forced redraw - let lazy optimization handle the rest
            # Only force what's absolutely necessary after clearing
            self._ensure_seats_created_and_update()

            # No need to manually trigger display state events - FPSM will emit them
            # when needed. This prevents duplicate rendering cycles.
            # Final canvas refresh
            debug_log("Final canvas refresh completed", "DISPLAY_UPDATE")
            self.canvas.update()

    def update_pot_amount(self, amount):
        """Update the pot amount display (FLICKER-FREE VERSION). Always apply update.
        Note: self.last_pot_amount may be updated by logging earlier; do not gate on it.
        """
        if hasattr(self, "pot_display") and self.pot_display:
            self.pot_display.set_amount(amount)
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "POT_DISPLAY",
                    f"Pot display set to ${amount:,.2f}",
                    {
                        "canvas_id": getattr(self, "pot_display_canvas_id", None),
                        "pot_display_visible": self.pot_display.winfo_viewable(),
                        "pot_display_width": self.pot_display.winfo_width(),
                        "pot_display_height": self.pot_display.winfo_height(),
                        "canvas_coords": self.canvas.coords(self.pot_display_canvas_id) if hasattr(self, "pot_display_canvas_id") else None
                    }
                )
        elif hasattr(self, "pot_label") and self.pot_label:
            # Fallback for legacy pot label
            self.pot_label.config(text=f"${amount:,.2f}")
            debug_log(f"Pot legacy label set to ${amount:,.2f}", "POT_DISPLAY")
        else:
            # Pot display doesn't exist yet - create it then set
            debug_log(
                f"Creating pot display for amount: ${
                    amount:,.2f}",
                "POT_DISPLAY",
            )
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "POT_DISPLAY",
                    "Creating pot display (not found)",
                    {"width": self.canvas.winfo_width(), "height": self.canvas.winfo_height()}
                )
            self._draw_pot_display()
            if hasattr(self, "pot_display") and self.pot_display:
                self.pot_display.set_amount(amount)
                # Debug the created pot display
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG", "POT_DISPLAY",
                        f"Pot display created and set to ${amount:,.2f}",
                        {
                            "pot_exists": hasattr(self, "pot_display"),
                            "pot_viewable": self.pot_display.winfo_viewable() if hasattr(self, "pot_display") else False,
                            "pot_width": self.pot_display.winfo_width() if hasattr(self, "pot_display") else 0,
                            "pot_height": self.pot_display.winfo_height() if hasattr(self, "pot_display") else 0,
                            "canvas_id": getattr(self, "pot_display_canvas_id", None)
                        }
                    )
            else:
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR", "POT_DISPLAY",
                        "Failed to create pot display",
                        {"has_pot_display": hasattr(self, "pot_display")}
                    )
        self.last_pot_amount = amount

    def play_sound(self, sound_type: str, **kwargs):
        """Play a sound effect using the configurable poker event system."""
        if not self.sound_manager:
            debug_log(f"No sound manager available for {sound_type}", "SOUND")
            return

        debug_log(f"Playing sound: {sound_type}", "SOUND")

        # Map sound types to poker events using the new configurable system
        if sound_type in ["fold", "call", "bet", "raise", "check", "all_in"]:
            # Player action sounds - use configurable poker events
            poker_event = f"player_action_{sound_type}"
            self.sound_manager.play_poker_event_sound(poker_event)

            # Also play chip sound for money actions
            amount = kwargs.get("amount", 0.0)
            if sound_type in ["bet", "call", "raise", "all_in"] and amount > 0:
                self.sound_manager.play_poker_event_sound("chip_bet")

        elif sound_type in ["dealing", "deal"]:
            # Card dealing sounds
            self.sound_manager.play_poker_event_sound("card_dealing")
        elif sound_type in ["shuffle"]:
            # Card shuffling sounds
            self.sound_manager.play_poker_event_sound("card_shuffle")
        elif sound_type in ["winner"]:
            # Winner announcement sounds
            self.sound_manager.play_poker_event_sound("winner_announce")
        elif sound_type in ["notification", "turn_notify"]:
            # Turn notification sounds
            self.sound_manager.play_poker_event_sound("turn_notification")
        elif sound_type in ["click", "ui_click"]:
            # UI click sounds
            self.sound_manager.play_poker_event_sound("ui_click")
        else:
            # Fallback: try as poker event first, then legacy
            self.sound_manager.play_poker_event_sound(sound_type)
            # If that doesn't work, try the old method
            if (
                not hasattr(self.sound_manager, "poker_sound_events")
                or sound_type not in self.sound_manager.poker_sound_events
            ):
                self.sound_manager.play(sound_type)

    def play_animation(self, animation_type: str, **kwargs):
        """Play an animation."""
        if animation_type == "street_progression":
            street_name = kwargs.get("street_name", "")
            board_cards = kwargs.get("board_cards", [])
            self._animate_street_progression(street_name, board_cards)
        elif animation_type == "bet_to_pot":
            player_index = kwargs.get("player_index")
            amount = kwargs.get("amount", 0.0)
            if player_index is not None:
                self._animate_bet_to_pot(player_index, amount)

    def _animate_street_progression(self, street_name, board_cards):
        """Animate street progression."""
        # Street progression animation started
        self._update_community_cards_from_display_state(board_cards)

    def _animate_bet_to_pot(self, player_index, amount):
        """Animate a bet moving to the pot with enhanced chip graphics."""
        if not hasattr(self, "pot_frame") or player_index >= len(
            self.player_seats
        ):
            return

        player_seat = self.player_seats[player_index]
        if not player_seat:
            return

        # Get player and pot positions using stored positions
        player_x, player_y = player_seat["position"]

        # Get pot position
        pot_x = self.canvas.winfo_width() // 2
        pot_y = self.canvas.winfo_height() // 2 + 50  # Pot position

        # Create animated chip for the movement (larger and more visible)
        chip_label = tk.Label(
            self.canvas,
            text="💰",
            bg="gold",
            fg="black",
            font=("Arial", 28, "bold"),  # Larger font
            bd=3,
            relief="raised",
            padx=6,
            pady=4,
        )

        chip_window = self.canvas.create_window(
            player_x, player_y, window=chip_label
        )
        self.canvas.tag_raise(chip_window)  # Bring to front

        # Play chip movement sound (but not voice during animations)
        if self.sound_manager:
            self.sound_manager.play_poker_event_sound(
                "chip_bet"
            )  # Only chip sound, no voice

        # Animate the chip to the pot with smooth movement
        def move_chip_step(step=0):
            # Faster animation (about ~2x faster than previous)
            total_steps = 30
            if step <= total_steps:
                progress = step / total_steps
                # Smooth easing function
                ease_progress = progress * progress * (3.0 - 2.0 * progress)

                x = player_x + (pot_x - player_x) * ease_progress
                y = player_y + (pot_y - player_y) * ease_progress

                # Add slight bounce effect
                if progress > 0.8:
                    bounce = math.sin((progress - 0.8) * 10) * 3
                    y += bounce

                self.canvas.coords(chip_window, x, y)
                # Faster frame rate
                self.after(30, lambda: move_chip_step(step + 1))
            else:
                # Animation complete - remove chip and update pot
                self.canvas.delete(chip_window)
                self._flash_pot_update(amount)

        move_chip_step()

    def _flash_pot_update(self, amount):
        """Flash the pot to indicate chips were added."""
        if (
            hasattr(self, "pot_label")
            and self.pot_label
            and hasattr(self.pot_label, "config")
        ):
            try:
                original_bg = self.pot_label.cget("bg")
                original_fg = self.pot_label.cget("fg")

                # Enhanced flash sequence for better visibility
                def flash_sequence(step=0):
                    if (
                        hasattr(self, "pot_label")
                        and self.pot_label
                        and hasattr(self.pot_label, "config")
                        and step < 8
                    ):
                        if step % 2 == 0:
                            self.pot_label.config(
                                bg="gold", fg="black"
                            )  # Brighter flash
                        else:
                            self.pot_label.config(
                                bg=original_bg, fg=original_fg
                            )
                        self.after(180, lambda: flash_sequence(step + 1))
                    elif (
                        hasattr(self, "pot_label")
                        and self.pot_label
                        and hasattr(self.pot_label, "config")
                    ):
                        self.pot_label.config(bg=original_bg, fg=original_fg)

                flash_sequence()
            except Exception as e:
                print(f"Warning: Could not flash pot label: {e}")

    def animate_pot_to_winner(self, winner_info, pot_amount):
        """Animate pot money moving to the winner's stack."""
        debug_log(
            f"animate_pot_to_winner called with winner_info={winner_info}, pot_amount={pot_amount}",
            "POT_ANIMATION",
        )

        if not winner_info or pot_amount <= 0:
            debug_log(
                f"Animation skipped - winner_info={
                    bool(winner_info)}, pot_amount={pot_amount}",
                "POT_ANIMATION",
            )
            return

        debug_log(
            f"Animating ${
                pot_amount:.2f} to {
                winner_info.get(
                    'name',
                    'Unknown')}",
            "POT_ANIMATION",
        )
        debug_log(
            f"Starting animation for ${
                pot_amount:.2f} to {
                winner_info.get(
                    'name',
                    'Unknown')}",
            "POT_ANIMATION",
        )

        # Find winner's seat
        winner_name = winner_info.get("name", "")
        winner_seat_index = -1

        for i, player_seat in enumerate(self.player_seats):
            if player_seat and player_seat.get("name_label"):
                player_name = player_seat["name_label"].cget("text")
                # Extract player name (remove position info)
                clean_name = player_name.split(" (")[0]
                if clean_name == winner_name:
                    winner_seat_index = i
                    break

        if winner_seat_index == -1:
            debug_log(
                f"Could not find winner seat for {winner_name}",
                "POT_ANIMATION",
            )
            debug_log(
                f"Could not find winner seat for '{winner_name}'",
                "POT_ANIMATION",
            )
            debug_log(
                f"Available players: {
                    [
                        seat['name_label'].cget('text') if seat and seat.get('name_label') else 'None' for seat in self.player_seats]}",
                "POT_ANIMATION",
            )
            return

        debug_log(
            f"Found winner at seat index {winner_seat_index}", "POT_ANIMATION"
        )

        # Get positions
        pot_x = self.canvas.winfo_width() // 2
        pot_y = self.canvas.winfo_height() // 2 + 50

        winner_seat = self.player_seats[winner_seat_index]
        winner_x, winner_y = winner_seat["position"]

        # Create multiple chips for large pots
        num_chips = min(max(1, int(pot_amount / 50)), 6)  # 1-6 chips

        debug_log(
            f"Creating {num_chips} chips animation from ({pot_x}, {pot_y}) to ({winner_x}, {winner_y})",
            "POT_ANIMATION",
        )

        for i in range(num_chips):
            self._animate_single_chip_to_winner(
                pot_x,
                pot_y,
                winner_x,
                winner_y,
                pot_amount / num_chips,
                i * 100,  # Stagger timing
            )

        # Play winner sound
        self.play_sound("winner")

        # Flash winner's stack after animation
        self.after(800, lambda: self._flash_winner_stack(winner_seat_index))

    def _animate_single_chip_to_winner(
        self, start_x, start_y, end_x, end_y, amount, delay
    ):
        """Animate a single chip from pot to winner using canvas drawing."""

        def start_animation():
            # Create chip as canvas oval (not a widget)
            chip_size = 40
            chip_id = self.canvas.create_oval(
                start_x - chip_size // 2,
                start_y - chip_size // 2,
                start_x + chip_size // 2,
                start_y + chip_size // 2,
                fill="gold",
                outline="darkgoldenrod",
                width=3,
                tags="pot_animation_chip",
            )

            # Add text on top of chip
            text_id = self.canvas.create_text(
                start_x,
                start_y,
                text="$",
                fill="red",
                font=("Arial", 20, "bold"),
                tags="pot_animation_chip",
            )

            # Ensure chips are on top
            self.canvas.tag_raise("pot_animation_chip")

            # Animate to winner
            def move_to_winner(step=0):
                total_steps = 30
                if step <= total_steps:
                    progress = step / total_steps
                    # Smooth easing
                    ease_progress = (
                        progress * progress * (3.0 - 2.0 * progress)
                    )

                    x = start_x + (end_x - start_x) * ease_progress
                    y = start_y + (end_y - start_y) * ease_progress

                    # Add celebratory bounce
                    if progress > 0.7:
                        bounce = math.sin((progress - 0.7) * 15) * 5
                        y += bounce

                    # Move both chip and text
                    self.canvas.coords(
                        chip_id,
                        x - chip_size // 2,
                        y - chip_size // 2,
                        x + chip_size // 2,
                        y + chip_size // 2,
                    )
                    self.canvas.coords(text_id, x, y)

                    self.after(20, lambda: move_to_winner(step + 1))
                else:
                    # Animation complete - delete the chip
                    self.canvas.delete(chip_id)
                    self.canvas.delete(text_id)

            move_to_winner()

        self.after(delay, start_animation)

    def _on_pot_animation_complete(self):
        """Cleanup after pot-to-winner animation: hide pot and bet graphics."""
        try:
            # Refresh player stacks and clear any seat bet labels from FPSM
            # state
            if hasattr(self, "state_machine") and self.state_machine:
                self._update_from_fpsm_state()
            # Clear pot display to 0 so no money remains shown at center
            self.update_pot_amount(0.0)
            # Clear any remaining bet displays (both modern and legacy)
            self._clear_all_bet_displays()
            self._clear_all_bet_displays_permanent()
            debug_log(
                "Pot animation complete - pot set to $0 and bet displays cleared",
                "POT_ANIMATION",
            )
        except Exception as e:
            debug_log(
                f"Error during pot animation cleanup: {e}", "POT_ANIMATION"
            )

    def _flash_winner_stack(self, winner_seat_index):
        """Flash the winner's stack to celebrate."""
        if winner_seat_index >= len(self.player_seats):
            return

        winner_seat = self.player_seats[winner_seat_index]
        if not winner_seat or not winner_seat.get("stack_label"):
            return

        stack_label = winner_seat["stack_label"]
        original_bg = stack_label.cget("bg")
        original_fg = stack_label.cget("fg")

        # Flash green for winner
        def flash_step(step=0):
            if step < 6:  # Flash 3 times
                if step % 2 == 0:
                    stack_label.config(bg="green", fg="white")
                else:
                    stack_label.config(bg=original_bg, fg=original_fg)
                self.after(200, lambda: flash_step(step + 1))
            else:
                stack_label.config(bg=original_bg, fg=original_fg)

        flash_step()

    def _ensure_player_seats_created(self):
        """Ensure player seats are created."""
        if not self.player_seats or all(
            seat is None for seat in self.player_seats
        ):
            self._draw_player_seats()

    def _ensure_seats_created_and_update(self):
        """Ensure seats are created and then update from FPSM (LAZY OPTIMIZATION)."""
        # Skip if seats already exist and match the expected count
        expected_player_count = None
        if hasattr(self, "state_machine") and self.state_machine:
            expected_player_count = len(self.state_machine.game_state.players)
        elif hasattr(self, "poker_game_config") and self.poker_game_config:
            expected_player_count = self.poker_game_config.num_players

        if (
            hasattr(self, "player_seats")
            and self.player_seats
            and all(seat is not None for seat in self.player_seats)
            and expected_player_count
            and len(self.player_seats) == expected_player_count
        ):
            # Seats already exist, proceeding to update
            self._update_from_fpsm_state()
            return

        # Ensuring seats are created and updating from FPSM

        # Force update to get actual canvas size
        self.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Canvas size determined for seat positioning

        # Check if canvas is ready - if not, use reasonable default size for
        # creation
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, using default size for seat creation
            # Don't return - create seats anyway with default positioning
            pass

        # Force creation of player seats if needed
        if not self.player_seats or all(
            seat is None for seat in self.player_seats
        ):
            # Creating player seats
            self._draw_player_seats()
        elif (
            expected_player_count
            and len(self.player_seats) != expected_player_count
        ):
            # Player count changed, recreating seats
            self._draw_player_seats()

        # Update display from FPSM
        self._update_from_fpsm_state()

        # Seats created and updated successfully

    def reveal_all_cards(self):
        """Reveal all cards (for simulation mode) - now driven by FPSM."""
        # Revealing all cards for simulation mode
        # This is now handled by FPSM state, so just update from FPSM
        self._update_from_fpsm_state()

    def update_font_size(self, font_size):
        """Update font sizes throughout the widget."""
        # Update pot label font
        if self.pot_label:
            self.pot_label.config(font=("Arial", int(font_size * 0.9)))

        # Update community card title font
        if hasattr(self, "community_frame"):
            for child in self.community_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(font=("Arial", int(font_size * 0.8)))

        # Update player pod fonts
        for player_seat in self.player_seats:
            if player_seat and player_seat["frame"]:
                player_frame = player_seat["frame"]
                player_frame.update_font_size(font_size)

    def increase_table_size(self):
        """Increase the table size (zoom in effect using canvas scaling)."""
        if hasattr(self, "canvas") and self.canvas:
            print("🔍 ReusablePokerGameWidget.increase_table_size() called")

            # Initialize scale factor if not exists
            if not hasattr(self, "_table_scale"):
                self._table_scale = 1.0

            # Increase scale by 20%, max 2.0x (larger increments for
            # visibility)
            old_scale = self._table_scale
            self._table_scale = min(2.0, self._table_scale * 1.2)

            print(
                f"🔍 Scale changed from {
                    old_scale:.1f}x to {
                    self._table_scale:.1f}x"
            )

            # Apply scaling using canvas.scale() on all items from center
            scale_factor = self._table_scale / old_scale

            # Get canvas center point as scaling origin
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = canvas_width / 2
            center_y = canvas_height / 2

            # Scale all canvas items from center
            for item in self.canvas.find_all():
                self.canvas.scale(
                    item, center_x, center_y, scale_factor, scale_factor
                )

            # Update canvas scroll region to accommodate scaling
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

            debug_log(
                f"Table size increased to {
                    self._table_scale:.1f}x scale",
                "TABLE_SIZE",
            )
            print(
                f"🔍 Table size increased to {
                    self._table_scale:.1f}x - canvas items scaled from center ({
                    center_x:.0f}, {
                    center_y:.0f})"
            )

    def decrease_table_size(self):
        """Decrease the table size (zoom out effect using canvas scaling)."""
        if hasattr(self, "canvas") and self.canvas:
            print("🔍 ReusablePokerGameWidget.decrease_table_size() called")

            # Initialize scale factor if not exists
            if not hasattr(self, "_table_scale"):
                self._table_scale = 1.0

            # Decrease scale by 20%, min 0.5x (larger increments for
            # visibility)
            old_scale = self._table_scale
            self._table_scale = max(0.5, self._table_scale * 0.8)

            print(
                f"🔍 Scale changed from {
                    old_scale:.1f}x to {
                    self._table_scale:.1f}x"
            )

            # Apply scaling using canvas.scale() on all items from center
            scale_factor = self._table_scale / old_scale

            # Get canvas center point as scaling origin
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = canvas_width / 2
            center_y = canvas_height / 2

            # Scale all canvas items from center
            for item in self.canvas.find_all():
                self.canvas.scale(
                    item, center_x, center_y, scale_factor, scale_factor
                )

            # Update canvas scroll region to accommodate scaling
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

            debug_log(
                f"Table size decreased to {
                    self._table_scale:.1f}x scale",
                "TABLE_SIZE",
            )
            print(
                f"🔍 Table size decreased to {
                    self._table_scale:.1f}x - canvas items scaled from center ({
                    center_x:.0f}, {
                    center_y:.0f})"
            )

    def _draw_community_card_area(self):
        """Draw the community card area in the center (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        # Check if community card area already exists and canvas size hasn't
        # changed
        current_size = (width, height)
        if (
            hasattr(self, "community_frame")
            and self.community_frame
            and hasattr(self, "community_card_widgets")
            and self.community_card_widgets
            and hasattr(self, "last_community_canvas_size")
            and self.last_community_canvas_size == current_size
        ):
            # Skipping community card area redraw - already exists and no size
            # changes
            return

        # Drawing community card area

        # Use layout manager for positioning
        community_x, community_y = (
            self.layout_manager.calculate_community_card_position(
                width, height
            )
        )

        # Create community card frame
        community_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=0)

        # Create title
        community_title = tk.Label(
            community_frame,
            text="Community Cards",
            bg=THEME["secondary_bg"],
            fg="white",
            font=("Helvetica", 10, "bold"),
        )
        community_title.pack(pady=2)

        # Create cards frame
        cards_frame = tk.Frame(community_frame, bg=THEME["secondary_bg"], bd=0)
        cards_frame.pack(pady=3)

        # Create five CardWidget instances for community cards
        self.community_card_widgets = []
        for i in range(5):
            card_widget = CardWidget(cards_frame, width=60, height=84)
            card_widget.pack(side=tk.LEFT, padx=3)
            self.community_card_widgets.append(card_widget)

        # Store the community frame
        self.community_frame = community_frame
        self.canvas.create_window(
            community_x, community_y, window=community_frame, anchor="center"
        )

        # Store canvas size for next comparison
        self.last_community_canvas_size = current_size

    def _draw_pot_display(self):
        """Draw the pot display in the center (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        # Don't create pot display if canvas is too small (not properly sized yet)
        if width <= 1 or height <= 1:
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG", "POT_DISPLAY",
                    f"Deferring pot display creation - canvas too small: {width}x{height}",
                    {"width": width, "height": height}
                )
            # Schedule retry after canvas is properly sized
            self.after(100, self._draw_pot_display)
            return

        # Check if pot display already exists and canvas size hasn't changed
        current_size = (width, height)
        if (
            hasattr(self, "pot_frame")
            and self.pot_frame
            and hasattr(self, "last_pot_canvas_size")
            and self.last_pot_canvas_size == current_size
        ):
            # Skipping pot display redraw - already exists and no size changes
            return

        # Drawing pot display

        # Use layout manager for positioning (center below community cards)
        pot_x, pot_y = self.layout_manager.calculate_pot_position(
            width, height, widget=self
        )

        # Create modern pot chip display
        self.pot_display = ChipStackDisplay(
            self.canvas, amount=0.0, title="Pot"
        )

        # Store reference to pot label for compatibility
        self.pot_label = self.pot_display.amount_label

        # Store the pot frame for compatibility
        self.pot_frame = self.pot_display
        self.pot_display_canvas_id = self.canvas.create_window(
            pot_x, pot_y, window=self.pot_display, anchor="center"
        )
        
        # Extensive logging for pot display debugging
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG", "POT_DISPLAY",
                f"Pot display created at ({pot_x}, {pot_y}) with canvas_id {self.pot_display_canvas_id}",
                {
                    "canvas_width": self.canvas.winfo_width(),
                    "canvas_height": self.canvas.winfo_height(),
                    "pot_x": pot_x,
                    "pot_y": pot_y,
                    "canvas_id": self.pot_display_canvas_id,
                    "pot_display_exists": hasattr(self, "pot_display") and self.pot_display is not None
                }
            )
        
        # Ensure the pot display is always on top
        try:
            self.canvas.tag_raise(self.pot_display_canvas_id)
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG", "POT_DISPLAY",
                    f"Pot display raised to top with canvas_id {self.pot_display_canvas_id}",
                    {}
                )
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "POT_DISPLAY",
                    f"Failed to raise pot display: {e}",
                    {"canvas_id": self.pot_display_canvas_id}
                )

        # Store canvas size for next comparison
        self.last_pot_canvas_size = current_size

    def _on_resize(self, event=None):
        """Handle resize events (LAZY REDRAW OPTIMIZATION)."""
        if event and event.width > 1 and event.height > 1:
            # Force redraw of all elements when canvas size changes
            self._force_complete_redraw()

    def _force_complete_redraw(self):
        """Force a complete redraw of all UI elements (used on resize)."""
        # Forcing complete redraw due to resize

        # Reset all canvas size tracking to force redraw
        if hasattr(self, "last_canvas_size"):
            delattr(self, "last_canvas_size")
        if hasattr(self, "last_seats_canvas_size"):
            delattr(self, "last_seats_canvas_size")
        if hasattr(self, "last_pot_canvas_size"):
            delattr(self, "last_pot_canvas_size")
        if hasattr(self, "last_community_canvas_size"):
            delattr(self, "last_community_canvas_size")

        # Mark table as not drawn to force redraw
        self.table_drawn = False

        # Redraw table (this will trigger all sub-elements)
        self._draw_table()

    def set_state_machine(self, state_machine):
        """Set the state machine for this widget."""
        self.state_machine = state_machine
        # Immediately update display based on new state machine
        if self.state_machine:
            self._update_from_fpsm_state()

    def set_game_director(self, game_director):
        """Set the game director for this widget."""
        self.game_director = game_director
        debug_log("GameDirector set for UI widget", "GAME_DIRECTOR")

    def render_current_state(self):
        """Pure render function - updates UI from current game state."""
        if not self.game_director:
            # Fallback to old method if no GameDirector
            self._update_from_fpsm_state()
            return

        try:
            # Get current state from GameDirector (single source of truth)
            game_state = self.game_director.get_current_state()

            if game_state:
                # Render immediately from current state
                self._render_from_game_state(game_state)
            else:
                debug_log(
                    "No game state available for rendering", "GAME_DIRECTOR"
                )

        except Exception as e:
            debug_log(f"Error in render_current_state: {e}", "GAME_DIRECTOR")
            # Fallback to old method
            self._update_from_fpsm_state()

    def _render_from_game_state(self, game_state: dict):
        """Render UI from game state dict (pure render function)."""
        try:
            # Update players
            for i, player_info in enumerate(game_state.get("players", [])):
                if i < len(self.player_seats) and self.player_seats[i]:
                    self._update_player_from_display_state(i, player_info)

            # Update community cards
            board_cards = game_state.get("board", [])
            filtered = [
                c
                for c in board_cards
                if isinstance(c, str) and len(c) in (2, 3) and c != "**"
            ]
            self._update_community_cards_from_display_state(filtered)

            # Update pot
            pot_amount = game_state.get("pot", 0.0)
            self.update_pot_amount(pot_amount)

            # Store display state for dealer button update
            self.last_display_state = game_state

            # Update dealer button
            self._update_dealer_button_display()

            # Update current action player highlight (only if hand is still
            # active)
            action_player_index = game_state.get("action_player", -1)
            current_state = game_state.get("current_state")

            if (
                action_player_index >= 0
                and action_player_index < len(self.player_seats)
                and "END_HAND" not in str(current_state)
                and "SHOWDOWN" not in str(current_state)
            ):
                self._highlight_current_player(action_player_index)
            elif "SHOWDOWN" in str(current_state):
                # Clear highlights only for SHOWDOWN, not END_HAND (preserve
                # winner highlighting)
                self._reset_all_highlights()

        except Exception as e:
            debug_log(
                f"Error in _render_from_game_state: {e}", "GAME_DIRECTOR"
            )

    def _update_from_fpsm_state(self):
        """Update the entire display based on FPSM's current state."""
        if not self.state_machine:
            return

        # Updating display from FPSM state

        # Get current game info from FPSM
        game_info = self.state_machine.get_game_info()

        # Debug: Print the cards being returned by FPSM
        for i, player_info in enumerate(game_info.get("players", [])):
            cards = player_info.get("cards", [])
            debug_log(
                f"FPSM returned cards for player {i}: {cards}", "CARD_DISPLAY"
            )

        # Update players
        for i, player_info in enumerate(game_info.get("players", [])):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_from_display_state(i, player_info)

        # Update community cards
        board_cards = game_info.get("board", [])
        # Ensure we only pass actual card codes, not placeholders
        filtered = [
            c
            for c in board_cards
            if isinstance(c, str) and len(c) in (2, 3) and c != "**"
        ]
        self._update_community_cards_from_display_state(filtered)

        # Update pot
        pot_amount = game_info.get("pot", 0.0)
        self.update_pot_amount(pot_amount)

        # Store display state for dealer button update
        self.last_display_state = game_info

        # Update dealer button
        self._update_dealer_button_display()

        # Update current action player (but not during hand completion)
        action_player_index = game_info.get("action_player", -1)
        current_state = game_info.get("current_state", "")

        # TIMING FIX: Don't change highlight if action is in progress
        if hasattr(self, "_action_in_progress") and self._action_in_progress:
            current_time = _time.time()
            if current_time < self._action_in_progress["end_time"]:
                # Action timing still in progress, keep current highlight
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "TIMING_COORDINATION",
                        "Suppressing highlight change - action in progress",
                        {
                            "acting_player": self._action_in_progress[
                                "player_index"
                            ]
                            + 1,
                            "time_remaining": self._action_in_progress[
                                "end_time"
                            ]
                            - current_time,
                            "component": "ReusablePokerGameWidget",
                        },
                    )
                return
            else:
                # Action timing completed, clear the flag
                delattr(self, "_action_in_progress")

        # Don't highlight during hand completion or showdown
        if (
            action_player_index >= 0
            and action_player_index < len(self.player_seats)
            and "END_HAND" not in str(current_state)
            and "SHOWDOWN" not in str(current_state)
        ):
            self._highlight_current_player(action_player_index)
        # Note: Removed _reset_all_highlights() for SHOWDOWN to preserve winner
        # highlighting

    def _setup_ui(self):
        """Set up the UI layout."""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create canvas for the poker table
        self.canvas = tk.Canvas(
            self, bg=THEME["table_felt"], highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Initialize player seats (will be set dynamically based on actual
        # player count)
        self.player_seats = []

        # Force initial draw immediately
        self._force_initial_draw()

        # Create player seats immediately if canvas is ready
        if self.canvas.winfo_width() > 1:
            self._draw_table()
        else:
            # If canvas not ready, schedule it
            self.after(100, self._draw_table)

    def _force_initial_draw(self):
        """Force the initial draw of the table."""
        # Ensure pot display starts from 0 on each new hand visually
        try:
            self.last_pot_amount = 0.0
        except Exception:
            pass
        self.after(100, self._draw_table)

    def _draw_table(self):
        """Draw the poker table with felt design (LAZY REDRAW OPTIMIZATION)."""
        if not self.canvas or self.canvas.winfo_width() <= 1:
            self.after(100, self._draw_table)
            return

        # Check if table is already drawn and canvas size hasn't changed
        current_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
        if (
            hasattr(self, "last_canvas_size")
            and self.last_canvas_size == current_size
            and self.table_drawn
        ):
            # Skipping table redraw - no size changes detected
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Drawing table

        # Clear canvas
        self.canvas.delete("all")

        # Get current scheme colors
        from backend.core.table_felt_styles import get_scheme_manager

        scheme_manager = get_scheme_manager()
        current_scheme = scheme_manager.get_current_scheme()

        # Draw background first (full canvas)
        self.canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill=current_scheme.background_color,
            outline="",
            tags="table_background",
        )

        # Draw table rail (outer ring)
        self.canvas.create_oval(
            width * 0.08,
            height * 0.12,
            width * 0.92,
            height * 0.88,
            fill=current_scheme.rail_color,
            outline=current_scheme.border_color,
            width=6,
            tags="table_rail",
        )

        # Draw table felt with texture and lighting effects
        self._draw_textured_felt(current_scheme, width, height)

        # Add gold inlay if specified
        if current_scheme.has_gold_inlay:
            self._draw_gold_inlay(width, height)

        # Apply lighting effects
        self._apply_lighting_effects(current_scheme, width, height)

        # Draw player seats
        self._draw_player_seats()

        # Draw community card area
        self._draw_community_card_area()

        # Draw pot display
        self._draw_pot_display()

        # Mark table as drawn and store canvas size
        self.table_drawn = True
        self.last_canvas_size = current_size

    def _draw_textured_felt(self, scheme, width, height):
        """Draw felt surface with texture based on scheme type."""
        felt_x1, felt_y1 = width * 0.12, height * 0.18
        felt_x2, felt_y2 = width * 0.88, height * 0.82

        if scheme.texture_type == "gradient":
            # Create gradient effect
            self._draw_gradient_felt(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "suede":
            # Suede texture with subtle noise
            self._draw_suede_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)
        elif scheme.texture_type == "diamond":
            # Diamond emboss pattern
            self._draw_diamond_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)
        elif scheme.texture_type == "microfiber":
            # Smooth microfiber finish
            self._draw_microfiber_felt(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "velvet":
            # Rich velvet texture
            self._draw_velvet_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)
        elif scheme.texture_type == "satin":
            # Satin finish with subtle sheen
            self._draw_satin_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)
        elif scheme.texture_type == "ripple":
            # Ripple emboss pattern
            self._draw_ripple_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)
        elif scheme.texture_type == "diamond_weave_pro":
            # Professional diamond weave with suit watermarks
            self._draw_diamond_weave_pro(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "championship_luxury":
            # WSOP championship luxury texture
            self._draw_championship_luxury(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "carbon_fiber_tech":
            # High-tech carbon fiber weave
            self._draw_carbon_fiber_tech(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "luxury_crosshatch":
            # Luxury crosshatch pattern
            self._draw_luxury_crosshatch(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        elif scheme.texture_type == "speed_cloth_pro":
            # Professional speed cloth with suit emboss
            self._draw_speed_cloth_pro(
                scheme, felt_x1, felt_y1, felt_x2, felt_y2
            )
        else:
            # Default solid felt
            self._draw_solid_felt(scheme, felt_x1, felt_y1, felt_x2, felt_y2)

    def _draw_solid_felt(self, scheme, x1, y1, x2, y2):
        """Draw basic solid felt surface."""
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )
        # Inner border for definition
        self.canvas.create_oval(
            x1 + 10,
            y1 + 10,
            x2 - 10,
            y2 - 10,
            fill=scheme.felt_color,
            outline=scheme.rail_color,
            width=1,
            tags="table_felt_inner",
        )

    def _draw_gradient_felt(self, scheme, x1, y1, x2, y2):
        """Draw gradient felt from edge to center."""
        # Create multiple rings for gradient effect
        colors = scheme.gradient_colors
        if len(colors) < 2:
            colors = [
                scheme.felt_color,
                self._lighten_color(scheme.felt_color, 0.1),
            ]

        # Outer ring (darker)
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=colors[0],
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )
        # Inner ring (lighter)
        ring_width = min((x2 - x1), (y2 - y1)) * 0.15
        self.canvas.create_oval(
            x1 + ring_width,
            y1 + ring_width,
            x2 - ring_width,
            y2 - ring_width,
            fill=colors[1],
            outline="",
            width=0,
            tags="table_felt_gradient",
        )

    def _draw_suede_felt(self, scheme, x1, y1, x2, y2):
        """Draw suede texture with subtle variations."""
        # Base felt
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Add subtle texture variations
        import random

        random.seed(42)  # Consistent pattern

        # Create small oval variations for suede texture
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        radius_x, radius_y = (x2 - x1) / 3, (y2 - y1) / 3

        for i in range(20):  # Subtle texture spots
            angle = i * 18  # Degrees
            import math

            spot_x = center_x + radius_x * 0.6 * math.cos(math.radians(angle))
            spot_y = center_y + radius_y * 0.6 * math.sin(math.radians(angle))

            # Very subtle color variation
            texture_color = self._darken_color(scheme.felt_color, 0.02)
            self.canvas.create_oval(
                spot_x - 3,
                spot_y - 2,
                spot_x + 3,
                spot_y + 2,
                fill=texture_color,
                outline="",
                tags="table_felt_texture",
            )

    def _draw_diamond_felt(self, scheme, x1, y1, x2, y2):
        """Draw diamond emboss pattern."""
        # Base felt
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Diamond pattern overlay
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        diamond_size = 15

        # Create diamond grid
        for row in range(-3, 4):
            for col in range(-5, 6):
                diamond_x = center_x + col * diamond_size * 1.5
                diamond_y = center_y + row * diamond_size * 1.5

                # Only draw diamonds within the oval
                if self._point_in_oval(diamond_x, diamond_y, x1, y1, x2, y2):
                    # Subtle diamond emboss
                    diamond_color = self._lighten_color(
                        scheme.felt_color, 0.03
                    )
                    self.canvas.create_polygon(
                        diamond_x,
                        diamond_y - diamond_size / 3,
                        diamond_x + diamond_size / 3,
                        diamond_y,
                        diamond_x,
                        diamond_y + diamond_size / 3,
                        diamond_x - diamond_size / 3,
                        diamond_y,
                        fill=diamond_color,
                        outline="",
                        tags="table_felt_diamond",
                    )

    def _draw_microfiber_felt(self, scheme, x1, y1, x2, y2):
        """Draw smooth microfiber texture."""
        # Base felt with smooth finish
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Subtle inner highlight for microfiber sheen
        highlight_color = self._lighten_color(scheme.felt_color, 0.05)
        self.canvas.create_oval(
            x1 + 20,
            y1 + 15,
            x2 - 20,
            y2 - 25,
            fill="",
            outline=highlight_color,
            width=1,
            tags="table_felt_microfiber",
        )

    def _draw_velvet_felt(self, scheme, x1, y1, x2, y2):
        """Draw rich velvet texture."""
        # Base felt
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Velvet has rich, deep appearance with subtle directional texture
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

        # Create subtle radial lines for velvet pile direction
        for angle in range(0, 360, 30):
            import math

            start_radius = min((x2 - x1), (y2 - y1)) * 0.2
            end_radius = min((x2 - x1), (y2 - y1)) * 0.35

            start_x = center_x + start_radius * math.cos(math.radians(angle))
            start_y = center_y + start_radius * math.sin(math.radians(angle))
            end_x = center_x + end_radius * math.cos(math.radians(angle))
            end_y = center_y + end_radius * math.sin(math.radians(angle))

            velvet_color = self._darken_color(scheme.felt_color, 0.02)
            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill=velvet_color,
                width=1,
                tags="table_felt_velvet",
            )

    def _draw_satin_felt(self, scheme, x1, y1, x2, y2):
        """Draw satin finish with subtle sheen."""
        # Base felt
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Satin diagonal sheen effect
        center_x = (x1 + x2) / 2
        sheen_color = self._lighten_color(scheme.felt_color, 0.08)

        # Diagonal stripe pattern for satin effect
        for i in range(-10, 11, 3):
            stripe_x1 = center_x + i * 20
            stripe_y1 = y1
            stripe_x2 = center_x + i * 20 + 50
            stripe_y2 = y2

            self.canvas.create_line(
                stripe_x1,
                stripe_y1,
                stripe_x2,
                stripe_y2,
                fill=sheen_color,
                width=1,
                tags="table_felt_satin",
            )

    def _draw_ripple_felt(self, scheme, x1, y1, x2, y2):
        """Draw ripple emboss pattern."""
        # Base felt
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Concentric ripple rings
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        max_radius = min((x2 - x1), (y2 - y1)) * 0.4

        ripple_color = self._lighten_color(scheme.felt_color, 0.04)

        for radius in range(20, int(max_radius), 25):
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="",
                outline=ripple_color,
                width=1,
                tags="table_felt_ripple",
            )

    def _draw_gold_inlay(self, width, height):
        """Draw gold thread inlay around table perimeter."""
        # Gold thread color
        gold_color = "#FFD700"

        # Outer gold ring
        self.canvas.create_oval(
            width * 0.115,
            height * 0.175,
            width * 0.885,
            height * 0.825,
            fill="",
            outline=gold_color,
            width=2,
            tags="table_gold_inlay",
        )

        # Inner gold accent
        self.canvas.create_oval(
            width * 0.135,
            height * 0.195,
            width * 0.865,
            height * 0.805,
            fill="",
            outline=gold_color,
            width=1,
            tags="table_gold_inner",
        )

    def _draw_diamond_weave_pro(self, scheme, x1, y1, x2, y2):
        """Draw professional diamond weave texture with suit watermarks (PokerStars style)."""
        # Base felt surface
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Diamond weave pattern
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        weave_color = self._lighten_color(scheme.felt_color, 0.03)

        # Create diamond grid pattern
        diamond_size = 30
        for i in range(-8, 9, 2):
            for j in range(-6, 7, 2):
                dx = center_x + i * diamond_size
                dy = center_y + j * diamond_size
        if self._point_in_oval(dx, dy, x1, y1, x2, y2):
            # Draw diamond shape
            self.canvas.create_polygon(
                dx,
                dy - diamond_size // 3,
                dx + diamond_size // 3,
                dy,
                dx,
                dy + diamond_size // 3,
                dx - diamond_size // 3,
                dy,
                fill=weave_color,
                outline="",
                width=1,
                tags="table_pattern",
            )

        # Subtle suit watermarks
        watermark_color = self._lighten_color(scheme.felt_color, 0.02)
        suit_positions = [
            (center_x - 80, center_y - 40, "♠"),
            (center_x + 80, center_y - 40, "♣"),
            (center_x - 80, center_y + 40, "♦"),
            (center_x + 80, center_y + 40, "♥"),
        ]

        for sx, sy, suit in suit_positions:
            if self._point_in_oval(sx, sy, x1, y1, x2, y2):
                self.canvas.create_text(
                    sx,
                    sy,
                    text=suit,
                    font=("Arial", 24, "bold"),
                    fill=watermark_color,
                    tags="table_watermark",
                )

    def _draw_championship_luxury(self, scheme, x1, y1, x2, y2):
        """Draw WSOP championship luxury texture with gold accents."""
        # Create radial gradient effect with multiple layers
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        radius = min((x2 - x1) / 2, (y2 - y1) / 2)

        # Multiple gradient rings for luxury effect
        colors = scheme.gradient_colors
        num_rings = 12
        for i in range(num_rings):
            factor = (num_rings - i) / num_rings
            ring_radius = radius * factor * 0.9
            color_index = int(i / num_rings * (len(colors) - 1))
            ring_color = colors[min(color_index, len(colors) - 1)]

            self.canvas.create_oval(
                center_x - ring_radius,
                center_y - ring_radius,
                center_x + ring_radius,
                center_y + ring_radius,
                fill=ring_color,
                outline="",
                tags="table_felt_gradient",
            )

        # Luxury crosshatch overlay
        crosshatch_color = self._darken_color(scheme.felt_color, 0.05)
        for i in range(-15, 16, 8):
            for j in range(-12, 13, 8):
                x, y = center_x + i * 20, center_y + j * 20
                if self._point_in_oval(x, y, x1, y1, x2, y2):
                    # Diagonal lines for crosshatch
                    self.canvas.create_line(
                        x - 15,
                        y - 15,
                        x + 15,
                        y + 15,
                        fill=crosshatch_color,
                        width=1,
                        tags="table_pattern",
                    )
                    self.canvas.create_line(
                        x - 15,
                        y + 15,
                        x + 15,
                        y - 15,
                        fill=crosshatch_color,
                        width=1,
                        tags="table_pattern",
                    )

    def _draw_carbon_fiber_tech(self, scheme, x1, y1, x2, y2):
        """Draw high-tech carbon fiber weave pattern."""
        # Base surface
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Carbon fiber weave pattern
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        fiber_light = self._lighten_color(scheme.felt_color, 0.08)
        fiber_dark = self._darken_color(scheme.felt_color, 0.05)

        # Horizontal fibers
        for i in range(-20, 21, 4):
            y = center_y + i * 8
            for j in range(-25, 26, 8):
                x = center_x + j * 8
                if self._point_in_oval(x, y, x1, y1, x2, y2):
                    self.canvas.create_rectangle(
                        x - 3,
                        y - 1,
                        x + 3,
                        y + 1,
                        fill=fiber_light,
                        outline="",
                        tags="table_pattern",
                    )

        # Vertical fibers (weaving effect)
        for i in range(-25, 26, 8):
            x = center_x + i * 8
            for j in range(-20, 21, 8):
                y = center_y + j * 8 + 4  # Offset for weave
                if self._point_in_oval(x, y, x1, y1, x2, y2):
                    self.canvas.create_rectangle(
                        x - 1,
                        y - 3,
                        x + 1,
                        y + 3,
                        fill=fiber_dark,
                        outline="",
                        tags="table_pattern",
                    )

        # Geometric accent lines
        tech_accent = self._lighten_color(scheme.felt_color, 0.15)
        for angle in [0, 45, 90, 135]:
            for radius_factor in [0.3, 0.5, 0.7]:
                self._draw_tech_accent_line(
                    center_x,
                    center_y,
                    angle,
                    radius_factor,
                    x1,
                    y1,
                    x2,
                    y2,
                    tech_accent,
                )

    def _draw_luxury_crosshatch(self, scheme, x1, y1, x2, y2):
        """Draw luxury crosshatch pattern for VIP tables."""
        # Base surface with gradient
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

        # Create gradient base
        colors = scheme.gradient_colors
        for i, color in enumerate(colors):
            factor = 0.9 - (i * 0.1)
            radius = min((x2 - x1) / 2, (y2 - y1) / 2) * factor
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill=color,
                outline="",
                tags="table_felt_gradient",
            )

        # Fine crosshatch pattern
        hatch_light = self._lighten_color(scheme.felt_color, 0.06)
        hatch_dark = self._darken_color(scheme.felt_color, 0.04)

        # Diagonal crosshatch grid
        spacing = 12
        for i in range(-30, 31, spacing):
            for j in range(-25, 26, spacing):
                x, y = center_x + i * 6, center_y + j * 6
                if self._point_in_table(x, y, x1, y1, x2, y2):
                    # Create small crosshatch square
                    self.canvas.create_line(
                        x - 4,
                        y - 4,
                        x + 4,
                        y + 4,
                        fill=hatch_light,
                        width=1,
                        tags="table_pattern",
                    )
                    self.canvas.create_line(
                        x - 4,
                        y + 4,
                        x + 4,
                        y - 4,
                        fill=hatch_dark,
                        width=1,
                        tags="table_pattern",
                    )

    def _draw_speed_cloth_pro(self, scheme, x1, y1, x2, y2):
        """Draw professional speed cloth with suit symbol embossing."""
        # Ultra-smooth base surface
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=scheme.felt_color,
            outline=scheme.border_color,
            width=3,
            tags="table_felt",
        )

        # Speed cloth texture (very subtle directional grain)
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        grain_color = self._lighten_color(scheme.felt_color, 0.02)

        # Horizontal speed lines for smooth card glide
        for i in range(-15, 16, 3):
            y = center_y + i * 10
            if y > y1 + 20 and y < y2 - 20:  # Stay within table bounds
                self.canvas.create_line(
                    x1 + 40,
                    y,
                    x2 - 40,
                    y,
                    fill=grain_color,
                    width=1,
                    tags="table_pattern",
                )

        # Embossed suit symbols around perimeter
        emboss_color = self._darken_color(scheme.felt_color, 0.03)
        suit_symbols = ["♠", "♥", "♦", "♣"]

        # Place suits around the table edge
        radius = min((x2 - x1) / 2, (y2 - y1) / 2) * 0.85
        for i, suit in enumerate(suit_symbols * 3):  # Repeat suits
            angle = (2 * 3.14159 / 12) * i
            sx = center_x + radius * 0.7 * math.cos(angle)
            sy = center_y + radius * 0.7 * math.sin(angle)

            if self._point_in_oval(sx, sy, x1, y1, x2, y2):
                self.canvas.create_text(
                    sx,
                    sy,
                    text=suit,
                    font=("Arial", 16, "bold"),
                    fill=emboss_color,
                    tags="table_emboss",
                )

    def _draw_tech_accent_line(
        self, center_x, center_y, angle, radius_factor, x1, y1, x2, y2, color
    ):
        """Draw geometric accent line for tech patterns."""
        import math

        radius = min((x2 - x1) / 2, (y2 - y1) / 2) * radius_factor

        # Calculate line endpoints
        rad = math.radians(angle)
        start_x = center_x + radius * 0.3 * math.cos(rad)
        start_y = center_y + radius * 0.3 * math.sin(rad)
        end_x = center_x + radius * math.cos(rad)
        end_y = center_y + radius * math.sin(rad)

        # Draw line if both points are within table
        if self._point_in_oval(
            start_x, start_y, x1, y1, x2, y2
        ) and self._point_in_oval(end_x, end_y, x1, y1, x2, y2):
            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill=color,
                width=2,
                tags="table_tech_accent",
            )

    def _apply_lighting_effects(self, scheme, width, height):
        """Apply lighting effects based on scheme."""
        if scheme.lighting_effect == "vignette":
            self._apply_vignette_effect(width, height)
        elif scheme.lighting_effect == "center_glow":
            self._apply_center_glow_effect(width, height, scheme.felt_color)
        elif scheme.lighting_effect == "tournament_spotlight":
            self._apply_tournament_spotlight(width, height, scheme.felt_color)
        elif scheme.lighting_effect == "tech_glow":
            self._apply_tech_glow_effect(width, height)
        elif scheme.lighting_effect == "vip_ambience":
            self._apply_vip_ambience_effect(width, height, scheme.felt_color)
        elif scheme.lighting_effect == "classic_vignette":
            self._apply_classic_vignette_effect(width, height)
        elif scheme.lighting_effect == "frosted_edge":
            self._apply_frosted_edge_effect(width, height)
        elif scheme.lighting_effect == "reflective_highlights":
            self._apply_reflective_highlights(width, height)

    def _apply_vignette_effect(self, width, height):
        """Apply subtle darkening around edges."""
        # Dark vignette overlay

        # Create multiple rings for smooth vignette
        for i in range(3):
            # Very subtle effect
            ring_offset = 5 + i * 8

            # This would need alpha blending in a real implementation
            # For now, we'll use slightly darker colors
            self.canvas.create_oval(
                width * 0.12 - ring_offset,
                height * 0.18 - ring_offset,
                width * 0.88 + ring_offset,
                height * 0.82 + ring_offset,
                fill="",
                outline=self._darken_color("#000000", 0.8),
                width=1,
                tags="table_vignette",
            )

    def _apply_center_glow_effect(self, width, height, base_color):
        """Apply center glow effect."""
        center_x, center_y = width * 0.5, height * 0.5
        glow_color = self._lighten_color(base_color, 0.15)

        # Center glow rings
        for radius in range(30, 80, 15):
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="",
                outline=glow_color,
                width=1,
                tags="table_center_glow",
            )

    def _apply_tournament_spotlight(self, width, height, felt_color):
        """Apply WSOP tournament spotlight effect."""
        center_x, center_y = width * 0.5, height * 0.5

        # Create bright center spotlight
        spotlight_color = self._lighten_color(felt_color, 0.2)
        spotlight_radius = min(width, height) * 0.15

        # Multiple spotlight rings for smooth gradient
        for i in range(8):
            factor = (8 - i) / 8
            radius = spotlight_radius * factor
            # Fade out towards edges

            # Create semi-transparent spotlight effect
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill=spotlight_color,
                outline="",
                tags="table_spotlight",
            )

    def _apply_tech_glow_effect(self, width, height):
        """Apply modern tech glow effect."""
        # Create subtle blue-white glow around table edge
        glow_color = "#4A9EFF"

        # Outer glow ring
        self.canvas.create_oval(
            width * 0.10,
            height * 0.16,
            width * 0.90,
            height * 0.84,
            fill="",
            outline=glow_color,
            width=2,
            tags="table_tech_glow",
        )

        # Inner accent glow
        inner_glow = self._lighten_color(glow_color, 0.3)
        self.canvas.create_oval(
            width * 0.13,
            height * 0.19,
            width * 0.87,
            height * 0.81,
            fill="",
            outline=inner_glow,
            width=1,
            tags="table_tech_inner_glow",
        )

    def _apply_vip_ambience_effect(self, width, height, felt_color):
        """Apply VIP table ambience lighting."""
        center_x, center_y = width * 0.5, height * 0.5

        # Warm golden ambience around the table
        ambience_color = "#FFD700"  # Gold

        # Create soft ambient glow
        for i in range(5):
            factor = (5 - i) / 5
            radius = min(width, height) * 0.4 * factor

            # Soft golden rim lighting
            rim_color = self._lighten_color(ambience_color, 0.1 * i)
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius * 0.8,
                center_x + radius,
                center_y + radius * 0.8,
                fill="",
                outline=rim_color,
                width=1,
                tags="table_vip_ambience",
            )

    def _apply_classic_vignette_effect(self, width, height):
        """Apply classic casino vignette effect."""
        # Darker edges fading to center
        vignette_color = "#000000"

        # Create multiple vignette rings
        for i in range(6):
            factor = 1.0 - (i * 0.08)  # Start from outside edge
            # Fade intensity

            # Calculate oval dimensions for vignette ring
            x1 = width * (0.5 - 0.4 * factor)
            y1 = height * (0.5 - 0.3 * factor)
            x2 = width * (0.5 + 0.4 * factor)
            y2 = height * (0.5 + 0.3 * factor)

            # Only draw outer rings for vignette effect
            if i < 3:  # Only outermost rings
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="",
                    outline=vignette_color,
                    width=1,
                    tags="table_vignette",
                )

    def _apply_frosted_edge_effect(self, width, height):
        """Apply frosted edge effect."""
        frost_color = "#FFFFFF"

        # Subtle white edge highlight
        self.canvas.create_oval(
            width * 0.12 + 2,
            height * 0.18 + 2,
            width * 0.88 - 2,
            height * 0.82 - 2,
            fill="",
            outline=frost_color,
            width=1,
            tags="table_frost",
        )

    def _apply_reflective_highlights(self, width, height):
        """Apply reflective highlight streaks."""
        highlight_color = "#666666"
        center_x, center_y = width * 0.5, height * 0.5

        # Diagonal highlight streaks
        import math

        for angle in [45, 135, 225, 315]:  # Diagonal angles
            length = min(width, height) * 0.15

            start_x = center_x - length / 2 * math.cos(math.radians(angle))
            start_y = center_y - length / 2 * math.sin(math.radians(angle))
            end_x = center_x + length / 2 * math.cos(math.radians(angle))
            end_y = center_y + length / 2 * math.sin(math.radians(angle))

            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill=highlight_color,
                width=2,
                tags="table_highlights",
            )

    # Utility methods for color manipulation
    def _lighten_color(self, hex_color, factor):
        """Lighten a hex color by a factor (0.0 to 1.0)."""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color, factor):
        """Darken a hex color by a factor (0.0 to 1.0)."""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _point_in_oval(self, px, py, x1, y1, x2, y2):
        """Check if a point is inside an oval."""
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        radius_x, radius_y = (x2 - x1) / 2, (y2 - y1) / 2

        # Normalize point to unit circle
        normalized_x = (px - center_x) / radius_x
        normalized_y = (py - center_y) / radius_y

        # Check if point is inside unit circle
        return (
            normalized_x**2 + normalized_y**2
        ) <= 0.8  # Slightly inside edge

    def change_table_felt(self, felt_color: str, scheme=None):
        """Change the table color scheme dynamically."""
        if scheme is not None:
            # Complete scheme provided (new system)
            felt_color = scheme.felt_color
            rail_color = scheme.rail_color
            border_color = scheme.border_color
            # background_color = scheme.background_color  # May be used for
            # outer areas
        elif felt_color.startswith("#"):
            # Direct hex color (legacy system)
            rail_color = THEME["table_rail"]  # Use theme default for rail
            border_color = THEME["primary_bg"]  # Use theme default for border
        else:
            # Legacy color names (for backward compatibility)
            table_felt_colors = {
                "classic_green": "#015939",
                "royal_blue": "#2d5aa0",
                "burgundy_red": "#8b2d2d",
                "deep_purple": "#5a2d8b",
                "golden_brown": "#8b6b2d",
                "ocean_blue": "#2d8b8b",
                "forest_green": "#2d8b2d",
                "midnight_black": "#2d2d2d",
            }
            felt_color = table_felt_colors.get(felt_color, THEME["table_felt"])
            rail_color = THEME["table_rail"]

        # Update THEME with new colors
        THEME["table_felt"] = felt_color
        THEME["table_rail"] = rail_color

        # Update existing table elements
        try:
            # Update background elements
            if scheme:
                for item in self.canvas.find_withtag("table_background"):
                    self.canvas.itemconfig(item, fill=scheme.background_color)

                # Update table rail elements
                for item in self.canvas.find_withtag("table_rail"):
                    self.canvas.itemconfig(item, fill=scheme.rail_color)

                # Update table felt elements
                for item in self.canvas.find_withtag("table_felt"):
                    self.canvas.itemconfig(item, fill=scheme.felt_color)
                for item in self.canvas.find_withtag("table_felt_inner"):
                    self.canvas.itemconfig(item, fill=scheme.felt_color)
            else:
                # Legacy single color update
                for item in self.canvas.find_withtag("table_felt"):
                    self.canvas.itemconfig(item, fill=felt_color)
                for item in self.canvas.find_withtag("table_felt_inner"):
                    self.canvas.itemconfig(item, fill=felt_color)

            # Force a complete redraw to ensure all elements use new colors
            self._draw_table()
        except Exception as e:
            debug_log(f"Error changing table scheme: {e}", "TABLE_APPEARANCE")

    def _draw_player_seats(self):
        """Draw player seats around the table (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        # Use default size if canvas not ready
        if width <= 1 or height <= 1:
            width, height = 800, 600
            # Using default canvas size for seat positioning

        # Check if seats already exist and canvas size hasn't changed
        current_size = (width, height)
        if (
            hasattr(self, "player_seats")
            and self.player_seats
            and all(seat is not None for seat in self.player_seats)
            and hasattr(self, "last_seats_canvas_size")
            and self.last_seats_canvas_size == current_size
        ):
            # Skipping player seats redraw - already exist and no size changes
            return

        # Drawing player seats

        # Get dynamic positions based on current display state
        dynamic_positions = self._get_dynamic_player_positions()
        num_players = len(dynamic_positions)

        # Initialize player seats list for actual number of players
        self.player_seats = [None] * num_players

        # Use layout manager for positioning
        player_positions = self.layout_manager.calculate_player_positions(
            width, height, num_players, widget=self
        )

        for i in range(num_players):
            seat_x, seat_y = player_positions[i]
            player_name = dynamic_positions[i].get("name", f"Player {i + 1}")
            player_position = dynamic_positions[i].get("position", "")
            self._create_player_seat_widget(
                seat_x, seat_y, player_name, player_position, i
            )

        # Store canvas size for next comparison
        self.last_seats_canvas_size = current_size

    def _get_dynamic_player_positions(self):
        """Get dynamic player positions from current display state (NO HARDCODING)."""
        # If we have display state, use actual player data
        if hasattr(self, "last_display_state") and self.last_display_state:
            players = self.last_display_state.get("players", [])
            if players:

                return [
                    {
                        "name": player.get("name", f"Player {i + 1}"),
                        "position": player.get("position", ""),
                    }
                    for i, player in enumerate(players)
                ]

        # If we have a poker game config (from FPSM), use that
        if hasattr(self, "poker_game_config") and self.poker_game_config:
            num_players = getattr(self.poker_game_config, "num_players", 6)

            return [
                {
                    "name": f"Player {i + 1}",
                    "position": self._calculate_position_for_seat(
                        i, num_players
                    ),
                }
                for i in range(num_players)
            ]

        # Default fallback for 6 players with calculated positions
        default_num_players = 6

        return [
            {
                "name": f"Player {i + 1}",
                "position": self._calculate_position_for_seat(
                    i, default_num_players
                ),
            }
            for i in range(default_num_players)
        ]

    def _calculate_position_for_seat(
        self, seat_index: int, total_players: int
    ) -> str:
        """Calculate position name based on seat index and total players (DYNAMIC)."""
        if total_players == 2:
            # Heads-up: Seat 0 = Small Blind/Button, Seat 1 = Big Blind
            return "SB/BTN" if seat_index == 0 else "BB"
        elif total_players == 3:
            # 3-handed
            positions = ["BTN", "SB", "BB"]
            return positions[seat_index] if seat_index < len(positions) else ""
        elif total_players == 4:
            # 4-handed
            positions = ["UTG", "BTN", "SB", "BB"]
            return positions[seat_index] if seat_index < len(positions) else ""
        elif total_players == 5:
            # 5-handed
            positions = ["UTG", "CO", "BTN", "SB", "BB"]
            return positions[seat_index] if seat_index < len(positions) else ""
        elif total_players >= 6:
            # 6+ handed (standard)
            positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
            if total_players > 6:
                # For more than 6 players, add more MP positions
                positions = (
                    ["UTG"]
                    + [f"MP{i}" for i in range(1, total_players - 4)]
                    + ["CO", "BTN", "SB", "BB"]
                )
            return (
                positions[seat_index]
                if seat_index < len(positions)
                else f"Seat{seat_index + 1}"
            )
        else:
            return f"Seat{seat_index + 1}"

    def _create_player_seat_widget(self, x, y, name, position, index):
        """Create a modern player seat widget with professional card room aesthetics."""
        # Create a frame for the player pod with modern styling
        player_frame = tk.Frame(
            self.canvas,
            bg=THEME["secondary_bg"],
            highlightbackground=THEME["border_inactive"],
            highlightthickness=2,
            relief="solid",
            bd=1,
        )

        # Create info frame for name and cards with modern colors - increased
        # padding
        info_frame = tk.Frame(player_frame, bg=THEME["secondary_bg"])
        info_frame.pack(pady=(10, 2), padx=15)

        # Create name label with larger font for better readability
        name_font = THEME.get("player_name", ("Segoe UI", 13, "bold"))
        if isinstance(name_font, tuple) and len(name_font) >= 2:
            larger_font = (
                name_font[0],
                name_font[1] + 2,
                name_font[2] if len(name_font) > 2 else "bold",
            )
        else:
            larger_font = ("Segoe UI", 15, "bold")

        name_label = tk.Label(
            info_frame,
            text=f"{name} ({position})",
            font=larger_font,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
        )
        name_label.pack(fill="x")

        # Create cards frame with modern styling
        cards_frame = tk.Frame(info_frame, bg=THEME["secondary_bg"])
        cards_frame.pack(pady=(8, 12), padx=10)

        # Create card widgets with improved sizing
        card1 = CardWidget(cards_frame, width=55, height=75)
        card1.pack(side="left", padx=4)
        card2 = CardWidget(cards_frame, width=55, height=75)
        card2.pack(side="left", padx=4)

        # Create stack frame with modern styling
        stack_frame = tk.Frame(player_frame, bg=THEME["secondary_bg"])
        stack_frame.pack()

        # Create stack label with modern font and gold color
        # Get starting stack from poker game config if available
        default_stack = 200  # fallback default
        if hasattr(self, "poker_game_config") and self.poker_game_config:
            default_stack = getattr(
                self.poker_game_config, "starting_stack", 200
            )

        stack_label = tk.Label(
            stack_frame,
            # Use config-based starting stack, will be updated by state machine
            # data
            text=f"${int(default_stack)}",
            font=THEME.get("stack_amount", ("Segoe UI", 16, "bold")),
            bg=THEME["secondary_bg"],
            fg=THEME["text_gold"],
        )
        stack_label.pack(fill="x", pady=(0, 4))

        # Create bet label with modern styling
        bet_label = tk.Label(
            stack_frame,
            text="",
            font=THEME.get("bet_amount", ("Segoe UI", 12, "bold")),
            bg=THEME["secondary_bg"],
            fg=THEME["text_gold"],
        )
        bet_label.pack(fill="x", pady=(0, 8))

        # Store references for updates
        self.player_seats[index] = {
            "frame": player_frame,
            "name_label": name_label,
            "cards_frame": cards_frame,
            "card_widgets": [card1, card2],
            "stack_label": stack_label,
            "bet_label": bet_label,
            "position": (x, y),
            "dealer_button": None,  # Will store dealer button widget
        }

        # Position the player frame
        self.canvas.create_window(x, y, window=player_frame, anchor="center")

    def _create_dealer_button(self, player_index: int):
        """Create a dealer button next to the specified player."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
            or not self.player_seats[player_index].get("position")
        ):
            return

        player_x, player_y = self.player_seats[player_index]["position"]

        # Position dealer button to the right of the player seat
        button_x = player_x + 100  # 100 pixels to the right
        button_y = player_y

        # Create a modern dealer button with professional styling
        button_frame = tk.Frame(
            self.canvas,
            bg=THEME["accent"],  # Use accent color (gold/orange)
            highlightbackground="#FFD700",  # Gold border
            highlightthickness=2,
            relief="raised",
            bd=2,
            width=35,
            height=35,
        )

        # Create the "D" label for dealer
        dealer_label = tk.Label(
            button_frame,
            text="D",
            font=("Segoe UI", 14, "bold"),
            bg=THEME["accent"],
            fg="white",
            width=2,
            height=1,
        )
        dealer_label.pack(expand=True)

        # Position on canvas
        canvas_item = self.canvas.create_window(
            button_x,
            button_y,
            window=button_frame,
            anchor="center",
            tags="dealer_button",
        )

        # Store reference
        self.player_seats[player_index]["dealer_button"] = {
            "frame": button_frame,
            "label": dealer_label,
            "canvas_item": canvas_item,
        }

    def _remove_dealer_button(self, player_index: int):
        """Remove dealer button from the specified player."""
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
            or not self.player_seats[player_index].get("dealer_button")
        ):
            return

        dealer_button = self.player_seats[player_index]["dealer_button"]
        if dealer_button:
            # Remove from canvas
            if dealer_button.get("canvas_item"):
                self.canvas.delete(dealer_button["canvas_item"])
            # Destroy the frame
            if dealer_button.get("frame"):
                dealer_button["frame"].destroy()
            # Clear reference
            self.player_seats[player_index]["dealer_button"] = None

    def _update_dealer_button_display(self):
        """Update dealer button display based on current dealer position."""
        if (
            not hasattr(self, "last_display_state")
            or not self.last_display_state
        ):
            return

        dealer_position = self.last_display_state.get("dealer_position", -1)

        # Remove all existing dealer buttons
        for i in range(len(self.player_seats)):
            if self.player_seats[i]:
                self._remove_dealer_button(i)

        # Add dealer button to current dealer
        if 0 <= dealer_position < len(self.player_seats):
            self._create_dealer_button(dealer_position)

    class LayoutManager:
        """Manages dynamic positioning for the poker table."""

        def __init__(self):
            self.min_spacing = 20

        def calculate_player_positions(self, width, height, num_players, widget=None):
            """Calculate player seat positions with improved spacing for center area."""
            center_x, center_y = width / 2, height / 2

            # More compact radius for better space utilization
            base_radius_x = (
                width * 0.35
            )  # Reduced from 0.42 for compact layout
            base_radius_y = (
                height * 0.28
            )  # Reduced from 0.35 for compact layout

            # Adjust for different player counts
            if num_players <= 4:
                radius_x = base_radius_x * 0.85
                radius_y = base_radius_y * 0.85
            elif num_players <= 6:
                radius_x = base_radius_x
                radius_y = base_radius_y
            else:
                radius_x = base_radius_x * 1.05
                radius_y = base_radius_y * 1.05

            positions = []
            for i in range(num_players):
                angle = (2 * math.pi / num_players) * i - (math.pi / 2)
                x = center_x + radius_x * math.cos(angle)
                y = center_y + radius_y * math.sin(angle)
                
                # Apply GTO-specific positioning adjustments only for GTO widgets
                # Check if widget is provided and is a GTO widget
                is_gto_widget = widget and hasattr(widget, '_is_gto_widget') and widget._is_gto_widget
                if is_gto_widget and num_players >= 4:
                    # Move side players up for better spacing
                    if i == 1 or (num_players >= 6 and i == 4):
                        # Move side players up by reducing Y coordinate  
                        y -= height * 0.04  # Move up by 4% of table height
                    # Move bottom player(s) down to create space for pot
                    elif (num_players == 4 and i == 2) or (num_players == 5 and i == 3) or (num_players >= 6 and i == 3):
                        # Move bottom center player down to create pot space
                        y += height * 0.05  # Move down by 5% of table height
                    # For 8-9 players, also adjust additional positions
                    elif num_players >= 8:
                        if i == 2 or i == 7:
                            y -= height * 0.02  # Move upper side players up slightly
                        elif i == 5:  # Bottom player in 8-9 player games
                            y += height * 0.03  # Move bottom player down
                
                positions.append((x, y))

            return positions

        def calculate_community_card_position(self, width, height):
            """Calculate community card position with safe spacing from pot."""
            # Position community cards slightly above center to make room for pot below
            center_x, center_y = width / 2, height / 2
            community_y = center_y - max(50, height * 0.08)  # Moved up slightly more
            return center_x, community_y

        def calculate_pot_position(self, width, height, widget=None):
            """Calculate pot position with conditional spacing based on widget type."""
            center_x, center_y = width / 2, height / 2
            
            # Use different pot positioning for GTO vs Practice sessions
            is_gto_widget = widget and hasattr(widget, '_is_gto_widget') and widget._is_gto_widget
            if is_gto_widget:
                # GTO: Move pot up closer to community cards (reduced spacing)
                pot_y = center_y + max(35, height * 0.06)  # Tighter spacing for GTO
            else:
                # Practice: Use original spacing for familiar layout
                pot_y = center_y + max(48, height * 0.07)  # Original spacing
            
            return center_x, pot_y

    def animate_pot_to_multiple_winners(
        self, winner_names, share_amount, total_pot
    ):
        """Animate split pot to multiple winners equally."""
        try:
            pot_x = self.canvas.winfo_width() // 2
            pot_y = self.canvas.winfo_height() // 2 + 50
            # Map names to seat positions
            seat_targets = []
            for name in winner_names:
                idx = -1
                for i, seat in enumerate(self.player_seats):
                    if seat and seat.get("name_label"):
                        player_name = seat["name_label"].cget("text")
                        clean_name = player_name.split(" (")[0]
                        if clean_name == name:
                            idx = i
                            break
                if idx >= 0:
                    seat_targets.append(
                        (idx, self.player_seats[idx]["position"])
                    )
            if not seat_targets:
                debug_log(
                    "Split pot: no targets found; skipping", "POT_ANIMATION"
                )
                return
            # Launch chips to each winner
            max_delay = 0
            for n, (idx, (wx, wy)) in enumerate(seat_targets):
                num_chips = min(max(1, int(share_amount / 50)), 4)
                for i in range(num_chips):
                    delay = (i * 100) + (n * 120)  # stagger by winner too
                    max_delay = max(max_delay, delay)
                    self._animate_single_chip_to_winner(
                        pot_x, pot_y, wx, wy, share_amount / num_chips, delay
                    )
                # Flash each winner a bit later
                self.after(
                    max_delay + 400,
                    lambda seat_index=idx: self._flash_winner_stack(
                        seat_index
                    ),
                )
            # Sound once
            self.play_sound("winner")
        except Exception as e:
            debug_log(f"Error animating split pot: {e}", "POT_ANIMATION")
