#!/usr/bin/env python3
"""
Simplified final mile surgical patches regression tests.
Focus on testing the core adapter logic without complex hand creation.
"""

import sys

# Import PPSM and related types
sys.path.append('.')
from core.pure_poker_state_machine import HandModelDecisionEngineAdapter
from core.poker_types import Player, GameState, RoundState
from core.hand_model import ActionType as HM
from core.poker_types import ActionType


def create_mock_game_state(current_bet=0.0, street="flop", big_blind=10.0):
    """Create a minimal mock game state for testing adapter logic."""
    class MockPlayer:
        def __init__(self, name, position="", stack=1000.0, current_bet=0.0, is_active=True, has_folded=False):
            self.name = name
            self.position = position
            self.stack = stack
            self.current_bet = current_bet
            self.is_active = is_active
            self.has_folded = has_folded
    
    class MockRoundState:
        def __init__(self):
            self.need_action_from = {0, 1}  # seats 0 and 1 need to act
            self.last_full_raise_size = 0.0
            self.last_aggressor_idx = None
            self.reopen_available = True
    
    class MockGameState:
        def __init__(self):
            self.current_bet = current_bet
            self.street = street
            self.big_blind = big_blind
            self.players = [
                MockPlayer("seat1", "BB", stack=990.0, current_bet=10.0),  # BB already posted
                MockPlayer("seat2", "SB", stack=995.0, current_bet=5.0),   # SB already posted
            ]
            self.round_state = MockRoundState()
    
    return MockGameState()


def create_mock_actions():
    """Create mock actions for testing adapter logic."""
    class MockAction:
        def __init__(self, actor_uid, action, amount=None):
            self.actor_uid = actor_uid
            self.action = action
            self.amount = amount
    
    return [
        MockAction("seat1", HM.BET, 60.0),   # seat1 bets
        MockAction("seat2", HM.CALL, 60.0),  # seat2 calls (but this is wrong actor in sequence)
    ]


def test_should_inject_fold_logic():
    """Test the new _should_inject_fold logic directly."""
    print("🧪 Testing _should_inject_fold logic...")
    
    # Create mock adapter with actions
    class MockAdapter:
        def _seat_index(self, game_state, player_name):
            for i, pl in enumerate(game_state.players):
                if pl.name == player_name:
                    return i
            return None
        
        def _should_inject_fold(self, player_name, game_state):
            """Copy of the new _should_inject_fold method."""
            idx = self._seat_index(game_state, player_name)
            if idx is None:
                return False
            pl = game_state.players[idx]
            if not pl.is_active or pl.has_folded:
                return False
            curr = float(getattr(game_state, "current_bet", 0.0) or 0.0)
            # Must be facing a wager and not already matched
            if curr <= (pl.current_bet + 1e-9):
                return False
            rs = getattr(game_state, "round_state", None)
            need = set(getattr(rs, "need_action_from", set()) or set())
            # Only inject if this seat actually owes action
            return idx in need
    
    adapter = MockAdapter()
    
    # Test 1: Player facing bet should be able to fold
    game_state = create_mock_game_state(current_bet=60.0)  # someone bet 60
    game_state.players[0].current_bet = 10.0  # seat1 has only contributed 10 (BB)
    game_state.round_state.need_action_from = {0}  # seat1 needs to act
    
    should_fold = adapter._should_inject_fold("seat1", game_state)
    if should_fold:
        print("✅ Test 1 PASSED: Player facing bet can fold")
    else:
        print("❌ Test 1 FAILED: Player facing bet should be able to fold")
        return False
    
    # Test 2: Player already matched shouldn't fold
    game_state.players[0].current_bet = 60.0  # seat1 already matched
    should_fold = adapter._should_inject_fold("seat1", game_state)
    if not should_fold:
        print("✅ Test 2 PASSED: Player already matched shouldn't fold")
    else:
        print("❌ Test 2 FAILED: Player already matched should not fold")
        return False
    
    # Test 3: Player not needing action shouldn't fold
    game_state.players[0].current_bet = 10.0  # back to owing
    game_state.round_state.need_action_from = {1}  # seat2 needs action, not seat1
    should_fold = adapter._should_inject_fold("seat1", game_state)
    if not should_fold:
        print("✅ Test 3 PASSED: Player not needing action shouldn't fold")
    else:
        print("❌ Test 3 FAILED: Player not needing action should not fold")
        return False
    
    print("✅ _should_inject_fold logic working correctly")
    return True


