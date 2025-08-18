"""
Poker Animation System
Provides smooth animations for bet-to-pot, pot-to-winner, and other poker actions
"""

import math

class PokerAnimationSystem:
    def __init__(self, canvas, theme_manager):
        self.canvas = canvas
        self.theme = theme_manager
        self.active_animations = {}
        
    def animate_bet_to_pot(self, from_x, from_y, to_x, to_y, amount, callback=None):
        """Animate chips moving from player bet area to pot"""
        animation_id = f"bet_to_pot_{from_x}_{from_y}"
        
        # Create temporary chip stack for animation
        chip_ids = self._create_temp_chips(from_x, from_y, amount)
        
        # Animation parameters
        duration = self.theme.get_animation_duration("bet")
        steps = duration // 40  # 25 FPS
        dx = (to_x - from_x) / steps
        dy = (to_y - from_y) / steps
        
        def animate_step(step):
            if step >= steps:
                # Animation complete
                self._cleanup_temp_chips(chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
                
            # Move chips with easing
            progress = step / steps
            eased_progress = self._ease_out_cubic(progress)
            
            current_x = from_x + (to_x - from_x) * eased_progress
            current_y = from_y + (to_y - from_y) * eased_progress
            
            # Update chip positions
            for i, chip_id in enumerate(chip_ids):
                # Add slight randomness for natural movement
                offset_x = math.sin(step * 0.3 + i) * 2
                offset_y = math.cos(step * 0.2 + i) * 1
                
                self.canvas.coords(chip_id, 
                                 current_x + offset_x - 6, current_y + offset_y - 6,
                                 current_x + offset_x + 6, current_y + offset_y + 6)
                
            # Schedule next step
            self.canvas.after(40, lambda: animate_step(step + 1))
            
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def animate_pot_to_winner(self, pot_x, pot_y, winner_x, winner_y, amount, callback=None):
        """Animate pot chips moving to winner with celebration effect"""
        animation_id = f"pot_to_winner_{winner_x}_{winner_y}"
        
        # Create multiple chip stacks for explosion effect
        chip_positions = [
            (pot_x - 25, pot_y - 25),
            (pot_x + 25, pot_y - 25), 
            (pot_x, pot_y),
            (pot_x - 25, pot_y + 25),
            (pot_x + 25, pot_y + 25)
        ]
        
        all_chip_ids = []
        for pos_x, pos_y in chip_positions:
            chips = self._create_temp_chips(pos_x, pos_y, amount // len(chip_positions))
            all_chip_ids.extend(chips)
        
        # Animation parameters
        duration = self.theme.get_animation_duration("pot")
        steps = duration // 40
        
        def animate_step(step):
            if step >= steps:
                # Show winner celebration
                self._show_winner_celebration(winner_x, winner_y, amount)
                self._cleanup_temp_chips(all_chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
                
            # Animate all chips toward winner with different trajectories
            progress = step / steps
            eased_progress = self._ease_in_out_cubic(progress)
            
            for i, chip_id in enumerate(all_chip_ids):
                # Each chip follows slightly different path
                start_pos = chip_positions[i % len(chip_positions)]
                
                # Add arc to the movement
                arc_height = 30 * math.sin(progress * math.pi)
                
                current_x = start_pos[0] + (winner_x - start_pos[0]) * eased_progress
                current_y = start_pos[1] + (winner_y - start_pos[1]) * eased_progress - arc_height
                
                self.canvas.coords(chip_id,
                                 current_x - 6, current_y - 6,
                                 current_x + 6, current_y + 6)
                
            self.canvas.after(40, lambda: animate_step(step + 1))
            
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def animate_card_flip(self, card_x, card_y, card_width, card_height, 
                         from_card, to_card, callback=None):
        """Animate a card flip from back to face or vice versa"""
        animation_id = f"card_flip_{card_x}_{card_y}"
        
        duration = self.theme.get_animation_duration("card_flip")
        steps = duration // 20  # 50 FPS for smooth flip
        
        def animate_step(step):
            if step >= steps:
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
                
            # Calculate flip progress (0 to 1)
            progress = step / steps
            
            # Create flip effect by scaling width
            if progress < 0.5:
                # First half: shrink to nothing
                scale = 1 - (progress * 2)
                # Show original card
                self._render_card_at_scale(card_x, card_y, card_width, card_height, 
                                         from_card, scale)
            else:
                # Second half: grow from nothing
                scale = (progress - 0.5) * 2
                # Show new card
                self._render_card_at_scale(card_x, card_y, card_width, card_height,
                                         to_card, scale)
                
            self.canvas.after(20, lambda: animate_step(step + 1))
            
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def animate_dealer_button_move(self, from_x, from_y, to_x, to_y, callback=None):
        """Animate dealer button moving to new position"""
        animation_id = "dealer_button_move"
        
        # Create temporary dealer button for animation
        button_id = self._create_temp_dealer_button(from_x, from_y)
        
        duration = 800  # Smooth dealer button movement
        steps = duration // 40
        dx = (to_x - from_x) / steps
        dy = (to_y - from_y) / steps
        
        def animate_step(step):
            if step >= steps:
                self.canvas.delete(button_id)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
                
            # Move button with easing
            progress = step / steps
            eased_progress = self._ease_in_out_cubic(progress)
            
            current_x = from_x + (to_x - from_x) * eased_progress
            current_y = from_y + (to_y - from_y) * eased_progress
            
            # Update button position
            self.canvas.coords(button_id,
                             current_x - 10, current_y - 10,
                             current_x + 10, current_y + 10)
                             
            self.canvas.after(40, lambda: animate_step(step + 1))
            
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def _create_temp_chips(self, x, y, amount):
        """Create temporary chip graphics for animation"""
        chip_ids = []
        
        # Determine number of chips to show
        num_chips = min(5, max(1, amount // 100))
        
        for i in range(num_chips):
            chip_y = y - (i * 3)  # Stack chips
            
            # Get chip colors based on value
            chip_colors = self.theme.get_chip_colors(amount // num_chips)
            
            chip_id = self.canvas.create_oval(
                x - 6, chip_y - 6, x + 6, chip_y + 6,
                fill=chip_colors["bg"], outline=chip_colors["accent"], width=1,
                tags="temp_animation"
            )
            chip_ids.append(chip_id)
            
        return chip_ids
    
    def _cleanup_temp_chips(self, chip_ids):
        """Remove temporary animation chips"""
        for chip_id in chip_ids:
            try:
                self.canvas.delete(chip_id)
            except:
                pass  # Chip may already be deleted
    
    def _create_temp_dealer_button(self, x, y):
        """Create temporary dealer button for animation"""
        button_color = self.theme.get_token("dealer.buttonBg", "#F8FAFC")
        border_color = self.theme.get_token("dealer.buttonBorder", "#374151")
        text_color = self.theme.get_token("dealer.buttonFg", "#1F2937")
        
        # Create button circle
        button_id = self.canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10,
            fill=button_color, outline=border_color, width=2,
            tags="temp_animation"
        )
        
        # Add "D" text
        self.canvas.create_text(
            x, y, text="D", font=("Inter", 10, "bold"),
            fill=text_color, tags="temp_animation"
        )
        
        return button_id
    
    def _render_card_at_scale(self, x, y, width, height, card, scale):
        """Render a card at a specific scale for flip animation"""
        scaled_width = int(width * scale)
        if scaled_width <= 0:
            return
            
        # Clear previous card
        self.canvas.delete("flip_card")
        
        # Render scaled card
        if card and card != "XX":
            # Face-up card (simplified for animation)
            self.canvas.create_rectangle(
                x - scaled_width//2, y - height//2,
                x + scaled_width//2, y + height//2,
                fill="#FFFFFF", outline="#1F2937", width=1,
                tags="flip_card"
            )
        else:
            # Face-down card
            self.canvas.create_rectangle(
                x - scaled_width//2, y - height//2,
                x + scaled_width//2, y + height//2,
                fill="#7F1D1D", outline="#1F2937", width=1,
                tags="flip_card"
            )
    
    def _show_winner_celebration(self, x, y, amount):
        """Show winner celebration effect"""
        # Create celebration burst
        for i in range(8):
            angle = i * (math.pi * 2 / 8)
            end_x = x + math.cos(angle) * 50
            end_y = y + math.sin(angle) * 50
            
            # Create celebration particles
            particle_id = self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill="#FCD34D", outline="", tags="celebration"
            )
            
            # Animate particle outward
            self._animate_particle(particle_id, x, y, end_x, end_y)
        
        # Show winner text briefly
        winner_text_id = self.canvas.create_text(
            x, y - 30, text="WINNER!", font=("Inter", 16, "bold"),
            fill="#FCD34D", tags="celebration"
        )
        
        # Clean up celebration after 2 seconds
        self.canvas.after(2000, lambda: self.canvas.delete("celebration"))
    
    def _animate_particle(self, particle_id, start_x, start_y, end_x, end_y):
        """Animate a single celebration particle"""
        steps = 20
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        def move_particle(step):
            if step >= steps:
                return
                
            try:
                self.canvas.move(particle_id, dx, dy)
                self.canvas.after(30, lambda: move_particle(step + 1))
            except:
                pass  # Particle may be deleted
                
        move_particle(0)
    
    # Easing functions for smooth animations
    def _ease_out_cubic(self, t):
        """Cubic ease-out function"""
        return 1 - pow(1 - t, 3)
    
    def _ease_in_out_cubic(self, t):
        """Cubic ease-in-out function"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def stop_all_animations(self):
        """Stop all active animations"""
        self.canvas.delete("temp_animation")
        self.canvas.delete("celebration")
        self.canvas.delete("flip_card")
        self.active_animations.clear()
    
    def is_animating(self):
        """Check if any animations are currently running"""
        return len(self.active_animations) > 0
