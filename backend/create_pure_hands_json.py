#!/usr/bin/env python3
"""
Pure Hands JSON Creator

Creates a clean JSON format containing only the original hand data:
- Players info (name, stack size, position)
- Blinds (SB, BB)
- Actions by street (without simulation artifacts)
- Pot sizes by street
- Board cards by street
- Final results (winner, showdown, etc.)

No simulation-generated data included.
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.hands_database import LegendaryHandsPHHLoader

class PureHandsJSONCreator:
    """Creates pure hand data JSON from PHH files."""
    
    def __init__(self):
        self.hands_data = []
        
    def create_pure_json(self):
        """Create pure hands JSON from PHH data."""
        print("🎯 CREATING PURE HANDS JSON FORMAT")
        print("=" * 60)
        
        # Step 1: Load PHH hands
        self.load_phh_hands()
        
        # Step 2: Convert to pure JSON format
        self.convert_to_pure_json()
        
        # Step 3: Save JSON file
        self.save_json_file()
        
        print("✅ Pure hands JSON creation completed!")
    
    def load_phh_hands(self):
        """Load hands from PHH file."""
        print("📚 Loading PHH hands from legendary_hands.phh...")
        
        try:
            loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
            hands = loader.load_hands()
            
            print(f"✅ Loaded {len(hands)} hands from PHH")
            
            # Convert each hand to pure data format
            for hand in hands:
                pure_hand = self.convert_hand_to_pure_format(hand)
                if pure_hand:
                    self.hands_data.append(pure_hand)
            
            print(f"✅ Converted {len(self.hands_data)} hands to pure format")
            
        except Exception as e:
            print(f"❌ Failed to load PHH hands: {e}")
            raise
    
    def convert_hand_to_pure_format(self, hand) -> Optional[Dict[str, Any]]:
        """Convert a single PHH hand to pure JSON format."""
        try:
            # Extract basic metadata
            hand_data = {
                "id": hand.metadata.id,
                "name": hand.metadata.name,
                "note": getattr(hand.metadata, 'note', ''),
                "format_version": "1.0_pure"
            }
            
            # Extract game configuration
            hand_data["game_config"] = {
                "game_type": "No Limit Hold'em",
                "num_players": len(hand.players),
                "small_blind": getattr(hand, 'small_blind', 1000.0),
                "big_blind": getattr(hand, 'big_blind', 2000.0),
                "ante": getattr(hand, 'ante', 0.0)
            }
            
            # Extract players information
            hand_data["players"] = []
            for player_data in hand.players:
                player_info = {
                    "name": player_data['name'],
                    "seat": player_data.get('seat', 1),
                    "starting_stack": player_data.get('starting_stack_chips', 1000000.0),
                    "position": self._determine_position(player_data.get('seat', 1), len(hand.players)),
                    "hole_cards": player_data.get('cards', [])
                }
                hand_data["players"].append(player_info)
            
            # Extract board cards by street
            hand_data["board"] = {
                "flop": getattr(hand, 'flop', []),
                "turn": getattr(hand, 'turn', []),
                "river": getattr(hand, 'river', [])
            }
            
            # Extract actions by street
            hand_data["actions"] = {}
            if hasattr(hand, 'actions') and hand.actions:
                for street, actions in hand.actions.items():
                    if actions:
                        hand_data["actions"][street] = []
                        for action in actions:
                            action_data = {
                                "player_seat": action.get('actor', 1),
                                "action_type": action.get('type', 'fold').lower(),
                                "amount": action.get('amount', 0.0)
                            }
                            # Handle 'to' field for raises
                            if 'to' in action:
                                action_data["to_amount"] = action['to']
                            
                            hand_data["actions"][street].append(action_data)
            
            # Extract pot information by street (if available)
            hand_data["pot_by_street"] = {
                "preflop": getattr(hand, 'preflop_pot', 0.0),
                "flop": getattr(hand, 'flop_pot', 0.0),
                "turn": getattr(hand, 'turn_pot', 0.0),
                "river": getattr(hand, 'river_pot', 0.0),
                "final": getattr(hand, 'final_pot', 0.0)
            }
            
            # Extract final results
            hand_data["results"] = {
                "winner": getattr(hand, 'winner', ''),
                "winning_hand": getattr(hand, 'winning_hand', ''),
                "showdown": getattr(hand, 'showdown', False),
                "final_pot_size": getattr(hand, 'final_pot', 0.0)
            }
            
            # Add any additional metadata
            hand_data["metadata"] = {
                "source": "legendary_hands.phh",
                "created_at": "2024-01-01",  # Placeholder
                "hand_category": self._categorize_hand(hand.metadata.name)
            }
            
            return hand_data
            
        except Exception as e:
            print(f"⚠️  Failed to convert hand {getattr(hand.metadata, 'id', 'Unknown')}: {e}")
            return None
    
    def _determine_position(self, seat: int, num_players: int) -> str:
        """Determine position name based on seat and number of players."""
        if num_players == 2:
            return "SB" if seat == 1 else "BB"
        elif num_players == 6:
            positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
            return positions[(seat - 1) % 6]
        elif num_players == 9:
            positions = ["UTG", "UTG+1", "MP1", "MP2", "MP3", "CO", "BTN", "SB", "BB"]
            return positions[(seat - 1) % 9]
        else:
            # Generic position for other player counts
            if seat == num_players - 1:
                return "SB"
            elif seat == num_players:
                return "BB"
            elif seat == num_players - 2:
                return "BTN"
            else:
                return f"P{seat}"
    
    def _categorize_hand(self, hand_name: str) -> str:
        """Categorize hand based on name."""
        name_lower = hand_name.lower()
        
        if 'cooler' in name_lower:
            return "cooler"
        elif 'bluff' in name_lower:
            return "bluff"
        elif 'hero call' in name_lower:
            return "hero_call"
        elif 'wsop' in name_lower:
            return "wsop"
        elif 'final' in name_lower:
            return "final_table"
        elif 'heads up' in name_lower or 'hu' in name_lower:
            return "heads_up"
        else:
            return "cash_game"
    
    def convert_to_pure_json(self):
        """Convert all loaded hands to pure JSON format."""
        print(f"🔄 Converting {len(self.hands_data)} hands to pure JSON format...")
        
        # Hands are already converted in load_phh_hands
        print("✅ All hands converted to pure format")
    
    def save_json_file(self):
        """Save the pure hands data to JSON file."""
        output_file = "data/legendary_hands_pure.json"
        
        print(f"💾 Saving pure hands data to {output_file}...")
        
        try:
            # Create the final JSON structure
            json_data = {
                "format_version": "1.0_pure",
                "description": "Pure legendary poker hands data without simulation artifacts",
                "total_hands": len(self.hands_data),
                "data_source": "legendary_hands.phh",
                "created_at": "2024-01-01",
                "hands": self.hands_data
            }
            
            # Save to file with proper formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Calculate file size
            file_size = os.path.getsize(output_file)
            size_mb = file_size / (1024 * 1024)
            
            print(f"✅ Saved {len(self.hands_data)} hands to {output_file}")
            print(f"   File size: {size_mb:.2f} MB")
            
            # Show sample of the data
            print(f"\n📋 SAMPLE HAND DATA:")
            if self.hands_data:
                sample_hand = self.hands_data[0]
                print(f"   ID: {sample_hand['id']}")
                print(f"   Name: {sample_hand['name']}")
                print(f"   Players: {sample_hand['game_config']['num_players']}")
                print(f"   Blinds: ${sample_hand['game_config']['small_blind']:.0f}/${sample_hand['game_config']['big_blind']:.0f}")
                print(f"   Actions streets: {list(sample_hand['actions'].keys())}")
                
        except Exception as e:
            print(f"❌ Failed to save JSON file: {e}")
            raise

def main():
    """Main function to create pure hands JSON."""
    creator = PureHandsJSONCreator()
    
    try:
        creator.create_pure_json()
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create pure hands JSON: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
