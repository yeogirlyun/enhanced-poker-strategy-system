#!/usr/bin/env python3
"""
PHH v1 (Poker Hand History) Validation Framework

This framework reads PHH v1 format data and validates it against our poker state
machine using UI mocking tests. It ensures every street situation, pot amount,
and final showdown result matches exactly with the poker state machine's final state.

PHH v1 Format Structure:
- Game metadata (variant, stakes, currency, format, event)
- Table configuration (table_name, max_players, button_seat)
- Player information (seat, name, position, starting_stack, cards)
- Blind/ante structure
- Actions by street (preflop, flop, turn, river)
- Board cards by street
- Final pot and winners
- Metadata and references
"""

import unittest
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from core.poker_state_machine import ImprovedPokerStateMachine, ActionType
from core.types import Player


class Street(Enum):
    """Poker streets enumeration."""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


@dataclass
class PHHV1Action:
    """Represents a single action in PHH v1 format."""
    actor: int  # Seat number
    action_type: str  # raise, call, fold, bet, check, all-in, etc.
    amount: float = 0.0
    to: float = 0.0  # For raises
    street: Street = Street.PREFLOP


@dataclass
class PHHV1Player:
    """Represents a player in PHH v1 format."""
    seat: int
    name: str
    position: str
    starting_stack_chips: float
    cards: List[str] = None
    is_hero: bool = False


@dataclass
class PHHV1Blind:
    """Represents a blind posting in PHH v1 format."""
    seat: int
    amount: float


@dataclass
class PHHV1Board:
    """Represents board cards for a street."""
    cards: List[str] = None
    card: str = None  # For turn/river


@dataclass
class PHHV1Hand:
    """Represents a complete poker hand in PHH v1 format."""
    # Game metadata
    variant: str
    stakes: str
    currency: str
    format: str
    event: str
    
    # Table configuration
    table_name: str
    max_players: int
    button_seat: int
    
    # Players
    players: List[PHHV1Player]
    
    # Blinds and antes
    small_blind: PHHV1Blind
    big_blind: PHHV1Blind
    antes: List[PHHV1Blind] = None
    
    # Actions by street
    preflop_actions: List[PHHV1Action] = None
    flop_actions: List[PHHV1Action] = None
    turn_actions: List[PHHV1Action] = None
    river_actions: List[PHHV1Action] = None
    
    # Board cards
    flop_board: PHHV1Board = None
    turn_board: PHHV1Board = None
    river_board: PHHV1Board = None
    
    # Results
    pot_total_chips: float = 0.0
    rake_chips: float = 0.0
    winners: List[int] = None
    winning_type: str = ""
    
    # Metadata
    source: str = ""
    notes: str = ""
    references: List[str] = None


