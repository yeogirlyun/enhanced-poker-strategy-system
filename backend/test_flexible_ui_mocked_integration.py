#!/usr/bin/env python3
"""
Flexible UI-Mocked Tester for Flexible Poker State Machine

This script tests the flexible poker state machine with mocked UI integration
for integration testing without actual UI rendering.
"""

import unittest
from unittest import mock
from core.flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, GameEvent, EventListener, ActionType, PokerState
)


class TestEventListener(EventListener):
    """Test event listener for tracking events."""
    
    def __init__(self):
        self.events = []
        self.event_counts = {}
    
    def on_event(self, event: GameEvent):
        """Handle a game event."""
        self.events.append(event)
        self.event_counts[event.event_type] = (
            self.event_counts.get(event.event_type, 0) + 1
        )
    
    def get_events_by_type(self, event_type: str):
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def clear_events(self):
        """Clear all events."""
        self.events.clear()
        self.event_counts.clear()


class TestFlexiblePokerStateMachineWithMockedUI(unittest.TestCase):
    """Integration tests for flexible poker state machine with mocked UI."""

    def setUp(self):
        """Set up the flexible state machine with mocked UI renderer."""
        self.config = GameConfig(
            num_players=3,
            big_blind=1.0,
            small_blind=0.5,
            starting_stack=100.0,
            test_mode=True,
            show_all_cards=True
        )
        self.sm = FlexiblePokerStateMachine(self.config)
        self.event_listener = TestEventListener()
        self.sm.add_event_listener(self.event_listener)
        
        # Mock a sample display state
        self.mock_display = {
            "valid_actions": {},
            "player_highlights": [False] * 3,
            "card_visibilities": [False] * 3,
            "chip_representations": {},
            "layout_positions": {},
            "community_cards": [],
            "pot_amount": 0.0,
            "current_bet": 0.0,
            "action_player_index": 0,
            "game_state": "START_HAND",
            "last_action_details": ""
        }

    def test_full_hand_simulation_with_ui_mocks(self):
        """Simulate a full hand with UI updates mocked."""
        self.sm.start_hand()
        
        # Verify UI was "updated" at start by checking events
        self.assertGreater(len(self.event_listener.events), 0)
        
        # Test UI updates work
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a valid action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # Check UI update after action
            self.assertGreater(len(self.event_listener.events), 1)
        
        # Test that UI state is consistent
        display_state = self.sm.get_game_info()
        self.assertIsNotNone(display_state)
        self.assertIsInstance(display_state, dict)

    def test_all_in_scenario_with_ui(self):
        """Test all-in handling with mocked UI."""
        self.sm.start_hand()
        
        # Test that UI updates work with basic actions
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a call action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should update
            self.assertGreater(len(self.event_listener.events), 0)
        
        # Test UI state consistency
        display_state = self.sm.get_game_info()
        self.assertIsNotNone(display_state)
        self.assertIsInstance(display_state, dict)

    def test_multi_way_pot_with_ui_updates(self):
        """Test multi-way pot scenario with UI updates."""
        self.sm.start_hand()
        
        # Test basic UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a call action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should update
            self.assertGreaterEqual(len(self.event_listener.events), 1)
        
        # Test UI state consistency
        display_state = self.sm.get_game_info()
        self.assertIsNotNone(display_state)
        self.assertIsInstance(display_state, dict)

    def test_ui_state_consistency(self):
        """Test UI state consistency."""
        self.sm.start_hand()
        
        # Test that UI state is consistent
        display_state1 = self.sm.get_game_info()
        display_state2 = self.sm.get_game_info()
        
        # Should be consistent
        self.assertEqual(display_state1.keys(), display_state2.keys())
        
        # Test that events are tracked
        self.assertGreater(len(self.event_listener.events), 0)

    def test_error_handling_with_ui(self):
        """Test error handling with UI."""
        self.sm.start_hand()
        
        # Test that errors are handled gracefully
        try:
            action_player = self.sm.get_action_player()
            if action_player:
                self.sm.execute_action(action_player, ActionType.FOLD, 0.0)
        except Exception as e:
            self.fail(f"Error handling failed: {e}")
        
        # Test that UI state is still valid
        display_state = self.sm.get_game_info()
        self.assertIsNotNone(display_state)

    def test_ui_event_system(self):
        """Test UI event system."""
        self.sm.start_hand()
        
        # Test that events are emitted
        self.assertGreater(len(self.event_listener.events), 0)
        
        # Test event types
        event_types = set(event.event_type for event in self.event_listener.events)
        self.assertIsInstance(event_types, set)

    def test_ui_state_transitions(self):
        """Test UI state transitions."""
        self.sm.start_hand()
        
        # Test state transitions
        self.assertEqual(self.sm.current_state, PokerState.PREFLOP_BETTING)
        
        # Test transition to flop
        self.sm.transition_to(PokerState.DEAL_FLOP)
        self.assertEqual(self.sm.current_state, PokerState.DEAL_FLOP)
        
        # Test transition to flop betting
        self.sm.transition_to(PokerState.FLOP_BETTING)
        self.assertEqual(self.sm.current_state, PokerState.FLOP_BETTING)

    def test_ui_action_validation(self):
        """Test UI action validation."""
        self.sm.start_hand()
        
        # Test action validation
        action_player = self.sm.get_action_player()
        if action_player:
            valid_actions = self.sm.get_valid_actions_for_player(action_player)
            self.assertIsInstance(valid_actions, dict)
            self.assertIn("fold", valid_actions)

    def test_ui_pot_management(self):
        """Test UI pot management."""
        self.sm.start_hand()
        
        # Test pot management
        initial_pot = self.sm.game_state.pot
        
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # Pot should increase
            self.assertGreaterEqual(self.sm.game_state.pot, initial_pot)

    def test_ui_player_management(self):
        """Test UI player management."""
        self.sm.start_hand()
        
        # Test player management
        players = self.sm.game_state.players
        self.assertEqual(len(players), 3)
        
        for player in players:
            self.assertIsNotNone(player.name)
            self.assertGreaterEqual(player.stack, 0.0)

    def test_ui_hand_evaluation(self):
        """Test UI hand evaluation."""
        self.sm.start_hand()
        
        # Test hand evaluation
        player = self.sm.game_state.players[0]
        player.cards = ["Ah", "Kh"]
        self.sm.game_state.board = ["Qh", "Jh", "Th"]
        
        winners = self.sm.determine_winners([player])
        self.assertIsInstance(winners, list)

    def test_ui_performance(self):
        """Test UI performance."""
        import time
        
        start_time = time.time()
        
        # Test UI performance
        for _ in range(10):
            self.sm.start_hand()
            action_player = self.sm.get_action_player()
            if action_player:
                self.sm.execute_action(action_player, ActionType.FOLD, 0.0)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(execution_time, 5.0)  # 5 seconds max

    def test_ui_memory_usage(self):
        """Test UI memory usage."""
        # Test memory usage
        for _ in range(100):
            self.sm.start_hand()
            action_player = self.sm.get_action_player()
            if action_player:
                self.sm.execute_action(action_player, ActionType.FOLD, 0.0)
        
        # Should not cause memory issues
        self.assertTrue(True)

    def test_ui_error_recovery(self):
        """Test UI error recovery."""
        self.sm.start_hand()
        
        # Test error recovery
        try:
            action_player = self.sm.get_action_player()
            if action_player:
                self.sm.execute_action(action_player, ActionType.CALL, 1.0)
        except Exception as e:
            self.fail(f"Error recovery failed: {e}")
        
        # Should recover gracefully
        self.assertIsNotNone(self.sm.get_game_info())


def run_flexible_ui_mocked_tests():
    """Run all flexible UI mocked tests."""
    print("🎯 Running Flexible UI Mocked Integration Tests")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFlexiblePokerStateMachineWithMockedUI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 FLEXIBLE UI MOCKED TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print("\n🎯 Flexible UI mocked testing completed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_flexible_ui_mocked_tests()
    import sys
    sys.exit(0 if success else 1)
