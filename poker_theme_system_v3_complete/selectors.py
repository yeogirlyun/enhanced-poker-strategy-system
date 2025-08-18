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
        
    cx, cy = width // 2, int(height * 0.45)
    spacing = int(min(width, height) * 0.055)
    
    print(f"🃏 Board positions: center=({cx},{cy}), spacing={spacing}")
    
    # flop(3), turn(1), river(1)
    xs = [
        cx - 2 * spacing,
        cx - spacing,
        cx,
        cx + int(spacing * 1.5),
        cx + spacing * 3,
    ]
    positions = [(x, cy) for x in xs]
    print(f"🃏 Board card positions: {positions}")
    return positions


def get_dealer_position(state: Dict[str, Any]) -> int:
    dealer = state.get("dealer")
    try:
        return int(dealer)
    except Exception:
        return 0


