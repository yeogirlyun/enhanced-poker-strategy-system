"""
Premium Casino Chip System
==========================

Theme-aware chip rendering with distinct visual types:
- Stack chips (player stacks): calm, readable, less saturated
- Bet/Call chips (flying chips): vivid with theme accent for motion tracking  
- Pot chips (pot visualization): prestigious metal-leaning design

Features:
- Consistent casino denominations with theme-tinted colors
- Radial stripe patterns for instant denomination recognition
- Hover states, glow effects, and animation support
- Automatic theme integration via token system
"""

import math
from typing import Tuple, List, Optional


# Standard casino denominations with base colors
CHIP_DENOMINATIONS = [
    (1,    "#2E86AB"),  # $1  – blue
    (5,    "#B63D3D"),  # $5  – red
    (25,   "#2AA37A"),  # $25 – green
    (100,  "#3C3A3A"),  # $100 – black/graphite
    (500,  "#6C4AB6"),  # $500 – purple
    (1000, "#D1B46A"),  # $1k – gold
]


def get_denom_color(amount: int) -> str:
    """Get the base color for a chip denomination."""
    for denom, color in CHIP_DENOMINATIONS:
        if amount <= denom:
            return color
    return CHIP_DENOMINATIONS[-1][1]  # Default to highest denom color


def draw_chip_base(canvas, x: int, y: int, r: int, face: str, edge: str, rim: str, 
                   denom_color: str, text: str, text_color: str, tags: tuple = ()) -> int:
    """
    Draw the base chip structure with radial stripes and denomination text.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        r: Chip radius
        face: Base face color
        edge: Outer edge color  
        rim: Inner ring color
        denom_color: Denomination stripe color
        text: Text to display (e.g., "$25")
        text_color: Text color
        tags: Canvas tags for the chip elements
        
    Returns:
        Canvas item ID of the main chip disc
    """
    # Main chip disc
    chip_id = canvas.create_oval(
        x - r, y - r, x + r, y + r,
        fill=face, outline=edge, width=2,
        tags=tags
    )
    
    # Radial stripes (8 wedges) for denomination recognition
    for i in range(8):
        angle_start = i * 45  # 360/8 = 45 degrees per stripe
        angle_extent = 15     # Width of each stripe
        canvas.create_arc(
            x - r + 3, y - r + 3, x + r - 3, y + r - 3,
            start=angle_start, extent=angle_extent,
            outline="", fill=denom_color, width=0,
            tags=tags
        )
    
    # Inner ring for premium look
    inner_r = int(r * 0.70)
    canvas.create_oval(
        x - inner_r, y - inner_r, x + inner_r, y + inner_r,
        outline=rim, fill="", width=2,
        tags=tags
    )
    
    # Denomination text
    font_size = max(8, int(r * 0.4))  # Scale text with chip size
    canvas.create_text(
        x, y, text=text, fill=text_color,
        font=("Inter", font_size, "bold"),
        tags=tags
    )
    
    return chip_id


