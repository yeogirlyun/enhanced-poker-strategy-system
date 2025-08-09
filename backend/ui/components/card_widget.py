#!/usr/bin/env python3
"""
Card Widget

A standalone card widget for displaying playing cards.
Moved to separate module to avoid circular imports.
"""

import tkinter as tk


class CardWidget(tk.Canvas):
    """A custom widget to display a single, styled playing card."""
    def __init__(self, parent, width=50, height=70):
        super().__init__(parent, width=width, height=height, highlightthickness=1, highlightbackground="black", bg="white")
        self.width, self.height = width, height
        
        # Ensure canvas is properly configured for drawing
        self.config(width=width, height=height)
        
        # Initialize with card back
        self._draw_card_back()

    def set_card(self, card_str, is_folded=False):
        # Store the current card string
        self.current_card_str = card_str
        
        print(f"🎴 CardWidget.set_card called with: '{card_str}', is_folded={is_folded}")
        
        self.delete("all") # Clear previous drawing
        
        # Handle different card states
        if is_folded:
            # Player has folded - show dark folded card back
            self._draw_card_back(is_folded=True)
        elif not card_str or card_str == "**":
            # Card is hidden/empty - show transparent/empty space instead of card back
            self._draw_empty_card()
        else:
            # Valid card - show the actual card
            self.config(bg="white")
            self._draw_card_content(card_str)
        
        # Force update to ensure the drawing is applied
        self.update()

    def _draw_card_content(self, card_str):
        """Draw the card content (rank and suit) on the canvas."""
        if not card_str or len(card_str) < 2:
            print(f"🎴 Invalid card string: '{card_str}'")
            return
            
        rank, suit = card_str[0], card_str[1]
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_colors = {'h': '#c0392b', 'd': '#c0392b', 'c': 'black', 's': 'black'}
        color = suit_colors.get(suit, "black")
        
        print(f"🎴 Drawing card: rank='{rank}', suit='{suit}', color='{color}'")
        
        # Use larger, clearer fonts
        self.create_text(self.width / 2, self.height / 2 - 5, text=rank, font=("Helvetica", 22, "bold"), fill=color)
        self.create_text(self.width / 2, self.height / 2 + 18, text=suit_symbols.get(suit, ""), font=("Helvetica", 16), fill=color)

    def _draw_card_back(self, is_folded=False):
        """Draws a professional-looking checkerboard pattern for the card back."""
        # Clear any existing content
        self.delete("all")
        
        if is_folded:
            # Draw folded card back - dark gray with no border
            dark_gray = "#404040"  # Dark gray for folded cards
            self.config(bg=dark_gray)
            
            # Draw a simple dark gray card with no border
            self.create_rectangle(0, 0, self.width, self.height, 
                                fill=dark_gray, outline="")
        else:
            # Define colors for regular card back
            dark_red = "#a51d2d"
            light_red = "#c0392b"
            border_color = "#8b0000"
            
            # Set the background color
            self.config(bg=dark_red)
            
            # Draw the border first
            self.create_rectangle(2, 2, self.width-2, self.height-2, 
                                fill=dark_red, outline=border_color, width=2)
            
            # Draw the checkerboard pattern with larger squares for better visibility
            square_size = 8
            for y in range(4, self.height-4, square_size):
                for x in range(4, self.width-4, square_size):
                    # Create alternating pattern
                    color = light_red if (x // square_size + y // square_size) % 2 == 0 else dark_red
                    self.create_rectangle(x, y, x + square_size, y + square_size, 
                                       fill=color, outline="")
            
            # Add a subtle center design element
            center_x, center_y = self.width // 2, self.height // 2
            self.create_oval(center_x-8, center_y-8, center_x+8, center_y+8, 
                            fill=light_red, outline=border_color, width=1)
    
    def _draw_empty_card(self):
        """Draw an empty/transparent card space (no visible card)."""
        # Clear any existing content
        self.delete("all")
        
        # Set transparent/matching background
        parent_bg = "#1a1a1a"  # Match the player pod background
        self.config(bg=parent_bg)
        
        # Draw a subtle dashed border to indicate card space exists
        self.create_rectangle(2, 2, self.width-2, self.height-2, 
                            fill="", outline="#404040", width=1, dash=(3, 3))
    

    def set_folded(self):
        """Shows the card as folded (empty)."""
        self.set_card("", is_folded=True)
