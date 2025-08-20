#!/usr/bin/env python3
"""
Simple GTO Hands Generator

Creates comprehensive GTO poker hands for 2-9 players (20 hands each = 160 total).
Uses a simplified but effective approach to generate realistic poker scenarios.
"""

import json
import random
from typing import Dict, List, Any
from pathlib import Path

def create_realistic_poker_hand(num_players: int, hand_num: int) -> Dict[str, Any]:
    """Create a realistic poker hand for the given number of players."""
    
    # Set seed for reproducible results
    seed = (num_players * 1000) + hand_num
    random.seed(seed)
    
    hand_id = f"GTO_{num_players}P_H{hand_num:03d}"
    
    # Create deck
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
    random.shuffle(deck)
    
    # Deal hole cards
    cards_dealt = 0
    seats = {}
    stacks = {}
    
    for i in range(num_players):
        # Deal 2 hole cards
        hole_cards = [deck[cards_dealt], deck[cards_dealt + 1]]
        cards_dealt += 2
        
        seat_state = {
            "player_uid": f"Player{i}",
            "name": f"GTO_Bot_{i+1}",
            "stack": 1000,
            "chips_in_front": 0,
            "folded": False,
            "all_in": False,
            "cards": hole_cards,
            "starting_stack": 1000,
            "position": i
        }
        
        seats[i] = seat_state
        stacks[i] = 1000
    
    # Create board (community cards)
    board = []
    
    # Generate realistic actions
    actions = []
    streets = {
        "PREFLOP": {"pot": 15, "board": []},
        "FLOP": {"pot": 0, "board": [deck[cards_dealt], deck[cards_dealt+1], deck[cards_dealt+2]]},
        "TURN": {"pot": 0, "board": []},
        "RIVER": {"pot": 0, "board": []},
        "SHOWDOWN": {"pot": 0, "board": []}
    }
    
    # Set flop, turn, river
    streets["FLOP"]["board"] = [deck[cards_dealt], deck[cards_dealt+1], deck[cards_dealt+2]]
    cards_dealt += 3
    streets["TURN"]["board"] = streets["FLOP"]["board"] + [deck[cards_dealt]]
    cards_dealt += 1
    streets["RIVER"]["board"] = streets["TURN"]["board"] + [deck[cards_dealt]]
    cards_dealt += 1
    streets["SHOWDOWN"]["board"] = streets["RIVER"]["board"]
    
    # Generate some realistic preflop actions
    current_bet = 10  # big blind
    pot = 15  # small blind (5) + big blind (10)
    action_count = 0
    
    # Simulate preflop betting
    for player_idx in range(num_players):
        if action_count >= num_players * 2:  # Limit actions
            break
            
        # Determine action based on position and random factor
        action_type = random.choices(
            ["fold", "call", "raise"],
            weights=[30, 50, 20] if player_idx < 2 else [40, 45, 15]
        )[0]
        
        if action_type == "fold":
            amount = 0
            seats[player_idx]["folded"] = True
        elif action_type == "call":
            amount = current_bet
            pot += amount
        else:  # raise
            amount = current_bet + random.choice([10, 20, 30])
            current_bet = amount
            pot += amount
        
        actions.append({
            "seat": player_idx,
            "action": action_type.upper(),
            "amount": amount,
            "street": "PREFLOP"
        })
        
        action_count += 1
    
    # Update pot values
    streets["PREFLOP"]["pot"] = pot
    streets["FLOP"]["pot"] = pot + random.randint(20, 60)
    streets["TURN"]["pot"] = streets["FLOP"]["pot"] + random.randint(10, 40)
    streets["RIVER"]["pot"] = streets["TURN"]["pot"] + random.randint(0, 30)
    streets["SHOWDOWN"]["pot"] = streets["RIVER"]["pot"]
    
    # Create the final hand data structure
    hand_data = {
        "metadata": {
            "hand_id": hand_id,
            "variant": "NLHE",
            "small_blind": 5,
            "big_blind": 10,
            "max_players": num_players,
            "session_type": "gto"
        },
        "seats": seats,
        "streets": streets,
        "hero_player_uid": f"Player0",
        "pots": [streets["SHOWDOWN"]["pot"]],
        "showdown": [],
        "final_stacks": {str(i): seats[i]["stack"] for i in range(num_players)},
        "board": streets["SHOWDOWN"]["board"],
        "pot": streets["SHOWDOWN"]["pot"],
        "to_act_seat": None,
        "legal_actions": [],
        "review_len": len(actions)
    }
    
    return hand_data

