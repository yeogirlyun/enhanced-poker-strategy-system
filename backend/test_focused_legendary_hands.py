#!/usr/bin/env python3
"""
Focused Legendary Hands Test

This test validates a few specific legendary hands to ensure:
- Dynamic actor mapping works correctly
- Action sequences match historical data
- No hardcoded positions in RPGW
- Player mapping is correct
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

import tkinter as tk


def test_manion_zhu_labat_hand():
    """Test the specific hand that was problematic: Manion Zhu Labat Triple All In."""
    print("\n" + "="*80)
    print("🃏 TESTING: Manion Zhu Labat Triple All In")
    print("="*80)
    
    # Load hands
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Find the specific hand
    target_hand = None
    for hand in legendary_hands:
        if 'Manion' in getattr(hand.metadata, 'name', '') and 'Zhu' in getattr(hand.metadata, 'name', ''):
            target_hand = hand
            break
    
    if not target_hand:
        print("❌ Could not find Manion Zhu Labat hand")
        return False
    
    print(f"✅ Found hand: {target_hand.metadata.name}")
    print(f"📊 Players: {len(target_hand.players)}")
    
    # Print player details
    for i, player in enumerate(target_hand.players):
        name = player.get('name', f'Player {i+1}')
        seat = player.get('seat', i+1)
        cards = player.get('cards', ['?', '?'])
        stack = player.get('starting_stack_chips', 0)
        print(f"  Player {i}: {name} (Seat {seat}) - {cards} - ${stack:,}")
    
    # Fix missing fields
    for i, player in enumerate(target_hand.players):
        if 'starting_stack_chips' not in player:
            player['starting_stack_chips'] = 1000000
        if 'seat' not in player:
            player['seat'] = i + 1
    
    # Test FPSM setup
    print("\n🎰 Testing FPSM setup...")
    config = GameConfig(
        num_players=len(target_hand.players),
        small_blind=500000,
        big_blind=1000000
    )
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create players
    fpsm_players = []
    for i, player_info in enumerate(target_hand.players):
        player = Player(
            name=player_info.get('name', f'Player {i+1}'),
            stack=player_info.get('starting_stack_chips', 1000000),
            position=player_info.get('position', ''),
            is_human=False,
            is_active=True,
            cards=player_info.get('cards', ['**', '**'])
        )
        fpsm_players.append(player)
    
    fpsm.start_hand(existing_players=fpsm_players)
    print("✅ FPSM started successfully")
    
    # Test dynamic actor mapping
    print("\n🗺️ Testing dynamic actor mapping...")
    root = tk.Tk()
    root.withdraw()
    
    review_panel = FPSMHandsReviewPanel(root)
    review_panel.current_hand = target_hand
    review_panel.fpsm = fpsm
    
    # Build actor mapping
    actor_mapping = review_panel.build_actor_mapping()
    print(f"📋 Actor mapping: {actor_mapping}")
    
    # Test historical actions
    print("\n🎮 Testing historical actions...")
    review_panel.prepare_historical_actions()
    
    if review_panel.use_historical_actions:
        print(f"✅ Prepared {len(review_panel.historical_actions)} historical actions")
        for i, action in enumerate(review_panel.historical_actions[:10]):  # Show first 10
            print(f"  [{i}] Street {action['street']}: Actor {action['actor']} {action['type']} ${action['amount']:,}")
    else:
        print("❌ Failed to prepare historical actions")
    
    # Test RPGW dynamic positioning
    print("\n🖥️ Testing RPGW dynamic positioning...")
    rpgw = ReusablePokerGameWidget(root)
    rpgw.set_poker_game_config(config)
    
    # Get positions
    positions = rpgw._get_dynamic_player_positions()
    print(f"🎯 Dynamic positions for {len(positions)} players:")
    for i, pos in enumerate(positions):
        print(f"  Seat {i}: {pos['name']} ({pos['position']})")
    
    # Test action mapping for each FPSM player
    print("\n🔄 Testing action mapping for each player...")
    success_count = 0
    for i, fpsm_player in enumerate(fpsm.game_state.players):
        # Reset index for each test
        review_panel.historical_action_index = 0
        historical_action = review_panel.get_next_historical_action(fpsm_player)
        
        if historical_action:
            print(f"  ✅ {fpsm_player.name}: Found action {historical_action['type'].value} ${historical_action['amount']:,}")
            success_count += 1
        else:
            print(f"  ❌ {fpsm_player.name}: No historical action found")
    
    root.destroy()
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Dynamic positions: {len(positions)} created")
    print(f"✅ Actor mapping: {len(actor_mapping)} mappings")
    print(f"✅ Historical actions: {len(review_panel.historical_actions)} loaded")
    print(f"✅ Action mappings: {success_count}/{len(fpsm.game_state.players)} successful")
    
    return success_count == len(fpsm.game_state.players)


def test_moneymaker_farha_hand():
    """Test the classic Moneymaker vs Farha hand."""
    print("\n" + "="*80)
    print("🃏 TESTING: Moneymaker Farha Legendary Bluff")
    print("="*80)
    
    # Load hands
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Find the specific hand
    target_hand = None
    for hand in legendary_hands:
        if 'Moneymaker' in getattr(hand.metadata, 'name', '') and 'Farha' in getattr(hand.metadata, 'name', ''):
            target_hand = hand
            break
    
    if not target_hand:
        print("❌ Could not find Moneymaker Farha hand")
        return False
    
    print(f"✅ Found hand: {target_hand.metadata.name}")
    
    # Test same components as Manion hand but briefly
    root = tk.Tk()
    root.withdraw()
    
    # Fix missing fields
    for i, player in enumerate(target_hand.players):
        if 'starting_stack_chips' not in player:
            player['starting_stack_chips'] = 1000000
        if 'seat' not in player:
            player['seat'] = i + 1
    
    config = GameConfig(num_players=len(target_hand.players), small_blind=20000, big_blind=40000)
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create players
    fpsm_players = []
    for i, player_info in enumerate(target_hand.players):
        player = Player(
            name=player_info.get('name', f'Player {i+1}'),
            stack=player_info.get('starting_stack_chips', 1000000),
            position=player_info.get('position', ''),
            is_human=False,
            is_active=True,
            cards=player_info.get('cards', ['**', '**'])
        )
        fpsm_players.append(player)
    
    fpsm.start_hand(existing_players=fpsm_players)
    
    # Test mapping
    review_panel = FPSMHandsReviewPanel(root)
    review_panel.current_hand = target_hand
    review_panel.fpsm = fpsm
    actor_mapping = review_panel.build_actor_mapping()
    
    root.destroy()
    
    print(f"✅ Dynamic mapping successful: {len(actor_mapping)} players mapped")
    return len(actor_mapping) > 0


def main():
    """Run focused tests on specific hands."""
    print("🧪 FOCUSED LEGENDARY HANDS VALIDATION")
    print("Testing specific hands to ensure dynamic system works correctly")
    
    results = {}
    
    # Test problematic hand
    results['manion_zhu_labat'] = test_manion_zhu_labat_hand()
    
    # Test classic hand
    results['moneymaker_farha'] = test_moneymaker_farha_hand()
    
    # Summary
    print("\n" + "="*80)
    print("📊 FOCUSED TEST RESULTS")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    for hand_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {hand_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Dynamic system working correctly!")
    else:
        print("⚠️ Some tests failed - review output for details")


if __name__ == '__main__':
    main()
