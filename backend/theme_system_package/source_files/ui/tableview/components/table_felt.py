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
        
        # Use fallback size if canvas not ready
        if w <= 1 or h <= 1:
            w, h = 800, 600
            
        felt_color = THEME.get("table.felt", THEME.get("table_felt", "#1B4D3A"))
        rail_color = THEME.get("table.rail", THEME.get("table_rail", "#2E4F76"))
        edge_glow = THEME.get("table.edgeGlow", "#0B2F24")
        inlay_color = THEME.get("table.inlay", "#C6A664")
        
        print(f"🎨 Professional TableFelt rendering: {w}x{h}, felt: {felt_color}, rail: {rail_color}")
        
        # === PROFESSIONAL OVAL POKER TABLE (MATCHING OLD UI SCREENSHOT) ===
        
        # Get additional theme colors for professional look
        rail_highlight = THEME.get("table.railHighlight", "#DAA520")  # Gold accents
        center_color = THEME.get("table.center", "#154035")  # Center highlight
        
        # Table center and sizing for oval shape
        cx, cy = w//2, h//2
        
        # 1. Background canvas (very dark)  
        c.create_rectangle(
            0, 0, w, h,
            fill=THEME.get("primary_bg", "#0A1A0A"),
            outline="",
            tags=("layer:felt", "canvas_bg"),
        )
        
        # 2. Professional oval table rail (bronze/copper) - main table shape
        rail_width = min(w-60, int(h*1.6)) // 2  # Proper oval proportions
        rail_height = min(h-60, int(w*0.6)) // 2
        c.create_oval(
            cx - rail_width, cy - rail_height, 
            cx + rail_width, cy + rail_height,
            fill=rail_color,
            outline="",
            tags=("layer:felt", "table_rail"),
        )
        
        # 3. Gold accent lines on rail (matching screenshot)
        c.create_oval(
            cx - rail_width + 8, cy - rail_height + 8,
            cx + rail_width - 8, cy + rail_height - 8,
            fill="", 
            outline=rail_highlight, 
            width=3,
            tags=("layer:felt", "rail_accent"),
        )
        
        # 4. Outer edge glow (dark border for depth)
        felt_width = rail_width - 22
        felt_height = rail_height - 22
        c.create_oval(
            cx - felt_width - 2, cy - felt_height - 2,
            cx + felt_width + 2, cy + felt_height + 2,
            fill="", 
            outline=edge_glow, 
            width=2,
            tags=("layer:felt", "edge_glow"),
        )
        
        # 5. Main oval felt surface (deep professional green)
        c.create_oval(
            cx - felt_width, cy - felt_height,
            cx + felt_width, cy + felt_height,
            fill=felt_color,
            outline="",
            tags=("layer:felt", "felt_main"),
        )
        
        # 6. Subtle center oval for community cards (like screenshot)
        center_width = min(180, felt_width // 2)
        center_height = min(90, felt_height // 3)
        c.create_oval(
            cx - center_width, cy - center_height,
            cx + center_width, cy + center_height,
            fill="", 
            outline=center_color, 
            width=1,
            tags=("layer:felt", "center_oval"),
        )
        
        # 7. Professional inlay accents (6 decorative spots around table)
        import math
        for i, angle in enumerate([0, 60, 120, 180, 240, 300]):
            rad = math.radians(angle)
            accent_x = cx + (felt_width * 0.75) * math.cos(rad)
            accent_y = cy + (felt_height * 0.75) * math.sin(rad)
            c.create_oval(
                accent_x-4, accent_y-4, accent_x+4, accent_y+4,
                fill=inlay_color,
                outline="",
                tags=("layer:felt", f"inlay_accent_{i}"),
            )

