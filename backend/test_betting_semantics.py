"""
Comprehensive Betting Semantics Tests for PPSM

Tests for the concrete architecture with:
- Dealer & blinds rotation
- BET vs RAISE semantics 
- Short all-in reopen logic
- Chip conservation
- Pot display accuracy
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.poker_types import Player, PokerState
from core.hand_model import ActionType
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


# === HELPERS: Test DSL ===

def snapshot(ppsm):
    """Get readable snapshot of PPSM state for debugging."""
    gs = ppsm.get_game_info()
    lines = [
        f"hand={gs['hand_number']} street={gs['street']} state={gs['current_state']}",
        f"dealer={gs['dealer_position']} action_idx={gs['action_player_index']}",
        f"pot={gs['pot']} (committed={gs['committed_pot']}, street={gs['street_commit_sum']}) current_bet={gs['current_bet']} board={gs['board']}",
    ]
    for i, p in enumerate(gs["players"]):
        lines.append(
            f"  [{i}] {p['name']} pos={p['position']} stack={p['stack']:.2f} "
            f"bet={p['current_bet']:.2f} folded={p['has_folded']} active={p['is_active']}"
        )
    return "\n".join(lines)


def create_test_ppsm(num_players=3, bb=100, starting_stack=10000):
    """Create PPSM for testing."""
    config = GameConfig(
        num_players=num_players, 
        big_blind=bb, 
        starting_stack=starting_stack
    )
    return PurePokerStateMachine(
        config=config,
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )


def raise_to(ppsm, idx, to_amt):
    """Execute RAISE to specified amount."""
    player = ppsm.game_state.players[idx]
    success = ppsm.execute_action(player, ActionType.RAISE, to_amt)
    assert success, f"raise_to failed:\n{snapshot(ppsm)}"
    return success


def bet_to(ppsm, idx, to_amt):
    """Execute BET to specified amount."""
    player = ppsm.game_state.players[idx]
    success = ppsm.execute_action(player, ActionType.BET, to_amt)
    assert success, f"bet_to failed:\n{snapshot(ppsm)}"
    return success


def call(ppsm, idx):
    """Execute CALL."""
    player = ppsm.game_state.players[idx]
    success = ppsm.execute_action(player, ActionType.CALL, None)
    assert success, f"call failed:\n{snapshot(ppsm)}"
    return success


def check(ppsm, idx):
    """Execute CHECK."""
    player = ppsm.game_state.players[idx]
    success = ppsm.execute_action(player, ActionType.CHECK, None)
    assert success, f"check failed:\n{snapshot(ppsm)}"
    return success


def fold(ppsm, idx):
    """Execute FOLD."""
    player = ppsm.game_state.players[idx]
    success = ppsm.execute_action(player, ActionType.FOLD, None)
    assert success, f"fold failed:\n{snapshot(ppsm)}"
    return success


# === TESTS ===

def test_dealer_and_blinds_rotation_across_hands():
    """Test that dealer/blinds rotate correctly across hands."""
    print("🧪 Testing dealer and blinds rotation")
    
    # Test 3-handed rotation
    p = create_test_ppsm(num_players=3)
    p.start_hand()
    first_positions = (p.dealer_position, p.small_blind_position, p.big_blind_position)
    first_player_positions = [pl.position for pl in p.game_state.players]
    
    p.start_hand()
    second_positions = (p.dealer_position, p.small_blind_position, p.big_blind_position)
    second_player_positions = [pl.position for pl in p.game_state.players]
    
    assert first_positions != second_positions, f"Dealer/blinds did not rotate:\n{first_positions}\n{second_positions}\n{snapshot(p)}"
    assert first_player_positions != second_player_positions, f"Player positions did not change:\n{first_player_positions}\n{second_player_positions}"
    
    # Test heads-up rotation
    p2 = create_test_ppsm(num_players=2)
    p2.start_hand()
    hu_first = (p2.dealer_position, p2.small_blind_position, p2.big_blind_position)
    
    p2.start_hand()
    hu_second = (p2.dealer_position, p2.small_blind_position, p2.big_blind_position)
    
    assert hu_first != hu_second, f"HU rotation failed:\n{hu_first}\n{hu_second}"
    assert hu_second[0] == hu_second[1], "HU dealer should be SB"
    assert (hu_second[0] + 1) % 2 == hu_second[2], "HU BB should be opposite dealer"
    
    print("✅ Dealer and blinds rotation test passed")


def test_bet_vs_raise_semantics_postflop_and_preflop_open_is_raise():
    """Test proper BET vs RAISE semantics."""
    print("🧪 Testing BET vs RAISE semantics")
    
    p = create_test_ppsm(num_players=3)
    p.start_hand()
    
    # Preflop open should be RAISE (not BET) because current_bet = BB from blinds
    opener_idx = p.action_player_index
    opener = p.game_state.players[opener_idx]
    
    bet_allowed = p._is_valid_action(opener, ActionType.BET, 300)
    raise_allowed = p._is_valid_action(opener, ActionType.RAISE, 300)
    
    assert not bet_allowed, f"Preflop BET must not be allowed when current_bet={p.game_state.current_bet}"
    assert raise_allowed, "Preflop open RAISE should be allowed"
    
    # Execute the raise to continue
    raise_to(p, opener_idx, 300)
    
    # Move to flop manually for testing (simulate street end)
    p._end_street()  # Commit preflop bets
    p.game_state.street = "flop"
    p.current_state = PokerState.FLOP_BETTING
    
    # Set first to act postflop
    if p.rules_provider:
        p.action_player_index = p.rules_provider.get_first_to_act_postflop(p.dealer_position, p.game_state.players)
    else:
        p.action_player_index = (p.dealer_position + 1) % len(p.game_state.players)
    
    # On flop with no bet yet -> BET allowed, RAISE disallowed
    actor_idx = p.action_player_index
    actor = p.game_state.players[actor_idx]
    
    can_bet = p._is_valid_action(actor, ActionType.BET, 150)
    can_raise = p._is_valid_action(actor, ActionType.RAISE, 150)
    
    assert can_bet, f"Flop BET should be allowed when current_bet={p.game_state.current_bet}"
    assert not can_raise, f"Flop RAISE should not be allowed when current_bet={p.game_state.current_bet}"
    
    print("✅ BET vs RAISE semantics test passed")


def test_short_allin_does_not_reopen():
    """Test that short all-in doesn't reopen raising."""
    print("🧪 Testing short all-in reopen logic")
    
    p = create_test_ppsm(num_players=3, bb=100, starting_stack=10000)
    
    # Modify one player to have a short stack for all-in scenario
    p.game_state.players[1].stack = 350  # Will make short all-in possible
    
    p.start_hand()
    
    # Preflop: opener raises to 300 (full raise size = 200 over BB)
    opener_idx = p.action_player_index
    raise_to(p, opener_idx, 300)
    
    # Next player (short stack) goes all-in to 350 (raise size = 50, < min full 200)
    short_stack_idx = p.action_player_index
    short_stack = p.game_state.players[short_stack_idx]
    
    # All-in to 350 total
    all_in_amount = short_stack.stack + short_stack.current_bet
    raise_to(p, short_stack_idx, all_in_amount)
    
    # Verify short all-in didn't reopen
    assert not p.game_state.round_state.reopen_available, "Short all-in should not reopen raising"
    
    # Back to opener: cannot re-raise (not reopened), can only call/fold
    opener_player = p.game_state.players[opener_idx]
    
    can_reraise = p._is_valid_action(opener_player, ActionType.RAISE, 600)
    can_call = p._is_valid_action(opener_player, ActionType.CALL, None)
    can_fold = p._is_valid_action(opener_player, ActionType.FOLD, None)
    
    assert not can_reraise, f"Short all-in should not reopen raising:\n{snapshot(p)}"
    assert can_call, "Should be able to call short all-in"
    assert can_fold, "Should be able to fold to short all-in"
    
    print("✅ Short all-in reopen logic test passed")