def draw_stack_chip(canvas, x: int, y: int, amount: int, tokens: dict, 
                    r: int = 14, tags: tuple = ()) -> int:
    """
    Draw a single stack chip (calm, readable design for player stacks).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    return draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.stack.face", "#4A4A4A"),
        edge=tokens.get("chip.stack.edge", "#666666"), 
        rim=tokens.get("chip.stack.rim", "#888888"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.stack.text", "#F8F7F4"),
        tags=tags
    )


def draw_bet_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 14, hovering: bool = False, tags: tuple = ()) -> int:
    """
    Draw a bet/call chip (vivid design with theme accent for motion tracking).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        hovering: Whether to show hover glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.bet.face", "#6B4AB6"),
        edge=tokens.get("chip.bet.edge", "#8A6BC8"),
        rim=tokens.get("chip.bet.rim", "#A888CC"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.bet.text", "#F8F7F4"),
        tags=tags
    )
    
    # Optional hover glow
    if hovering:
        glow_color = tokens.get("chip.bet.glow", "#A888CC")
        canvas.create_oval(
            x - r - 4, y - r - 4, x + r + 4, y + r + 4,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_pot_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 16, breathing: bool = False, tags: tuple = ()) -> int:
    """
    Draw a pot chip (prestigious metal-leaning design).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates  
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius (slightly larger than other chips)
        breathing: Whether to show breathing glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.pot.face", "#D1B46A"),
        edge=tokens.get("chip.pot.edge", "#B8A157"),
        rim=tokens.get("chip.pot.rim", "#E6D078"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.pot.text", "#0B0B0E"),
        tags=tags
    )
    
    # Optional breathing glow for pot increases
    if breathing:
        glow_color = tokens.get("chip.pot.glow", "#E6D078")
        canvas.create_oval(
            x - r - 5, y - r - 5, x + r + 5, y + r + 5,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_chip_stack(canvas, x: int, y: int, total_amount: int, tokens: dict,
                    r: int = 14, max_height: int = 15, tags: tuple = ()) -> List[int]:
    """
    Draw a stack of chips representing a player's total amount.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Base center coordinates (bottom of stack)
        total_amount: Total dollar amount to represent
        tokens: Theme token dictionary
        r: Chip radius
        max_height: Maximum number of chips to show (for UI space)
        tags: Canvas tags
        
    Returns:
        List of canvas item IDs for all chips in the stack
    """
    if total_amount <= 0:
        return []
    
    # Break down amount into chip denominations (largest first)
    chip_plan = []
    remaining = total_amount
    
    for denom, _ in reversed(CHIP_DENOMINATIONS):
        if remaining >= denom:
            count = min(remaining // denom, max_height - len(chip_plan))
            chip_plan.extend([denom] * count)
            remaining -= denom * count
            
        if len(chip_plan) >= max_height:
            break
    
    # If we still have remaining amount and space, add smaller denominations
    if remaining > 0 and len(chip_plan) < max_height:
        # Fill remaining space with $1 chips
        remaining_space = max_height - len(chip_plan)
        chip_plan.extend([1] * min(remaining_space, remaining))
    
    # Draw soft shadow
    shadow_color = tokens.get("chip.stack.shadow", "#000000")
    canvas.create_oval(
        x - r - 4, y + 3, x + r + 4, y + 11,
        fill=shadow_color, outline="",
        tags=tags + ("shadow",)
    )
    
    # Draw chips from bottom to top
    chip_ids = []
    chip_spacing = 6  # Vertical spacing between chips
    
    for i, denom in enumerate(chip_plan):
        chip_y = y - (i * chip_spacing)
        chip_id = draw_stack_chip(
            canvas, x, chip_y, denom, tokens, r=r,
            tags=tags + (f"stack_chip_{i}",)
        )
        chip_ids.append(chip_id)
    
    return chip_ids


def animate_chip_bet(canvas, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                     amount: int, tokens: dict, r: int = 14, frames: int = 20,
                     callback: Optional[callable] = None) -> None:
    """
    Animate a chip flying from start to end position (bet → pot).
    
    Args:
        canvas: Tkinter canvas widget
        start_pos: (x, y) starting coordinates
        end_pos: (x, y) ending coordinates
        amount: Dollar amount for the chip
        tokens: Theme token dictionary
        r: Chip radius
        frames: Number of animation frames
        callback: Optional function to call when animation completes
    """
    x0, y0 = start_pos
    x1, y1 = end_pos
    glow_color = tokens.get("chip.bet.glow", "#A888CC")
    
    def animate_frame(frame: int):
        if frame >= frames:
            if callback:
                callback()
            return
        
        # Cubic easing for smooth motion
        t = frame / frames
        ease_t = t * t * (3 - 2 * t)
        
        # Position with arc (parabolic path)
        x = x0 + (x1 - x0) * ease_t
        y = y0 + (y1 - y0) * ease_t - 20 * math.sin(math.pi * ease_t)
        
        # Clear previous frame
        canvas.delete("flying_chip")
        
        # Draw chip at current position
        draw_bet_chip(
            canvas, int(x), int(y), amount, tokens, r=r, hovering=True,
            tags=("flying_chip",)
        )
        
        # Schedule next frame
        canvas.after(50, lambda: animate_frame(frame + 1))
    
    # Start animation
    animate_frame(0)


def pulse_pot_glow(canvas, center_pos: Tuple[int, int], tokens: dict,
                   r: int = 18, pulses: int = 3) -> None:
    """
    Create a pulsing glow effect at the pot center when pot increases.
    
    Args:
        canvas: Tkinter canvas widget
        center_pos: (x, y) center coordinates
        tokens: Theme token dictionary
        r: Base radius for the pulse
        pulses: Number of pulse cycles
    """
    x, y = center_pos
    glow_color = tokens.get("chip.pot.glow", "#E6D078")
    
    pulse_sequence = [0.0, 0.4, 0.8, 1.0, 0.8, 0.4, 0.0]
    
    def animate_pulse(pulse_num: int, frame: int):
        if pulse_num >= pulses:
            canvas.delete("pot_pulse")
            return
            
        if frame >= len(pulse_sequence):
            # Move to next pulse
            canvas.after(100, lambda: animate_pulse(pulse_num + 1, 0))
            return
        
        # Clear previous pulse
        canvas.delete("pot_pulse")
        
        # Draw current pulse ring
        intensity = pulse_sequence[frame]
        pulse_r = r + int(8 * intensity)
        alpha_val = int(255 * (0.6 - 0.4 * intensity))  # Fade as it expands
        
        canvas.create_oval(
            x - pulse_r, y - pulse_r, x + pulse_r, y + pulse_r,
            outline=glow_color, fill="", width=max(1, int(3 * (1 - intensity))),
            tags=("pot_pulse",)
        )
        
        # Schedule next frame
        canvas.after(80, lambda: animate_pulse(pulse_num, frame + 1))
    
    # Start pulsing
    animate_pulse(0, 0)


def clear_chip_animations(canvas) -> None:
    """Clear all chip animation elements from the canvas."""
    canvas.delete("flying_chip")
    canvas.delete("pot_pulse")
    canvas.delete("glow")
