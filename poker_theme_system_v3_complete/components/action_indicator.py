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
            "action.ring": "#10B981", 
            "action.pulse": "#34D399",
            "action.text": "#FFFFFF"
        }, 
        {"font.body": ("Arial", 10, "bold")}
    )


class ActionIndicator:
    def __init__(self):
        self._indicator_elements = {}  # Store indicator elements per seat
        self._pulse_state = 0  # For animation
    
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
        
        # Clear old indicators
        for seat_idx in list(self._indicator_elements.keys()):
            for element_id in self._indicator_elements[seat_idx].values():
                try:
                    c.delete(element_id)
                except Exception:
                    pass
            del self._indicator_elements[seat_idx]
        
        # Find acting player
        acting_player_idx = None
        for idx, seat in enumerate(seats_data):
            if seat.get('acting', False) or seat.get('active', False):
                acting_player_idx = idx
                break
        
        if acting_player_idx is not None and acting_player_idx < len(positions):
            x, y = positions[acting_player_idx]
            
            # Create pulsing ring around acting player
            ring_radius = int(min(w, h) * 0.08)  # Larger than seat
            
            # Pulse effect - alternate between two ring sizes
            self._pulse_state = (self._pulse_state + 1) % 20
            pulse_factor = 1.0 + 0.1 * (1 + 0.5 * (self._pulse_state < 10))
            current_radius = int(ring_radius * pulse_factor)
            
            self._indicator_elements[acting_player_idx] = {}
            
            # Outer ring (pulsing)
            self._indicator_elements[acting_player_idx]['outer_ring'] = c.create_oval(
                x - current_radius,
                y - current_radius,
                x + current_radius,
                y + current_radius,
                fill="",
                outline=THEME.get("action.pulse", "#34D399"),
                width=3,
                tags=("layer:action", f"action_ring_outer:{acting_player_idx}"),
            )
            
            # Inner ring (steady)
            inner_radius = ring_radius - 5
            self._indicator_elements[acting_player_idx]['inner_ring'] = c.create_oval(
                x - inner_radius,
                y - inner_radius,
                x + inner_radius,
                y + inner_radius,
                fill="",
                outline=THEME.get("action.ring", "#10B981"),
                width=2,
                tags=("layer:action", f"action_ring_inner:{acting_player_idx}"),
            )
            
            # Action text indicator
            action_text = "YOUR TURN"
            seat_data = seats_data[acting_player_idx]
            player_name = seat_data.get('name', f'Player {acting_player_idx + 1}')
            
            # Position text above the seat
            text_y = y - ring_radius - 20
            
            self._indicator_elements[acting_player_idx]['text'] = c.create_text(
                x,
                text_y,
                text=f"{player_name}'s Turn",
                font=FONTS.get("font.body", ("Arial", 10, "bold")),
                fill=THEME.get("action.text", "#FFFFFF"),
                tags=("layer:action", f"action_text:{acting_player_idx}"),
            )
            
            # Tag all elements
            for element_id in self._indicator_elements[acting_player_idx].values():
                c.addtag_withtag("layer:action", element_id)
        
        # Schedule next animation frame for pulsing effect
        if acting_player_idx is not None:
            canvas_manager.canvas.after(100, lambda: self._animate_pulse(canvas_manager))
    
    def _animate_pulse(self, canvas_manager):
        """Continue the pulse animation."""
        try:
            # Trigger a re-render to update the pulse
            if hasattr(canvas_manager, 'parent') and hasattr(canvas_manager.parent, 'renderer_pipeline'):
                # Get current state and re-render
                if hasattr(canvas_manager.parent, 'store'):
                    state = canvas_manager.parent.store.get_state()
                    canvas_manager.parent.renderer_pipeline.render_once(state)
        except Exception:
            pass  # Silently continue if animation fails
