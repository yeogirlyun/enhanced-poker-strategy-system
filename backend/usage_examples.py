# filename: usage_examples.py
"""
Practical Usage Examples for Enhanced Poker Strategy Simulation

This file demonstrates how to use the enhanced simulation framework
for real-world strategy development and testing scenarios.
"""

import json
import os
from enhanced_simulation_engine import EnhancedSimulationEngine
from strategy_testing_framework import StrategyTestingFramework
from next_gen_strategy_integration import NextGenStrategyFramework

# =============================================================================
# Example 1: Basic Strategy Comparison with Statistical Rigor
# =============================================================================

def example_basic_comparison():
    """Compare two strategies with proper statistical analysis."""
    
    print("🔬 EXAMPLE 1: Basic Strategy Comparison")
    print("=" * 50)
    
    # Strategy files to compare
    strategies = ['tight_strategy.json', 'loose_strategy.json']
    
    # Enhanced simulation configuration
    config = {
        'hands_per_run': 15000,    # More hands for better statistics
        'num_runs': 5,             # Multiple runs for confidence intervals
        'confidence_level': 0.95,  # 95% confidence intervals
        'use_multiprocessing': True,
        'track_detailed_logs': True
    }
    
    # Run enhanced simulation
    engine = EnhancedSimulationEngine(strategies, config)
    results = engine.run_comprehensive_analysis()
    
    # Extract key insights
    strategy_results = results['strategy_results']
    statistical_analysis = results['statistical_analysis']
    
    print(f"\n📊 RESULTS SUMMARY:")
    for strategy_name, result in strategy_results.items():
        name = strategy_name.replace('.json', '').replace('_', ' ').title()
        ci_low, ci_high = result.confidence_interval
        
        print(f"\n{name}:")
        print(f"  Win Rate: {result.win_rate_bb100:+.2f} bb/100")
        print(f"  95% CI: [{ci_low:+.2f}, {ci_high:+.2f}]")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"  Sample Size: {result.hands_played:,} hands")
    
    # Check for statistical significance
    print(f"\n🔍 STATISTICAL SIGNIFICANCE:")
    for comparison in statistical_analysis['pairwise_comparisons']:
        if comparison.is_significant:
            print(f"  ✅ {comparison.strategy_a} vs {comparison.strategy_b}:")
            print(f"     Difference: {comparison.win_rate_difference:+.2f} bb/100")
            print(f"     Confidence: {comparison.confidence_level:.0%}")
        else:
            print(f"  ❓ No significant difference detected")
            print(f"     Recommend {comparison.sample_size_needed:,} more hands")

# =============================================================================
# Example 2: Systematic Strategy Optimization
# =============================================================================

def example_strategy_optimization():
    """Optimize a strategy using systematic testing framework."""
    
    print("\n🎯 EXAMPLE 2: Strategy Optimization")
    print("=" * 50)
    
    # Initialize testing framework with baseline strategy
    baseline_strategy = 'baseline_strategy.json'
    framework = StrategyTestingFramework(baseline_strategy)
    
    # Test specific area (preflop aggression)
    print(f"🔧 Testing preflop aggression variations...")
    framework.run_focused_optimization('preflop')
    
    # Run ablation study to identify key components
    print(f"\n🔬 Running ablation study...")
    components = ['tight_preflop', 'aggressive_postflop', 'large_sizing']
    framework.run_ablation_study(components)
    
    # Generate comprehensive test suite
    print(f"\n🧪 Running comprehensive test suite...")
    framework.run_comprehensive_test_suite()

# =============================================================================
# Example 3: Population Analysis and Exploitation
# =============================================================================

