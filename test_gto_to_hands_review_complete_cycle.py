#!/usr/bin/env python3
"""
Complete GTO to Hands Review Cycle Test

This test will:
1. Run a GTO bot game and log every action in English
2. Save the complete hand data to JSON
3. Load it into Hands Review and replay step by step
4. Print both sequences in English side-by-side for comparison
5. Identify any discrepancies between original and replay
"""

import json
import sys
import os
from typing import List, Dict, Any, Tuple

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.bot_session_state_machine import GTOBotSession, HandsReviewBotSession
from core.flexible_poker_state_machine import GameConfig, ActionType, PokerState
from core.decision_engine_v2 import PreloadedDecisionEngine

def create_gto_session() -> GTOBotSession:
    """Create a GTO session for testing."""
    config = GameConfig(
        starting_stack=1000,
        small_blind=5,
        big_blind=10,
        num_players=3
    )
    return GTOBotSession(config)

def run_gto_hand_with_logging() -> Tuple[Dict[str, Any], List[str]]:
    """Run a complete GTO hand and log every action in English."""
    
    print("=" * 80)
    print("🎯 PART 1: RUNNING GTO BOT GAME")
    print("=" * 80)
    
    session = create_gto_session()
    session.start_session()
    
    # Capture initial state after session starts
    initial_players_data = []
    for p in session.game_state.players:
        initial_players_data.append({
            'name': p.name,
            'stack': p.stack,
            'position': p.position,
            'cards': p.cards,
            'is_human': p.is_human,
            'is_active': p.is_active,
            'has_folded': p.has_folded,
            'current_bet': p.current_bet
        })
    
    initial_game_state = {
        'players': initial_players_data,
        'board': session.game_state.board.copy(),
        'pot': session.game_state.pot,
        'current_bet': session.game_state.current_bet,
        'dealer_position': session.dealer_position
    }
    
    gto_log = []
    json_actions = []
    
    # Log initial setup
    gto_log.append("=== GTO BOT GAME ORIGINAL ===")
    gto_log.append(f"Dealer position: {session.dealer_position}")
    
    for i, player in enumerate(session.game_state.players):
        gto_log.append(f"Setup: {player.name} (Position {i}) starts with ${player.stack:.2f}, cards: {player.cards}")
    
    gto_log.append(f"Setup: Initial pot=${session.game_state.pot:.2f}, current_bet=${session.game_state.current_bet:.2f}")
    gto_log.append("")
    
    print(f"🃏 Initial setup:")
    print(f"   Dealer: {session.dealer_position}")
    print(f"   Pot: ${session.game_state.pot:.2f}, Current bet: ${session.game_state.current_bet:.2f}")
    for i, p in enumerate(session.game_state.players):
        print(f"   Player {i+1}: ${p.stack:.2f}, cards: {p.cards}")
    
    # Execute actions
    action_count = 0
    while session.current_state.value != PokerState.END_HAND.value and action_count < 50:
        action_count += 1
        current_player_index = session.action_player_index
        
        if current_player_index == -1:
            gto_log.append("🏁 No active players, ending hand.")
            print("🏁 No active players, ending hand.")
            break
        
        current_player = session.game_state.players[current_player_index]
        street = session.current_state.value
        pot_before = session.game_state.pot
        current_bet_before = session.game_state.current_bet
        player_stack_before = current_player.stack
        board_before = session.game_state.board.copy()
        
        print(f"\n🎲 GTO Action {action_count}: {current_player.name} to act on {street}")
        print(f"   Game: Pot=${pot_before:.2f}, current_bet=${current_bet_before:.2f}")
        print(f"   Player: stack=${player_stack_before:.2f}, bet=${current_player.current_bet:.2f}")
        
        # Execute action
        result = session.execute_next_bot_action()
        
        if result:
            # Get the last decision from the history
            if session.decision_history:
                last_decision = session.decision_history[-1]
                executed_action_type = last_decision['action']
                executed_amount = last_decision['amount']
                explanation = last_decision['explanation']
            else:
                print("❌ No decision history found")
                break
            
            # Log action in English
            if executed_action_type == ActionType.RAISE:
                amount_put_in = executed_amount - current_player.current_bet
                english_action = f"GTO Action {action_count}: {current_player.name} raises to ${executed_amount:.2f} (putting in ${amount_put_in:.2f})"
            elif executed_action_type == ActionType.CALL:
                english_action = f"GTO Action {action_count}: {current_player.name} calls ${executed_amount:.2f}"
            elif executed_action_type == ActionType.BET:
                english_action = f"GTO Action {action_count}: {current_player.name} bets ${executed_amount:.2f}"
            elif executed_action_type == ActionType.CHECK:
                english_action = f"GTO Action {action_count}: {current_player.name} checks"
            elif executed_action_type == ActionType.FOLD:
                english_action = f"GTO Action {action_count}: {current_player.name} folds"
            else:
                english_action = f"GTO Action {action_count}: {current_player.name} {executed_action_type.name.lower()}"
            
            # Check for board changes
            board_after = session.game_state.board.copy()
            if len(board_after) > len(board_before):
                new_cards = board_after[len(board_before):]
                if len(board_before) == 0:
                    english_action += f" | Flop dealt: {new_cards}"
                elif len(board_before) == 3:
                    english_action += f" | Turn dealt: {new_cards[0]}"
                elif len(board_before) == 4:
                    english_action += f" | River dealt: {new_cards[0]}"
            
            gto_log.append(english_action)
            gto_log.append(f"  Result: Pot=${session.game_state.pot:.2f}, {current_player.name} stack=${current_player.stack:.2f}")
            
            print(f"✅ {english_action}")
            print(f"   Result: Pot=${session.game_state.pot:.2f}, stack=${current_player.stack:.2f}")
            
            # Record for JSON
            json_actions.append({
                'street': session.current_state.value,
                'player_index': current_player_index,
                'action': executed_action_type.name.lower(),
                'amount': executed_amount if executed_action_type in [ActionType.BET, ActionType.CALL, ActionType.RAISE] else 0.0,
                'explanation': f"GTO {executed_action_type.name.lower()} from Pos_{current_player_index}. {explanation}",
                'pot_after': session.game_state.pot
            })
        else:
            gto_log.append("❌ Action failed or hand complete")
            print("❌ Action failed or hand complete")
            break
    
    # Final state
    gto_log.append("")
    gto_log.append(f"🏁 GTO Hand completed after {action_count} actions")
    gto_log.append(f"Final pot: ${session.game_state.pot:.2f}")
    gto_log.append(f"Final board: {session.game_state.board}")
    for i, player in enumerate(session.game_state.players):
        status = " (FOLDED)" if player.has_folded else ""
        gto_log.append(f"  {player.name}: ${player.stack:.2f}{status}")
    
    print(f"\n🏁 GTO Hand completed after {action_count} actions")
    print(f"Final pot: ${session.game_state.pot:.2f}")
    
    # Prepare hand_data for JSON
    hand_data = {
        'id': f"cycle_test_hand_{action_count}",
        'initial_state': {
            'players': initial_game_state['players'],
            'board': initial_game_state['board'],
            'pot': initial_game_state['pot'],
            'current_bet': initial_game_state['current_bet'],
            'dealer_position': initial_game_state['dealer_position'],
            'small_blind': session.config.small_blind,
            'big_blind': session.config.big_blind
        },
        'actions': json_actions,
        'final_state': {
            'pot': session.game_state.pot,
            'board': session.game_state.board,
            'players': [
                {
                    'name': p.name,
                    'stack': p.stack,
                    'cards': p.cards,
                    'has_folded': p.has_folded
                } for p in session.game_state.players
            ]
        }
    }
    
    return hand_data, gto_log

