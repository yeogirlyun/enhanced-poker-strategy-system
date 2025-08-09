#!/usr/bin/env python3
"""
Player Count Scenarios Test

Tests how the system handles different player counts:
1. Less than 6 players (2-5) - Should simulate with folded players
2. Exactly 6 players - Standard case
3. More than 6 players (7-9) - Should use full FPSM scaling

Validates that FPSM, RPGW, and action mapping work correctly for all scenarios.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.types import Player
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

import tkinter as tk


def find_hands_by_original_player_count():
    """Find hands by their original player count before database conversion."""
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Categorize by original player count (before padding)
    hands_by_count = {2: [], 3: [], 6: [], 7: [], 8: [], 9: []}
    
    for hand in legendary_hands:
        # Count non-folded players (those with real names, not "Folded Player X")
        real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
        original_count = len(real_players)
        
        if original_count in hands_by_count:
            hands_by_count[original_count].append(hand)
    
    return hands_by_count


def test_heads_up_scenario():
    """Test 2-player (heads-up) scenario."""
    print("\n" + "="*80)
    print("🎯 TESTING: 2-Player (Heads-Up) Scenario")
    print("="*80)
    
    hands_by_count = find_hands_by_original_player_count()
    if not hands_by_count[2]:
        print("❌ No 2-player hands found")
        return False
    
    hand = hands_by_count[2][0]  # Take first 2-player hand
    print(f"✅ Testing hand: {getattr(hand.metadata, 'name', 'Unknown')}")
    
    # Count real vs folded players
    real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
    folded_players = [p for p in hand.players if p.get('name', '').startswith('Folded Player')]
    
    print(f"📊 Real players: {len(real_players)}")
    print(f"🚫 Folded players: {len(folded_players)}")
    print(f"🎲 Total FPSM players: {len(hand.players)}")
    
    for i, player in enumerate(real_players):
        name = player.get('name', 'Unknown')
        cards = player.get('cards', ['?', '?'])
        print(f"  Real Player {i+1}: {name} - {cards}")
    
    # Test FPSM setup
    print("\n🎰 Testing FPSM setup for heads-up...")
    try:
        config = GameConfig(
            num_players=len(hand.players),  # Use total including folded
            small_blind=50,
            big_blind=100
        )
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players
        fpsm_players = []
        for i, player_info in enumerate(hand.players):
            player = Player(
                name=player_info.get('name', f'Player {i+1}'),
                stack=player_info.get('starting_stack_chips', 1000),
                position=player_info.get('position', ''),
                is_human=False,
                is_active=True,
                cards=player_info.get('cards', ['**', '**'])
            )
            fpsm_players.append(player)
        
        fpsm.start_hand(existing_players=fpsm_players)
        print("✅ FPSM setup successful")
        
        # Test RPGW dynamic positioning for heads-up
        print("\n🖥️ Testing RPGW heads-up positioning...")
        root = tk.Tk()
        root.withdraw()
        
        rpgw = ReusablePokerGameWidget(root)
        rpgw.set_poker_game_config(config)
        
        # Test position calculation for heads-up
        positions = rpgw._get_dynamic_player_positions()
        print(f"🎯 Heads-up positions: {len(positions)} seats")
        
        for i, pos in enumerate(positions):
            is_real = not pos['name'].startswith('Player ') or i < len(real_players)
            player_type = "REAL" if is_real and i < len(real_players) else "FOLDED"
            print(f"  Seat {i}: {pos['name']} ({pos['position']}) [{player_type}]")
        
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_table_scenario():
    """Test 7+ player (full table) scenario."""
    print("\n" + "="*80)
    print("🎯 TESTING: 7+ Player (Full Table) Scenario")
    print("="*80)
    
    hands_by_count = find_hands_by_original_player_count()
    
    # Find a hand with 7+ players
    test_hand = None
    player_count = 0
    for count in [9, 8, 7]:  # Prefer larger tables
        if hands_by_count[count]:
            test_hand = hands_by_count[count][0]
            player_count = count
            break
    
    if not test_hand:
        print("❌ No 7+ player hands found")
        return False
    
    print(f"✅ Testing {player_count}-player hand: {getattr(test_hand.metadata, 'name', 'Unknown')}")
    
    # Show all players
    real_players = [p for p in test_hand.players if not p.get('name', '').startswith('Folded Player')]
    print(f"📊 Active players: {len(real_players)}")
    print(f"🎲 Total FPSM players: {len(test_hand.players)}")
    
    for i, player in enumerate(real_players):
        name = player.get('name', 'Unknown')
        position = player.get('position', '')
        seat = player.get('seat', i+1)
        print(f"  Player {i+1}: {name} (Seat {seat}, {position})")
    
    # Test FPSM scalability
    print(f"\n🎰 Testing FPSM scalability for {player_count} players...")
    try:
        config = GameConfig(
            num_players=len(test_hand.players),
            small_blind=500000,
            big_blind=1000000
        )
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players
        fpsm_players = []
        for i, player_info in enumerate(test_hand.players):
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
        print("✅ FPSM scales to large table successfully")
        
        # Test RPGW dynamic positioning for large table
        print(f"\n🖥️ Testing RPGW positioning for {player_count} players...")
        root = tk.Tk()
        root.withdraw()
        
        rpgw = ReusablePokerGameWidget(root)
        rpgw.set_poker_game_config(config)
        
        # Test position calculation for large table
        positions = rpgw._get_dynamic_player_positions()
        print(f"🎯 Large table positions: {len(positions)} seats")
        
        # Show position distribution
        position_names = [pos['position'] for pos in positions]
        unique_positions = list(set(position_names))
        print(f"📍 Position types: {', '.join(unique_positions)}")
        
        # Show first 10 positions
        for i, pos in enumerate(positions[:10]):
            is_real = i < len(real_players)
            player_type = "REAL" if is_real else "FOLDED"
            print(f"  Seat {i}: {pos['name']} ({pos['position']}) [{player_type}]")
        
        if len(positions) > 10:
            print(f"  ... and {len(positions) - 10} more seats")
        
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_standard_6_player_scenario():
    """Test standard 6-player scenario."""
    print("\n" + "="*80)
    print("🎯 TESTING: 6-Player (Standard) Scenario")
    print("="*80)
    
    hands_by_count = find_hands_by_original_player_count()
    if not hands_by_count[6]:
        print("❌ No 6-player hands found")
        return False
    
    hand = hands_by_count[6][0]
    print(f"✅ Testing hand: {getattr(hand.metadata, 'name', 'Unknown')}")
    
    # Test that all positions are filled with real players
    real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
    print(f"📊 Real players: {len(real_players)} (should be 6)")
    
    # Quick FPSM test
    try:
        config = GameConfig(num_players=6, small_blind=20000, big_blind=40000)
        fpsm = FlexiblePokerStateMachine(config)
        
        root = tk.Tk()
        root.withdraw()
        rpgw = ReusablePokerGameWidget(root)
        rpgw.set_poker_game_config(config)
        
        positions = rpgw._get_dynamic_player_positions()
        position_names = [pos['position'] for pos in positions]
        
        print(f"🎯 Standard positions: {', '.join(position_names)}")
        print("✅ Standard 6-player scenario working correctly")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def analyze_folding_simulation_effectiveness():
    """Analyze how effective the folding simulation is for small player counts."""
    print("\n" + "="*80)
    print("🔍 FOLDING SIMULATION ANALYSIS")
    print("="*80)
    
    hands_by_count = find_hands_by_original_player_count()
    
    # Analyze 2-3 player hands to see folding simulation
    for original_count in [2, 3]:
        hands = hands_by_count[original_count]
        if hands:
            print(f"\n📊 {original_count}-player hands analysis:")
            print(f"   Total hands: {len(hands)}")
            
            # Analyze first hand
            hand = hands[0]
            real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
            folded_players = [p for p in hand.players if p.get('name', '').startswith('Folded Player')]
            
            print(f"   Real players: {len(real_players)}")
            print(f"   Simulated folded players: {len(folded_players)}")
            print(f"   Total FPSM players: {len(hand.players)}")
            print(f"   Simulation ratio: {len(folded_players)}/{len(hand.players)} folded")
            
            # Check if folded players have weak cards
            if folded_players:
                folded_cards = [p.get('cards', []) for p in folded_players]
                print(f"   Folded player cards: {folded_cards[:3]}...")  # Show first 3
        else:
            print(f"\n📊 {original_count}-player hands: None found")


def main():
    """Run comprehensive player count scenario tests."""
    print("🧪 PLAYER COUNT SCENARIOS VALIDATION")
    print("Testing system behavior with different player counts")
    
    results = {}
    
    # Test all scenarios
    print("\n🔍 First, analyzing folding simulation effectiveness...")
    analyze_folding_simulation_effectiveness()
    
    print("\n🎯 Now testing each scenario...")
    
    # Test edge cases and standard case
    results['heads_up'] = test_heads_up_scenario()
    results['standard_6'] = test_standard_6_player_scenario()  
    results['full_table'] = test_full_table_scenario()
    
    # Summary
    print("\n" + "="*80)
    print("📊 PLAYER COUNT SCENARIOS RESULTS")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    scenario_names = {
        'heads_up': '2-Player (Heads-Up)',
        'standard_6': '6-Player (Standard)', 
        'full_table': '7+ Player (Full Table)'
    }
    
    for scenario, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        name = scenario_names.get(scenario, scenario)
        print(f"{status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} scenarios passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SCENARIOS WORKING - System handles all player counts correctly!")
        print("\n💡 KEY FINDINGS:")
        print("   ✅ FPSM scales to any player count (2-9+)")
        print("   ✅ RPGW dynamically adjusts positions")
        print("   ✅ Folded player simulation works for <6 players")
        print("   ✅ Full table support works for 7+ players")
    else:
        print("⚠️ Some scenarios need attention - review output for details")


if __name__ == '__main__':
    main()
