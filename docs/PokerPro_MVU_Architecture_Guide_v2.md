# PokerPro MVU Architecture Guide v2.0
**Status**: Critical Reference - Prevents Infinite Loop Bugs  
**Last Updated**: January 2025  
**Purpose**: Authoritative guide for MVU implementation with explicit anti-patterns  

---

## 🚨 **CRITICAL: PREVENTING INFINITE LOOPS**

### **The Infinite Loop Problem**
The MVU architecture is susceptible to infinite rendering loops when:
1. **Equality checks fail** between identical data structures
2. **State oscillates** between empty and populated states  
3. **UI callbacks trigger** during programmatic updates
4. **Props are recreated** on every render cycle

### **Mandatory Prevention Patterns**

#### **1. ALWAYS Use Immutable Collections in Models**

```python
# ❌ NEVER DO THIS - Causes equality check failures
@dataclass(frozen=True)
class Model:
    seats: Dict[int, SeatState]  # WRONG - mutable Dict
    legal_actions: Set[str]      # WRONG - mutable Set
    banners: List[Banner]        # WRONG - mutable List

# ✅ ALWAYS DO THIS - Enables proper equality
from typing import Mapping, FrozenSet

@dataclass(frozen=True)
class Model:
    seats: Mapping[int, SeatState]  # CORRECT - immutable Mapping
    legal_actions: frozenset[str]   # CORRECT - immutable frozenset
    banners: tuple[Banner, ...]     # CORRECT - immutable tuple
```

#### **2. ALWAYS Implement Explicit Equality Methods**

```python
# ❌ NEVER RELY ON AUTO-GENERATED EQUALITY
@dataclass(frozen=True, eq=True)  # Auto eq=True FAILS with nested objects
class TableRendererProps:
    seats: Dict[int, SeatState]

# ✅ ALWAYS IMPLEMENT CUSTOM EQUALITY
@dataclass(frozen=True, eq=False)  # Disable auto-equality
class TableRendererProps:
    seats: Mapping[int, SeatState]
    
    def __eq__(self, other):
        """Deep equality that actually works"""
        if not isinstance(other, TableRendererProps):
            return False
        # Compare dictionaries by converting to dict
        return dict(self.seats) == dict(other.seats)
```

#### **3. ALWAYS Guard Against State Resets**

```python
# ✅ MANDATORY STORE PROTECTION
def dispatch(self, msg: Msg) -> None:
    old_model = self.model
    new_model, commands = update(self.model, msg)
    
    # CRITICAL: Prevent unexpected state resets
    if (len(old_model.seats) > 0 and 
        len(new_model.seats) == 0 and
        type(msg).__name__ not in ['ResetHand', 'ClearTable']):
        print(f"⚠️ Blocking suspicious reset: {type(msg).__name__}")
        return  # Reject the update
    
    # Only notify if model actually changed
    if new_model != old_model:
        self.model = new_model
        for subscriber in self.subscribers[:]:  # Use slice!
            subscriber(new_model)
```

#### **4. ALWAYS Defer Initial Data Loading**

```python
# ❌ NEVER LOAD DATA IN __init__
def __init__(self):
    self._initialize_mvu()
    self._load_hand(0)  # WRONG - Race condition!

# ✅ ALWAYS DEFER INITIAL LOAD
def __init__(self):
    self._initialize_mvu()
    self._mvu_initialized = True
    # Load data AFTER initialization
    
def _load_hands_data(self):
    # Only load if MVU is ready
    if hasattr(self, '_mvu_initialized'):
        self._load_hand(0)
```

#### **5. ALWAYS Disable Callbacks During Programmatic Updates**

```python
# ✅ MANDATORY CALLBACK PROTECTION
def _update_review_controls(self, props):
    if not hasattr(self, '_updating_scale'):
        self._updating_scale = False
    
    if not self._updating_scale:
        self._updating_scale = True
        try:
            # Temporarily disable callback
            self.review_scale.config(command="")
            self.review_scale.set(props.review_cursor)
            # Re-enable after delay
            self.after(10, lambda: self.review_scale.config(
                command=self._on_review_seek))
        finally:
            self._updating_scale = False
```

---

## 📋 **MVU IMPLEMENTATION CHECKLIST**

### **Model Definition Requirements**
- [ ] All collections use immutable types (`tuple`, `frozenset`, `Mapping`)
- [ ] Custom `__eq__` method implemented for all dataclasses
- [ ] Custom `__hash__` method for frozen dataclasses
- [ ] No mutable default values in dataclass fields
- [ ] `frozen=True` on all model dataclasses

### **Store Implementation Requirements**
- [ ] Guard against suspicious state resets
- [ ] Check model equality before notifying subscribers
- [ ] Use slice when iterating subscribers to avoid mutation
- [ ] Log all state transitions for debugging
- [ ] Thread-safe with proper locking

