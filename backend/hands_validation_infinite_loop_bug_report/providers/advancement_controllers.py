"""
Advancement Controller Implementations

Different advancement strategies for different session types.
"""

from typing import List
from ..pure_poker_state_machine import AdvancementController
from ..poker_types import Player, PokerState, GameState


class AutoAdvancementController(AdvancementController):
    """Auto-advance for all-bot sessions (GTO, HandsReview)."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Always auto-advance for bot sessions."""
        return current_state in [
            PokerState.DEAL_FLOP,
            PokerState.DEAL_TURN, 
            PokerState.DEAL_RIVER
        ]
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion for auto-advance sessions."""
        print(f"🤖 AUTO_ADVANCE: Round complete on {street}, pot: ${game_state.displayed_pot()}")


class HumanAdvancementController(AdvancementController):
    """Manual advancement for sessions with human players."""
    
    def __init__(self, human_player_names: List[str] = None):
        self.human_player_names = set(human_player_names or [])
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Only auto-advance if no human players are involved."""
        # Check if any human players are still active
        active_humans = [
            p for p in players 
            if (p.name in self.human_player_names and 
                not p.has_folded and p.is_active)
        ]
        
        # Auto-advance dealing states if no humans are active
        if current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            return len(active_humans) == 0
        
        return False
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion for human sessions."""
        print(f"👤 HUMAN_ADVANCE: Round complete on {street}, pot: ${game_state.displayed_pot()}")


class HandsReviewAdvancementController(AdvancementController):
    """Special advancement for hands review with deterministic replay."""
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Always auto-advance for deterministic replay."""
        return current_state in [
            PokerState.DEAL_FLOP,
            PokerState.DEAL_TURN,
            PokerState.DEAL_RIVER
        ]
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion for hands review."""
        print(f"📖 HANDS_REVIEW: Round complete on {street}, pot: ${game_state.displayed_pot()}")
        
        # Could add special logging or validation here for hands review


class LiveAdvancementController(AdvancementController):
    """Advancement for live play with mixed human/bot players."""
    
    def __init__(self, human_player_names: List[str] = None):
        self.human_player_names = set(human_player_names or [])
    
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Smart advancement based on player types and game state."""
        if current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            # Check if any human players are still in the hand
            active_humans = [
                p for p in players 
                if (p.name in self.human_player_names and 
                    not p.has_folded and p.is_active)
            ]
            
            # If no humans are active, auto-advance
            # If humans are active, they might want to see the cards being dealt
            return len(active_humans) == 0
        
        return False
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion for live play."""
        active_players = [p for p in game_state.players if not p.has_folded and p.is_active]
        human_count = len([p for p in active_players if p.name in self.human_player_names])
        bot_count = len(active_players) - human_count
        
        print(f"🎮 LIVE_PLAY: Round complete on {street}, pot: ${game_state.displayed_pot()} ({human_count} humans, {bot_count} bots active)")
