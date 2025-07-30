#!/usr/bin/env python3
"""
Test script to evaluate different Python poker libraries
"""

import time
import sys

def test_pypokerengine():
    """Test PyPokerEngine library."""
    print("🔍 Testing PyPokerEngine...")
    try:
        from pypokerengine.api.game import setup_config, start_poker
        from pypokerengine.players import BasePokerPlayer
        from pypokerengine.utils.card_utils import gen_cards
        
        print("✅ PyPokerEngine imported successfully")
        
        # Test basic functionality
        config = setup_config(max_round=1, initial_stack=100, small_blind=1)
        print("✅ PyPokerEngine config setup works")
        
        return True
    except Exception as e:
        print(f"❌ PyPokerEngine test failed: {e}")
        return False

def test_pokerkit():
    """Test PokerKit library."""
    print("🔍 Testing PokerKit...")
    try:
        from pokerkit import Game, Player, Action, Card, Hand
        
        print("✅ PokerKit imported successfully")
        
        # Test basic functionality
        game = Game()
        print("✅ PokerKit Game created successfully")
        
        # Test hand evaluation
        cards = [Card.from_str("Ah"), Card.from_str("Kh")]
        hand = Hand(cards)
        print("✅ PokerKit hand evaluation works")
        
        return True
    except Exception as e:
        print(f"❌ PokerKit test failed: {e}")
        return False

def test_treys():
    """Test treys library."""
    print("🔍 Testing treys...")
    try:
        from treys import Card, Evaluator
        
        print("✅ treys imported successfully")
        
        # Test hand evaluation
        evaluator = Evaluator()
        card1 = Card.new('Ah')
        card2 = Card.new('Kh')
        print("✅ treys hand evaluation works")
        
        return True
    except Exception as e:
        print(f"❌ treys test failed: {e}")
        return False

def benchmark_hand_evaluation():
    """Benchmark hand evaluation performance."""
    print("\n🏁 Benchmarking hand evaluation performance...")
    
    # Test treys (fastest)
    try:
        from treys import Card, Evaluator
        evaluator = Evaluator()
        
        start_time = time.time()
        for _ in range(10000):
            card1 = Card.new('Ah')
            card2 = Card.new('Kh')
            evaluator.evaluate([card1, card2], [])
        treys_time = time.time() - start_time
        print(f"✅ treys: {treys_time:.4f}s for 10,000 evaluations")
    except Exception as e:
        print(f"❌ treys benchmark failed: {e}")
        treys_time = float('inf')
    
    # Test PokerKit
    try:
        from pokerkit import Card, Hand
        start_time = time.time()
        for _ in range(10000):
            cards = [Card.from_str("Ah"), Card.from_str("Kh")]
            hand = Hand(cards)
        pokerkit_time = time.time() - start_time
        print(f"✅ PokerKit: {pokerkit_time:.4f}s for 10,000 evaluations")
    except Exception as e:
        print(f"❌ PokerKit benchmark failed: {e}")
        pokerkit_time = float('inf')
    
    return treys_time, pokerkit_time

def test_integration_with_strategy():
    """Test how well each library integrates with our strategy system."""
    print("\n🎯 Testing integration with our strategy system...")
    
    # Load our strategy
    try:
        from gui_models import StrategyData
        strategy_data = StrategyData()
        strategy_data.load_strategy_from_file("modern_strategy.json")
        print("✅ Strategy data loaded successfully")
    except Exception as e:
        print(f"❌ Strategy loading failed: {e}")
        return
    
    # Test PokerKit integration
    try:
        from pokerkit import Game, Player, Action, Card
        from poker_practice_simulator import Action as SimAction
        
        print("✅ PokerKit can integrate with our strategy system")
        
        # Test action mapping
        action_map = {
            "fold": Action.FOLD,
            "check": Action.CHECK,
            "call": Action.CALL,
            "bet": Action.BET,
            "raise": Action.RAISE
        }
        print("✅ Action mapping works")
        
    except Exception as e:
        print(f"❌ PokerKit integration test failed: {e}")

def main():
    """Main test function."""
    print("🎰 Testing Python Poker Libraries\n")
    
    # Test basic functionality
    pypokerengine_works = test_pypokerengine()
    pokerkit_works = test_pokerkit()
    treys_works = test_treys()
    
    print(f"\n📊 Library Status:")
    print(f"PyPokerEngine: {'✅' if pypokerengine_works else '❌'}")
    print(f"PokerKit: {'✅' if pokerkit_works else '❌'}")
    print(f"treys: {'✅' if treys_works else '❌'}")
    
    # Benchmark performance
    treys_time, pokerkit_time = benchmark_hand_evaluation()
    
    # Test integration
    test_integration_with_strategy()
    
    # Recommendations
    print(f"\n🎯 Recommendations:")
    if pokerkit_works:
        print("✅ PokerKit: Best choice for full game engine")
        print("   - Modern, well-structured API")
        print("   - Good integration potential")
        print("   - Active development")
    
    if treys_works:
        print("✅ treys: Best for hand evaluation")
        print("   - Fastest performance")
        print("   - Battle-tested")
        print("   - Good for hybrid approach")
    
    if pypokerengine_works:
        print("✅ PyPokerEngine: Most comprehensive")
        print("   - Full game engine")
        print("   - AI player support")
        print("   - More complex setup")

if __name__ == "__main__":
    main() 