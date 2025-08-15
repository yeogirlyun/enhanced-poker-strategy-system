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

# Use backend.core.* imports to avoid import-path drift
try:
    from backend.core.hand_model import Hand, HandMetadata, Seat, Action, ActionType
    from backend.core.hand_model_decision_engine import HandModelDecisionEngine
    from backend.core.gto_to_hand_converter import GTOToHandConverter
    from backend.core.session_logger import SessionLogger
    from backend.core.gui_models import THEME, FONTS
    from backend.utils.sound_manager import SoundManager
except ImportError as e:
    print(f"Import warning: {e}. Using fallbacks.")
    # Fallback definitions if imports fail
    class Hand:
        def __init__(self, **kwargs):
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
        "body": ("Arial", 10),
        "small": ("Arial", 8)
    }


class HandsReviewState(Enum):
    """States for the hands review session."""
    IDLE = "idle"
    HAND_LOADED = "hand_loaded"
    REPLAYING = "replaying"
    COMPLETED = "completed"


@dataclass
class ReplaySession:
    """Lightweight session for hand replay."""
    hand: Hand
    decision_engine: HandModelDecisionEngine
    current_state: HandsReviewState = HandsReviewState.IDLE
    current_action_index: int = 0
    total_actions: int = 0
    pot: float = 0.0
    
    def __post_init__(self):
        self.total_actions = len(getattr(self.hand, 'actions', []))
    
    def start(self) -> bool:
        """Start the replay session."""
        try:
            self.decision_engine.reset()
            self.current_action_index = 0
            self.current_state = HandsReviewState.HAND_LOADED
            return True
        except Exception as e:
            print(f"Failed to start replay session: {e}")
            return False
    
    def next_action(self) -> tuple[bool, str]:
        """Execute next action in the replay."""
        if self.current_state == HandsReviewState.COMPLETED:
            return False, "Hand already completed"
        
        if self.current_action_index >= self.total_actions:
            self.current_state = HandsReviewState.COMPLETED
            return False, "All actions completed"
        
        try:
            # Get next action from decision engine
            action_type, amount, explanation = self.decision_engine.get_decision("", {})
            self.current_action_index += 1
            
            if self.current_action_index >= self.total_actions:
                self.current_state = HandsReviewState.COMPLETED
            else:
                self.current_state = HandsReviewState.REPLAYING
            
            return True, explanation
        except Exception as e:
            print(f"Failed to execute next action: {e}")
            return False, f"Error: {e}"
    
    def reset(self):
        """Reset to beginning of hand."""
        self.decision_engine.reset()
        self.current_action_index = 0
        self.current_state = HandsReviewState.HAND_LOADED
    
    def is_complete(self) -> bool:
        """Check if replay is complete."""
        return self.current_state == HandsReviewState.COMPLETED


