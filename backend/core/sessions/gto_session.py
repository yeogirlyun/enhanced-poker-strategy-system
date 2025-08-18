"""
GTO Session Controller

Specialized session for GTO (Game Theory Optimal) poker with all bot players.
"""

from typing import Dict, Any, List, Optional
from .base_session import BasePokerSession
from ..pure_poker_state_machine import PurePokerStateMachine, GameConfig
from ..poker_types import Player
from ..hand_model import ActionType
from ..providers import GTODeck, StandardRules, AutoAdvancementController


class GTOSession(BasePokerSession):
    """
    Session controller for GTO poker with all bot players.
    
    Features:
    - All players are bots (no human interaction)
    - Auto-advancement through all game states
    - Seeded randomness for reproducible results
    - Integration with GTO decision engines
    """
    
    def __init__(self, config: GameConfig, decision_engines: Dict[str, Any] = None, seed: int = None):
        super().__init__(config)
        self.decision_engines = decision_engines or {}
        self.seed = seed
        self.hand_count = 0
        
    def initialize_session(self) -> bool:
        """Initialize GTO session with auto-advance providers."""
        try:
            # Create providers for GTO play
            deck_provider = GTODeck(seed=self.seed)
            rules_provider = StandardRules()
            advancement_controller = AutoAdvancementController()
            
            # Create pure FPSM with injected dependencies
            self.fpsm = PurePokerStateMachine(
                config=self.config,
                deck_provider=deck_provider,
                rules_provider=rules_provider,
                advancement_controller=advancement_controller
            )
            
            self.session_active = True
            print(f"🤖 GTO_SESSION: Initialized with {self.config.num_players} bot players")
            if self.seed is not None:
                print(f"🤖 GTO_SESSION: Using seed {self.seed} for reproducible results")
            return True
            
        except Exception as e:
            print(f"❌ GTO_SESSION: Failed to initialize: {e}")
            return False
    
    def start_hand(self, **kwargs) -> bool:
        """Start a new GTO hand."""
        try:
            if not self.fpsm:
                return False
            
            self.hand_count += 1
            
            # Create bot players
            bot_players = []
            for i in range(self.config.num_players):
                player = Player(
                    name=f"GTO_Bot_{i+1}",
                    stack=self.config.starting_stack,
                    position="",
                    is_human=False,  # All bots
                    is_active=True,
                    cards=[],
                )
                bot_players.append(player)
            
            # Start hand with bot players
            self.fpsm.start_hand(existing_players=bot_players)
            
            print(f"🤖 GTO_SESSION: Hand {self.hand_count} started with {len(bot_players)} bots")
            return True
            
        except Exception as e:
            print(f"❌ GTO_SESSION: Failed to start hand: {e}")
            return False
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute action through pure FPSM."""
        if not self.fpsm:
            return False
        
        print(f"🤖 GTO_SESSION: {player.name} {action_type.value} ${amount}")
        return self.fpsm.execute_action(player, action_type, amount)
    
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions for a bot player."""
        if not self.fpsm:
            return []
        
        valid_actions = []
        
        # Fold is always valid (except when already folded)
        if not player.has_folded:
            valid_actions.append({"action": "fold", "amount": 0})
        
        # Check if player can check
        if player.current_bet == self.fpsm.game_state.current_bet:
            valid_actions.append({"action": "check", "amount": 0})
        
        # Call if there's a bet to call
        call_amount = max(0, self.fpsm.game_state.current_bet - player.current_bet)
        if call_amount > 0 and call_amount <= player.stack:
            valid_actions.append({"action": "call", "amount": call_amount})
        
        # Bet/Raise options
        min_bet = max(self.config.big_blind, self.fpsm.game_state.current_bet * 2)
        if player.stack >= min_bet:
            valid_actions.append({"action": "bet", "amount": min_bet})
            valid_actions.append({"action": "bet", "amount": player.stack})  # All-in
        
        return valid_actions
    
    def execute_next_bot_action(self) -> bool:
        """Execute the next bot action automatically."""
        try:
            action_player = self.get_action_player()
            if not action_player:
                return False
            
            # Get decision from appropriate decision engine
            decision_engine = self.decision_engines.get(action_player.name)
            if not decision_engine:
                # Use default GTO strategy (simplified)
                decision = self._get_default_gto_decision(action_player)
            else:
                game_state = self.fpsm.get_game_info()
                decision = decision_engine.get_decision(
                    self.fpsm.action_player_index,
                    game_state
                )
            
            if not decision or 'action' not in decision:
                return False
            
            # Execute the decision
            action_type = decision['action']
            amount = decision.get('amount', 0.0)
            
            return self.execute_action(action_player, action_type, amount)
            
        except Exception as e:
            print(f"❌ GTO_SESSION: Error executing bot action: {e}")
            return False
    
    def _get_default_gto_decision(self, player: Player) -> Dict[str, Any]:
        """Get a default GTO decision (simplified strategy)."""
        valid_actions = self.get_valid_actions_for_player(player)
        
        if not valid_actions:
            return {"action": ActionType.FOLD, "amount": 0}
        
        # Simple strategy: mostly call/check, occasionally bet
        import random
        
        # Check if we can check
        check_actions = [a for a in valid_actions if a["action"] == "check"]
        if check_actions and random.random() < 0.6:
            return {"action": ActionType.CHECK, "amount": 0}
        
        # Check if we can call
        call_actions = [a for a in valid_actions if a["action"] == "call"]
        if call_actions and random.random() < 0.7:
            return {"action": ActionType.CALL, "amount": call_actions[0]["amount"]}
        
        # Sometimes bet
        bet_actions = [a for a in valid_actions if a["action"] == "bet"]
        if bet_actions and random.random() < 0.3:
            return {"action": ActionType.BET, "amount": bet_actions[0]["amount"]}
        
        # Default to fold
        return {"action": ActionType.FOLD, "amount": 0}
    
    def run_hand_automatically(self) -> bool:
        """Run an entire hand automatically with bot decisions."""
        try:
            if not self.start_hand():
                return False
            
            max_actions = 100  # Safety limit
            actions_taken = 0
            
            while (not self.is_hand_complete() and 
                   actions_taken < max_actions and 
                   self.session_active):
                
                if not self.execute_next_bot_action():
                    break
                
                actions_taken += 1
            
            print(f"🤖 GTO_SESSION: Hand completed after {actions_taken} actions")
            return True
            
        except Exception as e:
            print(f"❌ GTO_SESSION: Error running automatic hand: {e}")
            return False
    
    def is_hand_complete(self) -> bool:
        """Check if the current hand is complete."""
        if not self.fpsm:
            return True
        
        from ..poker_types import PokerState
        return self.fpsm.current_state == PokerState.END_HAND
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get GTO session statistics."""
        return {
            "hands_played": self.hand_count,
            "session_type": "GTO",
            "seed": self.seed,
            "players": self.config.num_players,
        }
