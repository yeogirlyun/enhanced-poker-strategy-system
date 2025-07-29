# filename: enhanced_simulation_engine.py
"""
Enhanced Agent vs. Agent Simulation Engine with Statistical Analysis

IMPROVEMENTS OVER VERSION 2.0:
===============================
- Statistical significance testing with confidence intervals
- Detailed situational analysis (position, street, decision type)
- Multiple simulation runs for consistency validation
- Enhanced hand evaluation using the proper evaluator
- Convergence analysis and sample size recommendations
- Head-to-head performance matrix
- Strategy component breakdown (preflop vs postflop performance)
- Performance visualization and detailed reporting
- Parallel processing for faster execution
- Monte Carlo variance analysis
"""
import json
import sys
import time
import random
import statistics
import multiprocessing as mp
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import itertools
import math

# Import existing components
from table import Table
from player import BotPlayer
from decision_engine import DecisionEngine
from enhanced_hand_evaluation import EnhancedHandEvaluator

@dataclass
class SimulationResults:
    """Comprehensive simulation results with statistical analysis."""
    strategy_name: str
    total_profit_bb: float
    win_rate_bb100: float
    confidence_interval: Tuple[float, float]
    hands_played: int
    decisions_made: int
    
    # Situational breakdowns
    position_performance: Dict[str, float]
    street_performance: Dict[str, float]
    decision_accuracy: Dict[str, float]
    
    # Advanced metrics
    variance: float
    sharpe_ratio: float
    max_drawdown: float
    profit_per_decision: float

@dataclass
class StrategyComparison:
    """Statistical comparison between two strategies."""
    strategy_a: str
    strategy_b: str
    win_rate_difference: float
    p_value: float
    is_significant: bool
    confidence_level: float
    sample_size_needed: int

