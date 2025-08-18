"""
Luxury Themed Chip Graphics System
Renders poker chips with theme-aware styling for bets, calls, and pot displays.
"""
import math
import tkinter as tk
from typing import Dict, List, Tuple, Optional
from ...services.theme_manager import ThemeManager


def _tokens(canvas):
    """Get theme tokens and fonts from widget tree."""
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return ({"chip.primary": "#DAA520", "chip.secondary": "#8B4513"}, {"body": ("Arial", 10, "bold")})


class ChipGraphics:
    """Renders luxury themed poker chips with animations."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_stacks = {}  # Track chip positions for animations
        self.animation_queue = []  # Queue for chip animations
        
    def get_chip_colors_for_value(self, value: int, theme: Dict) -> Tuple[str, str, str]:
        """Get themed chip colors based on value."""
        # Standard poker chip color scheme with theme variations
        if value >= 1000:
            # High value - use theme's luxury colors
            return (
                theme.get("chip.luxury.bg", "#2D1B69"),      # Deep purple/navy
                theme.get("chip.luxury.ring", "#FFD700"),    # Gold ring
                theme.get("chip.luxury.accent", "#E6E6FA")   # Light accent
            )
        elif value >= 500:
            # Medium-high value - theme primary colors
            return (
                theme.get("chip.high.bg", "#8B0000"),        # Deep red
                theme.get("chip.high.ring", "#FFD700"),      # Gold ring
                theme.get("chip.high.accent", "#FFFFFF")     # White accent
            )
        elif value >= 100:
            # Medium value - theme secondary colors
            return (
                theme.get("chip.medium.bg", "#006400"),      # Forest green
                theme.get("chip.medium.ring", "#FFFFFF"),    # White ring
                theme.get("chip.medium.accent", "#90EE90")   # Light green accent
            )
        elif value >= 25:
            # Low-medium value
            return (
                theme.get("chip.low.bg", "#4169E1"),         # Royal blue
                theme.get("chip.low.ring", "#FFFFFF"),       # White ring
                theme.get("chip.low.accent", "#ADD8E6")      # Light blue accent
            )
        else:
            # Lowest value - theme accent colors
            return (
                theme.get("chip.minimal.bg", "#FFFFFF"),     # White
                theme.get("chip.minimal.ring", "#000000"),   # Black ring
                theme.get("chip.minimal.accent", "#D3D3D3")  # Light gray accent
            )
    
    def render_chip(self, x: int, y: int, value: int, chip_type: str = "bet", 
                   size: int = 20, tags: Tuple = ()) -> List[int]:
        """Render a single luxury themed chip."""
        theme, fonts = _tokens(self.canvas)
        
        # Get themed colors for this chip value
        bg_color, ring_color, accent_color = self.get_chip_colors_for_value(value, theme)
        
        # Adjust colors based on chip type
        if chip_type == "pot":
            # Pot chips get special treatment with theme's pot colors
            bg_color = theme.get("pot.chipBg", bg_color)
            ring_color = theme.get("pot.badgeRing", ring_color)
        elif chip_type == "call":
            # Call chips get muted colors
            bg_color = theme.get("chip.call.bg", "#6B7280")
            ring_color = theme.get("chip.call.ring", "#9CA3AF")
        
        elements = []
        
        # Main chip body with luxury gradient effect
        chip_id = self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=bg_color,
            outline=ring_color,
            width=3,
            tags=tags + ("chip", f"chip_{chip_type}")
        )
        elements.append(chip_id)
        
        # Inner highlight for 3D effect
        highlight_size = size - 4
        highlight_id = self.canvas.create_oval(
            x - highlight_size, y - highlight_size + 2,
            x + highlight_size, y - highlight_size + 8,
            fill=accent_color,
            outline="",
            tags=tags + ("chip_highlight",)
        )
        elements.append(highlight_id)
        
        # Luxury center pattern based on theme
        pattern_color = theme.get("chip.pattern", ring_color)
        
        # Theme-specific chip patterns
        theme_name = theme.get("_theme_name", "default")
        if "monet" in theme_name.lower():
            # Impressionist water lily pattern
            for angle in [0, 60, 120, 180, 240, 300]:
                rad = math.radians(angle)
                px = x + (size // 3) * math.cos(rad)
                py = y + (size // 3) * math.sin(rad)
                dot_id = self.canvas.create_oval(
                    px - 2, py - 2, px + 2, py + 2,
                    fill=pattern_color, outline="",
                    tags=tags + ("chip_pattern",)
                )
                elements.append(dot_id)
                
        elif "caravaggio" in theme_name.lower():
            # Baroque cross pattern
            cross_size = size // 2
            # Vertical line
            line1_id = self.canvas.create_line(
                x, y - cross_size, x, y + cross_size,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line1_id)
            # Horizontal line
            line2_id = self.canvas.create_line(
                x - cross_size, y, x + cross_size, y,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line2_id)
            
        elif "klimt" in theme_name.lower():
            # Art Nouveau geometric pattern
            square_size = size // 3
            square_id = self.canvas.create_rectangle(
                x - square_size, y - square_size,
                x + square_size, y + square_size,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(square_id)
            
        else:
            # Default diamond pattern
            diamond_size = size // 2
            diamond_points = [
                x, y - diamond_size,  # Top
                x + diamond_size, y,  # Right
                x, y + diamond_size,  # Bottom
                x - diamond_size, y   # Left
            ]
            diamond_id = self.canvas.create_polygon(
                diamond_points,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(diamond_id)
        
        # Value text (for larger chips)
        if size >= 15 and value >= 5:
            font_size = max(8, size // 3)
            text_font = (fonts.get("body", ("Arial", 10))[0], font_size, "bold")
            
            # Format value display
            if value >= 1000:
                display_value = f"{value//1000}K"
            else:
                display_value = str(value)
            
            text_id = self.canvas.create_text(
                x, y + size // 4,
                text=display_value,
                font=text_font,
                fill=theme.get("chip.text", "#FFFFFF"),
                tags=tags + ("chip_text",)
            )
            elements.append(text_id)
        
        return elements
    
    def render_chip_stack(self, x: int, y: int, total_value: int, 
                         chip_type: str = "bet", max_chips: int = 5,
                         tags: Tuple = ()) -> List[int]:
        """Render a stack of chips representing a total value."""
        theme, _ = _tokens(self.canvas)
        
        # Calculate chip denominations for the stack
        chip_values = self._calculate_chip_breakdown(total_value, max_chips)
        
        elements = []
        stack_height = 0
        
        for i, (value, count) in enumerate(chip_values):
            for j in range(count):
                # Stack chips with slight offset for 3D effect
                chip_x = x + j
                chip_y = y - stack_height - (j * 2)
                
                # Render individual chip
                chip_elements = self.render_chip(
                    chip_x, chip_y, value, chip_type,
                    size=18, tags=tags + (f"stack_{i}_{j}",)
                )
                elements.extend(chip_elements)
                
            stack_height += count * 3  # Increase stack height
        
        return elements
    
    def _calculate_chip_breakdown(self, total_value: int, max_chips: int) -> List[Tuple[int, int]]:
        """Calculate optimal chip breakdown for a given value."""
        denominations = [1000, 500, 100, 25, 5, 1]
        breakdown = []
        remaining = total_value
        chips_used = 0
        
        for denom in denominations:
            if chips_used >= max_chips:
                break
                
            if remaining >= denom:
                count = min(remaining // denom, max_chips - chips_used)
                if count > 0:
                    breakdown.append((denom, count))
                    remaining -= denom * count
                    chips_used += count
        
        # If we still have remaining value and room for chips, add smaller denominations
        if remaining > 0 and chips_used < max_chips:
            breakdown.append((remaining, 1))
        
        return breakdown
    
    def animate_chips_to_pot(self, start_x: int, start_y: int, 
                           end_x: int, end_y: int, chip_value: int,
                           duration: int = 500, callback=None):
        """Animate chips moving from player position to pot."""
        theme, _ = _tokens(self.canvas)
        
        # Create temporary chips for animation
        temp_chips = self.render_chip_stack(
            start_x, start_y, chip_value, "bet",
            tags=("animation", "temp_chip")
        )
        
        # Animation parameters
        steps = 20
        step_duration = duration // steps
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete - remove temp chips and call callback
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Move chips
            for chip_id in temp_chips:
                try:
                    self.canvas.move(chip_id, dx, dy)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def animate_pot_to_winner(self, pot_x: int, pot_y: int,
                            winner_x: int, winner_y: int, pot_value: int,
                            duration: int = 800, callback=None):
        """Animate pot chips moving to winner."""
        theme, _ = _tokens(self.canvas)
        
        # Create celebration effect
        self._create_winner_celebration(winner_x, winner_y, pot_value)
        
        # Create pot chips for animation
        temp_chips = self.render_chip_stack(
            pot_x, pot_y, pot_value, "pot",
            max_chips=8, tags=("animation", "pot_to_winner")
        )
        
        # Animation with arc trajectory
        steps = 25
        step_duration = duration // steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Calculate arc position
            progress = step / steps
            # Parabolic arc
            arc_height = -50 * math.sin(math.pi * progress)
            
            current_x = pot_x + (winner_x - pot_x) * progress
            current_y = pot_y + (winner_y - pot_y) * progress + arc_height
            
            # Move chips to calculated position
            for i, chip_id in enumerate(temp_chips):
                try:
                    # Get current position
                    coords = self.canvas.coords(chip_id)
                    if len(coords) >= 4:
                        old_x = (coords[0] + coords[2]) / 2
                        old_y = (coords[1] + coords[3]) / 2
                        
                        # Calculate new position with slight spread
                        spread = i * 3
                        new_x = current_x + spread
                        new_y = current_y
                        
                        # Move chip
                        self.canvas.move(chip_id, new_x - old_x, new_y - old_y)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def _create_winner_celebration(self, x: int, y: int, pot_value: int):
        """Create celebration effect around winner."""
        theme, fonts = _tokens(self.canvas)
        
        # Celebration burst effect
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            distance = 30
            star_x = x + distance * math.cos(angle)
            star_y = y + distance * math.sin(angle)
            
            # Create star burst
            star_id = self.canvas.create_text(
                star_x, star_y,
                text="✨",
                font=("Arial", 16),
                fill=theme.get("celebration.color", "#FFD700"),
                tags=("celebration", "temp")
            )
            
            # Fade out after delay
            self.canvas.after(1000, lambda sid=star_id: self._fade_element(sid))
    
    def _fade_element(self, element_id: int):
        """Fade out and remove an element."""
        try:
            self.canvas.delete(element_id)
        except tk.TclError:
            pass


class BetDisplay:
    """Renders themed bet amounts with chip graphics."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_graphics = ChipGraphics(canvas)
    
    def render(self, x: int, y: int, amount: int, bet_type: str = "bet",
               tags: Tuple = ()) -> List[int]:
        """Render bet display with chips and text."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        if amount > 0:
            # Render chip stack
            chip_elements = self.chip_graphics.render_chip_stack(
                x, y - 15, amount, bet_type, max_chips=3,
                tags=tags + ("bet_chips",)
            )
            elements.extend(chip_elements)
            
            # Render amount text
            text_color = theme.get("bet.text", "#FFFFFF")
            if bet_type == "call":
                text_color = theme.get("bet.call.text", "#9CA3AF")
            elif bet_type == "raise":
                text_color = theme.get("bet.raise.text", "#EF4444")
            
            text_id = self.canvas.create_text(
                x, y + 20,
                text=f"${amount:,}",
                font=fonts.get("body", ("Arial", 10, "bold")),
                fill=text_color,
                tags=tags + ("bet_text",)
            )
            elements.append(text_id)
        
        return elements


class WinnerBadge:
    """Renders themed winner announcement badges."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def render(self, x: int, y: int, player_name: str, amount: int,
               hand_description: str = "", tags: Tuple = ()) -> List[int]:
        """Render luxury winner badge with theme styling."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        # Badge dimensions
        badge_width = 200
        badge_height = 80
        
        # Theme-aware colors
        badge_bg = theme.get("winner.bg", "#1F2937")
        badge_border = theme.get("winner.border", "#FFD700")
        badge_accent = theme.get("winner.accent", "#FEF3C7")
        
        # Main badge background with luxury styling
        badge_id = self.canvas.create_rectangle(
            x - badge_width//2, y - badge_height//2,
            x + badge_width//2, y + badge_height//2,
            fill=badge_bg,
            outline=badge_border,
            width=3,
            tags=tags + ("winner_badge",)
        )
        elements.append(badge_id)
        
        # Luxury gradient highlight
        highlight_id = self.canvas.create_rectangle(
            x - badge_width//2 + 3, y - badge_height//2 + 3,
            x + badge_width//2 - 3, y - badge_height//2 + 12,
            fill=badge_accent,
            outline="",
            tags=tags + ("winner_highlight",)
        )
        elements.append(highlight_id)
        
        # Winner crown symbol
        crown_id = self.canvas.create_text(
            x - badge_width//3, y - 10,
            text="👑",
            font=("Arial", 20),
            tags=tags + ("winner_crown",)
        )
        elements.append(crown_id)
        
        # Winner text
        winner_text = f"WINNER: {player_name}"
        text_id = self.canvas.create_text(
            x, y - 15,
            text=winner_text,
            font=fonts.get("heading", ("Arial", 12, "bold")),
            fill=theme.get("winner.text", "#FFFFFF"),
            tags=tags + ("winner_text",)
        )
        elements.append(text_id)
        
        # Amount won
        amount_id = self.canvas.create_text(
            x, y + 5,
            text=f"${amount:,}",
            font=fonts.get("body", ("Arial", 14, "bold")),
            fill=theme.get("winner.amount", "#FFD700"),
            tags=tags + ("winner_amount",)
        )
        elements.append(amount_id)
        
        # Hand description (if provided)
        if hand_description:
            hand_id = self.canvas.create_text(
                x, y + 20,
                text=hand_description,
                font=fonts.get("caption", ("Arial", 9, "italic")),
                fill=theme.get("winner.description", "#D1D5DB"),
                tags=tags + ("winner_hand",)
            )
            elements.append(hand_id)
        
        return elements
    
    def animate_winner_announcement(self, x: int, y: int, player_name: str,
                                  amount: int, hand_description: str = "",
                                  duration: int = 3000):
        """Animate winner badge with entrance and exit effects."""
        # Create badge elements
        elements = self.render(x, y, player_name, amount, hand_description,
                             tags=("winner_animation",))
        
        # Entrance animation - scale up
        self._animate_scale(elements, 0.1, 1.0, 300)
        
        # Exit animation after duration
        self.canvas.after(duration, lambda: self._animate_fade_out(elements, 500))
    
    def _animate_scale(self, elements: List[int], start_scale: float,
                      end_scale: float, duration: int):
        """Animate scaling of elements."""
        steps = 15
        step_duration = duration // steps
        scale_step = (end_scale - start_scale) / steps
        
        def scale_step_func(step: int):
            if step >= steps:
                return
            
            current_scale = start_scale + scale_step * step
            
            for element_id in elements:
                try:
                    # Get element center
                    coords = self.canvas.coords(element_id)
                    if len(coords) >= 2:
                        if len(coords) == 4:  # Rectangle
                            center_x = (coords[0] + coords[2]) / 2
                            center_y = (coords[1] + coords[3]) / 2
                        else:  # Text or other
                            center_x, center_y = coords[0], coords[1]
                        
                        # Apply scaling (simplified - just adjust position)
                        # In a full implementation, you'd use canvas.scale()
                        pass
                except tk.TclError:
                    pass
            
            self.canvas.after(step_duration, lambda: scale_step_func(step + 1))
        
        scale_step_func(0)
    
    def _animate_fade_out(self, elements: List[int], duration: int):
        """Fade out and remove elements."""
        # Simplified fade - just remove after duration
        self.canvas.after(duration, lambda: self._remove_elements(elements))
    
    def _remove_elements(self, elements: List[int]):
        """Remove elements from canvas."""
        for element_id in elements:
            try:
                self.canvas.delete(element_id)
            except tk.TclError:
                pass
