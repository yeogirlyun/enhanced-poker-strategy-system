"""
Enhanced Button Component with Casino-style Design
Based on the working old UI approach with direct color application
"""

import tkinter as tk
from typing import Callable, Optional


class EnhancedButton(tk.Label):
    """
    Casino-style button using tk.Label to avoid macOS system color overrides.
    Uses click bindings and hover effects like the old UI approach.
    """
    
    def __init__(self, parent, text: str, command: Optional[Callable] = None, 
                 theme_manager=None, button_type: str = "primary", **kwargs):
        
        self.theme_manager = theme_manager
        self.button_type = button_type
        self.is_disabled = False  # Track disabled state manually
        
        # Get theme colors
        theme = theme_manager.get_theme() if theme_manager else {}
        fonts = theme_manager.get_fonts() if theme_manager else {}
        
        # Determine button colors based on type - prefer per-type tokens, fall back to generic
        if button_type == "primary":
            btn_key = "primary"
        elif button_type == "danger":
            btn_key = "danger"
        else:
            btn_key = "secondary"

        self.default_bg = theme.get(f'btn.{btn_key}.bg', theme.get('btn.default.bg', '#1E1E1E'))
        self.default_fg = theme.get(f'btn.{btn_key}.fg', theme.get('btn.default.fg', '#E0E0E0'))
        self.hover_bg = theme.get(f'btn.{btn_key}.hoverBg', theme.get('btn.hover.bg', '#2D5A3D'))
        self.hover_fg = theme.get(f'btn.{btn_key}.hoverFg', theme.get('btn.hover.fg', '#E6C76E'))
        self.active_bg = theme.get(f'btn.{btn_key}.activeBg', theme.get('btn.active.bg', '#008F4C'))
        self.active_fg = theme.get(f'btn.{btn_key}.activeFg', theme.get('btn.active.fg', '#FFD700'))
        self.disabled_bg = theme.get(f'btn.{btn_key}.disabledBg', theme.get('btn.disabled.bg', '#2B2B2B'))
        self.disabled_fg = theme.get(f'btn.{btn_key}.disabledFg', theme.get('btn.disabled.fg', '#777777'))

        # Optional borders for premium look
        self.border_color = theme.get(f'btn.{btn_key}.border', theme.get('btn.default.border', '#A0A0A0'))
        self.hover_border_color = theme.get(f'btn.{btn_key}.hoverBorder', self.border_color)
        self.active_border_color = theme.get(f'btn.{btn_key}.activeBorder', self.hover_border_color)
        self.disabled_border_color = theme.get(f'btn.{btn_key}.disabledBorder', theme.get('divider', '#2A2622'))
        
        # Store the command for click binding
        self.command = command
        
        # Label configuration - Using tk.Label to avoid macOS color overrides
        config = {
            'text': text,
            'font': fonts.get('body', ('Segoe UI', 14, 'bold')),
            'relief': 'raised',  # Button-like appearance
            'borderwidth': 2,    # Button border
            'cursor': 'hand2',
            'pady': 12 if button_type == "primary" else 8,
            'padx': 20 if button_type == "primary" else 16,
            # Direct color application - Works with tk.Label!
            'bg': self.default_bg,
            'fg': self.default_fg,
        }
        
        config.update(kwargs)
        
        # Initialize label as button
        super().__init__(parent, **config)
        
        # Store colors for hover effects
        self.colors = {
            "normal": self.default_bg,
            "hover": self.hover_bg
        }
        
        # Bind events - Label approach
        self.bind('<Button-1>', self._on_click)  # Click event
        self.bind('<Enter>', self._on_enter)     # Hover enter
        self.bind('<Leave>', self._on_leave)     # Hover leave
        
        # Apply initial border
        self._apply_border(self.border_color)
    
    def _apply_border(self, color):
        """Apply border color for premium visual feedback"""
        # Simple 1px border via highlight; for a thicker look, wrap in a Frame
        self.config(highlightthickness=1, highlightbackground=color)
    
    def _on_click(self, event):
        """Handle click event with premium visual feedback"""
        if not self.is_disabled and self.command:
            # Visual feedback - press effect with border
            self._apply_border(self.active_border_color)
            self.config(bg=self.active_bg, fg=self.active_fg, relief='sunken')
            # Restore normal state after brief delay
            self.after(100, lambda: (
                self._apply_border(self.border_color),
                self.config(bg=self.colors["normal"], fg=self.default_fg, relief='raised')
            ))
            # Execute command
            self.command()
    
    def _on_enter(self, event):
        """Handle mouse enter (hover) with premium border effects"""
        if not self.is_disabled:
            self._apply_border(self.hover_border_color)
            self.config(bg=self.colors["hover"], fg=self.hover_fg)
    
    def _on_leave(self, event):
        """Handle mouse leave with border restoration"""
        if not self.is_disabled:
            self._apply_border(self.border_color)
            self.config(bg=self.colors["normal"], fg=self.default_fg)
    
    def refresh_theme(self):
        """Refresh colors when theme changes - EXACT old UI pattern"""
        if not self.theme_manager:
            return
            
        # Reload theme colors
        theme = self.theme_manager.get_theme()
        
        # Update color properties using per-type tokens
        if self.button_type == "primary":
            btn_key = "primary"
        elif self.button_type == "danger":
            btn_key = "danger"
        else:
            btn_key = "secondary"

        self.default_bg = theme.get(f'btn.{btn_key}.bg', theme.get('btn.default.bg', '#1E1E1E'))
        self.default_fg = theme.get(f'btn.{btn_key}.fg', theme.get('btn.default.fg', '#E0E0E0'))
        self.hover_bg = theme.get(f'btn.{btn_key}.hoverBg', theme.get('btn.hover.bg', '#2D5A3D'))
        self.hover_fg = theme.get(f'btn.{btn_key}.hoverFg', theme.get('btn.hover.fg', '#E6C76E'))
        self.active_bg = theme.get(f'btn.{btn_key}.activeBg', theme.get('btn.active.bg', '#008F4C'))
        self.active_fg = theme.get(f'btn.{btn_key}.activeFg', theme.get('btn.active.fg', '#FFD700'))
        self.disabled_bg = theme.get(f'btn.{btn_key}.disabledBg', theme.get('btn.disabled.bg', '#2B2B2B'))
        self.disabled_fg = theme.get(f'btn.{btn_key}.disabledFg', theme.get('btn.disabled.fg', '#777777'))

        # Update border colors
        self.border_color = theme.get(f'btn.{btn_key}.border', theme.get('btn.default.border', '#A0A0A0'))
        self.hover_border_color = theme.get(f'btn.{btn_key}.hoverBorder', self.border_color)
        self.active_border_color = theme.get(f'btn.{btn_key}.activeBorder', self.hover_border_color)
        self.disabled_border_color = theme.get(f'btn.{btn_key}.disabledBorder', theme.get('divider', '#2A2622'))
        
        # Update colors dict for hover effects
        self.colors = {
            "normal": self.default_bg,
            "hover": self.hover_bg
        }
        
        # Apply current colors and border
        self.config(
            bg=self.default_bg,
            fg=self.default_fg,
            activebackground=self.active_bg,
            activeforeground=self.active_fg
        )
        self._apply_border(self.border_color)

        
        print(f"🎨 Enhanced button refreshed: {self.button_type} -> bg:{self.default_bg}, hover:{self.hover_bg}")


class PrimaryButton(EnhancedButton):
    """Primary action button (Load Hand, etc.) - Prominent casino styling"""
    def __init__(self, parent, text: str, command: Optional[Callable] = None, 
                 theme_manager=None, **kwargs):
        super().__init__(parent, text, command, theme_manager, "primary", **kwargs)


class SecondaryButton(EnhancedButton):
    """Secondary action button (Next, Auto, Reset, etc.) - Subtle casino styling"""
    def __init__(self, parent, text: str, command: Optional[Callable] = None, 
                 theme_manager=None, **kwargs):
        super().__init__(parent, text, command, theme_manager, "secondary", **kwargs)
