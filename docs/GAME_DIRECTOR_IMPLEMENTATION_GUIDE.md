# 🎮 **GameDirector Implementation Guide**
## **Step-by-Step Migration to Event-Driven Architecture**

---

## 🎯 **Phase 1: Minimal GameDirector (Immediate)**

### **Step 1: Create Basic GameDirector**

```python
# backend/core/game_director.py
import time
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum

@dataclass
class ScheduledEvent:
    """A scheduled event in the game director queue."""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    callback: Callable = None

class GameDirector:
    """Central coordinator for all game timing and events."""
    
    def __init__(self, state_machine, ui_renderer, audio_manager, session_logger):
        self.state_machine = state_machine
        self.ui_renderer = ui_renderer
        self.audio_manager = audio_manager
        self.session_logger = session_logger
        
        # Event system
        self.event_queue: List[ScheduledEvent] = []
        self.is_running = False
        
        # Timing control
        self.last_update = time.time()
        
    def start(self):
        """Start the game director."""
        self.is_running = True
        self._start_update_loop()
        
    def stop(self):
        """Stop the game director and clear events."""
        self.is_running = False
        self.event_queue.clear()
        
    def schedule_event(self, delay_ms: int, event_type: str, data: Dict[str, Any] = None, callback: Callable = None):
        """Schedule an event to execute after delay_ms milliseconds."""
        if data is None:
            data = {}
            
        scheduled_time = time.time() + (delay_ms / 1000.0)
        event = ScheduledEvent(
            timestamp=scheduled_time,
            event_type=event_type,
            data=data,
            callback=callback
        )
        
        self.event_queue.append(event)
        self.session_logger.log_system("DEBUG", "GAME_DIRECTOR", f"Scheduled event: {event_type} in {delay_ms}ms", {
            "event_type": event_type,
            "delay_ms": delay_ms,
            "data_keys": list(data.keys())
        })
        
    def execute_player_action(self, player, action, amount: float = 0.0):
        """Single entry point for ALL player actions."""
        self.session_logger.log_system("INFO", "GAME_DIRECTOR", f"Executing action: {player.name} {action.value} ${amount}", {
            "player": player.name,
            "action": action.value,
            "amount": amount
        })
        
        # 1. Execute in state machine (synchronous)
        if self.state_machine.execute_action(player, action, amount):
            # 2. Update UI immediately (synchronous)
            self._update_ui()
            
            # 3. Schedule sound (non-blocking)
            if hasattr(self.audio_manager, 'play_action_sound'):
                sound_duration = self.audio_manager.play_action_sound(action.value)
                
                # 4. Schedule next bot action if needed (after sound + processing delay)
                if self._is_bot_turn_next():
                    total_delay = int(sound_duration * 1000) + 1000  # Sound + 1 second
                    self.schedule_event(total_delay, "execute_bot_action", {
                        "player_index": self.state_machine.action_player_index
                    })
            
            return True
        return False
        
    def _update_ui(self):
        """Update UI immediately from current state."""
        if hasattr(self.ui_renderer, 'render_current_state'):
            self.ui_renderer.render_current_state()
        elif hasattr(self.ui_renderer, '_update_from_fpsm_state'):
            self.ui_renderer._update_from_fpsm_state()
            
    def _is_bot_turn_next(self):
        """Check if next player is a bot."""
        if (self.state_machine.action_player_index >= 0 and 
            self.state_machine.action_player_index < len(self.state_machine.game_state.players)):
            current_player = self.state_machine.game_state.players[self.state_machine.action_player_index]
            return not current_player.is_human
        return False
        
    def _start_update_loop(self):
        """Start the main update loop (Tkinter-based)."""
        if hasattr(self.ui_renderer, 'after'):
            self._tkinter_update_loop()
        else:
            # Fallback for testing
            self._simple_update_loop()
            
    def _tkinter_update_loop(self):
        """Tkinter-compatible update loop."""
        if self.is_running:
            self.update()
            self.ui_renderer.after(16, self._tkinter_update_loop)  # ~60 FPS
            
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
            "event_type": event.event_type,
            "data": event.data
        })
        
        try:
            if event.event_type == "execute_bot_action":
                self._handle_bot_action_event(event.data)
            elif event.event_type == "update_ui":
                self._update_ui()
            elif event.event_type == "play_sound":
                self.audio_manager.play_sound(event.data.get("sound_name", ""))
            elif event.event_type == "custom":
                if event.callback:
                    event.callback(event.data)
                    
        except Exception as e:
            self.session_logger.log_system("ERROR", "GAME_DIRECTOR", f"Error executing event {event.event_type}: {e}", {
                "event_type": event.event_type,
                "error": str(e)
            })
            
    def _handle_bot_action_event(self, data: Dict[str, Any]):
        """Handle bot action execution."""
        player_index = data.get("player_index", -1)
        
        if (player_index >= 0 and 
            player_index < len(self.state_machine.game_state.players) and
            player_index == self.state_machine.action_player_index):
            
            current_player = self.state_machine.game_state.players[player_index]
            
            if not current_player.is_human:
                # Get bot decision
                action, amount = self._get_bot_decision(current_player)
                # Execute through this director (maintains single flow)
                self.execute_player_action(current_player, action, amount)
                
    def _get_bot_decision(self, bot_player):
        """Get bot's decision (delegates to state machine)."""
        if hasattr(self.state_machine, '_get_bot_strategy_decision'):
            return self.state_machine._get_bot_strategy_decision(bot_player)
        else:
            # Fallback
            from core.types import ActionType
            return ActionType.FOLD, 0.0
```

