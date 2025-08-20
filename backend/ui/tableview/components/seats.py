"""
Player Seats Component
Renders player seats, hole cards, and stack information on the poker table.
"""

import math
from typing import List, Dict, Any, Optional
from .sizing_utils import create_sizing_system

# Fallback chip graphics if premium_chips module is not available
try:
    from .premium_chips import draw_chip_stack
except Exception:
    def draw_chip_stack(canvas, x, y, denom_key="chip.gold", text="", r=14, tags=None):
        fill = "#D97706"  # goldish
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline="black", width=1, tags=tags or ())

# Fallback theme if theme manager is not available
THEME = {
    "seat.bg": "#1F2937",
    "seat.border": "#6B7280",
    "card.faceFg": "#F8FAFC",
    "card.border": "#0B1220",
    "card.back.bg": "#8B0000",
    "card.back.border": "#2F4F4F",
    "card.back.pattern": "#AA0000",
    "stack.bg": "#10B981",
    "stack.border": "#059669",
}

# Fallback fonts
FONTS = {
    "font.body": ("Arial", 12, "bold"),
    "font.small": ("Arial", 10, "bold"),
}


class Seats:
    """Renders player seats, hole cards, and stack information."""
    
    def __init__(self):
        self.sizing_system = None
        self._stack_chips = {}
        self._blind_elements = {}
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        """Render all player seats on the table."""
        # Get canvas and dimensions
        canvas = canvas_manager.canvas
        w, h = canvas_manager.size()
        
        if w <= 1 or h <= 1:
            return
        
        # Get seats data from state
        seats_data = state.get("seats", [])
        if not seats_data:
            return
        
        # Initialize sizing system if not already done
        if not self.sizing_system:
            num_players = len(seats_data)
            self.sizing_system = create_sizing_system(w, h, num_players)
        
        # Get card size from sizing system
        card_width, card_height = self.sizing_system.get_card_size()
        
        # Use consistent seat positions from geometry helper
        from ...state.selectors import get_seat_positions
        seat_positions = get_seat_positions(state, seat_count=len(seats_data), 
                                          canvas_width=w, canvas_height=h)
        
        print(f"🪑 Seats rendering: {len(seats_data)} seats, canvas: {w}x{h}")
        print(f"🪑 Using consistent seat positions from geometry helper")
        
        for idx, (x, y) in enumerate(seat_positions):
            print(f"🪑 Seat {idx} position: ({x}, {y}) - within canvas bounds: {0 <= x <= w and 0 <= y <= h}")
        
        # Check if any seats are outside canvas bounds
        seats_outside = [(i, x, y) for i, (x, y) in enumerate(seat_positions) if not (0 <= x <= w and 0 <= y <= h)]
        if seats_outside:
            print(f"⚠️ Warning: {len(seats_outside)} seats are outside canvas bounds:")
            for i, x, y in seats_outside:
                print(f"   Seat {i}: ({x}, {y}) - canvas size: {w}x{h}")
        
        # Render each seat
        for idx, seat in enumerate(seats_data):
            x, y = seat_positions[idx]
            
            print(f"🪑 Rendering seat {idx}: {seat.get('name', 'Unknown')} at ({x}, {y})")
            print(f"   Cards: {seat.get('cards', [])}")
            print(f"   Stack: {seat.get('stack', 0)}")
            print(f"   Position: {seat.get('position', '')}")
            
            # Render seat background
            self._render_seat_background(canvas, x, y, idx, seat)
            
            # Render player name
            self._render_player_name(canvas, x, y, idx, seat)
            
            # Render hole cards
            if seat.get('cards'):
                self._render_hole_cards(canvas, x, y, idx, seat, card_width, card_height)
            
            # Render player stack chips
            if seat.get('stack', 0) > 0:
                self._render_stack_chips(canvas, x, y, idx, seat)
            
            # Draw SB/BB indicators if applicable
            position = seat.get('position', '')
            if position in ['SB', 'BB']:
                self._draw_blind_indicator(canvas, x, y, position, seat, idx)
        
        print(f"🪑 Calculated positions for {len(seats_data)} seats on {w}x{h} canvas")
        print(f"🪑 Seat positions: {seat_positions}")
    
    def _render_seat_background(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render seat background circle."""
        # Get seat size from sizing system
        seat_size = self.sizing_system.get_chip_size('stack') * 2  # Seat is 2x stack chip size
        
        # Create seat background
        seat_bg = canvas.create_oval(
            x - seat_size, y - seat_size,
            x + seat_size, y + seat_size,
            fill=THEME.get("seat.bg", "#1F2937"),
            outline=THEME.get("seat.border", "#6B7280"),
            width=2,
            tags=("layer:seats", f"seat_bg:{idx}")
        )
        
        # Add seat number label
        label_y = y + seat_size + 15
        seat_label = canvas.create_text(
            x, label_y,
            text=f"Seat {idx + 1}",
            font=FONTS.get("font.small", ("Arial", 10, "bold")),
            fill="#FFFFFF",
            tags=("layer:seats", f"seat_label:{idx}"),
        )
    
    def _render_player_name(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render player name above the seat."""
        # Get text size from sizing system
        name_size = self.sizing_system.get_text_size('player_name')
        
        # Position name above seat
        name_y = y - 40
        
        name_text = canvas.create_text(
            x, name_y,
            text=seat.get('name', f'Player{idx + 1}'),
            font=("Arial", name_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:seats", f"player_name:{idx}")
        )
    
    def _render_hole_cards(self, canvas, x: int, y: int, idx: int, seat: dict, 
                          card_width: int, card_height: int):
        """Render player's hole cards."""
        cards = seat.get('cards', [])
        if not cards:
            return
        
        # Get text sizes from sizing system
        rank_size = self.sizing_system.get_text_size('card_rank')
        suit_size = self.sizing_system.get_text_size('card_suit')
        
        # Calculate card positions (side by side)
        card_spacing = self.sizing_system.get_spacing('card_gap')
        total_width = len(cards) * card_width + (len(cards) - 1) * card_spacing
        start_x = x - total_width // 2
        
        print(f"🃏 Rendering {len(cards)} hole cards for seat {idx} at position ({x}, {y})")
        
        for i, card in enumerate(cards):
            card_x = start_x + i * (card_width + card_spacing) + card_width // 2
            card_y = y + 35  # Further below the seat for better visibility
            
            # Create card background
            card_bg = canvas.create_rectangle(
                card_x - card_width // 2, card_y - card_height // 2,
                card_x + card_width // 2, card_y + card_height // 2,
                fill=THEME.get("card.faceFg", "#F8FAFC"),
                outline=THEME.get("card.border", "#0B1220"),
                width=2,
                tags=("layer:hole_cards", f"hole_card:{idx}:{i}")
            )
            
            # Parse card
            if len(card) >= 2:
                rank = card[0]
                suit = card[1]
                
                # Render rank
                rank_text = canvas.create_text(
                    card_x, card_y - card_height // 4,
                    text=rank,
                    font=("Arial", rank_size, "bold"),
                    fill="#000000",
                    tags=("layer:hole_cards", f"hole_card:{idx}:{i}", "card_rank")
                )
                
                # Render suit
                suit_text = canvas.create_text(
                    card_x, card_y + card_height // 4,
                    text=suit,
                    font=("Arial", suit_size, "bold"),
                    fill=self._get_suit_color(suit),
                    tags=("layer:hole_cards", f"hole_card:{idx}:{i}", "card_suit")
                )
        
        print(f"🃏 Rendering cards for seat {idx}: {cards}, size: {card_width}x{card_height}, players: {self.sizing_system.num_players}")
    
    def _render_stack_chips(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render player's stack chips."""
        stack_amount = seat.get('stack', 0)
        if stack_amount <= 0:
            return
        
        # Get chip size from sizing system
        chip_size = self.sizing_system.get_chip_size('stack')
        
        # Position stack below the seat
        stack_x = x
        stack_y = y + 50
        
        # Create stack background
        stack_bg = canvas.create_oval(
            stack_x - chip_size, stack_y - chip_size,
            stack_x + chip_size, stack_y + chip_size,
            fill=THEME.get("stack.bg", "#10B981"),
            outline=THEME.get("stack.border", "#059669"),
            width=2,
            tags=("layer:stacks", f"stack_bg:{idx}")
        )
        
        # Create stack amount text
        stack_text_size = self.sizing_system.get_text_size('stack_amount')
        stack_text = canvas.create_text(
            stack_x, stack_y,
            text=f"${stack_amount}",
            font=("Arial", stack_text_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:stacks", f"stack_text:{idx}")
        )
        
        # Store for cleanup
        self._stack_chips[idx] = [stack_bg, stack_text]
    
    def _draw_blind_indicator(self, canvas, x: int, y: int, position: str, seat: dict, idx: int):
        """Draw small blind or big blind indicator with chip graphics."""
        # Get chip size from sizing system
        chip_size = self.sizing_system.get_chip_size('bet')
        
        # Position blind indicator above the seat
        blind_x = x
        blind_y = y - 60
        
        # Get blind amount
        if position == 'SB':
            amount = seat.get('small_blind', 5)  # Default small blind
            color = "#F59E0B"  # Orange for small blind
            label = "SB"
        else:  # BB
            amount = seat.get('big_blind', 10)  # Default big blind
            color = "#EF4444"  # Red for big blind
            label = "BB"
        
        # Create blind chip background
        chip_bg = canvas.create_oval(
            blind_x - chip_size, blind_y - chip_size,
            blind_x + chip_size, blind_y + chip_size,
            fill=color,
            outline="#FFFFFF",
            width=2,
            tags=("layer:blinds", f"blind_chip:{idx}")
        )
        
        # Create blind amount text
        amount_text_size = self.sizing_system.get_text_size('blind_label')
        amount_text = canvas.create_text(
            blind_x, blind_y,
            text=f"${amount}",
            font=("Arial", amount_text_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:blinds", f"blind_amount:{idx}")
        )
        
        # Create blind label (SB/BB)
        label_y = blind_y - chip_size - 10
        label_text = canvas.create_text(
            blind_x, label_y,
            text=label,
            font=("Arial", amount_text_size, "bold"),
            fill=color,
            tags=("layer:blinds", f"blind_label:{idx}")
        )
        
        # Store for cleanup
        if idx not in self._blind_elements:
            self._blind_elements[idx] = {}
        self._blind_elements[idx].update({
            'chip_bg': chip_bg,
            'amount_text': amount_text,
            'label_text': label_text
        })
    
    def _get_suit_color(self, suit: str) -> str:
        """Get color for card suit."""
        if suit in ['♥', '♦']:
            return "#FF0000"  # Red for hearts and diamonds
        else:
            return "#000000"  # Black for clubs and spades
