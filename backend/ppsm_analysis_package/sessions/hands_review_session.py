"""
Hands Review Session Controller

Specialized session for reviewing historical hands with deterministic replay.
"""

from typing import Dict, Any, List, Optional
from .base_session import BasePokerSession
from ..pure_poker_state_machine import PurePokerStateMachine, GameConfig
from ..poker_types import Player
from ..hand_model import ActionType
from ..providers import DeterministicDeck, HandsReviewRules, HandsReviewAdvancementController
from ..hand_model_decision_engine import HandModelDecisionEngine


class HandsReviewSession(BasePokerSession):
    """
    Session controller for hands review with deterministic replay.
    
    Features:
    - Deterministic deck with known board/hole cards
    - Auto-advancement through all streets
    - Integration with HandModelDecisionEngine for action replay
    - No human interaction required
    """
    
    def __init__(self, config: GameConfig, decision_engine: HandModelDecisionEngine = None):
        super().__init__(config)
        self.decision_engine = decision_engine
        self.preloaded_hand_data: Optional[Dict[str, Any]] = None
        
    def initialize_session(self) -> bool:
        """Initialize hands review session with deterministic providers."""
        try:
            # Create providers for deterministic replay
            deck_provider = DeterministicDeck()
            rules_provider = HandsReviewRules()
            advancement_controller = HandsReviewAdvancementController()
            
            # Create pure FPSM with injected dependencies
            self.fpsm = PurePokerStateMachine(
                config=self.config,
                deck_provider=deck_provider,
                rules_provider=rules_provider,
                advancement_controller=advancement_controller
            )
            
            # Link decision engine to FPSM if provided
            if self.decision_engine:
                self.decision_engine.fpsm = self.fpsm
            
            self.session_active = True
            print(f"🔧 HANDS_REVIEW: Session initialized with deterministic providers")
            return True
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Failed to initialize session: {e}")
            return False
    
    def load_hand_for_review(self, hand_data: Dict[str, Any]) -> bool:
        """
        Load a specific hand for review.
        
        Args:
            hand_data: Hand data with initial_state containing players, board, etc.
        """
        try:
            if not self.fpsm:
                print(f"❌ HANDS_REVIEW: Session not initialized")
                return False
            
            self.preloaded_hand_data = hand_data
            initial_state = hand_data.get('initial_state', {})
            
            # Extract board cards and hole cards for deterministic deck
            board_cards = initial_state.get('board', [])
            
            # Extract hole cards from players
            hole_cards = {}
            players_data = initial_state.get('players', [])
            for player_data in players_data:
                player_name = player_data.get('name', '')
                player_cards = player_data.get('cards', [])
                if player_name and player_cards:
                    hole_cards[player_name] = player_cards
            
            # Update deck provider with known cards
            if hasattr(self.fpsm.deck_provider, 'set_board_cards'):
                self.fpsm.deck_provider.set_board_cards(board_cards)
            if hasattr(self.fpsm.deck_provider, 'set_hole_cards'):
                self.fpsm.deck_provider.set_hole_cards(hole_cards)
            
            print(f"🃏 HANDS_REVIEW: Loaded hand with {len(players_data)} players, board: {board_cards}")
            return True
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Failed to load hand: {e}")
            return False
    
    def start_hand(self, **kwargs) -> bool:
        """Start hand with preloaded data."""
        try:
            if not self.fpsm or not self.preloaded_hand_data:
                print(f"❌ HANDS_REVIEW: No hand data loaded")
                return False
            
            initial_state = self.preloaded_hand_data['initial_state']
            players_data = initial_state.get('players', [])
            
            # Create players with exact data from hand
            loaded_players = []
            for i, player_data in enumerate(players_data):
                player = Player(
                    name=player_data.get('name', f'Player{i+1}'),
                    stack=player_data.get('stack', 1000.0),
                    position=player_data.get('position', 'UTG'),
                    is_human=False,  # All players are bots in review mode
                    is_active=player_data.get('is_active', True),
                    cards=player_data.get('cards', []),
                    current_bet=player_data.get('current_bet', 0.0),
                )
                loaded_players.append(player)
            
            # Start hand with preloaded players
            self.fpsm.start_hand(existing_players=loaded_players)
            
            # Set additional game state from preloaded data
            self.fpsm.game_state.pot = initial_state.get('pot', 0.0)
            self.fpsm.game_state.current_bet = initial_state.get('current_bet', 0.0)
            self.fpsm.game_state.street = initial_state.get('street', 'preflop')
            self.fpsm.game_state.board = initial_state.get('board', [])
            
            # Set positions
            if 'dealer_position' in initial_state:
                self.fpsm.dealer_position = initial_state['dealer_position']
            
            print(f"🃏 HANDS_REVIEW: Hand started with preloaded state")
            return True
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Failed to start hand: {e}")
            return False
    
    def execute_action(self, player: Player, action_type: ActionType, amount: float = 0.0) -> bool:
        """Execute action through pure FPSM."""
        if not self.fpsm:
            return False
        
        return self.fpsm.execute_action(player, action_type, amount)
    
    def get_valid_actions_for_player(self, player: Player) -> List[Dict[str, Any]]:
        """Get valid actions (simplified for review mode)."""
        if not self.fpsm:
            return []
        
        # In review mode, actions are determined by the decision engine
        # This is mainly for compatibility
        return [
            {"action": "fold", "amount": 0},
            {"action": "check", "amount": 0}, 
            {"action": "call", "amount": max(0, self.fpsm.game_state.current_bet - player.current_bet)},
            {"action": "bet", "amount": player.stack},
        ]
    
    def step_forward(self) -> bool:
        """Step forward to the next action in the replay."""
        try:
            if not self.decision_engine or not self.fpsm:
                return False
            
            # Get current action player
            action_player = self.get_action_player()
            if not action_player:
                print(f"🛡️ HANDS_REVIEW: No action player available")
                return False
            
            # Get decision from engine
            game_state = self.fpsm.get_game_info()
            decision = self.decision_engine.get_decision(
                self.fpsm.action_player_index, 
                game_state
            )
            
            if not decision or 'action' not in decision:
                print(f"🛡️ HANDS_REVIEW: No valid decision available")
                return False
            
            # Execute the action
            action_type = decision['action']
            amount = decision.get('amount', 0.0)
            
            success = self.execute_action(action_player, action_type, amount)
            if success:
                print(f"🎯 HANDS_REVIEW: Executed {action_type.value} ${amount} for {action_player.name}")
            
            return success
            
        except Exception as e:
            print(f"❌ HANDS_REVIEW: Error stepping forward: {e}")
            return False
    
    def is_replay_complete(self) -> bool:
        """Check if the hand replay is complete."""
        if not self.decision_engine:
            return True
        
        return self.decision_engine.is_session_complete()
    
    def set_preloaded_hand_data(self, hand_data: Dict[str, Any]):
        """Set preloaded hand data for the session."""
        self.preloaded_hand_data = hand_data
