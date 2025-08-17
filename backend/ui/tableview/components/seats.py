import math
from ...services.theme_manager import ThemeManager
from .card_utils import format_card_display
from .premium_chips import draw_chip_stack


def _lighten_color(color_hex: str, factor: float) -> str:
    """Lighten a hex color by the given factor (0.0 to 1.0)."""
    try:
        # Remove # if present
        color_hex = color_hex.lstrip("#")
        # Convert to RGB
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return color_hex  # Return original if parsing fails


def _darken_color(color_hex: str, factor: float) -> str:
    """Darken a hex color by the given factor (0.0 to 1.0)."""
    try:
        # Remove # if present
        color_hex = color_hex.lstrip("#")
        # Convert to RGB
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return color_hex  # Return original if parsing fails


def _tokens(canvas):
    # Prefer ThemeManager from widget tree
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")  # type: ignore[attr-defined]
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts(), tm
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return (
        {"text": "#E6E9EF", "seat_bg": "#23262B"},
        {"main": ("Arial", 12, "bold")},
        None,
    )


class Seats:
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS, theme_manager = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return

        # Get seats data from state
        seats_data = state.get("seats", [])
        print(f"🪑 Seats rendering: {len(seats_data)} seats, canvas: {w}x{h}")
        print(f"🪑 State keys: {list(state.keys())}")
        print(f"🪑 Seats data: {seats_data}")

        if not seats_data:
            # Create default seats for visualization
            seats_data = [
                {
                    "name": f"Seat {i + 1}",
                    "stack": 1000,
                    "cards": [],
                    "position": "",
                    "current_bet": 0,
                    "folded": False,
                    "active": True,
                }
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

        print(
            f"🪑 Calculated positions for {count} seats on {w}x{h} canvas: center=({cx},{cy}), radius={radius}"
        )

        for idx, (x, y) in enumerate(positions):
            if idx >= len(seats_data):
                break

            seat = seats_data[idx]
            # seat_radius = int(min(w, h) * 0.06)  # Would be used for circular seats

            # Luxury themed player pods with enhanced styling
            pod_width = 110
            pod_height = 80

            # Theme-aware luxury pod styling
            seat_bg_color = THEME.get("seat.bg.idle", "#334155")
            seat_ring_color = THEME.get("seat.ring", "#475569")
            seat_accent_color = THEME.get("seat.accent", "#64748B")
            border_width = 2

            # Enhanced state-based styling
            if seat.get("acting"):
                # Luxury gold border for acting player with glow effect
                seat_ring_color = THEME.get("a11y.focus", "#DAA520")
                seat_accent_color = THEME.get("pot.badgeRing", "#E6C200")
                border_width = 3
                # Add subtle glow effect
                c.create_rectangle(
                    x - pod_width // 2 - 2,
                    y - pod_height // 2 - 2,
                    x + pod_width // 2 + 2,
                    y + pod_height // 2 + 2,
                    fill="",
                    outline=seat_accent_color,
                    width=1,
                    tags=("layer:seats", f"seat_glow:{idx}"),
                )
            elif seat.get("active"):
                seat_bg_color = THEME.get("seat.bg.active", "#475569")
                seat_ring_color = THEME.get("btn.secondary.border", "#6B7280")

            # Luxury themed player pod with gradient effect
            # Main pod background
            c.create_rectangle(
                x - pod_width // 2,
                y - pod_height // 2,
                x + pod_width // 2,
                y + pod_height // 2,
                fill=seat_bg_color,
                outline=seat_ring_color,
                width=border_width,
                tags=("layer:seats", f"seat:{idx}"),
            )

            # Luxury gradient highlight (top edge)
            highlight_color = THEME.get("seat.highlight", "#475569")
            c.create_rectangle(
                x - pod_width // 2 + 2,
                y - pod_height // 2 + 2,
                x + pod_width // 2 - 2,
                y - pod_height // 2 + 8,
                fill=highlight_color,
                outline="",
                tags=("layer:seats", f"seat_highlight:{idx}"),
            )

            # Inner shadow for depth and luxury feel
            shadow_color = THEME.get("seat.shadow", "#1E293B")
            c.create_rectangle(
                x - pod_width // 2 + 3,
                y - pod_height // 2 + 3,
                x + pod_width // 2 - 3,
                y + pod_height // 2 - 3,
                fill="",
                outline=shadow_color,
                width=1,
                tags=("layer:seats", f"seat_shadow:{idx}"),
            )

            # Corner accent dots (luxury detail)
            accent_size = 3
            corner_color = THEME.get("seat.cornerAccent", seat_accent_color)
            for corner_x, corner_y in [
                (x - pod_width // 2 + 8, y - pod_height // 2 + 8),  # Top-left
                (x + pod_width // 2 - 8, y - pod_height // 2 + 8),  # Top-right
            ]:
                c.create_oval(
                    corner_x - accent_size // 2,
                    corner_y - accent_size // 2,
                    corner_x + accent_size // 2,
                    corner_y + accent_size // 2,
                    fill=corner_color,
                    outline="",
                    tags=("layer:seats", f"seat_accent:{idx}"),
                )

            # Enhanced luxury player display with decorative nameplate
            name = seat.get("name", f"Player {idx + 1}")
            position = seat.get("position", "")
            if (
                name != f"Player {idx + 1}" or position
            ):  # Show if player present or has position
                # Calculate font sizes proportional to card size (minimum 20px as requested)
                base_font_size = max(
                    20, int(pod_width * 0.15)
                )  # Scale with pod size, min 20px
                name_font_size = base_font_size
                stack_font_size = max(
                    18, int(base_font_size * 0.9)
                )  # Slightly smaller for stack

                # Luxury nameplate background (decorative frame)
                nameplate_width = pod_width - 8
                nameplate_height = 28
                nameplate_y = y - pod_height // 2 + 14

                # Nameplate background with theme-aware luxury styling
                nameplate_bg = THEME.get(
                    "player.nameplate.bg", _darken_color(seat_bg_color, 0.1)
                )
                nameplate_border = THEME.get("player.nameplate.border", seat_ring_color)

                c.create_rectangle(
                    x - nameplate_width // 2,
                    nameplate_y - nameplate_height // 2,
                    x + nameplate_width // 2,
                    nameplate_y + nameplate_height // 2,
                    fill=nameplate_bg,
                    outline=nameplate_border,
                    width=2,
                    tags=("layer:seats", f"nameplate_bg:{idx}"),
                )

                # Inner nameplate border for luxury depth
                c.create_rectangle(
                    x - nameplate_width // 2 + 2,
                    nameplate_y - nameplate_height // 2 + 2,
                    x + nameplate_width // 2 - 2,
                    nameplate_y + nameplate_height // 2 - 2,
                    fill="",
                    outline=_lighten_color(nameplate_border, 0.2),
                    width=1,
                    tags=("layer:seats", f"nameplate_inner:{idx}"),
                )

                # Format: "Player 6 (BB)" or "seat1 (UTG)" like screenshot
                display_name = name
                if position:
                    display_name = f"{name} ({position})"

                # Player name with enhanced luxury typography (20px minimum)
                c.create_text(
                    x,
                    nameplate_y,  # Centered in nameplate
                    text=display_name,
                    font=("Arial", name_font_size, "bold"),
                    fill=THEME.get("player.name", "#E5E7EB"),
                    tags=("layer:seats", f"name:{idx}"),
                )

                # Premium chip stack display (replaces text-based stack)
                stack = seat.get("stack", 0)
                if stack > 0:
                    # Position chip stack to the right of the nameplate for better visibility
                    stack_x = x + pod_width // 3
                    stack_y = y + pod_height // 2 - 15  # Slightly above bottom of pod

                    # Draw premium chip stack with theme-aware colors
                    chip_r = max(8, int(pod_width * 0.08))  # Scale chip size with pod
                    draw_chip_stack(
                        c,
                        stack_x,
                        stack_y,
                        stack,
                        THEME,
                        r=chip_r,
                        max_height=8,  # Limit height for UI space
                        tags=("layer:seats", f"chip_stack:{idx}"),
                    )

                    # Add stack amount text below chips for exact readability
                    stack_text_y = stack_y + 25
                    c.create_text(
                        stack_x,
                        stack_text_y,
                        text=f"${stack:,}",  # Exact amount with commas
                        font=("Arial", max(10, stack_font_size - 4), "normal"),
                        fill=THEME.get("text.secondary", "#B0B0B0"),  # Subtle text
                        tags=("layer:seats", f"stack_text:{idx}"),
                    )

                # Position indicator (in seat circle)
                position = seat.get("position", "")
                if position:
                    c.create_text(
                        x,
                        y - 8,
                        text=position,
                        font=FONTS.get("font.body", ("Arial", 9, "bold")),
                        fill=THEME.get("player.name", "#E5E7EB"),
                        tags=("layer:seats", f"position:{idx}"),
                    )

                # Professional hole cards with dynamic sizing based on player count
                cards = seat.get("cards", [])
                if cards and len(cards) >= 2:
                    # Dynamic card sizing: 2-3 players: 6%, 4-6 players: 5%, 7-9 players: 4%
                    # Use same active seat logic as community cards for consistency
                    active_seats = [s for s in seats_data if s.get("active", True)]
                    num_players = len(active_seats) if active_seats else len(seats_data)
                    if num_players <= 3:
                        card_scale = 0.06  # 6% of table size
                    elif num_players <= 6:
                        card_scale = 0.05  # 5% of table size
                    else:
                        card_scale = 0.04  # 4% of table size

                    # Calculate card dimensions based on table size
                    table_size = min(w, h)
                    card_width = int(table_size * card_scale * 0.7)  # Width ratio
                    card_height = int(card_width * 1.45)  # Maintain 1.45 aspect ratio
                    # No gap between hole cards - make them stick together like community cards

                    # Log card rendering details
                    print(
                        f"🃏 Rendering cards for seat {idx}: {cards}, size: {card_width}x{card_height}, players: {num_players}"
                    )

                    for i, card in enumerate(cards[:2]):  # Only show 2 hole cards
                        card_x = (
                            x - card_width + i * card_width
                        )  # Cards touching each other
                        card_y = y - 5  # Position cards inside the pod

                        # Token-driven card back colors that change with theme
                        card_back_bg = THEME.get(
                            "card.back.bg", THEME.get("board.cardBack", "#8B0000")
                        )
                        card_back_border = THEME.get(
                            "card.back.border", THEME.get("board.border", "#2F4F4F")
                        )
                        card_back_pattern = THEME.get("card.back.pattern", "#AA0000")

                        # Debug: Check if new tokens are available (remove after testing)
                        # if i == 0 and idx == 0:  # Only log once per render
                        #     print(f"🎨 Card back tokens: bg={card_back_bg}, border={card_back_border}, pattern={card_back_pattern}")

                        # Professional card back with theme integration
                        c.create_rectangle(
                            card_x,
                            card_y,
                            card_x + card_width,
                            card_y + card_height,
                            fill=card_back_bg,  # Theme-aware card back
                            outline=card_back_border,  # Theme-aware border
                            width=2,  # Professional border width
                            tags=("layer:seats", f"card:{idx}:{i}"),
                        )

                        # Inner border for depth
                        c.create_rectangle(
                            card_x + 2,
                            card_y + 2,
                            card_x + card_width - 2,
                            card_y + card_height - 2,
                            fill="",
                            outline=card_back_pattern,
                            width=1,
                            tags=("layer:seats", f"card_inner:{idx}:{i}"),
                        )

                        # Luxury crosshatch pattern (inspired by old UI luxury_crosshatch)
                        hatch_light = _lighten_color(card_back_bg, 0.15)
                        hatch_dark = _darken_color(card_back_bg, 0.1)

                        # Fine crosshatch grid across the card
                        spacing = max(
                            4, int(card_width // 8)
                        )  # Scale with card size, ensure int
                        for hx in range(
                            int(card_x + spacing),
                            int(card_x + card_width - spacing),
                            spacing,
                        ):
                            for hy in range(
                                int(card_y + spacing),
                                int(card_y + card_height - spacing),
                                spacing,
                            ):
                                # Diagonal crosshatch lines
                                line_size = spacing // 2
                                c.create_line(
                                    hx - line_size,
                                    hy - line_size,
                                    hx + line_size,
                                    hy + line_size,
                                    fill=hatch_light,
                                    width=1,
                                    tags=("layer:seats", f"card_hatch1:{idx}:{i}"),
                                )
                                c.create_line(
                                    hx - line_size,
                                    hy + line_size,
                                    hx + line_size,
                                    hy - line_size,
                                    fill=hatch_dark,
                                    width=1,
                                    tags=("layer:seats", f"card_hatch2:{idx}:{i}"),
                                )

                        # Central luxury emblem (dual symbols with enhanced styling)
                        symbol_font_size = max(
                            8, int(card_height * 0.25)
                        )  # Scale with card size
                        c.create_text(
                            card_x + card_width // 2,
                            card_y + card_height // 2 - 6,  # Upper symbol
                            text="♣",  # Club
                            fill=card_back_pattern,  # Theme-aware pattern color
                            font=("Arial", symbol_font_size, "bold"),
                            tags=("layer:seats", f"card_pattern_top:{idx}:{i}"),
                        )

                        c.create_text(
                            card_x + card_width // 2,
                            card_y + card_height // 2 + 6,  # Lower symbol
                            text="♦",  # Diamond
                            fill=card_back_pattern,  # Theme-aware pattern color
                            font=("Arial", symbol_font_size, "bold"),
                            tags=("layer:seats", f"card_pattern_bottom:{idx}:{i}"),
                        )

                        # Show actual card if revealed (not face down)
                        if (
                            card and card != "XX" and card != ""
                        ):  # "XX" means face down, "" means empty
                            try:
                                # Clear the card back pattern first
                                c.delete(f"card_pattern_top:{idx}:{i}")
                                c.delete(f"card_pattern_bottom:{idx}:{i}")

                                # Show face-up card with white background
                                c.create_rectangle(
                                    card_x,
                                    card_y,
                                    card_x + card_width,
                                    card_y + card_height,
                                    fill=THEME.get(
                                        "board.cardFaceFg", "#F8FAFC"
                                    ),  # White card face
                                    outline=THEME.get("board.border", "#0B1220"),
                                    width=2,
                                    tags=("layer:seats", f"card_face:{idx}:{i}"),
                                )

                                display_text, text_color = format_card_display(
                                    card, show_suits=True
                                )

                                # Calculate font size as 60% of card space (based on smaller dimension)
                                card_font_size = int(min(card_width, card_height) * 0.6)
                                card_font_size = max(
                                    8, min(card_font_size, 24)
                                )  # Clamp between 8-24px

                                c.create_text(
                                    card_x + card_width // 2,
                                    card_y + card_height // 2,
                                    text=display_text,
                                    font=("Arial", card_font_size, "bold"),
                                    fill=text_color,
                                    tags=("layer:seats", f"card_text:{idx}:{i}"),
                                )
                            except Exception as e:
                                print(f"🃏 Error displaying card {card}: {e}")
                                # Keep card back pattern if display fails
                                pass

                # Apply state-driven styling effects
                if theme_manager:
                    state_styler = theme_manager.get_state_styler()
                    if state_styler:
                        theme_id = theme_manager.get_current_theme_id()

                        # Determine player state for styling
                        player_state = None
                        if seat.get("winner", False):
                            player_state = "winner"
                        elif seat.get("showdown", False):
                            player_state = "showdown"
                        elif seat.get("all_in", False):
                            player_state = "allin"
                        elif seat.get("acting", False):
                            player_state = "active"
                        elif seat.get("folded", False):
                            player_state = "folded"

                        if player_state:
                            state_styler.apply_player_state_styling(
                                c,
                                idx,
                                player_state,
                                theme_id,
                                x,
                                y,
                                pod_width,
                                pod_height,
                            )
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
