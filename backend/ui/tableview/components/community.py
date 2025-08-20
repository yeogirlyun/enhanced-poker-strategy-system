"""
Community Cards Component
Renders the community cards (flop, turn, river) on the poker table.
"""

import math
from typing import List, Tuple, Optional
from .sizing_utils import create_sizing_system


class Community:
    """Renders community cards on the poker table."""
    
    def __init__(self):
        self.community_cards = []
        self.sizing_system = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        """Render community cards on the table with professional poker app behavior."""
        # Get canvas and dimensions
        canvas = canvas_manager.canvas
        w, h = canvas_manager.size()
        
        if w <= 1 or h <= 1:
            return
        
        # Get board cards from state
        board_cards = state.get("board", [])
        
        # Professional poker behavior: Always show 5 card positions
        # Show card backs initially, reveal as game progresses
        street = state.get("street", "PREFLOP")
        
        # Determine how many cards to show face-up based on street
        if street == "PREFLOP":
            revealed_cards = 0
        elif street == "FLOP":
            revealed_cards = 3
        elif street == "TURN":
            revealed_cards = 4
        elif street in ["RIVER", "SHOWDOWN"]:
            revealed_cards = 5
        else:
            revealed_cards = len(board_cards)  # Fallback
        
        # Get seats data for player count
        seats_data = state.get("seats", [])
        num_players = len(seats_data) if seats_data else 6
        
        # Initialize sizing system if not already done
        if not self.sizing_system:
            self.sizing_system = create_sizing_system(w, h, num_players)
        
        # Get card size from sizing system
        card_w, card_h = self.sizing_system.get_card_size()
        
        # Calculate table center and board position
        cx, cy = w // 2, int(h * 0.45)  # Board above center
        
        # Calculate spacing between cards
        spacing = self.sizing_system.get_spacing('card_gap')
        
        # Always render 5 card positions (professional poker standard)
        total_cards = 5
        total_width = total_cards * card_w + (total_cards - 1) * spacing
        start_x = cx - total_width // 2
        
        # Store positions for other components
        positions = []
        
        print(f"🃏 Community cards positioning: center=({cx},{cy}), card_size={card_w}x{card_h}, spacing={spacing}")
        print(f"🃏 Street: {street}, revealed: {revealed_cards}/{total_cards}")
        
        # Render all 5 card positions
        for i in range(total_cards):
            card_x = start_x + i * (card_w + spacing) + card_w // 2
            card_y = cy
            
            # Store position for other components
            positions.append((card_x, card_y))
            
            # Determine what to show for this card position
            if i < revealed_cards and i < len(board_cards):
                # Show face-up card
                card = board_cards[i]
                self._render_card(canvas, card_x, card_y, card, card_w, card_h, face_up=True)
            else:
                # Show card back
                self._render_card_back(canvas, card_x, card_y, card_w, card_h)
        
        print(f"🃏 Community rendering: {total_cards} positions, {revealed_cards} revealed, canvas: {w}x{h}")
        print(f"🃏 Board positions on {w}x{h}: center=({cx},{cy}), card_size={card_w}x{card_h}, positions={positions}")
    
    def _render_card(self, canvas, x: int, y: int, card: str, card_w: int, card_h: int, face_up: bool = True):
        """Render a single community card face-up."""
        # Get text sizes from sizing system
        rank_size = self.sizing_system.get_text_size('card_rank')
        suit_size = self.sizing_system.get_text_size('card_suit')
        
        # Create card background
        card_bg = canvas.create_rectangle(
            x - card_w // 2, y - card_h // 2,
            x + card_w // 2, y + card_h // 2,
            fill="#FFFFFF",
            outline="#000000",
            width=2,
            tags=("layer:community", "community_card")
        )
        
        # Parse and render card face
        if len(card) >= 2:
            rank = card[0]
            suit = card[1]
            
            # Render rank
            rank_text = canvas.create_text(
                x, y - card_h // 4,
                text=rank,
                font=("Arial", rank_size, "bold"),
                fill="#000000",
                tags=("layer:community", "community_card", "card_rank")
            )
            
            # Render suit
            suit_text = canvas.create_text(
                x, y + card_h // 4,
                text=suit,
                font=("Arial", suit_size, "bold"),
                fill=self._get_suit_color(suit),
                tags=("layer:community", "community_card", "card_suit")
            )
    
    def _render_card_back(self, canvas, x: int, y: int, card_w: int, card_h: int):
        """Render a card back (professional poker style)."""
        # Create card background with darker color for back
        card_bg = canvas.create_rectangle(
            x - card_w // 2, y - card_h // 2,
            x + card_w // 2, y + card_h // 2,
            fill="#8B0000",  # Dark red background
            outline="#000000",
            width=2,
            tags=("layer:community", "community_card_back")
        )
        
        # Add card back pattern (simple diamond pattern)
        # Inner border
        inner_border = canvas.create_rectangle(
            x - card_w // 2 + 4, y - card_h // 2 + 4,
            x + card_w // 2 - 4, y + card_h // 2 - 4,
            fill="",
            outline="#AA0000",
            width=1,
            tags=("layer:community", "community_card_back")
        )
        
        # Center diamond
        diamond_size = min(card_w, card_h) // 4
        canvas.create_polygon(
            x, y - diamond_size,  # Top
            x + diamond_size, y,  # Right
            x, y + diamond_size,  # Bottom
            x - diamond_size, y,  # Left
            fill="#AA0000",
            outline="#FFFFFF",
            width=1,
            tags=("layer:community", "community_card_back")
        )
    
    def _get_suit_color(self, suit: str) -> str:
        """Get color for card suit."""
        if suit in ['♥', '♦']:
            return "#FF0000"  # Red for hearts and diamonds
        else:
            return "#000000"  # Black for clubs and spades

