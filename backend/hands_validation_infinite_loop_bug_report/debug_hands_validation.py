"""
Debug Hands Review Validation - Find the infinite loop

This version adds extensive logging and limits to identify where the replay gets stuck.
"""

import sys
import json
import time
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules  
from core.providers.advancement_controllers import AutoAdvancementController


def load_hands_debug(limit=2):
    """Load just a few hands for debugging."""
    hands_file = Path("data/legendary_hands_normalized.json")
    
    with open(hands_file) as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "hands" in data:
        hands_data = data["hands"]
    else:
        hands_data = data
    
    print(f"🔍 DEBUG: Loaded {len(hands_data)} hands, testing {limit}")
    return hands_data[:limit]


def debug_replay_hand(ppsm, hand_model, max_actions=50, timeout_seconds=5):
    """Debug version with detailed logging and safety limits."""
    
    print(f"\n🎯 DEBUG: Starting hand replay for {hand_model.metadata.hand_id}")
    print(f"🔍 DEBUG: Players: {len(hand_model.seats)}")
    print(f"🔍 DEBUG: Actions: {len(hand_model.get_all_actions())}")
    
    start_time = time.time()
    
    try:
        # Setup PPSM for this hand model
        print("🔍 DEBUG: Setting up PPSM for hand model...")
        ppsm._setup_for_hand_model(hand_model)
        
        # Create decision engine adapter
        print("🔍 DEBUG: Creating decision engine adapter...")
        from core.pure_poker_state_machine import HandModelDecisionEngineAdapter
        decision_engine = HandModelDecisionEngineAdapter(hand_model)
        
        print(f"🔍 DEBUG: Decision engine has {len(decision_engine.actions_for_replay)} actions")
        for i, action in enumerate(decision_engine.actions_for_replay[:5]):
            print(f"  Action {i}: {action.actor_uid} {action.action.value} {action.amount}")
        
        # Set decision engine
        ppsm.decision_engine = decision_engine
        ppsm.decision_engine.reset_for_new_hand()
        
        # Start the hand
        print("🔍 DEBUG: Starting hand...")
        ppsm.start_hand()
        
        # Track progress
        actions_executed = 0
        last_state = None
        last_action_player = None
        state_change_count = 0
        
        print(f"🔍 DEBUG: Initial state: {ppsm.current_state}, action_player: {ppsm.action_player_index}")
        
        # Game loop with debug info
        while (ppsm.current_state not in [ppsm.current_state.__class__.END_HAND, ppsm.current_state.__class__.SHOWDOWN] and 
               actions_executed < max_actions and
               time.time() - start_time < timeout_seconds):
            
            current_state = ppsm.current_state
            current_action_player = ppsm.action_player_index
            
            # Check if we're making progress
            if current_state != last_state or current_action_player != last_action_player:
                print(f"🔍 DEBUG: State: {current_state}, Action Player: {current_action_player}")
                last_state = current_state
                last_action_player = current_action_player
                state_change_count += 1
                
                # Show game state
                if current_action_player >= 0 and current_action_player < len(ppsm.game_state.players):
                    current_player = ppsm.game_state.players[current_action_player]
                    print(f"🔍 DEBUG: Current player: {current_player.name}, stack: ${current_player.stack}, current_bet: ${current_player.current_bet}")
                    print(f"🔍 DEBUG: Game current_bet: ${ppsm.game_state.current_bet}, pot: ${ppsm.game_state.displayed_pot()}")
            
            # Check if we need a player action
            if ppsm.action_player_index >= 0 and ppsm.action_player_index < len(ppsm.game_state.players):
                current_player = ppsm.game_state.players[ppsm.action_player_index]
                
                if ppsm.decision_engine and ppsm.decision_engine.has_decision_for_player(current_player.name):
                    print(f"🔍 DEBUG: Getting decision for {current_player.name}")
                    
                    decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
                    if decision:
                        action_type, amount = decision
                        print(f"🔍 DEBUG: Decision: {action_type.value} {amount}")
                        
                        if ppsm._is_valid_action(current_player, action_type, amount):
                            success = ppsm.execute_action(current_player, action_type, amount)
                            print(f"🔍 DEBUG: Action executed: {success}")
                            actions_executed += 1
                        else:
                            print(f"🔍 DEBUG: Invalid action: {action_type.value} {amount}")
                            break
                    else:
                        print("🔍 DEBUG: No decision available")
                        break
                else:
                    print(f"🔍 DEBUG: No decision engine or no decision for {current_player.name}")
                    break
            else:
                # Auto-advance states
                print(f"🔍 DEBUG: Auto-advancing from {ppsm.current_state}")
                print(f"🔍 DEBUG: Current action_player_index: {ppsm.action_player_index}")
                
                # Check if we're in a dealing state that needs advancement
                if ppsm.current_state.value in ["deal_flop", "deal_turn", "deal_river"]:
                    print(f"🔍 DEBUG: Calling _advance_to_betting_round() for {ppsm.current_state}")
                    ppsm._advance_to_betting_round()
                    print(f"🔍 DEBUG: After advancement - state: {ppsm.current_state}, action_player: {ppsm.action_player_index}")
                elif ppsm.current_state.value in ["flop_betting", "turn_betting", "river_betting"]:
                    print(f"🔍 DEBUG: In betting state but action_player is {ppsm.action_player_index}")
                    # Check if we need to set first to act
                    if ppsm.action_player_index == -1:
                        print("🔍 DEBUG: Setting first to act for postflop")
                        ppsm._set_first_to_act_postflop()
                        print(f"🔍 DEBUG: After setting first to act: {ppsm.action_player_index}")
                    else:
                        print("🔍 DEBUG: No more actions available, ending hand")
                        break
                elif (ppsm.advancement_controller and 
                      ppsm.advancement_controller.should_advance_automatically(ppsm.current_state, ppsm.game_state.players)):
                    print("🔍 DEBUG: Controller says advance automatically")
                    ppsm._advance_to_betting_round()
                else:
                    print("🔍 DEBUG: No auto-advancement available")
                    break
        
        # Check why we stopped
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            print(f"⏰ DEBUG: TIMEOUT after {elapsed:.2f}s")
        elif actions_executed >= max_actions:
            print(f"🛑 DEBUG: MAX ACTIONS reached: {actions_executed}")
        else:
            print(f"✅ DEBUG: Hand completed normally after {elapsed:.2f}s, {actions_executed} actions")
        
        # Get final results
        final_pot = ppsm.game_state.displayed_pot()
        print(f"🔍 DEBUG: Final pot: ${final_pot}")
        
        return {
            'success': elapsed < timeout_seconds and actions_executed < max_actions,
            'final_pot': final_pot,
            'actions_executed': actions_executed,
            'elapsed_time': elapsed,
            'state_changes': state_change_count,
            'final_state': ppsm.current_state.value
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ DEBUG: EXCEPTION after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'exception': str(e),
            'elapsed_time': elapsed,
            'actions_executed': actions_executed
        }


def main():
    """Run debug validation with detailed logging."""
    print("🐛 DEBUG HANDS REVIEW VALIDATION")
    print("=" * 50)
    
    # Load just 2 hands for debugging
    hands_data = load_hands_debug(limit=2)
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Test each hand
    for i, hand_data in enumerate(hands_data):
        print(f"\n{'='*20} HAND {i+1} {'='*20}")
        
        hand_model = Hand.from_dict(hand_data)
        result = debug_replay_hand(ppsm, hand_model)
        
        print(f"\n📊 HAND {i+1} RESULT:")
        print(f"   Success: {result['success']}")
        print(f"   Final pot: ${result.get('final_pot', 0)}")
        print(f"   Actions: {result.get('actions_executed', 0)}")
        print(f"   Time: {result.get('elapsed_time', 0):.2f}s")
        print(f"   State changes: {result.get('state_changes', 0)}")
        print(f"   Final state: {result.get('final_state', 'unknown')}")
        
        if not result['success']:
            print("🚨 STOPPING DEBUG - Found the issue!")
            break


if __name__ == "__main__":
    main()
