from ...state.selectors import get_board_positions
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
    return (
        {"board.slotBg": "#133C2E", "board.cardFaceFg": "#111317"}, 
        {"font.body": ("Arial", 14, "bold")}
    )


class Community:
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
            
        # Get number of players to match hole card sizing exactly
        seats_data = state.get("seats", [])
        # Use same player count logic as seats component
        active_seats = [s for s in seats_data if s.get("active", True)]
        num_players = len(active_seats) if active_seats else 6
        
        # Use IDENTICAL card sizing logic as hole cards for perfect consistency
        if num_players <= 3:
            card_scale = 0.06  # 6% of table size
        elif num_players <= 6:
            card_scale = 0.05  # 5% of table size
        else:
            card_scale = 0.04  # 4% of table size
        
        table_size = min(w, h)
        card_w = int(table_size * card_scale * 0.7)   # IDENTICAL width calculation
        card_h = int(card_w * 1.45)                   # IDENTICAL aspect ratio
        
        # Center community cards with no gaps (compact layout)
        cx, cy = w // 2, int(h * 0.45)  # Centered horizontally, 45% down vertically
        total_width = 5 * card_w  # 5 cards touching each other
        start_x = cx - total_width // 2 + card_w // 2  # Start position for first card
        
        positions = [(start_x + i * card_w, cy) for i in range(5)]
        
        print(f"🃏 Board positions on {w}x{h}: center=({cx},{cy}), card_size={card_w}x{card_h}, positions={positions}")
        
        # Get community cards from state
        board_cards = state.get("board", [])
        print(f"🃏 Community rendering: {len(board_cards)} cards, {len(positions)} positions, canvas: {w}x{h}")
        
        # Always show card slots even if no cards
        if not board_cards:
            board_cards = ["", "", "", "", ""]  # 5 empty slots
        
        for idx, (x, y) in enumerate(positions):
            if idx < len(board_cards) and board_cards[idx]:
                # Show actual community card
                card = board_cards[idx]
                
                # Card background (face up)
                c.create_rectangle(
                    x - card_w // 2,
                    y - card_h // 2,
                    x + card_w // 2,
                    y + card_h // 2,
                    fill=THEME.get("board.cardFaceFg", "#F8FAFC"),
                    outline=THEME.get("board.border", "#0B1220"),
                    width=2,
                    tags=("layer:community", f"board:{idx}"),
                )
                
                # Card text (rank and suit with proper colors) - 60% of card space
                display_text, text_color = format_card_display(card, show_suits=True)
                
                # Calculate font size as 60% of card space (matching hole cards)
                card_font_size = int(min(card_w, card_h) * 0.6)
                card_font_size = max(8, min(card_font_size, 24))  # Clamp between 8-24px
                
                c.create_text(
                    x,
                    y,
                    text=display_text,
                    font=("Arial", card_font_size, "bold"),
                    fill=text_color,
                    tags=("layer:community", f"board_text:{idx}"),
                )
            else:
                # Token-driven card back colors that change with theme (same as hole cards)
                card_back_bg = THEME.get("card.back.bg", THEME.get("board.cardBack", "#8B0000"))
                card_back_border = THEME.get("card.back.border", THEME.get("board.border", "#2F4F4F"))
                card_back_pattern = THEME.get("card.back.pattern", "#AA0000")
                
                # Professional card back (face down) - consistent with hole cards
                c.create_rectangle(
                    x - card_w // 2,
                    y - card_h // 2,
                    x + card_w // 2,
                    y + card_h // 2,
                    fill=card_back_bg,  # Theme-aware card back
                    outline=card_back_border,  # Theme-aware border
                    width=2,
                    tags=("layer:community", f"board_slot:{idx}"),
                )
                
                # Inner border for depth (matching hole cards)
                c.create_rectangle(
                    x - card_w // 2 + 2, y - card_h // 2 + 2,
                    x + card_w // 2 - 2, y + card_h // 2 - 2,
                    fill="", outline=card_back_pattern, width=1,
                    tags=("layer:community", f"board_inner:{idx}"),
                )
                
                # Luxury crosshatch pattern (matching hole cards)
                from .seats import _lighten_color, _darken_color
                hatch_light = _lighten_color(card_back_bg, 0.15)
                hatch_dark = _darken_color(card_back_bg, 0.1)
                
                # Fine crosshatch grid across the card
                spacing = max(4, card_w // 8)  # Scale with card size
                for hx in range(int(x - card_w//2 + spacing), int(x + card_w//2 - spacing), spacing):
                    for hy in range(int(y - card_h//2 + spacing), int(y + card_h//2 - spacing), spacing):
                        # Diagonal crosshatch lines
                        line_size = spacing // 2
                        c.create_line(
                            hx - line_size, hy - line_size,
                            hx + line_size, hy + line_size,
                            fill=hatch_light, width=1,
                            tags=("layer:community", f"board_hatch1:{idx}"),
                        )
                        c.create_line(
                            hx - line_size, hy + line_size,
                            hx + line_size, hy - line_size,
                            fill=hatch_dark, width=1,
                            tags=("layer:community", f"board_hatch2:{idx}"),
                        )
                
                # Central luxury emblem (dual symbols with enhanced styling)
                pattern_font_size = max(10, int(card_h * 0.25))  # Scale pattern with card size
                c.create_text(
                    x,
                    y - 8,  # Upper pattern
                    text="♣",
                    fill=card_back_pattern,  # Theme-aware pattern color
                    font=("Arial", pattern_font_size, "bold"),
                    tags=("layer:community", f"card_pattern_top:{idx}"),
                )
                
                c.create_text(
                    x,
                    y + 8,  # Lower pattern
                    text="♦",
                    fill=card_back_pattern,  # Theme-aware pattern color
                    font=("Arial", pattern_font_size, "bold"),
                    tags=("layer:community", f"card_pattern_bottom:{idx}"),
                )

