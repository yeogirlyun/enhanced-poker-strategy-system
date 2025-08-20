# HandsReviewTab Animation Patch

```python
def _handle_effect_animate(self, event_name, data):
    """Handle animation effect events."""
    if not event_name or not self.canvas:
        return
        
    anim = self.chip_animations
    if not anim:
        return
        
    # Get pot display center
    pot_center = self._get_pot_center()
    if not pot_center:
        return
        
    if event_name == "chips_to_pot":
        # Find acting seat
        acting_seat = None
        for seat in self.display_state.get("seats", []):
            if seat.get("acting"):
                acting_seat = seat
                break
                
        if not acting_seat:
            print("⚠️ No acting seat found for chips_to_pot animation")
            return
            
        # Get chip start position (from bet location)
        seat_center = self._get_seat_position(acting_seat)
        bet_pos = self._get_bet_position(acting_seat)
        if not bet_pos:
            return
            
        # Start animation
        bet_amount = acting_seat.get("current_bet", 0)
        if bet_amount > 0:
            anim.fly_chips_to_pot(
                canvas=self.canvas,
                start_x=bet_pos[0],
                start_y=bet_pos[1],
                end_x=pot_center[0],
                end_y=pot_center[1],
                amount=bet_amount,
                chip_size=self.config.chip_size
            )
            
    elif event_name == "pot_to_winner":
        winner = data.get("winner")
        if not winner:
            return
            
        # Find winner seat
        winner_seat = None
        for seat in self.display_state.get("seats", []):
            if seat.get("player_uid") == winner.get("player_uid"):
                winner_seat = seat
                break
                
        if not winner_seat:
            return
            
        # Get end position
        seat_pos = self._get_seat_position(winner_seat)
        if not seat_pos:
            return
            
        # Start animation
        pot_amount = data.get("amount", 0)
        if pot_amount > 0:
            anim.fly_chips_to_winner(
                canvas=self.canvas,
                start_x=pot_center[0],
                start_y=pot_center[1],
                end_x=seat_pos[0],
                end_y=seat_pos[1],
                amount=pot_amount,
                chip_size=self.config.chip_size
            )

def _get_pot_center(self):
    """Get pot display center coordinates."""
    if not self.canvas:
        return None
        
    width = self.canvas.winfo_width()
    height = self.canvas.winfo_height()
    
    return (width//2, height//2)

def _get_seat_position(self, seat_data):
    """Get seat center coordinates."""
    if not seat_data or not self.canvas:
        return None
        
    width = self.canvas.winfo_width()
    height = self.canvas.winfo_height()
    
    # Calculate based on seat index
    seat_index = seat_data.get("seat_index", 0)
    total_seats = len(self.display_state.get("seats", []))
    
    angle = (2 * math.pi * seat_index / total_seats) - (math.pi/2)
    radius = min(width, height) * 0.35
    
    x = width/2 + radius * math.cos(angle)
    y = height/2 + radius * math.sin(angle)
    
    return (int(x), int(y))

def _get_bet_position(self, seat_data):
    """Get bet display coordinates for seat."""
    seat_pos = self._get_seat_position(seat_data)
    if not seat_pos:
        return None
        
    # Offset toward pot
    pot_center = self._get_pot_center()
    if not pot_center:
        return seat_pos
        
    dx = pot_center[0] - seat_pos[0]
    dy = pot_center[1] - seat_pos[1]
    dist = math.sqrt(dx*dx + dy*dy)
    
    if dist == 0:
        return seat_pos
        
    # Place 60px closer to pot
    t = 60 / dist
    x = int(seat_pos[0] + dx * t)
    y = int(seat_pos[1] + dy * t)
    
    return (x, y)
```

Key changes:
1. Added robust animation handling
2. Fixed position calculations
3. Added missing chip_size parameter
4. Improved error handling
