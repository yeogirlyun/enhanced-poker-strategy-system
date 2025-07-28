# filename: training_modes.py
"""
Advanced Training Modes for Hold'em Trainer

REVISION HISTORY:
================

Version 1.0 (2025-01-25) - Initial Implementation
- Created base TrainingModeBase class for mode architecture
- Implemented DrillMode for scenario-specific practice:
  * 3-bet situations (preflop re-raising scenarios)
  * Continuation betting (post-flop aggressor decisions)
  * Facing bets (responding to opponent aggression)
  * River decision making (final street optimization)
  * Draw situations (playing with outs and potential)
- Added SpeedTraining for time-pressured decisions
- Implemented BlindTraining with information hiding:
  * Partial information (some data hidden)
  * Full blind (most information hidden)
  * Position-only (ultimate intuition test)
- Created MistakeReview mode for targeted improvement
- Added TrainingModeManager for unified interface
- Integrated with session logging for performance tracking

Features:
- Multiple specialized training modes
- Configurable difficulty and focus areas
- Time-pressure training capabilities
- Progressive information hiding for advanced practice
- Mistake review system for targeted improvement
- Comprehensive scenario generation
- Integration with analytics system
"""

import random
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

class TrainingModeBase:
    """Base class for all training modes."""
    
    def __init__(self, strategy, session_logger=None):
        self.strategy = strategy
        self.session_logger = session_logger
        self.stats = {'correct': 0, 'total': 0, 'start_time': time.time()}
    
    def setup_mode(self):
        """Override in subclasses for mode-specific setup."""
        pass
    
    def should_continue(self):
        """Override in subclasses for mode-specific continuation logic."""
        return True
    
    def generate_scenario(self):
        """Override in subclasses to generate training scenarios."""
        raise NotImplementedError
    
    def present_scenario(self, scenario):
        """Present the scenario to the user and get their response."""
        raise NotImplementedError
    
    def check_answer(self, user_action, optimal_action, scenario):
        """Check if the user's answer is correct."""
        is_correct = user_action[0] == optimal_action[0]
        self.stats['total'] += 1
        if is_correct:
            self.stats['correct'] += 1
        return is_correct
    
    def print_progress(self):
        """Print current progress."""
        if self.stats['total'] > 0:
            accuracy = (self.stats['correct'] / self.stats['total']) * 100
            elapsed = time.time() - self.stats['start_time']
            print(f"\nProgress: {self.stats['correct']}/{self.stats['total']} ({accuracy:.1f}%) - {elapsed:.1f}s elapsed")

