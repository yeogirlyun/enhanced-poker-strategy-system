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
