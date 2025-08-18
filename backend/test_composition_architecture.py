#!/usr/bin/env python3
"""
Test Composition Architecture Implementation

This script tests that the new composition architecture works correctly:
- BotSessionStateMachine uses composition with FPSM
- GTOBotSession and HandsReviewBotSession inherit from BotSessionStateMachine
- All poker operations delegate to FPSM correctly
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_composition_architecture():
    """Test the composition architecture implementation."""
    print("🧪 Testing Composition Architecture Implementation")
    print("=" * 60)
    
    try:
        # Import the classes
        from core.bot_session_state_machine import (
            BotSessionStateMachine, 
            GTOBotSession, 
            HandsReviewBotSession
        )
        from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
        from core.decision_engine import GTODecisionEngine
        
        print("✅ SUCCESS: All classes imported successfully")
        
        # Test 1: Check if BotSessionStateMachine inherits from FPSM
        print("\n🔍 Test 1: Inheritance Check")
        if issubclass(BotSessionStateMachine, FlexiblePokerStateMachine):
            print("   ❌ FAIL: BotSessionStateMachine still inherits from FPSM")
            return False
        else:
            print("   ✅ PASS: BotSessionStateMachine does NOT inherit from FPSM")
        
        # Test 2: Check if BotSessionStateMachine has FPSM as member
        print("\n🔍 Test 2: Composition Check")
        config = GameConfig(num_players=6, small_blind=1.0, big_blind=2.0)
        decision_engine = GTODecisionEngine(6)
        
        bot_session = BotSessionStateMachine(config, decision_engine)
        
        if hasattr(bot_session, 'fpsm'):
            print("   ✅ PASS: BotSessionStateMachine has 'fpsm' member")
            if isinstance(bot_session.fpsm, FlexiblePokerStateMachine):
                print("   ✅ PASS: 'fpsm' is instance of FlexiblePokerStateMachine")
            else:
                print("   ❌ FAIL: 'fpsm' is not instance of FlexiblePokerStateMachine")
                return False
        else:
            print("   ❌ FAIL: BotSessionStateMachine missing 'fpsm' member")
            return False
        
        # Test 3: Check if subclasses inherit from BotSessionStateMachine
        print("\n🔍 Test 3: Subclass Inheritance Check")
        if issubclass(GTOBotSession, BotSessionStateMachine):
            print("   ✅ PASS: GTOBotSession inherits from BotSessionStateMachine")
        else:
            print("   ❌ FAIL: GTOBotSession does not inherit from BotSessionStateMachine")
            return False
        
        if issubclass(HandsReviewBotSession, BotSessionStateMachine):
            print("   ✅ PASS: HandsReviewBotSession inherits from BotSessionStateMachine")
        else:
            print("   ❌ FAIL: HandsReviewBotSession does not inherit from BotSessionStateMachine")
            return False
        
        # Test 4: Check delegation to FPSM
        print("\n🔍 Test 4: FPSM Delegation Check")
        try:
            # Test that we can call FPSM methods through delegation
            game_info = bot_session.get_game_info()
            print("   ✅ PASS: Can call get_game_info() through delegation")
            
            display_state = bot_session.get_display_state()
            print("   ✅ PASS: Can call get_display_state() through delegation")
            
        except Exception as e:
            print(f"   ❌ FAIL: Error calling delegated methods: {e}")
            return False
        
        # Test 5: Check that subclasses can be instantiated
        print("\n🔍 Test 5: Subclass Instantiation Check")
        try:
            gto_session = GTOBotSession(config)
            print("   ✅ PASS: GTOBotSession instantiated successfully")
            
            hands_review_session = HandsReviewBotSession(config, None)
            print("   ✅ PASS: HandsReviewBotSession instantiated successfully")
            
        except Exception as e:
            print(f"   ❌ FAIL: Error instantiating subclasses: {e}")
            return False
        
        print("\n🎉 ALL TESTS PASSED! Composition architecture is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_composition_architecture()
    sys.exit(0 if success else 1)
