"""
GameDirector - Central coordinator for all game timing and events.

This is the single source of truth for ALL timing in the poker application.
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
    callback: Optional[Callable] = None
    event_id: str = ""


class GameDirector:
    """
    Central coordinator for all game timing and events.
    
    ARCHITECTURE PRINCIPLE:
    - Single-threaded event-driven design
    - Only GameDirector controls timing
    - Components are pure (no timing logic)
    - All coordination through event scheduling
    """
    
    def __init__(self, state_machine, ui_renderer, audio_manager, session_logger: SessionLogger):
        """Initialize the game director with all required components."""
        self.state_machine = state_machine
        self.ui_renderer = ui_renderer
        self.audio_manager = audio_manager
        self.session_logger = session_logger
        
        # Event system
        self.event_queue: List[ScheduledEvent] = []
        self.is_running = False
        self.event_counter = 0
        
        # Timing control
        self.last_update = time.time()
        
        # Log initialization
        self.session_logger.log_system("INFO", "GAME_DIRECTOR", "GameDirector initialized", {
            "state_machine_type": type(state_machine).__name__,
            "ui_renderer_type": type(ui_renderer).__name__,
            "audio_manager_type": type(audio_manager).__name__
        })
        
    def start(self):
        """Start the game director."""
        self.is_running = True
        self.session_logger.log_system("INFO", "GAME_DIRECTOR", "GameDirector started", {})
        self._start_update_loop()
        
    def stop(self):
        """Stop the game director and clear events."""
        self.is_running = False
        cancelled_events = len(self.event_queue)
        self.event_queue.clear()
        
        self.session_logger.log_system("INFO", "GAME_DIRECTOR", "GameDirector stopped", {
            "cancelled_events": cancelled_events
        })
        
    def schedule_event(self, delay_ms: int, event_type: str, data: Dict[str, Any] = None, callback: Callable = None) -> str:
        """
        Schedule an event to execute after delay_ms milliseconds.
        
        Returns:
            event_id: Unique identifier for the scheduled event
        """
        if data is None:
            data = {}
            
        scheduled_time = time.time() + (delay_ms / 1000.0)
        event_id = f"event_{self.event_counter}"
        self.event_counter += 1
        
        event = ScheduledEvent(
            timestamp=scheduled_time,
            event_type=event_type,
            data=data,
            callback=callback,
            event_id=event_id
        )
        
        self.event_queue.append(event)
        
        self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Scheduled event: {event_type} in {delay_ms}ms", {
            "event_id": event_id,
            "event_type": event_type,
            "delay_ms": delay_ms,
            "data_keys": list(data.keys()),
            "queue_size": len(self.event_queue)
        })
        
        return event_id
        
    def schedule_next_bot_action(self) -> None:
        """Schedule the next bot action if it's a bot's turn."""
        current_action_player_index = self.state_machine.action_player_index
        
        if self._is_bot_turn_next():
            # Use 1.5 second delay for proper bot timing (includes sound + processing time)
            delay_ms = 1500
            
            self.schedule_event(delay_ms, "execute_bot_action", {
                "player_index": current_action_player_index,
                "scheduled_by": "state_machine_transition"
            })
        
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event by its ID."""
        for event in self.event_queue:
            if event.event_id == event_id:
                self.event_queue.remove(event)
                self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Cancelled event: {event_id}", {
                    "event_type": event.event_type
                })
                return True
        return False
        
    def execute_player_action(self, player, action: ActionType, amount: float = 0.0) -> bool:
        """
        Single entry point for ALL player actions.
        
        This is the ONLY way actions should be executed in the system.
        Ensures proper coordination between state, UI, and audio.
        """
        self.session_logger.log_system("INFO", "GAME_DIRECTOR", f"Executing action: {player.name} {action.value} ${amount}", {
            "player": player.name,
            "action": action.value,
            "amount": amount,
            "is_human": player.is_human
        })
        
        # 1. Execute in state machine (synchronous)
        action_successful = self.state_machine.execute_action(player, action, amount)
        
        if action_successful:
            # 2. Update UI immediately (synchronous)
            self._update_ui()
            
            # 3. Schedule sound (non-blocking)
            self._schedule_action_sound(action)
            
            # 4. Add delay for human actions to match bot timing
            if player.is_human:
                self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Scheduling post-human-action delay (500ms)", {
                    "player": player.name,
                    "action": action.value
                })
                # Schedule a 500ms delay after human actions for consistent pacing
                self.schedule_event(500, "human_action_delay_complete", {
                    "player_name": player.name,
                    "action": action.value
                })
            
            # Bot actions are scheduled by schedule_next_bot_action() from state machine transitions
            # No need to schedule here to avoid duplicate events
                
        else:
            self.session_logger.log_system("WARNING", "GAME_DIRECTOR", f"Action failed: {player.name} {action.value}", {
                "player": player.name,
                "action": action.value,
                "amount": amount
            })
            
        return action_successful
        
    def _schedule_action_sound(self, action: ActionType) -> int:
        """Schedule action sound and return duration in milliseconds."""
        try:
            if hasattr(self.audio_manager, 'play_action_sound'):
                # Get sound duration
                duration_seconds = self.audio_manager.get_action_sound_duration(action.value)
                duration_ms = int(duration_seconds * 1000)
                
                # Play sound immediately (non-blocking)
                self.audio_manager.play_action_sound(action.value)
                
                self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Scheduled sound: {action.value}", {
                    "action": action.value,
                    "duration_ms": duration_ms
                })
                
                return duration_ms
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error scheduling sound: {e}", {
                "action": action.value,
                "error": str(e)
            })
            
        return 800  # Default duration if sound fails
        
    def _update_ui(self):
        """Update UI immediately from current state."""
        try:
            if hasattr(self.ui_renderer, 'render_current_state'):
                self.ui_renderer.render_current_state()
            elif hasattr(self.ui_renderer, '_update_from_fpsm_state'):
                self.ui_renderer._update_from_fpsm_state()
            else:
                self.session_logger.log_system("WARNING", "GAME_DIRECTOR", "UI renderer has no update method", {})
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error updating UI: {e}", {
                "error": str(e)
            })
            
    def _is_bot_turn_next(self) -> bool:
        """Check if next player is a bot and game is still active."""
        try:
            # First check if hand/game is still active
            if hasattr(self.state_machine, 'current_state'):
                from .types import PokerState
                current_state = self.state_machine.current_state
                
                # Log current state for debugging
                self.session_logger.log_system("DEBUG", "HIGHLIGHT_DEBUG", f"Checking bot turn - current state: {current_state}", {
                    "current_state": str(current_state),
                    "action_player_index": getattr(self.state_machine, 'action_player_index', -1)
                })
                
                # Don't schedule bot actions if hand is over
                if current_state in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                    self.session_logger.log_system("DEBUG", "HIGHLIGHT_DEBUG", f"Hand is over - not scheduling bot action", {
                        "current_state": str(current_state)
                    })
                    return False
            
            # Check if there's a valid action player
            action_player_idx = self.state_machine.action_player_index
            if (action_player_idx >= 0 and action_player_idx < len(self.state_machine.game_state.players)):
                current_player = self.state_machine.game_state.players[action_player_idx]
                is_bot = not current_player.is_human
                
                self.session_logger.log_system("DEBUG", "HIGHLIGHT_DEBUG", f"Action player check result", {
                    "action_player_index": action_player_idx,
                    "player_name": current_player.name,
                    "is_human": current_player.is_human,
                    "is_bot": is_bot
                })
                
                return is_bot
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error checking bot turn: {e}", {
                "error": str(e)
            })
            
        return False
        
    def _start_update_loop(self):
        """Start the main update loop (Tkinter-based)."""
        if hasattr(self.ui_renderer, 'after'):
            self._tkinter_update_loop()
        else:
            self.session_logger.log_system("WARNING", "GAME_DIRECTOR", "No Tkinter update loop available", {})
            
    def _tkinter_update_loop(self):
        """Tkinter-compatible update loop (~60 FPS)."""
        if self.is_running:
            self.update()
            # Schedule next update
            try:
                self.ui_renderer.after(16, self._tkinter_update_loop)  # ~60 FPS
            except RecursionError:
                # In test environments, prevent infinite recursion
                self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", "Stopping update loop (test mode)", {})
            
    def update(self):
        """Process all scheduled events (called every frame)."""
        now = time.time()
        ready_events = [e for e in self.event_queue if e.timestamp <= now]
        
        for event in ready_events:
            self._execute_event(event)
            self.event_queue.remove(event)
            
        self.last_update = now
        
    def _execute_event(self, event: ScheduledEvent):
        """Execute a scheduled event."""
        self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Executing scheduled event: {event.event_type}", {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "data": event.data
        })
        
        try:
            if event.event_type == "execute_bot_action":
                self._handle_bot_action_event(event.data)
            elif event.event_type == "update_ui":
                self._update_ui()
            elif event.event_type == "play_sound":
                self._handle_sound_event(event.data)
            elif event.event_type == "human_action_delay_complete":
                self._handle_human_action_delay_complete(event.data)
            elif event.event_type == "hands_review_auto_advance":
                self._handle_hands_review_auto_advance(event.data)
            elif event.event_type == "custom":
                if event.callback:
                    event.callback(event.data)
            else:
                self.session_logger.log_system("WARNING", "GAME_DIRECTOR", f"Unknown event type: {event.event_type}", {
                    "event_type": event.event_type
                })
                    
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error executing event {event.event_type}: {e}", {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "error": str(e)
            })
            
    def _handle_bot_action_event(self, data: Dict[str, Any]):
        """Handle bot action execution."""
        player_index = data.get("player_index", -1)
        
        # Validate player and turn
        if not self._validate_bot_action(player_index):
            return
            
        current_player = self.state_machine.game_state.players[player_index]
        
        # Get bot decision
        action, amount = self._get_bot_decision(current_player)
        
        # Execute through this director (maintains single flow)
        self.execute_player_action(current_player, action, amount)
        
    def _validate_bot_action(self, player_index: int) -> bool:
        """Validate that bot action should execute."""
        # Check player index validity
        if not (0 <= player_index < len(self.state_machine.game_state.players)):
            self.session_logger.log_system("WARNING", "GAME_DIRECTOR", f"Invalid bot player index: {player_index}", {
                "player_index": player_index,
                "num_players": len(self.state_machine.game_state.players)
            })
            return False
            
        # Check it's still this player's turn
        if player_index != self.state_machine.action_player_index:
            self.session_logger.log_system("WARNING", "GAME_DIRECTOR", f"Bot action player mismatch", {
                "expected": player_index,
                "current": self.state_machine.action_player_index
            })
            return False
            
        current_player = self.state_machine.game_state.players[player_index]
        
        # Check player is actually a bot
        if current_player.is_human:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Attempted bot action on human player: {current_player.name}", {
                "player": current_player.name,
                "player_index": player_index
            })
            return False
            
        return True
        
    def _get_bot_decision(self, bot_player):
        """Get bot's decision (delegates to state machine)."""
        try:
            if hasattr(self.state_machine, '_get_bot_strategy_decision'):
                return self.state_machine._get_bot_strategy_decision(bot_player)
            else:
                # Fallback decision
                return ActionType.FOLD, 0.0
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error getting bot decision: {e}", {
                "player": bot_player.name,
                "error": str(e)
            })
            return ActionType.FOLD, 0.0
            
    def _handle_sound_event(self, data: Dict[str, Any]):
        """Handle sound playback event."""
        sound_name = data.get("sound_name", "")
        if sound_name and hasattr(self.audio_manager, 'play_sound'):
            try:
                self.audio_manager.play_sound(sound_name)
            except Exception as e:
                self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error playing sound: {e}", {
                    "sound_name": sound_name,
                    "error": str(e)
                })
    
    def _handle_human_action_delay_complete(self, data: Dict[str, Any]):
        """Handle completion of human action delay (for consistent pacing)."""
        player_name = data.get("player_name", "Unknown")
        action = data.get("action", "unknown")
        
        self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Human action delay completed for {player_name} {action}", {
            "player_name": player_name,
            "action": action
        })
        
        # After human action delay, check if next player is a bot and schedule their action
        if self._is_bot_turn_next():
            self.schedule_next_bot_action()
            
    def _handle_hands_review_auto_advance(self, data: Dict[str, Any]):
        """Handle hands review auto-advance event."""
        source = data.get("source", "unknown")
        
        self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Handling hands review auto-advance", {
            "source": source
        })
        
        # Call the state machine's auto-advance handler
        if hasattr(self.state_machine, 'handle_auto_advance_event'):
            try:
                self.state_machine.handle_auto_advance_event()
            except Exception as e:
                self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error in hands review auto-advance: {e}", {
                    "error": str(e),
                    "source": source
                })
        else:
            self.session_logger.log_system("WARNING", "GAME_DIRECTOR", "State machine does not support auto-advance events", {})
                
    def get_current_state(self) -> Dict[str, Any]:
        """Get current game state (for UI rendering)."""
        try:
            return self.state_machine.get_game_info()
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error getting game state: {e}", {
                "error": str(e)
            })
            return {}
            
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about GameDirector state."""
        return {
            "is_running": self.is_running,
            "event_queue_size": len(self.event_queue),
            "pending_events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "time_remaining": max(0, e.timestamp - time.time())
                }
                for e in self.event_queue
            ],
            "last_update": self.last_update,
            "current_time": time.time()
        }
