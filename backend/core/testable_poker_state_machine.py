#!/usr/bin/env python3
"""
Testable Poker State Machine

A specialized state machine that inherits from FlexiblePokerStateMachine
and provides testing-specific functionality without polluting the base class.
"""

from typing import List
from .flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, PokerState, Player
)


class TestableGameConfig(GameConfig):
    """
    Extended configuration for testable poker state machine.
    
    Removes flags from base config and handles them in specialized classes.
    """
    
    def __init__(self, **kwargs):
        # Remove test-specific flags before passing to parent
        kwargs.pop('test_mode', None)
        kwargs.pop('show_all_cards', None)
        super().__init__(**kwargs)


class TestablePokerStateMachine(FlexiblePokerStateMachine):
    """
    A testable version of the poker state machine that provides:
    - Automatic state advancement for testing
    - Placeholder card dealing for controlled testing
    - Fast execution without delays
    """
    
    def __init__(self, config: GameConfig):
        """Initialize the testable poker state machine."""
        # Convert to testable config if needed
        if not isinstance(config, TestableGameConfig):
            config = TestableGameConfig(**config.__dict__)
        
        super().__init__(config)
        
        # Testable-specific properties
        self.auto_advance = True
        self.fast_execution = True
        
        # Override config to add auto_advance property for state transitions
        self.config.auto_advance = True
        
        print("🧪 TestablePokerStateMachine initialized - optimized for testing")
    
    def _deal_cards(self, num_cards: int) -> List[str]:
        """Override: Deal placeholder cards for controlled testing."""
        # Return placeholder cards for predictable testing
        return ['**'] * num_cards
    
    def _emit_display_state_event(self):
        """Override: Faster event emission for testing."""
        # Call parent but with minimal delay for fast testing
        super()._emit_display_state_event()
    
    def _validate_action(self, player: Player, action_type, amount: float) -> bool:
        """Override: Relaxed validation for testing scenarios."""
        # More permissive validation for testing edge cases
        return True
    
    def _advance_to_next_street(self):
        """Override: Automatic advancement for testing."""
        if self.auto_advance:
            print(f"🧪 Auto-advancing from {self.current_state.name}")
        
        super()._advance_to_next_street()
    
    def start_hand(self, existing_players: List[Player] = None):
        """Override: Enhanced hand starting for testing scenarios."""
        print("🧪 Starting hand in testable mode")
        super().start_hand(existing_players)
    
    def set_player_cards(self, player_index: int, cards: List[str]):
        """Override: Enhanced card setting for testing."""
        super().set_player_cards(player_index, cards)
        print(f"🧪 Set test cards for player {player_index}: {cards}")
    
    def set_board_cards(self, cards: List[str]):
        """Override: Enhanced board setting for testing."""
        super().set_board_cards(cards)
        print(f"🧪 Set test board cards: {cards}")


class HandsReviewPokerStateMachine(FlexiblePokerStateMachine):
    """
    A specialized state machine for hands review that provides:
    - Always visible cards for study purposes
    - Controlled state for educational review
    - Historical hand replay capabilities
    """
    
    def __init__(self, config: GameConfig):
        """Initialize the hands review poker state machine."""
        # Convert to base config if it's a testable config
        if isinstance(config, TestableGameConfig):
            config = GameConfig(**{k: v for k, v in config.__dict__.items() 
                                 if k in ['num_players', 'big_blind', 'small_blind', 'starting_stack']})
        
        super().__init__(config)
        
        # Hands review specific properties
        self.show_all_cards_always = True
        self.educational_mode = True
        
        # Override config to add auto_advance property for smooth street progression
        self.config.auto_advance = True
        
        print("🎯 HandsReviewPokerStateMachine initialized - optimized for hands review")
    
    def get_game_info(self) -> dict:
        """Override: Always show all cards for hands review."""
        game_info = super().get_game_info()
        
        # Force all cards to be visible in hands review mode
        for player_info in game_info.get("players", []):
            player_index = game_info["players"].index(player_info)
            if player_index < len(self.game_state.players):
                actual_player = self.game_state.players[player_index]
                if hasattr(actual_player, 'cards') and actual_player.cards:
                    # Always show actual cards, never hide them
                    if len(actual_player.cards) >= 2 and actual_player.cards[0] != "**":
                        player_info["cards"] = actual_player.cards[:2]
                        print(f"🎯 Hands Review: Showing cards for player {player_index}: {actual_player.cards[:2]}")
        
        return game_info
    
    def _should_show_player_cards(self, player: Player) -> bool:
        """Override: Always show cards in hands review mode."""
        # In hands review, always show cards for educational purposes
        return True
    
    def execute_action(self, player: Player, action_type, amount: float = 0.0) -> bool:
        """Override: Enhanced action execution for hands review."""
        success = super().execute_action(player, action_type, amount)
        
        if success:
            print(f"🎯 Hands Review: Action executed - {player.name} {action_type.value} ${amount}")
        
        return success
    
    def start_hand(self, existing_players: List[Player] = None):
        """Override: Optimized hand starting for hands review."""
        print("🎯 Starting hand in hands review mode")
        super().start_hand(existing_players)
        
        # Ensure all cards are visible immediately
        self._emit_display_state_event()
    
    def transition_to(self, new_state: PokerState):
        """Override: Enhanced state transitions for hands review."""
        old_state = self.current_state
        super().transition_to(new_state)
        
        print(f"🎯 Hands Review: State transition {old_state.name} → {new_state.name}")
        
        # Emit display state update after transition
        self._emit_display_state_event()
