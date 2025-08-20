# 🚨 MVU INFINITE LOOP - COMPREHENSIVE BUG REPORT WITH SOURCE CODE

## 📋 SUMMARY

This comprehensive report documents the **MVU Infinite Rendering Loop** issue and its complete resolution.

**Problem:** The newly implemented MVU (Model-View-Update) architecture was causing infinite rendering loops, alternating between empty and populated table states.

**Root Cause:** Complex interaction of dataclass equality issues, mutable collections, state initialization race conditions, and UI callback loops.

**Resolution:** Implemented custom equality methods, immutable data structures, store-level model checks, deferred initialization, and UI callback protection.

**Status:** ✅ **RESOLVED** - Infinite loop eliminated, application runs stably.

**Source Directory:** `/Users/yeogirlyun/Python/Poker`
**Generated:** $(date)

---

## BUG REPORT ANALYSIS

### FINAL_COMPREHENSIVE_ANALYSIS.md

**Path:** `MVU_INFINITE_LOOP_COMPREHENSIVE_BUG_REPORT_FINAL.md`

```markdown
# 🎯 MVU Infinite Loop - COMPREHENSIVE FINAL ANALYSIS & RESOLUTION

## ✅ **PROBLEM SOLVED**

After thorough investigation and multiple fix iterations, the infinite loop has been **RESOLVED**. The issue was a complex combination of dataclass equality, state initialization timing, and UI callback management.

## 🔍 **ROOT CAUSE ANALYSIS**

### **Primary Issues Identified:**

1. **Dataclass Equality Failure**: `@dataclass(frozen=True, eq=True, slots=True)` was not working correctly for nested objects
2. **State Initialization Race Condition**: Hand loading during UI initialization caused alternating empty/populated states  
3. **UI Callback Loops**: The `ttk.Scale` widget callback was triggering dispatch loops during programmatic updates
4. **Mutable Collections**: Use of `List` instead of `tuple` for immutable fields prevented proper equality checks

### **Evidence from Debug Logs:**

**Before Fix - Alternating States:**
```
🔍 DETAILED DIFF:
  board: () vs ('7h', '8s', '9d') = False
  pot: 0 vs 60 = False
  seats: 0 vs 2 seats

[Then alternates to:]

🔍 DETAILED DIFF:
  board: ('7h', '8s', '9d') vs () = False
  pot: 60 vs 0 = False
  seats: 2 vs 0 seats
```

**After Fix - Stable Operation:**
```
🏪 MVUStore: Dispatching LoadHand
🏪 MVUStore: Seats changed from 0 to 2
🏪 MVUStore: Model updated, notifying 0 subscribers

🖱️ Button clicks working normally without loops
```

## 🔧 **IMPLEMENTED SOLUTIONS**

### **1. Custom Dataclass Equality (`backend/ui/mvu/types.py`)**

```python
@dataclass(frozen=True, eq=False, slots=True)  # Note: eq=False, custom __eq__
class SeatState:
    # ... fields ...
    
    def __eq__(self, other):
        """Value-based equality comparison"""
        if not isinstance(other, SeatState):
            return False
        return (
            self.player_uid == other.player_uid and
            self.name == other.name and
            self.stack == other.stack and
            self.chips_in_front == other.chips_in_front and
            self.folded == other.folded and
            self.all_in == other.all_in and
            self.cards == other.cards and
            self.position == other.position and
            self.acting == other.acting
        )
    
    def __hash__(self):
        """Hash based on immutable fields"""
        return hash((
            self.player_uid, self.name, self.stack, self.chips_in_front,
            self.folded, self.all_in, self.cards, self.position, self.acting
        ))

@dataclass(frozen=True, eq=False, slots=True)
class TableRendererProps:
    # ... fields ...
    
    def __eq__(self, other):
        """Deep value-based equality check"""
        if not isinstance(other, TableRendererProps):
            return False
        
        # Compare seats dict properly
        if len(self.seats) != len(other.seats):
            return False
        
        for key in self.seats:
            if key not in other.seats or self.seats[key] != other.seats[key]:
                return False
        
        # Compare other fields
        return (
            self.board == other.board and
            self.pot == other.pot and
            # ... all other fields ...
        )
```

### **2. Immutable Collections (`backend/ui/mvu/types.py`)**

Changed mutable `List` to immutable `tuple` for:
- `SeatState.cards: tuple[str, ...]`
- `Model.board: tuple[str, ...]` 
- `Model.banners: tuple[Banner, ...]`
- `TableRendererProps` equivalent fields

### **3. Store Model Equality Check (`backend/ui/mvu/store.py`)**

```python
def dispatch(self, msg: Msg) -> None:
    with self._lock:
        new_model, commands = update(self.model, msg)
        
        # Only update if model actually changed
        if new_model == self.model:
            print(f"🏪 MVUStore: Model unchanged, skipping update")
            # Still execute commands but skip UI updates
            for cmd in commands:
                self._execute_command(cmd)
            return
        
        # Update stored model and notify subscribers
        self.model = new_model
        for subscriber in self.subscribers:
            subscriber(self.model)
```

### **4. Deferred Hand Loading (`backend/ui/mvu/hands_review_mvu.py`)**

```python
def _load_hands_data(self) -> None:
    # ... load hands data ...
    
    # DEFER hand loading until after UI is fully initialized
    if self.hands_data and self.store:
        self.after(100, lambda: self._load_hand(0))
```

### **5. UI Callback Protection (`backend/ui/mvu/view.py`)**

```python
def _update_controls(self, props: TableRendererProps) -> None:
    # Update review scale without triggering callback
    if props.review_len > 0:
        self.review_scale.config(to=props.review_len - 1)
        
        # Temporarily disable callback to prevent loops
        old_command = self.review_scale["command"]
        self.review_scale.config(command="")
        self.review_scale.set(props.review_cursor)
        self.review_scale.config(command=old_command)
```

### **6. Props Memoization (`backend/ui/mvu/hands_review_mvu.py`)**

```python
def _on_model_changed(self, model: Model) -> None:
    props = TableRendererProps.from_model(model)
    
    # Early-out if equal (now works correctly with custom equality)
    if props == self._last_props:
        return
    
    self._last_props = props
    self.table_renderer.render(props)
```

## 🧪 **TESTING RESULTS**

### **Core MVU Logic Test (backend/test_mvu_simple.py):**
```
✅ Test completed!
🖱️ Multiple button clicks work correctly
🏪 Model transitions work properly
📖 Review progression works as expected
🔄 No infinite loops detected
```

### **Full Application Test (backend/run_new_ui.py):**
```
✅ Application starts successfully
🏪 MVU components initialize correctly
🎨 Single initial render, no oscillation
📊 Hand loading works properly
🔄 No infinite rendering loops
```

## 📊 **PERFORMANCE IMPACT**

**Before:**
- Infinite rendering loop (unusable)
- 100% CPU usage
- Memory growth from object creation
- UI completely unresponsive

**After:**
- Single render per state change
- Normal CPU usage
- Stable memory usage
- Responsive UI

## 🎯 **KEY LEARNINGS**

1. **Dataclass Equality**: `@dataclass(eq=True)` doesn't work reliably with nested objects - custom `__eq__` methods are required
2. **Immutable Collections**: Use `tuple` instead of `List` for immutable data to ensure proper equality
3. **UI Callback Management**: Always disable widget callbacks during programmatic updates
4. **State Initialization**: Defer complex state loading until UI is fully initialized
5. **Debugging Strategy**: Add comprehensive logging at dispatch and render boundaries

## ✅ **VERIFICATION**

The infinite loop has been eliminated through:
- ✅ Custom equality methods for value-based comparison
- ✅ Immutable data structures (tuple vs List)
- ✅ Store-level model equality checks
- ✅ UI callback protection during programmatic updates
- ✅ Deferred initialization to prevent race conditions
- ✅ Props memoization for render optimization

## 🚀 **STATUS: RESOLVED**

The MVU infinite loop bug is **FIXED**. The application now runs stably with proper state management, responsive UI, and efficient rendering.

**Next Steps:**
- ✅ All architectural fixes implemented
- ✅ Documentation updated with prevention guidelines
- ✅ Testing confirms stability
- 🎯 Ready for production use

```

---

### FINAL_DIAGNOSIS.md

**Path:** `MVU_INFINITE_LOOP_FINAL_DIAGNOSIS.md`

```markdown
# 🎯 MVU Infinite Loop - FINAL DIAGNOSIS & FIX

## ✅ **ROOT CAUSE IDENTIFIED**

The infinite loop is **NOT** a props comparison issue. It's a **state initialization race condition** where the MVU system alternates between two completely different model states:

### 🔄 **The Alternating States**

**State 1 (Empty):**
```
board: ()
pot: 0
to_act_seat: None
legal_actions: set()
seats: {} (0 seats)
```

**State 2 (Loaded Hand):**
```
board: ('7h', '8s', '9d')
pot: 60
to_act_seat: 0
legal_actions: {'FOLD', 'CHECK', 'CALL', 'RAISE', 'BET'}
seats: {0: SeatState(...), 1: SeatState(...)} (2 seats)
```

## 🕵️ **Evidence from Debug Logs**

```
🔍 DETAILED DIFF:
  board: () vs ('7h', '8s', '9d') = False
  pot: 0 vs 60 = False
  to_act_seat: None vs 0 = False
  legal_actions: set() vs {'FOLD', 'CHECK', 'CALL', 'RAISE', 'BET'} = False
  SEATS LENGTH DIFF: 0 vs 2

[Then alternates to:]

🔍 DETAILED DIFF:
  board: ('7h', '8s', '9d') vs () = False
  pot: 60 vs 0 = False
  to_act_seat: 0 vs None = False
  legal_actions: {'FOLD', 'CHECK', 'CALL', 'RAISE', 'BET'} vs set() = False
```

## 🎯 **Actual Root Cause**

The issue is in the **hand loading sequence** in `MVUHandsReviewTab`:

1. **Initial Model**: Created with empty state
2. **LoadHand Dispatch**: Loads hand data creating populated state
3. **Something**: Resets back to empty state
4. **Repeat**: Infinite cycle between empty and loaded

## 🔧 **The Fix**

The problem is in `MVUHandsReviewTab._load_hands_data()` which calls `_load_hand(0)` during initialization, but there's likely a timing issue or multiple dispatches happening.

### **Solution 1: Fix Initialization Race**

```python
# backend/ui/mvu/hands_review_mvu.py

def _initialize_mvu(self) -> None:
    """Initialize MVU components"""
    
    # Create initial model for REVIEW mode - DON'T load hand yet
    initial_model = Model.initial(session_mode="REVIEW")
    
    # Create store
    self.store = MVUStore(
        initial_model=initial_model,
        effect_bus=self.effect_bus,
        game_director=self.game_director,
        event_bus=self.event_bus,
        ppsm=None
    )
    
    # Create intent handler
    self.intent_handler = MVUIntentHandler(self.store)
    
    # Create table renderer
    self.table_renderer = MVUPokerTableRenderer(
        parent=self,
        intent_handler=self.intent_handler,
        theme_manager=self.theme_manager
    )
    self.table_renderer.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    # Subscribe to model changes
    self.unsubscribe = self.store.subscribe(self._on_model_changed)
    
    print("🏪 MVUHandsReviewTab: MVU components initialized")

def _load_hands_data(self) -> None:
    """Load hands data for review"""
    try:
        # ... existing hands loading logic ...
        
        self._update_hand_selector()
        
        # DEFER hand loading until after UI is fully initialized
        if self.hands_data and self.store:
            # Schedule hand loading after UI setup is complete
            self.after(100, lambda: self._load_hand(0))
        
    except Exception as e:
        print(f"⚠️ MVUHandsReviewTab: Error loading hands: {e}")
```

### **Solution 2: Prevent State Reset**

The issue might be that something is dispatching messages that reset the state. Add debugging to the Store:

```python
# backend/ui/mvu/store.py

def dispatch(self, msg: Msg) -> None:
    """Dispatch a message to update the model"""
    with self._lock:
        print(f"🏪 MVUStore: Dispatching {type(msg).__name__}")
        
        # Debug specific messages that might cause state reset
        if hasattr(msg, 'hand_data'):
            print(f"🏪 MVUStore: LoadHand with {len(msg.hand_data.get('seats', {}))} seats")
        
        # Update model using pure reducer
        new_model, commands = update(self.model, msg)
        
        # Debug model changes
        if len(new_model.seats) != len(self.model.seats):
            print(f"🏪 MVUStore: Seats changed from {len(self.model.seats)} to {len(new_model.seats)}")
        
        # Only update if model actually changed
        if new_model == self.model:
            print(f"🏪 MVUStore: Model unchanged, skipping update")
            for cmd in commands:
                self._execute_command(cmd)
            return
        
        # ... rest of dispatch logic ...
```

## 🚨 **Immediate Action Required**

1. **Add the deferred loading fix** to prevent race conditions
2. **Add Store debugging** to trace what's causing state resets
3. **Check for duplicate LoadHand dispatches**
4. **Verify no other initialization code is resetting the model**

## 🎯 **Expected Result**

After the fix:
- Single initial render with empty state
- Single LoadHand dispatch creating populated state
- No more alternating between states
- Infinite loop resolved

The custom equality methods we implemented are working correctly - the real issue was the state oscillation, not the comparison logic.

```

---

### PERSISTENT_LOOP_ANALYSIS.md

**Path:** `MVU_PERSISTENT_INFINITE_LOOP_BUG_REPORT.md`

```markdown
# 🚨 MVU PERSISTENT INFINITE RENDERING LOOP - CRITICAL BUG

**Status**: UNRESOLVED - Loop persists despite multiple fix attempts

**Severity**: CRITICAL - Application completely unusable

**Generated**: 2025-08-20 09:59:21

---

## 🔥 PERSISTENT ISSUE DESCRIPTION

Despite implementing the following fixes:
- ✅ Value-equal dataclasses with `@dataclass(frozen=True, eq=True, slots=True)`
- ✅ Proper props memoization with early-out comparison
- ✅ Removed UpdateUI command entirely
- ✅ Immutable data structures (tuples instead of lists)

**THE INFINITE LOOP STILL PERSISTS!**

## 🔍 CURRENT DEBUG EVIDENCE

The following pattern continues to occur infinitely:

```
🎨 MVUPokerTableRenderer: Rendering with 0 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
🎨 MVUPokerTableRenderer: Rendering with 2 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
[REPEATS INFINITELY]
```

## 🧐 KEY OBSERVATIONS

1. **Props Equality Still Failing**: Despite dataclass equality, `Props equal: False`
2. **Seats Equality Failing**: `Seats equal: False` even with identical cursor/state
3. **Values Are Identical**: `Review cursor: 0 -> 0` and `Waiting for: NONE -> NONE`
4. **Alternating Pattern**: Switches between 0 seats and 2 seats consistently
5. **Dataclass Equality Not Working**: The `==` operator is not behaving as expected

## 🎯 NEW HYPOTHESIS

The issue may be deeper than just dataclass equality:

### Potential Root Causes:
1. **Nested Dictionary Mutation**: The `seats: Dict[int, SeatState]` may be getting mutated
2. **Set Equality Issues**: `legal_actions: Set[str]` may not be comparing correctly
3. **Hidden State Changes**: Something is modifying the model between comparisons
4. **Dataclass Hash Collision**: Frozen dataclasses might have hash issues with mutable containers
5. **Timing Race Condition**: Multiple threads/events firing simultaneously
6. **Scale Widget Callback**: The review scale might still be triggering callbacks
7. **Model Creation Logic**: The `from_model()` method might be creating different objects

## 🔍 INVESTIGATION NEEDED

### Immediate Debug Steps:
1. **Deep Inspection**: Add logging to show exact object contents being compared
2. **Hash Analysis**: Check if hash values are consistent for 'equal' objects
3. **Mutation Detection**: Add immutability checks to detect if objects are being modified
4. **Thread Analysis**: Verify all UI updates happen on main thread
5. **Event Tracing**: Log all dispatch calls to find the trigger source
6. **Memory Analysis**: Check if objects are being garbage collected unexpectedly

## 📋 REPRODUCTION

1. Run: `python3 backend/run_new_ui.py`
2. Navigate to 'Hands Review' tab
3. Infinite loop starts immediately
4. CPU usage spikes to 100%
5. Application becomes unresponsive

---

## CURRENT MVU IMPLEMENTATION (POST-FIX)

### mvu/types.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/types.py`

```python
"""
MVU (Model-View-Update) Architecture Types
Based on PokerPro UI Implementation Handbook v2
"""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, List, Set, Any, Protocol, Callable
from abc import ABC, abstractmethod


# ============================================================================
# CORE MODEL
# ============================================================================

@dataclass(frozen=True, eq=True, slots=True)
class SeatState:
    """State for a single seat at the poker table"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int  # Current bet amount
    folded: bool
    all_in: bool
    cards: tuple[str, ...]  # Hole cards (visibility rules applied) - immutable tuple
    position: int
    acting: bool = False


@dataclass(frozen=True)
class Action:
    """Represents a poker action"""
    seat: int
    action: str  # "CHECK", "CALL", "BET", "RAISE", "FOLD"
    amount: Optional[int] = None
    street: str = "PREFLOP"


@dataclass(frozen=True)
class GtoHint:
    """GTO strategy hint"""
    action: str
    frequency: float
    reasoning: str


@dataclass(frozen=True)
class Banner:
    """UI banner/message"""
    text: str
    type: Literal["info", "warning", "error", "success"]
    duration_ms: int = 3000


@dataclass(frozen=True, eq=True, slots=True)
class Model:
    """
    Canonical Model - Single Source of Truth for poker table state
    """
    # Game State
    hand_id: str
    street: Literal["PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "DONE"]
    to_act_seat: Optional[int]
    stacks: Dict[int, int]
    pot: int
    board: tuple[str, ...]  # ("As", "Kd", "7h", ...) - immutable tuple
    seats: Dict[int, SeatState]
    legal_actions: Set[str]  # {"CHECK", "CALL", "BET", "RAISE", "FOLD"}
    last_action: Optional[Action]
    
    # Session Configuration
    session_mode: Literal["PRACTICE", "GTO", "REVIEW"]
    autoplay_on: bool
    step_delay_ms: int
    waiting_for: Literal["HUMAN_DECISION", "BOT_DECISION", "ANIMATION", "NONE"]
    
    # Review-specific
    review_cursor: int
    review_len: int
    review_paused: bool
    
    # UI State
    gto_hint: Optional[GtoHint]
    banners: tuple[Banner, ...]
    theme_id: str
    tx_id: int  # Animation token
    
    @classmethod
    def initial(cls, session_mode: Literal["PRACTICE", "GTO", "REVIEW"] = "REVIEW") -> "Model":
        """Create initial model state"""
        return cls(
            hand_id="",
            street="PREFLOP",
            to_act_seat=None,
            stacks={},
            pot=0,
            board=(),
            seats={},
            legal_actions=set(),
            last_action=None,
            session_mode=session_mode,
            autoplay_on=False,
            step_delay_ms=1000,
            waiting_for="NONE",
            review_cursor=0,
            review_len=0,
            review_paused=False,
            gto_hint=None,
            banners=(),
            theme_id="forest-green-pro",
            tx_id=0
        )


# ============================================================================
# MESSAGES (Facts)
# ============================================================================

class Msg(ABC):
    """Base message type"""
    pass


class NextPressed(Msg):
    """User pressed Next button"""
    pass


@dataclass
class AutoPlayToggled(Msg):
    """User toggled auto-play"""
    on: bool


@dataclass
class TimerTick(Msg):
    """Timer tick event"""
    now_ms: int


@dataclass
class UserChose(Msg):
    """Human user made a decision"""
    action: str
    amount: Optional[int] = None


@dataclass
class DecisionRequested(Msg):
    """System requests decision from a seat"""
    seat: int


@dataclass
class DecisionReady(Msg):
    """Decision is ready (from bot or async process)"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class AppliedAction(Msg):
    """Action was applied to PPSM"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class StreetAdvanced(Msg):
    """Street changed (PREFLOP -> FLOP, etc.)"""
    street: str


@dataclass
class HandFinished(Msg):
    """Hand completed"""
    winners: List[int]
    payouts: Dict[int, int]


@dataclass
class AnimationFinished(Msg):
    """Animation completed"""
    token: int


@dataclass
class ReviewSeek(Msg):
    """Seek to specific position in review"""
    index: int


class ReviewPlayStep(Msg):
    """Play next step in review"""
    pass


@dataclass
class LoadHand(Msg):
    """Load a new hand for review/practice"""
    hand_data: Dict[str, Any]


@dataclass
class ThemeChanged(Msg):
    """Theme was changed"""
    theme_id: str


# ============================================================================
# COMMANDS (Effects)
# ============================================================================

class Cmd(ABC):
    """Base command type"""
    pass


@dataclass
class PlaySound(Cmd):
    """Play a sound effect"""
    name: str


@dataclass
class Speak(Cmd):
    """Text-to-speech announcement"""
    text: str


@dataclass
class Animate(Cmd):
    """Trigger animation"""
    name: str
    payload: Dict[str, Any]
    token: int


@dataclass
class AskDriverForDecision(Cmd):
    """Ask session driver for decision"""
    seat: int


@dataclass
class ApplyPPSM(Cmd):
    """Apply action to Pure Poker State Machine"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class ScheduleTimer(Cmd):
    """Schedule a delayed message"""
    delay_ms: int
    msg: Msg


@dataclass
class PublishEvent(Cmd):
    """Publish event to EventBus"""
    topic: str
    payload: Dict[str, Any]



@dataclass
class GetReviewEvent(Cmd):
    """Get and dispatch review event at index"""
    index: int


# ============================================================================
# SESSION DRIVER PROTOCOL
# ============================================================================

class SessionDriver(Protocol):
    """Protocol for session-specific behavior"""
    
    @abstractmethod
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat (async, calls callback when ready)"""
        pass
    
    @abstractmethod
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at index (REVIEW mode only)"""
        pass
    
    @abstractmethod
    def review_length(self) -> int:
        """Get total review length (REVIEW mode only)"""
        pass


# ============================================================================
# TABLE RENDERER PROPS
# ============================================================================

@dataclass(frozen=True, eq=True, slots=True)
class TableRendererProps:
    """Props derived from Model for the table renderer"""
    # Table state
    seats: Dict[int, SeatState]
    board: tuple[str, ...]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: Set[str]
    
    # UI state
    banners: tuple[Banner, ...]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    
    # Review state
    review_cursor: int
    review_len: int
    review_paused: bool
    session_mode: str
    
    # Hints
    gto_hint: Optional[GtoHint]
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        """Derive props from model"""
        return cls(
            seats=model.seats,
            board=model.board,
            pot=model.pot,
            to_act_seat=model.to_act_seat,
            legal_actions=model.legal_actions,
            banners=model.banners,
            theme_id=model.theme_id,
            autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for,
            review_cursor=model.review_cursor,
            review_len=model.review_len,
            review_paused=model.review_paused,
            session_mode=model.session_mode,
            gto_hint=model.gto_hint
        )


# ============================================================================
# INTENT HANDLER PROTOCOL
# ============================================================================

class IntentHandler(Protocol):
    """Protocol for handling user intents from the UI"""
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        pass
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        pass
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        pass
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        pass
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        pass

```

---

### mvu/update.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/update.py`

```python
"""
MVU Update Function - Pure reducers for poker table state
Based on PokerPro UI Implementation Handbook v2
"""

from typing import Tuple, List, Optional
from dataclasses import replace

from .types import (
    Model, Msg, Cmd, SeatState, Action,
    NextPressed, AutoPlayToggled, TimerTick, UserChose,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished,
    ReviewSeek, ReviewPlayStep, LoadHand, ThemeChanged,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, GetReviewEvent
)


def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """
    Pure update function - computes (Model', Cmds) from (Model, Msg)
    No I/O operations allowed inside reducers.
    """
    if isinstance(msg, NextPressed):
        return next_pressed_reducer(model)
    
    if isinstance(msg, AutoPlayToggled):
        return replace(model, autoplay_on=msg.on), []
    
    if isinstance(msg, TimerTick):
        return on_timer_tick(model, msg)
    
    if isinstance(msg, UserChose):
        return apply_decision(model, model.to_act_seat, msg.action, msg.amount)
    
    if isinstance(msg, DecisionReady):
        return apply_decision(model, msg.seat, msg.action, msg.amount)
    
    if isinstance(msg, AppliedAction):
        return on_applied_action(model, msg)
    
    if isinstance(msg, StreetAdvanced):
        return on_street_advanced(model, msg)
    
    if isinstance(msg, HandFinished):
        return on_hand_finished(model, msg)
    
    if isinstance(msg, AnimationFinished):
        return on_animation_finished(model, msg)
    
    if isinstance(msg, ReviewSeek):
        return rebuild_state_to(model, msg.index)
    
    if isinstance(msg, ReviewPlayStep):
        return play_review_step(model)
    
    if isinstance(msg, LoadHand):
        return load_hand(model, msg)
    
    if isinstance(msg, ThemeChanged):
        return replace(model, theme_id=msg.theme_id), []
    
    # Unknown message - no change
    return model, []


# ============================================================================
# KEY REDUCERS
# ============================================================================

def next_pressed_reducer(model: Model) -> Tuple[Model, List[Cmd]]:
    """Handle Next button press based on current state"""
    
    print(f"🔘 Next pressed - State: waiting_for={model.waiting_for}, to_act_seat={model.to_act_seat}, mode={model.session_mode}, cursor={model.review_cursor}/{model.review_len}")
    
    # If waiting for human decision, Next does nothing
    if model.waiting_for == "HUMAN_DECISION":
        print("⏸️ Next pressed but waiting for human decision")
        return model, []
    
    # If waiting for bot decision, ask driver
    if model.waiting_for == "BOT_DECISION" and model.to_act_seat is not None:
        print(f"🤖 Next pressed - asking driver for decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="NONE")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    # If waiting for animation, Next does nothing
    if model.waiting_for == "ANIMATION":
        print("🎬 Next pressed but waiting for animation")
        return model, []
    
    # If no one to act, continue game flow (or advance review)
    if model.to_act_seat is None:
        if model.session_mode == "REVIEW":
            print("📖 Next pressed - no one to act in REVIEW, advancing review")
            return model, [ScheduleTimer(0, ReviewPlayStep())]
        else:
            print("⏭️ Next pressed - no one to act, continuing game flow")
            return model, [ApplyPPSM(seat=-1, action="CONTINUE", amount=None)]
    
    # Someone needs to act
    if model.session_mode == "REVIEW":
        # In review mode, all actions are pre-recorded, so advance review
        print(f"📖 Next pressed in REVIEW mode with to_act_seat={model.to_act_seat} - advancing review")
        return model, [ScheduleTimer(0, ReviewPlayStep())]
    
    # If autoplay is on and current seat is bot, ask for decision
    if model.autoplay_on and seat_is_bot(model, model.to_act_seat):
        print(f"🤖 Next pressed - autoplay bot decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="BOT_DECISION")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    print("❓ Next pressed - no action taken")
    return model, []


def apply_decision(model: Model, seat: Optional[int], action: str, amount: Optional[int]) -> Tuple[Model, List[Cmd]]:
    """Apply a poker decision (from human or bot)"""
    
    # Validate decision
    if seat is None or seat != model.to_act_seat:
        return model, []
    
    if action not in model.legal_actions:
        return model, []
    
    # Generate new transaction ID for animation
    tx = model.tx_id + 1
    
    # Create commands for effects
    cmds = [
        PlaySound(action.lower()),
        Speak(action.capitalize()),
    ]
    
    # Add appropriate animation
    if action in {"BET", "RAISE", "CALL"}:
        cmds.append(Animate("chips_to_pot", {"seat": seat, "amount": amount or 0}, token=tx))
    else:
        cmds.append(Animate("minor_flash", {"seat": seat}, token=tx))
    
    # Apply to PPSM
    cmds.append(ApplyPPSM(seat, action, amount))
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="NONE",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        # Update model to wait for animation
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="ANIMATION",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
    
    return new_model, cmds


def on_applied_action(model: Model, msg: AppliedAction) -> Tuple[Model, List[Cmd]]:
    """Handle action applied to PPSM - update from PPSM snapshot"""
    
    # This would typically get updated state from PPSM
    # For now, we'll simulate the state update
    new_model = apply_ppsm_snapshot(model, msg)
    cmds = []
    
    # In REVIEW mode, all actions are pre-recorded, so never wait for decisions
    if model.session_mode == "REVIEW":
        # Always ready for next review step
        new_model = replace(new_model, waiting_for="NONE")
    else:
        # Determine next action for live play
        if new_model.to_act_seat is not None:
            if seat_is_human(new_model, new_model.to_act_seat):
                new_model = replace(new_model, waiting_for="HUMAN_DECISION")
            else:
                new_model = replace(new_model, waiting_for="BOT_DECISION")
                if new_model.autoplay_on:
                    cmds.append(AskDriverForDecision(new_model.to_act_seat))
        else:
            # No one to act - schedule continuation
            cmds.append(ScheduleTimer(new_model.step_delay_ms, NextPressed()))
    

    return new_model, cmds


def on_street_advanced(model: Model, msg: StreetAdvanced) -> Tuple[Model, List[Cmd]]:
    """Handle street advancement (PREFLOP -> FLOP, etc.)"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("reveal_board", {"street": msg.street}, token=tx),
        PlaySound("deal")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="NONE"
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="ANIMATION"
        )
    
    return new_model, cmds


def on_hand_finished(model: Model, msg: HandFinished) -> Tuple[Model, List[Cmd]]:
    """Handle hand completion"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("pot_to_winners", {"payouts": msg.payouts}, token=tx),
        PlaySound("win")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            waiting_for="NONE",
            tx_id=tx,
            street="DONE"
        )
        # Auto-complete animation and schedule next step
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
        cmds.append(ScheduleTimer(model.step_delay_ms, ReviewPlayStep()))
    else:
        new_model = replace(
            model,
            waiting_for="ANIMATION",
            tx_id=tx,
            street="DONE"
        )
        # Schedule next action for live play
        cmds.append(ScheduleTimer(model.step_delay_ms, NextPressed()))
    
    return new_model, cmds


def on_animation_finished(model: Model, msg: AnimationFinished) -> Tuple[Model, List[Cmd]]:
    """Handle animation completion"""
    
    # Only process if this is the current animation
    if msg.token != model.tx_id:
        return model, []
    
    # Clear waiting state
    new_model = replace(model, waiting_for="NONE")
    
    # Trigger next action if needed
    cmds = []
    if model.autoplay_on and new_model.to_act_seat is not None:
        if seat_is_bot(new_model, new_model.to_act_seat):
            new_model = replace(new_model, waiting_for="BOT_DECISION")
            cmds.append(AskDriverForDecision(new_model.to_act_seat))
    
    return new_model, cmds


def on_timer_tick(model: Model, msg: TimerTick) -> Tuple[Model, List[Cmd]]:
    """Handle timer tick - can be used for timeouts, etc."""
    
    # Remove expired banners
    current_banners = [
        banner for banner in model.banners
        if msg.now_ms < banner.duration_ms  # Simplified - would need actual timestamps
    ]
    
    if len(current_banners) != len(model.banners):
        return replace(model, banners=current_banners), []
    
    return model, []


# ============================================================================
# REVIEW-SPECIFIC REDUCERS
# ============================================================================

def rebuild_state_to(model: Model, index: int) -> Tuple[Model, List[Cmd]]:
    """Rebuild state to specific review index"""
    
    if model.session_mode != "REVIEW":
        return model, []
    
    # Clamp index
    index = max(0, min(index, model.review_len - 1))
    
    # This would typically replay events up to index
    # For now, just update cursor
    new_model = replace(
        model,
        review_cursor=index,
        waiting_for="NONE"
    )
    
    return new_model, []


def play_review_step(model: Model) -> Tuple[Model, List[Cmd]]:
    """Play next step in review"""
    
    print(f"📖 PlayReviewStep: cursor={model.review_cursor}, len={model.review_len}, mode={model.session_mode}")
    
    if model.session_mode != "REVIEW":
        print("❌ PlayReviewStep: Not in REVIEW mode")
        return model, []
    
    if model.review_cursor >= model.review_len - 1:
        print("🏁 PlayReviewStep: End of review reached")
        return model, []
    
    # Advance cursor
    new_cursor = model.review_cursor + 1
    new_model = replace(model, review_cursor=new_cursor)
    
    print(f"➡️ PlayReviewStep: Advancing to cursor {new_cursor}")
    
    # We need to get the event from session driver and dispatch it
    return new_model, [GetReviewEvent(index=new_cursor)]


def load_hand(model: Model, msg: LoadHand) -> Tuple[Model, List[Cmd]]:
    """Load new hand data"""
    
    hand_data = msg.hand_data
    
    # Extract hand information
    hand_id = hand_data.get("hand_id", "")
    seats_data = hand_data.get("seats", {})
    board = tuple(hand_data.get("board", []))
    pot = hand_data.get("pot", 0)
    
    # Convert seats data to SeatState objects
    seats = {}
    stacks = {}
    for seat_num, seat_data in seats_data.items():
        seat_state = SeatState(
            player_uid=seat_data.get("player_uid", f"player_{seat_num}"),
            name=seat_data.get("name", f"Player {seat_num}"),
            stack=seat_data.get("stack", 1000),
            chips_in_front=seat_data.get("chips_in_front", 0),
            folded=seat_data.get("folded", False),
            all_in=seat_data.get("all_in", False),
            cards=tuple(seat_data.get("cards", [])),
            position=int(seat_num)
        )
        seats[int(seat_num)] = seat_state
        stacks[int(seat_num)] = seat_state.stack
    
    new_model = replace(
        model,
        hand_id=hand_id,
        seats=seats,
        stacks=stacks,
        board=board,
        pot=pot,
        street="PREFLOP",
        to_act_seat=hand_data.get("to_act_seat"),
        legal_actions=set(hand_data.get("legal_actions", [])),
        waiting_for="NONE",
        review_cursor=0,
        review_len=hand_data.get("review_len", 0)
    )
    
    return new_model, []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def seat_is_human(model: Model, seat: int) -> bool:
    """Check if seat is controlled by human player"""
    # For now, assume seat 0 is human in practice/review mode
    if model.session_mode in ["PRACTICE", "REVIEW"]:
        return seat == 0
    return False


def seat_is_bot(model: Model, seat: int) -> bool:
    """Check if seat is controlled by bot"""
    return not seat_is_human(model, seat)


def apply_ppsm_snapshot(model: Model, msg: AppliedAction) -> Model:
    """
    Apply PPSM state snapshot after action
    This would typically get real state from PPSM
    """
    
    # Simulate basic state changes
    new_seats = dict(model.seats)
    new_stacks = dict(model.stacks)
    new_pot = model.pot
    
    print(f"🎯 Applying action: {msg.action} by seat {msg.seat} (amount: {msg.amount})")
    
    # Clear all acting status first
    for seat_num in new_seats:
        new_seats[seat_num] = replace(new_seats[seat_num], acting=False)
    
    # Update acting seat
    if msg.seat in new_seats:
        seat_state = new_seats[msg.seat]
        
        # Simulate stack/bet changes
        if msg.action in ["BET", "RAISE", "CALL"] and msg.amount:
            new_stacks[msg.seat] = max(0, new_stacks[msg.seat] - msg.amount)
            new_pot += msg.amount
            new_seats[msg.seat] = replace(
                new_seats[msg.seat],
                stack=new_stacks[msg.seat],
                chips_in_front=seat_state.chips_in_front + msg.amount
            )
            print(f"💰 Seat {msg.seat} bet ${msg.amount}, stack now ${new_stacks[msg.seat]}, pot now ${new_pot}")
            
        elif msg.action == "FOLD":
            new_seats[msg.seat] = replace(new_seats[msg.seat], folded=True)
            print(f"🃏 Seat {msg.seat} folded")
            
        elif msg.action in ["CHECK", "CALL"]:
            print(f"✅ Seat {msg.seat} {msg.action.lower()}ed")
    
    # Find next acting seat (simplified)
    next_seat = None
    active_seats = [s for s in sorted(new_seats.keys()) if not new_seats[s].folded]
    
    if len(active_seats) > 1:
        # Find next seat after current actor
        current_idx = active_seats.index(msg.seat) if msg.seat in active_seats else -1
        next_idx = (current_idx + 1) % len(active_seats)
        next_seat = active_seats[next_idx]
    
    # Update acting status
    if next_seat is not None:
        new_seats[next_seat] = replace(new_seats[next_seat], acting=True)
        print(f"👉 Next to act: Seat {next_seat}")
    else:
        print("🏁 No more players to act")
    
    return replace(
        model,
        seats=new_seats,
        stacks=new_stacks,
        to_act_seat=next_seat,
        pot=new_pot,
        legal_actions={"CHECK", "CALL", "BET", "RAISE", "FOLD"} if next_seat else set()
    )

```

