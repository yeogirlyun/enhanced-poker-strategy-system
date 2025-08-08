#!/usr/bin/env python3
"""
Comprehensive debug test for FPSM Hands Review Panel
This test will help identify exactly what's going wrong with card display and animations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, Player
from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
from core.types import ActionType

class ComprehensiveDebugTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FPSM Hands Review Debug Tester")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.hands_database = ComprehensiveHandsDatabase()
        self.fpsm = None
        self.poker_widget = None
        self.current_hand = None
        self.action_history = []
        
        self.setup_ui()
        self.load_sample_hand()
    
    def setup_ui(self):
        """Setup the debug UI."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Controls
        ttk.Label(left_panel, text="Debug Controls", font=("Arial", 12, "bold")).pack(pady=5)
        
        ttk.Button(left_panel, text="Load Sample Hand", command=self.load_sample_hand).pack(pady=2)
        ttk.Button(left_panel, text="Start Simulation", command=self.start_simulation).pack(pady=2)
        ttk.Button(left_panel, text="Next Action", command=self.next_action).pack(pady=2)
        ttk.Button(left_panel, text="Show Debug Info", command=self.show_debug_info).pack(pady=2)
        ttk.Button(left_panel, text="Force Card Display", command=self.force_card_display).pack(pady=2)
        ttk.Button(left_panel, text="Test Animation", command=self.test_animation).pack(pady=2)
        
        # Debug info
        self.debug_text = tk.Text(left_panel, width=40, height=20)
        self.debug_text.pack(pady=10)
        
        # Right panel for poker widget
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Poker widget container
        self.poker_container = ttk.Frame(right_panel)
        self.poker_container.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = ttk.Label(right_panel, text="Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)
    
    def load_sample_hand(self):
        """Load a sample legendary hand for testing."""
        try:
            # Load all hands
            all_hands = self.hands_database.load_all_hands()
            legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
            
            if not legendary_hands:
                self.log("❌ No legendary hands found")
                return
            
            # Get the first hand
            self.current_hand = legendary_hands[0]
            self.log(f"✅ Loaded hand: {self.current_hand.metadata.name}")
            self.log(f"📊 Hand data: {len(self.current_hand.players)} players")
            
            # Show hand details
            for i, player in enumerate(self.current_hand.players):
                cards = player.get('cards', [])
                self.log(f"👤 Player {i+1}: {player.get('name', f'Player {i+1}')} - Cards: {cards}")
            
            # Show board cards
            board = self.current_hand.board
            if board:
                self.log(f"🃏 Board cards: {board}")
            
            self.status_label.config(text=f"Loaded: {self.current_hand.metadata.name}")
            
        except Exception as e:
            self.log(f"❌ Error loading hand: {e}")
            import traceback
            traceback.print_exc()
    
    def start_simulation(self):
        """Start the hand simulation."""
        if not self.current_hand:
            self.log("❌ No hand loaded")
            return
        
        try:
            self.log("🎯 Starting simulation...")
            
            # Create FPSM
            config = GameConfig(num_players=6, test_mode=True, show_all_cards=True)
            self.fpsm = FlexiblePokerStateMachine(config)
            
            # Setup hand
            self.setup_hand_for_simulation()
            
            # Create poker widget
            if self.poker_widget:
                self.poker_widget.destroy()
            
            self.poker_widget = ReusablePokerGameWidget(self.poker_container, state_machine=self.fpsm)
            self.poker_widget.pack(fill=tk.BOTH, expand=True)
            
            # Force initial display
            self.poker_widget.update_display("full_update")
            self.poker_widget.reveal_all_cards()
            
            self.log("✅ Simulation started")
            self.status_label.config(text="Simulation active")
            
        except Exception as e:
            self.log(f"❌ Error starting simulation: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_hand_for_simulation(self):
        """Setup the hand for simulation."""
        if not self.current_hand:
            return
        
        try:
            self.log(f"🎯 Setting up hand: {self.current_hand.metadata.name}")
            
            # Get hand data
            players = self.current_hand.players
            board = self.current_hand.board
            actions = self.current_hand.actions
            
            self.log(f"📊 Players: {len(players)}, Board: {board}, Actions: {len(actions)}")
            
            # Create FPSM players
            fpsm_players = []
            for i, player_info in enumerate(players):
                cards = player_info.get('cards', [])
                if not cards:
                    # Use sample cards if none found
                    sample_cards = [["Ah", "Ks"], ["Qd", "Jc"], ["Th", "9s"], 
                                   ["8d", "7c"], ["6h", "5s"], ["4d", "3c"]]
                    cards = sample_cards[i] if i < len(sample_cards) else []
                
                player = Player(
                    name=player_info.get('name', f"Player {i+1}"),
                    stack=player_info.get('starting_stack_chips', 1000.0),
                    position=player_info.get('position', ''),
                    is_human=False,
                    is_active=True,
                    cards=cards
                )
                fpsm_players.append(player)
                self.log(f"👤 Created player {i}: {player.name} with cards: {cards}")
            
            # Start hand
            self.fpsm.start_hand(existing_players=fpsm_players)
            
            # Set board cards
            if board:
                board_cards = []
                for street in ['flop', 'turn', 'river']:
                    if street in board:
                        board_cards.extend(board[street])
                
                if board_cards:
                    self.fpsm.set_board_cards(board_cards)
                    self.log(f"✅ Set board cards: {board_cards}")
            
            # Set player cards in FPSM (widget will be updated automatically)
            for i, player in enumerate(fpsm_players):
                if hasattr(player, 'cards') and player.cards:
                    self.log(f"🎴 Setting cards for player {i}: {player.cards}")
                    self.fpsm.set_player_cards(i, player.cards)
            
            self.log("✅ Hand setup complete")
            
        except Exception as e:
            self.log(f"❌ Error setting up hand: {e}")
            import traceback
            traceback.print_exc()
    
    def next_action(self):
        """Execute the next action."""
        if not self.fpsm:
            self.log("❌ No simulation active")
            return
        
        try:
            # Get current game state
            game_info = self.fpsm.get_game_info()
            current_player = game_info.get('current_player')
            
            if current_player is None:
                self.log("❌ No current player")
                return
            
            # Get valid actions
            valid_actions = self.fpsm.get_valid_actions_for_player(current_player)
            self.log(f"🎯 Current player: {current_player}, Valid actions: {valid_actions}")
            
            # Determine next action
            action = self.determine_next_action(current_player, valid_actions)
            if action:
                self.log(f"🎬 Executing action: {action}")
                self.fpsm.execute_action(action)
                self.action_history.append(action)
                
                # Update display
                if self.poker_widget:
                    self.poker_widget.update_display("action_executed")
            else:
                self.log("❌ No valid action found")
                
        except Exception as e:
            self.log(f"❌ Error executing action: {e}")
            import traceback
            traceback.print_exc()
    
    def determine_next_action(self, player_index, valid_actions):
        """Determine the next action to execute."""
        if not self.current_hand or not self.current_hand.actions:
            return self.get_default_action(valid_actions)
        
        try:
            # Get all actions from the hand
            all_actions = []
            for street, actions in self.current_hand.actions.items():
                for action in actions:
                    all_actions.append(action)
            
            # Get the next action based on history
            if len(self.action_history) < len(all_actions):
                next_action_data = all_actions[len(self.action_history)]
                action_type = next_action_data.get('type', 'fold')
                amount = next_action_data.get('amount', 0)
                
                # Convert to ActionType
                if action_type == 'fold':
                    return ActionType.FOLD
                elif action_type == 'call':
                    return ActionType.CALL
                elif action_type == 'check':
                    return ActionType.CHECK
                elif action_type in ['bet', 'raise']:
                    return ActionType.RAISE
                else:
                    return ActionType.FOLD
            
        except Exception as e:
            self.log(f"⚠️ Error determining action from history: {e}")
        
        return self.get_default_action(valid_actions)
    
    def get_default_action(self, valid_actions):
        """Get a default action if no historical action is found."""
        if ActionType.CHECK in valid_actions:
            return ActionType.CHECK
        elif ActionType.CALL in valid_actions:
            return ActionType.CALL
        elif ActionType.BET in valid_actions:
            return ActionType.BET
        elif ActionType.RAISE in valid_actions:
            return ActionType.RAISE
        elif ActionType.FOLD in valid_actions:
            return ActionType.FOLD
        return None
    
    def force_card_display(self):
        """Force display of all cards."""
        if not self.poker_widget:
            self.log("❌ No poker widget")
            return
        
        try:
            self.log("🎴 Forcing card display...")
            
            # Force reveal all cards
            self.poker_widget.reveal_all_cards()
            
            # Force update display
            self.poker_widget.update_display("full_update")
            
            # Force canvas update
            if hasattr(self.poker_widget, 'canvas'):
                self.poker_widget.canvas.update()
            
            self.log("✅ Card display forced")
            
        except Exception as e:
            self.log(f"❌ Error forcing card display: {e}")
            import traceback
            traceback.print_exc()
    
    def test_animation(self):
        """Test animation system."""
        if not self.poker_widget:
            self.log("❌ No poker widget")
            return
        
        try:
            self.log("🎬 Testing animation...")
            
            # Test bet animation
            self.poker_widget.show_bet_display(0, "TEST", 100)
            
            # Test bet to pot animation
            self.poker_widget._animate_bet_to_pot(0, 100)
            
            self.log("✅ Animation test completed")
            
        except Exception as e:
            self.log(f"❌ Error testing animation: {e}")
            import traceback
            traceback.print_exc()
    
    def show_debug_info(self):
        """Show comprehensive debug information."""
        if not self.current_hand:
            self.log("❌ No hand loaded")
            return
        
        try:
            self.log("🔍 Debug Information:")
            self.log(f"  Hand: {self.current_hand.metadata.name}")
            self.log(f"  Players: {len(self.current_hand.players)}")
            
            for i, player in enumerate(self.current_hand.players):
                cards = player.get('cards', [])
                self.log(f"    Player {i+1}: {player.get('name', f'Player {i+1}')} - Cards: {cards}")
            
            if self.fpsm:
                game_info = self.fpsm.get_game_info()
                self.log(f"  FPSM State: {game_info.get('current_state', 'Unknown')}")
                self.log(f"  Current Player: {game_info.get('current_player', 'None')}")
                self.log(f"  Pot: {game_info.get('pot', 0)}")
            
            if self.poker_widget:
                self.log("  Poker Widget: Active")
            else:
                self.log("  Poker Widget: Not created")
            
        except Exception as e:
            self.log(f"❌ Error showing debug info: {e}")
    
    def log(self, message):
        """Log a message to the debug text area."""
        self.debug_text.insert(tk.END, f"{message}\n")
        self.debug_text.see(tk.END)
        print(message)
    
    def run(self):
        """Run the debug tester."""
        self.root.mainloop()

if __name__ == "__main__":
    tester = ComprehensiveDebugTester()
    tester.run()
