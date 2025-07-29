# filename: simplified_optimizer_interface.py
"""
Simplified Interface for Human-Executable Strategy Optimization

This provides an easy-to-use interface for optimizing poker strategies
while maintaining human memorability through HS tiers.

Usage:
1. Define your HS tiers (which hands belong to which strength groups)
2. Set your constraints (how complex you want the strategy to be)
3. Run optimization to find best decision tables
4. Get human-readable strategy guide
"""

import json
import os
from typing import List, Dict, Optional
from human_executable_optimizer import (
    HumanExecutableOptimizer, HSTier, OptimizationConstraints
)

class StrategyOptimizerInterface:
    """Simplified interface for strategy optimization."""
    
    def __init__(self):
        self.hs_tiers = []
        self.constraints = None
        self.optimizer = None
        
    def define_hs_tiers_from_strategy(self, strategy_file: str, 
                                    tier_config: Dict[str, Dict]) -> List[HSTier]:
        """
        Automatically create HS tiers from existing strategy file.
        
        Args:
            strategy_file: Path to strategy.json file
            tier_config: Dictionary defining tier names and HS ranges
                        Example: {
                            "Elite": {"min_hs": 40, "max_hs": 50},
                            "Premium": {"min_hs": 30, "max_hs": 39},
                            ...
                        }
        """
        
        print("📊 Analyzing strategy file to create HS tiers...")
        
        # Load strategy
        with open(strategy_file, 'r') as f:
            strategy = json.load(f)
        
        preflop_hs = strategy['hand_strength_tables']['preflop']
        
        # Create tiers based on config
        tiers = []
        for tier_name, tier_info in tier_config.items():
            min_hs = tier_info['min_hs']
            max_hs = tier_info['max_hs']
            
            # Find hands in this HS range
            tier_hands = []
            for hand, hs in preflop_hs.items():
                if min_hs <= hs <= max_hs:
                    tier_hands.append(hand)
            
            # Sort hands by strength (descending)
            tier_hands.sort(key=lambda h: preflop_hs[h], reverse=True)
            
            tier = HSTier(
                name=tier_name,
                min_hs=min_hs,
                max_hs=max_hs,
                hands=tier_hands,
                description=self._generate_tier_description(tier_name, len(tier_hands)),
                color_code=self._get_tier_color(tier_name)
            )
            tiers.append(tier)
        
        self.hs_tiers = tiers
        
        print(f"✅ Created {len(tiers)} HS tiers:")
        for tier in tiers:
            print(f"   {tier.name}: {len(tier.hands)} hands (HS {tier.min_hs}-{tier.max_hs})")
        
        return tiers
    
    def set_simple_constraints(self, complexity_level: str = "moderate"):
        """
        Set optimization constraints using simple complexity levels.
        
        Args:
            complexity_level: "simple", "moderate", or "complex"
        """
        
        if complexity_level == "simple":
            self.constraints = OptimizationConstraints(
                max_tiers_per_decision=2,
                max_threshold_complexity=3,
                require_monotonic_thresholds=True,
                allow_tier_splitting=False,
                execution_time_limit=2.0
            )
            print("📝 Set SIMPLE constraints (easiest to learn)")
            
        elif complexity_level == "moderate":
            self.constraints = OptimizationConstraints(
                max_tiers_per_decision=3,
                max_threshold_complexity=4,
                require_monotonic_thresholds=True,
                allow_tier_splitting=False,
                execution_time_limit=3.0
            )
            print("📝 Set MODERATE constraints (balanced complexity)")
            
        elif complexity_level == "complex":
            self.constraints = OptimizationConstraints(
                max_tiers_per_decision=4,
                max_threshold_complexity=6,
                require_monotonic_thresholds=False,
                allow_tier_splitting=True,
                execution_time_limit=5.0
            )
            print("📝 Set COMPLEX constraints (maximum performance)")
            
        else:
            raise ValueError("complexity_level must be 'simple', 'moderate', or 'complex'")
    
    def optimize_strategy(self, base_strategy_file: str, 
                         method: str = "quick",
                         output_prefix: str = "optimized") -> Dict:
        """
        Run strategy optimization with simple interface.
        
        Args:
            base_strategy_file: Starting strategy file
            method: "quick" (20 evaluations), "standard" (50), or "thorough" (100)
            output_prefix: Prefix for output files
        """
        
        if not self.hs_tiers:
            raise ValueError("Must define HS tiers first using define_hs_tiers_from_strategy()")
        
        if not self.constraints:
            print("⚠️ No constraints set, using 'moderate' complexity")
            self.set_simple_constraints("moderate")
        
        # Set evaluation count based on method
        if method == "quick":
            max_evaluations = 20
            opt_method = "grid"
        elif method == "standard":
            max_evaluations = 50
            opt_method = "bayesian"
        elif method == "thorough":
            max_evaluations = 100
            opt_method = "bayesian"
        else:
            raise ValueError("method must be 'quick', 'standard', or 'thorough'")
        
        print(f"🚀 Starting {method.upper()} optimization ({max_evaluations} evaluations)...")
        
        # Initialize optimizer
        self.optimizer = HumanExecutableOptimizer(self.hs_tiers, self.constraints)
        
        # Run optimization
        result = self.optimizer.optimize_strategy(
            base_strategy_file=base_strategy_file,
            optimization_method=opt_method,
            max_evaluations=max_evaluations
        )
        
        # Save optimized strategy
        strategy_filename = f"{output_prefix}_strategy.json"
        with open(strategy_filename, 'w') as f:
            json.dump(result.optimized_strategy, f, indent=2)
        
        # Generate human-readable guide
        guide_filename = f"{output_prefix}_guide.md"
        self.optimizer.generate_human_readable_guide(result, guide_filename)
        
        # Create summary report
        summary = self._create_summary_report(result, strategy_filename, guide_filename)
        
        return summary
    
    def _generate_tier_description(self, tier_name: str, hand_count: int) -> str:
        """Generate description for a tier."""
        descriptions = {
            "Elite": f"Premium hands ({hand_count} hands) - Always play aggressively",
            "Premium": f"Strong hands ({hand_count} hands) - Open most positions",
            "Gold": f"Good hands ({hand_count} hands) - Position dependent",
            "Silver": f"Marginal hands ({hand_count} hands) - Late position preferred",
            "Bronze": f"Weak hands ({hand_count} hands) - Button/blinds only"
        }
        
        return descriptions.get(tier_name, f"{tier_name} tier with {hand_count} hands")
    
    def _get_tier_color(self, tier_name: str) -> str:
        """Get color code for tier visualization."""
        colors = {
            "Elite": "#FF0000",      # Red
            "Premium": "#FF8800",    # Orange
            "Gold": "#FFD700",       # Gold
            "Silver": "#C0C0C0",     # Silver
            "Bronze": "#CD7F32"      # Bronze
        }
        
        return colors.get(tier_name, "#808080")  # Default gray
    
    def _create_summary_report(self, result, strategy_filename: str, 
                              guide_filename: str) -> Dict:
        """Create summary report of optimization results."""
        
        summary = {
            "optimization_results": {
                "final_performance": result.performance_metrics['final_win_rate'],
                "readability_score": result.human_readability_score,
                "complexity_rating": result.execution_complexity['complexity_rating'],
                "learning_time_hours": result.execution_complexity['estimated_learning_time_hours'],
                "unique_thresholds": result.execution_complexity['unique_thresholds'],
                "tier_alignment": result.execution_complexity['tier_alignment_score']
            },
            "files_created": {
                "strategy_file": strategy_filename,
                "guide_file": guide_filename
            },
            "tier_usage": result.tier_usage_analysis,
            "execution_tips": self._generate_execution_tips(result)
        }
        
        # Print summary
        print(f"\n🎉 OPTIMIZATION COMPLETE!")
        print(f"   Performance: {result.performance_metrics['final_win_rate']:+.2f} bb/100")
        print(f"   Readability: {result.human_readability_score:.1f}/100")
        print(f"   Complexity: {result.execution_complexity['complexity_rating']}")
        print(f"   Learning Time: ~{result.execution_complexity['estimated_learning_time_hours']:.1f} hours")
        print(f"\n📁 Files Created:")
        print(f"   Strategy: {strategy_filename}")
        print(f"   Guide: {guide_filename}")
        
        return summary
    
    def _generate_execution_tips(self, result) -> List[str]:
        """Generate specific execution tips based on optimization results."""
        
        tips = []
        
        complexity = result.execution_complexity['complexity_rating']
        
        if complexity == "EASY":
            tips.append("✅ This strategy is easy to learn - focus on memorizing tier boundaries")
            tips.append("🎯 Practice position-based opening ranges first")
        elif complexity == "MODERATE":
            tips.append("📚 Moderate complexity - break learning into chunks")
            tips.append("🏃 Practice preflop decisions until automatic, then add postflop")
        elif complexity in ["COMPLEX", "VERY_COMPLEX"]:
            tips.append("⚠️ Complex strategy - consider using simpler version for live play")
            tips.append("💡 Master one position at a time (start with Button)")
        
        # Tier-specific tips
        alignment_score = result.execution_complexity['tier_alignment_score']
        if alignment_score > 0.8:
            tips.append("🎯 Excellent tier alignment - use tier names instead of numbers")
        else:
            tips.append("📊 Consider adjusting tier boundaries for better memorability")
        
        # Learning time tips
        learning_hours = result.execution_complexity['estimated_learning_time_hours']
        if learning_hours < 3:
            tips.append("⚡ Quick to learn - perfect for immediate implementation")
        elif learning_hours < 8:
            tips.append("📅 Plan 1-2 study sessions to master this strategy")
        else:
            tips.append("📖 Complex strategy - plan multiple study sessions over time")
        
        return tips

