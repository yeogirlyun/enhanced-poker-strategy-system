"""
Improved GTO Strategy Engine using Deuces Library

This module provides a modern GTO (Game Theory Optimal) strategy implementation
that uses the deuces library for accurate hand evaluation and realistic
preflop ranges based on modern poker theory.
"""

import random
from typing import Tuple, Dict, List
from deuces import Card, Evaluator

from .poker_types import ActionType, Player, GameState


class ImprovedGTOStrategy:
    """Enhanced GTO strategy engine using deuces for hand evaluation."""

    def __init__(self, num_players: int = 6):
        self.num_players = num_players
        self.evaluator = Evaluator()
        self.preflop_ranges = self._initialize_modern_preflop_ranges()

    def _initialize_modern_preflop_ranges(self) -> Dict[str, Dict[str, float]]:
        """Initialize modern 6-max preflop ranges based on current solver data."""
        return {
            "UTG": {
                # Tight range from UTG - premium hands only
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 0.5,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 0.7,
                "QJs": 1.0,
                "QTs": 0.5,
                "JTs": 0.8,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 0.7,
                "KQo": 1.0,
                "KJo": 0.3,
            },
            "MP": {
                # Slightly wider from MP
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "88": 1.0,
                "77": 0.8,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 0.8,
                "A8s": 0.5,
                "A7s": 0.3,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 1.0,
                "K9s": 0.6,
                "QJs": 1.0,
                "QTs": 0.9,
                "Q9s": 0.5,
                "JTs": 1.0,
                "J9s": 0.6,
                "T9s": 0.7,
                "98s": 0.4,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 1.0,
                "A9o": 0.5,
                "KQo": 1.0,
                "KJo": 0.8,
                "KTo": 0.4,
                "QJo": 0.6,
            },
            "CO": {
                # Wider range from cutoff
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "88": 1.0,
                "77": 1.0,
                "66": 0.8,
                "55": 0.6,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 1.0,
                "A8s": 0.8,
                "A7s": 0.6,
                "A6s": 0.4,
                "A5s": 0.7,
                "A4s": 0.5,
                "A3s": 0.4,
                "A2s": 0.3,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 1.0,
                "K9s": 0.9,
                "K8s": 0.6,
                "K7s": 0.4,
                "QJs": 1.0,
                "QTs": 1.0,
                "Q9s": 0.8,
                "Q8s": 0.5,
                "J9s": 0.9,
                "JTs": 1.0,
                "T9s": 1.0,
                "T8s": 0.7,
                "98s": 0.8,
                "97s": 0.5,
                "87s": 0.6,
                "76s": 0.4,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 1.0,
                "A9o": 0.8,
                "A8o": 0.4,
                "KQo": 1.0,
                "KJo": 1.0,
                "KTo": 0.8,
                "K9o": 0.4,
                "QJo": 1.0,
                "QTo": 0.6,
                "JTo": 0.5,
            },
            "BTN": {
                # Wide button range
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "88": 1.0,
                "77": 1.0,
                "66": 1.0,
                "55": 1.0,
                "44": 0.8,
                "33": 0.6,
                "22": 0.5,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 1.0,
                "A8s": 1.0,
                "A7s": 1.0,
                "A6s": 1.0,
                "A5s": 1.0,
                "A4s": 1.0,
                "A3s": 1.0,
                "A2s": 1.0,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 1.0,
                "K9s": 1.0,
                "K8s": 1.0,
                "K7s": 0.8,
                "K6s": 0.6,
                "K5s": 0.6,
                "K4s": 0.4,
                "K3s": 0.3,
                "K2s": 0.2,
                "QJs": 1.0,
                "QTs": 1.0,
                "Q9s": 1.0,
                "Q8s": 1.0,
                "Q7s": 0.7,
                "Q6s": 0.5,
                "Q5s": 0.4,
                "Q4s": 0.3,
                "JTs": 1.0,
                "J9s": 1.0,
                "J8s": 1.0,
                "J7s": 0.8,
                "J6s": 0.5,
                "J5s": 0.3,
                "T9s": 1.0,
                "T8s": 1.0,
                "T7s": 0.9,
                "T6s": 0.6,
                "T5s": 0.4,
                "98s": 1.0,
                "97s": 1.0,
                "96s": 0.7,
                "95s": 0.4,
                "87s": 1.0,
                "86s": 0.8,
                "85s": 0.5,
                "76s": 1.0,
                "75s": 0.7,
                "74s": 0.4,
                "65s": 0.8,
                "64s": 0.5,
                "54s": 0.7,
                "53s": 0.4,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 1.0,
                "A9o": 1.0,
                "A8o": 0.8,
                "A7o": 0.6,
                "A6o": 0.4,
                "A5o": 0.5,
                "A4o": 0.3,
                "A3o": 0.2,
                "A2o": 0.1,
                "KQo": 1.0,
                "KJo": 1.0,
                "KTo": 1.0,
                "K9o": 0.8,
                "K8o": 0.5,
                "K7o": 0.3,
                "QJo": 1.0,
                "QTo": 1.0,
                "Q9o": 0.8,
                "Q8o": 0.4,
                "JTo": 1.0,
                "J9o": 0.7,
                "J8o": 0.3,
                "T9o": 0.8,
                "T8o": 0.4,
                "98o": 0.6,
                "97o": 0.3,
                "87o": 0.4,
            },
            "SB": {
                # Small blind range (vs no action)
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "88": 1.0,
                "77": 1.0,
                "66": 1.0,
                "55": 1.0,
                "44": 1.0,
                "33": 1.0,
                "22": 1.0,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 1.0,
                "A8s": 1.0,
                "A7s": 1.0,
                "A6s": 1.0,
                "A5s": 1.0,
                "A4s": 1.0,
                "A3s": 1.0,
                "A2s": 1.0,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 1.0,
                "K9s": 1.0,
                "K8s": 1.0,
                "K7s": 1.0,
                "K6s": 1.0,
                "K5s": 1.0,
                "K4s": 1.0,
                "K3s": 1.0,
                "K2s": 1.0,
                "QJs": 1.0,
                "QTs": 1.0,
                "Q9s": 1.0,
                "Q8s": 1.0,
                "Q7s": 1.0,
                "Q6s": 1.0,
                "Q5s": 1.0,
                "Q4s": 1.0,
                "Q3s": 1.0,
                "Q2s": 1.0,
                "JTs": 1.0,
                "J9s": 1.0,
                "J8s": 1.0,
                "J7s": 1.0,
                "J6s": 1.0,
                "J5s": 1.0,
                "J4s": 1.0,
                "J3s": 1.0,
                "J2s": 1.0,
                "T9s": 1.0,
                "T8s": 1.0,
                "T7s": 1.0,
                "T6s": 1.0,
                "T5s": 1.0,
                "T4s": 1.0,
                "T3s": 1.0,
                "T2s": 1.0,
                "98s": 1.0,
                "97s": 1.0,
                "96s": 1.0,
                "95s": 1.0,
                "94s": 1.0,
                "93s": 1.0,
                "92s": 1.0,
                "87s": 1.0,
                "86s": 1.0,
                "85s": 1.0,
                "84s": 1.0,
                "83s": 1.0,
                "82s": 1.0,
                "76s": 1.0,
                "75s": 1.0,
                "74s": 1.0,
                "73s": 1.0,
                "72s": 1.0,
                "65s": 1.0,
                "64s": 1.0,
                "63s": 1.0,
                "62s": 1.0,
                "54s": 1.0,
                "53s": 1.0,
                "52s": 1.0,
                "43s": 1.0,
                "42s": 1.0,
                "32s": 1.0,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 1.0,
                "A9o": 1.0,
                "A8o": 1.0,
                "A7o": 1.0,
                "A6o": 1.0,
                "A5o": 1.0,
                "A4o": 1.0,
                "A3o": 1.0,
                "A2o": 1.0,
                "KQo": 1.0,
                "KJo": 1.0,
                "KTo": 1.0,
                "K9o": 1.0,
                "K8o": 1.0,
                "K7o": 1.0,
                "K6o": 1.0,
                "K5o": 1.0,
                "K4o": 1.0,
                "K3o": 1.0,
                "K2o": 1.0,
                "QJo": 1.0,
                "QTo": 1.0,
                "Q9o": 1.0,
                "Q8o": 1.0,
                "Q7o": 1.0,
                "Q6o": 1.0,
                "Q5o": 1.0,
                "Q4o": 1.0,
                "Q3o": 1.0,
                "Q2o": 1.0,
                "JTo": 1.0,
                "J9o": 1.0,
                "J8o": 1.0,
                "J7o": 1.0,
                "J6o": 1.0,
                "J5o": 1.0,
                "J4o": 1.0,
                "J3o": 1.0,
                "J2o": 1.0,
                "T9o": 1.0,
                "T8o": 1.0,
                "T7o": 1.0,
                "T6o": 1.0,
                "T5o": 1.0,
                "T4o": 1.0,
                "T3o": 1.0,
                "T2o": 1.0,
                "98o": 1.0,
                "97o": 1.0,
                "96o": 1.0,
                "95o": 1.0,
                "94o": 1.0,
                "93o": 1.0,
                "92o": 1.0,
                "87o": 1.0,
                "86o": 1.0,
                "85o": 1.0,
                "84o": 1.0,
                "83o": 1.0,
                "82o": 1.0,
                "76o": 1.0,
                "75o": 1.0,
                "74o": 1.0,
                "73o": 1.0,
                "72o": 1.0,
                "65o": 1.0,
                "64o": 1.0,
                "63o": 1.0,
                "62o": 1.0,
                "54o": 1.0,
                "53o": 1.0,
                "52o": 1.0,
                "43o": 1.0,
                "42o": 1.0,
                "32o": 1.0,
            },
            "BB": {
                # Big blind defense range (vs steal)
                "AA": 1.0,
                "KK": 1.0,
                "QQ": 1.0,
                "JJ": 1.0,
                "TT": 1.0,
                "99": 1.0,
                "88": 1.0,
                "77": 1.0,
                "66": 1.0,
                "55": 1.0,
                "44": 1.0,
                "33": 1.0,
                "22": 1.0,
                "AKs": 1.0,
                "AQs": 1.0,
                "AJs": 1.0,
                "ATs": 1.0,
                "A9s": 1.0,
                "A8s": 1.0,
                "A7s": 1.0,
                "A6s": 1.0,
                "A5s": 1.0,
                "A4s": 1.0,
                "A3s": 1.0,
                "A2s": 1.0,
                "KQs": 1.0,
                "KJs": 1.0,
                "KTs": 1.0,
                "K9s": 1.0,
                "K8s": 1.0,
                "K7s": 1.0,
                "K6s": 1.0,
                "K5s": 1.0,
                "K4s": 1.0,
                "K3s": 1.0,
                "K2s": 1.0,
                "QJs": 1.0,
                "QTs": 1.0,
                "Q9s": 1.0,
                "Q8s": 1.0,
                "Q7s": 1.0,
                "Q6s": 1.0,
                "Q5s": 1.0,
                "Q4s": 1.0,
                "Q3s": 1.0,
                "Q2s": 1.0,
                "JTs": 1.0,
                "J9s": 1.0,
                "J8s": 1.0,
                "J7s": 1.0,
                "J6s": 1.0,
                "J5s": 1.0,
                "J4s": 1.0,
                "J3s": 1.0,
                "J2s": 1.0,
                "T9s": 1.0,
                "T8s": 1.0,
                "T7s": 1.0,
                "T6s": 1.0,
                "T5s": 1.0,
                "T4s": 1.0,
                "T3s": 1.0,
                "T2s": 1.0,
                "98s": 1.0,
                "97s": 1.0,
                "96s": 1.0,
                "95s": 1.0,
                "94s": 1.0,
                "93s": 1.0,
                "92s": 1.0,
                "87s": 1.0,
                "86s": 1.0,
                "85s": 1.0,
                "84s": 1.0,
                "83s": 1.0,
                "82s": 1.0,
                "76s": 1.0,
                "75s": 1.0,
                "74s": 1.0,
                "73s": 1.0,
                "72s": 0.8,
                "65s": 1.0,
                "64s": 1.0,
                "63s": 1.0,
                "62s": 1.0,
                "54s": 1.0,
                "53s": 1.0,
                "52s": 1.0,
                "43s": 1.0,
                "42s": 1.0,
                "32s": 1.0,
                "AKo": 1.0,
                "AQo": 1.0,
                "AJo": 1.0,
                "ATo": 1.0,
                "A9o": 1.0,
                "A8o": 1.0,
                "A7o": 1.0,
                "A6o": 1.0,
                "A5o": 1.0,
                "A4o": 1.0,
                "A3o": 1.0,
                "A2o": 1.0,
                "KQo": 1.0,
                "KJo": 1.0,
                "KTo": 1.0,
                "K9o": 1.0,
                "K8o": 1.0,
                "K7o": 1.0,
                "K6o": 1.0,
                "K5o": 1.0,
                "K4o": 1.0,
                "K3o": 1.0,
                "K2o": 1.0,
                "QJo": 1.0,
                "QTo": 1.0,
                "Q9o": 1.0,
                "Q8o": 1.0,
                "Q7o": 1.0,
                "Q6o": 1.0,
                "Q5o": 1.0,
                "Q4o": 1.0,
                "Q3o": 1.0,
                "Q2o": 1.0,
                "JTo": 1.0,
                "J9o": 1.0,
                "J8o": 1.0,
                "J7o": 1.0,
                "J6o": 1.0,
                "J5o": 1.0,
                "J4o": 1.0,
                "J3o": 1.0,
                "J2o": 1.0,
                "T9o": 1.0,
                "T8o": 1.0,
                "T7o": 1.0,
                "T6o": 1.0,
                "T5o": 1.0,
                "T4o": 1.0,
                "T3o": 1.0,
                "T2o": 1.0,
                "98o": 1.0,
                "97o": 1.0,
                "96o": 1.0,
                "95o": 1.0,
                "94o": 1.0,
                "93o": 1.0,
                "92o": 1.0,
                "87o": 1.0,
                "86o": 1.0,
                "85o": 1.0,
                "84o": 1.0,
                "83o": 1.0,
                "82o": 1.0,
                "76o": 1.0,
                "75o": 1.0,
                "74o": 1.0,
                "73o": 1.0,
                "72o": 0.6,
                "65o": 1.0,
                "64o": 1.0,
                "63o": 1.0,
                "62o": 1.0,
                "54o": 1.0,
                "53o": 1.0,
                "52o": 1.0,
                "43o": 1.0,
                "42o": 1.0,
                "32o": 1.0,
            },
        }

    def convert_cards_to_deuces(self, cards: List[str]) -> List[int]:
        """Convert our card format to deuces format."""
        deuces_cards = []
        for card_str in cards:
            # Convert our format (e.g., 'Ah') to deuces format
            try:
                deuces_card = Card.new(card_str)
                deuces_cards.append(deuces_card)
            except BaseException:
                # If conversion fails, skip this card
                continue
        return deuces_cards

    def convert_board_to_deuces(self, board: List[str]) -> List[int]:
        """Convert board cards to deuces format."""
        return self.convert_cards_to_deuces(board)

    def get_hand_notation(self, cards: List[str]) -> str:
        """Convert two cards to standard notation (e.g., AKs, ATo, 88)."""
        if len(cards) != 2:
            return "XX"

        # Parse ranks and suits
        ranks = []
        suits = []
        for card in cards:
            if len(card) >= 2:
                rank = card[0]
                suit = card[1]
                ranks.append(rank)
                suits.append(suit)

        if len(ranks) != 2:
            return "XX"

        # Convert to standard notation
        rank_values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        r1, r2 = ranks[0], ranks[1]
        s1, s2 = suits[0], suits[1]

        # Order by rank (higher first)
        if rank_values.get(r1, 0) < rank_values.get(r2, 0):
            r1, r2 = r2, r1
            s1, s2 = s2, s1

        # Check if pair
        if r1 == r2:
            return f"{r1}{r2}"

        # Check if suited
        suited = "s" if s1 == s2 else "o"
        return f"{r1}{r2}{suited}"

    def get_preflop_action(
        self, player: Player, game_state: GameState
    ) -> Tuple[ActionType, float]:
        """Get preflop action based on modern GTO ranges."""
        position = player.position
        hand_notation = self.get_hand_notation(player.cards)

        print(f"🔍 GTO_PREFLOP: Position={position}, Cards={player.cards}, Notation={hand_notation}")

        # Get position range
        if position not in self.preflop_ranges:
            print(f"🔍 GTO_PREFLOP: Position {position} not in ranges, defaulting to UTG")
            # Default to tight range for unknown positions
            position = "UTG"

        position_range = self.preflop_ranges[position]
        play_frequency = position_range.get(hand_notation, 0.0)
        
        print(f"🔍 GTO_PREFLOP: Play frequency for {hand_notation} in {position}: {play_frequency}")

        # Determine if we should play this hand
        random_roll = random.random()
        print(f"🔍 GTO_PREFLOP: Random roll: {random_roll}, threshold: {play_frequency}")
        
        if random_roll > play_frequency:
            print(f"🔍 GTO_PREFLOP: FOLDING - random {random_roll} > frequency {play_frequency}")
            return ActionType.FOLD, 0.0
        
        print(f"🔍 GTO_PREFLOP: PLAYING HAND - proceeding with action logic")

        # If we're playing, determine action based on situation
        call_amount = game_state.current_bet - player.current_bet

        # Simple action logic for now
        if call_amount == 0:
            # No bet to call - decide between check and bet
            if play_frequency >= 0.8:  # Premium hands - bet for value
                bet_size = min(game_state.pot * 0.7, player.stack * 0.1)
                return ActionType.BET, bet_size
            else:
                return ActionType.CHECK, 0.0
        else:
            # Facing a bet - call or raise based on hand strength  
            if play_frequency >= 0.9:  # Premium hands - consider raising
                if random.random() < 0.3:  # 30% raise frequency with premium
                    # Calculate raise amount (additional on top of current bet to call)
                    additional_raise_size = min(call_amount * 2, player.stack * 0.15)
                    # Total bet amount = current bet of game + additional raise
                    total_bet_amount = game_state.current_bet + additional_raise_size
                    return ActionType.RAISE, total_bet_amount

            # Default to calling playable hands
            if call_amount <= player.stack * 0.15:  # Reasonable call
                return ActionType.CALL, call_amount
            else:
                return ActionType.FOLD, 0.0

    def get_postflop_action(
        self, player: Player, game_state: GameState
    ) -> Tuple[ActionType, float]:
        """Get postflop action using hand strength evaluation."""
        try:
            # Convert cards to deuces format
            hole_cards = self.convert_cards_to_deuces(player.cards)
            board_cards = self.convert_board_to_deuces(game_state.board)

            if len(hole_cards) != 2 or len(board_cards) < 3:
                # Fallback if card conversion fails
                return self._get_conservative_action(player, game_state)

            # Evaluate hand strength
            hand_score = self.evaluator.evaluate(board_cards, hole_cards)
            hand_strength = 1.0 - self.evaluator.get_five_card_rank_percentage(
                hand_score
            )

            # Decision based on hand strength
            call_amount = game_state.current_bet - player.current_bet
            pot_size = game_state.pot

            if call_amount == 0:
                # No bet to call - decide between check and bet
                if hand_strength >= 0.8:  # Very strong hands
                    bet_size = min(pot_size * 0.75, player.stack * 0.2)
                    return ActionType.BET, bet_size
                elif hand_strength >= 0.6:  # Good hands
                    if random.random() < 0.4:  # 40% bet frequency
                        bet_size = min(pot_size * 0.5, player.stack * 0.15)
                        return ActionType.BET, bet_size

                return ActionType.CHECK, 0.0
            else:
                # Facing a bet
                pot_odds = call_amount / (pot_size + call_amount)

                if hand_strength >= 0.85:  # Very strong - consider raising
                    if random.random() < 0.5:
                        # Calculate raise amount (additional on top of current bet to call)
                        additional_raise_size = min(call_amount * 1.5, player.stack * 0.2)
                        # Total bet amount = current bet of game + additional raise
                        total_bet_amount = game_state.current_bet + additional_raise_size
                        return ActionType.RAISE, total_bet_amount
                    else:
                        return ActionType.CALL, call_amount
                elif hand_strength >= pot_odds + 0.1:  # Good odds
                    return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0.0

        except Exception:
            # Fallback to conservative play if evaluation fails
            return self._get_conservative_action(player, game_state)

    def _get_conservative_action(
        self, player: Player, game_state: GameState
    ) -> Tuple[ActionType, float]:
        """Conservative fallback action."""
        call_amount = game_state.current_bet - player.current_bet

        if call_amount == 0:
            return ActionType.CHECK, 0.0
        elif call_amount <= player.stack * 0.1:
            return ActionType.CALL, call_amount
        else:
            return ActionType.FOLD, 0.0

    def get_gto_action(
        self, player: Player, game_state: GameState
    ) -> Tuple[ActionType, float]:
        """Main method to get GTO action for a player."""
        # Check if it's preflop or postflop
        if game_state.street == "preflop" or not game_state.board:
            return self.get_preflop_action(player, game_state)
        else:
            return self.get_postflop_action(player, game_state)
