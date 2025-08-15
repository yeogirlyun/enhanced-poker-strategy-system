"""
GameDirector - Central coordinator for all game timing and events.

This is the single source of truth for ALL timing in the poker application.
Follows the event-driven architecture pattern to eliminate timing conflicts.
"""

import time
from typing import List, Dict, Callable, Any

from .poker_types import ActionType
from .session_logger import SessionLogger
from .multi_session_game_director import ScheduledEvent


class GameDirector:
    """
    Central coordinator for all game timing and events.

    ARCHITECTURE PRINCIPLE:
    - Single-threaded event-driven design
    - Only GameDirector controls timing
    - Components are pure (no timing logic)
    - All coordination through event scheduling
    """

    def __init__(
        self,
        state_machine,
        ui_renderer,
        audio_manager,
        session_logger: SessionLogger,
    ):
        """Initialize the game director with all required components."""
        self.state_machine = state_machine
        self.ui_renderer = ui_renderer
        self.audio_manager = audio_manager
        self.session_logger = session_logger

        # Event system
        self.event_queue: List[ScheduledEvent] = []
        self.is_running = False
        self.event_counter = 0

        # Event listeners for UI updates
        self.event_listeners: List[Any] = []

        # Timing control
        self.last_update = time.time()

        # Hands Review Timeline System
        self.hands_review_timeline: List[Dict[str, Any]] = []
        self.current_timeline_index: int = 0
        self.is_hands_review_mode: bool = False
        self.hands_review_play_speed_ms: int = 2000  # 2 seconds between states

        # Log initialization
        self.session_logger.log_system(
            "INFO",
            "GAME_DIRECTOR",
            "GameDirector initialized",
            {
                "state_machine_type": type(state_machine).__name__,
                "ui_renderer_type": type(ui_renderer).__name__,
                "audio_manager_type": type(audio_manager).__name__,
            },
        )

    def add_event_listener(self, listener: Any):
        """Add an event listener for UI updates."""
        if listener not in self.event_listeners:
            self.event_listeners.append(listener)
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "Event listener added",
                {
                    "listener_type": type(listener).__name__,
                    "total_listeners": len(self.event_listeners),
                },
            )

    def remove_event_listener(self, listener: Any):
        """Remove an event listener."""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "Event listener removed",
                {
                    "listener_type": type(listener).__name__,
                    "total_listeners": len(self.event_listeners),
                },
            )

    def _emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Emit an event to all registered listeners."""
        if data is None:
            data = {}

        # Import here to avoid circular imports
        from .flexible_poker_state_machine import GameEvent

        event = GameEvent(
            event_type=event_type, timestamp=time.time(), data=data
        )

        for listener in self.event_listeners:
            try:
                if hasattr(listener, "on_event"):
                    listener.on_event(event)
            except Exception as e:
                self.session_logger.log_system(
                    "ERROR",
                    "GAME_DIRECTOR",
                    f"Error notifying listener: {e}",
                    {
                        "error": str(e),
                        "listener_type": type(listener).__name__,
                    },
                )

    def start(self):
        """Start the game director."""
        self.is_running = True
        self.session_logger.log_system(
            "INFO", "GAME_DIRECTOR", "GameDirector started", {}
        )
        self._start_update_loop()

    def stop(self):
        """Stop the game director and clear events."""
        self.is_running = False
        cancelled_events = len(self.event_queue)
        self.event_queue.clear()

        self.session_logger.log_system(
            "INFO",
            "GAME_DIRECTOR",
            "GameDirector stopped",
            {"cancelled_events": cancelled_events},
        )

    def schedule_event(
        self,
        delay_ms: int,
        event_type: str,
        data: Dict[str, Any] = None,
        callback: Callable = None,
    ) -> str:
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
            session_id="hands_review",  # Default session ID for main GameDirector
            callback=callback,
            event_id=event_id,
        )

        self.event_queue.append(event)

        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            f"Scheduled event: {event_type} in {delay_ms}ms",
            {
                "event_id": event_id,
                "event_type": event_type,
                "delay_ms": delay_ms,
                "data_keys": list(data.keys()),
                "queue_size": len(self.event_queue),
            },
        )

        return event_id

    def schedule_next_bot_action(self) -> None:
        """Schedule the next bot action if it's a bot's turn."""
        current_action_player_index = self.state_machine.action_player_index

        if self._is_bot_turn_next():
            # Use 1.5 second delay for proper bot timing (includes sound +
            # processing time)
            delay_ms = 1500

            self.schedule_event(
                delay_ms,
                "execute_bot_action",
                {
                    "player_index": current_action_player_index,
                    "scheduled_by": "state_machine_transition",
                },
            )

    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event by its ID."""
        for event in self.event_queue:
            if event.event_id == event_id:
                self.event_queue.remove(event)
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    f"Cancelled event: {event_id}",
                    {"event_type": event.event_type},
                )
                return True
        return False

    def execute_player_action(
        self, player, action: ActionType, amount: float = 0.0
    ) -> bool:
        """
        Single entry point for ALL player actions.

        This is the ONLY way actions should be executed in the system.
        Ensures proper coordination between state, UI, and audio.
        """
        self.session_logger.log_system(
            "INFO",
            "GAME_DIRECTOR",
            f"Executing action: {
                player.name} {
                action.value} ${amount}",
            {
                "player": player.name,
                "action": action.value,
                "amount": amount,
                "is_human": player.is_human,
            },
        )

        # 1. Execute in state machine (synchronous)
        action_successful = self.state_machine.execute_action(
            player, action, amount
        )

        if action_successful:
            # 2. Update UI immediately (synchronous)
            self._update_ui()

            # 3. Schedule sound (non-blocking)
            self._schedule_action_sound(action)

            # 4. Add delay for human actions to match bot timing
            if player.is_human:
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Scheduling post-human-action delay (500ms)",
                    {"player": player.name, "action": action.value},
                )
                # Schedule a 500ms delay after human actions for consistent
                # pacing
                self.schedule_event(
                    500,
                    "human_action_delay_complete",
                    {"player_name": player.name, "action": action.value},
                )

            # Bot actions are scheduled by schedule_next_bot_action() from state machine transitions
            # No need to schedule here to avoid duplicate events

        else:
            self.session_logger.log_system(
                "WARNING",
                "GAME_DIRECTOR",
                f"Action failed: {
                    player.name} {
                    action.value}",
                {
                    "player": player.name,
                    "action": action.value,
                    "amount": amount,
                },
            )

        return action_successful

    def _schedule_action_sound(self, action: ActionType) -> int:
        """Schedule action sound and return duration in milliseconds."""
        try:
            if hasattr(self.audio_manager, "play_action_sound"):
                # Get sound duration
                duration_seconds = (
                    self.audio_manager.get_action_sound_duration(action.value)
                )
                duration_ms = int(duration_seconds * 1000)

                # Play sound immediately (non-blocking)
                self.audio_manager.play_action_sound(action.value)

                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    f"Scheduled sound: {
                        action.value}",
                    {"action": action.value, "duration_ms": duration_ms},
                )

                return duration_ms

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error scheduling sound: {e}",
                {"action": action.value, "error": str(e)},
            )

        return 800  # Default duration if sound fails

    def _update_ui(self):
        """Update UI immediately from current state."""
        try:
            if hasattr(self.ui_renderer, "render_current_state"):
                self.ui_renderer.render_current_state()
            elif hasattr(self.ui_renderer, "_update_from_fpsm_state"):
                self.ui_renderer._update_from_fpsm_state()
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    "UI renderer has no update method",
                    {},
                )

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error updating UI: {e}",
                {"error": str(e)},
            )

    def _is_bot_turn_next(self) -> bool:
        """Check if next player is a bot and game is still active."""
        try:
            # First check if hand/game is still active
            if hasattr(self.state_machine, "current_state"):
                from .poker_types import PokerState

                current_state = self.state_machine.current_state

                # Log current state for debugging
                self.session_logger.log_system(
                    "DEBUG",
                    "HIGHLIGHT_DEBUG",
                    f"Checking bot turn - current state: {current_state}",
                    {
                        "current_state": str(current_state),
                        "action_player_index": getattr(
                            self.state_machine, "action_player_index", -1
                        ),
                    },
                )

                # Don't schedule bot actions if hand is over
                if current_state in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                    self.session_logger.log_system(
                        "DEBUG",
                        "HIGHLIGHT_DEBUG",
                        "Hand is over - not scheduling bot action",
                        {"current_state": str(current_state)},
                    )
                    return False

            # Check if there's a valid action player
            action_player_idx = self.state_machine.action_player_index
            if action_player_idx >= 0 and action_player_idx < len(
                self.state_machine.game_state.players
            ):
                current_player = self.state_machine.game_state.players[
                    action_player_idx
                ]
                is_bot = not current_player.is_human

                self.session_logger.log_system(
                    "DEBUG",
                    "HIGHLIGHT_DEBUG",
                    "Action player check result",
                    {
                        "action_player_index": action_player_idx,
                        "player_name": current_player.name,
                        "is_human": current_player.is_human,
                        "is_bot": is_bot,
                    },
                )

                return is_bot

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error checking bot turn: {e}",
                {"error": str(e)},
            )

        return False

    def _start_update_loop(self):
        """Start the main update loop (Tkinter-based)."""
        if hasattr(self.ui_renderer, "after"):
            self._tkinter_update_loop()
        else:
            self.session_logger.log_system(
                "WARNING",
                "GAME_DIRECTOR",
                "No Tkinter update loop available",
                {},
            )

    def _tkinter_update_loop(self):
        """Tkinter-compatible update loop (~60 FPS)."""
        if self.is_running:
            self.update()
            # Schedule next update
            try:
                self.ui_renderer.after(
                    16, self._tkinter_update_loop
                )  # ~60 FPS
            except RecursionError:
                # In test environments, prevent infinite recursion
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Stopping update loop (test mode)",
                    {},
                )

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
        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            f"Executing scheduled event: {
                event.event_type}",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "data": event.data,
            },
        )

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
            elif event.event_type == "hands_review_play_advance":
                self._handle_hands_review_play_advance(event.data)
            elif event.event_type == "custom":
                if event.callback:
                    event.callback(event.data)
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    f"Unknown event type: {
                        event.event_type}",
                    {"event_type": event.event_type},
                )

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error executing event {
                    event.event_type}: {e}",
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "error": str(e),
                },
            )

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
        if not (
            0 <= player_index < len(self.state_machine.game_state.players)
        ):
            self.session_logger.log_system(
                "WARNING",
                "GAME_DIRECTOR",
                f"Invalid bot player index: {player_index}",
                {
                    "player_index": player_index,
                    "num_players": len(self.state_machine.game_state.players),
                },
            )
            return False

        # Check it's still this player's turn
        if player_index != self.state_machine.action_player_index:
            self.session_logger.log_system(
                "WARNING",
                "GAME_DIRECTOR",
                "Bot action player mismatch",
                {
                    "expected": player_index,
                    "current": self.state_machine.action_player_index,
                },
            )
            return False

        current_player = self.state_machine.game_state.players[player_index]

        # Check player is actually a bot
        if current_player.is_human:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Attempted bot action on human player: {
                    current_player.name}",
                {"player": current_player.name, "player_index": player_index},
            )
            return False

        return True

    def _get_bot_decision(self, bot_player):
        """Get bot's decision (delegates to state machine)."""
        try:
            if hasattr(self.state_machine, "_get_bot_strategy_decision"):
                return self.state_machine._get_bot_strategy_decision(
                    bot_player
                )
            else:
                # Fallback decision
                return ActionType.FOLD, 0.0

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error getting bot decision: {e}",
                {"player": bot_player.name, "error": str(e)},
            )
            return ActionType.FOLD, 0.0

    def _handle_sound_event(self, data: Dict[str, Any]):
        """Handle sound playback event."""
        sound_name = data.get("sound_name", "")
        if sound_name and hasattr(self.audio_manager, "play_sound"):
            try:
                self.audio_manager.play_sound(sound_name)
            except Exception as e:
                self.session_logger.log_system(
                    "ERROR",
                    "GAME_DIRECTOR",
                    f"Error playing sound: {e}",
                    {"sound_name": sound_name, "error": str(e)},
                )

    def _handle_human_action_delay_complete(self, data: Dict[str, Any]):
        """Handle completion of human action delay (for consistent pacing)."""
        player_name = data.get("player_name", "Unknown")
        action = data.get("action", "unknown")

        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            f"Human action delay completed for {player_name} {action}",
            {"player_name": player_name, "action": action},
        )

        # After human action delay, check if next player is a bot and schedule
        # their action
        if self._is_bot_turn_next():
            self.schedule_next_bot_action()

    def _handle_hands_review_auto_advance(self, data: Dict[str, Any]):
        """Handle hands review auto-advance event."""
        source = data.get("source", "unknown")

        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            "Handling hands review auto-advance",
            {"source": source},
        )

        # Call the state machine's auto-advance handler
        if hasattr(self.state_machine, "handle_auto_advance_event"):
            try:
                self.state_machine.handle_auto_advance_event()
            except Exception as e:
                self.session_logger.log_system(
                    "ERROR",
                    "GAME_DIRECTOR",
                    f"Error in hands review auto-advance: {e}",
                    {"error": str(e), "source": source},
                )
        else:
            self.session_logger.log_system(
                "WARNING",
                "GAME_DIRECTOR",
                "State machine does not support auto-advance events",
                {},
            )

    def _handle_hands_review_play_advance(self, data: Dict[str, Any]):
        """Handle hands review play mode advance event."""
        current_index = data.get("current_index", 0)

        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            "Handling hands review play advance",
            {"current_index": current_index},
        )

        # Move to next timeline state
        if self.next_timeline_state():
            # Schedule next advance if we're still in play mode
            if self.is_hands_review_mode:
                self.schedule_event(
                    delay_ms=self.hands_review_play_speed_ms,
                    event_type="hands_review_play_advance",
                    data={"current_index": self.current_timeline_index},
                )
        else:
            # Reached end of timeline, stop play mode
            self.stop_hands_review_play()

    def get_current_state(self) -> Dict[str, Any]:
        """Get current game state (for UI rendering)."""
        try:
            return self.state_machine.get_game_info()
        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error getting game state: {e}",
                {"error": str(e)},
            )
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
                    "time_remaining": max(0, e.timestamp - time.time()),
                }
                for e in self.event_queue
            ],
            "last_update": self.last_update,
            "current_time": time.time(),
            "hands_review_mode": self.is_hands_review_mode,
            "timeline_index": self.current_timeline_index,
            "timeline_size": len(self.hands_review_timeline),
        }

    # ===== HANDS REVIEW TIMELINE SYSTEM =====

    def load_hands_review_timeline(self, hand_data: Dict[str, Any]) -> bool:
        """
        Load a hand and pre-simulate the complete timeline.

        This method runs the entire hand simulation and stores every state
        for instant navigation without re-computation.
        """
        try:
            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "Loading hands review timeline",
                {"hand_id": hand_data.get("hand_id", "unknown")},
            )

            # Reset timeline state
            self.hands_review_timeline.clear()
            self.current_timeline_index = 0
            self.is_hands_review_mode = True

            # Load hand into state machine
            if hasattr(self.state_machine, "load_hand_for_review"):
                success = self.state_machine.load_hand_for_review(hand_data)
                if not success:
                    return False
            else:
                self.session_logger.log_system(
                    "ERROR",
                    "GAME_DIRECTOR",
                    "State machine does not support hands review",
                    {},
                )
                return False

            # Pre-simulate the complete hand
            self._simulate_complete_hand()

            # Store initial state
            self._store_current_timeline_state("hand_loaded")

            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "Hands review timeline loaded successfully",
                {
                    "timeline_states": len(self.hands_review_timeline),
                    "hand_id": hand_data.get("hand_id", "unknown"),
                },
            )

            return True

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error loading hands review timeline: {e}",
                {"error": str(e), "hand_data": hand_data},
            )
            return False

    def _simulate_complete_hand(self):
        """Pre-simulate the entire hand and store every state."""
        try:
            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "Starting complete hand simulation",
                {},
            )

            # Enable timeline creation mode in PSM - completely passive, no
            # actions/events
            if hasattr(self.state_machine, "enable_timeline_creation_mode"):
                self.state_machine.enable_timeline_creation_mode()
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Timeline creation mode enabled in PSM",
                    {},
                )

            # Get initial state
            self._store_current_timeline_state("initial_state")

            # Simulate through all actions
            action_index = 0
            while True:
                # Check if there are more actions
                if hasattr(self.state_machine, "can_step_forward"):
                    if not self.state_machine.can_step_forward():
                        break

                # Step forward
                if hasattr(self.state_machine, "step_forward"):
                    success = self.state_machine.step_forward()
                    if not success:
                        break

                # Store state after each action
                action_index += 1
                self._store_current_timeline_state(f"action_{action_index}")

                # Safety check to prevent infinite loops
                if action_index > 1000:
                    self.session_logger.log_system(
                        "WARNING",
                        "GAME_DIRECTOR",
                        "Simulation exceeded 1000 actions, stopping",
                        {"action_index": action_index},
                    )
                    break

            # Store final state
            self._store_current_timeline_state("final_state")

            # Disable timeline creation mode to resume normal operation
            if hasattr(self.state_machine, "disable_timeline_creation_mode"):
                self.state_machine.disable_timeline_creation_mode()
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Timeline creation mode disabled in PSM",
                    {},
                )

            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "Complete hand simulation finished",
                {
                    "total_actions": action_index,
                    "total_states": len(self.hands_review_timeline),
                },
            )

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error in complete hand simulation: {e}",
                {"error": str(e)},
            )

    def _store_current_timeline_state(self, state_name: str):
        """Store the current game state in the timeline."""
        try:
            # Get complete game state
            game_state = self.state_machine.get_game_info()

            # Create timeline state entry
            timeline_state = {
                "state_name": state_name,
                "timestamp": time.time(),
                "game_state": game_state.copy(),
                "board_cards": (
                    self.state_machine.game_state.board.copy()
                    if hasattr(self.state_machine, "game_state")
                    else []
                ),
                "pot_amount": (
                    self.state_machine.game_state.pot
                    if hasattr(self.state_machine, "game_state")
                    else 0.0
                ),
                "current_street": (
                    self.state_machine.current_state.name
                    if hasattr(self.state_machine, "current_state")
                    else "unknown"
                ),
                "player_states": [],
            }

            # Store player states
            if hasattr(self.state_machine, "game_state") and hasattr(
                self.state_machine.game_state, "players"
            ):
                for i, player in enumerate(
                    self.state_machine.game_state.players
                ):
                    player_state = {
                        "index": i,
                        "name": player.name,
                        "cards": (
                            player.cards.copy()
                            if hasattr(player, "cards")
                            else []
                        ),
                        "current_bet": player.current_bet,
                        "stack": player.stack,
                        "has_folded": player.has_folded,
                        "is_active": player.is_active,
                    }
                    timeline_state["player_states"].append(player_state)

            # Add to timeline
            self.hands_review_timeline.append(timeline_state)

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error storing timeline state: {e}",
                {"error": str(e), "state_name": state_name},
            )

    def display_timeline_state(self, index: int) -> bool:
        """
        Display a specific timeline state.

        This method restores the game state to a specific point in the timeline
        without re-running the simulation.
        """
        try:
            if not self.is_hands_review_mode:
                self.session_logger.log_system(
                    "WARNING", "GAME_DIRECTOR", "Not in hands review mode", {}
                )
                return False

            if index < 0 or index >= len(self.hands_review_timeline):
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    f"Invalid timeline index: {index}",
                    {
                        "index": index,
                        "timeline_size": len(self.hands_review_timeline),
                    },
                )
                return False

            # Get the timeline state
            timeline_state = self.hands_review_timeline[index]

            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                f"🎬 DISPLAYING TIMELINE STATE {index}",
                {
                    "state_name": timeline_state["state_name"],
                    "current_street": timeline_state["current_street"],
                    "pot_amount": timeline_state["pot_amount"],
                    "board_cards": timeline_state["board_cards"],
                    "player_count": len(timeline_state["player_states"]),
                },
            )

            # STEP 1: Restore the game state from timeline
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "🔄 STEP 1: Restoring game state from timeline",
                {},
            )
            self._restore_timeline_state(timeline_state)

            # STEP 2: Update current index
            self.current_timeline_index = index
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                f"🔄 STEP 2: Updated current index to {index}",
                {},
            )

            # STEP 3: Force UI update by triggering state machine update
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "🔄 STEP 3: Forcing UI update via state machine",
                {},
            )
            if (
                hasattr(self.state_machine, "ui_renderer")
                and self.state_machine.ui_renderer
            ):
                if hasattr(
                    self.state_machine.ui_renderer, "_update_from_fpsm_state"
                ):
                    self.session_logger.log_system(
                        "DEBUG",
                        "GAME_DIRECTOR",
                        "🔄 Calling _update_from_fpsm_state on UI renderer",
                        {},
                    )
                    self.state_machine.ui_renderer._update_from_fpsm_state()
                else:
                    self.session_logger.log_system(
                        "WARNING",
                        "GAME_DIRECTOR",
                        "UI renderer missing _update_from_fpsm_state method",
                        {},
                    )
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    "No UI renderer available for update",
                    {},
                )

            # STEP 4: Notify UI via event system
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "🔄 STEP 4: Emitting UI update event",
                {},
            )
            self._emit_ui_update_event(timeline_state)

            # STEP 5: Log completion
            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                f"✅ TIMELINE STATE {index} DISPLAY COMPLETE",
                {
                    "state_name": timeline_state["state_name"],
                    "current_street": timeline_state["current_street"],
                    "pot_amount": timeline_state["pot_amount"],
                    "board_cards_count": len(timeline_state["board_cards"]),
                },
            )

            return True

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error displaying timeline state: {e}",
                {"error": str(e), "index": index},
            )
            return False

    def _restore_timeline_state(self, timeline_state: Dict[str, Any]):
        """Restore the game state from a timeline state."""
        try:
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "🔄 Starting timeline state restoration",
                {
                    "state_name": timeline_state["state_name"],
                    "board_cards": timeline_state["board_cards"],
                    "pot_amount": timeline_state["pot_amount"],
                },
            )

            # Enable timeline restoration mode in PSM to prevent board/pot
            # clearing
            print(
                "🔥 CONSOLE: 🔍 Checking if PSM has enable_timeline_restoration_mode method"
            )
            if hasattr(self.state_machine, "enable_timeline_restoration_mode"):
                print(
                    "🔥 CONSOLE: ✅ Method exists, calling enable_timeline_restoration_mode()"
                )
                self.state_machine.enable_timeline_restoration_mode()
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Timeline restoration mode enabled in PSM",
                    {},
                )
            else:
                print("🔥 CONSOLE: ❌ Method NOT found on PSM!")
                print(
                    f"🔥 CONSOLE: 🔍 PSM methods: {
                        [
                            m for m in dir(
                                self.state_machine) if 'timeline' in m.lower()]}"
                )

            # Restore board cards
            if hasattr(self.state_machine, "game_state"):
                old_board = (
                    self.state_machine.game_state.board.copy()
                    if self.state_machine.game_state.board
                    else []
                )
                self.state_machine.game_state.board = timeline_state[
                    "board_cards"
                ].copy()
                self.state_machine.game_state.pot = timeline_state[
                    "pot_amount"
                ]

                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "🔄 Board and pot restored",
                    {
                        "old_board": old_board,
                        "new_board": timeline_state["board_cards"],
                        "old_pot": getattr(
                            self.state_machine.game_state, "pot", "N/A"
                        ),
                        "new_pot": timeline_state["pot_amount"],
                    },
                )
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    "No game_state available for restoration",
                    {},
                )

            # Restore player states
            if hasattr(self.state_machine, "game_state") and hasattr(
                self.state_machine.game_state, "players"
            ):
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    f"🔄 Restoring {
                        len(
                            timeline_state['player_states'])} player states",
                    {},
                )

                for i, player in enumerate(
                    self.state_machine.game_state.players
                ):
                    if i < len(timeline_state["player_states"]):
                        player_state = timeline_state["player_states"][i]
                        old_cards = player.cards.copy() if player.cards else []
                        old_bet = player.current_bet
                        old_stack = player.stack

                        player.cards = player_state["cards"].copy()
                        player.current_bet = player_state["current_bet"]
                        player.stack = player_state["stack"]
                        player.has_folded = player_state["has_folded"]
                        player.is_active = player_state["is_active"]

                        self.session_logger.log_system(
                            "DEBUG",
                            "GAME_DIRECTOR",
                            f"🔄 Player {i} ({player.name}) restored",
                            {
                                "old_cards": old_cards,
                                "new_cards": player_state["cards"],
                                "old_bet": old_bet,
                                "new_bet": player_state["current_bet"],
                                "old_stack": old_stack,
                                "new_stack": player_state["stack"],
                                "folded": player_state["has_folded"],
                                "active": player_state["is_active"],
                            },
                        )
                    else:
                        self.session_logger.log_system(
                            "WARNING",
                            "GAME_DIRECTOR",
                            f"Player {i} index out of range for restoration",
                            {
                                "player_index": i,
                                "available_states": len(
                                    timeline_state["player_states"]
                                ),
                            },
                        )
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    "No players available for restoration",
                    {},
                )

            # Restore current state
            if hasattr(self.state_machine, "current_state"):
                old_state = self.state_machine.current_state
                # Find the PokerState enum value by name
                from .flexible_poker_state_machine import PokerState

                state_name = timeline_state["current_street"]
                for state in PokerState:
                    if state.name == state_name:
                        self.state_machine.current_state = state
                        self.session_logger.log_system(
                            "DEBUG",
                            "GAME_DIRECTOR",
                            "🔄 Game state restored",
                            {
                                "old_state": str(old_state),
                                "new_state": str(state),
                            },
                        )
                        break
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "GAME_DIRECTOR",
                    "No current_state available for restoration",
                    {},
                )

            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "✅ Timeline state restoration complete",
                {},
            )

            # Disable timeline restoration mode to resume normal operation
            if hasattr(
                self.state_machine, "disable_timeline_restoration_mode"
            ):
                self.state_machine.disable_timeline_restoration_mode()
                self.session_logger.log_system(
                    "DEBUG",
                    "GAME_DIRECTOR",
                    "Timeline restoration mode disabled in PSM",
                    {},
                )

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error restoring timeline state: {e}",
                {"error": str(e)},
            )

    def load_hands_review_timeline(self, hand_json: dict) -> bool:
        """
        Build a list of snapshots (one per step/action/street) from a hand json,
        switch the state machine into review mode, and show the first snapshot.
        """
        try:
            print(
                "\n🎯 LOADING HAND: Starting hands review timeline creation"
            )
            print(f"📊 Raw hand data keys: {list(hand_json.keys())}")
            print(f"👥 Players count: {len(hand_json.get('players', []))}")
            print(
                f"🎲 Dealer index: {
                    hand_json.get(
                        'dealer_index',
                        'Not found')}"
            )
            print(
                f"📝 Actions structure: {
                    list(
                        hand_json.get(
                            'actions',
                            {}).keys()) if 'actions' in hand_json else 'No actions'}"
            )

            # Debug: Log the actual hand data structure
            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "Hand data structure analysis",
                {
                    "hand_keys": list(hand_json.keys()),
                    "has_players": "players" in hand_json,
                    "has_actions": "actions" in hand_json,
                    "has_board": "board" in hand_json,
                    "has_pot": "pot" in hand_json,
                    "sample_player": (
                        hand_json.get("players", [{}])[0]
                        if hand_json.get("players")
                        else "No players"
                    ),
                    "sample_action": (
                        list(hand_json.get("actions", {}).keys())
                        if hand_json.get("actions")
                        else "No actions"
                    ),
                },
            )

            self.is_hands_review_mode = True
            self.state_machine.set_mode("review")

            print("🔄 Building snapshots from hand data...")
            self.hands_review_timeline = self._build_snapshots(hand_json)
            self.current_timeline_index = 0

            if not self.hands_review_timeline:
                print("❌ ERROR: No snapshots created!")
                return False

            print(
                f"✅ Created {len(self.hands_review_timeline)} timeline snapshots"
            )
            print("🎬 Jumping to initial state (index 0)...")

            self._jump_to_timeline_index(0)

            print("🎯 Hands review timeline loaded successfully!")
            print(
                f"📊 Timeline summary: {len(self.hands_review_timeline)} states"
            )

            self.session_logger.log_system(
                "INFO",
                "GAME_DIRECTOR",
                "Hands review timeline loaded",
                {"states": len(self.hands_review_timeline)},
            )
            return True
        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Failed to load hands review: {e}",
                {},
            )
            return False

    def _build_snapshots(self, hand_json: dict) -> list[dict]:
        """
        Returns a list of dicts, each shaped like:
          { "board": [...], "pot": 12.5, "current_bet": 4.0, "street":"turn",
            "dealer_index": 2, "action_player_index": 4,
            "players":[{"stack":..., "current_bet":..., "has_folded":..., "cards":[...]}] }
        """
        import copy

        print("🔨 BUILDING SNAPSHOTS: Processing hand data")
        print(f"📊 Hand data keys: {list(hand_json.keys())}")
        print(f"👥 Players: {len(hand_json.get('players', []))}")
        print(f"🎲 Dealer: {hand_json.get('dealer_index', 'Not found')}")
        print(
            f"📝 Actions: {
                list(
                    hand_json.get(
                        'actions',
                        {}).keys()) if 'actions' in hand_json else 'No actions'}"
        )

        # Debug: Log what we're building
        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            "Building snapshots",
            {
                "hand_json_keys": list(hand_json.keys()),
                "actions_structure": hand_json.get("actions", "No actions"),
                "players_count": len(hand_json.get("players", [])),
                "dealer_index": hand_json.get("dealer_index", "Not found"),
                "sample_player": (
                    hand_json.get("players", [{}])[0]
                    if hand_json.get("players")
                    else {}
                ),
                "hand_json_sample": (
                    str(hand_json)[:500] + "..."
                    if len(str(hand_json)) > 500
                    else str(hand_json)
                ),
            },
        )

        snaps = []
        base = {
            "dealer_index": hand_json.get("dealer_index", 0),
            "players": hand_json.get("players", []),
            "board": list(hand_json.get("board", [])),  # ← Use top-level board
            "pot": float(hand_json.get("pot", 0.0)),  # ← Use top-level pot
            "current_bet": 0.0,
            "street": "preflop",
        }
        print("🎬 Creating base snapshot with TOP-LEVEL data...")
        print(
            f"   📊 Base: dealer={base['dealer_index']}, players={len(base['players'])}"
        )
        print(f"   🃏 Board: {base['board']}")
        print(f"   💰 Pot: ${base['pot']}")
        snaps.append(copy.deepcopy(base))

        print("🎬 Creating base snapshot...")
        print(
            f"   📊 Base: dealer={
                base['dealer_index']}, players={
                len(
                    base['players'])}, board={
                    base['board']}, pot={
                        base['pot']}"
        )

        # evolve snapshot across actions/streets
        for street in ("preflop", "flop", "turn", "river"):
            street_actions = hand_json.get("actions", {}).get(street, [])
            print(
                f"🎯 Processing {
                    street.upper()}: {
                    len(street_actions)} actions"
            )

            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                f"Processing {street}",
                {
                    "action_count": len(street_actions),
                    # Show first 2 actions
                    "actions": (
                        street_actions[:2] if street_actions else "No actions"
                    ),
                },
            )

            for i, action in enumerate(street_actions):
                print(
                    f"   🔄 Action {
                        i +
                        1}: {
                        action.get(
                            'action_type',
                            'Unknown')} by player {
                        action.get(
                            'actor',
                            'Unknown')}"
                )

                # mutate base as actions happen
                # Note: Board and pot are typically at top level, but some
                # actions might update them
                if "board" in action:
                    base["board"] = list(action["board"])
                    base["street"] = street
                    print(f"      🃏 Board updated: {base['board']}")
                if "pot" in action:
                    base["pot"] = float(action["pot"])
                    print(f"      💰 Pot updated: ${base['pot']}")
                if "current_bet" in action:
                    base["current_bet"] = float(action["current_bet"])
                    print(f"      🎯 Current bet: ${base['current_bet']}")
                if "players" in action:
                    base["players"] = action["players"]
                    print(
                        f"      👥 Players updated: {len(base['players'])} players"
                    )
                if "action_player_index" in action:
                    base["action_player_index"] = int(
                        action["action_player_index"]
                    )
                    print(
                        f"      👤 Action player: {
                            base['action_player_index']}"
                    )

                snaps.append(copy.deepcopy(base))
                print(f"      ✅ Snapshot {len(snaps)} created")

        print("\n🎯 SNAPSHOTS BUILT: Summary")
        print(f"📊 Total snapshots: {len(snaps)}")
        if snaps:
            print(
                f"🃏 First snapshot: board={
                    snaps[0].get(
                        'board',
                        [])}, pot=${
                    snaps[0].get(
                        'pot',
                        0)}"
            )
            print(
                f"🃏 Last snapshot: board={snaps[-1].get('board', [])}, pot=${snaps[-1].get('pot', 0)}"
            )

        self.session_logger.log_system(
            "DEBUG",
            "GAME_DIRECTOR",
            "Snapshots built",
            {
                "total_snapshots": len(snaps),
                "first_snapshot": snaps[0] if snaps else "No snapshots",
                "last_snapshot": snaps[-1] if snaps else "No snapshots",
            },
        )

        return snaps

    def _jump_to_timeline_index(self, idx: int) -> None:
        """Jump to a specific timeline index using the new snapshot system."""
        idx = max(0, min(idx, len(self.hands_review_timeline) - 1))
        self.current_timeline_index = idx
        snap = self.hands_review_timeline[idx]

        print(f"\n🎬 JUMPING TO TIMELINE INDEX {idx}")
        print(
            f"📊 Snapshot data: board={
                snap.get(
                    'board',
                    [])}, pot=${
                snap.get(
                    'pot',
                    0)}"
        )
        print(f"👥 Players: {len(snap.get('players', []))}")
        print(
            f"🎯 Action player: {snap.get('action_player_index', 'Not set')}"
        )
        print("🔄 Restoring snapshot to FPSM...")

        self.state_machine.restore_snapshot(snap)  # << no clears after this

        print("✅ Snapshot restored successfully!")
        # Notify listeners UI already refreshes from FPSM DISPLAY_STATE event

    def _emit_ui_update_event(self, timeline_state: Dict[str, Any]):
        """Emit an event to notify UI to update."""
        try:
            # Emit timeline state changed event through state machine
            import time
            from .flexible_poker_state_machine import GameEvent

            event = GameEvent(
                event_type="timeline_state_changed",
                timestamp=time.time(),
                data={
                    "current_index": self.current_timeline_index,
                    "timeline_size": len(self.hands_review_timeline),
                    "state_name": timeline_state["state_name"],
                    "current_street": timeline_state["current_street"],
                    "pot_amount": timeline_state["pot_amount"],
                },
            )

            # Emit through state machine if it has event listeners
            if (
                hasattr(self.state_machine, "event_listeners")
                and self.state_machine.event_listeners
            ):
                for listener in self.state_machine.event_listeners:
                    try:
                        listener.on_event(event)
                    except Exception as e:
                        self.session_logger.log_system(
                            "ERROR",
                            "GAME_DIRECTOR",
                            f"Error notifying listener: {e}",
                            {"error": str(e)},
                        )

            self.session_logger.log_system(
                "DEBUG",
                "GAME_DIRECTOR",
                "Emitted timeline_state_changed event",
                {
                    "current_index": self.current_timeline_index,
                    "timeline_size": len(self.hands_review_timeline),
                },
            )

        except Exception as e:
            self.session_logger.log_system(
                "ERROR",
                "GAME_DIRECTOR",
                f"Error emitting timeline state changed event: {e}",
                {"error": str(e)},
            )

    def next_timeline_state(self) -> bool:
        """Move to the next timeline state using the new snapshot system."""
        if not self.is_hands_review_mode:
            print("❌ Not in hands review mode")
            return False
        if self.current_timeline_index + 1 >= len(self.hands_review_timeline):
            print(
                f"❌ Already at last timeline state ({self.current_timeline_index + 1}/{len(self.hands_review_timeline)})"
            )
            return False

        print(
            f"\n⏭️ NEXT TIMELINE STATE: {
                self.current_timeline_index +
                1} -> {
                self.current_timeline_index +
                2}"
        )
        self._jump_to_timeline_index(self.current_timeline_index + 1)
        return True

    def previous_timeline_state(self) -> bool:
        """Move to the previous timeline state using the new snapshot system."""
        if not self.is_hands_review_mode:
            print("❌ Not in hands review mode")
            return False
        if self.current_timeline_index - 1 < 0:
            print("❌ Already at first timeline state (0)")
            return False

        print(
            f"\n⏮️ PREVIOUS TIMELINE STATE: {
                self.current_timeline_index + 1} -> {
                self.current_timeline_index}"
        )
        self._jump_to_timeline_index(self.current_timeline_index - 1)
        return True

    def jump_to_street(self, street_name: str) -> bool:
        """Jump to a specific street in the timeline."""
        for i, state in enumerate(self.hands_review_timeline):
            if state["current_street"] == street_name:
                return self.display_timeline_state(i)
        return False

    def start_hands_review_play(self):
        """Start auto-play mode for hands review."""
        if not self.is_hands_review_mode:
            return False

        # Schedule the next timeline state
        self.schedule_event(
            delay_ms=self.hands_review_play_speed_ms,
            event_type="hands_review_play_advance",
            data={"current_index": self.current_timeline_index},
        )

        self.session_logger.log_system(
            "INFO",
            "GAME_DIRECTOR",
            "Started hands review play mode",
            {"play_speed_ms": self.hands_review_play_speed_ms},
        )

    def stop_hands_review_play(self):
        """Stop auto-play mode for hands review."""
        # Cancel any pending play events
        self.event_queue = [
            e
            for e in self.event_queue
            if e.event_type != "hands_review_play_advance"
        ]

        self.session_logger.log_system(
            "INFO", "GAME_DIRECTOR", "Stopped hands review play mode", {}
        )

    def set_hands_review_play_speed(self, speed_ms: int):
        """Set the play speed for hands review auto-play."""
        self.hands_review_play_speed_ms = speed_ms

        self.session_logger.log_system(
            "INFO",
            "GAME_DIRECTOR",
            "Updated hands review play speed",
            {"new_speed_ms": speed_ms},
        )
