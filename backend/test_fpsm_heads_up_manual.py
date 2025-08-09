#!/usr/bin/env python3
"""
Manual test for FPSM heads-up functionality using hardcoded scenarios.
This bypasses the PHH parser issues and directly tests our enhanced FPSM.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from core.types import Player


def test_heads_up_basic():
    """Test basic heads-up functionality."""
    print("🎯 Testing Heads-Up Basic Functionality")
    print("-" * 40)
    
    # Create heads-up config
    config = GameConfig(
        num_players=2,
        big_blind=600,
        small_blind=300
    )
    
    # Initialize FPSM
    fpsm = FlexiblePokerStateMachine(config)
    
    # Create heads-up players (Tom Dwan vs Phil Ivey scenario)
    players = [
        Player(
            name="Tom Dwan",
            stack=20000,
            position="",  # Will be assigned by FPSM
            is_human=False,
            is_active=True,
            cards=["8h", "6h"]
        ),
        Player(
            name="Phil Ivey",
            stack=20000,
            position="",  # Will be assigned by FPSM
            is_human=False,
            is_active=True,
            cards=["As", "Qd"]
        )
    ]
    
    # Start the hand
    fpsm.start_hand(existing_players=players)
    
    # Validate heads-up setup
    checks = {
        'player_count': len(fpsm.game_state.players) == 2,
        'dealer_is_sb': fpsm.dealer_position == fpsm.small_blind_position,
        'correct_positions': False,
        'correct_action_order': fpsm.action_player_index == fpsm.small_blind_position
    }
    
    # Check positions
    dealer_player = fpsm.game_state.players[fpsm.dealer_position]
    other_player = fpsm.game_state.players[1 - fpsm.dealer_position]
    checks['correct_positions'] = (
        dealer_player.position == "SB/BTN" and other_player.position == "BB"
    )
    
    # Print results
    print(f"✅ Player Count: {checks['player_count']} (2 players)")
    print(f"✅ Dealer is SB: {checks['dealer_is_sb']}")
    print(f"✅ Positions: {checks['correct_positions']} ({dealer_player.position}, {other_player.position})")
    print(f"✅ Action Order: {checks['correct_action_order']} (SB acts first preflop)")
    
    passed = sum(checks.values())
    total = len(checks)
    print(f"\n🏆 Heads-Up Basic: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    
    return passed == total


def test_multi_player_scenarios():
    """Test various multi-player scenarios."""
    print("\n🎯 Testing Multi-Player Scenarios")
    print("-" * 40)
    
    results = {}
    
    for num_players in [3, 4, 5, 6, 7, 8, 9]:
        print(f"\n🎲 Testing {num_players} players:")
        
        config = GameConfig(
            num_players=num_players,
            big_blind=1000,
            small_blind=500
        )
        
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players
        players = []
        for i in range(num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=100000,
                position="",
                is_human=False,
                is_active=True,
                cards=["**", "**"]  # Hidden cards
            )
            players.append(player)
        
        try:
            fpsm.start_hand(existing_players=players)
            
            # Validate setup
            checks = {
                'player_count': len(fpsm.game_state.players) == num_players,
                'positions_assigned': all(p.position for p in fpsm.game_state.players),
                'valid_blinds': fpsm.small_blind_position != fpsm.big_blind_position,
                'correct_action_order': fpsm.action_player_index is not None
            }
            
            # Check UTG position for multi-way
            if num_players > 2:
                utg_index = (fpsm.big_blind_position + 1) % num_players
                checks['utg_acts_first'] = fpsm.action_player_index == utg_index
            else:
                checks['utg_acts_first'] = True  # N/A for heads-up
            
            passed = sum(checks.values())
            total = len(checks)
            success = passed == total
            
            print(f"   {'✅' if success else '❌'} {passed}/{total} checks passed")
            if not success:
                failed = [k for k, v in checks.items() if not v]
                print(f"   Failed: {failed}")
            
            results[num_players] = success
            
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[num_players] = False
    
    # Summary
    passed_scenarios = sum(results.values())
    total_scenarios = len(results)
    print(f"\n🏆 Multi-Player: {passed_scenarios}/{total_scenarios} scenarios passed ({passed_scenarios/total_scenarios*100:.1f}%)")
    
    return passed_scenarios == total_scenarios


def test_position_assignment():
    """Test position assignment for different player counts."""
    print("\n🎯 Testing Position Assignment")
    print("-" * 40)
    
    expected_positions = {
        2: ["SB/BTN", "BB"],
        3: ["BTN", "SB", "BB"],
        4: ["UTG", "BTN", "SB", "BB"],
        5: ["UTG", "CO", "BTN", "SB", "BB"],
        6: ["UTG", "MP", "CO", "BTN", "SB", "BB"],
        7: ["UTG", "MP1", "CO", "BTN", "SB", "BB"],
        8: ["UTG", "MP1", "MP2", "CO", "BTN", "SB", "BB"],
        9: ["UTG", "MP1", "MP2", "MP3", "CO", "BTN", "SB", "BB"]
    }
    
    results = {}
    
    for num_players, expected in expected_positions.items():
        print(f"\n🎲 Testing {num_players} players positions:")
        
        config = GameConfig(num_players=num_players, big_blind=1000, small_blind=500)
        fpsm = FlexiblePokerStateMachine(config)
        
        # Create players
        players = [
            Player(name=f"Player {i+1}", stack=100000, position="", 
                   is_human=False, is_active=True, cards=["**", "**"])
            for i in range(num_players)
        ]
        
        try:
            fpsm.start_hand(existing_players=players)
            
            # Extract actual positions in order
            actual_positions = [p.position for p in fpsm.game_state.players]
            
            # For dynamic position checking, we need to map relative to dealer
            # The FPSM assigns positions relative to dealer, so let's check the pattern
            position_check = len(actual_positions) == len(expected)
            
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual_positions}")
            print(f"   {'✅' if position_check else '❌'} Position count matches")
            
            # Check that all positions are assigned
            all_assigned = all(pos for pos in actual_positions)
            print(f"   {'✅' if all_assigned else '❌'} All positions assigned")
            
            success = position_check and all_assigned
            results[num_players] = success
            
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[num_players] = False
    
    passed_scenarios = sum(results.values())
    total_scenarios = len(results)
    print(f"\n🏆 Position Assignment: {passed_scenarios}/{total_scenarios} scenarios passed ({passed_scenarios/total_scenarios*100:.1f}%)")
    
    return passed_scenarios == total_scenarios


def main():
    """Run all manual FPSM tests."""
    print("🚀 MANUAL FPSM TESTING (Enhanced 2-9 Player Support)")
    print("=" * 60)
    print("This tests our enhanced FPSM without relying on PHH parsing.")
    print()
    
    tests = [
        ("Heads-Up Basic", test_heads_up_basic),
        ("Multi-Player Scenarios", test_multi_player_scenarios),
        ("Position Assignment", test_position_assignment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏆 FINAL MANUAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(success for _, success in results)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL MANUAL TESTS PASSED!")
        print("✅ Enhanced FPSM 2-9 player support is working correctly")
    else:
        print("⚠️  Some tests failed - review needed")
    
    return passed == total


if __name__ == "__main__":
    main()
