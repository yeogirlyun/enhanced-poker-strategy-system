#!/usr/bin/env python3
"""
Practice Session Poker Widget

A specialized poker widget that inherits from ReusablePokerGameWidget
and provides practice-specific functionality for learning and skill development.
"""

import tkinter as tk
from typing import List, Optional
from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.flexible_poker_state_machine import GameEvent


class PracticeSessionPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for practice sessions that inherits from RPGW.
    It provides enhanced features for learning and skill development:
    - Educational feedback display
    - Strategy suggestions
    - Performance tracking
    - Interactive learning aids
    """
    
    def __init__(self, parent, state_machine=None, strategy_data=None, **kwargs):
        # Enable normal mode for full features
        kwargs['debug_mode'] = False
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        self.strategy_data = strategy_data
        self.practice_mode = True
        self.show_educational_features = True
        
        # Practice-specific UI elements
        self.feedback_label = None
        self.suggestion_label = None
        self.stats_display = None
        
        self._setup_practice_ui()
        
        print("🎓 PracticeSessionPokerWidget initialized - enhanced for learning")
    
    def _setup_practice_ui(self):
        """Set up practice-specific UI elements."""
        # Create feedback area at the bottom
        self.feedback_frame = tk.Frame(self, bg=self.table_color)
        self.feedback_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Strategy feedback label
        self.feedback_label = tk.Label(
            self.feedback_frame,
            text="🎓 Practice Mode: Make your move and receive strategic feedback",
            bg="#2E4A3D",  # Darker green background
            fg="white",
            font=("Arial", 10, "bold"),
            wraplength=800,
            justify=tk.CENTER,
            relief="raised",
            bd=2
        )
        self.feedback_label.pack(fill=tk.X, pady=2)
        
        # Strategy suggestion label
        self.suggestion_label = tk.Label(
            self.feedback_frame,
            text="💡 Strategy suggestions will appear here",
            bg="#1E3A2E",  # Even darker green
            fg="#A0FFA0",  # Light green text
            font=("Arial", 9),
            wraplength=800,
            justify=tk.CENTER,
            relief="sunken",
            bd=1
        )
        self.suggestion_label.pack(fill=tk.X, pady=2)
        
        # Session stats display (initially hidden)
        self.stats_frame = tk.Frame(self.feedback_frame, bg=self.table_color)
        
        self.stats_label = tk.Label(
            self.stats_frame,
            text="📊 Session Stats: 0 hands played",
            bg="#1A1A2E",  # Dark blue background
            fg="white",
            font=("Arial", 8),
            justify=tk.LEFT,
            relief="flat"
        )
        self.stats_label.pack(side=tk.LEFT, padx=5)
        
        # Show/hide stats button
        self.toggle_stats_btn = tk.Button(
            self.stats_frame,
            text="📊",
            command=self._toggle_stats_display,
            bg="#4A4A4A",
            fg="white",
            font=("Arial", 8),
            width=3,
            relief="raised"
        )
        self.toggle_stats_btn.pack(side=tk.RIGHT, padx=5)
    
    def _handle_action_executed(self, event: GameEvent):
        """Override: Enhanced action handling with educational feedback."""
        print(f"🎓 Practice: Action executed - {event.action} by {event.player_name}")
        
        # Call parent's action handling
        super()._handle_action_executed(event)
        
        # Display practice-specific feedback
        if hasattr(event, 'data') and event.data and 'feedback' in event.data:
            self._display_feedback(event.data['feedback'])
        
        # Update stats display
        self._update_stats_display()
    
    def _handle_street_progression(self, event: GameEvent):
        """Override: Enhanced street progression with educational insights."""
        print(f"🎓 Practice: Street progression - {event.event_type}")
        
        # Call parent's street progression
        super()._handle_street_progression(event)
        
        # Display street-specific educational content
        if hasattr(event, 'data') and event.data and 'analysis' in event.data:
            self._display_suggestion(event.data['analysis'])
    
    def _display_feedback(self, feedback_text: str):
        """Display educational feedback to the player."""
        if self.feedback_label:
            self.feedback_label.config(
                text=f"🎓 Feedback: {feedback_text}",
                bg="#2E4A3D",
                fg="white"
            )
            
            # Auto-clear feedback after 8 seconds
            self.after(8000, lambda: self._clear_feedback())
    
    def _display_suggestion(self, suggestion_text: str):
        """Display strategic suggestions to the player."""
        if self.suggestion_label:
            self.suggestion_label.config(
                text=f"💡 Strategy: {suggestion_text}",
                bg="#1E3A2E",
                fg="#A0FFA0"
            )
            
            # Auto-clear suggestion after 10 seconds
            self.after(10000, lambda: self._clear_suggestion())
    
    def _clear_feedback(self):
        """Clear the feedback display."""
        if self.feedback_label:
            self.feedback_label.config(
                text="🎓 Practice Mode: Make your move and receive strategic feedback",
                bg="#2E4A3D",
                fg="white"
            )
    
    def _clear_suggestion(self):
        """Clear the suggestion display."""
        if self.suggestion_label:
            self.suggestion_label.config(
                text="💡 Strategy suggestions will appear here",
                bg="#1E3A2E",
                fg="#A0FFA0"
            )
    
    def _update_stats_display(self):
        """Update the session statistics display."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            return
        
        # Get stats from practice state machine
        if hasattr(self.state_machine, 'get_practice_stats'):
            stats = self.state_machine.get_practice_stats()
            
            stats_text = (
                f"📊 Session: {stats['hands_played']} hands | "
                f"Win Rate: {stats['win_rate']:.1f}% | "
                f"Decision Accuracy: {stats['decision_accuracy']:.1f}%"
            )
            
            if self.stats_label:
                self.stats_label.config(text=stats_text)
    
    def _toggle_stats_display(self):
        """Toggle the visibility of detailed statistics."""
        if not hasattr(self, 'stats_displayed'):
            self.stats_displayed = False
        
        if self.stats_displayed:
            # Hide detailed stats
            self.stats_frame.pack_forget()
            self.stats_displayed = False
            self.toggle_stats_btn.config(text="📊")
        else:
            # Show detailed stats
            self.stats_frame.pack(fill=tk.X, pady=2)
            self.stats_displayed = True
            self.toggle_stats_btn.config(text="📈")
            self._update_stats_display()
    
    def _set_player_cards_from_display_state(self, player_index: int, cards: List[str]):
        """Override: Enhanced card display for practice sessions."""
        # Call parent's card setting
        super()._set_player_cards_from_display_state(player_index, cards)
        
        # Add practice-specific card annotations for human player
        if (player_index < len(self.player_seats) and 
            self.player_seats[player_index] and
            hasattr(self, 'state_machine') and 
            self.state_machine):
            
            # Check if this is the human player
            if (player_index < len(self.state_machine.game_state.players) and
                self.state_machine.game_state.players[player_index].is_human):
                
                self._add_card_annotations(player_index, cards)
    
    def _add_card_annotations(self, player_index: int, cards: List[str]):
        """Add educational annotations to the human player's cards."""
        if len(cards) >= 2 and cards[0] != "**" and cards[1] != "**":
            # Analyze hand strength (simplified)
            hand_strength = self._analyze_hand_strength(cards)
            
            # Add visual indicator for hand strength
            player_seat = self.player_seats[player_index]
            if player_seat and "frame" in player_seat:
                # Add hand strength indicator
                strength_color = {
                    "Premium": "#FFD700",  # Gold
                    "Strong": "#90EE90",   # Light Green
                    "Playable": "#87CEEB", # Sky Blue
                    "Weak": "#FFA07A"      # Light Salmon
                }.get(hand_strength, "#FFFFFF")
                
                player_seat["frame"].config(
                    highlightbackground=strength_color,
                    highlightthickness=3
                )
    
    def _analyze_hand_strength(self, cards: List[str]) -> str:
        """Analyze and categorize hand strength for educational purposes."""
        if len(cards) < 2:
            return "Unknown"
        
        # Extract ranks and suits
        rank1, suit1 = cards[0][0], cards[0][1]
        rank2, suit2 = cards[1][0], cards[1][1]
        
        # Simplified hand strength analysis
        high_ranks = ['A', 'K', 'Q', 'J', 'T']
        
        # Pocket pairs
        if rank1 == rank2:
            if rank1 in ['A', 'K', 'Q']:
                return "Premium"
            elif rank1 in ['J', 'T', '9', '8']:
                return "Strong"
            else:
                return "Playable"
        
        # High card combinations
        if rank1 in high_ranks and rank2 in high_ranks:
            return "Premium" if 'A' in [rank1, rank2] else "Strong"
        
        # Suited connectors and suited hands
        if suit1 == suit2:
            return "Playable"
        
        # Connected hands
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        if abs(rank_values.get(rank1, 0) - rank_values.get(rank2, 0)) <= 2:
            return "Playable"
        
        return "Weak"
    
    def display_showdown_analysis(self, analysis_data: dict):
        """Display detailed showdown analysis for learning."""
        if not analysis_data:
            return
        
        result = analysis_data.get('result', 'unknown')
        lesson = analysis_data.get('lesson', 'Keep practicing!')
        
        result_color = "#90EE90" if result == "won" else "#FFA07A"
        
        analysis_text = f"🎯 Hand Result: You {result}! {lesson}"
        
        self._display_feedback(analysis_text)
    
    def highlight_action_player(self, player_index: int):
        """Override: Enhanced action player highlighting for practice."""
        super().highlight_action_player(player_index)
        
        # Add educational prompt for human player
        if (hasattr(self, 'state_machine') and 
            self.state_machine and 
            player_index < len(self.state_machine.game_state.players) and
            self.state_machine.game_state.players[player_index].is_human):
            
            # Get strategy suggestion
            suggestion = None
            if hasattr(self.state_machine, 'get_strategy_suggestion'):
                suggestion = self.state_machine.get_strategy_suggestion(
                    self.state_machine.game_state.players[player_index]
                )
            
            if suggestion:
                self._display_suggestion(suggestion)
            else:
                self._display_suggestion("Consider your position, hand strength, and opponents' actions.")
    
    def reset_practice_session(self):
        """Reset the practice session and clear displays."""
        print("🎓 Resetting practice session")
        
        # Clear feedback and suggestions
        self._clear_feedback()
        self._clear_suggestion()
        
        # Reset stats display
        if hasattr(self, 'state_machine') and hasattr(self.state_machine, 'reset_practice_stats'):
            self.state_machine.reset_practice_stats()
        
        self._update_stats_display()
        
        # Clear any card annotations
        for i, player_seat in enumerate(self.player_seats):
            if player_seat and "frame" in player_seat:
                player_seat["frame"].config(
                    highlightbackground="#2F4F2F",
                    highlightthickness=1
                )
    
    def enable_coaching_mode(self, enabled: bool = True):
        """Enable or disable coaching mode with enhanced feedback."""
        self.show_educational_features = enabled
        
        if enabled:
            self.feedback_label.config(text="🎓 Coaching Mode: Enhanced feedback enabled")
            print("🎓 Coaching mode enabled - providing enhanced educational feedback")
        else:
            self.feedback_label.config(text="🎓 Practice Mode: Basic feedback enabled")
            print("🎓 Coaching mode disabled - providing basic feedback")
    
    def get_practice_performance(self) -> dict:
        """Get comprehensive practice performance data."""
        if hasattr(self, 'state_machine') and hasattr(self.state_machine, 'get_practice_stats'):
            return self.state_machine.get_practice_stats()
        
        return {
            "hands_played": 0,
            "performance": "No data available"
        }
