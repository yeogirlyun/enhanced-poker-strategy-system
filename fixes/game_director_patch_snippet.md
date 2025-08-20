# GameDirector Patches - ARCHITECTURE COMPLIANT VERSION

**CRITICAL**: This patch removes threading violations and uses proper event-driven scheduling.

```python
class GameDirector:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.gates = 0
        self.last_tick = time.time()
        self.speed = 1.0  # 1.0 = normal, 2.0 = 2x speed
        
    def play(self):
        """Start autoplay sequence."""
        self._publish_telemetry("play", {"speed": self.speed})
        self._schedule_next(initial=True)
        
    def pause(self):
        """Pause autoplay sequence."""
        self._publish_telemetry("pause")
        
    def gate_start(self):
        """Begin an effect gate."""
        self.gates += 1
        self._publish_telemetry("gate ++", {"count": self.gates})
        
    def gate_end(self):
        """End an effect gate."""
        if self.gates > 0:
            self.gates -= 1
            self._publish_telemetry("gate --", {"count": self.gates})
            
        # Re-schedule if gates cleared
        if self.gates == 0:
            self._schedule_next()
            
    def _schedule_next(self, initial=False):
        """Schedule next autoplay action via event bus."""
        # Don't schedule if gates active
        if self.gates > 0:
            return
            
        # Calculate delay based on speed
        delay = 1000  # Base delay 1 second
        if not initial:
            delay = 2000  # Longer delay between actions
            
        # Scale by speed
        delay = delay / self.speed
        
        # Use event bus to schedule - NO THREADING
        if self.event_bus:
            # Schedule via event bus, not threading.Timer
            self.event_bus.publish("game_director:schedule_advance", {
                "delay_ms": delay,
                "type": "AUTO_ADVANCE"
            })
            
    def update(self, dt=None):
        """Update director state."""
        # Calculate dt if not provided
        if dt is None:
            now = time.time()
            dt = (now - self.last_tick) * 1000
            self.last_tick = now
            
        # Process updates
        pass
        
    def _publish_telemetry(self, event, data=None):
        """Publish telemetry event."""
        if not self.event_bus:
            return
            
        if data is None:
            data = {}
            
        self.event_bus.publish(
            "game_director:telemetry",
            {
                "event": event,
                "gates": self.gates,
                "speed": self.speed,
                "data": data
            }
        )
```

**Key Changes Made:**
1. ❌ **REMOVED**: `threading.Timer` usage (architecture violation)
2. ✅ **ADDED**: Event-driven scheduling via event bus
3. ✅ **MAINTAINED**: Single-threaded, event-driven architecture
4. ✅ **COMPLIANT**: All timing controlled by GameDirector
5. ✅ **SAFE**: No blocking operations or threading

**Architecture Compliance:**
- ✅ Single-threaded
- ✅ Event-driven only
- ✅ GameDirector controls timing
- ✅ No threading/timers for game logic
- ✅ All timing via coordinator
