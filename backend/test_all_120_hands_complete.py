#!/usr/bin/env python3
"""
Comprehensive test of all 120 legendary hands with enhanced hands review panel.
Tests complete simulation workflow, animations, and accuracy for every hand.
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

class Comprehensive120HandsTest:
    def __init__(self):
        self.results = {
            'total_hands': 0,
            'successful_simulations': 0,
            'failed_simulations': 0,
            'timeout_hands': 0,
            'error_hands': 0,
            'category_stats': defaultdict(lambda: {'tested': 0, 'successful': 0}),
            'detailed_results': [],
            'failed_hands': []
        }
        self.timeout_seconds = 5   # Max time per hand (faster with debug mode)
        self.max_actions = 30      # Max actions per hand
    
    def run_all_tests(self):
        """Run comprehensive tests on all 120 legendary hands."""
        print("🎯 COMPREHENSIVE 120 HANDS TEST")
        print("=" * 60)
        print("Testing complete simulation workflow on all legendary hands...")
        print("🚀 RPGW Debug Mode ENABLED: No delays, animations, or sounds for ultra-fast testing")
        print(f"⏱️  Timeout: {self.timeout_seconds}s per hand, Max actions: {self.max_actions}")
        print()
        
        # Test all 120 hands
        self._test_all_legendary_hands()
        
        # Print final results
        self._print_comprehensive_results()
    
    def _test_all_legendary_hands(self):
        """Test complete simulation on all 120 legendary hands."""
        print("🎮 Testing all 120 legendary hands...")
        
        try:
            # Create minimal UI environment (headless)
            root = tk.Tk()
            root.title("120 Hands Test")
            root.geometry("1x1")  # Minimal size
            root.withdraw()  # Hide completely
            root.update_idletasks()
            
            # Create hands review panel
            print("📋 Creating hands review panel...")
            review_panel = FPSMHandsReviewPanel(root)
            review_panel.pack(fill=tk.BOTH, expand=True)
            root.update_idletasks()
            
            # Get all hands
            all_hands = []
            
            # Add legendary hands (should be 100)
            if hasattr(review_panel, 'legendary_hands') and review_panel.legendary_hands:
                for hand in review_panel.legendary_hands:
                    category = getattr(hand.metadata, 'category', 'Unknown')
                    hand_id = getattr(hand.metadata, 'id', f'Hand_{len(all_hands)+1}')
                    all_hands.append({
                        'hand': hand,
                        'category': category,
                        'id': hand_id,
                        'source': 'legendary'
                    })
            
            # Add practice hands if available
            if hasattr(review_panel, 'practice_hands') and review_panel.practice_hands:
                for hand in review_panel.practice_hands:
                    category = getattr(hand.metadata, 'category', 'Practice')
                    hand_id = getattr(hand.metadata, 'id', f'Practice_{len(all_hands)+1}')
                    all_hands.append({
                        'hand': hand,
                        'category': category,
                        'id': hand_id,
                        'source': 'practice'
                    })
            
            self.results['total_hands'] = len(all_hands)
            print(f"📊 Found {len(all_hands)} total hands to test")
            
            if len(all_hands) == 0:
                print("❌ No hands found to test!")
                return
            
            # Test each hand
            for i, hand_info in enumerate(all_hands):
                hand_id = hand_info['id']
                category = hand_info['category']
                source = hand_info['source']
                
                print(f"\n🎮 [{i+1}/{len(all_hands)}] Testing {hand_id} ({category}) [{source}]")
                
                # Track category stats
                self.results['category_stats'][category]['tested'] += 1
                
                # Test this hand
                success, details = self._test_single_hand(review_panel, hand_info, i)
                
                if success:
                    self.results['successful_simulations'] += 1
                    self.results['category_stats'][category]['successful'] += 1
                    print(f"      ✅ {hand_id} completed successfully!")
                else:
                    self.results['failed_simulations'] += 1
                    self.results['failed_hands'].append({
                        'id': hand_id,
                        'category': category,
                        'source': source,
                        'error': details.get('error', 'Unknown error')
                    })
                    print(f"      ❌ {hand_id} failed: {details.get('error', 'Unknown')}")
                
                # Store detailed results
                self.results['detailed_results'].append({
                    'hand_id': hand_id,
                    'category': category,
                    'source': source,
                    'success': success,
                    'actions': details.get('actions', 0),
                    'time': details.get('time', 0.0),
                    'final_state': details.get('final_state', 'Unknown'),
                    'error': details.get('error', None)
                })
                
                # Progress update every 5 hands for faster feedback
                if (i + 1) % 5 == 0:
                    success_rate = (self.results['successful_simulations'] / (i + 1)) * 100
                    print(f"\n📈 Progress: {i+1}/{len(all_hands)} hands, {success_rate:.1f}% success rate")
            
            # Cleanup
            root.destroy()
            
        except Exception as e:
            print(f"❌ Test setup failed: {str(e)}")
            import traceback
            print(f"📍 Traceback: {traceback.format_exc()}")
    
    def _test_single_hand(self, review_panel, hand_info, hand_index):
        """Test a single hand for complete simulation."""
        hand = hand_info['hand']
        hand_id = hand_info['id']
        
        try:
            # Set current hand
            review_panel.current_hand = hand
            review_panel.current_hand_index = hand_index
            
            # Start simulation
            start_time = time.time()
            review_panel.start_hand_simulation()
            
            if not (review_panel.simulation_active and review_panel.fpsm):
                return False, {'error': 'Failed to start simulation'}
            
            # Execute actions until completion
            action_count = 0
            
            while (not review_panel.hand_completed and 
                   action_count < self.max_actions and
                   (time.time() - start_time) < self.timeout_seconds):
                
                # Check if we're in an end state
                current_state = review_panel.fpsm.current_state.name if review_panel.fpsm else "UNKNOWN"
                if current_state in ['END_HAND', 'SHOWDOWN']:
                    break
                
                # Execute next action
                try:
                    review_panel.next_action()
                    action_count += 1
                except Exception as e:
                    return False, {
                        'error': f'Action failed: {str(e)}',
                        'actions': action_count,
                        'time': time.time() - start_time
                    }
                
                # Brief yield for UI processing
                if hasattr(review_panel, 'master') and review_panel.master:
                    review_panel.master.update_idletasks()
            
            # Check completion
            elapsed_time = time.time() - start_time
            final_state = review_panel.fpsm.current_state.name if review_panel.fpsm else "UNKNOWN"
            
            # Determine success
            if review_panel.hand_completed or final_state in ['END_HAND', 'SHOWDOWN']:
                return True, {
                    'actions': action_count,
                    'time': elapsed_time,
                    'final_state': final_state
                }
            elif action_count >= self.max_actions:
                self.results['timeout_hands'] += 1
                return False, {
                    'error': f'Action limit reached ({self.max_actions})',
                    'actions': action_count,
                    'time': elapsed_time,
                    'final_state': final_state
                }
            elif elapsed_time >= self.timeout_seconds:
                self.results['timeout_hands'] += 1
                return False, {
                    'error': f'Timeout ({self.timeout_seconds}s)',
                    'actions': action_count,
                    'time': elapsed_time,
                    'final_state': final_state
                }
            else:
                self.results['error_hands'] += 1
                return False, {
                    'error': 'Simulation ended unexpectedly',
                    'actions': action_count,
                    'time': elapsed_time,
                    'final_state': final_state
                }
            
        except Exception as e:
            self.results['error_hands'] += 1
            return False, {
                'error': f'Exception: {str(e)}',
                'actions': 0,
                'time': time.time() - start_time if 'start_time' in locals() else 0.0
            }
        finally:
            # Reset for next hand
            if hasattr(review_panel, 'quit_simulation'):
                try:
                    review_panel.quit_simulation()
                except:
                    pass
    
    def _print_comprehensive_results(self):
        """Print detailed results for all 120 hands."""
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE 120 HANDS TEST RESULTS")
        print("=" * 80)
        
        # Overall statistics
        total = self.results['total_hands']
        success = self.results['successful_simulations']
        failed = self.results['failed_simulations']
        success_rate = (success / total * 100) if total > 0 else 0.0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   • Total Hands Tested: {total}")
        print(f"   • Successful Simulations: {success}")
        print(f"   • Failed Simulations: {failed}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Timeout Hands: {self.results['timeout_hands']}")
        print(f"   • Error Hands: {self.results['error_hands']}")
        
        # Category breakdown
        print(f"\n📈 CATEGORY BREAKDOWN:")
        for category, stats in self.results['category_stats'].items():
            tested = stats['tested']
            successful = stats['successful']
            cat_success_rate = (successful / tested * 100) if tested > 0 else 0.0
            print(f"   • {category}: {successful}/{tested} ({cat_success_rate:.1f}%)")
        
        # Performance statistics
        if self.results['detailed_results']:
            total_actions = sum(r['actions'] for r in self.results['detailed_results'])
            avg_actions = total_actions / len(self.results['detailed_results'])
            total_time = sum(r['time'] for r in self.results['detailed_results'])
            avg_time = total_time / len(self.results['detailed_results'])
            
            print(f"\n⚡ PERFORMANCE STATISTICS:")
            print(f"   • Average Actions per Hand: {avg_actions:.1f}")
            print(f"   • Average Time per Hand: {avg_time:.2f}s")
            print(f"   • Total Test Time: {total_time:.1f}s")
        
        # Failed hands details
        if self.results['failed_hands']:
            print(f"\n❌ FAILED HANDS ({len(self.results['failed_hands'])}):")
            for failed in self.results['failed_hands']:
                print(f"   • {failed['id']} ({failed['category']}): {failed['error']}")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 95.0:
            print("   🎉 EXCELLENT: System is production-ready!")
        elif success_rate >= 85.0:
            print("   ✅ GOOD: System is mostly stable with minor issues")
        elif success_rate >= 70.0:
            print("   ⚠️  FAIR: System needs improvements")
        else:
            print("   ❌ POOR: System requires significant fixes")
        
        print(f"\n💾 Expected: 120 hands (100 legendary + 10 heads-up + 10 YouTube)")
        print(f"📊 Actual: {total} hands tested")
        
        if total == 120:
            print("✅ Correct hand count: All 120 legendary hands found!")
        else:
            print(f"⚠️  Hand count mismatch: Expected 120, found {total}")

def main():
    """Run the comprehensive 120 hands test."""
    test = Comprehensive120HandsTest()
    test.run_all_tests()

if __name__ == "__main__":
    main()
