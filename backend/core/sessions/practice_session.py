"""
Practice Session Controller

Specialized session for practice play with one human player and bot opponents.
"""

from typing import Dict, Any, List, Optional
from .base_session import BasePokerSession
from ..pure_poker_state_machine import PurePokerStateMachine, GameConfig
from ..poker_types import Player
from ..hand_model import ActionType
from ..providers import StandardDeck, StandardRules, HumanAdvancementController


class PracticeSession(BasePokerSession):
    """
    Session controller for practice poker with human + bot players.
    
    Features:
    - One human player (usually position 0)
    - Bot opponents with configurable difficulty
    - Manual advancement when human is involved
    - Educational feedback and hints
    """
    
    def __init__(self, config: GameConfig, human_player_name: str = "Player1", bot_engines: Dict[str, Any] = None):
        super().__init__(config)
        self.human_player_name = human_player_name
        self.bot_engines = bot_engines or {}
        self.hand_count = 0
        self.human_action_pending = False
        
    def initialize_session(self) -> bool:
        """Initialize practice session with human-aware providers."""
        try:
            # Create providers for practice play
            deck_provider = StandardDeck(shuffle=True)
            rules_provider = StandardRules()
            advancement_controller = HumanAdvancementController(
                human_player_names=[self.human_player_name]
            )
            
            # Create pure FPSM with injected dependencies
            self.fpsm = PurePokerStateMachine(
                config=self.config,
                deck_provider=deck_provider,
                rules_provider=rules_provider,
                advancement_controller=advancement_controller
            )
            
            self.session_active = True
            print(f"👤 PRACTICE_SESSION: Initialized with human player '{self.human_player_name}'")
            return True
            
        except Exception as e:
            print(f"❌ PRACTICE_SESSION: Failed to initialize: {e}")
            return False
    
    def start_hand(self, **kwargs) -> bool:
        """Start a new practice hand."""
        try:
            if not self.fpsm:
                return False
            
            self.hand_count += 1
            
            # Create players (human + bots)
            players = []
            for i in range(self.config.num_players):
                is_human = (i == 0)  # First player is human
                player_name = self.human_player_name if is_human else f"Bot_{i}"
                
                player = Player(
                    name=player_name,
                    stack=self.config.starting_stack,
                    position="",
                    is_human=is_human,
                    is_active=True,
                    cards=[],
                )
                players.append(player)
            
            # Start hand
            self.fpsm.start_hand(existing_players=players)
            
            # Check if human needs to act first
            action_player = self.get_action_player()
            self.human_action_pending = (action_player and action_player.is_human)
            
            print(f"👤 PRACTICE_SESSION: Hand {self.hand_count} started")
            if self.human_action_pending:
                print(f"👤 PRACTICE_SESSION: Waiting for human action from {action_player.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ PRACTICE_SESSION: Failed to start hand: {e}")
            return False
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute action and handle human/bot flow."""
        if not self.fpsm:
            return False
        
        # Execute through pure FPSM
        success = self.fpsm.execute_action(player, action_type, amount)
        
        if success:
            print(f"👤 PRACTICE_SESSION: {player.name} {'(Human)' if player.is_human else '(Bot)'} {action_type.value} ${amount}")
            
            # Update human action pending status
            next_action_player = self.get_action_player()
            self.human_action_pending = (next_action_player and next_action_player.is_human)
            
            # If next player is a bot, execute their action automatically
            if next_action_player and not next_action_player.is_human:
                self._execute_bot_action_after_delay()
        
        return success
    
    def _execute_bot_action_after_delay(self):
        """Execute bot action after a short delay for realism."""
        # In a real implementation, this might use a timer
        # For now, execute immediately
        self.execute_next_bot_action()
    
    def execute_next_bot_action(self) -> bool:
        """Execute the next bot action automatically."""
        try:
            action_player = self.get_action_player()
            if not action_player or action_player.is_human:
                return False
            
            # Get decision from bot engine
            bot_engine = self.bot_engines.get(action_player.name)
            if not bot_engine:
                decision = self._get_default_bot_decision(action_player)
            else:
                game_state = self.fpsm.get_game_info()
                decision = bot_engine.get_decision(
                    self.fpsm.action_player_index,
                    game_state
                )
            
            if not decision or 'action' not in decision:
                return False
            
            # Execute the bot decision
            action_type = decision['action']
            amount = decision.get('amount', 0.0)
            
            return self.execute_action(action_player, action_type, amount)
            
        except Exception as e:
            print(f"❌ PRACTICE_SESSION: Error executing bot action: {e}")
            return False
    
    def _get_default_bot_decision(self, player: Player) -> Dict[str, Any]:
        """Get a default bot decision for practice opponents."""
        valid_actions = self.get_valid_actions_for_player(player)
        
        if not valid_actions:
            return {"action": ActionType.FOLD, "amount": 0}
        
        # Simple practice bot strategy
        import random
        
        # Mostly passive for practice
        check_actions = [a for a in valid_actions if a["action"] == "check"]
        if check_actions and random.random() < 0.7:
            return {"action": ActionType.CHECK, "amount": 0}
        
        call_actions = [a for a in valid_actions if a["action"] == "call"]
        if call_actions and random.random() < 0.8:
            return {"action": ActionType.CALL, "amount": call_actions[0]["amount"]}
        
        # Occasionally fold to give human wins
        if random.random() < 0.3:
            return {"action": ActionType.FOLD, "amount": 0}
        
        # Rarely bet
        bet_actions = [a for a in valid_actions if a["action"] == "bet"]
        if bet_actions and random.random() < 0.2:
            return {"action": ActionType.BET, "amount": bet_actions[0]["amount"]}
        
        return {"action": ActionType.FOLD, "amount": 0}
    
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions with educational context."""
        if not self.fpsm:
            return []
        
        valid_actions = []
        
        # Fold (always available unless already folded)
        if not player.has_folded:
            valid_actions.append({
                "action": "fold",
                "amount": 0,
                "description": "Give up your hand"
            })
        
        # Check (if no bet to call)
        if player.current_bet == self.fpsm.game_state.current_bet:
            valid_actions.append({
                "action": "check", 
                "amount": 0,
                "description": "Pass the action without betting"
            })
        
        # Call (if there's a bet to call)
        call_amount = max(0, self.fpsm.game_state.current_bet - player.current_bet)
        if call_amount > 0 and call_amount <= player.stack:
            valid_actions.append({
                "action": "call",
                "amount": call_amount,
                "description": f"Match the current bet of ${call_amount}"
            })
        
        # Bet/Raise options
        min_bet = max(self.config.big_blind, self.fpsm.game_state.current_bet * 2)
        if player.stack >= min_bet:
            valid_actions.append({
                "action": "bet",
                "amount": min_bet,
                "description": f"Bet ${min_bet} (minimum)"
            })
            
            # Pot-sized bet
            pot_bet = min(self.fpsm.game_state.pot, player.stack)
            if pot_bet >= min_bet:
                valid_actions.append({
                    "action": "bet",
                    "amount": pot_bet,
                    "description": f"Bet ${pot_bet} (pot-sized)"
                })
            
            # All-in
            if player.stack > min_bet:
                valid_actions.append({
                    "action": "bet",
                    "amount": player.stack,
                    "description": f"All-in ${player.stack}"
                })
        
        return valid_actions
    
    def get_human_player(self) -> Optional[Player]:
        """Get the human player."""
        if not self.fpsm:
            return None
        
        for player in self.fpsm.game_state.players:
            if player.is_human:
                return player
        
        return None
    
    def is_human_action_required(self) -> bool:
        """Check if human action is required."""
        return self.human_action_pending
    
    def get_educational_hint(self) -> str:
        """Get an educational hint for the current situation."""
        if not self.fpsm:
            return ""
        
        human_player = self.get_human_player()
        if not human_player:
            return ""
        
        # Simple hints based on game state
        pot_odds = self.fpsm.game_state.pot / max(1, self.fpsm.game_state.current_bet - human_player.current_bet)
        
        if pot_odds > 3:
            return "💡 Good pot odds - consider calling with marginal hands"
        elif self.fpsm.game_state.street == "preflop":
            return "💡 Preflop: Play tight, focus on premium hands"
        elif len(self.fpsm.game_state.board) >= 3:
            return "💡 Consider your hand strength relative to the board"
        
        return "💡 Think about your position and opponents' actions"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get practice session statistics."""
        human_player = self.get_human_player()
        
        return {
            "hands_played": self.hand_count,
            "session_type": "Practice",
            "human_player": self.human_player_name,
            "human_stack": human_player.stack if human_player else 0,
            "starting_stack": self.config.starting_stack,
        }
