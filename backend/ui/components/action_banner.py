#!/usr/bin/env python3
"""
ActionBanner - Visual notifications for poker actions
===================================================

This component displays banners and notifications for poker actions,
integrating with the EffectBus to show visual feedback for:
- Player actions (BET, CALL, CHECK, FOLD, etc.)
- Important events (SHOWDOWN, ALL_IN)
- Game state changes
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Any, Optional


class ActionBanner(tk.Frame):
    """
    ActionBanner displays visual notifications for poker actions.
    
    Features:
    - Animated banners for different action types
    - Color-coded by action importance
    - Auto-dismiss after configurable duration
    - Stacking multiple banners
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Banner configuration
        self.banner_duration = 3000  # milliseconds
        self.banner_height = 60
        self.banner_width = 300
        self.animation_duration = 300  # milliseconds
        
        # Active banners
        self.active_banners = []
        self.banner_counter = 0
        
        # Banner styles by type
        self.banner_styles = {
            "info": {
                "bg": "#3B82F6",  # Blue
                "fg": "white",
                "icon": "ℹ️"
            },
            "success": {
                "bg": "#10B981",  # Green
                "fg": "white",
                "icon": "✅"
            },
            "warning": {
                "bg": "#F59E0B",  # Yellow
                "fg": "black",
                "icon": "⚠️"
            },
            "highlight": {
                "bg": "#EF4444",  # Red
                "fg": "white",
                "icon": "🔥"
            },
            "action": {
                "bg": "#8B5CF6",  # Purple
                "fg": "white",
                "icon": "🎯"
            }
        }
        
        # Setup the banner container
        self._setup_banner_container()
        
        print("🎭 ActionBanner: Initialized")
    
    def _setup_banner_container(self):
        """Setup the banner container frame."""
        # Create a frame to hold banners (positioned at top-center)
        self.banner_container = tk.Frame(self)
        self.banner_container.pack(fill="x", padx=10, pady=5)
        
        # Configure grid for banner positioning
        self.banner_container.grid_columnconfigure(0, weight=1)
        self.banner_container.grid_columnconfigure(1, weight=0)
        self.banner_container.grid_columnconfigure(2, weight=1)
    
    def show_banner(self, message: str, banner_type: str = "info", duration_ms: Optional[int] = None):
        """
        Show a banner notification.
        
        Args:
            message: Banner message text
            banner_type: Type of banner (info, success, warning, highlight, action)
            duration_ms: Duration in milliseconds (None for default)
        """
        if banner_type not in self.banner_styles:
            banner_type = "info"
        
        # Create banner ID
        banner_id = f"banner_{self.banner_counter}"
        self.banner_counter += 1
        
        # Get banner style
        style = self.banner_styles[banner_type]
        
        # Create banner frame
        banner_frame = tk.Frame(
            self.banner_container,
            bg=style["bg"],
            relief="raised",
            borderwidth=2
        )
        
        # Position banner (center horizontally, stack vertically)
        row = len(self.active_banners)
        banner_frame.grid(row=row, column=1, pady=(5, 0), sticky="ew")
        
        # Create banner content
        icon_label = tk.Label(
            banner_frame,
            text=style["icon"],
            font=("Arial", 16),
            bg=style["bg"],
            fg=style["fg"]
        )
        icon_label.pack(side="left", padx=(10, 5))
        
        message_label = tk.Label(
            banner_frame,
            text=message,
            font=("Arial", 12, "bold"),
            bg=style["bg"],
            fg=style["fg"],
            wraplength=self.banner_width - 60
        )
        message_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add close button
        close_button = tk.Label(
            banner_frame,
            text="✕",
            font=("Arial", 12, "bold"),
            bg=style["bg"],
            fg=style["fg"],
            cursor="hand2"
        )
        close_button.pack(side="right", padx=(5, 10))
        
        # Bind close button
        close_button.bind("<Button-1>", lambda e: self._dismiss_banner(banner_id))
        
        # Store banner info
        banner_info = {
            "id": banner_id,
            "frame": banner_frame,
            "type": banner_type,
            "message": message,
            "created_at": time.time(),
            "duration": duration_ms or self.banner_duration
        }
        
        self.active_banners.append(banner_info)
        
        # Animate banner in
        self._animate_banner_in(banner_frame)
        
        # Schedule auto-dismiss
        self.after(banner_info["duration"], lambda: self._dismiss_banner(banner_id))
        
        print(f"🎭 ActionBanner: Showing {banner_type} banner: {message}")
        return banner_id
    
    def _animate_banner_in(self, banner_frame):
        """Animate banner sliding in from top."""
        # Start with banner above visible area
        banner_frame.grid_configure(row=len(self.active_banners) - 1)
        
        # Animate slide-in effect
        def slide_in(step=0, total_steps=10):
            if step <= total_steps:
                # Calculate position (slide down from top)
                progress = step / total_steps
                banner_frame.grid_configure(row=len(self.active_banners) - 1)
                
                if step < total_steps:
                    self.after(self.animation_duration // total_steps, 
                              lambda: slide_in(step + 1, total_steps))
        
        slide_in()
    
    def _dismiss_banner(self, banner_id: str):
        """Dismiss a banner by ID."""
        for i, banner_info in enumerate(self.active_banners):
            if banner_info["id"] == banner_id:
                # Animate banner out
                self._animate_banner_out(banner_info["frame"], i)
                break
    
    def _animate_banner_out(self, banner_frame, banner_index: int):
        """Animate banner sliding out."""
        def slide_out(step=0, total_steps=10):
            if step <= total_steps:
                # Calculate position (slide up and fade)
                progress = step / total_steps
                alpha = 1.0 - progress
                
                # Apply transparency effect
                try:
                    banner_frame.attributes = ("-alpha", alpha)
                except:
                    pass  # Some platforms don't support transparency
                
                if step < total_steps:
                    self.after(self.animation_duration // total_steps, 
                              lambda: slide_out(step + 1, total_steps))
                else:
                    # Remove banner completely
                    banner_frame.destroy()
                    
                    # Remove from active banners
                    self.active_banners = [b for b in self.active_banners 
                                         if b["frame"] != banner_frame]
                    
                    # Reposition remaining banners
                    self._reposition_banners()
        
        slide_out()
    
    def _reposition_banners(self):
        """Reposition remaining banners after one is dismissed."""
        for i, banner_info in enumerate(self.active_banners):
            banner_info["frame"].grid_configure(row=i)
    
    def show_poker_action(self, action_type: str, player_name: str = None, amount: int = None):
        """
        Show a banner for a poker action.
        
        Args:
            action_type: Type of poker action (BET, CALL, CHECK, FOLD, etc.)
            player_name: Name of the player performing the action
            amount: Amount involved in the action (if applicable)
        """
        # Determine banner type based on action
        if action_type in ["SHOWDOWN", "ALL_IN"]:
            banner_type = "highlight"
        elif action_type in ["BET", "RAISE"]:
            banner_type = "action"
        elif action_type in ["CALL", "CHECK"]:
            banner_type = "success"
        elif action_type == "FOLD":
            banner_type = "warning"
        else:
            banner_type = "info"
        
        # Build message
        if player_name:
            if amount:
                message = f"{player_name}: {action_type} {amount}"
            else:
                message = f"{player_name}: {action_type}"
        else:
            if amount:
                message = f"{action_type} {amount}"
            else:
                message = action_type
        
        # Show banner
        return self.show_banner(message, banner_type)
    
    def clear_all_banners(self):
        """Clear all active banners."""
        for banner_info in self.active_banners[:]:
            self._dismiss_banner(banner_info["id"])
        print("🎭 ActionBanner: All banners cleared")
    
    def get_active_banner_count(self) -> int:
        """Get the number of active banners."""
        return len(self.active_banners)


class NoopActionBanner:
    """No-op action banner for testing or when banners are not needed."""
    
    def __init__(self, *args, **kwargs):
        pass
    
    def show_banner(self, *args, **kwargs) -> str: return "noop"
    def show_poker_action(self, *args, **kwargs) -> str: return "noop"
    def clear_all_banners(self) -> None: pass
    def get_active_banner_count(self) -> int: return 0
