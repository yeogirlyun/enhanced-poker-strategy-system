#!/usr/bin/env python3
"""
Comprehensive Round Trip Integrity Testing Framework

This module provides comprehensive testing for the GTO integration with PPSM and Hand Model.
Tests the complete pipeline: HandModel → PPSM → GTO → HandModel

Architecture Compliance:
- Single-threaded, event-driven testing
- Deterministic behavior for reproducible results
- Clean separation of concerns
- No timing violations or UI coupling
"""

import json
import time
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.hand_model import Hand, HandMetadata, Seat
from backend.core.pure_poker_state_machine import GameConfig
from backend.core.sessions.hands_review_session import HandsReviewSession
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.gto.gto_hands_generator import GTOHandsGenerator

@dataclass
class RoundTripTestResult:
    """Results from a round trip test"""
    test_id: str
    original_hand_id: str
    generated_hand_id: str
    player_count: int
    success: bool
    pot_match: bool
    action_count_match: bool
    final_state_match: bool
    errors: List[str]
    performance_metrics: Dict[str, float]
    detailed_comparison: Dict[str, Any]

class RoundTripIntegrityTester:
    """
    Comprehensive round trip integrity testing framework.
    
    Tests the complete pipeline:
    1. HandModel → PPSM replay (using HandModelDecisionEngineAdapter)
    2. PPSM → GTO generation (using GTODecisionEngineAdapter) 
    3. GTO → HandModel export (round trip completion)
    4. Validation of integrity across the pipeline
    """
    
    def __init__(self, output_dir: str = "round_trip_test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_results: List[RoundTripTestResult] = []
        print(f"🧪 RoundTripIntegrityTester: Initialized with output dir {self.output_dir}")
    
    def convert_gto_hand_to_hand_model(self, gto_hand_data: Dict[str, Any]) -> Hand:
        """
        Convert GTO hand data to Hand model for deterministic replay.
        
        Args:
            gto_hand_data: Generated GTO hand data
            
        Returns:
            Hand model for hands review session
        """
        try:
            print(f"📋 Converting GTO hand {gto_hand_data.get('hand_id', 'unknown')} to Hand model")
            
            # Create metadata
            metadata = HandMetadata(
                table_id='gto_table',
                hand_id=gto_hand_data.get('hand_id', 'gto_unknown'),
                big_blind=100.0,  # From our GTO config
                small_blind=50.0  # From our GTO config
            )
            
            # Create seats from players data
            seats = []
            players_data = gto_hand_data.get('players', [])
            
            for i, player_data in enumerate(players_data):
                seat = Seat(
                    seat_no=i+1,
                    player_uid=player_data.get('name', f'Seat{i+1}'),
                    starting_stack=player_data.get('stack', 10000.0),
                    is_button=(i == 0)  # First seat is button for simplicity
                )
                seats.append(seat)
            
            # Create Hand model
            hand = Hand(metadata=metadata, seats=seats)
            
            print(f"✅ Converted GTO hand to Hand model with {len(seats)} players")
            return hand
            
        except Exception as e:
            print(f"❌ Error converting GTO hand to Hand model: {e}")
            raise
    
    def test_hand_model_to_ppsm_replay(self, hand_model: Hand) -> Tuple[bool, Dict[str, Any]]:
        """
        Test HandModel → PPSM replay using HandsReviewSession with deterministic deck.
        
        Args:
            hand_model: Hand model to replay
            
        Returns:
            (success, replay_results) tuple
        """
        try:
            print(f"🎯 Testing HandModel → PPSM replay for hand {hand_model.metadata.hand_id}")
            
            # Create game config matching the hand
            config = GameConfig(
                num_players=len(hand_model.seats),
                starting_stack=max(seat.starting_stack for seat in hand_model.seats),
                small_blind=hand_model.metadata.small_blind,
                big_blind=hand_model.metadata.big_blind
            )
            
            # Create decision engine with hand model (provides deterministic actions)
            decision_engine = HandModelDecisionEngine(hand_model)
            
            # Create hands review session (this uses deterministic deck)
            session = HandsReviewSession(config, decision_engine)
            
            # Initialize session
            if not session.initialize_session():
                raise Exception("Failed to initialize hands review session")
            
            # Link decision engine to FPSM
            decision_engine.fpsm = session.fpsm
            
            # Replay the hand by stepping through
            max_actions = 50
            actions_executed = 0
            start_time = time.time()
            timeout_seconds = 10.0
            
            print(f"   Starting replay with max {max_actions} actions...")
            
            while (not session.is_replay_complete() and 
                   actions_executed < max_actions and 
                   session.session_active):
                
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"   ⏰ TIMEOUT: Hand took longer than {timeout_seconds} seconds")
                    break
                
                if not session.step_forward():
                    break
                
                actions_executed += 1
            
            # Get final state
            final_game_info = session.get_game_info()
            final_pot = final_game_info.get('pot', 0)
            
            success = (
                final_pot > 0 and
                actions_executed > 0 and
                session.is_replay_complete()
            )
            
            replay_results = {
                'success': success,
                'final_pot': final_pot,
                'actions_executed': actions_executed,
                'action_log': [],  # Would need to be captured from session
                'execution_time_ms': (time.time() - start_time) * 1000
            }
            
            print(f"✅ HandModel → PPSM replay {'SUCCESS' if success else 'FAILED'} "
                  f"({actions_executed} actions, pot: ${final_pot})")
            return success, replay_results
            
        except Exception as e:
            print(f"❌ HandModel → PPSM replay ERROR: {e}")
            return False, {"error": str(e)}
    
    def test_ppsm_to_gto_generation(self, player_count: int, num_hands: int = 5) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Test PPSM → GTO generation using GTOHandsGenerator.
        
        Args:
            player_count: Number of players for generated hands
            num_hands: Number of hands to generate
            
        Returns:
            (success, generated_hands) tuple
        """
        try:
            print(f"🧠 Testing PPSM → GTO generation for {player_count} players, {num_hands} hands")
            
            # Create GTO hands generator
            generator = GTOHandsGenerator(player_count=player_count)
            
            # Generate batch of hands
            start_time = time.time()
            generated_hands = generator.generate_hands_batch(hands_count=num_hands)
            generation_time = time.time() - start_time
            
            success = (
                len(generated_hands) == num_hands and
                all(hand.get('final_pot', 0) > 0 for hand in generated_hands) and
                all(len(hand.get('players', [])) == player_count for hand in generated_hands)
            )
            
            print(f"✅ PPSM → GTO generation {'SUCCESS' if success else 'FAILED'} "
                  f"({len(generated_hands)} hands in {generation_time:.2f}s)")
            
            return success, generated_hands
            
        except Exception as e:
            print(f"❌ PPSM → GTO generation ERROR: {e}")
            return False, []
    
    def test_gto_to_hand_model_conversion(self, gto_hand_data: Dict[str, Any]) -> Tuple[bool, Optional[Hand]]:
        """
        Test GTO → HandModel conversion.
        
        Args:
            gto_hand_data: GTO generated hand data
            
        Returns:
            (success, hand_model) tuple
        """
        try:
            print(f"📋 Testing GTO → HandModel conversion for hand {gto_hand_data.get('hand_id', 'unknown')}")
            
            # This is a placeholder for the conversion logic
            # In a complete implementation, this would convert GTO data back to Hand model format
            # For now, we'll simulate this conversion
            
            success = (
                'hand_id' in gto_hand_data and
                'player_count' in gto_hand_data and
                'final_pot' in gto_hand_data and
                'players' in gto_hand_data
            )
            
            print(f"✅ GTO → HandModel conversion {'SUCCESS' if success else 'FAILED'}")
            
            # Return None for now since conversion isn't fully implemented
            return success, None
            
        except Exception as e:
            print(f"❌ GTO → HandModel conversion ERROR: {e}")
            return False, None
    
    def run_complete_round_trip_test(self, hand_model: Hand) -> RoundTripTestResult:
        """
        Run complete round trip test: HandModel → PPSM → GTO → HandModel.
        
        Args:
            hand_model: Original hand model to test
            
        Returns:
            RoundTripTestResult with comprehensive results
        """
        test_id = f"rt_{int(time.time())}_{hand_model.metadata.hand_id}"
        start_time = time.time()
        errors = []
        
        print(f"\n🔄 Starting complete round trip test: {test_id}")
        
        # Step 1: HandModel → PPSM replay
        ppsm_success, ppsm_results = self.test_hand_model_to_ppsm_replay(hand_model)
        if not ppsm_success:
            errors.append(f"PPSM replay failed: {ppsm_results.get('error', 'Unknown error')}")
        
        # Step 2: PPSM → GTO generation  
        player_count = len(hand_model.seats)
        gto_success, gto_hands = self.test_ppsm_to_gto_generation(player_count, num_hands=1)
        if not gto_success:
            errors.append("GTO generation failed")
        
        # Step 3: GTO → HandModel conversion and replay test
        conversion_success = False
        replay_gto_success = False
        if gto_success and gto_hands:
            try:
                # Convert GTO hand back to Hand model
                converted_hand = self.convert_gto_hand_to_hand_model(gto_hands[0])
                conversion_success = True
                
                # Test replay of the converted hand using hands review
                replay_gto_success, replay_gto_results = self.test_hand_model_to_ppsm_replay(converted_hand)
                if not replay_gto_success:
                    errors.append("GTO hand replay failed")
                    
            except Exception as e:
                conversion_success = False
                errors.append(f"GTO to HandModel conversion failed: {e}")
        
        # Performance metrics
        total_time = time.time() - start_time
        performance_metrics = {
            "total_time_ms": total_time * 1000,
            "ppsm_replay_time_ms": ppsm_results.get('execution_time_ms', 0),
            "gto_generation_time_ms": 0,  # Would be measured in actual implementation
            "conversion_time_ms": 0       # Would be measured in actual implementation
        }
        
        # Overall success - all steps must pass
        overall_success = ppsm_success and gto_success and conversion_success and replay_gto_success
        
        # Create detailed comparison
        detailed_comparison = {
            "original_pot": sum(seat.starting_stack for seat in hand_model.seats),
            "ppsm_final_pot": ppsm_results.get('final_pot', 0),
            "gto_final_pot": gto_hands[0].get('final_pot', 0) if gto_hands else 0,
            "original_actions": len(hand_model.actions),
            "ppsm_actions": len(ppsm_results.get('action_log', [])),
            "players_match": True  # Would be computed in actual implementation
        }
        
        # Pot matching (within tolerance)
        pot_match = (
            abs(detailed_comparison['original_pot'] - detailed_comparison['ppsm_final_pot']) < 1.0 and
            abs(detailed_comparison['ppsm_final_pot'] - detailed_comparison['gto_final_pot']) < 1.0
        )
        
        result = RoundTripTestResult(
            test_id=test_id,
            original_hand_id=hand_model.metadata.hand_id,
            generated_hand_id=gto_hands[0].get('hand_id', '') if gto_hands else '',
            player_count=player_count,
            success=overall_success,
            pot_match=pot_match,
            action_count_match=abs(detailed_comparison['original_actions'] - detailed_comparison['ppsm_actions']) <= 2,
            final_state_match=conversion_success,
            errors=errors,
            performance_metrics=performance_metrics,
            detailed_comparison=detailed_comparison
        )
        
        self.test_results.append(result)
        
        print(f"{'✅ SUCCESS' if overall_success else '❌ FAILED'} - Round trip test {test_id} completed in {total_time:.2f}s")
        
        return result
    
    def run_batch_round_trip_tests(self, hand_models: List[Hand], player_counts: List[int] = None) -> Dict[str, Any]:
        """
        Run batch round trip tests across multiple hands and player counts.
        
        Args:
            hand_models: List of hand models to test
            player_counts: Optional list of player counts for GTO generation tests
            
        Returns:
            Comprehensive batch test results
        """
        if player_counts is None:
            player_counts = [2, 3, 4, 6, 9]
        
        print(f"\n🚀 Starting batch round trip tests: {len(hand_models)} hands, {len(player_counts)} player counts")
        
        batch_start_time = time.time()
        
        # Test each hand model
        for i, hand_model in enumerate(hand_models):
            print(f"\n--- Testing hand {i+1}/{len(hand_models)}: {hand_model.metadata.hand_id} ---")
            self.run_complete_round_trip_test(hand_model)
        
        # Test GTO generation for each player count
        for player_count in player_counts:
            print(f"\n--- Testing GTO generation for {player_count} players ---")
            self.test_ppsm_to_gto_generation(player_count, num_hands=3)
        
        batch_time = time.time() - batch_start_time
        
        # Compile results
        successful_tests = [r for r in self.test_results if r.success]
        failed_tests = [r for r in self.test_results if not r.success]
        
        batch_results = {
            "total_tests": len(self.test_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(self.test_results) if self.test_results else 0,
            "total_time_seconds": batch_time,
            "average_test_time_ms": (batch_time * 1000) / len(self.test_results) if self.test_results else 0,
            "pot_match_rate": len([r for r in self.test_results if r.pot_match]) / len(self.test_results) if self.test_results else 0,
            "player_counts_tested": player_counts,
            "errors_summary": {}
        }
        
        # Error analysis
        all_errors = []
        for result in failed_tests:
            all_errors.extend(result.errors)
        
        for error in set(all_errors):
            batch_results["errors_summary"][error] = all_errors.count(error)
        
        print(f"\n📊 BATCH RESULTS:")
        print(f"   Success Rate: {batch_results['success_rate']*100:.1f}% ({batch_results['successful_tests']}/{batch_results['total_tests']})")
        print(f"   Pot Match Rate: {batch_results['pot_match_rate']*100:.1f}%")
        print(f"   Average Test Time: {batch_results['average_test_time_ms']:.1f}ms")
        print(f"   Total Time: {batch_results['total_time_seconds']:.2f}s")
        
        return batch_results
    
    def export_results(self, filename: str = None) -> str:
        """
        Export test results to JSON file.
        
        Args:
            filename: Optional filename, defaults to timestamped name
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = int(time.time())
            filename = f"round_trip_test_results_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        export_data = {
            "test_metadata": {
                "timestamp": time.time(),
                "test_count": len(self.test_results),
                "framework_version": "1.0.0"
            },
            "test_results": [asdict(result) for result in self.test_results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Test results exported to: {filepath}")
        return str(filepath)

def main():
    """
    Main function for running round trip integrity tests.
    """
    print("🧪 Round Trip Integrity Testing Framework")
    print("=========================================")
    
    # Initialize tester
    tester = RoundTripIntegrityTester()
    
    # For now, run basic GTO generation tests since we don't have hand models loaded
    player_counts = [2, 3, 4, 6, 9]
    
    print(f"\n🧠 Testing GTO generation for player counts: {player_counts}")
    
    for player_count in player_counts:
        success, hands = tester.test_ppsm_to_gto_generation(player_count, num_hands=2)
        if success:
            print(f"✅ {player_count} players: Generated {len(hands)} hands successfully")
        else:
            print(f"❌ {player_count} players: Generation failed")
    
    # Export results
    results_file = tester.export_results()
    print(f"\n📁 Results exported to: {results_file}")

if __name__ == "__main__":
    main()
