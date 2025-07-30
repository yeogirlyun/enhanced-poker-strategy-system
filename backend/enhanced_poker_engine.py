#!/usr/bin/env python3
"""
Enhanced Poker Engine with Strategy Integration

This module provides a robust poker engine using treys for fast hand evaluation
and integrates with our strategy system for practice sessions.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import random

from treys import Card, Evaluator
from gui_models import StrategyData


class Action(Enum):
    """Poker actions."""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class Position(Enum):
    """Player positions."""

    SB = "SB"
    BB = "BB"
    UTG = "UTG"
    MP = "MP"
    CO = "CO"
    BTN = "BTN"


@dataclass
class Player:
    """Player in the game."""

    name: str
    position: Position
    stack: float
    is_human: bool = False
    is_active: bool = True
    current_bet: float = 0.0
    cards: List[str] = field(default_factory=list)
    last_action: Optional[Action] = None
    last_bet_size: float = 0.0


@dataclass
class GameState:
    """Game state."""

    players: List[Player]
    pot: float = 0.0
    current_bet: float = 0.0
    board: List[str] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)
    current_player_index: int = 0
    street: str = "preflop"
    dealer_position: int = 0
    small_blind: float = 1.0
    big_blind: float = 2.0


@dataclass
class DeviationLog:
    """Log of strategy deviations."""

    hand_id: str
    player_name: str
    position: str
    street: str
    action_taken: str
    strategy_action: str
    deviation_type: str
    pot_size: float
    stack_size: float
    board: List[str]
    player_cards: List[str]
    timestamp: float


class EnhancedPokerEngine:
    """Enhanced poker engine with strategy integration."""

    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.evaluator = Evaluator()
        self.deviation_logs = []
        self.current_game_state: Optional[GameState] = None

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
        shuffled = deck.copy()
        random.shuffle(shuffled)
        return shuffled

    def deal_cards(self, game_state: GameState) -> None:
        """Deal hole cards to players."""
        deck = self.shuffle_deck(self.create_deck())
        game_state.deck = deck

        # Deal 2 cards to each player
        for player in game_state.players:
            if player.is_active:
                player.cards = [deck.pop(), deck.pop()]

    def deal_board(self, game_state: GameState, street: str) -> None:
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
        """Evaluate hand strength using treys."""
        if not hole_cards:
            return "high_card", 0.0

        # Convert cards to treys format
        treys_cards = []
        for card in hole_cards:
            treys_cards.append(Card.new(card))

        treys_board = []
        for card in board:
            treys_board.append(Card.new(card))

        # Evaluate hand
        if treys_board:
            # Postflop
            score = self.evaluator.evaluate(treys_cards, treys_board)
            rank = self.evaluator.get_rank_class(score)
            rank_name = self.evaluator.class_to_string(rank)

            # Normalize score (lower is better in treys)
            normalized_score = 1.0 - (score / 7462.0)  # 7462 is worst hand
            return rank_name, normalized_score * 100
        else:
            # Preflop - use simplified evaluation
            return self._evaluate_preflop_strength(hole_cards)

    def _evaluate_preflop_strength(self, hole_cards: List[str]) -> Tuple[str, float]:
        """Evaluate preflop hand strength."""
        if len(hole_cards) != 2:
            return "high_card", 0.0

        card1, card2 = hole_cards
        rank1, suit1 = card1[0], card1[1]
        rank2, suit2 = card2[0], card2[1]

        # Convert ranks to values
        rank_values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        val1, val2 = rank_values[rank1], rank_values[rank2]
        suited = suit1 == suit2
        paired = val1 == val2

        # Calculate strength
        if paired:
            if val1 >= 10:  # TT+
                return "pair", 85.0 + (val1 - 10) * 2
            else:  # 22-99
                return "pair", 60.0 + (val1 - 2) * 3
        elif suited:
            if val1 == 14 and val2 >= 10:  # AKs, AQs, AJs
                return "suited", 80.0 + (val2 - 10) * 5
            elif val1 >= 12 and val2 >= 10:  # KQs, KJs, QJs
                return "suited", 70.0 + (val1 - 12) * 5
            else:
                return "suited", 50.0 + (val1 + val2) / 2
        else:
            if val1 == 14 and val2 >= 10:  # AKo, AQo, AJo
                return "offsuit", 75.0 + (val2 - 10) * 3
            elif val1 >= 12 and val2 >= 10:  # KQo, KJo, QJo
                return "offsuit", 65.0 + (val1 - 12) * 3
            else:
                return "offsuit", 40.0 + (val1 + val2) / 2

    def get_strategy_action(self, player: Player, game_state: GameState) -> Action:
        """Get strategy-based action for a player."""
        if not player.cards:
            return Action.FOLD

        # Evaluate hand strength
        hand_rank, strength = self.evaluate_hand_strength(
            player.cards, game_state.board
        )

        # Get position
        position = player.position.value

        # Get street
        street = game_state.street

        # Determine action based on strategy
        if street == "preflop":
            return self._get_preflop_action(player, game_state, strength)
        else:
            return self._get_postflop_action(player, game_state, strength, hand_rank)

    def _get_preflop_action(
        self, player: Player, game_state: GameState, strength: float
    ) -> Action:
        """Get preflop action based on strategy."""
        position = player.position.value

        # Get preflop strategy
        preflop_strategy = self.strategy_data.strategy.get("preflop", {})
        open_rules = preflop_strategy.get("open_rules", {})

        # Get position-specific rules
        position_rules = open_rules.get(position, {})
        threshold = position_rules.get("threshold", 50)

        # Determine action based on hand strength vs threshold
        if strength >= threshold:
            if game_state.current_bet > 0:
                return Action.CALL
            else:
                return Action.BET
        else:
            if game_state.current_bet > 0:
                return Action.FOLD
            else:
                return Action.CHECK

    def _get_postflop_action(
        self, player: Player, game_state: GameState, strength: float, hand_rank: str
    ) -> Action:
        """Get postflop action based on strategy."""
        position = player.position.value
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
            return Action.BET
        elif strength >= check_thresh:
            if game_state.current_bet > 0:
                return Action.CALL
            else:
                return Action.CHECK
        else:
            if game_state.current_bet > 0:
                return Action.FOLD
            else:
                return Action.CHECK

    def execute_action(
        self, player: Player, action: Action, bet_size: float, game_state: GameState
    ) -> None:
        """Execute a player action."""
        player.last_action = action
        player.last_bet_size = bet_size

        if action == Action.FOLD:
            player.is_active = False
        elif action in [Action.CALL, Action.BET, Action.RAISE]:
            # Update pot and player stack
            if action == Action.CALL:
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
        self, player: Player, action: Action, game_state: GameState
    ) -> None:
        """Log strategy deviation for human player."""
        strategy_action = self.get_strategy_action(player, game_state)

        deviation = DeviationLog(
            hand_id=f"hand_{int(time.time())}",
            player_name=player.name,
            position=player.position.value,
            street=game_state.street,
            action_taken=action.value,
            strategy_action=strategy_action.value,
            deviation_type="different" if action != strategy_action else "correct",
            pot_size=game_state.pot,
            stack_size=player.stack,
            board=game_state.board.copy(),
            player_cards=player.cards.copy(),
            timestamp=time.time(),
        )

        self.deviation_logs.append(deviation)

    def get_feedback_message(self, deviation: DeviationLog) -> str:
        """Get feedback message for a deviation."""
        if deviation.deviation_type == "correct":
            return "✅ Correct action! You followed the strategy perfectly."

        action_taken = deviation.action_taken
        strategy_action = deviation.strategy_action

        if action_taken == "fold" and strategy_action != "fold":
            return f"❌ You folded, but the strategy suggests {strategy_action}. Consider the hand strength and position."
        elif action_taken in ["call", "check"] and strategy_action == "bet":
            return f"⚠️ You {action_taken}ed, but the strategy suggests betting. Your hand might be strong enough to value bet."
        elif action_taken == "bet" and strategy_action in ["check", "fold"]:
            return f"⚠️ You bet, but the strategy suggests {strategy_action}. Consider if your hand is strong enough."
        else:
            return f"📊 Action: {action_taken}, Strategy: {strategy_action}. Review the hand strength and position."

    def play_hand(self, num_players: int = 6) -> Dict[str, Any]:
        """Play a complete hand."""
        # Create players
        players = []
        positions = [
            Position.SB,
            Position.BB,
            Position.UTG,
            Position.MP,
            Position.CO,
            Position.BTN,
        ]

        for i in range(num_players):
            player = Player(
                name=f"Player {i+1}",
                position=positions[i % len(positions)],
                stack=100.0,
                is_human=(i == 0),  # First player is human
            )
            players.append(player)

        # Create game state
        game_state = GameState(
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

        # Store current game state for external access
        self.current_game_state = game_state

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

    def _play_betting_round(self, game_state: GameState) -> None:
        """Play a betting round."""
        # Simplified betting round for now
        # In a full implementation, this would handle all betting logic
        pass

    def _determine_winner(self, game_state: GameState) -> Player:
        """Determine the winner of the hand."""
        active_players = [p for p in game_state.players if p.is_active]

        if len(active_players) == 1:
            return active_players[0]

        # Evaluate hands and find winner
        best_player = active_players[0]
        best_strength = 0

        for player in active_players:
            strength = self.evaluate_hand_strength(player.cards, game_state.board)[1]
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
            [d for d in self.deviation_logs if d.deviation_type == "correct"]
        )
        accuracy = (correct_actions / total_hands) * 100 if total_hands > 0 else 0

        return {
            "total_hands": total_hands,
            "correct_actions": correct_actions,
            "accuracy_percentage": accuracy,
            "deviations": self.deviation_logs,
        }


# Test the enhanced engine
if __name__ == "__main__":
    # Load strategy
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")

    # Create engine
    engine = EnhancedPokerEngine(strategy_data)

    # Play a hand
    result = engine.play_hand(6)
    print(f"Hand completed. Winner: {result['winner'].name}")
    print(f"Pot: ${result['pot']:.2f}")
    print(f"Board: {result['board']}")

    # Get session report
    report = engine.get_session_report()
    print(f"\nSession Report: {report}")
