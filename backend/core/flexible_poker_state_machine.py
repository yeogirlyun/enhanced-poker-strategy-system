#!/usr/bin/env python3
"""
Flexible Poker State Machine (FPSM)

A modular and extensible poker state machine that can be used for:
- Practice sessions (interactive play)
- Simulations (replaying hands)
- Analysis (studying hands)
- Testing (automated scenarios)

This implementation uses an event-driven architecture and integrates with
the existing SessionLogger for comprehensive JSON logging.
"""

import random
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from .types import ActionType, Player, GameState, PokerState
from .hand_evaluation import EnhancedHandEvaluator
from .position_mapping import HandHistoryManager
from utils.sound_manager import SoundManager
from .session_logger import get_session_logger


@dataclass
class GameConfig:
    """Configuration for the poker game."""
    num_players: int = 6
    big_blind: float = 1.0
    small_blind: float = 0.5
    starting_stack: float = 100.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (2 <= self.num_players <= 9):
            raise ValueError(f"num_players must be between 2 and 9, got {self.num_players}")
        if self.big_blind <= 0:
            raise ValueError(f"big_blind must be positive, got {self.big_blind}")
        if self.small_blind <= 0:
            raise ValueError(f"small_blind must be positive, got {self.small_blind}")
        if self.small_blind >= self.big_blind:
            raise ValueError(f"small_blind ({self.small_blind}) must be less than big_blind ({self.big_blind})")
    
    auto_advance: bool = False  # For simulation mode


@dataclass
class GameEvent:
    """Represents a game event that can be handled by listeners."""
    event_type: str
    timestamp: float
    player_name: Optional[str] = None
    action: Optional[ActionType] = None
    amount: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)


class EventListener:
    """Base class for event listeners."""
    
    def on_event(self, event: GameEvent):
        """Handle a game event."""
        pass


