#!/usr/bin/env python3
"""
Corrected BB test that ensures BB gets to act.
"""

from backend.shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType
from backend.gui_models import StrategyData

def test_bb_checking():
    """Test BB checks with weak hand when no raise is made."""
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
    
    # Have some players call to create a scenario where BB gets to act
    players_acted = 0
    while players_acted < 4:  # Have 4 players act
        current_player = state_machine.get_action_player()
        if current_player and current_player.position != "BB":
            print(f"Player {current_player.name} ({current_player.position}) acting...")
            if current_player.position in ["UTG", "MP"]:
                # These players fold
                print(f"  Folding {current_player.name}")
                state_machine.execute_action(current_player, ActionType.FOLD)
            else:
                # Other players call to keep the hand going
                print(f"  Calling with {current_player.name}")
                state_machine.execute_action(current_player, ActionType.CALL)
            players_acted += 1
        else:
            print(f"Current player is BB: {current_player.name}")
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
        
        if bb_action and "CHECK" in bb_action:
            print("✅ BB correctly checked!")
            return True
        else:
            print(f"❌ BB did not check: {bb_action}")
            return False
    else:
        print(f"❌ BB is not the action player: {current_player}")
        return False

if __name__ == "__main__":
    success = test_bb_checking()
    print(f"Test result: {'PASS' if success else 'FAIL'}") 