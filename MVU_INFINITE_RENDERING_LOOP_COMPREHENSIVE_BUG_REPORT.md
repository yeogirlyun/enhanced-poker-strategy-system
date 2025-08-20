# 🚨 MVU INFINITE RENDERING LOOP - COMPREHENSIVE BUG REPORT

**Issue**: MVU (Model-View-Update) poker hands review tab stuck in infinite rendering loop

**Symptoms**: Application becomes unresponsive due to continuous alternating renders between 0 and 2 seats

**Generated**: 2025-08-20 03:52:48

**Source Directory**: `/Users/yeogirlyun/Python/Poker`

---

## 🔍 DEBUG OUTPUT PATTERN

The following infinite loop pattern was observed:

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
[Pattern repeats infinitely...]
```

**Key Observation**: Despite identical cursor and waiting state values, `Props equal: False` and `Seats equal: False` always, indicating object identity issues.

---

## BUG REPORT SUMMARY

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

## MVU ARCHITECTURE - CORE FILES

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

@dataclass(frozen=True)
class SeatState:
    """State for a single seat at the poker table"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int  # Current bet amount
    folded: bool
    all_in: bool
    cards: List[str]  # Hole cards (visibility rules applied)
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


@dataclass(frozen=True)
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
    board: List[str]  # ["As", "Kd", "7h", ...]
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
    banners: List[Banner]
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
            board=[],
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
            banners=[],
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
class UpdateUI(Cmd):
    """Request UI update (for immediate rendering)"""
    pass


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

@dataclass(frozen=True)
class TableRendererProps:
    """Props derived from Model for the table renderer"""
    # Table state
    seats: Dict[int, SeatState]
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
    ScheduleTimer, UpdateUI, GetReviewEvent
)


def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """
    Pure update function - computes (Model', Cmds) from (Model, Msg)
    No I/O operations allowed inside reducers.
    """
    if isinstance(msg, NextPressed):
        return next_pressed_reducer(model)
    
    if isinstance(msg, AutoPlayToggled):
        return replace(model, autoplay_on=msg.on), [UpdateUI()]
    
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
        return replace(model, theme_id=msg.theme_id), [UpdateUI()]
    
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
    
    cmds.append(UpdateUI())
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
    cmds = [UpdateUI()]
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
        return replace(model, banners=current_banners), [UpdateUI()]
    
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
    
    return new_model, [UpdateUI()]


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
    return new_model, [GetReviewEvent(index=new_cursor), UpdateUI()]


def load_hand(model: Model, msg: LoadHand) -> Tuple[Model, List[Cmd]]:
    """Load new hand data"""
    
    hand_data = msg.hand_data
    
    # Extract hand information
    hand_id = hand_data.get("hand_id", "")
    seats_data = hand_data.get("seats", {})
    board = hand_data.get("board", [])
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
            cards=seat_data.get("cards", []),
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
    
    return new_model, [UpdateUI()]


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
    ScheduleTimer, PublishEvent, UpdateUI, GetReviewEvent,
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
            
            elif isinstance(cmd, UpdateUI):
                self._execute_update_ui(cmd)
            
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
    
    def _execute_update_ui(self, cmd: UpdateUI) -> None:
        """Execute UpdateUI command - triggers immediate re-render"""
        # This is handled by notifying subscribers, which happens automatically
        # after model updates. This command is mainly for explicit UI updates.
        print("🖥️ MVUStore: UI update requested")
    
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

### mvu/__init__.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/mvu/__init__.py`

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

## MVU HANDS REVIEW IMPLEMENTATION

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

## INTEGRATION AND APP SHELL

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

## DEPRECATED/LEGACY FILES (for reference)

### deprecated/hands_review_tab_legacy.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/tabs/deprecated/hands_review_tab_legacy.py`