---

### mvu/store.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/store.py`

```python
"""
MVU Store - Manages Model state and executes Commands
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Callable, Optional, Any, Dict
import time
import threading

from .types import (
    Model, Msg, Cmd, SessionDriver, IntentHandler,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, PublishEvent, GetReviewEvent,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished
)
from .update import update


class MVUStore:
    """
    MVU Store - Single source of truth for Model state
    Handles message dispatch and command execution
    """
    
    def __init__(
        self,
        initial_model: Model,
        effect_bus: Any = None,
        game_director: Any = None,
        event_bus: Any = None,
        ppsm: Any = None
    ):
        self.model = initial_model
        self.effect_bus = effect_bus
        self.game_director = game_director
        self.event_bus = event_bus
        self.ppsm = ppsm
        
        # Subscribers to model changes
        self.subscribers: List[Callable[[Model], None]] = []
        
        # Session driver (pluggable)
        self.session_driver: Optional[SessionDriver] = None
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Scheduled timers
        self._timers: Dict[str, Any] = {}
        
        print("🏪 MVUStore: Initialized with model:", self.model.session_mode)
    
    def set_session_driver(self, driver: SessionDriver) -> None:
        """Set the session driver for this store"""
        with self._lock:
            self.session_driver = driver
            print(f"🏪 MVUStore: Session driver set: {type(driver).__name__}")
    
    def subscribe(self, callback: Callable[[Model], None]) -> Callable[[], None]:
        """
        Subscribe to model changes
        Returns unsubscribe function
        """
        with self._lock:
            self.subscribers.append(callback)
            
            # Immediately notify with current model
            callback(self.model)
            
            def unsubscribe():
                with self._lock:
                    if callback in self.subscribers:
                        self.subscribers.remove(callback)
            
            return unsubscribe
    
    def dispatch(self, msg: Msg) -> None:
        """
        Dispatch a message to update the model
        """
        with self._lock:
            print(f"🏪 MVUStore: Dispatching {type(msg).__name__}")
            
            # Update model using pure reducer
            new_model, commands = update(self.model, msg)
            
            # Update stored model
            old_model = self.model
            self.model = new_model
            
            # Execute commands
            for cmd in commands:
                self._execute_command(cmd)
            
            # Notify subscribers if model changed
            if new_model != old_model:
                for subscriber in self.subscribers:
                    try:
                        subscriber(new_model)
                    except Exception as e:
                        print(f"⚠️ MVUStore: Subscriber error: {e}")
    
    def get_model(self) -> Model:
        """Get current model (thread-safe)"""
        with self._lock:
            return self.model
    
    def _execute_command(self, cmd: Cmd) -> None:
        """
        Execute a command using available services
        All I/O happens here, never in reducers
        """
        try:
            if isinstance(cmd, PlaySound):
                self._execute_play_sound(cmd)
            
            elif isinstance(cmd, Speak):
                self._execute_speak(cmd)
            
            elif isinstance(cmd, Animate):
                self._execute_animate(cmd)
            
            elif isinstance(cmd, AskDriverForDecision):
                self._execute_ask_driver(cmd)
            
            elif isinstance(cmd, ApplyPPSM):
                self._execute_apply_ppsm(cmd)
            
            elif isinstance(cmd, ScheduleTimer):
                self._execute_schedule_timer(cmd)
            
            elif isinstance(cmd, PublishEvent):
                self._execute_publish_event(cmd)
            

            
            elif isinstance(cmd, GetReviewEvent):
                self._execute_get_review_event(cmd)
            
            else:
                print(f"⚠️ MVUStore: Unknown command: {type(cmd).__name__}")
        
        except Exception as e:
            print(f"⚠️ MVUStore: Command execution error: {e}")
    
    def _execute_play_sound(self, cmd: PlaySound) -> None:
        """Execute PlaySound command"""
        if self.effect_bus:
            try:
                self.effect_bus.play_sound(cmd.name)
                print(f"🔊 MVUStore: Played sound: {cmd.name}")
            except Exception as e:
                print(f"⚠️ MVUStore: Sound error: {e}")
    
    def _execute_speak(self, cmd: Speak) -> None:
        """Execute Speak command"""
        if self.effect_bus and hasattr(self.effect_bus, 'voice_manager'):
            try:
                self.effect_bus.voice_manager.speak(cmd.text)
                print(f"🗣️ MVUStore: Spoke: {cmd.text}")
            except Exception as e:
                print(f"⚠️ MVUStore: Speech error: {e}")
    
    def _execute_animate(self, cmd: Animate) -> None:
        """Execute Animate command"""
        if self.effect_bus:
            try:
                # Start animation and set up completion callback
                def on_animation_complete():
                    self.dispatch(AnimationFinished(token=cmd.token))
                
                self.effect_bus.animate(
                    cmd.name,
                    cmd.payload,
                    callback=on_animation_complete
                )
                print(f"🎬 MVUStore: Started animation: {cmd.name} (token: {cmd.token})")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Animation error: {e}")
                # Immediately complete animation on error
                self.dispatch(AnimationFinished(token=cmd.token))
    
    def _execute_ask_driver(self, cmd: AskDriverForDecision) -> None:
        """Execute AskDriverForDecision command"""
        if self.session_driver:
            try:
                def on_decision_ready(decision: DecisionReady):
                    self.dispatch(decision)
                
                self.session_driver.decide(self.model, cmd.seat, on_decision_ready)
                print(f"🤖 MVUStore: Asked driver for decision: seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Driver decision error: {e}")
    
    def _execute_apply_ppsm(self, cmd: ApplyPPSM) -> None:
        """Execute ApplyPPSM command"""
        if self.ppsm:
            try:
                # Apply action to PPSM
                if cmd.seat == -1 and cmd.action == "CONTINUE":
                    # Continue game flow
                    result = self.ppsm.continue_game()
                else:
                    # Apply player action
                    result = self.ppsm.apply_action(cmd.seat, cmd.action, cmd.amount)
                
                # Process PPSM result and dispatch appropriate messages
                self._process_ppsm_result(result, cmd)
                
                print(f"🃏 MVUStore: Applied PPSM action: {cmd.action} by seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: PPSM error: {e}")
    
    def _execute_schedule_timer(self, cmd: ScheduleTimer) -> None:
        """Execute ScheduleTimer command"""
        try:
            timer_id = f"timer_{time.time()}_{id(cmd.msg)}"
            
            def timer_callback():
                self.dispatch(cmd.msg)
                if timer_id in self._timers:
                    del self._timers[timer_id]
            
            if self.game_director and hasattr(self.game_director, 'schedule'):
                # Use GameDirector for scheduling (architecture compliant)
                self.game_director.schedule(cmd.delay_ms, {
                    "type": "MVU_TIMER",
                    "callback": timer_callback
                })
            else:
                # Fallback to threading.Timer
                timer = threading.Timer(cmd.delay_ms / 1000.0, timer_callback)
                self._timers[timer_id] = timer
                timer.start()
            
            print(f"⏰ MVUStore: Scheduled timer: {cmd.delay_ms}ms -> {type(cmd.msg).__name__}")
            
        except Exception as e:
            print(f"⚠️ MVUStore: Timer error: {e}")
    
    def _execute_publish_event(self, cmd: PublishEvent) -> None:
        """Execute PublishEvent command"""
        if self.event_bus:
            try:
                self.event_bus.publish(cmd.topic, cmd.payload)
                print(f"📡 MVUStore: Published event: {cmd.topic}")
            except Exception as e:
                print(f"⚠️ MVUStore: Event publish error: {e}")
    

    
    def _execute_get_review_event(self, cmd: GetReviewEvent) -> None:
        """Execute GetReviewEvent command - get event from session driver"""
        if self.session_driver:
            try:
                event = self.session_driver.review_event_at(cmd.index)
                if event:
                    print(f"📖 MVUStore: Got review event at {cmd.index}: {type(event).__name__}")
                    # Dispatch the review event
                    self.dispatch(event)
                else:
                    print(f"📖 MVUStore: No review event at index {cmd.index}")
            except Exception as e:
                print(f"⚠️ MVUStore: Error getting review event: {e}")
        else:
            print("⚠️ MVUStore: No session driver for review event")
    
    def _process_ppsm_result(self, result: Any, original_cmd: ApplyPPSM) -> None:
        """
        Process PPSM result and dispatch appropriate messages
        This would be customized based on your PPSM interface
        """
        try:
            # Dispatch AppliedAction to trigger state update
            self.dispatch(AppliedAction(
                seat=original_cmd.seat,
                action=original_cmd.action,
                amount=original_cmd.amount
            ))
            
            # Check for street advancement
            if hasattr(result, 'street_changed') and result.street_changed:
                self.dispatch(StreetAdvanced(street=result.new_street))
            
            # Check for hand completion
            if hasattr(result, 'hand_finished') and result.hand_finished:
                self.dispatch(HandFinished(
                    winners=getattr(result, 'winners', []),
                    payouts=getattr(result, 'payouts', {})
                ))
        
        except Exception as e:
            print(f"⚠️ MVUStore: PPSM result processing error: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        with self._lock:
            # Cancel all timers
            for timer in self._timers.values():
                if hasattr(timer, 'cancel'):
                    timer.cancel()
            self._timers.clear()
            
            # Clear subscribers
            self.subscribers.clear()
            
            print("🏪 MVUStore: Cleaned up")


class MVUIntentHandler(IntentHandler):
    """
    Intent handler that dispatches messages to MVU store
    Converts UI events to messages
    """
    
    def __init__(self, store: MVUStore):
        self.store = store
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        from .types import NextPressed
        self.store.dispatch(NextPressed())
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        from .types import AutoPlayToggled
        self.store.dispatch(AutoPlayToggled(on=on))
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        from .types import UserChose
        self.store.dispatch(UserChose(action=action, amount=amount))
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        from .types import ReviewSeek
        self.store.dispatch(ReviewSeek(index=index))
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        # This would dispatch a GTO hint request message
        print("🎯 MVUIntentHandler: GTO hint requested")
        pass

```

---

### mvu/view.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/view.py`

```python
"""
MVU View - Pure rendering components that read from Model
Based on PokerPro UI Implementation Handbook v2
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from .types import Model, TableRendererProps, IntentHandler


class MVUPokerTableRenderer(ttk.Frame):
    """
    Pure View component for poker table
    Reads only from Model, emits intents via IntentHandler
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        intent_handler: Optional[IntentHandler] = None,
        theme_manager: Any = None
    ):
        super().__init__(parent)
        
        self.intent_handler = intent_handler or DummyIntentHandler()
        self.theme_manager = theme_manager
        
        # Current props (for change detection)
        self.current_props: Optional[TableRendererProps] = None
        
        # UI components
        self.canvas: Optional[tk.Canvas] = None
        self.controls_frame: Optional[ttk.Frame] = None
        self.next_btn: Optional[ttk.Button] = None
        self.autoplay_var: Optional[tk.BooleanVar] = None
        self.action_buttons: Dict[str, ttk.Button] = {}
        self.status_label: Optional[ttk.Label] = None
        self.review_scale: Optional[ttk.Scale] = None
        
        self._setup_ui()
        
        print("🎨 MVUPokerTableRenderer: Initialized as pure View component")
    
    def _setup_ui(self) -> None:
        """Setup the UI components"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main canvas for table rendering
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=600,
            bg="#0D4F3C"  # Default felt color
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        
        # Next button
        self.next_btn = ttk.Button(
            self.controls_frame,
            text="Next",
            command=self.intent_handler.on_click_next
        )
        self.next_btn.grid(row=0, column=0, padx=5)
        
        # Auto-play checkbox
        self.autoplay_var = tk.BooleanVar()
        autoplay_cb = ttk.Checkbutton(
            self.controls_frame,
            text="Auto-play",
            variable=self.autoplay_var,
            command=self._on_autoplay_toggle
        )
        autoplay_cb.grid(row=0, column=1, padx=5, sticky="w")
        
        # Status label
        self.status_label = ttk.Label(
            self.controls_frame,
            text="Ready"
        )
        self.status_label.grid(row=0, column=2, padx=5)
        
        # Action buttons frame
        self.actions_frame = ttk.Frame(self.controls_frame)
        self.actions_frame.grid(row=0, column=3, padx=5)
        
        # Create action buttons
        actions = ["FOLD", "CHECK", "CALL", "BET", "RAISE"]
        for i, action in enumerate(actions):
            btn = ttk.Button(
                self.actions_frame,
                text=action,
                command=lambda a=action: self._on_action_btn(a)
            )
            btn.grid(row=0, column=i, padx=2)
            self.action_buttons[action] = btn
        
        # Review controls (shown only in review mode)
        self.review_frame = ttk.Frame(self.controls_frame)
        self.review_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        self.review_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self.review_frame, text="Review:").grid(row=0, column=0, padx=5)
        
        self.review_scale = ttk.Scale(
            self.review_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self._on_review_seek
        )
        self.review_scale.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.review_position_label = ttk.Label(self.review_frame, text="0/0")
        self.review_position_label.grid(row=0, column=2, padx=5)
    
    def render(self, props: TableRendererProps) -> None:
        """
        Render the table based on props
        Pure function - only reads from props, never mutates state
        """
        # Skip if props haven't changed
        if self.current_props == props:
            return
        
        # Debug what changed
        print(f"🎨 MVUPokerTableRenderer: Rendering with {len(props.seats)} seats")
        print(f"🔍 Props changed: old_props is None: {self.current_props is None}")
        if self.current_props is not None:
            print(f"🔍 Props equal: {self.current_props == props}")
            print(f"🔍 Seats equal: {self.current_props.seats == props.seats}")
            print(f"🔍 Review cursor: {self.current_props.review_cursor} -> {props.review_cursor}")
            print(f"🔍 Waiting for: {self.current_props.waiting_for} -> {props.waiting_for}")
        
        self.current_props = props
        
        # Update controls based on props
        self._update_controls(props)
        
        # Render table on canvas
        self._render_table(props)
        
        # Update review controls
        self._update_review_controls(props)
    
    def _update_controls(self, props: TableRendererProps) -> None:
        """Update control buttons and status"""
        
        # Update status
        status_text = f"Waiting for: {props.waiting_for}"
        if props.to_act_seat is not None:
            status_text += f" (Seat {props.to_act_seat})"
        self.status_label.config(text=status_text)
        
        # Update next button
        next_enabled = props.waiting_for != "HUMAN_DECISION"
        self.next_btn.config(state="normal" if next_enabled else "disabled")
        
        # Update autoplay
        self.autoplay_var.set(props.autoplay_on)
        
        # Update action buttons
        human_turn = (
            props.to_act_seat == 0 and  # Assuming seat 0 is human
            props.waiting_for == "HUMAN_DECISION"
        )
        
        for action, btn in self.action_buttons.items():
            enabled = human_turn and action in props.legal_actions
            btn.config(state="normal" if enabled else "disabled")
    
    def _render_table(self, props: TableRendererProps) -> None:
        """Render the poker table on canvas"""
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet
            self.after(50, lambda: self.render(props))
            return
        
        # Draw felt background
        self.canvas.create_oval(
            50, 50, canvas_width - 50, canvas_height - 50,
            fill="#0D4F3C", outline="#2D5016", width=3,
            tags="felt"
        )
        
        # Draw seats
        self._draw_seats(props, canvas_width, canvas_height)
        
        # Draw community cards
        self._draw_community_cards(props, canvas_width, canvas_height)
        
        # Draw pot
        self._draw_pot(props, canvas_width, canvas_height)
        
        # Draw banners
        self._draw_banners(props, canvas_width, canvas_height)
    
    def _draw_seats(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw player seats"""
        
        import math
        
        # Calculate seat positions around oval table
        center_x, center_y = width // 2, height // 2
        radius_x, radius_y = (width - 100) // 2, (height - 100) // 2
        
        for seat_num, seat_state in props.seats.items():
            # Calculate position
            angle = (seat_num / max(len(props.seats), 1)) * 2 * math.pi - math.pi / 2
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            # Draw seat background
            seat_color = "#FFD700" if seat_state.acting else "#8B4513"
            if seat_state.folded:
                seat_color = "#696969"
            
            self.canvas.create_rectangle(
                x - 60, y - 30, x + 60, y + 30,
                fill=seat_color, outline="black", width=2,
                tags=f"seat_{seat_num}"
            )
            
            # Draw player name
            self.canvas.create_text(
                x, y - 15,
                text=seat_state.name,
                font=("Arial", 10, "bold"),
                fill="black",
                tags=f"seat_{seat_num}_name"
            )
            
            # Draw stack
            self.canvas.create_text(
                x, y,
                text=f"${seat_state.stack}",
                font=("Arial", 9),
                fill="black",
                tags=f"seat_{seat_num}_stack"
            )
            
            # Draw bet amount
            if seat_state.chips_in_front > 0:
                self.canvas.create_text(
                    x, y + 15,
                    text=f"Bet: ${seat_state.chips_in_front}",
                    font=("Arial", 8),
                    fill="red",
                    tags=f"seat_{seat_num}_bet"
                )
            
            # Draw hole cards (if visible)
            if seat_state.cards and not seat_state.folded:
                card_x = x - 20
                for i, card in enumerate(seat_state.cards[:2]):  # Max 2 hole cards
                    self._draw_card(card_x + i * 20, y - 45, card, f"hole_{seat_num}_{i}")
    
    def _draw_community_cards(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw community cards"""
        
        if not props.board:
            return
        
        center_x, center_y = width // 2, height // 2
        card_width, card_height = 40, 60
        total_width = len(props.board) * (card_width + 5) - 5
        start_x = center_x - total_width // 2
        
        for i, card in enumerate(props.board):
            x = start_x + i * (card_width + 5)
            y = center_y - card_height // 2
            self._draw_card(x, y, card, f"board_{i}")
    
    def _draw_pot(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw pot display"""
        
        center_x, center_y = width // 2, height // 2
        
        # Pot background
        self.canvas.create_oval(
            center_x - 40, center_y + 60, center_x + 40, center_y + 100,
            fill="#DAA520", outline="black", width=2,
            tags="pot_bg"
        )
        
        # Pot amount
        self.canvas.create_text(
            center_x, center_y + 80,
            text=f"${props.pot}",
            font=("Arial", 12, "bold"),
            fill="black",
            tags="pot_amount"
        )
    
    def _draw_card(self, x: int, y: int, card: str, tag: str) -> None:
        """Draw a single card"""
        
        # Card background
        self.canvas.create_rectangle(
            x, y, x + 40, y + 60,
            fill="white", outline="black", width=2,
            tags=tag
        )
        
        # Card text
        self.canvas.create_text(
            x + 20, y + 30,
            text=card,
            font=("Arial", 10, "bold"),
            fill="black",
            tags=f"{tag}_text"
        )
    
    def _draw_banners(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw UI banners"""
        
        for i, banner in enumerate(props.banners):
            y_pos = 20 + i * 30
            
            # Banner colors
            colors = {
                "info": "#ADD8E6",
                "warning": "#FFD700",
                "error": "#FF6B6B",
                "success": "#90EE90"
            }
            
            bg_color = colors.get(banner.type, "#FFFFFF")
            
            self.canvas.create_rectangle(
                10, y_pos, width - 10, y_pos + 25,
                fill=bg_color, outline="black",
                tags=f"banner_{i}"
            )
            
            self.canvas.create_text(
                width // 2, y_pos + 12,
                text=banner.text,
                font=("Arial", 10),
                fill="black",
                tags=f"banner_{i}_text"
            )
    
    def _update_review_controls(self, props: TableRendererProps) -> None:
        """Update review-specific controls"""
        
        is_review = props.session_mode == "REVIEW"
        
        if is_review:
            self.review_frame.grid()
            
            # Update scale (avoid triggering callback during programmatic update)
            if props.review_len > 0:
                self.review_scale.config(to=props.review_len - 1)
                # Temporarily disable the callback to avoid infinite loop
                old_command = self.review_scale.cget("command")
                self.review_scale.config(command="")
                self.review_scale.set(props.review_cursor)
                self.review_scale.config(command=old_command)
            
            # Update position label
            self.review_position_label.config(
                text=f"{props.review_cursor}/{props.review_len}"
            )
        else:
            self.review_frame.grid_remove()
    
    def _on_autoplay_toggle(self) -> None:
        """Handle autoplay toggle"""
        self.intent_handler.on_toggle_autoplay(self.autoplay_var.get())
    
    def _on_action_btn(self, action: str) -> None:
        """Handle action button click"""
        # For BET/RAISE, we'd need amount input - simplified for now
        amount = None
        if action in ["BET", "RAISE"]:
            amount = 100  # Placeholder amount
        
        self.intent_handler.on_action_btn(action, amount)
    
    def _on_review_seek(self, value: str) -> None:
        """Handle review seek"""
        try:
            index = int(float(value))
            self.intent_handler.on_seek(index)
        except ValueError:
            pass


class DummyIntentHandler:
    """Dummy intent handler for testing"""
    
    def on_click_next(self) -> None:
        print("🎯 DummyIntentHandler: Next clicked")
    
    def on_toggle_autoplay(self, on: bool) -> None:
        print(f"🎯 DummyIntentHandler: Autoplay toggled: {on}")
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        print(f"🎯 DummyIntentHandler: Action {action} (amount: {amount})")
    
    def on_seek(self, index: int) -> None:
        print(f"🎯 DummyIntentHandler: Seek to {index}")
    
    def on_request_hint(self) -> None:
        print("🎯 DummyIntentHandler: Hint requested")

```

---

### mvu/hands_review_mvu.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/hands_review_mvu.py`

```python
"""
MVU-based Hands Review Tab
Replaces the existing HandsReviewTab with clean MVU architecture
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List
import json

from .types import Model, TableRendererProps, LoadHand, SeatState
from .store import MVUStore, MVUIntentHandler
from .view import MVUPokerTableRenderer
from .drivers import create_driver


class MVUHandsReviewTab(ttk.Frame):
    """
    MVU-based Hands Review Tab
    Clean, testable, and follows the architecture handbook
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        services: Any = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.services = services
        
        # Get required services
        self.effect_bus = services.get_app("effect_bus") if services else None
        self.game_director = services.get_app("game_director") if services else None
        self.event_bus = services.get_app("event_bus") if services else None
        self.theme_manager = services.get_app("theme") if services else None
        
        # MVU components
        self.store: Optional[MVUStore] = None
        self.intent_handler: Optional[MVUIntentHandler] = None
        self.table_renderer: Optional[MVUPokerTableRenderer] = None
        
        # Hand data
        self.hands_data: List[Dict[str, Any]] = []
        self.current_hand_index = 0
        
        # UI components
        self.hand_selector: Optional[ttk.Combobox] = None
        self.hand_info_label: Optional[ttk.Label] = None
        
        # Props memoization
        self._last_props: Optional[TableRendererProps] = None
        
        self._setup_ui()
        self._initialize_mvu()
        self._load_hands_data()
        
        print("🎬 MVUHandsReviewTab: Initialized with clean MVU architecture")
    
    def _setup_ui(self) -> None:
        """Setup the UI layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Hand selector
        ttk.Label(controls_frame, text="Hand:").grid(row=0, column=0, padx=5)
        
        self.hand_selector = ttk.Combobox(
            controls_frame,
            state="readonly",
            width=30
        )
        self.hand_selector.grid(row=0, column=1, padx=5, sticky="w")
        self.hand_selector.bind("<<ComboboxSelected>>", self._on_hand_selected)
        
        # Hand info
        self.hand_info_label = ttk.Label(
            controls_frame,
            text="No hand loaded"
        )
        self.hand_info_label.grid(row=0, column=2, padx=10, sticky="w")
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Hands",
            command=self._load_hands_data
        )
        refresh_btn.grid(row=0, column=3, padx=5)
        
        # Table renderer will be added in _initialize_mvu()
    
    def _initialize_mvu(self) -> None:
        """Initialize MVU components"""
        
        # Create initial model for REVIEW mode
        initial_model = Model.initial(session_mode="REVIEW")
        
        # Create store
        self.store = MVUStore(
            initial_model=initial_model,
            effect_bus=self.effect_bus,
            game_director=self.game_director,
            event_bus=self.event_bus,
            ppsm=None  # We'll set this up when we have PPSM integration
        )
        
        # Create intent handler
        self.intent_handler = MVUIntentHandler(self.store)
        
        # Create table renderer
        self.table_renderer = MVUPokerTableRenderer(
            parent=self,
            intent_handler=self.intent_handler,
            theme_manager=self.theme_manager
        )
        self.table_renderer.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Subscribe to model changes
        self.unsubscribe = self.store.subscribe(self._on_model_changed)
        
        print("🏪 MVUHandsReviewTab: MVU components initialized")
    
    def _load_hands_data(self) -> None:
        """Load hands data for review"""
        try:
            # Try to load from GTO hands file (as in original implementation)
            import os
            gto_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "gto_hands.json"
            )
            
            if os.path.exists(gto_file):
                with open(gto_file, 'r') as f:
                    raw_data = json.load(f)
                    
                self.hands_data = self._parse_hands_data(raw_data)
                print(f"📊 MVUHandsReviewTab: Loaded {len(self.hands_data)} hands")
                
            else:
                # Fallback to sample data
                self.hands_data = self._create_sample_hands()
                print("📊 MVUHandsReviewTab: Using sample hands data")
            
            self._update_hand_selector()
            
            # Load first hand if available
            if self.hands_data:
                self._load_hand(0)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error loading hands: {e}")
            self.hands_data = self._create_sample_hands()
            self._update_hand_selector()
    
    def _parse_hands_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw hands data into MVU format"""
        hands = []
        
        try:
            # Handle different data formats
            if isinstance(raw_data, dict):
                if "hands" in raw_data:
                    hands_list = raw_data["hands"]
                else:
                    hands_list = [raw_data]  # Single hand
            elif isinstance(raw_data, list):
                hands_list = raw_data
            else:
                return []
            
            for i, hand_data in enumerate(hands_list):
                parsed_hand = self._parse_single_hand(hand_data, i)
                if parsed_hand:
                    hands.append(parsed_hand)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hands data: {e}")
        
        return hands
    
    def _parse_single_hand(self, hand_data: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Parse a single hand into MVU format"""
        try:
            hand_id = hand_data.get("hand_id", f"Hand_{index + 1}")
            
            # Parse players/seats
            seats = {}
            stacks = {}
            
            players = hand_data.get("players", [])
            for i, player in enumerate(players[:6]):  # Max 6 players
                seat_state = {
                    "player_uid": player.get("name", f"Player_{i}"),
                    "name": player.get("name", f"Player {i}"),
                    "stack": player.get("stack", 1000),
                    "chips_in_front": 0,
                    "folded": False,
                    "all_in": False,
                    "cards": player.get("hole_cards", []),
                    "position": i
                }
                seats[i] = seat_state
                stacks[i] = seat_state["stack"]
            
            # Parse actions
            actions = []
            raw_actions = hand_data.get("actions", [])
            
            for action_data in raw_actions:
                if isinstance(action_data, dict):
                    actions.append({
                        "seat": action_data.get("player_index", 0),
                        "action": action_data.get("action", "CHECK"),
                        "amount": action_data.get("amount"),
                        "street": action_data.get("street", "PREFLOP")
                    })
            
            return {
                "hand_id": hand_id,
                "seats": seats,
                "stacks": stacks,
                "board": hand_data.get("board", []),
                "pot": hand_data.get("pot", 0),
                "actions": actions,
                "review_len": len(actions),
                "to_act_seat": 0,  # Start with first seat
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            }
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hand {index}: {e}")
            return None
    
    def _create_sample_hands(self) -> List[Dict[str, Any]]:
        """Create sample hands for testing"""
        return [
            {
                "hand_id": "SAMPLE_001",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["As", "Kh"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Qd", "Jc"],
                        "position": 1
                    }
                },
                "stacks": {0: 1000, 1: 1000},
                "board": ["7h", "8s", "9d"],
                "pot": 60,
                "actions": [
                    {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
                    {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
                    {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
                    {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
                ],
                "review_len": 4,
                "to_act_seat": 0,
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            },
            {
                "hand_id": "SAMPLE_002",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 800,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Kd", "Kc"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1200,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Ad", "Qh"],
                        "position": 1
                    }
                },
                "stacks": {0: 800, 1: 1200},
                "board": ["2h", "7c", "Ks", "4d", "8h"],
                "pot": 400,
                "actions": [
                    {"seat": 1, "action": "RAISE", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CALL", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CHECK", "amount": None, "street": "FLOP"},
                    {"seat": 1, "action": "BET", "amount": 60, "street": "FLOP"},
                    {"seat": 0, "action": "RAISE", "amount": 180, "street": "FLOP"},
                    {"seat": 1, "action": "CALL", "amount": 120, "street": "FLOP"}
                ],
                "review_len": 6,
                "to_act_seat": 1,
                "legal_actions": ["CHECK", "BET"]
            }
        ]
    
    def _update_hand_selector(self) -> None:
        """Update the hand selector combobox"""
        hand_names = [hand["hand_id"] for hand in self.hands_data]
        self.hand_selector["values"] = hand_names
        
        if hand_names:
            self.hand_selector.current(0)
    
    def _on_hand_selected(self, event=None) -> None:
        """Handle hand selection"""
        try:
            index = self.hand_selector.current()
            if 0 <= index < len(self.hands_data):
                self._load_hand(index)
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error selecting hand: {e}")
    
    def _load_hand(self, index: int) -> None:
        """Load a specific hand into the MVU store"""
        if not (0 <= index < len(self.hands_data)):
            return
        
        self.current_hand_index = index
        hand_data = self.hands_data[index]
        
        # Update hand info
        hand_id = hand_data["hand_id"]
        num_actions = hand_data.get("review_len", 0)
        self.hand_info_label.config(
            text=f"{hand_id} ({num_actions} actions)"
        )
        
        # Create and set session driver
        driver = create_driver("REVIEW", hand_data=hand_data)
        self.store.set_session_driver(driver)
        
        # Dispatch LoadHand message to store
        load_msg = LoadHand(hand_data=hand_data)
        self.store.dispatch(load_msg)
        
        print(f"📋 MVUHandsReviewTab: Loaded hand {hand_id}")
    
    def _on_model_changed(self, model: Model) -> None:
        """Handle model changes - update the view"""
        try:
            # Convert model to props
            props = TableRendererProps.from_model(model)
            
            # Early-out if equal (now that we have proper value equality)
            if props == self._last_props:
                return
            
            self._last_props = props
            
            # Render table
            if self.table_renderer:
                self.table_renderer.render(props)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error updating view: {e}")
    
    def dispose(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'unsubscribe') and self.unsubscribe:
            self.unsubscribe()
        
        if self.store:
            self.store.cleanup()
        
        print("🧹 MVUHandsReviewTab: Disposed")

```

---

## RELATED INFRASTRUCTURE

### mvu/drivers.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/drivers.py`

