#!/usr/bin/env python3
"""
Comparison script: BB001 (failing) vs HC001 (working)
Side-by-side execution to identify where they diverge.
"""

import sys
import os
sys.path.append('..')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.providers.deck_providers import DeterministicDeck
from core.providers.rules_providers import HandsReviewRules
from core.providers.advancement_controllers import HandsReviewAdvancementController
from core.hand_model import Hand
from core.poker_types import PokerState, ActionType
import json


def load_hand_by_id(hand_id):
    """Load specific hand by ID from legendary_hands_normalized.json."""
    hands_file = "../data/legendary_hands_normalized.json"
    
    with open(hands_file, 'r') as f:
        data = json.load(f)
    
    hands_list = data if isinstance(data, list) else data.get("hands", [])
    
    # Find hand by ID
    for hand_data in hands_list:
        if hand_data.get('metadata', {}).get('hand_id') == hand_id:
            return Hand.from_dict(hand_data)
    
    # Fallback: use index mapping
    if hand_id == "BB001":
        return Hand.from_dict(hands_list[0]) if len(hands_list) > 0 else None
    elif hand_id == "HC001":
        return Hand.from_dict(hands_list[10]) if len(hands_list) > 10 else None
    
    raise ValueError(f"Could not find hand {hand_id}")


class CompactLogger:
    """Compact logging for side-by-side comparison."""
    
    def __init__(self, prefix):
        self.prefix = prefix
        self.actions = []
        
    def log_action(self, action_num, player, action_type, amount, success, state_info=""):
        """Log a single action attempt."""
        status = "✅" if success else "❌"
        self.actions.append({
            'num': action_num,
            'player': player,
            'action': action_type.value if hasattr(action_type, 'value') else str(action_type),
            'amount': amount,
            'success': success,
            'state': state_info
        })
        print(f"{self.prefix} Action {action_num:2d}: {status} {player} {action_type.value if hasattr(action_type, 'value') else str(action_type)} {amount} {state_info}")
    
    def log_state(self, message):
        """Log state information."""
        print(f"{self.prefix} {message}")
    
    def get_summary(self):
        """Get execution summary."""
        successful = sum(1 for a in self.actions if a['success'])
        total = len(self.actions)
        return {
            'actions': self.actions,
            'successful': successful,
            'total': total,
            'success_rate': f"{successful}/{total} ({100*successful//total if total > 0 else 0}%)"
        }


def run_hand_with_logging(hand_model, logger):
    """Run a single hand with compact logging."""
    
    # Create PPSM
    config = GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0)
    ppsm = PurePokerStateMachine(
        config=config,
        deck_provider=DeterministicDeck(),
        rules_provider=HandsReviewRules(),
        advancement_controller=HandsReviewAdvancementController()
    )
    
    # Set up hand model replay
    ppsm._setup_for_hand_model(hand_model, create_hand_replay_engine=True)
    
    # Start hand
    ppsm.start_hand()
    logger.log_state(f"Started hand: {hand_model.metadata.hand_id}")
    
    # Track execution
    max_actions = 20
    action_count = 0
    successful_actions = 0
    
    while (ppsm.current_state not in [PokerState.END_HAND] and 
           action_count < max_actions):
        
        if ppsm.action_player_index >= 0 and ppsm.action_player_index < len(ppsm.game_state.players):
            current_player = ppsm.game_state.players[ppsm.action_player_index]
            
            # Get decision
            if ppsm.decision_engine:
                decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
                
                if decision:
                    action_type, amount = decision
                    
                    # Create state info for logging
                    state_info = f"(street={ppsm.game_state.street}, bet={ppsm.game_state.current_bet}, state={ppsm.current_state.value})"
                    
                    # Validate and execute
                    if ppsm._is_valid_action(current_player, action_type, amount):
                        success = ppsm.execute_action(current_player, action_type, amount)
                        if success:
                            successful_actions += 1
                        
                        logger.log_action(action_count + 1, current_player.name, action_type, amount, success, state_info)
                    else:
                        logger.log_action(action_count + 1, current_player.name, action_type, amount, False, f"VALIDATION_FAIL {state_info}")
                    
                    action_count += 1
                else:
                    # Try advancing
                    ppsm._advance_to_next_player()
        else:
            # Auto-advance for non-action states
            if ppsm.current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                ppsm._advance_to_betting_round()
            else:
                break
    
    # Final state
    final_pot = ppsm.game_state.displayed_pot()
    logger.log_state(f"Final: {successful_actions}/{action_count} actions, pot=${final_pot}, state={ppsm.current_state.value}")
    
    return logger.get_summary()


