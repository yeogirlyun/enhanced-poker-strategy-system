# 🎨 Token-Driven UI System Integration Guide

## 🎯 Overview

This guide shows how to integrate the complete token-driven UI system into your poker application. The system provides:

- **Deterministic color generation** from 6 base colors per theme
- **Professional visual effects** (glows, pulses, animations)
- **Consistent theming** across all 16 themes
- **Micro-interactions** for premium feel

## 📁 New Files Added

```
backend/ui/services/
├── theme_utils.py              # Color derivation helpers
├── theme_factory.py            # Token generation from base palettes
└── theme_manager.py            # Enhanced with token system

backend/ui/tableview/components/
├── table_center.py             # Subtle center pattern
├── enhanced_cards.py           # Token-driven card graphics
├── chip_animations.py          # Flying chip animations
├── micro_interactions.py       # Subtle glows and pulses
└── token_driven_renderer.py    # Main coordinator
```

## 🚀 Quick Integration

### 1. Update Your Table Renderer

Replace your existing table rendering with the token-driven system:

```python
# In your main table component
from .components.token_driven_renderer import TokenDrivenRenderer

class PokerTable:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.renderer = TokenDrivenRenderer(theme_manager)
    
    def render(self, canvas, state):
        """Render complete poker table with all enhancements"""
        self.renderer.render_complete_table(canvas, state)
    
    def animate_bet_to_pot(self, canvas, from_x, from_y, amount):
        """Animate chips flying to pot"""
        self.renderer.animate_bet_to_pot(canvas, from_x, from_y, amount)
    
    def animate_pot_to_winner(self, canvas, winner_x, winner_y, amount):
        """Animate pot to winner with celebration"""
        self.renderer.animate_pot_to_winner(canvas, winner_x, winner_y, amount)
```

### 2. Add Micro-Interactions to Buttons

Enhance your buttons with hover effects and press feedback:

```python
# In your button components
def on_button_hover(self, event):
    """Add glow effect on hover"""
    self.renderer.add_hover_effect(
        self.canvas, "my_button", 
        self.x, self.y, self.width, self.height
    )

def on_button_leave(self, event):
    """Remove glow effect"""
    self.renderer.remove_hover_effect(self.canvas, "my_button")

def on_button_press(self, event):
    """Visual feedback for press"""
    self.renderer.button_press_feedback(
        self.canvas, self.x, self.y, self.width, self.height
    )
```

### 3. Use Token-Driven Colors

Replace hard-coded colors with token lookups:

```python
# OLD: Hard-coded colors
canvas.create_rectangle(x, y, x+w, y+h, fill="#1E4D2B", outline="#C9A86A")

# NEW: Token-driven colors
tokens = self.theme.get_all_tokens()
felt_color = tokens.get("table.felt", "#1E4D2B")
metal_color = tokens.get("table.inlay", "#C9A86A")
canvas.create_rectangle(x, y, x+w, y+h, fill=felt_color, outline=metal_color)
```

## 🎨 Theme System Architecture

### Base Color Palettes (6 colors → 100+ tokens)

Each theme needs only 6 base colors:

```python
"Forest Green Professional": {
    "felt": "#1E4D2B",      # Primary table surface
    "metal": "#C9A86A",     # Trim/accent metallic
    "accent": "#2E7D32",    # Secondary accent
    "raise_": "#B63D3D",    # Danger/raise actions
    "call": "#2AA37A",      # Success/call actions
    "neutral": "#9AA0A6",   # Neutral gray base
    "text": "#EDECEC"       # Primary text color
}
```

### Automatic Token Generation

The system automatically generates 100+ tokens:

```python
# Surfaces
"table.felt": felt,
"table.rail": darken(felt, 0.75),
"table.centerPattern": lighten(felt, 0.06),

# Cards  
"card.face.bg": lighten(neutral, 0.85),
"card.pip.red": mix(raise_c, "#FF2A2A", 0.35),

# Chips
"chip.$25": "#2AA37A",  # Standard casino colors
"chip.rim": alpha_over(metal, "#000000", 0.35),

# Micro-interactions
"glow.soft": alpha_over(metal, "#000000", 0.20),
"pulse.slow": alpha_over(call_c, "#000000", 0.30),
```

## 🎬 Animation System

### Flying Chip Animations

```python
# Bet to pot
self.renderer.animate_bet_to_pot(canvas, player_x, player_y, bet_amount)

# Pot to winner (with celebration)
self.renderer.animate_pot_to_winner(canvas, winner_x, winner_y, pot_amount)
```

### Card Reveal Effects

```python
# Flip animation with shimmer
self.renderer.animate_card_reveal(
    canvas, card_x, card_y, card_w, card_h,
    from_card="XX", to_card="Ah"
)
```

### Micro-Interactions

