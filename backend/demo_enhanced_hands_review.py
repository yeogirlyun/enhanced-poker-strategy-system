#!/usr/bin/env python3
"""
Demo: Enhanced Hands Review System

This demo showcases the new comprehensive hands review system with:
- Loading legendary hands from PHH files
- Practice session hands integration  
- User tagging and categorization
- Hand analysis capabilities
"""

import os
import json
import tempfile
from pathlib import Path

from core.hands_database import (
    ComprehensiveHandsDatabase, HandCategory, UserTaggedHandsManager
)


def demo_hands_database():
    """Demonstrate the hands database functionality."""
    print("🎯 Enhanced Hands Review System Demo")
    print("=" * 50)
    
    # Initialize the database with real data
    db = ComprehensiveHandsDatabase(
        legendary_phh_path="data/legendary_hands.phh",
        practice_hands_dir="logs/practice_hands",
        tags_file="logs/user_hand_tags.json"
    )
    
    print("📂 Loading hands from all sources...")
    hands_by_category = db.load_all_hands()
    
    # Display category statistics
    print("\n📊 Category Statistics:")
    stats = db.get_category_stats()
    
    for category_name, category_stats in stats.items():
        print(f"\n🏷️  {category_name.title()}:")
        print(f"   • Total hands: {category_stats['total_hands']}")
        print(f"   • Average pot: ${category_stats['avg_pot_size']:.0f}")
        print(f"   • Favorites: {category_stats['favorites']}")
        print(f"   • Unique tags: {category_stats['unique_tags']}")
        print(f"   • Avg difficulty: {category_stats['avg_difficulty']:.1f}/5")
    
    # Show legendary hands
    legendary_hands = hands_by_category[HandCategory.LEGENDARY]
    if legendary_hands:
        print(f"\n🏆 Sample Legendary Hands ({len(legendary_hands)} total):")
        for i, hand in enumerate(legendary_hands[:3]):  # Show first 3
            print(f"   {i+1}. {hand.metadata.name}")
            print(f"      Category: {hand.metadata.subcategory}")
            print(f"      Players: {', '.join(hand.metadata.players_involved)}")
            print(f"      Pot: ${hand.metadata.pot_size:.0f}")
            if hand.metadata.event:
                print(f"      Event: {hand.metadata.event}")
            print()
    
    # Show practice hands if any
    practice_hands = hands_by_category[HandCategory.PRACTICE]
    if practice_hands:
        print(f"\n📚 Practice Hands ({len(practice_hands)} total):")
        for i, hand in enumerate(practice_hands[:3]):
            print(f"   {i+1}. {hand.metadata.name}")
            print(f"      Date: {hand.metadata.date}")
            print(f"      Pot: ${hand.metadata.pot_size:.2f}")
    else:
        print("\n📚 No practice hands found (run a practice session to generate some!)")
    
    # Demonstrate tagging system
    if legendary_hands:
        print("\n🏷️  Demonstrating Tagging System:")
        sample_hand = legendary_hands[0]
        
        # Tag the hand
        db.tags_manager.tag_hand(
            sample_hand.metadata.id,
            ["high_stakes", "legendary_bluff", "must_study"],
            "Classic example of high-level play. Great for studying pressure situations.",
            is_favorite=True,
            difficulty=5
        )
        
        print(f"   ✅ Tagged hand: {sample_hand.metadata.name}")
        print(f"   🏷️  Tags: high_stakes, legendary_bluff, must_study")
        print(f"   ⭐ Marked as favorite")
        print(f"   📊 Difficulty: 5/5")
        
        # Show tagged hands
        tagged_hands = db.get_hands_by_tag("high_stakes")
        print(f"   📋 Found {len(tagged_hands)} hands with 'high_stakes' tag")
    
    # Demonstrate search functionality
    if legendary_hands:
        print("\n🔍 Search Functionality:")
        search_results = db.search_hands("Dwan")
        print(f"   • Search for 'Dwan': {len(search_results)} results")
        
        for hand in search_results[:2]:
            print(f"     - {hand.metadata.name}")
        
        search_results = db.search_hands("Blom")
        print(f"   • Search for 'Blom': {len(search_results)} results")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nThe enhanced hands review system provides:")
    print("• 🏆 Legendary hands from PHH files")
    print("• 📚 Practice session hands (auto-exported)")
    print("• 🏷️  User tagging and categorization")
    print("• 🔍 Search and filtering capabilities")
    print("• 📊 Statistics and analysis")
    print("• 🎮 Hand simulation (in UI)")
    
    return db


def demo_ui_integration():
    """Show how the UI would integrate with the system."""
    print("\n🖥️  UI Integration Preview:")
    print("=" * 30)
    
    print("""
📱 Enhanced Hands Review Panel Structure:

┌─────────────────────────────────────────────────────────┐
│ 🎯 Hands Review Center                                   │
├─────────────────────────────────────────────────────────┤
│ 📂 Categories                                           │
│ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐ │
│ │ 🏆 Legendary    │ │ 📚 Practice     │ │ 🏷️ Tagged    │ │
│ │    Hands        │ │    Sessions     │ │   Important  │ │
│ └─────────────────┘ └─────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 🔍 Search & Filter                                      │
│ Search: [____________] 🔍  Tag: [All Tags ▼] [Clear]    │
├─────────────────────────────────────────────────────────┤
│ 📋 Hands List                        │ 🎮 Hand Simulation│
│ • 🏆 Viktor vs Tom Dwan $15K ⭐       │                   │
│ • 🏆 Phil Ivey Epic Bluff            │ [Hand details and │
│ • 📚 Practice Hand 1 $25             │  step-by-step     │
│ • 🏷️ Hero Call Study [review_needed] │  replay with      │
│                                      │  analysis tools]  │
│ [🏷️ Tag] [⭐ Fav] [🔄 Refresh]       │                   │
└─────────────────────────────────────────────────────────┘

Key Features:
• Three main categories with visual indicators
• Advanced search and tag filtering
• Drag-and-drop tagging interface
• Integrated hand simulation and analysis
• Favorite marking and difficulty ratings
• Study notes and review tracking
""")


if __name__ == "__main__":
    # Run the demo
    try:
        db = demo_hands_database()
        demo_ui_integration()
        
        print(f"\n📁 Database initialized with:")
        print(f"   • Legendary hands file: data/legendary_hands.phh")
        print(f"   • Practice hands directory: logs/practice_hands/")
        print(f"   • User tags file: logs/user_hand_tags.json")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure data/legendary_hands.phh exists and is properly formatted.")