### **View Implementation Requirements**  
- [ ] Props cached and compared before rendering
- [ ] UI callbacks disabled during programmatic updates
- [ ] Initialization order: Create → Initialize → Subscribe → Load
- [ ] First empty render skipped in review mode
- [ ] All renders logged with seat count

### **Testing Requirements**
- [ ] Test equality between identical models returns `True`
- [ ] Test props comparison with nested structures
- [ ] Test store rejects invalid state transitions
- [ ] Test no infinite loops in 5-second render test
- [ ] Test memory usage remains stable

---

## 🏗️ **MVU ARCHITECTURE PATTERNS**

### **The Three-Layer Architecture**

```
┌─────────────────────────────────────┐
│           View Layer                │
│  - Pure rendering functions         │
│  - No business logic                │
│  - Emits intents only              │
└─────────────┬───────────────────────┘
              │ Props (immutable)
┌─────────────▼───────────────────────┐
│           Model Layer               │
│  - Immutable state (Model)         │
│  - Pure update functions           │
│  - Deterministic transitions       │
└─────────────┬───────────────────────┘
              │ Commands (effects)
┌─────────────▼───────────────────────┐
│         Effects Layer               │
│  - Side effects (I/O, timers)      │
│  - Service calls                   │
│  - External integrations           │
└─────────────────────────────────────┘
```

### **Data Flow (Unidirectional)**

```
User Action → Intent → Message → Update → Model' → Props → Render
                           ↓
                        Commands → Effects → New Messages
```

### **Immutable Model Pattern**

```python
from dataclasses import dataclass, replace
from typing import Mapping, FrozenSet

@dataclass(frozen=True, slots=True)
class Model:
    """Immutable model with value semantics"""
    # Primitive immutable types
    hand_id: str
    pot: int
    
    # Immutable collections
    board: tuple[str, ...]
    seats: Mapping[int, SeatState]
    legal_actions: frozenset[str]
    
    def with_seats(self, seats: dict) -> 'Model':
        """Return new model with updated seats"""
        return replace(self, seats=seats)
    
    def __eq__(self, other):
        """Value-based equality"""
        if not isinstance(other, Model):
            return False
        return (
            self.hand_id == other.hand_id and
            self.pot == other.pot and
            self.board == other.board and
            dict(self.seats) == dict(other.seats) and
            self.legal_actions == other.legal_actions
        )
```

### **Props Memoization Pattern**

```python
class TableRenderer:
    def __init__(self):
        self._props_cache = {}
        self._last_model_hash = None
    
    def render(self, model: Model) -> None:
        # Create stable hash of model
        model_hash = self._compute_model_hash(model)
        
        # Check cache
        if model_hash == self._last_model_hash:
            return  # Skip render, nothing changed
        
        # Create props only when needed
        if model_hash not in self._props_cache:
            self._props_cache[model_hash] = TableRendererProps.from_model(model)
            # Limit cache size
            if len(self._props_cache) > 10:
                self._props_cache.pop(next(iter(self._props_cache)))
        
        props = self._props_cache[model_hash]
        self._last_model_hash = model_hash
        self._render_internal(props)
```

---

## 🧪 **TESTING FOR INFINITE LOOPS**

### **Mandatory Test Suite**

```python
import time
import threading

class TestMVUInfiniteLoopPrevention:
    
    def test_model_equality_with_nested_structures(self):
        """Ensure identical models are equal"""
        model1 = Model.initial()
        model2 = Model.initial()
        assert model1 == model2
        
        # With seats
        seats = {0: SeatState(...), 1: SeatState(...)}
        model1 = replace(model1, seats=seats)
        model2 = replace(model2, seats=seats)
        assert model1 == model2
    
    def test_no_infinite_render_loop(self):
        """Ensure no infinite rendering occurs"""
        render_count = [0]
        
        def counting_render(props):
            render_count[0] += 1
            if render_count[0] > 100:
                raise Exception("Infinite loop detected!")
        
        # Set up MVU with counting renderer
        store = MVUStore(Model.initial())
        renderer = MockRenderer(counting_render)
        store.subscribe(lambda m: renderer.render(
            TableRendererProps.from_model(m)))
        
        # Load hand data
        store.dispatch(LoadHand(hand_data={...}))
        
        # Wait for any async operations
        time.sleep(0.5)
        
        # Should have rendered once or twice, not 100+ times
        assert render_count[0] < 10
    
    def test_store_blocks_invalid_resets(self):
        """Ensure store prevents suspicious state resets"""
        store = MVUStore(Model.initial())
        
        # Load populated state
        store.dispatch(LoadHand(hand_data={'seats': {...}}))
        assert len(store.model.seats) > 0
        
        # Try to reset (should be blocked)
        store.dispatch(SomeOtherMessage())
        assert len(store.model.seats) > 0  # Still populated
    
    def test_props_caching_works(self):
        """Ensure props aren't recreated unnecessarily"""
        created_count = [0]
        
        original_from_model = TableRendererProps.from_model
        def counting_from_model(model):
            created_count[0] += 1
            return original_from_model(model)
        
        TableRendererProps.from_model = counting_from_model
        
        # Render same model multiple times
        model = Model.initial()
        renderer = TableRenderer()
        
        for _ in range(10):
            renderer.render(model)  # Same model
        
        # Props should be created once, not 10 times
        assert created_count[0] == 1
```

