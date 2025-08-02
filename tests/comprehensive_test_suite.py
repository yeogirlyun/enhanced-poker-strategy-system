#!/usr/bin/env python3
"""
Comprehensive Test Suite for Improved Poker State Machine (Upgraded)

Tests all critical fixes and additional edge cases:
1. BB folding bug fix (BB checks with weak hands when no raise)
2. Dynamic position tracking
3. Correct raise logic
4. All-in state tracking and side pots
5. Strategy integration (preflop and postflop)
6. Input validation
7. State transitions
8. Showdown and winner determination
9. Hand evaluation cache
10. Multi-player interactions
11. Sound integration
12. Hand history logging
"""

import sys
import os
import time
import pytest
from typing import List, Dict, Any
from dataclasses import dataclass

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState
)
from gui_models import StrategyData, HandStrengthTier


# Mock dependencies
class MockSoundManager:
    def __init__(self):
        self.sounds = {
            "player_fold": True, "card_fold": True, "player_check": True,
            "player_call": True, "player_bet": True, "player_raise": True,
            "winner_announce": True, "card_deal": True
        }
        self.last_played = None

    def play(self, sound_name):
        self.last_played = sound_name

class MockHandEvaluator:
    class HandRank:
        def __init__(self, name):
            self.name = name

    def __init__(self):
        self.preflop_strengths = {
            "AA": 85, "KK": 82, "QQ": 80, "JJ": 77, "AKs": 67, "AKo": 65,
            "AQs": 66, "AQo": 64, "KTs": 45, "QJs": 40, "QTs": 38, "JTs": 35,
            "T9s": 30, "98s": 28, "87s": 25, "76s": 22, "65s": 20, "54s": 18,
            "T8s": 17, "TT": 55, "99": 50, "88": 45, "77": 40, "66": 35,
            "55": 30, "44": 25, "33": 20, "22": 15, "AJo": 45, "ATs": 50,
            "KJs": 48, "KQo": 42, "QJo": 35, "J9s": 32, "K9s": 38, "K8s": 30,
            "Q9s": 35, "A9s": 55, "A8s": 50, "A7s": 45, "A6s": 40, "A5s": 35,
            "A4s": 30, "A3s": 25, "A2s": 20, "72o": 1
        }
        self.postflop_strengths = {
            "high_card": 5, "pair": 15, "top_pair": 30, "top_pair_good_kicker": 40,
            "top_pair_bad_kicker": 25, "over_pair": 35, "two_pair": 45, "set": 60,
            "straight": 70, "flush": 80, "full_house": 90, "quads": 100,
            "straight_flush": 120, "gutshot_draw": 12, "open_ended_draw": 18,
            "flush_draw": 20, "combo_draw": 35, "nut_flush_draw": 25,
            "nut_straight_draw": 22, "overcard_draw": 8, "backdoor_flush": 3,
            "backdoor_straight": 2, "pair_plus_draw": 28, "set_plus_draw": 65
        }

    def get_preflop_hand_strength(self, cards):
        hand_str = self._get_hand_notation(cards)
        return self.preflop_strengths.get(hand_str, 1)

    def evaluate_hand(self, cards, board):
        hand_type = self.classify_hand(cards, board)
        return {
            "strength_score": self.postflop_strengths.get(hand_type, 5),
            "hand_rank": self.HandRank(hand_type),
            "hand_description": hand_type.replace("_", " ").title(),
            "rank_values": []
        }

    def classify_hand(self, cards, board):
        if not board:
            return "high_card"
        if len(board) >= 3 and cards[0][0] == board[0][0]:
            return "top_pair"
        if len(board) >= 3 and all(card[1] == board[0][1] for card in cards + board[:3]):
            return "flush"
        if len(board) >= 3 and cards[0][0] == cards[1][0]:
            return "set"
        return "high_card"

    def _compare_hands(self, hand1, hand2):
        rank_values = {"high_card": 1, "top_pair": 3, "set": 6, "flush": 8}
        rank1, values1 = hand1
        rank2, values2 = hand2
        if rank_values.get(rank1.name, 0) > rank_values.get(rank2.name, 0):
            return 1
        elif rank_values.get(rank1.name, 0) < rank_values.get(rank2.name, 0):
            return -1
        return 0

    def _get_hand_notation(self, cards):
        if len(cards) != 2:
            return ""
        rank1, suit1 = cards[0][0], cards[0][1]
        rank2, suit2 = cards[1][0], cards[1][1]
        if rank1 == rank2:
            return f"{rank1}{rank2}"
        suited = "s" if suit1 == suit2 else "o"
        rank_order = "AKQJT98765432"
        if rank_order.index(rank1) < rank_order.index(rank2):
            return f"{rank1}{rank2}{suited}"
        return f"{rank2}{rank1}{suited}"

