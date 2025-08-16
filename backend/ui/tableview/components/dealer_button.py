from ...state.selectors import (
    get_seat_positions,
    get_dealer_position,
    get_num_seats,
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
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        count = get_num_seats(state)
        positions = get_seat_positions(state, seat_count=count)
        if not positions:
            return
        idx = get_dealer_position(state) % len(positions)
        x, y = positions[idx]
        r = int(min(w, h) * 0.018)
        c.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            fill=THEME.get("dealer.buttonBg", "#FDE68A"),
            outline="",
            tags=("layer:seats", "dealer_button"),
        )
        c.create_text(
            x,
            y,
            text="D",
            font=FONTS.get("font.body", ("Arial", 12, "bold")),
            fill=THEME.get("dealer.buttonFg", "#0B1220"),
            tags=("layer:seats", "dealer_button_label"),
        )


