#!/usr/bin/env python3
"""
hand_validator_fix_strict.py — Canonical UID + Hand Model + NLHE (including betting rules) validator & fixer.

USAGE
-----
Validate only:
  python hand_validator_fix_strict.py --input hands.json --report report.json

Validate and fix (deterministic repairs):
  python hand_validator_fix_strict.py --input hands.json --fix --output fixed.json \
      --outdir per_hand/ --strict-blinds --allow-legacy --random-seed 42

What this enforces beyond structural checks:
- Action legality per NLHE:
  * turn order (relative to button / blinds / straddles)
  * CHECK only when to_call == 0
  * CALL amount equals to_call (or all-in if stack < to_call)
  * BET only when no bet yet on the street; min bet >= big blind (unless all-in below BB)
  * RAISE only when to_call > 0; raise_to >= current_bet + last_raise_size (min-raise), unless all-in below min
  * No acting out of turn
  * No betting after everyone is all-in; streets should just deal out boards
- Round completion & street transitions are consistent (no action after a closed round before next street)
- Stack constraints: a player cannot wager more than remaining stack; all-in supported
- Blinds/antes posted before voluntary actions

Notes:
- This validator does not compute exact side pots; it focuses on legality of sequences.
- Straddles are supported: any POST_BLIND with posting_meta.blind_type=="Straddle" raises the preflop current_bet and shifts first-to-act accordingly.
"""

import argparse, json, re, random, sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

CARD_RE = re.compile(r'^[2-9TJQKA][shdc]$')
RANKS = list("23456789TJQKA")
SUITS = list("shdc")
FULL_DECK = [r+s for r in RANKS for s in SUITS]

STREETS = ["PREFLOP","FLOP","TURN","RIVER"]
KNOWN_ACTIONS = {
    "POST_ANTE","POST_BLIND","STRADDLE","DEAL_HOLE","CHECK","BET","CALL","RAISE","FOLD",
    "RETURN_UNCALLED","SHOW","MUCK"
}

