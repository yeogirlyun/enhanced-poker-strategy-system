#!/usr/bin/env python3
"""
JSON Hands Database Loader

A specialized loader for our tested and validated JSON hands database.
This ensures the GUI uses our latest 130-hand collection that passed
all comprehensive tests.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Define needed classes directly (no longer dependent on hands_database module)

class HandCategory(Enum):
    """Hand categories for organization."""
    LEGENDARY = "legendary"
    PRACTICE = "practice"
    TAGGED = "tagged"


@dataclass
class HandMetadata:
    """Unified hand metadata for all hand types."""
    id: str
    name: str
    category: HandCategory
    subcategory: str
    source_file: str
    date: Optional[str] = None
    description: str = ""
    study_notes: str = ""
    difficulty_rating: int = 1


@dataclass
class ParsedHand:
    """Complete hand data with metadata and game information."""
    metadata: HandMetadata
    game_info: Dict[str, Any]
    players: List[Dict[str, Any]]
    actions: Dict[str, List[Dict[str, Any]]]
    board: Dict[str, Any]
    result: Dict[str, Any]
    raw_data: Dict[str, Any]


@dataclass
class JSONHandMetadata:
    """Metadata for JSON hands."""
    id: str
    name: str
    source: str = "json_database"
    created_at: str = "2024-01-01"
    hand_category: str = "legendary"
    description: str = ""
    lesson: str = ""


class JSONHandsDatabase:
    """Database loader for our validated JSON hands database."""
    
    def __init__(self, json_file_path: str = "data/legendary_hands_complete_130_fixed.json"):
        self.json_file_path = Path(json_file_path)
        self.hands: List[ParsedHand] = []
        self.raw_data: Dict[str, Any] = {}
    
    def load_all_hands(self) -> Dict[HandCategory, List[ParsedHand]]:
        """Load all hands from the JSON database."""
        hands_by_category = {
            HandCategory.LEGENDARY: [],
            HandCategory.PRACTICE: [],
            HandCategory.TAGGED: []
        }
        
        if not self.json_file_path.exists():
            print(f"❌ JSON hands database not found: {self.json_file_path}")
            return hands_by_category
        
        try:
            # Load JSON data
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            
            hands_data = self.raw_data.get('hands', [])
            print(f"📚 Loading {len(hands_data)} hands from JSON database...")
            
            # Convert each hand to ParsedHand format
            for hand_data in hands_data:
                parsed_hand = self._convert_json_hand(hand_data)
                if parsed_hand:
                    self.hands.append(parsed_hand)
                    hands_by_category[HandCategory.LEGENDARY].append(parsed_hand)
            
            print(f"✅ Successfully loaded {len(self.hands)} legendary hands from JSON")
            return hands_by_category
            
        except Exception as e:
            print(f"❌ Error loading JSON hands database: {e}")
            import traceback
            traceback.print_exc()
            return hands_by_category
    
    def _convert_json_hand(self, hand_data: Dict[str, Any]) -> Optional[ParsedHand]:
        """Convert JSON hand data to ParsedHand format."""
        try:
            # Extract basic info
            hand_id = hand_data.get('id', 'Unknown')
            hand_name = hand_data.get('name', 'Unknown Hand')
            
            # Create metadata
            metadata_dict = hand_data.get('metadata', {})
            lesson = metadata_dict.get('lesson', '')
            if not lesson and 'meta' in hand_data:
                lesson = hand_data['meta'].get('lesson', '')
            
            metadata = JSONHandMetadata(
                id=hand_id,
                name=hand_name,
                source="json_database",
                created_at=metadata_dict.get('created_at', '2024-01-01'),
                hand_category=metadata_dict.get('hand_category', 'legendary'),
                description=metadata_dict.get('description', f"Hand {hand_id}: {hand_name}"),
                lesson=lesson
            )
            
            # Convert to HandMetadata for compatibility
            hand_metadata = HandMetadata(
                id=hand_id,
                name=hand_name,
                category=HandCategory.LEGENDARY,
                subcategory=metadata.hand_category,
                source_file="json_database",
                date=metadata.created_at,
                description=metadata.description,
                study_notes=lesson,
                difficulty_rating=1
            )
            
            # Create ParsedHand
            parsed_hand = ParsedHand(
                metadata=hand_metadata,
                game_info=hand_data.get('game', {}),
                players=hand_data.get('players', []),
                actions=hand_data.get('actions', {}),
                board=hand_data.get('board', {}),
                result=hand_data.get('outcome', {}),
                raw_data=hand_data
            )
            
            return parsed_hand
            
        except Exception as e:
            print(f"❌ Error converting hand {hand_data.get('id', 'Unknown')}: {e}")
            return None
    
    def get_hand_data(self, hand_id: str) -> Optional[Dict[str, Any]]:
        """Get raw hand data by ID."""
        for hand in self.hands:
            if hand.metadata.id == hand_id:
                return hand.raw_data
        return None
    
    def get_hands_by_category(self) -> Dict[HandCategory, List[ParsedHand]]:
        """Get hands organized by category."""
        return self.load_all_hands()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database."""
        return {
            'file_path': str(self.json_file_path),
            'total_hands': len(self.hands),
            'format_version': self.raw_data.get('format_version', '2.0'),
            'created_at': self.raw_data.get('created_at', '2024-01-01'),
            'description': self.raw_data.get('description', 'JSON Hands Database'),
            'supported_variants': self.raw_data.get('supported_variants', ['No-Limit Hold\'em']),
            'supported_formats': self.raw_data.get('supported_formats', ['Cash Game', 'Tournament']),
            'special_features': self.raw_data.get('special_features', [])
        }


# For backward compatibility
class ComprehensiveJSONHandsDatabase(JSONHandsDatabase):
    """Alias for JSONHandsDatabase with comprehensive interface."""
    pass
