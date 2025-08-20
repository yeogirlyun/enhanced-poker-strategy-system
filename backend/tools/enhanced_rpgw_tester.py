#!/usr/bin/env python3
"""
Enhanced RPGW – Full Poker Table Tester
- Loads GTO hands and displays them on a real poker table
- Steps through actions with visual feedback
- Integrates with existing UI architecture components
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Add backend to path for imports
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

try:
    from ui.services.service_container import ServiceContainer
    from ui.services.theme_manager import ThemeManager
    from utils.sound_manager import SoundManager
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from core.hand_model import Hand
    
    # Import UI components for poker table
    from ui.tableview.canvas_manager import CanvasManager
    from ui.tableview.layer_manager import LayerManager
    from ui.tableview.renderer_pipeline import RendererPipeline
    from ui.tableview.components.pot_display import PotDisplay
    from ui.tableview.components.seats import Seats
    from ui.tableview.components.community import Community
    from ui.tableview.components.table_felt import TableFelt
    from ui.tableview.components.dealer_button import DealerButton
    from ui.tableview.components.bet_display import BetDisplay
    from ui.tableview.components.action_indicator import ActionIndicator
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️ Some components may not work properly")
    # Create fallback classes
    class ServiceContainer: pass
    class ThemeManager: pass
    class SoundManager: pass
    class PurePokerStateMachine: pass
    class GameConfig: pass
    class Hand: pass

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON = os.path.join(HERE, "..", "test_hand_with_flop.json")

def load_hands(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError("gto_hands.json should be a non-empty list of hands")
    return data

def flatten_hand(hand: dict):
    """Produce a list of 'steps' to drive the UI."""
    steps = []

    # Synthesize: deal hole cards
    holes = (hand.get("metadata", {}) or {}).get("hole_cards", {}) or {}
    steps.append({
        "type": "DEAL_HOLE",
        "desc": "🃏 Deal hole cards",
        "payload": {"hole_cards": holes},
    })

    streets = hand.get("streets", {}) or {}
    # Keep deterministic street order
    for street_name in ("PREFLOP", "FLOP", "TURN", "RIVER"):
        if street_name not in streets:
            continue
        s = streets[street_name] or {}
        actions = s.get("actions", []) or []
        board = s.get("board", []) or []

        # If board present, add board-deal step
        if street_name != "PREFLOP" and board:
            steps.append({
                "type": "DEAL_BOARD",
                "desc": f"🂠 Deal {street_name} board: {', '.join(board)}",
                "payload": {"street": street_name, "board": board},
            })

        for a in actions:
            # Handle different action types
            action_type = a.get("action", "UNKNOWN")
            actor = a.get("actor_uid", "Unknown")
            amount = a.get("amount", 0)
            
            if action_type == "POST_BLIND":
                desc = f"{street_name}: {actor} → {action_type} {amount}"
            elif action_type in ["BET", "RAISE", "CALL"]:
                desc = f"{street_name}: {actor} → {action_type} {amount}"
            elif action_type == "CHECK":
                desc = f"{street_name}: {actor} → {action_type}"
            elif action_type == "FOLD":
                desc = f"{street_name}: {actor} → {action_type}"
            else:
                desc = f"{street_name}: {actor} → {action_type} {amount if amount else ''}"
            
            steps.append({
                "type": action_type,
                "desc": desc,
                "payload": {"street": street_name, **a},
            })

    # Terminal step
    steps.append({"type": "END_HAND", "desc": "✅ End of hand", "payload": {}})
    return steps

class EnhancedRPGWTester(ttk.Frame):
    """Full Enhanced RPGW with poker table display."""
    
    def __init__(self, parent, services, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.services = services
        self.session_id = "test_session"
        
        # Get sound manager
        self.sound_manager = services.get_app("sound") if services else None
        if not self.sound_manager:
            self.sound_manager = SoundManager(test_mode=True)
        
        # Poker game state
        self.current_hand = None
        self.hand_actions = []
        self.current_action_index = 0
        self.ppsm = None
        
        # Initialize UI
        self._setup_poker_table()
        self._setup_controls()
        self._setup_state_management()
        
        # Start update loop
        self.after(100, self._update_loop)
        
        print("🎯 Enhanced RPGW Tester initialized")

    def _setup_poker_table(self):
        """Set up the poker table with all UI components."""
        # Get screen dimensions for 50% sizing
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate table size as 50% of screen
        table_width = int(screen_width * 0.5)
        table_height = int(screen_height * 0.5)
        
        # Ensure minimum usable size
        table_width = max(table_width, 1200)
        table_height = max(table_height, 800)
        
        # Calculate card size based on table dimensions
        # Cards should be proportional to table size
        card_width = max(40, int(table_width * 0.035))  # ~3.5% of table width
        card_height = int(card_width * 1.45)  # Standard card aspect ratio
        
        print(f"🎯 Screen: {screen_width}x{screen_height}, Table: {table_width}x{table_height}")
        print(f"🎯 Card size: {card_width}x{card_height}")
        
        # Create canvas infrastructure with proper sizing
        self.canvas_manager = CanvasManager(self)
        
        # Configure canvas size
        self.canvas_manager.canvas.configure(width=table_width, height=table_height)
        
        self.layer_manager = LayerManager(
            self.canvas_manager.canvas,
            self.canvas_manager.overlay
        )
        
        # Create poker table components with proper sizing
        self.table_components = [
            TableFelt(),           # Background felt
            Seats(),              # Player seats with cards, stacks, names  
            Community(),          # Community cards
            BetDisplay(),         # Current bet amounts
            PotDisplay(),         # Pot amount display
            DealerButton(),       # Dealer button
            ActionIndicator(),    # Highlight acting player
        ]
        
        # Create rendering pipeline
        self.renderer_pipeline = RendererPipeline(
            self.canvas_manager,
            self.layer_manager,
            self.table_components
        )
        
        # Grid canvas to fill the widget
        self.canvas_manager.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Store dimensions for state management
        self.table_width = table_width
        self.table_height = table_height
        self.card_width = card_width
        self.card_height = card_height
        
        print("🎨 Poker table components ready")

    def _setup_controls(self):
        """Set up control interface above the poker table."""
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Hand selection
        ttk.Label(controls_frame, text="Hand:").pack(side=tk.LEFT, padx=(0, 5))
        self.hand_idx_var = tk.IntVar(value=0)
        hand_spin = ttk.Spinbox(controls_frame, from_=0, to=9999, textvariable=self.hand_idx_var, width=7)
        hand_spin.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load button
        self.load_btn = ttk.Button(controls_frame, text="Load GTO Hand", command=self.load_hand)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress display
        self.progress_label = ttk.Label(controls_frame, text="No hand loaded")
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Action controls
        self.next_btn = ttk.Button(controls_frame, text="Next Action ▶", command=self.next_action, state="disabled")
        self.next_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.reset_btn = ttk.Button(controls_frame, text="Reset", command=self.reset, state="disabled")
        self.reset_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status
        self.status_label = ttk.Label(controls_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        print("🎮 Controls ready")

    def _setup_state_management(self):
        """Initialize state management for the poker table."""
        # Initialize display state (follows your established architecture)
        self.display_state = {
            'table': {
                'width': 1200,  # Will be updated after table setup
                'height': 800   # Will be updated after table setup
            },
            'pot': {
                'amount': 0.0,
                'side_pots': []
            },
            'seats': [],
            'board': [],
            'dealer': {
                'position': 0
            },
            'action': {
                'current_player': -1,
                'action_type': None,
                'amount': 0.0,
                'highlight': False
            },
            'replay': {
                'active': False,
                'current_action': 0,
                'total_actions': 0,
                'description': "No hand loaded"
            }
        }
        
        print("🎯 State management ready")

    def _update_table_dimensions(self):
        """Update display state with actual table dimensions."""
        if hasattr(self, 'table_width') and hasattr(self, 'table_height'):
            self.display_state['table'].update({
                'width': self.table_width,
                'height': self.table_height
            })
            print(f"🎯 Updated table dimensions: {self.table_width}x{self.table_height}")

    def load_hand(self):
        """Load a GTO hand and prepare for replay."""
        try:
            # Load hands from JSON
            hands = load_hands(DEFAULT_JSON)
            
            # Handle both single hand and multiple hands
            if isinstance(hands, dict):
                # Single hand file
                hands = [hands]
            
            # Get selected hand index
            idx = self.hand_idx_var.get()
            if idx < 0 or idx >= len(hands):
                messagebox.showerror("Index error", f"Hand index {idx} out of range (0..{len(hands)-1})")
                return
            
            # Store current hand
            self.current_hand = hands[idx]
            
            # Extract actions for replay
            self.hand_actions = flatten_hand(self.current_hand)
            self.current_action_index = 0
            
            # Initialize PPSM
            self._initialize_ppsm()
            
            # Load hand into display state
            self._load_hand_into_state()
            
            # Update controls
            self.next_btn.config(state="normal")
            self.reset_btn.config(state="normal")
            
            # Update display
            self._render_table()
            
            # Update status
            hand_id = self.current_hand.get('metadata', {}).get('hand_id', 'Unknown')
            self.status_label.config(text=f"Hand {hand_id} loaded")
            self.progress_label.config(text=f"Action 0/{len(self.hand_actions)}")
            
            # Play deal sound
            if self.sound_manager:
                self.sound_manager.play_card_sound("deal")
            
            print(f"✅ Hand loaded: {len(self.hand_actions)} actions")
            print(f"🎯 Hand has flop: {len(self.current_hand.get('streets', {}).get('FLOP', {}).get('board', []))} cards")
            
        except Exception as e:
            print(f"❌ Error loading hand: {e}")
            messagebox.showerror("Load error", f"Failed to load hand:\n{e}")

    def _initialize_ppsm(self):
        """Initialize PPSM for the hand."""
        try:
            # Create game config from hand metadata
            metadata = self.current_hand.get('metadata', {})
            seats = self.current_hand.get('seats', [])
            
            config = GameConfig(
                num_players=len(seats),
                small_blind=metadata.get('small_blind', 5),
                big_blind=metadata.get('big_blind', 10),
                starting_stack=seats[0].get('starting_stack', 1000) if seats else 1000
            )
            
            # Create PPSM instance
            self.ppsm = PurePokerStateMachine(config=config)
            
            print("✅ PPSM initialized for hand")
            
        except Exception as e:
            print(f"⚠️ PPSM initialization error: {e}")
            self.ppsm = None

    def _load_hand_into_state(self):
        """Load hand data into display state."""
        if not self.current_hand:
            return
        
        try:
            # Update table dimensions first
            self._update_table_dimensions()
            
            # Update seats from hand with proper card display
            seats = []
            for i, seat in enumerate(self.current_hand.get('seats', [])):
                # Get hole cards from metadata if available
                hole_cards = []
                if 'metadata' in self.current_hand and 'hole_cards' in self.current_hand['metadata']:
                    hole_cards = self.current_hand['metadata']['hole_cards'].get(seat.get('player_uid', f'Player{i+1}'), [])
                
                seat_data = {
                    'player_uid': seat.get('player_uid', f'Player{i+1}'),
                    'name': seat.get('display_name', f'Player {i+1}'),
                    'starting_stack': seat.get('starting_stack', 1000),
                    'current_stack': seat.get('starting_stack', 1000),
                    'current_bet': 0.0,
                    'cards': hole_cards,  # Use actual hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': i
                }
                seats.append(seat_data)
            
            # Update state
            self.display_state.update({
                'seats': seats,
                'pot': {'amount': 0.0, 'side_pots': []},
                'board': [],
                'dealer': {'position': 0},
                'replay': {
                    'active': False,
                    'current_action': 0,
                    'total_actions': len(self.hand_actions),
                    'description': self.hand_actions[0]['desc'] if self.hand_actions else "No actions"
                }
            })
            
            print(f"🎯 Loaded {len(seats)} seats with cards: {[len(s['cards']) for s in seats]}")
            
        except Exception as e:
            print(f"⚠️ Error updating display state: {e}")

    def next_action(self):
        """Execute next action and update poker table."""
        if not self.hand_actions or self.current_action_index >= len(self.hand_actions):
            return
        
        # Get current action
        action = self.hand_actions[self.current_action_index]
        
        # Execute action
        self._execute_action(action)
        
        # Play sound effects
        self._play_action_sound(action)
        
        # Advance action index
        self.current_action_index += 1
        
        # Update progress
        self.progress_label.config(text=f"Action {self.current_action_index}/{len(self.hand_actions)}")
        
        # Disable next button if complete
        if self.current_action_index >= len(self.hand_actions):
            self.next_btn.config(state="disabled")
            self.status_label.config(text="Hand complete!")
        
        # Re-render table
        self._render_table()
        
        print(f"🎬 Action {self.current_action_index}/{len(self.hand_actions)}: {action['desc']}")

    def _execute_action(self, action):
        """Execute action and update state."""
        action_type = action['type']
        
        if action_type == 'DEAL_HOLE':
            # Cards are already in seats from initialization
            self.display_state['action'].update({
                'current_player': -1,
                'action_type': 'Deal',
                'amount': 0.0,
                'highlight': False
            })
            
        elif action_type == 'DEAL_BOARD':
            street = action['payload']['street']
            board = action['payload'].get('board', [])
            
            # Add community cards based on street
            if street == 'FLOP':
                self.display_state['board'] = board if board else ['XX', 'YY', 'ZZ']
            elif street == 'TURN':
                if len(self.display_state['board']) >= 3:
                    self.display_state['board'].append(board[0] if board else 'TT')
            elif street == 'RIVER':
                if len(self.display_state['board']) >= 4:
                    self.display_state['board'].append(board[0] if board else 'RR')
            
            self.display_state['action'].update({
                'current_player': -1,
                'action_type': f'Deal {street}',
                'amount': 0.0,
                'highlight': False
            })
            
        elif action_type == 'POST_BLIND':
            # Handle blind posting
            actor_uid = action['payload'].get('actor_uid', 'Unknown')
            amount = action['payload'].get('amount', 0.0)
            
            # Find player and update
            for seat in self.display_state['seats']:
                if seat['player_uid'] == actor_uid:
                    seat['current_bet'] = amount
                    seat['current_stack'] -= amount
                    self.display_state['pot']['amount'] += amount
                    
                    # Highlight acting player
                    self.display_state['action'].update({
                        'current_player': seat['position'],
                        'action_type': 'POST_BLIND',
                        'amount': amount,
                        'highlight': True
                    })
                    break
            
        elif action_type == 'END_HAND':
            # Hand complete
            self.display_state['action'].update({
                'current_player': -1,
                'action_type': 'End',
                'amount': 0.0,
                'highlight': False
            })
        
        # Update replay state
        self.display_state['replay'].update({
            'current_action': self.current_action_index + 1,
            'description': action['desc']
        })

    def _play_action_sound(self, action):
        """Play sound effects for actions."""
        if not self.sound_manager:
            return
        
        try:
            action_type = action['type']
            
            if action_type in ['DEAL_HOLE', 'DEAL_BOARD']:
                self.sound_manager.play_card_sound('deal')
            elif action_type == 'POST_BLIND':
                self.sound_manager.play_action_sound('bet', action['payload'].get('amount', 0))
                
        except Exception as e:
            print(f"⚠️ Sound error: {e}")

    def reset(self):
        """Reset to beginning of hand."""
        self.current_action_index = 0
        self._load_hand_into_state()
        self._render_table()
        
        self.next_btn.config(state="normal")
        self.progress_label.config(text=f"Action 0/{len(self.hand_actions)}")
        self.status_label.config(text="Hand reset")
        
        print("↩️ Reset to start")

    def _render_table(self):
        """Render the poker table using the component pipeline."""
        try:
            # Use state-driven rendering pipeline
            self.renderer_pipeline.render_once(self.display_state)
        except Exception as e:
            print(f"⚠️ Render error: {e}")

    def _update_loop(self):
        """Main update loop for animations and state."""
        # Update any ongoing animations
        # For now, just schedule next update
        self.after(50, self._update_loop)

class App:
    def __init__(self, root):
        self.root = root
        root.title("Enhanced RPGW – Full Poker Table Tester")
        
        # Initialize services
        services = ServiceContainer()
        
        # Theme manager
        theme_manager = ThemeManager()
        services.provide_app("theme", theme_manager)
        
        # Sound manager
        sound_manager = SoundManager(test_mode=False)
        services.provide_app("sound", sound_manager)
        
        print("✅ Services initialized")
        
        # Create Enhanced RPGW Tester
        self.tester = EnhancedRPGWTester(root, services)
        self.tester.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        print("✅ Enhanced RPGW Tester created")

def main():
    try:
        root = tk.Tk()
    except Exception as e:
        raise SystemExit(f"Tk failed to start (try OS Terminal): {e}")

    # Get screen dimensions for proper window sizing
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate window size (table + controls + padding)
    window_width = int(screen_width * 0.6)  # 60% of screen width
    window_height = int(screen_height * 0.7)  # 70% of screen height
    
    # Ensure minimum usable size
    window_width = max(window_width, 1400)
    window_height = max(window_height, 900)
    
    # Center the window on screen
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.title("Enhanced RPGW – Full Poker Table Tester")
    
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
