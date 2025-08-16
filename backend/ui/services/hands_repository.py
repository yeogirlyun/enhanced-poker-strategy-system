import json
import os
from typing import List, Dict, Any, Optional
from enum import Enum

class StudyMode(Enum):
    """Study modes for hands review."""
    REPLAY = "replay"
    SOLVER_DIFF = "solver_diff"
    RECALL_QUIZ = "recall_quiz"
    EXPLAIN_MISTAKE = "explain_mistake"

class HandsFilter:
    """Filter criteria for hands."""
    def __init__(self):
        self.positions: List[str] = []
        self.pot_type: Optional[str] = None  # "SRP", "3BP", "4BP+"
        self.min_stack_depth: Optional[int] = None
        self.max_stack_depth: Optional[int] = None
        self.line_type: Optional[str] = None
        self.themes: List[str] = []
        self.min_spr: Optional[float] = None
        self.max_spr: Optional[float] = None
        self.search_text: str = ""

    def matches(self, hand: Dict[str, Any]) -> bool:
        """Check if a hand matches the filter criteria."""
        # Position filter
        if self.positions:
            hand_positions = []
            for player in hand.get('players', []):
                if player.get('position'):
                    hand_positions.append(player['position'])
            if not any(pos in hand_positions for pos in self.positions):
                return False
        
        # Stack depth filter
        if self.min_stack_depth is not None or self.max_stack_depth is not None:
            stacks = [p.get('stack', 0) for p in hand.get('players', [])]
            avg_stack = sum(stacks) / len(stacks) if stacks else 0
            bb = hand.get('big_blind', 10)
            stack_depth_bb = avg_stack / bb if bb > 0 else 0
            
            if self.min_stack_depth is not None and stack_depth_bb < self.min_stack_depth:
                return False
            if self.max_stack_depth is not None and stack_depth_bb > self.max_stack_depth:
                return False
        
        # Search text filter
        if self.search_text:
            search_lower = self.search_text.lower()
            hand_text = f"{hand.get('hand_id', '')} {hand.get('description', '')}".lower()
            if search_lower not in hand_text:
                return False
        
        # TODO: Add more filter logic for pot_type, line_type, themes, SPR
        
        return True

class HandsRepository:
    """Repository for managing poker hands data."""
    
    def __init__(self):
        self.legendary_hands: List[Dict[str, Any]] = []
        self.bot_hands: List[Dict[str, Any]] = []
        self.imported_hands: List[Dict[str, Any]] = []
        self.collections: Dict[str, List[str]] = {}  # collection_name -> [hand_ids]
        self.current_filter = HandsFilter()
        self._load_hands()
    
    def _load_hands(self):
        """Load hands from various sources."""
        self._load_legendary_hands()
        # TODO: Load bot hands and imported hands
        self._create_default_collections()
    
    def _load_legendary_hands(self):
        """Load legendary hands from data directory."""
        try:
            data_paths = [
                "backend/data/legendary_hands.json",
                "data/legendary_hands.json", 
                os.path.join(os.path.dirname(__file__), "../../../data/legendary_hands.json"),
                os.path.join(os.path.dirname(__file__), "../../data/legendary_hands.json")
            ]
            
            for path in data_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        self.legendary_hands = data
                    elif isinstance(data, dict) and 'hands' in data:
                        self.legendary_hands = data['hands']
                    
                    # Ensure each hand has required metadata
                    for i, hand in enumerate(self.legendary_hands):
                        if 'source' not in hand:
                            hand['source'] = 'legendary'
                        if 'hand_id' not in hand:
                            hand['hand_id'] = f'legendary_{i+1}'
                    
                    print(f"✅ HandsRepository loaded {len(self.legendary_hands)} legendary hands")
                    break
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
    
    def _create_default_collections(self):
        """Create default collections."""
        if self.legendary_hands:
            # Create collections by pot size ranges
            self.collections["High Stakes"] = [
                hand['hand_id'] for hand in self.legendary_hands 
                if hand.get('pot_size', 0) > 1000
            ]
            self.collections["Tournament Classics"] = [
                hand['hand_id'] for hand in self.legendary_hands 
                if any(keyword in hand.get('description', '').lower() 
                      for keyword in ['wsop', 'tournament', 'final table'])
            ]
    
    def get_all_hands(self) -> List[Dict[str, Any]]:
        """Get all hands from all sources."""
        return self.legendary_hands + self.bot_hands + self.imported_hands
    
    def get_filtered_hands(self) -> List[Dict[str, Any]]:
        """Get hands that match current filter."""
        all_hands = self.get_all_hands()
        return [hand for hand in all_hands if self.current_filter.matches(hand)]
    
    def get_hand_by_id(self, hand_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific hand by ID."""
        for hand in self.get_all_hands():
            if hand.get('hand_id') == hand_id:
                return hand
        return None
    
    def set_filter(self, filter_criteria: HandsFilter):
        """Set new filter criteria."""
        self.current_filter = filter_criteria
    
    def get_collections(self) -> Dict[str, List[str]]:
        """Get all collections."""
        return self.collections.copy()
    
    def get_collection_hands(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get hands in a specific collection."""
        hand_ids = self.collections.get(collection_name, [])
        hands = []
        for hand_id in hand_ids:
            hand = self.get_hand_by_id(hand_id)
            if hand:
                hands.append(hand)
        return hands
    
    def add_to_collection(self, collection_name: str, hand_id: str):
        """Add hand to a collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        if hand_id not in self.collections[collection_name]:
            self.collections[collection_name].append(hand_id)
    
    def create_collection(self, collection_name: str, hand_ids: List[str] = None):
        """Create a new collection."""
        self.collections[collection_name] = hand_ids or []
    
    def get_stats(self) -> Dict[str, int]:
        """Get repository statistics."""
        return {
            "total_hands": len(self.get_all_hands()),
            "legendary_hands": len(self.legendary_hands),
            "bot_hands": len(self.bot_hands),
            "imported_hands": len(self.imported_hands),
            "collections": len(self.collections),
            "filtered_hands": len(self.get_filtered_hands())
        }