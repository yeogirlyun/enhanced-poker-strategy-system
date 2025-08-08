#!/usr/bin/env python3
"""
Test Simulation/Hand Review Session

This file tests the simulation functionality of the redesigned hands review panel
by mocking the exact same environment as the GUI but without launching the full UI.

This ensures that all simulation features work correctly before they're used in the GUI.
"""

import unittest
import sys
import os
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, patch
from io import StringIO

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hands_database import ParsedHand, HandMetadata, HandCategory
from core.poker_state_machine import ActionType
from ui.components.redesigned_hands_review_panel import RedesignedHandsReviewPanel


class MockTkinter:
    """Mock Tkinter components for testing."""
    
    def __init__(self):
        # Create a real Tkinter root for testing
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        
        # Create real frames
        self.frame = ttk.Frame(self.root)
        self.label = ttk.Label(self.frame)
        self.button = ttk.Button(self.frame)
        self.listbox = tk.Listbox(self.frame)
        self.text = tk.Text(self.frame)
        self.notebook = ttk.Notebook(self.frame)
        self.paned = ttk.PanedWindow(self.frame)
        
        # Mock some methods that we don't want to actually execute
        self.frame.pack = Mock()
        self.frame.pack_forget = Mock()
        self.frame.pack.return_value = None
        self.frame.pack_forget.return_value = None
        
        # Mock configure methods
        self.button.configure = Mock()
        self.label.configure = Mock()
        
        # Mock listbox methods
        self.listbox.get = Mock(return_value="Test Hand")
        self.listbox.curselection = Mock(return_value=(0,))
        
        # Mock text methods
        self.text.insert = Mock()
        self.text.delete = Mock()
        
        # Mock notebook methods
        self.notebook.select = Mock()
        
        # Mock paned methods
        self.paned.add = Mock()


