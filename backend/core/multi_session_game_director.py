"""
Multi-Session GameDirector - Central coordinator for all game timing and events.

This is the single source of truth for ALL timing in the poker application,
supporting both Practice Sessions and Hands Review simultaneously.
Follows the event-driven architecture pattern to eliminate timing conflicts.
"""

import time
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass

from .types import ActionType
from .session_logger import SessionLogger


@dataclass
class ScheduledEvent:
    """A scheduled event in the game director queue."""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    session_id: str  # 'practice' or 'hands_review'
    callback: Optional[Callable] = None
    event_id: str = ""


@dataclass 
class SessionComponents:
    """Components for a single game session."""
    state_machine: Any
    ui_renderer: Any
    audio_manager: Any
    session_type: str  # 'practice' or 'hands_review'
    is_active: bool = False


class MultiSessionGameDirector:
    """
    Central coordinator for all game timing and events across multiple sessions.
    
    ARCHITECTURE PRINCIPLE:
    - Single-threaded, event-driven design
    - All timing decisions made here
    - No threading.Timer usage elsewhere
    - Components request timing via events
    - Supports multiple sessions (practice + hands review)
    - Seamless tab switching without timing conflicts
    """
    
    def __init__(self, session_logger: SessionLogger):
        """Initialize the multi-session GameDirector."""
        self.session_logger = session_logger
        
        # Multi-session support
        self.active_session: Optional[str] = None  # 'practice' | 'hands_review' | None
        self.sessions: Dict[str, SessionComponents] = {}
        
        # Event system
        self.event_queue: List[ScheduledEvent] = []
        self.is_running = False
        self.event_counter = 0
        
        # Timing control
        self.last_update = time.time()
        
        # Log initialization
        self.session_logger.log_system("INFO", "MULTI_GAME_DIRECTOR", "Multi-Session GameDirector initialized", {})
        
    def register_session(self, session_id: str, state_machine, ui_renderer, audio_manager, session_type: str):
        """Register a new session with the GameDirector."""
        self.sessions[session_id] = SessionComponents(
            state_machine=state_machine,
            ui_renderer=ui_renderer,
            audio_manager=audio_manager,
            session_type=session_type,
            is_active=False
        )
        
        # Set the GameDirector reference in the state machine
        if hasattr(state_machine, 'set_game_director'):
            state_machine.set_game_director(self)
            
        self.session_logger.log_system("INFO", "MULTI_GAME_DIRECTOR", f"Registered {session_type} session", {
            "session_id": session_id,
            "session_type": session_type,
            "state_machine_type": type(state_machine).__name__,
            "ui_renderer_type": type(ui_renderer).__name__
        })
    
    def activate_session(self, session_id: str):
        """Switch to a different session."""
        if session_id not in self.sessions:
            self.session_logger.log_system("ERROR", "MULTI_GAME_DIRECTOR", f"Session not found: {session_id}", {})
            return False
            
        # Deactivate current session
        if self.active_session and self.active_session in self.sessions:
            self.sessions[self.active_session].is_active = False
            
        # Activate new session
        self.active_session = session_id
        self.sessions[session_id].is_active = True
        
        self.session_logger.log_system("INFO", "MULTI_GAME_DIRECTOR", f"Switched to session: {session_id}", {
            "session_type": self.sessions[session_id].session_type
        })
        return True
        
    def get_active_session(self) -> Optional[SessionComponents]:
        """Get the currently active session components."""
        if self.active_session and self.active_session in self.sessions:
            return self.sessions[self.active_session]
        return None
        
    def start(self):
        """Start the multi-session game director."""
        self.is_running = True
        self.session_logger.log_system("INFO", "MULTI_GAME_DIRECTOR", "Multi-Session GameDirector started", {
            "registered_sessions": list(self.sessions.keys())
        })
        self._start_update_loop()
        
    def stop(self):
        """Stop the game director and clear events."""
        self.is_running = False
        cancelled_events = len(self.event_queue)
        self.event_queue.clear()
        
        # Deactivate all sessions
        for session in self.sessions.values():
            session.is_active = False
            
        self.session_logger.log_system("INFO", "MULTI_GAME_DIRECTOR", "Multi-Session GameDirector stopped", {
            "cancelled_events": cancelled_events
        })
        
    def _start_update_loop(self):
        """Start the main update loop for Tkinter integration."""
        if hasattr(self, '_schedule_next_update'):
            return  # Already scheduled
            
        def update_callback():
            if self.is_running:
                self.update()
                # Schedule next update
                active_session = self.get_active_session()
                if active_session and active_session.ui_renderer:
                    active_session.ui_renderer.after(50, update_callback)  # 20 FPS
                    
        # Start the update loop using the active UI renderer
        active_session = self.get_active_session()
        if active_session and active_session.ui_renderer:
            active_session.ui_renderer.after(50, update_callback)
        self._schedule_next_update = True
        
    def update(self):
        """Process events - called regularly by Tkinter."""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Process due events for active session only
        active_session = self.get_active_session()
        if not active_session:
            return
            
        processed_count = 0
        remaining_events = []
        
        for event in self.event_queue:
            if event.timestamp <= current_time and event.session_id == self.active_session:
                self._execute_event(event)
                processed_count += 1
            else:
                remaining_events.append(event)
                
        self.event_queue = remaining_events
        
        if processed_count > 0:
            self.session_logger.log_system("DEBUG", "MULTI_GAME_DIRECTOR", f"Processed {processed_count} events for {self.active_session}", {})
            
    def schedule_event(self, delay_ms: int, event_type: str, data: Dict[str, Any] = None, session_id: str = None):
        """Schedule an event for execution after a delay."""
        if data is None:
            data = {}
            
        # Use active session if no session specified
        if session_id is None:
            session_id = self.active_session
            
        if session_id is None:
            self.session_logger.log_system("WARNING", "MULTI_GAME_DIRECTOR", "No active session for event scheduling", {
                "event_type": event_type
            })
            return
            
        timestamp = time.time() * 1000 + delay_ms
        self.event_counter += 1
        
        event = ScheduledEvent(
            timestamp=timestamp,
            event_type=event_type,
            data=data,
            session_id=session_id,
            event_id=f"event_{self.event_counter}"
        )
        
        self.event_queue.append(event)
        
        self.session_logger.log_system("DEBUG", "MULTI_GAME_DIRECTOR", f"Scheduled event: {event_type}", {
            "delay_ms": delay_ms,
            "session_id": session_id,
            "event_id": event.event_id,
            "data": data
        })
        
    def _execute_event(self, event: ScheduledEvent):
        """Execute a scheduled event for the specified session."""
        active_session = self.get_active_session()
        if not active_session or event.session_id != self.active_session:
            return  # Skip events for inactive sessions
            
        try:
            if event.event_type == "bot_action":
                self._handle_bot_action(event.data, active_session)
            elif event.event_type == "human_action_delay_complete":
                self._handle_human_action_delay_complete(event.data, active_session)
            elif event.event_type == "hands_review_auto_advance":
                self._handle_hands_review_auto_advance(event.data, active_session)
            else:
                self.session_logger.log_system("WARNING", "MULTI_GAME_DIRECTOR", f"Unknown event type: {event.event_type}", {
                    "session_id": event.session_id
                })
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "MULTI_GAME_DIRECTOR", f"Error executing event: {e}", {
                "event_type": event.event_type,
                "session_id": event.session_id,
                "error": str(e)
            })
            
    def execute_player_action(self, player, action: ActionType, amount: float = 0.0):
        """Execute a player action in the active session."""
        active_session = self.get_active_session()
        if not active_session:
            self.session_logger.log_system("ERROR", "MULTI_GAME_DIRECTOR", "No active session for player action", {})
            return False
            
        # Route to the appropriate session's state machine
        return self._execute_player_action_for_session(player, action, amount, active_session)
        
    def _execute_player_action_for_session(self, player, action: ActionType, amount: float, session: SessionComponents):
        """Execute a player action for a specific session."""
        try:
            success = session.state_machine.execute_action(player, action, amount)
            
            if success:
                self.session_logger.log_system("DEBUG", "MULTI_GAME_DIRECTOR", f"Action executed: {player.name} {action.value} ${amount:.2f}", {
                    "session_type": session.session_type,
                    "player": player.name,
                    "action": action.value,
                    "amount": amount
                })
                
                # Schedule next bot action if needed (for practice sessions)
                if session.session_type == 'practice':
                    self.schedule_next_bot_action()
                    
                # Add delay for human actions
                if player.is_human:
                    self.schedule_event(500, "human_action_delay_complete", {
                        "player_name": player.name,
                        "action_type": action.value
                    })
                    
            return success
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "MULTI_GAME_DIRECTOR", f"Error executing player action: {e}", {
                "session_type": session.session_type,
                "player": player.name,
                "action": action.value,
                "error": str(e)
            })
            return False
            
    def schedule_next_bot_action(self):
        """Schedule the next bot action for the active practice session."""
        active_session = self.get_active_session()
        if not active_session:
            return
            
        # HANDS REVIEW: No delays - all actions are immediate historical replays
        if active_session.session_type == 'hands_review':
            return  # No automatic bot scheduling for hands review
            
        # PRACTICE SESSION: Normal bot delays
        if active_session.session_type == 'practice':
            if hasattr(active_session.state_machine, 'action_player_index'):
                player_index = active_session.state_machine.action_player_index
                
                if self._is_bot_turn_next(active_session.state_machine):
                    delay_ms = 1500  # 1.5 second delay for bots in practice
                    self.schedule_event(delay_ms, "bot_action", {
                        "player_index": player_index
                    })
                
    def _is_bot_turn_next(self, state_machine) -> bool:
        """Check if it's a bot's turn next."""
        # Implementation from original GameDirector
        from .types import PokerState
        
        if state_machine.current_state in [PokerState.END_HAND, PokerState.SHOWDOWN]:
            return False
            
        if (hasattr(state_machine, 'action_player_index') and 
            state_machine.action_player_index >= 0 and 
            state_machine.action_player_index < len(state_machine.game_state.players)):
            
            current_player = state_machine.game_state.players[state_machine.action_player_index]
            return not current_player.is_human
            
        return False
        
    def _handle_bot_action(self, data: Dict[str, Any], session: SessionComponents):
        """Handle bot action execution for practice sessions."""
        if session.session_type != 'practice':
            return
            
        # Implementation from original GameDirector
        if hasattr(session.state_machine, '_execute_bot_action_if_needed'):
            session.state_machine._execute_bot_action_if_needed()
            
    def _handle_human_action_delay_complete(self, data: Dict[str, Any], session: SessionComponents):
        """Handle completion of human action delay."""
        if session.session_type == 'practice':
            self.schedule_next_bot_action()
            
    def _handle_hands_review_auto_advance(self, data: Dict[str, Any], session: SessionComponents):
        """Handle hands review auto-advance event."""
        if session.session_type != 'hands_review':
            return
            
        if hasattr(session.state_machine, 'handle_auto_advance_event'):
            session.state_machine.handle_auto_advance_event()
