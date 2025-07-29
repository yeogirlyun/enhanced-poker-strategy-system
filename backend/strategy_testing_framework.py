# filename: strategy_testing_framework.py
"""
Comprehensive Strategy Testing Framework

This framework provides tools for systematic strategy development and testing:
- Automated strategy variant generation
- A/B testing with statistical rigor
- Performance benchmarking against known baselines
- Strategy component isolation testing
- Continuous integration for strategy development
"""
import json
import os
import sys
import itertools
import copy
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enhanced_simulation_engine import EnhancedSimulationEngine
import time

@dataclass
class StrategyVariant:
    """Represents a strategy variant for testing."""
    name: str
    base_strategy: str
    modifications: Dict[str, Any]
    description: str
    hypothesis: str

@dataclass
class TestResult:
    """Results from a strategy test."""
    variant_name: str
    win_rate_bb100: float
    confidence_interval: Tuple[float, float]
    is_significant_vs_baseline: bool
    sample_size: int
    test_duration: float

class StrategyTestingFramework:
    """Framework for systematic strategy testing and development."""
    
    def __init__(self, baseline_strategy: str, output_dir: str = "strategy_tests"):
        self.baseline_strategy = baseline_strategy
        self.output_dir = output_dir
        self.test_results = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load baseline strategy
        with open(baseline_strategy, 'r') as f:
            self.baseline_config = json.load(f)
    
    def create_position_tightness_variants(self) -> List[StrategyVariant]:
        """Create variants testing different position-based tightness levels."""
        variants = []
        
        # Test tighter early position play
        tight_ep_mods = {
            "preflop.open_rules.UTG.threshold": 35,  # Tighter than baseline
            "preflop.open_rules.MP.threshold": 25,
        }
        variants.append(StrategyVariant(
            name="tight_early_position",
            base_strategy=self.baseline_strategy,
            modifications=tight_ep_mods,
            description="Tighter opening ranges in early position",
            hypothesis="Tighter EP play reduces variance and improves win rate"
        ))
        
        # Test looser button play
        loose_btn_mods = {
            "preflop.open_rules.BTN.threshold": 3,  # Much looser
            "preflop.vs_raise.BTN.IP.call_range": [8, 19]  # Wider calling range
        }
        variants.append(StrategyVariant(
            name="loose_button",
            base_strategy=self.baseline_strategy,
            modifications=loose_btn_mods,
            description="Much looser button play",
            hypothesis="Aggressive button play exploits position advantage"
        ))
        
        # Test balanced approach
        balanced_mods = {
            "preflop.open_rules.UTG.threshold": 32,
            "preflop.open_rules.MP.threshold": 22,
            "preflop.open_rules.CO.threshold": 12,
            "preflop.open_rules.BTN.threshold": 7
        }
        variants.append(StrategyVariant(
            name="balanced_ranges",
            base_strategy=self.baseline_strategy,
            modifications=balanced_mods,
            description="Smoothly balanced opening ranges by position",
            hypothesis="Smooth range progression optimizes overall strategy"
        ))
        
        return variants
    
    def create_aggression_variants(self) -> List[StrategyVariant]:
        """Create variants testing different aggression levels."""
        variants = []
        
        # High aggression postflop
        high_aggr_mods = {
            "postflop.pfa.flop.BTN.IP.val_thresh": 15,  # Lower threshold for betting
            "postflop.pfa.turn.BTN.IP.val_thresh": 20,
            "postflop.pfa.flop.BTN.IP.sizing": 0.8,     # Larger bet sizes
            "postflop.pfa.turn.BTN.IP.sizing": 0.9
        }
        variants.append(StrategyVariant(
            name="high_aggression",
            base_strategy=self.baseline_strategy,
            modifications=high_aggr_mods,
            description="More aggressive postflop betting",
            hypothesis="Higher aggression wins more pots and builds bigger pots with strong hands"
        ))
        
        # Conservative postflop
        conservative_mods = {
            "postflop.pfa.flop.UTG.OOP.val_thresh": 40,  # Higher threshold
            "postflop.pfa.flop.MP.OOP.val_thresh": 35,
            "postflop.caller.flop.UTG.OOP.small_bet": [50, 35],  # Tighter calling
            "postflop.caller.flop.MP.OOP.small_bet": [45, 32]
        }
        variants.append(StrategyVariant(
            name="conservative_postflop",
            base_strategy=self.baseline_strategy,
            modifications=conservative_mods,
            description="More conservative postflop play",
            hypothesis="Conservative play reduces variance in difficult spots"
        ))
        
        return variants
    
    def create_sizing_variants(self) -> List[StrategyVariant]:
        """Create variants testing different bet sizing strategies."""
        variants = []
        
        # Polarized sizing (small value bets, large bluffs)
        polarized_mods = {
            "postflop.pfa.flop.BTN.IP.sizing": 0.4,     # Smaller value bets
            "postflop.pfa.turn.BTN.IP.sizing": 0.5,
            "postflop.pfa.river.BTN.IP.sizing": 0.9,    # Larger river bets
            "preflop.open_rules.BTN.sizing": 2.2        # Smaller opens
        }
        variants.append(StrategyVariant(
            name="polarized_sizing",
            base_strategy=self.baseline_strategy,
            modifications=polarized_mods,
            description="Polarized bet sizing strategy",
            hypothesis="Polarized sizing is harder to exploit and more profitable"
        ))
        
        # Large sizing across all streets
        large_sizing_mods = {
            "postflop.pfa.flop.BTN.IP.sizing": 0.9,
            "postflop.pfa.turn.BTN.IP.sizing": 1.0,
            "postflop.pfa.river.BTN.IP.sizing": 1.2,
            "preflop.open_rules.BTN.sizing": 3.0
        }
        variants.append(StrategyVariant(
            name="large_sizing",
            base_strategy=self.baseline_strategy,
            modifications=large_sizing_mods,
            description="Consistently large bet sizing",
            hypothesis="Large sizing maximizes value and fold equity"
        ))
        
        return variants
    
    def create_blind_defense_variants(self) -> List[StrategyVariant]:
        """Create variants testing different blind defense strategies."""
        variants = []
        
        # Tight blind defense
        tight_defense_mods = {
            "preflop.blind_defense.BB.vs_BTN.call_range": [8, 19],  # Tighter calling
            "preflop.blind_defense.BB.vs_CO.call_range": [10, 19],
            "preflop.blind_defense.SB.vs_BTN.call_range": [12, 19]
        }
        variants.append(StrategyVariant(
            name="tight_blind_defense",
            base_strategy=self.baseline_strategy,
            modifications=tight_defense_mods,
            description="Tighter blind defense ranges",
            hypothesis="Tight defense reduces losses in difficult OOP spots"
        ))
        
        # Aggressive blind defense (more 3-betting)
        aggressive_defense_mods = {
            "preflop.blind_defense.BB.vs_BTN.value_thresh": 15,    # 3-bet more hands
            "preflop.blind_defense.BB.vs_CO.value_thresh": 18,
            "preflop.blind_defense.SB.vs_BTN.value_thresh": 18,
            "preflop.blind_defense.BB.vs_BTN.sizing": 4.0         # Larger 3-bets
        }
        variants.append(StrategyVariant(
            name="aggressive_blind_defense",
            base_strategy=self.baseline_strategy,
            modifications=aggressive_defense_mods,
            description="More aggressive blind defense with more 3-betting",
            hypothesis="Aggressive defense exploits late position opens"
        ))
        
        return variants
    
    def create_strategy_file(self, variant: StrategyVariant) -> str:
        """Create a strategy file for a variant."""
        # Start with baseline strategy
        modified_strategy = copy.deepcopy(self.baseline_config)
        
        # Apply modifications
        for path, value in variant.modifications.items():
            self._set_nested_value(modified_strategy, path, value)
        
        # Save to file
        filename = os.path.join(self.output_dir, f"{variant.name}.json")
        with open(filename, 'w') as f:
            json.dump(modified_strategy, f, indent=2)
        
        return filename
    
    def _set_nested_value(self, config: Dict, path: str, value: Any):
        """Set a nested dictionary value using dot notation."""
        keys = path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def run_variant_test(self, variant: StrategyVariant, hands_per_run: int = 10000, num_runs: int = 3) -> TestResult:
        """Test a single strategy variant against the baseline."""
        print(f"\n🧪 Testing variant: {variant.name}")
        print(f"   Hypothesis: {variant.hypothesis}")
        
        # Create strategy file
        variant_file = self.create_strategy_file(variant)
        
        # Run simulation
        start_time = time.time()
        
        config = {
            'hands_per_run': hands_per_run,
            'num_runs': num_runs,
            'use_multiprocessing': True,
            'track_detailed_logs': True
        }
        
        engine = EnhancedSimulationEngine([self.baseline_strategy, variant_file], config)
        results = engine.run_comprehensive_analysis()
        
        end_time = time.time()
        
        # Extract results for the variant
        variant_results = None
        baseline_results = None
        
        for strategy_name, result in results['strategy_results'].items():
            if variant_file in strategy_name:
                variant_results = result
            elif self.baseline_strategy in strategy_name:
                baseline_results = result
        
        # Determine if significantly different from baseline
        is_significant = False
        for comparison in results['statistical_analysis']['pairwise_comparisons']:
            if (variant_file in comparison.strategy_a or variant_file in comparison.strategy_b):
                is_significant = comparison.is_significant
                break
        
        test_result = TestResult(
            variant_name=variant.name,
            win_rate_bb100=variant_results.win_rate_bb100,
            confidence_interval=variant_results.confidence_interval,
            is_significant_vs_baseline=is_significant,
            sample_size=variant_results.hands_played,
            test_duration=end_time - start_time
        )
        
        self.test_results.append(test_result)
        
        # Print immediate results
        improvement = variant_results.win_rate_bb100 - baseline_results.win_rate_bb100
        significance_marker = "✅" if is_significant else "❓"
        
        print(f"   Result: {improvement:+.2f} bb/100 vs baseline {significance_marker}")
        print(f"   Confidence: {variant_results.confidence_interval}")
        print(f"   Duration: {end_time - start_time:.1f}s")
        
        return test_result
    
    def run_comprehensive_test_suite(self):
        """Run a comprehensive test of multiple strategy variants."""
        print("🚀 STARTING COMPREHENSIVE STRATEGY TEST SUITE")
        print("=" * 60)
        
        all_variants = []
        all_variants.extend(self.create_position_tightness_variants())
        all_variants.extend(self.create_aggression_variants())
        all_variants.extend(self.create_sizing_variants())
        all_variants.extend(self.create_blind_defense_variants())
        
        print(f"Testing {len(all_variants)} strategy variants...")
        
        successful_variants = []
        
        for i, variant in enumerate(all_variants, 1):
            print(f"\n[{i}/{len(all_variants)}] Testing: {variant.name}")
            
            try:
                result = self.run_variant_test(variant, hands_per_run=15000, num_runs=3)
                
                if result.is_significant_vs_baseline and result.win_rate_bb100 > 0:
                    successful_variants.append((variant, result))
                    print(f"   ✅ PROMISING VARIANT IDENTIFIED!")
                
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
                continue
        
        # Generate final report
        self._generate_test_suite_report(all_variants, successful_variants)
    
    def run_focused_optimization(self, focus_area: str):
        """Run focused testing on a specific area."""
        print(f"🎯 FOCUSED OPTIMIZATION: {focus_area.upper()}")
        print("=" * 50)
        
        if focus_area == "preflop":
            variants = self.create_position_tightness_variants()
        elif focus_area == "aggression":
            variants = self.create_aggression_variants()
        elif focus_area == "sizing":
            variants = self.create_sizing_variants()
        elif focus_area == "blinds":
            variants = self.create_blind_defense_variants()
        else:
            print(f"Unknown focus area: {focus_area}")
            return
        
        best_variant = None
        best_result = None
        
        for variant in variants:
            result = self.run_variant_test(variant, hands_per_run=20000, num_runs=5)
            
            if best_result is None or result.win_rate_bb100 > best_result.win_rate_bb100:
                best_variant = variant
                best_result = result
        
        print(f"\n🏆 BEST VARIANT IN {focus_area.upper()}:")
        print(f"   Name: {best_variant.name}")
        print(f"   Win Rate: {best_result.win_rate_bb100:+.2f} bb/100")
        print(f"   Confidence: {best_result.confidence_interval}")
        print(f"   Significant: {'Yes' if best_result.is_significant_vs_baseline else 'No'}")
        
        # Create optimized strategy file
        if best_result.is_significant_vs_baseline and best_result.win_rate_bb100 > 0:
            optimized_file = self.create_strategy_file(best_variant)
            optimized_output = os.path.join(self.output_dir, f"optimized_{focus_area}.json")
            os.rename(optimized_file, optimized_output)
            print(f"   Optimized strategy saved to: {optimized_output}")
    
    def run_ablation_study(self, strategy_components: List[str]):
        """Run ablation study by removing/modifying individual components."""
        print("🔬 ABLATION STUDY")
        print("=" * 40)
        
        component_modifications = {
            "tight_preflop": {
                "preflop.open_rules.UTG.threshold": 35,
                "preflop.open_rules.MP.threshold": 25,
                "preflop.open_rules.CO.threshold": 15,
                "preflop.open_rules.BTN.threshold": 8
            },
            "aggressive_postflop": {
                "postflop.pfa.flop.BTN.IP.val_thresh": 15,
                "postflop.pfa.turn.BTN.IP.val_thresh": 20,
                "postflop.pfa.river.BTN.IP.val_thresh": 30
            },
            "large_sizing": {
                "postflop.pfa.flop.BTN.IP.sizing": 0.8,
                "postflop.pfa.turn.BTN.IP.sizing": 0.9,
                "postflop.pfa.river.BTN.IP.sizing": 1.0
            },
            "tight_blind_defense": {
                "preflop.blind_defense.BB.vs_BTN.call_range": [8, 19],
                "preflop.blind_defense.SB.vs_BTN.call_range": [12, 19]
            }
        }
        
        component_results = {}
        
        for component in strategy_components:
            if component in component_modifications:
                variant = StrategyVariant(
                    name=f"ablation_{component}",
                    base_strategy=self.baseline_strategy,
                    modifications=component_modifications[component],
                    description=f"Ablation test of {component}",
                    hypothesis=f"Testing isolated impact of {component}"
                )
                
                result = self.run_variant_test(variant, hands_per_run=12000, num_runs=4)
                component_results[component] = result
        
        # Report ablation results
        print(f"\n📊 ABLATION STUDY RESULTS:")
        sorted_components = sorted(
            component_results.items(), 
            key=lambda x: x[1].win_rate_bb100, 
            reverse=True
        )
        
        for component, result in sorted_components:
            significance = "✅" if result.is_significant_vs_baseline else "❓"
            print(f"   {component}: {result.win_rate_bb100:+.2f} bb/100 {significance}")
    
    def _generate_test_suite_report(self, all_variants: List[StrategyVariant], successful_variants: List[Tuple[StrategyVariant, TestResult]]):
        """Generate comprehensive test suite report."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE STRATEGY TEST SUITE RESULTS")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total variants tested: {len(all_variants)}")
        print(f"   Successful improvements: {len(successful_variants)}")
        print(f"   Success rate: {len(successful_variants) / len(all_variants) * 100:.1f}%")
        
        if successful_variants:
            print(f"\n🏆 TOP PERFORMING VARIANTS:")
            sorted_successful = sorted(successful_variants, key=lambda x: x[1].win_rate_bb100, reverse=True)
            
            for i, (variant, result) in enumerate(sorted_successful[:5], 1):
                print(f"   #{i}: {variant.name}")
                print(f"      Win Rate: {result.win_rate_bb100:+.2f} bb/100")
                print(f"      Hypothesis: {variant.hypothesis}")
                print(f"      Confidence: {result.confidence_interval}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if successful_variants:
            best_variant, best_result = max(successful_variants, key=lambda x: x[1].win_rate_bb100)
            print(f"   1. Implement '{best_variant.name}' as primary strategy improvement")
            print(f"   2. Further test combinations of successful variants")
            print(f"   3. Run longer simulations on top performers for final validation")
        else:
            print(f"   1. Current baseline strategy appears well-optimized")
            print(f"   2. Consider testing more radical strategy changes")
            print(f"   3. Examine opponent strategy assumptions")
        
        # Save detailed results
        report_file = os.path.join(self.output_dir, "test_suite_report.json")
        report_data = {
            "summary": {
                "total_variants": len(all_variants),
                "successful_variants": len(successful_variants),
                "test_timestamp": time.time()
            },
            "results": [
                {
                    "variant_name": result.variant_name,
                    "win_rate_bb100": result.win_rate_bb100,
                    "confidence_interval": result.confidence_interval,
                    "is_significant": result.is_significant_vs_baseline,
                    "sample_size": result.sample_size
                }
                for _, result in successful_variants
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("=" * 80)


def main():
    """Command-line interface for strategy testing framework."""
    if len(sys.argv) < 2:
        print("Usage: python strategy_testing_framework.py <baseline_strategy.json> [command] [options]")
        print("\nCommands:")
        print("  comprehensive    - Run full test suite on all areas")
        print("  focused <area>   - Focus on specific area (preflop/aggression/sizing/blinds)")
        print("  ablation <comp>  - Run ablation study on components")
        print("  custom <file>    - Test custom strategy variants from file")
        print("\nExamples:")
        print("  python strategy_testing_framework.py baseline.json comprehensive")
        print("  python strategy_testing_framework.py baseline.json focused preflop")
        print("  python strategy_testing_framework.py baseline.json ablation tight_preflop,aggressive_postflop")
        return
    
    baseline_strategy = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "comprehensive"
    
    framework = StrategyTestingFramework(baseline_strategy)
    
    try:
        if command == "comprehensive":
            framework.run_comprehensive_test_suite()
        elif command == "focused" and len(sys.argv) > 3:
            focus_area = sys.argv[3]
            framework.run_focused_optimization(focus_area)
        elif command == "ablation" and len(sys.argv) > 3:
            components = sys.argv[3].split(',')
            framework.run_ablation_study(components)
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()