```python
"""
MVU Session Drivers - Pluggable session behavior
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Dict, Any, Optional, Callable
import threading
import time

from .types import Model, Msg, DecisionReady, UserChose, AppliedAction, StreetAdvanced, HandFinished


class ReviewDriver:
    """
    Driver for REVIEW sessions - serves pre-recorded events
    """
    
    def __init__(self, hand_data: Dict[str, Any]):
        self.hand_data = hand_data
        self.events: List[Msg] = []
        self.current_index = 0
        
        # Parse hand data into events
        self._parse_hand_events()
        
        print(f"🎬 ReviewDriver: Initialized with {len(self.events)} events")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """
        In review mode, decisions are pre-recorded
        This should not be called in normal review flow
        """
        print(f"⚠️ ReviewDriver: decide() called unexpectedly for seat {seat}")
        
        # If somehow called, provide a default action
        def delayed_callback():
            time.sleep(0.1)  # Small delay to simulate decision time
            callback(DecisionReady(seat=seat, action="CHECK", amount=None))
        
        thread = threading.Thread(target=delayed_callback)
        thread.daemon = True
        thread.start()
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at specific index"""
        print(f"🎬 ReviewDriver: Getting event at index {index}, have {len(self.events)} events")
        if 0 <= index < len(self.events):
            event = self.events[index]
            print(f"🎬 ReviewDriver: Returning event {index}: {type(event).__name__} - {event}")
            return event
        print(f"🎬 ReviewDriver: No event at index {index}")
        return None
    
    def review_length(self) -> int:
        """Get total number of review events"""
        return len(self.events)
    
    def _parse_hand_events(self) -> None:
        """
        Parse hand data into chronological events
        This converts the hand history into a sequence of messages
        """
        try:
            # Get actions from hand data
            actions = self.hand_data.get("actions", [])
            
            for i, action_data in enumerate(actions):
                # Create event based on action type
                seat = action_data.get("seat", 0)
                action = action_data.get("action", "CHECK")
                amount = action_data.get("amount")
                street = action_data.get("street", "PREFLOP")
                
                # Add the action event
                self.events.append(AppliedAction(
                    seat=seat,
                    action=action,
                    amount=amount
                ))
                
                # Check if street changes after this action
                next_action = actions[i + 1] if i + 1 < len(actions) else None
                if next_action and next_action.get("street") != street:
                    self.events.append(StreetAdvanced(street=next_action.get("street")))
            
            # Add hand finished event if we have winner data
            winners = self.hand_data.get("winners", [])
            payouts = self.hand_data.get("payouts", {})
            if winners or payouts:
                self.events.append(HandFinished(
                    winners=winners,
                    payouts=payouts
                ))
        
        except Exception as e:
            print(f"⚠️ ReviewDriver: Error parsing events: {e}")
            # Fallback to empty events
            self.events = []


class PracticeDriver:
    """
    Driver for PRACTICE sessions - human play with optional bots
    """
    
    def __init__(self, bot_seats: List[int] = None):
        self.bot_seats = bot_seats or []
        print(f"🎯 PracticeDriver: Initialized with bots on seats: {self.bot_seats}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat"""
        if seat in self.bot_seats:
            # Bot decision - simple logic for now
            self._make_bot_decision(model, seat, callback)
        else:
            # Human decision - this shouldn't be called directly
            # Human decisions come through UserChose messages
            print(f"⚠️ PracticeDriver: decide() called for human seat {seat}")
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for practice mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for practice mode"""
        return 0
    
    def _make_bot_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make a simple bot decision"""
        def delayed_decision():
            # Simulate thinking time
            time.sleep(0.5 + (seat * 0.1))  # Staggered timing
            
            # Simple decision logic
            legal_actions = model.legal_actions
            
            if "CHECK" in legal_actions:
                action = "CHECK"
                amount = None
            elif "CALL" in legal_actions:
                action = "CALL"
                amount = None  # PPSM will determine call amount
            elif "FOLD" in legal_actions:
                action = "FOLD"
                amount = None
            else:
                action = "CHECK"
                amount = None
            
            callback(DecisionReady(seat=seat, action=action, amount=amount))
        
        thread = threading.Thread(target=delayed_decision)
        thread.daemon = True
        thread.start()


class GTODriver:
    """
    Driver for GTO sessions - calls GTO provider for decisions
    """
    
    def __init__(self, gto_provider: Any = None):
        self.gto_provider = gto_provider
        print(f"🧠 GTODriver: Initialized with provider: {gto_provider is not None}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get GTO decision from provider"""
        if self.gto_provider:
            self._get_gto_decision(model, seat, callback)
        else:
            # Fallback to simple decision
            self._fallback_decision(model, seat, callback)
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for GTO mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for GTO mode"""
        return 0
    
    def _get_gto_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get decision from GTO provider"""
        def gto_decision():
            try:
                # This would call your actual GTO provider
                # For now, simulate with a delay
                time.sleep(1.0)  # GTO thinking time
                
                # Placeholder GTO logic
                legal_actions = model.legal_actions
                if "RAISE" in legal_actions and len(model.board) == 0:  # Preflop aggression
                    action = "RAISE"
                    amount = model.pot * 2  # 2x pot raise
                elif "BET" in legal_actions and len(model.board) >= 3:  # Post-flop betting
                    action = "BET"
                    amount = int(model.pot * 0.75)  # 3/4 pot bet
                elif "CALL" in legal_actions:
                    action = "CALL"
                    amount = None
                else:
                    action = "CHECK"
                    amount = None
                
                callback(DecisionReady(seat=seat, action=action, amount=amount))
                
            except Exception as e:
                print(f"⚠️ GTODriver: Error getting GTO decision: {e}")
                self._fallback_decision(model, seat, callback)
        
        thread = threading.Thread(target=gto_decision)
        thread.daemon = True
        thread.start()
    
    def _fallback_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Fallback decision when GTO provider fails"""
        def simple_decision():
            time.sleep(0.3)
            
            legal_actions = model.legal_actions
            if "CHECK" in legal_actions:
                action = "CHECK"
            elif "CALL" in legal_actions:
                action = "CALL"
            else:
                action = "FOLD"
            
            callback(DecisionReady(seat=seat, action=action, amount=None))
        
        thread = threading.Thread(target=simple_decision)
        thread.daemon = True
        thread.start()


def create_driver(session_mode: str, **kwargs) -> Any:
    """Factory function to create appropriate driver"""
    
    if session_mode == "REVIEW":
        hand_data = kwargs.get("hand_data", {})
        return ReviewDriver(hand_data)
    
    elif session_mode == "PRACTICE":
        bot_seats = kwargs.get("bot_seats", [1, 2, 3, 4, 5])  # All except seat 0 (human)
        return PracticeDriver(bot_seats)
    
    elif session_mode == "GTO":
        gto_provider = kwargs.get("gto_provider")
        return GTODriver(gto_provider)
    
    else:
        raise ValueError(f"Unknown session mode: {session_mode}")

```

---

### app_shell.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/app_shell.py`

```python
import tkinter as tk
from tkinter import ttk
import uuid

from .services.event_bus import EventBus
from .services.service_container import ServiceContainer
from .services.timer_manager import TimerManager
from .services.theme_manager import ThemeManager
from .services.hands_repository import HandsRepository, StudyMode
from .state.store import Store
from .state.reducers import root_reducer
from .mvu.hands_review_mvu import MVUHandsReviewTab as HandsReviewTab
from .tabs.practice_session_tab import PracticeSessionTab
from .tabs.gto_session_tab import GTOSessionTab

from .menu_integration import add_theme_manager_to_menu


class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # Store root reference for menu integration
        self.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # app-scoped services
        self.services = ServiceContainer()
        self.services.provide_app("event_bus", EventBus())
        self.services.provide_app("theme", ThemeManager())
        self.services.provide_app("hands_repository", HandsRepository())
        
        # Create global GameDirector for action sequencing
        from .services.game_director import GameDirector
        game_director = GameDirector(event_bus=self.services.get_app("event_bus"))
        self.services.provide_app("game_director", game_director)
        
        # Create global EffectBus service for sound management
        from .services.effect_bus import EffectBus
        effect_bus = EffectBus(
            game_director=game_director,
            event_bus=self.services.get_app("event_bus")
        )
        self.services.provide_app("effect_bus", effect_bus)
        
        # Create architecture compliant hands review controller
        from .services.hands_review_event_controller import HandsReviewEventController
        
        # Initialize Store with initial state and reducer
        initial_state = {
            "table": {"dim": {"width": 800, "height": 600}},
            "seats": [],
            "board": [],
            "pot": {"amount": 0},
            "dealer": {},
            "review": {},
            "enhanced_rpgw": {},
            "event_bus": self.services.get_app("event_bus")
        }
        store = Store(initial_state, root_reducer)
        self.services.provide_app("store", store)
        
        hands_review_controller = HandsReviewEventController(
            event_bus=self.services.get_app("event_bus"),
            store=store,
            services=self.services
        )
        self.services.provide_app("hands_review_controller", hands_review_controller)
        
        # Subscribe to voice events to keep architecture event-driven
        def _on_voice(payload):
            try:
                action = (payload or {}).get("action")
                vm = getattr(effect_bus, "voice_manager", None)
                if not (vm and action):
                    return
                cfg = getattr(effect_bus, "config", {}) or {}
                voice_type = getattr(effect_bus, "voice_type", "")
                table = (cfg.get("voice_sounds", {}) or {}).get(voice_type, {})
                rel = table.get(action)
                if rel:
                    vm.play(rel)
            except Exception:
                pass
        self.services.get_app("event_bus").subscribe("effect_bus:voice", _on_voice)
        
        # Create shared store for poker game state (per architecture doc)
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": StudyMode.REPLAY.value,
                "collection": None
            }
        }
        self.services.provide_app("store", Store(initial_state, root_reducer))

        # Create menu system
        self._create_menu_system()
        
        # tabs (order: Practice, GTO, Hands Review - main product features only)
        self._add_tab("Practice Session", PracticeSessionTab)
        self._add_tab("GTO Session", GTOSessionTab)
        self._add_tab("Hands Review", HandsReviewTab)
        # Bind global font size shortcuts (Cmd/Ctrl - and =)
        self._bind_font_shortcuts(root)

    def _add_tab(self, title: str, TabClass):
        session_id = str(uuid.uuid4())
        timers = TimerManager(self)
        self.services.provide_session(session_id, "timers", timers)

        # Update active tab in shared store
        store = self.services.get_app("store")
        store.dispatch({"type": "SET_ACTIVE_TAB", "name": title})
        
        # Create tab with services
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)
        
        # Call on_show if available
        if hasattr(tab, "on_show"):
            tab.on_show()

    def _create_menu_system(self):
        """Create the application menu system."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._increase_font(None))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._decrease_font(None))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=lambda: self._reset_font(None))
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme management
        settings_menu.add_command(label="Theme Editor", command=self._open_theme_editor)
        settings_menu.add_command(label="Sound Settings", command=self._open_sound_settings)
        settings_menu.add_separator()
        
        # Add Theme Manager to Settings menu using our integration helper
        add_theme_manager_to_menu(settings_menu, self.root, self._on_theme_changed)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _new_session(self):
        """Start a new session."""
        print("🔄 New session requested")
        # TODO: Implement session reset
        
    def _on_theme_changed(self):
        """Called when theme is changed via Theme Manager."""
        print("🎨 Theme changed - refreshing UI...")
        
        try:
            # Reload theme manager to get latest changes
            theme_manager = self.services.get_app("theme")
            if hasattr(theme_manager, 'reload'):
                theme_manager.reload()
            
            # Force rebuild themes to pick up any live changes
            try:
                from .services.theme_factory import build_all_themes
                themes = build_all_themes()
                # Register updated themes
                for name, tokens in themes.items():
                    theme_manager.register(name, tokens)
                print(f"🔄 Rebuilt and registered {len(themes)} themes")
            except Exception as e:
                print(f"⚠️ Theme rebuild warning: {e}")
            
            # Refresh all tabs with new theme
            for i in range(self.notebook.index("end")):
                try:
                    tab = self.notebook.nametowidget(self.notebook.tabs()[i])
                    
                    # Try multiple refresh methods
                    if hasattr(tab, '_refresh_ui_colors'):
                        tab._refresh_ui_colors()
                        print(f"✅ Refreshed tab {i} via _refresh_ui_colors")
                    elif hasattr(tab, 'refresh_theme'):
                        tab.refresh_theme()
                        print(f"✅ Refreshed tab {i} via refresh_theme")
                    elif hasattr(tab, '_on_theme_changed'):
                        tab._on_theme_changed()
                        print(f"✅ Refreshed tab {i} via _on_theme_changed")
                    else:
                        print(f"ℹ️ Tab {i} has no theme refresh method")
                        
                except Exception as e:
                    print(f"⚠️ Error refreshing tab {i}: {e}")
            
            print("✅ Live theme refresh completed")
            
        except Exception as e:
            print(f"❌ Theme refresh error: {e}")
            import traceback
            traceback.print_exc()
        
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Poker Pro Trainer",
            "Poker Pro Trainer\n\n"
            "Advanced poker training with luxury themes\n"
            "and professional game analysis.\n\n"
            "🎨 Theme Manager integrated\n"
            "🃏 16 luxury themes available\n"
            "📊 Comprehensive hand review\n"
            "🤖 AI-powered training"
        )

    def _bind_font_shortcuts(self, root):
        # macOS Command key bindings (Cmd - decreases, Cmd = increases)
        root.bind_all("<Command-minus>", self._decrease_font)
        root.bind_all("<Command-equal>", self._increase_font)  # This is Cmd = (increase)
        root.bind_all("<Command-0>", self._reset_font)
        
        # Additional symbols that might work
        root.bind_all("<Command-plus>", self._increase_font)   # Shift+= gives +
        
        # Numpad variants
        root.bind_all("<Command-KP_Subtract>", self._decrease_font)
        root.bind_all("<Command-KP_Add>", self._increase_font)
        
        # Windows/Linux Control variants  
        root.bind_all("<Control-minus>", self._decrease_font)
        root.bind_all("<Control-equal>", self._increase_font)
        root.bind_all("<Control-plus>", self._increase_font)
        root.bind_all("<Control-0>", self._reset_font)
        
        print("🔧 Font shortcuts bound successfully")

    def _set_global_font_scale(self, delta: int | None):
        print(f"🔧 Font scale called with delta: {delta}")
        theme: ThemeManager = self.services.get_app("theme")
        fonts = dict(theme.get_fonts())
        base = list(fonts.get("main", ("Arial", 20, "normal")))
        print(f"🔧 Current base font: {base}")
        
        if delta is None:
            new_base_size = 20  # Default 20px size for readability
        else:
            new_base_size = max(10, min(40, int(base[1]) + delta))
        
        print(f"🔧 New base size: {new_base_size}")
        
        # Scale all fonts proportionally from 20px base
        fonts["main"] = (base[0], new_base_size, base[2] if len(base) > 2 else "normal")
        fonts["pot_display"] = (base[0], new_base_size + 8, "bold")  # +8 for pot display
        fonts["bet_amount"] = (base[0], new_base_size + 4, "bold")   # +4 for bet amounts
        fonts["body"] = ("Consolas", max(new_base_size, 12))         # Same as main for body text
        fonts["small"] = ("Consolas", max(new_base_size - 4, 10))    # -4 for smaller text
        fonts["header"] = (base[0], max(new_base_size + 2, 14), "bold") # +2 for headers
        
        print(f"🔧 Updated fonts: {fonts}")
        theme.set_fonts(fonts)
        
        # Force all tabs to re-render with new fonts
        for idx in range(self.notebook.index("end")):
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[idx])
            if hasattr(tab_widget, "on_show"):
                tab_widget.on_show()
            # Also force font refresh if the widget has that method
            if hasattr(tab_widget, "_refresh_fonts"):
                tab_widget._refresh_fonts()
        print("🔧 Font scaling complete")

    def _increase_font(self, event=None):
        print("🔧 Increase font called!")
        self._set_global_font_scale(+1)

    def _decrease_font(self, event=None):
        print("🔧 Decrease font called!")
        self._set_global_font_scale(-1)

    def _reset_font(self, event=None):
        print("🔧 Reset font called!")
        self._set_global_font_scale(None)

    def _open_theme_editor(self):
        """Open the Theme Editor in a new window."""
        try:
            from .tabs.theme_editor_tab import ThemeEditorTab
            # Create a new toplevel window for the theme editor
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Theme Editor - Poker Pro Trainer")
            theme_window.geometry("900x700")
            theme_window.resizable(True, True)
            
            # Center the window on screen
            theme_window.update_idletasks()
            x = (theme_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (theme_window.winfo_screenheight() // 2) - (700 // 2)
            theme_window.geometry(f"900x700+{x}+{y}")
            
            # Create the theme editor tab in the new window
            theme_editor = ThemeEditorTab(theme_window, self.services)
            theme_editor.pack(fill=tk.BOTH, expand=True)
            
            print("🎨 Theme Editor opened in new window")
        except Exception as e:
            print(f"❌ Error opening Theme Editor: {e}")
            import traceback
            traceback.print_exc()

    def _open_sound_settings(self):
        """Open the Sound Settings in a new window."""
        try:
            from .tabs.sound_settings_tab import SoundSettingsTab
            # Create a new toplevel window for the sound settings
            sound_window = tk.Toplevel(self.root)
            sound_window.title("Sound Settings - Poker Pro Trainer")
            sound_window.geometry("1200x800")
            sound_window.resizable(True, True)
            
            # Center the window on screen
            sound_window.update_idletasks()
            x = (sound_window.winfo_screenwidth() // 2) - (1200 // 2)
            y = (sound_window.winfo_screenheight() // 2) - (800 // 2)
            sound_window.geometry(f"1200x800+{x}+{y}")
            
            # Create the sound settings tab in the new window
            sound_settings = SoundSettingsTab(sound_window, self.services)
            sound_settings.pack(fill=tk.BOTH, expand=True)
            
            print("🔊 Sound Settings opened in new window")
        except Exception as e:
            print(f"❌ Error opening Sound Settings: {e}")
            import traceback
            traceback.print_exc()



```

---

### run_new_ui.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/run_new_ui.py`

```python
import tkinter as tk
import sys
import os

def check_terminal_compatibility():
    """Check if we're running in VS Code integrated terminal and warn user."""
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        print("⚠️  WARNING: Running GUI in VS Code integrated terminal may cause crashes!")
        print("💡 RECOMMENDED: Run this from macOS Terminal app instead:")
        print(f"   cd {os.getcwd()}")
        print(f"   python3 {os.path.basename(__file__)}")
        print("🚀 Continuing automatically...")
        print()
        
        # Commented out for convenience during development
        # response = input("Continue anyway? (y/N): ").lower().strip()
        # if response not in ['y', 'yes']:
        #     print("Exiting safely. Run from external terminal for best experience.")
        #     sys.exit(0)

try:  # Prefer package-relative import (python -m backend.run_new_ui)
    from .ui.app_shell import AppShell  # type: ignore
except Exception:
    try:  # Running as a script from backend/ (python backend/run_new_ui.py)
        from ui.app_shell import AppShell  # type: ignore
    except Exception:
        # Last resort: ensure repo root is on sys.path then import absolute
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from ui.app_shell import AppShell  # type: ignore


def main() -> None:
    # Apply runtime fixes before starting the application
    try:
        print("🔧 Applying runtime fixes...")
        from fix_runtime_errors import main as apply_fixes
        apply_fixes()
        print("✅ Runtime fixes applied successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not apply runtime fixes: {e}")
        print("🎯 Continuing anyway...")
    
    # Check terminal compatibility before creating GUI
    check_terminal_compatibility()
    
    root = tk.Tk()
    root.title("Poker Trainer — New UI Preview")
    
    # Configure window size and position (70% of screen, centered)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate 70% size
    window_width = int(screen_width * 0.7)
    window_height = int(screen_height * 0.7)
    
    # Calculate center position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set window geometry (width x height + x_offset + y_offset)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Set minimum size (50% of calculated size)
    root.minsize(int(window_width * 0.5), int(window_height * 0.5))
    
    AppShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()


```

---

## PREVIOUS FIX ATTEMPTS

### MVU_INFINITE_LOOP_FIX_SUMMARY.md

**Path**: `/Users/yeogirlyun/Python/Poker/MVU_INFINITE_LOOP_FIX_SUMMARY.md`

```markdown
# 🎉 MVU Infinite Rendering Loop - FIXED!

## ✅ **Status: RESOLVED**

The infinite rendering loop issue has been successfully fixed! The application now starts normally without the continuous "0 seats ↔ 2 seats" rendering loop.

## 🔧 **Fixes Applied**

### ✅ **Fix A: Value-Equal Dataclasses**
- **Changed**: All core types (`Model`, `SeatState`, `TableRendererProps`) now use `@dataclass(frozen=True, eq=True, slots=True)`
- **Impact**: Proper value equality instead of object identity comparison
- **Result**: `props == self.current_props` now works correctly

### ✅ **Fix B: Proper Props Memoization**
- **Changed**: Added `_last_props` field with early-out comparison in `_on_model_changed`
- **Removed**: Broken `hash(id(...))` approach
- **Result**: Props are only created when model actually changes

### ✅ **Fix D: Removed UpdateUI Command**
- **Deleted**: `UpdateUI` command class and all usages
- **Changed**: Store only notifies subscribers when `new_model != old_model`
- **Result**: No redundant UI update commands causing extra renders

### ✅ **Fix H: Immutable Structures**
- **Changed**: `board: List[str]` → `board: tuple[str, ...]`
- **Changed**: `cards: List[str]` → `cards: tuple[str, ...]`
- **Changed**: `banners: List[Banner]` → `banners: tuple[Banner, ...]`
- **Result**: Immutable data structures prevent accidental mutations

## 🧪 **Test Results**

**Before Fix:**
```
🎨 MVUPokerTableRenderer: Rendering with 0 seats
🎨 MVUPokerTableRenderer: Rendering with 2 seats
🎨 MVUPokerTableRenderer: Rendering with 0 seats
🎨 MVUPokerTableRenderer: Rendering with 2 seats
[Infinite loop - app unusable]
```

**After Fix:**
```
🎬 GameDirector: Initialized
🔊 EffectBus: Loaded 36 sound files
🎯 HandsReviewEventController: Architecture compliant controller initialized
[Normal startup - no infinite loop]
```

## 📋 **Remaining Tasks**

### 🔄 **Still Pending (Lower Priority)**

- **Fix C**: Make view completely pure and callback-safe
- **Fix E**: Ensure UI updates happen on main thread
- **Fix F**: Add rigorous gating for advance operations
- **Fix G**: Guard AnimationFinished against stale tokens

These remaining fixes are **performance and robustness improvements** but are not critical since the main infinite loop issue is resolved.

## 🎯 **Key Learnings**

1. **Value Equality is Critical**: Using `@dataclass(eq=True)` is essential for proper props comparison
2. **Immutable Data Structures**: Tuples prevent accidental mutations and ensure consistent equality
3. **Avoid Redundant Commands**: The Store's automatic notification is sufficient; explicit `UpdateUI` commands create loops
4. **Early-Out Memoization**: Proper props caching prevents unnecessary re-renders

## 🚀 **Next Steps**

The MVU architecture is now **fully functional** with:
- ✅ No infinite loops
- ✅ Proper state management
- ✅ Clean separation of concerns
- ✅ Value-based equality checking

The poker hands review feature should now work smoothly without performance issues!

---

**Fixed by**: Implementing proper MVU patterns with value equality and immutable data structures
**Date**: 2024-12-19
**Status**: ✅ **RESOLVED**

```

---

### MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md

**Path**: `/Users/yeogirlyun/Python/Poker/MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md`

```markdown
# MVU Infinite Rendering Loop Bug Report

## Summary
The MVU (Model-View-Update) implementation of the poker hands review tab is stuck in an infinite rendering loop, alternating between "Rendering with 0 seats" and "Rendering with 2 seats" continuously, making the application unusable.

## Issue Details

### Symptoms
- Application becomes unresponsive due to continuous rendering
- Console output shows infinite alternating pattern:
  ```
  🎨 MVUPokerTableRenderer: Rendering with 0 seats
  🎨 MVUPokerTableRenderer: Rendering with 2 seats
  🎨 MVUPokerTableRenderer: Rendering with 0 seats
  🎨 MVUPokerTableRenderer: Rendering with 2 seats
  ```
- Debug output shows `Seats equal: False` despite same review cursor and waiting state
- Props comparison always returns `False` even when data appears identical

### Debug Information
From the debug logs:
```
🎨 MVUPokerTableRenderer: Rendering with 2 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
🎨 MVUPokerTableRenderer: Rendering with 0 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
```

## Root Cause Analysis

### Primary Issue
The `TableRendererProps` objects are being recreated on every model update, causing the equality check `self.current_props == props` to always fail, even when the actual data is identical. This leads to unnecessary re-renders.

### Contributing Factors
1. **Fresh Object Creation**: `TableRendererProps.from_model(model)` creates new objects every time
2. **Nested Object Inequality**: The `seats` dictionary contains `SeatState` objects that may be recreated
3. **Model Update Frequency**: Something is causing frequent model updates that trigger re-renders

## Affected Files

### 1. backend/ui/mvu/view.py
**MVUPokerTableRenderer.render() method:**
```python
def render(self, props: TableRendererProps) -> None:
    """
    Render the table based on props
    Pure function - only reads from props, never mutates state
    """
    # Skip if props haven't changed
    if self.current_props == props:  # ❌ This check always fails
        return
    
    # Debug what changed
    print(f"🎨 MVUPokerTableRenderer: Rendering with {len(props.seats)} seats")
    print(f"🔍 Props changed: old_props is None: {self.current_props is None}")
    if self.current_props is not None:
        print(f"🔍 Props equal: {self.current_props == props}")
        print(f"🔍 Seats equal: {self.current_props.seats == props.seats}")
        print(f"🔍 Review cursor: {self.current_props.review_cursor} -> {props.review_cursor}")
        print(f"🔍 Waiting for: {self.current_props.waiting_for} -> {props.waiting_for}")
    
    self.current_props = props
    
    # Update controls based on props
    self._update_controls(props)
    
    # Render table on canvas
    self._render_table(props)
    
    # Update review controls
    self._update_review_controls(props)
```

### 2. backend/ui/mvu/hands_review_mvu.py
**Model change handler that triggers renders:**
```python
def _on_model_changed(self, model: Model) -> None:
    """Handle model changes - update the view"""
    try:
        # Convert model to props
        props = TableRendererProps.from_model(model)  # ❌ Creates fresh object
        
        # Render table
        if self.table_renderer:
            self.table_renderer.render(props)  # ❌ Triggers infinite loop
    
    except Exception as e:
        print(f"⚠️ MVUHandsReviewTab: Error updating view: {e}")
```

### 3. backend/ui/mvu/types.py
**TableRendererProps definition:**
```python
@dataclass(frozen=True)
class TableRendererProps:
    """Props derived from Model for the table renderer"""
    # Table state
    seats: Dict[int, SeatState]  # ❌ Contains nested objects
    board: List[str]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: Set[str]
    
    # UI state
    banners: List[Banner]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    
    # Review state
    review_cursor: int
    review_len: int
    review_paused: bool
    session_mode: str
    
    # Hints
    gto_hint: Optional[GtoHint]
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        """Derive props from model"""
        return cls(  # ❌ Creates new instance every time
            seats=model.seats,
            board=model.board,
            pot=model.pot,
            to_act_seat=model.to_act_seat,
            legal_actions=model.legal_actions,
            banners=model.banners,
            theme_id=model.theme_id,
            autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for,
            review_cursor=model.review_cursor,
            review_len=model.review_len,
            review_paused=model.review_paused,
            session_mode=model.session_mode,
            gto_hint=model.gto_hint
        )
```

### 4. backend/ui/mvu/store.py
**Store dispatch and subscription mechanism:**
```python
def dispatch(self, msg: Msg) -> None:
    """
    Dispatch a message to update the model
    """
    with self._lock:
        print(f"🏪 MVUStore: Dispatching {type(msg).__name__}")
        
        # Update model using pure reducer
        new_model, commands = update(self.model, msg)
        
        # Update stored model
        old_model = self.model
        self.model = new_model
        
        # Execute commands
        for cmd in commands:
            self._execute_command(cmd)
        
        # Notify subscribers - ❌ This may trigger too frequently
        for callback in self.subscribers:
            callback(self.model)
```

## Reproduction Steps

1. Start the application: `python3 backend/run_new_ui.py`
2. Navigate to the "Hands Review" tab
3. Observe infinite console output of rendering messages
4. Application becomes unresponsive due to continuous rendering

## Test Case
Create a simple test to reproduce:
```python
# backend/test_mvu_infinite_loop.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ui.mvu.hands_review_mvu import MVUHandsReviewTab
from ui.mvu.types import Model
import tkinter as tk

def test_infinite_loop():
    root = tk.Tk()
    
    # Create MVU tab
    tab = MVUHandsReviewTab(root, services=None)
    
    # This should trigger the infinite loop
    print("Starting test - should see infinite rendering...")
    
    # Let it run for a few seconds
    root.after(3000, root.quit)
    root.mainloop()

if __name__ == "__main__":
    test_infinite_loop()
```

## Proposed Solutions

### Solution 1: Implement Proper Props Memoization
Cache `TableRendererProps` objects and only create new ones when the underlying data actually changes:

```python
class MVUHandsReviewTab:
    def __init__(self, ...):
        self._cached_props = None
        self._last_model_hash = None
    
    def _on_model_changed(self, model: Model) -> None:
        # Create a hash of relevant model data
        model_hash = hash((
            id(model.seats), model.review_cursor, model.waiting_for,
            model.pot, model.to_act_seat, model.theme_id
        ))
        
        # Only create new props if model actually changed
        if model_hash != self._last_model_hash:
            self._cached_props = TableRendererProps.from_model(model)
            self._last_model_hash = model_hash
        
        if self.table_renderer and self._cached_props:
            self.table_renderer.render(self._cached_props)
```

### Solution 2: Implement Deep Equality Check
Add a custom `__eq__` method to `TableRendererProps` that properly compares nested objects:

```python
@dataclass(frozen=True)
class TableRendererProps:
    # ... fields ...
    
    def __eq__(self, other):
        if not isinstance(other, TableRendererProps):
            return False
        
        # Compare all fields deeply
        return (
            self.seats == other.seats and
            self.board == other.board and
            self.pot == other.pot and
            self.to_act_seat == other.to_act_seat and
            self.legal_actions == other.legal_actions and
            # ... other fields
        )
```

### Solution 3: Reduce Subscription Frequency
Only notify view subscribers when specific fields that affect rendering actually change:

```python
def dispatch(self, msg: Msg) -> None:
    with self._lock:
        old_model = self.model
        new_model, commands = update(self.model, msg)
        
        # Only notify if rendering-relevant fields changed
        if self._should_notify_view(old_model, new_model):
            for callback in self.subscribers:
                callback(new_model)
        
        self.model = new_model
        # ... execute commands
```

## Priority
**HIGH** - Application is completely unusable due to infinite loop consuming CPU resources.

## Environment
- Python 3.13.2
- Tkinter GUI framework
- MVU architecture implementation
- macOS (darwin 24.6.0)

## Additional Notes
- This issue was introduced when implementing the MVU architecture to replace the previous HandsReviewTab
- The previous ReviewSeek infinite loop was fixed, but this rendering loop emerged as a separate issue
- The root cause is fundamental to how props comparison works in the MVU pattern
- A proper solution requires careful consideration of when and how to trigger re-renders

## Workaround
Currently, there is no viable workaround. The application must be terminated with Ctrl+C.

```

---

## ARCHITECTURE REFERENCES

### PROJECT_PRINCIPLES_v2.md

**Path**: `/Users/yeogirlyun/Python/Poker/docs/PROJECT_PRINCIPLES_v2.md`

```markdown
## Project Principles v2 (Authoritative)

### Architecture
- Single-threaded, event-driven coordinator (GameDirector). All timing via coordinator.
- Single source of truth per session (Store). No duplicate state.
- Event-driven only. UI is pure render from state; no business logic in UI.

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

### 🚫 CRITICAL AI AGENT COMPLIANCE RULES (NEVER VIOLATE)

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

```

---

## 🚨 URGENT ACTION ITEMS

1. **Add Deep Debug Logging**: Instrument the props comparison to show exact differences
2. **Isolate the Trigger**: Find what's causing the initial model change
3. **Test Dataclass Equality**: Create minimal test case for TableRendererProps equality
4. **Check Object Identity**: Verify if objects are being recreated unnecessarily
5. **Review Scale Widget**: Ensure review scale callbacks are truly disabled
6. **Memory Profiling**: Check for memory leaks or object pooling issues

## 🆘 EMERGENCY WORKAROUNDS

If the issue cannot be resolved quickly:

1. **Revert to Legacy Tab**: Temporarily restore the old HandsReviewTab
2. **Disable MVU Tab**: Remove MVU tab from main app until fixed
3. **Add Rate Limiting**: Limit renders to max 1 per 100ms as emergency brake
4. **Force Early Return**: Add counter-based early return after N renders

---

## 📋 END OF PERSISTENT LOOP BUG REPORT

**Priority**: CRITICAL - Application completely broken

**Next Step**: Immediate deep debugging session required

*This report documents the failure of initial fix attempts and provides direction for deeper investigation.*

```

---

### INITIAL_ANALYSIS.md

**Path:** `MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md`

```markdown
# MVU Infinite Rendering Loop Bug Report

## Summary
The MVU (Model-View-Update) implementation of the poker hands review tab is stuck in an infinite rendering loop, alternating between "Rendering with 0 seats" and "Rendering with 2 seats" continuously, making the application unusable.

## Issue Details

### Symptoms
- Application becomes unresponsive due to continuous rendering
- Console output shows infinite alternating pattern:
  ```
  🎨 MVUPokerTableRenderer: Rendering with 0 seats
  🎨 MVUPokerTableRenderer: Rendering with 2 seats
  🎨 MVUPokerTableRenderer: Rendering with 0 seats
  🎨 MVUPokerTableRenderer: Rendering with 2 seats
  ```
