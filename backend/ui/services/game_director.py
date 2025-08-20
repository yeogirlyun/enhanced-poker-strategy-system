#!/usr/bin/env python3
"""
GameDirector - Centralized timing, autoplay, and effect sequencing
(minimal, single-threaded)
"""
from __future__ import annotations

import time
import heapq
import itertools
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass


class PlaybackState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class _Scheduled:
    due_ms: int
    seq: int
    event: Dict[str, Any]
    callback: Optional[Callable]


class GameDirector:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.playback_state = PlaybackState.STOPPED
        self.speed = 1.0
        self.autoplay_interval_ms = 600
        self.current_step = 0
        self.total_steps = 0
        self.on_advance_callback: Optional[Callable[[int], None]] = None
        self.on_step_change_callback: Optional[Callable[[int], None]] = None

        self._q: List[tuple] = []  # (due_ms, seq, event, callback)
        self._seq = itertools.count()
        self._gate_count = 0
        self._cancelled = set()
        self._last_now = self._now_ms()
        print("🎬 GameDirector: Initialized")

    # Wiring
    def set_event_bus(self, event_bus): 
        self.event_bus = event_bus

    def set_advance_callback(self, callback: Callable[[int], None]): 
        self.on_advance_callback = callback

    def set_step_change_callback(self, callback: Callable[[int], None]): 
        self.on_step_change_callback = callback

    def set_total_steps(self, total: int):
        self.total_steps = max(0, int(total))
        print(f"🎬 GameDirector: Total steps set to {self.total_steps}")

    # Playback controls
    def play(self) -> None:
        if self.playback_state == PlaybackState.STOPPED:
            self.current_step = max(0, self.current_step)
        self.playback_state = PlaybackState.PLAYING
        print("🎬 GameDirector: PLAY")
        # Ensure scheduling is attempted when play is pressed. _schedule_next_auto
        # will internally respect gate_count and playback_state.
        try:
            self._schedule_next_auto()
        except Exception:
            # Scheduling is best-effort; swallow errors for robustness
            pass

    def pause(self) -> None:
        self.playback_state = PlaybackState.PAUSED
        print("🎬 GameDirector: PAUSE")
        # Don't schedule more autoplay when paused

    def stop(self) -> None:
        self.playback_state = PlaybackState.STOPPED
        self._q.clear()
        self._gate_count = 0
        print("🎬 GameDirector: STOP")

    def step_forward(self, n: int = 1) -> None:
        for _ in range(max(1, n)):
            self._advance_once()

    def step_back(self, n: int = 1) -> None:
        self.current_step = max(0, self.current_step - max(1, n))
        if self.on_step_change_callback:
            self.on_step_change_callback(self.current_step)

    def seek(self, step_index: int) -> None:
        # Cancel pending tokens and reset gate count
        self._q.clear()
        self._gate_count = 0
        self.current_step = max(0, min(int(step_index),
                                       self.total_steps - 1))
        if self.on_step_change_callback:
            self.on_step_change_callback(self.current_step)

    def set_speed(self, multiplier: float) -> None:
        self.speed = max(0.1, float(multiplier))
        print(f"🎬 GameDirector: Speed={self.speed}x")

    def set_autoplay_interval(self, ms: int) -> None:
        self.autoplay_interval_ms = max(60, int(ms))

    # Gate controls (effects)
    def gate_begin(self) -> None:
        self._gate_count += 1
        print(f"🎬 GameDirector: GATE ++ ({self._gate_count})")

    def gate_end(self) -> None:
        self._gate_count = max(0, self._gate_count - 1)
        print(f"🎬 GameDirector: GATE -- ({self._gate_count})")
        # Only schedule next autoplay when gate is closed and we're playing
        if (self._gate_count == 0 and
                self.playback_state == PlaybackState.PLAYING):
            self._schedule_next_auto()

    def notify_sound_complete(self, event_data=None):
        """Called when sound effect completes."""
        if event_data is None:
            event_data = {}
        print(f"🎬 GameDirector: Sound complete: {event_data.get('id', 'unknown')}")
        self.gate_end()

    def notify_animation_complete(self, event_data=None):
        """Called when animation effect completes."""
        if event_data is None:
            event_data = {}
        print(f"🎬 GameDirector: Animation complete: {event_data.get('name', 'unknown')}")
        self.gate_end()

    # Scheduling
    def schedule(self, delay_ms: int, event: Dict[str, Any],
                 callback: Optional[Callable] = None) -> str:
        """Schedule an event with delay."""
        # Use defensive speed scaling: divide delay by speed multiplier (faster -> shorter delay)
        scaled_delay = int(delay_ms / max(0.1, float(self.speed)))
        due_ms = self._now_ms() + scaled_delay
        seq = next(self._seq)
        heapq.heappush(self._q, (due_ms, seq, event, callback))
        # Telemetry: publish scheduled event for diagnostics
        try:
            if self.event_bus:
                self.event_bus.publish("game_director:scheduled", {"delay_ms": delay_ms, "event": event})
        except Exception:
            pass

        return f"{seq}"

    def cancel(self, token: str) -> None:
        try:
            seq = int(token[1:])
            self._cancelled.add(seq)
        except Exception:
            pass

    def update(self, dt_ms: int = 16) -> None:
        """Update the director - process scheduled events."""
        now = self._now_ms()
        while self._q and self._q[0][0] <= now:
            due_ms, seq, event, callback = heapq.heappop(self._q)
            # Publish dispatch telemetry so callers can trace scheduling behavior
            try:
                if self.event_bus:
                    self.event_bus.publish("game_director:dispatch", event)
            except Exception:
                pass

            if event.get("type") == "AUTO_ADVANCE":
                self._advance_once()
                # Only schedule next if gate is closed and we're playing
                if (self._gate_count == 0 and
                        self.playback_state == PlaybackState.PLAYING):
                    self._schedule_next_auto()
            else:
                if callback:
                    callback()

    # Internals
    def _schedule_next_auto(self) -> None:
        """Schedule the next autoplay step."""
        if (self.playback_state == PlaybackState.PLAYING and
                self.current_step < self.total_steps):
            self.schedule(self.autoplay_interval_ms,
                         {"type": "AUTO_ADVANCE"})

    def _advance_once(self) -> None:
        """Advance one step forward."""
        if self.current_step < self.total_steps:
            self.current_step += 1
            if self.on_advance_callback:
                self.on_advance_callback(self.current_step)
            if self.on_step_change_callback:
                self.on_step_change_callback(self.current_step)

    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        return int(time.time() * 1000)


class NoopDirector:
    """No-op director for testing or when GameDirector is not needed."""
    
    def __init__(self):
        pass
    
    def play(self) -> None: pass
    def pause(self) -> None: pass
    def stop(self) -> None: pass
    def step_forward(self, n: int = 1) -> None: pass
    def step_back(self, n: int = 1) -> None: pass
    def seek(self, step_index: int) -> None: pass
    def set_speed(self, multiplier: float) -> None: pass
    def set_autoplay_interval(self, ms: int) -> None: pass
    def schedule(self, delay_ms: int, event: Dict[str, Any], callback: Optional[Callable] = None) -> str: return "noop"
    def cancel(self, token: str) -> None: pass
    def gate_begin(self) -> None: pass
    def gate_end(self) -> None: pass
    def notify_animation_complete(self) -> None: pass
    def notify_sound_complete(self) -> None: pass
    def get_status(self) -> Dict[str, Any]: return {"type": "noop"}
    def update(self, delta_time_ms: float = 16.67) -> None: pass
