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
            
        # Calculate board positions using actual canvas size
        cx, cy = w // 2, int(h * 0.45)
        spacing = int(min(w, h) * 0.055)
        xs = [
            cx - 2 * spacing,
            cx - spacing, 
            cx,
            cx + int(spacing * 1.5),
            cx + spacing * 3,
        ]
        positions = [(x, cy) for x in xs]
        
        # Consistent professional card dimensions
        card_w = 44  # Standard card width (consistent with hole cards)
        card_h = 64  # Standard card height (maintaining 1.45 ratio)
        
        print(f"🃏 Board positions on {w}x{h}: center=({cx},{cy}), spacing={spacing}, positions={positions}")
        
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
                
                # Card text (rank and suit with proper colors)
                display_text, text_color = format_card_display(card, show_suits=True)
                c.create_text(
                    x,
                    y,
                    text=display_text,
                    font=FONTS.get("font.body", ("Arial", 14, "bold")),
                    fill=text_color,
                    tags=("layer:community", f"board_text:{idx}"),
                )
            else:
                # Professional card back (face down) - consistent with hole cards
                c.create_rectangle(
                    x - card_w // 2,
                    y - card_h // 2,
                    x + card_w // 2,
                    y + card_h // 2,
                    fill=THEME.get("board.cardBack", "#8B0000"),  # Red card back
                    outline=THEME.get("board.border", "#2F4F4F"),
                    width=2,
                    tags=("layer:community", f"board_slot:{idx}"),
                )
                
                # Professional card back pattern (matching hole cards)
                c.create_text(
                    x,
                    y - 8,  # Upper pattern
                    text="♣",
                    fill="#AA0000",  # Darker red for pattern
                    font=("Arial", 18, "bold"),  # Larger for community cards
                    tags=("layer:community", f"card_pattern_top:{idx}"),
                )
                
                c.create_text(
                    x,
                    y + 8,  # Lower pattern
                    text="♦",
                    fill="#AA0000",  # Darker red for pattern
                    font=("Arial", 18, "bold"),  # Larger for community cards
                    tags=("layer:community", f"card_pattern_bottom:{idx}"),
                )