```python
import tkinter as tk
from tkinter import ttk
import uuid
import time
from typing import Optional

# New UI Architecture imports
from ..state.actions import (
    SET_REVIEW_HANDS,
    SET_REVIEW_FILTER,
    SET_STUDY_MODE
)
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer
from ..services.game_director import GameDirector
from ..services.effect_bus import EffectBus
from ..services.hands_repository import HandsRepository, HandsFilter, StudyMode
from ..services.hands_review_session_manager import HandsReviewSessionManager

# PPSM architecture - using HandsReviewSessionManager and PokerTableRenderer as per architecture guidelines

# Import enhanced button components
try:
    from ..components.enhanced_button import PrimaryButton, SecondaryButton
except ImportError:
    # Fallback to basic buttons if enhanced buttons not available
    PrimaryButton = SecondaryButton = tk.Button

# Import ActionBanner for visual feedback
try:
    from ..components.action_banner import ActionBanner
except ImportError:
    print("⚠️ ActionBanner not available, using fallback")
    ActionBanner = None

# Core imports - fail fast if not available
USE_DEV_STUBS = True  # Temporarily use stubs to fix console error

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from core.hand_model import Hand
    from core.hand_model_decision_engine import HandModelDecisionEngine
    # PPSM imports instead of FPSM
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    # HandsReviewBotSession removed - using PPSMHandsReviewBotSession below
    from core.session_logger import get_session_logger
            # Sound manager for poker table
    from utils.sound_manager import SoundManager
except ImportError as e:
    if not USE_DEV_STUBS:
        raise ImportError(f"Critical core modules not available: {e}. This will break hands review functionality.") from e
    print("⚠️ Using dev stubs due to import error:", e)
    
    # Minimal stubs for development only
    class Hand:
        def __init__(self, data):
            if isinstance(data, dict):
                self.hand_id = data.get("hand_id", "Unknown")
                self.players = data.get("players", [])
                self.pot_size = data.get("pot_size", 0)
                self.small_blind = data.get("small_blind", 5)
                self.big_blind = data.get("big_blind", 10)
                self.community_cards = data.get("community_cards", [])
                self.dealer = data.get("dealer", 0)
                self.__dict__.update(data)

        @classmethod
        def from_dict(cls, data):
            return cls(data)

    class HandModelDecisionEngine:
        def __init__(self, hand):
            pass

        def is_session_complete(self):
            return False

    class GameConfig:
        def __init__(self, **kwargs):
            pass

    def get_session_logger():
        class FallbackLogger:
            def log_system(self, *args, **kwargs):
                pass

        return FallbackLogger()


# Session manager will be initialized in the tab
# HandsReviewSessionManager handles all business logic per architecture guidelines

    




    """Concrete wrapper for HandModelDecisionEngine."""

    def __init__(self, hand):
        self.hand = hand
        try:
            if HandModelDecisionEngine and hand:
                self._engine = HandModelDecisionEngine.__new__(HandModelDecisionEngine)
                self._engine.hand = hand
                if hasattr(self._engine, "_organize_actions_by_street"):
                    self._engine.actions_by_street = (
                        self._engine._organize_actions_by_street()
                    )
                self._engine.current_action_index = 0
                if hasattr(self._engine, "_get_betting_actions"):
                    self._engine.actions_for_replay = (
                        self._engine._get_betting_actions()
                    )
                    self._engine.total_actions = len(self._engine.actions_for_replay)
                else:
                    self._engine.actions_for_replay = []
                    self._engine.total_actions = 0
            else:
                self._engine = None
        except Exception as e:
            print(f"❌ Error initializing decision engine: {e}")
            self._engine = None

    def get_decision(self, player_index: int, game_state):
        if self._engine and hasattr(self._engine, "get_decision"):
            return self._engine.get_decision(player_index, game_state)
        return {
            "action": "fold",
            "amount": 0,
            "explanation": "Default action",
            "confidence": 0.5,
        }

    def is_session_complete(self):
        if self._engine and hasattr(self._engine, "is_session_complete"):
            return self._engine.is_session_complete()
        return True

    def reset(self):
        if self._engine and hasattr(self._engine, "reset"):
            self._engine.reset()

    def get_session_info(self):
        if self._engine and hasattr(self._engine, "hand"):
            # Handle both fallback Hand class (hand.hand_id) and real Hand class (hand.metadata.hand_id)
            hand_id = "Unknown"
            if hasattr(self._engine.hand, "hand_id"):
                hand_id = self._engine.hand.hand_id
            elif hasattr(self._engine.hand, "metadata") and hasattr(
                self._engine.hand.metadata, "hand_id"
            ):
                hand_id = self._engine.hand.metadata.hand_id

            return {
                "hand_id": hand_id,
                "total_actions": getattr(self._engine, "total_actions", 0),
                "current_action": getattr(self._engine, "current_action_index", 0),
                "engine_type": "HandModelDecisionEngine",
            }
        return {
            "hand_id": "Unknown",
            "total_actions": 0,
            "current_action": 0,
            "engine_type": "Fallback",
        }


class HandsReviewTab(ttk.Frame):
    """Hands Review tab implementing the full PRD requirements."""

    def __init__(self, parent, services: ServiceContainer):
        super().__init__(parent)
        self.services = services
        self.session_id = f"hands_review_{uuid.uuid4().hex[:8]}"

        # Get app services
        self.event_bus: EventBus = services.get_app("event_bus")
        self.store: Store = services.get_app("store")
        self.theme = services.get_app("theme")
        self.hands_repository: HandsRepository = services.get_app("hands_repository")
        # Sounds are owned by EffectBus per architecture; no local fallback

        # Session state - using HandsReviewSessionManager per architecture guidelines
        self.session_manager: Optional[HandsReviewSessionManager] = None
        self.session_active = False
        
        # Use global services from service container for proper coordination
        self.game_director = self.services.get_app("game_director")
        if not self.game_director:
            # Create global GameDirector if not exists
            self.game_director = GameDirector(event_bus=self.event_bus)
            self.services.provide_app("game_director", self.game_director)
        
        # Use global EffectBus service for proper event coordination
        self.effect_bus = self.services.get_app("effect_bus")
        if not self.effect_bus:
            # Create global EffectBus if not exists
            self.effect_bus = EffectBus(
                game_director=self.game_director,
                event_bus=self.event_bus
            )
            self.services.provide_app("effect_bus", self.effect_bus)
        
        # Ensure proper connections for event coordination
        self.game_director.set_event_bus(self.event_bus)
        self.effect_bus.set_game_director(self.game_director)
        self.effect_bus.set_event_bus(self.event_bus)
        
        # Initialize HandsReviewSessionManager per architecture guidelines
        try:
            # Try direct import first
            try:
                from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
            except ImportError:
                # Fallback to relative import
                from ...core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
                
            # Create a default game config for hands review
            game_config = GameConfig(
                num_players=6,  # Default to 6 players for hands review
                small_blind=1.0,
                big_blind=2.0,
                starting_stack=1000.0
            )
            
            ppsm = PurePokerStateMachine(config=game_config)
            self.session_manager = HandsReviewSessionManager(
                store=self.store,
                ppsm=ppsm,
                game_director=self.game_director,
                effect_bus=self.effect_bus,
                event_bus=self.event_bus
            )
            
            # ARCHITECTURE COMPLIANT: Register session with event controller
            try:
                hands_review_controller = self.services.get_app("hands_review_controller")
                if hands_review_controller:
                    self.event_bus.publish(
                        "hands_review:session_created",
                        {
                            "session_id": self.session_id,
                            "session_manager": self.session_manager
                        }
                    )
                    print(f"🎯 HandsReviewTab: Session {self.session_id} registered with event controller")
            except Exception as e:
                print(f"⚠️ HandsReviewTab: Failed to register session: {e}")
            print("🎯 HandsReviewTab: Session manager initialized per architecture guidelines")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Could not initialize session manager: {e}")
            self.session_manager = None

        # Setup UI
        self.on_mount()

        # Subscribe to events and store changes
        self._setup_event_subscriptions()
        self.store.subscribe(self._on_store_change)

        # Initialize GTO hands for PPSM testing
        self.loaded_gto_hands = []
        # GTO hands will be loaded in on_mount() to ensure proper UI initialization order

    def on_mount(self):
        """Set up the tab layout per PRD design."""
        # Two-column layout: Controls (20%) | Poker Table (80%)
        # Using 1:4 ratio for poker table emphasis
        self.grid_columnconfigure(0, weight=1)  # Library + Filters & Controls (20%)
        self.grid_columnconfigure(1, weight=4)  # Poker Table (80%)
        self.grid_rowconfigure(0, weight=1)

        # Create the two main sections
        self._create_combined_left_section()
        self._create_poker_table_section()
        
        # Load GTO hands for PPSM testing
        self._load_gto_hands()
        
        # Refresh hands list now that GTO hands are loaded
        self._refresh_hands_list()
        
        # Start main update loop for GameDirector and EffectBus
        self._start_update_loop()
        
        # Setup ActionBanner for visual feedback
        self._setup_action_banner()
        
        # Start the UI tick loop for GameDirector and EffectBus
        self._start_ui_tick_loop()

    def _create_combined_left_section(self):
        """Create the combined left section with hands library and controls."""
        # Get theme colors
        theme = self.theme.get_theme()

        # Main left frame
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2.5), pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=60)  # Hands library gets 60%
        left_frame.grid_rowconfigure(1, weight=40)  # Controls get 40%

        # Apply theme colors to main left frame
        try:
            left_frame.configure(background=theme.get("panel.bg", "#111827"))
        except Exception:
            pass

        # Create library section at top
        self._create_library_section_in_frame(left_frame)

        # Create filters/controls section at bottom
        self._create_filters_section_in_frame(left_frame)

    def _create_library_section_in_frame(self, parent):
        """Create the Library section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()

        library_frame = ttk.LabelFrame(parent, text="📚 Hands Library", padding=10)
        library_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 2.5))

        # Apply theme colors to the frame
        try:
            library_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass  # Fallback to default colors if theming fails
        library_frame.grid_columnconfigure(0, weight=1)
        library_frame.grid_rowconfigure(
            3, weight=1
        )  # Hands list gets most space (shifted down due to theme selector)

        # Theme selector (at top) - 5 Professional Casino Schemes
        theme_frame = ttk.LabelFrame(
            library_frame, text="🎨 Professional Casino Themes", padding=5
        )
        theme_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(0, weight=1)

        theme_controls = ttk.Frame(theme_frame)
        theme_controls.grid(row=0, column=0, sticky="ew")

        current_theme = self.theme.current_profile_name()
        self.theme_var = tk.StringVar(value=current_theme)

        # All available themes from ThemeManager
        all_theme_names = self.theme.names()
        print(
            f"🎨 HandsReviewTab: Found {len(all_theme_names)} themes: {all_theme_names}"
        )

        # Fallback if no themes found
        if not all_theme_names:
            print("⚠️ No themes found, forcing theme manager reload...")
            # Try to reload theme manager
            try:
                from ..services.theme_factory import build_all_themes

                themes = build_all_themes()
                print(f"🔄 Force-built {len(themes)} themes: {list(themes.keys())}")
                # Register them with the theme manager
                for name, tokens in themes.items():
                    self.theme.register(name, tokens)
                all_theme_names = self.theme.names()
                print(
                    f"🎨 After reload: {len(all_theme_names)} themes: {all_theme_names}"
                )
            except Exception as e:
                print(f"❌ Failed to reload themes: {e}")
                # Get actual theme names from config, with ultimate fallback
                default_theme_data = self.theme.get_available_themes()
                all_theme_names = (
                    list(default_theme_data.keys())
                    if default_theme_data
                    else ["Forest Green Professional 🌿"]
                )

        # Theme icons are now embedded in theme names from JSON config
        # No need for separate THEME_ICONS or THEME_INTROS - all data comes from poker_themes.json

        # Create clean 4x4 grid layout for 16 themes with 20px font
        # Configure grid weights for even distribution
        for col_idx in range(4):
            theme_controls.grid_columnconfigure(col_idx, weight=1)

        for i, theme_name in enumerate(all_theme_names):
            row = i // 4  # 4 themes per row
            col = i % 4

            # Theme names from JSON config already include icons and formatting
            display_name = theme_name

            # Simple radiobutton with 20px font and equal spacing
            radio_btn = ttk.Radiobutton(
                theme_controls,
                text=display_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._on_theme_change,
            )
            radio_btn.grid(row=row, column=col, sticky="w", padx=5, pady=3)

            # Configure font size to 20px and store reference for styling
            try:
                fonts = self.theme.get_fonts()
                radio_font = fonts.get(
                    "button", fonts.get("body", ("Inter", 20, "normal"))
                )
                radio_btn.configure(font=radio_font)
            except:
                # Fallback if font configuration fails
                pass

            # Store radio button reference for theme styling
            if not hasattr(self, "theme_radio_buttons"):
                self.theme_radio_buttons = []
            self.theme_radio_buttons.append(radio_btn)

            # Theme intro will update only on selection, not hover
            # Removed confusing hover effects that changed intro on mouse over

        # Apply initial theme styling to radio buttons
        self.after_idle(self._style_theme_radio_buttons)

        # Artistic Theme Info Panel - shows evocative descriptions (positioned AFTER theme controls)
        info_frame = ttk.Frame(theme_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        # Luxury Museum Placard - Theme intro with elegant styling
        fonts = self.theme.get_fonts()
        # Use theme-aware font for luxury feel
        fonts = self.theme.get_fonts()
        intro_font = fonts.get("intro", fonts.get("body", ("Georgia", 16, "normal")))

        # Create luxury museum placard frame with theme-aware styling
        base_colors = self.theme.get_base_colors()
        placard_bg = base_colors.get("panel_bg", "#2A2A2A")
        placard_accent = base_colors.get("highlight", "#D4AF37")

        placard_frame = tk.Frame(
            info_frame,
            relief="raised",
            borderwidth=2,
            bg=placard_bg,
            highlightbackground=placard_accent,
            highlightcolor=placard_accent,
            highlightthickness=1,
        )
        # Use theme dimensions for consistent spacing
        dimensions = self.theme.get_dimensions()
        medium_pad = dimensions["padding"]["medium"]
        placard_frame.grid(
            row=0, column=0, sticky="ew", padx=medium_pad, pady=medium_pad
        )
        placard_frame.grid_columnconfigure(0, weight=1)

        # Store reference to placard frame for dynamic styling
        self.placard_frame = placard_frame

        # Get initial theme colors instead of hardcoding
        base_colors = self.theme.get_base_colors()
        initial_bg = base_colors.get("panel_bg", "#1A1A1A")
        initial_fg = base_colors.get("text", "#F5F5DC")

        intro_height = dimensions["text_height"][
            "medium"
        ]  # Use medium instead of small for theme intros
        self.theme_intro_label = tk.Text(
            placard_frame,
            height=intro_height,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            font=intro_font,
            state="disabled",
            cursor="arrow",
            padx=dimensions["padding"]["xlarge"],
            pady=dimensions["padding"]["medium"],
            bg=initial_bg,
            fg=initial_fg,
        )  # Dynamic theme colors
        self.theme_intro_label.grid(row=0, column=0, sticky="ew")

        # Show current theme's introduction
        self._show_theme_intro(current_theme)

        # Library type selector
        type_frame = ttk.Frame(library_frame)
        type_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        type_frame.grid_columnconfigure(0, weight=1)

        self.library_type = tk.StringVar(value="legendary")
        ttk.Radiobutton(
            type_frame,
            text="🏆 Legendary",
            variable=self.library_type,
            value="legendary",
            command=self._on_library_type_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="🤖 Bot Sessions",
            variable=self.library_type,
            value="bot",
            command=self._on_library_type_change,
        ).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="📥 Imported",
            variable=self.library_type,
            value="imported",
            command=self._on_library_type_change,
        ).grid(row=0, column=2, sticky="w")

        # Collections dropdown
        collections_frame = ttk.Frame(library_frame)
        collections_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        collections_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(collections_frame, text="Collection:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.collection_var = tk.StringVar(value="🤖 GTO Hands")
        self.collection_combo = ttk.Combobox(
            collections_frame, textvariable=self.collection_var, state="readonly"
        )
        self.collection_combo.grid(row=0, column=1, sticky="ew")
        self.collection_combo.bind("<<ComboboxSelected>>", self._on_collection_change)

        # Hands listbox
        hands_frame = ttk.Frame(library_frame)
        hands_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        hands_frame.grid_columnconfigure(0, weight=1)
        hands_frame.grid_rowconfigure(0, weight=1)

        # Get fonts from theme
        fonts = self.theme.get_fonts()
        body_font = fonts.get("body", ("Consolas", 20))

        self.hands_listbox = tk.Listbox(
            hands_frame, font=body_font, selectmode=tk.SINGLE
        )
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        self.hands_listbox.bind("<<ListboxSelect>>", self._on_hand_select)

        # Apply theme colors to listbox with dynamic selection highlight
        try:
            # Get theme-specific selection highlight
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            # Get selection highlight from config-driven system
            base_colors = self.theme.get_base_colors()
            selection_highlight = {
                "color": base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
            }

            self.hands_listbox.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                selectbackground=selection_highlight[
                    "color"
                ],  # Dynamic theme-specific highlight
                selectforeground=base_colors.get(
                    "highlight_text", base_colors.get("text", "#FFFFFF")
                ),  # Theme-aware text when highlighted
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        scrollbar = ttk.Scrollbar(
            hands_frame, orient="vertical", command=self.hands_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.configure(yscrollcommand=scrollbar.set)

        # Hand details text (smaller in the combined layout)
        details_frame = ttk.LabelFrame(library_frame, text="Hand Details", padding=5)
        details_frame.grid(row=5, column=0, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)

        small_font = fonts.get("small", ("Consolas", 16))
        details_height = self.theme.get_dimensions()["text_height"]["medium"]
        self.details_text = tk.Text(
            details_frame, height=details_height, wrap=tk.WORD, font=small_font
        )
        self.details_text.grid(row=0, column=0, sticky="ew")

        # Apply theme colors to details text
        try:
            self.details_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

    def _create_filters_section_in_frame(self, parent):
        """Create the Filters & Controls section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()

        filters_frame = ttk.LabelFrame(
            parent, text="🔍 Filters & Study Mode", padding=10
        )
        filters_frame.grid(row=1, column=0, sticky="nsew", pady=(2.5, 0))

        # Apply theme colors to the frame
        try:
            filters_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass
        filters_frame.grid_columnconfigure(0, weight=1)

        # Study Mode selector
        study_frame = ttk.LabelFrame(filters_frame, text="Study Mode", padding=5)
        study_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.study_mode = tk.StringVar(value=StudyMode.REPLAY.value)
        ttk.Radiobutton(
            study_frame,
            text="🔄 Replay",
            variable=self.study_mode,
            value=StudyMode.REPLAY.value,
            command=self._on_study_mode_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="📊 Solver Diff",
            variable=self.study_mode,
            value=StudyMode.SOLVER_DIFF.value,
            command=self._on_study_mode_change,
        ).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="🧠 Recall Quiz",
            variable=self.study_mode,
            value=StudyMode.RECALL_QUIZ.value,
            command=self._on_study_mode_change,
        ).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="❓ Explain Mistake",
            variable=self.study_mode,
            value=StudyMode.EXPLAIN_MISTAKE.value,
            command=self._on_study_mode_change,
        ).grid(row=3, column=0, sticky="w")

        # Filters section
        filter_frame = ttk.LabelFrame(filters_frame, text="Filters", padding=5)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        # Position filter
        ttk.Label(filter_frame, text="Position:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.position_var = tk.StringVar(value="All")
        position_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.position_var,
            values=["All", "UTG", "MP", "CO", "BTN", "SB", "BB"],
            state="readonly",
            width=8,
        )
        position_combo.grid(row=0, column=1, sticky="w", pady=2)

        # Stack depth filter
        ttk.Label(filter_frame, text="Stack Depth:").grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        stack_frame = ttk.Frame(filter_frame)
        stack_frame.grid(row=1, column=1, sticky="w", pady=2)
        self.min_stack = tk.StringVar(value="20")
        self.max_stack = tk.StringVar(value="200")
        ttk.Entry(stack_frame, textvariable=self.min_stack, width=5).grid(
            row=0, column=0
        )
        ttk.Label(stack_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(stack_frame, textvariable=self.max_stack, width=5).grid(
            row=0, column=2
        )
        ttk.Label(stack_frame, text=" BB").grid(row=0, column=3)

        # Pot type filter
        ttk.Label(filter_frame, text="Pot Type:").grid(
            row=2, column=0, sticky="w", padx=(0, 5)
        )
        self.pot_type_var = tk.StringVar(value="All")
        pot_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.pot_type_var,
            values=["All", "SRP", "3BP", "4BP+"],
            state="readonly",
            width=8,
        )
        pot_combo.grid(row=2, column=1, sticky="w", pady=2)

        # Search text
        ttk.Label(filter_frame, text="Search:").grid(
            row=3, column=0, sticky="w", padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=3, column=1, sticky="ew", pady=2)
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        # Apply filters button
        ttk.Button(
            filter_frame, text="Apply Filters", command=self._apply_filters
        ).grid(row=4, column=0, columnspan=2, pady=5)

        # Action buttons
        actions_frame = ttk.LabelFrame(filters_frame, text="Actions", padding=5)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        actions_frame.grid_columnconfigure(0, weight=1)

        # Load button (main action) - Enhanced primary button
        self.load_btn = PrimaryButton(
            actions_frame,
            text="🔥 LOAD HAND",
            command=self._load_selected_hand,
            theme_manager=self.theme,
        )
        self.load_btn.grid(row=0, column=0, sticky="ew", pady=5)

        # Enhanced button handles its own styling

        # Playback controls
        controls_frame = ttk.Frame(actions_frame)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Enhanced buttons handle their own styling

        # Enhanced secondary buttons for controls
        self.next_btn = SecondaryButton(
            controls_frame,
            text="Next →",
            command=self._next_action,  # Use session manager method
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        self.auto_btn = SecondaryButton(
            controls_frame,
            text="Auto",
            command=self._toggle_auto_play,  # Use session manager method
            theme_manager=self.theme,
        )
        self.auto_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = SecondaryButton(
            controls_frame,
            text="Reset",
            command=self._reset_hand,  # Use session manager method
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=2, padx=(5, 0))

        # Enhanced buttons handle their own styling

        # Status text
        status_frame = ttk.LabelFrame(filters_frame, text="Status", padding=5)
        status_frame.grid(row=3, column=0, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)

        fonts = self.theme.get_fonts()
        small_font = fonts.get("small", ("Consolas", 16))
        status_height = self.theme.get_dimensions()["text_height"]["large"]
        self.status_text = tk.Text(
            status_frame, height=status_height, wrap=tk.WORD, font=small_font
        )
        self.status_text.grid(row=0, column=0, sticky="nsew")

        # Apply theme colors to status text
        try:
            self.status_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        # Poker Table Controls
        poker_frame = ttk.LabelFrame(actions_frame, text="🎮 Poker Table Controls", padding=5)
        poker_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        poker_frame.grid_columnconfigure(1, weight=1)

        # Next Action button for poker table
        self.next_btn = SecondaryButton(
            poker_frame,
            text="▶ Next Action",
            command=self._next_action,
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        # Reset button for poker table
        self.reset_btn = SecondaryButton(
            poker_frame,
            text="↩ Reset Hand",
            command=self._reset_hand,
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=1, padx=5)

        # Progress display for poker table
        self.progress_label = ttk.Label(poker_frame, text="No hand loaded")
        self.progress_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Enhanced buttons handle their own styling

    def _create_poker_table_section(self):
        """Create poker table using PokerTableRenderer (right column)."""
        # Get theme colors for poker table
        theme = self.theme.get_theme()

        table_frame = ttk.LabelFrame(self, text="♠️ Enhanced Poker Table", padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(2.5, 5), pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Apply theme colors to table frame
        try:
            table_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass

        # Create PokerTableRenderer directly in the table frame
        self._setup_poker_table(table_frame)
        
        print(f"🎯 HandsReviewTab: Table frame created and configured")
        print(f"   Frame size: {table_frame.winfo_width()}x{table_frame.winfo_height()}")
        print(f"   Table renderer created: {hasattr(self, 'table_renderer')}")

    def _setup_poker_table(self, parent_frame):
        """Set up the PokerTableRenderer with poker table display."""
        # Do not force early geometry; allow CanvasManager to handle readiness
        parent_frame.grid_propagate(False)
        frame_width = parent_frame.winfo_width()
        frame_height = parent_frame.winfo_height()
        table_width = max(1200, max(0, frame_width) - 20) if frame_width > 0 else 1200
        table_height = max(800, max(0, frame_height) - 20) if frame_height > 0 else 800
        
        # Calculate card size based on table dimensions
        card_width = max(40, int(table_width * 0.035))
        card_height = int(card_width * 1.45)
        
        print(f"🎯 HandsReviewTab: Initial frame {frame_width}x{frame_height}, desired table {table_width}x{table_height}")
        
        # Use PokerTableRenderer as per architecture guidelines
        from ..renderers.poker_table_renderer import PokerTableRenderer

        self.table_renderer = PokerTableRenderer(
            parent_frame,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme if hasattr(self, 'theme') else None,
        )
        self.table_renderer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        
        # Access canvas manager through renderer for legacy compatibility
        self.canvas_manager = self.table_renderer.canvas_manager
        # layer_manager may not be available immediately due to deferred initialization
        if hasattr(self.table_renderer, 'layer_manager'):
            self.layer_manager = self.table_renderer.layer_manager
        else:
            self.layer_manager = None
        
        # Link EffectBus to renderer so animation bridge can draw chips
        try:
            if hasattr(self, 'effect_bus'):
                self.effect_bus.renderer = self.table_renderer
        except Exception:
            pass
        
        # Accumulate declarative effects per frame
        self._pending_effects = []
        
        # Store dimensions for state management
        self.table_width = table_width
        self.table_height = table_height
        self.card_width = card_width
        self.card_height = card_height
        
        # Initialize poker table state
        self._setup_poker_table_state()
        
        # Force table to expand to fill available space
        self._force_table_expansion()

        # Bind a one-time resize to trigger first render when ready via CanvasManager
        try:
            self._resize_bound = False
            def _on_parent_configure(event):
                if getattr(self, '_resize_bound', False):
                    return
                if event.width > 100 and event.height > 100:
                    self._resize_bound = True
                    self.table_width = event.width - 20
                    self.table_height = event.height - 20
                    try:
                        self._render_poker_table()
                    except Exception:
                        pass
            parent_frame.bind('<Configure>', _on_parent_configure)
        except Exception:
            pass
        
        print("🎨 PokerTableRenderer components ready")

    def _retry_frame_sizing(self, parent_frame):
        """Retry getting frame dimensions after a delay."""
        try:
            # Get updated frame dimensions
            frame_width = parent_frame.winfo_width()
            frame_height = parent_frame.winfo_height()
            
            if frame_width > 100 and frame_height > 100:
                # Frame is now properly sized, update table dimensions
                table_width = frame_width - 20
                table_height = frame_height - 20
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update canvas size
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    self.canvas_manager.canvas.configure(
                        width=table_width, 
                        height=table_height
                    )
                
                print(f"🎯 HandsReviewTab: Retry successful, updated to {table_width}x{table_height}")
                
                # Force table expansion
                self._force_table_expansion()
            else:
                # Still too small, try again via GameDirector
                if hasattr(self, 'game_director') and self.game_director:
                    self.game_director.schedule(100, {
                        "type": "RETRY_FRAME_SIZING",
                        "callback": lambda: self._retry_frame_sizing(parent_frame)
                    })
                else:
                    # Fallback: use timing helper
                    if hasattr(self, 'timing_helper') and self.timing_helper:
                        self.timing_helper.schedule_event(
                            delay_ms=100,
                            timing_type="delayed_action",
                            callback=lambda: self._retry_frame_sizing(parent_frame),
                            component_name="hands_review_tab"
                        )
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Retry sizing error: {e}")

    def _force_table_expansion(self):
        """Force the poker table to expand and fill the available space."""
        try:
            # Get the parent frame
            if hasattr(self, 'table_renderer') and self.table_renderer:
                parent_frame = self.table_renderer.master
                
                # Force geometry update
                parent_frame.update_idletasks()
                
                # Configure grid weights to ensure expansion
                parent_frame.grid_columnconfigure(0, weight=1)
                parent_frame.grid_rowconfigure(0, weight=1)
                
                # Force the table renderer to expand
                self.table_renderer.grid_configure(sticky="nsew")
                
                # Update canvas size to fill available space
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    # Get current frame dimensions
                    frame_width = parent_frame.winfo_width()
                    frame_height = parent_frame.winfo_height()
                    
                    # Use reasonable dimensions if frame is too small
                    if frame_width <= 100 or frame_height <= 100:
                        frame_width = 800
                        frame_height = 600
                    
                    # Set canvas size to fill frame
                    canvas_width = frame_width - 20  # Leave padding
                    canvas_height = frame_height - 20
                    
                    self.canvas_manager.canvas.configure(
                        width=canvas_width, 
                        height=canvas_height
                    )
                    
                    # Update stored dimensions
                    self.table_width = canvas_width
                    self.table_height = canvas_height
                    
                    print(f"🎯 HandsReviewTab: Forced table expansion to {canvas_width}x{canvas_height}")
                    
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Table expansion error: {e}")

    def _setup_poker_table_state(self):
        """Initialize state management for the poker table."""
        # Initialize display state for the poker table with placeholder data for visual testing
        self.display_state = {
            'table': {
                'width': self.table_width,
                'height': self.table_height
            },
            'pot': {
                'amount': 0.0,
                'side_pots': []
            },
            'seats': [
                # Placeholder seat 1 (top)
                {
                    'player_uid': 'placeholder_1',
                    'name': 'Player 1',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Ah', 'Kh'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 0
                },
                # Placeholder seat 2 (bottom) 
                {
                    'player_uid': 'placeholder_2',
                    'name': 'Player 2',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Qd', 'Jd'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 1
                }
            ],
            'board': [],  # Empty board initially (will show 5 card backs)
            'street': 'PREFLOP',  # Current street for community card rendering
            'dealer': {
                'position': 0
            },
            'action': {
                'current_player': -1,
                'action_type': None,
                'amount': 0.0,
                'highlight': False
            },
            'replay': {
                'active': False,
                'current_action': 0,
                'total_actions': 0,
                'description': "No hand loaded - showing placeholder state"
            }
        }
        
        print("🎯 HandsReviewTab state management ready with placeholder seats for visual testing")

    def _setup_event_subscriptions(self):
        """Subscribe to relevant events."""
        # Subscribe to review:load events as per architecture doc
        self.event_bus.subscribe(
            self.event_bus.topic(self.session_id, "review:load"),
            self._handle_load_hand_event,
        )

    def _refresh_hands_list(self):
        """Refresh the hands list based on current filters - prioritize GTO hands for PPSM."""
        # Check collection selection
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        # Load hands based on selection
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            # Repository hands (legendary hands)
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"

        print(f"🎯 HandsReviewTab: Loading {len(hands)} hands from {hands_source}")

        # Dispatch to store - convert Hand objects to dict format if needed
        hands_for_store = []
        for hand in hands:
            if hasattr(hand, 'metadata'):  # Hand object
                hands_for_store.append({
                    'hand_id': hand.metadata.get('hand_id', 'Unknown'),
                    'players': hand.seats,
                    'pot_size': hand.metadata.get('pot_size', 0)
                })
            else:  # Already dict format
                hands_for_store.append(hand)
                
        self.store.dispatch({"type": SET_REVIEW_HANDS, "hands": hands_for_store})

        # Update UI display
        self.hands_listbox.delete(0, tk.END)
        for i, hand in enumerate(hands):
            try:
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', f'GTO_Hand_{i+1}')
                    players_count = len(hand.seats) if hasattr(hand, 'seats') else 2
                    display_text = f"{hand_id} | {players_count}p | PPSM Ready"
                else:  # Dict format
                    hand_id = hand.get("hand_id", f"Hand_{i+1}")
                    # GTO hands use 'seats', regular hands use 'players'
                    seats = hand.get("seats", [])
                    players = hand.get("players", [])
                    # Use whichever is available
                    players_count = len(seats) if seats else len(players)
                    pot_size = hand.get("pot_size", 0)
                    small_blind = hand.get("small_blind", 5)
                    big_blind = hand.get("big_blind", 10)
                    
                    details = f"Hand ID: {hand_id}\\n"
                    details += f"Players: {players_count}\\n"
                    details += f"Pot: ${pot_size}\\n"
                    details += f"Blinds: ${small_blind}/${big_blind}\\n"
                    details += f"Source: Repository"
                self.hands_listbox.insert(tk.END, display_text)
            except Exception as e:
                # Fallback display
                self.hands_listbox.insert(tk.END, f"Hand_{i+1} | PPSM")
                print(f"⚠️ Error displaying hand {i}: {e}")

        # Update collections - prioritize GTO hands
        gto_available = hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands
        if gto_available:
            collections = ["🤖 GTO Hands", "All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        else:
            collections = ["All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        self.collection_combo["values"] = collections

        # Update status with workflow guidance based on active source
        if hands_source == "GTO":
            self._update_status(
                f"🤖 GTO Library: {len(hands)} hands loaded for PPSM testing"
            )
        else:
            stats = self.hands_repository.get_stats()
            self._update_status(
                f"📊 Repository: {stats['total_hands']} total, {stats['filtered_hands']} filtered"
            )
        self._update_status(
            "👆 SELECT a hand from the list, then click 'LOAD HAND' to begin PPSM study"
        )
        
        # Refresh poker table widget to ensure proper sizing
        if hasattr(self, '_refresh_poker_table_widget'):
            self._refresh_poker_table_widget()

    def _on_theme_change(self):
        """Handle poker table theme change for poker table."""
        theme_name = self.theme_var.get()
        print(f"🎨 HandsReviewTab: Switching to theme: {theme_name}")

        # Switch theme in the theme manager
        self.theme.set_profile(theme_name)

        # Update status to show theme change
        self._update_status(
            f"🎨 Switched to {theme_name} theme - Poker table colors applied!"
        )

        # Force poker table refresh with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with {theme_name} theme")

        # Refresh widget sizing to ensure proper fit
        self._refresh_poker_table_widget()

        # Update artistic theme introduction
        self._show_theme_intro(theme_name)

    def _show_theme_intro(self, theme_name):
        """Show artistic introduction for the selected theme with luxury museum placard styling."""
        # Get theme metadata from config-driven system
        metadata = self.theme.get_theme_metadata(theme_name)
        main_desc = metadata.get(
            "intro", "A unique poker table theme with its own distinctive character."
        )
        persona = metadata.get("persona", "")

        # Update the intro label with luxury styling
        self.theme_intro_label.config(state="normal")
        self.theme_intro_label.delete(1.0, tk.END)

        # Insert main description with elegant styling
        self.theme_intro_label.insert(tk.END, main_desc)

        # Add poker persona in italic gold if present
        if persona:
            self.theme_intro_label.insert(tk.END, "\n\n")
            persona_start = self.theme_intro_label.index(tk.INSERT)
            # Format persona with attribution
            persona_text = f"— {persona} style —"
            self.theme_intro_label.insert(tk.END, persona_text)
            persona_end = self.theme_intro_label.index(tk.INSERT)

            # Apply italic styling to persona
            self.theme_intro_label.tag_add("persona", persona_start, persona_end)
            fonts = self.theme.get_fonts()
            persona_font = fonts.get(
                "persona", fonts.get("intro", ("Georgia", 15, "italic"))
            )
            self.theme_intro_label.tag_config("persona", font=persona_font)

        self.theme_intro_label.config(state="disabled")

        # Apply DYNAMIC luxury museum placard styling based on current theme
        theme = self.theme.get_theme()

        # Dynamic theme-aware colors for museum placard
        # Use theme's panel colors but make them more luxurious
        base_bg = theme.get("panel.bg", "#1A1A1A")
        base_border = theme.get("panel.border", "#2A2A2A")
        accent_color = theme.get("table.inlay", theme.get("pot.badgeRing", "#D4AF37"))
        text_primary = theme.get("text.primary", "#F5F5DC")
        text_secondary = theme.get("text.secondary", "#E0E0C0")

        # Use hand-tuned JSON theme colors for perfect quality
        base_colors = self.theme.get_base_colors()

        # Use hand-tuned emphasis tokens for perfect theme-specific quality
        placard_bg = base_colors.get(
            "emphasis_bg_top", base_colors.get("felt", base_bg)
        )
        placard_border = base_colors.get(
            "emphasis_border", base_colors.get("rail", base_border)
        )
        text_color = base_colors.get(
            "emphasis_text", base_colors.get("text", text_primary)
        )
        persona_color = base_colors.get(
            "emphasis_accent_text", base_colors.get("accent", accent_color)
        )
        accent_glow = base_colors.get(
            "highlight", base_colors.get("metal", accent_color)
        )

        # Apply dynamic luxury styling
        self.theme_intro_label.config(
            bg=placard_bg,
            fg=text_color,
            insertbackground=text_color,
            selectbackground=accent_glow,
            selectforeground=base_colors.get("highlight_text", "#FFFFFF"),
        )

        # Style the placard frame with hand-tuned luxury border
        if hasattr(self, "placard_frame"):
            self.placard_frame.config(
                bg=placard_border,  # Hand-tuned theme border color
                relief="raised",
                borderwidth=2,  # Luxury feel
                highlightbackground=accent_glow,
                highlightcolor=accent_glow,
                highlightthickness=1,
            )

        # Apply theme-specific persona text color
        if persona:
            self.theme_intro_label.config(state="normal")
            self.theme_intro_label.tag_config("persona", foreground=persona_color)
            self.theme_intro_label.config(state="disabled")

    def _refresh_ui_colors(self):
        """Refresh poker table with new theme colors."""
        theme = self.theme.get_theme()
        print(f"🎨 HandsReviewTab: Refreshing colors for {self.theme_var.get()} theme")

        # Update poker table canvas background with new theme
        if hasattr(self, "canvas_manager") and self.canvas_manager.canvas:
            # Update canvas background to match new theme
            self.canvas_manager.canvas.configure(
                bg=theme.get("table.felt", "#1E5B44")
            )
            print(f"🎨 HandsReviewTab: Canvas background updated to {theme.get('table.felt', '#1E5B44')}")

        # Force poker table re-render with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with new theme colors")

        # Update enhanced buttons to refresh their theme
        for btn_name in ["load_btn", "next_btn", "auto_btn", "reset_btn"]:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if hasattr(btn, "refresh_theme"):
                    btn.refresh_theme()

        # Update artistic theme intro panel colors
        if hasattr(self, "theme_intro_label"):
            self._show_theme_intro(self.theme_var.get())

    def _on_library_type_change(self):
        """Handle library type change."""
        library_type = self.library_type.get()
        # TODO: Filter by library type
        self._refresh_hands_list()

    def _on_collection_change(self, event=None):
        """Handle collection selection change."""
        collection = self.collection_var.get()
        print(f"🎯 Collection changed to: {collection}")
        
        if collection == "🤖 GTO Hands":
            # GTO hands are handled in _refresh_hands_list()
            pass
        elif collection == "All Hands":
            self.hands_repository.set_filter(HandsFilter())  # Clear filter
        else:
            # TODO: Set filter for specific collection
            pass
        self._refresh_hands_list()

    def _on_hand_select(self, event):
        """Handle hand selection - prioritize GTO hands for PPSM."""
        selection = self.hands_listbox.curselection()
        if selection:
            index = selection[0]
            
            # Get hands from the same source as _refresh_hands_list
            collection = getattr(self, 'collection_var', None)
            selected_collection = collection.get() if collection else "🤖 GTO Hands"
            
            if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
                hands = self.loaded_gto_hands
                hands_source = "GTO"
            else:
                hands = self.hands_repository.get_filtered_hands()
                hands_source = "Repository"
                
            if index < len(hands):
                hand = hands[index]
                self._update_hand_details(hand)
                
                # Get hand ID based on format
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', 'Unknown')
                else:  # Dict format
                    hand_id = hand.get("hand_id", "Unknown")
                    
                # Show that hand is selected and ready to load
                self._update_status(
                    f"✅ Selected: {hand_id} ({hands_source}) - Click 'LOAD HAND' to start PPSM study"
                )

    def _update_hand_details(self, hand_data):
        """Update the hand details display - works with both Hand objects and dicts."""
        self.details_text.delete(1.0, tk.END)
        
        try:
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'metadata'):  # Hand object
                hand_id = hand_data.metadata.get('hand_id', 'Unknown')
                small_blind = hand_data.metadata.get('small_blind', 5)
                big_blind = hand_data.metadata.get('big_blind', 10)
                players_count = len(hand_data.seats) if hasattr(hand_data, 'seats') else 0
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Engine: PPSM Ready\\n"
                details += f"Source: GTO Dataset"
                
            else:  # Dict format
                hand_id = hand_data.get("hand_id", "Unknown")
                # GTO hands use 'seats', regular hands use 'players'
                seats = hand_data.get("seats", [])
                players = hand_data.get("players", [])
                # Use whichever is available
                players_count = len(seats) if seats else len(players)
                pot_size = hand_data.get("pot_size", 0)
                small_blind = hand_data.get("small_blind", 5)
                big_blind = hand_data.get("big_blind", 10)
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Pot: ${pot_size}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Source: Repository"
                
        except Exception as e:
            details = f"Hand details unavailable: {e}"
            
        self.details_text.insert(1.0, details)

    def _on_study_mode_change(self):
        """Handle study mode change."""
        mode = self.study_mode.get()
        self.store.dispatch({"type": SET_STUDY_MODE, "mode": mode})
        self._update_status(f"📚 Study mode: {mode}")

    def _apply_filters(self):
        """Apply current filter settings."""
        filter_criteria = HandsFilter()

        # Apply position filter
        if self.position_var.get() != "All":
            filter_criteria.positions = [self.position_var.get()]

        # Apply stack depth filter
        try:
            filter_criteria.min_stack_depth = (
                int(self.min_stack.get()) if self.min_stack.get() else None
            )
            filter_criteria.max_stack_depth = (
                int(self.max_stack.get()) if self.max_stack.get() else None
            )
        except ValueError:
            pass

        # Apply pot type filter
        if self.pot_type_var.get() != "All":
            filter_criteria.pot_type = self.pot_type_var.get()

        # Apply search text
        filter_criteria.search_text = self.search_var.get()

        # Set filter and refresh
        self.hands_repository.set_filter(filter_criteria)
        self.store.dispatch(
            {"type": SET_REVIEW_FILTER, "filter": filter_criteria.__dict__}
        )
        self._refresh_hands_list()

    def _load_selected_hand(self):
        """Load the selected hand for PPSM study."""
        selection = self.hands_listbox.curselection()
        if not selection:
            self._update_status("❌ Please select a hand to load")
            return

        index = selection[0]
        
        # Get hands from the same source as _refresh_hands_list
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"
            
        if index >= len(hands):
            return

        hand_data = hands[index]
        
        print(f"🎯 Loading {hands_source} hand for PPSM study...")

        # Publish load event as per architecture doc
        self.event_bus.publish(
            self.event_bus.topic(self.session_id, "review:load"), hand_data
        )

    def _handle_load_hand_event(self, hand_data):
        """Handle the review:load event - pure UI logic only."""
        try:
            hand_id = hand_data.get("metadata", {}).get("hand_id", "Unknown")
            self._update_status(f"🔄 Loading hand {hand_id}...")

            # Store hand data for reset functionality
            self.current_hand_data = hand_data

            # Use session manager to load hand (business logic)
            if self.session_manager:
                session_state = self.session_manager.load_hand(hand_data)
                
                # Update UI based on session state
                total_actions = session_state.total_actions
                if total_actions > 0:
                    self.progress_label.config(
                        text=f"Hand loaded: {total_actions} actions"
                    )
                    print(f"🎯 HandsReviewTab: Hand {hand_id} loaded with {total_actions} actions")
                else:
                    self.progress_label.config(text="No actions available")
                    print(f"⚠️ HandsReviewTab: Hand {hand_id} loaded but no actions found")
                
                self._update_status(f"✅ Hand {hand_id} loaded via session manager")
            else:
                self._update_status(f"❌ Session manager not available")
                print(f"❌ HandsReviewTab: Session manager not available")

        except Exception as e:
            print(f"❌ HandsReviewTab: Error loading hand: {e}")
            self._update_status(f"❌ Error loading hand: {e}")

    def _toggle_auto_play(self):
        """Toggle poker table auto-play mode."""
        if not hasattr(self, 'hand_actions') or not self.hand_actions:
            print("⚠️ HandsReviewTab: No hand actions available for auto-play")
            return
        
        if not hasattr(self, 'auto_play_active'):
            self.auto_play_active = False
        
        self.auto_play_active = not self.auto_play_active
        
        if self.auto_play_active:
            print("🎬 HandsReviewTab: Auto-play started")
            self.auto_btn.config(text="Stop Auto")
            self._run_auto_play()
        else:
            print("⏹️ HandsReviewTab: Auto-play stopped")
            self.auto_btn.config(text="Auto")

    def _run_auto_play(self):
        """Run poker table auto-play using GameDirector."""
        if not hasattr(self, 'auto_play_active') or not self.auto_play_active:
            return
        
        if self.current_action_index >= len(self.hand_actions):
            self.auto_play_active = False
            self.auto_btn.config(text="Auto")
            print("✅ HandsReviewTab: Auto-play complete")
            return
        
        # Use GameDirector for coordinated action execution
        if hasattr(self, 'game_director'):
            self.game_director.play()
            print("🎬 GameDirector: Auto-play started")
        else:
            # ARCHITECTURE COMPLIANT: Use GameDirector for timing
            self._next_action()
            if hasattr(self, 'game_director') and self.game_director:
                self.game_director.schedule(1000, {
                    "type": "AUTO_PLAY_NEXT",
                    "callback": self._run_auto_play
                })
            else:
                print("⚠️ GameDirector not available for auto-play timing")



    def _update_status(self, message: str):
        """Update the status display."""
        self.status_text.insert(tk.END, f"\n{message}")
        self.status_text.see(tk.END)

    def _on_store_change(self, state):
        """Handle store state changes for poker table rendering."""
        try:
            # Check if we have poker table state to update
            if hasattr(self, 'display_state') and 'poker_table' in state:
                # Update local display state from store
                self.display_state.update(state['poker_table'])
                
                # Re-render the table with updated state
                self._render_poker_table()
                
                # Handle animation events
                if 'animation_event' in state.get('poker_table', {}):
                    self._handle_animation_event(
                        state['poker_table']['animation_event']
                    )
                    
                print("🔄 HandsReviewTab: State updated from store")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Store change handling error: {e}")

    def _handle_animation_event(self, animation_event):
        """Handle animation events from the store."""
        try:
            if animation_event.get('action') == 'clear_highlight':
                self._clear_highlight()
                print("🎬 HandsReviewTab: Animation event processed")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation event handling error: {e}")

    def _refresh_fonts(self):
        """Refresh fonts after theme changes."""
        fonts = self.theme.get_fonts()

        # Update listbox font
        if hasattr(self, "hands_listbox"):
            body_font = fonts.get("body", ("Consolas", 20))
            self.hands_listbox.configure(font=body_font)

        # Update text areas
        small_font = fonts.get("small", ("Consolas", 16))
        if hasattr(self, "details_text"):
            self.details_text.configure(font=small_font)
        if hasattr(self, "status_text"):
            self.status_text.configure(font=small_font)

        # Update theme intro label font (luxury serif)
        if hasattr(self, "theme_intro_label"):
            intro_font = fonts.get(
                "intro", fonts.get("body", ("Georgia", 16, "normal"))
            )
            self.theme_intro_label.configure(font=intro_font)
    
    def _start_update_loop(self):
        """Start the main update loop for GameDirector and EffectBus."""
        def update_loop():
            try:
                # Update GameDirector
                if hasattr(self, 'game_director'):
                    self.game_director.update()
                
                # Update EffectBus
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()
                
                # Schedule next update (60 FPS)
                self.after(16, update_loop)
                
            except Exception as e:
                print(f"⚠️ Update loop error: {e}")
                # Continue update loop even if there's an error
                self.after(16, update_loop)
        
        # Start the update loop
        update_loop()
        print("🔄 Update loop started for GameDirector and EffectBus")
    
    def _start_ui_tick_loop(self):
        """Start the UI tick loop for GameDirector and EffectBus every ~16ms."""
        def _tick():
            try:
                # Pump GameDirector and EffectBus every ~16ms (60 FPS)
                if hasattr(self, 'game_director'):
                    self.game_director.update(16.7)  # pump scheduled events
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()  # if bus keeps any transient state
            except Exception as e:
                print(f"⚠️ UI tick loop error: {e}")
            finally:
                # Schedule next tick
                self.after(16, _tick)
        
        # Start the tick loop
        _tick()
        print("⏱️ UI tick loop started for GameDirector and EffectBus (60 FPS)")

    def _handle_renderer_intent(self, intent: dict):
        """Handle intents emitted by PokerTableRenderer (state-driven).
        Currently forwards REQUEST_ANIMATION to EffectBus via event bus.
        """
        try:
            t = intent.get("type")
            if t == "REQUEST_ANIMATION" and hasattr(self, 'event_bus'):
                payload = intent.get("payload", {})
                name = payload.get("name")
                # Map declarative types to bridge names if not provided
                if not name:
                    et = payload.get("type")
                    if et == "CHIP_TO_POT":
                        name = "chips_to_pot"
                    elif et == "POT_TO_WINNER":
                        name = "pot_to_winner"
                self.event_bus.publish("effect_bus:animate", {"name": name, "args": payload})
        except Exception:
            pass
    
    def _setup_action_banner(self):
        """Setup ActionBanner and connect it to EffectBus events."""
        try:
            if ActionBanner:
                # Create ActionBanner at the top of the poker table section
                self.action_banner = ActionBanner(self)
                
                # Subscribe to EffectBus banner events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:banner_show", self._handle_banner_event)

                # Subscribe to EffectBus animation events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:animate", self._handle_effect_animate)
                    print("🎞️ Animation: Connected to EffectBus events")
                    print("🎭 ActionBanner: Connected to EffectBus events")
                else:
                    print("⚠️ ActionBanner: No event bus available")
            else:
                print("⚠️ ActionBanner: Not available, skipping setup")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Setup error: {e}")
    
    def _handle_banner_event(self, event_data):
        """Handle banner events from EffectBus."""
        try:
            if hasattr(self, 'action_banner'):
                message = event_data.get('message', '')
                banner_type = event_data.get('banner_type', 'info')
                duration_ms = event_data.get('duration_ms', 3000)
                
                self.action_banner.show_banner(message, banner_type, duration_ms)
                print(f"🎭 ActionBanner: Showing banner: {message}")
            else:
                print("⚠️ ActionBanner: Not available for banner event")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Banner event error: {e}")

        # Update enhanced button themes (handles both fonts and colors)
        enhanced_buttons = []
        if hasattr(self, "load_btn") and hasattr(self.load_btn, "refresh_theme"):
            enhanced_buttons.append(self.load_btn)
        if hasattr(self, "next_btn") and hasattr(self.next_btn, "refresh_theme"):
            enhanced_buttons.append(self.next_btn)
        if hasattr(self, "auto_btn") and hasattr(self.auto_btn, "refresh_theme"):
            enhanced_buttons.append(self.auto_btn)
        if hasattr(self, "reset_btn") and hasattr(self.reset_btn, "refresh_theme"):
            enhanced_buttons.append(self.reset_btn)

        for btn in enhanced_buttons:
            btn.refresh_theme()

    def _handle_effect_animate(self, payload):
        """Handle animation requests from EffectBus using ChipAnimations where possible."""
        try:
            name = (payload or {}).get("name")
            ms = int((payload or {}).get("ms", 300))
            if not getattr(self, "canvas_manager", None):
                return
            c = self.canvas_manager.canvas
            
            # Get theme manager from the correct location
            theme_manager = getattr(self, 'theme', None)
            if not theme_manager:
                print("⚠️ No theme manager available for animations")
                return
                
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)
            
            # Get proper pot center from display state
            pot_center = (self.canvas_manager.canvas.winfo_width() // 2, 
                         int(self.canvas_manager.canvas.winfo_height() * 0.52))
            
            # Get seat positions for proper animation coordinates
            seats = self.display_state.get("seats", [])
            if not seats:
                return
                
            # Get consistent seat positions for animation
            w, h = self.canvas_manager.size()
            from ..state.selectors import get_seat_positions
            seat_positions = get_seat_positions(self.display_state, seat_count=len(seats), 
                                              canvas_width=w, canvas_height=h)
            
            if name == "betting_action":
                # Handle betting actions (BET, RAISE, CALL, CHECK, FOLD)
                action_type = (payload or {}).get("action_type", "UNKNOWN")
                actor_uid = (payload or {}).get("actor_uid", "Unknown")
                
                print(f"🎬 Betting action animation: {action_type} by {actor_uid}")
                
                # Find the acting player for source position with robust normalization
                def _norm(v):
                    return str(v).strip().lower()

                actor_norm = _norm(actor_uid)
                acting_seat = None

                # Build lookup maps
                uid_to_idx = { _norm(s.get('player_uid')): i for i, s in enumerate(seats) }
                name_to_idx = { _norm(s.get('name', '')): i for i, s in enumerate(seats) }

                # Prefer player_uid
                if actor_norm in uid_to_idx:
                    acting_seat = seats[uid_to_idx[actor_norm]]
                elif actor_norm in name_to_idx:
                    acting_seat = seats[name_to_idx[actor_norm]]
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating {action_type} from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        
                        # Different animation based on action type
                        if action_type in ["BET", "RAISE", "CALL"]:
                            # Animate chips to pot
                            anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                        elif action_type == "CHECK":
                            # Visual feedback for check (no chips)
                            print(f"🎬 Check action - no chip animation needed")
                        elif action_type == "FOLD":
                            # Visual feedback for fold (maybe card flip or seat dimming)
                            print(f"🎬 Fold action - seat dimming effect")
                else:
                    print(f"⚠️ No seat found for actor {actor_uid} in betting action animation")
                    
            elif name == "chips_to_pot":
                # This should ONLY happen at end of street (DEAL_BOARD, DEAL_TURN, DEAL_RIVER)
                # NOT during betting rounds
                print(f"🎬 End-of-street animation: chips flying to pot")
                
                # Find the acting player for source position
                acting_seat = None
                for seat in seats:
                    if seat.get('acting', False):
                        acting_seat = seat
                        break
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating chips from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                else:
                    print("⚠️ No acting seat found for chips_to_pot animation")
                    
            elif name == "pot_to_winner":
                # This is for showdown/end of hand
                print(f"🎬 Showdown animation: pot flying to winner")
                
                # Find winner seat
                winner = None
                for seat in seats:
                    if not seat.get("folded", False):
                        winner = seat
                        break
                
                if winner:
                    # Get winner position using consistent positioning
                    winner_idx = seats.index(winner)
                    if winner_idx < len(seat_positions):
                        wx, wy = seat_positions[winner_idx]
                        
                        print(f"🎬 Animating pot to winner {winner.get('name', 'Unknown')} at ({wx}, {wy})")
                        anim.fly_pot_to_winner(c, pot_center[0], pot_center[1], wx, wy, amount=200, callback=None)
                else:
                    print("⚠️ No winner found for pot_to_winner animation")
                    
        except Exception as e:
            print(f"⚠️ Animation handler error: {e}")
            import traceback
            traceback.print_exc()

    def _style_theme_radio_buttons(self):
        """Apply theme-specific styling to radio buttons to eliminate default green highlights."""
        if not hasattr(self, "theme_radio_buttons"):
            return

        try:
            # Get current theme and highlight colors
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            theme = self.theme.get_theme()

            # Create a custom style for radio buttons
            style = ttk.Style()

            # Apply config-driven selection styling
            selection_styler = self.theme.get_selection_styler()
            if selection_styler:
                theme_id = self.theme.get_current_theme_id()
                selection_styler.apply_selection_styles(style, theme_id)

            # Get selection highlight colors (config-driven with legacy fallback)
            try:
                base_colors = self.theme.get_base_colors()
                selection_color = base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
                selection_glow = base_colors.get(
                    "metal", base_colors.get("accent", "#C9A34E")
                )
            except Exception:
                # Get selection highlight from config-driven system
                base_colors = self.theme.get_base_colors()
                selection_highlight = {
                    "color": base_colors.get(
                        "highlight", base_colors.get("accent", "#D4AF37")
                    )
                }
                selection_color = selection_highlight["color"]
                selection_glow = selection_highlight.get("glow", "#C9A34E")

            # Configure the radio button style with theme-specific colors
            style.configure(
                "Themed.TRadiobutton",
                background=theme.get("panel.bg", "#1F2937"),
                foreground=theme.get("panel.fg", "#E5E7EB"),
                focuscolor=selection_color,
            )

            # Configure the selection/active state colors
            style.map(
                "Themed.TRadiobutton",
                background=[
                    ("active", theme.get("panel.bg", "#1F2937")),
                    ("selected", theme.get("panel.bg", "#1F2937")),
                ],
                foreground=[
                    ("active", theme.get("panel.fg", "#E5E7EB")),
                    ("selected", theme.get("panel.fg", "#E5E7EB")),
                ],
                indicatorcolor=[
                    ("selected", selection_color),
                    ("active", selection_glow),
                    ("!selected", theme.get("panel.border", "#374151")),
                ],
            )

            # Apply the custom style to all radio buttons
            for radio_btn in self.theme_radio_buttons:
                if radio_btn.winfo_exists():
                    radio_btn.configure(style="Themed.TRadiobutton")

        except Exception as e:
            # Fallback styling if custom styling fails
            print(f"⚠️ Radio button styling failed: {e}")
            pass


    def _next_action(self):
        """Dispatch next action intent - pure UI logic only."""
        print("🎯 NEXT_ACTION: Button clicked!")

        # ARCHITECTURE COMPLIANT: Dispatch action to Store instead of direct service call
        try:
            self.store.dispatch({
                "type": "HANDS_REVIEW_NEXT_ACTION",
                "session_id": self.session_id,
                "timestamp": time.time()
            })
            print("🎯 NEXT_ACTION: Action dispatched to Store")
        except Exception as e:
            print(f"⚠️ NEXT_ACTION: Failed to dispatch action: {e}")
            self._update_status(f"❌ Error dispatching next action: {e}")
    
    def _render_table_with_state(self, session_state):
        """Render poker table with session state - pure UI logic only."""
        try:
            # Convert session state to PokerTableState
            from ..table.state import PokerTableState
            
            table_state = PokerTableState(
                table=session_state.table,
                seats=session_state.seats,
                board=session_state.board,
                pot=session_state.pot,
                dealer=session_state.dealer,
                action=session_state.action,
                animation=session_state.animation,
                effects=session_state.effects,
                street=session_state.street
            )
            
            # Render using PokerTableRenderer
            if hasattr(self, 'table_renderer') and self.table_renderer:
                self.table_renderer.render(table_state)
                print("🎯 HandsReviewTab: Table rendered with session state")
            else:
                print("⚠️ HandsReviewTab: Table renderer not available")
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error rendering table: {e}")

    def _reset_hand(self):
        """Reset the current hand to the beginning - pure UI logic only."""
        if not self.session_manager:
            self._update_status("⚠️ Session manager not available")
            return

        try:
            # Reset hand via session manager (business logic)
            if hasattr(self, "last_loaded_hand") and self.last_loaded_hand:
                session_state = self.session_manager.load_hand(self.last_loaded_hand)
                self._update_status("🔄 Hand reset to beginning")
                
                # Render table with reset state
                self._render_table_with_state(session_state)
            else:
                self._update_status("⚠️ No hand to reset")
        except Exception as e:
            self._update_status(f"❌ Error resetting hand: {e}")

    def on_show(self):
        """Called when tab is shown - refresh display."""
        if hasattr(self, "renderer_pipeline"):
            state = self.store.get_state()
            self.renderer_pipeline.render_once(state)

    def dispose(self):
        """Clean up when tab is closed."""
        # ARCHITECTURE COMPLIANT: Notify event controller of session disposal
        try:
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish(
                    "hands_review:session_disposed",
                    {"session_id": self.session_id}
                )
                print(f"🎯 HandsReviewTab: Session {self.session_id} disposal notified")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Failed to notify session disposal: {e}")
        
        # Clean up session manager if active
        if self.session_manager:
            self.session_manager.cleanup()
            self.session_manager = None
        self.services.dispose_session(self.session_id)

    def _load_gto_hands(self):
        """Load GTO hands for PPSM testing."""
        try:
            import json
            import os
            
            gto_hands_file = "gto_hands.json"
            print(f"🔍 Looking for GTO hands file: {gto_hands_file}")
            
            if os.path.exists(gto_hands_file):
                print(f"📂 Found GTO hands file, loading...")
                with open(gto_hands_file, 'r') as f:
                    hands_data = json.load(f)
                    
                print(f"📊 Raw GTO hands data: {len(hands_data)} hands")
                    
                # Convert to Hand objects
                self.loaded_gto_hands = []
                for i, hand_data in enumerate(hands_data):
                    try:
                        hand = Hand(**hand_data)  # Create proper Hand object
                        self.loaded_gto_hands.append(hand)
                    except Exception as e:
                        print(f"⚠️ Error creating Hand object for hand {i}: {e}")
                        # Fallback: store as dict
                        self.loaded_gto_hands.append(hand_data)
                        
                print(f"✅ Loaded {len(self.loaded_gto_hands)} GTO hands for PPSM testing")
            else:
                print(f"⚠️ GTO hands file not found: {gto_hands_file}")
                self.loaded_gto_hands = []
                
        except Exception as e:
            print(f"⚠️ Error loading GTO hands: {e}")
            self.loaded_gto_hands = []

    def _load_hand(self, hand_data):
        """Load hand data into poker table using new architecture."""
        try:
            # Store the hand data for reference
            self.current_hand_data = hand_data
            
            # Flatten hand actions for step-by-step replay
            self.hand_actions = self._flatten_hand_for_replay(hand_data)
            
            # Reset action index
            self.current_action_index = 0
            
            # Create display state from hand data
            new_display_state = self._create_display_state_from_hand(hand_data)
            
            # Update the existing display state with new data
            self.display_state.update(new_display_state)
            
            # Dispatch LOAD_REVIEW_HAND action to store
            self.store.dispatch({
                "type": "LOAD_REVIEW_HAND",
                "hand_data": hand_data,
                "flattened_actions": self.hand_actions
            })
            
            # Update progress display
            if self.hand_actions:
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                self.progress_label.config(text=progress_text)
                # Enable next button
                self.next_btn.config(state="normal")
                
                # Setup GameDirector for this hand
                if hasattr(self, 'game_director'):
                    self.game_director.set_total_steps(len(self.hand_actions))
                    self.game_director.set_advance_callback(self._execute_action_at_index)
                    print(f"🎬 GameDirector: Configured for {len(self.hand_actions)} actions")
            
            # Render the table
            self._render_poker_table()
            
            # Refresh widget to ensure proper sizing
            self._refresh_poker_table_widget()
            
            print(f"✅ HandsReviewTab: Hand loaded with {len(self.hand_actions)} actions")
        
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error loading hand: {e}")

    def _create_display_state_from_hand(self, hand_data):
        """Create display state from hand data for poker table."""
        try:
            # Debug: Log the raw hand data
            print(f"🎯 Creating display state from hand data:")
            print(f"   Hand data type: {type(hand_data)}")
            print(f"   Hand data keys: {list(hand_data.keys()) if hasattr(hand_data, 'keys') else 'N/A'}")
            
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'seats'):  # Hand object
                seats = hand_data.seats
                metadata = hand_data.metadata
                print(f"   Using Hand object: {len(seats)} seats")
            else:  # Dict format
                seats = hand_data.get('seats', [])
                metadata = hand_data.get('metadata', {})
                print(f"   Using dict format: {len(seats)} seats")
            
            print(f"   Raw seats data: {seats}")
            print(f"   Metadata: {metadata}")
            
            # Extract basic hand information
            small_blind = metadata.get('small_blind', 5) if metadata else 5
            big_blind = metadata.get('big_blind', 10) if metadata else 10
            
            print(f"   Extracted {len(seats)} seats, SB: {small_blind}, BB: {big_blind}")
            
            # Create initial display state with actual table dimensions
            display_state = {
                'table': {
                    'width': getattr(self, 'table_width', 800),
                    'height': getattr(self, 'table_height', 600),
                    'theme': 'luxury_noir'  # Default theme
                },
                'pot': {
                    'amount': 0,
                    'position': (400, 300)
                },
                'seats': [],
                'board': [],
                'dealer': {'position': 0},
                'action': {'type': None, 'player': None, 'amount': 0},
                'replay': {'current_step': 0, 'total_steps': 0}
            }
            
            # Set up seats from GTO hand data
            for i, seat in enumerate(seats):
                player_uid = seat.get('player_uid', f'player_{i}')
                name = seat.get('display_name', f'Player {i+1}')
                starting_stack = seat.get('starting_stack', 1000)
                
                # Calculate seat position (simplified for now)
                angle = (2 * 3.14159 * i) / len(seats)
                radius = 200
                x = 400 + int(radius * math.cos(angle))
                y = 300 + int(radius * math.sin(angle))
                
                # Get hole cards for this player from metadata
                if hasattr(hand_data, 'metadata') and hasattr(hand_data.metadata, 'hole_cards'):
                    hole_cards = hand_data.metadata.hole_cards.get(player_uid, [])
                else:
                    hole_cards = metadata.get('hole_cards', {}).get(player_uid, [])
                
                seat_data = {
                    'player_uid': player_uid,
                    'name': name,
                    'starting_stack': starting_stack,
                    'current_stack': starting_stack,
                    'current_bet': 0,
                    # Backwards-compatible keys used by renderer components
                    'stack': starting_stack,
                    'bet': 0,
                    'cards': hole_cards,  # Populate with actual hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': i
                }
                
                # Set initial blinds based on seat order
                if i == 0:  # Small blind
                    seat_data['current_bet'] = small_blind
                    seat_data['current_stack'] -= small_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'SB'
                elif i == 1:  # Big blind
                    seat_data['current_bet'] = big_blind
                    seat_data['current_stack'] -= big_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'BB'
                
                display_state['seats'].append(seat_data)
                print(f"   🪑 Created seat {i}: {name} at ({x}, {y}) with cards {hole_cards}")
            
            print(f"🎯 HandsReviewTab: Created display state with {len(display_state['seats'])} seats")
            for seat in display_state['seats']:
                print(f"  🪑 {seat['name']}: {seat['cards']} (stack: {seat['current_stack']}, bet: {seat['current_bet']})")
            
            return display_state
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error creating display state: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _flatten_hand_for_replay(self, hand):
        """Produce a list of 'steps' to drive the poker table UI."""
        steps = []

        # Synthesize: deal hole cards
        holes = (hand.get("metadata", {}) or {}).get("hole_cards", {}) or {}
        steps.append({
            "type": "DEAL_HOLE",
            "desc": "🃏 Deal hole cards",
            "payload": {"hole_cards": holes},
        })

        streets = hand.get("streets", {}) or {}
        # Keep deterministic street order
        for street_name in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            if street_name not in streets:
                continue
            s = streets[street_name] or {}
            actions = s.get("actions", []) or []
            board = s.get("board", []) or []

            # If board present, add board-deal step
            if street_name != "PREFLOP" and board:
                steps.append({
                    "type": "DEAL_BOARD",
                    "desc": f"🂠 Deal {street_name} board: {', '.join(board)}",
                    "payload": {"street": street_name, "board": board},
                })

            for a in actions:
                # Handle different action types
                action_type = a.get("action", "UNKNOWN")
                actor = a.get("actor_uid", "Unknown")
                amount = a.get("amount", 0)
                
                if action_type == "POST_BLIND":
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type in ["BET", "RAISE", "CALL"]:
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type == "CHECK":
                    desc = f"{street_name}: {actor} → {action_type}"
                elif action_type == "FOLD":
                    desc = f"{street_name}: {actor} → {action_type}"
                else:
                    desc = f"{street_name}: {actor} → {action_type} {amount if amount else ''}"
                
                steps.append({
                    "type": action_type,
                    "desc": desc,
                    "payload": {"street": street_name, **a},
                })

        # Terminal step
        steps.append({"type": "END_HAND", "desc": "✅ End of hand", "payload": {}})
        return steps

    def _render_poker_table(self):
        """Render the poker table using the component pipeline."""
        try:
            # Debug: Log what's in the display state
            print(f"🎯 Rendering table with state:")
            print(f"   Seats: {len(self.display_state.get('seats', []))}")
            print(f"   Board: {self.display_state.get('board', [])}")
            print(f"   Pot: {self.display_state.get('pot', {}).get('amount', 0)}")
            
            if self.display_state.get('seats'):
                for i, seat in enumerate(self.display_state['seats']):
                    print(f"   Seat {i}: {seat}")
            
            # Build PokerTableState and render
            try:
                from ..table.state import PokerTableState
            except Exception:
                # Inline lightweight structure if import fails
                class PokerTableState(dict):
                    pass

            state = PokerTableState(
                table={"width": self.table_width, "height": self.table_height},
                seats=self.display_state.get('seats', []),
                board=self.display_state.get('board', []),
                pot=self.display_state.get('pot', {}),
                dealer={"position": self.display_state.get('dealer', 0)},
                action=self.display_state.get('action', {}),
                animation={},
                effects=list(self._pending_effects),
                street=self.display_state.get('street', 'PREFLOP'),  # Pass street for community cards
            )
            # Clear effects after issuing
            self._pending_effects.clear()
            
            # Let PokerTableRenderer handle its own readiness checking and deferral
            print("🎯 HandsReviewTab: Attempting to render via PokerTableRenderer")
                
            self.table_renderer.render(state)
            print("🎨 HandsReviewTab: Table rendered successfully (state-driven)")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Render error: {e}")
            import traceback
            traceback.print_exc()


    
    def _execute_action_step(self, action):
        """Execute a single action step and update display state."""
        try:
            action_type = action.get('type', 'UNKNOWN')
            payload = action.get('payload', {})
            
            # Get player name for effects
            actor_uid = payload.get('actor_uid', 'Unknown')
            player_name = None
            for seat in self.display_state['seats']:
                if seat['player_uid'] == actor_uid:
                    player_name = seat.get('name', actor_uid)
                    break
            

            # Update acting highlight: set only the actor as acting
            try:
                for s in self.display_state.get('seats', []):
                    s['acting'] = (s.get('player_uid') == actor_uid)
            except Exception:
                pass
                
            # optional: re-render to reflect highlight immediately
            try:
                self.renderer_pipeline.render_once(self.display_state)
            except Exception:
                pass
            
            if action_type == "DEAL_HOLE":
                # Hole cards are already loaded in initial state
                print(f"🃏 HandsReviewTab: Hole cards dealt")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_HOLE", player_name)
                
            elif action_type == "DEAL_BOARD":
                street = payload.get('street', 'UNKNOWN')
                board = payload.get('board', [])
                self.display_state['board'] = board
                self.display_state['street'] = street  # Update street for community card rendering
                print(f"🂠 HandsReviewTab: Dealt {street} board: {board}")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_BOARD", player_name)
                
                # Professional poker behavior: Animate chips to pot at end of street
                # This clears all bet chips from in front of players and moves them to pot
                if street in ["FLOP", "TURN", "RIVER"]:
                    try:
                        from ..state.selectors import get_seat_positions
                        w, h = self.table_renderer.canvas_manager.size() if hasattr(self, 'table_renderer') else (self.table_width, self.table_height)
                        positions = get_seat_positions(self.display_state, seat_count=len(self.display_state.get('seats', [])), canvas_width=w, canvas_height=h)
                        
                        # Find any seat with bets to animate from (use first betting seat)
                        for seat_idx, seat in enumerate(self.display_state.get('seats', [])):
                            if seat.get('current_bet', 0) > 0 and seat_idx < len(positions):
                                fx, fy = positions[seat_idx]
                                pot_x, pot_y = (w // 2, int(h * 0.58))
                                self._pending_effects.append({
                                    "type": "CHIP_TO_POT",
                                    "from_x": int(fx), "from_y": int(fy),
                                    "to_x": pot_x, "to_y": pot_y,
                                    "amount": seat.get('current_bet', 0),
                                })
                                print(f"🎬 End-of-street: Moving chips from seat {seat_idx} to pot for {street}")
                                break
                    except Exception as e:
                        print(f"⚠️ Could not add end-of-street animation: {e}")
                
            elif action_type in ["BET", "RAISE", "CALL", "CHECK", "FOLD"]:
                amount = payload.get('amount', 0)
                
                # Update the appropriate seat's bet and stack
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        if action_type in ["BET", "RAISE"]:
                            # For BET/RAISE, amount is the total bet
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = action_type.lower()  # Add last_action for bet styling
                        elif action_type == "CALL":
                            # For CALL, amount is the total bet to match
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = "call"  # Add last_action for bet styling
                        elif action_type == "CHECK":
                            # CHECK doesn't change bet or stack
                            seat['last_action'] = "check"  # Add last_action for bet styling
                        elif action_type == "FOLD":
                            seat['folded'] = True
                            seat['last_action'] = "fold"  # Add last_action for bet styling
                            # Folded players keep their current bet
                        
                        # Set acting flag for highlighting on this seat only
                        seat['acting'] = True
                        break

                # Clear acting flag from other seats using different loop variable
                for s2 in self.display_state['seats']:
                    if s2.get('player_uid') != actor_uid:
                        s2['acting'] = False
                
                # Update pot amount
                if action_type in ["BET", "RAISE", "CALL"]:
                    total_pot = sum(seat['current_bet'] for seat in self.display_state['seats'])
                    self.display_state['pot']['amount'] = total_pot
                
                print(f"🎯 HandsReviewTab: {actor_uid} {action_type} {amount if amount else ''}")
                print(f"🎯 Seat state updated: current_bet={seat.get('current_bet', 0)}, last_action={seat.get('last_action', 'none')}")
                
                # Add action sound effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects(action_type, player_name)

                # Professional poker behavior: Only animate chips to pot at END of streets
                # Individual bets/calls just place chips in front of players
                # (CHIP_TO_POT animation will be triggered by DEAL_FLOP, DEAL_TURN, DEAL_RIVER actions)
                
                # Show action banner for immediate visual feedback
                if hasattr(self, 'action_banner'):
                    amount = payload.get('amount', 0)
                    self.action_banner.show_poker_action(action_type, player_name, amount)

                # Re-render immediately after state updates to ensure highlight and bets update
                try:
                    self.renderer_pipeline.render_once(self.display_state)
                except Exception:
                    pass
                
            elif action_type == "POST_BLIND":
                amount = payload.get('amount', 0)
                
                # Update seat bet and stack for blind posting
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        seat['current_bet'] = amount
                        seat['current_stack'] -= amount
                        break
                
                print(f"💰 HandsReviewTab: {actor_uid} posted blind: {amount}")
                
                # Add blind posting sounds (chips stay in front of player until street ends)
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("POST_BLIND", player_name)
            
            # Re-render the table with updated state
            self._render_poker_table()
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing action step: {e}")
    
    def _execute_action_at_index(self, action_index: int):
        """Execute action at specific index - called by GameDirector."""
        try:
            if 0 <= action_index < len(self.hand_actions):
                self.current_action_index = action_index
                action = self.hand_actions[action_index]
                
                # Execute the action
                self._execute_action_step(action)
                
                # Update progress display
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                if hasattr(self, 'progress_label'):
                    self.progress_label.config(text=progress_text)
                
                print(f"🎬 GameDirector: Executed action at index {action_index}")
            else:
                print(f"⚠️ GameDirector: Invalid action index {action_index}")
                
        except Exception as e:
            print(f"⚠️ GameDirector: Error executing action at index {action_index}: {e}")

    def _prev_action(self):
        """Execute previous action using proper Store-based architecture."""
        try:
            # Check if we have actions to execute
            if not hasattr(self, 'hand_actions') or not self.hand_actions:
                print("⚠️ HandsReviewTab: No hand actions available")
                return
            
            # Check if we can go to previous action
            if self.current_action_index <= 0:
                print("⚠️ HandsReviewTab: Already at first action")
                return
            
            # Move to previous action
            self.current_action_index -= 1
            action = self.hand_actions[self.current_action_index]
            
            # Execute the action to update display state
            self._execute_action_step(action)
            
            # Update progress display
            progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=progress_text)
            
            # Dispatch action to store for state management
            self.store.dispatch({
                "type": "PREV_REVIEW_ACTION"
            })
            
            print(f"🎬 HandsReviewTab: Executed previous action {self.current_action_index}: {action.get('type', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing previous action: {e}")



    def _execute_action(self, action):
        """Execute action and update poker table state with rich UI/UX features."""
        # REMOVED: This method should not contain business logic
        # Business logic should be in PPSM or Store reducers
        # UI should only dispatch actions and render state
        pass

    def _play_sound(self, sound_type):
        """Play sound effects for poker table actions."""
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                # Map sound types to sound manager events
                sound_mapping = {
                    'card_deal': 'card_deal',
                    'chip_bet': 'chip_bet',
                    'player_bet': 'player_action_bet',
                    'player_call': 'player_action_call',
                    'player_check': 'player_action_check',
                    'player_fold': 'player_action_fold',
                    'hand_end': 'hand_end'
                }
                
                event_name = sound_mapping.get(sound_type, sound_type)
                self.sound_manager.play(event_name)
                print(f"🔊 HandsReviewTab: Playing {sound_type} sound")
            else:
                print(f"🔇 HandsReviewTab: No sound manager available for {sound_type}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Sound error for {sound_type}: {e}")

    def _schedule_animation(self):
        """Schedule animation effects using event-driven system."""
        try:
            # Use event bus instead of direct UI timing (architectural compliance)
            if hasattr(self, 'event_bus'):
                self.event_bus.publish(
                    self.event_bus.topic(self.session_id, "poker_table:animation"),
                    {
                        "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                        "delay_ms": 200,
                        "action": "clear_highlight"
                    }
                )
                print(f"🎬 HandsReviewTab: Scheduled animation via event bus")
            else:
                print(f"⚠️ HandsReviewTab: No event bus available for animation")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation scheduling error: {e}")

    def _clear_highlight(self):
        """Clear player highlighting after animation."""
        try:
            if hasattr(self, 'display_state') and 'action' in self.display_state:
                self.display_state['action']['highlight'] = False
                # Re-render to show cleared highlight
                self._render_poker_table()
                print(f"🎬 HandsReviewTab: Cleared action highlight")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Highlight clear error: {e}")

    def _refresh_poker_table_widget(self):
        """Refresh the poker table widget to ensure proper sizing and fit."""
        try:
            if hasattr(self, 'canvas_manager') and self.canvas_manager:
                # Force canvas to update its geometry
                self.canvas_manager.canvas.update_idletasks()
                
                # Get current frame dimensions
                parent_frame = self.canvas_manager.canvas.master
                frame_width = parent_frame.winfo_width()
                frame_height = parent_frame.winfo_height()
                
                # Recalculate table dimensions
                table_width = max(800, frame_width - 20)
                table_height = max(600, frame_height - 20)
                
                # Update canvas size
                self.canvas_manager.canvas.configure(width=table_width, height=table_height)
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update display state
                if hasattr(self, 'display_state'):
                    self.display_state['table']['width'] = table_width
                    self.display_state['table']['height'] = table_height
                
                # Re-render with new dimensions
                self._render_poker_table()
                
                print(f"🔄 HandsReviewTab: Widget refreshed to {table_width}x{table_height}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Widget refresh error: {e}")

```