# Test result tracking
@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None

class PokerStateMachineTestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.strategy_data = self._create_test_strategy()

    def _create_test_strategy(self) -> StrategyData:
        """Create a test strategy with minimal hands to test BB folding."""
        strategy = StrategyData()
        strategy.strategy_dict = {
            "preflop": {
                "AA": 85, "KK": 82, "QQ": 80, "JJ": 77, "AKs": 67, "AKo": 65,
                "AQs": 66, "AQo": 64, "KTs": 45, "QJs": 40, "QTs": 38, "JTs": 35,
                "T9s": 30, "98s": 28, "87s": 25, "76s": 22, "65s": 20, "54s": 18,
                "T8s": 17, "TT": 55, "99": 50, "88": 45, "77": 40, "66": 35,
                "55": 30, "44": 25, "33": 20, "22": 15, "AJo": 45, "ATs": 50,
                "KJs": 48, "KQo": 42, "QJo": 35, "J9s": 32, "K9s": 38, "K8s": 30,
                "Q9s": 35, "A9s": 55, "A8s": 50, "A7s": 45, "A6s": 40, "A5s": 35,
                "A4s": 30, "A3s": 25, "A2s": 20, "72o": 1,
                "open_rules": {
                    "UTG": {"threshold": 50, "sizing": 3.0},
                    "MP": {"threshold": 45, "sizing": 3.0},
                    "CO": {"threshold": 40, "sizing": 2.5},
                    "BTN": {"threshold": 30, "sizing": 2.5},
                    "SB": {"threshold": 35, "sizing": 3.0},
                    "BB": {"threshold": 35, "sizing": 3.0}
                },
                "vs_raise": {
                    "UTG": {"value_thresh": 75, "call_thresh": 60, "sizing": 3.0},
                    "MP": {"value_thresh": 72, "call_thresh": 55, "sizing": 3.0},
                    "CO": {"value_thresh": 70, "call_thresh": 50, "sizing": 2.5},
                    "BTN": {"value_thresh": 68, "call_thresh": 45, "sizing": 2.5},
                    "SB": {"value_thresh": 70, "call_thresh": 50, "sizing": 3.0},
                    "BB": {"value_thresh": 70, "call_thresh": 50, "sizing": 3.0}
                }
            },
            "postflop": {
                "high_card": 5, "pair": 15, "top_pair": 30, "top_pair_good_kicker": 40,
                "top_pair_bad_kicker": 25, "over_pair": 35, "two_pair": 45, "set": 60,
                "straight": 70, "flush": 80, "full_house": 90, "quads": 100,
                "straight_flush": 120, "gutshot_draw": 12, "open_ended_draw": 18,
                "flush_draw": 20, "combo_draw": 35, "nut_flush_draw": 25,
                "nut_straight_draw": 22, "overcard_draw": 8, "backdoor_flush": 3,
                "backdoor_straight": 2, "pair_plus_draw": 28, "set_plus_draw": 65,
                "pfa": {
                    "flop": {
                        "UTG": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.75},
                        "MP": {"val_thresh": 20, "check_thresh": 15, "sizing": 0.75},
                        "CO": {"val_thresh": 15, "check_thresh": 10, "sizing": 0.75},
                        "BTN": {"val_thresh": 10, "check_thresh": 10, "sizing": 0.75},
                        "SB": {"val_thresh": 15, "check_thresh": 15, "sizing": 0.75},
                        "BB": {"val_thresh": 15, "check_thresh": 15, "sizing": 0.75}
                    },
                    "turn": {
                        "UTG": {"val_thresh": 35, "check_thresh": 20, "sizing": 0.8},
                        "MP": {"val_thresh": 30, "check_thresh": 20, "sizing": 0.8},
                        "CO": {"val_thresh": 25, "check_thresh": 15, "sizing": 0.8},
                        "BTN": {"val_thresh": 20, "check_thresh": 15, "sizing": 0.8},
                        "SB": {"val_thresh": 25, "check_thresh": 20, "sizing": 0.8},
                        "BB": {"val_thresh": 25, "check_thresh": 20, "sizing": 0.8}
                    },
                    "river": {
                        "UTG": {"val_thresh": 40, "check_thresh": 25, "sizing": 1.0},
                        "MP": {"val_thresh": 35, "check_thresh": 25, "sizing": 1.0},
                        "CO": {"val_thresh": 30, "check_thresh": 20, "sizing": 1.0},
                        "BTN": {"val_thresh": 25, "check_thresh": 20, "sizing": 1.0},
                        "SB": {"val_thresh": 30, "check_thresh": 25, "sizing": 1.0},
                        "BB": {"val_thresh": 30, "check_thresh": 25, "sizing": 1.0}
                    }
                }
            }
        }
        strategy.tiers = [
            HandStrengthTier("Premium", 60, 100, "#ff0000", 
                            {"AA", "KK", "QQ", "JJ", "AKs", "AKo", "AQs", "AQo"})
        ]
        return strategy

    def log_test(self, name: str, passed: bool, message: str, details: Dict = None):
        """Log a test result."""
        self.results.append(TestResult(name, passed, message, details))

