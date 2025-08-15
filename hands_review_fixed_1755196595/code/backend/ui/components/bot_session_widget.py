#!/usr/bin/env python3
"""
Bot Session Widget - UI wrapper for bot-only poker sessions.
Provides a unified interface for GTO and Hands Review sessions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
from backend.core.session_logger import SessionLogger


class BotSessionWidget(ttk.Frame):
    """Base widget for bot-only poker sessions."""
    
    def __init__(self, parent_frame: tk.Frame, session, logger: SessionLogger):
        """Initialize bot session widget."""
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        self.session = session
        self.logger = logger
        self.is_active = False
        
    def start_session(self) -> bool:
        """Start the bot session."""
        try:
            success = self.session.start_session()
            self.is_active = success
            return success
        except Exception as e:
            self.logger.log_system("ERROR", "BOT_WIDGET", f"Failed to start session: {e}")
            return False
    
    def stop_session(self):
        """Stop the bot session."""
        try:
            if hasattr(self.session, 'stop_session'):
                self.session.stop_session()
            self.is_active = False
        except Exception as e:
            self.logger.log_system("ERROR", "BOT_WIDGET", f"Failed to stop session: {e}")
    
    def execute_next_action(self) -> bool:
        """Execute the next action in the session."""
        if not self.is_active:
            return False
            
        try:
            # Direct call to session's action execution
            result = self.session.execute_next_bot_action()
            
            # Update display after action
            if result and hasattr(self, 'update_display'):
                self.update_display("action_complete")
                
            return result
        except Exception as e:
            self.logger.log_system("ERROR", "BOT_WIDGET", f"Failed to execute action: {e}")
            return False
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information."""
        if hasattr(self.session, 'get_game_info'):
            return self.session.get_game_info()
        return {}
    
    def update_display(self, update_type: str = "general"):
        """Update the display (override in subclasses)."""
        pass


