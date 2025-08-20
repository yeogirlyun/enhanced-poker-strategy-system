#!/usr/bin/env python3
"""
Timing Migration Helper - Architecture Compliance Utility

This utility helps migrate self.after() calls to event-driven scheduling
via GameDirector, ensuring compliance with the single-threaded architecture.

CRITICAL: All timing must go through GameDirector, not direct UI component calls.
"""

from typing import Optional, Callable, Dict, Any
from enum import Enum


class TimingType(Enum):
    """Types of timing operations that need migration."""
    ANIMATION = "animation"
    HIGHLIGHT = "highlight"
    UPDATE_LOOP = "update_loop"
    DELAYED_ACTION = "delayed_action"
    SOUND_COMPLETION = "sound_completion"
    CHIP_MOVEMENT = "chip_movement"
    POT_ANIMATION = "pot_animation"
    WINNER_CELEBRATION = "winner_celebration"


class TimingMigrationHelper:
    """
    Helper class to migrate self.after() calls to event-driven scheduling.
    
    This ensures all timing goes through GameDirector as required by the architecture.
    """
    
    def __init__(self, game_director=None, event_bus=None):
        self.game_director = game_director
        self.event_bus = event_bus
        self._pending_events = {}
        self._next_event_id = 0
    
    def schedule_event(self, 
                      delay_ms: int, 
                      timing_type: TimingType,
                      callback: Optional[Callable] = None,
                      data: Optional[Dict[str, Any]] = None,
                      component_name: str = "unknown") -> str:
        """
        Schedule an event via GameDirector instead of self.after().
        
        Args:
            delay_ms: Delay in milliseconds
            timing_type: Type of timing operation
            callback: Optional callback function
            data: Additional data for the event
            component_name: Name of the component scheduling the event
            
        Returns:
            Event ID for cancellation if needed
        """
        event_id = f"{timing_type.value}_{self._next_event_id}"
        self._next_event_id += 1
        
        event_data = {
            "type": "TIMED_EVENT",
            "timing_type": timing_type.value,
            "event_id": event_id,
            "component": component_name,
            "callback": callback,
            "data": data or {}
        }
        
        # Store pending event for callback execution
        if callback:
            self._pending_events[event_id] = {
                "callback": callback,
                "data": data or {},
                "component": component_name
            }
        
        # Schedule via GameDirector if available
        if self.game_director and hasattr(self.game_director, 'schedule'):
            self.game_director.schedule(delay_ms, event_data)
        else:
            # Fallback: publish event for manual handling
            if self.event_bus:
                self.event_bus.publish("timing:schedule_event", {
                    "delay_ms": delay_ms,
                    "event_data": event_data
                })
        
        return event_id
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a pending event."""
        if event_id in self._pending_events:
            del self._pending_events[event_id]
            return True
        return False
    
    def execute_pending_event(self, event_id: str) -> bool:
        """Execute a pending event callback."""
        if event_id in self._pending_events:
            event_info = self._pending_events[event_id]
            try:
                if event_info["callback"]:
                    event_info["callback"]()
                del self._pending_events[event_id]
                return True
            except Exception as e:
                print(f"⚠️ Error executing timing event {event_id}: {e}")
                del self._pending_events[event_id]
        return False
    
    def clear_all_events(self):
        """Clear all pending events."""
        self._pending_events.clear()
    
    def get_pending_events(self) -> Dict[str, Dict]:
        """Get all pending events for debugging."""
        return self._pending_events.copy()


# Migration patterns for common self.after() usage:

def migrate_animation_timing(helper: TimingMigrationHelper, 
                           delay_ms: int, 
                           animation_callback: Callable,
                           component_name: str = "unknown") -> str:
    """Migrate animation timing from self.after() to event-driven."""
    return helper.schedule_event(
        delay_ms=delay_ms,
        timing_type=TimingType.ANIMATION,
        callback=animation_callback,
        component_name=component_name
    )


def migrate_highlight_timing(helper: TimingMigrationHelper,
                           delay_ms: int,
                           highlight_callback: Callable,
                           component_name: str = "unknown") -> str:
    """Migrate highlight timing from self.after() to event-driven."""
    return helper.schedule_event(
        delay_ms=delay_ms,
        timing_type=TimingType.HIGHLIGHT,
        callback=highlight_callback,
        component_name=component_name
    )


def migrate_update_loop(helper: TimingMigrationHelper,
                       interval_ms: int,
                       update_callback: Callable,
                       component_name: str = "unknown") -> str:
    """Migrate update loop timing from self.after() to event-driven."""
    return helper.schedule_event(
        delay_ms=interval_ms,
        timing_type=TimingType.UPDATE_LOOP,
        callback=lambda: _schedule_next_update(helper, interval_ms, update_callback, component_name),
        component_name=component_name
    )


def _schedule_next_update(helper: TimingMigrationHelper,
                         interval_ms: int,
                         update_callback: Callable,
                         component_name: str):
    """Helper to schedule the next update in a loop."""
    # Execute current update
    update_callback()
    
    # Schedule next update
    helper.schedule_event(
        delay_ms=interval_ms,
        timing_type=TimingType.UPDATE_LOOP,
        callback=lambda: _schedule_next_update(helper, interval_ms, update_callback, component_name),
        component_name=component_name
    )


# Example migration usage:
"""
# BEFORE (VIOLATION):
self.after(1000, self._complete_action)

# AFTER (COMPLIANT):
event_id = self.timing_helper.schedule_event(
    delay_ms=1000,
    timing_type=TimingType.DELAYED_ACTION,
    callback=self._complete_action,
    component_name="poker_widget"
)

# BEFORE (VIOLATION):
self.after(50, self._update_loop)

# AFTER (COMPLIANT):
event_id = migrate_update_loop(
    self.timing_helper,
    interval_ms=50,
    update_callback=self._update_loop,
    component_name="poker_widget"
)
"""
