# filename: enhanced_hand_evaluation.py
"""
Enhanced Hand Evaluation System for Hold'em Trainer

REVISION HISTORY:
================

Version 1.0 (2025-01-25) - Initial Implementation
- Created EnhancedHandEvaluator with accurate hand ranking
- Implemented proper 5-card hand evaluation using itertools combinations
- Added comprehensive draw detection:
  * Flush draws with out counting
  * Straight draws (open-ended and gutshot)
  * Combo draws with multiple outs
- Created board texture analysis system:
  * Dry, semi-dry, wet, very wet classifications
  * Considers pairs, flush possibilities, straight potential
- Added equity estimation framework
- Implemented PositionAdjustedEvaluator for contextual analysis
- Created EquityCalculator with Monte Carlo simulation capability
- Added nut potential and reverse implied odds assessment
- Comprehensive hand strength calculation with board texture adjustments

Features:
- Accurate hand ranking for all poker hands
- Advanced draw detection and out counting
- Board texture analysis for strategic adjustments
- Position-relative hand strength calculations
- Equity estimation against opponent ranges
- Monte Carlo simulation capabilities
- Nut potential and reverse implied odds evaluation
- Integration-ready design for trainer systems
"""

import itertools
from collections import Counter
from enum import IntEnum
import random

class HandRank(IntEnum):
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

class BoardTexture(IntEnum):
    DRY = 1
    SEMI_DRY = 2
    WET = 3
    VERY_WET = 4

