"""
Hands Review Tab — Unified Panel (drop-in replacement)

This module provides a clean, self-contained implementation of the Hands Review tab
that fixes import-path drift, adds conversion caching, and works with lightweight
fallbacks even if some legacy UI/session pieces are missing.

Key Features:
- Loads hands from sessions-style JSON or Hand Model JSON
- Uses SHA-256 conversion cache to avoid 150+ re-conversions
- Normalizes player IDs for robust matching
- Replays actions with HandModelDecisionEngine
- Uses backend.core.* imports to avoid import errors
- Lightweight fallbacks for missing components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Use internal backend module imports (run from backend/ per project convention)
try:
    from core.hand_model import Hand
    from core.hand_model_decision_engine import HandModelDecisionEngine
    from core.gto_to_hand_converter import GTOToHandConverter
    from core.legendary_to_hand_converter import LegendaryToHandConverter, is_legendary_hand_obj
    from core.gui_models import THEME, FONTS
    from core.bot_session_state_machine import HandsReviewBotSession
    from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
    from core.flexible_poker_state_machine import GameConfig
except ImportError as e:
    print(f"Import warning: {e}. Using fallbacks.")
    # Fallback definitions if imports fail
    class Hand:
        def __init__(self, **kwargs):
            # Set default attributes
            self.actions = kwargs.get('actions', [])
            self.metadata = kwargs.get('metadata', {})
            self.seats = kwargs.get('seats', [])
            # Set any other attributes
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class HandModelDecisionEngine:
        def __init__(self, hand):
            self.hand = hand
            self.current_step = 0
            self.total_steps = len(getattr(hand, 'actions', []))
        
        def get_decision(self, player_id, game_state):
            if self.current_step >= self.total_steps:
                return ("CHECK", 0, "Hand complete")
            action = self.hand.actions[self.current_step]
            self.current_step += 1
            return (action.action_type, action.amount, f"Replaying: {action.action_type}")
        
        def reset(self):
            self.current_step = 0
    
    class GTOToHandConverter:
        @staticmethod
        def convert_gto_hand(gto_data):
            return Hand(actions=[], metadata={})
    class LegendaryToHandConverter:
        def convert_hand(self, data):
            return Hand(actions=[], metadata={})
    def is_legendary_hand_obj(obj):
        return False
    
    class HandsReviewBotSession:
        def __init__(self, *args, **kwargs):
            self.game_state = None
    
    class ReusablePokerGameWidget(ttk.Frame):
        def __init__(self, parent, **kwargs):
            super().__init__(parent)
    
    class GameConfig:
        def __init__(self, **kwargs):
            pass
    
    # Fallback theme
    THEME = {
        "primary_bg": "#2D3748",
        "widget_bg": "#4A5568", 
        "text": "#E2E8F0",
        "button_call": "#38A169",
        "button_fold": "#E53E3E",
        "border_inactive": "#718096"
    }
    
    FONTS = {
        "header": ("Arial", 12, "bold"),
        "main": ("Arial", 10),
        "small": ("Arial", 8),
        "large": ("Arial", 16, "bold")
    }


# Removed ReplaySession - now using HandsReviewBotSession architecture


class UnifiedHandsReviewPanel(ttk.Frame):
    """
    Unified Hands Review Panel following the bot session architecture.
    
    This panel reuses the same architecture as GTO simulation:
    - HandsReviewBotSession (bot session state machine)
    - ReusablePokerGameWidget (poker table display)
    - SHA-256 conversion caching to prevent repeated processing
    - Player ID normalization for robust matching
    """
    
    def __init__(self, parent, session_logger=None, sound_manager=None):
        super().__init__(parent, style="Card.TFrame")
        self.parent = parent
        self.session_logger = session_logger or self._create_fallback_logger()
        self.sound_manager = sound_manager
        
        # Conversion cache to prevent 150+ re-conversions
        self._conversion_cache: Dict[str, Hand] = {}
        
        # Current state
        self.available_hands: List[Dict[str, Any]] = []
        self.selected_hand_index: Optional[int] = None
        self.session_active = False
        
        # Bot session components (following GTO architecture)
        self.hands_review_session: Optional[HandsReviewBotSession] = None
        self.poker_game_widget: Optional[ReusablePokerGameWidget] = None
        
        # UI components
        self.hands_listbox: Optional[tk.Listbox] = None
        self.poker_table_frame: Optional[ttk.Frame] = None
        self.controls_frame: Optional[ttk.Frame] = None
        self.info_label: Optional[ttk.Label] = None
        self.game_placeholder: Optional[ttk.Label] = None
        
        self._create_ui()
        self._load_hands()
        
        self.session_logger.log_system("INFO", "HANDS_REVIEW", "UnifiedHandsReviewPanel initialized")
    
    def _create_fallback_logger(self):
        """Create a fallback logger if none provided."""
        class FallbackLogger:
            def log_system(self, level, component, message):
                print(f"[{level}] {component}: {message}")
        return FallbackLogger()
    
    def _create_ui(self):
        """Create the three-panel UI layout."""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=3)  # Left panel (hand list)
        self.grid_columnconfigure(1, weight=7)  # Right panel (poker table + controls)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel: Hand selection
        self._create_hand_selection_panel()
        
        # Right panel: Poker table and controls
        self._create_poker_panel()
    
    def _create_hand_selection_panel(self):
        """Create the left panel for hand selection."""
        left_frame = ttk.LabelFrame(self, text="Available Hands", style="Card.TLabelframe")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        
        # Hands listbox with scrollbar
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        
        self.hands_listbox = tk.Listbox(
            listbox_frame,
            bg=THEME["widget_bg"],
            fg=THEME["text"],
            selectbackground=THEME["button_call"],
            font=FONTS["main"],
            activestyle="none"
        )
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.hands_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.config(yscrollcommand=scrollbar.set)
        
        # Load hand button
        load_button = ttk.Button(
            left_frame,
            text="Load Selected Hand",
            command=self._load_selected_hand,
            style="Primary.TButton"
        )
        load_button.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        
        # Manual reload button
        reload_button = ttk.Button(
            left_frame,
            text="🔄 Reload Hands",
            command=self._load_hands,
            style="Secondary.TButton"
        )
        reload_button.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
    
    def _create_poker_panel(self):
        """Create the right panel for poker table and controls."""
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=7)  # Poker table
        right_frame.grid_rowconfigure(1, weight=2)  # Controls and comments
        right_frame.grid_rowconfigure(2, weight=1)  # Info
        
        # Poker table area (container for ReusablePokerGameWidget)
        self.poker_table_frame = ttk.LabelFrame(right_frame, text="Poker Table", style="Card.TLabelframe")
        self.poker_table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.poker_table_frame.grid_columnconfigure(0, weight=1)
        self.poker_table_frame.grid_rowconfigure(0, weight=1)
        
        # Initially show placeholder (like GTO session)
        self.game_placeholder = ttk.Label(
            self.poker_table_frame,
            text="Select a hand from the left panel to begin review",
            font=FONTS["large"],  # Use larger font
            foreground=THEME["text"]
        )
        self.game_placeholder.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Controls area
        self._create_controls_panel(right_frame)
        
        # Info area
        self.info_label = ttk.Label(
            right_frame,
            text="Ready to load hand",
            font=FONTS["main"],
            foreground=THEME["text"]
        )
        self.info_label.grid(row=2, column=0, pady=5, sticky="ew")
    
    def _create_controls_panel(self, parent):
        """Create the controls panel."""
        self.controls_frame = ttk.LabelFrame(parent, text="Controls", style="Card.TLabelframe")
        self.controls_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.controls_frame)
        button_frame.pack(pady=10)
        
        # Control buttons (using larger fonts like other tabs)
        self.reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self._reset_hand,
            state="disabled",
            style="Primary.TButton"
        )
        self.reset_button.pack(side="left", padx=10, pady=5)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next",
            command=self._next_action,
            state="disabled",
            style="Primary.TButton"
        )
        self.next_button.pack(side="left", padx=10, pady=5)
        
        self.auto_play_button = ttk.Button(
            button_frame,
            text="Auto Play",
            command=self._auto_play,
            state="disabled",
            style="Primary.TButton"
        )
        self.auto_play_button.pack(side="left", padx=10, pady=5)
        
        # Action display (using larger font like other tabs)
        self.action_display = tk.Text(
            self.controls_frame,
            height=4,
            bg=THEME["widget_bg"],
            fg=THEME["text"],
            font=FONTS["main"],  # Use main font instead of small
            wrap="word",
            state="disabled"
        )
        self.action_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _load_hands(self):
        """Load available hands from data files."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW", "Loading available hands...")
        
        hands_found = 0
        data_directories = ["data", "backend/data", "../data"]
        
        for data_dir in data_directories:
            if not os.path.exists(data_dir):
                continue
                
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW", f"Checking directory: {data_dir}")
            
            for filename in os.listdir(data_dir):
                if not filename.endswith('.json'):
                    continue
                    
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Handle different JSON formats
                    if isinstance(data, dict):
                        if 'hands' in data and isinstance(data['hands'], list):
                            # Sessions-style format
                            for i, hand in enumerate(data['hands']):
                                self.available_hands.append({
                                    'source_file': filepath,
                                    'hand_index': i,
                                    'id': f"{filename}_{i}",
                                    'display_name': f"{filename} Hand {i+1}",
                                    'raw_data': hand
                                })
                                hands_found += 1
                        elif 'metadata' in data or 'actions' in data:
                            # Hand Model format
                            self.available_hands.append({
                                'source_file': filepath,
                                'hand_index': 0,
                                'id': filename.replace('.json', ''),
                                'display_name': filename.replace('.json', ''),
                                'raw_data': data
                            })
                            hands_found += 1
                    elif isinstance(data, list):
                        # Array of hands
                        for i, hand in enumerate(data):
                            self.available_hands.append({
                                'source_file': filepath,
                                'hand_index': i,
                                'id': f"{filename}_{i}",
                                'display_name': f"{filename} Hand {i+1}",
                                'raw_data': hand
                            })
                            hands_found += 1
                            
                except Exception as e:
                    self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Failed to load {filepath}: {e}")
        
        # Update UI
        self._update_hands_list()
        self.session_logger.log_system("INFO", "HANDS_REVIEW", f"Loaded {hands_found} hands from {len(data_directories)} directories")
        
        if hands_found == 0:
            self.info_label.config(text="No hands found in data directories")
        else:
            self.info_label.config(text=f"{hands_found} hands available")
    
    def _update_hands_list(self):
        """Update the hands listbox display."""
        if not self.hands_listbox:
            return
            
        self.hands_listbox.delete(0, tk.END)
        for hand in self.available_hands:
            self.hands_listbox.insert(tk.END, hand['display_name'])
    
    def _hash_hand_data(self, raw_data: Any) -> str:
        """Generate SHA-256 hash for conversion caching."""
        json_str = json.dumps(raw_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _convert_with_cache(self, raw_data: Any) -> Hand:
        """Convert hand data to Hand model with caching."""
        cache_key = self._hash_hand_data(raw_data)
        
        if cache_key in self._conversion_cache:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Using cached conversion")
            return self._conversion_cache[cache_key]
        
        self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Converting hand data...")
        
        try:
            # Detect format and convert appropriately
            if isinstance(raw_data, dict):
                # Already Hand model?
                if "metadata" in raw_data and "seats" in raw_data:
                    hand_obj = Hand.from_dict(raw_data) if hasattr(Hand, 'from_dict') else None
                    if hand_obj:
                        self._conversion_cache[cache_key] = hand_obj
                        self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Loaded Hand model directly")
                        return hand_obj

                # Legendary format (street-keyed actions dict)
                if is_legendary_hand_obj(raw_data):
                    conv = LegendaryToHandConverter()
                    hand_obj = conv.convert_hand(raw_data)
                    self._conversion_cache[cache_key] = hand_obj
                    self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Converted legendary hand → Hand model")
                    return hand_obj

                # GTO format fallback
                if ("initial_state" in raw_data) or isinstance(raw_data.get("actions"), list):
                    hand_obj = GTOToHandConverter.convert_gto_hand(raw_data)
                    self._conversion_cache[cache_key] = hand_obj
                    self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Converted GTO hand → Hand model")
                    return hand_obj

            # Unknown format
            raise ValueError("Unsupported hand data format")

        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Conversion failed: {e}")
            raise
    
    def _normalize_player_id(self, player_id: str) -> str:
        """Normalize player ID format (e.g., 'Player 1' -> 'Player1')."""
        return player_id.replace(' ', '')
    
    def _load_selected_hand(self):
        """Load the selected hand for review (following GTO session architecture)."""
        if not self.hands_listbox or not self.hands_listbox.curselection():
            messagebox.showwarning("No Selection", "Please select a hand from the list")
            return
        
        self.selected_hand_index = self.hands_listbox.curselection()[0]
        selected_hand = self.available_hands[self.selected_hand_index]
        
        self.session_logger.log_system("INFO", "HANDS_REVIEW", f"Loading hand: {selected_hand['display_name']}")
        
        try:
            # Convert to Hand model with caching
            hand = self._convert_with_cache(selected_hand['raw_data'])
            
            # Create HandsReviewBotSession (like GTOBotSession in GTO tab)
            game_config = GameConfig(
                starting_stack=1000,  # Default values
                small_blind=5,
                big_blind=10,
                num_players=3
            )
            
            # Create decision engine and session
            decision_engine = HandModelDecisionEngine(hand)
            self.hands_review_session = HandsReviewBotSession(
                config=game_config,
                decision_engine=decision_engine,
            )
            
            # Set the preloaded hand data (provide actual Hand model)
            try:
                self.hands_review_session.set_preloaded_hand_data({"hand_model": hand})
            except Exception:
                # Fallback to raw data if session expects legacy structure
                self.hands_review_session.set_preloaded_hand_data(selected_hand['raw_data'])
            
            # Create ReusablePokerGameWidget (like GTO session)
            if self.poker_game_widget:
                self.poker_game_widget.destroy()
            
            self.poker_game_widget = ReusablePokerGameWidget(
                self.poker_table_frame,
                state_machine=self.hands_review_session
            )
            
            # Replace placeholder with actual poker table (like GTO session)
            if self.game_placeholder:
                self.game_placeholder.grid_remove()
            self.poker_game_widget.grid(row=0, column=0, sticky="nsew")
            
            # Start the session (like GTO session)
            success = self.hands_review_session.start_session()
            if success:
                self.session_active = True
                self._enable_controls()
                self.info_label.config(text=f"Hand loaded: {selected_hand['display_name']}")
                self._display_action("Hand loaded successfully. Click Next to begin replay.")
                
                # Update poker widget to show initial state (like GTO session)
                if hasattr(self, 'poker_game_widget'):
                    self.poker_game_widget.update_display("hand_start")
                    # Defer one more update for proper layout
                    self.after(150, lambda: self.poker_game_widget.update_display("hand_start"))
                
                if self.sound_manager:
                    # Use configured poker event for chip bet sound
                    self.sound_manager.play_poker_event_sound("chip_bet")
            else:
                self.info_label.config(text="Failed to load hand")
                self._display_action("Failed to start replay session.")
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Failed to load hand: {e}")
            self.info_label.config(text=f"Error loading hand: {e}")
            self._display_action(f"Error: {e}")
    
# _update_poker_display removed - now handled by ReusablePokerGameWidget
    
    def _enable_controls(self):
        """Enable the control buttons."""
        self.reset_button.config(state="normal")
        self.next_button.config(state="normal")
        self.auto_play_button.config(state="normal")
    
    def _disable_controls(self):
        """Disable the control buttons."""
        self.reset_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.auto_play_button.config(state="disabled")
    
    def _next_action(self):
        """Execute the next action in the replay (following GTO session architecture)."""
        if not self.hands_review_session or not self.session_active:
            return
        
        try:
            # Execute next action via bot session (like GTO session)
            result = self.hands_review_session.execute_next_bot_action()
            
            if result:
                # Update poker table display
                if self.poker_game_widget:
                    self.poker_game_widget.update_display("action_complete")
                
                # Get explanation from session
                explanation = "Action executed"
                if hasattr(self.hands_review_session, 'decision_history') and self.hands_review_session.decision_history:
                    last_decision = self.hands_review_session.decision_history[-1]
                    explanation = last_decision.get('explanation', 'Action executed')
                
                self._display_action(explanation)
                
                if self.sound_manager:
                    # Use UI click event for button feedback
                    self.sound_manager.play_poker_event_sound("ui_click")
            else:
                # Session complete or failed
                self._display_action("Hand replay completed")
                self.info_label.config(text="Hand replay completed")
                self._disable_controls()
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Failed to execute next action: {e}")
            self._display_action(f"Error: {e}")
    
    def _reset_hand(self):
        """Reset the hand to the beginning."""
        if not self.hands_review_session:
            return
        
        try:
            # Reset the decision engine
            if hasattr(self.hands_review_session, 'decision_engine'):
                self.hands_review_session.decision_engine.reset()
            
            # Restart the session
            success = self.hands_review_session.start_session()
            if success:
                self._enable_controls()
                if self.poker_game_widget:
                    self.poker_game_widget.update_display("hand_start")
                self.info_label.config(text="Hand reset to beginning")
                self._display_action("Hand reset. Click Next to begin replay.")
                
                if self.sound_manager:
                    # Use configured poker event for chip bet sound
                    self.sound_manager.play_poker_event_sound("chip_bet")
            else:
                self._display_action("Failed to reset hand")
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Failed to reset hand: {e}")
            self._display_action(f"Reset error: {e}")
    
    def _auto_play(self):
        """Auto-play through remaining actions."""
        if not self.hands_review_session or not self.session_active:
            return
        
        actions_played = 0
        try:
            while actions_played < 50:  # Safety limit
                result = self.hands_review_session.execute_next_bot_action()
                if not result:
                    break
                actions_played += 1
            
            # Update final display
            if self.poker_game_widget:
                self.poker_game_widget.update_display("action_complete")
            
            self.info_label.config(text=f"Auto-played {actions_played} actions")
            self._display_action(f"Auto-play completed. {actions_played} actions executed.")
            
            # Check if session is complete
            if not self.hands_review_session.execute_next_bot_action():
                self._disable_controls()
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Auto-play failed: {e}")
            self._display_action(f"Auto-play error: {e}")
    
    def _display_action(self, message: str):
        """Display an action message in the action display."""
        if not self.action_display:
            return
            
        self.action_display.config(state="normal")
        self.action_display.insert(tk.END, f"{message}\n")
        self.action_display.see(tk.END)
        self.action_display.config(state="disabled")
    
    def update_font_size(self, base_size: int):
        """Update font sizes based on global setting (controlled by app font size)."""
        try:
            # Update the listbox font
            if self.hands_listbox:
                new_font = (FONTS["main"][0], base_size)
                self.hands_listbox.config(font=new_font)
            
            # Update action display font
            if self.action_display:
                new_font = (FONTS["main"][0], base_size)
                self.action_display.config(font=new_font)
            
            # Update info label font
            if self.info_label:
                new_font = (FONTS["main"][0], base_size)
                self.info_label.config(font=new_font)
            
            # Update placeholder font
            if self.game_placeholder:
                new_font = (FONTS["large"][0], base_size + 4)  # Larger for placeholder
                self.game_placeholder.config(font=new_font)
                
            # Update poker game widget font if it exists
            if self.poker_game_widget and hasattr(self.poker_game_widget, 'update_font_size'):
                self.poker_game_widget.update_font_size(base_size)
                
        except Exception as e:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW", f"Font update failed: {e}")


# Convenience function for easy integration
def create_hands_review_panel(parent, session_logger=None, sound_manager=None) -> UnifiedHandsReviewPanel:
    """Create and return a UnifiedHandsReviewPanel instance."""
    return UnifiedHandsReviewPanel(parent, session_logger, sound_manager)


if __name__ == "__main__":
    # Quick test when run directly
    root = tk.Tk()
    root.title("Hands Review Test")
    root.geometry("1200x800")
    
    panel = UnifiedHandsReviewPanel(root)
    panel.pack(fill="both", expand=True)
    
    root.mainloop()
