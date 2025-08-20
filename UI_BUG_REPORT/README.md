# Poker UI Bug Report

## Missing Elements
1. Stack Size Display:
   - Stack size chip graphics not visible
   - Stack size labels not showing
   - Stack updates not reflecting correctly after bets

2. Betting Graphics:
   - User bet/call chip graphics missing
   - Bet amount labels not displaying
   - Betting position indicators not showing

3. Animations:
   - Bet → Pot animation missing at street end
   - Pot → Winner animation missing at showdown
   - Winner announcement not displaying

## Core Issues Found

1. ChipAnimations._create_chip_with_label() Error:
```
TypeError: ChipAnimations._create_chip_with_label() missing 1 required positional argument: 'chip_size'
```

2. Acting Seat Issues:
```
⚠️ No acting seat found for chips_to_pot animation
```

## Affected Components

1. hands_review_tab.py:
   - Missing bet graphics creation
   - Incomplete animation handling
   - Stack size display issues

2. chip_animations.py:
   - Missing chip_size parameter
   - Animation triggers not firing properly
   - Position calculation errors

3. effect_bus.py:
   - Sound effects not properly mapped
   - Animation events not synchronized
   - Missing winner announcement events

4. game_director.py:
   - Gate timing issues
   - Animation completion tracking incomplete
   - Event sequencing problems

## Priority Fixes

1. Add chip_size parameter to ChipAnimations._create_chip_with_label():
```python
def _create_chip_with_label(self, canvas, start_x, start_y, denom, tokens, chip_size=58, tags=None):
    if tags is None:
        tags = []
    # Create chip graphic implementation
```

2. Fix acting seat tracking in hands_review_tab.py:
```python
def _handle_effect_animate(self, effect_name, data):
    if effect_name == "chips_to_pot":
        acting_seat = self._get_acting_seat()
        if acting_seat:
            # Animation implementation
```

3. Add animation triggers to effect_bus.py:
```python
def trigger_animation(self, name, data):
    self.subscribers.dispatch(
        "animation_effect",
        {"name": name, "data": data}
    )
```

4. Fix GameDirector animation gates:
```python
def notify_animation_complete(self, event_data=None):
    if event_data is None:
        event_data = {}
    print(f"🎬 GameDirector: Animation complete: {event_data.get('name', 'unknown')}")
    self._check_animation_queue()  # Add this line
    self.gate_end()
```

## Testing Steps

1. Verify Stack Display:
   - Check stack size graphics visible for all players
   - Confirm stack labels update after bets/calls
   - Test stack animations during betting

2. Verify Bet Graphics:
   - Confirm bet chips appear when betting
   - Check bet labels show correct amounts
   - Verify position indicators match actions

3. Test Animations:
   - Test bet → pot animations each street
   - Verify pot → winner animations
   - Check winner announcements display

## Environment Info
- OS: macOS
- Python: 3.13
- GUI Backend: Canvas
- Sound: pygame.mixer
