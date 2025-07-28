# filename: simulation_engine.py
"""
Agent vs. Agent Simulation Engine for Hold'em Strategy Evaluation

REVISION HISTORY:
================
Version 2.0 (2025-07-28) - Flexible N-Strategy Comparison
- RECONFIGURED: Engine now accepts any number of strategy files as command-line
  arguments, allowing for flexible A/B/C/... testing.
- DYNAMIC PLAYER SETUP: The table size and player strategies are now created
  dynamically based on the number of input files.
- ADDED: The final results report is now sorted by performance and includes
  a rank for each strategy.
- SIMPLIFIED: Removed hardcoded configuration in favor of dynamic command-line
  based setup for easier use.

Version 1.0 (2025-07-28) - Initial Implementation
- Implemented SimulationEngine for high-speed, headless simulations.
"""
import json
import sys
import time
import random
from collections import defaultdict

# Leverage our existing, well-structured components
from table import Table
from player import BotPlayer
from decision_engine import DecisionEngine

# Constants for the simulation
INITIAL_STACK = 100
SMALL_BLIND = 0.5
BIG_BLIND = 1.0
NUM_HANDS_TO_SIMULATE = 20000 # Increased for better statistical significance

class SimulationEngine:
    """Orchestrates a high-speed simulation between bots using different strategies."""

    # CHANGED: Init now takes a list of strategy files
    def __init__(self, strategy_files):
        if not 2 <= len(strategy_files) <= 9:
            print("❌ Error: Please provide between 2 and 9 strategy files to compare.")
            sys.exit(1)
            
        self.strategy_files = strategy_files
        self.num_hands = NUM_HANDS_TO_SIMULATE
        self.strategies = self._load_strategies(self.strategy_files)
        
        self.player_map = self._setup_players(self.strategy_files)
        self.table = Table(num_players=len(self.player_map))
        self.decision_engine = DecisionEngine()
        
        self.table.players = [p['player'] for p in self.player_map]
        
        print("✅ Simulation Engine Initialized")
        print(f"   - Simulating {self.num_hands} hands.")
        print(f"   - Comparing {len(self.strategy_files)} strategies in a {len(self.strategy_files)}-player game.")
        print("-" * 40)

    def _load_strategies(self, strategy_files):
        """Loads all necessary strategy JSON files into memory."""
        loaded_strategies = {}
        for strategy_file in strategy_files:
            if strategy_file in loaded_strategies: continue # Avoid loading the same file twice
            try:
                with open(strategy_file, 'r') as f:
                    loaded_strategies[strategy_file] = json.load(f)
            except FileNotFoundError:
                print(f"❌ FATAL: Strategy file not found: '{strategy_file}'")
                sys.exit(1)
        return loaded_strategies

    # CHANGED: Setup now takes a list of files and creates one player per file
    def _setup_players(self, strategy_files):
        """Creates bot players and assigns them a strategy, one for each file."""
        player_map = []
        for i, strategy_file in enumerate(strategy_files):
            bot = BotPlayer(seat_number=i)
            bot.stack = INITIAL_STACK
            player_map.append({
                'player': bot,
                'strategy_name': strategy_file,
                'initial_stack': INITIAL_STACK
            })
        return player_map

    def run_simulation(self):
        """Executes the entire simulation."""
        start_time = time.time()
        print(f"🚀 Starting simulation of {self.num_hands} hands...")
        
        for hand_num in range(1, self.num_hands + 1):
            self._play_one_hand()
            if hand_num % (self.num_hands // 10) == 0: # Print progress every 10%
                print(f"   ... {(hand_num / self.num_hands) * 100:.0f}% complete ({hand_num} hands).")

        end_time = time.time()
        print(f"🏁 Simulation finished in {end_time - start_time:.2f} seconds.")
        self._analyze_and_print_results()

    def _play_one_hand(self):
        # This method's internal logic remains the same
        self.table.move_dealer_button()
        for p_map in self.player_map:
            if p_map['player'].stack < BIG_BLIND * 40:
                p_map['player'].stack = INITIAL_STACK
            p_map['player'].reset_for_hand()

        deck = self._get_shuffled_deck()
        for p_map in self.player_map:
            p_map['player'].hole = [deck.pop(), deck.pop()]

        hand_state = {'pot': 0.0, 'board': [], 'to_call': 0.0, 'history': []}

        sb_player = self.table.get_player_at_position('SB')
        bb_player = self.table.get_player_at_position('BB')
        sb_player.stack -= SMALL_BLIND
        sb_player.contributed_this_street = SMALL_BLIND
        bb_player.stack -= BIG_BLIND
        bb_player.contributed_this_street = BIG_BLIND
        hand_state['pot'] = SMALL_BLIND + BIG_BLIND
        hand_state['to_call'] = BIG_BLIND

        for street in ['preflop', 'flop', 'turn', 'river']:
            if len([p for p in self.table.players if p.is_active]) <= 1: break
            if street == 'flop': hand_state['board'].extend([deck.pop() for _ in range(3)])
            elif street in ['turn', 'river']: hand_state['board'].append(deck.pop())
            self._run_betting_round(street, hand_state)
        self._showdown(hand_state)

    def _run_betting_round(self, street, hand_state):
        # This method's internal logic remains the same
        if street != 'preflop':
            for p in self.table.players: p.contributed_this_street = 0
            hand_state['to_call'] = 0.0
        
        players_to_act = self.table.get_action_order(street)
        last_aggressor = None
        
        while players_to_act:
            player = players_to_act.pop(0)
            if not player.is_active or player.stack == 0 or player == last_aggressor: continue
            if len([p for p in self.table.players if p.is_active]) <= 1: break

            bot_strategy_name = next(p['strategy_name'] for p in self.player_map if p['player'] == player)
            bot_strategy = self.strategies[bot_strategy_name]
            
            amount_to_call = max(0, hand_state['to_call'] - player.contributed_this_street)
            player_game_state = self._build_player_game_state(player, street, hand_state, amount_to_call) # Simplified state
            action, size = self.decision_engine.get_optimal_action(player_game_state, bot_strategy)

            new_aggressor = self._execute_action(player, action, size, hand_state, amount_to_call)
            if new_aggressor:
                last_aggressor = new_aggressor
                players_to_act = self.table.get_action_order(street)
                while players_to_act and players_to_act[0].seat_number != new_aggressor.seat_number:
                    players_to_act.pop(0)
                if players_to_act: players_to_act.pop(0)

    def _showdown(self, hand_state):
        # This method's internal logic remains the same
        active_players = [p for p in self.table.players if p.is_active]
        if not active_players: return
        if len(active_players) == 1:
            winner = active_players[0]
        else:
            winner = max(active_players, key=lambda p: self._get_hand_value(p.hole + hand_state['board']))
        winner.stack += hand_state['pot']

    # CHANGED: Analysis now sorts and ranks the results
    def _analyze_and_print_results(self):
        """Calculates, sorts, ranks, and prints the final simulation results."""
        results_list = []
        for p_map in self.player_map:
            profit = p_map['player'].stack - p_map['initial_stack']
            profit_bb = profit / BIG_BLIND
            win_rate_bb_100 = (profit_bb / self.num_hands) * 100
            
            results_list.append({
                'name': p_map['strategy_name'],
                'profit_bb': profit_bb,
                'win_rate_bb_100': win_rate_bb_100
            })
            
        # Sort the results by win rate in descending order
        sorted_results = sorted(results_list, key=lambda x: x['win_rate_bb_100'], reverse=True)

        print("\n" + "="*50)
        print("📊 RANKED SIMULATION RESULTS")
        print("="*50)
        
        for i, result in enumerate(sorted_results):
            rank = i + 1
            name = result['name']
            profit_bb = result['profit_bb']
            win_rate_bb_100 = result['win_rate_bb_100']
            
            color = '\033[92m' if win_rate_bb_100 > 0 else '\033[91m'
            print(f"\nRank #{rank}: '{name}'")
            print(f"  - Total Profit: {profit_bb:+.2f} BB")
            print(f"  - Win Rate: {color}{win_rate_bb_100:+.2f} bb/100 hands\033[0m")
        print("="*50)

    # --- Helper Methods ---
    def _get_shuffled_deck(self):
        deck = [r + s for r in '23456789TJQKA' for s in 'cdhs']
        random.shuffle(deck)
        return deck
        
    def _build_player_game_state(self, player, street, hand_state, to_call):
        ranks = '23456789TJQKA'
        rank_values = {r: i for i, r in enumerate(ranks, 2)}
        r_vals = sorted([rank_values[c[0]] for c in player.hole], reverse=True)
        r1, r2 = ranks[r_vals[0]-2], ranks[r_vals[1]-2]
        suited = player.hole[0][1] == player.hole[1][1]
        key = r1 + r2 if r1 == r2 else (r1 + r2 + 's' if suited else r1 + r2 + 'o')
        bot_strategy = self.strategies[next(p['strategy_name'] for p in self.player_map if p['player'] == player)]
        hs = bot_strategy['hand_strength_tables']['preflop'].get(key, 0)
        return {'preflop_hs': hs, 'dynamic_hs': hs, 'position': player.current_position, 'street': street, 'history': hand_state['history'], 'pot': hand_state['pot'], 'to_call': to_call}
    
    def _execute_action(self, player, action, size, hand_state, to_call):
        new_aggressor = None
        if action == 'fold': player.is_active = False
        elif action == 'call':
            amount = min(to_call, player.stack)
            player.stack -= amount; player.contributed_this_street += amount; hand_state['pot'] += amount
        elif action in ['bet', 'raise']:
            amount = min(size, player.stack)
            player.stack -= amount; player.contributed_this_street += amount; hand_state['pot'] += amount
            hand_state['to_call'] = player.contributed_this_street
            new_aggressor = player
        hand_state['history'].append(action)
        return new_aggressor

    def _get_hand_value(self, cards):
        return max('23456789TJQKA'.index(c[0]) for c in cards)

# --- Main Execution Block ---
if __name__ == '__main__':
    # CHANGED: Get strategy files from command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 simulation_engine.py <strategy1.json> <strategy2.json> ...")
        print("Example: python3 simulation_engine.py strategy_good.json strategy_bad.json")
        sys.exit(1)
        
    strategy_files_to_compare = sys.argv[1:]
    
    engine = SimulationEngine(strategy_files_to_compare)
    engine.run_simulation()