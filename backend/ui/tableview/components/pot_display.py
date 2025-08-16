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
        {"pot.valueText": "#F8FAFC", "chip_gold": "#FFD700"}, 
        {"font.display": ("Arial", 28, "bold")}
    )


class PotDisplay:
    def __init__(self) -> None:
        self._fallback_text_id = None

    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        center_x, center_y = w // 2, int(h * 0.58)
        amount = int(state.get("pot", {}).get("amount", 0))
        text_value = f"${amount:,}"

        # Use theme tokens
        fill = THEME.get("pot.valueText", THEME.get("chip_gold", "#F8FAFC"))
        font = FONTS.get("font.display", ("Arial", 28, "bold"))

        if not self._fallback_text_id:
            self._fallback_text_id = c.create_text(
                center_x,
                center_y,
                text=text_value,
                font=font,
                fill=fill,
                tags=("layer:pot", "pot_text"),
            )
        else:
            c.itemconfigure(
                self._fallback_text_id, text=text_value, fill=fill, font=font
            )
            # Reposition on resize
            try:
                c.coords(self._fallback_text_id, center_x, center_y)
            except Exception:
                pass
            c.addtag_withtag("layer:pot", self._fallback_text_id)


