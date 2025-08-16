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
    if width <= 1 or height <= 1:
        return []
    n = seat_count if seat_count is not None else get_num_seats(state)
    # Circle around center, radius relative to table size
    cx, cy = width // 2, int(height * 0.52)
    radius = int(min(width, height) * 0.36)
    positions: List[Tuple[int, int]] = []
    # Start from top and proceed clockwise
    for i in range(n):
        theta = -math.pi / 2 + (2 * math.pi * i) / n
        x = cx + int(radius * math.cos(theta))
        y = cy + int(radius * math.sin(theta))
        positions.append((x, y))
    return positions


def get_board_positions(state: Dict[str, Any]) -> List[Tuple[int, int]]:
    width, height = get_table_dim(state)
    if width <= 1 or height <= 1:
        return []
    cx, cy = width // 2, int(height * 0.45)
    spacing = int(min(width, height) * 0.055)
    # flop(3), turn(1), river(1)
    xs = [
        cx - 2 * spacing,
        cx - spacing,
        cx,
        cx + int(spacing * 1.5),
        cx + spacing * 3,
    ]
    return [(x, cy) for x in xs]


def get_dealer_position(state: Dict[str, Any]) -> int:
    dealer = state.get("dealer")
    try:
        return int(dealer)
    except Exception:
        return 0


