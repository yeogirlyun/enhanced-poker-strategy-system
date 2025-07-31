# 🎮 Poker Strategy Development System - Clean Structure

## 📁 Final Directory Structure

The project has been reorganized and cleaned up. All main files are now directly in the `backend/` folder:

```
backend/
├── main_gui.py                    # Main GUI application
├── enhanced_main_gui_v2.py        # Enhanced GUI version
├── cli_poker_game.py             # CLI poker game
├── comprehensive_test_suite.py    # Test suite
├── dialogs.py                    # GUI dialog windows
├── hand_grid.py                  # Hand grid widget
├── tier_panel.py                 # Tier management panel
├── pdf_export.py                 # PDF export functionality
├── gui_models.py                 # Shared GUI models
├── run_gui.py                    # GUI launcher script
├── run_cli.py                    # CLI launcher script
├── shared/                       # Shared components
│   ├── poker_state_machine_enhanced.py
│   └── gui_models.py (original)
├── modern_strategy.json          # Strategy configuration
├── optimized_modern_strategy.json # Optimized strategy
├── strategy.json                 # Base strategy file
├── requirements.txt              # Python dependencies
└── README.md                     # Main documentation
```

## 🚀 How to Run

### **CLI Version:**
```bash
cd backend
python3 cli_poker_game.py
# OR
python3 run_cli.py
```

### **GUI Version:**
```bash
cd backend
python3 run_gui.py
# OR for enhanced version:
python3 enhanced_main_gui_v2.py
```

## ✅ Cleanup Completed

- ✅ **Removed**: `cli_version/` and `gui_version/` directories
- ✅ **Removed**: `__pycache__/` and `.mypy_cache/` directories
- ✅ **Moved**: All important files to main backend directory
- ✅ **Updated**: All import statements and run scripts
- ✅ **Tested**: Both CLI and GUI versions work correctly

## 🎯 Benefits of Clean Structure

1. **📁 Simple Navigation**: All files in one directory
2. **🧹 Clean Codebase**: No unused directories or files
3. **⚡ Fast Development**: Direct access to all components
4. **🔧 Easy Maintenance**: Clear organization and structure
5. **📦 Minimal Dependencies**: Only essential files included

## 📋 Key Features

- **🎮 CLI Poker Game**: Interactive command-line poker with strategy integration
- **🖥️ GUI Strategy Development**: Visual poker strategy development system
- **📊 PDF Export**: Generate strategy reports in PDF format
- **🧪 Comprehensive Testing**: Full test suite for all components
- **📈 Strategy Optimization**: Advanced strategy optimization tools

The project is now clean, organized, and ready for development! 🚀 