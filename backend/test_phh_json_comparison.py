#!/usr/bin/env python3
"""
PHH-to-JSON Content Comparison Tester

This script loads the generated JSON file and compares it back to the original PHH
to ensure 100% data integrity and identify any parsing discrepancies.
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from core.hands_database import ComprehensiveHandsDatabase

class PHHJSONComparisonTester:
    """Compares generated JSON back to original PHH format for validation."""
    
    def __init__(self):
        self.hands_db = ComprehensiveHandsDatabase()
        self.json_data = None
        self.comparison_results = []
        self.critical_errors = []
        self.warnings = []
        
    def run_comprehensive_comparison(self):
        """Run the complete PHH-to-JSON comparison test."""
        print("🔍 COMPREHENSIVE PHH-TO-JSON COMPARISON TEST")
        print("=" * 60)
        
        # Step 1: Load original PHH data
        self.load_original_phh_data()
        
        # Step 2: Load converted JSON data
        self.load_converted_json_data()
        
        # Step 3: Compare each hand
        self.compare_all_hands()
        
        # Step 4: Generate comparison report
        self.generate_comparison_report()
        
        return self.comparison_results
    
    def load_original_phh_data(self):
        """Load the original PHH data."""
        print("📚 Loading original PHH data...")
        
        self.hands_db.load_all_hands()
        original_count = len(self.hands_db.all_hands)
        
        print(f"✅ Loaded {original_count} hands from original PHH files")
    
    def load_converted_json_data(self):
        """Load the converted JSON data."""
        json_file_path = "data/legendary_hands_converted.json"
        
        print(f"📄 Loading converted JSON data from: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            
            json_count = len(self.json_data['hands'])
            print(f"✅ Loaded {json_count} hands from converted JSON file")
            
            # Validate JSON structure
            if self.json_data['total_hands'] != json_count:
                self.critical_errors.append(f"JSON total_hands mismatch: {self.json_data['total_hands']} != {json_count}")
            
        except Exception as e:
            self.critical_errors.append(f"Failed to load JSON file: {str(e)}")
            raise
    
    def compare_all_hands(self):
        """Compare all hands between PHH and JSON formats."""
        print(f"🔄 Comparing {len(self.json_data['hands'])} hands...")
        
        # Create a mapping from JSON hands by ID for efficient lookup
        json_hands_by_id = {hand['metadata']['id']: hand for hand in self.json_data['hands']}
        
        for i, (hand_id, original_hand) in enumerate(self.hands_db.all_hands.items()):
            print(f"  [{i+1:3d}] Comparing: {original_hand.metadata.name}")
            
            # Find corresponding JSON hand
            json_hand = json_hands_by_id.get(hand_id)
            if not json_hand:
                self.critical_errors.append(f"Hand {hand_id} not found in JSON data")
                continue
            
            # Compare this hand
            comparison_result = self.compare_single_hand(original_hand, json_hand)
            self.comparison_results.append(comparison_result)
    
    def compare_single_hand(self, original_hand, json_hand) -> Dict[str, Any]:
        """Compare a single hand between PHH and JSON formats."""
        hand_id = original_hand.metadata.id
        comparison_result = {
            'hand_id': hand_id,
            'hand_name': original_hand.metadata.name,
            'success': True,
            'metadata_match': True,
            'players_match': True,
            'board_match': True,
            'actions_match': True,
            'discrepancies': [],
            'details': {}
        }
        
        try:
            # Compare metadata
            self.compare_metadata(original_hand, json_hand, comparison_result)
            
            # Compare players
            self.compare_players(original_hand, json_hand, comparison_result)
            
            # Compare board cards
            self.compare_board_cards(original_hand, json_hand, comparison_result)
            
            # Compare actions
            self.compare_actions(original_hand, json_hand, comparison_result)
            
            # Overall success determination
            if comparison_result['discrepancies']:
                comparison_result['success'] = False
                
        except Exception as e:
            comparison_result['success'] = False
            comparison_result['discrepancies'].append(f"Comparison failed: {str(e)}")
        
        return comparison_result
    
    def compare_metadata(self, original_hand, json_hand, result):
        """Compare metadata between original and JSON."""
        original_meta = original_hand.metadata
        json_meta = json_hand['metadata']
        
        # Check ID
        if original_meta.id != json_meta['id']:
            result['metadata_match'] = False
            result['discrepancies'].append(f"ID mismatch: {original_meta.id} != {json_meta['id']}")
        
        # Check name
        if original_meta.name != json_meta['name']:
            result['metadata_match'] = False
            result['discrepancies'].append(f"Name mismatch: {original_meta.name} != {json_meta['name']}")
        
        # Store comparison details
        result['details']['metadata'] = {
            'original': {
                'id': original_meta.id,
                'name': original_meta.name,
                'event': getattr(original_meta, 'event', ''),
                'variant': getattr(original_meta, 'variant', '')
            },
            'json': {
                'id': json_meta['id'],
                'name': json_meta['name'],
                'event': json_meta['event'],
                'variant': json_meta['variant']
            }
        }
    
    def compare_players(self, original_hand, json_hand, result):
        """Compare players between original and JSON."""
        original_players = original_hand.players
        json_players = json_hand['players']
        
        if len(original_players) != len(json_players):
            result['players_match'] = False
            result['discrepancies'].append(f"Player count mismatch: {len(original_players)} != {len(json_players)}")
            return
        
        player_discrepancies = []
        
        for i, (orig_player, json_player) in enumerate(zip(original_players, json_players)):
            # Compare names
            orig_name = orig_player.get('name', '')
            json_name = json_player.get('name', '')
            if orig_name != json_name:
                player_discrepancies.append(f"Player {i} name: {orig_name} != {json_name}")
            
            # Compare seats
            orig_seat = orig_player.get('seat', 0)
            json_seat = json_player.get('seat', 0)
            if orig_seat != json_seat:
                player_discrepancies.append(f"Player {i} seat: {orig_seat} != {json_seat}")
            
            # Compare starting stacks
            orig_stack = orig_player.get('starting_stack_chips', 0)
            json_stack = json_player.get('starting_stack_chips', 0)
            if orig_stack != json_stack:
                player_discrepancies.append(f"Player {i} stack: {orig_stack} != {json_stack}")
            
            # Compare cards
            orig_cards = orig_player.get('cards', [])
            json_cards = json_player.get('cards', [])
            if orig_cards != json_cards:
                player_discrepancies.append(f"Player {i} cards: {orig_cards} != {json_cards}")
        
        if player_discrepancies:
            result['players_match'] = False
            result['discrepancies'].extend(player_discrepancies)
        
        result['details']['players'] = {
            'original_count': len(original_players),
            'json_count': len(json_players),
            'discrepancies': player_discrepancies
        }
    
    def compare_board_cards(self, original_hand, json_hand, result):
        """Compare board cards between original and JSON."""
        # Extract original board cards
        original_board = []
        if hasattr(original_hand, 'board_cards') and original_hand.board_cards:
            if isinstance(original_hand.board_cards, dict):
                for street in ['flop', 'turn', 'river']:
                    if street in original_hand.board_cards:
                        street_cards = original_hand.board_cards[street]
                        if isinstance(street_cards, list):
                            original_board.extend(street_cards)
                        elif isinstance(street_cards, str):
                            original_board.append(street_cards)
            elif isinstance(original_hand.board_cards, list):
                original_board = original_hand.board_cards[:]
        
        json_board = json_hand['board_cards']
        
        if original_board != json_board:
            result['board_match'] = False
            result['discrepancies'].append(f"Board cards mismatch: {original_board} != {json_board}")
        
        result['details']['board_cards'] = {
            'original': original_board,
            'json': json_board
        }
    
    def compare_actions(self, original_hand, json_hand, result):
        """Compare actions between original and JSON."""
        original_actions = getattr(original_hand, 'actions', {})
        json_actions = json_hand['actions']
        
        action_discrepancies = []
        
        # Compare each street
        all_streets = set(original_actions.keys()) | set(json_actions.keys())
        
        for street in all_streets:
            orig_street_actions = original_actions.get(street, [])
            json_street_actions = json_actions.get(street, [])
            
            if street not in original_actions:
                action_discrepancies.append(f"Street {street} missing in original")
                continue
            
            if street not in json_actions:
                action_discrepancies.append(f"Street {street} missing in JSON")
                continue
            
            if len(orig_street_actions) != len(json_street_actions):
                action_discrepancies.append(f"Street {street} action count: {len(orig_street_actions)} != {len(json_street_actions)}")
                continue
            
            # Compare individual actions
            for i, (orig_action, json_action) in enumerate(zip(orig_street_actions, json_street_actions)):
                if isinstance(orig_action, dict) and isinstance(json_action, dict):
                    # Compare actor
                    if orig_action.get('actor') != json_action.get('actor'):
                        action_discrepancies.append(f"Street {street} action {i} actor: {orig_action.get('actor')} != {json_action.get('actor')}")
                    
                    # Compare type (normalize case)
                    orig_type = str(orig_action.get('type', '')).upper()
                    json_type = str(json_action.get('type', '')).upper()
                    if orig_type != json_type:
                        action_discrepancies.append(f"Street {street} action {i} type: {orig_type} != {json_type}")
                    
                    # Compare amount (check both 'amount' and 'to' fields)
                    orig_amount = orig_action.get('amount', orig_action.get('to', 0))
                    json_amount = json_action.get('amount', 0)
                    if orig_amount != json_amount:
                        action_discrepancies.append(f"Street {street} action {i} amount: {orig_amount} != {json_amount}")
        
        if action_discrepancies:
            result['actions_match'] = False
            result['discrepancies'].extend(action_discrepancies)
        
        result['details']['actions'] = {
            'original_streets': list(original_actions.keys()),
            'json_streets': list(json_actions.keys()),
            'original_total_actions': sum(len(actions) for actions in original_actions.values()),
            'json_total_actions': sum(len(actions) for actions in json_actions.values()),
            'discrepancies': action_discrepancies
        }
    
    def generate_comparison_report(self):
        """Generate a comprehensive comparison report."""
        print("\n" + "=" * 60)
        print("📋 PHH-TO-JSON COMPARISON REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_hands = len(self.comparison_results)
        successful_matches = sum(1 for result in self.comparison_results if result['success'])
        failed_matches = total_hands - successful_matches
        
        metadata_matches = sum(1 for result in self.comparison_results if result['metadata_match'])
        players_matches = sum(1 for result in self.comparison_results if result['players_match'])
        board_matches = sum(1 for result in self.comparison_results if result['board_match'])
        actions_matches = sum(1 for result in self.comparison_results if result['actions_match'])
        
        print(f"📊 OVERALL COMPARISON STATISTICS:")
        print(f"  Total hands compared: {total_hands}")
        print(f"  Perfect matches: {successful_matches}")
        print(f"  Failed matches: {failed_matches}")
        print(f"  Success rate: {(successful_matches/max(1,total_hands)*100):.1f}%")
        
        print(f"\n📊 COMPONENT MATCH RATES:")
        print(f"  Metadata matches: {metadata_matches}/{total_hands} ({metadata_matches/max(1,total_hands)*100:.1f}%)")
        print(f"  Players matches: {players_matches}/{total_hands} ({players_matches/max(1,total_hands)*100:.1f}%)")
        print(f"  Board matches: {board_matches}/{total_hands} ({board_matches/max(1,total_hands)*100:.1f}%)")
        print(f"  Actions matches: {actions_matches}/{total_hands} ({actions_matches/max(1,total_hands)*100:.1f}%)")
        
        # Show critical errors
        if self.critical_errors:
            print(f"\n❌ CRITICAL ERRORS ({len(self.critical_errors)}):")
            for error in self.critical_errors:
                print(f"  - {error}")
        
        # Show hands with discrepancies
        failed_hands = [result for result in self.comparison_results if not result['success']]
        if failed_hands:
            print(f"\n❌ HANDS WITH DISCREPANCIES ({len(failed_hands)}):")
            for result in failed_hands[:10]:  # Show first 10
                print(f"  - {result['hand_name']} ({result['hand_id']}):")
                for discrepancy in result['discrepancies'][:3]:  # Show first 3 discrepancies
                    print(f"    • {discrepancy}")
                if len(result['discrepancies']) > 3:
                    print(f"    • ... and {len(result['discrepancies']) - 3} more")
            
            if len(failed_hands) > 10:
                print(f"  ... and {len(failed_hands) - 10} more hands with discrepancies")
        
        # Summary assessment
        if successful_matches == total_hands:
            print("\n🎉 PERFECT MATCH! All hands converted with 100% accuracy!")
        elif successful_matches / max(1, total_hands) >= 0.95:
            print("\n✅ EXCELLENT! Very high conversion accuracy")
        elif successful_matches / max(1, total_hands) >= 0.90:
            print("\n🟡 GOOD: Good conversion accuracy, minor issues to address")
        else:
            print("\n🔴 NEEDS WORK: Significant conversion discrepancies detected")
        
        # Data integrity summary
        if failed_hands:
            print(f"\n🔍 COMMON DISCREPANCY PATTERNS:")
            all_discrepancies = []
            for result in failed_hands:
                all_discrepancies.extend(result['discrepancies'])
            
            # Count discrepancy types
            discrepancy_types = {}
            for discrepancy in all_discrepancies:
                if 'mismatch' in discrepancy:
                    key = discrepancy.split(':')[0].strip()
                    discrepancy_types[key] = discrepancy_types.get(key, 0) + 1
            
            for dtype, count in sorted(discrepancy_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {dtype}: {count} occurrences")

def main():
    """Main function to run the comprehensive comparison."""
    tester = PHHJSONComparisonTester()
    
    try:
        results = tester.run_comprehensive_comparison()
        
        # Return 0 if all comparisons successful, 1 otherwise
        success_count = sum(1 for r in results if r['success'])
        return 0 if success_count == len(results) else 1
        
    except Exception as e:
        print(f"❌ Comparison failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
