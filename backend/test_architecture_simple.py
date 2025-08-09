#!/usr/bin/env python3
"""
Simple architectural test for the new hook-based system.

This demonstrates the debugging principle of identifying which inheritance level fixes belong to.
Run from backend directory: python3 test_architecture_simple.py
"""

def test_inheritance_hierarchy():
    """Test that our inheritance hierarchy works correctly."""
    print("🧪 TESTING INHERITANCE HIERARCHY")
    print("=" * 50)
    
    try:
        # Test FPSM Base
        print("🔧 Testing FPSM Base...")
        from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
        config = GameConfig(num_players=6, big_blind=1.0, small_blind=0.5, starting_stack=100.0)
        base_fpsm = FlexiblePokerStateMachine(config)
        print(f"  ✅ Base FPSM: {type(base_fpsm).__name__}")
        
        # Test FPSM Children
        print("🎓 Testing FPSM Children...")
        from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
        from core.hands_review_poker_state_machine import HandsReviewPokerStateMachine
        from core.gui_models import StrategyData
        
        strategy_data = StrategyData()
        practice_fpsm = PracticeSessionPokerStateMachine(config, strategy_data)
        review_fpsm = HandsReviewPokerStateMachine(config)
        
        print(f"  ✅ Practice FPSM: {type(practice_fpsm).__name__}")
        print(f"  ✅ Review FPSM: {type(review_fpsm).__name__}")
        
        # Verify inheritance
        assert isinstance(practice_fpsm, FlexiblePokerStateMachine)
        assert isinstance(review_fpsm, FlexiblePokerStateMachine)
        assert hasattr(practice_fpsm, 'practice_mode')
        assert hasattr(review_fpsm, 'review_mode')
        print("  ✅ Inheritance hierarchy correct")
        
        # Test RPGW Base
        print("🎨 Testing RPGW Base...")
        from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
        # Can't create without parent widget, but can test class
        assert hasattr(ReusablePokerGameWidget, '_should_show_card')
        assert hasattr(ReusablePokerGameWidget, '_transform_card_data')
        print(f"  ✅ Base RPGW: {ReusablePokerGameWidget.__name__}")
        
        # Test RPGW Children  
        print("🎮 Testing RPGW Children...")
        from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget
        from ui.components.hands_review_poker_widget import HandsReviewPokerWidget
        
        # Verify they inherit from base
        assert issubclass(PracticeSessionPokerWidget, ReusablePokerGameWidget)
        assert issubclass(HandsReviewPokerWidget, ReusablePokerGameWidget)
        print(f"  ✅ Practice Widget: {PracticeSessionPokerWidget.__name__}")
        print(f"  ✅ Review Widget: {HandsReviewPokerWidget.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ HIERARCHY TEST FAILED: {e}")
        import traceback
        print(f"📍 Full trace: {traceback.format_exc()}")
        return False

def test_hook_behavior():
    """Test that hook methods work as intended."""
    print("\n🧪 TESTING HOOK BEHAVIOR")
    print("=" * 50)
    
    try:
        from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
        from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget  
        from ui.components.hands_review_poker_widget import HandsReviewPokerWidget
        
        # Test base hook behavior
        print("🔧 Testing Base Hook Behavior...")
        # We can test the methods even without a widget instance
        base_class = ReusablePokerGameWidget
        
        # Create dummy instances to test hook methods (simplified)
        class TestWidget(ReusablePokerGameWidget):
            def __init__(self):
                # Minimal init for testing
                pass
        
        test_widget = TestWidget()
        
        # Test base behavior
        assert test_widget._should_show_card(0, "As") == True
        assert test_widget._should_show_card(0, "**") == False
        assert test_widget._transform_card_data(0, "As") == "As"
        print("  ✅ Base hooks work correctly")
        
        # Test specialized behavior
        print("🎓 Testing Specialized Hook Behavior...")
        
        class TestPracticeWidget(PracticeSessionPokerWidget):
            def __init__(self):
                pass
        
        class TestReviewWidget(HandsReviewPokerWidget):
            def __init__(self):
                pass
        
        practice_widget = TestPracticeWidget()
        review_widget = TestReviewWidget()
        
        # Test practice session hooks
        # Note: Without state machine, practice widget defaults to base behavior for **
        assert practice_widget._should_show_card(0, "As") == True
        assert practice_widget._should_show_card(0, "**") == False  # No state machine
        print("  ✅ Practice hooks work correctly")
        
        # Test hands review hooks  
        assert review_widget._should_show_card(0, "As") == True
        assert review_widget._should_show_card(0, "**") == True  # Always show in review
        print("  ✅ Review hooks work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ HOOK TEST FAILED: {e}")
        import traceback
        print(f"📍 Full trace: {traceback.format_exc()}")
        return False