def test_chip_conservation_invariants():
    """Test that total chips are conserved throughout play."""
    print("🧪 Testing chip conservation")
    
    p = create_test_ppsm(num_players=3, bb=100, starting_stack=10000)
    p.start_hand()
    
    # Calculate initial total
    total_initial = sum(pl.stack for pl in p.game_state.players) + p.game_state.displayed_pot()
    
    # Simple sequence preflop
    opener_idx = p.action_player_index
    raise_to(p, opener_idx, 300)
    
    second_idx = p.action_player_index
    call(p, second_idx)
    
    third_idx = p.action_player_index
    call(p, third_idx)
    
    # Check conservation during betting
    total_during = sum(pl.stack for pl in p.game_state.players) + p.game_state.displayed_pot()
    assert abs(total_during - total_initial) < 1e-6, f"Chip conservation violated during betting:\nInitial: {total_initial}\nDuring: {total_during}\n{snapshot(p)}"
    
    # End street should move to flop and commit street chips properly
    p._end_street()
    
    total_after = sum(pl.stack for pl in p.game_state.players) + p.game_state.displayed_pot()
    assert abs(total_after - total_initial) < 1e-6, f"Chip conservation violated after street end:\nInitial: {total_initial}\nAfter: {total_after}\n{snapshot(p)}"
    
    print("✅ Chip conservation test passed")


