#!/usr/bin/env python3
"""
Test script for the Poker Practice Simulator.
"""

from poker_practice_simulator import PokerPracticeSimulator
from gui_models import StrategyData


def test_practice_simulator():
    """Test the practice simulator functionality."""
    print("🎰 Testing Poker Practice Simulator")
    print("=" * 50)
    
    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    # Create simulator
    simulator = PokerPracticeSimulator(strategy_data)
    
    # Test hand evaluation
    print("\n📊 Testing Hand Evaluation:")
    test_cases = [
        (["Ah", "Kd"], [], "AKo preflop"),
        (["Ah", "Ad"], [], "AA preflop"),
        (["Ah", "Kd"], ["Th", "Jc", "Qd"], "AK on T-J-Q flop"),
        (["Ah", "Kh"], ["Th", "Jh", "Qh"], "AK suited on flush draw"),
    ]
    
    for hole_cards, board, description in test_cases:
        strength = simulator.evaluate_hand_strength(hole_cards, board)
        print(f"  {description}: {strength:.1f}")
    
    # Test strategy actions
    print("\n🎯 Testing Strategy Actions:")
    from poker_practice_simulator import Player, GameState, Position, Action
    
    # Create test player
    player = Player(
        name="Test Player",
        position=Position.UTG,
        stack=100.0,
        cards=["Ah", "Kd"]
    )
    
    # Test preflop action
    game_state = GameState(
        players=[player],
        street="preflop"
    )
    
    action, bet_size = simulator.get_strategy_action(player, game_state)
    print(f"  UTG with AKo: {action.value} (bet size: {bet_size})")
    
    # Test postflop action
    game_state.board = ["Th", "Jc", "Qd"]
    game_state.street = "flop"
    
    action, bet_size = simulator.get_strategy_action(player, game_state)
    print(f"  Flop with straight: {action.value} (bet size: {bet_size})")
    
    # Test session report
    print("\n📈 Session Report:")
    report = simulator.get_session_report()
    for key, value in report.items():
        if key != "deviation_logs":  # Skip the logs for display
            print(f"  {key}: {value}")
    
    print("\n✅ Practice simulator test completed successfully!")


if __name__ == "__main__":
    test_practice_simulator() 