class DrillMode(TrainingModeBase):
    """Focus on specific scenarios."""
    
    DRILL_TYPES = {
        '3bet': 'Preflop 3-betting situations',
        'cbet': 'Continuation betting scenarios',  
        'facing_bet': 'Facing bets on all streets',
        'river': 'River decision making',
        'draws': 'Playing with draws',
        'position': 'Specific position play',
        'stack_sizes': 'Short/deep stack situations'
    }
    
    def __init__(self, strategy, drill_type, session_logger=None):
        super().__init__(strategy, session_logger)
        self.drill_type = drill_type
        self.target_count = 20  # Default number of scenarios
        
    def setup_mode(self):
        print(f"\n🎯 DRILL MODE: {self.DRILL_TYPES.get(self.drill_type, self.drill_type)}")
        print(f"Target: {self.target_count} scenarios")
        print("Focus on getting these specific situations right!")
    
    def should_continue(self):
        return self.stats['total'] < self.target_count
    
    def generate_scenario(self):
        """Generate a scenario based on the drill type."""
        if self.drill_type == '3bet':
            return self._generate_3bet_scenario()
        elif self.drill_type == 'cbet':
            return self._generate_cbet_scenario()
        elif self.drill_type == 'facing_bet':
            return self._generate_facing_bet_scenario()
        elif self.drill_type == 'river':
            return self._generate_river_scenario()
        elif self.drill_type == 'draws':
            return self._generate_draw_scenario()
        else:
            return self._generate_generic_scenario()
    
    def _generate_3bet_scenario(self):
        """Generate preflop 3-betting scenarios."""
        positions = ['UTG', 'MP', 'CO', 'BTN']
        position = random.choice(positions)
        
        # Generate a hand that's in the potential 3-bet range
        hands_3bet_range = ['AA', 'KK', 'QQ', 'AKs', 'AKo', 'JJ', 'TT', 'AQs', 'AJs', 'KQs']
        hands_call_range = ['99', '88', '77', 'AQo', 'AJo', 'KJs', 'QJs', 'JTs']
        hands_fold_range = ['A9s', 'KTs', 'QTs', '66', '55', 'K9s']
        
        all_hands = hands_3bet_range + hands_call_range + hands_fold_range
        hole_cards = random.choice(all_hands)
        
        return {
            'street': 'preflop',
            'position': position,
            'hole_cards': hole_cards,
            'board_cards': '',
            'action_history': ['raise'],  # Facing a raise
            'pot_size': 7.5,  # 2.5x open
            'to_call': 2.5,
            'stack_size': 97.5,
            'is_ip': random.choice([True, False]),
            'scenario_type': '3bet_decision'
        }
    
    def _generate_cbet_scenario(self):
        """Generate continuation betting scenarios."""
        positions = ['UTG', 'MP', 'CO', 'BTN']
        position = random.choice(positions)
        
        # Generate flop scenarios
        boards = [
            ['As', 'Kh', '7c'],  # Dry ace-high
            ['Ts', '9h', '4c'],  # Medium dry
            ['8s', '7h', '6c'],  # Coordinated
            ['Qs', 'Js', '4s'],  # Two-tone with draws
            ['2h', '2c', '9s']   # Paired board
        ]
        
        board = random.choice(boards)
        
        # Generate hand that opened preflop
        opening_hands = ['AKs', 'AQs', 'KQs', 'JJ', 'TT', '99', 'AJs', 'KJs']
        hole_cards = random.choice(opening_hands)
        
        return {
            'street': 'flop',
            'position': position,
            'hole_cards': hole_cards,
            'board_cards': ' '.join(board),
            'action_history': [],  # First to act postflop
            'pot_size': 7.5,  # After preflop raise and call
            'to_call': 0,
            'stack_size': 96,
            'is_ip': random.choice([True, False]),
            'was_pfa': True,
            'scenario_type': 'cbet_decision'
        }
    
    def _generate_facing_bet_scenario(self):
        """Generate scenarios facing bets."""
        streets = ['flop', 'turn', 'river']
        street = random.choice(streets)
        position = random.choice(['UTG', 'MP', 'CO', 'BTN'])
        
        # Generate appropriate board for street
        if street == 'flop':
            board = ['As', 'Kh', '7c']
        elif street == 'turn':
            board = ['As', 'Kh', '7c', '4s']
        else:  # river
            board = ['As', 'Kh', '7c', '4s', '9d']
        
        bet_sizes = [0.3, 0.5, 0.75, 1.0, 1.5]  # Fraction of pot
        bet_size = random.choice(bet_sizes)
        pot_size = 15.0
        to_call = pot_size * bet_size
        
        hole_cards = random.choice(['AQs', 'KJs', 'JTs', '99', '88', 'A7s'])
        
        return {
            'street': street,
            'position': position,
            'hole_cards': hole_cards,
            'board_cards': ' '.join(board),
            'action_history': ['bet'],
            'pot_size': pot_size + to_call,
            'to_call': to_call,
            'stack_size': 85,
            'is_ip': random.choice([True, False]),
            'was_pfa': False,
            'scenario_type': 'facing_bet'
        }
    
    def _generate_river_scenario(self):
        """Generate river-specific scenarios."""
        position = random.choice(['UTG', 'MP', 'CO', 'BTN'])
        
        # River boards with different textures
        river_boards = [
            ['As', 'Kh', '7c', '4s', '2d'],  # Dry runout
            ['9s', '8h', '7c', '6s', '5d'],  # Straight possible
            ['Ks', 'Kh', '7c', '4s', '2d'],  # Paired board
            ['As', '9s', '7s', '4s', '2d'],  # Flush possible
        ]
        
        board = random.choice(river_boards)
        
        # Hands that might get to river
        river_hands = ['AK', 'AQ', 'KQ', 'QJ', 'JT', 'AA', 'KK', 'QQ', 'AJ', 'AT']
        hole_cards = random.choice(river_hands)
        
        # River action - either first to act or facing bet
        if random.choice([True, False]):
            action_history = []
            pot_size = 45
            to_call = 0
        else:
            action_history = ['bet']
            pot_size = 60
            to_call = 15
        
        return {
            'street': 'river',
            'position': position,
            'hole_cards': hole_cards,
            'board_cards': ' '.join(board),
            'action_history': action_history,
            'pot_size': pot_size,
            'to_call': to_call,
            'stack_size': 70,
            'is_ip': random.choice([True, False]),
            'was_pfa': random.choice([True, False]),
            'scenario_type': 'river_decision'
        }
    
    def _generate_draw_scenario(self):
        """Generate scenarios with draws."""
        # Flop/turn scenarios with draws
        street = random.choice(['flop', 'turn'])
        
        if street == 'flop':
            # Draw-heavy boards
            boards = [
                ['9s', '8h', '7c'],  # Straight draws
                ['Ks', '9s', '4c'],  # Flush draw
                ['Ts', '9s', '8c'],  # Combo draws possible
            ]
            draw_hands = ['JTs', 'QJs', 'T9s', '87s', '76s', 'As5s', 'KsQc']
        else:  # turn
            boards = [
                ['9s', '8h', '7c', '2d'],
                ['Ks', '9s', '4c', '3h'],
                ['Ts', '9s', '8c', '2h'],
            ]
            draw_hands = ['JTs', 'QJs', 'T9s', '87s', '76s', 'As5s']
        
        board = random.choice(boards)
        hole_cards = random.choice(draw_hands)
        
        return {
            'street': street,
            'position': random.choice(['CO', 'BTN']),
            'hole_cards': hole_cards,
            'board_cards': ' '.join(board),
            'action_history': random.choice([[], ['bet']]),
            'pot_size': 20,
            'to_call': random.choice([0, 10, 15]),
            'stack_size': 80,
            'is_ip': random.choice([True, False]),
            'was_pfa': random.choice([True, False]),
            'scenario_type': 'draw_decision'
        }
    
    def _generate_generic_scenario(self):
        """Generate a generic training scenario."""
        street = random.choice(['preflop', 'flop', 'turn', 'river'])
        position = random.choice(['UTG', 'MP', 'CO', 'BTN'])
        
        return {
            'street': street,
            'position': position,
            'hole_cards': 'AKs',  # Default hand
            'board_cards': 'As Kh 7c' if street != 'preflop' else '',
            'action_history': [],
            'pot_size': 10,
            'to_call': 0,
            'stack_size': 90,
            'is_ip': True,
            'was_pfa': False,
            'scenario_type': 'generic'
        }

