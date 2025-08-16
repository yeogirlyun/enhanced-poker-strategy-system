from ...state.selectors import get_seat_positions, get_num_seats
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
    return ({"text": "#E6E9EF", "seat_bg": "#23262B"}, {"main": ("Arial", 12, "bold")})


class Seats:
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        count = get_num_seats(state)
        positions = get_seat_positions(state, seat_count=count)
        for idx, (x, y) in enumerate(positions):
            r = int(min(w, h) * 0.035)
            c.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=THEME.get("seat.bg.idle", "#0F172A"),
                outline="",
                tags=("layer:seats", f"seat:{idx}"),
            )
            c.create_text(
                x,
                y,
                text=str(idx + 1),
                font=FONTS.get("font.body", FONTS.get("main", ("Arial", 12, "bold"))),
                fill=THEME.get("player.name", "#E2E8F0"),
                tags=("layer:seats", f"seat_label:{idx}"),
            )

