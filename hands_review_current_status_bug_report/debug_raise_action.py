#!/usr/bin/env python3
"""
Debug script to test RAISE action processing in the poker state machine.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def debug_raise_action():
    """Debug the RAISE action processing."""
    print("🧪 DEBUGGING RAISE ACTION PROCESSING")
    print("=" * 60)
    
    try:
        from core.bot_session_state_machine import HandsReviewBotSession
        from core.flexible_poker_state_machine import GameConfig
        from core.hand_model import Hand
        
        # Load the first legendary hand (BB001)
        hand_file = "data/legendary_hands.json"
        with open(hand_file, 'r') as f:
            import json
            data = json.load(f)
            hand_data = data['hands'][0]  # BB001 hand
        
        print(f"📊 Loaded hand: {hand_data['metadata']['hand_id']}")
        print(f"📊 Blind amounts: SB=${hand_data['metadata']['small_blind']}, BB=${hand_data['metadata']['big_blind']}")
        
        # Create Hand Model
        hand_model = Hand.from_dict(hand_data)
        
        # Create session
        config = GameConfig(num_players=2, small_blind=1, big_blind=2, starting_stack=1000)
        session = HandsReviewBotSession(config)
        
        # Set up hand
        session.preloaded_hand_data = {'hand_model': hand_model}
        session.start_session()
        
        print(f"\n🎯 INITIAL GAME STATE:")
        print(f"   • Pot: ${session.game_state.pot}")
        print(f"   • Current bet: ${session.game_state.current_bet}")
        print(f"   • Players:")
        for i, player in enumerate(session.game_state.players):
            print(f"     - {player.name}: bet=${player.current_bet}, stack=${player.stack}")
        
        # Execute first action (should be RAISE to $30)
        print(f"\n🎯 EXECUTING FIRST ACTION (RAISE to $30)...")
        
        # Get the decision first
        decision = session.decision_engine.get_decision(0, session.game_state)
        print(f"   • Decision: {decision}")
        
        # Execute the action manually to see what happens
        action_type = decision['action']
        amount = decision['amount']
        player_index = 0
        
        print(f"\n🎯 MANUAL ACTION EXECUTION:")
        print(f"   • Action: {action_type}")
        print(f"   • Amount: ${amount}")
        print(f"   • Player: {session.game_state.players[player_index].name}")
        
        # Execute the action using the session's execute_action method
        if action_type.value == 'RAISE':
            print(f"   • Executing RAISE to ${amount}")
            
            # Get current player
            player = session.game_state.players[player_index]
            current_bet = player.current_bet
            call_amount = session.game_state.current_bet - current_bet
            
            print(f"   • Player current bet: ${current_bet}")
            print(f"   • Call amount needed: ${call_amount}")
            print(f"   • Total needed: ${call_amount + amount}")
            
            # Use the session's execute_action method instead of manual updates
            try:
                # Execute the action through the session using correct signature
                success = session.execute_action(player, action_type, amount)
                print(f"   • Action execution result: {success}")
                
                print(f"   • After RAISE:")
                print(f"     - Player bet: ${player.current_bet}")
                print(f"     - Player stack: ${player.stack}")
                print(f"     - Pot: ${session.game_state.pot}")
                print(f"     - Current bet: ${session.game_state.current_bet}")
                
            except Exception as e:
                print(f"   ❌ Error executing action: {e}")
                # Fall back to manual execution for debugging
                player.current_bet = session.game_state.current_bet + amount
                player.stack -= (call_amount + amount)
                session.game_state.pot += (call_amount + amount)
                session.game_state.current_bet = player.current_bet
                print(f"   • Manual fallback executed")
        
        # Check if the action was successful by looking at game state
        print(f"   • Game state after action:")
        print(f"     - Pot: ${session.game_state.pot}")
        print(f"     - Current bet: ${session.game_state.current_bet}")
        print(f"     - Player1 bet: ${session.game_state.players[0].current_bet}")
        print(f"     - Player2 bet: ${session.game_state.players[1].current_bet}")
        
        # Try to execute second action (should be CALL $30)
        print(f"\n🎯 TESTING SECOND ACTION (CALL $30)...")
        decision2 = session.decision_engine.get_decision(1, session.game_state)
        print(f"   • Decision: {decision2}")
        
        # Check if CALL is now valid by looking at the game state
        print(f"   • Game state for player 2:")
        print(f"     - Current bet: ${session.game_state.current_bet}")
        print(f"     - Player2 current bet: ${session.game_state.players[1].current_bet}")
        print(f"     - Call amount needed: ${session.game_state.current_bet - session.game_state.players[1].current_bet}")
        
        # Try to execute the CALL action
        if decision2['action'].value == 'CALL':
            print(f"   • Attempting to execute CALL action...")
            try:
                player2 = session.game_state.players[1]
                call_amount = decision2['amount']
                success = session.execute_action(player2, decision2['action'], call_amount)
                print(f"   • CALL action result: {success}")
                
                if success:
                    print(f"   ✅ CALL action executed successfully!")
                    print(f"   • Final game state:")
                    print(f"     - Pot: ${session.game_state.pot}")
                    print(f"     - Current bet: ${session.game_state.current_bet}")
                    print(f"     - Player1 bet: ${session.game_state.players[0].current_bet}")
                    print(f"     - Player2 bet: ${session.game_state.players[1].current_bet}")
                else:
                    print(f"   ❌ CALL action failed")
            except Exception as e:
                print(f"   ❌ Error executing CALL action: {e}")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_raise_action()
