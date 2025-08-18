# Infinite Loop Analysis - Technical Deep Dive

## 🔍 **Suspected Location**

**File**: `pure_poker_state_machine.py`  
**Method**: `play_hand_with_decision_engine()` (lines ~290-400)  
**Phase**: FLOP_BETTING after successful flop card dealing  

## 🕵️ **Loop Analysis**

### **The Problematic Loop**
```python
# Line ~320-370 in play_hand_with_decision_engine()
while (self.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN] and 
       action_count < max_actions):
    
    # Check if we need a player action
    if self.action_player_index >= 0 and self.action_player_index < len(self.game_state.players):
        current_player = self.game_state.players[self.action_player_index]
        
        # Get decision from engine
        if self.decision_engine and self.decision_engine.has_decision_for_player(current_player.name):
            # THIS SECTION LIKELY HAS THE BUG
        else:
            # No decision available, break to avoid infinite loop
            break
    else:
        # Auto-advance for non-action states
        # THIS SECTION MIGHT ALSO HAVE ISSUES
```

## 🎯 **Three Likely Bug Scenarios**

### **Scenario 1: Decision Engine Mismatch**
```python
# HYPOTHESIS: Decision engine logic bug
if self.decision_engine.has_decision_for_player(current_player.name):
    # Returns True but get_decision() returns None -> infinite loop
    decision = self.decision_engine.get_decision(current_player.name, self.game_state)
    if decision:
        # Execute action
    else:
        # BUG: Should break here but doesn't
        # Loops forever checking same condition
```

### **Scenario 2: Action Player Index Never Changes**
```python
# HYPOTHESIS: action_player_index stuck at same value
# Player 0 acts, but action_player_index never advances to player 1
# So loop keeps asking same player for same decision infinitely
current_player = self.game_state.players[self.action_player_index]  # Always player 0
if self.decision_engine.has_decision_for_player(current_player.name):  # Always True
    # Gets same decision over and over
```

### **Scenario 3: State Advancement Failure**
```python
# HYPOTHESIS: Auto-advancement section has bug
else:
    # Check if more decisions available from decision engine
    if (self.decision_engine and 
        hasattr(self.decision_engine, 'current_action_index')):
        # BUG: This condition might always be True
        # Never breaks out of loop
```

## 🔬 **Evidence Supporting Scenario 2**

From the timeout trace:
1. ✅ Preflop completes successfully (seat1 RAISE, seat2 CALL)
2. ✅ Flop cards dealt: ['6D', 'TD', '2D']  
3. ✅ Transitions to FLOP_BETTING state
4. ❌ **HANGS** - Should execute seat1 BET 60.0

**Expected**: seat1 should BET 60.0 on flop  
**Actual**: Infinite loop before action executes  

This suggests `action_player_index` is set correctly (0 = seat1), but something in the decision logic is looping.

## 🎯 **Most Likely Root Cause**

**Decision Engine Index Management Bug**:

```python
# In HandModelDecisionEngineAdapter.get_decision()
if self.current_action_index >= len(self.actions_for_replay):
    return None  # No more actions

current_action = self.actions_for_replay[self.current_action_index]

if current_action.actor_uid == player_name:
    self.current_action_index += 1  # BUG: This might not increment properly
    return (ActionType.BET, 60.0)
else:
    return None  # BUG: Wrong player, but should advance somehow
```

**Hypothesis**: The decision engine is stuck returning the same decision or returning None when it should advance, causing the main loop to never progress.

## 🔧 **Debug Steps to Confirm**

1. Add logging to `play_hand_with_decision_engine()` loop
2. Log `action_player_index`, `current_action_index`, decision results
3. Check if decision engine state advances properly
4. Verify action execution actually changes game state

---

**Next Action**: Add detailed logging to confirm which scenario is causing the infinite loop.
