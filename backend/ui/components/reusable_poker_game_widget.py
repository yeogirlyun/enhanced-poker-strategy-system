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
from ..practice_session_ui import CardWidget

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
        self.sound_manager = SoundManager(test_mode=False)
        
    def reset_change_tracking(self):
        """Reset all change tracking for a new hand (prevents false change detection)."""
        print("🔄 Resetting change tracking for new hand")
        self.last_player_states.clear()
        self.last_pot_amount = 0.0
        if hasattr(self, 'last_board_cards'):
            self.last_board_cards.clear()
        
        # Clear bet displays for new hand
        self._clear_all_bet_displays_permanent()
    
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
        
        # Session logger for comprehensive logging
        self.session_logger = get_session_logger()
        
        # Logging state tracking
        self.current_hand_id = None
        self.last_player_stacks = {}
        self.last_player_bets = {}
        self.current_street = "preflop"
        
        # Setup the UI
        self._setup_ui()
        
        # If state machine is provided, add this widget as a listener
        if self.state_machine:
            self.state_machine.add_event_listener(self)
            # Wait for player seats to be created before updating
            self.after(200, self._update_from_fpsm_state)
    
    def on_event(self, event: GameEvent):
        """Handle events from the FPSM."""
        print(f"🎯 Received event: {event.event_type}")
        
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
        """Render the widget based on the FPSM's display state."""
        print("🎯 Rendering from FPSM display state")
        
        # Update players
        for i, player_info in enumerate(display_state.get("players", [])):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_from_display_state(i, player_info)
        
        # Update community cards
        board_cards = display_state.get("board", [])
        self._update_community_cards_from_display_state(board_cards)
        
        # Update pot
        pot_amount = display_state.get("pot", 0.0)
        self.update_pot_amount(pot_amount)
        
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
            print(f"🎯 Updated player {player_index} name: {name_text}")
        
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
        
        # Only update cards if they changed
        if last_state.get("cards") != cards:
            self._set_player_cards_from_display_state(player_index, cards)
            print(f"🎴 Updated player {player_index} cards: {cards}")
        
        # Only update folded status if it changed
        if last_state.get("has_folded", False) != has_folded:
            if has_folded:
                self._mark_player_folded(player_index)
                print(f"❌ Player {player_index} folded")
        
        # Store the current state for next comparison
        self.last_player_states[player_index] = {
            "name_text": name_text,
            "stack": stack_amount,
            "bet_text": bet_text,
            "cards": cards.copy() if cards else [],
            "has_folded": has_folded
        }
    
    def _set_player_cards_from_display_state(self, player_index: int, cards: List[str]):
        """Set player cards based on display state (FLICKER-FREE VERSION)."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        card_widgets = self.player_seats[player_index]["card_widgets"]
        
        if len(cards) >= 2 and len(card_widgets) >= 2:
            # Only use the first 2 cards (hole cards)
            for i in range(2):
                card = cards[i] if i < len(cards) else ""
                
                # Check if card actually changed to prevent redraw
                current_card = getattr(card_widgets[i], '_current_card', "")
                
                if current_card != card:
                    if card and card != "**" and card != "" and card is not None:
                        try:
                            card_widgets[i].set_card(card, is_folded=False)
                            card_widgets[i]._current_card = card
                            print(f"🎴 Player {player_index} card {i}: {current_card} → {card}")
                        except tk.TclError:
                            # Widget was destroyed, skip
                            pass
                    else:
                        try:
                            card_widgets[i].set_card("", is_folded=False)
                            card_widgets[i]._current_card = ""
                            print(f"🎴 Player {player_index} card {i}: cleared")
                        except tk.TclError:
                            # Widget was destroyed, skip
                            pass
    
    def _update_community_cards_from_display_state(self, board_cards: List[str]):
        """Update community cards based on display state (FLICKER-FREE VERSION)."""
        # Ensure community card widgets are created
        if not self.community_card_widgets:
            self._draw_community_card_area()
        
        if not self.community_card_widgets:
            return
        
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
            else:
                cards_to_show = len(board_cards)  # Default to all cards for other states
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
        
        # Only update if visible board cards have actually changed (prevents flickering)
        if visible_board_cards == self.last_board_cards:
            return  # No change needed
        
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
        """Highlight the current action player."""
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                if i == player_index:
                    player_frame.config(highlightbackground="gold", highlightthickness=3)
                else:
                    player_frame.config(highlightbackground="#006400", highlightthickness=2)
    
    def _mark_player_folded(self, player_index):
        """Mark a player as folded."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            card_widget.set_folded()
    
    def update_display(self, update_type: str, **kwargs):
        """Update the display based on FPSM events."""
        print(f"🎯 Display update requested: {update_type}")
        
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
        print(f"🎯 Handling action executed: {event.action} by {event.player_name} for ${event.amount}")
        
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
                    print(f"🎯 Found player {player_name} at index {i} (seat text: {seat_text})")
                    break
        
        if player_index >= 0:
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
        print(f"🎯 Handling state change: {new_state}")
        
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
        print(f"🎯 Round complete: {street}")
        
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
            
            print(f"🎯 Round complete on {street} - animating {len(players)} player bets to pot")
            
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
            total_delay = animation_delay + 500  # Extra delay for last animation
            self.after(total_delay, self._clear_all_bet_displays)
            self.after(total_delay, self._clear_all_bet_displays_permanent)
        
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
            print("⚠️ No valid winner info or pot amount for animation")
    
    def _handle_player_action(self, **kwargs):
        """Handle player action updates from FPSM."""
        player_name = kwargs.get("player_name", "")
        action = kwargs.get("action", "")
        amount = kwargs.get("amount", 0.0)
        
        print(f"🎯 Player action: {player_name} {action} ${amount}")
        
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
        print("🧹 Clearing all bet displays")
        for player_index in list(self.bet_labels.keys()):
            self._remove_bet_display(player_index)
    
    def update_pot_amount(self, amount):
        """Update the pot amount display (FLICKER-FREE VERSION)."""
        # Only update if pot amount actually changed
        if self.last_pot_amount != amount:
            if self.pot_label:
                self.pot_label.config(text=f"${amount:.2f}")
                print(f"💰 Updated pot: ${self.last_pot_amount:.2f} → ${amount:.2f}")
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
        print(f"🎯 Animating street progression: {street_name} with cards {board_cards}")
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
    
    def reveal_all_cards(self):
        """Reveal all cards (for simulation mode) - now driven by FPSM."""
        print("🎴 Revealing all cards for simulation mode")
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
        """Draw the community card area in the center."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
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
    
    def _draw_pot_display(self):
        """Draw the pot display in the center."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
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
    
    def _on_resize(self, event=None):
        """Handle resize events."""
        if event and event.width > 1 and event.height > 1:
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
        
        print("🎯 Updating display from FPSM state")
        
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
        
        # Initialize player seats
        self.player_seats = [None] * 6
        
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
        """Draw the poker table with felt design."""
        if not self.canvas or self.canvas.winfo_width() <= 1:
            self.after(100, self._draw_table)
            return
            
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
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
    
    def _draw_player_seats(self):
        """Draw player seats around the table."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        # Use layout manager for positioning
        player_positions = self.layout_manager.calculate_player_positions(width, height, 6)
        
        for i in range(6):
            seat_x, seat_y = player_positions[i]
            self._create_player_seat_widget(seat_x, seat_y, f"Player {i+1}", positions[i], i)
    
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
