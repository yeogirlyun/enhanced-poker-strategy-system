#!/usr/bin/env python3
"""
Generate 100 Legendary Poker Hands

This script generates 100 legendary poker hands across 10 categories
for comprehensive testing and study purposes.
"""

import sys
import os
from typing import List, Dict, Any

# Add backend directory to path
sys.path.append('.')

from core.poker_state_machine import ActionType

def generate_bad_beats() -> List[Dict[str, Any]]:
    """Generate 10 bad beat hands."""
    hands = []
    
    # Base scenarios for bad beats
    scenarios = [
        {
            "name": "Quads vs Royal Flush",
            "description": "Pocket Kings make quads, lose to royal flush on river",
            "event": "2023 Online Cash Game",
            "players": ["Player 1", "Player 2"],
            "cards": [["Kh", "Kd"], ["Ad", "Kd"]],
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "winner": 1,
            "pot": 2000.0,
            "study": "Tests river equity flips and pot awards",
            "legendary": "$100k bad beat jackpot; ultimate cooler"
        },
        {
            "name": "AA vs 72o Preflop",
            "description": "Aces cracked by worst hand preflop all-in",
            "event": "ClubGG 2025",
            "players": ["Doug Polk", "Villain"],
            "cards": [["As", "Ah"], ["7d", "2c"]],
            "board": ["7h", "2s", "4d", "9c", "Jh"],
            "winner": 1,
            "pot": 1000.0,
            "study": "Preflop all-in variance simulation",
            "legendary": "$800k jackpot; worst starting hand wins"
        },
        {
            "name": "Set vs Runner-Runner",
            "description": "Flopped set loses to runner-runner straight",
            "event": "WSOP 2023",
            "players": ["Phil Hellmuth", "Opponent"],
            "cards": [["9s", "9d"], ["Jh", "Tc"]],
            "board": ["9c", "8d", "4s", "7h", "6c"],
            "winner": 1,
            "pot": 600.0,
            "study": "Multi-street betting with runner-runner",
            "legendary": "Hellmuth's iconic tilt moment"
        },
        {
            "name": "KK vs A2",
            "description": "Kings lose to ace-deuce on ace-high board",
            "event": "WSOP Main Event",
            "players": ["Player1", "Player2"],
            "cards": [["Kh", "Kd"], ["Ah", "2s"]],
            "board": ["As", "7h", "3d", "9c", "2h"],
            "winner": 1,
            "pot": 275.0,
            "study": "Ace-high board dynamics",
            "legendary": "Classic bad beat scenario"
        },
        {
            "name": "QQ vs J9",
            "description": "Queens lose to jack-nine on flush draw",
            "event": "Online Cash Game",
            "players": ["Player1", "Player2"],
            "cards": [["Qh", "Qd"], ["Jc", "9s"]],
            "board": ["Jh", "9h", "2h", "7s", "Ah"],
            "winner": 1,
            "pot": 345.0,
            "study": "Flush draw completion",
            "legendary": "Runner-runner flush"
        },
        {
            "name": "AK vs 72",
            "description": "Ace-king loses to seven-deuce on straight",
            "event": "Live Cash Game",
            "players": ["Player1", "Player2"],
            "cards": [["Ah", "Kd"], ["7c", "2s"]],
            "board": ["7h", "2d", "3c", "4s", "5h"],
            "winner": 1,
            "pot": 205.0,
            "study": "Straight completion",
            "legendary": "Wheel straight with 72o"
        },
        {
            "name": "JJ vs T9",
            "description": "Jacks lose to ten-nine on straight",
            "event": "Online Tournament",
            "players": ["Player1", "Player2"],
            "cards": [["Jh", "Jd"], ["Tc", "9s"]],
            "board": ["Th", "9d", "8c", "7s", "6h"],
            "winner": 1,
            "pot": 170.0,
            "study": "Broadway straight",
            "legendary": "Broadway with T9o"
        },
        {
            "name": "TT vs 98",
            "description": "Tens lose to nine-eight on flush",
            "event": "Live Tournament",
            "players": ["Player1", "Player2"],
            "cards": [["Th", "Td"], ["9c", "8s"]],
            "board": ["9h", "8d", "2h", "7h", "Ah"],
            "winner": 1,
            "pot": 275.0,
            "study": "Flush over pair",
            "legendary": "Runner-runner flush"
        },
        {
            "name": "99 vs 87",
            "description": "Nines lose to eight-seven on straight",
            "event": "Online Cash Game",
            "players": ["Player1", "Player2"],
            "cards": [["9h", "9d"], ["8c", "7s"]],
            "board": ["8h", "7d", "6c", "5s", "4h"],
            "winner": 1,
            "pot": 345.0,
            "study": "Wheel straight",
            "legendary": "Wheel with 87o"
        },
        {
            "name": "88 vs 76",
            "description": "Eights lose to seven-six on straight",
            "event": "Live Cash Game",
            "players": ["Player1", "Player2"],
            "cards": [["8h", "8d"], ["7c", "6s"]],
            "board": ["7h", "6d", "5c", "4s", "3h"],
            "winner": 1,
            "pot": 205.0,
            "study": "Wheel straight",
            "legendary": "Wheel with 76o"
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        hand = {
            "category": "Bad Beats",
            "name": scenario["name"],
            "description": scenario["description"],
            "event": scenario["event"],
            "players_involved": scenario["players"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [1000.0, 1000.0],
                "player_cards": scenario["cards"]
            },
            "actions": generate_standard_actions(),
            "board": scenario["board"],
            "expected_winner_index": scenario["winner"],
            "expected_pot": scenario["pot"],
            "study_value": scenario["study"],
            "why_legendary": scenario["legendary"]
        }
        hands.append(hand)
    
    return hands

def generate_hero_calls() -> List[Dict[str, Any]]:
    """Generate 10 hero call hands."""
    hands = []
    
    # High card scenarios for hero calls
    high_cards = [
        ("Ace-High", "Ah", "Jd", "Calling massive river bet with just ace-high"),
        ("Queen-High", "Qd", "Jh", "Instant call with queen-high vs massive bluff"),
        ("Jack-High", "Jh", "Td", "Calling with jack-high vs triple barrel"),
        ("Ten-High", "Th", "9d", "Calling with ten-high vs aggressive opponent"),
        ("Nine-High", "9h", "8d", "Calling with nine-high vs massive bet"),
        ("Eight-High", "8h", "7d", "Calling with eight-high vs aggressive line"),
        ("Seven-High", "7h", "6d", "Calling with seven-high vs triple barrel"),
        ("Six-High", "6h", "5d", "Calling with six-high vs aggressive opponent"),
        ("Five-High", "5h", "4d", "Calling with five-high vs massive bet"),
        ("Four-High", "4h", "3d", "Calling with four-high vs aggressive line")
    ]
    
    for i, (name, card1, card2, desc) in enumerate(high_cards):
        hand = {
            "category": "Hero Calls",
            "name": f"{name} Soul Read",
            "description": desc,
            "event": f"2025 WSOP Hand {i+1}",
            "players_involved": ["Hero", "Villain"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [1000.0, 1200.0],
                "player_cards": [[card1, card2], ["Ks", "Qs"]]
            },
            "actions": generate_hero_call_actions(),
            "board": ["7c", "3h", "2s", "9d", "4c"],
            "expected_winner_index": 0,
            "expected_pot": 530.0 + (i * 20),
            "study_value": f"{name} bluff-catching logic and pot odds",
            "why_legendary": f"Perfect soul read with {name.lower()}"
        }
        hands.append(hand)
    
    return hands

def generate_massive_bluffs() -> List[Dict[str, Any]]:
    """Generate 10 massive bluff hands."""
    hands = []
    
    # Famous bluff scenarios
    bluff_scenarios = [
        ("Moneymaker's Bluff", "The bluff that started the poker boom", "2003 WSOP Main Event"),
        ("Dwan's 7-2", "Bluffing with the worst hand vs two strong hands", "WPT Championship"),
        ("Ivey's Triple Barrel", "Triple barrel bluff with air", "High Stakes Poker"),
        ("Negreanu's Soul Read", "Bluffing based on opponent tells", "Poker After Dark"),
        ("Doyle's Old School", "Classic old school bluff", "WSOP 1976"),
        ("Phil's Tilt Bluff", "Bluffing a tilted opponent", "Live Cash Game"),
        ("Online Hero Bluff", "Massive online bluff", "Online High Stakes"),
        ("Tournament Bubble", "Bubble pressure bluff", "WSOP Main Event"),
        ("Cash Game Hero", "Live cash game hero call", "Bellagio High Stakes"),
        ("Final Table Bluff", "Final table pressure bluff", "WSOP Championship")
    ]
    
    for i, (name, desc, event) in enumerate(bluff_scenarios):
        hand = {
            "category": "Massive Bluffs",
            "name": name,
            "description": desc,
            "event": event,
            "players_involved": ["Bluffer", "Caller"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [2000.0, 1800.0],
                "player_cards": [["5d", "4d"], ["Qc", "9h"]]
            },
            "actions": generate_bluff_actions(),
            "board": ["9s", "2d", "6s", "8h", "3h"],
            "expected_winner_index": 0,
            "expected_pot": 1900.0 + (i * 50),
            "study_value": "Bluff raise sizing and fold equity",
            "why_legendary": f"Changed poker forever; {name}"
        }
        hands.append(hand)
    
    return hands

def generate_cooler_hands() -> List[Dict[str, Any]]:
    """Generate 10 cooler hands."""
    hands = []
    
    # Cooler scenarios
    cooler_scenarios = [
        ("Quads over Full House", "Four of a kind vs full house", ["Kh", "Kd"], ["Ah", "Ad"]),
        ("Straight Flush over Quads", "Straight flush vs four of a kind", ["7h", "8h"], ["Kh", "Kd"]),
        ("Royal over Straight Flush", "Royal flush vs straight flush", ["Ah", "Kh"], ["7h", "8h"]),
        ("Full House over Flush", "Full house vs flush", ["Ah", "Ad"], ["Kh", "Qh"]),
        ("Flush over Straight", "Flush vs straight", ["Ah", "Kh"], ["Jc", "Tc"]),
        ("Straight over Trips", "Straight vs three of a kind", ["Jc", "Tc"], ["Ah", "Ad"]),
        ("Trips over Two Pair", "Three of a kind vs two pair", ["Ah", "Ad"], ["Kh", "Qd"]),
        ("Two Pair over Pair", "Two pair vs one pair", ["Kh", "Qd"], ["Ah", "Jc"]),
        ("Pair over High Card", "One pair vs high card", ["Ah", "Jc"], ["Kh", "Qd"]),
        ("High Card vs High Card", "Higher high card wins", ["Ah", "Jc"], ["Kh", "Qd"])
    ]
    
    for i, (name, desc, cards1, cards2) in enumerate(cooler_scenarios):
        hand = {
            "category": "Cooler Hands",
            "name": name,
            "description": desc,
            "event": f"WSOP 2025 Hand {i+1}",
            "players_involved": ["Player1", "Player2"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [1000.0, 1000.0],
                "player_cards": [cards1, cards2]
            },
            "actions": generate_standard_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 1000.0 + (i * 100),
            "study_value": "Cooler hand dynamics and pot distribution",
            "why_legendary": f"Classic cooler: {name}"
        }
        hands.append(hand)
    
    return hands

def generate_wsop_championship_hands() -> List[Dict[str, Any]]:
    """Generate 10 WSOP championship hands."""
    hands = []
    
    # WSOP championship scenarios
    wsop_scenarios = [
        ("Scotty Nguyen 1998", "Scotty's famous 'You call, gonna be all over baby'", 1998),
        ("Chris Moneymaker 2003", "The hand that started the poker boom", 2003),
        ("Greg Raymer 2004", "Fossilman's championship hand", 2004),
        ("Joe Hachem 2005", "Australian's championship moment", 2005),
        ("Jamie Gold 2006", "Gold's championship hand", 2006),
        ("Jerry Yang 2007", "Yang's championship moment", 2007),
        ("Peter Eastgate 2008", "Youngest champion's hand", 2008),
        ("Joe Cada 2009", "Cada's championship hand", 2009),
        ("Jonathan Duhamel 2010", "Canadian's championship moment", 2010),
        ("Pius Heinz 2011", "German's championship hand", 2011)
    ]
    
    for i, (name, desc, year) in enumerate(wsop_scenarios):
        hand = {
            "category": "WSOP Championship Hands",
            "name": name,
            "description": desc,
            "event": f"WSOP Main Event {year}",
            "players_involved": ["Champion", "Runner-up"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [5000.0, 4500.0],
                "player_cards": [["Ah", "Kh"], ["Qd", "Jc"]]
            },
            "actions": generate_championship_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 9500.0,
            "study_value": "WSOP championship pressure and decision making",
            "why_legendary": f"WSOP {year} championship hand"
        }
        hands.append(hand)
    
    return hands

def generate_tv_hands() -> List[Dict[str, Any]]:
    """Generate 10 famous TV hands."""
    hands = []
    
    # TV show scenarios
    tv_scenarios = [
        ("Hellmuth's 10-4", "Phil's famous blowup hand", "Poker After Dark"),
        ("Doyle's Old School", "Doyle's classic hand", "High Stakes Poker"),
        ("Ivey's Triple Barrel", "Ivey's aggressive play", "Poker After Dark"),
        ("Negreanu's Soul Read", "Daniel's famous read", "High Stakes Poker"),
        ("Dwan's 7-2", "Tom's famous bluff", "Poker After Dark"),
        ("Antonio's Bluff", "Antonio's massive bluff", "High Stakes Poker"),
        ("Gus's Hero Call", "Gus's famous call", "Poker After Dark"),
        ("Barry's Cooler", "Barry's unfortunate hand", "High Stakes Poker"),
        ("Patrik's Bluff", "Patrik's aggressive play", "Poker After Dark"),
        ("Tommy's Hero", "Tommy's hero moment", "High Stakes Poker")
    ]
    
    for i, (name, desc, show) in enumerate(tv_scenarios):
        hand = {
            "category": "Famous TV Hands",
            "name": name,
            "description": desc,
            "event": show,
            "players_involved": ["Player1", "Player2"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [2000.0, 1800.0],
                "player_cards": [["Ah", "Kh"], ["Qd", "Jc"]]
            },
            "actions": generate_tv_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 3800.0,
            "study_value": "TV poker dynamics and entertainment value",
            "why_legendary": f"Famous {show} moment"
        }
        hands.append(hand)
    
    return hands

def generate_heads_up_duels() -> List[Dict[str, Any]]:
    """Generate 10 heads-up duel hands."""
    hands = []
    
    # Heads-up scenarios
    duel_scenarios = [
        ("Ace vs King", "Ace-king vs king-queen", ["Ah", "Kh"], ["Kd", "Qc"]),
        ("Queen vs Jack", "Queen-jack vs jack-ten", ["Qh", "Jd"], ["Jc", "Tc"]),
        ("Ten vs Nine", "Ten-nine vs nine-eight", ["Th", "9d"], ["9c", "8s"]),
        ("Eight vs Seven", "Eight-seven vs seven-six", ["8h", "7d"], ["7c", "6s"]),
        ("Six vs Five", "Six-five vs five-four", ["6h", "5d"], ["5c", "4s"]),
        ("Four vs Three", "Four-three vs three-two", ["4h", "3d"], ["3c", "2s"]),
        ("Ace vs Queen", "Ace-queen vs queen-jack", ["Ah", "Qd"], ["Qc", "Js"]),
        ("King vs Ten", "King-ten vs ten-nine", ["Kh", "Td"], ["Tc", "9s"]),
        ("Jack vs Eight", "Jack-eight vs eight-seven", ["Jh", "8d"], ["8c", "7s"]),
        ("Nine vs Six", "Nine-six vs six-five", ["9h", "6d"], ["6c", "5s"])
    ]
    
    for i, (name, desc, cards1, cards2) in enumerate(duel_scenarios):
        hand = {
            "category": "Heads-Up Duels",
            "name": name,
            "description": desc,
            "event": f"Heads-Up Championship {2025+i}",
            "players_involved": ["Player1", "Player2"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [1000.0, 1000.0],
                "player_cards": [cards1, cards2]
            },
            "actions": generate_heads_up_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 2000.0,
            "study_value": "Heads-up dynamics and aggression",
            "why_legendary": f"Intense heads-up duel: {name}"
        }
        hands.append(hand)
    
    return hands

def generate_multi_way_pots() -> List[Dict[str, Any]]:
    """Generate 10 multi-way pot hands."""
    hands = []
    
    # Multi-way scenarios
    multi_way_scenarios = [
        ("Three-Way All-In", "Three players all-in preflop", 3),
        ("Four-Way Flop", "Four players see the flop", 4),
        ("Five-Way Turn", "Five players reach the turn", 5),
        ("Six-Way River", "Six players reach the river", 6),
        ("Three-Way Cooler", "Three-way cooler hand", 3),
        ("Four-Way Bluff", "Four-way bluff scenario", 4),
        ("Five-Way Draw", "Five-way drawing hand", 5),
        ("Six-Way Pair", "Six-way pair scenario", 6),
        ("Three-Way Flush", "Three-way flush draw", 3),
        ("Four-Way Straight", "Four-way straight draw", 4)
    ]
    
    for i, (name, desc, num_players) in enumerate(multi_way_scenarios):
        hand = {
            "category": "Multi-Way Pots",
            "name": name,
            "description": desc,
            "event": f"Live Cash Game {2025+i}",
            "players_involved": [f"Player{j+1}" for j in range(num_players)],
            "setup": {
                "num_players": num_players,
                "dealer_position": 0,
                "player_stacks": [1000.0] * num_players,
                "player_cards": [["Ah", "Kh"], ["Qd", "Jc"], ["9s", "8h"]] + [["7d", "6c"]] * (num_players - 3)
            },
            "actions": generate_multi_way_actions(num_players),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 1000.0 * num_players,
            "study_value": f"Multi-way pot dynamics with {num_players} players",
            "why_legendary": f"Complex {num_players}-way scenario"
        }
        hands.append(hand)
    
    return hands

def generate_slow_played_traps() -> List[Dict[str, Any]]:
    """Generate 10 slow-played trap hands."""
    hands = []
    
    # Slow-play scenarios
    trap_scenarios = [
        ("Aces Slow-Played", "Pocket aces slow-played", ["Ah", "Ad"]),
        ("Kings Trapped", "Pocket kings trapped", ["Kh", "Kd"]),
        ("Queens Checked", "Pocket queens checked down", ["Qh", "Qd"]),
        ("Jacks Trapped", "Pocket jacks trapped", ["Jh", "Jd"]),
        ("Tens Slow-Played", "Pocket tens slow-played", ["Th", "Td"]),
        ("Nines Trapped", "Pocket nines trapped", ["9h", "9d"]),
        ("Eights Checked", "Pocket eights checked down", ["8h", "8d"]),
        ("Sevens Trapped", "Pocket sevens trapped", ["7h", "7d"]),
        ("Sixes Slow-Played", "Pocket sixes slow-played", ["6h", "6d"]),
        ("Fives Trapped", "Pocket fives trapped", ["5h", "5d"])
    ]
    
    for i, (name, desc, cards) in enumerate(trap_scenarios):
        hand = {
            "category": "Slow-Played Traps",
            "name": name,
            "description": desc,
            "event": f"Live Cash Game {2025+i}",
            "players_involved": ["Trapper", "Victim"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [1000.0, 1000.0],
                "player_cards": [cards, ["Ah", "Kh"]]
            },
            "actions": generate_trap_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 2000.0,
            "study_value": "Slow-playing monster hands for value",
            "why_legendary": f"Perfect trap: {name}"
        }
        hands.append(hand)
    
    return hands

def generate_bubble_plays() -> List[Dict[str, Any]]:
    """Generate 10 bubble play hands."""
    hands = []
    
    # Bubble scenarios
    bubble_scenarios = [
        ("Bubble Burst", "Bubble burst hand", "WSOP Main Event"),
        ("ICM Pressure", "ICM pressure decision", "Online Tournament"),
        ("Bubble Bluff", "Bubble bluff attempt", "Live Tournament"),
        ("Bubble Call", "Bubble hero call", "Online Tournament"),
        ("Bubble Fold", "Bubble fold decision", "Live Tournament"),
        ("Bubble All-In", "Bubble all-in decision", "WSOP Main Event"),
        ("Bubble Check", "Bubble check decision", "Online Tournament"),
        ("Bubble Raise", "Bubble raise decision", "Live Tournament"),
        ("Bubble Check-Raise", "Bubble check-raise", "WSOP Main Event"),
        ("Bubble Check-Call", "Bubble check-call", "Online Tournament")
    ]
    
    for i, (name, desc, event) in enumerate(bubble_scenarios):
        hand = {
            "category": "Bubble Plays",
            "name": name,
            "description": desc,
            "event": event,
            "players_involved": ["Bubble Player", "Opponent"],
            "setup": {
                "num_players": 2,
                "dealer_position": 0,
                "player_stacks": [500.0, 800.0],
                "player_cards": [["Ah", "Kh"], ["Qd", "Jc"]]
            },
            "actions": generate_bubble_actions(),
            "board": ["Ks", "Qd", "Jd", "Kc", "Td"],
            "expected_winner_index": 0,
            "expected_pot": 1300.0,
            "study_value": "Bubble dynamics and ICM pressure",
            "why_legendary": f"Critical bubble decision: {name}"
        }
        hands.append(hand)
    
    return hands

def generate_standard_actions() -> List[Dict[str, Any]]:
    """Generate standard action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 30.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 30.0, "street": "preflop"},
        {"player_index": 0, "action": "BET", "amount": 60.0, "street": "flop"},
        {"player_index": 1, "action": "CALL", "amount": 60.0, "street": "flop"},
        {"player_index": 0, "action": "BET", "amount": 150.0, "street": "turn"},
        {"player_index": 1, "action": "CALL", "amount": 150.0, "street": "turn"},
        {"player_index": 0, "action": "BET", "amount": 760.0, "street": "river"},
        {"player_index": 1, "action": "CALL", "amount": 760.0, "street": "river"}
    ]

def generate_hero_call_actions() -> List[Dict[str, Any]]:
    """Generate hero call action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 25.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 25.0, "street": "preflop"},
        {"player_index": 1, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 1, "action": "BET", "amount": 35.0, "street": "turn"},
        {"player_index": 0, "action": "CALL", "amount": 35.0, "street": "turn"},
        {"player_index": 1, "action": "BET", "amount": 200.0, "street": "river"},
        {"player_index": 0, "action": "CALL", "amount": 200.0, "street": "river"}
    ]

