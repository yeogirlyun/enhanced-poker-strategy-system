from typing import Dict, Any, List, Tuple
import math


def get_table_dim(state: Dict[str, Any]) -> Tuple[int, int]:
    table = state.get("table", {})
    dim = table.get("dim", (0, 0))
    return int(dim[0] or 0), int(dim[1] or 0)


def get_num_seats(state: Dict[str, Any], default: int = 6) -> int:
    seats = state.get("seats") or []
    if isinstance(seats, list) and len(seats) > 0:
        return len(seats)
    return default


def get_seat_positions(
    state: Dict[str, Any],
    seat_count: int | None = None,
) -> List[Tuple[int, int]]:
    width, height = get_table_dim(state)
    
    # Use fallback dimensions if table not sized yet  
    if width <= 1 or height <= 1:
        # Try to get actual canvas size from components if available
        width, height = 1200, 800  # Better default for modern displays
        print(f"🎯 Using fallback table size: {width}x{height}")
    
    n = seat_count if seat_count is not None else get_num_seats(state)
    if n <= 0:
        n = 6  # Default to 6 seats
        
    # Circle around center, radius relative to table size
    cx, cy = width // 2, int(height * 0.52)
    radius = int(min(width, height) * 0.36)
    positions: List[Tuple[int, int]] = []
    
    print(f"🎯 Seat positions: center=({cx},{cy}), radius={radius}, seats={n}")
    
    # Start from top and proceed clockwise
    for i in range(n):
        theta = -math.pi / 2 + (2 * math.pi * i) / n
        x = cx + int(radius * math.cos(theta))
        y = cy + int(radius * math.sin(theta))
        positions.append((x, y))
        
    return positions


def get_board_positions(state: Dict[str, Any]) -> List[Tuple[int, int]]:
    width, height = get_table_dim(state)
    
    # Use fallback dimensions if table not sized yet
    if width <= 1 or height <= 1:
        width, height = 800, 600  # Default poker table size
    
    # Get number of players to match hole card sizing (same logic as community.py)
    seats_data = state.get("seats", [])
    num_players = len([s for s in seats_data if s.get("active", False)]) or 6
    
    # Use same card sizing logic as hole cards for consistency
    if num_players <= 3:
        card_scale = 0.06  # 6% of table size
    elif num_players <= 6:
        card_scale = 0.05  # 5% of table size
    else:
        card_scale = 0.04  # 4% of table size
    
    table_size = min(width, height)
    card_w = int(table_size * card_scale * 0.7)   # Same width ratio as hole cards
    
    # Center community cards with no gaps (compact layout) - same as community.py
    cx, cy = width // 2, int(height * 0.45)  # Centered horizontally, 45% down vertically
    total_width = 5 * card_w  # 5 cards touching each other
    start_x = cx - total_width // 2 + card_w // 2  # Start position for first card
    
    positions = [(start_x + i * card_w, cy) for i in range(5)]
    print(f"🃏 Board positions (selector): center=({cx},{cy}), card_size={card_w}, positions={positions}")
    return positions


def get_dealer_position(state: Dict[str, Any]) -> int:
    dealer = state.get("dealer")
    try:
        return int(dealer)
    except Exception:
        return 0


