#!/usr/bin/env python3
"""
Practice Session UI Module for Enhanced Poker Strategy GUI (Corrected)

This version resolves the game stall bug by making the UI a pure renderer
and letting the state machine control the entire game flow.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading # Still needed for bot action delays in the state machine
import time
import json
import os
import sys
from enum import Enum
from typing import Dict, List, Optional, Any

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.poker_state_machine import ImprovedPokerStateMachine, ActionType, PokerState
# from sound_manager import SoundManager  # Removed in cleanup
from core.gui_models import THEME, FONTS
from ui.components.tooltips import ToolTip

# Custom CardWidget class for properly sized playing cards
class CardWidget(tk.Canvas):
    """A custom widget to display a single, styled playing card."""
    def __init__(self, parent, width=50, height=70):
        super().__init__(parent, width=width, height=height, highlightthickness=1, highlightbackground="black", bg="white")
        self.width, self.height = width, height
        
        # Ensure canvas is properly configured for drawing
        self.config(width=width, height=height)
        
        # Initialize with card back
        self._draw_card_back()

    def set_card(self, card_str, is_folded=False):
        # Store the current card string
        self.current_card_str = card_str
        
        self.delete("all") # Clear previous drawing
        if not card_str or card_str == "**" or is_folded:
            self._draw_card_back(is_folded=is_folded)
            self.update()
            return

        # Set normal white background
        self.config(bg="white")
        
        # Draw the card content
        self._draw_card_content(card_str)
        
        # Force update to ensure the drawing is applied
        self.update()

    def _draw_card_content(self, card_str):
        """Draw the card content (rank and suit) on the canvas."""
        if not card_str or len(card_str) < 2:
            return
            
        rank, suit = card_str[0], card_str[1]
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_colors = {'h': '#c0392b', 'd': '#c0392b', 'c': 'black', 's': 'black'}
        color = suit_colors.get(suit, "black")
        
        # Use larger, clearer fonts
        self.create_text(self.width / 2, self.height / 2 - 5, text=rank, font=("Helvetica", 22, "bold"), fill=color)
        self.create_text(self.width / 2, self.height / 2 + 18, text=suit_symbols.get(suit, ""), font=("Helvetica", 16), fill=color)

    def _draw_card_back(self, is_folded=False):
        """Draws a professional-looking checkerboard pattern for the card back."""
        # Clear any existing content
        self.delete("all")
        
        if is_folded:
            # Draw folded card back - dark gray with no border
            dark_gray = "#404040"  # Dark gray for folded cards
            self.config(bg=dark_gray)
            
            # Draw a simple dark gray card with no border
            self.create_rectangle(0, 0, self.width, self.height, 
                                fill=dark_gray, outline="")
        else:
            # Define colors for regular card back
            dark_red = "#a51d2d"
            light_red = "#c0392b"
            border_color = "#8b0000"
            
            # Set the background color
            self.config(bg=dark_red)
            
            # Draw the border first
            self.create_rectangle(2, 2, self.width-2, self.height-2, 
                                fill=dark_red, outline=border_color, width=2)
            
            # Draw the checkerboard pattern with larger squares for better visibility
            square_size = 8
            for y in range(4, self.height-4, square_size):
                for x in range(4, self.width-4, square_size):
                    # Create alternating pattern
                    color = light_red if (x // square_size + y // square_size) % 2 == 0 else dark_red
                    self.create_rectangle(x, y, x + square_size, y + square_size, 
                                       fill=color, outline="")
            
            # Add a subtle center design element
            center_x, center_y = self.width // 2, self.height // 2
            self.create_oval(center_x-8, center_y-8, center_x+8, center_y+8, 
                            fill=light_red, outline=border_color, width=1)
    

    def set_folded(self):
        """Shows the card as folded (empty)."""
        self.set_card("", is_folded=True)
    


class PlayerPod(tk.Frame):
    """A modern widget for a player's area with enhanced stack display and active player highlighting."""
    def __init__(self, parent):
        # The main pod frame with highlightable border for active player indication
        super().__init__(parent, bg="#1a1a1a", highlightthickness=2, highlightbackground="#006400")
        
        # This frame holds the name and cards with a visible background
        self.info_frame = tk.Frame(self, bg="gray15", highlightthickness=2)
        self.info_frame.pack(pady=(0, 5))
        
        self.name_label = tk.Label(self.info_frame, text="", font=("Helvetica", 14, "bold"), bg="gray15", fg="white")
        self.name_label.pack(pady=5)

        self.cards_frame = tk.Frame(self.info_frame, bg="gray15")
        self.cards_frame.pack(pady=(5, 10), padx=10)
        
        self.card1 = CardWidget(self.cards_frame, width=50, height=70)
        self.card1.pack(side="left", padx=3)
        self.card2 = CardWidget(self.cards_frame, width=50, height=70)
        self.card2.pack(side="left", padx=3)
        
        # Ensure cards show card backs initially
        self.card1.set_card("")  # This will trigger card back drawing
        self.card2.set_card("")  # This will trigger card back drawing

        # --- ENHANCED: Modern Stack Display ---
        # This frame sits below the main info_frame
        self.stack_frame = tk.Frame(self, bg="#1a1a1a")
        self.stack_frame.pack()
        
        # Numerical stack display
        self.stack_label = tk.Label(self.stack_frame, text="", font=("Helvetica", 12, "bold"), bg="#1a1a1a", fg="white")
        self.stack_label.pack(fill='x', pady=(0, 2))
        
        # Graphical stack bar using ttk.Progressbar
        self.stack_bar = ttk.Progressbar(self.stack_frame, orient='horizontal', length=120, mode='determinate')
        self.stack_bar.pack(fill='x', pady=(0, 3))
        
        # Bet amount display
        self.bet_label = tk.Label(self.stack_frame, text="", font=("Helvetica", 10, "bold"), bg="#1a1a1a", fg="gold")
        self.bet_label.pack(fill='x')
        
        # Canvas for drawing chip graphics
        self.chip_canvas = tk.Canvas(self.stack_frame, width=50, height=50, bg="#1a1a1a", highlightthickness=0)
        self.chip_canvas.pack(side="left", padx=5)
        self.chip_canvas.config(width=50, height=50)
        
        # Initialize starting stack for progress bar
        self.starting_stack = 100.0  # Default starting stack

    def update_pod(self, data):
        """Updates all player information including stack bar and highlighting."""
        # Update name
        self.name_label.config(text=data.get("name", ""))
        
        # Update stack information
        stack_amount = data.get('stack', 0)
        bet_amount = data.get('bet', 0)
        starting_stack = data.get('starting_stack', stack_amount)
        
        # Update numerical stack display
        self.stack_label.config(text=f"${stack_amount:,.2f}")
        
        # Update bet display
        if bet_amount > 0:
            self.bet_label.config(text=f"Bet: ${bet_amount:,.2f}")
        else:
            self.bet_label.config(text="")
        
        # Update stack progress bar
        self.starting_stack = starting_stack if starting_stack > 0 else 100.0
        progress = (stack_amount / self.starting_stack) * 100
        self.stack_bar['value'] = min(progress, 100)  # Cap at 100%
        
        # Update chip graphics
        self._draw_chips(stack_amount)
    
    def set_active_player(self, is_active):
        """Applies a 'lighting effect' to indicate the active player."""
        if is_active:
            # Bright gold border for active player
            self.config(highlightbackground="gold", highlightthickness=3)
        else:
            # Standard border for inactive players
            self.config(highlightbackground="#006400", highlightthickness=2)

    def _draw_chips(self, stack):
        """Draws a graphical stack of chips based on the stack amount."""
        self.chip_canvas.delete("all")
        colors = ["#d35400", "#2980b9", "#27ae60"]  # Orange, Blue, Green chips
        
        if stack <= 0:
            return
        
        # Improved logic: Default 3 chips, then 5, then 7 for larger stacks
        if stack < 50:
            num_chips = 3  # Default minimum
        elif stack < 200:
            num_chips = 5  # Medium stacks
        else:
            num_chips = 7  # Large stacks
        
        # Make chips larger and more visible for the bigger canvas
        chip_width = 16
        chip_height = 18
        start_x = 12
        
        for i in range(num_chips):
            # Draw chips in a straight vertical tower
            y_offset = 45 - i * 3  # Vertical spacing for straight tower
            x_offset = start_x  # Same x position for all chips (straight tower)
            
            # Draw the main chip
            self.chip_canvas.create_oval(x_offset, y_offset, x_offset + chip_width, y_offset - chip_height, 
                                       fill=colors[i % 3], outline="black", width=1)
            
            # Add a highlight to make chips look more 3D
            self.chip_canvas.create_oval(x_offset + 2, y_offset - 3, x_offset + chip_width - 2, y_offset - chip_height + 3, 
                                       fill="", outline="white", width=1)

