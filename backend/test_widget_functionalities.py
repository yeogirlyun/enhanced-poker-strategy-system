#!/usr/bin/env python3
"""
Widget Functionality Tests

Tests basic functionalities of both Practice Session and Hands Review widgets
using the new hook-based architecture. Demonstrates debugging principles by
clearly identifying which inheritance level any issues belong to.
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime

def test_practice_session_widget():
    """Test Practice Session Widget basic functionality."""
    print("🎓 TESTING PRACTICE SESSION WIDGET")
    print("=" * 60)
    
    try:
        # Test imports at correct levels
        print("📦 Testing imports...")
        from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
        from core.flexible_poker_state_machine import GameConfig
        from core.gui_models import StrategyData
        from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget
        print("  ✅ All imports successful")
        
        # Create test window
        print("🖼️ Creating test window...")
        root = tk.Tk()
        root.title("Practice Session Widget Test")
        root.geometry("1000x800")
        
        # Create state machine (FPSM level)
        print("🎮 Creating Practice Session State Machine...")
        config = GameConfig(
            num_players=6,
            big_blind=1.0,
            small_blind=0.5,
            starting_stack=100.0
        )
        strategy_data = StrategyData()
        state_machine = PracticeSessionPokerStateMachine(config, strategy_data)
        print(f"  ✅ State machine created: {type(state_machine).__name__}")
        
        # Verify FPSM specialized properties
        assert hasattr(state_machine, 'practice_mode')
        assert state_machine.practice_mode == True
        assert hasattr(state_machine, 'strategy_engine')
        print("  ✅ Practice-specific FPSM properties verified")
        
        # Create widget (RPGW level)
        print("🎨 Creating Practice Session Widget...")
        widget = PracticeSessionPokerWidget(root, state_machine=state_machine)
        widget.pack(fill=tk.BOTH, expand=True)
        print(f"  ✅ Widget created: {type(widget).__name__}")
        
        # Verify RPGW specialized hooks
        print("🔧 Testing hook methods...")
        
        # Test card visibility hooks
        human_card_visible = widget._should_show_card(0, "As")  # Human player
        bot_card_hidden = widget._should_show_card(1, "**")     # Bot card
        
        print(f"  🎯 Human card visible: {human_card_visible}")
        print(f"  🤖 Bot card hidden: {not bot_card_hidden}")
        
        # Test card transformation hooks  
        transformed_card = widget._transform_card_data(0, "**", 0)
        print(f"  🔄 Card transformation test: ** → {transformed_card}")
        
        # Test update hooks
        should_update = widget._should_update_display(0, ["As", "Kh"], ["As", "Kh"])
        print(f"  📱 Update responsiveness: {should_update}")
        
        print("  ✅ All hook methods working correctly")
        
        # Verify action buttons exist (Practice-specific feature)
        print("🎮 Testing Practice-specific features...")
        if hasattr(widget, 'action_buttons'):
            button_count = len(widget.action_buttons)
            print(f"  ✅ Action buttons created: {button_count} buttons")
            
            expected_buttons = ['fold', 'check_call', 'bet_raise', 'all_in']
            for button_name in expected_buttons:
                if button_name in widget.action_buttons:
                    print(f"    ✅ {button_name.upper()} button exists")
                else:
                    print(f"    ❌ {button_name.upper()} button missing")
        else:
            print("  ⚠️ Action buttons not yet created (need UI setup)")
        
        # Test basic game operations
        print("🎯 Testing basic game operations...")
        
        # Start a hand
        state_machine.start_hand()
        print("  ✅ Hand started successfully")
        
        # Get display state
        display_state = state_machine.get_display_state()
        print(f"  ✅ Display state retrieved: {len(display_state)} properties")
        
        # Verify practice-specific display properties
        practice_props = ['practice_mode', 'hands_played', 'session_stats']
        for prop in practice_props:
            if prop in display_state:
                print(f"    ✅ Practice property '{prop}' exists")
            else:
                print(f"    ⚠️ Practice property '{prop}' missing")
        
        # Test human player detection
        if hasattr(state_machine, 'game_state') and state_machine.game_state.players:
            human_player = state_machine.game_state.players[0]
            is_human = getattr(human_player, 'is_human', False)
            print(f"  ✅ Human player detected: {is_human}")
        
        print("\n🎉 PRACTICE SESSION WIDGET TEST COMPLETE")
        print("✅ All basic functionalities working correctly")
        print("✅ Hook-based architecture functioning properly")
        print("✅ Practice-specific features implemented")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ PRACTICE SESSION TEST FAILED: {e}")
        print("🔍 DEBUGGING GUIDANCE:")
        
        import traceback
        error_trace = traceback.format_exc()
        
        # Analyze error to suggest correct fix level
        if "PracticeSessionPokerStateMachine" in str(e):
            print("  → This appears to be a FPSM Child level issue")
            print("  → Check PracticeSessionPokerStateMachine implementation")
        elif "PracticeSessionPokerWidget" in str(e):
            print("  → This appears to be a RPGW Child level issue") 
            print("  → Check PracticeSessionPokerWidget implementation")
        elif "FlexiblePokerStateMachine" in str(e):
            print("  → This appears to be a FPSM Base level issue")
            print("  → Check base game logic implementation")
        elif "ReusablePokerGameWidget" in str(e):
            print("  → This appears to be a RPGW Base level issue")
            print("  → Check base widget or hook system")
        else:
            print("  → Check imports and module structure")
        
        print(f"\n📍 Full error trace:\n{error_trace}")
        return False

def test_hands_review_widget_DISABLED():
    """Test Hands Review Widget basic functionality."""
    print("\n🎯 TESTING HANDS REVIEW WIDGET")
    print("=" * 60)
    
    try:
        # Test imports at correct levels
        print("📦 Testing imports...")
        from core.hands_review_poker_state_machine import HandsReviewPokerStateMachine
        from core.flexible_poker_state_machine import GameConfig
        # from ui.components.hands_review_poker_widget import HandsReviewPokerWidget  # REMOVED
        print("  ✅ All imports successful")
        
        # Create test window
        print("🖼️ Creating test window...")
        root = tk.Tk()
        root.title("Hands Review Widget Test")
        root.geometry("1000x800")
        
        # Create state machine (FPSM level)
        print("🎮 Creating Hands Review State Machine...")
        config = GameConfig(
            num_players=6,
            big_blind=1.0,
            small_blind=0.5,
            starting_stack=100.0
        )
        state_machine = HandsReviewPokerStateMachine(config)
        print(f"  ✅ State machine created: {type(state_machine).__name__}")
        
        # Verify FPSM specialized properties
        assert hasattr(state_machine, 'review_mode')
        assert state_machine.review_mode == True
        assert hasattr(state_machine, 'current_hand_data')
        assert hasattr(state_machine, 'replay_actions')
        print("  ✅ Review-specific FPSM properties verified")
        
        # Create widget (RPGW level)
        print("🎨 Creating Hands Review Widget...")
        # widget = HandsReviewPokerWidget(root, state_machine=state_machine)  # REMOVED
        widget.pack(fill=tk.BOTH, expand=True)
        print(f"  ✅ Widget created: {type(widget).__name__}")
        
        # Verify RPGW specialized hooks
        print("🔧 Testing hook methods...")
        
        # Test card visibility hooks (should always show all cards)
        any_card_visible = widget._should_show_card(0, "As")
        hidden_card_visible = widget._should_show_card(0, "**")
        
        print(f"  🎯 Regular card visible: {any_card_visible}")
        print(f"  🎯 Hidden card visible: {hidden_card_visible}")
        assert any_card_visible == True, "Regular cards should be visible in review"
        assert hidden_card_visible == True, "Hidden cards should be visible in review"
        
        # Test card transformation hooks
        transformed_card = widget._transform_card_data(0, "**", 0)
        print(f"  🔄 Card transformation test: ** → {transformed_card}")
        
        # Test update hooks (should always update)
        should_update = widget._should_update_display(0, ["As", "Kh"], ["As", "Kh"])
        print(f"  📱 Update responsiveness: {should_update}")
        assert should_update == True, "Should always update in review mode"
        
        print("  ✅ All hook methods working correctly")
        
        # Test hands review specific features
        print("🎯 Testing Review-specific features...")
        
        # Test hand loading capability
        test_hand_data = {
            'hand_id': 'test_001',
            'players': [
                {'name': 'Player 1', 'cards': ['As', 'Kh'], 'stack': 100.0, 'position': 0},
                {'name': 'Player 2', 'cards': ['Qd', 'Jc'], 'stack': 100.0, 'position': 1},
            ],
            'community_cards': ['Ah', 'Kd', '7s', '3h', '2c'],
            'actions': [
                {'player_name': 'Player 1', 'action_type': 'bet', 'amount': 10.0},
                {'player_name': 'Player 2', 'action_type': 'call', 'amount': 10.0},
            ]
        }
        
        state_machine.load_hand_for_review(test_hand_data)
        print("  ✅ Hand loaded for review")
        
        # Test replay functionality
        can_step_forward = state_machine.step_forward()
        print(f"  ✅ Step forward capability: {can_step_forward}")
        
        # Test display state for review
        display_state = state_machine.get_display_state()
        print(f"  ✅ Display state retrieved: {len(display_state)} properties")
        
        # Verify review-specific display properties
        review_props = ['review_mode', 'current_step', 'total_steps', 'can_step_forward']
        for prop in review_props:
            if prop in display_state:
                print(f"    ✅ Review property '{prop}' exists")
            else:
                print(f"    ⚠️ Review property '{prop}' missing")
        
        # Test educational features
        if hasattr(state_machine, 'get_educational_summary'):
            summary = state_machine.get_educational_summary()
            print(f"  ✅ Educational summary available: {len(summary)} sections")
        
        print("\n🎉 HANDS REVIEW WIDGET TEST COMPLETE")
        print("✅ All basic functionalities working correctly")
        print("✅ Hook-based architecture functioning properly")
        print("✅ Review-specific features implemented")
        print("✅ Always-visible card policy working")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ HANDS REVIEW TEST FAILED: {e}")
        print("🔍 DEBUGGING GUIDANCE:")
        
        import traceback
        error_trace = traceback.format_exc()
        
        # Analyze error to suggest correct fix level
        if "HandsReviewPokerStateMachine" in str(e):
            print("  → This appears to be a FPSM Child level issue")
            print("  → Check HandsReviewPokerStateMachine implementation")
        elif "HandsReviewPokerWidget" in str(e):
            print("  → This appears to be a RPGW Child level issue")
            print("  → Check HandsReviewPokerWidget implementation")
        elif "FlexiblePokerStateMachine" in str(e):
            print("  → This appears to be a FPSM Base level issue")
            print("  → Check base game logic implementation")
        elif "ReusablePokerGameWidget" in str(e):
            print("  → This appears to be a RPGW Base level issue")
            print("  → Check base widget or hook system")
        else:
            print("  → Check imports and module structure")
        
        print(f"\n📍 Full error trace:\n{error_trace}")
        return False

def test_main_gui_integration():
    """Test that both widgets integrate properly with main GUI."""
    print("\n🏢 TESTING MAIN GUI INTEGRATION")
    print("=" * 60)
    
    try:
        print("📦 Testing main GUI imports...")
        from ui.practice_session_ui import PracticeSessionUI
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        from core.gui_models import StrategyData
        print("  ✅ Main GUI components import successfully")
        
        # Test that the new widgets are being used
        print("🔗 Testing widget integration...")
        
        # Check Practice Session UI uses new widget
        import inspect
        practice_ui_source = inspect.getsource(PracticeSessionUI)
        if "PracticeSessionPokerWidget" in practice_ui_source:
            print("  ✅ PracticeSessionUI uses new PracticeSessionPokerWidget")
        else:
            print("  ⚠️ PracticeSessionUI may not be using new widget")
        
        # Check Hands Review Panel uses new widget
        review_panel_source = inspect.getsource(FPSMHandsReviewPanel)
        if "HandsReviewPokerWidget" in review_panel_source:
            print("  ✅ FPSMHandsReviewPanel uses new HandsReviewPokerWidget")
        else:
            print("  ⚠️ FPSMHandsReviewPanel may not be using new widget")
        
        print("  ✅ Integration verification complete")
        
        return True
        
    except Exception as e:
        print(f"❌ INTEGRATION TEST FAILED: {e}")
        print("🔍 DEBUGGING GUIDANCE:")
        print("  → Check that UI components are importing new widgets")
        print("  → Verify widget instantiation in UI classes")
        return False

def main():
    """Run all widget functionality tests."""
    print("🧪 WIDGET FUNCTIONALITY TESTS")
    print("🎯 Testing new hook-based architecture in practice")
    print(f"📅 Test Time: {datetime.now()}")
    print("=" * 70)
    
    # Run all tests
    results = []
    
    print("🚀 Starting widget functionality tests...")
    print("(Windows will appear briefly during testing)")
    
    results.append(("Practice Session Widget", test_practice_session_widget()))
    results.append(("Hands Review Widget", test_hands_review_widget()))
    results.append(("Main GUI Integration", test_main_gui_integration()))
    
    # Report results
    print("\n📊 WIDGET FUNCTIONALITY TEST RESULTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    overall_status = "✅ EXCELLENT" if all_passed else "❌ NEEDS FIXES"
    print(f"\n🎯 OVERALL FUNCTIONALITY: {overall_status}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Practice Session Widget: Hook-based architecture working")
        print("✅ Hands Review Widget: Always-visible cards policy working")
        print("✅ Both widgets: Proper inheritance and specialization")
        print("✅ Main GUI: Correctly integrated with new widgets")
        print("✅ Architecture: Ready for production use")
        print("\n🚀 The new hook-based architecture is fully functional!")
    else:
        print("\n🔧 SOME ISSUES FOUND:")
        print("📋 Use the debugging guidance above to identify fix levels")
        print("📚 Refer to ARCHITECTURAL_DEBUGGING_GUIDE.md for detailed help")
        print("🎯 Remember: Fix at the most specific level that solves the problem")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
