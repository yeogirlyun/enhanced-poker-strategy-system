def fly_chips_to_pot(self, canvas, start_x, start_y, end_x, end_y, amount, callback=None):
    """Animate chips flying from player to pot.
    
    Args:
        canvas: Canvas to animate on
        start_x: Starting X position 
        start_y: Starting Y position
        end_x: Ending X position at pot
        end_y: Ending Y position at pot
        amount: Bet amount to animate
        callback: Optional completion callback
    """
    # Get chip denominations to display
    denoms = self._get_chip_denoms(amount)
    
    # Create chip graphics with labels
    chip_ids = []
    for i, denom in enumerate(denoms):
        # Offset each chip slightly
        x = start_x + (i * 10) 
        y = start_y + (i * 10)
        
        chip_id = self._create_chip_with_label(
            canvas=canvas,
            start_x=x,
            start_y=y, 
            denom=denom,
            tokens=self.tokens,
            chip_size=58,
            tags=["flying_chip", "temp_animation"]
        )
        chip_ids.append(chip_id)
    
    # Animate chips moving to pot
    self._animate_chips_to_pot(canvas, chip_ids, end_x, end_y, callback)
    
    return chip_ids
