#!/usr/bin/env python3
"""
Test script for the Professional Poker Table

Demonstrates the enhanced poker table with animations and sound effects.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from enhanced_visual_poker_table import ProfessionalPokerTableGUI
from gui_models import StrategyData
import time
import random


def test_poker_table():
    """Test the professional poker table with various features."""
    print("🎮 Testing Professional Poker Table...")
    
    # Initialize strategy data
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Create poker table
    table = ProfessionalPokerTableGUI(strategy_data, num_players=6)
    
    print("✅ Poker table created successfully!")
    print("🎯 Features available:")
    print("   • Professional green felt table")
    print("   • 6 player seats with realistic positioning")
    print("   • Movable dealer button")
    print("   • Community card area")
    print("   • Pot display")
    print("   • Sound effects (with emoji simulation)")
    print("   • Action animations with fade-out effects")
    
    # Test the table features
    print("\n🧪 Testing table features...")
    
    # Test dealer button movement
    for i in range(6):
        print(f"🎯 Moving dealer to Player {i+1}")
        table.move_dealer_button(i)
        time.sleep(1)
    
    # Test player actions
    actions = ["Call", "Bet", "Raise", "Fold", "Check"]
    amounts = [25.0, 50.0, 75.0, 100.0, 150.0]
    
    print("\n🎭 Testing player actions...")
    for i in range(6):
        action = random.choice(actions)
        amount = random.choice(amounts) if action in ["Bet", "Raise"] else None
        print(f"Player {i+1}: {action} {f'${amount:.2f}' if amount else ''}")
        table.update_player_action(i, action, amount)
        table.update_player_bet(i, amount if amount else 0)
        time.sleep(0.5)
    
    # Test pot updates
    print("\n💰 Testing pot updates...")
    for pot in [50, 100, 200, 350, 500]:
        print(f"Pot: ${pot:.2f}")
        table.update_pot(pot)
        time.sleep(0.5)
    
    # Test community cards
    print("\n🃏 Testing community cards...")
    test_cards = ["A♠", "K♥", "Q♦", "J♣", "10♠"]
    table.update_community_cards(test_cards)
    
    print("\n✅ All tests completed!")
    print("🎮 Poker table is ready for use!")
    
    # Run the table
    table.run()


if __name__ == "__main__":
    test_poker_table() 