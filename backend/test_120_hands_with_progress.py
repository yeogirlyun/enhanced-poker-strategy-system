#!/usr/bin/env python3
"""
Test all 120 hands with clear hand-by-hand progress feedback.
Shows exactly which hand number is being tested to detect infinite loops.
"""

import sys
import os
import time
import tkinter as tk
from collections import defaultdict

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from core.flexible_poker_state_machine import PokerState

class Progress120HandsTest:
    def __init__(self):
        self.results = {
            'total_hands': 0,
            'successful': 0,
            'failed': 0,
            'by_category': defaultdict(lambda: {'tested': 0, 'passed': 0}),
            'stuck_hands': []
        }
    
    def run_test(self):
        """Run test with detailed hand-by-hand progress."""
        print("🎯 120 HANDS TEST WITH PROGRESS TRACKING")
        print("=" * 50)
        print("🚀 RPGW Debug Mode: No animations/delays")
        print("📍 Will show each hand number 1-120 being tested")
        print()
        
        try:
            # Create headless UI
            root = tk.Tk()
            root.geometry("1x1")
            root.withdraw()
            root.update_idletasks()
            
            # Create panel (debug mode already enabled in panel)
            print("📋 Creating hands review panel...")
            panel = FPSMHandsReviewPanel(root)
            root.update_idletasks()
            
            # Get all hands
            all_hands = []
            if hasattr(panel, 'legendary_hands'):
                for hand in panel.legendary_hands:
                    category = getattr(hand.metadata, 'category', 'Legendary')
                    hand_id = getattr(hand.metadata, 'id', f'Hand_{len(all_hands)+1}')
                    all_hands.append({'hand': hand, 'category': category, 'id': hand_id})
            
            self.results['total_hands'] = len(all_hands)
            print(f"📊 Found {len(all_hands)} hands to test")
            print()
            
            # Test each hand with clear progress
            for i, hand_info in enumerate(all_hands):
                hand_number = i + 1
                hand_id = hand_info['id']
                category = hand_info['category']
                
                print(f"🎮 Testing Hand {hand_number}/120: {hand_id} ({category})")
                
                start_time = time.time()
                success = self._test_hand_with_progress(panel, hand_info, hand_number)
                elapsed = time.time() - start_time
                
                # Track results
                self.results['by_category'][category]['tested'] += 1
                if success:
                    self.results['successful'] += 1
                    self.results['by_category'][category]['passed'] += 1
                    print(f"      ✅ Hand {hand_number} PASSED in {elapsed:.2f}s")
                else:
                    self.results['failed'] += 1
                    self.results['stuck_hands'].append(f"Hand {hand_number}: {hand_id}")
                    print(f"      ❌ Hand {hand_number} FAILED in {elapsed:.2f}s")
                
                # Progress milestone every 10 hands
                if hand_number % 10 == 0:
                    success_rate = (self.results['successful'] / hand_number) * 100
                    print(f"   📈 Milestone {hand_number}/120: {success_rate:.1f}% success rate")
                    print()
            
            # Print final results
            self._print_final_results()
            
            root.destroy()
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _test_hand_with_progress(self, panel, hand_info, hand_number):
        """Test a single hand with detailed progress tracking."""
        try:
            panel.current_hand = hand_info['hand']
            panel.current_hand_index = hand_number - 1
            
            # Start simulation
            print(f"      🚀 Starting simulation for hand {hand_number}...")
            panel.start_hand_simulation()
            
            if not (panel.simulation_active and panel.fpsm):
                print(f"      ❌ Hand {hand_number}: Failed to start simulation")
                return False
            
            # Execute actions with loop detection
            action_count = 0
            max_actions = 20  # Reduced to catch infinite loops faster
            start_time = time.time()
            timeout = 2  # 2 second timeout per hand
            
            print(f"      🎯 Executing actions for hand {hand_number}...")
            
            while (not panel.hand_completed and 
                   action_count < max_actions and 
                   (time.time() - start_time) < timeout):
                
                # Check current state
                state = panel.fpsm.current_state.name if panel.fpsm else "UNKNOWN"
                if state in ['END_HAND', 'SHOWDOWN']:
                    print(f"      🏁 Hand {hand_number}: Reached end state {state}")
                    break
                
                # Show action progress every 5 actions
                if action_count % 5 == 0 and action_count > 0:
                    print(f"         💭 Hand {hand_number}: Action {action_count}, State: {state}")
                
                try:
                    panel.next_action()
                    action_count += 1
                except Exception as e:
                    print(f"      ⚠️ Hand {hand_number}: Action {action_count + 1} failed: {str(e)}")
                    return False
            
            # Check completion
            final_state = panel.fpsm.current_state.name if panel.fpsm else "UNKNOWN"
            elapsed = time.time() - start_time
            
            if panel.hand_completed or final_state in ['END_HAND', 'SHOWDOWN']:
                print(f"      ✅ Hand {hand_number}: Completed with {action_count} actions")
                success = True
            elif action_count >= max_actions:
                print(f"      ⏱️ Hand {hand_number}: Hit action limit ({max_actions})")
                success = False
            elif elapsed >= timeout:
                print(f"      ⏱️ Hand {hand_number}: Timed out after {timeout}s")
                success = False
            else:
                print(f"      ❓ Hand {hand_number}: Ended unexpectedly")
                success = False
            
            # Cleanup
            if hasattr(panel, 'quit_simulation'):
                panel.quit_simulation()
            
            return success
            
        except Exception as e:
            print(f"      💥 Hand {hand_number}: Exception: {str(e)}")
            return False
    
    def _print_final_results(self):
        """Print comprehensive final results."""
        total = self.results['total_hands']
        success = self.results['successful']
        failed = self.results['failed']
        success_rate = (success / total * 100) if total > 0 else 0
        
        print()
        print("=" * 60)
        print("🏆 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Hands Tested: {total}")
        print(f"   Successful: {success}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📈 RESULTS BY CATEGORY:")
        for category, stats in self.results['by_category'].items():
            tested = stats['tested']
            passed = stats['passed']
            rate = (passed / tested * 100) if tested > 0 else 0
            print(f"   {category}: {passed}/{tested} ({rate:.1f}%)")
        
        if self.results['stuck_hands']:
            print(f"\n❌ FAILED HANDS ({len(self.results['stuck_hands'])}):")
            for stuck_hand in self.results['stuck_hands']:
                print(f"   {stuck_hand}")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 95:
            print("   🎉 EXCELLENT: System is production ready!")
        elif success_rate >= 85:
            print("   ✅ GOOD: Minor issues detected")
        elif success_rate >= 70:
            print("   ⚠️  FAIR: Some improvements needed")
        else:
            print("   ❌ POOR: Significant issues require fixing")
        
        print(f"\n💾 HAND COUNT VERIFICATION:")
        if total == 120:
            print("   ✅ Perfect: All 120 legendary hands found!")
        else:
            print(f"   ⚠️  Mismatch: Expected 120, found {total}")

if __name__ == "__main__":
    test = Progress120HandsTest()
    test.run_test()
