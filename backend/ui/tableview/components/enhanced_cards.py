"""
Enhanced Card Graphics with Token-Driven Colors
Professional card rendering using the complete theme token system
"""

import math

class EnhancedCards:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    # Suit symbols
    SUIT_SYMBOLS = {
        'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'
    }
    
    def draw_card_face(self, canvas, x, y, rank, suit, w=58, h=82, tags=None):
        """Draw a face-up card with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Card colors from tokens
        bg = tokens.get("card.face.bg", "#F8F8FF")
        border = tokens.get("card.face.border", "#2F4F4F")
        pip_red = tokens.get("card.pip.red", "#DC2626")
        pip_black = tokens.get("card.pip.black", "#111827")
        
        # Determine suit color
        suit_color = pip_red if suit.lower() in ('h', 'd') else pip_black
        suit_symbol = self.SUIT_SYMBOLS.get(suit.lower(), '?')
        
        # Create tags
        card_tags = ["card_face"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle with rounded corners effect
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=border, width=1,
            tags=tuple(card_tags)
        )
        
        # Calculate font sizes based on card size
        rank_font_size = max(10, w // 5)
        suit_font_size = max(8, w // 6)
        center_font_size = max(14, w // 3)
        
        # Top-left rank and suit
        canvas.create_text(
            x + w//8, y + h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w//8, y + h//8 + rank_font_size + 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        # Center suit symbol (larger)
        canvas.create_text(
            x + w//2, y + h//2,
            text=suit_symbol, font=("Inter", center_font_size, "bold"),
            fill=suit_color, anchor="center", tags=tuple(card_tags)
        )
        
        # Bottom-right rank and suit (rotated appearance)
        canvas.create_text(
            x + w - w//8, y + h - h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w - w//8, y + h - h//8 - rank_font_size - 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_card_back(self, canvas, x, y, w=58, h=82, tags=None):
        """Draw a face-down card back with theme integration"""
        tokens = self.theme.get_all_tokens()
        
        # Card back colors from tokens
        bg = tokens.get("card.back.bg", "#7F1D1D")
        border = tokens.get("card.back.border", "#2F4F4F")
        pattern = tokens.get("card.back.pattern", "#991B1B")
        
        # Create tags
        card_tags = ["card_back"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        # Diamond lattice pattern
        step = max(6, w // 8)
        for i in range(0, w + step, step):
            # Diagonal lines creating diamond pattern
            canvas.create_line(
                x + i, y, x, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y, x + w, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + i, y + h, x, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y + h, x + w, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
        
        # Center decorative element
        center_size = min(w, h) // 4
        canvas.create_rectangle(
            x + w//2 - center_size//2, y + h//2 - center_size//4,
            x + w//2 + center_size//2, y + h//2 + center_size//4,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_community_board(self, canvas, tokens, slots=5, card_w=58, gap=8):
        """Draw community card area with token-driven styling"""
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        # Calculate board position
        x0, y0 = w * 0.5, h * 0.4
        total_w = slots * card_w + (slots - 1) * gap
        left = x0 - total_w / 2
        top = y0 - 4
        height = card_w * 0.2
        
        # Board colors from tokens
        slot_bg = tokens.get("board.slotBg", "#334155")
        border_color = tokens.get("board.border", "#475569")
        shadow_color = tokens.get("board.shadow", "#1E293B")
        
        # Clear previous board
        canvas.delete("board:underlay")
        
        # Shadow (offset slightly)
        canvas.create_rectangle(
            left - 8, top - 8, left + total_w + 12, top + height + 12,
            fill=shadow_color, outline="",
            tags=("board:underlay", "board_shadow")
        )
        
        # Main underlay
        canvas.create_rectangle(
            left - 10, top - 10, left + total_w + 10, top + height + 10,
            fill=slot_bg, outline=border_color, width=2,
            tags=("board:underlay", "board_main")
        )
        
        # Individual card slots
        for i in range(slots):
            slot_x = left + i * (card_w + gap)
            slot_y = top - card_w * 0.6
            
            # Slot outline
            canvas.create_rectangle(
                slot_x - 2, slot_y - 2, slot_x + card_w + 2, slot_y + card_w * 1.4 + 2,
                fill="", outline=border_color, width=1, stipple="gray25",
                tags=("board:underlay", f"slot_{i}")
            )
    
    def animate_card_flip(self, canvas, x, y, w, h, from_card, to_card, callback=None):
        """Animate card flip with token-aware colors"""
        flip_steps = 10
        
        def flip_step(step):
            if step >= flip_steps:
                if callback:
                    callback()
                return
            
            # Calculate flip progress (0 to 1)
            progress = step / flip_steps
            
            # Clear previous flip frame
            canvas.delete("card_flip")
            
            if progress < 0.5:
                # First half: shrink to nothing (show original card)
                scale = 1 - (progress * 2)
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if from_card and from_card != "XX":
                        rank, suit = from_card[:-1], from_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y, 
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y, 
                                          scaled_w, h, ["card_flip"])
            else:
                # Second half: grow from nothing (show new card)
                scale = (progress - 0.5) * 2
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if to_card and to_card != "XX":
                        rank, suit = to_card[:-1], to_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y,
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y,
                                          scaled_w, h, ["card_flip"])
            
            # Schedule next step
            canvas.after(40, lambda: flip_step(step + 1))
        
        flip_step(0)
    
    def add_card_glow(self, canvas, x, y, w, h, glow_type="soft"):
        """Add subtle glow effect around card"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get(f"glow.{glow_type}", tokens.get("a11y.focus", "#22C55E"))
        
        # Create glow effect with multiple rings
        for i in range(3):
            offset = (i + 1) * 2
            canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset,
                fill="", outline=glow_color, width=1,
                tags=("card_glow",)
            )
    
    def clear_card_effects(self, canvas):
        """Clear all card animation and effect elements"""
        canvas.delete("card_flip")
        canvas.delete("card_glow")