def example_population_exploitation():
    """Analyze population trends and create exploitative strategies."""
    
    print("\n🎣 EXAMPLE 3: Population Exploitation")
    print("=" * 50)
    
    # Initialize next-gen framework
    base_strategies = ['gto_baseline.json', 'population_default.json']
    framework = NextGenStrategyFramework(base_strategies)
    
    # Analyze current population
    print(f"📊 Analyzing population trends...")
    opportunities = framework.population_analyzer.identify_exploitation_opportunities()
    
    if opportunities:
        print(f"\n🎯 EXPLOITATION OPPORTUNITIES FOUND:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"  {i}. {opp['type']}: {opp['description']}")
            print(f"     Confidence: {opp['confidence']:.1%}")
            print(f"     Expected Value: {opp['expected_value']:+.1f} bb/100")
            print(f"     Risk Level: {opp['risk_level']}")
        
        # Generate exploitative strategies
        print(f"\n🧬 Generating exploitative strategies...")
        market_intel = framework._gather_market_intelligence()
        evolved_strategies = framework.agentic_evolution.evolve_strategies(
            market_intel, opportunities
        )
        
        print(f"✅ Created {len(evolved_strategies)} exploitative variants")
        
    else:
        print(f"ℹ️ No significant exploitation opportunities detected")
        print(f"   Population appears well-balanced")

# =============================================================================
# Example 4: Continuous Learning and Adaptation
# =============================================================================

def example_continuous_adaptation():
    """Demonstrate continuous strategy adaptation over time."""
    
    print("\n🔄 EXAMPLE 4: Continuous Adaptation")
    print("=" * 50)
    
    # Setup for continuous learning
    strategies = ['adaptive_base.json']
    config = {
        'update_frequency_hours': 4,  # Check every 4 hours
        'min_confidence_threshold': 0.8,
        'max_evolution_generations': 5
    }
    
    framework = NextGenStrategyFramework(strategies, config)
    
    # Run short continuous optimization cycle
    print(f"🚀 Starting 24-hour continuous optimization...")
    framework.run_continuous_optimization(duration_hours=24)

# =============================================================================
# Example 5: Performance Validation and Quality Assurance
# =============================================================================

def example_validation_qa():
    """Demonstrate validation and quality assurance procedures."""
    
    print("\n✅ EXAMPLE 5: Validation & Quality Assurance")
    print("=" * 50)
    
    # Load test results for validation
    strategies = ['new_strategy.json', 'benchmark_strategy.json']
    
    # Run validation simulation
    config = {
        'hands_per_run': 25000,
        'num_runs': 8,  # More runs for better validation
        'confidence_level': 0.99,  # Higher confidence for validation
        'use_multiprocessing': True
    }
    
    engine = EnhancedSimulationEngine(strategies, config)
    results = engine.run_comprehensive_analysis()
    
    # Validate results quality
    validator = StatisticalValidator()
    validation_results = validator.validate_simulation_results(results['strategy_results'])
    
    print(f"📋 VALIDATION RESULTS:")
    print(f"  Overall Valid: {'✅' if validation_results['overall_valid'] else '❌'}")
    
    for check_name, check_result in validation_results['individual_checks'].items():
        status = '✅' if check_result['passed'] else '❌'
        print(f"  {check_name}: {status}")
        
        if not check_result['passed']:
            print(f"    Issue: {check_result.get('issue', 'Check failed')}")
    
    # Display recommendations
    if validation_results['recommendations']:
        print(f"\n💡 VALIDATION RECOMMENDATIONS:")
        for rec in validation_results['recommendations']:
            print(f"  • {rec}")

# =============================================================================
# Example 6: Advanced Strategy Analysis
# =============================================================================

def example_advanced_analysis():
    """Demonstrate advanced analysis capabilities."""
    
    print("\n📈 EXAMPLE 6: Advanced Strategy Analysis")
    print("=" * 50)
    
    # Analyze strategy performance by situation
    strategies = ['analyzed_strategy.json']
    
    config = {
        'hands_per_run': 20000,
        'num_runs': 6,
        'track_detailed_logs': True,
        'situational_analysis': True
    }
    
    engine = EnhancedSimulationEngine(strategies, config)
    results = engine.run_comprehensive_analysis()
    
    # Extract situational performance
    strategy_result = list(results['strategy_results'].values())[0]
    
    print(f"📊 SITUATIONAL PERFORMANCE BREAKDOWN:")
    
    # Position performance
    if strategy_result.position_performance:
        print(f"\n🎭 By Position:")
        for position, performance in strategy_result.position_performance.items():
            print(f"  {position}: {performance:.1f} avg hand strength")
    
    # Street performance  
    if strategy_result.street_performance:
        print(f"\n🃏 By Street:")
        for street, performance in strategy_result.street_performance.items():
            print(f"  {street.title()}: {performance:.1f} avg hand strength")
    
    # Component analysis
    print(f"\n🔧 Strategy Components:")
    print(f"  Variance: {strategy_result.variance:.2f}")
    print(f"  Sharpe Ratio: {strategy_result.sharpe_ratio:.2f}")
    print(f"  Profit per Decision: {strategy_result.profit_per_decision:.3f} BB")

# =============================================================================
# Example 7: Integration with External Tools
# =============================================================================

def example_external_integration():
    """Demonstrate integration with external poker tools."""
    
    print("\n🔗 EXAMPLE 7: External Tool Integration")
    print("=" * 50)
    
    # GTO Wizard integration example
    gto_config = {
        'gto_wizard_api': 'your_api_key_here',
        'comparison_spots': 100,  # Number of spots to compare
        'deviation_threshold': 0.1  # Significant deviation threshold
    }
    
    solver_integration = ModernSolverIntegration(gto_config)
    
    # Compare strategy to GTO baseline
    test_situation = {
        'street': 'flop',
        'position': 'BTN',
        'stack_depth': 100,
        'pot_size': 7.5,
        'board_cards': ['As', 'Kh', '7c']
    }
    
    print(f"🎯 Testing situation: BTN on As Kh 7c")
    
    gto_baseline = solver_integration.get_gto_baseline(test_situation)
    
    print(f"📊 GTO Baseline:")
    print(f"  Action Frequencies: {gto_baseline['action_frequencies']}")
    print(f"  Sizing Distribution: {gto_baseline['sizing_distribution']}")
    print(f"  Solver Confidence: {gto_baseline['solver_confidence']:.1%}")
    
    # Database integration for historical tracking
    print(f"\n💾 Historical Performance Tracking:")
    analyzer = HistoricalAnalyzer(get_database_connection())
    
    # Track strategy evolution over time
    evolution_report = analyzer.generate_evolution_report('test_strategy.json')
    print(f"  Performance trend: {evolution_report['trend_direction']}")
    print(f"  Trend strength: {evolution_report['trend_strength']:.2f}")
    print(f"  Recent volatility: {evolution_report['recent_volatility']:.2f}")

# =============================================================================
# Helper Classes for Examples
# =============================================================================

class StatisticalValidator:
    """Statistical validation helper for examples."""
    
    def validate_simulation_results(self, results):
        """Simplified validation for demonstration."""
        
        validations = {}
        
        # Check sample size adequacy
        total_hands = sum(r.hands_played for r in results.values())
        validations['sample_size'] = {
            'passed': total_hands >= 50000,
            'actual': total_hands,
            'required': 50000
        }
        
        # Check confidence interval width
        avg_ci_width = np.mean([
            r.confidence_interval[1] - r.confidence_interval[0] 
            for r in results.values()
        ])
        validations['confidence_precision'] = {
            'passed': avg_ci_width <= 4.0,  # Max 4 bb/100 width
            'actual_width': avg_ci_width,
            'max_acceptable': 4.0
        }
        
        # Overall validation
        overall_valid = all(v['passed'] for v in validations.values())
        
        recommendations = []
        if not validations['sample_size']['passed']:
            recommendations.append(f"Increase sample size to {validations['sample_size']['required']:,} hands")
        
        if not validations['confidence_precision']['passed']:
            recommendations.append("Run more simulation rounds to tighten confidence intervals")
        
        return {
            'overall_valid': overall_valid,
            'individual_checks': validations,
            'recommendations': recommendations
        }

class ModernSolverIntegration:
    """Mock solver integration for examples."""
    
    def __init__(self, config):
        self.config = config
    
    def get_gto_baseline(self, situation):
        """Mock GTO solver response."""
        return {
            'action_frequencies': {'check': 0.3, 'bet': 0.5, 'fold': 0.2},
            'sizing_distribution': {'small': 0.6, 'medium': 0.3, 'large': 0.1},
            'range_description': 'balanced_mixed',
            'solver_confidence': 0.89
        }

class HistoricalAnalyzer:
    """Mock historical analyzer for examples."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def generate_evolution_report(self, strategy_name):
        """Mock evolution report."""
        return {
            'trend_direction': 'improving',
            'trend_strength': 0.75,
            'recent_volatility': 1.8,
            'performance_history': []
        }

def get_database_connection():
    """Mock database connection."""
    return None

# =============================================================================
# Main Execution
# =============================================================================

def run_all_examples():
    """Run all usage examples."""
    
    print("🚀 ENHANCED POKER SIMULATION USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        example_basic_comparison()
        example_strategy_optimization()
        example_population_exploitation()
        example_continuous_adaptation()
        example_validation_qa()
        example_advanced_analysis()
        example_external_integration()
        
        print(f"\n✅ All examples completed successfully!")
        print(f"📚 These examples demonstrate the full capabilities")
        print(f"   of the enhanced poker strategy simulation framework.")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        print(f"💡 Make sure all required files and dependencies are available")

if __name__ == '__main__':
    # Import numpy for statistical calculations
    import numpy as np
    
    # Run examples
    run_all_examples()
    
    # Additional usage tips
    print(f"\n💡 USAGE TIPS:")
    print(f"   • Start with basic comparisons to validate your setup")
    print(f"   • Use systematic optimization for strategy development")
    print(f"   • Implement population analysis for real-world adaptation")
    print(f"   • Always validate results with statistical checks")
    print(f"   • Consider continuous adaptation for dynamic environments")