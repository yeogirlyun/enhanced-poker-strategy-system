"""
Hand Progress Indicator - Shows current street and progress through the hand
"""
from ...services.theme_manager import ThemeManager


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
        {
            "progress.bg": "#1F2937",
            "progress.border": "#374151", 
            "progress.active": "#10B981",
            "progress.completed": "#6B7280",
            "progress.text": "#E5E7EB"
        }, 
        {"font.body": ("Arial", 10, "bold")}
    )


class HandProgress:
    def __init__(self):
        self._progress_elements = {}
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Clear previous elements
        for element_id in self._progress_elements.values():
            try:
                c.delete(element_id)
            except Exception:
                pass
        self._progress_elements = {}
        
        # Get current street from state
        current_street = state.get("street", "preflop").lower()
        streets = ["preflop", "flop", "turn", "river"]
        
        # Position at top of table
        start_x = w // 2 - 100
        start_y = int(h * 0.08)
        
        # Street progress indicators
        street_width = 50
        street_spacing = 10
        
        for i, street in enumerate(streets):
            x = start_x + i * (street_width + street_spacing)
            
            # Determine status
            current_index = streets.index(current_street) if current_street in streets else 0
            is_completed = i < current_index
            is_current = i == current_index
            
            # Street background
            if is_current:
                bg_color = THEME.get("progress.active", "#10B981")
            elif is_completed:
                bg_color = THEME.get("progress.completed", "#6B7280")
            else:
                bg_color = THEME.get("progress.bg", "#1F2937")
            
            self._progress_elements[f'street_bg_{i}'] = c.create_rectangle(
                x, start_y,
                x + street_width, start_y + 20,
                fill=bg_color,
                outline=THEME.get("progress.border", "#374151"),
                width=1,
                tags=("layer:progress", f"street_bg:{i}"),
            )
            
            # Street text
            text_color = "#FFFFFF" if (is_current or is_completed) else THEME.get("progress.text", "#E5E7EB")
            self._progress_elements[f'street_text_{i}'] = c.create_text(
                x + street_width//2,
                start_y + 10,
                text=street.title(),
                font=FONTS.get("font.body", ("Arial", 9, "bold")),
                fill=text_color,
                tags=("layer:progress", f"street_text:{i}"),
            )
        
        # Add street labels
        self._progress_elements['progress_label'] = c.create_text(
            start_x - 20,
            start_y + 10,
            text="Street:",
            font=FONTS.get("font.body", ("Arial", 10, "normal")),
            fill=THEME.get("progress.text", "#E5E7EB"),
            anchor="e",
            tags=("layer:progress", "progress_label"),
        )
        
        # Tag all elements
        for element_id in self._progress_elements.values():
            c.addtag_withtag("layer:progress", element_id)
