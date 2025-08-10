"""
GTO Strategy Engine for Poker State Machine

This module contains the GTO (Game Theory Optimal) strategy implementation,
including preflop ranges, hand strength evaluation, and bot action logic.
"""

from typing import Tuple, Optional, Dict, List, Any
import random

# Import shared types from types module
from .types import ActionType, Player, GameState


class GTOStrategyEngine:
    """Handles GTO strategy decisions, ranges, and hand evaluations."""

    def __init__(self, num_players: int, strategy_data: Optional[dict] = None):
        self.num_players = num_players
        self.strategy_data = strategy_data
        self.gto_preflop_ranges = {}
        self._initialize_gto_ranges()

    def _initialize_gto_ranges(self):
        """Initialize GTO preflop ranges for 6-max poker."""
        self.gto_preflop_ranges = {
            "UTG": {
                "rfi": {
                    "range": ["AA-88", "AKs-AJs", "KQs", "AJo+", "KQo"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-99", "AKs-AQs", "AJo+", "KQo"],
                    "freq": 0.8
                },
                "vs_three_bet": {
                    "range": ["AA-JJ", "AKs", "AKo"],
                    "freq": 0.8
                }
            },
            "MP": {
                "rfi": {
                    "range": ["AA-77", "AKs-ATs", "KQs-KJs", "AJo+", "KQo", "KJo"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-88", "AKs-AJs", "AJo+", "KQo"],
                    "freq": 0.7
                },
                "vs_three_bet": {
                    "range": ["AA-QQ", "AKs", "AKo"],
                    "freq": 0.8
                }
            },
            "CO": {
                "rfi": {
                    "range": ["AA-66", "AKs-ATs", "KQs-KTs", "QJs", "AJo+", "KQo", "KJo", "QJo"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-77", "AKs-AJs", "AJo+", "KQo"],
                    "freq": 0.6
                },
                "vs_three_bet": {
                    "range": ["AA-JJ", "AKs", "AKo"],
                    "freq": 0.8
                }
            },
            "BTN": {
                "rfi": {
                    "range": ["AA-55", "AKs-ATs", "KQs-KTs", "QJs-QTs", "JTs",
                              "T9s", "AJo+", "KQo", "KJo", "QJo"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-66", "AKs-AJs", "AJo+", "KQo"],
                    "freq": 0.5
                },
                "vs_three_bet": {
                    "range": ["AA-QQ", "AKs", "AKo"],
                    "freq": 0.8
                }
            },
            "SB": {
                "rfi": {
                    "range": ["AA-22", "AKs-A2s", "KQs-K2s", "QJs-Q2s", "JTs-J2s", "T9s", "AJo+", "KQo", "KJo", "QJo", "JTo"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-44", "AKs-AJs", "AJo+", "KQo"],
                    "freq": 0.4
                },
                "vs_three_bet": {
                    "range": ["AA-99", "AKs", "AKo"],
                    "freq": 0.8
                }
            },
            "BB": {
                "rfi": {
                    "range": ["AA-22", "AKs-A2s", "KQs-K2s", "QJs-Q2s", "JTs-J2s", "T9s-T8s", "98s", "AJo+", "KQo", "KJo", "QJo", "JTo", "T9o"],
                    "freq": 1.0
                },
                "vs_rfi": {
                    "range": ["AA-33", "AKs-AJs", "AJo+", "KQo"],
                    "freq": 0.6  # FIXED: Loosened from 0.3 to 0.6 for wider BB defense (GTO standard vs min-raise)
                },
                "vs_three_bet": {
                    "range": ["AA-88", "AKs", "AKo"],
                    "freq": 0.8
                }
            }
        }

    def get_gto_bot_action(self, player: Player, game_state: GameState) -> Tuple[ActionType, float]:
        """
        Get GTO bot action for a player.
        
        Args:
            player: The player making the decision
            game_state: Current game state
            
        Returns:
            Tuple of (action_type, amount)
        """
        street = game_state.street
        call_amount = game_state.current_bet - player.current_bet
        pot_odds = call_amount / (game_state.pot + call_amount) if call_amount > 0 else 0.0
        
        # Preflop logic
        if street == "preflop" and not game_state.board:
            action, amount = self._get_gto_preflop_action(player, game_state, call_amount)
        # Postflop logic
        else:
            action, amount = self._get_gto_postflop_action(player, game_state, call_amount, pot_odds)
        
        # NEW: Comprehensive stack validation
        return self._validate_stack_limits(player, action, amount, call_amount)
    
    def _validate_stack_limits(self, player: Player, action: ActionType, amount: float, call_amount: float) -> Tuple[ActionType, float]:
        """Validate that action amount doesn't exceed stack and handle all-in scenarios."""
        if amount > player.stack:
            # Can't afford the action - need to handle all-in or fold
            if call_amount > 0:
                # Facing a bet - can all-in call or fold
                if player.stack >= call_amount:
                    return ActionType.CALL, player.stack  # All-in call
                else:
                    return ActionType.FOLD, 0.0  # Can't afford to call
            else:
                # No bet to call - can all-in bet or check
                if player.stack >= 2.0:  # Minimum bet amount
                    return ActionType.BET, player.stack  # All-in bet
                else:
                    return ActionType.CHECK, 0.0  # Can't afford to bet
        return action, amount  # Amount is valid

    def _get_gto_preflop_action(self, player: Player, game_state: GameState, call_amount: float) -> Tuple[ActionType, float]:
        """Get GTO preflop action with FIXED validation."""
        hand = self.get_hand_notation(player.cards)
        position = player.position
        strength = self.get_preflop_hand_strength(player.cards)
        
        # FIXED: Calculate minimum raise properly
        min_raise_total = game_state.current_bet + game_state.min_raise
        
        # Short stack all-in logic
        if player.stack <= 2.0:
            if strength >= 70:
                return ActionType.RAISE, player.stack
            else:
                return ActionType.FOLD, 0.0
        
        # Determine context
        facing_bet = call_amount > 0
        
        # Get position ranges
        if position not in self.gto_preflop_ranges:
            return ActionType.FOLD, 0.0
            
        position_ranges = self.gto_preflop_ranges[position]
        
        # FIXED: RFI (Raise First In) - Check if pot is unopened
        if game_state.current_bet <= game_state.big_blind:
            # FIXED: For unchecked pots (call_amount == 0), always check (GTO: no limp-raise weak)
            if call_amount == 0:
                return ActionType.CHECK, 0.0
            # For facing a bet, use range logic
            elif self.is_hand_in_range(hand, position_ranges["rfi"]["range"]):
                if random.random() <= position_ranges["rfi"]["freq"]:
                    # FIXED: Ensure raise meets minimum requirement
                    raise_amount = max(min_raise_total, game_state.big_blind * 3)
                    raise_amount = int(round(raise_amount))  # Ensure integer bet sizes
                    if raise_amount <= player.stack:
                        return ActionType.RAISE, raise_amount
                    else:
                        return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0.0
            else:
                return ActionType.FOLD, 0.0
        
        # vs RFI
        elif (facing_bet and 
              game_state.current_bet <= game_state.big_blind * 3):
            # FIXED: BB-specific defense logic - defend 60% vs raise (GTO standard)
            if position == "BB" and call_amount > 0:
                if random.random() < 0.6:  # Defend 60% vs raise
                    return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0.0
            elif self.is_hand_in_range(hand, position_ranges["vs_rfi"]["range"]):
                if random.random() <= position_ranges["vs_rfi"]["freq"]:
                    if strength >= 80:
                        # FIXED: Ensure raise meets minimum requirement
                        raise_amount = max(min_raise_total, game_state.current_bet * 3)
                        raise_amount = int(round(raise_amount))  # Ensure integer bet sizes
                        if raise_amount <= player.stack:
                            return ActionType.RAISE, raise_amount
                        else:
                            return ActionType.CALL, call_amount
                    else:
                        return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0.0
            else:
                return ActionType.FOLD, 0.0
        
        # vs 3-bet
        else:
            if self.is_hand_in_range(hand, position_ranges["vs_three_bet"]["range"]):
                if random.random() <= position_ranges["vs_three_bet"]["freq"]:
                    if strength >= 80:  # Lower threshold for 3-bet defense
                        # FIXED: Ensure raise meets minimum requirement
                        raise_amount = max(min_raise_total, game_state.current_bet * 2.5)
                        raise_amount = int(round(raise_amount))  # Ensure integer bet sizes
                        if raise_amount <= player.stack:
                            return ActionType.RAISE, raise_amount
                        else:
                            return ActionType.CALL, call_amount
                    else:
                        return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0.0
            else:
                return ActionType.FOLD, 0.0

    def _get_gto_postflop_action(self, player: Player, game_state: GameState, call_amount: float, pot_odds: float) -> Tuple[ActionType, float]:
        """Get GTO postflop action with FIXED validation."""
        strength = self.get_postflop_hand_strength(player.cards, game_state.board)
        position = player.position
        facing_bet = call_amount > 0
        
        # FIXED: Calculate minimum raise properly
        min_raise_total = game_state.current_bet + game_state.min_raise
        
        # Calculate SPR (Stack-to-Pot Ratio)
        spr = player.stack / game_state.pot if game_state.pot > 0 else float('inf')
        
        # Board texture analysis
        texture = self.classify_board_texture(game_state.board)
        
        # Bet sizing based on board texture
        if texture["type"] == "dry":
            bet_size = game_state.pot * 0.6
        elif texture["type"] == "wet":
            bet_size = game_state.pot * 0.75
        else:  # medium
            bet_size = game_state.pot * 0.67
        
        # Stack depth adjustment
        stack_mult = min(1.0, max(0.3, spr / 5))
        bet_size *= stack_mult
        
        # POKER FIX: Round bet sizes to proper poker amounts (integers, BB multiples)
        big_blind = game_state.big_blind
        
        def round_to_poker_bet(amount):
            """Round amount to proper poker bet size (integer, BB multiples)."""
            if amount < big_blind:
                return int(big_blind)
            # Round to nearest big blind for bets > 2BB, otherwise round to nearest integer
            if amount >= 2 * big_blind:
                return int(round(amount / big_blind)) * int(big_blind)
            else:
                return int(round(amount))
        
        if facing_bet:
            # Facing a bet
            value_thresh = 70  # Raise nuts only
            call_thresh = pot_odds * 100
            if strength >= value_thresh:
                # FIXED: Ensure raise meets minimum requirement and round to proper poker bet
                raise_amount = max(min_raise_total, bet_size)
                raise_amount = round_to_poker_bet(raise_amount)
                if raise_amount <= player.stack:
                    return ActionType.RAISE, raise_amount
                else:
                    return ActionType.CALL, call_amount
            elif strength > call_thresh and strength > 30:  # Call medium
                return ActionType.CALL, call_amount
            elif call_amount == 0:
                return ActionType.CHECK, 0.0
            else:
                return ActionType.FOLD, 0.0
        else:
            # No bet to call
            if strength >= 70:
                # FIXED: Ensure bet meets minimum requirement and round to proper poker bet
                bet_amount = max(game_state.min_raise, bet_size)
                bet_amount = round_to_poker_bet(bet_amount)
                if bet_amount <= player.stack:
                    return ActionType.BET, bet_amount
                else:
                    return ActionType.CHECK, 0.0
            elif strength >= 50:
                return ActionType.CHECK, 0.0
            else:
                return ActionType.CHECK, 0.0

    def get_preflop_hand_strength(self, cards: List[str]) -> int:
        """Get preflop hand strength (0-100)."""
        if len(cards) != 2:
            return 0
            
        rank1, rank2 = cards[0][0], cards[1][0]
        suited = cards[0][1] == cards[1][1]
        
        # High card values
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        val1, val2 = rank_values[rank1], rank_values[rank2]
        
        # Pairs
        if val1 == val2:
            if val1 >= 14: return 95  # AA
            elif val1 >= 12: return 90  # KK
            elif val1 >= 10: return 85  # QQ
            elif val1 >= 8: return 80   # JJ
            elif val1 >= 6: return 75   # TT
            else: return 70 + val1       # 99-22
        
        # Suited
        if suited:
            if val1 == 14 or val2 == 14:  # AKs, AQs, etc.
                if max(val1, val2) >= 12: return 85
                elif max(val1, val2) >= 10: return 80
                else: return 75
            elif val1 >= 12 or val2 >= 12:  # KQs, KJs, etc.
                return 70 + min(val1, val2)
            else:
                return 60 + min(val1, val2)
        
        # Offsuit
        else:
            if val1 == 14 or val2 == 14:  # AKo, AQo, etc.
                if max(val1, val2) >= 12: return 80
                elif max(val1, val2) >= 10: return 75
                else: return 70
            elif val1 >= 12 or val2 >= 12:  # KQo, KJo, etc.
                return 65 + min(val1, val2)
            else:
                return 55 + min(val1, val2)

    def get_postflop_hand_strength(self, cards: List[str], board: List[str]) -> int:
        """Get postflop hand strength (0-100)."""
        if not board or len(cards) != 2:
            return 0
            
        # Simple hand strength calculation
        all_cards = cards + board
        ranks = [card[0] for card in all_cards]
        suits = [card[1] for card in all_cards]
        
        # Count ranks and suits
        rank_counts = {}
        suit_counts = {}
        
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Evaluate hand strength
        max_rank_count = max(rank_counts.values()) if rank_counts else 0
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        
        if max_rank_count >= 4: return 95  # Four of a kind
        elif max_rank_count == 3 and len(rank_counts) == 2: return 90  # Full house
        elif max_suit_count >= 5: return 85  # Flush
        elif max_rank_count == 3: return 80  # Three of a kind
        elif len([c for c in rank_counts.values() if c == 2]) == 2: return 75  # Two pair
        elif max_rank_count == 2: return 70  # One pair
        else: return 60  # High card

    def classify_board_texture(self, board: List[str]) -> Dict[str, Any]:
        """Classify board texture for postflop strategy."""
        if not board:
            return {"type": "dry", "dynamism": 0.0, "wetness": 0.0}
        
        ranks = [card[0] for card in board]
        suits = [card[1] for card in board]
        
        # Count suits
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Calculate wetness (flush potential)
        max_suit = max(suit_counts.values()) if suit_counts else 0
        wetness = max_suit / len(board)
        
        # Calculate dynamism (straight potential)
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        values = [rank_values[r] for r in ranks]
        values.sort()
        
        # Check for connected cards
        connected = 0
        for i in range(len(values) - 1):
            if values[i+1] - values[i] <= 2:
                connected += 1
        
        dynamism = connected / (len(values) - 1) if len(values) > 1 else 0.0
        
        # Determine board type
        if wetness >= 0.6 or dynamism >= 0.7:
            board_type = "wet"
        elif wetness <= 0.4 and dynamism <= 0.3:
            board_type = "dry"
        else:
            board_type = "medium"
        
        return {
            "type": board_type,
            "wetness": wetness,
            "dynamism": dynamism
        }

    def get_hand_notation(self, cards: List[str]) -> str:
        """Convert cards to hand notation (e.g., 'AKs', 'TT')."""
        if len(cards) != 2:
            return ""
        
        rank1, rank2 = cards[0][0], cards[1][0]
        suited = cards[0][1] == cards[1][1]
        
        if rank1 == rank2:
            return rank1 + rank1  # e.g., "TT"
        else:
            # Order by rank value
            rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                          '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            
            if rank_values[rank1] > rank_values[rank2]:
                high, low = rank1, rank2
            else:
                high, low = rank2, rank1
            
            suffix = "s" if suited else "o"
            return high + low + suffix  # e.g., "AKs", "AJo"

    def is_hand_in_range(self, hand: str, range_list: List[str]) -> bool:
        """Check if hand is in the given range."""
        for range_entry in range_list:
            if self._hand_matches_range_entry(hand, range_entry):
                return True
        return False

    def _hand_matches_range_entry(self, hand: str, range_entry: str) -> bool:
        """Check if hand matches a specific range entry."""
        if not hand or not range_entry:
            return False
        
        # Handle pairs
        if len(range_entry) == 2 and range_entry[0] == range_entry[1]:
            return hand[:2] == range_entry
        
        # Handle suited/offsuit
        if len(range_entry) == 3:
            if range_entry.endswith('s'):
                return hand == range_entry
            elif range_entry.endswith('o'):
                return hand == range_entry
        
        # Handle ranges like "AA-88"
        if '-' in range_entry:
            return self._hand_in_range(hand, range_entry.split('-')[0], range_entry.split('-')[1])
        
        # Handle plus ranges like "AJo+"
        if range_entry.endswith('+'):
            return self._hand_stronger_than_or_equal(hand, range_entry[:-1])
        
        return hand == range_entry

    def _hand_in_range(self, hand: str, start_hand: str, end_hand: str) -> bool:
        """Check if hand is in range between start and end hands."""
        hand_value = self._get_hand_strength_value(hand)
        start_value = self._get_hand_strength_value(start_hand)
        end_value = self._get_hand_strength_value(end_hand)
        
        return start_value >= hand_value >= end_value

    def _hand_stronger_than_or_equal(self, hand: str, base_hand: str) -> bool:
        """Check if hand is stronger than or equal to base hand."""
        hand_value = self._get_hand_strength_value(hand)
        base_value = self._get_hand_strength_value(base_hand)
        
        return hand_value >= base_value

    def _get_hand_strength_value(self, hand: str) -> int:
        """Get numeric strength value for hand comparison."""
        if not hand or len(hand) < 2:
            return 0
        
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        # Pairs
        if len(hand) == 2 and hand[0] == hand[1]:
            return rank_values[hand[0]] * 100
        
        # Suited/offsuit
        if len(hand) == 3:
            high_rank = hand[0]
            low_rank = hand[1]
            suited = hand[2] == 's'
            
            high_val = rank_values[high_rank]
            low_val = rank_values[low_rank]
            
            # Suited hands are worth more
            multiplier = 10 if suited else 1
            return (high_val * 10 + low_val) * multiplier
        
        return 0
