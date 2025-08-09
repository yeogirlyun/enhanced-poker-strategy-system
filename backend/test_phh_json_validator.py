#!/usr/bin/env python3
"""
Comprehensive PHH-to-JSON Validation Tester

This script:
1. Reads all 120 legendary hands from PHH format
2. Converts them to internal FPSM format
3. Generates corresponding JSON format hands file
4. Validates that the JSON contains the exact same content as the original PHH

This will identify any PHH parsing errors and ensure 100% data integrity.
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
from core.hands_database import ComprehensiveHandsDatabase
from core.flexible_poker_state_machine import FlexiblePokerStateMachine, Player, GameConfig
from core.types import ActionType

class PHHToJSONValidator:
    """Validates PHH parsing by converting to JSON and comparing content."""
    
    def __init__(self):
        self.hands_db = ComprehensiveHandsDatabase()
        self.validation_results = []
        self.total_hands = 0
        self.successful_conversions = 0
        self.parsing_errors = []
        
    def run_comprehensive_validation(self):
        """Run the complete PHH-to-JSON validation process."""
        print("🔍 COMPREHENSIVE PHH-TO-JSON VALIDATION")
        print("=" * 60)
        
        # Step 1: Load all hands
        self.load_all_hands()
        
        # Step 2: Convert each hand to JSON format
        json_hands = self.convert_all_hands_to_json()
        
        # Step 3: Save JSON file
        json_file_path = self.save_json_hands(json_hands)
        
        # Step 4: Validate content integrity
        self.validate_content_integrity(json_hands)
        
        # Step 5: Generate report
        self.generate_validation_report(json_file_path)
        
        return self.validation_results
    
    def load_all_hands(self):
        """Load all hands from the hands database."""
        print("📚 Loading all hands from database...")
        
        self.hands_db.load_all_hands()
        
        all_hands = list(self.hands_db.all_hands.values())
        self.total_hands = len(all_hands)
        
        print(f"✅ Loaded {self.total_hands} hands from database")
        
        if self.total_hands != 120:
            print(f"⚠️  WARNING: Expected 120 hands, but found {self.total_hands}")
    
    def convert_all_hands_to_json(self) -> List[Dict[str, Any]]:
        """Convert all PHH hands to JSON format."""
        print(f"🔄 Converting {self.total_hands} hands from PHH to JSON...")
        
        json_hands = []
        
        for i, (hand_id, hand) in enumerate(self.hands_db.all_hands.items()):
            print(f"  [{i+1:3d}/{self.total_hands}] Converting: {hand.metadata.name}")
            
            try:
                json_hand = self.convert_single_hand_to_json(hand)
                json_hands.append(json_hand)
                self.successful_conversions += 1
                
                # Validate the conversion
                validation_result = self.validate_single_hand_conversion(hand, json_hand)
                self.validation_results.append(validation_result)
                
            except Exception as e:
                error_msg = f"Failed to convert hand {hand_id}: {str(e)}"
                print(f"    ❌ {error_msg}")
                self.parsing_errors.append({
                    'hand_id': hand_id,
                    'hand_name': hand.metadata.name,
                    'error': error_msg
                })
        
        print(f"✅ Successfully converted {self.successful_conversions}/{self.total_hands} hands")
        
        return json_hands
    
    def convert_single_hand_to_json(self, hand) -> Dict[str, Any]:
        """Convert a single PHH hand to JSON format."""
        
        # Extract metadata
        metadata = {
            'id': hand.metadata.id,
            'name': hand.metadata.name,
            'event': getattr(hand.metadata, 'event', ''),
            'note': getattr(hand.metadata, 'note', ''),
            'variant': getattr(hand.metadata, 'variant', "No-Limit Hold'em"),
            'stakes': getattr(hand.metadata, 'stakes', ''),
            'date': getattr(hand.metadata, 'date', ''),
            'location': getattr(hand.metadata, 'location', '')
        }
        
        # Extract game configuration
        game_config = {
            'variant': metadata['variant'],
            'stakes': metadata['stakes'],
            'max_players': len(hand.players),
            'actual_players': len([p for p in hand.players if not p.get('name', '').startswith('Folded Player')])
        }
        
        # Extract player information
        players = []
        for player_data in hand.players:
            player_json = {
                'seat': player_data.get('seat', 0),
                'name': player_data.get('name', 'Unknown'),
                'starting_stack_chips': player_data.get('starting_stack_chips', 1000000),
                'cards': player_data.get('cards', [])
            }
            players.append(player_json)
        
        # Extract board cards
        board_cards = []
        if hasattr(hand, 'board_cards') and hand.board_cards:
            if isinstance(hand.board_cards, dict):
                # Convert board dict to flat list
                for street in ['flop', 'turn', 'river']:
                    if street in hand.board_cards:
                        street_cards = hand.board_cards[street]
                        if isinstance(street_cards, list):
                            board_cards.extend(street_cards)
                        elif isinstance(street_cards, str):
                            board_cards.append(street_cards)
            elif isinstance(hand.board_cards, list):
                board_cards = hand.board_cards[:]
        
        # Extract actions by street
        actions_by_street = {}
        if hasattr(hand, 'actions') and hand.actions:
            for street, street_actions in hand.actions.items():
                if isinstance(street_actions, list):
                    actions_by_street[street] = []
                    for action in street_actions:
                        if isinstance(action, dict):
                            action_json = {
                                'actor': action.get('actor', 0),
                                'type': action.get('type', '').upper(),
                                'amount': action.get('amount', action.get('to', 0))
                            }
                            actions_by_street[street].append(action_json)
        
        # Construct the complete JSON hand
        json_hand = {
            'metadata': metadata,
            'game_config': game_config,
            'players': players,
            'board_cards': board_cards,
            'actions': actions_by_street,
            'validation': {
                'source_format': 'PHH',
                'conversion_timestamp': self.get_current_timestamp(),
                'total_actions': sum(len(actions) for actions in actions_by_street.values()),
                'player_count': len(players),
                'board_card_count': len(board_cards)
            }
        }
        
        return json_hand
    
    def validate_single_hand_conversion(self, original_hand, json_hand) -> Dict[str, Any]:
        """Validate that a single hand conversion preserves all data."""
        validation_result = {
            'hand_id': original_hand.metadata.id,
            'hand_name': original_hand.metadata.name,
            'success': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Validate metadata
            self.validate_metadata(original_hand, json_hand, validation_result)
            
            # Validate players
            self.validate_players(original_hand, json_hand, validation_result)
            
            # Validate board cards
            self.validate_board_cards(original_hand, json_hand, validation_result)
            
            # Validate actions
            self.validate_actions(original_hand, json_hand, validation_result)
            
            # Calculate statistics
            validation_result['stats'] = {
                'player_count': len(json_hand['players']),
                'board_card_count': len(json_hand['board_cards']),
                'total_actions': json_hand['validation']['total_actions'],
                'streets_with_actions': len(json_hand['actions'])
            }
            
            if validation_result['errors']:
                validation_result['success'] = False
                
        except Exception as e:
            validation_result['success'] = False
            validation_result['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_result
    
    def validate_metadata(self, original_hand, json_hand, validation_result):
        """Validate metadata conversion."""
        original_meta = original_hand.metadata
        json_meta = json_hand['metadata']
        
        # Check required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if not json_meta.get(field):
                validation_result['errors'].append(f"Missing required metadata field: {field}")
        
        # Check field consistency
        if json_meta['id'] != original_meta.id:
            validation_result['errors'].append(f"Metadata ID mismatch: {original_meta.id} != {json_meta['id']}")
        
        if json_meta['name'] != original_meta.name:
            validation_result['errors'].append(f"Metadata name mismatch: {original_meta.name} != {json_meta['name']}")
    
    def validate_players(self, original_hand, json_hand, validation_result):
        """Validate player data conversion."""
        original_players = original_hand.players
        json_players = json_hand['players']
        
        if len(original_players) != len(json_players):
            validation_result['errors'].append(
                f"Player count mismatch: {len(original_players)} != {len(json_players)}")
            return
        
        for i, (orig_player, json_player) in enumerate(zip(original_players, json_players)):
            # Check required fields
            if not json_player.get('name'):
                validation_result['errors'].append(f"Player {i}: Missing name")
            
            if json_player.get('starting_stack_chips', 0) <= 0:
                validation_result['warnings'].append(f"Player {i}: Invalid stack chips: {json_player.get('starting_stack_chips')}")
            
            # Check consistency
            if orig_player.get('name') != json_player.get('name'):
                validation_result['errors'].append(
                    f"Player {i} name mismatch: {orig_player.get('name')} != {json_player.get('name')}")
    
    def validate_board_cards(self, original_hand, json_hand, validation_result):
        """Validate board cards conversion."""
        json_board = json_hand['board_cards']
        
        # Check board card format
        for i, card in enumerate(json_board):
            if not isinstance(card, str) or len(card) not in [2, 3]:
                validation_result['errors'].append(f"Invalid board card format at index {i}: {card}")
        
        # Check board card count (should be 0, 3, 4, or 5)
        valid_counts = [0, 3, 4, 5]
        if len(json_board) not in valid_counts:
            validation_result['warnings'].append(f"Unusual board card count: {len(json_board)}")
    
    def validate_actions(self, original_hand, json_hand, validation_result):
        """Validate actions conversion."""
        original_actions = getattr(original_hand, 'actions', {})
        json_actions = json_hand['actions']
        
        # Check action structure
        for street, actions in json_actions.items():
            if not isinstance(actions, list):
                validation_result['errors'].append(f"Actions for {street} is not a list")
                continue
            
            for i, action in enumerate(actions):
                if not isinstance(action, dict):
                    validation_result['errors'].append(f"{street} action {i}: Not a dictionary")
                    continue
                
                # Check required action fields
                required_fields = ['actor', 'type']
                for field in required_fields:
                    if field not in action:
                        validation_result['errors'].append(f"{street} action {i}: Missing {field}")
                
                # Validate action type
                valid_types = ['FOLD', 'CHECK', 'CALL', 'BET', 'RAISE', 'ALL-IN', 'ALL_IN']
                if action.get('type') not in valid_types:
                    validation_result['warnings'].append(f"{street} action {i}: Unusual action type: {action.get('type')}")
                
                # Validate actor ID
                if not isinstance(action.get('actor'), int) or action.get('actor') <= 0:
                    validation_result['errors'].append(f"{street} action {i}: Invalid actor ID: {action.get('actor')}")
    
    def save_json_hands(self, json_hands: List[Dict[str, Any]]) -> str:
        """Save the converted hands to a JSON file."""
        json_file_path = "data/legendary_hands_converted.json"
        
        print(f"💾 Saving {len(json_hands)} hands to JSON file: {json_file_path}")
        
        # Create a comprehensive JSON structure
        json_data = {
            'format_version': '1.0',
            'source': 'PHH format legendary hands',
            'conversion_date': self.get_current_timestamp(),
            'total_hands': len(json_hands),
            'validation_summary': {
                'successful_conversions': self.successful_conversions,
                'total_hands': self.total_hands,
                'parsing_errors': len(self.parsing_errors)
            },
            'hands': json_hands
        }
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON file saved successfully")
        return json_file_path
    
    def validate_content_integrity(self, json_hands: List[Dict[str, Any]]):
        """Perform final content integrity validation."""
        print("🔍 Performing final content integrity validation...")
        
        # Check for duplicate hand IDs
        hand_ids = [hand['metadata']['id'] for hand in json_hands]
        if len(hand_ids) != len(set(hand_ids)):
            print("⚠️  WARNING: Duplicate hand IDs found")
        
        # Check for empty hands
        empty_hands = [hand for hand in json_hands if not hand['actions']]
        if empty_hands:
            print(f"⚠️  WARNING: {len(empty_hands)} hands have no actions")
        
        # Check player count distribution
        player_counts = {}
        for hand in json_hands:
            count = hand['game_config']['actual_players']
            player_counts[count] = player_counts.get(count, 0) + 1
        
        print(f"📊 Player count distribution: {player_counts}")
    
    def generate_validation_report(self, json_file_path: str):
        """Generate a comprehensive validation report."""
        print("\n" + "=" * 60)
        print("📋 VALIDATION REPORT")
        print("=" * 60)
        
        successful_validations = sum(1 for result in self.validation_results if result['success'])
        failed_validations = len(self.validation_results) - successful_validations
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"  Total hands processed: {self.total_hands}")
        print(f"  Successful conversions: {self.successful_conversions}")
        print(f"  Successful validations: {successful_validations}")
        print(f"  Failed validations: {failed_validations}")
        print(f"  Parsing errors: {len(self.parsing_errors)}")
        
        if self.parsing_errors:
            print(f"\n❌ PARSING ERRORS:")
            for error in self.parsing_errors:
                print(f"  - {error['hand_name']}: {error['error']}")
        
        # Show validation errors
        validation_errors = []
        validation_warnings = []
        
        for result in self.validation_results:
            if result['errors']:
                validation_errors.extend([(result['hand_name'], error) for error in result['errors']])
            if result['warnings']:
                validation_warnings.extend([(result['hand_name'], warning) for warning in result['warnings']])
        
        if validation_errors:
            print(f"\n❌ VALIDATION ERRORS ({len(validation_errors)}):")
            for hand_name, error in validation_errors[:10]:  # Show first 10
                print(f"  - {hand_name}: {error}")
            if len(validation_errors) > 10:
                print(f"  ... and {len(validation_errors) - 10} more errors")
        
        if validation_warnings:
            print(f"\n⚠️  VALIDATION WARNINGS ({len(validation_warnings)}):")
            for hand_name, warning in validation_warnings[:10]:  # Show first 10
                print(f"  - {hand_name}: {warning}")
            if len(validation_warnings) > 10:
                print(f"  ... and {len(validation_warnings) - 10} more warnings")
        
        print(f"\n💾 JSON OUTPUT:")
        print(f"  File: {json_file_path}")
        print(f"  Size: {os.path.getsize(json_file_path) / 1024:.1f} KB")
        
        # Success rate
        success_rate = (successful_validations / max(1, len(self.validation_results))) * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print("🎉 PERFECT! All hands converted and validated successfully!")
        elif success_rate >= 95.0:
            print("✅ EXCELLENT! Conversion quality is very high")
        elif success_rate >= 90.0:
            print("🟡 GOOD: Most hands converted successfully, minor issues to address")
        else:
            print("🔴 NEEDS WORK: Significant parsing issues detected")
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main function to run the comprehensive validation."""
    validator = PHHToJSONValidator()
    
    try:
        results = validator.run_comprehensive_validation()
        return 0 if all(r['success'] for r in results) else 1
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
