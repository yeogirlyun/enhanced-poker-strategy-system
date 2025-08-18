#!/usr/bin/env python3
"""
Debug the decision engine behavior during HC series replay.
"""

import sys
import json
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig, HandModelDecisionEngineAdapter
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController
from core.poker_types import PokerState


def debug_decision_engine():
    """Debug HC001 decision engine step by step."""
    
    # Load HC001 hand
    with open('data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    hc_hand = data['hands'][10]
    
    print("🔍 DEBUGGING DECISION ENGINE FOR HC001")
    print("=" * 60)
    
    # Parse hand
    hand_model = Hand.from_dict(hc_hand)
    all_actions = hand_model.get_all_actions()
    
    print("📋 All Actions in Hand Model:")
    for i, action in enumerate(all_actions):
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({action.street.value})")
    
    print()
    
    # Create adapter and check its actions
    adapter = HandModelDecisionEngineAdapter(hand_model)
    print("🤖 Adapter Actions for Replay:")
    for i, action in enumerate(adapter.actions_for_replay):
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({action.street.value})")
    
    print()
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    ppsm._setup_for_hand_model(hand_model)
    ppsm.start_hand()
    
    # Manual step-through
    print("⚡ Step-by-step Hand Replay:")
    step = 0
    while ppsm.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN]:
        step += 1
        print(f"\n  --- Step {step} ---")
        print(f"  State: {ppsm.current_state.value}")
        print(f"  Street: {ppsm.game_state.street}")
        print(f"  Action player: {ppsm.action_player_index}")
        print(f"  Current bet: ${ppsm.game_state.current_bet}")
        
        if ppsm.action_player_index >= 0:
            current_player = ppsm.game_state.players[ppsm.action_player_index]
            print(f"  Current player: {current_player.name}")
            
            # Check if adapter has decision
            print(f"  Adapter current index: {adapter.current_action_index}/{len(adapter.actions_for_replay)}")
            has_decision = adapter.has_decision_for_player(current_player.name)
            print(f"  Has decision for {current_player.name}: {has_decision}")
            
            if has_decision:
                decision = adapter.get_decision(current_player.name, ppsm.game_state)
                print(f"  Decision: {decision}")
                
                if decision:
                    action_type, amount = decision
                    is_valid = ppsm._is_valid_action(current_player, action_type, amount)
                    print(f"  Is valid: {is_valid}")
                    
                    if is_valid:
                        success = ppsm.execute_action(current_player, action_type, amount)
                        print(f"  Executed: {success}")
                    else:
                        print(f"  ❌ INVALID ACTION - breaking")
                        break
                else:
                    print(f"  ❌ NO DECISION - breaking") 
                    break
            else:
                print(f"  ❌ NO DECISION FOR PLAYER - breaking")
                break
        else:
            print(f"  No action player - checking auto-advancement")
            if ppsm.current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                print(f"  Auto-advancing from {ppsm.current_state.value}")
                ppsm._advance_to_betting_round()
            else:
                print(f"  No advancement available")
                break
                
        if step > 20:  # Safety limit
            print(f"  Safety limit reached")
            break
    
    print(f"\n🏁 Final state: {ppsm.current_state.value}")
    print(f"🎯 Final pot: ${ppsm.game_state.displayed_pot()}")
    print(f"📊 Adapter ended at index: {adapter.current_action_index}/{len(adapter.actions_for_replay)}")

if __name__ == "__main__":
    debug_decision_engine()
