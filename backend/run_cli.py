#!/usr/bin/env python3
"""
CLI Poker Game Launcher

This script launches the enhanced CLI poker game with all the latest features.
"""

import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

if __name__ == "__main__":
    from cli_poker_game import ImprovedCLIPokerGame
    
    print("🎮 Starting Enhanced CLI Poker Game...")
    print("=" * 50)
    
    game = ImprovedCLIPokerGame()
    game.run_game() 