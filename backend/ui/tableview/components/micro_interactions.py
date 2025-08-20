"""
Micro-Interactions System
Subtle glows, pulses, and state transitions for premium feel
"""

import math
from ...services.theme_utils import ease_color_transition, lighten, alpha_over

class MicroInteractions:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.active_pulses = {}
        self.active_glows = {}
        
    def pulse_seat_ring(self, canvas, seat_x, seat_y, seat_w, seat_h, duration_ms=1000):
        """Subtle pulsing ring around acting player seat"""
        tokens = self.theme.get_all_tokens()
        focus_color = tokens.get("a11y.focus", "#22C55E")
        
        pulse_id = f"seat_pulse_{seat_x}_{seat_y}"
        
        # Clear any existing pulse
        if pulse_id in self.active_pulses:
            canvas.after_cancel(self.active_pulses[pulse_id])
        
        frames = duration_ms // 50  # 20 FPS
        
        def pulse_step(frame):
            if frame >= frames:
                canvas.delete(f"pulse_{pulse_id}")
                if pulse_id in self.active_pulses:
                    del self.active_pulses[pulse_id]
                return
            
            # Calculate pulse intensity (sine wave)
            progress = (frame / frames) * 2 * math.pi
            intensity = (math.sin(progress) + 1) / 2  # 0 to 1
            
            # Clear previous pulse frame
            canvas.delete(f"pulse_{pulse_id}")
            
            # Draw pulsing ring with varying alpha
            ring_width = 2 + int(intensity * 2)  # 2-4px width
            alpha = 0.3 + (intensity * 0.4)  # 30-70% alpha
            
            # Create multiple rings for glow effect
            for i in range(3):
                offset = i * 2
                canvas.create_rectangle(
                    seat_x - seat_w//2 - offset, seat_y - seat_h//2 - offset,
                    seat_x + seat_w//2 + offset, seat_y + seat_h//2 + offset,
                    outline=focus_color, width=ring_width - i,
                    tags=(f"pulse_{pulse_id}",)
                )
            
            # Schedule next frame
            timer_id = canvas.after(50, lambda: pulse_step(frame + 1))
            self.active_pulses[pulse_id] = timer_id
        
        pulse_step(0)
    
    def flash_pot_increase(self, canvas, pot_x, pot_y, pot_w, pot_h):
        """Brief flash when pot amount increases"""
        tokens = self.theme.get_all_tokens()
        metal_color = tokens.get("table.inlay", "#C9A86A")
        flash_color = lighten(metal_color, 0.25)
        
        flash_frames = 8  # Quick flash
        
        def flash_step(frame):
            if frame >= flash_frames:
                canvas.delete("pot_flash")
                return
            
            # Fade from bright to normal
            progress = frame / flash_frames
            current_color = ease_color_transition(flash_color, metal_color, progress)
            
            # Clear previous flash
            canvas.delete("pot_flash")
            
            # Draw flash ring around pot
            canvas.create_rectangle(
                pot_x - pot_w//2 - 3, pot_y - pot_h//2 - 3,
                pot_x + pot_w//2 + 3, pot_y + pot_h//2 + 3,
                outline=current_color, width=2,
                tags=("pot_flash",)
            )
            
            canvas.after(60, lambda: flash_step(frame + 1))
        
        flash_step(0)
    
    def hover_glow(self, canvas, element_id, x, y, w, h, glow_type="soft"):
        """Add hover glow effect to UI element"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get(f"glow.{glow_type}", tokens.get("a11y.focus", "#22C55E"))
        
        glow_tag = f"hover_glow_{element_id}"
        
        # Clear existing glow
        canvas.delete(glow_tag)
        
        # Create soft glow with multiple rings
        for i in range(4):
            offset = (i + 1) * 2
            alpha = 1.0 - (i * 0.2)  # Fade outward
            
            canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset,
                outline=glow_color, width=1,
                tags=(glow_tag,)
            )
    
    def remove_hover_glow(self, canvas, element_id):
        """Remove hover glow effect"""
        canvas.delete(f"hover_glow_{element_id}")
    
    def button_press_feedback(self, canvas, btn_x, btn_y, btn_w, btn_h):
        """Quick visual feedback for button press"""
        tokens = self.theme.get_all_tokens()
        active_color = tokens.get("btn.primary.activeBorder", "#FFD700")
        
        feedback_frames = 6
        
        def feedback_step(frame):
            if frame >= feedback_frames:
                canvas.delete("button_feedback")
                return
            
            # Quick expand and contract
            progress = frame / feedback_frames
            scale = 1.0 + (0.1 * math.sin(progress * math.pi))  # Slight scale pulse
            
            offset = int((scale - 1.0) * min(btn_w, btn_h) / 2)
            
            canvas.delete("button_feedback")
            canvas.create_rectangle(
                btn_x - offset, btn_y - offset,
                btn_x + btn_w + offset, btn_y + btn_h + offset,
                outline=active_color, width=2,
                tags=("button_feedback",)
            )
            
            canvas.after(30, lambda: feedback_step(frame + 1))
        
        feedback_step(0)
    
    def card_reveal_shimmer(self, canvas, card_x, card_y, card_w, card_h):
        """Subtle shimmer effect when card is revealed"""
        tokens = self.theme.get_all_tokens()
        shimmer_color = tokens.get("glow.medium", "#FFD700")
        
        shimmer_frames = 12
        
        def shimmer_step(frame):
            if frame >= shimmer_frames:
                canvas.delete("card_shimmer")
                return
            
            # Moving highlight across card
            progress = frame / shimmer_frames
            highlight_x = card_x + (progress * card_w)
            
            canvas.delete("card_shimmer")
            
            # Vertical highlight line
            canvas.create_line(
                highlight_x, card_y, highlight_x, card_y + card_h,
                fill=shimmer_color, width=2,
                tags=("card_shimmer",)
            )
            
            # Soft glow around line
            canvas.create_line(
                highlight_x - 1, card_y, highlight_x - 1, card_y + card_h,
                fill=shimmer_color, width=1,
                tags=("card_shimmer",)
            )
            canvas.create_line(
                highlight_x + 1, card_y, highlight_x + 1, card_y + card_h,
                fill=shimmer_color, width=1,
                tags=("card_shimmer",)
            )
            
            canvas.after(40, lambda: shimmer_step(frame + 1))
        
        shimmer_step(0)
    
    def dealer_button_move_trail(self, canvas, from_x, from_y, to_x, to_y):
        """Subtle trail effect when dealer button moves"""
        tokens = self.theme.get_all_tokens()
        trail_color = tokens.get("dealer.buttonBorder", "#C9A86A")
        
        trail_frames = 15
        
        def trail_step(frame):
            if frame >= trail_frames:
                canvas.delete("dealer_trail")
                return
            
            progress = frame / trail_frames
            
            # Create fading trail points
            for i in range(5):
                trail_progress = max(0, progress - (i * 0.1))
                if trail_progress <= 0:
                    continue
                
                trail_x = from_x + (to_x - from_x) * trail_progress
                trail_y = from_y + (to_y - from_y) * trail_progress
                
                # Fading circle
                alpha = (1.0 - i * 0.2) * (1.0 - progress)
                radius = 8 - i
                
                canvas.create_oval(
                    trail_x - radius, trail_y - radius,
                    trail_x + radius, trail_y + radius,
                    outline=trail_color, width=1,
                    tags=("dealer_trail",)
                )
            
            canvas.after(50, lambda: trail_step(frame + 1))
        
        trail_step(0)
    
    def winner_confetti_burst(self, canvas, center_x, center_y):
        """Celebration confetti burst for winner"""
        tokens = self.theme.get_all_tokens()
        colors = [
            tokens.get("chip.$25", "#2AA37A"),
            tokens.get("chip.$100", "#3C3A3A"),
            tokens.get("chip.$500", "#6C4AB6"),
            tokens.get("table.inlay", "#C9A86A"),
        ]
        
        # Create 20 confetti pieces
        confetti_pieces = []
        for i in range(20):
            angle = (i / 20) * 2 * math.pi
            velocity = 30 + (i % 3) * 10  # Varying speeds
            
            piece_data = {
                'x': center_x,
                'y': center_y,
                'vx': velocity * math.cos(angle),
                'vy': velocity * math.sin(angle),
                'color': colors[i % len(colors)],
                'size': 3 + (i % 2),
                'rotation': 0,
                'id': None
            }
            confetti_pieces.append(piece_data)
        
        confetti_frames = 30
        
        def confetti_step(frame):
            if frame >= confetti_frames:
                canvas.delete("confetti")
                return
            
            canvas.delete("confetti")
            
            for piece in confetti_pieces:
                # Update position
                piece['x'] += piece['vx'] * 0.8  # Slow down over time
                piece['y'] += piece['vy'] * 0.8
                piece['vy'] += 1  # Gravity
                piece['rotation'] += 10
                
                # Draw confetti piece
                size = piece['size']
                canvas.create_rectangle(
                    piece['x'] - size, piece['y'] - size,
                    piece['x'] + size, piece['y'] + size,
                    fill=piece['color'], outline="",
                    tags=("confetti",)
                )
            
            canvas.after(50, lambda: confetti_step(frame + 1))
        
        confetti_step(0)
    
    def stop_all_interactions(self):
        """Stop all active micro-interactions"""
        # Cancel all active pulses
        for pulse_id, timer_id in self.active_pulses.items():
            try:
                # Note: canvas.after_cancel would need canvas reference
                pass
            except:
                pass
        self.active_pulses.clear()
        self.active_glows.clear()
    
    def cleanup_effects(self, canvas):
        """Clean up all visual effects"""
        canvas.delete("pot_flash")
        canvas.delete("card_shimmer")
        canvas.delete("dealer_trail")
        canvas.delete("confetti")
        canvas.delete("button_feedback")
        
        # Clean up all hover glows
        for glow_id in list(self.active_glows.keys()):
            canvas.delete(f"hover_glow_{glow_id}")
        
        # Clean up all pulses
        for pulse_id in list(self.active_pulses.keys()):
            canvas.delete(f"pulse_{pulse_id}")
