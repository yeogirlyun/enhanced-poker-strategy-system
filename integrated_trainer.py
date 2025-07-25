# filename: integrated_trainer.py
"""
Integrated Advanced Hold'em Trainer (Refactored)

REVISION HISTORY:
================
Version 9.1 (2025-07-26) - Refactoring Fix
- FIXED: ImportError for 'AdvancedHandEvaluator' by importing the correct
  'EnhancedHandEvaluator' and 'PositionAdjustedEvaluator' classes.
- FIXED: Logic to correctly instantiate and use the proper evaluation classes,
  restoring the bridge between the orchestrator and the evaluation module that
  was lost during the initial refactoring.
- RE-IMPLEMENTED: Helper methods `_get_preflop_hs` and `_get_postflop_evaluation`
  within the GameOrchestrator to handle hand strength lookups and evaluation calls,
  making the main game loop cleaner.
- ENSURED: The program is now fully executable after the OOP refactoring.

Version 9.0 (2025-07-26) - Full OOP Refactoring
- Replaced the monolithic `AdvancedGame` class with a `GameOrchestrator`.
- The orchestrator now uses dedicated modules for core responsibilities.
"""

import json
import sys
import time
import random
from collections import defaultdict

# --- Refactored Core Imports ---
from table import Table
from decision_engine import DecisionEngine

# --- Supporting Module Imports ---
# FIXED: Correctly import the existing classes from the evaluation module.
from enhanced_hand_evaluation import EnhancedHandEvaluator, PositionAdjustedEvaluator
try:
    from session_logger import SessionLogger, SessionAnalyzer
    from training_modes import TrainingModeManager
    SESSION_LOGGING_ENABLED = True
except ImportError:
    SESSION_LOGGING_ENABLED = False

# --- UI and Utility Imports ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

RANKS = '23456789TJQKA'
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}
SUITS = 'cdhs'

