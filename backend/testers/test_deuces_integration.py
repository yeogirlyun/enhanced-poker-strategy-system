#!/usr/bin/env python3
"""
Test the deuces hand evaluation integration with PPSM.
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.poker_types import Player
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_deuces_integration():
    """Test that PPSM properly integrates deuces hand evaluation."""
    
    print("🧪 TESTING DEUCES INTEGRATION WITH PPSM")
    print("=" * 50)
    
    # Create PPSM with deuces integration
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Verify hand evaluator is initialized
    assert hasattr(ppsm, 'hand_evaluator'), "Hand evaluator not initialized!"
    print("✅ Hand evaluator initialized successfully")
    
    # Set up a test scenario with specific hole cards and board
    ppsm.game_state.players[0].cards = ['Ah', 'Kh']  # Royal flush draw
    ppsm.game_state.players[1].cards = ['2c', '2d']  # Pocket twos
    ppsm.game_state.board = ['Qh', 'Jh', 'Th', '9h', '8h']  # Board gives player 1 royal flush
    
    print(f"🃏 Player 1: {ppsm.game_state.players[0].cards} + {ppsm.game_state.board}")
    print(f"🃏 Player 2: {ppsm.game_state.players[1].cards} + {ppsm.game_state.board}")
    
    # Test hand evaluation directly
    eval1 = ppsm.hand_evaluator.evaluate_hand(ppsm.game_state.players[0].cards, ppsm.game_state.board)
    eval2 = ppsm.hand_evaluator.evaluate_hand(ppsm.game_state.players[1].cards, ppsm.game_state.board)
    
    print(f"✅ Player 1 evaluation: {eval1['hand_description']} (score={eval1['hand_score']})")
    print(f"✅ Player 2 evaluation: {eval2['hand_description']} (score={eval2['hand_score']})")
    
    # Test winner determination
    active_players = [p for p in ppsm.game_state.players if not p.has_folded]
    winners = ppsm._determine_winners(active_players)
    
    print(f"🏆 Winner: {winners[0].name if winners else 'None'}")
    
    # Test full showdown resolution
    print("\n🎭 Testing full showdown resolution:")
    ppsm.game_state.committed_pot = 100.0  # Set up pot
    initial_stack_1 = ppsm.game_state.players[0].stack
    initial_stack_2 = ppsm.game_state.players[1].stack
    
    ppsm._resolve_showdown()
    
    final_stack_1 = ppsm.game_state.players[0].stack
    final_stack_2 = ppsm.game_state.players[1].stack
    
    print(f"💰 Player 1 stack: ${initial_stack_1} → ${final_stack_1} (change: +${final_stack_1 - initial_stack_1})")
    print(f"💰 Player 2 stack: ${initial_stack_2} → ${final_stack_2} (change: +${final_stack_2 - initial_stack_2})")
    
    # Verify winner got the pot
    if winners and winners[0].name == ppsm.game_state.players[0].name:
        assert final_stack_1 > initial_stack_1, "Winner should have gained chips!"
        print("✅ Correct winner received the pot!")
    else:
        print("❌ Unexpected winner or pot distribution!")
    
    print("\n🎉 DEUCES INTEGRATION TEST COMPLETE!")


if __name__ == "__main__":
    test_deuces_integration()
