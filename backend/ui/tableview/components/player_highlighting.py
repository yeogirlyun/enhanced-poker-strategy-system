"""
Professional Player Seat Highlighting System
Implements industry-standard seat highlighting similar to PokerStars, 888poker, etc.
"""

import math
from typing import Dict, Any, List, Tuple, Optional


class PlayerHighlighting:
    """Professional-grade player seat highlighting system."""
    
    def __init__(self):
        self._highlight_elements = {}  # Store highlight elements per seat
        self._animation_state = 0  # For pulsing animations
        self._last_acting_player = None
        
    def render(self, state, canvas_manager, layer_manager) -> None:
        """Render professional seat highlighting."""
        canvas = canvas_manager.canvas
        w, h = canvas_manager.size()
        
        if w <= 1 or h <= 1:
            return
            
        # Get seats data
        seats_data = state.get("seats", [])
        if not seats_data:
            return
            
        # Get seat positions
        from ...state.selectors import get_seat_positions
        positions = get_seat_positions(state, seat_count=len(seats_data), 
                                     canvas_width=w, canvas_height=h)
        
        # Clear old highlights
        self._clear_all_highlights(canvas)
        
        # Render highlights for each seat
        for idx, (seat_data, (x, y)) in enumerate(zip(seats_data, positions)):
            self._render_seat_highlight(canvas, x, y, idx, seat_data, w, h)
            
        # Update animation state
        self._animation_state = (self._animation_state + 1) % 60
        
        # Schedule next animation frame if needed
        if any(seat.get('acting', False) for seat in seats_data):
            canvas.after(100, lambda: self._animate_highlights(canvas_manager))
    
    def _render_seat_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any], 
                              canvas_w: int, canvas_h: int) -> None:
        """Render highlighting for a single seat."""
        
        # Base seat circle - always visible for occupied seats
        if seat.get('name') or seat.get('stack', 0) > 0:
            self._render_base_seat_circle(canvas, x, y, idx, seat)
        
        # Player state highlighting
        if seat.get('acting', False):
            self._render_acting_player_highlight(canvas, x, y, idx, seat)
        elif seat.get('folded', False):
            self._render_folded_player_highlight(canvas, x, y, idx, seat)
        elif seat.get('all_in', False):
            self._render_all_in_player_highlight(canvas, x, y, idx, seat)
        elif seat.get('winner', False):
            self._render_winner_highlight(canvas, x, y, idx, seat)
        else:
            self._render_active_player_highlight(canvas, x, y, idx, seat)
            
        # Position indicator
        self._render_position_indicator(canvas, x, y, idx, seat)
        
        # Player info overlay
        self._render_player_info(canvas, x, y, idx, seat)
    
    def _render_base_seat_circle(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render the base seat circle - professional style."""
        # Seat size based on canvas size
        seat_radius = 45
        
        # Base seat background - dark with subtle border
        base_circle = canvas.create_oval(
            x - seat_radius, y - seat_radius,
            x + seat_radius, y + seat_radius,
            fill="#1F2937",  # Dark gray background
            outline="#374151",  # Slightly lighter border
            width=3,
            tags=("layer:seats", f"seat_base:{idx}")
        )
        
        # Inner seat circle - slightly lighter
        inner_radius = seat_radius - 8
        inner_circle = canvas.create_oval(
            x - inner_radius, y - inner_radius,
            x + inner_radius, y + inner_radius,
            fill="#2D3748",  # Slightly lighter
            outline="",
            tags=("layer:seats", f"seat_inner:{idx}")
        )
        
        self._store_element(idx, 'base_circle', base_circle)
        self._store_element(idx, 'inner_circle', inner_circle)
    
    def _render_acting_player_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render highlighting for the acting player - bright and pulsing."""
        # Pulsing outer ring - bright gold
        pulse_factor = 1.0 + 0.3 * math.sin(self._animation_state * 0.3)
        outer_radius = int(55 * pulse_factor)
        
        # Bright pulsing outer ring
        outer_ring = canvas.create_oval(
            x - outer_radius, y - outer_radius,
            x + outer_radius, y + outer_radius,
            fill="",
            outline="#FFD700",  # Bright gold
            width=5,
            tags=("layer:action", f"acting_outer:{idx}")
        )
        
        # Steady inner action ring
        action_ring = canvas.create_oval(
            x - 50, y - 50,
            x + 50, y + 50,
            fill="",
            outline="#FFA500",  # Orange
            width=3,
            tags=("layer:action", f"acting_inner:{idx}")
        )
        
        # Action indicator dot
        dot_radius = 8
        action_dot = canvas.create_oval(
            x - dot_radius, y - dot_radius,
            x + dot_radius, y + dot_radius,
            fill="#FF4444",  # Bright red
            outline="#FFFFFF",  # White outline
            width=2,
            tags=("layer:action", f"acting_dot:{idx}")
        )
        
        self._store_element(idx, 'acting_outer', outer_ring)
        self._store_element(idx, 'acting_inner', action_ring)
        self._store_element(idx, 'acting_dot', action_dot)
        
        # Action text
        self._render_action_text(canvas, x, y - 70, "YOUR TURN", "#FFD700")
    
    def _render_active_player_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render highlighting for active (non-folded) players."""
        # Subtle green ring for active players
        active_ring = canvas.create_oval(
            x - 48, y - 48,
            x + 48, y + 48,
            fill="",
            outline="#10B981",  # Green
            width=2,
            tags=("layer:status", f"active_ring:{idx}")
        )
        
        self._store_element(idx, 'active_ring', active_ring)
    
    def _render_folded_player_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render highlighting for folded players."""
        # Red ring for folded players
        folded_ring = canvas.create_oval(
            x - 48, y - 48,
            x + 48, y + 48,
            fill="",
            outline="#EF4444",  # Red
            width=2,
            tags=("layer:status", f"folded_ring:{idx}")
        )
        
        # Semi-transparent overlay to dim the seat
        overlay = canvas.create_oval(
            x - 45, y - 45,
            x + 45, y + 45,
            fill="#000000",
            stipple="gray50",  # Semi-transparent
            outline="",
            tags=("layer:status", f"folded_overlay:{idx}")
        )
        
        self._store_element(idx, 'folded_ring', folded_ring)
        self._store_element(idx, 'folded_overlay', overlay)
        
        # Status text
        self._render_status_text(canvas, x, y + 60, "FOLDED", "#EF4444")
    
    def _render_all_in_player_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render highlighting for all-in players."""
        # Bright orange ring for all-in
        all_in_ring = canvas.create_oval(
            x - 50, y - 50,
            x + 50, y + 50,
            fill="",
            outline="#F59E0B",  # Orange
            width=4,
            tags=("layer:status", f"all_in_ring:{idx}")
        )
        
        self._store_element(idx, 'all_in_ring', all_in_ring)
        
        # Status text
        self._render_status_text(canvas, x, y + 60, "ALL IN", "#F59E0B")
    
    def _render_winner_highlight(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render highlighting for winning players."""
        # Bright green celebration ring
        winner_ring = canvas.create_oval(
            x - 52, y - 52,
            x + 52, y + 52,
            fill="",
            outline="#22C55E",  # Bright green
            width=5,
            tags=("layer:status", f"winner_ring:{idx}")
        )
        
        # Inner celebration ring
        inner_winner = canvas.create_oval(
            x - 46, y - 46,
            x + 46, y + 46,
            fill="",
            outline="#16A34A",  # Darker green
            width=3,
            tags=("layer:status", f"winner_inner:{idx}")
        )
        
        self._store_element(idx, 'winner_ring', winner_ring)
        self._store_element(idx, 'winner_inner', inner_winner)
        
        # Winner text
        self._render_status_text(canvas, x, y + 60, "WINNER", "#22C55E")
    
    def _render_position_indicator(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render position indicator (SB, BB, BTN, etc.)."""
        position = seat.get('position', '')
        if not position:
            return
            
        # Position badge
        badge_width = 30
        badge_height = 16
        
        # Position colors
        pos_colors = {
            'SB': '#3B82F6',  # Blue
            'BB': '#EF4444',  # Red
            'BTN': '#F59E0B', # Orange
            'CO': '#8B5CF6',  # Purple
            'MP': '#06B6D4',  # Cyan
            'UTG': '#10B981'  # Green
        }
        
        color = pos_colors.get(position, '#6B7280')  # Default gray
        
        # Badge background
        badge_bg = canvas.create_rectangle(
            x - badge_width//2, y - 25 - badge_height//2,
            x + badge_width//2, y - 25 + badge_height//2,
            fill=color,
            outline="#FFFFFF",
            width=1,
            tags=("layer:status", f"position_badge:{idx}")
        )
        
        # Badge text
        badge_text = canvas.create_text(
            x, y - 25,
            text=position,
            font=("Arial", 9, "bold"),
            fill="#FFFFFF",
            tags=("layer:status", f"position_text:{idx}")
        )
        
        self._store_element(idx, 'position_badge', badge_bg)
        self._store_element(idx, 'position_text', badge_text)
    
    def _render_player_info(self, canvas, x: int, y: int, idx: int, seat: Dict[str, Any]) -> None:
        """Render player name and stack info."""
        name = seat.get('name', f'Player {idx + 1}')
        stack = seat.get('stack', 0)
        
        # Player name
        name_text = canvas.create_text(
            x, y + 10,
            text=name,
            font=("Arial", 11, "bold"),
            fill="#F8FAFC",
            tags=("layer:seats", f"player_name:{idx}")
        )
        
        # Stack amount
        stack_text = canvas.create_text(
            x, y + 25,
            text=f"${stack:,}" if stack > 0 else "",
            font=("Arial", 9, "normal"),
            fill="#D1D5DB",
            tags=("layer:seats", f"player_stack:{idx}")
        )
        
        self._store_element(idx, 'name_text', name_text)
        self._store_element(idx, 'stack_text', stack_text)
    
    def _render_action_text(self, canvas, x: int, y: int, text: str, color: str) -> None:
        """Render action text with background."""
        # Text background
        bg_width = len(text) * 8 + 20
        bg_height = 20
        
        text_bg = canvas.create_rectangle(
            x - bg_width//2, y - bg_height//2,
            x + bg_width//2, y + bg_height//2,
            fill="#000000",
            outline=color,
            width=2,
            tags=("layer:action", "action_text_bg")
        )
        
        # Action text
        action_text = canvas.create_text(
            x, y,
            text=text,
            font=("Arial", 12, "bold"),
            fill=color,
            tags=("layer:action", "action_text")
        )
    
    def _render_status_text(self, canvas, x: int, y: int, text: str, color: str) -> None:
        """Render status text with background."""
        # Text background
        bg_width = len(text) * 7 + 16
        bg_height = 18
        
        text_bg = canvas.create_rectangle(
            x - bg_width//2, y - bg_height//2,
            x + bg_width//2, y + bg_height//2,
            fill="#1F2937",
            outline=color,
            width=1,
            tags=("layer:status", "status_text_bg")
        )
        
        # Status text
        status_text = canvas.create_text(
            x, y,
            text=text,
            font=("Arial", 10, "bold"),
            fill=color,
            tags=("layer:status", "status_text")
        )
    
    def _store_element(self, seat_idx: int, element_type: str, element_id: Any) -> None:
        """Store element ID for cleanup."""
        if seat_idx not in self._highlight_elements:
            self._highlight_elements[seat_idx] = {}
        self._highlight_elements[seat_idx][element_type] = element_id
    
    def _clear_all_highlights(self, canvas) -> None:
        """Clear all existing highlight elements."""
        for seat_elements in self._highlight_elements.values():
            for element_id in seat_elements.values():
                try:
                    canvas.delete(element_id)
                except Exception:
                    pass
        self._highlight_elements.clear()
    
    def _animate_highlights(self, canvas_manager) -> None:
        """Continue highlight animations."""
        try:
            # Trigger a re-render to update animations
            if hasattr(canvas_manager, 'parent') and hasattr(canvas_manager.parent, 'renderer_pipeline'):
                if hasattr(canvas_manager.parent, 'store'):
                    state = canvas_manager.parent.store.get_state()
                    if state:
                        canvas_manager.parent.renderer_pipeline.render_once(state)
        except Exception:
            pass  # Silently continue if animation fails
