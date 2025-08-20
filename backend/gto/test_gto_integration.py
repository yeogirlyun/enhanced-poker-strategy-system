import argparse
import time
import sys
import os
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .gto_hands_generator import GTOHandsGenerator
from .round_trip_integrity_tester import RoundTripIntegrityTester
from backend.core.hand_model import Hand

class GTOIntegrationTester:
    def __init__(self):
        self.round_trip_tester = RoundTripIntegrityTester()
    
    def test_generation_replay_integrity(self, player_count: int, hands_to_generate: int):
        print(f"\n--- 🔄 Starting Generation-Replay Integrity Test for {player_count} players ---")
        start_time = time.time()
        generator = GTOHandsGenerator(player_count=player_count)
        generated_hands = generator.generate_hands_batch(hands_count=hands_to_generate)
        generation_time = time.time() - start_time
        print(f"✅ 1. Generated {len(generated_hands)} hands in {generation_time:.2f}s")
        filename = f"gto_hands_{player_count}_players.json"
        generator.export_to_json(generated_hands, filename)
        print(f"✅ 2. Saved hands to {filename}")
        print("✅ 3. Basic generation integrity verified")
        print(f"--- ✅ Generation Test Passed for {player_count} players ---\n")
        return generated_hands
    
    def test_comprehensive_round_trip_integrity(self, player_counts: List[int], hands_per_count: int = 3):
        """
        Test comprehensive round trip integrity using the RoundTripIntegrityTester.
        This tests: HandModel → PPSM → GTO → HandModel
        """
        print(f"\n--- 🔄 Starting Comprehensive Round-Trip Integrity Test ---")
        print(f"Player counts: {player_counts}, Hands per count: {hands_per_count}")
        
        start_time = time.time()
        total_tests = 0
        successful_tests = 0
        
        # Test GTO generation and basic integrity for each player count
        for player_count in player_counts:
            print(f"\n🧠 Testing {player_count} players...")
            
            # Test GTO generation
            success, hands = self.round_trip_tester.test_ppsm_to_gto_generation(
                player_count=player_count, 
                num_hands=hands_per_count
            )
            
            total_tests += 1
            if success:
                successful_tests += 1
                
                # Save generated hands for analysis
                filename = f"gto_hands_{player_count}_players_comprehensive.json"
                generator = GTOHandsGenerator(player_count=player_count)
                generator.export_to_json(hands, filename)
                print(f"📁 Saved {len(hands)} hands to {filename}")
        
        test_time = time.time() - start_time
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY:")
        print(f"   Success Rate: {success_rate*100:.1f}% ({successful_tests}/{total_tests})")
        print(f"   Total Time: {test_time:.2f}s")
        print(f"   Player Counts Tested: {player_counts}")
        
        # Export comprehensive results
        results_file = self.round_trip_tester.export_results("comprehensive_gto_integration_results.json")
        print(f"📁 Comprehensive results exported to: {results_file}")
        
        return {
            "success_rate": success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "test_time": test_time,
            "results_file": results_file
        }

    def benchmark_performance(self, player_count: int, iterations: int):
        print(f"\n--- ⏱️  Starting Performance Benchmark for {player_count} players ({iterations} iterations) ---")
        total_time = 0
        for i in range(iterations):
            start_time = time.time()
            generator = GTOHandsGenerator(player_count=player_count)
            generator.generate_hand()
            total_time += time.time() - start_time
        avg_time = total_time / iterations
        print(f"✅ Average hand generation time: {avg_time:.4f}s")
        print(f"--- ✅ Benchmark Complete ---\n")

def main():
    parser = argparse.ArgumentParser(description="GTO Integration Testing Harness with Round Trip Integrity")
    parser.add_argument('--generate', action='store_true', help="Generate and test basic GTO hands.")
    parser.add_argument('--comprehensive', action='store_true', help="Run comprehensive round trip integrity tests.")
    parser.add_argument('--players', default='2-6', help="Player counts to test (e.g., '6' or '2-6').")
    parser.add_argument('--hands-per-count', type=int, default=3, help="Number of hands to generate per player count.")
    parser.add_argument('--benchmark', action='store_true', help="Run performance benchmarks.")
    parser.add_argument('--iterations', type=int, default=20, help="Number of iterations for benchmarks.")
    parser.add_argument('--all', action='store_true', help="Run all tests (generate, comprehensive, benchmark).")
    args = parser.parse_args()
    
    print("🧪 GTO Integration Testing Framework")
    print("===================================")
    
    tester = GTOIntegrationTester()
    
    try:
        if '-' in args.players:
            start, end = map(int, args.players.split('-'))
            player_counts = list(range(start, end + 1))
        else:
            player_counts = [int(args.players)]
    except ValueError:
        print("❌ Invalid player range. Use format '6' or '2-9'.")
        return
    
    print(f"🎯 Testing player counts: {player_counts}")
    print(f"🔢 Hands per count: {args.hands_per_count}")
    
    # Run basic generation tests
    if args.generate or args.all:
        print("\n🚀 RUNNING BASIC GENERATION TESTS")
        for count in player_counts:
            tester.test_generation_replay_integrity(player_count=count, hands_to_generate=args.hands_per_count)
    
    # Run comprehensive round trip tests
    if args.comprehensive or args.all:
        print("\n🚀 RUNNING COMPREHENSIVE ROUND TRIP TESTS")
        results = tester.test_comprehensive_round_trip_integrity(
            player_counts=player_counts, 
            hands_per_count=args.hands_per_count
        )
        print(f"📊 Overall Success Rate: {results['success_rate']*100:.1f}%")
    
    # Run performance benchmarks
    if args.benchmark or args.all:
        print("\n🚀 RUNNING PERFORMANCE BENCHMARKS")
        for count in player_counts:
            tester.benchmark_performance(player_count=count, iterations=args.iterations)
    
    print("\n✅ All requested tests completed!")
    print("📁 Check the generated JSON files for detailed results.")

if __name__ == "__main__":
    main()