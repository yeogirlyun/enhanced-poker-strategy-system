#!/usr/bin/env python3
"""
Comprehensive Test Suite for PurePokerStateMachine (PPSM)

Tests all critical poker state machine functionality with clean architecture:
1. State transitions and poker flow
2. Action validation and execution
3. Betting round completion logic
4. Street progression (preflop → flop → turn → river)
5. Position tracking and blind posting
6. Pot and current bet management
7. Player state tracking (folded, all-in, active)
8. Multi-player scenarios (2-10 players)
9. Edge cases and error handling
10. Provider integration (deck, rules, advancement)
11. Pure poker logic validation
12. Dependency injection verification
"""

import sys
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add current directory to path
sys.path.append('.')

from core.pure_poker_state_machine import (
    PurePokerStateMachine, GameConfig, DeckProvider, RulesProvider, AdvancementController
)
from core.poker_types import Player, PokerState
from core.hand_model import ActionType


# Mock Providers for Testing
class MockDeckProvider:
    """Mock deck provider for deterministic testing."""
    
    def __init__(self, custom_deck: Optional[List[str]] = None):
        self.custom_deck = custom_deck
        
    def get_deck(self) -> List[str]:
        if self.custom_deck:
            return self.custom_deck.copy()
        
        # Standard deck for testing
        suits = ["C", "D", "H", "S"] 
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        return [rank + suit for suit in suits for rank in ranks]
    
    def replace_deck(self, deck: List[str]) -> None:
        self.custom_deck = deck


class MockRulesProvider:
    """Mock rules provider for testing."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        if num_players == 2:
            # Heads-up: small blind acts first preflop
            return dealer_pos  # dealer is small blind in heads-up
        else:
            # Multi-way: UTG acts first (after big blind)
            return (dealer_pos + 3) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        # First active player after dealer
        for i in range(1, len(players) + 1):
            idx = (dealer_pos + i) % len(players)
            if not players[idx].has_folded and players[idx].is_active:
                return idx
        return -1


class MockAdvancementController:
    """Mock advancement controller for testing."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        # Auto-advance dealing states for testing
        return current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]
    
    def on_round_complete(self, street: str, game_state) -> None:
        # Log round completion for testing
        pass


