#!/usr/bin/env python3
"""
App Configuration

Central configuration for the poker training application.
"""

# App Configuration
APP_CONFIG = {
    "name": "PokerPro Trainer",
    "full_name": "PokerPro Trainer - Strategy Development System",
    "version": "3.0",
    "description": "Professional poker training with strategy development",
    "author": "PokerPro Development Team",
    "website": "https://pokerpro-trainer.com",
    
    # Window Configuration
    "window_size_percent": 0.6,  # 60% of screen size
    "min_window_width": 1200,
    "min_window_height": 800,
    
    # Theme Configuration
    "theme": {
        "primary_bg": "#2b2b2b",
        "secondary_bg": "#3c3c3c",
        "accent_primary": "#007acc",
        "accent_secondary": "#005a9e",
        "text": "#ffffff",
        "text_dark": "#cccccc",
        "border": "#555555",
        "widget_bg": "#404040"
    },
    
    # Sound Configuration
    "default_master_volume": 0.7,
    "default_category_volume": 0.8,
    "sound_enabled": True,
    "voice_enabled": True,
    
    # Game Configuration
    "default_starting_stack": 100,
    "default_blinds": (1, 2),
    "max_players": 9,
    "default_player_count": 6,
    
    # Strategy Configuration
    "default_strategy_file": "modern_strategy.json",
    "auto_save_enabled": True,
    "strategy_backup_enabled": True
}

# Available App Names (for easy switching)
AVAILABLE_APP_NAMES = {
    "PokerPro Trainer": {
        "full_name": "PokerPro Trainer - Strategy Development System",
        "description": "Professional poker training with strategy development"
    },
    "GTO Poker Studio": {
        "full_name": "GTO Poker Studio - Game Theory Optimal Training",
        "description": "Advanced GTO poker strategy development"
    },
    "Poker Strategy Lab": {
        "full_name": "Poker Strategy Lab - Research & Development",
        "description": "Laboratory for developing and testing poker strategies"
    },
    "Hold'em Academy": {
        "full_name": "Hold'em Academy - Comprehensive Learning Platform",
        "description": "Complete Texas Hold'em learning and training system"
    },
    "Poker Edge Builder": {
        "full_name": "Poker Edge Builder - Competitive Training",
        "description": "Building your edge in poker through strategy"
    }
}

def get_app_name():
    """Get the current app name."""
    return APP_CONFIG["name"]

def get_app_full_name():
    """Get the current full app name."""
    return APP_CONFIG["full_name"]

def set_app_name(name):
    """Set the app name (must be one of AVAILABLE_APP_NAMES)."""
    if name in AVAILABLE_APP_NAMES:
        APP_CONFIG["name"] = name
        APP_CONFIG["full_name"] = AVAILABLE_APP_NAMES[name]["full_name"]
        APP_CONFIG["description"] = AVAILABLE_APP_NAMES[name]["description"]
        return True
    return False

def get_available_app_names():
    """Get list of available app names."""
    return list(AVAILABLE_APP_NAMES.keys())

def print_app_config():
    """Print current app configuration."""
    print("🎯 APP CONFIGURATION")
    print("=" * 50)
    print(f"Name: {get_app_full_name()}")
    print(f"Version: {APP_CONFIG['version']}")
    print(f"Description: {APP_CONFIG['description']}")
    print(f"Author: {APP_CONFIG['author']}")
    print(f"Website: {APP_CONFIG['website']}")
    
    print(f"\n📋 AVAILABLE APP NAMES:")
    for name in get_available_app_names():
        info = AVAILABLE_APP_NAMES[name]
        print(f"  • {name}")
        print(f"    - {info['description']}")

if __name__ == "__main__":
    print_app_config() 