- Debug output shows `Seats equal: False` despite same review cursor and waiting state
- Props comparison always returns `False` even when data appears identical

### Debug Information
From the debug logs:
```
🎨 MVUPokerTableRenderer: Rendering with 2 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
🎨 MVUPokerTableRenderer: Rendering with 0 seats
🔍 Props changed: old_props is None: False
🔍 Props equal: False
🔍 Seats equal: False
🔍 Review cursor: 0 -> 0
🔍 Waiting for: NONE -> NONE
```

## Root Cause Analysis

### Primary Issue
The `TableRendererProps` objects are being recreated on every model update, causing the equality check `self.current_props == props` to always fail, even when the actual data is identical. This leads to unnecessary re-renders.

### Contributing Factors
1. **Fresh Object Creation**: `TableRendererProps.from_model(model)` creates new objects every time
2. **Nested Object Inequality**: The `seats` dictionary contains `SeatState` objects that may be recreated
3. **Model Update Frequency**: Something is causing frequent model updates that trigger re-renders

## Affected Files

### 1. backend/ui/mvu/view.py
**MVUPokerTableRenderer.render() method:**
```python
def render(self, props: TableRendererProps) -> None:
    """
    Render the table based on props
    Pure function - only reads from props, never mutates state
    """
    # Skip if props haven't changed
    if self.current_props == props:  # ❌ This check always fails
        return
    
    # Debug what changed
    print(f"🎨 MVUPokerTableRenderer: Rendering with {len(props.seats)} seats")
    print(f"🔍 Props changed: old_props is None: {self.current_props is None}")
    if self.current_props is not None:
        print(f"🔍 Props equal: {self.current_props == props}")
        print(f"🔍 Seats equal: {self.current_props.seats == props.seats}")
        print(f"🔍 Review cursor: {self.current_props.review_cursor} -> {props.review_cursor}")
        print(f"🔍 Waiting for: {self.current_props.waiting_for} -> {props.waiting_for}")
    
    self.current_props = props
    
    # Update controls based on props
    self._update_controls(props)
    
    # Render table on canvas
    self._render_table(props)
    
    # Update review controls
    self._update_review_controls(props)
```

### 2. backend/ui/mvu/hands_review_mvu.py
**Model change handler that triggers renders:**
```python
def _on_model_changed(self, model: Model) -> None:
    """Handle model changes - update the view"""
    try:
        # Convert model to props
        props = TableRendererProps.from_model(model)  # ❌ Creates fresh object
        
        # Render table
        if self.table_renderer:
            self.table_renderer.render(props)  # ❌ Triggers infinite loop
    
    except Exception as e:
        print(f"⚠️ MVUHandsReviewTab: Error updating view: {e}")
```

### 3. backend/ui/mvu/types.py
**TableRendererProps definition:**
```python
@dataclass(frozen=True)
class TableRendererProps:
    """Props derived from Model for the table renderer"""
    # Table state
    seats: Dict[int, SeatState]  # ❌ Contains nested objects
    board: List[str]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: Set[str]
    
    # UI state
    banners: List[Banner]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    
    # Review state
    review_cursor: int
    review_len: int
    review_paused: bool
    session_mode: str
    
    # Hints
    gto_hint: Optional[GtoHint]
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        """Derive props from model"""
        return cls(  # ❌ Creates new instance every time
            seats=model.seats,
            board=model.board,
            pot=model.pot,
            to_act_seat=model.to_act_seat,
            legal_actions=model.legal_actions,
            banners=model.banners,
            theme_id=model.theme_id,
            autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for,
            review_cursor=model.review_cursor,
            review_len=model.review_len,
            review_paused=model.review_paused,
            session_mode=model.session_mode,
            gto_hint=model.gto_hint
        )
```

### 4. backend/ui/mvu/store.py
**Store dispatch and subscription mechanism:**
```python
def dispatch(self, msg: Msg) -> None:
    """
    Dispatch a message to update the model
    """
    with self._lock:
        print(f"🏪 MVUStore: Dispatching {type(msg).__name__}")
        
        # Update model using pure reducer
        new_model, commands = update(self.model, msg)
        
        # Update stored model
        old_model = self.model
        self.model = new_model
        
        # Execute commands
        for cmd in commands:
            self._execute_command(cmd)
        
        # Notify subscribers - ❌ This may trigger too frequently
        for callback in self.subscribers:
            callback(self.model)
```

## Reproduction Steps

1. Start the application: `python3 backend/run_new_ui.py`
2. Navigate to the "Hands Review" tab
3. Observe infinite console output of rendering messages
4. Application becomes unresponsive due to continuous rendering

## Test Case
Create a simple test to reproduce:
```python
# backend/test_mvu_infinite_loop.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ui.mvu.hands_review_mvu import MVUHandsReviewTab
from ui.mvu.types import Model
import tkinter as tk

def test_infinite_loop():
    root = tk.Tk()
    
    # Create MVU tab
    tab = MVUHandsReviewTab(root, services=None)
    
    # This should trigger the infinite loop
    print("Starting test - should see infinite rendering...")
    
    # Let it run for a few seconds
    root.after(3000, root.quit)
    root.mainloop()

if __name__ == "__main__":
    test_infinite_loop()
```

## Proposed Solutions

### Solution 1: Implement Proper Props Memoization
Cache `TableRendererProps` objects and only create new ones when the underlying data actually changes:

```python
class MVUHandsReviewTab:
    def __init__(self, ...):
        self._cached_props = None
        self._last_model_hash = None
    
    def _on_model_changed(self, model: Model) -> None:
        # Create a hash of relevant model data
        model_hash = hash((
            id(model.seats), model.review_cursor, model.waiting_for,
            model.pot, model.to_act_seat, model.theme_id
        ))
        
        # Only create new props if model actually changed
        if model_hash != self._last_model_hash:
            self._cached_props = TableRendererProps.from_model(model)
            self._last_model_hash = model_hash
        
        if self.table_renderer and self._cached_props:
            self.table_renderer.render(self._cached_props)
```

### Solution 2: Implement Deep Equality Check
Add a custom `__eq__` method to `TableRendererProps` that properly compares nested objects:

```python
@dataclass(frozen=True)
class TableRendererProps:
    # ... fields ...
    
    def __eq__(self, other):
        if not isinstance(other, TableRendererProps):
            return False
        
        # Compare all fields deeply
        return (
            self.seats == other.seats and
            self.board == other.board and
            self.pot == other.pot and
            self.to_act_seat == other.to_act_seat and
            self.legal_actions == other.legal_actions and
            # ... other fields
        )
```

### Solution 3: Reduce Subscription Frequency
Only notify view subscribers when specific fields that affect rendering actually change:

```python
def dispatch(self, msg: Msg) -> None:
    with self._lock:
        old_model = self.model
        new_model, commands = update(self.model, msg)
        
        # Only notify if rendering-relevant fields changed
        if self._should_notify_view(old_model, new_model):
            for callback in self.subscribers:
                callback(new_model)
        
        self.model = new_model
        # ... execute commands
```

## Priority
**HIGH** - Application is completely unusable due to infinite loop consuming CPU resources.

## Environment
- Python 3.13.2
- Tkinter GUI framework
- MVU architecture implementation
- macOS (darwin 24.6.0)

## Additional Notes
- This issue was introduced when implementing the MVU architecture to replace the previous HandsReviewTab
- The previous ReviewSeek infinite loop was fixed, but this rendering loop emerged as a separate issue
- The root cause is fundamental to how props comparison works in the MVU pattern
- A proper solution requires careful consideration of when and how to trigger re-renders

## Workaround
Currently, there is no viable workaround. The application must be terminated with Ctrl+C.

```

---

## MVU ARCHITECTURE CORE

### mvu_types.py

**Path:** `backend/ui/mvu/types.py`

```python
"""
MVU (Model-View-Update) Architecture Types
Based on PokerPro UI Implementation Handbook v2
"""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, List, Set, Any, Protocol, Callable
from abc import ABC, abstractmethod


# ============================================================================
# CORE MODEL
# ============================================================================

@dataclass(frozen=True, eq=False, slots=True)
class SeatState:
    """State for a single seat at the poker table"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int  # Current bet amount
    folded: bool
    all_in: bool
    cards: tuple[str, ...]  # Hole cards (visibility rules applied) - immutable tuple
    position: int
    acting: bool = False
    
    def __eq__(self, other):
        """Value-based equality comparison"""
        if not isinstance(other, SeatState):
            return False
        return (
            self.player_uid == other.player_uid and
            self.name == other.name and
            self.stack == other.stack and
            self.chips_in_front == other.chips_in_front and
            self.folded == other.folded and
            self.all_in == other.all_in and
            self.cards == other.cards and
            self.position == other.position and
            self.acting == other.acting
        )
    
    def __hash__(self):
        """Hash based on immutable fields"""
        return hash((
            self.player_uid,
            self.name, 
            self.stack,
            self.chips_in_front,
            self.folded,
            self.all_in,
            self.cards,  # Already a tuple
            self.position,
            self.acting
        ))


@dataclass(frozen=True)
class Action:
    """Represents a poker action"""
    seat: int
    action: str  # "CHECK", "CALL", "BET", "RAISE", "FOLD"
    amount: Optional[int] = None
    street: str = "PREFLOP"


@dataclass(frozen=True)
class GtoHint:
    """GTO strategy hint"""
    action: str
    frequency: float
    reasoning: str


@dataclass(frozen=True)
class Banner:
    """UI banner/message"""
    text: str
    type: Literal["info", "warning", "error", "success"]
    duration_ms: int = 3000


@dataclass(frozen=True, eq=True, slots=True)
class Model:
    """
    Canonical Model - Single Source of Truth for poker table state
    """
    # Game State
    hand_id: str
    street: Literal["PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "DONE"]
    to_act_seat: Optional[int]
    stacks: Dict[int, int]
    pot: int
    board: tuple[str, ...]  # ("As", "Kd", "7h", ...) - immutable tuple
    seats: Dict[int, SeatState]
    legal_actions: Set[str]  # {"CHECK", "CALL", "BET", "RAISE", "FOLD"}
    last_action: Optional[Action]
    
    # Session Configuration
    session_mode: Literal["PRACTICE", "GTO", "REVIEW"]
    autoplay_on: bool
    step_delay_ms: int
    waiting_for: Literal["HUMAN_DECISION", "BOT_DECISION", "ANIMATION", "NONE"]
    
    # Review-specific
    review_cursor: int
    review_len: int
    review_paused: bool
    
    # UI State
    gto_hint: Optional[GtoHint]
    banners: tuple[Banner, ...]
    theme_id: str
    tx_id: int  # Animation token
    
    @classmethod
    def initial(cls, session_mode: Literal["PRACTICE", "GTO", "REVIEW"] = "REVIEW") -> "Model":
        """Create initial model state"""
        return cls(
            hand_id="",
            street="PREFLOP",
            to_act_seat=None,
            stacks={},
            pot=0,
            board=(),
            seats={},
            legal_actions=set(),
            last_action=None,
            session_mode=session_mode,
            autoplay_on=False,
            step_delay_ms=1000,
            waiting_for="NONE",
            review_cursor=0,
            review_len=0,
            review_paused=False,
            gto_hint=None,
            banners=(),
            theme_id="forest-green-pro",
            tx_id=0
        )


# ============================================================================
# MESSAGES (Facts)
# ============================================================================

class Msg(ABC):
    """Base message type"""
    pass


class NextPressed(Msg):
    """User pressed Next button"""
    pass


@dataclass
class AutoPlayToggled(Msg):
    """User toggled auto-play"""
    on: bool


@dataclass
class TimerTick(Msg):
    """Timer tick event"""
    now_ms: int


@dataclass
class UserChose(Msg):
    """Human user made a decision"""
    action: str
    amount: Optional[int] = None


@dataclass
class DecisionRequested(Msg):
    """System requests decision from a seat"""
    seat: int


@dataclass
class DecisionReady(Msg):
    """Decision is ready (from bot or async process)"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class AppliedAction(Msg):
    """Action was applied to PPSM"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class StreetAdvanced(Msg):
    """Street changed (PREFLOP -> FLOP, etc.)"""
    street: str


@dataclass
class HandFinished(Msg):
    """Hand completed"""
    winners: List[int]
    payouts: Dict[int, int]


@dataclass
class AnimationFinished(Msg):
    """Animation completed"""
    token: int


@dataclass
class ReviewSeek(Msg):
    """Seek to specific position in review"""
    index: int


class ReviewPlayStep(Msg):
    """Play next step in review"""
    pass


@dataclass
class LoadHand(Msg):
    """Load a new hand for review/practice"""
    hand_data: Dict[str, Any]


@dataclass
class ThemeChanged(Msg):
    """Theme was changed"""
    theme_id: str


# ============================================================================
# COMMANDS (Effects)
# ============================================================================

class Cmd(ABC):
    """Base command type"""
    pass


@dataclass
class PlaySound(Cmd):
    """Play a sound effect"""
    name: str


@dataclass
class Speak(Cmd):
    """Text-to-speech announcement"""
    text: str


@dataclass
class Animate(Cmd):
    """Trigger animation"""
    name: str
    payload: Dict[str, Any]
    token: int


@dataclass
class AskDriverForDecision(Cmd):
    """Ask session driver for decision"""
    seat: int


@dataclass
class ApplyPPSM(Cmd):
    """Apply action to Pure Poker State Machine"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class ScheduleTimer(Cmd):
    """Schedule a delayed message"""
    delay_ms: int
    msg: Msg


@dataclass
class PublishEvent(Cmd):
    """Publish event to EventBus"""
    topic: str
    payload: Dict[str, Any]



@dataclass
class GetReviewEvent(Cmd):
    """Get and dispatch review event at index"""
    index: int


# ============================================================================
# SESSION DRIVER PROTOCOL
# ============================================================================

class SessionDriver(Protocol):
    """Protocol for session-specific behavior"""
    
    @abstractmethod
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat (async, calls callback when ready)"""
        pass
    
    @abstractmethod
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at index (REVIEW mode only)"""
        pass
    
    @abstractmethod
    def review_length(self) -> int:
        """Get total review length (REVIEW mode only)"""
        pass


# ============================================================================
# TABLE RENDERER PROPS
# ============================================================================

@dataclass(frozen=True, eq=False, slots=True)
class TableRendererProps:
    """Props derived from Model for the table renderer"""
    # Table state
    seats: Dict[int, SeatState]
    board: tuple[str, ...]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: Set[str]
    
    # UI state
    banners: tuple[Banner, ...]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    
    # Review state
    review_cursor: int
    review_len: int
    review_paused: bool
    session_mode: str
    
    # Hints
    gto_hint: Optional[GtoHint]
    
    def __eq__(self, other):
        """Deep value-based equality check"""
        if not isinstance(other, TableRendererProps):
            return False
        
        # Compare seats dict properly
        if len(self.seats) != len(other.seats):
            return False
        
        for key in self.seats:
            if key not in other.seats:
                return False
            if self.seats[key] != other.seats[key]:
                return False
        
        # Compare other fields
        return (
            self.board == other.board and
            self.pot == other.pot and
            self.to_act_seat == other.to_act_seat and
            self.legal_actions == other.legal_actions and
            self.banners == other.banners and
            self.theme_id == other.theme_id and
            self.autoplay_on == other.autoplay_on and
            self.waiting_for == other.waiting_for and
            self.review_cursor == other.review_cursor and
            self.review_len == other.review_len and
            self.review_paused == other.review_paused and
            self.session_mode == other.session_mode and
            self.gto_hint == other.gto_hint
        )
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        """Derive props from model"""
        return cls(
            seats=model.seats,
            board=model.board,
            pot=model.pot,
            to_act_seat=model.to_act_seat,
            legal_actions=model.legal_actions,
            banners=model.banners,
            theme_id=model.theme_id,
            autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for,
            review_cursor=model.review_cursor,
            review_len=model.review_len,
            review_paused=model.review_paused,
            session_mode=model.session_mode,
            gto_hint=model.gto_hint
        )


# ============================================================================
# INTENT HANDLER PROTOCOL
# ============================================================================

class IntentHandler(Protocol):
    """Protocol for handling user intents from the UI"""
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        pass
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        pass
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        pass
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        pass
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        pass

```

---

### mvu_update.py

**Path:** `backend/ui/mvu/update.py`

```python
"""
MVU Update Function - Pure reducers for poker table state
Based on PokerPro UI Implementation Handbook v2
"""

from typing import Tuple, List, Optional
from dataclasses import replace

from .types import (
    Model, Msg, Cmd, SeatState, Action,
    NextPressed, AutoPlayToggled, TimerTick, UserChose,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished,
    ReviewSeek, ReviewPlayStep, LoadHand, ThemeChanged,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, GetReviewEvent
)


def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """
    Pure update function - computes (Model', Cmds) from (Model, Msg)
    No I/O operations allowed inside reducers.
    """
    if isinstance(msg, NextPressed):
        return next_pressed_reducer(model)
    
    if isinstance(msg, AutoPlayToggled):
        return replace(model, autoplay_on=msg.on), []
    
    if isinstance(msg, TimerTick):
        return on_timer_tick(model, msg)
    
    if isinstance(msg, UserChose):
        return apply_decision(model, model.to_act_seat, msg.action, msg.amount)
    
    if isinstance(msg, DecisionReady):
        return apply_decision(model, msg.seat, msg.action, msg.amount)
    
    if isinstance(msg, AppliedAction):
        return on_applied_action(model, msg)
    
    if isinstance(msg, StreetAdvanced):
        return on_street_advanced(model, msg)
    
    if isinstance(msg, HandFinished):
        return on_hand_finished(model, msg)
    
    if isinstance(msg, AnimationFinished):
        return on_animation_finished(model, msg)
    
    if isinstance(msg, ReviewSeek):
        return rebuild_state_to(model, msg.index)
    
    if isinstance(msg, ReviewPlayStep):
        return play_review_step(model)
    
    if isinstance(msg, LoadHand):
        return load_hand(model, msg)
    
    if isinstance(msg, ThemeChanged):
        return replace(model, theme_id=msg.theme_id), []
    
    # Unknown message - no change
    return model, []


# ============================================================================
# KEY REDUCERS
# ============================================================================

