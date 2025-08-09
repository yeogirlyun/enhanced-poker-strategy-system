#!/usr/bin/env python3
"""
Test the exact action execution that's failing: "Fedor Holz call $2300000.0"
This reproduces the scenario outside the GUI to isolate the issue.
"""

import sys
import os
from core.hands_database import ComprehensiveHandsDatabase
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, Player, GameConfig
from core.types import ActionType

def test_action_execution():
    """Test the specific failing action execution scenario."""
    print("🧪 TESTING ACTION EXECUTION")
    print("=" * 50)
    
    # Get the exact PHH data
    hands_db = ComprehensiveHandsDatabase()
    hands_db.load_all_hands()
    
    target_hand = None
    for hand_id, hand in hands_db.all_hands.items():
        if "Holz Smith Triton" in hand.metadata.name:
            target_hand = hand
            break
    
    print(f"🎯 Testing hand: {target_hand.metadata.name}")
    
    # Extract the actions
    preflop_actions = target_hand.actions.get('preflop', [])
    print(f"📋 Preflop actions: {len(preflop_actions)}")
    for i, action in enumerate(preflop_actions):
        print(f"  [{i}] Actor {action['actor']} {action['type']} {action.get('amount', action.get('to', 0))}")
    
    # Set up FPSM with exact same configuration as hands review panel
    print(f"\n🔧 Setting up FPSM...")
    
    config = GameConfig(
        num_players=9,
        small_blind=50000,
        big_blind=100000,
        test_mode=False,  # Match GUI mode
        show_all_cards=True,
        auto_advance=False  # Match GUI mode
    )
    
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create players with exact same setup as hands review panel
    fpsm_players = []
    for i, player_info in enumerate(target_hand.players):
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
    
    print(f"👥 Created {len(fpsm_players)} players")
    
    # Start the hand
    print(f"\n🚀 Starting hand...")
    fpsm.start_hand(fpsm_players)
    
    print(f"🎮 Initial state:")
    print(f"  Pot: ${fpsm.game_state.pot:,}")
    print(f"  Current bet: ${fpsm.game_state.current_bet:,}")
    print(f"  Players in game: {len(fpsm.game_state.players)}")
    
    # Execute all preflop actions in sequence
    print(f"\n🎯 Executing preflop actions...")
    
    for i, action in enumerate(preflop_actions):
        actor_id = action['actor']
        action_type = action['type'].upper()
        
        # Find the FPSM player corresponding to this actor
        target_player = None
        for j, player in enumerate(fpsm.game_state.players):
            # Actor IDs in PHH are 1-based seat numbers
            if j + 1 == actor_id:  # Convert to 0-based index
                target_player = player
                break
        
        if not target_player:
            print(f"❌ Could not find player for actor {actor_id}")
            continue
            
        print(f"\n  Action [{i}]: {target_player.name} (Actor {actor_id}) {action_type}")
        
        # Check if it's this player's turn  
        current_player = fpsm.game_state.players[fpsm.action_player_index]
        if current_player != target_player:
            print(f"    ⚠️  Turn mismatch: Expected {target_player.name}, but it's {current_player.name}'s turn")
            print(f"    🎯 Attempting to process actions to get to correct player...")
            
            # Let the wrong player fold to advance turn
            print(f"    🔄 Making {current_player.name} fold to advance turn")
            success = fpsm.execute_action(current_player, ActionType.FOLD, 0)
            print(f"       Result: {'✅' if success else '❌'}")
            
            # Skip the action order logic for now and just continue with this action
                            
            if current_player != target_player:
                print(f"    ❌ Still wrong player after attempting to advance")
                continue
        
        # Now execute the intended action
        current_player = fpsm.game_state.players[fpsm.action_player_index]
        print(f"    🎮 Current turn: {current_player.name}")
        print(f"    💰 Stack: ${current_player.stack:,}, Bet: ${current_player.current_bet:,}")
        print(f"    🎯 Game state: Pot=${fpsm.game_state.pot:,}, Current bet=${fpsm.game_state.current_bet:,}")
        
        # Get the action amount
        amount = 0
        if action_type in ['RAISE', 'RERAISE'] and 'to' in action:
            amount = action['to']
        elif 'amount' in action:
            amount = action['amount']
        
        print(f"    🎲 Attempting: {action_type} ${amount:,}")
        
        # Convert action type to ActionType enum
        action_enum = None
        try:
            if action_type == 'FOLD':
                action_enum = ActionType.FOLD
            elif action_type == 'CALL':
                action_enum = ActionType.CALL
            elif action_type == 'RAISE':
                action_enum = ActionType.RAISE
            elif action_type == 'BET':
                action_enum = ActionType.BET
            elif action_type == 'ALL-IN':
                action_enum = ActionType.ALL_IN
            else:
                print(f"    ❌ Unknown action type: {action_type}")
                continue
        except Exception as e:
            print(f"    ❌ Could not convert action type: {action_type}: {e}")
            continue
        
        # Execute the action
        success = fpsm.execute_action(current_player, action_enum, amount)
        print(f"    Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"    💰 New stack: ${current_player.stack:,}")
            print(f"    💸 New bet: ${current_player.current_bet:,}")
            print(f"    🏦 New pot: ${fpsm.game_state.pot:,}")
        else:
            print(f"    ❌ Action execution failed!")
            print(f"       This is the exact failure we're trying to fix!")
            break
    
    print(f"\n✅ Action execution test complete")

if __name__ == "__main__":
    test_action_execution()
