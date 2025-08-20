#!/usr/bin/env python3
"""
Test FPSM Action Execution

Debug why GTO hands are not completing after actions are executed.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pure_poker_state_machine import GameConfig
from core.sessions import GTOSession
from core.decision_engine import GTODecisionEngine
from core.poker_types import ActionType

def test_fpsm_action_execution():
    """Test FPSM action execution to see why hands are not completing."""
    
    print("🧪 Testing FPSM action execution...")
    
    # Create config for 2 players
    config = GameConfig(
        num_players=2,
        small_blind=5,
        big_blind=10,
        starting_stack=1000
    )
    
    # Create GTO decision engines
    gto_decision_engines = {}
    for i in range(2):
        gto_decision_engines[f"GTO_Bot_{i+1}"] = GTODecisionEngine(num_players=2)
    
    # Create GTO session
    session = GTOSession(config, decision_engines=gto_decision_engines, seed=42)
    
    # Initialize session
    if not session.initialize_session():
        print("❌ Failed to initialize GTO session")
        return
    
    print("✅ Session initialized")
    
    # Start hand
    if not session.start_hand():
        print("❌ Failed to start hand")
        return
    
    print("✅ Hand started")
    
    # Get initial game state
    initial_info = session.get_game_info()
    print(f"\n🎯 Initial game state:")
    print(f"   Street: {initial_info.get('street', 'unknown')}")
    print(f"   Pot: {initial_info.get('pot', 0)}")
    print(f"   Current bet: {initial_info.get('current_bet', 0)}")
    print(f"   Action player index: {initial_info.get('action_player_index', -1)}")
    
    # Check player states
    for i, player in enumerate(initial_info.get('players', [])):
        print(f"   Player {i}: {player.get('name', 'Unknown')}")
        print(f"     Stack: {player.get('stack', 0)}")
        print(f"     Current bet: {player.get('current_bet', 0)}")
        print(f"     Folded: {player.get('has_folded', False)}")
        print(f"     Active: {player.get('is_active', False)}")
    
    # Execute first action manually
    print(f"\n🔄 Executing first action...")
    
    # Get action player
    action_player = session.get_action_player()
    if not action_player:
        print("❌ No action player available")
        return
    
    print(f"   Action player: {action_player.name}")
    print(f"   Cards: {action_player.cards}")
    print(f"   Stack: {action_player.stack}")
    print(f"   Current bet: {action_player.current_bet}")
    
    # Get valid actions
    valid_actions = session.get_valid_actions_for_player(action_player)
    print(f"   Valid actions: {valid_actions}")
    
    # Execute call action manually
    print(f"\n🎯 Executing CALL action...")
    success = session.execute_action(action_player, ActionType.CALL, 5.0)
    print(f"   Action execution result: {success}")
    
    if success:
        # Get post-action game state
        post_action_info = session.get_game_info()
        print(f"\n🎯 Post-action game state:")
        print(f"   Street: {post_action_info.get('street', 'unknown')}")
        print(f"   Pot: {post_action_info.get('pot', 0)}")
        print(f"   Current bet: {post_action_info.get('current_bet', 0)}")
        print(f"   Action player index: {post_action_info.get('action_player_index', -1)}")
        print(f"   Hand complete: {session.is_hand_complete()}")
        
        # Check player states
        for i, player in enumerate(post_action_info.get('players', [])):
            print(f"   Player {i}: {player.get('name', 'Unknown')}")
            print(f"     Stack: {player.get('stack', 0)}")
            print(f"     Current bet: {player.get('current_bet', 0)}")
            print(f"     Folded: {player.get('has_folded', False)}")
            print(f"     Active: {player.get('is_active', False)}")
        
        # Try to get next action player
        next_action_player = session.get_action_player()
        if next_action_player:
            print(f"\n✅ Next action player: {next_action_player.name}")
        else:
            print(f"\n❌ No next action player available")
            print(f"   This suggests the hand ended prematurely")
    else:
        print(f"\n❌ Action execution failed")
    
    print(f"\n🏁 Test completed")

if __name__ == "__main__":
    test_fpsm_action_execution()
