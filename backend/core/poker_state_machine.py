#!/usr/bin/env python3
"""
Texas Hold'em Poker State Machine - FULLY IMPROVED VERSION

This version implements all critical fixes:
1. Dynamic position tracking
2. Correct raise logic  
3. All-in state tracking
4. Improved round completion
5. Strategy integration for bots
6. Better input validation
7. COMPREHENSIVE SESSION TRACKING - NEW!
"""

from enum import Enum
from typing import List, Optional, Set, Tuple, Dict, Any
from dataclasses import dataclass, field
import time
import random
import sys
from .session_logger import get_session_logger, SessionLogger
import os
import json
import uuid
from datetime import datetime
import math

# Import the enhanced hand evaluator for accurate winner determination
from .hand_evaluation import EnhancedHandEvaluator, HandRank

# Import the position mapping system for strategy integration
from .position_mapping import EnhancedStrategyIntegration, HandHistoryManager

# Import the sound manager
from utils.sound_manager import SoundManager

# IMMEDIATE FLUSH DEBUG PRINT for critical debugging
def debug_print(*args, **kwargs):
    """Print with immediate flush to prevent buffer loss on abrupt exits."""
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
        sys.stderr.flush()
    except BrokenPipeError:
        # Handle broken pipe gracefully during testing
        pass


@dataclass
class DisplayState:
    """UI-ready display state with pre-computed visual data."""
    valid_actions: Dict[str, Dict[str, Any]]  # Button states and labels
    player_highlights: List[bool]  # Index-based list for highlighting
    card_visibilities: List[bool]  # Per-player: True if cards should be shown
    chip_representations: Dict[str, str]  # Chip symbols for stacks and pots
    layout_positions: Dict[str, Tuple[int, int]]  # UI positions
    community_cards: List[str]  # Current board cards (preserved during showdown)
    pot_amount: float  # Current pot amount
    current_bet: float  # Current bet amount
    action_player_index: int  # Index of current action player
    game_state: str  # Current game state string
    last_action_details: str  # Last action for UI feedback


class PokerState(Enum):
    """Poker game states following standard Texas Hold'em flow."""
    START_HAND = "start_hand"
    PREFLOP_BETTING = "preflop_betting"
    DEAL_FLOP = "deal_flop"
    FLOP_BETTING = "flop_betting"
    DEAL_TURN = "deal_turn"
    TURN_BETTING = "turn_betting"
    DEAL_RIVER = "deal_river"
    RIVER_BETTING = "river_betting"
    SHOWDOWN = "showdown"
    END_HAND = "end_hand"


class ActionType(Enum):
    """Valid poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"


@dataclass
class Player:
    """Enhanced Player data structure with all-in tracking."""
    name: str
    stack: float
    position: str
    is_human: bool
    is_active: bool
    cards: List[str]
    current_bet: float = 0.0
    has_acted_this_round: bool = False
    is_all_in: bool = False  # NEW: Track all-in state
    total_invested: float = 0.0  # NEW: Track total money put in pot
    # BUG FIX: Track partial calls for side pot calculations
    partial_call_amount: Optional[float] = None
    full_call_amount: Optional[float] = None


@dataclass
class GameState:
    """Enhanced game state with better tracking."""
    players: List[Player]
    board: List[str]
    pot: float
    current_bet: float
    street: str
    players_acted: Set[int] = field(default_factory=set)
    round_complete: bool = False
    deck: List[str] = field(default_factory=list)
    min_raise: float = 1.0  # NEW: Track minimum raise amount
    big_blind: float = 1.0
    last_raise_amount: float = 0.0  # NEW: Track the size of the last raise for under-raise validation
    last_full_raise_amount: float = 0.0  # NEW: Track the amount of the last valid, action-reopening raise
    last_action_details: str = ""  # NEW: Track the last action for UI feedback


@dataclass
class HandHistoryLog:
    """A snapshot of the game state at a specific action."""
    timestamp: float
    street: str
    player_name: str
    action: ActionType
    amount: float
    pot_size: float
    board: List[str]
    player_states: List[dict]  # Store a simplified dict of each player's state


@dataclass
class SessionMetadata:
    """Complete session information and metadata."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_hands: int = 0
    total_players: int = 0
    initial_stacks: Dict[str, float] = field(default_factory=dict)
    final_stacks: Dict[str, float] = field(default_factory=dict)
    big_blind_amount: float = 1.0
    strategy_data: Optional[Dict] = None
    session_notes: str = ""


@dataclass
class HandResult:
    """Complete information about a hand's outcome."""
    hand_number: int
    start_time: float
    end_time: float
    players_at_start: List[Dict[str, Any]]
    players_at_end: List[Dict[str, Any]]
    board_cards: List[str]
    pot_amount: float
    winners: List[Dict[str, Any]]
    side_pots: List[Dict[str, Any]]
    action_history: List[HandHistoryLog]
    showdown_cards: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SessionState:
    """Complete session state for replay and debugging."""
    session_metadata: SessionMetadata
    current_hand_number: int
    hands_played: List[HandResult]
    current_hand_state: Optional[GameState] = None
    current_hand_history: List[HandHistoryLog] = field(default_factory=list)
    session_log: List[str] = field(default_factory=list)


