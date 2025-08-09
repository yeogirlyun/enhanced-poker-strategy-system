#!/usr/bin/env python3
"""
Simple test to go through hands one by one with clear progress tracking.
Shows exactly which hand number (1-120) is being tested.
"""

import sys
import os
import time
import tkinter as tk
from collections import defaultdict

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class SimpleHandByHandTest:
    def __init__(self):
        self.results = []
        self.current_hand_number = 0
        
    def run_test(self):
        """Run test with clear hand-by-hand progress."""
        print("🎯 SIMPLE HAND-BY-HAND TEST")
        print("=" * 40)
        print("Shows each hand number being tested to detect infinite loops")
        print()
        
        try:
            # Create minimal UI
            root = tk.Tk()
            root.geometry("1x1")
            root.withdraw()
            root.update_idletasks()
            
            # Create panel
            panel = FPSMHandsReviewPanel(root)
            root.update_idletasks()
            
            # Get all hands
            all_hands = []
            if hasattr(panel, 'legendary_hands'):
                for hand in panel.legendary_hands:
                    category = getattr(hand.metadata, 'category', 'Legendary')
                    hand_id = getattr(hand.metadata, 'id', f'Hand_{len(all_hands)+1}')
                    all_hands.append({'hand': hand, 'category': category, 'id': hand_id})
            
            total_hands = len(all_hands)
            print(f"📊 Total hands to test: {total_hands}")
            print()
            
            if total_hands == 0:
                print("❌ No hands found!")
                return
            
            # Test hands one by one with clear progress
            for i, hand_info in enumerate(all_hands):
                self.current_hand_number = i + 1
                hand_id = hand_info['id']
                category = hand_info['category']
                
                print("=" * 80)
                print(f"🎮 🎮 🎮 TESTING HAND {self.current_hand_number}/{total_hands} 🎮 🎮 🎮")
                print(f"   ID: {hand_id}")
                print(f"   Category: {category}")
                print("=" * 80)
                
                try:
                    # Set up the hand
                    panel.current_hand = hand_info['hand']
                    panel.current_hand_index = i
                    
                    # Start simulation with timeout
                    print(f"   🚀 Starting simulation...")
                    start_time = time.time()
                    panel.start_hand_simulation()
                    
                    if not (panel.simulation_active and panel.fpsm):
                        print(f"   ❌ Failed to start simulation")
                        self.results.append({'hand': self.current_hand_number, 'status': 'failed', 'reason': 'setup_failed'})
                        continue
                    
                    # Run with strict loop detection
                    print(f"   🎯 Executing actions...")
                    success = self._run_hand_with_loop_detection(panel)
                    
                    elapsed = time.time() - start_time
                    
                    if success:
                        print(f"   ✅ PASSED in {elapsed:.2f}s")
                        self.results.append({'hand': self.current_hand_number, 'status': 'passed', 'time': elapsed})
                    else:
                        print(f"   ❌ FAILED in {elapsed:.2f}s")
                        self.results.append({'hand': self.current_hand_number, 'status': 'failed', 'reason': 'infinite_loop', 'time': elapsed})
                    
                    # Clean up
                    if hasattr(panel, 'quit_simulation'):
                        panel.quit_simulation()
                    
                except Exception as e:
                    print(f"   💥 EXCEPTION: {str(e)}")
                    self.results.append({'hand': self.current_hand_number, 'status': 'exception', 'error': str(e)})
                
                print()  # Blank line between hands
                
                # Test first 10 hands to verify progress tracking
                if self.current_hand_number >= 10:
                    print(f"🛑 Stopping after {self.current_hand_number} hands to verify progress...")
                    break
            
            # Print results
            self._print_results()
            
            root.destroy()
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _run_hand_with_loop_detection(self, panel):
        """Run a hand with strict loop detection."""
        max_actions = 50  # Increased for complete hands
        timeout_seconds = 15  # Longer timeout for full simulation
        start_time = time.time()
        
        action_count = 0
        last_event_counts = {}
        
        print(f"   ⏳ Running simulation for Hand {self.current_hand_number}...")
        
        while (not panel.hand_completed and 
               action_count < max_actions and 
               (time.time() - start_time) < timeout_seconds):
            
            # Check for end states
            if panel.fpsm:
                state = panel.fpsm.current_state.name
                if state in ['END_HAND', 'SHOWDOWN']:
                    print(f"      🏁 Hand {self.current_hand_number} reached end state: {state}")
                    return True
            
            # Execute next action
            try:
                old_action_count = action_count
                panel.next_action()
                action_count += 1
                
                # Show progress every few actions with hand number
                if action_count % 10 == 0:
                    state = panel.fpsm.current_state.name if panel.fpsm else "UNKNOWN"
                    print(f"      💭 Hand {self.current_hand_number} - Action {action_count}: State={state}")
                
            except Exception as e:
                print(f"      ⚠️ Hand {self.current_hand_number} Action {action_count + 1} failed: {str(e)}")
                return False
        
        # Check why we exited the loop
        if panel.hand_completed:
            print(f"      ✅ Hand completed after {action_count} actions")
            print(f"🎉 🎉 HAND {self.current_hand_number} COMPLETED SUCCESSFULLY! 🎉 🎉")
            return True
        elif action_count >= max_actions:
            print(f"      ⏱️ Hit action limit ({max_actions})")
            return False
        elif (time.time() - start_time) >= timeout_seconds:
            print(f"      ⏱️ Timed out after {timeout_seconds}s")
            return False
        else:
            print(f"      ❓ Unknown exit condition")
            return False
    
    def _print_results(self):
        """Print test results."""
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'passed'])
        failed = len([r for r in self.results if r['status'] == 'failed'])
        exceptions = len([r for r in self.results if r['status'] == 'exception'])
        
        print("=" * 50)
        print("🏆 TEST RESULTS")
        print("=" * 50)
        print(f"📊 Total Tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Exceptions: {exceptions}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print()
        print("📋 DETAILED RESULTS:")
        for result in self.results:
            hand_num = result['hand']
            status = result['status']
            if status == 'passed':
                time_taken = result.get('time', 0)
                print(f"   Hand {hand_num}: ✅ PASSED ({time_taken:.2f}s)")
            elif status == 'failed':
                reason = result.get('reason', 'unknown')
                print(f"   Hand {hand_num}: ❌ FAILED ({reason})")
            else:
                error = result.get('error', 'unknown')
                print(f"   Hand {hand_num}: 💥 EXCEPTION ({error})")

if __name__ == "__main__":
    test = SimpleHandByHandTest()
    test.run_test()
