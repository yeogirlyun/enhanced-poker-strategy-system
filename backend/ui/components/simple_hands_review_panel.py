#!/usr/bin/env python3
"""
Simple Hands Review Panel - Clean Data Rendering Approach

This panel replicates the practice session UI exactly but without complex game logic.
It simply renders hand data step-by-step based on user navigation.

Key principles:
- UI layer is a dumb renderer - NO game logic
- All data comes from JSON hand files
- Step-by-step navigation (next/prev/play)
- Looks and feels exactly like practice session
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List

# Core components
from core.json_hands_database import JSONHandsDatabase, HandCategory

# Simple components
from .simple_hands_data_renderer import SimpleHandsDataRenderer
from .simple_poker_canvas import SimplePokerCanvas


class SimpleHandsReviewPanel(ttk.Frame):
    """
    Simple hands review panel that replicates practice session UI exactly.
    
    This panel provides:
    - Hand selection and categorization (UI only)
    - Step-by-step navigation controls (UI only)
    - Educational features and annotations (UI only)
    - Clean data-driven rendering
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Get session logger
        try:
            from core.session_logger import get_session_logger
            self.logger = get_session_logger()
            if self.logger:
                self.logger.log_system(
                    "INFO",
                    "SIMPLE_HANDS_REVIEW",
                    "SimpleHandsReviewPanel __init__ started",
                    {},
                )
        except Exception as e:
            self.logger = None
            print(f"🚨 SIMPLE HANDS REVIEW: Logger initialization failed: {e}")

        # Console fallback logging
        print("🔧 CONSOLE: SimpleHandsReviewPanel __init__ started")

        # Initialize hands database
        self.hands_database = JSONHandsDatabase(
            "data/clean_poker_hands_flat.json"
        )

        # UI state (NO game logic)
        self.legendary_hands = []
        self.practice_hands = []
        self.current_hand_index = -1
        self.font_size = 12
        self.mode = "legendary"  # or "practice"

        # Simple components
        self.data_renderer: Optional[SimpleHandsDataRenderer] = None
        self.poker_canvas: Optional[SimplePokerCanvas] = None

        # UI elements
        self.hand_listbox = None
        self.progress_var = None
        self.action_label_var = None
        self.step_buttons = {}

        # Setup
        if self.logger:
            self.logger.log_system(
                "INFO", "SIMPLE_HANDS_REVIEW", "🔧 About to setup UI", {}
            )
        self._setup_ui()

        if self.logger:
            self.logger.log_system(
                "INFO", "SIMPLE_HANDS_REVIEW", "🔧 UI setup completed", {}
            )

        # Load hands
        self._load_hands()

    def _setup_ui(self):
        """Setup the UI components."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top control panel (hand selection)
        self._create_top_control_panel(main_container)

        # Middle poker table area
        self._create_poker_table_area(main_container)

        # Bottom navigation panel
        self._create_bottom_navigation_panel(main_container)

    def _create_top_control_panel(self, parent):
        """Create the top control panel for hand selection."""
        top_frame = ttk.LabelFrame(parent, text="Hand Selection", padding=10)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Mode selection
        mode_frame = ttk.Frame(top_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="legendary")
        mode_combo = ttk.Combobox(
            mode_frame, 
            textvariable=self.mode_var,
            values=["legendary", "practice"],
            state="readonly",
            width=15
        )
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        # Hand list
        list_frame = ttk.Frame(top_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(list_frame, text="Available Hands:").pack(anchor=tk.W)
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.hand_listbox = tk.Listbox(
            listbox_frame, 
            height=8,
            selectmode=tk.SINGLE
        )
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.hand_listbox.yview)
        self.hand_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.hand_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hand_listbox.bind("<<ListboxSelect>>", self._on_hand_selected)

        # Load button
        load_button = ttk.Button(
            top_frame, 
            text="Load Selected Hand", 
            command=self._load_selected_hand
        )
        load_button.pack(pady=(10, 0))

    def _create_poker_table_area(self, parent):
        """Create the poker table area."""
        table_frame = ttk.LabelFrame(parent, text="Poker Table", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create simple poker canvas
        self.poker_canvas = SimplePokerCanvas(table_frame)
        self.poker_canvas.pack(fill=tk.BOTH, expand=True)

    def _create_bottom_navigation_panel(self, parent):
        """Create the bottom navigation panel."""
        nav_frame = ttk.LabelFrame(parent, text="Navigation", padding=10)
        nav_frame.pack(fill=tk.X)

        # Progress display
        progress_frame = ttk.Frame(nav_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="No hand loaded")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=(10, 0))

        # Action label
        action_frame = ttk.Frame(nav_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(action_frame, text="Current Action:").pack(side=tk.LEFT)
        self.action_label_var = tk.StringVar(value="No action")
        ttk.Label(action_frame, textvariable=self.action_label_var).pack(side=tk.LEFT, padx=(10, 0))

        # Navigation buttons
        button_frame = ttk.Frame(nav_frame)
        button_frame.pack(fill=tk.X)

        self.step_buttons = {
            "first": ttk.Button(button_frame, text="⏮ First", command=self._go_to_first),
            "prev": ttk.Button(button_frame, text="⏪ Previous", command=self._go_to_previous),
            "play": ttk.Button(button_frame, text="▶ Play", command=self._play_sequence),
            "next": ttk.Button(button_frame, text="⏩ Next", command=self._go_to_next),
            "last": ttk.Button(button_frame, text="⏭ Last", command=self._go_to_last)
        }

        # Position buttons
        self.step_buttons["first"].pack(side=tk.LEFT, padx=(0, 5))
        self.step_buttons["prev"].pack(side=tk.LEFT, padx=(0, 5))
        self.step_buttons["play"].pack(side=tk.LEFT, padx=(0, 5))
        self.step_buttons["next"].pack(side=tk.LEFT, padx=(0, 5))
        self.step_buttons["last"].pack(side=tk.LEFT, padx=(0, 5))

        # Initially disable navigation buttons
        self._update_navigation_buttons()

    def _load_hands(self):
        """Load hands from the database."""
        try:
            if self.logger:
                self.logger.log_system(
                    "INFO", "SIMPLE_HANDS_REVIEW", "Loading hands from database", {}
                )

            # Load legendary hands
            legendary_result = self.hands_database.get_hands_by_category(HandCategory.LEGENDARY)
            self.legendary_hands = legendary_result if isinstance(legendary_result, list) else []
            
            # Load practice hands
            practice_result = self.hands_database.get_hands_by_category(HandCategory.PRACTICE)
            self.practice_hands = practice_result if isinstance(practice_result, list) else []

            if self.logger:
                self.logger.log_system(
                    "INFO", "SIMPLE_HANDS_REVIEW", 
                    f"Loaded {len(self.legendary_hands)} legendary, {len(self.practice_hands)} practice hands",
                    {}
                )

            # Populate listbox
            self._populate_hand_listbox()

        except Exception as e:
            error_msg = f"Failed to load hands: {e}"
            if self.logger:
                self.logger.log_system("ERROR", "SIMPLE_HANDS_REVIEW", error_msg, {"error": str(e)})
            messagebox.showerror("Error", error_msg)

    def _populate_hand_listbox(self):
        """Populate the hand listbox with available hands."""
        if not self.hand_listbox:
            return

        self.hand_listbox.delete(0, tk.END)
        
        hands_to_show = self.legendary_hands if self.mode == "legendary" else self.practice_hands
        
        for i, hand in enumerate(hands_to_show):
            # Use ParsedHand attributes instead of dict methods
            hand_name = f"{hand.metadata.id} - {hand.metadata.name} ({hand.game_info.get('num_players', 0)} players)"
            self.hand_listbox.insert(tk.END, hand_name)

    def _on_mode_changed(self, event=None):
        """Handle mode change."""
        self._populate_hand_listbox()
        self.current_hand_index = -1
        self._update_navigation_buttons()

    def _on_hand_selected(self, event=None):
        """Handle hand selection."""
        selection = self.hand_listbox.curselection()
        if selection:
            self.current_hand_index = selection[0]

    def _load_selected_hand(self):
        """Load the selected hand."""
        if self.current_hand_index < 0:
            messagebox.showwarning("Warning", "Please select a hand first")
            return

        try:
            hands_to_use = self.legendary_hands if self.mode == "legendary" else self.practice_hands
            selected_hand = hands_to_use[self.current_hand_index]
            
            print(f"🔍 DEBUG: Selected hand type: {type(selected_hand)}")
            print(f"🔍 DEBUG: Selected hand attributes: {dir(selected_hand)}")
            print(f"🔍 DEBUG: Game info: {selected_hand.game_info}")
            print(f"🔍 DEBUG: Players count: {len(selected_hand.players)}")
            print(f"🔍 DEBUG: Actions keys: {list(selected_hand.actions.keys())}")
            
            if self.logger:
                self.logger.log_system(
                    "INFO", "SIMPLE_HANDS_REVIEW", 
                    f"Loading hand: {selected_hand.metadata.name}",
                    {"hand_id": selected_hand.metadata.id}
                )

            # Create data renderer for this hand
            print("🔍 DEBUG: Creating data renderer...")
            self.data_renderer = SimpleHandsDataRenderer(selected_hand)
            print(f"🔍 DEBUG: Data renderer created, steps: {self.data_renderer.get_total_steps()}")
            
            # Update poker canvas with first step
            if self.poker_canvas and self.data_renderer:
                current_step = self.data_renderer.get_current_step()
                print(f"🔍 DEBUG: Current step: {current_step}")
                self.poker_canvas.render_step(current_step)
                
            # Update UI
            self._update_progress_display()
            self._update_navigation_buttons()

        except Exception as e:
            error_msg = f"Failed to load hand: {e}"
            print(f"🔍 DEBUG: Error details: {e}")
            import traceback
            traceback.print_exc()
            if self.logger:
                self.logger.log_system("ERROR", "SIMPLE_HANDS_REVIEW", error_msg, {"error": str(e)})
            messagebox.showerror("Error", error_msg)

    def _update_progress_display(self):
        """Update the progress display."""
        if not self.data_renderer:
            self.progress_var.set("No hand loaded")
            self.action_label_var.set("No action")
            return

        current_step_index = self.data_renderer.current_step_index
        total_steps = self.data_renderer.get_total_steps()
        
        self.progress_var.set(f"Step {current_step_index + 1} of {total_steps}")
        
        # Get action description
        action_desc = self.data_renderer.get_current_action_description()
        self.action_label_var.set(action_desc)

    def _update_navigation_buttons(self):
        """Update navigation button states."""
        if not self.data_renderer:
            for button in self.step_buttons.values():
                button.config(state=tk.DISABLED)
            return

        current_step_index = self.data_renderer.current_step_index
        total_steps = self.data_renderer.get_total_steps()

        # Update button states
        self.step_buttons["first"].config(state=tk.NORMAL if current_step_index > 0 else tk.DISABLED)
        self.step_buttons["prev"].config(state=tk.NORMAL if current_step_index > 0 else tk.DISABLED)
        self.step_buttons["next"].config(state=tk.NORMAL if current_step_index < total_steps - 1 else tk.DISABLED)
        self.step_buttons["last"].config(state=tk.NORMAL if current_step_index < total_steps - 1 else tk.DISABLED)
        self.step_buttons["play"].config(state=tk.NORMAL)

    def _go_to_first(self):
        """Go to the first step."""
        if self.data_renderer:
            self.data_renderer.go_to_first()
            self._update_display()

    def _go_to_previous(self):
        """Go to the previous step."""
        if self.data_renderer:
            self.data_renderer.go_to_previous()
            self._update_display()

    def _go_to_next(self):
        """Go to the next step."""
        if self.data_renderer:
            self.data_renderer.go_to_next()
            self._update_display()

    def _go_to_last(self):
        """Go to the last step."""
        if self.data_renderer:
            self.data_renderer.go_to_last()
            self._update_display()

    def _play_sequence(self):
        """Play the sequence automatically."""
        if not self.data_renderer:
            return

        # Simple auto-play - could be enhanced with configurable speed
        def play_next():
            if self.data_renderer and self.data_renderer.get_current_step() < self.data_renderer.get_total_steps() - 1:
                self.data_renderer.go_to_next()
                self._update_display()
                self.after(1000, play_next)  # 1 second delay

        play_next()

    def _update_display(self):
        """Update the display after navigation."""
        if self.poker_canvas and self.data_renderer:
            self.poker_canvas.render_step(self.data_renderer.get_current_step())
            self._update_progress_display()
            self._update_navigation_buttons()
