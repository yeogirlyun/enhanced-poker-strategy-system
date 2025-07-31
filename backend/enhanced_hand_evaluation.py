#!/usr/bin/env python3
"""
Enhanced Hand Evaluation System

This module provides a comprehensive and accurate hand evaluation system
that serves as the single source of truth for all hand strength calculations
across the poker application.
"""

from enum import Enum
from typing import List, Tuple, Dict, Optional
import itertools


class HandRank(Enum):
    """Poker hand rankings from highest to lowest."""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class EnhancedHandEvaluator:
    """Enhanced hand evaluator with comprehensive hand strength calculation."""
    
    def __init__(self):
        self.rank_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        self.suits = ['h', 'd', 'c', 's']  # hearts, diamonds, clubs, spades
    
    def evaluate_hand(self, hole_cards: List[str], board_cards: List[str]) -> Dict:
        """
        Evaluate a poker hand and return comprehensive information.
        
        Args:
            hole_cards: List of hole cards (e.g., ['Ah', 'Kd'])
            board_cards: List of board cards (e.g., ['7c', '8h', '9s'])
            
        Returns:
            Dictionary with hand evaluation details
        """
        all_cards = hole_cards + board_cards
        
        # Validate cards
        if not self._validate_cards(all_cards):
            return {
                'hand_rank': HandRank.HIGH_CARD,
                'rank_values': [0],
                'hand_description': 'Invalid cards',
                'strength_score': 0
            }
        
        # Analyze the hand
        rank_counts = self._count_ranks(all_cards)
        suit_counts = self._count_suits(all_cards)
        ranks = [card[0] for card in all_cards]
        rank_values = [self.rank_values[rank] for rank in ranks]
        
        # Determine hand rank
        hand_rank, rank_values, description = self._determine_hand_rank(
            rank_counts, suit_counts, rank_values
        )
        
        # Calculate strength score (0-100)
        strength_score = self._calculate_strength_score(hand_rank, rank_values)
        
        return {
            'hand_rank': hand_rank,
            'rank_values': rank_values,
            'hand_description': description,
            'strength_score': strength_score,
            'hole_cards': hole_cards,
            'board_cards': board_cards
        }
    
    def _validate_cards(self, cards: List[str]) -> bool:
        """Validate that all cards are in correct format."""
        for card in cards:
            if len(card) != 2:
                return False
            rank, suit = card[0], card[1]
            if rank not in self.rank_values or suit not in self.suits:
                return False
        return True
    
    def _count_ranks(self, cards: List[str]) -> Dict[str, int]:
        """Count occurrences of each rank."""
        rank_counts = {}
        for card in cards:
            rank = card[0]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        return rank_counts
    
    def _count_suits(self, cards: List[str]) -> Dict[str, int]:
        """Count occurrences of each suit."""
        suit_counts = {}
        for card in cards:
            suit = card[1]
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        return suit_counts
    
    def _determine_hand_rank(self, rank_counts: Dict, suit_counts: Dict, 
                           rank_values: List[int]) -> Tuple[HandRank, List[int], str]:
        """Determine the rank of the hand."""
        sorted_values = sorted(rank_counts.values(), reverse=True)
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        
        # Check for royal flush (A-high straight flush)
        if self._is_straight_flush(rank_counts, suit_counts):
            # Check if it's a royal flush (A-high straight flush)
            if 14 in rank_values and 13 in rank_values and 12 in rank_values and 11 in rank_values and 10 in rank_values:
                return HandRank.ROYAL_FLUSH, sorted(rank_values, reverse=True), "Royal Flush"
            return HandRank.STRAIGHT_FLUSH, sorted(rank_values, reverse=True), "Straight Flush"
        
        # Check for four of a kind
        if 4 in sorted_values:
            return HandRank.FOUR_OF_A_KIND, sorted(rank_values, reverse=True), "Four of a Kind"
        
        # Check for full house
        if sorted_values == [3, 2]:
            return HandRank.FULL_HOUSE, sorted(rank_values, reverse=True), "Full House"
        
        # Check for flush
        if max_suit_count >= 5:
            return HandRank.FLUSH, sorted(rank_values, reverse=True), "Flush"
        
        # Check for straight
        if self._is_straight(rank_counts):
            return HandRank.STRAIGHT, sorted(rank_values, reverse=True), "Straight"
        
        # Check for three of a kind
        if 3 in sorted_values:
            return HandRank.THREE_OF_A_KIND, sorted(rank_values, reverse=True), "Three of a Kind"
        
        # Check for two pair
        if sorted_values.count(2) >= 2:
            return HandRank.TWO_PAIR, sorted(rank_values, reverse=True), "Two Pair"
        
        # Check for pair
        if 2 in sorted_values:
            return HandRank.PAIR, sorted(rank_values, reverse=True), "Pair"
        
        # High card
        return HandRank.HIGH_CARD, sorted(rank_values, reverse=True), "High Card"
    
    def _is_straight_flush(self, rank_counts: Dict, suit_counts: Dict) -> bool:
        """Check for straight flush."""
        return (self._is_straight(rank_counts) and 
                max(suit_counts.values()) >= 5)
    
    def _is_straight(self, rank_counts: Dict) -> bool:
        """Check for straight."""
        ranks = list(rank_counts.keys())
        rank_values = [self.rank_values[rank] for rank in ranks]
        rank_values.sort()
        
        # Check for regular straight
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] - rank_values[i] == 4:
                return True
        
        # Check for Ace-low straight (A,2,3,4,5)
        if 14 in rank_values and 2 in rank_values and 3 in rank_values and 4 in rank_values and 5 in rank_values:
            return True
        
        return False
    
    def _calculate_strength_score(self, hand_rank: HandRank, rank_values: List[int]) -> int:
        """Calculate a strength score from 0-100."""
        base_score = hand_rank.value * 10
        
        # Add kicker strength
        kicker_strength = sum(rank_values[:5]) / 70.0  # Normalize to 0-1
        
        total_score = base_score + (kicker_strength * 10)
        return min(100, int(total_score))
    
    def _compare_hands(self, hand1: Tuple[HandRank, List[int]], 
                      hand2: Tuple[HandRank, List[int]]) -> int:
        """Compare two hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
        rank1, values1 = hand1
        rank2, values2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same rank, compare kickers
            for v1, v2 in zip(values1, values2):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0  # Tie
    
    def get_preflop_hand_strength(self, hole_cards: List[str]) -> int:
        """Get preflop hand strength using lookup table."""
        if len(hole_cards) != 2:
            return 0
        
        # Sort cards by rank value
        sorted_cards = sorted(hole_cards, 
                            key=lambda x: self.rank_values[x[0]], reverse=True)
        
        rank1, suit1 = sorted_cards[0][0], sorted_cards[0][1]
        rank2, suit2 = sorted_cards[1][0], sorted_cards[1][1]
        
        # Create hand notation
        if rank1 == rank2:
            hand_notation = f"{rank1}{rank2}"  # Pocket pair
        else:
            suited = suit1 == suit2
            hand_notation = f"{rank1}{rank2}{'s' if suited else 'o'}"
        
        # Preflop hand strength lookup table
        preflop_strengths = {
            'AA': 85, 'KK': 82, 'QQ': 80, 'JJ': 77, 'TT': 75,
            '99': 72, '88': 69, '77': 67, '66': 64, '55': 62,
            'AKs': 67, 'AQs': 66, 'AJs': 65, 'ATs': 64, 'A9s': 62,
            'AKo': 65, 'AQo': 64, 'AJo': 63, 'ATo': 62, 'A9o': 60,
            'KQs': 63, 'KJs': 62, 'KTs': 61, 'KQo': 61, 'KJo': 60,
            'QJs': 60, 'QTs': 59, 'QJo': 58, 'JTs': 58, 'JTo': 57
        }
        
        return preflop_strengths.get(hand_notation, 50)  # Default to 50 for unlisted hands

    def hand_rank_to_string(self, hand_rank: HandRank) -> str:
        """Convert HandRank enum to string for easier use."""
        conversion = {
            HandRank.HIGH_CARD: 'high_card',
            HandRank.PAIR: 'pair',
            HandRank.TWO_PAIR: 'two_pair',
            HandRank.THREE_OF_A_KIND: 'three_of_a_kind',
            HandRank.STRAIGHT: 'straight',
            HandRank.FLUSH: 'flush',
            HandRank.FULL_HOUSE: 'full_house',
            HandRank.FOUR_OF_A_KIND: 'four_of_a_kind',
            HandRank.STRAIGHT_FLUSH: 'straight_flush',
            HandRank.ROYAL_FLUSH: 'royal_flush'
        }
        return conversion.get(hand_rank, 'high_card')


# Global instance for easy access
hand_evaluator = EnhancedHandEvaluator() 