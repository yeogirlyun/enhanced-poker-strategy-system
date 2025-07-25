# filename: player.py
"""
Player Module for the Advanced Hold'em Trainer

REVISION HISTORY:
================
Version 1.0 (2025-07-26) - Initial Refactoring
- Created the `player.py` module as part of a major OOP refactoring.
- Moved the `Player` class from `integrated_trainer.py` into this module.
- Created subclasses `UserPlayer` and `BotPlayer` to separate user input
  logic from the AI's strategic decision-making process. This improves
  modularity and adheres to the Single Responsibility Principle.
- The `get_action` method is now specialized in the subclasses.

This module isolates all player-related logic, making the main trainer
file cleaner and more focused on orchestration.
"""

from abc import ABC, abstractmethod

# Assuming Colors class and get_optimal_action will be in their own utility/engine modules
# For now, we define them here for simplicity until the full refactoring is complete.
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class Player(ABC):
    """
    Abstract base class for a poker player.
    Represents a player at the table with a fixed seat, stack, and hand.
    """
    def __init__(self, name, seat_number):
        self.name = name
        self.seat_number = seat_number  # FIXED seat at the table (0-8)
        self.stack = 100.0
        self.hole = []
        self.is_active = True
        self.contributed_this_street = 0
        self.was_aggressor = False
        self.current_position = None  # This will be updated each hand by the Table class

    def __repr__(self):
        return (f"Player(name={self.name}, seat={self.seat_number}, "
                f"stack={self.stack:.1f}, pos={self.current_position})")

    def reset_for_hand(self):
        """Resets player state for the start of a new hand."""
        self.hole = []
        self.is_active = True
        self.contributed_this_street = 0
        self.was_aggressor = False
        # Reload stack if it's too low
        if self.stack < 1.0:
            print(f"{Colors.YELLOW}Player at seat #{self.seat_number} reloaded to 100 BB{Colors.END}")
            self.stack = 100.0

    @abstractmethod
    def get_action(self, game_state, strategy, hand_evaluator):
        """
        Abstract method to get the player's action.
        Must be implemented by subclasses.
        """
        pass

class BotPlayer(Player):
    """
    Represents an AI player that executes decisions based on the loaded strategy.
    """
    def __init__(self, seat_number):
        super().__init__(f"P{seat_number}", seat_number)

    def get_action(self, game_state, strategy, decision_engine):
        """
        Gets the optimal action from the decision engine for the bot.
        
        Args:
            game_state (dict): The current state of the game.
            strategy (dict): The loaded strategy configuration.
            decision_engine (DecisionEngine): The engine to calculate the optimal action.

        Returns:
            tuple: A tuple containing the action (str) and size (float).
        """
        # The bot player will use the decision engine to get the perfect strategic move.
        return decision_engine.get_optimal_action(game_state, strategy)

class UserPlayer(Player):
    """
    Represents the human user, handling input and displaying information.
    """
    def __init__(self, seat_number):
        super().__init__("You", seat_number)

    def get_action(self, game_state, strategy, decision_engine):
        """
        Prompts the human user for their action and returns it.
        This method will be called by the game engine when it's the user's turn.
        
        Args:
            game_state (dict): The current state of the game.
            strategy (dict): The loaded strategy configuration.
            decision_engine (DecisionEngine): The engine (used here for providing hints if needed).

        Returns:
            tuple: A tuple containing the action (str) and size (float).
        """
        # This UI logic will be moved to a dedicated UI class in the final refactoring.
        # For now, it lives here to keep the player self-contained.
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        
        hand_str = f"{Colors.BOLD}{' '.join(self.hole)}{Colors.END}"
        hs_val = game_state.get('dynamic_hs', 0) if game_state.get('street') != 'preflop' else game_state.get('preflop_hs', 0)
        
        hs_color = Colors.GREEN if hs_val >= 80 else Colors.YELLOW if hs_val >= 60 else Colors.BLUE if hs_val >= 40 else Colors.RED
        
        print(f"Your Hand: {hand_str} (HS: {hs_color}{hs_val}{Colors.END})")
        print(f"Your Seat: #{self.seat_number} | Current Position: {Colors.BLUE}{self.current_position}{Colors.END}")
        
        if game_state.get('street') != 'preflop' and 'postflop_details' in game_state:
            details = game_state['postflop_details']
            print(f"Hand Type: {Colors.CYAN}{details.get('rank', 'unknown').replace('_', ' ').title()}{Colors.END}")
            if details.get('is_draw'):
                print(f"Draw: {Colors.PURPLE}Yes{Colors.END} (Outs: {details.get('outs', 0)})")
            if 'board_texture' in details:
                print(f"Board Texture: {Colors.YELLOW}{details['board_texture'].title()}{Colors.END}")
            if 'equity_estimate' in details:
                equity = details['equity_estimate']
                equity_color = Colors.GREEN if equity >= 60 else Colors.YELLOW if equity >= 40 else Colors.RED
                print(f"Estimated Equity: {equity_color}{equity:.1f}%{Colors.END}")
        
        if game_state.get('board'): 
            board_str = f"{Colors.YELLOW}{' '.join(game_state['board'])}{Colors.END}"
            print(f"Board: {board_str}")
        
        print(f"Pot: {Colors.GREEN}{game_state.get('pot', 0):.1f} BB{Colors.END} | "
              f"To Call: {Colors.RED if game_state.get('to_call', 0) > 0 else Colors.GREEN}{game_state.get('to_call', 0):.1f} BB{Colors.END}")
        print(f"Stack: {Colors.CYAN}{self.stack:.1f} BB{Colors.END}")
        
        available_actions = []
        if game_state.get('to_call', 0) == 0:
            available_actions.extend([f"{Colors.CYAN}check (k){Colors.END}", f"{Colors.GREEN}bet (b){Colors.END}"])
        else:
            available_actions.extend([
                f"{Colors.RED}fold (f){Colors.END}", 
                f"{Colors.YELLOW}call (c){Colors.END}", 
                f"{Colors.GREEN}raise (r){Colors.END}"
            ])
        
        print(f"Available actions: {', '.join(available_actions)}")
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        while True:
            user_input = input(f"\n{Colors.BOLD}Your action: {Colors.END}").lower().strip()
            action = action_map.get(user_input)
            if not action: 
                print(f"{Colors.RED}Invalid action. Try again.{Colors.END}")
                continue
            if action in ['bet', 'raise']:
                try: 
                    size = float(input("Enter size in BB: "))
                    return action, size
                except ValueError:
                    print(f"{Colors.RED}Invalid size. Try again.{Colors.END}")
                    continue
            return action, 0
