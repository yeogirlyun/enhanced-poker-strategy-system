from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..state.selectors import get_seat_positions


def pot_center(canvas_width: int, canvas_height: int) -> Tuple[int, int]:
    """Standard pot center used across sessions (slightly below center)."""
    return canvas_width // 2, int(canvas_height * 0.58)


def actor_seat_xy(display_state: Dict[str, Any], actor_uid: str,
                  canvas_width: int, canvas_height: int) -> Tuple[int, int]:
    seats: List[Dict[str, Any]] = display_state.get('seats', [])
    positions = get_seat_positions(
        display_state,
        seat_count=len(seats),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )
    idx = next(
        (i for i, s in enumerate(seats) if s.get('player_uid') == actor_uid),
        -1,
    )
    if 0 <= idx < len(positions):
        x, y = positions[idx]
        return int(x), int(y)
    return canvas_width // 2, canvas_height // 2


