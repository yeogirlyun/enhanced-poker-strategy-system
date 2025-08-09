#!/usr/bin/env python3
"""
Clean test with minimal output - just hand numbers and results.
Shows clear progress through all hands.
"""

import sys
import os
import time
import tkinter as tk

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class CleanProgressTest:
    def __init__(self):
        self.results = []
        
    def run_test(self):
        """Run test with minimal output - just progress and results."""
        print("🎯 CLEAN PROGRESS TEST - 100% SUCCESS RATE TARGET")
        print("=" * 60)
        
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
            print(f"📊 Testing {total_hands} hands for 100% success rate")
            print()
            
            if total_hands == 0:
                print("❌ No hands found!")
                return
            
            # Test hands with minimal output
            for i, hand_info in enumerate(all_hands):
                hand_number = i + 1
                hand_id = hand_info['id']
                
                # Clear progress line
                print(f"🎮 Hand {hand_number:3d}/{total_hands} ({hand_id}): ", end="", flush=True)
                
                try:
                    # Set up the hand
                    panel.current_hand = hand_info['hand']
                    panel.current_hand_index = i
                    
                    # Start simulation
                    start_time = time.time()
                    panel.start_hand_simulation()
                    
                    if not (panel.simulation_active and panel.fpsm):
                        print("❌ SETUP FAILED")
                        self.results.append({'hand': hand_number, 'status': 'failed', 'reason': 'setup'})
                        continue
                    
                    # Run simulation
                    success = self._run_hand_quietly(panel)
                    elapsed = time.time() - start_time
                    
                    if success:
                        print(f"✅ PASSED ({elapsed:.1f}s)")
                        self.results.append({'hand': hand_number, 'status': 'passed', 'time': elapsed})
                    else:
                        print(f"❌ FAILED ({elapsed:.1f}s)")
                        self.results.append({'hand': hand_number, 'status': 'failed', 'reason': 'timeout'})
                        
                    # Clean up
                    if hasattr(panel, 'quit_simulation'):
                        panel.quit_simulation()
                        
                except Exception as e:
                    print(f"💥 EXCEPTION: {str(e)[:50]}...")
                    self.results.append({'hand': hand_number, 'status': 'exception', 'error': str(e)})
                
                # Progress update every 10 hands
                if hand_number % 10 == 0:
                    passed = len([r for r in self.results if r['status'] == 'passed'])
                    rate = (passed / hand_number) * 100
                    print(f"📈 Progress: {hand_number}/{total_hands} hands, {rate:.1f}% success rate")
                    print()
                
                # Stop at 20 hands for initial verification
                if hand_number >= 20:
                    print(f"🛑 Stopping after {hand_number} hands for verification...")
                    break
            
            # Print final results
            self._print_results()
            root.destroy()
            
        except Exception as e:
            print(f"💥 Test framework error: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _run_hand_quietly(self, panel):
        """Run a hand with minimal output - just check completion."""
        max_actions = 100  # Generous limit
        timeout_seconds = 20  # Generous timeout
        start_time = time.time()
        action_count = 0
        
        while (not panel.hand_completed and 
               action_count < max_actions and 
               (time.time() - start_time) < timeout_seconds):
            
            # Check for end states
            if panel.fpsm:
                state = panel.fpsm.current_state.name
                if state in ['END_HAND', 'SHOWDOWN']:
                    return True
            
            try:
                panel.next_action()
                action_count += 1
            except Exception:
                return False
        
        return panel.hand_completed
    
    def _print_results(self):
        """Print final test results."""
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'passed'])
        failed = len([r for r in self.results if r['status'] == 'failed'])
        exceptions = len([r for r in self.results if r['status'] == 'exception'])
        
        print()
        print("=" * 60)
        print("🏆 FINAL RESULTS")
        print("=" * 60)
        print(f"📊 Total Tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Exceptions: {exceptions}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("🎉 🎉 🎉 100% SUCCESS RATE ACHIEVED! 🎉 🎉 🎉")
            elif success_rate >= 90:
                print("🎯 Excellent! Very close to 100%")
            elif success_rate >= 75:
                print("👍 Good progress, some issues to fix")
            else:
                print("🔧 More work needed to reach 100%")

if __name__ == "__main__":
    test = CleanProgressTest()
    test.run_test()
