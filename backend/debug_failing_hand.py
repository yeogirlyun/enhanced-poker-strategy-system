#!/usr/bin/env python3
"""
Debug the specific hand that's causing action execution failures.
Focus on "Holz Smith Triton Super High Roller Manila" hand.
"""

import sys
import os
from core.hands_database import ComprehensiveHandsDatabase
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, Player, GameConfig
from core.types import ActionType

def debug_failing_hand():
    """Debug the specific failing hand step by step."""
    print("🔍 DEBUGGING FAILING HAND")
    print("=" * 60)
    
    # Load the hands database
    hands_db = ComprehensiveHandsDatabase()
    hands_db.load_all_hands()
    
    # Find the failing hand
    target_hand = None
    for hand_id, hand in hands_db.all_hands.items():
        if "Holz Smith Triton" in hand.metadata.name:
            target_hand = hand
            break
    
    if not target_hand:
        print("❌ Failed to find target hand")
        return
        
    print(f"🎯 Found target hand: {target_hand.metadata.name}")
    print(f"📊 Players: {len(target_hand.players)}")
    print(f"🎴 Actions: {len(target_hand.actions) if target_hand.actions else 0}")
    
    # Show the exact action that's failing
    print(f"\n📋 Hand Actions:")
    if target_hand.actions:
        for i, action in enumerate(target_hand.actions):
            if isinstance(action, dict):
                print(f"  [{i}] {action.get('street', 'unknown')}: Actor {action.get('actor', '?')} {action.get('type', '?')} ${action.get('amount', 0)}")
            else:
                print(f"  [{i}] {action}")
    else:
        print("  No actions found!")
        
    # Show player details
    print(f"\n👥 Players:")
    for i, player in enumerate(target_hand.players):
        print(f"  [{i}] {player.get('name', 'Unknown')} - Stack: ${player.get('starting_stack_chips', 0):,}")
    
    # Set up FPSM with exact same configuration
    print(f"\n🎯 Setting up FPSM...")
    num_players = len(target_hand.players)
    
    # Create game config
    config = GameConfig(
        num_players=num_players,
        small_blind=50000,  # From the logs
        big_blind=100000,
        test_mode=False,  # Use normal mode to match GUI behavior
        show_all_cards=True,
        auto_advance=False  # Use manual advance to match GUI behavior
    )
    
    # Create FPSM
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create players with exact stacks from PHH
    fpsm_players = []
    for i, player_info in enumerate(target_hand.players):
        # Get actual starting stack from PHH data
        starting_stack = player_info.get('starting_stack_chips', 5000000)
        
        player = Player(
            name=player_info.get('name', f'Player {i+1}'),
            stack=starting_stack,
            position=f"P{i}",
            is_human=False,
            is_active=True,
            cards=player_info.get('cards', [])
        )
        fpsm_players.append(player)
    
    print(f"📊 Created {len(fpsm_players)} FPSM players")
    
    # Start the hand
    print(f"\n🚀 Starting hand...")
    fpsm.start_hand(fpsm_players)
    
    # Debug the exact state when the failure occurs
    print(f"\n🔍 FPSM State after hand start:")
    print(f"  Current state: {fpsm.game_state.state}")
    print(f"  Current player index: {fpsm.current_player_index}")
    print(f"  Current player: {fpsm.players[fpsm.current_player_index].name if fpsm.current_player_index < len(fpsm.players) else 'None'}")
    print(f"  Current bet: ${fpsm.game_state.current_bet:,}")
    print(f"  Pot: ${fpsm.game_state.pot:,}")
    
    # Show each player's state
    print(f"\n👥 Player states:")
    for i, player in enumerate(fpsm.players):
        print(f"  [{i}] {player.name}: Stack=${player.stack:,}, Bet=${player.current_bet:,}, Folded={player.has_folded}")
    
    # Test the exact failing action: "Fedor Holz call $2300000.0"
    print(f"\n🧪 Testing the failing action...")
    
    # Find Fedor Holz
    fedor_player = None
    for player in fpsm.players:
        if "Fedor Holz" in player.name:
            fedor_player = player
            break
    
    if not fedor_player:
        print("❌ Could not find Fedor Holz player")
        return
        
    print(f"🎯 Found Fedor Holz: Stack=${fedor_player.stack:,}, Bet=${fedor_player.current_bet:,}")
    
    # Check if it's actually Fedor's turn
    current_player = fpsm.players[fpsm.current_player_index]
    print(f"🎯 Current player is: {current_player.name}")
    print(f"🎯 Is it Fedor's turn? {'YES' if current_player == fedor_player else 'NO'}")
    
    if current_player != fedor_player:
        print("⚠️  The failing action is being attempted on the wrong player!")
        print(f"   Expected: {fedor_player.name}")
        print(f"   Actual: {current_player.name}")
        return
    
    # Get valid actions for current player
    valid_actions = fpsm.get_valid_actions(current_player)
    print(f"✅ Valid actions for {current_player.name}: {[action.value for action in valid_actions]}")
    
    # Check if CALL is valid
    if ActionType.CALL not in valid_actions:
        print(f"❌ CALL is not a valid action for {current_player.name}")
        print(f"   Valid actions: {[action.value for action in valid_actions]}")
        print(f"   Current bet: ${fpsm.game_state.current_bet:,}")
        print(f"   Player bet: ${current_player.current_bet:,}")
        print(f"   Player stack: ${current_player.stack:,}")
        
        # Calculate call amount
        call_amount = fpsm.game_state.current_bet - current_player.current_bet
        print(f"   Required call amount: ${call_amount:,}")
        
        if call_amount > current_player.stack:
            print(f"   🚨 PROBLEM: Player doesn't have enough stack to call!")
        
        return
    
    # Try to execute the failing action
    print(f"\n🎲 Attempting to execute: call $2,300,000")
    
    # Calculate actual call amount needed
    call_amount = fpsm.game_state.current_bet - current_player.current_bet
    print(f"   Required call amount: ${call_amount:,}")
    print(f"   Player has: ${current_player.stack:,}")
    
    if call_amount > current_player.stack:
        print(f"   ⚠️  Player cannot afford full call amount")
        actual_call = current_player.stack  # All-in
        print(f"   Will attempt all-in for: ${actual_call:,}")
    else:
        actual_call = call_amount
    
    # Execute the action
    try:
        success = fpsm.execute_action(current_player, ActionType.CALL, actual_call)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"   New player stack: ${current_player.stack:,}")
            print(f"   New player bet: ${current_player.current_bet:,}")
            print(f"   New pot: ${fpsm.game_state.pot:,}")
        else:
            print(f"   ❌ Action execution failed in FPSM")
            
    except Exception as e:
        print(f"   ❌ Exception during action execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_failing_hand()
