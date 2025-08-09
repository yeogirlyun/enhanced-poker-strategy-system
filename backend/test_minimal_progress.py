#!/usr/bin/env python3
"""
MINIMAL test with ZERO debug output - only shows hand numbers and results.
Perfect for tracking progress to 100% success rate.
"""

import sys
import os
import time
import tkinter as tk
import logging

# Suppress ALL logging to eliminate debug output
logging.disable(logging.CRITICAL)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Redirect stdout to suppress debug prints temporarily
from io import StringIO
import contextlib

@contextlib.contextmanager
def suppress_output():
    """Context manager to suppress all print output."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class MinimalProgressTest:
    def __init__(self):
        self.results = []
        
    def run_test(self):
        """Run test with absolutely minimal output."""
        print("🎯 MINIMAL PROGRESS TEST - TRACKING TO 100%")
        print("=" * 50)
        
        try:
            # Create UI with all output suppressed
            with suppress_output():
                root = tk.Tk()
                root.geometry("1x1")
                root.withdraw()
                root.update_idletasks()
                
                panel = FPSMHandsReviewPanel(root)
                root.update_idletasks()
            
            # Get hands (with output suppressed)
            with suppress_output():
                all_hands = []
                if hasattr(panel, 'legendary_hands'):
                    for hand in panel.legendary_hands:
                        category = getattr(hand.metadata, 'category', 'Legendary')
                        hand_id = getattr(hand.metadata, 'id', f'Hand_{len(all_hands)+1}')
                        all_hands.append({'hand': hand, 'category': category, 'id': hand_id})
            
            total_hands = len(all_hands)
            print(f"📊 Testing {total_hands} hands")
            print()
            
            if total_hands == 0:
                print("❌ No hands found!")
                return
            
            # Test hands with ZERO output except progress
            for i, hand_info in enumerate(all_hands):
                hand_number = i + 1
                hand_id = hand_info['id']
                
                print(f"Hand {hand_number:3d}/{total_hands} ({hand_id:8s}): ", end="", flush=True)
                
                try:
                    # Everything suppressed except result
                    with suppress_output():
                        panel.current_hand = hand_info['hand']
                        panel.current_hand_index = i
                        
                        start_time = time.time()
                        panel.start_hand_simulation()
                        
                        if not (panel.simulation_active and panel.fpsm):
                            success = False
                            reason = "setup"
                        else:
                            success = self._run_hand_silently(panel)
                            reason = "timeout" if not success else "passed"
                            
                        elapsed = time.time() - start_time
                        
                        if hasattr(panel, 'quit_simulation'):
                            panel.quit_simulation()
                    
                    # Only print result
                    if success:
                        print(f"✅ ({elapsed:.1f}s)")
                        self.results.append({'hand': hand_number, 'status': 'passed', 'time': elapsed})
                    else:
                        print(f"❌ {reason}")
                        self.results.append({'hand': hand_number, 'status': 'failed', 'reason': reason})
                        
                except Exception as e:
                    print(f"💥 {str(e)[:20]}...")
                    self.results.append({'hand': hand_number, 'status': 'exception', 'error': str(e)})
                
                # Progress summary every 10 hands
                if hand_number % 10 == 0:
                    passed = len([r for r in self.results if r['status'] == 'passed'])
                    rate = (passed / hand_number) * 100
                    print(f"   📈 {hand_number}/{total_hands}: {rate:.0f}% success rate")
                
                # Test only first 20 hands for now
                if hand_number >= 20:
                    print(f"🛑 Tested {hand_number} hands")
                    break
            
            # Final results
            self._print_final_results(total_hands)
            
            with suppress_output():
                root.destroy()
            
        except Exception as e:
            print(f"💥 Test error: {e}")
    
    def _run_hand_silently(self, panel):
        """Run hand with all output suppressed."""
        max_actions = 200  # Increased for multi-player hands
        timeout_seconds = 60  # Longer timeout for complex hands
        start_time = time.time()
        action_count = 0
        
        while (not panel.hand_completed and 
               action_count < max_actions and 
               (time.time() - start_time) < timeout_seconds):
            
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
    
    def _print_final_results(self, total_tested):
        """Print clean final results."""
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'passed'])
        failed = len([r for r in self.results if r['status'] == 'failed'])
        exceptions = len([r for r in self.results if r['status'] == 'exception'])
        
        print()
        print("=" * 50)
        print("🏆 RESULTS SUMMARY")
        print("=" * 50)
        print(f"✅ Passed:     {passed:3d}/{total}")
        print(f"❌ Failed:     {failed:3d}/{total}")
        print(f"💥 Exceptions: {exceptions:3d}/{total}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success:    {success_rate:5.1f}%")
            
            if success_rate == 100:
                print("🎉 🎉 🎉 100% SUCCESS ACHIEVED! 🎉 🎉 🎉")
            elif success_rate >= 95:
                print("🎯 Excellent! Almost perfect!")
            elif success_rate >= 85:
                print("👍 Very good progress!")
            elif success_rate >= 70:
                print("📈 Good progress, more fixes needed")
            else:
                print("🔧 Significant work needed")

if __name__ == "__main__":
    test = MinimalProgressTest()
    test.run_test()
