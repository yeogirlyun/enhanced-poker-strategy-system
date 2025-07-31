#!/usr/bin/env python3
"""
Integrated Poker Trainer

This module provides a comprehensive training system that integrates
with the enhanced hand evaluator and dynamic position manager.
"""

import time
from typing import Dict, List, Tuple, Optional
from enhanced_hand_evaluation import hand_evaluator, HandRank
from dynamic_position_manager import DynamicPositionManager
from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType


class IntegratedTrainer:
    """Integrated poker training system with enhanced evaluation."""
    
    def __init__(self, num_players: int = 6):
        self.num_players = num_players
        self.position_manager = DynamicPositionManager(num_players)
        self.state_machine = ImprovedPokerStateMachine(num_players)
        self.current_hand = 0
        self.stats = {
            'hands_played': 0,
            'correct_decisions': 0,
            'total_decisions': 0,
            'profit': 0.0
        }
    
    def _get_postflop_evaluation(self, hole: List[str], board: List[str], 
                                position: str, history: List[str]) -> Dict:
        """Gets a full postflop evaluation using the enhanced evaluator."""
        evaluation = hand_evaluator.evaluate_hand(hole, board)
        
        # Convert HandRank enum to string using the new method
        rank_str = hand_evaluator.hand_rank_to_string(evaluation['hand_rank'])
        
        return {
            'hs': evaluation.get('strength_score', 0),
            'rank': rank_str,
            'is_draw': len(evaluation.get('draws', [])) > 0,
            'outs': evaluation.get('outs', 0),
            'board_texture': 'unknown',  # Simplified for now
            'equity_estimate': evaluation.get('strength_score', 50),
        }
    
    def _run_betting_round(self, street: str, hand_state: Dict) -> None:
        """Manages a single round of betting by delegating to the state machine."""
        # Reset street-specific state
        if street != 'preflop':
            for p in self.state_machine.game_state.players:
                p.has_acted_this_round = False
            hand_state['to_call'] = 0.0

        # Let the state machine handle the betting round until it's complete
        while not self.state_machine.is_round_complete():
            if len([p for p in self.state_machine.game_state.players if p.is_active]) <= 1:
                break  # Hand is over

            player = self.state_machine.get_action_player()
            if not player or not player.is_active:
                # If no one can act, the round is over
                break

            # Get action (from user or bot)
            action, size = self._get_player_action(player, street, hand_state)
            
            # Execute the action via the state machine
            self.state_machine.execute_action(player, action, size)
            
            # Update local hand_state from the authoritative state machine
            hand_state['pot'] = self.state_machine.game_state.pot
            hand_state['to_call'] = self.state_machine.game_state.current_bet
    
    def _get_player_action(self, player, street: str, hand_state: Dict) -> Tuple[str, float]:
        """Get action from player (simplified for training)."""
        # Simplified action logic for training
        if player.is_human:
            return self._get_human_action(player, street, hand_state)
        else:
            return self._get_bot_action(player, street, hand_state)
    
    def _get_human_action(self, player, street: str, hand_state: Dict) -> Tuple[str, float]:
        """Get action from human player."""
        print(f"\n🎮 Your turn! Position: {player.position}")
        print(f"Hand: {' '.join(player.cards)}")
        print(f"Pot: {hand_state['pot']:.1f} BB")
        print(f"To call: {hand_state['to_call']:.1f} BB")
        
        action = input("Action (f/c/b/r): ").lower().strip()
        
        if action == 'f':
            return ('fold', 0)
        elif action == 'c':
            return ('call', hand_state['to_call'])
        elif action == 'b':
            size = float(input("Bet size: "))
            return ('bet', size)
        elif action == 'r':
            size = float(input("Raise size: "))
            return ('raise', size)
        else:
            print("Invalid action, folding.")
            return ('fold', 0)
    
    def _get_bot_action(self, player, street: str, hand_state: Dict) -> Tuple[str, float]:
        """Get action from bot player."""
        # Simple bot logic for training
        if street == 'preflop':
            strength = hand_evaluator.get_preflop_hand_strength(player.cards)
            if strength > 70:
                return ('raise', min(3.0, player.stack))
            elif strength > 50:
                return ('call', hand_state['to_call'])
            else:
                return ('fold', 0)
        else:
            # Postflop evaluation
            evaluation = self._get_postflop_evaluation(
                player.cards, hand_state.get('board', []), 
                player.position, []
            )
            
            if evaluation['hs'] > 60:
                return ('bet', min(hand_state['pot'] * 0.75, player.stack))
            elif evaluation['hs'] > 40:
                return ('call', hand_state['to_call'])
            else:
                return ('fold', 0)
    
    def run_training_session(self, num_hands: int = 10) -> None:
        """Run a complete training session."""
        print(f"🎮 Starting Integrated Poker Training Session")
        print(f"Hands to play: {num_hands}")
        print("=" * 50)
        
        for hand_num in range(num_hands):
            self.current_hand = hand_num + 1
            print(f"\n🎯 HAND #{self.current_hand}")
            print("-" * 30)
            
            # Start new hand
            self.state_machine.start_hand()
            
            # Run through all streets
            streets = ['preflop', 'flop', 'turn', 'river']
            hand_state = {
                'pot': 1.5,  # Blinds
                'to_call': 1.0,  # BB
                'board': []
            }
            
            for street in streets:
                if len([p for p in self.state_machine.game_state.players if p.is_active]) <= 1:
                    break
                
                print(f"\n📊 {street.upper()}")
                if street != 'preflop':
                    # Deal community cards
                    if street == 'flop':
                        hand_state['board'] = ['7c', '8h', '9s']
                    elif street == 'turn':
                        hand_state['board'].append('2d')
                    elif street == 'river':
                        hand_state['board'].append('Ah')
                    print(f"Board: {' '.join(hand_state['board'])}")
                
                self._run_betting_round(street, hand_state)
            
            # Showdown
            self._showdown(hand_state)
            
            # Move dealer button
            self.position_manager.move_dealer_button()
        
        self._print_session_summary()
    
    def _showdown(self, hand_state: Dict) -> None:
        """Handle showdown and determine winner."""
        print(f"\n🏆 SHOWDOWN")
        active_players = [p for p in self.state_machine.game_state.players if p.is_active]
        
        if not active_players:
            print("No active players at showdown.")
            return
        
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"{winner.name} wins uncontested pot of {hand_state['pot']:.1f} BB")
            winner.stack += hand_state['pot']
        else:
            # Use enhanced hand evaluator to determine winner
            best_rank = None
            winner = None
            
            for player in active_players:
                evaluation = hand_evaluator.evaluate_hand(player.cards, hand_state['board'])
                player_rank = (evaluation['hand_rank'], evaluation['rank_values'])
                
                if winner is None or hand_evaluator._compare_hands(player_rank, best_rank) > 0:
                    best_rank = player_rank
                    winner = player
            
            print(f"{winner.name} wins {hand_state['pot']:.1f} BB with {evaluation['hand_description']}")
            for p in active_players:
                if p != winner:
                    print(f"  {p.name} shows {' '.join(p.cards)}")
            
            winner.stack += hand_state['pot']
    
    def _print_session_summary(self) -> None:
        """Print training session summary."""
        print(f"\n📊 TRAINING SESSION SUMMARY")
        print("=" * 40)
        print(f"Hands played: {self.current_hand}")
        print(f"Total decisions: {self.stats['total_decisions']}")
        print(f"Correct decisions: {self.stats['correct_decisions']}")
        if self.stats['total_decisions'] > 0:
            accuracy = (self.stats['correct_decisions'] / self.stats['total_decisions']) * 100
            print(f"Accuracy: {accuracy:.1f}%")


def main():
    """Main function to run the integrated trainer."""
    trainer = IntegratedTrainer(num_players=6)
    
    try:
        num_hands = int(input("How many hands to play? (default: 5): ") or "5")
        trainer.run_training_session(num_hands)
    except KeyboardInterrupt:
        print("\n👋 Training session interrupted by user")
    except Exception as e:
        print(f"❌ Error during training: {e}")


if __name__ == "__main__":
    main() 