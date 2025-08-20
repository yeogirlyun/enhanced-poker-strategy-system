"""
Hands Review Tab with PPSM Integration

This tab integrates the new PurePokerStateMachine architecture with the hands review functionality.
It loads and displays GTO hands for analysis and replay using the production-ready PPSM engine.

Features:
- Load GTO hands (160 hands with 100% validation success)
- PPSM-based hand replay with deterministic behavior
- HandModelDecisionEngine integration for accurate replay
- Modern UI with theme system integration
- Comprehensive hand analysis and review tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

# New UI Architecture imports
from ..state.actions import (
    SET_TABLE_DIM,
    SET_POT,
    SET_SEATS,
    SET_BOARD,
    SET_DEALER,
    SET_REVIEW_HANDS,
    SET_REVIEW_FILTER,
    SET_LOADED_HAND,
    SET_STUDY_MODE
)
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer

# Theme and UI components
from ..services.theme_manager import ThemeManager
from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager

# Import enhanced button components
try:
    from ..components.enhanced_button import PrimaryButton, SecondaryButton
except ImportError:
    # Fallback to basic buttons if enhanced buttons not available
    PrimaryButton = SecondaryButton = tk.Button

# PPSM Architecture imports
try:
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from core.hand_model_decision_engine import HandModelDecisionEngine
    from core.hand_model import Hand
    from core.poker_types import PokerState, ActionType
    PPSM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PPSM imports failed: {e}")
    PPSM_AVAILABLE = False
    
    # Minimal stubs for development
    class PurePokerStateMachine:
        def __init__(self, *args, **kwargs): pass
    class GameConfig:
        def __init__(self, *args, **kwargs): pass
    class HandModelDecisionEngine:
        def __init__(self, *args, **kwargs): pass
    class Hand:
        def __init__(self, *args, **kwargs): pass


class GTOHandsLoader:
    """Loader for GTO hands with proper Hand model format."""
    
    def __init__(self, gto_hands_file: str = "gto_hands.json"):
        self.gto_hands_file = gto_hands_file
        self.hands_cache: List[Hand] = []
        self._loaded = False
    
    def load_gto_hands(self) -> List[Hand]:
        """Load GTO hands from JSON file."""
        if self._loaded:
            return self.hands_cache
            
        gto_path = Path(self.gto_hands_file)
        if not gto_path.exists():
            print(f"⚠️ GTO hands file not found: {gto_path}")
            return []
        
        try:
            with open(gto_path, 'r') as f:
                hands_data = json.load(f)
            
            print(f"📊 Loading {len(hands_data)} GTO hands...")
            
            # Convert JSON data to Hand objects
            for i, hand_data in enumerate(hands_data):
                try:
                    # Create Hand object from JSON data
                    hand = Hand(**hand_data)
                    self.hands_cache.append(hand)
                    
                    if (i + 1) % 20 == 0:
                        print(f"   📋 Loaded {i + 1}/{len(hands_data)} hands...")
                        
                except Exception as e:
                    print(f"   ⚠️ Failed to load hand {i + 1}: {e}")
                    continue
            
            self._loaded = True
            print(f"✅ Successfully loaded {len(self.hands_cache)} GTO hands")
            return self.hands_cache
            
        except Exception as e:
            print(f"❌ Failed to load GTO hands: {e}")
            return []
    
    def get_hands_summary(self) -> Dict[str, Any]:
        """Get summary statistics of loaded hands."""
        if not self._loaded:
            self.load_gto_hands()
        
        if not self.hands_cache:
            return {"total": 0, "by_players": {}}
        
        # Count by player count
        by_players = {}
        for hand in self.hands_cache:
            # Hand objects with dict attributes
            player_count = len(hand.seats)
            by_players[player_count] = by_players.get(player_count, 0) + 1
        
        return {
            "total": len(self.hands_cache),
            "by_players": by_players,
            "variants": ["NLHE"],  # GTO hands are all NLHE
            "sources": ["GTO Engine Generated"]
        }


class PPSMHandReplayEngine:
    """PPSM-based hand replay engine for hands review."""
    
    def __init__(self):
        self.ppsm = None
        self.decision_engine = None
        self.current_hand = None
        self.replay_results = {}
    
    def setup_hand_replay(self, hand) -> bool:
        """Setup PPSM for replaying the given Hand object."""
        try:
            if not PPSM_AVAILABLE:
                print("⚠️ PPSM not available - using stub functionality")
                return False
            
            # Handle Hand object with dict attributes
            seats = hand.seats
            metadata = hand.metadata
            small_blind = metadata['small_blind']
            big_blind = metadata['big_blind']
            hand_id = metadata['hand_id']
            
            # Extract configuration from hand
            config = GameConfig(
                num_players=len(seats),
                small_blind=small_blind,
                big_blind=big_blind,
                starting_stack=max(seat['starting_stack'] for seat in seats)
            )
            
            # Create PPSM instance
            self.ppsm = PurePokerStateMachine(config)
            
            # Create decision engine for hand replay
            self.decision_engine = HandModelDecisionEngine(hand)
            
            # Store current hand
            self.current_hand = hand
            
            print(f"✅ PPSM setup complete for hand {hand_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup PPSM replay: {e}")
            return False
    
    def replay_hand(self) -> Dict[str, Any]:
        """Replay the current hand using PPSM."""
        if not self.ppsm or not self.decision_engine or not self.current_hand:
            return {"success": False, "error": "Hand replay not properly setup"}
        
        try:
            # Get hand_id from Hand object
            hand_id = self.current_hand.metadata['hand_id']
            print(f"🎬 Starting PPSM replay for hand {hand_id}")
            
            # Use PPSM replay_hand_model method
            replay_results = self.ppsm.replay_hand_model(self.current_hand)
            
            self.replay_results = replay_results
            
            success = replay_results.get('success', False)
            if success:
                print(f"✅ Hand replay successful: {replay_results.get('successful_actions', 0)} actions")
            else:
                print(f"⚠️ Hand replay issues: {replay_results.get('failed_actions', 0)} failed actions")
            
            return replay_results
            
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            print(f"❌ Hand replay failed: {e}")
            return error_result
    
    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """Get current PPSM game state for UI display."""
        if not self.ppsm:
            return None
        
        try:
            return self.ppsm.get_game_info()
        except Exception as e:
            print(f"⚠️ Failed to get game state: {e}")
            return None


class HandsReviewTabPPSM:
    """
    Hands Review Tab with integrated PPSM architecture.
    
    Features:
    - GTO hands loading and display
    - PPSM-based hand replay
    - Modern UI with theme integration
    - Comprehensive hand analysis
    """
    
    def __init__(self, parent, store: Store, event_bus: EventBus, theme_manager: ThemeManager):
        self.parent = parent
        self.store = store
        self.event_bus = event_bus
        self.theme_manager = theme_manager
        self.session_id = str(uuid.uuid4())
        
        # Components
        self.gto_loader = GTOHandsLoader()
        self.replay_engine = PPSMHandReplayEngine()
        
        # UI State
        self.loaded_hands: List[Hand] = []
        self.current_hand: Optional[Hand] = None
        self.current_hand_index: int = -1
        
        # Create UI
        self._setup_ui()
        
        # Load GTO hands on initialization
        self._load_gto_hands()
        
        print(f"🎯 HandsReviewTabPPSM initialized with session {self.session_id}")
    
    def _setup_ui(self):
        """Setup the hands review UI with PPSM integration."""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="🎯 Hands Review - PPSM Integration",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(
            title_frame,
            text="Ready to load GTO hands...",
            foreground="green"
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Create main layout
        self._create_hands_list_panel()
        self._create_hand_details_panel()
        self._create_control_panel()
    
    def _create_hands_list_panel(self):
        """Create the hands list panel."""
        list_frame = ttk.LabelFrame(self.main_frame, text="📊 Available Hands", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create hands listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.hands_listbox = tk.Listbox(list_container, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.hands_listbox.yview)
        self.hands_listbox.config(yscrollcommand=scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.hands_listbox.bind('<<ListboxSelect>>', self._on_hand_selected)
        
        # Summary frame
        summary_frame = ttk.Frame(list_frame)
        summary_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.summary_label = ttk.Label(
            summary_frame,
            text="No hands loaded",
            font=("Arial", 10)
        )
        self.summary_label.pack(side=tk.LEFT)
    
    def _create_hand_details_panel(self):
        """Create the hand details panel."""
        details_frame = ttk.LabelFrame(self.main_frame, text="🔍 Hand Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Hand info display
        self.hand_info_text = tk.Text(
            details_frame, 
            height=8, 
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.hand_info_text.pack(fill=tk.X)
    
    def _create_control_panel(self):
        """Create the control panel with PPSM integration."""
        control_frame = ttk.LabelFrame(self.main_frame, text="🎮 PPSM Controls", padding=10)
        control_frame.pack(fill=tk.X)
        
        # Button container
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        # Load/Refresh button
        self.load_button = PrimaryButton(
            button_frame,
            text="🔄 Refresh GTO Hands",
            command=self._load_gto_hands
        )
        self.load_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Replay button
        self.replay_button = PrimaryButton(
            button_frame,
            text="🎬 PPSM Replay",
            command=self._replay_selected_hand,
            state=tk.DISABLED
        )
        self.replay_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Analysis button
        self.analyze_button = SecondaryButton(
            button_frame,
            text="📈 Analyze Hand",
            command=self._analyze_selected_hand,
            state=tk.DISABLED
        )
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Test PPSM button
        self.test_ppsm_button = SecondaryButton(
            button_frame,
            text="🔧 Test PPSM",
            command=self._test_ppsm_integration
        )
        self.test_ppsm_button.pack(side=tk.RIGHT)
    
    def _load_gto_hands(self):
        """Load GTO hands and populate the list."""
        self._update_status("🔄 Loading GTO hands...")
        
        try:
            # Load hands using the GTO loader
            self.loaded_hands = self.gto_loader.load_gto_hands()
            
            # Clear and populate listbox
            self.hands_listbox.delete(0, tk.END)
            
            for i, hand in enumerate(self.loaded_hands):
                # Create display string for hand (Hand object with dict attributes)
                hand_id = hand.metadata['hand_id']
                seats = hand.seats
                small_blind = hand.metadata['small_blind']
                big_blind = hand.metadata['big_blind']
                
                display_text = f"{hand_id} | {len(seats)}P | SB:{small_blind} BB:{big_blind}"
                self.hands_listbox.insert(tk.END, display_text)
            
            # Update summary
            summary = self.gto_loader.get_hands_summary()
            summary_text = f"Total: {summary['total']} hands"
            if summary['by_players']:
                players_summary = ", ".join([f"{p}P: {c}" for p, c in summary['by_players'].items()])
                summary_text += f" ({players_summary})"
            
            self.summary_label.config(text=summary_text)
            
            # Update status
            if self.loaded_hands:
                self._update_status(f"✅ Loaded {len(self.loaded_hands)} GTO hands successfully")
                
                # Update store with loaded hands
                self.store.dispatch({
                    "type": SET_REVIEW_HANDS,
                    "hands": [{"hand_id": h.metadata.hand_id, "players": len(h.seats)} for h in self.loaded_hands]
                })
            else:
                self._update_status("⚠️ No GTO hands loaded")
                
        except Exception as e:
            self._update_status(f"❌ Failed to load GTO hands: {e}")
            messagebox.showerror("Load Error", f"Failed to load GTO hands:\\n{e}")
    
    def _on_hand_selected(self, event):
        """Handle hand selection from the list."""
        selection = self.hands_listbox.curselection()
        if not selection or not self.loaded_hands:
            return
        
        # Get selected hand
        index = selection[0]
        if index >= len(self.loaded_hands):
            return
        
        self.current_hand = self.loaded_hands[index]
        self.current_hand_index = index
        
        # Update hand details display
        self._display_hand_details(self.current_hand)
        
        # Enable control buttons
        self.replay_button.config(state=tk.NORMAL)
        self.analyze_button.config(state=tk.NORMAL)
        
        # Update store (Hand object with dict attributes)
        hand_id = self.current_hand.metadata['hand_id']
        
        self.store.dispatch({
            "type": SET_LOADED_HAND,
            "hand": {"hand_id": hand_id}
        })
        
        self._update_status(f"📋 Selected hand: {hand_id}")
    
    def _display_hand_details(self, hand):
        """Display details of the selected Hand object."""
        self.hand_info_text.config(state=tk.NORMAL)
        self.hand_info_text.delete(1.0, tk.END)
        
        # Handle Hand object with dict attributes
        metadata = hand.metadata
        hand_id = metadata['hand_id']
        seats = hand.seats
        small_blind = metadata['small_blind']
        big_blind = metadata['big_blind']
        variant = metadata['variant']
        started_at = metadata['started_at_utc']
        hero_uid = hand.hero_player_uid
        streets = hand.streets
        
        # Format hand information
        details = f"""Hand ID: {hand_id}
