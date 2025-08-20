from ...services.theme_manager import ThemeManager
from .chip_graphics import ChipGraphics

try:
    from .premium_chips import draw_pot_chip, pulse_pot_glow
except Exception:
    def draw_pot_chip(canvas, x, y, theme, fonts, scale=1.0, tags=()):
        r = int(10*scale)
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=theme.get("chip.gold","#D97706"), outline="black", width=1, tags=tags)
    def pulse_pot_glow(canvas, pot_bg_id, theme):
        # simple glow by toggling outline width
        try:
            w = int(canvas.itemcget(pot_bg_id, "width") or 2)
            canvas.itemconfig(pot_bg_id, width=(w%4)+1)
        except Exception:
            pass


def _tokens(canvas):
    # Prefer ThemeManager from widget tree
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")  # type: ignore[attr-defined]
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return (
        {"pot.valueText": "#F8FAFC", "chip_gold": "#FFD700"}, 
        {"font.display": ("Arial", 28, "bold")}
    )


class PotDisplay:
    def __init__(self) -> None:
        self._pot_bg_id = None
        self._pot_text_id = None
        self._pot_label_id = None
        self._chip_graphics = None
        self._pot_chips = []  # Track pot chip elements

    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Initialize chip graphics if needed
        if self._chip_graphics is None:
            self._chip_graphics = ChipGraphics(c)
        
        center_x, center_y = w // 2, int(h * 0.58)
        
        # Get pot amount from state - handle both formats
        pot_data = state.get("pot", {})
        if isinstance(pot_data, dict):
            amount = int(pot_data.get("amount", 0))
        else:
            amount = int(pot_data or 0)
        
        text_value = f"${amount:,}" if amount > 0 else "$0"

        # Use theme tokens (prefer badge keys; fall back to legacy)
        text_fill = THEME.get("pot.valueText", THEME.get("text.primary", "#F6EFDD"))
        bg_fill = (THEME.get("pot.badgeBg") or
                   THEME.get("pot.bg") or "#15212B")
        border_color = (THEME.get("pot.badgeRing") or
                        THEME.get("pot.border") or "#C9B47A")
        font = FONTS.get("font.display", ("Arial", 24, "bold"))
        label_font = FONTS.get("font.body", ("Arial", 12, "normal"))

        # Pot background (rounded rectangle)
        bg_width, bg_height = 120, 50
        if not self._pot_bg_id:
            self._pot_bg_id = c.create_rectangle(
                center_x - bg_width//2,
                center_y - bg_height//2,
                center_x + bg_width//2,
                center_y + bg_height//2,
                fill=bg_fill,
                outline=border_color,
                width=2,
                tags=("layer:pot", "pot_bg"),
            )
        else:
            # Update background position and colors
            c.coords(
                self._pot_bg_id,
                center_x - bg_width//2,
                center_y - bg_height//2,
                center_x + bg_width//2,
                center_y + bg_height//2
            )
            c.itemconfig(self._pot_bg_id, fill=bg_fill, outline=border_color)

        # Pot label ("POT")
        if not self._pot_label_id:
            self._pot_label_id = c.create_text(
                center_x,
                center_y - 15,
                text="POT",
                font=label_font,
                fill=THEME.get("pot.label", "#9CA3AF"),
                tags=("layer:pot", "pot_label"),
            )
        else:
            c.coords(self._pot_label_id, center_x, center_y - 15)
            c.itemconfig(self._pot_label_id, fill=THEME.get("pot.label", "#9CA3AF"))

        # Pot amount
        if not self._pot_text_id:
            self._pot_text_id = c.create_text(
                center_x,
                center_y + 5,
                text=text_value,
                font=font,
                fill=text_fill,
                tags=("layer:pot", "pot_text"),
            )
        else:
            c.coords(self._pot_text_id, center_x, center_y + 5)
            c.itemconfig(self._pot_text_id, text=text_value, fill=text_fill, font=font)
            
        # Clear old pot chips
        for chip_id in self._pot_chips:
            try:
                c.delete(chip_id)
            except Exception:
                pass
        self._pot_chips = []
        
        # Render premium pot chips if amount > 0
        if amount > 0:
            self._render_premium_pot_chips(c, center_x, center_y, amount, THEME)
        
        # Ensure proper layering
        c.addtag_withtag("layer:pot", self._pot_bg_id or "")
        c.addtag_withtag("layer:pot", self._pot_label_id or "")
        c.addtag_withtag("layer:pot", self._pot_text_id or "")
        for chip_id in self._pot_chips:
            c.addtag_withtag("layer:pot", chip_id)

    def _render_premium_pot_chips(self, canvas, center_x: int, center_y: int, 
                                  amount: int, tokens: dict) -> None:
        """Render premium pot chips in an elegant arrangement around the pot."""
        if amount <= 0:
            return
        
        # Elegant chip arrangement around the pot badge
        chip_positions = [
            (center_x - 35, center_y + 25),   # Left
            (center_x + 35, center_y + 25),   # Right  
            (center_x - 20, center_y + 40),   # Left-center
            (center_x + 20, center_y + 40),   # Right-center
            (center_x, center_y + 45),        # Center bottom
        ]
        
        # Determine number of chip positions based on pot size
        if amount < 100:
            positions = chip_positions[:1]  # Just center
        elif amount < 500:
            positions = chip_positions[:3]  # Left, right, center
        else:
            positions = chip_positions  # All positions for big pots
        
        # Draw premium pot chips at each position
        chip_r = 12  # Slightly smaller for elegant clustering
        for i, (chip_x, chip_y) in enumerate(positions):
            # Vary chip values for visual interest
            if i == 0:  # Center/first chip gets highest value
                chip_value = min(amount // 2, 1000)
            else:
                chip_value = min(amount // len(positions), 500)
            
            if chip_value > 0:
                # Add subtle breathing effect for large pots
                breathing = amount > 1000
                chip_id = draw_pot_chip(
                    canvas, chip_x, chip_y, chip_value, tokens,
                    r=chip_r, breathing=breathing,
                    tags=("layer:pot", "pot_chips", f"pot_chip_{i}")
                )
                self._pot_chips.append(chip_id)

    def pulse_pot_increase(self, center_pos: tuple) -> None:
        """Trigger a pulsing glow effect when the pot increases."""
        # Get theme tokens for glow effect
        THEME, _ = _tokens(self._canvas if hasattr(self, '_canvas') else None)
        if THEME:
            pulse_pot_glow(self._canvas, center_pos, THEME, r=20, pulses=2)


