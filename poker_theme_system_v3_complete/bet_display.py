from ...state.selectors import get_seat_positions, get_num_seats
from ...services.theme_manager import ThemeManager
from .chip_graphics import ChipGraphics, BetDisplay as ChipBetDisplay


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
        self._chip_graphics = None  # Will be initialized when canvas is available
        self._chip_bet_display = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Initialize chip graphics if needed
        if self._chip_graphics is None:
            self._chip_graphics = ChipGraphics(c)
            self._chip_bet_display = ChipBetDisplay(c)
        
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
                    offset = 45  # Distance from seat center towards table
                    bet_x = x + (dx / distance) * offset
                    bet_y = y + (dy / distance) * offset
                else:
                    bet_x, bet_y = x + 45, y
                
                # Clear old bet elements for this seat
                if idx in self._bet_elements:
                    for element_id in self._bet_elements[idx].values():
                        try:
                            c.delete(element_id)
                        except Exception:
                            pass
                    self._bet_elements[idx] = {}
                
                # Determine bet type for styling
                is_acting = seat.get('acting', False)
                last_action = seat.get('last_action', '')
                
                bet_type = "bet"
                if last_action == "call":
                    bet_type = "call"
                elif last_action in ["raise", "bet"]:
                    bet_type = "raise"
                elif is_acting:
                    bet_type = "active"
                
                # Render luxury chip-based bet display
                bet_elements = self._chip_bet_display.render(
                    bet_x, bet_y, current_bet, bet_type,
                    tags=("layer:bets", f"bet:{idx}")
                )
                
                # Store elements for cleanup
                self._bet_elements[idx] = {f"element_{i}": elem_id for i, elem_id in enumerate(bet_elements)}
                
            else:
                # No bet - hide bet display
                if idx in self._bet_elements:
                    for element_id in self._bet_elements[idx].values():
                        try:
                            c.delete(element_id)
                        except Exception:
                            pass
                    self._bet_elements[idx] = {}
    
    def animate_bet_to_pot(self, seat_idx: int, pot_x: int, pot_y: int, 
                          bet_amount: int, callback=None):
        """Animate bet chips moving from seat to pot."""
        if self._chip_graphics and seat_idx in self._bet_elements:
            # Get bet position
            c = self._chip_graphics.canvas
            w, h = c.winfo_width(), c.winfo_height()
            
            # Calculate seat position (simplified)
            center_x, center_y = w // 2, int(h * 0.52)
            # This should use the actual seat position calculation
            # For now, using a simplified version
            
            self._chip_graphics.animate_chips_to_pot(
                center_x + 50, center_y + 50,  # Approximate bet position
                pot_x, pot_y, bet_amount,
                duration=600, callback=callback
            )
    
    def animate_pot_to_winner(self, pot_x: int, pot_y: int, 
                            winner_seat_idx: int, pot_amount: int, callback=None):
        """Animate pot chips moving to winner."""
        if self._chip_graphics:
            # Get winner position (simplified)
            c = self._chip_graphics.canvas
            w, h = c.winfo_width(), c.winfo_height()
            
            # Calculate winner position (simplified)
            center_x, center_y = w // 2, int(h * 0.52)
            winner_x, winner_y = center_x - 100, center_y - 100  # Approximate
            
            self._chip_graphics.animate_pot_to_winner(
                pot_x, pot_y, winner_x, winner_y, pot_amount,
                duration=1000, callback=callback
            )