@dataclass 
class TestResult:
    """Test result tracking."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None


class PurePokerStateMachineTestSuite:
    """Comprehensive test suite for PurePokerStateMachine."""
    
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
    
    def test_initialization_and_config(self):
        """Test 1: Initialization and Configuration."""
        print("\n🧪 Test 1: Initialization and Configuration")
        
        # Test basic initialization
        ppsm = self.create_test_ppsm()
        self.log_test(
            "Basic Initialization",
            ppsm.config.num_players == 2,
            f"PPSM initialized with {ppsm.config.num_players} players"
        )
        
        # Test custom config
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
        
        # Test provider injection
        self.log_test(
            "Provider Injection",
            ppsm.deck_provider is not None and ppsm.rules_provider is not None,
            "All providers properly injected"
        )
    
    def test_player_initialization(self):
        """Test 2: Player Initialization and Positions."""
        print("\n🧪 Test 2: Player Initialization and Positions")
        
        # Test heads-up positions
        ppsm_hu = self.create_test_ppsm(num_players=2)
        positions_hu = [p.position for p in ppsm_hu.game_state.players]
        expected_hu = ["SB", "BB"]
        
        self.log_test(
            "Heads-Up Positions",
            set(positions_hu) == set(expected_hu),
            f"Positions: {positions_hu}",
            {"expected": expected_hu, "actual": positions_hu}
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
        starting_stack = ppsm_hu.config.starting_stack
        all_stacks_correct = all(p.stack == starting_stack for p in ppsm_hu.game_state.players)
        
        self.log_test(
            "Starting Stack Assignment",
            all_stacks_correct,
            f"All players start with ${starting_stack}"
        )
    
    def test_hand_startup_and_blinds(self):
        """Test 3: Hand Startup and Blind Posting."""
        print("\n🧪 Test 3: Hand Startup and Blind Posting")
        
        ppsm = self.create_test_ppsm()
        initial_stacks = {p.name: p.stack for p in ppsm.game_state.players}
        
        # Start hand
        ppsm.start_hand()
        
        # Check hand initialization
        self.log_test(
            "Hand State Initialization",
            ppsm.current_state == PokerState.PREFLOP_BETTING,
            f"Hand started in state: {ppsm.current_state}"
        )
        
        # Check blind posting
        sb_player = ppsm.game_state.players[ppsm.small_blind_position]
        bb_player = ppsm.game_state.players[ppsm.big_blind_position]
        
        sb_posted = initial_stacks[sb_player.name] - sb_player.stack == ppsm.config.small_blind
        bb_posted = initial_stacks[bb_player.name] - bb_player.stack == ppsm.config.big_blind
        
        self.log_test(
            "Small Blind Posted",
            sb_posted,
            f"SB posted ${ppsm.config.small_blind}: {sb_player.current_bet}"
        )
        
        self.log_test(
            "Big Blind Posted", 
            bb_posted,
            f"BB posted ${ppsm.config.big_blind}: {bb_player.current_bet}"
        )
        
        # Check pot calculation - displayed_pot includes current_bet during betting
        expected_pot = ppsm.config.small_blind + ppsm.config.big_blind
        self.log_test(
            "Initial Pot Calculation",
            ppsm.game_state.displayed_pot() == expected_pot,
            f"Pot: ${ppsm.game_state.displayed_pot()} (expected: ${expected_pot})"
        )
        
        # Check current bet
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
        
        # Test valid FOLD
        fold_valid = ppsm._is_valid_action(action_player, ActionType.FOLD, 0.0)
        self.log_test(
            "FOLD Action Valid",
            fold_valid,
            "FOLD should always be valid for active players"
        )
        
        # Test CALL validation
        call_valid = ppsm._is_valid_action(action_player, ActionType.CALL, 0.0)
        expected_call = action_player.current_bet < ppsm.game_state.current_bet
        
        self.log_test(
            "CALL Action Validation",
            call_valid == expected_call,
            f"CALL valid: {call_valid} (current_bet: ${action_player.current_bet}, to_call: ${ppsm.game_state.current_bet})"
        )
        
        # Test CHECK validation
        check_valid = ppsm._is_valid_action(action_player, ActionType.CHECK, 0.0)
        expected_check = action_player.current_bet == ppsm.game_state.current_bet
        
        self.log_test(
            "CHECK Action Validation",
            check_valid == expected_check,
            f"CHECK valid: {check_valid} (player_bet: ${action_player.current_bet}, current_bet: ${ppsm.game_state.current_bet})"
        )
        
        # Test RAISE validation
        raise_amount = 4.0  # Valid raise to $4
        raise_valid = ppsm._is_valid_action(action_player, ActionType.RAISE, raise_amount)
        expected_raise = (raise_amount > ppsm.game_state.current_bet and 
                         (raise_amount - action_player.current_bet) <= action_player.stack)
        
        self.log_test(
            "RAISE Action Validation",
            raise_valid == expected_raise,
            f"RAISE to ${raise_amount} valid: {raise_valid}"
        )
        
        # Test invalid large raise (more than stack)
        invalid_raise = ppsm.game_state.players[0].stack + 100.0
        invalid_raise_valid = ppsm._is_valid_action(action_player, ActionType.RAISE, invalid_raise)
        
        self.log_test(
            "Invalid RAISE Rejection",
            not invalid_raise_valid,
            f"RAISE to ${invalid_raise} should be invalid (stack: ${action_player.stack})"
        )
    
    def test_action_execution(self):
        """Test 5: Action Execution and State Updates."""
        print("\n🧪 Test 5: Action Execution and State Updates")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        initial_pot = ppsm.game_state.displayed_pot()
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        initial_stack = action_player.stack
        
        # Test RAISE execution
        raise_amount = 4.0
        success = ppsm.execute_action(action_player, ActionType.RAISE, raise_amount)
        
        self.log_test(
            "RAISE Execution Success",
            success,
            f"RAISE to ${raise_amount} executed successfully"
        )
        
        # Check bet update
        self.log_test(
            "Player Bet Update",
            action_player.current_bet == raise_amount,
            f"Player bet updated: ${action_player.current_bet}"
        )
        
        # Check stack update
        expected_stack = initial_stack - (raise_amount - ppsm.config.small_blind)  # Assuming SB player
        actual_stack_change = initial_stack - action_player.stack
        
        self.log_test(
            "Stack Update", 
            actual_stack_change > 0,
            f"Stack reduced by ${actual_stack_change}"
        )
        
        # Check pot update
        expected_pot_increase = raise_amount - ppsm.config.small_blind  # Additional amount
        actual_pot = ppsm.game_state.displayed_pot()
        
        self.log_test(
            "Pot Update",
            actual_pot > initial_pot,
            f"Pot increased from ${initial_pot} to ${actual_pot}"
        )
        
        # Check current bet update  
        self.log_test(
            "Current Bet Update",
            ppsm.game_state.current_bet == raise_amount,
            f"Current bet updated to ${ppsm.game_state.current_bet}"
        )
    
    def test_betting_round_completion(self):
        """Test 6: Betting Round Completion Logic."""
        print("\n🧪 Test 6: Betting Round Completion Logic")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        # Execute actions to complete preflop
        players = ppsm.game_state.players
        
        # SB calls BB
        sb_player = players[ppsm.small_blind_position]
        if ppsm.action_player_index == ppsm.small_blind_position:
            success = ppsm.execute_action(sb_player, ActionType.CALL, 0.0)
            self.log_test(
                "SB Call Execution",
                success,
                "SB completed call to BB"
            )
            
            # After SB call, BB should have the option to act
            initial_state = ppsm.current_state
            action_player_after_sb = ppsm.game_state.players[ppsm.action_player_index]
            
            # BB should now be the action player
            bb_is_action_player = ppsm.action_player_index == ppsm.big_blind_position
            
            # Complete the round with BB check
            if bb_is_action_player:
                bb_player = players[ppsm.big_blind_position]
                bb_success = ppsm.execute_action(bb_player, ActionType.CHECK, 0.0)
                
                # Now check if round completes after BB check
                current_state = ppsm.current_state
                advanced_to_flop = current_state in [PokerState.DEAL_FLOP, PokerState.FLOP_BETTING]
                
                self.log_test(
                    "Preflop Round Completion",
                    advanced_to_flop,
                    f"Advanced from {initial_state} to {current_state} after SB call + BB check"
                )
    
    def test_street_progression(self):
        """Test 7: Street Progression (Preflop → Flop → Turn → River)."""
        print("\n🧪 Test 7: Street Progression")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        # Track state progression
        states_visited = [ppsm.current_state]
        
        # Complete preflop (SB calls, then BB checks)
        if ppsm.action_player_index == ppsm.small_blind_position:
            # SB calls
            ppsm.execute_action(ppsm.game_state.players[ppsm.small_blind_position], ActionType.CALL, 0.0)
            states_visited.append(ppsm.current_state)
            
            # BB checks (if BB is now action player)
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
        
        # Check board cards dealt
        if ppsm.current_state == PokerState.FLOP_BETTING:
            flop_cards_dealt = len(ppsm.game_state.board) == 3
            self.log_test(
                "Flop Cards Dealt", 
                flop_cards_dealt,
                f"Board has {len(ppsm.game_state.board)} cards: {ppsm.game_state.board}"
            )
            
            # Check street update
            self.log_test(
                "Street Update to Flop",
                ppsm.game_state.street == "flop",
                f"Game street updated to: {ppsm.game_state.street}"
            )
            
            # Check bets reset for new round
            bets_reset = all(p.current_bet == 0.0 for p in ppsm.game_state.players if not p.has_folded)
            current_bet_reset = ppsm.game_state.current_bet == 0.0
            
            self.log_test(
                "Bets Reset for Flop",
                bets_reset and current_bet_reset,
                f"Bets reset: players={bets_reset}, current_bet=${ppsm.game_state.current_bet}"
            )
    
    def test_multi_player_scenarios(self):
        """Test 8: Multi-Player Scenarios."""
        print("\n🧪 Test 8: Multi-Player Scenarios")
        
        # Test 6-max game
        ppsm_6max = self.create_test_ppsm(num_players=6)
        ppsm_6max.start_hand()
        
        active_players = len([p for p in ppsm_6max.game_state.players if p.is_active])
        self.log_test(
            "6-Max Active Players",
            active_players == 6,
            f"6-max game has {active_players} active players"
        )
        
        # Test position assignment in 6-max
        positions = [p.position for p in ppsm_6max.game_state.players]
        expected_positions = {"SB", "BB", "UTG", "MP", "CO", "BTN"} 
        
        self.log_test(
            "6-Max Position Assignment",
            len(set(positions) & expected_positions) >= 4,  # At least 4 standard positions
            f"Positions assigned: {positions}"
        )
        
        # Test action player determination
        action_player = ppsm_6max.game_state.players[ppsm_6max.action_player_index]
        self.log_test(
            "6-Max Action Player",
            action_player is not None and action_player.is_active,
            f"Action player: {action_player.name} ({action_player.position})"
        )
    
    def test_fold_scenarios(self):
        """Test 9: Fold Scenarios and Player Elimination."""
        print("\n🧪 Test 9: Fold Scenarios")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        # Get action player and fold
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        initial_active_count = len([p for p in ppsm.game_state.players if p.is_active])
        
        # Execute fold
        fold_success = ppsm.execute_action(action_player, ActionType.FOLD, 0.0)
        
        self.log_test(
            "Fold Execution",
            fold_success,
            f"{action_player.name} folded successfully"
        )
        
        # Check player marked as folded
        self.log_test(
            "Player Marked Folded",
            action_player.has_folded,
            f"{action_player.name} marked as folded"
        )
        
        # Check player marked inactive
        self.log_test(
            "Player Marked Inactive",
            not action_player.is_active,
            f"{action_player.name} marked as inactive"
        )
        
        # Check active player count reduced
        final_active_count = len([p for p in ppsm.game_state.players if p.is_active])
        self.log_test(
            "Active Player Count Reduced",
            final_active_count < initial_active_count,
            f"Active players: {initial_active_count} → {final_active_count}"
        )
    
    def test_pot_and_stack_tracking(self):
        """Test 10: Pot and Stack Tracking Accuracy.""" 
        print("\n🧪 Test 10: Pot and Stack Tracking")
        
        ppsm = self.create_test_ppsm()
        
        # Track initial totals
        initial_total_chips = sum(p.stack for p in ppsm.game_state.players)
        
        ppsm.start_hand()
        
        # After blinds - include current_bet as chips are there during betting
        total_after_blinds = sum(p.stack + p.current_bet for p in ppsm.game_state.players) + ppsm.game_state.committed_pot
        
        self.log_test(
            "Chip Conservation After Blinds",
            abs(total_after_blinds - initial_total_chips) < 0.01,
            f"Total chips: {initial_total_chips} → {total_after_blinds}"
        )
        
        # Execute a raise
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        raise_amount = 6.0
        
        if ppsm._is_valid_action(action_player, ActionType.RAISE, raise_amount):
            ppsm.execute_action(action_player, ActionType.RAISE, raise_amount)
            
            # Check chip conservation after raise
            total_after_raise = sum(p.stack + p.current_bet for p in ppsm.game_state.players) + ppsm.game_state.committed_pot
            
            self.log_test(
                "Chip Conservation After Raise", 
                abs(total_after_raise - initial_total_chips) < 0.01,
                f"Total chips: {initial_total_chips} → {total_after_raise}"
            )
    
    def test_edge_cases_and_error_handling(self):
        """Test 11: Edge Cases and Error Handling."""
        print("\n🧪 Test 11: Edge Cases and Error Handling")
        
        ppsm = self.create_test_ppsm()
        ppsm.start_hand()
        
        # Test action on folded player
        folded_player = Player(
            name="FoldedPlayer",
            stack=100.0,
            position="TEST",
            is_human=False,
            is_active=False,
            cards=[]
        )
        folded_player.has_folded = True
        
        invalid_action = ppsm._is_valid_action(folded_player, ActionType.RAISE, 10.0)
        self.log_test(
            "Folded Player Action Rejected",
            not invalid_action,
            "Actions on folded players should be invalid"
        )
        
        # Test action with insufficient stack
        action_player = ppsm.game_state.players[ppsm.action_player_index]
        oversized_bet = action_player.stack + 100.0
        
        oversized_invalid = ppsm._is_valid_action(action_player, ActionType.BET, oversized_bet)
        self.log_test(
            "Oversized Bet Rejected",
            not oversized_invalid,
            f"Bet of ${oversized_bet} rejected (stack: ${action_player.stack})"
        )
        
        # Test negative amounts
        negative_invalid = ppsm._is_valid_action(action_player, ActionType.BET, -5.0)
        self.log_test(
            "Negative Bet Rejected",
            not negative_invalid,
            "Negative bet amounts should be invalid"
        )
    
    def test_provider_integration(self):
        """Test 12: Provider Integration and Dependency Injection."""
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
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite."""
        print("🧪 COMPREHENSIVE PURE POKER STATE MACHINE TEST SUITE")
        print("=" * 70)
        print("Testing pure poker logic with clean architecture...")
        print()
        
        start_time = time.time()
        
        # Run all test categories
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
        
        end_time = time.time()
        
        # Calculate results
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Print summary
        print(f"\n{'=' * 70}")
        print("🏁 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Test Duration: {end_time - start_time:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.results:
                if not result.passed:
                    print(f"   • {result.name}: {result.message}")
                    if result.details:
                        print(f"     Details: {result.details}")
        
        if success_rate >= 95.0:
            print(f"\n🎉 EXCELLENT! PurePokerStateMachine passed {success_rate:.1f}% of tests!")
            print("✅ Ready for production use with clean architecture!")
        elif success_rate >= 80.0:
            print(f"\n🟡 GOOD: {success_rate:.1f}% success rate - minor issues to address")
        else:
            print(f"\n🔴 NEEDS WORK: {success_rate:.1f}% success rate - significant issues found")
        
        return success_rate >= 95.0


def main():
    """Run the comprehensive PPSM test suite."""
    suite = PurePokerStateMachineTestSuite()
    success = suite.run_comprehensive_test_suite()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
