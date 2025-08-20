def _handle_effect_animate(self, effect_name, data):
    """Handle animation effects.
    
    Args:
        effect_name: Name of animation effect
        data: Animation effect data
    """
    if effect_name == "chips_to_pot":
        # Get acting seat
        acting_seat = self._get_acting_seat()
        if not acting_seat:
            print("⚠️ No acting seat found for chips_to_pot animation")
            return
            
        # Get positions
        seat_pos = self._get_seat_position(acting_seat)
        bet_pos = self._get_bet_position(acting_seat)
        pot_center = self._get_pot_center()
        
        # Create animation
        anim = ChipAnimations(
            canvas=self.canvas,
            tokens=self.tokens,
            config=self.config
        )
        
        # Trigger animation with chip size
        anim.fly_chips_to_pot(
            canvas=self.canvas,
            start_x=bet_pos[0],
            start_y=bet_pos[1],
            end_x=pot_center[0], 
            end_y=pot_center[1],
            amount=acting_seat.current_bet,
            chip_size=58,
            callback=self._on_animation_complete
        )
        
    elif effect_name == "pot_to_winner":
        # Similar winner animation implementation
        pass