---

## 📐 **ARCHITECTURAL RULES**

### **Rule 1: Immutability First**
- Models are **always** immutable
- Use `replace()` to create new models
- Collections must be immutable types
- No in-place mutations ever

### **Rule 2: Explicit Over Implicit**
- Custom equality methods over auto-generated
- Explicit type annotations everywhere
- Clear subscription/unsubscription patterns
- Named constants for magic values

### **Rule 3: Defensive Programming**
- Guard against unexpected state transitions
- Validate inputs at boundaries
- Log everything for debugging
- Fail fast with clear error messages

### **Rule 4: Performance Through Design**
- Cache computed values (props, hashes)
- Early-out comparisons before expensive operations
- Batch updates when possible
- Profile and measure, don't guess

---

## 🎯 **QUICK REFERENCE: DO's AND DON'Ts**

### **DO's**
- ✅ Use `frozenset` for sets in models
- ✅ Use `tuple` for lists in models  
- ✅ Use `Mapping` for dicts in models
- ✅ Implement custom `__eq__` methods
- ✅ Cache props between renders
- ✅ Guard against state resets
- ✅ Defer initial data loading
- ✅ Disable UI callbacks during updates
- ✅ Test for infinite loops explicitly

### **DON'Ts**
- ❌ Use `Dict`, `List`, `Set` in frozen dataclasses
- ❌ Rely on auto-generated equality
- ❌ Create new props on every render
- ❌ Load data during initialization
- ❌ Allow callbacks during programmatic updates
- ❌ Skip equality checks before notifying
- ❌ Mutate subscriber lists during iteration
- ❌ Assume dataclass equality works

---

## 🔍 **DEBUGGING INFINITE LOOPS**

### **Symptoms to Watch For**
1. Console shows alternating states (0 seats → 2 seats → 0 seats)
2. CPU usage spikes to 100%
3. UI becomes unresponsive
4. Render count exceeds reasonable limits

### **Debugging Steps**
1. **Add render counting** to detect excessive renders
2. **Log all dispatches** with message types
3. **Log model transitions** with before/after seat counts
4. **Check equality** between supposedly identical models
5. **Trace callbacks** to find circular triggers
6. **Profile memory** to detect object creation loops

### **Common Root Causes**
1. **Mutable collections** in frozen dataclasses
2. **Missing equality methods** for nested structures
3. **Race conditions** during initialization
4. **Callback loops** from UI widgets
5. **Props recreation** on every render

---

## 🎯 **INTEGRATION WITH EXISTING ARCHITECTURE**

### **GameDirector Compatibility**
The MVU architecture works within the existing GameDirector pattern:

```python
# MVU commands trigger GameDirector scheduling
def _execute_schedule_timer(self, cmd: ScheduleTimer) -> None:
    """Execute timer command via GameDirector"""
    if self.game_director:
        self.game_director.schedule(
            cmd.delay_ms / 1000.0,
            lambda: self.dispatch(cmd.msg)
        )
```

### **Event Bus Integration**
MVU stores can publish to the legacy event bus:

```python
def _execute_publish_event(self, cmd: PublishEvent) -> None:
    """Publish event to legacy event bus"""
    if self.event_bus:
        self.event_bus.publish(cmd.event_type, cmd.data)
```

### **Service Container Access**
MVU components get services through dependency injection:

```python
class MVUHandsReviewTab:
    def __init__(self, parent, services: ServiceContainer):
        self.theme_manager = services.get_app("theme")
        self.effect_bus = services.get_app("effect_bus")
        # ... MVU initialization
```

---

## 🔧 **MIGRATION GUIDELINES**

### **From Legacy UI to MVU**

1. **Extract State**: Move all UI state into immutable Model
2. **Pure Renderers**: Convert UI components to pure functions
3. **Event Mapping**: Map UI events to MVU messages
4. **Command Effects**: Convert side effects to commands
5. **Test Thoroughly**: Verify no infinite loops

### **Gradual Migration Strategy**

1. **Start Small**: Convert one tab/component at a time
2. **Bridge Pattern**: Use adapters between MVU and legacy
3. **Shared Services**: Keep using ServiceContainer
4. **Incremental Testing**: Test each migration step
5. **Monitor Performance**: Watch for regressions

---

*This document is **mandatory reading** for all developers and AI agents working on MVU implementations. Violations of these patterns **will** cause infinite loops.*
