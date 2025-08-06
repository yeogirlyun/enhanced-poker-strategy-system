#!/usr/bin/env python3
"""
App Name Suggestions for Poker Strategy Development System

Professional names for the poker training and strategy application.
"""

# Professional App Names
APP_NAME_SUGGESTIONS = {
    "PokerPro Trainer": {
        "description": "Professional poker training with strategy development",
        "style": "Modern, professional, emphasizes training aspect",
        "best_for": "Main app name"
    },
    "GTO Poker Studio": {
        "description": "Game Theory Optimal poker strategy development",
        "style": "Technical, advanced, emphasizes GTO concepts",
        "best_for": "Advanced users"
    },
    "Poker Strategy Lab": {
        "description": "Laboratory for developing and testing poker strategies",
        "style": "Scientific, research-oriented, experimental",
        "best_for": "Strategy development focus"
    },
    "Hold'em Academy": {
        "description": "Comprehensive Texas Hold'em learning platform",
        "style": "Educational, comprehensive, academy-style",
        "best_for": "Learning and education focus"
    },
    "Poker Edge Builder": {
        "description": "Building your edge in poker through strategy",
        "style": "Competitive, edge-focused, improvement-oriented",
        "best_for": "Competitive players"
    },
    "Strategy Poker Pro": {
        "description": "Professional poker strategy development tool",
        "style": "Professional, strategy-focused, comprehensive",
        "best_for": "Professional use"
    },
    "Poker Mastermind": {
        "description": "Master poker strategy and decision making",
        "style": "Intellectual, mastery-focused, advanced",
        "best_for": "Advanced strategy development"
    },
    "Hold'em Strategy Suite": {
        "description": "Complete suite of poker strategy tools",
        "style": "Comprehensive, suite-style, professional",
        "best_for": "Complete solution"
    },
    "Poker Decision Lab": {
        "description": "Laboratory for improving poker decision making",
        "style": "Decision-focused, analytical, improvement",
        "best_for": "Decision making focus"
    },
    "GTO Poker Trainer": {
        "description": "Game Theory Optimal poker training system",
        "style": "GTO-focused, training-oriented, modern",
        "best_for": "GTO training"
    }
}

# Top Recommendations
TOP_RECOMMENDATIONS = [
    "PokerPro Trainer",
    "GTO Poker Studio", 
    "Poker Strategy Lab",
    "Hold'em Academy",
    "Poker Edge Builder"
]

def print_name_suggestions():
    """Print all app name suggestions with details."""
    print("🎯 APP NAME SUGGESTIONS")
    print("=" * 50)
    
    print("\n🏆 TOP RECOMMENDATIONS:")
    for i, name in enumerate(TOP_RECOMMENDATIONS, 1):
        info = APP_NAME_SUGGESTIONS[name]
        print(f"{i}. {name}")
        print(f"   Description: {info['description']}")
        print(f"   Style: {info['style']}")
        print(f"   Best for: {info['best_for']}")
        print()
    
    print("\n📋 ALL SUGGESTIONS:")
    for name, info in APP_NAME_SUGGESTIONS.items():
        print(f"• {name}")
        print(f"  - {info['description']}")
        print(f"  - {info['style']}")
        print()

if __name__ == "__main__":
    print_name_suggestions() 