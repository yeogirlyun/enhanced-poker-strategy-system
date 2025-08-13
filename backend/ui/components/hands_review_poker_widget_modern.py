#!/usr/bin/env python3
"""
Modern Hands Review Poker Widget

A clean, specialized poker widget that inherits from ReusablePokerGameWidget
and provides hands review specific UI behavior following our established architecture.

Key principles:
- UI is a dumb renderer - NO game logic
- All behavior comes from specialized state machine
- Clean hook-based customization
- Event-driven updates only
"""

from typing import Dict, Any, Optional
import tkinter as tk

from .reusable_poker_game_widget import ReusablePokerGameWidget, THEME
from core.flexible_poker_state_machine import GameEvent


class HandsReviewPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for hands review that provides educational features.
    
    This widget extends ReusablePokerGameWidget with hands review specific behavior:
    - Always visible cards for all players
    - Educational styling and annotations
    - Hand progress indicators
    - Study mode features
    
    All game logic is handled by HandsReviewPokerStateMachine.
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the hands review poker widget."""
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        # Hands review specific UI state
        self.review_mode = True
        self.show_all_cards = True
        self.highlight_current_action = True
        
        # Progress tracking for visual indicators
        self.current_action_index = 0
        self.total_actions = 0
        
        # Study annotations UI elements
        self.annotation_widgets = {}
        
        if self.session_logger:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_WIDGET", "HandsReviewPokerWidget initialized", {
                "parent": str(type(parent).__name__),
                "review_mode": True
            })
    
    # ==============================
    # HOOK OVERRIDES FOR HANDS REVIEW
    # Clean customization without logic
    # ==============================
    
    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Hook Override: Always show all cards in hands review mode.
        
        In hands review, we want to see everyone's cards for educational purposes.
        """
        return True  # Always show cards, even for non-human players
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
        """
        Hook Override: Ensure real card data is shown instead of placeholders.
        
        Convert ** placeholders to actual card data if available from state machine.
        """
        if card == "**" and hasattr(self, 'state_machine') and self.state_machine:
            # Get real card data from state machine
            try:
                if hasattr(self.state_machine, 'game_state') and self.state_machine.game_state:
                    players = self.state_machine.game_state.players
                    if player_index < len(players):
                        player_cards = players[player_index].cards
                        if card_index < len(player_cards):
                            return player_cards[card_index]
            except Exception:
                pass  # Fall back to original card
        
        return card
    
    def _should_highlight_player(self, player_index: int, player_info: dict) -> bool:
        """
        Hook Override: Highlight the player whose action is currently being reviewed.
        """
        if not self.highlight_current_action:
            return False
        
        # Check if this player is involved in the current action being reviewed
        if hasattr(self, 'current_action_player_index'):
            return player_index == self.current_action_player_index
        
        return super()._should_highlight_player(player_index, player_info)
    
    def _should_show_turn_indicator(self, player_index: int) -> bool:
        """
        Hook Override: Disable "YOUR TURN" labels in hands review mode.
        
        In hands review, users are watching the sequence, not taking turns,
        so turn indicators are unnecessary and distracting.
        """
        return False  # Never show "YOUR TURN" in hands review
    
    def _add_action_indicator(self, player_frame):
        """
        Hook Override: Disable action indicators in hands review mode.
        
        In hands review, we don't need "YOUR TURN" or action indicators
        since users are just watching the sequence.
        """
        # Do nothing - no action indicators in hands review mode
        pass
    
    def _clear_action_indicators(self, player_index=None):
        """
        Hook Override: Aggressively clear ALL action indicators in hands review mode.
        
        This ensures no "YOUR TURN" or other action labels persist between hands.
        """
        # Clear for all players to ensure complete cleanup
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                for widget in player_frame.winfo_children():
                    if hasattr(widget, '_action_indicator'):
                        widget.destroy()
                        print(f"🔥 CONSOLE: Cleared action indicator for player {i}")
    
    def _clear_all_hand_state(self):
        """
        COMPLETE UI cleanup - remove ALL remnants from previous hands.
        
        This method aggressively clears every UI element that could persist
        between hands, ensuring a completely clean table state.
        """
        print("🔥 CONSOLE: Starting COMPLETE UI cleanup...")
        
        # Clear all action indicators and labels
        self._clear_action_indicators()
        
        # Clear all player-specific labels and highlights
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                
                # Remove ALL labels and widgets that aren't the core player info
                for widget in list(player_frame.winfo_children()):
                    widget_text = getattr(widget, 'cget', lambda x: '')(1) if hasattr(widget, 'cget') else ''
                    
                    # Keep only the core player frame elements, remove everything else
                    if (hasattr(widget, '_action_indicator') or 
                        'WINNER' in str(widget_text) or
                        'BET' in str(widget_text) or
                        'CALL' in str(widget_text) or
                        'RAISE' in str(widget_text) or
                        'CHECK' in str(widget_text) or
                        'FOLD' in str(widget_text) or
                        'ALL-IN' in str(widget_text) or
                        hasattr(widget, '_status_label') or
                        hasattr(widget, '_winner_label')):
                        
                        widget.destroy()
                        print(f"🔥 CONSOLE: Cleared UI element for player {i}: {widget_text}")
                
                # Reset player frame styling to default
                player_frame.config(
                    highlightbackground=THEME["player_border"],
                    highlightthickness=2,
                    bg=THEME["player_bg"]
                )
        
        # Clear pot display
        if hasattr(self, 'pot_label') and self.pot_label:
            self.pot_label.config(text="Pot: $0")
        
                # Clear any bet labels (completely removed bet label system)
        if hasattr(self, 'bet_labels'):
            for bet_label in self.bet_labels.values():
                try:
                    bet_label.destroy()
                except:
                    pass
            self.bet_labels.clear()
        
        # Remove bet_label references from player seats (clean up the data structure)
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and "bet_label" in player_seat:
                del player_seat["bet_label"]
                print(f"🔥 CONSOLE: Removed bet_label reference for player {i}")
        
        # Clear winner labels and any other action-related labels
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and "frame" in player_seat:
                player_frame = player_seat["frame"]
                for widget in list(player_frame.winfo_children()):
                    try:
                        widget_text = widget.cget(1) if hasattr(widget, 'cget') else ''
                        if any(keyword in str(widget_text) for keyword in ['WINNER', 'BET', 'CALL', 'RAISE', 'CHECK', 'FOLD', 'ALL-IN']):
                            widget.destroy()
                            print(f"🔥 CONSOLE: Cleared action label for player {i}: {widget_text}")
                    except Exception as e:
                        print(f"🔥 CONSOLE: Error clearing action label for player {i}: {e}")
        
        # Clear board display
        if hasattr(self, 'board_canvas'):
            self.board_canvas.delete("all")
            # Recreate the "Community Cards" label
            self.board_canvas.create_text(
                150, 30,  # Center of the canvas
                text="Community Cards",
                fill=THEME["text_primary"],
                font=("Arial", 14, "bold")
            )
        
        print("🔥 CONSOLE: COMPLETE UI cleanup finished!")
    
    def _update_player_from_display_state(self, player_index: int, player_info: dict):
        """
        Override: Completely remove bet label system - use only chip graphics.
        
        The practice session uses only chip graphics for bet displays, so we
        completely eliminate the text label system to maintain consistency.
        """
        # Call parent method but prevent bet label creation/updates
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        player_seat = self.player_seats[player_index]
        
        # Get current state for comparison
        last_state = getattr(self, 'last_player_states', {}).get(player_index, {})
        
        # Extract new state
        name = player_info.get("name", f"Player {player_index+1}")
        position = player_info.get("position", "")
        stack_amount = player_info.get("stack", 0.0)
        cards = player_info.get("cards", [])
        has_folded = player_info.get("has_folded", False)
        
        # Update name if it changed
        name_text = f"{name} ({position})"
        if last_state.get("name_text") != name_text:
            player_seat["name_label"].config(text=name_text)
        
        # Update stack if it changed
        if last_state.get("stack", 0.0) != stack_amount:
            player_seat["stack_label"].config(text=f"${int(stack_amount):,}")
        
        # NO BET LABELS - only chip graphics will be used
        
        # Update cards
        last_cards = last_state.get("cards", [])
        if last_cards != cards:
            self._set_player_cards_from_display_state(player_index, cards)
        
        # Update folded status
        if last_state.get("has_folded", False) != has_folded:
            if has_folded:
                self._mark_player_folded(player_index)
            else:
                self._unmark_player_folded(player_index)
        
        # Store current state for next comparison
        if not hasattr(self, 'last_player_states'):
            self.last_player_states = {}
        self.last_player_states[player_index] = {
            "name_text": name_text,
            "stack": stack_amount,
            "cards": cards,
            "has_folded": has_folded
        }
    
    def _create_player_seat(self, player_index: int, position: tuple) -> dict:
        """
        Override: Create player seat without bet labels - only chip graphics.
        
        The practice session doesn't use text bet labels, so we completely
        eliminate them from the player seat structure.
        """
        # Call parent method but remove bet label creation
        player_seat = super()._create_player_seat(player_index, position)
        
        # Remove bet_label if it was created by parent
        if "bet_label" in player_seat:
            del player_seat["bet_label"]
            print(f"🔥 CONSOLE: Removed bet_label from player seat {player_index}")
        
        return player_seat
    
    def _handle_ui_cleanup_event(self, event_data: dict):
        """
        Handle UI cleanup events from the state machine.
        
        This ensures complete cleanup when loading new hands.
        """
        if event_data.get('action') == 'clear_all_hand_state':
            print("🔥 CONSOLE: Received UI cleanup event - clearing all hand state")
            self._clear_all_hand_state()
    
    def on_event(self, event: GameEvent):
        """
        Override: Handle events from the state machine.
        
        This ensures we can intercept and handle UI cleanup events.
        """
        # Handle UI cleanup events specifically
        if event.event_type == "ui_cleanup":
            self._handle_ui_cleanup_event(event.data)
        
        # Call parent class event handling for all other events
        super().on_event(event)
    
    def _customize_player_styling(self, player_index: int, player_info: dict) -> dict:
        """
        Hook Override: Enhanced styling for hands review mode.
        
        Provide educational visual cues while maintaining readability.
        """
        styling = super()._customize_player_styling(player_index, player_info)
        
        # Educational styling for folded players (show cards but indicate folded state)
        if player_info.get('has_folded', False):
            styling.update({
                'border_color': '#8B4513',  # Brown border for folded
                'background': '#2F2F2F',    # Darker background
                'text_color': '#D2691E',    # Orange text for folded
                'card_opacity': 0.7         # Slightly transparent cards
            })
        
        # Highlight current action player
        if self._should_highlight_player(player_index, player_info):
            styling.update({
                'border_color': '#FFD700',  # Gold border for current action
                'border_width': 3,          # Thicker border
                'background': '#1A1A2E'     # Highlighted background
            })
        
        return styling
    
    def _should_update_community_cards(self, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Always update community cards in hands review.
        
        We want to see all board progression for educational purposes.
        """
        return True
    
    def _get_pot_display_text(self, pot_amount: float) -> str:
        """
        Enhanced pot display with educational info for hands review.
        """
        # Format basic pot display (since base class doesn't have this method)
        base_text = f"Pot: ${pot_amount:.2f}"
        
        # Add progress indicator if we have action tracking
        if hasattr(self, 'total_actions') and self.total_actions > 0:
            progress = self.current_action_index / self.total_actions
            progress_bar = "█" * int(progress * 10) + "░" * (10 - int(progress * 10))
            return f"{base_text}\n[{progress_bar}] {self.current_action_index}/{self.total_actions}"
        
        return base_text
    
    # ==============================
    # HANDS REVIEW SPECIFIC METHODS
    # UI-only methods for display/interaction
    # ==============================
    
    def update_hand_progress(self, current_action: int, total_actions: int):
        """Update visual progress indicators."""
        self.current_action_index = current_action
        self.total_actions = total_actions
        
        # Update pot display to reflect progress
        if hasattr(self, 'pot_display') and self.pot_display:
            current_pot = getattr(self.state_machine.game_state, 'pot', 0.0) if self.state_machine else 0.0
            pot_text = self._get_pot_display_text(current_pot)
            # Update pot display text if it supports it
            if hasattr(self.pot_display, 'set_title'):
                self.pot_display.set_title(f"Pot (Action {current_action}/{total_actions})")
    
    def highlight_action_player(self, player_index: int):
        """Highlight the player who is taking the current action."""
        self.current_action_player_index = player_index
        
        # Trigger a visual update
        self._update_player_highlights()
    
    def clear_action_highlight(self):
        """Clear the current action player highlight."""
        if hasattr(self, 'current_action_player_index'):
            delattr(self, 'current_action_player_index')
        self._update_player_highlights()
    
    def _update_player_highlights(self):
        """Update player highlighting based on current state."""
        # Force a display update to refresh highlights
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                display_state = self.state_machine.get_display_state()
                self._apply_display_state(display_state)
            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_system("WARNING", "HANDS_REVIEW_WIDGET", f"Error updating highlights: {e}")
    
    def add_annotation_marker(self, player_index: int, annotation: str, category: str = "general"):
        """Add a visual annotation marker near a player."""
        try:
            if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
                return
            
            # Create annotation marker
            marker_id = f"annotation_{player_index}_{len(self.annotation_widgets)}"
            
            # Get player position
            player_seat = self.player_seats[player_index]
            player_x, player_y = player_seat["position"]
            
            # Create annotation icon
            annotation_text = self.canvas.create_text(
                player_x + 30, player_y - 30,
                text="📝",
                font=("Arial", 16),
                fill="#FFD700",
                tags=("annotation", marker_id)
            )
            
            # Store annotation data
            self.annotation_widgets[marker_id] = {
                'canvas_id': annotation_text,
                'annotation': annotation,
                'category': category,
                'player_index': player_index
            }
            
            # Add click handler for annotation details
            self.canvas.tag_bind(annotation_text, "<Button-1>", 
                               lambda e: self._show_annotation_details(marker_id))
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("WARNING", "HANDS_REVIEW_WIDGET", f"Error adding annotation: {e}")
    
    def _show_annotation_details(self, marker_id: str):
        """Show annotation details in a tooltip or popup."""
        if marker_id in self.annotation_widgets:
            annotation_data = self.annotation_widgets[marker_id]
            # For now, just print - could be enhanced with tooltips
            print(f"📝 Annotation: {annotation_data['annotation']} (Category: {annotation_data['category']})")
    
    def clear_all_annotations(self):
        """Clear all annotation markers from the display."""
        # Remove canvas items
        for marker_id, data in self.annotation_widgets.items():
            if 'canvas_id' in data:
                self.canvas.delete(data['canvas_id'])
        
        # Clear storage
        self.annotation_widgets.clear()
    
    def set_educational_mode(self, enabled: bool):
        """Enable/disable educational features like annotations and highlights."""
        self.highlight_current_action = enabled
        
        if not enabled:
            self.clear_action_highlight()
            self.clear_all_annotations()
    
    # ==============================
    # EVENT HANDLING OVERRIDES
    # Handle hands review specific events
    # ==============================
    
    def on_event(self, event: GameEvent):
        """Handle hands review specific events."""
        # Call parent event handler first
        super().on_event(event)
        
        # Handle hands review specific events
        if event.event_type == "step_forward":
            self._handle_step_forward_event(event)
        elif event.event_type == "step_backward":
            self._handle_step_backward_event(event)
        elif event.event_type == "hand_loaded":
            self._handle_hand_loaded_event(event)
        elif event.event_type == "annotation_added":
            self._handle_annotation_added_event(event)
    
    def _handle_step_forward_event(self, event: GameEvent):
        """Handle step forward event."""
        data = event.data
        current_action = data.get('action_index', 0)
        total_actions = data.get('total_actions', 0)
        
        # Update progress display
        self.update_hand_progress(current_action, total_actions)
        
        # Highlight player if action data available
        action_executed = data.get('action_executed', {})
        if 'player' in action_executed:
            player_name = action_executed['player']
            # Find player index by name
            for i, seat in enumerate(self.player_seats):
                if seat and seat.get('name_label'):
                    if seat['name_label'].cget('text').split(' (')[0] == player_name:
                        self.highlight_action_player(i)
                        break
    
    def _handle_step_backward_event(self, event: GameEvent):
        """Handle step backward event."""
        data = event.data
        current_action = data.get('action_index', 0)
        total_actions = data.get('total_actions', 0)
        
        # Update progress display
        self.update_hand_progress(current_action, total_actions)
        
        # Clear highlights when stepping backward
        self.clear_action_highlight()
    
    def _handle_hand_loaded_event(self, event: GameEvent):
        """Handle hand loaded event."""
        data = event.data
        total_actions = data.get('num_actions', 0)
        
        # Reset progress
        self.update_hand_progress(0, total_actions)
        
        # Clear previous annotations
        self.clear_all_annotations()
        
        if self.session_logger:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_WIDGET", "Hand loaded in widget", {
                "hand_id": data.get('id', 'unknown') if isinstance(data, dict) else 'unknown',
                "total_actions": total_actions
            })
    
    def _handle_annotation_added_event(self, event: GameEvent):
        """Handle annotation added event."""
        data = event.data
        action_index = data.get('action_index', 0)
        annotation = data.get('annotation', '')
        category = data.get('category', 'general')
        
        # For now, we don't automatically add visual markers for all annotations
        # This could be enhanced based on UI needs
        pass
    
    def _animate_player_action(self, player_index, action, amount):
        """
        Override: Disable ONLY text labels, keep chip graphics and animations.
        
        In hands review, we don't want "CALL $2" or "BET $5" text labels cluttering
        the UI, but we DO want to keep the actual chip graphics and animations.
        """
        # Play sound for the action
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.play_sound(action.lower())
        
        # DO NOT show text bet labels - but chip graphics will still work
        # The practice session uses text labels, but hands review should be clean
        # Chip animations, bet-to-pot movements, and actual chip displays are preserved
    
    def show_bet_display(self, player_index, action, amount):
        """
        Override: Disable ONLY text bet labels, preserve chip graphics.
        
        This method creates text overlays like "💰 CALL $2" which we don't want.
        But we DO want to keep the actual chip animations and graphics.
        """
        # Do nothing - no text bet labels in hands review mode
        # Chip graphics, animations, and bet-to-pot movements are handled elsewhere
        pass
    
    def _show_bet_display_for_player(self, player_index: int, action: str, amount: float):
        """
        Override: Disable ONLY text bet displays, preserve chip graphics.
        
        This method is called from other places in the parent class, but we
        only want to disable the text labels, not the chip graphics.
        """
        # Do nothing - no text bet displays in hands review mode
        # Actual chip graphics and animations are preserved
        pass
    
    def _handle_round_complete(self, event: GameEvent):
        """
        Override: Prevent duplicate card dealing sounds in hands review.
        
        The state machine already plays card dealing sounds when transitioning
        to DEAL_FLOP, DEAL_TURN, DEAL_RIVER. The UI widget shouldn't play
        them again to avoid duplicate sounds.
        """
        street = event.data.get("street", "") if hasattr(event, 'data') else ""
        
        # Skip the duplicate card dealing sound - state machine handles it
        # self.play_sound("dealing")  # REMOVED - prevents duplicate sounds
        
        # Animate all player bets to pot during street transition using snapshot from event
        snapshot = event.data.get("player_bets", []) if hasattr(event, 'data') else []
        if snapshot:
            self.animating_bets_to_pot = True
            animation_delay = 0
            for item in snapshot:
                idx = item.get("index", -1)
                amt = item.get("amount", 0.0)
                if idx >= 0 and amt > 0:
                    self.after(animation_delay, lambda pidx=idx, pam=amt: self._animate_bet_to_pot(pidx, pam))
                    animation_delay += 280
            # Add a small delay after animations complete so users can perceive completion
            total_delay = animation_delay + 800
            # Remember total delay so hand-complete can start pot animation AFTER this
            self._bet_animation_total_delay_ms = total_delay
            self.after(total_delay, lambda: self._finish_bet_animations())
            print(f"🔥 CONSOLE: Round complete bet-to-pot animation scheduled; total_delay={total_delay}ms")
        
        # Animate street progression (but without duplicate sound)
        if street in ["flop", "turn", "river"]:
            # Get current board cards from display state
            if hasattr(self, 'state_machine') and self.state_machine:
                display_state = self.state_machine.get_game_info()
                board_cards = display_state.get("board", [])
                self.play_animation("street_progression", street_name=street, board_cards=board_cards)