class ImprovedPokerStateMachine:
    """Fully improved poker state machine with comprehensive session tracking."""

    # Valid state transitions
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
        PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING],
        PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
        PokerState.DEAL_TURN: [PokerState.TURN_BETTING],
        PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
        PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING],
        PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }

    def __init__(self, num_players: int = 6, strategy_data=None, root_tk=None, test_mode: bool = False):
        """Initialize the poker state machine."""
        debug_print(f"🏗️ CONSTRUCTOR: PokerStateMachine created with {num_players} players")
        debug_print(f"🏗️ CONSTRUCTOR: Object ID = {id(self)}")
        
        self.num_players = num_players
        self.strategy_data = strategy_data
        self.root_tk = root_tk
        
        # Initialize comprehensive logging system
        self.logger = get_session_logger()
        self.session_id = None
        self.hand_number = 0
        
        # Start logging session
        self._start_logging_session()
        
        # Register cleanup for this state machine instance
        self._register_cleanup()
        
        # Game state
        self.current_state = PokerState.START_HAND
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[]
        )
        self.action_player_index = 0
        self.hand_completed = False  # Add hand_completed attribute
        self.preserved_board = None  # Add preserved_board attribute
        
        # Action logging
        self.action_log = []  # Add action_log attribute
        self.max_log_size = 1000  # Add max_log_size attribute
        
        # FIXED: Add proper memory management initialization
        self.max_hand_history = 1000  # Limit hand history size
        self.max_action_log = 500     # Reduce action log size
        self._memory_check_interval = 10  # Check memory every 10 hands
        self._hands_since_cleanup = 0
        
        # Position tracking
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 0
        
        # Callbacks
        self.on_action_required = None
        self.on_hand_complete = None
        self.on_state_change = None
        self.on_log_entry = None
        self.on_round_complete = None
        self.on_action_executed = None
        self.on_action_player_changed = None
        
        # Session tracking
        self.session_state = None
        self.hand_history = []
        
        # Strategy integration
        if strategy_data and hasattr(strategy_data, 'strategy_dict'):
            self.strategy_integration = EnhancedStrategyIntegration(strategy_data.strategy_dict, num_players)
        else:
            self.strategy_integration = None
        self.hand_history_manager = HandHistoryManager()
        
        # Hand evaluator
        self.hand_evaluator = EnhancedHandEvaluator()
        
        # Initialize hand evaluation cache
        self._hand_eval_cache = {}
        self._max_cache_size = 1000
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Sound manager
        self.sound_manager = SoundManager(test_mode=test_mode)
        self.test_mode = test_mode  # Store test_mode for access by other components
        
        # Initialize voice system
        try:
            from voice_announcement_system import voice_system
            self.voice_system = voice_system
        except ImportError:
            self.voice_system = None
        
        # GTO Strategy Mode
        self.strategy_mode = "GTO"  # Default to GTO mode
        
        # Initialize GTO preflop ranges
        self._initialize_gto_ranges()
        
        # Initialize players and session
        self._initialize_players()
        self.session_state = self._initialize_session_state()

    def _initialize_gto_ranges(self):
        """Initialize comprehensive GTO preflop ranges based on modern poker theory."""
        self.gto_preflop_ranges = {
            "UTG": {  # ~15% RFI (from Red Chip/ Upswing)
                "rfi": { "range": ["AA-88", "AKs-AJs", "KQs", "AJo+", "KQo"], "freq": 1.0 },
                "vs_rfi": { "call": {"range": ["TT-88", "AQs-AJs", "KQs", "QJs"], "freq": 1.0}, "three_bet": {"range": ["AA-JJ", "AKs", "AQs"], "freq": 1.0, "size_mult": 3.0} },
                "vs_three_bet": { "call": {"range": ["QQ-JJ", "AKs", "AQs"], "freq": 1.0}, "four_bet": {"range": ["AA-KK", "AKs"], "freq": 1.0, "size_mult": 2.5} }
            },
            "MP": {  # ~20-25% RFI
                "rfi": { "range": ["AA-77", "AKs-A9s", "KQs-KTs", "QJs", "JTs", "AJo+", "KQo", "QJo"], "freq": 1.0 },
                "vs_rfi": { "call": {"range": ["99-77", "AQs-A9s", "KQs-KJs", "QJs-JTs"], "freq": 1.0}, "three_bet": {"range": ["AA-TT", "AKs-AQs", "KQs"], "freq": 1.0, "size_mult": 3.0} },
                "vs_three_bet": { "call": {"range": ["JJ-99", "AQs", "KQs"], "freq": 1.0}, "four_bet": {"range": ["AA-KK", "AKs"], "freq": 1.0, "size_mult": 2.5} }
            },
            "CO": {  # ~35-40% RFI
                "rfi": { "range": ["AA-66", "AKs-A8s", "KQs-K9s", "QJs-QTs", "JTs", "T9s", "98s", "87s", "AJo+", "KTo+", "QTo+", "JTo"], "freq": 1.0 },
                "vs_rfi": { "call": {"range": ["88-66", "AJs-A8s", "KJs-KTs", "QTs-JTs", "T9s-98s"], "freq": 1.0}, "three_bet": {"range": ["AA-99", "AKs-AJs", "KQs"], "freq": 1.0, "size_mult": 2.5} },
                "vs_three_bet": { "call": {"range": ["TT-88", "AJs", "KQs"], "freq": 1.0}, "four_bet": {"range": ["AA-QQ", "AKs"], "freq": 1.0, "size_mult": 2.5} }
            },
            "BTN": {  # ~50-55% RFI
                "rfi": { "range": ["AA-55", "AKs-A2s", "KQs-K8s", "QJs-Q9s", "JTs-J9s", "T9s-T8s", "98s-97s", "87s-86s", "76s", "ATo+", "K9o+", "QTo+", "JTo", "T9o", "98o"], "freq": 1.0 },
                "vs_rfi": { "call": {"range": ["77-55", "ATs-A2s", "KTs-K9s", "QTs-Q9s", "J9s-T8s", "98s-87s"], "freq": 1.0}, "three_bet": {"range": ["AA-88", "AKs-ATs", "KQs-KJs"], "freq": 1.0, "size_mult": 2.5} },
                "vs_three_bet": { "call": {"range": ["99-77", "ATs", "KJs"], "freq": 1.0}, "four_bet": {"range": ["AA-JJ", "AKs"], "freq": 1.0, "size_mult": 2.5} }
            },
            "SB": {  # ~60-65% RFI (mix limps)
                "rfi": { "range": ["AA-22", "AKs-A2s", "KQs-K2s", "QJs-Q2s", "JTs-J2s", "T9s-T2s", "98s-92s", "87s-82s", "76s-72s", "65s-62s", "54s-52s", "43s", "A9o+", "KTo+", "Q9o+", "J9o+", "T8o+", "97o+", "86o+", "75o+", "64o+", "53o+"], "freq": 0.8 },
                "vs_rfi": { "call": {"range": ["TT-22", "AJs-A2s", "KJs-K2s", "QTs-Q2s", "J9s-J2s", "T8s-T2s", "97s-92s", "86s-82s", "75s-72s", "64s-62s", "53s-52s", "43s"], "freq": 0.7}, "three_bet": {"range": ["AA-99", "AKs-AJs", "KQs"], "freq": 1.0, "size_mult": 3.0} },
                "vs_three_bet": { "call": {"range": ["JJ-88", "AQs-AJs", "KQs"], "freq": 0.8}, "four_bet": {"range": ["AA-KK", "AKs"], "freq": 1.0, "size_mult": 3.0} }
            },
            "BB": {  # Defensive, no RFI
                "vs_rfi": { "call": {"range": ["JJ-22", "AQs-A2s", "KQs-K5s", "QJs-Q8s", "JTs-J8s", "T9s-T8s", "98s-97s", "87s-86s", "76s", "AJo+", "KQo+", "QJo"], "freq": 1.0}, "three_bet": {"range": ["AA-TT", "AKs-AQs", "KQs"], "freq": 1.0, "size_mult": 3.5} },
                "vs_three_bet": { "call": {"range": ["QQ-99", "AQs", "KQs"], "freq": 1.0}, "four_bet": {"range": ["AA-KK", "AKs"], "freq": 1.0, "size_mult": 2.5} }
            }
        }
        # Note: Original UTG RFI frequency is 1.0, but can be overridden for testing

    def _initialize_session_state(self) -> SessionState:
        """Initialize comprehensive session tracking."""
        session_id = str(uuid.uuid4())
        metadata = SessionMetadata(
            session_id=session_id,
            start_time=time.time(),
            total_players=self.num_players,
            big_blind_amount=self.game_state.big_blind if self.game_state else 1.0,
            strategy_data=self.strategy_data
        )
        
        return SessionState(
            session_metadata=metadata,
            current_hand_number=0,
            hands_played=[],
            current_hand_state=None,
            current_hand_history=[],
            session_log=[]
        )

    def _log_session_event(self, event: str):
        """Log session-level events."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[SESSION {timestamp}] {event}"
        self.session_state.session_log.append(log_entry)

    def _capture_player_state(self, player: Player) -> Dict[str, Any]:
        """Capture complete player state for session tracking."""
        return {
            "name": player.name,
            "stack": player.stack,
            "position": player.position,
            "is_human": player.is_human,
            "is_active": player.is_active,
            "cards": player.cards.copy() if player.is_human else [],
            "current_bet": player.current_bet,
            "total_invested": player.total_invested,
            "is_all_in": player.is_all_in,
            "has_acted_this_round": player.has_acted_this_round
        }

    def _capture_game_state(self) -> Dict[str, Any]:
        """Capture complete game state for session tracking."""
        if not self.game_state:
            return {}
        
        return {
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "street": self.game_state.street,
            "board": self.game_state.board.copy(),
            "min_raise": self.game_state.min_raise,
            "big_blind": self.game_state.big_blind,
            "players_acted": list(self.game_state.players_acted),
            "round_complete": self.game_state.round_complete,
            "players": [self._capture_player_state(p) for p in self.game_state.players]
        }

    def start_session(self):
        """Start a new poker session."""
        self.session_state = self._initialize_session_state()
        # Reset hand history and any other per-session state
        self.hand_history = []
        self.current_state = PokerState.START_HAND
        # FIX: Don't set action_player_index here - it will be set correctly in start_hand
        self.dealer_position = 0
        self._log_session_event("Session started")
        self._log_session_event(f"Players: {self.num_players}")
        self._log_session_event(f"Big Blind: ${self.session_state.session_metadata.big_blind_amount}")

    def end_session(self):
        """End the current session and capture final statistics."""
        if self.session_state:
            self.session_state.session_metadata.end_time = time.time()
            self.session_state.session_metadata.total_hands = len(self.session_state.hands_played)
            
            # Capture final player stacks
            if self.game_state:
                for player in self.game_state.players:
                    self.session_state.session_metadata.final_stacks[player.name] = player.stack
            
            self._log_session_event("Session ended")
            self._log_session_event(f"Total hands played: {self.session_state.session_metadata.total_hands}")

    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        if not self.session_state:
            return {}
        metadata = self.session_state.session_metadata
        duration = (metadata.end_time or time.time()) - metadata.start_time
        # Get human win/loss stats if present
        human_wins = getattr(self.session_state, 'human_wins', 0)
        human_losses = getattr(self.session_state, 'human_losses', 0)
        return {
            "session_id": metadata.session_id,
            "start_time": datetime.fromtimestamp(metadata.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(metadata.end_time).isoformat() if metadata.end_time else None,
            "session_duration": duration,
            "total_hands": metadata.total_hands,
            "total_players": metadata.total_players,
            "big_blind_amount": metadata.big_blind_amount,
            "initial_stacks": metadata.initial_stacks,
            "final_stacks": metadata.final_stacks,
            "session_notes": metadata.session_notes,
            "hands_played": len(self.session_state.hands_played),
            "human_wins": human_wins,
            "human_losses": human_losses,
        }

    def export_session(self, filepath: str) -> bool:
        """Export complete session data to JSON file."""
        try:
            session_data = {
                "session_info": self.get_session_info(),
                "hands_played": [
                    {
                        "hand_number": hand.hand_number,
                        "start_time": datetime.fromtimestamp(hand.start_time).isoformat(),
                        "end_time": datetime.fromtimestamp(hand.end_time).isoformat(),
                        "players_at_start": hand.players_at_start,
                        "players_at_end": hand.players_at_end,
                        "board_cards": hand.board_cards,
                        "pot_amount": hand.pot_amount,
                        "winners": hand.winners,
                        "side_pots": hand.side_pots,
                        "action_history": [
                            {
                                "timestamp": datetime.fromtimestamp(action.timestamp).isoformat(),
                                "street": action.street,
                                "player_name": action.player_name,
                                "action": action.action.value,
                                "amount": action.amount,
                                "pot_size": action.pot_size,
                                "board": action.board,
                                "player_states": action.player_states
                            }
                            for action in hand.action_history
                        ],
                        "showdown_cards": hand.showdown_cards
                    }
                    for hand in self.session_state.hands_played
                ],
                "session_log": self.session_state.session_log
            }
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            self._log_session_event(f"Session exported to {filepath}")
            return True
            
        except Exception as e:
            self._log_session_event(f"Failed to export session: {str(e)}")
            return False

    def import_session(self, filepath: str) -> bool:
        """Import session data from JSON file."""
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            
            # Reconstruct session state from imported data
            # This would require more complex reconstruction logic
            self._log_session_event(f"Session imported from {filepath}")
            return True
            
        except Exception as e:
            self._log_session_event(f"Failed to import session: {str(e)}")
            return False

    def replay_hand(self, hand_number: int) -> Optional[Dict[str, Any]]:
        """Replay a specific hand from the session."""
        if not self.session_state or hand_number >= len(self.session_state.hands_played):
            return None
        
        hand = self.session_state.hands_played[hand_number]
        
        replay_data = {
            "hand_number": hand.hand_number,
            "start_time": datetime.fromtimestamp(hand.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(hand.end_time).isoformat(),
            "players_at_start": hand.players_at_start,
            "players_at_end": hand.players_at_end,
            "board_cards": hand.board_cards,
            "pot_amount": hand.pot_amount,
            "winners": hand.winners,
            "side_pots": hand.side_pots,
            "action_history": [
                {
                    "timestamp": datetime.fromtimestamp(action.timestamp).isoformat(),
                    "street": action.street,
                    "player_name": action.player_name,
                    "action": action.action.value,
                    "amount": action.amount,
                    "pot_size": action.pot_size,
                    "board": action.board,
                    "player_states": action.player_states
                }
                for action in hand.action_history
            ],
            "showdown_cards": hand.showdown_cards
        }
        
        return replay_data

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics."""
        if not self.session_state:
            return {}
        
        stats = {
            "total_hands": len(self.session_state.hands_played),
            "session_duration": (self.session_state.session_metadata.end_time or time.time()) - self.session_state.session_metadata.start_time,
            "hands_per_hour": 0,
            "total_pot_volume": 0,
            "biggest_pot": 0,
            "player_statistics": {}
        }
        
        # Calculate statistics from hands played
        for hand in self.session_state.hands_played:
            stats["total_pot_volume"] += hand.pot_amount
            stats["biggest_pot"] = max(stats["biggest_pot"], hand.pot_amount)
        
        if stats["session_duration"] > 0:
            stats["hands_per_hour"] = (stats["total_hands"] / stats["session_duration"]) * 3600
        
        # Initialize player statistics from current game state
        player_stats = {}
        if self.game_state:
            for player in self.game_state.players:
                player_stats[player.name] = {
                    "hands_played": 0,
                    "total_winnings": 0,
                    "biggest_win": 0,
                    "all_ins": 0,
                    "total_bets": 0,
                    "total_calls": 0,
                    "total_raises": 0,
                    "total_folds": 0,
                    "total_checks": 0,
                    "current_stack": player.stack,
                    "total_invested": player.total_invested
                }
        
        # Calculate player statistics from hands played
        for hand in self.session_state.hands_played:
            for player_end in hand.players_at_end:
                name = player_end["name"]
                if name not in player_stats:
                    player_stats[name] = {
                        "hands_played": 0,
                        "total_winnings": 0,
                        "biggest_win": 0,
                        "all_ins": 0,
                        "total_bets": 0,
                        "total_calls": 0,
                        "total_raises": 0,
                        "total_folds": 0,
                        "total_checks": 0,
                        "current_stack": player_end.get("stack", 0),
                        "total_invested": player_end.get("total_invested", 0)
                    }
                
                player_stats[name]["hands_played"] += 1
        
        # Add real-time action tracking from action log
        for action_log in self.action_log:
            if hasattr(action_log, 'player_name') and hasattr(action_log, 'action'):
                player_name = action_log.player_name
                action = action_log.action
                amount = getattr(action_log, 'amount', 0)
                
                if player_name not in player_stats:
                    player_stats[player_name] = {
                        "hands_played": 0,
                        "total_winnings": 0,
                        "biggest_win": 0,
                        "all_ins": 0,
                        "total_bets": 0,
                        "total_calls": 0,
                        "total_raises": 0,
                        "total_folds": 0,
                        "total_checks": 0,
                        "current_stack": 0,
                        "total_invested": 0
                    }
                
                if action == ActionType.BET:
                    player_stats[player_name]["total_bets"] += 1
                elif action == ActionType.CALL:
                    player_stats[player_name]["total_calls"] += 1
                elif action == ActionType.RAISE:
                    player_stats[player_name]["total_raises"] += 1
                elif action == ActionType.FOLD:
                    player_stats[player_name]["total_folds"] += 1
                elif action == ActionType.CHECK:
                    player_stats[player_name]["total_checks"] += 1
        
        stats["player_statistics"] = player_stats
        
        return stats

    def _initialize_players(self):
        """Initialize the player list with default players."""
        position_names = self._get_position_names()
        self.game_state.players = []
        
        for i in range(self.num_players):
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position=position_names[i],
                is_human=(i == 0),  # First player is human
                is_active=True,
                cards=[],
                current_bet=0.0,
                has_acted_this_round=False,
                is_all_in=False,
                total_invested=0.0
            )
            self.game_state.players.append(player)
        
        # Initialize blind positions after players are created
        self.update_blind_positions()

    def _get_position_names(self) -> List[str]:
        """Get position names based on number of players."""
        if self.num_players == 2:
            return ["BTN/SB", "BB"]
        elif self.num_players == 3:
            return ["BTN", "SB", "BB"]
        elif self.num_players == 6:
            return ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        elif self.num_players == 9:
            return ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "MP+1", "CO", "LJ"]
        else:
            # Generic positions for other sizes
            positions = ["BTN", "SB", "BB"]
            for i in range(3, self.num_players):
                positions.append(f"P{i+1}")
            return positions

    def log_state_change(self, player: Player, action: ActionType, amount: float):
        """Logs the entire game state at the moment of an action."""
        if not self.game_state:
            return

        # Create a simplified snapshot of each player's state
        player_states = [
            {
                "name": p.name,
                "stack": p.stack,
                "current_bet": p.current_bet,
                "is_active": p.is_active,
                "is_all_in": p.is_all_in,
                "is_human": p.is_human,
                "cards": p.cards if p.is_human else []  # Only log human cards for privacy/realism
            }
            for p in self.game_state.players
        ]

        log_entry = HandHistoryLog(
            timestamp=time.time(),
            street=self.game_state.street,
            player_name=player.name,
            action=action,
            amount=amount,
            pot_size=self.game_state.pot,
            board=self.game_state.board.copy(),
            player_states=player_states
        )
        
        # Always append the log entry
        self.hand_history.append(log_entry)
        
        # Also log to action_log for statistics tracking
        self._log_action(player.name, action, amount)
            
        # Also print a simple debug message to the console
        debug_message = f"{player.name}: {action.value.upper()} ${amount:.2f}"
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {debug_message}")

    def _log_action(self, player_name: str, action: ActionType, amount: float):
        """Log a structured action for statistics tracking - FIXED memory management."""
        # Use a more memory-efficient structure
        action_entry = {
            'player_name': player_name,
            'action': action,
            'amount': amount,
            'timestamp': time.time()
        }
        
        # Use deque for efficient memory management
        if not hasattr(self, '_action_deque'):
            from collections import deque
            self._action_deque = deque(maxlen=self.max_log_size)
        
        self._action_deque.append(action_entry)
        
        # Convert to list for compatibility
        self.action_log = list(self._action_deque)
    
    def _log_message(self, message: str):
        """Log a simple message for debugging."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # NEW: Call the UI callback for detailed logging
        if self.on_log_entry:
            self.on_log_entry(message)

    def transition_to(self, new_state: PokerState):
        """Transition to a new state with validation and logging."""
        # FIXED: Add transition lock to prevent concurrent transitions
        if hasattr(self, '_transitioning') and self._transitioning:
            self._log_message(f"WARNING: Transition already in progress, ignoring transition to {new_state.value}")
            return
        
        self._transitioning = True
        try:
            debug_print(f"🔄 DEBUG: Transitioning from {self.current_state.value} to {new_state.value}")
            
            if self.current_state == new_state:
                debug_print(f"🔄 DEBUG: Already in {new_state.value}, no transition needed")
                return

            # Validate transition
            if new_state not in self.STATE_TRANSITIONS.get(self.current_state, []):
                debug_print(f"❌ ERROR: Invalid transition from {self.current_state.value} to {new_state.value}")
                self._log_message(f"Invalid state transition: {self.current_state.value} -> {new_state.value}")
                return

            # Check for active players before END_HAND transition
            if new_state == PokerState.END_HAND:
                active_players = [p for p in self.game_state.players if p.is_active]
                debug_print(f"🔄 DEBUG: END_HAND transition - {len(active_players)} active players")
                if len(active_players) > 1:
                    debug_print(f"🔄 DEBUG: Multiple active players, proceeding to showdown")
                else:
                    debug_print(f"🔄 DEBUG: Single active player, ending hand")

            # Log the transition
            self._log_message(f"State transition: {self.current_state.value} -> {new_state.value}")
            
            # Update state
            old_state = self.current_state
            self.current_state = new_state
            
            # CRITICAL: Notify UI of state change (this was missing!)
            if self.on_state_change:
                debug_print(f"🔄 DEBUG: Calling on_state_change callback")
                self.on_state_change(new_state)
                debug_print(f"✅ DEBUG: on_state_change callback completed")
            else:
                debug_print(f"❌ ERROR: on_state_change callback is None!")
            
            # Call appropriate handler based on state
            if new_state == PokerState.END_HAND:
                debug_print(f"🔄 DEBUG: Calling handle_end_hand")
                self.handle_end_hand()
                debug_print(f"✅ DEBUG: handle_end_hand completed")
            elif new_state == PokerState.SHOWDOWN:
                debug_print(f"🔄 DEBUG: Calling handle_showdown")
                self.handle_showdown()
                debug_print(f"✅ DEBUG: handle_showdown completed")
            else:
                debug_print(f"🔄 DEBUG: Calling handle_state_entry for {new_state.value}")
                self.handle_state_entry()
                debug_print(f"✅ DEBUG: handle_state_entry completed")
            
            # Special handling for END_HAND state
            if new_state == PokerState.END_HAND:
                debug_print(f"🔄 DEBUG: END_HAND state reached, ensuring hand completion")
                # Ensure hand is properly completed
                if hasattr(self, 'logger') and self.logger:
                    debug_print(f"🔄 DEBUG: Logger available, ensuring hand logging completion")
                else:
                    debug_print(f"❌ ERROR: Logger not available for hand completion!")
            
            # Validate state consistency after transition
            self._validate_state_consistency()
            
            debug_print(f"✅ DEBUG: Transition to {new_state.value} completed successfully")
            
        finally:
            self._transitioning = False

    def _validate_state_consistency(self):
        """Validate state consistency after transitions."""
        if not self.game_state:
            return
        
        # Check pot consistency
        total_invested = sum(p.total_invested for p in self.game_state.players)
        if abs(self.game_state.pot - total_invested) > 0.01:
            self._log_message(f"WARNING: Pot inconsistency - Pot: ${self.game_state.pot:.2f}, Invested: ${total_invested:.2f}")
        
        # Check for negative stacks
        for player in self.game_state.players:
            if player.stack < 0:
                self._log_message(f"ERROR: {player.name} has negative stack: ${player.stack:.2f}")
                player.stack = 0  # Fix it
        
        # Check action player validity
        if self.action_player_index >= 0:
            player = self.get_action_player()
            if player and (not player.is_active or player.is_all_in):
                self._log_message(f"ERROR: Invalid action player: {player.name}")
                self.advance_to_next_player()

    def handle_state_entry(self, existing_players: Optional[List[Player]] = None):
        """
        The main handler for all state transitions. Executes the appropriate
        logic based on the current game state.
        """
        debug_print(f"⭐ DEBUG: handle_state_entry() called with current_state={self.current_state}")
        
        handlers = {
            PokerState.START_HAND: lambda: self.handle_start_hand(existing_players),
            PokerState.PREFLOP_BETTING: self.handle_preflop_betting,
            PokerState.DEAL_FLOP: self.handle_deal_flop,
            PokerState.FLOP_BETTING: self.handle_flop_betting,
            PokerState.DEAL_TURN: self.handle_deal_turn,
            PokerState.TURN_BETTING: self.handle_turn_betting,
            PokerState.DEAL_RIVER: self.handle_deal_river,
            PokerState.RIVER_BETTING: self.handle_river_betting,
            PokerState.SHOWDOWN: self.handle_showdown,
            PokerState.END_HAND: self.handle_end_hand,
        }
        
        debug_print(f"⭐ DEBUG: Available handlers: {list(handlers.keys())}")
        debug_print(f"⭐ DEBUG: Looking for handler for {self.current_state}")
        
        handler = handlers.get(self.current_state)
        if handler:
            debug_print(f"⭐ DEBUG: Found handler for {self.current_state}, executing...")
            handler()
            debug_print(f"⭐ DEBUG: Handler for {self.current_state} completed")
        else:
            debug_print(f"❌ DEBUG: NO HANDLER FOUND for {self.current_state}!")

    # FIX 1: Dynamic Position Tracking
    def advance_dealer_position(self):
        """Move dealer button for next hand."""
        self.dealer_position = (self.dealer_position + 1) % self.num_players
        self.update_blind_positions()
        # Update player positions after dealer advance
        if self.game_state:
            self.assign_positions()

    def update_blind_positions(self):
        """Update blind positions based on current dealer position."""
        active_players = [i for i, p in enumerate(self.game_state.players) if p.is_active]
        if len(active_players) < 2:
            # Only log this message if we're not in the middle of a hand completion
            if self.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN]:
                self._log_message("Not enough active players for blinds")
            self.small_blind_position = -1
            self.big_blind_position = -1
            return
        if self.num_players == 2:
            # Heads up: dealer is small blind
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.num_players
        else:
            self.small_blind_position = (self.dealer_position + 1) % self.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.num_players

    def assign_positions(self):
        """Assign positions relative to dealer with proper mapping."""
        # FIXED: Never use generic fallback positions
        positions = self._get_position_names()
        
        # Ensure we have enough position names
        while len(positions) < self.num_players:
            # Add specific positions instead of generic ones
            extra_positions = ["MP+2", "MP+3", "EP", "LP"]
            positions.extend(extra_positions[:self.num_players - len(positions)])
        
        for i in range(self.num_players):
            seat_offset = (i - self.dealer_position) % self.num_players
            self.game_state.players[i].position = positions[seat_offset]
        
        # Validate no generic positions
        for player in self.game_state.players:
            if player.position.startswith('P') and player.position[1:].isdigit():
                # This should never happen now
                self._log_message(f"ERROR: Generic position assigned to {player.name}")
                player.position = "MP"  # Safe fallback

    def _start_logging_session(self):
        """Initialize the comprehensive logging session."""
        try:
            print("DEBUG: Starting logging session...")
            self.session_id = self.logger.start_session(
                num_players=self.num_players,
                starting_stack=100.0  # Default starting stack
            )
            print(f"DEBUG: Session ID created: {self.session_id}")
            self.logger.log_system("INFO", "SYSTEM", "Poker state machine initialized", {
                "num_players": self.num_players,
                "session_id": self.session_id
            })
            print("DEBUG: System log created successfully")
        except Exception as e:
            print(f"Warning: Could not initialize logging: {e}")
            import traceback
            traceback.print_exc()
            self.session_id = None
    
    def _end_logging_session(self):
        """End the current logging session."""
        if self.session_id:
            try:
                self.logger.end_session()
                self.logger.log_system("INFO", "SYSTEM", "Session ended")
            except Exception as e:
                print(f"Warning: Could not end logging session: {e}")
    
    def _register_cleanup(self):
        """Register cleanup handlers for graceful shutdown."""
        import atexit
        import signal
        
        # Register cleanup on normal exit
        atexit.register(self._cleanup)
        
        # Override signal handlers to include state machine cleanup
        original_signal_handler = getattr(self.logger, '_signal_handler', None)
        if original_signal_handler:
            def combined_signal_handler(signum, frame):
                print("🔄 Cleaning up poker state machine...")
                self._cleanup()
                # Call original logger signal handler
                original_signal_handler(signum, frame)
            
            try:
                signal.signal(signal.SIGINT, combined_signal_handler)
                signal.signal(signal.SIGTERM, combined_signal_handler)
            except Exception as e:
                print(f"Warning: Could not override signal handlers: {e}")
    
    def _cleanup(self):
        """Cleanup method called on shutdown."""
        try:
            print("🧹 Cleaning up poker state machine...")
            debug_print(f"🔄 DEBUG: _cleanup() called on object ID = {id(self)}")
            
            # Check if we have an active hand that needs completion
            if (hasattr(self, 'current_state') and 
                self.current_state != PokerState.END_HAND and
                hasattr(self, 'logger') and 
                hasattr(self.logger, 'current_hand') and 
                self.logger.current_hand):
                
                print("📝 Completing current hand due to program termination...")
                debug_print(f"🔄 DEBUG: Current state = {self.current_state.value}")
                debug_print(f"🔄 DEBUG: Logger has current_hand = {self.logger.current_hand is not None}")
                
                # End the current hand gracefully with termination note
                try:
                    active_players = [p for p in self.game_state.players if p.is_active]
                    debug_print(f"🔄 DEBUG: Active players at termination: {[p.name for p in active_players]}")
                    
                    if len(active_players) == 1:
                        winner = active_players[0].name
                        winning_hand = "Session terminated - single active player"
                    else:
                        winner = "Session terminated - multiple active players"
                        winning_hand = "Session terminated - hand incomplete"
                    
                    # Log the incomplete hand with termination note
                    self.logger.end_hand(
                        winner=winner,
                        winning_hand=winning_hand,
                        pot_size=self.game_state.pot,
                        showdown=False
                    )
                    
                    # Add a system log entry about the termination
                    self.logger.log_system(
                        "WARNING", 
                        "SESSION", 
                        "Program terminated before hand completion", 
                        {
                            "current_state": self.current_state.value,
                            "active_players": len(active_players),
                            "pot_size": self.game_state.pot,
                            "board": self.game_state.board,
                            "termination_reason": "User quit (Ctrl+C or Cmd+Q)"
                        }
                    )
                    
                    debug_print(f"✅ DEBUG: Incomplete hand logged successfully")
                    print(f"📝 Hand terminated: {winner} wins ${self.game_state.pot:.2f} (incomplete)")
                    
                except Exception as e:
                    debug_print(f"❌ ERROR: Could not complete current hand: {e}")
                    print(f"Warning: Could not complete current hand: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                debug_print(f"🔄 DEBUG: No active hand to complete")
                print("📝 No active hand to complete")
            
            # End logging session with termination note
            if hasattr(self, 'logger') and self.logger:
                debug_print(f"🔄 DEBUG: Ending logging session")
                self.logger.log_system(
                    "INFO", 
                    "SESSION", 
                    "Session ended by user (Ctrl+C or Cmd+Q)", 
                    {
                        "hands_played": getattr(self.logger.session, 'hands_played', 0) if hasattr(self.logger, 'session') else 0,
                        "session_duration": time.time() - getattr(self.logger.session, 'start_time', time.time()) if hasattr(self.logger, 'session') else 0
                    }
                )
                
                # Call emergency save to ensure all data is saved
                if hasattr(self.logger, '_emergency_save'):
                    self.logger._emergency_save()
                
                self._end_logging_session()
                debug_print(f"✅ DEBUG: Logging session ended successfully")
            else:
                debug_print(f"❌ ERROR: No logger available for session cleanup")
            
            print("✅ Poker state machine cleanup complete")
            debug_print(f"✅ DEBUG: _cleanup() completed successfully")
            
        except Exception as e:
            debug_print(f"❌ ERROR: Error during state machine cleanup: {e}")
            print(f"Warning: Error during state machine cleanup: {e}")
            import traceback
            traceback.print_exc()

    def _cleanup_memory(self):
        """Perform memory cleanup - ENHANCED."""
        # More aggressive memory cleanup
        if hasattr(self, '_action_deque'):
            # Keep only recent actions
            from collections import deque
            recent_actions = list(self._action_deque)[-100:]
            self._action_deque = deque(recent_actions, maxlen=self.max_log_size)
            self.action_log = recent_actions
        
        # Trim hand history
        if len(self.hand_history) > self.max_hand_history:
            self.hand_history = self.hand_history[-self.max_hand_history:]
        
        # Clear old cache entries
        if hasattr(self, '_hand_eval_cache') and len(self._hand_eval_cache) > self._max_cache_size // 2:
            # Keep only most recent half of cache
            cache_items = list(self._hand_eval_cache.items())
            self._hand_eval_cache = dict(cache_items[-self._max_cache_size // 2:])
        
        # Clear session logs if too large
        if self.session_state and len(self.session_state.session_log) > 500:
            self.session_state.session_log = self.session_state.session_log[-500:]
        
        # Force garbage collection
        import gc
        gc.collect()
    
    def _start_hand_logging(self):
        """Start logging for the current hand."""
        debug_print(f"🐛 DEBUG: _start_hand_logging called for hand {self.hand_number}")
        debug_print(f"🐛 DEBUG: session_id = {self.session_id}")
        debug_print(f"🐛 DEBUG: logger object = {self.logger}")
        
        if not self.session_id:
            debug_print("❌ DEBUG: No session_id, skipping hand logging")
            return
            
        try:
            debug_print(f"✅ DEBUG: Starting hand {self.hand_number} logging...")
            # Prepare player data for logging
            players_data = []
            for i, player in enumerate(self.game_state.players):
                players_data.append({
                    "name": player.name,
                    "position": player.position,
                    "stack": player.stack,
                    "is_human": player.is_human,
                    "is_active": player.is_active,
                    "index": i
                })
            
            debug_print(f"🐛 DEBUG: Player data prepared: {len(players_data)} players")
            
            # Find blind positions
            dealer_button = 0  # Will be set properly when we implement button tracking
            small_blind = getattr(self, 'small_blind_position', 0)
            big_blind = getattr(self, 'big_blind_position', 1)
            
            debug_print(f"🐛 DEBUG: About to call logger.start_hand...")
            hand_id = self.logger.start_hand(
                hand_number=self.hand_number,
                players=players_data,
                dealer_button=dealer_button,
                small_blind=small_blind,
                big_blind=big_blind,
                sb_amount=0.5,
                bb_amount=1.0
            )
            
            debug_print(f"✅ DEBUG: Hand started successfully with ID: {hand_id}")
            
            self.logger.log_system("INFO", "HAND", f"Hand {self.hand_number} started", {
                "hand_id": hand_id,
                "players": len(players_data),
                "deck_size": len(self.game_state.deck)
            })
            
            debug_print(f"✅ DEBUG: Hand logging initialization complete")
            
        except Exception as e:
            debug_print(f"❌ ERROR: Could not start hand logging: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
    
    def _log_player_action(self, player: 'Player', action: str, amount: float, 
                          pot_before: float, pot_after: float):
        """Log a player action to the comprehensive logging system."""
        if not self.session_id:
            return
            
        try:
            player_index = self.game_state.players.index(player)
            
            self.logger.start_player_action(player.name)
            self.logger.log_action(
                player_name=player.name,
                player_index=player_index,
                action=action,
                amount=amount,
                stack_before=player.stack + amount if action in ["BET", "CALL", "RAISE"] else player.stack,
                stack_after=player.stack,
                pot_before=pot_before,
                pot_after=pot_after,
                current_bet=self.game_state.current_bet,
                street=self.game_state.street,
                position=player.position,
                is_human=player.is_human
            )
        except Exception as e:
            print(f"Warning: Could not log player action: {e}")

    def create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        suits = ["h", "d", "c", "s"]
        deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
        
        # Ensure proper shuffling with multiple passes
        for _ in range(3):  # Multiple shuffle passes for better randomization
            random.shuffle(deck)
        
        self._log_message(f"🃏 Created and shuffled deck: {len(deck)} cards")
        self._log_message(f"🃏 DEBUG: First 10 cards in new deck: {deck[:10]}")
        self._log_message(f"🃏 DEBUG: Last 5 cards in new deck: {deck[-5:]}")
        
        # Force a different random seed each call to ensure different shuffles
        import time
        random.seed(time.time())
        random.shuffle(deck)  # Extra shuffle with time-based seed
        self._log_message(f"🃏 DEBUG: After extra shuffle, first 10 cards: {deck[:10]}")
        
        return deck

    def deal_card(self) -> str:
        """Deal a single card from the deck."""
        if not self.game_state.deck:
            raise ValueError("No cards left in deck!")
        card = self.game_state.deck.pop()
        valid_ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        valid_suits = ["h", "d", "c", "s"]
        if len(card) != 2 or card[0] not in valid_ranks or card[1] not in valid_suits:
            self._log_message(f"Invalid card dealt: {card}")
            raise ValueError(f"Invalid card: {card}")
        return card

    def handle_start_hand(self, existing_players: Optional[List[Player]] = None):
        """Initialize a new hand with all fixes, using existing players if provided."""
        debug_print(f"🚀 DEBUG: handle_start_hand called - existing_players={len(existing_players) if existing_players else 'None'}")
        self._log_message("Starting new hand")
        
        # FIXED: Add memory cleanup check
        self._hands_since_cleanup += 1
        if self._hands_since_cleanup >= self._memory_check_interval:
            self._cleanup_memory()
            self._hands_since_cleanup = 0
        
        # Increment hand number for logging
        self.hand_number += 1
        debug_print(f"🚀 DEBUG: hand_number incremented to {self.hand_number}")
        
        # --- NEW: Clear the hand history ---
        self.hand_history.clear()

        # Create a fresh, properly shuffled deck
        self._log_message("🃏 Creating fresh deck for new hand")
        deck = self.create_deck()
        self._log_message(f"🃏 New deck created with {len(deck)} cards")
        self._log_message(f"🃏 DEBUG: First 10 cards in new deck: {deck[:10]}")

        # Use existing players or create new ones
        if existing_players:
            players = existing_players
            for player in players:
                # Reset hand-specific attributes
                player.is_active = True
                player.cards = []
                player.current_bet = 0.0  # FIX: Ensure current_bet is reset to 0.0
                player.has_acted_this_round = False
                player.is_all_in = False
                player.total_invested = 0.0  # FIX: Ensure total_invested is reset to 0.0
                player.partial_call_amount = None
                player.full_call_amount = None
        else:
            # Create players if they don't exist
            players = []
            for i in range(self.num_players):
                is_human = i == 0
                player = Player(
                    name=f"Player {i+1}",
                    stack=100.0,
                    position="",  # Will be assigned
                    is_human=is_human,
                    is_active=True,
                    cards=[],
                    current_bet=0.0,
                    has_acted_this_round=False,
                    is_all_in=False,
                    total_invested=0.0,
                )
                players.append(player)

        # Create enhanced game state with fresh board and deck
        self.game_state = GameState(
            players=players,
            board=[],  # Fresh empty board
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=deck,  # Fresh shuffled deck
            min_raise=1.0,
            big_blind=1.0,
        )
        self._log_message(f"🃏 New game state created with fresh board and {len(deck)} cards")
        
        # DEBUG: Verify deck was properly assigned and is different 
        self._log_message(f"🃏 DEBUG: GameState deck assigned, first 5 cards: {self.game_state.deck[:5]}")
        self._log_message(f"🃏 DEBUG: Deck object id: {id(self.game_state.deck)}")

        # Assign positions correctly
        self.assign_positions()
        
        # --- POSITION VALIDATION ---
        # Validate that all players have valid positions using dynamic position names
        valid_positions = self._get_position_names()
        for i, player in enumerate(self.game_state.players):
            if player.position not in valid_positions and not player.position.startswith("P"):
                self._log_message(f"ERROR: Invalid position '{player.position}' for {player.name}")
                player.position = "Unknown"  # Fallback position
        # --- END POSITION VALIDATION ---
        
        debug_print(f"🚀 DEBUG: About to call _start_hand_logging() for hand {self.hand_number}")
        
        # Start comprehensive hand logging
        self._start_hand_logging()
        
        debug_print(f"🚀 DEBUG: _start_hand_logging() completed for hand {self.hand_number}")

        # FIX: Update blind positions BEFORE trying to use them
        self.update_blind_positions()

        # Post blinds with proper tracking
        sb_player = self.game_state.players[self.small_blind_position]
        bb_player = self.game_state.players[self.big_blind_position]

        sb_amount = 0.5
        bb_amount = 1.0

        # Check if players can post blinds
        if sb_player.stack < sb_amount or bb_player.stack < bb_amount:
            self._log_message("Insufficient stacks for blinds; ending game")
            self.transition_to(PokerState.END_HAND)
            return

        # Post blinds
        sb_player.stack -= sb_amount
        sb_player.total_invested = sb_amount
        sb_player.current_bet = sb_amount

        bb_player.stack -= bb_amount
        bb_player.total_invested = bb_amount
        bb_player.current_bet = bb_amount

        # Set game state
        self.game_state.pot = sb_player.total_invested + bb_player.total_invested
        self.game_state.current_bet = bb_amount
        self.game_state.min_raise = bb_amount

        debug_print(f"🚀 DEBUG: About to call deal_hole_cards() for hand {self.hand_number}")
        
        # Deal hole cards with animation
        self.deal_hole_cards()
        
        debug_print(f"🚀 DEBUG: deal_hole_cards() completed for hand {self.hand_number}")

        # --- THIS IS THE FIX ---
        # Set action to UTG (first player after BB) AFTER all setup is complete.
        self.action_player_index = (self.big_blind_position + 1) % self.num_players
        
        # FIX: Ensure all players are active for action order testing
        for player in self.game_state.players:
            player.is_active = True
        # --- End of Fix ---

        # FIXED: Don't transition to preflop betting immediately
        # Wait for dealing animation to complete via callback
        self._log_message("🃏 Waiting for dealing animation to complete before starting betting...")

    def deal_hole_cards(self):
        """Deal hole cards to all players with casino-style one-card-at-a-time dealing."""
        self._log_message("🃏 DEALING HOLE CARDS - Casino Style")
        
        # Create a fresh deck for this hand
        self.game_state.deck = self.create_deck()
        self._log_message(f"🃏 Created fresh deck with {len(self.game_state.deck)} cards")
        
        # Clear all player cards first
        for player in self.game_state.players:
            player.cards = []
        
        # Deal one card at a time to each player (casino style)
        # First round: deal first card to each player
        for player in self.game_state.players:
            card = self.deal_card()
            player.cards.append(card)
            self._log_message(f"🃏 First card to {player.name}: {card}")
            
            # Notify UI of single card dealt
            if hasattr(self, 'on_single_card_dealt'):
                player_index = self.game_state.players.index(player)
                self.on_single_card_dealt(player_index, 0, card)
        
        # Second round: deal second card to each player
        for player in self.game_state.players:
            card = self.deal_card()
            player.cards.append(card)
            self._log_message(f"🃏 Second card to {player.name}: {card}")
            
            # Notify UI of single card dealt
            if hasattr(self, 'on_single_card_dealt'):
                player_index = self.game_state.players.index(player)
                self.on_single_card_dealt(player_index, 1, card)
        
        # Log all hole cards to comprehensive logging system
        try:
            hole_cards = {}
            for player in self.game_state.players:
                hole_cards[player.name] = player.cards
            
            debug_print(f"🐛 DEBUG: About to log hole cards: {hole_cards}")
            debug_print(f"🐛 DEBUG: Logger object: {self.logger}")
            debug_print(f"🐛 DEBUG: Logger type: {type(self.logger)}")
            
            if hasattr(self.logger, 'current_hand'):
                debug_print(f"🐛 DEBUG: Logger current_hand: {self.logger.current_hand}")
            else:
                debug_print(f"❌ ERROR: Logger has no current_hand attribute!")
            
            self.logger.log_hole_cards(hole_cards)
            debug_print(f"✅ DEBUG: Hole cards logged successfully")
            
        except Exception as e:
            debug_print(f"❌ ERROR: Could not log hole cards: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
        
        # Notify UI that dealing is complete and calculate dealing animation time
        # Total cards dealt = players × 2 cards, with delays between each card
        total_cards = len(self.game_state.players) * 2
        total_dealing_time = total_cards * 300 + 1000  # 300ms per card + 1s buffer
        if hasattr(self, 'on_dealing_complete'):
            self.on_dealing_complete(total_dealing_time)

    def start_preflop_betting_after_dealing(self):
        """Start preflop betting after dealing animation is complete."""
        self._log_message("🃏 All cards dealt - starting preflop betting round")
        self.transition_to(PokerState.PREFLOP_BETTING)

    def handle_preflop_betting(self):
        """Handle preflop betting round."""
        self._log_message("Preflop betting round")
        self.game_state.street = "preflop"
        
        # --- NEW: Only reset round tracking, NOT the action player index ---
        # The action player index was already set correctly in handle_start_hand
        self.game_state.players_acted.clear()
        for player in self.game_state.players:
            player.has_acted_this_round = False
        # --- END NEW ---

        # Check if round is complete first (e.g., if all but one player folded during blinds posting)
        # This preserves the fix for hand transition issues
        if self.is_round_complete():
            self._log_message("🔄 Round already complete, transitioning to flop")
            self.transition_to(PokerState.DEAL_FLOP)
        else:
            # Start the action flow - the action player was set correctly in handle_start_hand
            self._log_message("🎯 Starting preflop action flow")
            self.handle_current_player_action()

    def reset_round_tracking(self):
        """Reset tracking for new betting round."""
        self.game_state.players_acted.clear()
        for player in self.game_state.players:
            player.has_acted_this_round = False

    def handle_deal_flop(self):
        """Deal the flop."""

        self._log_message("🎴 DEALING FLOP")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        # Deal 3 community cards
        for i in range(3):
            card = self.deal_card()
            self.game_state.board.append(card)
            self._log_message(f"🎴 Dealt card {i+1}: {card}")

        self._log_message(f"🎴 FLOP COMPLETE: {' '.join(self.game_state.board)}")
        self._log_message(f"📊 Pot before flop betting: ${self.game_state.pot:.2f}")
        
        # Log board cards to comprehensive logging system
        try:
            self.logger.log_board_cards(self.game_state.board, "flop")
        except Exception as e:
            print(f"Warning: Could not log flop cards: {e}")
        
        # FIX: Update street before preparing new betting round
        self.game_state.street = "flop"
        self.prepare_new_betting_round()
        self.transition_to(PokerState.FLOP_BETTING)

    def handle_deal_turn(self):
        """Deal the turn."""

        self._log_message("🎴 DEALING TURN")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        # Deal 1 community card (turn)
        card = self.deal_card()
        self.game_state.board.append(card)
        self._log_message(f"🎴 Dealt turn card: {card}")

        self._log_message(f"🎴 TURN COMPLETE: {' '.join(self.game_state.board)}")
        self._log_message(f"📊 Pot before turn betting: ${self.game_state.pot:.2f}")
        
        # Log board cards to comprehensive logging system
        try:
            self.logger.log_board_cards(self.game_state.board, "turn")
        except Exception as e:
            print(f"Warning: Could not log turn cards: {e}")
        
        # FIX: Update street before preparing new betting round
        self.game_state.street = "turn"
        self.prepare_new_betting_round()
        self.transition_to(PokerState.TURN_BETTING)

    def handle_deal_river(self):
        """Deal the river."""

        self._log_message("🎴 DEALING RIVER")
        
        # Burn card
        if self.game_state.deck:
            self.game_state.deck.pop()

        # Deal 1 community card (river)
        card = self.deal_card()
        self.game_state.board.append(card)
        self._log_message(f"🎴 Dealt river card: {card}")

        self._log_message(f"🎴 RIVER COMPLETE: {' '.join(self.game_state.board)}")
        self._log_message(f"📊 Pot before river betting: ${self.game_state.pot:.2f}")
        
        # Log board cards to comprehensive logging system
        try:
            self.logger.log_board_cards(self.game_state.board, "river")
        except Exception as e:
            print(f"Warning: Could not log river cards: {e}")
        
        # FIX: Update street before preparing new betting round
        self.game_state.street = "river"
        self.prepare_new_betting_round()
        self.transition_to(PokerState.RIVER_BETTING)

    def prepare_new_betting_round(self):
        """
        Resets bets for the new round and finds the correct first player to act.
        Post-flop, action starts with the first active player left of the dealer.
        """
        # Add street transition announcement
        street_names = {
            'preflop': 'PREFLOP',
            'flop': 'FLOP',
            'turn': 'TURN', 
            'river': 'RIVER'
        }
        street_name = street_names.get(self.game_state.street, self.game_state.street.upper())
        self._log_message(f"🔄 TRANSITIONING TO {street_name} BETTING")
        self._log_message(f"📊 Pot: ${self.game_state.pot:.2f}")
        
        # Reset game state for new round
        self.game_state.current_bet = 0.0
        self.game_state.min_raise = self.game_state.big_blind  # Reset to big blind
        self.reset_round_tracking()

        # Reset bets and action flags for all players
        for p in self.game_state.players:
            p.current_bet = 0
            p.has_acted_this_round = False

        # Find the correct first player to act
        num_players = len(self.game_state.players)
        
        # In pre-flop, the player after the Big Blind acts first.
        if self.game_state.street == 'preflop':
            start_index = (self.big_blind_position + 1) % num_players
        # Post-flop, the first active player to the left of the dealer acts first.
        else:
            start_index = (self.dealer_position + 1) % num_players

        # Find the first active player starting from the calculated start_index
        # FIX: Ensure we follow the correct action order by checking all players in order
        checked_indices = set()
        for i in range(num_players):
            current_index = (start_index + i) % num_players
            if current_index in checked_indices:
                continue  # Skip if we've already checked this index
            checked_indices.add(current_index)
            
            player_at_index = self.game_state.players[current_index]
            if player_at_index.is_active and not player_at_index.is_all_in:
                self.action_player_index = current_index
                self._log_message(f"🎯 Action starts with {player_at_index.name} in seat {current_index}.")
                return

        # If no player can act, something is wrong. Log it.
        self._log_message("ERROR: Could not find any active player to start the betting round.")

    def set_action_to_first_active_after_button(self):
        """Set action to first active player after button."""
        for i in range(1, self.num_players):
            player_index = (self.dealer_position + i) % self.num_players
            player = self.game_state.players[player_index]
            if player.is_active and not player.is_all_in:
                self.action_player_index = player_index
                return
        
        # If no one can act, round is complete
        self.action_player_index = -1

    def handle_flop_betting(self):
        """Handle flop betting round."""
        self._log_message("Flop betting round")
        self.game_state.street = "flop"
        self._handle_betting_round(PokerState.DEAL_TURN)

    def handle_turn_betting(self):
        """Handle turn betting round."""
        self._log_message("Turn betting round")
        self.game_state.street = "turn"
        self._handle_betting_round(PokerState.DEAL_RIVER)

    def handle_river_betting(self):
        """Handle river betting round."""
        self._log_message("River betting round")
        self.game_state.street = "river"
        self._handle_betting_round(PokerState.SHOWDOWN)

    def _handle_betting_round(self, next_state: PokerState):
        """Generic betting round handler."""
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) <= 1:
            self.transition_to(PokerState.END_HAND)
            return

        if self.is_round_complete():
            self.handle_round_complete()
        else:
            self.handle_current_player_action()

    # FIX 4: Improved Round Completion Logic
    def is_round_complete(self) -> bool:
        """
        Checks if the betting round is complete with robust logic.
        The round is over if all active players who are not all-in have had a turn
        and have contributed the same amount to the pot in this round.
        """
        active_players = [p for p in self.game_state.players if p.is_active]
        self._log_message(f"🔍 ROUND_COMPLETE_CHECK: {len(active_players)} active players")
        
        if len(active_players) <= 1:
            self._log_message("✅ Round complete: ≤1 active players")
            return True

        # Identify players who can still make a move
        players_who_can_act = [p for p in active_players if not p.is_all_in]
        self._log_message(f"🔍 Players who can act: {[p.name for p in players_who_can_act]}")
        
        if not players_who_can_act:
            self._log_message("✅ Round complete: Everyone is all-in")
            return True # Round is over if everyone is all-in

        # Check if everyone who can act has had their turn
        all_have_acted = all(p.has_acted_this_round for p in players_who_can_act)
        self._log_message(f"🔍 All have acted: {all_have_acted}")
        for p in players_who_can_act:
            self._log_message(f"   {p.name}: has_acted={p.has_acted_this_round}")
        
        # Find the highest bet made by any player still in the hand
        highest_bet = max(p.current_bet for p in active_players)
        self._log_message(f"🔍 Highest bet: ${highest_bet:.2f}")

        # Check if all players who can act have matched the highest bet
        self._log_message(f"🔍 Checking bet equality against highest bet ${highest_bet:.2f}:")
        bet_check_results = []
        for p in players_who_can_act:
            meets_bet = p.current_bet == highest_bet or (p.is_all_in and p.partial_call_amount is not None)
            bet_check_results.append(meets_bet)
            self._log_message(f"   {p.name}: bet=${p.current_bet:.2f}, meets_requirement={meets_bet}")
        
        bets_are_equal = all(bet_check_results)
        self._log_message(f"🔍 Bets are equal: {bets_are_equal} (all results: {bet_check_results})")
        
        # Special case: If BB is the only active player and hasn't acted yet, round is not complete
        if len(active_players) == 1 and active_players[0].position == "BB" and not active_players[0].has_acted_this_round:
            self._log_message("❌ Round not complete: BB hasn't acted yet")
            return False
        
        # The round is complete if everyone has acted and all bets are equal
        is_complete = all_have_acted and bets_are_equal
        self._log_message(f"🔍 FINAL RESULT: Round complete = {is_complete}")
        return is_complete

    def handle_current_player_action(self):
        """Handle the current player's action with a delay for bots."""
        self._log_message(f"🎯 HANDLE_CURRENT_PLAYER_ACTION: Current state = {self.current_state.value}")
        
        if self.current_state == PokerState.END_HAND:
            self._log_message("🚨 Current state is END_HAND, returning early")
            return

        current_player = self.get_action_player()
        self._log_message(f"🎯 Action player index: {self.action_player_index}")
        
        if not current_player:
            self._log_message("⚠️ No current action player found")
            # This can happen if all remaining players are all-in
            if self.is_round_complete():
                self._log_message("🔄 Round is complete, handling round completion")
                self.handle_round_complete()
            else:
                self._log_message("⏸️ Round not complete but no action player - potential issue!")
            return

        self._log_message(f"🎯 ACTION TURN: Player at index {self.action_player_index} ({current_player.name})")
        self._log_message(f"   👤 Human: {current_player.is_human}, Active: {current_player.is_active}, All-in: {current_player.is_all_in}")
        self._log_message(f"   💰 Stack: ${current_player.stack:.2f}, Current bet: ${current_player.current_bet:.2f}")
        self._log_message(f"   🎲 Has acted this round: {current_player.has_acted_this_round}")

        # Call the action player changed callback for both human and bot players
        if self.on_action_player_changed:
            self.on_action_player_changed(current_player)

        if current_player.is_human:
            self._log_message(f"👨 HUMAN TURN: {current_player.name}")
            if self.on_action_required:
                self.on_action_required(current_player)
        else:
            self._log_message(f"🤖 BOT TURN: {current_player.name}")
            if self.root_tk:
                # Capture all necessary state to prevent race conditions
                bot_action_data = {
                    'player_index': self.action_player_index,
                    'state': self.current_state,
                    'street': self.game_state.street,
                    'pot': self.game_state.pot,
                    'current_bet': self.game_state.current_bet
                }
                self._log_message(f"⏰ Scheduling bot action in 500ms for {current_player.name}")
                self.root_tk.after(500, lambda: self._execute_bot_action_safe(bot_action_data))  # Reduced delay to 500ms for faster bot play
            else:
                self._log_message(f"🚀 Executing bot action immediately for {current_player.name}")
                self.execute_bot_action(current_player)
    
    def _execute_bot_action_safe(self, action_data: dict):
        """Safely execute bot action with state validation."""
        self._log_message(f"⏰ SAFE_BOT_ACTION: Executing scheduled action for player index {action_data['player_index']}")
        
        # BUG FIX: Enhanced race condition protection with atomic state check
        current_state_snapshot = {
            'state': self.current_state,
            'player_index': self.action_player_index,
            'timestamp': time.time()
        }
        
        # Validate state hasn't changed since action was scheduled
        if (current_state_snapshot['state'] != action_data['state'] or
            current_state_snapshot['player_index'] != action_data['player_index']):
            self._log_message(f"❌ Bot action cancelled - game state changed:")
            self._log_message(f"   Expected state: {action_data['state']}, Current: {current_state_snapshot['state']}")
            self._log_message(f"   Expected player index: {action_data['player_index']}, Current: {current_state_snapshot['player_index']}")
            return
        
        # BUG FIX: Additional validation to prevent race conditions
        if self.current_state == PokerState.END_HAND:
            self._log_message(f"❌ Bot action cancelled - hand has ended")
            return
        
        # Validate player still exists and is active
        if action_data['player_index'] >= len(self.game_state.players):
            self._log_message(f"❌ Bot action cancelled - player index {action_data['player_index']} no longer exists")
            return
        
        player = self.game_state.players[action_data['player_index']]
        if not player.is_active:
            self._log_message(f"❌ Bot action cancelled - {player.name} no longer active")
            return
        
        # BUG FIX: Final atomic check before execution
        if (self.current_state != current_state_snapshot['state'] or
            self.action_player_index != current_state_snapshot['player_index']):
            self._log_message(f"❌ Bot action cancelled - state changed during validation")
            return
        
        self._log_message(f"✅ State validation passed, executing bot action for {player.name}")
        self.execute_bot_action(player)

    # FIX 5: Strategy Integration for Bots
    def execute_bot_action(self, player: Player):
        """Execute bot action using strategy data."""
        # FIXED: Add state validation before bot action
        if self.current_state == PokerState.END_HAND:
            self._log_message("Bot action cancelled - hand ended")
            return
        
        # Validate player is still the action player
        current_action_player = self.get_action_player()
        if current_action_player != player:
            self._log_message(f"Bot action cancelled - not {player.name}'s turn anymore")
            return
        
        # Validate player can still act
        if not player.is_active or player.is_all_in:
            self._log_message(f"Bot action cancelled - {player.name} cannot act")
            return
        
        # --- ENHANCED DEBUG LOGGING ---
        self._log_message(f"🤖 Bot {player.name} ({player.position}) is taking action")
        self._log_message(f"   📊 Player state: Stack=${player.stack:.2f}, Bet=${player.current_bet:.2f}")
        self._log_message(f"   🎴 Cards: {player.cards}")
        self._log_message(f"   🃏 Board: {self.game_state.board}")
        self._log_message(f"   💰 Pot: ${self.game_state.pot:.2f}, Current bet: ${self.game_state.current_bet:.2f}")
        self._log_message(f"   🎯 Street: {self.game_state.street}")
        
        # Log strategy data availability
        if self.strategy_data:
            self._log_message(f"   📋 Using strategy data: {type(self.strategy_data).__name__}")
            action, amount = self.get_strategy_action(player)
        else:
            self._log_message(f"   ⚠️ No strategy data available, using basic logic")
            action, amount = self.get_basic_bot_action(player)
        
        # Log the decision with detailed context
        self._log_message(f"🤖 Bot {player.name} decided: {action.value} ${amount:.2f}")
        self._log_message(f"   ✅ Executing action: {action.value} ${amount:.2f}")
        # --- END ENHANCED DEBUG LOGGING ---
        
        self.execute_action(player, action, amount)

    def get_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get bot action using enhanced strategy integration with position mapping."""
        try:
            # Use enhanced strategy integration if available
            if self.strategy_integration:
                return self._get_enhanced_strategy_action(player)
            else:
                return self._get_basic_strategy_action(player)
        except Exception as e:
            self._log_message(f"❌ Strategy error: {e}, using emergency fallback")
            return self._get_emergency_fallback_action(player)
    
    def _get_enhanced_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get bot action using enhanced strategy integration."""
        street = self.game_state.street
        position = player.position
        call_amount = self.game_state.current_bet - player.current_bet
        
        self._log_message(f"🤖 Getting enhanced strategy for {player.name} ({position}) on {street}")
        
        if street == "preflop":
            return self._get_preflop_strategy_action(player)
        else:
            return self._get_postflop_strategy_action(player)
    
    def _get_preflop_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get preflop action with enhanced position mapping."""
        call_amount = self.game_state.current_bet - player.current_bet
        hand_notation = self.get_hand_notation(player.cards)
        
        # Get hand strength using enhanced strategy integration
        hand_strength_tables = self.strategy_data.strategy_dict.get("hand_strength_tables", {})
        preflop_strengths = hand_strength_tables.get("preflop", {})
        hand_strength = preflop_strengths.get(hand_notation, 1)
        
        self._log_message(f"📊 Hand: {hand_notation}, Strength: {hand_strength}")
        
        # Special handling for BB when no raise has been made
        if player.position == "BB" and call_amount == 0:
            self._log_message(f"🎯 BB with no raise, checking")
            return ActionType.CHECK, 0
        
        if call_amount > 0:  # Facing a raise
            strategy = self.strategy_integration.get_strategy_for_position(
                player.position, "preflop", "vs_raise"
            )
            return self._apply_vs_raise_strategy(player, hand_strength, call_amount, strategy)
        else:  # Opening action
            strategy = self.strategy_integration.get_strategy_for_position(
                player.position, "preflop", "open"
            )
            return self._apply_open_strategy(player, hand_strength, strategy)
    
    def _get_postflop_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Get postflop action with enhanced position mapping."""
        # For now, use basic postflop logic
        return self.get_basic_bot_action(player)
    
    def _apply_vs_raise_strategy(self, player: Player, hand_strength: int, 
                                 call_amount: float, strategy: Dict) -> Tuple[ActionType, float]:
        """Apply strategy when facing a raise."""
        value_thresh = strategy.get("value_thresh", 75)
        call_thresh = strategy.get("call_thresh", 65)
        sizing = strategy.get("sizing", 3.0)
        
        self._log_message(f"📊 3bet threshold: {value_thresh}, call threshold: {call_thresh}")
        
        if hand_strength >= value_thresh:
            self._log_message(f"🚀 3-betting with strong hand")
            # FIXED: Calculate raise_to consistently and ensure minimum raise is met
            suggested_raise_by = sizing * self.game_state.big_blind
            min_raise_by = self.game_state.min_raise
            actual_raise_by = max(suggested_raise_by, min_raise_by)
            raise_to = self.game_state.current_bet + actual_raise_by
            # Cap at player's available stack
            max_raise_to = player.current_bet + player.stack
            final_raise_to = min(raise_to, max_raise_to)
            self._log_message(f"💰 Calculating 3bet: suggested_raise_by=${suggested_raise_by:.2f}, min_raise_by=${min_raise_by:.2f}, raise_to=${final_raise_to:.2f}")
            return ActionType.RAISE, final_raise_to
        elif hand_strength >= call_thresh:
            self._log_message(f"📞 Calling with medium hand")
            return ActionType.CALL, call_amount
        else:
            self._log_message(f"❌ Folding to raise")
            return ActionType.FOLD, 0
    
    def _apply_open_strategy(self, player: Player, hand_strength: int, 
                             strategy: Dict) -> Tuple[ActionType, float]:
        """Apply strategy when opening action."""
        threshold = strategy.get("threshold", 50)
        sizing = strategy.get("sizing", 3.0)
        
        self._log_message(f"📊 Opening threshold: {threshold}, sizing: {sizing}")
        
        if hand_strength >= threshold:
            self._log_message(f"🚀 Opening with strong hand")
            # FIXED: Calculate raise_to consistently
            if self.game_state.current_bet == 0:
                # Opening bet
                bet_amount = min(self.game_state.big_blind * sizing, player.stack)
                return ActionType.BET, bet_amount
            else:
                # Raising over existing bet
                suggested_raise_by = sizing * self.game_state.big_blind
                min_raise_by = self.game_state.min_raise
                actual_raise_by = max(suggested_raise_by, min_raise_by)
                raise_to = self.game_state.current_bet + actual_raise_by
                max_raise_to = player.current_bet + player.stack
                final_raise_to = min(raise_to, max_raise_to)
                return ActionType.RAISE, final_raise_to
        else:
            self._log_message(f"❌ Folding weak hand")
            return ActionType.FOLD, 0
    
    def _get_basic_strategy_action(self, player: Player) -> Tuple[ActionType, float]:
        """Fallback to basic strategy when enhanced integration is not available."""
        street = self.game_state.street
        position = player.position
        call_amount = self.game_state.current_bet - player.current_bet
        
        self._log_message(f"🤖 BOT ACTION DEBUG for {player.name} ({position}):")
        self._log_message(f"   Current bet: ${self.game_state.current_bet}, Player bet: ${player.current_bet}")
        self._log_message(f"   Call amount: ${call_amount}")
        self._log_message(f"   Street: {street}")
        self._log_message(f"   Position: {position}")
        
        # --- HANDLE UNKNOWN POSITION ---
        if position == "Unknown" or position not in ["UTG", "MP", "CO", "BTN", "SB", "BB"]:
            self._log_message(f"   ⚠️ Unknown position '{position}', using default logic")
            return self.get_basic_bot_action(player)
    
    def _get_emergency_fallback_action(self, player: Player) -> Tuple[ActionType, float]:
        """Emergency fallback when all else fails."""
        call_amount = self.game_state.current_bet - player.current_bet
        
        # Ultra-conservative strategy
        if call_amount > player.stack * 0.1:  # More than 10% of stack
            return ActionType.FOLD, 0
        elif call_amount > 0:
            return ActionType.CALL, call_amount
        else:
            return ActionType.CHECK, 0
        
        try:
            if street == "preflop":
                # BB check logic for no raise - BB has already paid the big blind
                if position == "BB" and call_amount == 0:
                    self._log_message(f"BB with no raise, checking")
                    return ActionType.CHECK, 0
                
                # BB facing a raise - special handling
                if position == "BB" and call_amount > 0:
                    player_hand_str = self.get_hand_notation(player.cards)
                    self._log_message(f"   🎴 Hand notation: {player_hand_str}")
                    self._log_message(f"   🃏 Hand: {' '.join(player.cards)} ({player_hand_str})")
                    
                    # Get hand strength directly from strategy_dict
                    hand_strength = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("preflop", {}).get(player_hand_str, 1)
                    self._log_message(f"   💪 Hand strength: {hand_strength}")
                    
                    # BB vs raise rules
                    vs_raise_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("vs_raise", {}).get("BB", {})
                    value_3bet_thresh = vs_raise_rules.get("value_thresh", 75)
                    call_thresh = vs_raise_rules.get("call_thresh", 60)  # BB is more likely to call
                    
                    self._log_message(f"   🎯 BB LOGIC: Facing a raise")
                    self._log_message(f"   📊 3bet threshold: {value_3bet_thresh}, call threshold: {call_thresh}")
                    
                    if hand_strength >= value_3bet_thresh:
                        self._log_message(f"   🚀 BB 3-betting with strong hand")
                        return ActionType.RAISE, min(self.game_state.current_bet * 3.0, player.stack)
                    elif hand_strength >= call_thresh:
                        self._log_message(f"   📞 BB calling with medium hand")
                        return ActionType.CALL, call_amount
                    else:
                        self._log_message(f"   ❌ BB folding to raise")
                        return ActionType.FOLD, 0
                
                player_hand_str = self.get_hand_notation(player.cards)
                self._log_message(f"   🎴 Hand notation: {player_hand_str}")
                self._log_message(f"   🃏 Hand: {' '.join(player.cards)} ({player_hand_str})")
                
                # Get hand strength directly from strategy_dict
                hand_strength = self.strategy_data.strategy_dict.get("preflop", {}).get(player_hand_str, 1)
                self._log_message(f"   💪 Hand strength: {hand_strength}")
                
                # If facing a raise (call_amount > 0)
                if call_amount > 0:
                    self._log_message(f"   🎯 LOGIC: Facing a raise")
                    vs_raise_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("vs_raise", {}).get(position, {})
                    value_3bet_thresh = vs_raise_rules.get("value_thresh", 75)
                    call_thresh = vs_raise_rules.get("call_thresh", 65)
                    sizing = vs_raise_rules.get("sizing", 3.0)
                    
                    self._log_message(f"   📊 3bet threshold: {value_3bet_thresh}, call threshold: {call_thresh}")
                    
                    if hand_strength >= value_3bet_thresh:
                        self._log_message(f"   🚀 3-betting with strong hand")
                        return ActionType.RAISE, min(self.game_state.current_bet * sizing, player.stack)
                    elif hand_strength >= call_thresh:
                        self._log_message(f"   📞 Calling with medium hand")
                        return ActionType.CALL, call_amount
                    else:
                        self._log_message(f"   ❌ Folding to raise")
                        return ActionType.FOLD, 0
                else:
                    open_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("open_rules", {})
                    threshold = open_rules.get(position, {}).get("threshold", 60)
                    sizing = open_rules.get(position, {}).get("sizing", 3.0)
                    
                    self._log_message(f"   📊 Opening threshold: {threshold}, sizing: {sizing}")
                    
                    limpers = len([p for p in self.game_state.players 
                                  if p.current_bet == self.game_state.big_blind and p.position != "BB"])
                    if limpers > 0:
                        sizing += limpers
                        self._log_message(f"   👥 Adjusted sizing for {limpers} limpers: {sizing}")
                    
                    if hand_strength >= threshold:
                        action = ActionType.RAISE if self.game_state.current_bet > 0 else ActionType.BET
                        self._log_message(f"   🚀 {action.value} with strong hand")
                        return action, min(sizing, player.stack)
                    self._log_message(f"   ✅ Checking with weak hand")
                    return ActionType.CHECK, 0
            else:  # Postflop logic
                self._log_message(f"   🎯 POSTFLOP LOGIC: {street}")
                hand_type = self.classify_hand(player.cards, self.game_state.board)
                hand_strength = self.strategy_data.strategy_dict.get("postflop", {}).get(hand_type, 5)
                pfa_data = self.strategy_data.strategy_dict.get("postflop", {}).get("pfa", {}).get(street, {}).get(position, {})
                val_thresh = pfa_data.get("val_thresh", 25)
                check_thresh = pfa_data.get("check_thresh", 10)
                sizing = pfa_data.get("sizing", 0.75)
                
                self._log_message(f"   📊 Postflop hand: {hand_type}, strength: {hand_strength}, val: {val_thresh}, check: {check_thresh}")
                
                if call_amount > 0:
                    pot_odds = self.calculate_pot_odds(call_amount)
                    if self.should_call_by_pot_odds(player, call_amount, hand_strength):
                        self._log_message(f"   📞 Calling based on pot odds")
                        return ActionType.CALL, call_amount
                    self._log_message(f"   ❌ Folding based on pot odds")
                    return ActionType.FOLD, 0
                
                if hand_strength >= val_thresh:
                    bet_amount = min(self.game_state.pot * sizing, player.stack)
                    self._log_message(f"   💰 Betting with strong hand: ${bet_amount}")
                    return ActionType.BET, bet_amount
                elif hand_strength >= check_thresh:
                    self._log_message(f"   ✅ Checking with medium hand")
                    return ActionType.CHECK, 0
                self._log_message(f"   ✅ Checking weak hands postflop")
                return ActionType.CHECK, 0
        except (KeyError, AttributeError) as e:
            self._log_message(f"   🤖 Strategy error: {e}, falling back to basic logic")
            return self.get_basic_bot_action(player)

    def get_hand_notation(self, cards: List[str]) -> str:
        """Converts two cards into standard poker notation (e.g., AKs, T9o, 77)."""
        if len(cards) != 2:
            return ""

        try:
            rank1, suit1 = cards[0][0], cards[0][1]
            rank2, suit2 = cards[1][0], cards[1][1]

            # Added validation for rank characters
            rank_order = "AKQJT98765432"
            if rank1 not in rank_order or rank2 not in rank_order:
                return ""  # Return empty for invalid ranks

            if rank1 == rank2:
                return f"{rank1}{rank2}"
            else:
                suited = "s" if suit1 == suit2 else "o"
                if rank_order.index(rank1) < rank_order.index(rank2):
                    return f"{rank1}{rank2}{suited}"
                else:
                    return f"{rank2}{rank1}{suited}"
        except (ValueError, IndexError):
            # Catch any other parsing errors
            return ""

    def is_hand_in_range(self, hand: str, range_list: List[str]) -> bool:
        """Check if a hand is in a given range using compact notation."""
        if not hand or not range_list:
            return False
        
        # Parse the hand (e.g., 'AKs', 'AKs', '72o')
        if len(hand) < 2:
            return False
        
        # Check each range entry
        for range_entry in range_list:
            if self._hand_matches_range_entry(hand, range_entry):
                return True
        
        return False

    def _hand_matches_range_entry(self, hand: str, range_entry: str) -> bool:
        """Check if a hand matches a specific range entry."""
        # Handle individual hands
        if len(range_entry) < 4:  # Single hand like 'AKs', '72o'
            return hand == range_entry
        
        # Handle ranges like 'AA-88', 'AKs-AJs'
        if '-' in range_entry:
            expanded_range = self._expand_range(range_entry)
            return hand in expanded_range
        
        # Handle plus notation like 'AJo+'
        if range_entry.endswith('+'):
            expanded_range = self._expand_plus_range(range_entry)
            return hand in expanded_range
        
        return False

    def _expand_range(self, range_str: str) -> List[str]:
        """Expand a range like 'AA-88' to ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88']."""
        if '-' not in range_str:
            return [range_str]
        
        parts = range_str.split('-')
        if len(parts) != 2:
            return [range_str]
        
        start, end = parts[0], parts[1]
        # Handle pairs (AA, KK, etc.)
        if len(start) == 2 and start[0] == start[1]:
            return self._expand_pair_range(start, end)
        
        # Handle suited hands (AKs, AQs, etc.)
        if start.endswith('s') and end.endswith('s'):
            return self._expand_suited_range(start, end)
        
        # Handle offsuit hands (AKo, AQo, etc.)
        if start.endswith('o') and end.endswith('o'):
            return self._expand_offsuit_range(start, end)
        
        return [range_str]  # Fallback

    def _expand_pair_range(self, start: str, end: str) -> List[str]:
        """Expand pair range like 'AA-88'."""
        ranks = 'AKQJT98765432'
        start_rank = start[0]
        end_rank = end[0]
        
        try:
            start_idx = ranks.index(start_rank)
            end_idx = ranks.index(end_rank)
            result = []
            for i in range(start_idx, end_idx + 1):
                rank = ranks[i]
                result.append(rank + rank)
            return result
        except ValueError:
            return [start, end]

    def _expand_suited_range(self, start: str, end: str) -> List[str]:
        """Expand suited range like 'AKs-AJs'."""
        ranks = 'AKQJT98765432'
        start_rank1, start_rank2 = start[0], start[1]
        end_rank1, end_rank2 = end[0], end[1]
        
        try:
            start_idx1 = ranks.index(start_rank1)
            start_idx2 = ranks.index(start_rank2)
            end_idx1 = ranks.index(end_rank1)
            end_idx2 = ranks.index(end_rank2)
            
            result = []
            # For suited ranges, we need to handle the case where first rank stays same
            # and second rank changes (e.g., AKs-AJs means A stays, K->J)
            if start_rank1 == end_rank1:
                # Same first rank, expand second rank
                for j in range(start_idx2, end_idx2 + 1):
                    rank1, rank2 = start_rank1, ranks[j]
                    result.append(rank1 + rank2 + 's')
            else:
                # Generate all combinations between start and end
                for i in range(start_idx1, end_idx1 + 1):
                    for j in range(start_idx2, end_idx2 + 1):
                        if i >= j:  # Higher rank first or equal
                            rank1, rank2 = ranks[i], ranks[j]
                            result.append(rank1 + rank2 + 's')
            return result
        except ValueError as e:
            return [start, end]

    def _expand_offsuit_range(self, start: str, end: str) -> List[str]:
        """Expand offsuit range like 'AKo-AJo'."""
        ranks = 'AKQJT98765432'
        start_rank1, start_rank2 = start[0], start[1]
        end_rank1, end_rank2 = end[0], end[1]
        
        try:
            start_idx1 = ranks.index(start_rank1)
            start_idx2 = ranks.index(start_rank2)
            end_idx1 = ranks.index(end_rank1)
            end_idx2 = ranks.index(end_rank2)
            
            result = []
            for i in range(start_idx1, end_idx1 + 1):
                for j in range(start_idx2, end_idx2 + 1):
                    if i > j:  # Higher rank first
                        rank1, rank2 = ranks[i], ranks[j]
                        result.append(rank1 + rank2 + 'o')
            return result
        except ValueError:
            return [start, end]

    def _expand_plus_range(self, range_str: str) -> List[str]:
        """Expand plus range like 'AJo+'."""
        if not range_str.endswith('+'):
            return [range_str]
        
        base = range_str[:-1]
        ranks = 'AKQJT98765432'
        
        # Handle AJo+ -> AJo, AQo, AKo
        if base.startswith('A') and base.endswith('o'):
            second_rank = base[1]
            try:
                second_idx = ranks.index(second_rank)
                result = []
                # Go from current rank up to K (index 1)
                for i in range(second_idx, 0, -1):  # Go backwards from J to K (include K)
                    if ranks[i] != 'A':  # Avoid AA
                        result.append('A' + ranks[i] + 'o')
                return result
            except ValueError:
                return [base]
        
        # Handle KJo+ -> KJo, KQo, KKo
        if base.startswith('K') and base.endswith('o'):
            second_rank = base[1]
            try:
                second_idx = ranks.index(second_rank)
                result = []
                for i in range(second_idx, len(ranks)):
                    if ranks[i] != 'K':  # Avoid KK
                        result.append('K' + ranks[i] + 'o')
                return result
            except ValueError:
                return [base]
        
        # Handle pairs like QQ+ -> QQ, KK, AA
        if len(base) == 2 and base[0] == base[1]:
            rank = base[0]
            try:
                rank_idx = ranks.index(rank)
                result = []
                for i in range(rank_idx, 3):  # Up to AA (index 0,1,2)
                    result.append(ranks[i] + ranks[i])
                return result
            except ValueError:
                return [base]
        
        return [base]  # Fallback

    def _hand_in_range(self, hand: str, start_hand: str, end_hand: str) -> bool:
        """Check if hand is between start_hand and end_hand."""
        hand_strength = self._get_hand_strength_value(hand)
        start_strength = self._get_hand_strength_value(start_hand)
        end_strength = self._get_hand_strength_value(end_hand)
        
        return start_strength >= hand_strength >= end_strength

    def _hand_stronger_than_or_equal(self, hand: str, base_hand: str) -> bool:
        """Check if hand is stronger than or equal to base_hand."""
        hand_strength = self._get_hand_strength_value(hand)
        base_strength = self._get_hand_strength_value(base_hand)
        
        return hand_strength >= base_strength

    def _get_hand_strength_value(self, hand: str) -> int:
        """Get numeric strength value for hand comparison."""
        if len(hand) < 2:
            return 0
        
        # Parse hand components
        rank1 = hand[0]
        rank2 = hand[1]
        suited = hand.endswith('s')
        
        # Rank values
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        val1 = rank_values.get(rank1, 0)
        val2 = rank_values.get(rank2, 0)
        
        # Sort by rank (higher first)
        if val1 < val2:
            val1, val2 = val2, val1
        
        # Calculate strength (pairs are strongest, then suited, then offsuit)
        if val1 == val2:  # Pair
            return 1000 + val1 * 10
        elif suited:  # Suited
            return 100 + val1 * 10 + val2
        else:  # Offsuit
            return val1 * 10 + val2

    def classify_board_texture(self, board: List[str]) -> Dict:
        if not board:
            return {"type": "preflop", "wetness": 0, "dynamism": 0, "max_suit_count": 0}
        
        ranks = sorted([self.hand_evaluator.rank_values[card[0]] for card in board], reverse=True)
        suits = [card[1] for card in board]
        max_suit_count = max(suits.count(s) for s in set(suits))
        
        # Wetness: Flush potential (suits)
        wetness = max_suit_count / len(board)
        
        # Dynamism: Straight potential (connectedness)
        connectedness = 0
        for i in range(len(ranks) - 1):
            diff = ranks[i] - ranks[i+1]
            connectedness += 1 if diff <= 2 else 0.5 if diff <= 4 else 0
        dynamism = connectedness / (len(ranks) - 1)
        
        if max_suit_count >= 3:
            type_ = "wet_flush"
        elif connectedness >= 2:  # More connected = wet straight
            type_ = "wet_straight"
        elif wetness >= 0.7 or dynamism >= 0.6 or max(ranks) >= 10:  # High wetness, dynamism, or high cards
            type_ = "medium"
        else:
            type_ = "dry"
        
        return {"type": type_, "wetness": wetness, "dynamism": dynamism, "max_suit_count": max_suit_count}

    def get_preflop_hand_strength(self, cards: List[str]) -> int:
        """Get preflop hand strength using enhanced evaluator."""
        cache_key = f"preflop:{':'.join(sorted(cards))}"
        if cache_key in self._hand_eval_cache:
            self._cache_hits += 1
            return self._hand_eval_cache[cache_key]
        strength = self.hand_evaluator.get_preflop_hand_strength(cards)
        self._hand_eval_cache[cache_key] = strength
        self._cache_misses += 1
        if len(self._hand_eval_cache) > self._max_cache_size:
            self._hand_eval_cache.pop(next(iter(self._hand_eval_cache)))
        return strength

    def get_postflop_hand_strength(self, cards: List[str], board: List[str]) -> int:
        """Get postflop hand strength using enhanced evaluator."""
        cache_key = f"postflop:{':'.join(sorted(cards + board))}"
        if cache_key in self._hand_eval_cache:
            self._cache_hits += 1
            return self._hand_eval_cache[cache_key]
        evaluation = self.hand_evaluator.evaluate_hand(cards, board)
        strength = evaluation['strength_score']
        self._hand_eval_cache[cache_key] = strength
        self._cache_misses += 1
        if len(self._hand_eval_cache) > self._max_cache_size:
            self._hand_eval_cache.pop(next(iter(self._hand_eval_cache)))
        return strength

    def classify_hand(self, cards: List[str], board: List[str]) -> str:
        """Classify hand type for postflop strategy with all variants."""
        all_cards = cards + board
        rank_counts = {}
        suit_counts = {}
        for card in all_cards:
            rank, suit = card[0], card[1]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        rank_values = sorted(rank_counts.values(), reverse=True)
        
        # Check pocket pair for set vs trips
        has_pocket_pair = len(cards) == 2 and cards[0][0] == cards[1][0]
        
        # Hand classifications from strongest to weakest
        if 4 in rank_values:
            return "quads"
        
        elif 3 in rank_values and 2 in rank_values:
            return "full_house"
        
        # Check for straight flush BEFORE regular flush
        elif max(suit_counts.values()) >= 5 and self._has_straight(list(rank_counts.keys())):
            return "straight_flush"
        
        elif max(suit_counts.values()) >= 5:
            if self._is_nut_flush(cards, board, suit_counts):
                return "nut_flush"
            return "flush"
        
        elif self._has_straight(list(rank_counts.keys())):
            return "straight"
        
        elif 3 in rank_values:
            if has_pocket_pair:
                pocket_rank = cards[0][0]
                if rank_counts.get(pocket_rank, 0) == 3:
                    return "set"
            return "trips"
        
        elif rank_values.count(2) >= 2:
            return "two_pair"
        
        # Check for draws first (before pairs)
        elif max(suit_counts.values()) == 4:
            if self._is_nut_flush_draw(cards, board, suit_counts):
                return "nut_flush_draw"
            return "flush_draw"
        
        elif self._has_open_ended_draw(list(rank_counts.keys())):
            if max(suit_counts.values()) == 4:
                return "combo_draw"
            return "open_ended_draw"
        
        elif self._has_gutshot_draw(list(rank_counts.keys())):
            return "gutshot_draw"
        
        elif self._has_backdoor_straight_draw(list(rank_counts.keys())):
            return "backdoor_straight"
        
        elif max(suit_counts.values()) == 3:
            if self._has_backdoor_flush(cards, board, suit_counts):
                return "backdoor_flush"
            return "high_card"  # Default for 3-to-a-suit without backdoor flush
        
        elif 2 in rank_values:
            # Detailed pair classification
            pair_rank = None
            for rank, count in rank_counts.items():
                if count == 2:
                    pair_rank = rank
                    break
            
            if not board:  # Preflop
                return "pair"
            
            # Check pair strength relative to board
            board_ranks = [card[0] for card in board]
            rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                         '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                         '4': 4, '3': 3, '2': 2}
            
            board_values = sorted([rank_order.get(r, 0) for r in board_ranks], reverse=True)
            pair_value = rank_order.get(pair_rank, 0)
            
            if has_pocket_pair and pair_value > max(board_values, default=0):
                return "over_pair"
            
            max_board = max(board_values, default=0)
            
            if pair_value == max_board:
                # Top pair - check kicker strength
                kicker_ranks = [card[0] for card in cards if card[0] != pair_rank]
                if kicker_ranks:
                    kicker_value = max(rank_order.get(r, 0) for r in kicker_ranks)
                    if kicker_value >= 10:  # T or higher
                        return "top_pair_good_kicker"
                    else:
                        return "top_pair_bad_kicker"
                return "top_pair"
            elif len(board_values) > 1 and pair_value == board_values[1]:
                return "second_pair"
            else:
                return "bottom_pair"
        
        elif 2 in rank_values and (max(suit_counts.values()) == 4 or self._has_open_ended_draw(list(rank_counts.keys()))):
            return "pair_plus_draw"
        
        elif 3 in rank_values and has_pocket_pair and (max(suit_counts.values()) == 4 or self._has_open_ended_draw(list(rank_counts.keys()))):
            return "set_plus_draw"
        
        else:
            return "high_card"

    def get_hand_description_and_cards(self, cards: List[str], board: List[str]) -> Dict[str, any]:
        """Get user-friendly hand description and the 5 cards that form the winning hand."""
        # Use the enhanced hand evaluator to get detailed information
        evaluation = self.hand_evaluator.evaluate_hand(cards, board)
        
        # Get the best 5-card combination
        best_hand = self._get_best_five_cards(cards, board)
        
        # Convert internal classification to user-friendly description
        classification = self.classify_hand(cards, board)
        description = self._classification_to_description(classification, cards, board)
        
        return {
            'description': description,
            'winning_cards': best_hand,
            'classification': classification,
            'hand_rank': evaluation['hand_rank'],
            'strength_score': evaluation['strength_score']
        }

    def _classification_to_description(self, classification: str, cards: List[str], board: List[str]) -> str:
        """Convert internal classification to user-friendly description."""
        # Safety check for None classification
        if classification is None:
            return "Unknown Hand"
            
        descriptions = {
            'quads': 'Four of a Kind',
            'full_house': 'Full House',
            'nut_flush': 'Nut Flush',
            'flush': 'Flush',
            'straight': 'Straight',
            'set': 'Three of a Kind (Set)',
            'trips': 'Three of a Kind (Trips)',
            'two_pair': 'Two Pair',
            'over_pair': 'Overpair',
            'top_pair_good_kicker': 'Top Pair (Good Kicker)',
            'top_pair_bad_kicker': 'Top Pair (Weak Kicker)',
            'top_pair': 'Top Pair',
            'second_pair': 'Second Pair',
            'bottom_pair': 'Bottom Pair',
            'high_card': 'High Card',
            'nut_flush_draw': 'Nut Flush Draw',
            'flush_draw': 'Flush Draw',
            'combo_draw': 'Combo Draw',
            'open_ended_draw': 'Open-Ended Straight Draw',
            'gutshot_draw': 'Gutshot Draw',
            'backdoor_flush': 'Backdoor Flush Draw',
            'backdoor_straight': 'Backdoor Straight Draw',
            'pair_plus_draw': 'Pair Plus Draw',
            'set_plus_draw': 'Set Plus Draw'
        }
        
        return descriptions.get(classification, classification.replace('_', ' ').title())

    def _get_best_five_cards(self, cards: List[str], board: List[str]) -> List[str]:
        """Get the 5 cards that form the best hand."""
        # Use the enhanced hand evaluator's new method to get the actual best 5-card combination
        return self.hand_evaluator.get_best_five_cards(cards, board)

    def _has_backdoor_flush(self, cards: List[str], board: List[str], suit_counts: dict) -> bool:
        """Check for backdoor flush draw (3 to a suit, one from player)."""
        player_suits = [card[1] for card in cards]
        board_suits = [card[1] for card in board]
        for suit in suit_counts:
            if suit_counts[suit] == 3 and suit in player_suits and board_suits.count(suit) == 2:
                return True
        return False

    def _is_nut_flush(self, cards: List[str], board: List[str], suit_counts: dict) -> bool:
        """Check if player has the nut flush (highest possible flush)."""
        if not board:
            return False
        
        # Find the suit with 5+ cards
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break
        
        if not flush_suit:
            return False
        
        # Get all cards of the flush suit
        flush_cards = [card for card in cards + board if card[1] == flush_suit]
        flush_cards.sort(key=lambda x: self._get_rank_value(x[0]), reverse=True)
        
        # Check if player has the highest flush card
        player_flush_cards = [card for card in cards if card[1] == flush_suit]
        if not player_flush_cards:
            return False
        
        highest_player_rank = max(self._get_rank_value(card[0]) for card in player_flush_cards)
        highest_board_rank = max(self._get_rank_value(card[0]) for card in board if card[1] == flush_suit)
        
        return highest_player_rank > highest_board_rank

    def _has_straight(self, ranks: List[str]) -> bool:
        """Check if the given ranks form a straight."""
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        rank_values = [self._get_rank_value(rank) for rank in ranks]
        rank_values = sorted(list(set(rank_values)))  # Remove duplicates and sort
        
        # Check for regular straight
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] - rank_values[i] == 4:
                return True
        
        # Check for wheel straight (A-2-3-4-5)
        if 14 in rank_values:  # Ace
            wheel_ranks = [14, 2, 3, 4, 5]
            if all(rank in rank_values for rank in wheel_ranks):
                return True
        
        return False

    def _is_nut_flush_draw(self, cards: List[str], board: List[str], suit_counts: dict) -> bool:
        """Check if player has the nut flush draw (highest possible flush draw)."""
        if not board:
            return False
        
        # Find the suit with 4 cards (flush draw)
        draw_suit = None
        for suit, count in suit_counts.items():
            if count == 4:
                draw_suit = suit
                break
        
        if not draw_suit:
            return False
        
        # Check if player has the highest card of the draw suit
        player_draw_cards = [card for card in cards if card[1] == draw_suit]
        board_draw_cards = [card for card in board if card[1] == draw_suit]
        
        if not player_draw_cards:
            return False
        
        highest_player_rank = max(self._get_rank_value(card[0]) for card in player_draw_cards)
        highest_board_rank = max(self._get_rank_value(card[0]) for card in board_draw_cards)
        
        return highest_player_rank > highest_board_rank

    def _has_open_ended_draw(self, ranks: List[str]) -> bool:
        """Check for open-ended straight draw."""
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        rank_values = [self._get_rank_value(rank) for rank in ranks]
        rank_values = sorted(list(set(rank_values)))
        
        # Check for open-ended draws
        for i in range(len(rank_values) - 3):
            if rank_values[i+3] - rank_values[i] == 3:
                return True
        
        return False

    def _has_gutshot_draw(self, ranks: List[str]) -> bool:
        """Check for gutshot straight draw."""
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        rank_values = [self._get_rank_value(rank) for rank in ranks]
        rank_values = sorted(list(set(rank_values)))
        
        # Check for gutshot draws (missing one card in the middle)
        for i in range(len(rank_values) - 3):
            if rank_values[i+3] - rank_values[i] == 4:
                return True
        
        return False

    def _has_backdoor_straight_draw(self, ranks: List[str]) -> bool:
        """Check for backdoor straight draw."""
        rank_values = [self._get_rank_value(rank) for rank in ranks]
        rank_values = sorted(list(set(rank_values)))
        
        # Check for backdoor draws (need 2 more cards to complete straight)
        # Look for 3 consecutive cards or 4 cards with one gap
        for i in range(len(rank_values) - 2):
            # Check for 3 consecutive cards (e.g., 2,3,4)
            if rank_values[i+2] - rank_values[i] == 2:
                return True
        
        # Check for 4 cards with one gap (e.g., A,2,3,4 needs 5)
        if len(rank_values) >= 4:
            for i in range(len(rank_values) - 3):
                if rank_values[i+3] - rank_values[i] == 3:
                    return True
        
        return False

    def _get_rank_value(self, rank: str) -> int:
        """Get numeric value of a rank."""
        rank_values = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
        return rank_values.get(rank, 0)

    def calculate_pot_odds(self, call_amount: float) -> float:
        """Calculates pot odds for a given call amount."""
        if call_amount <= 0:
            return 0
        pot_total = self.game_state.pot + call_amount
        return pot_total / call_amount

    def should_call_by_pot_odds(self, player: Player, call_amount: float, hand_strength: int) -> bool:
        """Determines if a call is justified by pot odds and hand strength."""
        # This is a simplified model. A more advanced model would use equity.
        # For now, we'll say a call is good if the hand has at least pair-strength.
        if hand_strength > 15:  # Corresponds to at least a pair
            return True
        return False

    def get_basic_bot_action(self, player: Player) -> Tuple[ActionType, float]:
        """GTO bot logic with modern poker theory."""
        # Use GTO strategy if enabled, otherwise fall back to basic logic
        if hasattr(self, 'strategy_mode') and self.strategy_mode == "GTO":
            return self.get_gto_bot_action(player)
        else:
            return self._get_legacy_bot_action(player)

    def get_gto_bot_action(self, player: Player) -> Tuple[ActionType, float]:
        hand = self.get_hand_notation(player.cards)
        position = player.position
        street = self.game_state.street
        facing_bet = self.game_state.current_bet > player.current_bet
        to_call = self.game_state.current_bet - player.current_bet
        pot_odds = to_call / (self.game_state.pot + to_call) if to_call > 0 else 0
        strength = self.get_postflop_hand_strength(player.cards, self.game_state.board) if street != "preflop" else self.hand_evaluator.get_preflop_hand_strength(player.cards)
        big_blind = self.game_state.big_blind
        spr = player.stack / self.game_state.pot if self.game_state.pot > 0 else float('inf')
        
        if street == "preflop" and not self.game_state.board:
            # Short stack all-in logic
            spr = player.stack / big_blind
            if spr < 3 and strength > 60:  # Short stack with strong hand
                return ActionType.RAISE, player.stack  # All-in
            
            context = "rfi" if self.game_state.last_raise_amount == 0 else "vs_rfi" if self.game_state.last_raise_amount < 3*big_blind else "vs_three_bet"
            range_data = self.gto_preflop_ranges.get(position, {}).get(context, {})
            
            if "three_bet" in range_data and self.is_hand_in_range(hand, range_data["three_bet"]["range"]) and random.random() < range_data["three_bet"]["freq"]:
                amount = self.game_state.current_bet * range_data["three_bet"]["size_mult"]
                if player.stack <= 15 * big_blind:  # Short stack jam
                    amount = player.stack
                return ActionType.RAISE, amount
            elif "call" in range_data and self.is_hand_in_range(hand, range_data["call"]["range"]) and random.random() < range_data["call"]["freq"]:
                return ActionType.CALL, to_call
            elif "four_bet" in range_data and self.is_hand_in_range(hand, range_data["four_bet"]["range"]) and random.random() < range_data["four_bet"]["freq"]:
                amount = self.game_state.current_bet * range_data["four_bet"]["size_mult"]
                if player.stack <= 15 * big_blind:
                    amount = player.stack
                return ActionType.RAISE, amount
            elif self.is_hand_in_range(hand, range_data.get("range", [])) and random.random() < range_data.get("freq", 1.0):
                amount = big_blind * 3  # Default open size
                if player.stack <= 15 * big_blind and strength > 70:
                    amount = player.stack
                return ActionType.RAISE, amount
            return ActionType.FOLD, 0.0
        
        # Postflop (fixed sizing with exact mult)
        texture = self.classify_board_texture(self.game_state.board)
        bet_size_mult = 0.33 if texture["type"] == "dry" else 0.66 if "wet" in texture["type"] else 0.5  # Medium 50%
        
        # Stack depth adjustment
        spr = player.stack / self.game_state.pot if self.game_state.pot > 0 else float('inf')
        stack_mult = min(1.0, max(0.3, spr / 5))  # Clamp between 0.3 and 1.0
        
        if strength > 80:  # Value bet
            amount = self.game_state.pot * bet_size_mult * stack_mult
            if facing_bet:
                amount += to_call  # Raise includes call
            return ActionType.BET if not facing_bet else ActionType.RAISE, amount
        elif strength > 50:  # Mid: Check/call if odds good
            if pot_odds >= 0.3:
                return ActionType.FOLD, 0.0
            return ActionType.CHECK if not facing_bet else ActionType.CALL, to_call
        else:  # Weak: Check or bluff occasionally
            if pot_odds < 0.2:  # Good bluffing spot
                amount = self.game_state.pot * 0.5  # Small bluff
                if facing_bet:
                    amount += to_call
                return ActionType.BET if not facing_bet else ActionType.RAISE, amount
            return ActionType.CHECK if not facing_bet else ActionType.FOLD, 0.0

    def _log_gto_decision(self, player: Player, hand: str, position: str, street: str, 
                          strength: int, action: ActionType, amount: float, pot_odds: float):
        """Log GTO decision for debugging."""
        if hasattr(self, 'logger') and self.logger:
            self.logger.log_system("INFO", "GTO", f"GTO Decision: {player.name} {position} {street} "
                               f"hand:{hand} strength:{strength} action:{action.value} "
                               f"amount:${amount:.2f} pot_odds:{pot_odds:.2f}")

    def _get_gto_preflop_action(self, player: Player, hand: str, position: str, 
                               facing_bet: bool, to_call: float, strength: int) -> Tuple[ActionType, float]:
        """GTO preflop action based on position and ranges."""
        # Short stack all-in logic
        spr = player.stack / self.game_state.big_blind
        if spr < 3 and strength > 60:  # Short stack with strong hand
            return ActionType.RAISE, player.stack  # All-in
        
        # Determine context
        if self.game_state.last_raise_amount == 0:
            context = "rfi"  # Raise First In
        elif self.game_state.last_raise_amount < 3 * self.game_state.big_blind:
            context = "vs_rfi"  # Versus Raise First In
        else:
            context = "vs_three_bet"  # Versus 3-bet
        
        # Get position ranges
        position_ranges = self.gto_preflop_ranges.get(position, {})
        context_data = position_ranges.get(context, {})
        
        # Check if hand is in range for this context
        if "range" in context_data and "freq" in context_data:
            # Simple structure (rfi context)
            freq_check = random.random() < context_data["freq"]
            range_check = self.is_hand_in_range(hand, context_data["range"])
            
            if freq_check and range_check:
                # RFI - raise
                raise_amount = self.game_state.big_blind * 3  # Standard 3x raise
                return ActionType.RAISE, min(raise_amount, player.stack)
        elif "call" in context_data and "three_bet" in context_data:
            # Complex structure (vs_rfi context)
            # Check for 3-bet opportunity first
            three_bet_data = context_data["three_bet"]
            if (random.random() < three_bet_data["freq"] and 
                self.is_hand_in_range(hand, three_bet_data["range"])):
                raise_amount = self.game_state.current_bet * three_bet_data["size_mult"]
                return ActionType.RAISE, min(raise_amount, player.stack)
            
            # Check for call opportunity
            call_data = context_data["call"]
            if (random.random() < call_data["freq"] and 
                self.is_hand_in_range(hand, call_data["range"])):
                return ActionType.CALL, to_call
        
        # Default to fold if not in any range
        return ActionType.FOLD, 0

    def _get_gto_postflop_action(self, player: Player, position: str, facing_bet: bool,
                                to_call: float, strength: int, pot_odds: float) -> Tuple[ActionType, float]:
        """GTO postflop action based on hand strength and board texture."""
        board_texture = self.classify_board_texture(self.game_state.board)
        
        # Stack depth adjustment
        spr = player.stack / self.game_state.pot if self.game_state.pot > 0 else 100
        stack_mult = min(2.0, max(0.5, spr / 10))  # Clamp between 0.5 and 2.0
        
        # Determine bet sizing based on board texture
        if board_texture["type"] == "dry":
            bet_size_mult = 0.33 * stack_mult  # Small bet on dry boards
        elif board_texture["type"] in ["wet_flush", "wet_straight"]:
            bet_size_mult = 0.66 * stack_mult  # Large bet on wet boards
        else:
            bet_size_mult = 0.5 * stack_mult  # Medium bet on medium boards
        
        # Check-raise logic for strong hands facing bets
        if facing_bet and strength > 70 and random.random() < 0.3:
            raise_amount = self.game_state.current_bet * 2.5
            if raise_amount <= player.stack:
                return ActionType.RAISE, raise_amount
        
        # Value betting with strong hands
        if strength > 80:
            if random.random() < 0.7:  # 70% frequency for value betting
                bet_amount = self.game_state.pot * bet_size_mult
                if not facing_bet:
                    return ActionType.BET, bet_amount
                else:
                    return ActionType.RAISE, bet_amount
            else:
                if not facing_bet:
                    return ActionType.CHECK, 0
                else:
                    return ActionType.CALL, to_call
        
        # Medium strength hands
        elif strength > 50:
            if not facing_bet:
                # Check or bet small for protection
                if random.random() < 0.3:  # 30% bluff frequency
                    bet_amount = self.game_state.pot * 0.25
                    return ActionType.BET, bet_amount
                else:
                    return ActionType.CHECK, 0
            else:
                # Call if pot odds are good
                if pot_odds < 0.3:
                    return ActionType.CALL, to_call
                else:
                    return ActionType.FOLD, 0
        
        # Weak hands - bluff or fold
        else:
            if not facing_bet:
                # Bluff with some frequency if board is favorable
                if (random.random() < 0.25 and 
                    board_texture["type"] in ["dry", "medium"]):
                    bet_amount = self.game_state.pot * 1.2  # Overbet bluff
                    return ActionType.BET, bet_amount
                else:
                    return ActionType.CHECK, 0
            else:
                # Fold weak hands facing bets
                return ActionType.FOLD, 0

    def _get_legacy_bot_action(self, player: Player) -> Tuple[ActionType, float]:
        """Legacy basic bot logic as fallback."""
        # Use the enhanced hand evaluator instead of the old method
        hand_info = self.hand_evaluator.evaluate_hand(player.cards, self.game_state.board)
        hand_strength = hand_info['strength_score']  # Use the strength score from the dict
        
        # --- FIXED: BB should not fold when there's no risk (no raise) ---
        if player.position == "BB":
            # BB should not fold when there's no risk (no raise has been made)
            if self.game_state.current_bet <= self.game_state.big_blind:
                # No raise has been made, BB should check or bet
                if hand_strength > 20:
                    return ActionType.BET, min(3.0, player.stack)
                else:
                    return ActionType.CHECK, 0
            else:
                # There's a raise, BB can fold if hand is weak
                call_amount = self.game_state.current_bet - player.current_bet
                if hand_strength > 30 and call_amount < player.stack * 0.5:
                    # BB can raise with strong hands
                    min_raise_total = self.game_state.current_bet + self.game_state.min_raise
                    raise_amount = max(min_raise_total, min(self.game_state.current_bet * 2, player.stack))
                    if raise_amount <= player.stack:
                        return ActionType.RAISE, raise_amount
                    else:
                        return ActionType.CALL, call_amount
                elif hand_strength > 15 and call_amount <= player.stack * 0.2:
                    return ActionType.CALL, call_amount
                else:
                    return ActionType.FOLD, 0  # BB can fold to a raise with weak hands
        # --- End of BB folding fix ---
        
        # Regular bot logic for non-BB players
        if self.game_state.current_bet == 0:
            if hand_strength > 20:
                return ActionType.BET, min(3.0, player.stack)
            else:
                return ActionType.CHECK, 0
        else:
            call_amount = self.game_state.current_bet - player.current_bet
            if hand_strength > 30 and call_amount < player.stack * 0.5:
                # --- FIX: Ensure raise meets minimum requirement ---
                min_raise_total = self.game_state.current_bet + self.game_state.min_raise
                raise_amount = max(min_raise_total, min(self.game_state.current_bet * 2, player.stack))
                if raise_amount <= player.stack:
                    return ActionType.RAISE, raise_amount
                else:
                    return ActionType.FOLD, 0
            elif hand_strength > 15 and call_amount <= player.stack * 0.2:
                return ActionType.CALL, call_amount
            else:
                return ActionType.FOLD, 0

    # FIX 2 & 3: Correct Raise Logic and All-In Detection
    def execute_action(self, player: Player, action: ActionType, amount: float = 0, _is_fallback: bool = False):
        """Execute a player action with all fixes."""
        # --- FIX: Log and play sound immediately upon receiving the action ---
        self.log_state_change(player, action, amount)
        
        # Play industry-standard sound for the action
        self.sound_manager.play_action_sound(action.value.lower(), amount)
        
        # Play voice announcement for the action
        if hasattr(self, 'voice_system') and self.voice_system:
            self.voice_system.play_action_with_voice(f"player_{action.value.lower()}", amount)
        
        # Track last action details for UI feedback
        self.game_state.last_action_details = f"{player.name} {action.value.lower()}s"
        if amount > 0:
            self.game_state.last_action_details += f" to ${amount:.2f}"
        # --- END FIX ---
        
        # --- NEW: Proper invalid action handling ---
        # Validate inputs
        if not player:
            self._log_message(f"ERROR in execute_action: Player cannot be None")
            return
        
        if not isinstance(action, ActionType):
            self._log_message(f"ERROR in execute_action: Invalid action type: {action}")
            return
        
        if amount < 0:
            self._log_message(f"ERROR in execute_action: Amount cannot be negative: ${amount}")
            return
        
        # Validate action is valid for current state
        errors = self.validate_action(player, action, amount)
        if errors:
            error_msg = f"Invalid action: {'; '.join(errors)}"
            self._log_message(f"ERROR in execute_action: {error_msg}")
            
            # --- NEW: Handle invalid bot actions with fallback ---
            if not player.is_human and not _is_fallback:
                self._log_message(f"🤖 Bot action failed, trying fallback")
                # Try fallback actions in order: CALL -> CHECK -> FOLD
                call_amount = self.game_state.current_bet - player.current_bet
                
                # Try CALL first if there's something to call
                if call_amount > 0 and call_amount <= player.stack:
                    fallback_errors = self.validate_action(player, ActionType.CALL, call_amount)
                    if not fallback_errors:
                        self._log_message(f"📞 Bot falling back to CALL ${call_amount:.2f}")
                        return self.execute_action(player, ActionType.CALL, call_amount, _is_fallback=True)
                
                # Try CHECK if no bet to call
                if call_amount == 0:
                    fallback_errors = self.validate_action(player, ActionType.CHECK, 0)
                    if not fallback_errors:
                        self._log_message(f"✅ Bot falling back to CHECK")
                        return self.execute_action(player, ActionType.CHECK, 0, _is_fallback=True)
                
                # Last resort: FOLD
                fallback_errors = self.validate_action(player, ActionType.FOLD, 0)
                if not fallback_errors:
                    self._log_message(f"❌ Bot falling back to FOLD")
                    return self.execute_action(player, ActionType.FOLD, 0, _is_fallback=True)
                
                # If even FOLD fails, something is seriously wrong
                self._log_message(f"🚨 CRITICAL: Bot cannot make any valid action!")
                return
            
            # --- Re-prompt human player for valid action ---
            if player.is_human and self.on_action_required:
                self._log_message(f"🔄 Re-prompting human player for valid action")
                self.on_action_required(player)
            return
        # --- END NEW ---
        
        # --- ENHANCED: Detailed Action Logging ---
        old_pot = self.game_state.pot  # Track pot changes
        old_stack = player.stack  # Track stack changes
        pot_change = 0.0  # Track actual pot change for this action
        self._log_message(f"🎯 {player.name} attempting {action.value.upper()} ${amount:.2f}")
        self._log_message(f"📊 Before action - Pot: ${self.game_state.pot:.2f}, Current Bet: ${self.game_state.current_bet:.2f}")
        self._log_message(f"💰 {player.name} stack: ${player.stack:.2f}, current bet: ${player.current_bet:.2f}")
        self._log_message(f"🎴 {player.name} cards: {player.cards}")
        self._log_message(f"🃏 Board: {self.game_state.board}")
        self._log_message(f"🏆 Street: {self.game_state.street}")

        # NEW: Trigger action animation callback (MOVED to after action execution for correct amounts)
        # Will be called after each action type with the actual amount used

        # Play sound effects based on action (prioritize authentic sounds)
        if action == ActionType.FOLD:
            player.is_active = False
            
            # --- THIS IS THE CRITICAL BUG FIX ---
            # DO NOT reset the player's current bet when they fold.
            # Their bet from this round is still part of the pot calculation for other players.
            # REMOVE this line: player.current_bet = 0
            # --- End of Bug Fix ---
            
            # FIXED: Trigger callback for fold action (amount is 0)
            if self.on_action_executed:
                player_index = self.game_state.players.index(player)
                self.on_action_executed(player_index, action.value, 0)

        elif action == ActionType.CHECK:
            # Only valid when current_bet is 0 or player already has current bet
            call_amount = self.game_state.current_bet - player.current_bet
            if call_amount > 0:
                self._log_message(f"ERROR: {player.name} cannot check when bet is ${self.game_state.current_bet}")
                return
            # FIX: Do NOT reset current_bet when checking - it should remain as is
            # player.current_bet = 0  # ← REMOVED THIS BUG
            
            # FIXED: Trigger callback for check action (amount is 0)
            if self.on_action_executed:
                player_index = self.game_state.players.index(player)
                self.on_action_executed(player_index, action.value, 0)

        elif action == ActionType.CALL:
            call_amount = self.game_state.current_bet - player.current_bet
            actual_call = min(call_amount, player.stack)
            
            # BUG FIX: Track partial calls for side pot calculations
            if actual_call < call_amount:
                # Player can't make full call - this creates a side pot situation
                player.is_all_in = True
                player.partial_call_amount = actual_call
                player.full_call_amount = call_amount
                self._log_message(f"{player.name} ALL-IN for ${actual_call:.2f} (${call_amount - actual_call:.2f} short)")
            else:
                player.partial_call_amount = None
                player.full_call_amount = None
            
            player.stack -= actual_call
            player.current_bet += actual_call
            player.total_invested += actual_call
            self.game_state.pot += actual_call
            pot_change += actual_call  # Track pot change for this action
            
            # FIXED: Trigger callback with actual call amount for animation
            if self.on_action_executed:
                player_index = self.game_state.players.index(player)
                self.on_action_executed(player_index, action.value, actual_call)
            
            # Check for all-in
            if player.stack == 0:
                player.is_all_in = True
                self._log_message(f"{player.name} is ALL-IN!")
                # Play all-in voice announcement if available
                if hasattr(self, 'voice_system') and self.voice_system:
                    self.voice_system.play_voice_announcement('all_in')

        elif action == ActionType.BET:
            if self.game_state.current_bet > 0:
                self._log_message(f"ERROR: {player.name} cannot bet when current bet is ${self.game_state.current_bet}")
                return
            
            actual_bet = min(amount, player.stack)
            player.stack -= actual_bet
            player.current_bet = actual_bet
            player.total_invested += actual_bet
            self.game_state.pot += actual_bet
            pot_change += actual_bet  # Track pot change for this action
            self.game_state.current_bet = actual_bet
            
            # CRITICAL FIX: Set min_raise to the size of the bet
            self.game_state.min_raise = actual_bet
            self._log_message(f"💰 Bet of ${actual_bet:.2f} sets min_raise to ${self.game_state.min_raise:.2f}")
            
            # FIXED: Trigger callback with actual bet amount for animation
            if self.on_action_executed:
                player_index = self.game_state.players.index(player)
                self.on_action_executed(player_index, action.value, actual_bet)
            
            # Check for all-in
            if player.stack == 0:
                player.is_all_in = True
                self._log_message(f"{player.name} is ALL-IN!")

        elif action == ActionType.RAISE:
            # Validation already done earlier, proceed with execution
            total_bet = min(amount, player.current_bet + player.stack)
            additional_amount = total_bet - player.current_bet
            
            player.stack -= additional_amount
            player.current_bet = total_bet
            player.total_invested += additional_amount
            self.game_state.pot += additional_amount
            pot_change += additional_amount  # Track pot change for this action
            
            # --- REFACTORED AND IMPROVED RAISE LOGIC ---
            
            # Calculate the size of this raise
            raise_amount = total_bet - self.game_state.current_bet
            
            # Check if this raise is a "full" raise
            is_full_raise = raise_amount >= self.game_state.min_raise
            
            # Update the game state with the new bet and raise amounts
            self.game_state.current_bet = total_bet
            self.game_state.min_raise = raise_amount  # The next min raise must be at least this large
            
            # If it was a full raise, update the state to reflect that the action is reopened.
            # Otherwise, the last full raise amount remains unchanged.
            if is_full_raise:
                self.game_state.last_full_raise_amount = raise_amount
                self._log_message(f"🔄 Full raise made. Action is re-opened.")
                # Reset has_acted for other active players
                for p in self.game_state.players:
                    if p.is_active and p != player:
                        p.has_acted_this_round = False
                        # Also remove from players_acted set to ensure they can act again
                        if self.game_state.players.index(p) in self.game_state.players_acted:
                            self.game_state.players_acted.remove(self.game_state.players.index(p))
                self._log_message(f"🔄 Reset has_acted for all other active players")
            else:
                self._log_message(f"📉 Under-raise all-in. Action is not re-opened.")
                
            # --- END REFACTOR ---
            
            # FIXED: Trigger callback with actual raise amount for animation
            if self.on_action_executed:
                player_index = self.game_state.players.index(player)
                self.on_action_executed(player_index, action.value, additional_amount)
            
            if player.stack == 0:
                player.is_all_in = True
                self._log_message(f"{player.name} is ALL-IN!")

        # Mark player as acted
        player.has_acted_this_round = True
        self.game_state.players_acted.add(self.action_player_index)
        
        # Log action to comprehensive logging system
        try:
            # FIXED: Calculate actual amount used based on stack change (more reliable)
            actual_amount_used = old_stack - player.stack
            
            # For actions that don't involve money, set to 0
            if action in [ActionType.FOLD, ActionType.CHECK]:
                actual_amount_used = 0
            
            self._log_player_action(player, action.value, actual_amount_used, old_pot, self.game_state.pot)
            
            # Log system debug info
            self.logger.log_system("DEBUG", "ACTION", f"Action completed: {player.name} {action.value}", {
                "amount": actual_amount_used,
                "pot_change": pot_change,  # Use tracked pot change instead of total difference
                "stack_change": old_stack - player.stack,
                "street": self.game_state.street,
                "active_players": len([p for p in self.game_state.players if p.is_active])
            })
        except Exception as e:
            print(f"Warning: Could not log action: {e}")

        # --- CORRECTED GAME FLOW LOGIC ---
        # Check for a winner after any action that might end the hand
        active_players = [p for p in self.game_state.players if p.is_active]
        self._log_message(f"🎯 After {player.name} {action.value}, active players: {[p.name for p in active_players]}")
        
        if len(active_players) == 1:
            # CRITICAL FIX: Defer awarding to handle_end_hand to preserve pot for animation
            self._log_message(f"🏆 {active_players[0].name} wins by default (all others folded)")
            self._log_message(f"💰 Pot preserved for animation: ${self.game_state.pot:.2f}")
            
            # Only transition if not already in END_HAND state
            if self.current_state != PokerState.END_HAND:
                self.transition_to(PokerState.END_HAND)
            return  # End the action here since the hand is over

        # If the hand is not over, check if the round is complete
        self._log_message(f"🔄 POST-ACTION: Checking if round is complete...")
        self._log_message(f"🔍 DEBUG: About to call is_round_complete()")
        round_complete_result = self.is_round_complete()
        self._log_message(f"🔍 DEBUG: is_round_complete() returned: {round_complete_result}")
        
        if round_complete_result:
            self._log_message("✅ Round is complete, handling round completion")
            self.handle_round_complete()
        else:
            self._log_message("⏭️ Round not complete, advancing to next player")
            self.advance_to_next_player()
            self._log_message("🎯 Calling handle_current_player_action after advancing")
            self.handle_current_player_action()
        # --- END CORRECTION ---

    def advance_to_next_player(self):
        """Move to the next active player who can act."""
        original_index = self.action_player_index
        attempts = 0
        
        self._log_message(f"⏭️ ADVANCE_TO_NEXT_PLAYER: Starting from index {original_index}")
        
        while attempts < self.num_players:
            self.action_player_index = (self.action_player_index + 1) % self.num_players
            current_player = self.game_state.players[self.action_player_index]
            
            self._log_message(f"   Checking index {self.action_player_index}: {current_player.name}")
            self._log_message(f"     Active: {current_player.is_active}, All-in: {current_player.is_all_in}")
            self._log_message(f"     In players_acted: {self.action_player_index in self.game_state.players_acted}")
            self._log_message(f"     Current bet: ${current_player.current_bet:.2f}, Game bet: ${self.game_state.current_bet:.2f}")
            
            # Found a player who can act
            if (current_player.is_active and 
                not current_player.is_all_in and
                (self.action_player_index not in self.game_state.players_acted or
                 current_player.current_bet < self.game_state.current_bet)):
                self._log_message(f"✅ Found next player: {current_player.name} at index {self.action_player_index}")
                return
            else:
                self._log_message(f"   ❌ Player {current_player.name} cannot act")
            
            attempts += 1
        
        # No one can act - round is complete
        self._log_message("⚠️ No valid next player found, setting action_player_index to -1")
        self.action_player_index = -1
        
        # Safety check: If we can't find a next player but the round isn't complete,
        # there might be an issue with the action tracking
        if not self.is_round_complete():
            self._log_message("🚨 WARNING: No next player found but round is not complete!")
            self._log_message(f"   Active players: {[p.name for p in self.game_state.players if p.is_active]}")
            self._log_message(f"   Players acted: {self.game_state.players_acted}")
            self._log_message(f"   Current bet: ${self.game_state.current_bet:.2f}")
            for p in self.game_state.players:
                if p.is_active:
                    self._log_message(f"   {p.name}: has_acted={p.has_acted_this_round}, bet=${p.current_bet:.2f}")

    def handle_round_complete(self):
        """
        Handles the completion of a betting round by advancing to the next street
        or proceeding to showdown.
        """
        self._log_message(f"🔄 ROUND COMPLETE for {self.game_state.street}")
        
        # FIX: Trigger the on_round_complete callback BEFORE transitioning to next state
        # This ensures pot consolidation animation happens before street advancement
        if self.on_round_complete:
            debug_print(f"🔄 DEBUG: Triggering on_round_complete callback")
            self.on_round_complete()
            debug_print(f"🔄 DEBUG: on_round_complete callback completed")
        else:
            debug_print(f"❌ ERROR: on_round_complete callback is None!")

        # Determine the next state based on the current street
        if self.game_state.street == 'preflop':
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.game_state.street == 'flop':
            self.transition_to(PokerState.DEAL_TURN)
        elif self.game_state.street == 'turn':
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.game_state.street == 'river':
            self.transition_to(PokerState.SHOWDOWN)

    def determine_winner(self, players_to_evaluate: List[Player] = None) -> List[Player]:
        """Determine winners with proper tie handling using the enhanced evaluator."""
        # If a specific list of players is provided, use it. Otherwise, use all active players.
        active_players = players_to_evaluate if players_to_evaluate is not None else [p for p in self.game_state.players if p.is_active]
        
        if len(active_players) == 1:
            return active_players
        
        self._log_message(f"🔍 SHOWDOWN: Evaluating {len(active_players)} active players")
        self._log_message(f"🎴 Board: {' '.join(self.game_state.board)}")
        
        # Collect all hand evaluations for detailed comparison
        player_hands = []
        best_hand_info = None
        winners = []
        
        # First pass: evaluate all hands
        for player in active_players:
            hand_info = self.hand_evaluator.evaluate_hand(player.cards, self.game_state.board)
            player_hands.append({
                'player': player,
                'hand_info': hand_info
            })
            
            # Log each player's hand details
            hand_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
            self._log_message(f"📊 {player.name} ({' '.join(player.cards)}): {hand_rank} - {hand_info['hand_description']}")
        
        # Second pass: determine winner(s)
        for player_hand in player_hands:
            player = player_hand['player']
            hand_info = player_hand['hand_info']
            
            if not winners:  # First player to be evaluated
                best_hand_info = hand_info
                winners = [player]
                hand_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
                self._log_message(f"🏆 {player.name} leads with {hand_rank}")
            else:
                # Compare current player's hand with the best so far
                comparison = self.hand_evaluator._compare_hands(
                    (hand_info['hand_rank'], hand_info['rank_values']),
                    (best_hand_info['hand_rank'], best_hand_info['rank_values'])
                )
                
                current_rank = hand_info['hand_rank'].name.replace('_', ' ').title()
                best_rank = best_hand_info['hand_rank'].name.replace('_', ' ').title()
                
                if comparison > 0:  # Current player has a better hand
                    best_hand_info = hand_info
                    winners = [player]
                    self._log_message(f"🏆 {player.name} wins with {current_rank} vs {best_rank}")
                elif comparison == 0:  # It's a tie
                    winners.append(player)
                    self._log_message(f"🤝 {player.name} ties with {current_rank}")
                else:
                    self._log_message(f"❌ {player.name} loses with {current_rank} vs {best_rank}")
        
        # Final showdown summary
        if len(winners) == 1:
            winner = winners[0]
            winner_hand = next(ph for ph in player_hands if ph['player'] == winner)
            hand_rank = winner_hand['hand_info']['hand_rank'].name.replace('_', ' ').title()
            self._log_message(f"🎉 {winner.name} wins with {hand_rank}!")
        else:
            winner_names = [w.name for w in winners]
            self._log_message(f"🎉 Split pot between {', '.join(winner_names)}")
        
        return winners

    def handle_showdown(self):
        """Handle showdown with tie handling and side pots."""
        self._log_message("Showdown")
        
        # Preserve the board cards for display during showdown
        self.preserved_board = self.game_state.board.copy()
        
        # Only play winner announcement if there's actually a showdown (multiple active players)
        active_players = [p for p in self.game_state.players if p.is_active]
        if len(active_players) > 1:
            self.sound_manager.play("winner_announce")

        # FIX: Don't award pot here - let handle_end_hand do it
        # This prevents double-awarding the pot
        self.transition_to(PokerState.END_HAND)

    def create_side_pots(self) -> List[dict]:
        """
        Create side pots correctly handling all edge cases including folds and partial calls.
        """
        # Collect all players who have invested money (including folded players)
        all_players = self.game_state.players
        invested_players = [p for p in all_players if p.total_invested > 0]
        
        if not invested_players:
            return [{'amount': 0, 'eligible_players': []}]
        
        # Create a list of unique investment levels (sorted)
        investment_levels = sorted(set(p.total_invested for p in invested_players))
        
        side_pots = []
        previous_level = 0
        
        for level in investment_levels:
            # Calculate this pot level
            pot_amount = 0
            eligible_players = []
            contributors = []
            
            # Find all players who contributed to this pot level
            for player in all_players:
                if player.total_invested >= level:
                    # This player contributes to this pot level
                    contribution = level - previous_level
                    pot_amount += contribution
                    contributors.append(player)
                    
                    # Only active (non-folded) players are eligible to win
                    if player.is_active:
                        eligible_players.append(player)
                elif player.total_invested > previous_level:
                    # Partial contribution (player invested less than this level)
                    contribution = player.total_invested - previous_level
                    pot_amount += contribution
                    contributors.append(player)
                    
                    # Still eligible if active
                    if player.is_active:
                        eligible_players.append(player)
            
            # Only create a pot if there are eligible players to win it
            if pot_amount > 0 and eligible_players:
                side_pots.append({
                    'amount': pot_amount,
                    'eligible_players': eligible_players,
                    'level': level,
                    'contributors': len(contributors)
                })
            elif pot_amount > 0:
                # Dead money (from folded players) goes to the last pot
                if side_pots:
                    side_pots[-1]['amount'] += pot_amount
                else:
                    # Create a pot for the remaining active players
                    active_players = [p for p in all_players if p.is_active]
                    if active_players:
                        side_pots.append({
                            'amount': pot_amount,
                            'eligible_players': active_players,
                            'level': level,
                            'contributors': len(contributors)
                        })
            
            previous_level = level
        
        # Validate total
        total_created = sum(pot['amount'] for pot in side_pots)
        expected_total = sum(p.total_invested for p in all_players)
        
        if abs(total_created - expected_total) > 0.01:
            self._log_message(f"⚠️ Side pot discrepancy: Created ${total_created:.2f} vs Expected ${expected_total:.2f}")
            
            # Try to fix discrepancy by adding to main pot
            if side_pots:
                side_pots[-1]['amount'] += (expected_total - total_created)
        
        return side_pots if side_pots else [{'amount': self.game_state.pot, 
                                             'eligible_players': [p for p in all_players if p.is_active]}]

    def handle_end_hand(self):
        """
        Handles hand completion, determines winner, awards pot, and notifies UI.
        This is now the single source of truth for ending a hand.
        """
        debug_print(f"🔄 DEBUG: handle_end_hand() called for {self.game_state.street}")
        debug_print(f"🔄 DEBUG: Current pot: ${self.game_state.pot:.2f}")
        debug_print(f"🔄 DEBUG: Active players: {[p.name for p in self.game_state.players if p.is_active]}")

        self._log_message("Hand complete")

        # FIX: Handle side pots for all-in scenarios
        side_pots = self.create_side_pots()
        total_pot_awarded = 0
        all_winners = set()

        for i, pot in enumerate(side_pots):
            pot_amount = pot['amount']
            eligible_players = pot['eligible_players']
            
            if not eligible_players: continue

            # Determine winner(s) only from the eligible players for this specific pot
            winners = self.determine_winner(eligible_players)
            
            if winners:
                split_amount = pot_amount / len(winners)
                winner_names = ", ".join([w.name for w in winners])
                pot_name = f"Side Pot {i+1}" if i < len(side_pots) -1 else "Main Pot"
                
                self._log_message(f"🏆 {pot_name} ({pot_amount:.2f}) won by {winner_names}")

                for winner in winners:
                    winner.stack += split_amount
                    all_winners.add(winner.name)
                
                total_pot_awarded += pot_amount

        # Final check to ensure all money is awarded
        if abs(total_pot_awarded - self.game_state.pot) > 0.01:
             self._log_message(f"⚠️ Pot distribution discrepancy: {self.game_state.pot} vs {total_pot_awarded} awarded")

        if all_winners:
            winner_names = ", ".join(sorted(all_winners))
            pot_amount = self.game_state.pot  # Use original pot amount
            
            # ENHANCED: Include hand and board information for better UI display
            # Get the winning hand rank for the first winner
            winning_hand_rank = "Unknown"
            if all_winners:
                first_winner_name = list(all_winners)[0]
                for player in self.game_state.players:
                    if player.name == first_winner_name and player.is_active:
                        winning_hand_rank = self.classify_hand(player.cards, self.game_state.board)
                        break
            
            winner_info = {
                "name": winner_names, 
                "amount": pot_amount,
                "board": self.game_state.board.copy(),  # Include final board
                "hand": winning_hand_rank  # Include actual hand rank
            }
            self._last_winner = winner_info
            self._log_message(f"🏆 Winner(s): {winner_names} win ${pot_amount:.2f}")
            debug_print(f"🏆 DEBUG: Winner info: {winner_info}")
        else:
            self._log_message("No winner determined (should not happen in a normal game).")
            winner_info = None
            debug_print(f"❌ DEBUG: No winner determined")

        # Reset game state for next hand
        if self.game_state:
            # Reset pot to 0 for next hand - the pot will be rebuilt with blinds
            self.game_state.pot = 0.0  # FIX: Reset pot for next hand
            self.game_state.current_bet = 0
            self.game_state.min_raise = 1.0
            self.game_state.players_acted.clear()
            self.game_state.round_complete = False
            self.game_state.board = []
            self.game_state.street = "preflop"
            
            # DO NOT reset player states here - that should happen in handle_start_hand
            # This preserves the player state (including is_all_in) until the hand is properly concluded
        
        # Advance dealer position for next hand
        self.advance_dealer_position()
        
        # SESSION TRACKING - NEW!
        debug_print(f"🔄 DEBUG: Calling _capture_hand_result")
        self._capture_hand_result(winner_info, side_pots)
        debug_print(f"✅ DEBUG: _capture_hand_result completed")
        
        if self.on_hand_complete:
            debug_print(f"🔄 DEBUG: Calling on_hand_complete callback")
            self.on_hand_complete(winner_info)
            debug_print(f"✅ DEBUG: on_hand_complete callback completed")
        else:
            debug_print(f"❌ ERROR: on_hand_complete callback is None!")
        
        debug_print(f"✅ DEBUG: handle_end_hand() completed successfully")

    def _capture_hand_result(self, winner_info: Optional[Dict], side_pots: List[Dict]):
        """Capture complete hand result for session tracking."""
        if not self.session_state:
            return
        
        # FIX: Call the logger's end_hand method to properly complete hand logging
        if self.logger and hasattr(self.logger, 'end_hand'):
            winner_name = winner_info.get('name', 'Unknown') if winner_info else 'Unknown'
            winning_hand = winner_info.get('hand', 'Unknown') if winner_info else 'Unknown'
            pot_size = self.game_state.pot
            showdown = len([p for p in self.game_state.players if p.is_active]) > 1
            
            debug_print(f"🔄 DEBUG: Calling logger.end_hand with winner={winner_name}, hand={winning_hand}, pot=${pot_size:.2f}")
            self.logger.end_hand(winner_name, winning_hand, pot_size, showdown)
            debug_print(f"✅ DEBUG: logger.end_hand completed successfully")
        else:
            debug_print(f"❌ ERROR: Logger or end_hand method not available!")
        
        # Capture players at end of hand
        players_at_end = [self._capture_player_state(p) for p in self.game_state.players]
        
        # Capture showdown cards for all active players
        showdown_cards = {}
        for player in self.game_state.players:
            if player.is_active and player.cards:
                showdown_cards[player.name] = player.cards.copy()
        
        # Create hand result
        hand_result = HandResult(
            hand_number=self.session_state.current_hand_number,
            start_time=time.time() - 60,  # Approximate start time
            end_time=time.time(),
            players_at_start=self.session_state.current_hand_state["players"] if self.session_state.current_hand_state else [],
            players_at_end=players_at_end,
            board_cards=self.game_state.board.copy(),
            pot_amount=self.game_state.pot,
            winners=[winner_info] if winner_info else [],
            side_pots=side_pots,
            action_history=self.hand_history.copy(),
            showdown_cards=showdown_cards
        )
        
        # Add to session
        self.session_state.hands_played.append(hand_result)
        self.session_state.current_hand_number += 1
        
        # Log session event
        if winner_info:
            self._log_session_event(f"Hand {hand_result.hand_number} complete: {winner_info['name']} wins ${winner_info['amount']:.2f}")
        else:
            self._log_session_event(f"Hand {hand_result.hand_number} complete: No winner")
        
        # Clear current hand history for next hand
        self.hand_history = []
        self.session_state.current_hand_history = []

    # FIX 6: Better Input Validation
    def validate_action(self, player: Player, action: ActionType, amount: float = 0) -> List[str]:
        """Validate action and return list of errors."""
        errors = []
        current_player = self.get_action_player()
        if current_player != player:
            errors.append(f"It's not {player.name}'s turn")

        if amount < 0:
            errors.append("Amount cannot be negative")

        call_amount = self.game_state.current_bet - player.current_bet

        # FIXED: BB folding logic - BB CAN fold when facing a raise
        if action == ActionType.FOLD:
            # BB can always fold if facing a raise (call_amount > 0)
            # BB cannot fold if no raise has been made and it's preflop
            if (player.position == "BB" and 
                self.game_state.street == "preflop" and 
                call_amount == 0):
                errors.append(f"Big Blind ({player.name}) cannot fold when no raise has been made")
            # No other restrictions on folding

        if action == ActionType.CHECK:
            # FIX: A player can only check if the amount to call is zero.
            if call_amount > 0:
                errors.append(f"Cannot check when bet is ${self.game_state.current_bet:.2f}")
        
        elif action == ActionType.CALL:
            if call_amount <= 0:
                errors.append("Nothing to call")
            elif amount != call_amount and amount != 0:
                errors.append(f"Call amount must be ${call_amount:.2f}, got ${amount:.2f}")

        elif action == ActionType.BET:
            # FIX: A bet is only valid if there is no current bet.
            if self.game_state.current_bet > 0:
                errors.append("Cannot bet when there's already a bet - use raise instead")
            if amount < self.game_state.min_raise:
                errors.append(f"Bet amount ${amount:.2f} is less than minimum bet ${self.game_state.min_raise:.2f}")
            if amount > player.stack:
                errors.append(f"Bet amount ${amount:.2f} exceeds stack ${player.stack:.2f}")

        elif action == ActionType.RAISE:
            min_raise_total = self.game_state.current_bet + self.game_state.min_raise
            # A player can go all-in for less than a min-raise.
            is_all_in_raise = (player.current_bet + player.stack) == amount

            # --- FIXED: All-in raise validation ---
            # A player who has already acted cannot re-raise unless another player
            # has since made a "full" raise, EXCEPT for all-in raises
            if player.has_acted_this_round and not is_all_in_raise:
                # The size of the last raise must be at least the size of the last *full* raise.
                # If it's smaller, it was an under-raise, and action is not reopened.
                if self.game_state.min_raise < self.game_state.last_full_raise_amount:
                    errors.append("Cannot re-raise as the last all-in was not a full raise.")
            # --- End of fixed validation ---

            if not is_all_in_raise and amount < min_raise_total:
                errors.append(f"Raise to ${amount:.2f} is less than minimum raise to ${min_raise_total:.2f}")
            if amount > player.current_bet + player.stack:
                errors.append(f"Raise amount ${amount:.2f} exceeds available chips")

        return errors

    def is_valid_action(self, player: Player, action: ActionType, amount: float = 0) -> bool:
        """Check if action is valid."""
        return len(self.validate_action(player, action, amount)) == 0

    # Public interface methods
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand, using existing players if provided."""
        debug_print(f"🌟 DEBUG: start_hand() called with existing_players={len(existing_players) if existing_players else 'None'}")
        debug_print(f"🌟 DEBUG: start_hand() called on object ID = {id(self)}")
        
        # SESSION TRACKING - NEW!
        self._capture_hand_start()
        
        debug_print(f"🌟 DEBUG: Setting current_state to START_HAND")
        self.current_state = PokerState.START_HAND
        
        debug_print(f"🌟 DEBUG: About to call handle_state_entry()")
        self.handle_state_entry(existing_players)
        
        debug_print(f"🌟 DEBUG: start_hand() completed")

    def _capture_hand_start(self):
        """Capture initial hand state for session tracking."""
        if not self.session_state:
            return
        
        # Capture current game state
        self.session_state.current_hand_state = self._capture_game_state()
        
        # Log session event
        self._log_session_event(f"Starting hand {self.session_state.current_hand_number + 1}")
        
        # Capture initial player stacks if this is the first hand
        if self.session_state.current_hand_number == 0:
            for player in self.game_state.players:
                self.session_state.session_metadata.initial_stacks[player.name] = player.stack

    def get_current_state(self) -> PokerState:
        """Get current state."""
        return self.current_state

    def get_action_player(self) -> Optional[Player]:
        """Get current action player."""
        if (self.game_state and 
            0 <= self.action_player_index < len(self.game_state.players)):
            return self.game_state.players[self.action_player_index]
        return None

    def get_game_info(self) -> dict:
        """Get comprehensive game information."""
        if not self.game_state:
            return {}
        action_player = self.get_action_player()
        valid_actions = self.get_valid_actions_for_player(action_player) if action_player else {}
        session_info = self.get_session_info()
        return {
            "state": self.current_state.value,
            "pot": self.game_state.pot,
            "current_bet": self.game_state.current_bet,
            "min_raise": self.game_state.min_raise,
            "board": self.game_state.board,
            "players": [
                {
                    "name": p.name,
                    "position": p.position,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "total_invested": p.total_invested,  # BUG FIX: Add missing field
                    "is_active": p.is_active,
                    "is_all_in": p.is_all_in,
                    "is_human": p.is_human,  # BUG FIX: Add missing is_human field
                    "cards": p.cards if (p.is_human or self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND]) else ["**", "**"],
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
            "valid_actions": valid_actions,
            "session_info": session_info,
            "last_action_details": self.game_state.last_action_details,
        }
    
    def get_valid_actions_for_player(self, player: Player) -> dict:
        """Get valid actions and amounts for a player. UI should use this instead of duplicating logic."""
        if not self.game_state:
            return {}
        
        call_amount = self.game_state.current_bet - player.current_bet
        min_bet = self.game_state.min_raise
        min_raise_total = self.game_state.current_bet + self.game_state.min_raise
        max_bet = player.stack + player.current_bet
        
        # Calculate preset bet amounts for UI convenience
        pot_size = self.game_state.pot
        preset_bets = {
            "half_pot": pot_size * 0.5,
            "pot": pot_size,
            "all_in": player.stack
        }
        
        # Determine valid actions with proper BB folding logic
        valid_actions = {
            "fold": self.is_valid_action(player, ActionType.FOLD, 0),
            "check": self.is_valid_action(player, ActionType.CHECK, 0),
            "call": self.is_valid_action(player, ActionType.CALL, call_amount),
            "bet": self.is_valid_action(player, ActionType.BET, min_bet),
            "raise": self.is_valid_action(player, ActionType.RAISE, min_raise_total),
            "call_amount": call_amount,
            "min_bet": min_bet,
            "min_raise": min_raise_total,
            "max_bet": max_bet,
            "current_bet": self.game_state.current_bet,
            "player_current_bet": player.current_bet,
            "preset_bets": preset_bets,
        }
        
        # Special case for BB preflop with no raise
        if (player.position == "BB" and 
            self.game_state.street == "preflop" and 
            call_amount == 0):
            valid_actions["fold"] = False  # BB cannot fold when no raise
        
        return valid_actions
    
    def get_hand_history(self) -> List[HandHistoryLog]:
        """Returns the structured log for the current hand."""
        return self.hand_history

    def get_comprehensive_session_data(self) -> Dict[str, Any]:
        """Get complete session data for debugging and analysis."""
        if not self.session_state:
            return {}
        
        # Convert hand history to serializable format
        current_hand_history = []
        for action in self.hand_history:
            current_hand_history.append({
                "timestamp": action.timestamp,
                "street": action.street,
                "player_name": action.player_name,
                "action": action.action.value,
                "amount": action.amount,
                "pot_size": action.pot_size,
                "board": action.board,
                "player_states": action.player_states
            })
        
        return {
            "session_info": self.get_session_info(),
            "session_statistics": self.get_session_statistics(),
            "current_hand_state": self._capture_game_state(),
            "current_hand_history": current_hand_history,
            "hands_played": [
                {
                    "hand_number": hand.hand_number,
                    "start_time": datetime.fromtimestamp(hand.start_time).isoformat(),
                    "end_time": datetime.fromtimestamp(hand.end_time).isoformat(),
                    "pot_amount": hand.pot_amount,
                    "winners": hand.winners,
                    "action_count": len(hand.action_history)
                }
                for hand in self.session_state.hands_played
            ],
            "session_log": self.session_state.session_log[-50:]  # Last 50 entries
        }

    def get_display_state(self) -> DisplayState:
        """Get UI-ready display state with pre-computed visual data."""
        if not self.game_state:
            return DisplayState(
                valid_actions={},
                player_highlights=[],
                card_visibilities=[],
                chip_representations={},
                layout_positions={},
                community_cards=[],
                pot_amount=0.0,
                current_bet=0.0,
                action_player_index=-1,
                game_state="",
                last_action_details=""
            )
        
        action_player = self.get_action_player()
        valid_actions_raw = self.get_valid_actions_for_player(action_player) if action_player else {}
        call_amount = valid_actions_raw.get('call_amount', 0)

        # Pre-compute UI-ready action data
        actions_ui = {
            'fold': {
                'enabled': valid_actions_raw.get('fold', False), 
                'label': 'Fold'
            },
            'check': {
                'enabled': valid_actions_raw.get('check', False), 
                'label': 'Check'
            },
            'call': {
                'enabled': valid_actions_raw.get('call', False), 
                'label': f"Call ${call_amount:.2f}" if call_amount > 0 else 'Call'
            },
            'bet': {
                'enabled': valid_actions_raw.get('bet', False), 
                'label': 'Bet'
            },
            'raise': {
                'enabled': valid_actions_raw.get('raise', False), 
                'label': 'Raise'
            },
            'preset_bets': valid_actions_raw.get('preset_bets', {})
        }

        # Player highlights: True for action player
        highlights = [i == self.action_player_index for i in range(len(self.game_state.players))]

        # Card visibilities: Show for human or during showdown/end (but only for active players)
        is_showdown_or_end = self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND]
        visibilities = [
            p.is_human or (is_showdown_or_end and p.is_active)
            for p in self.game_state.players
        ]

        # Chip representations (move calculations here)
        chip_reps = {}
        for i, p in enumerate(self.game_state.players):
            chip_reps[f'player{i}_stack'] = self._get_chip_symbols(p.stack)
        chip_reps['pot'] = self._get_pot_chip_symbols(self.game_state.pot)

        # Layout positions (compute based on num_players)
        layout = self._compute_layout_positions(800, 600, self.num_players)

        # Community cards (preserved during showdown)
        community_cards = self.game_state.board.copy()
        if self.current_state in [PokerState.SHOWDOWN, PokerState.END_HAND]:
            # Use preserved board if available
            if self.preserved_board:
                community_cards = self.preserved_board

        return DisplayState(
            valid_actions=actions_ui,
            player_highlights=highlights,
            card_visibilities=visibilities,
            chip_representations=chip_reps,
            layout_positions=layout,
            community_cards=community_cards,
            pot_amount=self.game_state.pot,
            current_bet=self.game_state.current_bet,
            action_player_index=self.action_player_index,
            game_state=self.current_state.value,
            last_action_details=self.game_state.last_action_details
        )

    def _get_chip_symbols(self, amount: float) -> str:
        """Calculate chip symbols for a given amount."""
        chip_count = self._calculate_chip_count(amount)
        if amount <= 25:
            return "🟡" * chip_count
        elif amount <= 50:
            return "🟠" * chip_count
        elif amount <= 100:
            return "🔴" * chip_count
        elif amount <= 250:
            return "🟢" * chip_count
        elif amount <= 500:
            return "🔵" * chip_count
        else:
            return "🟣" * chip_count

    def _get_pot_chip_symbols(self, amount: float) -> str:
        """Calculate chip symbols for pot display."""
        chip_count = self._calculate_pot_chip_count(amount)
        if amount <= 50:
            return "🟡" * chip_count
        elif amount <= 100:
            return "🟠" * chip_count
        elif amount <= 250:
            return "🔴" * chip_count
        elif amount <= 500:
            return "🟢" * chip_count
        else:
            return "🔵" * chip_count

    def _calculate_chip_count(self, amount: float) -> int:
        """Calculate how many chips to display for a given amount."""
        if amount <= 0:
            return 0
        elif amount <= 10:
            return 1
        elif amount <= 25:
            return 2
        elif amount <= 50:
            return 3
        elif amount <= 100:
            return 4
        elif amount <= 250:
            return 5
        elif amount <= 500:
            return 6
        else:
            return 7

    def _calculate_pot_chip_count(self, amount: float) -> int:
        """Calculate chip count for pot display."""
        if amount <= 0:
            return 0
        elif amount <= 25:
            return 1
        elif amount <= 50:
            return 2
        elif amount <= 100:
            return 3
        elif amount <= 250:
            return 4
        elif amount <= 500:
            return 5
        else:
            return 6

    def _compute_layout_positions(self, width: int, height: int, num_players: int) -> Dict[str, Tuple[int, int]]:
        """Compute layout positions for UI elements."""
        positions = {}
        
        # Center of the table
        center_x, center_y = width // 2, height // 2
        
        # Player positions around the table
        for i in range(num_players):
            angle = (i * 360 / num_players) * (3.14159 / 180)  # Convert to radians
            radius = min(width, height) * 0.35
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            positions[f'player{i}'] = (x, y)
        
        # Pot position (center)
        positions['pot'] = (center_x, center_y)
        
        # Community cards position (slightly above center)
        positions['community_cards'] = (center_x, center_y - 40)
        
        return positions

    def execute_action_string(self, player: Player, action_str: str, amount: float = 0):
        """Execute action with string input (UI-friendly)."""
        action_map = {
            "fold": ActionType.FOLD,
            "check": ActionType.CHECK,
            "call": ActionType.CALL,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE,
            "bet_or_raise": ActionType.BET  # Will be converted to RAISE if needed
        }
        
        action = action_map.get(action_str.lower())
        if action is None:
            raise ValueError(f"Invalid action: {action_str}")
        
        # Auto-convert bet to raise if there's a current bet
        if action == ActionType.BET and self.game_state.current_bet > 0:
            action = ActionType.RAISE
        
        # Execute the action using the original execute_action method
        self.execute_action(player, action, amount)

    def get_valid_actions(self, player: Player) -> dict:
        """Get valid actions for a specific player (alias for get_valid_actions_for_player)."""
        return self.get_valid_actions_for_player(player)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        debug_print(f"🔄 Signal {signum} received, initiating cleanup...")
        self._cleanup()
        sys.exit(0)



