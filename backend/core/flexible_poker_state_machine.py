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

from .poker_types import ActionType, Player, GameState, PokerState

from .deuces_hand_evaluator import DeucesHandEvaluator
# from .position_mapping import HandHistoryManager  # Removed - unused functionality
try:
    from ..utils.sound_manager import SoundManager
except ImportError:
    try:
        from utils.sound_manager import SoundManager
    except ImportError:
        # Fallback: create a mock SoundManager
        class SoundManager:
            def __init__(self, *args, **kwargs): pass
            def play_sound(self, *args, **kwargs): pass
            def stop_all(self): pass
from .session_logger import get_session_logger


@dataclass
class GameConfig:
    """Configuration for the poker game."""

    num_players: int = 6
    big_blind: float = 2.0  # Changed from 1.0 to 2.0 (no floating point)
    small_blind: float = 1.0  # Changed from 0.5 to 1.0 (no floating point)
    starting_stack: float = 200.0  # Changed from 100.0 to 200.0
    # Optional testing flag kept for backward compatibility with tester scripts
    test_mode: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (2 <= self.num_players <= 9):
            raise ValueError(
                f"num_players must be between 2 and 9, got {self.num_players}"
            )
        if self.big_blind <= 0:
            raise ValueError(
                f"big_blind must be positive, got {self.big_blind}"
            )
        if self.small_blind <= 0:
            raise ValueError(
                f"small_blind must be positive, got {self.small_blind}"
            )
        if self.small_blind >= self.big_blind:
            raise ValueError(
                f"small_blind ({self.small_blind}) must be less than "
                f"big_blind ({self.big_blind})"
            )

    # Re-add auto_advance for dealing states - was needed for practice session
    # bug fix
    auto_advance: bool = False


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

    def __init__(self, config: GameConfig = None, mode: str = "live"):
        """Initialize the flexible poker state machine."""
        self.config = config or GameConfig()

        # Mode system: "live" for interactive play, "review" for timeline
        if mode not in ("live", "review"):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode

        # Core game state
        self.current_state = PokerState.START_HAND
        self.game_state = GameState(
            players=[],
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[],
        )

        # Player management
        self.action_player_index = 0

        # Prevents events during controlled restores
        self._suspend_side_effects = False
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 0

        # Event system
        self.event_listeners: List[EventListener] = []
        self.event_history: List[GameEvent] = []

        # Hand tracking
        self.hand_number = 0
        self.hand_history: List[Dict[str, Any]] = []

        # Utilities - Use proven deuces library for hand evaluation
        self.hand_evaluator = DeucesHandEvaluator()
        # Pass through test_mode so testers can disable sound/voice
        self.sound_manager = SoundManager(test_mode=self.config.test_mode)

        # Strategy integration (optional)
        self.strategy_integration = self._create_basic_strategy_integration()
        # self.hand_history_manager = HandHistoryManager()  # Removed - unused

        # Callbacks (for backward compatibility)
        self.on_action_required: Optional[Callable] = None
        self.on_hand_complete: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None
        self.on_action_executed: Optional[Callable] = None
        self.on_round_complete: Optional[Callable] = None

        # Round tracking
        self.actions_this_round = 0
        self.players_acted_this_round = set()  # Track which players have acted this betting round

        # Initialize players
        self._initialize_players()

        # Initialize session logger
        self.session_logger = get_session_logger()
        self.session_logger.log_system(
            "INFO",
            "STATE_MACHINE",
            "FPSM initialized",
            {
                "num_players": self.config.num_players,
                "mode": self.mode,
            },
        )

    def set_mode(self, mode: str) -> None:
        """Set the mode of the state machine."""
        if mode not in ("live", "review"):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode
        if self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                f"Mode set to {self.mode}",
                {},
            )

    def restore_snapshot(self, snap: Dict[str, Any]) -> None:
        """
        Restore a full table snapshot without triggering any live 'reset' or
        'advance' behavior. Intended for Hands Review timeline jumps.
        """
        print("🔄 FPSM RESTORING SNAPSHOT:")
        print(
            f"   📊 Input snapshot: board={snap.get('board', [])}, "
            f"pot=${snap.get('pot', 0.0)}"
        )
        print(f"   👥 Players: {len(snap.get('players', []))}")
        print(f"   🎲 Dealer: {snap.get('dealer_index', 'Not set')}")
        action_player = snap.get("action_player_index", "Not set")
        print(f"   🎯 Action player: {action_player}")

        self._suspend_side_effects = True
        try:
            # Game state: board, pot, current_bet, street
            self.game_state.board = snap.get("board", [])
            self.game_state.pot = float(snap.get("pot", 0.0))
            self.game_state.street = snap.get("street", "preflop")
            self.game_state.current_bet = float(snap.get("current_bet", 0.0))

            print(
                f"   ✅ Game state updated: board={self.game_state.board}, "
                f"pot=${self.game_state.pot}"
            )

            # Players: stack, bets, cards, status
            players = snap.get("players", [])
            for i, p in enumerate(players):
                if i < len(self.game_state.players):
                    gp = self.game_state.players[i]
                    old_stack = getattr(gp, "stack", 0.0)
                    old_bet = getattr(gp, "current_bet", 0.0)
                    old_cards = getattr(gp, "cards", [])

                    gp.stack = float(p.get("stack", old_stack))
                    gp.current_bet = float(p.get("current_bet", 0.0))
                    gp.is_active = p.get("is_active", True)
                    gp.has_folded = p.get("has_folded", False)

                    # Handle cards - preserve existing if not in snapshot
                    cards = p.get("cards", None)
                    if cards is not None:
                        if isinstance(cards, list):
                            gp.cards = list(cards)

                    print(
                        f"      Player {i}: stack ${old_stack}->${gp.stack}, "
                        f"bet ${old_bet}->${gp.current_bet}, "
                        f"cards {old_cards}->{gp.cards}"
                    )

            # Dealer/button & action pointer (if present)
            if "dealer_index" in snap:
                self.dealer_position = int(snap["dealer_index"])
                print(f"   🎲 Dealer position: {self.dealer_position}")

            if "action_player_index" in snap:
                self.action_player_index = int(snap["action_player_index"])
                print(f"   🎯 Action player: {self.action_player_index}")

        finally:
            self._suspend_side_effects = False

        # Emit display state event to update UI
        self._emit_display_state_event()
        print("   ✅ Snapshot restoration complete!")

    def _initialize_players(self):
        """Initialize players for the game."""
        self.game_state.players = []
        for i in range(self.config.num_players):
            # Enforce canonical Seat* uid for identity
            player = Player(
                name=f"Seat{i + 1}",
                stack=self.config.starting_stack,
                position="",
                is_human=False,
                is_active=True,
                cards=[],
            )
            self.game_state.players.append(player)

        # Assign positions
        self._assign_positions()

    def assign_positions(self):
        """Public method to assign positions to players."""
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
                # Multi-way: assign positions starting from dealer (BTN)
                # Position names are in order: [BTN, SB, BB, UTG, MP, CO]
                position_offset = (i - self.dealer_position) % num_players

                if position_offset < len(position_names):
                    self.game_state.players[i].position = position_names[
                        position_offset
                    ]
                else:
                    self.game_state.players[i].position = f"Seat{i + 1}"

    def _get_position_names(self) -> List[str]:
        num_players = self.config.num_players

        if num_players == 2:
            # Heads-up: [SB/BTN, BB]
            return ["SB/BTN", "BB"]
        elif num_players == 3:
            # 3-handed: [BTN, SB, BB] (starting from dealer position)
            return ["BTN", "SB", "BB"]
        elif num_players == 4:
            # 4-handed: [BTN, SB, BB, UTG] (starting from dealer position)
            return ["BTN", "SB", "BB", "UTG"]
        elif num_players == 5:
            # 5-handed: [BTN, SB, BB, UTG, CO] (starting from dealer position)
            return ["BTN", "SB", "BB", "UTG", "CO"]
        elif num_players == 6:
            # 6-handed: [BTN, SB, BB, UTG, MP, CO] (dealer position)
            return ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        else:
            # 7+ players: [BTN, SB, BB, UTG, MP1, MP2, ..., CO] (starting from
            # dealer position)
            positions = ["BTN", "SB", "BB", "UTG"]
            # Add middle positions
            mp_count = num_players - 5  # Total - (BTN + SB + BB + UTG + CO)
            for i in range(1, mp_count + 1):
                positions.append(f"MP{i}")
            positions.append("CO")
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
        if self._suspend_side_effects:
            return
        import time

        display_state = self.get_game_info()
        event = GameEvent(
            event_type="display_state_update",
            timestamp=time.time(),
            data={"display_state": display_state},
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
        # In review mode we never mutate the state for a "new hand"
        if self.mode == "review":
            if self.session_logger:
                self.session_logger.log_system(
                    "WARN",
                    "STATE_MACHINE",
                    "Ignored start_hand in review mode",
                    {},
                )
            # just refresh UI with what was restored
            self._emit_display_state_event()
            return

        # --- existing LIVE logic below ---
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
                raise ValueError(
                    f"Player count mismatch: config expects "
                    f"{self.config.num_players}, "
                    f"got {len(self.game_state.players)}"
                )
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
            self.dealer_position = (
                self.dealer_position + 1
            ) % self.config.num_players
        else:
            self.dealer_position = random.randint(
                0, self.config.num_players - 1
            )

        # Set blind positions
        if self.config.num_players == 2:
            # Heads-up: Dealer is Small Blind, other player is Big Blind
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % 2
        else:
            # Multi-way: SB left of dealer, BB left of SB
            self.small_blind_position = (
                self.dealer_position + 1
            ) % self.config.num_players
            self.big_blind_position = (
                self.small_blind_position + 1
            ) % self.config.num_players

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
            self.action_player_index = (
                self.big_blind_position + 1
            ) % self.config.num_players

        # Transition to preflop betting
        self.transition_to(PokerState.PREFLOP_BETTING)

        # Emit display state event
        self._emit_display_state_event()

    def _create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        suits = ["h", "d", "c", "s"]
        ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "T",
            "J",
            "Q",
            "K",
            "A",
        ]
        return [rank + suit for suit in suits for rank in ranks]

    def _deal_cards(self, num_cards: int) -> List[str]:
        """Deal cards from the deck."""
        cards = self.game_state.deck[:num_cards]
        self.game_state.deck = self.game_state.deck[num_cards:]
        return cards

    # Valid state transitions
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [
            PokerState.DEAL_FLOP,
            PokerState.END_HAND,
        ],
        # Allow END_HAND for fold situations
        PokerState.DEAL_FLOP: [
            PokerState.FLOP_BETTING,
            PokerState.END_HAND,
        ],
        PokerState.FLOP_BETTING: [
            PokerState.DEAL_TURN,
            PokerState.END_HAND,
        ],
        # Allow END_HAND for fold situations
        PokerState.DEAL_TURN: [
            PokerState.TURN_BETTING,
            PokerState.END_HAND,
        ],
        PokerState.TURN_BETTING: [
            PokerState.DEAL_RIVER,
            PokerState.END_HAND,
        ],
        # Allow END_HAND for fold situations
        PokerState.DEAL_RIVER: [
            PokerState.RIVER_BETTING,
            PokerState.END_HAND,
        ],
        PokerState.RIVER_BETTING: [
            PokerState.SHOWDOWN,
            PokerState.END_HAND,
        ],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }

    def transition_to(self, new_state: PokerState):
        """Transition to a new state if valid."""
        if new_state not in PokerState.__members__.values():
            raise ValueError(f"Invalid state: {new_state}")

        valid_transitions = self.STATE_TRANSITIONS.get(self.current_state, [])
        if (
            new_state not in valid_transitions
            and new_state != self.current_state
        ):
            raise ValueError(
                f"Invalid transition from {self.current_state} to {new_state}"
            )

        old_state = self.current_state
        self.current_state = new_state

        self.session_logger.log_system(
            "INFO",
            "STATE_MACHINE",
            f"State transition: {old_state} → {new_state}",
        )

        # Handle state-specific logic
        if new_state == PokerState.DEAL_FLOP:
            self.game_state.board.extend(self._deal_cards(3))
            self.game_state.street = "flop"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            next_player = self._find_first_active_after_dealer()
            if next_player == -1:
                print(f"⚠️ STREET_TRANSITION: No active players for new street, ending hand")
                self.transition_to(PokerState.END_HAND)
                return
            self.action_player_index = next_player
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                "Flop dealt",
                {"board": self.game_state.board},
            )
            # Play card dealing sound for flop
            if self.sound_manager:
                self.sound_manager.play_poker_event_sound("card_dealing")
            # Auto-advance to FLOP_BETTING if auto_advance is enabled
            if (
                hasattr(self.config, "auto_advance")
                and self.config.auto_advance
            ):
                self.transition_to(PokerState.FLOP_BETTING)

        elif new_state == PokerState.DEAL_TURN:
            self.game_state.board.append(self._deal_cards(1)[0])
            self.game_state.street = "turn"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            next_player = self._find_first_active_after_dealer()
            if next_player == -1:
                print(f"⚠️ STREET_TRANSITION: No active players for new street, ending hand")
                self.transition_to(PokerState.END_HAND)
                return
            self.action_player_index = next_player
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                "Turn dealt",
                {"board": self.game_state.board},
            )
            # Play card dealing sound for turn
            if self.sound_manager:
                self.sound_manager.play_poker_event_sound("card_dealing")
            # Auto-advance to TURN_BETTING if auto_advance is enabled
            if (
                hasattr(self.config, "auto_advance")
                and self.config.auto_advance
            ):
                self.transition_to(PokerState.TURN_BETTING)

        elif new_state == PokerState.DEAL_RIVER:
            self.game_state.board.append(self._deal_cards(1)[0])
            self.game_state.street = "river"
            self._reset_bets_for_new_round()
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            next_player = self._find_first_active_after_dealer()
            if next_player == -1:
                print(f"⚠️ STREET_TRANSITION: No active players for new street, ending hand")
                self.transition_to(PokerState.END_HAND)
                return
            self.action_player_index = next_player
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                "River dealt",
                {"board": self.game_state.board},
            )
            # Play card dealing sound for river
            if self.sound_manager:
                self.sound_manager.play_poker_event_sound("card_dealing")
            # Auto-advance to RIVER_BETTING if auto_advance is enabled
            if (
                hasattr(self.config, "auto_advance")
                and self.config.auto_advance
            ):
                self.transition_to(PokerState.RIVER_BETTING)

        elif new_state == PokerState.SHOWDOWN:
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                "Showdown reached",
                {"board": self.game_state.board},
            )
            self.transition_to(PokerState.END_HAND)

        elif new_state == PokerState.END_HAND:
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                f"Hand {self.hand_number} ended",
            )
            # Determine winners
            active_players = [
                p for p in self.game_state.players if not p.has_folded
            ]
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
                self.session_logger.log_system(
                    "INFO",
                    "STATE_MACHINE",
                    "Winners determined",
                    {
                        "winners": [w.name for w in winners],
                        "pot": self.game_state.pot,
                    },
                )
            else:
                self.session_logger.log_system(
                    "WARNING",
                    "STATE_MACHINE",
                    "No winners - pot returned",
                )

            # Reset current bet and player bets
            self.game_state.current_bet = 0.0
            for player in self.game_state.players:
                player.current_bet = 0.0

            # Create winner_info structure that matches what the UI expects
            # FIXED: Use primary winner name instead of comma list
            primary_winner_name = winners[0].name if winners else "Unknown"
            winner_info = {
                "name": primary_winner_name,  # Single winner name for backward compatibility
                "amount": self.game_state.pot,
                "board": self.game_state.board.copy(),
                "hand": "Unknown",  # Backward compatible field
                # New fields for richer showdown messaging
                "hand_description": "Unknown",
                "hand_rank": "",
                "best_five": [],
            }

            # Try to get hand description for the first winner
            if winners and hasattr(self, "hand_evaluator"):
                try:
                    first_winner = winners[0]
                    if first_winner.cards and len(first_winner.cards) == 2:
                        hand_eval = self.hand_evaluator.evaluate_hand(
                            first_winner.cards,
                            self.game_state.board,
                        )
                        if isinstance(hand_eval, dict):
                            # Prefer explicit description when available
                            if "hand_description" in hand_eval:
                                winner_info["hand_description"] = hand_eval[
                                    "hand_description"
                                ]
                                # legacy alias
                                winner_info["hand"] = hand_eval[
                                    "hand_description"
                                ]
                            if "hand_rank" in hand_eval:
                                winner_info["hand_rank"] = (
                                    getattr(
                                        hand_eval["hand_rank"],
                                        "name",
                                        str(hand_eval["hand_rank"]),
                                    )
                                    .replace("_", " ")
                                    .title()
                                )
                        # Compute and attach best five cards used to win
                        try:
                            winner_eval = self.hand_evaluator.evaluate_hand(
                                first_winner.cards,
                                self.game_state.board,
                            )
                            best_five_cards = winner_eval.get(
                                "best_five_cards", []
                            )
                            if best_five_cards:
                                winner_info["best_five"] = best_five_cards
                        except Exception:
                            pass
                except Exception as e:
                    self._safe_print(
                        f"Warning: Could not evaluate winning hand: {e}"
                    )

            # Store pot amount before reset for event
            final_pot_amount = self.game_state.pot

            self._emit_event(
                GameEvent(
                    event_type="hand_complete",
                    timestamp=time.time(),
                    data={
                        "hand_number": self.hand_number,
                        "winners": [w.name for w in winners],
                        "winner_info": winner_info,
                        "pot_amount": final_pot_amount,  # Use stored amount before reset
                    },
                )
            )

            # Emit display state update reflecting final showdown state and pot
            # Do NOT reset pot here; keep it until the next hand starts so the
            # UI can animate chips cleanly and still show the last pot amount.
            self._emit_display_state_event()

        # For betting states, reset actions_this_round only when transitioning
        # TO a new betting round
        betting_states = [
            PokerState.PREFLOP_BETTING,
            PokerState.FLOP_BETTING,
            PokerState.TURN_BETTING,
            PokerState.RIVER_BETTING,
        ]
        if new_state in betting_states and old_state != new_state:
            # Only reset if we're entering a NEW betting state, not re-entering
            # the same one
            self.actions_this_round = 0
            self.players_acted_this_round.clear()
            if new_state != PokerState.PREFLOP_BETTING:
                self._reset_bets_for_new_round()
            # Set first action player
            if new_state == PokerState.PREFLOP_BETTING:
                # Preflop: First action is UTG (player after big blind)
                # Don't override - action player was already set correctly in
                # start_hand()
                pass
            else:
                # Postflop: First action is player after dealer
                if self.config.num_players == 2:
                    # Heads-up postflop: BB acts first (opposite of preflop)
                    self.action_player_index = self.big_blind_position
                else:
                    # Multi-way postflop: SB acts first (player after dealer)
                    self.action_player_index = (
                        self._find_first_active_after_dealer()
                    )
            first_player = self.game_state.players[
                self.action_player_index
            ].name
            self.session_logger.log_system(
                "INFO",
                "STATE_MACHINE",
                f"{new_state} betting started",
                {"first_action_player": first_player},
            )

        # Emit state change event
        self._emit_event(
            GameEvent(
                event_type="state_change",
                timestamp=time.time(),
                data={
                    "new_state": str(new_state),
                    "old_state": str(old_state),
                },
            )
        )

    def _reset_bets_for_new_round(self):
        """Reset bets for a new betting round."""
        if self.mode == "review":
            return
        # IMPORTANT: Pot is already incremented during actions and blind posting.
        # Do NOT add player.current_bet again here or pot will double-count.
        for player in self.game_state.players:
            player.current_bet = 0.0
        self.game_state.current_bet = 0.0

    def _find_first_active_after_dealer(self) -> int:
        """Find the first active player after the dealer (for postflop)."""
        start = (self.dealer_position + 1) % len(self.game_state.players)
        result = self._find_next_active_player(
            start - 1
        )  # Start from dealer to find next
        
        print(f"🔍 FIND_ACTIVE_DEBUG: dealer_position={self.dealer_position}, start={start}, result={result}")
        if result == -1:
            print(f"⚠️ FIND_ACTIVE_DEBUG: No active players found!")
            active_players = [i for i, p in enumerate(self.game_state.players) if not p.has_folded and p.is_active and p.stack > 0]
            print(f"🔍 FIND_ACTIVE_DEBUG: Active players: {active_players}")
            print(f"🔍 FIND_ACTIVE_DEBUG: Player states: {[(i, p.name, p.has_folded, p.is_active, p.stack) for i, p in enumerate(self.game_state.players)]}")
        
        return result

    def _find_next_active_player(self, current_index: int) -> int:
        """Find the next active player after the given index."""
        n = len(self.game_state.players)
        for i in range(1, n + 1):
            idx = (current_index + i) % n
            player = self.game_state.players[idx]
            if not player.has_folded and player.is_active and player.stack > 0:
                return idx
        return -1  # No active players

    def _is_action_valid(
        self,
        action: ActionType,
        amount: float,
        valid_actions: Dict[str, Any],
    ) -> bool:
        """Check if an action is valid for the current game state."""
        # Check if action is allowed (handle case mismatch)
        action_key = action.value.lower()
        if not valid_actions.get(action_key, False):
            return False

        # Additional validation based on action type
        if action == ActionType.CALL:
            # No Limit Hold'em: Always allow calls (automatically capped at
            # stack in execute_action)
            return True

        elif action == ActionType.BET:
            # No Limit Hold'em: Only check minimum bet, no maximum limit
            return amount > 0

        elif action == ActionType.RAISE:
            # No Limit Hold'em: Only check minimum raise, no maximum limit
            min_raise = valid_actions.get("min_bet", self.config.big_blind)
            return amount >= min_raise

        return True

    def _safe_print(self, message: str):
        """Safely print a message, handling BrokenPipeError."""
        try:
            print(message, flush=True)
        except (BrokenPipeError, OSError):
            # Ignore broken pipe errors when output is piped
            pass

    def execute_action(
        self,
        player: Player,
        action: ActionType,
        amount: float = 0.0,
    ):
        """Execute a player action."""
        if not player.is_active or player.has_folded:
            return False

        # CRITICAL FIX: Only allow actions during betting states
        betting_states = [
            PokerState.PREFLOP_BETTING,
            PokerState.FLOP_BETTING,
            PokerState.TURN_BETTING,
            PokerState.RIVER_BETTING,
        ]
        if self.current_state not in betting_states:
            self._safe_print(
                f"❌ Action rejected: {action.value} not allowed during {self.current_state.value}"
            )
            return False

        # Validate action
        valid_actions = self.get_valid_actions_for_player(player)
        if not self._is_action_valid(action, amount, valid_actions):
            self._safe_print(
                f"❌ Invalid action: {player.name} cannot {action.value} ${amount:.2f}. Valid: {valid_actions}"
            )
            return False

        # Log current state (reduced verbosity)
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "GAME_STATE",
                f"Action executed: {self.current_state}, Street: {self.game_state.street}",
                {
                    "current_bet": self.game_state.current_bet,
                    "player_bet": player.current_bet,
                    "player": player.name,
                    "action": action.value,
                },
            )

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
                old_stack = player.stack
                actual_call = min(call_amount, player.stack)
                # POKER FIX: Round all money amounts to avoid float precision
                # issues
                actual_call = round(actual_call, 2)
                player.current_bet = round(player.current_bet + actual_call, 2)
                player.stack = round(player.stack - actual_call, 2)
                self.game_state.pot = round(
                    self.game_state.pot + actual_call, 2
                )
                self._safe_print(f"   {player.name} calls ${actual_call:.2f}")
                print(f"💰 STACK_DEBUG: {player.name} stack: ${old_stack:.2f} -> ${player.stack:.2f} (called ${actual_call:.2f})")

        elif action == ActionType.BET:
            if amount > 0:
                # No Limit Hold'em: Allow any bet amount (capped at stack if
                # needed)
                old_stack = player.stack
                actual_amount = min(amount, player.stack)
                # POKER FIX: Round all money amounts to avoid float precision
                # issues
                actual_amount = round(actual_amount, 2)
                player.current_bet = round(
                    player.current_bet + actual_amount, 2
                )
                player.stack = round(player.stack - actual_amount, 2)
                self.game_state.pot = round(
                    self.game_state.pot + actual_amount, 2
                )
                self.game_state.current_bet = player.current_bet
                self._safe_print(f"   {player.name} bets ${actual_amount:.2f}")
                print(f"💰 STACK_DEBUG: {player.name} stack: ${old_stack:.2f} -> ${player.stack:.2f} (bet ${actual_amount:.2f})")

        elif action == ActionType.RAISE:
            if amount >= self.game_state.current_bet:
                # No Limit Hold'em: Allow any raise amount (capped at stack if
                # needed)
                total_needed = amount - player.current_bet
                actual_total = min(total_needed, player.stack)
                actual_amount = player.current_bet + actual_total

                # POKER FIX: Round all money amounts to avoid float precision
                # issues
                actual_total = round(actual_total, 2)
                actual_amount = round(actual_amount, 2)
                player.current_bet = actual_amount
                player.stack = round(player.stack - actual_total, 2)
                self.game_state.pot = round(
                    self.game_state.pot + actual_total, 2
                )
                self.game_state.current_bet = actual_amount
                self._safe_print(
                    f"   {player.name} raises to ${actual_amount:.2f}"
                )
                
                # CRITICAL: When someone raises, reset players_acted_this_round
                # because all other players now need a chance to act to the new bet level
                old_acted = self.players_acted_this_round.copy()
                self.players_acted_this_round.clear()
                self.players_acted_this_round.add(player.name)  # Only the raiser has acted to this bet level

        # Mark player as acted this round
        self.players_acted_this_round.add(player.name)
        self.actions_this_round += 1

        # Reduced verbosity: only log round completion status to session logger
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "ROUND_PROGRESS",
                f"Round progress: {self.actions_this_round} actions, "
                f"{len(self.players_acted_this_round)} players acted",
                {
                    "actions_this_round": self.actions_this_round,
                    "players_acted": len(self.players_acted_this_round),
                    "street": self.game_state.street,
                },
            )

        # Emit action event
        import time

        action_event = GameEvent(
            event_type="action_executed",
            timestamp=time.time(),
            player_name=player.name,  # canonical Seat*
            action=action,
            amount=amount,
        )
        self._emit_event(action_event)

        # Add debug logging for action flow
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "ACTION_FLOW",
                f"After {player.name}'s {action.value}: checking round completion",
                {
                    "player": player.name,
                    "action": action.value,
                    "amount": amount,
                    "current_action_player": self.action_player_index,
                },
            )

        # Check if round is complete BEFORE advancing action player
        round_complete = self._is_round_complete()
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "DEBUG",
                "ACTION_FLOW",
                f"Round complete check result: {round_complete}",
                {
                    "round_complete": round_complete,
                    "actions_this_round": self.actions_this_round,
                },
            )

        if round_complete:
            # Round complete detected
            self._handle_round_complete()
        else:
            # Round not complete - advance to next player
            if hasattr(self, "session_logger") and self.session_logger:
                self.session_logger.log_system(
                    "DEBUG",
                    "ACTION_FLOW",
                    "Advancing to next action player",
                    {},
                )
            self._advance_action_player()
            # Only emit display state event if round is not complete to avoid
            # conflicts
            self._emit_display_state_event()

        return True

    def _advance_action_player(self):
        """Advance to the next action player."""
        next_index = self._find_next_active_player(self.action_player_index)
        if next_index == -1:
            self.transition_to(PokerState.END_HAND)
            return
        self.action_player_index = next_index
        self._emit_event(
            GameEvent(
                event_type="action_required",
                timestamp=time.time(),
                player_name=self.game_state.players[next_index].name,
                data={"player_index": next_index}  # Include player_index for UI button enabling
            )
        )

    def _is_round_complete(self) -> bool:
        """Check if the current betting round is complete.

        Fix: Ensure ALL actionable players have had a chance to act, not just
        count total actions. This prevents Big Blind from being skipped.
        """
        players = self.game_state.players
        # Players still in the hand
        active_players = [
            p for p in players if not p.has_folded and p.is_active
        ]
        # Players who can actually take an action (not all-in and with chips)
        actionable_players = [
            p for p in active_players if not p.is_all_in and p.stack > 0
        ]

        # If everyone but one is out (folded/all-in/zero stack), the round is
        # done
        if len(actionable_players) <= 1:
            return True

        # Bets equalization across active players (include all-in for equality)
        max_bet = (
            max(p.current_bet for p in active_players)
            if active_players
            else 0.0
        )
        all_equal = all(
            (p.current_bet == max_bet) or p.is_all_in for p in active_players
        )

        if not all_equal:
            return False

        # CRITICAL FIX: Check that ALL actionable players have actually acted this round
        # Don't just count total actions - ensure each actionable player got a turn
        actionable_player_names = {
            p.name for p in actionable_players
        }
        
        # Check if all actionable players have acted in this round
        all_actionable_acted = actionable_player_names.issubset(self.players_acted_this_round)
        
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "DEBUG", "ROUND_COMPLETION",
                f"Round completion check: actionable={len(actionable_players)}, "
                f"all_equal={all_equal}, all_acted={all_actionable_acted}",
                {
                    "actionable_names": list(actionable_player_names),
                    "acted_names": list(self.players_acted_this_round),
                    "missing_players": list(actionable_player_names - self.players_acted_this_round)
                }
            )
        
        return all_actionable_acted

    def _handle_round_complete(self):
        """Handle completion of a betting round."""
        # Round complete on current street (reduced console verbosity)
        if hasattr(self, "session_logger") and self.session_logger:
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                f"Round complete: {self.current_state}",
                {
                    "current_state": self.current_state.name,
                    "actions_this_round": self.actions_this_round,
                    "players_acted": len(self.players_acted_this_round),
                    "street": self.game_state.street,
                },
            )

        # Capture snapshot of bets BEFORE clearing, so UI can animate bets →
        # pot
        player_bets_snapshot = [
            {
                "index": i,
                "name": p.name,
                "amount": getattr(p, "current_bet", 0.0),
            }
            for i, p in enumerate(self.game_state.players)
        ]

        self._reset_bets_for_new_round()
        self.actions_this_round = 0
        self.players_acted_this_round.clear()  # Reset for new betting round

        # Check active players after reset
        active_players = [
            p
            for p in self.game_state.players
            if not p.has_folded and p.is_active
        ]

        if len(active_players) <= 1:
            self._safe_print(
                f"🏁 Only {len(active_players)} active players, ending hand"
            )
            self.transition_to(PokerState.END_HAND)
            return

        # Emit round complete event with snapshot of player bets and current
        # pot
        self._emit_event(
            GameEvent(
                event_type="round_complete",
                timestamp=time.time(),
                data={
                    "street": self.game_state.street,
                    "player_bets": player_bets_snapshot,
                    "pot": self.game_state.pot,
                },
            )
        )

        # Transition to next state based on current state
        if self.current_state == PokerState.PREFLOP_BETTING:
            # Log betting round completion to session (keep console clean)
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                "Preflop betting complete, transitioning to DEAL_FLOP",
                {},
            )
            self.transition_to(PokerState.DEAL_FLOP)
        elif self.current_state == PokerState.DEAL_FLOP:
            # Flop dealing complete, transitioning to FLOP_BETTING (logged via
            # session_logger)
            self.transition_to(PokerState.FLOP_BETTING)
        elif self.current_state == PokerState.FLOP_BETTING:
            # Log betting round completion to session (keep console clean)
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                "Flop betting complete, transitioning to DEAL_TURN",
                {},
            )
            self.transition_to(PokerState.DEAL_TURN)
        elif self.current_state == PokerState.DEAL_TURN:
            # Turn dealing complete, transitioning to TURN_BETTING (logged via
            # session_logger)
            self.transition_to(PokerState.TURN_BETTING)
        elif self.current_state == PokerState.TURN_BETTING:
            # Log betting round completion to session (keep console clean)
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                "Turn betting complete, transitioning to DEAL_RIVER",
                {},
            )
            self.transition_to(PokerState.DEAL_RIVER)
        elif self.current_state == PokerState.DEAL_RIVER:
            # River dealing complete, transitioning to RIVER_BETTING (logged
            # via session_logger)
            self.transition_to(PokerState.RIVER_BETTING)
        elif self.current_state == PokerState.RIVER_BETTING:
            # Log betting round completion to session (keep console clean)
            self.session_logger.log_system(
                "INFO",
                "ROUND_COMPLETE",
                "River betting complete, transitioning to SHOWDOWN",
                {},
            )
            self.transition_to(PokerState.SHOWDOWN)

        # Note: Display state event will be emitted by transition_to method

    def determine_winners(self, players: List[Player]) -> List[Player]:
        """Determine the winners among the given players using deuces library."""
        if not players:
            return []

        if len(players) == 1:
            return players

        # Evaluate hands using deuces
        player_evaluations = []
        for player in players:
            if len(player.cards) == 2:
                hand_eval = self.hand_evaluator.evaluate_hand(
                    player.cards, self.game_state.board
                )
                player_evaluations.append((player, hand_eval))

                # Debug logging for hand evaluation
                score = hand_eval.get("hand_score", 9999)
                desc = hand_eval.get("hand_description", "Unknown")
                self._safe_print(
                    f"🃏 {player.name}: {player.cards} + {self.game_state.board} = {desc} (score={score})"
                )

        # Handle case where no valid hands are evaluated
        if not player_evaluations:
            return players

        # Use deuces evaluator to determine winners
        winners_with_evals = self.hand_evaluator.determine_winners(
            player_evaluations
        )
        winners = [player for player, eval_data in winners_with_evals]

        # Debug logging for final winner determination
        if len(winners) == 1:
            winner_eval = winners_with_evals[0][1]
            hand_desc = winner_eval.get("hand_description", "Unknown")
            best_five = winner_eval.get("best_five_cards", [])
            five_cards_str = f" [{', '.join(best_five)}]" if best_five else ""
            self._safe_print(
                f"🏆 Single winner: {winners[0].name} with {hand_desc}{five_cards_str}"
            )
        else:
            winner_names = [w.name for w in winners]
            winner_eval = winners_with_evals[0][1]
            hand_desc = winner_eval.get("hand_description", "Unknown")
            best_five = winner_eval.get("best_five_cards", [])
            five_cards_str = f" [{', '.join(best_five)}]" if best_five else ""
            self._safe_print(
                f"🤝 Split pot: {', '.join(winner_names)} tie with {hand_desc}{five_cards_str}"
            )

        return winners

    def get_action_player(self) -> Optional[Player]:
        """Get the current action player."""
        try:
            if not self.game_state or not self.game_state.players:
                return None

            if 0 <= self.action_player_index < len(self.game_state.players):
                player = self.game_state.players[self.action_player_index]
                # Ensure we're returning a Player object, not a string
                if hasattr(player, "is_human"):
                    return player
                else:
                    # Log the issue for debugging
                    self.session_logger.log_system(
                        "ERROR",
                        "STATE_MACHINE",
                        f"get_action_player returning non-Player object: {type(player)} - {player}",
                        {
                            "action_player_index": self.action_player_index,
                            "players_count": len(self.game_state.players),
                            "player_type": str(type(player)),
                        },
                    )
                    return None
            return None
        except Exception as e:
            # Log any exceptions that occur
            self.session_logger.log_system(
                "ERROR",
                "STATE_MACHINE",
                f"Exception in get_action_player: {e}",
                {
                    "action_player_index": getattr(
                        self, "action_player_index", "unknown"
                    ),
                    "players_count": (
                        len(getattr(self.game_state, "players", []))
                        if self.game_state
                        else 0
                    ),
                },
            )
            return None

    def get_game_info(self) -> Dict[str, Any]:
        """Get comprehensive game information."""
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
                    "cards": (
                        p.cards
                        if (
                            p.is_human
                            or self.current_state
                            in [
                                PokerState.SHOWDOWN,
                                PokerState.END_HAND,
                            ]
                        )
                        else ["**", "**"]
                    ),
                }
                for p in self.game_state.players
            ],
            "action_player": self.action_player_index,
            "street": self.game_state.street,
            "hand_number": self.hand_number,
            "dealer_position": self.dealer_position,
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
            "max_bet": player.stack,
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
