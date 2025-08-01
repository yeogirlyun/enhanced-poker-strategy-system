# Poker Strategy Development System

A comprehensive poker strategy development and practice system with advanced UI and state management.

## 🚀 Quick Start

### Run the Application
```bash
# From the project root directory
python3 run_poker.py
```

### Alternative Run Method
```bash
# Navigate to backend directory
cd backend
python3 main_gui.py
```

## 📁 Project Structure

```
Poker/
├── backend/                 # Main application code
│   ├── main_gui.py         # Main GUI application
│   ├── practice_session_ui.py  # Practice session interface
│   ├── shared/             # Shared components
│   └── sounds/             # Sound effects
├── frontend/               # Web interface (if applicable)
├── tests/                  # Test suite
├── sounds/                 # Additional sound files
└── run_poker.py           # Launcher script
```

## 🎯 Features

- **Practice Session**: Interactive poker practice with AI opponents
- **Strategy Development**: Advanced strategy analysis and optimization
- **Hand Grid**: Visual hand selection and tier management
- **Decision Tables**: Postflop decision analysis
- **Sound Effects**: Authentic poker sound effects
- **Responsive UI**: Dynamic layout that adapts to window size

## 🔧 Requirements

- Python 3.8+
- tkinter (usually included with Python)
- pygame (for sound effects)

## 📝 Recent Fixes

- ✅ Fixed state corruption issues
- ✅ Centralized winner determination
- ✅ Dynamic button visibility
- ✅ Proper PhotoImage reference management
- ✅ Game flow improvements
- ✅ UI/UX enhancements

## 🎮 How to Play

1. Run the application using `python3 run_poker.py`
2. Navigate to the "Practice Session" tab
3. Click "🚀 Start New Hand" to begin
4. Use the action buttons to play your hand
5. Watch the game messages for detailed feedback

## 🐛 Troubleshooting

If you encounter any issues:
1. Make sure you're running from the project root directory
2. Check that all dependencies are installed
3. Clear Python cache if needed: `find . -name "*.pyc" -delete`

## 📊 Development Status

All critical bugs have been fixed and the application is fully functional! 