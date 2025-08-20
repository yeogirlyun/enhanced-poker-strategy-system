# Poker MVU Project

This is a complete MVU (Model-View-Update) implementation for a poker training application.

## Features

- Clean MVU architecture with immutable state
- Infinite loop prevention through proper equality checks
- Professional poker table rendering
- Hands review functionality

## Running the Application

```bash
cd poker_mvu_project
python main.py
```

## Architecture

The project follows strict MVU principles:
- Model: Immutable state representation
- View: Pure rendering components  
- Update: Pure state transition functions
- Commands: Side effects as data

## Key Components

- `ui/mvu/types.py` - Core type definitions
- `ui/mvu/update.py` - Pure update functions
- `ui/mvu/store.py` - State management
- `ui/mvu/view.py` - UI rendering
- `ui/mvu/hands_review_mvu.py` - Complete hands review implementation

This implementation prevents all common MVU pitfalls including infinite rendering loops.