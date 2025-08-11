#!/usr/bin/env python3
"""
Modern Poker UI Widgets

Professional poker app style widgets including bet sliders, chip displays,
and modern action buttons based on current industry standards.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Callable, Optional
from core.gui_models import THEME, FONTS


class BetSliderWidget(tk.Frame):
    """
    Professional bet slider widget inspired by modern poker apps.
    Features a circular slider with chip-style visual feedback.
    """
    
    def __init__(self, parent, min_bet: float = 0, max_bet: float = 1000, 
                 current_bet: float = 0, on_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=THEME["secondary_bg"], **kwargs)
        
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.current_bet = current_bet
        self.on_change = on_change
        
        self.canvas_size = 200
        self.center_x = self.canvas_size // 2
        self.center_y = self.canvas_size // 2
        self.radius = 70
        self.knob_radius = 15
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create the slider components."""
        # Title
        title_label = tk.Label(
            self, 
            text="Bet Amount", 
            font=FONTS["header"],
            fg=THEME["text"],
            bg=THEME["secondary_bg"]
        )
        title_label.pack(pady=(10, 5))
        
        # Canvas for circular slider
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=THEME["secondary_bg"],
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Bet amount display
        self.amount_label = tk.Label(
            self,
            text=f"${self.current_bet:.0f}",
            font=FONTS["bet_amount"],
            fg=THEME["text_gold"],
            bg=THEME["secondary_bg"]
        )
        self.amount_label.pack(pady=5)
        
        # Quick bet buttons
        self._create_quick_buttons()
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        
        self._draw_slider()
    
    def _create_quick_buttons(self):
        """Create quick bet amount buttons."""
        button_frame = tk.Frame(self, bg=THEME["secondary_bg"])
        button_frame.pack(pady=10)
        
        # Quick bet percentages
        quick_bets = [
            ("1/4 Pot", 0.25),
            ("1/2 Pot", 0.5),
            ("3/4 Pot", 0.75),
            ("Pot", 1.0),
            ("All-In", 1.0)  # Will be handled specially
        ]
        
        for i, (text, multiplier) in enumerate(quick_bets):
            btn = tk.Button(
                button_frame,
                text=text,
                font=FONTS["small"],
                bg=THEME["widget_bg"],
                fg=THEME["text"],
                activebackground=THEME["button_call"],
                activeforeground=THEME["text"],
                border=1,
                relief="solid",
                command=lambda m=multiplier, t=text: self._quick_bet(m, t)
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def _draw_slider(self):
        """Draw the circular slider interface."""
        self.canvas.delete("all")
        
        # Draw outer ring (track)
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline=THEME["border_inactive"],
            width=3,
            fill=THEME["widget_bg"]
        )
        
        # Draw progress arc
        extent = self._get_angle_from_bet()
        if extent > 0:
            self.canvas.create_arc(
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.center_x + self.radius,
                self.center_y + self.radius,
                start=90,  # Start from top
                extent=-extent,  # Clockwise
                outline=THEME["chip_green"],
                width=6,
                style="arc"
            )
        
        # Draw knob
        knob_x, knob_y = self._get_knob_position()
        self.canvas.create_oval(
            knob_x - self.knob_radius,
            knob_y - self.knob_radius,
            knob_x + self.knob_radius,
            knob_y + self.knob_radius,
            fill=THEME["chip_gold"],
            outline=THEME["border_active"],
            width=2
        )
        
        # Draw center circle with min/max labels
        self.canvas.create_oval(
            self.center_x - 25,
            self.center_y - 25,
            self.center_x + 25,
            self.center_y + 25,
            fill=THEME["widget_bg"],
            outline=THEME["border_inactive"]
        )
        
        # Min/Max labels
        self.canvas.create_text(
            self.center_x - self.radius + 15, self.center_y + 5,
            text=f"${self.min_bet:.0f}",
            fill=THEME["text_muted"],
            font=FONTS["small"]
        )
        self.canvas.create_text(
            self.center_x + self.radius - 15, self.center_y + 5,
            text=f"${self.max_bet:.0f}",
            fill=THEME["text_muted"],
            font=FONTS["small"]
        )
    
    def _get_angle_from_bet(self) -> float:
        """Convert bet amount to angle (0-270 degrees)."""
        if self.max_bet <= self.min_bet:
            return 0
        
        progress = (self.current_bet - self.min_bet) / (self.max_bet - self.min_bet)
        return progress * 270  # 270 degrees for 3/4 circle
    
    def _get_knob_position(self) -> tuple:
        """Get knob position based on current bet."""
        angle = self._get_angle_from_bet()
        # Convert to radians and adjust for starting position (top)
        rad = math.radians(angle - 90)  # -90 to start from top
        
        knob_x = self.center_x + (self.radius * math.cos(rad))
        knob_y = self.center_y + (self.radius * math.sin(rad))
        
        return knob_x, knob_y
    
    def _get_bet_from_position(self, x: int, y: int) -> float:
        """Convert mouse position to bet amount."""
        # Calculate angle from center
        dx = x - self.center_x
        dy = y - self.center_y
        
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 90) % 360  # Adjust for starting position
        
        # Limit to 270 degrees
        if angle > 270:
            angle = 270
        
        # Convert to bet amount
        progress = angle / 270
        bet_amount = self.min_bet + (progress * (self.max_bet - self.min_bet))
        
        return max(self.min_bet, min(self.max_bet, bet_amount))
    
    def _on_click(self, event):
        """Handle mouse click on slider."""
        self._update_bet_from_mouse(event.x, event.y)
    
    def _on_drag(self, event):
        """Handle mouse drag on slider."""
        self._update_bet_from_mouse(event.x, event.y)
    
    def _update_bet_from_mouse(self, x: int, y: int):
        """Update bet amount from mouse position."""
        new_bet = self._get_bet_from_position(x, y)
        self.set_bet_amount(new_bet)
    
    def _quick_bet(self, multiplier: float, text: str):
        """Handle quick bet button clicks."""
        if text == "All-In":
            new_bet = self.max_bet
        else:
            # For pot-based bets, we'd need the current pot size
            # For now, use a percentage of max bet
            new_bet = self.min_bet + (multiplier * (self.max_bet - self.min_bet))
        
        self.set_bet_amount(new_bet)
    
    def set_bet_amount(self, amount: float):
        """Set the bet amount and update display."""
        self.current_bet = max(self.min_bet, min(self.max_bet, amount))
        self._update_display()
        
        if self.on_change:
            self.on_change(self.current_bet)
    
    def set_limits(self, min_bet: float, max_bet: float):
        """Update the betting limits."""
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.current_bet = max(min_bet, min(max_bet, self.current_bet))
        self._update_display()
    
    def _update_display(self):
        """Update the visual display."""
        self._draw_slider()
        self.amount_label.config(text=f"${self.current_bet:.0f}")


