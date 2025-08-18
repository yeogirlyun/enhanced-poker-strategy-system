#!/usr/bin/env python3
"""
Legendary Hands Data Verifier

Validates legendary_hands.json for common data flaws that break the hands
review validator:
 - Canonical UID consistency (actor_uid must match a seat.player_uid or seat label)
 - Seats integrity (unique seat_no, unique player_uid, single button)
 - Action ordering (monotonic order per street)
 - Actor presence for every action
 - Amount sanity (non-negative; totals do not exceed total chips)

Outputs a JSON report and prints a concise summary.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


ALLOWED_ACTIONS = {
    "POST_BLIND", "CHECK", "BET", "CALL", "RAISE", "FOLD",
    # tolerate case variations
}


def load_legendary_hands(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "hands" in data:
        return data["hands"]
    raise ValueError(f"Unexpected structure in {path}")


def norm_uid(s: str) -> str:
    if s is None:
        return ""
    return str(s).strip()


def verify_hand(hand: Dict[str, Any], index: int) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    hand_id = hand.get("id") or f"hand_{index}"

    seats = hand.get("seats") or hand.get("players") or []
    if not isinstance(seats, list) or len(seats) < 2:
        errors.append("Invalid seats list (must be >= 2)")
        return {"hand_id": hand_id, "ok": False, "errors": errors, "warnings": warnings}

    # Seats integrity
    seat_nos = []
    player_uids = []
    button_count = 0
    for s in seats:
        seat_nos.append(s.get("seat_no"))
        player_uids.append(norm_uid(s.get("player_uid") or s.get("player_id") or s.get("name")))
        if s.get("is_button"):
            button_count += 1
    if len(set(seat_nos)) != len(seats):
        errors.append("Duplicate seat_no values")
    if None in seat_nos:
        warnings.append("Some seats missing seat_no")
    if len(set(player_uids)) != len(player_uids):
        errors.append("Duplicate player_uid across seats")
    if button_count not in (0, 1):
        errors.append(f"Invalid button count: {button_count}")

    # Build seat label mapping (e.g., seat1 -> player_uid)
    seat_label_to_uid: Dict[str, str] = {}
    for s in seats:
        sn = s.get("seat_no")
        if sn is not None:
            seat_label_to_uid[f"seat{sn}"] = norm_uid(s.get("player_uid") or s.get("player_id") or s.get("name"))

    # Streets/actions
    streets = hand.get("streets") or {}
    if not isinstance(streets, dict):
        errors.append("streets must be a dict")
        streets = {}

    # Track chip sanity (rough)
    total_starting = 0.0
    for s in seats:
        try:
            total_starting += float(s.get("starting_stack") or s.get("stack") or 0)
        except Exception:
            pass
    total_bet = 0.0

    for street_key, street_state in streets.items():
        actions = (street_state or {}).get("actions") or []
        last_order = -1
        for a in actions:
            # Order monotonic
            order = a.get("order")
            if order is None:
                warnings.append(f"{street_key}: action missing order")
            else:
                try:
                    if int(order) <= int(last_order):
                        errors.append(f"{street_key}: non-monotonic action order (order={order} after {last_order})")
                    last_order = order
                except Exception:
                    warnings.append(f"{street_key}: non-integer order: {order}")

            # Actor present and canonical (except for system actions)
            action_type = str(a.get("action") or "").upper()
            system_actions = {"DEAL_HOLE", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER", "SHOWDOWN"}
            
            actor = norm_uid(a.get("actor_uid") or a.get("actor") or a.get("player"))
            if not actor and action_type not in system_actions:
                errors.append(f"{street_key}: action missing actor_uid")
            elif actor and actor not in player_uids:
                # try seat label map
                mapped = seat_label_to_uid.get(actor)
                if mapped and mapped in player_uids:
                    warnings.append(f"{street_key}: actor '{actor}' mapped to player_uid '{mapped}'")
                else:
                    errors.append(f"{street_key}: actor '{actor}' not in seats")

            # Action type
            act = str(a.get("action") or "").upper()
            if act not in ALLOWED_ACTIONS:
                warnings.append(f"{street_key}: unknown action '{a.get('action')}'")

            # Amount sanity
            try:
                amt = float(a.get("amount") or 0.0)
                if amt < 0:
                    errors.append(f"{street_key}: negative amount {amt}")
                else:
                    if act in {"BET", "RAISE", "CALL", "POST_BLIND"}:
                        total_bet += amt
            except Exception:
                warnings.append(f"{street_key}: non-numeric amount: {a.get('amount')}")

    # Rough chip cap check
    if total_starting > 0 and total_bet > total_starting * 2:  # heads-up rough bound
        warnings.append(f"Total bet {total_bet} exceeds rough cap {total_starting*2}")

    ok = not errors
    return {"hand_id": hand_id, "ok": ok, "errors": errors, "warnings": warnings}


def main():
    # Optional argv[1]: path to hands json
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])
    else:
        data_path = Path(__file__).resolve().parents[1] / "data" / "legendary_hands.json"
    out_path = Path(__file__).resolve().parents[1] / "legendary_hands_verifier_report.json"

    try:
        hands = load_legendary_hands(data_path)
    except Exception as e:
        print(f"❌ Failed to load legendary hands: {e}")
        sys.exit(1)

    results = []
    ok_count = 0
    for i, hand in enumerate(hands):
        res = verify_hand(hand, i)
        if res.get("ok"):
            ok_count += 1
        results.append(res)

    report = {
        "total": len(results),
        "ok": ok_count,
        "failed": len(results) - ok_count,
        "results": results,
    }
    out_path.write_text(json.dumps(report, indent=2))

    print("=" * 60)
    print(f"Legendary Hands Data Verifier")
    print(f"  File: {data_path}")
    print(f"  Total: {report['total']}  OK: {report['ok']}  Failed: {report['failed']}")

    # Print first few failures concisely
    shown = 0
    for r in results:
        if not r.get("ok"):
            print(f"  ✖ {r['hand_id']}")
            for e in r.get("errors", [])[:5]:
                print(f"     - {e}")
            shown += 1
            if shown >= 5:
                break
    print(f"💾 Report: {out_path}")


if __name__ == "__main__":
    main()