class HandsReviewSessionWidget(BotSessionWidget):
    """Widget specifically for Hands Review sessions."""
    
    def __init__(self, parent_frame: tk.Frame, session, logger: SessionLogger):
        """Initialize hands review session widget."""
        super().__init__(parent_frame, session, logger)
        self.logger.log_system("INFO", "HANDS_REVIEW_WIDGET", "HandsReviewSessionWidget initialized")
        self._create_ui()
    
    def _create_ui(self):
        """Create the hands review UI."""
        # Create a simple placeholder for now - the actual poker table will be managed
        # by the ReusablePokerGameWidget that the panel creates separately
        self.info_label = ttk.Label(self, text="Hands Review Session Ready")
        self.info_label.pack(pady=10)
        
        # Control buttons frame
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.pack(pady=5)
        
        # Next button (main functionality)
        self.next_button = ttk.Button(
            self.controls_frame, 
            text="Next", 
            command=self._next_action,
            state="disabled"
        )
        self.next_button.pack(side="left", padx=5)
        
        # Reset button
        self.reset_button = ttk.Button(
            self.controls_frame,
            text="Reset",
            command=self.reset_session,
            state="disabled"
        )
        self.reset_button.pack(side="left", padx=5)
    
    def _next_action(self):
        """Handle Next button click."""
        try:
            self.logger.log_system("DEBUG", "HANDS_REVIEW_WIDGET", "Next button clicked")
            result = self.execute_next_action()
            
            if not result:
                # Session complete or error
                self.next_button.config(state="disabled")
                self.info_label.config(text="Hand complete")
                
        except Exception as e:
            self.logger.log_system("ERROR", "HANDS_REVIEW_WIDGET", f"Next action failed: {e}")
    
    def enable_controls(self):
        """Enable the control buttons."""
        self.next_button.config(state="normal")
        self.reset_button.config(state="normal")
        self.info_label.config(text="Hand loaded - ready to review")
    
    def disable_controls(self):
        """Disable the control buttons."""
        self.next_button.config(state="disabled") 
        self.reset_button.config(state="disabled")
        self.info_label.config(text="No hand loaded")
    
    def load_hand(self, hand_data: Dict[str, Any]) -> bool:
        """Load a specific hand for review."""
        try:
            if hasattr(self.session, 'set_preloaded_hand_data'):
                self.session.set_preloaded_hand_data(hand_data)
                self.logger.log_system("INFO", "HANDS_REVIEW_WIDGET", f"Hand loaded: {hand_data.get('hand_id', 'unknown')}")
                return True
            return False
        except Exception as e:
            self.logger.log_system("ERROR", "HANDS_REVIEW_WIDGET", f"Failed to load hand: {e}")
            return False
    
    def reset_session(self):
        """Reset the session to beginning of hand."""
        try:
            if hasattr(self.session, 'decision_engine') and hasattr(self.session.decision_engine, 'reset'):
                self.session.decision_engine.reset()
                self.logger.log_system("INFO", "HANDS_REVIEW_WIDGET", "Session reset to beginning")
        except Exception as e:
            self.logger.log_system("ERROR", "HANDS_REVIEW_WIDGET", f"Failed to reset session: {e}")
    
    def get_current_action_info(self) -> Dict[str, Any]:
        """Get information about the current action."""
        try:
            if hasattr(self.session, 'decision_engine'):
                engine = self.session.decision_engine
                return {
                    'current_index': getattr(engine, 'current_action_index', 0),
                    'total_actions': getattr(engine, 'total_actions', 0),
                    'is_complete': engine.is_session_complete() if hasattr(engine, 'is_session_complete') else False
                }
        except Exception as e:
            self.logger.log_system("ERROR", "HANDS_REVIEW_WIDGET", f"Failed to get action info: {e}")
        
        return {'current_index': 0, 'total_actions': 0, 'is_complete': True}
    
    def update_display(self, update_type: str = "general"):
        """Update the hands review display."""
        # This would typically update UI elements, but since we're working
        # with the panel directly, we'll let the panel handle display updates
        self.logger.log_system("DEBUG", "HANDS_REVIEW_WIDGET", f"Display update requested: {update_type}")
    
    def _update_display(self):
        """Internal display update method (called by panel)."""
        self.update_display("internal")
    
    def update_font_size(self, base_size: int):
        """Update font size for the widget (called by panel)."""
        self.logger.log_system("DEBUG", "HANDS_REVIEW_WIDGET", f"Font size update requested: {base_size}")
        # Font update would be implemented here if needed


class GTOSessionWidget(BotSessionWidget):
    """Widget specifically for GTO simulation sessions."""
    
    def __init__(self, parent_frame: tk.Frame, session, logger: SessionLogger):
        """Initialize GTO session widget."""
        super().__init__(parent_frame, session, logger)
        self.logger.log_system("INFO", "GTO_WIDGET", "GTOSessionWidget initialized")
    
    def start_new_hand(self) -> bool:
        """Start a new random hand."""
        try:
            if hasattr(self.session, 'start_hand'):
                self.session.start_hand()
                return True
            return False
        except Exception as e:
            self.logger.log_system("ERROR", "GTO_WIDGET", f"Failed to start new hand: {e}")
            return False
    
    def get_gto_explanation(self) -> str:
        """Get explanation for the last GTO decision."""
        try:
            if hasattr(self.session, 'decision_history') and self.session.decision_history:
                last_decision = self.session.decision_history[-1]
                return last_decision.get('explanation', 'No explanation available')
        except Exception as e:
            self.logger.log_system("ERROR", "GTO_WIDGET", f"Failed to get GTO explanation: {e}")
        
        return "No explanation available"


# Factory function for creating appropriate widgets
def create_session_widget(session_type: str, parent_frame: tk.Frame, session, logger: SessionLogger):
    """Factory function to create the appropriate session widget."""
    
    if session_type.lower() in ['hands_review', 'review']:
        return HandsReviewSessionWidget(parent_frame, session, logger)
    elif session_type.lower() in ['gto', 'simulation']:
        return GTOSessionWidget(parent_frame, session, logger)
    else:
        # Default to base widget
        return BotSessionWidget(parent_frame, session, logger)