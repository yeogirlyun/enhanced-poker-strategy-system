# Hands Review Panel - Problem Analysis

## Executive Summary

The Hands Review panel is experiencing critical issues:
1. **Poker Table Not Loading**: ReusablePokerGameWidget not displaying
2. **Next/Auto-Play Not Working**: Action execution fails
3. **Data Conversion Errors**: Hand model conversion failing

## Current Status
- ✅ Panel Creation: UI loads with 393 hands
- ✅ Hand Selection: Users can select hands
- ❌ Hand Loading: Fails with conversion errors  
- ❌ Poker Table Display: No table appears
- ❌ Action Execution: Buttons don't work

## Architecture Goal

Follow GTO Session pattern:
```
UnifiedHandsReviewPanel
    ↓
HandsReviewBotSession (extends BotSessionStateMachine)  
    ↓
ReusablePokerGameWidget (poker table display)
```

## Critical Problems

### Problem 1: Data Conversion Failures
```
ERROR: 'str' object has no attribute 'get'
ERROR: Hand.__init__() got unexpected keyword 'actions'
```

### Problem 2: Session Integration 
- HandsReviewBotSession created but doesn't integrate with widget
- No poker table display after loading
- Next button doesn't execute actions

### Problem 3: Import Dependencies
```
Import warning: No module named 'backend'. Using fallbacks.
```

## Expected vs Current Flow

### Expected (like GTO):
1. Select hand → 2. Create session → 3. Create widget → 4. Display table → 5. Execute actions

### Current (broken):
1. Select hand ✅ → 2. Conversion fails ❌

## Requirements

**Primary Goals:**
1. Load hands successfully 
2. Display poker table with cards/chips
3. Next button advances through actions
4. Visual updates after each action
5. Complete hand replay functionality

**Success Criteria:**
- User can load any hand without errors
- Poker table displays correctly
- Step-by-step action execution works
- Visual feedback shows game state changes