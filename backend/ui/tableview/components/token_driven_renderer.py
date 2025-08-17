"""
Token-Driven Renderer Integration
Coordinates all enhanced components with the token system
"""

import math
from .table_center import TableCenter
from .enhanced_cards import EnhancedCards
from .chip_animations import ChipAnimations
from .micro_interactions import MicroInteractions

class TokenDrivenRenderer:
    """
    Main coordinator for all token-driven UI components
    Provides a unified interface for rendering poker table elements
    """
    
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
        # Initialize all enhanced components
        self.table_center = TableCenter(theme_manager)
        self.enhanced_cards = EnhancedCards(theme_manager)
        self.chip_animations = ChipAnimations(theme_manager)
        self.micro_interactions = MicroInteractions(theme_manager)
        
    def render_complete_table(self, canvas, state):
        """Render complete poker table with all enhancements"""
        # Clear any existing elements
        self.clear_all_effects(canvas)
        
        # Get current tokens
        tokens = self.theme.get_all_tokens()
        
        # 1. Render table center pattern
        self.table_center.render(canvas, state)
        
        # 2. Render community board area
        self.enhanced_cards.draw_community_board(canvas, tokens)
        
        # 3. Render community cards if present
        community_cards = state.get("board", [])
        if community_cards:
            self._render_community_cards(canvas, community_cards, tokens)
        
        # 4. Render player seats with enhanced cards
        seats_data = state.get("seats", [])
        if seats_data:
            self._render_enhanced_seats(canvas, seats_data, tokens)
        
        # 5. Render pot with chip stacks
        pot_amount = state.get("pot", {}).get("total", 0)
        if pot_amount > 0:
            self._render_enhanced_pot(canvas, pot_amount, tokens)
    
    def _render_community_cards(self, canvas, cards, tokens):
        """Render community cards with enhanced graphics"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        board_x, board_y = w * 0.5, h * 0.4
        
        card_w, card_h = 58, 82
        gap = 8
        total_w = 5 * card_w + 4 * gap
        start_x = board_x - total_w / 2
        
        for i in range(5):
            card_x = start_x + i * (card_w + gap)
            card_y = board_y - card_h / 2
            
            if i < len(cards) and cards[i]:
                # Render face-up community card
                rank, suit = cards[i][:-1], cards[i][-1]
                self.enhanced_cards.draw_card_face(
                    canvas, card_x, card_y, rank, suit, card_w, card_h,
                    tags=[f"community_card_{i}"]
                )
            else:
                # Render empty slot
                self.enhanced_cards.draw_card_back(
                    canvas, card_x, card_y, card_w, card_h,
                    tags=[f"community_slot_{i}"]
                )
    
    def _render_enhanced_seats(self, canvas, seats_data, tokens):
        """Render player seats with enhanced hole cards"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        num_seats = len(seats_data)
        
        # Calculate seat positions (simplified - would use actual seat positioning logic)
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) * 0.35
        
        for i, seat in enumerate(seats_data):
            if num_seats <= 1:
                continue
                
            # Calculate seat position
            angle = (i / num_seats) * 2 * 3.14159
            seat_x = center_x + radius * math.cos(angle)
            seat_y = center_y + radius * math.sin(angle)
            
            # Render hole cards if present
            cards = seat.get('cards', [])
            if cards and len(cards) >= 2:
                self._render_hole_cards(canvas, seat_x, seat_y, cards, num_seats)
            
            # Add micro-interactions for acting player
            if seat.get('acting', False):
                self.micro_interactions.pulse_seat_ring(
                    canvas, seat_x, seat_y, 120, 85
                )
    
    def _render_hole_cards(self, canvas, seat_x, seat_y, cards, num_players):
        """Render hole cards with dynamic sizing"""
        # Dynamic card sizing based on player count
        if num_players <= 3:
            card_w, card_h = 52, 75  # 6% scale
        elif num_players <= 6:
            card_w, card_h = 44, 64  # 5% scale
        else:
            card_w, card_h = 35, 51  # 4% scale
        
        gap = max(4, card_w // 8)
        
        for i, card in enumerate(cards[:2]):
            card_x = seat_x - (card_w + gap//2) + i * (card_w + gap)
            card_y = seat_y - card_h//2
            
            if card and card != "XX":
                # Face-up hole card
                rank, suit = card[:-1], card[-1]
                self.enhanced_cards.draw_card_face(
                    canvas, card_x, card_y, rank, suit, card_w, card_h,
                    tags=[f"hole_card_{seat_x}_{i}"]
                )
                
                # Add subtle shimmer for newly revealed cards
                if i == 0:  # Only shimmer first card to avoid overload
                    self.micro_interactions.card_reveal_shimmer(
                        canvas, card_x, card_y, card_w, card_h
                    )
            else:
                # Face-down hole card
                self.enhanced_cards.draw_card_back(
                    canvas, card_x, card_y, card_w, card_h,
                    tags=[f"hole_back_{seat_x}_{i}"]
                )
    
    def _render_enhanced_pot(self, canvas, pot_amount, tokens):
        """Render pot with chip stack visualization"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        # Render chip stacks around pot area
        if pot_amount > 0:
            # Create multiple small stacks for visual appeal
            num_stacks = min(6, max(2, pot_amount // 100))
            
            for i in range(num_stacks):
                angle = (i / num_stacks) * 2 * 3.14159
                stack_x = pot_x + 25 * math.cos(angle)
                stack_y = pot_y + 15 * math.sin(angle)
                
                stack_amount = pot_amount // num_stacks
                self.chip_animations.draw_chip_stack(
                    canvas, stack_x, stack_y, stack_amount,
                    tags=[f"pot_stack_{i}"]
                )
    
    # Animation Methods
    def animate_bet_to_pot(self, canvas, from_x, from_y, amount, callback=None):
        """Animate bet chips flying to pot"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        self.chip_animations.fly_chips_to_pot(
            canvas, from_x, from_y, pot_x, pot_y, amount, callback
        )
        
        # Flash pot when chips arrive
        if callback:
            original_callback = callback
            def enhanced_callback():
                self.micro_interactions.flash_pot_increase(canvas, pot_x, pot_y, 100, 60)
                if original_callback:
                    original_callback()
            callback = enhanced_callback
    
    def animate_pot_to_winner(self, canvas, winner_x, winner_y, amount, callback=None):
        """Animate pot chips flying to winner with celebration"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        self.chip_animations.fly_pot_to_winner(
            canvas, pot_x, pot_y, winner_x, winner_y, amount, callback
        )
        
        # Add confetti burst
        self.micro_interactions.winner_confetti_burst(canvas, winner_x, winner_y)
    
    def animate_card_reveal(self, canvas, card_x, card_y, card_w, card_h, 
                          from_card, to_card, callback=None):
        """Animate card flip with shimmer effect"""
        self.enhanced_cards.animate_card_flip(
            canvas, card_x, card_y, card_w, card_h, from_card, to_card, callback
        )
    
    def animate_dealer_button_move(self, canvas, from_x, from_y, to_x, to_y, callback=None):
        """Animate dealer button movement with trail"""
        self.micro_interactions.dealer_button_move_trail(canvas, from_x, from_y, to_x, to_y)
        
        # Use existing dealer button animation if available
        # This would integrate with existing dealer button component
        if callback:
            canvas.after(800, callback)  # Match trail duration
    
    # Interaction Methods
    def add_hover_effect(self, canvas, element_id, x, y, w, h):
        """Add hover glow to UI element"""
        self.micro_interactions.hover_glow(canvas, element_id, x, y, w, h)
    
    def remove_hover_effect(self, canvas, element_id):
        """Remove hover glow from UI element"""
        self.micro_interactions.remove_hover_glow(canvas, element_id)
    
    def button_press_feedback(self, canvas, btn_x, btn_y, btn_w, btn_h):
        """Visual feedback for button press"""
        self.micro_interactions.button_press_feedback(canvas, btn_x, btn_y, btn_w, btn_h)
    
    def pulse_acting_player(self, canvas, seat_x, seat_y):
        """Start pulsing ring around acting player"""
        self.micro_interactions.pulse_seat_ring(canvas, seat_x, seat_y, 120, 85)
    
    # Cleanup Methods
    def clear_all_effects(self, canvas):
        """Clear all visual effects and animations"""
        self.table_center.clear(canvas)
        self.enhanced_cards.clear_card_effects(canvas)
        self.chip_animations.cleanup_temp_elements(canvas)
        self.micro_interactions.cleanup_effects(canvas)
    
    def stop_all_animations(self):
        """Stop all active animations"""
        self.chip_animations.stop_all_animations()
        self.micro_interactions.stop_all_interactions()
    
    # Theme Integration
    def on_theme_change(self):
        """Handle theme change - refresh all components"""
        # Components automatically pick up new theme via theme_manager
        # No additional action needed due to token-driven design
        pass