Players: {len(seats)}
Blinds: {small_blind}/{big_blind}
Variant: {variant}
Generated: {started_at}

Seats:
"""
        for seat in seats:
            # Seat is a dict
            seat_no = seat['seat_no']
            display_name = seat['display_name']
            starting_stack = seat['starting_stack']
            is_button = seat['is_button']
            
            details += f"  {seat_no}: {display_name} (${starting_stack})"
            if is_button:
                details += " [BTN]"
            details += "\\n"
        
        details += f"\\nHero: {hero_uid}\\n"
        
        # Add streets info
        details += f"\\nStreets Available: {list(streets.keys())}\\n"
        for street_name, street_data in streets.items():
            # Street data is a dict
            action_count = len(street_data.get('actions', []))
            details += f"  {street_name}: {action_count} actions\\n"
        
        self.hand_info_text.insert(1.0, details)
        self.hand_info_text.config(state=tk.DISABLED)
    
    def _replay_selected_hand(self):
        """Replay the selected hand using PPSM."""
        if not self.current_hand:
            messagebox.showwarning("No Selection", "Please select a hand to replay.")
            return
        
        self._update_status("🎬 Setting up PPSM replay...")
        
        try:
            # Setup PPSM for replay
            if not self.replay_engine.setup_hand_replay(self.current_hand):
                messagebox.showerror("Setup Error", "Failed to setup PPSM for hand replay.")
                return
            
            self._update_status("▶️ Replaying hand with PPSM...")
            
            # Perform replay
            results = self.replay_engine.replay_hand()
            
            if results.get('success', False):
                # Show success results
                successful_actions = results.get('successful_actions', 0)
                total_actions = successful_actions + results.get('failed_actions', 0)
                final_pot = results.get('final_pot', 0)
                expected_pot = results.get('expected_pot', 0)
                
                # Get hand_id from Hand object
                hand_id = self.current_hand.metadata['hand_id']
                
                message = f"""✅ PPSM Replay Successful!
                