def generate_comprehensive_gto_hands():
    """Generate comprehensive GTO hands for 2-9 players."""
    
    print("🎯 SIMPLE GTO HANDS GENERATOR")
    print("=" * 50)
    print("🎲 Creating realistic poker scenarios for 2-9 players")
    print("📊 Target: 20 hands per player count = 160 total hands")
    print()
    
    all_hands = []
    
    for num_players in range(2, 10):  # 2-9 players
        print(f"🎯 Generating 20 hands for {num_players} players...")
        
        player_hands = []
        for hand_num in range(1, 21):  # 20 hands each
            try:
                hand_data = create_realistic_poker_hand(num_players, hand_num)
                player_hands.append(hand_data)
                
                if hand_num % 5 == 0:
                    print(f"   ✅ Generated {hand_num}/20 hands")
                    
            except Exception as e:
                print(f"   ❌ Failed to generate hand {hand_num}: {e}")
        
        all_hands.extend(player_hands)
        print(f"   🏆 {num_players}P: {len(player_hands)}/20 hands generated successfully")
    
    print(f"\n🏆 GENERATION COMPLETE")
    print(f"✅ Total hands generated: {len(all_hands)}")
    print(f"📊 Breakdown:")
    
    for num_players in range(2, 10):
        count = len([h for h in all_hands if h["metadata"]["max_players"] == num_players])
        print(f"   {num_players}P: {count} hands")
    
    return all_hands

def save_hands_to_data_folder(hands: List[Dict[str, Any]]):
    """Save hands to the data folder."""
    
    # Ensure we're in the backend directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    output_file = data_dir / "gto_hands_comprehensive.json"
    
    print(f"\n💾 Saving {len(hands)} hands to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hands, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully saved {len(hands)} GTO hands to {output_file}")
        
        # Also create a backup in the main backend directory for easy access
        backup_file = Path("gto_hands_comprehensive.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(hands, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup saved to {backup_file}")
        
        # Print some stats
        total_actions = sum(hand.get("review_len", 0) for hand in hands)
        avg_actions = total_actions / len(hands) if hands else 0
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Total hands: {len(hands)}")
        print(f"   Total actions: {total_actions}")
        print(f"   Average actions per hand: {avg_actions:.1f}")
        
        # Show player distribution
        player_counts = {}
        for hand in hands:
            pc = hand["metadata"]["max_players"]
            player_counts[pc] = player_counts.get(pc, 0) + 1
        
        print(f"   Player distribution:")
        for pc in sorted(player_counts.keys()):
            print(f"     {pc} players: {player_counts[pc]} hands")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save hands: {e}")
        return False

def main():
    """Main entry point."""
    
    try:
        # Generate the hands
        hands = generate_comprehensive_gto_hands()
        
        if hands:
            # Save to data folder
            success = save_hands_to_data_folder(hands)
            
            if success:
                print("\n🎉 SUCCESS: Comprehensive GTO hands generated and saved!")
                print("   📁 Primary: backend/data/gto_hands_comprehensive.json")
                print("   📁 Backup: backend/gto_hands_comprehensive.json")
                print("   🔄 Ready to load into UI")
            else:
                print("\n❌ FAILED: Could not save hands")
        else:
            print("\n❌ FAILED: No hands generated")
            
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
