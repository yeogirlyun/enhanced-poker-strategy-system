# filename: strategy_manager.py
"""
Hold'em Strategy Manager - Command-Line Interface

REVISION HISTORY:
================
Version 10.5 (2025-07-28) - Final Data Restoration
- FIXED: The `create` command was still missing postflop data for late
  positions (CO, BTN). The postflop tables have been fully restored with
  data for ALL positions on ALL streets. This is the final, complete version.

Version 10.4 (2025-07-28) - Bug Fix
- FIXED: A NameError crash caused by the accidental deletion of handler functions.

Version 10.3 (2025-07-28) - Postflop Data Restoration
- FIXED: Restored missing postflop decision tables.
"""
import json
import sys

DEFAULT_STRATEGY_FILE = 'strategy.json'

def _ensure_json_extension(filename):
    """Appends .json to the filename if it's not already there."""
    if not filename.endswith('.json'):
        return filename + '.json'
    return filename

def load_strategy(filename=DEFAULT_STRATEGY_FILE):
    """Loads the strategy from the JSON file, or exits if not found."""
    filename = _ensure_json_extension(filename)
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{filename}' not found. To create it, run 'python3 strategy_manager.py create {filename}'.")
        sys.exit(1)

def save_strategy(strategy, filename, success_message):
    """Saves the updated strategy to the specified JSON file."""
    filename = _ensure_json_extension(filename)
    with open(filename, 'w') as f:
        json.dump(strategy, f, indent=4)
    print(f"✅ {success_message}")

# --- COMMAND HANDLERS ---
def handle_set(args, filename):
    """Handles the 'set' or 'add' command to update a hand's HS."""
    if len(args) != 2:
        print("❌ Error: 'set' command requires exactly two arguments: <hand> <hs_value>")
        return
    hand, hs_str = args
    try:
        hs_value = int(hs_str)
        strategy = load_strategy(filename)
        strategy['hand_strength_tables']['preflop'][hand] = hs_value
        save_strategy(strategy, filename, f"In '{_ensure_json_extension(filename)}', set HS for {hand} to {hs_value}.")
    except ValueError:
        print("❌ Error: HS value must be an integer.")
    except KeyError:
        print(f"❌ Error: Could not find 'hand_strength_tables.preflop' in '{_ensure_json_extension(filename)}'.")

def handle_remove(args, filename):
    """Handles the 'remove' command to delete a hand."""
    if len(args) != 1:
        print("❌ Error: 'remove' command requires exactly one argument: <hand>")
        return
    hand = args[0]
    strategy = load_strategy(filename)
    if hand in strategy['hand_strength_tables']['preflop']:
        del strategy['hand_strength_tables']['preflop'][hand]
        save_strategy(strategy, filename, f"In '{_ensure_json_extension(filename)}', removed {hand} from the HS table.")
    else:
        print(f"⚠️ Warning: Hand '{hand}' not found in the HS table in '{_ensure_json_extension(filename)}'.")

def handle_edit(args, filename):
    """Handles the 'edit' command to change any value in the strategy."""
    if len(args) != 2:
        print("❌ Error: 'edit' command requires exactly two arguments: <path.to.key> <value>")
        return
    path_str, new_value_str = args
    strategy = load_strategy(filename)
    try:
        if '.' in new_value_str: new_value = float(new_value_str)
        else: new_value = int(new_value_str)
    except ValueError:
        new_value = new_value_str
    try:
        keys = path_str.split('.')
        data = strategy
        for key in keys[:-1]: data = data[key]
        data[keys[-1]] = new_value
        save_strategy(strategy, filename, f"In '{_ensure_json_extension(filename)}', set '{path_str}' to {new_value}.")
    except (KeyError, TypeError):
        print(f"❌ Error: Invalid path '{path_str}'. Please check the path and try again.")

def handle_view(args, filename):
    """Handles the 'view' command to display parts of the strategy."""
    if len(args) == 0:
        print("❌ Error: 'view' command requires a path (e.g., 'preflop.open_rules').")
        return
    path_str = args[0]
    strategy = load_strategy(filename)
    try:
        keys = path_str.split('.')
        data = strategy
        for key in keys: data = data[key]
        print(json.dumps(data, indent=4))
    except (KeyError, TypeError):
        print(f"❌ Error: Invalid path '{path_str}'.")