# =============================================================================
# Predefined Tier Configurations
# =============================================================================

def get_standard_5_tier_config() -> Dict[str, Dict]:
    """Standard 5-tier configuration for most players."""
    return {
        "Elite": {"min_hs": 40, "max_hs": 50},
        "Premium": {"min_hs": 30, "max_hs": 39},
        "Gold": {"min_hs": 20, "max_hs": 29},
        "Silver": {"min_hs": 10, "max_hs": 19},
        "Bronze": {"min_hs": 1, "max_hs": 9}
    }

def get_simple_3_tier_config() -> Dict[str, Dict]:
    """Simplified 3-tier configuration for beginners."""
    return {
        "Strong": {"min_hs": 25, "max_hs": 50},
        "Medium": {"min_hs": 10, "max_hs": 24},
        "Weak": {"min_hs": 1, "max_hs": 9}
    }

def get_advanced_7_tier_config() -> Dict[str, Dict]:
    """Advanced 7-tier configuration for experts."""
    return {
        "Nuts": {"min_hs": 45, "max_hs": 50},
        "Elite": {"min_hs": 35, "max_hs": 44},
        "Premium": {"min_hs": 25, "max_hs": 34},
        "Strong": {"min_hs": 18, "max_hs": 24},
        "Good": {"min_hs": 12, "max_hs": 17},
        "Marginal": {"min_hs": 6, "max_hs": 11},
        "Weak": {"min_hs": 1, "max_hs": 5}
    }