Actions: {successful_actions}/{total_actions} successful
Final Pot: ${final_pot:.2f}
Expected Pot: ${expected_pot:.2f}
Pot Match: {'✅' if abs(final_pot - expected_pot) < 1.0 else '⚠️'}

Hand: {hand_id}
Engine: PurePokerStateMachine v2"""
                
                messagebox.showinfo("Replay Success", message)
                self._update_status(f"✅ Replay complete: {successful_actions}/{total_actions} actions successful")
                
            else:
                # Show error results
                error = results.get('error', 'Unknown error')
                failed_actions = results.get('failed_actions', 0)
                
                message = f"""⚠️ PPSM Replay Issues:
                
Error: {error}
Failed Actions: {failed_actions}

This may indicate compatibility issues between 
the hand format and PPSM replay engine."""
                
                messagebox.showwarning("Replay Issues", message)
                self._update_status(f"⚠️ Replay had issues: {error}")
                
        except Exception as e:
            messagebox.showerror("Replay Error", f"Failed to replay hand:\\n{e}")
            self._update_status(f"❌ Replay failed: {e}")
    
    def _analyze_selected_hand(self):
        """Analyze the selected hand."""
        if not self.current_hand:
            messagebox.showwarning("No Selection", "Please select a hand to analyze.")
            return
        
        try:
            # Get hand info from Hand object
            metadata = self.current_hand.metadata
            hand_id = metadata['hand_id']
            seats = self.current_hand.seats
            small_blind = metadata['small_blind']
            big_blind = metadata['big_blind']
            streets = self.current_hand.streets
            starting_stacks = [seat['starting_stack'] for seat in seats]
            
            # Get game state if available
            game_state = self.replay_engine.get_game_state()
            
            analysis = f"""🔍 Hand Analysis: {hand_id}
            
