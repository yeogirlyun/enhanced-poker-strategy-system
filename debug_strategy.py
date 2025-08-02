#!/usr/bin/env python3
"""Debug script to check strategy data structure."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from gui_models import StrategyData

def debug_strategy():
    """Debug the strategy data structure."""
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    print("Strategy data structure:")
    print(f"Keys in strategy_dict: {list(strategy_data.strategy_dict.keys())}")
    
    if "hand_strength_tables" in strategy_data.strategy_dict:
        print(f"Keys in hand_strength_tables: {list(strategy_data.strategy_dict['hand_strength_tables'].keys())}")
        
        if "preflop" in strategy_data.strategy_dict["hand_strength_tables"]:
            preflop = strategy_data.strategy_dict["hand_strength_tables"]["preflop"]
            print(f"Sample preflop hands: {list(preflop.items())[:5]}")
            print(f"AA strength: {preflop.get('AA', 'NOT FOUND')}")
            print(f"KK strength: {preflop.get('KK', 'NOT FOUND')}")
    
    if "preflop" in strategy_data.strategy_dict:
        print(f"Keys in preflop: {list(strategy_data.strategy_dict['preflop'].keys())}")
        if "open_rules" in strategy_data.strategy_dict["preflop"]:
            print(f"UTG threshold: {strategy_data.strategy_dict['preflop']['open_rules']['UTG']['threshold']}")

if __name__ == "__main__":
    debug_strategy() 