@pytest.fixture
def test_suite():
    """Fixture to create a test suite instance."""
    suite = PokerStateMachineTestSuite()
    ImprovedPokerStateMachine.hand_evaluator = MockHandEvaluator()
    return suite

@pytest.fixture
def state_machine(test_suite):
    """Fixture to create a state machine with mocked dependencies."""
    sm = ImprovedPokerStateMachine(num_players=6, strategy_data=test_suite.strategy_data)
    sm.sfx = MockSoundManager()
    sm._log_enabled = False  # Disable logging for performance
    return sm

@pytest.mark.parametrize("num_players,expected_positions", [
    (2, ["BTN/SB", "BB"]),
    (3, ["BTN", "SB", "BB"]),
    (6, ["BTN", "SB", "BB", "UTG", "MP", "CO"]),
    (9, ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "MP+1", "CO", "LJ"])
])
def test_position_tracking(test_suite, num_players, expected_positions):
    """Test dynamic position tracking for different table sizes."""
    sm = ImprovedPokerStateMachine(num_players=num_players)
    sm.start_hand()
    positions = [p.position for p in sm.game_state.players]
    all_present = all(pos in positions for pos in expected_positions)
    test_suite.log_test(
        f"Position Tracking ({num_players} players)",
        all_present,
        f"Positions: {positions}",
        {"expected": expected_positions, "actual": positions}
    )
    assert all_present, f"Expected {expected_positions}, got {positions}"

def test_bb_folding_bug_fix(state_machine, test_suite):
    """Test BB checks with weak hand when no raise is made."""
    state_machine.start_hand()
    actions_taken = []
    state_machine.on_log_entry = lambda msg: actions_taken.append(msg)
    bb_player = next(p for p in state_machine.game_state.players if p.position == "BB")
    bb_player.cards = ["7h", "2c"]  # Weak hand
    for i in range(5):
        current_player = state_machine.get_action_player()
        if current_player and current_player.position != "BB":
            state_machine.execute_action(current_player, ActionType.FOLD)
    current_player = state_machine.get_action_player()
    if current_player and current_player.position == "BB":
        state_machine.execute_bot_action(current_player)
    bb_action = next((a for a in actions_taken if "BB" in a and "decided" in a), None)
    test_suite.log_test(
        "BB Checks with Weak Hand",
        bb_action and "CHECK" in bb_action,
        f"BB should check with {bb_player.cards} when no raise",
        {"bb_action": bb_action, "bb_cards": bb_player.cards}
    )
    assert bb_action and "CHECK" in bb_action, f"BB folded instead of checking: {bb_action}"

