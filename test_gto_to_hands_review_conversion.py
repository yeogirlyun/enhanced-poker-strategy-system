#!/usr/bin/env python3
"""
Test GTO bot hand generation -> JSON export -> Hands Review import -> Replay
This will help us identify exactly where the conversion breaks down.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import json
from core.bot_session_state_machine import GTOBotSession, HandsReviewBotSession
from core.flexible_poker_state_machine import GameConfig
from core.session_logger import SessionLogger
from core.decision_engine_v2 import PreloadedDecisionEngine

def log_game_state(session, action_description=""):
    """Log current game state in human-readable format."""
    game_state = session.get_game_info()
    
    print(f"\n=== GAME STATE: {action_description} ===")
    print(f"Street: {game_state.get('street', 'unknown')}")
    print(f"Pot: ${game_state.get('pot', 0):.2f}")
    print(f"Current bet: ${game_state.get('current_bet', 0):.2f}")
    
    # Board cards
    board = game_state.get('board', [])
    if board:
        print(f"Board: {' '.join(board)}")
    
    # Players
    players = game_state.get('players', [])
    for i, player in enumerate(players):
        cards_display = ' '.join(player.get('cards', ['**', '**']))
        stack = player.get('stack', 0)
        current_bet = player.get('current_bet', 0)
        status = ""
        if player.get('has_folded', False):
            status = " (FOLDED)"
        if i == session.action_player_index:
            status += " <-- ACTION"
            
        print(f"Player {i+1}: {cards_display} | Stack: ${stack:.2f} | Bet: ${current_bet:.2f}{status}")

def run_gto_session_and_log():
    """Run a GTO session and log every action in English."""
    print("🎯 STEP 1: Creating GTO Session and logging all actions")
    print("=" * 60)
    
    # Create GTO session
    config = GameConfig(
        starting_stack=1000.0,
        small_blind=5.0,
        big_blind=10.0,
        num_players=3
    )
    
    logger = SessionLogger()
    gto_session = GTOBotSession(config)
    
    # Start session
    gto_session.start_session()
    
    action_log = []
    action_count = 0
    
    print(f"\n🚀 Starting GTO session with {config.num_players} players")
    log_game_state(gto_session, "Initial state after blinds")
    
    # Log initial state
    initial_state = gto_session.get_game_info()
    action_log.append({
        "action_type": "initial_state",
        "description": "Game started with blinds posted",
        "game_state": initial_state
    })
    
    # Execute actions until hand complete  
    while gto_session.current_state.name != 'END_HAND' and action_count < 20:  # Safety limit
        action_count += 1
        
        # Get current player info
        current_player = gto_session.get_action_player()
        if not current_player:
            print("❌ No current player found - hand may be complete")
            break
            
        current_game_state = gto_session.get_game_info()
        
        # Execute bot action
        result = gto_session.execute_next_bot_action()
        if not result:
            print(f"❌ Action {action_count} failed to execute")
            break
            
        # Get the action details from the last executed action
        new_game_state = gto_session.get_game_info()
        
        # Log the action in English
        action_description = f"Action {action_count}: Player {current_player.name} "
        
        # Determine what action was taken by comparing states
        old_pot = current_game_state.get('pot', 0)
        new_pot = new_game_state.get('pot', 0)
        old_current_bet = current_game_state.get('current_bet', 0)
        new_current_bet = new_game_state.get('current_bet', 0)
        
        player_index = gto_session.action_player_index
        if player_index < len(current_game_state.get('players', [])):
            old_player_bet = current_game_state['players'][player_index].get('current_bet', 0)
            new_player_bet = new_game_state['players'][player_index].get('current_bet', 0)
            bet_difference = new_player_bet - old_player_bet
            
            if bet_difference == 0:
                if new_game_state['players'][player_index].get('has_folded', False):
                    action_description += "FOLDED"
                else:
                    action_description += "CHECKED"
            elif new_current_bet > old_current_bet:
                if old_current_bet == 0:
                    action_description += f"BET ${bet_difference:.2f}"
                else:
                    action_description += f"RAISED to ${new_current_bet:.2f} (raised ${bet_difference - old_current_bet:.2f})"
            else:
                action_description += f"CALLED ${bet_difference:.2f}"
        
        print(f"\n{action_description}")
        log_game_state(gto_session, action_description)
        
        # Store action details
        action_log.append({
            "action_type": "player_action",
            "action_number": action_count,
            "player_index": player_index,
            "description": action_description,
            "game_state_before": current_game_state,
            "game_state_after": new_game_state
        })
        
        # Check for street transitions
        old_street = current_game_state.get('street', 'preflop')
        new_street = new_game_state.get('street', 'preflop')
        if old_street != new_street:
            print(f"\n🃏 STREET TRANSITION: {old_street} → {new_street}")
            if new_street in ['flop', 'turn', 'river']:
                board = new_game_state.get('board', [])
                print(f"Board: {' '.join(board)}")
    
    print(f"\n🎯 GTO session completed after {action_count} actions")
    print("=" * 60)
    
    return gto_session, action_log

def convert_gto_to_hands_review_format(gto_session, action_log):
    """Convert GTO session data to hands review JSON format."""
    print("\n🔄 STEP 2: Converting GTO data to Hands Review format")
    print("=" * 60)
    
    # Get final game state
    final_state = gto_session.get_game_info()
    
    # Extract actions in chronological order
    actions = []
    for log_entry in action_log:
        if log_entry["action_type"] == "player_action":
            before_state = log_entry["game_state_before"]
            after_state = log_entry["game_state_after"]
            
            # Determine action type and amount
            player_idx = log_entry["player_index"]
            
            if player_idx < len(before_state.get('players', [])):
                old_bet = before_state['players'][player_idx].get('current_bet', 0)
                new_bet = after_state['players'][player_idx].get('current_bet', 0)
                bet_amount = new_bet - old_bet
                
                # Determine action type
                if after_state['players'][player_idx].get('has_folded', False):
                    action_type = "fold"
                    amount = 0.0
                elif bet_amount == 0:
                    action_type = "check"
                    amount = 0.0
                elif after_state.get('current_bet', 0) > before_state.get('current_bet', 0):
                    if before_state.get('current_bet', 0) == 0:
                        action_type = "bet"
                    else:
                        action_type = "raise"
                    amount = float(bet_amount)
                else:
                    action_type = "call"
                    amount = float(bet_amount)
                
                action = {
                    "street": after_state.get('street', 'preflop'),
                    "player_index": player_idx,
                    "action": action_type,
                    "amount": amount,
                    "explanation": f"GTO {action_type} from Pos_{player_idx}",
                    "pot_after": float(after_state.get('pot', 0))
                }
                actions.append(action)
                print(f"Action: Player {player_idx} {action_type} {amount} on {after_state.get('street', 'preflop')}")
    
    # Create hands review format
    hands_review_data = {
        "id": "test_gto_hand_001",
        "initial_state": {
            "players": final_state.get('players', []),
            "dealer_position": final_state.get('dealer_position', 0),
            "small_blind": gto_session.config.small_blind,
            "big_blind": gto_session.config.big_blind,
            "starting_stacks": gto_session.config.starting_stack
        },
        "actions": actions,
        "final_state": final_state
    }
    
    print(f"✅ Converted {len(actions)} actions to hands review format")
    return hands_review_data

def save_to_json(hands_review_data, filename="test_gto_conversion.json"):
    """Save hands review data to JSON file."""
    print(f"\n💾 STEP 3: Saving to {filename}")
    print("=" * 60)
    
    filepath = os.path.join("data", filename)
    os.makedirs("data", exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(hands_review_data, f, indent=2, default=str)
    
    print(f"✅ Saved hands review data to {filepath}")
    return filepath

def load_and_replay_hands_review(filepath):
    """Load JSON data and replay through hands review state machine."""
    print(f"\n🔄 STEP 4: Loading and replaying through Hands Review")
    print("=" * 60)
    
    # Load JSON data
    with open(filepath, 'r') as f:
        hands_data = json.load(f)
    
    print(f"📖 Loaded hand: {hands_data.get('id', 'unknown')}")
    print(f"📖 Actions to replay: {len(hands_data.get('actions', []))}")
    
    # Create hands review session
    config = GameConfig(
        starting_stack=hands_data['initial_state']['starting_stacks'],
        small_blind=hands_data['initial_state']['small_blind'],
        big_blind=hands_data['initial_state']['big_blind'],
        num_players=len(hands_data['initial_state']['players'])
    )
    
    logger = SessionLogger()
    decision_engine = PreloadedDecisionEngine(hands_data)
    hands_review_session = HandsReviewBotSession(config, decision_engine)
    
    # Set preloaded data and start session
    hands_review_session.set_preloaded_hand_data(hands_data)
    hands_review_session.start_session()
    
    print(f"\n🚀 Starting Hands Review replay")
    log_game_state(hands_review_session, "Initial state")
    
    replay_log = []
    action_count = 0
    
    # Execute actions through hands review
    while not hands_review_session.decision_engine.is_session_complete() and action_count < 20:
        action_count += 1
        
        current_player = hands_review_session.get_action_player()
        if not current_player:
            print("❌ No current player found in hands review")
            break
            
        current_state = hands_review_session.get_game_info()
        
        # Execute next action
        result = hands_review_session.execute_next_bot_action()
        if not result:
            print(f"❌ Hands review action {action_count} failed")
            break
            
        new_state = hands_review_session.get_game_info()
        
        # Log action in English
        player_index = hands_review_session.action_player_index
        action_description = f"Replay {action_count}: Player {current_player.name} "
        
        # Determine action taken
        if player_index < len(current_state.get('players', [])):
            old_bet = current_state['players'][player_index].get('current_bet', 0)
            new_bet = new_state['players'][player_index].get('current_bet', 0)
            bet_difference = new_bet - old_bet
            
            if bet_difference == 0:
                if new_state['players'][player_index].get('has_folded', False):
                    action_description += "FOLDED"
                else:
                    action_description += "CHECKED"
            elif new_state.get('current_bet', 0) > current_state.get('current_bet', 0):
                if current_state.get('current_bet', 0) == 0:
                    action_description += f"BET ${bet_difference:.2f}"
                else:
                    action_description += f"RAISED to ${new_state.get('current_bet', 0):.2f}"
            else:
                action_description += f"CALLED ${bet_difference:.2f}"
        
        print(f"\n{action_description}")
        log_game_state(hands_review_session, action_description)
        
        replay_log.append({
            "action_number": action_count,
            "description": action_description,
            "player_index": player_index,
            "game_state": new_state
        })
    
    print(f"\n🎯 Hands review replay completed after {action_count} actions")
    return replay_log

def compare_sequences(gto_log, replay_log):
    """Compare GTO and Hands Review sequences to identify differences."""
    print(f"\n🔍 STEP 5: Comparing sequences")
    print("=" * 60)
    
    gto_actions = [entry for entry in gto_log if entry["action_type"] == "player_action"]
    
    print(f"GTO actions: {len(gto_actions)}")
    print(f"Replay actions: {len(replay_log)}")
    
    min_length = min(len(gto_actions), len(replay_log))
    differences = []
    
    for i in range(min_length):
        gto_action = gto_actions[i]
        replay_action = replay_log[i]
        
        gto_desc = gto_action["description"]
        replay_desc = replay_action["description"]
        
        if gto_desc != replay_desc:
            differences.append({
                "action_number": i + 1,
                "gto": gto_desc,
                "replay": replay_desc
            })
    
    if differences:
        print(f"\n❌ Found {len(differences)} differences:")
        for diff in differences:
            print(f"Action {diff['action_number']}:")
            print(f"  GTO:    {diff['gto']}")
            print(f"  Replay: {diff['replay']}")
    else:
        print(f"\n✅ All {min_length} actions match perfectly!")
    
    if len(gto_actions) != len(replay_log):
        print(f"\n⚠️  Different number of actions: GTO={len(gto_actions)}, Replay={len(replay_log)}")
    
    return differences

def main():
    """Run the complete GTO -> Hands Review conversion test."""
    print("🧪 GTO to Hands Review Conversion Test")
    print("=" * 80)
    
    try:
        # Step 1: Run GTO session
        gto_session, gto_log = run_gto_session_and_log()
        
        # Step 2: Convert to hands review format
        hands_review_data = convert_gto_to_hands_review_format(gto_session, gto_log)
        
        # Step 3: Save to JSON
        filepath = save_to_json(hands_review_data)
        
        # Step 4: Load and replay
        replay_log = load_and_replay_hands_review(filepath)
        
        # Step 5: Compare sequences
        differences = compare_sequences(gto_log, replay_log)
        
        print("\n" + "=" * 80)
        if not differences:
            print("🎉 SUCCESS: Perfect GTO -> Hands Review conversion!")
        else:
            print(f"❌ ISSUES FOUND: {len(differences)} action mismatches")
            print("This indicates the conversion or replay logic needs fixing.")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
