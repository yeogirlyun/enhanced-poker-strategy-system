from typing import List
from .rules_provider import RulesProvider
from ..core.poker_types import Player


class StandardRules(RulesProvider):
    """Standard heads-up action order rules."""
    
    def get_first_to_act(self, players: List[Player], street: str) -> int:
        """Return the index of the first player to act on the given street."""
        if street == "preflop":
            # Small blind acts first preflop
            for i, player in enumerate(players):
                if player.position == "small_blind":
                    return i
            # Fallback to first active player
            for i, player in enumerate(players):
                if player.is_active and not player.has_folded:
                    return i
        else:
            # Button acts first postflop
            for i, player in enumerate(players):
                if player.position == "button":
                    return i
            # Fallback to first active player
            for i, player in enumerate(players):
                if player.is_active and not player.has_folded:
                    return i
        return 0  # Default fallback
    
    def get_action_order(
        self, players: List[Player], street: str
    ) -> List[int]:
        """Return the order of players to act on the given street."""
        first = self.get_first_to_act(players, street)
        order = []
        for i in range(len(players)):
            idx = (first + i) % len(players)
            if players[idx].is_active and not players[idx].has_folded:
                order.append(idx)
        return order
