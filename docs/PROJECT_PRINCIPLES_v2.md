## Project Principles v2 (Authoritative)

### Architecture
- Single-threaded, event-driven coordinator (GameDirector). All timing via coordinator.
- Single source of truth per session (Store). No duplicate state.
- Event-driven only. UI is pure render from state; no business logic in UI.
- **MVU Pattern**: For complex UI, use Model-View-Update architecture (see `PokerPro_MVU_Architecture_Guide_v2.md`).

### Separation of concerns
- Domain: entities, rules, state machines; pure and deterministic.
- Application/Services: orchestration, schedulers, adapters; no UI.
- Adapters: persistence, audio, estimators, external APIs.
- UI: render-only; reads from Store; raises intents.

### Coding standards
- OO-first; composition/strategies/state machines over conditionals.
- DRY; reuse components; small, stable public APIs.
- Deterministic core; isolate I/O, randomness, timing.
- Explicit dependency injection; avoid globals/singletons.

### UI design
- Canvas layers: felt < seats < community < pot < overlay.
- Theme tokens only; central ThemeManager; hot-swappable profiles.
- Accessibility: ≥4.5:1 contrast; 44×44 targets; keyboard bindings; live regions.

### Testing & logging
- Snapshot tests for UI; unit tests for reducers/selectors and adapters.
- Logs to `logs/` with rotation; ISO timestamps; module:file:line; no secrets/PII.

### Prohibitions
- No threading/timers for game logic; no blocking animations/sounds.
- No duplicate state sources; no component-to-component timing calls.
- **No mutable collections in MVU models** (use `tuple`, `frozenset`, `Mapping`).
- **No auto-generated equality for nested structures** (implement custom `__eq__`).
- **No data loading during UI initialization** (defer until components ready).

### 🚫 CRITICAL AI AGENT COMPLIANCE RULES (NEVER VIOLATE)

#### **🔥 MVU INFINITE LOOP PREVENTION (CRITICAL)**

**❌ NEVER USE MUTABLE COLLECTIONS IN MVU MODELS**
```python
# WRONG - Will cause infinite loops
@dataclass(frozen=True)
class Model:
    seats: Dict[int, SeatState]  # ❌ Mutable Dict
    legal_actions: Set[str]      # ❌ Mutable Set

# CORRECT - Prevents infinite loops  
@dataclass(frozen=True)
class Model:
    seats: Mapping[int, SeatState]  # ✅ Immutable Mapping
    legal_actions: frozenset[str]   # ✅ Immutable frozenset
```

**❌ NEVER RELY ON AUTO-GENERATED EQUALITY**
```python
# WRONG - eq=True fails with nested objects
@dataclass(frozen=True, eq=True)
class Props: ...

# CORRECT - Custom equality works
@dataclass(frozen=True, eq=False)
class Props:
    def __eq__(self, other): ...
```

**❌ NEVER LOAD DATA DURING UI __init__**
```python
# WRONG - Race condition causes loops
def __init__(self):
    self._init_mvu()
    self._load_hand(0)  # ❌ Too early!

# CORRECT - Deferred loading
def __init__(self):
    self._init_mvu()
    self._mvu_initialized = True
def _load_data(self):
    if hasattr(self, '_mvu_initialized'):
        self._load_hand(0)  # ✅ Safe timing
```

**🔍 REFERENCE: See `docs/PokerPro_MVU_Architecture_Guide_v2.md` for complete infinite loop prevention guide.**

#### **🔥 ARCHITECTURE VIOLATIONS THAT MUST BE PREVENTED**

**❌ VIOLATION 1: Business Logic in UI Components**
```python
# ❌ FORBIDDEN - Business logic in UI
def _next_action(self):
    session_state = self.session_manager.execute_action()  # WRONG!
    self._update_ui(session_state)

# ✅ CORRECT - Pure UI dispatch
def _next_action(self):
    self.store.dispatch({"type": "HANDS_REVIEW_NEXT_ACTION"})
```

**❌ VIOLATION 2: Direct Service Calls from UI**
```python
# ❌ FORBIDDEN - Direct service calls
self.session_manager.execute_action()  # WRONG!
self.effect_bus.play_sound("bet")      # WRONG!

# ✅ CORRECT - Event-driven
self.store.dispatch({"type": "NEXT_ACTION"})
self.event_bus.publish("sound:play", {"type": "bet"})
```

**❌ VIOLATION 3: Timing Violations**
```python
# ❌ FORBIDDEN - Direct timing calls
self.after(1000, callback)           # WRONG!
threading.Timer(1.0, callback)      # WRONG!
time.sleep(1)                        # WRONG!

# ✅ CORRECT - GameDirector timing
self.game_director.schedule(1000, {"type": "DELAYED_ACTION", "callback": callback})
```

**❌ VIOLATION 4: State Mutations in UI**
```python
# ❌ FORBIDDEN - Direct state mutation
self.game_state.pot += 100           # WRONG!
self.display_state['acting'] = True  # WRONG!

# ✅ CORRECT - Store dispatch
self.store.dispatch({"type": "UPDATE_POT", "amount": 100})
```

#### **✅ MANDATORY COMPLIANCE RULES**

1. **UI Components MUST be Pure Renderers**
2. **All Communication MUST be Event-Driven**  
3. **All Timing MUST go through GameDirector**
4. **Single Source of Truth MUST be Maintained**
5. **Store/Reducer Pattern MUST be Used**

#### **🛡️ ENFORCEMENT CHECKLIST**
- [ ] No business logic in UI components
- [ ] No direct service calls from UI  
- [ ] No timing violations (after/Timer/sleep)
- [ ] All state changes via Store dispatch
- [ ] Event-driven communication only

### AI Agent Compliance (Do not deviate)
1. Do **not** add new events or fields. If missing, leave TODO and stop.
2. Never compute poker legality in UI; call selectors/PPSM.
3. Use theme tokens only; no literal colors, shadows, or fonts.
4. Do not use timers/threads for game logic; schedule via Director.
5. No cross-component writes; only Store and events.
6. Respect casing rules (events UPPER_SNAKE_CASE; domain snake_case).
7. Keep functions small and pure; side effects only in adapters.
8. If uncertain, generate interface stubs, not implementations.
9. **NEVER put business logic in UI components - they are pure renderers only**
10. **ALWAYS use Store/Reducer pattern - no direct service calls from UI**
11. **ALL timing must go through GameDirector - no self.after() violations**

### PR Acceptance Checklist
- [ ] No business logic in UI; all decisions via PPSM or DecisionEngine.
- [ ] Events are UPPER_SNAKE_CASE; fields snake_case; streets uppercase.
- [ ] Only theme tokens used; contrast checks pass.
- [ ] Components subscribe via selectors; no direct Store writes.
- [ ] Replay tests pass on sample hands; headless run produces stable state hashes.
- [ ] Logs are present, structured, and scrubbed.
