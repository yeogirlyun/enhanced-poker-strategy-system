#!/usr/bin/env python3
"""
Legendary Hands Manager

A comprehensive system to manage, review, and simulate legendary poker hands
stored in JSON format.
"""

import json
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Add backend directory to path
sys.path.append('.')

from core.flexible_poker_state_machine import ActionType, PokerState

@dataclass
class HandSummary:
    """Summary of a legendary hand for quick review."""
    id: str
    category: str
    name: str
    description: str
    event: str
    players_involved: List[str]
    expected_winner_index: int
    expected_pot: float
    study_value: str
    why_legendary: str

class LegendaryHandsManager:
    """Manager for legendary poker hands database."""
    
    def __init__(self, json_file_path: str = "tools_data_generation/legendary_hands.json"):
        """Initialize the manager with the JSON file path."""
        self.json_file_path = json_file_path
        self.data = None
        self.hands = []
        self.load_hands()
    
    def load_hands(self) -> bool:
        """Load hands from JSON file."""
        try:
            with open(self.json_file_path, 'r') as f:
                self.data = json.load(f)
                self.hands = self.data.get('hands', [])
            print(f"✅ Loaded {len(self.hands)} legendary hands from {self.json_file_path}")
            return True
        except FileNotFoundError:
            print(f"❌ File not found: {self.json_file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return False
    
    def save_hands(self) -> bool:
        """Save hands to JSON file."""
        try:
            with open(self.json_file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            print(f"✅ Saved {len(self.hands)} hands to {self.json_file_path}")
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def get_hand_by_id(self, hand_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific hand by ID."""
        for hand in self.hands:
            if hand.get('id') == hand_id:
                return hand
        return None
    
    def get_hands_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all hands in a specific category."""
        return [hand for hand in self.hands if hand.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set()
        for hand in self.hands:
            categories.add(hand.get('category', ''))
        return sorted(list(categories))
    
    def get_hand_summaries(self, category: str = None) -> List[HandSummary]:
        """Get summaries of hands, optionally filtered by category."""
        summaries = []
        target_hands = self.hands if category is None else self.get_hands_by_category(category)
        
        for hand in target_hands:
            summary = HandSummary(
                id=hand.get('id', ''),
                category=hand.get('category', ''),
                name=hand.get('name', ''),
                description=hand.get('description', ''),
                event=hand.get('event', ''),
                players_involved=hand.get('players_involved', []),
                expected_winner_index=hand.get('expected_winner_index', -1),
                expected_pot=hand.get('expected_pot', 0.0),
                study_value=hand.get('study_value', ''),
                why_legendary=hand.get('why_legendary', '')
            )
            summaries.append(summary)
        
        return summaries
    
    def print_hand_summary(self, hand: Dict[str, Any]) -> None:
        """Print a detailed summary of a hand."""
        print(f"\n🎯 {hand.get('name', 'Unknown Hand')}")
        print("=" * 60)
        print(f"📋 ID: {hand.get('id', 'N/A')}")
        print(f"📂 Category: {hand.get('category', 'N/A')}")
        print(f"📝 Description: {hand.get('description', 'N/A')}")
        print(f"🏆 Event: {hand.get('event', 'N/A')}")
        print(f"👥 Players: {', '.join(hand.get('players_involved', []))}")
        print(f"💰 Expected Pot: ${hand.get('expected_pot', 0):.2f}")
        print(f"🏅 Winner: Player {hand.get('expected_winner_index', -1) + 1}")
        print(f"📚 Study Value: {hand.get('study_value', 'N/A')}")
        print(f"⭐ Why Legendary: {hand.get('why_legendary', 'N/A')}")
        
        # Print setup info
        setup = hand.get('setup', {})
        print(f"\n🎮 Setup:")
        print(f"   Players: {setup.get('num_players', 0)}")
        print(f"   Dealer: Position {setup.get('dealer_position', 0)}")
        print(f"   Blinds: ${setup.get('small_blind', 0)}/${setup.get('big_blind', 0)}")
        
        # Print player cards
        player_cards = setup.get('player_cards', [])
        player_stacks = setup.get('player_stacks', [])
        print(f"   Player Cards:")
        for i, (cards, stack) in enumerate(zip(player_cards, player_stacks)):
            print(f"     Player {i+1}: {cards} (Stack: ${stack:.2f})")
        
        # Print board
        board = hand.get('board', [])
        print(f"   Board: {board}")
        
        # Print actions
        actions = hand.get('actions', [])
        print(f"\n🎲 Actions ({len(actions)} total):")
        for i, action in enumerate(actions[:10]):  # Show first 10 actions
            player_idx = action.get('player_index', 0) + 1
            action_type = action.get('action', 'UNKNOWN')
            amount = action.get('amount', 0)
            street = action.get('street', 'preflop')
            print(f"   {i+1:2d}. Player {player_idx} {action_type} ${amount:.1f} ({street})")
        
        if len(actions) > 10:
            print(f"   ... and {len(actions) - 10} more actions")
    
    def simulate_hand(self, hand: Dict[str, Any], verbose: bool = True) -> Dict[str, Any]:
        """Simulate a legendary hand using the poker state machine."""
        if verbose:
            print(f"\n🎮 Simulating: {hand.get('name', 'Unknown Hand')}")
            print("=" * 50)
        
        # Create state machine
        setup = hand.get('setup', {})
        num_players = setup.get('num_players', 2)
        sm = ImprovedPokerStateMachine(num_players=num_players, test_mode=True)
        
        # Configure players
        player_cards = setup.get('player_cards', [])
        player_stacks = setup.get('player_stacks', [])
        
        for i, (cards, stack) in enumerate(zip(player_cards, player_stacks)):
            if i < len(sm.game_state.players):
                player = sm.game_state.players[i]
                player.cards = cards
                player.stack = stack
                player.name = f"Player {i+1}"
        
        # Set blinds
        sm.game_state.small_blind = setup.get('small_blind', 0.5)
        sm.game_state.big_blind = setup.get('big_blind', 1.0)
        
        # Start hand
        sm.start_hand()
        
        # Execute actions
        actions = hand.get('actions', [])
        current_street = "preflop"
        
        for action in actions:
            player_idx = action.get('player_index', 0)
            action_type_str = action.get('action', 'CALL')
            amount = action.get('amount', 0)
            street = action.get('street', 'preflop')
            
            # Convert action string to ActionType
            action_type = getattr(ActionType, action_type_str, ActionType.CALL)
            
            # Handle street transitions
            if street != current_street:
                if current_street == "preflop" and street == "flop":
                    sm.transition_to(PokerState.DEAL_FLOP)
                    current_street = "flop"
                elif current_street == "flop" and street == "turn":
                    sm.transition_to(PokerState.DEAL_TURN)
                    current_street = "turn"
                elif current_street == "turn" and street == "river":
                    sm.transition_to(PokerState.DEAL_RIVER)
                    current_street = "river"
            
            # Execute action
            if player_idx < len(sm.game_state.players):
                player = sm.game_state.players[player_idx]
                try:
                    if action_type == ActionType.CHECK:
                        sm.execute_action(player, ActionType.CHECK, 0)
                    elif action_type == ActionType.FOLD:
                        sm.execute_action(player, ActionType.FOLD, 0)
                    else:
                        sm.execute_action(player, action_type, amount)
                    
                    if verbose:
                        print(f"   Player {player_idx+1} {action_type_str} ${amount:.1f} ({street})")
                        
                except Exception as e:
                    if verbose:
                        print(f"   ❌ Action failed: {e}")
        
        # Set board if provided
        board = hand.get('board', [])
        if board:
            sm.game_state.board = board
        
        # End hand
        sm.transition_to(PokerState.SHOWDOWN)
        
        # Get results
        winners = sm.determine_winner()
        actual_pot = sm.game_state.pot
        
        results = {
            "expected_winner": hand.get('expected_winner_index', -1),
            "actual_winners": [i for i, p in enumerate(sm.game_state.players) if p in winners],
            "expected_pot": hand.get('expected_pot', 0),
            "actual_pot": actual_pot,
            "success": len(winners) > 0 and winners[0] == sm.game_state.players[hand.get('expected_winner_index', 0)]
        }
        
        if verbose:
            print(f"\n📊 Results:")
            print(f"   Expected Winner: Player {results['expected_winner'] + 1}")
            print(f"   Actual Winners: Players {[i+1 for i in results['actual_winners']]}")
            print(f"   Expected Pot: ${results['expected_pot']:.2f}")
            print(f"   Actual Pot: ${results['actual_pot']:.2f}")
            print(f"   Success: {'✅' if results['success'] else '❌'}")
        
        return results
    
    def run_category_simulation(self, category: str, max_hands: int = None) -> Dict[str, Any]:
        """Run simulation for all hands in a category."""
        hands = self.get_hands_by_category(category)
        if max_hands:
            hands = hands[:max_hands]
        
        print(f"\n🎯 Simulating {len(hands)} hands in category: {category}")
        print("=" * 60)
        
        results = {
            "category": category,
            "total_hands": len(hands),
            "successful_simulations": 0,
            "failed_simulations": 0,
            "success_rate": 0.0,
            "hand_results": []
        }
        
        for i, hand in enumerate(hands, 1):
            print(f"\n[{i}/{len(hands)}] Simulating: {hand.get('name', 'Unknown')}")
            
            try:
                hand_result = self.simulate_hand(hand, verbose=False)
                results["hand_results"].append({
                    "hand_id": hand.get('id', ''),
                    "name": hand.get('name', ''),
                    "success": hand_result['success']
                })
                
                if hand_result['success']:
                    results["successful_simulations"] += 1
                    print("   ✅ Success")
                else:
                    results["failed_simulations"] += 1
                    print("   ❌ Failed")
                    
            except Exception as e:
                results["failed_simulations"] += 1
                print(f"   ❌ Error: {e}")
        
        results["success_rate"] = (results["successful_simulations"] / results["total_hands"]) * 100
        
        print(f"\n📊 Category Results:")
        print(f"   Total Hands: {results['total_hands']}")
        print(f"   Successful: {results['successful_simulations']}")
        print(f"   Failed: {results['failed_simulations']}")
        print(f"   Success Rate: {results['success_rate']:.1f}%")
        
        return results
    
    def print_database_summary(self) -> None:
        """Print a summary of the entire database."""
        print("\n🎯 Legendary Hands Database Summary")
        print("=" * 50)
        
        categories = self.get_categories()
        print(f"📊 Total Hands: {len(self.hands)}")
        print(f"📂 Categories: {len(categories)}")
        
        print(f"\n📈 Hands per Category:")
        for category in categories:
            count = len(self.get_hands_by_category(category))
            print(f"   {category}: {count} hands")
        
        print(f"\n🏆 Sample Hands:")
        for category in categories[:5]:  # Show first 5 categories
            hands = self.get_hands_by_category(category)
            if hands:
                sample_hand = hands[0]
                print(f"   {category}: {sample_hand.get('name', 'Unknown')}")

def main():
    """Main function to demonstrate the manager."""
    manager = LegendaryHandsManager()
    
    if not manager.data:
        print("❌ Failed to load hands database")
        return
    
    # Print database summary
    manager.print_database_summary()
    
    # Show sample hand details
    if manager.hands:
        print(f"\n📋 Sample Hand Details:")
        manager.print_hand_summary(manager.hands[0])
    
    # Run simulation for first category
    categories = manager.get_categories()
    if categories:
        print(f"\n🎮 Running Sample Simulation:")
        manager.run_category_simulation(categories[0], max_hands=3)

if __name__ == "__main__":
    main()