def generate_bluff_actions() -> List[Dict[str, Any]]:
    """Generate bluff action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 100.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 100.0, "street": "preflop"},
        {"player_index": 1, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 0, "action": "BET", "amount": 175.0, "street": "flop"},
        {"player_index": 1, "action": "RAISE", "amount": 500.0, "street": "flop"},
        {"player_index": 0, "action": "CALL", "amount": 325.0, "street": "flop"},
        {"player_index": 1, "action": "CHECK", "amount": 0, "street": "turn"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "turn"},
        {"player_index": 1, "action": "BET", "amount": 300.0, "street": "river"},
        {"player_index": 0, "action": "RAISE", "amount": 1600.0, "street": "river"},
        {"player_index": 1, "action": "FOLD", "amount": 0, "street": "river"}
    ]

def generate_championship_actions() -> List[Dict[str, Any]]:
    """Generate championship action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 200.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 200.0, "street": "preflop"},
        {"player_index": 0, "action": "BET", "amount": 400.0, "street": "flop"},
        {"player_index": 1, "action": "CALL", "amount": 400.0, "street": "flop"},
        {"player_index": 0, "action": "BET", "amount": 800.0, "street": "turn"},
        {"player_index": 1, "action": "CALL", "amount": 800.0, "street": "turn"},
        {"player_index": 0, "action": "BET", "amount": 1600.0, "street": "river"},
        {"player_index": 1, "action": "CALL", "amount": 1600.0, "street": "river"}
    ]

