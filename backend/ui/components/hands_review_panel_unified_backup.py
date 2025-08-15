"""
Unified Hands Review Panel using bot session architecture.

This panel allows users to review pre-recorded poker hands,
navigate through actions, and add/view comments for learning.
"""

import tkinter as tk
from tkinter import ttk
import os
import json
import glob
import re
from typing import Dict, List, Optional

from core.gui_models import THEME, FONTS
from utils.sound_manager import SoundManager
from core.bot_session_state_machine import HandsReviewBotSession
from ui.components.bot_session_widget import HandsReviewSessionWidget
from core.decision_engine_v2 import PreloadedDecisionEngine
from core.hand_model_decision_engine import HandModelDecisionEngine
from core.gto_to_hand_converter import GTOToHandConverter
from core.hand_model import Hand
from core.session_logger import SessionLogger


class UnifiedHandsReviewPanel(ttk.Frame):
    """
    Unified Hands Review panel using bot session architecture.

    This panel allows users to review pre-recorded poker hands,
    navigate through actions, and add/view comments for learning.
    """

    def __init__(self, master, session_logger: SessionLogger = None):
        super().__init__(master, style="DarkFrame.TFrame")
        self.session_logger = session_logger or SessionLogger()
        self.available_hands: List[Dict] = []
        self.current_hand_index = -1
        self.current_hand_id: Optional[str] = None
        self.hands_review_session: Optional[HandsReviewBotSession] = None
        self.hands_review_widget: Optional[HandsReviewSessionWidget] = None
        self.sound_manager = SoundManager()
        self.session_active = False
        self.auto_play_job = None

        self._setup_styles()
        self._setup_ui()
        self._load_initial_hands()

    def _setup_styles(self):
        """Configure ttk styles for this panel."""
        s = ttk.Style()
        s.configure("DarkFrame.TFrame", background=THEME["primary_bg"])
        s.configure("DarkLabel.TLabel", background=THEME["primary_bg"], foreground=THEME["text"])
        s.configure("DarkButton.TButton", background=THEME["button_call"], foreground=THEME["text"])
        s.map("DarkButton.TButton",
            background=[('active', THEME["button_call_hover"])],
            foreground=[('active', THEME["text"])])
        s.configure("TCombobox", fieldbackground=THEME["widget_bg"], background=THEME["button_call"],
                    foreground=THEME["text"], selectbackground=THEME["accent_primary"],
                    selectforeground=THEME["text_dark"])
        s.configure("TListbox", background=THEME["widget_bg"], foreground=THEME["text"],
                    selectbackground=THEME["accent_primary"], selectforeground=THEME["text_dark"])
        s.configure("TText", background=THEME["widget_bg"], foreground=THEME["text"],
                    insertbackground=THEME["text"]) # Cursor color

    def _setup_ui(self):
        """Set up the hands review UI: 30% left (hands), 50% top-right (table), 20% bottom-right (comments)."""
        self.grid_rowconfigure(0, weight=1) # Main content area
        self.grid_columnconfigure(0, weight=3) # Left: Hand Selection (30%)
        self.grid_columnconfigure(1, weight=7) # Right: Poker Table + Comments (70%)

        # Left Panel: Hand Selection
        self.left_panel = ttk.Frame(self, style="DarkFrame.TFrame")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_rowconfigure(0, weight=0) # Title
        self.left_panel.grid_rowconfigure(1, weight=1) # Listbox
        self.left_panel.grid_rowconfigure(2, weight=0) # Load button
        self.left_panel.grid_columnconfigure(0, weight=1)

        ttk.Label(self.left_panel, text="Available Hands", font=FONTS["header"], style="DarkLabel.TLabel").grid(row=0, column=0, pady=(0, 5))
        
        self.hand_listbox = tk.Listbox(
            self.left_panel,
            font=FONTS["small"],
            selectmode=tk.SINGLE,
            exportselection=False,
            height=10, # Initial height, will expand
            background=THEME["widget_bg"],
            foreground=THEME["text"],
            selectbackground=THEME["accent_primary"],
            selectforeground=THEME["text_dark"],
            borderwidth=0,
            highlightthickness=0 # Remove default border
        )
        self.hand_listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.hand_listbox.bind("<<ListboxSelect>>", self._on_hand_selected)

        # Add Load Hands button for manual loading
        self.load_hands_button = ttk.Button(
            self.left_panel,
            text="🔄 Load Hands",
            command=self._manual_load_hands,
            style="Primary.TButton"
        )
        self.load_hands_button.grid(row=2, column=0, pady=(5, 0), sticky="ew")

        self.load_hand_button = ttk.Button(
            self.left_panel,
            text="Load Selected Hand",
            command=self._load_selected_hand,
            style="Primary.TButton",
            state=tk.DISABLED
        )
        self.load_hand_button.grid(row=3, column=0, pady=(5, 0), sticky="ew")

        # Right Side: Combined Poker Table + Comments (70% total)
        self.right_side = ttk.Frame(self, style="DarkFrame.TFrame")
        self.right_side.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.right_side.grid_rowconfigure(0, weight=5) # Top: Poker Table (50% of total / 70% = 5/7)
        self.right_side.grid_rowconfigure(1, weight=2) # Bottom: Comments (20% of total / 70% = 2/7)
        self.right_side.grid_columnconfigure(0, weight=1)

        # Top-Right Panel: Poker Table (50% of total space)
        self.poker_panel = ttk.Frame(self.right_side, style="DarkFrame.TFrame")
        self.poker_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 2))
        self.poker_panel.grid_rowconfigure(0, weight=1)
        self.poker_panel.grid_columnconfigure(0, weight=1)

        self.placeholder_label = ttk.Label(
            self.poker_panel,
            text="Select a hand from the left to begin review",
            font=FONTS["large"],
            background=THEME["primary_bg"],
            foreground=THEME["text_secondary"]
        )
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")

        # Bottom-Right Panel: Comments and Controls (20% of total space)
        self.comments_panel = ttk.Frame(self.right_side, style="DarkFrame.TFrame")
        self.comments_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=(2, 5))
        self.comments_panel.grid_rowconfigure(0, weight=0) # Hand Comments Title
        self.comments_panel.grid_rowconfigure(1, weight=1) # Hand Comments Text
        self.comments_panel.grid_rowconfigure(2, weight=0) # Street Comments Title
        self.comments_panel.grid_rowconfigure(3, weight=1) # Street Comments Text
        self.comments_panel.grid_rowconfigure(4, weight=0) # Navigation Buttons
        self.comments_panel.grid_columnconfigure(0, weight=1)

        ttk.Label(self.comments_panel, text="Hand Comments", font=FONTS["header"], style="DarkLabel.TLabel").grid(row=0, column=0, pady=(0, 5))
        self.hand_comments_text = tk.Text(
            self.comments_panel,
            wrap=tk.WORD,
            height=3,  # Reduced height for smaller space
            font=FONTS["small"],
            background=THEME["widget_bg"],
            foreground=THEME["text"],
            insertbackground=THEME["text"]
        )
        self.hand_comments_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(self.comments_panel, text="Street Comments", font=FONTS["header"], style="DarkLabel.TLabel").grid(row=2, column=0, pady=(5, 5))
        self.street_comments_text = tk.Text(
            self.comments_panel,
            wrap=tk.WORD,
            height=3,  # Reduced height for smaller space
            font=FONTS["small"],
            background=THEME["widget_bg"],
            foreground=THEME["text"],
            insertbackground=THEME["text"]
        )
        self.street_comments_text.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        # Navigation Buttons
        nav_button_frame = ttk.Frame(self.comments_panel, style="DarkFrame.TFrame")
        nav_button_frame.grid(row=4, column=0, pady=(10, 0))
        nav_button_frame.grid_columnconfigure(0, weight=1)
        nav_button_frame.grid_columnconfigure(1, weight=1)
        nav_button_frame.grid_columnconfigure(2, weight=1)

        self.reset_button = ttk.Button(
            nav_button_frame,
            text="Reset",
            command=self._reset_hand,
            style="Primary.TButton",
            state=tk.DISABLED
        )
        self.reset_button.grid(row=0, column=0, padx=2)

        self.next_button = ttk.Button(
            nav_button_frame,
            text="Next",
            command=self._next_action,
            style="Primary.TButton",
            state=tk.DISABLED
        )
        self.next_button.grid(row=0, column=1, padx=2)

        self.auto_play_button = ttk.Button(
            nav_button_frame,
            text="Auto Play",
            command=self._auto_play,
            style="Primary.TButton",
            state=tk.DISABLED
        )
        self.auto_play_button.grid(row=0, column=2, padx=2)

    def _manual_load_hands(self):
        """Manually trigger hands loading for debugging."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Manual hands loading triggered")
        
        # Clear existing hands
        self.available_hands = []
        self.hand_listbox.delete(0, tk.END)
        
        # Load hands
        success = self._load_gto_hands()
        
        if success:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"✅ Manual load successful: {len(self.available_hands)} hands")
            self._refresh_hands_list()
        else:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", "❌ Manual load failed")
            self.hand_listbox.insert(tk.END, "❌ Failed to load hands - check data files")

    def _load_initial_hands(self):
        """Load initial hands data including GTO generated hands."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Starting initial hands loading")
        
        try:
            # First try to load GTO generated hands from logs
            gto_hands_loaded = self._load_gto_hands()
            
            # If no GTO hands, look for other hands in common locations
            if not gto_hands_loaded:
                hands_files = [
                    "backend/data/hands.json",
                    "backend/data/clean_poker_hands.json", 
                    "data/hands.json",
                    "hands.json"
                ]
                
                for file_path in hands_files:
                    if os.path.exists(file_path):
                        self._load_hands_from_file(file_path)
                        return
                
                # No hands found, show empty state
                self.hand_listbox.insert(tk.END, "No hands found - click 'Load Hands' to import")
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error loading initial hands: {e}")
            self.hand_listbox.insert(tk.END, "Error loading hands - click 'Load Hands' to try again")

    def _load_gto_hands(self) -> bool:
        """Load GTO generated hands from data directory."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🔄 _load_gto_hands() method called")
        
        try:
            import os
            import json
            current_dir = os.getcwd()
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"🔍 Current working directory: {current_dir}")
            
            # Use absolute paths to ensure we find the files
            gto_data_files = [
                "/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json",
                "/Users/yeogirlyun/Python/Poker/data/clean_gto_sessions_generated.json"
            ]
            
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"🔍 Attempting to load from {len(gto_data_files)} file paths")
            
            # Quick file existence check first
            for file_path in gto_data_files:
                exists = os.path.exists(file_path)
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📁 {file_path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
                if exists:
                    size = os.path.getsize(file_path)
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📏 File size: {size} bytes")
            
            all_hands = []
            total_loaded = 0
            
            for file_path in gto_data_files:
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"🔍 Processing file: {file_path}")
                if not os.path.exists(file_path):
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"⏭️  Skipping non-existent file: {file_path}")
                    continue
                
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📖 Opening file: {file_path}")
                    
                try:
                    with open(file_path, 'r') as f:
                        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📄 Reading JSON from: {file_path}")
                        data = json.load(f)
                    
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📄 Loaded JSON data from {file_path}")
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📊 JSON keys: {list(data.keys())}")
                    
                    # Handle different data formats
                    hands_data = []
                    if 'hands' in data:
                        # Flat hands format
                        hands_data = data['hands']
                        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📋 Found {len(hands_data)} hands in flat format")
                    elif 'sessions' in data:
                        # Sessions format - extract hands from all sessions
                        for session in data['sessions']:
                            if 'hands' in session:
                                hands_data.extend(session['hands'])
                        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"📋 Found {len(hands_data)} hands in sessions format")
                    else:
                        self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Unknown data format in {file_path}: {list(data.keys())}")
                        continue
                    
                    if hands_data:
                        # Parse and convert GTO hands
                        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"🔄 Parsing {len(hands_data)} hands...")
                        parsed_hands = self._parse_gto_hands(hands_data)
                        all_hands.extend(parsed_hands)
                        total_loaded += len(parsed_hands)
                        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"✅ Loaded {len(parsed_hands)} hands from {file_path}")
                        
                except Exception as e:
                    self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Error loading GTO file {file_path}: {e}")
                    import traceback
                    self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Traceback: {traceback.format_exc()}")
                    continue
            
            if all_hands:
                self.available_hands = all_hands
                self._refresh_hands_list()
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"✅ SUCCESS: Loaded {total_loaded} GTO hands for review")
                return True
            else:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ No hands found in any of the checked files")
                return False
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Fatal error loading GTO hands: {e}")
            import traceback
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Fatal traceback: {traceback.format_exc()}")
            return False

    def _parse_gto_hands(self, gto_hands: List[Dict]) -> List[Dict]:
        """Parse GTO hands and convert to reviewable format."""
        parsed_hands = []
        
        for hand in gto_hands:
            try:
                # Convert GTO hand format to review format
                parsed_hand = self._convert_gto_hand_format(hand)
                if parsed_hand:
                    parsed_hands.append(parsed_hand)
            except Exception as e:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error parsing GTO hand: {e}")
                continue
        
        return parsed_hands

    def _convert_gto_hand_format(self, gto_hand: Dict) -> Optional[Dict]:
        """Convert a single GTO hand to review format using robust Hand Model converter."""
        
        # Cache to prevent repeated conversions of the same hand
        hand_id = gto_hand.get('id', 'unknown')
        if not hasattr(self, '_conversion_cache'):
            self._conversion_cache = {}
        
        if hand_id in self._conversion_cache:
            return self._conversion_cache[hand_id]
        
        try:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"🔄 Converting GTO hand: {list(gto_hand.keys())}")
            
            # Use the robust GTOToHandConverter that includes player ID normalization
            hand_model = GTOToHandConverter.convert_gto_hand(gto_hand)
            
            # Store the Hand Model object for use by HandModelDecisionEngine
            hand_dict = {
                'hand_model': hand_model,  # Store the actual Hand object
                'hand_id': hand_model.metadata.hand_id,
                'id': hand_model.metadata.hand_id,  # For UI compatibility
                'timestamp': hand_model.metadata.hand_id,  # Use hand_id as timestamp for now
                'source': 'GTO Generated (Hand Model)',
                'comments': '',
                'street_comments': {
                    'preflop': '',
                    'flop': '',
                    'turn': '',
                    'river': '',
                    'overall': ''
                }
            }
            
            # Calculate total actions for display
            total_actions = sum(len(street_state.actions) for street_state in hand_model.streets.values())
            
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", 
                f"✅ Converted hand {hand_model.metadata.hand_id} with {total_actions} actions using Hand Model")
            
            # Cache the result
            self._conversion_cache[hand_id] = hand_dict
            
            return hand_dict
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Hand Model conversion failed: {e}")
            import traceback
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Conversion traceback: {traceback.format_exc()}")
            
            # Fallback to legacy conversion for backwards compatibility
            return self._convert_gto_hand_format_legacy(gto_hand)

    def _convert_gto_hand_format_legacy(self, gto_hand: Dict) -> Optional[Dict]:
        """Legacy GTO hand conversion (fallback)."""
        try:
            # Extract basic info
            hand_id = gto_hand.get('id', 'Unknown')
            timestamp = gto_hand.get('timestamp', '')
            
            # Parse players from clean data format
            initial_state = gto_hand.get('initial_state', {})
            players_data = initial_state.get('players', [])
            
            # Parse players
            parsed_players = []
            for player_data in players_data:
                if isinstance(player_data, dict):
                    player_info = {
                        'name': player_data.get('name', 'Unknown'),
                        'stack': player_data.get('stack', 1000.0),
                        'position': player_data.get('position', 'UTG'),
                        'is_human': False,
                        'is_active': player_data.get('is_active', True),
                        'cards': player_data.get('hole_cards', []),
                        'current_bet': player_data.get('current_bet', 0.0)
                    }
                    parsed_players.append(player_info)
                elif isinstance(player_data, str):
                    player_info = self._parse_player_string(player_data)
                    if player_info:
                        parsed_players.append(player_info)
            
            if not parsed_players:
                return None
            
            # Get actions
            raw_actions = gto_hand.get('actions', [])
            flat_actions = []
            
            for action in raw_actions:
                flat_action = {
                    'street': action.get('street', 'preflop'),
                    'player_index': action.get('player_index', 0),
                    'action': action.get('action', 'fold'),
                    'amount': action.get('amount', 0.0),
                    'explanation': action.get('explanation', f"GTO {action.get('action', 'fold')}"),
                    'pot_after': action.get('pot_after', 0.0)
                }
                flat_actions.append(flat_action)
            
            # Legacy format
            return {
                'hand_id': hand_id,
                'timestamp': timestamp,
                'source': 'GTO Generated (Legacy)',
                'initial_state': {
                    'players': parsed_players,
                    'dealer_position': gto_hand.get('dealer_position', 0),
                    'pot': gto_hand.get('pot', 0),
                    'street': 'preflop'
                },
                'actions': flat_actions,
                'final_state': gto_hand.get('final_state', {}),
                'board_progression': gto_hand.get('board_progression', {}),
                'comments': '',
                'street_comments': {
                    'preflop': '', 'flop': '', 'turn': '', 'river': '', 'overall': ''
                }
            }
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"❌ Legacy conversion failed: {e}")
            return None

    def _parse_player_string(self, player_str: str) -> Optional[Dict]:
        """Parse a Player() string representation to extract data."""
        try:
            # Example: "Player(name='Player 1', stack=985, position='MP', is_human=False, is_active=True, cards=['Kh', 'Kd'], ...)"
            
            # Extract key information using string parsing
            # Extract name
            name_match = re.search(r"name='([^']*)'", player_str)
            name = name_match.group(1) if name_match else "Unknown"
            
            # Extract stack
            stack_match = re.search(r"stack=([0-9.]+)", player_str)
            stack = float(stack_match.group(1)) if stack_match else 1000.0
            
            # Extract position
            position_match = re.search(r"position='([^']*)'", player_str)
            position = position_match.group(1) if position_match else "UTG"
            
            # Extract cards
            cards_match = re.search(r"cards=\[([^\]]*)\]", player_str)
            cards = ['**', '**']
            if cards_match:
                cards_str = cards_match.group(1)
                # Extract individual cards
                card_matches = re.findall(r"'([^']*)'", cards_str)
                if len(card_matches) >= 2:
                    cards = [card_matches[0], card_matches[1]]
            
            # Extract current_bet
            bet_match = re.search(r"current_bet=([0-9.]+)", player_str)
            current_bet = float(bet_match.group(1)) if bet_match else 0.0
            
            # Extract is_active
            active_match = re.search(r"is_active=([TrueFalse]+)", player_str)
            is_active = active_match and active_match.group(1) == "True"
            
            # Extract has_folded
            folded_match = re.search(r"has_folded=([TrueFalse]+)", player_str)
            has_folded = folded_match and folded_match.group(1) == "True"
            
            return {
                'name': name,
                'stack': stack,
                'position': position,
                'cards': cards,
                'current_bet': current_bet,
                'is_active': is_active,
                'has_folded': has_folded,
                'is_human': False  # All GTO hands are bot vs bot
            }
            
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error parsing player string: {e}")
            return None

    def _refresh_hands_list(self):
        """Refresh the hands listbox with available hands."""
        # Clear existing items
        self.hand_listbox.delete(0, tk.END)
        
        # Add all available hands
        for i, hand in enumerate(self.available_hands):
            # Format hand display
            display_text = self._format_hand_display(hand, i)
            self.hand_listbox.insert(tk.END, display_text)

    def _format_hand_display(self, hand: Dict, index: int) -> str:
        """Format hand for display in list."""
        try:
            # Try to extract meaningful info
            hand_id = hand.get('id', hand.get('hand_id', f"Hand #{index + 1}"))  # Check both 'id' and 'hand_id'
            source = hand.get('source', 'GTO Session')
            
            # Try to get player info
            if 'initial_state' in hand and 'players' in hand['initial_state']:
                players = hand['initial_state']['players']
                num_players = len(players)
                pot = hand['initial_state'].get('pot', 0)
                
                # For GTO hands, show interesting cards/actions
                premium_hands = []
                action_summary = ""
                
                # Look for premium hands
                for player in players:
                    if isinstance(player, dict):
                        cards = player.get('cards', ['**', '**'])
                        if cards and cards != ['**', '**']:
                            # Check for premium hands
                            card_str = f"{cards[0]}{cards[1]}"
                            position = player.get('position', 'Unknown')
                            
                            # Identify premium combinations
                            ranks = [card[0] for card in cards]
                            suits = [card[1] for card in cards]
                            
                            is_pair = ranks[0] == ranks[1]
                            is_suited = suits[0] == suits[1]
                            is_premium = (
                                is_pair and ranks[0] in ['A', 'K', 'Q', 'J'] or
                                'A' in ranks and 'K' in ranks or
                                'A' in ranks and 'Q' in ranks and is_suited
                            )
                            
                            if is_premium:
                                premium_hands.append(f"{position}:{card_str}")
                
                # Get action count if available
                actions = hand.get('actions', [])
                if actions:
                    action_summary = f" - {len(actions)} actions"
                
                # Format display
                premium_str = ""
                if premium_hands:
                    premium_str = f" [{', '.join(premium_hands[:2])}]"  # Show first 2 premium hands
                
                if source == 'GTO Generated':
                    return f"🤖 {hand_id} ({num_players}P, ${pot}{premium_str}{action_summary})"
                else:
                    return f"🎯 {hand_id} ({num_players}P, ${pot}{premium_str}{action_summary})"
            else:
                return f"📄 {hand_id}"
                
        except Exception as e:
            return f"Hand #{index + 1} (Error: {str(e)[:20]})"

    def _on_hand_selected(self, event):
        """Handle selection of a hand in the listbox."""
        selection = self.hand_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_hand_index = index
            if index < len(self.available_hands):
                hand = self.available_hands[index]
                self.current_hand_id = hand.get('hand_id', 'Unknown')
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"Selected hand: {self.current_hand_id}")
                self.load_hand_button.config(state=tk.NORMAL)
            else:
                self.current_hand_index = -1
                self.load_hand_button.config(state=tk.DISABLED)
        else:
            self.current_hand_index = -1
            self.current_hand_id = None
            self.load_hand_button.config(state=tk.DISABLED)

    def _load_selected_hand(self):
        """Load the selected hand into the review session."""
        if self.current_hand_index < 0 or self.current_hand_index >= len(self.available_hands):
            self.session_logger.log_system("WARNING", "HANDS_REVIEW_PANEL", "No valid hand selected to load.")
            return

        hand_to_review = self.available_hands[self.current_hand_index]
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"Loading hand {self.current_hand_id} for review.")

        try:
            # Stop any existing session
            if self.session_active:
                self._stop_session()

            # Use HandModelDecisionEngine if Hand Model available, otherwise fallback to PreloadedDecisionEngine
            if 'hand_model' in hand_to_review and isinstance(hand_to_review['hand_model'], Hand):
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🚀 Using HandModelDecisionEngine (robust)")
                decision_engine = HandModelDecisionEngine(hand_to_review['hand_model'])
            else:
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "⚠️ Using PreloadedDecisionEngine (legacy fallback)")
                decision_engine = PreloadedDecisionEngine(hand_to_review)

            # Create config from hand data  
            if 'hand_model' in hand_to_review:
                # Hand Model format - get player count from seats
                num_players = len(hand_to_review['hand_model'].seats)
            else:
                # Legacy format
                players_data = hand_to_review.get('initial_state', {}).get('players', [])
                num_players = len(players_data)
            config = {
                'num_players': num_players,
                'starting_stack': 1000,
                'small_blind': 5,
                'big_blind': 10
            }

            # Initialize HandsReviewBotSession
            from core.flexible_poker_state_machine import GameConfig
            game_config = GameConfig(
                num_players=config['num_players'],
                starting_stack=config['starting_stack'],
                small_blind=config['small_blind'],
                big_blind=config['big_blind']
            )
            self.hands_review_session = HandsReviewBotSession(
                config=game_config,
                decision_engine=decision_engine
            )
            self.hands_review_session.set_sound_manager(self.sound_manager)
            
            # CRITICAL: Set the preloaded hand data so the session can load the correct cards
            self.hands_review_session.set_preloaded_hand_data(hand_to_review)
            
            # Create and display the HandsReviewSessionWidget FIRST (like GTO session)
            if self.hands_review_widget:
                self.hands_review_widget.destroy()
            
            # Hide placeholder
            self.placeholder_label.grid_remove()
            
            # Import the correct widget class
            from ui.components.bot_session_widget import HandsReviewSessionWidget
            self.hands_review_widget = HandsReviewSessionWidget(
                self.poker_panel,
                self.hands_review_session,
                logger=self.session_logger
            )
            self.hands_review_widget.grid(row=0, column=0, sticky="nsew")
            
            # Load the hand data into the widget
            self.hands_review_widget.load_hand(hand_to_review)
            
            # Start the session (like GTO session) - this will start the hand and initialize display
            success = self.hands_review_session.start_session()
            if success:
                self.session_active = True
                self._update_button_states()
                self.current_hand_index = 0 # Start at the beginning of the hand's actions
                
                # Enable the widget controls
                self.hands_review_widget.enable_controls()
                
                # Update poker widget to show initial state
                if hasattr(self, 'hands_review_widget'):
                    self.hands_review_widget._update_display()
                    # Defer one more update for proper layout
                    try:
                        self.after(150, self.hands_review_widget._update_display)
                    except Exception:
                        pass
            else:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", "Failed to start hands review session")
            
            # Load hand comments
            hand_comments = hand_to_review.get('comments', 'No overall hand comments.')
            self.hand_comments_text.delete(1.0, tk.END)
            self.hand_comments_text.insert(tk.END, hand_comments)
            
            # Clear street comments initially
            self.street_comments_text.delete(1.0, tk.END)

            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"Hand {self.current_hand_id} loaded successfully.")

        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to load hand {self.current_hand_id}: {e}")
            self.session_active = False
            self._update_button_states()
            if self.hands_review_widget:
                self.hands_review_widget.destroy()
                self.hands_review_widget = None
            self.placeholder_label.grid(row=0, column=0, sticky="nsew") # Show placeholder on error

    def _stop_session(self):
        """Stop the current review session."""
        if self.auto_play_job:
            self.after_cancel(self.auto_play_job)
            self.auto_play_job = None
        
        self.session_active = False
        self._update_button_states()
        
        if self.hands_review_session:
            self.hands_review_session.reset_session()
        
        if self.hands_review_widget:
            self.hands_review_widget.destroy()
            self.hands_review_widget = None
        
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")

    def _next_action(self):
        """Execute the next action in the hands review session using unified bot architecture."""
        print("🔥 NEXT_DEBUG: _next_action called!")
        
        if not self.session_active or not self.hands_review_session:
            print("🔥 NEXT_DEBUG: No active session!")
            return

        if not hasattr(self, 'hands_review_widget') or not self.hands_review_widget:
            print("🔥 NEXT_DEBUG: No hands review widget!")
            return

        try:
            print("🔥 NEXT_DEBUG: Calling hands_review_widget.execute_next_action()...")
            # Execute next bot action using the widget (exactly like GTO session)
            success = self.hands_review_widget.execute_next_action()
            print(f"🔥 NEXT_DEBUG: execute_next_action returned: {success}")
            
            if success:
                print("🔥 NEXT_DEBUG: Action executed successfully!")
                # Get the decision explanation from the bot session
                explanation = self.hands_review_session.get_current_explanation()
                if explanation:
                    print(f"🔥 NEXT_DEBUG: Got explanation: {explanation}")
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"Action executed with explanation: {explanation}")
                
                # Update poker widget to show the action result (exactly like GTO session)
                if hasattr(self, 'hands_review_widget'):
                    print("🔥 NEXT_DEBUG: Updating display...")
                    self.hands_review_widget._update_display()
                
                # Update street comments based on current street
                current_street = self.hands_review_session.game_state.street
                hand_data = self.available_hands[self.current_hand_index]
                street_comments = hand_data.get("street_comments", {}).get(current_street, "No comments for this street.")
                self.street_comments_text.delete(1.0, tk.END)
                self.street_comments_text.insert(tk.END, street_comments)

                # Check if session is now complete (like GTO session)
                if self.hands_review_session.decision_engine.is_session_complete():
                    print("🔥 NEXT_DEBUG: Session complete!")
                    self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Hands review complete!")
                    self.session_active = False
                    self._update_button_states()
                    
            else:
                print("🔥 NEXT_DEBUG: No action executed - session may be complete")
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "No more actions in this hand or hand complete.")
                self.session_active = False
                self._update_button_states()

        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error during next action: {e}")
            self.session_active = False
            self._update_button_states()

    def _reset_hand(self):
        """Reset the hand to the beginning."""
        if not self.session_active or not self.hands_review_session:
            return
            
        try:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Resetting hand to beginning.")
            
            # Stop auto-play if running
            if self.auto_play_job:
                self.after_cancel(self.auto_play_job)
                self.auto_play_job = None
            
            # Reload the same hand from scratch
            if self.current_hand_index >= 0 and self.current_hand_index < len(self.available_hands):
                self._load_selected_hand()
                
        except Exception as e:
            self.session_logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error resetting hand: {e}")

    def _auto_play(self):
        """Toggle auto-play for the hands review."""
        if self.auto_play_job:
            self.after_cancel(self.auto_play_job)
            self.auto_play_job = None
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Auto-play stopped.")
            self._update_button_states()
        else:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Auto-play started.")
            self._run_auto_play_step()
            self._update_button_states()

    def _run_auto_play_step(self):
        """Execute a single step in auto-play mode."""
        if self.session_active and self.hands_review_session:
            self._next_action()
            if self.session_active: # Continue if hand is not complete
                self.auto_play_job = self.after(1000, self._run_auto_play_step) # 1 second delay
            else:
                self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Auto-play finished: Hand complete.")
                self.auto_play_job = None
                self._update_button_states()
        else:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Auto-play stopped: Session inactive.")
            self.auto_play_job = None
            self._update_button_states()

    def _update_button_states(self):
        """Update the state of navigation buttons based on session activity."""
        is_active = self.session_active and self.hands_review_session is not None
        
        self.load_hand_button.config(state=tk.NORMAL if not is_active and self.current_hand_index >= 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if is_active else tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL if is_active else tk.DISABLED)
        self.auto_play_button.config(state=tk.NORMAL if is_active else tk.DISABLED)

        if self.auto_play_job:
            self.auto_play_button.config(text="Stop Auto Play")
        else:
            self.auto_play_button.config(text="Auto Play")

    def update_font_size(self, base_size: int = 10):
        """Update font sizes throughout the panel.
        
        Args:
            base_size: Base font size for calculations
        """
        # Re-apply styles to update fonts
        self._setup_styles()
        # Update specific widgets that don't use styles directly or need explicit font updates
        self.placeholder_label.config(font=FONTS["large"])
        self.hand_listbox.config(font=FONTS["small"])
        self.hand_comments_text.config(font=FONTS["small"])
        self.street_comments_text.config(font=FONTS["small"])
        # If poker widget exists, update its font size
        if self.hands_review_widget:
            self.hands_review_widget.update_font_size(base_size)

    def on_tab_focus(self):
        """Called when the hands review tab gains focus."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Hands Review tab focused.")
        self._load_initial_hands() # Reload hands to ensure up-to-date list
        self._update_button_states()

    def on_tab_unfocus(self):
        """Called when the hands review tab loses focus."""
        self.session_logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Hands Review tab unfocused.")
        if self.auto_play_job:
            self.after_cancel(self.auto_play_job)
            self.auto_play_job = None
        self._stop_session()