# =============================================================================
# Easy Usage Examples
# =============================================================================

def example_quick_optimization():
    """Example: Quick optimization with standard 5-tier system."""
    
    print("🔥 EXAMPLE: Quick Strategy Optimization")
    print("=" * 50)
    
    # Initialize interface
    interface = StrategyOptimizerInterface()
    
    # Define HS tiers from existing strategy
    tier_config = get_standard_5_tier_config()
    interface.define_hs_tiers_from_strategy('baseline_strategy.json', tier_config)
    
    # Set simple constraints
    interface.set_simple_constraints("moderate")
    
    # Run quick optimization
    result = interface.optimize_strategy(
        base_strategy_file='baseline_strategy.json',
        method='quick',
        output_prefix='quick_optimized'
    )
    
    print(f"\n💡 EXECUTION TIPS:")
    for tip in result['execution_tips']:
        print(f"   {tip}")

def example_thorough_optimization():
    """Example: Thorough optimization for maximum performance."""
    
    print("\n🎯 EXAMPLE: Thorough Strategy Optimization")
    print("=" * 50)
    
    interface = StrategyOptimizerInterface()
    
    # Use advanced 7-tier system
    tier_config = get_advanced_7_tier_config()
    interface.define_hs_tiers_from_strategy('baseline_strategy.json', tier_config)
    
    # Set complex constraints for maximum performance
    interface.set_simple_constraints("complex")
    
    # Run thorough optimization
    result = interface.optimize_strategy(
        base_strategy_file='baseline_strategy.json',
        method='thorough',
        output_prefix='thorough_optimized'
    )
    
    print(f"\n📊 TIER USAGE ANALYSIS:")
    for tier_name, usage_count in result['tier_usage'].items():
        print(f"   {tier_name}: Used {usage_count} times in decision tables")