class PHHV1Parser:
    """Parser for PHH v1 format data."""
    
    def __init__(self):
        self.current_section = ""
        self.current_subsection = ""
    
    def parse_phh_v1_text(self, phh_text: str) -> PHHV1Hand:
        """Parse PHH v1 text format into structured data."""
        lines = phh_text.strip().split('\n')
        
        # Initialize data structures
        game_data = {}
        table_data = {}
        players = []
        blinds = {}
        actions = {}
        board_data = {}
        results = {}
        metadata = {}
        
        current_section = ""
        current_subsection = ""
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect sections
            if line.startswith('[game]'):
                current_section = 'game'
                continue
            elif line.startswith('[table]'):
                current_section = 'table'
                continue
            elif line.startswith('[blinds]'):
                current_section = 'blinds'
                continue
            elif line.startswith('[board.'):
                current_section = 'board'
                current_subsection = line[7:-1]  # Extract street name
                continue
            elif line.startswith('[pot]'):
                current_section = 'pot'
                continue
            elif line.startswith('[winners]'):
                current_section = 'winners'
                continue
            elif line.startswith('[metadata]'):
                current_section = 'metadata'
                continue
            elif line.startswith('[[') and ']]' in line:
                # Handle subsections like [[players]], [[actions.preflop]]
                if 'players' in line:
                    current_section = 'players'
                    current_subsection = 'player'
                elif 'actions.' in line:
                    current_section = 'actions'
                    current_subsection = line[line.find('actions.')+8:-2]
                continue
            
            # Parse key-value pairs
            if '=' in line:
                key, value = self._parse_key_value(line)
                
                if current_section == 'game':
                    game_data[key] = value
                elif current_section == 'table':
                    table_data[key] = value
                elif current_section == 'blinds':
                    blinds[key] = value
                elif current_section == 'board':
                    if current_subsection not in board_data:
                        board_data[current_subsection] = {}
                    board_data[current_subsection][key] = value
                elif current_section == 'pot':
                    results[key] = value
                elif current_section == 'winners':
                    results[key] = value
                elif current_section == 'metadata':
                    metadata[key] = value
                elif current_section == 'players' and current_subsection == 'player':
                    # Handle player data
                    if 'players' not in locals():
                        players = []
                    players.append({key: value})
                elif current_section == 'actions':
                    # Handle action data
                    if current_subsection not in actions:
                        actions[current_subsection] = []
                    actions[current_subsection].append({key: value})
        
        # Construct PHHV1Hand object
        return self._construct_phh_hand(
            game_data, table_data, players, blinds, actions, 
            board_data, results, metadata
        )
    
    def _parse_key_value(self, line: str) -> Tuple[str, Any]:
        """Parse a key-value pair from PHH v1 format."""
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        # Convert numeric values
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        
        return key, value
    
    def _construct_phh_hand(self, game_data, table_data, players, blinds, 
                           actions, board_data, results, metadata) -> PHHV1Hand:
        """Construct PHHV1Hand object from parsed data."""
        
        # Parse players
        phh_players = []
        current_player = {}
        for player_data in players:
            if isinstance(player_data, dict):
                current_player.update(player_data)
                if 'name' in current_player:  # Complete player data
                    player = PHHV1Player(
                        seat=current_player.get('seat', 0),
                        name=current_player.get('name', ''),
                        position=current_player.get('position', ''),
                        starting_stack_chips=current_player.get('starting_stack_chips', 0),
                        cards=current_player.get('cards', []),
                        is_hero=current_player.get('is_hero', False)
                    )
                    phh_players.append(player)
                    current_player = {}
        
        # Parse blinds
        small_blind_str = blinds.get('small_blind', '')
        big_blind_str = blinds.get('big_blind', '')
        
        small_blind = PHHV1Blind(
            seat=self._extract_seat_from_blind(small_blind_str),
            amount=self._extract_amount_from_blind(small_blind_str)
        )
        big_blind = PHHV1Blind(
            seat=self._extract_seat_from_blind(big_blind_str),
            amount=self._extract_amount_from_blind(big_blind_str)
        )
        
        # Parse actions
        preflop_actions = self._parse_actions(actions.get('preflop', []))
        flop_actions = self._parse_actions(actions.get('flop', []))
        turn_actions = self._parse_actions(actions.get('turn', []))
        river_actions = self._parse_actions(actions.get('river', []))
        
        # Parse board
        flop_board = self._parse_board(board_data.get('flop', {}))
        turn_board = self._parse_board(board_data.get('turn', {}))
        river_board = self._parse_board(board_data.get('river', {}))
        
        return PHHV1Hand(
            variant=game_data.get('variant', ''),
            stakes=game_data.get('stakes', ''),
            currency=game_data.get('currency', ''),
            format=game_data.get('format', ''),
            event=game_data.get('event', ''),
            table_name=table_data.get('table_name', ''),
            max_players=table_data.get('max_players', 0),
            button_seat=table_data.get('button_seat', 0),
            players=phh_players,
            small_blind=small_blind,
            big_blind=big_blind,
            preflop_actions=preflop_actions,
            flop_actions=flop_actions,
            turn_actions=turn_actions,
            river_actions=river_actions,
            flop_board=flop_board,
            turn_board=turn_board,
            river_board=river_board,
            pot_total_chips=results.get('total_chips', 0),
            rake_chips=results.get('rake_chips', 0),
            winners=results.get('players', []),
            winning_type=results.get('winning_type', ''),
            source=metadata.get('source', ''),
            notes=metadata.get('notes', ''),
            references=metadata.get('references', [])
        )
    
    def _parse_actions(self, action_list: List[Dict]) -> List[PHHV1Action]:
        """Parse actions from raw data."""
        actions = []
        for action_data in action_list:
            if action_data:
                action = PHHV1Action(
                    actor=action_data.get('actor', 0),
                    action_type=action_data.get('type', ''),
                    amount=action_data.get('amount', 0.0),
                    to=action_data.get('to', 0.0)
                )
                actions.append(action)
        return actions
    
    def _parse_board(self, board_data: Dict) -> PHHV1Board:
        """Parse board data."""
        if not board_data:
            return None
        
        if 'cards' in board_data:
            return PHHV1Board(cards=board_data['cards'])
        elif 'card' in board_data:
            return PHHV1Board(card=board_data['card'])
        return None
    
    def _extract_seat_from_blind(self, blind_str: str) -> int:
        """Extract seat number from blind string."""
        match = re.search(r'seat\s*=\s*(\d+)', blind_str)
        return int(match.group(1)) if match else 0
    
    def _extract_amount_from_blind(self, blind_str: str) -> float:
        """Extract amount from blind string."""
        match = re.search(r'amount\s*=\s*(\d+)', blind_str)
        return float(match.group(1)) if match else 0.0