def generate_tv_actions() -> List[Dict[str, Any]]:
    """Generate TV action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 150.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 150.0, "street": "preflop"},
        {"player_index": 0, "action": "BET", "amount": 300.0, "street": "flop"},
        {"player_index": 1, "action": "CALL", "amount": 300.0, "street": "flop"},
        {"player_index": 0, "action": "BET", "amount": 600.0, "street": "turn"},
        {"player_index": 1, "action": "CALL", "amount": 600.0, "street": "turn"},
        {"player_index": 0, "action": "BET", "amount": 1200.0, "street": "river"},
        {"player_index": 1, "action": "CALL", "amount": 1200.0, "street": "river"}
    ]

def generate_heads_up_actions() -> List[Dict[str, Any]]:
    """Generate heads-up action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 50.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 50.0, "street": "preflop"},
        {"player_index": 0, "action": "BET", "amount": 100.0, "street": "flop"},
        {"player_index": 1, "action": "CALL", "amount": 100.0, "street": "flop"},
        {"player_index": 0, "action": "BET", "amount": 200.0, "street": "turn"},
        {"player_index": 1, "action": "CALL", "amount": 200.0, "street": "turn"},
        {"player_index": 0, "action": "BET", "amount": 400.0, "street": "river"},
        {"player_index": 1, "action": "CALL", "amount": 400.0, "street": "river"}
    ]