class ModernActionButton(tk.Button):
    """
    Modern poker action button with professional styling and hover effects.
    """
    
    def __init__(self, parent, action_type: str, text: str = None, **kwargs):
        # Get colors based on action type
        colors = self._get_action_colors(action_type)
        
        # Set default styling
        default_kwargs = {
            "font": FONTS["action_button"],
            "bg": colors["normal"],
            "fg": THEME["text"],
            "activebackground": colors["hover"],
            "activeforeground": THEME["text"],
            "relief": "flat",
            "border": 0,
            "cursor": "hand2",
            "pady": 12,
            "padx": 20
        }
        
        # Merge with provided kwargs
        default_kwargs.update(kwargs)
        
        super().__init__(parent, text=text or action_type.title(), **default_kwargs)
        
        self.action_type = action_type
        self.colors = colors
        
        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _get_action_colors(self, action_type: str) -> dict:
        """Get color scheme for action type."""
        color_map = {
            "call": {"normal": THEME["button_call"], "hover": THEME["button_call_hover"]},
            "raise": {"normal": THEME["button_raise"], "hover": THEME["button_raise_hover"]},
            "bet": {"normal": THEME["button_raise"], "hover": THEME["button_raise_hover"]},
            "fold": {"normal": THEME["button_fold"], "hover": THEME["button_fold_hover"]},
            "check": {"normal": THEME["button_check"], "hover": THEME["button_check_hover"]},
            "all_in": {"normal": THEME["button_allin"], "hover": THEME["button_allin_hover"]},
        }
        
        return color_map.get(action_type.lower(), {
            "normal": THEME["widget_bg"], 
            "hover": THEME["border_active"]
        })
    
    def _on_enter(self, event):
        """Handle mouse enter (hover)."""
        self.config(bg=self.colors["hover"])
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.config(bg=self.colors["normal"])
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button with visual feedback."""
        if enabled:
            self.config(state="normal", bg=self.colors["normal"])
        else:
            self.config(state="disabled", bg=THEME["border_inactive"])


class ChipStackDisplay(tk.Frame):
    """
    Professional chip stack visualization for bet and pot displays.
    """
    
    def __init__(self, parent, amount: float = 0, title: str = "Chips", **kwargs):
        super().__init__(parent, bg=THEME["table_felt"], **kwargs)
        
        self.amount = amount
        self.title = title
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create the chip display components."""
        # Title label
        self.title_label = tk.Label(
            self,
            text=self.title,
            font=FONTS["small"],
            fg=THEME["text_secondary"],
            bg=THEME["table_felt"]
        )
        self.title_label.pack(pady=(5, 2))
        
        # Chip stack canvas
        self.chip_canvas = tk.Canvas(
            self,
            width=80,
            height=60,
            bg=THEME["table_felt"],
            highlightthickness=0
        )
        self.chip_canvas.pack()
        
        # Amount label
        self.amount_label = tk.Label(
            self,
            text=f"${self.amount:,.0f}",
            font=FONTS["bet_amount"],
            fg=THEME["text_gold"],
            bg=THEME["table_felt"]
        )
        self.amount_label.pack(pady=(2, 5))
    
    def _draw_chip_stack(self):
        """Draw visual chip stack based on amount."""
        self.chip_canvas.delete("all")
        
        if self.amount <= 0:
            return
        
        # Calculate chip distribution
        chips = self._get_chip_breakdown(self.amount)
        
        x_center = 40
        y_bottom = 55
        chip_height = 4
        
        current_y = y_bottom
        
        # Draw chips from bottom up
        for chip_value, count in chips:
            color = self._get_chip_color(chip_value)
            
            for i in range(min(count, 10)):  # Max 10 chips per stack for display
                # Draw chip
                self.chip_canvas.create_oval(
                    x_center - 15, current_y - chip_height,
                    x_center + 15, current_y,
                    fill=color,
                    outline=THEME["border_inactive"],
                    width=1
                )
                current_y -= chip_height
                
                if current_y < 10:  # Don't stack too high
                    break
    
    def _get_chip_breakdown(self, amount: float) -> list:
        """Break down amount into chip denominations."""
        # Standard poker chip values
        chip_values = [100, 25, 5, 1]
        chips = []
        
        remaining = amount
        for value in chip_values:
            count = int(remaining // value)
            if count > 0:
                chips.append((value, count))
                remaining -= count * value
        
        return chips
    
    def _get_chip_color(self, value: float) -> str:
        """Get chip color based on value."""
        if value >= 100:
            return THEME["chip_black"]
        elif value >= 25:
            return THEME["chip_green"]
        elif value >= 5:
            return THEME["chip_red"]
        else:
            return THEME["chip_blue"]
    
    def set_amount(self, amount: float):
        """Update the displayed amount."""
        self.amount = amount
        self._update_display()
    
    def set_title(self, title: str):
        """Update the title."""
        self.title = title
        self.title_label.config(text=title)
    
    def _update_display(self):
        """Update the visual display."""
        self._draw_chip_stack()
        self.amount_label.config(text=f"${self.amount:,.0f}")


class PlayerSeatWidget(tk.Frame):
    """
    Modern player seat display with professional card room aesthetics.
    """
    
    def __init__(self, parent, player_name: str = "Player", stack: float = 0, 
                 is_active: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.player_name = player_name
        self.stack = stack
        self.is_active = is_active
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create the player seat components."""
        # Main seat frame
        self.seat_frame = tk.Frame(
            self,
            bg=THEME["secondary_bg"],
            relief="solid",
            border=2
        )
        self.seat_frame.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Player name
        self.name_label = tk.Label(
            self.seat_frame,
            text=self.player_name,
            font=FONTS["player_name"],
            fg=THEME["text"],
            bg=THEME["secondary_bg"]
        )
        self.name_label.pack(pady=(8, 2))
        
        # Stack amount
        self.stack_label = tk.Label(
            self.seat_frame,
            text=f"${self.stack:.0f}",
            font=FONTS["stack_amount"],
            fg=THEME["text_gold"],
            bg=THEME["secondary_bg"]
        )
        self.stack_label.pack(pady=(2, 8))
        
        # Card display area (placeholder)
        self.card_frame = tk.Frame(
            self.seat_frame,
            bg=THEME["secondary_bg"],
            height=30
        )
        self.card_frame.pack(fill="x", padx=10, pady=5)
    
    def set_active(self, active: bool):
        """Set the active state of the player seat."""
        self.is_active = active
        self._update_display()
    
    def set_stack(self, stack: float):
        """Update the player's stack."""
        self.stack = stack
        self.stack_label.config(text=f"${stack:.0f}")
    
    def set_name(self, name: str):
        """Update the player's name."""
        self.player_name = name
        self.name_label.config(text=name)
    
    def _update_display(self):
        """Update the visual appearance based on state."""
        if self.is_active:
            border_color = THEME["border_active"]
            self.seat_frame.config(highlightbackground=border_color, highlightthickness=3)
        else:
            border_color = THEME["border_inactive"]
            self.seat_frame.config(highlightbackground=border_color, highlightthickness=1)
