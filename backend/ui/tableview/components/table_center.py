"""
Table Center Pattern Component
Renders subtle ellipse and micro-mosaic pattern at the center of the poker table
"""

import math

class TableCenter:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    def render(self, canvas, state):
        """Render table center pattern with subtle ellipse and micro-mosaic"""
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            return
            
        # Clear previous center elements
        canvas.delete("felt:center")
        
        # Get theme tokens
        tokens = self.theme.get_all_tokens()
        
        cx, cy = w // 2, h // 2
        
        # Main ellipse pattern (6% lighter than felt)
        ellipse_color = tokens.get("table.centerPattern", tokens.get("table.felt", "#1E4D2B"))
        
        # Subtle ellipse at center
        ellipse_w = min(w * 0.3, 210)
        ellipse_h = min(h * 0.15, 90)
        
        canvas.create_oval(
            cx - ellipse_w, cy - ellipse_h,
            cx + ellipse_w, cy + ellipse_h,
            fill=ellipse_color, outline="",
            tags=("felt:center", "table_pattern")
        )
        
        # Micro-mosaic pattern (thin arc strokes in metal at low alpha)
        inlay_color = tokens.get("table.inlay", "#C9A86A")
        
        # Create concentric arcs for mosaic effect
        base_radius = min(w, h) * 0.08  # Scale with table size
        
        for i, r_factor in enumerate([0.8, 1.0, 1.2]):
            r = int(base_radius * r_factor)
            
            # Create subtle arc pattern
            self._draw_mosaic_arc(canvas, cx, cy, r, inlay_color, i)
            
        # Optional: Add subtle radial lines
        if w > 800:  # Only on larger tables
            self._draw_radial_lines(canvas, cx, cy, base_radius, inlay_color)
    
    def _draw_mosaic_arc(self, canvas, cx, cy, radius, color, offset):
        """Draw a single mosaic arc with stipple pattern"""
        # Horizontal ellipse
        canvas.create_oval(
            cx - (radius * 2), cy - radius,
            cx + (radius * 2), cy + radius,
            outline=color, width=1, stipple="gray25",
            tags=("felt:center", "mosaic_arc")
        )
        
        # Add subtle cross-hatching for texture
        if offset % 2 == 0:
            # Vertical accent lines
            for angle in [30, 60, 120, 150]:
                x_offset = int(radius * 0.7 * math.cos(math.radians(angle)))
                y_offset = int(radius * 0.4 * math.sin(math.radians(angle)))
                
                canvas.create_line(
                    cx + x_offset - 5, cy + y_offset - 5,
                    cx + x_offset + 5, cy + y_offset + 5,
                    fill=color, width=1, stipple="gray12",
                    tags=("felt:center", "texture_line")
                )
    
    def _draw_radial_lines(self, canvas, cx, cy, base_radius, color):
        """Draw subtle radial lines for enhanced texture"""
        line_length = base_radius * 0.6
        
        # 8 radial lines at 45-degree intervals
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            
            # Inner point
            x1 = cx + int((base_radius * 0.3) * math.cos(rad))
            y1 = cy + int((base_radius * 0.3) * math.sin(rad))
            
            # Outer point
            x2 = cx + int((base_radius * 0.9) * math.cos(rad))
            y2 = cy + int((base_radius * 0.9) * math.sin(rad))
            
            canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=1, stipple="gray6",
                tags=("felt:center", "radial_line")
            )
    
    def animate_pulse(self, canvas):
        """Subtle pulse animation for dramatic moments"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get("glow.soft", tokens.get("table.inlay", "#C9A86A"))
        
        w, h = canvas.winfo_width(), canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Create expanding glow ring
        def pulse_step(radius, alpha_step):
            if alpha_step <= 0:
                canvas.delete("center_pulse")
                return
                
            # Calculate alpha for fade effect
            alpha = alpha_step / 10.0
            
            # Create glow ring
            canvas.create_oval(
                cx - radius, cy - radius//2,
                cx + radius, cy + radius//2,
                outline=glow_color, width=2,
                tags=("center_pulse",)
            )
            
            # Schedule next step
            canvas.after(50, lambda: pulse_step(radius + 5, alpha_step - 1))
        
        pulse_step(50, 10)
    
    def clear(self, canvas):
        """Clear all center pattern elements"""
        canvas.delete("felt:center")
        canvas.delete("center_pulse")
