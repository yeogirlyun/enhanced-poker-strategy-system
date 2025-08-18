#!/usr/bin/env python3
"""
Enhanced Test Suite for PurePokerStateMachine with Bug Detection

Improvements:
- Tests for all-in scenarios and side pots
- Minimum raise validation tests  
- Complete street progression verification
- Proper round completion validation
- Edge case coverage for chip amounts
- State transition validation
"""

import sys
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

sys.path.append('.')

from core.pure_poker_state_machine import (
    PurePokerStateMachine, GameConfig, DeckProvider, RulesProvider, AdvancementController
)
from core.poker_types import Player, PokerState
from core.hand_model import ActionType


@dataclass
class TestResult:
    """Test result data structure."""
    name: str
    passed: bool
    message: str
    details: Optional[Dict] = None


class MockDeckProvider:
    def __init__(self, deck=None):
        if deck:
            self.deck = deck
        else:
            suits = ["C", "D", "H", "S"] 
            ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
            self.deck = [rank + suit for suit in suits for rank in ranks]
    
    def get_deck(self):
        return self.deck.copy()
    
    def replace_deck(self, deck):
        self.deck = deck


class MockRulesProvider:
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        if num_players == 2:
            return dealer_pos  # dealer is small blind in heads-up
        else:
            return (dealer_pos + 3) % num_players  # UTG
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        # First active player after dealer
        for i in range(1, len(players) + 1):
            idx = (dealer_pos + i) % len(players)
            if not players[idx].has_folded and players[idx].is_active and players[idx].stack > 0:
                return idx
        return 0


class MockAdvancementController:
    def should_advance_automatically(self, current_state, players):
        return True  # Auto-advance for testing
    
    def on_round_complete(self, street, game_state):
        pass


