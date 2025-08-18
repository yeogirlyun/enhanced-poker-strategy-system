# Hands Review Validation Bug Report

## Issue Summary
The hands review validation tester is failing because the `current_bet` is being incorrectly reset to $0.0 after BET actions are executed, preventing subsequent CALL actions from working properly.

## Current Status
- **Success Rate**: 0.0% (0 out of 100 hands)
- **Progress Made**: Hands now progress through multiple streets (preflop → flop → turn)
- **Critical Issue**: BET actions don't properly update `current_bet`, breaking action validation

## Detailed Bug Description

### What Works
1. ✅ **RAISE actions** on preflop work correctly
2. ✅ **CALL actions** on preflop work correctly  
3. ✅ **CHECK actions** on flop work correctly
4. ✅ **Street transitions** work (preflop → flop → turn)
5. ✅ **Deck provider** integration works
6. ✅ **Auto-deal remaining board** functionality works

### What's Broken
1. ❌ **BET actions** don't update `current_bet` correctly
2. ❌ **CALL actions** after BETs fail because `current_bet` is $0.0
3. ❌ **Pot calculation** is still off (showing $155.0 instead of expected $295.0)

## Bug Reproduction Steps

1. Run `python3 tools/hands_review_validation_tester.py`
2. Observe that hands progress through preflop and flop successfully
3. On turn street, seat2 successfully bets $40
4. System shows "Action executed successfully" 
5. But then immediately shows `FPSM current_bet: $0.0`
6. When seat1 tries to CALL $40, action validation fails with:
   ```
   ❌ Invalid action: seat1 cannot CALL $40.00. 
   Valid: {'fold': True, 'check': True, 'call': False, 'bet': True, 'raise': True, 'call_amount': 0.0, 'min_bet': 10, 'max_bet': 500}
   ```

## Root Cause Analysis

### Primary Issue: `current_bet` Reset Timing
The `_reset_bets_for_new_round()` method is being called at the wrong time, causing `current_bet` to be reset to $0.0 after BET actions are executed.

**Evidence from logs:**
```
✅ BOT_ACTION_DEBUG: Action executed successfully
   FPSM current_bet: $0.0  # Should be $40.0 after BET
```

### Secondary Issue: Pot Calculation
The initial pot calculation in the hands review session is not correctly accounting for all blind postings and initial bets from the hand model.

**Evidence:**
```
❌ Results differ from original hand
   - Pot size mismatch: original=295, final=155.0
```

## Technical Details

### Affected Components
1. **`FlexiblePokerStateMachine._reset_bets_for_new_round()`** - Called at wrong time
2. **`FlexiblePokerStateMachine._is_round_complete()`** - May be incorrectly determining round completion
3. **`FlexiblePokerStateMachine.execute_action()`** - BET action handling works but gets reset
4. **`HandsReviewBotSession.start_hand()`** - Initial pot calculation

### Code Flow
1. Street transition (e.g., to turn) calls `_reset_bets_for_new_round()`
2. `current_bet` is set to $0.0 for all players
3. seat2 executes BET $40 action successfully
4. `current_bet` should become $40.0 but gets reset to $0.0
5. seat1 tries to CALL $40 but validation fails because `call_amount: 0.0`

## Proposed Fixes

### Fix 1: Prevent Premature Bet Reset
Modify `_reset_bets_for_new_round()` to not reset bets when there are active betting actions in progress.

### Fix 2: Fix Round Completion Logic
Ensure `_is_round_complete()` correctly identifies when players have unequal bets and should continue the round.

### Fix 3: Fix Initial Pot Calculation
Correctly calculate initial pot from hand model actions including blinds and initial bets.

## Files Modified in Recent Fixes

1. **`backend/providers/deck_provider.py`** - Added deck provider protocol
2. **`backend/providers/preloaded_deck.py`** - Added deterministic deck implementation
3. **`backend/providers/random_deck.py`** - Added random deck implementation
4. **`backend/core/flexible_poker_state_machine.py`** - Added deck provider integration and auto-deal functionality
5. **`backend/core/bot_session_state_machine.py`** - Updated to use deck providers
6. **`backend/tools/hands_review_validation_tester.py`** - Fixed sound manager mock

## Next Steps
1. Debug why `_reset_bets_for_new_round()` is being called after BET actions
2. Fix the round completion logic to properly handle unequal bets
3. Fix initial pot calculation from hand model data
4. Test validation success rate improvement

## Expected Outcome After Fixes
- Hands should progress through all streets successfully
- BET actions should properly update `current_bet`
- CALL actions should work after BETs
- Pot calculations should match original hand data
- Validation success rate should approach 100%
