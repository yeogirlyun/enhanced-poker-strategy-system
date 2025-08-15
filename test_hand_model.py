#!/usr/bin/env python3
"""
Comprehensive test harness for hand_model.py

This test suite fuzz-tests the hand schema end-to-end:
- Randomly generates valid NLHE hands for 2–9 players
- Tests posting, betting rounds, boards, side pots, showdowns/mucks
- Tests all-ins, straddles, antes, rake, run-it-twice scenarios
- Saves to JSON, loads from JSON, asserts round-trip identity
- Validates structural invariants and mathematical consistency

Run with: python -m unittest -v test_hand_model.py
"""

import unittest
import random
import tempfile
import os
import sys
from typing import List, Dict, Optional, Tuple

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.hand_model import (
    Hand, HandMetadata, Seat, Street, StreetState, Action, ActionType, PostingMeta,
    Pot, PotShare, ShowdownEntry, Variant
)

RANKS = "23456789TJQKA"
SUITS = "cdhs"

# ----------------------------
# Helpers: cards & dealing
# ----------------------------
def fresh_deck() -> List[str]:
    """Create a fresh 52-card deck."""
    return [r+s for r in RANKS for s in SUITS]

def draw(deck: List[str], n: int) -> List[str]:
    """Draw n cards from deck (modifies deck)."""
    out = deck[:n]
    del deck[:n]
    return out

