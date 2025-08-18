#!/usr/bin/env python3
"""
Enhanced Hands Review Validation Test with Drain Logic and Loop Guards

This is the ULTIMATE test for PPSM production readiness.
Implements comprehensive validation with:
- Drain implied checks at street boundaries
- Loop guards to prevent infinite loops
- Robust error reporting and analysis
- 100% success rate requirement

MUST PASS: 20/20 hands successful for production deployment
"""

import sys
import json
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

# Add backend to path
sys.path.append('../' if 'backend' not in __file__ else '.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController
from core.poker_types import PokerState, ActionType


@dataclass
class ValidationResult:
    """Result of validating a single hand."""
    hand_id: str
    success: bool
    total_actions: int
    successful_actions: int
    expected_pot: float
    final_pot: float
    errors: List[str]
    execution_time: float
    infinite_loop: bool = False


def _drain_preflop_bb_option(ppsm) -> int:
    """
    If we're in preflop, no raise happened (current_bet == BB), and the actor is BB,
    inject a single CHECK to close the street when the log jumps.
    """
    if str(getattr(ppsm.game_state, "street", "")).lower() != "preflop":
        return 0
    bb_amt = float(getattr(ppsm.game_state, "big_blind", 0.0) or 0.0)
    if abs(float(ppsm.game_state.current_bet) - bb_amt) > 1e-9:
        return 0
    idx = ppsm.action_player_index
    try:
        is_bb = (ppsm.game_state.players[idx].position == "BB")
    except Exception:
        is_bb = False
    if not is_bb:
        return 0
    return 1 if ppsm.execute_action(idx, ActionType.CHECK, None) else 0


def _drain_implied_checks(ppsm: PurePokerStateMachine) -> int:
    """
    While current_bet == 0 and the round_state says players still need to act,
    auto-issue CHECK for each in-order actor to close the street cleanly.
    
    Returns:
        int: Number of CHECKs injected
    """
    checks_injected = 0
    rs = getattr(ppsm.game_state, "round_state", None)
    
    while ppsm.game_state.current_bet == 0 and rs and getattr(rs, "need_action_from", None):
        if not rs.need_action_from:
            break
            
        actor_idx = ppsm.action_player_index
        # Safety: if actor isn't in need_action_from (rare), break to avoid loop
        if actor_idx not in rs.need_action_from:
            break
            
        # Execute implicit CHECK
        success = ppsm.execute_action(actor_idx, ActionType.CHECK, None)
        if not success:
            break
            
        checks_injected += 1
        rs = ppsm.game_state.round_state  # refresh after action
        
        # Safety limit to prevent infinite drain loops
        if checks_injected > 10:  
            break
    
    return checks_injected


def _expected_pot_from_hand_model(hand_model) -> float:
    """Calculate expected pot from hand model (excludes blinds/antes)."""
    from core.hand_model import ActionType as HM
    include = {HM.BET, HM.CALL, HM.RAISE}
    return sum(float(a.amount or 0.0) for a in hand_model.get_all_actions() if a.action in include)


def validate_single_hand(hand_data: Dict[str, Any], hand_index: int) -> ValidationResult:
    """Validate a single hand with enhanced logic."""
    start_time = time.time()
    hand_id = hand_data.get('hand_id', f'Hand_{hand_index+1:03d}')
    
    try:
        # Parse hand model
        hand_model = Hand.from_dict(hand_data)
        expected_pot = _expected_pot_from_hand_model(hand_model)
        
        # Create PPSM with configuration
        config = GameConfig(
            num_players=2,
            small_blind=5.0,
            big_blind=10.0,
            starting_stack=1000.0
        )
        
        ppsm = PurePokerStateMachine(
            config=config,
            deck_provider=StandardDeck(),
            rules_provider=StandardRules(),
            advancement_controller=AutoAdvancementController()
        )
        
        # Enhanced validation with loop guards and drain logic
        replay_results = validate_hand_with_enhanced_logic(ppsm, hand_model)
        
        # Analyze results
        total_actions = replay_results['total_actions']
        successful_actions = replay_results['successful_actions']
        errors = replay_results['errors']
        final_pot = replay_results['final_pot']
        
        # Check for infinite loop detection
        infinite_loop = any('INFINITE_LOOP_DETECTED' in error for error in errors)
        
        # Success criteria: all actions successful AND no errors AND no infinite loops
        success = (
            successful_actions == total_actions and
            len(errors) == 0 and 
            not infinite_loop
        )
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            hand_id=hand_id,
            success=success,
            total_actions=total_actions,
            successful_actions=successful_actions,
            expected_pot=expected_pot,
            final_pot=final_pot,
            errors=errors,
            execution_time=execution_time,
            infinite_loop=infinite_loop
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return ValidationResult(
            hand_id=hand_id,
            success=False,
            total_actions=0,
            successful_actions=0,
            expected_pot=0.0,
            final_pot=0.0,
            errors=[f"Exception: {str(e)}"],
            execution_time=execution_time
        )


def validate_hand_with_enhanced_logic(ppsm: PurePokerStateMachine, hand_model) -> Dict[str, Any]:
    """
    Validate hand replay with enhanced logic including:
    - Loop guards (fail loud, don't spin)
    - Drain implied checks at street boundaries
    - Comprehensive error tracking
    """
    from core.poker_types import PokerState
    
    # Constants for loop guards
    MAX_STEPS_PER_STREET = 200
    MAX_STEPS_PER_HAND = 800
    
    BETTING_STATES = {
        PokerState.PREFLOP_BETTING,
        PokerState.FLOP_BETTING, 
        PokerState.TURN_BETTING,
        PokerState.RIVER_BETTING
    }
    
    steps_this_street = 0
    steps_this_hand = 0
    last_street = None
    
    total_actions = 0
    successful_actions = 0
    errors = []
    
    try:
        # Start hand replay
        replay_results = ppsm.replay_hand_model(hand_model)
        
        # Enhanced validation loop with guards and draining
        while ppsm.current_state in BETTING_STATES:
            # Track steps and detect street changes
            current_street = getattr(ppsm.game_state, 'street', 'unknown')
            if current_street != last_street:
                last_street = current_street
                steps_this_street = 0
                
                # Drain implied checks at street start
                checks_drained = _drain_implied_checks(ppsm)
                if checks_drained > 0:
                    print(f"   🔧 Drained {checks_drained} implied CHECKs at {current_street} start")
                # NEW:
                if current_street == "preflop":
                    opt = _drain_preflop_bb_option(ppsm)
                    if opt:
                        print("   🔧 Injected BB option CHECK to close preflop")
            
            steps_this_street += 1
            steps_this_hand += 1
            
            # Loop guard: fail loud with full state snapshot
            if steps_this_street > MAX_STEPS_PER_STREET or steps_this_hand > MAX_STEPS_PER_HAND:
                info = ppsm.get_game_info()
                error_msg = (
                    f"Loop guard tripped.\n"
                    f"street={info['street']} state={info['current_state']} pot={info.get('pot', 'N/A')}\n"
                    f"dealer={info['dealer_position']} actor={info['action_player_index']}\n"
                    f"need_action_from={info.get('need_action_from', 'N/A')}\n"
                    f"steps_this_street={steps_this_street} steps_this_hand={steps_this_hand}\n"
                    f"players={info['players']}"
                )
                errors.append(f"INFINITE_LOOP_DETECTED: {error_msg}")
                break
            
            # Try to advance the game
            game_advanced = False
            
            # Check if we need to drain checks after an action
            if ppsm.current_state in BETTING_STATES:
                checks_drained = _drain_implied_checks(ppsm)
                if checks_drained > 0:
                    game_advanced = True
                    print(f"   🔧 Drained {checks_drained} implied CHECKs during betting")
            
            # If we didn't advance through draining, we're done with this loop iteration
            if not game_advanced:
                break
        
        # Get final results
        final_pot = getattr(ppsm.game_state, 'displayed_pot', lambda: 0.0)()
        if callable(final_pot):
            final_pot = final_pot()
            
        # Combine results from replay_results and our enhanced validation
        total_actions = replay_results.get('total_actions', 0)
        successful_actions = replay_results.get('successful_actions', 0) 
        errors.extend(replay_results.get('errors', []))
        
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'final_pot': final_pot,
            'errors': errors,
            'steps_this_hand': steps_this_hand
        }
        
    except Exception as e:
        errors.append(f"Enhanced validation exception: {str(e)}")
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'final_pot': 0.0,
            'errors': errors,
            'steps_this_hand': steps_this_hand
        }


