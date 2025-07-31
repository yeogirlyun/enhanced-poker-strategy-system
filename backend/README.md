# Poker Strategy Development System (GUI Version)

A comprehensive GUI-based poker strategy development and practice system with visual poker table simulation.

## Features

- **Visual Poker Table** - Professional-looking poker table with player positions and cards
- **Strategy Development** - Hand grid editor with tier-based strategy management
- **Postflop HS Editor** - Advanced postflop hand strength editing
- **Strategy Optimization** - Automated strategy optimization tools
- **Practice Session** - Visual poker practice against strategy-based bots
- **State Machine Architecture** - Robust, predictable game flow
- **Strategy-Based Bots** - AI bots that follow loaded strategy files

## Components

### Main GUI (`main_gui.py`)
- Tabbed interface for all poker strategy tools
- Font size and grid size controls
- Strategy file management

### Hand Grid & Tiers (`hand_grid.py`, `tier_panel.py`)
- Visual hand grid editor
- Tier-based strategy organization
- Hand strength evaluation

### Postflop HS Editor (`postflop_hs_editor.py`)
- Advanced postflop hand strength editing
- Position-based decision tables
- Betting strategy configuration

### Strategy Optimization (`strategy_optimization_panel.py`, `simple_optimizer.py`)
- Automated strategy optimization
- Performance analysis tools
- Strategy validation

### Practice Session (`enhanced_visual_poker_table.py`)
- Visual poker table simulation
- Real-time game state display
- Strategy-based bot decisions
- Human practice mode

### Core Engine (`poker_state_machine.py`, `gui_models.py`)
- State machine for game flow
- Strategy data management
- Game state handling

## Files

### Core Files
- `main_gui.py` - Main application window
- `enhanced_visual_poker_table.py` - Visual poker table
- `poker_state_machine.py` - Game state machine
- `gui_models.py` - Strategy data models

### Strategy Development
- `hand_grid.py` - Hand grid editor
- `tier_panel.py` - Tier management
- `postflop_hs_editor.py` - Postflop editor
- `strategy_optimization_panel.py` - Optimization tools

### UI Components
- `dialogs.py` - Dialog boxes
- `decision_table_panel.py` - Decision table editor
- `pdf_export.py` - PDF report generation

### Data Files
- `modern_strategy.json` - Strategy file
- `strategy.json` - Alternative strategy file

## Usage

### Starting the Application
```bash
python3 main_gui.py
```

### Features
- **Hand Grid & Tiers** - Edit poker hand strategies
- **Postflop HS Editor** - Configure postflop decisions
- **Strategy Optimization** - Optimize strategies automatically
- **Practice Session** - Practice against strategy-based bots

## Architecture

### State Machine
- Clean, predictable game flow
- Proper Texas Hold'em rules implementation
- Strategy-based bot decisions

### GUI Framework
- Tkinter-based interface
- Responsive design
- Professional styling

### Strategy Integration
- JSON-based strategy files
- Tier-based organization
- Position-aware decisions

## Development

### Dependencies
- Python 3.7+
- Tkinter (usually included with Python)
- No external dependencies required

### Testing
- Visual testing through GUI
- Strategy validation tools
- Practice session debugging

## Related Projects

- **CLI Poker Game** - Separate command-line version for debugging
- **Strategy Analysis** - Tools for strategy evaluation

## License

This is a development tool for poker strategy practice and analysis. 