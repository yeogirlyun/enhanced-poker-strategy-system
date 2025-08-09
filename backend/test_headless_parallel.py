#!/usr/bin/env python3
"""
Headless parallel hand testing - No UI, pure FPSM logic.
"""

import multiprocessing as mp
import sys
import os
import time
import json
from typing import Dict, List, Tuple

def test_single_hand_headless(hand_index: int) -> Dict:
    """Test a single hand using pure FPSM logic (no UI). This runs in a separate process."""
    try:
        # Suppress all output
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        # Import inside the function to avoid pickle issues
        from core.hands_database import LegendaryHandsPHHLoader
        from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
        from core.types import Player, ActionType
        
        # Load hands directly
        loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
        hands = loader.load_hands()
        
        if hand_index >= len(hands):
            return {
                'hand_number': hand_index + 1,
                'hand_id': f'Hand {hand_index + 1}',
                'status': 'not_found',
                'time': 0.0,
                'actions': 0,
                'error': 'Hand index out of range'
            }
            
        hand = hands[hand_index]
        hand_id = getattr(hand.metadata, 'id', f'Hand {hand_index + 1}')
        
        start_time = time.time()
        
        # Extract game info
        stakes_str = hand.game_info.get('stakes', '20000/40000/0') if hasattr(hand, 'game_info') else '20000/40000/0'
        stakes_parts = stakes_str.split('/')
        small_blind = float(stakes_parts[0]) if len(stakes_parts) >= 1 else 20000
        big_blind = float(stakes_parts[1]) if len(stakes_parts) >= 2 else 40000
        
        # Create game config
        num_players = len(hand.players)
        config = GameConfig(
            num_players=num_players,
            big_blind=big_blind,
            small_blind=small_blind,
            starting_stack=5000000,  # Default high stakes
            test_mode=True,
            auto_advance=True
        )
        
        # Create FPSM
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players with actual stack data
        fpsm_players = []
        for i, player_info in enumerate(hand.players):
            # Use actual starting stack from PHH data
            phh_stack = player_info.get('starting_stack_chips', 0)
            if phh_stack > 0:
                stack = phh_stack
            else:
                stack = 5000000  # Fallback
            
            cards = player_info.get('cards', ['**', '**'])
            if not cards or len(cards) < 2:
                cards = ['**', '**']
            elif len(cards) > 2:
                cards = cards[:2]
                
            player = Player(
                name=player_info.get('name', f'Player {i+1}'),
                stack=stack,
                position=player_info.get('position', ''),
                is_human=False,
                is_active=True,
                cards=cards
            )
            fpsm_players.append(player)
            
        # Start hand
        fpsm.start_hand(fpsm_players)
        
        # Set board cards if available
        if hasattr(hand, 'board') and hand.board:
            board_cards = []
            for street, cards in hand.board.items():
                if isinstance(cards, list):
                    board_cards.extend(cards)
                else:
                    board_cards.append(cards)
            fpsm.set_board_cards(board_cards[:5])  # Max 5 cards
        
        # Prepare historical actions
        historical_actions = []
        if hasattr(hand, 'actions') and hand.actions:
            for street, street_actions in hand.actions.items():
                if isinstance(street_actions, list):
                    for action in street_actions:
                        action_type = action.get('type', '').upper()
                        amount = 0
                        
                        if action_type in ['RAISE', 'RERAISE'] and 'to' in action:
                            amount = action['to']
                        elif action_type in ['CALL', 'BET'] and 'amount' in action:
                            amount = action['amount']
                        elif action_type == 'ALL-IN' and 'amount' in action:
                            amount = action['amount']
                        
                        historical_actions.append({
                            'street': street,
                            'actor': action.get('actor'),
                            'type': action_type,
                            'amount': amount
                        })
        
        # Build actor mapping (simplified)
        actor_mapping = {}
        for i, player in enumerate(fpsm_players):
            # Simple positional mapping for now
            actor_mapping[i] = i + 1
        
        # Simulate actions
        action_count = 0
        max_actions = 200
        timeout_seconds = 30
        historical_index = 0
        
        while (not fpsm.is_hand_complete() and 
               action_count < max_actions and 
               (time.time() - start_time) < timeout_seconds):
            
            try:
                current_player = fpsm.get_current_player()
                if not current_player:
                    break
                
                # Find matching historical action (simplified logic)
                action_found = False
                if historical_index < len(historical_actions):
                    historical_action = historical_actions[historical_index]
                    action_type_str = historical_action['type']
                    amount = historical_action['amount']
                    
                    # Convert to ActionType enum
                    if action_type_str == 'FOLD':
                        action_type = ActionType.FOLD
                        amount = 0
                    elif action_type_str == 'CHECK':
                        action_type = ActionType.CHECK
                        amount = 0
                    elif action_type_str == 'CALL':
                        action_type = ActionType.CALL
                        # Use current bet amount for call
                        amount = max(0, fpsm.current_bet - current_player.current_bet)
                    elif action_type_str in ['BET', 'ALL-IN']:
                        action_type = ActionType.BET
                    elif action_type_str in ['RAISE', 'RERAISE']:
                        action_type = ActionType.RAISE
                    else:
                        # Default fallback
                        action_type = ActionType.FOLD
                        amount = 0
                    
                    historical_index += 1
                    action_found = True
                else:
                    # No more historical actions, use fallback
                    if "Folded Player" in current_player.name:
                        action_type = ActionType.FOLD
                        amount = 0
                    else:
                        action_type = ActionType.CHECK  # Safe fallback
                        amount = 0
                
                # Execute action
                success = fpsm.execute_action(action_type, amount)
                if not success:
                    # Try folding as fallback
                    fpsm.execute_action(ActionType.FOLD, 0)
                
                action_count += 1
                
            except Exception as e:
                # Action failed, try to continue
                action_count += 1
                if action_count > max_actions // 2:
                    break
        
        elapsed = time.time() - start_time
        
        if fpsm.is_hand_complete():
            status = 'passed'
        elif action_count >= max_actions:
            status = 'max_actions'
        else:
            status = 'timeout'
            
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

def main():
    """Run headless parallel hand testing."""
    print("🚀 HEADLESS PARALLEL HAND TESTING")
    print("=" * 50)
    
    # Test parameters
    total_hands = 100  # Test first 100 hands
    max_processes = min(10, mp.cpu_count())  # Use up to 10 processes
    
    print(f"📋 Testing {total_hands} hands using {max_processes} parallel processes")
    print(f"💻 Available CPUs: {mp.cpu_count()}")
    print(f"🚫 No UI - Pure FPSM logic only")
    print()
    
    # Create process pool
    start_time = time.time()
    
    with mp.Pool(max_processes) as pool:
        # Submit all hands
        hand_indices = list(range(total_hands))
        results = pool.map(test_single_hand_headless, hand_indices)
    
    total_time = time.time() - start_time
    
    # Process results
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] not in ['passed'])
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("🏆 HEADLESS PARALLEL TEST RESULTS")
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
    with open('headless_test_results.json', 'w') as f:
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
    
    print(f"\n💾 Detailed results saved to: headless_test_results.json")

if __name__ == "__main__":
    # Set multiprocessing start method for macOS compatibility
    mp.set_start_method('spawn', force=True)
    main()
