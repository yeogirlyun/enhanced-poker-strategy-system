# 🏗️ **POKER PROJECT ARCHITECTURE RULES**
## **Mandatory Guidelines for AI Assistants**

> **⚠️ CRITICAL**: These rules MUST be followed in all AI sessions. Any code changes that violate these principles should be rejected.

---

## 🎯 **CORE ARCHITECTURE PRINCIPLE**

### **Single-Threaded Event-Driven Game Director Pattern**

The Poker Training System uses a **centralized, single-threaded event-driven architecture** with a GameDirector as the single source of truth for all timing and coordination.

```
✅ REQUIRED ARCHITECTURE:

┌─────────────────────────────────────────────┐
│                GAME DIRECTOR                │ ← SINGLE SOURCE OF TRUTH
│  - Controls ALL timing                     │
│  - Schedules ALL events                    │  
│  - Manages state transitions               │
│  - Coordinates all components              │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│   Game   │ │  Audio   │ │    UI    │
│  Engine  │ │ Manager  │ │ Renderer │
│ (FPSM)   │ │          │ │ (Widgets)│
└──────────┘ └──────────┘ └──────────┘
```

---

## 🚫 **FORBIDDEN PATTERNS** 

### **❌ NEVER USE - These Patterns Cause Cascading Bugs:**

1. **Multiple Threading for Game Logic**
   ```python
   # ❌ FORBIDDEN
   threading.Timer(delay, execute_bot_action)
   threading.Thread(target=advance_player)
   
   # ✅ REQUIRED: Use GameDirector event scheduling
   game_director.schedule_event(delay_ms, "bot_action", data)
   ```

2. **Direct Timing Control in Components**
   ```python
   # ❌ FORBIDDEN: Components controlling their own timing
   class PokerWidget:
       def _schedule_highlight_update(self):
           self.after(500, self._update_highlight)  # NO!
   
   # ✅ REQUIRED: GameDirector controls timing
   game_director.schedule_event(500, "update_highlight", {})
   ```

3. **Multiple Sources of Game State**
   ```python
   # ❌ FORBIDDEN: Duplicate state tracking
   class UI:
       self.current_action_player = 2  # NO!
       self.pending_highlight_player = 1  # NO!
       
   # ✅ REQUIRED: Single source
   action_player = game_state_machine.action_player_index  # ONLY SOURCE
   ```

4. **Blocking Audio/Animation Operations**
   ```python
   # ❌ FORBIDDEN: Blocking operations
   play_sound_and_wait(duration)
   time.sleep(voice_duration)
   
   # ✅ REQUIRED: Non-blocking with callbacks
   audio_manager.play_sound(sound, callback=on_sound_complete)
   ```

---

## ✅ **REQUIRED PATTERNS**

### **1. Event-Driven Communication**

```python
# ✅ All communication via events
class GameDirector:
    def execute_player_action(self, player, action, amount):
        # 1. Update state
        if self.state_machine.execute_action(player, action, amount):
            # 2. Emit events (never direct calls)
            self.emit_event("action_executed", {player, action, amount})
            self.emit_event("ui_update_required", {})
            
            # 3. Schedule follow-up events
            if action_sound_needed:
                self.schedule_event(0, "play_sound", {action})
            if bot_turn_next:
                self.schedule_event(1500, "bot_action", {})
```

### **2. Pure Render Functions**

```python
# ✅ UI components are pure renderers
class PokerWidget:
    def render_game_state(self, game_state):
        """Pure function - no timing, no state storage"""
        self._update_player_display(game_state.players)
        self._update_highlights(game_state.action_player)
        self._update_dealer_button(game_state.dealer_position)
        # NO scheduling, NO timers, NO state storage
```

### **3. Single State Source**

```python
# ✅ Components read state, never store it
class UIComponent:
    def update_display(self):
        # Get state from single source
        game_state = self.game_director.get_current_state()
        # Render immediately
        self.render_game_state(game_state)
        # No local state variables!
```

---

## 📋 **COMPONENT RESPONSIBILITIES**

### **🎮 GameDirector** - The Central Coordinator
- **Controls**: ALL timing, event scheduling, component coordination
- **Owns**: Event queue, timing logic, component lifecycle
- **Never**: Implements game rules or UI rendering

### **🧠 FlexiblePokerStateMachine (FPSM)** - Pure Game Logic
- **Controls**: Game state, rule validation, winner determination
- **Owns**: Game state, player data, hand evaluation
- **Never**: Handles timing, UI updates, or audio

### **🎨 UI Components** - Pure Renderers
- **Controls**: Display appearance only
- **Owns**: Visual styling, layout, animations
- **Never**: Game logic, timing, or state storage

