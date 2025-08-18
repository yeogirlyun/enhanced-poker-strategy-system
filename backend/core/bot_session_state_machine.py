#!/usr/bin/env python3
"""
Unified Bot Session State Machine - COMPOSITION ARCHITECTURE

This module provides a unified state machine for all bot-only poker sessions,
including GTO simulation and hands review. By using COMPOSITION with FPSM,
the same state machine can handle different decision sources while maintaining
consistent behavior and event flows.

ARCHITECTURE: Uses composition with FlexiblePokerStateMachine as the
single source of truth for game state, avoiding inheritance issues.

Key benefits:
- Code reuse between GTO and hands review sessions
- Consistent timing and animation behavior
- Clean separation between bot session logic and poker game logic
- Easier testing and mocking
"""

from typing import List, Dict, Any, Optional
import time

from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from .poker_types import Player, ActionType, PokerState
from .decision_engine import DecisionEngine, GTODecisionEngine


class BotSessionStateMachine:
    """
    Unified state machine for all bot-only poker sessions.
    
    This state machine handles both GTO simulation and hands review by using
    COMPOSITION with FlexiblePokerStateMachine. All poker operations delegate
    to self.fpsm, providing clean separation of concerns.
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
        
        # CRITICAL: Set auto-advance on the FPSM's config (composition model)
        self.fpsm.config.auto_advance = True
        print(f"🔧 BOT_SESSION: Set FPSM auto_advance = {self.fpsm.config.auto_advance}")
        
        # Sound manager for audio feedback
        self.sound_manager = None
        
        # Session state tracking
        self.session_active = False
        self.current_decision_explanation = ""
        
        # Session logger from FPSM
        self.session_logger = getattr(self.fpsm, 'session_logger', None)
        
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
        
        # Get current action player from FPSM
        action_player_index = getattr(self.fpsm, 'action_player_index', 0)
        print(f"🔍 BOT_DEBUG: action_player_index={action_player_index}, num_players={len(self.fpsm.game_state.players)}")
        print(f"🔍 BOT_DEBUG: Available players: {[p.name for p in self.fpsm.game_state.players]}")
        print(f"🔍 BOT_DEBUG: Current street: {self.fpsm.game_state.street}")
        print(f"🔍 BOT_DEBUG: FPSM action_player_index: {action_player_index}")
        print(f"🔍 BOT_DEBUG: FPSM players length: {len(self.fpsm.game_state.players)}")
        
        # Validate action player index
        if action_player_index < 0 or action_player_index >= len(self.fpsm.game_state.players):
            print(f"❌ BOT_ACTION_DEBUG: Invalid action player index: {action_player_index} (valid range: 0-{len(self.fpsm.game_state.players)-1})")
            return False
        
        try:
            print(f"🔍 BOT_DEBUG: About to access player at index {action_player_index}")
            current_player = self.fpsm.game_state.players[action_player_index]
        except IndexError as e:
            print(f"❌ BOT_ACTION_DEBUG: IndexError accessing player {action_player_index}: {e}")
            print(f"🔍 BOT_DEBUG: Players list length: {len(self.fpsm.game_state.players)}")
            print(f"🔍 BOT_DEBUG: Players: {[p.name for p in self.fpsm.game_state.players]}")
            print(f"🔍 BOT_DEBUG: FPSM action_player_index: {action_player_index}")
            return False
        
        print(f"🔥 BOT_ACTION_DEBUG: Current player: {current_player.name} (index {action_player_index})")
        
        try:
            # Get current game state from FPSM
            game_state = self.fpsm.get_game_info()
            # Snapshot pre-action values for post-adjustment in review mode
            gs_obj = self.fpsm.game_state
            pre_snapshot = {
                'street': getattr(gs_obj, 'street', 'preflop'),
                'pot': float(getattr(gs_obj, 'pot', 0.0)),
                'current_bet': float(getattr(gs_obj, 'current_bet', 0.0)),
                'player_current_bet': float(getattr(current_player, 'current_bet', 0.0)),
                'player_stack': float(getattr(current_player, 'stack', 0.0)),
            }
            
            # Get decision from decision engine
            decision = self.decision_engine.get_decision(action_player_index, game_state)
            
            # Log the decision
            print(f"🔥 BOT_ACTION_DEBUG: Decision: {decision}")
            
            # Extract action details
            action_type = decision.get('action')
            amount = decision.get('amount', 0.0)
            explanation = decision.get('explanation', 'No explanation')
            confidence = decision.get('confidence', 0.0)
            
            # Log action details
            print(f"🔥 BOT_ACTION_DEBUG: Executing action:")
            print(f"   Player: {current_player.name}")
            print(f"   Action: {action_type}")
            print(f"   Amount: ${amount}")
            print(f"   Explanation: {explanation}")
            print(f"   Confidence: {confidence}")
            print(f"   Street: {self.fpsm.game_state.street}")
            
            # Log detailed pre-action state
            print(f"💰 PRE-ACTION STATE:")
            print(f"   FPSM pot: ${getattr(self.fpsm.game_state, 'pot', 0.0)}")
            print(f"   FPSM current_bet: ${getattr(self.fpsm.game_state, 'current_bet', 0.0)}")
            print(f"   Player {current_player.name} stack: ${getattr(current_player, 'stack', 0.0)}")
            print(f"   Player {current_player.name} current_bet: ${getattr(current_player, 'current_bet', 0.0)}")
            if len(self.fpsm.game_state.players) > 1:
                other_player = self.fpsm.game_state.players[1 - action_player_index]
                print(f"   Player {other_player.name} stack: ${getattr(other_player, 'stack', 0.0)}")
                print(f"   Player {other_player.name} current_bet: ${getattr(other_player, 'current_bet', 0.0)}")
            
            # If the decision engine specifies an explicit actor index, override turn
            actor_index_override = decision.get('actor_index')
            if isinstance(actor_index_override, int) and 0 <= actor_index_override < len(self.fpsm.game_state.players):
                self.fpsm.action_player_index = actor_index_override
                current_player = self.fpsm.game_state.players[self.fpsm.action_player_index]

            # REVIEW-ONLY CHIP MATH SHIM: ensure pot/current_bet are correct in review mode
            # without modifying FPSM internals.
            try:
                if self.session_type == "hands_review":
                    if self.session_logger:
                        self.session_logger.log_system(
                            "DEBUG", "REVIEW_SHIM_PRE",
                            "Pre-shim state",
                            {
                                "street": getattr(self.fpsm.game_state, 'street', ''),
                                "actor_index": getattr(self.fpsm, 'action_player_index', -1),
                                "actor_name": getattr(current_player, 'name', ''),
                                "pot": getattr(self.fpsm.game_state, 'pot', 0.0),
                                "current_bet": getattr(self.fpsm.game_state, 'current_bet', 0.0),
                                "player_current_bet": getattr(current_player, 'current_bet', 0.0),
                                "amount": amount,
                                "action": action_type.name if hasattr(action_type, 'name') else str(action_type),
                            },
                        )
                    self._apply_review_chip_delta(current_player, action_type, amount)
                    if self.session_logger:
                        self.session_logger.log_system(
                            "DEBUG", "REVIEW_SHIM_POST",
                            "Post-shim state",
                            {
                                "street": getattr(self.fpsm.game_state, 'street', ''),
                                "actor_index": getattr(self.fpsm, 'action_player_index', -1),
                                "actor_name": getattr(current_player, 'name', ''),
                                "pot": getattr(self.fpsm.game_state, 'pot', 0.0),
                                "current_bet": getattr(self.fpsm.game_state, 'current_bet', 0.0),
                                "player_current_bet": getattr(current_player, 'current_bet', 0.0),
                                "amount": amount,
                                "action": action_type.name if hasattr(action_type, 'name') else str(action_type),
                            },
                        )
            except Exception as _e:
                # Do not break flow if shim fails
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR", "REVIEW_SHIM_ERROR",
                        f"Shim failure: {_e}",
                        {"action": str(action_type), "amount": amount},
                    )
                pass

            # Execute the action through FPSM
            success = self.fpsm.execute_action(current_player, action_type, amount)
            
            if success:
                print(f"✅ BOT_ACTION_DEBUG: Action executed successfully")
                
                # Log detailed post-action state
                print(f"💰 POST-ACTION STATE:")
                print(f"   FPSM pot: ${getattr(self.fpsm.game_state, 'pot', 0.0)}")
                print(f"   FPSM current_bet: ${getattr(self.fpsm.game_state, 'current_bet', 0.0)}")
                print(f"   Player {current_player.name} stack: ${getattr(current_player, 'stack', 0.0)}")
                print(f"   Player {current_player.name} current_bet: ${getattr(current_player, 'current_bet', 0.0)}")
                if len(self.fpsm.game_state.players) > 1:
                    other_player = self.fpsm.game_state.players[1 - action_player_index]
                    print(f"   Player {other_player.name} stack: ${getattr(other_player, 'stack', 0.0)}")
                    print(f"   Player {other_player.name} current_bet: ${getattr(other_player, 'current_bet', 0.0)}")
                
                # Calculate and log the changes
                pot_change = getattr(self.fpsm.game_state, 'pot', 0.0) - pre_snapshot.get('pot', 0.0)
                current_bet_change = getattr(self.fpsm.game_state, 'current_bet', 0.0) - pre_snapshot.get('current_bet', 0.0)
                stack_change = getattr(current_player, 'stack', 0.0) - pre_snapshot.get('player_stack', 0.0)
                player_bet_change = getattr(current_player, 'current_bet', 0.0) - pre_snapshot.get('player_current_bet', 0.0)
                
                print(f"📊 CHANGES FROM ACTION:")
                print(f"   Pot change: ${pot_change}")
                print(f"   Current bet change: ${current_bet_change}")
                print(f"   Player stack change: ${stack_change}")
                print(f"   Player current_bet change: ${player_bet_change}")

                # Post-exec reconciliation for review mode
                try:
                    if self.session_type == "hands_review":
                        if self.session_logger:
                            self.session_logger.log_system(
                                "DEBUG", "REVIEW_POST_EXEC_PRE",
                                "Pre-reconcile snapshot",
                                {
                                    "street": getattr(self.fpsm.game_state, 'street', ''),
                                    "actor_index": getattr(self.fpsm, 'action_player_index', -1),
                                    "actor_name": getattr(current_player, 'name', ''),
                                    "pot": getattr(self.fpsm.game_state, 'pot', 0.0),
                                    "current_bet": getattr(self.fpsm.game_state, 'current_bet', 0.0),
                                    "player_current_bet": getattr(current_player, 'current_bet', 0.0),
                                    "amount": amount,
                                    "action": action_type.name if hasattr(action_type, 'name') else str(action_type),
                                },
                            )
                        self._apply_review_post_exec_adjustment(current_player, action_type, amount, pre_snapshot)
                        if self.session_logger:
                            self.session_logger.log_system(
                                "DEBUG", "REVIEW_POST_EXEC_POST",
                                "Post-reconcile snapshot",
                                {
                                    "street": getattr(self.fpsm.game_state, 'street', ''),
                                    "actor_index": getattr(self.fpsm, 'action_player_index', -1),
                                    "actor_name": getattr(current_player, 'name', ''),
                                    "pot": getattr(self.fpsm.game_state, 'pot', 0.0),
                                    "current_bet": getattr(self.fpsm.game_state, 'current_bet', 0.0),
                                    "player_current_bet": getattr(current_player, 'current_bet', 0.0),
                                    "amount": amount,
                                    "action": action_type.name if hasattr(action_type, 'name') else str(action_type),
                                },
                            )
                except Exception as _e:
                    if self.session_logger:
                        self.session_logger.log_system(
                            "ERROR", "REVIEW_POST_EXEC_ERROR",
                            f"Post-exec reconcile failure: {_e}",
                            {"action": str(action_type), "amount": amount},
                        )
                
                # Record the decision in history
                self.decision_history.append({
                    'timestamp': time.time(),
                    'player_index': action_player_index,
                'player_name': current_player.name,
                'action': action_type,
                'amount': amount,
                'explanation': explanation,
                    'confidence': confidence,
                    'street': self.fpsm.game_state.street,
                    'success': True
                })
                
                # Log success
                if self.session_logger:
                    self.session_logger.log_system(
                        "INFO", "BOT_ACTION_EXECUTED",
                        f"Bot action executed successfully",
                        {
                            "player_name": current_player.name,
                            "action": action_type.value if hasattr(action_type, 'value') else str(action_type),
                            "amount": amount,
                            "street": self.fpsm.game_state.street
                        }
                    )
                
                return True
            else:
                print(f"❌ BOT_ACTION_DEBUG: Action execution failed")
                
                # Record the failed decision
                self.decision_history.append({
                    'timestamp': time.time(),
                    'player_index': action_player_index,
                    'player_name': current_player.name,
                    'action': action_type,
                    'amount': amount,
                    'explanation': explanation,
                    'confidence': confidence,
                    'street': self.fpsm.game_state.street,
                    'success': False
                })
                
                # Log failure
                if self.session_logger:
                    self.session_logger.log_system(
                        "ERROR", "BOT_ACTION_FAILED",
                        f"Bot action execution failed",
                        {
                            "player_name": current_player.name,
                            "action": action_type.value if hasattr(action_type, 'value') else str(action_type),
                            "amount": amount,
                            "street": self.fpsm.game_state.street
                        }
                    )
            
                return False
            
        except Exception as e:
            print(f"❌ BOT_ACTION_DEBUG: Error executing action: {e}")
            import traceback
            traceback.print_exc()
            
            # Log error
            if self.session_logger:
                self.session_logger.log_system(
                    "ERROR", "BOT_ACTION_ERROR",
                    f"Error executing bot action: {e}",
                    {"player_index": action_player_index}
                )
            
            return False
    
    def _apply_review_chip_delta(self, current_player: Player, action_type: ActionType, amount: float) -> None:
        """Apply chip deltas to keep pot/current_bet consistent in review mode before delegating.

        This avoids touching FPSM while ensuring subsequent CALL checks see the correct to-call.
        """
        gs = self.fpsm.game_state
        # Skip shim for POST_BLIND actions; FPSM handles blinds correctly
        # But still apply shim for other preflop actions (BET, RAISE, CALL)
        try:
            if hasattr(action_type, 'name'):
                at = action_type.name
            else:
                at = str(action_type)
            
            if at == 'POST_BLIND':
                return  # Let FPSM handle blind posting
        except Exception:
            pass
        # Attach contribution fields if missing
        for p in gs.players:
            if not hasattr(p, "street_contribution"):
                setattr(p, "street_contribution", float(getattr(p, "current_bet", 0.0)))
            if not hasattr(p, "total_contribution"):
                setattr(p, "total_contribution", 0.0)
            if not hasattr(p, "acted_this_round"):
                setattr(p, "acted_this_round", False)

        actor = current_player
        # Compute current to-call based on FPSM fields
        call_amount = max(0.0, float(gs.current_bet) - float(actor.current_bet))

        # Use the action type already determined above

        if at == 'BET':
            # Establish bet line for this round; do not move pot here.
            bet_to = float(amount)
            bet_to = max(0.0, bet_to)
            old_actor_bet = float(actor.current_bet)
            old_current_bet = float(gs.current_bet)
            actor.current_bet = bet_to
            gs.current_bet = max(float(gs.current_bet), bet_to)
            actor.acted_this_round = True
            print(f"🔧 SHIM BET: {actor.name} bet ${bet_to}")
            print(f"   Actor current_bet: ${old_actor_bet} -> ${actor.current_bet}")
            print(f"   Game current_bet: ${old_current_bet} -> ${gs.current_bet}")
        elif at == 'CALL':
            # Do not pre-apply CALL; FPSM will compute and move chips.
            pass
        else:
            # For CHECK/FOLD/RAISE we keep shim minimal; RAISE commonly encoded as BET on new street in data
            if at == 'RAISE':
                # Treat as raise-to total; bring actor.current_bet up and line accordingly
                raise_to = float(amount)
                raise_to = max(0.0, raise_to)
                old_actor_bet = float(actor.current_bet)
                old_current_bet = float(gs.current_bet)
                actor.current_bet = max(float(actor.current_bet), raise_to)
                gs.current_bet = max(float(gs.current_bet), float(actor.current_bet))
                actor.acted_this_round = True
                print(f"🔧 SHIM RAISE: {actor.name} raise to ${raise_to}")
                print(f"   Actor current_bet: ${old_actor_bet} -> ${actor.current_bet}")
                print(f"   Game current_bet: ${old_current_bet} -> ${gs.current_bet}")

    def _apply_review_post_exec_adjustment(self, current_player: Player, action_type: ActionType, amount: float, snap: dict) -> None:
        """After FPSM action succeeds, reconcile pot/current_bet if FPSM didn't move chips in review.

        We compute the expected pay based on the pre-action snapshot and only add the missing delta to pot
        and player fields to avoid double counting.
        """
        gs = self.fpsm.game_state
        street_now = str(getattr(gs, 'street', snap.get('street', 'preflop'))).lower()
        
        # Skip adjustment for POST_BLIND actions (FPSM handles these correctly)
        if hasattr(action_type, 'name'):
            at = action_type.name
        else:
            at = str(action_type)
            
        if at == 'POST_BLIND':
            return
        prev_pot = float(snap.get('pot', 0.0))
        prev_line = float(snap.get('current_bet', 0.0))
        prev_player_bet = float(snap.get('player_current_bet', 0.0))

        # Expected payment by actor for this action
        expected_pay = 0.0
        if at == 'BET':
            expected_pay = float(amount)
        elif at == 'CALL':
            expected_pay = max(0.0, prev_line - prev_player_bet)
        elif at == 'RAISE':
            # Treat amount as raise-to total
            target = float(amount)
            expected_pay = max(0.0, target - prev_player_bet)
        else:
            return

        # Compute what FPSM already added
        actual_delta_pot = float(getattr(gs, 'pot', 0.0)) - prev_pot
        missing = max(0.0, expected_pay - actual_delta_pot)
        
        print(f"🔧 POST-EXEC ADJUSTMENT for {at}:")
        print(f"   Expected payment: ${expected_pay}")
        print(f"   Actual pot delta: ${actual_delta_pot}")
        print(f"   Missing amount: ${missing}")
        print(f"   Pot before: ${prev_pot}, after: ${getattr(gs, 'pot', 0.0)}")
        
        if missing <= 1e-9:
            print(f"   No adjustment needed (missing <= 1e-9)")
            return

        # Ensure contribution fields exist
        for p in gs.players:
            if not hasattr(p, "street_contribution"):
                setattr(p, "street_contribution", float(getattr(p, "current_bet", 0.0)))
            if not hasattr(p, "total_contribution"):
                setattr(p, "total_contribution", 0.0)

        actor = current_player
        # Apply only the missing delta
        missing = min(float(missing), float(getattr(actor, 'stack', 0.0)))
        if missing <= 0.0:
            print(f"   No adjustment applied (missing <= 0)")
            return
            
        old_stack = float(actor.stack)
        old_pot = float(gs.pot)
        old_actor_bet = float(actor.current_bet)
        
        actor.stack = float(actor.stack) - missing
        # Don't double-count current_bet - the shim already set it correctly
        # actor.current_bet = float(actor.current_bet) + missing  # REMOVED: causes double-counting
        actor.street_contribution = float(actor.street_contribution) + missing
        actor.total_contribution = float(actor.total_contribution) + missing
        gs.pot = float(gs.pot) + missing
        # gs.current_bet should already be set correctly by the shim
        
        print(f"   ✅ APPLIED ADJUSTMENT: ${missing}")
        print(f"   Actor stack: ${old_stack} -> ${actor.stack}")
        print(f"   Actor current_bet: ${old_actor_bet} -> ${actor.current_bet}")
        print(f"   Pot: ${old_pot} -> ${gs.pot}")
    
    def get_display_state(self) -> Dict[str, Any]:
        """Get the current display state by delegating to FPSM."""
        try:
            # Get game info from FPSM
            display_state = self.fpsm.get_game_info()
            num_players = len(self.fpsm.game_state.players)
            
            # Add bot session specific information
            display_state.update({
                'session_type': self.session_type,
                'session_active': self.session_active,
                'current_decision_explanation': self.current_decision_explanation,
                'action_player_highlight': [
                    i == getattr(self.fpsm, 'action_player_index', 0) 
                    for i in range(num_players)
                ]
            })
            
            return display_state
            
        except Exception as e:
            print(f"❌ Error getting display state: {e}")
            return {}
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get game information by delegating to FPSM."""
        try:
            return self.fpsm.get_game_info()
        except Exception as e:
            print(f"❌ Error getting game info: {e}")
            return {}
    
    def start_hand(self, existing_players=None):
        """Start a new hand by delegating to FPSM."""
        try:
            return self.fpsm.start_hand(existing_players)
        except Exception as e:
            print(f"❌ Error starting hand: {e}")
            return None
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute an action by delegating to FPSM."""
        try:
            return self.fpsm.execute_action(player, action_type, amount)
        except Exception as e:
            print(f"❌ Error executing action: {e}")
            return False
    
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions for a player by delegating to FPSM."""
        try:
            return self.fpsm.get_valid_actions_for_player(player)
        except Exception as e:
            print(f"❌ Error getting valid actions: {e}")
            return []
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player from FPSM."""
        try:
            action_player_index = getattr(self.fpsm, 'action_player_index', 0)
            if 0 <= action_player_index < len(self.fpsm.game_state.players):
                return self.fpsm.game_state.players[action_player_index]
            return None
        except Exception as e:
            print(f"❌ Error getting action player: {e}")
            return None
    
    def reset_session(self):
        """Reset the session state."""
        self.session_active = False
        self.decision_history.clear()
        self.current_decision_explanation = ""
        
        # Reset FPSM if it has a reset method
        if hasattr(self.fpsm, 'reset'):
            self.fpsm.reset()
    
    def is_session_complete(self) -> bool:
        """Check if the session is complete."""
        return not self.session_active or self.decision_engine.is_session_complete()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            'session_type': self.session_type,
            'session_active': self.session_active,
            'decision_engine_type': self.decision_engine.__class__.__name__,
            'decision_history_count': len(self.decision_history),
            'current_decision_explanation': self.current_decision_explanation
        }


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
            players = self.fpsm.game_state.players
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
                        actual_players = self.fpsm.game_state.players
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
    
    def __init__(self, config: GameConfig, decision_engine, mode: str = "review"):
        """Initialize hands review session with preloaded decision engine."""
        # Create a preloaded deck provider for deterministic replay
        try:
            from ..providers.preloaded_deck import PreloadedDeck
            deck_provider = PreloadedDeck([])
        except ImportError:
            deck_provider = None
        
        # Initialize with deck provider for deterministic replay
        super().__init__(config, decision_engine, "hands_review", mode)
        
        # Override the FPSM's deck provider with our deterministic one
        if deck_provider is not None:
            self.fpsm.deck_provider = deck_provider
        
        self.preloaded_hand_data = None  # Will be set by the UI
    
    def set_sound_manager(self, sound_manager):
        """Set sound manager for audio feedback."""
        self.sound_manager = sound_manager
    
    def set_preloaded_hand_data(self, hand_data: Dict[str, Any]):
        """Set the preloaded hand data including initial player cards."""
        self.preloaded_hand_data = hand_data

    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Override to load preloaded hand data instead of dealing new cards."""
        if self.preloaded_hand_data and "initial_state" in self.preloaded_hand_data:
            # Load players from preloaded hand data
            initial_state = self.preloaded_hand_data["initial_state"]
            players_data = initial_state.get("players", [])

            # Create players with the exact cards from the hand data
            loaded_players: List[Player] = []
        for i, player_data in enumerate(players_data):
            player = Player(
                        name=player_data.get("name", f"Player {i+1}"),
                        stack=player_data.get("stack", 1000.0),
                        position=player_data.get("position", "UTG"),
                        is_human=player_data.get("is_human", False),
                        is_active=player_data.get("is_active", True),
                        cards=player_data.get("cards", []),  # exact hole cards
                        current_bet=player_data.get("current_bet", 0.0),
            )
            loaded_players.append(player)
        
        print(f"🃏 HANDS_REVIEW: Loaded {len(loaded_players)} players with preloaded cards")
        for i, player in enumerate(loaded_players):
            print(f"🃏 HANDS_REVIEW: {player.name} -> {player.cards}")
        
            # CRITICAL: Setup game state manually (skip parent's start_hand)
            self.fpsm.hand_number += 1
            self.fpsm.current_state = PokerState.START_HAND
        
        # Set the preloaded players directly
            self.fpsm.game_state.players = loaded_players

            # Set additional game state from preloaded data
            self.fpsm.game_state.pot = initial_state.get("pot", 0.0)
            self.fpsm.game_state.current_bet = initial_state.get("current_bet", 0.0)
            self.fpsm.game_state.street = initial_state.get("street", "preflop")
            self.fpsm.game_state.board = initial_state.get("board", [])
            if "dealer_position" in initial_state:
                self.fpsm.dealer_position = initial_state["dealer_position"]

            # Set blind positions without dealing
            if self.config.num_players == 2:
                self.fpsm.small_blind_position = self.fpsm.dealer_position
                self.fpsm.big_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
            else:
                self.fpsm.small_blind_position = (self.fpsm.dealer_position + 1) % self.config.num_players
                self.fpsm.big_blind_position = (self.fpsm.small_blind_position + 1) % self.config.num_players

            # Determine correct first-to-act based on street
            street = (self.fpsm.game_state.street or "preflop").lower()
            if street == "preflop":
                if self.config.num_players == 2:
                    self.fpsm.action_player_index = self.fpsm.small_blind_position
                else:
                    self.fpsm.action_player_index = (
                        self.fpsm.big_blind_position + 1
                    ) % self.config.num_players
            else:
                idx = (
                    self.fpsm._find_first_active_after_dealer()
                    if hasattr(self.fpsm, "_find_first_active_after_dealer")
                    else (self.fpsm.dealer_position + 1) % self.config.num_players
                )
                if idx == -1:
                    self.fpsm.current_state = PokerState.END_HAND
                    self.fpsm._emit_display_state_event()
                    return
                self.fpsm.action_player_index = idx

            # === Deterministic deck install for Hands Review ===
            try:
                initial = initial_state

                # 1) Build board sequence in deal order (flop 3, turn 1, river 1)
                flop = (initial.get("flop", []) or [])[:3]
                turn_list = initial.get("turn", []) or []
                river_list = initial.get("river", []) or []

                # If cumulative board provided instead
                if not flop and initial.get("board"):
                    b = initial["board"]
                    flop = b[:3]
                    turn_list = b[3:4]
                    river_list = b[4:5]

                turn = turn_list[-1:] if turn_list else []
                river = river_list[-1:] if river_list else []
                board_seq = [*flop, *turn, *river]

                # 2) Collect used cards (hole cards + board)
                used = set(c.upper().replace("10", "T") for c in board_seq)
                for p in self.fpsm.game_state.players:
                    for c in (getattr(p, "cards", []) or []):
                        used.add(str(c).upper().replace("10", "T"))

                # 3) Construct full deck (standard 52)
                ranks = "23456789TJQKA"
                suits = "CDHS"
                full_deck = [f"{r}{s}" for r in ranks for s in suits]

                # 4) Normalize + install deck: board first (normalized), then remaining
                board_norm = [str(c).upper().replace("10", "T") for c in board_seq]
                remaining = [c for c in full_deck if c not in used]
                deterministic_deck = board_norm + remaining

                # 5) Install into engine (and provider, if present)
                self.fpsm.game_state.deck = deterministic_deck.copy()
                deck_provider = getattr(self.fpsm, "deck_provider", None)
                if deck_provider and hasattr(deck_provider, "replace_deck"):
                    deck_provider.replace_deck(deterministic_deck.copy())

                # 6) Quick sanity on head cards
                if len(board_norm) >= 3:
                    assert self.fpsm.game_state.deck[:3] == board_norm[:3], "Flop mismatch"
                if len(board_norm) >= 4:
                    assert self.fpsm.game_state.deck[3] == board_norm[3], "Turn mismatch"
                if len(board_norm) >= 5:
                    assert self.fpsm.game_state.deck[4] == board_norm[4], "River mismatch"

                print(
                    f"🃏 HANDS_REVIEW: Deck seeded (head 5): {self.fpsm.game_state.deck[:5]}"
                )
            except Exception as e:
                print(f"❌ HANDS_REVIEW: Deck seeding failed: {e}")
            # === End deterministic deck install ===
        
            # Transition to preflop betting phase
            self.fpsm.current_state = PokerState.PREFLOP_BETTING
        
            # Emit initial display state
            self.fpsm._emit_display_state_event()
            
            print(
                f"🃏 HANDS_REVIEW: Hand initialized with preloaded data, street={self.fpsm.game_state.street}"
            )
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
                        actual_players = self.fpsm.game_state.players
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
        num_players = len(self.fpsm.game_state.players)
        display_state["card_visibilities"] = [True] * num_players
        
        # Ensure community cards are visible based on current street
        if "board" in display_state:
            display_state["community_cards_visible"] = True
        
        return display_state

    def load_hand_for_review(self, hand_data: Dict[str, Any]) -> bool:
        """Load hand data for review replay."""
        try:
            print(f"🃏 HANDS_REVIEW: Loading hand for review")
            
            # Set the preloaded hand data
            self.set_preloaded_hand_data(hand_data)
            
            # Start the hand with preloaded data
            self.start_hand()
            
            print(f"🃏 HANDS_REVIEW: Hand loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error loading hand: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step_forward(self) -> bool:
        """Step forward to the next action in the hand replay."""
        try:
            print(f"🃏 HANDS_REVIEW: Stepping forward")
            
            # Check if session is complete
            if self.decision_engine.is_session_complete():
                print(f"🃏 HANDS_REVIEW: Session complete, cannot step forward")
                return False
            
            # Execute the next bot action
            success = self.execute_next_bot_action()
            
            if success:
                print(f"🃏 HANDS_REVIEW: Step forward successful")
            else:
                print(f"🃏 HANDS_REVIEW: Step forward failed")
            
            return success
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error in step_forward: {e}")
            import traceback
            traceback.print_exc()
            return False
