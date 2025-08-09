#!/usr/bin/env python3
"""
Test script for the new hook-based architecture.

This script tests both Practice Session and Hands Review widgets
while demonstrating proper debugging practices for identifying
which inheritance level issues belong to.

Run from backend directory: cd backend && python3 ../test_new_architecture.py
"""

import sys
import os
import traceback
from datetime import datetime

# Ensure we're running from the backend directory
if not os.path.exists('core') or not os.path.exists('ui'):
    print("❌ ERROR: This script must be run from the backend directory")
    print("💡 SOLUTION: cd backend && python3 ../test_new_architecture.py")
    sys.exit(1)

# Test imports and identify where any issues occur
def test_imports():
    """Test all imports and identify the exact failure point."""
    print("🧪 TESTING IMPORTS - Identifying Inheritance Levels")
    print("=" * 60)
    
    try:
        print("🔧 Testing FPSM Base...")
        from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
        print("  ✅ FPSM Base import successful")
        
        print("🎓 Testing FPSM Children...")
        from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
        print("  ✅ PracticeSessionPokerStateMachine import successful")
        
        from core.hands_review_poker_state_machine import HandsReviewPokerStateMachine
        print("  ✅ HandsReviewPokerStateMachine import successful")
        
        print("🎨 Testing RPGW Base...")
        from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
        print("  ✅ RPGW Base import successful")
        
        print("🎮 Testing RPGW Children...")
        from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget
        print("  ✅ PracticeSessionPokerWidget import successful")
        
        from ui.components.hands_review_poker_widget import HandsReviewPokerWidget
        print("  ✅ HandsReviewPokerWidget import successful")
        
        print("🎯 Testing UI Integration...")
        from ui.practice_session_ui import PracticeSessionUI
        print("  ✅ PracticeSessionUI import successful")
        
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        print("  ✅ FPSMHandsReviewPanel import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ IMPORT FAILED at {traceback.format_exc()}")
        print("\n🔍 DEBUGGING GUIDANCE:")
        print("- Check which inheritance level the error occurs in")
        print("- Fix at the appropriate level (base vs child)")
        return False

def test_hook_system():
    """Test the hook system to ensure proper inheritance behavior."""
    print("\n🧪 TESTING HOOK SYSTEM")
    print("=" * 60)
    
    try:
        from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
        from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget
        from ui.components.hands_review_poker_widget import HandsReviewPokerWidget
        
        # Test base class hooks (should have default behavior)
        print("🔧 Testing RPGW Base Hooks...")
        base_widget = ReusablePokerGameWidget(None)
        
        # Test default hook behavior
        assert base_widget._should_show_card(0, "As") == True
        assert base_widget._should_show_card(0, "**") == False
        assert base_widget._transform_card_data(0, "As") == "As"
        print("  ✅ Base hooks working correctly")
        
        # Test child class hooks (should have specialized behavior)
        print("🎓 Testing Practice Session Hooks...")
        practice_widget = PracticeSessionPokerWidget(None)
        
        # Practice should show human cards but hide bot cards for **
        assert practice_widget._should_show_card(0, "As") == True  # Human card
        assert practice_widget._should_show_card(0, "**") == False  # Bot card (no state machine)
        print("  ✅ Practice hooks working correctly")
        
        print("🎯 Testing Hands Review Hooks...")
        review_widget = HandsReviewPokerWidget(None)
        
        # Hands review should always show cards
        assert review_widget._should_show_card(0, "As") == True
        assert review_widget._should_show_card(0, "**") == True  # Always show in review
        print("  ✅ Hands review hooks working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ HOOK TEST FAILED: {e}")
        print(f"📍 Error trace: {traceback.format_exc()}")
        print("\n🔍 DEBUGGING GUIDANCE:")
        print("- If base hooks fail → Fix in RPGW base class")
        print("- If child hooks fail → Fix in specific child class")
        print("- If inheritance is broken → Check hook method signatures")
        return False

def test_state_machine_hierarchy():
    """Test the state machine inheritance hierarchy."""
    print("\n🧪 TESTING STATE MACHINE HIERARCHY")
    print("=" * 60)
    
    try:
        from core.flexible_poker_state_machine import GameConfig
        from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
        from core.hands_review_poker_state_machine import HandsReviewPokerStateMachine
        from core.gui_models import StrategyData
        
        # Create test configuration
        config = GameConfig(
            num_players=6,
            big_blind=1.0,
            small_blind=0.5,
            starting_stack=100.0
        )
        
        # Test practice session state machine
        print("🎓 Testing PracticeSessionPokerStateMachine...")
        strategy_data = StrategyData()  # Default strategy
        practice_psm = PracticeSessionPokerStateMachine(config, strategy_data)
        
        # Check practice-specific properties
        assert hasattr(practice_psm, 'practice_mode')
        assert practice_psm.practice_mode == True
        print("  ✅ Practice PSM initialized correctly")
        
        # Test hands review state machine  
        print("🎯 Testing HandsReviewPokerStateMachine...")
        review_psm = HandsReviewPokerStateMachine(config)
        
        # Check review-specific properties
        assert hasattr(review_psm, 'review_mode')
        assert review_psm.review_mode == True
        print("  ✅ Hands Review PSM initialized correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ STATE MACHINE TEST FAILED: {e}")
        print(f"📍 Error trace: {traceback.format_exc()}")
        print("\n🔍 DEBUGGING GUIDANCE:")
        print("- If config fails → Fix in FPSM base class")
        print("- If child PSM fails → Fix in specific child PSM class")
        print("- If inheritance broken → Check constructor signatures")
        return False

def main():
    """Run all architecture tests with proper debugging guidance."""
    print("🏗️ TESTING NEW HOOK-BASED ARCHITECTURE")
    print("🎯 Focus: Identifying correct inheritance level for fixes")
    print(f"📅 Test Time: {datetime.now()}")
    print("=" * 60)
    
    # Track test results
    results = []
    
    # Test each level independently
    results.append(("Imports", test_imports()))
    results.append(("Hook System", test_hook_system()))
    results.append(("State Machine Hierarchy", test_state_machine_hierarchy()))
    
    # Report results
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n🎯 ARCHITECTURE HEALTH:", "✅ EXCELLENT" if all_passed else "❌ NEEDS FIXES")
    
    if not all_passed:
        print("\n🔧 DEBUGGING NEXT STEPS:")
        print("1. Review failed tests above")
        print("2. Identify which inheritance level the issue belongs to")
        print("3. Apply fixes at the correct abstraction level")
        print("4. Re-run tests to verify fixes")
        print("\n📚 See ARCHITECTURAL_DEBUGGING_GUIDE.md for detailed guidance")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
