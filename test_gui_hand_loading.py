#!/usr/bin/env python3
"""
Test the GUI's hand loading process to see where hole cards are lost.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model import Hand

def test_gui_hand_loading():
    """Test the GUI's hand loading logic."""
    print("🔍 TESTING GUI HAND LOADING LOGIC")
    print("=" * 50)
    
    # Load the same data the GUI loads
    gto_data_files = [
        "/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json",
        "/Users/yeogirlyun/Python/Poker/data/clean_gto_sessions_generated.json"
    ]
    
    for file_path in gto_data_files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n📁 Loading: {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"   Data type: {type(data)}")
        print(f"   Data keys: {list(data.keys())}")
        
        # Handle the GUI's logic - extract hands from data
        hands_data = []
        if 'hands' in data:
            hands_data = data['hands']
            print(f"   ✅ Found {len(hands_data)} hands in 'hands' array")
        elif 'sessions' in data:
            for session in data['sessions']:
                if 'hands' in session:
                    hands_data.extend(session['hands'])
            print(f"   ✅ Found {len(hands_data)} hands in sessions format")
        else:
            print(f"   ❌ No 'hands' or 'sessions' key found")
            continue
        
        if hands_data:
            first_hand = hands_data[0]
            print(f"   First hand keys: {list(first_hand.keys())}")
            
            # Test the GUI's conversion process
            print(f"\n🔄 Testing GUI conversion for first hand...")
            print(f"   Hand ID: {first_hand.get('id', 'Unknown')}")
            
            # Check original hole cards in first_hand
            if 'initial_state' in first_hand and 'players' in first_hand['initial_state']:
                players = first_hand['initial_state']['players']
                print(f"   Original players: {len(players)}")
                for i, player in enumerate(players):
                    if isinstance(player, dict):
                        cards = player.get('hole_cards', player.get('cards', ['**', '**']))
                        name = player.get('name', f'Player{i+1}')
                        print(f"     {name}: {cards}")
            
            # Test Hand Model conversion (like GUI does)
            try:
                hand_model = GTOToHandConverter.convert_gto_hand(first_hand)
                print(f"   ✅ Hand Model created: {hand_model.metadata.hand_id}")
                print(f"   Players: {len(hand_model.seats)}")
                
                # Check hole cards in Hand Model
                hole_cards = getattr(hand_model.metadata, 'hole_cards', {})
                print(f"   Hole cards in metadata: {hole_cards}")
                
                for seat in hand_model.seats:
                    print(f"   {seat.player_id}: stack=${seat.starting_stack}")
                
                # Create the same hand_dict the GUI creates
                hand_dict = {
                    'hand_model': hand_model,
                    'hand_id': hand_model.metadata.hand_id,
                    'id': hand_model.metadata.hand_id,
                    'timestamp': hand_model.metadata.hand_id,
                    'source': 'GTO Generated (Hand Model)',
                    'comments': '',
                    'street_comments': {
                        'preflop': '', 'flop': '', 'turn': '', 'river': '', 'overall': ''
                    }
                }
                
                print(f"   ✅ GUI hand_dict created")
                print(f"   hand_dict keys: {list(hand_dict.keys())}")
                print(f"   'hand_model' in hand_dict: {'hand_model' in hand_dict}")
                print(f"   hand_model type: {type(hand_dict.get('hand_model'))}")
                print(f"   is Hand instance: {isinstance(hand_dict.get('hand_model'), Hand)}")
                
                # Test if the hand_model has hole cards
                if hasattr(hand_dict['hand_model'].metadata, 'hole_cards'):
                    metadata_cards = hand_dict['hand_model'].metadata.hole_cards
                    print(f"   Metadata hole_cards: {metadata_cards}")
                else:
                    print(f"   ❌ No hole_cards in metadata!")
                
            except Exception as e:
                print(f"   ❌ Conversion failed: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
            
            break

if __name__ == "__main__":
    test_gui_hand_loading()
