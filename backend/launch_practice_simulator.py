#!/usr/bin/env python3
"""
Standalone launcher for the Poker Practice Simulator.
"""

from poker_practice_simulator import PracticeSimulatorGUI
from gui_models import StrategyData


def main():
    """Launch the poker practice simulator."""
    print("🎰 Launching Poker Practice Simulator...")

    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")

    # Create and run simulator
    simulator = PracticeSimulatorGUI(strategy_data)
    simulator.run()


if __name__ == "__main__":
    main()
