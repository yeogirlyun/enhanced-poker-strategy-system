#!/usr/bin/env python3
"""
PokerKit Integration for Strategy-Based Poker Practice

This module integrates PokerKit with our strategy system to provide
a robust, battle-tested poker engine while maintaining our custom
strategy-based decision making and visual interface.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from pokerkit import (
    NoLimitTexasHoldem,
    State,
    Card,
    Hand,
    Action,
    Folding,
    CheckingOrCalling,
    CompletionBettingOrRaisingTo,
    ChipsPulling,
    ChipsPushing,
    Pot,
    Player,
    Deck,
    Street,
    Mode,
    AntePosting,
    BlindOrStraddlePosting,
    HoleDealing,
    BoardDealing,
    HoleCardsShowingOrMucking,
    HandKilling,
    BetCollection,
    ChipsPulling,
    ChipsPushing,
)

from gui_models import StrategyData
from hand_evaluator import HandEvaluator


class StrategyAction(Enum):
    """Strategy-based actions."""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class StrategyPlayer:
    """Player with strategy-based decision making."""

    name: str
    position: str
    stack: float
    is_human: bool = False
    is_active: bool = True
    current_bet: float = 0.0
    cards: List[str] = field(default_factory=list)
    last_action: Optional[StrategyAction] = None
    last_bet_size: float = 0.0


@dataclass
class StrategyGameState:
    """Game state for strategy-based poker."""

    players: List[StrategyPlayer]
    pot: float = 0.0
    current_bet: float = 0.0
    board: List[str] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)
    current_player_index: int = 0
    street: str = "preflop"
    dealer_position: int = 0
    small_blind: float = 1.0
    big_blind: float = 2.0


class PokerKitStrategyEngine:
    """PokerKit-based strategy engine."""

    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.hand_evaluator = HandEvaluator()
        self.deviation_logs = []

        # Initialize PokerKit game
        self.game = NoLimitTexasHoldem.create_game(
            (False, 2),  # (ante_trimming_status, ante)
            (1, 2),  # blinds_or_straddles
            (2, 100),  # (min_buy_in, max_buy_in)
            (2, 100),  # (small_blind, big_blind)
        )

    def create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        deck = []
        suits = ["h", "d", "c", "s"]  # hearts, diamonds, clubs, spades
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        for suit in suits:
            for rank in ranks:
                deck.append(f"{rank}{suit}")
        return deck

    def shuffle_deck(self, deck: List[str]) -> List[str]:
        """Shuffle the deck."""
        import random

        shuffled = deck.copy()
        random.shuffle(shuffled)
        return shuffled

    def deal_cards(self, game_state: StrategyGameState) -> None:
        """Deal hole cards to players."""
        deck = self.shuffle_deck(self.create_deck())
        game_state.deck = deck

        # Deal 2 cards to each player
        for player in game_state.players:
            if player.is_active:
                player.cards = [deck.pop(), deck.pop()]

    def deal_board(self, game_state: StrategyGameState, street: str) -> None:
        """Deal community cards based on street."""
        if street == "flop" and len(game_state.board) == 0:
            # Deal flop (3 cards)
            for _ in range(3):
                game_state.board.append(game_state.deck.pop())
        elif street in ["turn", "river"] and len(game_state.board) < 5:
            # Deal turn (1 card) or river (1 card)
            game_state.board.append(game_state.deck.pop())

    def evaluate_hand_strength(
        self, hole_cards: List[str], board: List[str]
    ) -> Tuple[str, float]:
        """Evaluate hand strength using our hand evaluator."""
        hand_rank, kickers, strength = self.hand_evaluator.evaluate_hand(
            hole_cards, board
        )
        return hand_rank.name, strength

    def get_strategy_action(
        self, player: StrategyPlayer, game_state: StrategyGameState
    ) -> StrategyAction:
        """Get strategy-based action for a player."""
        if not player.cards:
            return StrategyAction.FOLD

        # Evaluate hand strength
        hand_rank, strength = self.evaluate_hand_strength(
            player.cards, game_state.board
        )

        # Get position
        position = player.position

        # Get street
        street = game_state.street

        # Determine action based on strategy
        if street == "preflop":
            return self._get_preflop_action(player, game_state, strength)
        else:
            return self._get_postflop_action(player, game_state, strength, hand_rank)

    def _get_preflop_action(
        self, player: StrategyPlayer, game_state: StrategyGameState, strength: float
    ) -> StrategyAction:
        """Get preflop action based on strategy."""
        position = player.position

        # Get preflop strategy
        preflop_strategy = self.strategy_data.strategy.get("preflop", {})
        open_rules = preflop_strategy.get("open_rules", {})

        # Get position-specific rules
        position_rules = open_rules.get(position, {})
        threshold = position_rules.get("threshold", 50)

        # Determine action based on hand strength vs threshold
        if strength >= threshold:
            if game_state.current_bet > 0:
                return StrategyAction.CALL
            else:
                return StrategyAction.BET
        else:
            if game_state.current_bet > 0:
                return StrategyAction.FOLD
            else:
                return StrategyAction.CHECK

    def _get_postflop_action(
        self,
        player: StrategyPlayer,
        game_state: StrategyGameState,
        strength: float,
        hand_rank: str,
    ) -> StrategyAction:
        """Get postflop action based on strategy."""
        position = player.position
        street = game_state.street

        # Get postflop strategy
        postflop_strategy = self.strategy_data.strategy.get("postflop", {})
        street_strategy = postflop_strategy.get(street, {})

        # Get PFA (Postflop Aggressor) strategy
        pfa_strategy = street_strategy.get("pfa", {})
        position_pfa = pfa_strategy.get(position, {})

        val_thresh = position_pfa.get("val_thresh", 50)
        check_thresh = position_pfa.get("check_thresh", 30)

        # Determine action based on hand strength
        if strength >= val_thresh:
            return StrategyAction.BET
        elif strength >= check_thresh:
            if game_state.current_bet > 0:
                return StrategyAction.CALL
            else:
                return StrategyAction.CHECK
        else:
            if game_state.current_bet > 0:
                return StrategyAction.FOLD
            else:
                return StrategyAction.CHECK

    def execute_action(
        self,
        player: StrategyPlayer,
        action: StrategyAction,
        bet_size: float,
        game_state: StrategyGameState,
    ) -> None:
        """Execute a player action."""
        player.last_action = action
        player.last_bet_size = bet_size

        if action == StrategyAction.FOLD:
            player.is_active = False
        elif action in [StrategyAction.CALL, StrategyAction.BET, StrategyAction.RAISE]:
            # Update pot and player stack
            if action == StrategyAction.CALL:
                call_amount = game_state.current_bet - player.current_bet
                player.stack -= call_amount
                game_state.pot += call_amount
                player.current_bet = game_state.current_bet
            else:  # BET or RAISE
                player.stack -= bet_size
                game_state.pot += bet_size
                game_state.current_bet = bet_size
                player.current_bet = bet_size

        # Log deviation if human player
        if player.is_human:
            self._log_deviation(player, action, game_state)

    def _log_deviation(
        self,
        player: StrategyPlayer,
        action: StrategyAction,
        game_state: StrategyGameState,
    ) -> None:
        """Log strategy deviation for human player."""
        strategy_action = self.get_strategy_action(player, game_state)

        deviation = {
            "hand_id": f"hand_{int(time.time())}",
            "player_name": player.name,
            "position": player.position,
            "street": game_state.street,
            "action_taken": action.value,
            "strategy_action": strategy_action.value,
            "deviation_type": "different" if action != strategy_action else "correct",
            "pot_size": game_state.pot,
            "stack_size": player.stack,
            "board": game_state.board.copy(),
            "player_cards": player.cards.copy(),
            "timestamp": time.time(),
        }

        self.deviation_logs.append(deviation)

    def get_feedback_message(self, deviation: Dict) -> str:
        """Get feedback message for a deviation."""
        if deviation["deviation_type"] == "correct":
            return "✅ Correct action! You followed the strategy perfectly."

        action_taken = deviation["action_taken"]
        strategy_action = deviation["strategy_action"]

        if action_taken == "fold" and strategy_action != "fold":
            return f"❌ You folded, but the strategy suggests {strategy_action}. Consider the hand strength and position."
        elif action_taken in ["call", "check"] and strategy_action == "bet":
            return f"⚠️ You {action_taken}ed, but the strategy suggests betting. Your hand might be strong enough to value bet."
        elif action_taken == "bet" and strategy_action in ["check", "fold"]:
            return f"⚠️ You bet, but the strategy suggests {strategy_action}. Consider if your hand is strong enough."
        else:
            return f"📊 Action: {action_taken}, Strategy: {strategy_action}. Review the hand strength and position."

    def play_hand(self, num_players: int = 6) -> Dict[str, Any]:
        """Play a complete hand using PokerKit."""
        # Create players
        players = []
        positions = ["SB", "BB", "UTG", "MP", "CO", "BTN"]

        for i in range(num_players):
            player = StrategyPlayer(
                name=f"Player {i+1}",
                position=positions[i % len(positions)],
                stack=100.0,
                is_human=(i == 0),  # First player is human
            )
            players.append(player)

        # Create game state
        game_state = StrategyGameState(
            players=players,
            pot=0.0,
            current_bet=0.0,
            board=[],
            deck=[],
            current_player_index=0,
            street="preflop",
            dealer_position=0,
            small_blind=1.0,
            big_blind=2.0,
        )

        # Deal cards
        self.deal_cards(game_state)

        # Play through streets
        streets = ["preflop", "flop", "turn", "river"]

        for street in streets:
            game_state.street = street
            if street != "preflop":
                self.deal_board(game_state, street)

            # Play betting round
            self._play_betting_round(game_state)

            # Check if hand is over
            active_players = [p for p in game_state.players if p.is_active]
            if len(active_players) <= 1:
                break

        # Determine winner
        winner = self._determine_winner(game_state)

        return {
            "winner": winner,
            "pot": game_state.pot,
            "board": game_state.board,
            "players": game_state.players,
        }

    def _play_betting_round(self, game_state: StrategyGameState) -> None:
        """Play a betting round."""
        # Simplified betting round for now
        # In a full implementation, this would handle all betting logic
        pass

    def _determine_winner(self, game_state: StrategyGameState) -> StrategyPlayer:
        """Determine the winner of the hand."""
        active_players = [p for p in game_state.players if p.is_active]

        if len(active_players) == 1:
            return active_players[0]

        # Evaluate hands and find winner
        best_player = active_players[0]
        best_strength = 0

        for player in active_players:
            strength = self.hand_evaluator.evaluate_hand(
                player.cards, game_state.board
            )[2]
            if strength > best_strength:
                best_strength = strength
                best_player = player

        return best_player

    def get_session_report(self) -> Dict[str, Any]:
        """Get session statistics and analysis."""
        if not self.deviation_logs:
            return {"message": "No hands played yet."}

        total_hands = len(self.deviation_logs)
        correct_actions = len(
            [d for d in self.deviation_logs if d["deviation_type"] == "correct"]
        )
        accuracy = (correct_actions / total_hands) * 100 if total_hands > 0 else 0

        return {
            "total_hands": total_hands,
            "correct_actions": correct_actions,
            "accuracy_percentage": accuracy,
            "deviations": self.deviation_logs,
        }


# Test the integration
if __name__ == "__main__":
    # Load strategy
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")

    # Create engine
    engine = PokerKitStrategyEngine(strategy_data)

    # Play a hand
    result = engine.play_hand(6)
    print(f"Hand completed. Winner: {result['winner'].name}")
    print(f"Pot: ${result['pot']:.2f}")
    print(f"Board: {result['board']}")

    # Get session report
    report = engine.get_session_report()
    print(f"\nSession Report: {report}")
