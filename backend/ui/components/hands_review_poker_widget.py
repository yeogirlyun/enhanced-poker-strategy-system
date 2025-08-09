#!/usr/bin/env python3
"""
Hands Review Poker Widget

A specialized poker widget that inherits from ReusablePokerGameWidget
and provides hands review specific functionality, such as:
- Always showing all hole cards for study purposes
- Simplified UI optimized for review rather than gameplay
- Enhanced card visibility and analysis features
"""

import tkinter as tk
from typing import List

# Import the base widget
from .reusable_poker_game_widget import ReusablePokerGameWidget

# Import FPSM components
from core.flexible_poker_state_machine import GameEvent


class HandsReviewPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for hands review that inherits from RPGW.
    
    This widget is specifically designed for studying hands and provides:
    - Always visible hole cards for all players
    - Simplified animations optimized for learning
    - Enhanced card state management for review purposes
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the hands review poker widget."""
        # Hands review widget always has full features enabled
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        # Hands review specific properties
        self.always_show_cards = True
        self.review_mode = True
        
        print("🎯 HandsReviewPokerWidget initialized - full animations and sounds enabled")
    
    def _set_player_cards_from_display_state(self, player_index: int, cards: List[str]):
        """Override: Always show cards in hands review mode."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        card_widgets = self.player_seats[player_index]["card_widgets"]
        
        # In hands review mode, get the actual player cards from FPSM directly
        # This bypasses any display state filtering
        actual_cards = self._get_actual_player_cards(player_index)
        if actual_cards and len(actual_cards) >= 2:
            cards = actual_cards
            print(f"🎴 Hands Review: Using actual cards for player {player_index}: {cards}")
        
        if len(cards) >= 2 and len(card_widgets) >= 2:
            # In hands review mode, always show the first 2 cards
            for i in range(2):
                card = cards[i] if i < len(cards) else ""
                
                # Check if card actually changed to prevent redraw
                current_card = getattr(card_widgets[i], '_current_card', "")
                
                if current_card != card:
                    if card and card != "**" and card != "" and card is not None:
                        try:
                            # In hands review, never show cards as folded - always visible
                            # Check if this player has actually folded for visual styling
                            player_has_folded = False
                            if player_index < len(self.last_player_states):
                                player_has_folded = self.last_player_states[player_index].get("has_folded", False)
                            
                            # Show card face even if folded, but with a subtle visual indicator
                            card_widgets[i].set_card(card, is_folded=False)
                            card_widgets[i]._current_card = card
                            
                            # Add subtle visual indicator for folded players without hiding cards
                            if player_has_folded:
                                self._add_folded_overlay(card_widgets[i])
                            
                            print(f"🎴 Hands Review: Player {player_index} card {i}: {current_card} → {card} (always visible)")
                        except tk.TclError:
                            # Widget was destroyed, skip
                            pass
                    elif card == "**":
                        # In hands review, even hidden cards should be preserved if we have them
                        if current_card and current_card != "":
                            print(f"🎴 Hands Review: Player {player_index} card {i}: preserved {current_card} (ignoring ** in review mode)")
                        else:
                            # If we truly don't have a card, show empty (not card back)
                            try:
                                card_widgets[i].set_card("", is_folded=False)  # Empty, not card back
                                card_widgets[i]._current_card = ""
                                print(f"🎴 Hands Review: Player {player_index} card {i}: showing empty space (no card back)")
                            except tk.TclError:
                                pass
    
    def _get_actual_player_cards(self, player_index: int) -> List[str]:
        """Get actual player cards directly from FPSM, bypassing display state filtering."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            return []
        
        try:
            if (hasattr(self.state_machine, 'game_state') and 
                self.state_machine.game_state and 
                player_index < len(self.state_machine.game_state.players)):
                
                player = self.state_machine.game_state.players[player_index]
                if hasattr(player, 'cards') and player.cards:
                    # If cards are not placeholders, return them
                    if len(player.cards) >= 2 and player.cards[0] != "**":
                        return player.cards[:2]  # Return first 2 cards (hole cards)
        except Exception as e:
            print(f"⚠️ Error getting actual player cards for player {player_index}: {e}")
        
        return []
    
    def _add_folded_overlay(self, card_widget):
        """Add a subtle visual indicator that this player folded without hiding the card."""
        try:
            # Add a semi-transparent overlay or border to indicate folded status
            # while keeping the card visible for study purposes
            card_widget.create_rectangle(
                0, 0, card_widget.width, card_widget.height,
                fill="", outline="#ff6b6b", width=3, dash=(5, 5)
            )
        except Exception:
            # If overlay fails, continue without it
            pass
    
    def _mark_player_folded(self, player_index):
        """Override: In hands review, don't hide cards when players fold."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        # Don't hide the cards - just add visual indicators
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            # Add folded overlay instead of hiding cards
            self._add_folded_overlay(card_widget)
        
        # Update the player frame styling
        player_frame = self.player_seats[player_index]["frame"]
        
        # Remove any existing action indicators
        for widget in player_frame.winfo_children():
            if hasattr(widget, '_action_indicator'):
                widget.destroy()
        
        # Add "FOLDED" indicator with more subtle styling
        folded_label = tk.Label(
            player_frame,
            text="🚫 FOLDED 🚫",
            bg="#ff6b6b",  # Red background but more vibrant
            fg="#FFFFFF",  # White text
            font=("Arial", 9, "bold"),
            relief="raised",
            bd=1
        )
        folded_label._action_indicator = True
        folded_label.pack(side=tk.TOP, pady=2)
        
        # Change player frame to indicate folded but keep it visible
        player_frame.config(
            highlightbackground="#ff6b6b",  # Red border
            highlightthickness=2,
            bg="#2a1a1a"  # Slightly darker but not gray
        )
        
        print(f"🎯 Hands Review: Player {player_index} folded - cards remain visible for study")
    
    def _restore_player_cards(self, player_index):
        """Override: Enhanced card restoration for new hands in review mode."""
        if player_index >= len(self.player_seats) or not self.player_seats[player_index]:
            return
        
        # Remove folded overlays and restore normal appearance
        card_widgets = self.player_seats[player_index]["card_widgets"]
        for card_widget in card_widgets:
            # Remove any overlay elements
            try:
                # Clear and redraw the card if it exists
                current_card = getattr(card_widget, '_current_card', "")
                if current_card:
                    card_widget.delete("all")
                    card_widget.set_card(current_card, is_folded=False)
            except Exception:
                pass
        
        print(f"🎯 Hands Review: Player {player_index} cards restored for new hand")
    
    def _handle_action_executed(self, event: GameEvent):
        """Override: Enhanced action handling for review mode with sounds and animations."""
        print(f"🎯 Hands Review: Action executed - {event.action} by {event.player_name} for ${event.amount}")
        
        # Find player index
        player_index = -1
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and player_seat.get("name_label"):
                seat_text = player_seat["name_label"].cget("text")
                seat_name = seat_text.split(' (')[0]
                if event.player_name == seat_name or event.player_name in seat_text:
                    player_index = i
                    break
        
        if player_index >= 0:
            # Clear action indicators
            self._clear_action_indicators(player_index)
            
            # Play sound based on action (re-enabled for better experience)
            if event.action:
                if event.action.value == "fold":
                    self.play_sound("fold")
                elif event.action.value == "call":
                    self.play_sound("call") 
                elif event.action.value == "bet":
                    self.play_sound("bet")
                elif event.action.value == "raise":
                    self.play_sound("raise")
                elif event.action.value == "check":
                    self.play_sound("check")
            
            # Show bet display with normal animations
            if event.amount > 0:
                self._show_bet_display_for_player(player_index, event.action.value if event.action else "bet", event.amount)
        
        # Call parent's logging functionality
        self._log_event(event)
    
    def _animate_bet_to_pot(self, player_index, amount):
        """Override: Re-enable animations for better hands review experience."""
        print(f"🎯 Hands Review: Animating ${amount} from player {player_index} to pot")
        
        # Use parent's full animation for better visual feedback
        super()._animate_bet_to_pot(player_index, amount)
    
    def _animate_street_progression(self, street_name, board_cards):
        """Override: Immediate street progression for review."""
        print(f"🎯 Hands Review: Street progression to {street_name} with cards {board_cards}")
        
        # Immediately update community cards without animation
        self._update_community_cards_from_display_state(board_cards)
    
    def play_sound(self, sound_type: str, **kwargs):
        """Override: Re-enable sounds for better hands review experience."""
        print(f"🔊 Hands Review: Playing sound - {sound_type}")
        # Use parent's sound system for full audio feedback
        super().play_sound(sound_type, **kwargs)
    
    def reveal_all_cards(self):
        """Override: Enhanced card revelation for study purposes."""
        print("🎴 Hands Review: Revealing all cards for comprehensive study")
        
        # Force update from FPSM state to ensure all cards are shown
        self._update_from_fpsm_state()
        
        # Additionally, ensure any hidden cards are made visible
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and hasattr(self, 'state_machine') and self.state_machine:
                try:
                    game_info = self.state_machine.get_game_info()
                    players = game_info.get("players", [])
                    if i < len(players):
                        player_cards = players[i].get("cards", [])
                        if player_cards and len(player_cards) >= 2:
                            # Force set the cards to ensure visibility
                            self._set_player_cards_from_display_state(i, player_cards)
                except Exception as e:
                    print(f"⚠️ Error revealing cards for player {i}: {e}")
    
    def update_font_size(self, font_size):
        """Override: Optimized font sizing for review readability."""
        # Use slightly larger fonts for better readability during study
        review_font_size = int(font_size * 1.1)  # 10% larger for better readability
        super().update_font_size(review_font_size)
        print(f"🎯 Hands Review: Font size optimized for readability - {review_font_size}")