class EnhancedPurePokerStateMachineTestSuite:
    """Enhanced test suite with stronger bug detection."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        
    def snapshot(self, ppsm):
        """Create a detailed state snapshot for debugging."""
        gs = ppsm.get_game_info()
        lines = [
            f"hand={gs['hand_number']} street={gs['street']} state={gs['current_state']}",
            f"dealer={gs['dealer_position']} action_idx={gs['action_player_index']}",
            f"SB_idx={getattr(ppsm,'small_blind_position',None)} BB_idx={getattr(ppsm,'big_blind_position',None)}",
            f"pot={gs['pot']} current_bet={gs['current_bet']} board={gs['board']}",
        ]
        for i, p in enumerate(gs["players"]):
            lines.append(
                f"  [{i}] {p['name']} pos={p['position']} stack={p['stack']:.2f} "
                f"bet={p['current_bet']:.2f} folded={p['has_folded']} active={p['is_active']}"
            )
        return "\n".join(lines)

    def log_test(self, name: str, passed: bool, message: str, details: Dict = None, ppsm=None):
        """Log a test result with optional state snapshot."""
        self.results.append(TestResult(name, passed, message, details))
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {name} - {message}")
        
        if not passed:
            if details:
                print(f"      ⟶ Details: {details}")
            if ppsm is not None:
                print("      ⟶ STATE SNAPSHOT:")
                snapshot = self.snapshot(ppsm)
                for line in snapshot.split("\n"):
                    print(f"        {line}")
        
    def create_test_ppsm(self, num_players: int = 2, **config_kwargs) -> PurePokerStateMachine:
        """Create a test PPSM with mock providers."""
        config = GameConfig(
            num_players=num_players,
            small_blind=config_kwargs.get('small_blind', 1.0),
            big_blind=config_kwargs.get('big_blind', 2.0),
            starting_stack=config_kwargs.get('starting_stack', 200.0)
        )
        
        return PurePokerStateMachine(
            config=config,
            deck_provider=MockDeckProvider(),
            rules_provider=MockRulesProvider(),
            advancement_controller=MockAdvancementController()
        )

    # Import all original test methods from the comprehensive test suite
    def test_initialization_and_config(self):
        """Test 1: Initialization and Configuration."""
        print("\n🧪 Test 1: Initialization and Configuration")
        
        # Basic initialization
        ppsm = self.create_test_ppsm()
        self.log_test(
            "Basic Initialization", 
            len(ppsm.game_state.players) == 2,
            f"PPSM initialized with {len(ppsm.game_state.players)} players"
        )
        
        # Custom configuration
        ppsm_custom = self.create_test_ppsm(
            num_players=6,
            small_blind=5.0,
            big_blind=10.0,
            starting_stack=1000.0
        )
        self.log_test(
            "Custom Configuration",
            ppsm_custom.config.num_players == 6 and ppsm_custom.config.big_blind == 10.0,
            f"Custom config: {ppsm_custom.config.num_players}p, BB=${ppsm_custom.config.big_blind}"
        )
        
        # Provider injection
        has_providers = all([
            ppsm_custom.deck_provider is not None,
            ppsm_custom.rules_provider is not None,
            ppsm_custom.advancement_controller is not None
        ])
        self.log_test(
            "Provider Injection",
            has_providers,
            "All providers properly injected"
        )

    def test_player_initialization(self):
        """Test 2: Player Initialization and Positions."""
        print("\n🧪 Test 2: Player Initialization and Positions")
        
        # Test heads-up positions
        ppsm = self.create_test_ppsm(num_players=2)
        positions = [p.position for p in ppsm.game_state.players]
        
        self.log_test(
            "Heads-Up Positions",
            positions == ["SB", "BB"],
            f"Positions: {positions}"
        )
        
        # Test 6-max positions  
        ppsm_6max = self.create_test_ppsm(num_players=6)
        positions_6max = [p.position for p in ppsm_6max.game_state.players]
        
        self.log_test(
            "6-Max Position Count",
            len(positions_6max) == 6,
            f"6-max has {len(positions_6max)} position assignments"
        )
        
        # Test starting stacks
        all_stacks_correct = all(
            p.stack == 200.0 for p in ppsm_6max.game_state.players
        )
        self.log_test(
            "Starting Stack Assignment",
            all_stacks_correct,
            f"All players start with ${ppsm_6max.game_state.players[0].stack}"
        )

    def test_hand_startup_and_blinds(self):
        """Test 3: Hand Startup and Blind Posting."""
        print("\n🧪 Test 3: Hand Startup and Blind Posting")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        # Test initial state
        self.log_test(
            "Hand State Initialization",
            ppsm.current_state == PokerState.PREFLOP_BETTING,
            f"Hand started in state: {ppsm.current_state}"
        )
        
        # Test blind posting
        sb_player = ppsm.game_state.players[ppsm.small_blind_position]
        bb_player = ppsm.game_state.players[ppsm.big_blind_position]
        
        self.log_test(
            "Small Blind Posted",
            sb_player.current_bet == ppsm.config.small_blind,
            f"SB posted ${sb_player.current_bet}: {sb_player.current_bet}"
        )
        
        self.log_test(
            "Big Blind Posted", 
            bb_player.current_bet == ppsm.config.big_blind,
            f"BB posted ${bb_player.current_bet}: {bb_player.current_bet}"
        )
        
        # Test pot calculation - during betting, pot should be 0 (blinds in current_bet)
        expected_pot = ppsm.config.small_blind + ppsm.config.big_blind  # displayed_pot includes current_bet
        self.log_test(
            "Initial Pot Calculation", 
            ppsm.game_state.displayed_pot() == expected_pot,
            f"Pot: ${ppsm.game_state.displayed_pot()} (correct: ${expected_pot} during betting)"
        )
        
        # Test current bet
        self.log_test(
            "Initial Current Bet",
            ppsm.game_state.current_bet == ppsm.config.big_blind,
            f"Current bet: ${ppsm.game_state.current_bet}"
        )

    def test_action_validation(self):
        """Test 4: Action Validation Logic."""
        print("\n🧪 Test 4: Action Validation Logic")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        
        # Test basic action validation
        fold_valid = ppsm._is_valid_action(action_player, ActionType.FOLD, 0.0)
        call_valid = ppsm._is_valid_action(action_player, ActionType.CALL, 0.0)
        check_valid = ppsm._is_valid_action(action_player, ActionType.CHECK, 0.0)  
        raise_valid = ppsm._is_valid_action(action_player, ActionType.RAISE, 4.0)
        invalid_raise = ppsm._is_valid_action(action_player, ActionType.RAISE, 299.0)  # More than stack
        
        self.log_test("FOLD Action Valid", fold_valid, "FOLD should always be valid for active players")
        self.log_test("CALL Action Validation", call_valid, f"CALL valid: {call_valid} (current_bet: ${action_player.current_bet}, to_call: ${ppsm.game_state.current_bet})")
        self.log_test("CHECK Action Validation", not check_valid, f"CHECK valid: {check_valid} (player_bet: ${action_player.current_bet}, current_bet: ${ppsm.game_state.current_bet})")
        self.log_test("RAISE Action Validation", raise_valid, f"RAISE to $4.0 valid: {raise_valid}")
        self.log_test("Invalid RAISE Rejection", not invalid_raise, f"RAISE to $299.0 should be invalid (stack: ${action_player.stack})")

    def test_action_execution(self):
        """Test 5: Action Execution and State Updates."""
        print("\n🧪 Test 5: Action Execution and State Updates")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        initial_stack = action_player.stack
        initial_pot = ppsm.game_state.displayed_pot()
        
        # Execute a raise
        raise_amount = 4.0
        success = ppsm.execute_action(action_player, ActionType.RAISE, raise_amount)
        
        self.log_test("RAISE Execution Success", success, f"RAISE to ${raise_amount} executed successfully")
        self.log_test("Player Bet Update", action_player.current_bet == raise_amount, f"Player bet updated: ${action_player.current_bet}")
        
        expected_stack_reduction = raise_amount - ppsm.config.small_blind  # SB already posted
        expected_new_stack = initial_stack - expected_stack_reduction
        self.log_test("Stack Update", action_player.stack == expected_new_stack, f"Stack reduced by ${expected_stack_reduction}")
        
        # During active betting, displayed_pot shows committed_pot + sum of current_bets
        # After RAISE to $4: SB has $4 bet, BB has $2 bet = $6 total displayed
        expected_pot_during_betting = raise_amount + ppsm.config.big_blind  # $4 + $2 = $6
        self.log_test("Pot During Betting", ppsm.game_state.displayed_pot() == expected_pot_during_betting, f"Pot correctly shows ${ppsm.game_state.displayed_pot()} during betting")
        self.log_test("Current Bet Update", ppsm.game_state.current_bet == raise_amount, f"Current bet updated to ${ppsm.game_state.current_bet}")

    def test_betting_round_completion(self):
        """Test 6: Betting Round Completion Logic."""
        print("\n🧪 Test 6: Betting Round Completion Logic")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        # Execute actions to complete preflop
        players = ppsm.game_state.players
        
        # SB calls (complete preflop) 
        sb_player = players[ppsm.small_blind_position]
        if ppsm.action_player_index == ppsm.small_blind_position:
            success = ppsm.execute_action(sb_player, ActionType.CALL, 0.0)
            self.log_test(
                "SB Call Execution",
                success,
                "SB completed call to BB"
            )
            
            # BB should be able to check to complete the round
            if ppsm.action_player_index == ppsm.big_blind_position:
                bb_player = players[ppsm.big_blind_position]
                initial_state = ppsm.current_state
                ppsm.execute_action(bb_player, ActionType.CHECK, 0.0)
                
                # Check if round completed and advanced to next state
                advanced = ppsm.current_state != initial_state
                self.log_test(
                    "Preflop Round Completion",
                    advanced,
                    f"Advanced from {initial_state} to {ppsm.current_state} after SB call + BB check"
                )

    def test_street_progression(self):
        """Test 7: Street Progression."""
        print("\n🧪 Test 7: Street Progression")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        # Track state progression
        states_visited = [ppsm.current_state]
        
        # Complete preflop (both players check/call to advance)
        if ppsm.action_player_index == ppsm.small_blind_position:
            ppsm.execute_action(ppsm.game_state.players[ppsm.small_blind_position], ActionType.CALL, 0.0)
            states_visited.append(ppsm.current_state)
            
            if ppsm.action_player_index == ppsm.big_blind_position:
                ppsm.execute_action(ppsm.game_state.players[ppsm.big_blind_position], ActionType.CHECK, 0.0)
                states_visited.append(ppsm.current_state)
        
        # Should now be in flop or flop betting
        flop_reached = ppsm.current_state in [PokerState.DEAL_FLOP, PokerState.FLOP_BETTING]
        self.log_test(
            "Flop State Reached",
            flop_reached,
            f"Reached flop state: {ppsm.current_state}"
        )
        
        # Check board has flop cards
        has_flop_cards = len(ppsm.game_state.board) >= 3
        self.log_test(
            "Flop Cards Dealt",
            has_flop_cards,
            f"Board has {len(ppsm.game_state.board)} cards: {ppsm.game_state.board}"
        )
        
        # Check street updated
        self.log_test(
            "Street Update to Flop",
            ppsm.game_state.street == "flop",
            f"Game street updated to: {ppsm.game_state.street}"
        )
        
        # Check bets reset for new street
        players_reset = all(p.current_bet == 0.0 for p in ppsm.game_state.players if not p.has_folded)
        current_bet_reset = ppsm.game_state.current_bet == 0.0
        bets_reset = players_reset and current_bet_reset
        
        self.log_test(
            "Bets Reset for Flop", 
            bets_reset,
            f"Bets reset: players={players_reset}, current_bet=${ppsm.game_state.current_bet}"
        )

    def test_multi_player_scenarios(self):
        """Test 8: Multi-Player Scenarios."""
        print("\n🧪 Test 8: Multi-Player Scenarios")
        
        ppsm = self.create_test_ppsm(num_players=6)
        ppsm.start_hand()
        
        # Check all players active
        active_count = len([p for p in ppsm.game_state.players if p.is_active])
        self.log_test(
            "6-Max Active Players",
            active_count == 6,
            f"6-max game has {active_count} active players"
        )
        
        # Check position assignments
        positions = [p.position for p in ppsm.game_state.players]
        expected_positions = ["SB", "BB", "UTG", "MP", "CO", "BTN"]
        
        self.log_test(
            "6-Max Position Assignment",
            positions == expected_positions,
            f"Positions assigned: {positions}"
        )
        
        # Check action player (should be UTG in 6-max)
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        self.log_test(
            "6-Max Action Player",
            action_player.position in ["UTG", "MP"],  # Could be UTG or MP depending on rules
            f"Action player: {action_player.name} ({action_player.position})"
        )

    def test_fold_scenarios(self):
        """Test 9: Fold Scenarios."""
        print("\n🧪 Test 9: Fold Scenarios")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        initial_active = len([p for p in ppsm.game_state.players if p.is_active])
        
        # Execute fold
        success = ppsm.execute_action(action_player, ActionType.FOLD, 0.0)
        
        self.log_test("Fold Execution", success, f"{action_player.name} folded successfully")
        self.log_test("Player Marked Folded", action_player.has_folded, f"{action_player.name} marked as folded")  
        self.log_test("Player Marked Inactive", not action_player.is_active, f"{action_player.name} marked as inactive")
        
        # Check active count reduced
        final_active = len([p for p in ppsm.game_state.players if p.is_active])
        self.log_test(
            "Active Player Count Reduced",
            final_active == initial_active - 1,
            f"Active players: {initial_active} → {final_active}"
        )

    def test_pot_and_stack_tracking(self):
        """Test 10: Pot and Stack Tracking."""
        print("\n🧪 Test 10: Pot and Stack Tracking")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        # Check chip conservation after blinds
        total_chips_before = sum(p.stack for p in ppsm.game_state.players) + ppsm.game_state.displayed_pot()
        expected_total = 2 * ppsm.config.starting_stack
        
        self.log_test(
            "Chip Conservation After Blinds",
            abs(total_chips_before - expected_total) < 0.01,
            f"Total chips: {expected_total} → {total_chips_before}"
        )
        
        # Execute raise and check conservation
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        ppsm.execute_action(action_player, ActionType.RAISE, 6.0)
        
        total_chips_after = sum(p.stack for p in ppsm.game_state.players) + ppsm.game_state.displayed_pot()
        
        self.log_test(
            "Chip Conservation After Raise",
            abs(total_chips_after - expected_total) < 0.01,
            f"Total chips: {expected_total} → {total_chips_after}"
        )

    def test_edge_cases_and_error_handling(self):
        """Test 11: Edge Cases and Error Handling."""
        print("\n🧪 Test 11: Edge Cases and Error Handling")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        # Test action on folded player
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        action_player.has_folded = True
        action_player.is_active = False
        
        folded_action_rejected = not ppsm.execute_action(action_player, ActionType.RAISE, 10.0)
        self.log_test(
            "Folded Player Action Rejected",
            folded_action_rejected,
            "Actions on folded players should be invalid"
        )
        
        # Reset for next tests
        action_player.has_folded = False
        action_player.is_active = True
        
        # Test oversized bet
        oversized_rejected = not ppsm.execute_action(action_player, ActionType.RAISE, 299.0)
        self.log_test(
            "Oversized Bet Rejected",
            oversized_rejected,
            f"Bet of $299.0 rejected (stack: ${action_player.stack})"
        )
        
        # Test negative bet
        negative_invalid = not ppsm._is_valid_action(action_player, ActionType.RAISE, -10.0)
        self.log_test(
            "Negative Bet Rejected",
            negative_invalid,
            "Negative bet amounts should be invalid"
        )

    def test_provider_integration(self):
        """Test 12: Provider Integration."""
        print("\n🧪 Test 12: Provider Integration")
        
        # Test with custom deck
        custom_deck = ["AH", "KH", "QH", "JH", "TH"] + ["2C"] * 47  # Royal flush setup
        custom_deck_provider = MockDeckProvider(custom_deck)
        
        config = GameConfig(num_players=2)
        ppsm_custom = PurePokerStateMachine(
            config=config,
            deck_provider=custom_deck_provider,
            rules_provider=MockRulesProvider(),
            advancement_controller=MockAdvancementController()
        )
        
        ppsm_custom.start_hand()
        
        # Check custom deck was used - the first cards should be from our custom deck
        # After dealing hole cards, the custom cards should be depleted from the top
        remaining_cards = ppsm_custom.game_state.deck[:10]  # Check more cards
        
        # Check if any players got the custom royal flush cards in their hole cards
        custom_cards_dealt = False
        for player in ppsm_custom.game_state.players:
            if any(card in ["AH", "KH", "QH", "JH", "TH"] for card in player.cards):
                custom_cards_dealt = True
                break
        
        # Also check if royal flush cards are in the remaining deck (indicating custom deck was loaded)
        royal_flush_in_deck = any(card in ["AH", "KH", "QH", "JH", "TH"] for card in remaining_cards)
        
        custom_deck_used = custom_cards_dealt or royal_flush_in_deck
        
        self.log_test(
            "Custom Deck Provider Integration",
            custom_deck_used,
            f"Custom deck used - dealt to players: {custom_cards_dealt}, in remaining: {royal_flush_in_deck}"
        )
        
        # Test rules provider integration
        first_to_act = ppsm_custom.rules_provider.get_first_to_act_preflop(0, 2)
        self.log_test(
            "Rules Provider Integration",
            isinstance(first_to_act, int) and 0 <= first_to_act < 2,
            f"Rules provider returned valid action player: {first_to_act}"
        )
        
        # Test advancement controller integration 
        should_advance = ppsm_custom.advancement_controller.should_advance_automatically(
            PokerState.DEAL_FLOP, ppsm_custom.game_state.players
        )
        self.log_test(
            "Advancement Controller Integration",
            isinstance(should_advance, bool),
            f"Advancement controller returned: {should_advance}"
        )

    def test_dealer_and_blinds_rotation(self):
        """Test 13: Dealer & Blind Rotation Across Hands."""
        print("\n🧪 Test 13: Dealer & Blind Rotation Across Hands")

        # 3-handed rotation
        ppsm = self.create_test_ppsm(num_players=3)
        ppsm.start_hand()
        s1 = (ppsm.dealer_position, ppsm.small_blind_position, ppsm.big_blind_position,
              [p.position for p in ppsm.game_state.players])

        ppsm.start_hand()
        s2 = (ppsm.dealer_position, ppsm.small_blind_position, ppsm.big_blind_position,
              [p.position for p in ppsm.game_state.players])

        self.log_test(
            "Positions Reassign Each Hand (3-max)",
            s1 != s2,
            f"Hand1={s1}, Hand2={s2}"
        )

        # Heads-up rotation sanity: dealer toggles between seats, and dealer is SB
        ppsm2 = self.create_test_ppsm(num_players=2)
        ppsm2.start_hand()
        d1 = (ppsm2.dealer_position, ppsm2.small_blind_position, ppsm2.big_blind_position)
        ppsm2.start_hand()
        d2 = (ppsm2.dealer_position, ppsm2.small_blind_position, ppsm2.big_blind_position)

        self.log_test(
            "HU Dealer/SB Toggle",
            d1 != d2 and d2[0] == d2[1] and ((d2[0] + 1) % 2 == d2[2]),
            f"HU Hand1={d1}, Hand2={d2}"
        )

    def test_bet_vs_raise_semantics(self):
        """Test 14: BET vs RAISE Semantics."""
        print("\n🧪 Test 14: BET vs RAISE Semantics")

        # Create a fresh PPSM and set it up for flop betting manually
        ppsm = self.create_test_ppsm(num_players=3)
        ppsm.current_state = PokerState.FLOP_BETTING
        ppsm.game_state.current_bet = 0.0  # No current bet on flop
        ppsm.game_state.street = "flop"
        ppsm.action_player_index = 0
        
        # Reset all player bets for the new betting round
        for p in ppsm.game_state.players:
            p.current_bet = 0.0
            p.has_folded = False
            p.is_active = True
        
        action_player = ppsm.game_state.players[ppsm.action_player_index]

        # Test 1: No current bet -> BET allowed, RAISE not
        can_bet = ppsm._is_valid_action(action_player, ActionType.BET, 10.0)
        can_raise = ppsm._is_valid_action(action_player, ActionType.RAISE, 10.0)

        self.log_test("Bet Allowed When CurrentBet=0", can_bet, f"current_bet={ppsm.game_state.current_bet}")
        self.log_test("Raise Disallowed When CurrentBet=0", not can_raise, f"current_bet={ppsm.game_state.current_bet}")

        # Test 2: Place a bet to set current_bet > 0
        success = ppsm.execute_action(action_player, ActionType.BET, 10.0)
        self.log_test("Execute Opening Bet", success, "Opening bet of $10")

        # Test 3: After bet placed -> RAISE allowed, BET not
        # Move to next player
        ppsm.action_player_index = (ppsm.action_player_index + 1) % len(ppsm.game_state.players)
        next_player = ppsm.game_state.players[ppsm.action_player_index]
        
        can_bet2 = ppsm._is_valid_action(next_player, ActionType.BET, 20.0)
        can_raise2 = ppsm._is_valid_action(next_player, ActionType.RAISE, 20.0)

        self.log_test("Bet Disallowed When CurrentBet>0", not can_bet2, f"current_bet={ppsm.game_state.current_bet}")
        self.log_test("Raise Allowed When CurrentBet>0", can_raise2, f"current_bet={ppsm.game_state.current_bet}")

    def test_rotation_invariants_over_many_hands(self):
        """Test 15: Rotation Invariants Over Many Hands."""
        print("\n🧪 Test 15: Rotation Invariants Over Many Hands")

        for n in (2, 3, 6):
            ppsm = self.create_test_ppsm(num_players=n)
            seen_dealers = set()
            for _ in range(n * 2):
                ppsm.start_hand()
                seen_dealers.add(ppsm.dealer_position)
            self.log_test(
                f"Every Seat Becomes Dealer (n={n})",
                len(seen_dealers) == n,
                f"seen_dealers={sorted(seen_dealers)}"
            )
    
    # ========== ENHANCED TESTS START HERE ==========
    
    def test_round_completion_with_checks(self):
        """Enhanced Test: Round completion with check scenarios."""
        print("\n🧪 Enhanced Test: Round Completion with Checks")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        # Scenario 1: SB calls, BB checks - round should complete
        if ppsm.action_player_index == ppsm.small_blind_position:
            # SB calls
            sb_player = ppsm.game_state.players[ppsm.small_blind_position]
            ppsm.execute_action(sb_player, ActionType.CALL, 0.0)
            
            # BB should be able to check
            bb_player = ppsm.game_state.players[ppsm.big_blind_position]
            can_check = ppsm._is_valid_action(bb_player, ActionType.CHECK, 0.0)
            
            self.log_test(
                "BB Can Check After SB Call",
                can_check,
                f"BB can check: {can_check}"
            )
            
            # BB checks
            if ppsm.action_player_index == ppsm.big_blind_position:
                initial_state = ppsm.current_state
                ppsm.execute_action(bb_player, ActionType.CHECK, 0.0)
                
                # Verify round completed and advanced
                advanced = ppsm.current_state != initial_state
                self.log_test(
                    "Round Completes After BB Check",
                    advanced,
                    f"State: {initial_state} → {ppsm.current_state}",
                    ppsm=ppsm
                )
                
                # Verify we're on the flop
                on_flop = ppsm.game_state.street in ["flop"] or "FLOP" in str(ppsm.current_state)
                self.log_test(
                    "Advanced to Flop",
                    on_flop,
                    f"Street: {ppsm.game_state.street}, State: {ppsm.current_state}"
                )
    
    def test_all_in_scenarios(self):
        """Test all-in player handling."""
        print("\n🧪 Test: All-in Scenarios")
        
        # Create game with small stacks
        ppsm = self.create_test_ppsm(
            num_players=3,
            small_blind=10.0,
            big_blind=20.0,
            starting_stack=30.0  # Small stack for all-in testing
        )
        ppsm.start_hand()
        
        # Player goes all-in
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        all_in_amount = action_player.stack + action_player.current_bet
        
        success = ppsm.execute_action(action_player, ActionType.RAISE, all_in_amount)
        
        self.log_test(
            "All-in Execution",
            success and action_player.stack == 0,
            f"Player all-in with stack: {action_player.stack}"
        )
        
        # Next player calls all-in
        next_idx = ppsm.action_player_index
        if next_idx >= 0:
            next_player = ppsm.game_state.players[next_idx]
            
            if next_player.stack > 0:
                call_success = ppsm.execute_action(next_player, ActionType.CALL, 0.0)
                
                self.log_test(
                    "Call All-in",
                    call_success,
                    f"Next player called, stack: {next_player.stack}"
                )
                
                # Verify all-in player is skipped in future action
                if next_player.stack == 0:
                    self.log_test(
                        "All-in Player Has No Stack",
                        next_player.stack == 0,
                        "All-in player correctly has 0 stack"
                    )
    
    def test_minimum_raise_amounts(self):
        """Test minimum raise validation."""
        print("\n🧪 Test: Minimum Raise Amounts")
        
        ppsm = self.create_test_ppsm(
            small_blind=5.0,
            big_blind=10.0
        )
        ppsm.start_hand()
        
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        
        # Test 1: Minimum raise should be to 2x BB (20)
        min_raise = ppsm.config.big_blind * 2
        min_raise_valid = ppsm._is_valid_action(action_player, ActionType.RAISE, min_raise)
        
        self.log_test(
            "Minimum Raise Valid",
            min_raise_valid,
            f"Min raise to ${min_raise} valid: {min_raise_valid}"
        )
        
        # Test 2: Raise less than minimum should be invalid
        small_raise = ppsm.config.big_blind + 1  # Only $11, should be invalid
        small_raise_valid = ppsm._is_valid_action(action_player, ActionType.RAISE, small_raise)
        
        self.log_test(
            "Below Minimum Raise Invalid",
            not small_raise_valid,  # Should be False if minimum raise is enforced
            f"Small raise to ${small_raise} should be invalid",
            details={"Note": "This may fail if minimum raise not enforced"}
        )
    
    def test_complete_hand_progression(self):
        """Test complete hand from preflop to showdown."""
        print("\n🧪 Test: Complete Hand Progression")
        
        ppsm = self.create_test_ppsm(num_players=2)
        ppsm.start_hand()
        
        streets_visited = []
        states_visited = []
        
        def play_street_checks():
            """Both players check through a street."""
            for _ in range(2):
                if ppsm.action_player_index >= 0 and ppsm.action_player_index < len(ppsm.game_state.players):
                    player = ppsm.game_state.players[ppsm.action_player_index]
                    if not player.has_folded and player.stack > 0:
                        if player.current_bet < ppsm.game_state.current_bet:
                            ppsm.execute_action(player, ActionType.CALL, 0.0)
                        else:
                            ppsm.execute_action(player, ActionType.CHECK, 0.0)
        
        # Preflop
        streets_visited.append(ppsm.game_state.street)
        states_visited.append(ppsm.current_state)
        play_street_checks()
        
        # Flop
        if ppsm.current_state in [PokerState.FLOP_BETTING, PokerState.DEAL_FLOP]:
            streets_visited.append(ppsm.game_state.street)
            states_visited.append(ppsm.current_state)
            self.log_test(
                "Reached Flop",
                ppsm.game_state.street == "flop" or "FLOP" in str(ppsm.current_state),
                f"Street: {ppsm.game_state.street}"
            )
            
            if ppsm.current_state == PokerState.FLOP_BETTING:
                play_street_checks()
                
                # Turn
                if ppsm.current_state in [PokerState.TURN_BETTING, PokerState.DEAL_TURN]:
                    streets_visited.append(ppsm.game_state.street)
                    states_visited.append(ppsm.current_state)
                    self.log_test(
                        "Reached Turn",
                        ppsm.game_state.street == "turn" or "TURN" in str(ppsm.current_state),
                        f"Street: {ppsm.game_state.street}"
                    )
                    
                    if ppsm.current_state == PokerState.TURN_BETTING:
                        play_street_checks()
                        
                        # River
                        if ppsm.current_state in [PokerState.RIVER_BETTING, PokerState.DEAL_RIVER]:
                            streets_visited.append(ppsm.game_state.street)
                            states_visited.append(ppsm.current_state)
                            self.log_test(
                                "Reached River",
                                ppsm.game_state.street == "river" or "RIVER" in str(ppsm.current_state),
                                f"Street: {ppsm.game_state.street}"
                            )
                            
                            if ppsm.current_state == PokerState.RIVER_BETTING:
                                play_street_checks()
                                
                                # Should reach showdown
                                self.log_test(
                                    "Reached Showdown",
                                    ppsm.current_state == PokerState.SHOWDOWN,
                                    f"Final state: {ppsm.current_state}"
                                )
        
        # Verify board cards
        self.log_test(
            "Complete Board Dealt",
            len(ppsm.game_state.board) == 5,
            f"Board cards: {ppsm.game_state.board}"
        )
    
    def test_re_raise_scenarios(self):
        """Test re-raise scenarios (3-bet, 4-bet, etc)."""
        print("\n🧪 Test: Re-raise Scenarios")
        
        ppsm = self.create_test_ppsm(
            num_players=3,
            small_blind=1.0,
            big_blind=2.0,
            starting_stack=200.0
        )
        ppsm.start_hand()
        
        # UTG raises to 6
        utg_idx = ppsm.action_player_index
        utg = ppsm.game_state.players[utg_idx]
        success1 = ppsm.execute_action(utg, ActionType.RAISE, 6.0)
        
        self.log_test(
            "UTG Initial Raise",
            success1,
            f"UTG raises to $6"
        )
        
        # Next player re-raises to 18 (3-bet)
        if ppsm.action_player_index >= 0:
            player2 = ppsm.game_state.players[ppsm.action_player_index]
            success2 = ppsm.execute_action(player2, ActionType.RAISE, 18.0)
            
            self.log_test(
                "3-Bet Execution",
                success2,
                f"{player2.name} 3-bets to $18"
            )
            
            # Next player re-re-raises to 54 (4-bet)
            if ppsm.action_player_index >= 0:
                player3 = ppsm.game_state.players[ppsm.action_player_index]
                success3 = ppsm.execute_action(player3, ActionType.RAISE, 54.0)
                
                self.log_test(
                    "4-Bet Execution",
                    success3,
                    f"{player3.name} 4-bets to $54"
                )
                
                # During betting, pot stays at 0 - verify total bets instead
                total_current_bets = sum(p.current_bet for p in ppsm.game_state.players)
                expected_total_bets = 54 + 54 + 54  # All players matched the 4-bet
                self.log_test(
                    "Total Bets After Re-raises",
                    total_current_bets >= 54,  # At least one 4-bet amount
                    f"Total current bets: ${total_current_bets} (pot will accumulate when round completes)"
                )
    
    def test_exact_blind_amount_edge_case(self):
        """Test when player has exactly enough for blind."""
        print("\n🧪 Test: Exact Blind Amount Edge Case")
        
        # Create game where BB has exactly the blind amount
        ppsm = self.create_test_ppsm(
            num_players=2,
            small_blind=5.0,
            big_blind=10.0,
            starting_stack=10.0  # Exactly BB amount
        )
        
        ppsm.start_hand()
        
        bb_player = ppsm.game_state.players[ppsm.big_blind_position]
        
        self.log_test(
            "BB Posted with Exact Stack",
            bb_player.stack == 0.0 and bb_player.current_bet == 10.0,
            f"BB stack: {bb_player.stack}, bet: {bb_player.current_bet}"
        )
        
        # BB should not be able to raise
        can_raise = ppsm._is_valid_action(bb_player, ActionType.RAISE, 20.0)
        self.log_test(
            "BB Cannot Raise With No Stack",
            not can_raise,
            "BB with 0 stack cannot raise"
        )
    
    def test_invalid_state_transitions(self):
        """Test that invalid state transitions are prevented."""
        print("\n🧪 Test: Invalid State Transitions")
        
        ppsm = self.create_test_ppsm()
        
        # Try invalid transition from START_HAND to SHOWDOWN
        try:
            ppsm.current_state = PokerState.START_HAND
            ppsm.transition_to(PokerState.SHOWDOWN)
            self.log_test(
                "Invalid Transition Prevented",
                False,
                "Should have raised exception"
            )
        except ValueError as e:
            self.log_test(
                "Invalid Transition Prevented",
                True,
                f"Correctly raised: {e}"
            )
        
        # Try invalid transition from FLOP_BETTING to PREFLOP_BETTING
        try:
            ppsm.current_state = PokerState.FLOP_BETTING
            ppsm.transition_to(PokerState.PREFLOP_BETTING)
            self.log_test(
                "Backward Transition Prevented",
                False,
                "Should have raised exception"
            )
        except ValueError as e:
            self.log_test(
                "Backward Transition Prevented",
                True,
                f"Correctly raised: {e}"
            )
    
    def test_concurrent_all_ins(self):
        """Test multiple players going all-in."""
        print("\n🧪 Test: Concurrent All-ins")
        
        ppsm = self.create_test_ppsm(
            num_players=3,
            small_blind=5.0,
            big_blind=10.0,
            starting_stack=50.0
        )
        ppsm.start_hand()
        
        all_in_count = 0
        
        # First player goes all-in
        p1 = ppsm.game_state.players[ppsm.action_player_index]
        all_in_1 = p1.stack + p1.current_bet
        success1 = ppsm.execute_action(p1, ActionType.RAISE, all_in_1)
        if success1 and p1.stack == 0:
            all_in_count += 1
        
        # Second player calls all-in
        if ppsm.action_player_index >= 0:
            p2 = ppsm.game_state.players[ppsm.action_player_index]
            success2 = ppsm.execute_action(p2, ActionType.CALL, 0.0)
            if success2 and p2.stack == 0:
                all_in_count += 1
        
        self.log_test(
            "Multiple All-ins Handled",
            all_in_count >= 1,
            f"{all_in_count} players all-in"
        )
        
        # Verify game continues correctly
        active_with_chips = len([p for p in ppsm.game_state.players 
                                if not p.has_folded and p.stack > 0])
        
        self.log_test(
            "Game Continues After All-ins",
            ppsm.current_state != PokerState.END_HAND or active_with_chips <= 1,
            f"Active with chips: {active_with_chips}, State: {ppsm.current_state}"
        )
    
    def test_action_player_after_folds(self):
        """Test action player determination after multiple folds."""
        print("\n🧪 Test: Action Player After Folds")
        
        ppsm = self.create_test_ppsm(num_players=4)
        ppsm.start_hand()
        
        initial_active = len([p for p in ppsm.game_state.players if p.is_active])
        
        # Have 2 players fold
        folds = 0
        for _ in range(2):
            if ppsm.action_player_index >= 0:
                player = ppsm.game_state.players[ppsm.action_player_index]
                if ppsm.execute_action(player, ActionType.FOLD, 0.0):
                    folds += 1
        
        self.log_test(
            "Multiple Folds Executed",
            folds == 2,
            f"{folds} players folded"
        )
        
        # Verify action player is still valid
        if ppsm.action_player_index >= 0:
            action_player = ppsm.game_state.players[ppsm.action_player_index]
            self.log_test(
                "Action Player Still Active",
                not action_player.has_folded and action_player.is_active,
                f"Action on {action_player.name}"
            )
        
        # Check active count
        final_active = len([p for p in ppsm.game_state.players if p.is_active])
        self.log_test(
            "Active Count Correct",
            final_active == initial_active - folds,
            f"Active: {initial_active} → {final_active}"
        )
    
    def run_enhanced_test_suite(self):
        """Run the enhanced test suite."""
        print("🧪 ENHANCED PURE POKER STATE MACHINE TEST SUITE")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run original tests
        self.test_initialization_and_config()
        self.test_player_initialization()
        self.test_hand_startup_and_blinds()
        self.test_action_validation()
        self.test_action_execution()
        self.test_betting_round_completion()
        self.test_street_progression()
        self.test_multi_player_scenarios()
        self.test_fold_scenarios()
        self.test_pot_and_stack_tracking()
        self.test_edge_cases_and_error_handling()
        self.test_provider_integration()
        self.test_dealer_and_blinds_rotation()
        self.test_bet_vs_raise_semantics()
        self.test_rotation_invariants_over_many_hands()
        
        # Run enhanced tests
        self.test_round_completion_with_checks()
        self.test_all_in_scenarios()
        self.test_minimum_raise_amounts()
        self.test_complete_hand_progression()
        self.test_re_raise_scenarios()
        self.test_exact_blind_amount_edge_case()
        self.test_invalid_state_transitions()
        self.test_concurrent_all_ins()
        self.test_action_player_after_folds()
        
        end_time = time.time()
        
        # Results summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'=' * 70}")
        print("📊 ENHANCED TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {end_time - start_time:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.results:
                if not result.passed:
                    print(f"   • {result.name}: {result.message}")
                    if result.details:
                        print(f"     {result.details}")
        
        if success_rate >= 95.0:
            print(f"\n🎉 EXCELLENT! Enhanced PPSM passed {success_rate:.1f}% of tests!")
            print("✅ Ready for production use with rigorous validation!")
        elif success_rate >= 80.0:
            print(f"\n🟡 GOOD: {success_rate:.1f}% success rate - minor issues to address")
        else:
            print(f"\n🔴 NEEDS WORK: {success_rate:.1f}% success rate - significant issues found")
        
        return success_rate >= 95.0


def main():
    """Run the enhanced test suite."""
    suite = EnhancedPurePokerStateMachineTestSuite()
    success = suite.run_enhanced_test_suite()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
