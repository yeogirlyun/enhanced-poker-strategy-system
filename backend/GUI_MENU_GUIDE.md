# Poker Strategy Development System - GUI Menu Guide

## Overview
The Poker Strategy Development System now features a comprehensive GUI with modern PFA/Caller postflop strategy and a complete menu system for strategy management.

## Menu System

### File Menu
- **New Strategy**: Creates a new strategy with default hand strength tiers
- **Load Strategy...**: Opens a file dialog to load an existing strategy file
- **Save Strategy**: Saves the current strategy to the last used file
- **Save Strategy As...**: Opens a file dialog to save with a new name
- **Generate Default Strategy**: Creates a new strategy with modern PFA/Caller theory
- **Exit**: Closes the application

### Help Menu
- **About**: Shows application information and version

## Key Features

### 1. Modern PFA/Caller Strategy
- **PFA (Position of Final Action)**: Aggressive betting with lower thresholds
- **Caller**: Defensive play with higher thresholds
- **Position-based adjustments**: UTG, MP, CO, BTN with appropriate values
- **Street progression**: Flop, Turn, River with increasing requirements

### 2. Three-Tab Interface
- **Hand Grid & Tiers**: Visual hand strength grid with tier management
- **Decision Tables**: Postflop decision table editor with PFA/Caller structure
- **Strategy Overview**: Comprehensive strategy summary and statistics

### 3. Strategy Management
- **Default Strategy Generation**: Creates modern theory-based strategies
- **File Operations**: Load, save, and manage strategy files
- **Real-time Updates**: All panels update when strategy changes

## Modern Strategy Values

### PFA (Aggressor) Values
- **Flop**: Lower thresholds (20-35), smaller sizing (0.5-0.75)
- **Turn**: Medium thresholds (30-40), medium sizing (0.55-0.75)
- **River**: Higher thresholds (35-45), larger sizing (0.7-1.0)

### Caller (Passive) Values
- **Flop**: Higher thresholds (30-40), larger sizing (0.6-0.8)
- **Turn**: Higher thresholds (35-45), larger sizing (0.7-0.9)
- **River**: Highest thresholds (40-50), largest sizing (0.9-1.2)

## Position Adjustments
- **UTG**: Most conservative (highest thresholds)
- **MP**: Slightly more aggressive
- **CO**: More aggressive
- **BTN**: Most aggressive (lowest thresholds)

## Usage Workflow

### Creating a New Strategy
1. Use **File → Generate Default Strategy** to create a modern strategy
2. Edit hand strength tiers in the "Hand Grid & Tiers" tab
3. Adjust postflop decision tables in the "Decision Tables" tab
4. Use **File → Save Strategy As...** to save your work

### Loading and Editing
1. Use **File → Load Strategy...** to open an existing file
2. Make your changes across all tabs
3. Use **File → Save Strategy** to save changes

### Strategy Overview
- View comprehensive strategy information in the "Strategy Overview" tab
- See hand strength tiers, postflop strategy type, and statistics
- Monitor total hands, tiers, and supported positions

## Benefits Over CLI
- **Visual Editing**: See all data in organized tables
- **Real-time Updates**: Changes reflect immediately across all panels
- **Modern Theory**: Built-in PFA/Caller concept with modern values
- **File Management**: Integrated save/load with file dialogs
- **User-Friendly**: No command-line knowledge required

## Technical Details
- **Framework**: Python with Tkinter
- **Data Format**: JSON strategy files
- **Architecture**: Modular design with separate panels
- **Styling**: Dark theme with sky blue accents
- **Responsive**: Font size and grid size controls

## Migration from CLI
The old CLI tool (`strategy_manager.py`) has been removed. All functionality is now available through the GUI:
- **Create**: Use "Generate Default Strategy" menu option
- **Load**: Use "Load Strategy..." menu option
- **Save**: Use "Save Strategy" or "Save Strategy As..." menu options
- **Edit**: Use the visual editors in each tab
- **View**: Use the "Strategy Overview" tab

The GUI provides a more intuitive and comprehensive experience for strategy development. 