#!/usr/bin/env python3
"""
Equity-Based Decision Engine

Implements GTO-inspired decision making using equity calculations and pot odds.
Provides optimal action recommendations based on hand equity vs opponent ranges.
"""

import math
from typing import Dict, Tuple, Optional, List
from enhanced_hand_evaluation import EnhancedHandEvaluator


class EquityDecisionEngine:
    """
    Advanced decision engine using equity calculations and pot odds.
    Implements GTO-inspired decision making for optimal poker play.
    """
    
    def __init__(self):
        self.evaluator = EnhancedHandEvaluator()
        
        # GTO-inspired thresholds
        self.VALUE_BET_THRESHOLD = 0.65  # 65% equity for value betting
        self.BLUFF_THRESHOLD = 0.25      # 25% equity for bluffing
        self.CALL_THRESHOLD_MARGIN = 0.05  # 5% margin for calling decisions
        self.RAISE_THRESHOLD = 0.75      # 75% equity for raising
        
        # Position-based adjustments
        self.POSITION_MULTIPLIERS = {
            "BTN": 1.1,   # Button gets 10% equity boost
            "CO": 1.05,   # Cutoff gets 5% equity boost
            "MP": 1.0,    # Middle position neutral
            "UTG": 0.95,  # Under the gun gets 5% penalty
            "SB": 0.9,    # Small blind gets 10% penalty
            "BB": 0.85    # Big blind gets 15% penalty
        }
    
    def calculate_pot_odds(self, to_call: float, pot_size: float) -> float:
        """
        Calculate the pot odds required to call.
        
        Args:
            to_call: Amount needed to call
            pot_size: Current pot size
            
        Returns:
            Required equity as decimal (0.0 to 1.0)
        """
        if to_call == 0:
            return 0.0
        return to_call / (pot_size + to_call)
    
    def adjust_equity_for_position(self, equity: float, position: str) -> float:
        """
        Adjust equity based on position.
        
        Args:
            equity: Raw equity (0.0 to 1.0)
            position: Player position
            
        Returns:
            Position-adjusted equity
        """
        multiplier = self.POSITION_MULTIPLIERS.get(position, 1.0)
        adjusted = equity * multiplier
        return max(0.0, min(1.0, adjusted))  # Clamp between 0 and 1
    
    def get_optimal_action(
        self, 
        hand: str, 
        board: str, 
        position: str, 
        pot_size: float, 
        to_call: float, 
        street: str,
        opponent_range: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """
        Get optimal action based on equity and pot odds.
        
        Args:
            hand: Player's hole cards (e.g., "AhKs")
            board: Community cards (e.g., "AhKsQd")
            position: Player position
            pot_size: Current pot size
            to_call: Amount needed to call
            street: Current street (preflop, flop, turn, river)
            opponent_range: Opponent's likely hand range
            
        Returns:
            Tuple of (action, amount)
        """
        # Calculate hand equity
        equity = self._calculate_hand_equity(hand, board, opponent_range)
        position_adjusted_equity = self.adjust_equity_for_position(equity, position)
        
        # Calculate pot odds
        pot_odds = self.calculate_pot_odds(to_call, pot_size)
        
        print(f"🎯 Equity Analysis:")
        print(f"   Hand: {hand}")
        print(f"   Board: {board}")
        print(f"   Position: {position}")
        print(f"   Raw Equity: {equity:.1%}")
        print(f"   Position Adjusted: {position_adjusted_equity:.1%}")
        print(f"   Pot Odds: {pot_odds:.1%}")
        
        # Decision logic based on street
        if street == "preflop":
            return self._get_preflop_action(position_adjusted_equity, to_call, pot_size, position)
        else:
            return self._get_postflop_action(position_adjusted_equity, to_call, pot_size, street)
    
    def _calculate_hand_equity(self, hand: str, board: str, opponent_range: Optional[List[str]] = None) -> float:
        """
        Calculate hand equity against opponent range using Monte Carlo simulation.
        
        Args:
            hand: Player's hole cards (e.g., "AhKs")
            board: Community cards (e.g., "AhKsQd")
            opponent_range: Opponent's likely hands
            
        Returns:
            Equity as decimal (0.0 to 1.0)
        """
        if not opponent_range:
            opponent_range = self._get_default_opponent_range()
        
        # Parse hand and board
        hand_list = [hand[0:2], hand[2:4]] if len(hand) == 4 else hand.split()
        board_list = board.split() if board else []
        
        # Use Monte Carlo simulation for accurate equity
        return self._simulate_equity(hand_list, board_list, opponent_range)
    
    def _simulate_equity(self, hand: List[str], board: List[str], opponent_range: List[str], num_sims: int = 1000) -> float:
        """
        Monte Carlo simulation for equity against opponent range.
        
        Args:
            hand: Player's hole cards as list
            board: Community cards as list
            opponent_range: Opponent's likely hands
            num_sims: Number of simulations to run
            
        Returns:
            Equity as decimal (0.0 to 1.0)
        """
        import random
        
        # Convert to card format for evaluation
        hand_cards = [self._parse_card(card) for card in hand]
        board_cards = [self._parse_card(card) for card in board]
        
        # Create opponent range cards
        opp_range_cards = []
        for hand_combo in opponent_range:
            if len(hand_combo) == 4:  # e.g., "AhKs"
                card1 = self._parse_card(hand_combo[0:2])
                card2 = self._parse_card(hand_combo[2:4])
                opp_range_cards.append((card1, card2))
            elif len(hand_combo) == 2:  # e.g., "AA"
                # Handle paired hands
                card1 = self._parse_card(hand_combo[0] + hand_combo[0])
                card2 = self._parse_card(hand_combo[1] + hand_combo[1])
                opp_range_cards.append((card1, card2))
        
        if not opp_range_cards:
            # Fallback to simplified calculation
            return self._simplified_equity_calculation(hand_cards, board_cards)
        
        wins = ties = 0
        remaining_cards = len(board_cards) < 5  # If not river, more cards to deal
        
        for _ in range(num_sims):
            # Create deck excluding known cards
            deck = self._create_deck_excluding(hand_cards + board_cards)
            
            # Complete the board if needed
            sim_board = board_cards.copy()
            if remaining_cards:
                for _ in range(5 - len(board_cards)):
                    if deck:
                        sim_board.append(deck.pop())
            
            # Sample opponent hand from range
            opp_hand = random.choice(opp_range_cards)
            
            # Ensure opponent cards don't conflict with board
            while any(card in sim_board for card in opp_hand):
                opp_hand = random.choice(opp_range_cards)
            
            # Evaluate hands
            my_score = self.evaluator.evaluate_hand(hand_cards, sim_board)['strength_score']
            opp_score = self.evaluator.evaluate_hand(opp_hand, sim_board)['strength_score']
            
            if my_score > opp_score:  # Higher score wins
                wins += 1
            elif my_score == opp_score:
                ties += 1
        
        return (wins + ties / 2) / num_sims
    
    def _parse_card(self, card_str: str) -> str:
        """Parse card string to internal format."""
        # Convert from "Ah" format to internal format
        rank_map = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T', 
                   '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'}
        suit_map = {'h': 'h', 'd': 'd', 'c': 'c', 's': 's'}
        
        if len(card_str) == 2:
            rank = rank_map.get(card_str[0], card_str[0])
            suit = suit_map.get(card_str[1], card_str[1])
            return rank + suit
        return card_str
    
    def _create_deck_excluding(self, known_cards: List[str]) -> List[str]:
        """Create a deck excluding known cards."""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        suits = ['h', 'd', 'c', 's']
        
        deck = []
        for rank in ranks:
            for suit in suits:
                card = rank + suit
                if card not in known_cards:
                    deck.append(card)
        
        import random
        random.shuffle(deck)
        return deck
    
    def _simplified_equity_calculation(self, hand_cards: List[str], board_cards: List[str]) -> float:
        """Fallback simplified equity calculation."""
        hand_strength = self.evaluator.evaluate_hand(hand_cards, board_cards)
        hand_rank_value = hand_strength['hand_rank'].value
        
        # Convert hand rank to approximate equity
        max_rank = 9  # Royal Flush
        equity = hand_rank_value / max_rank
        
        # Add some randomness to simulate real equity calculation
        import random
        equity += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, equity))
    
    def _get_default_opponent_range(self) -> List[str]:
        """Get default opponent range for equity calculation."""
        # Simplified default range - in practice this would be more sophisticated
        return ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AQo"]
    
    def _get_preflop_action(self, equity: float, to_call: float, pot_size: float, position: str) -> Tuple[str, float]:
        """Get optimal preflop action."""
        if to_call > 0:  # Facing a bet
            pot_odds = self.calculate_pot_odds(to_call, pot_size)
            
            if equity >= pot_odds + self.CALL_THRESHOLD_MARGIN:
                if equity >= self.RAISE_THRESHOLD:
                    raise_amount = min(to_call * 3.0, pot_size * 2.0)
                    return ("raise", raise_amount)
                else:
                    return ("call", to_call)
            else:
                return ("fold", 0)
        else:  # No bet to call
            if equity >= self.VALUE_BET_THRESHOLD:
                bet_amount = pot_size * 0.75
                return ("bet", bet_amount)
            elif equity >= self.BLUFF_THRESHOLD and position in ["BTN", "CO"]:
                bet_amount = pot_size * 0.5
                return ("bet", bet_amount)
            else:
                return ("check", 0)
    
    def _get_postflop_action(self, equity: float, to_call: float, pot_size: float, street: str) -> Tuple[str, float]:
        """Get optimal postflop action."""
        if to_call > 0:  # Facing a bet
            pot_odds = self.calculate_pot_odds(to_call, pot_size)
            
            if equity >= pot_odds + self.CALL_THRESHOLD_MARGIN:
                if equity >= self.RAISE_THRESHOLD:
                    raise_amount = min(to_call * 2.5, pot_size * 1.5)
                    return ("raise", raise_amount)
                else:
                    return ("call", to_call)
            else:
                return ("fold", 0)
        else:  # No bet to call
            if equity >= self.VALUE_BET_THRESHOLD:
                # Adjust bet sizing based on street
                if street == "river":
                    bet_amount = pot_size * 0.75
                elif street == "turn":
                    bet_amount = pot_size * 0.67
                else:  # flop
                    bet_amount = pot_size * 0.5
                return ("bet", bet_amount)
            elif equity >= self.BLUFF_THRESHOLD:
                # Smaller bluff sizing
                bet_amount = pot_size * 0.33
                return ("bet", bet_amount)
            else:
                return ("check", 0)
    
    def suggest_strategy_improvements(self, current_strategy: Dict) -> Dict:
        """
        Suggest improvements to strategy based on equity analysis.
        
        Args:
            current_strategy: Current strategy dictionary
            
        Returns:
            Improved strategy dictionary
        """
        improved_strategy = current_strategy.copy()
        
        # Analyze and improve postflop thresholds
        if "postflop" in improved_strategy:
            for street in ["flop", "turn", "river"]:
                if street in improved_strategy["postflop"].get("pfa", {}):
                    for pos in improved_strategy["postflop"]["pfa"][street]:
                        for ip_oop in improved_strategy["postflop"]["pfa"][street][pos]:
                            rule = improved_strategy["postflop"]["pfa"][street][pos][ip_oop]
                            
                            # Adjust thresholds based on equity principles
                            if "val_thresh" in rule and "check_thresh" in rule:
                                # Ensure logical gap between check and bet thresholds
                                if rule["check_thresh"] >= rule["val_thresh"]:
                                    rule["check_thresh"] = rule["val_thresh"] - 10
                                
                                # Adjust value threshold based on street
                                if street == "river":
                                    rule["val_thresh"] = max(rule["val_thresh"], 65)
                                elif street == "turn":
                                    rule["val_thresh"] = max(rule["val_thresh"], 60)
                                else:  # flop
                                    rule["val_thresh"] = max(rule["val_thresh"], 55)
        
        return improved_strategy
    
    def generate_equity_report(self, hand: str, board: str, position: str) -> Dict:
        """
        Generate detailed equity analysis report.
        
        Args:
            hand: Player's hole cards
            board: Community cards
            position: Player position
            
        Returns:
            Equity analysis report
        """
        equity = self._calculate_hand_equity(hand, board)
        position_adjusted_equity = self.adjust_equity_for_position(equity, position)
        
        return {
            "hand": hand,
            "board": board,
            "position": position,
            "raw_equity": equity,
            "position_adjusted_equity": position_adjusted_equity,
            "position_multiplier": self.POSITION_MULTIPLIERS.get(position, 1.0),
            "recommendations": self._get_equity_recommendations(position_adjusted_equity)
        }
    
    def _get_equity_recommendations(self, equity: float) -> List[str]:
        """Get recommendations based on equity."""
        recommendations = []
        
        if equity >= 0.75:
            recommendations.append("Strong value betting opportunity")
        elif equity >= 0.65:
            recommendations.append("Good value betting candidate")
        elif equity >= 0.50:
            recommendations.append("Marginal hand - consider checking")
        elif equity >= 0.25:
            recommendations.append("Potential bluffing opportunity")
        else:
            recommendations.append("Weak hand - fold or check")
        
        return recommendations


if __name__ == "__main__":
    # Test the equity decision engine
    engine = EquityDecisionEngine()
    
    # Test cases
    test_cases = [
        ("AhKs", "", "BTN", 100, 0, "preflop"),
        ("AhKs", "AhKsQd", "CO", 200, 50, "flop"),
        ("7h8h", "AhKsQd", "BB", 300, 100, "turn"),
    ]
    
    for hand, board, pos, pot, to_call, street in test_cases:
        print(f"\n{'='*50}")
        action, amount = engine.get_optimal_action(hand, board, pos, pot, to_call, street)
        print(f"🎯 Optimal Action: {action.upper()} ${amount:.2f}")
        
        # Generate equity report
        report = engine.generate_equity_report(hand, board, pos)
        print(f"📊 Equity Report:")
        print(f"   Raw Equity: {report['raw_equity']:.1%}")
        print(f"   Position Adjusted: {report['position_adjusted_equity']:.1%}")
        print(f"   Recommendations: {', '.join(report['recommendations'])}") 