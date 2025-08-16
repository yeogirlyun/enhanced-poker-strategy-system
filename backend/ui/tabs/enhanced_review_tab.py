import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Dict, List, Any, Optional

from ..tabs.base_tab import BaseTab
from ..state.actions import SET_TABLE_DIM, SET_POT, SET_SEATS, SET_BOARD, SET_DEALER
from ..services.theme_manager import ThemeManager
from ..services.hands_repository import HandsRepository
from ..services.fpsm_adapter import FpsmEventAdapter

# Import the rich poker game functionality
from ..components.reusable_poker_game_widget import ReusablePokerGameWidget
from ..components.hands_review_panel_unified_legacy import UnifiedHandsReviewPanel

try:
    from ...core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
    from ...core.bot_session_state_machine import HandsReviewBotSession
    from ...core.hand_model import Hand
    from ...core.hand_model_decision_engine import HandModelDecisionEngine
    from ...core.legendary_to_hand_converter import LegendaryToHandConverter, is_legendary_hand_obj
    from ...core.session_logger import get_session_logger
except ImportError:
    # Fallback imports for different import contexts
    try:
        from backend.core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
        from backend.core.bot_session_state_machine import HandsReviewBotSession
        from backend.core.hand_model import Hand
        from backend.core.hand_model_decision_engine import HandModelDecisionEngine
        from backend.core.legendary_to_hand_converter import LegendaryToHandConverter, is_legendary_hand_obj
        from backend.core.session_logger import get_session_logger
    except ImportError as e:
        print(f"Import warning in enhanced_review_tab: {e}")
        # Fallback classes for when core modules are missing
        FlexiblePokerStateMachine = None
        GameConfig = None
        HandsReviewBotSession = None
        Hand = None
        HandModelDecisionEngine = None
        LegendaryToHandConverter = None
        is_legendary_hand_obj = lambda x: True
        def get_session_logger():
            class FallbackLogger:
                def log_system(self, level, category, message, metadata):
                    print(f"[{level}] {category}: {message}")
            return FallbackLogger()





