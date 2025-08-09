#!/usr/bin/env python3
"""
FPSM Hands Review Panel - JSON Version

Updated version that uses our validated 130-hand JSON database directly
instead of the older PHH-based database loader.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

# Import core components
from core.json_hands_database import JSONHandsDatabase, HandCategory
from core.types import ActionType
from core.flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, GameEvent, EventListener, Player
)

# Import UI components
from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.gui_models import THEME


class FPSMHandsReviewPanelJSON(ttk.Frame, EventListener):
    """
    Enhanced FPSM Hands Review Panel using JSON database.
    
    This panel provides:
    - Access to all 130 validated legendary hands
    - Interactive step-by-step simulation using FPSM
    - Study mode with hand analysis
    - Event-driven updates
    """
    
    def __init__(self, parent, json_db_path="data/legendary_hands_complete_130_fixed.json", 
                 debug_mode=False, test_mode=False, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize JSON hands database
        self.hands_database = JSONHandsDatabase(json_db_path)
        
        # Mock UI testing support
        self.debug_mode = debug_mode
        self.test_mode = test_mode
        
        # Data
        self.legendary_hands = []
        self.practice_hands = []  # Not used in JSON version
        self.current_hand = None
        self.current_hand_data = None
        
        # UI components
        self.poker_game_widget = None
        self.fpsm = None
        
        # Font size
        self.font_size = 16
        
        # Log system
        self.log_entries = []
        
        # Initialize UI and load data
        if not test_mode:
            self.setup_ui()
        
        self.load_data()
        
        if not test_mode:
            self.update_font_size(self.font_size)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with database info
        self.setup_title_section(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel: Hand selection
        self.setup_left_panel(content_frame)
        
        # Right panel: Game simulation
        self.setup_right_panel(content_frame)
    
    def setup_title_section(self, parent):
        """Setup title section with database info."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        self.title_label = ttk.Label(
            title_frame, 
            text="🎯 Hands Review (JSON Database)", 
            font=('TkDefaultFont', 16, 'bold')
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Database info
        self.db_info_label = ttk.Label(title_frame, text="Loading...")
        self.db_info_label.pack(side=tk.RIGHT)
    
    def setup_left_panel(self, parent):
        """Setup left panel for hand selection."""
        # Create left frame
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.configure(width=300)
        left_frame.pack_propagate(False)
        
        # Category selection
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(category_frame, text="Category:").pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="Legendary Hands")
        category_combo = ttk.Combobox(
            category_frame, 
            textvariable=self.category_var,
            values=["Legendary Hands"],
            state="readonly"
        )
        category_combo.pack(fill=tk.X, pady=(5, 0))
        category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Hands list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="Hands:").pack(anchor=tk.W)
        
        # Hands listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.hands_listbox = tk.Listbox(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.hands_listbox.yview)
        self.hands_listbox.config(yscrollcommand=scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hands_listbox.bind('<<ListboxSelect>>', self.on_hand_select)
        
        # Hand info
        info_frame = ttk.Frame(left_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.hand_info_label = ttk.Label(info_frame, text="Select a hand to view details", wraplength=280)
        self.hand_info_label.pack(anchor=tk.W)
    
    def setup_right_panel(self, parent):
        """Setup right panel for game simulation."""
        # Create right frame
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Simulation controls
        controls_left = ttk.Frame(control_frame)
        controls_left.pack(side=tk.LEFT)
        
        self.load_hand_btn = ttk.Button(controls_left, text="▶️ Load Hand", command=self.load_selected_hand)
        self.load_hand_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_btn = ttk.Button(controls_left, text="🔄 Reset", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status info
        controls_right = ttk.Frame(control_frame)
        controls_right.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(controls_right, text="Ready")
        self.status_label.pack()
        
        # Game container
        self.game_container = ttk.Frame(right_frame)
        self.game_container.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        placeholder_label = ttk.Label(
            self.game_container, 
            text="Select and load a hand to begin simulation",
            font=('TkDefaultFont', 12)
        )
        placeholder_label.pack(expand=True)
    
    def load_data(self):
        """Load hands data from JSON database."""
        try:
            print("📚 Loading hands from JSON database...")
            
            # Load all hands
            all_hands = self.hands_database.load_all_hands()
            self.legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
            
            # Get database info
            db_info = self.hands_database.get_database_info()
            
            print(f"✅ Loaded {len(self.legendary_hands)} legendary hands")
            
            # Update UI if not in test mode
            if not self.test_mode:
                self.update_hands_list()
                self.update_database_info(db_info)
                
        except Exception as e:
            print(f"❌ Error loading hands data: {e}")
            self.legendary_hands = []
            if not self.test_mode:
                self.db_info_label.config(text="❌ Error loading database")
    
    def update_database_info(self, db_info):
        """Update database info display."""
        info_text = f"📊 {db_info['total_hands']} hands loaded from JSON"
        self.db_info_label.config(text=info_text)
    
    def update_hands_list(self):
        """Update the hands listbox."""
        self.hands_listbox.delete(0, tk.END)
        
        # Add legendary hands
        for hand in self.legendary_hands:
            display_name = f"{hand.metadata.id}: {hand.metadata.name}"
            self.hands_listbox.insert(tk.END, display_name)
        
        print(f"📋 Updated hands list with {len(self.legendary_hands)} hands")
    
    def on_category_change(self, event=None):
        """Handle category selection change."""
        self.update_hands_list()
    
    def on_hand_select(self, event=None):
        """Handle hand selection."""
        selection = self.hands_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.legendary_hands):
            hand = self.legendary_hands[index]
            self.current_hand = hand
            
            # Get raw JSON data
            self.current_hand_data = self.hands_database.get_hand_data(hand.metadata.id)
            
            # Update hand info
            info_text = f"ID: {hand.metadata.id}\\nName: {hand.metadata.name}"
            if hand.metadata.study_notes:
                info_text += f"\\n\\nLesson: {hand.metadata.study_notes}"
            
            self.hand_info_label.config(text=info_text)
            
            print(f"🎯 Selected hand: {hand.metadata.id} - {hand.metadata.name}")
    
    def load_selected_hand(self):
        """Load the selected hand for simulation."""
        if not self.current_hand or not self.current_hand_data:
            messagebox.showwarning("No Hand Selected", "Please select a hand first.")
            return
        
        try:
            self.status_label.config(text="Loading hand...")
            print(f"🔄 Loading hand: {self.current_hand.metadata.name}")
            
            # Setup hand for simulation
            self.setup_hand_for_simulation()
            
            self.status_label.config(text="Hand loaded successfully")
            print(f"✅ Hand loaded: {self.current_hand.metadata.name}")
            
        except Exception as e:
            error_msg = f"Error loading hand: {str(e)}"
            self.status_label.config(text="❌ Error loading hand")
            messagebox.showerror("Error", error_msg)
            print(f"❌ {error_msg}")
    
    def setup_hand_for_simulation(self):
        """Setup hand for FPSM simulation."""
        if not self.current_hand_data:
            return
        
        # Clear existing game widget
        for widget in self.game_container.winfo_children():
            widget.destroy()
        
        # Create FPSM from hand data
        self.fpsm = self.create_fpsm_from_hand_data(self.current_hand_data)
        
        # Create poker game widget
        self.poker_game_widget = ReusablePokerGameWidget(
            self.game_container,
            state_machine=self.fpsm,
            debug_mode=self.debug_mode
        )
        self.poker_game_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        print(f"🎮 Setup complete for hand: {self.current_hand.metadata.name}")
    
    def create_fpsm_from_hand_data(self, hand_data):
        """Create FPSM from JSON hand data."""
        # Extract game configuration
        game_config_data = hand_data.get('game_config', {})
        game_config = GameConfig(
            num_players=game_config_data.get('num_players', 2),
            small_blind=game_config_data.get('small_blind', 25),
            big_blind=game_config_data.get('big_blind', 50)
        )
        
        # Create FPSM
        fpsm = FlexiblePokerStateMachine(game_config)
        
        # Add event listener
        fpsm.add_event_listener(self)
        
        # Setup players
        players_data = hand_data.get('players', [])
        for player_data in players_data:
            player = Player(
                name=player_data.get('name', 'Unknown'),
                stack=player_data.get('starting_stack', 1000),
                seat=player_data.get('seat', 1)
            )
            fpsm.add_player(player)
        
        # Set board cards
        board_data = hand_data.get('board', {})
        if isinstance(board_data, dict):
            # Extract all board cards
            flop = board_data.get('flop', [])
            turn = board_data.get('turn', [])
            river = board_data.get('river', [])
            
            all_board_cards = flop.copy()
            if turn:
                if isinstance(turn, list):
                    all_board_cards.extend(turn)
                else:
                    all_board_cards.append(turn)
            if river:
                if isinstance(river, list):
                    all_board_cards.extend(river)
                else:
                    all_board_cards.append(river)
            
            fpsm.set_board_cards(all_board_cards)
        
        return fpsm
    
    def reset_simulation(self):
        """Reset the current simulation."""
        if self.poker_game_widget:
            for widget in self.game_container.winfo_children():
                widget.destroy()
            self.poker_game_widget = None
            self.fpsm = None
            
            # Add placeholder
            placeholder_label = ttk.Label(
                self.game_container, 
                text="Select and load a hand to begin simulation",
                font=('TkDefaultFont', 12)
            )
            placeholder_label.pack(expand=True)
            
            self.status_label.config(text="Ready")
            print("🔄 Simulation reset")
    
    def update_font_size(self, size):
        """Update font sizes for all components."""
        self.font_size = size
        # Implementation would update all text elements
        # For now, just store the size
    
    def on_event(self, event: GameEvent):
        """Handle FPSM events."""
        # Basic event handling for debugging
        if self.debug_mode:
            print(f"🎯 FPSM Event: {event.event_type}")


# For backward compatibility
FPSMHandsReviewPanel = FPSMHandsReviewPanelJSON