def test_bb_facing_raise(state_machine, test_suite):
    """Test BB folds to a raise with a weak hand."""
    state_machine.start_hand()
    actions_taken = []
    state_machine.on_log_entry = lambda msg: actions_taken.append(msg)
    bb_player = next(p for p in state_machine.game_state.players if p.position == "BB")
    bb_player.cards = ["7h", "2c"]  # Weak hand
    utg_player = next(p for p in state_machine.game_state.players if p.position == "UTG")
    state_machine.execute_action(utg_player, ActionType.RAISE, 3.0)
    for i in range(4):
        current_player = state_machine.get_action_player()
        if current_player and current_player.position not in ["BB", "UTG"]:
            state_machine.execute_action(current_player, ActionType.FOLD)
    current_player = state_machine.get_action_player()
    if current_player and current_player.position == "BB":
        state_machine.execute_bot_action(current_player)
    bb_action = next((a for a in actions_taken if "BB" in a and "decided" in a), None)
    test_suite.log_test(
        "BB Folds to Raise with Weak Hand",
        bb_action and "FOLD" in bb_action,
        f"BB should fold {bb_player.cards} to a raise",
        {"bb_action": bb_action, "bb_cards": bb_player.cards}
    )
    assert bb_action and "FOLD" in bb_action, f"BB did not fold to raise: {bb_action}"

def test_raise_logic(state_machine, test_suite):
    """Test minimum raise calculation and invalid raise detection."""
    state_machine.start_hand()
    utg_player = state_machine.get_action_player()
    state_machine.execute_action(utg_player, ActionType.RAISE, 3.0)
    expected_min_raise = 2.0  # Raise by 2 (from 1 to 3)
    actual_min_raise = state_machine.game_state.min_raise
    test_suite.log_test(
        "Minimum Raise Calculation",
        actual_min_raise == expected_min_raise,
        f"Min raise after 3BB raise",
        {"expected": expected_min_raise, "actual": actual_min_raise}
    )
    assert actual_min_raise == expected_min_raise, f"Expected min raise {expected_min_raise}, got {actual_min_raise}"
    next_player = state_machine.get_action_player()
    errors = state_machine.validate_action(next_player, ActionType.RAISE, 4.0)
    test_suite.log_test(
        "Invalid Raise Detection",
        len(errors) > 0,
        "Raise to 4.0 when min is 5.0 should fail",
        {"errors": errors}
    )
    assert len(errors) > 0, f"Invalid raise not detected: {errors}"

def test_all_in_tracking(state_machine, test_suite):
    """Test all-in state tracking and partial calls."""
    state_machine.start_hand()
    player = state_machine.get_action_player()
    player.stack = 5.0
    state_machine.game_state.current_bet = 10.0
    state_machine.execute_action(player, ActionType.CALL)
    test_suite.log_test(
        "All-In Partial Call",
        player.is_all_in and player.partial_call_amount == 5.0 and player.full_call_amount == 10.0,
        "Player should be all-in with partial call",
        {"stack": player.stack, "all_in": player.is_all_in, "partial_call": player.partial_call_amount}
    )
    assert player.is_all_in, "Player should be all-in"
    assert player.partial_call_amount == 5.0, f"Expected partial call 5.0, got {player.partial_call_amount}"

def test_side_pots(state_machine, test_suite):
    """Test side pot creation for all-in scenarios."""
    state_machine.start_hand()
    players = state_machine.game_state.players
    players[0].stack = 10.0
    players[0].is_all_in = True
    players[0].total_invested = 10.0
    players[1].stack = 50.0
    players[1].is_all_in = True
    players[1].total_invested = 50.0
    players[2].total_invested = 50.0
    state_machine.game_state.pot = 110.0
    side_pots = state_machine.create_side_pots()
    test_suite.log_test(
        "Side Pot Creation",
        len(side_pots) == 2 and side_pots[0]["amount"] == 30.0 and side_pots[1]["amount"] == 80.0,
        "Should create two side pots: $30 (3 players), $80 (2 players)",
        {"side_pots": [{"amount": p["amount"], "eligible": [e.name for e in p["eligible_players"]]} for p in side_pots]}
    )
    assert len(side_pots) == 2, f"Expected 2 side pots, got {len(side_pots)}"
    assert side_pots[0]["amount"] == 30.0, f"Expected first pot 30.0, got {side_pots[0]['amount']}"
    assert side_pots[1]["amount"] == 80.0, f"Expected second pot 80.0, got {side_pots[1]['amount']}"

