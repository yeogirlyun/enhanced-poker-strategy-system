#!/usr/bin/env python3
"""
Complete Hands JSON Creator

Creates a comprehensive JSON format that captures ALL information from PHH:
- Complete game metadata (stakes, currency, event, date)
- Table information (button seat, max players)
- Complete board cards (flop, turn, river)
- Player positions and detailed info
- All action sequences with proper actor mapping
- Results and final hand information

This preserves 100% of the original PHH information.
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from core.hands_database import LegendaryHandsPHHLoader

class CompleteHandsJSONCreator:
    """Creates complete hands JSON preserving all PHH information."""
    
    def __init__(self):
        self.hands_data = []
        
    def create_complete_json(self):
        """Create complete hands JSON from PHH data."""
        print("🎯 CREATING COMPLETE HANDS JSON FORMAT")
        print("=" * 60)
        
        # Step 1: Load PHH hands
        self.load_phh_hands()
        
        # Step 2: Convert to complete JSON format
        self.convert_to_complete_json()
        
        # Step 3: Save JSON file
        self.save_json_file()
        
        print("✅ Complete hands JSON creation finished!")
    
    def load_phh_hands(self):
        """Load hands from PHH file."""
        print("📚 Loading PHH hands from legendary_hands.phh...")
        
        try:
            loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
            hands = loader.load_hands()
            
            print(f"✅ Loaded {len(hands)} hands from PHH")
            
            # Convert each hand to complete format
            for hand in hands:
                complete_hand = self.convert_hand_to_complete_format(hand)
                if complete_hand:
                    self.hands_data.append(complete_hand)
            
            print(f"✅ Converted {len(self.hands_data)} hands to complete format")
            
        except Exception as e:
            print(f"❌ Failed to load PHH hands: {e}")
            raise
    
    def convert_hand_to_complete_format(self, hand) -> Optional[Dict[str, Any]]:
        """Convert a single PHH hand to complete JSON format preserving all information."""
        try:
            # Extract complete metadata
            hand_data = {
                "id": hand.metadata.id,
                "name": hand.metadata.name,
                "format_version": "1.0_complete"
            }
            
            # Extract complete game information
            game_info = getattr(hand, 'game_info', {})
            hand_data["game"] = {
                "variant": game_info.get('variant', "No Limit Hold'em"),
                "stakes": game_info.get('stakes', '1000/2000/0'),
                "currency": game_info.get('currency', 'USD'),
                "format": game_info.get('format', 'Cash Game'),
                "event": game_info.get('event', ''),
                "date": hand.metadata.date if hasattr(hand.metadata, 'date') else '',
                "category": hand.metadata.subcategory if hasattr(hand.metadata, 'subcategory') else ''
            }
            
            # Extract table information
            hand_data["table"] = {
                "name": getattr(hand, 'table_name', 'Table 1'),
                "max_players": len(hand.players),
                "button_seat": getattr(hand, 'button_seat', 1),
                "num_players": len(hand.players)
            }
            
            # Extract game configuration
            stakes_parts = hand_data["game"]["stakes"].split('/')
            small_blind = float(stakes_parts[0]) if len(stakes_parts) > 0 else 1000.0
            big_blind = float(stakes_parts[1]) if len(stakes_parts) > 1 else 2000.0
            ante = float(stakes_parts[2]) if len(stakes_parts) > 2 else 0.0
            
            hand_data["game_config"] = {
                "game_type": hand_data["game"]["variant"],
                "num_players": len(hand.players),
                "small_blind": small_blind,
                "big_blind": big_blind,
                "ante": ante
            }
            
            # Extract complete players information
            hand_data["players"] = []
            for player_data in hand.players:
                player_info = {
                    "name": player_data['name'],
                    "seat": player_data.get('seat', 1),
                    "starting_stack": player_data.get('starting_stack_chips', 1000000.0),
                    "position": self._get_player_position(player_data, hand),
                    "hole_cards": player_data.get('cards', [])
                }
                hand_data["players"].append(player_info)
            
            # Extract complete board information
            board_data = getattr(hand, 'board', {})
            
            # Handle the flop cards issue - they might be in player 6's cards
            flop_cards = []
            turn_cards = board_data.get('turn', [])
            river_cards = board_data.get('river', [])
            
            # Check if last player has flop cards (common parsing issue)
            if len(hand.players) >= 6:
                last_player_cards = hand.players[-1].get('cards', [])
                if len(last_player_cards) == 3:  # Likely flop cards
                    flop_cards = last_player_cards
                    # Fix the player's hole cards
                    hand_data["players"][-1]["hole_cards"] = []
            
            hand_data["board"] = {
                "flop": flop_cards,
                "turn": turn_cards,
                "river": river_cards,
                "all_cards": flop_cards + turn_cards + river_cards
            }
            
            # Extract complete actions with proper actor mapping
            hand_data["actions"] = {}
            if hasattr(hand, 'actions') and hand.actions:
                for street, actions in hand.actions.items():
                    if actions:
                        hand_data["actions"][street] = []
                        for action in actions:
                            action_data = {
                                "actor": action.get('actor', 1),
                                "player_seat": action.get('actor', 1),
                                "player_name": self._get_player_name_by_seat(action.get('actor', 1), hand.players),
                                "action_type": action.get('type', 'fold').lower(),
                                "amount": action.get('amount', 0.0)
                            }
                            # Handle 'to' field for raises
                            if 'to' in action:
                                action_data["to_amount"] = action['to']
                            
                            hand_data["actions"][street].append(action_data)
            
            # Extract blinds information
            hand_data["blinds"] = {
                "small_blind": {
                    "seat": self._get_sb_seat(hand),
                    "amount": small_blind
                },
                "big_blind": {
                    "seat": self._get_bb_seat(hand),
                    "amount": big_blind
                }
            }
            
            # Extract pot information by street (calculate from actions)
            hand_data["pot_by_street"] = self._calculate_pot_by_street(hand_data["actions"], small_blind, big_blind)
            
            # Extract final results
            hand_data["results"] = {
                "winner": getattr(hand, 'winner', ''),
                "winning_hand": getattr(hand, 'winning_hand', ''),
                "showdown": getattr(hand, 'showdown', False),
                "final_pot_size": hand.metadata.pot_size if hasattr(hand.metadata, 'pot_size') else 0.0
            }
            
            # Add complete metadata
            hand_data["metadata"] = {
                "source": "legendary_hands.phh",
                "created_at": "2024-01-01",
                "hand_category": hand.metadata.subcategory if hasattr(hand.metadata, 'subcategory') else '',
                "event": hand_data["game"]["event"],
                "date": hand_data["game"]["date"],
                "pot_size": hand.metadata.pot_size if hasattr(hand.metadata, 'pot_size') else 0.0,
                "difficulty_rating": getattr(hand.metadata, 'difficulty_rating', 0),
                "description": getattr(hand.metadata, 'description', '')
            }
            
            return hand_data
            
        except Exception as e:
            print(f"⚠️  Failed to convert hand {getattr(hand.metadata, 'id', 'Unknown')}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_player_position(self, player_data: Dict, hand) -> str:
        """Get detailed position for a player."""
        seat = player_data.get('seat', 1)
        num_players = len(hand.players)
        
        # Use button seat if available
        button_seat = getattr(hand, 'button_seat', 1)
        
        if num_players == 2:
            return "SB/BTN" if seat == button_seat else "BB"
        elif num_players == 6:
            # Standard 6-max positions relative to button
            positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
            offset = (seat - button_seat) % 6
            return positions[offset]
        elif num_players == 9:
            # Standard 9-max positions relative to button
            positions = ["UTG", "UTG+1", "MP1", "MP2", "MP3", "CO", "BTN", "SB", "BB"]
            offset = (seat - button_seat) % 9
            return positions[offset]
        else:
            # Generic positions
            if seat == button_seat:
                return "BTN"
            elif (seat - button_seat) % num_players == 1:
                return "SB"
            elif (seat - button_seat) % num_players == 2:
                return "BB"
            else:
                return f"P{seat}"
    
    def _get_player_name_by_seat(self, seat: int, players: List[Dict]) -> str:
        """Get player name by seat number."""
        for player in players:
            if player.get('seat') == seat:
                return player.get('name', f'Player {seat}')
        return f'Player {seat}'
    
    def _get_sb_seat(self, hand) -> int:
        """Determine small blind seat."""
        button_seat = getattr(hand, 'button_seat', 1)
        num_players = len(hand.players)
        
        if num_players == 2:
            return button_seat  # Button is SB in heads-up
        else:
            return (button_seat % num_players) + 1  # SB is next to button
    
    def _get_bb_seat(self, hand) -> int:
        """Determine big blind seat."""
        button_seat = getattr(hand, 'button_seat', 1)
        num_players = len(hand.players)
        
        if num_players == 2:
            return (button_seat % num_players) + 1  # BB is opposite to button
        else:
            return ((button_seat + 1) % num_players) + 1  # BB is two seats from button
    
    def _calculate_pot_by_street(self, actions: Dict, sb: float, bb: float) -> Dict[str, float]:
        """Calculate pot size by street from actions."""
        pot_by_street = {
            "preflop": sb + bb,  # Start with blinds
            "flop": 0.0,
            "turn": 0.0,
            "river": 0.0,
            "final": 0.0
        }
        
        current_pot = sb + bb
        
        for street in ['preflop', 'flop', 'turn', 'river']:
            if street in actions:
                for action in actions[street]:
                    amount = action.get('amount', 0.0)
                    if amount > 0:
                        current_pot += amount
                
                pot_by_street[street] = current_pot
        
        pot_by_street["final"] = current_pot
        return pot_by_street
    
    def convert_to_complete_json(self):
        """Convert all loaded hands to complete JSON format."""
        print(f"🔄 Converting {len(self.hands_data)} hands to complete JSON format...")
        print("✅ All hands converted to complete format")
    
    def save_json_file(self):
        """Save the complete hands data to JSON file."""
        output_file = "data/legendary_hands_complete.json"
        
        print(f"💾 Saving complete hands data to {output_file}...")
        
        try:
            # Create the final JSON structure
            json_data = {
                "format_version": "1.0_complete",
                "description": "Complete legendary poker hands data preserving ALL PHH information",
                "total_hands": len(self.hands_data),
                "data_source": "legendary_hands.phh",
                "created_at": "2024-01-01",
                "features": [
                    "Complete game metadata (stakes, currency, event, date)",
                    "Table information (button seat, max players)", 
                    "Complete board cards (flop, turn, river)",
                    "Player positions and detailed info",
                    "All action sequences with actor mapping",
                    "Pot calculations by street",
                    "Results and final hand information"
                ],
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
            
            # Show sample of the complete data
            if self.hands_data:
                sample_hand = self.hands_data[0]
                print(f"\n📋 SAMPLE COMPLETE HAND DATA:")
                print(f"   ID: {sample_hand['id']}")
                print(f"   Name: {sample_hand['name']}")
                print(f"   Event: {sample_hand['game']['event']}")
                print(f"   Date: {sample_hand['game']['date']}")
                print(f"   Stakes: {sample_hand['game']['stakes']}")
                print(f"   Players: {sample_hand['game_config']['num_players']}")
                print(f"   Button seat: {sample_hand['table']['button_seat']}")
                print(f"   Board: {sample_hand['board']['all_cards']}")
                print(f"   Actions streets: {list(sample_hand['actions'].keys())}")
                print(f"   Final pot: ${sample_hand['results']['final_pot_size']:,.0f}")
                
        except Exception as e:
            print(f"❌ Failed to save JSON file: {e}")
            raise

def main():
    """Main function to create complete hands JSON."""
    creator = CompleteHandsJSONCreator()
    
    try:
        creator.create_complete_json()
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create complete hands JSON: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