### **🔊 AudioManager** - Sound Coordination
- **Controls**: Sound playback, duration tracking
- **Owns**: Sound assets, playback state
- **Never**: Game timing or UI updates

---

## 🛠️ **IMPLEMENTATION RULES**

### **For State Machine Changes:**
1. **MUST**: Keep state machines pure (no timing logic)
2. **MUST**: Emit events for all state changes
3. **MUST**: Validate actions synchronously
4. **NEVER**: Use threading or delays in state machine

### **For UI Changes:**
1. **MUST**: Make UI components stateless renderers
2. **MUST**: Update UI through GameDirector events
3. **MUST**: Use immediate rendering (no delayed updates)
4. **NEVER**: Store game state in UI components

### **For Audio/Animation:**
1. **MUST**: Use non-blocking audio with callbacks
2. **MUST**: Schedule follow-up actions through GameDirector
3. **MUST**: Provide duration estimates for timing
4. **NEVER**: Use blocking operations or sleep()

### **For Bot Logic:**
1. **MUST**: Implement bots as pure decision functions
2. **MUST**: Execute bot actions through GameDirector
3. **MUST**: Use event scheduling for bot timing
4. **NEVER**: Use threading or timers in bot logic

---

## 🧪 **TESTING REQUIREMENTS**

### **All Code Changes Must:**
1. **Be deterministic**: No threading = predictable tests
2. **Be synchronous**: All operations complete immediately
3. **Be event-driven**: Testable via event injection
4. **Have single state source**: Easy to verify state

### **Test Pattern:**
```python
def test_player_action():
    # Setup
    game_director = GameDirector(state_machine, ui, audio)
    
    # Execute
    game_director.execute_player_action(player, ACTION.CALL, 10)
    
    # Verify (all synchronous)
    assert state_machine.action_player_index == expected_next_player
    assert ui.last_rendered_state.pot == expected_pot
    assert len(game_director.event_queue) == expected_scheduled_events
```

---

## 🚨 **DEBUGGING GUIDELINES**

### **When Bugs Occur:**
1. **Check event queue**: All actions should be in GameDirector events
2. **Verify single state source**: No duplicate state tracking
3. **Confirm no threading**: All operations in main thread
4. **Validate event order**: Events should be deterministic

### **Common Anti-Patterns to Avoid:**
- "Quick fix" timers or delays
- Direct component-to-component calls
- State storage in UI components
- Threading for "better performance"

---

## 📝 **CODE REVIEW CHECKLIST**

Before accepting any code changes, verify:

- [ ] **No new threading**: No `threading.Timer`, `Thread`, or `sleep()`
- [ ] **Single state source**: No duplicate state variables
- [ ] **Event-driven**: Components communicate via events only
- [ ] **Pure functions**: UI renders immediately from state
- [ ] **GameDirector control**: All timing goes through GameDirector
- [ ] **No blocking operations**: Audio/animations are non-blocking
- [ ] **Deterministic**: Code behavior is predictable
- [ ] **Testable**: Changes include synchronous tests

---

## 🎯 **MIGRATION STRATEGY**

### **Phase 1: GameDirector Introduction**
- Implement minimal GameDirector
- Route key actions through it
- Keep existing components temporarily

### **Phase 2: Threading Elimination**
- Replace all `threading.Timer` with event scheduling
- Make UI updates synchronous
- Implement non-blocking audio

### **Phase 3: State Centralization**
- Remove duplicate state variables
- Make UI components stateless
- Single source of truth for all game state

### **Phase 4: Pure Components**
- Convert UI to pure renderers
- Make state machine pure logic
- Remove all mixed responsibilities

---

## 💡 **QUICK REFERENCE**

### **✅ When in doubt, ask:**
- Does this component control its own timing? → **Should be NO**
- Does this component store game state? → **Should be NO** 
- Does this use threading for game logic? → **Should be NO**
- Does this go through GameDirector? → **Should be YES**

### **🎯 Golden Rule:**
> **"Every timing decision flows through GameDirector. Every state question is answered by FPSM. Every display update is a pure render."**

---

## 📞 **AI ASSISTANT INSTRUCTIONS**

When working on this codebase:

1. **ALWAYS** refer to these rules before implementing changes
2. **REJECT** any suggestions that violate these patterns
3. **PROPOSE** refactoring when legacy patterns are encountered
4. **EXPLAIN** architecture benefits when making changes
5. **ENSURE** all changes follow event-driven, single-threaded principles

**Remember**: Short-term convenience that violates these rules creates long-term architectural debt and cascading bugs.

---

*Last Updated: 2025-01-13*
*Architecture Version: 2.0 - Single-Threaded Event-Driven*
