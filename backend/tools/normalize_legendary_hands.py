#!/usr/bin/env python3
"""
Normalize legendary_hands.json into a canonical, verifier-passing dataset.

Fixes:
 - Ensures actor_uid on every action when derivable from seat label or player ids
 - Uppercases action verbs
 - Assigns/repairs per-street action.order (monotonic)
 - Infers dealer/button from preflop blinds for heads-up if missing

Writes <input_basename>_normalized.json alongside the input.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


def norm_uid(s: str) -> str:
    return "" if s is None else str(s).strip()


def load_json(path: Path):
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "hands" in data:
        return data["hands"]
    raise ValueError(f"Unexpected structure in {path}")


def save_json(path: Path, hands: List[Dict[str, Any]]):
    path.write_text(json.dumps({"hands": hands}, indent=2))


def build_seat_maps(seats: List[Dict[str, Any]]) -> Tuple[Dict[str, str], Dict[str, int]]:
    label_to_uid: Dict[str, str] = {}
    uid_to_seatno: Dict[str, int] = {}
    for s in seats:
        seat_no = s.get("seat_no")
        uid = norm_uid(s.get("player_uid") or s.get("player_id") or s.get("name"))
        if seat_no is not None:
            label_to_uid[f"seat{seat_no}"] = uid
        if uid:
            try:
                uid_to_seatno[uid] = int(seat_no) if seat_no is not None else None
            except Exception:
                uid_to_seatno[uid] = None
    return label_to_uid, uid_to_seatno


def infer_button_index(hand: Dict[str, Any], seats: List[Dict[str, Any]]) -> int:
    # Prefer explicit flag
    for i, s in enumerate(seats):
        if s.get("is_button"):
            return i
    # Prefer metadata.button_seat_no
    md = hand.get("metadata", {})
    btn_no = md.get("button_seat_no")
    if btn_no is not None:
        for i, s in enumerate(seats):
            if s.get("seat_no") == btn_no:
                return i
    # Infer from preflop SB (HU assumption)
    streets = hand.get("streets", {})
    pre = (streets.get("PREFLOP") or {}).get("actions") or []
    sb_uid = None
    sb_amt = md.get("small_blind")
    for a in pre:
        act = str(a.get("action") or "").upper()
        if act == "POST_BLIND":
            # If configured SB available, take matching amount; else take the smallest blind
            if sb_amt is not None and abs(float(a.get("amount") or 0.0) - float(sb_amt)) < 1e-6:
                sb_uid = norm_uid(a.get("actor_uid") or a.get("actor"))
                break
    if sb_uid is None:
        blinds = [a for a in pre if str(a.get("action") or "").upper() == "POST_BLIND"]
        if blinds:
            sb_uid = norm_uid(min(blinds, key=lambda x: float(x.get("amount") or 0.0)).get("actor_uid") or blinds[0].get("actor"))
    if sb_uid:
        for i, s in enumerate(seats):
            uid = norm_uid(s.get("player_uid") or s.get("player_id") or s.get("name"))
            if uid == sb_uid:
                return i
    return 0


def normalize_hand(hand: Dict[str, Any]) -> Dict[str, Any]:
    seats = hand.get("seats") or hand.get("players") or []
    label_to_uid, uid_to_seatno = build_seat_maps(seats)

    # Ensure metadata.button_seat_no
    md = hand.setdefault("metadata", {})
    if "button_seat_no" not in md:
        btn_index = infer_button_index(hand, seats)
        try:
            md["button_seat_no"] = int(seats[btn_index].get("seat_no") or btn_index + 1)
        except Exception:
            md["button_seat_no"] = btn_index + 1

    streets = hand.get("streets") or {}
    hand["streets"] = streets
    # Normalize action actor_uid and order per street
    for street_key in ("PREFLOP", "FLOP", "TURN", "RIVER"):
        st = streets.get(street_key)
        if not isinstance(st, dict):
            continue
        actions = st.get("actions") or []
        # Sort if orders present; otherwise keep sequence
        if any("order" in a for a in actions):
            try:
                actions = sorted(actions, key=lambda a: int(a.get("order", 0)))
            except Exception:
                pass
        # Rewrite actions
        new_actions = []
        order = 1
        for a in actions:
            act = str(a.get("action") or "").upper()
            amt = a.get("amount")
            try:
                amt = float(amt) if amt is not None else None
            except Exception:
                amt = None

            actor_uid = norm_uid(a.get("actor_uid"))
            if not actor_uid:
                # Try actor seat label
                actor = norm_uid(a.get("actor"))
                if actor in label_to_uid:
                    actor_uid = label_to_uid[actor]
                else:
                    # Try mapping from player_id/name
                    if actor:
                        actor_uid = actor
            # Build normalized action
            na = {
                "order": order,
                "street": street_key.upper(),
                "action": act,
            }
            if actor_uid:
                na["actor_uid"] = actor_uid
            if amt is not None:
                na["amount"] = amt
            new_actions.append(na)
            order += 1
        st["actions"] = new_actions
    return hand


def main():
    in_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "legendary_hands.json"
    hands = load_json(in_path)
    out_path = in_path.with_name(in_path.stem + "_normalized.json")
    normalized = [normalize_hand(h) for h in hands]
    save_json(out_path, normalized)
    print(f"WROTE: {out_path}")


if __name__ == "__main__":
    main()


