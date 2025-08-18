#!/usr/bin/env python3
"""
Hands Review Session State Machine - Composition Architecture

This module implements a hands review session state machine that uses
composition with FlexiblePokerStateMachine instead of inheritance.
"""

from typing import Dict, List, Any, Optional
from .poker_types import Player, ActionType, PokerState
from .flexible_poker_state_machine import FlexiblePokerStateMachine
from .decision_engine import PreloadedDecisionEngine
from .session_logger import SessionLogger


class HandsReviewSessionStateMachine:
    """
    Composition-based hands review session state machine.
    
    This class uses composition with FlexiblePokerStateMachine (FPSM)
    instead of inheritance, providing better separation of concerns
    and avoiding the tight coupling issues of inheritance.
    """
    
    def __init__(self, config):
        """Initialize the hands review session state machine."""
        # Use composition: FPSM is a member variable, not a parent class
        self.fpsm = FlexiblePokerStateMachine(config)
        
        # Session state
        self.session_active = False
        self.hand_completed = False
        self.current_hand_id = None
        self.session_type = "hands_review"
        self.mode = "composition"
        
        # Hands review specific
        self.preloaded_hand_data = None
        self.decision_engine = None
        
        # Configuration and logging
        self.config = config
        self.logger = SessionLogger()
        
        print("🃏 HANDS_REVIEW: Created composition-based session state machine")
    
    def start_session(self):
        """Start the hands review session."""
        if not self.preloaded_hand_data:
            print("❌ HANDS_REVIEW: No preloaded hand data set")
            return False
        
        self.session_active = True
        self.hand_completed = False
        
        # Start the hand using composition pattern
        success = self.start_hand()
        if success:
            print("✅ HANDS_REVIEW: Session started successfully")
            self.logger.log_system(
                "HANDS_REVIEW", "Session started", 
                {"hand_id": self.current_hand_id}
            )
        else:
            print("❌ HANDS_REVIEW: Failed to start session")
        
        return success
    
    def set_preloaded_hand_data(self, hand_data: Dict[str, Any]):
        """Set the preloaded hand data including initial player cards."""
        # Convert legendary hands format if needed
        converted_hand_data = self._convert_legendary_hands_format(hand_data)
        self.preloaded_hand_data = converted_hand_data
        
        # Create decision engine for historical actions
        if converted_hand_data and 'actions' in converted_hand_data:
            self.decision_engine = PreloadedDecisionEngine(converted_hand_data)
            action_count = len(converted_hand_data.get('actions', {}))
            print(f"🃏 HANDS_REVIEW: Set preloaded hand data with {action_count} streets")
        else:
            print("⚠️ HANDS_REVIEW: No actions found in preloaded hand data")
    
    def _convert_legendary_hands_format(self, hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legendary hands format to expected format."""
        converted_hand_data = hand_data.copy()
        
        # Convert actions from legendary hands format to expected format
        if "streets" in hand_data:
            print("🎯 LOAD_HAND: Converting legendary hands actions format...")
            actions_converted = {}
            
            # Map legendary hands street names to expected names
            street_mapping = {
                "PREFLOP": "preflop",
                "FLOP": "flop", 
                "TURN": "turn",
                "RIVER": "river"
            }
            
            for legendary_street, street_data in hand_data["streets"].items():
                if legendary_street in street_mapping:
                    expected_street = street_mapping[legendary_street]
                    if "actions" in street_data:
                        # Convert action format
                        converted_actions = []
                        for action in street_data["actions"]:
                            converted_action = {
                                "action_type": action.get("action", "check").lower(),
                                "amount": action.get("amount", 0.0),
                                "player_seat": action.get("actor_uid", "seat1"),
                                "street": expected_street
                            }
                            converted_actions.append(converted_action)
                        
                        actions_converted[expected_street] = converted_actions
                        print(f"   • {legendary_street} -> {expected_street}: {len(converted_actions)} actions")
            
            converted_hand_data["actions"] = actions_converted
            print(f"🎯 LOAD_HAND: Converted {len(actions_converted)} streets with actions")
        else:
            print("🎯 LOAD_HAND: No streets data found, using original actions if available")
        
        # Copy metadata to converted hand data so blind amounts are available
        if "metadata" in hand_data:
            converted_hand_data["metadata"] = hand_data["metadata"]
            print(f"🎯 LOAD_HAND: Copied metadata with blinds: SB=${hand_data['metadata'].get('small_blind', 'N/A')}, BB=${hand_data['metadata'].get('big_blind', 'N/A')}")
        
        return converted_hand_data
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand using the composition pattern."""
        if not self.preloaded_hand_data:
            print("❌ HANDS_REVIEW: No preloaded hand data available")
            return False
        
        try:
            # Use composition: call FPSM methods directly
            if existing_players:
                success = self.fpsm.start_hand(
                    existing_players=existing_players
                )
            else:
                success = self.fpsm.start_hand()
            
            if success:
                # Set up hands review specific state
                self._setup_hands_review_state()
                print("✅ HANDS_REVIEW: Hand started successfully")
                return True
            else:
                print("❌ HANDS_REVIEW: FPSM failed to start hand")
                return False
                
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error starting hand: {e}")
            return False
    
    def _setup_hands_review_state(self):
        """Set up hands review specific state after hand starts."""
        if not self.preloaded_hand_data:
            return
        
        # Load players from preloaded data if available
        if 'initial_state' in self.preloaded_hand_data:
            players_data = (
                self.preloaded_hand_data['initial_state'].get('players', [])
            )
            if players_data:
                # Update FPSM players with preloaded data
                self._load_preloaded_players(players_data)
        
        # === BEGIN: Deterministic deck for Hands Review ===
        # Block accidental shuffles in review mode
        setattr(self.fpsm, "skip_shuffle", True)
        
        # Build the preloaded board in deal order: flop(3) -> turn(1) -> river(1)
        try:
            # Extract board cards from preloaded data
            board_cards = self.preloaded_hand_data.get('board_cards', [])
            if board_cards:
                # Set board cards using composition
                self.fpsm.set_board_cards(board_cards)
                print(f"✅ HANDS_REVIEW: Set board cards: {board_cards}")
                
                # Create deterministic deck with board cards at the top
                # Collect used cards (all hole cards + the board) so they don't reappear
                used = set(board_cards)
                for p in self.fpsm.game_state.players:
                    for c in getattr(p, "cards", []):
                        used.add(str(c))
                
                # Create a full deck using the base helper, then remove used and prepend the board
                full_deck = self.fpsm._create_deck()  # method of FlexiblePokerStateMachine
                full_deck = [str(c) for c in full_deck]
                remaining = [c for c in full_deck if c not in used]
                self.fpsm.game_state.deck = board_cards + remaining
                
                print(f"🃏 HANDS_REVIEW: Deterministic deck installed: {self.fpsm.game_state.deck[:5]}")
            else:
                print("⚠️ HANDS_REVIEW: No board cards found for deterministic deck")
                
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Failed to install deterministic deck: {e}")
        # === END: Deterministic deck for Hands Review ===
    
    def _load_preloaded_players(self, players_data: List[Dict]):
        """Load players from preloaded hand data."""
        try:
            # Use composition: access FPSM game state directly
            for i, player_data in enumerate(players_data):
                if i < len(self.fpsm.game_state.players):
                    player = self.fpsm.game_state.players[i]
                    
                    # Update player cards if available
                    if 'cards' in player_data:
                        player.cards = player_data['cards']
                        print(
                            f"🃏 HANDS_REVIEW: Loaded cards for {player.name}: "
                            f"{player.cards}"
                        )
                    
                    # Update player stack if available
                    if 'stack' in player_data:
                        player.stack = float(player_data['stack'])
                        print(
                            f"💰 HANDS_REVIEW: Set stack for {player.name}: "
                            f"${player.stack}"
                        )
            
            print(
                f"✅ HANDS_REVIEW: Loaded {len(players_data)} players "
                f"from preloaded data"
            )
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error loading preloaded players: {e}")
    
    def step_forward(self):
        """Execute the next action in the hands review session."""
        if not self.session_active or self.hand_completed:
            print("🚫 HANDS_REVIEW: Session not active or hand completed")
            return False
        
        try:
            # Use composition: get action player from FPSM
            action_player = self.fpsm.get_action_player()
            if not action_player:
                print("🏁 HANDS_REVIEW: No action player - hand may be complete")
                self._check_for_hand_completion()
                return False
            
            # Get decision from decision engine
            if not self.decision_engine:
                print("❌ HANDS_REVIEW: No decision engine available")
                return False
            
            # Use composition: get game state from FPSM
            game_state = self._get_game_state_for_decision()
            decision = self.decision_engine.get_decision(
                action_player.name, game_state
            )
            
            if not decision:
                print("🏁 HANDS_REVIEW: No more decisions available")
                self._handle_hand_completion()
                return False
            
            # Execute the action using composition pattern
            success = self._execute_decision(action_player, decision)
            
            if success:
                action_type = decision.get('action', 'unknown')
                print(
                    f"✅ HANDS_REVIEW: Executed action: {action_player.name} "
                    f"{action_type}"
                )
                return True
            else:
                print("❌ HANDS_REVIEW: Failed to execute action")
                return False
                
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error in step_forward: {e}")
            return False
    
    def _get_game_state_for_decision(self) -> Dict[str, Any]:
        """Get game state in format expected by decision engine."""
        # Use composition: access FPSM game state directly
        return {
            'street': self.fpsm.current_state.name.lower(),
            'pot': self.fpsm.game_state.pot,
            'current_bet': self.fpsm.game_state.current_bet,
            'players': [
                {
                    'name': p.name,
                    'stack': p.stack,
                    'current_bet': p.current_bet,
                    'cards': p.cards
                }
                for p in self.fpsm.game_state.players
            ]
        }
    
    def _execute_decision(self, player: Player, decision: Dict[str, Any]) -> bool:
        """Execute a decision using the composition pattern."""
        try:
            action_type = decision.get('action')
            amount = decision.get('amount', 0.0)
            
            # Use composition: call FPSM execute_action method
            success = self.fpsm.execute_action(player, action_type, amount)
            
            if success:
                # Check for hand completion after each action
                self._check_for_hand_completion()
            
            return success
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error executing decision: {e}")
            return False
    
    def _check_for_hand_completion(self):
        """Check if the hand is complete."""
        # Use composition: check FPSM state
        if self.fpsm.current_state == PokerState.END_HAND:
            self.hand_completed = True
            print("🏁 HANDS_REVIEW: Hand completed")
    
    def _handle_hand_completion(self):
        """Handle hand completion."""
        self.hand_completed = True
        print("🏁 HANDS_REVIEW: Hand completion handled")
    
    def get_display_state(self) -> Dict[str, Any]:
        """Get the current display state for UI rendering."""
        # Use composition: get game info from FPSM and merge with session state
        game_info = self.fpsm.get_game_info()
        
        display_state = {
            'state': self.fpsm.current_state.name.lower(),
            'pot': self.fpsm.game_state.pot,
            'current_bet': self.fpsm.game_state.current_bet,
            'board': self.fpsm.game_state.board,
            'players': self.fpsm.game_state.players,
            'action_player': self.fpsm.get_action_player(),
            'street': self.fpsm.current_state.name.lower(),
            'hand_number': self.current_hand_id,
            'dealer_position': self.fpsm.dealer_position,
            'session_type': self.session_type,
            'session_active': self.session_active,
            'hand_completed': self.hand_completed,
            'current_hand_id': self.current_hand_id
        }
        
        return display_state
    
    def reset_session(self):
        """Reset the session to initial state."""
        self.session_active = False
        self.hand_completed = False
        self.current_hand_id = None
        self.preloaded_hand_data = None
        self.decision_engine = None
        
        # Use composition: reset FPSM
        self.fpsm.reset_game()
        
        print("🔄 HANDS_REVIEW: Session reset")
    
    def is_session_complete(self) -> bool:
        """Check if the session is complete."""
        return self.hand_completed
    
    def get_valid_actions_for_player(self, player: Player) -> Dict[str, Any]:
        """Get valid actions for a player."""
        if not self.fpsm:
            return {}
        
        # Use composition: delegate to FPSM
        return self.fpsm.get_valid_actions_for_player(player)
    
    def get_action_player(self):
        """Get the current action player."""
        if not self.fpsm:
            return None
        
        # Use composition: delegate to FPSM
        return self.fpsm.get_action_player()
