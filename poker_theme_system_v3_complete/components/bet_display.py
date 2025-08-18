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
    return (
        {
            "bet.bg": "#374151", 
            "bet.border": "#6B7280",
            "bet.text": "#FFD700",
            "bet.active": "#DC2626"
        }, 
        {"font.body": ("Arial", 12, "bold")}
    )


class BetDisplay:
    def __init__(self):
        self._bet_elements = {}  # Store bet display elements per seat
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Get seats data from state
        seats_data = state.get("seats", [])
        if not seats_data:
            return
        
        count = len(seats_data)
        positions = get_seat_positions(state, seat_count=count)
        
        # Clear old bet displays that are no longer needed
        current_seats = set(range(len(seats_data)))
        old_seats = set(self._bet_elements.keys()) - current_seats
        for old_seat in old_seats:
            if old_seat in self._bet_elements:
                for element_id in self._bet_elements[old_seat].values():
                    try:
                        c.delete(element_id)
                    except Exception:
                        pass
                del self._bet_elements[old_seat]
        
        for idx, (x, y) in enumerate(positions):
            if idx >= len(seats_data):
                break
                
            seat = seats_data[idx]
            current_bet = seat.get('current_bet', 0) or seat.get('bet', 0)
            
            # Initialize bet elements for this seat if needed
            if idx not in self._bet_elements:
                self._bet_elements[idx] = {}
            
            if current_bet > 0:
                # Position bet display between seat and table center
                center_x, center_y = w // 2, int(h * 0.52)
                
                # Calculate direction from seat to center  
                dx = center_x - x
                dy = center_y - y
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance > 0:
                    # Position bet closer to center than seat
                    offset = 35  # Distance from seat center towards table
                    bet_x = x + (dx / distance) * offset
                    bet_y = y + (dy / distance) * offset
                else:
                    bet_x, bet_y = x + 35, y
                
                bet_text = f"${current_bet:,.0f}"
                
                # Bet background
                bg_width, bg_height = 50, 25
                is_acting = seat.get('acting', False)
                bg_color = THEME.get("bet.active", "#DC2626") if is_acting else THEME.get("bet.bg", "#374151")
                
                if 'bg' not in self._bet_elements[idx]:
                    self._bet_elements[idx]['bg'] = c.create_rectangle(
                        bet_x - bg_width//2,
                        bet_y - bg_height//2,
                        bet_x + bg_width//2,
                        bet_y + bg_height//2,
                        fill=bg_color,
                        outline=THEME.get("bet.border", "#6B7280"),
                        width=1,
                        tags=("layer:bets", f"bet_bg:{idx}"),
                    )
                else:
                    c.coords(
                        self._bet_elements[idx]['bg'],
                        bet_x - bg_width//2,
                        bet_y - bg_height//2,
                        bet_x + bg_width//2,
                        bet_y + bg_height//2
                    )
                    c.itemconfig(
                        self._bet_elements[idx]['bg'],
                        fill=bg_color,
                        outline=THEME.get("bet.border", "#6B7280")
                    )
                
                # Bet text
                if 'text' not in self._bet_elements[idx]:
                    self._bet_elements[idx]['text'] = c.create_text(
                        bet_x,
                        bet_y,
                        text=bet_text,
                        font=FONTS.get("font.body", ("Arial", 10, "bold")),
                        fill=THEME.get("bet.text", "#FFD700"),
                        tags=("layer:bets", f"bet_text:{idx}"),
                    )
                else:
                    c.coords(self._bet_elements[idx]['text'], bet_x, bet_y)
                    c.itemconfig(
                        self._bet_elements[idx]['text'],
                        text=bet_text,
                        fill=THEME.get("bet.text", "#FFD700")
                    )
                
                # Tag elements properly
                c.addtag_withtag("layer:bets", self._bet_elements[idx]['bg'])
                c.addtag_withtag("layer:bets", self._bet_elements[idx]['text'])
                
            else:
                # No bet - hide bet display
                for element_type in ['bg', 'text']:
                    if element_type in self._bet_elements[idx]:
                        try:
                            c.delete(self._bet_elements[idx][element_type])
                        except Exception:
                            pass
                        del self._bet_elements[idx][element_type]
