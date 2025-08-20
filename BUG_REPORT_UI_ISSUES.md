# Bug Report: Missing UI Elements and Animations in Poker Table

## Summary
The following UI elements and animations are missing in the poker table interface:

1. **Stack Size Chip Graphics and Labels**: Player stack sizes are not displayed as chip graphics or labels.
2. **User Bet/Call Chip Graphics and Labels**: Bets and calls made by players are not visually represented with chip graphics or labels.
3. **Bet to Pot Animation**: The animation of chips moving from a player's stack to the pot at the end of a street is missing.
4. **Pot to Winner Animation**: The animation of chips moving from the pot to the winner's stack at showdown is missing.
5. **Winner Announcement**: The winner of the hand is not announced visually or textually.

## Steps to Reproduce
1. Launch the poker table UI using `run_new_ui.py`.
2. Play through a hand or review a hand in the Hands Review tab.
3. Observe the missing elements and animations during gameplay or hand review.

## Expected Behavior
- Stack sizes should be displayed as chip graphics and labels.
- Bets and calls should be represented with chip graphics and labels.
- Chips should animate from player stacks to the pot at the end of a street.
- Chips should animate from the pot to the winner's stack at showdown.
- The winner should be announced visually or textually.

## Actual Behavior
- None of the above elements or animations are displayed.

## Relevant Source Code
The following files are likely related to the missing elements and animations:

1. **`game_director.py`**: Manages timing, autoplay, and event scheduling.
2. **`effect_bus.py`**: Handles sound and animation effects.
3. **`hands_review_tab.py`**: Implements the Hands Review tab UI.
4. **Tableview Components**:
   - `chip_graphics.py`
   - `chip_animations.py`
   - `pot_display.py`
   - `seats.py`

## Attachments
All relevant source code files have been included in the attached zip file for review.

## Additional Notes
- Console logs do not show errors related to these missing elements.
- Ensure that state inputs to the tableview components are correct.
- Verify that animation events are triggered correctly in `EffectBus` and `GameDirector`.

---

**Date**: August 19, 2025
**Reported By**: yeogirlyun