def test_strategy_integration_preflop(state_machine, test_suite):
    """Test bot strategy integration for preflop with strong hand."""
    state_machine.start_hand()
    actions_taken = []
    state_machine.on_log_entry = lambda msg: actions_taken.append(msg)
    utg_bot = next(p for p in state_machine.game_state.players if p.position == "UTG")
    utg_bot.cards = ["Ah", "As"]  # Pocket aces
    if state_machine.get_action_player().is_human:
        state_machine.execute_action(state_machine.get_action_player(), ActionType.FOLD)
    current_player = state_machine.get_action_player()
    if current_player and not current_player.is_human:
        state_machine.execute_bot_action(current_player)
    strong_action = any("RAISE" in action or "BET" in action for action in actions_taken if "UTG" in action)
    test_suite.log_test(
        "Bot Preflop Strategy Decision",
        strong_action,
        "Bot should raise/bet with AA",
        {"bot_actions": actions_taken}
    )
    assert strong_action, f"Bot did not raise/bet with AA: {actions_taken}"

def test_strategy_integration_postflop(state_machine, test_suite):
    """Test bot strategy integration for postflop with top pair."""
    state_machine.start_hand()
    state_machine.game_state.street = "flop"
    state_machine.game_state.board = ["Ah", "Kh", "Qh"]  # Flush-heavy board
    player = next(p for p in state_machine.game_state.players if p.position == "UTG")
    player.cards = ["As", "Ks"]  # Top pair
    action, amount = state_machine.get_strategy_action(player)
    test_suite.log_test(
        "Postflop Bet with Top Pair",
        action == ActionType.BET and amount > 0,
        "Should bet with top pair on flop",
        {"action": action.value, "amount": amount}
    )
    assert action == ActionType.BET, f"Expected BET, got {action.value}"
    assert amount > 0, f"Expected positive bet amount, got {amount}"

@pytest.mark.parametrize("action,amount,expected_error", [
    (ActionType.BET, -10, "Amount cannot be negative"),
    (ActionType.CHECK, 0, "Cannot check when bet"),
    (ActionType.BET, 5, "Cannot bet when there's already a bet"),
    (ActionType.CALL, 10, "Call amount must be"),
])
def test_input_validation(state_machine, test_suite, action, amount, expected_error):
    """Test input validation for various invalid actions."""
    state_machine.start_hand()
    player = state_machine.get_action_player()
    state_machine.execute_action(player, ActionType.RAISE, 3.0)
    player = state_machine.get_action_player()
    errors = state_machine.validate_action(player, action, amount)
    has_expected_error = any(expected_error in error for error in errors)
    test_suite.log_test(
        f"Validation: {action.value} ${amount}",
        has_expected_error or len(errors) > 0,
        f"Should detect: {expected_error}",
        {"errors": errors}
    )
    assert has_expected_error or len(errors) > 0, f"Expected error containing '{expected_error}', got {errors}"

def test_invalid_cards(state_machine, test_suite):
    """Test handling of invalid card inputs."""
    state_machine.start_hand()
    state_machine.game_state.deck = ["XX"]  # Invalid card
    with pytest.raises(ValueError, match="Invalid card"):
        state_machine.deal_card()
    player = state_machine.get_action_player()
    player.cards = ["XX", "YY"]
    action, amount = state_machine.get_strategy_action(player)
    test_suite.log_test(
        "Invalid Card Handling",
        action == ActionType.FOLD,
        "Should fold with invalid cards",
        {"cards": player.cards, "action": action.value}
    )
    assert action == ActionType.FOLD, f"Expected FOLD, got {action.value}"

def test_state_transitions(state_machine, test_suite):
    """Test proper state transitions in heads-up scenario."""
    sm = ImprovedPokerStateMachine(num_players=2, strategy_data=test_suite.strategy_data)
    sm.sfx = MockSoundManager()
    states = []
    sm.on_state_change = lambda new_state=None: states.append(new_state.value if new_state else "None")
    sm.start_hand()
    for _ in range(8):
        player = sm.get_action_player()
        if player and sm.current_state != PokerState.END_HAND:
            if sm.game_state.current_bet > player.current_bet:
                sm.execute_action(player, ActionType.CALL)
            else:
                sm.execute_action(player, ActionType.CHECK)
        else:
            break
    expected_sequence = ["preflop_betting", "deal_flop", "flop_betting", "deal_turn", 
                         "turn_betting", "deal_river", "river_betting", "showdown", "end_hand"]
    all_present = all(state in states for state in expected_sequence)
    test_suite.log_test(
        "State Transitions",
        all_present,
        "All states should be visited",
        {"states": states}
    )
    assert all_present, f"Expected states {expected_sequence}, got {states}"

