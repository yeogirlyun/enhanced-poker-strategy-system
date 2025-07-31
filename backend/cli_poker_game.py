#!/usr/bin/env python3
"""
CLI Poker Game

A command-line interface poker game that uses the same state machine
as the GUI version for testing and debugging.
"""

import time
import random
from poker_state_machine import PokerStateMachine, PokerState, ActionType
from gui_models import StrategyData


class CLIPokerGame:
    """Command-line poker game using the state machine."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.state_machine = PokerStateMachine(num_players=6)
        
        # Set up callbacks
        self.state_machine.on_action_required = self._handle_human_action_required
        self.state_machine.on_hand_complete = self._handle_hand_complete
        self.state_machine.on_round_complete = self._handle_round_complete
        
        # Game state
        self.current_game_state = None
        self.hand_number = 0
        
    def _handle_human_action_required(self, player):
        """Handle when human action is required."""
        self.current_game_state = self.state_machine.game_state
        self._display_game_state()
        self._get_human_action(player)
    
    def _handle_hand_complete(self):
        """Handle when hand is complete."""
        self.current_game_state = self.state_machine.game_state
        print("\n" + "="*50)
        print("HAND COMPLETE!")
        self._display_final_state()
        print("="*50 + "\n")
        self.hand_number += 1
    
    def _handle_round_complete(self):
        """Handle when round is complete."""
        self.current_game_state = self.state_machine.game_state
        print(f"\n--- ROUND COMPLETE: {self.state_machine.get_current_state()} ---")
    
    def _display_game_state(self):
        """Display the current game state."""
        if not self.current_game_state:
            return
            
        print("\n" + "-"*60)
        print(f"STATE: {self.state_machine.get_current_state()}")
        print(f"POT: ${self.current_game_state.pot:.2f}")
        print(f"CURRENT BET: ${self.current_game_state.current_bet:.2f}")
        print(f"BOARD: {self._format_cards(self.current_game_state.board)}")
        print("-"*60)
        
        # Display players
        current_player = self.state_machine.get_action_player()
        for i, player in enumerate(self.current_game_state.players):
            status = "ACTIVE" if player.is_active else "FOLDED"
            turn_indicator = " ← YOUR TURN" if player == current_player else ""
            bet_info = f" (Bet: ${player.current_bet:.2f})" if player.current_bet > 0 else ""
            
            print(f"{player.name} ({player.position}): ${player.stack:.2f} - {status}{bet_info}{turn_indicator}")
            
            if player.is_human and player.is_active:
                print(f"  Your cards: {self._format_cards(player.cards)}")
    
    def _display_final_state(self):
        """Display the final state of the hand."""
        if not self.current_game_state:
            return
            
        print(f"FINAL POT: ${self.current_game_state.pot:.2f}")
        print(f"FINAL BOARD: {self._format_cards(self.current_game_state.board)}")
        
        # Show all active players' cards
        active_players = [p for p in self.current_game_state.players if p.is_active]
        for player in active_players:
            print(f"{player.name}: {self._format_cards(player.cards)}")
    
    def _format_cards(self, cards):
        """Format cards for display."""
        if not cards:
            return "[]"
        
        suit_symbols = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}
        formatted = []
        for card in cards:
            rank, suit = card[0], card[1]
            suit_symbol = suit_symbols[suit]
            color = "red" if suit in ["h", "d"] else "black"
            formatted.append(f"{rank}{suit_symbol}")
        
        return " ".join(formatted)
    
    def _get_human_action(self, player):
        """Get human action from command line."""
        print(f"\n🎯 YOUR TURN ({player.name})")
        print("Available actions:")
        
        # Determine valid actions
        valid_actions = []
        if self.state_machine.get_current_state() == PokerState.PREFLOP_BETTING:
            valid_actions = ["fold", "call", "raise"]
        else:
            if self.current_game_state.current_bet == 0:
                valid_actions = ["check", "bet"]
            else:
                valid_actions = ["fold", "call", "raise"]
        
        print(f"  Valid: {', '.join(valid_actions)}")
        
        # Get action
        while True:
            action = input("Enter action: ").lower().strip()
            if action in valid_actions:
                break
            print(f"Invalid action. Valid actions: {', '.join(valid_actions)}")
        
        # Get amount for betting actions
        amount = 0
        if action in ["bet", "raise"]:
            while True:
                try:
                    amount = float(input(f"Enter {action} amount: $"))
                    if amount > 0:
                        break
                    print("Amount must be greater than 0")
                except ValueError:
                    print("Please enter a valid number")
        
        # Convert to ActionType and execute
        action_type = None
        if action == "fold":
            action_type = ActionType.FOLD
        elif action == "check":
            action_type = ActionType.CHECK
        elif action == "call":
            action_type = ActionType.CALL
        elif action == "bet":
            action_type = ActionType.BET
        elif action == "raise":
            action_type = ActionType.RAISE
        
        if action_type:
            print(f"Executing: {action.upper()} ${amount:.2f}")
            self.state_machine.execute_action(player, action_type, amount)
    
    def start_hand(self):
        """Start a new hand."""
        print(f"\n🎮 STARTING HAND #{self.hand_number + 1}")
        print("="*60)
        
        # Start the state machine
        self.state_machine.start_hand()
        self.current_game_state = self.state_machine.game_state
        
        # Deal hole cards
        deck = self._create_deck()
        random.shuffle(deck)
        for player in self.current_game_state.players:
            player.cards = [deck.pop(), deck.pop()]
        
        # Display initial state
        self._display_game_state()
        
        # Let the state machine handle the first action
        self.state_machine.handle_current_player_action()
    
    def _create_deck(self):
        """Create a standard 52-card deck."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        suits = ["h", "d", "c", "s"]
        deck = []
        for rank in ranks:
            for suit in suits:
                deck.append(f"{rank}{suit}")
        return deck
    
    def run_game(self, num_hands=3):
        """Run the poker game for a specified number of hands."""
        print("🎰 CLI POKER GAME")
        print("="*60)
        print(f"Strategy: {self.strategy_data.strategy_file if hasattr(self.strategy_data, 'strategy_file') else 'modern_strategy.json'}")
        print(f"Players: 6 (1 human + 5 bots)")
        print(f"Hands to play: {num_hands}")
        print("="*60)
        
        for i in range(num_hands):
            self.start_hand()
            
            if i < num_hands - 1:
                input("\nPress Enter to start next hand...")
        
        print("\n🎉 GAME COMPLETE!")
        print("="*60)


def main():
    """Main function to run the CLI poker game."""
    # Load strategy data
    strategy_data = StrategyData()
    try:
        strategy_data.load_strategy_from_file("modern_strategy.json")
        print("✅ Strategy loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load strategy: {e}")
        return
    
    # Create and run the game
    game = CLIPokerGame(strategy_data)
    
    try:
        game.run_game(num_hands=3)
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted by user")
    except Exception as e:
        print(f"\n❌ Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 