class SpeedTraining(TrainingModeBase):
    """Time-limited decision training."""
    
    def __init__(self, strategy, time_limit=10, session_logger=None):
        super().__init__(strategy, session_logger)
        self.time_limit = time_limit  # seconds per decision
        self.target_count = 25
        self.time_penalties = 0
    
    def setup_mode(self):
        print(f"\n⚡ SPEED TRAINING MODE")
        print(f"Time limit: {self.time_limit} seconds per decision")
        print(f"Target: {self.target_count} decisions")
        print("Make quick, accurate decisions!")
    
    def should_continue(self):
        return self.stats['total'] < self.target_count
    
    def generate_scenario(self):
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
    
    def present_scenario(self, scenario):
        """Present scenario with timer."""
        print(f"\n⏱️  DECISION #{self.stats['total'] + 1} - {self.time_limit}s limit")
        print(f"Street: {scenario['street'].upper()}")
        print(f"Position: {scenario['position']}")
        print(f"Hand: {scenario['hole_cards']}")
        if scenario['board_cards']:
            print(f"Board: {scenario['board_cards']}")
        print(f"Pot: {scenario['pot_size']:.1f} BB | To Call: {scenario['to_call']:.1f} BB")
        
        # Start timer
        start_time = time.time()
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        while True:
            elapsed = time.time() - start_time
            remaining = max(0, self.time_limit - elapsed)
            
            if remaining == 0:
                print(f"\n⏰ TIME'S UP! Auto-folding...")
                self.time_penalties += 1
                return ('fold', 0), elapsed
            
            try:
                print(f"\rTime remaining: {remaining:.1f}s | Action (f/c/k/b/r): ", end='', flush=True)
                # This is a simplified input - in a real implementation you'd want non-blocking input
                user_input = input().lower().strip()
                elapsed = time.time() - start_time
                
                action = action_map.get(user_input)
                if not action:
                    if elapsed >= self.time_limit:
                        print(f"\n⏰ TIME'S UP! Auto-folding...")
                        self.time_penalties += 1
                        return ('fold', 0), elapsed
                    continue
                
                if action in ['bet', 'raise']:
                    if elapsed >= self.time_limit:
                        print(f"\n⏰ TIME'S UP! Auto-folding...")
                        self.time_penalties += 1
                        return ('fold', 0), elapsed
                    try:
                        size = float(input("Size in BB: "))
                        return (action, size), elapsed
                    except ValueError:
                        continue
                
                return (action, 0), elapsed
                
            except KeyboardInterrupt:
                return ('fold', 0), elapsed
    
    def check_answer(self, user_action, optimal_action, scenario):
        """Check answer and account for time penalty."""
        is_correct = super().check_answer(user_action, optimal_action, scenario)
        
        # Show time-specific feedback
        if hasattr(self, '_last_decision_time'):
            decision_time = self._last_decision_time
            if decision_time >= self.time_limit:
                print(f"⏰ Time penalty! ({decision_time:.1f}s)")
            elif decision_time < 3:
                print(f"⚡ Quick decision! ({decision_time:.1f}s)")
        
        return is_correct
    
    def print_final_stats(self):
        """Print speed training specific stats."""
        self.print_progress()
        avg_time = (time.time() - self.stats['start_time']) / max(self.stats['total'], 1)
        print(f"Average decision time: {avg_time:.1f}s")
        print(f"Time penalties: {self.time_penalties}")

