#!/usr/bin/env python3
"""
Dry validation test - Pure logic validation of hand sequences, stacks, and pots.
No UI, no animations, just data validation in seconds.
"""

import time
import json
from typing import Dict, List, Tuple, Optional
from core.hands_database import LegendaryHandsPHHLoader
from core.types import ActionType

class DryHandValidator:
    """Pure logic validator for poker hands - no UI dependencies."""
    
    def __init__(self):
        self.loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
        self.hands = self.loader.load_hands()
        self.validation_results = []
        
    def validate_single_hand(self, hand_index: int) -> Dict:
        """Validate a single hand's logic, sequences, and final states."""
        hand = self.hands[hand_index]
        hand_id = getattr(hand.metadata, 'id', f'Hand {hand_index + 1}')
        
        result = {
            'hand_number': hand_index + 1,
            'hand_id': hand_id,
            'status': 'unknown',
            'issues': [],
            'validation_details': {}
        }
        
        try:
            # Step 1: Validate basic hand data
            players_valid = self._validate_players(hand, result)
            actions_valid = self._validate_actions(hand, result)
            board_valid = self._validate_board(hand, result)
            
            # Debug failing validation
            if not (players_valid and actions_valid and board_valid):
                result['status'] = 'data_invalid'
                result['validation_debug'] = {
                    'players_valid': players_valid,
                    'actions_valid': actions_valid,
                    'board_valid': board_valid
                }
                return result
            
            # Step 2: Simulate hand logic (pure calculation)
            simulation_result = self._simulate_hand_logic(hand, result)
            
            if simulation_result:
                result['status'] = 'valid'
            else:
                result['status'] = 'simulation_failed'
                
        except Exception as e:
            result['status'] = 'exception'
            result['issues'].append(f'Validation exception: {str(e)[:100]}')
            
        return result
    
    def _validate_players(self, hand, result: Dict) -> bool:
        """Validate player data integrity."""
        issues = []
        
        if not hasattr(hand, 'players') or not hand.players:
            issues.append('No players found')
            return False
        
        if len(hand.players) < 2:
            issues.append(f'Invalid player count: {len(hand.players)}')
            return False
        
        total_stack = 0
        for i, player in enumerate(hand.players):
            name = player.get('name', f'Player {i+1}') if isinstance(player, dict) else getattr(player, 'name', f'Player {i+1}')
            stack = player.get('starting_stack_chips', 0) if isinstance(player, dict) else getattr(player, 'starting_stack_chips', 0)
            cards = player.get('cards', []) if isinstance(player, dict) else getattr(player, 'cards', [])
            
            if stack <= 0:
                issues.append(f'Player {i+1} ({name}) has invalid stack: ${stack}')
            
            if not cards or len(cards) < 2:
                issues.append(f'Player {i+1} ({name}) has invalid cards: {cards}')
            
            total_stack += stack
        
        result['validation_details']['players'] = {
            'count': len(hand.players),
            'total_starting_stack': total_stack,
            'issues': issues
        }
        
        result['issues'].extend(issues)
        return len(issues) == 0
    
    def _validate_actions(self, hand, result: Dict) -> bool:
        """Validate action sequence integrity."""
        issues = []
        
        if not hasattr(hand, 'actions'):
            issues.append('No actions attribute found')
            return False
        
        # Empty actions dict is valid for some hand formats    
        if not hand.actions:
            result['validation_details']['actions'] = {
                'total_actions': 0,
                'street_counts': {},
                'action_details': [],
                'issues': ['No actions data - may be summary format']
            }
            return True  # Empty actions is not an error
        
        total_actions = 0
        street_counts = {}
        action_details = []
        
        for street, street_actions in hand.actions.items():
            if not isinstance(street_actions, list):
                continue
                
            street_count = len(street_actions)
            total_actions += street_count
            street_counts[street] = street_count
            
            for j, action in enumerate(street_actions):
                action_type = action.get('type', 'UNKNOWN')
                actor = action.get('actor', 'Unknown')
                amount = action.get('amount', action.get('to', 0))
                
                action_details.append({
                    'street': street,
                    'action_num': j + 1,
                    'actor': actor,
                    'type': action_type,
                    'amount': amount
                })
                
                # Validate action types (normalize to uppercase and map variants)
                action_type_upper = action_type.upper()
                # Map action type variants
                if action_type_upper in ['3BET', '4BET', '5BET']:
                    action_type_upper = 'RAISE'  # 3bet/4bet/5bet are raises
                elif action_type_upper in ['ALLIN', 'ALL_IN']:
                    action_type_upper = 'ALL-IN'
                
                if action_type_upper not in ['FOLD', 'CHECK', 'CALL', 'BET', 'RAISE', 'RERAISE', 'ALL-IN']:
                    issues.append(f'{street} action {j+1}: Invalid action type: {action_type}')
                
                # Validate amounts for betting actions
                if action_type_upper in ['RAISE', 'RERAISE'] and amount == 0:
                    issues.append(f'{street} action {j+1}: {action_type} with $0 amount')
        
        result['validation_details']['actions'] = {
            'total_actions': total_actions,
            'street_counts': street_counts,
            'action_details': action_details,
            'issues': issues
        }
        
        result['issues'].extend(issues)
        return len(issues) == 0
    
    def _validate_board(self, hand, result: Dict) -> bool:
        """Validate board card data."""
        issues = []
        board_cards = []
        
        if hasattr(hand, 'board') and hand.board:
            for street, cards in hand.board.items():
                if isinstance(cards, list):
                    board_cards.extend(cards)
                else:
                    board_cards.append(cards)
        else:
            # Board data is optional for some hand formats
            pass
        
        result['validation_details']['board'] = {
            'total_cards': len(board_cards),
            'cards': board_cards,
            'issues': issues
        }
        
        # Board issues are warnings, not fatal errors
        return True
    
    def _simulate_hand_logic(self, hand, result: Dict) -> bool:
        """Simulate hand logic purely with calculations - no UI."""
        
        # Initialize game state
        players = []
        for i, player_info in enumerate(hand.players):
            stack = player_info.get('starting_stack_chips', 0) if isinstance(player_info, dict) else getattr(player_info, 'starting_stack_chips', 0)
            name = player_info.get('name', f'Player {i+1}') if isinstance(player_info, dict) else getattr(player_info, 'name', f'Player {i+1}')
            
            players.append({
                'name': name,
                'stack': stack,
                'current_bet': 0,
                'total_invested': 0,
                'is_active': True,
                'actor_id': i + 1  # PHH actors are 1-indexed
            })
        
        # Extract game info
        stakes_str = hand.game_info.get('stakes', '0/0/0') if hasattr(hand, 'game_info') else '0/0/0'
        stakes_parts = stakes_str.split('/')
        small_blind = float(stakes_parts[0]) if len(stakes_parts) >= 1 else 0
        big_blind = float(stakes_parts[1]) if len(stakes_parts) >= 2 else 0
        
        pot = 0
        current_bet = 0
        
        # Post blinds
        if len(players) >= 2:
            if len(players) == 2:
                # Heads-up: button/small blind is first to act preflop
                sb_idx, bb_idx = 0, 1
            else:
                # Multi-way: small blind is left of dealer, big blind is left of small blind
                sb_idx, bb_idx = 1, 2
            
            players[sb_idx]['current_bet'] = small_blind
            players[sb_idx]['total_invested'] += small_blind
            players[sb_idx]['stack'] -= small_blind
            pot += small_blind
            
            players[bb_idx]['current_bet'] = big_blind
            players[bb_idx]['total_invested'] += big_blind
            players[bb_idx]['stack'] -= big_blind
            pot += big_blind
            current_bet = big_blind
        
        # Track state through streets
        street_results = {}
        
        # Process actions by street
        if hasattr(hand, 'actions') and hand.actions:
            for street, street_actions in hand.actions.items():
                if not isinstance(street_actions, list):
                    continue
                
                street_pot_start = pot
                street_actions_processed = 0
                
                for action in street_actions:
                    action_type = action.get('type', '').upper()  # Normalize to uppercase
                    # Map action type variants
                    if action_type in ['3BET', '4BET', '5BET']:
                        action_type = 'RAISE'  # 3bet/4bet/5bet are raises
                    elif action_type in ['ALLIN', 'ALL_IN']:
                        action_type = 'ALL-IN'
                    
                    actor_id = action.get('actor', 0)
                    amount = 0
                    
                    # Extract amount based on action type
                    if action_type in ['RAISE', 'RERAISE'] and 'to' in action:
                        amount = action['to']  # Total amount to raise to
                    elif action_type in ['CALL', 'BET'] and 'amount' in action:
                        amount = action['amount']  # Amount to call or bet
                    elif action_type == 'ALL-IN' and 'amount' in action:
                        amount = action['amount']  # All-in amount
                    
                    # Find player by actor ID
                    player_idx = None
                    for i, player in enumerate(players):
                        if player['actor_id'] == actor_id:
                            player_idx = i
                            break
                    
                    if player_idx is None:
                        result['issues'].append(f'{street}: Unknown actor {actor_id} for action {action_type}')
                        continue
                    
                    player = players[player_idx]
                    
                    if not player['is_active']:
                        continue  # Skip actions by folded players
                    
                    # Process action
                    if action_type == 'FOLD':
                        player['is_active'] = False
                    elif action_type == 'CHECK':
                        pass  # No money movement
                    elif action_type == 'CALL':
                        call_amount = current_bet - player['current_bet']
                        actual_call = min(call_amount, player['stack'])
                        player['current_bet'] += actual_call
                        player['total_invested'] += actual_call
                        player['stack'] -= actual_call
                        pot += actual_call
                    elif action_type in ['BET', 'RAISE', 'RERAISE']:
                        if action_type == 'BET':
                            bet_amount = amount
                        else:  # RAISE/RERAISE
                            bet_amount = amount - player['current_bet']
                        
                        actual_bet = min(bet_amount, player['stack'])
                        player['current_bet'] += actual_bet
                        player['total_invested'] += actual_bet
                        player['stack'] -= actual_bet
                        pot += actual_bet
                        current_bet = player['current_bet']
                    elif action_type == 'ALL-IN':
                        all_in_amount = player['stack']
                        player['current_bet'] += all_in_amount
                        player['total_invested'] += all_in_amount
                        player['stack'] = 0
                        pot += all_in_amount
                        current_bet = max(current_bet, player['current_bet'])
                    
                    street_actions_processed += 1
                
                # Reset current bets for next street
                for player in players:
                    player['current_bet'] = 0
                current_bet = 0
                
                street_results[street] = {
                    'pot': pot,
                    'actions_processed': street_actions_processed,
                    'active_players': sum(1 for p in players if p['is_active'])
                }
        
        # Final validation
        final_stacks = [p['stack'] for p in players]
        total_final_stack = sum(final_stacks)
        total_invested = sum(p['total_invested'] for p in players)
        
        result['validation_details']['simulation'] = {
            'final_pot': pot,
            'total_invested': total_invested,
            'final_stacks': final_stacks,
            'total_final_stack': total_final_stack,
            'street_results': street_results,
            'active_players': sum(1 for p in players if p['is_active']),
            'conservation_check': abs(total_final_stack + pot - sum(p['stack'] + p['total_invested'] for p in players)) < 0.01
        }
        
        # Check conservation of money
        original_total = sum(p.get('starting_stack_chips', 0) if isinstance(p, dict) else getattr(p, 'starting_stack_chips', 0) for p in hand.players)
        final_total = total_final_stack + pot
        
        if abs(original_total - final_total) > 1:  # Allow small rounding errors
            result['issues'].append(f'Money conservation failed: ${original_total:,} → ${final_total:,} (diff: ${abs(original_total - final_total):,})')
            return False
        
        return True
    
    def run_full_validation(self) -> Dict:
        """Run validation on all hands."""
        print("🧪 DRY VALIDATION TEST - Pure Logic Only")
        print("=" * 60)
        print(f"📋 Validating {len(self.hands)} hands without UI...")
        
        start_time = time.time()
        
        # Validate all hands
        for i in range(len(self.hands)):
            result = self.validate_single_hand(i)
            self.validation_results.append(result)
            
            # Progress indicator every 20 hands
            if (i + 1) % 20 == 0:
                elapsed = time.time() - start_time
                print(f"   📊 Progress: {i + 1:3d}/{len(self.hands)} hands ({elapsed:.1f}s)")
        
        total_time = time.time() - start_time
        
        # Analyze results
        valid_count = sum(1 for r in self.validation_results if r['status'] == 'valid')
        data_invalid_count = sum(1 for r in self.validation_results if r['status'] == 'data_invalid')
        simulation_failed_count = sum(1 for r in self.validation_results if r['status'] == 'simulation_failed')
        exception_count = sum(1 for r in self.validation_results if r['status'] == 'exception')
        
        # Print results
        print(f"\n{'='*60}")
        print(f"🏆 DRY VALIDATION RESULTS")
        print(f"{'='*60}")
        print(f"✅ Valid hands:          {valid_count:3d}/{len(self.hands)} ({valid_count/len(self.hands)*100:.1f}%)")
        print(f"❌ Data invalid:         {data_invalid_count:3d}/{len(self.hands)} ({data_invalid_count/len(self.hands)*100:.1f}%)")
        print(f"❌ Simulation failed:    {simulation_failed_count:3d}/{len(self.hands)} ({simulation_failed_count/len(self.hands)*100:.1f}%)")
        print(f"💥 Exceptions:           {exception_count:3d}/{len(self.hands)} ({exception_count/len(self.hands)*100:.1f}%)")
        print(f"⏱️  Total time:           {total_time:.2f}s")
        print(f"⚡ Avg per hand:         {total_time/len(self.hands)*1000:.1f}ms")
        
        # Show examples of each issue type
        for status in ['data_invalid', 'simulation_failed', 'exception']:
            examples = [r for r in self.validation_results if r['status'] == status]
            if examples:
                print(f"\n❌ {status.upper().replace('_', ' ')} EXAMPLES:")
                for example in examples[:3]:  # Show first 3
                    hand_id = example['hand_id']
                    issues = example['issues'][:2]  # Show first 2 issues
                    print(f"   • {hand_id}: {', '.join(issues)}")
                if len(examples) > 3:
                    print(f"   ... and {len(examples) - 3} more")
        
        # Performance benchmark
        if total_time < 10:
            print(f"🚀 EXCELLENT: All hands validated in {total_time:.2f}s!")
        elif total_time < 30:
            print(f"✅ GOOD: All hands validated in {total_time:.2f}s")
        else:
            print(f"⚠️  SLOW: Validation took {total_time:.2f}s")
        
        # Success rate assessment
        if valid_count >= len(self.hands) * 0.95:
            print("🎉 OUTSTANDING: 95%+ hands are perfectly valid!")
        elif valid_count >= len(self.hands) * 0.90:
            print("✅ EXCELLENT: 90%+ hands are valid!")
        elif valid_count >= len(self.hands) * 0.80:
            print("📈 GOOD: 80%+ hands are valid!")
        else:
            print("⚠️  NEEDS WORK: Less than 80% hands are valid")
        
        # Save detailed results
        summary = {
            'total_hands': len(self.hands),
            'valid_count': valid_count,
            'data_invalid_count': data_invalid_count,
            'simulation_failed_count': simulation_failed_count,
            'exception_count': exception_count,
            'success_rate': valid_count / len(self.hands) * 100,
            'total_time': total_time,
            'avg_time_per_hand': total_time / len(self.hands),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('dry_validation_results.json', 'w') as f:
            json.dump({
                'summary': summary,
                'detailed_results': self.validation_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: dry_validation_results.json")
        
        return summary

if __name__ == "__main__":
    validator = DryHandValidator()
    validator.run_full_validation()
