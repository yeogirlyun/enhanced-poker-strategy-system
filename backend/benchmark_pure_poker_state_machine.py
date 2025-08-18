#!/usr/bin/env python3
"""
Performance Benchmarks for PurePokerStateMachine

Comprehensive performance testing to ensure the poker engine can handle:
- High-volume gameplay (thousands of hands)
- Many concurrent players
- Rapid action processing
- Memory efficiency
- State transition speed

Benchmarks:
1. Throughput: Hands per second
2. Action latency: Time per action
3. Memory usage: Memory footprint over time
4. Scalability: Performance with different player counts
5. Stress testing: Extended sessions
6. Profiling: Identify bottlenecks
"""

import sys
import os
import time
import gc
import random
import tracemalloc
import cProfile
import pstats
import io
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import json
from unittest.mock import patch

sys.path.append('.')

from core.pure_poker_state_machine import (
    PurePokerStateMachine, GameConfig, DeckProvider, RulesProvider, AdvancementController
)
from core.poker_types import Player, PokerState
from core.hand_model import ActionType


# Mock providers for benchmarking
class FastDeckProvider:
    """Optimized deck provider for benchmarking."""
    
    def __init__(self):
        self.base_deck = self._create_base_deck()
    
    def _create_base_deck(self):
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        return [rank + suit for suit in suits for rank in ranks]
    
    def get_deck(self) -> List[str]:
        deck = self.base_deck.copy()
        random.shuffle(deck)
        return deck
    
    def replace_deck(self, deck: List[str]) -> None:
        pass


class FastRulesProvider:
    """Optimized rules provider for benchmarking."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        if num_players == 2:
            return dealer_pos
        return (dealer_pos + 3) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        n = len(players)
        for i in range(1, n + 1):
            idx = (dealer_pos + i) % n
            p = players[idx]
            if not p.has_folded and p.is_active:
                return idx
        return -1


class FastAdvancementController:
    """Optimized advancement controller for benchmarking."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        return current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]
    
    def on_round_complete(self, street: str, game_state) -> None:
        pass


@dataclass
class BenchmarkResult:
    """Store benchmark results."""
    name: str
    value: float
    unit: str
    details: Dict[str, Any] = None