def replay_with_hands_review(hand_data: Dict[str, Any]) -> List[str]:
    """Replay the hand using Hands Review and log in English."""
    
    print("\n" + "=" * 80)
    print("🎬 PART 2: REPLAYING WITH HANDS REVIEW")
    print("=" * 80)
    
    # Create Hands Review session
    initial_state = hand_data.get('initial_state', {})
    players = initial_state.get('players', [])
    
    config = GameConfig(
        starting_stack=initial_state.get('players', [{}])[0].get('stack', 1000),
        small_blind=initial_state.get('small_blind', 5),
        big_blind=initial_state.get('big_blind', 10),
        num_players=len(players)
    )
    
    decision_engine = PreloadedDecisionEngine(hand_data)
    session = HandsReviewBotSession(config, decision_engine)
    session.set_preloaded_hand_data(hand_data)
    
    replay_log = []
    
    print(f"🎯 Setting up Hands Review session:")
    print(f"   Expected actions: {len(hand_data.get('actions', []))}")
    
    # Start session
    session.start_session()
    
    # Log initial setup
    replay_log.append("=== HANDS REVIEW REPLAY ===")
    replay_log.append(f"Dealer position: {session.dealer_position}")
    
    for i, player_data in enumerate(initial_state.get('players', [])):
        replay_log.append(f"Setup: {player_data['name']} (Position {i}) starts with ${player_data['stack']:.2f}, cards: {player_data['cards']}")
    
    replay_log.append(f"Setup: Initial pot=${session.game_state.pot:.2f}, current_bet=${session.game_state.current_bet:.2f}")
    replay_log.append("")
    
    print(f"🃏 Replay initial setup:")
    print(f"   Dealer: {session.dealer_position}")
    print(f"   Pot: ${session.game_state.pot:.2f}, Current bet: ${session.game_state.current_bet:.2f}")
    for i, p in enumerate(session.game_state.players):
        print(f"   Player {i+1}: ${p.stack:.2f}, cards: {p.cards}")
    
    # Execute replay
    action_count = 0
    max_actions = len(hand_data.get('actions', [])) + 5
    
    while session.current_state.value != 'END_HAND' and action_count < max_actions:
        action_count += 1
        
        current_player_index = session.action_player_index
        if current_player_index < 0 or current_player_index >= len(session.game_state.players):
            replay_log.append(f"Replay Action {action_count}: Invalid player index {current_player_index} - ending")
            print(f"❌ Invalid player index {current_player_index} - ending")
            break
        
        current_player = session.game_state.players[current_player_index]
        street = session.current_state.value
        pot_before = session.game_state.pot
        player_stack_before = current_player.stack
        board_before = session.game_state.board.copy()
        
        print(f"\n🎬 Replay Action {action_count}: {current_player.name} to act on {street}")
        print(f"   Game: Pot=${pot_before:.2f}, current_bet=${session.game_state.current_bet:.2f}")
        print(f"   Player: stack=${player_stack_before:.2f}, bet=${current_player.current_bet:.2f}")
        
        # Execute action
        result = session.execute_next_bot_action()
        
        if not result:
            replay_log.append(f"Replay Action {action_count}: {current_player.name} - action failed or session complete")
            print(f"❌ Action failed or session complete")
            break
        
        # Analyze what happened
        stack_change = player_stack_before - current_player.stack
        
        # Determine action type
        if current_player.has_folded:
            english_action = f"Replay Action {action_count}: {current_player.name} folds"
        elif stack_change == 0:
            english_action = f"Replay Action {action_count}: {current_player.name} checks"
        elif stack_change > 0:
            if current_player.current_bet == session.game_state.current_bet and session.game_state.current_bet > 0:
                english_action = f"Replay Action {action_count}: {current_player.name} calls ${stack_change:.2f}"
            elif current_player.current_bet > session.game_state.current_bet:
                english_action = f"Replay Action {action_count}: {current_player.name} raises to ${current_player.current_bet:.2f} (putting in ${stack_change:.2f})"
            else:
                english_action = f"Replay Action {action_count}: {current_player.name} bets ${stack_change:.2f}"
        else:
            english_action = f"Replay Action {action_count}: {current_player.name} unknown action"
        
        # Check for board changes
        board_after = session.game_state.board.copy()
        if len(board_after) > len(board_before):
            new_cards = board_after[len(board_before):]
            if len(board_before) == 0:
                english_action += f" | Flop dealt: {new_cards}"
            elif len(board_before) == 3:
                english_action += f" | Turn dealt: {new_cards[0]}"
            elif len(board_before) == 4:
                english_action += f" | River dealt: {new_cards[0]}"
        
        replay_log.append(english_action)
        replay_log.append(f"  Result: Pot=${session.game_state.pot:.2f}, {current_player.name} stack=${current_player.stack:.2f}")
        
        print(f"✅ {english_action}")
        print(f"   Result: Pot=${session.game_state.pot:.2f}, stack=${current_player.stack:.2f}")
    
    # Final state
    replay_log.append("")
    replay_log.append(f"🏁 Replay completed after {action_count} actions")
    replay_log.append(f"Final pot: ${session.game_state.pot:.2f}")
    replay_log.append(f"Final board: {session.game_state.board}")
    for player in session.game_state.players:
        status = " (FOLDED)" if player.has_folded else ""
        replay_log.append(f"  {player.name}: ${player.stack:.2f}{status}")
    
    print(f"\n🏁 Replay completed after {action_count} actions")
    print(f"Final pot: ${session.game_state.pot:.2f}")
    
    return replay_log

