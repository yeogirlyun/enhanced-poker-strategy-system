#!/usr/bin/env python3
"""
Individual failure analysis - Debug each failing hand to identify specific issues.
"""

import sys
import os
import time
import json
import tkinter as tk
from typing import Dict, List, Any
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class IndividualFailureDebugger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.panel = FPSMHandsReviewPanel(self.root)
        
        # Load the batch test results to identify failures
        with open('batch_test_results.json', 'r') as f:
            self.batch_results = json.load(f)
        
        # Extract failed hands
        self.failed_hands = [
            r for r in self.batch_results['results'] 
            if r['status'] in ['timeout', 'max_actions', 'setup_failed', 'exception']
        ]
        
        print(f"🔍 Found {len(self.failed_hands)} failed hands to debug")
        
    def debug_single_failure(self, hand_info: Dict) -> Dict:
        """Debug a single failing hand with detailed analysis."""
        hand_number = hand_info['hand_number']
        hand_id = hand_info['hand_id']
        failure_type = hand_info['status']
        
        print(f"\n{'='*80}")
        print(f"🔍 DEBUGGING FAILURE: Hand {hand_number} ({hand_id}) - {failure_type.upper()}")
        print(f"{'='*80}")
        
        hand_index = hand_number - 1
        if hand_index >= len(self.panel.legendary_hands):
            return {
                'hand_id': hand_id,
                'issue': 'hand_not_found',
                'details': f'Hand index {hand_index} out of range',
                'fix_needed': 'Check hand database loading'
            }
        
        hand = self.panel.legendary_hands[hand_index]
        
        # Analyze hand data
        print(f"📋 HAND DATA ANALYSIS:")
        print(f"   ID: {getattr(hand.metadata, 'id', 'No ID')}")
        print(f"   Players: {len(hand.players)}")
        print(f"   Game: {getattr(hand, 'game_info', {})}")
        
        # Check player data
        print(f"\n👥 PLAYER ANALYSIS:")
        issues = []
        for i, player in enumerate(hand.players):
            name = player.get('name', f'Player {i+1}') if isinstance(player, dict) else getattr(player, 'name', f'Player {i+1}')
            stack = player.get('starting_stack_chips', 0) if isinstance(player, dict) else getattr(player, 'starting_stack_chips', 0)
            cards = player.get('cards', []) if isinstance(player, dict) else getattr(player, 'cards', [])
            
            print(f"   {i+1:2d}. {name:20s}: ${stack:>8,} | Cards: {cards}")
            
            if stack == 0:
                issues.append(f"Player {i+1} ({name}) has $0 stack")
            if not cards or len(cards) < 2:
                issues.append(f"Player {i+1} ({name}) has invalid cards: {cards}")
        
        # Check actions
        print(f"\n🎯 ACTION ANALYSIS:")
        total_actions = 0
        if hasattr(hand, 'actions') and hand.actions:
            for street, street_actions in hand.actions.items():
                if isinstance(street_actions, list):
                    action_count = len(street_actions)
                    total_actions += action_count
                    print(f"   {street:8s}: {action_count} actions")
                    
                    # Check for problematic actions
                    for j, action in enumerate(street_actions):
                        action_type = action.get('type', 'UNKNOWN')
                        amount = action.get('amount', action.get('to', 0))
                        actor = action.get('actor', 'Unknown')
                        
                        if action_type in ['RAISE', 'RERAISE'] and amount == 0:
                            issues.append(f"{street} action {j+1}: {action_type} $0 by actor {actor}")
                        elif action_type == 'BET' and amount == 0:
                            issues.append(f"{street} action {j+1}: BET $0 by actor {actor}")
        
        print(f"   Total actions: {total_actions}")
        
        # Check board
        print(f"\n🎴 BOARD ANALYSIS:")
        if hasattr(hand, 'board') and hand.board:
            for street, cards in hand.board.items():
                print(f"   {street:8s}: {cards}")
        else:
            print("   No board data")
            issues.append("Missing board data")
        
        # Identify specific issue type
        if issues:
            print(f"\n⚠️  IDENTIFIED ISSUES:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Now try to simulate and see where it fails
        print(f"\n🚀 SIMULATION TEST:")
        
        try:
            self.panel.current_hand = hand
            self.panel.current_hand_index = hand_index
            
            start_time = time.time()
            self.panel.start_hand_simulation()
            
            if not (self.panel.simulation_active and self.panel.fpsm):
                return {
                    'hand_id': hand_id,
                    'issue': 'setup_failed',
                    'details': 'Failed to initialize FPSM simulation',
                    'fix_needed': 'Check FPSM setup logic',
                    'data_issues': issues
                }
            
            # Enable headless mode
            if hasattr(self.panel.poker_game_widget, 'headless_mode'):
                self.panel.poker_game_widget.headless_mode = True
            
            # Run simulation step by step with detailed logging
            action_count = 0
            max_actions = 50  # Reduced for debugging
            stuck_count = 0
            last_state = None
            last_player = None
            
            print(f"   Starting simulation...")
            
            while (not self.panel.hand_completed and action_count < max_actions):
                try:
                    # Check current state
                    current_state = self.panel.fpsm.current_state.name if self.panel.fpsm and self.panel.fpsm.current_state else "UNKNOWN"
                    current_player = None
                    
                    # Get current player more reliably
                    current_player_name = "Unknown"
                    try:
                        if hasattr(self.panel.fpsm, 'current_player_index') and self.panel.fpsm.current_player_index is not None:
                            player_idx = self.panel.fpsm.current_player_index
                            if hasattr(self.panel.fpsm, 'players') and player_idx < len(self.panel.fpsm.players):
                                current_player_name = self.panel.fpsm.players[player_idx].name
                            else:
                                current_player_name = f"Player{player_idx}"
                        elif hasattr(self.panel.fpsm, 'get_current_player'):
                            current_player = self.panel.fpsm.get_current_player()
                            current_player_name = current_player.name if current_player else "None"
                        else:
                            current_player_name = "N/A"
                    except Exception as e:
                        current_player_name = f"Error: {str(e)[:20]}"
                    
                    print(f"   Action {action_count+1:2d}: State={current_state:15s} Player={current_player_name:20s}")
                    
                    # Check for infinite loops
                    if current_state == last_state and current_player_name == last_player:
                        stuck_count += 1
                        if stuck_count >= 3:
                            return {
                                'hand_id': hand_id,
                                'issue': 'infinite_loop',
                                'details': f'Stuck in state {current_state} with player {current_player_name}',
                                'fix_needed': 'Check action sequence logic or historical action mapping',
                                'data_issues': issues,
                                'stuck_at_action': action_count + 1
                            }
                    else:
                        stuck_count = 0
                    
                    last_state = current_state
                    last_player = current_player_name
                    
                    # Execute next action
                    action_start = time.time()
                    self.panel.next_action()
                    action_time = time.time() - action_start
                    
                    print(f"      → Executed in {action_time:.3f}s")
                    
                    action_count += 1
                    
                    # Check for very slow actions
                    if action_time > 2.0:
                        return {
                            'hand_id': hand_id,
                            'issue': 'slow_action',
                            'details': f'Action {action_count} took {action_time:.1f}s in state {current_state}',
                            'fix_needed': 'Optimize action execution or check for complex logic',
                            'data_issues': issues,
                            'slow_action': action_count
                        }
                    
                except Exception as e:
                    return {
                        'hand_id': hand_id,
                        'issue': 'action_exception',
                        'details': f'Exception on action {action_count + 1}: {str(e)[:100]}',
                        'fix_needed': 'Fix action execution logic',
                        'data_issues': issues,
                        'failed_action': action_count + 1,
                        'exception': str(e)
                    }
            
            elapsed = time.time() - start_time
            
            if self.panel.hand_completed:
                print(f"   ✅ Hand completed successfully in {elapsed:.2f}s with {action_count} actions")
                return {
                    'hand_id': hand_id,
                    'issue': 'false_positive',
                    'details': f'Hand actually completes in {elapsed:.2f}s with {action_count} actions',
                    'fix_needed': 'May need timeout adjustment or was intermittent',
                    'data_issues': issues
                }
            elif action_count >= max_actions:
                return {
                    'hand_id': hand_id,
                    'issue': 'too_many_actions',
                    'details': f'Required more than {max_actions} actions, got to action {action_count}',
                    'fix_needed': 'Check for action loops or increase action limit',
                    'data_issues': issues,
                    'final_state': current_state,
                    'final_player': current_player_name
                }
            else:
                return {
                    'hand_id': hand_id,
                    'issue': 'incomplete_simulation',
                    'details': f'Simulation stopped after {action_count} actions without completion',
                    'fix_needed': 'Check hand completion logic',
                    'data_issues': issues,
                    'final_state': current_state,
                    'final_player': current_player_name
                }
                
        except Exception as e:
            return {
                'hand_id': hand_id,
                'issue': 'simulation_exception',
                'details': f'Simulation failed: {str(e)[:100]}',
                'fix_needed': 'Fix simulation setup or execution',
                'data_issues': issues,
                'exception': str(e)
            }
    
    def analyze_failure_patterns(self):
        """Analyze all failures and group by issue type."""
        print(f"🔍 ANALYZING {len(self.failed_hands)} FAILED HANDS")
        print("=" * 80)
        
        failure_analysis = {}
        
        # Debug first 10 failures in detail
        detailed_count = min(10, len(self.failed_hands))
        print(f"📋 Debugging first {detailed_count} failures in detail...")
        
        for i, hand_info in enumerate(self.failed_hands[:detailed_count]):
            analysis = self.debug_single_failure(hand_info)
            
            issue_type = analysis['issue']
            if issue_type not in failure_analysis:
                failure_analysis[issue_type] = []
            failure_analysis[issue_type].append(analysis)
            
            # Brief pause to avoid overwhelming output
            time.sleep(0.1)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 FAILURE PATTERN ANALYSIS")
        print(f"{'='*80}")
        
        for issue_type, analyses in failure_analysis.items():
            count = len(analyses)
            print(f"\n❌ {issue_type.upper().replace('_', ' ')}: {count} hands")
            
            # Show examples
            for analysis in analyses[:3]:  # Show first 3 examples
                hand_id = analysis['hand_id']
                details = analysis['details']
                fix_needed = analysis['fix_needed']
                print(f"   • {hand_id}: {details}")
                print(f"     → Fix: {fix_needed}")
            
            if count > 3:
                print(f"   ... and {count - 3} more similar cases")
        
        print(f"\n🎯 RECOMMENDED FIXES:")
        priority_fixes = {}
        for issue_type, analyses in failure_analysis.items():
            fix = analyses[0]['fix_needed']
            if fix not in priority_fixes:
                priority_fixes[fix] = 0
            priority_fixes[fix] += len(analyses)
        
        for fix, count in sorted(priority_fixes.items(), key=lambda x: x[1], reverse=True):
            print(f"   {count:2d}x: {fix}")
        
        # Save detailed analysis
        with open('failure_analysis.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_failures_analyzed': detailed_count,
                    'issue_types': {k: len(v) for k, v in failure_analysis.items()},
                    'priority_fixes': priority_fixes
                },
                'detailed_analysis': failure_analysis
            }, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: failure_analysis.json")
        
        self.root.destroy()
        return failure_analysis

if __name__ == "__main__":
    debugger = IndividualFailureDebugger()
    debugger.analyze_failure_patterns()