def get_shuffled_deck():
    """Returns a shuffled 52-card deck."""
    deck = [r + s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

class GameOrchestrator:
    """
    Orchestrates the poker game, coordinating all the different modules.
    Manages the game loop, hand progression, and user interaction menu.
    """
    def __init__(self, num_players=6):
        print(f"{Colors.BOLD}Initializing trainer for {num_players} players...{Colors.END}")
        self.strategy = self._load_strategy()
        
        # FIXED: Instantiate the correct components from the imported modules.
        self.table = Table(num_players)
        self.decision_engine = DecisionEngine()
        self.base_evaluator = EnhancedHandEvaluator()
        self.position_evaluator = PositionAdjustedEvaluator(self.base_evaluator)

        # Instantiate optional components
        self.session_logger = SessionLogger() if SESSION_LOGGING_ENABLED else None
        self.session_analyzer = SessionAnalyzer() if SESSION_LOGGING_ENABLED else None
        self.training_manager = TrainingModeManager(self.strategy, self.session_logger) if SESSION_LOGGING_ENABLED else None

        # Session state
        self.session_id = None
        self.hand_count = 0
        self.session_stats = defaultdict(lambda: {'correct': 0, 'total': 0})

    def _load_strategy(self):
        """Loads the strategy configuration from a JSON file."""
        try:
            with open('strategy.json', 'r') as f:
                print(f"{Colors.GREEN}✅ Strategy file loaded successfully.{Colors.END}")
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}❌ FATAL: 'strategy.json' not found. Please run strategy_manager.py to create one.{Colors.END}")
            sys.exit(1)

    def _get_preflop_hs(self, hole):
        """Looks up preflop hand strength from the strategy file."""
        if not hole or len(hole) != 2:
            return 0
        r_vals = sorted([RANK_VALUES[c[0]] for c in hole], reverse=True)
        r1, r2 = RANKS[r_vals[0]-2], RANKS[r_vals[1]-2]
        suited = hole[0][1] == hole[1][1]
        key = r1 + r2 if r1 == r2 else (r1 + r2 + 's' if suited else r1 + r2 + 'o')
        return self.strategy['hand_strength_tables']['preflop'].get(key, 0)

    def _get_postflop_evaluation(self, hole, board, position, history):
        """Gets a full postflop evaluation using the position-adjusted evaluator."""
        evaluation = self.position_evaluator.evaluate_hand_in_context(
            hole, board, position, history
        )
        # Convert HandRank enum to a string for easier use
        rank_enum = evaluation.get('hand_rank')
        conversion = {
            1: 'high_card', 2: 'pair', 3: 'two_pair', 4: 'three_of_a_kind',
            5: 'straight', 6: 'flush', 7: 'full_house', 8: 'four_of_a_kind',
            9: 'straight_flush', 10: 'straight_flush' # Royal Flush
        }
        rank_str = conversion.get(int(rank_enum), 'high_card')

        return {
            'hs': evaluation.get('hand_strength', 0),
            'rank': rank_str,
            'is_draw': len(evaluation.get('draws', [])) > 0,
            'outs': evaluation.get('outs', 0),
            'board_texture': evaluation.get('board_texture').name.lower() if evaluation.get('board_texture') else 'unknown',
            'equity_estimate': evaluation.get('equity_estimate', 50),
        }

    def play_hand(self):
        """
        Plays a single hand of poker, from dealing to showdown.
        """
        self.hand_count += 1
        print(f"\n{Colors.BOLD}{'='*20} Hand #{self.hand_count} {'='*20}{Colors.END}")

        # 1. Setup the hand
        self.table.move_dealer_button()
        deck = get_shuffled_deck()
        for player in self.table.players:
            player.reset_for_hand()
            player.hole = [deck.pop(), deck.pop()]

        # Hand state variables
        hand_state = {
            'pot': 0.0,
            'board': [],
            'to_call': 0.0,
            'history': []
        }

        # 2. Post Blinds
        self._post_blinds(hand_state)

        # 3. Run Betting Rounds
        for street in ['preflop', 'flop', 'turn', 'river']:
            if len(self.table.get_active_players()) <= 1:
                break
            
            print(f"\n{Colors.BOLD}--- {street.upper()} ---{Colors.END}")
            if street == 'flop':
                hand_state['board'].extend([deck.pop() for _ in range(3)])
            elif street in ['turn', 'river']:
                hand_state['board'].append(deck.pop())
            
            if hand_state['board']:
                print(f"Board: {Colors.YELLOW}{' '.join(hand_state['board'])}{Colors.END}")
            
            self._run_betting_round(street, hand_state)

        # 4. Handle Showdown
        self._showdown(hand_state)

    def _post_blinds(self, hand_state):
        """Posts the small and big blinds."""
        sb_player = self.table.get_player_at_position('SB')
        bb_player = self.table.get_player_at_position('BB')

        sb_amount = min(0.5, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.contributed_this_street = sb_amount
        hand_state['pot'] += sb_amount

        bb_amount = min(1.0, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.contributed_this_street = bb_amount
        hand_state['pot'] += bb_amount
        hand_state['to_call'] = bb_amount

        print(f"Blinds: {sb_player.current_position} posts {sb_amount}, {bb_player.current_position} posts {bb_amount}")

    def _run_betting_round(self, street, hand_state):
        """Manages a single round of betting."""
        if street != 'preflop':
            for p in self.table.players:
                p.contributed_this_street = 0
            hand_state['to_call'] = 0.0
        
        players_to_act = self.table.get_action_order(street)
        last_aggressor = None
        
        while players_to_act:
            player = players_to_act.pop(0)
            
            if not player.is_active or player.stack == 0:
                continue
            
            if player == last_aggressor:
                break

            if len(self.table.get_active_players()) <= 1:
                break

            amount_to_call = max(0, hand_state['to_call'] - player.contributed_this_street)

            player_game_state = self._build_player_game_state(player, street, hand_state, amount_to_call)
            
            action, size = player.get_action(player_game_state, self.strategy, self.decision_engine)

            if player == self.table.user_player:
                self._handle_user_decision(player, player_game_state, action, size)

            new_aggressor = self._execute_action(player, action, size, hand_state, amount_to_call)
            
            if new_aggressor:
                last_aggressor = new_aggressor
                players_to_act = self.table.get_action_order(street)
                # Fast-forward to the player after the aggressor
                while players_to_act and players_to_act[0].seat_number != new_aggressor.seat_number:
                    players_to_act.pop(0)
                if players_to_act:
                    players_to_act.pop(0)

    def _build_player_game_state(self, player, street, hand_state, amount_to_call):
        """Constructs the state dictionary for a player's decision."""
        preflop_hs = self._get_preflop_hs(player.hole)
        postflop_eval = {}
        if street != 'preflop':
            postflop_eval = self._get_postflop_evaluation(
                player.hole, hand_state['board'], player.current_position, hand_state['history']
            )

        return {
            'preflop_hs': preflop_hs,
            'dynamic_hs': postflop_eval.get('hs', preflop_hs),
            'postflop_details': postflop_eval,
            'position': player.current_position,
            'is_ip': False,
            'street': street,
            'history': hand_state['history'],
            'pot': hand_state['pot'],
            'to_call': amount_to_call,
            'hole': player.hole,
            'board': hand_state['board'],
            'was_aggressor': player.was_aggressor,
        }

    def _execute_action(self, player, action, size, hand_state, amount_to_call):
        """Applies a player's action to the game state."""
        pos_str = f"{player.current_position} (Seat #{player.seat_number})"
        new_aggressor = None

        if action == 'fold':
            player.is_active = False
            print(f"   {Colors.RED}{pos_str} folds{Colors.END}")
        elif action == 'check':
            print(f"   {Colors.BLUE}{pos_str} checks{Colors.END}")
        elif action == 'call':
            amount = min(amount_to_call, player.stack)
            player.stack -= amount
            player.contributed_this_street += amount
            hand_state['pot'] += amount
            print(f"   {Colors.YELLOW}{pos_str} calls {amount:.1f} BB{Colors.END}")
        elif action in ['bet', 'raise']:
            amount = min(size, player.stack)
            player.stack -= amount
            player.contributed_this_street += amount
            hand_state['pot'] += amount
            hand_state['to_call'] = player.contributed_this_street
            player.was_aggressor = True
            new_aggressor = player
            action_word = 'bets' if action == 'bet' else 'raises to'
            print(f"   {Colors.GREEN}{pos_str} {action_word} {amount:.1f} BB{Colors.END}")
        
        hand_state['history'].append(action)
        return new_aggressor

    def _handle_user_decision(self, player, game_state, action, size):
        """Provides feedback on the user's decision and logs it."""
        opt_action, opt_size = self.decision_engine.get_optimal_action(game_state, self.strategy)
        is_correct = (action == opt_action)

        if is_correct:
            print(f"{Colors.GREEN}✅ Correct!{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Incorrect! Optimal was {opt_action.upper()} {opt_size if opt_size > 0 else ''}{Colors.END}")

        if self.session_logger and self.session_id:
            pass

    def _showdown(self, hand_state):
        """Handles the showdown and awards the pot."""
        print(f"\n{Colors.BOLD}--- SHOWDOWN ---{Colors.END}")
        active_players = self.table.get_active_players()
        
        if not active_players:
            # This can happen if the last two players fold simultaneously in a weird edge case.
            # The pot should be awarded to the last player to not fold.
            print("No active players at showdown.")
            return

        if len(active_players) == 1:
            winner = active_players[0]
            print(f"{winner.name} wins uncontested pot of {Colors.GREEN}{hand_state['pot']:.1f} BB{Colors.END}")
        else:
            winner = max(active_players, key=lambda p: self._get_postflop_evaluation(p.hole, hand_state['board'], p.current_position, [])['hs'])
            print(f"{winner.name} shows {' '.join(winner.hole)} and wins {Colors.GREEN}{hand_state['pot']:.1f} BB{Colors.END}")
            for p in active_players:
                if p != winner:
                    print(f"  {p.name} shows {' '.join(p.hole)}")
        
        winner.stack += hand_state['pot']

    def run(self):
        """Main application loop."""
        while True:
            self.play_hand()
            if input("\nPlay another hand? (y/n): ").lower() != 'y':
                break
        print(f"{Colors.CYAN}Thanks for training!{Colors.END}")


def main():
    """Main entry point for the application."""
    num_players = 6
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        num_players = int(sys.argv[1])
    
    try:
        orchestrator = GameOrchestrator(num_players=num_players)
        orchestrator.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Training interrupted. Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}\nAn unexpected error occurred: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
