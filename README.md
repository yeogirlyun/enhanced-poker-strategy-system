# 🎯 **Poker Strategy Practice System**

A comprehensive poker practice application that allows users to develop, test, and refine their poker strategies against both their own strategy and popular GTO (Game Theory Optimal) strategies.

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- Git

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yeogirlyun/enhanced-poker-strategy-system.git
   cd enhanced-poker-strategy-system
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Run the application**
   
   **Option A: Using the launcher (recommended)**
   ```bash
   # From the project root directory (Poker/)
   python3 run_poker.py
   ```

   **Option B: Direct execution**
   ```bash
   # Change to backend directory first
   cd backend
   python3 main_gui.py
   ```

   > **Note**: The `run_poker.py` launcher automatically handles the correct working directory and is the recommended way to start the application.

## 🎮 **Features**

### **Core Functionality**
- **Dual Strategy Bot System**: Practice against bots using your own strategy or GTO strategy
- **Real-time Strategy Analysis**: Get immediate feedback on your strategic decisions
- **Comprehensive Logging**: Track all actions and decisions for post-session analysis
- **Strategy Deviation Detection**: Identify when you deviate from your intended strategy
- **Performance Metrics**: Track win rates, decision accuracy, and strategic effectiveness

### **Practice Modes**
- **User Strategy Mode**: Bots play using your own strategy (test consistency)
- **GTO Strategy Mode**: Bots play using popular GTO strategy (test effectiveness)
- **Mixed Mode**: Some bots use your strategy, others use GTO

### **Analysis Tools**
- **Real-time Feedback**: See optimal vs chosen actions during play
- **Post-session Reports**: Detailed analysis of your strategic performance
- **Strategy Comparison**: Compare your strategy effectiveness against GTO
- **Improvement Recommendations**: Get specific suggestions for strategy refinement

## 📁 **Project Structure**

```
poker-strategy-system/
├── backend/
│   ├── core/                    # Core game logic
│   │   ├── poker_state_machine.py
│   │   ├── hand_evaluation.py
│   │   ├── position_mapping.py
│   │   └── gui_models.py
│   ├── ui/                      # User interface
│   │   ├── practice_session_ui.py
│   │   ├── practice_session_ui_api.py
│   │   ├── poker_practice_simulator.py
│   │   └── components/
│   │       ├── tier_panel.py
│   │       ├── decision_table_panel.py
│   │       ├── hand_grid.py
│   │       ├── tooltips.py
│   │       ├── postflop_hs_editor.py
│   │       ├── dialogs.py
│   │       └── dynamic_position_manager.py
│   ├── strategy/                 # Strategy management
│   │   └── strategy_optimization_panel.py
│   ├── analysis/                 # Analysis tools (future)
│   ├── data/                     # Strategy data
│   │   ├── modern_strategy.json
│   │   └── strategies/
│   │       ├── user_strategies/
│   │       ├── gto_strategies/
│   │       └── templates/
│   ├── utils/                    # Utilities
│   │   ├── pdf_export.py
│   │   └── sound_config.json
│   ├── sounds/                   # Audio files
│   ├── main_gui.py              # Main application entry
│   ├── main.py                  # CLI entry point
│   └── requirements.txt
├── tests/                        # Test suite
├── docs/                         # Documentation
└── README.md
```

## 🎯 **Usage Guide**

### **Starting a Practice Session**

1. **Launch the application**
   ```bash
   cd backend
   python3 main_gui.py
   ```

2. **Choose your practice mode**
   - **User Strategy**: Bots will play using your uploaded strategy
   - **GTO Strategy**: Bots will play using proven GTO strategy
   - **Mixed Mode**: Combination of both strategies

3. **Upload your strategy** (optional)
   - Use the strategy upload feature to load your custom strategy
   - Or practice with the default strategy

4. **Start playing**
   - Make your decisions based on your strategy
   - Receive real-time feedback on your choices
   - Review post-session analysis

### **Strategy Development**

1. **Create your strategy file**
   ```json
   {
     "strategy_name": "My Custom Strategy",
     "strategy_type": "user",
     "preflop": {
       "open_rules": {
         "UTG": {"threshold": 60, "sizing": 3.0},
         "MP": {"threshold": 55, "sizing": 3.0}
       },
       "vs_raise": {
         "UTG": {"value_thresh": 75, "call_thresh": 65, "sizing": 3.0}
       }
     }
   }
   ```

2. **Upload and test**
   - Upload your strategy file
   - Practice against it to test consistency
   - Compare performance against GTO

3. **Refine based on analysis**
   - Review post-session reports
   - Identify strategic weaknesses
   - Adjust your strategy accordingly

## 🔧 **Configuration**

### **Strategy Files**
- **Location**: `backend/data/strategies/`
- **Format**: JSON with position-based decision trees
- **Validation**: Automatic validation of strategy completeness

### **Audio Settings**
- **Location**: `backend/utils/sound_config.json`
- **Customization**: Modify sound mappings and voice announcements

### **Performance Tracking**
- **Session Data**: Automatically saved for analysis
- **Export Options**: PDF reports and JSON data export
- **Privacy**: All data stored locally

## 🛠️ **Development**

### **Running Tests**
```bash
cd tests
python3 run_all_tests.py
```

### **Adding New Features**
1. Follow the modular architecture
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

### **Strategy Engine Development**
- Core logic in `backend/core/`
- Strategy management in `backend/strategy/`
- Analysis tools in `backend/analysis/`

## 📊 **Performance Metrics**

The application tracks:
- **Win Rate**: Overall performance against different strategies
- **Decision Accuracy**: How often you follow your intended strategy
- **Strategic Effectiveness**: Performance in different situations
- **Improvement Trends**: Progress over time

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See `docs/` for detailed guides
- **Strategy Guide**: See `docs/STRATEGY_GUIDE.md` for strategy development help

---

**🎯 Goal**: Help poker players develop and refine their strategies through systematic practice and analysis against both their own strategies and proven GTO approaches. 