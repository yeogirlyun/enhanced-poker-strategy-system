#!/usr/bin/env python3
"""
Populate 100 Legendary Hands JSON Database

This script uses the generator functions to create all 100 hands
and save them to the JSON file.
"""

import json
import sys
import os

# Add backend directory to path
sys.path.append('.')

from tests.generate_100_hands import (
    generate_bad_beats, generate_hero_calls, generate_massive_bluffs,
    generate_cooler_hands, generate_wsop_championship_hands, generate_tv_hands,
    generate_heads_up_duels, generate_multi_way_pots, generate_slow_played_traps,
    generate_bubble_plays
)

def create_hand_id(category: str, index: int) -> str:
    """Create a unique hand ID."""
    category_prefix = {
        "Bad Beats": "BB",
        "Hero Calls": "HC", 
        "Massive Bluffs": "MB",
        "Cooler Hands": "CH",
        "WSOP Championship Hands": "WS",
        "Famous TV Hands": "TV",
        "Heads-Up Duels": "HU",
        "Multi-Way Pots": "MW",
        "Slow-Played Traps": "SP",
        "Bubble Plays": "BP"
    }
    prefix = category_prefix.get(category, "XX")
    return f"{prefix}{index:03d}"

def populate_100_hands():
    """Generate and save all 100 legendary hands."""
    print("🎯 Populating 100 Legendary Hands Database")
    print("=" * 50)
    
    # Generate all hands
    all_hands = []
    
    # Bad Beats (10 hands)
    bad_beats = generate_bad_beats()
    for i, hand in enumerate(bad_beats, 1):
        hand['id'] = create_hand_id("Bad Beats", i)
        all_hands.append(hand)
    
    # Hero Calls (10 hands)
    hero_calls = generate_hero_calls()
    for i, hand in enumerate(hero_calls, 1):
        hand['id'] = create_hand_id("Hero Calls", i)
        all_hands.append(hand)
    
    # Massive Bluffs (10 hands)
    massive_bluffs = generate_massive_bluffs()
    for i, hand in enumerate(massive_bluffs, 1):
        hand['id'] = create_hand_id("Massive Bluffs", i)
        all_hands.append(hand)
    
    # Cooler Hands (10 hands)
    cooler_hands = generate_cooler_hands()
    for i, hand in enumerate(cooler_hands, 1):
        hand['id'] = create_hand_id("Cooler Hands", i)
        all_hands.append(hand)
    
    # WSOP Championship Hands (10 hands)
    wsop_hands = generate_wsop_championship_hands()
    for i, hand in enumerate(wsop_hands, 1):
        hand['id'] = create_hand_id("WSOP Championship Hands", i)
        all_hands.append(hand)
    
    # Famous TV Hands (10 hands)
    tv_hands = generate_tv_hands()
    for i, hand in enumerate(tv_hands, 1):
        hand['id'] = create_hand_id("Famous TV Hands", i)
        all_hands.append(hand)
    
    # Heads-Up Duels (10 hands)
    heads_up_hands = generate_heads_up_duels()
    for i, hand in enumerate(heads_up_hands, 1):
        hand['id'] = create_hand_id("Heads-Up Duels", i)
        all_hands.append(hand)
    
    # Multi-Way Pots (10 hands)
    multi_way_hands = generate_multi_way_pots()
    for i, hand in enumerate(multi_way_hands, 1):
        hand['id'] = create_hand_id("Multi-Way Pots", i)
        all_hands.append(hand)
    
    # Slow-Played Traps (10 hands)
    slow_played_hands = generate_slow_played_traps()
    for i, hand in enumerate(slow_played_hands, 1):
        hand['id'] = create_hand_id("Slow-Played Traps", i)
        all_hands.append(hand)
    
    # Bubble Plays (10 hands)
    bubble_hands = generate_bubble_plays()
    for i, hand in enumerate(bubble_hands, 1):
        hand['id'] = create_hand_id("Bubble Plays", i)
        all_hands.append(hand)
    
    # Create the complete database structure
    database = {
        "metadata": {
            "title": "100 Legendary Poker Hands Database",
            "description": "Comprehensive collection of 100 legendary poker hands across 10 categories for testing, study, and simulation",
            "version": "1.0",
            "created": "2025-01-08",
            "total_hands": len(all_hands),
            "categories": [
                "Bad Beats",
                "Hero Calls", 
                "Massive Bluffs",
                "Cooler Hands",
                "WSOP Championship Hands",
                "Famous TV Hands",
                "Heads-Up Duels",
                "Multi-Way Pots",
                "Slow-Played Traps",
                "Bubble Plays"
            ]
        },
        "hands": all_hands
    }
    
    # Save to JSON file
    json_file_path = "tests/legendary_hands.json"
    try:
        with open(json_file_path, 'w') as f:
            json.dump(database, f, indent=2)
        
        print(f"✅ Successfully created {len(all_hands)} legendary hands")
        print(f"📁 Saved to: {json_file_path}")
        
        # Print summary
        categories = {}
        for hand in all_hands:
            category = hand['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print(f"\n📊 Hands per Category:")
        for category, count in categories.items():
            print(f"   {category}: {count} hands")
        
        print(f"\n🎯 Total: {len(all_hands)} hands across {len(categories)} categories")
        
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

if __name__ == "__main__":
    populate_100_hands()
