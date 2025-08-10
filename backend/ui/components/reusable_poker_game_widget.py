#!/usr/bin/env python3
"""
Reusable Poker Game Widget

This widget provides a complete poker table interface that is solely driven by the FPSM's display state.
It's designed to be used for both simulation and practice sessions, with no independent decision-making.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, Any, List
import time

# Import shared components
from .card_widget import CardWidget

# Import theme
from core.gui_models import THEME

# Import sound manager
from utils.sound_manager import SoundManager

# Import FPSM components
from core.flexible_poker_state_machine import EventListener, GameEvent

# Import session logger for comprehensive logging
from core.session_logger import get_session_logger


class ReusablePokerGameWidget(ttk.Frame, EventListener):
    """
    A reusable poker game widget that provides a complete poker table interface 
    that is solely driven by the FPSM's display state.
    It's designed to be used for both simulation and practice sessions, 
    with no independent decision-making.
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the reusable poker game widget."""
        ttk.Frame.__init__(self, parent, **kwargs)
        EventListener.__init__(self)
        
        # Store the state machine
        self.state_machine = state_machine
        
        # Event loop detection to prevent infinite loops
        self.event_history = []
        self.max_event_history = 100
        self.last_round_complete_time = 0
        self.min_round_complete_interval = 0.1  # Minimum 100ms between round_complete events
        
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
        self.player_bet_displays = {}  # Store bet display widgets for each player
        
        # Sound manager
        self.sound_manager = SoundManager()
        
        # Animation protection flag
        self.animating_bets_to_pot = False
        
        # Display state tracking for lazy redrawing
        self.last_display_state = None
        self.last_action_player = -1
        self.table_drawn = False
        
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
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
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
    
    def _should_update_display(self, player_index: int, old_cards: list, new_cards: list) -> bool:
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
    
    def _should_update_community_cards(self, old_cards: list, new_cards: list) -> bool:
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
    
    def _customize_player_styling(self, player_index: int, player_info: dict) -> dict:
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
            'highlight': False,
            'background': None,
            'border_color': None,
            'text_color': None
        }
    
    def _handle_card_interaction(self, player_index: int, card_index: int, card: str):
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
        print("🔄 Resetting change tracking for new hand")
        self.last_player_states.clear()
        self.last_pot_amount = 0.0
        if hasattr(self, 'last_board_cards'):
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
                {"config": str(config)}
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
        
        for i, (last_player, current_player) in enumerate(zip(last_players, current_players)):
            # Check key player attributes
            if (last_player.get("name") != current_player.get("name") or
                last_player.get("stack") != current_player.get("stack") or
                last_player.get("current_bet") != current_player.get("current_bet") or
                last_player.get("has_folded") != current_player.get("has_folded")):
                return True
            
            # Special handling for cards - don't trigger redraw if cards go from real to hidden
            last_cards = last_player.get("cards", [])
            current_cards = current_player.get("cards", [])
            
            # Only consider it a change if cards go from hidden/empty to real cards
            # Don't redraw when real cards become hidden (preserve visual state)
            if (last_cards != current_cards and 
                not (last_cards and current_cards == ["**", "**"])):  # Don't trigger on real→hidden
                return True
        
        return False  # No meaningful changes detected
    
    def _create_bet_display_for_player(self, player_index: int):
        """Create a bet display widget positioned in front of a player."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        # Calculate position between player and center of table
        player_seat = self.player_seats[player_index]
        player_x, player_y = player_seat["position"]
        
        # Position bet display closer to table center
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        
        # Bet display positioned 60% toward center from player
        bet_x = player_x + (center_x - player_x) * 0.6
        bet_y = player_y + (center_y - player_y) * 0.6
        
        # Create bet display widget
        bet_widget = tk.Label(
            self.canvas,
            text="",
            bg="#2c3e50",  # Dark blue background
            fg="gold",     # Gold text
            font=("Arial", 12, "bold"),
            bd=2,
            relief="raised",
            padx=8,
            pady=4
        )
        
        bet_window = self.canvas.create_window(bet_x, bet_y, window=bet_widget, anchor="center")
        
        # Store the bet display
        self.player_bet_displays[player_index] = {
            "widget": bet_widget,
            "window": bet_window,
            "amount": 0.0
        }
        
        # Initially hidden
        self.canvas.itemconfig(bet_window, state="hidden")
        
        print(f"💰 Created bet display for player {player_index} at ({bet_x:.0f}, {bet_y:.0f})")
    
    def _show_bet_display_for_player(self, player_index: int, action: str, amount: float):
        """Show money graphics in front of a player when they bet/call."""
        # Create bet display if it doesn't exist
        if player_index not in self.player_bet_displays:
            self._create_bet_display_for_player(player_index)
        
        if player_index not in self.player_bet_displays:
            return
        
        bet_display = self.player_bet_displays[player_index]
        bet_widget = bet_display["widget"]
        bet_window = bet_display["window"]
        
        if amount > 0:
            # Show the money amount in front of player
            bet_widget.config(text=f"💰 ${amount:,.0f}")
            self.canvas.itemconfig(bet_window, state="normal")
            bet_display["amount"] = amount
            print(f"💸 Showing ${amount:,.0f} in front of player {player_index}")
        else:
            # Hide for non-betting actions
            self.canvas.itemconfig(bet_window, state="hidden")
            bet_display["amount"] = 0.0
    
    def _clear_all_bet_displays_permanent(self):
        """Clear all bet displays for new hand."""
        print("🧹 Clearing all player bet displays")
        for player_index, bet_display in self.player_bet_displays.items():
            bet_window = bet_display["window"]
            self.canvas.itemconfig(bet_window, state="hidden")
            bet_display["amount"] = 0.0
        

    
    def on_event(self, event: GameEvent):
        """Handle events from the FPSM."""
        # Event logging is handled by specific event handlers, no console output needed
        
        # ENHANCED Event deduplication to prevent infinite loops
        if not hasattr(self, 'last_processed_events'):
            self.last_processed_events = {}
        if not hasattr(self, 'rapid_event_count'):
            self.rapid_event_count = {}
        
        # Create a more comprehensive unique key for this event
        event_data = getattr(event, 'data', {})
        player_name = event_data.get('player_name', getattr(event, 'player_name', ''))
        action = event_data.get('action', getattr(event, 'action', ''))
        amount = event_data.get('amount', getattr(event, 'amount', 0))
        
        event_key = f"{event.event_type}_{player_name}_{action}_{amount}"
        current_time = time.time()
        
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
                    print(f"🛑 BLOCKING rapid-fire event: {event.event_type} (#{self.rapid_event_count[event_key]}) within {time_diff*1000:.1f}ms")
                    return
                else:
                    print(f"⚠️  Skipping duplicate event: {event.event_type} (within {time_diff*1000:.1f}ms)")
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
            self._handle_hand_complete(event)
    
    def _handle_action_executed(self, event: GameEvent):
        """Handle action execution events - show bet amounts and play sounds."""
        if not hasattr(event, 'data') or not event.data:
            return
            
        action_type = event.data.get("action_type")
        amount = event.data.get("amount", 0.0)
        player_name = event.data.get("player_name", "Unknown")
        
        # Find player index by name
        player_index = -1
        if hasattr(self, 'state_machine') and self.state_machine and hasattr(self.state_machine, 'game_state'):
            for i, player in enumerate(self.state_machine.game_state.players):
                if player.name == player_name:
                    player_index = i
                    break
        
        # Action execution logging handled by session logger, no console output needed
        
        # Show bet amount for betting actions
        if action_type in ["bet", "raise", "call"] and amount > 0 and player_index >= 0:
            print(f"💰 Displaying bet ${amount:.2f} for player {player_index}")
            self.show_bet_display(player_index, action_type, amount)
        
        # Clear any existing action indicator for this player
        if player_index >= 0:
            # Player found, proceed with action indicator clearing
            # Action indicator cleared for player
            # Clear action indicator (you can enhance this later)
            pass
        
        # Play sound for the action
        if action_type and hasattr(self, 'play_sound'):
            sound_map = {
                "bet": "bet",
                "raise": "bet", 
                "call": "call",
                "check": "check",
                "fold": "fold",
                "all_in": "all_in"
            }
            if action_type.lower() in sound_map:
                self.play_sound(sound_map[action_type.lower()])
    
    def _log_event(self, event: GameEvent):
        """Log all events for debugging and analysis."""
        if not self.session_logger:
            return
        
        # Extract event data for logging
        event_data = {
            "event_type": event.event_type,
            "timestamp": time.time(),
            "player_name": getattr(event, 'player_name', None),
            "action": getattr(event, 'action', None),
            "amount": getattr(event, 'amount', 0.0),
            "data": event.data if hasattr(event, 'data') else {}
        }
        
        # Log system event
        self.session_logger.log_system(
            "INFO", 
            "GUI_EVENT", 
            f"GUI received {event.event_type} event", 
            event_data
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
        
        player_name = getattr(event, 'player_name', 'Unknown')
        action = getattr(event, 'action', None)
        amount = getattr(event, 'amount', 0.0)
        
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
                    if action and hasattr(action, 'value'):
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
                is_human=player_name == "Player 1"
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
                "current_street": self.current_street
            }
        )
    
    def _log_display_state_update(self, event: GameEvent):
        """Log display state updates for tracking UI changes."""
        if not self.session_logger:
            return
        
        display_state = event.data.get("display_state", {})
        
        # Log pot changes
        pot_amount = display_state.get("pot", 0.0)
        if pot_amount != self.last_pot_amount:
            pot_msg = (f"Pot updated from ${self.last_pot_amount:.2f} "
                      f"to ${pot_amount:.2f}")
            self.session_logger.log_system(
                "INFO", 
                "POT_UPDATE", 
                pot_msg, 
                {
                    "old_pot": self.last_pot_amount,
                    "new_pot": pot_amount,
                    "pot_change": pot_amount - self.last_pot_amount
                }
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
                    stack_msg = (f"{player_name} stack changed from "
                               f"${old_stack:.2f} to ${stack_amount:.2f}")
                    self.session_logger.log_system(
                        "INFO", 
                        "STACK_UPDATE", 
                        stack_msg, 
                        {
                            "player_name": player_name,
                            "old_stack": old_stack,
                            "new_stack": stack_amount,
                            "stack_change": stack_amount - old_stack
                        }
                    )
            
            self.last_player_stacks[player_name] = stack_amount
            
            # Track bet changes
            if player_name in self.last_player_bets:
                old_bet = self.last_player_bets[player_name]
                if current_bet != old_bet:
                    bet_msg = (f"{player_name} bet changed from "
                             f"${old_bet:.2f} to ${current_bet:.2f}")
                    self.session_logger.log_system(
                        "INFO", 
                        "BET_UPDATE", 
                        bet_msg, 
                        {
                            "player_name": player_name,
                            "old_bet": old_bet,
                            "new_bet": current_bet,
                            "bet_change": current_bet - old_bet
                        }
                    )
            
            self.last_player_bets[player_name] = current_bet
    
    def _log_card_reveal(self, player_name: str, cards: List[str], 
                        is_hole_cards: bool = True):
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
                "street": self.current_street
            }
        )
    
    def _log_hand_completion(self, winner: str, winning_hand: str, pot_size: float, 
                           showdown: bool = False):
        """Log hand completion events."""
        if not self.session_logger:
            return
        
        hand_msg = (f"Hand completed - Winner: {winner}, Hand: {winning_hand}, "
                   f"Pot: ${pot_size:.2f}")
        self.session_logger.log_system(
            "INFO", 
            "HAND_COMPLETE", 
            hand_msg, 
            {
                "winner": winner,
                "winning_hand": winning_hand,
                "pot_size": pot_size,
                "showdown": showdown,
                "street": self.current_street
            }
        )
    
    def _log_session_event(self, event_type: str, message: str, 
                          data: Dict[str, Any] = None):
        """Log general session events."""
        if not self.session_logger:
            return
        
        self.session_logger.log_system(
            "INFO", 
            "SESSION_EVENT", 
            message, 
            data or {}
        )
    
    def _render_from_display_state(self, display_state: Dict[str, Any]):
        """Render the widget based on the FPSM's display state (LAZY REDRAW OPTIMIZATION)."""
        
        # Protect ongoing bet animations (don't interrupt them with excessive redraws)
        if self.animating_bets_to_pot:
            print("🛡️ PROTECTING BET ANIMATION - skipping excessive redraw")
            return  # Don't redraw while animations are in progress
        
        # Rendering from FPSM display state with lazy redraw optimization
        
        # Only redraw table if needed (lazy optimization to prevent flicker)
        if not hasattr(self, '_table_drawn') or not self._table_drawn:
            self._draw_table()
            self._table_drawn = True
        
        # Update all players
        for i, player_info in enumerate(display_state.get("players", [])):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_from_display_state(i, player_info)
        
        # LAZY redraw community cards (only when changed)
        board_cards = display_state.get("board", [])
        # Filter out placeholder cards ("**") and ensure we have valid cards
        filtered_board_cards = [card for card in board_cards if card and card != "**" and len(card) >= 2]
        
        # Only update if cards actually changed
        if not hasattr(self, '_last_board_cards') or self._last_board_cards != filtered_board_cards:
            print(f"🎴 LAZY updating community cards: {getattr(self, '_last_board_cards', [])} → {filtered_board_cards}")
            if not hasattr(self, '_community_area_drawn') or not self._community_area_drawn:
                self._draw_community_card_area()
                self._community_area_drawn = True
            self._update_community_cards_from_display_state(filtered_board_cards)
            self._last_board_cards = filtered_board_cards[:]
        
        # LAZY redraw pot (only when changed)
        pot_amount = display_state.get("pot", 0.0)
        if not hasattr(self, '_last_pot_amount') or self._last_pot_amount != pot_amount:
            print(f"💰 LAZY updating pot display: ${getattr(self, '_last_pot_amount', 0)} → ${pot_amount:,.2f}")
            if not hasattr(self, '_pot_area_drawn') or not self._pot_area_drawn:
                self._draw_pot_display()
                self._pot_area_drawn = True
            self.update_pot_amount(pot_amount)
            self._last_pot_amount = pot_amount
        
        # Update current action player
        action_player_index = display_state.get("action_player", -1)
        if action_player_index >= 0 and action_player_index < len(self.player_seats):
            self._highlight_current_player(action_player_index)
    
    def _update_player_from_display_state(self, player_index: int, player_info: Dict[str, Any]):
        """Update a single player based on display state (FLICKER-FREE VERSION)."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        player_seat = self.player_seats[player_index]
        
        # Get current state for comparison
        last_state = self.last_player_states.get(player_index, {})
        
        # Extract new state
        name = player_info.get("name", f"Player {player_index+1}")
        position = player_info.get("position", "")
        stack_amount = player_info.get("stack", 1000.0)
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
            player_seat["stack_label"].config(text=f"${stack_amount:,.2f}")
            print(f"💰 Updated player {player_index} stack: ${stack_amount:,.2f}")
        
        # Only update bet if it changed
        bet_text = f"Bet: ${bet_amount:,.2f}" if bet_amount > 0 else ""
        if last_state.get("bet_text") != bet_text:
            player_seat["bet_label"].config(text=bet_text)
            if bet_amount > 0:
                print(f"💸 Updated player {player_index} bet: ${bet_amount:,.2f}")
                # Also show graphical money display for existing bets (like blinds)
                self._show_bet_display_for_player(player_index, "bet", bet_amount)
        
        # Always call card update method - let specialized widgets decide how to handle **
        last_cards = last_state.get("cards", [])
        if last_cards != cards:
            self._set_player_cards_from_display_state(player_index, cards)
            print(f"🎴 Updated player {player_index} cards: {last_cards} → {cards}")
        elif last_cards and cards == ["**", "**"]:
            # Still call the method - specialized widgets may want to override ** behavior
            self._set_player_cards_from_display_state(player_index, cards)
            print(f"🎴 Calling card update with hidden data: {cards} (specialized widgets may override)")
        
        # Only update folded status if it changed
        if last_state.get("has_folded", False) != has_folded:
            if has_folded:
                self._mark_player_folded(player_index)
                print(f"❌ Player {player_index} folded")
            else:
                # Player is no longer folded (new hand), restore normal card display
                self._restore_player_cards(player_index)
        
        # Store the current state for next comparison
        self.last_player_states[player_index] = {
            "name_text": name_text,
            "stack": stack_amount,
            "bet_text": bet_text,
            "cards": cards.copy() if cards else [],
            "has_folded": has_folded
        }
    
    def _set_player_cards_from_display_state(self, player_index: int, cards: List[str]):
        """Set player cards based on display state using extensibility hooks."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        card_widgets = self.player_seats[player_index]["card_widgets"]
        
        # Get current cards for change detection
        old_cards = [getattr(card_widgets[i], '_current_card', "") for i in range(min(2, len(card_widgets)))]
        
        # Ask child class if we should update
        if not self._should_update_display(player_index, old_cards, cards):
            print(f"🎴 HOOK: Child class blocked card update for player {player_index}")
            return
        
        if len(cards) >= 2 and len(card_widgets) >= 2:
            # Process each card through the hook system
            for i in range(2):
                original_card = cards[i] if i < len(cards) else ""
                
                # Transform card data through hook
                display_card = self._transform_card_data(player_index, original_card, i)
                
                # Check if card should be shown through hook
                should_show = self._should_show_card(player_index, display_card)
                
                # Get current card for change detection
                current_card = getattr(card_widgets[i], '_current_card', "")
                
                # Only update if changed
                if current_card != display_card:
                    try:
                        if should_show and display_card and display_card not in ["**", ""]:
                            # Show actual card
                            player_has_folded = False
                            if player_index < len(self.last_player_states) and self.last_player_states[player_index]:
                                player_has_folded = self.last_player_states[player_index].get("has_folded", False)
                            
                            card_widgets[i].set_card(display_card, is_folded=player_has_folded)
                            card_widgets[i]._current_card = display_card
                            print(f"🎴 HOOK: Player {player_index} card {i}: {current_card} → {display_card} (shown)")
                            
                            # Call interaction hook
                            self._handle_card_interaction(player_index, i, display_card)
                            
                        elif display_card == "**":
                            # Show card back (hook decided to keep as hidden)
                            player_has_folded = False
                            if player_index < len(self.last_player_states) and self.last_player_states[player_index]:
                                player_has_folded = self.last_player_states[player_index].get("has_folded", False)
                            
                            card_widgets[i].set_card("**", is_folded=player_has_folded)
                            card_widgets[i]._current_card = "**"
                            color = "GRAY" if player_has_folded else "RED"
                            print(f"🎴 HOOK: Player {player_index} card {i}: {current_card} → {color} card back")
                            
                        else:
                            # Empty card or hook decided to hide
                            card_widgets[i].set_card("", is_folded=False)
                            card_widgets[i]._current_card = ""
                            print(f"🎴 HOOK: Player {player_index} card {i}: {current_card} → empty")
                    
                    except tk.TclError:
                        # Widget was destroyed, skip
                        pass
                elif current_card and not should_show:
                    # Hook wants to hide a previously visible card
                    try:
                        card_widgets[i].set_card("", is_folded=False)
                        card_widgets[i]._current_card = ""
                        print(f"🎴 HOOK: Player {player_index} card {i}: {current_card} → hidden by hook")
                    except tk.TclError:
                        pass
    
    def _update_community_cards_from_display_state(self, board_cards: List[str]):
        """Update community cards based on display state (FLICKER-FREE VERSION)."""
        print(f"🎴 COMMUNITY CARD UPDATE: Input cards: {board_cards}")
        
        # Ensure community card widgets are created
        if not self.community_card_widgets:
            print(f"🎴 No community card widgets, creating them...")
            self._draw_community_card_area()
        
        if not self.community_card_widgets:
            print(f"❌ COMMUNITY CARD WIDGETS STILL NOT CREATED!")
            return
        
        print(f"🎴 Community card widgets exist: {len(self.community_card_widgets)} widgets")
        
        # Initialize tracking if not exists
        if not hasattr(self, 'last_board_cards'):
            self.last_board_cards = []
        
        # Check game state - don't show community cards during preflop
        current_state = None
        if hasattr(self, 'state_machine') and self.state_machine:
            if hasattr(self.state_machine, 'current_state'):
                current_state = str(self.state_machine.current_state)
            elif hasattr(self.state_machine, 'get_current_state'):
                current_state = str(self.state_machine.get_current_state())
        
        # Determine how many cards to show based on current state
        cards_to_show = 0
        if current_state:
            if 'PREFLOP_BETTING' in current_state:
                cards_to_show = 0  # No community cards during preflop
                print(f"🚫 Preflop: Showing {cards_to_show} community cards (state: {current_state})")
            elif 'FLOP' in current_state or 'DEAL_FLOP' in current_state:
                cards_to_show = 3  # Show first 3 cards during flop
                print(f"🎴 Flop: Showing {cards_to_show} community cards (state: {current_state})")
            elif 'TURN' in current_state or 'DEAL_TURN' in current_state:
                cards_to_show = 4  # Show first 4 cards during turn
                print(f"🎴 Turn: Showing {cards_to_show} community cards (state: {current_state})")
            elif 'RIVER' in current_state or 'DEAL_RIVER' in current_state:
                cards_to_show = 5  # Show all 5 cards during river
                print(f"🎴 River: Showing {cards_to_show} community cards (state: {current_state})")
            elif 'END_HAND' in current_state or 'SHOWDOWN' in current_state:
                cards_to_show = 5  # Show only 5 community cards during showdown/end
                print(f"🎴 Showdown/End: Showing {cards_to_show} community cards (state: {current_state})")
            else:
                cards_to_show = min(5, len(board_cards))  # Max 5 community cards for unknown states
                print(f"🎴 Other state: Showing {cards_to_show} community cards (state: {current_state})")
        
        # Limit board cards to only the first N cards that should be visible
        visible_board_cards = board_cards[:cards_to_show] if board_cards else []
        
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
        print(f"🎴 CHANGE CHECK: visible_board_cards={visible_board_cards}, last_board_cards={self.last_board_cards}")
        if not self._should_update_community_cards(self.last_board_cards, visible_board_cards):
            print(f"🎴 HOOK: Child class blocked community card update")
            return  # Child class decided not to update
        
        print(f"🎴 Board changed: {self.last_board_cards} → {visible_board_cards} (showing {cards_to_show}/{len(board_cards)} cards)")
        
        # EFFICIENT UPDATE: Only change cards that are different
        for i, card_widget in enumerate(self.community_card_widgets):
            try:
                current_card = getattr(card_widget, '_current_card', "")
                new_card = visible_board_cards[i] if i < len(visible_board_cards) else ""
                
                # Only update if the card has actually changed
                if current_card != new_card:
                    if new_card and new_card != "**":
                        # Set actual card
                        card_widget.set_card(new_card, is_folded=False)
                        card_widget._current_card = new_card
                        print(f"🎴 Updated community card {i}: {current_card} → {new_card}")
                    else:
                        # Set empty card (for cards beyond what should be shown)
                        card_widget.set_card("", is_folded=False)
                        card_widget._current_card = ""
                        print(f"🎴 Cleared community card {i}")
            except tk.TclError:
                # Widget was destroyed, skip
                pass
        
        # Update the tracking
        self.last_board_cards = visible_board_cards.copy()
    
    def _highlight_current_player(self, player_index):
        """Highlight the current action player with strong visual indication."""
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                
                # Check if this player has folded by looking for existing folded indicator
                has_folded_indicator = False
                for widget in player_frame.winfo_children():
                    if (hasattr(widget, '_action_indicator') and 
                        hasattr(widget, 'cget') and 
                        "FOLDED" in widget.cget('text')):
                        has_folded_indicator = True
                        break
                
                if i == player_index and not has_folded_indicator:
                    # STRONG highlighting for active player (only if not folded)
                    player_frame.config(
                        highlightbackground="#FFD700",  # Bright gold
                        highlightthickness=6,           # Much thicker border
                        bg="#2A2A00"                    # Darker background for contrast
                    )
                    # Add blinking effect for extra visibility
                    self._add_action_indicator(player_frame)
                elif not has_folded_indicator:
                    # Normal appearance for inactive players (only if not folded)
                    player_frame.config(
                        highlightbackground="#006400",  # Dark green
                        highlightthickness=2,
                        bg="#1a1a1a"                    # Normal background
                    )
                # Note: Folded players keep their gray styling set by _mark_player_folded
    
    def _add_action_indicator(self, player_frame):
        """Add a visual action indicator to the player frame."""
        # Create or update action indicator text
        for widget in player_frame.winfo_children():
            if hasattr(widget, '_action_indicator'):
                widget.destroy()  # Remove old indicator
        
        # Add "YOUR TURN" indicator
        action_label = tk.Label(
            player_frame,
            text="⚡ YOUR TURN ⚡",
            bg="#FFD700",
            fg="#000000",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2
        )
        action_label._action_indicator = True
        action_label.pack(side=tk.TOP, pady=2)
        
        # Start blinking animation
        self._blink_action_indicator(action_label, True)
    
    def _blink_action_indicator(self, label, visible=True):
        """Create a blinking effect for the action indicator."""
        if label.winfo_exists():
            if visible:
                label.config(bg="#FFD700", fg="#000000")
            else:
                label.config(bg="#FF4500", fg="#FFFFFF")  # Orange flash
            
            # Continue blinking every 500ms
            self.after(500, lambda: self._blink_action_indicator(label, not visible))
    
    def _clear_action_indicators(self, player_index=None):
        """Clear action indicators for a specific player or all players."""
        if player_index is not None:
            # Clear for specific player
            if player_index < len(self.player_seats) and self.player_seats[player_index]:
                player_frame = self.player_seats[player_index]["frame"]
                for widget in player_frame.winfo_children():
                    if hasattr(widget, '_action_indicator'):
                        # Action indicator cleared for player
                        widget.destroy()
        else:
            # Clear for all players
            for i, player_seat in enumerate(self.player_seats):
                if player_seat:
                    self._clear_action_indicators(i)
    
    def _mark_player_folded(self, player_index):
        """Mark a player as folded."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        # Mark cards as folded
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            card_widget.set_folded()
        
        # Remove any "YOUR TURN" indicator and add "FOLDED" indicator
        player_frame = self.player_seats[player_index]["frame"]
        
        # Remove any existing action indicators
        for widget in player_frame.winfo_children():
            if hasattr(widget, '_action_indicator'):
                widget.destroy()
        
        # Add "FOLDED" indicator with gray background
        folded_label = tk.Label(
            player_frame,
            text="💤 FOLDED 💤",
            bg="#808080",  # Gray background
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief="sunken",
            bd=2
        )
        folded_label._action_indicator = True
        folded_label.pack(side=tk.TOP, pady=2)
        
        # Change player frame to gray background to indicate folded
        player_frame.config(
            highlightbackground="#696969",  # Dark gray
            highlightthickness=2,
            bg="#404040"  # Dark gray background
        )
    
    def _restore_player_cards(self, player_index):
        """Restore player cards to normal display (unfold them)."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            # Restore the card to unfolded state if it has a card
            current_card = getattr(card_widget, '_current_card', "")
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
    
    def _handle_action_executed(self, event: GameEvent):
        """Handle action execution events."""
        # Action executed event handled
        
        action = event.action
        amount = event.amount
        player_name = event.player_name
        
        # Find player index by matching names more flexibly
        player_index = -1
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and player_seat.get("name_label"):
                seat_text = player_seat["name_label"].cget("text")
                # Extract just the player name part (before position)
                seat_name = seat_text.split(' (')[0]
                if player_name == seat_name or player_name in seat_text:
                    player_index = i
                    # Player found at specified index
                    break
        
        if player_index >= 0:
            # Clear "YOUR TURN" indicator for this player since they just acted
            self._clear_action_indicators(player_index)
            
            # Play sound based on action
            if action:
                if action.value == "fold":
                    self.play_sound("fold")
                elif action.value == "call":
                    self.play_sound("call")
                elif action.value == "bet":
                    self.play_sound("bet")
                elif action.value == "raise":
                    self.play_sound("raise")
                elif action.value == "check":
                    self.play_sound("check")
            
            # Show bet display in front of player (proper money graphics)
            if amount > 0:
                self._show_bet_display_for_player(player_index, action.value if action else "bet", amount)
        else:
            print(f"⚠️ Could not find player index for {player_name}")
    
    def _handle_state_change(self, event: GameEvent):
        """Handle state change events."""
        new_state = event.data.get("new_state", "")
        # State change event handled
        
        # Play sounds for street progression
        if "DEAL_FLOP" in new_state:
            self.play_sound("dealing")
            print("🎴 Flop dealt - playing dealing sound")
        elif "DEAL_TURN" in new_state:
            self.play_sound("dealing")
            print("🎴 Turn dealt - playing dealing sound")
        elif "DEAL_RIVER" in new_state:
            self.play_sound("dealing")
            print("🎴 River dealt - playing dealing sound")
        elif "SHOWDOWN" in new_state:
            self.play_sound("winner")
            print("🏆 Showdown - playing winner sound")
    
    def _handle_round_complete(self, event: GameEvent):
        """Handle round completion events."""
        street = event.data.get("street", "")
        
        # Loop detection: prevent rapid-fire round_complete events
        current_time = time.time()
        if current_time - self.last_round_complete_time < self.min_round_complete_interval:
            print(f"⚠️  Ignoring rapid round_complete event (street={street}) - too soon after last one")
            return
        
        self.last_round_complete_time = current_time
        
        # Track event history for loop detection
        self.event_history.append({'type': 'round_complete', 'street': street, 'time': current_time})
        if len(self.event_history) > self.max_event_history:
            self.event_history.pop(0)
        
        # Check for infinite loop (same street repeated too many times)
        recent_street_events = [e for e in self.event_history[-10:] if e['type'] == 'round_complete' and e['street'] == street]
        if len(recent_street_events) >= 5:
            print(f"🛑 INFINITE LOOP DETECTED: {street} round_complete repeated {len(recent_street_events)} times - STOPPING")
            return
        
        # Round complete event handled
        
        # Log round completion
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", 
                "ROUND_COMPLETE", 
                f"Round completed: {street}", 
                {
                    "street": street,
                    "current_street": self.current_street
                }
            )
        
        # Play sound for round completion
        self.play_sound("dealing")
        
        # Animate all player bets to pot during street transition
        if hasattr(self, 'state_machine') and self.state_machine:
            display_state = self.state_machine.get_game_info()
            players = display_state.get("players", [])
            
            # Round complete animation started
            
            # Set animation flag to protect bet displays
            self.animating_bets_to_pot = True
            
            # Animate each player's current bet to the pot
            animation_delay = 0
            for i, player in enumerate(players):
                current_bet = player.get("current_bet", 0)
                if current_bet > 0:
                    player_name = player.get('name', f'Player {i+1}')
                    print(f"💰 Scheduling animation: {player_name}'s ${current_bet:,.0f} to pot (delay: {animation_delay}ms)")
                    
                    # Schedule staggered animations
                    self.after(animation_delay, lambda idx=i, amt=current_bet: 
                             self._animate_bet_to_pot(idx, amt))
                    animation_delay += 300  # 300ms between each animation (more visible)
            
            # Clear all bet displays after all animations complete
            total_delay = animation_delay + 500  # Shorter delay for better responsiveness
            self.after(total_delay, lambda: self._finish_bet_animations())
            print(f"💰 Scheduled bet clearing in {total_delay}ms")
        
        # Animate street progression
        if street in ["flop", "turn", "river"]:
            # Get current board cards from display state
            if hasattr(self, 'state_machine') and self.state_machine:
                display_state = self.state_machine.get_game_info()
                board_cards = display_state.get("board", [])
                self.play_animation("street_progression", street_name=street, board_cards=board_cards)
    
    def _handle_hand_complete(self, event: GameEvent):
        """Handle hand completion events with pot-to-winner animation."""
        winner_info = event.data.get("winner_info", {})
        pot_amount = event.data.get("pot_amount", 0.0)
        
        print(f"🏆 Hand complete: {winner_info.get('name', 'Unknown')} wins ${pot_amount:.2f}")
        
        # Log hand completion
        if self.session_logger:
            winner_name = winner_info.get('name', 'Unknown')
            winning_hand = winner_info.get('hand_description', 'Unknown')
            
            self._log_hand_completion(
                winner=winner_name,
                winning_hand=winning_hand,
                pot_size=pot_amount,
                showdown=True
            )
        
        # Animate pot to winner
        if winner_info and pot_amount > 0:
            self.animate_pot_to_winner(winner_info, pot_amount)
        else:
            # Log to session logger instead of console
            if self.session_logger:
                self.session_logger.log_system(
                    "WARNING", 
                    "HAND_COMPLETE", 
                    "No valid winner info or pot amount for animation", 
                    {
                        "winner_info": winner_info,
                        "pot_amount": pot_amount,
                        "event_data": event.data
                    }
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
                    "street": self.current_street
                }
            )
        
        # Find player index by name
        if self.state_machine:
            for i, player in enumerate(self.state_machine.game_state.players):
                if player.name == player_name:
                    self._animate_player_action(i, action, amount)
                    break
    
    def _animate_player_action(self, player_index, action, amount):
        """Animate a player action."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        # Play sound
        if self.sound_manager:
            self.sound_manager.play_sound(action.lower())
        
        # Show bet display
        if amount > 0:
            self.show_bet_display(player_index, action, amount)
    
    def show_bet_display(self, player_index, action, amount):
        """Show an enhanced bet display for a player with chip graphics."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        player_seat = self.player_seats[player_index]
        
        # Remove any existing bet display first
        self._remove_bet_display(player_index)
        
        # Create enhanced bet display frame
        bet_frame = tk.Frame(self.canvas, bg="#1a1a1a", relief="raised", bd=2)
        
        # Create bet text with chip icon
        bet_text = f"💰 {action.upper()}"
        if amount > 0:
            bet_text += f" ${amount:.2f}"
        
        bet_label = tk.Label(
            bet_frame,
            text=bet_text,
            bg="gold",
            fg="black",
            font=("Arial", 12, "bold"),
            padx=8,
            pady=4
        )
        bet_label.pack()
        
        # Add chip stack visualization for larger bets
        if amount >= 10:
            chip_frame = tk.Frame(bet_frame, bg="#1a1a1a")
            chip_frame.pack(pady=2)
            
            # Show chip stacks based on amount
            chip_count = min(int(amount / 10), 5)  # Max 5 chip icons
            for i in range(chip_count):
                chip_label = tk.Label(
                    chip_frame,
                    text="🔴",  # Red chip icon
                    bg="#1a1a1a",
                    fg="red",
                    font=("Arial", 8)
                )
                chip_label.pack(side="left", padx=1)
        
        # Position the bet display near the player
        try:
            # Wait for the widget to be properly positioned
            self.canvas.update_idletasks()
            player_x = player_seat["position"][0]
            player_y = player_seat["position"][1] - 60  # Above player
            
            bet_window = self.canvas.create_window(player_x, player_y, window=bet_frame, anchor="center")
            
            # Store the bet display for later removal
            self.bet_labels[player_index] = bet_window
            
            # Make the bet display fade after showing for a few seconds
            self.after(3000, lambda: self._fade_bet_display(player_index))
            
        except Exception as e:
            print(f"⚠️ Error positioning bet display: {e}")
            # Fallback to simple positioning
            bet_window = self.canvas.create_window(100 + player_index * 80, 100, window=bet_frame)
            self.bet_labels[player_index] = bet_window
            self.after(3000, lambda: self._remove_bet_display(player_index))
    
    def _fade_bet_display(self, player_index):
        """Fade out a bet display before removing it."""
        if player_index in self.bet_labels:
            # Simple fade by changing to a dimmer color
            bet_window = self.bet_labels[player_index]
            try:
                widget = self.canvas.nametowidget(self.canvas.itemcget(bet_window, "window"))
                if widget:
                    # Change to a faded appearance
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(bg="gray", fg="darkgray")
                    # Remove after fade effect
                    self.after(500, lambda: self._remove_bet_display(player_index))
            except Exception:
                # If fade fails, just remove
                self._remove_bet_display(player_index)
    
    def _remove_bet_display(self, player_index):
        """Remove a bet display for a player."""
        if player_index in self.bet_labels:
            bet_window = self.bet_labels[player_index]
            self.canvas.delete(bet_window)
            del self.bet_labels[player_index]
    
    def _clear_all_bet_displays(self):
        """Clear all bet displays at once."""
        if self.animating_bets_to_pot:
            print("🧹 Skipping bet clearing - animation in progress")
            return
        print("🧹 Clearing all bet displays")
        for player_index in list(self.bet_labels.keys()):
            self._remove_bet_display(player_index)
    
    def _finish_bet_animations(self):
        """Finish bet animations and clear displays."""
        print("💰 Finishing bet animations - clearing displays")
        self.animating_bets_to_pot = False
        self._clear_all_bet_displays()
        self._clear_all_bet_displays_permanent()
        
        # Force a display update after animation completes
        print("🔄 Forcing display update after bet animation completion")
        self.after_idle(self._force_display_refresh)
    
    def _force_display_refresh(self):
        """Force a complete display refresh after animations."""
        print("🔄 Forcing complete display refresh")
        if hasattr(self, 'state_machine') and self.state_machine:
            # Force a complete canvas refresh
            print("🔄 Forcing canvas update and refresh")
            self.canvas.update()
            self.canvas.update_idletasks()
            
            # Force redraw all table components - reset all lazy redraw flags
            print("🔄 Force redrawing all components with complete table refresh")
            
            # Reset ALL drawing flags to force complete redraw
            self.table_drawn = False
            
            # Reset lazy redraw tracking for ALL components
            if hasattr(self, 'last_canvas_size'):
                delattr(self, 'last_canvas_size')
            if hasattr(self, 'last_community_canvas_size'):
                delattr(self, 'last_community_canvas_size')
            if hasattr(self, 'last_pot_canvas_size'):
                delattr(self, 'last_pot_canvas_size')
            
            # Force clear community card and pot existence flags
            if hasattr(self, 'community_card_widgets'):
                print("🔄 Clearing community card widgets for forced redraw")
                self.community_card_widgets = []
            if hasattr(self, 'pot_label'):
                print("🔄 Clearing pot label for forced redraw")
                self.pot_label = None
            if hasattr(self, 'last_seats_canvas_size'):
                delattr(self, 'last_seats_canvas_size')
            
            # Minimal forced redraw - let lazy optimization handle the rest
            # Only force what's absolutely necessary after clearing
            self._ensure_seats_created_and_update()
            
            # No need to manually trigger display state events - FPSM will emit them
            # when needed. This prevents duplicate rendering cycles.
            # Final canvas refresh
            print("🔄 Final canvas refresh completed")
            self.canvas.update()
    
    def update_pot_amount(self, amount):
        """Update the pot amount display (FLICKER-FREE VERSION)."""
        # Only update if pot amount actually changed
        if self.last_pot_amount != amount:
            if hasattr(self, 'pot_label') and self.pot_label:
                self.pot_label.config(text=f"${amount:,.2f}")
                print(f"💰 Updated pot: ${self.last_pot_amount:,.2f} → ${amount:,.2f}")
            else:
                # Pot display doesn't exist yet - ensure it's created
                print(f"💰 Creating pot display for amount: ${amount:,.2f}")
                self._draw_pot_display()
                if hasattr(self, 'pot_label') and self.pot_label:
                    self.pot_label.config(text=f"${amount:,.2f}")
            self.last_pot_amount = amount
    
    def play_sound(self, sound_type: str, **kwargs):
        """Play a sound effect."""
        if not self.sound_manager:
            print(f"🔇 No sound manager available for {sound_type}")
            return
        
        print(f"🔊 Playing sound: {sound_type}")
        
        # Map sound types to the appropriate SoundManager methods
        if sound_type in ["fold", "call", "bet", "raise", "check", "all_in"]:
            self.sound_manager.play_action_sound(sound_type)
        elif sound_type in ["dealing", "shuffle", "flip"]:
            self.sound_manager.play_card_sound(sound_type)
        elif sound_type in ["winner", "notification"]:
            self.sound_manager.play_ui_sound(sound_type)
        else:
            # Try to play as a generic sound
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
        if not hasattr(self, 'pot_frame') or player_index >= len(self.player_seats):
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
            pady=4
        )
        
        chip_window = self.canvas.create_window(player_x, player_y, window=chip_label)
        self.canvas.tag_raise(chip_window)  # Bring to front
        
        # Play chip movement sound
        self.play_sound("bet")
        
        # Animate the chip to the pot with smooth movement
        def move_chip_step(step=0):
            total_steps = 40  # Longer animation for visibility
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
                self.after(40, lambda: move_chip_step(step + 1))  # Slower frame rate
            else:
                # Animation complete - remove chip and update pot
                self.canvas.delete(chip_window)
                self._flash_pot_update(amount)
        
        move_chip_step()
    
    def _flash_pot_update(self, amount):
        """Flash the pot to indicate chips were added."""
        if self.pot_label:
            original_bg = self.pot_label.cget("bg")
            original_fg = self.pot_label.cget("fg")
            
            # Enhanced flash sequence for better visibility
            def flash_sequence(step=0):
                if step < 6:  # Flash 3 times
                    if step % 2 == 0:
                        self.pot_label.config(bg="gold", fg="black")  # Brighter flash
                    else:
                        self.pot_label.config(bg=original_bg, fg=original_fg)
                    self.after(150, lambda: flash_sequence(step + 1))  # 150ms per flash
                else:
                    self.pot_label.config(bg=original_bg, fg=original_fg)
            
            flash_sequence()
    
    def animate_pot_to_winner(self, winner_info, pot_amount):
        """Animate pot money moving to the winner's stack."""
        if not winner_info or pot_amount <= 0:
            return
        
        print(f"🏆 Animating ${pot_amount:.2f} to {winner_info.get('name', 'Unknown')}")
        
        # Find winner's seat
        winner_name = winner_info.get('name', '')
        winner_seat_index = -1
        
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and player_seat.get("name_label"):
                player_name = player_seat["name_label"].cget("text")
                # Extract player name (remove position info)
                clean_name = player_name.split(' (')[0]
                if clean_name == winner_name:
                    winner_seat_index = i
                    break
        
        if winner_seat_index == -1:
            print(f"⚠️ Could not find winner seat for {winner_name}")
            return
        
        # Get positions
        pot_x = self.canvas.winfo_width() // 2
        pot_y = self.canvas.winfo_height() // 2 + 50
        
        winner_seat = self.player_seats[winner_seat_index]
        winner_x, winner_y = winner_seat["position"]
        
        # Create multiple chips for large pots
        num_chips = min(max(1, int(pot_amount / 50)), 6)  # 1-6 chips
        
        for i in range(num_chips):
            self._animate_single_chip_to_winner(
                pot_x, pot_y, winner_x, winner_y, 
                pot_amount / num_chips, i * 100  # Stagger timing
            )
        
        # Play winner sound
        self.play_sound("winner")
        
        # Flash winner's stack after animation
        self.after(800, lambda: self._flash_winner_stack(winner_seat_index))
    
    def _animate_single_chip_to_winner(self, start_x, start_y, end_x, end_y, amount, delay):
        """Animate a single chip from pot to winner."""
        
        def start_animation():
            # Create winner chip
            winner_chip = tk.Label(
                self.canvas,
                text="🏆",
                bg="gold",
                fg="red",
                font=("Arial", 30, "bold"),
                bd=3,
                relief="raised",
                padx=6,
                pady=4
            )
            
            chip_window = self.canvas.create_window(start_x, start_y, window=winner_chip)
            self.canvas.tag_raise(chip_window)
            
            # Animate to winner
            def move_to_winner(step=0):
                total_steps = 30
                if step <= total_steps:
                    progress = step / total_steps
                    # Smooth easing
                    ease_progress = progress * progress * (3.0 - 2.0 * progress)
                    
                    x = start_x + (end_x - start_x) * ease_progress
                    y = start_y + (end_y - start_y) * ease_progress
                    
                    # Add celebratory bounce
                    if progress > 0.7:
                        bounce = math.sin((progress - 0.7) * 15) * 5
                        y += bounce
                    
                    self.canvas.coords(chip_window, x, y)
                    self.after(20, lambda: move_to_winner(step + 1))
                else:
                    # Animation complete
                    self.canvas.delete(chip_window)
            
            move_to_winner()
        
        # Start with delay for staggered effect
        self.after(delay, start_animation)
    
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
        if not self.player_seats or all(seat is None for seat in self.player_seats):
            self._draw_player_seats()
    
    def _ensure_seats_created_and_update(self):
        """Ensure seats are created and then update from FPSM (LAZY OPTIMIZATION)."""
        # Skip if seats already exist and match the expected count
        expected_player_count = None
        if hasattr(self, 'state_machine') and self.state_machine:
            expected_player_count = len(self.state_machine.game_state.players)
        elif hasattr(self, 'poker_game_config') and self.poker_game_config:
            expected_player_count = self.poker_game_config.num_players
            
        if (hasattr(self, 'player_seats') and 
            self.player_seats and 
            all(seat is not None for seat in self.player_seats) and
            expected_player_count and len(self.player_seats) == expected_player_count):
            # Seats already exist, proceeding to update
            self._update_from_fpsm_state()
            return
        
        # Ensuring seats are created and updating from FPSM
        
        # Force update to get actual canvas size
        self.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Canvas size determined for seat positioning
        
        # Check if canvas is ready - if not, use reasonable default size for creation
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, using default size for seat creation
            # Don't return - create seats anyway with default positioning
            pass
        
        # Force creation of player seats if needed
        if not self.player_seats or all(seat is None for seat in self.player_seats):
            # Creating player seats
            self._draw_player_seats()
        elif expected_player_count and len(self.player_seats) != expected_player_count:
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
        if hasattr(self, 'community_frame'):
            for child in self.community_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(font=("Arial", int(font_size * 0.8)))
        
        # Update player pod fonts
        for player_seat in self.player_seats:
            if player_seat and player_seat["frame"]:
                player_frame = player_seat["frame"]
                player_frame.update_font_size(font_size)
    
    def _draw_community_card_area(self):
        """Draw the community card area in the center (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Check if community card area already exists and canvas size hasn't changed
        current_size = (width, height)
        if (hasattr(self, 'community_frame') and 
            self.community_frame and 
            hasattr(self, 'community_card_widgets') and
            self.community_card_widgets and
            hasattr(self, 'last_community_canvas_size') and
            self.last_community_canvas_size == current_size):
            # Skipping community card area redraw - already exists and no size changes
            return
        
        # Drawing community card area
        
        # Use layout manager for positioning
        community_x, community_y = self.layout_manager.calculate_community_card_position(width, height)
        
        # Create community card frame
        community_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=0)
        
        # Create title
        community_title = tk.Label(
            community_frame,
            text="Community Cards",
            bg=THEME["secondary_bg"],
            fg="white",
            font=("Helvetica", 10, "bold")
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
        self.canvas.create_window(community_x, community_y, window=community_frame, anchor="center")
        
        # Store canvas size for next comparison
        self.last_community_canvas_size = current_size
    
    def _draw_pot_display(self):
        """Draw the pot display in the center (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Check if pot display already exists and canvas size hasn't changed
        current_size = (width, height)
        if (hasattr(self, 'pot_frame') and 
            self.pot_frame and 
            hasattr(self, 'last_pot_canvas_size') and
            self.last_pot_canvas_size == current_size):
            # Skipping pot display redraw - already exists and no size changes
            return
        
        # Drawing pot display
        
        # Use layout manager for positioning
        pot_x, pot_y = self.layout_manager.calculate_pot_position(width, height)
        
        # Create pot frame
        pot_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=0)
        
        # Create pot title
        pot_title = tk.Label(
            pot_frame,
            text="Pot",
            bg=THEME["secondary_bg"],
            fg="white",
            font=("Helvetica", 10, "bold")
        )
        pot_title.pack(pady=2)
        
        # Create pot amount label
        self.pot_label = tk.Label(
            pot_frame,
            text="$0.00",
            bg=THEME["secondary_bg"],
            fg="yellow",
            font=("Helvetica", 12, "bold")
        )
        self.pot_label.pack(pady=2)
        
        # Store the pot frame
        self.pot_frame = pot_frame
        self.canvas.create_window(pot_x, pot_y, window=pot_frame, anchor="center")
        
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
        if hasattr(self, 'last_canvas_size'):
            delattr(self, 'last_canvas_size')
        if hasattr(self, 'last_seats_canvas_size'):
            delattr(self, 'last_seats_canvas_size')
        if hasattr(self, 'last_pot_canvas_size'):
            delattr(self, 'last_pot_canvas_size')
        if hasattr(self, 'last_community_canvas_size'):
            delattr(self, 'last_community_canvas_size')
        
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
            print(f"🎴 FPSM returned cards for player {i}: {cards}")
        
        # Update players
        for i, player_info in enumerate(game_info.get("players", [])):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_from_display_state(i, player_info)
        
        # Update community cards
        board_cards = game_info.get("board", [])
        self._update_community_cards_from_display_state(board_cards)
        
        # Update pot
        pot_amount = game_info.get("pot", 0.0)
        self.update_pot_amount(pot_amount)
        
        # Update current action player
        action_player_index = game_info.get("action_player", -1)
        if action_player_index >= 0 and action_player_index < len(self.player_seats):
            self._highlight_current_player(action_player_index)
    
    def _setup_ui(self):
        """Set up the UI layout."""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create canvas for the poker table
        self.canvas = tk.Canvas(
            self,
            bg=THEME["primary_bg"],
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Initialize player seats (will be set dynamically based on actual player count)
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
        self.after(100, self._draw_table)
    
    def _draw_table(self):
        """Draw the poker table with felt design (LAZY REDRAW OPTIMIZATION)."""
        if not self.canvas or self.canvas.winfo_width() <= 1:
            self.after(100, self._draw_table)
            return
        
        # Check if table is already drawn and canvas size hasn't changed
        current_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
        if (hasattr(self, 'last_canvas_size') and 
            self.last_canvas_size == current_size and 
            self.table_drawn):
            # Skipping table redraw - no size changes detected
            return
            
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Drawing table
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw table felt
        self.canvas.create_oval(
            width*0.05, height*0.1, width*0.95, height*0.9, 
            fill="#0B6623", outline=THEME["border"], width=10
        )
        self.canvas.create_oval(
            width*0.06, height*0.11, width*0.94, height*0.89, 
            fill="#228B22", outline="#222222", width=2
        )
        
        # Draw player seats
        self._draw_player_seats()
        
        # Draw community card area
        self._draw_community_card_area()
        
        # Draw pot display
        self._draw_pot_display()
        
        # Mark table as drawn and store canvas size
        self.table_drawn = True
        self.last_canvas_size = current_size
    
    def _draw_player_seats(self):
        """Draw player seats around the table (LAZY REDRAW OPTIMIZATION)."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Use default size if canvas not ready
        if width <= 1 or height <= 1:
            width, height = 800, 600
            # Using default canvas size for seat positioning
        
        # Check if seats already exist and canvas size hasn't changed
        current_size = (width, height)
        if (hasattr(self, 'player_seats') and 
            self.player_seats and 
            all(seat is not None for seat in self.player_seats) and
            hasattr(self, 'last_seats_canvas_size') and
            self.last_seats_canvas_size == current_size):
            # Skipping player seats redraw - already exist and no size changes
            return
        
        # Drawing player seats
        
        # Get dynamic positions based on current display state
        dynamic_positions = self._get_dynamic_player_positions()
        num_players = len(dynamic_positions)
        
        # Initialize player seats list for actual number of players
        self.player_seats = [None] * num_players
        
        # Use layout manager for positioning
        player_positions = self.layout_manager.calculate_player_positions(width, height, num_players)
        
        for i in range(num_players):
            seat_x, seat_y = player_positions[i]
            player_name = dynamic_positions[i].get('name', f"Player {i+1}")
            player_position = dynamic_positions[i].get('position', '')
            self._create_player_seat_widget(seat_x, seat_y, player_name, player_position, i)
        
        # Store canvas size for next comparison
        self.last_seats_canvas_size = current_size
    
    def _get_dynamic_player_positions(self):
        """Get dynamic player positions from current display state (NO HARDCODING)."""
        # If we have display state, use actual player data
        if hasattr(self, 'last_display_state') and self.last_display_state:
            players = self.last_display_state.get('players', [])
            if players:

                return [
                    {
                        'name': player.get('name', f"Player {i+1}"),
                        'position': player.get('position', '')
                    }
                    for i, player in enumerate(players)
                ]
        
        # If we have a poker game config (from FPSM), use that
        if hasattr(self, 'poker_game_config') and self.poker_game_config:
            num_players = getattr(self.poker_game_config, 'num_players', 6)

            return [
                {
                    'name': f"Player {i+1}",
                    'position': self._calculate_position_for_seat(i, num_players)
                }
                for i in range(num_players)
            ]
        
        # Default fallback for 6 players with calculated positions
        default_num_players = 6

        return [
            {
                'name': f"Player {i+1}",
                'position': self._calculate_position_for_seat(i, default_num_players)
            }
            for i in range(default_num_players)
        ]
    
    def _calculate_position_for_seat(self, seat_index: int, total_players: int) -> str:
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
                positions = ["UTG"] + [f"MP{i}" for i in range(1, total_players-4)] + ["CO", "BTN", "SB", "BB"]
            return positions[seat_index] if seat_index < len(positions) else f"Seat{seat_index+1}"
        else:
            return f"Seat{seat_index+1}"
    
    def _create_player_seat_widget(self, x, y, name, position, index):
        """Create a player seat widget with all components controlled by RPGW."""
        # Create a frame for the player pod
        player_frame = tk.Frame(self.canvas, bg="#1a1a1a", highlightbackground="#006400", highlightthickness=2)
        
        # Create info frame for name and cards
        info_frame = tk.Frame(player_frame, bg="#1a1a1a")
        info_frame.pack(pady=(5, 0), padx=10)
        
        # Create name label
        name_label = tk.Label(
            info_frame, 
            text=f"{name} ({position})", 
            font=("Helvetica", 10, "bold"), 
            bg="#1a1a1a", 
            fg="white"
        )
        name_label.pack(fill='x')
        
        # Create cards frame
        cards_frame = tk.Frame(info_frame, bg="#1a1a1a")
        cards_frame.pack(pady=(5, 10), padx=10)
        
        # Create card widgets (not initialized with card backs)
        card1 = CardWidget(cards_frame, width=50, height=70)
        card1.pack(side="left", padx=3)
        card2 = CardWidget(cards_frame, width=50, height=70)
        card2.pack(side="left", padx=3)
        
        # Create stack frame
        stack_frame = tk.Frame(player_frame, bg="#1a1a1a")
        stack_frame.pack()
        
        # Create stack label
        stack_label = tk.Label(
            stack_frame, 
            text="$1000.00", 
            font=("Helvetica", 12, "bold"), 
            bg="#1a1a1a", 
            fg="white"
        )
        stack_label.pack(fill='x', pady=(0, 2))
        
        # Create bet label
        bet_label = tk.Label(
            stack_frame, 
            text="", 
            font=("Helvetica", 10, "bold"), 
            bg="#1a1a1a", 
            fg="gold"
        )
        bet_label.pack(fill='x')
        
        # Store references for updates
        self.player_seats[index] = {
            "frame": player_frame,
            "name_label": name_label,
            "cards_frame": cards_frame,
            "card_widgets": [card1, card2],
            "stack_label": stack_label,
            "bet_label": bet_label,
            "position": (x, y)
        }
        
        # Position the player frame
        self.canvas.create_window(x, y, window=player_frame, anchor="center")
    
    class LayoutManager:
        """Manages dynamic positioning for the poker table."""
        
        def __init__(self):
            self.min_spacing = 20
        
        def calculate_player_positions(self, width, height, num_players):
            """Calculate player seat positions with proper spacing."""
            center_x, center_y = width / 2, height / 2
            
            # Dynamic radius based on table size and number of players
            base_radius_x = width * 0.42
            base_radius_y = height * 0.35
            
            # Adjust for different player counts
            if num_players <= 4:
                radius_x = base_radius_x * 0.9
                radius_y = base_radius_y * 0.9
            elif num_players <= 6:
                radius_x = base_radius_x
                radius_y = base_radius_y
            else:
                radius_x = base_radius_x * 1.1
                radius_y = base_radius_y * 1.1
            
            positions = []
            for i in range(num_players):
                angle = (2 * math.pi / num_players) * i - (math.pi / 2)
                x = center_x + radius_x * math.cos(angle)
                y = center_y + radius_y * math.sin(angle)
                positions.append((x, y))
            
            return positions
        
        def calculate_community_card_position(self, width, height):
            """Calculate community card position."""
            return width / 2, height / 2 - 50
        
        def calculate_pot_position(self, width, height):
            """Calculate pot position."""
            return width / 2, height / 2 + 50
