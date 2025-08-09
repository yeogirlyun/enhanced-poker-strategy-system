#!/usr/bin/env python3
"""
Hands Review Panel JSON Format Tester

Tests the complete FPSM + RPGW + Hands Review Panel integration using JSON format.
This tests the full UI pipeline in a controlled way.
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player, ActionType, PokerState
from core.position_mapping import UniversalPosition
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class HandsReviewJSONTester:
    """Tests Hands Review Panel using JSON format legendary hands."""
    
    def __init__(self):
        self.json_data = None
        self.hands = []
        self.test_results = []
        self.total_hands = 0
        self.successful_tests = 0
        self.errors = []
        
    def run_comprehensive_test(self):
        """Run comprehensive Hands Review Panel tests using JSON format."""
        print("🎯 HANDS REVIEW PANEL JSON FORMAT COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Step 1: Load JSON data
        self.load_json_data()
        
        # Step 2: Test subset of hands (to avoid UI overhead)
        self.test_representative_hands()
        
        # Step 3: Generate report
        self.generate_test_report()
        
        return self.test_results
    
    def load_json_data(self):
        """Load the comprehensive JSON legendary hands data."""
        json_file_path = "data/legendary_hands_comprehensive.json"
        
        print(f"📚 Loading JSON data from {json_file_path}...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            self.hands = self.json_data['hands']
            self.total_hands = len(self.hands)
            
            print(f"✅ Loaded {self.total_hands} hands from JSON")
            
        except Exception as e:
            print(f"❌ Failed to load JSON data: {e}")
            raise
    
    def test_representative_hands(self):
        """Test a representative subset of hands to validate the hands review panel."""
        # Test first 10 hands as a representative sample
        test_hands = self.hands[:10]
        self.total_hands = len(test_hands)
        
        print(f"🎮 Testing {self.total_hands} representative hands with Hands Review Panel...")
        
        for i, hand_data in enumerate(test_hands):
            hand_id = hand_data['metadata']['id']
            hand_name = hand_data['metadata']['name']
            
            print(f"  [{i+1:2d}/{self.total_hands}] Testing: {hand_name}")
            
            try:
                result = self.test_single_hand(hand_data)
                self.test_results.append(result)
                
                if result['success']:
                    self.successful_tests += 1
                    print(f"    ✅ SUCCESS - Panel loaded and configured properly")
                else:
                    print(f"    ❌ FAILED - {result['error']}")
                    
            except Exception as e:
                error_msg = f"Exception during test: {str(e)}"
                print(f"    💥 EXCEPTION - {error_msg}")
                self.errors.append({
                    'hand_id': hand_id,
                    'hand_name': hand_name,
                    'error': error_msg
                })
        
        print(f"✅ Completed testing: {self.successful_tests}/{self.total_hands} successful")
    
    def test_single_hand(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hand with the Hands Review Panel in test mode."""
        start_time = time.time()
        
        hand_id = hand_data['metadata']['id']
        hand_name = hand_data['metadata']['name']
        
        try:
            # Create a minimal hands database for testing
            class MockHandsDB:
                def __init__(self, hand_data):
                    self.all_hands = {hand_data['metadata']['id']: self._convert_json_to_hand(hand_data)}
                
                def _convert_json_to_hand(self, hand_data):
                    """Convert JSON hand data to a mock hand object."""
                    class MockHand:
                        def __init__(self, data):
                            self.metadata = type('MockMetadata', (), {
                                'id': data['metadata']['id'],
                                'name': data['metadata']['name']
                            })()
                            self.players = [
                                {
                                    'name': p['name'],
                                    'seat': i + 1,
                                    'starting_stack_chips': p['starting_stack'],
                                    'cards': p.get('cards', [])
                                }
                                for i, p in enumerate(data['players'])
                            ]
                            # Convert actions back to PHH-like format
                            self.actions = {}
                            for street, street_data in data.get('streets', {}).items():
                                actions = street_data.get('actions', [])
                                if actions:
                                    self.actions[street] = [
                                        {
                                            'actor': i + 1,  # Mock actor mapping
                                            'type': action.get('action_type', 'fold'),
                                            'amount': action.get('amount', 0)
                                        }
                                        for i, action in enumerate(actions)
                                    ]
                    
                    return MockHand(hand_data)
            
            # Create mock hands database
            hands_db = MockHandsDB(hand_data)
            
            # Create Hands Review Panel in test mode
            panel = FPSMHandsReviewPanel(
                parent=None,  # No parent for testing
                hands_db=hands_db,
                debug_mode=True,
                test_mode=True  # This should skip UI setup
            )
            
            # Try to load the hand data
            mock_hand = hands_db.all_hands[hand_id]
            panel.load_hand_data(mock_hand)
            
            # Verify the panel was configured correctly
            validation_errors = []
            
            # Check if current_hand is set
            if not hasattr(panel, 'current_hand') or panel.current_hand is None:
                validation_errors.append("Current hand not set")
            
            # Check if FPSM was created
            if not hasattr(panel, 'fpsm') or panel.fpsm is None:
                validation_errors.append("FPSM not created")
            
            # Check if RPGW was created (if not in test mode)
            if hasattr(panel, 'rpgw') and panel.rpgw is not None:
                # RPGW was created, verify it's connected
                if not hasattr(panel.rpgw, 'fpsm') or panel.rpgw.fpsm != panel.fpsm:
                    validation_errors.append("RPGW not properly connected to FPSM")
            
            # Check if actions data is available
            if (hasattr(panel.current_hand, 'actions') and 
                isinstance(panel.current_hand.actions, dict) and
                len(panel.current_hand.actions) == 0):
                validation_errors.append("No actions data available")
            
            duration = time.time() - start_time
            success = len(validation_errors) == 0
            
            return {
                'hand_id': hand_id,
                'hand_name': hand_name,
                'success': success,
                'validation_errors': validation_errors,
                'duration': duration,
                'error': '; '.join(validation_errors) if validation_errors else None
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'hand_id': hand_id,
                'hand_name': hand_name,
                'success': False,
                'validation_errors': [f"Exception: {str(e)}"],
                'duration': duration,
                'error': f"Exception: {str(e)}"
            }
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 60)
        print("📋 HANDS REVIEW PANEL JSON FORMAT TEST REPORT")
        print("=" * 60)
        
        success_rate = (self.successful_tests / max(1, self.total_hands)) * 100
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"  Total hands tested: {self.total_hands}")
        print(f"  Successful tests: {self.successful_tests}")
        print(f"  Failed tests: {self.total_hands - self.successful_tests}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        # Show failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  - {result['hand_name']}: {result['error']}")
        
        # Show exceptions
        if self.errors:
            print(f"\n💥 EXCEPTIONS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error['hand_name']}: {error['error']}")
        
        # Performance statistics
        if self.test_results:
            total_time = sum(r['duration'] for r in self.test_results)
            avg_time = total_time / len(self.test_results)
            
            print(f"\n⚡ PERFORMANCE:")
            print(f"  Total test time: {total_time:.3f}s")
            print(f"  Average time per hand: {avg_time:.3f}s")
        
        # Success rate assessment
        print(f"\n🎯 ASSESSMENT:")
        if success_rate == 100.0:
            print("🎉 PERFECT! Hands Review Panel works perfectly with JSON format!")
        elif success_rate >= 95.0:
            print("✅ EXCELLENT! Hands Review Panel integration is very solid")
        elif success_rate >= 90.0:
            print("🟡 GOOD: Hands Review Panel mostly working, minor issues")
        else:
            print("🔴 NEEDS WORK: Significant Hands Review Panel integration issues")
        
        print(f"\n📝 NOTE:")
        print(f"  This test validates panel setup and configuration.")
        print(f"  For full simulation testing, use the GUI manually as")
        print(f"  requested by the user.")

def main():
    """Main function to run the Hands Review Panel JSON format test."""
    tester = HandsReviewJSONTester()
    
    try:
        results = tester.run_comprehensive_test()
        return 0 if tester.successful_tests == tester.total_hands else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
