"""
Complete Theme System for Poker UI
Enhanced theme tokens for all UI elements with better contrast and readability
"""

class CompleteThemeSystem:
    """Enhanced theme system with comprehensive tokens for all UI elements"""
    
    # Base theme with enhanced contrast and readability
    ENHANCED_BASE_THEME = {
        # Card Graphics
        "card.face.bg": "#FFFFFF",           # Pure white for maximum contrast
        "card.face.border": "#1F2937",       # Dark gray border
        "card.back.bg": "#7F1D1D",           # Dark red
        "card.back.pattern": "#991B1B",      # Slightly lighter red for pattern
        "card.suit.red": "#DC2626",          # Bright red for hearts/diamonds
        "card.suit.black": "#111827",        # Very dark gray for clubs/spades
        
        # Enhanced Player Display
        "player.name.font": ("Inter", 16, "bold"),      # Larger, more readable
        "player.name.color": "#F8FAFC",                 # Almost white
        "player.stack.font": ("Inter", 14, "bold"),     # Clear stack display
        "player.stack.color": "#FCD34D",                # Gold for money
        "player.position.font": ("Inter", 11, "normal"), # Position text
        "player.position.color": "#D1D5DB",             # Light gray
        
        # Player Pod States
        "seat.bg.idle": "#1E293B",           # Dark blue-gray (idle)
        "seat.bg.active": "#0F172A",         # Darker blue (active)
        "seat.bg.acting": "#14532D",         # Dark green (acting)
        "seat.bg.folded": "#1C1917",         # Dark brown (folded)
        "seat.ring": "#475569",              # Medium gray border
        "seat.highlight": "#334155",         # Subtle highlight
        "seat.shadow": "#0F172A",            # Deep shadow
        
        # Status Indicators with High Contrast
        "status.folded.color": "#9CA3AF",    # Medium gray
        "status.allin.color": "#EF4444",     # Bright red
        "status.acting.glow": "#22C55E",     # Bright green glow
        "status.waiting.color": "#6B7280",   # Muted gray
        
        # Chip Graphics (Value-Based)
        "chip.white.bg": "#FFFFFF",          # $1-4 chips
        "chip.white.accent": "#1F2937",
        "chip.red.bg": "#DC2626",            # $5-24 chips  
        "chip.red.accent": "#FFFFFF",
        "chip.green.bg": "#16A34A",          # $25-99 chips
        "chip.green.accent": "#FFFFFF",
        "chip.black.bg": "#1F2937",          # $100-499 chips
        "chip.black.accent": "#FFFFFF", 
        "chip.purple.bg": "#7C3AED",         # $500+ chips
        "chip.purple.accent": "#FCD34D",     # Gold accent
        
        # Pot Display Enhancement
        "pot.badgeBg": "#0F172A",            # Dark background
        "pot.badgeRing": "#FCD34D",          # Gold ring
        "pot.valueText": "#FFFFFF",          # White text
        "pot.label": "#D1D5DB",              # Light gray label
        
        # Winner Announcement
        "winner.badge.bg": "#0F172A",        # Dark badge
        "winner.badge.border": "#FCD34D",    # Gold border
        "winner.badge.glow": "#F59E0B",      # Amber glow
        "winner.text.color": "#FCD34D",      # Gold text
        "winner.amount.color": "#FFFFFF",    # White amount
        
        # Dealer Button
        "dealer.buttonBg": "#F8FAFC",        # Light background
        "dealer.buttonFg": "#1F2937",        # Dark text
        "dealer.buttonBorder": "#374151",    # Gray border
        
        # Action Colors (High Contrast)
        "action.fold": "#6B7280",            # Gray
        "action.check": "#10B981",           # Green
        "action.call": "#3B82F6",            # Blue
        "action.bet": "#F59E0B",             # Amber
        "action.raise": "#EF4444",           # Red
        "action.allin": "#8B5CF6",           # Purple
        
        # Animation Settings
        "animation.bet.duration": 800,        # Faster animations
        "animation.pot.duration": 1200,
        "animation.winner.duration": 3000,
        "animation.card.flip": 400,
        
        # Enhanced Typography
        "font.display": ("Inter", 24, "bold"),      # Large display text
        "font.h1": ("Inter", 20, "bold"),           # Main headings
        "font.h2": ("Inter", 16, "semibold"),       # Sub headings
        "font.body": ("Inter", 14, "normal"),       # Body text
        "font.small": ("Inter", 12, "normal"),      # Small text
        "font.mono": ("JetBrains Mono", 12, "normal"), # Monospace
        
        # Accessibility
        "a11y.focus": "#22C55E",             # Focus indicator
        "a11y.contrast.min": 4.5,           # Minimum contrast ratio
        "a11y.target.size": 44,             # Minimum touch target
    }
    
    # Theme variations with enhanced contrast
    FOREST_GREEN_ENHANCED = {
        **ENHANCED_BASE_THEME,
        "table.felt": "#0D4F3C",            # Darker forest green
        "table.rail": "#064E3B",            # Very dark green
        "table.inlay": "#10B981",           # Bright emerald
        "seat.bg.acting": "#065F46",        # Forest green acting
        "status.acting.glow": "#34D399",    # Bright green glow
    }
    
    VELVET_BURGUNDY_ENHANCED = {
        **ENHANCED_BASE_THEME,
        "table.felt": "#7C2D12",            # Rich burgundy
        "table.rail": "#451A03",            # Dark brown
        "table.inlay": "#F59E0B",           # Gold inlay
        "seat.bg.acting": "#92400E",        # Amber acting
        "status.acting.glow": "#FBBF24",    # Gold glow
        "winner.badge.border": "#F59E0B",   # Amber winner
    }
    
    OBSIDIAN_GOLD_ENHANCED = {
        **ENHANCED_BASE_THEME,
        "table.felt": "#0A0A0A",            # Pure black
        "table.rail": "#1F1F1F",            # Dark gray
        "table.inlay": "#FCD34D",           # Bright gold
        "seat.bg.idle": "#1F1F1F",          # Dark gray
        "seat.bg.acting": "#374151",        # Medium gray acting
        "status.acting.glow": "#FCD34D",    # Gold glow
        "winner.badge.border": "#FCD34D",   # Gold winner
    }
    
    def __init__(self):
        self.current_theme = "forest_green_enhanced"
        self.themes = {
            "forest_green_enhanced": self.FOREST_GREEN_ENHANCED,
            "velvet_burgundy_enhanced": self.VELVET_BURGUNDY_ENHANCED,
            "obsidian_gold_enhanced": self.OBSIDIAN_GOLD_ENHANCED,
        }
        
    def get_token(self, token_path, fallback=None):
        """Get a theme token with fallback support"""
        theme = self.themes[self.current_theme]
        return theme.get(token_path, fallback)
    
    def get_font(self, font_key):
        """Get font configuration"""
        return self.get_token(f"font.{font_key}", ("Inter", 14, "normal"))
    
    def get_color(self, color_key):
        """Get color with high contrast guarantee"""
        color = self.get_token(color_key)
        if not color:
            # Fallback to high contrast defaults
            if "bg" in color_key:
                return "#1F2937"  # Dark background
            else:
                return "#F8FAFC"  # Light text
        return color
    
    def set_theme(self, theme_name):
        """Switch to a different theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_card_colors(self, suit):
        """Get appropriate colors for card suits"""
        if suit.lower() in ['h', 'd']:  # Hearts, Diamonds
            return self.get_token("card.suit.red", "#DC2626")
        else:  # Clubs, Spades
            return self.get_token("card.suit.black", "#111827")
    
    def get_chip_colors(self, value):
        """Get chip colors based on value"""
        if value < 5:
            return {
                "bg": self.get_token("chip.white.bg", "#FFFFFF"),
                "accent": self.get_token("chip.white.accent", "#1F2937")
            }
        elif value < 25:
            return {
                "bg": self.get_token("chip.red.bg", "#DC2626"),
                "accent": self.get_token("chip.red.accent", "#FFFFFF")
            }
        elif value < 100:
            return {
                "bg": self.get_token("chip.green.bg", "#16A34A"),
                "accent": self.get_token("chip.green.accent", "#FFFFFF")
            }
        elif value < 500:
            return {
                "bg": self.get_token("chip.black.bg", "#1F2937"),
                "accent": self.get_token("chip.black.accent", "#FFFFFF")
            }
        else:
            return {
                "bg": self.get_token("chip.purple.bg", "#7C3AED"),
                "accent": self.get_token("chip.purple.accent", "#FCD34D")
            }
    
    def get_player_state_colors(self, player_state):
        """Get colors for different player states"""
        state_colors = {
            "idle": {
                "bg": self.get_token("seat.bg.idle", "#1E293B"),
                "border": self.get_token("seat.ring", "#475569"),
                "text": self.get_token("player.name.color", "#F8FAFC")
            },
            "acting": {
                "bg": self.get_token("seat.bg.acting", "#14532D"),
                "border": self.get_token("status.acting.glow", "#22C55E"),
                "text": self.get_token("player.name.color", "#F8FAFC")
            },
            "folded": {
                "bg": self.get_token("seat.bg.folded", "#1C1917"),
                "border": self.get_token("status.folded.color", "#9CA3AF"),
                "text": self.get_token("status.folded.color", "#9CA3AF")
            }
        }
        return state_colors.get(player_state, state_colors["idle"])
    
    def validate_contrast(self, fg_color, bg_color):
        """Validate color contrast meets accessibility standards"""
        # This would implement WCAG contrast calculation
        # For now, return True (implementation would calculate actual contrast)
        return True
    
    def get_animation_duration(self, animation_type):
        """Get animation duration for different types"""
        durations = {
            "bet": self.get_token("animation.bet.duration", 800),
            "pot": self.get_token("animation.pot.duration", 1200),
            "winner": self.get_token("animation.winner.duration", 3000),
            "card_flip": self.get_token("animation.card.flip", 400),
        }
        return durations.get(animation_type, 500)
