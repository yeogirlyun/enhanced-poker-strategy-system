# filename: launch_gui.py
"""
Simple launcher script for the Poker Strategy Development GUI

This script handles dependency checking, creates necessary files,
and launches the GUI with proper error handling.
"""

import sys
import os
import json
import traceback
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    
    missing_deps = []
    
    # Check core GUI dependencies
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter (usually comes with Python)")
    
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with: pip install matplotlib numpy")
        return False
    
    return True

def check_backend_availability():
    """Check if backend modules are available."""
    
    backend_files = [
        'enhanced_simulation_engine.py',
        'human_executable_optimizer.py', 
        'simplified_optimizer_interface.py'
    ]
    
    available_files = []
    missing_files = []
    
    for file in backend_files:
        if os.path.exists(file):
            available_files.append(file)
        else:
            missing_files.append(file)
    
    if missing_files:
        print("⚠️ Some backend modules not found:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nGUI will run in demo mode with limited functionality.")
        print("For full functionality, ensure all backend files are present.")
        
        response = input("\nContinue in demo mode? (y/n): ").lower()
        return response == 'y'
    else:
        print("✅ All backend modules found - full functionality available")
        return True

def create_default_strategy():
    """Create a default strategy file if it doesn't exist."""
    
    strategy_file = 'baseline_strategy.json'
    
    if os.path.exists(strategy_file):
        print(f"✅ Found existing strategy file: {strategy_file}")
        return True
    
    print(f"📝 Creating default strategy file: {strategy_file}")
    
    # Create a minimal default strategy
    default_strategy = {
        "hand_strength_tables": {
            "preflop": {
                "AA": 50, "KK": 45, "QQ": 40, "AKs": 35, "JJ": 30,
                "AKo": 30, "TT": 25, "AQs": 20, "AJs": 20, "KQs": 20,
                "AQo": 20, "99": 15, "KJs": 15, "QJs": 15, "JTs": 15,
                "ATs": 15, "T9s": 15, "88": 10, "77": 10, "A8s": 10,
                "A7s": 10, "A6s": 10, "A5s": 10, "A4s": 10, "A3s": 10,
                "A2s": 10, "KTs": 10, "QTs": 10, "AJo": 10, "KQo": 10,
                "66": 5, "55": 5, "44": 5, "33": 5, "22": 5,
                "K9s": 5, "Q9s": 5, "J9s": 5, "T8s": 5, "98s": 5,
                "87s": 5, "76s": 5, "KJo": 5, "QJo": 5
            },
            "postflop": {
                "high_card": 5, "pair": 15, "top_pair": 30, "over_pair": 35,
                "two_pair": 45, "set": 60, "straight": 70, "flush": 80,
                "full_house": 90, "quads": 100, "straight_flush": 120
            }
        },
        "preflop": {
            "open_rules": {
                "UTG": {"threshold": 30, "sizing": 3.0},
                "MP": {"threshold": 20, "sizing": 3.0},
                "CO": {"threshold": 15, "sizing": 2.5},
                "BTN": {"threshold": 10, "sizing": 2.5},
                "SB": {"threshold": 20, "sizing": 3.0}
            },
            "vs_raise": {
                "UTG": {"IP": {"value_thresh": 40, "call_range": [30, 39], "sizing": 3.0}},
                "MP": {"IP": {"value_thresh": 35, "call_range": [25, 34], "sizing": 3.0}},
                "CO": {"IP": {"value_thresh": 30, "call_range": [20, 29], "sizing": 3.0}},
                "BTN": {"IP": {"value_thresh": 25, "call_range": [15, 24], "sizing": 3.0}}
            }
        },
        "postflop": {
            "pfa": {
                "flop": {
                    "UTG": {"IP": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}},
                    "MP": {"IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}},
                    "CO": {"IP": {"val_thresh": 25, "check_thresh": 12, "sizing": 0.6}},
                    "BTN": {"IP": {"val_thresh": 20, "check_thresh": 10, "sizing": 0.5}}
                },
                "turn": {
                    "UTG": {"IP": {"val_thresh": 40, "check_thresh": 20, "sizing": 0.8}},
                    "MP": {"IP": {"val_thresh": 35, "check_thresh": 18, "sizing": 0.75}},
                    "CO": {"IP": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.7}},
                    "BTN": {"IP": {"val_thresh": 25, "check_thresh": 12, "sizing": 0.6}}
                },
                "river": {
                    "UTG": {"IP": {"val_thresh": 45, "check_thresh": 25, "sizing": 1.0}},
                    "MP": {"IP": {"val_thresh": 40, "check_thresh": 22, "sizing": 0.9}},
                    "CO": {"IP": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.8}},
                    "BTN": {"IP": {"val_thresh": 30, "check_thresh": 18, "sizing": 0.7}}
                }
            },
            "caller": {
                "flop": {
                    "UTG": {"IP": {"small_bet": [45, 25], "medium_bet": [60, 30], "large_bet": [70, 100]}},
                    "MP": {"IP": {"small_bet": [40, 22], "medium_bet": [55, 28], "large_bet": [65, 100]}},
                    "CO": {"IP": {"small_bet": [35, 20], "medium_bet": [50, 25], "large_bet": [60, 100]}},
                    "BTN": {"IP": {"small_bet": [30, 18], "medium_bet": [45, 22], "large_bet": [55, 100]}}
                }
            }
        }
    }
    
    try:
        with open(strategy_file, 'w') as f:
            json.dump(default_strategy, f, indent=2)
        print(f"✅ Created default strategy file: {strategy_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create strategy file: {e}")
        return False

def launch_gui():
    """Launch the GUI application."""
    
    try:
        print("🚀 Launching Poker Strategy Development GUI...")
        
        # Import and launch
        from strategy_development_gui import PokerStrategyGUI
        
        app = PokerStrategyGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("\nMake sure 'strategy_development_gui.py' is in the current directory.")
        return False
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main launcher function."""
    
    print("🎯 Advanced Poker Strategy Development GUI Launcher")
    print("=" * 55)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Check backend availability
    print("\n🔍 Checking backend modules...")
    if not check_backend_availability():
        return False
    
    # Create default strategy if needed
    print("\n📝 Checking strategy files...")
    if not create_default_strategy():
        return False
    
    # Launch GUI
    print("\n" + "=" * 55)
    return launch_gui()

def create_requirements_file():
    """Create requirements.txt file for easy installation."""
    
    requirements = [
        "# Core GUI requirements",
        "matplotlib>=3.0.0",
        "numpy>=1.18.0",
        "",
        "# Optional: Enhanced backend functionality", 
        "scipy>=1.6.0",
        "scikit-learn>=0.24.0",
        "",
        "# Optional: PDF export",
        "reportlab>=3.5.0",
        "",
        "# Optional: Enhanced optimization",
        "pandas>=1.2.0",
        ""
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    print("📝 Created requirements.txt - install with: pip install -r requirements.txt")

if __name__ == '__main__':
    try:
        # Create requirements file if it doesn't exist
        if not os.path.exists('requirements.txt'):
            create_requirements_file()
        
        # Run main launcher
        success = main()
        
        if not success:
            print("\n" + "=" * 55)
            print("❌ GUI launch failed")
            print("\nTroubleshooting:")
            print("1. Install dependencies: pip install matplotlib numpy")
            print("2. Ensure strategy_development_gui.py is present")
            print("3. Check Python version (3.6+ required)")
            print("4. Try running in demo mode for basic functionality")
            
            input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")