#!/usr/bin/env python3
"""
Test script for the new snapshot system in FlexiblePokerStateMachine.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig


def test_hands_review_snapshot_restore():
    """Test the new snapshot system."""
    print("🧪 Testing Hands Review Snapshot System...")
    
    # Create state machine in review mode
    config = GameConfig(num_players=6, starting_stack=1000.0)
    fpsm = FlexiblePokerStateMachine(config, mode="review")
    
    print(f"✅ FPSM created in {fpsm.mode} mode")
    
    # Test snapshot 1: Preflop
    flop_snap = {
        "board": ["7c", "8h", "Kh"],
        "pot": 12.5,
        "current_bet": 4.0,
        "street": "flop",
        "dealer_index": 2,
        "action_player_index": 4,
        "players": [
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["6c", "Js"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["Kd", "6s"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["3h", "Qc"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["7c", "6d"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["Qh", "As"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["2h", "Td"]}
        ]
    }
    
    print("🔄 Restoring flop snapshot...")
    fpsm.restore_snapshot(flop_snap)
    
    # Assertions reflect the restored state
    assert fpsm.game_state.board == flop_snap["board"], f"Board mismatch: {fpsm.game_state.board} != {flop_snap['board']}"
    assert abs(fpsm.game_state.pot - flop_snap["pot"]) < 1e-9, f"Pot mismatch: {fpsm.game_state.pot} != {flop_snap['pot']}"
    assert fpsm.game_state.street == flop_snap["street"], f"Street mismatch: {fpsm.game_state.street} != {flop_snap['street']}"
    
    print(f"✅ Flop snapshot restored successfully:")
    print(f"   Board: {fpsm.game_state.board}")
    print(f"   Pot: {fpsm.game_state.pot}")
    print(f"   Street: {fpsm.game_state.street}")
    
    # Test snapshot 2: River (later state)
    river_snap = {
        "board": ["7c", "8h", "Kh", "9c", "Qc"],
        "pot": 42.5,
        "current_bet": 0.0,
        "street": "river",
        "dealer_index": 2,
        "action_player_index": 4,
        "players": [
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["6c", "Js"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["Kd", "6s"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["3h", "Qc"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["7c", "6d"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["Qh", "As"]},
            {"stack": 950.0, "current_bet": 0.0, "has_folded": False, "cards": ["2h", "Td"]}
        ]
    }
    
    print("🔄 Restoring river snapshot...")
    fpsm.restore_snapshot(river_snap)
    
    # Assertions reflect the restored state
    assert fpsm.game_state.board == river_snap["board"], f"Board mismatch: {fpsm.game_state.board} != {river_snap['board']}"
    assert abs(fpsm.game_state.pot - river_snap["pot"]) < 1e-9, f"Pot mismatch: {fpsm.game_state.pot} != {river_snap['pot']}"
    assert fpsm.game_state.street == river_snap["street"], f"Street mismatch: {fpsm.game_state.street} != {river_snap['street']}"
    assert fpsm.game_state.board[-1] == "Qc", f"Last card mismatch: {fpsm.game_state.board[-1]} != Qc"
    
    print(f"✅ River snapshot restored successfully:")
    print(f"   Board: {fpsm.game_state.board}")
    print(f"   Pot: {fpsm.game_state.pot}")
    print(f"   Street: {fpsm.game_state.street}")
    print(f"   Last card: {fpsm.game_state.board[-1]}")
    
    # Test mode switching
    print("🔄 Testing mode switching...")
    fpsm.set_mode("live")
    assert fpsm.mode == "live", f"Mode switch failed: {fpsm.mode} != live"
    
    fpsm.set_mode("review")
    assert fpsm.mode == "review", f"Mode switch failed: {fpsm.mode} != review"
    
    print("✅ Mode switching works correctly")
    
    # Test that start_hand is ignored in review mode
    print("🔄 Testing start_hand in review mode...")
    original_board = list(fpsm.game_state.board)
    original_pot = fpsm.game_state.pot
    
    fpsm.start_hand()  # This should be ignored in review mode
    
    assert fpsm.game_state.board == original_board, "Board should not change in review mode"
    assert fpsm.game_state.pot == original_pot, "Pot should not change in review mode"
    
    print("✅ start_hand correctly ignored in review mode")
    
    print("🎉 All snapshot system tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_hands_review_snapshot_restore()
        print("✅ Snapshot system is working correctly!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
