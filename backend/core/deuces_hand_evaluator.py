#!/usr/bin/env python3
"""
Deuces-based Hand Evaluator

This module provides a poker hand evaluator that uses the proven deuces library
for accurate and reliable hand evaluation and comparison.
"""

from typing import List, Dict, Any
from deuces import Card, Evaluator


class DeucesHandEvaluator:
    """Hand evaluator using the deuces library for proven accuracy."""
    
    def __init__(self):
        self.evaluator = Evaluator()
        
    def evaluate_hand(self, hole_cards: List[str], board_cards: List[str]) -> Dict[str, Any]:
        """
        Evaluate a poker hand using deuces library.
        
        Args:
            hole_cards: List of hole cards (e.g., ['Ah', 'Kd'])
            board_cards: List of board cards (e.g., ['Qh', 'Jh', 'Th', '9h', '8h'])
        
        Returns:
            Dict containing:
            - hand_score: Integer score (lower = better)
            - hand_rank: Rank class (1=Straight Flush, 8=High Card)
            - hand_description: Human readable description
            - strength_score: Percentile strength (0-100)
        """
        try:
            # Convert our card format to deuces format
            deuces_hole = self._convert_cards_to_deuces(hole_cards)
            deuces_board = self._convert_cards_to_deuces(board_cards)
            
            if len(deuces_hole) != 2:
                raise ValueError(f"Expected 2 hole cards, got {len(deuces_hole)}")
            
            if len(deuces_board) < 3:
                raise ValueError(f"Expected at least 3 board cards, got {len(deuces_board)}")
            
            # Evaluate hand using deuces
            hand_score = self.evaluator.evaluate(deuces_board, deuces_hole)
            hand_rank = self.evaluator.get_rank_class(hand_score)
            hand_description = self.evaluator.class_to_string(hand_rank)
            
            # Calculate strength score (percentile)
            strength_percentage = 1.0 - self.evaluator.get_five_card_rank_percentage(hand_score)
            strength_score = strength_percentage * 100
            
            return {
                'hand_score': hand_score,          # Lower = better (for comparison)
                'hand_rank': hand_rank,            # Rank class (1-8)
                'hand_description': hand_description,
                'strength_score': strength_score,   # 0-100 percentile
                'hole_cards': list(hole_cards),
                'board_cards': list(board_cards)
            }
            
        except Exception as e:
            # Fallback evaluation for invalid hands
            return {
                'hand_score': 9999,  # Worst possible score
                'hand_rank': 8,      # High card
                'hand_description': 'Invalid Hand',
                'strength_score': 0.0,
                'hole_cards': list(hole_cards),
                'board_cards': list(board_cards),
                'error': str(e)
            }
    
    def _convert_cards_to_deuces(self, cards: List[str]) -> List[int]:
        """Convert our card format to deuces format."""
        deuces_cards = []
        for card_str in cards:
            try:
                # Convert our format (e.g., 'Ah') to deuces format
                deuces_card = Card.new(card_str)
                deuces_cards.append(deuces_card)
            except Exception:
                # Skip invalid cards
                continue
        return deuces_cards
    
    def compare_hands(self, eval1: Dict[str, Any], eval2: Dict[str, Any]) -> int:
        """
        Compare two hand evaluations.
        
        Returns:
            -1 if eval1 is better than eval2
             0 if they are equal (true tie)
             1 if eval2 is better than eval1
        """
        score1 = eval1.get('hand_score', 9999)
        score2 = eval2.get('hand_score', 9999)
        
        if score1 < score2:
            return -1
        elif score1 > score2:
            return 1
        else:
            return 0
    
    def determine_winners(self, player_evaluations: List[tuple]) -> List[tuple]:
        """
        Determine winners from a list of (player, evaluation) tuples.
        
        Args:
            player_evaluations: List of (player_object, hand_evaluation_dict) tuples
            
        Returns:
            List of (player, evaluation) tuples for all winners (ties included)
        """
        if not player_evaluations:
            return []
        
        # Sort by hand score (lower = better)
        sorted_hands = sorted(player_evaluations, key=lambda x: x[1].get('hand_score', 9999))
        
        # Find all players with the best (lowest) score
        best_score = sorted_hands[0][1].get('hand_score', 9999)
        winners = [item for item in sorted_hands if item[1].get('hand_score', 9999) == best_score]
        
        return winners