class EnhancedHandEvaluator:
    """Advanced hand evaluation with equity calculations."""
    
    SUITS = 'cdhs'
    RANKS = '23456789TJQKA'
    RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}
    VALUE_RANKS = {i: r for r, i in RANK_VALUES.items()}
    
    def __init__(self):
        self.deck = self._create_deck()
    
    def _create_deck(self):
        """Create a standard 52-card deck."""
        return [rank + suit for rank in self.RANKS for suit in self.SUITS]
    
    def parse_card(self, card_str):
        """Parse card string into (rank_value, suit)."""
        return (self.RANK_VALUES[card_str[0]], card_str[1])
    
    def evaluate_hand(self, hole_cards, board_cards):
        """Comprehensive hand evaluation."""
        all_cards = hole_cards + board_cards
        if len(all_cards) < 5:
            return self._evaluate_incomplete_hand(hole_cards, board_cards)
        
        # Find best 5-card hand
        best_hand = self._find_best_hand(all_cards)
        hand_rank, rank_values = self._rank_hand(best_hand)
        
        # Additional analysis
        draws = self._analyze_draws(hole_cards, board_cards)
        outs = self._count_outs(hole_cards, board_cards)
        board_texture = self._analyze_board_texture(board_cards)
        
        return {
            'hand_rank': hand_rank,
            'rank_values': rank_values,
            'best_hand': best_hand,
            'draws': draws,
            'outs': outs,
            'board_texture': board_texture,
            'hand_strength': self._calculate_hand_strength(hand_rank, rank_values, board_texture),
            'equity_estimate': self._estimate_equity(hole_cards, board_cards, hand_rank),
            'nut_potential': self._assess_nut_potential(hole_cards, board_cards),
            'reverse_implied_odds': self._assess_reverse_implied_odds(hole_cards, board_cards)
        }
    
    def _find_best_hand(self, cards):
        """Find the best 5-card hand from available cards."""
        if len(cards) == 5:
            return cards
        
        best_hand = None
        best_rank = (0, [])
        
        for combo in itertools.combinations(cards, 5):
            rank_info = self._rank_hand(list(combo))
            if self._compare_hands(rank_info, best_rank) > 0:
                best_rank = rank_info
                best_hand = list(combo)
        
        return best_hand
    
    def _rank_hand(self, cards):
        """Rank a 5-card hand."""
        parsed_cards = [self.parse_card(card) for card in cards]
        ranks = [card[0] for card in parsed_cards]
        suits = [card[1] for card in parsed_cards]
        
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        sorted_ranks = sorted(ranks, reverse=True)
        
        is_flush = len(suit_counts) == 1
        is_straight = self._is_straight(sorted_ranks)
        
        # Check for special straights (A-2-3-4-5)
        if sorted_ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            sorted_ranks = [5, 4, 3, 2, 1]  # Ace-low straight
        
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Determine hand rank
        if is_straight and is_flush:
            if sorted_ranks[0] == 14:  # Ace-high straight flush
                return (HandRank.ROYAL_FLUSH, sorted_ranks)
            return (HandRank.STRAIGHT_FLUSH, sorted_ranks)
        elif counts == [4, 1]:
            quads = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return (HandRank.FOUR_OF_A_KIND, [quads, kicker])
        elif counts == [3, 2]:
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            return (HandRank.FULL_HOUSE, [trips, pair])
        elif is_flush:
            return (HandRank.FLUSH, sorted_ranks)
        elif is_straight:
            return (HandRank.STRAIGHT, sorted_ranks)
        elif counts == [3, 1, 1]:
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return (HandRank.THREE_OF_A_KIND, [trips] + kickers)
        elif counts == [2, 2, 1]:
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return (HandRank.TWO_PAIR, pairs + [kicker])
        elif counts == [2, 1, 1, 1]:
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return (HandRank.PAIR, [pair] + kickers)
        else:
            return (HandRank.HIGH_CARD, sorted_ranks)
    
    def _is_straight(self, ranks):
        """Check if ranks form a straight."""
        if len(set(ranks)) != 5:
            return False
        return max(ranks) - min(ranks) == 4
    
    def _compare_hands(self, hand1, hand2):
        """Compare two hands. Return 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
        rank1, values1 = hand1
        rank2, values2 = hand2
        
        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1
        else:
            # Same rank, compare values
            for v1, v2 in zip(values1, values2):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0
    
    def _evaluate_incomplete_hand(self, hole_cards, board_cards):
        """Evaluate hand with fewer than 5 total cards."""
        all_cards = hole_cards + board_cards
        
        if len(all_cards) < 2:
            return {
                'hand_rank': HandRank.HIGH_CARD,
                'hand_strength': 5,
                'draws': [],
                'outs': 0,
                'board_texture': BoardTexture.DRY
            }
        
        # Basic evaluation for incomplete hands
        parsed_cards = [self.parse_card(card) for card in all_cards]
        ranks = [card[0] for card in parsed_cards]
        suits = [card[1] for card in parsed_cards]
        
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        
        # Determine basic hand strength
        if max(rank_counts.values()) >= 2:
            hand_rank = HandRank.PAIR
            strength = 15 + max(ranks) * 2
        else:
            hand_rank = HandRank.HIGH_CARD
            strength = max(ranks)
        
        # Check for draws
        draws = self._analyze_draws(hole_cards, board_cards)
        outs = self._count_outs(hole_cards, board_cards)
        
        return {
            'hand_rank': hand_rank,
            'hand_strength': strength,
            'draws': draws,
            'outs': outs,
            'board_texture': self._analyze_board_texture(board_cards) if board_cards else BoardTexture.DRY,
            'equity_estimate': self._estimate_equity(hole_cards, board_cards, hand_rank),
            'nut_potential': self._assess_nut_potential(hole_cards, board_cards),
            'reverse_implied_odds': self._assess_reverse_implied_odds(hole_cards, board_cards)
        }
    
    def _analyze_draws(self, hole_cards, board_cards):
        """Analyze potential draws."""
        if len(board_cards) < 3:
            return []
        
        all_cards = hole_cards + board_cards
        draws = []
        
        # Check for flush draws
        if self._has_flush_draw(all_cards):
            draws.append('flush_draw')
        
        # Check for straight draws
        straight_type = self._analyze_straight_draws(all_cards)
        if straight_type:
            draws.append(straight_type)
        
        # Check for combo draws
        if len(draws) > 1:
            draws.append('combo_draw')
        
        return draws
    
    def _has_flush_draw(self, cards):
        """Check if we have a flush draw."""
        parsed_cards = [self.parse_card(card) for card in cards]
        suits = [card[1] for card in parsed_cards]
        suit_counts = Counter(suits)
        return max(suit_counts.values()) == 4
    
    def _analyze_straight_draws(self, cards):
        """Analyze straight draw possibilities."""
        parsed_cards = [self.parse_card(card) for card in cards]
        ranks = sorted(set([card[0] for card in parsed_cards]))
        
        # Check for open-ended straight draw
        if self._has_open_ended_draw(ranks):
            return 'open_ended_draw'
        
        # Check for gutshot
        if self._has_gutshot_draw(ranks):
            return 'gutshot_draw'
        
        return None
    
    def _has_open_ended_draw(self, ranks):
        """Check for open-ended straight draw."""
        for i in range(len(ranks) - 3):
            consecutive = 0
            for j in range(i, len(ranks)):
                if j == i or ranks[j] == ranks[j-1] + 1:
                    consecutive += 1
                else:
                    break
            
            if consecutive >= 4:
                # Check if we can complete on both ends
                low_complete = ranks[i] - 1 >= 2
                high_complete = ranks[i + consecutive - 1] + 1 <= 14
                if low_complete or high_complete:
                    return True
        
        return False
    
    def _has_gutshot_draw(self, ranks):
        """Check for gutshot straight draw."""
        # Look for 4 cards that need exactly one in the middle
        for combo in itertools.combinations(ranks, 4):
            sorted_combo = sorted(combo)
            gaps = []
            for i in range(len(sorted_combo) - 1):
                if sorted_combo[i+1] - sorted_combo[i] > 1:
                    gaps.append((sorted_combo[i], sorted_combo[i+1]))
            
            # Exactly one gap of size 1
            if len(gaps) == 1 and gaps[0][1] - gaps[0][0] == 2:
                return True
        
        return False
    
    def _count_outs(self, hole_cards, board_cards):
        """Count outs for improving the hand."""
        if len(board_cards) < 3:
            return 0
        
        all_cards = hole_cards + board_cards
        used_cards = set(all_cards)
        outs = 0
        
        # Count flush outs
        if self._has_flush_draw(all_cards):
            parsed_cards = [self.parse_card(card) for card in all_cards]
            suits = [card[1] for card in parsed_cards]
            flush_suit = max(set(suits), key=suits.count)
            
            for rank in self.RANKS:
                card = rank + flush_suit
                if card not in used_cards:
                    outs += 1
        
        # Count straight outs (simplified)
        if self._analyze_straight_draws(all_cards):
            # This is a simplified calculation
            # In practice, you'd want to be more precise about which cards complete straights
            straight_type = self._analyze_straight_draws(all_cards)
            if straight_type == 'open_ended_draw':
                outs += 8  # 4 cards on each end
            elif straight_type == 'gutshot_draw':
                outs += 4  # 4 cards in the middle
        
        return min(outs, 15)  # Cap at 15 outs
    
    def _analyze_board_texture(self, board_cards):
        """Analyze how wet or dry the board is."""
        if len(board_cards) < 3:
            return BoardTexture.DRY
        
        parsed_cards = [self.parse_card(card) for card in board_cards]
        ranks = [card[0] for card in parsed_cards]
        suits = [card[1] for card in parsed_cards]
        
        wetness_score = 0
        
        # Check for pairs on board
        rank_counts = Counter(ranks)
        if max(rank_counts.values()) >= 2:
            wetness_score += 1
        
        # Check for flush possibilities
        suit_counts = Counter(suits)
        if max(suit_counts.values()) >= 3:
            wetness_score += 2
        
        # Check for straight possibilities
        sorted_ranks = sorted(set(ranks))
        for i in range(len(sorted_ranks) - 2):
            if sorted_ranks[i+2] - sorted_ranks[i] <= 4:
                wetness_score += 2
                break
        
        # Check for high cards
        high_cards = sum(1 for rank in ranks if rank >= 10)
        if high_cards >= 2:
            wetness_score += 1
        
        # Classify texture
        if wetness_score <= 1:
            return BoardTexture.DRY
        elif wetness_score <= 3:
            return BoardTexture.SEMI_DRY
        elif wetness_score <= 5:
            return BoardTexture.WET
        else:
            return BoardTexture.VERY_WET
    
    def _calculate_hand_strength(self, hand_rank, rank_values, board_texture):
        """Calculate normalized hand strength (0-100)."""
        base_strength = {
            HandRank.HIGH_CARD: 5,
            HandRank.PAIR: 25,
            HandRank.TWO_PAIR: 45,
            HandRank.THREE_OF_A_KIND: 65,
            HandRank.STRAIGHT: 75,
            HandRank.FLUSH: 80,
            HandRank.FULL_HOUSE: 90,
            HandRank.FOUR_OF_A_KIND: 95,
            HandRank.STRAIGHT_FLUSH: 98,
            HandRank.ROYAL_FLUSH: 100
        }
        
        strength = base_strength.get(hand_rank, 0)
        
        # Adjust for rank values
        if rank_values:
            high_card_bonus = (rank_values[0] - 2) * 2  # 0-24 bonus
            strength += min(high_card_bonus, 15)
        
        # Adjust for board texture
        texture_adjustment = {
            BoardTexture.DRY: 5,
            BoardTexture.SEMI_DRY: 0,
            BoardTexture.WET: -5,
            BoardTexture.VERY_WET: -10
        }
        
        strength += texture_adjustment.get(board_texture, 0)
        
        return max(0, min(100, strength))
    
    def _estimate_equity(self, hole_cards, board_cards, hand_rank):
        """Estimate equity against a random range (simplified)."""
        # This is a simplified equity estimation
        # In a real implementation, you'd want Monte Carlo simulation
        
        base_equity = {
            HandRank.HIGH_CARD: 15,
            HandRank.PAIR: 35,
            HandRank.TWO_PAIR: 55,
            HandRank.THREE_OF_A_KIND: 75,
            HandRank.STRAIGHT: 85,
            HandRank.FLUSH: 90,
            HandRank.FULL_HOUSE: 95,
            HandRank.FOUR_OF_A_KIND: 98,
            HandRank.STRAIGHT_FLUSH: 99,
            HandRank.ROYAL_FLUSH: 100
        }
        
        equity = base_equity.get(hand_rank, 10)
        
        # Adjust based on board texture and remaining cards
        cards_to_come = 5 - len(board_cards)
        if cards_to_come > 0:
            # More variance with more cards to come
            equity_adjustment = random.uniform(-10, 10) * (cards_to_come / 2)
            equity += equity_adjustment
        
        return max(5, min(95, equity))
    
    def _assess_nut_potential(self, hole_cards, board_cards):
        """Assess potential to make the nuts."""
        if len(board_cards) < 3:
            return 'unknown'
        
        parsed_hole = [self.parse_card(card) for card in hole_cards]
        hole_ranks = [card[0] for card in parsed_hole]
        hole_suits = [card[1] for card in parsed_hole]
        
        # Check for nut flush potential
        for suit in hole_suits:
            if 14 in hole_ranks and hole_suits.count(suit) >= 1:  # Ace in hole
                return 'high'
        
        # Check for high cards for straight potential
        if max(hole_ranks) >= 10:
            return 'medium'
        
        return 'low'
    
    def _assess_reverse_implied_odds(self, hole_cards, board_cards):
        """Assess reverse implied odds potential."""
        if len(board_cards) < 3:
            return 'low'
        
        parsed_hole = [self.parse_card(card) for card in hole_cards]
        hole_ranks = [card[0] for card in parsed_hole]
        
        # High reverse implied odds if we have low cards on a high board
        board_high_cards = sum(1 for card in board_cards 
                              if self.parse_card(card)[0] >= 10)
        hole_low_cards = sum(1 for rank in hole_ranks if rank <= 9)
        
        if board_high_cards >= 2 and hole_low_cards >= 1:
            return 'high'
        elif board_high_cards >= 1 or hole_low_cards >= 1:
            return 'medium'
        
        return 'low'

class PositionAdjustedEvaluator:
    """Adjust hand strength based on position and action."""
    
    def __init__(self, base_evaluator):
        self.base_evaluator = base_evaluator
        
        # Position multipliers for hand strength
        self.position_multipliers = {
            'UTG': 0.85,
            'MP': 0.90,
            'CO': 0.95,
            'BTN': 1.05,
            'SB': 0.90,
            'BB': 0.95
        }
        
        # Action adjustments
        self.action_adjustments = {
            'no_action': 0,
            'single_bet': -5,
            'raise': -10,
            'multiple_bets': -15
        }
    
    def evaluate_hand_in_context(self, hole_cards, board_cards, position, 
                                action_history, num_opponents=1):
        """Evaluate hand strength considering position and action."""
        
        # Get base evaluation
        base_eval = self.base_evaluator.evaluate_hand(hole_cards, board_cards)
        base_strength = base_eval['hand_strength']
        
        # Apply position adjustment
        pos_multiplier = self.position_multipliers.get(position, 1.0)
        adjusted_strength = base_strength * pos_multiplier
        
        # Apply action adjustment
        action_type = self._classify_action_history(action_history)
        action_adj = self.action_adjustments.get(action_type, 0)
        adjusted_strength += action_adj
        
        # Apply opponent adjustment
        if num_opponents > 1:
            opponent_penalty = (num_opponents - 1) * 3
            adjusted_strength -= opponent_penalty
        
        # Create adjusted evaluation
        adjusted_eval = base_eval.copy()
        adjusted_eval['hand_strength'] = max(5, min(100, adjusted_strength))
        adjusted_eval['position_adjusted'] = True
        adjusted_eval['original_strength'] = base_strength
        adjusted_eval['position_multiplier'] = pos_multiplier
        adjusted_eval['action_adjustment'] = action_adj
        
        return adjusted_eval
    
    def _classify_action_history(self, action_history):
        """Classify the action history for adjustment purposes."""
        if not action_history:
            return 'no_action'
        elif len(action_history) == 1:
            return 'single_bet' if action_history[0] in ['bet', 'raise'] else 'no_action'
        elif 'raise' in action_history:
            return 'raise'
        elif action_history.count('bet') > 1:
            return 'multiple_bets'
        else:
            return 'single_bet'

class EquityCalculator:
    """Monte Carlo equity calculator."""
    
    def __init__(self, hand_evaluator, num_simulations=1000):
        self.hand_evaluator = hand_evaluator
        self.num_simulations = num_simulations
    
    def calculate_equity(self, hero_hole, board_cards, villain_range, 
                        dead_cards=None):
        """Calculate equity against a specific range."""
        if dead_cards is None:
            dead_cards = []
        
        used_cards = set(hero_hole + board_cards + dead_cards)
        available_deck = [card for card in self.hand_evaluator.deck 
                         if card not in used_cards]
        
        wins = 0
        ties = 0
        total_simulations = 0
        
        # Sample villain hands from range
        for _ in range(self.num_simulations):
            # Random villain hand from range (simplified - assumes range is list of hands)
            if isinstance(villain_range, list):
                villain_hole = random.choice(villain_range)
                if any(card in used_cards for card in villain_hole):
                    continue
            else:
                # Random hand from remaining deck
                villain_hole = random.sample([card for card in available_deck 
                                            if card not in hero_hole], 2)
            
            # Complete the board if needed
            cards_needed = 5 - len(board_cards)
            if cards_needed > 0:
                remaining_deck = [card for card in available_deck 
                                if card not in villain_hole]
                if len(remaining_deck) < cards_needed:
                    continue
                complete_board = board_cards + random.sample(remaining_deck, cards_needed)
            else:
                complete_board = board_cards
            
            # Evaluate both hands
            hero_eval = self.hand_evaluator.evaluate_hand(hero_hole, complete_board)
            villain_eval = self.hand_evaluator.evaluate_hand(villain_hole, complete_board)
            
            # Compare hands
            hero_hand = (hero_eval['hand_rank'], hero_eval['rank_values'])
            villain_hand = (villain_eval['hand_rank'], villain_eval['rank_values'])
            
            comparison = self.hand_evaluator._compare_hands(hero_hand, villain_hand)
            
            if comparison > 0:
                wins += 1
            elif comparison == 0:
                ties += 1
            
            total_simulations += 1
        
        if total_simulations == 0:
            return 50  # Default equity
        
        equity = (wins + ties * 0.5) / total_simulations * 100
        return equity

def main():
    """Test the enhanced hand evaluation system."""
    evaluator = EnhancedHandEvaluator()
    position_evaluator = PositionAdjustedEvaluator(evaluator)
    equity_calc = EquityCalculator(evaluator, 100)  # Quick test with 100 sims
    
    # Test cases
    test_cases = [
        {
            'hole': ['As', 'Kh'],
            'board': ['Ac', '7s', '2d'],
            'position': 'BTN',
            'action': [],
            'description': 'Top pair, Ace kicker on dry board'
        },
        {
            'hole': ['9s', '8s'],
            'board': ['7s', '6c', '2s'],
            'position': 'UTG',
            'action': ['bet', 'raise'],
            'description': 'Combo draw facing aggression'
        },
        {
            'hole': ['Qh', 'Jd'],
            'board': ['Ts', '9c', '8h', '2s'],
            'position': 'CO',
            'action': ['bet'],
            'description': 'Straight on turn'
        }
    ]
    
    print("ENHANCED HAND EVALUATION TESTS")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Hand: {' '.join(test['hole'])}")
        print(f"Board: {' '.join(test['board'])}")
        print(f"Position: {test['position']}")
        print(f"Action: {test['action']}")
        
        # Basic evaluation
        basic_eval = evaluator.evaluate_hand(test['hole'], test['board'])
        print(f"\nBasic evaluation:")
        print(f"  Hand rank: {basic_eval['hand_rank'].name}")
        print(f"  Hand strength: {basic_eval['hand_strength']}")
        print(f"  Board texture: {basic_eval['board_texture'].name}")
        print(f"  Draws: {basic_eval['draws']}")
        print(f"  Outs: {basic_eval['outs']}")
        
        # Position-adjusted evaluation
        pos_eval = position_evaluator.evaluate_hand_in_context(
            test['hole'], test['board'], test['position'], test['action']
        )
        print(f"\nPosition-adjusted evaluation:")
        print(f"  Adjusted strength: {pos_eval['hand_strength']}")
        print(f"  Original strength: {pos_eval['original_strength']}")
        print(f"  Position multiplier: {pos_eval['position_multiplier']:.2f}")
        print(f"  Action adjustment: {pos_eval['action_adjustment']}")
        
        # Equity calculation (simplified)
        if len(test['board']) >= 3:
            villain_range = [['7h', '7d'], ['Ah', 'Qc'], ['Ks', 'Qd']]  # Simple range
            equity = equity_calc.calculate_equity(
                test['hole'], test['board'], villain_range
            )
            print(f"\nEquity vs sample range: {equity:.1f}%")
        
        print("-" * 50)

if __name__ == '__main__':
    main()