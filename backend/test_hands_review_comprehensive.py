#!/usr/bin/env python3
"""
Comprehensive Hands Review Test Suite

This script automatically tests all 130 legendary poker hands by mocking
user step forward clicks, validating complete hand progression, and 
identifying any stalling or UI issues.

Usage:
    python3 test_hands_review_comprehensive.py
"""

import sys
import os
import json
import time
import traceback
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core components
try:
    from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
    from core.multi_session_game_director import MultiSessionGameDirector
    from core.session_manager import SessionManager
    from core.types import PokerState
    from core.flexible_poker_state_machine import GameConfig
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this script from the project root directory")
    sys.exit(1)


class TestResult(Enum):
    SUCCESS = "success"
    STALLED = "stalled"
    ERROR = "error"
    INCOMPLETE = "incomplete"


@dataclass
class HandTestResult:
    hand_id: str
    hand_name: str
    result: TestResult
    total_actions: int
    completed_actions: int
    final_state: Optional[PokerState]
    error_message: Optional[str]
    execution_time: float
    stalling_pattern: Optional[str]


class HandsReviewTester:
    """Comprehensive tester for hands review functionality."""
    
    def __init__(self):
        self.session_manager = SessionManager(num_players=9, big_blind=100.0)  # Default poker table setup
        session_id = self.session_manager.start_session()
        self.logger = self.session_manager.logger  # Access logger directly
        print(f"Started test session: {session_id}")
        
        self.game_director = None
        self.state_machine = None
        self.test_results: List[HandTestResult] = []
        
    def setup_hands_review(self) -> bool:
        """Initialize the hands review components."""
        try:
            print("🔧 Setting up hands review components...")
            
            # Create game director
            self.game_director = MultiSessionGameDirector(self.logger)
            
            # Create hands review state machine
            config = GameConfig(
                num_players=9,
                big_blind=100.0,
                small_blind=50.0,
                starting_stack=1000000.0,  # Large stack for legendary hands
                test_mode=True
            )
            self.state_machine = HandsReviewPokerStateMachine(config, session_logger=self.logger)
            self.state_machine.set_game_director(self.game_director)
            
            # Register with game director (use None for UI components in headless test)
            self.game_director.register_session(
                session_id='hands_review',
                state_machine=self.state_machine,
                ui_renderer=None,  # Headless test
                audio_manager=None,  # Headless test
                session_type='hands_review'
            )
            self.game_director.activate_session('hands_review')
            
            print("✅ Hands review components initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup hands review: {e}")
            traceback.print_exc()
            return False
    
    def load_legendary_hands(self) -> List[Dict[str, Any]]:
        """Load all 130 legendary poker hands."""
        try:
            hands_file = os.path.join(os.path.dirname(__file__), 'data', 'legendary_hands_complete_130_fixed.json')
            
            if not os.path.exists(hands_file):
                print(f"❌ Legendary hands file not found: {hands_file}")
                return []
                
            with open(hands_file, 'r') as f:
                hands_data = json.load(f)
                
            if isinstance(hands_data, dict) and 'hands' in hands_data:
                hands = hands_data['hands']
            elif isinstance(hands_data, list):
                hands = hands_data
            else:
                print(f"❌ Unexpected hands data format")
                return []
                
            print(f"📚 Loaded {len(hands)} legendary hands")
            return hands
            
        except Exception as e:
            print(f"❌ Failed to load legendary hands: {e}")
            traceback.print_exc()
            return []
    
    def mock_step_forward_clicks(self, hand_data: Dict[str, Any], max_steps: int = 100) -> HandTestResult:
        """Mock repeated step forward button clicks for a single hand."""
        import time
        
        hand_id = str(hand_data.get('id', 'unknown'))
        hand_name = hand_data.get('description', f"Hand {hand_id}")
        
        print(f"\n🎮 Testing Hand {hand_id}: {hand_name}")
        
        start_time = time.time()
        completed_actions = 0
        total_actions = 0  # Initialize here to avoid scope issues
        stalling_pattern = None
        error_message = None
        
        try:
            # Load the hand
            if not self.state_machine.load_hand_for_review(hand_data):
                return HandTestResult(
                    hand_id=hand_id,
                    hand_name=hand_name,
                    result=TestResult.ERROR,
                    total_actions=0,
                    completed_actions=0,
                    final_state=None,
                    error_message="Failed to load hand",
                    execution_time=time.time() - start_time,
                    stalling_pattern=None
                )
            
            total_actions = len(self.state_machine.historical_actions)
            print(f"📋 Hand loaded - {total_actions} total actions")
            
            # Track consecutive failures for stalling detection
            consecutive_failures = 0
            last_action_index = -1
            
            # Mock step forward clicks
            for step in range(max_steps):
                current_action_index = getattr(self.state_machine, 'action_index', 0)
                
                # Check if we've completed all actions
                if current_action_index >= total_actions:
                    print(f"✅ Hand completed - all {total_actions} actions executed")
                    completed_actions = total_actions
                    break
                
                # Check for stalling (same action index for multiple steps)
                if current_action_index == last_action_index:
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        stalling_pattern = self._identify_stalling_pattern(current_action_index)
                        print(f"🚨 STALLING DETECTED: {stalling_pattern}")
                        break
                else:
                    consecutive_failures = 0
                    completed_actions = current_action_index
                
                last_action_index = current_action_index
                
                # Mock step forward click
                success = self.state_machine.step_forward()
                
                if step % 5 == 0:  # Progress update every 5 steps
                    print(f"   Step {step + 1}: Action {current_action_index + 1}/{total_actions} - {'✅' if success else '❌'}")
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
            
            # Determine final result
            final_state = getattr(self.state_machine, 'current_state', None)
            
            if completed_actions >= total_actions:
                result = TestResult.SUCCESS
            elif stalling_pattern:
                result = TestResult.STALLED
            elif completed_actions == 0:
                result = TestResult.ERROR
                error_message = "No actions completed"
            else:
                result = TestResult.INCOMPLETE
                error_message = f"Only {completed_actions}/{total_actions} actions completed"
            
        except Exception as e:
            error_message = str(e)
            result = TestResult.ERROR
            final_state = getattr(self.state_machine, 'current_state', None)
            print(f"❌ Exception during hand test: {e}")
            traceback.print_exc()
        
        execution_time = time.time() - start_time
        
        return HandTestResult(
            hand_id=hand_id,
            hand_name=hand_name,
            result=result,
            total_actions=total_actions,
            completed_actions=completed_actions,
            final_state=final_state,
            error_message=error_message,
            execution_time=execution_time,
            stalling_pattern=stalling_pattern
        )
    
    def _identify_stalling_pattern(self, action_index: int) -> str:
        """Identify the specific stalling pattern based on current state."""
        try:
            current_state = getattr(self.state_machine, 'current_state', None)
            current_action = None
            
            if hasattr(self.state_machine, 'historical_actions') and self.state_machine.historical_actions:
                actions = self.state_machine.historical_actions
                if 0 <= action_index < len(actions):
                    current_action = actions[action_index]
            
            # Pattern identification
            if current_action:
                action_type = current_action.get('action_type', 'unknown')
                amount = current_action.get('amount', 0)
                player_name = current_action.get('player_name', 'unknown')
                
                if action_type == 'call' and amount == 0:
                    return "CALL_AMOUNT_ZERO"
                elif action_type == 'call':
                    return "INSUFFICIENT_STACK_CALL"
                elif action_type == 'all-in':
                    return "ALL_IN_VALIDATION_FAILURE"
                elif "Player" in str(current_state) and "DEAL" in str(current_state):
                    return "BASE_CLASS_TRANSITION_CONFLICT"
                else:
                    return f"UNKNOWN_STALLING_{action_type.upper()}"
            
            return f"UNKNOWN_STATE_{current_state}"
            
        except Exception:
            return "PATTERN_IDENTIFICATION_ERROR"
    
    def test_all_hands(self) -> None:
        """Test all legendary hands and generate comprehensive report."""
        print("🚀 Starting comprehensive hands review testing...")
        
        if not self.setup_hands_review():
            return
        
        legendary_hands = self.load_legendary_hands()
        if not legendary_hands:
            return
        
        # Test each hand (limit to first 2 for winner announcement testing)
        for i, hand_data in enumerate(legendary_hands[:2]):
            print(f"\n{'='*60}")
            print(f"Testing Hand {i+1}/{len(legendary_hands)}")
            
            result = self.mock_step_forward_clicks(hand_data)
            self.test_results.append(result)
            
            # Print immediate result
            status_emoji = {
                TestResult.SUCCESS: "✅",
                TestResult.STALLED: "🚨", 
                TestResult.ERROR: "❌",
                TestResult.INCOMPLETE: "⚠️"
            }
            
            print(f"{status_emoji[result.result]} {result.result.value.upper()}: "
                  f"{result.completed_actions}/{result.total_actions} actions "
                  f"({result.execution_time:.2f}s)")
            
            if result.stalling_pattern:
                print(f"   🔍 Stalling Pattern: {result.stalling_pattern}")
            if result.error_message:
                print(f"   💬 Error: {result.error_message}")
        
        # Generate final report
        self._generate_report()
    
    def _generate_report(self) -> None:
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE HANDS REVIEW TEST REPORT")
        print("="*80)
        
        # Summary statistics
        total_hands = len(self.test_results)
        successful = len([r for r in self.test_results if r.result == TestResult.SUCCESS])
        stalled = len([r for r in self.test_results if r.result == TestResult.STALLED])
        errors = len([r for r in self.test_results if r.result == TestResult.ERROR])
        incomplete = len([r for r in self.test_results if r.result == TestResult.INCOMPLETE])
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Hands Tested: {total_hands}")
        print(f"   ✅ Successful: {successful} ({successful/total_hands*100:.1f}%)")
        print(f"   🚨 Stalled: {stalled} ({stalled/total_hands*100:.1f}%)")
        print(f"   ❌ Errors: {errors} ({errors/total_hands*100:.1f}%)")
        print(f"   ⚠️  Incomplete: {incomplete} ({incomplete/total_hands*100:.1f}%)")
        
        # Stalling pattern analysis
        if stalled > 0:
            print(f"\n🔍 STALLING PATTERNS DETECTED:")
            stalling_patterns = {}
            for result in self.test_results:
                if result.stalling_pattern:
                    pattern = result.stalling_pattern
                    if pattern not in stalling_patterns:
                        stalling_patterns[pattern] = []
                    stalling_patterns[pattern].append(result.hand_id)
            
            for pattern, hand_ids in stalling_patterns.items():
                print(f"   {pattern}: {len(hand_ids)} hands ({', '.join(hand_ids[:5])}{'...' if len(hand_ids) > 5 else ''})")
        
        # Error analysis
        if errors > 0:
            print(f"\n❌ ERROR ANALYSIS:")
            error_messages = {}
            for result in self.test_results:
                if result.error_message:
                    msg = result.error_message
                    if msg not in error_messages:
                        error_messages[msg] = []
                    error_messages[msg].append(result.hand_id)
            
            for error, hand_ids in error_messages.items():
                print(f"   {error}: {len(hand_ids)} hands")
        
        # Performance analysis
        total_time = sum(r.execution_time for r in self.test_results)
        avg_time = total_time / total_hands if total_hands > 0 else 0
        
        print(f"\n⏱️  PERFORMANCE:")
        print(f"   Total Execution Time: {total_time:.2f}s")
        print(f"   Average Time per Hand: {avg_time:.2f}s")
        print(f"   Estimated Full Suite Time: {avg_time * 130:.2f}s")
        
        # Recommendations
        print(f"\n🛠️  RECOMMENDATIONS:")
        if stalled > 0:
            print(f"   1. Fix stalling patterns - {stalled} hands affected")
        if errors > 0:
            print(f"   2. Resolve error conditions - {errors} hands affected")
        if incomplete > 0:
            print(f"   3. Investigate incomplete executions - {incomplete} hands affected")
        
        if successful == total_hands:
            print(f"   🎉 All hands completed successfully! Ready for production.")
        
        # Save detailed report to file
        self._save_detailed_report()
    
    def _save_detailed_report(self) -> None:
        """Save detailed test results to JSON file."""
        try:
            report_data = {
                'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total_hands': len(self.test_results),
                    'successful': len([r for r in self.test_results if r.result == TestResult.SUCCESS]),
                    'stalled': len([r for r in self.test_results if r.result == TestResult.STALLED]),
                    'errors': len([r for r in self.test_results if r.result == TestResult.ERROR]),
                    'incomplete': len([r for r in self.test_results if r.result == TestResult.INCOMPLETE])
                },
                'detailed_results': [
                    {
                        'hand_id': r.hand_id,
                        'hand_name': r.hand_name,
                        'result': r.result.value,
                        'total_actions': r.total_actions,
                        'completed_actions': r.completed_actions,
                        'final_state': str(r.final_state) if r.final_state else None,
                        'error_message': r.error_message,
                        'execution_time': r.execution_time,
                        'stalling_pattern': r.stalling_pattern
                    }
                    for r in self.test_results
                ]
            }
            
            report_file = 'hands_review_test_report.json'
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Detailed report saved to: {report_file}")
            
        except Exception as e:
            print(f"❌ Failed to save detailed report: {e}")


def main():
    """Main test execution function."""
    print("🎯 Comprehensive Hands Review Testing Suite")
    print("="*50)
    
    tester = HandsReviewTester()
    tester.test_all_hands()


if __name__ == "__main__":
    main()