class FlexiblePokerStateMachine:
    """
    Flexible and modular poker state machine.
    
    This state machine can be used for:
    - Practice sessions (interactive play)
    - Simulations (replaying hands)
    - Analysis (studying hands)
    - Testing (automated scenarios)
    """
    
    def __init__(self, config: GameConfig = None):
        """Initialize the flexible poker state machine."""
        self.config = config or GameConfig()
        
        # Core game state
        self.current_state = PokerState.START_HAND
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[]
        )
        
        # Player management
        self.action_player_index = 0
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 0
        
        # Event system
        self.event_listeners: List[EventListener] = []
        self.event_history: List[GameEvent] = []
        
        # Hand tracking
        self.hand_number = 0
        self.hand_history: List[Dict[str, Any]] = []
        
        # Utilities
        self.hand_evaluator = EnhancedHandEvaluator()
        self.sound_manager = SoundManager()
        
        # Strategy integration (optional)
        self.strategy_integration = self._create_basic_strategy_integration()
        self.hand_history_manager = HandHistoryManager()
        
        # Callbacks (for backward compatibility)
        self.on_action_required: Optional[Callable] = None
        self.on_hand_complete: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_action_executed: Optional[Callable] = None
        self.on_round_complete: Optional[Callable] = None
        
        # Round tracking
        self.actions_this_round = 0
        self.players_acted_this_round = set()
        
        # Initialize players
        self._initialize_players()
        
        # Initialize session logger
        self.session_logger = get_session_logger()
        self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                     "FPSM initialized", {
                                         "num_players": self.config.num_players
                                     })
    
    def _initialize_players(self):
        """Initialize players for the game."""
        self.game_state.players = []
        for i in range(self.config.num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=self.config.starting_stack,
                position="",
                is_human=False,
                is_active=True,
                cards=[]
            )
            self.game_state.players.append(player)
        
        # Assign positions
        self._assign_positions()
    
    def _assign_positions(self):
        """Assign positions to players relative to dealer position."""
        position_names = self._get_position_names()
        num_players = len(self.game_state.players)
        
        # Assign positions relative to dealer
        for i in range(num_players):
            # Calculate position index relative to dealer
            if self.config.num_players == 2:
                # Heads-up: dealer=SB/BTN (pos 0), BB (pos 1)  
                if i == self.dealer_position:
                    self.game_state.players[i].position = "SB/BTN"
                else:
                    self.game_state.players[i].position = "BB"
            else:
                # Multi-way: assign positions in order starting from UTG
                # UTG is first after BB, so we calculate from that
                utg_position = (self.big_blind_position + 1) % num_players
                position_offset = (i - utg_position) % num_players
                
                if position_offset < len(position_names):
                    self.game_state.players[i].position = position_names[position_offset]
                else:
                    self.game_state.players[i].position = f"Seat{i+1}"
    
    def _get_position_names(self) -> List[str]:
        """Get position names for the current number of players (proper poker order)."""
        num_players = self.config.num_players
        
        if num_players == 2:
            # Heads-up: [SB/BTN, BB]
            return ["SB/BTN", "BB"]
        elif num_players == 3:
            # 3-handed: [BTN, SB, BB]
            return ["BTN", "SB", "BB"]
        elif num_players == 4:
            # 4-handed: [UTG, BTN, SB, BB]
            return ["UTG", "BTN", "SB", "BB"]
        elif num_players == 5:
            # 5-handed: [UTG, CO, BTN, SB, BB]
            return ["UTG", "CO", "BTN", "SB", "BB"]
        elif num_players == 6:
            # 6-handed: [UTG, MP, CO, BTN, SB, BB]
            return ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        else:
            # 7+ players: [UTG, MP1, MP2, ..., CO, BTN, SB, BB]
            positions = ["UTG"]
            # Add middle positions
            mp_count = num_players - 5  # Total - (UTG + CO + BTN + SB + BB)
            for i in range(1, mp_count + 1):
                positions.append(f"MP{i}")
            positions.extend(["CO", "BTN", "SB", "BB"])
            return positions
    
    def add_event_listener(self, listener: EventListener):
        """Add an event listener."""
        self.event_listeners.append(listener)
    
    def remove_event_listener(self, listener: EventListener):
        """Remove an event listener."""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
    
    def _emit_display_state_event(self):
        """Emit a display state event with complete game information."""
        import time
        display_state = self.get_game_info()
        event = GameEvent(
            event_type="display_state_update",
            timestamp=time.time(),
            data={"display_state": display_state}
        )
        self._emit_event(event)
    
    def _emit_event(self, event: GameEvent):
        """Emit an event to all listeners."""
        self.event_history.append(event)
        
        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                self._safe_print(f"Error in event listener: {e}")
        
        # Call legacy callbacks for backward compatibility
        self._call_legacy_callbacks(event)
    
    def _call_legacy_callbacks(self, event: GameEvent):
        """Call legacy callbacks for backward compatibility."""
        if event.event_type == "action_required" and self.on_action_required:
            self.on_action_required(event.player_name)
        
        if event.event_type == "hand_complete" and self.on_hand_complete:
            self.on_hand_complete(event.data)
        
        if event.event_type == "state_change" and self.on_state_change:
            self.on_state_change(self.current_state)
        
        if event.event_type == "action_executed" and self.on_action_executed:
            self.on_action_executed(event.action, event.amount)
        
        if event.event_type == "round_complete" and self.on_round_complete:
            self.on_round_complete(event.data.get("street"))
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand."""
        self.hand_number += 1
        self.current_state = PokerState.START_HAND
        
        # Reset game state
        self.game_state.board = []
        self.game_state.pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.street = "preflop"
        
        # Use existing players if provided (for simulation)
        if existing_players:
            self.game_state.players = existing_players
            # Validate player count matches config
            if len(self.game_state.players) != self.config.num_players:
                raise ValueError(f"Player count mismatch: config expects {self.config.num_players}, got {len(self.game_state.players)}")
        else:
            # Reset player states
            for player in self.game_state.players:
                player.cards = []
                player.current_bet = 0.0
                player.has_folded = False
                player.is_all_in = False
                player.is_active = True
        
        # Advance dealer position
        if self.hand_number > 1:
            self.dealer_position = (self.dealer_position + 1) % self.config.num_players
        else:
            self.dealer_position = random.randint(0, self.config.num_players - 1)
        
        # Set blind positions
        if self.config.num_players == 2:
            # Heads-up: Dealer is Small Blind, other player is Big Blind
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % 2
        else:
            # Multi-way: SB is left of dealer, BB is left of SB
            self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
            self.big_blind_position = (self.small_blind_position + 1) % self.config.num_players
        
        # Assign positions based on dealer position
        self._assign_positions()
        
        # Initialize and shuffle deck
        self.game_state.deck = self._create_deck()
        random.shuffle(self.game_state.deck)
        
        # Deal cards to all players
        for player in self.game_state.players:
            if not player.cards:
                # Only deal new cards if player doesn't have cards
                player.cards = self._deal_cards(2)
        
        # Post blinds
        sb_player = self.game_state.players[self.small_blind_position]
        bb_player = self.game_state.players[self.big_blind_position]
        
        sb_amount = min(self.config.small_blind, sb_player.stack)
        bb_amount = min(self.config.big_blind, bb_player.stack)
        
        sb_player.current_bet = sb_amount
        sb_player.stack -= sb_amount
        bb_player.current_bet = bb_amount
        bb_player.stack -= bb_amount
        
        # Add blinds to pot
        self.game_state.pot = sb_amount + bb_amount
        
        self.game_state.current_bet = bb_amount
        
        # Set first action player (special handling for heads-up)
        if self.config.num_players == 2:
            # Heads-up: SB/BTN acts first preflop (small blind is also button)
            self.action_player_index = self.small_blind_position
        else:
            # Multi-way: First action is UTG (after big blind)
            self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
        
        # Transition to preflop betting
        self.transition_to(PokerState.PREFLOP_BETTING)
        
        # Emit display state event
        self._emit_display_state_event()
    
    def _create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        suits = ['h', 'd', 'c', 's']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        return [rank + suit for suit in suits for rank in ranks]
    
    def _deal_cards(self, num_cards: int) -> List[str]:
        """Deal cards from the deck."""
        cards = self.game_state.deck[:num_cards]
        self.game_state.deck = self.game_state.deck[num_cards:]
        return cards
    
    # Valid state transitions
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
        PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING, PokerState.END_HAND],  # Allow END_HAND for fold situations
        PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
        PokerState.DEAL_TURN: [PokerState.TURN_BETTING, PokerState.END_HAND],  # Allow END_HAND for fold situations
        PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
        PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING, PokerState.END_HAND],  # Allow END_HAND for fold situations
        PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }

    def transition_to(self, new_state: PokerState):
        """Transition to a new state if valid."""
        if new_state not in PokerState.__members__.values():
            raise ValueError(f"Invalid state: {new_state}")
        
        valid_transitions = self.STATE_TRANSITIONS.get(self.current_state, [])
        if new_state not in valid_transitions and new_state != self.current_state:
            raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                     f"State transition: {old_state} → {new_state}")
        
        # Handle state-specific logic
        if new_state == PokerState.DEAL_FLOP:
            self.game_state.board.extend(self._deal_cards(3))
            self.game_state.street = "flop"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            self.action_player_index = self._find_first_active_after_dealer()
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         "Flop dealt", {"board": self.game_state.board})
            # Auto-advance to FLOP_BETTING if auto_advance is enabled
            if hasattr(self.config, 'auto_advance') and self.config.auto_advance:
                self.transition_to(PokerState.FLOP_BETTING)
        
        elif new_state == PokerState.DEAL_TURN:
            self.game_state.board.append(self._deal_cards(1)[0])
            self.game_state.street = "turn"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            self.action_player_index = self._find_first_active_after_dealer()
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         "Turn dealt", {"board": self.game_state.board})
            # Auto-advance to TURN_BETTING if auto_advance is enabled
            if hasattr(self.config, 'auto_advance') and self.config.auto_advance:
                self.transition_to(PokerState.TURN_BETTING)
        
        elif new_state == PokerState.DEAL_RIVER:
            self.game_state.board.append(self._deal_cards(1)[0])
            self.game_state.street = "river"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            self.action_player_index = self._find_first_active_after_dealer()
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         "River dealt", {"board": self.game_state.board})
            # Auto-advance to RIVER_BETTING if auto_advance is enabled  
            if hasattr(self.config, 'auto_advance') and self.config.auto_advance:
                self.transition_to(PokerState.RIVER_BETTING)
        
        elif new_state == PokerState.SHOWDOWN:
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         "Showdown reached", {"board": self.game_state.board})
            self.transition_to(PokerState.END_HAND)
        
        elif new_state == PokerState.END_HAND:
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         f"Hand {self.hand_number} ended")
            # Determine winners
            active_players = [p for p in self.game_state.players 
                            if not p.has_folded]
            if active_players:
                if len(active_players) == 1:
                    winners = active_players
                else:
                    winners = self.determine_winners(active_players)
            else:
                winners = []

            # Award pot to winners
            if winners:
                pot_per_winner = self.game_state.pot / len(winners)
                for winner in winners:
                    winner.stack += pot_per_winner
                self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                             "Winners determined", {
                                                 "winners": [w.name for w in winners],
                                                 "pot": self.game_state.pot
                                             })
            else:
                self.session_logger.log_system("WARNING", "STATE_MACHINE", 
                                             "No winners - pot returned")
            
            # Reset current bet and player bets
            self.game_state.current_bet = 0.0
            for player in self.game_state.players:
                player.current_bet = 0.0

            # Create winner_info structure that matches what the UI expects
            winner_info = {
                "name": ", ".join([w.name for w in winners]) if winners else "Unknown",
                "amount": self.game_state.pot,
                "board": self.game_state.board.copy(),
                "hand": "Unknown"  # Will be filled by hand evaluator if available
            }
            
            # Try to get hand description for the first winner
            if winners and hasattr(self, 'hand_evaluator'):
                try:
                    first_winner = winners[0]
                    if first_winner.cards and len(first_winner.cards) == 2:
                        hand_eval = self.hand_evaluator.evaluate_hand(
                            first_winner.cards, self.game_state.board)
                        if isinstance(hand_eval, dict) and 'hand_description' in hand_eval:
                            winner_info["hand"] = hand_eval['hand_description']
                        elif isinstance(hand_eval, dict) and 'hand_rank' in hand_eval:
                            winner_info["hand"] = hand_eval['hand_rank'].name.replace('_', ' ').title()
                except Exception as e:
                    self._safe_print(f"Warning: Could not evaluate winning hand: {e}")
            
            self._emit_event(GameEvent(
                event_type="hand_complete",
                timestamp=time.time(),
                data={
                    "hand_number": self.hand_number,
                    "winners": [w.name for w in winners],
                    "winner_info": winner_info,
                    "pot_amount": self.game_state.pot
                }
            ))
            
            # Reset pot after emitting the event (for validation purposes)
            self.game_state.pot = 0.0
        
        # For betting states, ensure actions_this_round is reset if not already
        betting_states = [PokerState.PREFLOP_BETTING, PokerState.FLOP_BETTING, 
                         PokerState.TURN_BETTING, PokerState.RIVER_BETTING]
        if new_state in betting_states:
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            if new_state != PokerState.PREFLOP_BETTING:
                self._reset_bets_for_new_round()
            # Set first action player
            if new_state == PokerState.PREFLOP_BETTING:
                # Preflop: First action is UTG (player after big blind)
                # Don't override - action player was already set correctly in start_hand()
                pass
            else:
                # Postflop: First action is player after dealer
                if self.config.num_players == 2:
                    # Heads-up postflop: BB acts first (opposite of preflop)
                    self.action_player_index = self.big_blind_position
                else:
                    # Multi-way postflop: SB acts first (player after dealer)
                    self.action_player_index = self._find_first_active_after_dealer()
            first_player = self.game_state.players[self.action_player_index].name
            self.session_logger.log_system("INFO", "STATE_MACHINE", 
                                         f"{new_state} betting started", 
                                         {"first_action_player": first_player})
        
        # Emit state change event
        self._emit_event(GameEvent(
            event_type="state_change",
            timestamp=time.time(),
            data={"new_state": str(new_state), "old_state": str(old_state)}
        ))
    
    def _reset_bets_for_new_round(self):
        """Reset bets for a new betting round."""
        for player in self.game_state.players:
            self.game_state.pot += player.current_bet
            player.current_bet = 0.0
        self.game_state.current_bet = 0.0
    
    def _find_first_active_after_dealer(self) -> int:
        """Find the first active player after the dealer (for postflop)."""
        start = (self.dealer_position + 1) % len(self.game_state.players)
        return self._find_next_active_player(start - 1)  # Start from dealer to find next
    
    def _find_next_active_player(self, current_index: int) -> int:
        """Find the next active player after the given index."""
        n = len(self.game_state.players)
        for i in range(1, n + 1):
            idx = (current_index + i) % n
            player = self.game_state.players[idx]
            if not player.has_folded and player.is_active and player.stack > 0:
                return idx
        return -1  # No active players
    
    def _is_action_valid(self, action: ActionType, amount: float, valid_actions: Dict[str, Any]) -> bool:
        """Check if an action is valid for the current game state."""
        if not valid_actions.get(action.value, False):
            return False
        
        # Additional validation based on action type
        if action == ActionType.CALL:
            # No Limit Hold'em: Always allow calls (automatically capped at stack in execute_action)
            return True
        
        elif action == ActionType.BET:
            # No Limit Hold'em: Only check minimum bet, no maximum limit
            return amount > 0
        
        elif action == ActionType.RAISE:
            # No Limit Hold'em: Only check minimum raise, no maximum limit
            min_raise = valid_actions.get('min_bet', self.config.big_blind)
            return amount >= min_raise
        
        return True
    
    def _safe_print(self, message: str):
        """Safely print a message, handling BrokenPipeError."""
        try:
            print(message, flush=True)
        except (BrokenPipeError, OSError):
            # Ignore broken pipe errors when output is piped
            pass
    
    def execute_action(self, player: Player, action: ActionType, amount: float = 0.0):
        """Execute a player action."""
        if not player.is_active or player.has_folded:
            return False
        
        # Validate action
        valid_actions = self.get_valid_actions_for_player(player)
        if not self._is_action_valid(action, amount, valid_actions):
            return False
        
        # Log current state
        self._safe_print(f"   Current state: {self.current_state}, Street: {self.game_state.street}")
        self._safe_print(f"   Current bet: ${self.game_state.current_bet}, Player bet: ${player.current_bet}")
        
        # Execute the action
        if action == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
            self._safe_print(f"   {player.name} folds")
            
        elif action == ActionType.CHECK:
            self._safe_print(f"   {player.name} checks")
            
        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount > 0:
                actual_call = min(call_amount, player.stack)
                player.current_bet += actual_call
                player.stack -= actual_call
                self.game_state.pot += actual_call
                self._safe_print(f"   {player.name} calls ${actual_call}")
            
        elif action == ActionType.BET:
            if amount > 0:
                # No Limit Hold'em: Allow any bet amount (capped at stack if needed)
                actual_amount = min(amount, player.stack)
                player.current_bet += actual_amount
                player.stack -= actual_amount
                self.game_state.pot += actual_amount
                self.game_state.current_bet = player.current_bet
                self._safe_print(f"   {player.name} bets ${actual_amount}")
            
        elif action == ActionType.RAISE:
            if amount >= self.game_state.current_bet:
                # No Limit Hold'em: Allow any raise amount (capped at stack if needed)
                total_needed = amount - player.current_bet
                actual_total = min(total_needed, player.stack)
                actual_amount = player.current_bet + actual_total
                
                player.current_bet = actual_amount
                player.stack -= actual_total
                self.game_state.pot += actual_total
                self.game_state.current_bet = actual_amount
                self._safe_print(f"   {player.name} raises to ${actual_amount}")
        
        # Mark player as acted this round
        self.players_acted_this_round.add(player.name)
        self.actions_this_round += 1
        
        self._safe_print(f"   Actions this round: {self.actions_this_round}")
        self._safe_print(f"   Players acted: {len(self.players_acted_this_round)}")
        
        # Emit action event
        import time
        action_event = GameEvent(
            event_type="action_executed",
            timestamp=time.time(),
            player_name=player.name,
            action=action,
            amount=amount
        )
        self._emit_event(action_event)
        
        # Check if round is complete BEFORE advancing action player
        if self._is_round_complete():
            # Round complete detected
            self._handle_round_complete()
        else:
            # Round not complete - advance to next player
            self._advance_action_player()
            # Only emit display state event if round is not complete to avoid conflicts
            self._emit_display_state_event()
        
        return True
    
    def _advance_action_player(self):
        """Advance to the next action player."""
        next_index = self._find_next_active_player(self.action_player_index)
        if next_index == -1:
            self.transition_to(PokerState.END_HAND)
            return
        self.action_player_index = next_index
        self._emit_event(GameEvent(
            event_type="action_required",
            timestamp=time.time(),
            player_name=self.game_state.players[next_index].name
        ))
    
    def _is_round_complete(self) -> bool:
        """Check if the current betting round is complete."""
        active_players = [p for p in self.game_state.players 
                         if not p.has_folded and p.is_active]
        
        if len(active_players) <= 1:
            return True
        
        # Check if bets are equalized first (this is the key poker rule)
        max_bet = max(p.current_bet for p in active_players)
        all_equal = all(p.current_bet == max_bet or p.is_all_in 
                       for p in active_players)
        
        if not all_equal:
            return False
        
        # If bets are equalized, check if we've gone around the table
        # This prevents infinite loops while ensuring proper round completion
        if self.actions_this_round >= len(active_players):
            return True
        
        # Special case: if everyone checked/called and no bets were made
        if max_bet == 0 and self.actions_this_round > 0:
            return True
        
        return False
    
    def _handle_round_complete(self):
        """Handle completion of a betting round."""
        # Round complete on current street
        self._safe_print(f"   Current state: {self.current_state}")
        self._safe_print(f"   Actions this round: {self.actions_this_round}")
        self._safe_print(f"   Players acted: {len(self.players_acted_this_round)}")
        
        self._reset_bets_for_new_round()
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        
        # Check active players after reset
        active_players = [p for p in self.game_state.players 
                         if not p.has_folded and p.is_active]
        
        if len(active_players) <= 1:
            self._safe_print(f"🏁 Only {len(active_players)} active players, ending hand")
            self.transition_to(PokerState.END_HAND)
            return
        
        # Emit round complete event
        self._emit_event(GameEvent(
            event_type="round_complete",
            timestamp=time.time(),
            data={"street": self.game_state.street}
        ))
        
        # Transition to next state based on current state
        if self.current_state == PokerState.PREFLOP_BETTING:
            self._safe_print("🔄 Preflop betting complete, transitioning to DEAL_FLOP")
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.current_state == PokerState.DEAL_FLOP:
            self._safe_print("🔄 Flop dealing complete, transitioning to FLOP_BETTING")
            self.transition_to(PokerState.FLOP_BETTING)
        elif self.current_state == PokerState.FLOP_BETTING:
            self._safe_print("🔄 Flop betting complete, transitioning to DEAL_TURN")
            self.transition_to(PokerState.DEAL_TURN)
        elif self.current_state == PokerState.DEAL_TURN:
            self._safe_print("🔄 Turn dealing complete, transitioning to TURN_BETTING")
            self.transition_to(PokerState.TURN_BETTING)
        elif self.current_state == PokerState.TURN_BETTING:
            self._safe_print("🔄 Turn betting complete, transitioning to DEAL_RIVER")
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.current_state == PokerState.DEAL_RIVER:
            self._safe_print("🔄 River dealing complete, transitioning to RIVER_BETTING")
            self.transition_to(PokerState.RIVER_BETTING)
        elif self.current_state == PokerState.RIVER_BETTING:
            self._safe_print("🔄 River betting complete, transitioning to SHOWDOWN")
            self.transition_to(PokerState.SHOWDOWN)
        
        # Note: Display state event will be emitted by transition_to method
    
    def determine_winners(self, players: List[Player]) -> List[Player]:
        """Determine the winners among the given players."""
        if not players:
            return []
        
        if len(players) == 1:
            return players
        
        # Evaluate hands
        player_hands = []
        for player in players:
            if len(player.cards) == 2:
                hand_eval = self.hand_evaluator.evaluate_hand(
                    player.cards, self.game_state.board)
                # Extract the hand rank value from the evaluation result
                if isinstance(hand_eval, dict) and 'hand_rank' in hand_eval:
                    hand_rank = hand_eval['hand_rank']
                    # Convert HandRank enum to integer value for comparison
                    rank_value = hand_rank.value if hasattr(hand_rank, 'value') else hand_rank
                else:
                    rank_value = hand_eval if isinstance(hand_eval, (int, float)) else 0
                player_hands.append((player, rank_value))
        
        # Handle case where no valid hands are evaluated
        if not player_hands:
            return players  # Return all players if no hands can be evaluated
        
        # Sort by hand rank (best first)
        player_hands.sort(key=lambda x: x[1], reverse=True)
        
        # Find winners (players with the same best hand rank)
        best_rank = player_hands[0][1]
        winners = [player for player, rank in player_hands if rank == best_rank]
        
        return winners
    
    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        if 0 <= self.action_player_index < len(self.game_state.players):
            return self.game_state.players[self.action_player_index]
        return None
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get comprehensive game information."""
        action_player = self.get_action_player()
        
        return {
            "state": self.current_state.value,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board.copy(),
            "players": [
                {
                    "name": p.name,
                    "position": p.position,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "has_folded": p.has_folded,
                    "is_human": p.is_human,
                    "cards": p.cards if (
                        p.is_human or 
                        self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND]
                    ) else ["**", "**"],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
            "street": self.game_state.street,
            "hand_number": self.hand_number
        }
    
    def get_valid_actions_for_player(self, player: Player) -> Dict[str, Any]:
        """Get valid actions for a player."""
        if not player or player.has_folded:
            return {}
        
        call_amount = self.game_state.current_bet - player.current_bet
        min_bet = max(self.game_state.current_bet, self.config.big_blind)
        
        valid_actions = {
            "fold": True,
            "check": call_amount == 0,
            "call": call_amount > 0 and call_amount <= player.stack,
            "bet": player.stack > 0,
            "raise": player.stack > min_bet,
            "call_amount": call_amount,
            "min_bet": min_bet,
            "max_bet": player.stack
        }
        
        return valid_actions
    
    def set_player_cards(self, player_index: int, cards: List[str]):
        """Set cards for a specific player (for simulation mode)."""
        if 0 <= player_index < len(self.game_state.players):
            self.game_state.players[player_index].cards = cards.copy()
    
    def set_board_cards(self, cards: List[str]):
        """Set board cards (for simulation mode)."""
        self.game_state.board = cards.copy()
        # Emit display state event to update UI immediately
        self._emit_display_state_event()
    
    def set_player_folded(self, player_index: int, folded: bool):
        """Set folded status for a player (for simulation mode)."""
        if 0 <= player_index < len(self.game_state.players):
            self.game_state.players[player_index].has_folded = folded
            self.game_state.players[player_index].is_active = not folded

    def _create_basic_strategy_integration(self):
        """Create a basic strategy integration for testing."""
        class BasicStrategyIntegration:
            def __init__(self):
                self.name = "Basic Strategy Integration"
                self.version = "1.0"
            
            def get_action(self, player, game_state, valid_actions):
                """Get action for a player based on basic strategy."""
                return "check"  # Default action
            
            def load_strategy(self, strategy_file):
                """Load strategy from file."""
                return True
            
            def save_strategy(self, strategy_file):
                """Save strategy to file."""
                return True
        
        return BasicStrategyIntegration()
