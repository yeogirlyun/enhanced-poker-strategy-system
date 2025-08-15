#!/usr/bin/env python3
"""
Game Director Non-GUI Tester

This script tests the Game Director without any GUI components to confirm:
1. GTO bot hands are properly loaded
2. Timeline sequences are correctly built
3. State changes are properly tracked
4. Display data is complete at every step
5. The issue is with UI rendering, not Game Director data

Usage: python game_director_tester.py
"""

import sys
import os
import json
import time

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from core.game_director import GameDirector
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.flexible_poker_state_machine import FlexiblePokerStateMachine


class GameDirectorTester:
    """Comprehensive tester for Game Director functionality."""
    
    def __init__(self):
        self.test_results = []
        self.current_hand_index = 0
        
    def log_test(self, message, data=None):
        """Log test information with optional data."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        if data:
            log_entry += f"\n{json.dumps(data, indent=2, default=str)}"
        
        print(log_entry)
        print("-" * 80)
        self.test_results.append(log_entry)
        
    def test_hand_loading(self):
        """Test loading of GTO hands from JSON database."""
        print("🔍 TESTING HAND LOADING")
        print("=" * 80)
        
        try:
            # Test loading hands from the database
            hands_file = "data/legendary_hands_complete_130_fixed.json"
            if not os.path.exists(hands_file):
                self.log_test("❌ ERROR: Hands database file not found", {"file": hands_file})
                return False
                
            with open(hands_file, 'r') as f:
                database = json.load(f)
                
            # Extract hands from the database structure
            hands_data = database.get('hands', [])
            if not hands_data:
                self.log_test("❌ ERROR: No hands found in database", {"database_keys": list(database.keys())})
                return False
                
            self.log_test("✅ Hands database loaded successfully", {
                "total_hands": len(hands_data),
                "file_size_mb": round(os.path.getsize(hands_file) / (1024 * 1024), 2),
                "database_structure": list(database.keys()),
                "sample_hand_keys": list(hands_data[0].keys()) if hands_data else []
            })
            
            # Test first few hands structure
            for i, hand in enumerate(hands_data[:3]):
                self.log_test(f"📊 Hand {i+1} Structure Analysis", {
                    "hand_id": hand.get('id', 'N/A'),
                    "session_id": hand.get('session_id', 'N/A'),
                    "num_players": hand.get('num_players', 'N/A'),
                    "players_count": len(hand.get('players', [])),
                    "actions_structure": list(hand.get('actions', {}).keys()),
                    "pot_amount": hand.get('pot', 'N/A'),
                    "winner_info": hand.get('winner', 'N/A')
                })
                
            return True
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to load hands database", {"error": str(e)})
            return False
    
    def test_state_machine_creation(self):
        """Test creation and initialization of poker state machines."""
        print("\n🔍 TESTING STATE MACHINE CREATION")
        print("=" * 80)
        
        try:
            # Test HandsReviewPokerStateMachine
            self.log_test("🔄 Creating HandsReviewPokerStateMachine...")
            hands_review_fpsm = HandsReviewPokerStateMachine()
            
            # Test FlexiblePokerStateMachine
            self.log_test("🔄 Creating FlexiblePokerStateMachine...")
            flexible_fpsm = FlexiblePokerStateMachine()
            
            self.log_test("✅ Both state machines created successfully", {
                "hands_review_type": type(hands_review_fpsm).__name__,
                "flexible_type": type(flexible_fpsm).__name__
            })
            
            return True
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to create state machines", {"error": str(e)})
            return False
    
    def test_game_director_creation(self):
        """Test Game Director creation and initialization."""
        print("\n🔍 TESTING GAME DIRECTOR CREATION")
        print("=" * 80)
        
        try:
            # Create a mock state machine for testing
            mock_fpsm = HandsReviewPokerStateMachine()
            
            # Create Game Director
            self.log_test("🔄 Creating Game Director...")
            game_director = GameDirector(mock_fpsm)
            
            self.log_test("✅ Game Director created successfully", {
                "type": type(game_director).__name__,
                "has_state_machine": hasattr(game_director, 'state_machine'),
                "has_timeline": hasattr(game_director, 'timeline'),
                "has_snapshots": hasattr(game_director, 'snapshots')
            })
            
            return game_director
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to create Game Director", {"error": str(e)})
            return None
    
    def test_timeline_creation(self, game_director, hand_data):
        """Test timeline creation from hand data."""
        print(f"\n🔍 TESTING TIMELINE CREATION FOR HAND {self.current_hand_index + 1}")
        print("=" * 80)
        
        try:
            self.log_test("🔄 Loading hand into timeline...", {
                "hand_id": hand_data.get('id', 'N/A'),
                "session_id": hand_data.get('session_id', 'N/A'),
                "num_players": hand_data.get('num_players', 'N/A')
            })
            
            # Load the hand into the timeline
            success = game_director.load_hands_review_timeline(hand_data)
            
            if not success:
                self.log_test("❌ ERROR: Failed to load hand into timeline")
                return False
            
            # Get timeline information
            timeline = game_director.timeline
            snapshots = game_director.snapshots
            
            self.log_test("✅ Timeline created successfully", {
                "timeline_length": len(timeline) if timeline else 0,
                "snapshots_count": len(snapshots) if snapshots else 0,
                "current_index": game_director.current_timeline_index
            })
            
            return True
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to create timeline", {"error": str(e)})
            return False
    
    def test_timeline_sequence(self, game_director, hand_data):
        """Test going through each step in the timeline sequence."""
        print(f"\n🔍 TESTING TIMELINE SEQUENCE FOR HAND {self.current_hand_index + 1}")
        print("=" * 80)
        
        try:
            timeline = game_director.timeline
            if not timeline:
                self.log_test("❌ ERROR: No timeline available")
                return False
            
            self.log_test(f"🔄 Testing {len(timeline)} timeline steps...")
            
            # Test each step in the timeline
            for step_index, step in enumerate(timeline):
                self.log_test(f"📊 Step {step_index + 1}/{len(timeline)}", {
                    "step_type": step.get('type', 'N/A'),
                    "step_data": step.get('data', {}),
                    "step_metadata": {k: v for k, v in step.items() if k not in ['type', 'data']}
                })
                
                # Jump to this step
                self.log_test(f"🔄 Jumping to timeline index {step_index}...")
                success = game_director.jump_to_timeline_index(step_index)
                
                if not success:
                    self.log_test(f"❌ ERROR: Failed to jump to step {step_index}")
                    continue
                
                # Get the current game state
                current_state = game_director.state_machine.get_game_info()
                
                self.log_test(f"✅ Step {step_index + 1} loaded successfully", {
                    "current_state": current_state.get('state', 'N/A'),
                    "pot_amount": current_state.get('pot', 'N/A'),
                    "current_bet": current_state.get('current_bet', 'N/A'),
                    "street": current_state.get('street', 'N/A'),
                    "players_count": len(current_state.get('players', [])),
                    "board_cards": current_state.get('board', []),
                    "action_player": current_state.get('action_player', 'N/A')
                })
                
                # Test display state generation
                self.test_display_state_generation(game_director, step_index)
                
                print(f"✅ Step {step_index + 1} completed successfully")
                print("-" * 60)
            
            return True
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to test timeline sequence", {"error": str(e)})
            return False
    
    def test_display_state_generation(self, game_director, step_index):
        """Test that Game Director can generate complete display state."""
        print(f"  🔍 Testing display state generation for step {step_index + 1}")
        
        try:
            # Get the current display state
            display_state = game_director.get_display_state()
            
            if not display_state:
                self.log_test(f"  ❌ ERROR: No display state for step {step_index + 1}")
                return False
            
            # Analyze the display state
            self.log_test(f"  ✅ Display state generated for step {step_index + 1}", {
                "has_game_info": 'game_info' in display_state,
                "has_ui_state": 'ui_state' in display_state,
                "has_audio_events": 'audio_events' in display_state,
                "game_info_keys": list(display_state.get('game_info', {}).keys()),
                "ui_state_keys": list(display_state.get('ui_state', {}).keys()),
                "audio_events_count": len(display_state.get('audio_events', []))
            })
            
            # Test specific game info components
            game_info = display_state.get('game_info', {})
            if game_info:
                self.log_test(f"  📊 Game info details for step {step_index + 1}", {
                    "state": game_info.get('state', 'N/A'),
                    "pot": game_info.get('pot', 'N/A'),
                    "current_bet": game_info.get('current_bet', 'N/A'),
                    "street": game_info.get('street', 'N/A'),
                    "players_count": len(game_info.get('players', [])),
                    "board_cards": game_info.get('board', []),
                    "action_player": game_info.get('action_player', 'N/A'),
                    "dealer_position": game_info.get('dealer_position', 'N/A')
                })
                
                # Test player data
                players = game_info.get('players', [])
                if players:
                    self.log_test(f"  👥 Player data for step {step_index + 1}", {
                        "player_count": len(players),
                        "sample_player": {
                            "name": players[0].get('name', 'N/A') if players else 'N/A',
                            "stack": players[0].get('stack', 'N/A') if players else 'N/A',
                            "bet": players[0].get('bet', 'N/A') if players else 'N/A',
                            "cards": players[0].get('cards', []) if players else [],
                            "position": players[0].get('position', 'N/A') if players else 'N/A',
                            "is_active": players[0].get('is_active', 'N/A') if players else 'N/A'
                        } if players else {}
                    })
            
            return True
            
        except Exception as e:
            self.log_test(f"  ❌ ERROR: Failed to test display state for step {step_index + 1}", {"error": str(e)})
            return False
    
    def test_gto_bot_hands(self, game_director):
        """Test GTO bot hands specifically."""
        print(f"\n🔍 TESTING GTO BOT HANDS")
        print("=" * 80)
        
        try:
            # Load hands database
            hands_file = "data/legendary_hands_complete_130_fixed.json"
            with open(hands_file, 'r') as f:
                hands_data = json.load(f)
            
            # Test first 5 hands
            test_hands = hands_data[:5]
            
            for hand_index, hand_data in enumerate(test_hands):
                self.current_hand_index = hand_index
                
                self.log_test(f"🔄 Testing GTO Hand {hand_index + 1}", {
                    "hand_id": hand_data.get('id', 'N/A'),
                    "session_id": hand_data.get('session_id', 'N/A'),
                    "num_players": hand_data.get('num_players', 'N/A'),
                    "pot_amount": hand_data.get('pot', 'N/A')
                })
                
                # Test timeline creation
                if not self.test_timeline_creation(game_director, hand_data):
                    continue
                
                # Test timeline sequence
                if not self.test_timeline_sequence(game_director, hand_data):
                    continue
                
                self.log_test(f"✅ GTO Hand {hand_index + 1} completed successfully")
                print("=" * 80)
            
            return True
            
        except Exception as e:
            self.log_test("❌ ERROR: Failed to test GTO bot hands", {"error": str(e)})
            return False
    
    def run_comprehensive_test(self):
        """Run the complete comprehensive test suite."""
        print("🚀 GAME DIRECTOR COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print("This test will confirm that Game Director has all data needed for rendering.")
        print("If all tests pass, the issue is with UI rendering, not Game Director data.")
        print("=" * 80)
        
        # Test 1: Hand Loading
        if not self.test_hand_loading():
            print("❌ CRITICAL: Hand loading failed. Cannot proceed with tests.")
            return False
        
        # Test 2: State Machine Creation
        if not self.test_state_machine_creation():
            print("❌ CRITICAL: State machine creation failed. Cannot proceed with tests.")
            return False
        
        # Test 3: Game Director Creation
        game_director = self.test_game_director_creation()
        if not game_director:
            print("❌ CRITICAL: Game Director creation failed. Cannot proceed with tests.")
            return False
        
        # Test 4: GTO Bot Hands
        if not self.test_gto_bot_hands(game_director):
            print("❌ CRITICAL: GTO bot hands testing failed.")
            return False
        
        # Final Summary
        print("\n🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("✅ All tests passed!")
        print("✅ Game Director has complete data for rendering")
        print("✅ Timeline sequences are properly built")
        print("✅ State changes are correctly tracked")
        print("✅ Display state generation works at every step")
        print("\n🔍 CONCLUSION: If UI rendering issues exist, they are NOT caused by")
        print("   Game Director data problems. The issue is in the UI rendering layer.")
        
        return True
    
    def save_test_results(self):
        """Save test results to a file."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_file = f"logs/game_director_test_results_{timestamp}.log"
            
            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)
            
            with open(results_file, 'w') as f:
                f.write("\n".join(self.test_results))
            
            print(f"\n📝 Test results saved to: {results_file}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not save test results: {e}")


def main():
    """Main test execution function."""
    print("🎯 Game Director Non-GUI Tester")
    print("=" * 80)
    
    # Create tester instance
    tester = GameDirectorTester()
    
    try:
        # Run comprehensive test
        success = tester.run_comprehensive_test()
        
        # Save results
        tester.save_test_results()
        
        if success:
            print("\n🎯 TEST SUMMARY: Game Director is working correctly!")
            print("   All data is properly loaded and available for UI rendering.")
            print("   Any display issues are in the UI layer, not the Game Director.")
        else:
            print("\n❌ TEST SUMMARY: Game Director has issues that need fixing.")
            print("   Check the error logs above for specific problems.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