@contextmanager
def timer(name: str = "Operation"):
    """Context manager for timing operations."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"  ⏱️  {name}: {elapsed:.4f}s")


@contextmanager
def suppress_prints():
    """Context manager to suppress print statements for faster benchmarking."""
    with patch('builtins.print'):
        yield


class PerformanceBenchmarks:
    """Comprehensive performance benchmarks for PPSM."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def create_fast_ppsm(self, num_players: int = 2) -> PurePokerStateMachine:
        """Create optimized PPSM for benchmarking."""
        config = GameConfig(
            num_players=num_players,
            small_blind=1.0,
            big_blind=2.0,
            starting_stack=100.0
        )
        return PurePokerStateMachine(
            config=config,
            deck_provider=FastDeckProvider(),
            rules_provider=FastRulesProvider(),
            advancement_controller=FastAdvancementController()
        )
    
    def simulate_random_hand(self, ppsm: PurePokerStateMachine) -> int:
        """Simulate a complete hand with random actions. Returns action count."""
        with suppress_prints():  # Suppress verbose poker logging during benchmarking
            ppsm.start_hand()
            actions = 0
            max_actions = 100  # Prevent infinite loops
            
            while actions < max_actions and ppsm.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                if ppsm.action_player_index < 0:
                    break
                
                player = ppsm.game_state.players[ppsm.action_player_index]
                if player.has_folded or not player.is_active:
                    break
                
                # Choose random valid action (biased towards aggressive play for faster games)
                rand = random.random()
                if rand < 0.1:  # 10% fold
                    if ppsm._is_valid_action(player, ActionType.FOLD, 0):
                        ppsm.execute_action(player, ActionType.FOLD, 0)
                        actions += 1
                elif rand < 0.4:  # 30% check/call
                    if ppsm._is_valid_action(player, ActionType.CHECK, 0):
                        ppsm.execute_action(player, ActionType.CHECK, 0)
                        actions += 1
                    elif ppsm._is_valid_action(player, ActionType.CALL, 0):
                        ppsm.execute_action(player, ActionType.CALL, 0)
                        actions += 1
                else:  # 60% bet/raise
                    if ppsm.game_state.current_bet == 0:
                        amount = random.uniform(2, 10)
                        if ppsm._is_valid_action(player, ActionType.BET, amount):
                            ppsm.execute_action(player, ActionType.BET, amount)
                            actions += 1
                    else:
                        amount = ppsm.game_state.current_bet * random.uniform(2, 3)
                        if ppsm._is_valid_action(player, ActionType.RAISE, amount):
                            ppsm.execute_action(player, ActionType.RAISE, amount)
                            actions += 1
                        elif ppsm._is_valid_action(player, ActionType.CALL, 0):
                            ppsm.execute_action(player, ActionType.CALL, 0)
                            actions += 1
                            
                # Safety check to prevent infinite loops
                if actions > 50:  # Reasonable limit
                    break
            
            return actions
    
    def benchmark_throughput(self, num_hands: int = 1000, num_players: int = 6):
        """Benchmark hands per second throughput."""
        print(f"\n📊 Benchmarking Throughput ({num_hands} hands, {num_players} players)...")
        
        ppsm = self.create_fast_ppsm(num_players)
        total_actions = 0
        
        start_time = time.perf_counter()
        
        for _ in range(num_hands):
            actions = self.simulate_random_hand(ppsm)
            total_actions += actions
        
        elapsed = time.perf_counter() - start_time
        
        hands_per_second = num_hands / elapsed
        actions_per_second = total_actions / elapsed
        avg_actions_per_hand = total_actions / num_hands
        
        self.results.append(BenchmarkResult(
            "Throughput",
            hands_per_second,
            "hands/sec",
            {
                "total_hands": num_hands,
                "total_actions": total_actions,
                "actions_per_second": actions_per_second,
                "avg_actions_per_hand": avg_actions_per_hand,
                "elapsed_time": elapsed
            }
        ))
        
        print(f"  ✅ {hands_per_second:.1f} hands/sec")
        print(f"  ✅ {actions_per_second:.1f} actions/sec")
        print(f"  ✅ {avg_actions_per_hand:.1f} avg actions/hand")
    
    def benchmark_action_latency(self, num_actions: int = 5000):
        """Benchmark individual action execution time."""
        print(f"\n📊 Benchmarking Action Latency ({num_actions} actions)...")
        
        ppsm = self.create_fast_ppsm(6)
        
        # Prepare actions
        action_times = []
        
        for _ in range(num_actions // 50):  # Multiple hands
            ppsm.start_hand()
            
            for _ in range(50):  # Actions per hand
                if ppsm.action_player_index < 0:
                    break
                
                player = ppsm.game_state.players[ppsm.action_player_index]
                if player.has_folded or not player.is_active:
                    break
                
                # Time a single action
                start = time.perf_counter()
                
                # Try different actions
                if ppsm._is_valid_action(player, ActionType.CALL, 0):
                    ppsm.execute_action(player, ActionType.CALL, 0)
                elif ppsm._is_valid_action(player, ActionType.CHECK, 0):
                    ppsm.execute_action(player, ActionType.CHECK, 0)
                else:
                    ppsm.execute_action(player, ActionType.FOLD, 0)
                
                elapsed = time.perf_counter() - start
                action_times.append(elapsed * 1000)  # Convert to ms
                
                if len(action_times) >= num_actions:
                    break
            
            if len(action_times) >= num_actions:
                break
        
        if not action_times:
            print("  ⚠️ No action times collected")
            return
        
        avg_latency = sum(action_times) / len(action_times)
        min_latency = min(action_times)
        max_latency = max(action_times)
        
        # Calculate percentiles
        sorted_times = sorted(action_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        self.results.append(BenchmarkResult(
            "Action Latency",
            avg_latency,
            "ms",
            {
                "min": min_latency,
                "max": max_latency,
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "samples": len(action_times)
            }
        ))
        
        print(f"  ✅ Avg: {avg_latency:.3f}ms")
        print(f"  ✅ P50: {p50:.3f}ms, P95: {p95:.3f}ms, P99: {p99:.3f}ms")
    
    def benchmark_memory_usage(self, num_hands: int = 100):
        """Benchmark memory usage over time."""
        print(f"\n📊 Benchmarking Memory Usage ({num_hands} hands)...")
        
        # Start memory tracking
        tracemalloc.start()
        
        ppsm = self.create_fast_ppsm(6)
        
        # Baseline memory
        baseline = tracemalloc.get_traced_memory()[0]
        
        # Run hands and track memory
        memory_samples = []
        
        for i in range(num_hands):
            self.simulate_random_hand(ppsm)
            
            if i % 10 == 0:  # Sample every 10 hands
                current, peak = tracemalloc.get_traced_memory()
                memory_samples.append(current - baseline)
        
        # Final memory
        final_current, final_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        avg_memory = sum(memory_samples) / len(memory_samples) / 1024  # KB
        peak_memory = (final_peak - baseline) / 1024  # KB
        final_memory = (final_current - baseline) / 1024  # KB
        
        self.results.append(BenchmarkResult(
            "Memory Usage",
            avg_memory,
            "KB",
            {
                "peak_kb": peak_memory,
                "final_kb": final_memory,
                "samples": len(memory_samples)
            }
        ))
        
        print(f"  ✅ Avg: {avg_memory:.1f}KB")
        print(f"  ✅ Peak: {peak_memory:.1f}KB")
        print(f"  ✅ Final: {final_memory:.1f}KB")
    
    def benchmark_scalability(self):
        """Benchmark performance with different player counts."""
        print("\n📊 Benchmarking Scalability...")
        
        player_counts = [2, 3, 4, 6, 8, 10]
        hands_per_test = 100
        
        results = {}
        
        for num_players in player_counts:
            ppsm = self.create_fast_ppsm(num_players)
            
            start = time.perf_counter()
            for _ in range(hands_per_test):
                self.simulate_random_hand(ppsm)
            elapsed = time.perf_counter() - start
            
            hands_per_sec = hands_per_test / elapsed
            results[num_players] = hands_per_sec
            
            print(f"  {num_players} players: {hands_per_sec:.1f} hands/sec")
        
        # Calculate scalability factor
        base_speed = results[2]
        scalability_factors = {n: results[n] / base_speed for n in player_counts}
        
        self.results.append(BenchmarkResult(
            "Scalability",
            0,  # No single value
            "factor",
            {
                "player_counts": player_counts,
                "hands_per_sec": results,
                "scalability_factors": scalability_factors
            }
        ))
    
    def benchmark_stress_test(self, duration_seconds: int = 5):
        """Stress test with continuous gameplay."""
        print(f"\n📊 Running Stress Test ({duration_seconds} seconds)...")
        
        ppsm = self.create_fast_ppsm(6)
        
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        
        hands_played = 0
        actions_executed = 0
        errors = 0
        
        while time.perf_counter() < end_time:
            try:
                actions = self.simulate_random_hand(ppsm)
                hands_played += 1
                actions_executed += actions
            except Exception as e:
                errors += 1
                if errors <= 3:  # Only print first few errors
                    print(f"  ⚠️ Error during stress test: {e}")
        
        elapsed = time.perf_counter() - start_time
        
        self.results.append(BenchmarkResult(
            "Stress Test",
            hands_played / elapsed,
            "hands/sec",
            {
                "total_hands": hands_played,
                "total_actions": actions_executed,
                "errors": errors,
                "duration": elapsed
            }
        ))
        
        print(f"  ✅ {hands_played} hands played")
        print(f"  ✅ {actions_executed} actions executed")
        print(f"  ✅ {errors} errors encountered")
        print(f"  ✅ {hands_played/elapsed:.1f} hands/sec sustained")
    
    def benchmark_state_transitions(self, num_transitions: int = 5000):
        """Benchmark state transition speed."""
        print(f"\n📊 Benchmarking State Transitions ({num_transitions} transitions)...")
        
        ppsm = self.create_fast_ppsm(2)
        
        # Valid transition pairs
        transitions = [
            (PokerState.START_HAND, PokerState.PREFLOP_BETTING),
            (PokerState.PREFLOP_BETTING, PokerState.DEAL_FLOP),
            (PokerState.DEAL_FLOP, PokerState.FLOP_BETTING),
            (PokerState.FLOP_BETTING, PokerState.DEAL_TURN),
            (PokerState.DEAL_TURN, PokerState.TURN_BETTING),
            (PokerState.TURN_BETTING, PokerState.DEAL_RIVER),
            (PokerState.DEAL_RIVER, PokerState.RIVER_BETTING),
            (PokerState.RIVER_BETTING, PokerState.SHOWDOWN),
        ]
        
        successful_transitions = 0
        start = time.perf_counter()
        
        for _ in range(num_transitions):
            from_state, to_state = random.choice(transitions)
            ppsm.current_state = from_state
            
            # Time the transition
            try:
                ppsm.transition_to(to_state)
                successful_transitions += 1
            except:
                pass  # Some transitions might fail due to game state
        
        elapsed = time.perf_counter() - start
        transitions_per_sec = successful_transitions / elapsed if elapsed > 0 else 0
        
        self.results.append(BenchmarkResult(
            "State Transitions",
            transitions_per_sec,
            "transitions/sec",
            {
                "total_attempted": num_transitions,
                "successful": successful_transitions,
                "elapsed": elapsed
            }
        ))
        
        print(f"  ✅ {transitions_per_sec:.0f} transitions/sec")
        print(f"  ✅ {successful_transitions}/{num_transitions} successful")
    
    def run_all_benchmarks(self):
        """Run complete benchmark suite."""
        print("🚀 PERFORMANCE BENCHMARK SUITE FOR PURE POKER STATE MACHINE")
        print("=" * 70)
        
        overall_start = time.perf_counter()
        
        # Run benchmarks (reduced scale for faster execution)
        self.benchmark_throughput(num_hands=100, num_players=6)
        self.benchmark_action_latency(num_actions=1000)
        self.benchmark_memory_usage(num_hands=50)
        self.benchmark_scalability()
        self.benchmark_state_transitions(num_transitions=1000)
        self.benchmark_stress_test(duration_seconds=3)
        
        overall_elapsed = time.perf_counter() - overall_start
        
        # Print summary
        print("\n" + "=" * 70)
        print("📈 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 70)
        
        for result in self.results:
            if result.unit != "factor" and result.value > 0:
                print(f"{result.name}: {result.value:.2f} {result.unit}")
            elif result.details and result.name == "Scalability":
                print(f"{result.name}: See detailed results above")
        
        print(f"\nTotal benchmark time: {overall_elapsed:.1f}s")
        
        # Performance grades
        print("\n🏆 PERFORMANCE GRADES:")
        
        # Throughput grade
        throughput_result = next((r for r in self.results if r.name == "Throughput"), None)
        if throughput_result and throughput_result.value > 100:
            print("  ✅ Throughput: EXCELLENT (>100 hands/sec)")
        elif throughput_result and throughput_result.value > 50:
            print("  🟡 Throughput: GOOD (>50 hands/sec)")
        else:
            print("  🔴 Throughput: NEEDS OPTIMIZATION")
        
        # Latency grade
        latency_result = next((r for r in self.results if r.name == "Action Latency"), None)
        if latency_result and latency_result.value < 1.0:
            print("  ✅ Latency: EXCELLENT (<1ms per action)")
        elif latency_result and latency_result.value < 5.0:
            print("  🟡 Latency: GOOD (<5ms per action)")
        else:
            print("  🔴 Latency: NEEDS OPTIMIZATION")
        
        # Memory grade
        memory_result = next((r for r in self.results if r.name == "Memory Usage"), None)
        if memory_result and memory_result.value < 100:
            print("  ✅ Memory: EXCELLENT (<100KB avg)")
        elif memory_result and memory_result.value < 500:
            print("  🟡 Memory: GOOD (<500KB avg)")
        else:
            print("  🔴 Memory: NEEDS OPTIMIZATION")
        
        # Stress test grade
        stress_result = next((r for r in self.results if r.name == "Stress Test"), None)
        if stress_result:
            errors = stress_result.details.get("errors", 0)
            if errors == 0:
                print("  ✅ Stability: EXCELLENT (0 errors)")
            elif errors < 5:
                print("  🟡 Stability: GOOD (<5 errors)")
            else:
                print("  🔴 Stability: NEEDS INVESTIGATION")
        
        return True
    
    def export_results(self, filename: str = "benchmark_results.json"):
        """Export benchmark results to JSON."""
        data = {
            "timestamp": time.time(),
            "results": [
                {
                    "name": r.name,
                    "value": r.value,
                    "unit": r.unit,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n📁 Results exported to {filename}")
        except Exception as e:
            print(f"\n⚠️ Could not export results: {e}")


def main():
    """Run performance benchmarks."""
    benchmarks = PerformanceBenchmarks()
    success = benchmarks.run_all_benchmarks()
    benchmarks.export_results()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
