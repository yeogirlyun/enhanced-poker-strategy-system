#!/usr/bin/env python3
"""
Simple GTO Hands Test

Test the GTO hands generator with just a few hands to debug completion issues.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pure_poker_state_machine import GameConfig
from core.sessions import GTOSession
from core.decision_engine import GTODecisionEngine

def test_single_hand():
    """Test a single GTO hand to see why it's not completing."""
    
    print("🧪 Testing single GTO hand completion...")
    
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
    
    # Run hand with detailed logging
    max_actions = 50
    actions_taken = 0
    
    print(f"\n🎯 Starting hand execution...")
    print(f"   Initial state: {session.is_hand_complete()}")
    
    while (not session.is_hand_complete() and 
           actions_taken < max_actions and 
           session.session_active):
        
        # Get current game info
        game_info = session.get_game_info()
        action_player_index = session.fpsm.action_player_index if session.fpsm else -1
        
        print(f"\n🔄 Action {actions_taken + 1}:")
        print(f"   Hand complete: {session.is_hand_complete()}")
        print(f"   Session active: {session.session_active}")
        print(f"   Action player: {action_player_index}")
        print(f"   Street: {game_info.get('street', 'unknown')}")
        print(f"   Pot: {game_info.get('pot', 0)}")
        print(f"   Current bet: {game_info.get('current_bet', 0)}")
        
        if action_player_index < 0:
            print("   ❌ No action player available")
            break
            
        action_player = game_info['players'][action_player_index] if action_player_index < len(game_info['players']) else None
        
        if not action_player:
            print("   ❌ Action player not found")
            break
        
        print(f"   Player: {action_player.get('name', 'Unknown')}")
        print(f"   Cards: {action_player.get('cards', [])}")
        print(f"   Stack: {action_player.get('stack', 0)}")
        print(f"   Current bet: {action_player.get('current_bet', 0)}")
        
        # Execute bot action
        success = session.execute_next_bot_action()
        
        if success:
            print(f"   ✅ Action executed successfully")
            actions_taken += 1
        else:
            print(f"   ❌ Action execution failed")
            break
    
    print(f"\n🏁 Hand execution completed:")
    print(f"   Actions taken: {actions_taken}")
    print(f"   Hand complete: {session.is_hand_complete()}")
    print(f"   Session active: {session.session_active}")
    
    # Get final game info
    final_info = session.get_game_info()
    print(f"   Final street: {final_info.get('street', 'unknown')}")
    print(f"   Final pot: {final_info.get('pot', 0)}")
    
    # Check player states
    for i, player in enumerate(final_info.get('players', [])):
        print(f"   Player {i}: {player.get('name', 'Unknown')}")
        print(f"     Stack: {player.get('stack', 0)}")
        print(f"     Folded: {player.get('has_folded', False)}")
        print(f"     Active: {player.get('is_active', False)}")

if __name__ == "__main__":
    test_single_hand()
