#!/usr/bin/env python3
"""
Test PHH Session Integration

Tests the integration between practice session logging and PHH export
for hands review functionality.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from core.session_logger import SessionLogger, SessionLog, HandLog, ActionLog
from core.phh_converter import PHHConverter, PracticeHandsPHHManager
from core.session_manager import SessionManager


class TestPHHSessionIntegration(unittest.TestCase):
    """Test PHH session integration functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.test_logs_dir, exist_ok=True)
        
        # Initialize components
        self.phh_converter = PHHConverter()
        self.phh_manager = PracticeHandsPHHManager(
            os.path.join(self.temp_dir, "practice_hands")
        )

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_phh_converter_basic_functionality(self):
        """Test basic PHH converter functionality."""
        # Create a mock session with a simple hand
        session = SessionLog(
            session_id="test_session_123",
            start_time=1700000000.0,
            end_time=1700000300.0,
            num_players=6,
            starting_stack=100.0,
            human_player="Player 1",
            hands_played=1
        )
        
        # Create a simple completed hand
        hand = HandLog(
            hand_id="test_hand_1",
            session_id="test_session_123",
            timestamp=1700000100.0,
            hand_number=1,
            dealer_button=0,
            small_blind=1,
            big_blind=2,
            sb_amount=0.5,
            bb_amount=1.0,
            players=[
                {"name": "Player 1", "stack": 100.0, "position": 0},
                {"name": "Player 2", "stack": 100.0, "position": 1},
                {"name": "Player 3", "stack": 100.0, "position": 2},
                {"name": "Player 4", "stack": 100.0, "position": 3},
                {"name": "Player 5", "stack": 100.0, "position": 4},
                {"name": "Player 6", "stack": 100.0, "position": 5}
            ],
            hole_cards={
                "Player 1": ["As", "Kh"],
                "Player 2": ["Qd", "Jc"]
            },
            board_cards=["Ah", "Kd", "Qs", "Js", "Tc"],
            winner="Player 1",
            winning_hand="Straight",
            pot_size=15.0,
            hand_complete=True,
            hand_duration_ms=45000,
            streets_reached=["preflop", "flop", "turn", "river"]
        )
        
        # Add some actions
        hand.preflop_actions = [
            ActionLog(
                timestamp=1700000110.0,
                hand_id="test_hand_1",
                player_name="Player 3",
                player_index=2,
                action="FOLD",
                amount=0.0,
                stack_before=100.0,
                stack_after=100.0,
                pot_before=1.5,
                pot_after=1.5,
                current_bet=1.0,
                street="preflop",
                position="UTG",
                is_human=False
            ),
            ActionLog(
                timestamp=1700000115.0,
                hand_id="test_hand_1",
                player_name="Player 1",
                player_index=0,
                action="RAISE",
                amount=3.0,
                stack_before=100.0,
                stack_after=97.0,
                pot_before=1.5,
                pot_after=4.5,
                current_bet=3.0,
                street="preflop",
                position="BTN",
                is_human=True
            )
        ]
        
        session.hands = [hand]
        
        # Test PHH conversion
        phh_content = self.phh_converter.convert_hand_to_phh(hand, session)
        
        # Verify PHH content contains expected elements
        self.assertIn("variant = \"NLHE\"", phh_content)
        self.assertIn("blinds = [0.5, 1.0]", phh_content)
        self.assertIn("starting_stacks = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0]", phh_content)
        self.assertIn("actions = [", phh_content)
        self.assertIn("# Hand 1", phh_content)
        self.assertIn("# Winner: Player 1", phh_content)
        self.assertIn("# Pot: $15.00", phh_content)
        
        print("✅ PHH converter basic functionality test passed")

    def test_phh_export_workflow(self):
        """Test the complete PHH export workflow."""
        # Create a mock session
        session = SessionLog(
            session_id="test_workflow_456",
            start_time=1700001000.0,
            end_time=1700001600.0,
            num_players=6,
            starting_stack=100.0,
            human_player="Player 1",
            hands_played=2
        )
        
        # Add two completed hands
        for i in range(2):
            hand = HandLog(
                hand_id=f"test_hand_{i+1}",
                session_id="test_workflow_456",
                timestamp=1700001000.0 + (i * 300),
                hand_number=i + 1,
                dealer_button=i % 6,
                small_blind=(i + 1) % 6,
                big_blind=(i + 2) % 6,
                sb_amount=0.5,
                bb_amount=1.0,
                players=[
                    {"name": f"Player {j+1}", "stack": 100.0 - (i * 5), "position": j}
                    for j in range(6)
                ],
                hole_cards={
                    "Player 1": ["As", "Kh"],
                    "Player 2": ["Qd", "Jc"]
                },
                board_cards=["Ah", "Kd", "Qs"],
                winner=f"Player {(i % 2) + 1}",
                winning_hand="Pair",
                pot_size=10.0 + i * 5,
                hand_complete=True,
                hand_duration_ms=30000 + i * 5000,
                streets_reached=["preflop", "flop"]
            )
            session.hands.append(hand)
        
        # Test session export
        exported_files = self.phh_manager.export_session_hands(session)
        
        # Verify files were created
        self.assertTrue(len(exported_files) >= 1)
        
        # Check that PHH file exists and contains expected content
        phh_file = None
        for file_path in exported_files:
            if file_path.endswith('.phh'):
                phh_file = file_path
                break
        
        self.assertIsNotNone(phh_file)
        self.assertTrue(os.path.exists(phh_file))
        
        # Read and verify PHH content
        with open(phh_file, 'r') as f:
            phh_content = f.read()
        
        self.assertIn("Practice Session PHH File", phh_content)
        self.assertIn("Session ID: test_workflow_456", phh_content)
        self.assertIn("Hands Played: 2", phh_content)
        self.assertIn("# Hand 1", phh_content)
        self.assertIn("# Hand 2", phh_content)
        
        print("✅ PHH export workflow test passed")

    def test_practice_hands_manager_file_listing(self):
        """Test the practice hands manager file listing functionality."""
        # Create some mock PHH files
        practice_dir = Path(self.temp_dir) / "practice_hands"
        practice_dir.mkdir(exist_ok=True)
        
        # Create test PHH file
        test_phh_file = practice_dir / "practice_session_20231201_143000_abc12345.phh"
        with open(test_phh_file, 'w') as f:
            f.write("""# Practice Session PHH File
# Generated from Poker Trainer Practice Session
# Session ID: abc12345
# Start Time: 2023-12-01 14:30:00

variant = "NLHE"
ante = 0
blinds = [0.5, 1.0]
""")
        
        # Create corresponding metadata file
        metadata_file = practice_dir / "practice_metadata_20231201_143000_abc12345.json"
        metadata_content = {
            "session_info": {
                "session_id": "abc12345",
                "start_time": 1700000000.0,
                "hands_played": 1
            },
            "hands": [
                {
                    "id": "practice_abc12345_1",
                    "name": "Practice Hand 1",
                    "category": "Practice Hands",
                    "hand_number": 1,
                    "pot_size": 12.5,
                    "hand_complete": True
                }
            ]
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_content, f, indent=2)
        
        # Test file listing
        phh_manager = PracticeHandsPHHManager(str(practice_dir))
        files = phh_manager.get_practice_hands_files()
        
        self.assertEqual(len(files), 1)
        
        file_info = files[0]
        self.assertTrue(file_info["phh_file"].endswith("practice_session_20231201_143000_abc12345.phh"))
        self.assertTrue(file_info["metadata_file"].endswith("practice_metadata_20231201_143000_abc12345.json"))
        self.assertEqual(file_info["session_date"], "2023-12-01 14:30")
        
        print("✅ Practice hands manager file listing test passed")

    def test_session_manager_integration(self):
        """Test SessionManager integration with PHH export."""
        # Create a session manager with mock logger
        mock_logger = Mock()
        mock_session = SessionLog(
            session_id="integration_test_789",
            start_time=1700002000.0,
            num_players=6,
            starting_stack=100.0,
            hands_played=1
        )
        
        # Add a completed hand
        mock_hand = HandLog(
            hand_id="integration_hand_1",
            session_id="integration_test_789",
            timestamp=1700002100.0,
            hand_number=1,
            dealer_button=0,
            small_blind=1,
            big_blind=2,
            sb_amount=0.5,
            bb_amount=1.0,
            players=[{"name": f"Player {i+1}", "stack": 100.0} for i in range(6)],
            hole_cards={},
            board_cards=[],
            winner="Player 1",
            pot_size=8.0,
            hand_complete=True
        )
        
        mock_session.hands = [mock_hand]
        mock_logger.session = mock_session
        
        # Test session manager
        session_manager = SessionManager(
            num_players=6,
            big_blind=1.0,
            logger=mock_logger
        )
        
        # Mock the session state with proper types
        from core.session_manager import SessionState, SessionMetadata
        
        metadata = SessionMetadata(
            session_id="integration_test_789",
            start_time=1700002000.0,
            total_players=6,
            big_blind_amount=1.0
        )
        
        session_state = SessionState(
            session_metadata=metadata,
            current_hand_number=1,
            hands_played=[mock_hand]
        )
        
        session_manager.session_state = session_state
        
        # Test end session (should trigger PHH export)
        result = session_manager.end_session()
        
        # Verify session ended properly
        self.assertIsInstance(result, dict)
        
        print("✅ Session manager integration test passed")


def run_tests():
    """Run all PHH integration tests."""
    print("🔄 Running PHH Session Integration Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPHHSessionIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All PHH integration tests passed!")
        print(f"Tests run: {result.testsRun}")
        return True
    else:
        print("❌ Some tests failed!")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False


if __name__ == "__main__":
    run_tests()
