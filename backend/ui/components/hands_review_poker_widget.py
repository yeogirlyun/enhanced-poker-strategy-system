#!/usr/bin/env python3
"""
Hands Review Poker Widget - Hook-Based Architecture

A specialized poker widget that inherits from ReusablePokerGameWidget
and uses the new hook-based architecture for clean extensibility.

This widget provides hands review specific functionality by overriding
simple, focused hook methods instead of complex core logic.
"""

import tkinter as tk
from typing import List

# Import the base widget
from .reusable_poker_game_widget import ReusablePokerGameWidget

# Import FPSM components
from core.flexible_poker_state_machine import GameEvent


class HandsReviewPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for hands review using hook-based architecture.
    
    This widget is specifically designed for studying hands and provides:
    - Always visible hole cards for all players
    - Simplified logic using clean hook overrides
    - Enhanced educational features
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the hands review poker widget."""
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        # Hands review specific properties
        self.review_mode = True
        
        print("🎯 HandsReviewPokerWidget initialized with hook-based architecture")
    
    # ==============================
    # HOOK OVERRIDES
    # Simple, focused overrides for hands review behavior
    # ==============================
    
    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Hook Override: Always show all cards in hands review mode.
        
        In hands review, we want to see everyone's cards for study purposes.
        """
        return True  # Always show cards, even ** placeholders
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
        """
        Hook Override: Transform ** placeholders to actual cards.
        
        When we receive **, fetch the actual card from the state machine.
        """
        if card == "**" and hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    if hasattr(player, 'cards') and player.cards and card_index < len(player.cards):
                        actual_card = player.cards[card_index]
                        # Card transformation for hands review (keep silent for clean console)
                        return actual_card
            except Exception as e:
                print(f"⚠️ Error transforming card for player {player_index}: {e}")
        
        return card  # Return as-is if no transformation needed
    
    def _should_update_display(self, player_index: int, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Always update in hands review mode.
        
        We want immediate updates for better study experience.
        """
        return True  # Always update for responsive hands review
    
    def _should_update_community_cards(self, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Always update community cards.
        
        Immediate updates for better hands review experience.
        """
        return True  # Always update community cards
    
    def _customize_player_styling(self, player_index: int, player_info: dict) -> dict:
        """
        Hook Override: Enhanced styling for hands review.
        
        Add subtle visual cues for folded players without hiding cards.
        """
        styling = super()._customize_player_styling(player_index, player_info)
        
        # Add subtle folded indicator without hiding cards
        if player_info.get('has_folded', False):
            styling.update({
                'border_color': '#ff6b6b',  # Red border for folded
                'background': '#2a1a1a',    # Slightly darker background
                'text_color': '#ff6b6b'     # Red text
            })
        
        return styling
    
    def _handle_card_interaction(self, player_index: int, card_index: int, card: str):
        """
        Hook Override: Add educational annotations for hands review.
        
        Could be used for hand strength analysis, equity calculations, etc.
        """
        # Add educational features here
        print(f"🎓 Hands Review: Card interaction - Player {player_index}, Card {card_index}: {card}")
        
        # Future: Add hand strength analysis, equity calculations, etc.
        pass
    
    # ==============================
    # HANDS REVIEW SPECIFIC METHODS
    # Additional functionality specific to hands review
    # ==============================
    
    def reveal_all_cards(self):
        """Force revelation of all cards for comprehensive study."""
        print("🎴 Hands Review: Revealing all cards for comprehensive study")
        
        # Force update from FPSM state to ensure all cards are shown
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                # Trigger a display update which will use our hooks
                self._update_from_fpsm_state()
            except Exception as e:
                print(f"⚠️ Error revealing cards: {e}")
    
    def highlight_action_sequence(self, actions: list):
        """Highlight a sequence of actions for study purposes."""
        print(f"🎯 Hands Review: Highlighting action sequence: {actions}")
        # Implementation for action sequence highlighting
        pass
    
    def analyze_hand_strength(self, player_index: int):
        """Analyze and display hand strength for educational purposes."""
        print(f"🎓 Hands Review: Analyzing hand strength for player {player_index}")
        # Implementation for hand strength analysis
        pass


# ==============================
# EXAMPLE OF HOW CLEAN THIS BECOMES
# ==============================

# OLD WAY (complex overrides):
# - Override _set_player_cards_from_display_state with 50+ lines
# - Duplicate change detection logic
# - Fight parent's assumptions
# - Complex conditional logic

# NEW WAY (simple hooks):
# - Override _should_show_card: return True (1 line)
# - Override _transform_card_data: fetch actual cards (10 lines)
# - Override update hooks for responsive behavior (1 line each)
# - Clean, focused, testable methods