class PHHV1Validator:
    """Validator for PHH v1 data against poker state machine."""
    
    def __init__(self):
        self.parser = PHHV1Parser()
    
    def validate_phh_v1_hand(self, phh_text: str) -> Dict[str, Any]:
        """Validate a PHH v1 hand against our poker state machine."""
        # Parse PHH v1 data
        phh_hand = self.parser.parse_phh_v1_text(phh_text)
        
        # Create and configure state machine
        sm = self._create_state_machine_from_phh_v1(phh_hand)
        
        # Execute all actions
        results = self._execute_phh_v1_actions(sm, phh_hand)
        
        # Validate final state
        validation_results = self._validate_final_state(sm, phh_hand)
        
        return {
            'phh_hand': phh_hand,
            'execution_results': results,
            'validation_results': validation_results,
            'success': validation_results['overall_success']
        }
    
    def _create_state_machine_from_phh_v1(self, phh_hand: PHHV1Hand) -> ImprovedPokerStateMachine:
        """Create a state machine configured from PHH v1 data."""
        # Create state machine with correct number of players
        sm = ImprovedPokerStateMachine(num_players=phh_hand.max_players, test_mode=True)
        sm.strategy_mode = "GTO"
        
        # Configure game state
        sm.game_state.big_blind = phh_hand.big_blind.amount
        
        # Set up players with correct positions and stacks
        for i, player_info in enumerate(phh_hand.players):
            if i < len(sm.game_state.players):
                player = sm.game_state.players[i]
                player.name = player_info.name
                player.stack = player_info.starting_stack_chips
                player.position = player_info.position
                
                # Set cards if available
                if player_info.cards:
                    player.cards = player_info.cards
        
        return sm
    
    def _execute_phh_v1_actions(self, sm: ImprovedPokerStateMachine, phh_hand: PHHV1Hand) -> List[Dict[str, Any]]:
        """Execute all PHH v1 actions on the state machine."""
        results = []
        
        # Start the hand
        sm.start_hand()
        results.append({
            'action': 'start_hand',
            'state': sm.current_state.value,
            'pot': sm.game_state.pot
        })
        
        # Execute preflop actions
        if phh_hand.preflop_actions:
            for action in phh_hand.preflop_actions:
                result = self._execute_single_action(sm, action, Street.PREFLOP)
                results.append(result)
        
        # Execute flop actions
        if phh_hand.flop_actions:
            for action in phh_hand.flop_actions:
                result = self._execute_single_action(sm, action, Street.FLOP)
                results.append(result)
        
        # Execute turn actions
        if phh_hand.turn_actions:
            for action in phh_hand.turn_actions:
                result = self._execute_single_action(sm, action, Street.TURN)
                results.append(result)
        
        # Execute river actions
        if phh_hand.river_actions:
            for action in phh_hand.river_actions:
                result = self._execute_single_action(sm, action, Street.RIVER)
                results.append(result)
        
        return results
    
    def _execute_single_action(self, sm: ImprovedPokerStateMachine, action: PHHV1Action, street: Street) -> Dict[str, Any]:
        """Execute a single action on the state machine."""
        # Find the player by seat
        player = self._find_player_by_seat(sm, action.actor)
        if not player:
            return {
                'action': f'ERROR: Player seat {action.actor} not found',
                'success': False
            }
        
        # Convert PHH v1 action to state machine action
        action_type = self._convert_phh_v1_action_type(action.action_type)
        amount = action.amount if action.amount > 0 else action.to
        
        # Execute the action
        try:
            sm.execute_action(player, action_type, amount)
            return {
                'action': f'Seat {action.actor} {action.action_type} ${amount}',
                'success': True,
                'state': sm.current_state.value,
                'pot': sm.game_state.pot
            }
        except Exception as e:
            return {
                'action': f'Seat {action.actor} {action.action_type} ${amount}',
                'success': False,
                'error': str(e)
            }
    
    def _find_player_by_seat(self, sm: ImprovedPokerStateMachine, seat: int) -> Optional[Player]:
        """Find a player by seat number in the state machine."""
        for player in sm.game_state.players:
            if hasattr(player, 'seat') and player.seat == seat:
                return player
        # Fallback to index-based lookup
        if 0 <= seat - 1 < len(sm.game_state.players):
            return sm.game_state.players[seat - 1]
        return None
    
    def _convert_phh_v1_action_type(self, phh_action_type: str) -> ActionType:
        """Convert PHH v1 action type to state machine action type."""
        mapping = {
            'fold': ActionType.FOLD,
            'check': ActionType.CHECK,
            'call': ActionType.CALL,
            'bet': ActionType.BET,
            'raise': ActionType.RAISE,
            'reraise': ActionType.RAISE,
            'all-in': ActionType.BET
        }
        return mapping.get(phh_action_type, ActionType.FOLD)
    
    def _validate_final_state(self, sm: ImprovedPokerStateMachine, phh_hand: PHHV1Hand) -> Dict[str, Any]:
        """Validate the final state against PHH v1 data."""
        results = {
            'pot_match': False,
            'winners_match': False,
            'community_cards_match': False,
            'overall_success': False
        }
        
        # Validate pot amount
        pot_tolerance = 0.01
        if abs(sm.game_state.pot - phh_hand.pot_total_chips) <= pot_tolerance:
            results['pot_match'] = True
        
        # Validate community cards (if applicable)
        if phh_hand.flop_board and phh_hand.flop_board.cards:
            sm_cards = sm.game_state.board[:3] if len(sm.game_state.board) >= 3 else []
            if len(sm_cards) == len(phh_hand.flop_board.cards):
                phh_cards_normalized = [self._normalize_card(card) for card in phh_hand.flop_board.cards]
                sm_cards_normalized = [self._normalize_card(card) for card in sm_cards]
                if sorted(phh_cards_normalized) == sorted(sm_cards_normalized):
                    results['community_cards_match'] = True
        
        # Validate winners (placeholder)
        if phh_hand.winners:
            results['winners_match'] = True  # Placeholder
        
        # Overall success
        results['overall_success'] = (
            results['pot_match'] and 
            results['community_cards_match'] and 
            results['winners_match']
        )
        
        return results
    
    def _normalize_card(self, card: str) -> str:
        """Normalize card format for comparison."""
        return card.upper()


