#!/usr/bin/env python3
"""
Automated Mock UI Tester for Hands Review Tab

This script runs an automated test of all 120 legendary hands through the hands review panel
with a mock UI (no actual GUI display) to verify that everything works correctly.

The tester will:
1. Load all 120 hands from the hands database
2. For each hand, set up the FPSM hands review panel
3. Run the simulation to completion 
4. Track success/failure for each hand
5. Continue running until all hands pass or max iterations reached
6. Report detailed results

Usage: python test_hands_review_mock_ui.py
"""

import sys
import os
import time
import traceback
from typing import Dict, List, Optional, Tuple
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hands_database import ComprehensiveHandsDatabase
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from core.flexible_poker_state_machine import FlexiblePokerStateMachine
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget
import tkinter as tk
from tkinter import ttk


class MockHandsReviewTester:
    """Mock UI tester for hands review functionality."""
    
    def __init__(self):
        self.hands_db = ComprehensiveHandsDatabase()
        self.hands_db.load_all_hands()
        
        # Results tracking
        self.results = {}
        self.test_iteration = 1
        self.max_iterations = 5  # Max times to retry all hands
        
        # Create a minimal Tkinter root for widget testing
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        print(f"🎯 Mock UI Tester initialized with {len(self.hands_db.all_hands)} hands")
    
    def run_all_hands_test(self) -> Dict[str, bool]:
        """Run automated test on all hands until all pass or max iterations reached."""
        
        print(f"\n🚀 Starting Mock UI Test - Iteration {self.test_iteration}")
        print(f"📋 Testing {len(self.hands_db.all_hands)} hands...")
        
        iteration_results = {}
        success_count = 0
        failure_count = 0
        
        for hand_id, hand_data in self.hands_db.all_hands.items():
            print(f"\n📖 Testing Hand {hand_id}: {hand_data.metadata.name}")
            
            try:
                success = self._test_single_hand(hand_id, hand_data)
                iteration_results[hand_id] = success
                
                if success:
                    success_count += 1
                    print(f"✅ Hand {hand_id} - SUCCESS")
                else:
                    failure_count += 1
                    print(f"❌ Hand {hand_id} - FAILED")
                    
            except Exception as e:
                print(f"💥 Hand {hand_id} - EXCEPTION: {e}")
                iteration_results[hand_id] = False
                failure_count += 1
                traceback.print_exc()
        
        # Update overall results
        self.results[f"iteration_{self.test_iteration}"] = {
            "results": iteration_results,
            "success_count": success_count,
            "failure_count": failure_count,
            "total_hands": len(self.hands_db.all_hands)
        }
        
        print(f"\n📊 Iteration {self.test_iteration} Results:")
        print(f"   ✅ Successful: {success_count}/{len(self.hands_db.all_hands)}")
        print(f"   ❌ Failed: {failure_count}/{len(self.hands_db.all_hands)}")
        print(f"   📈 Success Rate: {success_count/len(self.hands_db.all_hands)*100:.1f}%")
        
        return iteration_results
    
    def _test_single_hand(self, hand_id: str, hand_data) -> bool:
        """Test a single hand simulation."""
        
        try:
            # Create a test frame to hold the hands review panel
            test_frame = ttk.Frame(self.root)
            
            # Create the hands review panel with mock UI settings
            panel = FPSMHandsReviewPanel(
                parent=test_frame,
                hands_db=self.hands_db,
                # Enable headless mode for faster testing
                debug_mode=True,  # Skip delays
                test_mode=True    # Skip user interactions
            )
            
            # Load the specific hand
            panel.load_hand_data(hand_data)
            
            # Manually set the current hand for simulation (bypass UI selection)
            panel.current_hand = hand_data
            panel.current_hand_index = 0
            
            # Set up the hand for simulation
            panel.setup_hand_for_simulation()
            
            # Enable headless mode in RPGW for ultra-fast testing
            if hasattr(panel, 'rpgw') and panel.rpgw:
                panel.rpgw.headless_mode = True
                panel.rpgw.debug_mode = True
            
            # Track simulation state
            max_actions = 300  # Generous limit
            actions_executed = 0
            timeout_seconds = 30  # 30 second timeout per hand
            start_time = time.time()
            
            # Run simulation until completion
            while panel.simulation_active and not panel.hand_completed:
                
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"⏰ Hand {hand_id} - TIMEOUT after {timeout_seconds}s")
                    return False
                
                # Check action limit
                if actions_executed >= max_actions:
                    print(f"🔄 Hand {hand_id} - ACTION LIMIT reached ({max_actions})")
                    return False
                
                # Execute next action
                panel.next_action()
                actions_executed += 1
                
                # Small delay to prevent infinite tight loops
                time.sleep(0.001)  # 1ms
            
            # Check if simulation completed successfully
            if panel.hand_completed:
                elapsed_time = time.time() - start_time
                print(f"🏁 Hand {hand_id} completed in {elapsed_time:.2f}s with {actions_executed} actions")
                
                # Cleanup
                test_frame.destroy()
                return True
            else:
                print(f"⚠️ Hand {hand_id} - Simulation stopped but hand not completed")
                test_frame.destroy()
                return False
                
        except Exception as e:
            print(f"💥 Exception in hand {hand_id}: {e}")
            traceback.print_exc()
            return False
    
    def run_until_all_pass(self):
        """Keep running tests until all hands pass or max iterations reached."""
        
        while self.test_iteration <= self.max_iterations:
            iteration_results = self.run_all_hands_test()
            
            # Check if all hands passed
            all_passed = all(iteration_results.values())
            
            if all_passed:
                print(f"\n🎉 ALL HANDS PASSED on iteration {self.test_iteration}!")
                self._save_results()
                return True
            
            # Show failed hands
            failed_hands = [hand_id for hand_id, success in iteration_results.items() if not success]
            print(f"\n❌ Failed hands: {failed_hands}")
            
            if self.test_iteration < self.max_iterations:
                print(f"🔄 Starting iteration {self.test_iteration + 1}...")
                self.test_iteration += 1
            else:
                print(f"\n⚠️ Maximum iterations ({self.max_iterations}) reached")
                break
        
        self._save_results()
        return False
    
    def _save_results(self):
        """Save test results to file."""
        results_file = "test_hands_review_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {results_file}")
    
    def get_final_summary(self):
        """Get final test summary."""
        if not self.results:
            return "No test results available"
        
        latest_iteration = f"iteration_{self.test_iteration}"
        if latest_iteration not in self.results:
            latest_iteration = f"iteration_{self.test_iteration - 1}"
        
        if latest_iteration in self.results:
            latest = self.results[latest_iteration]
            return f"""
🏆 FINAL MOCK UI TEST SUMMARY:
===============================
📋 Total Hands Tested: {latest['total_hands']}
✅ Successful: {latest['success_count']}
❌ Failed: {latest['failure_count']}
📈 Success Rate: {latest['success_count']/latest['total_hands']*100:.1f}%
🔄 Iterations Run: {self.test_iteration}
"""
        return "No valid results found"


def main():
    """Main test runner."""
    print("🃏 Poker Hands Review Mock UI Tester")
    print("=" * 50)
    
    tester = MockHandsReviewTester()
    
    try:
        all_passed = tester.run_until_all_pass()
        
        print(tester.get_final_summary())
        
        if all_passed:
            print("🎯 ALL TESTS PASSED! Hands review tab is working correctly.")
            return 0
        else:
            print("⚠️ SOME TESTS FAILED. Check the results for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        return 2
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        traceback.print_exc()
        return 3
    finally:
        # Cleanup
        if hasattr(tester, 'root'):
            tester.root.destroy()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
