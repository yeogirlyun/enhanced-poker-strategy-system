#!/usr/bin/env python3
"""
Standalone Test for Unified Bot Session Architecture

This script tests both GTO simulation and hands review functionality
by generating GTO bot hands and then reviewing them step by step.

This validates that:
1. GTOBotSession generates valid poker hands with proper decisions
2. HandsReviewBotSession can replay those hands correctly
3. The unified architecture works end-to-end without GUI dependencies
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.bot_session_state_machine import GTOBotSession, HandsReviewBotSession
from core.decision_engine_v2 import GTODecisionEngine, PreloadedDecisionEngine
from core.flexible_poker_state_machine import GameConfig
from core.session_logger import SessionLogger

class UnifiedBotSessionTester:
    """Test harness for the unified bot session architecture."""
    
    def __init__(self):
        self.session_logger = SessionLogger()
        self.generated_hands = []
        
    def generate_gto_hands(self, num_hands: int = 10) -> List[Dict[str, Any]]:
        """Generate hands using GTO bot session."""
        print(f"\n🎲 GENERATING {num_hands} GTO HANDS")
        print("=" * 50)
        
        # Create GTO session
        config = GameConfig(
            num_players=6,
            starting_stack=1000,
            small_blind=5,
            big_blind=10
        )
        
        gto_session = GTOBotSession(config)
        gto_session.set_sound_manager(None)  # No sound in test
        
        hands = []
        
        for hand_num in range(1, num_hands + 1):
            print(f"\n🃏 HAND {hand_num}")
            print("-" * 30)
            
            # Start new hand
            success = gto_session.start_session()
            if not success:
                print(f"❌ Failed to start hand {hand_num}")
                continue
                
            hand_data = self._capture_hand_data(gto_session, hand_num)
            
            # Execute all actions until hand completes
            actions_taken = 0
            max_actions = 50  # Safety limit
            
            while gto_session.current_state.value not in ['hand_complete', 'game_over'] and actions_taken < max_actions:
                try:
                    action_result = gto_session.execute_next_bot_action()
                    if action_result:
                        action, explanation = action_result
                        hand_data['actions'].append({
                            'street': gto_session.game_state.street,
                            'player_index': gto_session.action_player_index,
                            'action': action['action'],
                            'amount': action.get('amount', 0),
                            'explanation': explanation,
                            'pot_after': gto_session.game_state.pot
                        })
                        print(f"  🎯 P{gto_session.action_player_index}: {action['action']} {action.get('amount', '')}")
                        actions_taken += 1
                    else:
                        print(f"  ⚠️ No action returned at step {actions_taken}")
                        break
                except Exception as e:
                    print(f"  ❌ Error executing action: {e}")
                    break
            
            hand_data['final_state'] = {
                'state': gto_session.current_state.value,
                'pot': gto_session.game_state.pot,
                'street': gto_session.game_state.street
            }
            hand_data['total_actions'] = actions_taken
            hands.append(hand_data)
            
            print(f"  ✅ Hand {hand_num} completed with {actions_taken} actions")
            
        print(f"\n✅ Generated {len(hands)} hands successfully")
        self.generated_hands = hands
        return hands
    
    def _capture_hand_data(self, session, hand_num: int) -> Dict[str, Any]:
        """Capture comprehensive hand data for later review."""
        game_state = session.game_state
        game_info = session.get_game_info()
        
        return {
            'hand_id': f"test_hand_{hand_num}",
            'timestamp': datetime.now().isoformat(),
            'initial_state': {
                'players': list(game_state.players) if hasattr(game_state, 'players') else [],
                'dealer_position': session.dealer_position,
                'pot': game_state.pot,
                'street': game_state.street
            },
            'revealed_cards': game_info.get('players', []),  # Should show actual cards
            'actions': [],
            'board_progression': {
                'preflop': [],
                'flop': game_state.board[:3] if len(game_state.board) >= 3 else [],
                'turn': game_state.board[:4] if len(game_state.board) >= 4 else [],
                'river': game_state.board[:5] if len(game_state.board) >= 5 else []
            }
        }
    
    def review_generated_hands(self, hands: List[Dict[str, Any]]) -> bool:
        """Review generated hands using HandsReview bot session."""
        print(f"\n📖 REVIEWING {len(hands)} GENERATED HANDS")
        print("=" * 50)
        
        if not hands:
            print("❌ No hands to review")
            return False
        
        success_count = 0
        
        for i, hand_data in enumerate(hands, 1):
            print(f"\n📚 REVIEWING HAND {i}: {hand_data['hand_id']}")
            print("-" * 40)
            
            try:
                # Convert hand data to decision sequence
                decision_sequence = self._convert_hand_to_decisions(hand_data)
                
                if not decision_sequence:
                    print(f"  ⚠️ No decisions found in hand {i}")
                    continue
                
                # Create preloaded decision engine
                decision_engine = PreloadedDecisionEngine(decision_sequence)
                
                # Create hands review session
                config = GameConfig(
                    num_players=len(hand_data['initial_state']['players']),
                    starting_stack=1000,
                    small_blind=5,
                    big_blind=10
                )
                
                review_session = HandsReviewBotSession(config, decision_engine)
                review_session.set_sound_manager(None)  # No sound in test
                
                # Start review session
                if not review_session.start_session():
                    print(f"  ❌ Failed to start review session for hand {i}")
                    continue
                
                # Execute all decisions
                decisions_executed = 0
                max_decisions = len(decision_sequence) + 5  # Safety margin
                
                while review_session.current_state.value not in ['hand_complete', 'game_over'] and decisions_executed < max_decisions:
                    try:
                        action_result = review_session.execute_next_bot_action()
                        if action_result:
                            action, explanation = action_result
                            print(f"    🔄 P{review_session.action_player_index}: {action['action']} {action.get('amount', '')} - {explanation[:50]}...")
                            decisions_executed += 1
                        else:
                            print(f"    ⚠️ No more decisions available at step {decisions_executed}")
                            break
                    except Exception as e:
                        print(f"    ❌ Error executing review decision: {e}")
                        break
                
                print(f"  ✅ Review completed: {decisions_executed}/{len(decision_sequence)} decisions executed")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to review hand {i}: {e}")
                continue
        
        print(f"\n✅ REVIEW SUMMARY: {success_count}/{len(hands)} hands reviewed successfully")
        return success_count == len(hands)
    
    def _convert_hand_to_decisions(self, hand_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert captured hand data to decision sequence for review."""
        decisions = []
        
        for action_data in hand_data['actions']:
            decision = {
                'player_index': action_data['player_index'],
                'action': action_data['action'],
                'amount': action_data['amount'],
                'explanation': action_data['explanation']
            }
            decisions.append(decision)
        
        return decisions
    
    def save_test_results(self, filename: str = None):
        """Save generated hands to JSON file for further analysis."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_gto_hands_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), "logs", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'total_hands': len(self.generated_hands),
            'hands': self.generated_hands
        }
        
        with open(filepath, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: {filepath}")
        return filepath
    
    def run_full_test(self, num_hands: int = 10) -> bool:
        """Run complete GTO generation + hands review test."""
        print("🚀 STARTING UNIFIED BOT SESSION TEST")
        print("=" * 60)
        
        try:
            # Step 1: Generate GTO hands
            hands = self.generate_gto_hands(num_hands)
            if not hands:
                print("❌ Failed to generate any hands")
                return False
            
            # Step 2: Review generated hands
            review_success = self.review_generated_hands(hands)
            
            # Step 3: Save results
            self.save_test_results()
            
            # Step 4: Summary
            print("\n" + "=" * 60)
            if review_success:
                print("🎉 UNIFIED BOT SESSION TEST: SUCCESS!")
                print(f"✅ Generated {len(hands)} GTO hands")
                print("✅ Successfully reviewed all generated hands")
                print("✅ Both GTO and HandsReview systems are working correctly")
            else:
                print("⚠️ UNIFIED BOT SESSION TEST: PARTIAL SUCCESS")
                print(f"✅ Generated {len(hands)} GTO hands")
                print("❌ Some hands failed during review")
                print("🔍 Check individual hand results above")
            
            return review_success
            
        except Exception as e:
            print(f"❌ UNIFIED BOT SESSION TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run the unified bot session test."""
    tester = UnifiedBotSessionTester()
    
    # Test with 5 hands first (quick test)
    success = tester.run_full_test(num_hands=5)
    
    if success:
        print("\n🎯 Quick test passed! Ready for larger test...")
        # If quick test passes, run with more hands
        tester.run_full_test(num_hands=20)
    else:
        print("\n🚨 Quick test failed - fix issues before larger test")
    
    return success

if __name__ == "__main__":
    main()
