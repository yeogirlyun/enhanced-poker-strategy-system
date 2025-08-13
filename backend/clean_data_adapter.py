#!/usr/bin/env python3
"""Adapter to convert clean session data to flat hands format for hands review."""

import json
from typing import List, Dict, Any

class CleanDataAdapter:
    """Convert clean session data to flat hands format for hands review."""
    
    def __init__(self, sessions_file: str):
        """Initialize with the clean sessions data file."""
        self.sessions_file = sessions_file
        self.sessions_data = None
        self.flat_hands = []
        
    def load_sessions(self) -> bool:
        """Load the clean sessions data."""
        try:
            with open(self.sessions_file, 'r') as f:
                self.sessions_data = json.load(f)
            print(f"✅ Loaded {self.sessions_data['metadata']['total_sessions']} sessions")
            return True
        except Exception as e:
            print(f"❌ Error loading sessions: {e}")
            return False
    
    def convert_to_flat_hands(self) -> List[Dict[str, Any]]:
        """Convert sessions to flat hands format expected by hands review."""
        if not self.sessions_data:
            print("❌ No sessions data loaded")
            return []
        
        flat_hands = []
        
        for session in self.sessions_data['sessions']:
            session_id = session['session_id']
            num_players = session['num_players']
            
            for hand in session['hands']:
                # Convert hand to flat format
                flat_hand = {
                    'id': hand['id'],
                    'name': hand['name'],
                    'session_id': session_id,
                    'num_players': num_players,
                    'players': hand['players'],
                    'board': hand['board'],
                    'actions': hand['actions'],
                    'pot': hand['pot'],
                    'winner': hand['winner'],
                    'timestamp': hand['timestamp']
                }
                
                flat_hands.append(flat_hand)
        
        self.flat_hands = flat_hands
        print(f"✅ Converted {len(flat_hands)} hands to flat format")
        return flat_hands
    
    def save_flat_hands(self, output_file: str) -> bool:
        """Save the flat hands data to a file."""
        if not self.flat_hands:
            print("❌ No flat hands data to save")
            return False
        
        try:
            output_data = {
                'metadata': {
                    'source': 'CleanDataAdapter',
                    'original_file': self.sessions_file,
                    'total_hands': len(self.flat_hands),
                    'description': 'Clean poker hands converted to flat format for hands review'
                },
                'hands': self.flat_hands
            }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"✅ Saved {len(self.flat_hands)} hands to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving flat hands: {e}")
            return False
    
    def validate_flat_hands(self) -> bool:
        """Validate that the flat hands have the correct structure."""
        if not self.flat_hands:
            print("❌ No flat hands to validate")
            return False
        
        required_keys = ['id', 'name', 'players', 'board', 'actions', 'pot']
        required_board_keys = ['flop', 'turn', 'river', 'all_cards']
        # Only preflop actions are required (hands can end early)
        
        valid_count = 0
        invalid_count = 0
        
        for i, hand in enumerate(self.flat_hands):
            # Check required top-level keys
            if not all(key in hand for key in required_keys):
                print(f"❌ Hand {i} missing required keys: {hand.get('id', 'Unknown')}")
                invalid_count += 1
                continue
            
            # Check board structure
            if not all(key in hand['board'] for key in required_board_keys):
                print(f"❌ Hand {i} missing board keys: {hand.get('id', 'Unknown')}")
                invalid_count += 1
                continue
            
            # Check actions structure - only preflop is required
            if 'preflop' not in hand['actions']:
                print(f"❌ Hand {i} missing preflop actions: {hand.get('id', 'Unknown')}")
                invalid_count += 1
                continue
            
            # Check player structure
            if not isinstance(hand['players'], list) or len(hand['players']) == 0:
                print(f"❌ Hand {i} invalid players: {hand.get('id', 'Unknown')}")
                invalid_count += 1
                continue
            
            # Check each player has required keys
            for j, player in enumerate(hand['players']):
                player_required = ['name', 'hole_cards', 'stack']
                if not all(key in player for key in player_required):
                    print(f"❌ Hand {i} player {j} missing keys: {hand.get('id', 'Unknown')}")
                    invalid_count += 1
                    break
            
            valid_count += 1
        
        print(f"✅ Validation complete: {valid_count} valid, {invalid_count} invalid")
        return invalid_count == 0

def main():
    """Main function to convert clean data to flat format."""
    
    print("🔄 Clean Data to Flat Hands Converter")
    print("=" * 50)
    
    # Initialize adapter
    adapter = CleanDataAdapter('data/clean_poker_sessions_100.json')
    
    # Load sessions
    if not adapter.load_sessions():
        return
    
    # Convert to flat hands
    flat_hands = adapter.convert_to_flat_hands()
    
    # Validate the converted data
    if not adapter.validate_flat_hands():
        print("❌ Validation failed!")
        return
    
    # Save flat hands
    output_file = 'data/clean_poker_hands_flat.json'
    if adapter.save_flat_hands(output_file):
        print(f"\n🎉 Conversion complete!")
        print(f"📁 Output file: {output_file}")
        print(f"🃏 Total hands: {len(flat_hands)}")

if __name__ == "__main__":
    main()
