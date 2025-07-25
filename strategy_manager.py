# filename: strategy_manager.py
"""
Hold'em Strategy Manager

Version 7.1 (2025-07-26) - 8-Max Expansion
- ADDED: Open rules, vs_raise, and blind_defense for UTG+1 and HJ
- UPDATED: Postflop pfa and caller rules with fallbacks for new positions
- ENSURED: Tighter ranges for early positions like UTG+1, looser for HJ

Version 7.0 (2025-01-25) - Modern Blind Defense Update

REVISION HISTORY:
================
- Version 7.0: Added modern blind defense strategy based on GTO principles
  * Implemented position-based blind defense ranges
  * Added pot odds considerations for BB and SB
  * Expanded hand ranges for blind defense
  * Created separate defense thresholds vs different positions
- Version 6.6: Fixed postflop data generation for all streets
- Version 6.2: Initial data-driven implementation
"""
import json
import sys

def create_default_strategy():
    """
    Generates a new strategy.json file with modern blind defense and 8-max positions.
    """
    strategy = {
        "hand_strength_tables": {
            "preflop": {
                # Core opening ranges (unchanged)
                "AA": 50, "KK": 45, "QQ": 40, "AKs": 35, "JJ": 30, "AKo": 30, "TT": 25,
                "AQs": 20, "AJs": 20, "KQs": 20, "AQo": 20, "99": 15, "KJs": 15,
                "QJs": 15, "JTs": 15, "ATs": 15, "T9s": 15, "88": 10, "77": 10,
                "A9s": 10, "A8s": 10, "A7s": 10, "A6s": 10, "A5s": 10, "A4s": 10,
                "A3s": 10, "A2s": 10, "KTs": 10, "QTs": 10, "AJo": 10, "66": 5, "55": 5,
                "44": 5, "33": 5, "22": 5, "K9s": 5, "Q9s": 5, "J9s": 5, "T8s": 5,
                "98s": 5, "87s": 5, "76s": 5, "KJo": 5, "QJo": 5,
                # Additional hands for blind defense
                "KQo": 8, "ATo": 7, "KTo": 6, "QTo": 6, "JTo": 6,
                "A9o": 5, "A8o": 4, "A7o": 4, "A6o": 3, "A5o": 3,
                "A4o": 3, "A3o": 3, "A2o": 3, "K9o": 4, "Q9o": 3,
                "J9o": 3, "T9o": 3, "98o": 2, "87o": 2, "76o": 2,
                "65s": 4, "54s": 4, "97s": 3, "86s": 3, "75s": 3,
                "64s": 2, "53s": 2, "K8s": 4, "K7s": 3, "K6s": 3,
                "K5s": 2, "K4s": 2, "K3s": 2, "K2s": 2,
                "Q8s": 3, "Q7s": 2, "Q6s": 2, "Q5s": 2,
                "J8s": 3, "J7s": 2, "T7s": 2, "96s": 2, "85s": 2
            },
            "postflop": {
                "high_card": 5, "pair": 15, "top_pair": 30, "over_pair": 35,
                "two_pair": 45, "set": 60, "straight": 70, "flush": 80,
                "full_house": 90, "quads": 100, "straight_flush": 120,
                "gutshot_draw": 12, "open_ended_draw": 18, "flush_draw": 20,
                "combo_draw": 35
            }
        },
        "preflop": {
            "open_rules": {
                "UTG": {"threshold": 30, "sizing": 3.0}, 
                "UTG+1": {"threshold": 28, "sizing": 3.0},  # Slightly looser than UTG
                "UTG+2": {"threshold": 25, "sizing": 3.0},  # For 8/9-max
                "MP": {"threshold": 20, "sizing": 3.0},
                "HJ": {"threshold": 18, "sizing": 2.5},    # Hijack, looser
                "CO": {"threshold": 15, "sizing": 2.5}, 
                "BTN": {"threshold": 10, "sizing": 2.5},
                "SB": {"threshold": 20, "sizing": 3.0}
            },
            "vs_raise": {
                # Standard 3-bet/call ranges for non-blind positions
                "UTG": {"OOP": {"value_thresh": 40, "call_range": [30, 35], "sizing": 3.5}, 
                        "IP": {"value_thresh": 40, "call_range": [30, 35], "sizing": 3.0}},
                "UTG+1": {"OOP": {"value_thresh": 38, "call_range": [28, 35], "sizing": 3.5}, 
                          "IP": {"value_thresh": 38, "call_range": [28, 35], "sizing": 3.0}},
                "UTG+2": {"OOP": {"value_thresh": 36, "call_range": [26, 33], "sizing": 3.5}, 
                          "IP": {"value_thresh": 36, "call_range": [26, 33], "sizing": 3.0}},
                "MP": {"OOP": {"value_thresh": 35, "call_range": [25, 30], "sizing": 3.5}, 
                       "IP": {"value_thresh": 35, "call_range": [25, 30], "sizing": 3.0}},
                "HJ": {"OOP": {"value_thresh": 32, "call_range": [22, 28], "sizing": 3.5}, 
                       "IP": {"value_thresh": 32, "call_range": [22, 28], "sizing": 3.0}},
                "CO": {"OOP": {"value_thresh": 30, "call_range": [20, 25], "sizing": 3.5}, 
                       "IP": {"value_thresh": 30, "call_range": [20, 25], "sizing": 3.0}},
                "BTN": {"OOP": {"value_thresh": 25, "call_range": [15, 20], "sizing": 3.5}, 
                        "IP": {"value_thresh": 25, "call_range": [15, 20], "sizing": 3.0}}
            },
            "blind_defense": {
                "BB": {
                    "vs_UTG": {
                        "value_thresh": 30,      # 3-bet: AA-TT, AK, AQs
                        "call_range": [8, 29],   # Call: 99-66, AQ-AJ, KQ, suited broadways
                        "sizing": 3.5,
                        "defend_freq": 0.35      # Defend 35% vs UTG
                    },
                    "vs_MP": {
                        "value_thresh": 25,      # 3-bet: AA-99, AK, AQ
                        "call_range": [6, 24],   # Call: 88-22, AJ-AT, KQ-KJ, suited connectors
                        "sizing": 3.5,
                        "defend_freq": 0.40      # Defend 40% vs MP
                    },
                    "vs_CO": {
                        "value_thresh": 20,      # 3-bet: AA-88, AK-AJ, KQ
                        "call_range": [3, 19],   # Call: 77-22, AT-A2, KJ-K9, all suited
                        "sizing": 3.0,
                        "defend_freq": 0.55      # Defend 55% vs CO
                    },
                    "vs_BTN": {
                        "value_thresh": 15,      # 3-bet: AA-77, AK-AT, KQ-KJ
                        "call_range": [2, 14],   # Call: 66-22, A9-A2, K9-K2, broadways
                        "sizing": 3.0,
                        "defend_freq": 0.65      # Defend 65% vs BTN
                    },
                    "vs_SB": {
                        "value_thresh": 20,      # 3-bet more vs SB (we have position)
                        "call_range": [3, 19],   # Call wide
                        "sizing": 2.5,           # Can size down IP
                        "defend_freq": 0.60      # Defend 60% vs SB
                    },
                    "vs_UTG+1": {"value_thresh": 28, "call_range": [7, 27], "sizing": 3.5, "defend_freq": 0.38},
                    "vs_UTG+2": {"value_thresh": 26, "call_range": [6, 25], "sizing": 3.5, "defend_freq": 0.42},
                    "vs_HJ": {"value_thresh": 22, "call_range": [4, 21], "sizing": 3.0, "defend_freq": 0.58}
                },
                "SB": {
                    "vs_UTG": {
                        "value_thresh": 35,      # 3-bet: AA-JJ, AK
                        "call_range": [20, 34],  # Call: TT-88, AQ, KQs
                        "sizing": 4.0,
                        "defend_freq": 0.15      # Defend only 15% vs UTG
                    },
                    "vs_MP": {
                        "value_thresh": 30,      # 3-bet: AA-TT, AK, AQs
                        "call_range": [15, 29],  # Call: 99-77, AQ, KQ, suited broadways
                        "sizing": 4.0,
                        "defend_freq": 0.18      # Defend 18% vs MP
                    },
                    "vs_CO": {
                        "value_thresh": 25,      # 3-bet: AA-99, AK, AQ
                        "call_range": [10, 24],  # Call: 88-66, AJ, KQ, suited connectors
                        "sizing": 3.5,
                        "defend_freq": 0.25      # Defend 25% vs CO
                    },
                    "vs_BTN": {
                        "value_thresh": 20,      # 3-bet: AA-88, AK-AJ, KQ
                        "call_range": [7, 19],   # Call: 77-55, AT, KJ, suited hands
                        "sizing": 3.5,
                        "defend_freq": 0.35      # Defend 35% vs BTN
                    },
                    "vs_UTG+1": {"value_thresh": 33, "call_range": [18, 32], "sizing": 4.0, "defend_freq": 0.16},
                    "vs_HJ": {"value_thresh": 27, "call_range": [12, 26], "sizing": 3.5, "defend_freq": 0.28}
                }
            }
        },
        "postflop": {
            "pfa": {
                "flop": {
                    "UTG": {"OOP": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}, 
                            "IP": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}},
                    "UTG+1": {"OOP": {"val_thresh": 34, "check_thresh": 15, "sizing": 0.75}, 
                              "IP": {"val_thresh": 34, "check_thresh": 15, "sizing": 0.75}},
                    "UTG+2": {"OOP": {"val_thresh": 32, "check_thresh": 15, "sizing": 0.72}, 
                              "IP": {"val_thresh": 32, "check_thresh": 15, "sizing": 0.72}},
                    "MP": {"OOP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}, 
                           "IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}},
                    "HJ": {"OOP": {"val_thresh": 28, "check_thresh": 14, "sizing": 0.65}, 
                           "IP": {"val_thresh": 28, "check_thresh": 14, "sizing": 0.65}},
                    "CO": {"OOP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6}, 
                           "IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6}},
                    "BTN": {"OOP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.5}, 
                            "IP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.5}},
                    # Blind-specific c-bet strategy (more careful from blinds)
                    "BB": {"OOP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.6}, 
                           "IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6}},
                    "SB": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.7}, 
                           "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.65}}
                },
                "turn": {
                    "UTG": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}, 
                            "IP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}},
                    "UTG+1": {"OOP": {"val_thresh": 39, "check_thresh": 24, "sizing": 0.75}, 
                              "IP": {"val_thresh": 39, "check_thresh": 24, "sizing": 0.75}},
                    "UTG+2": {"OOP": {"val_thresh": 38, "check_thresh": 23, "sizing": 0.75}, 
                              "IP": {"val_thresh": 38, "check_thresh": 23, "sizing": 0.75}},
                    "MP": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}, 
                           "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7}},
                    "HJ": {"OOP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7}, 
                           "IP": {"val_thresh": 32, "check_thresh": 18, "sizing": 0.65}},
                    "CO": {"OOP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7}, 
                           "IP": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.55}},
                    "BTN": {"OOP": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.55}, 
                            "IP": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.4}},
                    "BB": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.65}, 
                           "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.6}},
                    "SB": {"OOP": {"val_thresh": 45, "check_thresh": 30, "sizing": 0.75}, 
                           "IP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.7}}
                },
                "river": {
                    "UTG": {"OOP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}, 
                            "IP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}},
                    "UTG+1": {"OOP": {"val_thresh": 49, "check_thresh": 29, "sizing": 1.0}, 
                              "IP": {"val_thresh": 49, "check_thresh": 29, "sizing": 1.0}},
                    "UTG+2": {"OOP": {"val_thresh": 48, "check_thresh": 28, "sizing": 1.0}, 
                              "IP": {"val_thresh": 48, "check_thresh": 28, "sizing": 1.0}},
                    "MP": {"OOP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}, 
                           "IP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.8}},
                    "HJ": {"OOP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.8}, 
                           "IP": {"val_thresh": 42, "check_thresh": 22, "sizing": 0.75}},
                    "CO": {"OOP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.8}, 
                           "IP": {"val_thresh": 40, "check_thresh": 22, "sizing": 0.7}},
                    "BTN": {"OOP": {"val_thresh": 40, "check_thresh": 22, "sizing": 0.7}, 
                            "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.55}},
                    "BB": {"OOP": {"val_thresh": 50, "check_thresh": 30, "sizing": 0.8}, 
                           "IP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.75}},
                    "SB": {"OOP": {"val_thresh": 55, "check_thresh": 35, "sizing": 0.9}, 
                           "IP": {"val_thresh": 50, "check_thresh": 30, "sizing": 0.85}}
                }
            },
            "caller": {
                "flop": {
                    "UTG": {"OOP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}, 
                            "IP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}},
                    "UTG+1": {"OOP": {"small_bet": [44, 29], "medium_bet": [59, 34], "large_bet": [69, 100]}, 
                              "IP": {"small_bet": [44, 29], "medium_bet": [59, 34], "large_bet": [69, 100]}},
                    "UTG+2": {"OOP": {"small_bet": [43, 28], "medium_bet": [58, 33], "large_bet": [68, 100]}, 
                              "IP": {"small_bet": [43, 28], "medium_bet": [58, 33], "large_bet": [68, 100]}},
                    "MP": {"OOP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}, 
                           "IP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}},
                    "HJ": {"OOP": {"small_bet": [42, 27], "medium_bet": [57, 32], "large_bet": [67, 100]}, 
                           "IP": {"small_bet": [42, 27], "medium_bet": [57, 32], "large_bet": [67, 100]}},
                    "CO": {"OOP": {"small_bet": [45, 20], "medium_bet": [60, 30], "large_bet": [70, 100]}, 
                           "IP": {"small_bet": [45, 20], "medium_bet": [60, 30], "large_bet": [70, 100]}},
                    "BTN": {"OOP": {"small_bet": [35, 15], "medium_bet": [45, 20], "large_bet": [60, 100]}, 
                            "IP": {"small_bet": [35, 15], "medium_bet": [45, 20], "large_bet": [60, 100]}},
                    # Blinds play differently as callers (wider ranges)
                    "BB": {"OOP": {"small_bet": [40, 15], "medium_bet": [50, 20], "large_bet": [65, 100]}, 
                           "IP": {"small_bet": [35, 12], "medium_bet": [45, 18], "large_bet": [60, 100]}},
                    "SB": {"OOP": {"small_bet": [45, 20], "medium_bet": [55, 25], "large_bet": [70, 100]}, 
                           "IP": {"small_bet": [40, 18], "medium_bet": [50, 22], "large_bet": [65, 100]}}
                },
                "turn": {
                    "UTG": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, 
                            "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}},
                    "UTG+1": {"OOP": {"small_bet": [44, 24], "medium_bet": [49, 29], "large_bet": [54, 100]}, 
                              "IP": {"small_bet": [39, 21], "medium_bet": [44, 24], "large_bet": [49, 100]}},
                    "UTG+2": {"OOP": {"small_bet": [43, 23], "medium_bet": [48, 28], "large_bet": [53, 100]}, 
                              "IP": {"small_bet": [38, 20], "medium_bet": [43, 23], "large_bet": [48, 100]}},
                    "MP": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, 
                           "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}},
                    "HJ": {"OOP": {"small_bet": [42, 22], "medium_bet": [47, 27], "large_bet": [52, 100]}, 
                           "IP": {"small_bet": [37, 19], "medium_bet": [42, 22], "large_bet": [47, 100]}},
                    "CO": {"OOP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}, 
                           "IP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}},
                    "BTN": {"OOP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}, 
                            "IP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}},
                    "BB": {"OOP": {"small_bet": [40, 20], "medium_bet": [45, 22], "large_bet": [50, 100]}, 
                           "IP": {"small_bet": [35, 18], "medium_bet": [40, 20], "large_bet": [45, 100]}},
                    "SB": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 28], "large_bet": [55, 100]}, 
                           "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}}
                },
                "river": {
                    "UTG": {"OOP": {"small_bet": [55, 35], "medium_bet": [60, 40], "large_bet": [65, 100]}, 
                            "IP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}},
                    "UTG+1": {"OOP": {"small_bet": [54, 34], "medium_bet": [59, 39], "large_bet": [64, 100]}, 
                              "IP": {"small_bet": [49, 29], "medium_bet": [54, 34], "large_bet": [59, 100]}},
                    "UTG+2": {"OOP": {"small_bet": [53, 33], "medium_bet": [58, 38], "large_bet": [63, 100]}, 
                              "IP": {"small_bet": [48, 28], "medium_bet": [53, 33], "large_bet": [58, 100]}},
                    "MP": {"OOP": {"small_bet": [55, 35], "medium_bet": [60, 40], "large_bet": [65, 100]}, 
                           "IP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}},
                    "HJ": {"OOP": {"small_bet": [52, 32], "medium_bet": [57, 37], "large_bet": [62, 100]}, 
                           "IP": {"small_bet": [47, 27], "medium_bet": [52, 32], "large_bet": [57, 100]}},
                    "CO": {"OOP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}, 
                           "IP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}},
                    "BTN": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, 
                            "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}},
                    "BB": {"OOP": {"small_bet": [50, 28], "medium_bet": [55, 32], "large_bet": [60, 100]}, 
                           "IP": {"small_bet": [45, 25], "medium_bet": [50, 28], "large_bet": [55, 100]}},
                    "SB": {"OOP": {"small_bet": [55, 32], "medium_bet": [60, 38], "large_bet": [65, 100]}, 
                           "IP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}}
                }
            }
        }
    }
    
    with open('strategy.json', 'w') as f:
        json.dump(strategy, f, indent=4)
    print("✅ Successfully created 'strategy.json' with modern blind defense strategy and 8-max positions.")
    print("   - Added wider hand ranges for blind defense")
    print("   - Implemented position-based defense frequencies")
    print("   - Created specific blind vs position thresholds")
    print("   - Added pot odds considerations")
    print("   - Expanded for 8-max with UTG+1 and HJ")

def load_strategy():
    try:
        with open('strategy.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: 'strategy.json' not found. Please run 'python3 strategy_manager.py create' first.")
        return None

def save_strategy(strategy):
    with open('strategy.json', 'w') as f:
        json.dump(strategy, f, indent=4)
    print("✅ Strategy saved successfully.")

def view_strategy(path):
    strategy = load_strategy()
    if not strategy: return
    try:
        data = strategy
        for key in path:
            data = data[key]
        print(json.dumps(data, indent=4))
    except KeyError:
        print(f"❌ Error: Invalid path '{' '.join(path)}'.")

def edit_strategy(path, key, value):
    strategy = load_strategy()
    if not strategy: return
    try:
        data = strategy
        for p in path:
            data = data[p]
        try:
            if key == 'call_range':
                value = [int(x.strip()) for x in value.split(',')]
            else:
                value = float(value)
        except ValueError:
            pass
        original_value = data.get(key)
        data[key] = value
        print(f"✅ Changed '{'.'.join(path)}.{key}' from '{original_value}' to '{value}'.")
        save_strategy(strategy)
    except (KeyError, TypeError):
        print(f"❌ Error: Invalid path or key '{' '.join(path)} {key}'.")

def show_blind_defense_stats():
    """Display blind defense statistics."""
    strategy = load_strategy()
    if not strategy: return
    
    print("\n📊 BLIND DEFENSE FREQUENCIES")
    print("="*50)
    
    blind_def = strategy['preflop']['blind_defense']
    
    print("\n🎯 BIG BLIND Defense:")
    for opponent, rules in blind_def['BB'].items():
        defend_pct = rules['defend_freq'] * 100
        print(f"  {opponent}: Defend {defend_pct:.0f}% | 3-bet HS≥{rules['value_thresh']} | Call HS {rules['call_range']}")
    
    print("\n🎯 SMALL BLIND Defense:")
    for opponent, rules in blind_def['SB'].items():
        defend_pct = rules['defend_freq'] * 100
        print(f"  {opponent}: Defend {defend_pct:.0f}% | 3-bet HS≥{rules['value_thresh']} | Call HS {rules['call_range']}")
    
    print("\n💡 Key Improvements:")
    print("  - BB defends 35-65% depending on opener position")
    print("  - SB defends 15-35% (tighter due to position)")
    print("  - Wider calling ranges with good pot odds")
    print("  - Position-specific 3-bet frequencies")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  - python3 strategy_manager.py create")
        print("  - python3 strategy_manager.py view <path>")
        print("  - python3 strategy_manager.py edit <path> <key> <value>")
        print("  - python3 strategy_manager.py blinds (show blind defense stats)")
        return
    
    command = sys.argv[1]
    if command == 'create':
        create_default_strategy()
    elif command == 'view':
        view_strategy(sys.argv[2:])
    elif command == 'edit':
        edit_strategy(sys.argv[2:-2], sys.argv[-2], sys.argv[-1])
    elif command == 'blinds':
        show_blind_defense_stats()
    else:
        print(f"❌ Error: Unknown command '{command}'.")

if __name__ == '__main__':
    main()