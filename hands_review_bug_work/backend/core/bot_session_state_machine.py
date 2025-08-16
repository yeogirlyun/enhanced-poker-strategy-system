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
- Simplified architecture compared to complex event-driven approaches
- Clean separation between decision logic and game flow
"""

from typing import List, Dict, Any, Optional
import time

from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, GameEvent
from .poker_types import Player, ActionType, PokerState
from .decision_engine_v2 import DecisionEngine, GTODecisionEngine
from .hand_model import Hand


class BotSessionStateMachine:
    """
    Unified state machine for all bot-only poker sessions.
    
    This state machine handles both GTO simulation and hands review by using
    a DecisionEngine interface that abstracts the source of decisions. All
    timing, animation, and event handling is identical between session types.
    
    ARCHITECTURE: Uses composition with FlexiblePokerStateMachine as the
    single source of truth for game state, avoiding inheritance issues.
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
        # COMPOSITION: Create FPSM instance instead of inheriting
        self.fpsm = FlexiblePokerStateMachine(config, mode)
        
        self.decision_engine = decision_engine
        self.session_type = session_type
        self.decision_history: List[Dict[str, Any]] = []
        
        # All bot sessions use auto-advance for smooth gameplay
        self.config = config
        self.config.auto_advance = True
        
        # Sound manager for audio feedback
        self.sound_manager = None
        
        # Session state tracking
        self.session_active = False
        self.current_decision_explanation = ""
        
        # REMOVED: No more separate action_player_index - always use FPSM's
        
        if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
            self.fpsm.session_logger.log_system(
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
            if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                self.fpsm.session_logger.log_system(
                    "INFO", "BOT_SESSION",
                    f"Bot session started successfully",
                    {"session_type": self.session_type}
                )
            
            return True
            
        except Exception as e:
            if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                self.fpsm.session_logger.log_system(
                    "ERROR", "BOT_SESSION",
                    f"Failed to start bot session: {e}",
                    {"session_type": self.session_type}
                )
            return False
    
    def stop_session(self):
        """Stop the current bot session."""
        self.session_active = False
        if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
            self.fpsm.session_logger.log_system(
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
        
        # Get current action player from FPSM (always in sync)
        print(f"🔍 BOT_DEBUG: action_player_index={self.fpsm.action_player_index}, num_players={len(self.fpsm.game_state.players)}")
        print(f"🔍 BOT_DEBUG: Available players: {[p.name for p in self.fpsm.game_state.players]}")
        print(f"🔍 BOT_DEBUG: Current street: {self.fpsm.game_state.street}")
        print(f"🔍 BOT_DEBUG: FPSM action_player_index: {self.fpsm.action_player_index}")
        print(f"🔍 BOT_DEBUG: FPSM players length: {len(self.fpsm.game_state.players)}")
        
        if self.fpsm.action_player_index < 0 or self.fpsm.action_player_index >= len(self.fpsm.game_state.players):
            print(f"❌ BOT_ACTION_DEBUG: Invalid action player index: {self.fpsm.action_player_index} (valid range: 0-{len(self.fpsm.game_state.players)-1})")
            self.stop_session()  # Stop session instead of continuing with invalid state
            return False
        
        try:
            print(f"🔍 BOT_DEBUG: About to access player at index {self.fpsm.action_player_index}")
            current_player = self.fpsm.game_state.players[self.fpsm.action_player_index]
            print(f"🔍 BOT_DEBUG: Successfully accessed player: {current_player.name}")
        except IndexError as e:
            print(f"❌ BOT_ACTION_DEBUG: IndexError accessing player {self.fpsm.action_player_index}: {e}")
            print(f"🔍 BOT_DEBUG: Players list length: {len(self.fpsm.game_state.players)}")
            print(f"🔍 BOT_DEBUG: Players: {[p.name for p in self.fpsm.game_state.players]}")
            print(f"🔍 BOT_DEBUG: FPSM action_player_index: {self.fpsm.action_player_index}")
            self.stop_session()
            return False
        print(f"🔥 BOT_ACTION_DEBUG: Current player: {current_player.name} (index {self.fpsm.action_player_index})")
        
        # Get decision from the engine
        try:
            print("🔥 BOT_ACTION_DEBUG: Getting game state...")
            game_state = self.fpsm.get_game_info()
            print("🔥 BOT_ACTION_DEBUG: Getting decision from engine...")
            decision = self.decision_engine.get_decision(self.fpsm.action_player_index, game_state)
            print(f"🔥 BOT_ACTION_DEBUG: Decision received: {decision}")
            
            action_type = decision.get('action', ActionType.FOLD)
            amount = decision.get('amount', 0.0)
            explanation = decision.get('explanation', 'Bot decision')
            print(f"🔥 BOT_ACTION_DEBUG: Action: {action_type}, Amount: {amount}")
            
            # Store decision for history
            decision_record = {
                'player_index': self.fpsm.action_player_index,
                'player_name': current_player.name,
                'action': action_type,
                'amount': amount,
                'explanation': explanation,
                'street': self.fpsm.game_state.street,
                'timestamp': time.time()
            }
            self.decision_history.append(decision_record)
            self.current_decision_explanation = explanation
            
            # Execute the action
            success = self.fpsm.execute_action(current_player, action_type, amount)
            
            # DEBUG: Log the state after action execution
            if success:
                print(f"🔍 BOT_ACTION_DEBUG: Action executed successfully")
                print(f"   FPSM current_bet: ${self.fpsm.game_state.current_bet}")
                print(f"   FPSM pot: ${self.fpsm.game_state.pot}")
                print(f"   Player current_bet: ${current_player.current_bet}")
                print(f"   Player stack: ${current_player.stack}")
            else:
                print(f"🔍 BOT_ACTION_DEBUG: Action execution failed")
            
            if success:
                # Play sound for the action
                self._play_action_sound(action_type)
                
                if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                    self.fpsm.session_logger.log_system(
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
            if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                self.fpsm.session_logger.log_system(
                    "ERROR", "BOT_SESSION",
                    f"Error executing bot action: {e}",
                    {"player_index": self.fpsm.action_player_index}
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
                if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                    self.fpsm.session_logger.log_system(
                        "ERROR", "BOT_SESSION",
                        f"Error playing sound: {e}"
                    )
    
    def get_display_state(self) -> Dict[str, Any]:
        """
        Get the current display state for UI rendering.
        
        Returns:
            Dict containing all information needed for UI updates
        """
        display_state = self.fpsm.get_game_info()
        num_players = len(self.fpsm.game_state.players)
        
        # All bot sessions show all cards (no hidden information)
        display_state["card_visibilities"] = [True] * num_players
        
        # Highlight the current action player
        display_state["player_highlights"] = [
            i == self.fpsm.action_player_index for i in range(num_players)
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
        
        if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
            self.fpsm.session_logger.log_system(
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
            players = getattr(self, 'players', None) or getattr(self.fpsm.game_state, 'players', [])
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
                        actual_players = getattr(self.fpsm.game_state, 'players', [])
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
        num_players = len(self.fpsm.game_state.players)
        display_state["card_visibilities"] = [True] * num_players
        
        # Ensure community cards are visible based on current street
        if "board" in display_state:
            display_state["community_cards_visible"] = True
        
        return display_state


class HandsReviewBotSession(BotSessionStateMachine):
    """Specialized bot session for hands review using preloaded data."""
    
    def __init__(self, config: GameConfig, session_logger=None, decision_engine=None, mode: str = "review"):
        """Initialize hands review session.
        - Accept optional session_logger for tests/backward-compat.
        - If no decision_engine provided, use an empty PreloadedDecisionEngine.
        """
        if decision_engine is None:
            # Create a simple fallback decision engine
            class FallbackDecisionEngine(DecisionEngine):
                def get_decision(self, player_index, game_state):
                    return {'action': ActionType.CHECK, 'amount': 0.0, 'explanation': 'Fallback', 'confidence': 0.0}
                def is_session_complete(self): return False
                def reset(self): pass
                def get_session_info(self): return {'engine_type': 'Fallback'}
            
            decision_engine = FallbackDecisionEngine()
        super().__init__(config, decision_engine, "hands_review", mode)
        if session_logger is not None:
            self.fpsm.session_logger = session_logger # Assign session_logger to fpsm
        self.preloaded_hand_data = None  # Will be set by the UI
        # Compatibility fields for legacy tests
        self.historical_actions: List[Dict[str, Any]] = []
        self.current_hand_data: Dict[str, Any] = {}
        self.action_index: int = 0
    
    def set_sound_manager(self, sound_manager):
        """Set sound manager for audio feedback."""
        self.sound_manager = sound_manager
    
    def set_preloaded_hand_data(self, hand_data: Dict[str, Any]):
        """Set the preloaded hand data including initial player cards."""
        self.preloaded_hand_data = hand_data



    # ----------------- Legacy Hands Review Compatibility -----------------
    def _flatten_historical_actions(self, actions_in) -> List[Dict[str, Any]]:
        """Flatten actions to a single chronological list.
        Accepts either a list (already flat) or a dict keyed by streets.
        """
        # If already a flat list, return as-is
        if isinstance(actions_in, list):
            return list(actions_in)
        # Else expect dict keyed by street names
        order: List[str] = ["preflop", "flop", "turn", "river"]
        flat: List[Dict[str, Any]] = []
        actions_by_street = actions_in or {}
        for street in order:
            items = actions_by_street.get(street, []) or []
            for a in items:
                d = dict(a)
                d.setdefault("street", street)
                flat.append(d)
        return flat

    def load_hand_for_review(self, hand_data: Dict[str, Any]) -> bool:
        """Load a single legacy-format hand dict for review.

        Sets up players, posts blinds, prepares historical_actions, and
        initializes state for step_forward().
        """
        try:
            self.current_hand_data = hand_data
            # Build players from hand data
            players_src = hand_data.get("players", [])
            loaded_players: List[Player] = []
            # Map seat to index
            seat_to_index: Dict[int, int] = {}
            for i, p in enumerate(players_src):
                seat_no = int(p.get("seat", i + 1))
                name = f"Seat{seat_no}"
                seat_to_index[seat_no] = i
                starting_stack = float(p.get("starting_stack", p.get("stack", self.config.starting_stack)))
                cards = p.get("hole_cards", p.get("cards", []))
                loaded_players.append(
                    Player(
                        name=name,
                        stack=starting_stack,
                        position="",
                        is_human=False,
                        is_active=True,
                        cards=list(cards) if isinstance(cards, list) else [],
                    )
                )

            # Initialize core state
            self.fpsm.hand_number += 1
            self.fpsm.current_state = PokerState.START_HAND
            self.fpsm.game_state.players = loaded_players
            self.fpsm.game_state.board = []
            self.fpsm.game_state.pot = 0.0
            self.fpsm.game_state.current_bet = 0.0
            self.fpsm.game_state.street = "preflop"

            # Dealer/button seat if provided
            table = hand_data.get("table", {})
            button_seat = int(table.get("button_seat", 1))
            dealer_idx = None
            # Find player index by button seat
            for idx, p in enumerate(players_src):
                if int(p.get("seat", idx + 1)) == button_seat:
                    dealer_idx = idx
                    break
            self.fpsm.dealer_position = dealer_idx if dealer_idx is not None else 0

            # Blind positions
            if self.config.num_players == 2:
                self.fpsm.small_blind_position = self.fpsm.dealer_position
                self.fpsm.big_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
            else:
                self.fpsm.small_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
                self.fpsm.big_blind_position = (self.fpsm.small_blind_position + 1) % self.config.num_players

            # Post blinds
            sb_amount = float(self.config.small_blind)
            bb_amount = float(self.config.big_blind)
            sb = self.fpsm.game_state.players[self.fpsm.small_blind_position]
            bb = self.fpsm.game_state.players[self.fpsm.big_blind_position]
            sb.current_bet = min(sb_amount, sb.stack)
            sb.stack = max(0.0, sb.stack - sb.current_bet)
            bb.current_bet = min(bb_amount, bb.stack)
            bb.stack = max(0.0, bb.stack - bb.current_bet)
            self.fpsm.game_state.pot = round(sb.current_bet + bb.current_bet, 2)
            self.fpsm.game_state.current_bet = bb.current_bet

            # Action pointer (UTG after BB preflop)
            self.fpsm.action_player_index = (self.fpsm.big_blind_position + 1) % self.fpsm.config.num_players

            # Transition to preflop betting and emit state
            self.fpsm.current_state = PokerState.PREFLOP_BETTING
            self.fpsm._emit_display_state_event()

            # Prepare historical actions
            actions_by_street = hand_data.get("actions", {}) or {}
            self.historical_actions = self._flatten_historical_actions(actions_by_street)
            self.action_index = 0

            return True
        except Exception as e:
            if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                self.fpsm.session_logger.log_system("ERROR", "HANDS_REVIEW_LOAD", f"Failed to load hand: {e}")
            return False

    def step_forward(self) -> bool:
        """Execute the next historical action if available."""
        try:
            if self.action_index >= len(self.historical_actions):
                # Already complete; emit hand_complete once
                self.fpsm._emit_event(
                    GameEvent(event_type="hand_complete", timestamp=time.time(), data={"hand_number": self.fpsm.hand_number})
                )
                return False

            act = self.historical_actions[self.action_index]
            action_type = str(act.get("action_type", "fold")).lower()
            amount = float(act.get("amount", 0.0) or 0.0)

            # Determine current player by sequence; prefer provided player index/name
            player_idx = self.fpsm.action_player_index
            name = act.get("player_name")
            seat = act.get("player_seat")
            if seat is not None:
                # Seats are 1-based; our players are in table order; try to find SeatX name
                target = f"Seat{int(seat)}"
                for i, p in enumerate(self.fpsm.game_state.players):
                    if p.name == target:
                        player_idx = i
                        break
            elif name:
                for i, p in enumerate(self.fpsm.game_state.players):
                    if p.name == name:
                        player_idx = i
                        break

            # Execute mapped action
            player = self.fpsm.game_state.players[player_idx]
            from .poker_types import ActionType as AT
            if action_type == "fold":
                ok = self.fpsm.execute_action(player, AT.FOLD, 0.0)
            elif action_type == "check":
                ok = self.fpsm.execute_action(player, AT.CHECK, 0.0)
            elif action_type == "call":
                call_amt = max(0.0, self.fpsm.game_state.current_bet - player.current_bet)
                ok = self.fpsm.execute_action(player, AT.CALL, call_amt)
            elif action_type == "bet":
                ok = self.fpsm.execute_action(player, AT.BET, amount)
            elif action_type == "raise":
                ok = self.fpsm.execute_action(player, AT.RAISE, amount)
            else:
                ok = self.fpsm.execute_action(player, AT.CHECK, 0.0)

            # Advance pointer if executed (or even if failed to avoid infinite loop)
            self.action_index += 1
            return bool(ok)
        except Exception as e:
            if hasattr(self.fpsm, 'session_logger') and self.fpsm.session_logger:
                self.fpsm.session_logger.log_system("ERROR", "HANDS_REVIEW_STEP", f"Error in step_forward: {e}")
            return False

    def _align_action_player_with_engine(self):
        """Remove this old method - we now use FPSM's action_player_index directly."""
        pass

    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Override to load preloaded hand data instead of dealing new cards."""
        try:
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
            
            print(f"🃏 HANDS_REVIEW: About to process players_data: {players_data}")
            
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
            
            # CRITICAL: Call FPSM's start_hand to initialize the deck and game state
            # This ensures the deck is properly created and shuffled
            print(f"🃏 HANDS_REVIEW: Calling FPSM start_hand to initialize deck and game state")
            print(f"🃏 HANDS_REVIEW: Before FPSM start_hand - deck size: {len(self.fpsm.game_state.deck)}")
            print(f"🃏 HANDS_REVIEW: Before FPSM start_hand - deck contents: {self.fpsm.game_state.deck}")
            
            self.fpsm.start_hand()
            
            print(f"🃏 HANDS_REVIEW: After FPSM start_hand - deck size: {len(self.fpsm.game_state.deck)}")
            print(f"🃏 HANDS_REVIEW: After FPSM start_hand - deck contents: {self.fpsm.game_state.deck[:10]}...")
            
            # Now override the players with our preloaded data (preserving the deck)
            print(f"🃏 HANDS_REVIEW: Overriding players with preloaded data")
            print(f"🃏 HANDS_REVIEW: Before override - deck size: {len(self.fpsm.game_state.deck)}")
            
            self.fpsm.game_state.players = loaded_players
            
            print(f"🃏 HANDS_REVIEW: After override - deck size: {len(self.fpsm.game_state.deck)}")
            print(f"🃏 HANDS_REVIEW: After override - deck contents: {self.fpsm.game_state.deck[:10]}...")
            
            # CRITICAL: Post the blinds to set up correct game state
            # This ensures current_bet is correct for the first action
            sb_amount = self.config.small_blind
            bb_amount = self.config.big_blind
            
            # Post small blind
            sb_player = self.fpsm.game_state.players[self.fpsm.small_blind_position]
            sb_player.current_bet = sb_amount
            sb_player.stack -= sb_amount
            self.fpsm.game_state.pot += sb_amount
            
            # Post big blind
            bb_player = self.fpsm.game_state.players[self.fpsm.big_blind_position]
            bb_player.current_bet = bb_amount
            bb_player.stack -= bb_amount
            self.fpsm.game_state.pot += bb_amount
            
            # Set the current bet to the big blind amount
            self.fpsm.game_state.current_bet = bb_amount
            
            # Set the first action player (special handling for heads-up)
            if self.config.num_players == 2:
                # Heads-up: SB/BTN acts first preflop (small blind is also button)
                self.fpsm.action_player_index = self.fpsm.small_blind_position
            else:
                # Multi-way: First action is UTG (after big blind)
                self.fpsm.action_player_index = (
                    self.fpsm.big_blind_position + 1
                ) % self.fpsm.config.num_players
            
            # Transition to preflop betting
            self.fpsm.transition_to(PokerState.PREFLOP_BETTING)
            
            # Emit display state event
            self.fpsm._emit_display_state_event()
            
            print(f"🃏 HANDS_REVIEW: Hand setup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Exception in start_hand: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _start_hand_from_hand_model(self, hand_model):
        """Initialize the poker session from a robust Hand Model object."""
        from .poker_types import Player, PokerState
        
        print(f"🃏 HAND_MODEL: Starting hand {hand_model.metadata.hand_id}")
        print(f"🃏 HAND_MODEL: Players: {len(hand_model.seats)}")
        
        # CRITICAL FIX: Read actual blind values from Hand Model metadata
        # Use Hand Model values instead of hardcoded config values
        actual_sb = getattr(hand_model.metadata, 'small_blind', self.config.small_blind)
        actual_bb = getattr(hand_model.metadata, 'big_blind', self.config.big_blind)
        
        print(f"🃏 HAND_MODEL: Actual blinds - SB: ${actual_sb}, BB: ${actual_bb}")
        print(f"🃏 HAND_MODEL: Config blinds - SB: ${self.config.small_blind}, BB: ${self.config.big_blind}")
        
        # Create players from Hand Model seats (with hole cards)
        loaded_players = []
        for seat in hand_model.seats:
            # Hand Model contains hole cards in metadata format - extract the actual cards
            hole_cards = []
            if hasattr(hand_model.metadata, 'hole_cards') and seat.player_uid in hand_model.metadata.hole_cards:
                hole_cards = hand_model.metadata.hole_cards[seat.player_uid]
            
            # ENFORCE CANONICAL UID SCHEME: Use player_uid consistently
            player = Player(
                name=seat.player_uid,  # Use canonical player UID (e.g., "seat1")
                stack=seat.starting_stack,  # Use starting stack from Hand Model
                position='UTG',  # Position will be set by the state machine
                is_human=False,  # All hands review are bots
                is_active=True,  # All players start active
                cards=hole_cards,  # Use hole cards from Hand Model
                current_bet=0.0,  # Always start with clean slate
                has_folded=False,  # No one folded initially
                has_acted_this_round=False,  # Fresh round
                is_all_in=False  # No one all-in initially
            )
            loaded_players.append(player)
        
        print(f"🃏 HAND_MODEL: Loaded {len(loaded_players)} players")
        for i, player in enumerate(loaded_players):
            print(f"🃏 HAND_MODEL: {player.name} -> {player.cards} (stack: ${player.stack})")
        self.fpsm.game_state.players = loaded_players
        
        self.fpsm.game_state.players = loaded_players
        
        # Set dealer and blind positions
        # ENFORCE CANONICAL UID SCHEME: Use button_seat_no from Hand Model if available
        if hasattr(hand_model.metadata, 'button_seat_no') and hand_model.metadata.button_seat_no is not None:
            # Find player index by button seat number
            button_seat_no = hand_model.metadata.button_seat_no
            self.fpsm.dealer_position = None
            for i, seat in enumerate(hand_model.seats):
                if seat.seat_no == button_seat_no:
                    self.fpsm.dealer_position = i
                    break
            if self.fpsm.dealer_position is None:
                self.fpsm.dealer_position = 0  # Fallback to default
                print(f"⚠️ HAND_MODEL: Button seat {button_seat_no} not found, using default position 0")
        else:
            self.fpsm.dealer_position = 0  # Hand Model doesn't store button position, use default
            print(f"⚠️ HAND_MODEL: No button seat info, using default position 0")
        
        if self.config.num_players == 2:
            self.fpsm.small_blind_position = self.fpsm.dealer_position
            self.fpsm.big_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
        else:
            self.fpsm.small_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
            self.fpsm.big_blind_position = (self.fpsm.dealer_position + 2) % self.config.num_players
        
        print(f"🃏 HAND_MODEL: Dealer: position {self.fpsm.dealer_position} ({self.fpsm.game_state.players[self.fpsm.dealer_position].name})")
        print(f"🃏 HAND_MODEL: SB: position {self.fpsm.small_blind_position} ({self.fpsm.game_state.players[self.fpsm.small_blind_position].name})")
        print(f"🃏 HAND_MODEL: BB: position {self.fpsm.big_blind_position} ({self.fpsm.game_state.players[self.fpsm.big_blind_position].name})")
        
        # CRITICAL FIX: Post blinds using actual values from Hand Model
        sb_player = self.fpsm.game_state.players[self.fpsm.small_blind_position]
        bb_player = self.fpsm.game_state.players[self.fpsm.big_blind_position]
        
        # Use actual blind values from Hand Model, not hardcoded config values
        sb_amount = actual_sb
        bb_amount = actual_bb
        
        print(f"🃏 HAND_MODEL: Posting blinds - SB: ${sb_amount}, BB: ${bb_amount}")
        
        # CRITICAL: Post blinds correctly
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        self.fpsm.game_state.pot += sb_amount
        
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        self.fpsm.game_state.pot += bb_amount
        self.fpsm.game_state.current_bet = bb_amount
        
        print(f"🃏 HAND_MODEL: After blinds - Pot: ${self.fpsm.game_state.pot}, Current bet: ${self.fpsm.game_state.current_bet}")
        print(f"🃏 HAND_MODEL: SB player {sb_player.name}: bet=${sb_player.current_bet}, stack=${sb_player.stack}")
        print(f"🃏 HAND_MODEL: BB player {bb_player.name}: bet=${bb_player.current_bet}, stack=${bb_player.stack}")
        
        # Set first action player (same logic as base class)
        if self.config.num_players == 2:
            # Heads-up: SB/BTN acts first preflop
            self.fpsm.action_player_index = self.fpsm.small_blind_position
        else:
            # Multi-way: First action is UTG (after big blind)
            self.fpsm.action_player_index = (self.fpsm.big_blind_position + 1) % self.fpsm.config.num_players
        
        print(f"🃏 HAND_MODEL: First action player: {self.fpsm.action_player_index} ({self.fpsm.game_state.players[self.fpsm.action_player_index].name})")
        
        # Transition to preflop betting
        self.fpsm.transition_to(PokerState.PREFLOP_BETTING)
        
        # Emit initial display state
        self.fpsm._emit_display_state_event()
        
        print(f"🃏 HAND_MODEL: Hand initialized successfully, street={self.fpsm.game_state.street}")
        return True
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get game information from the FPSM."""
        return self.fpsm.get_game_info()
    
    def get_game_state(self):
        """Get the current game state from the FPSM."""
        return self.fpsm.game_state
    
    def is_hand_complete(self) -> bool:
        """Check if the hand is complete by delegating to FPSM."""
        return self.fpsm.current_state in [
            PokerState.SHOWDOWN,
            PokerState.END_HAND
        ]
    
    def get_display_state(self) -> Dict[str, Any]:
        """Get display state for UI rendering."""
        # Get game info from FPSM
        game_info = self.fpsm.get_game_info()
        num_players = len(self.fpsm.game_state.players)
        
        # All bot sessions show all cards (no hidden information)
        card_visibilities = [True] * num_players
        
        # Highlight the current action player
        player_highlights = [
            i == self.fpsm.action_player_index for i in range(num_players)
        ]
        
        # Layout positions (simple sequential layout)
        layout_positions = [
            {"seat": i, "position": i} for i in range(num_players)
        ]
        
        # Session-specific information
        session_info = {
            "type": self.session_type,
            "active": self.session_active,
            "current_explanation": self.current_decision_explanation,
            "decision_count": len(self.decision_history),
            "engine_info": self.decision_engine.get_session_info()
        }
        
        # Combine all display state information
        display_state = {
            **game_info,
            "card_visibilities": card_visibilities,
            "player_highlights": player_highlights,
            "layout_positions": layout_positions,
            "session_info": session_info
        }
        
        return display_state
        
        
        
        
        
        
        
        
        
        