Basic Info:
- Players: {len(seats)}
- Starting Stacks: {starting_stacks}
- Blinds: {small_blind}/{big_blind}

Streets:
"""
            
            for street_name, street_data in streets.items():
                # Street data is a dict
                actions = street_data.get('actions', [])
                analysis += f"- {street_name}: {len(actions)} actions\\n"
                
                # Show first few actions
                for i, action in enumerate(actions[:3]):
                    if isinstance(action, dict):
                        actor_uid = action.get('actor_uid', 'Unknown')
                        action_type = action.get('action', 'Unknown')
                        amount = action.get('amount', '')
                        analysis += f"  {actor_uid}: {action_type} {amount}\\n"
                    else:
                        analysis += f"  Action {i+1}: {action}\\n"
                        
                if len(actions) > 3:
                    analysis += f"  ... and {len(actions) - 3} more actions\\n"
            
            # Add PPSM state if available
            if game_state:
                analysis += f"\\nPPSM State:\\n"
                analysis += f"- Current State: {game_state.get('current_state', 'Unknown')}\\n"
                analysis += f"- Current Pot: ${game_state.get('pot', 0):.2f}\\n"
            
            # Show analysis in a new window
            analysis_window = tk.Toplevel(self.parent)
            analysis_window.title(f"Hand Analysis - {hand_id}")
            analysis_window.geometry("600x400")
            
            analysis_text = tk.Text(analysis_window, font=("Consolas", 10))
            analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            analysis_text.insert(1.0, analysis)
            analysis_text.config(state=tk.DISABLED)
            
            self._update_status(f"📊 Analysis complete for {hand_id}")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze hand:\\n{e}")
            self._update_status(f"❌ Analysis failed: {e}")
    
    def _test_ppsm_integration(self):
        """Test PPSM integration and report status."""
        test_results = f"""🔧 PPSM Integration Test
        
