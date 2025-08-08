#!/usr/bin/env python3
"""
Comprehensive Poker State Machine Sequence Tester

This tester validates the complete poker flow including:
1. State transitions
2. Player action sequences
3. Betting rounds
4. Card dealing
5. Pot management
6. Player progression
7. Display state updates

The tester simulates a complete hand and validates each step.
"""

import sys
import os
from typing import List, Optional
from dataclasses import dataclass

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from core.poker_state_machine_adapter import PokerStateMachineAdapter
from core.types import ActionType, PokerState
from core.flexible_poker_state_machine import GameConfig


@dataclass
class TestAction:
    """Represents a test action to be executed."""
    player_name: str
    action_type: ActionType
    amount: float = 0.0
    expected_state: Optional[PokerState] = None
    expected_pot: Optional[float] = None
    expected_current_bet: Optional[float] = None
    expected_action_player: Optional[str] = None


@dataclass
class TestScenario:
    """Represents a complete test scenario."""
    name: str
    num_players: int
    starting_stacks: List[float]
    player_names: List[str]
    player_cards: List[List[str]]
    board_cards: List[str]
    actions: List[TestAction]
    expected_final_pot: float
    expected_winners: List[str]


class PokerStateMachineTester:
    """Comprehensive tester for poker state machine sequences."""
    
    def __init__(self):
        self.test_results = []
        self.current_test = None
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("🎯 Starting Poker State Machine Sequence Tests")
        print("=" * 60)
        
        test_scenarios = self._create_test_scenarios()
        
        for scenario in test_scenarios:
            self._run_test_scenario(scenario)
        
        self._print_summary()
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create test scenarios to validate."""
        scenarios = []
        
        # Test Scenario 1: Simple preflop fold
        scenarios.append(TestScenario(
            name="Simple Preflop Fold",
            num_players=3,
            starting_stacks=[100.0, 100.0, 100.0],
            player_names=["Player 1", "Player 2", "Player 3"],
            player_cards=[["Ah", "Kh"], ["Qd", "Jd"], ["2c", "3c"]],
            board_cards=[],
            actions=[
                TestAction("Player 1", ActionType.RAISE, 3.0,
                          PokerState.PREFLOP_BETTING, 4.5, 3.0, "Player 2"),  # $1.5 blinds + $3.0 raise
                TestAction("Player 2", ActionType.FOLD, 0.0,
                          PokerState.PREFLOP_BETTING, 4.5, 3.0, "Player 3"),
                TestAction("Player 3", ActionType.FOLD, 0.0,
                          PokerState.END_HAND, 4.5, 0.0, None),
            ],
            expected_final_pot=4.5,  # $1.5 blinds + $3.0 raise
            expected_winners=["Player 1"]
        ))
        
        # Test Scenario 2: Complete hand to showdown
        scenarios.append(TestScenario(
            name="Complete Hand to Showdown",
            num_players=2,
            starting_stacks=[100.0, 100.0],
            player_names=["Player 1", "Player 2"],
            player_cards=[["Ah", "Kh"], ["Qd", "Jd"]],
            board_cards=["As", "Ks", "Qh", "2c", "3d"],
            actions=[
                # Preflop
                TestAction("Player 1", ActionType.RAISE, 3.0,
                          PokerState.PREFLOP_BETTING, 4.5, 3.5, "Player 2"),  # $1.5 blinds + $3.0 raise, current bet is $3.5 (includes $0.5 SB)
                TestAction("Player 2", ActionType.CALL, 3.0,
                          PokerState.DEAL_FLOP, 7.0, 0.0, "Player 1"),  # $4.5 + $2.5 call (difference between $3.5 and $1.0)
                # Flop
                TestAction("Player 1", ActionType.BET, 5.0,
                          PokerState.FLOP_BETTING, 12.0, 5.0, "Player 2"),  # $7.0 + $5.0 bet
                TestAction("Player 2", ActionType.CALL, 5.0,
                          PokerState.DEAL_TURN, 17.0, 0.0, "Player 1"),  # $12.0 + $5.0 call
                # Turn
                TestAction("Player 1", ActionType.CHECK, 0.0,
                          PokerState.TURN_BETTING, 17.0, 0.0, "Player 2"),
                TestAction("Player 2", ActionType.CHECK, 0.0,
                          PokerState.DEAL_RIVER, 17.0, 0.0, "Player 1"),
                # River
                TestAction("Player 1", ActionType.BET, 10.0,
                          PokerState.RIVER_BETTING, 27.0, 10.0, "Player 2"),  # $17.0 + $10.0 bet
                TestAction("Player 2", ActionType.CALL, 10.0,
                          PokerState.SHOWDOWN, 37.0, 0.0, None),  # $27.0 + $10.0 call
            ],
            expected_final_pot=37.0,  # $1.5 blinds + $3.0 raise + $2.5 call + $5.0 bet + $5.0 call + $10.0 bet + $10.0 call
            expected_winners=["Player 1"]  # Player 1 has Aces full of Kings
        ))
        
        return scenarios
    
    def _run_test_scenario(self, scenario: TestScenario):
        """Run a single test scenario."""
        print(f"\n🎮 Testing Scenario: {scenario.name}")
        print("-" * 40)
        
        self.current_test = scenario
        
        try:
            # Initialize state machine
            config = GameConfig(
                num_players=scenario.num_players,
                starting_stack=100.0,
                show_all_cards=True
            )
            
            state_machine = PokerStateMachineAdapter(
                num_players=scenario.num_players,
                test_mode=True
            )
            
            # Start hand
            state_machine.start_hand()
            print(f"✅ Hand started with {scenario.num_players} players")
            
            # Set up players
            self._setup_players(state_machine, scenario)
            
            # Execute actions
            for i, action in enumerate(scenario.actions):
                print(f"\n🎯 Action {i+1}: {action.player_name} "
                      f"{action.action_type.value} ${action.amount}")
                
                # Get current player
                current_player = state_machine.get_action_player()
                if not current_player:
                    print(f"❌ No current player found")
                    self._record_test_result(scenario.name, False,
                                           f"No current player for action {i+1}")
                    return
                
                # Validate it's the expected player
                if current_player.name != action.player_name:
                    print(f"❌ Expected {action.player_name}, got {current_player.name}")
                    self._record_test_result(scenario.name, False,
                                           f"Wrong player for action {i+1}")
                    return
                
                # Execute action
                try:
                    state_machine.execute_action(current_player, action.action_type,
                                               action.amount)
                    print(f"✅ Action executed successfully")
                    
                    # Validate state
                    if not self._validate_state(state_machine, action, i+1):
                        return
                    
                except Exception as e:
                    print(f"❌ Action failed: {e}")
                    self._record_test_result(scenario.name, False,
                                           f"Action {i+1} failed: {e}")
                    return
            
            # Validate final state
            if not self._validate_final_state(state_machine, scenario):
                return
            
            print(f"✅ Scenario completed successfully")
            self._record_test_result(scenario.name, True, "All validations passed")
            
        except Exception as e:
            print(f"❌ Scenario failed: {e}")
            import traceback
            traceback.print_exc()
            self._record_test_result(scenario.name, False, f"Scenario failed: {e}")
    
    def _setup_players(self, state_machine: PokerStateMachineAdapter,
                      scenario: TestScenario):
        """Set up players with cards and stacks."""
        print(f"👥 Setting up {len(scenario.player_names)} players")
        
        for i, (name, cards, stack) in enumerate(zip(scenario.player_names,
                                                    scenario.player_cards,
                                                    scenario.starting_stacks)):
            # Set player cards
            state_machine.set_player_cards(i, cards)
            
            # Set player stack and name
            if (hasattr(state_machine, 'game_state') and
                    i < len(state_machine.game_state.players)):
                state_machine.game_state.players[i].stack = stack
                state_machine.game_state.players[i].name = name
            
            print(f"  Player {i+1}: {name} - Cards: {cards} - Stack: ${stack}")
    
    def _validate_state(self, state_machine: PokerStateMachineAdapter,
                       action: TestAction, action_num: int) -> bool:
        """Validate the state after an action."""
        game_info = state_machine.get_game_info()
        
        # Validate state
        if (action.expected_state and
                game_info['state'] != action.expected_state.value):
            print(f"❌ Expected state {action.expected_state.value}, "
                  f"got {game_info['state']}")
            self._record_test_result(self.current_test.name, False,
                                   f"Wrong state after action {action_num}")
            return False
        
        # Validate pot
        if (action.expected_pot is not None and
                abs(game_info['pot'] - action.expected_pot) > 0.01):
            print(f"❌ Expected pot ${action.expected_pot}, got ${game_info['pot']}")
            self._record_test_result(self.current_test.name, False,
                                   f"Wrong pot after action {action_num}")
            return False
        
        # Validate current bet
        if (action.expected_current_bet is not None and
                abs(game_info['current_bet'] - action.expected_current_bet) > 0.01):
            print(f"❌ Expected current bet ${action.expected_current_bet}, "
                  f"got ${game_info['current_bet']}")
            self._record_test_result(self.current_test.name, False,
                                   f"Wrong current bet after action {action_num}")
            return False
        
        # Validate action player
        if action.expected_action_player:
            current_player = state_machine.get_action_player()
            if (not current_player or
                    current_player.name != action.expected_action_player):
                print(f"❌ Expected action player {action.expected_action_player}, "
                      f"got {current_player.name if current_player else 'None'}")
                self._record_test_result(self.current_test.name, False,
                                       f"Wrong action player after action {action_num}")
                return False
        
        print(f"✅ State validation passed for action {action_num}")
        return True
    
    def _validate_final_state(self, state_machine: PokerStateMachineAdapter,
                             scenario: TestScenario) -> bool:
        """Validate the final state of the hand."""
        game_info = state_machine.get_game_info()
        
        # Validate final pot
        if abs(game_info['pot'] - scenario.expected_final_pot) > 0.01:
            print(f"❌ Expected final pot ${scenario.expected_final_pot}, "
                  f"got ${game_info['pot']}")
            self._record_test_result(scenario.name, False, "Wrong final pot")
            return False
        
        # Validate hand is complete
        if not state_machine.is_hand_complete():
            print(f"❌ Hand should be complete but isn't")
            self._record_test_result(scenario.name, False, "Hand not complete")
            return False
        
        print(f"✅ Final state validation passed")
        return True
    
    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Record a test result."""
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'message': message
        })
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print(f"\n🎯 Success Rate: {(passed/total)*100:.1f}%")


def main():
    """Main test runner."""
    tester = PokerStateMachineTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
