"""
Live Session Controller

Specialized session for live poker with mixed human and bot players.
"""

from typing import Dict, Any, List, Optional, Set
from .base_session import BasePokerSession
from ..pure_poker_state_machine import PurePokerStateMachine, GameConfig
from ..poker_types import Player
from ..hand_model import ActionType
from ..providers import StandardDeck, StandardRules, LiveAdvancementController


class LiveSession(BasePokerSession):
    """
    Session controller for live poker with mixed human/bot players.
    
    Features:
    - Configurable mix of human and bot players
    - Smart advancement based on player types
    - Real-time action handling
    - Spectator support
    - Chat and social features
    """
    
    def __init__(
        self, 
        config: GameConfig, 
        human_player_names: List[str] = None,
        bot_engines: Dict[str, Any] = None,
        allow_spectators: bool = True
    ):
        super().__init__(config)
        self.human_player_names: Set[str] = set(human_player_names or [])
        self.bot_engines = bot_engines or {}
        self.allow_spectators = allow_spectators
        self.spectators: Set[str] = set()
        self.hand_count = 0
        self.action_timeout_seconds = 30  # Default action timeout
        
    def initialize_session(self) -> bool:
        """Initialize live session with mixed player support."""
        try:
            # Create providers for live play
            deck_provider = StandardDeck(shuffle=True)
            rules_provider = StandardRules()
            advancement_controller = LiveAdvancementController(
                human_player_names=list(self.human_player_names)
            )
            
            # Create pure FPSM with injected dependencies
            self.fpsm = PurePokerStateMachine(
                config=self.config,
                deck_provider=deck_provider,
                rules_provider=rules_provider,
                advancement_controller=advancement_controller
            )
            
            self.session_active = True
            print(f"🎮 LIVE_SESSION: Initialized with {len(self.human_player_names)} humans, {self.config.num_players - len(self.human_player_names)} bots")
            return True
            
        except Exception as e:
            print(f"❌ LIVE_SESSION: Failed to initialize: {e}")
            return False
    
    def start_hand(self, **kwargs) -> bool:
        """Start a new live hand."""
        try:
            if not self.fpsm:
                return False
            
            self.hand_count += 1
            
            # Create mixed players
            players = []
            human_names = list(self.human_player_names)
            
            for i in range(self.config.num_players):
                if i < len(human_names):
                    # Human player
                    player = Player(
                        name=human_names[i],
                        stack=self.config.starting_stack,
                        position="",
                        is_human=True,
                        is_active=True,
                        cards=[],
                    )
                else:
                    # Bot player
                    player = Player(
                        name=f"Bot_{i - len(human_names) + 1}",
                        stack=self.config.starting_stack,
                        position="",
                        is_human=False,
                        is_active=True,
                        cards=[],
                    )
                
                players.append(player)
            
            # Start hand
            self.fpsm.start_hand(existing_players=players)
            
            print(f"🎮 LIVE_SESSION: Hand {self.hand_count} started")
            self._log_action_required()
            
            return True
            
        except Exception as e:
            print(f"❌ LIVE_SESSION: Failed to start hand: {e}")
            return False
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute action with live session handling."""
        if not self.fpsm:
            return False
        
        # Validate that it's this player's turn
        action_player = self.get_action_player()
        if not action_player or action_player.name != player.name:
            print(f"❌ LIVE_SESSION: Not {player.name}'s turn to act")
            return False
        
        # Execute through pure FPSM
        success = self.fpsm.execute_action(player, action_type, amount)
        
        if success:
            player_type = "Human" if player.is_human else "Bot"
            print(f"🎮 LIVE_SESSION: {player.name} ({player_type}) {action_type.value} ${amount}")
            
            # Broadcast action to spectators
            self._broadcast_action(player, action_type, amount)
            
            # Handle next action
            self._handle_next_action()
        
        return success
    
    def _handle_next_action(self):
        """Handle the next action in the sequence."""
        action_player = self.get_action_player()
        
        if not action_player:
            return
        
        if action_player.is_human:
            # Human player - wait for input
            print(f"🎮 LIVE_SESSION: Waiting for {action_player.name} to act")
            self._start_action_timer(action_player)
        else:
            # Bot player - execute automatically
            self._execute_bot_action_after_delay(action_player)
    
    def _execute_bot_action_after_delay(self, bot_player: Player):
        """Execute bot action after a realistic delay."""
        # In a real implementation, this would use a timer
        # For now, execute with a small delay simulation
        print(f"🤖 LIVE_SESSION: {bot_player.name} is thinking...")
        self.execute_next_bot_action()
    
    def execute_next_bot_action(self) -> bool:
        """Execute the next bot action."""
        try:
            action_player = self.get_action_player()
            if not action_player or action_player.is_human:
                return False
            
            # Get decision from bot engine
            bot_engine = self.bot_engines.get(action_player.name)
            if not bot_engine:
                decision = self._get_default_live_bot_decision(action_player)
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
            print(f"❌ LIVE_SESSION: Error executing bot action: {e}")
            return False
    
    def _get_default_live_bot_decision(self, player: Player) -> Dict[str, Any]:
        """Get a default bot decision for live play."""
        valid_actions = self.get_valid_actions_for_player(player)
        
        if not valid_actions:
            return {"action": ActionType.FOLD, "amount": 0}
        
        # More aggressive strategy for live play
        import random
        
        # Sometimes bet aggressively
        bet_actions = [a for a in valid_actions if a["action"] == "bet"]
        if bet_actions and random.random() < 0.4:
            return {"action": ActionType.BET, "amount": bet_actions[0]["amount"]}
        
        # Check when possible
        check_actions = [a for a in valid_actions if a["action"] == "check"]
        if check_actions and random.random() < 0.5:
            return {"action": ActionType.CHECK, "amount": 0}
        
        # Call moderately
        call_actions = [a for a in valid_actions if a["action"] == "call"]
        if call_actions and random.random() < 0.6:
            return {"action": ActionType.CALL, "amount": call_actions[0]["amount"]}
        
        # Fold as backup
        return {"action": ActionType.FOLD, "amount": 0}
    
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions for live play."""
        if not self.fpsm:
            return []
        
        valid_actions = []
        
        # Standard actions
        if not player.has_folded:
            valid_actions.append({"action": "fold", "amount": 0})
        
        if player.current_bet == self.fpsm.game_state.current_bet:
            valid_actions.append({"action": "check", "amount": 0})
        
        call_amount = max(0, self.fpsm.game_state.current_bet - player.current_bet)
        if call_amount > 0 and call_amount <= player.stack:
            valid_actions.append({"action": "call", "amount": call_amount})
        
        # Betting options
        min_bet = max(self.config.big_blind, self.fpsm.game_state.current_bet * 2)
        if player.stack >= min_bet:
            # Minimum bet
            valid_actions.append({"action": "bet", "amount": min_bet})
            
            # Half pot
            half_pot = min(self.fpsm.game_state.pot // 2, player.stack)
            if half_pot >= min_bet:
                valid_actions.append({"action": "bet", "amount": half_pot})
            
            # Pot bet
            pot_bet = min(self.fpsm.game_state.pot, player.stack)
            if pot_bet >= min_bet:
                valid_actions.append({"action": "bet", "amount": pot_bet})
            
            # All-in
            if player.stack > min_bet:
                valid_actions.append({"action": "bet", "amount": player.stack})
        
        return valid_actions
    
    def add_spectator(self, spectator_name: str) -> bool:
        """Add a spectator to the session."""
        if not self.allow_spectators:
            return False
        
        self.spectators.add(spectator_name)
        print(f"👁️ LIVE_SESSION: {spectator_name} joined as spectator")
        return True
    
    def remove_spectator(self, spectator_name: str) -> bool:
        """Remove a spectator from the session."""
        if spectator_name in self.spectators:
            self.spectators.remove(spectator_name)
            print(f"👁️ LIVE_SESSION: {spectator_name} left as spectator")
            return True
        return False
    
    def _broadcast_action(self, player: Player, action_type: ActionType, amount: float):
        """Broadcast action to all spectators."""
        if self.spectators:
            action_msg = f"{player.name} {action_type.value} ${amount}"
            print(f"📢 BROADCAST: {action_msg} (to {len(self.spectators)} spectators)")
    
    def _start_action_timer(self, player: Player):
        """Start action timer for human player."""
        # In a real implementation, this would start a countdown timer
        print(f"⏰ LIVE_SESSION: {player.name} has {self.action_timeout_seconds} seconds to act")
    
    def _log_action_required(self):
        """Log which player needs to act."""
        action_player = self.get_action_player()
        if action_player:
            player_type = "Human" if action_player.is_human else "Bot"
            print(f"🎮 LIVE_SESSION: Action required from {action_player.name} ({player_type})")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get live session statistics."""
        human_players = [p for p in self.fpsm.game_state.players if p.is_human] if self.fpsm else []
        bot_players = [p for p in self.fpsm.game_state.players if not p.is_human] if self.fpsm else []
        
        return {
            "hands_played": self.hand_count,
            "session_type": "Live",
            "human_players": len(human_players),
            "bot_players": len(bot_players),
            "spectators": len(self.spectators),
            "human_stacks": {p.name: p.stack for p in human_players},
            "bot_stacks": {p.name: p.stack for p in bot_players},
        }
    
    def is_human_action_required(self) -> bool:
        """Check if a human player needs to act."""
        action_player = self.get_action_player()
        return action_player is not None and action_player.is_human