PPSM Available: {'✅ Yes' if PPSM_AVAILABLE else '❌ No'}
GTO Hands Loaded: {'✅ Yes' if self.loaded_hands else '❌ No'}
Total Hands: {len(self.loaded_hands)}
Current Hand: {'✅ Selected' if self.current_hand else '❌ None'}

Components:
- PurePokerStateMachine: {'✅' if PPSM_AVAILABLE else '❌'}
- HandModelDecisionEngine: {'✅' if PPSM_AVAILABLE else '❌'}
- GTO Hands Loader: {'✅' if self.gto_loader else '❌'}
- Replay Engine: {'✅' if self.replay_engine else '❌'}

Status: {'🟢 Ready for hand replay' if PPSM_AVAILABLE and self.loaded_hands else '🔴 Setup required'}
"""
        
        messagebox.showinfo("PPSM Integration Test", test_results)
        print("🔧 PPSM Integration Test Complete")
    
    def _update_status(self, message: str):
        """Update the status label."""
        self.status_label.config(text=message)
        print(f"📱 Status: {message}")
        
        # Also update the parent if needed
        if hasattr(self.parent, 'update'):
            self.parent.update()
    
    def get_frame(self) -> ttk.Frame:
        """Get the main frame for this tab."""
        return self.main_frame