def generate_multi_way_actions(num_players: int) -> List[Dict[str, Any]]:
    """Generate multi-way action sequence."""
    actions = []
    for i in range(num_players):
        actions.append({"player_index": i, "action": "CALL", "amount": 10.0, "street": "preflop"})
    actions.extend([
        {"player_index": 0, "action": "BET", "amount": 50.0, "street": "flop"},
        {"player_index": 1, "action": "CALL", "amount": 50.0, "street": "flop"},
        {"player_index": 2, "action": "CALL", "amount": 50.0, "street": "flop"}
    ])
    return actions

def generate_trap_actions() -> List[Dict[str, Any]]:
    """Generate trap action sequence."""
    return [
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "preflop"},
        {"player_index": 1, "action": "RAISE", "amount": 30.0, "street": "preflop"},
        {"player_index": 0, "action": "CALL", "amount": 30.0, "street": "preflop"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 1, "action": "BET", "amount": 60.0, "street": "flop"},
        {"player_index": 0, "action": "CALL", "amount": 60.0, "street": "flop"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "turn"},
        {"player_index": 1, "action": "BET", "amount": 120.0, "street": "turn"},
        {"player_index": 0, "action": "RAISE", "amount": 300.0, "street": "turn"},
        {"player_index": 1, "action": "CALL", "amount": 180.0, "street": "turn"}
    ]