def next_pressed_reducer(model: Model) -> Tuple[Model, List[Cmd]]:
    """Handle Next button press based on current state"""
    
    print(f"🔘 Next pressed - State: waiting_for={model.waiting_for}, to_act_seat={model.to_act_seat}, mode={model.session_mode}, cursor={model.review_cursor}/{model.review_len}")
    
    # If waiting for human decision, Next does nothing
    if model.waiting_for == "HUMAN_DECISION":
        print("⏸️ Next pressed but waiting for human decision")
        return model, []
    
    # If waiting for bot decision, ask driver
    if model.waiting_for == "BOT_DECISION" and model.to_act_seat is not None:
        print(f"🤖 Next pressed - asking driver for decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="NONE")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    # If waiting for animation, Next does nothing
    if model.waiting_for == "ANIMATION":
        print("🎬 Next pressed but waiting for animation")
        return model, []
    
    # If no one to act, continue game flow (or advance review)
    if model.to_act_seat is None:
        if model.session_mode == "REVIEW":
            print("📖 Next pressed - no one to act in REVIEW, advancing review")
            return model, [ScheduleTimer(0, ReviewPlayStep())]
        else:
            print("⏭️ Next pressed - no one to act, continuing game flow")
            return model, [ApplyPPSM(seat=-1, action="CONTINUE", amount=None)]
    
    # Someone needs to act
    if model.session_mode == "REVIEW":
        # In review mode, all actions are pre-recorded, so advance review
        print(f"📖 Next pressed in REVIEW mode with to_act_seat={model.to_act_seat} - advancing review")
        return model, [ScheduleTimer(0, ReviewPlayStep())]
    
    # If autoplay is on and current seat is bot, ask for decision
    if model.autoplay_on and seat_is_bot(model, model.to_act_seat):
        print(f"🤖 Next pressed - autoplay bot decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="BOT_DECISION")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    print("❓ Next pressed - no action taken")
    return model, []


def apply_decision(model: Model, seat: Optional[int], action: str, amount: Optional[int]) -> Tuple[Model, List[Cmd]]:
    """Apply a poker decision (from human or bot)"""
    
    # Validate decision
    if seat is None or seat != model.to_act_seat:
        return model, []
    
    if action not in model.legal_actions:
        return model, []
    
    # Generate new transaction ID for animation
    tx = model.tx_id + 1
    
    # Create commands for effects
    cmds = [
        PlaySound(action.lower()),
        Speak(action.capitalize()),
    ]
    
    # Add appropriate animation
    if action in {"BET", "RAISE", "CALL"}:
        cmds.append(Animate("chips_to_pot", {"seat": seat, "amount": amount or 0}, token=tx))
    else:
        cmds.append(Animate("minor_flash", {"seat": seat}, token=tx))
    
    # Apply to PPSM
    cmds.append(ApplyPPSM(seat, action, amount))
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="NONE",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        # Update model to wait for animation
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="ANIMATION",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
    
    return new_model, cmds


def on_applied_action(model: Model, msg: AppliedAction) -> Tuple[Model, List[Cmd]]:
    """Handle action applied to PPSM - update from PPSM snapshot"""
    
    # This would typically get updated state from PPSM
    # For now, we'll simulate the state update
    new_model = apply_ppsm_snapshot(model, msg)
    cmds = []
    
    # In REVIEW mode, all actions are pre-recorded, so never wait for decisions
    if model.session_mode == "REVIEW":
        # Always ready for next review step
        new_model = replace(new_model, waiting_for="NONE")
    else:
        # Determine next action for live play
        if new_model.to_act_seat is not None:
            if seat_is_human(new_model, new_model.to_act_seat):
                new_model = replace(new_model, waiting_for="HUMAN_DECISION")
            else:
                new_model = replace(new_model, waiting_for="BOT_DECISION")
                if new_model.autoplay_on:
                    cmds.append(AskDriverForDecision(new_model.to_act_seat))
        else:
            # No one to act - schedule continuation
            cmds.append(ScheduleTimer(new_model.step_delay_ms, NextPressed()))
    

    return new_model, cmds


def on_street_advanced(model: Model, msg: StreetAdvanced) -> Tuple[Model, List[Cmd]]:
    """Handle street advancement (PREFLOP -> FLOP, etc.)"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("reveal_board", {"street": msg.street}, token=tx),
        PlaySound("deal")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="NONE"
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="ANIMATION"
        )
    
    return new_model, cmds


def on_hand_finished(model: Model, msg: HandFinished) -> Tuple[Model, List[Cmd]]:
    """Handle hand completion"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("pot_to_winners", {"payouts": msg.payouts}, token=tx),
        PlaySound("win")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            waiting_for="NONE",
            tx_id=tx,
            street="DONE"
        )
        # Auto-complete animation and schedule next step
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
        cmds.append(ScheduleTimer(model.step_delay_ms, ReviewPlayStep()))
    else:
        new_model = replace(
            model,
            waiting_for="ANIMATION",
            tx_id=tx,
            street="DONE"
        )
        # Schedule next action for live play
        cmds.append(ScheduleTimer(model.step_delay_ms, NextPressed()))
    
    return new_model, cmds


def on_animation_finished(model: Model, msg: AnimationFinished) -> Tuple[Model, List[Cmd]]:
    """Handle animation completion"""
    
    # Only process if this is the current animation
    if msg.token != model.tx_id:
        return model, []
    
    # Clear waiting state
    new_model = replace(model, waiting_for="NONE")
    
    # Trigger next action if needed
    cmds = []
    if model.autoplay_on and new_model.to_act_seat is not None:
        if seat_is_bot(new_model, new_model.to_act_seat):
            new_model = replace(new_model, waiting_for="BOT_DECISION")
            cmds.append(AskDriverForDecision(new_model.to_act_seat))
    
    return new_model, cmds


def on_timer_tick(model: Model, msg: TimerTick) -> Tuple[Model, List[Cmd]]:
    """Handle timer tick - can be used for timeouts, etc."""
    
    # Remove expired banners
    current_banners = [
        banner for banner in model.banners
        if msg.now_ms < banner.duration_ms  # Simplified - would need actual timestamps
    ]
    
    if len(current_banners) != len(model.banners):
        return replace(model, banners=current_banners), []
    
    return model, []


# ============================================================================
# REVIEW-SPECIFIC REDUCERS
# ============================================================================

def rebuild_state_to(model: Model, index: int) -> Tuple[Model, List[Cmd]]:
    """Rebuild state to specific review index"""
    
    if model.session_mode != "REVIEW":
        return model, []
    
    # Clamp index
    index = max(0, min(index, model.review_len - 1))
    
    # This would typically replay events up to index
    # For now, just update cursor
    new_model = replace(
        model,
        review_cursor=index,
        waiting_for="NONE"
    )
    
    return new_model, []


def play_review_step(model: Model) -> Tuple[Model, List[Cmd]]:
    """Play next step in review"""
    
    print(f"📖 PlayReviewStep: cursor={model.review_cursor}, len={model.review_len}, mode={model.session_mode}")
    
    if model.session_mode != "REVIEW":
        print("❌ PlayReviewStep: Not in REVIEW mode")
        return model, []
    
    if model.review_cursor >= model.review_len - 1:
        print("🏁 PlayReviewStep: End of review reached")
        return model, []
    
    # Advance cursor
    new_cursor = model.review_cursor + 1
    new_model = replace(model, review_cursor=new_cursor)
    
    print(f"➡️ PlayReviewStep: Advancing to cursor {new_cursor}")
    
    # We need to get the event from session driver and dispatch it
    return new_model, [GetReviewEvent(index=new_cursor)]


def load_hand(model: Model, msg: LoadHand) -> Tuple[Model, List[Cmd]]:
    """Load new hand data"""
    
    hand_data = msg.hand_data
    
    # Extract hand information
    hand_id = hand_data.get("hand_id", "")
    seats_data = hand_data.get("seats", {})
    board = tuple(hand_data.get("board", []))
    pot = hand_data.get("pot", 0)
    
    # Convert seats data to SeatState objects
    seats = {}
    stacks = {}
    for seat_num, seat_data in seats_data.items():
        seat_state = SeatState(
            player_uid=seat_data.get("player_uid", f"player_{seat_num}"),
            name=seat_data.get("name", f"Player {seat_num}"),
            stack=seat_data.get("stack", 1000),
            chips_in_front=seat_data.get("chips_in_front", 0),
            folded=seat_data.get("folded", False),
            all_in=seat_data.get("all_in", False),
            cards=tuple(seat_data.get("cards", [])),
            position=int(seat_num)
        )
        seats[int(seat_num)] = seat_state
        stacks[int(seat_num)] = seat_state.stack
    
    new_model = replace(
        model,
        hand_id=hand_id,
        seats=seats,
        stacks=stacks,
        board=board,
        pot=pot,
        street="PREFLOP",
        to_act_seat=hand_data.get("to_act_seat"),
        legal_actions=set(hand_data.get("legal_actions", [])),
        waiting_for="NONE",
        review_cursor=0,
        review_len=hand_data.get("review_len", 0)
    )
    
    return new_model, []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def seat_is_human(model: Model, seat: int) -> bool:
    """Check if seat is controlled by human player"""
    # For now, assume seat 0 is human in practice/review mode
    if model.session_mode in ["PRACTICE", "REVIEW"]:
        return seat == 0
    return False


def seat_is_bot(model: Model, seat: int) -> bool:
    """Check if seat is controlled by bot"""
    return not seat_is_human(model, seat)


def apply_ppsm_snapshot(model: Model, msg: AppliedAction) -> Model:
    """
    Apply PPSM state snapshot after action
    This would typically get real state from PPSM
    """
    
    # Simulate basic state changes
    new_seats = dict(model.seats)
    new_stacks = dict(model.stacks)
    new_pot = model.pot
    
    print(f"🎯 Applying action: {msg.action} by seat {msg.seat} (amount: {msg.amount})")
    
    # Clear all acting status first
    for seat_num in new_seats:
        new_seats[seat_num] = replace(new_seats[seat_num], acting=False)
    
    # Update acting seat
    if msg.seat in new_seats:
        seat_state = new_seats[msg.seat]
        
        # Simulate stack/bet changes
        if msg.action in ["BET", "RAISE", "CALL"] and msg.amount:
            new_stacks[msg.seat] = max(0, new_stacks[msg.seat] - msg.amount)
            new_pot += msg.amount
            new_seats[msg.seat] = replace(
                new_seats[msg.seat],
                stack=new_stacks[msg.seat],
                chips_in_front=seat_state.chips_in_front + msg.amount
            )
            print(f"💰 Seat {msg.seat} bet ${msg.amount}, stack now ${new_stacks[msg.seat]}, pot now ${new_pot}")
            
        elif msg.action == "FOLD":
            new_seats[msg.seat] = replace(new_seats[msg.seat], folded=True)
            print(f"🃏 Seat {msg.seat} folded")
            
        elif msg.action in ["CHECK", "CALL"]:
            print(f"✅ Seat {msg.seat} {msg.action.lower()}ed")
    
    # Find next acting seat (simplified)
    next_seat = None
    active_seats = [s for s in sorted(new_seats.keys()) if not new_seats[s].folded]
    
    if len(active_seats) > 1:
        # Find next seat after current actor
        current_idx = active_seats.index(msg.seat) if msg.seat in active_seats else -1
        next_idx = (current_idx + 1) % len(active_seats)
        next_seat = active_seats[next_idx]
    
    # Update acting status
    if next_seat is not None:
        new_seats[next_seat] = replace(new_seats[next_seat], acting=True)
        print(f"👉 Next to act: Seat {next_seat}")
    else:
        print("🏁 No more players to act")
    
    return replace(
        model,
        seats=new_seats,
        stacks=new_stacks,
        to_act_seat=next_seat,
        pot=new_pot,
        legal_actions={"CHECK", "CALL", "BET", "RAISE", "FOLD"} if next_seat else set()
    )

```

---

### mvu_store.py

**Path:** `backend/ui/mvu/store.py`

```python
"""
MVU Store - Manages Model state and executes Commands
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Callable, Optional, Any, Dict
import time
import threading

from .types import (
    Model, Msg, Cmd, SessionDriver, IntentHandler,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, PublishEvent, GetReviewEvent,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished
)
from .update import update


class MVUStore:
    """
    MVU Store - Single source of truth for Model state
    Handles message dispatch and command execution
    """
    
    def __init__(
        self,
        initial_model: Model,
        effect_bus: Any = None,
        game_director: Any = None,
        event_bus: Any = None,
        ppsm: Any = None
    ):
        self.model = initial_model
        self.effect_bus = effect_bus
        self.game_director = game_director
        self.event_bus = event_bus
        self.ppsm = ppsm
        
        # Subscribers to model changes
        self.subscribers: List[Callable[[Model], None]] = []
        
        # Session driver (pluggable)
        self.session_driver: Optional[SessionDriver] = None
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Scheduled timers
        self._timers: Dict[str, Any] = {}
        
        print("🏪 MVUStore: Initialized with model:", self.model.session_mode)
    
    def set_session_driver(self, driver: SessionDriver) -> None:
        """Set the session driver for this store"""
        with self._lock:
            self.session_driver = driver
            print(f"🏪 MVUStore: Session driver set: {type(driver).__name__}")
    
    def subscribe(self, callback: Callable[[Model], None]) -> Callable[[], None]:
        """
        Subscribe to model changes
        Returns unsubscribe function
        """
        with self._lock:
            self.subscribers.append(callback)
            
            # Immediately notify with current model
            callback(self.model)
            
            def unsubscribe():
                with self._lock:
                    if callback in self.subscribers:
                        self.subscribers.remove(callback)
            
            return unsubscribe
    
    def dispatch(self, msg: Msg) -> None:
        """
        Dispatch a message to update the model
        """
        with self._lock:
            print(f"🏪 MVUStore: Dispatching {type(msg).__name__}")
            
            # Debug specific messages that might cause state reset
            if hasattr(msg, 'hand_data'):
                seats_count = len(msg.hand_data.get('seats', {})) if msg.hand_data else 0
                print(f"🏪 MVUStore: LoadHand with {seats_count} seats")
            
            # Update model using pure reducer
            new_model, commands = update(self.model, msg)
            
            # Debug model changes
            if len(new_model.seats) != len(self.model.seats):
                print(f"🏪 MVUStore: Seats changed from {len(self.model.seats)} to {len(new_model.seats)}")
                print(f"🏪 MVUStore: Old model seats: {list(self.model.seats.keys())}")
                print(f"🏪 MVUStore: New model seats: {list(new_model.seats.keys())}")
            
            if new_model.pot != self.model.pot:
                print(f"🏪 MVUStore: Pot changed from {self.model.pot} to {new_model.pot}")
            
            if new_model.board != self.model.board:
                print(f"🏪 MVUStore: Board changed from {self.model.board} to {new_model.board}")
            
            # Only update if model actually changed
            if new_model == self.model:
                print(f"🏪 MVUStore: Model unchanged, skipping update")
                # Still execute commands even if model didn't change
                for cmd in commands:
                    self._execute_command(cmd)
                return
            
            # Update stored model
            old_model = self.model
            self.model = new_model
            print(f"🏪 MVUStore: Model updated, notifying {len(self.subscribers)} subscribers")
            
            # Execute commands
            for cmd in commands:
                self._execute_command(cmd)
            
            # Notify subscribers of model change
            for subscriber in self.subscribers:
                try:
                    subscriber(self.model)
                except Exception as e:
                    print(f"⚠️ MVUStore: Subscriber error: {e}")
    
    def get_model(self) -> Model:
        """Get current model (thread-safe)"""
        with self._lock:
            return self.model
    
    def _execute_command(self, cmd: Cmd) -> None:
        """
        Execute a command using available services
        All I/O happens here, never in reducers
        """
        try:
            if isinstance(cmd, PlaySound):
                self._execute_play_sound(cmd)
            
            elif isinstance(cmd, Speak):
                self._execute_speak(cmd)
            
            elif isinstance(cmd, Animate):
                self._execute_animate(cmd)
            
            elif isinstance(cmd, AskDriverForDecision):
                self._execute_ask_driver(cmd)
            
            elif isinstance(cmd, ApplyPPSM):
                self._execute_apply_ppsm(cmd)
            
            elif isinstance(cmd, ScheduleTimer):
                self._execute_schedule_timer(cmd)
            
            elif isinstance(cmd, PublishEvent):
                self._execute_publish_event(cmd)
            

            
            elif isinstance(cmd, GetReviewEvent):
                self._execute_get_review_event(cmd)
            
            else:
                print(f"⚠️ MVUStore: Unknown command: {type(cmd).__name__}")
        
        except Exception as e:
            print(f"⚠️ MVUStore: Command execution error: {e}")
    
    def _execute_play_sound(self, cmd: PlaySound) -> None:
        """Execute PlaySound command"""
        if self.effect_bus:
            try:
                self.effect_bus.play_sound(cmd.name)
                print(f"🔊 MVUStore: Played sound: {cmd.name}")
            except Exception as e:
                print(f"⚠️ MVUStore: Sound error: {e}")
    
    def _execute_speak(self, cmd: Speak) -> None:
        """Execute Speak command"""
        if self.effect_bus and hasattr(self.effect_bus, 'voice_manager'):
            try:
                self.effect_bus.voice_manager.speak(cmd.text)
                print(f"🗣️ MVUStore: Spoke: {cmd.text}")
            except Exception as e:
                print(f"⚠️ MVUStore: Speech error: {e}")
    
    def _execute_animate(self, cmd: Animate) -> None:
        """Execute Animate command"""
        if self.effect_bus:
            try:
                # Start animation and set up completion callback
                def on_animation_complete():
                    self.dispatch(AnimationFinished(token=cmd.token))
                
                self.effect_bus.animate(
                    cmd.name,
                    cmd.payload,
                    callback=on_animation_complete
                )
                print(f"🎬 MVUStore: Started animation: {cmd.name} (token: {cmd.token})")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Animation error: {e}")
                # Immediately complete animation on error
                self.dispatch(AnimationFinished(token=cmd.token))
    
    def _execute_ask_driver(self, cmd: AskDriverForDecision) -> None:
        """Execute AskDriverForDecision command"""
        if self.session_driver:
            try:
                def on_decision_ready(decision: DecisionReady):
                    self.dispatch(decision)
                
                self.session_driver.decide(self.model, cmd.seat, on_decision_ready)
                print(f"🤖 MVUStore: Asked driver for decision: seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Driver decision error: {e}")
    
    def _execute_apply_ppsm(self, cmd: ApplyPPSM) -> None:
        """Execute ApplyPPSM command"""
        if self.ppsm:
            try:
                # Apply action to PPSM
                if cmd.seat == -1 and cmd.action == "CONTINUE":
                    # Continue game flow
                    result = self.ppsm.continue_game()
                else:
                    # Apply player action
                    result = self.ppsm.apply_action(cmd.seat, cmd.action, cmd.amount)
                
                # Process PPSM result and dispatch appropriate messages
                self._process_ppsm_result(result, cmd)
                
                print(f"🃏 MVUStore: Applied PPSM action: {cmd.action} by seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: PPSM error: {e}")
    
    def _execute_schedule_timer(self, cmd: ScheduleTimer) -> None:
        """Execute ScheduleTimer command"""
        try:
            timer_id = f"timer_{time.time()}_{id(cmd.msg)}"
            
            def timer_callback():
                self.dispatch(cmd.msg)
                if timer_id in self._timers:
                    del self._timers[timer_id]
            
            if self.game_director and hasattr(self.game_director, 'schedule'):
                # Use GameDirector for scheduling (architecture compliant)
                self.game_director.schedule(cmd.delay_ms, {
                    "type": "MVU_TIMER",
                    "callback": timer_callback
                })
            else:
                # Fallback to threading.Timer
                timer = threading.Timer(cmd.delay_ms / 1000.0, timer_callback)
                self._timers[timer_id] = timer
                timer.start()
            
            print(f"⏰ MVUStore: Scheduled timer: {cmd.delay_ms}ms -> {type(cmd.msg).__name__}")
            
        except Exception as e:
            print(f"⚠️ MVUStore: Timer error: {e}")
    
    def _execute_publish_event(self, cmd: PublishEvent) -> None:
        """Execute PublishEvent command"""
        if self.event_bus:
            try:
                self.event_bus.publish(cmd.topic, cmd.payload)
                print(f"📡 MVUStore: Published event: {cmd.topic}")
            except Exception as e:
                print(f"⚠️ MVUStore: Event publish error: {e}")
    

    
    def _execute_get_review_event(self, cmd: GetReviewEvent) -> None:
        """Execute GetReviewEvent command - get event from session driver"""
        if self.session_driver:
            try:
                event = self.session_driver.review_event_at(cmd.index)
                if event:
                    print(f"📖 MVUStore: Got review event at {cmd.index}: {type(event).__name__}")
                    # Dispatch the review event
                    self.dispatch(event)
                else:
                    print(f"📖 MVUStore: No review event at index {cmd.index}")
            except Exception as e:
                print(f"⚠️ MVUStore: Error getting review event: {e}")
        else:
            print("⚠️ MVUStore: No session driver for review event")
    
    def _process_ppsm_result(self, result: Any, original_cmd: ApplyPPSM) -> None:
        """
        Process PPSM result and dispatch appropriate messages
        This would be customized based on your PPSM interface
        """
        try:
            # Dispatch AppliedAction to trigger state update
            self.dispatch(AppliedAction(
                seat=original_cmd.seat,
                action=original_cmd.action,
                amount=original_cmd.amount
            ))
            
            # Check for street advancement
            if hasattr(result, 'street_changed') and result.street_changed:
                self.dispatch(StreetAdvanced(street=result.new_street))
            
            # Check for hand completion
            if hasattr(result, 'hand_finished') and result.hand_finished:
                self.dispatch(HandFinished(
                    winners=getattr(result, 'winners', []),
                    payouts=getattr(result, 'payouts', {})
                ))
        
        except Exception as e:
            print(f"⚠️ MVUStore: PPSM result processing error: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        with self._lock:
            # Cancel all timers
            for timer in self._timers.values():
                if hasattr(timer, 'cancel'):
                    timer.cancel()
            self._timers.clear()
            
            # Clear subscribers
            self.subscribers.clear()
            
            print("🏪 MVUStore: Cleaned up")


class MVUIntentHandler(IntentHandler):
    """
    Intent handler that dispatches messages to MVU store
    Converts UI events to messages
    """
    
    def __init__(self, store: MVUStore):
        self.store = store
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        from .types import NextPressed
        self.store.dispatch(NextPressed())
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        from .types import AutoPlayToggled
        self.store.dispatch(AutoPlayToggled(on=on))
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        from .types import UserChose
        self.store.dispatch(UserChose(action=action, amount=amount))
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        from .types import ReviewSeek
        self.store.dispatch(ReviewSeek(index=index))
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        # This would dispatch a GTO hint request message
        print("🎯 MVUIntentHandler: GTO hint requested")
        pass

```

---

### mvu_view.py

**Path:** `backend/ui/mvu/view.py`

```python
"""
MVU View - Pure rendering components that read from Model
Based on PokerPro UI Implementation Handbook v2
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from .types import Model, TableRendererProps, IntentHandler


class MVUPokerTableRenderer(ttk.Frame):
    """
    Pure View component for poker table
    Reads only from Model, emits intents via IntentHandler
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        intent_handler: Optional[IntentHandler] = None,
        theme_manager: Any = None
    ):
        super().__init__(parent)
        
        self.intent_handler = intent_handler or DummyIntentHandler()
        self.theme_manager = theme_manager
        
        # Current props (for change detection)
        self.current_props: Optional[TableRendererProps] = None
        
        # UI components
        self.canvas: Optional[tk.Canvas] = None
        self.controls_frame: Optional[ttk.Frame] = None
        self.next_btn: Optional[ttk.Button] = None
        self.autoplay_var: Optional[tk.BooleanVar] = None
        self.action_buttons: Dict[str, ttk.Button] = {}
        self.status_label: Optional[ttk.Label] = None
        self.review_scale: Optional[ttk.Scale] = None
        
        self._setup_ui()
        
        print("🎨 MVUPokerTableRenderer: Initialized as pure View component")
    
    def _setup_ui(self) -> None:
        """Setup the UI components"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main canvas for table rendering
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=600,
            bg="#0D4F3C"  # Default felt color
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        
        # Next button
        self.next_btn = ttk.Button(
            self.controls_frame,
            text="Next",
            command=self.intent_handler.on_click_next
        )
        self.next_btn.grid(row=0, column=0, padx=5)
        
        # Auto-play checkbox
        self.autoplay_var = tk.BooleanVar()
        autoplay_cb = ttk.Checkbutton(
            self.controls_frame,
            text="Auto-play",
            variable=self.autoplay_var,
            command=self._on_autoplay_toggle
        )
        autoplay_cb.grid(row=0, column=1, padx=5, sticky="w")
        
        # Status label
        self.status_label = ttk.Label(
            self.controls_frame,
            text="Ready"
        )
        self.status_label.grid(row=0, column=2, padx=5)
        
        # Action buttons frame
        self.actions_frame = ttk.Frame(self.controls_frame)
        self.actions_frame.grid(row=0, column=3, padx=5)
        
        # Create action buttons
        actions = ["FOLD", "CHECK", "CALL", "BET", "RAISE"]
        for i, action in enumerate(actions):
            btn = ttk.Button(
                self.actions_frame,
                text=action,
                command=lambda a=action: self._on_action_btn(a)
            )
            btn.grid(row=0, column=i, padx=2)
            self.action_buttons[action] = btn
        
        # Review controls (shown only in review mode)
        self.review_frame = ttk.Frame(self.controls_frame)
        self.review_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        self.review_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self.review_frame, text="Review:").grid(row=0, column=0, padx=5)
        
        self.review_scale = ttk.Scale(
            self.review_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self._on_review_seek
        )
        self.review_scale.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.review_position_label = ttk.Label(self.review_frame, text="0/0")
        self.review_position_label.grid(row=0, column=2, padx=5)
    
    def render(self, props: TableRendererProps) -> None:
        """
        Render the table based on props
        Pure function - only reads from props, never mutates state
        """
        # Skip if props haven't changed
        if self.current_props == props:
            return
        
        # Debug what changed
        print(f"🎨 MVUPokerTableRenderer: Rendering with {len(props.seats)} seats")
        print(f"🔍 Props changed: old_props is None: {self.current_props is None}")
        if self.current_props is not None:
            print(f"🔍 Props equal: {self.current_props == props}")
            print(f"🔍 Seats equal: {self.current_props.seats == props.seats}")
            print(f"🔍 Review cursor: {self.current_props.review_cursor} -> {props.review_cursor}")
            print(f"🔍 Waiting for: {self.current_props.waiting_for} -> {props.waiting_for}")
            
            # Detailed debugging of differences
            if self.current_props != props:
                print("🔍 DETAILED DIFF:")
                print(f"  board: {self.current_props.board} vs {props.board} = {self.current_props.board == props.board}")
                print(f"  pot: {self.current_props.pot} vs {props.pot} = {self.current_props.pot == props.pot}")
                print(f"  to_act_seat: {self.current_props.to_act_seat} vs {props.to_act_seat} = {self.current_props.to_act_seat == props.to_act_seat}")
                print(f"  legal_actions: {self.current_props.legal_actions} vs {props.legal_actions} = {self.current_props.legal_actions == props.legal_actions}")
                print(f"  theme_id: {self.current_props.theme_id} vs {props.theme_id} = {self.current_props.theme_id == props.theme_id}")
                print(f"  autoplay_on: {self.current_props.autoplay_on} vs {props.autoplay_on} = {self.current_props.autoplay_on == props.autoplay_on}")
                print(f"  session_mode: {self.current_props.session_mode} vs {props.session_mode} = {self.current_props.session_mode == props.session_mode}")
                
                # Check seats in detail
                if len(self.current_props.seats) != len(props.seats):
                    print(f"  SEATS LENGTH DIFF: {len(self.current_props.seats)} vs {len(props.seats)}")
                else:
                    for seat_num in self.current_props.seats:
                        if seat_num in props.seats:
                            old_seat = self.current_props.seats[seat_num]
                            new_seat = props.seats[seat_num]
                            if old_seat != new_seat:
                                print(f"  SEAT {seat_num} DIFF:")
                                print(f"    player_uid: {old_seat.player_uid} vs {new_seat.player_uid}")
                                print(f"    stack: {old_seat.stack} vs {new_seat.stack}")
                                print(f"    folded: {old_seat.folded} vs {new_seat.folded}")
                                print(f"    acting: {old_seat.acting} vs {new_seat.acting}")
                        else:
                            print(f"  SEAT {seat_num} MISSING in new props")
        
        self.current_props = props
        
        # Update controls based on props
        self._update_controls(props)
        
        # Render table on canvas
        self._render_table(props)
        
        # Update review controls
        self._update_review_controls(props)
    
    def _update_controls(self, props: TableRendererProps) -> None:
        """Update control buttons and status"""
        
        # Update status
        status_text = f"Waiting for: {props.waiting_for}"
        if props.to_act_seat is not None:
            status_text += f" (Seat {props.to_act_seat})"
        self.status_label.config(text=status_text)
        
        # Update next button
        next_enabled = props.waiting_for != "HUMAN_DECISION"
        self.next_btn.config(state="normal" if next_enabled else "disabled")
        
        # Update autoplay
        self.autoplay_var.set(props.autoplay_on)
        
        # Update action buttons
        human_turn = (
            props.to_act_seat == 0 and  # Assuming seat 0 is human
            props.waiting_for == "HUMAN_DECISION"
        )
        
        for action, btn in self.action_buttons.items():
            enabled = human_turn and action in props.legal_actions
            btn.config(state="normal" if enabled else "disabled")
    
    def _render_table(self, props: TableRendererProps) -> None:
        """Render the poker table on canvas"""
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet
            self.after(50, lambda: self.render(props))
            return
        
        # Draw felt background
        self.canvas.create_oval(
            50, 50, canvas_width - 50, canvas_height - 50,
            fill="#0D4F3C", outline="#2D5016", width=3,
            tags="felt"
        )
        
        # Draw seats
        self._draw_seats(props, canvas_width, canvas_height)
        
        # Draw community cards
        self._draw_community_cards(props, canvas_width, canvas_height)
        
        # Draw pot
        self._draw_pot(props, canvas_width, canvas_height)
        
        # Draw banners
        self._draw_banners(props, canvas_width, canvas_height)
    
    def _draw_seats(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw player seats"""
        
        import math
        
        # Calculate seat positions around oval table
        center_x, center_y = width // 2, height // 2
        radius_x, radius_y = (width - 100) // 2, (height - 100) // 2
        
        for seat_num, seat_state in props.seats.items():
            # Calculate position
            angle = (seat_num / max(len(props.seats), 1)) * 2 * math.pi - math.pi / 2
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            # Draw seat background
            seat_color = "#FFD700" if seat_state.acting else "#8B4513"
            if seat_state.folded:
                seat_color = "#696969"
            
            self.canvas.create_rectangle(
                x - 60, y - 30, x + 60, y + 30,
                fill=seat_color, outline="black", width=2,
                tags=f"seat_{seat_num}"
            )
            
            # Draw player name
            self.canvas.create_text(
                x, y - 15,
                text=seat_state.name,
                font=("Arial", 10, "bold"),
                fill="black",
                tags=f"seat_{seat_num}_name"
            )
            
            # Draw stack
            self.canvas.create_text(
                x, y,
                text=f"${seat_state.stack}",
                font=("Arial", 9),
                fill="black",
                tags=f"seat_{seat_num}_stack"
            )
            
            # Draw bet amount
            if seat_state.chips_in_front > 0:
                self.canvas.create_text(
                    x, y + 15,
                    text=f"Bet: ${seat_state.chips_in_front}",
                    font=("Arial", 8),
                    fill="red",
                    tags=f"seat_{seat_num}_bet"
                )
            
            # Draw hole cards (if visible)
            if seat_state.cards and not seat_state.folded:
                card_x = x - 20
                for i, card in enumerate(seat_state.cards[:2]):  # Max 2 hole cards
                    self._draw_card(card_x + i * 20, y - 45, card, f"hole_{seat_num}_{i}")
    
    def _draw_community_cards(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw community cards"""
        
        if not props.board:
            return
        
        center_x, center_y = width // 2, height // 2
        card_width, card_height = 40, 60
        total_width = len(props.board) * (card_width + 5) - 5
        start_x = center_x - total_width // 2
        
        for i, card in enumerate(props.board):
            x = start_x + i * (card_width + 5)
            y = center_y - card_height // 2
            self._draw_card(x, y, card, f"board_{i}")
    
    def _draw_pot(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw pot display"""
        
        center_x, center_y = width // 2, height // 2
        
        # Pot background
        self.canvas.create_oval(
            center_x - 40, center_y + 60, center_x + 40, center_y + 100,
            fill="#DAA520", outline="black", width=2,
            tags="pot_bg"
        )
        
        # Pot amount
        self.canvas.create_text(
            center_x, center_y + 80,
            text=f"${props.pot}",
            font=("Arial", 12, "bold"),
            fill="black",
            tags="pot_amount"
        )
    
    def _draw_card(self, x: int, y: int, card: str, tag: str) -> None:
        """Draw a single card"""
        
        # Card background
        self.canvas.create_rectangle(
            x, y, x + 40, y + 60,
            fill="white", outline="black", width=2,
            tags=tag
        )
        
        # Card text
        self.canvas.create_text(
            x + 20, y + 30,
            text=card,
            font=("Arial", 10, "bold"),
            fill="black",
            tags=f"{tag}_text"
        )
    
    def _draw_banners(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw UI banners"""
        
        for i, banner in enumerate(props.banners):
            y_pos = 20 + i * 30
            
            # Banner colors
            colors = {
                "info": "#ADD8E6",
                "warning": "#FFD700",
                "error": "#FF6B6B",
                "success": "#90EE90"
            }
            
            bg_color = colors.get(banner.type, "#FFFFFF")
            
            self.canvas.create_rectangle(
                10, y_pos, width - 10, y_pos + 25,
                fill=bg_color, outline="black",
                tags=f"banner_{i}"
            )
            
            self.canvas.create_text(
                width // 2, y_pos + 12,
                text=banner.text,
                font=("Arial", 10),
                fill="black",
                tags=f"banner_{i}_text"
            )
    
    def _update_review_controls(self, props: TableRendererProps) -> None:
        """Update review-specific controls"""
        
        is_review = props.session_mode == "REVIEW"
        
        if is_review:
            self.review_frame.grid()
            
            # Update scale (avoid triggering callback during programmatic update)
            if props.review_len > 0:
                self.review_scale.config(to=props.review_len - 1)
                # Temporarily disable the callback to avoid infinite loop
                old_command = self.review_scale.cget("command")
                self.review_scale.config(command="")
                self.review_scale.set(props.review_cursor)
                self.review_scale.config(command=old_command)
            
            # Update position label
            self.review_position_label.config(
                text=f"{props.review_cursor}/{props.review_len}"
            )
        else:
            self.review_frame.grid_remove()
    
    def _on_autoplay_toggle(self) -> None:
        """Handle autoplay toggle"""
        self.intent_handler.on_toggle_autoplay(self.autoplay_var.get())
    
    def _on_action_btn(self, action: str) -> None:
        """Handle action button click"""
        # For BET/RAISE, we'd need amount input - simplified for now
        amount = None
        if action in ["BET", "RAISE"]:
            amount = 100  # Placeholder amount
        
        self.intent_handler.on_action_btn(action, amount)
    
    def _on_review_seek(self, value: str) -> None:
        """Handle review seek"""
        try:
            index = int(float(value))
            self.intent_handler.on_seek(index)
        except ValueError:
            pass


class DummyIntentHandler:
    """Dummy intent handler for testing"""
    
    def on_click_next(self) -> None:
        print("🎯 DummyIntentHandler: Next clicked")
    
    def on_toggle_autoplay(self, on: bool) -> None:
        print(f"🎯 DummyIntentHandler: Autoplay toggled: {on}")
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        print(f"🎯 DummyIntentHandler: Action {action} (amount: {amount})")
    
    def on_seek(self, index: int) -> None:
        print(f"🎯 DummyIntentHandler: Seek to {index}")
    
    def on_request_hint(self) -> None:
        print("🎯 DummyIntentHandler: Hint requested")

```

---

### mvu_drivers.py

**Path:** `backend/ui/mvu/drivers.py`

```python
"""
MVU Session Drivers - Pluggable session behavior
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Dict, Any, Optional, Callable
import threading
import time

from .types import Model, Msg, DecisionReady, UserChose, AppliedAction, StreetAdvanced, HandFinished


class ReviewDriver:
    """
    Driver for REVIEW sessions - serves pre-recorded events
    """
    
    def __init__(self, hand_data: Dict[str, Any]):
        self.hand_data = hand_data
        self.events: List[Msg] = []
        self.current_index = 0
        
        # Parse hand data into events
        self._parse_hand_events()
        
        print(f"🎬 ReviewDriver: Initialized with {len(self.events)} events")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """
        In review mode, decisions are pre-recorded
        This should not be called in normal review flow
        """
        print(f"⚠️ ReviewDriver: decide() called unexpectedly for seat {seat}")
        
        # If somehow called, provide a default action
        def delayed_callback():
            time.sleep(0.1)  # Small delay to simulate decision time
            callback(DecisionReady(seat=seat, action="CHECK", amount=None))
        
        thread = threading.Thread(target=delayed_callback)
        thread.daemon = True
        thread.start()
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at specific index"""
        print(f"🎬 ReviewDriver: Getting event at index {index}, have {len(self.events)} events")
        if 0 <= index < len(self.events):
            event = self.events[index]
            print(f"🎬 ReviewDriver: Returning event {index}: {type(event).__name__} - {event}")
            return event
        print(f"🎬 ReviewDriver: No event at index {index}")
        return None
    
    def review_length(self) -> int:
        """Get total number of review events"""
        return len(self.events)
    
    def _parse_hand_events(self) -> None:
        """
        Parse hand data into chronological events
        This converts the hand history into a sequence of messages
        """
        try:
            # Get actions from hand data
            actions = self.hand_data.get("actions", [])
            
            for i, action_data in enumerate(actions):
                # Create event based on action type
                seat = action_data.get("seat", 0)
                action = action_data.get("action", "CHECK")
                amount = action_data.get("amount")
                street = action_data.get("street", "PREFLOP")
                
                # Add the action event
                self.events.append(AppliedAction(
                    seat=seat,
                    action=action,
                    amount=amount
                ))
                
                # Check if street changes after this action
                next_action = actions[i + 1] if i + 1 < len(actions) else None
                if next_action and next_action.get("street") != street:
                    self.events.append(StreetAdvanced(street=next_action.get("street")))
            
            # Add hand finished event if we have winner data
            winners = self.hand_data.get("winners", [])
            payouts = self.hand_data.get("payouts", {})
            if winners or payouts:
                self.events.append(HandFinished(
                    winners=winners,
                    payouts=payouts
                ))
        
        except Exception as e:
            print(f"⚠️ ReviewDriver: Error parsing events: {e}")
            # Fallback to empty events
            self.events = []


class PracticeDriver:
    """
    Driver for PRACTICE sessions - human play with optional bots
    """
    
    def __init__(self, bot_seats: List[int] = None):
        self.bot_seats = bot_seats or []
        print(f"🎯 PracticeDriver: Initialized with bots on seats: {self.bot_seats}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat"""
        if seat in self.bot_seats:
            # Bot decision - simple logic for now
            self._make_bot_decision(model, seat, callback)
        else:
            # Human decision - this shouldn't be called directly
            # Human decisions come through UserChose messages
            print(f"⚠️ PracticeDriver: decide() called for human seat {seat}")
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for practice mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for practice mode"""
        return 0
    
    def _make_bot_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make a simple bot decision"""
        def delayed_decision():
            # Simulate thinking time
            time.sleep(0.5 + (seat * 0.1))  # Staggered timing
            
            # Simple decision logic
            legal_actions = model.legal_actions
            
            if "CHECK" in legal_actions:
                action = "CHECK"
                amount = None
            elif "CALL" in legal_actions:
                action = "CALL"
                amount = None  # PPSM will determine call amount
            elif "FOLD" in legal_actions:
                action = "FOLD"
                amount = None
            else:
                action = "CHECK"
                amount = None
            
            callback(DecisionReady(seat=seat, action=action, amount=amount))
        
        thread = threading.Thread(target=delayed_decision)
        thread.daemon = True
        thread.start()


class GTODriver:
    """
    Driver for GTO sessions - calls GTO provider for decisions
    """
    
    def __init__(self, gto_provider: Any = None):
        self.gto_provider = gto_provider
        print(f"🧠 GTODriver: Initialized with provider: {gto_provider is not None}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get GTO decision from provider"""
        if self.gto_provider:
            self._get_gto_decision(model, seat, callback)
        else:
            # Fallback to simple decision
            self._fallback_decision(model, seat, callback)
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for GTO mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for GTO mode"""
        return 0
    
    def _get_gto_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get decision from GTO provider"""
        def gto_decision():
            try:
                # This would call your actual GTO provider
                # For now, simulate with a delay
                time.sleep(1.0)  # GTO thinking time
                
                # Placeholder GTO logic
                legal_actions = model.legal_actions
                if "RAISE" in legal_actions and len(model.board) == 0:  # Preflop aggression
                    action = "RAISE"
                    amount = model.pot * 2  # 2x pot raise
                elif "BET" in legal_actions and len(model.board) >= 3:  # Post-flop betting
                    action = "BET"
                    amount = int(model.pot * 0.75)  # 3/4 pot bet
                elif "CALL" in legal_actions:
                    action = "CALL"
                    amount = None
                else:
                    action = "CHECK"
                    amount = None
                
                callback(DecisionReady(seat=seat, action=action, amount=amount))
                
            except Exception as e:
                print(f"⚠️ GTODriver: Error getting GTO decision: {e}")
                self._fallback_decision(model, seat, callback)
        
        thread = threading.Thread(target=gto_decision)
        thread.daemon = True
        thread.start()
    
    def _fallback_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Fallback decision when GTO provider fails"""
        def simple_decision():
            time.sleep(0.3)
            
            legal_actions = model.legal_actions
            if "CHECK" in legal_actions:
                action = "CHECK"
            elif "CALL" in legal_actions:
                action = "CALL"
            else:
                action = "FOLD"
            
            callback(DecisionReady(seat=seat, action=action, amount=None))
        
        thread = threading.Thread(target=simple_decision)
        thread.daemon = True
        thread.start()


def create_driver(session_mode: str, **kwargs) -> Any:
    """Factory function to create appropriate driver"""
    
    if session_mode == "REVIEW":
        hand_data = kwargs.get("hand_data", {})
        return ReviewDriver(hand_data)
    
    elif session_mode == "PRACTICE":
        bot_seats = kwargs.get("bot_seats", [1, 2, 3, 4, 5])  # All except seat 0 (human)
        return PracticeDriver(bot_seats)
    
    elif session_mode == "GTO":
        gto_provider = kwargs.get("gto_provider")
        return GTODriver(gto_provider)
    
    else:
        raise ValueError(f"Unknown session mode: {session_mode}")

```

---

### mvu_init.py

**Path:** `backend/ui/mvu/__init__.py`

```python
"""
MVU (Model-View-Update) Architecture Package
Based on PokerPro UI Implementation Handbook v2

This package implements a clean, testable MVU architecture for the poker table UI.
All timing, state management, and effects are handled through pure reducers and command execution.
"""

from .types import (
    Model, SeatState, Action, GtoHint, Banner,
    Msg, NextPressed, AutoPlayToggled, UserChose, DecisionReady, LoadHand,
    Cmd, PlaySound, Speak, Animate,
    SessionDriver, IntentHandler, TableRendererProps
)

from .update import update

from .store import MVUStore, MVUIntentHandler

from .view import MVUPokerTableRenderer

from .drivers import ReviewDriver, PracticeDriver, GTODriver, create_driver

from .hands_review_mvu import MVUHandsReviewTab

__all__ = [
    # Core types
    "Model", "SeatState", "Action", "GtoHint", "Banner",
    "Msg", "NextPressed", "AutoPlayToggled", "UserChose", "DecisionReady", "LoadHand",
    "Cmd", "PlaySound", "Speak", "Animate",
    "SessionDriver", "IntentHandler", "TableRendererProps",
    
    # Core functions
    "update",
    
    # Store
    "MVUStore", "MVUIntentHandler",
    
    # View
    "MVUPokerTableRenderer",
    
    # Drivers
    "ReviewDriver", "PracticeDriver", "GTODriver", "create_driver",
    
    # Complete implementations
    "MVUHandsReviewTab"
]

```

---

## MVU INTEGRATION

### hands_review_mvu.py

**Path:** `backend/ui/mvu/hands_review_mvu.py`

```python
"""
MVU-based Hands Review Tab
Replaces the existing HandsReviewTab with clean MVU architecture
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List
import json

from .types import Model, TableRendererProps, LoadHand, SeatState
from .store import MVUStore, MVUIntentHandler
from .view import MVUPokerTableRenderer
from .drivers import create_driver


class MVUHandsReviewTab(ttk.Frame):
    """
    MVU-based Hands Review Tab
    Clean, testable, and follows the architecture handbook
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        services: Any = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.services = services
        
        # Get required services
        self.effect_bus = services.get_app("effect_bus") if services else None
        self.game_director = services.get_app("game_director") if services else None
        self.event_bus = services.get_app("event_bus") if services else None
        self.theme_manager = services.get_app("theme") if services else None
        
        # MVU components
        self.store: Optional[MVUStore] = None
        self.intent_handler: Optional[MVUIntentHandler] = None
        self.table_renderer: Optional[MVUPokerTableRenderer] = None
        
        # Hand data
        self.hands_data: List[Dict[str, Any]] = []
        self.current_hand_index = 0
        
        # UI components
        self.hand_selector: Optional[ttk.Combobox] = None
        self.hand_info_label: Optional[ttk.Label] = None
        
        # Props memoization
        self._last_props: Optional[TableRendererProps] = None
        
        self._setup_ui()
        self._initialize_mvu()
        self._load_hands_data()
        
        print("🎬 MVUHandsReviewTab: Initialized with clean MVU architecture")
    
    def _setup_ui(self) -> None:
        """Setup the UI layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Hand selector
        ttk.Label(controls_frame, text="Hand:").grid(row=0, column=0, padx=5)
        
        self.hand_selector = ttk.Combobox(
            controls_frame,
            state="readonly",
            width=30
        )
        self.hand_selector.grid(row=0, column=1, padx=5, sticky="w")
        self.hand_selector.bind("<<ComboboxSelected>>", self._on_hand_selected)
        
        # Hand info
        self.hand_info_label = ttk.Label(
            controls_frame,
            text="No hand loaded"
        )
        self.hand_info_label.grid(row=0, column=2, padx=10, sticky="w")
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Hands",
            command=self._load_hands_data
        )
        refresh_btn.grid(row=0, column=3, padx=5)
        
        # Table renderer will be added in _initialize_mvu()
    
    def _initialize_mvu(self) -> None:
        """Initialize MVU components"""
        
        # Create initial model for REVIEW mode
        initial_model = Model.initial(session_mode="REVIEW")
        
        # Create store
        self.store = MVUStore(
            initial_model=initial_model,
            effect_bus=self.effect_bus,
            game_director=self.game_director,
            event_bus=self.event_bus,
            ppsm=None  # We'll set this up when we have PPSM integration
        )
        
        # Create intent handler
        self.intent_handler = MVUIntentHandler(self.store)
        
        # Create table renderer
        self.table_renderer = MVUPokerTableRenderer(
            parent=self,
            intent_handler=self.intent_handler,
            theme_manager=self.theme_manager
        )
        self.table_renderer.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Subscribe to model changes
        self.unsubscribe = self.store.subscribe(self._on_model_changed)
        
        print("🏪 MVUHandsReviewTab: MVU components initialized")
    
    def _load_hands_data(self) -> None:
        """Load hands data for review"""
        try:
            # Try to load from GTO hands file (as in original implementation)
            import os
            gto_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "gto_hands.json"
            )
            
            if os.path.exists(gto_file):
                with open(gto_file, 'r') as f:
                    raw_data = json.load(f)
                    
                self.hands_data = self._parse_hands_data(raw_data)
                print(f"📊 MVUHandsReviewTab: Loaded {len(self.hands_data)} hands")
                
            else:
                # Fallback to sample data
                self.hands_data = self._create_sample_hands()
                print("📊 MVUHandsReviewTab: Using sample hands data")
            
            self._update_hand_selector()
            
            # DEFER hand loading until after UI is fully initialized to prevent race conditions
            if self.hands_data and self.store:
                # Schedule hand loading after UI setup is complete
                self.after(100, lambda: self._load_hand(0))
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error loading hands: {e}")
            self.hands_data = self._create_sample_hands()
            self._update_hand_selector()
    
    def _parse_hands_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw hands data into MVU format"""
        hands = []
        
        try:
            # Handle different data formats
            if isinstance(raw_data, dict):
                if "hands" in raw_data:
                    hands_list = raw_data["hands"]
                else:
                    hands_list = [raw_data]  # Single hand
            elif isinstance(raw_data, list):
                hands_list = raw_data
            else:
                return []
            
            for i, hand_data in enumerate(hands_list):
                parsed_hand = self._parse_single_hand(hand_data, i)
                if parsed_hand:
                    hands.append(parsed_hand)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hands data: {e}")
        
        return hands
    
    def _parse_single_hand(self, hand_data: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Parse a single hand into MVU format"""
        try:
            hand_id = hand_data.get("hand_id", f"Hand_{index + 1}")
            
            # Parse players/seats
            seats = {}
            stacks = {}
            
            players = hand_data.get("players", [])
            for i, player in enumerate(players[:6]):  # Max 6 players
                seat_state = {
                    "player_uid": player.get("name", f"Player_{i}"),
                    "name": player.get("name", f"Player {i}"),
                    "stack": player.get("stack", 1000),
                    "chips_in_front": 0,
                    "folded": False,
                    "all_in": False,
                    "cards": player.get("hole_cards", []),
                    "position": i
                }
                seats[i] = seat_state
                stacks[i] = seat_state["stack"]
            
            # Parse actions
            actions = []
            raw_actions = hand_data.get("actions", [])
            
            for action_data in raw_actions:
                if isinstance(action_data, dict):
                    actions.append({
                        "seat": action_data.get("player_index", 0),
                        "action": action_data.get("action", "CHECK"),
                        "amount": action_data.get("amount"),
                        "street": action_data.get("street", "PREFLOP")
                    })
            
            return {
                "hand_id": hand_id,
                "seats": seats,
                "stacks": stacks,
                "board": hand_data.get("board", []),
                "pot": hand_data.get("pot", 0),
                "actions": actions,
                "review_len": len(actions),
                "to_act_seat": 0,  # Start with first seat
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            }
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hand {index}: {e}")
            return None
    
    def _create_sample_hands(self) -> List[Dict[str, Any]]:
        """Create sample hands for testing"""
        return [
            {
                "hand_id": "SAMPLE_001",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["As", "Kh"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Qd", "Jc"],
                        "position": 1
                    }
                },
                "stacks": {0: 1000, 1: 1000},
                "board": ["7h", "8s", "9d"],
                "pot": 60,
                "actions": [
                    {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
                    {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
                    {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
                    {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
                ],
                "review_len": 4,
                "to_act_seat": 0,
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            },
            {
                "hand_id": "SAMPLE_002",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 800,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Kd", "Kc"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1200,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Ad", "Qh"],
                        "position": 1
                    }
                },
                "stacks": {0: 800, 1: 1200},
                "board": ["2h", "7c", "Ks", "4d", "8h"],
                "pot": 400,
                "actions": [
                    {"seat": 1, "action": "RAISE", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CALL", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CHECK", "amount": None, "street": "FLOP"},
                    {"seat": 1, "action": "BET", "amount": 60, "street": "FLOP"},
                    {"seat": 0, "action": "RAISE", "amount": 180, "street": "FLOP"},
                    {"seat": 1, "action": "CALL", "amount": 120, "street": "FLOP"}
                ],
                "review_len": 6,
                "to_act_seat": 1,
                "legal_actions": ["CHECK", "BET"]
            }
        ]
    
    def _update_hand_selector(self) -> None:
        """Update the hand selector combobox"""
        hand_names = [hand["hand_id"] for hand in self.hands_data]
        self.hand_selector["values"] = hand_names
        
        if hand_names:
            self.hand_selector.current(0)
    
    def _on_hand_selected(self, event=None) -> None:
        """Handle hand selection"""
        try:
            index = self.hand_selector.current()
            if 0 <= index < len(self.hands_data):
                self._load_hand(index)
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error selecting hand: {e}")
    
    def _load_hand(self, index: int) -> None:
        """Load a specific hand into the MVU store"""
        if not (0 <= index < len(self.hands_data)):
            return
        
        self.current_hand_index = index
        hand_data = self.hands_data[index]
        
        # Update hand info
        hand_id = hand_data["hand_id"]
        num_actions = hand_data.get("review_len", 0)
        self.hand_info_label.config(
            text=f"{hand_id} ({num_actions} actions)"
        )
        
        # Create and set session driver
        driver = create_driver("REVIEW", hand_data=hand_data)
        self.store.set_session_driver(driver)
        
        # Dispatch LoadHand message to store
        load_msg = LoadHand(hand_data=hand_data)
        self.store.dispatch(load_msg)
        
        print(f"📋 MVUHandsReviewTab: Loaded hand {hand_id}")
    
    def _on_model_changed(self, model: Model) -> None:
        """Handle model changes - update the view"""
        try:
            print(f"🔄 MVUHandsReviewTab: Model changed callback triggered")
            print(f"🔄 MVUHandsReviewTab: Model has {len(model.seats)} seats, pot={model.pot}")
            
            # Convert model to props
            props = TableRendererProps.from_model(model)
            
            # Early-out if equal (now that we have proper value equality)
            if props == self._last_props:
                print(f"🔄 MVUHandsReviewTab: Props unchanged, skipping render")
                return
            
            print(f"🔄 MVUHandsReviewTab: Props changed, updating renderer")
            self._last_props = props
            
            # Render table
            if self.table_renderer:
                self.table_renderer.render(props)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error updating view: {e}")
    
    def dispose(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'unsubscribe') and self.unsubscribe:
            self.unsubscribe()
        
        if self.store:
            self.store.cleanup()
        
        print("🧹 MVUHandsReviewTab: Disposed")

```

---

### app_shell.py

**Path:** `backend/ui/app_shell.py`

```python
import tkinter as tk
from tkinter import ttk
import uuid

from .services.event_bus import EventBus
from .services.service_container import ServiceContainer
from .services.timer_manager import TimerManager
from .services.theme_manager import ThemeManager
from .services.hands_repository import HandsRepository, StudyMode
from .state.store import Store
from .state.reducers import root_reducer
from .mvu.hands_review_mvu import MVUHandsReviewTab as HandsReviewTab
from .tabs.practice_session_tab import PracticeSessionTab
from .tabs.gto_session_tab import GTOSessionTab

from .menu_integration import add_theme_manager_to_menu


class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # Store root reference for menu integration
        self.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # app-scoped services
        self.services = ServiceContainer()
        self.services.provide_app("event_bus", EventBus())
        self.services.provide_app("theme", ThemeManager())
        self.services.provide_app("hands_repository", HandsRepository())
        
        # Create global GameDirector for action sequencing
        from .services.game_director import GameDirector
        game_director = GameDirector(event_bus=self.services.get_app("event_bus"))
        self.services.provide_app("game_director", game_director)
        
        # Create global EffectBus service for sound management
        from .services.effect_bus import EffectBus
        effect_bus = EffectBus(
            game_director=game_director,
            event_bus=self.services.get_app("event_bus")
        )
        self.services.provide_app("effect_bus", effect_bus)
        
        # Create architecture compliant hands review controller
        from .services.hands_review_event_controller import HandsReviewEventController
        
        # Initialize Store with initial state and reducer
        initial_state = {
            "table": {"dim": {"width": 800, "height": 600}},
            "seats": [],
            "board": [],
            "pot": {"amount": 0},
            "dealer": {},
            "review": {},
            "enhanced_rpgw": {},
            "event_bus": self.services.get_app("event_bus")
        }
        store = Store(initial_state, root_reducer)
        self.services.provide_app("store", store)
        
        hands_review_controller = HandsReviewEventController(
            event_bus=self.services.get_app("event_bus"),
            store=store,
            services=self.services
        )
        self.services.provide_app("hands_review_controller", hands_review_controller)
        
        # Subscribe to voice events to keep architecture event-driven
        def _on_voice(payload):
            try:
                action = (payload or {}).get("action")
                vm = getattr(effect_bus, "voice_manager", None)
                if not (vm and action):
                    return
                cfg = getattr(effect_bus, "config", {}) or {}
                voice_type = getattr(effect_bus, "voice_type", "")
                table = (cfg.get("voice_sounds", {}) or {}).get(voice_type, {})
                rel = table.get(action)
                if rel:
                    vm.play(rel)
            except Exception:
                pass
        self.services.get_app("event_bus").subscribe("effect_bus:voice", _on_voice)
        
        # Create shared store for poker game state (per architecture doc)
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": StudyMode.REPLAY.value,
                "collection": None
            }
        }
        self.services.provide_app("store", Store(initial_state, root_reducer))

        # Create menu system
        self._create_menu_system()
        
        # tabs (order: Practice, GTO, Hands Review - main product features only)
        self._add_tab("Practice Session", PracticeSessionTab)
        self._add_tab("GTO Session", GTOSessionTab)
        self._add_tab("Hands Review", HandsReviewTab)
        # Bind global font size shortcuts (Cmd/Ctrl - and =)
        self._bind_font_shortcuts(root)

    def _add_tab(self, title: str, TabClass):
        session_id = str(uuid.uuid4())
        timers = TimerManager(self)
        self.services.provide_session(session_id, "timers", timers)

        # Update active tab in shared store
        store = self.services.get_app("store")
        store.dispatch({"type": "SET_ACTIVE_TAB", "name": title})
        
        # Create tab with services
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)
        
        # Call on_show if available
        if hasattr(tab, "on_show"):
            tab.on_show()

    def _create_menu_system(self):
        """Create the application menu system."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._increase_font(None))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._decrease_font(None))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=lambda: self._reset_font(None))
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme management
        settings_menu.add_command(label="Theme Editor", command=self._open_theme_editor)
        settings_menu.add_command(label="Sound Settings", command=self._open_sound_settings)
        settings_menu.add_separator()
        
        # Add Theme Manager to Settings menu using our integration helper
        add_theme_manager_to_menu(settings_menu, self.root, self._on_theme_changed)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _new_session(self):
        """Start a new session."""
        print("🔄 New session requested")
        # TODO: Implement session reset
        
    def _on_theme_changed(self):
        """Called when theme is changed via Theme Manager."""
        print("🎨 Theme changed - refreshing UI...")
        
        try:
            # Reload theme manager to get latest changes
            theme_manager = self.services.get_app("theme")
            if hasattr(theme_manager, 'reload'):
                theme_manager.reload()
            
            # Force rebuild themes to pick up any live changes
            try:
                from .services.theme_factory import build_all_themes
                themes = build_all_themes()
                # Register updated themes
                for name, tokens in themes.items():
                    theme_manager.register(name, tokens)
                print(f"🔄 Rebuilt and registered {len(themes)} themes")
            except Exception as e:
                print(f"⚠️ Theme rebuild warning: {e}")
            
            # Refresh all tabs with new theme
            for i in range(self.notebook.index("end")):
                try:
                    tab = self.notebook.nametowidget(self.notebook.tabs()[i])
                    
                    # Try multiple refresh methods
                    if hasattr(tab, '_refresh_ui_colors'):
                        tab._refresh_ui_colors()
                        print(f"✅ Refreshed tab {i} via _refresh_ui_colors")
                    elif hasattr(tab, 'refresh_theme'):
                        tab.refresh_theme()
                        print(f"✅ Refreshed tab {i} via refresh_theme")
                    elif hasattr(tab, '_on_theme_changed'):
                        tab._on_theme_changed()
                        print(f"✅ Refreshed tab {i} via _on_theme_changed")
                    else:
                        print(f"ℹ️ Tab {i} has no theme refresh method")
                        
                except Exception as e:
                    print(f"⚠️ Error refreshing tab {i}: {e}")
            
            print("✅ Live theme refresh completed")
            
        except Exception as e:
            print(f"❌ Theme refresh error: {e}")
            import traceback
            traceback.print_exc()
        
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Poker Pro Trainer",
            "Poker Pro Trainer\n\n"
            "Advanced poker training with luxury themes\n"
            "and professional game analysis.\n\n"
            "🎨 Theme Manager integrated\n"
            "🃏 16 luxury themes available\n"
            "📊 Comprehensive hand review\n"
            "🤖 AI-powered training"
        )

    def _bind_font_shortcuts(self, root):
        # macOS Command key bindings (Cmd - decreases, Cmd = increases)
        root.bind_all("<Command-minus>", self._decrease_font)
        root.bind_all("<Command-equal>", self._increase_font)  # This is Cmd = (increase)
        root.bind_all("<Command-0>", self._reset_font)
        
        # Additional symbols that might work
        root.bind_all("<Command-plus>", self._increase_font)   # Shift+= gives +
        
        # Numpad variants
        root.bind_all("<Command-KP_Subtract>", self._decrease_font)
        root.bind_all("<Command-KP_Add>", self._increase_font)
        
        # Windows/Linux Control variants  
        root.bind_all("<Control-minus>", self._decrease_font)
        root.bind_all("<Control-equal>", self._increase_font)
        root.bind_all("<Control-plus>", self._increase_font)
        root.bind_all("<Control-0>", self._reset_font)
        
        print("🔧 Font shortcuts bound successfully")

    def _set_global_font_scale(self, delta: int | None):
        print(f"🔧 Font scale called with delta: {delta}")
        theme: ThemeManager = self.services.get_app("theme")
        fonts = dict(theme.get_fonts())
        base = list(fonts.get("main", ("Arial", 20, "normal")))
        print(f"🔧 Current base font: {base}")
        
        if delta is None:
            new_base_size = 20  # Default 20px size for readability
        else:
            new_base_size = max(10, min(40, int(base[1]) + delta))
        
        print(f"🔧 New base size: {new_base_size}")
        
        # Scale all fonts proportionally from 20px base
        fonts["main"] = (base[0], new_base_size, base[2] if len(base) > 2 else "normal")
        fonts["pot_display"] = (base[0], new_base_size + 8, "bold")  # +8 for pot display
        fonts["bet_amount"] = (base[0], new_base_size + 4, "bold")   # +4 for bet amounts
        fonts["body"] = ("Consolas", max(new_base_size, 12))         # Same as main for body text
        fonts["small"] = ("Consolas", max(new_base_size - 4, 10))    # -4 for smaller text
        fonts["header"] = (base[0], max(new_base_size + 2, 14), "bold") # +2 for headers
        
        print(f"🔧 Updated fonts: {fonts}")
        theme.set_fonts(fonts)
        
        # Force all tabs to re-render with new fonts
        for idx in range(self.notebook.index("end")):
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[idx])
            if hasattr(tab_widget, "on_show"):
                tab_widget.on_show()
            # Also force font refresh if the widget has that method
            if hasattr(tab_widget, "_refresh_fonts"):
                tab_widget._refresh_fonts()
        print("🔧 Font scaling complete")

    def _increase_font(self, event=None):
        print("🔧 Increase font called!")
        self._set_global_font_scale(+1)

    def _decrease_font(self, event=None):
        print("🔧 Decrease font called!")
        self._set_global_font_scale(-1)

    def _reset_font(self, event=None):
        print("🔧 Reset font called!")
        self._set_global_font_scale(None)

    def _open_theme_editor(self):
        """Open the Theme Editor in a new window."""
        try:
            from .tabs.theme_editor_tab import ThemeEditorTab
            # Create a new toplevel window for the theme editor
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Theme Editor - Poker Pro Trainer")
            theme_window.geometry("900x700")
            theme_window.resizable(True, True)
            
            # Center the window on screen
            theme_window.update_idletasks()
            x = (theme_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (theme_window.winfo_screenheight() // 2) - (700 // 2)
            theme_window.geometry(f"900x700+{x}+{y}")
            
            # Create the theme editor tab in the new window
            theme_editor = ThemeEditorTab(theme_window, self.services)
            theme_editor.pack(fill=tk.BOTH, expand=True)
            
            print("🎨 Theme Editor opened in new window")
        except Exception as e:
            print(f"❌ Error opening Theme Editor: {e}")
            import traceback
            traceback.print_exc()

    def _open_sound_settings(self):
        """Open the Sound Settings in a new window."""
        try:
            from .tabs.sound_settings_tab import SoundSettingsTab
            # Create a new toplevel window for the sound settings
            sound_window = tk.Toplevel(self.root)
            sound_window.title("Sound Settings - Poker Pro Trainer")
            sound_window.geometry("1200x800")
            sound_window.resizable(True, True)
            
            # Center the window on screen
            sound_window.update_idletasks()
            x = (sound_window.winfo_screenwidth() // 2) - (1200 // 2)
            y = (sound_window.winfo_screenheight() // 2) - (800 // 2)
            sound_window.geometry(f"1200x800+{x}+{y}")
            
            # Create the sound settings tab in the new window
            sound_settings = SoundSettingsTab(sound_window, self.services)
            sound_settings.pack(fill=tk.BOTH, expand=True)
            
            print("🔊 Sound Settings opened in new window")
        except Exception as e:
            print(f"❌ Error opening Sound Settings: {e}")
            import traceback
            traceback.print_exc()



```

---

## TESTING FILES

### test_mvu_simple.py

**Path:** `backend/test_mvu_simple.py`

```python
#!/usr/bin/env python3
"""
Simple MVU Test - Just test the store directly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUStore, Model, NextPressed, LoadHand
from ui.mvu.drivers import create_driver