class BlindTraining(TrainingModeBase):
    """Training with hidden information."""
    
    def __init__(self, strategy, blind_type='partial', session_logger=None):
        super().__init__(strategy, session_logger)
        self.blind_type = blind_type  # 'partial', 'full', 'position_only'
        self.target_count = 15
    
    def setup_mode(self):
        print(f"\n🙈 BLIND TRAINING MODE: {self.blind_type}")
        print(f"Target: {self.target_count} decisions")
        print("Make decisions with limited information!")
        
        if self.blind_type == 'partial':
            print("Some information will be hidden")
        elif self.blind_type == 'full':
            print("Most information hidden - rely on position and action")
        elif self.blind_type == 'position_only':
            print("Only position visible - ultimate test!")
    
    def should_continue(self):
        return self.stats['total'] < self.target_count
    
    def generate_scenario(self):
        """Generate scenarios for blind training."""
        return {
            'street': random.choice(['preflop', 'flop', 'turn', 'river']),
            'position': random.choice(['UTG', 'MP', 'CO', 'BTN']),
            'hole_cards': random.choice(['AA', 'KK', 'AKs', 'QQ', 'JJ', 'AQs', 'TT', '99']),
            'board_cards': 'As Kh 7c 2d' if random.choice([True, False]) else '',
            'action_history': random.choice([[], ['bet'], ['raise']]),
            'pot_size': random.uniform(10, 40),
            'to_call': random.uniform(0, 20),
            'stack_size': 85,
            'is_ip': random.choice([True, False]),
            'was_pfa': random.choice([True, False]),
            'scenario_type': 'blind_training'
        }
    
    def present_scenario(self, scenario):
        """Present scenario with information hidden based on blind type."""
        print(f"\n🙈 BLIND DECISION #{self.stats['total'] + 1}")
        
        # Always show position and street
        print(f"Street: {scenario['street'].upper()}")
        print(f"Position: {scenario['position']}")
        
        if self.blind_type == 'position_only':
            print("Hand: [HIDDEN]")
            print("Board: [HIDDEN]")
            print("Pot/Stack info: [HIDDEN]")
            print("Action: ???")
        elif self.blind_type == 'full':
            print("Hand: [HIDDEN]")
            if scenario['board_cards']:
                print("Board: [HIDDEN]")
            print(f"Pot: ~{scenario['pot_size']:.0f} BB (approx)")
            if scenario['to_call'] > 0:
                print("Facing action: YES")
            else:
                print("First to act: YES")
        else:  # partial
            print(f"Hand: {scenario['hole_cards']}")
            if scenario['board_cards']:
                print("Board: [PARTIALLY HIDDEN]")
            print(f"Pot: {scenario['pot_size']:.1f} BB")
            print(f"To Call: {scenario['to_call']:.1f} BB")
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        while True:
            user_input = input("Your action (f/c/k/b/r): ").lower().strip()
            action = action_map.get(user_input)
            if not action:
                continue
            
            if action in ['bet', 'raise']:
                try:
                    size = float(input("Size in BB: "))
                    return (action, size)
                except ValueError:
                    continue
            
            return (action, 0)