class TestSimulationHandsReview(unittest.TestCase):
    """Test suite for simulation/hand review functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock tkinter environment
        self.mock_tk = MockTkinter()
        
        # Create mock hands database
        self.hands_database = Mock()
        
        # Create sample legendary hand
        self.sample_hand = self._create_sample_legendary_hand()
        
        # Mock the hands database to return our sample hand
        self.hands_database.load_all_hands.return_value = {
            HandCategory.LEGENDARY: [self.sample_hand],
            HandCategory.PRACTICE: [],
            HandCategory.TAGGED: []
        }
        
        # Create mock practice session
        self.mock_practice_session = Mock()
        self.mock_practice_session.refresh_display = Mock()
        self.mock_practice_session.destroy = Mock()
        self.mock_practice_session.pack = Mock()
        
        # Create mock poker state machine
        self.mock_state_machine = Mock()
        self.mock_state_machine.start_hand = Mock()
        self.mock_state_machine.get_action_player = Mock()
        self.mock_state_machine.execute_action = Mock()
        self.mock_state_machine.state = "preflop"
        
        # Mock current player
        self.mock_player = Mock()
        self.mock_player.name = "Chris Moneymaker"
        self.mock_state_machine.get_action_player.return_value = self.mock_player
    
    def _create_sample_legendary_hand(self):
        """Create a sample legendary hand for testing."""
        metadata = HandMetadata(
            id="test_hand_1",
            name="Moneymaker vs Farha 2003",
            category=HandCategory.LEGENDARY,
            subcategory="Epic Bluffs",
            source_file="data/legendary_hands.phh",
            event="WSOP Main Event 2003",
            players_involved=["Chris Moneymaker", "Sammy Farha"],
            pot_size=7000000.0,
            description="The famous bluff that won Moneymaker the Main Event"
        )
        
        return ParsedHand(
            metadata=metadata,
            game_info={
                "variant": "No-Limit Hold'em",
                "stakes": "20000/40000/0",
                "currency": "USD",
                "format": "Tournament",
                "event": "WSOP Main Event 2003 — Final Table"
            },
            players=[
                {
                    "name": "Chris Moneymaker",
                    "cards": ["5s", "4s"],
                    "position": "Button/SB",
                    "starting_stack_chips": 4700000
                },
                {
                    "name": "Sammy Farha", 
                    "cards": ["Kh", "Qd"],
                    "position": "Big Blind",
                    "starting_stack_chips": 2300000
                },
                {
                    "name": "Folded Player 1",
                    "cards": ["2c", "7h"],
                    "position": "UTG",
                    "starting_stack_chips": 100000,
                    "folded_preflop": True
                },
                {
                    "name": "Folded Player 2",
                    "cards": ["3d", "8s"],
                    "position": "MP", 
                    "starting_stack_chips": 100000,
                    "folded_preflop": True
                },
                {
                    "name": "Folded Player 3",
                    "cards": ["6h", "9c"],
                    "position": "CO",
                    "starting_stack_chips": 100000,
                    "folded_preflop": True
                },
                {
                    "name": "Folded Player 4",
                    "cards": ["Tc", "Jd"],
                    "position": "HJ",
                    "starting_stack_chips": 100000,
                    "folded_preflop": True
                }
            ],
            actions={
                "preflop": [
                    {"actor": 3, "type": "fold"},
                    {"actor": 4, "type": "fold"},
                    {"actor": 5, "type": "fold"},
                    {"actor": 6, "type": "fold"},
                    {"actor": 1, "type": "call", "amount": 20000},
                    {"actor": 2, "type": "check"}
                ],
                "flop": [
                    {"actor": 2, "type": "check"},
                    {"actor": 1, "type": "bet", "amount": 60000},
                    {"actor": 2, "type": "call", "amount": 60000}
                ],
                "turn": [
                    {"actor": 2, "type": "check"},
                    {"actor": 1, "type": "bet", "amount": 300000},
                    {"actor": 2, "type": "call", "amount": 300000}
                ],
                "river": [
                    {"actor": 2, "type": "check"},
                    {"actor": 1, "type": "all-in", "amount": 4280000},
                    {"actor": 2, "type": "call", "amount": 1900000}
                ]
            },
            board={
                "flop": ["Kc", "Ts", "6c"],
                "turn": "8h",
                "river": "8d"
            },
            result={
                "winners": [1],
                "winning_type": "showdown",
                "pot_total": 7000000
            },
            raw_data={}
        )
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_simulation_startup(self, mock_state_machine_class, mock_practice_session_class):
        """Test that simulation starts up correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel with mocked parent
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.hands_database = self.hands_database
        panel.current_hand = self.sample_hand
        
        # Mock the practice container
        panel.practice_container = self.mock_tk.frame
        
        # Test simulation startup
        panel.start_hand_simulation()
        
        # Verify state machine was created
        mock_state_machine_class.assert_called_once_with(num_players=6)
        
        # Verify practice session was created
        mock_practice_session_class.assert_called_once()
        
        # Verify hand setup was called
        self.mock_state_machine.start_hand.assert_called_once()
        
        print("✅ Simulation startup test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_legendary_hand_setup(self, mock_state_machine_class, mock_practice_session_class):
        """Test that legendary hand setup works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test legendary hand setup
        panel.setup_legendary_hand()
        
        # Verify hand was started
        self.mock_state_machine.start_hand.assert_called_once()
        
        # Verify practice session was updated
        self.mock_practice_session.refresh_display.assert_called()
        
        print("✅ Legendary hand setup test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_next_action_execution(self, mock_state_machine_class, mock_practice_session_class):
        """Test that next action execution works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test next action
        panel.next_action()
        
        # Verify action was executed
        self.mock_state_machine.execute_action.assert_called_once()
        
        # Verify practice session was refreshed
        self.mock_practice_session.refresh_display.assert_called()
        
        print("✅ Next action execution test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_simulation_completion(self, mock_state_machine_class, mock_practice_session_class):
        """Test that simulation handles completion correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Set state to game over
        self.mock_state_machine.state = "game_over"
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test next action when game is over
        panel.next_action()
        
        # Verify no action was executed (game is over)
        self.mock_state_machine.execute_action.assert_not_called()
        
        print("✅ Simulation completion test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_player_action_logic(self, mock_state_machine_class, mock_practice_session_class):
        """Test that player action logic works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test with main player (should call)
        self.mock_player.name = "Chris Moneymaker"
        panel.next_action()
        
        # Verify CALL action was executed
        call_args = self.mock_state_machine.execute_action.call_args
        self.assertEqual(call_args[0][1], ActionType.CALL)
        
        # Test with folded player (should fold)
        self.mock_player.name = "Folded Player 1"
        panel.next_action()
        
        # Verify FOLD action was executed
        fold_args = self.mock_state_machine.execute_action.call_args
        self.assertEqual(fold_args[0][1], ActionType.FOLD)
        
        print("✅ Player action logic test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_error_handling(self, mock_state_machine_class, mock_practice_session_class):
        """Test that error handling works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Make state machine raise an exception
        self.mock_state_machine.execute_action.side_effect = Exception("Test error")
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test error handling
        panel.next_action()
        
        # Verify error was handled gracefully (no exception raised)
        print("✅ Error handling test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_auto_play_functionality(self, mock_state_machine_class, mock_practice_session_class):
        """Test that auto play functionality works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        
        # Test auto play toggle
        panel.auto_play_active = False
        panel.toggle_auto_play()
        
        # Verify auto play was activated
        self.assertTrue(panel.auto_play_active)
        
        # Test auto play deactivation
        panel.toggle_auto_play()
        
        # Verify auto play was deactivated
        self.assertFalse(panel.auto_play_active)
        
        print("✅ Auto play functionality test passed!")
    
    @patch('ui.practice_session_ui.PracticeSessionUI')
    @patch('core.poker_state_machine.ImprovedPokerStateMachine')
    def test_simulation_reset(self, mock_state_machine_class, mock_practice_session_class):
        """Test that simulation reset works correctly."""
        # Setup mocks
        mock_state_machine_class.return_value = self.mock_state_machine
        mock_practice_session_class.return_value = self.mock_practice_session
        
        # Create the panel
        panel = RedesignedHandsReviewPanel(self.mock_tk.frame)
        panel.poker_state_machine = self.mock_state_machine
        panel.current_hand = self.sample_hand
        panel.practice_session = self.mock_practice_session
        panel.auto_play_active = True
        
        # Test simulation reset
        panel.reset_hand_simulation()
        
        # Verify practice session was destroyed
        self.mock_practice_session.destroy.assert_called_once()
        
        # Verify state was reset
        self.assertIsNone(panel.poker_state_machine)
        self.assertFalse(panel.auto_play_active)
        
        print("✅ Simulation reset test passed!")


def run_simulation_tests():
    """Run all simulation tests."""
    print("🧪 Starting Simulation/Hand Review Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulationHandsReview)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    print(f"📊 Test Results:")
    print(f"   - Tests run: {result.testsRun}")
    print(f"   - Failures: {len(result.failures)}")
    print(f"   - Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All simulation tests passed!")
        return True
    else:
        print("\n❌ Some simulation tests failed!")
        return False


if __name__ == "__main__":
    success = run_simulation_tests()
    sys.exit(0 if success else 1)