def test_showdown_split_pot(state_machine, test_suite):
    """Test split pot in showdown with identical hands."""
    sm = ImprovedPokerStateMachine(num_players=2, strategy_data=test_suite.strategy_data)
    sm.sfx = MockSoundManager()
    sm.hand_evaluator = MockHandEvaluator()
    sm.start_hand()
    sm.game_state.street = "river"
    sm.game_state.board = ["Ah", "Kh", "Qh", "Jh", "Th"]
    sm.game_state.players[0].cards = ["As", "Kd"]
    sm.game_state.players[1].cards = ["Ac", "Kc"]
    sm.game_state.pot = 20.0
    winners = sm.determine_winner()
    sm.handle_showdown()
    test_suite.log_test(
        "Split Pot in Showdown",
        len(winners) == 2 and all(p.stack == 110.0 for p in winners),
        "Both players should win with identical hands",
        {"winners": [p.name for p in winners], "stacks": [p.stack for p in winners]}
    )
    assert len(winners) == 2, f"Expected 2 winners, got {len(winners)}"
    assert all(p.stack == 110.0 for p in winners), f"Expected stacks 110.0, got {[p.stack for p in winners]}"

def test_hand_eval_cache(state_machine, test_suite):
    """Test hand evaluation cache functionality."""
    state_machine.start_hand()
    state_machine.game_state.board = ["Ah", "Kh", "Qh"]
    player = state_machine.get_action_player()
    player.cards = ["As", "Ks"]
    state_machine.get_postflop_hand_strength(player.cards, state_machine.game_state.board)
    cache_hits_before = state_machine._cache_hits
    state_machine.get_postflop_hand_strength(player.cards, state_machine.game_state.board)
    test_suite.log_test(
        "Hand Evaluation Cache",
        state_machine._cache_hits > cache_hits_before,
        "Cache should register a hit for repeated evaluation",
        {"cache_hits": state_machine._cache_hits, "cache_misses": state_machine._cache_misses}
    )
    assert state_machine._cache_hits > cache_hits_before, "Cache hit not registered"

def test_multi_player_pot(state_machine, test_suite):
    """Test multi-player pot with raises, calls, and folds."""
    state_machine.start_hand()
    actions_taken = []
    state_machine.on_log_entry = lambda msg: actions_taken.append(msg)
    players = state_machine.game_state.players
    state_machine.execute_action(players[0], ActionType.RAISE, 3.0)
    state_machine.execute_action(players[1], ActionType.CALL, 3.0)
    state_machine.execute_action(players[2], ActionType.FOLD, 0.0)
    state_machine.execute_action(players[3], ActionType.CALL, 3.0)
    test_suite.log_test(
        "Multi-Player Pot",
        state_machine.game_state.pot == 9.5,  # SB (0.5) + BB (1.0) + 3 + 3 + 2
        "Pot should reflect contributions from multiple players",
        {"pot": state_machine.game_state.pot, "actions": actions_taken}
    )
    assert state_machine.game_state.pot == 9.5, f"Expected pot 9.5, got {state_machine.game_state.pot}"

def test_sound_integration(state_machine, test_suite):
    """Test sound integration for actions."""
    state_machine.start_hand()
    player = state_machine.get_action_player()
    state_machine.execute_action(player, ActionType.FOLD)
    test_suite.log_test(
        "Sound on Fold",
        state_machine.sfx.last_played in ["player_fold", "card_fold"],
        "Should play fold sound",
        {"last_sound": state_machine.sfx.last_played}
    )
    assert state_machine.sfx.last_played in ["player_fold", "card_fold"], f"Expected fold sound, got {state_machine.sfx.last_played}"