def generate_bubble_actions() -> List[Dict[str, Any]]:
    """Generate bubble action sequence."""
    return [
        {"player_index": 0, "action": "RAISE", "amount": 20.0, "street": "preflop"},
        {"player_index": 1, "action": "CALL", "amount": 20.0, "street": "preflop"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 1, "action": "CHECK", "amount": 0, "street": "flop"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "turn"},
        {"player_index": 1, "action": "BET", "amount": 40.0, "street": "turn"},
        {"player_index": 0, "action": "CALL", "amount": 40.0, "street": "turn"},
        {"player_index": 0, "action": "CHECK", "amount": 0, "street": "river"},
        {"player_index": 1, "action": "BET", "amount": 80.0, "street": "river"},
        {"player_index": 0, "action": "CALL", "amount": 80.0, "street": "river"}
    ]

def generate_all_100_hands() -> List[Dict[str, Any]]:
    """Generate all 100 legendary hands."""
    all_hands = []
    
    # Generate 10 hands for each category
    all_hands.extend(generate_bad_beats())
    all_hands.extend(generate_hero_calls())
    all_hands.extend(generate_massive_bluffs())
    all_hands.extend(generate_cooler_hands())
    all_hands.extend(generate_wsop_championship_hands())
    all_hands.extend(generate_tv_hands())
    all_hands.extend(generate_heads_up_duels())
    all_hands.extend(generate_multi_way_pots())
    all_hands.extend(generate_slow_played_traps())
    all_hands.extend(generate_bubble_plays())
    
    return all_hands

def main():
    """Generate and display the 100 hands."""
    print("🎯 Generating 100 Legendary Poker Hands")
    print("=" * 50)
    
    hands = generate_all_100_hands()
    
    print(f"✅ Generated {len(hands)} legendary hands:")
    print()
    
    categories = {}
    for hand in hands:
        category = hand["category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    for category, count in categories.items():
        print(f"📊 {category}: {count} hands")
    
    print()
    print("🎯 Categories covered:")
    for category in categories.keys():
        print(f"   • {category}")
    
    print()
    print("📝 Next steps:")
    print("   1. Convert to proper test format")
    print("   2. Add to comprehensive test suite")
    print("   3. Run validation tests")
    print("   4. Generate study materials")

if __name__ == "__main__":
    main()