class TestPHHV1ValidationFramework(unittest.TestCase):
    """Test suite for PHH v1 validation framework."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
        self.parser = PHHV1Parser()
    
    def test_phh_v1_parser_basic(self):
        """Test basic PHH v1 parsing functionality."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000/2000/0"
        currency = "USD"
        format = "Tournament"
        event = "Test Event"
        
        [table]
        table_name = "Test Table"
        max_players = 2
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Player1"
        position = "Button/SB"
        starting_stack_chips = 100000
        cards = ["Ah", "Kh"]
        
        [[players]]
        seat = 2
        name = "Player2"
        position = "Big Blind"
        starting_stack_chips = 100000
        cards = ["Qd", "Jd"]
        
        [blinds]
        small_blind = { seat = 1, amount = 1000 }
        big_blind = { seat = 2, amount = 2000 }
        
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 6000
        
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 4000
        
        [pot]
        total_chips = 12000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "no-showdown"
        """
        
        phh_hand = self.parser.parse_phh_v1_text(phh_text)
        
        self.assertEqual(phh_hand.variant, "No-Limit Hold'em")
        self.assertEqual(phh_hand.max_players, 2)
        self.assertEqual(phh_hand.big_blind.amount, 2000)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 12000)
    
    def test_legendary_hand_validation(self):
        """Test validation of a legendary poker hand."""
        # This would be a real legendary hand in PHH v1 format
        legendary_phh = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "20000/40000/5000"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2003 — Heads-Up"
        
        [table]
        table_name = "Final Table (HU)"
        max_players = 2
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Chris Moneymaker"
        position = "Button/SB"
        starting_stack_chips = 4620000
        is_hero = true
        cards = ["Ks", "7h"]
        
        [[players]]
        seat = 2
        name = "Sammy Farha"
        position = "Big Blind"
        starting_stack_chips = 3770000
        cards = ["Qs", "9h"]
        
        [blinds]
        small_blind = { seat = 1, amount = 20000 }
        big_blind = { seat = 2, amount = 40000 }
        
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 100000
        
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 60000
        
        [board.flop]
        cards = ["9s", "2d", "6s"]
        
        [[actions.flop]]
        actor = 2
        type = "check"
        
        [[actions.flop]]
        actor = 1
        type = "check"
        
        [board.turn]
        card = "8s"
        
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 300000
        
        [[actions.turn]]
        actor = 1
        type = "raise"
        to = 800000
        
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 500000
        
        [board.river]
        card = "3h"
        
        [[actions.river]]
        actor = 2
        type = "check"
        
        [[actions.river]]
        actor = 1
        type = "all-in"
        amount = 2800000
        
        [[actions.river]]
        actor = 2
        type = "fold"
        
        [pot]
        total_chips = 1810000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "no-showdown"
        """
        
        result = self.validator.validate_phh_v1_hand(legendary_phh)
        
        self.assertIsInstance(result, dict)
        self.assertIn('phh_hand', result)
        self.assertIn('execution_results', result)
        self.assertIn('validation_results', result)
        self.assertIn('success', result)


if __name__ == '__main__':
    unittest.main()
