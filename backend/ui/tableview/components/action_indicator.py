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
        positions = get_seat_positions(state, seat_count=count, 
                                     canvas_width=w, canvas_height=h)
        
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
            
            # Create much more visible pulsing ring around acting player
            ring_radius = int(min(w, h) * 0.12)  # Larger radius for better visibility
            
            # Enhanced pulse effect with stronger colors and animation
            self._pulse_state = (self._pulse_state + 1) % 30
            pulse_factor = 1.0 + 0.2 * (1 + 0.8 * (self._pulse_state < 15))  # Stronger pulse
            current_radius = int(ring_radius * pulse_factor)
            
            self._indicator_elements[acting_player_idx] = {}
            
            # Outer ring (bright pulsing)
            self._indicator_elements[acting_player_idx]['outer_ring'] = c.create_oval(
                x - current_radius,
                y - current_radius,
                x + current_radius,
                y + current_radius,
                fill="",
                outline="#FFD700",  # Bright gold for maximum visibility
                width=4,  # Thicker line
                tags=("layer:action", f"action_ring_outer:{acting_player_idx}"),
            )
            
            # Inner ring (steady bright)
            inner_radius = ring_radius - 8
            self._indicator_elements[acting_player_idx]['inner_ring'] = c.create_oval(
                x - inner_radius,
                y - inner_radius,
                x + inner_radius,
                y + inner_radius,
                fill="",
                outline="#00FF00",  # Bright green for maximum visibility
                width=3,  # Thicker line
                tags=("layer:action", f"action_ring_inner:{acting_player_idx}"),
            )
            
            # Add a bright center dot for maximum visibility
            center_radius = 8
            self._indicator_elements[acting_player_idx]['center_dot'] = c.create_oval(
                x - center_radius,
                y - center_radius,
                x + center_radius,
                y + center_radius,
                fill="#FF0000",  # Bright red center
                outline="#FFFFFF",  # White outline
                width=2,
                tags=("layer:action", f"action_center:{acting_player_idx}"),
            )
            
            # Enhanced action text indicator with background
            action_text = "YOUR TURN"
            seat_data = seats_data[acting_player_idx]
            player_name = seat_data.get('name', f'Player {acting_player_idx + 1}')
            
            # Position text above the seat with background for better readability
            text_y = y - ring_radius - 30
            
            # Create background rectangle for text
            text_bg = c.create_rectangle(
                x - 80, text_y - 15,
                x + 80, text_y + 15,
                fill="#000000",  # Black background
                outline="#FFD700",  # Gold outline
                width=2,
                tags=("layer:action", f"action_bg:{acting_player_idx}"),
            )
            
            # Create the text
            self._indicator_elements[acting_player_idx]['text'] = c.create_text(
                x,
                text_y,
                text=f"{player_name}'s Turn",
                font=("Arial", 12, "bold"),  # Larger, bolder font
                fill="#FFFFFF",  # White text for maximum contrast
                tags=("layer:action", f"action_text:{acting_player_idx}"),
            )
            
            # Add player status labels for all seats
            self._add_player_status_labels(c, seats_data, positions)
            
            # Tag all elements
            for element_id in self._indicator_elements[acting_player_idx].values():
                c.addtag_withtag("layer:action", element_id)
        
        # Schedule next animation frame for pulsing effect
        if acting_player_idx is not None:
            canvas_manager.canvas.after(80, lambda: self._animate_pulse(canvas_manager))  # Faster animation
    
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

    def _add_player_status_labels(self, canvas, seats_data, positions):
        """Add status labels for all players (folded, winner, etc.)"""
        for idx, (seat, (x, y)) in enumerate(zip(seats_data, positions)):
            if idx in self._indicator_elements:
                continue  # Skip acting player (already handled)
                
            # Create status label
            status = self._get_player_status(seat)
            if status:
                # Position label below the seat
                label_y = y + 40
                
                # Create background for status
                bg_id = canvas.create_rectangle(
                    x - 50, label_y - 10,
                    x + 50, label_y + 10,
                    fill="#1F2937",  # Dark background
                    outline="#6B7280",  # Gray outline
                    width=1,
                    tags=("layer:status", f"status_bg:{idx}"),
                )
                
                # Create status text
                text_id = canvas.create_text(
                    x,
                    label_y,
                    text=status,
                    font=("Arial", 9, "bold"),
                    fill=self._get_status_color(status),
                    tags=("layer:status", f"status_text:{idx}"),
                )
                
                # Store for cleanup
                if idx not in self._indicator_elements:
                    self._indicator_elements[idx] = {}
                self._indicator_elements[idx][f'status_bg'] = bg_id
                self._indicator_elements[idx][f'status_text'] = text_id
    
    def _get_player_status(self, seat):
        """Get the status text for a player seat"""
        if seat.get('folded', False):
            return "FOLDED"
        elif seat.get('all_in', False):
            return "ALL IN"
        elif seat.get('winner', False):
            return "WINNER"
        elif seat.get('acting', False):
            return "ACTING"
        else:
            return None
    
    def _get_status_color(self, status):
        """Get the appropriate color for a status"""
        if status == "FOLDED":
            return "#EF4444"  # Red
        elif status == "ALL IN":
            return "#F59E0B"  # Orange
        elif status == "WINNER":
            return "#10B981"  # Green
        elif status == "ACTING":
            return "#3B82F6"  # Blue
        else:
            return "#6B7280"  # Gray
