import random
from typing import Optional, Tuple

from .unified_types import ActionType, StandardGameState, UnifiedDecisionEngineProtocol

class IndustryGTOEngine(UnifiedDecisionEngineProtocol):
    def __init__(self, player_count: int, stack_depth: float = 100.0, aggression_factor: float = 1.0):
        self.player_count = player_count
        self.stack_depth = stack_depth
        self.aggression_factor = aggression_factor
        print(f"🧠 IndustryGTOEngine: Initialized for {player_count} players.")

    def get_decision(self, player_name: str, game_state: StandardGameState) -> Tuple[ActionType, Optional[float]]:
        player = next((p for p in game_state.players if p.name == player_name), None)
        if not player:
            return ActionType.FOLD, None

        if game_state.street == 'preflop':
            return self._get_preflop_decision(player, game_state)

        return self._get_postflop_decision(player, game_state)

    def _get_preflop_decision(self, player, game_state) -> Tuple[ActionType, Optional[float]]:
        is_open_pot = game_state.current_bet_to_call <= 10
        if is_open_pot:
            if player.position in ["UTG", "MP"] and self._is_premium_hand(player.cards):
                return ActionType.RAISE, 30.0
            elif self._is_playable_hand(player.cards):
                return ActionType.RAISE, 25.0
        else:
            pot_odds = game_state.current_bet_to_call / (game_state.pot + game_state.current_bet_to_call)
            if pot_odds < 0.33 and self._is_strong_hand(player.cards):
                return ActionType.CALL, float(game_state.current_bet_to_call)
        return ActionType.FOLD, None

    def _get_postflop_decision(self, player, game_state) -> Tuple[ActionType, Optional[float]]:
        equity = self._simulate_equity(player.cards, game_state.board)
        if equity > 0.7:
            return ActionType.BET, float(game_state.pot) * 0.66
        if equity > 0.4:
            return (ActionType.CALL, float(game_state.current_bet_to_call)) if game_state.current_bet_to_call > 0 else (ActionType.CHECK, None)
        if random.random() < 0.15 * self.aggression_factor:
            return ActionType.BET, float(game_state.pot) * 0.5
        return (ActionType.FOLD, None) if game_state.current_bet_to_call > 0 else (ActionType.CHECK, None)

    def _is_premium_hand(self, cards):
        ranks = sorted([c[0] for c in cards], key=lambda r: '23456789TJQKA'.index(r), reverse=True)
        return ''.join(ranks) in ['AA', 'KK', 'QQ', 'AK']

    def _is_strong_hand(self, cards):
        ranks = sorted([c[0] for c in cards], key=lambda r: '23456789TJQKA'.index(r), reverse=True)
        return ''.join(ranks) in ['JJ', 'TT', 'AQ', 'AJ', 'KQ'] or self._is_premium_hand(cards)

    def _is_playable_hand(self, cards):
        return self._is_strong_hand(cards)

    def _simulate_equity(self, hole_cards, board):
        hand_strength = 0
        all_cards = hole_cards + board
        ranks = [c[0] for c in all_cards]
        suits = [c[1] for c in all_cards]
        rank_counts = {r: ranks.count(r) for r in set(ranks)}
        if 4 in rank_counts.values(): hand_strength = 0.95
        elif 3 in rank_counts.values() and 2 in rank_counts.values(): hand_strength = 0.9
        elif 3 in rank_counts.values(): hand_strength = 0.7
        elif list(rank_counts.values()).count(2) >= 2: hand_strength = 0.6
        elif 2 in rank_counts.values(): hand_strength = 0.5
        suit_counts = {s: suits.count(s) for s in set(suits)}
        if 5 in suit_counts.values(): hand_strength = max(hand_strength, 0.85)
        return hand_strength

    def has_decision_for_player(self, player_name: str) -> bool:
        return True

    def reset_for_new_hand(self) -> None:
        pass