#!/usr/bin/env python3
"""
Test script for the new GameDirector timeline system.

This script tests the pre-simulation timeline approach for hands review.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_director import GameDirector
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.json_hands_database import JSONHandsDatabase, HandCategory
from core.session_logger import SessionLogger
from utils.sound_manager import SoundManager

def test_timeline_system():
    """Test the complete timeline system."""
    print("🧪 Testing GameDirector Timeline System")
    print("=" * 50)
    
    # Initialize components
    session_logger = SessionLogger()
    sound_manager = SoundManager()
    
    # Create hands review state machine
    from core.flexible_poker_state_machine import GameConfig
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
    
    # Set the game director reference in the state machine
    state_machine.game_director = game_director
    
    print("✅ Components initialized")
    
    # Load hands database
    hands_db = JSONHandsDatabase()
    hands_by_category = hands_db.load_all_hands()
    hands_data = hands_by_category[HandCategory.LEGENDARY]
    
    print(f"📚 Database keys: {list(hands_db.raw_data.keys())}")
    print(f"📚 Hands data types: {[(k, type(v), len(v) if isinstance(v, list) else 'N/A') for k, v in hands_db.raw_data.items()]}")
    
    if not hands_data:
        print("❌ No hands found in database")
        return
    
    print(f"📚 Loaded {len(hands_data)} hands from database")
    
    # Test with first hand
    test_hand = hands_data[0].raw_data
    print(f"🎯 Testing with hand: {test_hand.get('hand_id', 'unknown')}")
    
    # Test timeline loading
    print("\n🔄 Testing timeline loading...")
    success = game_director.load_hands_review_timeline(test_hand)
    
    if success:
        print(f"✅ Timeline loaded successfully!")
        print(f"   - Timeline states: {len(game_director.hands_review_timeline)}")
        print(f"   - Current index: {game_director.current_timeline_index}")
        print(f"   - Hands review mode: {game_director.is_hands_review_mode}")
        
        # Show timeline structure
        print("\n📊 Timeline Structure:")
        for i, state in enumerate(game_director.hands_review_timeline):
            print(f"   {i:2d}: {state['state_name']} - {state['current_street']} - Pot: ${state['pot_amount']:.2f}")
        
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
        
    else:
        print("❌ Timeline loading failed")
    
    print("\n🎉 Timeline system test completed!")

if __name__ == "__main__":
    test_timeline_system()
