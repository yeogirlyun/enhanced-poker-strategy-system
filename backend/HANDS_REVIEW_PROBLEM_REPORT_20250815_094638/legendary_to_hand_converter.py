#!/usr/bin/env python3
"""
Legendary → Hand Model Converter

Purpose
-------
Convert the project's "legendary" hands JSON format (single file with
hands[...], players, board, and street-keyed actions) into the standardized
`Hand` model used everywhere else in the app for deterministic replay and
analysis.

Format detection
----------------
We treat an object as "legendary format" when all of the following are true:
- It has a `players` list of dicts (with at least name/seat/starting_stack)
- It has an `actions` dict with keys like `preflop`, `flop`, `turn`, `river`
- It optionally has a `board` dict with `flop/turn/river`

Result
------
Produces a `Hand` instance with populated `metadata`, `seats`, `streets`, and
optional `pots/showdown/final_stacks` (left empty unless future data suffices).

Notes
-----
- Player IDs are canonicalized to "Player{index+1}" in the order given by the
  `players` list to match our `HandModelDecisionEngine` expectation.
- Blind postings are inferred from the `players[].position` field when present.
- Action `action_type` strings are mapped to the `ActionType` enum; unknowns
  such as "all-in", "reraise", "3bet", "4bet" are treated as `RAISE`.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

# Internal imports (backend run-from-backend convention)
from core.hand_model import (
    Hand,
    HandMetadata,
    Seat,
    Street,
    StreetState,
    Action,
    ActionType,
    PostingMeta,
    Variant,
)


def is_legendary_hand_obj(obj: Dict[str, Any]) -> bool:
    """Return True if the given dict looks like a single legendary-format hand."""
    return isinstance(obj, dict) and "players" in obj and isinstance(obj.get("actions"), dict)


class LegendaryToHandConverter:
    """Converter for a single legendary-format hand dict → `Hand` object."""

    def __init__(self) -> None:
        # Map lowercase strings found in legendary file to ActionType
        self._action_type_map: Dict[str, ActionType] = {
            "fold": ActionType.FOLD,
            "check": ActionType.CHECK,
            "call": ActionType.CALL,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE,
            # Common aliases → treat as raise
            "all-in": ActionType.RAISE,
            "allin": ActionType.RAISE,
            "reraise": ActionType.RAISE,
            "3bet": ActionType.RAISE,
            "4bet": ActionType.RAISE,
            "5bet": ActionType.RAISE,
        }

    @staticmethod
    def _to_int_chips(value: Any) -> int:
        try:
            return int(round(float(value)))
        except Exception:
            return 0

    def _build_player_id_map(self, players: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create a mapping from either seat or name → canonical player_id.

        We canonicalize to Player{index+1} in the order given by the players list
        so the hand model aligns with our decision engine's expectations.
        """
        id_by_seat: Dict[str, str] = {}
        id_by_name: Dict[str, str] = {}

        for idx, p in enumerate(players):
            pid = f"Player{idx + 1}"
            seat = str(p.get("seat", idx + 1))
            name = str(p.get("name", pid))
            id_by_seat[seat] = pid
            id_by_name[name] = pid
        # Prefer seat mapping when available; fall back to name
        # Use a merged dict where seat keys take precedence
        merged: Dict[str, str] = {**id_by_name, **id_by_seat}
        return merged

    def _infer_blinds(self, players: List[Dict[str, Any]]) -> Dict[str, str]:
        """Return a role mapping: {player_id: 'SB'|'BB'} when positions provided."""
        roles: Dict[str, str] = {}
        pid_map = self._build_player_id_map(players)
        for p in players:
            pos = str(p.get("position", "")).upper()
            seat_key = str(p.get("seat", ""))
            pid = pid_map.get(seat_key) or pid_map.get(p.get("name", ""))
            if not pid:
                continue
            if pos == "SB":
                roles[pid] = "SB"
            elif pos == "BB":
                roles[pid] = "BB"
        return roles

    def _create_metadata(self, src: Dict[str, Any], players_count: int) -> HandMetadata:
        game_cfg = src.get("game_config", {})
        small_blind = self._to_int_chips(game_cfg.get("small_blind", 5))
        big_blind = self._to_int_chips(game_cfg.get("big_blind", 10))

        md = HandMetadata(
            table_id=src.get("table", {}).get("name", "Legendary-Table-1"),
            hand_id=src.get("id", "LEG-UNKNOWN"),
            variant=Variant.NLHE,
            max_players=int(src.get("table", {}).get("max_players", players_count or 6)),
            small_blind=small_blind,
            big_blind=big_blind,
            ante=self._to_int_chips(game_cfg.get("ante", 0)),
            currency="CHIPS",
            session_type="review",
        )

        # Add hole cards into metadata.hole_cards if present
        pid_map = self._build_player_id_map(src.get("players", []))
        for p in src.get("players", []):
            pid = pid_map.get(str(p.get("seat", ""))) or pid_map.get(p.get("name", ""))
            cards = p.get("hole_cards") or []
            if pid and cards and cards != ["**", "**"]:
                md.hole_cards[pid] = list(cards)

        return md

    def _create_seats(self, players: List[Dict[str, Any]]) -> List[Seat]:
        seats: List[Seat] = []
        for idx, p in enumerate(players):
            pid = f"Player{idx + 1}"
            seats.append(
                Seat(
                    seat_no=int(p.get("seat", idx + 1)),
                    player_id=pid,
                    display_name=p.get("name", pid),
                    starting_stack=self._to_int_chips(p.get("starting_stack", p.get("stack", 1000))),
                    is_button=(idx == 0),
                )
            )
        return seats

    def _set_board(self, src: Dict[str, Any]) -> Dict[Street, StreetState]:
        streets: Dict[Street, StreetState] = {
            Street.PREFLOP: StreetState(),
            Street.FLOP: StreetState(),
            Street.TURN: StreetState(),
            Street.RIVER: StreetState(),
        }
        board = src.get("board", {})
        flop = board.get("flop", [])
        turn = board.get("turn", [])
        river = board.get("river", [])

        if flop:
            streets[Street.FLOP].board = list(flop)
        if turn:
            streets[Street.TURN].board = list(flop) + list(turn[:1])
        if river:
            base = streets[Street.TURN].board or (list(flop) + list(turn[:1]))
            streets[Street.RIVER].board = base + list(river[:1])
        return streets

    def _append_blind_postings(self, streets: Dict[Street, StreetState], roles: Dict[str, str], md: HandMetadata) -> int:
        """Append blind posting `Action`s at the start of PREFLOP. Returns next order index."""
        order = 1
        # Small blind then big blind
        for pid, blind_type in ([(k, v) for k, v in roles.items() if v == "SB"] + [(k, v) for k, v in roles.items() if v == "BB"]):
            amount = md.small_blind if blind_type == "SB" else md.big_blind
            streets[Street.PREFLOP].actions.append(
                Action(
                    order=order,
                    street=Street.PREFLOP,
                    actor_id=pid,
                    action=ActionType.POST_BLIND,
                    amount=amount,
                    to_amount=amount,
                    posting_meta=PostingMeta(blind_type=blind_type),
                )
            )
            order += 1
        return order

    def _convert_street_actions(
        self,
        actions_by_street: Dict[str, List[Dict[str, Any]]],
        streets: Dict[Street, StreetState],
        players: List[Dict[str, Any]],
        first_order: int,
    ) -> None:
        pid_map = self._build_player_id_map(players)
        order = first_order

        def map_street_key(key: str) -> Street:
            k = (key or "").lower()
            if k == "preflop":
                return Street.PREFLOP
            if k == "flop":
                return Street.FLOP
            if k == "turn":
                return Street.TURN
            if k == "river":
                return Street.RIVER
            return Street.PREFLOP

        for street_key in ["preflop", "flop", "turn", "river"]:
            items = actions_by_street.get(street_key, []) or []
            street = map_street_key(street_key)
            for a in items:
                # Identify player
                seat_key = str(a.get("player_seat", a.get("actor", "")))
                name_key = a.get("player_name", "")
                pid = pid_map.get(seat_key) or pid_map.get(name_key)
                # Map action type
                atype_str = str(a.get("action_type", "fold")).lower()
                atype = self._action_type_map.get(atype_str, ActionType.FOLD)
                amount = self._to_int_chips(a.get("amount", 0))

                streets[street].actions.append(
                    Action(
                        order=order,
                        street=street,
                        actor_id=pid,
                        action=atype,
                        amount=amount,
                        to_amount=amount if atype in (ActionType.BET, ActionType.RAISE, ActionType.CALL) else None,
                        all_in=(atype_str in ("all-in", "allin")),
                        note=None,
                    )
                )
                order += 1

    def convert_hand(self, src: Dict[str, Any]) -> Hand:
        if not is_legendary_hand_obj(src):
            raise ValueError("Input is not a legendary-format hand dict")

        players = list(src.get("players", []))
        md = self._create_metadata(src, len(players))
        seats = self._create_seats(players)
        streets = self._set_board(src)
        roles = self._infer_blinds(players)
        next_order = self._append_blind_postings(streets, roles, md)
        self._convert_street_actions(src.get("actions", {}), streets, players, next_order)

        return Hand(
            metadata=md,
            seats=seats,
            hero_player_id=seats[0].player_id if seats else None,
            streets=streets,
            pots=[],
            showdown=[],
            final_stacks={},
        )


def convert_legendary_collection(collection: Dict[str, Any]) -> List[Hand]:
    """Convert a top-level legendary file with `hands: [...]` into `List[Hand]`."""
    hands_in = collection.get("hands", []) or []
    conv = LegendaryToHandConverter()
    results: List[Hand] = []
    for item in hands_in:
        if is_legendary_hand_obj(item):
            results.append(conv.convert_hand(item))
    return results


