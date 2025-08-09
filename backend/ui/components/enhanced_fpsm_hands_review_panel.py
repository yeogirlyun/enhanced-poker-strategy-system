#!/usr/bin/env python3
"""
Enhanced FPSM Hands Review Panel

This is the full-featured hands review panel with complete simulation controls,
step-by-step hand progression, and rich interactive features.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from typing import Dict, List, Any, Optional

# Import core components
from core.json_hands_database import JSONHandsDatabase, HandCategory
from core.types import ActionType
from core.flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, GameEvent, EventListener, Player
)

# Import UI components
from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.gui_models import THEME


class EnhancedFPSMHandsReviewPanel(ttk.Frame, EventListener):
    """
    Enhanced FPSM Hands Review Panel with full simulation controls.
    
    Features:
    - Complete hand simulation controls
    - Step-by-step action progression
    - Street navigation (preflop, flop, turn, river)
    - Player action tracking
    - Game state monitoring
    - Interactive poker game widget
    """
    
    def __init__(self, parent, json_db_path="data/legendary_hands_complete_130_fixed.json", 
                 debug_mode=False, test_mode=False, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize JSON hands database
        self.hands_database = JSONHandsDatabase(json_db_path)
        
        # Mode configuration
        self.debug_mode = debug_mode
        self.test_mode = test_mode
        
        # Data
        self.legendary_hands = []
        self.current_hand = None
        self.current_hand_data = None
        
        # Simulation state
        self.poker_game_widget = None
        self.fpsm = None
        self.current_action_index = 0
        self.current_street = "preflop"
        self.hand_actions = {}  # Actions organized by street
        self.is_simulation_running = False
        self.auto_play = False
        
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
        """Setup the enhanced user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with database info
        self.setup_title_section(main_frame)
        
        # Main content area with three sections
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel: Hand selection (30%)
        self.setup_left_panel(content_frame)
        
        # Center panel: Simulation controls (20%)
        self.setup_center_panel(content_frame)
        
        # Right panel: Game simulation (50%)
        self.setup_right_panel(content_frame)
    
    def setup_title_section(self, parent):
        """Setup title section with database info."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        self.title_label = ttk.Label(
            title_frame, 
            text="🎯 Enhanced Hands Review with Full Simulation", 
            font=('TkDefaultFont', 16, 'bold')
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Database info
        self.db_info_label = ttk.Label(title_frame, text="Loading...")
        self.db_info_label.pack(side=tk.RIGHT)
    
    def setup_left_panel(self, parent):
        """Setup left panel for hand selection."""
        # Create left frame (30% width)
        left_frame = ttk.LabelFrame(parent, text="📚 Hand Selection", padding=10)
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
        
        self.hands_listbox = tk.Listbox(list_container, font=('TkDefaultFont', 10))
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.hands_listbox.yview)
        self.hands_listbox.config(yscrollcommand=scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hands_listbox.bind('<<ListboxSelect>>', self.on_hand_select)
        
        # Hand info
        info_frame = ttk.Frame(left_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(info_frame, text="Hand Details:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        self.hand_info_label = ttk.Label(info_frame, text="Select a hand to view details", 
                                        wraplength=280, justify=tk.LEFT, font=('TkDefaultFont', 9))
        self.hand_info_label.pack(anchor=tk.W, pady=(5, 0))
    
    def setup_center_panel(self, parent):
        """Setup center panel for simulation controls."""
        # Create center frame (20% width)
        center_frame = ttk.LabelFrame(parent, text="🎮 Simulation Controls", padding=10)
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        center_frame.configure(width=250)
        center_frame.pack_propagate(False)
        
        # Hand loading section
        load_section = ttk.LabelFrame(center_frame, text="Load Hand", padding=5)
        load_section.pack(fill=tk.X, pady=(0, 10))
        
        self.load_hand_btn = ttk.Button(load_section, text="▶️ Load Selected Hand", 
                                       command=self.load_selected_hand, width=20)
        self.load_hand_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_btn = ttk.Button(load_section, text="🔄 Reset Simulation", 
                                   command=self.reset_simulation, width=20)
        self.reset_btn.pack(fill=tk.X)
        
        # Simulation controls section
        sim_section = ttk.LabelFrame(center_frame, text="Play Controls", padding=5)
        sim_section.pack(fill=tk.X, pady=(0, 10))
        
        # Play/Pause controls
        play_frame = ttk.Frame(sim_section)
        play_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.play_btn = ttk.Button(play_frame, text="▶️ Play", command=self.play_simulation, width=9)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_btn = ttk.Button(play_frame, text="⏸️ Pause", command=self.pause_simulation, width=9)
        self.pause_btn.pack(side=tk.LEFT)
        
        # Step controls
        step_frame = ttk.Frame(sim_section)
        step_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.prev_btn = ttk.Button(step_frame, text="⏮️ Prev", command=self.previous_action, width=9)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_btn = ttk.Button(step_frame, text="⏭️ Next", command=self.next_action, width=9)
        self.next_btn.pack(side=tk.LEFT)
        
        # Auto-play checkbox
        self.auto_play_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(sim_section, text="Auto-play", variable=self.auto_play_var,
                                    command=self.toggle_auto_play)
        auto_check.pack(anchor=tk.W)
        
        # Street navigation section
        street_section = ttk.LabelFrame(center_frame, text="Street Navigation", padding=5)
        street_section.pack(fill=tk.X, pady=(0, 10))
        
        self.street_var = tk.StringVar(value="preflop")
        streets = ["preflop", "flop", "turn", "river"]
        
        for street in streets:
            street_btn = ttk.Radiobutton(street_section, text=street.capitalize(), 
                                        variable=self.street_var, value=street,
                                        command=lambda s=street: self.jump_to_street(s))
            street_btn.pack(anchor=tk.W)
        
        # Progress section
        progress_section = ttk.LabelFrame(center_frame, text="Progress", padding=5)
        progress_section.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_section, text="No hand loaded", font=('TkDefaultFont', 9))
        self.progress_label.pack(anchor=tk.W)
        
        self.action_progress = ttk.Progressbar(progress_section, mode='determinate')
        self.action_progress.pack(fill=tk.X, pady=(5, 0))
        
        # Status section
        status_section = ttk.LabelFrame(center_frame, text="Status", padding=5)
        status_section.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(status_section, text="Ready", font=('TkDefaultFont', 9, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        # Current action display
        self.current_action_label = ttk.Label(status_section, text="", 
                                             font=('TkDefaultFont', 8), foreground='blue')
        self.current_action_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Initially disable simulation controls
        self.set_simulation_controls_state(False)
    
    def setup_right_panel(self, parent):
        """Setup right panel for game simulation."""
        # Create right frame (50% width)
        right_frame = ttk.LabelFrame(parent, text="🎰 Poker Game Simulation", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Game container
        self.game_container = ttk.Frame(right_frame)
        self.game_container.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.placeholder_label = ttk.Label(
            self.game_container, 
            text="Select a hand and click 'Load Selected Hand' to begin simulation",
            font=('TkDefaultFont', 14),
            foreground='gray'
        )
        self.placeholder_label.pack(expand=True)
    
    def set_simulation_controls_state(self, enabled: bool):
        """Enable or disable simulation controls."""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.play_btn.config(state=state)
        self.pause_btn.config(state=state)
        self.prev_btn.config(state=state)
        self.next_btn.config(state=state)
        
        # Street navigation buttons
        for widget in self.master.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and "Street Navigation" in str(widget):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Radiobutton):
                        child.config(state=state)
    
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
        info_text = f"📊 {db_info['total_hands']} hands • JSON Database"
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
            
            # Add game info
            if self.current_hand_data:
                game_info = self.current_hand_data.get('game', {})
                info_text += f"\\n\\nGame: {game_info.get('variant', 'Unknown')}"
                info_text += f"\\nStakes: {game_info.get('stakes', 'Unknown')}"
                info_text += f"\\nFormat: {game_info.get('format', 'Unknown')}"
                
                # Count actions
                actions = self.current_hand_data.get('actions', {})
                total_actions = sum(len(street_actions) for street_actions in actions.values())
                info_text += f"\\n\\nTotal Actions: {total_actions}"
            
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
            
            # Enable simulation controls
            self.set_simulation_controls_state(True)
            
            self.status_label.config(text="Hand loaded - Ready to simulate")
            print(f"✅ Hand loaded: {self.current_hand.metadata.name}")
            
        except Exception as e:
            error_msg = f"Error loading hand: {str(e)}"
            self.status_label.config(text="❌ Error loading hand")
            messagebox.showerror("Error", error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
    
    def setup_hand_for_simulation(self):
        """Setup hand for FPSM simulation."""
        if not self.current_hand_data:
            return
        
        # Clear existing game widget
        for widget in self.game_container.winfo_children():
            widget.destroy()
        
        # Prepare hand actions
        self.prepare_hand_actions()
        
        # Create FPSM from hand data
        self.fpsm = self.create_fpsm_from_hand_data(self.current_hand_data)
        
        # Create poker game widget
        self.poker_game_widget = ReusablePokerGameWidget(
            self.game_container,
            state_machine=self.fpsm,
            debug_mode=self.debug_mode
        )
        self.poker_game_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Reset simulation state
        self.current_action_index = 0
        self.current_street = "preflop"
        self.is_simulation_running = False
        
        # Update progress
        self.update_progress_display()
        
        print(f"🎮 Setup complete for hand: {self.current_hand.metadata.name}")
    
    def prepare_hand_actions(self):
        """Prepare hand actions organized by street."""
        if not self.current_hand_data:
            return
        
        actions_data = self.current_hand_data.get('actions', {})
        self.hand_actions = {}
        
        # Organize actions by street
        for street, actions in actions_data.items():
            if actions:  # Only include streets with actions
                self.hand_actions[street] = actions
        
        print(f"📋 Prepared actions for streets: {list(self.hand_actions.keys())}")
    
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
        
        # Set board cards if available
        board_data = hand_data.get('board', {})
        if isinstance(board_data, dict):
            all_board_cards = []
            
            # Extract all board cards in order
            flop = board_data.get('flop', [])
            turn = board_data.get('turn', [])
            river = board_data.get('river', [])
            
            all_board_cards.extend(flop if isinstance(flop, list) else [flop] if flop else [])
            all_board_cards.extend(turn if isinstance(turn, list) else [turn] if turn else [])
            all_board_cards.extend(river if isinstance(river, list) else [river] if river else [])
            
            if all_board_cards:
                fpsm.set_board_cards(all_board_cards)
        
        return fpsm
    
    def play_simulation(self):
        """Start or resume simulation playback."""
        self.is_simulation_running = True
        self.auto_play = True
        self.status_label.config(text="Playing simulation...")
        
        if self.auto_play_var.get():
            self.auto_advance()
    
    def pause_simulation(self):
        """Pause simulation playback."""
        self.is_simulation_running = False
        self.auto_play = False
        self.status_label.config(text="Simulation paused")
    
    def next_action(self):
        """Execute the next action in the hand."""
        if not self.hand_actions:
            return
        
        # Find current action
        current_action = self.get_current_action()
        if current_action:
            self.execute_action(current_action)
            self.current_action_index += 1
            self.update_progress_display()
        
        # Auto-advance if enabled
        if self.auto_play and self.is_simulation_running:
            self.master.after(1000, self.auto_advance)  # 1 second delay
    
    def previous_action(self):
        """Go back to the previous action."""
        if self.current_action_index > 0:
            self.current_action_index -= 1
            self.update_progress_display()
            # Note: Full undo would require state snapshots
    
    def get_current_action(self):
        """Get the current action to execute."""
        action_count = 0
        for street, actions in self.hand_actions.items():
            if action_count <= self.current_action_index < action_count + len(actions):
                action_index = self.current_action_index - action_count
                return actions[action_index], street
            action_count += len(actions)
        return None, None
    
    def execute_action(self, action_data):
        """Execute a single action."""
        if not self.fpsm or not action_data:
            return
        
        action, street = action_data
        player_name = action.get('player', '')
        action_type = action.get('type', '').lower()
        amount = action.get('amount', 0)
        
        print(f"🎮 Executing: {player_name} {action_type} {amount} on {street}")
        
        # Update current action display
        self.current_action_label.config(text=f"Current: {player_name} {action_type} {amount}")
        
        # Here you would execute the action on the FPSM
        # This would require matching player names to FPSM player indices
        # and converting action types to ActionType enum values
    
    def jump_to_street(self, street):
        """Jump to a specific street in the hand."""
        self.current_street = street
        # Calculate the action index for the start of this street
        action_count = 0
        for s in self.hand_actions:
            if s == street:
                break
            action_count += len(self.hand_actions.get(s, []))
        
        self.current_action_index = action_count
        self.update_progress_display()
    
    def toggle_auto_play(self):
        """Toggle auto-play mode."""
        self.auto_play = self.auto_play_var.get()
        if self.auto_play and self.is_simulation_running:
            self.auto_advance()
    
    def auto_advance(self):
        """Automatically advance to next action."""
        if self.auto_play and self.is_simulation_running:
            self.next_action()
    
    def update_progress_display(self):
        """Update the progress display."""
        if not self.hand_actions:
            self.progress_label.config(text="No actions to display")
            return
        
        total_actions = sum(len(actions) for actions in self.hand_actions.values())
        
        progress_text = f"Action {self.current_action_index + 1}/{total_actions}"
        progress_text += f" • Street: {self.current_street}"
        
        self.progress_label.config(text=progress_text)
        
        # Update progress bar
        if total_actions > 0:
            progress_percent = (self.current_action_index / total_actions) * 100
            self.action_progress['value'] = progress_percent
    
    def reset_simulation(self):
        """Reset the current simulation."""
        if self.poker_game_widget:
            for widget in self.game_container.winfo_children():
                widget.destroy()
            self.poker_game_widget = None
            self.fpsm = None
            
            # Restore placeholder
            self.placeholder_label = ttk.Label(
                self.game_container, 
                text="Select a hand and click 'Load Selected Hand' to begin simulation",
                font=('TkDefaultFont', 14),
                foreground='gray'
            )
            self.placeholder_label.pack(expand=True)
            
            # Disable controls
            self.set_simulation_controls_state(False)
            
            # Reset state
            self.current_action_index = 0
            self.current_street = "preflop"
            self.is_simulation_running = False
            self.auto_play = False
            
            self.status_label.config(text="Ready")
            self.progress_label.config(text="No hand loaded")
            self.current_action_label.config(text="")
            self.action_progress['value'] = 0
            
            print("🔄 Simulation reset")
    
    def update_font_size(self, size):
        """Update font sizes for all components."""
        self.font_size = size
        # Implementation would update all text elements
    
    def on_event(self, event: GameEvent):
        """Handle FPSM events."""
        if self.debug_mode:
            print(f"🎯 FPSM Event: {event.event_type}")


# Alias for backward compatibility  
FPSMHandsReviewPanelJSON = EnhancedFPSMHandsReviewPanel
