#!/usr/bin/env python3
"""
Test various showdown scenarios with deuces integration.
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_showdown_scenarios():
    """Test different showdown scenarios."""
    
    print("🎭 TESTING SHOWDOWN SCENARIOS")
    print("=" * 40)
    
    # Test 1: High card vs pair
    print("\n🧪 Test 1: High card vs pair")
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    ppsm.game_state.players[0].cards = ['Ah', 'Kc']  # High card
    ppsm.game_state.players[1].cards = ['2h', '2c']  # Pair
    ppsm.game_state.board = ['7s', '8d', '9h', 'Jc', 'Qd']
    ppsm.game_state.committed_pot = 50.0
    
    ppsm._resolve_showdown()
    print(f"Winner should be Seat2 (pair): {ppsm.game_state.players[1].stack > 1000}")
    
    # Test 2: Split pot scenario
    print("\n🧪 Test 2: Split pot (both make same straight)")
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    ppsm.game_state.players[0].cards = ['Ah', '2c']  # Both make 9-high straight
    ppsm.game_state.players[1].cards = ['Kh', '3c']  # Both make 9-high straight
    ppsm.game_state.board = ['5s', '6d', '7h', '8c', '9d']  # 5-6-7-8-9 straight on board
    ppsm.game_state.committed_pot = 100.0
    
    initial_1 = ppsm.game_state.players[0].stack
    initial_2 = ppsm.game_state.players[1].stack
    ppsm._resolve_showdown()
    
    final_1 = ppsm.game_state.players[0].stack
    final_2 = ppsm.game_state.players[1].stack
    
    print(f"Player 1 gain: {final_1 - initial_1}")
    print(f"Player 2 gain: {final_2 - initial_2}")
    print(f"Split pot successful: {abs((final_1 - initial_1) - (final_2 - initial_2)) < 0.01}")
    
    # Test 3: Single player (all others folded)
    print("\n🧪 Test 3: Single player remaining")
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=3, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Fold two players
    ppsm.game_state.players[1].has_folded = True
    ppsm.game_state.players[1].is_active = False
    ppsm.game_state.players[2].has_folded = True
    ppsm.game_state.players[2].is_active = False
    
    ppsm.game_state.committed_pot = 75.0
    initial = ppsm.game_state.players[0].stack
    
    ppsm._resolve_showdown()
    
    final = ppsm.game_state.players[0].stack
    print(f"Single winner gain: {final - initial} (should be $75)")
    
    print("\n🎉 SHOWDOWN SCENARIOS TEST COMPLETE!")


if __name__ == "__main__":
    test_showdown_scenarios()
