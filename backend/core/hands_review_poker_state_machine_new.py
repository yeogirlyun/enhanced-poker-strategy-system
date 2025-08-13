#!/usr/bin/env python3
"""
Modern Hands Review Poker State Machine

A clean, specialized state machine that inherits from PracticeSessionPokerStateMachine
and provides hands review specific functionality following our established architecture.

Key principles:
- Clean separation: UI has NO game logic
- Event-driven: All communication via events
- Specialized: Focused on hands review needs
- Extensible: Built on established FPSM patterns
"""

import json
import copy
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from .flexible_poker_state_machine import FlexiblePokerStateMachine, PokerState, ActionType, GameEvent
from .types import Player
from .session_logger import SessionLogger


class HandsReviewPokerStateMachine(FlexiblePokerStateMachine):
    """Specialized poker state machine for hands review mode."""
    
    def __init__(self, config, 
                 session_logger: Optional[SessionLogger] = None, **kwargs):
        self.session_logger = session_logger
        super().__init__(config, **kwargs)
        self.historical_actions = []
        self.action_index = 0
        self.current_hand_data = {}
        self.replay_paused = False
        self.auto_advance = False
        self.study_annotations = []
        
        # Data validation tracking
        self.validation_errors = []
        self.is_data_valid = False
        
    @staticmethod
    def validate_hand_data_integrity(hand_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of hand data integrity.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ['id', 'name', 'players', 'actions', 'board']
        for key in required_keys:
            if key not in hand_data:
                errors.append(f"Missing required key: {key}")
                return False, errors
        
        # Validate players structure
        players = hand_data.get('players', [])
        if not isinstance(players, list) or len(players) == 0:
            errors.append("Players must be a non-empty list")
            return False, errors
        
        for i, player in enumerate(players):
            if not isinstance(player, dict):
                errors.append(f"Player {i} is not a dictionary")
                continue
            
            # Check for either 'stack' or 'starting_stack' (data has both formats)
            player_required = ['name', 'hole_cards']
            for key in player_required:
                if key not in player:
                    errors.append(f"Player {i} missing required key: {key}")
            
            # Check for stack information (either 'stack' or 'starting_stack')
            has_stack = 'stack' in player or 'starting_stack' in player
            if not has_stack:
                errors.append(f"Player {i} missing stack information")
            
            # Validate cards format
            cards = player.get('hole_cards', [])
            if not isinstance(cards, list) or len(cards) != 2:
                errors.append(f"Player {i} must have exactly 2 hole cards")
        
        # Validate actions structure
        actions = hand_data.get('actions', {})
        if not isinstance(actions, dict):
            errors.append("Actions must be a dictionary")
            return False, errors
        
        # Validate each street's actions
        for street in ['preflop', 'flop', 'turn', 'river']:
            street_actions = actions.get(street, [])
            if isinstance(street_actions, list):
                for j, action in enumerate(street_actions):
                    if not isinstance(action, dict):
                        errors.append(f"Action {j} in {street} is not a dictionary")
                        continue
                    
                    # Check required action keys
                    action_required = ['actor', 'player_name', 'action_type', 'amount']
                    for key in action_required:
                        if key not in action:
                            errors.append(
                                f"Action {j} in {street} missing required key: {key}"
                            )
                    
                    # Validate action_type
                    action_type = action.get('action_type')
                    valid_action_types = [
                        'fold', 'check', 'call', 'bet', 'raise', 'reraise', 'all-in',
                        '3bet', '4bet', '5bet', 'street_transition'
                    ]
                    if action_type not in valid_action_types:
                        errors.append(f"Action {j} in {street} has invalid action_type: {action_type}")
                    
                    # Validate amounts for betting actions
                    if action_type in ['call', 'bet', 'raise']:
                        amount = action.get('amount', 0)
                        if not isinstance(amount, (int, float)) or amount < 0:
                            errors.append(f"Action {j} in {street} has invalid amount: {amount}")
        
        # Validate board structure
        board = hand_data.get('board', {})
        if not isinstance(board, dict):
            errors.append("Board must be a dictionary")
            return False, errors
        
        # Check board progression consistency
        for street in ['flop', 'turn', 'river']:
            street_cards = board.get(street)
            street_actions = actions.get(street, [])
            
            # If we have actions for a street, we should have cards
            if street_actions and not street_cards:
                errors.append(f"Street {street} has actions but no board cards")
            
            # Validate card format
            if street_cards:
                if street == 'flop' and (not isinstance(street_cards, list) or len(street_cards) != 3):
                    errors.append(f"Flop must have exactly 3 cards, got: {street_cards}")
                elif street in ['turn', 'river'] and not isinstance(street_cards, list):
                    errors.append(f"{street.capitalize()} must be a list of cards, got: {street_cards}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def filter_valid_hands(hands_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter hands data to separate valid from invalid hands.
        Returns (valid_hands, invalid_hands_with_reasons)
        """
        valid_hands = []
        invalid_hands = []
        
        for i, hand in enumerate(hands_data):
            is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(hand)
            
            if is_valid:
                valid_hands.append(hand)
            else:
                invalid_hands.append({
                    'hand_index': i,
                    'hand_data': hand,
                    'errors': errors,
                    'hand_id': hand.get('id', f'Unknown-{i}'),
                    'name': hand.get('name', 'Unknown')
                })
        
        return valid_hands, invalid_hands
    
    def load_hand_for_review(self, hand_data: Dict[str, Any]) -> bool:
        """
        Load a hand for review with comprehensive data validation.
        Returns True if successful, False if validation fails.
        """
        # Validate hand data integrity
        is_valid, errors = self.validate_hand_data_integrity(hand_data)
        
        if not is_valid:
            self.validation_errors = errors
            self.is_data_valid = False
            
            # Log validation errors
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_VALIDATION", 
                    f"Hand validation failed: {hand_data.get('id', 'Unknown')}", {
                        'hand_id': hand_data.get('id', 'Unknown'),
                        'errors': errors
                    })
            
            return False
        
        # Data is valid, proceed with loading
        self.validation_errors = []
        self.is_data_valid = True
        self.current_hand_data = copy.deepcopy(hand_data)
        
        # Reset state for new hand
        self._reset_to_hand_start()
        
        # Flatten and prepare historical actions
        self.historical_actions = self._flatten_historical_actions(hand_data)
        self.action_index = 0
        
        # Log successful hand loading
        if self.session_logger:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_LOAD", 
                f"Hand loaded successfully: {hand_data.get('id', 'Unknown')}", {
                    'hand_id': hand_data.get('id', 'Unknown'),
                    'total_actions': len(self.historical_actions),
                    'players': len(hand_data.get('players', [])),
                    'board_size': len(self.game_state.board)
                })
        
        return True
    
    def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status and any errors."""
        return {
            'is_valid': self.is_data_valid,
            'errors': self.validation_errors,
            'hand_id': self.current_hand_data.get('id', 'Unknown') if self.current_hand_data else None,
            'total_actions': len(self.historical_actions) if hasattr(self, 'historical_actions') else 0
        }
    
    def is_hand_ready_for_review(self) -> bool:
        """Check if the current hand is ready for review."""
        return (self.is_data_valid and 
                self.current_hand_data and 
                len(self.historical_actions) > 0 and
                self.game_state.players)
    
    def _initialize_players(self):
        """Initialize players for hands review - ALL players are automated."""
        super()._initialize_players()
        
        # Override: ALL players are bots in hands review mode
        for player in self.game_state.players:
            player.is_human = False
            
        if self.session_logger:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW_INIT", "All players set to automated mode", {
                "player_count": len(self.game_state.players)
            })
    
    def is_player_automated(self, player: Player) -> bool:
        """In hands review mode, ALL players are automated."""
        return True
    
    def _flatten_historical_actions(self, hand_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Flatten the historical actions from street-based dictionary to chronological list.
        Insert street transition markers to guide the poker state machine naturally.
        
        Args:
            hand_data: Dictionary containing hand information
            
        Returns:
            List of actions in chronological order with street transitions
        """
        flattened_actions = []
        
        # Get actions from hand data
        actions_data = hand_data.get('actions', {})
        
        # Handle both dict format (by street) and list format (already flattened)
        if isinstance(actions_data, list):
            # Already a list, use as-is
            return actions_data
        elif isinstance(actions_data, dict):
            # Dict format - flatten by street order and insert transition markers
            street_order = ['preflop', 'flop', 'turn', 'river']
            
            for i, street in enumerate(street_order):
                street_actions = actions_data.get(street, [])
                if isinstance(street_actions, list) and street_actions:
                    # Add street transition marker before first action of each street (except preflop)
                    if i > 0:  # Skip preflop (starts automatically)
                        transition_action = {
                            'actor': 0,  # System actor
                            'player_seat': 0,
                            'player_name': 'SYSTEM',
                            'action_type': 'street_transition',
                            'amount': 0.0,
                            'street': street,
                            'is_transition': True
                        }
                        flattened_actions.append(transition_action)
                        print(f"🔥 CONSOLE: Inserted {street.upper()} transition marker")
                    
                    # Add all actions for this street
                    flattened_actions.extend(street_actions)
                    
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_LOAD", f"Flattened {len(flattened_actions)} actions from {len(actions_data)} streets with transitions", {
                    "total_actions": len(flattened_actions),
                    "streets": list(actions_data.keys()),
                    "transition_markers": len([a for a in flattened_actions if a.get('is_transition')])
                })
        else:
            # Unknown format
            if self.session_logger:
                self.session_logger.log_system("WARNING", "HANDS_REVIEW_LOAD", f"Unknown actions format: {type(actions_data)}", {
                    "actions_type": str(type(actions_data))
                })
        
        return flattened_actions
    
    def _setup_players_from_hand_data(self, hand_data: Dict[str, Any]):
        """Set up players based on historical hand data."""
        players_data = hand_data.get('players', [])
        
        # Ensure we have enough players - create additional ones if needed
        while len(self.game_state.players) < len(players_data):
            from core.types import Player
            new_player = Player(
                name=f"Player {len(self.game_state.players) + 1}",
                stack=1000.0,
                position="",
                is_human=False,
                is_active=True,
                cards=[]
            )
            self.game_state.players.append(new_player)
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_SETUP", f"Created additional player {len(self.game_state.players)}", {
                    "player_name": new_player.name,
                    "total_players": len(self.game_state.players)
                })
        
        # Setup all players with hand-specific data
        for i, player_data in enumerate(players_data):
            if i < len(self.game_state.players):
                player = self.game_state.players[i]
                
                # Set player name from hand data
                player.name = player_data.get('name', f'Player {i+1}')
                
                # Set starting stack
                starting_stack = player_data.get('starting_stack', 1000)
                player.stack = float(starting_stack)
                
                # Set hole cards if available
                hole_cards = player_data.get('hole_cards', [])
                if hole_cards:
                    player.cards = hole_cards[:2]  # Take first 2 cards
                else:
                    player.cards = ['', '']  # Empty cards
                
                # Ensure player is active and not folded initially
                player.is_active = True
                player.has_folded = False
                player.current_bet = 0.0
                
                # All players are automated in hands review
                player.is_human = False
                
                if self.session_logger:
                    self.session_logger.log_system("DEBUG", "HANDS_REVIEW_SETUP", f"Setup player {i}: {player.name}", {
                        "name": player.name,
                        "stack": player.stack,
                        "cards": player.cards,
                        "position": player_data.get('position', 'unknown')
                    })
        
        if self.session_logger:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_SETUP", f"Players setup complete", {
                "total_players": len(players_data),
                "active_players": len([p for p in self.game_state.players if p.is_active])
            })
    
    def _setup_board_progression(self, hand_data: Dict[str, Any]):
        """Set up board progression data for step-by-step reveal."""
        board_data = hand_data.get('board', {})
        
        # Store full board for later progression
        self._full_board = board_data.get('all_cards', [])
        
        if self.session_logger:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW_SETUP", f"Board progression setup", {
                "full_board": self._full_board
            })
    
    def set_game_director(self, game_director):
        """Set the GameDirector for coordinating timing and events."""
        self.game_director = game_director
        
        if self.session_logger:
            self.session_logger.log_system("INFO", "HANDS_REVIEW_INIT", "GameDirector set for hands review state machine", {})
    
    def handle_auto_advance_event(self):
        """Handle auto-advance event from GameDirector."""
        if self.auto_advance_enabled and not self.replay_paused:
            self.step_forward()
    

    
    def _reset_to_hand_start(self):
        """Reset the state machine to the beginning of the hand."""
        print(f"🔥 CONSOLE: COMPLETE TABLE RESET for new hand")
        
        # Setup players from historical hand data FIRST
        if hasattr(self, 'current_hand_data') and self.current_hand_data:
            self._setup_players_from_hand_data(self.current_hand_data)
            # Setup board progression data
            self._setup_board_progression(self.current_hand_data)
        
        # COMPLETE GAME STATE RESET
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.board = []
        self.game_state.street = "preflop"
        
        # COMPLETE PLAYER RESET
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_folded = False
            player.is_active = True
            # Clear any previous action labels or status
            if hasattr(player, 'last_action'):
                player.last_action = None
            if hasattr(player, 'action_label'):
                player.action_label = None
        
        # COMPLETE ACTION TRACKING RESET
        self.action_index = 0
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        # Initialize action_player_index to first active player (not None)
        self.action_player_index = self._find_first_active_after_dealer()
        
        # COMPLETE STATE RESET
        self.current_state = PokerState.PREFLOP_BETTING
        
        # Initialize board as empty - cards will be dealt progressively as streets progress
        self.game_state.board = []
        print(f"🔥 CONSOLE: Board initialized empty - cards will be dealt progressively")
        
        # CLEAR ANY PREVIOUS HAND STATE
        if hasattr(self, '_previous_hand_state'):
            delattr(self, '_previous_hand_state')
        
        if self.session_logger:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW_BOARD", "Board initialized empty for progressive dealing", {
                "board_size": len(self.game_state.board)
            })
        
        # EMIT COMPLETE RESET EVENT for UI cleanup
        self._emit_event(GameEvent(
            event_type="hand_reset",
            data={
                'message': 'New hand loaded - table reset',
                'pot': 0.0,
                'board': [],
                'players': [{'name': p.name, 'stack': p.stack, 'cards': p.cards} for p in self.game_state.players]
            },
            timestamp=datetime.now().timestamp()
        ))
        
        # EMIT COMPLETE UI CLEANUP EVENT - force UI to clear all previous hand state
        self._emit_event(GameEvent(
            event_type="ui_cleanup",
            data={
                'action': 'clear_all_hand_state',
                'clear_labels': True,
                'clear_highlights': True,
                'clear_action_indicators': True,
                'clear_winner_labels': True,
                'clear_turn_indicators': True
            },
            timestamp=datetime.now().timestamp()
        ))
        
        # DIRECT UI CLEANUP - call the widget's cleanup method if available
        if hasattr(self, 'ui_widget') and self.ui_widget:
            try:
                if hasattr(self.ui_widget, '_clear_all_hand_state'):
                    print("🔥 CONSOLE: Calling widget cleanup method directly")
                    self.ui_widget._clear_all_hand_state()
                else:
                    print("🔥 CONSOLE: Widget cleanup method not found")
            except Exception as e:
                print(f"🔥 CONSOLE: Error calling widget cleanup: {e}")
        
        # Emit initial display state so UI shows the properly initialized table
        self._emit_display_state_event()
        
        if self.session_logger:
            self.session_logger.log_system("DEBUG", "HANDS_REVIEW_INIT", "Hand initialized for review", {
                "current_state": str(self.current_state),
                "pot": self.game_state.pot,
                "current_bet": self.game_state.current_bet,
                "active_players": len([p for p in self.game_state.players if p.is_active]),
                "players_with_cards": len([p for p in self.game_state.players if p.cards and p.cards != ['', '']]),
                "board_size": len(self.game_state.board)
            })
    
    def step_forward(self) -> bool:
        """
        Execute the next historical action in the sequence.
        
        Returns:
            bool: True if action executed, False if at end of hand
        """
        print(f"🔥 CONSOLE: step_forward ENTRY - action_index: {self.action_index}, total_actions: {len(self.historical_actions)}")
        
        if self.action_index >= len(self.historical_actions):
            print(f"🔥 CONSOLE: END OF ACTIONS DETECTED!")
            print(f"🔥 CONSOLE: action_index: {self.action_index}, total_actions: {len(self.historical_actions)}")
            print(f"🔥 CONSOLE: current_state: {self.current_state}")
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_STEP", "Reached end of historical actions - transitioning to showdown", {
                    "total_actions": len(self.historical_actions),
                    "current_state": str(self.current_state)
                })
            
            print(f"🔥 CONSOLE: All actions complete - transitioning to showdown from state: {self.current_state}")
            
            # Check if this is a preflop-only hand (no post-flop actions)
            has_post_flop_actions = any(
                action.get('is_transition') and action.get('street') in ['flop', 'turn', 'river']
                for action in self.historical_actions
            )
            
            if not has_post_flop_actions and self.current_state == PokerState.PREFLOP_BETTING:
                print(f"🔥 CONSOLE: Preflop-only hand detected - ending hand directly")
                # For preflop-only hands, end the hand immediately
                self._emit_event(GameEvent(
                    event_type="hand_complete",
                    data={
                        'winners': self._determine_winners(),
                        'pot': self.game_state.pot,
                        'board': self.game_state.board,
                        'players': [p.name for p in self.game_state.players if not p.has_folded]
                    },
                    timestamp=datetime.now().timestamp()
                ))
                return False
            
            # All actions complete - transition to showdown then end hand
            if self.current_state not in [PokerState.SHOWDOWN, PokerState.END_HAND]:
                print(f"🔥 CONSOLE: Calling transition_to(SHOWDOWN)")
                self.transition_to(PokerState.SHOWDOWN)
            else:
                print(f"🔥 CONSOLE: Already in SHOWDOWN or END_HAND state")
            
            return False
        
        try:
            action_data = self.historical_actions[self.action_index]
            
            print(f"🔥 CONSOLE: step_forward - action_index: {self.action_index}, action_data: {action_data}")
            print(f"🔥 CONSOLE: Current state before action: {self.current_state}")
            print(f"🔥 CONSOLE: Board size: {len(self.game_state.board)}")
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_STEP", "About to execute historical action", {
                    "action_index": self.action_index,
                    "action_data": action_data,
                    "current_state": str(self.current_state)
                })
            
            # Ensure we're in the correct betting state before executing actions
            self._ensure_proper_betting_state()
            
            print(f"🔥 CONSOLE: State after _ensure_proper_betting_state: {self.current_state}")
            
            # Execute the historical action
            print(f"🔥 CONSOLE: About to call _execute_historical_action")
            success = self._execute_historical_action(action_data)
            print(f"🔥 CONSOLE: _execute_historical_action returned: {success}")
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_STEP", f"Historical action execution result: {success}", {
                    "action_data": action_data
                })
            
            if success:
                self.action_index += 1
                
                # DON'T automatically detect street boundaries - let historical data control progression
                # The system should stay in each betting state until historical actions indicate otherwise
                
                # Emit step forward event
                self._emit_event(GameEvent(
                    event_type="step_forward",
                    data={
                        'action_index': self.action_index,
                        'total_actions': len(self.historical_actions),
                        'action_executed': action_data,
                        'progress': self.action_index / len(self.historical_actions)
                    },
                    timestamp=datetime.now().timestamp()
                ))
            
            return success
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_STEP", f"Error stepping forward: {e}", {
                    "action_index": self.action_index,
                    "action_data": self.historical_actions[self.action_index] if self.action_index < len(self.historical_actions) else None
                })
            return False
    
    def _ensure_proper_betting_state(self):
        """Ensure we're in the correct betting state for action execution."""
        print(f"🔥 CONSOLE: _ensure_proper_betting_state called - current state: {self.current_state}")
        
        # If we're in a dealing state but need to execute an action, advance to betting state
        state_transitions = {
            PokerState.DEAL_FLOP: PokerState.FLOP_BETTING,
            PokerState.DEAL_TURN: PokerState.TURN_BETTING,
            PokerState.DEAL_RIVER: PokerState.RIVER_BETTING
        }
        
        if self.current_state in state_transitions:
            new_state = state_transitions[self.current_state]
            print(f"🔥 CONSOLE: Auto-advancing from {self.current_state} to {new_state} for action execution")
            
            # Deal the community cards first if needed (use historical board data)
            if self.current_state == PokerState.DEAL_FLOP and len(self.game_state.board) < 3:
                self._deal_historical_flop()
            elif self.current_state == PokerState.DEAL_TURN and len(self.game_state.board) < 4:
                self._deal_historical_turn()
            elif self.current_state == PokerState.DEAL_RIVER and len(self.game_state.board) < 5:
                self._deal_historical_river()
            
            # DIRECTLY transition to betting state (skip dealing states to avoid _deal_cards conflicts)
            old_state = self.current_state
            self.current_state = new_state
            
            # Reset betting for new round
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            self.action_player_index = self._find_first_active_after_dealer()
            
            # Log the transition manually since we bypassed transition_to()
            if self.session_logger:
                self.session_logger.log_system("INFO", "STATE_MACHINE", f"Hands Review State transition: {old_state} → {new_state}")
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_STATE", f"Auto-advanced to {new_state} for action execution", {
                    "previous_state": str(old_state),
                    "new_state": str(new_state),
                    "board_size": len(self.game_state.board)
                })
    
    def _deal_historical_flop(self):
        """Deal flop cards from historical data."""
        if hasattr(self, '_full_board') and len(self._full_board) >= 3:
            # CRITICAL: Clear board first to prevent duplicates from previous hands
            self.game_state.board = []
            self.game_state.board.extend(self._full_board[:3])
            self.game_state.street = "flop"
            print(f"🔥 CONSOLE: Dealt historical flop: {self._full_board[:3]}")
            
            # Log board dealing
            if self.session_logger:
                self.session_logger.log_board_cards(self.game_state.board, "flop")
    
    def _deal_historical_turn(self):
        """Deal turn card from historical data."""
        if hasattr(self, '_full_board') and len(self._full_board) >= 4 and len(self.game_state.board) == 3:
            # CRITICAL: Ensure board has exactly 3 cards before adding turn
            if len(self.game_state.board) != 3:
                print(f"🔥 CONSOLE: WARNING - Board has {len(self.game_state.board)} cards, expected 3 for turn")
                self.game_state.board = self._full_board[:3]  # Reset to flop
            self.game_state.board.append(self._full_board[3])
            self.game_state.street = "turn"
            print(f"🔥 CONSOLE: Dealt historical turn: {self._full_board[3]}")
            
            # Log board dealing
            if self.session_logger:
                self.session_logger.log_board_cards(self.game_state.board, "turn")
    
    def _deal_historical_river(self):
        """Deal river card from historical data."""
        if hasattr(self, '_full_board') and len(self._full_board) >= 5 and len(self.game_state.board) == 4:
            # CRITICAL: Ensure board has exactly 4 cards before adding river
            if len(self.game_state.board) != 4:
                print(f"🔥 CONSOLE: WARNING - Board has {len(self.game_state.board)} cards, expected 4 for river")
                self.game_state.board = self._full_board[:4]  # Reset to turn
            self.game_state.board.append(self._full_board[4])
            self.game_state.street = "river"
            print(f"🔥 CONSOLE: Dealt historical river: {self._full_board[4]}")
            
            # Log board dealing
            if self.session_logger:
                self.session_logger.log_board_cards(self.game_state.board, "river")
    
    def _check_and_advance_street_if_complete(self):
        """Check if the current betting round is complete and advance to next street if needed."""
        print(f"🔥 CONSOLE: _check_and_advance_street_if_complete called - current state: {self.current_state}")
        
        # Check if all active players have acted and matched the current bet
        active_players = [p for p in self.game_state.players if p.is_active and not p.has_folded]
        
        if len(active_players) <= 1:
            print(f"🔥 CONSOLE: Only {len(active_players)} active players - ending hand")
            self.transition_to(PokerState.SHOWDOWN)
            return
        
        # Check if all active players have matched the current bet
        print(f"🔥 CONSOLE: Checking if all players have matched - current_bet: {self.game_state.current_bet}")
        all_matched = True
        for player in active_players:
            print(f"🔥 CONSOLE: Player {player.name}: current_bet={player.current_bet}, has_folded={player.has_folded}")
            if player.current_bet != self.game_state.current_bet:
                all_matched = False
                print(f"🔥 CONSOLE: Player {player.name} has not matched the bet")
                break
        
        print(f"🔥 CONSOLE: All players matched: {all_matched}")
        
        if not all_matched:
            print(f"🔥 CONSOLE: Not all players have matched - betting round continues")
            return
        
        print(f"🔥 CONSOLE: Betting round complete - advancing to next street")
        
        # Determine next state based on current state
        if self.current_state == PokerState.PREFLOP_BETTING:
            print(f"🔥 CONSOLE: Preflop complete - dealing flop")
            self.current_state = PokerState.DEAL_FLOP
            self._deal_historical_flop()
            self.current_state = PokerState.FLOP_BETTING
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.FLOP_BETTING:
            print(f"🔥 CONSOLE: Flop complete - dealing turn")
            self.current_state = PokerState.DEAL_TURN
            self._deal_historical_turn()
            self.current_state = PokerState.TURN_BETTING
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.TURN_BETTING:
            print(f"🔥 CONSOLE: Turn complete - dealing river")
            self.current_state = PokerState.DEAL_RIVER
            self._deal_historical_river()
            self.current_state = PokerState.RIVER_BETTING
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.RIVER_BETTING:
            print(f"🔥 CONSOLE: River complete - transitioning to showdown")
            self.transition_to(PokerState.SHOWDOWN)
            return
        
        # Reset round tracking
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        self.action_player_index = self._find_first_active_after_dealer()
        
        print(f"🔥 CONSOLE: Advanced to {self.current_state}, board size: {len(self.game_state.board)}")
        
        # Emit round_complete event for UI animations
        street_names = {
            PokerState.PREFLOP_BETTING: "preflop",
            PokerState.FLOP_BETTING: "flop", 
            PokerState.TURN_BETTING: "turn",
            PokerState.RIVER_BETTING: "river"
        }
        previous_street = street_names.get(self.current_state, "unknown")
        
        # Collect current bet amounts for animation
        player_bets = []
        for i, player in enumerate(self.game_state.players):
            if player.current_bet > 0:
                player_bets.append({
                    "index": i,
                    "amount": player.current_bet,
                    "player_name": player.name
                })
        
        print(f"🔥 CONSOLE: Emitting round_complete event - street: {previous_street}, player_bets: {len(player_bets)}")
        import time
        self._emit_event(GameEvent(
            event_type="round_complete",
            data={
                'street': previous_street,
                'player_bets': player_bets,
                'pot': self.game_state.pot
            },
            timestamp=time.time()
        ))
    
    def _check_for_street_boundary(self, action_data: Dict[str, Any]):
        """Check if this action indicates a new street should begin based on historical patterns."""
        print(f"🔥 CONSOLE: _check_for_street_boundary called for action: {action_data}")
        
        # DISABLED: This method was causing premature street advancement
        # The system should stay in each betting state until historical data indicates otherwise
        # Street progression should be controlled by the historical action sequence, not betting patterns
        
        print(f"🔥 CONSOLE: Street boundary detection DISABLED - staying in current state")
        return
    
    def _advance_to_next_street(self):
        """Advance to the next street and deal community cards."""
        print(f"🔥 CONSOLE: _advance_to_next_street called from state: {self.current_state}")
        
        if self.current_state == PokerState.PREFLOP_BETTING:
            print(f"🔥 CONSOLE: Advancing from PREFLOP to FLOP")
            self.current_state = PokerState.FLOP_BETTING
            self._deal_historical_flop()
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.FLOP_BETTING:
            print(f"🔥 CONSOLE: Advancing from FLOP to TURN")
            self.current_state = PokerState.TURN_BETTING
            self._deal_historical_turn()
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.TURN_BETTING:
            print(f"🔥 CONSOLE: Advancing from TURN to RIVER")
            self.current_state = PokerState.RIVER_BETTING
            self._deal_historical_river()
            self._reset_bets_for_new_round()
            
        elif self.current_state == PokerState.RIVER_BETTING:
            print(f"🔥 CONSOLE: Advancing from RIVER to SHOWDOWN")
            self.transition_to(PokerState.SHOWDOWN)
            return
        
        # Reset round tracking
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        self.action_player_index = self._find_first_active_after_dealer()
        
        print(f"🔥 CONSOLE: Advanced to {self.current_state}, board size: {len(self.game_state.board)}")
        
        # Emit round_complete event for UI animations
        street_names = {
            PokerState.PREFLOP_BETTING: "preflop",
            PokerState.FLOP_BETTING: "flop", 
            PokerState.TURN_BETTING: "turn",
            PokerState.RIVER_BETTING: "river"
        }
        current_street = street_names.get(self.current_state, "unknown")
        
        # Collect current bet amounts for animation
        player_bets = []
        for i, player in enumerate(self.game_state.players):
            if player.current_bet > 0:
                player_bets.append({
                    "index": i,
                    "amount": player.current_bet,
                    "player_name": player.name
                })
        
        print(f"🔥 CONSOLE: Emitting round_complete event - street: {current_street}, player_bets: {len(player_bets)}")
        import time
        self._emit_event(GameEvent(
            event_type="round_complete",
            data={
                'street': current_street,
                'player_bets': player_bets,
                'pot': self.game_state.pot
            },
            timestamp=time.time()
        ))
    
    def transition_to(self, new_state: PokerState):
        """Override: Prevent automatic card dealing in hands review mode."""
        if new_state not in PokerState.__members__.values():
            raise ValueError(f"Invalid state: {new_state}")
        
        valid_transitions = self.STATE_TRANSITIONS.get(self.current_state, [])
        if new_state not in valid_transitions and new_state != self.current_state:
            raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        if self.session_logger:
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                 f"Hands Review State transition: {old_state} → {new_state}")
        
        # Handle state-specific logic WITHOUT automatic card dealing
        # (Cards are dealt manually using historical data in _ensure_proper_betting_state)
        if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            # Reset betting for new round without dealing random cards
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            self.action_player_index = self._find_first_active_after_dealer()
            
            # Don't auto-advance to betting state - let _ensure_proper_betting_state handle it
            print(f"🔥 CONSOLE: Hands Review transition to {new_state} - cards will be dealt from historical data")
        
        elif new_state == PokerState.SHOWDOWN:
            print(f"🔥 CONSOLE: Hands Review showdown - calling base class for winner evaluation")
            # Call base class to handle showdown logic (winner evaluation) then auto-advance to END_HAND
            super().transition_to(new_state)
            return  # Base class handles showdown and auto-advances to END_HAND
            
        elif new_state == PokerState.END_HAND:
            print(f"🔥 CONSOLE: Hands Review hand ended - calling base class END_HAND logic")
            # CRITICAL: Call base class transition_to for END_HAND to get winner determination and hand_complete event
            super().transition_to(new_state)
            return  # Base class handles everything for END_HAND
    
    def _handle_round_complete(self):
        """Override: Prevent automatic transitions that try to deal random cards."""
        print(f"🔥 CONSOLE: _handle_round_complete called - checking if betting round is complete")
        
        # Check if all active players have acted (same logic as base class)
        active_players = [p for p in self.game_state.players if p.is_active and not p.has_folded]
        
        if len(active_players) <= 1:
            print(f"🔥 CONSOLE: Only {len(active_players)} active players, ending hand")
            self.transition_to(PokerState.END_HAND)
            return
        
        # Check if all active players have matched the current bet
        all_matched = True
        for player in active_players:
            if player.current_bet != self.game_state.current_bet:
                all_matched = False
                break
        
        if not all_matched:
            print(f"🔥 CONSOLE: Not all players have matched current bet - round continues")
            return
        
        # Determine next state based on current state
        if self.current_state == PokerState.PREFLOP_BETTING:
            next_state = PokerState.DEAL_FLOP
        elif self.current_state == PokerState.FLOP_BETTING:
            next_state = PokerState.DEAL_TURN
        elif self.current_state == PokerState.TURN_BETTING:
            next_state = PokerState.DEAL_RIVER
        elif self.current_state == PokerState.RIVER_BETTING:
            next_state = PokerState.SHOWDOWN
        else:
            print(f"🔥 CONSOLE: Unexpected state in _handle_round_complete: {self.current_state}")
            return
        
        print(f"🔥 CONSOLE: Round complete - transitioning from {self.current_state} to {next_state}")
        
        # CRITICAL: Emit round_complete event with player bet data for UI animations
        street_names = {
            PokerState.PREFLOP_BETTING: "preflop",
            PokerState.FLOP_BETTING: "flop", 
            PokerState.TURN_BETTING: "turn",
            PokerState.RIVER_BETTING: "river"
        }
        current_street = street_names.get(self.current_state, "unknown")
        
        # Collect current bet amounts for animation
        player_bets = []
        for i, player in enumerate(self.game_state.players):
            if player.current_bet > 0:
                player_bets.append({
                    "index": i,
                    "amount": player.current_bet,
                    "player_name": player.name
                })
        
        print(f"🔥 CONSOLE: Emitting round_complete event - street: {current_street}, player_bets: {len(player_bets)}")
        import time
        self._emit_event(GameEvent(
            event_type="round_complete",
            timestamp=time.time(),
            data={
                "street": current_street,
                "player_bets": player_bets,
                "next_state": str(next_state)
            }
        ))
        
        # CRITICAL: Use our overridden transition_to to prevent base class deck dealing
        self.transition_to(next_state)
    
    def get_valid_actions_for_player(self, player: Player) -> Dict[str, Any]:
        """Override: Always allow historical actions regardless of calculated betting state."""
        if not player or player.has_folded:
            return {}
        
        # In hands review, allow ALL actions since they're historical and pre-validated
        # The base class validation often fails because betting states don't match historical context
        return {
            "fold": True,
            "check": True,  # Always allow check in hands review
            "call": True,   # Always allow call in hands review  
            "bet": True,    # Always allow bet in hands review
            "raise": True,  # Always allow raise in hands review
            "call_amount": player.stack,  # Max possible call
            "min_bet": 0.0,               # Min bet (historical data has exact amounts)
            "max_bet": player.stack       # Max bet
        }
    
    # REMOVED: execute_action override - using base class implementation
    # The base class FlexiblePokerStateMachine.execute_action() handles all action logic correctly
    
    def _play_dual_sounds(self, action: ActionType, amount: float = 0.0):
        """Play both human voice and chip sounds for actions, just like practice session."""
        try:
            action_name = action.value.lower()  # "bet", "call", "fold", etc.
            
            # Get the audio manager
            audio_manager = None
            if hasattr(self, 'game_director') and self.game_director and hasattr(self.game_director, 'audio_manager'):
                audio_manager = self.game_director.audio_manager
                print(f"🔥 CONSOLE: Using GameDirector audio manager: {type(audio_manager)}")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                audio_manager = self.sound_manager
                print(f"🔥 CONSOLE: Using local sound manager: {type(audio_manager)}")
                
                # Ensure local sound manager has the updated voice sound configuration
                if hasattr(audio_manager, 'load_poker_sound_config'):
                    try:
                        audio_manager.load_poker_sound_config()
                        print(f"🔥 CONSOLE: Reloaded poker sound config for local sound manager")
                    except Exception as e:
                        print(f"🔥 CONSOLE: Failed to reload sound config: {e}")
            
            if not audio_manager:
                print(f"🔥 CONSOLE: No audio manager available for dual sounds")
                print(f"🔥 CONSOLE: Debug - has game_director: {hasattr(self, 'game_director')}")
                print(f"🔥 CONSOLE: Debug - has sound_manager: {hasattr(self, 'sound_manager')}")
                return
            
            # 1. Play human voice sound (e.g., "bet", "call", "fold")
            voice_event = f"player_action_{action_name}"
            if hasattr(audio_manager, 'play_poker_event_sound'):
                try:
                    audio_manager.play_poker_event_sound(voice_event)
                    print(f"🔥 CONSOLE: Played VOICE sound: {voice_event}")
                except Exception as voice_error:
                    print(f"🔥 CONSOLE: ERROR playing VOICE sound {voice_event}: {voice_error}")
            else:
                print(f"🔥 CONSOLE: Audio manager has no play_poker_event_sound method")
            
            # 2. Play chip sound for money actions (bet, call, raise)
            if action_name in ["bet", "call", "raise"] and amount > 0:
                if hasattr(audio_manager, 'play_poker_event_sound'):
                    try:
                        audio_manager.play_poker_event_sound("chip_bet")
                        print(f"🔥 CONSOLE: Played CHIP sound: chip_bet")
                    except Exception as chip_error:
                        print(f"🔥 CONSOLE: ERROR playing CHIP sound: {chip_error}")
                else:
                    print(f"🔥 CONSOLE: Audio manager has no play_poker_event_sound method for chips")
            
            print(f"🔥 CONSOLE: Dual sounds complete for {action_name} ${amount}")
                
        except Exception as e:
            print(f"🔥 CONSOLE: Error playing dual sounds: {e}")
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_SOUND", f"Error playing dual sounds: {e}", {
                    "action": action.value,
                    "amount": amount,
                    "error": str(e)
                })
    
    def _execute_historical_action(self, action_data: Dict[str, Any]) -> bool:
        """
        Execute a single historical action from the replay data.
        
        Args:
            action_data: Historical action data containing action type, player, amounts
            
        Returns:
            bool: True if action executed successfully
        """
        print(f"🔥 CONSOLE: _execute_historical_action METHOD ENTRY")
        try:
            print(f"🔥 CONSOLE: _execute_historical_action ENTRY - action_data: {action_data}")
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_EXEC", "Starting _execute_historical_action", {
                    "action_data": action_data,
                    "action_data_type": type(action_data),
                    "action_data_keys": list(action_data.keys()) if isinstance(action_data, dict) else "not_dict"
                })
            
            # Extract action details
            player_name = action_data.get('player_name', '')
            action_type = action_data.get('action_type', '').lower()
            amount = action_data.get('amount', 0.0)
            
            print(f"🔥 CONSOLE: Extracted - player_name: '{player_name}', action_type: '{action_type}', amount: {amount}")
            print(f"🔥 CONSOLE: Available players: {[p.name for p in self.game_state.players]}")
            to_amount = action_data.get('to_amount', 0.0)
            
            # Handle street transition markers
            if action_data.get('is_transition') and action_type == 'street_transition':
                street = action_data.get('street', '')
                print(f"🔥 CONSOLE: Processing street transition to: {street}")
                
                if street == 'flop':
                    print(f"🔥 CONSOLE: Transitioning to FLOP - dealing flop cards")
                    self._deal_historical_flop()
                    self.current_state = PokerState.FLOP_BETTING
                    self._reset_bets_for_new_round()
                    print(f"🔥 CONSOLE: Advanced to FLOP_BETTING, board size: {len(self.game_state.board)}")
                    
                elif street == 'turn':
                    print(f"🔥 CONSOLE: Transitioning to TURN - dealing turn card")
                    self._deal_historical_turn()
                    self.current_state = PokerState.TURN_BETTING
                    self._reset_bets_for_new_round()
                    print(f"🔥 CONSOLE: Advanced to TURN_BETTING, board size: {len(self.game_state.board)}")
                    
                elif street == 'river':
                    print(f"🔥 CONSOLE: Transitioning to RIVER - dealing river card")
                    self._deal_historical_river()
                    self.current_state = PokerState.RIVER_BETTING
                    self._reset_bets_for_new_round()
                    print(f"🔥 CONSOLE: Advanced to RIVER_BETTING, board size: {len(self.game_state.board)}")
                
                # Reset round tracking
                self.actions_this_round = 0
                self.players_acted_this_round.clear()
                self.action_player_index = self._find_first_active_after_dealer()
                
                # Emit round_complete event for UI animations
                street_names = {
                    PokerState.FLOP_BETTING: "flop",
                    PokerState.TURN_BETTING: "turn", 
                    PokerState.RIVER_BETTING: "river"
                }
                current_street = street_names.get(self.current_state, "unknown")
                
                print(f"🔥 CONSOLE: Emitting round_complete event - street: {current_street}")
                import time
                self._emit_event(GameEvent(
                    event_type="round_complete",
                    data={
                        'street': current_street,
                        'player_bets': [],
                        'pot': self.game_state.pot
                    },
                    timestamp=time.time()
                ))
                
                return True  # Street transition successful
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_EXEC", "Extracted action details", {
                    "player_name": player_name,
                    "action_type": action_type,
                    "amount": amount,
                    "to_amount": to_amount
                })
            
            # Find the player by name
            player = None
            for p in self.game_state.players:
                if p.name == player_name:
                    player = p
                    break
            
            if not player:
                if self.session_logger:
                    self.session_logger.log_system("ERROR", "HANDS_REVIEW_EXEC", f"Player not found: {player_name}", {
                        "action_data": action_data,
                        "available_players": [p.name for p in self.game_state.players],
                        "looking_for": player_name
                    })
                return False
            
            # Check if player is still in the hand (hasn't folded)
            if player.has_folded:
                if self.session_logger:
                    self.session_logger.log_system("WARNING", "HANDS_REVIEW_EXEC", f"Trying to execute action for folded player: {player_name}", {
                        "action_data": action_data
                    })
                # For historical accuracy, we still process fold actions even for already-folded players
                # but skip other actions
                if action_type != 'fold':
                    return False
            
            # Convert historical action to ActionType enum
            action_type_mapping = {
                'fold': ActionType.FOLD,
                'check': ActionType.CHECK,
                'call': ActionType.CALL,
                'bet': ActionType.BET,
                'raise': ActionType.RAISE,
                'reraise': ActionType.RAISE,  # reraise maps to raise
                'all-in': ActionType.RAISE,  # all-in is treated as raise
            }
            
            poker_action = action_type_mapping.get(action_type)
            if not poker_action:
                if self.session_logger:
                    self.session_logger.log_system("WARNING", "HANDS_REVIEW_EXEC", f"Unknown action type: {action_type}", {
                        "action_data": action_data
                    })
                return False
            
            # Determine the action amount - USE HISTORICAL DATA for hands review
            action_amount = 0.0
            if poker_action in [ActionType.BET, ActionType.RAISE]:
                # For bet/raise, use to_amount if available, otherwise amount
                action_amount = to_amount if to_amount > 0 else amount
            elif poker_action == ActionType.CALL:
                # For hands review, use the historical call amount directly
                # The historical data contains the exact amount that was called
                action_amount = amount  # Use historical amount, not calculated
                
                # CRITICAL FIX: Handle insufficient stack calls (convert to all-in)
                if action_amount > player.stack:
                    print(f"🔥 CONSOLE: Converting call ${action_amount} to all-in ${player.stack} (insufficient stack)")
                    action_amount = player.stack
                    poker_action = ActionType.RAISE  # All-in is treated as a raise
                
                print(f"🔥 CONSOLE: Using historical call amount: ${action_amount} (historical) vs ${self.game_state.current_bet - player.current_bet} (calculated)")
            
            # Log the action execution
            print(f"🔥 CONSOLE: Processing action - player: {player_name}, type: {action_type}, amount: {action_amount}")
            
            if self.session_logger:
                self.session_logger.log_system("DEBUG", "HANDS_REVIEW_EXEC", f"Executing: {player_name} {action_type} ${action_amount:.0f}", {
                    "player": player_name,
                    "action": action_type,
                    "amount": action_amount,
                    "original_data": action_data
                })
            
            # Execute the action through the base state machine
            print(f"🔥 CONSOLE: About to execute_action - player: {player_name}, action: {poker_action}, amount: {action_amount}")
            print(f"🔥 CONSOLE: Game state - current_bet: {self.game_state.current_bet}, player_stack: {player.stack}, player_current_bet: {player.current_bet}, state: {self.current_state}")
            
            success = self.execute_action(player, poker_action, action_amount)
            
            print(f"🔥 CONSOLE: execute_action result: {success}")
            
            # Play both voice and chip sounds directly (event system has errors)
            if success:
                self._play_dual_sounds(poker_action, action_amount)
            
            if not success and self.session_logger:
                self.session_logger.log_system("WARNING", "HANDS_REVIEW_EXEC", f"Action execution failed for {player_name}: {action_type}", {
                    "poker_action": str(poker_action),
                    "action_amount": action_amount,
                    "player_stack": player.stack,
                    "current_bet": self.game_state.current_bet,
                    "player_current_bet": player.current_bet,
                    "current_state": str(self.current_state)
                })
            
            return success
            
        except Exception as e:
            print(f"🔥 CONSOLE: EXCEPTION in _execute_historical_action: {e}")
            print(f"🔥 CONSOLE: Exception type: {type(e).__name__}")
            import traceback
            print(f"🔥 CONSOLE: Exception traceback: {traceback.format_exc()}")
            
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_EXEC", f"Failed to execute historical action: {e}", {
                    "action_data": action_data,
                    "error": str(e)
                })
            return False
    
    def step_backward(self) -> bool:
        """
        Step backward to the previous action (requires state reconstruction).
        
        Returns:
            bool: True if stepped backward successfully
        """
        if self.action_index <= 0:
            return False
        
        try:
            # Decrement action index
            self.action_index -= 1
            
            # Reconstruct state by replaying from beginning
            self._reset_to_hand_start()
            
            # Replay actions up to current index
            for i in range(self.action_index):
                action_data = self.historical_actions[i]
                self._execute_historical_action(action_data)
            
            # Emit step backward event
            self._emit_event(GameEvent(
                event_type="step_backward",
                data={
                    'action_index': self.action_index,
                    'total_actions': len(self.historical_actions),
                    'progress': self.action_index / len(self.historical_actions)
                },
                timestamp=datetime.now().timestamp()
            ))
            
            return True
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_STEP", f"Error stepping backward: {e}", {
                    "action_index": self.action_index
                })
            return False
    

    
    def get_hand_progress(self) -> Dict[str, Any]:
        """Get current progress through the hand."""
        total_actions = len(self.historical_actions)
        current_action = self.action_index
        
        return {
            'current_action': current_action,
            'total_actions': total_actions,
            'progress_percentage': (current_action / total_actions * 100) if total_actions > 0 else 0,
            'is_complete': current_action >= total_actions,
            'remaining_actions': total_actions - current_action
        }
    
    def add_study_annotation(self, action_index: int, annotation: str, category: str = "general"):
        """Add a study annotation to a specific action."""
        annotation_data = {
            'action_index': action_index,
            'annotation': annotation,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        
        self.study_annotations.append(annotation_data)
        
        # Emit annotation event
        self._emit_event(GameEvent(
            event_type="annotation_added",
            data=annotation_data,
            timestamp=datetime.now().timestamp()
        ))
    
    def get_game_info(self) -> Dict[str, Any]:
        """Override: In hands review mode, ALL cards should be visible for education."""
        action_player = self.get_action_player()
        
        return {
            "state": self.current_state.value,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board.copy(),
            "players": [
                {
                    "name": p.name,
                    "position": p.position,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "has_folded": p.has_folded,
                    "is_human": p.is_human,
                    # CRITICAL FIX: In hands review, show ALL cards for education
                    "cards": p.cards if p.cards and p.cards != ['', ''] else ["", ""],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
            "street": self.game_state.street,
            "hand_number": self.hand_number,
            "dealer_position": self.dealer_position
        }
    
    def get_display_state(self) -> dict:
        """Override to provide hands review specific display state."""
        # Use our overridden get_game_info method which shows all cards
        display_state = self.get_game_info()
        
        # Add hands review specific information
        display_state["review_mode"] = True
        display_state["action_index"] = self.action_index
        display_state["total_actions"] = len(self.historical_actions)
        display_state["replay_paused"] = self.replay_paused
        
        # Add expected UI structure fields
        num_players = len(self.game_state.players)
        
        # Card visibilities - in hands review mode, ALL cards should be visible for education
        display_state["card_visibilities"] = []
        for i, player in enumerate(self.game_state.players):
            # All cards always visible in hands review for educational purposes
            display_state["card_visibilities"].append(True)
        
        # Player highlights - highlight the current action player in review
        display_state["player_highlights"] = []
        for i in range(num_players):
            is_highlighted = (i == self.action_player_index)
            display_state["player_highlights"].append(is_highlighted)
        
        # Layout positions - simple circular layout
        display_state["layout_positions"] = []
        for i in range(num_players):
            angle = (i * 360 / num_players) if num_players > 0 else 0
            display_state["layout_positions"].append({
                "angle": angle,
                "radius": 200,  # Fixed radius for table layout
                "position": i
            })
        
        # Add hands review specific data
        display_state.update({
            'review_mode': True,
            'hand_progress': self.get_hand_progress(),
            'study_annotations': self.study_annotations,
            'hand_id': self.current_hand_data.get('hand_id', 'unknown')
        })
        
        return display_state
    
    def _schedule_bot_actions(self):
        """Override bot scheduling - in hands review, actions are manual/controlled."""
        # In hands review mode, we don't auto-schedule bot actions
        # All progression is controlled via step_forward/step_backward
        pass
    
    def set_auto_advance(self, enabled: bool, delay_ms: int = 2000):
        """Enable/disable automatic progression through actions."""
        self.auto_advance = enabled
        
        if enabled and not self.replay_paused:
            # Schedule next step using GameDirector (no threading)
            if hasattr(self, 'game_director') and self.game_director:
                self.game_director.schedule_event(delay_ms, "hands_review_auto_advance", {
                    "source": "set_auto_advance"
                })
                if self.session_logger:
                    self.session_logger.log_system("DEBUG", "HANDS_REVIEW", f"Scheduled auto-advance in {delay_ms}ms", {
                        "delay_ms": delay_ms
                    })
            else:
                if self.session_logger:
                    self.session_logger.log_system("WARNING", "HANDS_REVIEW", "GameDirector not available for auto-advance", {})
    
    def _determine_winners(self):
        """Determine winners for preflop-only hands or when showdown is reached."""
        # For preflop-only hands, winners are players who haven't folded
        active_players = [p for p in self.game_state.players if not p.has_folded]
        
        if len(active_players) == 1:
            # Only one player left - they win
            return [active_players[0].name]
        elif len(active_players) > 1:
            # Multiple players - this should trigger showdown logic
            # For now, return all active players (this will be refined by showdown logic)
            return [p.name for p in active_players]
        else:
            # No active players (shouldn't happen)
            return []