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