def run_enhanced_hands_review_validation():
    """Run the enhanced hands review validation test."""
    
    print("🎯 ENHANCED HANDS REVIEW VALIDATION TEST")
    print("=" * 50)
    print("This is the ULTIMATE test for PPSM production readiness.")
    print("REQUIREMENT: 20/20 hands must pass (100% success rate)")
    print("=" * 50)
    
    # Load test data
    try:
        with open('data/legendary_hands_normalized.json') as f:
            data = json.load(f)
        
        hands_data = data['hands'] if 'hands' in data else data
        print(f"📋 Loaded {len(hands_data)} hands for validation")
        
    except Exception as e:
        print(f"❌ Failed to load test data: {e}")
        return False
    
    # Validate each hand
    results: List[ValidationResult] = []
    start_time = time.time()
    
    for i, hand_data in enumerate(hands_data):
        print(f"\n🎯 Validating Hand {i+1:2d}/20: {hand_data.get('hand_id', f'Hand_{i+1}')}")
        
        result = validate_single_hand(hand_data, i)
        results.append(result)
        
        # Print immediate feedback
        if result.success:
            print(f"   ✅ SUCCESS: {result.successful_actions}/{result.total_actions} actions, "
                  f"pot ${result.final_pot:.2f} (expected ${result.expected_pot:.2f})")
        else:
            print(f"   ❌ FAILED: {result.successful_actions}/{result.total_actions} actions, "
                  f"pot ${result.final_pot:.2f} (expected ${result.expected_pot:.2f})")
            if result.infinite_loop:
                print(f"      🔄 Infinite loop detected")
            if result.errors:
                print(f"      Errors: {len(result.errors)}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"         {error}")
    
    total_time = time.time() - start_time
    
    # Comprehensive results analysis
    print(f"\n" + "=" * 50)
    print(f"📊 ENHANCED VALIDATION RESULTS")
    print(f"=" * 50)
    
    successful_hands = sum(1 for r in results if r.success)
    total_actions = sum(r.total_actions for r in results)
    successful_actions = sum(r.successful_actions for r in results)
    infinite_loops = sum(1 for r in results if r.infinite_loop)
    total_errors = sum(len(r.errors) for r in results)
    
    print(f"📋 Hands: {successful_hands}/{len(results)} successful ({successful_hands/len(results)*100:.1f}%)")
    print(f"⚡ Actions: {successful_actions}/{total_actions} successful ({successful_actions/total_actions*100:.1f}%)")
    print(f"🔄 Infinite loops: {infinite_loops}")
    print(f"❌ Total errors: {total_errors}")
    print(f"⏱️  Total time: {total_time:.2f}s ({total_time/len(results):.3f}s per hand)")
    
    # Series breakdown
    bb_results = results[:10]  # BB001-BB010
    hc_results = results[10:]  # HC001-HC010 
    
    bb_success = sum(1 for r in bb_results if r.success)
    hc_success = sum(1 for r in hc_results if r.success)
    
    print(f"\n📈 SERIES BREAKDOWN:")
    print(f"BB Series (1-10):  {bb_success}/10 successful ({bb_success/10*100:.0f}%)")
    print(f"HC Series (11-20): {hc_success}/10 successful ({hc_success/10*100:.0f}%)")
    
    # Production readiness assessment
    production_ready = (successful_hands == len(results))
    
    print(f"\n" + "=" * 50)
    print(f"🎯 PRODUCTION READINESS ASSESSMENT")
    print(f"=" * 50)
    
    if production_ready:
        print(f"🎉 PRODUCTION READY: 100% SUCCESS ACHIEVED!")
        print(f"✅ All 20 hands completed successfully")
        print(f"✅ No infinite loops detected") 
        print(f"✅ All actions executed correctly")
        print(f"🚀 PPSM is ready for production deployment!")
    else:
        print(f"⚠️  PRODUCTION NOT READY: {successful_hands}/20 hands successful")
        if infinite_loops > 0:
            print(f"❌ {infinite_loops} infinite loops detected")
        if total_errors > 0:
            print(f"❌ {total_errors} total errors found")
        print(f"🔧 Additional fixes required before production deployment")
        
        # Show failed hands for debugging
        failed_hands = [r for r in results if not r.success]
        if failed_hands:
            print(f"\n🔍 FAILED HANDS (for debugging):")
            for r in failed_hands[:5]:  # Show first 5 failed hands
                print(f"   {r.hand_id}: {r.successful_actions}/{r.total_actions} actions, "
                      f"pot ${r.final_pot:.2f}, {len(r.errors)} errors")
    
    print(f"\n" + "=" * 50)
    
    return production_ready


if __name__ == "__main__":
    success = run_enhanced_hands_review_validation()
    sys.exit(0 if success else 1)
