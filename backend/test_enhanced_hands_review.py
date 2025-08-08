#!/usr/bin/env python3
"""
Test Enhanced Hands Review System

Tests the new comprehensive hands review system with:
- Legendary hands PHH loading
- Practice session hands integration
- User tagging system
- Hand simulation capabilities
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

from core.hands_database import (
    ComprehensiveHandsDatabase, LegendaryHandsPHHLoader, 
    UserTaggedHandsManager, HandCategory, HandMetadata, ParsedHand
)


class TestEnhancedHandsReview(unittest.TestCase):
    """Test the enhanced hands review system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test PHH file for legendary hands
        self.test_phh_file = os.path.join(self.temp_dir, "test_legendary.phh")
        self.create_test_phh_file()
        
        # Create test tags file
        self.tags_file = os.path.join(self.temp_dir, "test_tags.json")
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_phh_file(self):
        """Create a test PHH file with sample legendary hands."""
        phh_content = """# Test Legendary Hands PHH File

# Hand 1 — Test Epic Bluff (Phil Ivey vs Tom Dwan)
[hand.meta]
category = "Epic Bluffs"
id = "test_epic_1"

[game]
variant = "No-Limit Hold'em"
stakes = "200/400/0"
currency = "USD"
format = "Cash Game"
event = "High Stakes Poker TV Show"
date = "2008-03-15"

[table]
table_name = "Test Table"
max_players = 6
button_seat = 1

[[players]]
seat = 1
name = "Phil Ivey"
position = "Button"
starting_stack_chips = 80000
cards = ["7h","2d"]

[[players]]
seat = 2
name = "Tom Dwan"
position = "Small Blind"
starting_stack_chips = 120000
cards = ["Ah","Kh"]

[blinds]
small_blind = { seat = 2, amount = 200 }
big_blind   = { seat = 3, amount = 400 }

[[actions.preflop]]
actor = 1
type = "raise"
to = 1200

[[actions.preflop]]
actor = 2
type = "call"
amount = 1000

[board.flop]
cards = ["As","Kd","9h"]

[[actions.flop]]
actor = 2
type = "check"

[[actions.flop]]
actor = 1
type = "bet"
amount = 1800

[[actions.flop]]
actor = 2
type = "call"
amount = 1800

[board.turn]
card = "3c"

[[actions.turn]]
actor = 2
type = "check"

[[actions.turn]]
actor = 1
type = "bet"
amount = 4500

[[actions.turn]]
actor = 2
type = "call"
amount = 4500

[board.river]
card = "Qd"

[[actions.river]]
actor = 2
type = "check"

[[actions.river]]
actor = 1
type = "bet"
amount = 12000

[[actions.river]]
actor = 2
type = "fold"

[result]
winner = "Phil Ivey"
pot_size = 16000
winning_hand = "Bluff"

# Hand 2 — Test Bad Beat (Aces vs Kings)
[hand.meta]
category = "Bad Beats"
id = "test_badbeat_1"

[game]
variant = "No-Limit Hold'em"
stakes = "100/200/0"
currency = "USD"
format = "Cash Game"
event = "Test Session"
date = "2023-12-01"

[[players]]
seat = 1
name = "Player A"
starting_stack_chips = 20000
cards = ["Ac","Ad"]

[[players]]
seat = 2
name = "Player B"
starting_stack_chips = 20000
cards = ["Kc","Kd"]

[result]
winner = "Player B"
pot_size = 40000
winning_hand = "Set of Kings"
"""
        
        with open(self.test_phh_file, 'w') as f:
            f.write(phh_content)
    
    def test_legendary_hands_phh_loader(self):
        """Test loading legendary hands from PHH file."""
        loader = LegendaryHandsPHHLoader(self.test_phh_file)
        hands = loader.load_hands()
        
        # Should load 2 hands
        self.assertEqual(len(hands), 2)
        
        # Check first hand
        hand1 = hands[0]
        self.assertIsInstance(hand1, ParsedHand)
        self.assertEqual(hand1.metadata.category, HandCategory.LEGENDARY)
        self.assertIn("Phil Ivey", hand1.metadata.name)
        self.assertEqual(len(hand1.metadata.players_involved), 2)
        self.assertIn("Phil Ivey", hand1.metadata.players_involved)
        self.assertIn("Tom Dwan", hand1.metadata.players_involved)
        
        # Check game info
        self.assertEqual(hand1.game_info.get('variant'), 'No-Limit Hold\'em')
        self.assertEqual(hand1.game_info.get('event'), 'High Stakes Poker TV Show')
        
        print("✅ Legendary hands PHH loader test passed")
    
    def test_user_tagged_hands_manager(self):
        """Test the user tagging system."""
        tags_manager = UserTaggedHandsManager(self.tags_file)
        
        # Tag a hand
        hand_id = "test_hand_123"
        tags = ["hero_call", "difficult", "review_needed"]
        notes = "Great example of thin value betting"
        
        tags_manager.tag_hand(hand_id, tags, notes, is_favorite=True, difficulty=4)
        
        # Verify tags were saved
        hand_tags = tags_manager.get_hand_tags(hand_id)
        self.assertEqual(hand_tags['tags'], tags)
        self.assertEqual(hand_tags['notes'], notes)
        self.assertTrue(hand_tags['is_favorite'])
        self.assertEqual(hand_tags['difficulty'], 4)
        
        # Test getting hands by tag
        hero_call_hands = tags_manager.get_hands_by_tag("hero_call")
        self.assertIn(hand_id, hero_call_hands)
        
        # Test getting all tags
        all_tags = tags_manager.get_all_tags()
        self.assertTrue(all_tags.issuperset(set(tags)))
        
        # Mark as reviewed
        tags_manager.mark_reviewed(hand_id)
        updated_tags = tags_manager.get_hand_tags(hand_id)
        self.assertIsNotNone(updated_tags.get('last_reviewed'))
        self.assertEqual(updated_tags.get('review_count'), 1)
        
        print("✅ User tagged hands manager test passed")
    
    def test_comprehensive_hands_database(self):
        """Test the comprehensive hands database."""
        # Create test practice hands directory
        practice_dir = os.path.join(self.temp_dir, "practice_hands")
        os.makedirs(practice_dir, exist_ok=True)
        
        # Create test practice metadata file
        practice_metadata = {
            "session_info": {
                "session_id": "test_session_456",
                "start_time": 1700000000.0,
                "hands_played": 1
            },
            "hands": [
                {
                    "id": "practice_test_456_1",
                    "name": "Practice Hand 1",
                    "category": "Practice Hands",
                    "hand_number": 1,
                    "pot_size": 25.0,
                    "hand_complete": True,
                    "players_involved": ["Player 1", "Player 2"],
                    "session_date": "2023-11-15 12:30",
                    "description": "Practice session hand"
                }
            ]
        }
        
        metadata_file = os.path.join(practice_dir, "practice_metadata_20231115_123000_test456.json")
        with open(metadata_file, 'w') as f:
            json.dump(practice_metadata, f, indent=2)
        
        # Initialize database
        db = ComprehensiveHandsDatabase(
            legendary_phh_path=self.test_phh_file,
            practice_hands_dir=practice_dir,
            tags_file=self.tags_file
        )
        
        # Load all hands
        hands_by_category = db.load_all_hands()
        
        # Check legendary hands
        legendary_hands = hands_by_category[HandCategory.LEGENDARY]
        self.assertEqual(len(legendary_hands), 2)
        self.assertEqual(legendary_hands[0].metadata.category, HandCategory.LEGENDARY)
        
        # Check practice hands
        practice_hands = hands_by_category[HandCategory.PRACTICE]
        self.assertEqual(len(practice_hands), 1)
        self.assertEqual(practice_hands[0].metadata.category, HandCategory.PRACTICE)
        self.assertEqual(practice_hands[0].metadata.name, "Practice Hand 1")
        
        # Test search functionality
        search_results = db.search_hands("Phil Ivey")
        self.assertEqual(len(search_results), 1)
        self.assertIn("Phil Ivey", search_results[0].metadata.name)
        
        # Test category stats
        stats = db.get_category_stats()
        self.assertIn('legendary', stats)
        self.assertIn('practice', stats)
        self.assertEqual(stats['legendary']['total_hands'], 2)
        self.assertEqual(stats['practice']['total_hands'], 1)
        
        print("✅ Comprehensive hands database test passed")
    
    def test_hand_tagging_integration(self):
        """Test integration between database and tagging system."""
        # Create database with test data
        practice_dir = os.path.join(self.temp_dir, "practice_hands")
        os.makedirs(practice_dir, exist_ok=True)
        
        db = ComprehensiveHandsDatabase(
            legendary_phh_path=self.test_phh_file,
            practice_hands_dir=practice_dir,
            tags_file=self.tags_file
        )
        
        hands_by_category = db.load_all_hands()
        
        # Tag a legendary hand
        legendary_hand = hands_by_category[HandCategory.LEGENDARY][0]
        hand_id = legendary_hand.metadata.id
        
        db.tags_manager.tag_hand(
            hand_id, 
            ["epic_bluff", "high_stakes", "ivey"], 
            "Classic Ivey bluff with 7-2 offsuit",
            is_favorite=True,
            difficulty=5
        )
        
        # Reload to check tagged hands category
        hands_by_category = db.load_all_hands()
        tagged_hands = hands_by_category[HandCategory.TAGGED]
        
        # Should have 1 tagged hand
        self.assertEqual(len(tagged_hands), 1)
        
        # Check the tagged hand has updated metadata
        tagged_hand = tagged_hands[0]
        self.assertTrue(tagged_hand.metadata.is_favorite)
        self.assertEqual(tagged_hand.metadata.difficulty_rating, 5)
        self.assertIn("epic_bluff", tagged_hand.metadata.tags)
        
        # Test getting hands by specific tag
        bluff_hands = db.get_hands_by_tag("epic_bluff")
        self.assertEqual(len(bluff_hands), 1)
        self.assertEqual(bluff_hands[0].metadata.id, hand_id)
        
        print("✅ Hand tagging integration test passed")
    
    def test_phh_parsing_robustness(self):
        """Test PHH parsing with various formats and edge cases."""
        # Create PHH with minimal data
        minimal_phh = """# Minimal hand
[hand.meta]
id = "minimal_1"

[game]
variant = "No-Limit Hold'em"

[[players]]
name = "Player 1"

[result]
winner = "Player 1"
"""
        
        minimal_file = os.path.join(self.temp_dir, "minimal.phh")
        with open(minimal_file, 'w') as f:
            f.write(minimal_phh)
        
        loader = LegendaryHandsPHHLoader(minimal_file)
        hands = loader.load_hands()
        
        # Should still parse successfully
        self.assertEqual(len(hands), 1)
        hand = hands[0]
        self.assertEqual(hand.metadata.id, "minimal_1")
        self.assertEqual(hand.metadata.category, HandCategory.LEGENDARY)
        
        print("✅ PHH parsing robustness test passed")


def run_tests():
    """Run all enhanced hands review tests."""
    print("🔄 Running Enhanced Hands Review Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedHandsReview)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All enhanced hands review tests passed!")
        print(f"Tests run: {result.testsRun}")
        return True
    else:
        print("❌ Some tests failed!")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        # Print failure details
        for test, error in result.failures + result.errors:
            print(f"\n❌ {test}: {error}")
        
        return False


if __name__ == "__main__":
    run_tests()