class UnifiedHandsReviewPanel(ttk.Frame):
    """
    Unified Hands Review Panel with conversion caching and robust fallbacks.
    
    This panel provides:
    - Hand loading from multiple JSON formats
    - SHA-256 conversion caching to prevent repeated processing
    - Player ID normalization for robust matching
    - Lightweight replay session management
    - Fallback UI if full session/widget stack is missing
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
        self.current_session: Optional[ReplaySession] = None
        
        # UI components
        self.hands_listbox: Optional[tk.Listbox] = None
        self.poker_table_frame: Optional[ttk.Frame] = None
        self.controls_frame: Optional[ttk.Frame] = None
        self.info_label: Optional[ttk.Label] = None
        
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
            font=FONTS["body"],
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
        
        # Poker table area
        self.poker_table_frame = ttk.LabelFrame(right_frame, text="Poker Table", style="Card.TLabelframe")
        self.poker_table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        # Initially show placeholder
        self.placeholder_label = ttk.Label(
            self.poker_table_frame,
            text="Select a hand from the left panel to begin review",
            font=FONTS["header"],
            foreground=THEME["text"]
        )
        self.placeholder_label.pack(expand=True)
        
        # Controls area
        self._create_controls_panel(right_frame)
        
        # Info area
        self.info_label = ttk.Label(
            right_frame,
            text="Ready to load hand",
            font=FONTS["body"],
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
        
        # Control buttons
        self.reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self._reset_hand,
            state="disabled",
            style="Secondary.TButton"
        )
        self.reset_button.pack(side="left", padx=5)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next",
            command=self._next_action,
            state="disabled",
            style="Primary.TButton"
        )
        self.next_button.pack(side="left", padx=5)
        
        self.auto_play_button = ttk.Button(
            button_frame,
            text="Auto Play",
            command=self._auto_play,
            state="disabled",
            style="Secondary.TButton"
        )
        self.auto_play_button.pack(side="left", padx=5)
        
        # Action display
        self.action_display = tk.Text(
            self.controls_frame,
            height=4,
            bg=THEME["widget_bg"],
            fg=THEME["text"],
            font=FONTS["small"],
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
            # Try GTOToHandConverter first
            converted_hand = GTOToHandConverter.convert_gto_hand(raw_data)
            
            # Normalize player IDs
            if hasattr(converted_hand, 'actions'):
                for action in converted_hand.actions:
                    if hasattr(action, 'player_id'):
                        action.player_id = self._normalize_player_id(action.player_id)
            
            self._conversion_cache[cache_key] = converted_hand
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW", "Hand converted and cached")
            return converted_hand
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Conversion failed: {e}")
            # Return fallback Hand object
            return Hand(actions=[], metadata={})
    
    def _normalize_player_id(self, player_id: str) -> str:
        """Normalize player ID format (e.g., 'Player 1' -> 'Player1')."""
        return player_id.replace(' ', '')
    
    def _load_selected_hand(self):
        """Load the selected hand for review."""
        if not self.hands_listbox or not self.hands_listbox.curselection():
            messagebox.showwarning("No Selection", "Please select a hand from the list")
            return
        
        self.selected_hand_index = self.hands_listbox.curselection()[0]
        selected_hand = self.available_hands[self.selected_hand_index]
        
        self.session_logger.log_system("INFO", "HANDS_REVIEW", f"Loading hand: {selected_hand['display_name']}")
        
        try:
            # Convert to Hand model with caching
            hand = self._convert_with_cache(selected_hand['raw_data'])
            
            # Create decision engine
            decision_engine = HandModelDecisionEngine(hand)
            
            # Create replay session
            self.current_session = ReplaySession(hand, decision_engine)
            
            # Start the session
            if self.current_session.start():
                self._enable_controls()
                self._update_poker_display()
                self.info_label.config(text=f"Hand loaded: {selected_hand['display_name']}")
                self._display_action("Hand loaded successfully. Click Next to begin replay.")
                
                if self.sound_manager:
                    self.sound_manager.play_sound("chip_stack")
                    
            else:
                self.info_label.config(text="Failed to load hand")
                self._display_action("Failed to start replay session.")
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW", f"Failed to load hand: {e}")
            self.info_label.config(text=f"Error loading hand: {e}")
            self._display_action(f"Error: {e}")
    
    def _update_poker_display(self):
        """Update the poker table display."""
        if not self.current_session:
            return
            
        # Hide placeholder
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.pack_forget()
        
        # For now, show simple hand info
        # TODO: Integrate with full poker table widget when available
        info_text = f"Hand with {len(getattr(self.current_session.hand, 'actions', []))} actions loaded"
        
        if not hasattr(self, 'simple_display'):
            self.simple_display = ttk.Label(
                self.poker_table_frame,
                text=info_text,
                font=FONTS["body"]
            )
            self.simple_display.pack(expand=True)
        else:
            self.simple_display.config(text=info_text)
    
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
        """Execute the next action in the replay."""
        if not self.current_session:
            return
        
        success, explanation = self.current_session.next_action()
        
        if success:
            self._display_action(f"Action {self.current_session.current_action_index}: {explanation}")
            self._update_poker_display()
            
            if self.sound_manager:
                self.sound_manager.play_sound("button_click")
        else:
            self._display_action(explanation)
            if self.current_session.is_complete():
                self.info_label.config(text="Hand replay completed")
                self._disable_controls()
    
    def _reset_hand(self):
        """Reset the hand to the beginning."""
        if not self.current_session:
            return
        
        self.current_session.reset()
        self._enable_controls()
        self._update_poker_display()
        self.info_label.config(text="Hand reset to beginning")
        self._display_action("Hand reset. Click Next to begin replay.")
        
        if self.sound_manager:
            self.sound_manager.play_sound("chip_stack")
    
    def _auto_play(self):
        """Auto-play through remaining actions."""
        if not self.current_session:
            return
        
        actions_played = 0
        while not self.current_session.is_complete() and actions_played < 50:  # Safety limit
            success, explanation = self.current_session.next_action()
            if not success:
                break
            actions_played += 1
        
        self._update_poker_display()
        self.info_label.config(text=f"Auto-played {actions_played} actions")
        self._display_action(f"Auto-play completed. {actions_played} actions executed.")
        
        if self.current_session.is_complete():
            self._disable_controls()
    
    def _display_action(self, message: str):
        """Display an action message in the action display."""
        if not self.action_display:
            return
            
        self.action_display.config(state="normal")
        self.action_display.insert(tk.END, f"{message}\n")
        self.action_display.see(tk.END)
        self.action_display.config(state="disabled")
    
    def update_font_size(self, base_size: int):
        """Update font sizes based on global setting."""
        # Update fonts if needed
        pass


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
