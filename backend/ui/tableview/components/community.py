from ...state.selectors import get_board_positions
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
        {"board.slotBg": "#133C2E", "board.cardFaceFg": "#111317"}, 
        {"font.body": ("Arial", 14, "bold")}
    )


class Community:
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        positions = get_board_positions(state)
        card_w = int(min(w, h) * 0.07)
        card_h = int(card_w * 1.4)
        for idx, (x, y) in enumerate(positions):
            c.create_rectangle(
                x - card_w // 2,
                y - card_h // 2,
                x + card_w // 2,
                y + card_h // 2,
                fill=THEME.get("board.slotBg", "#133C2E"),
                outline="",
                tags=("layer:community", f"board:{idx}"),
            )
            # Placeholder rank/suit
            c.create_text(
                x,
                y,
                text="🂠",
                font=FONTS.get("font.body", FONTS.get("main", ("Arial", 14, "bold"))),
                fill=THEME.get("board.cardFaceFg", "#111317"),
                tags=("layer:community", f"board_label:{idx}"),
            )

