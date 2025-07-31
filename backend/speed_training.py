#!/usr/bin/env python3
"""
Speed Training Module

This module provides time-limited decision training with improved timer logic.
"""

import time
import random
from typing import Dict, List, Tuple
from enhanced_hand_evaluation import hand_evaluator


class SpeedTraining:
    """Time-limited decision training with conceptual timer."""
    
    def __init__(self, time_limit: int = 10, target_count: int = 25):
        self.time_limit = time_limit  # seconds per decision
        self.target_count = target_count
        self.time_penalties = 0
        self.stats = {
            'total': 0,
            'correct': 0,
            'average_time': 0.0,
            'time_penalties': 0
        }
    
    def setup_mode(self):
        """Setup speed training mode."""
        print(f"\n⚡ SPEED TRAINING MODE")
        print(f"Time limit: {self.time_limit} seconds per decision")
        print(f"Target: {self.target_count} decisions")
        print("Make quick, accurate decisions!")
    
    def should_continue(self) -> bool:
        """Check if training should continue."""
        return self.stats['total'] < self.target_count
    
    def generate_scenario(self) -> Dict:
        """Generate random scenarios for speed training."""
        streets = ['preflop', 'flop', 'turn', 'river']
        positions = ['UTG', 'MP', 'CO', 'BTN']
        
        street = random.choice(streets)
        position = random.choice(positions)
        
        # Generate realistic hands and boards
        hands = ['AA', 'KK', 'QQ', 'AKs', 'AKo', 'JJ', 'TT', 'AQs', '99', '88', 'AJs', 'KQs']
        hole_cards = random.choice(hands)
        
        if street == 'preflop':
            board_cards = ''
            pot_size = 3.5
            to_call = random.choice([0, 2.5])  # Open or facing raise
        else:
            boards = ['As Kh 7c', 'Ts 9h 4c', 'Qs Js 4s', '8s 7h 6c']
            board_cards = random.choice(boards)
            if street == 'turn':
                board_cards += ' 2d'
            elif street == 'river':
                board_cards += ' 2d 9h'
            
            pot_size = random.choice([15, 25, 35])
            to_call = random.choice([0, pot_size * 0.5, pot_size * 0.75])
        
        return {
            'street': street,
            'position': position,
            'hole_cards': hole_cards,
            'board_cards': board_cards,
            'action_history': ['bet'] if to_call > 0 else [],
            'pot_size': pot_size + to_call,
            'to_call': to_call,
            'stack_size': 85,
            'is_ip': random.choice([True, False]),
            'was_pfa': random.choice([True, False]),
            'scenario_type': 'speed_training'
        }
    
    def present_scenario(self, scenario: Dict) -> Tuple[str, float]:
        """Present scenario with a conceptual timer."""
        print(f"\n⏱️  DECISION #{self.stats['total'] + 1} - {self.time_limit}s limit")
        print(f"Street: {scenario['street'].upper()}")
        print(f"Position: {scenario['position']}")
        print(f"Hand: {scenario['hole_cards']}")
        if scenario['board_cards']:
            print(f"Board: {scenario['board_cards']}")
        print(f"Pot: {scenario['pot_size']:.1f} BB | To Call: {scenario['to_call']:.1f} BB")

        # NOTE: A true terminal timer is not possible with the standard `input()`
        # function because it blocks program execution. This code demonstrates the
        # intended logic. A library like `prompt_toolkit` or `threading` would
        # be required for a real-world, non-blocking implementation.
        
        start_time = time.time()
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        # We prompt the user for input and then check the time elapsed.
        user_input = input(f"\nAction (f/c/k/b/r): ").lower().strip()
        elapsed = time.time() - start_time

        if elapsed > self.time_limit:
            print(f"\n⏰ TIME'S UP! ({elapsed:.1f}s) Auto-folding...")
            self.time_penalties += 1
            self.stats['time_penalties'] += 1
            return ('fold', elapsed)

        action = action_map.get(user_input)
        if not action:
            print("Invalid action. Defaulting to fold.")
            return ('fold', elapsed)

        if action in ['bet', 'raise']:
            try:
                size = float(input("Enter size in BB: "))
                # Re-check time after the second input
                elapsed = time.time() - start_time
                if elapsed > self.time_limit:
                     print(f"\n⏰ TIME'S UP! ({elapsed:.1f}s) Auto-folding...")
                     self.time_penalties += 1
                     self.stats['time_penalties'] += 1
                     return ('fold', elapsed)
                return (action, elapsed)
            except ValueError:
                print("Invalid size. Defaulting to fold.")
                return ('fold', elapsed)

        return (action, elapsed)
    
    def evaluate_decision(self, scenario: Dict, action: str, elapsed: float) -> bool:
        """Evaluate if the decision was correct."""
        # Simplified evaluation logic for training
        hand_strength = self._calculate_hand_strength(scenario)
        
        # Determine correct action based on hand strength
        if hand_strength > 70:
            correct_action = 'raise' if scenario['to_call'] == 0 else 'call'
        elif hand_strength > 50:
            correct_action = 'call' if scenario['to_call'] <= scenario['pot_size'] * 0.3 else 'fold'
        else:
            correct_action = 'fold'
        
        is_correct = action == correct_action
        
        # Update stats
        self.stats['total'] += 1
        if is_correct:
            self.stats['correct'] += 1
        
        # Update average time
        total_time = self.stats['average_time'] * (self.stats['total'] - 1) + elapsed
        self.stats['average_time'] = total_time / self.stats['total']
        
        return is_correct
    
    def _calculate_hand_strength(self, scenario: Dict) -> float:
        """Calculate hand strength for evaluation."""
        # Simplified hand strength calculation
        if scenario['street'] == 'preflop':
            # Use preflop hand strength
            hole_cards = self._convert_hand_notation(scenario['hole_cards'])
            return hand_evaluator.get_preflop_hand_strength(hole_cards)
        else:
            # Simplified postflop strength
            return random.uniform(30, 80)
    
    def _convert_hand_notation(self, hand_notation: str) -> List[str]:
        """Convert hand notation to card list."""
        # Simplified conversion for common hands
        conversions = {
            'AA': ['Ah', 'Ad'],
            'KK': ['Kh', 'Kd'],
            'QQ': ['Qh', 'Qd'],
            'AKs': ['Ah', 'Kh'],
            'AKo': ['Ah', 'Kd'],
            'JJ': ['Jh', 'Jd'],
            'TT': ['Th', 'Td']
        }
        return conversions.get(hand_notation, ['Ah', 'Kd'])
    
    def print_feedback(self, scenario: Dict, action: str, elapsed: float, is_correct: bool):
        """Print feedback for the decision."""
        print(f"\n📊 FEEDBACK:")
        print(f"Your action: {action.upper()}")
        print(f"Time taken: {elapsed:.1f}s")
        print(f"Result: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
        
        if elapsed > self.time_limit:
            print(f"⚠️  Time penalty applied!")
    
    def print_summary(self):
        """Print training session summary."""
        print(f"\n📊 SPEED TRAINING SUMMARY")
        print("=" * 40)
        print(f"Total decisions: {self.stats['total']}")
        print(f"Correct decisions: {self.stats['correct']}")
        if self.stats['total'] > 0:
            accuracy = (self.stats['correct'] / self.stats['total']) * 100
            print(f"Accuracy: {accuracy:.1f}%")
        print(f"Average time: {self.stats['average_time']:.1f}s")
        print(f"Time penalties: {self.stats['time_penalties']}")
    
    def run_training_session(self):
        """Run a complete speed training session."""
        self.setup_mode()
        
        while self.should_continue():
            scenario = self.generate_scenario()
            action, elapsed = self.present_scenario(scenario)
            is_correct = self.evaluate_decision(scenario, action, elapsed)
            self.print_feedback(scenario, action, elapsed, is_correct)
            
            # Brief pause between decisions
            time.sleep(1)
        
        self.print_summary()


def main():
    """Main function to run speed training."""
    trainer = SpeedTraining(time_limit=10, target_count=10)
    
    try:
        trainer.run_training_session()
    except KeyboardInterrupt:
        print("\n👋 Speed training interrupted by user")
    except Exception as e:
        print(f"❌ Error during speed training: {e}")


if __name__ == "__main__":
    main() 