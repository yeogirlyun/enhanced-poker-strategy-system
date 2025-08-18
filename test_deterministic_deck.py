#!/usr/bin/env python3
"""
Test Deterministic Deck Injection

This script tests that our composition-based HandsReviewSessionStateMachine
correctly injects a deterministic deck for hands review.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_deterministic_deck():
    """Test the deterministic deck injection."""
    print("🧪 Testing Deterministic Deck Injection...")
    
    try:
        # Import our composition-based state machine
        from core.hands_review_session_state_machine import HandsReviewSessionStateMachine
        from core.flexible_poker_state_machine import GameConfig
        
        # Create a test hand with board cards
        test_hand_data = {
            "metadata": {
                "small_blind": 5,
                "big_blind": 10
            },
            "board_cards": ["Ah", "Kh", "Qh", "Jh", "Th"],  # Royal flush board
            "streets": {
                "PREFLOP": {
                    "actions": [
                        {"action": "RAISE", "amount": 20, "actor_uid": "seat1"}
                    ]
                },
                "FLOP": {
                    "actions": [
                        {"action": "BET", "amount": 30, "actor_uid": "seat1"}
                    ]
                }
            }
        }
        
        # Create session
        config = GameConfig(num_players=6)
        session = HandsReviewSessionStateMachine(config)
        
        # Test 1: Set preloaded hand data
        print("✅ Test 1: Setting preloaded hand data...")
        session.set_preloaded_hand_data(test_hand_data)
        
        # Test 2: Start session (this should trigger deterministic deck injection)
        print("✅ Test 2: Starting session...")
        success = session.start_session()
        
        if success:
            print("   ✓ Session started successfully")
            
            # Test 3: Check if deterministic deck was injected
            print("✅ Test 3: Checking deterministic deck...")
            
            if hasattr(session.fpsm, 'game_state') and hasattr(session.fpsm.game_state, 'deck'):
                deck = session.fpsm.game_state.deck
                print(f"   ✓ Deck length: {len(deck)}")
                print(f"   ✓ First 5 cards (should be board): {deck[:5]}")
                
                # Verify board cards are at the top
                expected_board = ["Ah", "Kh", "Qh", "Jh", "Th"]
                if deck[:5] == expected_board:
                    print("   ✓ SUCCESS: Board cards correctly placed at deck top!")
                else:
                    print(f"   ❌ FAILED: Board cards mismatch. Expected: {expected_board}, Got: {deck[:5]}")
                    return False
                
                # Test 4: Check if skip_shuffle flag was set
                print("✅ Test 4: Checking skip_shuffle flag...")
                if getattr(session.fpsm, 'skip_shuffle', False):
                    print("   ✓ SUCCESS: skip_shuffle flag set correctly!")
                else:
                    print("   ❌ FAILED: skip_shuffle flag not set")
                    return False
                
            else:
                print("   ❌ FAILED: No game state or deck found")
                return False
                
        else:
            print("   ❌ FAILED: Session failed to start")
            return False
        
        print("\n🎉 ALL TESTS PASSED! Deterministic deck injection is working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deterministic_deck()
    if success:
        print("\n🚀 Ready to test hands review validator!")
    else:
        print("\n💥 Deterministic deck test failed!")
        sys.exit(1)
