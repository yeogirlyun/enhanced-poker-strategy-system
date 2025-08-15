#!/usr/bin/env python3
"""
Comprehensive GameDirector Architecture Test

This script tests the GameDirector architecture to ensure:
1. Timeline system works correctly
2. Event system functions properly
3. State machine integration is intact
4. No import/export issues from cleanup
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_director import GameDirector
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.flexible_poker_state_machine import GameConfig, GameEvent, EventListener
from core.json_hands_database import JSONHandsDatabase
from core.session_logger import SessionLogger
from utils.sound_manager import SoundManager

class TestEventListener(EventListener):
    """Test event listener to capture events."""
    
    def __init__(self):
        self.events_received = []
        self.event_count = 0
    
    def on_event(self, event: GameEvent):
        """Capture events for testing."""
        self.events_received.append(event)
        self.event_count += 1
        print(f"📡 Event received: {event.event_type} (total: {self.event_count})")

def test_game_director_basic_functionality():
    """Test basic GameDirector functionality."""
    print("🧪 Testing Basic GameDirector Functionality")
    print("=" * 50)
    
    # Initialize components
    session_logger = SessionLogger()
    sound_manager = SoundManager()
    
    # Create state machine
    config = GameConfig(num_players=6, starting_stack=1000.0)
    state_machine = HandsReviewPokerStateMachine(
        config=config,
        session_logger=session_logger
    )
    
    # Create GameDirector
    game_director = GameDirector(
        state_machine=state_machine,
        ui_renderer=None,
        audio_manager=sound_manager,
        session_logger=session_logger
    )
    
    # Set reference
    state_machine.game_director = game_director
    
    print("✅ Components initialized successfully")
    
    # Test basic methods
    print("\n🔧 Testing basic methods...")
    
    # Test start/stop
    game_director.start()
    print("✅ GameDirector started")
    
    game_director.stop()
    print("✅ GameDirector stopped")
    
    # Test event scheduling
    event_id = game_director.schedule_event(
        delay_ms=100,
        event_type="test_event",
        data={"test": "data"}
    )
    print(f"✅ Event scheduled: {event_id}")
    
    # Test event cancellation
    cancelled = game_director.cancel_event(event_id)
    print(f"✅ Event cancelled: {cancelled}")
    
    return game_director, state_machine

def test_timeline_system():
    """Test the timeline system functionality."""
    print("\n🧪 Testing Timeline System")
    print("=" * 40)
    
    game_director, state_machine = test_game_director_basic_functionality()
    
    # Load hands database
    hands_db = JSONHandsDatabase()
    hands_db.load_all_hands()  # Ensure database is loaded
    hands_data = hands_db.raw_data.get('hands', [])
    
    if not hands_data:
        print("❌ No hands found in database")
        print(f"📊 Database keys: {list(hands_db.raw_data.keys())}")
        print(f"📊 Raw data type: {type(hands_db.raw_data)}")
        return False
    
    print(f"📚 Loaded {len(hands_data)} hands from database")
    
    # Test timeline loading
    test_hand = hands_data[0]
    print(f"🎯 Testing with hand: {test_hand.get('hand_id', 'unknown')}")
    
    success = game_director.load_hands_review_timeline(test_hand)
    
    if success:
        print(f"✅ Timeline loaded successfully!")
        print(f"   - Timeline states: {len(game_director.hands_review_timeline)}")
        print(f"   - Current index: {game_director.current_timeline_index}")
        print(f"   - Hands review mode: {game_director.is_hands_review_mode}")
        
        # Test timeline navigation
        print("\n🎮 Testing timeline navigation...")
        
        # Test next
        if game_director.next_timeline_state():
            print(f"✅ Next state: {game_director.current_timeline_index}")
        else:
            print("❌ Next state failed")
        
        # Test previous
        if game_director.previous_timeline_state():
            print(f"✅ Previous state: {game_director.current_timeline_index}")
        else:
            print("❌ Previous state failed")
        
        # Test street jumping
        print("\n🎯 Testing street jumping...")
        if game_director.jump_to_street("FLOP_BETTING"):
            print(f"✅ Jumped to flop: index {game_director.current_timeline_index}")
        else:
            print("❌ Street jump failed")
        
        # Test play mode
        print("\n▶️ Testing play mode...")
        game_director.set_hands_review_play_speed(1000)  # 1 second
        game_director.start_hands_review_play()
        print("✅ Play mode started")
        
        # Stop play mode
        game_director.stop_hands_review_play()
        print("✅ Play mode stopped")
        
        return True
    else:
        print("❌ Timeline loading failed")
        return False

def test_event_system():
    """Test the event system integration."""
    print("\n🧪 Testing Event System Integration")
    print("=" * 40)
    
    game_director, state_machine = test_game_director_basic_functionality()
    
    # Create test event listener
    test_listener = TestEventListener()
    
    # Add listener to state machine
    state_machine.add_event_listener(test_listener)
    
    print("✅ Event listener added to state machine")
    
    # Test event emission through state machine
    test_event = GameEvent(
        event_type="test_event",
        timestamp=time.time(),
        data={"test": "event_data"}
    )
    
    # Emit event through state machine
    state_machine._emit_event(test_event)
    
    # Check if listener received event
    if test_listener.event_count > 0:
        print(f"✅ Event system working: {test_listener.event_count} events received")
        return True
    else:
        print("❌ Event system not working")
        return False

def test_import_export_integrity():
    """Test that imports and exports work correctly."""
    print("\n🧪 Testing Import/Export Integrity")
    print("=" * 40)
    
    try:
        # Test importing GameDirector
        from core.game_director import GameDirector
        print("✅ GameDirector import successful")
        
        # Test importing ScheduledEvent
        from core.multi_session_game_director import ScheduledEvent
        print("✅ ScheduledEvent import successful")
        
        # Test importing state machine
        from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
        print("✅ HandsReviewPokerStateMachine import successful")
        
        # Test importing base classes
        from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameEvent
        print("✅ Base class imports successful")
        
        # Test creating instances
        game_director = GameDirector(None, None, None, SessionLogger())
        print("✅ GameDirector instance creation successful")
        
        scheduled_event = ScheduledEvent(time.time(), "test", {}, "test_session")
        print("✅ ScheduledEvent instance creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/Export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_architecture_integrity():
    """Test overall architecture integrity."""
    print("\n🧪 Testing Architecture Integrity")
    print("=" * 40)
    
    try:
        # Test component relationships
        session_logger = SessionLogger()
        sound_manager = SoundManager()
        config = GameConfig(num_players=6, starting_stack=1000.0)
        
        # Create state machine
        state_machine = HandsReviewPokerStateMachine(
            config=config,
            session_logger=session_logger
        )
        
        # Create GameDirector
        game_director = GameDirector(
            state_machine=state_machine,
            ui_renderer=None,
            audio_manager=sound_manager,
            session_logger=session_logger
        )
        
        # Set bidirectional references
        state_machine.game_director = game_director
        
        # Test that references are set correctly
        if state_machine.game_director == game_director:
            print("✅ Bidirectional references set correctly")
        else:
            print("❌ Bidirectional references not set correctly")
            return False
        
        # Test that GameDirector can access state machine
        if game_director.state_machine == state_machine:
            print("✅ GameDirector can access state machine")
        else:
            print("❌ GameDirector cannot access state machine")
            return False
        
        # Test that components have required methods
        required_methods = ['start', 'stop', 'schedule_event', 'cancel_event']
        for method in required_methods:
            if hasattr(game_director, method):
                print(f"✅ GameDirector has {method} method")
            else:
                print(f"❌ GameDirector missing {method} method")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Architecture integrity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all GameDirector architecture tests."""
    print("🚀 Starting GameDirector Architecture Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_game_director_basic_functionality),
        ("Timeline System", test_timeline_system),
        ("Event System", test_event_system),
        ("Import/Export", test_import_export_integrity),
        ("Architecture Integrity", test_architecture_integrity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Basic Functionality":
                # This test returns components, not boolean
                test_func()
                results.append((test_name, True))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! GameDirector architecture is intact.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
