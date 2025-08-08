#!/usr/bin/env python3
"""
Comprehensive Hands Database Manager

This module provides a unified interface for managing all types of poker hands:
- Legendary hands from PHH files
- Practice session hands (exported to PHH)
- User-tagged/important hands with custom labels

Features:
- TOML/PHH parsing for legendary hands
- Integration with practice session PHH files
- User tagging system with custom labels
- Unified hand data model for consistent UI display
- Search and filtering capabilities
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .phh_converter import PracticeHandsPHHManager


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
    subcategory: str  # e.g., "Epic Bluffs", "Practice Session", "Hero Call"
    source_file: str
    date: Optional[str] = None
    event: Optional[str] = None
    players_involved: List[str] = field(default_factory=list)
    pot_size: float = 0.0
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    is_favorite: bool = False
    difficulty_rating: int = 1  # 1-5 scale
    study_notes: str = ""
    last_reviewed: Optional[str] = None


@dataclass
class ParsedHand:
    """Complete hand data with metadata and game information."""
    metadata: HandMetadata
    game_info: Dict[str, Any]
    players: List[Dict[str, Any]]
    actions: Dict[str, List[Dict[str, Any]]]  # by street
    board: Dict[str, Any]  # flop, turn, river
    result: Dict[str, Any]
    raw_data: Dict[str, Any]  # Original parsed data


class LegendaryHandsPHHLoader:
    """Loader for legendary hands in PHH/TOML format."""
    
    def __init__(self, phh_file_path: str):
        self.phh_file_path = Path(phh_file_path)
        self.hands: List[ParsedHand] = []
    
    def load_hands(self) -> List[ParsedHand]:
        """Load and parse legendary hands from PHH file."""
        if not self.phh_file_path.exists():
            return []
        
        try:
            # Parse the PHH file as TOML-like structure
            hands = self._parse_phh_file()
            self.hands = hands
            return hands
        except Exception as e:
            print(f"Error loading legendary hands: {e}")
            return []
    
    def _parse_phh_file(self) -> List[ParsedHand]:
        """Parse PHH file with simplified structure parsing."""
        hands = []
        
        with open(self.phh_file_path, 'r') as f:
            content = f.read()
        
        # For now, create simplified hands from the PHH file
        # This is a basic implementation - can be enhanced later
        hands = self._create_simplified_hands_from_phh(content)
        
        return hands
    
    def _create_simplified_hands_from_phh(self, content: str) -> List[ParsedHand]:
        """Create simplified hands from PHH content."""
        hands = []
        lines = content.split('\n')
        
        current_hand = None
        hand_counter = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Detect start of new hand
            if stripped.startswith('# Hand ') and '—' in stripped:
                # Save previous hand if exists
                if current_hand:
                    hands.append(current_hand)
                
                # Start new hand
                hand_counter += 1
                hand_name = stripped.split('—', 1)[1].strip() if '—' in stripped else f"Legendary Hand {hand_counter}"
                
                # Extract players from name more robustly
                players_involved = []
                if ' vs ' in hand_name:
                    player_parts = hand_name.split(' vs ')
                    for part in player_parts:
                        # Clean up player names (remove quotes, parentheses, and extra info)
                        clean_name = part.split('(')[0].strip().strip('"').strip()
                        # Remove common prefixes/suffixes
                        if clean_name and not clean_name.startswith('('):
                            players_involved.append(clean_name)
                elif '(' in hand_name and ')' in hand_name:
                    # Try to extract from parentheses format
                    parts = hand_name.replace('(', ' vs ').replace(')', '').split(' vs ')
                    for part in parts:
                        clean_name = part.strip().strip('"')
                        if clean_name and len(clean_name) > 2:
                            players_involved.append(clean_name)
                
                metadata = HandMetadata(
                    id=f"legendary_{hand_counter}",
                    name=hand_name,
                    category=HandCategory.LEGENDARY,
                    subcategory="Legendary Hands",
                    source_file=str(self.phh_file_path),
                    players_involved=players_involved,
                    pot_size=0.0,  # Will be estimated
                    description=f"Legendary hand from {self.phh_file_path.name}",
                    difficulty_rating=4
                )
                
                current_hand = ParsedHand(
                    metadata=metadata,
                    game_info={},
                    players=[],
                    actions={},
                    board={},
                    result={},
                    raw_data={}
                )
            
            # Extract category information
            elif stripped.startswith('category =') and current_hand:
                category = stripped.split('=', 1)[1].strip().strip('"')
                current_hand.metadata.subcategory = category
            
            # Extract game information
            elif stripped.startswith('variant =') and current_hand:
                variant = stripped.split('=', 1)[1].strip().strip('"')
                current_hand.game_info['variant'] = variant
            elif stripped.startswith('date =') and current_hand:
                date = stripped.split('=', 1)[1].strip().strip('"')
                current_hand.metadata.date = date
            elif stripped.startswith('event =') and current_hand:
                event = stripped.split('=', 1)[1].strip().strip('"')
                current_hand.metadata.event = event
                current_hand.game_info['event'] = event
            elif stripped.startswith('stakes =') and current_hand:
                stakes = stripped.split('=', 1)[1].strip().strip('"')
                current_hand.game_info['stakes'] = stakes
                # Estimate pot size from stakes
                if '/' in stakes:
                    try:
                        parts = stakes.split('/')
                        if len(parts) >= 2:
                            big_blind = float(parts[1])
                            current_hand.metadata.pot_size = big_blind * 15  # Rough estimate
                    except:
                        pass
        
        # Add final hand
        if current_hand:
            hands.append(current_hand)
        
        return hands
    
    def _split_into_hand_blocks(self, content: str) -> List[str]:
        """Split PHH content into individual hand blocks."""
        # Look for hand boundaries (typically marked by [hand.meta] or similar)
        lines = content.split('\n')
        blocks = []
        current_block = []
        in_hand = False
        
        for line in lines:
            stripped = line.strip()
            
            # Start of new hand
            if stripped.startswith('[hand.meta]') or stripped.startswith('# Hand '):
                if current_block and in_hand:
                    blocks.append('\n'.join(current_block))
                current_block = [line]
                in_hand = True
            elif in_hand:
                current_block.append(line)
                # End hand on next hand start or file end
        
        # Add final block
        if current_block and in_hand:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _parse_hand_block(self, block: str, hand_index: int) -> Optional[ParsedHand]:
        """Parse a single hand block into ParsedHand."""
        try:
            # Extract hand information from the block
            lines = block.split('\n')
            
            # Initialize hand data
            hand_data = {
                'meta': {},
                'game': {},
                'players': [],
                'actions': {},
                'board': {},
                'result': {}
            }
            
            # Parse line by line
            current_section = None
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Section headers
                if stripped.startswith('[') and stripped.endswith(']'):
                    section = stripped[1:-1]
                    if '.' in section:
                        main_section, sub_section = section.split('.', 1)
                        current_section = (main_section, sub_section)
                    else:
                        current_section = (section, None)
                    continue
                
                # Parse key-value pairs and arrays
                if '=' in stripped:
                    key, value = stripped.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to parse as Python literal (for lists, dicts)
                    try:
                        parsed_value = eval(value)
                    except:
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            parsed_value = value[1:-1]
                        else:
                            parsed_value = value
                    
                    # Store in appropriate section
                    if current_section:
                        main_section, sub_section = current_section
                        if main_section not in hand_data:
                            hand_data[main_section] = {}
                        
                        if sub_section:
                            if sub_section not in hand_data[main_section]:
                                hand_data[main_section][sub_section] = {}
                            hand_data[main_section][sub_section][key] = parsed_value
                        else:
                            hand_data[main_section][key] = parsed_value
            
            # Create metadata
            meta = hand_data.get('meta', {})
            game = hand_data.get('game', {})
            
            metadata = HandMetadata(
                id=meta.get('id', f'legendary_{hand_index}'),
                name=self._extract_hand_name(block, hand_index),
                category=HandCategory.LEGENDARY,
                subcategory=meta.get('category', 'Legendary Hands'),
                source_file=str(self.phh_file_path),
                date=game.get('date'),
                event=game.get('event'),
                players_involved=self._extract_player_names(hand_data.get('players', [])),
                pot_size=self._estimate_pot_size(hand_data),
                description=self._create_description(hand_data),
                difficulty_rating=4  # Legendary hands are typically difficult
            )
            
            # Create ParsedHand
            parsed_hand = ParsedHand(
                metadata=metadata,
                game_info=game,
                players=hand_data.get('players', []),
                actions=hand_data.get('actions', {}),
                board=hand_data.get('board', {}),
                result=hand_data.get('result', {}),
                raw_data=hand_data
            )
            
            return parsed_hand
            
        except Exception as e:
            print(f"Error parsing hand block: {e}")
            return None
    
    def _extract_hand_name(self, block: str, hand_index: int) -> str:
        """Extract hand name from block."""
        lines = block.split('\n')
        for line in lines:
            if line.strip().startswith('# Hand ') and '—' in line:
                # Extract name from comment like "# Hand 1 — Viktor "Isildur1" Blom vs Tom "durrrr" Dwan"
                parts = line.split('—', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        return f"Legendary Hand {hand_index + 1}"
    
    def _extract_player_names(self, players: List[Dict]) -> List[str]:
        """Extract player names from players list."""
        names = []
        for player in players:
            if isinstance(player, dict) and 'name' in player:
                names.append(player['name'])
        return names
    
    def _estimate_pot_size(self, hand_data: Dict) -> float:
        """Estimate pot size from hand data."""
        # This is a simplified estimation
        game = hand_data.get('game', {})
        stakes = game.get('stakes', '0/0/0')
        if '/' in stakes:
            parts = stakes.split('/')
            if len(parts) >= 2:
                try:
                    big_blind = float(parts[1])
                    # Estimate based on big blinds (rough approximation)
                    return big_blind * 20  # Average pot might be 20bb
                except:
                    pass
        return 0.0
    
    def _create_description(self, hand_data: Dict) -> str:
        """Create description from hand data."""
        game = hand_data.get('game', {})
        meta = hand_data.get('meta', {})
        
        desc_parts = []
        if 'event' in game:
            desc_parts.append(f"Event: {game['event']}")
        if 'date' in game:
            desc_parts.append(f"Date: {game['date']}")
        if 'category' in meta:
            desc_parts.append(f"Category: {meta['category']}")
        
        return '; '.join(desc_parts)


class UserTaggedHandsManager:
    """Manager for user-tagged and important hands."""
    
    def __init__(self, tags_file: str = "logs/user_hand_tags.json"):
        self.tags_file = Path(tags_file)
        self.tags_file.parent.mkdir(exist_ok=True)
        self.tagged_hands: Dict[str, Dict] = {}
        self.load_tags()
    
    def load_tags(self):
        """Load user tags from file."""
        if self.tags_file.exists():
            try:
                with open(self.tags_file, 'r') as f:
                    self.tagged_hands = json.load(f)
            except Exception as e:
                print(f"Error loading tags: {e}")
                self.tagged_hands = {}
    
    def save_tags(self):
        """Save user tags to file."""
        try:
            with open(self.tags_file, 'w') as f:
                json.dump(self.tagged_hands, f, indent=2)
        except Exception as e:
            print(f"Error saving tags: {e}")
    
    def tag_hand(self, hand_id: str, tags: List[str], notes: str = "", 
                 is_favorite: bool = False, difficulty: int = 1):
        """Tag a hand with custom labels."""
        self.tagged_hands[hand_id] = {
            'tags': tags,
            'notes': notes,
            'is_favorite': is_favorite,
            'difficulty': difficulty,
            'tagged_date': datetime.now().isoformat(),
            'review_count': self.tagged_hands.get(hand_id, {}).get('review_count', 0)
        }
        self.save_tags()
    
    def get_hand_tags(self, hand_id: str) -> Dict[str, Any]:
        """Get tags for a specific hand."""
        return self.tagged_hands.get(hand_id, {})
    
    def get_hands_by_tag(self, tag: str) -> List[str]:
        """Get all hand IDs with a specific tag."""
        hands = []
        for hand_id, data in self.tagged_hands.items():
            if tag in data.get('tags', []):
                hands.append(hand_id)
        return hands
    
    def get_all_tags(self) -> Set[str]:
        """Get all unique tags."""
        all_tags = set()
        for data in self.tagged_hands.values():
            all_tags.update(data.get('tags', []))
        return all_tags
    
    def mark_reviewed(self, hand_id: str):
        """Mark a hand as reviewed."""
        if hand_id in self.tagged_hands:
            self.tagged_hands[hand_id]['last_reviewed'] = datetime.now().isoformat()
            self.tagged_hands[hand_id]['review_count'] = self.tagged_hands[hand_id].get('review_count', 0) + 1
            self.save_tags()


class ComprehensiveHandsDatabase:
    """Unified database for all hand types."""
    
    def __init__(self, legendary_phh_path: str = "data/legendary_hands.phh",
                 practice_hands_dir: str = "logs/practice_hands",
                 tags_file: str = "logs/user_hand_tags.json"):
        
        # Initialize managers
        self.legendary_loader = LegendaryHandsPHHLoader(legendary_phh_path)
        self.practice_manager = PracticeHandsPHHManager(practice_hands_dir)
        self.tags_manager = UserTaggedHandsManager(tags_file)
        
        # Cache for loaded hands
        self.all_hands: Dict[str, ParsedHand] = {}
        self.hands_by_category: Dict[HandCategory, List[ParsedHand]] = {
            HandCategory.LEGENDARY: [],
            HandCategory.PRACTICE: [],
            HandCategory.TAGGED: []
        }
    
    def load_all_hands(self) -> Dict[HandCategory, List[ParsedHand]]:
        """Load all hands from all sources."""
        self.all_hands.clear()
        for category in HandCategory:
            self.hands_by_category[category].clear()
        
        # Load legendary hands
        legendary_hands = self.legendary_loader.load_hands()
        for hand in legendary_hands:
            self.all_hands[hand.metadata.id] = hand
            self.hands_by_category[HandCategory.LEGENDARY].append(hand)
        
        # Load practice hands
        practice_hands = self._load_practice_hands()
        for hand in practice_hands:
            self.all_hands[hand.metadata.id] = hand
            self.hands_by_category[HandCategory.PRACTICE].append(hand)
        
        # Load tagged hands (references to existing hands)
        self._organize_tagged_hands()
        
        return self.hands_by_category
    
    def _load_practice_hands(self) -> List[ParsedHand]:
        """Load practice hands from PHH files."""
        practice_hands = []
        
        try:
            # Get practice PHH files
            phh_files = self.practice_manager.get_practice_hands_files()
            
            for file_info in phh_files:
                if file_info["metadata_file"]:
                    try:
                        with open(file_info["metadata_file"], 'r') as f:
                            metadata = json.load(f)
                        
                        # Convert each hand to ParsedHand format
                        for hand_data in metadata.get("hands", []):
                            parsed_hand = self._convert_practice_hand(hand_data)
                            if parsed_hand:
                                practice_hands.append(parsed_hand)
                    
                    except Exception as e:
                        print(f"Error loading practice metadata {file_info['metadata_file']}: {e}")
        
        except Exception as e:
            print(f"Error loading practice hands: {e}")
        
        return practice_hands
    
    def _convert_practice_hand(self, hand_data: Dict) -> Optional[ParsedHand]:
        """Convert practice hand data to ParsedHand format."""
        try:
            # Apply user tags if available
            hand_id = hand_data.get('id', '')
            tag_data = self.tags_manager.get_hand_tags(hand_id)
            
            metadata = HandMetadata(
                id=hand_id,
                name=hand_data.get('name', 'Practice Hand'),
                category=HandCategory.PRACTICE,
                subcategory='Practice Session',
                source_file=hand_data.get('phh_file', ''),
                date=hand_data.get('session_date'),
                event='Practice Session',
                players_involved=hand_data.get('players_involved', []),
                pot_size=hand_data.get('pot_size', 0.0),
                description=hand_data.get('description', ''),
                tags=set(tag_data.get('tags', [])),
                is_favorite=tag_data.get('is_favorite', False),
                difficulty_rating=tag_data.get('difficulty', 1),
                study_notes=tag_data.get('notes', ''),
                last_reviewed=tag_data.get('last_reviewed')
            )
            
            # Create simplified ParsedHand for practice hands
            parsed_hand = ParsedHand(
                metadata=metadata,
                game_info={'session_id': hand_data.get('session_id', '')},
                players=[],  # Detailed player info not needed for display
                actions={},  # Actions not needed for list display
                board={},
                result={},
                raw_data=hand_data
            )
            
            return parsed_hand
            
        except Exception as e:
            print(f"Error converting practice hand: {e}")
            return None
    
    def _organize_tagged_hands(self):
        """Organize hands that have user tags into tagged category."""
        tagged_hands = []
        
        # Find all hands that have tags
        for hand_id, hand in self.all_hands.items():
            tag_data = self.tags_manager.get_hand_tags(hand_id)
            if tag_data and tag_data.get('tags'):
                # Update metadata with tag information
                hand.metadata.tags = set(tag_data.get('tags', []))
                hand.metadata.is_favorite = tag_data.get('is_favorite', False)
                hand.metadata.difficulty_rating = tag_data.get('difficulty', hand.metadata.difficulty_rating)
                hand.metadata.study_notes = tag_data.get('notes', '')
                hand.metadata.last_reviewed = tag_data.get('last_reviewed')
                
                # Add to tagged hands if it has tags
                if hand.metadata.tags:
                    tagged_hands.append(hand)
        
        self.hands_by_category[HandCategory.TAGGED] = tagged_hands
    
    def get_hands_by_category(self, category: HandCategory) -> List[ParsedHand]:
        """Get hands by category."""
        return self.hands_by_category.get(category, [])
    
    def get_hands_by_tag(self, tag: str) -> List[ParsedHand]:
        """Get hands by specific tag."""
        tagged_hands = []
        for hand in self.all_hands.values():
            if tag in hand.metadata.tags:
                tagged_hands.append(hand)
        return tagged_hands
    
    def get_hand_by_id(self, hand_id: str) -> Optional[ParsedHand]:
        """Get a specific hand by ID."""
        return self.all_hands.get(hand_id)
    
    def search_hands(self, query: str, category: Optional[HandCategory] = None) -> List[ParsedHand]:
        """Search hands by name, description, or player names."""
        results = []
        search_hands = (self.hands_by_category[category] if category 
                       else list(self.all_hands.values()))
        
        query_lower = query.lower()
        for hand in search_hands:
            if (query_lower in hand.metadata.name.lower() or
                query_lower in hand.metadata.description.lower() or
                any(query_lower in player.lower() for player in hand.metadata.players_involved)):
                results.append(hand)
        
        return results
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each category."""
        stats = {}
        
        for category in HandCategory:
            hands = self.hands_by_category[category]
            stats[category.value] = {
                'total_hands': len(hands),
                'avg_pot_size': sum(h.metadata.pot_size for h in hands) / len(hands) if hands else 0,
                'unique_tags': len(set().union(*(h.metadata.tags for h in hands))),
                'favorites': sum(1 for h in hands if h.metadata.is_favorite),
                'avg_difficulty': sum(h.metadata.difficulty_rating for h in hands) / len(hands) if hands else 0
            }
        
        return stats
