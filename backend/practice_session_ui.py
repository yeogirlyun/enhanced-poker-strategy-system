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

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType, PokerState
from sound_manager import SoundManager
from gui_models import THEME, FONTS
from tooltips import ToolTip

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
        self.delete("all") # Clear previous drawing
        if not card_str or card_str == "**" or is_folded:
    
            self._draw_card_back(is_folded=is_folded)
            # Force update to ensure the drawing is applied
            self.update()
            return

        self.config(bg="white")
        rank, suit = card_str[0], card_str[1]
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_colors = {'h': '#c0392b', 'd': '#c0392b', 'c': 'black', 's': 'black'}
        color = suit_colors.get(suit, "black")
        
        # Use larger, clearer fonts
        self.create_text(self.width / 2, self.height / 2 - 5, text=rank, font=("Helvetica", 22, "bold"), fill=color)
        self.create_text(self.width / 2, self.height / 2 + 18, text=suit_symbols.get(suit, ""), font=("Helvetica", 16), fill=color)
        # Force update to ensure the drawing is applied
        self.update()

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
            
            # Debug: Print to confirm folded card back is being drawn
    
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
            
            # Debug: Print to confirm card back is being drawn
    

    def set_folded(self):
        """Shows the card as folded (empty)."""
        self.set_card("", is_folded=True)