class MistakeReview(TrainingModeBase):
    """Review and practice previous mistakes."""
    
    def __init__(self, strategy, session_logger=None, days_back=30):
        super().__init__(strategy, session_logger)
        self.days_back = days_back
        self.mistakes = []
        self.current_mistake_idx = 0
        
    def setup_mode(self):
        print(f"\n📚 MISTAKE REVIEW MODE")
        if self.session_logger:
            self._load_mistakes()
        
        if not self.mistakes:
            print("No recent mistakes found to review!")
            return False
        
        print(f"Reviewing {len(self.mistakes)} recent mistakes from last {self.days_back} days")
        print("Focus on getting these right this time!")
        return True
    
    def _load_mistakes(self):
        """Load recent mistakes from the database."""
        if not self.session_logger:
            return
        
        conn = sqlite3.connect(self.session_logger.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        
        cursor.execute('''
        SELECT d.street, d.position, d.hole_cards, d.board_cards,
               d.pot_size, d.to_call, d.action_history, d.was_pfa,
               d.user_action, d.optimal_action, m.mistake_type, m.description
        FROM decisions d
        JOIN mistakes m ON d.decision_id = m.decision_id
        WHERE d.timestamp >= ?
        ORDER BY d.timestamp DESC
        LIMIT 20
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        for row in results:
            self.mistakes.append({
                'street': row[0],
                'position': row[1],
                'hole_cards': row[2],
                'board_cards': row[3],
                'pot_size': row[4],
                'to_call': row[5],
                'action_history': json.loads(row[6]) if row[6] else [],
                'was_pfa': bool(row[7]),
                'user_action': row[8],
                'optimal_action': row[9],
                'mistake_type': row[10],
                'description': row[11]
            })
    
    def should_continue(self):
        return self.current_mistake_idx < len(self.mistakes)
    
    def generate_scenario(self):
        """Return the next mistake scenario."""
        if self.current_mistake_idx >= len(self.mistakes):
            return None
        
        mistake = self.mistakes[self.current_mistake_idx]
        self.current_mistake_idx += 1
        
        return {
            'street': mistake['street'],
            'position': mistake['position'],
            'hole_cards': mistake['hole_cards'],
            'board_cards': mistake['board_cards'],
            'action_history': mistake['action_history'],
            'pot_size': mistake['pot_size'],
            'to_call': mistake['to_call'],
            'stack_size': 85,  # Default
            'is_ip': True,  # Default
            'was_pfa': mistake['was_pfa'],
            'scenario_type': 'mistake_review',
            'previous_mistake': mistake['user_action'],
            'mistake_type': mistake['mistake_type']
        }
    
    def present_scenario(self, scenario):
        """Present the mistake scenario."""
        print(f"\n📚 MISTAKE REVIEW #{self.current_mistake_idx}")
        print(f"Previous mistake type: {scenario['mistake_type']}")
        print(f"Street: {scenario['street'].upper()}")
        print(f"Position: {scenario['position']}")
        print(f"Hand: {scenario['hole_cards']}")
        if scenario['board_cards']:
            print(f"Board: {scenario['board_cards']}")
        print(f"Pot: {scenario['pot_size']:.1f} BB | To Call: {scenario['to_call']:.1f} BB")
        print(f"Last time you played: {scenario['previous_mistake'].upper()}")
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        while True:
            user_input = input("What should you do this time? (f/c/k/b/r): ").lower().strip()
            action = action_map.get(user_input)
            if not action:
                continue
            
            if action in ['bet', 'raise']:
                try:
                    size = float(input("Size in BB: "))
                    return (action, size)
                except ValueError:
                    continue
            
            return (action, 0)

class TrainingModeManager:
    """Manages different training modes."""
    
    def __init__(self, strategy, session_logger=None):
        self.strategy = strategy
        self.session_logger = session_logger
        
    def list_modes(self):
        """List available training modes."""
        print("\n🎓 AVAILABLE TRAINING MODES:")
        print("1. drill <type> - Focus on specific scenarios")
        print("   Types: 3bet, cbet, facing_bet, river, draws, position")
        print("2. speed [time_limit] - Time-limited decisions (default: 10s)")
        print("3. blind [type] - Limited information training")
        print("   Types: partial, full, position_only")
        print("4. mistakes [days] - Review recent mistakes (default: 30 days)")
        print("5. random - Random scenarios for general practice")
        
    def start_mode(self, mode_name, *args):
        """Start a specific training mode."""
        if mode_name == 'drill':
            drill_type = args[0] if args else '3bet'
            mode = DrillMode(self.strategy, drill_type, self.session_logger)
        elif mode_name == 'speed':
            time_limit = int(args[0]) if args and args[0].isdigit() else 10
            mode = SpeedTraining(self.strategy, time_limit, self.session_logger)
        elif mode_name == 'blind':
            blind_type = args[0] if args else 'partial'
            mode = BlindTraining(self.strategy, blind_type, self.session_logger)
        elif mode_name == 'mistakes':
            days_back = int(args[0]) if args and args[0].isdigit() else 30
            mode = MistakeReview(self.strategy, self.session_logger, days_back)
            if not mode.setup_mode():
                return
        else:
            print(f"Unknown mode: {mode_name}")
            return
            
        self._run_training_mode(mode)
    
    def _run_training_mode(self, mode):
        """Run a training mode."""
        mode.setup_mode()
        
        while mode.should_continue():
            scenario = mode.generate_scenario()
            if not scenario:
                break
                
            # Get user action
            user_action = mode.present_scenario(scenario)
            
            # Calculate optimal action (simplified - you'd use your actual game logic)
            optimal_action = self._get_optimal_action(scenario)
            
            # Check answer
            is_correct = mode.check_answer(user_action, optimal_action, scenario)
            
            # Provide feedback
            if is_correct:
                print("✅ Correct!")
            else:
                print(f"❌ Incorrect. Optimal: {optimal_action[0].upper()}")
            
            mode.print_progress()
            
            # Ask to continue or get next scenario
            if hasattr(mode, 'print_final_stats'):
                continue
            
            if input("\nContinue? (y/n): ").lower() != 'y':
                break
        
        # Final stats
        if hasattr(mode, 'print_final_stats'):
            mode.print_final_stats()
        else:
            mode.print_progress()
            
        print("\n🎯 Training mode completed!")
    
    def _get_optimal_action(self, scenario):
        """Calculate optimal action for a scenario (simplified)."""
        # This is a simplified version - you'd integrate with your actual strategy logic
        # For now, return a reasonable default based on scenario
        
        if scenario['to_call'] == 0:
            return ('check', 0)
        elif scenario['to_call'] > scenario['pot_size']:
            return ('fold', 0)
        else:
            return ('call', scenario['to_call'])

def main():
    """Command-line interface for training modes."""
    import sys
    
    # Load strategy
    try:
        with open('strategy.json', 'r') as f:
            strategy = json.load(f)
    except FileNotFoundError:
        print("Error: strategy.json not found")
        return
    
    # Initialize session logger
    try:
        from session_logger import SessionLogger
        session_logger = SessionLogger()
    except ImportError:
        session_logger = None
    
    manager = TrainingModeManager(strategy, session_logger)
    
    if len(sys.argv) < 2:
        manager.list_modes()
        return
    
    mode_name = sys.argv[1]
    args = sys.argv[2:]
    
    manager.start_mode(mode_name, *args)

if __name__ == '__main__':
    main()