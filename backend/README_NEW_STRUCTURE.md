# 🎮 Poker Strategy Development System - Simplified Structure

## 📁 New Directory Structure

The project has been reorganized to eliminate confusing multi-level directories. All main files are now directly in the `backend/` folder:

```
backend/
├── main_gui.py                    # Main GUI application
├── cli_poker_game.py             # CLI poker game
├── comprehensive_test_suite.py    # Test suite
├── dialogs.py                    # GUI dialog windows
├── hand_grid.py                  # Hand grid widget
├── tier_panel.py                 # Tier management panel
├── gui_models.py                 # Shared GUI models
├── run_gui.py                    # GUI launcher script
├── run_cli.py                    # CLI launcher script
├── shared/                       # Shared components
│   ├── poker_state_machine_enhanced.py
│   └── gui_models.py (original)
└── [other files...]
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
```

## ✅ Benefits of New Structure

1. **🎯 Simpler Navigation**: All main files in one directory
2. **🔧 Easier Maintenance**: No complex import paths
3. **📦 Clear Organization**: Shared components in `shared/` folder
4. **⚡ Faster Development**: Direct access to all files

## 🔄 Migration Complete

- ✅ Moved CLI files from `cli_version/` to `backend/`
- ✅ Moved GUI files from `gui_version/` to `backend/`
- ✅ Updated all import statements
- ✅ Tested both CLI and GUI versions
- ✅ Maintained all functionality

The old `cli_version/` and `gui_version/` directories can now be safely removed if desired. 