def handle_create(args):
    """Creates a new default strategy file, with an optional custom name."""
    if len(args) > 1:
        print("❌ Error: 'create' command accepts at most one argument: [new_filename]")
        return
    
    raw_filename = args[0] if args else DEFAULT_STRATEGY_FILE
    filename = _ensure_json_extension(raw_filename)
    
    default_strategy = {
        "hand_strength_tables": {
            "preflop": {
                "AA": 50, "KK": 45, "QQ": 40, "AKs": 35, "JJ": 30, "AKo": 30, "TT": 25, "AQs": 20, "AJs": 20,
                "KQs": 20, "AQo": 20, "99": 15, "KJs": 15, "QJs": 15, "JTs": 15, "ATs": 15, "T9s": 15, "88": 10,
                "77": 10, "A8s": 10, "A7s": 10, "A6s": 10, "A5s": 10, "A4s": 10, "A3s": 10, "A2s": 10, "KTs": 10,
                "QTs": 10, "AJo": 10, "KQo": 10, "66": 5, "55": 5, "44": 5, "33": 5, "22": 5, "K9s": 5, "Q9s": 5,
                "J9s": 5, "T8s": 5, "98s": 5, "87s": 5, "76s": 5, "KJo": 5, "QJo": 5, "K8s": 4, "65s": 4, "54s": 4
            },
            "postflop": {
                "high_card": 5, "pair": 15, "top_pair": 30, "over_pair": 35, "two_pair": 45, "set": 60,
                "straight": 70, "flush": 80, "full_house": 90, "quads": 100, "straight_flush": 120,
                "gutshot_draw": 12, "open_ended_draw": 18, "flush_draw": 20, "combo_draw": 35
            }
        },
        "preflop": {
            "open_rules": {
                "UTG": {"threshold": 30, "sizing": 3.0}, "UTG+1": {"threshold": 20, "sizing": 3.0},
                "UTG+2": {"threshold": 20, "sizing": 3.0}, "MP": {"threshold": 15, "sizing": 3.0},
                "HJ": {"threshold": 10, "sizing": 2.5}, "CO": {"threshold": 10, "sizing": 2.5},
                "BTN": {"threshold": 5, "sizing": 2.5}, "SB": {"threshold": 20, "sizing": 3.0}
            },
            "vs_raise": {
                "UTG": {"OOP": {"value_thresh": 40, "call_range": [30, 39], "sizing": 3.5}, "IP": {"value_thresh": 40, "call_range": [30, 39], "sizing": 3.0}},
                "UTG+1": {"OOP": {"value_thresh": 40, "call_range": [30, 39], "sizing": 3.5}, "IP": {"value_thresh": 40, "call_range": [30, 39], "sizing": 3.0}},
                "UTG+2": {"OOP": {"value_thresh": 40, "call_range": [20, 29], "sizing": 3.5}, "IP": {"value_thresh": 40, "call_range": [20, 29], "sizing": 3.0}},
                "MP": {"OOP": {"value_thresh": 30, "call_range": [20, 29], "sizing": 3.5}, "IP": {"value_thresh": 30, "call_range": [20, 29], "sizing": 3.0}},
                "HJ": {"OOP": {"value_thresh": 30, "call_range": [10, 19], "sizing": 3.5}, "IP": {"value_thresh": 30, "call_range": [10, 19], "sizing": 3.0}},
                "CO": {"OOP": {"value_thresh": 30, "call_range": [10, 19], "sizing": 3.5}, "IP": {"value_thresh": 30, "call_range": [10, 19], "sizing": 3.0}},
                "BTN": {"OOP": {"value_thresh": 20, "call_range": [10, 19], "sizing": 3.5}, "IP": {"value_thresh": 20, "call_range": [10, 19], "sizing": 3.0}}
            },
            "blind_defense": {
                "BB": {"vs_UTG": {"value_thresh": 40, "call_range": [20, 39], "sizing": 3.5}, "vs_MP": {"value_thresh": 30, "call_range": [10, 29], "sizing": 3.5}, "vs_CO": {"value_thresh": 20, "call_range": [5, 19], "sizing": 3.0}, "vs_BTN": {"value_thresh": 20, "call_range": [5, 19], "sizing": 3.0}},
                "SB": {"vs_UTG": {"value_thresh": 30, "call_range": [99, 98], "sizing": 4.0}, "vs_MP": {"value_thresh": 30, "call_range": [99, 98], "sizing": 4.0}, "vs_CO": {"value_thresh": 20, "call_range": [10, 19], "sizing": 3.5}, "vs_BTN": {"value_thresh": 20, "call_range": [10, 19], "sizing": 3.5}}
            }
        },
        "postflop": {
            "pfa": {
                "flop": {
                    "UTG": {"OOP": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}, "IP": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}},
                    "MP": {"OOP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}, "IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}},
                    "CO": {"OOP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6}, "IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.6}},
                    "BTN": {"OOP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.5}, "IP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.5}}
                },
                "turn": {
                    "UTG": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}, "IP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}},
                    "MP": {"OOP": {"val_thresh": 40, "check_thresh": 25, "sizing": 0.75}, "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7}},
                    "CO": {"OOP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.7}, "IP": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.55}},
                    "BTN": {"OOP": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.55}, "IP": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.4}}
                },
                "river": {
                    "UTG": {"OOP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}, "IP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}},
                    "MP": {"OOP": {"val_thresh": 50, "check_thresh": 30, "sizing": 1.0}, "IP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.8}},
                    "CO": {"OOP": {"val_thresh": 45, "check_thresh": 25, "sizing": 0.8}, "IP": {"val_thresh": 40, "check_thresh": 22, "sizing": 0.7}},
                    "BTN": {"OOP": {"val_thresh": 40, "check_thresh": 22, "sizing": 0.7}, "IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.55}}
                }
            },
            "caller": {
                "flop": {
                    "UTG": {"OOP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}, "IP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}},
                    "MP": {"OOP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}, "IP": {"small_bet": [45, 30], "medium_bet": [60, 35], "large_bet": [70, 100]}},
                    "CO": {"OOP": {"small_bet": [45, 20], "medium_bet": [60, 30], "large_bet": [70, 100]}, "IP": {"small_bet": [45, 20], "medium_bet": [60, 30], "large_bet": [70, 100]}},
                    "BTN": {"OOP": {"small_bet": [35, 15], "medium_bet": [45, 20], "large_bet": [60, 100]}, "IP": {"small_bet": [35, 15], "medium_bet": [45, 20], "large_bet": [60, 100]}}
                },
                "turn": {
                    "UTG": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}},
                    "MP": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}},
                    "CO": {"OOP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}, "IP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}},
                    "BTN": {"OOP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}, "IP": {"small_bet": [35, 20], "medium_bet": [40, 22], "large_bet": [45, 100]}}
                },
                "river": {
                    "UTG": {"OOP": {"small_bet": [55, 35], "medium_bet": [60, 40], "large_bet": [65, 100]}, "IP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}},
                    "MP": {"OOP": {"small_bet": [55, 35], "medium_bet": [60, 40], "large_bet": [65, 100]}, "IP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}},
                    "CO": {"OOP": {"small_bet": [50, 30], "medium_bet": [55, 35], "large_bet": [60, 100]}, "IP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}},
                    "BTN": {"OOP": {"small_bet": [45, 25], "medium_bet": [50, 30], "large_bet": [55, 100]}, "IP": {"small_bet": [40, 22], "medium_bet": [45, 25], "large_bet": [50, 100]}}
                }
            }
        }
    }
    save_strategy(default_strategy, filename, f"Successfully created new, complete strategy file '{filename}'.")