class EnhancedReviewTab(BaseTab):
    """Enhanced Hands Review tab using new UI architecture with rich poker game functionality."""
    
    def __init__(self, parent, session_id: str, services, store):
        super().__init__(parent, session_id, services, store)
        self.current_hand_data = None
        self.current_session = None
        self.legendary_hands = []
        self.playback_index = 0
        self.is_playing = False
        self.play_speed = 1000  # milliseconds between actions
        self.session_active = False
        
        # Initialize session logger
        try:
            self.session_logger = get_session_logger()
            self.session_logger.log_system("INFO", "ENHANCED_REVIEW", "Enhanced Review Tab initialized", {})
        except Exception as e:
            print(f"⚠️  Could not initialize session logger: {e}")
            self.session_logger = None
        
    def on_mount(self) -> None:
        """Initialize the enhanced review tab."""
        # Two-pane layout: Hand list + Controls | Centered Poker table (25%:75% to ensure poker table dominance)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)  # Hand list + controls (left, ~25%)
        self.grid_columnconfigure(1, weight=8)  # Poker table (right, ~75%)
        
        # Create the two main panels
        self._create_combined_left_panel()
        self._create_poker_table_panel()
        
        # Load legendary hands data
        self._load_legendary_hands()
        
        # Setup theme integration
        theme: ThemeManager = self.services.get_app("theme")
        self._apply_theme_to_components(theme)
        
        # Subscribe to theme changes
        self._unsubs.append(theme.subscribe(self._on_theme_changed))
        
    def _create_combined_left_panel(self):
        """Create the left panel combining hands, controls, and info."""
        # Main left panel container
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=2)  # Hands list takes more space
        left_frame.grid_rowconfigure(1, weight=0)  # Controls compact
        left_frame.grid_rowconfigure(2, weight=1)  # Hand info takes remaining space
        
        # === HANDS SECTION ===
        hands_frame = ttk.LabelFrame(left_frame, text="Legendary Hands", padding=10)
        hands_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        hands_frame.grid_columnconfigure(0, weight=1)
        hands_frame.grid_rowconfigure(1, weight=1)
        
        # Search/filter controls
        search_frame = ttk.Frame(hands_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Filter:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.search_var.trace('w', self._filter_hands)
        
        # Hands listbox
        listbox_frame = ttk.Frame(hands_frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew")
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        
        # Get font from theme manager
        theme: ThemeManager = self.services.get_app("theme")
        listbox_font = theme.get_fonts().get("body", ("Consolas", 20))
        
        self.hands_listbox = tk.Listbox(
            listbox_frame,
            exportselection=False,
            font=listbox_font
        )
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.hands_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection events
        self.hands_listbox.bind("<<ListboxSelect>>", self._on_hand_selected)
        self.hands_listbox.bind("<Double-Button-1>", self._load_selected_hand)
        
        # Load button
        load_btn = ttk.Button(hands_frame, text="Load Hand", command=self._load_selected_hand)
        load_btn.grid(row=2, column=0, pady=(10, 0), sticky="ew")
        
        # === PLAYBACK CONTROLS SECTION ===
        controls_frame = ttk.LabelFrame(left_frame, text="Playback Controls", padding=10)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Playback buttons (left side)
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.next_btn = ttk.Button(btn_frame, text="Next →", command=self._next_action, state="disabled")
        self.next_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        self.play_btn = ttk.Button(btn_frame, text="▶ Auto", command=self._toggle_playback, state="disabled")
        self.play_btn.grid(row=0, column=1, sticky="ew", padx=2)
        
        self.reset_btn = ttk.Button(btn_frame, text="↺ Reset", command=self._reset_hand, state="disabled")
        self.reset_btn.grid(row=0, column=2, sticky="ew", padx=(2, 0))
        
        # Speed control (right side)
        speed_frame = ttk.LabelFrame(controls_frame, text="Speed", padding=5)
        speed_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        speed_frame.grid_columnconfigure(0, weight=1)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.5, to=3.0, variable=self.speed_var, orient="horizontal")
        speed_scale.grid(row=0, column=0, sticky="ew")
        speed_scale.configure(command=self._on_speed_changed)
        
        speed_label = ttk.Label(speed_frame, text="1.0x")
        speed_label.grid(row=1, column=0)
        self.speed_label = speed_label
        
        # === HAND INFO SECTION ===
        info_frame = ttk.LabelFrame(left_frame, text="Hand Info", padding=5)
        info_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)
        
        # Get font from theme manager
        text_font = theme.get_fonts().get("small", ("Consolas", 18))
        self.info_text = tk.Text(info_frame, wrap="word", height=6, font=text_font)
        self.info_text.grid(row=0, column=0, sticky="nsew")
        
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        info_scroll.grid(row=0, column=1, sticky="ns")
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
    def _create_poker_table_panel(self):
        """Create the right panel with centered poker table (80% size)."""
        table_frame = ttk.LabelFrame(self, text="Poker Table", padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        # Center the poker table with 80% sizing
        # Add padding around the table to center it
        table_frame.grid_columnconfigure(0, weight=1)  # Left padding
        table_frame.grid_columnconfigure(1, weight=8)  # Table (80%)
        table_frame.grid_columnconfigure(2, weight=1)  # Right padding
        table_frame.grid_rowconfigure(0, weight=1)     # Top padding
        table_frame.grid_rowconfigure(1, weight=8)     # Table (80%)
        table_frame.grid_rowconfigure(2, weight=1)     # Bottom padding
        
        # Create the ReusablePokerGameWidget for rich display (centered at 80%)
        self.poker_widget = ReusablePokerGameWidget(table_frame, state_machine=None)
        self.poker_widget.grid(row=1, column=1, sticky="nsew")
        
        # Initialize poker widget UI
        if hasattr(self.poker_widget, '_setup_ui'):
            self.poker_widget._setup_ui()
        
    def _load_legendary_hands(self):
        """Load legendary hands from the data directory."""
        try:
            # Try multiple possible locations for legendary hands data
            data_paths = [
                "backend/data/legendary_hands.json",
                "data/legendary_hands.json",
                os.path.join(os.path.dirname(__file__), "../../../data/legendary_hands.json"),
                os.path.join(os.path.dirname(__file__), "../../data/legendary_hands.json")
            ]
            
            legendary_data = None
            for path in data_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        legendary_data = json.load(f)
                    print(f"✅ Loaded legendary hands from: {path}")
                    break
            
            if not legendary_data:
                print("❌ No legendary hands data found")
                return
                
            # Process legendary hands data
            if isinstance(legendary_data, list):
                self.legendary_hands = legendary_data
            elif isinstance(legendary_data, dict) and 'hands' in legendary_data:
                self.legendary_hands = legendary_data['hands']
            else:
                print(f"⚠️ Unexpected legendary hands format: {type(legendary_data)}")
                return
                
            # Populate the hands list
            self._populate_hands_list()
            
            print(f"✅ Loaded {len(self.legendary_hands)} legendary hands")
            
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            
    def _populate_hands_list(self):
        """Populate the hands listbox with available hands."""
        self.hands_listbox.delete(0, tk.END)
        
        filter_text = self.search_var.get().lower()
        
        for i, hand in enumerate(self.legendary_hands):
            # Create display name from hand data
            if isinstance(hand, dict):
                hand_id = hand.get('hand_id', f'Hand_{i+1}')
                players_info = hand.get('players', [])
                num_players = len(players_info) if isinstance(players_info, list) else 'N/A'
                
                # Get some basic info for display
                display_name = f"{hand_id} ({num_players}p)"
                
                # Apply filter if present
                if not filter_text or filter_text in display_name.lower():
                    self.hands_listbox.insert(tk.END, display_name)
                    # Store the original index for retrieval
                    self.hands_listbox.insert(tk.END, "")  # Placeholder, we'll use index
                    self.hands_listbox.delete(tk.END)  # Remove placeholder
                    
    def _filter_hands(self, *args):
        """Filter the hands list based on search text."""
        self._populate_hands_list()
        
    def _on_hand_selected(self, event=None):
        """Handle hand selection in the listbox."""
        selection = self.hands_listbox.curselection()
        if not selection:
            return
            
        # Update info display with selected hand details
        try:
            selected_idx = selection[0]
            if selected_idx < len(self.legendary_hands):
                hand_data = self.legendary_hands[selected_idx]
                self._update_hand_info(hand_data)
        except (IndexError, KeyError) as e:
            print(f"Error selecting hand: {e}")
            
    def _update_hand_info(self, hand_data):
        """Update the hand info display."""
        self.info_text.delete(1.0, tk.END)
        
        if isinstance(hand_data, dict):
            info_lines = []
            info_lines.append(f"Hand ID: {hand_data.get('hand_id', 'Unknown')}")
            
            players = hand_data.get('players', [])
            if isinstance(players, list):
                info_lines.append(f"Players: {len(players)}")
                for i, player in enumerate(players):
                    if isinstance(player, dict):
                        name = player.get('name', f'Player {i+1}')
                        stack = player.get('stack', 'Unknown')
                        position = player.get('position', 'Unknown')
                        info_lines.append(f"  {name}: ${stack} ({position})")
            
            # Add more hand details as available
            if 'dealer_position' in hand_data:
                info_lines.append(f"Dealer: Position {hand_data['dealer_position']}")
                
            if 'small_blind' in hand_data:
                info_lines.append(f"Blinds: ${hand_data.get('small_blind', 1)}/${hand_data.get('big_blind', 2)}")
                
            self.info_text.insert(1.0, "\n".join(info_lines))
            
    def _load_selected_hand(self, event=None):
        """Load the selected hand for playback."""
        selection = self.hands_listbox.curselection()
        if not selection:
            return
            
        try:
            selected_idx = selection[0]
            if selected_idx < len(self.legendary_hands):
                hand_data = self.legendary_hands[selected_idx]
                self._initialize_hand_playback(hand_data)
                
                # Enable controls
                self.next_btn.configure(state="normal")  
                self.play_btn.configure(state="normal")
                self.reset_btn.configure(state="normal")
                
        except Exception as e:
            print(f"Error loading hand: {e}")
            
    def _initialize_hand_playback(self, hand_data):
        """Initialize a hand for playback (following legacy UnifiedHandsReviewPanel architecture)."""
        try:
            self.current_hand_data = hand_data
            self.playback_index = 0
            self.is_playing = False
            
            # Update info display  
            hand_id = hand_data.get('hand_id', 'Unknown')
            self._update_hand_info(f"Loading hand: {hand_id}")
            
            print(f"🔄 Initializing hand: {hand_id}")
            if self.session_logger:
                self.session_logger.log_system("INFO", "ENHANCED_REVIEW", f"Loading hand: {hand_id}", {})
            
            # Convert to Hand model (following validation tester pattern)
            if Hand and HandModelDecisionEngine and GameConfig:
                # Convert legendary hand data to Hand model using Hand.from_dict
                hand = Hand.from_dict(hand_data)
                
                # Build GameConfig from Hand model metadata (following validation tester pattern)
                game_config = GameConfig(
                    small_blind=getattr(hand.metadata, 'small_blind', 1.0),
                    big_blind=getattr(hand.metadata, 'big_blind', 2.0),
                    starting_stack=getattr(hand.metadata, 'starting_stack', 100.0),
                    num_players=len(hand.seats)
                )
                
                # Create decision engine and session (using the real working implementation)
                decision_engine = HandModelDecisionEngine(hand)
                self.current_session = HandsReviewBotSession(
                    config=game_config,
                    decision_engine=decision_engine,
                )
                
                # Set the preloaded hand data (following legacy pattern)
                try:
                    self.current_session.set_preloaded_hand_data({"hand_model": hand})
                except Exception:
                    self.current_session.set_preloaded_hand_data(hand_data)
                
                # Connect the ReusablePokerGameWidget (following legacy pattern)
                if hasattr(self.poker_widget, 'state_machine'):
                    self.poker_widget.state_machine = self.current_session
                    
                    # Add the widget as event listener (crucial for updates)
                    if hasattr(self.current_session, 'add_event_listener'):
                        self.current_session.add_event_listener(self.poker_widget)
                    
                    # Trigger seat creation and initial display update
                    if hasattr(self.poker_widget, '_ensure_seats_created_and_update'):
                        self.poker_widget.after(50, self.poker_widget._ensure_seats_created_and_update)
                    
                    print(f"🎯 Connected poker widget to state machine and triggered setup")
                    # Also force a display update to ensure the poker table appears
                    self.after(100, lambda: self._force_poker_display_update())
                
                # Start the session (following legacy pattern)
                success = self.current_session.start_session()
                if success:
                    self.session_active = True
                    self._update_hand_info("Hand loaded successfully. Click Next to begin replay.")
                    
                    # Update poker widget to show initial state with hole cards
                    if hasattr(self.poker_widget, 'update_display'):
                        self.poker_widget.update_display("hand_start")
                        # Defer one more update for proper layout (following legacy pattern)
                        self.after(150, lambda: self.poker_widget.update_display("hand_start"))
                    
                    print(f"✅ Hand session started successfully")
                else:
                    self._update_hand_info("Failed to start hand session")
                    print(f"❌ Failed to start hand session")
            else:
                # Fallback for when core modules are missing
                print("⚠️  Core modules not available, using fallback initialization")
                self._update_hand_info("Hand loaded (limited functionality)")
                
        except Exception as e:
            print(f"❌ Error initializing hand playback: {e}")
            self._update_hand_info(f"Error loading hand: {e}")
    
    def _next_action(self):
        """Execute the next action in the replay (following legacy UnifiedHandsReviewPanel pattern)."""
        if not self.current_session or not self.session_active:
            print("⚠️  No active session for next action")
            return
        
        try:
            # Execute next action via bot session (following legacy pattern)
            result = self.current_session.execute_next_bot_action()
            
            if result:
                # Update poker table display (following legacy pattern)
                if hasattr(self.poker_widget, 'update_display'):
                    self.poker_widget.update_display("action_complete")
                
                # Get explanation from session (following legacy pattern)
                explanation = "Action executed"
                if hasattr(self.current_session, 'decision_history') and self.current_session.decision_history:
                    last_decision = self.current_session.decision_history[-1]
                    explanation = last_decision.get('explanation', 'Action executed')
                
                self._update_hand_info(explanation)
                print(f"✅ Next action executed: {explanation}")
                
            else:
                # Session complete or failed (following legacy pattern)  
                self._update_hand_info("Hand replay completed")
                self.session_active = False
                self._disable_controls()
                print("🏁 Hand replay completed")
                
        except Exception as e:
            print(f"❌ Failed to execute next action: {e}")
            self._update_hand_info(f"Error: {e}")
    
    def _update_hand_info(self, message):
        """Update the hand info display."""
        try:
            if hasattr(self, 'info_text'):
                self.info_text.delete(1.0, "end")
                self.info_text.insert(1.0, message)
        except Exception:
            pass  # Fallback if info text not available
    
    def _force_poker_display_update(self):
        """Force the poker widget to display the current state."""
        print("🎯 Forcing poker display update...")
        try:
            if hasattr(self.poker_widget, 'update_display'):
                print("🎯 Calling update_display('hand_start')")
                self.poker_widget.update_display("hand_start")
            elif hasattr(self.poker_widget, '_ensure_seats_created_and_update'):
                print("🎯 Calling _ensure_seats_created_and_update directly")
                self.poker_widget._ensure_seats_created_and_update()
            else:
                print("🎯 No update method available")
        except Exception as e:
            print(f"❌ Error in force display update: {e}")
            import traceback
            traceback.print_exc()
    
    def _disable_controls(self):
        """Disable the control buttons."""
        try:
            self.next_btn.configure(state="disabled")
            self.play_btn.configure(state="disabled") 
            self.reset_btn.configure(state="disabled")
        except Exception:
            pass
            
    def _toggle_playback(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()
            
    def _start_playback(self):
        """Start automatic playback."""
        if not self.current_session or not self.session_active:
            return
            
        self.is_playing = True
        self.play_btn.configure(text="⏸ Pause")
        self._auto_step()
        
    def _pause_playback(self):
        """Pause automatic playback."""
        self.is_playing = False
        self.play_btn.configure(text="▶ Auto")
        
    def _auto_step(self):
        """Automatically step through the hand."""
        if not self.is_playing or not self.session_active:
            return
            
        # Use _next_action for consistency
        try:
            old_session_active = self.session_active
            self._next_action()
            
            # If session is still active, schedule next step  
            if self.session_active and self.is_playing:
                self.after(int(self.play_speed), self._auto_step)
            else:
                # Hand finished, stop playback
                self._pause_playback()
        except Exception as e:
            print(f"❌ Auto step failed: {e}")
            self._pause_playback()
            
    def _reset_hand(self):
        """Reset the hand to the beginning (following legacy pattern)."""
        if not self.current_session:
            return
        
        try:
            # Stop any auto playback
            self._pause_playback()
            
            # Reset the session (following legacy pattern)
            if hasattr(self.current_session, 'reset_session'):
                self.current_session.reset_session()
            
            # Re-initialize from the beginning
            if self.current_hand_data:
                self._initialize_hand_playback(self.current_hand_data)
                
            print("🔄 Hand reset to beginning")
            
        except Exception as e:
            print(f"❌ Error resetting hand: {e}")
            self._update_hand_info(f"Error resetting hand: {e}")
            
    def _on_speed_changed(self, value):
        """Handle speed control change."""
        speed = float(value)
        self.play_speed = int(2000 / speed)  # Convert to milliseconds (inverse relationship)
        self.speed_label.configure(text=f"{speed:.1f}x")
        
    def _apply_theme_to_components(self, theme: ThemeManager):
        """Apply the current theme to all components."""
        # Apply theme to poker widget if it supports theming
        if hasattr(self.poker_widget, 'apply_theme'):
            self.poker_widget.apply_theme(theme.get_theme())
            
    def _on_theme_changed(self, theme_manager: ThemeManager):
        """Handle theme changes."""
        self._apply_theme_to_components(theme_manager)
        
        # Refresh the poker table display
        if hasattr(self.poker_widget, '_draw_table'):
            self.poker_widget.after_idle(self.poker_widget._draw_table)
    
    def _refresh_fonts(self):
        """Refresh all fonts from theme manager (called by font scaling)."""
        theme: ThemeManager = self.services.get_app("theme")
        fonts = theme.get_fonts()
        
        # Update hands listbox font
        if hasattr(self, 'hands_listbox'):
            listbox_font = fonts.get("body", ("Consolas", 20))
            self.hands_listbox.config(font=listbox_font)
        
        # Update info text font
        if hasattr(self, 'info_text'):
            text_font = fonts.get("small", ("Consolas", 18))
            self.info_text.config(font=text_font)
        
        # Force poker widget to refresh fonts if it supports it
        if hasattr(self.poker_widget, '_refresh_fonts'):
            self.poker_widget._refresh_fonts()
        elif hasattr(self.poker_widget, '_draw_table'):
            # Fallback: redraw the table
            self.poker_widget.after_idle(self.poker_widget._draw_table)
            
    def on_show(self) -> None:
        """Called when the tab is shown."""
        if hasattr(self.poker_widget, '_draw_table'):
            # Refresh the poker table when tab becomes visible
            self.poker_widget.after_idle(self.poker_widget._draw_table)
