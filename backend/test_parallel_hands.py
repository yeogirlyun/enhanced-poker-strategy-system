#!/usr/bin/env python3
"""
Parallel hand testing - Run each hand in its own process to avoid memory buildup.
"""

import multiprocessing as mp
import sys
import os
import time
import json
from typing import Dict, List, Tuple

def test_single_hand(hand_index: int) -> Dict:
    """Test a single hand in isolation. This runs in a separate process."""
    try:
        # Import inside the function to avoid pickle issues
        import tkinter as tk
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        
        # Suppress all output
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        # Create fresh UI components
        root = tk.Tk()
        root.withdraw()
        panel = FPSMHandsReviewPanel(root)
        
        # Get the hand
        if hand_index >= len(panel.legendary_hands):
            return {
                'hand_number': hand_index + 1,
                'hand_id': f'Hand {hand_index + 1}',
                'status': 'not_found',
                'time': 0.0,
                'actions': 0,
                'error': 'Hand index out of range'
            }
            
        hand = panel.legendary_hands[hand_index]
        hand_id = getattr(hand.metadata, 'id', f'Hand {hand_index + 1}')
        
        # Setup hand
        panel.current_hand = hand
        panel.current_hand_index = hand_index
        
        start_time = time.time()
        panel.start_hand_simulation()
        
        if not (panel.simulation_active and panel.fpsm):
            return {
                'hand_number': hand_index + 1,
                'hand_id': hand_id,
                'status': 'setup_failed',
                'time': time.time() - start_time,
                'actions': 0,
                'error': 'Failed to setup simulation'
            }
        
        # Enable headless mode for speed
        if hasattr(panel.poker_game_widget, 'headless_mode'):
            panel.poker_game_widget.headless_mode = True
            
        # Run simulation with timeout
        action_count = 0
        max_actions = 200
        timeout_seconds = 30  # Reduced timeout per hand
        
        while (not panel.hand_completed and 
               action_count < max_actions and 
               (time.time() - start_time) < timeout_seconds):
            try:
                panel.next_action()
                action_count += 1
            except Exception as e:
                return {
                    'hand_number': hand_index + 1,
                    'hand_id': hand_id,
                    'status': 'action_failed',
                    'time': time.time() - start_time,
                    'actions': action_count,
                    'error': str(e)
                }
        
        elapsed = time.time() - start_time
        
        if panel.hand_completed:
            status = 'passed'
        elif action_count >= max_actions:
            status = 'max_actions'
        else:
            status = 'timeout'
            
        # Clean up
        root.destroy()
        
        return {
            'hand_number': hand_index + 1,
            'hand_id': hand_id,
            'status': status,
            'time': elapsed,
            'actions': action_count,
            'error': None
        }
        
    except Exception as e:
        return {
            'hand_number': hand_index + 1,
            'hand_id': f'Hand {hand_index + 1}',
            'status': 'exception',
            'time': 0.0,
            'actions': 0,
            'error': str(e)
        }

def print_progress(completed: int, total: int, passed: int):
    """Print progress update."""
    percentage = (completed / total) * 100
    success_rate = (passed / completed) * 100 if completed > 0 else 0
    print(f"📊 Progress: {completed:3d}/{total} ({percentage:5.1f}%) | ✅ {passed:3d} passed ({success_rate:5.1f}%)")

def main():
    """Run parallel hand testing."""
    print("🚀 PARALLEL HAND TESTING")
    print("=" * 50)
    
    # Test parameters
    total_hands = 100  # Test first 100 hands
    max_processes = min(10, mp.cpu_count())  # Use up to 10 processes
    
    print(f"📋 Testing {total_hands} hands using {max_processes} parallel processes")
    print(f"💻 Available CPUs: {mp.cpu_count()}")
    print()
    
    # Create process pool
    start_time = time.time()
    
    with mp.Pool(max_processes) as pool:
        # Submit all hands
        hand_indices = list(range(total_hands))
        results = []
        
        # Use map_async to get results as they complete
        async_result = pool.map_async(test_single_hand, hand_indices)
        
        # Wait for completion with progress updates
        while not async_result.ready():
            time.sleep(2)  # Check every 2 seconds
            # Unfortunately, we can't easily get partial results with map_async
            
        # Get all results
        results = async_result.get()
    
    total_time = time.time() - start_time
    
    # Process results
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] not in ['passed'])
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("🏆 PARALLEL TEST RESULTS")
    print("=" * 80)
    
    # Group results by status
    status_groups = {}
    for result in results:
        status = result['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(result)
    
    # Print summary by status
    for status, group in status_groups.items():
        count = len(group)
        emoji = "✅" if status == "passed" else "❌"
        print(f"{emoji} {status.upper()}: {count} hands")
        
        if status != "passed" and count <= 10:  # Show details for failures
            for result in group[:5]:  # Show first 5
                error_msg = f" ({result['error'][:50]}...)" if result['error'] else ""
                print(f"   - {result['hand_id']}: {result['time']:.1f}s{error_msg}")
            if count > 5:
                print(f"   ... and {count - 5} more")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Passed:      {passed}/{total_hands} ({passed/total_hands*100:.1f}%)")
    print(f"❌ Failed:      {failed}/{total_hands} ({failed/total_hands*100:.1f}%)")
    print(f"⏱️  Total time:  {total_time:.1f}s")
    print(f"⚡ Avg per hand: {total_time/total_hands:.1f}s")
    print(f"🚀 Speedup:     {max_processes}x parallelization")
    
    if passed >= total_hands * 0.9:
        print("🎉 EXCELLENT: 90%+ success rate achieved!")
    elif passed >= total_hands * 0.8:
        print("✅ GOOD: 80%+ success rate achieved!")
    elif passed >= total_hands * 0.7:
        print("📈 PROGRESS: 70%+ success rate - getting there!")
    else:
        print("⚠️  More fixes needed for higher success rate")
    
    # Save detailed results
    with open('parallel_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_hands': total_hands,
                'passed': passed,
                'failed': failed,
                'success_rate': passed/total_hands*100,
                'total_time': total_time,
                'avg_time_per_hand': total_time/total_hands,
                'max_processes': max_processes
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: parallel_test_results.json")

if __name__ == "__main__":
    # Set multiprocessing start method for macOS compatibility
    mp.set_start_method('spawn', force=True)
    main()