---

## TEST FILES

### test_mvu_implementation.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/test_mvu_implementation.py`

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

### test_mvu_simple.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/test_mvu_simple.py`

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

## SUPPORTING SERVICES

### services/service_container.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/services/service_container.py`

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

### services/event_bus.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/services/event_bus.py`

```python
from collections import defaultdict
from typing import Any, Callable, Dict, List


class EventBus:
    """
    Simple in-memory pub/sub event bus with string topics.

    Topics should be namespaced using a session identifier to prevent
    cross-talk between tabs/sessions.
    Example: f"{session_id}:ui:action".
    """

    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def topic(self, session_id: str, name: str) -> str:
        return f"{session_id}:{name}"

    def subscribe(
        self, topic: str, handler: Callable[[Any], None]
    ) -> Callable[[], None]:
        self._subs[topic].append(handler)

        def unsubscribe() -> None:
            try:
                self._subs[topic].remove(handler)
            except ValueError:
                pass

        return unsubscribe

    def publish(self, topic: str, payload: Any) -> None:
        # Copy list to avoid mutation during iteration
        for handler in list(self._subs.get(topic, [])):
            handler(payload)



```

---

### services/game_director.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/services/game_director.py`

```python
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

```

---

### services/effect_bus.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/services/effect_bus.py`

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