def test_hand_history_logging(state_machine, test_suite):
    """Test structured hand history logging."""
    state_machine.start_hand()
    player = state_machine.get_action_player()
    state_machine.execute_action(player, ActionType.RAISE, 3.0)
    test_suite.log_test(
        "Hand History Logging",
        len(state_machine.hand_history) > 0 and state_machine.hand_history[-1].action == ActionType.RAISE,
        "Should log raise action in hand history",
        {"last_log": vars(state_machine.hand_history[-1])}
    )
    assert len(state_machine.hand_history) > 0, "Hand history empty"
    assert state_machine.hand_history[-1].action == ActionType.RAISE, f"Expected RAISE, got {state_machine.hand_history[-1].action}"

def test_performance(state_machine, test_suite):
    """Test performance of action execution."""
    state_machine.start_hand()
    start_time = time.time()
    for _ in range(100):
        player = state_machine.get_action_player()
        if player:
            state_machine.execute_action(player, ActionType.FOLD)
    duration = time.time() - start_time
    test_suite.log_test(
        "Action Performance",
        duration < 1.5,
        "100 actions should take less than 1.5 seconds",
        {"duration": duration}
    )
    assert duration < 1.5, f"100 actions took {duration} seconds"

def test_no_active_players(state_machine, test_suite):
    """Test behavior when no active players remain."""
    state_machine.start_hand()
    for player in state_machine.game_state.players:
        state_machine.execute_action(player, ActionType.FOLD)
    test_suite.log_test(
        "No Active Players",
        state_machine.current_state == PokerState.END_HAND,
        "Should transition to END_HAND when all players fold",
        {"state": state_machine.current_state.value}
    )
    assert state_machine.current_state == PokerState.END_HAND, f"Expected END_HAND, got {state_machine.current_state.value}"

def test_invalid_state_transition(state_machine, test_suite):
    """Test invalid state transition handling."""
    state_machine.start_hand()
    with pytest.raises(ValueError, match="Invalid state transition"):
        state_machine.transition_to(PokerState.SHOWDOWN)
    test_suite.log_test(
        "Invalid State Transition",
        True,
        "Should raise ValueError for invalid transition",
        {"current_state": state_machine.current_state.value}
    )

def test_winner_determination(state_machine, test_suite):
    """Test winner determination with single winner."""
    state_machine.start_hand()
    state_machine.game_state.street = "river"
    state_machine.game_state.board = ["Ah", "Kh", "Qh", "Jh", "Th"]
    state_machine.game_state.players[0].cards = ["As", "Ks"]  # Flush
    state_machine.game_state.players[1].cards = ["Ad", "Kd"]  # Flush (tie)
    state_machine.game_state.pot = 20.0
    winners = state_machine.determine_winner()
    test_suite.log_test(
        "Winner Determination",
        len(winners) == 2,
        "Should detect tie between two players",
        {"winners": [p.name for p in winners]}
    )
    assert len(winners) == 2, f"Expected 2 winners, got {len(winners)}"

def test_hand_classification(state_machine, test_suite):
    """Test hand classification for postflop."""
    state_machine.start_hand()
    state_machine.game_state.street = "flop"
    state_machine.game_state.board = ["Ah", "Kh", "Qh"]
    player = state_machine.get_action_player()
    player.cards = ["As", "Ks"]
    hand_type = state_machine.classify_hand(player.cards, state_machine.game_state.board)
    test_suite.log_test(
        "Hand Classification",
        hand_type == "top_pair",
        "Should classify AsKs on AhKhQh as top pair",
        {"hand_type": hand_type}
    )
    assert hand_type == "top_pair", f"Expected top_pair, got {hand_type}"

def test_game_info(state_machine, test_suite):
    """Test game info retrieval."""
    state_machine.start_hand()
    game_info = state_machine.get_game_info()
    test_suite.log_test(
        "Game Info",
        game_info.get("state") == "preflop_betting" and len(game_info.get("players", [])) == 6,
        "Should return comprehensive game state",
        {"state": game_info.get("state"), "player_count": len(game_info.get("players", []))}
    )
    assert game_info.get("state") == "preflop_betting", f"Expected preflop_betting, got {game_info.get('state')}"
    assert len(game_info.get("players", [])) == 6, f"Expected 6 players, got {len(game_info.get('players', []))}"

def main():
    """Run the test suite with pytest."""
    print("Starting Poker State Machine Test Suite...")
    pytest.main([__file__, "-v"])
    print("\nTest suite completed.")

if __name__ == "__main__":
    sys.exit(main()) 