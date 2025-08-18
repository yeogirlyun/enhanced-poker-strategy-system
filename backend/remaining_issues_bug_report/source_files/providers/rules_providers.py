"""
Rules Provider Implementations

Different poker rules for different game types and situations.
"""

from typing import List
from ..pure_poker_state_machine import RulesProvider
from ..poker_types import Player


class StandardRules(RulesProvider):
    """Standard poker rules for most sessions."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """Get first player to act preflop."""
        if num_players == 2:
            # Heads-up: small blind (dealer) acts first preflop
            return dealer_pos
        else:
            # Multi-way: UTG (left of big blind) acts first
            big_blind_pos = (dealer_pos + 2) % num_players
            return (big_blind_pos + 1) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """Get first active player to act postflop."""
        # Heads-up: small blind (dealer) acts first postflop
        # Multi-way: first active player left of dealer acts first
        if len(players) == 2:
            # Heads-up: dealer/small blind acts first postflop
            dealer_player = players[dealer_pos]
            if not dealer_player.has_folded and dealer_player.is_active and dealer_player.stack > 0:
                return dealer_pos
            # If dealer is out, other player acts
            other_idx = (dealer_pos + 1) % 2
            other_player = players[other_idx]
            if not other_player.has_folded and other_player.is_active and other_player.stack > 0:
                return other_idx
            return -1
        else:
            # Multi-way: first active player left of dealer
            for i in range(1, len(players) + 1):
                idx = (dealer_pos + i) % len(players)
                player = players[idx]
                if not player.has_folded and player.is_active and player.stack > 0:
                    return idx
            return -1  # No active players


class HandsReviewRules(RulesProvider):
    """Rules for hands review - may need special handling for replaying actions."""
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """Get first player to act preflop (same as standard for now)."""
        if num_players == 2:
            return dealer_pos
        else:
            big_blind_pos = (dealer_pos + 2) % num_players
            return (big_blind_pos + 1) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """Get first active player to act postflop."""
        # Same logic as StandardRules - heads-up special case
        if len(players) == 2:
            # Heads-up: dealer/small blind acts first postflop
            dealer_player = players[dealer_pos]
            if not dealer_player.has_folded and dealer_player.is_active:
                return dealer_pos
            # If dealer is out, other player acts
            other_idx = (dealer_pos + 1) % 2
            other_player = players[other_idx]
            if not other_player.has_folded and other_player.is_active:
                return other_idx
            return -1
        else:
            # Multi-way: first active player left of dealer
            for i in range(1, len(players) + 1):
                idx = (dealer_pos + i) % len(players)
                player = players[idx]
                if not player.has_folded and player.is_active:
                    return idx
            return -1


class TournamentRules(RulesProvider):
    """Tournament rules with antes and special blind structures."""
    
    def __init__(self, ante: float = 0.0):
        self.ante = ante
    
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """Tournament preflop action (same as standard for now)."""
        if num_players == 2:
            return dealer_pos
        else:
            big_blind_pos = (dealer_pos + 2) % num_players
            return (big_blind_pos + 1) % num_players
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """Tournament postflop action."""
        for i in range(1, len(players) + 1):
            idx = (dealer_pos + i) % len(players)
            player = players[idx]
            if not player.has_folded and player.is_active and player.stack > 0:
                return idx
        return -1
