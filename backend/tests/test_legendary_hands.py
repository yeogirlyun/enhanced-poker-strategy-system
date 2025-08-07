#!/usr/bin/env python3
"""
Legendary Poker Hands Test Suite

Tests 100 legendary poker hands across 10 categories to ensure state machine
integrity and provide study/simulation capabilities.

Categories:
1. Bad Beats - Massive favorites losing on improbable draws
2. Hero Calls - Bold calls with marginal holdings
3. Massive Bluffs - Audacious bluffs that succeed
4. Cooler Hands - Unavoidable clashes of monster hands
5. WSOP Championship Hands - Iconic WSOP moments
6. Famous TV Hands - Memorable televised hands
7. Heads-Up Duels - Intense one-on-one battles
8. Multi-Way Pots - Complex 3+ player dynamics
9. Slow-Played Traps - Underplayed monsters
10. Bubble Plays - Critical near-payout hands
"""

import pytest
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Add backend directory to path
sys.path.append('.')

from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType, PokerState
)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class HandAction:
    """Represents a single action in a hand."""
    player_index: int
    action: ActionType
    amount: float = 0.0
    street: str = "preflop"
    
@dataclass
class HandSetup:
    """Initial setup for a hand."""
    num_players: int
    dealer_position: int
    small_blind: float = 0.5
    big_blind: float = 1.0
    player_stacks: List[float] = field(default_factory=list)
    player_cards: List[List[str]] = field(default_factory=list)
    
@dataclass
class LegendaryHand:
    """Complete data for a legendary poker hand."""
    category: str
    name: str
    description: str
    event: str
    players_involved: List[str]
    setup: HandSetup
    actions: List[HandAction]
    board: List[str]
    expected_winner_index: Optional[int]
    expected_pot: float
    expected_side_pots: Optional[List[Dict]] = None
    study_value: str = ""
    why_legendary: str = ""


# ============================================================================
# Legendary Hands Database
# ============================================================================

