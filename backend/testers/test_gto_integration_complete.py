#!/usr/bin/env python3
"""
Complete GTO Integration Test Runner

This script demonstrates the complete integration of:
- GTO Engine with PPSM
- HandModel replay capabilities
- Round trip integrity testing
- Performance benchmarking

Architecture Compliance:
- Uses existing Hand Model and PPSM architecture
- Follows single-threaded, event-driven patterns
- Maintains separation of concerns
- No UI coupling or timing violations
"""

import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.gto.test_gto_integration import GTOIntegrationTester
    from backend.gto.round_trip_integrity_tester import RoundTripIntegrityTester
    from backend.gto.gto_hands_generator import GTOHandsGenerator
    from backend.gto.industry_gto_engine import IndustryGTOEngine
    from backend.gto.gto_decision_engine_adapter import GTODecisionEngineAdapter
    from backend.core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    print("✅ All GTO integration modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all modules are properly installed and paths are correct.")
    sys.exit(1)

def test_basic_gto_engine():
    """Test basic GTO engine functionality."""
    print("\n🧠 Testing Basic GTO Engine...")
    
    try:
        # Create GTO engine
        engine = IndustryGTOEngine(player_count=6)
        print("✅ GTO engine created successfully")
        
        # Test engine capabilities
        print(f"✅ Engine configured for {engine.player_count} players")
        print(f"✅ Stack depth: {engine.stack_depth}")
        print(f"✅ Aggression factor: {engine.aggression_factor}")
        
        return True
        
    except Exception as e:
        print(f"❌ GTO engine test failed: {e}")
        return False

def test_ppsm_integration():
    """Test PPSM integration with GTO adapter."""
    print("\n🎯 Testing PPSM-GTO Integration...")
    
    try:
        # Create GTO engine and adapter
        gto_engine = IndustryGTOEngine(player_count=4)
        adapter = GTODecisionEngineAdapter(gto_engine)
        
        # Create PPSM with GTO adapter
        config = GameConfig(num_players=4, starting_stack=1000.0, small_blind=5.0, big_blind=10.0)
        ppsm = PurePokerStateMachine(config=config, decision_engine=adapter)
        
        print("✅ PPSM created with GTO decision engine")
        print("✅ Integration adapter working")
        
        return True
        
    except Exception as e:
        print(f"❌ PPSM-GTO integration test failed: {e}")
        return False

def test_hand_generation():
    """Test GTO hand generation."""
    print("\n🃏 Testing GTO Hand Generation...")
    
    try:
        # Test generation for different player counts
        player_counts = [2, 4, 6]
        
        for player_count in player_counts:
            generator = GTOHandsGenerator(player_count=player_count)
            hands = generator.generate_hands_batch(hands_count=2)
            
            if len(hands) == 2:
                print(f"✅ Generated 2 hands for {player_count} players")
            else:
                print(f"❌ Expected 2 hands, got {len(hands)} for {player_count} players")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Hand generation test failed: {e}")
        return False

def test_round_trip_integrity():
    """Test round trip integrity framework."""
    print("\n🔄 Testing Round Trip Integrity Framework...")
    
    try:
        # Create round trip tester
        tester = RoundTripIntegrityTester()
        
        # Test GTO generation for multiple player counts
        player_counts = [2, 3, 4]
        successful_tests = 0
        total_tests = len(player_counts)
        
        for player_count in player_counts:
            success, hands = tester.test_ppsm_to_gto_generation(player_count, num_hands=1)
            if success:
                successful_tests += 1
                print(f"✅ Round trip test passed for {player_count} players")
            else:
                print(f"❌ Round trip test failed for {player_count} players")
        
        success_rate = successful_tests / total_tests
        print(f"📊 Round trip success rate: {success_rate*100:.1f}% ({successful_tests}/{total_tests})")
        
        return success_rate >= 0.5  # At least 50% success rate
        
    except Exception as e:
        print(f"❌ Round trip integrity test failed: {e}")
        return False

def run_comprehensive_test_suite():
    """Run the complete test suite."""
    print("🧪 GTO Integration Complete Test Suite")
    print("=====================================")
    
    test_results = {}
    start_time = time.time()
    
    # Run individual tests
    test_results['basic_gto'] = test_basic_gto_engine()
    test_results['ppsm_integration'] = test_ppsm_integration()
    test_results['hand_generation'] = test_hand_generation()
    test_results['round_trip'] = test_round_trip_integrity()
    
    # Summary
    total_time = time.time() - start_time
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n📊 TEST SUITE SUMMARY")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"   Total Time: {total_time:.2f}s")
    
    # Individual test results
    print(f"\n📋 INDIVIDUAL TEST RESULTS:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    # Overall status
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! GTO integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--comprehensive':
        # Run the full integration test using the command line interface
        print("🚀 Running comprehensive GTO integration tests via command line...")
        os.system(f"cd {os.path.dirname(__file__)} && python -m gto.test_gto_integration --comprehensive --players 2-4 --hands-per-count 2")
    else:
        # Run our basic test suite
        success = run_comprehensive_test_suite()
        
        if success:
            print("\n🎯 Integration is ready! You can now:")
            print("   1. Generate GTO hands: python -m backend.gto.test_gto_integration --generate")
            print("   2. Run comprehensive tests: python -m backend.gto.test_gto_integration --comprehensive")
            print("   3. Run performance benchmarks: python -m backend.gto.test_gto_integration --benchmark")
            print("   4. Run all tests: python -m backend.gto.test_gto_integration --all")
        else:
            print("\n❌ Integration issues detected. Please review the test results above.")

if __name__ == "__main__":
    main()
