# filename: human_executable_optimizer.py
"""
Human-Executable Strategy Optimization System

This system automatically optimizes decision tables while respecting human
memorability constraints through predefined HS tiers. It finds the best
performance within the constraint of easy real-time execution.

Key Features:
- Respects user-defined HS tiers for human memorability
- Optimizes decision thresholds using advanced search algorithms
- Balances performance vs. execution complexity
- Generates human-readable strategy guides
- Validates strategies through simulation
"""

import json
import numpy as np
import random
import copy
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import itertools
from enhanced_simulation_engine import EnhancedSimulationEngine
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution, minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern

@dataclass
class HSTier:
    """Represents a Hand Strength tier for human memorability."""
    name: str
    min_hs: int
    max_hs: int
    hands: List[str]
    description: str
    color_code: str  # For visualization

@dataclass
class OptimizationConstraints:
    """Constraints for human-executable strategy optimization."""
    max_tiers_per_decision: int = 3  # Max tiers to consider in one decision
    max_threshold_complexity: int = 5  # Max different thresholds per street
    require_monotonic_thresholds: bool = True  # Tighter in earlier positions
    allow_tier_splitting: bool = False  # Can split tiers for decisions
    execution_time_limit: float = 3.0  # Max seconds to make decision

@dataclass
class OptimizationResult:
    """Result of strategy optimization."""
    optimized_strategy: Dict
    performance_metrics: Dict
    execution_complexity: Dict
    tier_usage_analysis: Dict
    human_readability_score: float
    optimization_history: List[Dict]