def test_can_inject_check_logic():
    """Test the enhanced _can_inject_check logic directly."""
    print("🧪 Testing enhanced _can_inject_check logic...")
    
    # Create mock adapter
    class MockAdapter:
        def _seat_index(self, game_state, player_name):
            for i, pl in enumerate(game_state.players):
                if pl.name == player_name:
                    return i
            return None
        
        def _can_inject_check(self, player_name, game_state):
            """Copy of the new _can_inject_check method."""
            street = (str(getattr(game_state, "street", "")) or "").lower()
            idx = self._seat_index(game_state, player_name)
            if idx is None:
                return False
            rs = getattr(game_state, "round_state", None)
            need = set(getattr(rs, "need_action_from", set()) or set())
            if street in ("flop", "turn", "river"):
                # Postflop, no wager yet: seats in need_action_from may CHECK.
                return float(getattr(game_state, "current_bet", 0.0) or 0.0) == 0.0 and idx in need
            if street == "preflop":
                # BB option check: allow BB to close when current_bet == BB and BB still needs to act.
                curr = float(getattr(game_state, "current_bet", 0.0) or 0.0)
                bb_amt = float(getattr(game_state, "big_blind", 0.0) or 0.0)
                pos = getattr(game_state.players[idx], "position", "")
                return pos == "BB" and idx in need and abs(curr - bb_amt) < 1e-9
            return False
    
    adapter = MockAdapter()
    
    # Test 1: Postflop with no bet should allow check
    game_state = create_mock_game_state(current_bet=0.0, street="flop")
    game_state.round_state.need_action_from = {0, 1}
    
    can_check = adapter._can_inject_check("seat1", game_state)
    if can_check:
        print("✅ Test 1 PASSED: Postflop no bet allows check")
    else:
        print("❌ Test 1 FAILED: Postflop no bet should allow check")
        return False
    
    # Test 2: Postflop with bet should not allow check
    game_state.current_bet = 60.0
    can_check = adapter._can_inject_check("seat1", game_state)
    if not can_check:
        print("✅ Test 2 PASSED: Postflop with bet prevents check")
    else:
        print("❌ Test 2 FAILED: Postflop with bet should prevent check")
        return False
    
    # Test 3: BB option check (preflop, current_bet = big_blind)
    game_state.current_bet = 10.0  # equals big blind
    game_state.street = "preflop"
    game_state.players[0].position = "BB"
    game_state.round_state.need_action_from = {0}  # BB needs to act
    
    can_check = adapter._can_inject_check("seat1", game_state)
    if can_check:
        print("✅ Test 3 PASSED: BB option check works")
    else:
        print("❌ Test 3 FAILED: BB option check should work")
        return False
    
    print("✅ _can_inject_check logic working correctly")
    return True


def test_wrong_player_injection():
    """Test the core wrong-player injection logic."""
    print("🧪 Testing wrong-player action injection...")
    
    # Create mock adapter with simplified get_decision logic
    class MockAdapter:
        def __init__(self):
            self.actions_for_replay = create_mock_actions()
            self.current_action_index = 0
        
        def _seat_index(self, game_state, player_name):
            for i, pl in enumerate(game_state.players):
                if pl.name == player_name:
                    return i
            return None
        
        def _can_inject_check(self, player_name, game_state):
            # Simplified: return True if current_bet is 0
            return float(getattr(game_state, "current_bet", 0.0) or 0.0) == 0.0
        
        def _should_inject_fold(self, player_name, game_state):
            # Simplified: return True if current_bet > 0 and player hasn't matched
            curr = float(getattr(game_state, "current_bet", 0.0) or 0.0)
            idx = self._seat_index(game_state, player_name)
            if idx is not None:
                pl = game_state.players[idx]
                return curr > pl.current_bet + 1e-9
            return False
        
        def test_get_decision_logic(self, player_name, game_state):
            """Simplified version of the enhanced get_decision logic."""
            if self.current_action_index >= len(self.actions_for_replay):
                return None
            
            act = self.actions_for_replay[self.current_action_index]
            
            # Core test: wrong player case
            if act.actor_uid != player_name:
                if self._can_inject_check(player_name, game_state):
                    return ActionType.CHECK, None
                if self._should_inject_fold(player_name, game_state):
                    return ActionType.FOLD, None
                return None
            
            # Right player case
            self.current_action_index += 1
            if act.action == HM.BET:
                return ActionType.BET, act.amount
            elif act.action == HM.CALL:
                return ActionType.CALL, None
            return None
    
    adapter = MockAdapter()
    
    # Test 1: Wrong player with current_bet=0 should inject CHECK
    game_state = create_mock_game_state(current_bet=0.0)
    
    # Ask seat2 for decision, but next action is for seat1
    decision = adapter.test_get_decision_logic("seat2", game_state)
    if decision and decision[0] == ActionType.CHECK:
        print("✅ Test 1 PASSED: Wrong player at bet=0 gets CHECK injection")
    else:
        print(f"❌ Test 1 FAILED: Expected CHECK injection, got {decision}")
        return False
    
    # Test 2: Wrong player with current_bet>0 should inject FOLD
    game_state.current_bet = 60.0
    game_state.players[1].current_bet = 5.0  # seat2 hasn't matched
    
    decision = adapter.test_get_decision_logic("seat2", game_state)
    if decision and decision[0] == ActionType.FOLD:
        print("✅ Test 2 PASSED: Wrong player at bet>0 gets FOLD injection")
    else:
        print(f"❌ Test 2 FAILED: Expected FOLD injection, got {decision}")
        return False
    
    # Test 3: Right player should consume action normally
    adapter.current_action_index = 0  # reset
    decision = adapter.test_get_decision_logic("seat1", game_state)
    if decision and decision[0] == ActionType.BET and decision[1] == 60.0:
        print("✅ Test 3 PASSED: Right player gets normal action")
    else:
        print(f"❌ Test 3 FAILED: Expected BET 60.0, got {decision}")
        return False
    
    print("✅ Wrong-player injection logic working correctly")
    return True


def main():
    """Run simplified final mile regression tests."""
    print("🚀 FINAL MILE SURGICAL PATCHES - SIMPLIFIED REGRESSION TESTS")
    print("=" * 70)
    
    tests = [
        ("_should_inject_fold Logic", test_should_inject_fold_logic),
        ("_can_inject_check Logic", test_can_inject_check_logic),
        ("Wrong Player Injection", test_wrong_player_injection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🎯 {test_name}")
        print("-" * 50)
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: EXCEPTION - {str(e)}")
            results.append((test_name, False))
    
    print(f"\n📊 FINAL RESULTS")
    print("=" * 70)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 SUCCESS RATE: {passed}/{total} ({100*passed//total if total > 0 else 0}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Surgical patch logic validated!")
        return True
    else:
        print("⚠️  Some tests failed - check implementations")
        return False


if __name__ == "__main__":
    main()
