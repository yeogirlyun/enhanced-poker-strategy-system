from ...state.selectors import (
    get_seat_positions,
    get_dealer_position,
)
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
        {"dealer.buttonBg": "#FDE68A", "dealer.buttonFg": "#0B1220"}, 
        {"font.body": ("Arial", 12, "bold")}
    )


class DealerButton:
    def __init__(self):
        self._button_id = None
        self._text_id = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Get seat count from state - use direct seats array if available
        seats_data = state.get('seats', [])
        count = len(seats_data) if seats_data else 6  # Default to 6 seats
            
        dealer_pos = get_dealer_position(state)
        
        # Use consistent seat positions from geometry helper  
        positions = get_seat_positions(
            state, seat_count=count, 
            canvas_width=w, canvas_height=h
        )
        
        print(f"🏷️ DealerButton on {w}x{h}: {count} seats, "
              f"dealer pos: {dealer_pos}")
            
        if dealer_pos < 0 or dealer_pos >= len(positions):
            print(f"🏷️ Invalid dealer position {dealer_pos}, using 0")
            dealer_pos = 0
            
        seat_x, seat_y = positions[dealer_pos]
        
        # Position dealer button outside the seat, towards table center
        center_x, center_y = w // 2, int(h * 0.52)
        
        # Calculate direction from seat to center
        dx = center_x - seat_x
        dy = center_y - seat_y
        distance = (dx*dx + dy*dy) ** 0.5
        
        if distance > 0:
            # Normalize and position button closer to table center
            offset = 25  # Distance from seat center
            button_x = seat_x + (dx / distance) * offset
            button_y = seat_y + (dy / distance) * offset
        else:
            button_x, button_y = seat_x + 25, seat_y
        
        # Make dealer button more prominent
        button_radius = int(min(w, h) * 0.025)  # Larger button
        
        # Dealer button background with border
        if not self._button_id:
            self._button_id = c.create_oval(
                button_x - button_radius,
                button_y - button_radius,
                button_x + button_radius,
                button_y + button_radius,
                fill=THEME.get("dealer.buttonBg", "#FDE68A"),
                outline=THEME.get("dealer.buttonBorder", "#D97706"),
                width=2,
                tags=("layer:seats", "dealer_button"),
            )
        else:
            c.coords(
                self._button_id,
                button_x - button_radius,
                button_y - button_radius,
                button_x + button_radius,
                button_y + button_radius
            )
            c.itemconfig(
                self._button_id,
                fill=THEME.get("dealer.buttonBg", "#FDE68A"),
                outline=THEME.get("dealer.buttonBorder", "#D97706")
            )
        
        # Dealer button text
        if not self._text_id:
            self._text_id = c.create_text(
                button_x,
                button_y,
                text="D",
                font=FONTS.get("font.body", ("Arial", 14, "bold")),
                fill=THEME.get("dealer.buttonFg", "#0B1220"),
                tags=("layer:seats", "dealer_button_label"),
            )
        else:
            c.coords(self._text_id, button_x, button_y)
            c.itemconfig(
                self._text_id,
                fill=THEME.get("dealer.buttonFg", "#0B1220")
            )
        
        # Ensure proper layering
        c.addtag_withtag("layer:seats", self._button_id or "")
        c.addtag_withtag("layer:seats", self._text_id or "")


