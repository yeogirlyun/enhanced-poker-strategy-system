"""
Debug HC001 hand to understand CALL validation failure.
"""

import sys
import json
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def debug_hc_hand():
    """Debug HC001 hand step by step."""
    
    # Load HC001 hand
    with open('data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    hc_hand = data['hands'][10]
    
    print("🔍 DEBUGGING HC001 HAND")
    print("=" * 40)
    
    # Parse hand
    hand_model = Hand.from_dict(hc_hand)
    all_actions = hand_model.get_all_actions()
    
    print("📋 Expected Action Sequence:")
    for i, action in enumerate(all_actions):
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({action.street.value})")
    
    print()
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Create decision engine adapter and check action sequence
    from core.pure_poker_state_machine import HandModelDecisionEngineAdapter
    adapter = HandModelDecisionEngineAdapter(hand_model)
    
    print("🤖 Decision Engine Actions:")
    for i, action in enumerate(adapter.actions_for_replay):
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({action.street.value})")
    
    print()
    
    # Step through manually
    print("⚡ Manual Replay:")
    ppsm._setup_for_hand_model(hand_model)
    ppsm.start_hand()
    
    step = 0
    while adapter.current_action_index < len(adapter.actions_for_replay):
        current_player = ppsm.game_state.players[ppsm.action_player_index] if ppsm.action_player_index >= 0 else None
        
        if not current_player:
            print(f"  Step {step}: No action player, advancing...")
            # Need to advance to betting round
            if ppsm.current_state in [ppsm.PokerState.DEAL_FLOP, ppsm.PokerState.DEAL_TURN, ppsm.PokerState.DEAL_RIVER]:
                ppsm._advance_to_betting_round()
            continue
            
        print(f"  Step {step}: Current player: {current_player.name}, State: {ppsm.current_state.value}")
        print(f"            Current bet: ${ppsm.game_state.current_bet}, Player bet: ${current_player.current_bet}")
        
        if adapter.has_decision_for_player(current_player.name):
            decision = adapter.get_decision(current_player.name, ppsm.game_state)
            if decision:
                action_type, amount = decision
                print(f"            Decision: {action_type.value} {amount}")
                
                # Check validation
                is_valid = ppsm._is_valid_action(current_player, action_type, amount)
                print(f"            Valid: {is_valid}")
                
                if is_valid:
                    success = ppsm.execute_action(current_player, action_type, amount)
                    print(f"            Executed: {success}")
                else:
                    print(f"            ❌ VALIDATION FAILED!")
                    break
            else:
                print(f"            No decision available")
                break
        else:
            print(f"            No decision for {current_player.name}")
            break
            
        step += 1
        if step > 20:  # Safety limit
            print("  Step limit reached")
            break


if __name__ == "__main__":
    debug_hc_hand()
