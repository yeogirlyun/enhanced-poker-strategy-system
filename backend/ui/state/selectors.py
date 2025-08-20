"""
Selectors for Hands Review Session - Pure functions for deriving UI state
All selectors must be pure and memoized where appropriate.
"""

from typing import Dict, Any, List, Optional
import math


def current_street(state: Dict[str, Any]) -> str:
    """Get current street from state."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return enhanced_rpgw.get('current_street', 'PREFLOP')


def current_actor(state: Dict[str, Any]) -> Optional[str]:
    """Get current actor (player_uid) from state."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return enhanced_rpgw.get('current_actor')


def legal_actions(state: Dict[str, Any]) -> List[str]:
    """Get legal actions for current state."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return enhanced_rpgw.get('legal_actions', [])


def pot_amount(state: Dict[str, Any]) -> int:
    """Get current pot amount."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return enhanced_rpgw.get('pot_amount', 0)


def seat_view(state: Dict[str, Any], uid: str) -> Dict[str, Any]:
    """Get seat view data for a specific player."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    seats = enhanced_rpgw.get('seats', [])
    
    for seat in seats:
        if seat.get('player_uid') == uid:
            return {
                'name': seat.get('name', 'Unknown'),
                'stack': seat.get('current_stack', 0),
                'bet': seat.get('current_bet', 0),
                'folded': seat.get('folded', False),
                'acting': seat.get('acting', False),
                'cards': seat.get('cards', [])
            }
    
    return {
        'name': 'Unknown',
        'stack': 0,
        'bet': 0,
        'folded': False,
        'acting': False,
        'cards': []
    }


def board_cards(state: Dict[str, Any]) -> List[str]:
    """Get current board cards."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return enhanced_rpgw.get('board', [])


def review_progress(state: Dict[str, Any]) -> Dict[str, Any]:
    """Get hands review progress information."""
    review = state.get('review', {})
    return {
        'current_step': review.get('current_step', 0),
        'total_steps': review.get('total_steps', 0),
        'current_hand': review.get('loaded_hand'),
        'status': review.get('status', 'idle')
    }


def enhanced_rpgw_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Get complete Enhanced RPGW state for rendering."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return {
        'table': enhanced_rpgw.get('table', {}),
        'pot': enhanced_rpgw.get('pot', {}),
        'seats': enhanced_rpgw.get('seats', []),
        'board': enhanced_rpgw.get('board', []),
        'dealer': enhanced_rpgw.get('dealer', {}),
        'action': enhanced_rpgw.get('action', {}),
        'replay': enhanced_rpgw.get('replay', {})
    }


def can_execute_action(state: Dict[str, Any]) -> bool:
    """Check if an action can be executed."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    return (
        enhanced_rpgw.get('execution_status') != 'pending' and
        enhanced_rpgw.get('current_action') is not None
    )


def can_go_next(state: Dict[str, Any]) -> bool:
    """Check if can go to next action."""
    review = state.get('review', {})
    current_step = review.get('current_step', 0)
    total_steps = review.get('total_steps', 0)
    return current_step < total_steps - 1


def can_go_prev(state: Dict[str, Any]) -> bool:
    """Check if can go to previous action."""
    review = state.get('review', {})
    current_step = review.get('current_step', 0)
    return current_step > 0


def is_hand_loaded(state: Dict[str, Any]) -> bool:
    """Check if a hand is currently loaded."""
    review = state.get('review', {})
    return review.get('loaded_hand') is not None


def get_num_seats(state: Dict[str, Any]) -> int:
    """Get number of seats from state."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    seats = enhanced_rpgw.get('seats', [])
    return len(seats) if seats else 6  # Default to 6 seats


def get_seat_positions(
    state: Dict[str, Any], 
    seat_count: Optional[int] = None,
    canvas_width: Optional[int] = None,
    canvas_height: Optional[int] = None
) -> List[tuple]:
    """Get seat positions for rendering. Returns list of (x, y) coordinates."""
    if seat_count is None:
        seat_count = get_num_seats(state)
    
    # Use actual canvas dimensions if provided, otherwise use reasonable defaults
    if canvas_width and canvas_height:
        w, h = canvas_width, canvas_height
        cx, cy = w // 2, int(h * 0.52)  # Center of table
        radius = int(min(w, h) * 0.25)   # Seat radius - same as seats component
    else:
        # Fallback to reasonable defaults
        radius = 200
        cx, cy = 400, 300
    
    # Calculate positions for seats in a circle
    # Start from top (-90 degrees) and distribute evenly
    positions = []
    for i in range(seat_count):
        # Calculate angle: start from top (-90°) and distribute evenly
        theta = -math.pi / 2 + (2 * math.pi * i) / seat_count
        
        # Calculate position on the circle
        x = cx + int(radius * math.cos(theta))
        y = cy + int(radius * math.sin(theta))
        
        positions.append((x, y))
        
        # Debug: Log the positioning calculation
        print(f"🎯 Seat {i} positioning: angle={theta:.2f}° -> ({x}, {y})")
    
    return positions


def get_dealer_position(state: Dict[str, Any]) -> int:
    """Get dealer position from state."""
    enhanced_rpgw = state.get('enhanced_rpgw', {})
    dealer_info = enhanced_rpgw.get('dealer', {})
    return dealer_info.get('position', 0)  # Default to seat 0


