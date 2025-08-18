# INFINITE LOOP ANALYSIS - BB Series Failure

## Overview
Detailed analysis of the infinite loop pattern affecting BB series hands (1-10) in hands review validation.

## Loop Detection Evidence
```
Error: INFINITE_LOOP_DETECTED: Loop guard tripped.
street=river state=river_betting pot=500.0
dealer=0 action_idx=0  
need_action_from=[0, 1]
steps_this_street=201 steps_this_hand=207
players=[
  {'name': 'seat1', 'stack': 750.0, 'current_bet': 0.0, 'is_active': True, 'has_folded': False, 'position': 'SB'}, 
  {'name': 'seat2', 'stack': 750.0, 'current_bet': 0.0, 'is_active': True, 'has_folded': False, 'position': 'BB'}
]
```

## Loop Pattern Analysis

### Initial State (River Betting)
- **Street**: river  
- **Current Bet**: $0 (no wager yet)
- **Action Player**: seat1 (index 0)
- **Need Action From**: [0, 1] (both players need to act)
- **Expected Flow**: seat2 should act first (OOP in HU)

### Loop Sequence (Repeating 200+ times)
```
🃏 FIXED_PPSM: Action advances to seat2   ← PPSM asks adapter for seat2 decision
[Adapter sees: next action is seat1 BET 760.0]
[Adapter returns: None]                  ← No decision for seat2 (wrong player)
🃏 FIXED_PPSM: Action advances to seat1   ← PPSM tries seat1  
[Adapter sees: current action is seat1 BET 760.0]
[Adapter returns: ActionType.BET, 760.0]
[PPSM validation: Invalid action]        ← seat1 can't BET first on river (OOP should act)
🃏 FIXED_PPSM: Action advances to seat2   ← Back to seat2
[Loop repeats...]
```

### Why Loop Never Resolves
1. **seat2** needs to CHECK first (OOP postflop rule)
2. **Hand data** shows seat1 BET 760.0 first (missing seat2 CHECK)  
3. **Adapter** has no decision for seat2 when asked
4. **PPSM** advances to seat1, but seat1 BET is invalid (wrong turn)
5. **need_action_from** never gets cleared because no valid actions execute
6. **Loop continues** until safety guard triggers (200 steps)

## Root Cause: Missing CHECK Injection

### Current Adapter Logic (Insufficient)
```python
# This only works when next action is BET by other player
if postflop and game_state.current_bet == 0 and next_is_bet:
    return ActionType.CHECK, None
```

### BB Series Problem
```python
# When PPSM asks: get_decision("seat2", game_state)
# current_action.actor_uid = "seat1" (not seat2)  
# next_is_bet = True (seat1 BET 760.0)
# BUT: current_action.actor_uid != player_name ("seat2")
# SO: Condition fails, no CHECK injection
```

## Solution: Enhanced CHECK Injection

### Required Logic
```python
def get_decision(self, player_name: str, game_state) -> tuple:
    # ... existing logic ...
    
    if current_action.actor_uid == player_name:
        # Normal case: action is for requested player
        # ... existing handling ...
    else:
        # Action is for different player
        from core.hand_model import ActionType as HM, Street
        street = str(game_state.street).lower()
        postflop = street in ("flop", "turn", "river")
        
        # Enhanced injection: ANY postflop action by wrong player 
        # when current_bet=0 indicates missing CHECK
        if postflop and game_state.current_bet == 0:
            return ActionType.CHECK, None  # INJECT CHECK
        
        # Otherwise no decision for this player
        return None
```

### Key Enhancement
- Don't check `next_is_bet` specifically
- Check ANY action by wrong player on new street  
- This covers both missing CHECK patterns:
  - HC series: explicit CHECKs (current fix works)
  - BB series: no CHECKs at all (needs enhanced fix)

## Expected Resolution

### After Fix - BB Series Flow
```
🃏 FIXED_PPSM: Action advances to seat2
[Adapter asked for seat2 decision]
[Adapter sees: next action is seat1 (wrong player), current_bet=0, postflop=True]  
[Adapter returns: ActionType.CHECK, None]     ← INJECTED CHECK
🃏 FIXED_PPSM: seat2 CHECK $0 (pot: $500.0)   ← Valid action executed
🃏 FIXED_PPSM: Action advances to seat1
[Adapter asked for seat1 decision]
[Adapter sees: current action is seat1 BET 760.0]
[Adapter returns: ActionType.BET, 760.0]      ← Now valid (seat2 already checked)
🃏 FIXED_PPSM: seat1 BET $760.0 (pot: $1260.0) ← Valid action executed  
[need_action_from removes seat1]
🃏 FIXED_PPSM: Action advances to seat2
[Adapter returns: ActionType.CALL, None]
🃏 FIXED_PPSM: seat2 CALL $0 (pot: $2020.0)   ← Valid action executed
[need_action_from removes seat2, now empty]
🃏 FIXED_PPSM: Street ended, pot now: $2020.0  ← Loop resolved!
```

## Performance Impact

### Current Loop Cost
- **200+ invalid iterations** per failed hand
- **CPU intensive**: validation + player advancement each loop
- **Memory impact**: repeated state queries and logging
- **Time cost**: ~100ms per failed hand (vs <1ms for working hands)

### After Fix Benefits
- **8-10 valid actions** total per hand
- **Direct execution**: no invalid action retries
- **Memory efficient**: no repeated state queries  
- **Time optimal**: <1ms per hand

## Validation Metrics

### Current BB Series (Broken)
```
Actions: 60/80 (75% success)
Hands: 0/10 (0% success) 
Infinite loops: 10/10 (100% failure rate)
Average steps per hand: 207
```

### Target BB Series (Fixed)  
```
Actions: 80/80 (100% success)
Hands: 10/10 (100% success)
Infinite loops: 0/10 (0% failure rate) 
Average steps per hand: 8-10
```

## Implementation Priority

1. **CRITICAL**: Enhanced CHECK injection logic
2. **HIGH**: Test on BB001 hand in isolation
3. **HIGH**: Validate all BB series hands  
4. **MEDIUM**: Performance regression testing
5. **LOW**: Loop detection tuning (should be unused after fix)

**Success criteria**: Zero infinite loop detections in hands review validation