```python
# Pulse acting player
self.renderer.pulse_acting_player(canvas, seat_x, seat_y)

# Flash pot on increase
self.micro_interactions.flash_pot_increase(canvas, pot_x, pot_y, pot_w, pot_h)

# Winner confetti burst
self.micro_interactions.winner_confetti_burst(canvas, winner_x, winner_y)
```

## 🎯 Visual Elements

### Table Center Pattern

Subtle ellipse and micro-mosaic at table center:

```python
# Automatically rendered by TokenDrivenRenderer
# Creates 6% lighter ellipse with metallic arc patterns
self.table_center.render(canvas, state)
```

### Enhanced Card Graphics

Professional cards with theme-integrated backs:

```python
# Face-up card with token colors
self.enhanced_cards.draw_card_face(canvas, x, y, "A", "h", w, h)

# Face-down with diamond lattice pattern
self.enhanced_cards.draw_card_back(canvas, x, y, w, h)
```

### Chip Stacks & Animations

Value-based chip colors with 3D stacking:

```python
# Static chip stack
self.chip_animations.draw_chip_stack(canvas, x, y, amount)

# Flying chips with arc trajectory
self.chip_animations.fly_chips_to_pot(canvas, from_x, from_y, to_x, to_y, amount)
```

## 🔧 Integration Steps

### Step 1: Update Theme Manager

The theme manager is already enhanced to use the token system. Verify it's working:

```python
# Test token access
theme = ThemeManager()
tokens = theme.get_all_tokens()
print(f"Available tokens: {len(tokens)}")
print(f"Table felt: {tokens.get('table.felt')}")
```

### Step 2: Replace Existing Components

Gradually replace existing components:

```python
# Replace card rendering
# OLD: Basic rectangles with hard-coded colors
# NEW: Enhanced cards with token-driven styling

# Replace pot display  
# OLD: Simple text label
# NEW: Chip stacks with animations

# Replace player seats
# OLD: Static rectangles
# NEW: Enhanced pods with micro-interactions
```

### Step 3: Add Animation Triggers

Connect animations to game events:

```python
# When player bets
def on_player_bet(self, player_id, amount):
    player_x, player_y = self.get_player_position(player_id)
    self.renderer.animate_bet_to_pot(canvas, player_x, player_y, amount)

# When hand ends
def on_hand_end(self, winner_id, pot_amount):
    winner_x, winner_y = self.get_player_position(winner_id)
    self.renderer.animate_pot_to_winner(canvas, winner_x, winner_y, pot_amount)
```

### Step 4: Add Micro-Interactions

Enhance user experience with subtle effects:

```python
# Acting player pulse
def set_acting_player(self, player_id):
    seat_x, seat_y = self.get_player_position(player_id)
    self.renderer.pulse_acting_player(canvas, seat_x, seat_y)

# Button hover effects
def setup_button_interactions(self, button):
    button.bind("<Enter>", lambda e: self.add_hover_effect(button))
    button.bind("<Leave>", lambda e: self.remove_hover_effect(button))
    button.bind("<Button-1>", lambda e: self.button_press_feedback(button))
```

## 🎨 Customization

### Adding New Themes

Create new themes by defining 6 base colors:

```python
"My Custom Theme": {
    "felt": "#2A1810",      # Dark brown felt
    "metal": "#B8860B",     # Dark goldenrod trim  
    "accent": "#8B4513",    # Saddle brown accent
    "raise_": "#DC143C",    # Crimson raise
    "call": "#228B22",      # Forest green call
    "neutral": "#A0A0A0",   # Gray neutral
    "text": "#F5F5DC"       # Beige text
}
```

All 100+ tokens are automatically generated!

### Customizing Animations

Adjust animation parameters:

```python
# Slower chip animations
self.chip_animations.fly_chips_to_pot(
    canvas, from_x, from_y, to_x, to_y, amount,
    frames=30  # Default: 20
)

# Longer pulse duration
self.micro_interactions.pulse_seat_ring(
    canvas, seat_x, seat_y, seat_w, seat_h,
    duration_ms=2000  # Default: 1000
)
```

## 🚀 Performance Notes

### Efficient Rendering

- **Token caching**: Tokens are computed once per theme change
- **Effect cleanup**: All animations clean up automatically
- **Canvas optimization**: Uses tags for efficient element management

### Memory Management

```python
# Clean up when switching hands
def on_new_hand(self):
    self.renderer.clear_all_effects(canvas)
    self.renderer.stop_all_animations()

# Clean up on app exit
def on_app_exit(self):
    self.renderer.stop_all_animations()
```

## 🎯 Result

With this system, you get:

- ✅ **16 professional themes** with consistent styling
- ✅ **Smooth animations** for all poker actions
- ✅ **Micro-interactions** that feel premium
- ✅ **Deterministic colors** - no more guessing hex codes
- ✅ **Easy customization** - 6 colors → complete theme
- ✅ **Performance optimized** - efficient rendering and cleanup

The poker table will feel **designed and alive** while staying **perfectly consistent** across all themes! 🎰✨