class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that correctly follows the
    state machine's flow.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        
        # CRITICAL FIX: Get the actual root Tk window for animation
        self.root = self.winfo_toplevel()
        
        self.strategy_data = strategy_data
        
        # Initialize missing attributes
        self.current_felt_color = "classic_green"  # Add missing attribute
        self.table_felt_colors = {
            "classic_green": {
                "outer": "#0B6623",
                "inner": "#228B22",
                "pattern": "#32CD32",
                "community_bg": "#228B22"
            },
            "dark_green": {
                "outer": "#0A4D0A",
                "inner": "#1B4F1B",
                "pattern": "#2E8B2E",
                "community_bg": "#1B4F1B"
            },
            "blue": {
                "outer": "#1E3A8A",
                "inner": "#2563EB",
                "pattern": "#3B82F6",
                "community_bg": "#2563EB"
            }
        }  # Add missing attribute
        
        # Initialize UI state tracking
        self.preserved_community_cards = []
        self.hand_completed = False
        self.preserved_pot_amount = 0.0  # Add pot preservation
        self.last_board_cards = []  # Track board changes to prevent unnecessary refreshes
        self.action_indicators = {}  # Track player action labels for animations
        self.last_action_player = None  # Track the last player who took an action
        
        # Initialize other attributes
        self.num_players = 6
        self.player_seats = [None] * self.num_players
        self.community_card_widgets = []
        self.pot_label = None
        self.pot_label_window = None
        self.pot_graphics = {}
        self.bet_size_var = tk.DoubleVar(value=0.0)
        self.bet_size_label = None
        self.last_action_label = None
        self.info_text = None
        self.session_info_labels = {}
        self.action_buttons = {}
        self.game_control_buttons = {}
        self.human_action_controls = {}  # Add missing initialization
        # Import and initialize sound manager
        from utils.sound_manager import SoundManager
        self.sfx = SoundManager()
        
        # Initialize state machine with proper root reference
        self.state_machine = ImprovedPokerStateMachine(
            num_players=6,
            strategy_data=strategy_data,
            root_tk=self.root  # Use the actual root window
        )
        
        # Set up callbacks after initialization
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_state_change = self._on_state_change
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_action_player_changed = self.update_action_player_highlighting
        self.state_machine.on_action_executed = self._handle_action_executed  # NEW: Selective updates for player actions
        self.state_machine.on_round_complete = self._handle_round_complete  # NEW: Handle street completion
        self.state_machine.on_dealing_cards = self._handle_dealing_start  # NEW: Handle card dealing start
        self.state_machine.on_single_card_dealt = self._handle_single_card_dealt  # NEW: Handle single card dealt
        self.state_machine.on_dealing_complete = self._handle_dealing_complete  # NEW: Handle dealing completion
        self.state_machine.on_log_entry = self.add_game_message
        
        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI layout with a responsive grid."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        right_panel_frame = ttk.Frame(self)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Session Info Area (Upper) with Scrollbar
        session_frame = ttk.LabelFrame(right_panel_frame, text="Session Information", padding=10)
        session_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create frame for session text and scrollbar
        session_text_frame = tk.Frame(session_frame)
        session_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Session text widget
        self.session_text = tk.Text(
            session_text_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=FONTS["main"],  # Use main font instead of small
            height=8,
            wrap=tk.WORD  # Enable word wrapping
        )
        self.session_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Session scrollbar
        self.session_scrollbar = ttk.Scrollbar(
            session_text_frame, 
            orient=tk.VERTICAL, 
            command=self.session_text.yview
        )
        self.session_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_text.config(yscrollcommand=self.session_scrollbar.set)
        
        # Action Messages Area (Lower) with Scrollbar
        action_frame = ttk.LabelFrame(right_panel_frame, text="Action Messages", padding=10)
        action_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create frame for action text and scrollbar
        action_text_frame = tk.Frame(action_frame)
        action_text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Action text widget
        # Use larger font for action messages (20% larger than main font)
        action_font_size = FONTS["main"][1] + 2  # Increase font size by 2 points
        action_font = (THEME["font_family"], action_font_size)
        self.info_text = tk.Text(
            action_text_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=action_font,  # Use larger font for action messages
            height=6,
            wrap=tk.WORD  # Enable word wrapping
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Action scrollbar
        self.action_scrollbar = ttk.Scrollbar(
            action_text_frame, 
            orient=tk.VERTICAL, 
            command=self.info_text.yview
        )
        self.action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=self.action_scrollbar.set)

        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        self._create_human_action_controls(controls_frame)

        self.canvas.bind("<Configure>", self._on_resize)
        
        # Initialize layout management system
        self.layout_manager = self.LayoutManager()
        
        # Force initial drawing after a short delay to ensure canvas has proper dimensions
        self.after(100, self._force_initial_draw)
    
    def _force_initial_draw(self):
        """Force initial drawing of the poker table and all elements."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width > 1 and height > 1:
            self._on_resize()
        else:
            # If canvas isn't ready yet, just initialize the table felt colors
            # Initialize table felt colors
            self.table_felt_colors = {
                "classic_green": {
                    "outer": "#013f28",
                    "inner": "#015939", 
                    "pattern": "#014a2f",
                    "community_bg": "#015939"
                },
                "royal_blue": {
                    "outer": "#1a365d",
                    "inner": "#2d5aa0",
                    "pattern": "#1e4a8a",
                    "community_bg": "#2d5aa0"
                },
                "burgundy_red": {
                    "outer": "#4a1a1a",
                    "inner": "#8b2d2d",
                    "pattern": "#6b1e1e",
                    "community_bg": "#8b2d2d"
                },
                "deep_purple": {
                    "outer": "#2d1a4a",
                    "inner": "#5a2d8b",
                    "pattern": "#4a1e6b",
                    "community_bg": "#5a2d8b"
                },
                "golden_brown": {
                    "outer": "#4a3a1a",
                    "inner": "#8b6b2d",
                    "pattern": "#6b4a1e",
                    "community_bg": "#8b6b2d"
                },
                "ocean_blue": {
                    "outer": "#1a4a4a",
                    "inner": "#2d8b8b",
                    "pattern": "#1e6b6b",
                    "community_bg": "#2d8b8b"
                },
                "forest_green": {
                    "outer": "#1a4a1a",
                    "inner": "#2d8b2d",
                    "pattern": "#1e6b1e",
                    "community_bg": "#2d8b2d"
                },
                "midnight_black": {
                    "outer": "#1a1a1a",
                    "inner": "#2d2d2d",
                    "pattern": "#1e1e1e",
                    "community_bg": "#2d2d2d"
                }
            }
            
            # Set default felt color
            self.current_felt_color = "classic_green"
    
    class LayoutManager:
        """Manages dynamic positioning to prevent overlays and ensure visibility."""
        
        def __init__(self):
            self.min_spacing = 20  # Minimum pixel spacing between elements
        
        def calculate_player_positions(self, width, height, num_players):
            """Calculate player seat positions with proper spacing."""
            center_x, center_y = width / 2, height / 2
            
            # Dynamic radius based on table size and number of players
            base_radius_x = width * 0.42
            base_radius_y = height * 0.35
            
            # Adjust for different player counts to prevent overcrowding
            if num_players <= 4:
                radius_x = base_radius_x * 0.9
                radius_y = base_radius_y * 0.9
            elif num_players <= 6:
                radius_x = base_radius_x
                radius_y = base_radius_y
            positions = []
            for i in range(num_players):
                angle = (2 * math.pi / num_players) * i - (math.pi / 2)
                x = center_x + radius_x * math.cos(angle)
                y = center_y + radius_y * math.sin(angle)
                positions.append((x, y))
            
            return positions
        
        def calculate_stack_positions(self, width, height, num_players):
            """Calculate stack graphics positions with proper spacing from player seats."""
            center_x, center_y = width / 2, height / 2
            
            # Stack graphics positioned much closer to table center to avoid overlapping with player seats
            # This ensures clear visibility of hole cards in player seat areas
            stack_radius_x = width * 0.25  # Reduced from 0.38 to move stacks closer to center
            stack_radius_y = height * 0.20  # Reduced from 0.31 to move stacks closer to center
            
            positions = []
            for i in range(num_players):
                angle = (2 * math.pi / num_players) * i - (math.pi / 2)
                x = center_x + stack_radius_x * math.cos(angle)
                y = center_y + stack_radius_y * math.sin(angle)
                positions.append((x, y))
            
            return positions
        
        def calculate_community_card_position(self, width, height):
            """Calculate community card area position."""
            center_x, center_y = width / 2, height / 2
            return (center_x, center_y)
        
        def calculate_pot_position(self, width, height):
            """Calculate pot display position."""
            center_x, center_y = width / 2, height / 2
            # Position pot further below community cards to avoid overlay
            return (center_x, center_y + 120)  # Increased from 80 to 120
        
        def calculate_bet_positions(self, width, height, num_players):
            """Calculate bet label positions - positioned to avoid overlay with stack display."""
            center_x, center_y = width / 2, height / 2
            
            # Bet labels positioned closer to table center than player seats to avoid overlay
            bet_radius_x = width * 0.25  # Closer to center than player seats
            bet_radius_y = height * 0.20  # Closer to center than player seats
            
            positions = []
            for i in range(num_players):
                angle = (2 * math.pi / num_players) * i - (math.pi / 2)
                x = center_x + bet_radius_x * math.cos(angle)
                y = center_y + bet_radius_y * math.sin(angle)
                positions.append((x, y))
            
            return positions
        
        def validate_positions(self, positions, min_distance=30):
            """Validate that positions don't overlap and adjust if necessary."""
            adjusted_positions = positions.copy()
            
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = adjusted_positions[i]
                    x2, y2 = adjusted_positions[j]
                    
                    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                    
                    if distance < min_distance:
                        # Adjust position to prevent overlap
                        angle = math.atan2(y2 - y1, x2 - x1)
                        new_x = x1 + min_distance * math.cos(angle)
                        new_y = y1 + min_distance * math.sin(angle)
                        adjusted_positions[j] = (new_x, new_y)
            
            return adjusted_positions
        
        def get_layout_info(self, width, height, num_players):
            """Get comprehensive layout information for debugging."""
            return {
                'table_size': (width, height),
                'num_players': num_players,
                'player_positions': self.calculate_player_positions(width, height, num_players),
                'stack_positions': self.calculate_stack_positions(width, height, num_players),
                'bet_positions': self.calculate_bet_positions(width, height, num_players),
                'community_position': self.calculate_community_card_position(width, height),
                'pot_position': self.calculate_pot_position(width, height)
            }
    
    # --- All _draw methods remain the same ---
    def _on_resize(self, event=None):
        self.canvas.delete("all")
        self._draw_table()
        self._draw_player_seats()
        self._draw_community_card_area()
        self._draw_pot_display()
        self.update_display()

    def _draw_table(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Get current felt colors
        felt_colors = self.table_felt_colors[self.current_felt_color]
        
        self.canvas.create_oval(width*0.05, height*0.1, width*0.95, height*0.9, fill=felt_colors["outer"], outline=THEME["border"], width=10)
        self.canvas.create_oval(width*0.06, height*0.11, width*0.94, height*0.89, fill=felt_colors["inner"], outline="#222222", width=2)
        x_start, x_end = int(width * 0.1), int(width * 0.9)
        y_start, y_end = int(height * 0.15), int(height * 0.85)
        for i in range(x_start, x_end, 20):
            for j in range(y_start, y_end, 20):
                if (((i - width/2)**2 / (width*0.4)**2) + ((j - height/2)**2 / (height*0.35)**2)) < 1:
                    if (i + j) % 40 == 0:
                        self.canvas.create_oval(i, j, i + 15, j + 15, fill=felt_colors["pattern"], outline="")

    def _draw_player_seats(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.player_seats = [{} for _ in range(self.num_players)]
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        
        # Use layout manager for positioning
        player_positions = self.layout_manager.calculate_player_positions(width, height, self.num_players)
        bet_positions = self.layout_manager.calculate_bet_positions(width, height, self.num_players)
        
        for i in range(self.num_players):
            seat_x, seat_y = player_positions[i]
            bet_x, bet_y = bet_positions[i]
            
            self._create_player_seat_widget(seat_x, seat_y, f"Player {i+1}", positions[i], i)
            
            # Create bet labels with proper positioning
            felt_colors = self.table_felt_colors[self.current_felt_color]
            bet_label = tk.Label(self.canvas, text="", bg=felt_colors["community_bg"], fg="yellow", font=FONTS["stack_bet"])
            bet_window = self.canvas.create_window(bet_x, bet_y, window=bet_label, anchor="center", state="hidden")
            self.player_seats[i]["bet_label_widget"] = bet_label
            self.player_seats[i]["bet_label_window"] = bet_window

    def _create_player_seat_widget(self, x, y, name, position, index):
        # Create a PlayerPod for professional stack display with chip graphics
        player_pod = PlayerPod(self.canvas)
        
        # Store references for updates
        self.player_seats[index] = {
            "frame": player_pod, 
            "name_label": player_pod.name_label, 
            "folded_label": None,  # Will be handled by PlayerPod
            "cards_label": player_pod.cards_frame,  # This is the cards frame
            "card_widgets": [player_pod.card1, player_pod.card2],  # Store individual card widgets
            "bet_label": None,  # Will be handled by PlayerPod
            "player_pod": player_pod  # Store the PlayerPod reference
        }
        self.canvas.create_window(x, y, window=player_pod, anchor="center")
        
        # Initialize the pod with player data
        player_data = {
            "name": f"{name} ({position})",
            "stack": 1000.0  # Default stack amount
        }
        player_pod.update_pod(player_data)
    
    # Removed _create_stack_graphics method - PlayerPod now handles stack display internally

    def _draw_community_card_area(self):
        """Draws the community card area in the center of the table."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Use layout manager for community card positioning
        community_x, community_y = self.layout_manager.calculate_community_card_position(width, height)
        
        # Create community card frame
        community_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=0)
        
        # Create title for community cards
        community_title = tk.Label(
            community_frame,
            text="Community Cards",
            bg=THEME["secondary_bg"],
            fg="white",
            font=FONTS["player_name"]  # Use existing font instead of non-existent community_title
        )
        community_title.pack(pady=2)
        
        # Create cards frame
        cards_frame = tk.Frame(community_frame, bg=THEME["secondary_bg"], bd=0)
        cards_frame.pack(pady=3)
        
        # Create five CardWidget instances for community cards
        self.community_card_widgets = []
        for i in range(5):
            card_widget = CardWidget(cards_frame, width=60, height=84)
            card_widget.pack(side=tk.LEFT, padx=3)
            self.community_card_widgets.append(card_widget)
        
        # Store the community frame for updates
        self.community_frame = community_frame
        self.canvas.create_window(community_x, community_y, window=community_frame, anchor="center")

    def _draw_pot_display(self):
        """Draws the pot display in the center of the table."""
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Use layout manager for pot positioning
        pot_x, pot_y = self.layout_manager.calculate_pot_position(width, height)
        
        # Create simple pot frame
        pot_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], bd=0)
        
        # Create simple pot title
        pot_title = tk.Label(
            pot_frame,
            text="Pot",
            bg=THEME["secondary_bg"],
            fg="white",
            font=FONTS["player_name"]
        )
        pot_title.pack(pady=2)
        
        # Create simple pot amount label
        self.pot_label = tk.Label(
            pot_frame,
            text="$0.00",
            bg=THEME["secondary_bg"],
            fg="yellow",
            font=FONTS["stack_bet"]
        )
        self.pot_label.pack(pady=2)
        
        # Store the pot frame for updates
        self.pot_frame = pot_frame
        self.canvas.create_window(pot_x, pot_y, window=pot_frame, anchor="center")
    
    # --- UI Update and Action Handling (Corrected) ---

    def _submit_human_action(self, action_str):
        """
        Submits the human's action to the state machine and does nothing else.
        The state machine will control all subsequent game flow via callbacks.
        """
        player = self.state_machine.get_action_player()
        if not player or not player.is_human:
            return

        # Get amount for bet/raise actions
        amount = 0
        if action_str in ["bet", "raise", "bet_or_raise"]:
            amount = self.bet_size_var.get()

        # Play industry-standard sound for the action
        self.sfx.play_action_sound(action_str, amount)

        # Provide immediate visual feedback that action was accepted
        self._set_action_buttons_processing()
        
        # Let the state machine handle EVERYTHING from here.
        # Use the new string-based execute_action method
        self.state_machine.execute_action_string(player, action_str, amount)
        
        # Hide controls after action is processed - better user experience
        self._show_game_control_buttons()

    def prompt_human_action(self, player):
        """Shows and configures the action controls for the human player using display state."""
        display_state = self.state_machine.get_display_state()
        actions = display_state.valid_actions

        self._show_action_buttons()
        
        # Pure rendering: Set states and labels directly from display state
        if 'fold' in actions:
            self.human_action_controls['fold'].config(
                state='normal' if actions['fold']['enabled'] else 'disabled',
                text=actions['fold']['label']
            )
        
        if 'check' in actions:
            self.human_action_controls['check'].config(
                state='normal' if actions['check']['enabled'] else 'disabled',
                text=actions['check']['label']
            )
        
        if 'call' in actions:
            self.human_action_controls['call'].config(
                state='normal' if actions['call']['enabled'] else 'disabled',
                text=actions['call']['label']
            )
        
        if 'bet' in actions:
            self.human_action_controls['bet_raise'].config(
                state='normal' if actions['bet']['enabled'] else 'disabled',
                text=actions['bet']['label']
            )
        elif 'raise' in actions:
            self.human_action_controls['bet_raise'].config(
                state='normal' if actions['raise']['enabled'] else 'disabled',
                text=actions['raise']['label']
            )

        # Configure bet slider using display state data
        valid_actions_raw = self.state_machine.get_valid_actions_for_player(player)
        min_bet_or_raise = valid_actions_raw.get('min_raise', self.state_machine.game_state.min_raise)
        max_bet = valid_actions_raw.get('max_bet', player.stack + player.current_bet)
        
        self.bet_slider.config(from_=min_bet_or_raise, to=max_bet)
        self.bet_size_var.set(min_bet_or_raise)
        self._update_bet_size_label()

    def start_new_hand(self):
        """Starts a new hand and resets the UI accordingly."""
        
        import sys
        print("🔥 UI DEBUG: start_new_hand() called from UI")
        sys.stdout.flush()
        
        # Clear preserved community cards and pot amount when starting new hand
        self.preserved_community_cards = []
        self.preserved_pot_amount = 0.0
        self.hand_completed = False
        self.last_board_cards = []  # Reset board tracking for new hand
        
        # Clear the winning announcement message when starting new hand
        if hasattr(self, 'last_action_label'):
            self.last_action_label.config(text="")
        
        # Clear community cards display when starting new hand
        for card_widget in self.community_card_widgets:
            card_widget.set_card("")  # Clear the card
        
        # Hide all folded labels when starting new hand
        for player_seat in self.player_seats:
            if player_seat and "folded_label" in player_seat:
                folded_label = player_seat["folded_label"]
                if folded_label:
                    folded_label.pack_forget()
        
        # Clear any winning cards data when starting new hand
        if hasattr(self, 'winning_cards'):
            self.winning_cards = []
        
        # Reset UI for new hand
        self._reset_ui_for_new_hand()
        
        # Start new hand in state machine
        try:
            import sys
            print("🔥 UI DEBUG: About to call self.state_machine.start_hand()")
            sys.stdout.flush()
            print(f"🔥 UI DEBUG: state_machine object = {self.state_machine}")
            sys.stdout.flush()
            print(f"🔥 UI DEBUG: state_machine type = {type(self.state_machine)}")
            sys.stdout.flush()
            
            self.state_machine.start_hand()
            
            print("🔥 UI DEBUG: state_machine.start_hand() completed successfully")
            sys.stdout.flush()
            
            # FIXED: Don't call update_display() immediately - let dealing animation handle it
            # The dealing animation will properly show cards at the right time
            print("🔥 UI DEBUG: Skipping immediate update_display() - waiting for dealing animation")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"❌ UI ERROR: Failed to start new hand: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()

    def handle_hand_complete(self, winner_info=None):
        """
        Handles hand completion by displaying the winner info received from the state machine.
        """
        
        # Add logging to track pot amounts
        pot_amount = winner_info.get("amount", 0) if winner_info else 0
        print(f"handle_hand_complete called with pot: ${pot_amount:.2f}")
        
        self.sfx.play("winner_announce")
        
        if winner_info and winner_info.get("name"):
            winner_names = winner_info["name"]
            pot_amount = winner_info["amount"]
            winning_hand = winner_info.get("hand", "")
            final_board = winner_info.get("board", [])

            # --- PRESERVE COMMUNITY CARDS ---
            # Store the final board cards to prevent them from disappearing
            self.preserved_community_cards = final_board.copy()
            self.hand_completed = True
            
            # --- PRESERVE POT AMOUNT ---
            # Store the pot amount to prevent it from resetting to $0
            self.preserved_pot_amount = pot_amount

            # --- ENHANCED: Better winner announcement and animation ---
            # Display the final community cards with proper coloring
            for i, card_widget in enumerate(self.community_card_widgets):
                if i < len(final_board):
                    card_widget.set_card(final_board[i])
                    # Force the card widget to update immediately
                    card_widget.update()
            # Force the canvas to refresh
            self.canvas.update()

            # FIRST: Get winner information and highlight winning cards BEFORE announcement
            winner_player = None
            if pot_amount > 0:
                # Handle split pots - winner_names may contain multiple names
                winner_names_list = [name.strip() for name in winner_names.split(', ')]
                for player in self.state_machine.game_state.players:
                    if player.name in winner_names_list:
                        winner_player = player
                        break
                
                # Store and highlight winning cards FIRST
                if winner_player and winner_player.cards:
                    hand_info = self.state_machine.get_hand_description_and_cards(
                        winner_player.cards, final_board
                    )
                    self.winning_cards = hand_info['winning_cards']
                    description = hand_info['description']
                    winning_cards = hand_info['winning_cards']
                else:
                    self.winning_cards = []
                    description = winning_hand if winning_hand != "Unknown" else ""
                    winning_cards = []
                
                # Create winner announcement message
                if description:
                    # Check if this is a split pot
                    if ',' in winner_names:
                        announcement = f"🏆 Split pot! {winner_names} each win ${pot_amount/len(winner_names_list):.2f}! ({description})"
                    else:
                        announcement = f"🏆 {winner_names} wins ${pot_amount:.2f}! ({description})"
                    if winning_cards:
                        announcement += f"\nWinning cards: {' '.join(winning_cards)}"
                else:
                    # Check if this is a split pot
                    if ',' in winner_names:
                        announcement = f"🏆 Split pot! {winner_names} each win ${pot_amount/len(winner_names_list):.2f}!"
                    else:
                        announcement = f"🏆 {winner_names} wins ${pot_amount:.2f}!"
                    if winning_hand and winning_hand != "Unknown":
                        announcement += f" ({winning_hand})"
                
                # Update pot label with winner info
                self.pot_label.config(text=f"Winner: {winner_names}!", fg=THEME["accent_secondary"])
                self.pot_label.update()  # Force pot label update
                
                # Add the winner announcement to the main game message area immediately
                self.add_game_message(announcement)
                
                # Also display winner announcement in action button area
                if hasattr(self, 'last_action_label'):
                    self.last_action_label.config(text=announcement)
                
                # ✅ FIXED: Only animate pot distribution to winner (consolidation happens at street completion)
                self._animate_pot_to_winner(winner_info, pot_amount)
        
        # Ensure animation triggers even for fold scenarios
        elif winner_info and winner_info.get("amount", 0) > 0:
            # Handle cases where pot_amount might be 0 but winner_info has amount
            pot_amount = winner_info.get("amount", 0)
            if pot_amount > 0:
                print(f"Triggering animation for fold scenario: ${pot_amount:.2f}")
                self._animate_pot_to_winner(winner_info, pot_amount)
        
        # Show game controls immediately (no delay)
        self._show_game_control_buttons()

    def animate_pot_distribution(self, winner_seat_index):
        """
        Triggers the visual animation of chips moving to the winner.
        This is the function you should call at the start of the showdown.
        """
        try:
            # Force the main window to process all pending drawing events.
            # This is the CRITICAL step to ensure we get correct coordinates.
            self.root.update_idletasks()

            winner_seat_data = self.player_seats[winner_seat_index]
            winner_seat_widget = winner_seat_data["player_pod"]  # Get the actual PlayerPod widget
            pot_widget = self.pot_label  # Assuming your pot display is self.pot_label

            # 1. Get Start and End coordinates using canvas coordinates instead of screen coordinates
            # Get pot position from layout manager
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
            pot_x, pot_y = self.layout_manager.calculate_pot_position(width, height)
            
            # Get winner position from layout manager
            player_positions = self.layout_manager.calculate_player_positions(width, height, self.num_players)
            winner_x, winner_y = player_positions[winner_seat_index]
            
            start_x = pot_x
            start_y = pot_y
            end_x = winner_x
            end_y = winner_y

            # Validate coordinates to ensure animation is visible
            if start_x == 0 and start_y == 0:
                print("Warning: Invalid start coordinates for animation")
                self.add_game_message("Animation failed: Invalid start coordinates")
                return
            
            if end_x == 0 and end_y == 0:
                print("Warning: Invalid end coordinates for animation")
                self.add_game_message("Animation failed: Invalid end coordinates")
                return

            # 2. Create the chip label with better visibility - use canvas coordinates
            chip_label = tk.Label(
                self.canvas, 
                text="💰", 
                font=("Arial", 40, "bold"), 
                bg="gold", 
                fg="black", 
                bd=2, 
                relief="raised"
            )
            # Create window on canvas instead of placing on root
            chip_window = self.canvas.create_window(start_x, start_y, window=chip_label, anchor="center")
            self.canvas.tag_raise(chip_window)  # Bring to front

            # 3. Start the animation immediately (no delay needed)
            self.root.after(15, lambda: self._move_chip_step(chip_window, start_x, start_y, end_x, end_y))  # Faster start delay to match other animations
            
        except Exception as e:
            print(f"Animation error: {e}")
            self.add_game_message(f"Animation failed: {str(e)}")

    def _move_chip_step(self, chip_window, x1, y1, x2, y2, step=0):
        """
        Private method to move the chip one step at a time.
        """
        total_steps = 30  # Faster animation: 30 steps instead of 50
        if step > total_steps:
            print(f"Animation complete at step {step}, calling _distribute_pot_to_winner")
            self.canvas.delete(chip_window)  # Animation is done, destroy the chip.
            
            # IMPORTANT: Now that the animation is finished,
            # tell the state machine to update the data model.
            self._distribute_pot_to_winner()
            return

        # Calculate the position for the current step
        new_x = x1 + (x2 - x1) * (step / total_steps)
        new_y = y1 + (y2 - y1) * (step / total_steps)
        self.canvas.coords(chip_window, new_x, new_y)

        # Schedule the next call to this method - faster timing
        self.root.after(15, lambda: self._move_chip_step(chip_window, x1, y1, x2, y2, step + 1))  # Reduced delay to 15ms for faster animation

    def _distribute_pot_to_winner(self):
        """
        Final method called after animation completes to update the winner's stack.
        """
        print("Animation complete - clearing pot and updating winner stack")
        
        # Clear the preserved pot amount to prevent override
        self.preserved_pot_amount = 0.0
        print(f"Cleared preserved_pot_amount to: {self.preserved_pot_amount}")
        
        # CRITICAL FIX: Reset the game state pot to 0 to prevent update_display override
        self.state_machine.game_state.pot = 0.0
        print(f"Reset game_state.pot to: {self.state_machine.game_state.pot}")
        
        # Clear the pot display
        self.pot_label.config(text="Pot: $0.00", fg="white")
        print(f"Pot cleared to: {self.pot_label.cget('text')}")
        
        # Update winner's stack in the state machine
        if hasattr(self, 'current_winner_seat') and self.current_winner_seat < len(self.player_seats):
            player_seat = self.player_seats[self.current_winner_seat]
            if player_seat and "player_pod" in player_seat:
                player_pod = player_seat["player_pod"]
                # Get current stack from PlayerPod
                current_stack_text = player_pod.stack_label.cget("text")
                try:
                    current_stack = float(current_stack_text.replace("$", "").replace(",", ""))
                    new_stack = current_stack + self.current_pot_amount
                    print(f"Updating winner stack: ${current_stack:.2f} + ${self.current_pot_amount:.2f} = ${new_stack:.2f}")
                    
                    # Update PlayerPod with new stack
                    pod_data = {
                        "name": player_pod.name_label.cget("text"),
                        "stack": new_stack,
                        "bet": 0,  # Clear bet
                        "starting_stack": player_pod.starting_stack
                    }
                    player_pod.update_pod(pod_data)
                    
                    # Force update display
                    self.update_display()
                except ValueError:
                    print("Error updating winner stack")
                    pass  # Handle invalid number format

    def _animate_pot_to_winner(self, winner_info, pot_amount):
        """Animate pot money moving to the winner's stack."""
        
        # Add logging to track animation calls
        print(f"Animating ${pot_amount:.2f} to {winner_info['name']}")
        
        # Handle multiple winners (comma-separated names)
        winner_names = winner_info['name'].split(', ')

        # Find the first winner's seat (or any winner if multiple)
        winner_seat = None
        for winner_name in winner_names:
            for i, seat in enumerate(self.player_seats):
                if seat and seat.get("player_pod"):
                    # Get player name from PlayerPod
                    player_pod = seat["player_pod"]
                    player_name = player_pod.name_label.cget("text")
                    
                    # Extract just the player name part (before the position)
                    # player_name format: "Player 1 (CO)" -> extract "Player 1"
                    player_name_clean = player_name.split(' (')[0]
                    if player_name_clean == winner_name:
                        winner_seat = i
                        break
            if winner_seat is not None:
                break
        
        # FIX: If we can't find the winner seat, use seat 0 as fallback
        if winner_seat is None:
            winner_seat = 0
            print(f"Warning: Could not find winner seat, using seat {winner_seat}")
        
        # Store winner info for the final distribution
        self.current_winner_seat = winner_seat
        self.current_pot_amount = pot_amount
        
        # Play sound effect for animation
        try:
            self.sfx.play("pot_win")
        except:
            pass  # Ignore if sound fails
        
        # Start the improved animation
        self.animate_pot_distribution(winner_seat)
    def add_game_message(self, message):
        """Add a message to the action messages area with enhanced formatting."""
        if hasattr(self, 'info_text'):
            # Enhanced keywords for vivid formatting
            action_keywords = [
                'FOLDS', 'CALLS', 'RAISES', 'BETS', 'CHECKS', 'folds', 'calls', 'raises', 'bets', 'checks',
                'attempting FOLD', 'attempting CALL', 'attempting RAISE', 'attempting BET', 'attempting CHECK'
            ]
            
            community_card_keywords = [
                'DEALING FLOP', 'DEALING TURN', 'DEALING RIVER', 'FLOP COMPLETE', 'TURN COMPLETE', 'RIVER COMPLETE',
                'Dealt card', 'Dealt flop', 'Dealt turn', 'Dealt river'
            ]
            
            showdown_keywords = [
                'SHOWDOWN', 'wins with', 'wins $', 'Winner(s):', '🏆', 'Main Pot', 'Side Pot'
            ]
            
            street_transition_keywords = [
                'TRANSITIONING TO', 'PREFLOP BETTING', 'FLOP BETTING', 'TURN BETTING', 'RIVER BETTING'
            ]
            
            # Check message type for appropriate formatting
            is_action = any(keyword.lower() in message.lower() for keyword in action_keywords)
            is_community_cards = any(keyword.lower() in message.lower() for keyword in community_card_keywords)
            is_showdown = any(keyword.lower() in message.lower() for keyword in showdown_keywords)
            is_street_transition = any(keyword.lower() in message.lower() for keyword in street_transition_keywords)
            
            # Always show important messages
            if is_action or is_community_cards or is_showdown or is_street_transition:
                self.info_text.config(state=tk.NORMAL)
                
                # Get current font size from the info_text widget
                current_font = self.info_text.cget("font")
                if isinstance(current_font, str):
                    # Parse font string like "Arial 10"
                    font_parts = current_font.split()
                    if len(font_parts) >= 2:
                        font_family = font_parts[0]
                        font_size = int(font_parts[1])
                    else:
                        font_family = "Arial"
                        font_size = 10
                else:
                    # Font is already a tuple
                    font_family = current_font[0]
                    font_size = current_font[1]
                
                # Create bold font for highlighted messages
                bold_font = (font_family, font_size, "bold")
                
                # Apply appropriate formatting based on message type
                if is_action:
                    # Bold yellow for player actions
                    formatted_message = f"🎯 {message}\n"
                    self.info_text.insert(tk.END, formatted_message)
                    # Apply yellow color to the last line
                    last_line_start = self.info_text.index("end-2c linestart")
                    last_line_end = self.info_text.index("end-1c")
                    self.info_text.tag_add("action_highlight", last_line_start, last_line_end)
                    self.info_text.tag_config("action_highlight", foreground="yellow", font=bold_font)
                    
                elif is_community_cards:
                    # Bold cyan for community card events
                    formatted_message = f"🎴 {message}\n"
                    self.info_text.insert(tk.END, formatted_message)
                    last_line_start = self.info_text.index("end-2c linestart")
                    last_line_end = self.info_text.index("end-1c")
                    self.info_text.tag_add("community_highlight", last_line_start, last_line_end)
                    self.info_text.tag_config("community_highlight", foreground="cyan", font=bold_font)
                    
                elif is_showdown:
                    # Bold yellow for showdown results
                    formatted_message = f"🏆 {message}\n"
                    self.info_text.insert(tk.END, formatted_message)
                    last_line_start = self.info_text.index("end-2c linestart")
                    last_line_end = self.info_text.index("end-1c")
                    self.info_text.tag_add("showdown_highlight", last_line_start, last_line_end)
                    self.info_text.tag_config("showdown_highlight", foreground="yellow", font=bold_font)
                    
                elif is_street_transition:
                    # Bold green for street transitions
                    formatted_message = f"🔄 {message}\n"
                    self.info_text.insert(tk.END, formatted_message)
                    last_line_start = self.info_text.index("end-2c linestart")
                    last_line_end = self.info_text.index("end-1c")
                    self.info_text.tag_add("transition_highlight", last_line_start, last_line_end)
                    self.info_text.tag_config("transition_highlight", foreground="green", font=bold_font)
                    
                else:
                    # Regular formatting for other important messages
                    self.info_text.insert(tk.END, f"{message}\n")
                
                self.info_text.see(tk.END)
                self.info_text.config(state=tk.DISABLED)
    
    def update_session_info(self):
        """Update the session information display."""
        if not self.state_machine.session_state:
            return
        
        session_info = self.state_machine.get_session_info()
        comprehensive_data = self.state_machine.get_comprehensive_session_data()
        
        self.session_text.config(state=tk.NORMAL)
        self.session_text.delete(1.0, tk.END)
        
        # Display session information
        display_text = "📊 SESSION INFORMATION\n"
        display_text += "=" * 40 + "\n\n"
        
        # Basic session info
        display_text += f"Session ID: {session_info.get('session_id', 'N/A')}\n"
        display_text += f"Duration: {session_info.get('session_duration', 0):.1f}s\n"
        display_text += f"Hands Played: {session_info.get('hands_played', 0)}\n"
        display_text += f"Human Wins: {session_info.get('human_wins', 0)}\n"
        display_text += f"Human Losses: {session_info.get('human_losses', 0)}\n"
        display_text += f"Big Blind: ${session_info.get('big_blind_amount', 1.0)}\n\n"
        
        # Current hand info
        game_info = self.state_machine.get_game_info()
        if game_info:
            display_text += "🎯 CURRENT HAND\n"
            display_text += "-" * 20 + "\n"
            display_text += f"State: {game_info.get('state', 'Unknown')}\n"
            display_text += f"Pot: ${game_info.get('pot', 0):.2f}\n"
            display_text += f"Current Bet: ${game_info.get('current_bet', 0):.2f}\n"
            display_text += f"Board: {game_info.get('board', [])}\n\n"
            
            # Valid actions
            valid_actions = game_info.get('valid_actions', {})
            if valid_actions:
                display_text += "✅ VALID ACTIONS\n"
                display_text += "-" * 15 + "\n"
                for action, is_valid in valid_actions.items():
                    if isinstance(is_valid, bool) and is_valid:
                        display_text += f"• {action.title()}\n"
                    elif isinstance(is_valid, dict) and is_valid.get('amount'):
                        display_text += f"• {action.title()}: ${is_valid['amount']:.2f}\n"
                display_text += "\n"
        
        # Session statistics
        if comprehensive_data:
            stats = comprehensive_data.get('session_statistics', {})
            if stats:
                display_text += "📈 SESSION STATS\n"
                display_text += "-" * 15 + "\n"
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        display_text += f"• {key.replace('_', ' ').title()}: {value}\n"
        
        # Table size information
        table_size_info = self.get_table_size_info()
        display_text += "\n🎮 TABLE LAYOUT\n"
        display_text += "-" * 15 + "\n"
        display_text += f"• Table Area: {table_size_info['table_percentage']:.1f}%\n"
        display_text += f"• Message Area: {table_size_info['message_percentage']:.1f}%\n"
        display_text += f"• Table Weight: {table_size_info['table_weight']}\n"
        display_text += f"• Message Weight: {table_size_info['message_weight']}\n"
        display_text += f"• Felt Color: {self.current_felt_color.replace('_', ' ').title()}\n"
        
        self.session_text.insert(1.0, display_text)
        self.session_text.config(state=tk.DISABLED)

    def _log_message(self, message: str):
        """Logs a message to the Game Messages panel."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END) # Auto-scroll to the bottom
        self.info_text.config(state=tk.DISABLED)

    def _create_human_action_controls(self, parent_frame):
        """Creates a fixed-position action bar for consistent user experience."""
        parent_frame.grid_columnconfigure(0, weight=1)
        self.action_bar_frame = ttk.Frame(parent_frame)
        self.action_bar_frame.grid(row=0, column=0, pady=5, sticky="ew")
        
        # Configure the action bar to maintain fixed layout
        self.action_bar_frame.grid_columnconfigure(1, weight=1)  # Center section expands
        self.action_bar_frame.grid_columnconfigure(3, weight=1)  # Right section expands
        
        # --- Game Control Buttons (Left - Fixed Position) ---
        control_frame = ttk.Frame(self.action_bar_frame)
        control_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Create larger buttons
        button_style = ttk.Style()
        button_style.configure('Large.TButton', padding=(18, 10))
        
        self.start_button = ttk.Button(
            control_frame, 
            text="🚀 Start New Hand", 
            style="Large.TButton", 
            command=self.start_new_hand
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.start_button, "Start a new poker hand")
        
        self.reset_button = ttk.Button(
            control_frame, 
            text="🔄 Reset Game", 
            style="Large.TButton",
            command=self._reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.reset_button, "Reset the entire game state")

        # --- Last Action Label (Center - Fixed Position) ---
        self.last_action_label = tk.Label(
            self.action_bar_frame, 
            text="", 
            font=("Helvetica", 14, "italic"),
            fg=THEME["text"],
            bg=THEME["secondary_bg"]
        )
        self.last_action_label.grid(row=0, column=1, padx=10, sticky="ew")
        
        # --- Action Buttons (Center - Fixed Position) ---
        action_frame = ttk.Frame(self.action_bar_frame)
        action_frame.grid(row=0, column=2, padx=10, sticky="ew")
        
        # Configure large button style for action buttons
        button_style.configure('LargeAction.TButton', padding=(14, 7))
        
        # Create all action buttons (always present, just enabled/disabled)
        self.human_action_controls['fold'] = ttk.Button(
            action_frame, 
            text="Fold", 
            style="LargeAction.TButton", 
            command=lambda: self._submit_human_action("fold")
        )
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['fold'], "Fold your hand and exit the current round")

        self.human_action_controls['check'] = ttk.Button(
            action_frame, 
            text="Check", 
            style="LargeAction.TButton",
            command=lambda: self._submit_human_action("check")
        )
        self.human_action_controls['check'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['check'], "Check (pass) if no bet to call")
        
        self.human_action_controls['call'] = ttk.Button(
            action_frame, 
            text="Call", 
            style="LargeAction.TButton",
            command=lambda: self._submit_human_action("call")
        )
        self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
        ToolTip(self.human_action_controls['call'], "Call the current bet")

        # --- Bet Sizing Slider (Right - Fixed Position) ---
        self.sizing_frame = ttk.Frame(self.action_bar_frame)
        self.sizing_frame.grid(row=0, column=3, padx=10, sticky="ew")
        
        self.bet_size_var = tk.DoubleVar()
        self.bet_slider = ttk.Scale(
            self.sizing_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.bet_size_var, 
            length=360
        )
        self.bet_slider.pack(fill=tk.X)
        self.bet_slider.bind("<B1-Motion>", self._update_bet_size_label)
        
        # Use larger font for bet size label (20% larger)
        large_font = (THEME["font_family"], FONTS["main"][1] + 4)  # Increased from +2 to +4
        self.bet_size_label = ttk.Label(
            self.sizing_frame, 
            text="$0.00", 
            font=large_font
        )
        self.bet_size_label.pack()

        # --- Preset Bet Buttons (Right - Fixed Position) ---
        preset_frame = ttk.Frame(self.action_bar_frame)
        preset_frame.grid(row=0, column=4, padx=10, sticky="e")
        
        self.preset_bet_buttons = {}
        
        # Half Pot button
        self.preset_bet_buttons['half_pot'] = ttk.Button(
            preset_frame,
            text="1/2 Pot",
            style="LargeAction.TButton",
            command=lambda: self._submit_preset_bet("half_pot")
        )
        self.preset_bet_buttons['half_pot'].pack(side=tk.LEFT, padx=2)
        ToolTip(self.preset_bet_buttons['half_pot'], "Bet half the pot size")
        
        # Pot button
        self.preset_bet_buttons['pot'] = ttk.Button(
            preset_frame,
            text="Pot",
            style="LargeAction.TButton",
            command=lambda: self._submit_preset_bet("pot")
        )
        self.preset_bet_buttons['pot'].pack(side=tk.LEFT, padx=2)
        ToolTip(self.preset_bet_buttons['pot'], "Bet the full pot size")
        
        # All-in button
        self.preset_bet_buttons['all_in'] = ttk.Button(
            preset_frame,
            text="All-In",
            style="LargeAction.TButton",
            command=lambda: self._submit_preset_bet("all_in")
        )
        self.preset_bet_buttons['all_in'].pack(side=tk.LEFT, padx=2)
        ToolTip(self.preset_bet_buttons['all_in'], "Bet your entire stack")
        
        # --- Bet/Raise Button (Right - Fixed Position) ---
        self.human_action_controls['bet_raise'] = ttk.Button(
            self.action_bar_frame, 
            text="Bet", 
            style="LargeAction.TButton", 
            command=self._submit_bet_raise
        )
        self.human_action_controls['bet_raise'].grid(row=0, column=5, padx=5, sticky="e")
        ToolTip(self.human_action_controls['bet_raise'], "Make a bet or raise")

        # Initially show only game control buttons
        self._show_game_control_buttons()

    def _set_action_buttons_processing(self):
        """Set action buttons to show 'processing' state with immediate visual feedback."""
        # Change all action buttons to show "Processing..." with visual feedback
        for button_name, widget in self.human_action_controls.items():
            if widget['state'] != tk.DISABLED:  # Only change enabled buttons
                widget.config(text="Processing...", state=tk.DISABLED)
        
        # Also update preset bet buttons
        for button in self.preset_bet_buttons.values():
            if button['state'] != tk.DISABLED:
                button.config(text="Processing...", state=tk.DISABLED)
        
        # Disable bet slider immediately
        if hasattr(self, 'bet_slider'):
            self.bet_slider.config(state=tk.DISABLED)

    def _show_game_control_buttons(self):
        """Shows only the game control buttons (Start/Reset) - Fixed Position."""
        
        # Enable game control buttons
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Disable all action buttons
        for widget in self.human_action_controls.values():
            widget.config(state=tk.DISABLED)
        
        # Disable preset bet buttons
        for button in self.preset_bet_buttons.values():
            button.config(state=tk.DISABLED)
        
        # Hide bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.config(state=tk.DISABLED)
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.config(text="")
        if hasattr(self, 'sizing_frame'):
            for child in self.sizing_frame.winfo_children():
                if hasattr(child, 'config'):
                    child.config(state=tk.DISABLED)

    def _show_action_buttons(self):
        """Shows the action buttons and hides game control buttons - Fixed Position."""
        
        # Disable game control buttons
        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        
        # Enable all action buttons
        for widget in self.human_action_controls.values():
            widget.config(state=tk.NORMAL)
        
        # Enable preset bet buttons
        for button in self.preset_bet_buttons.values():
            button.config(state=tk.NORMAL)
        
        # Show bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.config(state=tk.NORMAL)
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.config(text="Bet Size: $0.00")
        if hasattr(self, 'sizing_frame'):
            for child in self.sizing_frame.winfo_children():
                if hasattr(child, 'config'):
                    child.config(state=tk.NORMAL)


    def _reset_game(self):
        """Resets the game state and UI."""
        try:
            from tkinter import messagebox
            if messagebox.askyesno("Reset Game", "Are you sure you want to reset the game?"):
                self._log_message("🔄 Resetting game state...")
                
                # Reinitialize the state machine
                self.state_machine = ImprovedPokerStateMachine(
                    num_players=6, 
                    strategy_data=self.strategy_data
                )
                
                # Re-assign callbacks
                self.state_machine.on_action_required = self.prompt_human_action
                self.state_machine.on_hand_complete = self.handle_hand_complete
                self.state_machine.on_state_change = self.update_display
                self.state_machine.on_log_entry = self.add_game_message
                self.state_machine.on_action_player_changed = self.update_action_player_highlighting
                self.state_machine.on_action_executed = self._handle_action_executed  # NEW: Selective updates for player actions
                self.state_machine.on_round_complete = self._handle_round_complete  # NEW: Handle street completion
                self.state_machine.on_dealing_cards = self._handle_dealing_start  # NEW: Handle card dealing start
                self.state_machine.on_single_card_dealt = self._handle_single_card_dealt  # NEW: Handle single card dealt
                self.state_machine.on_dealing_complete = self._handle_dealing_complete  # NEW: Handle dealing completion
                
                # Reset UI
                self._reset_ui_for_new_hand()
                self.add_game_message("🔄 Game has been reset!")
                self._log_message("✅ Game reset completed")
                self.update_session_info()
        except Exception as e:
            self._log_message(f"❌ Error resetting game: {e}")

    def _reset_ui_for_new_hand(self):
        """Resets the UI for a new hand."""
        # Clear game messages
        if hasattr(self, 'info_text') and self.info_text is not None:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
        
        # Clear session info
        if hasattr(self, 'session_text') and self.session_text is not None:
            self.session_text.config(state=tk.NORMAL)
            self.session_text.delete(1.0, tk.END)
            self.session_text.config(state=tk.DISABLED)
        
        # Reset pot display
        if hasattr(self, 'pot_label') and self.pot_label is not None:
            self.pot_label.config(text="Pot: $0.00", fg="yellow")
        
        # Clear community cards display when starting new hand
        for card_widget in self.community_card_widgets:
            card_widget.set_card("")  # Clear the card
        
        # Reset board tracking for new hand
        self.last_board_cards = []
        
        # Hide all folded labels when starting new hand
        for player_seat in self.player_seats:
            if player_seat and "folded_label" in player_seat:
                folded_label = player_seat["folded_label"]
                if folded_label:
                    folded_label.pack_forget()
        
        # NEW: Clear all action indicators for new hand
        for player_index, action_label in self.action_indicators.items():
            if action_label and action_label.winfo_exists():
                action_label.destroy()
        self.action_indicators.clear()
        self.last_action_player = None
        
        # Reset player displays and clear all cards
        for player_seat in self.player_seats:
            if player_seat:
                frame = player_seat.get("frame")
                if frame:
                    frame.config(bg=THEME["secondary_bg"])
                
                # Clear old cards_label (legacy)
                cards_label = player_seat.get("cards_label")
                if cards_label:
                    try:
                        if hasattr(cards_label, 'config'):
                            cards_label.config(text="")
                        elif hasattr(cards_label, 'set_card'):
                            cards_label.set_card("")  # For CardWidget
                    except Exception as e:
                        print(f"Warning: Could not reset cards_label: {e}")
                
                # FIXED: Clear card_widgets properly for new hand
                card_widgets = player_seat.get("card_widgets", [])
                for i, widget in enumerate(card_widgets):
                    try:
                        old_card = getattr(widget, '_current_card', None)
                        widget.set_card("")  # Clear card display
                        widget._current_card = None  # Clear stored card data
                        # DEBUG: Log card clearing for human player
                        if self.player_seats.index(player_seat) == 0:
                            self._log_message(f"🐛 CLEAR DEBUG - Player 0 card {i}: {old_card} -> None")
                    except Exception as e:
                        print(f"Warning: Could not reset card_widget: {e}")
                
                self._log_message(f"🃏 Cleared all cards for player seat {self.player_seats.index(player_seat)}")
                
                bet_label = player_seat.get("bet_label")
                if bet_label:
                    # Handle different widget types safely
                    try:
                        if hasattr(bet_label, 'config'):
                            bet_label.config(text="")
                        elif hasattr(bet_label, 'set_text'):
                            bet_label.set_text("")
                    except Exception as e:
                        print(f"Warning: Could not reset bet_label: {e}")
                
                # Hide prominent bet displays
                bet_label_widget = player_seat.get("bet_label_widget")
                bet_label_window = player_seat.get("bet_label_window")
                if bet_label_widget and bet_label_window:
                    self.canvas.itemconfig(bet_label_window, state="hidden")
        
        # Show game control buttons
        self._show_game_control_buttons()
    
    def update_single_player(self, player_index: int, game_info: dict = None):
        """Update only a specific player's display elements efficiently."""
        if game_info is None:
            game_info = self.state_machine.get_game_info()
            if not game_info:
                return
        
        if not hasattr(self, 'player_seats') or not self.player_seats:
            return
            
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        player_info = game_info['players'][player_index]
        player_pod = player_seat.get("player_pod")
        
        # Update PlayerPod with new data including bet information
        if player_pod:
            # Clear bet amounts after hand completion
            bet_amount = 0 if self.hand_completed else player_info.get('current_bet', 0)
            
            pod_data = {
                "name": f"{player_info['name']} ({player_info['position']})",
                "stack": player_info['stack'],
                "bet": bet_amount,
                "starting_stack": 100.0  # Default starting stack for progress bar
            }
            player_pod.update_pod(pod_data)
            
            # Set active player highlighting (no highlighting after hand completion)
            is_active_turn = (player_index == game_info.get('action_player', -1)) and not self.hand_completed
            player_pod.set_active_player(is_active_turn)
        
        # Update frame highlighting
        frame = player_seat["frame"]
        action_player = game_info.get('action_player', -1)
        
        if player_index == action_player and not self.hand_completed:
            frame.config(bg=THEME["accent_primary"])
        else:
            frame.config(bg=THEME["secondary_bg"])
        
        # Update the prominent bet display on the table
        bet_label_widget = player_seat.get("bet_label_widget")
        bet_label_window = player_seat.get("bet_label_window")
        if bet_label_widget and bet_label_window:
            # Clear bet displays after hand completion
            if self.hand_completed:
                self.canvas.itemconfig(bet_label_window, state="hidden")
            else:
                current_bet = player_info.get("current_bet", 0.0)
                if current_bet > 0 and player_info['is_active']:
                    bet_label_widget.config(text=f"💰 ${current_bet:.2f}")
                    self.canvas.itemconfig(bet_label_window, state="normal")
                else:
                    self.canvas.itemconfig(bet_label_window, state="hidden")

    def update_action_player_highlighting(self, player_or_game_info=None):
        """Update only the action player highlighting efficiently."""
        # Handle both Player object (from callback) and dict (from direct call)
        if player_or_game_info is None or hasattr(player_or_game_info, 'name'):
            # Either None or Player object - get fresh game info
            game_info = self.state_machine.get_game_info()
        else:
            # Already a game_info dict
            game_info = player_or_game_info
            
        if not game_info:
            return
        
        if not hasattr(self, 'player_seats') or not self.player_seats:
            return
            
        action_player = game_info.get('action_player', -1)
        
        # Update highlighting for all players (this is still needed for turn changes)
        for i, player_seat in enumerate(self.player_seats):
            if not player_seat:
                continue
                
            frame = player_seat["frame"]
            player_pod = player_seat.get("player_pod")
            
            # Update frame highlighting
            if i == action_player and not self.hand_completed:
                frame.config(bg=THEME["accent_primary"])
            else:
                frame.config(bg=THEME["secondary_bg"])
                
            # Update player pod highlighting
            if player_pod:
                is_active_turn = (i == action_player) and not self.hand_completed
                player_pod.set_active_player(is_active_turn)

    def update_pot_display_only(self, pot_amount: float = None):
        """Update only the pot display efficiently."""
        if pot_amount is None:
            game_info = self.state_machine.get_game_info()
            if not game_info:
                return
            pot_amount = game_info['pot']
            
        # Use preserved pot amount if hand is completed
        if self.hand_completed and self.preserved_pot_amount > 0:
            pot_amount = self.preserved_pot_amount
        
        self.update_pot_amount(pot_amount)
    
    def _handle_action_executed(self, player_index: int, action: str, amount: float):
        """Handle when a player action is executed - use selective updates."""
        # Animate the specific player's action immediately
        self._animate_player_action(player_index, action, amount)
        
        # Handle fold action - set cards to folded state
        if action.upper() == "FOLD":
            self._handle_fold_action(player_index)
        
        # Update betting graphics immediately using the action data we have
        self._update_player_bet_display_immediate(player_index, action, amount)
        
        # Update pot display (since actions can change the pot)
        self.update_pot_display_only()
        
        # Action player highlighting will be handled by on_action_player_changed callback separately
        
        self._log_message(f"🎯 Selective update: Player {player_index} {action} ${amount:.2f}")
    
    def _handle_fold_action(self, player_index: int):
        """Handle when a player folds - set their cards to folded state."""
        if not hasattr(self, 'player_seats') or not self.player_seats:
            return
            
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        player_pod = player_seat.get("player_pod")
        
        if player_pod:
            # Set both cards to folded state
            player_pod.card1.set_folded()
            player_pod.card2.set_folded()
            self._log_message(f"🃏 Player {player_index} cards set to folded state")
    
    def _update_player_bet_display_immediate(self, player_index: int, action: str, amount: float):
        """Update a player's bet display immediately after their action."""
        if not hasattr(self, 'player_seats') or not self.player_seats:
            return
            
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        
        # Update the prominent bet display on the table
        bet_label_widget = player_seat.get("bet_label_widget")
        bet_label_window = player_seat.get("bet_label_window")
        if bet_label_widget and bet_label_window:
            if action.upper() in ["BET", "RAISE", "CALL"] and amount > 0:
                bet_label_widget.config(text=f"💰 ${amount:.2f}")
                self.canvas.itemconfig(bet_label_window, state="normal")
                self._log_message(f"💰 Updated bet display for Player {player_index}: ${amount:.2f}")
                
                # ✅ FIXED: Only update bet display - money stays in front of player until street completion
                # No individual chip animations - bet displays will consolidate to pot at street end
                self._log_message(f"💰 Updated bet display for {action.upper()} ${amount:.2f}")
                self.add_game_message(f"💰 {action.upper()} ${amount:.2f} - money stays in front of player")
            else:
                # Hide bet display for non-betting actions
                self.canvas.itemconfig(bet_label_window, state="hidden")
    
    def update_display(self, new_state=None):
        """Updates the UI using display state from the state machine."""
        # Safety check: Don't update if UI isn't ready yet
        if not hasattr(self, 'pot_label') or self.pot_label is None:
            return
            
        display_state = self.state_machine.get_display_state()
        if not display_state:
            self._log_message("DEBUG: update_display called but no display_state available.")
            return

        # Update pot and current bet display using display state
        self.update_pot_amount(display_state.pot_amount)
        
        # Show current bet information in message area if there's a current bet
        if display_state.current_bet > 0:
            self.add_game_message(f"💰 Current Bet: ${display_state.current_bet:.2f}")

        # Update community cards using display state
        board_cards = display_state.community_cards
        if board_cards:
            self._draw_community_cards(board_cards)

        # Update player positions and highlights using display state
        for i, (position, highlight) in enumerate(zip(display_state.layout_positions, display_state.player_highlights)):
            if i < len(self.player_seats) and self.player_seats[i]:
                self._update_player_position(i, position, highlight)

        # Update action controls using display state
        valid_actions = display_state.valid_actions
        if valid_actions:
            self._update_action_controls(valid_actions)
    

    
    def _update_bet_size_label(self, event=None):
        """Updates the label for the bet sizing slider."""
        self.bet_size_label.config(text=f"${self.bet_size_var.get():.2f}")

    def _submit_preset_bet(self, preset_type):
        """Submit a preset bet action using display state."""
        display_state = self.state_machine.get_display_state()
        preset_bets = display_state.valid_actions.get('preset_bets', {})
        
        if preset_type in preset_bets:
            amount = preset_bets[preset_type]
            # Set the bet size and then submit the action
            self.bet_size_var.set(amount)
            self._submit_human_action("bet_or_raise")
    
    def _submit_bet_raise(self):
        """Submits a bet or raise action - no context check needed."""
        # No context check: Just send action and amount
        amount = float(self.bet_size_var.get())
        self._submit_human_action("bet_or_raise", amount)
    def _animate_player_action(self, player_index: int, action: str, amount: float = 0):
        """Animate a player's action with visual feedback that persists until next player acts."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        frame = player_seat.get("frame")
        name_label = player_seat.get("name_label")
        
        if not frame or not name_label:
            return
            
        # Clear any existing action indicator for this player
        if player_index in self.action_indicators:
            old_label = self.action_indicators[player_index]
            if old_label and old_label.winfo_exists():
                old_label.destroy()
        
        # Clear the previous player's action indicator when a new action is taken
        if (self.last_action_player is not None and 
            self.last_action_player != player_index and
            self.last_action_player in self.action_indicators):
            # Clear the previous player's action indicator
            old_label = self.action_indicators[self.last_action_player]
            if old_label and old_label.winfo_exists():
                old_label.destroy()
                del self.action_indicators[self.last_action_player]
        
        # Create action indicator - FIXED: Unify CALL and BET graphics
        action_text = action.upper()
        if action.upper() == "CALL" and amount > 0:
            # FIXED: Show CALL as BET for visual consistency (both put money in front)
            action_text = f"BET ${amount:.2f}"
        elif amount > 0:
            action_text += f" ${amount:.2f}"
        elif action.upper() == "CHECK":
            action_text = "CHECK"  # Keep it simple for check
            
        # Create persistent action label (doesn't fade out)
        action_label = tk.Label(
            frame,
            text=action_text,
            bg=THEME["accent_secondary"],
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2
        )
        action_label.pack(side=tk.TOP, pady=2)
        
        # Force the label to be visible and properly configured
        action_label.lift()  # Bring to front
        action_label.update()  # Force update
        action_label.config(state="normal")  # Ensure it's enabled
        frame.update()  # Update the parent frame
        
        # Force a complete UI refresh
        self.canvas.update()
        self.update()
        
        # Store the action indicator for this player
        self.action_indicators[player_index] = action_label
        self.last_action_player = player_index
        
        # Action feedback is already handled by the action_label created above
        # and by the selective update system, so no additional display updates needed here
    
    # REMOVED: Individual chip animations - money stays in front of players until street completion
    # The _animate_chips_to_pot and _move_chip_to_pot_step methods have been removed
    # as they were causing money to move directly to pot instead of staying in front of players
    
    def _animate_all_bets_to_pot(self):
        """Animate all individual bet displays consolidating into the pot at street completion."""
        if not hasattr(self, 'player_seats') or not self.player_seats:
            self._log_message("⚠️ No player_seats available for bet consolidation")
            return
        
        self._log_message("🎰 Animating all bets consolidating into pot")
        self.add_game_message("🎰 Street complete - consolidating all bets to pot...")
        
        # Count how many players have bets to consolidate
        bet_count = 0
        for player_seat in self.player_seats:
            if player_seat:
                bet_label_widget = player_seat.get("bet_label_widget")
                if bet_label_widget:
                    bet_text = bet_label_widget.cget("text")
                    if bet_text and "$" in bet_text:
                        bet_count += 1
        
        self._log_message(f"🎰 Found {bet_count} players with bets to consolidate")
        self.add_game_message(f"🎰 Consolidating {bet_count} player bets to pot...")
        
        # Get pot position
        pot_x = self.pot_label.winfo_rootx() - self.canvas.winfo_rootx() + self.pot_label.winfo_width() // 2
        pot_y = self.pot_label.winfo_rooty() - self.canvas.winfo_rooty() + self.pot_label.winfo_height() // 2
        
        # Animate each player's bet display to the pot
        for player_index, player_seat in enumerate(self.player_seats):
            if not player_seat:
                continue
                
            bet_label_widget = player_seat.get("bet_label_widget")
            bet_label_window = player_seat.get("bet_label_window")
            
            if bet_label_widget and bet_label_window:
                # Check if this player has a bet displayed
                bet_text = bet_label_widget.cget("text")
                if bet_text and "$" in bet_text:
                    # Extract amount from bet text
                    try:
                        amount_str = bet_text.split("$")[1].split()[0]
                        amount = float(amount_str)
                        
                        # Get bet label position
                        bet_x = bet_label_widget.winfo_rootx() - self.canvas.winfo_rootx() + bet_label_widget.winfo_width() // 2
                        bet_y = bet_label_widget.winfo_rooty() - self.canvas.winfo_rooty() + bet_label_widget.winfo_height() // 2
                        
                        # Validate coordinates
                        if (bet_x >= 0 and bet_y >= 0 and 
                            pot_x >= 0 and pot_y >= 0 and
                            pot_x < self.canvas.winfo_width() and pot_y < self.canvas.winfo_height()):
                            
                            # Create chip animation from bet label to pot
                            self._animate_bet_label_to_pot(bet_label_window, bet_x, bet_y, pot_x, pot_y, amount, player_index)
                            
                    except (ValueError, IndexError):
                        self._log_message(f"⚠️ Could not parse bet amount from: {bet_text}")
        
        # Clear all bet displays after animation - faster clear to match showdown speed
        self.root.after(1000, self._clear_all_bet_displays)
    
    def _animate_bet_label_to_pot(self, bet_label_window, start_x, start_y, end_x, end_y, amount, player_index):
        """Animate a bet label moving to the pot."""
        # Create a chip representation
        chip_size = 25
        chip_color = "#FFD700"  # Gold color for chips
        chip_window = self.canvas.create_oval(
            start_x - chip_size//2, start_y - chip_size//2,
            start_x + chip_size//2, start_y + chip_size//2,
            fill=chip_color, outline="#B8860B", width=3
        )
        
        # Add amount text to chip
        amount_text = self.canvas.create_text(
            start_x, start_y,
            text=f"${amount:.1f}",
            fill="black",
            font=("Arial", 9, "bold")
        )
        
        # Hide the original bet label
        self.canvas.itemconfig(bet_label_window, state="hidden")
        
        # Start animation with fast staggered delay (same as showdown speed)
        delay = player_index * 100  # Faster stagger to match showdown timing
        self.root.after(delay, lambda: self._move_bet_to_pot_step(chip_window, amount_text, start_x, start_y, end_x, end_y))
    
    def _move_bet_to_pot_step(self, chip_window, amount_text, start_x, start_y, end_x, end_y, step=0):
        """Animate bet label movement to pot (fast like showdown animation)."""
        total_steps = 30  # FIXED: Fast animation same as showdown (was 50)
        
        if step >= total_steps:
            # Animation complete
            self.canvas.delete(chip_window)
            self.canvas.delete(amount_text)
            return
        
        # Calculate current position with simpler easing (same as showdown)
        progress = step / total_steps
        
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        
        # Move chip and text
        chip_size = 25
        self.canvas.coords(chip_window, 
                          current_x - chip_size//2, current_y - chip_size//2,
                          current_x + chip_size//2, current_y + chip_size//2)
        self.canvas.coords(amount_text, current_x, current_y)
        
        # FIXED: Fast timing same as showdown animation (was 60ms)
        self.root.after(15, lambda: self._move_bet_to_pot_step(chip_window, amount_text, start_x, start_y, end_x, end_y, step + 1))
    
    def _clear_all_bet_displays(self):
        """Clear all bet displays after consolidation animation."""
        if not hasattr(self, 'player_seats') or not self.player_seats:
            return
        
        for player_seat in self.player_seats:
            if not player_seat:
                continue
                
            bet_label_widget = player_seat.get("bet_label_widget")
            bet_label_window = player_seat.get("bet_label_window")
            
            if bet_label_widget and bet_label_window:
                bet_label_widget.config(text="")
                self.canvas.itemconfig(bet_label_window, state="hidden")
        
        self._log_message("✅ All bet displays cleared after consolidation")
    
    def _handle_round_complete(self):
        """Handle street completion by animating all bets consolidating into the pot."""
        self._log_message("🔄 Street complete - animating bet consolidation to pot")
        self.add_game_message("🔄 Street complete - consolidating bets to pot")
        
        # Animate all bet displays consolidating into the pot
        self._animate_all_bets_to_pot()
    
    def _handle_dealing_start(self):
        """Handle the start of card dealing animation."""
        self._log_message("🃏 Starting card dealing animation")
        self.add_game_message("🃏 House dealer is dealing hole cards...")
        
        # Show dealer indicator
        self._show_dealer_indicator()
        
        # CRITICAL: Clear all existing cards first to ensure no old cards show
        self._log_message("🃏 CLEARING ALL CARDS before dealing starts")
        self._clear_all_player_cards()
        self._log_message("🃏 ALL CARDS CLEARED - ready for dealing")
    
    def _handle_single_card_dealt(self, player_index: int, card_index: int, card: str):
        """Handle animation of a single card being dealt to a player."""
        player_name = f"Player {player_index + 1}"
        card_name = "first" if card_index == 0 else "second"
        self._log_message(f"🃏 House dealer dealing {card_name} card to {player_name}: {card}")
        
        # Calculate delay for proper casino-style dealing sequence
        # All first cards, then all second cards
        if card_index == 0:
            # First card round: delay based on player index
            delay = player_index * 300  # 300ms between each player's first card
        else:
            # Second card round: delay includes all first cards + this player's position
            first_round_time = len(self.state_machine.game_state.players) * 300
            delay = first_round_time + (player_index * 300)
        
        # Animate single card being dealt
        self.root.after(delay, lambda: self._animate_single_card_to_player(player_index, card_index, card))
        
        # Add progress message
        self.root.after(delay, lambda: self.add_game_message(f"🃏 {card_name.title()} card to {player_name}..."))
    
    def _handle_dealing_complete(self, total_dealing_time: int):
        """Handle completion of dealing animation and start betting."""
        self._log_message(f"🃏 Dealing will complete in {total_dealing_time}ms")
        self.add_game_message("🃏 Dealing cards... please wait...")
        
        # Wait for all dealing animations to complete, then start betting
        self.root.after(total_dealing_time, self._start_betting_after_dealing)
    
    def _start_betting_after_dealing(self):
        """Start the betting round after all dealing animations are complete."""
        self._log_message("🃏 All cards dealt - starting betting round")
        self.add_game_message("🃏 All cards dealt! Betting begins...")
        
        # Reveal human player's cards now that dealing is complete
        self._reveal_human_cards()
        
        # Tell state machine to start preflop betting
        if hasattr(self.state_machine, 'start_preflop_betting_after_dealing'):
            self.state_machine.start_preflop_betting_after_dealing()
    
    def _reveal_human_cards(self):
        """Reveal the human player's cards after dealing animation completes."""
        human_player_index = 0  # Human is always player 0
        
        if human_player_index < len(self.player_seats) and self.player_seats[human_player_index]:
            player_seat = self.player_seats[human_player_index]
            card_widgets = player_seat.get("card_widgets", [])
            
            for i, card_widget in enumerate(card_widgets):
                if hasattr(card_widget, '_current_card') and card_widget._current_card:
                    # Reveal the stored card
                    card_widget.set_card(card_widget._current_card)
                    self._log_message(f"🃏 Revealed human card {i}: {card_widget._current_card}")
            
            self.add_game_message("🃏 Your hole cards revealed!")
    
    def _clear_all_player_cards(self):
        """Clear all player cards at the start of dealing."""
        for player_seat in self.player_seats:
            if player_seat:
                card_widgets = player_seat.get("card_widgets", [])
                for widget in card_widgets:
                    widget.set_card("")  # Clear card
                    widget._current_card = None  # Clear stored card data
        self._log_message("🃏 Cleared all player cards for new dealing")
    
    def _show_dealer_indicator(self):
        """Show a visual indicator for the house dealer."""
        # Create dealer position (center of table)
        dealer_x = self.canvas.winfo_width() // 2
        dealer_y = self.canvas.winfo_height() // 2
        
        # Create dealer circle indicator
        dealer_size = 30
        self.dealer_indicator = self.canvas.create_oval(
            dealer_x - dealer_size, dealer_y - dealer_size,
            dealer_x + dealer_size, dealer_y + dealer_size,
            fill="#4CAF50", outline="#2E7D32", width=3
        )
        
        # Add "DEALER" text
        self.dealer_text = self.canvas.create_text(
            dealer_x, dealer_y,
            text="DEALER",
            fill="white",
            font=("Arial", 8, "bold")
        )
        
        # Hide dealer indicator after dealing is complete
        self.root.after(5000, self._hide_dealer_indicator)  # Hide after 5 seconds
    
    def _hide_dealer_indicator(self):
        """Hide the dealer indicator."""
        if hasattr(self, 'dealer_indicator'):
            self.canvas.delete(self.dealer_indicator)
        if hasattr(self, 'dealer_text'):
            self.canvas.delete(self.dealer_text)
    
    def _animate_single_card_to_player(self, player_index: int, card_index: int, card: str):
        """Animate a single card being dealt to a specific player."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        card_widgets = player_seat.get("card_widgets", [])
        
        if card_index < len(card_widgets):
            # Create dealer position (center of table - neutral house dealer)
            dealer_x = self.canvas.winfo_width() // 2
            dealer_y = self.canvas.winfo_height() // 2  # Center of table, not top
            
            # Get player position
            player_pod = player_seat.get("player_pod")
            if player_pod:
                player_x = player_pod.winfo_x() + player_pod.winfo_width() // 2
                player_y = player_pod.winfo_y() + player_pod.winfo_height() // 2
                
                # Animate the specific card
                self._animate_single_card_deal(dealer_x, dealer_y, player_x, player_y, card, 
                                               lambda: self._set_player_card(player_index, card_index, card))
    
    def _animate_single_card_deal(self, start_x, start_y, end_x, end_y, card, callback):
        """Animate a single card being dealt from dealer to player."""
        # Create card animation with proper card back design
        card_width, card_height = 40, 60
        
        # Create main card background (classic red card back)
        card_rect = self.canvas.create_rectangle(
            start_x - card_width//2, start_y - card_height//2,
            start_x + card_width//2, start_y + card_height//2,
            fill="#8B0000", outline="#000000", width=2
        )
        
        # Add realistic card back pattern
        pattern_items = []
        
        # Create decorative border
        pattern_items.append(self.canvas.create_rectangle(
            start_x - card_width//2 + 3, start_y - card_height//2 + 3,
            start_x + card_width//2 - 3, start_y + card_height//2 - 3,
            fill="", outline="#FFD700", width=1
        ))
        
        # Central diamond pattern
        diamond_size = 8
        pattern_items.append(self.canvas.create_polygon(
            start_x, start_y - diamond_size,  # Top
            start_x + diamond_size, start_y,  # Right
            start_x, start_y + diamond_size,  # Bottom
            start_x - diamond_size, start_y,  # Left
            fill="#FFD700", outline="#FFD700"
        ))
        
        # Corner decorations (small diamonds)
        for dx, dy in [(-card_width//3, -card_height//3), (card_width//3, -card_height//3),
                       (-card_width//3, card_height//3), (card_width//3, card_height//3)]:
            pattern_items.append(self.canvas.create_oval(
                start_x + dx - 2, start_y + dy - 2,
                start_x + dx + 2, start_y + dy + 2,
                fill="#FFD700", outline="#FFD700"
            ))
        
        # Add "POKER" text in center
        pattern_items.append(self.canvas.create_text(
            start_x, start_y + 8,
            text="♠♥♣♦",
            fill="#FFD700",
            font=("Arial", 8, "bold")
        ))
        
        # Animate movement
        self._move_card_step(card_rect, pattern_items, start_x, start_y, end_x, end_y, callback)
    
    def _move_card_step(self, card_rect, pattern_items, start_x, start_y, end_x, end_y, callback, step=0):
        """Animate card movement step by step."""
        total_steps = 20
        
        if step >= total_steps:
            # Animation complete - delete all card elements
            self.canvas.delete(card_rect)
            for item in pattern_items:
                self.canvas.delete(item)
            callback()  # Set the actual card
            return
        
        # Calculate current position
        progress = step / total_steps
        ease_progress = 1 - (1 - progress) ** 2  # Ease-out animation
        
        current_x = start_x + (end_x - start_x) * ease_progress
        current_y = start_y + (end_y - start_y) * ease_progress
        
        # Move card background
        card_width, card_height = 40, 60
        self.canvas.coords(card_rect,
                          current_x - card_width//2, current_y - card_height//2,
                          current_x + card_width//2, current_y + card_height//2)
        
        # Move pattern elements
        if len(pattern_items) >= 1:
            # Decorative border
            self.canvas.coords(pattern_items[0],
                              current_x - card_width//2 + 3, current_y - card_height//2 + 3,
                              current_x + card_width//2 - 3, current_y + card_height//2 - 3)
            
            # Central diamond
            if len(pattern_items) >= 2:
                diamond_size = 8
                self.canvas.coords(pattern_items[1],
                                  current_x, current_y - diamond_size,  # Top
                                  current_x + diamond_size, current_y,  # Right
                                  current_x, current_y + diamond_size,  # Bottom
                                  current_x - diamond_size, current_y)  # Left
            
            # Corner decorations
            for i, (dx, dy) in enumerate([(-card_width//3, -card_height//3), (card_width//3, -card_height//3),
                                        (-card_width//3, card_height//3), (card_width//3, card_height//3)]):
                if i + 2 < len(pattern_items):
                    self.canvas.coords(pattern_items[i + 2],
                                      current_x + dx - 2, current_y + dy - 2,
                                      current_x + dx + 2, current_y + dy + 2)
            
            # Poker symbols text
            if len(pattern_items) >= 7:  # border + diamond + 4 corners + text
                self.canvas.coords(pattern_items[6], current_x, current_y + 8)
        
        # Continue animation
        self.root.after(30, lambda: self._move_card_step(card_rect, pattern_items, start_x, start_y, end_x, end_y, callback, step + 1))
    
    def _set_player_card(self, player_index: int, card_index: int, card: str):
        """Set a specific card for a player after animation."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        card_widgets = player_seat.get("card_widgets", [])
        
        if card_index < len(card_widgets):
            # FIXED: Don't show any cards during dealing animation - store them only
            # All players (including human) show card backs during dealing
            card_widgets[card_index].set_card("")  # Show card back during dealing
            card_widgets[card_index]._current_card = card  # Store actual card for later
            # DEBUG: Extra logging for human player
            if player_index == 0:
                self._log_message(f"🐛 DEAL DEBUG - Player 0 card {card_index}: stored {card}")
            self._log_message(f"🃏 Stored card {card_index} for Player {player_index}: {card} (showing back during dealing)")
    
    def _format_card(self, card_str: str) -> str:
        """Formats a card string for display with proper colors."""
        if not card_str or card_str == "**":
            return "🂠"
        
        rank = card_str[0]
        suit = card_str[1]
        
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_symbol = suit_symbols.get(suit, suit)
        
        # Return formatted card with color indicators
        return f"{rank}{suit_symbol}"
    
    def _get_card_color(self, card_str: str) -> str:
        """Get the appropriate color for a card (red for hearts/diamonds, black for spades/clubs)."""
        if not card_str or card_str == "**":
            return "#CCCCCC"  # Gray for unknown cards
        
        suit = card_str[1]
        if suit in ['h', 'd']:  # Hearts and Diamonds
            return "#FF0000"  # Red
        else:  # Spades and Clubs
            return "#000000"  # Black

    def update_font_size(self, font_size: int):
        """Updates the font size for all components in the practice session."""
        # Create font configurations for different component types
        main_font = (THEME["font_family"], font_size)
        small_font = (THEME["font_family"], max(font_size - 2, 8))  # Ensure minimum size
        large_font = (THEME["font_family"], font_size + 2)
        bold_font = (THEME["font_family"], font_size, "bold")
        
        # Update session information text area
        if hasattr(self, 'session_text'):
            self.session_text.config(font=main_font)
        
        # Update action messages text area
        if hasattr(self, 'info_text'):
            self.info_text.config(font=main_font)
            # Update existing tags with new font size
            bold_font = (THEME["font_family"], font_size, "bold")
            self.info_text.tag_config("action_highlight", font=bold_font)
            self.info_text.tag_config("community_highlight", font=bold_font)
            self.info_text.tag_config("showdown_highlight", font=bold_font)
            self.info_text.tag_config("transition_highlight", font=bold_font)
        
        # Update scrollbars to match the new font size
        if hasattr(self, 'session_scrollbar'):
            # Scrollbar size can be adjusted if needed
            pass
        if hasattr(self, 'action_scrollbar'):
            # Scrollbar size can be adjusted if needed
            pass
        
        # Update player seat labels and information
        for player_seat in self.player_seats:
            if player_seat:
                frame = player_seat.get("frame")
                if frame:
                    # Update player name label
                    name_label = player_seat.get("name_label")
                    if name_label:
                        name_label.config(font=bold_font)
                    
                    # Update position label
                    position_label = player_seat.get("position_label")
                    if position_label:
                        position_label.config(font=small_font)
                    
                    # Update cards label
                    cards_label = player_seat.get("cards_label")
                    if cards_label:
                        cards_label.config(font=main_font)
                    
                    # Update bet label
                    bet_label = player_seat.get("bet_label")
                    if bet_label:
                        bet_label.config(font=main_font)
                
                # Update stack graphics
                stack_graphics = player_seat.get("stack_graphics")
                if stack_graphics:
                    amount_label = stack_graphics.get("amount_label")
                    if amount_label:
                        amount_label.config(font=main_font)
                    
                    chips_label = stack_graphics.get("chips_label")
                    if chips_label:
                        chips_label.config(font=small_font)
        
        # Update community card labels
        for card_widget in self.community_card_widgets:
            if card_widget and hasattr(card_widget, 'configure'):
                # CardWidget doesn't need font updates as it handles its own styling
                pass
        
        # Update pot display
        if hasattr(self, 'pot_label') and self.pot_label is not None:
            self.pot_label.config(font=large_font)
        if hasattr(self, 'pot_chips_label') and self.pot_chips_label is not None:
            self.pot_chips_label.config(font=small_font)
        
        # Update action buttons
        for control_name, control_dict in self.human_action_controls.items():
            if isinstance(control_dict, dict):
                button = control_dict.get("button")
                if button:
                    button.config(font=main_font)
        
        # Update bet size entry and label
        if hasattr(self, 'bet_size_entry') and self.bet_size_entry is not None:
            self.bet_size_entry.config(font=main_font)
        if hasattr(self, 'bet_size_label') and self.bet_size_label is not None:
            self.bet_size_label.config(font=main_font)
        
        # Update game control buttons
        if hasattr(self, 'start_hand_btn') and self.start_hand_btn is not None:
            self.start_hand_btn.config(font=main_font)
        if hasattr(self, 'reset_game_btn') and self.reset_game_btn is not None:
            self.reset_game_btn.config(font=main_font)
        
        # Force a complete UI refresh
        self.update()
    
    def increase_table_size(self):
        """Increase the table size by adjusting column weights."""
        # Get current weights
        current_table_weight = self.grid_columnconfigure(0)['weight']
        current_message_weight = self.grid_columnconfigure(1)['weight']
        
        # Increase table weight (make it larger)
        new_table_weight = min(current_table_weight + 1, 8)  # Cap at 8
        new_message_weight = max(current_message_weight - 0.5, 0.5)  # Don't go below 0.5
        
        # Update column weights
        self.grid_columnconfigure(0, weight=new_table_weight)
        self.grid_columnconfigure(1, weight=new_message_weight)
        
        # Force a complete redraw
        self._on_resize()
        
        # Update session info to reflect the change
        self.update_session_info()
    
    def decrease_table_size(self):
        """Decrease the table size by adjusting column weights."""
        # Get current weights
        current_table_weight = self.grid_columnconfigure(0)['weight']
        current_message_weight = self.grid_columnconfigure(1)['weight']
        
        # Decrease table weight (make it smaller)
        new_table_weight = max(current_table_weight - 1, 3)  # Don't go below 3
        new_message_weight = min(current_message_weight + 0.5, 2)  # Cap at 2
        
        # Update column weights
        self.grid_columnconfigure(0, weight=new_table_weight)
        self.grid_columnconfigure(1, weight=new_message_weight)
        
        # Force a complete redraw
        self._on_resize()
        
        # Update session info to reflect the change
        self.update_session_info()
    
    def get_table_size_info(self):
        """Get current table size information for display."""
        table_weight = self.grid_columnconfigure(0)['weight']
        message_weight = self.grid_columnconfigure(1)['weight']
        
        # Calculate relative sizes
        total_weight = table_weight + message_weight
        table_percentage = (table_weight / total_weight) * 100
        message_percentage = (message_weight / total_weight) * 100
        
        return {
            'table_weight': table_weight,
            'message_weight': message_weight,
            'table_percentage': table_percentage,
            'message_percentage': message_percentage
        }
    
    def change_table_felt(self, felt_color):
        """Change the table felt color and redraw immediately."""
        if felt_color in self.table_felt_colors:
            self.current_felt_color = felt_color
            # Force a complete redraw to apply the new felt color
            self._on_resize()
            # Update session info to reflect the change
            self.update_session_info()
    def update_stack_amount(self, player_index, new_amount):
        """Update the stack amount for a player."""
        if player_index < len(self.player_seats) and self.player_seats[player_index]:
            player_seat = self.player_seats[player_index]
            player_pod = player_seat.get("player_pod")
            if player_pod:
                # Get chip representation from display state
                display_state = self.state_machine.get_display_state()
                chip_symbols = display_state.chip_representations.get(f'player{player_index}_stack', '')
                
                # Update the stack display
                pod_data = {
                    "name": player_pod.name_label.cget("text"),
                    "stack": new_amount,
                    "bet": 0,  # Reset bet when updating stack
                    "starting_stack": 100.0
                }
                player_pod.update_pod(pod_data)

    def update_pot_amount(self, new_amount):
        """Update the pot amount display."""
        # Safety check: Don't update if pot_label isn't ready yet
        if not hasattr(self, 'pot_label') or self.pot_label is None:
            return
            
        # Get chip representation from display state
        display_state = self.state_machine.get_display_state()
        if display_state:
            chip_symbols = display_state.chip_representations.get('pot', '')
            self.pot_label.config(text=f"Pot: ${new_amount:.2f} {chip_symbols}")
        else:
            self.pot_label.config(text=f"Pot: ${new_amount:.2f}")
    
    def _on_state_change(self, new_state):
        """Handle state changes from the state machine."""
        self.update_display(new_state)

    def _update_player_position(self, player_index, position, highlight):
        """Update player position and highlighting using display state data."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
            
        player_seat = self.player_seats[player_index]
        player_pod = player_seat.get("player_pod")
        frame = player_seat.get("frame")
        
        if player_pod:
            # Update player pod with new data
            game_info = self.state_machine.get_game_info()
            if game_info and player_index < len(game_info['players']):
                player_info = game_info['players'][player_index]
                pod_data = {
                    "name": f"{player_info['name']} ({player_info['position']})",
                    "stack": player_info['stack'],
                    "bet": player_info.get('current_bet', 0),
                    "starting_stack": 100.0
                }
                player_pod.update_pod(pod_data)
                
                # Set active player highlighting
                player_pod.set_active_player(highlight)
                
                # Update card visibility using display state
                display_state = self.state_machine.get_display_state()
                if display_state and player_index < len(display_state.card_visibilities):
                    card_visible = display_state.card_visibilities[player_index]
                    card_widgets = player_seat.get("card_widgets", [])
                    
                    if len(card_widgets) >= 2 and len(player_info['cards']) >= 2:
                        # Check if player has folded (is not active)
                        player_has_folded = not player_info.get('is_active', True)
                        
                        # FIXED: Only set cards if they haven't been set yet or are different
                        # This prevents cards from changing during showdown
                        current_card1 = getattr(card_widgets[0], '_current_card', None)
                        current_card2 = getattr(card_widgets[1], '_current_card', None)
                        new_card1 = player_info['cards'][0] if len(player_info['cards']) > 0 else ""
                        new_card2 = player_info['cards'][1] if len(player_info['cards']) > 1 else ""
                        
                        # DEBUG: Log card changes to track the persistence bug
                        if player_index == 0:  # Human player
                            self._log_message(f"🐛 CARD DEBUG - Player {player_index}: current=({current_card1}, {current_card2}) new=({new_card1}, {new_card2})")
                        
                        if card_visible:
                            # Show actual cards for human players or during showdown
                            # Only update if cards have actually changed
                            if current_card1 != new_card1:
                                card_widgets[0].set_card(new_card1)
                                card_widgets[0]._current_card = new_card1
                            if current_card2 != new_card2:
                                card_widgets[1].set_card(new_card2)
                                card_widgets[1]._current_card = new_card2
                            self._log_message(f"🎴 Showing cards for {player_info['name']}: {player_info['cards']}")
                        else:
                            # Show card backs for hidden cards
                            if player_has_folded:
                                # Show folded (gray) card backs
                                card_widgets[0].set_folded()
                                card_widgets[1].set_folded()
                                self._log_message(f"🎴 Showing folded cards for {player_info['name']}")
                            else:
                                # Show normal card backs - but preserve the actual card data
                                card_widgets[0].set_card("")  # This will show card back
                                card_widgets[1].set_card("")  # This will show card back
                                # Store the actual cards for later reveal
                                card_widgets[0]._current_card = new_card1
                                card_widgets[1]._current_card = new_card2
                                self._log_message(f"🎴 Hiding cards for {player_info['name']}")
        
        # Update frame highlighting
        if frame:
            if highlight:
                frame.config(bg=THEME["accent_primary"])
            else:
                frame.config(bg=THEME["secondary_bg"])
    
    def _update_action_controls(self, valid_actions):
        """Update action controls using display state data."""
        # This method will be implemented to update action buttons
        # based on the valid_actions from display state
        pass

    def _draw_community_cards(self, board_cards):
        """Draw community cards using display state data."""
        if not board_cards:
            return
            
        # Safety check for community card widgets
        if hasattr(self, 'community_card_widgets') and self.community_card_widgets:
            for i, card_widget in enumerate(self.community_card_widgets):
                if i < len(board_cards):
                    card_widget.set_card(board_cards[i])
                    # Force the card widget to update immediately
                    card_widget.update()
                    self._log_message(f"   Set card {i}: {board_cards[i]}")
        
        # Update tracking variable
        if hasattr(self, 'last_board_cards'):
            if board_cards != self.last_board_cards:
                self._log_message(f"🎴 Board changed: {self.last_board_cards} → {board_cards}")
                self.last_board_cards = board_cards.copy()
        else:
            self.last_board_cards = board_cards.copy()