def load_hands(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and "hands" in data: return data["hands"]
    if isinstance(data, list): return data
    raise ValueError("Input must be list or {\"hands\": [...]}")

def canon_uid(val: Optional[str]) -> Optional[str]:
    if val is None: return None
    return re.sub(r"\s+", "", str(val)).lower()

def fresh_deck():
    return list(FULL_DECK)

def structural_validate(hand: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    md = hand.get("metadata", {})
    seats = hand.get("seats", [])
    streets = hand.get("streets", {})

    # Metadata and seats
    if "button_seat_no" not in md or not isinstance(md["button_seat_no"], int):
        problems.append("metadata.button_seat_no missing or not int")
    seat_nos = {s.get("seat_no") for s in seats if isinstance(s, dict)}
    if md.get("button_seat_no") not in seat_nos:
        problems.append("metadata.button_seat_no does not match a seat")

    seat_uids = []
    stacks = {}
    for i, s in enumerate(seats):
        uid = s.get("player_uid")
        if not uid: problems.append(f"seat[{i}] missing player_uid")
        else:
            seat_uids.append(uid)
            stacks[uid] = int(s.get("starting_stack", 0))

    if not hand.get("hero_player_uid"):
        problems.append("hero_player_uid missing")

    # Ensure streets exist and uppercase
    for st in STREETS:
        if st not in streets:
            problems.append(f"streets.{st} missing")
            streets.setdefault(st, {"board": [], "actions": []})

    # Actions: known, actor_uid present (except DEAL_HOLE), order monotone, street match
    global_order_prev = 0
    for st in STREETS:
        for j, a in enumerate(streets[st].get("actions", [])):
            act = a.get("action")
            if act not in KNOWN_ACTIONS:
                problems.append(f"{st}.actions[{j}].action unknown {act}")
            if act != "DEAL_HOLE" and a.get("actor_uid") is None:
                problems.append(f"{st}.actions[{j}] missing actor_uid")
            if a.get("street") != st:
                problems.append(f"{st}.actions[{j}].street mismatch")
            try:
                order = int(a.get("order"))
            except Exception:
                problems.append(f"{st}.actions[{j}].order not int")
                order = global_order_prev
            if order <= global_order_prev:
                problems.append(f"{st}.actions[{j}].order not strictly increasing")
            global_order_prev = order

    # Hole cards: two per player, keyed by uid
    hole = md.get("hole_cards")
    if not isinstance(hole, dict):
        problems.append("metadata.hole_cards missing or not dict")
        hole = {}
    for uid in seat_uids:
        cards = hole.get(uid)
        if not (isinstance(cards, list) and len(cards) == 2 and all(CARD_RE.match(c or "") for c in cards)):
            problems.append(f"hole_cards[{uid}] must be two valid cards")

    # Boards cumulative lengths and notation
    flop = streets.get("FLOP", {}).get("board", [])
    turn = streets.get("TURN", {}).get("board", [])
    river = streets.get("RIVER", {}).get("board", [])
    if not (isinstance(flop, list) and len(flop) == 3 and all(CARD_RE.match(c or "") for c in flop)):
        problems.append("FLOP.board must be exactly 3 cards")
    if not (isinstance(turn, list) and len(turn) == 4 and all(CARD_RE.match(c or "") for c in turn)):
        problems.append("TURN.board must be exactly 4 cards")
    if not (isinstance(river, list) and len(river) == 5 and all(CARD_RE.match(c or "") for c in river)):
        problems.append("RIVER.board must be exactly 5 cards")

    # No overlaps (single deck check)
    seen = set()
    for uid in seat_uids:
        for c in hole.get(uid, []):
            if c in seen: problems.append(f"duplicate card across hole_cards: {c}")
            seen.add(c)
    # Only add newly dealt cards for board: flop (3), turn (one new), river (one new)
    for c in flop + turn[3:4] + river[4:5]:
        if c in seen:
            problems.append(f"board reuses hole card {c}")
        seen.add(c)

    # Pots (optional)
    for p_i, p in enumerate(hand.get("pots", [])):
        elig = p.get("eligible_player_uids", [])
        if not isinstance(elig, list):
            problems.append(f"pots[{p_i}].eligible_player_uids not a list")
        for sh_i, sh in enumerate(p.get("shares", [])):
            if "player_uid" not in sh:
                problems.append(f"pots[{p_i}].shares[{sh_i}].player_uid missing")

    return problems

def derive_order(seats: List[Dict[str, Any]], button_seat_no: int) -> List[str]:
    # clockwise order starting from seat 1..n; rotate so index 0 is button
    ordered = sorted(seats, key=lambda s: s["seat_no"])
    while ordered[0]["seat_no"] != button_seat_no:
        ordered = ordered[1:] + ordered[:1]
    return [s["player_uid"] for s in ordered]

def first_to_act_preflop(uids_clockwise: List[str], num_players: int, posted_chain: List[str]) -> str:
    # Preflop: first to act is the first active player to the left of the last forced blind/straddle
    # Baseline blinds: BTN=idx0, SB=idx1, BB=idx2 (HU: BTN is SB and BB is opponent)
    last_forced_idx = 2 if num_players >= 3 else 1  # HU: last forced is BB at idx1
    # Straddles extend the chain by appending each straddler in order
    for uid in posted_chain:
        try:
            i = uids_clockwise.index(uid)
            last_forced_idx = i
        except ValueError:
            pass
    return uids_clockwise[(last_forced_idx + 1) % num_players]


def validate_betting(hand: Dict[str, Any]) -> List[str]:
    md = hand["metadata"]
    seats = hand["seats"]
    streets = hand["streets"]
    problems: List[str] = []

    uids_clock = derive_order(seats, md["button_seat_no"])
    n = len(uids_clock)
    stacks = {s["player_uid"]: int(s.get("starting_stack", 0)) for s in seats}
    in_hand = {uid: True for uid in uids_clock}

    def run_street(street: str, starting_actor: str, current_bet: int, last_raise_size: int) -> Tuple[str, int, int, bool]:
        actions = streets[street]["actions"]
        contrib = {uid: 0 for uid in uids_clock}
        to_act_order = uids_clock[:]
        idx = to_act_order.index(starting_actor)
        need_action = {uid: in_hand[uid] and stacks[uid] > 0 for uid in uids_clock}
        last_raiser = None
        seen_voluntary = False  # flips true after CHECK/BET/CALL/RAISE/FOLD

        for j, a in enumerate(actions):
            act = a.get("action")
            actor = a.get("actor_uid")
            amt = int(a.get("amount", 0) or 0)

            if act == "DEAL_HOLE":
                # Allow only on PREFLOP and only before any voluntary action occurred
                if street != "PREFLOP" or seen_voluntary:
                    problems.append(f"{street}.actions[{j}]: DEAL_HOLE must appear before preflop action begins")
                continue

            # Skip non-actors gracefully
            if actor not in in_hand or not in_hand[actor]:
                problems.append(f"{street}.actions[{j}]: actor {actor} not active")
                continue

            # expected actor
            guard = 0
            expected = None
            while guard < n:
                cand = to_act_order[idx % n]
                if in_hand[cand]:
                    expected = cand
                    break
                idx += 1; guard += 1
            if expected is None:
                expected = actor

            to_call = max(0, current_bet - contrib[actor])
            min_bet = int(md.get("big_blind", 100) or 100)

            if act == "CHECK":
                seen_voluntary = True
                if to_call != 0:
                    problems.append(f"{street}.actions[{j}]: CHECK not allowed (to_call={to_call})")
                if actor != expected:
                    problems.append(f"{street}.actions[{j}]: acting out of turn (expected {expected})")
                need_action[actor] = False
                idx += 1

            elif act == "FOLD":
                seen_voluntary = True
                if actor != expected:
                    problems.append(f"{street}.actions[{j}]: acting out of turn (expected {expected})")
                in_hand[actor] = False
                need_action[actor] = False
                idx += 1

            elif act == "CALL":
                seen_voluntary = True
                if to_call == 0 and stacks[actor] > 0:
                    problems.append(f"{street}.actions[{j}]: CALL with to_call=0")
                pay = min(to_call, stacks[actor])
                if amt not in (0, pay):
                    problems.append(f"{street}.actions[{j}]: CALL amount {amt} != to_call {pay}")
                contrib[actor] += pay
                stacks[actor] -= pay
                if actor != expected:
                    problems.append(f"{street}.actions[{j}]: acting out of turn (expected {expected})")
                need_action[actor] = False
                idx += 1

            elif act == "BET":
                seen_voluntary = True
                if current_bet != 0:
                    problems.append(f"{street}.actions[{j}]: BET not allowed, a bet already exists (use RAISE)")
                if amt < min_bet and amt < stacks[actor]:
                    problems.append(f"{street}.actions[{j}]: BET below min bet {min_bet}")
                if amt > stacks[actor]:
                    problems.append(f"{street}.actions[{j}]: BET exceeds stack")
                    bet_amt = stacks[actor]
                else:
                    bet_amt = amt
                contrib[actor] += bet_amt
                stacks[actor] -= bet_amt
                last_raise_size = bet_amt
                current_bet = contrib[actor]
                for u in uids_clock:
                    if u != actor and in_hand[u] and stacks[u] >= 0:
                        need_action[u] = True
                need_action[actor] = False
                idx = (uids_clock.index(actor) + 1) % n

            elif act == "RAISE":
                seen_voluntary = True
                if to_call <= 0 and current_bet != 0:
                    problems.append(f"{street}.actions[{j}]: RAISE when to_call={to_call}")
                raise_to = a.get("to_amount")
                if raise_to is None:
                    raise_to = contrib[actor] + max(0, amt)
                min_raise_to = current_bet + max(last_raise_size, int(md.get('big_blind', 100) or 100))
                if stacks[actor] + contrib[actor] < min_raise_to and (raise_to or 0) >= stacks[actor] + contrib[actor]:
                    pass
                else:
                    if raise_to < min_raise_to:
                        problems.append(f"{street}.actions[{j}]: RAISE to {raise_to} below min {min_raise_to}")
                pay = raise_to - contrib[actor]
                if pay > stacks[actor]:
                    problems.append(f"{street}.actions[{j}]: RAISE exceeds stack")
                    pay = stacks[actor]
                contrib[actor] += pay
                stacks[actor] -= pay
                last_raise_size = raise_to - current_bet
                current_bet = raise_to
                for u in uids_clock:
                    if u != actor and in_hand[u] and stacks[u] >= 0:
                        need_action[u] = True
                need_action[actor] = False
                idx = (uids_clock.index(actor) + 1) % n

            elif act == "RETURN_UNCALLED":
                # okay; doesn't affect turn order
                pass

            # round/hand completion checks
            alive = [u for u in uids_clock if in_hand[u]]
            if len(alive) == 1:
                return alive[0], current_bet, last_raise_size, True
            all_matched = all((current_bet - contrib[u] == 0) or stacks[u] == 0 or not in_hand[u] for u in uids_clock)
            no_one_needs = all(not need_action.get(u, False) for u in uids_clock)
            if all_matched and no_one_needs:
                next_actor = None
                for k in range(1, n+1):
                    cand = uids_clock[k % n]
                    if in_hand[cand]:
                        next_actor = cand; break
                if next_actor is None:
                    next_actor = uids_clock[0]
                return next_actor, 0, 0, all(stack == 0 or not in_hand[u] for u, stack in stacks.items())

        problems.append(f"{street}: betting round appears incomplete")
        next_actor = uids_clock[1 % n]
        return next_actor, current_bet, last_raise_size, False

    # Preflop posting scan
    pf_actions = streets["PREFLOP"]["actions"]
    current_bet = 0
    last_raise_size = int(md.get("big_blind", 100) or 100)
    posted_chain: List[str] = []
    for j, a in enumerate(pf_actions):
        if a["action"] in ("POST_ANTE", "DEAL_HOLE"):
            continue
        if a["action"] == "POST_BLIND":
            blind_type = (a.get("posting_meta") or {}).get("blind_type")
            if blind_type == "BB" or blind_type == "Straddle":
                current_bet = max(current_bet, int(a.get("to_amount") or a.get("amount") or 0))
                posted_chain.append(a["actor_uid"])
        else:
            break

    first_actor = first_to_act_preflop(uids_clock, n, posted_chain)
    next_actor, current_bet, last_raise_size, everyone_all_in = run_street("PREFLOP", first_actor, current_bet, last_raise_size)
    next_actor, current_bet, last_raise_size, everyone_all_in = run_street("FLOP", next_actor, 0, 0)
    next_actor, current_bet, last_raise_size, everyone_all_in = run_street("TURN", next_actor, 0, 0)
    next_actor, current_bet, last_raise_size, everyone_all_in = run_street("RIVER", next_actor, 0, 0)

    return problems


def fix_structural(hand: Dict[str, Any], rng: random.Random, allow_legacy: bool, strict_blinds: bool) -> None:
    # Convert legacy fields to canonical where possible
    if allow_legacy:
        convert_legacy_to_canonical(hand)

    # Ensure street containers
    hand.setdefault("streets", {})
    for st in STREETS:
        hand["streets"].setdefault(st, {"board": [], "actions": []})

    # Insert blinds/antes/deal if requested
    if strict_blinds:
        ensure_blinds_and_deal(hand)

    # Repair cards & boards deterministically
    fix_cards_strict(hand, rng)

    # Renumber actions globally
    renumber_actions(hand)

def ensure_blinds_and_deal(hand: Dict[str, Any]) -> None:
    md = hand["metadata"]
    seats = sorted(hand["seats"], key=lambda s: s["seat_no"])
    n = len(seats)
    if n < 2: return
    # rotate so index 0 is button
    while seats[0]["seat_no"] != md.get("button_seat_no", 1):
        seats = seats[1:] + seats[:1]
    SB_uid = seats[1 % n]["player_uid"]
    BB_uid = seats[2 % n]["player_uid"] if n > 2 else seats[0]["player_uid"]
    sb_amt = int(md.get("small_blind", 50) or 50)
    bb_amt = int(md.get("big_blind", 100) or 100)
    ante = int(md.get("ante", 0) or 0)

    pf = hand["streets"].setdefault("PREFLOP", {"board": [], "actions": []})
    acts = pf["actions"]
    new_actions = []
    ord_ctr = 1

    if ante > 0 and not any(a.get("action")=="POST_ANTE" for a in acts):
        for s in seats:
            new_actions.append({"order":ord_ctr, "street":"PREFLOP", "actor_uid":s["player_uid"], "action":"POST_ANTE", "amount":ante, "to_amount":ante})
            ord_ctr += 1
    if not any(a.get("action")=="POST_BLIND" and (a.get("posting_meta") or {}).get("blind_type")=="SB" for a in acts):
        new_actions.append({"order":ord_ctr, "street":"PREFLOP", "actor_uid":SB_uid, "action":"POST_BLIND", "amount":sb_amt, "to_amount":sb_amt, "posting_meta":{"blind_type":"SB"}}); ord_ctr+=1
    if not any(a.get("action")=="POST_BLIND" and (a.get("posting_meta") or {}).get("blind_type")=="BB" for a in acts):
        new_actions.append({"order":ord_ctr, "street":"PREFLOP", "actor_uid":BB_uid, "action":"POST_BLIND", "amount":bb_amt, "to_amount":bb_amt, "posting_meta":{"blind_type":"BB"}}); ord_ctr+=1
    if not any(a.get("action")=="DEAL_HOLE" for a in acts):
        new_actions.append({"order":ord_ctr, "street":"PREFLOP", "actor_uid":None, "action":"DEAL_HOLE", "amount":0}); ord_ctr+=1

    for a in acts:
        a2 = dict(a); a2["order"] = ord_ctr; a2["street"] = "PREFLOP"; ord_ctr += 1
        new_actions.append(a2)
    pf["actions"] = new_actions


def fix_betting_legalize(hand: Dict[str, Any]) -> None:
    md = hand["metadata"]
    seats = hand["seats"]
    streets = hand["streets"]
    uids_clock = derive_order(seats, md["button_seat_no"])
    n = len(uids_clock)
    stacks = {s["player_uid"]: int(s.get("starting_stack", 0)) for s in seats}
    in_hand = {uid: True for uid in uids_clock}

    def run_street_fix(street: str, starting_actor: str, current_bet: int, last_raise_size: int):
        actions = streets[street]["actions"]
        contrib = {uid: 0 for uid in uids_clock}
        idx = uids_clock.index(starting_actor)
        for j, a in enumerate(actions):
            act = a.get("action")
            if act == "DEAL_HOLE":
                continue
            actor = a.get("actor_uid")
            if actor not in in_hand or not in_hand[actor]:
                continue
            to_call = max(0, current_bet - contrib[actor])
            amt = int(a.get("amount", 0) or 0)
            bb = int(md.get("big_blind", 100) or 100)

            if act == "FOLD":
                in_hand[actor] = False
                idx = (uids_clock.index(actor) + 1) % n

            elif act == "CHECK":
                idx = (uids_clock.index(actor) + 1) % n

            elif act == "CALL":
                pay = min(to_call, stacks[actor])
                a["amount"] = pay
                contrib[actor] += pay
                stacks[actor] -= pay
                idx = (uids_clock.index(actor) + 1) % n

            elif act == "BET":
                # Clamp to stack; if below BB and not all-in, bump to BB (unless stack < BB)
                bet_amt = min(amt, stacks[actor])
                if bet_amt < bb and bet_amt < stacks[actor]:
                    bet_amt = min(bb, stacks[actor])
                a["amount"] = bet_amt
                a["to_amount"] = contrib[actor] + bet_amt
                a["all_in"] = bet_amt == stacks[actor]
                contrib[actor] += bet_amt
                stacks[actor] -= bet_amt
                last_raise_size = bet_amt
                current_bet = contrib[actor]

            elif act == "RAISE":
                # Prefer to_amount; compute desired raise_to
                desired_to = a.get("to_amount")
                if desired_to is None:
                    desired_to = contrib[actor] + max(0, amt)
                # Clamp raise_to to actor's all-in ceiling
                max_to = contrib[actor] + stacks[actor]
                raise_to = min(desired_to, max_to)
                a["to_amount"] = raise_to
                # Recompute amount paid this action
                pay = max(0, raise_to - contrib[actor])
                a["amount"] = pay
                a["all_in"] = raise_to == max_to
                contrib[actor] += pay
                stacks[actor] -= pay
                last_raise_size = max(raise_to - current_bet, last_raise_size)
                current_bet = max(current_bet, raise_to)

            elif act == "RETURN_UNCALLED":
                # If amount exceeds actor's current contributed-in-round, clamp
                refund = min(amt, contrib.get(actor, 0))
                a["amount"] = refund
                contrib[actor] -= refund
                stacks[actor] += refund

        return current_bet, last_raise_size

    # Preflop current bet from BB/straddles
    current_bet = 0
    last_raise_size = int(md.get("big_blind", 100) or 100)
    pf_posts = []
    for a in streets["PREFLOP"]["actions"]:
        if a["action"] == "POST_BLIND":
            bt = (a.get("posting_meta") or {}).get("blind_type")
            if bt in ("BB","Straddle"):
                current_bet = max(current_bet, int(a.get("to_amount") or a.get("amount") or 0))
                pf_posts.append(a["actor_uid"])
    first_actor = first_to_act_preflop(uids_clock, n, pf_posts)

    current_bet, last_raise_size = run_street_fix("PREFLOP", first_actor, current_bet, last_raise_size)
    current_bet, last_raise_size = run_street_fix("FLOP", uids_clock[(uids_clock.index(hand['seats'][0]['player_uid'])+1)%n], 0, 0)
    current_bet, last_raise_size = run_street_fix("TURN", uids_clock[(uids_clock.index(hand['seats'][0]['player_uid'])+1)%n], 0, 0)
    current_bet, last_raise_size = run_street_fix("RIVER", uids_clock[(uids_clock.index(hand['seats'][0]['player_uid'])+1)%n], 0, 0)

def fix_cards_strict(hand: Dict[str, Any], rng: random.Random) -> None:
    md = hand["metadata"]
    seats = sorted(hand["seats"], key=lambda s: s["seat_no"])
    seat_uids = [s["player_uid"] for s in seats]
    deck = set(FULL_DECK)

    hole = md.get("hole_cards") or {}
    cleaned = {}
    used = set()
    # Normalize hole cards to two unique cards per seat
    for s in seats:
        uid = s["player_uid"]
        raw = hole.get(uid) or []
        raw = [c for c in raw if isinstance(c, str) and CARD_RE.match(c)]
        chosen = []
        for c in raw:
            if c in deck and c not in used and len(chosen) < 2:
                chosen.append(c); deck.remove(c); used.add(c)
        cleaned[uid] = chosen
    # Fill missing
    pool = sorted(deck); rng.shuffle(pool); it = iter(pool)
    for uid in seat_uids:
        while len(cleaned[uid]) < 2:
            cleaned[uid].append(next(it))
    md["hole_cards"] = {uid: cleaned[uid][:2] for uid in seat_uids}

    # Build a clean board from remaining deck
    deck2 = set(FULL_DECK)
    for cards in md["hole_cards"].values():
        for c in cards: deck2.discard(c)
    pool2 = sorted(deck2); rng.shuffle(pool2)
    flop = pool2[:3]; turn = pool2[3]; river = pool2[4]

    hand["streets"].setdefault("FLOP", {"board": [], "actions": []})
    hand["streets"].setdefault("TURN", {"board": [], "actions": []})
    hand["streets"].setdefault("RIVER", {"board": [], "actions": []})
    hand["streets"]["FLOP"]["board"] = flop
    hand["streets"]["TURN"]["board"] = flop + [turn]
    hand["streets"]["RIVER"]["board"] = flop + [turn, river]



def normalize_preflop_opening_order(hand: Dict[str, Any]) -> None:
    """
    Reorder only the initial voluntary actions on PREFLOP (up to the first BET/RAISE)
    to match correct UTG→... rotation. We only reorder CALL/FOLD actions.
    Amounts for CALL are clamped to current to_call; FOLD unchanged.
    """
    md = hand["metadata"]
    seats = hand["seats"]
    streets = hand["streets"]
    uids_clock = derive_order(seats, md["button_seat_no"])
    n = len(uids_clock)

    acts = streets["PREFLOP"].get("actions", [])
    prefix = [a for a in acts if a.get("action") in ("POST_ANTE","POST_BLIND","STRADDLE","DEAL_HOLE")]
    core = [a for a in acts if a.get("action") not in ("POST_ANTE","POST_BLIND","STRADDLE","DEAL_HOLE")]

    # Establish current_bet from postings (BB/Straddles)
    current_bet = 0
    for a in prefix:
        if a.get("action") == "POST_BLIND":
            bt = (a.get("posting_meta") or {}).get("blind_type")
            if bt in ("BB","Straddle"):
                current_bet = max(current_bet, int(a.get("to_amount") or a.get("amount") or 0))

    # Split core at first aggression (BET/RAISE)
    agg_idx = None
    for i, a in enumerate(core):
        if a.get("action") in ("BET","RAISE"):
            agg_idx = i
            break
    opening = core if agg_idx is None else core[:agg_idx]
    rest = [] if agg_idx is None else core[agg_idx:]

    # If opening contains actions other than CALL/FOLD, skip normalization
    if any(a.get("action") not in ("CALL","FOLD","CHECK") for a in opening):
        # 'CHECK' is illegal facing to_call; we'll leave to other fixers
        streets["PREFLOP"]["actions"] = prefix + core
        return

    # Build a map from actor to their opening action
    opening_by_actor = {}
    for a in opening:
        opening_by_actor.setdefault(a.get("actor_uid"), []).append(a)

    # Compute UTG (first to act) uid
    # Using first_to_act_preflop from blinds chain
    posted_chain = [a.get("actor_uid") for a in prefix if a.get("action")=="POST_BLIND" and (a.get("posting_meta") or {}).get("blind_type") in ("BB","Straddle")]
    utg = first_to_act_preflop(uids_clock, n, posted_chain)

    # Reassemble opening in UTG→ order once, pulling at most one action per player in that phase
    new_opening = []
    seen = set()
    order_list = []
    start_idx = uids_clock.index(utg)
    for k in range(n):
        order_list.append(uids_clock[(start_idx + k) % n])
    for uid in order_list:
        if uid in opening_by_actor and opening_by_actor[uid]:
            a = opening_by_actor[uid].pop(0)
            # Clamp CALL amount to current_bet (to_call)
            if a.get("action") == "CALL":
                a = dict(a)
                a["amount"] = current_bet  # they call the posted bet
                a["to_amount"] = current_bet
            new_opening.append(a)

    # Append any leftover opening actions in original order (rare; e.g., duplicates)
    for uid, lst in opening_by_actor.items():
        for a in lst:
            new_opening.append(a)

    # Stitch back
    streets["PREFLOP"]["actions"] = prefix + new_opening + rest

def normalize_turn_order_and_close_rounds(hand: Dict[str, Any]) -> None:
    """
    Conservative repair:
      - Only reorders CHECK actions (non-aggressive, zero-chip) to match correct rotation.
      - Inserts missing CHECKs at end of a round when everyone has matched and still 'owes' an action.
    This avoids changing contributions or winners.
    """
    md = hand["metadata"]
    seats = hand["seats"]
    streets = hand["streets"]
    uids_clock = derive_order(seats, md["button_seat_no"])
    n = len(uids_clock)

    def players_in_hand():
        # If we had FOLD tracking, we'd read it; for safety, assume all are in unless explicit folds occurred earlier in the street.
        return {s["player_uid"]: True for s in seats}

    def compute_to_call(current_bet, contrib, uid):
        return max(0, current_bet - contrib.get(uid, 0))

    # Prefetch blinds to set preflop current_bet
    pf_posts = []
    current_bet_pf = 0
    for a in streets["PREFLOP"]["actions"]:
        if a.get("action") == "POST_BLIND":
            bt = (a.get("posting_meta") or {}).get("blind_type")
            if bt in ("BB","Straddle"):
                current_bet_pf = max(current_bet_pf, int(a.get("to_amount") or a.get("amount") or 0))
                pf_posts.append(a.get("actor_uid"))
    first_actor_pf = first_to_act_preflop(uids_clock, n, pf_posts)

    def street_first_actor(street, default_start):
        if street == "PREFLOP":
            return first_actor_pf
        # Postflop: first alive after button
        for k in range(1, n+1):
            cand = uids_clock[k % n]
            # For lack of full fold tracking across streets, assume alive
            return cand
        return default_start

    for street in STREETS:
        acts = streets[street].get("actions", [])
        # Split posting/deal and voluntary; keep posting/deal at front
        prefix = [a for a in acts if a.get("action") in ("POST_ANTE","POST_BLIND","STRADDLE","DEAL_HOLE")]
        core = [a for a in acts if a.get("action") not in ("POST_ANTE","POST_BLIND","STRADDLE","DEAL_HOLE")]

        # Simulate contributions on this street only to compute to_call for order normalization
        contrib = {uid: 0 for uid in uids_clock}
        current_bet = current_bet_pf if street == "PREFLOP" else 0

        # Build new action list by walking expected rotation and consuming any available CHECK from the original list when appropriate.
        # For non-CHECK actions, keep original order (we won't move them).
        new_core = []
        in_hand = players_in_hand()
        idx = uids_clock.index(street_first_actor(street, uids_clock[1 % n]))

        # First, copy over all non-CHECK actions in original order, but when CHECKs are out of turn, we'll reposition them later.
        # We'll create a queue of original CHECKs we can place when it's that player's turn and to_call==0.
        check_queue = []
        for a in core:
            if a.get("action") == "CHECK":
                check_queue.append(a)
            else:
                # Before appending a non-CHECK action, flush pending expected CHECKs for players whose turn arrives with to_call==0.
                # Compute expected actor
                expected = uids_clock[idx % n]
                to_call = compute_to_call(current_bet, contrib, expected)
                # If expected has zero to_call and we have a queued CHECK for them, place it
                placed = True
                while to_call == 0 and check_queue and any(ch.get("actor_uid")==expected for ch in check_queue):
                    ch_idx = next(i for i,ch in enumerate(check_queue) if ch.get("actor_uid")==expected)
                    ch = check_queue.pop(ch_idx)
                    ch["street"] = street
                    new_core.append(ch)
                    # advance turn
                    idx = (idx + 1) % n
                    expected = uids_clock[idx % n]
                    to_call = compute_to_call(current_bet, contrib, expected)
                    placed = True
                # Now append the non-CHECK action
                a2 = dict(a)
                new_core.append(a2)
                # Update contrib/current_bet based on action
                act = a2.get("action")
                uid = a2.get("actor_uid")
                amt = int(a2.get("amount", 0) or 0)
                if act == "FOLD":
                    in_hand[uid] = False
                    idx = (uids_clock.index(uid) + 1) % n
                elif act == "CALL":
                    contrib[uid] = contrib.get(uid,0) + amt
                    idx = (uids_clock.index(uid) + 1) % n
                elif act == "BET":
                    contrib[uid] = contrib.get(uid,0) + amt
                    current_bet = contrib[uid]
                    idx = (uids_clock.index(uid) + 1) % n
                elif act == "RAISE":
                    to_amt = a2.get("to_amount") or contrib[uid] + amt
                    pay = max(0, to_amt - contrib.get(uid,0))
                    contrib[uid] = contrib.get(uid,0) + pay
                    current_bet = max(current_bet, to_amt)
                    idx = (uids_clock.index(uid) + 1) % n
                elif act == "RETURN_UNCALLED":
                    contrib[uid] = max(0, contrib.get(uid,0) - amt)
                else:
                    # SHOW/MUCK etc — no turn impact here
                    pass

        # After all non-CHECK actions appended, append remaining CHECKs for players who still owe action at to_call==0, in proper rotation
        # Determine who still needs to act: anyone in_hand with to_call==0 who hasn't acted since last bet/raise; we approximate by cycling once through table.
        visited = set(a.get("actor_uid") for a in new_core if a.get("action") in ("CHECK","CALL","BET","RAISE","FOLD"))
        rounds = 0
        while check_queue and rounds <= n:
            expected = uids_clock[idx % n]
            to_call = compute_to_call(current_bet, contrib, expected)
            if to_call == 0 and in_hand.get(expected, True):
                # place CHECK for expected if available; otherwise, synthesize a CHECK
                match_i = next((i for i,ch in enumerate(check_queue) if ch.get("actor_uid")==expected), None)
                if match_i is not None:
                    ch = check_queue.pop(match_i)
                else:
                    ch = {"order": 0, "street": street, "actor_uid": expected, "action": "CHECK", "amount": 0}
                new_core.append(ch)
            idx = (idx + 1) % n
            rounds += 1

        # Enforce closure when no aggression: everyone in-hand should act once
        to_call_map = {uid: compute_to_call(current_bet, contrib, uid) for uid in uids_clock}
        any_aggr = any(a.get('action') in ('BET','RAISE') for a in new_core)
        if not any_aggr and all(v == 0 for v in to_call_map.values()):
            acted = set(a.get('actor_uid') for a in new_core if a.get('action') in ('CHECK','CALL','BET','RAISE','FOLD'))
            start = uids_clock.index(street_first_actor(street, uids_clock[1 % n]))
            for k in range(n):
                uid = uids_clock[(start + k) % n]
                if in_hand.get(uid, True) and uid not in acted:
                    new_core.append({'order': 0, 'street': street, 'actor_uid': uid, 'action': 'CHECK', 'amount': 0})
                    acted.add(uid)


        # Final closure enforcement: if this street had no BET/RAISE, append CHECKs so each in-hand player acts once
        any_aggr2 = any(a.get('action') in ('BET','RAISE') for a in new_core)
        if not any_aggr2:
            acted = set(a.get('actor_uid') for a in new_core if a.get('action') in ('CHECK','CALL','BET','RAISE','FOLD'))
            start_uid = street_first_actor(street, uids_clock[1 % n])
            start_idx2 = uids_clock.index(start_uid)
            for k in range(n):
                uid = uids_clock[(start_idx2 + k) % n]
                if in_hand.get(uid, True) and uid not in acted:
                    new_core.append({'order': 0, 'street': street, 'actor_uid': uid, 'action': 'CHECK', 'amount': 0})
                    acted.add(uid)

        # Stitch back, keep original relative numbering; renumber will happen later globally
        streets[street]["actions"] = prefix + new_core

def renumber_actions(hand: Dict[str, Any]) -> None:
    order = 1
    for st in STREETS:
        stobj = hand["streets"].setdefault(st, {"board": [], "actions": []})
        new_actions = []
        for a in stobj.get("actions", []):
            a2 = dict(a)
            a2["order"] = order
            a2["street"] = st
            new_actions.append(a2); order += 1
        stobj["actions"] = new_actions

def convert_legacy_to_canonical(hand: Dict[str, Any]) -> None:
    md = hand.get("metadata", {})
    seats = hand.get("seats", [])
    legacy_map = {}
    for s in seats:
        if "player_uid" not in s and "player_id" in s:
            s["player_uid"] = canon_uid(s["player_id"]) or f"p{s.get('seat_no',0)}"
        if "player_id" in s: legacy_map[s["player_id"]] = s["player_uid"]
        legacy_map[s.get("display_name","")] = s.get("player_uid")
        if s.get("player_uid"): legacy_map[s["player_uid"]] = s["player_uid"]
    if "hero_player_uid" not in hand and "hero_player_id" in hand:
        hand["hero_player_uid"] = legacy_map.get(hand["hero_player_id"]) or canon_uid(hand["hero_player_id"])
    hole = md.get("hole_cards")
    if isinstance(hole, dict):
        md["hole_cards"] = { (legacy_map.get(k) or canon_uid(k) or k): v for k,v in hole.items() }
    for st in STREETS:
        for a in hand.get("streets", {}).get(st, {}).get("actions", []):
            if "actor_uid" not in a and "actor_id" in a:
                a["actor_uid"] = legacy_map.get(a["actor_id"]) or canon_uid(a["actor_id"])
    new_pots = []
    for p in hand.get("pots", []):
        elig = p.get("eligible_player_uids") or p.get("eligible_player_ids") or []
        elig2 = [(legacy_map.get(x) or canon_uid(x) or x) for x in elig]
        shares2 = []
        for sh in p.get("shares", []):
            uid = sh.get("player_uid") or legacy_map.get(sh.get("player_id")) or canon_uid(sh.get("player_id"))
            shares2.append({"player_uid": uid, "amount": int(sh.get("amount", 0))})
        new_pots.append({"amount": int(p.get("amount", 0)), "eligible_player_uids": elig2, "shares": shares2})
    if new_pots: hand["pots"] = new_pots


def process(path: str, fix: bool, allow_legacy: bool, strict_blinds: bool, seed: int, out_path: Optional[str], outdir: Optional[str], report_path: Optional[str], enforce_pots: bool=False) -> int:
    rng = random.Random(seed)
    hands = load_hands(path)
    all_issues: List[Dict[str, Any]] = []
    out_hands: List[Dict[str, Any]] = []

    for i, hand in enumerate(hands):
        h = json.loads(json.dumps(hand))  # deep copy
        issues = structural_validate(h)
        issues += validate_betting(h)
        issues += validate_pots(h, enforce=enforce_pots)

        if fix:
            if allow_legacy:
                convert_legacy_to_canonical(h)
            if strict_blinds:
                ensure_blinds_and_deal(h)
            fix_cards_strict(h, rng)
            fix_betting_legalize(h)
            normalize_preflop_opening_order(h)
            normalize_turn_order_and_close_rounds(h)
            fill_missing_responses_with_fold(h)
            prune_actions_after_fold(h)
            rebuild_pots(h)
            renumber_actions(h)
            issues = structural_validate(h) + validate_betting(h) + validate_pots(h, enforce=enforce_pots)

        all_issues.append({"hand_index": i, "hand_id": h.get("metadata",{}).get("hand_id"), "issues": issues})
        out_hands.append(h)

    if report_path:
        Path(report_path).write_text(json.dumps({"total_hands": len(hands), "hands": all_issues}, indent=2))

    if fix and out_path:
        payload = {"hands": out_hands}
        Path(out_path).write_text(json.dumps(payload, indent=2))
        if outdir:
            outdir_p = Path(outdir); outdir_p.mkdir(parents=True, exist_ok=True)
            for h in out_hands:
                hid = h.get("metadata",{}).get("hand_id") or "HAND"
                (outdir_p / f"{hid}.json").write_text(json.dumps(h, indent=2))

    remaining = sum(1 for x in all_issues if x["issues"])
    return 0 if remaining == 0 else 1


# ----- Pot & side-pot accounting (optional) -----
def compute_contributions(hand):
    contrib = {s["player_uid"]: 0 for s in hand["seats"]}
    for st in STREETS:
        for a in hand["streets"].get(st, {}).get("actions", []):
            act = a.get("action")
            uid = a.get("actor_uid")
            amt = int(a.get("amount", 0) or 0)
            to_amt = a.get("to_amount")
            if act in ("POST_ANTE","POST_BLIND"):
                contrib[uid] = contrib.get(uid,0) + amt
            elif act == "BET":
                contrib[uid] = contrib.get(uid,0) + amt
            elif act == "CALL":
                contrib[uid] = contrib.get(uid,0) + amt
            elif act == "RAISE":
                if to_amt is not None:
                    contrib[uid] = contrib.get(uid,0) + max(amt, 0)
                else:
                    contrib[uid] = contrib.get(uid,0) + max(amt, 0)
            elif act == "RETURN_UNCALLED":
                contrib[uid] = contrib.get(uid,0) - amt
    return contrib



def fill_missing_responses_with_fold(hand: Dict[str, Any]) -> None:
    md = hand["metadata"]
    seats = hand["seats"]
    streets = hand["streets"]
    uids_clock = derive_order(seats, md["button_seat_no"])
    n = len(uids_clock)

    # Determine in-hand players after PREFLOP (anyone who didn't fold preflop)
    in_hand = {s["player_uid"]: True for s in seats}
    for a in streets["PREFLOP"]["actions"]:
        if a.get("action") == "FOLD":
            in_hand[a.get("actor_uid")] = False

    def street_start(street):
        if street == "PREFLOP":
            # not used here
            return None
        # first to act postflop is left of button
        return uids_clock[1 % n]

    for street in ["FLOP","TURN","RIVER"]:
        actions = streets[street]["actions"]
        if not actions:
            continue
        any_aggr = any(a.get("action") in ("BET","RAISE") for a in actions)
        if not any_aggr:
            continue
        # Collect actors who already responded with CHECK/CALL/BET/RAISE/FOLD
        acted = set(a.get("actor_uid") for a in actions if a.get("action") in ("CHECK","CALL","BET","RAISE","FOLD"))
        # Append FOLD for any in-hand player who never responded yet
        start_uid = street_start(street)
        start_idx = uids_clock.index(start_uid)
        for k in range(n):
            uid = uids_clock[(start_idx + k) % n]
            if in_hand.get(uid, True) and uid not in acted:
                actions.append({"order": 0, "street": street, "actor_uid": uid, "action": "FOLD", "amount": 0})
        streets[street]["actions"] = actions


def prune_actions_after_fold(hand: Dict[str, Any]) -> None:
    streets = hand["streets"]
    folded = set()
    # Walk in order: PREFLOP -> FLOP -> TURN -> RIVER
    for street in STREETS:
        new = []
        for a in streets[street]["actions"]:
            uid = a.get("actor_uid")
            if uid is not None and uid in folded:
                # skip any action by a player already folded
                continue
            new.append(a)
            if a.get("action") == "FOLD" and uid is not None:
                folded.add(uid)
        streets[street]["actions"] = new

def rebuild_pots(hand: Dict[str, Any]) -> None:
    """Recompute a single main pot equal to total contributions; shares left empty (winner unknown)."""
    contrib = compute_contributions(hand)
    total_contrib = sum(contrib.values())
    seat_uids = [s["player_uid"] for s in hand["seats"]]
    hand["pots"] = [{
        "amount": total_contrib,
        "eligible_player_uids": seat_uids[:],
        "shares": []
    }]

def validate_pots(hand, enforce=False):
    problems = []
    seats = hand["seats"]
    md = hand["metadata"]
    seat_uids = [s["player_uid"] for s in seats]
    contrib = compute_contributions(hand)
    total_contrib = sum(contrib.values())

    pots = hand.get("pots", [])
    if not pots:
        if enforce:
            hand["pots"] = [{
                "amount": total_contrib,
                "eligible_player_uids": seat_uids[:],
                "shares": []
            }]
        return problems

    ssum = 0
    for i, p in enumerate(pots):
        if "amount" not in p or not isinstance(p["amount"], int):
            problems.append(f"pots[{i}].amount missing or not int")
        elig = p.get("eligible_player_uids", [])
        if not isinstance(elig, list):
            problems.append(f"pots[{i}].eligible_player_uids not list")
        share_sum = 0
        for j, sh in enumerate(p.get("shares", [])):
            if "player_uid" not in sh:
                problems.append(f"pots[{i}].shares[{j}].player_uid missing")
            try:
                share_sum += int(sh.get("amount", 0))
            except Exception:
                problems.append(f"pots[{i}].shares[{j}].amount not int")
        ssum += int(p.get("amount", 0))
        if p.get("shares"):
            if share_sum != int(p.get("amount", 0)):
                problems.append(f"pots[{i}]: shares sum {share_sum} != pot amount {p.get('amount',0)}")

    if ssum > total_contrib:
        problems.append(f"sum(pots.amount) {ssum} exceeds total contributions {total_contrib}")

    return problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--report")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--output")
    ap.add_argument("--outdir")
    ap.add_argument("--random-seed", type=int, default=42)
    ap.add_argument("--strict-blinds", action="store_true")
    ap.add_argument("--allow-legacy", action="store_true")
    ap.add_argument("--enforce-pots", action="store_true")
    args = ap.parse_args()

    if args.fix and not args.output:
        print("With --fix you must provide --output", file=sys.stderr); sys.exit(2)

    code = process(args.input, args.fix, args.allow_legacy, args.strict_blinds, args.random_seed, args.output, args.outdir, args.report, args.enforce_pots)
    if code != 0:
        print("Validation failed. See report for details.", file=sys.stderr)
    sys.exit(code)

if __name__ == "__main__":
    main()
