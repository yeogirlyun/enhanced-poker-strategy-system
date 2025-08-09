#!/usr/bin/env python3
"""
Batch parallel testing - Run hands in small batches to avoid memory buildup.
"""

import multiprocessing as mp
import sys
import os
import time
import json
from typing import Dict, List

def test_hand_batch(hand_range: tuple) -> List[Dict]:
    """Test a batch of hands in sequence within a single process."""
    start_idx, end_idx = hand_range
    results = []
    
    try:
        # Suppress output for each process
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        # Import UI components
        import tkinter as tk
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        
        # Create UI once for this batch
        root = tk.Tk()
        root.withdraw()
        panel = FPSMHandsReviewPanel(root)
        
        # Enable headless mode
        if hasattr(panel.poker_game_widget, 'headless_mode'):
            panel.poker_game_widget.headless_mode = True
        
        # Test each hand in this batch
        for hand_index in range(start_idx, end_idx):
            if hand_index >= len(panel.legendary_hands):
                results.append({
                    'hand_number': hand_index + 1,
                    'hand_id': f'Hand {hand_index + 1}',
                    'status': 'not_found',
                    'time': 0.0,
                    'actions': 0,
                    'error': 'Hand index out of range'
                })
                continue
                
            hand = panel.legendary_hands[hand_index]
            hand_id = getattr(hand.metadata, 'id', f'Hand {hand_index + 1}')
            
            try:
                # Setup hand
                panel.current_hand = hand
                panel.current_hand_index = hand_index
                
                start_time = time.time()
                panel.start_hand_simulation()
                
                if not (panel.simulation_active and panel.fpsm):
                    results.append({
                        'hand_number': hand_index + 1,
                        'hand_id': hand_id,
                        'status': 'setup_failed',
                        'time': time.time() - start_time,
                        'actions': 0,
                        'error': 'Failed to setup simulation'
                    })
                    continue
                
                # Run simulation with timeout
                action_count = 0
                max_actions = 200
                timeout_seconds = 60  # Increased timeout based on individual success
                
                while (not panel.hand_completed and 
                       action_count < max_actions and 
                       (time.time() - start_time) < timeout_seconds):
                    try:
                        panel.next_action()
                        action_count += 1
                    except Exception:
                        break
                
                elapsed = time.time() - start_time
                
                if panel.hand_completed:
                    status = 'passed'
                elif action_count >= max_actions:
                    status = 'max_actions'
                else:
                    status = 'timeout'
                    
                results.append({
                    'hand_number': hand_index + 1,
                    'hand_id': hand_id,
                    'status': status,
                    'time': elapsed,
                    'actions': action_count,
                    'error': None
                })
                
                # Force cleanup between hands
                if hasattr(panel, 'quit_simulation'):
                    panel.quit_simulation()
                
            except Exception as e:
                results.append({
                    'hand_number': hand_index + 1,
                    'hand_id': hand_id,
                    'status': 'exception',
                    'time': 0.0,
                    'actions': 0,
                    'error': str(e)
                })
        
        # Clean up UI
        root.destroy()
        
    except Exception as e:
        # Batch-level error
        for hand_index in range(start_idx, end_idx):
            results.append({
                'hand_number': hand_index + 1,
                'hand_id': f'Hand {hand_index + 1}',
                'status': 'batch_exception',
                'time': 0.0,
                'actions': 0,
                'error': str(e)
            })
    
    return results

def main():
    """Run batch parallel hand testing."""
    print("🚀 BATCH PARALLEL HAND TESTING")
    print("=" * 50)
    
    # Test parameters
    total_hands = 100  # Test first 100 hands
    batch_size = 10   # 10 hands per batch to limit memory buildup
    max_processes = min(mp.cpu_count(), 10)  # Use available CPUs
    
    # Calculate batches
    batches = []
    for i in range(0, total_hands, batch_size):
        end_idx = min(i + batch_size, total_hands)
        batches.append((i, end_idx))
    
    print(f"📋 Testing {total_hands} hands in {len(batches)} batches of {batch_size}")
    print(f"💻 Using {max_processes} parallel processes")
    print(f"🔄 Each process handles 1 batch sequentially to limit memory usage")
    print()
    
    # Run batches in parallel
    start_time = time.time()
    
    with mp.Pool(max_processes) as pool:
        batch_results = pool.map(test_hand_batch, batches)
    
    # Flatten results
    all_results = []
    for batch_result in batch_results:
        all_results.extend(batch_result)
    
    total_time = time.time() - start_time
    
    # Process results
    passed = sum(1 for r in all_results if r['status'] == 'passed')
    failed = sum(1 for r in all_results if r['status'] not in ['passed'])
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("🏆 BATCH PARALLEL TEST RESULTS")
    print("=" * 80)
    
    # Group results by status
    status_groups = {}
    for result in all_results:
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
    
    # Show success rate progression
    print(f"\n📈 SUCCESS RATE BY BATCH:")
    for i, batch_result in enumerate(batch_results):
        batch_passed = sum(1 for r in batch_result if r['status'] == 'passed')
        batch_total = len(batch_result)
        batch_rate = (batch_passed / batch_total * 100) if batch_total > 0 else 0
        start_hand = i * batch_size + 1
        end_hand = min((i + 1) * batch_size, total_hands)
        print(f"   Batch {i+1} (Hands {start_hand:2d}-{end_hand:2d}): {batch_passed:2d}/{batch_total} ({batch_rate:5.1f}%)")
    
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"✅ Passed:      {passed}/{total_hands} ({passed/total_hands*100:.1f}%)")
    print(f"❌ Failed:      {failed}/{total_hands} ({failed/total_hands*100:.1f}%)")
    print(f"⏱️  Total time:  {total_time:.1f}s")
    print(f"⚡ Avg per hand: {total_time/total_hands:.1f}s")
    print(f"🚀 Parallel batches: {len(batches)} batches")
    
    if passed >= total_hands * 0.9:
        print("🎉 EXCELLENT: 90%+ success rate achieved!")
    elif passed >= total_hands * 0.8:
        print("✅ GOOD: 80%+ success rate achieved!")
    elif passed >= total_hands * 0.7:
        print("📈 PROGRESS: 70%+ success rate - getting there!")
    else:
        print("⚠️  More fixes needed for higher success rate")
    
    # Save detailed results
    with open('batch_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_hands': total_hands,
                'passed': passed,
                'failed': failed,
                'success_rate': passed/total_hands*100,
                'total_time': total_time,
                'avg_time_per_hand': total_time/total_hands,
                'batch_size': batch_size,
                'num_batches': len(batches),
                'max_processes': max_processes
            },
            'results': all_results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: batch_test_results.json")

if __name__ == "__main__":
    # Set multiprocessing start method for macOS compatibility
    mp.set_start_method('spawn', force=True)
    main()
