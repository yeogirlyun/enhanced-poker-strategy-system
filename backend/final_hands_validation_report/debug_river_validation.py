#!/usr/bin/env python3
"""
Debug script for river validation failures in BB series.
Runs BB001 with comprehensive logging to identify exact validation failure point.
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


def load_bb001_hand():
    """Load BB001 hand from legendary_hands_normalized.json."""
    hands_file = "../data/legendary_hands_normalized.json"
    
    with open(hands_file, 'r') as f:
        data = json.load(f)
    
    hands_list = data if isinstance(data, list) else data.get("hands", [])
    
    # BB001 should be hand_0
    if len(hands_list) > 0:
        hand_data = hands_list[0]
        hand_model = Hand.from_dict(hand_data)
        return hand_model
    
    raise ValueError("Could not load BB001 hand")


def debug_validation_wrapper(original_method):
    """Wrapper for _is_valid_action to add comprehensive debug logging."""
    
    def debug_is_valid_action(self, player, action_type, to_amount=None):
        print(f"\n🔍 VALIDATION DEBUG:")
        print(f"    Player: {player.name}")
        print(f"    Action: {action_type.value}")  
        print(f"    Amount: {to_amount}")
        print(f"    Street: {self.game_state.street}")
        print(f"    Current bet: {self.game_state.current_bet}")
        print(f"    Player current bet: {player.current_bet}")
        print(f"    Player stack: {player.stack}")
        print(f"    Player active: {player.is_active}")
        print(f"    Player folded: {player.has_folded}")
        print(f"    Game state: {self.current_state.value}")
        
        # Round state info
        rs = getattr(self.game_state, 'round_state', None)
        if rs:
            print(f"    Need action from: {getattr(rs, 'need_action_from', 'N/A')}")
            print(f"    Last aggressor: {getattr(rs, 'last_aggressor_idx', 'N/A')}")
            print(f"    Reopen available: {getattr(rs, 'reopen_available', 'N/A')}")
        else:
            print(f"    Round state: None")
        
        # Call original validation method
        result = original_method(self, player, action_type, to_amount)
        print(f"🔍 VALIDATION RESULT: {result}")
        
        if not result:
            print(f"❌ VALIDATION FAILED - analyzing why...")
            
            # Analyze specific failure reasons
            if action_type == ActionType.FOLD:
                print(f"   FOLD always allowed: should be True")
            elif action_type == ActionType.CALL:
                behind = player.current_bet < self.game_state.current_bet
                print(f"   CALL check: player.current_bet ({player.current_bet}) < game.current_bet ({self.game_state.current_bet}) = {behind}")
            elif action_type in (ActionType.BET, ActionType.RAISE):
                if to_amount is None:
                    print(f"   {action_type.value} check: to_amount is None")
                elif to_amount <= player.current_bet:
                    print(f"   {action_type.value} check: to_amount ({to_amount}) <= player.current_bet ({player.current_bet})")
                else:
                    addl = to_amount - player.current_bet
                    if addl > player.stack + 1e-9:
                        print(f"   {action_type.value} check: additional ({addl}) > stack ({player.stack})")
                    
                    if action_type == ActionType.BET:
                        if self.game_state.current_bet != 0:
                            print(f"   BET check: current_bet ({self.game_state.current_bet}) != 0 (BET only allowed when no existing bet)")
                    
                    if action_type == ActionType.RAISE:
                        if self.game_state.current_bet == 0:
                            print(f"   RAISE check: current_bet is 0 (RAISE only allowed when there's an existing bet)")
        
        print(f"🔍 END VALIDATION DEBUG\n")
        return result
    
    return debug_is_valid_action


def debug_adapter_wrapper(original_method):
    """Wrapper for adapter get_decision to add debug logging."""
    
    def debug_get_decision(self, player_name, game_state):
        print(f"\n🎯 ADAPTER DEBUG:")
        print(f"    Requesting decision for: {player_name}")
        print(f"    Action index: {self.current_action_index}/{len(self.actions_for_replay)}")
        
        if self.current_action_index < len(self.actions_for_replay):
            next_action = self.actions_for_replay[self.current_action_index]
            print(f"    Next logged action: {next_action.actor_uid} {next_action.action.value} {next_action.amount}")
        else:
            print(f"    No more logged actions available")
        
        print(f"    Game state: {game_state.street}, current_bet={game_state.current_bet}")
        
        # Call original method
        decision = original_method(self, player_name, game_state)
        print(f"🎯 ADAPTER DECISION: {decision}")
        print(f"🎯 END ADAPTER DEBUG\n")
        
        return decision
    
    return debug_get_decision


def debug_bb001_validation():
    """Run BB001 with comprehensive debug logging."""
    print("🐛 DEBUG: BB001 River Validation Failure")
    print("=" * 60)
    
    # Load BB001 hand
    try:
        hand_model = load_bb001_hand()
        print(f"✅ Loaded hand: {hand_model.metadata.hand_id}")
    except Exception as e:
        print(f"❌ Failed to load BB001: {e}")
        return
    
    # Create PPSM with debug logging
    config = GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0)
    ppsm = PurePokerStateMachine(
        config=config,
        deck_provider=DeterministicDeck(),
        rules_provider=HandsReviewRules(),
        advancement_controller=HandsReviewAdvancementController()
    )
    
    # Wrap validation method with debug logging
    original_validation = ppsm._is_valid_action
    ppsm._is_valid_action = debug_validation_wrapper(original_validation).__get__(ppsm, PurePokerStateMachine)
    
    # Set up hand model replay
    ppsm._setup_for_hand_model(hand_model, create_hand_replay_engine=True)
    
    # Wrap adapter method with debug logging
    if ppsm.decision_engine:
        original_get_decision = ppsm.decision_engine.get_decision
        ppsm.decision_engine.get_decision = debug_adapter_wrapper(original_get_decision).__get__(
            ppsm.decision_engine, ppsm.decision_engine.__class__
        )
    
    # Start hand
    print(f"\n🚀 Starting hand replay...")
    ppsm.start_hand()
    
    # Run until completion or failure
    max_actions = 50
    action_count = 0
    successful_actions = 0
    failed_actions = 0
    
    while (ppsm.current_state not in [PokerState.END_HAND] and 
           action_count < max_actions):
        
        print(f"\n📍 ACTION {action_count + 1}: State = {ppsm.current_state.value}")
        
        if ppsm.action_player_index >= 0 and ppsm.action_player_index < len(ppsm.game_state.players):
            current_player = ppsm.game_state.players[ppsm.action_player_index]
            print(f"    Current player: {current_player.name}")
            
            # Get decision
            if ppsm.decision_engine:
                decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
                
                if decision:
                    action_type, amount = decision
                    print(f"    Decision: {action_type.value} {amount}")
                    
                    # Validate and execute
                    if ppsm._is_valid_action(current_player, action_type, amount):
                        success = ppsm.execute_action(current_player, action_type, amount)
                        if success:
                            successful_actions += 1
                            print(f"    ✅ Action executed successfully")
                        else:
                            failed_actions += 1
                            print(f"    ❌ Action execution failed")
                    else:
                        failed_actions += 1  
                        print(f"    ❌ Action validation failed")
                        
                        # This is our target - validation failure
                        if action_count >= 6:  # Around river actions
                            print(f"\n🎯 TARGET VALIDATION FAILURE IDENTIFIED!")
                            print(f"    This is likely the river validation issue")
                            print(f"    Action: {action_type.value} {amount}")
                            print(f"    Street: {ppsm.game_state.street}")
                            print(f"    Current bet: {ppsm.game_state.current_bet}")
                            
                            # Additional analysis
                            print(f"\n🔬 ADDITIONAL ANALYSIS:")
                            rs = getattr(ppsm.game_state, 'round_state', None)
                            if rs and hasattr(rs, 'need_action_from'):
                                if len(rs.need_action_from) == 0:
                                    print(f"    🎯 POTENTIAL ISSUE: need_action_from is empty")
                                    print(f"        This suggests the round already closed")
                                    print(f"        But adapter is still trying to execute actions")
                    
                    action_count += 1
                else:
                    print(f"    No decision available - advancing")
                    ppsm._advance_to_next_player()
                    
        else:
            # Auto-advance for non-action states
            if ppsm.current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                ppsm._advance_to_betting_round()
            else:
                break
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"    Total actions attempted: {action_count}")
    print(f"    Successful actions: {successful_actions}")
    print(f"    Failed actions: {failed_actions}")
    print(f"    Success rate: {successful_actions}/{action_count} ({100*successful_actions//action_count if action_count > 0 else 0}%)")
    print(f"    Final pot: ${ppsm.game_state.displayed_pot()}")
    print(f"    Final state: {ppsm.current_state.value}")


if __name__ == "__main__":
    debug_bb001_validation()
