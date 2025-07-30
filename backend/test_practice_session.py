#!/usr/bin/env python3
"""
Test script for the integrated practice session functionality.
"""

from enhanced_main_gui import EnhancedMainGUI
from gui_models import StrategyData


def test_practice_session_integration():
    """Test the practice session integration."""
    print("🎰 Testing Practice Session Integration")
    print("=" * 50)

    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")

    # Create main GUI
    gui = EnhancedMainGUI()

    # Test practice simulator initialization
    if hasattr(gui, "practice_simulator"):
        print("✅ Practice simulator initialized successfully")

        # Test session report
        report = gui.practice_simulator.get_session_report()
        print(f"📊 Initial session stats: {report['hands_played']} hands played")

        # Test hand evaluation
        from poker_practice_simulator import Player, GameState, Position

        test_player = Player(
            name="Test Player", position=Position.UTG, stack=100.0, cards=["Ah", "Kd"]
        )

        test_game_state = GameState(players=[test_player])
        action, bet_size = gui.practice_simulator.get_strategy_action(
            test_player, test_game_state
        )
        print(f"🎯 Test strategy action: {action.value} (bet size: {bet_size})")

        print("✅ Practice session integration test completed successfully!")
    else:
        print("❌ Practice simulator not found in main GUI")


if __name__ == "__main__":
    test_practice_session_integration()
