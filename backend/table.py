# filename: table.py
"""
Table Module for the Advanced Hold'em Trainer

REVISION HISTORY:
================
Version 1.0 (2025-07-26) - Initial Refactoring
- Created the `table.py` module as part of a major OOP refactoring.
- The new `Table` class encapsulates all logic related to managing players,
  seats, the dealer button, and positional awareness.
- Moved position calculation and action order logic from `integrated_trainer.py`
  into this class.
- The `Table` class now manages the collection of Player objects.

This module is responsible for the physical and logical layout of the game,
further separating concerns from the main game-flow orchestrator.
"""
import random
from player import Player, UserPlayer, BotPlayer

class Table:
    """
    Manages the poker table, including players, seats, and positions.
    """
    def __init__(self, num_players=6):
        if not 3 <= num_players <= 9:
            raise ValueError("Number of players must be between 3 and 9.")
        
        self.num_players = num_players
        self.players = []
        self.dealer_seat = -1 # Starts at -1, will be 0 for the first hand
        self.user_player = None

        self._setup_seats()

    def _setup_seats(self):
        """Creates players and assigns them to fixed seats."""
        player_list = []
        for i in range(self.num_players):
            player_list.append(BotPlayer(seat_number=i))

        # Randomly assign one player to be the user
        user_seat_index = random.randint(0, self.num_players - 1)
        user_player = UserPlayer(seat_number=user_seat_index)
        player_list[user_seat_index] = user_player
        self.user_player = user_player
        
        self.players = player_list

    def move_dealer_button(self):
        """Moves the dealer button to the next active player."""
        self.dealer_seat = (self.dealer_seat + 1) % self.num_players
        self._update_all_player_positions()

    def _update_all_player_positions(self):
        """Updates the `current_position` attribute for every player on the table."""
        for player in self.players:
            player.current_position = self._get_position_for_seat(player.seat_number)

    def get_player_at_seat(self, seat_number):
        """Gets the player at a specific seat number."""
        return self.players[seat_number]

    def get_player_at_position(self, position):
        """Gets the player currently at a specific position."""
        for player in self.players:
            if player.current_position == position:
                return player
        return None

    def get_active_players(self):
        """Returns a list of players still active in the hand."""
        return [p for p in self.players if p.is_active]

    def get_action_order(self, street='preflop'):
        """
        Gets the correct list of players to act, in order, for the current street.
        """
        if self.num_players == 9:
            pos_order = ['UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO', 'BTN']
        elif self.num_players == 8:
            pos_order = ['UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO', 'BTN']
        elif self.num_players == 7:
            pos_order = ['UTG', 'UTG+1', 'MP', 'CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'UTG', 'UTG+1', 'MP', 'CO', 'BTN']
        elif self.num_players == 6:
            pos_order = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'UTG', 'MP', 'CO', 'BTN']
        elif self.num_players == 5:
            pos_order = ['CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'CO', 'BTN']
        elif self.num_players == 4:
            pos_order = ['CO', 'BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'CO', 'BTN']
        else: # 3-handed
            pos_order = ['BTN', 'SB', 'BB'] if street == 'preflop' else ['SB', 'BB', 'BTN']
        
        # Return a list of player objects in the correct order
        action_list = []
        for pos in pos_order:
            player = self.get_player_at_position(pos)
            if player and player.is_active:
                action_list.append(player)
        return action_list

    def _get_position_for_seat(self, seat_number):
        """Calculates the position name for a given seat based on dealer location."""
        # Positions are defined relative to the button.
        # BTN is at index 0, SB is at 1, BB is at 2, etc.
        if self.num_players == 9:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO']
        elif self.num_players == 8:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO']
        elif self.num_players == 7:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'CO']
        elif self.num_players == 6:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        elif self.num_players == 5:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'CO'] # UTG/CO are same
        elif self.num_players == 4:
            positions = ['BTN', 'SB', 'BB', 'CO']
        else: # 3-handed
            positions = ['BTN', 'SB', 'BB']
        
        # Calculate the seat's offset from the dealer button
        position_index = (seat_number - self.dealer_seat + self.num_players) % self.num_players
        return positions[position_index]