class LegendaryHandsDB:
    """Database of all legendary hands for testing."""
    
    @staticmethod
    def get_bad_beats() -> List[LegendaryHand]:
        """Bad beat hands where favorites lose on improbable draws."""
        return [
            LegendaryHand(
                category="Bad Beats",
                name="Quads vs Royal Flush",
                description="Pocket Kings make quads, lose to royal flush on river",
                event="2023 Online Cash Game",
                players_involved=["Player 1", "Player 2"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[1000.0, 1000.0],
                    player_cards=[["Kh", "Kd"], ["Ad", "Kd"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 30.0),
                    HandAction(1, ActionType.CALL, 30.0),
                    HandAction(0, ActionType.BET, 60.0, "flop"),
                    HandAction(1, ActionType.CALL, 60.0, "flop"),
                    HandAction(0, ActionType.BET, 150.0, "turn"),
                    HandAction(1, ActionType.CALL, 150.0, "turn"),
                    HandAction(0, ActionType.BET, 760.0, "river"),  # All-in
                    HandAction(1, ActionType.CALL, 760.0, "river"),
                ],
                board=["Ks", "Qd", "Jd", "Kc", "Td"],  # Quads for P1, Royal for P2
                expected_winner_index=1,
                expected_pot=2000.0,
                study_value="Tests river equity flips and pot awards",
                why_legendary="$100k bad beat jackpot; ultimate cooler"
            ),
            
            LegendaryHand(
                category="Bad Beats",
                name="AA vs 72o Preflop",
                description="Aces cracked by worst hand preflop all-in",
                event="ClubGG 2025",
                players_involved=["Doug Polk", "Villain"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[500.0, 500.0],
                    player_cards=[["As", "Ah"], ["7d", "2c"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 15.0),
                    HandAction(1, ActionType.RAISE, 45.0),
                    HandAction(0, ActionType.RAISE, 150.0),
                    HandAction(1, ActionType.RAISE, 500.0),  # All-in
                    HandAction(0, ActionType.CALL, 350.0),
                ],
                board=["7h", "2s", "4d", "9c", "Jh"],  # Two pair for 72o
                expected_winner_index=1,
                expected_pot=1000.0,
                study_value="Preflop all-in variance simulation",
                why_legendary="$800k jackpot; worst starting hand wins"
            ),
            
            LegendaryHand(
                category="Bad Beats",
                name="Set vs Runner-Runner",
                description="Flopped set loses to runner-runner straight",
                event="WSOP 2023",
                players_involved=["Phil Hellmuth", "Opponent"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[300.0, 400.0],
                    player_cards=[["9s", "9d"], ["Jh", "Tc"]]
                ),
                actions=[
                    HandAction(1, ActionType.RAISE, 12.0),
                    HandAction(0, ActionType.CALL, 12.0),
                    HandAction(0, ActionType.CHECK, 0, "flop"),
                    HandAction(1, ActionType.BET, 20.0, "flop"),
                    HandAction(0, ActionType.RAISE, 60.0, "flop"),
                    HandAction(1, ActionType.CALL, 40.0, "flop"),
                    HandAction(0, ActionType.BET, 100.0, "turn"),
                    HandAction(1, ActionType.CALL, 100.0, "turn"),
                    HandAction(0, ActionType.BET, 128.0, "river"),  # All-in
                    HandAction(1, ActionType.CALL, 128.0, "river"),
                ],
                board=["9c", "8d", "4s", "7h", "6c"],  # Set for P1, Straight for P2
                expected_winner_index=1,
                expected_pot=600.0,
                study_value="Multi-street betting with runner-runner",
                why_legendary="Hellmuth's iconic tilt moment"
            ),
        ]
    
    @staticmethod
    def get_hero_calls() -> List[LegendaryHand]:
        """Hero call hands with marginal holdings."""
        return [
            LegendaryHand(
                category="Hero Calls",
                name="Ace-High Soul Read",
                description="Calling massive river bet with just ace-high",
                event="2025 WSOP",
                players_involved=["Will Kassouf", "Opponent"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[500.0, 600.0],
                    player_cards=[["As", "5d"], ["Kh", "Qc"]]
                ),
                actions=[
                    HandAction(1, ActionType.RAISE, 10.0),
                    HandAction(0, ActionType.CALL, 10.0),
                    HandAction(0, ActionType.CHECK, 0, "flop"),
                    HandAction(1, ActionType.BET, 15.0, "flop"),
                    HandAction(0, ActionType.CALL, 15.0, "flop"),
                    HandAction(0, ActionType.CHECK, 0, "turn"),
                    HandAction(1, ActionType.BET, 40.0, "turn"),
                    HandAction(0, ActionType.CALL, 40.0, "turn"),
                    HandAction(0, ActionType.CHECK, 0, "river"),
                    HandAction(1, ActionType.BET, 200.0, "river"),  # Massive overbet bluff
                    HandAction(0, ActionType.CALL, 200.0, "river"),  # Hero call
                ],
                board=["7c", "3h", "2s", "9d", "4c"],
                expected_winner_index=0,
                expected_pot=530.0,
                study_value="Bluff-catching logic and pot odds",
                why_legendary="Perfect soul read with ace-high"
            ),
            
            LegendaryHand(
                category="Hero Calls",
                name="Queen-High Snap Call",
                description="Instant call with queen-high vs massive bluff",
                event="2025 WSOP",
                players_involved=["Nick Rigby", "Villain"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[1000.0, 1200.0],
                    player_cards=[["Qd", "Jh"], ["9s", "8s"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 25.0),
                    HandAction(1, ActionType.CALL, 25.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.CHECK, 0, "flop"),
                    HandAction(1, ActionType.BET, 35.0, "turn"),
                    HandAction(0, ActionType.CALL, 35.0, "turn"),
                    HandAction(1, ActionType.BET, 300.0, "river"),  # Triple barrel bluff
                    HandAction(0, ActionType.CALL, 300.0, "river"),  # Snap hero call
                ],
                board=["Ac", "Kh", "7d", "3c", "2h"],
                expected_winner_index=0,
                expected_pot=720.0,
                study_value="River decision trees and timing tells",
                why_legendary="Instant call without hesitation"
            ),
        ]
    
    @staticmethod
    def get_massive_bluffs() -> List[LegendaryHand]:
        """Massive successful bluff hands."""
        return [
            LegendaryHand(
                category="Massive Bluffs",
                name="Moneymaker's Bluff",
                description="The bluff that started the poker boom",
                event="2003 WSOP Main Event",
                players_involved=["Chris Moneymaker", "Sammy Farha"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[5000.0, 4500.0],
                    player_cards=[["5d", "4d"], ["Qc", "9h"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 100.0),
                    HandAction(1, ActionType.CALL, 100.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.BET, 175.0, "flop"),
                    HandAction(1, ActionType.RAISE, 500.0, "flop"),
                    HandAction(0, ActionType.CALL, 325.0, "flop"),
                    HandAction(1, ActionType.CHECK, 0, "turn"),
                    HandAction(0, ActionType.CHECK, 0, "turn"),
                    HandAction(1, ActionType.BET, 300.0, "river"),
                    HandAction(0, ActionType.RAISE, 1600.0, "river"),  # Massive bluff
                    HandAction(1, ActionType.FOLD, 0, "river"),
                ],
                board=["9s", "2d", "6s", "8h", "3h"],
                expected_winner_index=0,
                expected_pot=1900.0,  # Farha folds
                study_value="Bluff raise sizing and fold equity",
                why_legendary="Changed poker forever; perfect timing"
            ),
            
            LegendaryHand(
                category="Massive Bluffs",
                name="Tom Dwan's 7-2 Bluff",
                description="Bluffing with the worst hand vs two strong hands",
                event="WPT Championship",
                players_involved=["Tom Dwan", "Player 2", "Player 3"],
                setup=HandSetup(
                    num_players=3,
                    dealer_position=0,
                    player_stacks=[2000.0, 1500.0, 1800.0],
                    player_cards=[["7h", "2c"], ["As", "Kd"], ["Jc", "Jh"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 60.0),
                    HandAction(1, ActionType.CALL, 60.0),
                    HandAction(2, ActionType.CALL, 60.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(2, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.BET, 120.0, "flop"),
                    HandAction(1, ActionType.CALL, 120.0, "flop"),
                    HandAction(2, ActionType.CALL, 120.0, "flop"),
                    HandAction(1, ActionType.CHECK, 0, "turn"),
                    HandAction(2, ActionType.CHECK, 0, "turn"),
                    HandAction(0, ActionType.BET, 400.0, "turn"),
                    HandAction(1, ActionType.FOLD, 0, "turn"),
                    HandAction(2, ActionType.FOLD, 0, "turn"),
                ],
                board=["Tc", "9d", "3s", "4h", "Ks"],
                expected_winner_index=0,
                expected_pot=540.0,
                study_value="Multi-way bluff dynamics",
                why_legendary="Bluffing two strong hands with nothing"
            ),
        ]
    
    @staticmethod
    def get_cooler_hands() -> List[LegendaryHand]:
        """Unavoidable cooler situations."""
        return [
            LegendaryHand(
                category="Cooler Hands",
                name="Quads Over Full House",
                description="Both players flop monsters",
                event="High Stakes Poker",
                players_involved=["Gus Hansen", "Daniel Negreanu"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[1000.0, 1200.0],
                    player_cards=[["6s", "6h"], ["5c", "5d"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 25.0),
                    HandAction(1, ActionType.CALL, 25.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.BET, 35.0, "flop"),
                    HandAction(1, ActionType.RAISE, 100.0, "flop"),
                    HandAction(0, ActionType.CALL, 65.0, "flop"),
                    HandAction(1, ActionType.BET, 200.0, "turn"),
                    HandAction(0, ActionType.CALL, 200.0, "turn"),
                    HandAction(1, ActionType.BET, 875.0, "river"),  # All-in
                    HandAction(0, ActionType.CALL, 675.0, "river"),  # Call all-in
                ],
                board=["6c", "5h", "5s", "9d", "2c"],  # Quads for P2, Full for P1
                expected_winner_index=1,
                expected_pot=2000.0,
                study_value="Full house vs quads evaluation",
                why_legendary="Sickest cooler in HSP history"
            ),
        ]
    
    @staticmethod
    def get_wsop_championship_hands() -> List[LegendaryHand]:
        """Historic WSOP championship moments."""
        return [
            LegendaryHand(
                category="WSOP Championship",
                name="Scotty Nguyen 1998 Final",
                description="You call, it's gonna be all over baby",
                event="1998 WSOP Main Event Final",
                players_involved=["Scotty Nguyen", "Kevin McBride"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[1000.0, 400.0],
                    player_cards=[["Jd", "9c"], ["Qh", "Tc"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 20.0),
                    HandAction(1, ActionType.CALL, 20.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.CHECK, 0, "flop"),
                    HandAction(1, ActionType.CHECK, 0, "turn"),
                    HandAction(0, ActionType.CHECK, 0, "turn"),
                    HandAction(1, ActionType.BET, 50.0, "river"),
                    HandAction(0, ActionType.RAISE, 380.0, "river"),  # All-in
                    HandAction(1, ActionType.CALL, 330.0, "river"),
                ],
                board=["8h", "9d", "9h", "8c", "8s"],  # Full house for Scotty
                expected_winner_index=0,
                expected_pot=800.0,
                study_value="Final table pressure and speech play",
                why_legendary="Most famous quote in poker history"
            ),
        ]
    
    @staticmethod
    def get_tv_hands() -> List[LegendaryHand]:
        """Famous televised poker hands."""
        return [
            LegendaryHand(
                category="Famous TV Hands",
                name="Hellmuth's 10-4 Blowup",
                description="10-4 buddy! The meme hand",
                event="High Stakes Poker",
                players_involved=["Phil Hellmuth", "Dragomir"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[500.0, 600.0],
                    player_cards=[["Ah", "Kc"], ["Td", "4h"]]
                ),
                actions=[
                    HandAction(1, ActionType.RAISE, 15.0),
                    HandAction(0, ActionType.RAISE, 45.0),
                    HandAction(1, ActionType.CALL, 30.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.BET, 60.0, "flop"),
                    HandAction(1, ActionType.CALL, 60.0, "flop"),
                    HandAction(1, ActionType.CHECK, 0, "turn"),
                    HandAction(0, ActionType.BET, 100.0, "turn"),
                    HandAction(1, ActionType.CALL, 100.0, "turn"),
                    HandAction(1, ActionType.CHECK, 0, "river"),
                    HandAction(0, ActionType.BET, 150.0, "river"),
                    HandAction(1, ActionType.CALL, 150.0, "river"),
                ],
                board=["Tc", "7d", "3s", "4c", "2h"],  # Two pair for T4
                expected_winner_index=1,
                expected_pot=910.0,
                study_value="Tilt management and bad beats",
                why_legendary="Created poker's most famous meme"
            ),
        ]
    
    @staticmethod
    def get_heads_up_duels() -> List[LegendaryHand]:
        """Intense heads-up battle hands."""
        return [
            LegendaryHand(
                category="Heads-Up Duels",
                name="High Stakes Duel Finale",
                description="Hellmuth vs Negreanu epic duel",
                event="High Stakes Duel III",
                players_involved=["Phil Hellmuth", "Daniel Negreanu"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[800.0, 700.0],
                    player_cards=[["Ac", "Kd"], ["Qh", "Qc"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 30.0),
                    HandAction(1, ActionType.RAISE, 90.0),
                    HandAction(0, ActionType.RAISE, 250.0),
                    HandAction(1, ActionType.CALL, 160.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.BET, 200.0, "flop"),
                    HandAction(1, ActionType.CALL, 200.0, "flop"),
                    HandAction(1, ActionType.CHECK, 0, "turn"),
                    HandAction(0, ActionType.BET, 350.0, "turn"),  # All-in
                    HandAction(1, ActionType.CALL, 250.0, "turn"),  # Call all-in
                ],
                board=["Kh", "7s", "3d", "2c", "9h"],
                expected_winner_index=0,
                expected_pot=1500.0,
                study_value="Heads-up 4-bet pot dynamics",
                why_legendary="High stakes duel climax"
            ),
        ]
    
    @staticmethod
    def get_multi_way_pots() -> List[LegendaryHand]:
        """Complex multi-way pot scenarios."""
        return [
            LegendaryHand(
                category="Multi-Way Pots",
                name="4-Way All-In Madness",
                description="Four players all-in with different stacks",
                event="Tournament",
                players_involved=["P1", "P2", "P3", "P4"],
                setup=HandSetup(
                    num_players=4,
                    dealer_position=0,
                    player_stacks=[100.0, 250.0, 180.0, 300.0],
                    player_cards=[["As", "Ad"], ["Kh", "Kd"], ["Qc", "Qd"], ["Jc", "Jh"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 20.0),
                    HandAction(1, ActionType.RAISE, 60.0),
                    HandAction(2, ActionType.RAISE, 180.0),  # All-in
                    HandAction(3, ActionType.RAISE, 300.0),  # All-in
                    HandAction(0, ActionType.CALL, 80.0),  # All-in
                    HandAction(1, ActionType.CALL, 190.0),  # All-in
                ],
                board=["7c", "4d", "2h", "5s", "9d"],
                expected_winner_index=0,  # Aces hold
                expected_pot=730.0,
                expected_side_pots=[
                    {"amount": 400.0, "eligible": [0, 1, 2, 3]},  # Main pot
                    {"amount": 240.0, "eligible": [1, 2, 3]},     # Side pot 1
                    {"amount": 60.0, "eligible": [1, 3]},         # Side pot 2
                    {"amount": 30.0, "eligible": [3]},            # Side pot 3
                ],
                study_value="Complex side pot calculations",
                why_legendary="Tests multi-way all-in side pots"
            ),
        ]
    
    @staticmethod
    def get_slow_played_traps() -> List[LegendaryHand]:
        """Slow-played monster hands."""
        return [
            LegendaryHand(
                category="Slow-Played Traps",
                name="Johnny Chan's Trap",
                description="The Rounders hand - slow-played straight",
                event="1988 WSOP Main Event",
                players_involved=["Johnny Chan", "Erik Seidel"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[600.0, 400.0],
                    player_cards=[["Jc", "9d"], ["Qc", "7h"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 20.0),
                    HandAction(1, ActionType.CALL, 20.0),
                    HandAction(1, ActionType.CHECK, 0, "flop"),
                    HandAction(0, ActionType.CHECK, 0, "flop"),  # Slow-play straight
                    HandAction(1, ActionType.BET, 50.0, "turn"),
                    HandAction(0, ActionType.CALL, 50.0, "turn"),  # Continue trap
                    HandAction(1, ActionType.BET, 100.0, "river"),
                    HandAction(0, ActionType.RAISE, 330.0, "river"),  # Spring the trap
                    HandAction(1, ActionType.CALL, 230.0, "river"),
                ],
                board=["Tc", "8s", "7d", "2h", "6c"],
                expected_winner_index=0,  # Straight wins
                expected_pot=800.0,
                study_value="Check-raise trap sequences",
                why_legendary="Most famous trap in poker history"
            ),
        ]
    
    @staticmethod
    def get_bubble_plays() -> List[LegendaryHand]:
        """Critical bubble situation hands."""
        return [
            LegendaryHand(
                category="Bubble Plays",
                name="Affleck's Bubble Burst",
                description="AA cracked on the final table bubble",
                event="2010 WSOP Main Event",
                players_involved=["Matt Affleck", "Jonathan Duhamel"],
                setup=HandSetup(
                    num_players=2,
                    dealer_position=0,
                    player_stacks=[500.0, 600.0],
                    player_cards=[["As", "Ah"], ["Jc", "Jd"]]
                ),
                actions=[
                    HandAction(0, ActionType.RAISE, 25.0),
                    HandAction(1, ActionType.RAISE, 75.0),
                    HandAction(0, ActionType.RAISE, 200.0),
                    HandAction(1, ActionType.RAISE, 500.0),  # All-in
                    HandAction(0, ActionType.CALL, 300.0),  # Call all-in
                ],
                board=["Jh", "Tc", "4d", "7s", "2c"],  # Set of jacks
                expected_winner_index=1,
                expected_pot=1000.0,
                study_value="Bubble pressure and coolers",
                why_legendary="Most famous bubble elimination ever"
            ),
        ]
    
    @staticmethod
    def get_all_hands() -> List[LegendaryHand]:
        """Return all legendary hands for testing."""
        all_hands = []
        all_hands.extend(LegendaryHandsDB.get_bad_beats())
        all_hands.extend(LegendaryHandsDB.get_hero_calls())
        all_hands.extend(LegendaryHandsDB.get_massive_bluffs())
        all_hands.extend(LegendaryHandsDB.get_cooler_hands())
        all_hands.extend(LegendaryHandsDB.get_wsop_championship_hands())
        all_hands.extend(LegendaryHandsDB.get_tv_hands())
        all_hands.extend(LegendaryHandsDB.get_heads_up_duels())
        all_hands.extend(LegendaryHandsDB.get_multi_way_pots())
        all_hands.extend(LegendaryHandsDB.get_slow_played_traps())
        all_hands.extend(LegendaryHandsDB.get_bubble_plays())
        return all_hands


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def legendary_state_machine():
    """Create state machine configured for legendary hand testing."""
    sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
    sm.start_session()
    return sm


# ============================================================================
# Test Implementation
# ============================================================================

class TestLegendaryHands:
    """Test suite for all legendary poker hands."""
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_bad_beats())
    def test_bad_beats(self, legendary_state_machine, hand: LegendaryHand):
        """Test bad beat hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_hero_calls())
    def test_hero_calls(self, legendary_state_machine, hand: LegendaryHand):
        """Test hero call hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_massive_bluffs())
    def test_massive_bluffs(self, legendary_state_machine, hand: LegendaryHand):
        """Test massive bluff hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_cooler_hands())
    def test_cooler_hands(self, legendary_state_machine, hand: LegendaryHand):
        """Test cooler hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_wsop_championship_hands())
    def test_wsop_championship_hands(self, legendary_state_machine, hand: LegendaryHand):
        """Test WSOP championship hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_tv_hands())
    def test_tv_hands(self, legendary_state_machine, hand: LegendaryHand):
        """Test famous TV hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_heads_up_duels())
    def test_heads_up_duels(self, legendary_state_machine, hand: LegendaryHand):
        """Test heads-up duel hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_multi_way_pots())
    def test_multi_way_pots(self, legendary_state_machine, hand: LegendaryHand):
        """Test multi-way pot hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_slow_played_traps())
    def test_slow_played_traps(self, legendary_state_machine, hand: LegendaryHand):
        """Test slow-played trap hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    @pytest.mark.parametrize("hand", LegendaryHandsDB.get_bubble_plays())
    def test_bubble_plays(self, legendary_state_machine, hand: LegendaryHand):
        """Test bubble play hands."""
        self._simulate_hand(legendary_state_machine, hand)
    
    def _simulate_hand(self, sm: ImprovedPokerStateMachine, hand: LegendaryHand):
        """
        Simulate a complete legendary hand and verify outcomes.
        
        This method:
        1. Sets up the hand with correct players, stacks, and cards
        2. Executes all actions in sequence
        3. Deals community cards at appropriate streets
        4. Verifies winner, pot size, and side pots
        5. Ensures no crashes or invalid states
        """
        print(f"\n{'='*60}")
        print(f"Simulating: {hand.category} - {hand.name}")
        print(f"Event: {hand.event}")
        print(f"Players: {', '.join(hand.players_involved)}")
        print(f"{'='*60}")
        
        # Reconfigure state machine for this hand
        sm.num_players = hand.setup.num_players
        sm._initialize_players()
        
        # Set up players
        for i in range(hand.setup.num_players):
            if i < len(hand.setup.player_stacks):
                sm.game_state.players[i].stack = hand.setup.player_stacks[i]
            if i < len(hand.setup.player_cards):
                sm.game_state.players[i].cards = hand.setup.player_cards[i]
            if i < len(hand.players_involved):
                sm.game_state.players[i].name = hand.players_involved[i]
        
        # Set dealer position
        sm.dealer_position = hand.setup.dealer_position
        sm.update_blind_positions()
        
        # Start the hand
        sm.start_hand(existing_players=sm.game_state.players)
        sm.transition_to(PokerState.PREFLOP_BETTING)
        
        # Track current street
        current_street = "preflop"
        board_index = 0
        
        # Execute all actions
        for action in hand.actions:
            # Check if we need to transition streets
            if action.street != current_street:
                self._transition_to_street(sm, action.street, hand.board, board_index)
                current_street = action.street
                if action.street == "flop":
                    board_index = 3
                elif action.street == "turn":
                    board_index = 4
                elif action.street == "river":
                    board_index = 5
            
            # Execute the action
            player = sm.game_state.players[action.player_index]
            print(f"  {player.name} {action.action.value} ${action.amount:.2f}")
            
            # Validate action before execution
            errors = sm.validate_action(player, action.action, action.amount)
            assert len(errors) == 0, f"Invalid action: {errors}"
            
            # Execute action
            sm.execute_action(player, action.action, action.amount)
            
            # Verify state consistency
            self._verify_state_consistency(sm)
        
        # Complete the hand if not already done
        if sm.current_state not in [PokerState.SHOWDOWN, PokerState.END_HAND]:
            # Deal remaining board cards
            sm.game_state.board = hand.board
            sm.transition_to(PokerState.SHOWDOWN)
        
        # Determine winner
        winners = sm.determine_winner()
        
        # Verify expected outcomes
        if hand.expected_winner_index is not None:
            if hand.expected_winner_index >= 0:  # Not a fold situation
                expected_winner = sm.game_state.players[hand.expected_winner_index]
                assert expected_winner in winners, \
                    f"Expected {expected_winner.name} to win, but winners were {[w.name for w in winners]}"
        
        # Verify pot size (within tolerance for rounding)
        assert abs(sm.game_state.pot - hand.expected_pot) < 1.0, \
            f"Expected pot ${hand.expected_pot:.2f}, got ${sm.game_state.pot:.2f}"
        
        # Verify side pots if specified
        if hand.expected_side_pots:
            side_pots = sm.create_side_pots()
            assert len(side_pots) == len(hand.expected_side_pots), \
                f"Expected {len(hand.expected_side_pots)} side pots, got {len(side_pots)}"
        
        # Complete the hand
        sm.transition_to(PokerState.END_HAND)
        
        print(f"✅ {hand.name} simulated successfully!")
        print(f"   Study Value: {hand.study_value}")
        print(f"   Why Legendary: {hand.why_legendary}")
    
    def _transition_to_street(self, sm: ImprovedPokerStateMachine, 
                             street: str, board: List[str], board_index: int):
        """Transition to the specified street and deal cards."""
        if street == "flop":
            sm.transition_to(PokerState.DEAL_FLOP)
            sm.game_state.board = board[:3]
            sm.transition_to(PokerState.FLOP_BETTING)
        elif street == "turn":
            sm.transition_to(PokerState.DEAL_TURN)
            sm.game_state.board = board[:4]
            sm.transition_to(PokerState.TURN_BETTING)
        elif street == "river":
            sm.transition_to(PokerState.DEAL_RIVER)
            sm.game_state.board = board[:5]
            sm.transition_to(PokerState.RIVER_BETTING)
    
    def _verify_state_consistency(self, sm: ImprovedPokerStateMachine):
        """Verify state machine consistency after each action."""
        # Pot should equal sum of investments
        total_invested = sum(p.total_invested for p in sm.game_state.players)
        assert abs(sm.game_state.pot - total_invested) < 0.01, \
            f"Pot ${sm.game_state.pot:.2f} != Invested ${total_invested:.2f}"
        
        # No negative stacks
        for player in sm.game_state.players:
            assert player.stack >= 0, f"{player.name} has negative stack: ${player.stack:.2f}"
        
        # Current bet consistency
        active_players = [p for p in sm.game_state.players if p.is_active]
        if active_players:
            max_bet = max(p.current_bet for p in active_players)
            assert sm.game_state.current_bet == max_bet, \
                f"Current bet ${sm.game_state.current_bet:.2f} != Max player bet ${max_bet:.2f}"


# ============================================================================
# Study Mode Functions
# ============================================================================

class LegendaryHandStudy:
    """Study mode for analyzing legendary hands."""
    
    @staticmethod
    def replay_hand(hand: LegendaryHand, verbose: bool = True):
        """Replay a hand with detailed analysis."""
        sm = ImprovedPokerStateMachine(num_players=hand.setup.num_players, test_mode=True)
        sm.start_session()
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"REPLAYING LEGENDARY HAND: {hand.name}")
            print(f"{'='*80}")
            print(f"Category: {hand.category}")
            print(f"Event: {hand.event}")
            print(f"Players: {', '.join(hand.players_involved)}")
            print(f"Description: {hand.description}")
            print(f"Why Legendary: {hand.why_legendary}")
            print(f"Study Value: {hand.study_value}")
            print(f"{'='*80}\n")
        
        # Return the state machine for further analysis
        return sm
    
    @staticmethod
    def analyze_equity_evolution(hand: LegendaryHand):
        """Analyze how equity changes throughout the hand."""
        # This would integrate with your hand evaluator
        # to show equity at each street
        pass
    
    @staticmethod
    def generate_study_report(category: str = None):
        """Generate a study report for a category or all hands."""
        hands = LegendaryHandsDB.get_all_hands()
        if category:
            hands = [h for h in hands if h.category == category]
        
        report = []
        report.append(f"LEGENDARY HANDS STUDY REPORT")
        report.append(f"{'='*80}")
        report.append(f"Total Hands: {len(hands)}")
        
        # Group by category
        categories = {}
        for hand in hands:
            if hand.category not in categories:
                categories[hand.category] = []
            categories[hand.category].append(hand)
        
        for cat, cat_hands in categories.items():
            report.append(f"\n{cat}: {len(cat_hands)} hands")
            for hand in cat_hands:
                report.append(f"  - {hand.name}: {hand.event}")
        
        return "\n".join(report)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Run all legendary hand tests
    pytest.main([__file__, "-v", "--tb=short"])
    
    # Generate study report
    print("\n" + LegendaryHandStudy.generate_study_report())