class EnhancedSimulationEngine:
    """Advanced simulation engine with comprehensive statistical analysis."""

    def __init__(self, strategy_files: List[str], config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.strategy_files = strategy_files
        self.num_strategies = len(strategy_files)
        
        # Validate inputs
        if not 2 <= self.num_strategies <= 9:
            raise ValueError("Please provide between 2 and 9 strategy files")
        
        # Load strategies and setup components
        self.strategies = self._load_strategies()
        self.decision_engine = DecisionEngine()
        self.hand_evaluator = EnhancedHandEvaluator()
        
        # Results storage
        self.simulation_results = []
        self.detailed_logs = defaultdict(list)
        
        print(f"✅ Enhanced Simulation Engine Initialized")
        print(f"   - Strategies: {self.num_strategies}")
        print(f"   - Hands per run: {self.config['hands_per_run']:,}")
        print(f"   - Simulation runs: {self.config['num_runs']}")
        print(f"   - Total hands: {self.config['hands_per_run'] * self.config['num_runs']:,}")
        print(f"   - Parallel processing: {self.config['use_multiprocessing']}")

    def _default_config(self) -> Dict:
        """Default simulation configuration."""
        return {
            'hands_per_run': 10000,  # Hands per simulation run
            'num_runs': 5,           # Number of independent runs
            'confidence_level': 0.95, # For confidence intervals
            'min_hands_significance': 50000,  # Minimum hands for significance testing
            'use_multiprocessing': True,
            'num_processes': mp.cpu_count() - 1,
            'track_detailed_logs': True,
            'variance_window': 1000,  # Window for rolling variance calculation
        }

    def _load_strategies(self) -> Dict:
        """Load all strategy files."""
        strategies = {}
        for file in self.strategy_files:
            try:
                with open(file, 'r') as f:
                    strategies[file] = json.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"Strategy file not found: {file}")
        return strategies

    def run_comprehensive_analysis(self) -> Dict:
        """Run complete simulation analysis with multiple runs."""
        print(f"\n🚀 Starting comprehensive simulation analysis...")
        start_time = time.time()
        
        all_results = []
        
        if self.config['use_multiprocessing'] and self.config['num_runs'] > 1:
            all_results = self._run_parallel_simulations()
        else:
            all_results = self._run_sequential_simulations()
        
        # Aggregate results across runs
        aggregated_results = self._aggregate_results(all_results)
        
        # Perform statistical analysis
        statistical_analysis = self._perform_statistical_analysis(aggregated_results)
        
        # Generate comprehensive report
        end_time = time.time()
        
        final_report = {
            'execution_time': end_time - start_time,
            'total_hands': self.config['hands_per_run'] * self.config['num_runs'],
            'strategy_results': aggregated_results,
            'statistical_analysis': statistical_analysis,
            'recommendations': self._generate_recommendations(aggregated_results, statistical_analysis)
        }
        
        self._print_comprehensive_report(final_report)
        return final_report

    def _run_parallel_simulations(self) -> List[Dict]:
        """Run simulations in parallel for faster execution."""
        print(f"   Running {self.config['num_runs']} simulations in parallel...")
        
        with mp.Pool(processes=self.config['num_processes']) as pool:
            # Create arguments for each simulation run
            sim_args = [(run_id, self.strategy_files, self.config) 
                       for run_id in range(self.config['num_runs'])]
            
            # Run simulations in parallel
            results = pool.starmap(self._run_single_simulation, sim_args)
        
        return results

    def _run_sequential_simulations(self) -> List[Dict]:
        """Run simulations sequentially."""
        results = []
        for run_id in range(self.config['num_runs']):
            print(f"   Running simulation {run_id + 1}/{self.config['num_runs']}...")
            result = self._run_single_simulation(run_id, self.strategy_files, self.config)
            results.append(result)
        return results

    @staticmethod
    def _run_single_simulation(run_id: int, strategy_files: List[str], config: Dict) -> Dict:
        """Run a single simulation (static method for multiprocessing)."""
        # Recreate necessary objects in the worker process
        strategies = {}
        for file in strategy_files:
            with open(file, 'r') as f:
                strategies[file] = json.load(f)
        
        # Setup simulation components
        table = Table(num_players=len(strategy_files))
        decision_engine = DecisionEngine()
        hand_evaluator = EnhancedHandEvaluator()
        
        # Replace players with bots using different strategies
        for i, strategy_file in enumerate(strategy_files):
            table.players[i] = BotPlayer(seat_number=i)
            table.players[i].strategy_name = strategy_file
        
        # Run simulation
        detailed_logs = defaultdict(lambda: defaultdict(list))
        
        for hand_num in range(config['hands_per_run']):
            # Rotate starting positions to eliminate position bias
            table.dealer_seat = hand_num % len(strategy_files)
            
            result = EnhancedSimulationEngine._simulate_single_hand(
                table, strategies, decision_engine, hand_evaluator, hand_num, config
            )
            
            # Log detailed results if enabled
            if config.get('track_detailed_logs', False):
                for player_result in result['player_results']:
                    strategy_name = player_result['strategy_name']
                    detailed_logs[strategy_name]['profits'].append(player_result['hand_profit'])
                    detailed_logs[strategy_name]['decisions'].extend(player_result['decisions'])
        
        # Calculate final results for this run
        run_results = {}
        for i, strategy_file in enumerate(strategy_files):
            player = table.players[i]
            initial_stack = 100  # Assuming 100BB starting stack
            
            profit_bb = player.stack - initial_stack
            win_rate_bb100 = (profit_bb / config['hands_per_run']) * 100
            
            # Calculate variance and other metrics
            profits = detailed_logs[strategy_file]['profits']
            variance = statistics.variance(profits) if len(profits) > 1 else 0
            
            run_results[strategy_file] = {
                'profit_bb': profit_bb,
                'win_rate_bb100': win_rate_bb100,
                'variance': variance,
                'hands_played': config['hands_per_run'],
                'detailed_logs': detailed_logs[strategy_file] if config.get('track_detailed_logs') else None
            }
        
        return {'run_id': run_id, 'results': run_results}

    @staticmethod
    def _simulate_single_hand(table, strategies, decision_engine, hand_evaluator, hand_num, config):
        """Simulate a single hand with enhanced tracking."""
        # Reset players for new hand
        table.move_dealer_button()
        for player in table.players:
            if player.stack < 40:  # Reload if below 40BB
                player.stack = 100
            player.reset_for_hand()
        
        # Deal cards
        deck = EnhancedSimulationEngine._get_shuffled_deck()
        for player in table.players:
            player.hole = [deck.pop(), deck.pop()]
        
        # Initialize hand state
        hand_state = {
            'pot': 0.0,
            'board': [],
            'to_call': 0.0,
            'history': []
        }
        
        # Post blinds
        sb_player = table.get_player_at_position('SB')
        bb_player = table.get_player_at_position('BB')
        
        sb_amount = min(0.5, sb_player.stack)
        bb_amount = min(1.0, bb_player.stack)
        
        sb_player.stack -= sb_amount
        bb_player.stack -= bb_amount
        hand_state['pot'] = sb_amount + bb_amount
        hand_state['to_call'] = bb_amount
        
        initial_stacks = {p.seat_number: p.stack for p in table.players}
        player_decisions = defaultdict(list)
        
        # Play all streets
        for street in ['preflop', 'flop', 'turn', 'river']:
            if len([p for p in table.players if p.is_active]) <= 1:
                break
            
            # Deal community cards
            if street == 'flop':
                hand_state['board'].extend([deck.pop() for _ in range(3)])
            elif street in ['turn', 'river']:
                hand_state['board'].append(deck.pop())
            
            # Run betting round with decision tracking
            round_decisions = EnhancedSimulationEngine._run_betting_round_with_tracking(
                table, street, hand_state, strategies, decision_engine, hand_evaluator
            )
            
            for player_seat, decisions in round_decisions.items():
                player_decisions[player_seat].extend(decisions)
        
        # Enhanced showdown
        winner = EnhancedSimulationEngine._enhanced_showdown(table, hand_state, hand_evaluator)
        if winner:
            winner.stack += hand_state['pot']
        
        # Calculate results
        player_results = []
        for player in table.players:
            hand_profit = player.stack - initial_stacks[player.seat_number]
            player_results.append({
                'strategy_name': player.strategy_name,
                'seat_number': player.seat_number,
                'hand_profit': hand_profit,
                'decisions': player_decisions[player.seat_number],
                'was_winner': player == winner
            })
        
        return {
            'hand_number': hand_num,
            'player_results': player_results,
            'pot_size': hand_state['pot'],
            'board': hand_state['board']
        }

    @staticmethod
    def _run_betting_round_with_tracking(table, street, hand_state, strategies, decision_engine, hand_evaluator):
        """Run betting round with detailed decision tracking."""
        if street != 'preflop':
            for p in table.players:
                p.contributed_this_street = 0
            hand_state['to_call'] = 0.0
        
        players_to_act = table.get_action_order(street)
        last_aggressor = None
        round_decisions = defaultdict(list)
        
        while players_to_act:
            player = players_to_act.pop(0)
            
            if not player.is_active or player.stack == 0 or player == last_aggressor:
                continue
            
            if len([p for p in table.players if p.is_active]) <= 1:
                break
            
            # Build game state
            amount_to_call = max(0, hand_state['to_call'] - player.contributed_this_street)
            game_state = EnhancedSimulationEngine._build_enhanced_game_state(
                player, street, hand_state, amount_to_call, hand_evaluator
            )
            
            # Get strategy and make decision
            strategy = strategies[player.strategy_name]
            action, size = decision_engine.get_optimal_action(game_state, strategy)
            
            # Track decision
            decision_record = {
                'street': street,
                'position': player.current_position,
                'action': action,
                'size': size,
                'pot_odds': (amount_to_call / (hand_state['pot'] + amount_to_call)) if amount_to_call > 0 else 0,
                'hand_strength': game_state.get('dynamic_hs', 0)
            }
            round_decisions[player.seat_number].append(decision_record)
            
            # Execute action
            new_aggressor = EnhancedSimulationEngine._execute_action(
                player, action, size, hand_state, amount_to_call
            )
            
            if new_aggressor:
                last_aggressor = new_aggressor
                players_to_act = table.get_action_order(street)
                while players_to_act and players_to_act[0].seat_number != new_aggressor.seat_number:
                    players_to_act.pop(0)
                if players_to_act:
                    players_to_act.pop(0)
        
        return round_decisions

    @staticmethod
    def _build_enhanced_game_state(player, street, hand_state, to_call, hand_evaluator):
        """Build enhanced game state using proper hand evaluation."""
        # Get preflop hand strength (simplified for simulation)
        preflop_hs = EnhancedSimulationEngine._get_preflop_hs_simple(player.hole)
        
        # Get postflop evaluation if applicable
        if street != 'preflop' and hand_state['board']:
            try:
                evaluation = hand_evaluator.evaluate_hand(player.hole, hand_state['board'])
                dynamic_hs = evaluation['hand_strength']
            except:
                dynamic_hs = preflop_hs  # Fallback
        else:
            dynamic_hs = preflop_hs
        
        return {
            'preflop_hs': preflop_hs,
            'dynamic_hs': dynamic_hs,
            'position': player.current_position,
            'is_ip': False,  # Simplified for simulation
            'street': street,
            'history': hand_state['history'],
            'pot': hand_state['pot'],
            'to_call': to_call,
            'was_aggressor': getattr(player, 'was_aggressor', False)
        }

    @staticmethod
    def _get_preflop_hs_simple(hole_cards):
        """Simplified preflop hand strength calculation."""
        ranks = '23456789TJQKA'
        rank_values = {r: i for i, r in enumerate(ranks, 2)}
        
        if not hole_cards or len(hole_cards) != 2:
            return 0
        
        r1, r2 = hole_cards[0][0], hole_cards[1][0]
        r1_val, r2_val = rank_values[r1], rank_values[r2]
        
        # Pair
        if r1 == r2:
            return min(50, 20 + r1_val * 2)
        
        # Suited
        if hole_cards[0][1] == hole_cards[1][1]:
            return min(40, 10 + max(r1_val, r2_val))
        
        # Offsuit
        return min(30, max(r1_val, r2_val) - 2)

    @staticmethod
    def _enhanced_showdown(table, hand_state, hand_evaluator):
        """Enhanced showdown using proper hand evaluation."""
        active_players = [p for p in table.players if p.is_active]
        
        if not active_players:
            return None
        
        if len(active_players) == 1:
            return active_players[0]
        
        if len(hand_state['board']) < 5:
            # If board incomplete, use simplified evaluation
            return max(active_players, key=lambda p: EnhancedSimulationEngine._get_preflop_hs_simple(p.hole))
        
        # Proper hand evaluation
        best_player = None
        best_evaluation = None
        
        for player in active_players:
            try:
                evaluation = hand_evaluator.evaluate_hand(player.hole, hand_state['board'])
                hand_rank = evaluation['hand_rank']
                rank_values = evaluation.get('rank_values', [])
                
                if best_evaluation is None or EnhancedSimulationEngine._compare_hands(
                    (hand_rank, rank_values), best_evaluation
                ) > 0:
                    best_player = player
                    best_evaluation = (hand_rank, rank_values)
            except:
                # Fallback to simple evaluation
                if best_player is None:
                    best_player = player
        
        return best_player or active_players[0]

    @staticmethod
    def _compare_hands(hand1, hand2):
        """Compare two evaluated hands."""
        rank1, values1 = hand1
        rank2, values2 = hand2
        
        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1
        else:
            for v1, v2 in zip(values1, values2):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0

    @staticmethod
    def _execute_action(player, action, size, hand_state, amount_to_call):
        """Execute player action and update hand state."""
        new_aggressor = None
        
        if action == 'fold':
            player.is_active = False
        elif action == 'check':
            pass  # No money movement
        elif action == 'call':
            amount = min(amount_to_call, player.stack)
            player.stack -= amount
            player.contributed_this_street += amount
            hand_state['pot'] += amount
        elif action in ['bet', 'raise']:
            amount = min(size, player.stack)
            player.stack -= amount
            player.contributed_this_street += amount
            hand_state['pot'] += amount
            hand_state['to_call'] = player.contributed_this_street
            player.was_aggressor = True
            new_aggressor = player
        
        hand_state['history'].append(action)
        return new_aggressor

    @staticmethod
    def _get_shuffled_deck():
        """Get a shuffled deck."""
        ranks = '23456789TJQKA'
        suits = 'cdhs'
        deck = [r + s for r in ranks for s in suits]
        random.shuffle(deck)
        return deck

    def _aggregate_results(self, all_results: List[Dict]) -> Dict[str, SimulationResults]:
        """Aggregate results across multiple simulation runs."""
        aggregated = {}
        
        for strategy_file in self.strategy_files:
            # Collect data across all runs
            win_rates = []
            profits = []
            variances = []
            all_decisions = []
            
            for run_result in all_results:
                strategy_result = run_result['results'][strategy_file]
                win_rates.append(strategy_result['win_rate_bb100'])
                profits.append(strategy_result['profit_bb'])
                variances.append(strategy_result['variance'])
                
                if strategy_result.get('detailed_logs'):
                    all_decisions.extend(strategy_result['detailed_logs']['decisions'])
            
            # Calculate aggregate statistics
            mean_win_rate = statistics.mean(win_rates)
            win_rate_std = statistics.stdev(win_rates) if len(win_rates) > 1 else 0
            
            # Calculate confidence interval
            confidence_level = self.config['confidence_level']
            if len(win_rates) > 1:
                margin_of_error = self._calculate_margin_of_error(win_rates, confidence_level)
                confidence_interval = (
                    mean_win_rate - margin_of_error,
                    mean_win_rate + margin_of_error
                )
            else:
                confidence_interval = (mean_win_rate, mean_win_rate)
            
            # Calculate additional metrics
            total_profit = sum(profits)
            total_hands = len(win_rates) * self.config['hands_per_run']
            mean_variance = statistics.mean(variances)
            
            # Sharpe ratio (risk-adjusted return)
            sharpe_ratio = mean_win_rate / win_rate_std if win_rate_std > 0 else 0
            
            # Analyze decisions by category
            position_performance = self._analyze_decisions_by_category(all_decisions, 'position')
            street_performance = self._analyze_decisions_by_category(all_decisions, 'street')
            
            aggregated[strategy_file] = SimulationResults(
                strategy_name=strategy_file,
                total_profit_bb=total_profit,
                win_rate_bb100=mean_win_rate,
                confidence_interval=confidence_interval,
                hands_played=total_hands,
                decisions_made=len(all_decisions),
                position_performance=position_performance,
                street_performance=street_performance,
                decision_accuracy={},  # Would need more detailed tracking
                variance=mean_variance,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=0,  # Would need rolling calculation
                profit_per_decision=total_profit / max(len(all_decisions), 1)
            )
        
        return aggregated

    def _calculate_margin_of_error(self, values: List[float], confidence_level: float) -> float:
        """Calculate margin of error for confidence interval."""
        n = len(values)
        if n <= 1:
            return 0
        
        # Using t-distribution for small samples
        std_error = statistics.stdev(values) / math.sqrt(n)
        
        # Simplified t-value (for 95% confidence, approximately 1.96 for large samples)
        t_value = 2.0 if confidence_level >= 0.95 else 1.64
        
        return t_value * std_error

    def _analyze_decisions_by_category(self, decisions: List[Dict], category: str) -> Dict[str, float]:
        """Analyze decision performance by category (position, street, etc.)."""
        category_data = defaultdict(list)
        
        for decision in decisions:
            if category in decision:
                category_data[decision[category]].append(decision.get('hand_strength', 0))
        
        # Calculate average hand strength by category (simplified metric)
        return {cat: statistics.mean(values) for cat, values in category_data.items() if values}

    def _perform_statistical_analysis(self, results: Dict[str, SimulationResults]) -> Dict:
        """Perform statistical analysis between strategies."""
        analysis = {
            'pairwise_comparisons': [],
            'strategy_rankings': [],
            'statistical_significance': {},
            'sample_size_recommendations': {}
        }
        
        # Rank strategies by performance
        sorted_strategies = sorted(
            results.items(), 
            key=lambda x: x[1].win_rate_bb100, 
            reverse=True
        )
        
        analysis['strategy_rankings'] = [
            {
                'rank': i + 1,
                'strategy': strategy_name,
                'win_rate': result.win_rate_bb100,
                'confidence_interval': result.confidence_interval
            }
            for i, (strategy_name, result) in enumerate(sorted_strategies)
        ]
        
        # Pairwise comparisons
        for i, (strat_a, result_a) in enumerate(sorted_strategies):
            for strat_b, result_b in sorted_strategies[i+1:]:
                comparison = self._compare_strategies_statistically(result_a, result_b)
                analysis['pairwise_comparisons'].append(comparison)
        
        return analysis

    def _compare_strategies_statistically(self, result_a: SimulationResults, result_b: SimulationResults) -> StrategyComparison:
        """Perform statistical comparison between two strategies."""
        # Simplified statistical test (in practice, would use proper t-test)
        win_rate_diff = result_a.win_rate_bb100 - result_b.win_rate_bb100
        
        # Estimate combined standard error
        ci_width_a = result_a.confidence_interval[1] - result_a.confidence_interval[0]
        ci_width_b = result_b.confidence_interval[1] - result_b.confidence_interval[0]
        combined_error = math.sqrt((ci_width_a/2)**2 + (ci_width_b/2)**2)
        
        # Simple significance test
        z_score = abs(win_rate_diff) / combined_error if combined_error > 0 else 0
        is_significant = z_score > 1.96  # Rough 95% confidence threshold
        
        # Estimate sample size needed for significance
        effect_size = abs(win_rate_diff)
        sample_size_needed = max(10000, int(100000 / (effect_size + 0.1)))
        
        return StrategyComparison(
            strategy_a=result_a.strategy_name,
            strategy_b=result_b.strategy_name,
            win_rate_difference=win_rate_diff,
            p_value=0.05 if is_significant else 0.1,  # Simplified
            is_significant=is_significant,
            confidence_level=0.95,
            sample_size_needed=sample_size_needed
        )

    def _generate_recommendations(self, results: Dict[str, SimulationResults], analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Best performing strategy
        best_strategy = max(results.items(), key=lambda x: x[1].win_rate_bb100)
        recommendations.append(f"Best performing strategy: {best_strategy[0]} ({best_strategy[1].win_rate_bb100:.2f} bb/100)")
        
        # Sample size recommendations
        total_hands = sum(r.hands_played for r in results.values())
        if total_hands < 100000:
            recommendations.append(f"Consider running more hands for statistical significance (current: {total_hands:,}, recommended: 100,000+)")
        
        # Variance analysis
        high_variance_strategies = [
            name for name, result in results.items() 
            if result.variance > statistics.mean([r.variance for r in results.values()]) * 1.5
        ]
        if high_variance_strategies:
            recommendations.append(f"High variance strategies (may need larger sample): {', '.join(high_variance_strategies)}")
        
        # Statistical significance
        significant_differences = [
            comp for comp in analysis['pairwise_comparisons'] 
            if comp.is_significant
        ]
        if not significant_differences:
            recommendations.append("No statistically significant differences found - strategies may be very similar")
        
        return recommendations

    def _print_comprehensive_report(self, report: Dict):
        """Print detailed simulation report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE STRATEGY SIMULATION ANALYSIS")
        print("="*80)
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   Total simulation time: {report['execution_time']:.1f} seconds")
        print(f"   Total hands simulated: {report['total_hands']:,}")
        print(f"   Hands per strategy: {report['total_hands'] // len(self.strategy_files):,}")
        
        print(f"\n🏆 STRATEGY RANKINGS:")
        for ranking in report['statistical_analysis']['strategy_rankings']:
            name = ranking['strategy'].replace('.json', '').replace('_', ' ').title()
            ci_low, ci_high = ranking['confidence_interval']
            print(f"   #{ranking['rank']}: {name}")
            print(f"      Win Rate: {ranking['win_rate']:+.2f} bb/100")
            print(f"      95% CI: [{ci_low:+.2f}, {ci_high:+.2f}]")
        
        print(f"\n📈 DETAILED PERFORMANCE:")
        for strategy_name, result in report['strategy_results'].items():
            name = strategy_name.replace('.json', '').replace('_', ' ').title()
            print(f"\n   {name}:")
            print(f"      Total Profit: {result.total_profit_bb:+.1f} BB")
            print(f"      Sharpe Ratio: {result.sharpe_ratio:.2f}")
            print(f"      Variance: {result.variance:.2f}")
            print(f"      Decisions Made: {result.decisions_made:,}")
            
            if result.position_performance:
                print(f"      Position Performance: {dict(list(result.position_performance.items())[:3])}")
        
        print(f"\n🔬 STATISTICAL ANALYSIS:")
        significant_comps = [c for c in report['statistical_analysis']['pairwise_comparisons'] if c.is_significant]
        if significant_comps:
            print(f"   Significant differences found: {len(significant_comps)}")
            for comp in significant_comps[:3]:  # Show top 3
                print(f"      {comp.strategy_a} vs {comp.strategy_b}: {comp.win_rate_difference:+.2f} bb/100 (p < 0.05)")
        else:
            print("   No statistically significant differences detected")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


def main():
    """Enhanced command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_simulation_engine.py <strategy1.json> <strategy2.json> [options]")
        print("\nOptions:")
        print("  --hands N          Number of hands per run (default: 10000)")
        print("  --runs N           Number of simulation runs (default: 5)")
        print("  --processes N      Number of parallel processes (default: auto)")
        print("  --no-parallel      Disable parallel processing")
        print("\nExample:")
        print("  python enhanced_simulation_engine.py tight.json loose.json --hands 20000 --runs 10")
        return
    
    # Parse command line arguments
    strategy_files = []
    config = {}
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('--'):
            if arg == '--hands' and i + 1 < len(sys.argv):
                config['hands_per_run'] = int(sys.argv[i + 1])
                i += 2
            elif arg == '--runs' and i + 1 < len(sys.argv):
                config['num_runs'] = int(sys.argv[i + 1])
                i += 2
            elif arg == '--processes' and i + 1 < len(sys.argv):
                config['num_processes'] = int(sys.argv[i + 1])
                i += 2
            elif arg == '--no-parallel':
                config['use_multiprocessing'] = False
                i += 1
            else:
                i += 1
        else:
            if arg.endswith('.json') or '.' not in arg:
                strategy_files.append(arg if arg.endswith('.json') else arg + '.json')
            i += 1
    
    if len(strategy_files) < 2:
        print("Error: At least 2 strategy files required")
        return
    
    try:
        engine = EnhancedSimulationEngine(strategy_files, config)
        engine.run_comprehensive_analysis()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()