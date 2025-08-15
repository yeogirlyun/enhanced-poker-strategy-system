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
- Canonical UIDs are lowercased: seat{seat_no}
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
    """Return True if the given dict looks like a single legendary-format hand.

    Support both legacy shapes:
    - { players: [...], actions: {preflop:[...], flop:[...], ...}, board: {...} }
    - { players_involved: [...], setup: {...}, actions: [...], board: [...] }
    """
    if not isinstance(obj, dict):
        return False
    if "players" in obj and isinstance(obj.get("actions"), dict):
        return True
    # Support the source format present in backend/tools_data_generation/legendary_hands.json
    if "players_involved" in obj and isinstance(obj.get("actions"), list):
        return True
    return False


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

    def _build_player_uid_map(self, players: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create a mapping from either seat or name → canonical player_uid (seatN)."""
        uid_by_seat: Dict[str, str] = {}
        uid_by_name: Dict[str, str] = {}
        for idx, p in enumerate(players):
            seat = str(p.get("seat", idx + 1))
            uid = f"seat{int(seat)}"
            name = str(p.get("name", uid))
            uid_by_seat[seat] = uid
            uid_by_name[name] = uid
        return {**uid_by_name, **uid_by_seat}

    def _infer_blinds(self, players: List[Dict[str, Any]]) -> Dict[str, str]:
        """Return a role mapping: {player_uid: 'SB'|'BB'} when positions provided."""
        roles: Dict[str, str] = {}
        uid_map = self._build_player_uid_map(players)
        for p in players:
            pos = str(p.get("position", "")).upper()
            seat_key = str(p.get("seat", ""))
            uid = uid_map.get(seat_key) or uid_map.get(p.get("name", ""))
            if not uid:
                continue
            if pos == "SB":
                roles[uid] = "SB"
            elif pos == "BB":
                roles[uid] = "BB"
        if not roles:
            # Fallback: derive two smallest seats as SB/BB
            seat_numbers = sorted(int(p.get("seat", i + 1)) for i, p in enumerate(players))
            if len(seat_numbers) >= 2:
                sb_uid = f"seat{seat_numbers[0] if len(seat_numbers)==2 else seat_numbers[1]}"
                bb_uid = f"seat{seat_numbers[1] if len(seat_numbers)==2 else seat_numbers[2]}"
                roles[sb_uid] = "SB"
                roles[bb_uid] = "BB"
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
        button_seat = src.get("table", {}).get("button_seat")
        if button_seat is not None:
            try:
                md.__dict__["button_seat_no"] = int(button_seat)
            except Exception:
                pass

        # Hole cards from players
        uid_map = self._build_player_uid_map(src.get("players", []))
        for p in src.get("players", []):
            uid = uid_map.get(str(p.get("seat", ""))) or uid_map.get(p.get("name", ""))
            cards = p.get("hole_cards") or []
            if uid and cards and cards != ["**", "**"]:
                md.hole_cards[uid] = list(cards)
        # Also support setup.player_cards
        setup = src.get("setup", {}) or {}
        pc_raw = setup.get("player_cards", {}) or {}
        if isinstance(pc_raw, list):
            for idx, v in enumerate(pc_raw):
                uid = f"seat{idx+1}"
                if isinstance(v, list) and len(v) == 2 and v != ["**","**"]:
                    md.hole_cards[uid] = list(v)
        elif isinstance(pc_raw, dict):
            for k, v in pc_raw.items():
                try:
                    idx = int(k)
                except Exception:
                    continue
                uid = f"seat{idx+1}"
                if isinstance(v, list) and len(v) == 2 and v != ["**","**"]:
                    md.hole_cards[uid] = list(v)

        return md

    def _create_seats(self, players: List[Dict[str, Any]], src: Dict[str, Any]) -> List[Seat]:
        seats: List[Seat] = []
        ordered = sorted(
            [(int(p.get("seat", i + 1)), i, p) for i, p in enumerate(players)],
            key=lambda x: x[0]
        )
        for real_seat, idx, p in ordered:
            uid = f"seat{int(real_seat)}"
            seats.append(
                Seat(
                    seat_no=int(real_seat),
                    player_uid=uid,
                    display_name=p.get("name", uid),
                    starting_stack=self._to_int_chips(p.get("starting_stack", p.get("stack", 1000))),
                    is_button=(int(real_seat) == int(src.get("table", {}).get("button_seat", 1))),
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
        if isinstance(board, dict):
            flop = board.get("flop", [])
            turn = board.get("turn", [])
            river = board.get("river", [])
        else:
            cards = list(board) if isinstance(board, list) else []
            flop, turn, river = cards[:3], cards[3:4], cards[4:5]

        if flop:
            streets[Street.FLOP].board = list(flop)
        if turn:
            streets[Street.TURN].board = list(flop) + list(turn[:1])
        if river:
            base = streets[Street.TURN].board or (list(flop) + list(turn[:1]))
            streets[Street.RIVER].board = base + list(river[:1])
        return streets

    def _append_blind_postings(self, streets: Dict[Street, StreetState], roles: Dict[str, str], md: HandMetadata) -> int:
        order = 1
        for uid, blind_type in ([(k, v) for k, v in roles.items() if v == "SB"] + [(k, v) for k, v in roles.items() if v == "BB"]):
            amount = md.small_blind if blind_type == "SB" else md.big_blind
            streets[Street.PREFLOP].actions.append(
                Action(
                    order=order,
                    street=Street.PREFLOP,
                    actor_uid=uid,
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
        actions_in,
        streets: Dict[Street, StreetState],
        players: List[Dict[str, Any]],
        first_order: int,
    ) -> None:
        uid_map = {str(p.get("seat", i+1)): f"seat{int(p.get('seat', i+1))}" for i, p in enumerate(players)}
        for p in players:
            name = p.get("name")
            if name:
                uid_map[name] = f"seat{int(p.get('seat', 0) or (players.index(p)+1))}"
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
        if isinstance(actions_in, list):
            for a in actions_in:
                street = map_street_key(str(a.get("street", "preflop")))
                uid = None
                if "player_index" in a:
                    try:
                        idx = int(a["player_index"]) + 1
                        uid = f"seat{idx}"
                    except Exception:
                        pass
                if not uid:
                    seat_key = str(a.get("player_seat", ""))
                    name_key = a.get("player_name", "")
                    uid = uid_map.get(seat_key) or uid_map.get(name_key)
                atype_str = str(a.get("action", a.get("action_type", "fold"))).lower()
                atype = self._action_type_map.get(atype_str, ActionType.FOLD)
                amount = self._to_int_chips(a.get("amount", 0))
                streets[street].actions.append(
                    Action(
                        order=order,
                        street=street,
                        actor_uid=uid,
                        action=atype,
                        amount=amount,
                        to_amount=amount if atype in (ActionType.BET, ActionType.RAISE, ActionType.CALL) else None,
                        all_in=(atype_str in ("all-in", "allin")),
                        note=None,
                    )
                )
                order += 1
            return

        actions_by_street: Dict[str, List[Dict[str, Any]]] = actions_in or {}
        for street_key in ["preflop", "flop", "turn", "river"]:
            items = actions_by_street.get(street_key, []) or []
            street = map_street_key(street_key)
            for a in items:
                seat_key = str(a.get("player_seat", a.get("actor", "")))
                name_key = a.get("player_name", "")
                uid = uid_map.get(seat_key) or uid_map.get(name_key)
                atype_str = str(a.get("action_type", "fold")).lower()
                atype = self._action_type_map.get(atype_str, ActionType.FOLD)
                amount = self._to_int_chips(a.get("amount", 0))
                streets[street].actions.append(
                    Action(
                        order=order,
                        street=street,
                        actor_uid=uid,
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

        if src.get("players"):
            players = list(src.get("players", []))
        else:
            players = []
            names = src.get("players_involved", []) or []
            setup = src.get("setup", {}) or {}
            stacks_raw = setup.get("player_stacks", {}) or {}
            seats_raw = setup.get("player_seats", {}) or {}
            stacks = {str(i): v for i, v in enumerate(stacks_raw)} if isinstance(stacks_raw, list) else dict(stacks_raw)
            seats = {str(i): v for i, v in enumerate(seats_raw)} if isinstance(seats_raw, list) else dict(seats_raw)
            for i, name in enumerate(names):
                seat_no = int(seats.get(str(i), i + 1))
                players.append({
                    "seat": seat_no,
                    "name": name,
                    "starting_stack": stacks.get(str(i), setup.get("starting_stack", 1000)),
                })
        md = self._create_metadata(src, len(players))
        seats = self._create_seats(players, src)
        streets = self._set_board(src)
        roles = self._infer_blinds(players)
        next_order = self._append_blind_postings(streets, roles, md)
        self._convert_street_actions(src.get("actions", {}), streets, players, next_order)

        return Hand(
            metadata=md,
            seats=seats,
            hero_player_uid=seats[0].player_uid if seats else None,
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


