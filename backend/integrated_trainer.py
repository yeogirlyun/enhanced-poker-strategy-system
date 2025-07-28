# filename: integrated_trainer.py
"""
Integrated Advanced Hold'em Trainer with Enhanced Feedback System

REVISION HISTORY:
================
Version 9.2 (2025-07-27) - Enhanced Feedback System
- ADDED: DetailedFeedbackSystem class for educational explanations
- ENHANCED: User decision feedback with strategy rule explanations
- ADDED: Detailed breakdowns of why decisions are right/wrong
- IMPROVED: Learning experience with threshold displays and tips

Version 9.1 (2025-07-26) - Refactoring Fix
- FIXED: ImportError for 'AdvancedHandEvaluator' by importing the correct
  'EnhancedHandEvaluator' and 'PositionAdjustedEvaluator' classes.
- FIXED: Logic to correctly instantiate and use the proper evaluation classes
- RE-IMPLEMENTED: Helper methods for hand evaluation
- ENSURED: The program is now fully executable after the OOP refactoring

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
    PURPLE = '\033[95m'
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


# In integrated_trainer.py, replace the existing DetailedFeedbackSystem class with this one.

class DetailedFeedbackSystem:
    """
    Provides detailed, example-driven explanations for poker decisions
    based on the loaded strategy rules.
    """

    def __init__(self, strategy):
        self.strategy = strategy
        # ADDED: Store hand strength tables for easy lookup of examples
        self.preflop_hs_table = strategy['hand_strength_tables']['preflop']
        self.postflop_hs_table = strategy['hand_strength_tables']['postflop']
        # ADDED: Create a reverse map for postflop HS for easier explanations
        self.postflop_hs_to_rank = {v: k for k, v in self.postflop_hs_table.items()}


    # ADDED: Helper method to find example hands for a given HS threshold.
    def _get_example_hands_for_hs(self, threshold, stronger=True, count=3):
        """Finds example preflop hands that meet (or fail to meet) an HS threshold."""
        if stronger:
            # Find hands with HS >= threshold
            valid_hands = {hand: hs for hand, hs in self.preflop_hs_table.items() if hs >= threshold}
        else:
            # Find hands with HS < threshold
            valid_hands = {hand: hs for hand, hs in self.preflop_hs_table.items() if hs < threshold}

        if not valid_hands:
            return "N/A"

        # Sort by strength (descending) and get the top examples
        sorted_hands = sorted(valid_hands.items(), key=lambda item: item[1], reverse=True)
        return ", ".join([f"{hand} (HS {hs})" for hand, hs in sorted_hands[:count]])

    # ADDED: Helper method to get a descriptive rank from a postflop HS value.
    def _get_postflop_rank_from_hs(self, threshold):
        """Finds the descriptive hand rank for a postflop HS threshold."""
        # Find the closest matching rank for a given threshold
        closest_rank = min(self.postflop_hs_table.keys(), key=lambda rank: abs(self.postflop_hs_table[rank] - threshold))
        return closest_rank.replace('_', ' ').title()

    def explain_decision(self, game_state, user_action, optimal_action):
        """Generate detailed explanation for why a decision was right or wrong."""
        explanation = []
        street = game_state['street']
        position = game_state['position']
        # Use dynamic_hs for postflop, preflop_hs for preflop
        hs = game_state.get('dynamic_hs', 0) if street != 'preflop' else game_state.get('preflop_hs', 0)

        # Build the core explanation
        explanation.append(f"\n{Colors.BOLD}📚 STRATEGY EXPLANATION:{Colors.END}")
        explanation.append(f"Street: {Colors.CYAN}{street.upper()}{Colors.END} | Position: {Colors.CYAN}{position}{Colors.END} | Your Hand Strength: {Colors.CYAN}{hs}{Colors.END}")
        
        # Explain the user's error first
        if user_action[0] != optimal_action[0]:
             explanation.append(f"{Colors.RED}Your move was {user_action[0].upper()}, but the optimal move was {optimal_action[0].upper()}. Here's why:{Colors.END}")
        
        # Get the relevant strategy rules
        if street == 'preflop':
            rules = self._get_preflop_rules(game_state, position)
            explanation.extend(self._explain_preflop_decision(
                game_state, optimal_action, rules, hs
            ))
        else:
            rules = self._get_postflop_rules(game_state, position, street)
            explanation.extend(self._explain_postflop_decision(
                game_state, optimal_action, rules, hs
            ))

        # Add general tips
        explanation.extend(self._get_general_tips(game_state, optimal_action))

        return '\n'.join(explanation)

    # This private method remains the same
    def _get_preflop_rules(self, game_state, position):
        """Extract relevant preflop rules based on game state."""
        history = game_state.get('history', [])

        if not history:  # Opening action
            return self.strategy['preflop']['open_rules'].get(position, {})
        elif 'raise' in history:  # Facing a raise
            pos_type = 'IP' if game_state.get('is_ip') else 'OOP'
            return self.strategy['preflop']['vs_raise'].get(position, {}).get(pos_type, {})
        
        return {}
    
    # This private method remains the same
    def _get_postflop_rules(self, game_state, position, street):
        """Extract relevant postflop rules based on game state."""
        pos_type = 'IP' if game_state.get('is_ip') else 'OOP'
        
        if game_state.get('was_aggressor'):  # PFA
            return self.strategy['postflop']['pfa'][street].get(position, {}).get(pos_type, {})
        else:  # Caller facing bet
            if 'bet' in game_state.get('history', []):
                return self.strategy['postflop']['caller'][street].get(position, {}).get(pos_type, {})
        
        return {}

    # MODIFIED: This method is heavily enhanced with examples.
    def _explain_preflop_decision(self, game_state, optimal_action, rules, hs):
        """Detailed explanation for preflop decisions with concrete examples."""
        explanation = []
        history = game_state.get('history', [])

        if not history:  # Opening action
            threshold = rules.get('threshold', 20)
            explanation.append(f"\n{Colors.YELLOW}Rule:{Colors.END} From {game_state['position']}, you should open-raise with hands of {Colors.BOLD}HS ≥ {threshold}{Colors.END}.")
            
            if hs >= threshold:
                explanation.append(f"{Colors.GREEN}✓ Your hand (HS {hs}) meets this threshold.{Colors.END}")
            else:
                explanation.append(f"{Colors.RED}✗ Your hand (HS {hs}) is below this threshold.{Colors.END}")
            
            example_hands = self._get_example_hands_for_hs(threshold, stronger=True)
            explanation.append(f"{Colors.GREEN}  - Examples of hands to RAISE: {example_hands}{Colors.END}")
            example_weaker_hands = self._get_example_hands_for_hs(threshold, stronger=False)
            explanation.append(f"{Colors.RED}  - Examples of hands to FOLD: {example_weaker_hands}{Colors.END}")

        elif 'raise' in history:  # Facing raise
            if 'value_thresh' in rules:
                value_thresh = rules.get('value_thresh', 30)
                call_range = rules.get('call_range', [15, 25])
                
                explanation.append(f"\n{Colors.YELLOW}Rule:{Colors.END} Facing a raise from {game_state['position']}:")
                explanation.append(f"  • {Colors.GREEN}3-Bet (Re-raise){Colors.END} with premium hands, {Colors.BOLD}HS ≥ {value_thresh}{Colors.END}.")
                explanation.append(f"  • {Colors.YELLOW}Call{Colors.END} with strong but playable hands, {Colors.BOLD}HS {call_range[0]}-{call_range[1]}{Colors.END}.")
                explanation.append(f"  • {Colors.RED}Fold{Colors.END} with hands weaker than {Colors.BOLD}HS {call_range[0]}{Colors.END}.")
                
                explanation.append(f"\nYour hand's HS is {hs}.")
                
                # Give specific examples for each action
                raise_examples = self._get_example_hands_for_hs(value_thresh)
                explanation.append(f"  - Example 3-Bet hands: {raise_examples}")
                
                call_examples = self._get_example_hands_for_hs(call_range[0])
                explanation.append(f"  - Example Calling hands: {call_examples}")

        return explanation

    # MODIFIED: This method is also enhanced with better descriptions.
    def _explain_postflop_decision(self, game_state, optimal_action, rules, hs):
        """Detailed explanation for postflop decisions with descriptive examples."""
        explanation = []
        street = game_state['street']
        to_call = game_state['to_call']
        pot = game_state['pot']

        if game_state.get('was_aggressor') and to_call == 0:  # C-bet decision
            val_thresh = rules.get('val_thresh', 35)
            check_thresh = rules.get('check_thresh', 15)
            
            val_rank = self._get_postflop_rank_from_hs(val_thresh)
            check_rank = self._get_postflop_rank_from_hs(check_thresh)

            explanation.append(f"\n{Colors.YELLOW}Rule:{Colors.END} As the aggressor on the {street.upper()}:")
            explanation.append(f"  • {Colors.GREEN}Bet for Value{Colors.END} with strong hands like {Colors.BOLD}{val_rank} or better (HS ≥ {val_thresh}){Colors.END}.")
            explanation.append(f"  • {Colors.YELLOW}Check to control the pot{Colors.END} with marginal hands like {Colors.BOLD}{check_rank} (HS ≥ {check_thresh}){Colors.END}.")
            explanation.append(f"  • {Colors.RED}Check and be prepared to fold{Colors.END} with weaker hands (HS < {check_thresh}).")
            
            explanation.append(f"\nYour hand's current dynamic HS is {hs}.")

        elif to_call > 0:  # Facing a bet
            bet_ratio = to_call / pot if pot > 0 else 1
            bet_category = 'large_bet' if bet_ratio > 1 else 'medium_bet' if bet_ratio >= 0.5 else 'small_bet'
            
            thresholds = rules.get(bet_category, [60, 30])
            raise_thresh, call_thresh = thresholds[0], thresholds[1]

            raise_rank = self._get_postflop_rank_from_hs(raise_thresh)
            call_rank = self._get_postflop_rank_from_hs(call_thresh)
            
            explanation.append(f"\n{Colors.YELLOW}Rule:{Colors.END} Facing a {bet_category.replace('_', ' ')} on the {street.upper()}:")
            explanation.append(f"  • {Colors.GREEN}Raise{Colors.END} with monster hands like {Colors.BOLD}{raise_rank} or better (HS ≥ {raise_thresh}){Colors.END}.")
            explanation.append(f"  • {Colors.YELLOW}Call{Colors.END} with good made hands or strong draws like {Colors.BOLD}{call_rank} (HS ≥ {call_thresh}){Colors.END}.")
            explanation.append(f"  • {Colors.RED}Fold{Colors.END} with weaker hands (HS < {call_thresh}).")
            
            pot_odds = to_call / (pot + to_call) * 100
            explanation.append(f"  - You're getting pot odds of {pot_odds:.1f}%, which is a factor for calling with draws.")
            explanation.append(f"\nYour hand's current dynamic HS is {hs}.")

        return explanation

    # This private method can remain the same
    def _get_general_tips(self, game_state, optimal_action):
        """Add general strategic tips based on the situation."""
        tips = []
        tips.append(f"\n{Colors.BOLD}💡 Key Concepts:{Colors.END}")
        
        position = game_state['position']
        
        if position in ['UTG', 'MP']:
            tips.append("• From Early Position, your range should be tight. Mistakes are more costly because you act first on later streets.")
        elif position in ['CO', 'BTN']:
            tips.append("• From Late Position, you can play more hands. Position is a powerful advantage, allowing you to see what opponents do first.")
        
        if optimal_action[0] == 'fold':
            tips.append("• Disciplined folds are a hallmark of a strong player. Don't feel forced to play a hand just because you were dealt it.")
        elif optimal_action[0] in ['raise', 'bet']:
            tips.append("• Aggression builds the pot when you're strong and can make opponents fold when you're bluffing. Take control of the hand when the situation is right.")
            
        return tips

class GameOrchestrator:
    """
    Orchestrates the poker game, coordinating all the different modules.
    Manages the game loop, hand progression, and user interaction menu.
    """
    def __init__(self, num_players=6):
        print(f"{Colors.BOLD}Initializing trainer for {num_players} players...{Colors.END}")
        self.strategy = self._load_strategy()
        
        # Instantiate the correct components from the imported modules
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
        self.mistake_patterns = defaultdict(int)

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
            print(f"{Colors.RED}❌ Incorrect! Optimal was {opt_action.upper()}{Colors.END}")
            
            # Provide detailed explanation
            feedback_system = DetailedFeedbackSystem(self.strategy)
            explanation = feedback_system.explain_decision(
                game_state,
                (action, size),
                (opt_action, opt_size)
            )
            print(explanation)
            
            # Track mistake patterns
            mistake_key = f"{game_state['position']}_{game_state['street']}_{action}_should_{opt_action}"
            self.mistake_patterns[mistake_key] += 1
        
        # Update session stats
        self.session_stats[game_state['position']]['total'] += 1
        if is_correct:
            self.session_stats[game_state['position']]['correct'] += 1
        
        if self.session_logger and self.session_id:
            decision_data = {
                'hand_number': self.hand_count,
                'street': game_state['street'],
                'position': game_state['position'],
                'is_ip': game_state.get('is_ip', False),
                'hole_cards': ' '.join(player.hole),
                'board_cards': ' '.join(game_state.get('board', [])),
                'pot_size': game_state['pot'],
                'to_call': game_state['to_call'],
                'stack_size': player.stack,
                'preflop_hs': game_state.get('preflop_hs', 0),
                'postflop_hs': game_state.get('dynamic_hs', 0),
                'hand_rank': game_state.get('postflop_details', {}).get('rank', ''),
                'action_history': json.dumps(game_state.get('history', [])),
                'was_pfa': game_state.get('was_aggressor', False),
                'user_action': action,
                'user_size': size,
                'optimal_action': opt_action,
                'optimal_size': opt_size,
                'is_correct': is_correct
            }
            self.session_logger.log_decision(self.session_id, decision_data)

    def _showdown(self, hand_state):
        """Handles the showdown and awards the pot."""
        print(f"\n{Colors.BOLD}--- SHOWDOWN ---{Colors.END}")
        active_players = self.table.get_active_players()
        
        if not active_players:
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

    def print_session_summary(self):
        """Print detailed session statistics."""
        print(f"\n{Colors.BOLD}{'='*40}{Colors.END}")
        print(f"{Colors.BOLD}📊 SESSION SUMMARY (Hand #{self.hand_count}):{Colors.END}")
        print(f"{Colors.BOLD}{'='*40}{Colors.END}")
        
        total_decisions = sum(stats['total'] for stats in self.session_stats.values())
        total_correct = sum(stats['correct'] for stats in self.session_stats.values())
        
        if total_decisions > 0:
            overall_accuracy = (total_correct / total_decisions) * 100
            print(f"\nOverall Accuracy: {Colors.GREEN if overall_accuracy >= 70 else Colors.YELLOW if overall_accuracy >= 50 else Colors.RED}{overall_accuracy:.1f}%{Colors.END} ({total_correct}/{total_decisions})")
            
            print(f"\n{Colors.CYAN}By Position:{Colors.END}")
            for position, stats in sorted(self.session_stats.items()):
                if stats['total'] > 0:
                    accuracy = (stats['correct'] / stats['total']) * 100
                    color = Colors.GREEN if accuracy >= 70 else Colors.YELLOW if accuracy >= 50 else Colors.RED
                    print(f"  {position}: {color}{accuracy:.1f}%{Colors.END} ({stats['correct']}/{stats['total']})")
            
            if self.mistake_patterns:
                print(f"\n{Colors.CYAN}Common Mistakes:{Colors.END}")
                for mistake, count in sorted(self.mistake_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                    parts = mistake.split('_')
                    print(f"  {parts[0]} {parts[1]}: {parts[2]} → {parts[4]} ({count} times)")
        else:
            print("No decisions made yet!")
        
        print(f"{Colors.BOLD}{'='*40}{Colors.END}")

    def run(self):
        """Main application loop."""
        while True:
            self.play_hand()
            
            continue_prompt = input(f"\n{Colors.CYAN}Play another hand? (y/n) or (s)ession summary: {Colors.END}").lower()
            
            if continue_prompt == 's':
                self.print_session_summary()
                continue_prompt = input(f"\n{Colors.CYAN}Continue playing? (y/n): {Colors.END}").lower()
            
            if continue_prompt != 'y':
                break
        
        self.print_session_summary()
        print(f"\n{Colors.CYAN}Thanks for training!{Colors.END}")


def main():
    """Main entry point for the application."""
    num_players = 6
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        num_players = int(sys.argv[1])
    
    try:
        orchestrator = GameOrchestrator(num_players=num_players)
        orchestrator.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Training interrupted.{Colors.END}")
        orchestrator.print_session_summary()
        print(f"{Colors.YELLOW}Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}\nAn unexpected error occurred: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()