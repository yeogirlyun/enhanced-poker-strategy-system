from ...state.selectors import get_seat_positions, get_num_seats
from ...services.theme_manager import ThemeManager

try:
    from .chip_graphics import ChipGraphics, BetDisplay as ChipBetDisplay
except Exception:
    # Fallback: define minimal ChipGraphics inline if chip_graphics module is missing
    class ChipGraphics:
        @staticmethod
        def draw_chip_stack(canvas, x, y, amount, theme, fonts, tags=()):
            # Simple circle + text fallback
            r = 16
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=theme.get("chip.gold","#D97706"), outline="black", width=1, tags=tags)
            canvas.create_text(x, y, text=str(amount), fill="white", font=fonts.get("font.body", ("Arial", 10, "bold")), tags=tags)
    class ChipBetDisplay:
        def render(self, canvas, pos, amount, theme, fonts):
            ChipGraphics.draw_chip_stack(canvas, pos[0], pos[1], amount, theme, fonts, tags=("layer:chips",))


def _tokens(canvas):
    # Prefer ThemeManager from widget tree
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")  # type: ignore[attr-defined]
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return (
        {
            "bet.bg": "#374151", 
            "bet.border": "#6B7280",
            "bet.text": "#FFD700",
            "bet.active": "#DC2626"
        }, 
        {"font.body": ("Arial", 12, "bold")}
    )