### services/theme_manager.py

**Path**: `/Users/yeogirlyun/Python/Poker/backend/ui/services/theme_manager.py`

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

## ARCHITECTURE DOCUMENTATION

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

### PokerPro_Trainer_Complete_Architecture_v3.md

**Path**: `/Users/yeogirlyun/Python/Poker/docs/PokerPro_Trainer_Complete_Architecture_v3.md`

```markdown
# PokerPro Trainer - Complete Architecture Reference v3

**Status**: Production Ready  
**Last Updated**: January 2024  
**Purpose**: Comprehensive reference for complete codebase reconstruction if needed  

---

## 🏗️ **SYSTEM OVERVIEW**

The PokerPro Trainer uses a **single-threaded, event-driven architecture** centered around three core pillars:

1. **PurePokerStateMachine (PPSM)** - Deterministic poker engine with hand replay capabilities
2. **Modern UI Architecture** - Component-based UI with clean separation of concerns  
3. **Session Management System** - Pluggable session types (GTO, Practice, Hands Review, Live)

### **Core Design Principles**

- **Single Source of Truth**: PPSM is the authoritative game state
- **Deterministic Behavior**: All game logic is reproducible and testable
- **Clean Separation**: UI renders state, never controls game logic
- **Event-Driven**: All interactions flow through well-defined interfaces
- **Pluggable Components**: DecisionEngines and Sessions are swappable

---

## 🎮 **PURE POKER STATE MACHINE (PPSM)**

### **Architecture Overview**

The PPSM is a **deterministic, single-threaded poker engine** that serves as the single source of truth for all poker game state and logic.

```python
class PurePokerStateMachine:
    """
    Core poker engine with:
    - Deterministic game state management
    - Hand replay capabilities via DecisionEngineProtocol
    - Clean to-amount semantics for all actions
    - Comprehensive validation and error handling
    """
