#!/usr/bin/env python3
"""Validate the structure of generated clean poker data."""

import json

def main():
    print("🔍 Validating Clean Poker Data Structure")
    print("=" * 50)
    
    # Load the data
    with open('data/clean_poker_sessions_100.json', 'r') as f:
        data = json.load(f)
    
    print("📊 Data Structure:")
    print(f"  Metadata keys: {list(data['metadata'].keys())}")
    print(f"  Total sessions: {data['metadata']['total_sessions']}")
    print(f"  Total hands: {data['metadata']['total_hands']}")
    
    print("\n🔍 Sample Session:")
    session = data['sessions'][0]
    print(f"  Session ID: {session['session_id']}")
    print(f"  Players: {session['num_players']}")
    print(f"  Hands: {session['num_hands']}")
    
    print("\n🃏 Sample Hand:")
    hand = session['hands'][0]
    print(f"  Hand ID: {hand['id']}")
    print(f"  Players: {len(hand['players'])}")
    print(f"  Actions: {list(hand['actions'].keys())}")
    print(f"  Board: {list(hand['board'].keys())}")
    print(f"  Pot: ${hand['pot']}")
    
    print("\n✅ Data structure validation complete!")

if __name__ == "__main__":
    main()
