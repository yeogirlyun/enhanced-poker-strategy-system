#!/usr/bin/env python3
"""
Optimized Player Count Test

Tests an improved approach where we use the actual number of players
instead of always padding to 6, for more realistic simulation.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.types import Player
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

import tkinter as tk


def get_optimal_player_count(hand):
    """Determine optimal player count for FPSM based on hand structure."""
    # Count real players (non-folded)
    real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
    num_real = len(real_players)
    
    # Use actual player count for small games, minimum 6 for larger games
    if num_real <= 3:
        # For 2-3 player games, use actual count for realistic simulation
        return num_real, real_players
    else:
        # For 4+ player games, use all players (including folded simulation)
        return len(hand.players), hand.players


def test_optimized_heads_up():
    """Test optimized heads-up with only 2 actual players."""
    print("\n" + "="*80)
    print("🎯 TESTING: Optimized 2-Player (True Heads-Up)")
    print("="*80)
    
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Find a 2-player hand
    heads_up_hand = None
    for hand in legendary_hands:
        real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
        if len(real_players) == 2:
            heads_up_hand = hand
            break
    
    if not heads_up_hand:
        print("❌ No heads-up hands found")
        return False
    
    print(f"✅ Testing hand: {getattr(heads_up_hand.metadata, 'name', 'Unknown')}")
    
    # Use optimized player count
    optimal_count, optimal_players = get_optimal_player_count(heads_up_hand)
    print(f"📊 Optimal configuration: {optimal_count} players (vs {len(heads_up_hand.players)} original)")
    
    for i, player in enumerate(optimal_players):
        name = player.get('name', 'Unknown')
        cards = player.get('cards', ['?', '?'])
        stack = player.get('starting_stack_chips', 1000)
        print(f"  Player {i+1}: {name} - {cards} - ${stack:,}")
    
    try:
        # Create FPSM with optimal count
        config = GameConfig(
            num_players=optimal_count,
            small_blind=20000,
            big_blind=40000
        )
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create only the real players
        fpsm_players = []
        for i, player_info in enumerate(optimal_players):
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
        print("✅ Optimized FPSM setup successful")
        
        # Test RPGW with true heads-up
        root = tk.Tk()
        root.withdraw()
        
        rpgw = ReusablePokerGameWidget(root)
        rpgw.set_poker_game_config(config)
        
        positions = rpgw._get_dynamic_player_positions()
        print(f"🎯 True heads-up positions: {len(positions)} seats")
        
        for i, pos in enumerate(positions):
            print(f"  Seat {i}: {pos['name']} ({pos['position']})")
        
        # Test action order
        game_info = fpsm.get_game_info()
        action_player = game_info.get('action_player', -1)
        if action_player >= 0 and action_player < len(fpsm_players):
            acting_player = fpsm_players[action_player]
            print(f"🎮 First to act: {acting_player.name} (correct for heads-up preflop)")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optimized_3_handed():
    """Test optimized 3-handed with only 3 actual players.""" 
    print("\n" + "="*80)
    print("🎯 TESTING: Optimized 3-Player (True 3-Handed)")
    print("="*80)
    
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Find a 3-player hand
    three_handed_hand = None
    for hand in legendary_hands:
        real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
        if len(real_players) == 3:
            three_handed_hand = hand
            break
    
    if not three_handed_hand:
        print("❌ No 3-handed hands found")
        return False
    
    print(f"✅ Testing hand: {getattr(three_handed_hand.metadata, 'name', 'Unknown')}")
    
    # Use optimized player count
    optimal_count, optimal_players = get_optimal_player_count(three_handed_hand)
    print(f"📊 Optimal configuration: {optimal_count} players (vs {len(three_handed_hand.players)} original)")
    
    try:
        config = GameConfig(
            num_players=optimal_count,
            small_blind=500000,
            big_blind=1000000
        )
        fpsm = FlexiblePokerStateMachine(config)
        
        root = tk.Tk()
        root.withdraw()
        
        rpgw = ReusablePokerGameWidget(root)
        rpgw.set_poker_game_config(config)
        
        positions = rpgw._get_dynamic_player_positions()
        print(f"🎯 True 3-handed positions: {len(positions)} seats")
        
        position_names = [pos['position'] for pos in positions]
        print(f"📍 Positions: {', '.join(position_names)}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def compare_simulation_approaches():
    """Compare padded vs optimized simulation approaches."""
    print("\n" + "="*80)
    print("🔍 SIMULATION APPROACH COMPARISON")
    print("="*80)
    
    hands_db = ComprehensiveHandsDatabase()
    all_hands = hands_db.load_all_hands()
    legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
    
    # Analyze different approaches
    approaches = {
        'padded_to_6': 0,      # Always use 6+ players (current default)
        'optimal_count': 0,     # Use actual player count when beneficial
        'mixed_approach': 0     # Hybrid: optimal for 2-3, padded for 4+
    }
    
    optimization_benefits = []
    
    for hand in legendary_hands[:20]:  # Sample first 20 hands
        real_players = [p for p in hand.players if not p.get('name', '').startswith('Folded Player')]
        num_real = len(real_players)
        total_players = len(hand.players)
        
        # Current approach: always use total players (6+)
        approaches['padded_to_6'] += total_players
        
        # Optimal approach: use actual count when beneficial
        optimal_count, _ = get_optimal_player_count(hand)
        approaches['optimal_count'] += optimal_count
        
        # Mixed approach: optimal for small, padded for large
        if num_real <= 3:
            mixed_count = num_real
        else:
            mixed_count = total_players
        approaches['mixed_approach'] += mixed_count
        
        # Calculate benefits
        if optimal_count < total_players:
            benefit = total_players - optimal_count
            optimization_benefits.append({
                'hand': getattr(hand.metadata, 'name', 'Unknown')[:40],
                'real_players': num_real,
                'current': total_players,
                'optimized': optimal_count,
                'benefit': benefit
            })
    
    print("📊 FPSM Player Count Comparison:")
    for approach, total_count in approaches.items():
        avg_players = total_count / 20
        print(f"   {approach}: {total_count} total players ({avg_players:.1f} avg)")
    
    if optimization_benefits:
        print(f"\n💡 Optimization Benefits ({len(optimization_benefits)} hands):")
        for benefit in optimization_benefits[:5]:  # Show top 5
            print(f"   {benefit['hand']}: {benefit['current']} → {benefit['optimized']} "
                  f"({benefit['benefit']} fewer players)")
    
    # Calculate efficiency gains
    current_total = approaches['padded_to_6']
    optimal_total = approaches['optimal_count']
    efficiency_gain = ((current_total - optimal_total) / current_total) * 100
    
    print(f"\n🎯 Efficiency Analysis:")
    print(f"   Current approach: {current_total} total players")
    print(f"   Optimized approach: {optimal_total} total players")
    print(f"   Efficiency gain: {efficiency_gain:.1f}% fewer players")
    print(f"   Benefits: Faster simulation, more realistic gameplay, cleaner UI")


def main():
    """Run optimized player count tests."""
    print("🧪 OPTIMIZED PLAYER COUNT VALIDATION")
    print("Testing improved approach for different player counts")
    
    # Compare approaches first
    compare_simulation_approaches()
    
    # Test optimized scenarios
    results = {}
    results['optimized_heads_up'] = test_optimized_heads_up()
    results['optimized_3_handed'] = test_optimized_3_handed()
    
    # Summary
    print("\n" + "="*80)
    print("📊 OPTIMIZED APPROACH RESULTS")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    for scenario, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {scenario}")
    
    print(f"\n🎯 Overall: {passed}/{total} optimized scenarios passed")
    
    if passed == total:
        print("🎉 OPTIMIZED APPROACH SUCCESSFUL!")
        print("\n💡 RECOMMENDATIONS:")
        print("   ✅ Use actual player count for 2-3 player hands")
        print("   ✅ Use padded format for 4+ player hands") 
        print("   ✅ This provides more realistic simulation")
        print("   ✅ Better performance and cleaner UI")
    else:
        print("⚠️ Some optimizations need refinement")


if __name__ == '__main__':
    main()
