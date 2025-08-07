#!/usr/bin/env python3
"""
Corrected BB facing raise test.
"""

from backend.shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType
from backend.gui_models import StrategyData

def test_bb_facing_raise():
    """Test BB folds to a raise with a weak hand."""
    # Create state machine
    strategy_data = StrategyData()
    state_machine = ImprovedPokerStateMachine(strategy_data=strategy_data)
    
    # Start hand
    state_machine.start_hand()
    
    # Set up logging
    actions_taken = []
    state_machine.on_log_entry = lambda msg: actions_taken.append(msg)
    
    # Find BB player and set weak hand
    bb_player = next(p for p in state_machine.game_state.players if p.position == "BB")
    bb_player.cards = ["7h", "2c"]  # Weak hand
    print(f"BB player: {bb_player.name} ({bb_player.position})")
    print(f"BB cards: {bb_player.cards}")
    
    # Find UTG player
    utg_player = next(p for p in state_machine.game_state.players if p.position == "UTG")
    print(f"UTG player: {utg_player.name} ({utg_player.position})")
    
    # Wait for UTG to be the action player, then raise
    while state_machine.get_action_player() != utg_player:
        current_player = state_machine.get_action_player()
        if current_player and current_player.position != "UTG":
            print(f"Folding {current_player.name} to get to UTG")
            state_machine.execute_action(current_player, ActionType.FOLD)
    
    # Now UTG should be the action player
    current_player = state_machine.get_action_player()
    print(f"UTG is now acting: {current_player.name}")
    
    # UTG raises
    print("UTG raising to $3.0")
    state_machine.execute_action(utg_player, ActionType.RAISE, 3.0)
    
    # Fold other players to get to BB
    players_folded = 0
    while players_folded < 4:  # Fold 4 players to get to BB
        current_player = state_machine.get_action_player()
        if current_player and current_player.position not in ["BB", "UTG"]:
            print(f"Folding {current_player.name} ({current_player.position})")
            state_machine.execute_action(current_player, ActionType.FOLD)
            players_folded += 1
        elif current_player and current_player.position == "BB":
            print(f"BB is now acting: {current_player.name}")
            break
        else:
            print(f"Current player: {current_player.name} ({current_player.position})")
            break
    
    # Now BB should be the action player
    current_player = state_machine.get_action_player()
    print(f"Final action player: {current_player.name} ({current_player.position})")
    
    if current_player and current_player.position == "BB":
        print("BB is acting...")
        state_machine.execute_bot_action(current_player)
        
        # Find BB action in logs
        bb_action = next((a for a in actions_taken if "BB" in a and "decided" in a), None)
        print(f"BB action found: {bb_action}")
        
        if bb_action and "FOLD" in bb_action:
            print("✅ BB correctly folded to raise!")
            return True
        else:
            print(f"❌ BB did not fold: {bb_action}")
            return False
    else:
        print(f"❌ BB is not the action player: {current_player}")
        return False

if __name__ == "__main__":
    success = test_bb_facing_raise()
    print(f"Test result: {'PASS' if success else 'FAIL'}") 