def compare_bb_vs_hc():
    """Run side-by-side comparison of BB001 vs HC001."""
    print("🔬 COMPARISON: BB001 (Failing) vs HC001 (Working)")
    print("=" * 80)
    
    try:
        # Load hands
        bb001 = load_hand_by_id("BB001")
        hc001 = load_hand_by_id("HC001") 
        
        print(f"✅ Loaded BB001: {bb001.metadata.hand_id}")
        print(f"✅ Loaded HC001: {hc001.metadata.hand_id}")
        
    except Exception as e:
        print(f"❌ Failed to load hands: {e}")
        return
    
    print(f"\n📊 SIDE-BY-SIDE EXECUTION")
    print("-" * 80)
    
    # Create loggers
    bb_logger = CompactLogger("BB001:")
    hc_logger = CompactLogger("HC001:")
    
    # Run BB001
    print(f"\n🔴 RUNNING BB001 (Expected to fail on river)")
    bb_summary = run_hand_with_logging(bb001, bb_logger)
    
    print(f"\n🟢 RUNNING HC001 (Expected to succeed)")  
    hc_summary = run_hand_with_logging(hc001, hc_logger)
    
    # Compare results
    print(f"\n📊 COMPARISON SUMMARY")
    print("=" * 80)
    print(f"BB001: {bb_summary['success_rate']} actions successful")
    print(f"HC001: {hc_summary['success_rate']} actions successful")
    
    # Analyze divergence points
    print(f"\n🔍 DIVERGENCE ANALYSIS")
    print("-" * 50)
    
    bb_actions = bb_summary['actions']
    hc_actions = hc_summary['actions']
    
    max_actions = max(len(bb_actions), len(hc_actions))
    
    for i in range(max_actions):
        bb_action = bb_actions[i] if i < len(bb_actions) else None
        hc_action = hc_actions[i] if i < len(hc_actions) else None
        
        if bb_action and hc_action:
            if bb_action['success'] != hc_action['success']:
                print(f"🎯 DIVERGENCE at action {i+1}:")
                print(f"    BB001: {bb_action['action']} {bb_action['amount']} -> {'SUCCESS' if bb_action['success'] else 'FAIL'}")
                print(f"    HC001: {hc_action['action']} {hc_action['amount']} -> {'SUCCESS' if hc_action['success'] else 'FAIL'}")
                break
        elif bb_action and not hc_action:
            print(f"🎯 BB001 has more actions: {bb_action}")
        elif hc_action and not bb_action:
            print(f"🎯 HC001 has more actions: {hc_action}")
    
    # Identify first failure points
    bb_first_fail = next((a for a in bb_actions if not a['success']), None)
    hc_first_fail = next((a for a in hc_actions if not a['success']), None)
    
    if bb_first_fail:
        print(f"\n❌ BB001 first failure: Action {bb_first_fail['num']} - {bb_first_fail['action']} {bb_first_fail['amount']}")
        print(f"    State: {bb_first_fail['state']}")
    else:
        print(f"\n✅ BB001: No failures detected")
        
    if hc_first_fail:
        print(f"\n❌ HC001 first failure: Action {hc_first_fail['num']} - {hc_first_fail['action']} {hc_first_fail['amount']}")
    else:
        print(f"\n✅ HC001: No failures detected")
    
    # Street-by-street analysis
    print(f"\n🏒 STREET-BY-STREET ANALYSIS")
    print("-" * 50)
    
    # Count successes by street (rough estimation based on action sequence)
    bb_preflop = sum(1 for a in bb_actions[:2] if a['success'])
    bb_flop = sum(1 for a in bb_actions[2:4] if a['success']) if len(bb_actions) > 2 else 0
    bb_turn = sum(1 for a in bb_actions[4:6] if a['success']) if len(bb_actions) > 4 else 0  
    bb_river = sum(1 for a in bb_actions[6:] if a['success']) if len(bb_actions) > 6 else 0
    
    hc_preflop = sum(1 for a in hc_actions[:2] if a['success'])
    hc_flop = sum(1 for a in hc_actions[2:4] if a['success']) if len(hc_actions) > 2 else 0
    hc_turn = sum(1 for a in hc_actions[4:6] if a['success']) if len(hc_actions) > 4 else 0
    hc_river = sum(1 for a in hc_actions[6:] if a['success']) if len(hc_actions) > 6 else 0
    
    print(f"Preflop: BB001={bb_preflop}/2, HC001={hc_preflop}/2")
    print(f"Flop:    BB001={bb_flop}/2, HC001={hc_flop}/2")  
    print(f"Turn:    BB001={bb_turn}/2, HC001={hc_turn}/2")
    print(f"River:   BB001={bb_river}/?, HC001={hc_river}/? <- CRITICAL DIFFERENCE")
    
    print(f"\n🎯 CONCLUSION")
    print("=" * 50)
    if bb_summary['successful'] < hc_summary['successful']:
        print(f"✅ Confirmed: BB001 has validation issues that HC001 does not")
        print(f"   Likely root cause: River validation logic after CHECK injection")
    else:
        print(f"⚠️  Unexpected: Both hands show similar success patterns")


if __name__ == "__main__":
    compare_bb_vs_hc()
