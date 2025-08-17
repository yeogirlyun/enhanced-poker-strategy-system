"""
Chip Animation System - Flying Chips for Bet→Pot and Pot→Winner
Token-driven animations with smooth easing and particle effects
"""

import math
from ..services.theme_utils import ease_in_out_cubic

class ChipAnimations:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.active_animations = {}
        
    def draw_chip(self, canvas, x, y, denom_key, text="", r=14, tags=None):
        """Draw a single chip with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Get chip colors from tokens
        chip_color = tokens.get(denom_key, "#2E86AB")  # Default to $1 blue
        rim_color = tokens.get("chip.rim", "#000000")
        text_color = tokens.get("chip.text", "#F8F7F4")
        
        chip_tags = ["chip"]
        if tags:
            chip_tags.extend(tags)
        
        # Main chip circle
        chip_id = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=chip_color, outline=rim_color, width=2,
            tags=tuple(chip_tags)
        )
        
        # Inner ring for depth
        inner_r = r - 3
        canvas.create_oval(
            x - inner_r, y - inner_r, x + inner_r, y + inner_r,
            fill="", outline=rim_color, width=1,
            tags=tuple(chip_tags)
        )
        
        # Value text (if provided)
        if text:
            canvas.create_text(
                x, y, text=text, fill=text_color,
                font=("Inter", 8, "bold"), anchor="center",
                tags=tuple(chip_tags)
            )
        
        return chip_id
    
    def stack_height(self, amount):
        """Calculate stack height based on amount"""
        return min(8, max(1, int(amount / 50)))  # 50 units per chip
    
    def draw_chip_stack(self, canvas, x, y, amount, tags=None):
        """Draw a stack of chips representing the total value"""
        if amount <= 0:
            return []
        
        # Determine chip denominations to show
        denom_keys = ["chip.$1", "chip.$5", "chip.$25", "chip.$100", "chip.$500", "chip.$1k"]
        levels = self.stack_height(amount)
        
        chip_ids = []
        for i in range(levels):
            # Cycle through denominations for visual variety
            denom = denom_keys[i % len(denom_keys)]
            chip_y = y - (i * 4)  # Stack with 4px offset
            
            chip_id = self.draw_chip(canvas, x, chip_y, denom, tags=tags)
            chip_ids.append(chip_id)
        
        return chip_ids
    
    def fly_chips_to_pot(self, canvas, from_x, from_y, to_x, to_y, amount, callback=None):
        """Animate chips flying from player bet area to pot"""
        animation_id = f"bet_to_pot_{from_x}_{from_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create temporary chips for animation
        num_chips = min(5, max(1, int(amount / 100)))
        chip_ids = []
        
        for i in range(num_chips):
            # Slight spread for natural look
            start_x = from_x + (i - num_chips//2) * 8
            start_y = from_y + (i - num_chips//2) * 4
            
            chip_id = self.draw_chip(canvas, start_x, start_y, "chip.$25", 
                                   tags=["flying_chip", "temp_animation"])
            chip_ids.append((chip_id, start_x, start_y))
        
        # Animation parameters
        frames = 20
        
        def animate_step(frame):
            if frame >= frames:
                # Animation complete
                self._cleanup_flying_chips(canvas, chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            # Calculate progress with easing
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Update each chip position
            for i, (chip_id, start_x, start_y) in enumerate(chip_ids):
                # Calculate current position with slight arc
                current_x = start_x + (to_x - start_x) * eased_progress
                current_y = start_y + (to_y - start_y) * eased_progress
                
                # Add arc effect (parabolic path)
                arc_height = 25 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                # Add slight randomness for natural movement
                wobble_x = math.sin(frame * 0.5 + i) * 2
                wobble_y = math.cos(frame * 0.3 + i) * 1
                
                # Update chip position
                try:
                    canvas.coords(chip_id, 
                                current_x + wobble_x - 14, current_y + wobble_y - 14,
                                current_x + wobble_x + 14, current_y + wobble_y + 14)
                except:
                    pass  # Chip may have been deleted
            
            # Add motion blur/glow effect
            if frame % 3 == 0:  # Every 3rd frame
                glow_color = tokens.get("bet.glow", "#FFD700")
                for _, (chip_id, _, _) in enumerate(chip_ids):
                    try:
                        bbox = canvas.bbox(chip_id)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            canvas.create_oval(
                                x1 - 3, y1 - 3, x2 + 3, y2 + 3,
                                outline=glow_color, width=1,
                                tags=("motion_glow", "temp_animation")
                            )
                    except:
                        pass
            
            # Schedule next frame
            canvas.after(40, lambda: animate_step(frame + 1))
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def fly_pot_to_winner(self, canvas, pot_x, pot_y, winner_x, winner_y, amount, callback=None):
        """Animate pot chips flying to winner with celebration effect"""
        animation_id = f"pot_to_winner_{winner_x}_{winner_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create explosion of chips from pot
        explosion_positions = []
        num_stacks = 6
        
        for i in range(num_stacks):
            angle = (i / num_stacks) * 2 * math.pi
            radius = 30
            exp_x = pot_x + radius * math.cos(angle)
            exp_y = pot_y + radius * math.sin(angle)
            explosion_positions.append((exp_x, exp_y))
        
        # Create chip stacks for animation
        all_chip_ids = []
        for exp_x, exp_y in explosion_positions:
            stack_chips = self.draw_chip_stack(canvas, exp_x, exp_y, amount // num_stacks,
                                             tags=["flying_chip", "temp_animation"])
            all_chip_ids.extend([(chip_id, exp_x, exp_y) for chip_id in stack_chips])
        
        frames = 30
        
        def animate_step(frame):
            if frame >= frames:
                # Show winner celebration
                self._show_winner_celebration(canvas, winner_x, winner_y, tokens)
                self._cleanup_flying_chips(canvas, all_chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Move all chips toward winner
            for chip_id, start_x, start_y in all_chip_ids:
                # Calculate trajectory with arc
                current_x = start_x + (winner_x - start_x) * eased_progress
                current_y = start_y + (winner_y - start_y) * eased_progress
                
                # Higher arc for dramatic effect
                arc_height = 40 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                try:
                    canvas.coords(chip_id,
                                current_x - 14, current_y - 14,
                                current_x + 14, current_y + 14)
                except:
                    pass
            
            canvas.after(35, lambda: animate_step(frame + 1))
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def _show_winner_celebration(self, canvas, x, y, tokens):
        """Show celebration effect at winner position"""
        celebration_color = tokens.get("label.winner.bg", "#FFD700")
        
        # Create particle burst
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            
            # Particle trajectory
            end_x = x + 60 * math.cos(angle)
            end_y = y + 60 * math.sin(angle)
            
            # Create particle
            particle_id = canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=celebration_color, outline="",
                tags=("celebration_particle", "temp_animation")
            )
            
            # Animate particle outward
            self._animate_particle(canvas, particle_id, x, y, end_x, end_y)
        
        # Winner text flash
        canvas.create_text(
            x, y - 40, text="WINNER!", 
            font=("Inter", 18, "bold"), fill=celebration_color,
            tags=("winner_flash", "temp_animation")
        )
        
        # Auto-cleanup after 2 seconds
        canvas.after(2000, lambda: canvas.delete("celebration_particle", "winner_flash"))
    
    def _animate_particle(self, canvas, particle_id, start_x, start_y, end_x, end_y):
        """Animate a single celebration particle"""
        frames = 15
        
        def particle_step(frame):
            if frame >= frames:
                try:
                    canvas.delete(particle_id)
                except:
                    pass
                return
            
            progress = frame / frames
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            try:
                canvas.coords(particle_id,
                            current_x - 3, current_y - 3,
                            current_x + 3, current_y + 3)
            except:
                pass
            
            canvas.after(30, lambda: particle_step(frame + 1))
        
        particle_step(0)
    
    def _cleanup_flying_chips(self, canvas, chip_ids):
        """Clean up temporary animation chips"""
        for chip_data in chip_ids:
            if isinstance(chip_data, tuple):
                chip_id = chip_data[0]
            else:
                chip_id = chip_data
            try:
                canvas.delete(chip_id)
            except:
                pass
        
        # Clean up motion effects
        canvas.delete("motion_glow")
    
    def pulse_pot(self, canvas, pot_x, pot_y, tokens):
        """Subtle pot pulse when amount increases"""
        glow_color = tokens.get("glow.medium", "#FFD700")
        
        def pulse_step(radius, intensity):
            if intensity <= 0:
                canvas.delete("pot_pulse")
                return
            
            # Create expanding ring
            canvas.create_oval(
                pot_x - radius, pot_y - radius,
                pot_x + radius, pot_y + radius,
                outline=glow_color, width=2,
                tags=("pot_pulse", "temp_animation")
            )
            
            canvas.after(60, lambda: pulse_step(radius + 8, intensity - 1))
        
        pulse_step(20, 5)
    
    def stop_all_animations(self):
        """Stop all active chip animations"""
        self.active_animations.clear()
    
    def cleanup_temp_elements(self, canvas):
        """Clean up all temporary animation elements"""
        canvas.delete("temp_animation")
        canvas.delete("flying_chip")
        canvas.delete("motion_glow")
        canvas.delete("pot_pulse")
