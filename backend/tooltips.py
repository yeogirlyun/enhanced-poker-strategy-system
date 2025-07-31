#!/usr/bin/env python3
"""
ToolTip Module for Enhanced Poker Strategy GUI

Provides tooltip functionality with professional styling and enhanced features.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created tooltip system with professional theme integration
- Enhanced styling with dark theme compatibility
- Improved positioning and timing functionality
"""

import tkinter as tk
from tkinter import ttk
from gui_models import THEME, FONTS


class ToolTip:
    """
    Create a tooltip for a given widget with professional styling.
    
    Features:
    - Professional dark theme styling
    - Configurable delay and duration
    - Smart positioning to stay within screen bounds
    - Rich text support with formatting
    """
    
    def __init__(self, widget, text, delay=1000, duration=5000):
        """
        Initialize tooltip for a widget.
        
        Args:
            widget: The widget to attach tooltip to
            text: Tooltip text content
            delay: Delay before showing tooltip (ms)
            duration: How long to show tooltip (ms)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.duration = duration
        self.tooltip_window = None
        self.scheduled_show = None
        self.scheduled_hide = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Button-1>", self._on_click)  # Hide on click

    def _on_enter(self, event):
        """Handle mouse enter event."""
        self._schedule_show()

    def _on_leave(self, event):
        """Handle mouse leave event."""
        self._cancel_scheduled()
        self._schedule_hide()

    def _on_click(self, event):
        """Handle click event - hide tooltip immediately."""
        self._cancel_scheduled()
        self.hide_tooltip()

    def _schedule_show(self):
        """Schedule tooltip to show after delay."""
        self._cancel_scheduled()
        self.scheduled_show = self.widget.after(self.delay, self.show_tooltip)

    def _schedule_hide(self):
        """Schedule tooltip to hide after duration."""
        if self.tooltip_window:
            self.scheduled_hide = self.widget.after(self.duration, self.hide_tooltip)

    def _cancel_scheduled(self):
        """Cancel any scheduled show/hide events."""
        if self.scheduled_show:
            self.widget.after_cancel(self.scheduled_show)
            self.scheduled_show = None
        if self.scheduled_hide:
            self.widget.after_cancel(self.scheduled_hide)
            self.scheduled_hide = None

    def show_tooltip(self, event=None):
        """Show the tooltip window."""
        if self.tooltip_window or not self.text:
            return

        # Get widget position
        x, y, _, _ = self.widget.bbox("insert")
        if not x or not y:  # Widget not yet positioned
            return
            
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip window
        tw.configure(bg=THEME["secondary_bg"])
        tw.attributes("-topmost", True)
        
        # Create label with professional styling
        label = tk.Label(
            tw, 
            text=self.text, 
            justify=tk.LEFT,
            background=THEME["secondary_bg"],
            foreground=THEME["text"],
            relief=tk.SOLID, 
            borderwidth=1,
            font=FONTS["small"],
            padx=8,
            pady=4,
            wraplength=300  # Wrap long text
        )
        label.pack(ipadx=2, ipady=2)
        
        # Ensure tooltip stays within screen bounds
        self._adjust_position(tw)
        
        # Schedule auto-hide
        self._schedule_hide()

    def _adjust_position(self, tooltip_window):
        """Adjust tooltip position to stay within screen bounds."""
        tooltip_window.update_idletasks()
        
        # Get screen dimensions
        screen_width = tooltip_window.winfo_screenwidth()
        screen_height = tooltip_window.winfo_screenheight()
        
        # Get tooltip dimensions
        tooltip_width = tooltip_window.winfo_width()
        tooltip_height = tooltip_window.winfo_height()
        
        # Get current position
        x = tooltip_window.winfo_x()
        y = tooltip_window.winfo_y()
        
        # Adjust if tooltip goes off screen
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if y + tooltip_height > screen_height:
            y = y - tooltip_height - 50  # Move above widget
        
        # Ensure minimum position
        x = max(10, x)
        y = max(10, y)
        
        tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        self._cancel_scheduled()

    def update_text(self, new_text):
        """Update tooltip text content."""
        self.text = new_text
        if self.tooltip_window:
            # Update existing tooltip
            for child in self.tooltip_window.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=new_text)
                    break

    def destroy(self):
        """Clean up tooltip resources."""
        self.hide_tooltip()
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.widget.unbind("<Button-1>")


class RichToolTip(ToolTip):
    """
    Enhanced tooltip with rich text formatting support.
    
    Supports:
    - Bold text: **bold**
    - Italic text: *italic*
    - Line breaks: \n
    - Multiple paragraphs
    """
    
    def __init__(self, widget, text, delay=1000, duration=5000):
        super().__init__(widget, text, delay, duration)
        self.formatted_text = self._format_text(text)

    def _format_text(self, text):
        """Format text with basic markdown-like syntax."""
        if not text:
            return ""
        
        # Split into lines for processing
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Handle bold text: **text**
            line = line.replace('**', '')  # Simple bold removal for now
            # Handle italic text: *text*
            line = line.replace('*', '')   # Simple italic removal for now
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    def show_tooltip(self, event=None):
        """Show the tooltip with formatted text."""
        if self.tooltip_window or not self.formatted_text:
            return

        # Get widget position
        x, y, _, _ = self.widget.bbox("insert")
        if not x or not y:
            return
            
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip window
        tw.configure(bg=THEME["secondary_bg"])
        tw.attributes("-topmost", True)
        
        # Create text widget for rich formatting
        text_widget = tk.Text(
            tw,
            background=THEME["secondary_bg"],
            foreground=THEME["text"],
            relief=tk.SOLID,
            borderwidth=1,
            font=FONTS["small"],
            wrap=tk.WORD,
            width=40,
            height=5,
            padx=8,
            pady=4,
            state=tk.DISABLED
        )
        text_widget.pack(ipadx=2, ipady=2)
        
        # Insert formatted text
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, self.formatted_text)
        text_widget.config(state=tk.DISABLED)
        
        # Adjust size to content
        text_widget.update_idletasks()
        content_height = int(text_widget.index(tk.END).split('.')[0])
        text_widget.config(height=min(content_height, 8))  # Max 8 lines
        
        # Ensure tooltip stays within screen bounds
        self._adjust_position(tw)
        
        # Schedule auto-hide
        self._schedule_hide()


# --- Usage Examples ---
"""
# Basic tooltip
from tooltips import ToolTip