def test_displayed_pot_matches_committed_plus_street_commit():
    """Test that displayed pot equals committed pot + street commit sum."""
    print("🧪 Testing pot display accuracy")
    
    p = create_test_ppsm(num_players=3, bb=100, starting_stack=10000)
    p.start_hand()
    
    opener_idx = p.action_player_index
    raise_to(p, opener_idx, 300)
    
    second_idx = p.action_player_index
    call(p, second_idx)
    
    # Check pot calculation
    gs = p.get_game_info()
    expected_pot = gs["committed_pot"] + gs["street_commit_sum"]
    actual_pot = gs["pot"]
    
    assert abs(actual_pot - expected_pot) < 1e-6, f"Pot display mismatch:\nExpected: {expected_pot}\nActual: {actual_pot}\nCommitted: {gs['committed_pot']}\nStreet: {gs['street_commit_sum']}\n{snapshot(p)}"
    
    # After street end, committed should increase, street should reset
    p._end_street()
    
    gs_after = p.get_game_info()
    assert gs_after["committed_pot"] > gs["committed_pot"], "Committed pot should increase after street end"
    assert gs_after["street_commit_sum"] == 0, "Street commit sum should reset to 0 after street end"
    assert abs(gs_after["pot"] - gs_after["committed_pot"]) < 1e-6, "Pot should equal committed pot when street sum is 0"
    
    print("✅ Pot display accuracy test passed")


def test_full_raise_reopens_action():
    """Test that full raises reopen action for previous players."""
    print("🧪 Testing full raise reopen logic")
    
    p = create_test_ppsm(num_players=3, bb=100, starting_stack=10000)
    p.start_hand()
    
    # Preflop: opener raises to 300
    opener_idx = p.action_player_index
    raise_to(p, opener_idx, 300)
    
    # Next player makes full raise to 500 (raise size = 200, equals last full raise)
    second_idx = p.action_player_index
    raise_to(p, second_idx, 500)
    
    # Should reopen action
    assert p.game_state.round_state.reopen_available, "Full raise should reopen action"
    
    # Third player calls
    third_idx = p.action_player_index
    call(p, third_idx)
    
    # Back to opener - should be able to re-raise (action reopened)
    opener_player = p.game_state.players[opener_idx]
    can_reraise = p._is_valid_action(opener_player, ActionType.RAISE, 800)
    
    assert can_reraise, f"Should be able to re-raise after full raise reopened action:\n{snapshot(p)}"
    
    print("✅ Full raise reopen logic test passed")


def test_to_amount_semantics_consistency():
    """Test that to-amount semantics work consistently across all actions."""
    print("🧪 Testing to-amount semantics consistency")
    
    p = create_test_ppsm(num_players=3, bb=100, starting_stack=10000)
    p.start_hand()
    
    # Player starts with some blind commitment
    opener_idx = p.action_player_index
    opener = p.game_state.players[opener_idx]
    initial_bet = opener.current_bet
    initial_stack = opener.stack
    
    # RAISE to 300 means player's total commitment becomes 300
    raise_to(p, opener_idx, 300)
    
    assert opener.current_bet == 300, f"Player bet should be 300, got {opener.current_bet}"
    expected_stack = initial_stack - (300 - initial_bet)
    assert abs(opener.stack - expected_stack) < 1e-6, f"Stack should be {expected_stack}, got {opener.stack}"
    
    # Next player CALL means match current_bet
    second_idx = p.action_player_index
    second = p.game_state.players[second_idx]
    second_initial_bet = second.current_bet
    second_initial_stack = second.stack
    
    call(p, second_idx)
    
    assert second.current_bet == 300, f"Called player bet should be 300, got {second.current_bet}"
    expected_second_stack = second_initial_stack - (300 - second_initial_bet)
    assert abs(second.stack - expected_second_stack) < 1e-6, f"Called player stack should be {expected_second_stack}, got {second.stack}"
    
    print("✅ To-amount semantics consistency test passed")


# === TEST RUNNER ===

def run_betting_semantics_tests():
    """Run all betting semantics tests."""
    print("🔬 BETTING SEMANTICS TESTS FOR CONCRETE PPSM ARCHITECTURE")
    print("=" * 70)
    
    tests = [
        test_dealer_and_blinds_rotation_across_hands,
        test_bet_vs_raise_semantics_postflop_and_preflop_open_is_raise,
        test_short_allin_does_not_reopen,
        test_chip_conservation_invariants,
        test_displayed_pot_matches_committed_plus_street_commit,
        test_full_raise_reopens_action,
        test_to_amount_semantics_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"🎉 BETTING SEMANTICS TESTS COMPLETE")
    print(f"✅ {passed} tests passed")
    print(f"❌ {failed} tests failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Concrete PPSM architecture is working correctly.")
    else:
        print(f"⚠️ {failed} tests failed. Need to fix issues before proceeding.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_betting_semantics_tests()
    sys.exit(0 if success else 1)
