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
from .poker_types import Player, ActionType, PokerState
from .decision_engine_v2 import DecisionEngine, GTODecisionEngine, PreloadedDecisionEngine
from .hand_model import Hand


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
        print(f"🔍 BOT_DEBUG: action_player_index={self.action_player_index}, num_players={len(self.game_state.players)}")
        if self.action_player_index < 0 or self.action_player_index >= len(self.game_state.players):
            print(f"❌ BOT_ACTION_DEBUG: Invalid action player index: {self.action_player_index} (valid range: 0-{len(self.game_state.players)-1})")
            self.stop_session()  # Stop session instead of continuing with invalid state
            return False
        
        try:
            current_player = self.game_state.players[self.action_player_index]
        except IndexError as e:
            print(f"❌ BOT_ACTION_DEBUG: IndexError accessing player {self.action_player_index}: {e}")
            print(f"🔍 BOT_DEBUG: Players list length: {len(self.game_state.players)}")
            print(f"🔍 BOT_DEBUG: Players: {[p.name for p in self.game_state.players]}")
            self.stop_session()
            return False
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
            success = self.execute_action(current_player, action_type, amount)
            
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
            
            return success
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_SESSION",
                    f"Error executing bot action: {e}",
                    {"player_index": self.action_player_index}
                )
            return False
    
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

    def _sync_next_action_player_with_engine(self):
        """Align the next action player with the engine's next actor id."""
        try:
            eng = getattr(self, 'decision_engine', None)
            if not eng:
                return
            idx = getattr(eng, 'current_action_index', 0)
            actions = getattr(eng, 'actions_for_replay', [])
            if idx >= len(actions):
                return
            next_actor_id = getattr(actions[idx], 'actor_id', None)
            for i, p in enumerate(self.game_state.players):
                if getattr(p, 'name', '') == next_actor_id:
                    self.action_player_index = i
                    break
        except Exception:
            pass

    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Override to load preloaded hand data instead of dealing new cards."""
        print(f"🃏 HANDS_REVIEW: HandsReviewBotSession.start_hand() called!")
        print(f"🃏 HANDS_REVIEW: preloaded_hand_data exists: {self.preloaded_hand_data is not None}")
        if self.preloaded_hand_data:
            # Check if this is Hand Model format (new) or legacy format
            if 'hand_model' in self.preloaded_hand_data:
                print("🃏 HANDS_REVIEW: Using Hand Model format (robust)")
                return self._start_hand_from_hand_model(self.preloaded_hand_data['hand_model'])
            else:
                print("🃏 HANDS_REVIEW: Using legacy format (fallback)")
                # Legacy format handling
                # Try to get players from different possible locations in the data
                players_data = None
                if 'initial_state' in self.preloaded_hand_data:
                    players_data = self.preloaded_hand_data['initial_state'].get('players', [])
                elif 'players' in self.preloaded_hand_data:
                    players_data = self.preloaded_hand_data['players']
                else:
                    print("🃏 HANDS_REVIEW: No player data found")
                    return
        
        # Import Player class and PokerState
        from .poker_types import Player, PokerState
        
        # Create players with proper initial state reconstruction
        loaded_players = []
        for i, player_data in enumerate(players_data):
            # CRITICAL: Reconstruct initial state from corrupted final state data
            # The data contains final stacks, so we need to estimate initial stacks
            
            # Use either 'cards' or 'hole_cards' depending on data structure
            player_cards = player_data.get('cards', player_data.get('hole_cards', []))
            
            # For initial state, all players should be active and not folded
            # Use a reasonable starting stack if the final stack looks corrupted
            final_stack = player_data.get('stack', 1000.0)
            initial_stack = max(1000.0, final_stack)  # Ensure minimum reasonable stack
            
            player = Player(
                name=player_data.get('name', f'Player {i+1}'),
                stack=initial_stack,  # Use reconstructed initial stack
                position=player_data.get('position', 'UTG'),
                is_human=False,  # All GTO hands are bots
                is_active=True,  # Start with all players active
                cards=player_cards,  # Use the hole cards from data
                current_bet=0.0,  # ALWAYS start with 0 bets for clean replay
                has_folded=False,  # Start with no one folded
                has_acted_this_round=False,  # Fresh round
                is_all_in=False  # No one all-in initially
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
        
        # CRITICAL FIX: Start with completely clean game state
        # The original data is corrupted (final state), so we reconstruct initial state
        
        # Start with pristine poker state
        self.game_state.pot = 0.0  # Start with empty pot
        self.game_state.current_bet = 0.0  # No bets yet (will be set by blinds)
        self.game_state.street = 'preflop'  # Always start preflop
        self.game_state.board = []  # Empty board
        
        # Set dealer position - use default since data might be corrupted
        self.dealer_position = 0  # Start with first player as dealer
        
        # Set action positions manually (no dealing/shuffling needed)
        if self.config.num_players == 2:
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
        else:
            self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.config.num_players
        
        # CRITICAL: Post the blinds to set up correct game state
        # This ensures current_bet is correct for the first action
        sb_amount = self.config.small_blind
        bb_amount = self.config.big_blind
        
        # Post small blind
        sb_player = self.game_state.players[self.small_blind_position]
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        self.game_state.pot += sb_amount
        
        # Post big blind
        bb_player = self.game_state.players[self.big_blind_position]
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        self.game_state.pot += bb_amount
        
        # Set current bet to big blind amount
        self.game_state.current_bet = bb_amount
        
        print(f"🃏 HANDS_REVIEW: Posted blinds - SB: ${sb_amount}, BB: ${bb_amount}")
        print(f"🃏 HANDS_REVIEW: Current bet is now ${self.game_state.current_bet}")
        print(f"🃏 HANDS_REVIEW: Pot is now ${self.game_state.pot}")
        print(f"🃏 HANDS_REVIEW: Dealer: {self.dealer_position}, SB: {self.small_blind_position}, BB: {self.big_blind_position}")
        for i, player in enumerate(self.game_state.players):
            print(f"🃏 HANDS_REVIEW: Player {i}: {player.name}, current_bet=${player.current_bet}, stack=${player.stack}")
        
        # Set initial action player (after big blind)
        self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
        print(f"🃏 HANDS_REVIEW: First action player: {self.action_player_index} ({self.game_state.players[self.action_player_index].name})")
        
        # Transition to preflop betting phase
        self.current_state = PokerState.PREFLOP_BETTING
        
        # Emit initial display state
        self._emit_display_state_event()
        
        print(f"🃏 HANDS_REVIEW: Hand initialized with preloaded data, street={self.game_state.street}")
        
        
        
        
        
        
        
        
        
        