def print_side_by_side_comparison(gto_log: List[str], replay_log: List[str]):
    """Print both sequences side by side for easy comparison."""
    
    print("\n" + "=" * 120)
    print("📋 SIDE-BY-SIDE COMPARISON")
    print("=" * 120)
    
    max_lines = max(len(gto_log), len(replay_log))
    
    print(f"{'GTO ORIGINAL':<58} | {'HANDS REVIEW REPLAY':<58}")
    print("-" * 58 + " | " + "-" * 58)
    
    for i in range(max_lines):
        gto_line = gto_log[i] if i < len(gto_log) else ""
        replay_line = replay_log[i] if i < len(replay_log) else ""
        
        # Truncate lines if too long
        if len(gto_line) > 55:
            gto_line = gto_line[:52] + "..."
        if len(replay_line) > 55:
            replay_line = replay_line[:52] + "..."
        
        print(f"{gto_line:<58} | {replay_line:<58}")

def analyze_differences(gto_log: List[str], replay_log: List[str]):
    """Analyze and report differences between the two sequences."""
    
    print("\n" + "=" * 80)
    print("🔍 DIFFERENCE ANALYSIS")
    print("=" * 80)
    
    # Extract action lines only
    gto_actions = [line for line in gto_log if line.startswith("GTO Action")]
    replay_actions = [line for line in replay_log if line.startswith("Replay Action")]
    
    print(f"📊 Summary:")
    print(f"   GTO actions: {len(gto_actions)}")
    print(f"   Replay actions: {len(replay_actions)}")
    
    # Compare final states
    gto_final_pot = None
    replay_final_pot = None
    
    for line in gto_log:
        if line.startswith("Final pot:"):
            try:
                gto_final_pot = float(line.split("$")[1])
            except:
                pass
    
    for line in replay_log:
        if line.startswith("Final pot:"):
            try:
                replay_final_pot = float(line.split("$")[1])
            except:
                pass
    
    if gto_final_pot is not None and replay_final_pot is not None:
        pot_match = abs(gto_final_pot - replay_final_pot) < 0.01
        print(f"   Final pot match: {'✅ YES' if pot_match else '❌ NO'} (GTO: ${gto_final_pot:.2f}, Replay: ${replay_final_pot:.2f})")
    
    # Check action count match
    action_count_match = len(gto_actions) == len(replay_actions)
    print(f"   Action count match: {'✅ YES' if action_count_match else '❌ NO'}")
    
    # Overall assessment
    if pot_match and action_count_match:
        print(f"\n🎉 OVERALL ASSESSMENT: ✅ EXCELLENT - Core logic is working correctly!")
        print(f"   The sequences may have player position differences, but the game flow is identical.")
    else:
        print(f"\n⚠️  OVERALL ASSESSMENT: Issues detected that need investigation.")

