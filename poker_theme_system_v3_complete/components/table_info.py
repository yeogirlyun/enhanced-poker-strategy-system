"""
Table Info Display - Shows blinds, hand number, and other table information
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
            "info.bg": "#111827",
            "info.border": "#374151", 
            "info.text": "#D1D5DB",
            "info.highlight": "#F59E0B"
        }, 
        {"font.body": ("Arial", 9, "normal")}
    )


class TableInfo:
    def __init__(self):
        self._info_elements = {}
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Clear previous elements
        for element_id in self._info_elements.values():
            try:
                c.delete(element_id)
            except Exception:
                pass
        self._info_elements = {}
        
        # Get hand info from state
        loaded_hand = state.get("review", {}).get("loaded_hand", {})
        if not loaded_hand:
            return
            
        # Position at bottom left of table
        info_x = 20
        info_y = h - 60
        info_width = 200
        info_height = 50
        
        # Background panel
        self._info_elements['info_bg'] = c.create_rectangle(
            info_x, info_y,
            info_x + info_width, info_y + info_height,
            fill=THEME.get("info.bg", "#111827"),
            outline=THEME.get("info.border", "#374151"),
            width=1,
            tags=("layer:info", "info_bg"),
        )
        
        # Hand ID
        hand_id = loaded_hand.get('hand_id', 'Unknown')
        self._info_elements['hand_id'] = c.create_text(
            info_x + 10,
            info_y + 12,
            text=f"Hand: {hand_id}",
            font=FONTS.get("font.body", ("Arial", 9, "bold")),
            fill=THEME.get("info.highlight", "#F59E0B"),
            anchor="w",
            tags=("layer:info", "hand_id"),
        )
        
        # Blinds info
        small_blind = loaded_hand.get('small_blind', 1)
        big_blind = loaded_hand.get('big_blind', 2)
        self._info_elements['blinds'] = c.create_text(
            info_x + 10,
            info_y + 25,
            text=f"Blinds: ${small_blind}/${big_blind}",
            font=FONTS.get("font.body", ("Arial", 9, "normal")),
            fill=THEME.get("info.text", "#D1D5DB"),
            anchor="w",
            tags=("layer:info", "blinds"),
        )
        
        # Number of players
        seats_data = state.get("seats", [])
        active_players = len([s for s in seats_data if s.get('name', '').strip() and not s.get('name', '').startswith('seat')])
        self._info_elements['players'] = c.create_text(
            info_x + 10,
            info_y + 38,
            text=f"Players: {active_players}",
            font=FONTS.get("font.body", ("Arial", 9, "normal")),
            fill=THEME.get("info.text", "#D1D5DB"),
            anchor="w",
            tags=("layer:info", "players"),
        )
        
        # Game type (top right corner)
        game_type = "No Limit Hold'em"  # Could be dynamic from hand data
        self._info_elements['game_type'] = c.create_text(
            w - 20,
            20,
            text=game_type,
            font=FONTS.get("font.body", ("Arial", 10, "bold")),
            fill=THEME.get("info.text", "#D1D5DB"),
            anchor="ne",
            tags=("layer:info", "game_type"),
        )
        
        # Tag all elements
        for element_id in self._info_elements.values():
            c.addtag_withtag("layer:info", element_id)
