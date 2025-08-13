#!/usr/bin/env python3
"""
Generate clean, valid poker session data for hands review testing.
Creates 100 sessions with 2-9 bots, 20 hands each, complete action sequences.
"""

import json
import random
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime

class CleanPokerDataGenerator:
    """Generate clean poker session data with realistic GTO bot behavior."""
    
    def __init__(self):
        self.bot_names = [
            "GTO_Bot_Alpha", "GTO_Bot_Beta", "GTO_Bot_Gamma", "GTO_Bot_Delta",
            "GTO_Bot_Epsilon", "GTO_Bot_Zeta", "GTO_Bot_Eta", "GTO_Bot_Theta",
            "GTO_Bot_Iota", "GTO_Bot_Kappa", "GTO_Bot_Lambda", "GTO_Bot_Mu"
        ]
        
        self.card_deck = [
            '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s',
            '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s',
            '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Tc', 'Td', 'Th', 'Ts',
            'Jc', 'Jd', 'Jh', 'Js', 'Qc', 'Qd', 'Qh', 'Qs', 'Kc', 'Kd', 'Kh', 'Ks',
            'Ac', 'Ad', 'Ah', 'As'
        ]
        
        self.action_types = ['fold', 'check', 'call', 'bet', 'raise']
        self.streets = ['preflop', 'flop', 'turn', 'river']
        
    def generate_card_combinations(self, count: int) -> List[str]:
        """Generate random card combinations without duplicates."""
        return random.sample(self.card_deck, count)
    
    def generate_betting_sequence(self, street: str, num_players: int, pot_size: float, 
                                 current_bet: float, players: List[Dict]) -> Tuple[List[Dict], float]:
        """Generate realistic betting sequence for a street."""
        actions = []
        street_pot = pot_size
        
        # Determine if this street should have betting
        if street == 'preflop':
            # Preflop always has betting
            pass
        elif random.random() < 0.7:  # 70% chance of betting on postflop streets
            pass
        else:
            # Check-check scenario
            for i in range(num_players):
                if players[i].get('is_active', True):
                    actions.append({
                        'actor': i,
                        'player_seat': i,
                        'player_name': players[i]['name'],
                        'action_type': 'check',
                        'amount': 0.0
                    })
            return actions, street_pot
        
        # Generate betting actions
        active_players = [i for i in range(num_players) if players[i].get('is_active', True)]
        random.shuffle(active_players)
        
        for i, player_idx in enumerate(active_players):
            if not players[player_idx].get('is_active', True):
                continue
                
            player = players[player_idx]
            player_stack = player.get('stack', 1000.0)
            player_bet = player.get('current_bet', 0.0)
            
            # Determine action based on position and pot odds
            if i == 0:  # First to act
                if random.random() < 0.3:  # 30% chance to bet/raise
                    action_type = random.choice(['bet', 'raise'])
                    if action_type == 'bet':
                        bet_amount = min(random.uniform(0.5, 0.75) * street_pot, player_stack)
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'bet',
                            'amount': round(bet_amount, 2)
                        })
                        street_pot += bet_amount
                        players[player_idx]['current_bet'] = bet_amount
                        players[player_idx]['stack'] -= bet_amount
                    else:  # raise
                        raise_amount = min(random.uniform(2.0, 3.0) * current_bet, player_stack)
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'raise',
                            'amount': round(raise_amount, 2)
                        })
                        street_pot += raise_amount
                        current_bet = raise_amount
                        players[player_idx]['current_bet'] = raise_amount
                        players[player_idx]['stack'] -= raise_amount
                else:
                    actions.append({
                        'actor': player_idx,
                        'player_seat': player_idx,
                        'player_name': player['name'],
                        'action_type': 'check',
                        'amount': 0.0
                    })
            else:  # Later positions
                if current_bet > player_bet:  # Need to call, raise, or fold
                    if random.random() < 0.4:  # 40% chance to fold
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'fold',
                            'amount': 0.0
                        })
                        players[player_idx]['is_active'] = False
                        players[player_idx]['has_folded'] = True
                    elif random.random() < 0.3:  # 30% chance to raise
                        raise_amount = min(random.uniform(2.0, 3.0) * current_bet, player_stack)
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'raise',
                            'amount': round(raise_amount, 2)
                        })
                        street_pot += raise_amount
                        current_bet = raise_amount
                        players[player_idx]['current_bet'] = raise_amount
                        players[player_idx]['stack'] -= raise_amount
                    else:  # Call
                        call_amount = min(current_bet - player_bet, player_stack)
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'call',
                            'amount': round(call_amount, 2)
                        })
                        street_pot += call_amount
                        players[player_idx]['current_bet'] = current_bet
                        players[player_idx]['stack'] -= call_amount
                else:  # No bet to call
                    if random.random() < 0.3:  # 30% chance to bet
                        bet_amount = min(random.uniform(0.5, 0.75) * street_pot, player_stack)
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'bet',
                            'amount': round(bet_amount, 2)
                        })
                        street_pot += bet_amount
                        current_bet = bet_amount
                        players[player_idx]['current_bet'] = bet_amount
                        players[player_idx]['stack'] -= bet_amount
                    else:
                        actions.append({
                            'actor': player_idx,
                            'player_seat': player_idx,
                            'player_name': player['name'],
                            'action_type': 'check',
                            'amount': 0.0
                        })
        
        return actions, street_pot
    
    def generate_single_hand(self, session_id: str, hand_num: int, num_players: int) -> Dict[str, Any]:
        """Generate a complete poker hand with all streets and actions."""
        
        # Generate player names and starting stacks
        player_names = random.sample(self.bot_names, num_players)
        starting_stacks = [random.uniform(800, 1200) for _ in range(num_players)]
        
        # Initialize players
        players = []
        for i in range(num_players):
            players.append({
                'name': player_names[i],
                'seat': i,
                'stack': round(starting_stacks[i], 2),
                'current_bet': 0.0,
                'hole_cards': [],
                'is_active': True,
                'has_folded': False
            })
        
        # Deal hole cards
        all_cards = self.generate_card_combinations(num_players * 2)
        for i in range(num_players):
            players[i]['hole_cards'] = all_cards[i*2:(i+1)*2]
        
        # Generate board cards
        remaining_cards = [card for card in self.card_deck if card not in all_cards]
        flop_cards = random.sample(remaining_cards, 3)
        remaining_cards = [card for card in remaining_cards if card not in flop_cards]
        turn_card = random.sample(remaining_cards, 1)
        remaining_cards = [card for card in remaining_cards if card not in turn_card]
        river_card = random.sample(remaining_cards, 1)
        
        # Initialize game state
        pot = 0.0
        current_bet = 0.0
        actions = {}
        
        # Preflop betting (with blinds)
        small_blind = 1.0
        big_blind = 2.0
        
        # Post small blind
        if num_players >= 2:
            players[1]['current_bet'] = small_blind
            players[1]['stack'] -= small_blind
            pot += small_blind
        
        # Post big blind
        if num_players >= 3:
            players[2]['current_bet'] = big_blind
            players[2]['stack'] -= big_blind
            pot += big_blind
            current_bet = big_blind
        
        # Generate preflop actions
        preflop_actions, pot = self.generate_betting_sequence('preflop', num_players, pot, current_bet, players)
        actions['preflop'] = preflop_actions
        
        # Check if hand continues to flop
        active_players = [p for p in players if p.get('is_active', True) and not p.get('has_folded', False)]
        if len(active_players) > 1:
            # Generate flop actions
            flop_actions, pot = self.generate_betting_sequence('flop', num_players, pot, 0.0, players)
            actions['flop'] = flop_actions
            
            # Check if hand continues to turn
            active_players = [p for p in players if p.get('is_active', True) and not p.get('has_folded', False)]
            if len(active_players) > 1:
                # Generate turn actions
                turn_actions, pot = self.generate_betting_sequence('turn', num_players, pot, 0.0, players)
                actions['turn'] = turn_actions
                
                # Check if hand continues to river
                active_players = [p for p in players if p.get('is_active', True) and not p.get('has_folded', False)]
                if len(active_players) > 1:
                    # Generate river actions
                    river_actions, pot = self.generate_betting_sequence('river', num_players, pot, 0.0, players)
                    actions['river'] = river_actions
        
        # Create board structure
        board = {
            'flop': flop_cards,
            'turn': turn_card,
            'river': river_card,
            'all_cards': flop_cards + turn_card + river_card
        }
        
        # Determine winner (simplified - just pick random active player)
        active_players = [p for p in players if p.get('is_active', True) and not p.get('has_folded', False)]
        if active_players:
            winner = random.choice(active_players)
            winner_name = winner['name']
        else:
            winner_name = "Split Pot"
        
        # Create hand data
        hand_data = {
            'id': f"{session_id}-H{hand_num:03d}",
            'name': f"Session {session_id} Hand {hand_num} - {num_players} Players",
            'session_id': session_id,
            'hand_number': hand_num,
            'num_players': num_players,
            'players': players,
            'board': board,
            'actions': actions,
            'pot': round(pot, 2),
            'winner': winner_name,
            'timestamp': datetime.now().isoformat()
        }
        
        return hand_data
    
    def generate_session(self, session_id: str) -> Dict[str, Any]:
        """Generate a complete poker session with multiple hands."""
        
        # Random number of players (2-9)
        num_players = random.randint(2, 9)
        
        # Generate 20 hands for this session
        hands = []
        for hand_num in range(1, 21):
            hand = self.generate_single_hand(session_id, hand_num, num_players)
            hands.append(hand)
        
        session_data = {
            'session_id': session_id,
            'num_players': num_players,
            'num_hands': len(hands),
            'timestamp': datetime.now().isoformat(),
            'hands': hands
        }
        
        return session_data
    
    def generate_all_sessions(self, num_sessions: int = 100) -> Dict[str, Any]:
        """Generate multiple poker sessions."""
        
        print(f"🎯 Generating {num_sessions} clean poker sessions...")
        
        all_sessions = []
        for session_num in range(1, num_sessions + 1):
            session_id = f"S{session_num:03d}"
            print(f"  🔧 Generating session {session_id}...")
            
            session = self.generate_session(session_id)
            all_sessions.append(session)
        
        # Create final data structure
        final_data = {
            'metadata': {
                'generator': 'CleanPokerDataGenerator',
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'total_sessions': len(all_sessions),
                'total_hands': sum(len(s['hands']) for s in all_sessions),
                'description': 'Clean poker session data generated for hands review testing'
            },
            'sessions': all_sessions
        }
        
        return final_data

def main():
    """Main function to generate clean poker data."""
    
    print("🚀 Clean Poker Data Generator")
    print("=" * 50)
    
    # Create generator
    generator = CleanPokerDataGenerator()
    
    # Generate 100 sessions
    data = generator.generate_all_sessions(100)
    
    # Save to file
    output_file = 'data/clean_poker_sessions_100.json'
    print(f"\n💾 Saving data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Print summary
    print(f"\n🎉 Generation complete!")
    print(f"📊 Total sessions: {data['metadata']['total_sessions']}")
    print(f"🃏 Total hands: {data['metadata']['total_hands']}")
    print(f"📁 Output file: {output_file}")
    
    # Validate a few hands
    print(f"\n🔍 Validating sample hands...")
    for i, session in enumerate(data['sessions'][:3]):
        print(f"  Session {session['session_id']}: {session['num_hands']} hands, {session['num_players']} players")
        for j, hand in enumerate(session['hands'][:2]):
            print(f"    Hand {hand['id']}: {len(hand['actions'])} streets, pot: ${hand['pot']}")

if __name__ == "__main__":
    main()
