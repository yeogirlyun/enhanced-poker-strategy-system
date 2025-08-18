#!/usr/bin/env python3
"""
Unified Bot Session Widget

This module provides a unified poker widget for all bot-only sessions,
including GTO simulation and hands review. By reusing the same rendering
logic and event handling, both session types have consistent behavior
and appearance.

Key benefits:
- Single widget codebase for both GTO and hands review
- Consistent animations, sounds, and visual effects
- Simplified maintenance and bug fixes
- Clean separation from practice session complexity
"""

import tkinter as tk
from typing import Optional, Dict, Any

from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.bot_session_state_machine import BotSessionStateMachine
from core.gui_models import THEME, FONTS


class BotSessionWidget(ReusablePokerGameWidget):
    """
    Unified poker widget for all bot-only sessions.
    
    This widget can display both GTO simulation and hands review sessions
    using the same rendering logic. The only difference is the decision
    source (GTO algorithm vs preloaded hand data).
    """
    
    def __init__(self, parent, session: BotSessionStateMachine, **kwargs):
        """
        Initialize the bot session widget.
        
        Args:
            parent: Parent tkinter widget
            session: Bot session state machine (GTO or hands review)
            **kwargs: Additional widget configuration
        """
        super().__init__(parent, session, **kwargs)
        
        # Store session reference
        self.bot_session = session
        self.session_type = session.session_type
        
        # Mark this as a bot widget for conditional positioning
        self._is_bot_widget = True
        self._is_gto_widget = (session.session_type == "gto")
        
        # Bot session specific attributes
        self.current_decision: Optional[Dict[str, Any]] = None
        self.decision_explanation_var = tk.StringVar()
        
        # Initialize bot-specific UI
        self._setup_bot_ui()
        
        # Bind to session updates
        self._bind_bot_events()
    
    def _setup_ui(self):
        """Override parent's _setup_ui to optimize for bot sessions."""
        # Configure grid weights for proper sizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create canvas for the poker table (use grid to match container)
        self.canvas = tk.Canvas(
            self, bg=THEME["table_felt"], highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Initialize player seats (will be set dynamically)
        self.player_seats = []

        # Force initial draw
        self._force_initial_draw()
        
        # Create table elements when canvas is properly sized
        self._schedule_table_creation()
    
    def _schedule_table_creation(self):
        """Schedule table creation when canvas is properly sized."""
        # Check if canvas is properly sized
        if self.canvas.winfo_width() > 1 and self.canvas.winfo_height() > 1:
            # Canvas is ready, draw the table now
            self._draw_table()
        else:
            # Canvas not ready yet, schedule retry
            self.after(50, self._schedule_table_creation)
    
    def _setup_bot_ui(self):
        """Setup bot session specific UI elements."""
        # Initialize variables for communication with parent panels
        self.current_decision = None
        self.decision_explanation_var.set("Ready for bot session...")
        
        if self.session_logger:
            self.session_logger.log_system(
                "DEBUG", "BOT_WIDGET",
                f"Bot widget initialized for {self.session_type} session",
                {"session_type": self.session_type}
            )
    
    def _bind_bot_events(self):
        """Bind to bot session events."""
        if self.bot_session:
            # Register as event listener
            self.bot_session.add_event_listener(self)
    
    def execute_next_action(self) -> bool:
        """
        Execute the next bot action in the session.
        
        Returns:
            True if action was executed successfully, False otherwise
        """
        if not self.bot_session:
            return False
        
        try:
            success = self.bot_session.execute_next_bot_action()
            
            if success:
                # Update display after action
                self.after(100, self._update_display)
                
                if self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG", "BOT_WIDGET",
                        "Bot action executed successfully",
                        {"session_type": self.session_type}
                    )
            
            return success
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_WIDGET",
                    f"Error executing bot action: {e}",
                    {"session_type": self.session_type}
                )
            return False
    
    def start_session(self) -> bool:
        """Start the bot session."""
        if not self.bot_session:
            return False
        
        success = self.bot_session.start_session()
        
        if success:
            # Update display to show initial state
            self.after(100, self._update_display)
            
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO", "BOT_WIDGET",
                    f"Bot session started: {self.session_type}",
                    {"session_type": self.session_type}
                )
        
        return success
    
    def stop_session(self):
        """Stop the current bot session."""
        if self.bot_session:
            self.bot_session.stop_session()
            
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO", "BOT_WIDGET",
                    f"Bot session stopped: {self.session_type}",
                    {"session_type": self.session_type}
                )
    
    def _update_display(self):
        """Update the poker table display based on current session state."""
        try:
            if not self.bot_session:
                return
            
            # Get current display state from session
            display_state = self.bot_session.get_display_state()
            
            # Update the poker table display using parent's logic
            self._update_from_display_state(display_state)
            
            # Update decision explanation
            current_explanation = self.bot_session.get_current_explanation()
            self.decision_explanation_var.set(current_explanation)
            
            if self.session_logger:
                self.session_logger.log_system(
                    "DEBUG", "BOT_WIDGET",
                    "Display updated successfully",
                    {
                        "session_type": self.session_type,
                        "player_count": len(display_state.get("players", [])),
                        "current_street": display_state.get("street", "unknown")
                    }
                )
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_WIDGET",
                    f"Error updating display: {e}",
                    {"session_type": self.session_type}
                )
    
    def _update_from_display_state(self, display_state: Dict[str, Any]):
        """Update UI based on display state from bot session."""
        # Use parent's display state update logic
        # This ensures consistent rendering with practice sessions
        super()._update_from_fpsm_state()
        
        # Handle bot-specific display elements
        players = display_state.get("players", [])
        highlights = display_state.get("player_highlights", [])
        card_visibilities = display_state.get("card_visibilities", [])
        
        # Update player highlights (show current action player)
        for i, should_highlight in enumerate(highlights):
            if i < len(self.player_seats) and should_highlight:
                self._highlight_current_player(i)
        
        # Show all cards for bot sessions (no hidden information)
        for i, player_info in enumerate(players):
            if i < len(card_visibilities) and card_visibilities[i]:
                self._show_player_cards(i, player_info.get("cards", []))
        
        # Update bet displays (use chip graphics)
        for i, player_info in enumerate(players):
            current_bet = player_info.get("current_bet", 0.0)
            if current_bet > 0:
                self._show_bet_display_for_player(i, "bet", current_bet)
    
    def _show_player_cards(self, player_index: int, cards: list):
        """Show cards for a specific player."""
        if player_index < len(self.player_seats):
            player_frame = self.player_seats[player_index]
            # Update card display logic here
            # This would integrate with the existing card display system
            pass
    
    def get_decision_history(self) -> list:
        """Get the complete decision history for this session."""
        if self.bot_session:
            return self.bot_session.get_decision_history()
        return []
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        if self.bot_session:
            display_state = self.bot_session.get_display_state()
            return display_state.get("session_info", {})
        return {}
    
    def reset_session(self):
        """Reset the session to its initial state."""
        if self.bot_session:
            self.bot_session.reset_session()
            self.decision_explanation_var.set("Session reset - ready to start")
            
            # Clear display
            self._clear_table_display()
    
    def _clear_table_display(self):
        """Clear all table display elements."""
        # Clear player highlights
        for i in range(len(self.player_seats)):
            self._remove_player_highlight(i)
        
        # Clear bet displays
        for player_index in list(self.bet_displays.keys()):
            self._hide_bet_display_for_player(player_index)
        
        # Reset pot display
        if hasattr(self, 'pot_display') and self.pot_display:
            self.pot_display.set_amount(0.0)
    
    def _should_play_action_sounds(self) -> bool:
        """
        Override: Bot sessions should NOT play action sounds at widget level.
        
        The bot state machines (GTOPokerStateMachine, BotSessionStateMachine) 
        handle their own action sounds, so we disable widget-level sounds
        to prevent duplicate audio.
        """
        return False
    
    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Override: Always show all cards in bot sessions for educational purposes.
        
        Both GTO and hands review sessions should show all player cards
        to provide complete information for learning and analysis.
        """
        # Always show cards in bot sessions (no hidden information)
        return True
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
        """
        Override: Convert placeholder cards to real card data from state machine.
        
        This ensures that bot sessions show actual card values instead of
        placeholder symbols like "**".
        """
        if card == "**" and hasattr(self, 'state_machine') and self.state_machine:
            # Get real card data from state machine
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state):
                    players = self.state_machine.game_state.players
                    if player_index < len(players):
                        player_cards = players[player_index].cards
                        if card_index < len(player_cards):
                            return player_cards[card_index]
            except Exception:
                pass  # Fall back to original card
        
        return card


class GTOSessionWidget(BotSessionWidget):
    """Specialized widget for GTO simulation sessions."""
    
    def __init__(self, parent, gto_session, **kwargs):
        """Initialize GTO session widget."""
        super().__init__(parent, gto_session, **kwargs)
        
        # GTO-specific attributes
        self.gto_session = gto_session
    
    def get_gto_explanation(self) -> str:
        """Get the current GTO decision explanation."""
        return self.decision_explanation_var.get()



class HandsReviewSessionWidget(BotSessionWidget):
    """Specialized widget for hands review sessions."""
    
    def __init__(self, parent, hands_review_session, logger=None):
        """Initialize hands review session widget."""
        super().__init__(parent, hands_review_session)
        
        # Use same positioning as GTO widget
        self._is_gto_widget = True
        
        # Hands review specific attributes
        self.hands_review_session = hands_review_session
    
    def get_review_explanation(self) -> str:
        """Get the current hands review explanation."""
        if self.hands_review_session:
            return self.hands_review_session.get_current_explanation()
        return "No explanation available"
    
    def get_review_progress(self) -> Dict[str, Any]:
        """Get progress information for the hands review."""
        session_info = self.get_session_info()
        engine_info = session_info.get("engine_info", {})
        
        return {
            "current_step": engine_info.get("current_step", 0),
            "total_steps": engine_info.get("total_steps", 0),
            "progress_percent": engine_info.get("progress_percent", 0),
            "steps_remaining": engine_info.get("steps_remaining", 0)
        }