def demonstrate_debugging_levels():
    """Demonstrate how to identify which level bugs belong to."""
    print("\n🔍 DEBUGGING LEVEL IDENTIFICATION")
    print("=" * 50)
    
    print("📋 DEBUGGING DECISION TREE:")
    print("")
    
    print("1️⃣ ISSUE: 'Cards not showing properly'")
    print("   🔍 Affects ALL widgets? → Fix in RPGW base class")
    print("   🔍 Affects ONE widget type? → Fix in widget child class")
    print("   🔍 Card visibility logic? → Check _should_show_card hook")
    print("   🔍 Card transformation? → Check _transform_card_data hook")
    print("")
    
    print("2️⃣ ISSUE: 'Game logic broken'")
    print("   🔍 Affects ALL game modes? → Fix in FPSM base class")
    print("   🔍 Affects practice only? → Fix in PracticeSessionPSM")
    print("   🔍 Affects review only? → Fix in HandsReviewPSM")
    print("   🔍 State transitions? → Check FPSM base")
    print("   🔍 Action validation? → Check FPSM base")
    print("")
    
    print("3️⃣ ISSUE: 'Bot behavior wrong'")
    print("   🔍 Only in practice mode? → Fix in PracticeSessionPSM")
    print("   🔍 GTO strategy issue? → Check strategy_engine integration")
    print("   🔍 Auto-play logic? → Check bot scheduling methods")
    print("")
    
    print("4️⃣ ISSUE: 'Action buttons not working'")
    print("   🔍 Only in practice session? → Fix in PracticeSessionPW")
    print("   🔍 Button state management? → Check _enable/_disable methods")
    print("   🔍 Human player detection? → Check _is_human_player logic")
    print("")
    
    print("✅ PRINCIPLE: Always fix at the MOST SPECIFIC level that solves the problem")
    print("🚫 AVOID: Fixing child-specific issues in base classes")
    print("🚫 AVOID: Duplicating base functionality in children")
    print("✅ USE: Proper hook overrides for specialized behavior")

def main():
    """Run architectural tests and demonstrate debugging principles."""
    print("🏗️ NEW HOOK-BASED ARCHITECTURE TEST")
    print("🎯 Demonstrating proper debugging level identification")
    print("=" * 70)
    
    # Run tests
    hierarchy_ok = test_inheritance_hierarchy()
    hooks_ok = test_hook_behavior()
    
    # Show debugging principles
    demonstrate_debugging_levels()
    
    # Summary
    print("\n📊 ARCHITECTURE TEST RESULTS")
    print("=" * 50)
    
    hierarchy_status = "✅ PASS" if hierarchy_ok else "❌ FAIL"
    hooks_status = "✅ PASS" if hooks_ok else "❌ FAIL"
    
    print(f"{hierarchy_status} Inheritance Hierarchy")
    print(f"{hooks_status} Hook Behavior")
    
    overall = "✅ EXCELLENT" if (hierarchy_ok and hooks_ok) else "❌ NEEDS FIXES"
    print(f"\n🎯 OVERALL ARCHITECTURE: {overall}")
    
    if hierarchy_ok and hooks_ok:
        print("\n🎉 ARCHITECTURE SUCCESS!")
        print("✅ Both Practice Session and Hands Review use clean hook-based design")
        print("✅ Proper inheritance hierarchy maintained")
        print("✅ Debugging framework ready for identifying fix levels")
        print("✅ Ready for production testing!")
    
    return hierarchy_ok and hooks_ok

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
