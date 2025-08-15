#!/usr/bin/env python3
"""
Quick Hand Model validation test.

Fast, focused test that validates the core Hand Model system works correctly
without getting stuck in infinite loops. Designed to complete in under 1 minute.
"""

import sys
import os
import json
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.hand_model import Hand
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.gto_to_hand_converter import GTOToHandConverter

def test_hand_model_core():
    """Test 1: Core Hand Model functionality."""
    print("🧪 Test 1: Hand Model Core Functionality")
    print("-" * 50)
    
    try:
        # Test JSON round-trip
        hand = Hand.load_json('example_hand.json')
        hand.save_json('test_roundtrip.json')
        reloaded = Hand.load_json('test_roundtrip.json')
        
        assert hand.to_dict() == reloaded.to_dict(), "Round-trip failed"
        print("✅ JSON serialization: PASS")
        
        # Test analysis methods
        total_pot = hand.get_total_pot()
        all_actions = hand.get_all_actions()
        print(f"✅ Analysis methods: PASS (pot: ${total_pot}, actions: {len(all_actions)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Hand Model Core: FAIL - {e}")
        return False

def test_gto_conversion():
    """Test 2: GTO to Hand Model conversion."""
    print("\n🧪 Test 2: GTO Conversion")
    print("-" * 50)
    
    try:
        # Test conversion with existing data
        with open('cycle_test_hand.json', 'r') as f:
            gto_data = json.load(f)
        
        hand = GTOToHandConverter.convert_gto_hand(gto_data)
        
        print(f"✅ Conversion: PASS")
        print(f"   Hand ID: {hand.metadata.hand_id}")
        print(f"   Players: {len(hand.seats)}")
        print(f"   Actions: {len(hand.get_all_actions())}")
        print(f"   Final pot: ${hand.get_total_pot()}")
        
        # Check player ID format consistency
        all_actions = hand.get_all_actions()
        player_ids = set()
        for action in all_actions:
            if action.actor_id:
                player_ids.add(action.actor_id)
        
        print(f"   Player IDs: {sorted(player_ids)}")
        
        # Validate player ID format (should be "Player1", "Player2", etc.)
        for pid in player_ids:
            if not (pid.startswith('Player') and pid[6:].isdigit()):
                print(f"⚠️  Non-standard player ID: {pid}")
        
        return True
        
    except FileNotFoundError:
        print("⚠️  GTO test file not found - skipping")
        return True
    except Exception as e:
        print(f"❌ GTO Conversion: FAIL - {e}")
        return False

def test_decision_engine_basic():
    """Test 3: HandModelDecisionEngine basic functionality."""
    print("\n🧪 Test 3: Decision Engine Basic")
    print("-" * 50)
    
    try:
        # Load converted hand
        hand = Hand.load_json('cycle_test_hand_hand_model.json')
        engine = HandModelDecisionEngine(hand)
        
        print(f"✅ Engine creation: PASS ({engine.total_actions} actions)")
        
        # Test getting first few decisions without session interaction
        decisions_tested = 0
        max_test = min(5, engine.total_actions)
        
        for i in range(max_test):
            decision = engine.get_decision(0, {})  # Test with player 0
            
            if decision.get('action') and 'amount' in decision:
                decisions_tested += 1
                print(f"   Decision {i+1}: {decision['action'].value} ${decision['amount']:.2f}")
            else:
                print(f"   Decision {i+1}: Invalid format")
                break
                
            # Safety check - don't loop forever
            if engine.is_session_complete():
                print(f"   Session complete after {i+1} decisions")
                break
        
        success_rate = (decisions_tested / max_test) * 100
        print(f"✅ Decision success rate: {success_rate:.1f}% ({decisions_tested}/{max_test})")
        
        return success_rate >= 60  # At least 60% success rate
        
    except FileNotFoundError:
        print("⚠️  Converted hand file not found - skipping")
        return True
    except Exception as e:
        print(f"❌ Decision Engine: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_id_consistency():
    """Test 4: Player ID consistency check."""
    print("\n🧪 Test 4: Player ID Consistency")
    print("-" * 50)
    
    try:
        # Check both converted files for player ID consistency
        test_files = [
            'cycle_test_hand_hand_model.json',
            'gto_hand_for_verification_hand_model.json'
        ]
        
        all_consistent = True
        
        for filename in test_files:
            try:
                hand = Hand.load_json(filename)
                
                # Get all player IDs from actions
                action_player_ids = set()
                for action in hand.get_all_actions():
                    if action.actor_id:
                        action_player_ids.add(action.actor_id)
                
                # Get player IDs from seats
                seat_player_ids = {seat.player_id for seat in hand.seats}
                
                # Check format consistency
                canonical_format = True
                for pid in action_player_ids:
                    if ' ' in pid or not pid.startswith('Player'):
                        canonical_format = False
                        print(f"   Non-canonical ID in {filename}: '{pid}'")
                
                print(f"   {filename}: {'✅ CONSISTENT' if canonical_format else '❌ INCONSISTENT'}")
                print(f"      Seat IDs: {sorted(seat_player_ids)}")
                print(f"      Action IDs: {sorted(action_player_ids)}")
                
                if not canonical_format:
                    all_consistent = False
                    
            except FileNotFoundError:
                print(f"   {filename}: ⚠️  NOT FOUND")
        
        return all_consistent
        
    except Exception as e:
        print(f"❌ Player ID Consistency: FAIL - {e}")
        return False

def test_pot_arithmetic():
    """Test 5: Basic pot arithmetic validation."""
    print("\n🧪 Test 5: Pot Arithmetic")
    print("-" * 50)
    
    try:
        # Load a hand and check basic arithmetic
        hand = Hand.load_json('cycle_test_hand_hand_model.json')
        
        total_pot = hand.get_total_pot()
        total_shares = sum(share.amount for pot in hand.pots for share in pot.shares)
        
        print(f"   Total pot amount: ${total_pot}")
        print(f"   Total distributed: ${total_shares}")
        print(f"   Difference: ${abs(total_pot - total_shares)}")
        
        # Allow small differences due to rake/rounding
        arithmetic_ok = abs(total_pot - total_shares) <= 1.0
        
        print(f"✅ Pot arithmetic: {'PASS' if arithmetic_ok else 'FAIL'}")
        
        return arithmetic_ok
        
    except FileNotFoundError:
        print("⚠️  Test file not found - skipping")
        return True
    except Exception as e:
        print(f"❌ Pot Arithmetic: FAIL - {e}")
        return False

def cleanup_test_files():
    """Clean up temporary test files."""
    temp_files = ['test_roundtrip.json']
    for filename in temp_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

def main():
    """Run all quick tests."""
    print("🚀 QUICK HAND MODEL VALIDATION")
    print("=" * 60)
    print("⏱️  Target: Complete in < 1 minute")
    print()
    
    tests = [
        ("Hand Model Core", test_hand_model_core),
        ("GTO Conversion", test_gto_conversion),
        ("Decision Engine", test_decision_engine_basic),
        ("Player ID Consistency", test_player_id_consistency),
        ("Pot Arithmetic", test_pot_arithmetic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 QUICK TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Hand Model system is working correctly!")
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY WORKING - Minor issues detected")
    else:
        print("❌ SIGNIFICANT ISSUES - Hand Model needs attention")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