```

### **Key Features**

#### **1. Deterministic Deck System**
```python
# Uses predetermined card sequences for reproducible hands
deck = ["Kh", "Kd", "Ad", "2c", "4h", "4s", "Qh", "2h", "2d"]
```

#### **2. To-Amount Semantics (Authoritative)**
- **BET**: `to_amount` = total amount to reach (not delta)
- **RAISE**: `to_amount` = total amount to raise to (not additional)
- **CALL/CHECK**: `to_amount` ignored (engine computes)

#### **3. DecisionEngineProtocol Integration**
```python
class DecisionEngineProtocol:
    def get_decision(self, player_name: str, game_state) -> tuple[ActionType, Optional[float]]:
        """Return (ActionType, to_amount) for player to act"""
        pass
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if engine has decision for player"""
        pass
```

#### **4. Hand Model Replay**
```python
def replay_hand_model(self, hand_model) -> dict:
    """
    Replay a Hand object using HandModelDecisionEngineAdapter
    Returns comprehensive results with pot validation
    """
```

### **State Management**

#### **Game States**
- `START_HAND` → `PREFLOP_BETTING` → `FLOP_BETTING` → `TURN_BETTING` → `RIVER_BETTING` → `SHOWDOWN`

#### **Player State Tracking**
- `current_bet`: Amount player has wagered this street
- `stack`: Remaining chips
- `is_active`: Can still act in hand
- `has_folded`: Eliminated from hand

#### **Round State Management**
- `current_bet`: Current bet to match
- `last_full_raise_size`: For minimum raise validation  
- `need_action_from`: Set of player indices who need to act
- `reopen_available`: Whether betting can be reopened

### **Validation System**

#### **Action Validation**
```python
def _is_valid_action(self, player: Player, action_type: ActionType, to_amount: Optional[float]) -> bool:
    """
    Comprehensive validation including:
    - Player can act (not folded, has chips)
    - Action is legal for current street
    - Bet amounts are valid (within limits, proper increments)
    - Raise amounts meet minimum requirements
    """
```

#### **Pot Validation**
```python
def _validate_pot_integrity(self) -> bool:
    """
    Ensures total chips in play equals:
    - All player stacks + current bets + pot
    - No chips created or destroyed
    """
```

---

## 🎨 **UI ARCHITECTURE**

### **Component Hierarchy**

```
AppShell
├── ServiceContainer
│   ├── ThemeManager
│   ├── SoundManager
│   ├── EventBus
│   └── Store
├── TabContainer
│   ├── HandsReviewTab
│   ├── PracticeSessionTab
│   └── GTOSessionTab
└── PokerTableRenderer (Unified Poker Table — Pure Renderer)
    ├── CanvasManager
    ├── LayerManager (felt → seats → stacks → community → bets → pot → action → status → overlay)
    ├── RendererPipeline
    └── Table Components
        ├── TableFelt
        ├── Seats
        ├── Community
        ├── PotDisplay
        ├── BetDisplay
        ├── DealerButton
        └── ActionIndicator
```

### **Design Principles**

#### **1. Pure Rendering Components**
- UI components are **stateless renderers**
- All business logic resides in PPSM or services
- Components subscribe to state via selectors
- No direct state mutation from UI

#### **2. State-Driven Architecture**
- Single source of truth: Store
- UI renders based on state changes
- Actions flow: UI → Store → Reducer → State → UI
- No imperative UI updates

#### **3. Event-Driven Integration**
- EventBus for cross-service communication
- Services handle side effects (sounds, animations)
- UI dispatches actions, never calls services directly
- Clean separation of concerns

#### **4. Reusable Poker Table Renderer**
- `backend/ui/renderers/poker_table_renderer.py` is a **pure** renderer reused by every session.
- Input is a single `PokerTableState` (immutable dataclass).
- Emits renderer intents (e.g., `REQUEST_ANIMATION`) that the shell adapts to `EffectBus`.
- No business logic, no session awareness, no PPSM calls.

### **State / Effects Flow (MVU)**

```
UI Intent → SessionManager.handle_* → PPSM → Store.replace(table_state, effects)
      ↓                                    ↓
PokerTableRenderer.render(state)     EffectBus.run(effects) → Director gating
```

### **Theme System Integration**

- **Design System v2**: Token-based color system
- **Hot-swappable themes**: Runtime theme switching
- **Responsive design**: Dynamic sizing based on container
- **Accessibility**: WCAG 2.1 AA compliance

---

## 🎯 **SESSION IMPLEMENTATION ARCHITECTURE**

### **Hands Review Session**

#### **Purpose**
- Load and replay GTO/Legendary hands
- Step-by-step action progression
- Auto-play with configurable timing
- Theme switching and responsive layout

#### **Core Components**
- **Enhanced RPGW**: Unified poker table display
- **Hand Loader**: JSON parsing and validation
- **Action Controller**: Step-by-step progression
- **Theme Manager**: Dynamic theme switching

#### **Implementation Flow**
```python
# 1. Hand Loading
hand_data = load_hand_from_json(file_path)
display_state = create_display_state(hand_data)

# 2. Action Execution
action = get_next_action(hand_data, current_index)
store.dispatch({"type": "ENHANCED_RPGW_EXECUTE_ACTION", "action": action})

# 3. State Update
new_state = reducer(current_state, action)
renderer_pipeline.render_once(new_state)

# 4. Side Effects
event_bus.publish("enhanced_rpgw:feedback", {"type": "sound", "action": action})
```

### **Practice Session**

#### **Purpose**
- Interactive poker practice with AI opponents
- Configurable starting conditions
- Real-time decision making
- Performance tracking and analysis

#### **Core Components**
- **PPSM Integration**: Live game state management
- **AI Decision Engine**: Opponent behavior simulation
- **Session Controller**: Game flow coordination
- **Progress Tracker**: Performance metrics

#### **Implementation Flow**
```python
# 1. Session Initialization
ppsm = PurePokerStateMachine()
session_controller = PracticeSessionController(ppsm, event_bus)

# 2. Game Loop
while session_active:
    current_player = ppsm.get_current_player()
    if current_player.is_ai:
        decision = ai_engine.get_decision(current_player, ppsm.game_state)
        ppsm.execute_action(decision)
    else:
        # Wait for human input via UI
        pass

# 3. State Synchronization
display_state = ppsm_to_display_state(ppsm.game_state)
store.dispatch({"type": "UPDATE_PRACTICE_SESSION", "state": display_state})
```

### **GTO Session**

#### **Purpose**
- Live GTO strategy implementation
- Real-time hand analysis
- Decision tree visualization
- Performance benchmarking

#### **Core Components**
- **GTO Engine**: Strategy calculation and validation
- **Hand Analyzer**: Real-time equity calculations
- **Decision Tree**: Visual strategy representation
- **Benchmark System**: Performance metrics

#### **Implementation Flow**
```python
# 1. Strategy Loading
gto_strategy = load_gto_strategy(strategy_file)
gto_engine = GTOEngine(gto_strategy)

# 2. Live Analysis
current_hand = ppsm.get_current_hand_state()
gto_decision = gto_engine.analyze_hand(current_hand)
equity = gto_engine.calculate_equity(current_hand)

# 3. Decision Support
store.dispatch({
    "type": "UPDATE_GTO_ANALYSIS",
    "decision": gto_decision,
    "equity": equity,
    "confidence": gto_engine.get_confidence()
})
```

---

## 🔧 **ENHANCED RPGW ARCHITECTURE**

### **Component Integration**

The Enhanced RPGW serves as the unified poker table component across all session types, providing consistent rendering, theming, and interaction patterns.

#### **Core Architecture**
```python
class EnhancedRPGW:
    def __init__(self, parent_frame, theme_manager):
        self.canvas_manager = CanvasManager(parent_frame)
        self.layer_manager = LayerManager()
        self.renderer_pipeline = RendererPipeline()
        self.table_components = self._setup_table_components()
    
    def _setup_table_components(self):
        return {
            'table': TableFelt(),
            'seats': Seats(),
            'community': Community(),
            'pot': PotDisplay(),
            'bet': BetDisplay(),
            'dealer': DealerButton(),
            'action': ActionIndicator()
        }
```

#### **State-Driven Rendering**
```python
def render_table(self, display_state):
    """
    Renders poker table based on display state
    - No business logic, pure rendering
    - Responsive sizing and positioning
    - Theme-aware styling
    """
    self.renderer_pipeline.render_once(display_state)
```

#### **Display State Structure**
```python
display_state = {
    'table': {
        'width': 800,
        'height': 600,
        'theme': 'luxury_noir'
    },
    'pot': {
        'amount': 150,
        'position': (400, 300)
    },
    'seats': [
        {
            'player_uid': 'seat1',
            'name': 'Player1',
            'stack': 1000,
            'current_bet': 50,
            'cards': ['Ah', 'Kd'],
            'position': (300, 400),
            'acting': True
        }
    ],
    'board': ['2s', 'Jd', '6c'],
    'dealer': {'position': 0},
    'action': {'type': 'BET', 'player': 'seat1', 'amount': 50},
    'replay': {'current_step': 5, 'total_steps': 16}
}
```

---

## 🎭 **EVENT HANDLER INTEGRATION**

### **Store Reducer Pattern**

The UI architecture uses a Redux-like store with reducers to manage state updates and trigger side effects.

#### **Action Types**
```python
# Enhanced RPGW Actions
ENHANCED_RPGW_EXECUTE_ACTION = "ENHANCED_RPGW_EXECUTE_ACTION"
UPDATE_ENHANCED_RPGW_STATE = "UPDATE_ENHANCED_RPGW_STATE"
ENHANCED_RPGW_ANIMATION_EVENT = "ENHANCED_RPGW_ANIMATION_EVENT"

# Session Actions
UPDATE_PRACTICE_SESSION = "UPDATE_PRACTICE_SESSION"
UPDATE_GTO_ANALYSIS = "UPDATE_GTO_ANALYSIS"
```

#### **Reducer Implementation**
```python
def enhanced_rpgw_reducer(state, action):
    if action['type'] == 'ENHANCED_RPGW_EXECUTE_ACTION':
        # Triggers event for service layer
        new_state = {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': action['action'],
                'action_index': action['action_index'],
                'execution_status': 'pending'
            }
        }
        
        # Trigger service layer event
        if 'event_bus' in state:
            state['event_bus'].publish(
                "enhanced_rpgw:action_executed",
                {
                    "action": action['action'],
                    "action_index": action['action_index'],
                    "state": new_state
                }
            )
        return new_state
    
    elif action['type'] == 'UPDATE_ENHANCED_RPGW_STATE':
        # Updates state from PPSM execution results
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                **action['updates'],
                'execution_status': 'completed'
            }
        }
    
    elif action['type'] == 'ENHANCED_RPGW_ANIMATION_EVENT':
        # Handles animation events
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'animation_event': action['animation_data']
            }
        }
    
    return state
```

### **Service Layer Event Handling**

Services subscribe to events and handle business logic, side effects, and PPSM interactions.

#### **Enhanced RPGW Controller**
```python
class EnhancedRPGWController:
    def __init__(self, event_bus, store, ppsm):
        self.event_bus = event_bus
        self.store = store
        self.ppsm = ppsm
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(
            "enhanced_rpgw:action_executed",
            self._handle_action_execution
        )
        self.event_bus.subscribe(
            "enhanced_rpgw:trigger_animation",
            self._handle_animation_trigger
        )
    
    def _handle_action_execution(self, event_data):
        # Execute action in PPSM (business logic)
        ppsm_result = self._execute_ppsm_action(event_data['action'])
        
        # Update store with PPSM results
        self.store.dispatch({
            "type": "UPDATE_ENHANCED_RPGW_STATE",
            "updates": {
                "ppsm_result": ppsm_result,
                "last_executed_action": event_data['action'],
                "execution_timestamp": time.time()
            }
        })
        
        # Trigger appropriate animations/sounds
        self._trigger_action_feedback(event_data['action'], ppsm_result)
    
    def _execute_ppsm_action(self, action):
        # Placeholder for actual PPSM execution logic
        # This method will contain the core game state updates
        pass  # (Detailed logic for DEAL_HOLE, DEAL_BOARD, POST_BLIND, BET, RAISE, CALL, CHECK, FOLD, END_HAND)
    
    def _trigger_action_feedback(self, action, ppsm_result):
        # Publishes feedback events (sounds, animations)
        feedback_mapping = {
            'DEAL_HOLE': 'card_deal',
            'DEAL_BOARD': 'card_deal',
            'POST_BLIND': 'chip_bet',
            'BET': 'player_bet',
            'RAISE': 'player_bet',
            'CALL': 'player_call',
            'CHECK': 'player_check',
            'FOLD': 'player_fold',
            'END_HAND': 'hand_end'
        }
        feedback_type = feedback_mapping.get(action['type'], 'default')
        self.event_bus.publish(
            "enhanced_rpgw:feedback",
            {
                "type": feedback_type,
                "action": action,
                "ppsm_result": ppsm_result
            }
        )
    
    def _handle_animation_trigger(self, event_data):
        # Publishes animation events to the store for UI to pick up
        if event_data.get('type') == 'player_highlight':
            self.event_bus.publish(
                "enhanced_rpgw:animation_event",
                {
                    "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                    "delay_ms": 200,
                    "action": "clear_highlight"
                }
            )
```

---

## 🎨 **THEME SYSTEM INTEGRATION**

### **Design System v2**

The theme system provides a comprehensive, token-based approach to styling and theming across all UI components.

#### **Token Categories**
- **Colors**: Semantic color tokens (primary, secondary, accent)
- **Typography**: Font families, sizes, weights, and line heights
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl)
- **Elevation**: Shadow and depth tokens
- **Border Radius**: Corner rounding values
- **Animation**: Duration and easing curves

#### **Integration Points**
```python
# Theme Manager
theme_manager = ThemeManager()
theme_manager.load_theme('luxury_noir')

# Component Usage
button.configure(
    bg=theme_manager.get_token('btn.primary.bg'),
    fg=theme_manager.get_token('btn.primary.fg'),
    font=theme_manager.get_token('font.button')
)
```

#### **Theme Change Handling**
```python
def on_theme_change(self, new_theme):
    # Update theme manager
    self.theme_manager.load_theme(new_theme)
    
    # Re-render Enhanced RPGW with new theme
    self._render_enhanced_rpgw_table()
    
    # Refresh widget sizing for new theme
    self._refresh_enhanced_rpgw_widget()
```

---

## 🚀 **PERFORMANCE AND SCALABILITY**

### **Rendering Optimization**

- **Lazy Rendering**: Only re-render components when state changes
- **Layer Management**: Efficient z-order management via LayerManager
- **Canvas Optimization**: Minimize canvas redraws and object creation
- **Memory Management**: Proper cleanup of canvas objects and event handlers

### **State Management Efficiency**

- **Immutable Updates**: Use spread operators for state updates
- **Selective Subscriptions**: Components only subscribe to relevant state slices
- **Event Debouncing**: Prevent excessive event processing during rapid state changes
- **Batch Updates**: Group multiple state changes into single render cycles

### **Resource Management**

- **Sound Caching**: Pre-load and cache sound files
- **Image Optimization**: Use appropriate image formats and sizes
- **Memory Monitoring**: Track memory usage and implement cleanup strategies
- **Performance Profiling**: Monitor render times and optimize bottlenecks

---

## 🧪 **TESTING AND QUALITY ASSURANCE**

### **Testing Strategy**

#### **Unit Testing**
- **Reducers**: Test state transformations and side effects
- **Selectors**: Validate state derivation logic
- **Services**: Test business logic and PPSM interactions
- **Components**: Test rendering and event handling

#### **Integration Testing**
- **Session Flows**: End-to-end session execution
- **Theme Switching**: Theme change behavior and consistency
- **Hand Replay**: Complete hand replay functionality
- **Performance**: Render performance and memory usage

#### **Accessibility Testing**
- **WCAG Compliance**: Automated and manual accessibility testing
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader**: Screen reader compatibility
- **Color Contrast**: Visual accessibility validation

### **Quality Metrics**

- **Code Coverage**: Minimum 80% test coverage
- **Performance Benchmarks**: Render time < 16ms per frame
- **Memory Usage**: Stable memory footprint during extended use
- **Error Handling**: Graceful degradation and user feedback
- **Accessibility Score**: WCAG 2.1 AA compliance

---

## 📚 **IMPLEMENTATION GUIDELINES**

### **Development Workflow**

1. **Feature Planning**: Define requirements and acceptance criteria
2. **Architecture Review**: Ensure compliance with architectural principles
3. **Implementation**: Follow established patterns and conventions
4. **Testing**: Comprehensive unit and integration testing
5. **Code Review**: Architecture and quality review
6. **Integration**: Merge and deploy with monitoring

### **Code Standards**

- **Python**: PEP 8 compliance with project-specific overrides
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Clear docstrings and inline comments
- **Error Handling**: Graceful error handling with user feedback
- **Logging**: Structured logging for debugging and monitoring

### **Architecture Compliance**

- **Single Source of Truth**: All state managed through Store
- **Event-Driven**: UI actions flow through Store → Reducer → Services
- **Pure Components**: UI components are stateless renderers
- **Service Separation**: Business logic isolated in service layer
- **Theme Integration**: All styling via theme tokens

---

## 🔮 **FUTURE ROADMAP**

### **Phase 1: Core Implementation**
- Complete Enhanced RPGW integration
- Implement all three session types
- Establish testing framework
- Performance optimization

### **Phase 2: Advanced Features**
- Advanced animation system
- Enhanced sound integration
- Performance analytics
- Accessibility improvements

### **Phase 3: Scalability**
- Multi-table support
- Advanced session management
- Plugin architecture
- Cloud integration

---

*This document serves as the authoritative reference for the PokerPro Trainer architecture. All implementations must comply with these principles and patterns.*

```

---

## 🎯 ROOT CAUSE ANALYSIS

### Primary Issue
The `TableRendererProps` objects are being recreated on every model update via `TableRendererProps.from_model(model)`, causing the equality check `self.current_props == props` to always fail, even when the actual data is identical.

### Key Problem Areas
1. **Fresh Object Creation**: `TableRendererProps.from_model()` creates new instances every time
2. **Nested Object Inequality**: The `seats` dictionary contains `SeatState` objects that may be recreated
3. **Model Update Frequency**: Frequent model updates trigger unnecessary re-renders
4. **Props Comparison Logic**: Dataclass equality fails due to nested mutable objects

### Reproduction Steps
1. Start application: `python3 backend/run_new_ui.py`
2. Navigate to 'Hands Review' tab
3. Observe infinite console output and unresponsive UI
4. Application must be terminated with Ctrl+C

---

## 💡 PROPOSED SOLUTIONS

### Solution 1: Props Memoization
Cache `TableRendererProps` objects and only create new ones when underlying data actually changes:

```python
class MVUHandsReviewTab:
    def __init__(self, ...):
        self._cached_props = None
        self._last_model_hash = None
    
    def _on_model_changed(self, model: Model) -> None:
        # Create hash of relevant model data
        model_hash = hash((id(model.seats), model.review_cursor, model.waiting_for))
        
        # Only create new props if model actually changed
        if model_hash != self._last_model_hash:
            self._cached_props = TableRendererProps.from_model(model)
            self._last_model_hash = model_hash
        
        if self.table_renderer and self._cached_props:
            self.table_renderer.render(self._cached_props)
```

### Solution 2: Deep Equality Check
Implement proper deep comparison for `TableRendererProps`:

```python
@dataclass(frozen=True)
class TableRendererProps:
    # ... fields ...
    
    def __eq__(self, other):
        if not isinstance(other, TableRendererProps):
            return False
        
        return (
            self.seats == other.seats and
            self.board == other.board and
            self.pot == other.pot and
            # ... compare all fields
        )
```

### Solution 3: Selective Subscription
Only notify view subscribers when rendering-relevant fields actually change.

---

## 📋 END OF MVU INFINITE RENDERING LOOP BUG REPORT

**Priority**: HIGH - Application completely unusable

**Environment**: Python 3.13.2, Tkinter, MVU Architecture, macOS

*This comprehensive report contains all source code and analysis needed to resolve the MVU infinite rendering loop issue.*