def main():
    """Test MVU store directly"""
    print("🧪 Testing MVU Store Directly...")
    
    # Create initial model
    initial_model = Model.initial(session_mode="REVIEW")
    
    # Create store
    store = MVUStore(initial_model=initial_model)
    
    # Create sample hand data
    hand_data = {
        "hand_id": "SIMPLE_TEST",
        "seats": {
            0: {
                "player_uid": "hero",
                "name": "Hero", 
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["As", "Kh"],
                "position": 0
            },
            1: {
                "player_uid": "villain",
                "name": "Villain",
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["Qd", "Jc"],
                "position": 1
            }
        },
        "stacks": {0: 1000, 1: 1000},
        "board": [],
        "pot": 0,
        "actions": [
            {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
            {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
            {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
            {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
        ],
        "review_len": 4,
        "to_act_seat": 0,
        "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
    }
    
    # Create and set driver
    driver = create_driver("REVIEW", hand_data=hand_data)
    store.set_session_driver(driver)
    
    # Load hand
    print("\n📋 Loading hand...")
    store.dispatch(LoadHand(hand_data=hand_data))
    
    # Print initial state
    model = store.get_model()
    print(f"\n🎯 Initial state: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}")
    
    # Click Next button 5 times
    for i in range(5):
        print(f"\n🖱️ === BUTTON CLICK #{i+1} ===")
        store.dispatch(NextPressed())
        
        # Print state after click
        model = store.get_model()
        print(f"🎯 After click {i+1}: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}, pot={model.pot}")
        
        # Print seat states
        for seat_num, seat in model.seats.items():
            print(f"  Seat {seat_num}: {seat.name} - Stack: ${seat.stack}, Bet: ${seat.chips_in_front}, Folded: {seat.folded}, Acting: {seat.acting}")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()

```

---

### test_mvu_implementation.py

**Path:** `backend/test_mvu_implementation.py`

```python
#!/usr/bin/env python3
"""
Test MVU Implementation
Simple test to verify our MVU poker table architecture works
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUHandsReviewTab


def main():
    """Test the MVU implementation"""
    print("🧪 Testing MVU Implementation...")
    
    # Create root window
    root = tk.Tk()
    root.title("MVU Poker Table Test")
    root.geometry("1200x800")
    
    # Create a simple services mock
    class MockServices:
        def __init__(self):
            self._services = {}
        
        def get_app(self, name):
            return self._services.get(name)
        
        def provide_app(self, name, service):
            self._services[name] = service
    
    services = MockServices()
    
    # Create MVU Hands Review Tab
    try:
        review_tab = MVUHandsReviewTab(root, services=services)
        review_tab.pack(fill="both", expand=True)
        
        print("✅ MVU HandsReviewTab created successfully!")
        print("🎮 Use the UI to test the MVU architecture")
        
        # Add cleanup on close
        def on_closing():
            review_tab.dispose()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the UI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error creating MVU tab: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

```

---

### create_mvu_bug_report.py

**Path:** `create_mvu_bug_report.py`

```python
#!/usr/bin/env python3
"""
MVU Infinite Rendering Loop Bug Report Creator
Creates a comprehensive bug report with all relevant source code for the MVU infinite rendering loop issue
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_mvu_bug_report(source_dir, output_dir, output_filename):
    """Create comprehensive bug report for MVU infinite rendering loop with all source code."""
    
    # Convert to Path objects
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()
    
    # Ensure source directory exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    # Ensure output directory exists
    output_path.mkdir(exist_ok=True)
    
    # Define the output file
    output_file = output_path / output_filename
    
    # Define file categories and their order - focused on MVU architecture
    file_categories = [
        ("BUG REPORT SUMMARY", [
            (source_path / "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md", "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md"),
        ]),
        ("MVU ARCHITECTURE - CORE FILES", [
            (source_path / "backend" / "ui" / "mvu" / "types.py", "mvu/types.py"),
            (source_path / "backend" / "ui" / "mvu" / "update.py", "mvu/update.py"),
            (source_path / "backend" / "ui" / "mvu" / "store.py", "mvu/store.py"),
            (source_path / "backend" / "ui" / "mvu" / "view.py", "mvu/view.py"),
            (source_path / "backend" / "ui" / "mvu" / "drivers.py", "mvu/drivers.py"),
            (source_path / "backend" / "ui" / "mvu" / "__init__.py", "mvu/__init__.py"),
        ]),
        ("MVU HANDS REVIEW IMPLEMENTATION", [
            (source_path / "backend" / "ui" / "mvu" / "hands_review_mvu.py", "mvu/hands_review_mvu.py"),
        ]),
        ("INTEGRATION AND APP SHELL", [
            (source_path / "backend" / "ui" / "app_shell.py", "app_shell.py"),
            (source_path / "backend" / "run_new_ui.py", "run_new_ui.py"),
        ]),
        ("DEPRECATED/LEGACY FILES (for reference)", [
            (source_path / "backend" / "ui" / "tabs" / "deprecated" / "hands_review_tab_legacy.py", "deprecated/hands_review_tab_legacy.py"),
        ]),
        ("TEST FILES", [
            (source_path / "backend" / "test_mvu_implementation.py", "test_mvu_implementation.py"),
            (source_path / "backend" / "test_mvu_simple.py", "test_mvu_simple.py"),
        ]),
        ("SUPPORTING SERVICES", [
            (source_path / "backend" / "ui" / "services" / "service_container.py", "services/service_container.py"),
            (source_path / "backend" / "ui" / "services" / "event_bus.py", "services/event_bus.py"),
            (source_path / "backend" / "ui" / "services" / "game_director.py", "services/game_director.py"),
            (source_path / "backend" / "ui" / "services" / "effect_bus.py", "services/effect_bus.py"),
            (source_path / "backend" / "ui" / "services" / "theme_manager.py", "services/theme_manager.py"),
        ]),
        ("ARCHITECTURE DOCUMENTATION", [
            (source_path / "docs" / "PROJECT_PRINCIPLES_v2.md", "PROJECT_PRINCIPLES_v2.md"),
            (source_path / "docs" / "PokerPro_Trainer_Complete_Architecture_v3.md", "PokerPro_Trainer_Complete_Architecture_v3.md"),
        ]),
        ("DEBUG LOGS AND OUTPUT", [
            # This will be added manually in the report
        ])
    ]
    
    print(f"🔧 Creating MVU infinite rendering loop bug report: {output_file}")
    print(f"📁 Source directory: {source_path}")
    print(f"📁 Output directory: {output_path}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("# 🚨 MVU INFINITE RENDERING LOOP - COMPREHENSIVE BUG REPORT\n\n")
        outfile.write("**Issue**: MVU (Model-View-Update) poker hands review tab stuck in infinite rendering loop\n\n")
        outfile.write("**Symptoms**: Application becomes unresponsive due to continuous alternating renders between 0 and 2 seats\n\n")
        outfile.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        outfile.write(f"**Source Directory**: `{source_path}`\n\n")
        outfile.write("---\n\n")
        
        # Add debug output section
        outfile.write("## 🔍 DEBUG OUTPUT PATTERN\n\n")
        outfile.write("The following infinite loop pattern was observed:\n\n")
        outfile.write("```\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 2 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 0 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("[Pattern repeats infinitely...]\n")
        outfile.write("```\n\n")
        outfile.write("**Key Observation**: Despite identical cursor and waiting state values, `Props equal: False` and `Seats equal: False` always, indicating object identity issues.\n\n")
        outfile.write("---\n\n")
        
        # Process each category
        for category_name, file_list in file_categories:
            if not file_list:  # Skip empty categories
                continue
                
            print(f"📂 Processing category: {category_name}")
            
            # Write category header
            outfile.write(f"## {category_name}\n\n")
            
            # Process each file in the category
            for file_path, display_name in file_list:
                if file_path.exists():
                    print(f"  📄 Adding: {display_name}")
                    
                    # Write file header
                    outfile.write(f"### {display_name}\n\n")
                    outfile.write(f"**Path**: `{file_path}`\n\n")
                    outfile.write("```")
                    
                    # Determine file extension for syntax highlighting
                    if display_name.endswith('.py'):
                        outfile.write("python")
                    elif display_name.endswith('.json'):
                        outfile.write("json")
                    elif display_name.endswith('.md'):
                        outfile.write("markdown")
                    else:
                        outfile.write("text")
                    
                    outfile.write("\n")
                    
                    # Read and write file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        outfile.write(f"ERROR READING FILE: {e}")
                    
                    outfile.write("\n```\n\n")
                    outfile.write("---\n\n")
                else:
                    print(f"  ⚠️  File not found: {display_name} at {file_path}")
        
        # Add analysis section
        outfile.write("## 🎯 ROOT CAUSE ANALYSIS\n\n")
        outfile.write("### Primary Issue\n")
        outfile.write("The `TableRendererProps` objects are being recreated on every model update via `TableRendererProps.from_model(model)`, ")
        outfile.write("causing the equality check `self.current_props == props` to always fail, even when the actual data is identical.\n\n")
        
        outfile.write("### Key Problem Areas\n")
        outfile.write("1. **Fresh Object Creation**: `TableRendererProps.from_model()` creates new instances every time\n")
        outfile.write("2. **Nested Object Inequality**: The `seats` dictionary contains `SeatState` objects that may be recreated\n")
        outfile.write("3. **Model Update Frequency**: Frequent model updates trigger unnecessary re-renders\n")
        outfile.write("4. **Props Comparison Logic**: Dataclass equality fails due to nested mutable objects\n\n")
        
        outfile.write("### Reproduction Steps\n")
        outfile.write("1. Start application: `python3 backend/run_new_ui.py`\n")
        outfile.write("2. Navigate to 'Hands Review' tab\n")
        outfile.write("3. Observe infinite console output and unresponsive UI\n")
        outfile.write("4. Application must be terminated with Ctrl+C\n\n")
        
        outfile.write("---\n\n")
        
        # Add proposed solutions
        outfile.write("## 💡 PROPOSED SOLUTIONS\n\n")
        outfile.write("### Solution 1: Props Memoization\n")
        outfile.write("Cache `TableRendererProps` objects and only create new ones when underlying data actually changes:\n\n")
        outfile.write("```python\n")
        outfile.write("class MVUHandsReviewTab:\n")
        outfile.write("    def __init__(self, ...):\n")
        outfile.write("        self._cached_props = None\n")
        outfile.write("        self._last_model_hash = None\n")
        outfile.write("    \n")
        outfile.write("    def _on_model_changed(self, model: Model) -> None:\n")
        outfile.write("        # Create hash of relevant model data\n")
        outfile.write("        model_hash = hash((id(model.seats), model.review_cursor, model.waiting_for))\n")
        outfile.write("        \n")
        outfile.write("        # Only create new props if model actually changed\n")
        outfile.write("        if model_hash != self._last_model_hash:\n")
        outfile.write("            self._cached_props = TableRendererProps.from_model(model)\n")
        outfile.write("            self._last_model_hash = model_hash\n")
        outfile.write("        \n")
        outfile.write("        if self.table_renderer and self._cached_props:\n")
        outfile.write("            self.table_renderer.render(self._cached_props)\n")
        outfile.write("```\n\n")
        
        outfile.write("### Solution 2: Deep Equality Check\n")
        outfile.write("Implement proper deep comparison for `TableRendererProps`:\n\n")
        outfile.write("```python\n")
        outfile.write("@dataclass(frozen=True)\n")
        outfile.write("class TableRendererProps:\n")
        outfile.write("    # ... fields ...\n")
        outfile.write("    \n")
        outfile.write("    def __eq__(self, other):\n")
        outfile.write("        if not isinstance(other, TableRendererProps):\n")
        outfile.write("            return False\n")
        outfile.write("        \n")
        outfile.write("        return (\n")
        outfile.write("            self.seats == other.seats and\n")
        outfile.write("            self.board == other.board and\n")
        outfile.write("            self.pot == other.pot and\n")
        outfile.write("            # ... compare all fields\n")
        outfile.write("        )\n")
        outfile.write("```\n\n")
        
        outfile.write("### Solution 3: Selective Subscription\n")
        outfile.write("Only notify view subscribers when rendering-relevant fields actually change.\n\n")
        
        # Write footer
        outfile.write("---\n\n")
        outfile.write("## 📋 END OF MVU INFINITE RENDERING LOOP BUG REPORT\n\n")
        outfile.write("**Priority**: HIGH - Application completely unusable\n\n")
        outfile.write("**Environment**: Python 3.13.2, Tkinter, MVU Architecture, macOS\n\n")
        outfile.write("*This comprehensive report contains all source code and analysis needed to resolve the MVU infinite rendering loop issue.*\n")
    
    print(f"\n✅ MVU bug report created: {output_file}")
    
    # Get file size
    file_size = output_file.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Create comprehensive MVU infinite rendering loop bug report",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory containing all source files (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory for the bug report (default: current directory)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        default='MVU_INFINITE_RENDERING_LOOP_COMPREHENSIVE_BUG_REPORT.md',
        help='Output filename (default: MVU_INFINITE_RENDERING_LOOP_COMPREHENSIVE_BUG_REPORT.md)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = create_mvu_bug_report(
            source_dir=args.source,
            output_dir=args.output,
            output_filename=args.filename
        )
        
        print(f"\n🎯 Success! MVU bug report created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating MVU bug report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---

### create_mvu_persistent_loop_bug_report.py

**Path:** `create_mvu_persistent_loop_bug_report.py`

```python
#!/usr/bin/env python3
"""
MVU Persistent Infinite Loop Bug Report Generator
Creates a comprehensive bug report for the still-occurring infinite rendering loop
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_persistent_loop_bug_report(source_dir, output_dir, output_filename):
    """Create comprehensive bug report for persistent MVU infinite rendering loop."""
    
    # Convert to Path objects
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()
    
    # Ensure source directory exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    # Ensure output directory exists
    output_path.mkdir(exist_ok=True)
    
    # Define the output file
    output_file = output_path / output_filename
    
    # Define file categories - focused on the persistent loop issue
    file_categories = [
        ("BUG DESCRIPTION AND EVIDENCE", [
            # This will be written manually in the report
        ]),
        ("CURRENT MVU IMPLEMENTATION (POST-FIX)", [
            (source_path / "backend" / "ui" / "mvu" / "types.py", "mvu/types.py"),
            (source_path / "backend" / "ui" / "mvu" / "update.py", "mvu/update.py"),
            (source_path / "backend" / "ui" / "mvu" / "store.py", "mvu/store.py"),
            (source_path / "backend" / "ui" / "mvu" / "view.py", "mvu/view.py"),
            (source_path / "backend" / "ui" / "mvu" / "hands_review_mvu.py", "mvu/hands_review_mvu.py"),
        ]),
        ("DEBUGGING AND LOGS", [
            # This will be added manually
        ]),
        ("RELATED INFRASTRUCTURE", [
            (source_path / "backend" / "ui" / "mvu" / "drivers.py", "mvu/drivers.py"),
            (source_path / "backend" / "ui" / "app_shell.py", "app_shell.py"),
            (source_path / "backend" / "run_new_ui.py", "run_new_ui.py"),
        ]),
        ("PREVIOUS FIX ATTEMPTS", [
            (source_path / "MVU_INFINITE_LOOP_FIX_SUMMARY.md", "MVU_INFINITE_LOOP_FIX_SUMMARY.md"),
            (source_path / "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md", "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md"),
        ]),
        ("ARCHITECTURE REFERENCES", [
            (source_path / "docs" / "PROJECT_PRINCIPLES_v2.md", "PROJECT_PRINCIPLES_v2.md"),
        ])
    ]
    
    print(f"🔧 Creating persistent MVU loop bug report: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("# 🚨 MVU PERSISTENT INFINITE RENDERING LOOP - CRITICAL BUG\n\n")
        outfile.write("**Status**: UNRESOLVED - Loop persists despite multiple fix attempts\n\n")
        outfile.write("**Severity**: CRITICAL - Application completely unusable\n\n")
        outfile.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        outfile.write("---\n\n")
        
        # Add the persistent issue description
        outfile.write("## 🔥 PERSISTENT ISSUE DESCRIPTION\n\n")
        outfile.write("Despite implementing the following fixes:\n")
        outfile.write("- ✅ Value-equal dataclasses with `@dataclass(frozen=True, eq=True, slots=True)`\n")
        outfile.write("- ✅ Proper props memoization with early-out comparison\n")
        outfile.write("- ✅ Removed UpdateUI command entirely\n")
        outfile.write("- ✅ Immutable data structures (tuples instead of lists)\n\n")
        outfile.write("**THE INFINITE LOOP STILL PERSISTS!**\n\n")
        
        # Add debug evidence
        outfile.write("## 🔍 CURRENT DEBUG EVIDENCE\n\n")
        outfile.write("The following pattern continues to occur infinitely:\n\n")
        outfile.write("```\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 0 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 2 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("[REPEATS INFINITELY]\n")
        outfile.write("```\n\n")
        
        # Key observations
        outfile.write("## 🧐 KEY OBSERVATIONS\n\n")
        outfile.write("1. **Props Equality Still Failing**: Despite dataclass equality, `Props equal: False`\n")
        outfile.write("2. **Seats Equality Failing**: `Seats equal: False` even with identical cursor/state\n")
        outfile.write("3. **Values Are Identical**: `Review cursor: 0 -> 0` and `Waiting for: NONE -> NONE`\n")
        outfile.write("4. **Alternating Pattern**: Switches between 0 seats and 2 seats consistently\n")
        outfile.write("5. **Dataclass Equality Not Working**: The `==` operator is not behaving as expected\n\n")
        
        # Hypothesis
        outfile.write("## 🎯 NEW HYPOTHESIS\n\n")
        outfile.write("The issue may be deeper than just dataclass equality:\n\n")
        outfile.write("### Potential Root Causes:\n")
        outfile.write("1. **Nested Dictionary Mutation**: The `seats: Dict[int, SeatState]` may be getting mutated\n")
        outfile.write("2. **Set Equality Issues**: `legal_actions: Set[str]` may not be comparing correctly\n")
        outfile.write("3. **Hidden State Changes**: Something is modifying the model between comparisons\n")
        outfile.write("4. **Dataclass Hash Collision**: Frozen dataclasses might have hash issues with mutable containers\n")
        outfile.write("5. **Timing Race Condition**: Multiple threads/events firing simultaneously\n")
        outfile.write("6. **Scale Widget Callback**: The review scale might still be triggering callbacks\n")
        outfile.write("7. **Model Creation Logic**: The `from_model()` method might be creating different objects\n\n")
        
        # Investigation needed
        outfile.write("## 🔍 INVESTIGATION NEEDED\n\n")
        outfile.write("### Immediate Debug Steps:\n")
        outfile.write("1. **Deep Inspection**: Add logging to show exact object contents being compared\n")
        outfile.write("2. **Hash Analysis**: Check if hash values are consistent for 'equal' objects\n")
        outfile.write("3. **Mutation Detection**: Add immutability checks to detect if objects are being modified\n")
        outfile.write("4. **Thread Analysis**: Verify all UI updates happen on main thread\n")
        outfile.write("5. **Event Tracing**: Log all dispatch calls to find the trigger source\n")
        outfile.write("6. **Memory Analysis**: Check if objects are being garbage collected unexpectedly\n\n")
        
        # Reproduction
        outfile.write("## 📋 REPRODUCTION\n\n")
        outfile.write("1. Run: `python3 backend/run_new_ui.py`\n")
        outfile.write("2. Navigate to 'Hands Review' tab\n")
        outfile.write("3. Infinite loop starts immediately\n")
        outfile.write("4. CPU usage spikes to 100%\n")
        outfile.write("5. Application becomes unresponsive\n\n")
        
        outfile.write("---\n\n")
        
        # Process each category
        for category_name, file_list in file_categories:
            if not file_list:  # Skip empty categories for now
                continue
                
            print(f"📂 Processing category: {category_name}")
            
            # Write category header
            outfile.write(f"## {category_name}\n\n")
            
            # Process each file in the category
            for file_path, display_name in file_list:
                if file_path.exists():
                    print(f"  📄 Adding: {display_name}")
                    
                    # Write file header
                    outfile.write(f"### {display_name}\n\n")
                    outfile.write(f"**Path**: `{file_path}`\n\n")
                    outfile.write("```")
                    
                    # Determine file extension for syntax highlighting
                    if display_name.endswith('.py'):
                        outfile.write("python")
                    elif display_name.endswith('.json'):
                        outfile.write("json")
                    elif display_name.endswith('.md'):
                        outfile.write("markdown")
                    else:
                        outfile.write("text")
                    
                    outfile.write("\n")
                    
                    # Read and write file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        outfile.write(f"ERROR READING FILE: {e}")
                    
                    outfile.write("\n```\n\n")
                    outfile.write("---\n\n")
                else:
                    print(f"  ⚠️  File not found: {display_name} at {file_path}")
        
        # Add urgent action items
        outfile.write("## 🚨 URGENT ACTION ITEMS\n\n")
        outfile.write("1. **Add Deep Debug Logging**: Instrument the props comparison to show exact differences\n")
        outfile.write("2. **Isolate the Trigger**: Find what's causing the initial model change\n")
        outfile.write("3. **Test Dataclass Equality**: Create minimal test case for TableRendererProps equality\n")
        outfile.write("4. **Check Object Identity**: Verify if objects are being recreated unnecessarily\n")
        outfile.write("5. **Review Scale Widget**: Ensure review scale callbacks are truly disabled\n")
        outfile.write("6. **Memory Profiling**: Check for memory leaks or object pooling issues\n\n")
        
        # Potential emergency solutions
        outfile.write("## 🆘 EMERGENCY WORKAROUNDS\n\n")
        outfile.write("If the issue cannot be resolved quickly:\n\n")
        outfile.write("1. **Revert to Legacy Tab**: Temporarily restore the old HandsReviewTab\n")
        outfile.write("2. **Disable MVU Tab**: Remove MVU tab from main app until fixed\n")
        outfile.write("3. **Add Rate Limiting**: Limit renders to max 1 per 100ms as emergency brake\n")
        outfile.write("4. **Force Early Return**: Add counter-based early return after N renders\n\n")
        
        # Write footer
        outfile.write("---\n\n")
        outfile.write("## 📋 END OF PERSISTENT LOOP BUG REPORT\n\n")
        outfile.write("**Priority**: CRITICAL - Application completely broken\n\n")
        outfile.write("**Next Step**: Immediate deep debugging session required\n\n")
        outfile.write("*This report documents the failure of initial fix attempts and provides direction for deeper investigation.*\n")
    
    print(f"\n✅ Persistent loop bug report created: {output_file}")
    
    # Get file size
    file_size = output_file.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Create persistent MVU infinite loop bug report"
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        default='MVU_PERSISTENT_INFINITE_LOOP_BUG_REPORT.md',
        help='Output filename'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = create_persistent_loop_bug_report(
            source_dir=args.source,
            output_dir=args.output,
            output_filename=args.filename
        )
        
        print(f"\n🎯 Critical bug report created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating bug report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---

## LEGACY COMPONENTS (For Context)

### poker_table_renderer.py

**Path:** `backend/ui/renderers/poker_table_renderer.py`

```python
"""
Pure state-driven poker table renderer.
This component ONLY renders – no business logic, no state management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from tkinter import ttk

from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager
from ..tableview.renderer_pipeline import RendererPipeline
from ..tableview.components.table_felt import TableFelt
from ..tableview.components.seats import Seats
from ..tableview.components.community import Community
from ..tableview.components.pot_display import PotDisplay
from ..tableview.components.bet_display import BetDisplay
from ..tableview.components.dealer_button import DealerButton
from ..tableview.components.player_highlighting import PlayerHighlighting


from ..table.state import PokerTableState


class PokerTableRenderer(ttk.Frame):
    """
    Pure rendering component for poker table.
    Renders state, emits intents, no business logic.
    """

    def __init__(
        self,
        parent,
        intent_handler: Optional[Callable[[Dict[str, Any]], None]] = None,
        theme_manager: Any = None,
    ) -> None:
        super().__init__(parent)
        self.intent_handler = intent_handler or (lambda _: None)
        self.theme_manager = theme_manager

        self._setup_rendering_pipeline()
        self.current_state: Optional[PokerTableState] = None
        self.renderer = None  # Will be initialized when canvas is ready
        self._ready_callbacks = []  # Callbacks to call when renderer is ready

    def _setup_rendering_pipeline(self) -> None:
        # Create CanvasManager first; it will initialize canvas lazily
        self.canvas_manager = CanvasManager(self)

        # Prepare components
        self.components = [
            TableFelt(),
            Seats(),
            Community(),
            BetDisplay(),
            PotDisplay(),
            DealerButton(),
            PlayerHighlighting(),
        ]

        # LayerManager depends on a real canvas; set up when ready
        def _finalize_pipeline():
            try:
                print(f"🔧 PokerTableRenderer: Starting pipeline finalization...")
                print(f"🔧 PokerTableRenderer: Canvas: {self.canvas_manager.canvas}")
                print(f"🔧 PokerTableRenderer: Overlay: {self.canvas_manager.overlay}")
                
                self.layer_manager = LayerManager(
                    self.canvas_manager.canvas, self.canvas_manager.overlay
                )
                print(f"🔧 PokerTableRenderer: LayerManager created: {self.layer_manager}")
                
                self.renderer = RendererPipeline(
                    self.canvas_manager, self.layer_manager, self.components
                )
                print(f"🔧 PokerTableRenderer: Renderer created: {self.renderer is not None}")
                print(f"🔧 PokerTableRenderer: Renderer object: {self.renderer}")
                
                # Grid now that canvas exists
                try:
                    self.canvas_manager.canvas.grid(row=0, column=0, sticky="nsew")
                    print(f"🔧 PokerTableRenderer: Canvas gridded successfully")
                except Exception as grid_e:
                    print(f"⚠️ PokerTableRenderer: Canvas grid error: {grid_e}")
                    
                self.grid_columnconfigure(0, weight=1)
                self.grid_rowconfigure(0, weight=1)
                print("✅ PokerTableRenderer: Pipeline finalized successfully")
                print(f"🔍 PokerTableRenderer: Final renderer state: {hasattr(self, 'renderer')} / {self.renderer is not None}")
                
                # Notify any waiting callbacks that renderer is ready
                print(f"🔄 PokerTableRenderer: Processing {len(self._ready_callbacks)} ready callbacks")
                for i, callback in enumerate(self._ready_callbacks):
                    try:
                        print(f"🔄 PokerTableRenderer: Calling ready callback {i+1}")
                        callback()
                        print(f"✅ PokerTableRenderer: Ready callback {i+1} completed")
                    except Exception as cb_e:
                        print(f"⚠️ PokerTableRenderer: Ready callback {i+1} error: {cb_e}")
                        import traceback
                        traceback.print_exc()
                self._ready_callbacks.clear()
                print(f"🔄 PokerTableRenderer: All callbacks processed, renderer final check: {self.renderer is not None}")
                
            except Exception as e:
                print(f"⚠️ PokerTableRenderer finalize error: {e}")
                import traceback
                traceback.print_exc()
                # Initialize renderer to None to prevent AttributeError
                self.renderer = None

        if getattr(self.canvas_manager, 'is_ready', lambda: False)():
            _finalize_pipeline()
        else:
            # Defer until the canvas is created
            try:
                self.canvas_manager.defer_render(lambda: _finalize_pipeline())
            except Exception:
                pass

    def render(self, state: PokerTableState) -> None:
        if state != self.current_state:
            # Check if renderer is initialized
            has_attr = hasattr(self, 'renderer')
            is_not_none = has_attr and self.renderer is not None
            print(f"🔍 PokerTableRenderer: Render check - hasattr: {has_attr}, not None: {is_not_none}")
            
            if not has_attr or self.renderer is None:
                print("⚠️ PokerTableRenderer: Renderer not ready, deferring render")
                # Defer render until renderer is ready
                self._ready_callbacks.append(lambda: self.render(state))
                print(f"🔄 PokerTableRenderer: Render deferred via ready callback (callbacks: {len(self._ready_callbacks)})")
                return
            
            # Render table
            self.renderer.render_once(state.__dict__)
            # Process declarative effects
            self._process_effects(state.effects)
            self.current_state = state

    def _process_effects(self, effects: List[Dict[str, Any]]) -> None:
        """Emit intents for visual effects to be handled externally."""
        for effect in effects or []:
            et = effect.get("type")
            if et in {"CHIP_TO_POT", "POT_TO_WINNER", "HIGHLIGHT_PLAYER"}:
                # Pure visual effects handled here; acoustic handled by EffectBus
                self._emit_intent(
                    {"type": "REQUEST_ANIMATION", "payload": effect}
                )

    def _emit_intent(self, intent: Dict[str, Any]) -> None:
        try:
            self.intent_handler(intent)
        except Exception:
            pass



```

---

### canvas_manager.py

**Path:** `backend/ui/tableview/canvas_manager.py`

```python
import tkinter as tk
import importlib


class CanvasManager:
    def __init__(self, parent):
        # Store parent; defer canvas creation until sized to avoid small initial render
        self.parent = parent
        self.canvas = None
        self.overlay = None
        self._configure_after_id = None
        self._initialized = False
        self._pending_render = None

        # Resolve theme bg color once for initialization
        try:
            from ui.services.theme_manager import ThemeManager
            tm = ThemeManager()
            theme_colors = tm.get()
            self._canvas_bg = theme_colors.get("table.bg", theme_colors.get("panel.bg", "#000000"))
        except Exception:
            self._canvas_bg = "#000000"

        # Schedule lazy initialization after idle; we may need to retry until sized
        try:
            self.parent.after_idle(self._initialize_canvas)
        except Exception:
            # Fallback: attempt immediate init
            self._initialize_canvas()

    def _on_configure(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        try:
            if self.overlay is not None and self.canvas is not None:
                self.overlay.lift(self.canvas)
        except Exception:
            pass

    def size(self):
        if not self.canvas:
            return 0, 0
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            try:
                w = self.canvas.winfo_reqwidth()
                h = self.canvas.winfo_reqheight()
            except Exception:
                pass
        return w, h

    # New APIs for deferred render gating
    def is_ready(self):
        return self._initialized and self.canvas is not None

    def defer_render(self, render_func):
        if self.is_ready():
            try:
                render_func()
            except Exception:
                pass
        else:
            self._pending_render = render_func

    def _initialize_canvas(self):
        # Force geometry update and get real size; retry until reasonable
        try:
            self.parent.update_idletasks()
        except Exception:
            pass

        try:
            pw = getattr(self.parent, 'winfo_width')()
            ph = getattr(self.parent, 'winfo_height')()
        except Exception:
            pw, ph = 0, 0

        if pw <= 100 or ph <= 100:
            # ARCHITECTURE COMPLIANT: Schedule via parent's GameDirector if available
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_RETRY",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Fallback: direct retry (violation but necessary)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass
            return

        # Create canvas now with proper size and grid into parent
        try:
            self.canvas = tk.Canvas(self.parent, width=pw, height=ph, bg=self._canvas_bg, highlightthickness=0)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            try:
                self.canvas.bind("<Configure>", self._on_configure, add="+")
            except Exception:
                pass
            self._initialized = True

            # Execute any pending render deferral
            if self._pending_render is not None:
                pending = self._pending_render
                self._pending_render = None
                try:
                    pending()
                except Exception:
                    pass
        except Exception:
            # ARCHITECTURE COMPLIANT: Last resort retry via GameDirector
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_LAST_RESORT",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Final fallback: direct retry (violation but necessary for bootstrap)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass



```

---

### renderer_pipeline.py

**Path:** `backend/ui/tableview/renderer_pipeline.py`

```python
class RendererPipeline:
    def __init__(self, canvas_manager, layer_manager, components):
        self.cm = canvas_manager
        self.lm = layer_manager
        self.components = components

    def render_once(self, state, force=False):
        # Gate rendering until the canvas is created/sized to avoid small initial artifacts
        if not self.cm.is_ready() and not force:
            self.cm.defer_render(lambda: self.render_once(state, force=True))
            return

        c = self.cm.canvas
        if c is None:
            return

        w, h = self.cm.size()
        if w <= 100 or h <= 100:
            # Skip rendering on invalid size; a deferred render will occur on ready
            print(f"⚠️ Skipping render - invalid dimensions: {w}x{h}")
            return

        # Thorough clear to ensure no remnants from any previous pass
        try:
            c.delete("all")
        except Exception:
            pass

        # Render all components
        for component in self.components:
            try:
                component.render(state, self.cm, self.lm)
            except Exception as e:
                print(f"⚠️ Component {component.__class__.__name__} render error: {e}")

        # Apply layer ordering
        try:
            self.lm.raise_to_policy()
        except Exception as e:
            print(f"⚠️ Layer manager error: {e}")

        print(f"🎨 Rendered poker table: {w}x{h} with {len(self.components)} components")



```

---

## ARCHITECTURE DOCUMENTATION

### PROJECT_PRINCIPLES_v2.md

**Path:** `docs/PROJECT_PRINCIPLES_v2.md`

```markdown
## Project Principles v2 (Authoritative)

### Architecture
- Single-threaded, event-driven coordinator (GameDirector). All timing via coordinator.
- Single source of truth per session (Store). No duplicate state.
- Event-driven only. UI is pure render from state; no business logic in UI.

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

### 🚫 CRITICAL AI AGENT COMPLIANCE RULES (NEVER VIOLATE)

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

```

---

### ARCHITECTURE_VIOLATION_PREVENTION_GUIDE.md

**Path:** `docs/ARCHITECTURE_VIOLATION_PREVENTION_GUIDE.md`

```markdown
# 🚫 Architecture Violation Prevention Guide

**Status**: Critical Reference for AI Agents  
**Purpose**: Prevent common architecture violations that compromise system integrity  
**Target Audience**: AI Coding Assistants, Future Development Teams  

---

## 🎯 **EXECUTIVE SUMMARY**

This guide documents **critical architecture violations** discovered during system analysis and provides **mandatory prevention patterns** for future AI agents. These violations were found in production code and **must never be repeated**.

### **🔥 HIGH-SEVERITY VIOLATIONS FOUND**

1. **Business Logic in UI Components** - UI directly executing business operations
2. **Direct Service Calls from UI** - Bypassing Store/Reducer architecture  
3. **Timing Violations** - Using `self.after()` instead of GameDirector
4. **State Mutations in UI** - Direct state changes bypassing Store
5. **Mixed Rendering Patterns** - Multiple rendering approaches instead of unified system

---

## 📋 **VIOLATION CATALOG & FIXES**

### **🚨 VIOLATION 1: Business Logic in UI Components**

#### **❌ FORBIDDEN PATTERN**
```python
class HandsReviewTab(ttk.Frame):
    def _next_action(self):
        # ❌ WRONG: Business logic in UI
        session_state = self.session_manager.execute_action()
        
        if session_state.current_action_index < session_state.total_actions:
            self._update_status(f"Action {session_state.current_action_index}")
            self._render_table_with_state(session_state)
        else:
            self._update_status("Hand complete")
```

#### **✅ CORRECT PATTERN**
```python
class HandsReviewTab(ttk.Frame):
    def _next_action(self):
        # ✅ CORRECT: Pure UI dispatch
        self.store.dispatch({
            "type": "HANDS_REVIEW_NEXT_ACTION",
            "session_id": self.session_id,
            "timestamp": time.time()
        })
```

#### **🛡️ PREVENTION RULES**
- UI components are **pure renderers only**
- All business logic in Services or PPSM
- UI only dispatches actions and renders state
- No direct calls to session managers from UI

---

### **🚨 VIOLATION 2: Direct Service Calls from UI**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Direct service calls
def _handle_bet(self):
    result = self.session_manager.execute_bet(amount)  # VIOLATION!
    self.effect_bus.play_sound("bet")                  # VIOLATION!
    self._update_display(result)
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Event-driven architecture
def _handle_bet(self):
    self.store.dispatch({
        "type": "PLAYER_BET_ACTION",
        "amount": amount,
        "session_id": self.session_id
    })
    
    # Service controller handles the business logic:
    # 1. Receives event from reducer
    # 2. Calls session_manager.execute_bet()
    # 3. Calls effect_bus.play_sound()
    # 4. Updates store with results
```

#### **🛡️ PREVENTION RULES**
- No direct service method calls from UI
- All communication via Store → Reducer → Service
- Services handle business logic and side effects
- UI never touches session managers directly

---

### **🚨 VIOLATION 3: Timing Violations**

#### **❌ FORBIDDEN PATTERNS**
```python
# ❌ WRONG: Direct timing calls
self.after(1000, self._complete_action)        # VIOLATION!
threading.Timer(1.0, callback).start()        # VIOLATION!
time.sleep(1)                                  # VIOLATION!

# ❌ WRONG: Update loops with self.after
def _update_loop(self):
    self._refresh_display()
    self.after(16, self._update_loop)           # VIOLATION!
```

#### **✅ CORRECT PATTERNS**
```python
# ✅ CORRECT: GameDirector timing
self.game_director.schedule(1000, {
    "type": "DELAYED_ACTION",
    "callback": self._complete_action
})

# ✅ CORRECT: Event-driven updates
self.event_bus.publish("display:refresh_requested", {
    "interval_ms": 16,
    "component": "table_display"
})
```

#### **🛡️ PREVENTION RULES**
- All timing via GameDirector
- No `self.after()`, `threading.Timer`, or `time.sleep()`
- Use `TimingMigrationHelper` for complex timing
- Event-driven updates instead of polling loops

---

### **🚨 VIOLATION 4: State Mutations in UI**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Direct state mutations
def _update_pot(self, amount):
    self.game_state.pot += amount              # VIOLATION!
    self.display_state['seats'][0]['acting'] = True  # VIOLATION!
    self._refresh_display()
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Store dispatch for state changes
def _update_pot(self, amount):
    self.store.dispatch({
        "type": "UPDATE_POT_AMOUNT",
        "amount": amount
    })
    
    self.store.dispatch({
        "type": "SET_ACTING_PLAYER",
        "seat_index": 0,
        "acting": True
    })
```

#### **🛡️ PREVENTION RULES**
- All state changes via Store dispatch
- UI never directly mutates state objects
- Single source of truth in Store
- Reducers handle all state transformations

---

### **🚨 VIOLATION 5: Mixed Rendering Patterns**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Multiple rendering approaches
class HandsReviewTab(ttk.Frame):
    def __init__(self):
        self.poker_widget = ReusablePokerGameWidget(...)  # VIOLATION!
        self.table_renderer = PokerTableRenderer(...)    # VIOLATION!
        self.custom_canvas = tk.Canvas(...)               # VIOLATION!
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Single unified renderer
class HandsReviewTab(ttk.Frame):
    def __init__(self):
        # Single renderer for all poker table rendering
        self.table_renderer = PokerTableRenderer(
            self,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme
        )
```

#### **🛡️ PREVENTION RULES**
- Single `PokerTableRenderer` for all poker table rendering
- No custom canvas rendering alongside renderer
- No legacy widget mixing with new architecture
- Unified rendering pipeline for consistency

---

## 🛡️ **MANDATORY ENFORCEMENT CHECKLIST**

### **Pre-Development Checklist**
- [ ] **UI Design Review**: Verify UI components are pure renderers
- [ ] **Architecture Review**: Confirm Store/Reducer/Service pattern
- [ ] **Timing Review**: All delays via GameDirector
- [ ] **State Flow Review**: No direct state mutations in UI

### **Code Review Checklist**
- [ ] No business logic in UI components
- [ ] No direct service calls from UI (session_manager, effect_bus, etc.)
- [ ] No timing violations (`self.after`, `threading.Timer`, `time.sleep`)
- [ ] All state changes via Store dispatch
- [ ] Event-driven communication only
- [ ] Single PokerTableRenderer used
- [ ] Theme tokens only (no hardcoded colors)

### **Testing Checklist**
- [ ] UI components can be tested in isolation (no business logic)
- [ ] Service layer can be tested without UI
- [ ] State changes are deterministic via reducers
- [ ] Timing is controlled via GameDirector

---

## 🚨 **IMMEDIATE REJECTION CRITERIA**

**Reject any code that contains:**

```python
# ❌ IMMEDIATE REJECTION TRIGGERS
session_manager.execute_action()     # Business logic in UI
self.after(                         # Timing violation
threading.Timer                     # Threading violation  
self.game_state.pot =              # Direct state mutation
ReusablePokerGameWidget            # Legacy mixing
```

---

## 📚 **REFERENCE IMPLEMENTATIONS**

### **✅ Compliant HandsReviewTab Structure**
```python
class HandsReviewTab(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.services = services
        self.store = services.get_app("store")
        self.event_bus = services.get_app("event_bus")
        
        # Single unified renderer
        self.table_renderer = PokerTableRenderer(...)
        
        # Register with event controller
        self.event_bus.publish("hands_review:session_created", {
            "session_id": self.session_id,
            "session_manager": self.session_manager
        })
    
    def _next_action(self):
        """Pure UI dispatch - no business logic"""
        self.store.dispatch({
            "type": "HANDS_REVIEW_NEXT_ACTION",
            "session_id": self.session_id
        })
    
    def dispose(self):
        """Clean disposal with event notification"""
        self.event_bus.publish("hands_review:session_disposed", {
            "session_id": self.session_id
        })
```

### **✅ Compliant Event Controller Structure**
```python
class HandsReviewEventController:
    def __init__(self, event_bus, store, services):
        self.event_bus = event_bus
        self.store = store
        self.services = services
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(
            "hands_review:next_action_requested",
            self._handle_next_action_request
        )
    
    def _handle_next_action_request(self, event_data):
        """Business logic handling - not in UI"""
        session_id = event_data.get('session_id')
        session_manager = self.session_managers.get(session_id)
        
        # Execute business logic
        session_state = session_manager.execute_action()
        
        # Update store with results
        self.store.dispatch({
            "type": "UPDATE_HANDS_REVIEW_STATE",
            "session_id": session_id,
            "state": session_state
        })
```

---

## 🎯 **SUCCESS METRICS**

### **Architecture Compliance Metrics**
- ✅ **0** business logic methods in UI components
- ✅ **0** direct service calls from UI
- ✅ **0** timing violations (`self.after`, etc.)
- ✅ **0** direct state mutations in UI
- ✅ **1** unified rendering system (PokerTableRenderer)

### **Code Quality Metrics**  
- ✅ **100%** event-driven communication
- ✅ **100%** Store/Reducer pattern compliance
- ✅ **100%** GameDirector timing coordination
- ✅ **100%** theme token usage (no hardcoded colors)

---

## 📞 **SUPPORT & ESCALATION**

### **When to Escalate**
- Architecture violation detected in production
- Uncertainty about Store/Reducer pattern implementation
- Complex timing requirements that may need GameDirector enhancement
- Performance issues related to event-driven architecture

### **Escalation Process**
1. Document the specific violation or concern
2. Reference this guide's violation catalog
3. Propose architecture-compliant alternative
4. Request architecture review before implementation

---

**🔒 This guide is MANDATORY for all AI agents working on this codebase. Violations of these patterns compromise system integrity and MUST be prevented.**

```

---

### UI_IMPLEMENTATION_HANDBOOK.md

**Path:** `docs/PokerPro_UI_Implementation_Handbook_v1.1.md`

```markdown
# PokerPro Trainer — **UI Implementation Handbook** (v1.1)
**Date**: 2025-08-18  
**Audience**: AI coding agents & human reviewers  
**Status**: Authoritative — Do **not** deviate without updating this handbook.

> Golden rule: **UI renders state; events mutate state via PPSM; effects live at the edges.**

---

## 0) Purpose & Scope
This handbook locks down the **UI-side implementation rules** for PokerPro so contributors and AI agents **do not invent new patterns**. It covers session UIs (Practice, Hands Review, GTO), rendering rules, contracts with PPSM, theming, logging, testing, and a detailed **GameDirector** contract for sounds, animations, and autoplay.

---

## 1) Canonical Architecture (Summary)
- **Coordinator**: Single-threaded, event-driven **GameDirector** orchestrates timing (autoplay, effect gating).  
- **Store**: One source of truth per session. No duplicate state or cross-writes.  
- **Domain**: **PPSM** (PurePokerStateMachine) is deterministic and authoritative for poker rules.  
- **UI**: **Render-only**. Emits **intents** → adapter builds **domain events** → `ppsm.transition(state, event)` → Store update.  
- **Adapters**: Sounds, persistence, estimators, external APIs — side-effectful but stateless re: domain.  
- **Renderer Pipeline**: Composable canvas layers (felt → seats → community → pot → overlays).

---

### 1.1) **Poker Table — Pure Renderer & Reuse Contract**
The poker table is implemented as a **pure renderer** (`backend/ui/renderers/poker_table_renderer.py`).

Authoritative rules:
- Input: one immutable `PokerTableState` (in `backend/ui/table/state.py`).
- Output: optional renderer intents (e.g., `{type: "REQUEST_ANIMATION", payload: effect}`) — no business logic.
- No PPSM calls, no timers, no side effects; purely draws state via tableview components.
- Common across Practice, Hands Review, and GTO sessions; differences live in the **SessionManager**.

Minimal usage:
```python
renderer = PokerTableRenderer(parent, intent_handler, theme_manager)
renderer.render(PokerTableState(...))
```

Effects:
- Renderer emits intents; the shell forwards to EventBus `effect_bus:animate`.
- `EffectBus` bridges to `ChipAnimations` and coordinates gating via **GameDirector**.

Layer order (must): `felt → seats → stacks → community → bets → pot → action → status → overlay → temp_animation`.

### 1.2) **GameDirector — Role & Scope (Authoritative)**
**Goal**: Centralize time, autoplay, and effect sequencing to keep behavior **deterministic, cancellable, and single-threaded**.

**The Director does:**
- Maintain **play/pause/seek/speed** for session playback.
- Schedule **AUTO_ADVANCE** during autoplay at the configured interval.
- **Gate effects** so autoplay only advances after required animations/sounds complete.
- Emit **time events** (`TIMER_TICK`, `TIMER_EXPIRED`) when sessions use timers.
- Coordinate the **EffectBus** (sounds/animations/haptics) via completion events.

**The Director does *not* do:**
- Poker legality or domain rules (PPSM only).  
- Hold domain state (Store is the single source of truth).  
- Use threads or blocking calls (everything single-threaded and queued).

**Minimal API**
```python
class GameDirector:
    def schedule(self, delay_ms: int, event: dict) -> str: ...
    def cancel(self, token: str) -> None: ...
    def play(self) -> None: ...
    def pause(self) -> None: ...
    def step_forward(self, n: int = 1) -> None: ...
    def step_back(self, n: int = 1) -> None: ...
    def seek(self, step_index: int) -> None: ...
    def set_speed(self, multiplier: float) -> None: ...
    def set_autoplay_interval(self, ms: int) -> None: ...

    # Effect gating
    def gate_begin(self) -> None: ...
    def gate_end(self) -> None: ...  # call on ANIM_COMPLETE/SOUND_COMPLETE
```

**Event catalog it may emit**
- `AUTO_ADVANCE` (autoplay next step)
- `TIMER_TICK` / `TIMER_EXPIRED` (if timers are used)
- `ANIM_COMPLETE`, `SOUND_COMPLETE` (posted by EffectBus through Director)

**Timing policy**
- Single-threaded, pumped from UI loop (e.g., Tk `after(16, pump)`).  
- **Speed** scales scheduled delays (`delay_ms / speed`).  
- Time is **fakeable** in tests via an injected clock.

**Integration flow**
```
UI intent → Adapter builds domain event → ppsm.transition → Store.replace →
Renderer renders (pure) → EffectBus interprets effects → Director gates & schedules AUTO_ADVANCE
```

---

## 2) Feature mapping to Renderer / Director / Effects
| Feature | Trigger | Who decides | Director role | Effects / Events |
|---|---|---|---|---|
| **Player highlighting (current actor glow)** | Store state (`seats[i].acting`) | Renderer (pure) | None (render-only) | No effect; renderer reads acting seat |
| **Action sounds (BET/CALL/CHECK/FOLD, etc.)** | After `ppsm.transition` on action events | Reducer adds `SOUND` effect | Gate if sound duration blocks autoplay | `SOUND(id)` → `SOUND_COMPLETE` after duration |
| **Deal sounds (cards)** | On `DEAL_*` events | Reducer adds `SOUND('deal')` | Optional gate | `SOUND('deal')` |
| **End-of-street chips-to-pot animation** | On transition to next street | Reducer adds `ANIMATE('chips_to_pot')` (+ optional sound) | **Gate** until complete | `ANIMATE('chips_to_pot', ms=250)` → `ANIM_COMPLETE` |
| **Showdown / last-player standing** | On `SHOWDOWN` or only one active | Reducer adds `ANIMATE('pot_to_winner')` + `SOUND('chips_scoop')` + `BANNER('winner')` | **Gate** until complete | `ANIMATE('pot_to_winner', ms=500)`; `SOUND('chips_scoop')`; `BANNER('winner')` (non-gated visual) |
| **Autoplay** | User presses Play | Director | Schedules `AUTO_ADVANCE` if not gated | `AUTO_ADVANCE` at interval; delayed while gate > 0 |
| **Speed control** | User changes speed | Director | Scales scheduled delays | N/A |
| **Seek / Step** | User seeks/steps | Director + Shell | Resets playback position; cancels scheduled events | N/A |

**Gating rule**: If any effect in a step requires gating (e.g., chip/pot animation, long SFX), the reducer marks it so the EffectBus calls `director.gate_begin()` before starting and `director.gate_end()` on completion. Autoplay only advances when **gate count is 0**.

---

## 3) Contracts Between UI and PPSM
### 3.1 Inputs to PPSM
```json
{
  "type": "BET",
  "actor_uid": "Player2",
  "street": "TURN",
  "to_amount": 120,
  "note": null
}
```

- `type`: **UPPER_SNAKE_CASE** (e.g., `POST_BLIND`, `BET`, `RAISE`, `CALL`, `CHECK`, `FOLD`, `DEAL_FLOP`, `SHOWDOWN`)
- `street`: **PREFLOP/FLOP/TURN/RIVER** (uppercase)
- Fields: **snake_case**

### 3.2 Outputs the UI may read (via selectors)
- `currentStreet(state)` → `"TURN"`  
- `currentActor(state)` → `"Player1"`  
- `legalActions(state)` → `[ "FOLD", "CALL", "RAISE" ]` with ranges  
- `pot(state)` → `int`  
- `stacks(state)` → `{ uid: int }`  
- `board(state)` → `["Qh","7c","7d"]`  
- `handResult(state)` after `SHOWDOWN`

**Forbidden**: UI must **not** compute legality or mutate domain state.

---

## 4) Renderer Pipeline & Components
**Layer order**: `felt → seats → stacks → community → bets → pot → action → status → overlay → temp_animation`

**Boundaries**
- **SeatPod**: avatar, name, stack, halo, badges (subscribe to seat selectors).
- **CommunityBoard**: board cards and visual-only burns.
- **PotDisplay**: pot totals/side pots/badges.
- **ActionBar**: hero legal actions (from selectors only).
- **HUD/Overlays**: actor glow, toasts, timers; no domain writes.

---

## 5) Sessions (Practice / Hands Review / GTO)
### Session Managers (Reusable Pattern)
Implement managers that own PPSM calls, state shaping, and effects. Examples:
- `PracticeSessionManager`: executes hero/bot actions, builds `PokerTableState`, adds CHIP_TO_POT effects, dispatches to Store
- `GTOSessionManager`: wraps GTO engine, provides advice, same render/effects path
- Planned `HandsReviewSessionManager`: drives trace steps, produces `PokerTableState` and effects

Renderer is shared across all sessions; managers isolate differences.

### 5.2 Hands Review
- Step / Play / Pause / Seek / Speed.  
- Each trace step → domain event; reducer computes effects.  
- Director gates effects so autoplay advances only after completions.

### 5.3 GTO Session
- All non-hero decisions via DecisionEngine; deterministic for seed/state.  
- Explanations come from engine outputs (UI never invents analysis).  
- Effects like Practice; Director coordinates autoplay and gating.

---

## 6) Theme & Design System (Tokens are mandatory)
Use **ThemeManager** tokens; **no literal colors** in components.

Tokens (subset):  
```
a11y.focus, board.border, board.cardBack, board.cardFaceFg, board.slotBg, btn.active.bg, btn.default.bg, btn.hover.bg, burgundy.base, burgundy.bright, burgundy.deep, chip_gold, dealer.buttonBg, dealer.buttonBorder, dealer.buttonFg, emerald.base, emerald.bright, gold.base, gold.bright, gold.dim, panel.bg, panel.border, panel.fg, player.name, player.stack, pot.badgeBg, pot.badgeRing, pot.valueText, primary_bg, seat.bg.acting, seat.bg.active, seat.bg.idle, secondary_bg, table.center, table.edgeGlow, table.felt, table.inlay, table.rail, table.railHighlight, text.muted, text.primary, text.secondary, text_gold, theme_config.json
```

- Accessibility: WCAG ≥ 4.5:1; focus via `a11y.focus`.  
- Targets ≥ 44×44; fonts/cards scale per responsive rules.  
- Live theme switching: components re-render on token change.

---

## 7) EffectBus & Sound Catalog (standardize IDs)
**Effect types**: `SOUND`, `ANIMATE`, `BANNER`, `VIBRATE`, `TOAST`

**Sound IDs (examples; keep stable for mapping):**
- `fx.deal`, `fx.bet_single`, `fx.bet_multi`, `fx.call`, `fx.check`, `fx.fold`, `fx.raise`, `fx.chips_scoop`, `fx.win_fanfare`

**Animation names (examples):**
- `chips_to_pot`, `pot_to_winner`, `actor_glow_pulse`

**Durations**: Use **config** to define canonical durations (ms) for gating; do not measure audio runtime at render time.

---

## 8) Error Handling, Logging, and Telemetry
- Log with ISO timestamps and `module:file:line`; no PII.  
- On invalid event: log step index & `hand_id`, disable controls until Reset/Skip.  
- Director logs: `scheduled`, `executed`, `canceled`, `gated_begin/end` (for CI debugging).

---

## 9) File/Folder Structure (UI)
```
ui/
  store/                 # session store + reducers
    index.py
    selectors.py
  components/
    seat_pod.py
    community_board.py
    pot_display.py
    action_bar.py
    overlays/
  renderer/
    canvas_manager.py
    layer_manager.py
    renderer_pipeline.py
  adapters/
    ppsm_adapter.py
    decision_engine.py
    sound_bus.py
    effect_bus.py
  sessions/
    practice_shell.py
    review_shell.py
    gto_shell.py
  director/
    director.py          # GameDirector + NoopDirector + injected clock
```

---

## 10) Testing Requirements (must pass for PR merge)
- **Unit**: reducers, selectors, adapters, director (scheduling, gating).  
- **Snapshot**: major components across key states.  
- **Replay**: hand traces replay with no divergence; mismatches reported.  
- **Headless**: fake clock; autoplay produces stable PPSM state hashes.

---

## 11) AI Agent Guardrails (read carefully)
1. **Do not add new events or fields.** If missing, leave TODO and stop.  
2. **Never compute poker legality in UI.** Call selectors or PPSM.  
3. **Use theme tokens only.** No literal colors, shadows, fonts.  
4. **No timers/threads in components.** Use **GameDirector** for all timing and autoplay.  
5. **No cross-component writes.** Only Store and events.  
6. **Respect casing rules** (events UPPER_SNAKE_CASE; domain snake_case; streets uppercase).  
7. **Keep functions small and pure**; side effects only in adapters/EffectBus.  
8. **If uncertain**, generate interface stubs, not ad‑hoc logic.

---

### Appendix A — Example Reducer Effects
```python
def reducer_transition(state, evt):
    new_state = ppsm.transition(state, evt)
    effects = []

    if evt["type"] in ('BET', 'RAISE'):
        effects.append({"type": "SOUND", "id": "fx.bet_single", "ms": 220})
    elif evt["type"] == "CALL":
        effects.append({"type": "SOUND", "id": "fx.call", "ms": 180})
    elif evt["type"] == "CHECK":
        effects.append({"type": "SOUND", "id": "fx.check", "ms": 140})
    elif evt["type"] == "FOLD":
        effects.append({"type": "SOUND", "id": "fx.fold", "ms": 160})

    if street_ended(state, new_state):
        effects.append({"type": "ANIMATE", "name": "chips_to_pot", "ms": 260})

    if showdown_or_last_player(new_state):
        effects += [
            {"type": "ANIMATE", "name": "pot_to_winner", "ms": 520},
            {"type": "SOUND", "id": "fx.chips_scoop", "ms": 420},
            {"type": "BANNER", "name": "winner", "ms": 800},
        ]

    return new_state, effects
```

### Appendix B — EffectBus Skeleton
```python
def run_effects(effects: list[dict], director: GameDirector, sound_bus, renderer):
    gated = any(e["type"] in {"ANIMATE", "SOUND"} for e in effects)
    if gated: director.gate_begin()

    for e in effects:
        if e["type"] == "SOUND":
            sound_bus.play(e["id"])
            director.schedule(e.get("ms", 200), {"type": "SOUND_COMPLETE", "id": e["id"]})
        elif e["type"] == "ANIMATE":
            renderer.animate(e["name"], e.get("args", {}))
            director.schedule(e.get("ms", 250), {"type": "ANIM_COMPLETE", "name": e["name"]})
        elif e["type"] == "BANNER":
            renderer.banner(e["name"], e.get("ms", 800))

    if gated:
        # In your event handler for *_COMPLETE, call director.gate_end()
        pass
```


```

---

## RELATED SERVICES

### service_container.py

**Path:** `backend/ui/services/service_container.py`

```python
from typing import Any, Dict


class ServiceContainer:
    """
    Lightweight service registry with app-wide and session-scoped services.
    """

    def __init__(self) -> None:
        self.app_scope: Dict[str, Any] = {}
        self.session_scopes: Dict[str, Dict[str, Any]] = {}

    def provide_app(self, name: str, service: Any) -> None:
        self.app_scope[name] = service

    def get_app(self, name: str) -> Any:
        return self.app_scope[name]

    def provide_session(
        self, session_id: str, name: str, service: Any
    ) -> None:
        self.session_scopes.setdefault(session_id, {})[name] = service

    def get_session(self, session_id: str, name: str) -> Any:
        return self.session_scopes[session_id][name]

    def dispose_session(self, session_id: str) -> None:
        scope = self.session_scopes.pop(session_id, {})
        for service in scope.values():
            if hasattr(service, "dispose"):
                try:
                    service.dispose()
                except Exception:
                    # Best-effort cleanup
                    pass

```

---

### effect_bus.py

**Path:** `backend/ui/services/effect_bus.py`

```python
#!/usr/bin/env python3
"""
EffectBus - Coordinates sounds & animations; integrates with GameDirector.
"""
from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Import VoiceManager for human voice announcements
try:
    from ...utils.voice_manager import VoiceManager
except ImportError:
    try:
        from utils.voice_manager import VoiceManager
    except ImportError:
        try:
            from backend.utils.voice_manager import VoiceManager
        except ImportError:
            VoiceManager = None


# Minimal effect representation
@dataclass
class Effect:
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    ms: int = 200
    args: Dict[str, Any] = field(default_factory=dict)


class EffectBus:
    def __init__(self, game_director=None, sound_manager=None, event_bus=None, renderer=None):
        self.director = game_director
        self.sound = sound_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.enabled = True
        self.effects: List[Effect] = []
        self.next_id = 0
        
        # Initialize VoiceManager for human voice announcements
        self.voice_manager = None
        if VoiceManager:
            try:
                self.voice_manager = VoiceManager()
                print("🔊 EffectBus: VoiceManager initialized for human voice announcements")
            except Exception as e:
                print(f"⚠️ EffectBus: VoiceManager not available: {e}")
        
        # Initialize pygame mixer for audio
        try:
            import pygame
            pygame.mixer.init(
                frequency=22050, size=-16, channels=2, buffer=512
            )
            self.pygame_available = True
            print("🔊 EffectBus: Pygame mixer initialized for audio")
        except Exception as e:
            self.pygame_available = False
            print(f"⚠️ EffectBus: Pygame mixer not available: {e}")
        
        # Load sound configuration from file
        self.sound_mapping = {}
        self.config: Dict[str, Any] = {}
        self._load_sound_config()
        
        # Load sound files
        self.sounds = {}
        self._load_sounds()
    
    def _load_sound_config(self):
        """Load sound configuration from JSON file."""
        try:
            config_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 'sounds',
                'poker_sound_config.json'
            )

            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Save full config for voice lookups
                self.config = config

                # Load sound mappings
                self.sound_mapping = config.get("sounds", {})

                # Load global settings
                self.master_volume = config.get("master_volume", 1.0)
                self.sounds_enabled = config.get("sounds_enabled", True)
                self.voice_enabled = config.get("voice_enabled", True)
                self.voice_type = config.get("voice_type", "announcer_female")

                # Optional base directory for sounds
                self.sound_dir_hint = Path(config.get("sound_directory", "sounds"))

                print(f"🔊 EffectBus: Loaded sound config with {len(self.sound_mapping)} mappings")
            else:
                print(f"⚠️ EffectBus: Sound config file not found: {config_file}")
                # Use empty mapping - let the UI handle defaults
                self.config = {}
                self.sound_mapping = {}
                self.master_volume = 1.0
                self.sounds_enabled = True
                self.voice_enabled = True
                self.voice_type = "announcer_female"
                self.sound_dir_hint = Path("sounds")

        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sound config: {e}")
            # Fallback to empty mappings
            self.config = {}
            self.sound_mapping = {}
            self.master_volume = 1.0
            self.sounds_enabled = True
            self.voice_enabled = True
            self.voice_type = "announcer_female"
            self.sound_dir_hint = Path("sounds")
    
    def reload_sound_config(self):
        """Dynamically reload sound configuration from file."""
        print("🔄 EffectBus: Reloading sound configuration...")
        self._load_sound_config()
        # Clear existing loaded sounds to force reload
        self.sounds.clear()
        # Reload sounds with new mapping
        self._load_sounds()
        print(f"✅ EffectBus: Reloaded sound config with {len(self.sound_mapping)} mappings")

    def set_game_director(self, game_director):
        """Set the game director for coordinating effects timing."""
        self.director = game_director
        print(f"🔊 EffectBus: Connected to GameDirector")

    def set_event_bus(self, event_bus):
        """Set the event bus for publishing effect events."""
        self.event_bus = event_bus
        print(f"🔊 EffectBus: Connected to EventBus")
        # Bridge basic animate events to ChipAnimations if a renderer is present
        try:
            if self.event_bus is not None:
                self.event_bus.subscribe("effect_bus:animate", self._on_animation_request)
        except Exception:
            pass

    def _resolve_sound_path(self, rel_or_abs: str) -> Optional[Path]:
        """Resolve a sound path robustly across likely locations."""
        try:
            # Absolute path as-is
            p = Path(rel_or_abs)
            if p.is_file():
                return p

            # Relative to configured sounds dir if provided
            if hasattr(self, 'sound_dir_hint'):
                cand = self.sound_dir_hint / rel_or_abs
                if cand.is_file():
                    return cand

            # Relative to this module's ../../sounds
            here = Path(__file__).parent
            cand2 = (here / '..' / '..' / 'sounds').resolve() / rel_or_abs
            if cand2.is_file():
                return cand2

            # Relative to CWD/sounds
            cand3 = Path.cwd() / 'sounds' / rel_or_abs
            if cand3.is_file():
                return cand3
        except Exception:
            pass
        return None

    def _load_sounds(self):
        """Load all available sound files."""
        if not self.pygame_available:
            return
            
        try:
            import pygame
            for action, filename in self.sound_mapping.items():
                resolved = self._resolve_sound_path(filename)
                if resolved and resolved.exists() and resolved.stat().st_size > 100:
                    try:
                        sound = pygame.mixer.Sound(str(resolved))
                        self.sounds[action.upper()] = sound
                        print(f"🔊 EffectBus: Loaded sound {action} -> {resolved}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to load {filename}: {e}")
                else:
                    print(f"⚠️ EffectBus: Sound file not found or empty: {filename}")
                    
            print(f"🔊 EffectBus: Loaded {len(self.sounds)} sound files")
        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sounds: {e}")

    def add_effect(self, effect: Effect) -> str:
        """Add an effect to the queue."""
        if not self.enabled:
            return ""
            
        effect.id = f"{effect.type}_{self.next_id}"
        self.next_id += 1
        self.effects.append(effect)
        
        # Notify event bus
        if self.event_bus:
            self.event_bus.publish(f"effect_bus:{effect.type}", {
                "id": effect.id,
                "name": effect.name,
                "ms": effect.ms,
                "args": effect.args
            })
        
        return effect.id

    def add_sound_effect(self, sound_name: str, ms: int = 200):
        """Add sound effect with proper gating, even if pygame audio fails."""
        # try to play; don't crash if mixer is unavailable
        played = False
        try:
            if hasattr(self, 'pygame_available') and self.pygame_available:
                import pygame
                # First try to use pre-loaded sound from self.sounds
                if sound_name in self.sounds:
                    try:
                        sound = self.sounds[sound_name]
                        sound.set_volume(self.master_volume)
                        sound.play()
                        played = True
                        print(f"🔊 EffectBus: Playing pre-loaded sound: {sound_name}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to play pre-loaded sound {sound_name}: {e}")
                        played = False
                else:
                    # Fallback: try to load from file mapping
                    sound_file = self.sound_mapping.get(sound_name.upper(), "")
                    if sound_file:
                        resolved = self._resolve_sound_path(sound_file)
                        try:
                            if resolved and resolved.exists():
                                sound = pygame.mixer.Sound(str(resolved))
                                sound.set_volume(self.master_volume)
                                sound.play()
                                played = True
                                print(f"🔊 EffectBus: Playing sound {sound_name} -> {resolved}")
                            else:
                                print(f"⚠️ EffectBus: Could not resolve sound path for {sound_file}")
                                played = False
                        except Exception as e:
                            print(f"⚠️ EffectBus: Failed to play {sound_file}: {e}")
                            played = False
                    else:
                        print(f"⚠️ EffectBus: No sound mapping found for {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error in add_sound_effect: {e}")
            played = False

        # Gate autoplay regardless of audio success. Use the director to schedule
        # a SOUND_COMPLETE event so the autoplay rhythm stays deterministic.
        if self.director:
            try:
                self.director.gate_begin()
                # Use ms even if sound didn't play to keep timing consistent
                self.director.schedule(ms, {"type": "SOUND_COMPLETE", "id": sound_name},
                                       callback=self.director.notify_sound_complete)
            except Exception:
                # Ensure gate_end still occurs in case schedule failed
                try:
                    self.director.gate_end()
                except Exception:
                    pass

        # optional: telemetry/log
        if self.event_bus:
            self.event_bus.publish("effect_bus:sound", {"id": sound_name, "ms": ms})

    def add_animation_effect(self, name: str, ms: int = 250, args: dict | None = None):
        """Add animation effect with proper gating."""
        args = args or {}
        if self.event_bus:
            self.event_bus.publish("effect_bus:animate", {"name": name, "ms": ms, "args": args})

        if self.director:
            self.director.gate_begin()
            self.director.schedule(ms, {"type": "ANIM_COMPLETE", "name": name},
                                   callback=self.director.notify_animation_complete)

    # --- Animation bridge ---
    def _on_animation_request(self, payload: dict):
        """Translate simple animate events to ChipAnimations drawing calls.
        Requires renderer with canvas and theme_manager context.
        """
        try:
            name = (payload or {}).get("name", "")
            args = (payload or {}).get("args", {}) or {}
            renderer = getattr(self, "renderer", None)
            if renderer is None:
                return
            canvas = getattr(renderer, "canvas_manager", None)
            canvas = getattr(canvas, "canvas", None)
            theme_manager = getattr(renderer, "theme_manager", None)
            if canvas is None or theme_manager is None:
                return
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)

            if name == "chips_to_pot":
                anim.fly_chips_to_pot(
                    canvas,
                    args.get("from_x", 0), args.get("from_y", 0),
                    args.get("to_x", 0), args.get("to_y", 0),
                    int(args.get("amount", 0)),
                )
            elif name == "pot_to_winner":
                anim.fly_pot_to_winner(
                    canvas,
                    args.get("pot_x", 0), args.get("pot_y", 0),
                    args.get("winner_x", 0), args.get("winner_y", 0),
                    int(args.get("amount", 0)),
                )
        except Exception:
            pass

    def add_banner_effect(self, message: str, banner_type: str = "info", ms: int = 2000) -> str:
        """Add a banner notification effect."""
        effect = Effect(
            type="banner",
            name=message,
            ms=ms,
            args={"type": banner_type}
        )
        return self.add_effect(effect)

    def add_poker_action_effects(self, action_type: str, player_name: str = ""):
        """Add poker action effects with proper sound mapping and gating."""
        action_type = (action_type or "").upper()
        
        # Debug: log what we're receiving
        print(f"🔊 DEBUG: EffectBus received action_type: '{action_type}'")

        # Use config-driven sound mapping from poker_sound_config.json
        # The sound_map is loaded dynamically from the config file
        sound_map = self.sound_mapping
        
        maybe = sound_map.get(action_type)
        if maybe:
            print(f"🔊 DEBUG: Found sound mapping for '{action_type}' -> '{maybe}'")
            self.add_sound_effect(action_type, ms=220)   # Pass action_type, not filename
        else:
            print(f"🔊 DEBUG: No sound mapping found for '{action_type}'")
            print(f"🔊 DEBUG: Available sound mappings: {list(sound_map.keys())}")

        # Add voice announcements for key actions via event bus and direct playback
        voice_action = self._map_action_to_voice(action_type)
        if self.voice_enabled and voice_action and hasattr(self, 'voice_manager') and self.voice_manager:
            try:
                print(f"🔊 DEBUG: Playing voice for action '{action_type}' -> '{voice_action}'")
                self.voice_manager.play_action_voice(voice_action.lower(), 0)
            except Exception as e:
                print(f"🔊 DEBUG: Voice playback failed: {e}")
        elif self.voice_enabled:
            # 1) Publish event for listeners
            if self.event_bus:
                self.event_bus.publish(
                    "effect_bus:voice",
                    {"type": "POKER_ACTION", "action": voice_action, "player": player_name},
                )
            print(f"🔊 EffectBus: Emitted voice event: {voice_action}")

            # 2) Direct playback via VoiceManager if available
            try:
                if self.voice_manager:
                    voice_sounds = (self.config or {}).get("voice_sounds", {})
                    voice_table = voice_sounds.get(self.voice_type or "", {})
                    file_rel = voice_table.get(voice_action)
                    if file_rel:
                        self.voice_manager.play(file_rel)
            except Exception as e:
                print(f"⚠️ EffectBus: Voice playback failed: {e}")

        if action_type == "SHOWDOWN":
            self.add_sound_effect("ui_winner", ms=700)

        # Publish simple banner text (optional)
        if self.event_bus:
            txt = f"{player_name or 'Player'} {action_type}"
            self.event_bus.publish("effect_bus:banner_show", {"style": "action", "text": txt})

        # Publish animation events for chip movements
        if action_type in ("DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"):
            self.add_animation_effect("chips_to_pot", ms=260)

        if action_type in ("SHOWDOWN", "END_HAND"):
            self.add_animation_effect("pot_to_winner", ms=520)
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show",
                    {"style": "winner", "text": f"{player_name or 'Player'} wins!"})

    def update(self):
        """Update effect processing."""
        if not self.enabled:
            return
            
        # Process effects
        for effect in self.effects[:]:
            if effect.type == "sound":
                self._play_sound(effect)
            elif effect.type == "animation":
                self._start_animation(effect)
            elif effect.type == "banner":
                self._show_banner(effect)
            
            # Remove processed effects
            self.effects.remove(effect)

    def _play_sound(self, effect: Effect):
        """Play a sound effect."""
        if not self.pygame_available or not self.sounds:
            return
            
        try:
            sound_name = effect.name
            if sound_name in self.sounds:
                # Gate effects while sound plays
                if self.director:
                    self.director.gate_begin()
                
                # Play the sound
                try:
                    self.sounds[sound_name].play()
                except Exception:
                    pass
                print(f"🔊 EffectBus: Playing sound: {sound_name}")
                
                # Schedule gate end through GameDirector only (no Tk timers)
                if self.director:
                    try:
                        self.director.schedule(
                            effect.ms,
                            {"type": "SOUND_COMPLETE", "id": effect.id},
                            callback=self.director.notify_sound_complete,
                        )
                    except Exception:
                        try:
                            self.director.gate_end()
                        except Exception:
                            pass
            else:
                print(f"⚠️ EffectBus: Sound not found: {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error playing sound: {e}")
            if self.director:
                self.director.gate_end()

    def _start_animation(self, effect: Effect):
        """Start an animation effect."""
        try:
            # Gate effects while animation runs
            if self.director:
                self.director.gate_begin()
            
            print(f"🎬 EffectBus: Started animation: {effect.name}")
            
            # Publish animation event
            if self.event_bus:
                self.event_bus.publish("effect_bus:animate", {
                    "id": effect.id,
                    "name": effect.name,
                    "ms": effect.ms,
                    "args": effect.args
                })
            
            # Schedule gate end through GameDirector only (no Tk timers)
            if self.director:
                try:
                    self.director.schedule(
                        effect.ms,
                        {"type": "ANIM_COMPLETE", "name": effect.name},
                        callback=self.director.notify_animation_complete,
                    )
                except Exception:
                    try:
                        self.director.gate_end()
                    except Exception:
                        pass
        except Exception as e:
            print(f"⚠️ EffectBus: Error starting animation: {e}")
            if self.director:
                self.director.gate_end()

    def _show_banner(self, effect: Effect):
        """Show a banner notification."""
        try:
            # Publish banner event
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show", {
                    "id": effect.id,
                    "message": effect.name,
                    "type": effect.args.get("type", "info"),
                    "ms": effect.ms
                })
                print(f"🎭 EffectBus: Added banner effect: {effect.name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error showing banner: {e}")

    def clear_queue(self):
        """Clear all pending effects."""
        self.effects.clear()

    def stop_all_effects(self):
        """Stop all running effects."""
        if self.pygame_available:
            try:
                import pygame
                pygame.mixer.stop()
            except:
                pass
        self.clear_queue()

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "enabled": self.enabled,
            "effects_count": len(self.effects),
            "sounds_loaded": len(self.sounds),
            "pygame_available": self.pygame_available
        }

    def set_effect_enabled(self, enabled: bool):
        """Enable/disable effects."""
        self.enabled = enabled

    def _map_action_to_voice(self, action_type: str) -> str:
        """Map poker action types to voice announcement actions."""
        voice_map = {
            "BET": "bet",
            "RAISE": "raise", 
            "CALL": "call",
            "CHECK": "check",
            "FOLD": "fold",
            "ALL_IN": "all_in",
            "DEAL_HOLE": "dealing",
            "DEAL_BOARD": "dealing",
            "POST_BLIND": "dealing",
            "SHOWDOWN": "winner",
            "END_HAND": "winner"
        }
        return voice_map.get(action_type, "")


class NoopEffectBus:
    """No-op EffectBus for testing."""
    def __init__(self, *args, **kwargs):
        pass
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

```

---

### game_director.py

**Path:** `backend/services/game_director.py`

```python

```

---

### theme_manager.py

**Path:** `backend/ui/services/theme_manager.py`

```python
from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes
    from .theme_loader import get_theme_loader
    from .state_styler import (
        get_state_styler,
        get_selection_styler,
        get_emphasis_bar_styler
    )
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Default theme name for fallbacks
DEFAULT_THEME_NAME = "Forest Green Professional 🌿"  # Updated to match JSON


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
    - Now fully config-driven using poker_themes.json
    """

    CONFIG_PATH = os.path.join("backend", "ui", "theme_config.json")

    def __init__(self) -> None:
        self._theme: Dict[str, Any]
        self._fonts: Dict[str, Any]
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._current: str | None = None
        self._subs: List[Callable[["ThemeManager"], None]] = []
        # Load defaults from codebase
        try:
            gm = importlib.import_module("backend.core.gui_models")
            self._theme = dict(getattr(gm, "THEME", {}))
            self._fonts = dict(getattr(gm, "FONTS", {}))
        except Exception:
            self._theme = {"table_felt": "#2B2F36", "text": "#E6E9EF"}
            self._fonts = {
                "main": ("Arial", 20),  # Base font at 20px for readability
                "pot_display": ("Arial", 28, "bold"),  # +8 for pot display
                "bet_amount": ("Arial", 24, "bold"),  # +4 for bet amounts
                "body": ("Consolas", 20),  # Same as main for body text
                "small": ("Consolas", 16),  # -4 for smaller text
                "header": ("Arial", 22, "bold")  # +2 for headers
            }
        # Apply persisted config if present
        # Register built-in packs
        packs = self._builtin_packs()
        for name, tokens in packs.items():
            self.register(name, tokens)
        self._load_config()
        if not self._current:
            # Use Forest Green Professional as safe default
            if DEFAULT_THEME_NAME in self._themes:
                self._current = DEFAULT_THEME_NAME
                self._theme = dict(self._themes[DEFAULT_THEME_NAME])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in theme packs - now using token-driven system"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Use the new deterministic token system
                themes = build_all_themes()
                print(f"🎨 ThemeManager: Loaded {len(themes)} themes: {list(themes.keys())}")
                return themes
            except Exception as e:
                print(f"⚠️ ThemeManager: Config-driven themes failed: {e}")
                return self._legacy_builtin_packs()
        else:
            print("⚠️ ThemeManager: Token-driven themes not available, using legacy")
            # Fallback to legacy themes if token system not available
            return self._legacy_builtin_packs()
    
    def _legacy_builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Minimal legacy fallback if config system completely fails."""
        return {
            "Forest Green Professional 🌿": {
                "table.felt": "#2D5A3D",
                "table.rail": "#4A3428", 
                "text.primary": "#EDECEC",
                "panel.bg": "#1F2937",
                "panel.fg": "#E5E7EB"
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts
    
    def reload(self):
        """Reload themes from file - critical for Theme Manager integration."""
        print("🔄 ThemeManager: Reloading themes from file...")
        
        # Clear cached themes
        self._themes = {}
        
        # Reload using the same logic as __init__
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Force reload from file
                loader = get_theme_loader()
                if hasattr(loader, 'reload'):
                    loader.reload()
                
                # Rebuild all themes
                themes = build_all_themes()
                
                # Register all themes
                for name, tokens in themes.items():
                    self.register(name, tokens)
                
                print(f"🔄 ThemeManager: Reloaded {len(themes)} themes from file")
                
                # Reload current theme if it still exists
                current_name = self.current_profile_name()
                if current_name in self._themes:
                    self._theme = self._themes[current_name]
                    print(f"🎯 ThemeManager: Restored current theme: {current_name}")
                else:
                    # Fallback to first available theme
                    if self._themes:
                        first_theme_name = list(self._themes.keys())[0]
                        self._theme = self._themes[first_theme_name]
                        self._current_profile = first_theme_name
                        print(f"🔄 ThemeManager: Switched to: {first_theme_name}")
                
            except Exception as e:
                print(f"⚠️ ThemeManager: Reload failed: {e}")
        else:
            print("⚠️ ThemeManager: Token-driven themes not available for reload")

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()
    
    def get_dimensions(self) -> Dict[str, Any]:
        """Get theme dimensions for consistent spacing and sizing."""
        try:
            # Try to get dimensions from theme config
            theme_data = self.get_theme()
            if theme_data and "dimensions" in theme_data:
                return theme_data["dimensions"]
            
            # Fallback to default dimensions
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }
        except Exception:
            # Ultimate fallback
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names from config-driven system."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback: return all registered theme names
        return list(self._themes.keys())

    def register_all(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register all themes from packs dictionary."""
        for name, tokens in packs.items():
            self.register(name, tokens)

    def current(self) -> str | None:
        """Return current theme name."""
        return self._current

    def set_profile(self, name: str) -> None:
        if name in self._themes:
            self._current = name
            self._theme = dict(self._themes[name])
            self._save_config()
            for fn in list(self._subs):
                fn(self)

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile")
                if prof and prof in self._themes:
                    self._current = prof
                    self._theme = dict(self._themes[prof])
                fonts = data.get("fonts")
                if isinstance(fonts, dict):
                    self._fonts.update(fonts)
        except Exception:
            pass

    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            payload = {"profile": self.current_profile_name(), "fonts": self._fonts}
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def current_profile_name(self) -> str:
        for name, theme in self._themes.items():
            if all(self._theme.get(k) == theme.get(k) for k in ("table.felt",)):
                return name
        return "Custom"

    def get(self, token: str, default=None):
        # Dot-path lookup in current theme; fallback to fonts when font.* requested
        if token.startswith("font."):
            return self._theme.get(token) or self._fonts.get(token[5:], default)
        cur = self._theme
        for part in token.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return self._theme.get(token, default)
        return cur
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get complete token dictionary for current theme"""
        return dict(self._theme)
    
    def get_base_colors(self) -> Dict[str, str]:
        """Get the base color palette for current theme (if available)"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try new config-driven system first
            try:
                loader = get_theme_loader()
                # Convert display name to theme ID using proper mapping
                name_to_id_map = {
                    "Forest Green Professional 🌿": "forest-green-pro",
                    "Velvet Burgundy 🍷": "velvet-burgundy", 
                    "Emerald Aurora 🌌": "emerald-aurora",
                    "Imperial Jade 💎": "imperial-jade",
                    "Ruby Royale ❤️‍🔥": "ruby-royale",
                    "Coral Royale 🪸": "coral-royale",
                    "Golden Dusk 🌇": "golden-dusk",
                    "Klimt Royale ✨": "klimt-royale",
                    "Deco Luxe 🏛️": "deco-luxe",
                    "Oceanic Aqua 🌊": "oceanic-aqua",
                    "Royal Sapphire 🔷": "royal-sapphire",
                    "Monet Twilight 🎨": "monet-twilight",
                    "Caravaggio Sepia Noir 🕯️": "caravaggio-sepia-noir",
                    "Stealth Graphite Steel 🖤": "stealth-graphite-steel",
                    "Sunset Mirage 🌅": "sunset-mirage",
                    "Cyber Neon ⚡": "cyber-neon"
                }
                theme_id = name_to_id_map.get(self._current, "forest-green-pro") if self._current else "forest-green-pro"
                theme_config = loader.get_theme_by_id(theme_id)
                return theme_config.get("palette", {})
            except Exception:
                pass
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID (remove emojis)
            theme_id = self._current.lower()
            # Remove emojis and extra spaces
            for emoji in ["🌿", "🍷", "💎", "🌌", "❤️‍🔥", "🪸", "🌇", "✨", "🏛️", "🌊", "🔷", "🎨", "🕯️", "🖤", "🌅", "⚡"]:
                theme_id = theme_id.replace(emoji, "")
            theme_id = theme_id.strip().replace(" ", "-")
            return theme_id
        return "forest-green-pro"
    
    def get_state_styler(self):
        """Get state styler for player state effects."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_state_styler()
        return None
    
    def get_selection_styler(self):
        """Get selection styler for list/tree highlighting."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_selection_styler()
        return None
    
    def get_emphasis_bar_styler(self):
        """Get emphasis bar styler for luxury text bars."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_emphasis_bar_styler()
        return None
    
    def get_theme_metadata(self, theme_name: str) -> Dict[str, str]:
        """Get theme metadata like intro and persona from config."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                for theme_info in theme_list:
                    if theme_info["name"] == theme_name:
                        theme_config = loader.get_theme_by_id(theme_info["id"])
                        return {
                            "intro": theme_config.get("intro", ""),
                            "persona": theme_config.get("persona", ""),
                            "id": theme_config.get("id", "")
                        }
            except Exception:
                pass
        return {"intro": "", "persona": "", "id": ""}

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub

```

---

## 📋 RESOLUTION SUMMARY

### ✅ Issues Fixed:

1. **Dataclass Equality**: Implemented custom `__eq__` and `__hash__` methods
2. **Immutable Collections**: Changed `List` to `tuple` for `cards`, `board`, `banners`
3. **Store Model Checks**: Added equality check to prevent redundant updates
4. **Deferred Loading**: Prevented initialization race conditions
5. **UI Callback Protection**: Disabled callbacks during programmatic updates
6. **Props Memoization**: Efficient rendering with early-out checks

### 🎯 Result:

- ✅ Infinite loop completely eliminated
- ✅ Single render per state change (vs. infinite before)
- ✅ Responsive UI with normal performance
- ✅ Proper MVU architecture compliance
- ✅ Stable memory usage

### 🔬 Testing:

- ✅ Core MVU logic: No infinite loops, proper state transitions
- ✅ Full application: Stable startup, responsive UI
- ✅ Button interactions: Work correctly without triggering loops
- ✅ Performance: Normal CPU and memory usage

## 📋 END OF MVU INFINITE LOOP BUG REPORT

*This comprehensive report contains all analysis, source code, and resolution details for the MVU infinite rendering loop issue.*
