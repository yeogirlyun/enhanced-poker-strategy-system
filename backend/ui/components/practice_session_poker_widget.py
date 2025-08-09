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
        # Practice session widget always has full features enabled
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        self.strategy_data = strategy_data
        self.practice_mode = True
        self.show_educational_features = True
        
        # Practice-specific UI elements
        self.feedback_label = None
        self.suggestion_label = None
        self.stats_display = None
        self.action_buttons = {}
        
        # Setup practice UI after parent initialization
        self.after_idle(self._setup_practice_ui)
        
        print("🎓 PracticeSessionPokerWidget initialized - enhanced for learning")
    
    def _setup_practice_ui(self):
        """Set up practice-specific UI elements."""
        # Get table color or use default
        table_bg = getattr(self, 'table_color', '#2F4F2F')
        
        # Create feedback area at the bottom using grid (parent uses grid)
        self.feedback_frame = tk.Frame(self, bg=table_bg)
        
        # Configure grid to add feedback at bottom
        self.grid_rowconfigure(1, weight=0)  # Feedback area (fixed height)
        self.feedback_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
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
        self.stats_frame = tk.Frame(self.feedback_frame, bg=table_bg)
        
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
        
        # Add action buttons area
        self._setup_action_buttons()
    
    def _setup_action_buttons(self):
        """Set up industry-standard action buttons for user interaction."""
        # Get table color or use default
        table_bg = getattr(self, 'table_color', '#2F4F2F')
        
        # Create action buttons frame with professional spacing
        self.action_frame = tk.Frame(self, bg=table_bg)
        self.action_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        
        # Configure grid weights
        self.grid_rowconfigure(2, weight=0)  # Action buttons (fixed height)
        
        # Industry-standard button configuration (PokerStars/888poker style)
        button_config = {
            'font': ('Arial', 20, 'bold'),  # Much larger font for visibility
            'width': 12,                    # Wider professional buttons
            'height': 2,                    # Professional height
            'relief': 'raised',
            'bd': 4,                        # Thick professional border
            'cursor': 'hand2',              # Hand cursor on hover
            'pady': 10,                     # Internal padding
        }
        
        # FOLD button - Industry standard bright red
        self.action_buttons['fold'] = tk.Button(
            self.action_frame,
            text="FOLD",
            bg="#E53E3E",                   # Professional red (Chakra UI red.500)
            fg="white",
            activebackground="#C53030",     # Darker red on hover
            activeforeground="white",
            command=lambda: self._handle_action_click('fold'),
            **button_config
        )
        self.action_buttons['fold'].pack(side=tk.LEFT, padx=8, pady=5)
        
        # CHECK/CALL button - Industry standard blue
        self.action_buttons['check_call'] = tk.Button(
            self.action_frame,
            text="CHECK",
            bg="#3182CE",                   # Professional blue (Chakra UI blue.500)
            fg="white",
            activebackground="#2C5282",     # Darker blue on hover
            activeforeground="white",
            command=lambda: self._handle_action_click('check_call'),
            **button_config
        )
        self.action_buttons['check_call'].pack(side=tk.LEFT, padx=8, pady=5)
        
        # Bet amount section with label
        entry_frame = tk.Frame(self.action_frame, bg=table_bg)
        entry_frame.pack(side=tk.LEFT, padx=12, pady=5)
        
        # Amount label
        bet_label = tk.Label(
            entry_frame,
            text="AMOUNT",
            font=('Arial', 14, 'bold'),
            bg=table_bg,
            fg="white"
        )
        bet_label.pack()
        
        # Bet amount entry - enhanced visibility
        self.bet_amount_var = tk.StringVar(value="2.0")
        self.bet_entry = tk.Entry(
            entry_frame,
            textvariable=self.bet_amount_var,
            font=('Arial', 20, 'bold'),     # Large font for amount
            width=8,                        # Optimal width
            justify=tk.CENTER,
            bg="white",
            fg="black",
            relief='sunken',
            bd=4,                          # Thick border
            highlightthickness=3,
            highlightcolor="#68D391",      # Green highlight when focused
            insertbackground="black"        # Black cursor
        )
        self.bet_entry.pack(pady=3)
        
        # BET/RAISE button - Industry standard green
        self.action_buttons['bet_raise'] = tk.Button(
            self.action_frame,
            text="BET",
            bg="#38A169",                   # Professional green (Chakra UI green.500)
            fg="white",
            activebackground="#2F855A",     # Darker green on hover
            activeforeground="white",
            command=lambda: self._handle_action_click('bet_raise'),
            **button_config
        )
        self.action_buttons['bet_raise'].pack(side=tk.LEFT, padx=8, pady=5)
        
        # ALL IN button - Industry standard purple/gold
        self.action_buttons['all_in'] = tk.Button(
            self.action_frame,
            text="ALL IN",
            bg="#805AD5",                   # Professional purple (Chakra UI purple.500)
            fg="white",
            activebackground="#6B46C1",     # Darker purple on hover
            activeforeground="white",
            command=lambda: self._handle_action_click('all_in'),
            **button_config
        )
        self.action_buttons['all_in'].pack(side=tk.LEFT, padx=8, pady=5)
        
        # Initially disable all buttons until it's the human player's turn
        self._disable_action_buttons()
        
        print("🎓 Action buttons setup complete")
    
    def _handle_action_click(self, action_type: str):
        """Handle action button clicks."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            print("🚫 No state machine available")
            return
        
        from core.types import ActionType
        
        # Get the human player
        human_player = None
        for player in self.state_machine.game_state.players:
            if player.is_human:
                human_player = player
                break
        
        if not human_player:
            print("🚫 No human player found")
            return
        
        # Map button action to ActionType and amount
        amount = 0.0
        action = None
        
        if action_type == 'fold':
            action = ActionType.FOLD
        elif action_type == 'check_call':
            # Determine if it's check or call based on current bet
            if self.state_machine.game_state.current_bet > human_player.current_bet:
                action = ActionType.CALL
                amount = self.state_machine.game_state.current_bet - human_player.current_bet
            else:
                action = ActionType.CHECK
        elif action_type == 'bet_raise':
            # Determine if it's bet or raise
            try:
                amount = float(self.bet_amount_var.get())
                if self.state_machine.game_state.current_bet > 0:
                    action = ActionType.RAISE
                else:
                    action = ActionType.BET
            except ValueError:
                print("🚫 Invalid bet amount")
                return
        elif action_type == 'all_in':
            action = ActionType.ALL_IN
            amount = human_player.stack
        
        if action:
            print(f"🎓 Human player action: {action.value} (${amount:.2f})")
            success = self.state_machine.execute_action(human_player, action, amount)
            if success:
                self._disable_action_buttons()
            else:
                print("🚫 Action was not valid")
    
    def _enable_action_buttons(self):
        """Enable action buttons when it's the human player's turn."""
        if not hasattr(self, 'action_buttons'):
            return
        
        # Get current game state to determine valid actions
        if hasattr(self, 'state_machine') and self.state_machine:
            human_player = None
            for player in self.state_machine.game_state.players:
                if player.is_human:
                    human_player = player
                    break
            
            if human_player:
                current_bet = self.state_machine.game_state.current_bet
                player_bet = human_player.current_bet
                
                # Update check/call button text and enable appropriate buttons
                if current_bet > player_bet:
                    call_amount = current_bet - player_bet
                    self.action_buttons['check_call'].config(
                        text=f"CALL\n${call_amount:.1f}",
                        state=tk.NORMAL
                    )
                else:
                    self.action_buttons['check_call'].config(
                        text="CHECK",
                        state=tk.NORMAL
                    )
                
                # Update bet/raise button text
                if current_bet > 0:
                    self.action_buttons['bet_raise'].config(text="RAISE", state=tk.NORMAL)
                else:
                    self.action_buttons['bet_raise'].config(text="BET", state=tk.NORMAL)
                
                # Enable other buttons
                self.action_buttons['fold'].config(state=tk.NORMAL)
                self.action_buttons['all_in'].config(state=tk.NORMAL)
                self.bet_entry.config(state=tk.NORMAL)
                
                print("🎓 Action buttons enabled for human player")
    
    def _disable_action_buttons(self):
        """Disable action buttons when it's not the human player's turn."""
        if not hasattr(self, 'action_buttons'):
            return
        
        for button in self.action_buttons.values():
            button.config(state=tk.DISABLED)
        
        if hasattr(self, 'bet_entry'):
            self.bet_entry.config(state=tk.DISABLED)
        
        print("🎓 Action buttons disabled")
    
    def _handle_action_executed(self, event: GameEvent):
        """Override: Enhanced action handling with educational feedback."""
        print(f"🎓 Practice: Action executed - {event.action} by {event.player_name}")
        
        # Call parent's action handling (includes sounds and animations)
        super()._handle_action_executed(event)
        
        # Ensure sound plays for actions
        if hasattr(event, 'action') and event.action:
            action_str = event.action.value.lower()
            print(f"🔊 Playing sound for action: {action_str}")
            self.play_sound(action_str)
        
        # Display practice-specific feedback
        if hasattr(event, 'data') and event.data and 'feedback' in event.data:
            self._display_feedback(event.data['feedback'])
        
        # Update stats display
        self._update_stats_display()
    
    def _handle_street_progression(self, event: GameEvent):
        """Override: Enhanced street progression with educational insights."""
        print(f"🎓 Practice: Street progression - {event.event_type}")
        
        # Call parent's street progression (includes animations and sounds)
        super()._handle_street_progression(event)
        
        # Ensure animations play for street transitions
        street_name = event.event_type.replace('_', ' ').title()
        print(f"🎬 Animating street progression: {street_name}")
        
        # Play dealing sound for new streets
        if any(keyword in event.event_type.lower() for keyword in ['flop', 'turn', 'river']):
            print(f"🔊 Playing dealing sound for {street_name}")
            self.play_sound("dealing")
        
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
        # For human players, always get actual cards (not ** placeholders)
        actual_cards = cards
        if (hasattr(self, 'state_machine') and 
            self.state_machine and
            player_index < len(self.state_machine.game_state.players) and
            self.state_machine.game_state.players[player_index].is_human and
            cards and cards[0] == "**"):
            
            # Get actual cards from the state machine for human player
            human_player = self.state_machine.game_state.players[player_index]
            actual_cards = human_player.cards if human_player.cards else ["", ""]
            print(f"🎓 Showing human player actual cards: {actual_cards}")
        
        # Call parent's card setting with actual cards
        super()._set_player_cards_from_display_state(player_index, actual_cards)
        
        # Add practice-specific card annotations for human player
        if (player_index < len(self.player_seats) and 
            self.player_seats[player_index] and
            hasattr(self, 'state_machine') and 
            self.state_machine):
            
            # Check if this is the human player
            if (player_index < len(self.state_machine.game_state.players) and
                self.state_machine.game_state.players[player_index].is_human):
                
                self._add_card_annotations(player_index, actual_cards)
    
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
        
        # Play showdown sounds and animations
        print(f"🏆 Playing showdown sounds and animations")
        self.play_sound("winner")
        self._trigger_showdown_animations()
    
    def _trigger_showdown_animations(self):
        """Trigger showdown animations including pot to winner."""
        # This will be called by the parent class through proper event handling
        # The parent class already has _animate_pot_to_winner method
        print(f"🎬 Showdown animations triggered")
        
        # Find the winner and animate pot to them
        if hasattr(self, 'state_machine') and self.state_machine:
            # The parent class will handle the actual animation through its event system
            pass
    
    def highlight_action_player(self, player_index: int):
        """Override: Enhanced action player highlighting for practice."""
        # DON'T call super() - we'll handle highlighting ourselves to distinguish human vs bot
        
        # Use the parent's highlighting method but with custom logic
        self._highlight_current_player(player_index)
        
        # Play notification sound when highlighting any player
        print(f"🔊 Playing turn notification sound for player {player_index}")
        self.play_sound("turn_notify")
        
        # Enable/disable action buttons based on whether it's the human player's turn
        if (hasattr(self, 'state_machine') and 
            self.state_machine and 
            player_index < len(self.state_machine.game_state.players)):
            
            player = self.state_machine.game_state.players[player_index]
            
            if player.is_human:
                # It's the human player's turn - enable action buttons
                self._enable_action_buttons()
                
                # Play special sound for human player's turn
                print(f"🔊 Playing your turn sound")
                self.play_sound("your_turn")
                
                # Get strategy suggestion
                suggestion = None
                if hasattr(self.state_machine, 'get_strategy_suggestion'):
                    suggestion = self.state_machine.get_strategy_suggestion(player)
                
                if suggestion:
                    self._display_suggestion(suggestion)
                else:
                    self._display_suggestion("Consider your position, hand strength, and opponents' actions.")
            else:
                # It's not the human player's turn - disable action buttons
                self._disable_action_buttons()
    
    def _highlight_current_player(self, player_index):
        """Override: Practice-specific player highlighting that distinguishes human vs bot."""
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                
                # Reset all player highlighting first
                player_frame.config(
                    highlightbackground="#2F4F2F",
                    highlightthickness=1,
                    bg="#2F4F2F"
                )
                
                # Remove any existing action indicators
                for widget in player_frame.winfo_children():
                    if hasattr(widget, '_action_indicator'):
                        widget.destroy()
        
        # Now highlight the current action player
        if player_index < len(self.player_seats) and self.player_seats[player_index]:
            player_frame = self.player_seats[player_index]["frame"]
            
            # Check if this player is human
            is_human_player = False
            if (hasattr(self, 'state_machine') and 
                self.state_machine and 
                player_index < len(self.state_machine.game_state.players)):
                is_human_player = self.state_machine.game_state.players[player_index].is_human
            
            if is_human_player:
                # Human player highlighting - bright gold with "YOUR TURN"
                player_frame.config(
                    highlightbackground="#FFD700",  # Bright gold
                    highlightthickness=6,           # Much thicker border
                    bg="#2A2A00"                    # Darker background for contrast
                )
                
                # Add "YOUR TURN" indicator for human player
                action_label = tk.Label(
                    player_frame,
                    text="⚡ YOUR TURN ⚡",
                    bg="#FFD700",
                    fg="#000000",
                    font=("Arial", 10, "bold"),
                    relief="raised",
                    bd=2
                )
                action_label.pack(side=tk.TOP, pady=(0, 2))
                action_label._action_indicator = True
            else:
                # Bot player highlighting - blue with "BOT THINKING"
                player_frame.config(
                    highlightbackground="#4169E1",  # Royal blue
                    highlightthickness=4,           # Thinner than human
                    bg="#000A1A"                    # Dark blue background
                )
                
                # Add "BOT THINKING" indicator for bot player
                action_label = tk.Label(
                    player_frame,
                    text="🤖 BOT THINKING",
                    bg="#4169E1",
                    fg="white",
                    font=("Arial", 9, "bold"),
                    relief="raised",
                    bd=2
                )
                action_label.pack(side=tk.TOP, pady=(0, 2))
                action_label._action_indicator = True
    
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
    
    def increase_table_size(self):
        """Increase the table size (inherited from RPGW)."""
        # Implementation depends on parent class
        print("🎓 Table size increase requested")
    
    def decrease_table_size(self):
        """Decrease the table size (inherited from RPGW)."""
        # Implementation depends on parent class  
        print("🎓 Table size decrease requested")
    
    def change_table_felt(self, felt_color: str):
        """Change the table felt color (inherited from RPGW)."""
        # Implementation depends on parent class
        print(f"🎓 Table felt change requested: {felt_color}")