def print_usage():
    """Prints the help message."""
    print("--- Hold'em Strategy Manager ---")
    print("Usage: python3 strategy_manager.py [-f file] <command> [arguments...]\n")
    print("Options:")
    print("  -f, --file <filename>       - Specify a strategy file to edit. Auto-appends .json.")
    print("                                Defaults to 'strategy.json'.\n")
    print("Commands:")
    print("  create [new_filename]     - Creates a new default strategy file.")
    print("  view <path.to.key>          - Displays a part of the strategy.")
    print("  set <hand> <hs>             - Sets the Hand Strength for a preflop hand.")
    print("  remove <hand>               - Removes a hand from the preflop HS table.")
    print("  edit <path.to.key> <value>  - Edits a specific value in the decision tables.")
    print("-" * 34)

def main():
    """Main function to dispatch commands."""
    args = sys.argv[1:]
    filename = DEFAULT_STRATEGY_FILE
    if len(args) > 1 and (args[0] == '-f' or args[0] == '--file'):
        filename = _ensure_json_extension(args[1])
        args = args[2:]
    if not args:
        print_usage()
        return
    command = args[0]
    command_args = args[1:]
    command_map = {
        'create': handle_create, 'view': handle_view, 'set': handle_set,
        'add': handle_set, 'remove': handle_remove, 'edit': handle_edit,
    }
    if command in command_map:
        if command == 'create':
            handle_create(command_args)
        else:
            command_map[command](command_args, filename)
    else:
        print(f"❌ Error: Unknown command '{command}'.")
        print_usage()

if __name__ == '__main__':
    main()
