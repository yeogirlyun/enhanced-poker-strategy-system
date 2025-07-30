#!/usr/bin/env python3
"""
Poker Hand Evaluator

A comprehensive poker hand evaluator for the practice simulator.
Evaluates hand strength for both preflop and postflop situations.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum


class HandRank(Enum):
    """Poker hand rankings."""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9


class HandEvaluator:
    """Evaluates poker hands and calculates hand strength."""
    
    def __init__(self):
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.suits = ["h", "d", "c", "s"]
        
    def evaluate_hand(self, hole_cards: List[str], board: List[str]) -> Tuple[HandRank, List[int], float]:
        """
        Evaluate a poker hand.
        
        Args:
            hole_cards: Player's hole cards (e.g., ["Ah", "Kd"])
            board: Community cards (e.g., ["Th", "Jc", "Qd"])
            
        Returns:
            Tuple of (hand_rank, kickers, hand_strength_score)
        """
        if not board:  # Preflop
            return self._evaluate_preflop(hole_cards)
        else:  # Postflop
            return self._evaluate_postflop(hole_cards, board)
    
    def _evaluate_preflop(self, hole_cards: List[str]) -> Tuple[HandRank, List[int], float]:
        """Evaluate preflop hand strength."""
        if len(hole_cards) != 2:
            return HandRank.HIGH_CARD, [], 0.0
        
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, suit1 = card1[0], card1[1]
        rank2, suit2 = card2[0], card2[1]
        
        # Get rank values
        rank1_val = self.ranks.index(rank1)
        rank2_val = self.ranks.index(rank2)
        
        # Check if suited
        suited = suit1 == suit2
        
        # Calculate hand strength
        if rank1 == rank2:  # Pair
            strength = 50 + rank1_val * 2
            return HandRank.PAIR, [rank1_val], strength
        else:  # Unpaired
            # Higher card gets more weight
            high_card = max(rank1_val, rank2_val)
            low_card = min(rank1_val, rank2_val)
            gap = high_card - low_card
            
            # Suited hands are stronger
            suited_bonus = 10 if suited else 0
            
            # Connected hands are stronger
            connected_bonus = max(0, 5 - gap)
            
            strength = 20 + high_card + suited_bonus + connected_bonus
            return HandRank.HIGH_CARD, [high_card, low_card], strength
    
    def _evaluate_postflop(self, hole_cards: List[str], board: List[str]) -> Tuple[HandRank, List[int], float]:
        """Evaluate postflop hand strength."""
        all_cards = hole_cards + board
        
        # Count ranks and suits
        rank_counts = {}
        suit_counts = {}
        
        for card in all_cards:
            rank, suit = card[0], card[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Find best 5-card hand
        best_hand = self._find_best_hand(all_cards)
        hand_rank, kickers, base_strength = best_hand
        
        # Adjust strength based on board texture
        adjusted_strength = self._adjust_strength_for_board(
            base_strength, hand_rank, board, hole_cards
        )
        
        return hand_rank, kickers, adjusted_strength
    
    def _find_best_hand(self, cards: List[str]) -> Tuple[HandRank, List[int], float]:
        """Find the best 5-card hand from available cards."""
        if len(cards) < 5:
            return HandRank.HIGH_CARD, [], 0.0
        
        # Generate all 5-card combinations
        from itertools import combinations
        best_hand = None
        best_rank = HandRank.HIGH_CARD
        best_kickers = []
        best_strength = 0.0
        
        for combo in combinations(cards, 5):
            rank, kickers, strength = self._evaluate_five_cards(list(combo))
            if rank.value > best_rank.value or (rank.value == best_rank.value and strength > best_strength):
                best_rank = rank
                best_kickers = kickers
                best_strength = strength
        
        return best_rank, best_kickers, best_strength
    
    def _evaluate_five_cards(self, cards: List[str]) -> Tuple[HandRank, List[int], float]:
        """Evaluate a 5-card hand."""
        # Count ranks and suits
        rank_counts = {}
        suit_counts = {}
        
        for card in cards:
            rank, suit = card[0], card[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Check for flush
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break
        
        # Check for straight
        straight_high = self._check_straight(rank_counts)
        
        # Determine hand rank
        if flush_suit and straight_high:
            # Straight flush
            return HandRank.STRAIGHT_FLUSH, [straight_high], 90 + straight_high
        elif self._has_four_of_a_kind(rank_counts):
            # Four of a kind
            rank = self._get_four_of_a_kind_rank(rank_counts)
            kicker = self._get_kicker(rank_counts, [rank])
            return HandRank.FOUR_OF_A_KIND, [rank, kicker], 80 + rank
        elif self._has_full_house(rank_counts):
            # Full house
            trips_rank, pair_rank = self._get_full_house_ranks(rank_counts)
            return HandRank.FULL_HOUSE, [trips_rank, pair_rank], 70 + trips_rank
        elif flush_suit:
            # Flush
            flush_ranks = self._get_flush_ranks(cards, flush_suit)
            return HandRank.FLUSH, flush_ranks, 60 + flush_ranks[0]
        elif straight_high:
            # Straight
            return HandRank.STRAIGHT, [straight_high], 50 + straight_high
        elif self._has_three_of_a_kind(rank_counts):
            # Three of a kind
            rank = self._get_three_of_a_kind_rank(rank_counts)
            kickers = self._get_kickers(rank_counts, [rank])
            return HandRank.THREE_OF_A_KIND, [rank] + kickers, 40 + rank
        elif self._has_two_pair(rank_counts):
            # Two pair
            pair_ranks = self._get_two_pair_ranks(rank_counts)
            kicker = self._get_kicker(rank_counts, pair_ranks)
            return HandRank.TWO_PAIR, pair_ranks + [kicker], 30 + pair_ranks[0]
        elif self._has_pair(rank_counts):
            # Pair
            rank = self._get_pair_rank(rank_counts)
            kickers = self._get_kickers(rank_counts, [rank])
            return HandRank.PAIR, [rank] + kickers, 20 + rank
        else:
            # High card
            high_cards = self._get_high_cards(rank_counts)
            return HandRank.HIGH_CARD, high_cards, 10 + high_cards[0]
    
    def _check_straight(self, rank_counts: Dict[str, int]) -> Optional[int]:
        """Check for straight and return high card."""
        rank_values = [self.ranks.index(rank) for rank in rank_counts.keys()]
        rank_values.sort()
        
        # Check for regular straight
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] - rank_values[i] == 4:
                return rank_values[i+4]
        
        # Check for wheel straight (A-2-3-4-5)
        if 0 in rank_values and 1 in rank_values and 2 in rank_values and 3 in rank_values and 12 in rank_values:
            return 3  # 5 is high card
        
        return None
    
    def _has_four_of_a_kind(self, rank_counts: Dict[str, int]) -> bool:
        """Check for four of a kind."""
        return 4 in rank_counts.values()
    
    def _get_four_of_a_kind_rank(self, rank_counts: Dict[str, int]) -> int:
        """Get the rank of four of a kind."""
        for rank, count in rank_counts.items():
            if count == 4:
                return self.ranks.index(rank)
        return 0
    
    def _has_full_house(self, rank_counts: Dict[str, int]) -> bool:
        """Check for full house."""
        counts = list(rank_counts.values())
        return 3 in counts and 2 in counts
    
    def _get_full_house_ranks(self, rank_counts: Dict[str, int]) -> Tuple[int, int]:
        """Get ranks for full house (trips, pair)."""
        trips_rank = 0
        pair_rank = 0
        
        for rank, count in rank_counts.items():
            if count == 3:
                trips_rank = self.ranks.index(rank)
            elif count == 2:
                pair_rank = self.ranks.index(rank)
        
        return trips_rank, pair_rank
    
    def _get_flush_ranks(self, cards: List[str], flush_suit: str) -> List[int]:
        """Get ranks for flush cards."""
        flush_cards = [card for card in cards if card[1] == flush_suit]
        ranks = [self.ranks.index(card[0]) for card in flush_cards]
        ranks.sort(reverse=True)
        return ranks[:5]
    
    def _has_three_of_a_kind(self, rank_counts: Dict[str, int]) -> bool:
        """Check for three of a kind."""
        return 3 in rank_counts.values()
    
    def _get_three_of_a_kind_rank(self, rank_counts: Dict[str, int]) -> int:
        """Get the rank of three of a kind."""
        for rank, count in rank_counts.items():
            if count == 3:
                return self.ranks.index(rank)
        return 0
    
    def _has_two_pair(self, rank_counts: Dict[str, int]) -> bool:
        """Check for two pair."""
        pairs = [count for count in rank_counts.values() if count == 2]
        return len(pairs) >= 2
    
    def _get_two_pair_ranks(self, rank_counts: Dict[str, int]) -> List[int]:
        """Get ranks for two pair."""
        pair_ranks = []
        for rank, count in rank_counts.items():
            if count == 2:
                pair_ranks.append(self.ranks.index(rank))
        pair_ranks.sort(reverse=True)
        return pair_ranks[:2]
    
    def _has_pair(self, rank_counts: Dict[str, int]) -> bool:
        """Check for pair."""
        return 2 in rank_counts.values()
    
    def _get_pair_rank(self, rank_counts: Dict[str, int]) -> int:
        """Get the rank of pair."""
        for rank, count in rank_counts.items():
            if count == 2:
                return self.ranks.index(rank)
        return 0
    
    def _get_kickers(self, rank_counts: Dict[str, int], used_ranks: List[int]) -> List[int]:
        """Get kicker cards."""
        kickers = []
        for rank, count in rank_counts.items():
            rank_val = self.ranks.index(rank)
            if rank_val not in used_ranks:
                kickers.extend([rank_val] * count)
        kickers.sort(reverse=True)
        return kickers[:5-len(used_ranks)]
    
    def _get_high_cards(self, rank_counts: Dict[str, int]) -> List[int]:
        """Get high cards."""
        ranks = [self.ranks.index(rank) for rank in rank_counts.keys()]
        ranks.sort(reverse=True)
        return ranks[:5]
    
    def _adjust_strength_for_board(self, base_strength: float, hand_rank: HandRank, 
                                  board: List[str], hole_cards: List[str]) -> float:
        """Adjust hand strength based on board texture."""
        # Board texture analysis
        board_ranks = [card[0] for card in board]
        board_suits = [card[1] for card in board]
        
        # Paired board
        rank_counts = {}
        for rank in board_ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        paired_board = any(count >= 2 for count in rank_counts.values())
        
        # Suited board
        suit_counts = {}
        for suit in board_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        suited_board = any(count >= 3 for count in suit_counts.values())
        
        # Connected board
        board_values = [self.ranks.index(rank) for rank in board_ranks]
        board_values.sort()
        connected_board = any(board_values[i+1] - board_values[i] <= 2 
                            for i in range(len(board_values)-1))
        
        # Adjust strength based on board texture
        adjustment = 0.0
        
        if paired_board and hand_rank in [HandRank.PAIR, HandRank.TWO_PAIR]:
            adjustment -= 10  # Paired board reduces value of pairs
        
        if suited_board and hand_rank == HandRank.FLUSH:
            adjustment += 5  # Suited board increases flush value
        
        if connected_board and hand_rank == HandRank.STRAIGHT:
            adjustment += 5  # Connected board increases straight value
        
        # Overcard analysis
        hole_ranks = [self.ranks.index(card[0]) for card in hole_cards]
        board_ranks = [self.ranks.index(rank) for rank in board_ranks]
        
        overcards = sum(1 for hole_rank in hole_ranks if hole_rank > max(board_ranks))
        if overcards > 0 and hand_rank == HandRank.HIGH_CARD:
            adjustment += overcards * 5
        
        return max(0, base_strength + adjustment)


# Global hand evaluator instance
hand_evaluator = HandEvaluator()


def evaluate_hand_strength(hole_cards: List[str], board: List[str]) -> float:
    """Evaluate hand strength for the practice simulator."""
    try:
        hand_rank, kickers, strength = hand_evaluator.evaluate_hand(hole_cards, board)
        return strength
    except Exception as e:
        print(f"Error evaluating hand: {e}")
        return 0.0 