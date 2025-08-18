#!/usr/bin/env python3
"""
Unified Bot Session State Machine

This module provides a unified state machine for all bot-only poker sessions,
including GTO simulation and hands review. By using a DecisionEngine interface,
the same state machine can handle different decision sources while maintaining
consistent behavior and event flows.

Key benefits:
- Code reuse between GTO and hands review sessions
- Consistent timing and animation behavior
- Simplified architecture compared to GameDirector approach
- Clean separation between decision logic and game flow
"""

from typing import List, Dict, Any, Optional
import time

from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, GameEvent
from .types import Player, ActionType, PokerState
from .decision_engine import DecisionEngine, GTODecisionEngine, PreloadedDecisionEngine


class BotSessionStateMachine(FlexiblePokerStateMachine):
    """
    Unified state machine for all bot-only poker sessions.
    
    This state machine handles both GTO simulation and hands review by using
    a DecisionEngine interface that abstracts the source of decisions. All
    timing, animation, and event handling is identical between session types.
    """
    
    def __init__(self, config: GameConfig, decision_engine: DecisionEngine, 
                 session_type: str = "bot", mode: str = "live"):
        """
        Initialize the bot session state machine.
        
        Args:
            config: Game configuration (players, blinds, etc.)
            decision_engine: Engine that provides bot decisions
            session_type: Type of session ("gto" or "hands_review")
            mode: Operating mode ("live" for real-time, "review" for playback)
        """
        super().__init__(config, mode)
        
        self.decision_engine = decision_engine
        self.session_type = session_type
        self.decision_history: List[Dict[str, Any]] = []
        
        # All bot sessions use auto-advance for smooth gameplay
        self.config.auto_advance = True
        
        # Sound manager for audio feedback
        self.sound_manager = None
        
        # Session state tracking
        self.session_active = False
        self.current_decision_explanation = ""
        
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "BOT_SESSION_INIT",
                f"Bot session initialized: {session_type}",
                {
                    "session_type": session_type,
                    "engine_type": decision_engine.__class__.__name__,
                    "num_players": config.num_players,
                    "auto_advance": True
                }
            )
    
    def start_session(self) -> bool:
        """Start the bot session."""
        try:
            # Reset decision engine
            self.decision_engine.reset()
            self.decision_history.clear()
            
            # Start the first hand (returns None, so we just call it and assume success)
            self.start_hand()
            
            # If no exception was thrown, consider it successful
            self.session_active = True
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO", "BOT_SESSION",
                    f"Bot session started successfully",
                    {"session_type": self.session_type}
                )
            
            return True
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_SESSION",
                    f"Failed to start bot session: {e}",
                    {"session_type": self.session_type}
                )
            return False
    
    def stop_session(self):
        """Stop the current bot session."""
        self.session_active = False
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "BOT_SESSION",
                "Bot session stopped",
                {"session_type": self.session_type}
            )
    
    def execute_next_bot_action(self) -> bool:
        """
        Execute the next bot action using the decision engine.
        
        Returns:
            True if action was executed successfully, False otherwise
        """
        print("🔥 BOT_ACTION_DEBUG: execute_next_bot_action called!")
        
        if not self.session_active:
            print("🔥 BOT_ACTION_DEBUG: Session not active, returning False")
            return False
        
        # Check if session is complete
        if self.decision_engine.is_session_complete():
            print("🔥 BOT_ACTION_DEBUG: Session complete, stopping session")
            self.stop_session()
            return False
        
        # Get current action player
        if self.action_player_index < 0 or self.action_player_index >= len(self.game_state.players):
            print(f"🔥 BOT_ACTION_DEBUG: Invalid action player index: {self.action_player_index}")
            return False
        
        current_player = self.game_state.players[self.action_player_index]
        print(f"🔥 BOT_ACTION_DEBUG: Current player: {current_player.name} (index {self.action_player_index})")
        
        # Get decision from the engine
        try:
            print("🔥 BOT_ACTION_DEBUG: Getting game state...")
            game_state = self.get_game_info()
            print("🔥 BOT_ACTION_DEBUG: Getting decision from engine...")
            decision = self.decision_engine.get_decision(self.action_player_index, game_state)
            print(f"🔥 BOT_ACTION_DEBUG: Decision received: {decision}")
            
            action_type = decision.get('action', ActionType.FOLD)
            amount = decision.get('amount', 0.0)
            explanation = decision.get('explanation', 'Bot decision')
            print(f"🔥 BOT_ACTION_DEBUG: Action: {action_type}, Amount: {amount}")
            
            # Store decision for history
            decision_record = {
                'player_index': self.action_player_index,
                'player_name': current_player.name,
                'action': action_type,
                'amount': amount,
                'explanation': explanation,
                'street': self.game_state.street,
                'timestamp': time.time()
            }
            self.decision_history.append(decision_record)
            self.current_decision_explanation = explanation
            
            # Execute the action
            print(f"🔥 BOT_ACTION_DEBUG: Executing action on state machine...")
            success = self.execute_action(current_player, action_type, amount)
            print(f"🔥 BOT_ACTION_DEBUG: Action execution result: {success}")
            
            if success:
                # Play sound for the action
                self._play_action_sound(action_type)
                
                if self.session_logger:
                    self.session_logger.log_system(
                        "INFO", "BOT_SESSION",
                        f"Bot action executed: {current_player.name} {action_type.value} ${amount}",
                        {
                            "player": current_player.name,
                            "action": action_type.value,
                            "amount": amount,
                            "explanation": explanation
                        }
                    )
            
            if success:
                return ({'action': action_type.value, 'amount': amount}, explanation)
            else:
                return None
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_SESSION",
                    f"Error executing bot action: {e}",
                    {"player_index": self.action_player_index}
                )
            return None
    
    def _play_action_sound(self, action: ActionType):
        """Play sound for the given action."""
        if self.sound_manager:
            try:
                sound_mapping = {
                    ActionType.FOLD: "player_action_fold",
                    ActionType.CHECK: "player_action_check", 
                    ActionType.CALL: "player_action_call",
                    ActionType.BET: "player_action_bet",
                    ActionType.RAISE: "player_action_raise",
                }
                sound_name = sound_mapping.get(action)
                if sound_name:
                    self.sound_manager.play_poker_event_sound(sound_name)
            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR", "BOT_SESSION",
                        f"Error playing sound: {e}"
                    )
    
    def get_display_state(self) -> Dict[str, Any]:
        """
        Get the current display state for UI rendering.
        
        Returns:
            Dict containing all information needed for UI updates
        """
        display_state = self.get_game_info()
        num_players = len(self.game_state.players)
        
        # All bot sessions show all cards (no hidden information)
        display_state["card_visibilities"] = [True] * num_players
        
        # Highlight the current action player
        display_state["player_highlights"] = [
            i == self.action_player_index for i in range(num_players)
        ]
        
        # Layout positions (simple sequential layout)
        display_state["layout_positions"] = [
            {"seat": i, "position": i} for i in range(num_players)
        ]
        
        # Session-specific information
        display_state["session_info"] = {
            "type": self.session_type,
            "active": self.session_active,
            "current_explanation": self.current_decision_explanation,
            "decision_count": len(self.decision_history),
            "engine_info": self.decision_engine.get_session_info()
        }
        
        return display_state
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get the complete decision history for this session."""
        return self.decision_history.copy()
    
    def get_current_explanation(self) -> str:
        """Get the explanation for the most recent decision."""
        return self.current_decision_explanation
    
    def reset_session(self):
        """Reset the session to its initial state."""
        self.stop_session()
        self.decision_engine.reset()
        self.decision_history.clear()
        self.current_decision_explanation = ""
        
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "BOT_SESSION",
                "Session reset completed",
                {"session_type": self.session_type}
            )


class GTOBotSession(BotSessionStateMachine):
    """Specialized bot session for GTO simulation."""
    
    def __init__(self, config: GameConfig, mode: str = "live"):
        """Initialize GTO bot session with GTO decision engine."""
        gto_engine = GTODecisionEngine(config.num_players)
        super().__init__(config, gto_engine, "gto", mode)
        self._hand_count = 0
    
    def start_hand(self):
        """Override to occasionally deal premium hands for testing."""
        print(f"🃏 GTOBotSession.start_hand() called!")
        self._hand_count += 1
        print(f"🃏 HAND_COUNT: Starting hand #{self._hand_count}")
        
        result = super().start_hand()
        
        # Force premium hands EVERY time for testing - do this AFTER the hand is fully initialized
        print(f"🃏 PREMIUM_HAND_TEST: FORCING premium hands for testing (hand #{self._hand_count})")
        # Use a slight delay to ensure the hand is fully set up
        if hasattr(self, 'after'):
            self.after(50, self._deal_premium_test_hand)
        else:
            self._deal_premium_test_hand()
        
        return result
    
    def _deal_premium_test_hand(self):
        """Deal a premium hand to UTG for testing purposes."""
        try:
            players = getattr(self, 'players', None) or getattr(self.game_state, 'players', [])
            print(f"🃏 PREMIUM_HAND_TEST: Found {len(players)} players to modify")
            
            if len(players) > 0:
                # Give UTG player (index 0) pocket kings for testing
                utg_player = players[0]
                utg_player.cards = ['Kh', 'Kd']
                print(f"🃏 PREMIUM_HAND_TEST: Gave {utg_player.name} pocket kings: {utg_player.cards}")
                
                # Give MP player (index 1) pocket aces for testing
                if len(players) > 1:
                    mp_player = players[1]
                    mp_player.cards = ['As', 'Ac']
                    print(f"🃏 PREMIUM_HAND_TEST: Gave {mp_player.name} pocket aces: {mp_player.cards}")
                
                # Give CO player (index 2) AK suited for testing
                if len(players) > 2:
                    co_player = players[2]
                    co_player.cards = ['Ah', 'Kh']
                    print(f"🃏 PREMIUM_HAND_TEST: Gave {co_player.name} AK suited: {co_player.cards}")
            else:
                print(f"🃏 PREMIUM_HAND_TEST: No players found to modify")
        except Exception as e:
            print(f"🃏 PREMIUM_HAND_TEST: Error dealing premium hands: {e}")
            # Don't let this crash the session start
    
    def set_sound_manager(self, sound_manager):
        """Set sound manager for audio feedback."""
        self.sound_manager = sound_manager
    
    def get_game_info(self) -> Dict[str, Any]:
        """Override to always reveal all cards for GTO educational purposes."""
        game_info = super().get_game_info()
        
        # Reveal all players' hole cards for educational purposes
        if "players" in game_info:
            for i, player_info in enumerate(game_info["players"]):
                player_info["cards_revealed"] = True
                
                # If cards are still placeholders, try to get actual cards from the player object
                if player_info.get("cards") == ['**', '**']:
                    # Try to get actual cards from the game state players
                    try:
                        actual_players = getattr(self.game_state, 'players', [])
                        if i < len(actual_players) and hasattr(actual_players[i], 'cards'):
                            actual_cards = actual_players[i].cards
                            if actual_cards and actual_cards != ['**', '**']:
                                player_info["cards"] = actual_cards
                                # Successfully revealed cards for GTO decision making
                    except Exception as e:
                        print(f"🃏 CARD_REVEAL: Error getting actual cards for player {i}: {e}")
        
        return game_info
    
    def get_display_state(self) -> Dict[str, Any]:
        """Override to ensure all cards are visible for GTO education."""
        display_state = super().get_display_state()
        
        # Ensure all player cards are visible
        num_players = len(self.game_state.players)
        display_state["card_visibilities"] = [True] * num_players
        
        # Ensure community cards are visible based on current street
        if "board" in display_state:
            display_state["community_cards_visible"] = True
        
        return display_state


class HandsReviewBotSession(BotSessionStateMachine):
    """Specialized bot session for hands review using preloaded data."""
    
    def __init__(self, config: GameConfig, decision_engine, mode: str = "review"):
        """Initialize hands review session with preloaded decision engine."""
        super().__init__(config, decision_engine, "hands_review", mode)
        self.preloaded_hand_data = None  # Will be set by the UI
    
    def set_sound_manager(self, sound_manager):
        """Set sound manager for audio feedback."""
        self.sound_manager = sound_manager
    
    def set_preloaded_hand_data(self, hand_data: Dict[str, Any]):
        """Set the preloaded hand data including initial player cards."""
        self.preloaded_hand_data = hand_data
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Override to load preloaded hand data instead of dealing new cards."""
        if self.preloaded_hand_data and 'initial_state' in self.preloaded_hand_data:
            # Load players from preloaded hand data
            players_data = self.preloaded_hand_data['initial_state'].get('players', [])
            
            # Import Player class and PokerState
            from .types import Player, PokerState
            
            # Create players with the exact cards from the hand data
            loaded_players = []
            for i, player_data in enumerate(players_data):
                player = Player(
                    name=player_data.get('name', f'Player {i+1}'),
                    stack=player_data.get('stack', 1000.0),
                    position=player_data.get('position', 'UTG'),
                    is_human=player_data.get('is_human', False),
                    is_active=player_data.get('is_active', True),
                    cards=player_data.get('cards', []),  # These are the actual hole cards!
                    current_bet=player_data.get('current_bet', 0.0)
                )
                loaded_players.append(player)
            
            print(f"🃏 HANDS_REVIEW: Loaded {len(loaded_players)} players with preloaded cards")
            for i, player in enumerate(loaded_players):
                print(f"🃏 HANDS_REVIEW: {player.name} -> {player.cards}")
            
            # CRITICAL: Set up the game state manually without calling parent's start_hand
            # because parent's start_hand would deal new cards and overwrite our preloaded cards
            self.hand_number += 1
            self.current_state = PokerState.START_HAND
            
            # Set the preloaded players directly
            self.game_state.players = loaded_players
            
            # Set additional game state from preloaded data
            initial_state = self.preloaded_hand_data['initial_state']
            self.game_state.pot = initial_state.get('pot', 0.0)
            self.game_state.current_bet = initial_state.get('current_bet', 0.0)
            self.game_state.street = initial_state.get('street', 'preflop')
            self.game_state.board = initial_state.get('board', [])
            if 'dealer_position' in initial_state:
                self.dealer_position = initial_state['dealer_position']
            
            # Set action positions manually (no dealing/shuffling needed)
            if self.config.num_players == 2:
                self.small_blind_position = self.dealer_position
                self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
            else:
                self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
                self.big_blind_position = (self.dealer_position + 2) % self.config.num_players
            
            # Set initial action player (after big blind)
            self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
            
            # Transition to preflop betting phase
            self.current_state = PokerState.PREFLOP_BETTING
            
            # Emit initial display state
            self._emit_display_state_event()
            
            print(f"🃏 HANDS_REVIEW: Hand initialized with preloaded data, street={self.game_state.street}")
        else:
            # Fallback to normal hand start if no preloaded data
            print("🃏 HANDS_REVIEW: No preloaded data, using normal hand start")
            super().start_hand(existing_players)
    
    def get_game_info(self) -> Dict[str, Any]:
        """Override to always reveal all cards for hands review educational purposes."""
        game_info = super().get_game_info()
        
        # Reveal all players' hole cards for educational purposes (same as GTO session)
        if "players" in game_info:
            for i, player_info in enumerate(game_info["players"]):
                player_info["cards_revealed"] = True
                
                # If cards are still placeholders, try to get actual cards from the player object
                if player_info.get("cards") == ['**', '**']:
                    # Try to get actual cards from the game state players
                    try:
                        actual_players = getattr(self.game_state, 'players', [])
                        if i < len(actual_players) and hasattr(actual_players[i], 'cards'):
                            actual_cards = actual_players[i].cards
                            if actual_cards and actual_cards != ['**', '**']:
                                player_info["cards"] = actual_cards
                    except Exception as e:
                        print(f"🃏 CARD_REVEAL: Error getting actual cards for player {i}: {e}")
        
        return game_info
    
    def get_display_state(self) -> Dict[str, Any]:
        """Override to ensure all cards are visible for hands review education."""
        display_state = super().get_display_state()
        
        # Ensure all player cards are visible (same as GTO session)
        num_players = len(self.game_state.players)
        display_state["card_visibilities"] = [True] * num_players
        
        # Ensure community cards are visible based on current street
        if "board" in display_state:
            display_state["community_cards_visible"] = True
        
        return display_state
