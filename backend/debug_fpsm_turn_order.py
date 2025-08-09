#!/usr/bin/env python3
"""
Debug FPSM Turn Order Issues

Investigates the root cause of action execution failures by comparing
FPSM's natural turn order with the historical action sequence.
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player, ActionType
from core.position_mapping import UniversalPosition

def debug_hand_turn_order():
    """Debug turn order issues with a specific hand."""
    
    # Load JSON data
    with open('data/legendary_hands_complete.json', 'r') as f:
        data = json.load(f)
    
    # Use the first failing hand for debugging
    hand_data = data['hands'][0]  # Moneymaker Farha hand
    
    print("🔍 DEBUGGING FPSM TURN ORDER vs HISTORICAL ACTIONS")
    print("=" * 60)
    print(f"Hand: {hand_data['name']}")
    print(f"Players: {hand_data['game_config']['num_players']}")
    
    # Create FPSM
    config = GameConfig(
        num_players=hand_data['game_config']['num_players'],
        big_blind=hand_data['game_config']['big_blind'],
        small_blind=hand_data['game_config']['small_blind'],
        starting_stack=1000000.0,
        test_mode=True
    )
    
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create players
    players = []
    for player_data in hand_data['players']:
        player = Player(
            name=player_data['name'],
            stack=player_data['starting_stack'],
            position=UniversalPosition.BB.value,
            is_human=False,
            is_active=True,
            cards=player_data.get('hole_cards', [])
        )
        players.append(player)
    
    # Initialize hand
    fpsm.start_hand(players)
    
    # Show FPSM player setup
    print(f"\n📋 FPSM PLAYER SETUP:")
    for i, player in enumerate(fpsm.game_state.players):
        print(f"  [{i}] {player.name:20} | Stack: ${player.stack:>8,.0f} | Position: {player.position}")
    
    # Show historical action sequence
    print(f"\n📜 HISTORICAL ACTION SEQUENCE:")
    for street in ['preflop', 'flop', 'turn', 'river']:
        if street in hand_data['actions']:
            print(f"\n  {street.upper()}:")
            for i, action in enumerate(hand_data['actions'][street]):
                actor = action.get('actor', '?')
                seat = action.get('player_seat', '?')
                player_name = action.get('player_name', 'Unknown')
                action_type = action.get('action_type', '?')
                amount = action.get('amount', 0)
                print(f"    {i+1}. Actor {actor} (Seat {seat}) {player_name:20} {action_type} ${amount:,.0f}")
    
    # Test FPSM natural turn order vs historical
    print(f"\n🔄 TESTING TURN ORDER ALIGNMENT:")
    
    # Build seat mapping
    seat_to_player = {}
    for i, player_data in enumerate(hand_data['players']):
        seat_to_player[player_data['seat']] = fpsm.game_state.players[i]
    
    print(f"  Seat to Player Mapping:")
    for seat, player in seat_to_player.items():
        print(f"    Seat {seat} -> {player.name}")
    
    # Test preflop actions
    preflop_actions = hand_data['actions']['preflop']
    print(f"\n🎯 PREFLOP TURN ORDER TEST:")
    
    actions_attempted = 0
    for i, historical_action in enumerate(preflop_actions):
        current_player = fpsm.get_action_player()
        historical_seat = historical_action['player_seat']
        historical_player = seat_to_player.get(historical_seat)
        
        print(f"\n  Action {i+1}:")
        print(f"    FPSM expects: {current_player.name if current_player else 'None'}")
        print(f"    History has:  {historical_player.name if historical_player else 'None'} (Seat {historical_seat})")
        print(f"    Match: {'✅' if current_player == historical_player else '❌'}")
        
        if current_player != historical_player:
            print(f"    ⚠️  TURN ORDER MISMATCH!")
            print(f"         FPSM thinks it's {current_player.name}'s turn")
            print(f"         But history says {historical_player.name} acted")
            break
        
        # Execute the historical action to advance FPSM
        action_type_str = historical_action['action_type']
        amount = historical_action.get('amount', 0.0)
        
        # Parse action type
        action_mapping = {
            'fold': ActionType.FOLD,
            'check': ActionType.CHECK,
            'call': ActionType.CALL,
            'bet': ActionType.BET,
            'raise': ActionType.RAISE,
        }
        
        action_type = action_mapping.get(action_type_str.lower())
        if action_type:
            success = fpsm.execute_action(current_player, action_type, amount)
            print(f"    Executed: {action_type} ${amount} -> {'✅' if success else '❌'}")
            if success:
                actions_attempted += 1
            else:
                print(f"    💥 EXECUTION FAILED!")
                print(f"       Player: {current_player.name}")
                print(f"       Stack: ${current_player.stack}")
                print(f"       Current bet: ${getattr(current_player, 'current_bet', 0)}")
                print(f"       Game state: {fpsm.current_state}")
                print(f"       Game current bet: ${fpsm.game_state.current_bet}")
                break
        else:
            print(f"    💥 UNKNOWN ACTION TYPE: {action_type_str}")
            break
    
    print(f"\n📊 SUMMARY:")
    print(f"  Actions attempted: {actions_attempted}/{len(preflop_actions)}")
    print(f"  Success rate: {actions_attempted/len(preflop_actions)*100:.1f}%")

if __name__ == "__main__":
    debug_hand_turn_order()
