import math
from ...state.selectors import get_seat_positions, get_num_seats
from ...services.theme_manager import ThemeManager
from .card_utils import format_card_display


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
    return ({"text": "#E6E9EF", "seat_bg": "#23262B"}, {"main": ("Arial", 12, "bold")})


class Seats:
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Get seats data from state
        seats_data = state.get("seats", [])
        print(f"🪑 Seats rendering: {len(seats_data)} seats, canvas: {w}x{h}")
        
        if not seats_data:
            # Create default seats for visualization
            seats_data = [
                {"name": f"Seat {i+1}", "stack": 1000, "cards": [], "position": "", "current_bet": 0, "folded": False, "active": True}
                for i in range(6)  # Default 6 seats
            ]
            print(f"🪑 Using default seats: {len(seats_data)}")
        
        count = len(seats_data)
        
        # Calculate positions using actual canvas size instead of state
        cx, cy = w // 2, int(h * 0.52)
        radius = int(min(w, h) * 0.36)
        positions = []
        for i in range(count):
            theta = -math.pi / 2 + (2 * math.pi * i) / count
            x = cx + int(radius * math.cos(theta))
            y = cy + int(radius * math.sin(theta))
            positions.append((x, y))
        
        print(f"🪑 Calculated positions for {count} seats on {w}x{h} canvas: center=({cx},{cy}), radius={radius}")
        
        for idx, (x, y) in enumerate(positions):
            if idx >= len(seats_data):
                break
                
            seat = seats_data[idx]
            seat_radius = int(min(w, h) * 0.06)  # Larger for more info
            
            # Professional rectangular player pods (matching screenshot)
            pod_width = 100
            pod_height = 70
            
            # Determine seat colors based on state (matching screenshot)
            seat_bg_color = THEME.get("seat.bg.idle", "#334155")  # Dark blue like screenshot
            seat_ring_color = THEME.get("seat.ring", "#475569")
            border_width = 2
            
            if seat.get('acting'):
                # Gold border for acting player (like seat1 in screenshot)
                seat_ring_color = THEME.get("border_active", "#DAA520")  # Gold border
                border_width = 4
            elif seat.get('active'):
                seat_bg_color = THEME.get("seat.bg.active", "#475569")
            
            # Draw professional rectangular seat (dark blue pod like screenshot)
            c.create_rectangle(
                x - pod_width//2,
                y - pod_height//2,
                x + pod_width//2,
                y + pod_height//2,
                fill=seat_bg_color,
                outline=seat_ring_color,
                width=border_width,
                tags=("layer:seats", f"seat:{idx}"),
            )
            
            # Inner shadow for depth and professional look
            c.create_rectangle(
                x - pod_width//2 + 3,
                y - pod_height//2 + 3,
                x + pod_width//2 - 3,
                y + pod_height//2 - 3,
                fill="",
                outline=THEME.get("seat.shadow", "#1E293B"),
                width=1,
                tags=("layer:seats", f"seat_shadow:{idx}"),
            )
            
            # Player name with position (at top of pod like screenshot)
            name = seat.get('name', f'Player {idx + 1}')
            position = seat.get('position', '')
            if name != f'Player {idx + 1}' or position:  # Show if player present or has position
                # Format: "Player 6 (BB)" or "seat1 (UTG)" like screenshot
                display_name = name
                if position:
                    display_name = f"{name} ({position})"
                
                c.create_text(
                    x,
                    y - pod_height//2 + 8,  # Top of the pod
                    text=display_name,
                    font=FONTS.get("font.body", ("Arial", 11, "bold")),
                    fill=THEME.get("player.name", "#E5E7EB"),
                    tags=("layer:seats", f"name:{idx}"),
                )
                
                # Stack amount (at bottom of pod like screenshot)  
                stack = seat.get('stack', 0)
                if stack > 0:
                    c.create_text(
                        x,
                        y + pod_height//2 - 8,  # Bottom of the pod
                        text=f"${stack:,}",  # Format with commas like screenshot
                        font=FONTS.get("font.body", ("Arial", 12, "bold")),  # Larger, bold
                        fill=THEME.get("text_gold", "#DAA520"),  # Gold stack text like screenshot
                        tags=("layer:seats", f"stack:{idx}"),
                    )
                
                # Position indicator (in seat circle)
                position = seat.get('position', '')
                if position:
                    c.create_text(
                        x,
                        y - 8,
                        text=position,
                        font=FONTS.get("font.body", ("Arial", 9, "bold")),
                        fill=THEME.get("player.name", "#E5E7EB"),
                        tags=("layer:seats", f"position:{idx}"),
                    )
                
                # Professional hole cards (consistent with community cards)
                cards = seat.get('cards', [])
                if cards and len(cards) >= 2:
                    card_width = 22   # Consistent card width
                    card_height = 32  # Consistent card height (1.45 ratio)
                    card_gap = 6      # Tighter spacing for pods
                    
                    for i, card in enumerate(cards[:2]):  # Only show 2 hole cards
                        card_x = x - (card_width + card_gap//2) + i * (card_width + card_gap)
                        card_y = y - 5  # Position cards inside the pod
                        
                        # Professional red card back (matching community cards)
                        c.create_rectangle(
                            card_x,
                            card_y,
                            card_x + card_width,
                            card_y + card_height,
                            fill=THEME.get("board.cardBack", "#8B0000"),  # Red card back
                            outline=THEME.get("board.border", "#2F4F4F"),
                            width=2,  # Professional border width
                            tags=("layer:seats", f"card:{idx}:{i}"),
                        )
                        
                        # Enhanced card back pattern (dual symbols like old UI)
                        c.create_text(
                            card_x + card_width//2,
                            card_y + card_height//2 - 4,  # Upper symbol
                            text="♣",  # Club
                            fill="#AA0000",  # Darker red for pattern
                            font=("Arial", 10, "bold"),
                            tags=("layer:seats", f"card_pattern_top:{idx}:{i}"),
                        )
                        
                        c.create_text(
                            card_x + card_width//2,
                            card_y + card_height//2 + 4,  # Lower symbol
                            text="♦",  # Diamond
                            fill="#AA0000",  # Darker red for pattern
                            font=("Arial", 10, "bold"),
                            tags=("layer:seats", f"card_pattern_bottom:{idx}:{i}"),
                        )
                        
                        # Show actual card if revealed (not face down)
                        if card != "XX" and card:  # "XX" means face down
                            try:
                                display_text, text_color = format_card_display(card, show_suits=True)
                                c.create_text(
                                    card_x + card_width//2,
                                    card_y + card_height//2,
                                    text=display_text,
                                    font=("Arial", 8, "bold"),
                                    fill=text_color,
                                    tags=("layer:seats", f"card_text:{idx}:{i}"),
                                )
                            except Exception:
                                # Keep card back pattern if display fails
                                pass
            else:
                # Empty seat - just show seat number
                c.create_text(
                    x,
                    y,
                    text=str(idx + 1),
                    font=FONTS.get("font.body", ("Arial", 12, "bold")),
                    fill=THEME.get("player.name", "#6B7280"),
                    tags=("layer:seats", f"seat_label:{idx}"),
                )

