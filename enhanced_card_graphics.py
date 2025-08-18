"""
Enhanced Card Graphics System for Poker UI
Provides professional card rendering with proper sizing, colors, and theming
"""

class EnhancedCardGraphics:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    # Suit colors for better visibility
    SUIT_COLORS = {
        'h': '#DC143C',  # Hearts - Crimson Red
        'd': '#DC143C',  # Diamonds - Crimson Red  
        'c': '#000000',  # Clubs - Black
        's': '#000000'   # Spades - Black
    }
    
    # Suit symbols
    SUIT_SYMBOLS = {
        'h': '♥',  # Hearts
        'd': '♦',  # Diamonds
        'c': '♣',  # Clubs  
        's': '♠'   # Spades
    }
    
    def get_card_size(self, num_players, table_size):
        """Calculate card dimensions based on number of players"""
        if num_players <= 3:
            scale = 0.06  # 6% of table size
        elif num_players <= 6:
            scale = 0.05  # 5% of table size
        else:
            scale = 0.04  # 4% of table size
        
        card_width = int(table_size * scale * 0.7)
        card_height = int(card_width * 1.45)  # Standard poker card ratio
        return card_width, card_height
    
    def render_card_face(self, canvas, x, y, width, height, card_str):
        """Render a face-up playing card with enhanced visibility"""
        if not card_str or len(card_str) < 2:
            return self.render_card_back(canvas, x, y, width, height)
            
        rank = card_str[:-1]  # All but last character
        suit = card_str[-1].lower()  # Last character, lowercase
        
        # Card background (white/cream)
        bg_color = self.theme.get("card.face.bg", "#F8F8FF")
        border_color = self.theme.get("card.face.border", "#2F4F4F")
        
        # Main card rectangle with rounded corners effect
        canvas.create_rectangle(x, y, x + width, y + height,
                              fill=bg_color, outline=border_color, width=2,
                              tags="card_face")
        
        # Inner border for depth
        canvas.create_rectangle(x + 2, y + 2, x + width - 2, y + height - 2,
                              fill="", outline=border_color, width=1,
                              tags="card_face")
        
        # Suit color
        suit_color = self.SUIT_COLORS.get(suit, '#000000')
        suit_symbol = self.SUIT_SYMBOLS.get(suit, '?')
        
        # Calculate font sizes based on card size
        rank_font_size = max(12, width // 4)
        suit_font_size = max(10, width // 5)
        
        # Top-left rank and suit
        canvas.create_text(x + width//8, y + height//8,
                          text=rank, font=("Arial", rank_font_size, "bold"),
                          fill=suit_color, anchor="nw", tags="card_face")
        
        canvas.create_text(x + width//8, y + height//8 + rank_font_size + 2,
                          text=suit_symbol, font=("Arial", suit_font_size, "bold"),
                          fill=suit_color, anchor="nw", tags="card_face")
        
        # Center suit symbol (larger)
        center_font_size = max(16, width // 3)
        canvas.create_text(x + width//2, y + height//2,
                          text=suit_symbol, font=("Arial", center_font_size, "bold"),
                          fill=suit_color, anchor="center", tags="card_face")
        
        # Bottom-right rank and suit (rotated)
        canvas.create_text(x + width - width//8, y + height - height//8,
                          text=rank, font=("Arial", rank_font_size, "bold"),
                          fill=suit_color, anchor="se", tags="card_face")
        
        canvas.create_text(x + width - width//8, y + height - height//8 - rank_font_size - 2,
                          text=suit_symbol, font=("Arial", suit_font_size, "bold"),
                          fill=suit_color, anchor="se", tags="card_face")
    
    def render_card_back(self, canvas, x, y, width, height):
        """Render a face-down card back with theme integration"""
        # Base colors from theme
        back_color = self.theme.get("card.back.bg", "#8B0000")  # Dark Red
        border_color = self.theme.get("card.face.border", "#2F4F4F")
        pattern_color = self.theme.get("card.back.pattern", "#AA0000")
        
        # Main card rectangle
        canvas.create_rectangle(x, y, x + width, y + height,
                              fill=back_color, outline=border_color, width=2,
                              tags="card_back")
        
        # Inner border for depth
        canvas.create_rectangle(x + 2, y + 2, x + width - 2, y + height - 2,
                              fill="", outline=pattern_color, width=1,
                              tags="card_back")
        
        # Decorative pattern (dual symbols)
        symbol_size = max(8, width // 6)
        
        # Upper symbol (Club)
        canvas.create_text(x + width//2, y + height//2 - height//6,
                          text="♣", fill=pattern_color, 
                          font=("Arial", symbol_size, "bold"),
                          tags="card_back")
        
        # Lower symbol (Diamond)  
        canvas.create_text(x + width//2, y + height//2 + height//6,
                          text="♦", fill=pattern_color,
                          font=("Arial", symbol_size, "bold"),
                          tags="card_back")
        
        # Center decorative border
        center_size = width // 3
        canvas.create_rectangle(x + width//2 - center_size//2, y + height//2 - center_size//4,
                              x + width//2 + center_size//2, y + height//2 + center_size//4,
                              fill="", outline=pattern_color, width=1,
                              tags="card_back")
    
    def render_hole_cards(self, canvas, center_x, center_y, cards, num_players, table_size):
        """Render hole cards for a player with proper sizing and spacing"""
        if not cards or len(cards) < 2:
            return []
            
        card_width, card_height = self.get_card_size(num_players, table_size)
        card_gap = max(4, int(card_width * 0.2))  # Proportional gap
        
        card_elements = []
        
        for i, card in enumerate(cards[:2]):  # Only show 2 hole cards
            card_x = center_x - (card_width + card_gap//2) + i * (card_width + card_gap)
            card_y = center_y - card_height//2
            
            if card and card != "XX" and card != "":
                # Face-up card
                self.render_card_face(canvas, card_x, card_y, card_width, card_height, card)
            else:
                # Face-down card
                self.render_card_back(canvas, card_x, card_y, card_width, card_height)
                
        return card_elements
    
    def render_community_cards(self, canvas, positions, cards):
        """Render community cards on the board"""
        card_width = 44   # Standard community card width
        card_height = 64  # Standard community card height
        
        for idx, (x, y) in enumerate(positions):
            if idx < len(cards) and cards[idx]:
                # Show actual community card
                self.render_card_face(canvas, x - card_width//2, y - card_height//2,
                                    card_width, card_height, cards[idx])
            else:
                # Show empty card slot
                self.render_card_back(canvas, x - card_width//2, y - card_height//2,
                                    card_width, card_height)
    
    def format_card_display(self, card_str, show_suits=True):
        """Format card string for display with proper colors"""
        if not card_str or len(card_str) < 2:
            return "??", "#000000"
            
        rank = card_str[:-1]
        suit = card_str[-1].lower()
        
        if show_suits:
            suit_symbol = self.SUIT_SYMBOLS.get(suit, '?')
            display_text = f"{rank}{suit_symbol}"
        else:
            display_text = rank
            
        text_color = self.SUIT_COLORS.get(suit, '#000000')
        return display_text, text_color
