from ...services.theme_manager import ThemeManager


class TableFelt:
    def render(self, state, canvas_manager, layer_manager) -> None:
        # Persisted theme via ThemeManager
        # Note: We locate the theme service via the parent Frame stored on canvas
        # Find ThemeManager by walking up the widget tree
        theme_service = None
        w = canvas_manager.canvas
        while w is not None and theme_service is None:
            try:
                if hasattr(w, "services"):
                    theme_service = w.services.get_app("theme")  # type: ignore[attr-defined]
                    break
            except Exception:
                pass
            w = getattr(w, "master", None)
        if isinstance(theme_service, ThemeManager):
            THEME = theme_service.get_theme()
        else:
            THEME = {"table.felt": "#2B2F36", "table_rail": None}
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        # Base felt rectangle
        c.create_rectangle(
            0,
            0,
            w,
            h,
            fill=THEME.get("table.felt", THEME.get("table_felt", "#2B2F36")),
            outline="",
            tags=("layer:felt", "felt"),
        )
        # Optional subtle rail border
        rail = THEME.get("table.rail", THEME.get("table_rail"))
        if rail:
            c.create_rectangle(
                6,
                6,
                w - 6,
                h - 6,
                outline=rail,
                width=2,
                tags=("layer:felt", "felt_rail"),
            )