### **Step 2: Integration Points**

```python
# In your main_gui.py or initialization
def create_game_director():
    """Create and wire up the game director."""
    state_machine = PracticeSessionPokerStateMachine(config, session_logger)
    ui_renderer = ReusablePokerGameWidget(parent)
    audio_manager = SoundManager()
    
    game_director = GameDirector(state_machine, ui_renderer, audio_manager, session_logger)
    
    # Wire up UI to use game director
    ui_renderer.set_game_director(game_director)
    
    return game_director

# In ReusablePokerGameWidget
class ReusablePokerGameWidget(ttk.Frame):
    def set_game_director(self, game_director):
        """Set the game director for this widget."""
        self.game_director = game_director
        
    def on_player_action_button_clicked(self, action, amount):
        """Handle UI button clicks."""
        if self.game_director and hasattr(self, 'current_human_player'):
            # Route through game director instead of direct state machine
            self.game_director.execute_player_action(
                self.current_human_player, action, amount
            )
```

---

## 🔄 **Phase 2: Replace Threading (Priority)**

### **Before (Current Problematic Code):**
```python
# ❌ In practice_session_poker_state_machine.py
def _execute_bot_action_with_timing(self, player, action, amount):
    import threading
    # Complex threading logic that causes conflicts...
    delay_thread = threading.Thread(target=advance_after_delay, daemon=True)
    delay_thread.start()
```

### **After (GameDirector-Based):**
```python
# ✅ In game_director.py - already handled above
def execute_player_action(self, player, action, amount):
    # All timing through event scheduling, no threading
    if self.state_machine.execute_action(player, action, amount):
        self._update_ui()
        if self._is_bot_turn_next():
            self.schedule_event(1500, "execute_bot_action", {})
```

---

## 🧹 **Phase 3: Clean Up State Machine**

### **Remove from PracticeSessionPokerStateMachine:**
- `_execute_bot_action_with_timing()`
- `_cancel_active_timers()`
- `_active_timers`
- `_expected_player_index`
- All `threading.Timer` usage

### **Keep in PracticeSessionPokerStateMachine:**
- Pure game logic
- Action validation
- State transitions
- Bot decision algorithms (as pure functions)

---

## 🎨 **Phase 4: UI Renderer Pattern**

```python
# ✅ Make UI components pure renderers
class ReusablePokerGameWidget(ttk.Frame):
    def render_current_state(self):
        """Pure render function - no timing, no state storage."""
        if not self.game_director:
            return
            
        # Get current state from single source
        game_state = self.game_director.state_machine.get_game_info()
        
        # Render immediately
        self._render_players(game_state["players"])
        self._render_board(game_state["board"])
        self._render_pot(game_state["pot"])
        self._render_dealer_button(game_state["dealer_position"])
        self._render_action_player_highlight(game_state["action_player"])
        
    def _render_action_player_highlight(self, action_player_index):
        """Immediately apply highlight to action player."""
        # Clear all highlights
        self._clear_all_highlights()
        # Apply highlight to current action player
        if 0 <= action_player_index < len(self.player_seats):
            self._apply_action_highlight(action_player_index)
```

---

## 🧪 **Testing Pattern**

```python
# test_game_director.py
def test_bot_action_timing():
    """Test that bot actions are properly scheduled."""
    # Setup
    game_director = GameDirector(mock_state_machine, mock_ui, mock_audio, mock_logger)
    
    # Execute human action
    game_director.execute_player_action(human_player, ActionType.CALL, 10)
    
    # Verify bot action is scheduled (not executed immediately)
    assert len(game_director.event_queue) == 1
    assert game_director.event_queue[0].event_type == "execute_bot_action"
    
    # Advance time and verify bot action executes
    game_director.update()  # Should execute the scheduled event
    assert mock_state_machine.last_action == "bot_action_executed"
```

---

## ⚡ **Quick Migration Checklist**

- [ ] Create `GameDirector` class
- [ ] Route player actions through `GameDirector.execute_player_action()`
- [ ] Replace `threading.Timer` with `GameDirector.schedule_event()`
- [ ] Make UI updates synchronous via `render_current_state()`
- [ ] Remove duplicate state variables from UI components
- [ ] Test that timing bugs are resolved

---

## 🎯 **Expected Benefits After Migration**

1. **🐛 Zero Timing Conflicts**: Single event queue eliminates race conditions
2. **🧪 Deterministic Testing**: No threading = predictable test results  
3. **🔧 Easy Debugging**: Single event log shows all game flow
4. **⚡ Better Performance**: No thread overhead or synchronization
5. **📈 Maintainable Code**: Clear responsibilities and single source of truth

---

This architecture will eliminate the cascading highlight/sound/timing bugs you've been experiencing and provide a solid foundation for future development!