button = ttk.Button(root, text="Optimize")
button.pack()
ToolTip(button, "Run the strategy optimizer to improve decision tables.")

# Rich tooltip with formatting
from tooltips import RichToolTip

complex_button = ttk.Button(root, text="Advanced Settings")
complex_button.pack()
RichToolTip(complex_button, 
    "**Advanced Strategy Settings**\n\n"
    "Configure complex parameters for:\n"
    "* Position-based adjustments\n"
    "* Hand strength thresholds\n"
    "* Bet sizing strategies\n\n"
    "Use with caution - affects all calculations.")

# Tooltip with custom timing
ToolTip(widget, "Quick help", delay=500, duration=3000)
"""


def create_tooltip_for_widget(widget, text, rich=False, **kwargs):
    """
    Convenience function to create tooltips.
    
    Args:
        widget: The widget to attach tooltip to
        text: Tooltip text content
        rich: Whether to use rich text formatting
        **kwargs: Additional arguments for ToolTip constructor
    
    Returns:
        ToolTip or RichToolTip instance
    """
    if rich:
        return RichToolTip(widget, text, **kwargs)
    else:
        return ToolTip(widget, text, **kwargs)


# Common tooltip texts for the poker strategy system
COMMON_TOOLTIPS = {
    "font_size": "Adjust the font size for all UI elements. Affects readability and screen space usage.",
    "grid_size": "Change the size of the hand grid buttons. Larger sizes are easier to see but take more space.",
    "strategy_file": "Currently loaded strategy file. Shows the active strategy being used for calculations.",
    "hand_grid": "Visual representation of all poker hands. Colors indicate tier assignments and playability.",
    "tier_panel": "Manage hand strength tiers. Create, edit, and organize hands into strength categories.",
    "postflop_editor": "Edit postflop hand strength values. Fine-tune how hands are evaluated after the flop.",
    "decision_tables": "Configure decision matrices for different positions and situations.",
    "strategy_overview": "Comprehensive view of current strategy including statistics and tier information.",
    "optimization": "Advanced tools to optimize strategy parameters and improve decision accuracy.",
    "practice_session": "Interactive practice mode to test your strategy against simulated opponents.",
    "new_strategy": "Create a fresh strategy with default settings. Clears all current data.",
    "load_strategy": "Load a previously saved strategy file from disk.",
    "save_strategy": "Save current strategy to the active file.",
    "save_strategy_as": "Save current strategy with a new filename.",
    "refresh_panels": "Update all panels to reflect current strategy data.",
    "export_pdf": "Export strategy to PDF format for sharing or documentation.",
    "start_hand": "Begin a new practice hand with the selected number of players.",
    "submit_action": "Submit your action for the current practice hand.",
    "player_count": "Select the number of players for practice sessions (2-8 players).",
    "bet_size": "Enter the bet size for betting or raising actions.",
    "game_state": "Current state of the practice hand including cards, pot, and player actions.",
    "strategy_feedback": "Analysis of your actions compared to optimal strategy recommendations.",
    "session_stats": "Statistics from your practice session including win rate and decision accuracy."
} 