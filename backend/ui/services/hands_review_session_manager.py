#!/usr/bin/env python3
"""
HandsReviewSessionManager - Manages hands review session logic per architecture guidelines.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


try:
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from core.hand_model import Hand, Street
    from core.hand_model_decision_engine import HandModelDecisionEngine
    from core.session_logger import get_session_logger
    from core.poker_types import Player
except ImportError:
    # Fallback for when running from different directory
    from ...core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from ...core.hand_model import Hand, Street
    from ...core.hand_model_decision_engine import HandModelDecisionEngine
    from ...core.session_logger import get_session_logger
    from ...core.poker_types import Player


@dataclass
class HandsReviewState:
    """Immutable state for hands review session."""
    current_hand: Optional[Hand] = None
    current_action_index: int = 0
    total_actions: int = 0
    is_playing: bool = False
    playback_speed: float = 1.0
    street: str = "PREFLOP"
    board: List[str] = None
    seats: List[Dict[str, Any]] = None
    pot: Dict[str, Any] = None
    dealer: Dict[str, Any] = None
    action: Dict[str, Any] = None
    effects: List[Dict[str, Any]] = None
    table: Dict[str, Any] = None
    animation: Dict[str, Any] = None


class HandsReviewSessionManager:
    """Manages hands review session logic per architecture guidelines."""
    
    def __init__(self, store, ppsm: PurePokerStateMachine, game_director, effect_bus, event_bus):
        self.store = store
        self.ppsm = ppsm
        self.game_director = game_director
        self.effect_bus = effect_bus
        self.event_bus = event_bus
        self.session_logger = get_session_logger()
        
        # Session state
        self.current_hand: Optional[Hand] = None
        self.current_action_index: int = 0
        self.total_actions: int = 0
        self.is_playing: bool = False
        self.playback_speed: float = 1.0
        
        # Decision engine for hand replay
        self.decision_engine: Optional[HandModelDecisionEngine] = None
        
        print("🎯 HandsReviewSessionManager: Initialized per architecture guidelines")
    
    def load_hand(self, hand_data: Dict[str, Any]) -> HandsReviewState:
        """Load a hand for review - business logic only."""
        try:
            # Create Hand object from data
            self.current_hand = Hand.from_dict(hand_data)
            
            # Initialize PPSM with hand data
            self._initialize_ppsm_for_hand()
            
            # Create decision engine for replay
            self.decision_engine = HandModelDecisionEngine(self.current_hand)
            
            # Count total actions across all streets
            self.total_actions = sum(len(street_state.actions) for street_state in self.current_hand.streets.values())
            
            # Reset to beginning
            self.current_action_index = 0
            self.is_playing = False
            
            # Create initial state
            initial_state = self._create_table_state()
            
            # Update store (not UI directly)
            self.store.dispatch({
                "type": "HANDS_REVIEW_LOADED",
                "hand_id": self.current_hand.metadata.hand_id,
                "total_actions": self.total_actions,
                "state": initial_state
            })
            
            print(f"🎯 HandsReviewSessionManager: Loaded hand {self.current_hand.metadata.hand_id} with {self.total_actions} actions")
            
            return HandsReviewState(
                current_hand=self.current_hand,
                current_action_index=self.current_action_index,
                total_actions=self.total_actions,
                is_playing=self.is_playing,
                playback_speed=self.playback_speed,
                **initial_state
            )
            
        except Exception as e:
            print(f"❌ HandsReviewSessionManager: Error loading hand: {e}")
            raise
    
    def execute_action(self) -> HandsReviewState:
        """Execute next action through PPSM - business logic only."""
        try:
            if not self.current_hand:
                raise ValueError("No hand loaded")
            
            # Get action from hand data (need to find which street it's in)
            if self.current_action_index >= self.total_actions:
                print("🎯 HandsReviewSessionManager: All actions completed")
                return self._get_current_state()
            
            # Find the action across all streets
            action = self._get_action_by_index(self.current_action_index)
            
            # Convert action to PPSM format
            player = self._get_player_by_uid(action.actor_uid)
            action_type = action.action
            to_amount = action.to_amount if action.to_amount is not None else action.amount
            
            # Execute in PPSM
            result = self.ppsm.execute_action(player, action_type, to_amount)
            
            # Update action index
            self.current_action_index += 1
            
            # Create new table state
            new_state = self._create_table_state()
            
            # Add action effects
            self._add_action_effects(action, result)
            
            # Update store (not UI directly)
            self.store.dispatch({
                "type": "HANDS_REVIEW_ACTION_EXECUTED",
                "action_index": self.current_action_index - 1,
                "action": action,
                "state": new_state
            })
            
            print(f"🎯 HandsReviewSessionManager: Executed action {self.current_action_index}/{self.total_actions}")
            
            return HandsReviewState(
                current_hand=self.current_hand,
                current_action_index=self.current_action_index,
                total_actions=self.total_actions,
                is_playing=self.is_playing,
                playback_speed=self.playback_speed,
                street=new_state.get('street', 'PREFLOP'),
                board=new_state.get('board', []),
                seats=new_state.get('seats', []),
                pot=new_state.get('pot', {}),
                dealer=new_state.get('dealer', {}),
                action=new_state.get('action', {}),
                effects=new_state.get('effects', []),
                table=new_state.get('table', {}),
                animation=new_state.get('animation', {})
            )
            
        except Exception as e:
            print(f"❌ HandsReviewSessionManager: Error executing action: {e}")
            raise
    
    def _get_action_by_index(self, action_index: int) -> Dict[str, Any]:
        """Get action by global index across all streets."""
        if not self.current_hand:
            raise ValueError("No hand loaded")
        
        current_index = 0
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            street_actions = self.current_hand.streets[street].actions
            if current_index + len(street_actions) > action_index:
                return street_actions[action_index - current_index]
            current_index += len(street_actions)
        
        raise IndexError(f"Action index {action_index} out of range")
    
    def _get_player_by_uid(self, player_uid: str) -> Player:
        """Get Player object by UID from PPSM."""
        if not self.ppsm:
            raise ValueError("PPSM not initialized")
        
        # Get current game state
        game_state = self.ppsm.get_game_state()
        
        # Find player by name/UID
        for player_data in game_state.get('players', []):
            if player_data.get('name') == player_uid:
                # Create Player object from data
                from core.poker_types import Player
                return Player(
                    name=player_data.get('name', 'Unknown'),
                    stack=player_data.get('current_stack', 1000),
                    position=player_data.get('position', ''),
                    is_human=False,
                    is_active=player_data.get('acting', False),
                    cards=player_data.get('hole_cards', [])
                )
        
        # If not found, create a default player
        from core.poker_types import Player
        return Player(
            name=player_uid,
            stack=1000,
            position='',
            is_human=False,
            is_active=False,
            cards=[]
        )
    
    def play(self) -> None:
        """Start autoplay - business logic only."""
        if not self.is_playing and self.current_action_index < self.total_actions:
            self.is_playing = True
            
            # Schedule next action via GameDirector
            if self.game_director:
                self.game_director.schedule(
                    int(1000 / self.playback_speed),  # Convert to milliseconds
                    {"type": "AUTO_ADVANCE_HANDS_REVIEW"}
                )
            
            # Update store
            self.store.dispatch({
                "type": "HANDS_REVIEW_PLAY_STARTED",
                "is_playing": True
            })
            
            print("🎯 HandsReviewSessionManager: Autoplay started")
    
    def pause(self) -> None:
        """Pause autoplay - business logic only."""
        if self.is_playing:
            self.is_playing = False
            
            # Cancel scheduled events via GameDirector
            if self.game_director:
                self.game_director.cancel_all()
            
            # Update store
            self.store.dispatch({
                "type": "HANDS_REVIEW_PLAY_PAUSED",
                "is_playing": False
            })
            
            print("🎯 HandsReviewSessionManager: Autoplay paused")
    
    def seek(self, action_index: int) -> HandsReviewState:
        """Seek to specific action - business logic only."""
        if not self.current_hand:
            raise ValueError("No hand loaded")
        
        # Validate action index
        action_index = max(0, min(action_index, self.total_actions))
        
        # Reset PPSM to beginning
        self._initialize_ppsm_for_hand()
        
        # Execute actions up to target index
        self.current_action_index = 0
        for i in range(action_index):
            action = self._get_action_by_index(i)
            # Convert action to PPSM format
            player = self._get_player_by_uid(action.actor_uid)
            action_type = action.action
            to_amount = action.to_amount if action.to_amount is not None else action.amount
            
            self.ppsm.execute_action(player, action_type, to_amount)
            self.current_action_index += 1
        
        # Create table state
        new_state = self._create_table_state()
        
        # Update store
        self.store.dispatch({
            "type": "HANDS_REVIEW_SEEK_COMPLETED",
            "action_index": self.current_action_index,
            "state": new_state
        })
        
        print(f"🎯 HandsReviewSessionManager: Seeked to action {self.current_action_index}")
        
        return HandsReviewState(
            current_hand=self.current_hand,
            current_action_index=self.current_action_index,
            total_actions=self.total_actions,
            is_playing=self.is_playing,
            playback_speed=self.playback_speed,
            **new_state
        )
    
    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed - business logic only."""
        self.playback_speed = max(0.1, min(5.0, speed))
        
        # Update GameDirector if playing
        if self.is_playing and self.game_director:
            self.game_director.set_speed(self.playback_speed)
        
        # Update store
        self.store.dispatch({
            "type": "HANDS_REVIEW_SPEED_CHANGED",
            "speed": self.playback_speed
        })
        
        print(f"🎯 HandsReviewSessionManager: Playback speed set to {self.playback_speed}x")
    
    def _initialize_ppsm_for_hand(self) -> None:
        """Initialize PPSM with hand data - business logic only."""
        if not self.current_hand:
            return
        
        # Create game config from hand data
        config = GameConfig(
            num_players=len(self.current_hand.seats),
            small_blind=self.current_hand.metadata.small_blind,
            big_blind=self.current_hand.metadata.big_blind,
            starting_stack=1000  # Default, could be configurable
        )
        
        # Initialize PPSM
        self.ppsm.initialize_game(config)
        
        # Add players from seats
        for seat in self.current_hand.seats:
            self.ppsm.add_player(seat.player_uid, seat.starting_stack)
        
        # Set dealer position (default to seat 0 for now)
        self.ppsm.set_dealer_position(0)
    
    def _create_table_state(self) -> Dict[str, Any]:
        """Create table state from PPSM - business logic only."""
        try:
            # Get current game state from PPSM
            game_state = self.ppsm.get_game_state()
            
            # Extract relevant information
            seats = []
            for player in game_state.get('players', []):
                seats.append({
                    'player_uid': player.get('name', 'Unknown'),
                    'name': player.get('name', 'Unknown'),
                    'starting_stack': player.get('starting_stack', 1000),
                    'current_stack': player.get('current_stack', 1000),
                    'current_bet': player.get('current_bet', 0),
                    'stack': player.get('current_stack', 1000),
                    'bet': player.get('current_bet', 0),
                    'cards': player.get('hole_cards', []),
                    'folded': player.get('folded', False),
                    'all_in': player.get('all_in', False),
                    'acting': player.get('acting', False),
                    'position': player.get('position', ''),
                    'last_action': player.get('last_action', '')
                })
            
            # Determine current street
            street = "PREFLOP"
            board = game_state.get('board', [])
            if len(board) >= 3:
                street = "FLOP"
            if len(board) >= 4:
                street = "TURN"
            if len(board) >= 5:
                street = "RIVER"
            
            return {
                'table': {
                    'width': 1200,
                    'height': 800
                },
                'seats': seats,
                'board': board,
                'street': street,
                'pot': {
                    'amount': game_state.get('pot', 0),
                    'side_pots': game_state.get('side_pots', [])
                },
                'dealer': {
                    'position': game_state.get('dealer_position', 0)
                },
                'action': {
                    'current_player': game_state.get('current_player', -1),
                    'action_type': game_state.get('last_action_type', ''),
                    'amount': game_state.get('last_action_amount', 0)
                },
                'animation': {},
                'effects': []
            }
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Error creating table state: {e}")
            # Return default state
            return {
                'table': {'width': 1200, 'height': 800},
                'seats': [],
                'board': [],
                'street': 'PREFLOP',
                'pot': {'amount': 0, 'side_pots': []},
                'dealer': {'position': 0},
                'action': {'current_player': -1, 'action_type': '', 'amount': 0},
                'animation': {},
                'effects': []
            }
    
    def _add_action_effects(self, action, result) -> None:
        """Add action effects - business logic only."""
        try:
            # Get action type from Action object
            action_type = action.action.value if hasattr(action.action, 'value') else str(action.action)
            actor_uid = action.actor_uid if hasattr(action, 'actor_uid') else 'Unknown'
            
            # Debug: log what action type we're getting
            print(f"🎯 DEBUG: Action type: '{action_type}' (type: {type(action.action)})")
            
            # Add sound effects via EffectBus
            if self.effect_bus:
                self.effect_bus.add_poker_action_effects(action_type, actor_uid)
            
            # Add animation effects for ALL betting actions (not just end-of-street)
            if action_type in ["BET", "RAISE", "CALL", "CHECK", "FOLD"]:
                # Betting action animation - chips to pot
                if self.event_bus:
                    print(f"🎬 Triggering betting animation for action: {action_type}")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "betting_action",
                        "ms": 300,
                        "action_type": action_type,
                        "actor_uid": actor_uid
                    })
            
            # Add animation effects for specific actions
            if action_type in ["DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"]:
                # End-of-street animation
                if self.event_bus:
                    print(f"🎬 Triggering end-of-street animation for: {action_type}")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "chips_to_pot",
                        "ms": 260
                    })
            
            # Add showdown effects
            if action_type == "SHOWDOWN":
                if self.event_bus:
                    print(f"🎬 Triggering showdown animation")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "pot_to_winner",
                        "ms": 520
                    })
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Error adding action effects: {e}")
    
    def _get_current_state(self) -> HandsReviewState:
        """Get current session state."""
        table_state = self._create_table_state()
        return HandsReviewState(
            current_hand=self.current_hand,
            current_action_index=self.current_action_index,
            total_actions=self.total_actions,
            is_playing=self.is_playing,
            playback_speed=self.playback_speed,
            **table_state
        )
    
    def cleanup(self) -> None:
        """Clean up session resources."""
        try:
            # Cancel any scheduled events
            if self.game_director:
                self.game_director.cancel_all()
            
            # Reset state
            self.current_hand = None
            self.current_action_index = 0
            self.total_actions = 0
            self.is_playing = False
            
            print("🎯 HandsReviewSessionManager: Cleanup completed")
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Cleanup error: {e}")
