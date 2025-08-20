#!/usr/bin/env python3
"""
Converter from current GTO JSON format to comprehensive Hand model.

This module converts our existing GTO session data format into the new
standardized Hand model format, enabling:
- Precise action replay in Hands Review
- Advanced hand analysis capabilities  
- Statistical aggregation across sessions
- Future interoperability with other poker tools
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.core.hand_model import (
    Hand, HandMetadata, Seat, Street, StreetState, Action, ActionType, 
    PostingMeta, Pot, PotShare, ShowdownEntry, Variant
)

class GTOToHandConverter:
    """Converts GTO session data to standardized Hand model format."""
    
    @staticmethod
    def _normalize_player_id(name: str = None, index: int = None) -> str:
        """
        Canonical player ID normalizer.
        Always returns format: "Player1", "Player2", etc. (no spaces)
        """
        if name and name.startswith('Player'):
            # Extract number from existing player name
            import re
            match = re.search(r'(\d+)', name)
            if match:
                return f"Player{match.group(1)}"
        
        if index is not None:
            return f"Player{index + 1}"
        
        # Fallback
        return name or "Player1"
    
    @staticmethod
    def convert_gto_hand(gto_data: Dict[str, Any]) -> Hand:
        """
        Convert a single GTO hand from our current format to Hand model.
        
        Args:
            gto_data: Dictionary containing GTO hand data with keys:
                - id: Hand identifier
                - initial_state: Player and game setup
                - actions: List of actions taken
                - final_state: End results
                
        Returns:
            Hand object with complete standardized data
        """
        converter = GTOToHandConverter()
        return converter._convert_hand(gto_data)
    
    def _convert_hand(self, gto_data: Dict[str, Any]) -> Hand:
        """Internal conversion method."""
        
        # Extract basic data
        hand_id = gto_data.get('id', 'unknown')
        initial_state = gto_data.get('initial_state', {})
        actions = gto_data.get('actions', [])
        final_state = gto_data.get('final_state', {})
        
        # Create metadata
        metadata = self._create_metadata(hand_id, initial_state, gto_data)
        
        # Create seats from initial player data
        seats = self._create_seats(initial_state.get('players', []))
        
        # Convert actions to standardized format
        streets = self._convert_actions_to_streets(actions, initial_state)
        
        # Add RETURN_UNCALLED actions for proper pot accounting
        self._append_return_uncalled(streets, final_state)
        
        # Build pots from final state
        pots = self._create_pots(final_state, seats)
        
        # Create showdown entries (if any)
        showdown = self._create_showdown(final_state, seats)
        
        # Calculate final stacks
        final_stacks = self._calculate_final_stacks(final_state, seats)
        
        return Hand(
            metadata=metadata,
            seats=seats,
            hero_player_uid=seats[0].player_uid if seats else None,  # Fixed: use hero_player_uid
            streets=streets,
            pots=pots,
            showdown=showdown,
            final_stacks=final_stacks
        )
    
    def _create_metadata(self, hand_id: str, initial_state: Dict[str, Any], 
                        gto_data: Dict[str, Any]) -> HandMetadata:
        """Create hand metadata from GTO data."""
        
        # Extract hole cards from initial player data
        hole_cards = {}
        players_data = initial_state.get('players', [])
        
        for i, player_data in enumerate(players_data):
            player_id = self._normalize_player_id(name=player_data.get('name'), index=i)
            
            # Try different possible keys for hole cards
            cards = (player_data.get('hole_cards') or 
                    player_data.get('cards') or 
                    player_data.get('hand') or 
                    [])
            
            if cards and cards != ['**', '**']:
                hole_cards[player_id] = cards
                print(f"🃏 CONVERTER: Extracted hole cards for {player_id}: {cards}")
            else:
                print(f"⚠️  CONVERTER: No hole cards found for {player_id}")
        
        return HandMetadata(
            table_id="GTO-Table-1",
            hand_id=hand_id,
            variant=Variant.NLHE,
            max_players=len(initial_state.get('players', [])),
            small_blind=initial_state.get('small_blind', 5),
            big_blind=initial_state.get('big_blind', 10),
            ante=0,  # GTO sessions don't use antes
            rake=0,  # GTO sessions don't have rake
            currency="CHIPS",
            hole_cards=hole_cards,  # Add hole cards to metadata
            started_at_utc=datetime.now().isoformat() + "Z",
            ended_at_utc=None,  # Will be set when complete
            run_count=1,
            session_type="gto",
            bot_strategy="gto_v1",
            analysis_tags=["gto_generated", "bot_vs_bot"]
        )
    
    def _create_seats(self, players_data: List[Dict[str, Any]]) -> List[Seat]:
        """Create seat information from player data."""
        seats = []
        
        for i, player_data in enumerate(players_data):
            # Use normalized player ID consistently
            player_id = GTOToHandConverter._normalize_player_id(
                name=player_data.get('name'), 
                index=i
            )
            seat = Seat(
                seat_no=i + 1,
                player_uid=player_id,  # Fixed: use player_uid instead of player_id
                display_name=player_data.get('name', f'Player {i+1}'),  # Display can have spaces
                starting_stack=int(player_data.get('stack', 1000)),
                is_button=(i == 0)  # First player as button for simplicity
            )
            seats.append(seat)
            
        return seats
    
    def _convert_actions_to_streets(self, actions: List[Dict[str, Any]], 
                                  initial_state: Dict[str, Any]) -> Dict[Street, StreetState]:
        """Convert action list to street-organized format."""
        
        streets = {
            Street.PREFLOP: StreetState(),
            Street.FLOP: StreetState(),
            Street.TURN: StreetState(),
            Street.RIVER: StreetState(),
        }
        
        # Add blind postings first
        self._add_blind_postings(streets[Street.PREFLOP], initial_state)
        
        # Sort actions by any order field, or use list order
        sorted_actions = sorted(actions, key=lambda a: a.get('order', actions.index(a)))
        
        action_order = len(streets[Street.PREFLOP].actions) + 1  # Continue from blind postings
        
        for action_data in sorted_actions:
            street_name = action_data.get('street', 'preflop').upper()
            
            # Map street names
            if street_name == 'PREFLOP_BETTING':
                street = Street.PREFLOP
            elif street_name == 'FLOP_BETTING':
                street = Street.FLOP
            elif street_name == 'TURN_BETTING':
                street = Street.TURN
            elif street_name == 'RIVER_BETTING':
                street = Street.RIVER
            else:
                street = Street.PREFLOP  # Default
            
            # Convert action
            action = self._convert_single_action(action_data, action_order)
            if action:
                streets[street].actions.append(action)
                action_order += 1
        
        return streets
    
    def _append_return_uncalled(self, streets: Dict[Street, StreetState], final_state: Dict[str, Any]):
        """Add RETURN_UNCALLED actions for proper pot accounting when hands end with uncalled bets."""
        
        # Find the last street with actions
        last_street = None
        for street in [Street.RIVER, Street.TURN, Street.FLOP, Street.PREFLOP]:
            if streets[street].actions:
                last_street = street
                break
        
        if not last_street:
            return
            
        last_street_actions = streets[last_street].actions
        if not last_street_actions:
            return
            
        # Look for pattern: bet/raise followed by only folds
        last_aggressor = None
        last_aggressor_amount = 0
        actions_after_aggression = []
        
        # Find the last aggressive action (bet/raise)
        for i, action in enumerate(last_street_actions):
            if action.action in [ActionType.BET, ActionType.RAISE]:
                last_aggressor = action.actor_id
                last_aggressor_amount = action.amount
                actions_after_aggression = last_street_actions[i+1:]
        
        # Check if all actions after aggression are folds
        if last_aggressor and actions_after_aggression:
            all_folds = all(action.action == ActionType.FOLD for action in actions_after_aggression)
            
            if all_folds and last_aggressor_amount > 0:
                # Add RETURN_UNCALLED action
                next_order = max(action.order for action in last_street_actions) + 1
                
                return_action = Action(
                    order=next_order,
                    street=last_street,
                    actor_uid=last_aggressor,  # Fixed: use actor_uid instead of actor_id
                    action=ActionType.RETURN_UNCALLED,
                    amount=last_aggressor_amount,
                    note=f"Uncalled bet of ${last_aggressor_amount} returned"
                )
                
                streets[last_street].actions.append(return_action)
    
    def _add_blind_postings(self, preflop_street: StreetState, initial_state: Dict[str, Any]):
        """Add blind posting actions to preflop."""
        
        sb_amount = initial_state.get('small_blind', 5)
        bb_amount = initial_state.get('big_blind', 10)
        players = initial_state.get('players', [])
        
        if len(players) >= 2:
            # In our GTO format, blinds are already posted in the initial state
            # We infer them from player current_bet values
            
            order = 1
            for i, player in enumerate(players):
                current_bet = player.get('current_bet', 0)
                
                if current_bet == sb_amount:
                    # Small blind
                    player_id = GTOToHandConverter._normalize_player_id(
                        name=player.get('name'), index=i
                    )
                    preflop_street.actions.append(Action(
                        order=order,
                        street=Street.PREFLOP,
                        actor_uid=player_id,  # Fixed: use actor_uid instead of actor_id
                        action=ActionType.POST_BLIND,
                        amount=sb_amount,
                        to_amount=sb_amount,
                        posting_meta=PostingMeta(blind_type="SB")
                    ))
                    order += 1
                    
                elif current_bet == bb_amount:
                    # Big blind
                    player_id = GTOToHandConverter._normalize_player_id(
                        name=player.get('name'), index=i
                    )
                    preflop_street.actions.append(Action(
                        order=order,
                        street=Street.PREFLOP,
                        actor_uid=player_id,  # Fixed: use actor_uid instead of actor_id
                        action=ActionType.POST_BLIND,
                        amount=bb_amount,
                        to_amount=bb_amount,
                        posting_meta=PostingMeta(blind_type="BB")
                    ))
                    order += 1
    
    def _convert_single_action(self, action_data: Dict[str, Any], order: int) -> Optional[Action]:
        """Convert a single action from GTO format to Hand model format."""
        
        try:
            # Extract action details
            player_index = action_data.get('player_index', 0)
            action_str = action_data.get('action', 'fold').lower()
            amount = action_data.get('amount', 0.0)
            street_name = action_data.get('street', 'preflop')
            explanation = action_data.get('explanation', '')
            
            # Map action types
            action_type_map = {
                'fold': ActionType.FOLD,
                'check': ActionType.CHECK,
                'call': ActionType.CALL,
                'bet': ActionType.BET,
                'raise': ActionType.RAISE
            }
            
            action_type = action_type_map.get(action_str, ActionType.FOLD)
            
            # Convert street name
            street_map = {
                'preflop': Street.PREFLOP,
                'flop': Street.FLOP, 
                'turn': Street.TURN,
                'river': Street.RIVER
            }
            street = street_map.get(street_name.lower(), Street.PREFLOP)
            
            # Use normalized player ID
            player_id = GTOToHandConverter._normalize_player_id(index=player_index)
            
            # Calculate to_amount for raises/bets
            to_amount = None
            if action_type in [ActionType.BET, ActionType.RAISE, ActionType.CALL]:
                to_amount = int(amount)
            
            return Action(
                order=order,
                street=street,
                actor_uid=player_id,  # Fixed: use actor_uid instead of actor_id
                action=action_type,
                amount=int(amount),
                to_amount=to_amount,
                all_in=False,  # We don't track all-ins in current GTO format
                note=f"GTO: {explanation}" if explanation else None
            )
            
        except Exception as e:
            print(f"Warning: Failed to convert action {action_data}: {e}")
            return None
    
    def _create_pots(self, final_state: Dict[str, Any], seats: List[Seat]) -> List[Pot]:
        """Create pot information from final state."""
        
        final_pot = final_state.get('pot', 0)
        if final_pot <= 0:
            return []
        
        # For GTO sessions, create a single main pot
        # All players are eligible (we don't track side pots in current format)
        eligible_players = [seat.player_uid for seat in seats]
        
        pot = Pot(
            amount=int(final_pot),
            eligible_player_uids=eligible_players,  # Fixed: use eligible_player_uids
            shares=[]  # Will be filled by showdown analysis
        )
        
        # Determine winner(s) from final state
        players_final = final_state.get('players', [])
        max_stack = 0
        winners = []
        
        for player_data in players_final:
            stack = player_data.get('stack', 0)
            if stack > max_stack:
                max_stack = stack
                winners = [player_data.get('name', 'Unknown')]
            elif stack == max_stack and stack > 0:
                winners.append(player_data.get('name', 'Unknown'))
        
        # Award pot to winner(s)
        if winners:
            share_amount = pot.amount // len(winners)
            remainder = pot.amount % len(winners)
            
            for i, winner in enumerate(winners):
                pot.shares.append(PotShare(
                    player_uid=winner,  # Fixed: use player_uid instead of player_id
                    amount=share_amount + (1 if i < remainder else 0)
                ))
        
        return [pot]
    
    def _create_showdown(self, final_state: Dict[str, Any], seats: List[Seat]) -> List[ShowdownEntry]:
        """Create showdown entries from final state."""
        
        # For GTO sessions, we don't typically have showdown info
        # Return empty list for now - could be enhanced later
        return []
    
    def _calculate_final_stacks(self, final_state: Dict[str, Any], seats: List[Seat]) -> Dict[str, int]:
        """Calculate final stack sizes."""
        
        final_stacks = {}
        players_final = final_state.get('players', [])
        
        # Map by name to get final stacks
        for player_data in players_final:
            name = player_data.get('name', 'Unknown')
            stack = int(player_data.get('stack', 0))
            final_stacks[name] = stack
        
        # Ensure all seats have entries
        for seat in seats:
            if seat.player_uid not in final_stacks:
                final_stacks[seat.player_uid] = seat.starting_stack
        
        return final_stacks

def convert_gto_file(input_path: str, output_path: str) -> None:
    """
    Convert a GTO JSON file to Hand model format.
    
    Args:
        input_path: Path to input GTO JSON file
        output_path: Path to write converted Hand JSON file
    """
    try:
        with open(input_path, 'r') as f:
            gto_data = json.load(f)
        
        hand = GTOToHandConverter.convert_gto_hand(gto_data)
        hand.save_json(output_path)
        
        print(f"✅ Converted {input_path} -> {output_path}")
        print(f"   Hand ID: {hand.metadata.hand_id}")
        print(f"   Actions: {len(hand.get_all_actions())}")
        print(f"   Final pot: ${hand.get_total_pot()}")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        raise

if __name__ == "__main__":
    # Test conversion with our existing GTO data
    test_files = [
        "cycle_test_hand.json",
        "gto_hand_for_verification.json"
    ]
    
    for test_file in test_files:
        try:
            output_file = test_file.replace('.json', '_hand_model.json')
            convert_gto_file(test_file, output_file)
        except FileNotFoundError:
            print(f"⚠️  Test file {test_file} not found - skipping")
        except Exception as e:
            print(f"❌ Failed to convert {test_file}: {e}")
    
    print("✅ GTO to Hand model conversion test complete!")