class BetDisplay:
    def __init__(self):
        self._bet_elements = {}  # Store bet display elements per seat
        self._chip_graphics = None  # Will be initialized when canvas is available
        self._chip_bet_display = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Initialize chip graphics if needed
        if self._chip_graphics is None:
            self._chip_graphics = ChipGraphics(c)
            self._chip_bet_display = ChipBetDisplay(c)
        
        # Get seats data from state
        seats_data = state.get("seats", [])
        if not seats_data:
            return
        
        count = len(seats_data)
        # Pass canvas dimensions to get correct seat positions
        positions = get_seat_positions(state, seat_count=count, 
                                     canvas_width=w, canvas_height=h)
        
        # Clear old bet displays that are no longer needed
        current_seats = set(range(len(seats_data)))
        old_seats = set(self._bet_elements.keys()) - current_seats
        for old_seat in old_seats:
            if old_seat in self._bet_elements:
                for element_id in self._bet_elements[old_seat].values():
                    try:
                        c.delete(element_id)
                    except Exception:
                        pass
                del self._bet_elements[old_seat]
        
        for idx, (x, y) in enumerate(positions):
            if idx >= len(seats_data):
                break
                
            seat = seats_data[idx]
            current_bet = seat.get('current_bet', 0) or seat.get('bet', 0)
            
            # Debug: Log what data we have for each seat
            print(f"🎯 Seat {idx} data: {seat}")
            print(f"🎯 Seat {idx} position: ({x}, {y}), current_bet: {current_bet}")
            
            # Initialize bet elements for this seat if needed
            if idx not in self._bet_elements:
                self._bet_elements[idx] = {}
            
            # Always show stack size, even when no bet
            self._add_stack_display(c, x, y, seat, idx)
            
            # Show current bet if any
            if current_bet > 0:
                self._add_bet_display(c, x, y, current_bet, idx)
            
            if current_bet > 0:
                # Position bet display prominently in front of the player
                # Use proper offset based on seat position to ensure visibility
                # Calculate offset based on seat angle to position bet in front of player
                import math
                num_seats = len(seats_data)
                seat_angle = -math.pi / 2 + (2 * math.pi * idx) / num_seats
                
                # Offset in direction player is facing (toward table center)
                # Use larger offset for better visibility
                offset_distance = 60  # Increased from 40 for better visibility
                offset_x = int(offset_distance * math.cos(seat_angle))
                offset_y = int(offset_distance * math.sin(seat_angle))
                
                bet_x = int(x + offset_x)
                bet_y = int(y + offset_y)
                
                print(f"🎯 Bet positioning for seat {idx}: seat({x},{y}) -> bet({bet_x},{bet_y})")
                print(f"   Angle: {math.degrees(seat_angle):.1f}°, offset: ({offset_x}, {offset_y})")
                
                # Clear old bet elements for this seat
                if idx in self._bet_elements:
                    for element_id in self._bet_elements[idx].values():
                        try:
                            c.delete(element_id)
                        except Exception:
                            pass
                    self._bet_elements[idx] = {}
                
                # Determine bet type for styling
                is_acting = seat.get('acting', False)
                last_action = seat.get('last_action', '')
                
                bet_type = "bet"
                if last_action == "call":
                    bet_type = "call"
                elif last_action in ["raise", "bet"]:
                    bet_type = "raise"
                elif is_acting:
                    bet_type = "active"
                
                # Create chip-based bet display using ChipAnimations
                try:
                    from .chip_animations import ChipAnimations
                    chip_anim = ChipAnimations(self._get_theme_manager(c))
                    
                    # Place bet chips in front of player (NOT flying to pot)
                    chip_elements = chip_anim.place_bet_chips(
                        c, bet_x, bet_y, current_bet, 
                        self._get_theme_tokens(c),
                        tags=("layer:bets", f"bet:{idx}")
                    )
                    
                    # Store all elements for cleanup
                    self._bet_elements[idx] = {
                        f"chip_{i}": elem_id for i, elem_id in enumerate(chip_elements)
                    }
                    
                    print(f"🎯 Bet chips placed for seat {idx}: ${current_bet} ({last_action}) at ({bet_x}, {bet_y})")
                    
                except Exception as e:
                    print(f"⚠️ Could not create chip-based bet display: {e}")
                    # Fallback to simple text display
                    self._create_fallback_bet_display(c, bet_x, bet_y, current_bet, last_action, idx)
            else:
                # No bet - hide bet display
                if idx in self._bet_elements:
                    for element_id in self._bet_elements[idx].values():
                        try:
                            c.delete(element_id)
                        except Exception:
                            pass
                    self._bet_elements[idx] = {}
    
    def _add_stack_display(self, canvas, x, y, seat, idx):
        """Add stack size display for the player"""
        stack_amount = seat.get('current_stack', seat.get('stack', 0))
        if stack_amount > 0:
            # Get sizing system from canvas widget tree
            sizing_system = self._get_sizing_system(canvas)
            
            # Get chip size and text size from sizing system
            chip_size = 12  # Default fallback
            text_size = 10  # Default fallback
            
            if sizing_system:
                chip_size = sizing_system.get_chip_size('stack')
                text_size = sizing_system.get_text_size('stack_amount')
            
            # Position stack display below the seat
            stack_x = x
            stack_y = y + 40
            
            # Create stack background
            stack_bg = canvas.create_rectangle(
                stack_x - chip_size * 2, stack_y - chip_size // 2,
                stack_x + chip_size * 2, stack_y + chip_size // 2,
                fill="#1F2937",  # Dark background
                outline="#6B7280",  # Gray outline
                width=1,
                tags=("layer:stacks", f"stack_bg:{idx}")
            )
            
            # Create stack amount text
            stack_text = canvas.create_text(
                stack_x, stack_y,
                text=f"${stack_amount}",
                font=("Arial", text_size, "bold"),
                fill="#10B981",  # Green for stack
                tags=("layer:stacks", f"stack_text:{idx}")
            )
            
            # Store for cleanup
            if idx not in self._bet_elements:
                self._bet_elements[idx] = {}
            self._bet_elements[idx][f'stack_bg'] = stack_bg
            self._bet_elements[idx][f'stack_text'] = stack_text
    
    def _add_bet_display(self, canvas, x, y, amount, idx):
        """Add bet display for current bet amount"""
        # Get sizing system from canvas widget tree
        sizing_system = self._get_sizing_system(canvas)
        
        # Get chip size and text sizes from sizing system
        chip_size = 25  # Default fallback
        amount_text_size = 10  # Default fallback
        
        if sizing_system:
            chip_size = sizing_system.get_chip_size('bet')
            amount_text_size = sizing_system.get_text_size('bet_amount')
        
        bet_tag = f"bet:{idx}"
        
        # Position bet display prominently in front of the player
        # Use angular offset to place it in front of the seat
        bet_x = x + int(chip_size * 0.8)  # Slightly to the right
        bet_y = y - int(chip_size * 0.6)  # Slightly above
        
        # Create background circle for bet amount
        bet_bg = canvas.create_oval(
            bet_x - chip_size, bet_y - chip_size // 2,
            bet_x + chip_size, bet_y + chip_size // 2,
            fill="#1F2937",  # Dark background
            outline="#FFD700",  # Gold outline
            width=2,
            tags=("layer:bets", bet_tag, "bet_bg")
        )
        
        # Create bet amount text
        bet_text = canvas.create_text(
            bet_x, bet_y,
            text=f"${amount}",
            font=("Arial", amount_text_size, "bold"),
            fill="#FFFFFF",  # White text
            tags=("layer:bets", bet_tag, "bet_text")
        )
        
        # Store elements for cleanup
        if idx not in self._bet_elements:
            self._bet_elements[idx] = {}
        self._bet_elements[idx]['bet_bg'] = bet_bg
        self._bet_elements[idx]['bet_text'] = bet_text
    
    def _create_fallback_bet_display(self, canvas, x, y, amount, action, idx):
        """Create a fallback bet display if chip system fails"""
        # Get sizing system from canvas widget tree
        sizing_system = self._get_sizing_system(canvas)
        
        # Get chip size and text sizes from sizing system
        chip_size = 25  # Default fallback
        amount_text_size = 10  # Default fallback
        action_text_size = 8   # Default fallback
        
        if sizing_system:
            chip_size = sizing_system.get_chip_size('bet')
            amount_text_size = sizing_system.get_text_size('bet_amount')
            action_text_size = sizing_system.get_text_size('action_label')
        
        bet_tag = f"bet:{idx}"
        
        # Create background circle for bet amount
        bet_bg = canvas.create_oval(
            x - chip_size, y - chip_size // 2,
            x + chip_size, y + chip_size // 2,
            fill="#1F2937",  # Dark background
            outline="#FFD700",  # Gold outline
            width=2,
            tags=("layer:bets", bet_tag, "bet_bg")
        )
        
        # Create bet amount text
        bet_text = canvas.create_text(
            x, y,
            text=f"${amount}",
            font=("Arial", amount_text_size, "bold"),
            fill="#FFFFFF",  # White text
            tags=("layer:bets", bet_tag, "bet_text")
        )
        
        # Add action type indicator below bet amount
        if action:
            action_y = y + chip_size // 2 + 5
            action_text = canvas.create_text(
                x, action_y,
                text=action.upper(),
                font=("Arial", action_text_size, "bold"),
                fill=self._get_action_color(action),
                tags=("layer:bets", bet_tag, "bet_action")
            )
            
            # Store all elements for cleanup
            self._bet_elements[idx] = {
                'bet_bg': bet_bg,
                'bet_text': bet_text,
                'bet_action': action_text
            }
        else:
            # Store elements for cleanup
            self._bet_elements[idx] = {
                'bet_bg': bet_bg,
                'bet_text': bet_text
            }
    
    def _get_theme_manager(self, canvas):
        """Get theme manager from canvas widget tree"""
        w = canvas
        while w is not None:
            try:
                if hasattr(w, "services"):
                    tm = w.services.get_app("theme")
                    if tm:
                        return tm
            except Exception:
                pass
            w = getattr(w, "master", None)
        return None
    
    def _get_theme_tokens(self, canvas):
        """Get theme tokens from canvas widget tree"""
        w = canvas
        while w is not None:
            try:
                if hasattr(w, "services"):
                    tm = w.services.get_app("theme")
                    if tm:
                        return tm.get_all_tokens()
            except Exception:
                pass
            w = getattr(w, "master", None)
        return {}
    
    def _get_action_color(self, action):
        """Get the appropriate color for an action type"""
        if action == "call":
            return "#10B981"  # Green
        elif action == "raise":
            return "#F59E0B"  # Orange
        elif action == "bet":
            return "#3B82F6"  # Blue
        elif action == "check":
            return "#6B7280"  # Gray
        elif action == "fold":
            return "#EF4444"  # Red
        else:
            return "#FFFFFF"  # White

    def _get_sizing_system(self, canvas):
        """Get sizing system from canvas widget tree"""
        w = canvas
        while w is not None:
            try:
                if hasattr(w, "services"):
                    tm = w.services.get_app("theme")
                    if tm and hasattr(tm, 'sizing_system'):
                        return tm.sizing_system
            except Exception:
                pass
            w = getattr(w, "master", None)
        return None
