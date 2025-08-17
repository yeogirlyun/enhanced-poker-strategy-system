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
        
        # Determine button colors based on type
        if button_type == "primary":
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
            self.disabled_bg = theme.get('btn.disabled.bg', '#2B2B2B')
            self.disabled_fg = theme.get('btn.disabled.fg', '#777777')
        else:  # secondary
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
            self.disabled_bg = theme.get('btn.disabled.bg', '#2B2B2B')
            self.disabled_fg = theme.get('btn.disabled.fg', '#777777')
        
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
    
    def _on_click(self, event):
        """Handle click event"""
        if not self.is_disabled and self.command:
            # Visual feedback - press effect
            self.config(bg=self.active_bg, fg=self.active_fg, relief='sunken')
            # Restore normal state after brief delay
            self.after(100, lambda: self.config(
                bg=self.colors["normal"], 
                fg=self.default_fg, 
                relief='raised'
            ))
            # Execute command
            self.command()
    
    def _on_enter(self, event):
        """Handle mouse enter (hover) - Label version"""
        if not self.is_disabled:
            self.config(bg=self.colors["hover"], fg=self.hover_fg)
    
    def _on_leave(self, event):
        """Handle mouse leave - Label version"""
        if not self.is_disabled:
            self.config(bg=self.colors["normal"], fg=self.default_fg)
    
    def refresh_theme(self):
        """Refresh colors when theme changes - EXACT old UI pattern"""
        if not self.theme_manager:
            return
            
        # Reload theme colors
        theme = self.theme_manager.get_theme()
        
        # Update color properties
        if self.button_type == "primary":
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
        else:
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
        
        # Update colors dict for hover effects
        self.colors = {
            "normal": self.default_bg,
            "hover": self.hover_bg
        }
        
        # Apply current colors - EXACT old UI approach
        self.config(
            bg=self.default_bg,
            fg=self.default_fg,
            activebackground=self.active_bg,
            activeforeground=self.active_fg
        )
    
    def refresh_theme(self):
        """Refresh button colors when theme changes"""
        if not self.theme_manager:
            return
            
        # Get updated theme
        theme = self.theme_manager.get_theme()
        
        # Update color properties based on button type
        if self.button_type == "primary":
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
            self.disabled_bg = theme.get('btn.disabled.bg', '#2B2B2B')
            self.disabled_fg = theme.get('btn.disabled.fg', '#777777')
        else:  # secondary
            self.default_bg = theme.get('btn.default.bg', '#1E1E1E')
            self.default_fg = theme.get('btn.default.fg', '#E0E0E0')
            self.hover_bg = theme.get('btn.hover.bg', '#7A1C1C')
            self.hover_fg = theme.get('btn.hover.fg', '#E6C76E')
            self.active_bg = theme.get('btn.active.bg', '#B22222')
            self.active_fg = theme.get('btn.active.fg', '#FFD700')
            self.disabled_bg = theme.get('btn.disabled.bg', '#2B2B2B')
            self.disabled_fg = theme.get('btn.disabled.fg', '#777777')
        
        # Update colors dict for hover effects
        self.colors = {
            "normal": self.default_bg,
            "hover": self.hover_bg
        }
        
        # Apply new colors immediately
        self.config(
            bg=self.default_bg,
            fg=self.default_fg,
            activebackground=self.active_bg,
            activeforeground=self.active_fg
        )
        
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
