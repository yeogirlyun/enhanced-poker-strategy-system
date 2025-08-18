from ...services.theme_manager import ThemeManager
from .chip_graphics import ChipGraphics


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
        
        # Render pot chips if amount > 0
        if amount > 0:
            # Render chip stack around the pot display
            chip_positions = [
                (center_x - 30, center_y + 30),  # Left
                (center_x + 30, center_y + 30),  # Right
                (center_x, center_y + 35),       # Center bottom
            ]
            
            # Distribute chips across positions
            chips_per_position = max(1, amount // 300)  # Rough distribution
            for i, (chip_x, chip_y) in enumerate(chip_positions):
                if i < len(chip_positions):
                    chip_value = min(amount // len(chip_positions), 500)
                    if chip_value > 0:
                        pot_chip_elements = self._chip_graphics.render_chip_stack(
                            chip_x, chip_y, chip_value, "pot",
                            max_chips=3, tags=("layer:pot", "pot_chips")
                        )
                        self._pot_chips.extend(pot_chip_elements)
        
        # Ensure proper layering
        c.addtag_withtag("layer:pot", self._pot_bg_id or "")
        c.addtag_withtag("layer:pot", self._pot_label_id or "")
        c.addtag_withtag("layer:pot", self._pot_text_id or "")
        for chip_id in self._pot_chips:
            c.addtag_withtag("layer:pot", chip_id)


