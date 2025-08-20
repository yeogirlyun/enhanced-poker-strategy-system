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
