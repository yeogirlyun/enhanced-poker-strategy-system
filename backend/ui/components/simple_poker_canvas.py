#!/usr/bin/env python3
"""
Simple Poker Canvas

This canvas renders the poker table exactly like the practice session UI.
It's purely visual rendering - no game logic, just data display.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
import math

# Import the display step
from .simple_hands_data_renderer import DisplayStep


class SimplePokerCanvas(tk.Canvas):
    """
    Simple poker canvas that renders the table exactly like practice session.
    
    This canvas:
    - Draws player seats in the same positions
    - Shows cards, chips, and bets exactly like RPGW
    - Displays board cards in the center
    - Shows pot amount
    - NO game logic, just visual rendering
    """

    def __init__(self, parent, **kwargs):
        """Initialize the canvas."""
        super().__init__(parent, **kwargs)
        
        # Canvas setup
        self.configure(
            bg='#2d5016',  # Dark green felt
            highlightthickness=0,
            relief='flat'
        )
        
        # Table dimensions
        self.table_width = 800
        self.table_height = 600
        self.center_x = self.table_width // 2
        self.center_y = self.table_height // 2
        
        # Player seat positions (6-handed)
        self.seat_positions = self._calculate_seat_positions()
        
        # Visual elements
        self.player_seats = {}
        self.board_cards = []
        self.pot_label = None
        self.dealer_button = None
        
        # Bind resize event
        self.bind('<Configure>', self._on_resize)
        
        # Initial draw
        self._draw_table()

    def _calculate_seat_positions(self) -> List[tuple]:
        """Calculate player seat positions around the table."""
        positions = []
        radius = 200  # Distance from center
        
        # 6-handed positions (clockwise from top)
        angles = [90, 30, -30, -90, -150, 150]  # Degrees
        
        for angle in angles:
            rad = math.radians(angle)
            x = self.center_x + radius * math.cos(rad)
            y = self.center_y + radius * math.sin(rad)
            positions.append((int(x), int(y)))
        
        return positions

    def _on_resize(self, event):
        """Handle canvas resize."""
        if event.width > 1 and event.height > 1:
            self.table_width = event.width
            self.table_height = event.height
            self.center_x = self.table_width // 2
            self.center_y = self.table_height // 2
            
            # Recalculate positions and redraw
            self.seat_positions = self._calculate_seat_positions()
            self._draw_table()

    def _draw_table(self):
        """Draw the poker table."""
        # Clear canvas
        self.delete("all")
        
        # Draw table outline
        self._draw_table_outline()
        
        # Draw pot area
        self._draw_pot_area()
        
        # Draw dealer button area
        self._draw_dealer_button_area()
        
        # Draw community card area
        self._draw_community_card_area()

    def _draw_table_outline(self):
        """Draw the poker table outline."""
        # Main table (oval)
        table_width = min(self.table_width - 40, 700)
        table_height = min(self.table_height - 40, 500)
        
        x1 = self.center_x - table_width // 2
        y1 = self.center_y - table_height // 2
        x2 = self.center_x + table_width // 2
        y2 = self.center_y + table_height // 2
        
        # Table felt
        self.create_oval(
            x1, y1, x2, y2,
            fill='#2d5016',
            outline='#1a3d0f',
            width=3,
            tags="table_outline"
        )
        
        # Table border
        self.create_oval(
            x1 - 5, y1 - 5, x2 + 5, y2 + 5,
            outline='#8b4513',
            width=8,
            tags="table_border"
        )

    def _draw_pot_area(self):
        """Draw the pot area in the center."""
        pot_x = self.center_x
        pot_y = self.center_y + 20
        
        # Pot circle
        self.create_oval(
            pot_x - 30, pot_y - 20,
            pot_x + 30, pot_y + 20,
            fill='#8b4513',
            outline='#654321',
            width=2,
            tags="pot_area"
        )
        
        # Pot label
        self.pot_label = self.create_text(
            pot_x, pot_y,
            text="$0",
            fill='white',
            font=('Arial', 12, 'bold'),
            tags="pot_label"
        )

    def _draw_dealer_button_area(self):
        """Draw the dealer button area."""
        # Dealer button will be positioned when rendering players
        pass

    def _draw_community_card_area(self):
        """Draw the community card area."""
        # Community card area in center
        card_area_x = self.center_x
        card_area_y = self.center_y - 40
        
        # Card area background
        self.create_rectangle(
            card_area_x - 80, card_area_y - 15,
            card_area_x + 80, card_area_y + 15,
            fill='#1a3d0f',
            outline='#8b4513',
            width=2,
            tags="card_area"
        )

    def render_step(self, step: DisplayStep):
        """Render a specific step of the hand."""
        if not step:
            return
        
        # Clear previous player elements
        self._clear_player_elements()
        
        # Render players
        self._render_players(step.players, step.dealer_position, step.action_player)
        
        # Render board cards
        self._render_board_cards(step.board_cards)
        
        # Update pot
        self._update_pot(step.pot_amount)
        
        # Render dealer button
        self._render_dealer_button(step.dealer_position)

    def _clear_player_elements(self):
        """Clear all player-related elements."""
        for tags in ["player_seat", "player_name", "player_cards", "player_stack", 
                    "player_bet", "dealer_button"]:
            self.delete(tags)

    def _render_players(self, players: List[Dict], dealer_position: int, 
                       action_player: Optional[int]):
        """Render all players at their seats."""
        for i, player in enumerate(players):
            if i < len(self.seat_positions):
                x, y = self.seat_positions[i]
                self._render_player_seat(i, player, x, y, dealer_position, action_player)

    def _render_player_seat(self, player_index: int, player: Dict, x: int, y: int,
                           dealer_position: int, action_player: Optional[int]):
        """Render a single player seat."""
        # Player seat background
        seat_radius = 35
        seat_color = '#4a7c59'  # Standard seat color
        
        # Highlight if it's the action player
        if action_player == player_index:
            seat_color = '#ffd700'  # Gold for action player
        
        # Highlight if it's the dealer
        if dealer_position == player_index:
            seat_color = '#ff6b6b'  # Red for dealer
        
        self.create_oval(
            x - seat_radius, y - seat_radius,
            x + seat_radius, y + seat_radius,
            fill=seat_color,
            outline='#2d5016',
            width=3,
            tags="player_seat"
        )
        
        # Player name
        name = player.get('name', f'Player {player_index}')
        self.create_text(
            x, y - 50,
            text=name,
            fill='white',
            font=('Arial', 10, 'bold'),
            tags="player_name"
        )
        
        # Position label
        position = player.get('position', '')
        if position:
            self.create_text(
                x, y - 35,
                text=f"({position})",
                fill='#cccccc',
                font=('Arial', 8),
                tags="player_name"
            )
        
        # Player cards
        cards = player.get('cards', [])
        if cards:
            self._render_player_cards(player_index, cards, x, y)
        
        # Player stack
        stack = player.get('stack', 0.0)
        if stack > 0:
            self._render_player_stack(player_index, stack, x, y)
        
        # Player bet
        bet = player.get('bet', 0.0)
        if bet > 0:
            self._render_player_bet(player_index, bet, x, y)
        
        # Folded indicator
        if player.get('folded', False):
            self._render_folded_indicator(player_index, x, y)

    def _render_player_cards(self, player_index: int, cards: List[str], x: int, y: int):
        """Render player's hole cards."""
        if not cards:
            return
        
        # Card dimensions
        card_width = 25
        card_height = 35
        
        for i, card in enumerate(cards):
            if card and card != "**":
                # Calculate card position
                card_x = x - 15 + (i * 15)
                card_y = y + 20
                
                # Card background
                self.create_rectangle(
                    card_x, card_y,
                    card_x + card_width, card_y + card_height,
                    fill='white',
                    outline='black',
                    width=1,
                    tags="player_cards"
                )
                
                # Card text
                self.create_text(
                    card_x + card_width // 2, card_y + card_height // 2,
                    text=card,
                    fill='black',
                    font=('Arial', 8, 'bold'),
                    tags="player_cards"
                )

    def _render_player_stack(self, player_index: int, stack: float, x: int, y: int):
        """Render player's stack."""
        stack_text = f"${stack:.0f}"
        self.create_text(
            x, y + 60,
            text=stack_text,
            fill='#90ee90',
            font=('Arial', 9, 'bold'),
            tags="player_stack"
        )

    def _render_player_bet(self, player_index: int, bet: float, x: int, y: int):
        """Render player's bet."""
        if bet <= 0:
            return
        
        bet_text = f"${bet:.0f}"
        
        # Bet chip background
        chip_x = x
        chip_y = y + 45
        
        self.create_oval(
            chip_x - 20, chip_y - 12,
            chip_x + 20, chip_y + 12,
            fill='#ffd700',
            outline='#b8860b',
            width=2,
            tags="player_bet"
        )
        
        # Bet amount
        self.create_text(
            chip_x, chip_y,
            text=bet_text,
            fill='black',
            font=('Arial', 8, 'bold'),
            tags="player_bet"
        )

    def _render_folded_indicator(self, player_index: int, x: int, y: int):
        """Render folded indicator for a player."""
        # Folded text
        self.create_text(
            x, y + 80,
            text="FOLDED",
            fill='#ff6b6b',
            font=('Arial', 10, 'bold'),
            tags="player_seat"
        )

    def _render_board_cards(self, board_cards: List[str]):
        """Render community board cards."""
        # Clear previous board cards
        self.delete("board_cards")
        
        if not board_cards:
            return
        
        # Card dimensions
        card_width = 30
        card_height = 40
        
        # Calculate starting position
        total_width = len(board_cards) * card_width + (len(board_cards) - 1) * 5
        start_x = self.center_x - total_width // 2
        
        for i, card in enumerate(board_cards):
            if card and card != "**":
                # Calculate card position
                card_x = start_x + i * (card_width + 5)
                card_y = self.center_y - 40
                
                # Card background
                self.create_rectangle(
                    card_x, card_y,
                    card_x + card_width, card_y + card_height,
                    fill='white',
                    outline='black',
                    width=2,
                    tags="board_cards"
                )
                
                # Card text
                self.create_text(
                    card_x + card_width // 2, card_y + card_height // 2,
                    text=card,
                    fill='black',
                    font=('Arial', 10, 'bold'),
                    tags="board_cards"
                )

    def _update_pot(self, pot_amount: float):
        """Update the pot amount display."""
        if self.pot_label:
            self.itemconfig(self.pot_label, text=f"${pot_amount:.0f}")

    def _render_dealer_button(self, dealer_position: int):
        """Render the dealer button."""
        if dealer_position < 0 or dealer_position >= len(self.seat_positions):
            return
        
        # Get dealer seat position
        dealer_x, dealer_y = self.seat_positions[dealer_position]
        
        # Position dealer button above the seat
        button_x = dealer_x
        button_y = dealer_y - 70
        
        # Dealer button (white circle with "D")
        self.create_oval(
            button_x - 12, button_y - 12,
            button_x + 12, button_y + 12,
            fill='white',
            outline='black',
            width=2,
            tags="dealer_button"
        )
        
        # Dealer button text
        self.create_text(
            button_x, button_y,
            text="D",
            fill='black',
            font=('Arial', 10, 'bold'),
            tags="dealer_button"
        )
