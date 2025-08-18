"""
Enhanced Player Display System for Poker UI
Provides professional player pod rendering with readable text and proper theming
"""

class EnhancedPlayerDisplay:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    def render_player_pod(self, canvas, x, y, player_data, is_acting=False, num_players=6):
        """Render an enhanced player pod with better visibility"""
        # Dynamic pod sizing based on number of players
        if num_players <= 3:
            pod_width, pod_height = 140, 100  # Larger for fewer players
        elif num_players <= 6:
            pod_width, pod_height = 120, 85   # Medium size
        else:
            pod_width, pod_height = 100, 70   # Smaller for more players
            
        # Theme-based colors with better contrast
        if is_acting:
            bg_color = self.theme.get("seat.bg.acting", "#2D4A22")  # Dark green
            border_color = self.theme.get("a11y.focus", "#4ADE80")  # Bright green
            border_width = 3
            glow_color = self.theme.get("status.acting.glow", "#22C55E")
        elif player_data.get('folded'):
            bg_color = self.theme.get("seat.bg.folded", "#1F1F1F")  # Dark gray
            border_color = self.theme.get("status.folded.color", "#6B7280")
            border_width = 2
            glow_color = None
        else:
            bg_color = self.theme.get("seat.bg.idle", "#1E293B")    # Dark blue-gray
            border_color = self.theme.get("seat.ring", "#475569")   # Medium gray
            border_width = 2
            glow_color = None
            
        # Main pod rectangle with rounded corners effect
        canvas.create_rectangle(x - pod_width//2, y - pod_height//2,
                              x + pod_width//2, y + pod_height//2,
                              fill=bg_color, outline=border_color, width=border_width,
                              tags=("player_pod", f"pod_{player_data.get('name', 'empty')}"))
        
        # Glow effect for acting player
        if glow_color:
            canvas.create_rectangle(x - pod_width//2 - 3, y - pod_height//2 - 3,
                                  x + pod_width//2 + 3, y + pod_height//2 + 3,
                                  fill="", outline=glow_color, width=1,
                                  tags=("player_pod", "acting_glow"))
        
        # Luxury gradient highlight (top edge)
        highlight_color = self.theme.get("seat.highlight", "#334155")
        canvas.create_rectangle(x - pod_width//2 + 3, y - pod_height//2 + 3,
                              x + pod_width//2 - 3, y - pod_height//2 + 10,
                              fill=highlight_color, outline="",
                              tags=("player_pod", "highlight"))
        
        # Player name with enhanced readability
        self._render_player_name(canvas, x, y - pod_height//2 + 15, player_data, pod_width)
        
        # Stack amount with better formatting
        self._render_stack_display(canvas, x, y + pod_height//2 - 15, player_data)
        
        # Status indicators
        self._render_status_indicators(canvas, x, y + 5, player_data)
        
        return f"pod_{player_data.get('name', 'empty')}"
    
    def _render_player_name(self, canvas, x, y, player_data, pod_width):
        """Render player name with enhanced visibility"""
        name = player_data.get('name', 'Empty Seat')
        position = player_data.get('position', '')
        
        # Enhanced font size for better readability
        name_font = self.theme.get("player.name.font", ("Inter", 14, "bold"))
        name_color = self.theme.get("player.name.color", "#F1F5F9")  # Light gray
        
        # Display name with position if available
        if position and name != 'Empty Seat':
            display_text = f"{name} ({position})"
        else:
            display_text = name
            
        # Truncate text if too long for pod
        max_chars = max(8, pod_width // 10)
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-2] + ".."
            
        canvas.create_text(x, y, text=display_text, font=name_font, 
                          fill=name_color, anchor="center",
                          tags=("player_pod", "player_name"))
    
    def _render_stack_display(self, canvas, x, y, player_data):
        """Render stack amount with enhanced formatting"""
        stack = player_data.get('stack', 0)
        
        # Enhanced font for stack display
        stack_font = self.theme.get("player.stack.font", ("Inter", 12, "bold"))
        stack_color = self.theme.get("player.stack.color", "#FCD34D")  # Gold
        
        # Format stack amount
        if stack >= 1000000:
            stack_text = f"${stack/1000000:.1f}M"
        elif stack >= 1000:
            stack_text = f"${stack/1000:.1f}K"
        else:
            stack_text = f"${stack}"
            
        canvas.create_text(x, y, text=stack_text, font=stack_font,
                          fill=stack_color, anchor="center",
                          tags=("player_pod", "stack_amount"))
    
    def _render_status_indicators(self, canvas, x, y, player_data):
        """Render player status indicators"""
        status_font = ("Inter", 10, "bold")
        
        if player_data.get('folded'):
            canvas.create_text(x, y, text="FOLDED", font=status_font,
                              fill=self.theme.get("status.folded.color", "#6B7280"),
                              anchor="center", tags=("player_pod", "status"))
        elif player_data.get('all_in'):
            canvas.create_text(x, y, text="ALL-IN", font=status_font,
                              fill=self.theme.get("status.allin.color", "#EF4444"),
                              anchor="center", tags=("player_pod", "status"))
        elif player_data.get('current_bet', 0) > 0:
            bet_amount = player_data['current_bet']
            if bet_amount >= 1000:
                bet_text = f"${bet_amount/1000:.1f}K"
            else:
                bet_text = f"${bet_amount}"
            canvas.create_text(x, y, text=bet_text, font=status_font,
                              fill=self.theme.get("action.bet", "#3B82F6"),
                              anchor="center", tags=("player_pod", "current_bet"))
    
    def render_dealer_button(self, canvas, x, y, size=20):
        """Render dealer button with enhanced visibility"""
        button_color = self.theme.get("dealer.buttonBg", "#F1F5F9")
        button_border = self.theme.get("dealer.buttonBorder", "#1E293B") 
        text_color = self.theme.get("dealer.buttonFg", "#1E293B")
        
        # Main button circle
        canvas.create_oval(x - size//2, y - size//2, x + size//2, y + size//2,
                          fill=button_color, outline=button_border, width=2,
                          tags=("dealer_button",))
        
        # "D" text
        canvas.create_text(x, y, text="D", font=("Inter", size//2, "bold"),
                          fill=text_color, anchor="center",
                          tags=("dealer_button",))
    
    def update_player_pod(self, canvas, player_data, is_acting=False):
        """Update existing player pod with new data"""
        pod_tag = f"pod_{player_data.get('name', 'empty')}"
        
        # Remove old pod elements
        canvas.delete(pod_tag)
        
        # Re-render with updated data
        # Note: This would need position information to re-render
        # In practice, this would be called from the seats component
        pass
    
    def highlight_acting_player(self, canvas, player_name):
        """Add highlight effect to acting player"""
        glow_color = self.theme.get("status.acting.glow", "#22C55E")
        
        # Add pulsing glow effect
        def pulse_glow(alpha=1.0, direction=1):
            # This would implement a pulsing glow animation
            # Tkinter doesn't support alpha directly, so this would use
            # color interpolation or repeated redrawing
            pass
    
    def clear_all_highlights(self, canvas):
        """Remove all player highlights"""
        canvas.delete("acting_glow")
        canvas.delete("player_highlight")
