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
            print(f"🔥 BOT_ACTION_DEBUG: Session complete - current_action: {self.decision_engine.current_action_index}, total: {self.decision_engine.total_actions}")
            self.stop_session()
            return False
        
        # Let the decision engine handle player alignment internally
        # Don't override action_player_index here - let the game state machine manage it
        
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
            self.session_logger = session_logger
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
            self.hand_number += 1
            self.current_state = PokerState.START_HAND
            self.game_state.players = loaded_players
            self.game_state.board = []
            self.game_state.pot = 0.0
            self.game_state.current_bet = 0.0
            self.game_state.street = "preflop"

            # Dealer/button seat if provided
            table = hand_data.get("table", {})
            button_seat = int(table.get("button_seat", 1))
            dealer_idx = None
            # Find player index by button seat
            for idx, p in enumerate(players_src):
                if int(p.get("seat", idx + 1)) == button_seat:
                    dealer_idx = idx
                    break
            self.dealer_position = dealer_idx if dealer_idx is not None else 0

            # Blind positions
            if self.config.num_players == 2:
                self.small_blind_position = self.dealer_position
                self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
            else:
                self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
                self.big_blind_position = (self.small_blind_position + 1) % self.config.num_players

            # Post blinds - use actual blind amounts from hand data if available
            # Default to config values, but prefer hand-specific values
            hand_metadata = hand_data.get("metadata", {})
            sb_amount = float(hand_metadata.get("small_blind", self.config.small_blind))
            bb_amount = float(hand_metadata.get("big_blind", self.config.big_blind))
            
            print(f"🃏 HANDS_REVIEW: Posting blinds - SB: ${sb_amount}, BB: ${bb_amount}")
            
            sb = self.game_state.players[self.small_blind_position]
            bb = self.game_state.players[self.big_blind_position]
            sb.current_bet = min(sb_amount, sb.stack)
            sb.stack = max(0.0, sb.stack - sb.current_bet)
            bb.current_bet = min(bb_amount, bb.stack)
            bb.stack = max(0.0, bb.stack - bb.current_bet)
            self.game_state.pot = round(sb.current_bet + bb.current_bet, 2)
            self.game_state.current_bet = bb.current_bet
            
            print(f"🃏 HANDS_REVIEW: Blinds posted - Pot: ${self.game_state.pot}, Current bet: ${self.game_state.current_bet}")

            # Action pointer (UTG after BB preflop)
            self.action_player_index = (self.big_blind_position + 1) % self.config.num_players

            # Transition to preflop betting and emit state
            self.current_state = PokerState.PREFLOP_BETTING
            self._emit_display_state_event()

            # Prepare historical actions
            actions_by_street = hand_data.get("actions", {}) or {}
            self.historical_actions = self._flatten_historical_actions(actions_by_street)
            
            # Filter out blind posting actions since we already posted blinds
            # This prevents conflicts between auto-posted blinds and historical POST_BLIND actions
            filtered_actions = []
            for action in self.historical_actions:
                action_type = str(action.get("action_type", "")).lower()
                if action_type not in ["post_blind", "post_small_blind", "post_big_blind"]:
                    filtered_actions.append(action)
                else:
                    print(f"🔄 Skipping blind action: {action_type} (blinds already posted)")
            
            self.historical_actions = filtered_actions
            self.action_index = 0
            
            print(f"📊 Loaded {len(filtered_actions)} actions (filtered out blind actions)")

            return True
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_LOAD", f"Failed to load hand: {e}")
            return False

    def step_forward(self) -> bool:
        """Execute the next historical action if available."""
        try:
            if self.action_index >= len(self.historical_actions):
                # Already complete; emit hand_complete once
                self._emit_event(
                    GameEvent(event_type="hand_complete", timestamp=time.time(), data={"hand_number": self.hand_number})
                )
                return False

            act = self.historical_actions[self.action_index]
            action_type = str(act.get("action_type", "fold")).lower()
            amount = float(act.get("amount", 0.0) or 0.0)

            # Determine current player by sequence; prefer provided player index/name
            player_idx = self.action_player_index
            name = act.get("player_name")
            seat = act.get("player_seat")
            if seat is not None:
                # Seats are 1-based; our players are in table order; try to find SeatX name
                target = f"Seat{int(seat)}"
                for i, p in enumerate(self.game_state.players):
                    if p.name == target:
                        player_idx = i
                        break
            elif name:
                for i, p in enumerate(self.game_state.players):
                    if p.name == name:
                        player_idx = i
                        break

            # Execute mapped action
            player = self.game_state.players[player_idx]
            from .poker_types import ActionType as AT
            if action_type == "fold":
                ok = self.execute_action(player, AT.FOLD, 0.0)
            elif action_type == "check":
                ok = self.execute_action(player, AT.CHECK, 0.0)
            elif action_type == "call":
                # Calculate the incremental call amount needed
                call_amt = max(0.0, self.game_state.current_bet - player.current_bet)
                ok = self.execute_action(player, AT.CALL, call_amt)
            elif action_type == "bet":
                ok = self.execute_action(player, AT.BET, amount)
            elif action_type == "raise":
                ok = self.execute_action(player, AT.RAISE, amount)
            else:
                ok = self.execute_action(player, AT.CHECK, 0.0)

            # Advance pointer if executed (or even if failed to avoid infinite loop)
            self.action_index += 1
            return bool(ok)
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "HANDS_REVIEW_STEP", f"Error in step_forward: {e}")
            return False

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
        
    def _start_hand_from_hand_model(self, hand_model: Hand):
        """Initialize the poker session from a robust Hand Model object."""
        from .poker_types import Player, PokerState
        
        print(f"🃏 HAND_MODEL: Starting hand {hand_model.metadata.hand_id}")
        print(f"🃏 HAND_MODEL: Players: {len(hand_model.seats)}")
        
        # Create players from Hand Model seats (with hole cards)
        loaded_players = []
        for seat in hand_model.seats:
            # Hand Model contains hole cards in metadata format - extract the actual cards
            hole_cards = []
            if hasattr(hand_model.metadata, 'hole_cards') and seat.player_uid in hand_model.metadata.hole_cards:
                hole_cards = hand_model.metadata.hole_cards[seat.player_uid]
            
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
        
        # Set up clean game state
        self.hand_number += 1
        self.current_state = PokerState.START_HAND
        
        # Set the players directly from Hand Model
        self.game_state.players = loaded_players
        
        # Initialize pristine poker state
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.street = 'preflop'
        self.game_state.board = []
        
        # Set dealer and blind positions
        self.dealer_position = 0  # Hand Model doesn't store button position, use default
        
        if self.config.num_players == 2:
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
        else:
            self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.config.num_players
        
        # Post blinds to set up correct initial state
        sb_player = self.game_state.players[self.small_blind_position]
        bb_player = self.game_state.players[self.big_blind_position]
        
        # Use blind amounts from Hand Model metadata if available, otherwise fall back to config
        sb_amount = getattr(hand_model.metadata, 'small_blind', self.config.small_blind)
        bb_amount = getattr(hand_model.metadata, 'big_blind', self.config.big_blind)
        
        print(f"🃏 HAND_MODEL: Using blinds from metadata - SB: ${sb_amount}, BB: ${bb_amount}")
        
        # CRITICAL: Post blinds correctly
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        self.game_state.pot += sb_amount
        
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        self.game_state.pot += bb_amount
        self.game_state.current_bet = bb_amount
        
        # Transition to preflop betting
        self.current_state = PokerState.PREFLOP_BETTING
        
        # Set first action player (same logic as base class)
        if self.config.num_players == 2:
            # Heads-up: SB/BTN acts first preflop
            self.action_player_index = self.small_blind_position
        else:
            # Multi-way: First action is UTG (after big blind)
            self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
        
        print(f"🃏 HAND_MODEL: First action player: {self.action_player_index} ({self.game_state.players[self.action_player_index].name})")
        
        # Log successful initialization
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "HANDS_REVIEW_HAND_MODEL",
                f"Hand Model session started: {hand_model.metadata.hand_id}",
                {
                    "hand_id": hand_model.metadata.hand_id,
                    "players": [p.name for p in loaded_players],
                    "pot": self.game_state.pot,
                    "current_bet": self.game_state.current_bet,
                    "dealer": self.dealer_position,
                    "sb": self.small_blind_position,
                    "bb": self.big_blind_position,
                    "first_action": self.action_player_index
                }
            )
        
        # Emit initial display state
        self._emit_display_state_event()
        
        print(f"🃏 HAND_MODEL: Hand initialized successfully, street={self.game_state.street}")
        return True
        
        
        
        
        
        
        
        
        
        
