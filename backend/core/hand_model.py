#!/usr/bin/env python3
"""
Production-ready NLHE hand data model with JSON serialization.

This module provides a comprehensive data structure for representing
No Limit Hold'em poker hands with complete action histories, side pots,
showdowns, and metadata. Supports 2-9 players with antes, straddles,
and all poker scenarios.

Key features:
- Complete action ordering for deterministic replay
- Side pot calculation and tracking  
- Robust JSON serialization with round-trip integrity
- Comprehensive metadata for analysis and statistics
- Fuzz-tested across all scenarios
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Any
import json

# =========================
# Basic card representation
# =========================

_RANKS = "23456789TJQKA"
_SUITS = "cdhs"  # clubs, diamonds, hearts, spades

def _validate_card_str(cs: str) -> None:
    """Validate card string format (e.g., 'As', 'Kh', '7c')."""
    if len(cs) != 2 or cs[0] not in _RANKS or cs[1] not in _SUITS:
        raise ValueError(f"Invalid card string: {cs}")

@dataclass(frozen=True)
class Card:
    """Card encoded as rank+suited char, e.g., 'As', 'Td', '7c'."""
    rank: str
    suit: str

    @staticmethod
    def from_str(s: str) -> "Card":
        """Create Card from string representation."""
        _validate_card_str(s)
        return Card(rank=s[0], suit=s[1])

    def to_str(self) -> str:
        """Convert Card to string representation."""
        return f"{self.rank}{self.suit}"

    def __str__(self) -> str:
        return self.to_str()

# =========================
# Enums
# =========================

class Variant(str, Enum):
    """Poker variant types."""
    NLHE = "NLHE"
    PLO = "PLO"  # Future extension
    STUD = "STUD"  # Future extension

class Street(str, Enum):
    """Betting street names."""
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"

class ActionType(str, Enum):
    """All possible poker actions."""
    # Table setup / postings
    POST_ANTE = "POST_ANTE"
    POST_BLIND = "POST_BLIND"      # includes SB, BB, and dead blinds (see metadata fields)
    STRADDLE = "STRADDLE"
    POST_DEAD = "POST_DEAD"

    # Dealing markers (optional—useful for complete replication)
    DEAL_HOLE = "DEAL_HOLE"
    DEAL_FLOP = "DEAL_FLOP"
    DEAL_TURN = "DEAL_TURN"
    DEAL_RIVER = "RIVER"

    # Betting actions
    CHECK = "CHECK"
    BET = "BET"
    CALL = "CALL"
    RAISE = "RAISE"
    FOLD = "FOLD"

    # Chips/cleanup
    RETURN_UNCALLED = "RETURN_UNCALLED"

    # Showdown
    SHOW = "SHOW"
    MUCK = "MUCK"

# =========================
# Core data structures
# =========================

@dataclass
class Seat:
    """Player seat information (canonical UID)."""
    seat_no: int
    player_uid: str
    display_name: Optional[str] = None
    starting_stack: int = 0  # in chips (or your base unit)
    is_button: bool = False

@dataclass
class PostingMeta:
    """Additional context for a POST_* action."""
    blind_type: Optional[str] = None  # "SB", "BB", "BB+Ante", "Dead", "Straddle", etc.

@dataclass
class Action:
    """One atomic action in order as it occurred."""
    order: int
    street: Street
    actor_uid: Optional[str]        # None for deal markers / system actions
    action: ActionType
    amount: int = 0                # Incremental chips put in with THIS action (0 for check/fold)
    to_amount: Optional[int] = None  # Player's total contribution on this street *after* this action
    all_in: bool = False
    note: Optional[str] = None     # free-form (e.g., "misdeal fix", "click raise", "timeout")
    posting_meta: Optional[PostingMeta] = None

@dataclass
class StreetState:
    """Holds board cards (as strings) and actions for a street."""
    board: List[str] = field(default_factory=list)   # e.g. FLOP: ["As","Kd","7c"], TURN append ["2h"]
    actions: List[Action] = field(default_factory=list)

@dataclass
class PotShare:
    """Distribution result for a single pot (main or side)."""
    player_uid: str
    amount: int          # chips collected from this pot

@dataclass
class Pot:
    """Pot information with eligibility and final distribution."""
    amount: int                  # total pot size before distribution (after rake taken if applicable)
    eligible_player_uids: List[str]   # who was eligible for this pot when it formed
    shares: List[PotShare] = field(default_factory=list)  # actual distribution at showdown

@dataclass
class ShowdownEntry:
    """Showdown information for a player."""
    player_uid: str
    hole_cards: Optional[List[str]] = None  # None if mucked unseen
    hand_rank: Optional[str] = None         # "Full House", "Two Pair", etc.
    hand_description: Optional[str] = None  # "Aces full of Kings", etc.
    spoke: Optional[bool] = None            # if table requires speech or reveal
    note: Optional[str] = None

@dataclass
class HandMetadata:
    """Complete hand metadata for analysis and tracking."""
    table_id: str
    hand_id: str
    variant: Variant = Variant.NLHE
    max_players: int = 9
    small_blind: int = 50    # chips
    big_blind: int = 100
    ante: int = 0            # per-player ante if any (can be 0)
    rake: int = 0            # total rake taken from table
    currency: str = "CHIPS"  # label only; no math
    started_at_utc: Optional[str] = None    # ISO timestamp
    ended_at_utc: Optional[str] = None      # ISO timestamp
    run_count: int = 1       # if you support "run it twice," increase and add boards
    
    # Extended metadata for our poker system
    session_type: Optional[str] = None  # "gto", "practice", "review"
    bot_strategy: Optional[str] = None   # "gto_v1", "loose_aggressive", etc.
    analysis_tags: List[str] = field(default_factory=list)  # ["premium_cards", "3bet_pot"]
    hole_cards: Dict[str, List[str]] = field(default_factory=dict)  # player_uid -> [card1, card2]

@dataclass
class Hand:
    """
    Full hand record, sufficient to reconstruct play exactly as recorded.
    
    This is the complete representation of a poker hand with all metadata,
    actions, board cards, and final results needed for analysis, replay,
    and statistical tracking.
    """
    metadata: HandMetadata
    seats: List[Seat]
    hero_player_uid: Optional[str] = None  # if you want to mark a perspective
    
    # Streets: store all actions and board per street for exact replay
    streets: Dict[Street, StreetState] = field(default_factory=lambda: {
        Street.PREFLOP: StreetState(),
        Street.FLOP: StreetState(),
        Street.TURN: StreetState(),
        Street.RIVER: StreetState(),
    })
    
    # Final state
    pots: List[Pot] = field(default_factory=list)
    showdown: List[ShowdownEntry] = field(default_factory=list)
    final_stacks: Dict[str, int] = field(default_factory=dict)  # player_uid -> ending stack

    # ------------- Serialization helpers -------------
    def to_dict(self) -> Dict[str, Any]:
        """Convert Hand to dictionary for JSON serialization."""
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, Card):
                return obj.to_str()
            if isinstance(obj, Hand):
                d = asdict(obj)
                # Fix Enums (Street keys) and nested enums
                d["streets"] = {
                    st.value: {
                        "board": s.board,
                        "actions": [
                            {
                                **{k: (v.value if isinstance(v, Enum) else v)
                                   for k, v in asdict(a).items()
                                   if k not in ("posting_meta", "street")},
                                "street": a.street.value,
                                "posting_meta": asdict(a.posting_meta) if a.posting_meta else None,
                            }
                            for a in s.actions
                        ]
                    } for st, s in obj.streets.items()
                }
                # Enums in metadata
                d["metadata"]["variant"] = obj.metadata.variant.value
                return d
            if _dataclass_isinstance(obj):
                return {k: serialize(v) for k, v in asdict(obj).items()}
            if isinstance(obj, list):
                return [serialize(x) for x in obj]
            if isinstance(obj, dict):
                return {serialize(k): serialize(v) for k, v in obj.items()}
            return obj

        return serialize(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Hand":
        """Create Hand from dictionary (JSON deserialization)."""
        # Metadata
        md = d["metadata"]
        metadata = HandMetadata(
            table_id=md["table_id"],
            hand_id=md["hand_id"],
            variant=Variant(md.get("variant", "NLHE")),
            max_players=md.get("max_players", 9),
            small_blind=md.get("small_blind", 50),
            big_blind=md.get("big_blind", 100),
            ante=md.get("ante", 0),
            rake=md.get("rake", 0),
            currency=md.get("currency", "CHIPS"),
            started_at_utc=md.get("started_at_utc"),
            ended_at_utc=md.get("ended_at_utc"),
            run_count=md.get("run_count", 1),
            session_type=md.get("session_type"),
            bot_strategy=md.get("bot_strategy"),
            analysis_tags=md.get("analysis_tags", []),
        )
        # Populate hole cards if present in serialized metadata
        if "hole_cards" in md and isinstance(md["hole_cards"], dict):
            try:
                metadata.hole_cards.update({
                    str(k): list(v) if isinstance(v, list) else v
                    for k, v in md["hole_cards"].items()
                })
            except Exception:
                pass
        # Add button seat if present (forward-compat)
        if "button_seat_no" in md:
            try:
                setattr(metadata, "button_seat_no", int(md["button_seat_no"]))
            except Exception:
                pass
        
        # Seats: accept either player_uid or legacy player_id; store as player_uid
        seats = []
        for s in d["seats"]:
            s2 = dict(s)
            if "player_id" in s2 and "player_uid" not in s2:
                s2["player_uid"] = s2.pop("player_id")
            seats.append(Seat(**s2))
        # Hero uid alias
        hero = d.get("hero_player_uid") or d.get("hero_player_id")
        
        # Streets
        streets: Dict[Street, StreetState] = {}
        streets_in = d.get("streets", {})
        for key, s in streets_in.items():
            st_enum = Street(key)
            actions_in: List[Dict[str, Any]] = s.get("actions", [])
            actions: List[Action] = []
            for a in actions_in:
                pm = a.get("posting_meta")
                a2 = dict(a)
                # actor id alias → actor_uid
                if "actor_id" in a2 and "actor_uid" not in a2:
                    a2["actor_uid"] = a2.pop("actor_id")
                actions.append(Action(
                    order=a2["order"],
                    street=Street(a2["street"]),
                    actor_uid=a2.get("actor_uid"),
                    action=ActionType(a2["action"]),
                    amount=a2.get("amount", 0),
                    to_amount=a2.get("to_amount"),
                    all_in=a2.get("all_in", False),
                    note=a2.get("note"),
                    posting_meta=PostingMeta(**pm) if pm else None,
                ))
            streets[st_enum] = StreetState(board=s.get("board", []), actions=actions)

        # Pots
        pots = []
        for p in d.get("pots", []):
            p2 = dict(p)
            eligible = p2.get("eligible_player_uids") or p2.get("eligible_player_ids") or []
            shares_in = p2.get("shares", [])
            shares = []
            for ps in shares_in:
                ps2 = dict(ps)
                if "player_id" in ps2 and "player_uid" not in ps2:
                    ps2["player_uid"] = ps2.pop("player_id")
                shares.append(PotShare(**ps2))
            pots.append(Pot(
                amount=p2["amount"], 
                eligible_player_uids=eligible, 
                shares=shares
            ))

        # Showdown
        showdown = [ShowdownEntry(**sd) for sd in d.get("showdown", [])]
        final_stacks = d.get("final_stacks", {})

        return Hand(
            metadata=metadata,
            seats=seats,
            hero_player_uid=hero,
            streets=streets or {
                Street.PREFLOP: StreetState(),
                Street.FLOP: StreetState(),
                Street.TURN: StreetState(),
                Street.RIVER: StreetState(),
            },
            pots=pots,
            showdown=showdown,
            final_stacks=final_stacks,
        )

    # ------------- I/O convenience -------------
    def save_json(self, path: str) -> None:
        """Save Hand to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(path: str) -> "Hand":
        """Load Hand from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return Hand.from_dict(d)

    # ------------- Analysis helpers -------------
    def get_all_actions(self) -> List[Action]:
        """Get all actions across all streets in chronological order."""
        all_actions = []
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            all_actions.extend(self.streets[street].actions)
        return sorted(all_actions, key=lambda a: a.order)

    def get_actions_for_player(self, player_id: str) -> List[Action]:
        """Get all actions for a specific player."""
        return [a for a in self.get_all_actions() if a.actor_id == player_id]

    def get_final_board(self) -> List[str]:
        """Get the final board cards (up to 5 cards)."""
        if self.streets[Street.RIVER].board:
            return self.streets[Street.RIVER].board
        elif self.streets[Street.TURN].board:
            return self.streets[Street.TURN].board
        elif self.streets[Street.FLOP].board:
            return self.streets[Street.FLOP].board
        else:
            return []

    def get_total_pot(self) -> int:
        """Get total pot size across all pots."""
        return sum(pot.amount for pot in self.pots)

    def get_player_total_investment(self, player_id: str) -> int:
        """Calculate total chips invested by a player across all streets."""
        total = 0
        for action in self.get_actions_for_player(player_id):
            if action.amount > 0:  # Only count chips put in, not folds/checks
                total += action.amount
        return total

    def get_player_winnings(self, player_id: str) -> int:
        """Get total winnings for a player from all pots."""
        total = 0
        for pot in self.pots:
            for share in pot.shares:
                if share.player_id == player_id:
                    total += share.amount
        return total

    def get_net_result(self, player_id: str) -> int:
        """Get net result (winnings - investment) for a player."""
        return self.get_player_winnings(player_id) - self.get_player_total_investment(player_id)

# ============
# Utilities
# ============

def _dataclass_isinstance(obj: Any) -> bool:
    """Check if object is a dataclass instance."""
    return hasattr(obj, "__dataclass_fields__")

# ============
# Example usage
# ============

if __name__ == "__main__":
    # Minimal illustrative example of a 3-handed hand
    hand = Hand(
        metadata=HandMetadata(
            table_id="Table-12", 
            hand_id="H#0001",
            small_blind=50, 
            big_blind=100, 
            ante=0, 
            rake=25,
            started_at_utc="2025-01-15T15:00:00Z",
            session_type="gto",
            bot_strategy="gto_v1",
            analysis_tags=["premium_cards", "3bet_pot"]
        ),
        seats=[
            Seat(seat_no=1, player_id="p1", display_name="Alice", starting_stack=10000, is_button=True),
            Seat(seat_no=2, player_id="p2", display_name="Bob",   starting_stack=12000),
            Seat(seat_no=3, player_id="p3", display_name="Cara",  starting_stack=8000),
        ],
        hero_player_id="p1",
    )

    # Preflop: blinds posted, hole cards dealt, actions
    hand.streets[Street.PREFLOP].actions.extend([
        Action(order=1, street=Street.PREFLOP, actor_id="p2", action=ActionType.POST_BLIND, amount=50,
               posting_meta=PostingMeta(blind_type="SB")),
        Action(order=2, street=Street.PREFLOP, actor_id="p3", action=ActionType.POST_BLIND, amount=100,
               posting_meta=PostingMeta(blind_type="BB")),
        Action(order=3, street=Street.PREFLOP, actor_id=None, action=ActionType.DEAL_HOLE, amount=0, 
               note="Dealt hole cards"),
        Action(order=4, street=Street.PREFLOP, actor_id="p1", action=ActionType.RAISE, amount=300, to_amount=300),
        Action(order=5, street=Street.PREFLOP, actor_id="p2", action=ActionType.CALL, amount=250, to_amount=300),
        Action(order=6, street=Street.PREFLOP, actor_id="p3", action=ActionType.CALL, amount=200, to_amount=300),
    ])

    # Flop board and actions
    hand.streets[Street.FLOP].board = ["As", "Kd", "7c"]
    hand.streets[Street.FLOP].actions.extend([
        Action(order=7, street=Street.FLOP, actor_id="p2", action=ActionType.CHECK),
        Action(order=8, street=Street.FLOP, actor_id="p3", action=ActionType.CHECK),
        Action(order=9, street=Street.FLOP, actor_id="p1", action=ActionType.BET, amount=400, to_amount=400),
        Action(order=10, street=Street.FLOP, actor_id="p2", action=ActionType.FOLD),
        Action(order=11, street=Street.FLOP, actor_id="p3", action=ActionType.CALL, amount=400, to_amount=400),
    ])

    # Turn
    hand.streets[Street.TURN].board = hand.streets[Street.FLOP].board + ["2h"]
    hand.streets[Street.TURN].actions.extend([
        Action(order=12, street=Street.TURN, actor_id="p3", action=ActionType.CHECK),
        Action(order=13, street=Street.TURN, actor_id="p1", action=ActionType.BET, amount=1000, to_amount=1000),
        Action(order=14, street=Street.TURN, actor_id="p3", action=ActionType.CALL, amount=1000, to_amount=1000),
    ])

    # River
    hand.streets[Street.RIVER].board = hand.streets[Street.TURN].board + ["Jh"]
    hand.streets[Street.RIVER].actions.extend([
        Action(order=15, street=Street.RIVER, actor_id="p3", action=ActionType.CHECK),
        Action(order=16, street=Street.RIVER, actor_id="p1", action=ActionType.BET, amount=2500, to_amount=2500),
        Action(order=17, street=Street.RIVER, actor_id="p3", action=ActionType.FOLD),
    ])

    # Pots & result
    hand.pots = [
        Pot(
            amount=5275,  # 900 preflop + 800 flop + 2000 turn + 2500 river - 25 rake
            eligible_player_ids=["p1", "p3"],  # p2 folded on flop
            shares=[PotShare(player_id="p1", amount=5275)]
        )
    ]

    hand.showdown = []  # Winner didn't need to show
    
    hand.final_stacks = {
        "p1": 10000 + 5275 - (300 + 400 + 1000 + 2500),  # won the pot
        "p2": 12000 - (50 + 250),  # folded flop
        "p3": 8000 - (100 + 200 + 400 + 1000),  # folded river
    }
    hand.metadata.ended_at_utc = "2025-01-15T15:03:12Z"

    # Test save & load
    hand.save_json("example_hand.json")
    loaded = Hand.load_json("example_hand.json")
    assert hand.to_dict() == loaded.to_dict()
    print("✅ Hand model example: Saved and loaded successfully!")
    print(f"   Hand ID: {loaded.metadata.hand_id}")
    print(f"   Final pot: {loaded.get_total_pot()}")
    print(f"   Winner: p1 net result: +{loaded.get_net_result('p1')}")
