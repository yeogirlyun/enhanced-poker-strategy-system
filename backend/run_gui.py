#!/usr/bin/env python3
"""
GUI Poker Strategy Development System Launcher

This script launches the enhanced GUI poker strategy development system.
"""

import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

if __name__ == "__main__":
    from main_gui import PokerStrategyGUI
    
    print("🎮 Starting Enhanced GUI Poker Strategy Development System...")
    print("=" * 60)
    
    app = PokerStrategyGUI()
    app.run() 