class HumanExecutableOptimizer:
    """
    Optimizes poker strategy decision tables while maintaining human executability
    through predefined Hand Strength tiers and memorability constraints.
    """
    
    def __init__(self, hs_tiers: List[HSTier], constraints: OptimizationConstraints = None):
        self.hs_tiers = sorted(hs_tiers, key=lambda t: t.min_hs, reverse=True)
        self.constraints = constraints or OptimizationConstraints()
        
        # Create tier lookup for quick access
        self.tier_lookup = {tier.name: tier for tier in self.hs_tiers}
        self.hs_to_tier = self._build_hs_to_tier_mapping()
        
        # Optimization state
        self.optimization_history = []
        self.best_strategy = None
        self.best_performance = float('-inf')
        
        # Search space definition
        self.search_space = self._define_search_space()
        
    def _build_hs_to_tier_mapping(self) -> Dict[int, str]:
        """Build mapping from HS values to tier names."""
        mapping = {}
        for tier in self.hs_tiers:
            for hs in range(tier.min_hs, tier.max_hs + 1):
                mapping[hs] = tier.name
        return mapping
    
    def _define_search_space(self) -> Dict:
        """Define the search space for optimization."""
        # Extract tier boundaries for search space
        tier_boundaries = sorted(set([tier.min_hs for tier in self.hs_tiers] + 
                                   [tier.max_hs for tier in self.hs_tiers]))
        
        search_space = {
            'preflop': {
                'open_thresholds': {
                    'bounds': (tier_boundaries[0], tier_boundaries[-1]),
                    'positions': ['UTG', 'MP', 'CO', 'BTN', 'SB']
                },
                'vs_raise_thresholds': {
                    'value_bounds': (tier_boundaries[-3], tier_boundaries[-1]),
                    'call_bounds': (tier_boundaries[0], tier_boundaries[-2]),
                    'positions': ['UTG', 'MP', 'CO', 'BTN']
                }
            },
            'postflop': {
                'pfa_thresholds': {
                    'value_bounds': (10, 80),
                    'check_bounds': (5, 40),
                    'streets': ['flop', 'turn', 'river'],
                    'positions': ['UTG', 'MP', 'CO', 'BTN']
                },
                'caller_thresholds': {
                    'raise_bounds': (30, 90),
                    'call_bounds': (15, 60),
                    'bet_types': ['small_bet', 'medium_bet', 'large_bet']
                }
            }
        }
        
        return search_space
    
    def optimize_strategy(self, base_strategy_file: str, 
                         optimization_method: str = 'bayesian',
                         max_evaluations: int = 100) -> OptimizationResult:
        """
        Main optimization function that finds optimal decision tables.
        
        Args:
            base_strategy_file: Starting strategy file
            optimization_method: 'bayesian', 'genetic', or 'grid'
            max_evaluations: Maximum strategy evaluations
        """
        
        print("🎯 HUMAN-EXECUTABLE STRATEGY OPTIMIZATION")
        print("=" * 60)
        print(f"Method: {optimization_method.upper()}")
        print(f"HS Tiers: {len(self.hs_tiers)} tiers defined")
        print(f"Max Evaluations: {max_evaluations}")
        print(f"Execution Constraints: {self.constraints}")
        
        # Load base strategy
        with open(base_strategy_file, 'r') as f:
            self.base_strategy = json.load(f)
        
        # Validate HS table matches tiers
        self._validate_hs_tier_consistency()
        
        # Choose optimization method
        if optimization_method == 'bayesian':
            result = self._bayesian_optimization(max_evaluations)
        elif optimization_method == 'genetic':
            result = self._genetic_optimization(max_evaluations)
        elif optimization_method == 'grid':
            result = self._grid_search_optimization(max_evaluations)
        else:
            raise ValueError(f"Unknown optimization method: {optimization_method}")
        
        # Analyze final result
        final_analysis = self._analyze_final_result(result)
        
        return final_analysis
    
    def _validate_hs_tier_consistency(self):
        """Validate that HS table is consistent with defined tiers."""
        preflop_hs = self.base_strategy['hand_strength_tables']['preflop']
        
        tier_hands = defaultdict(list)
        for hand, hs in preflop_hs.items():
            if hs in self.hs_to_tier:
                tier_name = self.hs_to_tier[hs]
                tier_hands[tier_name].append(hand)
        
        print(f"\n📊 HS TIER VALIDATION:")
        for tier in self.hs_tiers:
            actual_hands = len(tier_hands.get(tier.name, []))
            expected_hands = len(tier.hands) if hasattr(tier, 'hands') and tier.hands else 'Variable'
            print(f"   {tier.name}: {actual_hands} hands (HS {tier.min_hs}-{tier.max_hs})")
        
        print(f"✅ Tier validation complete")
    
    def _bayesian_optimization(self, max_evaluations: int) -> OptimizationResult:
        """Bayesian optimization using Gaussian Process for efficient search."""
        
        print(f"\n🧠 Starting Bayesian Optimization...")
        
        # Define parameter vector and bounds
        param_names, bounds = self._create_parameter_vector()
        
        # Gaussian Process for modeling objective function
        kernel = Matern(length_scale=1.0, nu=2.5)
        gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-6, normalize_y=True)
        
        # Initial random samples
        n_initial = min(10, max_evaluations // 4)
        X_samples = []
        y_samples = []
        
        print(f"   🎲 Generating {n_initial} initial samples...")
        
        for i in range(n_initial):
            # Random parameter vector
            x = [random.uniform(bound[0], bound[1]) for bound in bounds]
            
            # Evaluate strategy
            performance = self._evaluate_parameter_vector(x, param_names)
            
            X_samples.append(x)
            y_samples.append(performance)
            
            print(f"      Sample {i+1}: Performance = {performance:.2f} bb/100")
        
        # Fit initial GP
        X_samples = np.array(X_samples)
        y_samples = np.array(y_samples)
        gp.fit(X_samples, y_samples)
        
        # Iterative optimization
        for iteration in range(n_initial, max_evaluations):
            print(f"   🔍 Iteration {iteration + 1}/{max_evaluations}")
            
            # Acquisition function: Upper Confidence Bound
            def acquisition(x):
                x = np.array(x).reshape(1, -1)
                mean, std = gp.predict(x, return_std=True)
                return -(mean + 2.0 * std)  # Negative for minimization
            
            # Optimize acquisition function
            result = differential_evolution(
                acquisition, bounds, maxiter=50, seed=42
            )
            
            next_x = result.x
            
            # Evaluate new point
            performance = self._evaluate_parameter_vector(next_x, param_names)
            
            # Update GP
            X_samples = np.vstack([X_samples, next_x])
            y_samples = np.append(y_samples, performance)
            gp.fit(X_samples, y_samples)
            
            # Track best
            if performance > self.best_performance:
                self.best_performance = performance
                self.best_strategy = self._vector_to_strategy(next_x, param_names)
                print(f"      🎉 New best: {performance:.2f} bb/100")
            else:
                print(f"      Performance: {performance:.2f} bb/100")
        
        return self._create_optimization_result()
    
    def _genetic_optimization(self, max_evaluations: int) -> OptimizationResult:
        """Genetic algorithm optimization for discrete parameter spaces."""
        
        print(f"\n🧬 Starting Genetic Algorithm Optimization...")
        
        param_names, bounds = self._create_parameter_vector()
        
        def objective_function(x):
            return -self._evaluate_parameter_vector(x, param_names)  # Minimize negative
        
        # Run differential evolution (a type of genetic algorithm)
        result = differential_evolution(
            objective_function, 
            bounds, 
            maxiter=max_evaluations // 10,
            popsize=10,
            seed=42,
            callback=self._optimization_callback
        )
        
        # Extract best strategy
        best_x = result.x
        self.best_performance = -result.fun
        self.best_strategy = self._vector_to_strategy(best_x, param_names)
        
        print(f"✅ Genetic optimization complete: {self.best_performance:.2f} bb/100")
        
        return self._create_optimization_result()
    
    def _grid_search_optimization(self, max_evaluations: int) -> OptimizationResult:
        """Grid search optimization for systematic exploration."""
        
        print(f"\n🔲 Starting Grid Search Optimization...")
        
        param_names, bounds = self._create_parameter_vector()
        
        # Create grid based on tier boundaries
        grid_points = []
        tier_boundaries = sorted([tier.min_hs for tier in self.hs_tiers] + 
                                [tier.max_hs for tier in self.hs_tiers])
        
        # Limit grid size to max_evaluations
        grid_size_per_dim = max(2, int(max_evaluations ** (1.0 / len(bounds))))
        
        for i, (param_name, (low, high)) in enumerate(zip(param_names, bounds)):
            # Use tier boundaries where applicable
            if 'threshold' in param_name:
                relevant_boundaries = [b for b in tier_boundaries if low <= b <= high]
                if len(relevant_boundaries) >= 2:
                    grid_points.append(relevant_boundaries[:grid_size_per_dim])
                else:
                    grid_points.append(np.linspace(low, high, grid_size_per_dim))
            else:
                grid_points.append(np.linspace(low, high, grid_size_per_dim))
        
        # Generate all combinations
        all_combinations = list(itertools.product(*grid_points))
        
        # Limit to max_evaluations
        if len(all_combinations) > max_evaluations:
            selected_combinations = random.sample(all_combinations, max_evaluations)
        else:
            selected_combinations = all_combinations
        
        print(f"   🎯 Evaluating {len(selected_combinations)} grid points...")
        
        # Evaluate each combination
        for i, combination in enumerate(selected_combinations):
            performance = self._evaluate_parameter_vector(combination, param_names)
            
            if performance > self.best_performance:
                self.best_performance = performance
                self.best_strategy = self._vector_to_strategy(combination, param_names)
                print(f"   #{i+1}: New best = {performance:.2f} bb/100")
            elif i % (len(selected_combinations) // 10) == 0:
                print(f"   #{i+1}: {performance:.2f} bb/100")
        
        print(f"✅ Grid search complete: {self.best_performance:.2f} bb/100")
        
        return self._create_optimization_result()
    
    def _create_parameter_vector(self) -> Tuple[List[str], List[Tuple[float, float]]]:
        """Create parameter vector and bounds for optimization."""
        
        param_names = []
        bounds = []
        
        # Preflop opening thresholds (by position)
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB']
        for pos in positions:
            param_names.append(f'preflop_open_{pos}')
            bounds.append((5, 50))  # HS range for opening
        
        # Preflop vs raise thresholds (value 3-bet and call ranges)
        for pos in ['UTG', 'MP', 'CO', 'BTN']:
            param_names.append(f'preflop_3bet_{pos}')
            bounds.append((20, 50))  # Value 3-bet threshold
            
            param_names.append(f'preflop_call_low_{pos}')
            bounds.append((5, 30))   # Call range lower bound
            
            param_names.append(f'preflop_call_high_{pos}')
            bounds.append((15, 40))  # Call range upper bound
        
        # Postflop PFA thresholds
        streets = ['flop', 'turn', 'river']
        for street in streets:
            for pos in ['UTG', 'MP', 'CO', 'BTN']:
                param_names.append(f'{street}_pfa_value_{pos}')
                bounds.append((15, 80))  # Value bet threshold
                
                param_names.append(f'{street}_pfa_check_{pos}')
                bounds.append((5, 40))   # Check threshold
        
        # Postflop caller thresholds (simplified)
        bet_types = ['small_bet', 'medium_bet', 'large_bet']
        for bet_type in bet_types:
            param_names.append(f'caller_{bet_type}_raise')
            bounds.append((30, 90))  # Raise threshold
            
            param_names.append(f'caller_{bet_type}_call')
            bounds.append((10, 60))  # Call threshold
        
        return param_names, bounds
    
    def _evaluate_parameter_vector(self, param_vector: List[float], 
                                  param_names: List[str]) -> float:
        """Evaluate a parameter vector by converting to strategy and simulating."""
        
        # Convert parameter vector to strategy
        strategy = self._vector_to_strategy(param_vector, param_names)
        
        # Check human executability constraints
        complexity_penalty = self._calculate_complexity_penalty(strategy)
        
        # Save strategy to temporary file
        temp_filename = f"temp_strategy_{random.randint(1000, 9999)}.json"
        with open(temp_filename, 'w') as f:
            json.dump(strategy, f, indent=2)
        
        try:
            # Quick simulation for evaluation
            config = {
                'hands_per_run': 5000,  # Smaller for speed
                'num_runs': 2,
                'use_multiprocessing': False,  # Avoid overhead
                'track_detailed_logs': False
            }
            
            # Compare against baseline
            baseline_strategy = 'baseline_strategy.json'  # Should exist
            engine = EnhancedSimulationEngine([baseline_strategy, temp_filename], config)
            results = engine.run_comprehensive_analysis()
            
            # Extract performance
            strategy_results = results['strategy_results']
            temp_result = None
            
            for strategy_name, result in strategy_results.items():
                if temp_filename in strategy_name:
                    temp_result = result
                    break
            
            if temp_result:
                base_performance = temp_result.win_rate_bb100
                
                # Apply complexity penalty
                final_performance = base_performance - complexity_penalty
                
                # Track in optimization history
                self.optimization_history.append({
                    'parameters': dict(zip(param_names, param_vector)),
                    'base_performance': base_performance,
                    'complexity_penalty': complexity_penalty,
                    'final_performance': final_performance,
                    'tier_usage': self._analyze_tier_usage(strategy)
                })
                
                return final_performance
            else:
                return -100.0  # Large penalty for failed evaluation
                
        except Exception as e:
            print(f"   ⚠️ Evaluation failed: {e}")
            return -100.0  # Large penalty for errors
            
        finally:
            # Clean up temp file
            try:
                import os
                os.remove(temp_filename)
            except:
                pass
    
    def _vector_to_strategy(self, param_vector: List[float], 
                           param_names: List[str]) -> Dict:
        """Convert parameter vector back to strategy dictionary."""
        
        strategy = copy.deepcopy(self.base_strategy)
        params = dict(zip(param_names, param_vector))
        
        # Apply preflop opening thresholds
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB']
        for pos in positions:
            if f'preflop_open_{pos}' in params:
                threshold = max(1, int(params[f'preflop_open_{pos}']))
                if pos in strategy['preflop']['open_rules']:
                    strategy['preflop']['open_rules'][pos]['threshold'] = threshold
        
        # Apply preflop vs raise thresholds
        for pos in ['UTG', 'MP', 'CO', 'BTN']:
            for ip_oop in ['IP', 'OOP']:
                if pos in strategy['preflop']['vs_raise'] and ip_oop in strategy['preflop']['vs_raise'][pos]:
                    # Value 3-bet threshold
                    if f'preflop_3bet_{pos}' in params:
                        value_thresh = max(1, int(params[f'preflop_3bet_{pos}']))
                        strategy['preflop']['vs_raise'][pos][ip_oop]['value_thresh'] = value_thresh
                    
                    # Call range
                    if f'preflop_call_low_{pos}' in params and f'preflop_call_high_{pos}' in params:
                        call_low = max(1, int(params[f'preflop_call_low_{pos}']))
                        call_high = max(call_low + 1, int(params[f'preflop_call_high_{pos}']))
                        strategy['preflop']['vs_raise'][pos][ip_oop]['call_range'] = [call_low, call_high]
        
        # Apply postflop PFA thresholds
        streets = ['flop', 'turn', 'river']
        for street in streets:
            for pos in ['UTG', 'MP', 'CO', 'BTN']:
                for ip_oop in ['IP', 'OOP']:
                    if (street in strategy['postflop']['pfa'] and 
                        pos in strategy['postflop']['pfa'][street] and
                        ip_oop in strategy['postflop']['pfa'][street][pos]):
                        
                        # Value bet threshold
                        if f'{street}_pfa_value_{pos}' in params:
                            val_thresh = max(1, int(params[f'{street}_pfa_value_{pos}']))
                            strategy['postflop']['pfa'][street][pos][ip_oop]['val_thresh'] = val_thresh
                        
                        # Check threshold
                        if f'{street}_pfa_check_{pos}' in params:
                            check_thresh = max(1, int(params[f'{street}_pfa_check_{pos}']))
                            strategy['postflop']['pfa'][street][pos][ip_oop]['check_thresh'] = check_thresh
        
        # Apply postflop caller thresholds
        bet_types = ['small_bet', 'medium_bet', 'large_bet']
        for street in streets:
            for pos in ['UTG', 'MP', 'CO', 'BTN']:
                for ip_oop in ['IP', 'OOP']:
                    if (street in strategy['postflop']['caller'] and 
                        pos in strategy['postflop']['caller'][street] and
                        ip_oop in strategy['postflop']['caller'][street][pos]):
                        
                        for bet_type in bet_types:
                            if (f'caller_{bet_type}_raise' in params and 
                                f'caller_{bet_type}_call' in params):
                                
                                raise_thresh = max(1, int(params[f'caller_{bet_type}_raise']))
                                call_thresh = max(1, int(params[f'caller_{bet_type}_call']))
                                
                                if bet_type in strategy['postflop']['caller'][street][pos][ip_oop]:
                                    strategy['postflop']['caller'][street][pos][ip_oop][bet_type] = [
                                        raise_thresh, call_thresh
                                    ]
        
        return strategy
    
    def _calculate_complexity_penalty(self, strategy: Dict) -> float:
        """Calculate penalty for strategy complexity that hurts human execution."""
        
        penalty = 0.0
        
        # Count unique thresholds across decision tables
        all_thresholds = set()
        
        # Preflop thresholds
        for pos, rule in strategy['preflop']['open_rules'].items():
            all_thresholds.add(rule['threshold'])
        
        for pos, pos_rules in strategy['preflop']['vs_raise'].items():
            for ip_oop, rule in pos_rules.items():
                all_thresholds.add(rule['value_thresh'])
                all_thresholds.add(rule['call_range'][0])
                all_thresholds.add(rule['call_range'][1])
        
        # Postflop thresholds
        for street, street_rules in strategy['postflop']['pfa'].items():
            for pos, pos_rules in street_rules.items():
                for ip_oop, rule in pos_rules.items():
                    all_thresholds.add(rule['val_thresh'])
                    all_thresholds.add(rule['check_thresh'])
        
        # Penalty for too many unique thresholds
        if len(all_thresholds) > self.constraints.max_threshold_complexity * 5:
            penalty += (len(all_thresholds) - self.constraints.max_threshold_complexity * 5) * 0.5
        
        # Penalty for non-tier-aligned thresholds
        tier_boundaries = set([tier.min_hs for tier in self.hs_tiers] + 
                             [tier.max_hs for tier in self.hs_tiers])
        
        misaligned_thresholds = all_thresholds - tier_boundaries
        penalty += len(misaligned_thresholds) * 0.2
        
        # Penalty for non-monotonic position adjustments (if required)
        if self.constraints.require_monotonic_thresholds:
            position_order = ['UTG', 'MP', 'CO', 'BTN']
            
            # Check preflop opening thresholds
            open_thresholds = []
            for pos in position_order:
                if pos in strategy['preflop']['open_rules']:
                    open_thresholds.append(strategy['preflop']['open_rules'][pos]['threshold'])
            
            # Should be decreasing (looser in later position)
            for i in range(len(open_thresholds) - 1):
                if open_thresholds[i] < open_thresholds[i + 1]:
                    penalty += 1.0  # Violation of position logic
        
        return penalty
    
    def _analyze_tier_usage(self, strategy: Dict) -> Dict:
        """Analyze how the strategy uses the defined tiers."""
        
        tier_usage = defaultdict(int)
        
        # Count threshold appearances by tier
        for tier in self.hs_tiers:
            tier_boundaries = set(range(tier.min_hs, tier.max_hs + 1))
            
            # Check all thresholds in strategy
            all_thresholds = self._extract_all_thresholds(strategy)
            
            for threshold in all_thresholds:
                if threshold in tier_boundaries:
                    tier_usage[tier.name] += 1
        
        return dict(tier_usage)
    
    def _extract_all_thresholds(self, strategy: Dict) -> List[int]:
        """Extract all threshold values from strategy."""
        
        thresholds = []
        
        # Preflop
        for pos, rule in strategy['preflop']['open_rules'].items():
            thresholds.append(rule['threshold'])
        
        for pos, pos_rules in strategy['preflop']['vs_raise'].items():
            for ip_oop, rule in pos_rules.items():
                thresholds.append(rule['value_thresh'])
                thresholds.extend(rule['call_range'])
        
        # Postflop
        for street, street_rules in strategy['postflop']['pfa'].items():
            for pos, pos_rules in street_rules.items():
                for ip_oop, rule in pos_rules.items():
                    thresholds.append(rule['val_thresh'])
                    thresholds.append(rule['check_thresh'])
        
        for street, street_rules in strategy['postflop']['caller'].items():
            for pos, pos_rules in street_rules.items():
                for ip_oop, rule in pos_rules.items():
                    for bet_type, thresholds_pair in rule.items():
                        if isinstance(thresholds_pair, list) and len(thresholds_pair) == 2:
                            thresholds.extend(thresholds_pair)
        
        return thresholds
    
    def _optimization_callback(self, x, convergence):
        """Callback function for optimization progress."""
        current_performance = -self._evaluate_parameter_vector(x, self._create_parameter_vector()[0])
        
        if len(self.optimization_history) % 10 == 0:
            print(f"   Iteration {len(self.optimization_history)}: {current_performance:.2f} bb/100")
    
    def _create_optimization_result(self) -> OptimizationResult:
        """Create comprehensive optimization result."""
        
        # Calculate execution complexity metrics
        execution_complexity = self._analyze_execution_complexity(self.best_strategy)
        
        # Calculate tier usage analysis
        tier_usage = self._analyze_tier_usage(self.best_strategy)
        
        # Calculate human readability score
        readability_score = self._calculate_readability_score(self.best_strategy)
        
        # Performance metrics
        performance_metrics = {
            'final_win_rate': self.best_performance,
            'improvement_over_baseline': self.best_performance,  # vs baseline
            'convergence_rate': len(self.optimization_history),
            'stability_score': self._calculate_stability_score()
        }
        
        return OptimizationResult(
            optimized_strategy=self.best_strategy,
            performance_metrics=performance_metrics,
            execution_complexity=execution_complexity,
            tier_usage_analysis=tier_usage,
            human_readability_score=readability_score,
            optimization_history=self.optimization_history
        )
    
    def _analyze_execution_complexity(self, strategy: Dict) -> Dict:
        """Analyze how complex the strategy is to execute."""
        
        all_thresholds = self._extract_all_thresholds(strategy)
        unique_thresholds = len(set(all_thresholds))
        
        # Count decision points
        decision_points = 0
        decision_points += len(strategy['preflop']['open_rules'])
        
        for pos_rules in strategy['preflop']['vs_raise'].values():
            decision_points += len(pos_rules) * 2  # value_thresh + call_range
        
        for street_rules in strategy['postflop']['pfa'].values():
            for pos_rules in street_rules.values():
                decision_points += len(pos_rules) * 2  # val_thresh + check_thresh
        
        # Tier alignment score
        tier_boundaries = set([tier.min_hs for tier in self.hs_tiers] + 
                             [tier.max_hs for tier in self.hs_tiers])
        aligned_thresholds = len(set(all_thresholds) & tier_boundaries)
        alignment_score = aligned_thresholds / max(len(set(all_thresholds)), 1)
        
        return {
            'unique_thresholds': unique_thresholds,
            'decision_points': decision_points,
            'tier_alignment_score': alignment_score,
            'complexity_rating': self._rate_complexity(unique_thresholds, decision_points),
            'estimated_learning_time_hours': unique_thresholds * 0.5 + decision_points * 0.2
        }
    
    def _rate_complexity(self, unique_thresholds: int, decision_points: int) -> str:
        """Rate strategy complexity for human execution."""
        
        complexity_score = unique_thresholds * 0.3 + decision_points * 0.1
        
        if complexity_score <= 10:
            return "EASY"
        elif complexity_score <= 20:
            return "MODERATE"
        elif complexity_score <= 35:
            return "COMPLEX"
        else:
            return "VERY_COMPLEX"
    
    def _calculate_readability_score(self, strategy: Dict) -> float:
        """Calculate how readable/memorable the strategy is."""
        
        # Base score
        score = 100.0
        
        # Penalty for too many unique thresholds
        unique_thresholds = len(set(self._extract_all_thresholds(strategy)))
        if unique_thresholds > 15:
            score -= (unique_thresholds - 15) * 2
        
        # Bonus for tier alignment
        tier_boundaries = set([tier.min_hs for tier in self.hs_tiers] + 
                             [tier.max_hs for tier in self.hs_tiers])
        all_thresholds = set(self._extract_all_thresholds(strategy))
        aligned_count = len(all_thresholds & tier_boundaries)
        alignment_ratio = aligned_count / max(len(all_thresholds), 1)
        score += alignment_ratio * 20
        
        # Bonus for logical position progressions
        position_logic_bonus = self._check_position_logic(strategy)
        score += position_logic_bonus
        
        return max(0.0, min(100.0, score))
    
    def _check_position_logic(self, strategy: Dict) -> float:
        """Check if strategy follows logical position-based progressions."""
        
        bonus = 0.0
        position_order = ['UTG', 'MP', 'CO', 'BTN']
        
        # Check preflop opening ranges (should get looser in later position)
        open_thresholds = []
        for pos in position_order:
            if pos in strategy['preflop']['open_rules']:
                open_thresholds.append(strategy['preflop']['open_rules'][pos]['threshold'])
        
        # Count monotonic decreases (looser = lower threshold)
        monotonic_decreases = 0
        for i in range(len(open_thresholds) - 1):
            if open_thresholds[i] >= open_thresholds[i + 1]:
                monotonic_decreases += 1
        
        if len(open_thresholds) > 1:
            bonus += (monotonic_decreases / (len(open_thresholds) - 1)) * 10
        
        return bonus
    
    def _calculate_stability_score(self) -> float:
        """Calculate how stable the optimization process was."""
        
        if len(self.optimization_history) < 5:
            return 0.5
        
        # Look at final 25% of optimization
        recent_history = self.optimization_history[-len(self.optimization_history)//4:]
        recent_performances = [h['final_performance'] for h in recent_history]
        
        # Calculate coefficient of variation (lower = more stable)
        if len(recent_performances) > 1:
            mean_perf = np.mean(recent_performances)
            std_perf = np.std(recent_performances)
            cv = std_perf / abs(mean_perf) if mean_perf != 0 else 1.0
            
            # Convert to 0-1 stability score (lower CV = higher stability)
            stability = max(0.0, 1.0 - cv)
        else:
            stability = 0.5
        
        return stability
    
    def generate_human_readable_guide(self, result: OptimizationResult, 
                                     output_file: str = "optimized_strategy_guide.md"):
        """Generate human-readable strategy guide for the optimized strategy."""
        
        strategy = result.optimized_strategy
        
        guide_content = f"""# Optimized Human-Executable Strategy Guide

## Performance Summary
- **Win Rate**: {result.performance_metrics['final_win_rate']:+.2f} bb/100
- **Readability Score**: {result.human_readability_score:.1f}/100
- **Complexity Rating**: {result.execution_complexity['complexity_rating']}
- **Learning Time**: ~{result.execution_complexity['estimated_learning_time_hours']:.1f} hours

## Hand Strength Tiers (Memorize These!)

"""
        
        # Add tier information
        for tier in self.hs_tiers:
            guide_content += f"### {tier.name} (HS {tier.min_hs}-{tier.max_hs})\n"
            if hasattr(tier, 'description'):
                guide_content += f"{tier.description}\n"
            if hasattr(tier, 'hands') and tier.hands:
                guide_content += f"**Example Hands**: {', '.join(tier.hands[:10])}\n"
            guide_content += "\n"
        
        # Add simplified decision tables
        guide_content += """## Preflop Decision Tables

### Opening Ranges by Position
| Position | Minimum HS | Tier | Example Action |
|----------|------------|------|----------------|
"""
        
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB']
        for pos in positions:
            if pos in strategy['preflop']['open_rules']:
                threshold = strategy['preflop']['open_rules'][pos]['threshold']
                tier_name = self._hs_to_tier_name(threshold)
                guide_content += f"| {pos} | {threshold}+ | {tier_name}+ | Raise {threshold}+ |\\n"
        
        guide_content += """
### Facing Raises (3-Bet or Call)
| Position | 3-Bet HS | Call Range | Action Guide |
|----------|----------|------------|--------------|
"""
        
        for pos in ['UTG', 'MP', 'CO', 'BTN']:
            if pos in strategy['preflop']['vs_raise']:
                rule = strategy['preflop']['vs_raise'][pos]['IP']  # Use IP for simplicity
                value_thresh = rule['value_thresh']
                call_range = rule['call_range']
                
                value_tier = self._hs_to_tier_name(value_thresh)
                call_tier_low = self._hs_to_tier_name(call_range[0])
                call_tier_high = self._hs_to_tier_name(call_range[1])
                
                guide_content += f"| {pos} | {value_thresh}+ ({value_tier}+) | {call_range[0]}-{call_range[1]} ({call_tier_low} to {call_tier_high}) | 3-bet {value_thresh}+, Call {call_range[0]}-{call_range[1]} |\\n"
        
        # Add postflop guidelines
        guide_content += """
## Postflop Guidelines

### As Preflop Aggressor (C-betting)
**Simple Rule**: Bet when you have a strong hand or good bluff, check when marginal.

### Facing Bets
**Simple Rule**: 
- **Small bets**: Call with decent hands, raise with very strong hands
- **Large bets**: Only continue with strong hands
- **When in doubt**: Use your tier system - higher tiers = more aggressive

## Execution Tips

1. **Memorize the tier boundaries** - this is your foundation
2. **Practice position-based adjustments** - tighter early, looser late
3. **Use the "tier plus" system** - e.g., "Tier 3+" is easier than "HS 20+"
4. **Start conservative** - better to be too tight than too loose while learning
5. **Focus on preflop first** - get this automatic before working on postflop

## Quick Reference Card

**Tier Boundaries**: {', '.join([f"{tier.name}:{tier.min_hs}-{tier.max_hs}" for tier in self.hs_tiers])}

**Position Opening**: UTG:{strategy['preflop']['open_rules'].get('UTG', {}).get('threshold', 'N/A')}+ | CO:{strategy['preflop']['open_rules'].get('CO', {}).get('threshold', 'N/A')}+ | BTN:{strategy['preflop']['open_rules'].get('BTN', {}).get('threshold', 'N/A')}+

---
*Generated by Human-Executable Strategy Optimizer*
"""
        
        # Save guide
        with open(output_file, 'w') as f:
            f.write(guide_content)
        
        print(f"📖 Human-readable guide saved to: {output_file}")
    
    def _hs_to_tier_name(self, hs_value: int) -> str:
        """Convert HS value to tier name."""
        for tier in self.hs_tiers:
            if tier.min_hs <= hs_value <= tier.max_hs:
                return tier.name
        return f"HS{hs_value}"

# =============================================================================
# Usage Example and Utility Functions
# =============================================================================

def create_example_hs_tiers() -> List[HSTier]:
    """Create example HS tiers for demonstration."""
    
    return [
        HSTier(
            name="Elite",
            min_hs=40,
            max_hs=50,
            hands=["AA", "KK", "QQ", "AKs"],
            description="Premium hands - always play aggressively",
            color_code="#FF0000"
        ),
        HSTier(
            name="Premium", 
            min_hs=30,
            max_hs=39,
            hands=["JJ", "AKo", "AQs", "AJs"],
            description="Strong hands - open most positions",
            color_code="#FF8800"
        ),
        HSTier(
            name="Gold",
            min_hs=20,
            max_hs=29,
            hands=["TT", "99", "88", "AQo", "KQs"],
            description="Good hands - position dependent",
            color_code="#FFD700"
        ),
        HSTier(
            name="Silver",
            min_hs=10,
            max_hs=19,
            hands=["77", "66", "AJo", "KJs", "QJs"],
            description="Marginal hands - late position only",
            color_code="#C0C0C0"
        ),
        HSTier(
            name="Bronze",
            min_hs=1,
            max_hs=9,
            hands=["55", "44", "33", "22", "A9s"],
            description="Weak hands - button/blinds only",
            color_code="#CD7F32"
        )
    ]

def main():
    """Example usage of the Human-Executable Strategy Optimizer."""
    
    print("🎯 HUMAN-EXECUTABLE STRATEGY OPTIMIZER")
    print("=" * 60)
    
    # Create example HS tiers
    hs_tiers = create_example_hs_tiers()
    
    # Set optimization constraints
    constraints = OptimizationConstraints(
        max_tiers_per_decision=3,
        max_threshold_complexity=4,
        require_monotonic_thresholds=True,
        allow_tier_splitting=False,
        execution_time_limit=3.0
    )
    
    # Initialize optimizer
    optimizer = HumanExecutableOptimizer(hs_tiers, constraints)
    
    # Run optimization
    result = optimizer.optimize_strategy(
        base_strategy_file='baseline_strategy.json',
        optimization_method='bayesian',
        max_evaluations=50
    )
    
    # Generate human-readable guide
    optimizer.generate_human_readable_guide(result)
    
    # Print summary
    print(f"\n✅ OPTIMIZATION COMPLETE!")
    print(f"   Final Performance: {result.performance_metrics['final_win_rate']:+.2f} bb/100")
    print(f"   Readability Score: {result.human_readability_score:.1f}/100")
    print(f"   Complexity: {result.execution_complexity['complexity_rating']}")
    print(f"   Estimated Learning Time: {result.execution_complexity['estimated_learning_time_hours']:.1f} hours")

if __name__ == '__main__':
    main()