# ----------------------------
# Betting-round simulator
# ----------------------------
class TableState:
    """Simulates a poker table for fuzz testing."""
    
    def __init__(self, player_ids: List[str], sb: int, bb: int, ante: int, rng: random.Random):
        self.rng = rng
        self.sb = sb
        self.bb = bb
        self.ante = ante
        self.players = player_ids[:]                  # seat order
        self.active = set(player_ids)                 # in-hand and not folded
        self.all_in = set()                           # players who can't act
        self.street_contrib: Dict[str,int] = {p:0 for p in player_ids}
        self.total_contrib: Dict[str,int]  = {p:0 for p in player_ids}
        self.order_counter = 1
        self.last_aggressor: Optional[str] = None

    def post_antes(self, hand: Hand):
        """Post antes for all players."""
        if self.ante <= 0: 
            return
        for pid in self.players:
            amt = self.ante
            self._post(hand, pid, ActionType.POST_ANTE, amt)

    def post_blinds_and_straddle(self, hand: Hand, sb_seat_idx: int, with_straddle: bool):
        """Post blinds and optional straddle."""
        n = len(self.players)
        sb_pid = self.players[sb_seat_idx % n]
        bb_pid = self.players[(sb_seat_idx+1) % n]
        
        self._post(hand, sb_pid, ActionType.POST_BLIND, self.sb, PostingMeta("SB"))
        self._post(hand, bb_pid, ActionType.POST_BLIND, self.bb, PostingMeta("BB"))
        
        if with_straddle and n >= 3:
            st_pid = self.players[(sb_seat_idx+2) % n]
            # Double big blind straddle
            self._post(hand, st_pid, ActionType.STRADDLE, self.bb*2, PostingMeta("Straddle"))

    def _post(self, hand: Hand, pid: str, kind: ActionType, amt: int, meta: Optional[PostingMeta]=None):
        """Record a posting action."""
        self.street_contrib[pid] += amt
        self.total_contrib[pid]  += amt
        hand.streets[Street.PREFLOP].actions.append(Action(
            order=self.order_counter, 
            street=Street.PREFLOP, 
            actor_id=pid, 
            action=kind, 
            amount=amt,
            to_amount=self.street_contrib[pid], 
            posting_meta=meta
        ))
        self.order_counter += 1

    def _bet_action(self, hand: Hand, street: Street, pid: str, kind: ActionType, 
                   inc: int, to_amount: Optional[int], all_in: bool, note: Optional[str]=None):
        """Record a betting action."""
        if inc > 0:
            self.street_contrib[pid] += inc
            self.total_contrib[pid]  += inc
        hand.streets[street].actions.append(Action(
            order=self.order_counter, 
            street=street, 
            actor_id=pid, 
            action=kind,
            amount=inc, 
            to_amount=to_amount, 
            all_in=all_in, 
            note=note
        ))
        self.order_counter += 1

    def street_reset(self):
        """Reset for new betting street."""
        for p in self.players:
            self.street_contrib[p] = 0
        self.last_aggressor = None

    def run_betting_round(self, hand: Hand, street: Street, opener_idx: int, 
                         min_raise: int) -> Tuple[bool, Optional[str]]:
        """
        Run a complete betting round.
        Returns (hand_ended, winner_if_fold).
        """
        if street == Street.PREFLOP:
            # Blinds already posted; to_call is current max contrib on this street
            to_call = max(self.street_contrib.values()) if self.street_contrib else 0
        else:
            to_call = 0

        pending = True
        turn_idx = opener_idx
        n = len(self.players)
        acted_since_raise = set()
        steps_left = 200  # Safety cap

        while pending and steps_left > 0:
            steps_left -= 1
            pid = self.players[turn_idx]
            turn_idx = (turn_idx + 1) % n
            
            if pid not in self.active or pid in self.all_in:
                if self._everybody_matched(to_call, acted_since_raise):
                    pending = False
                continue

            need = to_call - self.street_contrib[pid]

            # Choose an action
            choices = []
            if need == 0:
                choices.extend(["check", "bet"])
            else:
                choices.extend(["fold", "call", "raise"])

            # Sometimes go aggressive
            if self.rng.random() < 0.05:
                choices = ["raise"] if "raise" in choices else choices

            move = self.rng.choice(choices)

            if move == "check":
                self._bet_action(hand, street, pid, ActionType.CHECK, 0, self.street_contrib[pid], False)
                acted_since_raise.add(pid)

            elif move == "fold":
                self._bet_action(hand, street, pid, ActionType.FOLD, 0, self.street_contrib[pid], False)
                self.active.discard(pid)
                acted_since_raise.add(pid)
                
                if len(self.active) == 1:
                    # Return uncalled amount if needed
                    if self.last_aggressor is not None and to_call > 0:
                        self._bet_action(hand, street, self.last_aggressor, ActionType.RETURN_UNCALLED, 
                                       0, None, False, note="auto-return")
                    winner = next(iter(self.active))
                    return True, winner

            elif move == "call":
                pay = max(0, need)
                self._bet_action(hand, street, pid, ActionType.CALL, pay, 
                               self.street_contrib[pid]+pay, False)
                acted_since_raise.add(pid)
                if self._everybody_matched(to_call, acted_since_raise):
                    pending = False

            elif move == "bet":
                base = max(min_raise, int(self._pot_for_round())//3)
                inc = max(min_raise, self.rng.randint(min_raise, max(min_raise, base)))
                if self.rng.random() < 0.1:  # Sometimes big bet
                    inc = self.rng.randint(min_raise, min_raise*10)
                    
                self._bet_action(hand, street, pid, ActionType.BET, inc, 
                               self.street_contrib[pid]+inc, False)
                to_call = self.street_contrib[pid]
                acted_since_raise = {pid}
                self.last_aggressor = pid

            elif move == "raise":
                min_r = max(min_raise, need + min_raise)
                inc = self.rng.randint(min_r, max(min_r, min_r*3))
                is_ai = (self.rng.random() < 0.15)  # Sometimes all-in
                
                self._bet_action(hand, street, pid, ActionType.RAISE, inc, 
                               self.street_contrib[pid]+inc, is_ai)
                if is_ai:
                    self.all_in.add(pid)
                    
                to_call = self.street_contrib[pid]
                acted_since_raise = {pid}
                self.last_aggressor = pid

            # Stop if everyone left is all-in
            if all((p not in self.active) or (p in self.all_in) for p in self.players):
                pending = False

        return False, None

    def _everybody_matched(self, to_call: int, acted_since_raise: set) -> bool:
        """Check if all active players have matched the current bet."""
        for p in self.players:
            if p in self.active and p not in self.all_in:
                if self.street_contrib[p] < to_call and p not in acted_since_raise:
                    return False
        return True

    def _pot_for_round(self) -> int:
        """Calculate pot size for this betting round."""
        return sum(self.street_contrib.values())

# ----------------------------
# Pot builder (from contributions)
# ----------------------------
def build_pots(total_contrib: Dict[str,int], active_order: List[str]) -> List[Pot]:
    """
    Build main/side pots from total contributions.
    Returns Pot list with correct eligible sets.
    """
    contrib = {p: total_contrib.get(p,0) for p in active_order}
    contrib = {p:v for p,v in contrib.items() if v>0}
    if not contrib:
        return []

    # Sort by committed ascending (classic side-pot construction)
    levels = sorted(set(contrib.values()))
    pots: List[Pot] = []
    prev = 0
    remaining = set(contrib.keys())
    
    for lvl in levels:
        slice_amt = (lvl - prev) * len(remaining)
        if slice_amt > 0:
            pots.append(Pot(amount=slice_amt, eligible_player_ids=sorted(remaining), shares=[]))
        prev = lvl
        # Remove those who are capped at this level
        for p, v in list(contrib.items()):
            if v == lvl:
                remaining.discard(p)
    return pots

def split_pots_randomly(pots: List[Pot], finalists: List[str], rng: random.Random):
    """Assign random winners among each pot's eligible players."""
    for pot in pots:
        elig = [p for p in pot.eligible_player_ids if p in finalists]
        if not elig:
            continue
            
        # Pick 1–3 winners randomly from eligible
        k = rng.randint(1, min(3, len(elig)))
        winners = rng.sample(elig, k=k)
        share = pot.amount // k
        remainder = pot.amount - share*k
        
        for i, w in enumerate(winners):
            pot.shares.append(PotShare(
                player_id=w, 
                amount=share + (1 if i < remainder else 0)
            ))

# ----------------------------
# Invariant checks
# ----------------------------
def validate_hand_invariants(hand: Hand):
    """Validate structural and mathematical invariants."""
    # 1) Street order monotonicity in action.order
    last_order = 0
    for st in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
        for a in hand.streets[st].actions:
            assert a.order > last_order, f"Action order must be strictly increasing: {a.order} <= {last_order}"
            last_order = a.order
            assert a.amount >= 0, f"Negative chip movement not allowed: {a.amount}"
            
            # Actor validity
            if a.actor_id is not None:
                assert any(s.player_id == a.actor_id for s in hand.seats), f"Unknown actor_id: {a.actor_id}"
    
    # 2) Boards: flop 3, turn adds 1, river adds 1 (if present)
    flop = hand.streets[Street.FLOP].board
    turn = hand.streets[Street.TURN].board
    river = hand.streets[Street.RIVER].board
    
    if flop:  
        assert len(flop) == 3, f"Flop must have 3 cards, got {len(flop)}"
    if turn:  
        assert len(turn) == 4 and turn[:3] == flop, f"Turn must have 4 cards with same flop"
    if river: 
        assert len(river) == 5 and river[:4] == turn, f"River must have 5 cards with same turn"
    
    # 3) Pots non-negative and shares sum to pot.amount
    for i, p in enumerate(hand.pots):
        assert p.amount >= 0, f"Pot {i} amount must be non-negative: {p.amount}"
        if p.shares:
            total_shares = sum(s.amount for s in p.shares)
            assert total_shares == p.amount, f"Pot {i} shares ({total_shares}) don't sum to pot amount ({p.amount})"
    
    # 4) Final stacks consistency check
    if hand.final_stacks:
        expected_players = set(s.player_id for s in hand.seats)
        actual_players = set(hand.final_stacks.keys())
        assert expected_players == actual_players, f"Final stacks players mismatch: {expected_players} vs {actual_players}"

# ----------------------------
# Hand generator (fuzzer)
# ----------------------------
def generate_random_hand(num_players: int, seed: int) -> Hand:
    """Generate a random but valid poker hand for testing."""
    rng = random.Random(seed)
    
    # Table configuration
    sb = rng.choice([25, 50, 100, 200])
    bb = sb * 2
    ante = rng.choice([0, 5, 10, sb//2])
    rake = rng.choice([0, bb//4, bb//2, bb])
    run_count = rng.choice([1, 1, 1, 2])  # Mostly once, sometimes twice

    # Create seats
    seats = []
    for i in range(num_players):
        pid = f"p{i+1}"
        seats.append(Seat(
            seat_no=i+1, 
            player_id=pid, 
            display_name=f"Player{i+1}", 
            starting_stack=rng.randint(5_000, 50_000),
            is_button=(i==0)  # Seat 1 as button
        ))

    # Create hand
    hand = Hand(
        metadata=HandMetadata(
            table_id=f"T-{seed % 100}",
            hand_id=f"H#{seed}",
            small_blind=sb,
            big_blind=bb,
            ante=ante,
            rake=rake,
            run_count=run_count,
            started_at_utc="2025-01-15T12:00:00Z",
            session_type=rng.choice(["gto", "practice", "review"]),
            bot_strategy=rng.choice(["gto_v1", "tight_aggressive", "loose_passive"]),
            analysis_tags=rng.sample(["premium_cards", "3bet_pot", "bluff_catch", "value_bet"], 
                                   k=rng.randint(0, 2))
        ),
        seats=seats,
        hero_player_id=seats[0].player_id
    )

    # Initialize deck and hole cards
    deck = fresh_deck()
    rng.shuffle(deck)
    hole: Dict[str, List[str]] = {s.player_id: draw(deck, 2) for s in seats}

    # Setup table state and postings
    ts = TableState([s.player_id for s in seats], sb, bb, ante, rng)
    ts.post_antes(hand)
    
    with_straddle = rng.random() < 0.2
    sb_idx = 1 % num_players  # Button at index 0 -> SB at 1
    ts.post_blinds_and_straddle(hand, sb_idx, with_straddle)

    # Deal marker
    hand.streets[Street.PREFLOP].actions.append(Action(
        order=ts.order_counter, 
        street=Street.PREFLOP, 
        actor_id=None, 
        action=ActionType.DEAL_HOLE, 
        amount=0, 
        note="Dealt hole cards"
    ))
    ts.order_counter += 1

    # PREFLOP betting
    ts.street_reset()
    ended, winner = ts.run_betting_round(hand, Street.PREFLOP, 
                                       opener_idx=(sb_idx+1) % num_players, 
                                       min_raise=bb)
    if ended:
        # Early end - build pots and finish
        pots = build_pots(ts.total_contrib, [s.player_id for s in seats])
        if pots and rake:
            rake_to_apply = min(rake, pots[0].amount)
            pots[0].amount -= rake_to_apply
        if pots:
            split_pots_randomly(pots, [winner], rng)
        hand.pots = pots
        hand.metadata.ended_at_utc = "2025-01-15T12:01:00Z"
        hand.final_stacks = {s.player_id: s.starting_stack for s in seats}
        return hand

    # FLOP
    if len(ts.active) > 1:
        flop = draw(deck, 3)
        hand.streets[Street.FLOP].board = flop
        ts.street_reset()
        ended, winner = ts.run_betting_round(hand, Street.FLOP, 
                                           opener_idx=(sb_idx+1) % num_players, 
                                           min_raise=bb)
        if ended:
            pots = build_pots(ts.total_contrib, [s.player_id for s in seats])
            if pots and rake:
                rake_to_apply = min(rake, pots[0].amount)
                pots[0].amount -= rake_to_apply
            if pots:
                split_pots_randomly(pots, [winner], rng)
            hand.pots = pots
            hand.metadata.ended_at_utc = "2025-01-15T12:02:00Z"
            hand.final_stacks = {s.player_id: s.starting_stack for s in seats}
            return hand

    # TURN
    if len(ts.active) > 1:
        turn_card = draw(deck, 1)
        hand.streets[Street.TURN].board = flop + turn_card
        ts.street_reset()
        ended, winner = ts.run_betting_round(hand, Street.TURN, 
                                           opener_idx=(sb_idx+1) % num_players, 
                                           min_raise=bb*2)
        if ended:
            pots = build_pots(ts.total_contrib, [s.player_id for s in seats])
            if pots and rake:
                rake_to_apply = min(rake, pots[0].amount)
                pots[0].amount -= rake_to_apply
            if pots:
                split_pots_randomly(pots, [winner], rng)
            hand.pots = pots
            hand.metadata.ended_at_utc = "2025-01-15T12:03:00Z"
            hand.final_stacks = {s.player_id: s.starting_stack for s in seats}
            return hand

    # RIVER
    if len(ts.active) > 1:
        river_card = draw(deck, 1)
        hand.streets[Street.RIVER].board = flop + turn_card + river_card
        ts.street_reset()
        ts.run_betting_round(hand, Street.RIVER, 
                           opener_idx=(sb_idx+1) % num_players, 
                           min_raise=bb*2)

    # Final pots and showdown
    pots = build_pots(ts.total_contrib, [s.player_id for s in seats])
    if pots and rake:
        total_before_rake = sum(p.amount for p in pots)
        if total_before_rake >= rake:
            # Apply rake only if there's enough in the pot
            rake_to_apply = min(rake, pots[0].amount)
            pots[0].amount -= rake_to_apply

    # Choose finalists for showdown
    finalists = list(ts.active) if ts.active else [s.player_id for s in seats]
    split_pots_randomly(pots, finalists, rng)
    hand.pots = pots

    # Showdown entries
    sd = []
    for pid in finalists:
        show_cards = (rng.random() < 0.7)
        sd.append(ShowdownEntry(
            player_id=pid, 
            hole_cards=hole[pid] if show_cards else None,
            hand_rank="High Card" if show_cards else None
        ))
    hand.showdown = sd
    hand.metadata.ended_at_utc = "2025-01-15T12:05:00Z"
    hand.final_stacks = {s.player_id: s.starting_stack for s in seats}
    
    return hand

# ----------------------------
# Tests
# ----------------------------
class TestHandModel(unittest.TestCase):
    """Comprehensive test suite for hand model."""

    def roundtrip_test(self, hand: Hand):
        """Test JSON round-trip and invariant validation."""
        validate_hand_invariants(hand)
        
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "hand.json")
            hand.save_json(path)
            loaded = Hand.load_json(path)
            
            self.assertEqual(hand.to_dict(), loaded.to_dict(), "Round-trip JSON mismatch")
            validate_hand_invariants(loaded)

    def test_example_hand(self):
        """Test the example hand from hand_model.py."""
        # Run the example to make sure it works
        import sys
        import subprocess
        result = subprocess.run([sys.executable, "backend/core/hand_model.py"], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Example failed: {result.stderr}")
        self.assertIn("Saved and loaded successfully", result.stdout)

    def test_edge_cases(self):
        """Test specific edge cases."""
        # Heads-up
        h1 = generate_random_hand(num_players=2, seed=101)
        self.roundtrip_test(h1)
        
        # 9-max
        h2 = generate_random_hand(num_players=9, seed=999)
        self.roundtrip_test(h2)
        
        # 6-max typical
        h3 = generate_random_hand(num_players=6, seed=20250115)
        self.roundtrip_test(h3)

    def test_fuzz_many_hands(self):
        """Fuzz test across multiple scenarios."""
        test_count = 0
        for num_players in range(2, 10):  # 2-9 players
            for i in range(3):  # 3 hands per player count
                seed = 1000 + test_count
                hand = generate_random_hand(num_players=num_players, seed=seed)
                self.roundtrip_test(hand)
                test_count += 1
                
        print(f"✅ Successfully tested {test_count} randomly generated hands")

    def test_analysis_methods(self):
        """Test hand analysis helper methods."""
        hand = generate_random_hand(num_players=4, seed=12345)
        
        # Test analysis methods don't crash
        all_actions = hand.get_all_actions()
        self.assertIsInstance(all_actions, list)
        
        player_id = hand.seats[0].player_id
        player_actions = hand.get_actions_for_player(player_id)
        self.assertIsInstance(player_actions, list)
        
        final_board = hand.get_final_board()
        self.assertIsInstance(final_board, list)
        
        total_pot = hand.get_total_pot()
        self.assertIsInstance(total_pot, int)
        self.assertGreaterEqual(total_pot, 0)
        
        investment = hand.get_player_total_investment(player_id)
        self.assertIsInstance(investment, int)
        self.assertGreaterEqual(investment, 0)
        
        winnings = hand.get_player_winnings(player_id)
        self.assertIsInstance(winnings, int)
        self.assertGreaterEqual(winnings, 0)
        
        net_result = hand.get_net_result(player_id)
        self.assertIsInstance(net_result, int)

if __name__ == "__main__":
    # Clean up any existing example files
    if os.path.exists("example_hand.json"):
        os.remove("example_hand.json")
        
    unittest.main(verbosity=2)
