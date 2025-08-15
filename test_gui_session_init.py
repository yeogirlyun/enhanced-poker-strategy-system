#!/usr/bin/env python3
"""
Test the exact GUI session initialization process.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.bot_session_state_machine import HandsReviewBotSession
from backend.core.flexible_poker_state_machine import GameConfig
from backend.core.session_logger import SessionLogger

def test_gui_session_initialization():
    """Test the exact GUI session initialization steps."""
    print("🔍 TESTING GUI SESSION INITIALIZATION")
    print("=" * 50)
    
    # Load the same data as GUI
    with open("/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json", 'r') as f:
        data = json.load(f)
    
    first_hand = data['hands'][0]
    print(f"📊 Original hand: {first_hand.get('id')}")
    
    # Step 1: Convert like GUI does (already confirmed this works)
    hand_model = GTOToHandConverter.convert_gto_hand(first_hand)
    hand_to_review = {
        'hand_model': hand_model,
        'hand_id': hand_model.metadata.hand_id,
        'id': hand_model.metadata.hand_id,
        'timestamp': hand_model.metadata.hand_id,
        'source': 'GTO Generated (Hand Model)',
        'comments': '',
        'street_comments': {'preflop': '', 'flop': '', 'turn': '', 'river': '', 'overall': ''}
    }
    
    print(f"✅ hand_to_review created")
    print(f"   Hand Model in data: {'hand_model' in hand_to_review}")
    print(f"   Hole cards: {hand_to_review['hand_model'].metadata.hole_cards}")
    
    # Step 2: Create session like GUI does
    decision_engine = HandModelDecisionEngine(hand_to_review['hand_model'])
    game_config = GameConfig(
        num_players=3,
        starting_stack=1000,
        small_blind=5,
        big_blind=10
    )
    
    session = HandsReviewBotSession(
        config=game_config,
        decision_engine=decision_engine
    )
    
    print(f"✅ Session created")
    
    # Step 3: Set preloaded data like GUI does
    print(f"\n🔄 Setting preloaded hand data...")
    session.set_preloaded_hand_data(hand_to_review)
    print(f"✅ Preloaded data set")
    
    # Check if session received the data properly
    print(f"   Session has preloaded_hand_data: {hasattr(session, 'preloaded_hand_data')}")
    if hasattr(session, 'preloaded_hand_data') and session.preloaded_hand_data:
        print(f"   Preloaded data keys: {list(session.preloaded_hand_data.keys())}")
        print(f"   'hand_model' in preloaded data: {'hand_model' in session.preloaded_hand_data}")
        
        if 'hand_model' in session.preloaded_hand_data:
            preloaded_hand_model = session.preloaded_hand_data['hand_model']
            preloaded_hole_cards = getattr(preloaded_hand_model.metadata, 'hole_cards', {})
            print(f"   Preloaded hole cards: {preloaded_hole_cards}")
    
    # Step 4: Start session like GUI does
    print(f"\n🚀 Starting session...")
    success = session.start_session()
    print(f"   Start session result: {success}")
    
    # Check final session state
    if success:
        print(f"\n🔍 Final session state (direct access):")
        players = getattr(session.game_state, 'players', [])
        print(f"   Number of players: {len(players)}")
        for i, player in enumerate(players):
            name = getattr(player, 'name', f'Player{i+1}')
            cards = getattr(player, 'cards', [])
            stack = getattr(player, 'stack', 0)
            print(f"   {name}: {cards} (${stack})")
        
        print(f"   Pot: ${getattr(session.game_state, 'pot', 0)}")
        print(f"   Current bet: ${getattr(session.game_state, 'current_bet', 0)}")
        print(f"   Action player index: {getattr(session, 'action_player_index', -1)}")
        
        # Check what get_game_info() returns (like GUI does)
        print(f"\n🎮 GUI game_info (via get_game_info()):")
        game_info = session.get_game_info()
        game_players = game_info.get('players', [])
        print(f"   Number of players: {len(game_players)}")
        for i, player_info in enumerate(game_players):
            name = player_info.get('name', f'Player{i+1}')
            cards = player_info.get('cards', [])
            stack = player_info.get('stack', 0)
            print(f"   {name}: {cards} (${stack})")
        
        print(f"   Pot: ${game_info.get('pot', 0)}")
        print(f"   Current bet: ${game_info.get('current_bet', 0)}")
        print(f"   Action player index: {game_info.get('action_player_index', -1)}")

if __name__ == "__main__":
    test_gui_session_initialization()
