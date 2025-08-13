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
    
    Handles test-specific flags and configuration.
    """
    
    def __init__(self, **kwargs):
        # Extract test-specific parameters before parent init
        test_mode = kwargs.pop('test_mode', True)  # Default to True for testable config
        show_all_cards = kwargs.pop('show_all_cards', True)
        
        # Initialize parent dataclass
        super().__init__(**kwargs)
        
        # Override with test-specific values after parent init
        self.test_mode = test_mode
        self.show_all_cards = show_all_cards


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


# NOTE: HandsReviewPokerStateMachine moved to hands_review_poker_state_machine_new.py
# The duplicate class here was causing import conflicts and inconsistent behavior.
# All hands review functionality should use the dedicated hands_review_poker_state_machine_new.py