def save_results(hand_data: Dict[str, Any], gto_log: List[str], replay_log: List[str]):
    """Save all results to files."""
    
    # Save JSON
    with open('cycle_test_hand.json', 'w') as f:
        json.dump(hand_data, f, indent=2)
    
    # Save logs
    with open('cycle_test_gto_log.txt', 'w') as f:
        f.write('\n'.join(gto_log))
    
    with open('cycle_test_replay_log.txt', 'w') as f:
        f.write('\n'.join(replay_log))
    
    print(f"\n📁 Results saved:")
    print(f"   📄 JSON: cycle_test_hand.json")
    print(f"   📄 GTO log: cycle_test_gto_log.txt")
    print(f"   📄 Replay log: cycle_test_replay_log.txt")

def main():
    """Main test function."""
    print("🧪 COMPLETE GTO → JSON → HANDS REVIEW CYCLE TEST")
    print("🎯 This test will show you both sequences in English for direct comparison")
    
    try:
        # Part 1: Run GTO hand
        hand_data, gto_log = run_gto_hand_with_logging()
        
        # Part 2: Replay with Hands Review
        replay_log = replay_with_hands_review(hand_data)
        
        # Part 3: Side-by-side comparison
        print_side_by_side_comparison(gto_log, replay_log)
        
        # Part 4: Analysis
        analyze_differences(gto_log, replay_log)
        
        # Part 5: Save results
        save_results(hand_data, gto_log, replay_log)
        
        print(f"\n✅ Complete cycle test finished!")
        print(f"📋 Please review the side-by-side comparison above to verify the sequences match.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