class PlayerPod(tk.Frame):
    """A custom widget for a player's area, including a graphical stack display."""
    def __init__(self, parent):
        # The main pod frame is transparent to sit nicely on the canvas
        super().__init__(parent, bg="#1a1a1a") # Match your table's background
        
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

        # --- NEW: Professional Stack Display ---
        # This frame sits below the main info_frame
        self.stack_frame = tk.Frame(self, bg="#1a1a1a")
        self.stack_frame.pack()
        
        # Canvas for drawing chip graphics - make it larger for better visibility
        self.chip_canvas = tk.Canvas(self.stack_frame, width=40, height=35, bg="#1a1a1a", highlightthickness=0)
        self.chip_canvas.pack(side="left", padx=5)
        
        # Ensure the canvas is properly configured
        self.chip_canvas.config(width=40, height=35)
        
        # Label for the stack text
        self.stack_label = tk.Label(self.stack_frame, text="", font=("Helvetica", 12, "bold"), bg="#1a1a1a", fg="white")
        self.stack_label.pack(side="left")

    def update_pod(self, data):
        # Update name, cards, highlighting as before
        self.name_label.config(text=data.get("name", ""))
        stack_amount = data.get('stack', 0)
        self.stack_label.config(text=f"${stack_amount:.2f}")

        self._draw_chips(stack_amount) # Call the new chip drawing method

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
        chip_width = 12
        chip_height = 14
        start_x = 8
        
        for i in range(num_chips):
            # Draw chips in a straight vertical tower
            y_offset = 32 - i * 2  # Vertical spacing for straight tower
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
        self.sfx = SoundManager()
        
        # Initialize state machine
        self.state_machine = ImprovedPokerStateMachine(
            num_players=6,
            strategy_data=strategy_data,
            root_tk=parent
        )
        
        # Set up callbacks after initialization
        self.state_machine.on_action_required = self.prompt_human_action
        self.state_machine.on_state_change = self._on_state_change
        self.state_machine.on_hand_complete = self.handle_hand_complete
        self.state_machine.on_action_player_changed = self.update_display
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
        
        # Force initial display update to show highlighting
        self.update_display()
    
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
            """Calculate bet label positions."""
            center_x, center_y = width / 2, height / 2
            
            # Bet labels positioned closer to table center than player seats
            bet_radius_x = width * 0.32
            bet_radius_y = height * 0.25
            
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

        action_map = { "fold": ActionType.FOLD, "check": ActionType.CHECK, "call": ActionType.CALL, "bet": ActionType.BET, "raise": ActionType.RAISE }
        action = action_map.get(action_str)
        
        # FIX: Only get an amount for a bet or raise.
        amount = 0
        if action in [ActionType.BET, ActionType.RAISE]:
            amount = self.bet_size_var.get()

        # Play industry-standard sound for the action
        self.sfx.play_action_sound(action_str, amount)

        # Hide the controls immediately. The state machine will show them again when it's our turn.
        self._show_game_control_buttons()
        
        # Let the state machine handle EVERYTHING from here.
        self.state_machine.execute_action(player, action, amount)

    def prompt_human_action(self, player):
        """Shows and configures the action controls for the human player."""

        
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        self._show_action_buttons()
        
        # --- FIXED: Use state machine's valid actions instead of duplicating logic ---
        valid_actions = self.state_machine.get_valid_actions_for_player(player)

        
        # Configure fold button based on state machine's validation
        if valid_actions.get('fold', False):
            self.human_action_controls['fold'].config(state='normal')
            self.human_action_controls['fold'].config(text="Fold")
        # Get call amount from state machine
        call_amount = valid_actions.get('call_amount', 0)

        # --- End of proper separation of concerns ---
        
        self.human_action_controls['fold'].pack(side=tk.LEFT, padx=5)
        if call_amount > 0:
            self.human_action_controls['check'].pack_forget()
            self.human_action_controls['call'].config(text=f"Call ${call_amount:.2f}")
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=5)
            self.human_action_controls['bet_raise'].config(text="Raise To")
        self.human_action_controls['bet_raise'].pack(side=tk.RIGHT, padx=5)

        # Use state machine's values for bet/raise slider
        min_bet_or_raise = valid_actions.get('min_raise', self.state_machine.game_state.min_raise)
        max_bet = valid_actions.get('max_bet', player.stack + player.current_bet)
        
        self.bet_slider.config(from_=min_bet_or_raise, to=max_bet)
        self.bet_size_var.set(min_bet_or_raise)
        self._update_bet_size_label()
        


    def start_new_hand(self):
        """Starts a new hand and resets the UI accordingly."""

        
        # Clear preserved community cards and pot amount when starting new hand
        self.preserved_community_cards = []
        self.preserved_pot_amount = 0.0
        self.hand_completed = False
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
        
        self.state_machine.start_hand()

    def handle_hand_complete(self, winner_info=None):
        """
        Handles hand completion by displaying the winner info received from the state machine.
        """

        
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

            # Create a more descriptive announcement with proper formatting
            if pot_amount > 0:
                announcement = f"🏆 {winner_names} wins ${pot_amount:.2f}!"
                if winning_hand and winning_hand != "Unknown":
                    announcement += f" ({winning_hand})"
                
                # Update pot label with winner info
                self.pot_label.config(text=f"Winner: {winner_names}!", fg=THEME["accent_secondary"])
                self.pot_label.update()  # Force pot label update
                self.add_game_message(announcement)
                
                # Start pot animation to winner
                self._animate_pot_to_winner(winner_info)
        # Set the winning announcement message that will persist until next hand
        if hasattr(self, 'last_action_label'):
            winner_name = winner_info.get('name', 'Unknown')
            amount = winner_info.get('amount', 0)
            hand_type = winner_info.get('hand', 'unknown')
            announcement = f"🏆 {winner_name} wins ${amount:.2f}! ({hand_type})"
            self.last_action_label.config(text=announcement)

        
        # Mark hand as completed to preserve the announcement
        self.hand_completed = True

        # Show game controls after a delay
        self.after(3000, self._show_game_control_buttons)

    def _animate_pot_to_winner(self, winner_info):
        """Animate pot money moving to the winner's stack."""

        
        # Handle multiple winners (comma-separated names)
        winner_names = winner_info['name'].split(', ')

        
        # Find the first winner's seat (or any winner if multiple)
        winner_seat = None
        for winner_name in winner_names:
            for i, seat in enumerate(self.player_seats):
                if seat and seat.get("name_label"):
                    player_name = seat["name_label"].cget("text").split('\n')[0]
                    if player_name == winner_name:
                        winner_seat = i
    
                        break
            if winner_seat is not None:
                break
        
        # FIX: If we can't find the winner seat, use seat 0 as fallback
        if winner_seat is None:
    
            winner_seat = 0
        
        if winner_seat is not None:
            
            # Get pot center position
            pot_x = self.canvas.winfo_width() / 2
            pot_y = self.canvas.winfo_height() / 2 + 130  # Pot label position
            
            # Get winner's stack graphics position
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
            center_x, center_y = width / 2, height / 2
            
            # Calculate stack graphics position (same as in _create_stack_graphics)
            stack_radius_x = width * 0.35
            stack_radius_y = height * 0.28
            angle = (2 * math.pi / self.num_players) * winner_seat - (math.pi / 2)
            winner_x = center_x + stack_radius_x * math.cos(angle)
            winner_y = center_y + stack_radius_y * math.sin(angle)

            
            # Create enhanced animated money object with chip visualization
            chip_count = self._calculate_chip_count(winner_info['amount'])
            chip_symbols = self._get_chip_symbols(winner_info['amount'])
            money_text = f"${winner_info['amount']:.2f}\n{chip_symbols}"
            
            money_obj = self.canvas.create_text(
                pot_x, pot_y, 
                text=money_text, 
                fill="#FFD700",  # Bright gold
                font=("Arial", 16, "bold"),
                tags="money_animation",
                justify=tk.CENTER
            )
            
            # Add glow effect with chip visualization
            glow_obj = self.canvas.create_text(
                pot_x, pot_y, 
                text=money_text, 
                fill="#FFA500",  # Orange glow
                font=("Arial", 18, "bold"),
                tags="money_animation_glow",
                justify=tk.CENTER
            )
            

            
            # Enhanced animation with multiple effects
            def animate_money(step=0):
                if step <= 30:  # 30 steps for smoother animation
                    progress = step / 30
                    # Enhanced easing function
                    ease = 1 - (1 - progress) ** 2
                    
                    current_x = pot_x + (winner_x - pot_x) * ease
                    current_y = pot_y + (winner_y - pot_y) * ease
                    
                    # Update both objects
                    self.canvas.coords(money_obj, current_x, current_y)
                    self.canvas.coords(glow_obj, current_x, current_y)
                    
                    # Scale effect - money gets bigger as it moves
                    scale = 1.0 + (progress * 0.5)
                    font_size = int(16 * scale)
                    glow_font_size = int(18 * scale)
                    
                    self.canvas.itemconfig(money_obj, font=("Arial", font_size, "bold"))
                    self.canvas.itemconfig(glow_obj, font=("Arial", glow_font_size, "bold"))
                    
                    # Color transition effect
                    if progress > 0.5:
                        # Transition from gold to green (success color)
                        green_intensity = int(255 * (progress - 0.5) * 2)
                        color = f"#00{green_intensity:02x}00"  # Green with increasing intensity
                        self.canvas.itemconfig(money_obj, fill=color)
                    
                    # Fade out glow as it approaches
                    if progress > 0.7:
                        alpha = int(255 * (1 - (progress - 0.7) / 0.3))
                        glow_color = f"#{alpha:02x}ff{alpha:02x}"
                        self.canvas.itemconfig(glow_obj, fill=glow_color)
                    
                    self.canvas.after(40, lambda: animate_money(step + 1))  # Faster animation
                    
                    # Update the winner's stack graphics with the new amount
                    if winner_seat < len(self.player_seats):
                        player_seat = self.player_seats[winner_seat]
                        if player_seat and "stack_graphics" in player_seat:
                            stack_graphics = player_seat["stack_graphics"]
                            amount_label = stack_graphics.get("amount_label")
                            chips_label = stack_graphics.get("chips_label")
                            
                            if amount_label and chips_label:
                                # Get current amount and add the pot amount
                                current_text = amount_label.cget("text")
                                try:
                                    current_amount = float(current_text.replace("$", ""))
                                    new_amount = current_amount + winner_info['amount']
                                    
                                    # Update stack graphics
                                    amount_label.config(text=f"${new_amount:.2f}")
                                    chip_symbols = self._get_chip_symbols(new_amount)
                                    chips_label.config(text=chip_symbols)
                                except ValueError:
                                    pass  # Handle invalid number format
                                    
                    # Update the display
                    self.update_display()
            
            # Start the animation
            animate_money()
    def add_game_message(self, message):
        """Add a message to the action messages area."""
        if hasattr(self, 'info_text'):
            # Filter to show only important action messages
            important_keywords = [
                'attempting', 'FOLDS', 'CALLS', 'RAISES', 'BETS', 'CHECKS',
                'wins', 'STATE TRANSITION', 'ROUND COMPLETE', 'SHOWDOWN',
                'Player', 'raises to', 'calls', 'folds', 'bets'
            ]
            
            # Check if message contains any important keywords
            is_important = any(keyword.lower() in message.lower() for keyword in important_keywords)
            
            if is_important:
                self.info_text.config(state=tk.NORMAL)
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
        """Creates a modern, dynamic action bar for the human player."""
        parent_frame.grid_columnconfigure(0, weight=1)
        self.action_bar_frame = ttk.Frame(parent_frame)  # Store reference
        self.action_bar_frame.grid(row=0, column=0, pady=5)

        # --- NEW: Game Control Buttons (Left Side) ---
        control_frame = ttk.Frame(self.action_bar_frame)
        control_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create larger buttons (150% size increase)
        button_style = ttk.Style()
        button_style.configure('Large.TButton', padding=(18, 10))  # Increased from (15, 8) to (18, 10) - 20% larger
        
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
        # --- END NEW ---

        # --- Last Action Label (Center) ---
        self.last_action_label = tk.Label(
            self.action_bar_frame, 
            text="", 
            font=("Helvetica", 14, "italic"),  # Increased from 12 to 14 - 20% larger
            fg=THEME["text"],
            bg=THEME["secondary_bg"]
        )
        self.last_action_label.pack(side=tk.LEFT, padx=10)
        
        # --- Action Buttons (Center) ---
        action_frame = ttk.Frame(self.action_bar_frame)
        action_frame.pack(side=tk.LEFT, padx=10)
        
        # Configure large button style for action buttons (20% larger)
        button_style.configure('LargeAction.TButton', padding=(14, 7))  # Increased from (12, 6) to (14, 7)
        
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

        # --- Bet Sizing Slider (Center-Right) ---
        self.sizing_frame = ttk.Frame(self.action_bar_frame)
        self.sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.bet_size_var = tk.DoubleVar()
        # Configure larger slider and label
        self.bet_slider = ttk.Scale(
            self.sizing_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.bet_size_var, 
            length=360  # Increased from 300 to 360 (20% larger)
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

        # --- Bet/Raise Button (Right) ---
        # --- Preset Bet Buttons (Right) ---
        preset_frame = ttk.Frame(self.action_bar_frame)
        preset_frame.pack(side=tk.RIGHT, padx=10)
        
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
        
        # --- Bet/Raise Button (Right) ---
        self.human_action_controls['bet_raise'] = ttk.Button(
            self.action_bar_frame, 
            text="Bet", 
            style="LargeAction.TButton", 
            command=self._submit_bet_raise
        )
        self.human_action_controls['bet_raise'].pack(side=tk.RIGHT, padx=5)
        ToolTip(self.human_action_controls['bet_raise'], "Make a bet or raise")

        # Initially show only game control buttons
        self._show_game_control_buttons()

    def _show_game_control_buttons(self):
        """Shows only the game control buttons (Start/Reset)."""

        
        # Hide all action buttons
        for widget in self.human_action_controls.values():
            if hasattr(widget, 'pack_forget'):
                widget.pack_forget()

        
        # Show game control buttons
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        
        # Hide bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.pack_forget()
        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.pack_forget()
        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack_forget()


    def _show_action_buttons(self):
        """Shows the action buttons and hides game control buttons."""

        
        # Hide game control buttons
        self.start_button.pack_forget()
        self.reset_button.pack_forget()

        
        # Show bet sizing controls
        if hasattr(self, 'bet_slider'):
            self.bet_slider.pack(fill=tk.X)

        if hasattr(self, 'bet_size_label'):
            self.bet_size_label.pack()

        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)


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
                self.state_machine.on_action_player_changed = self.update_display
                
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
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
        
        # Clear session info
        if hasattr(self, 'session_text'):
            self.session_text.config(state=tk.NORMAL)
            self.session_text.delete(1.0, tk.END)
            self.session_text.config(state=tk.DISABLED)
        
        # Reset pot display
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text="Pot: $0.00", fg="yellow")
        
        # Clear community cards display when starting new hand
        for card_widget in self.community_card_widgets:
            card_widget.set_card("")  # Clear the card
        
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
        
        # Reset player displays
        for player_seat in self.player_seats:
            if player_seat:
                frame = player_seat.get("frame")
                if frame:
                    frame.config(bg=THEME["secondary_bg"])
                
                cards_label = player_seat.get("cards_label")
                if cards_label:
                    cards_label.config(text="")
                
                bet_label = player_seat.get("bet_label")
                if bet_label:
                    bet_label.config(text="")
                
                # Hide prominent bet displays
                bet_label_widget = player_seat.get("bet_label_widget")
                bet_label_window = player_seat.get("bet_label_window")
                if bet_label_widget and bet_label_window:
                    self.canvas.itemconfig(bet_label_window, state="hidden")
        
        # Show game control buttons
        self._show_game_control_buttons()
    
    def update_display(self, new_state=None):
        """Updates the UI and logs detailed debugging information."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            self._log_message("DEBUG: update_display called but no game_info available.")
            return

        # (Existing logging...)

        # Update pot and current bet display
        pot_amount = game_info['pot']
        # Use preserved pot amount if hand is completed
        if self.hand_completed and self.preserved_pot_amount > 0:
            pot_amount = self.preserved_pot_amount
    
        self.update_pot_amount(pot_amount)
        
        # Show current bet information in message area if there's a current bet
        if game_info['current_bet'] > 0:
            self.add_game_message(f"💰 Current Bet: ${game_info['current_bet']:.2f}")

        # --- THIS IS THE CRITICAL BUG FIX ---
        # Always display the community cards that are available on the board.
        # Ensure cards remain visible throughout the hand, including during winner announcement
        # Use preserved community cards if hand is completed
        board_cards = game_info['board']
        if self.hand_completed and self.preserved_community_cards:
            # Use preserved cards after hand completion
            board_cards = self.preserved_community_cards
    
        
        # Safety check for community card widgets
        if hasattr(self, 'community_card_widgets') and self.community_card_widgets:
            for i, card_widget in enumerate(self.community_card_widgets):
                if i < len(board_cards):
                    card_widget.set_card(board_cards[i])
                    # Force the card widget to update immediately
                    card_widget.update()
        # NEW: Only clear action indicators when the next player actually takes an action
        # Don't clear just because highlighting changes - wait for actual action
        current_action_player = game_info['action_player']
        # We'll clear action indicators in _animate_player_action when a new action is taken
        
        # Update player info
        if not hasattr(self, 'player_seats') or not self.player_seats:
    
            return
            
        for i, player_seat in enumerate(self.player_seats):
            if not player_seat:
                continue

            player_info = game_info['players'][i]
            player_pod = player_seat.get("player_pod")
            
            # Update PlayerPod with new data
            if player_pod:
                pod_data = {
                    "name": f"{player_info['name']} ({player_info['position']})",
                    "stack": player_info['stack']
                }
                player_pod.update_pod(pod_data)
            
            # FIXED: Highlight based on action_player index, not is_active status
            # Players should be highlighted when it's their turn, even if they fold
            frame = player_seat["frame"]
            action_player = game_info.get('action_player', -1)
    
            if i == action_player:
                frame.config(bg=THEME["accent_primary"])
        
            # Update the prominent bet display on the table
            bet_label_widget = player_seat.get("bet_label_widget")
            bet_label_window = player_seat.get("bet_label_window")
            if bet_label_widget and bet_label_window:
                current_bet = player_info.get("current_bet", 0.0)
                if current_bet > 0 and player_info['is_active']:
                    bet_label_widget.config(text=f"💰 ${current_bet:.2f}")
                    self.canvas.itemconfig(bet_label_window, state="normal")
            # Update player card display with proper card styling
            if player_info['is_active']:
                # Show cards for human players (always visible) or during showdown/end_hand (all active players)
                current_state = self.state_machine.get_current_state()
                is_showdown_or_end = current_state in [PokerState.SHOWDOWN, "end_hand"]
                
                # Show cards for human players or during showdown/end_hand (all active players)
                # Also show cards if hand is completed but player was active (for winner display)
                if player_info['is_human'] or is_showdown_or_end or (self.hand_completed and player_info['is_active']):
                    # Get the stored card widgets
                    card_widgets = player_seat.get("card_widgets", [])
                    if len(card_widgets) >= 2 and len(player_info['cards']) >= 2:
                        # Update first card using raw card string
                        card_widgets[0].set_card(player_info['cards'][0])
                        
                        # Update second card using raw card string
                        card_widgets[1].set_card(player_info['cards'][1])
                else: # Bot's cards are hidden during play - show card backs
                    # Get the stored card widgets
                    card_widgets = player_seat.get("card_widgets", [])
                    if len(card_widgets) >= 2:
                        # Show card backs for hidden cards - use set_card with empty string
                        card_widgets[0].set_card("")  # This should show card back
                        card_widgets[1].set_card("")  # This should show card back
            else: # Player has folded
                # Get the stored card widgets
                card_widgets = player_seat.get("card_widgets", [])
                
                if len(card_widgets) >= 2:
                    # Show folded card backs (dark gray, no border)
            
                    card_widgets[0].set_card("", is_folded=True)  # Dark gray card back
                    card_widgets[1].set_card("", is_folded=True)  # Dark gray card back
        
        # Update last action details - preserve winning announcement until new hand
        if hasattr(self, 'last_action_label'):
            # Only update if we don't have a preserved winning message
            if not self.hand_completed:
                last_action = game_info.get('last_action_details', '')
                self.last_action_label.config(text=last_action)
        
        # Update session information display
        self.update_session_info()
    
    def _update_bet_size_label(self, event=None):
        """Updates the label for the bet sizing slider."""
        self.bet_size_label.config(text=f"${self.bet_size_var.get():.2f}")

    def _submit_preset_bet(self, preset_type):
        """Submit a preset bet action."""
        game_info = self.state_machine.get_game_info()
        if not game_info or "valid_actions" not in game_info:
            return
            
        valid_actions = game_info["valid_actions"]
        if "preset_bets" not in valid_actions:
            return
            
        preset_bets = valid_actions["preset_bets"]
        if preset_type not in preset_bets:
            return
            
        amount = preset_bets[preset_type]
        self._submit_human_action("raise", amount)
    
    def _submit_bet_raise(self):
        """Submits a bet or raise action based on context."""
        game_info = self.state_machine.get_game_info()
        if game_info and game_info.get('current_bet', 0) > 0:
            self._submit_human_action("raise")
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
        
        # Create action indicator
        action_text = action.upper()
        if amount > 0:
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
        
        # Also update the player's display immediately
        if action.upper() == "FOLD":
            # Show "Folded" status immediately
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text="Folded", fg="red")
        elif action.upper() == "CHECK":
            # Show check text
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text="Check", fg="green")
        elif action.upper() in ["CALL", "BET", "RAISE"]:
            # Show bet amount
            cards_label = player_seat.get("cards_label")
            if cards_label:
                cards_label.config(text=f"${amount:.2f}", fg="blue")
    
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
        """Update the stack amount for a specific player."""
        if player_index < len(self.player_seats):
            player_seat = self.player_seats[player_index]
            player_pod = player_seat.get("player_pod")
            
            if player_pod:
                # Update the PlayerPod with new stack amount
                pod_data = {
                    "name": player_pod.name_label.cget("text"),  # Keep existing name
                    "stack": new_amount
                }
                player_pod.update_pod(pod_data)
    
    def _calculate_chip_count(self, amount):
        """Calculate how many chip symbols to display based on amount."""
        if amount <= 10:
            return 3
        elif amount <= 25:
            return 4
        elif amount <= 50:
            return 5
        elif amount <= 100:
            return 6
        elif amount <= 200:
            return 7
        elif amount <= 500:
            return 8
    def _get_chip_symbols(self, amount):
        """Get appropriate chip symbols based on amount."""
        chip_count = self._calculate_chip_count(amount)
        
        # Different chip colors based on amount ranges with better visibility
        if amount <= 25:
            return "🟡" * chip_count  # Yellow chips for small amounts
        elif amount <= 100:
            return "🟢" * chip_count  # Green chips for medium amounts
        elif amount <= 500:
            return "🔴" * chip_count  # Red chips for larger amounts
    def _get_pot_chip_symbols(self, amount):
        """Get unique pot chip symbols based on amount (different from player chips)."""
        chip_count = self._calculate_pot_chip_count(amount)
        
        # Pot uses different chip colors than player stacks
        if amount <= 25:
            return "🟠" * chip_count  # Orange chips for small pots
        elif amount <= 100:
            return "🔶" * chip_count  # Dark orange chips for medium pots
        elif amount <= 500:
            return "🟧" * chip_count  # Light orange chips for large pots
    def _calculate_pot_chip_count(self, amount):
        """Calculate how many pot chip symbols to display based on amount."""
        if amount <= 10:
            return 2
        elif amount <= 25:
            return 3
        elif amount <= 50:
            return 4
        elif amount <= 100:
            return 5
        elif amount <= 200:
            return 6
        elif amount <= 500:
            return 7
    def update_pot_amount(self, new_amount):
        """Updates the pot amount display with the new amount."""
        if hasattr(self, 'pot_label') and self.pot_label is not None:
            self.pot_label.config(text=f"${new_amount:.2f}")
    
    def _on_state_change(self, new_state):
        """Handle state changes from the state machine."""
        self.update_display(new_state)

