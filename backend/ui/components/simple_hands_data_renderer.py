#!/usr/bin/env python3
"""
Simple Hands Data Renderer

This class processes hand data into step-by-step display states.
It's purely data processing - no game logic, no state machines.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DisplayStep:
    """A single step in the hand review sequence."""
    step_number: int
    street: str  # preflop, flop, turn, river, showdown
    action_description: str
    board_cards: List[str]
    pot_amount: float
    current_bet: float
    players: List[Dict[str, Any]]
    dealer_position: int
    action_player: Optional[int]
    street_completed: bool


class SimpleHandsDataRenderer:
    """
    Simple data renderer that processes hand data into display steps.
    
    This class:
    - Parses hand data from ParsedHand objects
    - Creates step-by-step display states
    - Provides navigation between steps
    - NO game logic, just data processing
    """

    def __init__(self, parsed_hand):
        """Initialize with ParsedHand object."""
        self.parsed_hand = parsed_hand
        self.steps: List[DisplayStep] = []
        self.current_step_index = 0
        
        # Process the hand data into steps
        self._process_hand_data()

    def _process_hand_data(self):
        """Process hand data into display steps."""
        # Extract basic hand info from ParsedHand
        game_info = self.parsed_hand.game_info
        players = self.parsed_hand.players
        actions = self.parsed_hand.actions
        board = self.parsed_hand.board
        
        num_players = len(players)  # Use actual player count
        pot = game_info.get('pot', 0.0) if game_info else 0.0
        
        # Step 0: Initial state (all players seated, no actions yet)
        initial_players = self._create_initial_player_states(players, num_players)
        initial_step = DisplayStep(
            step_number=0,
            street="preflop",
            action_description="Hand begins - all players seated",
            board_cards=[],
            pot_amount=0.0,
            current_bet=0.0,
            players=initial_players,
            dealer_position=0,  # Default dealer position
            action_player=None,
            street_completed=False
        )
        self.steps.append(initial_step)

        # Process each street
        streets = ['preflop', 'flop', 'turn', 'river']
        step_number = 1
        
        for street in streets:
            if street in actions:
                street_actions = actions[street]
                if isinstance(street_actions, list):
                    # Process each action in the street
                    for i, action in enumerate(street_actions):
                        # Create step for this action
                        step = self._create_action_step(
                            step_number, street, action, i, len(street_actions),
                            board, pot, players, num_players
                        )
                        self.steps.append(step)
                        step_number += 1
                        
                        # Check if this completes the street
                        if i == len(street_actions) - 1:
                            # Street completed
                            step.street_completed = True
                            step.action_description += f" - {street.title()} complete"

        # Final step: Showdown
        if self.steps:
            final_step = DisplayStep(
                step_number=step_number,
                street="showdown",
                action_description="Showdown - determining winner",
                board_cards=self._get_final_board_cards(board),
                pot_amount=pot,
                current_bet=0.0,
                players=self._get_final_player_states(players, pot),
                dealer_position=0,
                action_player=None,
                street_completed=True
            )
            self.steps.append(final_step)

    def _create_initial_player_states(self, players_data: List[Dict], 
                                    num_players: int) -> List[Dict[str, Any]]:
        """Create initial player states for the beginning of the hand."""
        player_states = []
        
        for i in range(num_players):
            if i < len(players_data):
                player_data = players_data[i]
                # Handle both old and new data structures
                cards = player_data.get('cards', []) or player_data.get('hole_cards', [])
                stack = player_data.get('stack', 200.0)
                bet = player_data.get('bet', 0.0) or player_data.get('current_bet', 0.0)
                folded = player_data.get('folded', False) or player_data.get('has_folded', False)
                
                player_states.append({
                    'index': i,
                    'name': player_data.get('name', f'Player {i}'),
                    'cards': cards,
                    'stack': stack,
                    'bet': bet,
                    'folded': folded,
                    'all_in': False,
                    'position': self._get_position_name(i, num_players)
                })
            else:
                # Create default player if data missing
                player_states.append({
                    'index': i,
                    'name': f'Player {i}',
                    'cards': [],
                    'stack': 200.0,
                    'bet': 0.0,
                    'folded': False,
                    'all_in': False,
                    'position': self._get_position_name(i, num_players)
                })
        
        return player_states

    def _create_action_step(self, step_number: int, street: str, action: Dict, 
                           action_index: int, total_actions: int, board: Dict, 
                           pot: float, players_data: List[Dict], 
                           num_players: int) -> DisplayStep:
        """Create a step for a specific action."""
        # Extract action info - handle both old and new formats
        player_index = action.get('player', action.get('actor', 0))
        action_type = action.get('action', action.get('action_type', 'unknown'))
        amount = action.get('amount', 0.0)
        
        # Create action description
        action_desc = f"{street.title()}: Player {player_index} {action_type}"
        if amount > 0:
            action_desc += f" ${amount}"
        
        # Update player states based on this action
        updated_players = self._update_player_states_for_action(
            players_data, player_index, action_type, amount, street
        )
        
        # Get board cards for this street
        board_cards = self._get_board_cards_for_street(board, street)
        
        # Calculate current pot and bet
        current_pot = self._calculate_pot_up_to_action(players_data, 
                                                     action_index, street)
        current_bet = amount if action_type in ['bet', 'raise'] else 0.0
        
        return DisplayStep(
            step_number=step_number,
            street=street,
            action_description=action_desc,
            board_cards=board_cards,
            pot_amount=current_pot,
            current_bet=current_bet,
            players=updated_players,
            dealer_position=0,
            action_player=player_index,
            street_completed=action_index == total_actions - 1
        )

    def _update_player_states_for_action(self, players_data: List[Dict], 
                                       player_index: int, action_type: str, 
                                       amount: float, street: str) -> List[Dict[str, Any]]:
        """Update player states based on an action."""
        updated_players = []
        
        for i, player_data in enumerate(players_data):
            if i == player_index:
                # Update the acting player
                current_bet = player_data.get('bet', 0.0)
                stack = player_data.get('stack', 200.0)
                
                if action_type == 'fold':
                    updated_players.append({
                        'index': i,
                        'name': player_data.get('name', f'Player {i}'),
                        'cards': player_data.get('cards', []),
                        'stack': stack,
                        'bet': current_bet,
                        'folded': True,
                        'all_in': False,
                        'position': self._get_position_name(i, len(players_data))
                    })
                elif action_type in ['bet', 'raise']:
                    new_bet = current_bet + amount
                    updated_players.append({
                        'index': i,
                        'name': player_data.get('name', f'Player {i}'),
                        'cards': player_data.get('cards', []),
                        'stack': stack - amount,
                        'bet': new_bet,
                        'folded': False,
                        'all_in': (stack - amount) <= 0,
                        'position': self._get_position_name(i, len(players_data))
                    })
                else:  # check, call
                    updated_players.append({
                        'index': i,
                        'name': player_data.get('name', f'Player {i}'),
                        'cards': player_data.get('cards', []),
                        'stack': stack,
                        'bet': current_bet,
                        'folded': False,
                        'all_in': False,
                        'position': self._get_position_name(i, len(players_data))
                    })
            else:
                # Keep other players unchanged
                updated_players.append({
                    'index': i,
                    'name': player_data.get('name', f'Player {i}'),
                    'cards': player_data.get('cards', []),
                    'stack': player_data.get('stack', 200.0),
                    'bet': player_data.get('bet', 0.0),
                    'folded': player_data.get('folded', False),
                    'all_in': player_data.get('all_in', False),
                    'position': self._get_position_name(i, len(players_data))
                })
        
        return updated_players

    def _get_board_cards_for_street(self, board: Dict, street: str) -> List[str]:
        """Get board cards for a specific street."""
        if street == 'preflop':
            return []
        elif street == 'flop':
            return board.get('flop', [])
        elif street == 'turn':
            flop = board.get('flop', [])
            turn = board.get('turn', [])
            return flop + turn
        elif street == 'river':
            flop = board.get('flop', [])
            turn = board.get('turn', [])
            river = board.get('river', [])
            return flop + turn + river
        else:
            return []

    def _get_final_board_cards(self, board: Dict) -> List[str]:
        """Get all board cards for showdown."""
        all_cards = []
        for street in ['flop', 'turn', 'river']:
            if street in board:
                all_cards.extend(board[street])
        return all_cards

    def _calculate_pot_up_to_action(self, players_data: List[Dict], 
                                   action_index: int, street: str) -> float:
        """Calculate pot amount up to a specific action."""
        # Simple calculation - could be enhanced
        total_bets = sum(player.get('bet', 0.0) for player in players_data)
        return total_bets

    def _get_final_player_states(self, players_data: List[Dict], 
                                pot: float) -> List[Dict[str, Any]]:
        """Get final player states for showdown."""
        final_players = []
        
        for i, player_data in enumerate(players_data):
            final_players.append({
                'index': i,
                'name': player_data.get('name', f'Player {i}'),
                'cards': player_data.get('cards', []),
                'stack': player_data.get('stack', 200.0),
                'bet': player_data.get('bet', 0.0),
                'folded': player_data.get('folded', False),
                'all_in': player_data.get('all_in', False),
                'position': self._get_position_name(i, len(players_data))
            })
        
        return final_players

    def _get_position_name(self, player_index: int, num_players: int) -> str:
        """Get position name for a player."""
        if num_players == 2:
            return "BB" if player_index == 0 else "BTN"
        elif num_players == 6:
            positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
            return positions[player_index] if player_index < len(positions) else "Unknown"
        else:
            return f"Pos {player_index}"

    # Navigation methods
    def get_current_step(self) -> DisplayStep:
        """Get the current display step."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return self.steps[0] if self.steps else None

    def get_total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.steps)

    def get_current_action_description(self) -> str:
        """Get description of current action."""
        current_step = self.get_current_step()
        return current_step.action_description if current_step else "No action"

    def go_to_first(self):
        """Go to the first step."""
        self.current_step_index = 0

    def go_to_previous(self):
        """Go to the previous step."""
        if self.current_step_index > 0:
            self.current_step_index -= 1

    def go_to_next(self):
        """Go to the next step."""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1

    def go_to_last(self):
        """Go to the last step."""
        self.current_step_index = len(self.steps) - 1

    def go_to_step(self, step_number: int):
        """Go to a specific step."""
        if 0 <= step_number < len(self.steps):
            self.current_step_index = step_number