def example_beginner_optimization():
    """Example: Simple optimization for beginners."""
    
    print("\n👶 EXAMPLE: Beginner-Friendly Optimization")
    print("=" * 50)
    
    interface = StrategyOptimizerInterface()
    
    # Use simple 3-tier system
    tier_config = get_simple_3_tier_config()
    interface.define_hs_tiers_from_strategy('baseline_strategy.json', tier_config)
    
    # Set simple constraints
    interface.set_simple_constraints("simple")
    
    # Run quick optimization
    result = interface.optimize_strategy(
        base_strategy_file='baseline_strategy.json',
        method='standard',
        output_prefix='beginner_optimized'
    )
    
    print(f"\n🎓 LEARNING PLAN:")
    learning_hours = result['optimization_results']['learning_time_hours']
    print(f"   Total Learning Time: ~{learning_hours:.1f} hours")
    print(f"   Session 1 (1 hour): Memorize tier boundaries and opening ranges")
    print(f"   Session 2 (1 hour): Practice preflop vs raise decisions") 
    print(f"   Session 3 (1 hour): Add basic postflop c-betting rules")
    print(f"   Session 4+ ({learning_hours-3:.1f} hours): Practice and refinement")

# =============================================================================
# Command-Line Interface
# =============================================================================

def main():
    """Command-line interface for strategy optimization."""
    
    import sys
    
    if len(sys.argv) < 2:
        print("Human-Executable Strategy Optimizer")
        print("=" * 40)
        print("\nUsage:")
        print("  python simplified_optimizer_interface.py <strategy.json> [options]")
        print("\nOptions:")
        print("  --tiers {3|5|7}        Number of tiers (default: 5)")
        print("  --complexity {simple|moderate|complex}  Complexity level (default: moderate)")
        print("  --method {quick|standard|thorough}      Optimization method (default: standard)")
        print("  --output <prefix>      Output file prefix (default: optimized)")
        print("\nExamples:")
        print("  python simplified_optimizer_interface.py baseline.json")
        print("  python simplified_optimizer_interface.py baseline.json --tiers 3 --complexity simple")
        print("  python simplified_optimizer_interface.py baseline.json --method thorough --output advanced")
        
        print("\n🚀 QUICK START:")
        print("   1. Run with defaults: python simplified_optimizer_interface.py your_strategy.json")
        print("   2. Check optimized_strategy.json for new strategy")
        print("   3. Read optimized_guide.md for human-readable instructions")
        return
    
    # Parse arguments
    strategy_file = sys.argv[1]
    
    # Default options
    num_tiers = 5
    complexity = "moderate"
    method = "standard"
    output_prefix = "optimized"
    
    # Parse options
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--tiers' and i + 1 < len(sys.argv):
            num_tiers = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--complexity' and i + 1 < len(sys.argv):
            complexity = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--method' and i + 1 < len(sys.argv):
            method = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_prefix = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        # Validate strategy file exists
        if not os.path.exists(strategy_file):
            print(f"❌ Error: Strategy file '{strategy_file}' not found")
            return
        
        print(f"🎯 OPTIMIZING STRATEGY: {strategy_file}")
        print(f"   Tiers: {num_tiers}")
        print(f"   Complexity: {complexity}")
        print(f"   Method: {method}")
        print(f"   Output: {output_prefix}_*")
        
        # Initialize interface
        interface = StrategyOptimizerInterface()
        
        # Select tier configuration
        if num_tiers == 3:
            tier_config = get_simple_3_tier_config()
        elif num_tiers == 5:
            tier_config = get_standard_5_tier_config()
        elif num_tiers == 7:
            tier_config = get_advanced_7_tier_config()
        else:
            print(f"❌ Error: Unsupported number of tiers: {num_tiers}")
            return
        
        # Run optimization
        interface.define_hs_tiers_from_strategy(strategy_file, tier_config)
        interface.set_simple_constraints(complexity)
        
        result = interface.optimize_strategy(
            base_strategy_file=strategy_file,
            method=method,
            output_prefix=output_prefix
        )
        
        print(f"\n🎉 SUCCESS! Check these files:")
        print(f"   📋 Strategy: {result['files_created']['strategy_file']}")
        print(f"   📖 Guide: {result['files_created']['guide_file']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Run examples if no command line arguments
    if len(sys.argv) == 1:
        print("🔥 RUNNING EXAMPLES...")
        example_quick_optimization()
        example_beginner_optimization()
        # example_thorough_optimization()  # Skip for demo
    else:
        main()