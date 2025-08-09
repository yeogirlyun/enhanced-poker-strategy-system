#!/usr/bin/env python3
"""
Practice Session Poker State Machine

A specialized state machine that inherits from FlexiblePokerStateMachine
and provides practice-specific functionality for learning and skill development.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import random
import time
from .flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, PokerState, Player, GameEvent
)
from .types import ActionType
from .strategy_engine import GTOStrategyEngine


class PracticeSessionPokerStateMachine(FlexiblePokerStateMachine):
    """
    A specialized state machine for practice sessions that provides:
    - Educational feedback and guidance
    - Strategy analysis and suggestions
    - Performance tracking
    - Interactive learning features
    """
    
    def __init__(self, config: GameConfig, strategy_data=None):
        """Initialize the practice session poker state machine."""
        super().__init__(config)
        
        # Practice session specific properties
        self.strategy_data = strategy_data
        self.practice_mode = True
        
        # Initialize strategy engine for bot decision making
        self.strategy_engine = GTOStrategyEngine(self.config.num_players, strategy_data)
        
        # Mark Player 1 as human for practice sessions
        if self.game_state.players:
            self.game_state.players[0].is_human = True
            print(f"🎓 Marked {self.game_state.players[0].name} as human player")
        self.provide_feedback = True
        self.track_performance = True
        
        # Performance tracking
        self.hands_played = 0
        self.correct_decisions = 0
        self.total_decisions = 0
        self.session_stats = {
            'hands_won': 0,
            'hands_lost': 0,
            'total_winnings': 0.0,
            'position_stats': {},
            'hand_strength_stats': {}
        }
        
        print("🎓 PracticeSessionPokerStateMachine initialized - optimized for learning")
    
    def start_hand(self, existing_players: List[Player] = None):
        """Override: Enhanced hand starting for practice sessions."""
        print("🎓 Starting practice hand with educational features")
        super().start_hand(existing_players)
        
        self.hands_played += 1
        
        # Emit practice-specific events
        self._emit_event(GameEvent(
            event_type="practice_hand_started",
            timestamp=datetime.now(),
            data={
                "hand_number": self.hands_played,
                "players": len(self.game_state.players),
                "your_position": self._get_human_player_position()
            }
        ))
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Override: Enhanced action execution with feedback."""
        # Track decision making for human players
        if player.is_human:
            self.total_decisions += 1
            
            # Analyze if this was a good decision (simplified analysis)
            if self._analyze_decision_quality(player, action_type, amount):
                self.correct_decisions += 1
        
        success = super().execute_action(player, action_type, amount)
        
        if success and player.is_human:
            # Provide educational feedback
            feedback = self._generate_action_feedback(player, action_type, amount)
            self._emit_event(GameEvent(
                event_type="practice_feedback",
                timestamp=datetime.now(),
                player_name=player.name,
                action=action_type,
                amount=amount,
                data={"feedback": feedback}
            ))
        
        return success
    
    def transition_to(self, new_state: PokerState):
        """Override: Enhanced state transitions with educational insights."""
        old_state = self.current_state
        super().transition_to(new_state)
        
        # Provide street-specific educational content
        if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            self._provide_street_analysis(new_state)
        
        # Track showdown results for learning
        if new_state == PokerState.SHOWDOWN:
            self._analyze_showdown_for_learning()
        
        print(f"🎓 Practice: State transition {old_state.name} → {new_state.name}")
        
        # Handle bot auto-play after state transitions
        if new_state in [PokerState.PREFLOP_BETTING, PokerState.FLOP_BETTING, 
                        PokerState.TURN_BETTING, PokerState.RIVER_BETTING]:
            self._schedule_bot_actions()
    
    def _get_human_player_position(self) -> Optional[str]:
        """Get the position of the human player."""
        for i, player in enumerate(self.game_state.players):
            if player.is_human:
                # Calculate position relative to dealer
                dealer_pos = self.dealer_position
                position_offset = (i - dealer_pos) % len(self.game_state.players)
                
                if len(self.game_state.players) == 2:
                    return "Small Blind" if position_offset == 1 else "Big Blind"
                elif position_offset == 1:
                    return "Small Blind"
                elif position_offset == 2:
                    return "Big Blind"
                elif position_offset == 3:
                    return "Under the Gun"
                elif position_offset == len(self.game_state.players) - 1:
                    return "Button"
                else:
                    return f"Middle Position {position_offset}"
        return None
    
    def _analyze_decision_quality(self, player: Player, action_type: ActionType, amount: float) -> bool:
        """Analyze if the player's decision was strategically sound."""
        # Simplified decision analysis - in practice, this would use the strategy_data
        # For now, just basic validation
        
        if not self.strategy_data:
            return True  # Can't analyze without strategy data
        
        # Basic analysis: don't fold premium hands preflop
        if (self.current_state == PokerState.PREFLOP_BETTING and 
            action_type == ActionType.FOLD and 
            player.cards):
            
            # Check if player has a premium hand (simplified)
            hand_str = ''.join(player.cards)
            premium_hands = ['AA', 'KK', 'QQ', 'AK']
            
            for premium in premium_hands:
                if (premium[0] in hand_str and premium[1] in hand_str):
                    return False  # Folding a premium hand is not optimal
        
        return True  # Default to accepting the decision
    
    def _generate_action_feedback(self, player: Player, action_type: ActionType, amount: float) -> str:
        """Generate educational feedback for the player's action."""
        position = self._get_human_player_position()
        street = self.game_state.street
        
        feedback = f"You {action_type.value}"
        if amount > 0:
            feedback += f" ${amount}"
        
        feedback += f" from {position} on the {street}."
        
        # Add strategic insights
        if action_type == ActionType.FOLD:
            feedback += " Remember to consider pot odds and your hand strength."
        elif action_type == ActionType.RAISE:
            feedback += " Aggressive play can build pots with strong hands."
        elif action_type == ActionType.CALL:
            feedback += " Calling keeps you in the hand to see more cards."
        
        return feedback
    
    def _provide_street_analysis(self, street_state: PokerState):
        """Provide educational analysis for the current street."""
        street_name = {
            PokerState.DEAL_FLOP: "flop",
            PokerState.DEAL_TURN: "turn", 
            PokerState.DEAL_RIVER: "river"
        }.get(street_state, "unknown")
        
        analysis = f"🎓 {street_name.title()} Analysis: "
        
        if street_state == PokerState.DEAL_FLOP:
            analysis += "Consider how the flop connects with your hand and position."
        elif street_state == PokerState.DEAL_TURN:
            analysis += "The turn card changes pot odds and drawing possibilities."
        elif street_state == PokerState.DEAL_RIVER:
            analysis += "Final betting round - consider your final hand strength."
        
        self._emit_event(GameEvent(
            event_type="practice_analysis",
            timestamp=datetime.now(),
            data={
                "street": street_name,
                "analysis": analysis,
                "board": self.game_state.board.copy()
            }
        ))
    
    def _analyze_showdown_for_learning(self):
        """Analyze the showdown results for educational purposes."""
        human_player = next((p for p in self.game_state.players if p.is_human), None)
        if not human_player:
            return
        
        # Track results
        active_players = [p for p in self.game_state.players if not p.has_folded]
        if len(active_players) > 1:
            # Determine winner (simplified)
            winner = max(active_players, key=lambda p: p.stack)
            
            if winner.is_human:
                self.session_stats['hands_won'] += 1
                self.session_stats['total_winnings'] += self.game_state.pot
            else:
                self.session_stats['hands_lost'] += 1
        
        # Emit learning insights
        self._emit_event(GameEvent(
            event_type="practice_showdown_analysis",
            timestamp=datetime.now(),
            data={
                "your_cards": human_player.cards,
                "board": self.game_state.board,
                "result": "won" if winner and winner.is_human else "lost",
                "lesson": self._generate_showdown_lesson(human_player)
            }
        ))
    
    def _generate_showdown_lesson(self, human_player: Player) -> str:
        """Generate a lesson from the showdown result."""
        lessons = [
            "Hand strength is relative to your opponents and the board.",
            "Position affects your decision-making throughout the hand.",
            "Pot odds help determine if a call is profitable.",
            "Aggressive play builds bigger pots with strong hands.",
            "Reading opponents is as important as your cards."
        ]
        
        # Return a relevant lesson (simplified selection)
        import random
        return random.choice(lessons)
    
    def get_practice_stats(self) -> Dict[str, Any]:
        """Get comprehensive practice session statistics."""
        win_rate = (self.session_stats['hands_won'] / max(self.hands_played, 1)) * 100
        decision_accuracy = (self.correct_decisions / max(self.total_decisions, 1)) * 100
        
        return {
            "hands_played": self.hands_played,
            "hands_won": self.session_stats['hands_won'],
            "hands_lost": self.session_stats['hands_lost'],
            "win_rate": win_rate,
            "total_winnings": self.session_stats['total_winnings'],
            "decisions_made": self.total_decisions,
            "correct_decisions": self.correct_decisions,
            "decision_accuracy": decision_accuracy,
            "session_stats": self.session_stats.copy()
        }
    
    def reset_practice_stats(self):
        """Reset practice session statistics."""
        self.hands_played = 0
        self.correct_decisions = 0
        self.total_decisions = 0
        self.session_stats = {
            'hands_won': 0,
            'hands_lost': 0,
            'total_winnings': 0.0,
            'position_stats': {},
            'hand_strength_stats': {}
        }
        
        print("🎓 Practice session statistics reset")
        
        self._emit_event(GameEvent(
            event_type="practice_stats_reset",
            timestamp=datetime.now(),
            data={"message": "Practice session statistics have been reset"}
        ))
    
    def get_strategy_suggestion(self, player: Player) -> Optional[str]:
        """Get a strategy suggestion for the current situation."""
        if not player.is_human or not self.strategy_data:
            return None
        
        position = self._get_human_player_position()
        street = self.game_state.street
        
        # Simplified strategy suggestion
        suggestion = f"From {position} on the {street}, "
        
        if self.current_state == PokerState.PREFLOP_BETTING:
            suggestion += "consider your hand strength and position for optimal play."
        else:
            suggestion += "evaluate your hand strength against the board texture."
        
        return suggestion
    
    def get_display_state(self) -> dict:
        """Override: Get display state with practice-specific enhancements."""
        # Use parent's get_game_info method which provides display state
        display_state = self.get_game_info()
        
        # Add practice-specific information
        display_state["practice_mode"] = True
        display_state["hands_played"] = self.hands_played
        display_state["session_stats"] = self.get_practice_stats()
        
        # Add expected UI structure fields that the practice session UI expects
        num_players = len(self.game_state.players)
        
        # Card visibilities - in practice mode, human player cards should be visible
        display_state["card_visibilities"] = []
        for i, player in enumerate(self.game_state.players):
            # Human player cards always visible, others based on game state
            is_visible = (player.is_human or 
                         self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND])
            display_state["card_visibilities"].append(is_visible)
        
        # Player highlights - highlight the action player
        display_state["player_highlights"] = []
        for i in range(num_players):
            is_highlighted = (i == self.action_player_index)
            display_state["player_highlights"].append(is_highlighted)
        
        # Layout positions - simple circular layout
        display_state["layout_positions"] = []
        for i in range(num_players):
            # Simple position data
            display_state["layout_positions"].append({"seat": i, "position": i})
        
        # Valid actions for current player
        display_state["valid_actions"] = self._get_valid_actions_for_current_player()
        
        # Chip representations (simplified)
        display_state["chip_representations"] = {}
        for i, player in enumerate(self.game_state.players):
            display_state["chip_representations"][f"player{i}_stack"] = "🟡"  # Simple chip symbol
        display_state["chip_representations"]["pot"] = "💰"
        
        # Current bet info
        if hasattr(self.game_state, 'current_bet'):
            display_state["current_bet"] = self.game_state.current_bet
        else:
            display_state["current_bet"] = 0.0
        
        return display_state
    
    def _schedule_bot_actions(self):
        """Schedule bot actions to auto-play non-human players."""
        # Use after_idle to schedule bot actions so UI can update first
        if getattr(self, '_scheduled_bot_action', False):
            return  # Already scheduled
        
        self._scheduled_bot_action = True
        
        # Schedule bot action after a short delay for realism
        def execute_bot_action():
            self._scheduled_bot_action = False
            self._execute_bot_action_if_needed()
        
        # Use threading timer for delayed execution
        import threading
        timer = threading.Timer(0.8, execute_bot_action)  # 800ms delay for realism
        timer.start()
    
    def _execute_bot_action_if_needed(self):
        """Execute bot action if current player is a bot."""
        if (self.action_player_index >= 0 and 
            self.action_player_index < len(self.game_state.players)):
            
            current_player = self.game_state.players[self.action_player_index]
            
            # Only auto-play for non-human players
            if not current_player.is_human and current_player.is_active and not current_player.has_folded:
                action, amount = self._get_bot_strategy_decision(current_player)
                
                print(f"🤖 Bot {current_player.name} auto-playing: {action.value} ${amount:.2f}")
                
                # Execute the bot's decision
                success = self.execute_action(current_player, action, amount)
                
                if success:
                    # Schedule next bot action if needed (chain bot actions)
                    self._schedule_bot_actions()
                else:
                    print(f"🚫 Bot action failed: {action.value}")
    
    def _get_bot_strategy_decision(self, bot_player: Player) -> tuple[ActionType, float]:
        """Get bot's strategic decision using existing GTO strategy engine."""
        
        # Use the existing GTO strategy engine
        try:
            action, amount = self.strategy_engine.get_gto_bot_action(bot_player, self.game_state)
            print(f"🤖 GTO Strategy Engine: {bot_player.name} -> {action.value} ${amount:.2f}")
            return action, amount
        except Exception as e:
            print(f"🚫 GTO Strategy engine error: {e}")
            # Fallback to simple logic
            return self._get_simple_gto_decision(bot_player)
    
    def _get_simple_gto_decision(self, bot_player: Player) -> tuple[ActionType, float]:
        """Simple fallback decision making when GTO engine fails."""
        
        # Get valid actions first
        valid_actions = self.get_valid_actions_for_player(bot_player)
        current_bet = self.game_state.current_bet
        player_bet = bot_player.current_bet
        call_amount = current_bet - player_bet
        
        # Simple conservative fallback logic
        if call_amount == 0:
            # No bet to call - can check or bet
            if valid_actions.get('check', False):
                return ActionType.CHECK, 0.0
            else:
                return ActionType.FOLD, 0.0
        else:
            # Facing a bet - conservative approach: fold unless small call
            if call_amount <= bot_player.stack * 0.1 and valid_actions.get('call', False):
                return ActionType.CALL, call_amount
            else:
                return ActionType.FOLD, 0.0
    

    
    def _get_valid_actions_for_current_player(self) -> list:
        """Get valid actions for the current action player."""
        if (self.action_player_index >= 0 and 
            self.action_player_index < len(self.game_state.players)):
            
            current_player = self.game_state.players[self.action_player_index]
            
            # Basic valid actions based on game state
            valid_actions = []
            
            if current_player.is_human:
                valid_actions.extend(["fold", "check", "call", "bet", "raise"])
            
            return valid_actions
        
        return []
