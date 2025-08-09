#!/usr/bin/env python3
"""
Fast test of all 120 legendary hands with minimal output.
Shows progress and summary results only.
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

class Fast120HandsTest:
    def __init__(self):
        self.results = {
            'total_hands': 0,
            'successful': 0,
            'failed': 0,
            'by_category': defaultdict(lambda: {'tested': 0, 'passed': 0})
        }
    
    def run_test(self):
        """Run fast test on all 120 hands with minimal output."""
        print("🚀 FAST 120 HANDS TEST - Debug Mode Enabled")
        print("=" * 50)
        
        try:
            # Create headless UI
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
            
            self.results['total_hands'] = len(all_hands)
            print(f"📊 Testing {len(all_hands)} hands...")
            
            # Test each hand
            for i, hand_info in enumerate(all_hands):
                # Simple progress indicator
                if i % 20 == 0:
                    print(f"   Progress: {i}/{len(all_hands)} hands...")
                
                success = self._test_hand(panel, hand_info, i)
                category = hand_info['category']
                
                self.results['by_category'][category]['tested'] += 1
                if success:
                    self.results['successful'] += 1
                    self.results['by_category'][category]['passed'] += 1
                else:
                    self.results['failed'] += 1
            
            # Print results
            self._print_results()
            
            root.destroy()
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    def _test_hand(self, panel, hand_info, index):
        """Test a single hand quickly."""
        try:
            panel.current_hand = hand_info['hand']
            panel.current_hand_index = index
            
            # Start simulation
            panel.start_hand_simulation()
            if not (panel.simulation_active and panel.fpsm):
                return False
            
            # Execute actions quickly (max 25 actions, 3 second timeout)
            actions = 0
            start_time = time.time()
            
            while (not panel.hand_completed and 
                   actions < 25 and 
                   (time.time() - start_time) < 3):
                
                state = panel.fpsm.current_state.name if panel.fpsm else "UNKNOWN"
                if state in ['END_HAND', 'SHOWDOWN']:
                    break
                
                panel.next_action()
                actions += 1
            
            # Check success
            final_state = panel.fpsm.current_state.name if panel.fpsm else "UNKNOWN"
            success = (panel.hand_completed or final_state in ['END_HAND', 'SHOWDOWN'])
            
            # Quick cleanup
            if hasattr(panel, 'quit_simulation'):
                panel.quit_simulation()
            
            return success
            
        except Exception:
            return False
    
    def _print_results(self):
        """Print summary results."""
        total = self.results['total_hands']
        success = self.results['successful']
        success_rate = (success / total * 100) if total > 0 else 0
        
        print(f"\n🏆 RESULTS SUMMARY")
        print(f"   Total Hands: {total}")
        print(f"   Successful: {success}")
        print(f"   Failed: {self.results['failed']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📈 BY CATEGORY:")
        for category, stats in self.results['by_category'].items():
            tested = stats['tested']
            passed = stats['passed']
            rate = (passed / tested * 100) if tested > 0 else 0
            print(f"   {category}: {passed}/{tested} ({rate:.1f}%)")
        
        print(f"\n🎯 ASSESSMENT:")
        if success_rate >= 95:
            print("   🎉 EXCELLENT: All systems working!")
        elif success_rate >= 85:
            print("   ✅ GOOD: Minor issues detected")
        elif success_rate >= 70:
            print("   ⚠️  FAIR: Some improvements needed")
        else:
            print("   ❌ POOR: Significant issues found")
        
        if total == 120:
            print("   ✅ Correct count: All 120 hands found!")
        else:
            print(f"   ⚠️  Count mismatch: Expected 120, got {total}")

if __name__ == "__main__":
    test = Fast120HandsTest()
    test.run_test()
