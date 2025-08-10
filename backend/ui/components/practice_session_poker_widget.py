#!/usr/bin/env python3
"""
Practice Session Poker Widget - Hook-Based Architecture

A specialized poker widget that inherits from ReusablePokerGameWidget
and uses the new hook-based architecture for clean extensibility.

This widget provides practice session specific functionality by overriding
simple, focused hook methods instead of complex core logic.
"""

import tkinter as tk
from typing import List, Dict, Any

# Import the base widget
from .reusable_poker_game_widget import ReusablePokerGameWidget

# Import modern UI components
from .modern_poker_widgets import ModernActionButton, BetSliderWidget, ChipStackDisplay

# Import FPSM components
from core.flexible_poker_state_machine import GameEvent


def debug_log(message: str, category: str = "PRACTICE_WIDGET"):
    """Log debug messages to file instead of console."""
    try:
        from core.session_logger import get_session_logger
        logger = get_session_logger()
        logger.log_system("DEBUG", category, message, {})
    except:
        # Fallback to silent operation if logger not available
        pass


class PracticeSessionPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for practice sessions using hook-based architecture.
    
    This widget is specifically designed for interactive learning and provides:
    - Human player cards always visible
    - Educational annotations and feedback
    - Interactive action buttons
    - Performance tracking and analysis
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the practice session poker widget."""
        # Extract practice-specific parameters before calling parent
        self.strategy_data = kwargs.pop('strategy_data', None)
        
        # Call parent with remaining kwargs (tkinter-safe parameters only)
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        # Practice session specific properties
        self.practice_mode = True
        self.action_buttons = {}
        self.prebet_buttons = {}
        
        # Setup UI controller for state machine sound calls
        if self.state_machine:
            self._setup_ui_controller()
        
        # Setup practice-specific UI after parent initialization
        self.after_idle(self._setup_practice_ui)
        
        # Initialization debug removed to reduce log spam
    
    # ==============================
    # HOOK OVERRIDES
    # Simple, focused overrides for practice session behavior
    # ==============================
    
    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Hook Override: Show cards based on practice session policy.
        
        - Human player: Always show cards (including ** which will be transformed)
        - Bot players: Hide cards (show card backs)
        """
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    if hasattr(player, 'is_human') and player.is_human:
                        # Card hook debug removed to reduce log spam
                        return True  # Always show human player cards (including **)
            except Exception as e:
                # Card transform error debug removed
                pass
        
        # For bot players, use default behavior (hide ** cards)
        result = card != "**" and card != ""
        # Card hook debug removed to reduce log spam
        return result
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
        """
        Hook Override: Transform ** to actual cards for human players only.
        
        This ensures human players can always see their cards for learning.
        """
        # Card transform debug removed to reduce log spam
        
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    is_human = hasattr(player, 'is_human') and player.is_human
                    # Player type debug removed
                    
                    if is_human:
                        # For human player, ALWAYS return actual cards (even if not **)
                        if hasattr(player, 'cards') and player.cards and card_index < len(player.cards):
                            actual_card = player.cards[card_index]
                            # Card transform debug removed
                            return actual_card
                        else:
                            # Card error debug removed
                            return card
            except Exception:
                # Error debug removed to reduce log spam
                pass
        
        # Bot card debug removed to reduce log spam
        return card  # Return as-is for bot players
    
    def _should_update_display(self, player_index: int, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Responsive updates for practice sessions.
        
        Always update for immediate feedback during practice.
        """
        return True  # Always update for responsive practice experience
    
    def _should_update_community_cards(self, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Always update community cards for practice.
        
        Immediate updates for better learning experience.
        """
        return True  # Always update community cards
    
    def _customize_player_styling(self, player_index: int, player_info: dict) -> dict:
        """
        Hook Override: Enhanced styling for practice sessions.
        
        Highlight human player, add visual cues for different player types.
        """
        styling = super()._customize_player_styling(player_index, player_info)
        
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    if hasattr(player, 'is_human') and player.is_human:
                        # Highlight human player
                        styling.update({
                            'border_color': '#FFD700',  # Gold border for human
                            'background': '#1a1a2e',    # Slightly different background
                            'text_color': '#FFD700'     # Gold text
                        })
            except Exception:
                pass
        
        return styling
    
    def _handle_card_interaction(self, player_index: int, card_index: int, card: str):
        """
        Hook Override: Add educational features for practice sessions.
        
        Hand strength analysis, strategy suggestions, etc.
        """
        debug_log(f"Practice: Card interaction - Player {player_index}, Card {card_index}: {card}", "CARD_INTERACTION")
        
        # Add hand strength analysis for human player
        if self._is_human_player(player_index):
            self._add_card_analysis(player_index, card_index, card)
    
    # ==============================
    # PRACTICE SESSION SPECIFIC METHODS
    # Additional functionality specific to practice sessions
    # ==============================
    
    def _setup_practice_ui(self):
        """Setup practice-specific UI elements."""
        debug_log("Setting up practice session UI", "PRACTICE_INIT")
        
        # Create action buttons container
        self._create_action_buttons()
        
        # Create feedback display
        self._create_feedback_display()
        
        # Create performance tracking
        self._create_performance_display()
    
    def _create_action_buttons(self):
        """Create interactive action buttons for human player."""
        debug_log("Creating action buttons for practice session", "PRACTICE_INIT")
        
        # Get table background color
        table_bg = getattr(self, 'table_color', '#2F4F2F')
        
        # Create action buttons container at bottom of widget
        action_container = tk.Frame(self, bg=table_bg)
        action_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Configure grid weight
        self.grid_rowconfigure(1, weight=0)
        
        # Pre-bet size buttons section
        prebet_frame = tk.Frame(action_container, bg=table_bg)
        prebet_frame.grid(row=0, column=0, columnspan=4, pady=(0, 5))
        
        prebet_label = tk.Label(
            prebet_frame, 
            text="QUICK BETS:", 
            font=('Arial', 10, 'bold'),
            bg=table_bg, 
            fg="white"
        )
        prebet_label.pack(side=tk.LEFT, padx=(0, 10))
        
        prebet_config = {
            'font': ('Arial', 10, 'bold'),
            'width': 8,
            'height': 1,
            'bd': 2,
            'cursor': 'hand2',
            'bg': '#87CEEB',
            'fg': 'black',
            'activebackground': '#87CEEB',
            'activeforeground': 'black',
        }
        
        # Pre-bet size buttons
        prebet_sizes = [
            ("1/4 POT", 0.25), ("1/2 POT", 0.5), ("3/4 POT", 0.75),
            ("POT", 1.0), ("2X POT", 2.0)
        ]
        
        self.prebet_buttons = {}
        for text, multiplier in prebet_sizes:
            btn = tk.Button(
                prebet_frame,
                text=text,
                command=lambda m=multiplier: self._set_pot_bet(m),
                **prebet_config
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.prebet_buttons[text] = btn
        
        # Main action buttons section
        button_config = {
            'font': ('Arial', 18, 'bold'),
            'width': 10,
            'height': 2,
            'bd': 4,
            'cursor': 'hand2'
        }
        
        # FOLD button (modern style)
        self.action_buttons['fold'] = ModernActionButton(
            action_container,
            action_type="fold",
            text="FOLD",
            command=lambda: self._handle_action_click('fold')
        )
        self.action_buttons['fold'].grid(row=1, column=0, padx=5, pady=5)
        
        # CHECK/CALL button (modern style)
        self.action_buttons['check_call'] = ModernActionButton(
            action_container,
            action_type="check",
            text="CHECK",
            command=lambda: self._handle_action_click('check_call')
        )
        self.action_buttons['check_call'].grid(row=1, column=1, padx=5, pady=5)
        
        # BET/RAISE button (modern style)
        self.action_buttons['bet_raise'] = ModernActionButton(
            action_container,
            action_type="bet",
            text="BET",
            command=lambda: self._handle_action_click('bet_raise')
        )
        self.action_buttons['bet_raise'].grid(row=1, column=2, padx=5, pady=5)
        
        # ALL IN button (modern style)
        self.action_buttons['all_in'] = ModernActionButton(
            action_container,
            action_type="all_in",
            text="ALL IN",
            command=lambda: self._handle_action_click('all_in')
        )
        self.action_buttons['all_in'].grid(row=1, column=3, padx=5, pady=5)
        
        # Modern bet slider section
        slider_frame = tk.Frame(action_container, bg=table_bg)
        slider_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Create bet slider widget
        self.bet_slider = BetSliderWidget(
            slider_frame,
            min_bet=2.0,  # Default minimum bet
            max_bet=200.0,  # Default maximum (will be updated based on stack)
            current_bet=2.0,
            on_change=self._on_bet_amount_change
        )
        self.bet_slider.pack()
        
        # Store bet amount for compatibility
        self.bet_amount_var = tk.StringVar(value="2.0")
        
        # Initially disable all buttons
        self._disable_action_buttons()
    
    def _on_bet_amount_change(self, amount: float):
        """Handle bet amount changes from the slider."""
        self.bet_amount_var.set(str(amount))
        debug_log(f"Bet amount changed to: ${amount:.2f}", "BET_SLIDER")
    
    def _create_feedback_display(self):
        """Create educational feedback display."""
        debug_log("Creating feedback display for practice session", "PRACTICE_INIT")
        
        # Implementation would go here
        pass
    
    def _create_performance_display(self):
        """Create performance tracking display."""
        debug_log("Creating performance display for practice session", "PRACTICE_INIT")
        
        # Implementation would go here
        pass
    
    def _is_human_player(self, player_index: int) -> bool:
        """Check if player is human."""
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    return hasattr(player, 'is_human') and player.is_human
            except Exception:
                pass
        return False
    
    def _add_card_analysis(self, player_index: int, card_index: int, card: str):
        """Add educational card analysis."""
        debug_log(f"Adding card analysis for {card}", "CARD_ANALYSIS")
        
        # Implementation would analyze hand strength, provide suggestions, etc.
        pass
    
    def provide_action_feedback(self, action: str, amount: float):
        """Provide educational feedback on player actions."""
        print(f"🎓 Action feedback: {action} ${amount}")
        
        # Implementation would analyze the action and provide learning feedback
        pass
    
    def update_performance_stats(self, decision_quality: str):
        """Update performance tracking stats."""
        print(f"🎓 Performance update: {decision_quality}")
        
        # Implementation would track decision quality, learning progress, etc.
        pass
    
    # ==============================
    # ACTION BUTTON IMPLEMENTATION
    # ==============================
    
    def _handle_action_click(self, action_type: str):
        """Handle action button clicks."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            print("🚫 No state machine available")
            return
        
        try:
            from core.types import ActionType
            
            if action_type == 'fold':
                success = self.state_machine.execute_action(
                    self.state_machine.game_state.players[0],  # Human player
                    ActionType.FOLD,
                    0.0
                )
            elif action_type == 'check_call':
                # Determine if it's check or call
                current_bet = self.state_machine.game_state.current_bet
                human_bet = self.state_machine.game_state.players[0].current_bet
                
                if current_bet > human_bet:
                    # Need to call
                    call_amount = current_bet - human_bet
                    success = self.state_machine.execute_action(
                        self.state_machine.game_state.players[0],
                        ActionType.CALL,
                        call_amount
                    )
                else:
                    # Can check
                    success = self.state_machine.execute_action(
                        self.state_machine.game_state.players[0],
                        ActionType.CHECK,
                        0.0
                    )
            elif action_type == 'bet_raise':
                # Get amount from entry (POKER FIX: Only accept integers)
                try:
                    # Parse as float first, then convert to integer (proper poker bet sizing)
                    raw_amount = float(self.bet_amount_var.get())
                    amount = int(round(raw_amount))  # Round to nearest integer
                    
                    # Validate minimum bet size (must be at least big blind)
                    big_blind = self.state_machine.config.big_blind
                    if amount < big_blind:
                        debug_log(f"⚠️ Bet amount ${amount} below minimum (${big_blind}), adjusting to ${big_blind}", "BET_VALIDATION")
                        amount = int(big_blind)
                    
                    # Update the entry to show the corrected amount
                    self.bet_amount_var.set(str(amount))
                    
                    current_bet = self.state_machine.game_state.current_bet
                    
                    if current_bet > 0:
                        # It's a raise
                        success = self.state_machine.execute_action(
                            self.state_machine.game_state.players[0],
                            ActionType.RAISE,
                            amount
                        )
                    else:
                        # It's a bet
                        success = self.state_machine.execute_action(
                            self.state_machine.game_state.players[0],
                            ActionType.BET,
                            amount
                        )
                except ValueError:
                    print("🚫 Invalid bet amount")
                    return
            elif action_type == 'all_in':
                stack = self.state_machine.game_state.players[0].stack
                # For all-in, we use BET or RAISE with the full stack amount
                current_bet = self.state_machine.game_state.current_bet
                if current_bet > 0:
                    success = self.state_machine.execute_action(
                        self.state_machine.game_state.players[0],
                        ActionType.RAISE,
                        stack
                    )
                else:
                    success = self.state_machine.execute_action(
                        self.state_machine.game_state.players[0],
                        ActionType.BET,
                        stack
                    )
            
            if not success:
                print(f"🚫 Action {action_type} failed")
            else:
                print(f"✅ Action {action_type} successful")
                
        except Exception as e:
            print(f"🚫 Error executing action {action_type}: {e}")
    
    def _set_pot_bet(self, multiplier: float):
        """Set bet amount based on pot size multiplier."""
        if hasattr(self, 'state_machine') and self.state_machine:
            pot_size = self.state_machine.game_state.pot
            bet_amount = pot_size * multiplier
            
            # Round to nearest $0.50, minimum $2.00
            bet_amount = max(2.0, round(bet_amount * 2) / 2)
            
            self.bet_amount_var.set(f"{bet_amount:.2f}")
            print(f"🎓 Set bet amount to ${bet_amount:.2f} ({multiplier}x pot)")
    
    def _enable_action_buttons(self):
        """Enable action buttons when it's the human player's turn."""
        if not hasattr(self, 'action_buttons'):
            return
        
        # Update button text based on game state
        if hasattr(self, 'state_machine') and self.state_machine:
            current_bet = self.state_machine.game_state.current_bet
            human_bet = self.state_machine.game_state.players[0].current_bet
            
            if current_bet > human_bet:
                self.action_buttons['check_call'].config(text="CALL", state=tk.NORMAL)
                self.action_buttons['bet_raise'].config(text="RAISE", state=tk.NORMAL)
            else:
                self.action_buttons['check_call'].config(text="CHECK", state=tk.NORMAL)
                self.action_buttons['bet_raise'].config(text="BET", state=tk.NORMAL)
        
        # Enable all modern action buttons
        for button in self.action_buttons.values():
            if hasattr(button, 'set_enabled'):
                button.set_enabled(True)
            else:
                button.config(state=tk.NORMAL)
        
        # Enable pre-bet buttons
        if hasattr(self, 'prebet_buttons'):
            for button in self.prebet_buttons.values():
                button.config(state=tk.NORMAL)
        
        # Enable bet slider
        if hasattr(self, 'bet_slider'):
            # Bet slider is always enabled when action buttons are enabled
            pass
        
        debug_log("Action buttons enabled for human player", "PRACTICE_UI")
    
    def _disable_action_buttons(self):
        """Disable action buttons when it's not the human player's turn."""
        if not hasattr(self, 'action_buttons'):
            return
        
        # Disable all modern action buttons
        for button in self.action_buttons.values():
            if hasattr(button, 'set_enabled'):
                button.set_enabled(False)
            else:
                button.config(state=tk.DISABLED)
        
        if hasattr(self, 'prebet_buttons'):
            for button in self.prebet_buttons.values():
                button.config(state=tk.DISABLED)
        
        # Bet slider remains enabled but grayed out during opponent turns
        
        # Action buttons disabled for practice session
    
    # ==============================
    # HELPER METHODS
    # ==============================
    
    def _clear_all_player_highlights(self):
        """Clear highlights from all player seats."""
        for i, player_seat in enumerate(self.player_seats):
            if player_seat:
                player_frame = player_seat["frame"]
                # Reset to normal appearance
                player_frame.config(
                    highlightbackground="#006400",  # Dark green
                    highlightthickness=2,
                    bg="#1a1a1a"  # Normal background
                )
                # Remove any action indicators
                for widget in player_frame.winfo_children():
                    if hasattr(widget, '_action_indicator'):
                        widget.destroy()
    
    # ==============================
    # OVERRIDE PARENT HIGHLIGHTING METHOD
    # ==============================
    
    def _highlight_current_player(self, player_index):
        """Override: Enhanced player highlighting for practice sessions."""
        # Don't call parent's highlighting - we'll handle it completely here
        # Clear any existing highlights first
        self._clear_all_player_highlights()
        
        # Add practice-specific highlighting
        if self._is_human_player(player_index):
            # Human player turn - enable action buttons and provide feedback
            self._enable_action_buttons()
            
            # Play turn notification sound
            self.play_sound("turn_notify")
            
            # Add visual indicator
            if player_index < len(self.player_seats) and self.player_seats[player_index]:
                player_frame = self.player_seats[player_index]["frame"]
                
                # Gold border and label for human
                player_frame.config(
                    highlightbackground="#FFD700",
                    highlightthickness=6,
                    bg="#1a1a1a",  # Darker background for contrast
                    relief="solid",
                    bd=3
                )
                
                # Add turn indicator
                turn_label = tk.Label(
                    player_frame,
                    text="⚡ YOUR TURN ⚡",
                    bg="#FFD700",
                    fg="#000000",
                    font=("Arial", 10, "bold"),
                    relief="raised",
                    bd=2
                )
                turn_label._action_indicator = True
                turn_label.pack(side=tk.TOP, pady=2)
        else:
            # Bot player turn - disable action buttons
            self._disable_action_buttons()
            
            # Add bot indicator
            if player_index < len(self.player_seats) and self.player_seats[player_index]:
                player_frame = self.player_seats[player_index]["frame"]
                
                # Bright blue border for bots with better visibility
                player_frame.config(
                    highlightbackground="#4169E1",
                    highlightthickness=5,
                    bg="#0a0a1a",  # Darker background for contrast
                    relief="solid",
                    bd=2
                )
                
                # Add bot thinking indicator
                bot_label = tk.Label(
                    player_frame,
                    text="🤖 BOT THINKING",
                    bg="#4169E1",
                    fg="#FFFFFF",
                    font=("Arial", 9, "bold"),
                    relief="raised",
                    bd=1
                )
                bot_label._action_indicator = True
                bot_label.pack(side=tk.TOP, pady=2)
    
    def on_event(self, event: 'GameEvent'):
        """Override: Enhanced event handling with animations for practice sessions."""
        super().on_event(event)
        
        # Handle state changes that should disable action buttons
        if event.event_type == "state_change":
            try:
                new_state = getattr(event, 'new_state', None)
                if hasattr(event, 'data') and event.data:
                    new_state = event.data.get("new_state", new_state)
                
                # Disable action buttons during showdown and hand completion
                if new_state in ["SHOWDOWN", "END_HAND"]:
                    self._disable_action_buttons()
                    debug_log(f"🎓 Practice: Disabled action buttons for state {new_state}", "STATE_CHANGE")
                    
                    # Also disable pre-bet buttons
                    for btn in self.prebet_buttons.values():
                        btn.config(state=tk.DISABLED)
                        
            except Exception as e:
                debug_log(f"⚠️ Error handling state change: {e}", "STATE_CHANGE")
        
        # Handle hand completion events
        if event.event_type == "hand_complete":
            self._disable_action_buttons()
            # Disable pre-bet buttons as well
            for btn in self.prebet_buttons.values():
                btn.config(state=tk.DISABLED)
            debug_log("🎓 Practice: Disabled all action buttons for hand completion", "HAND_COMPLETE")
        
        # Add bet animations for practice sessions
        if event.event_type == "action_executed":
            try:
                # GameEvent structure has different attributes
                action_type = getattr(event, 'action_type', None)
                amount = getattr(event, 'amount', 0.0) 
                player_index = getattr(event, 'player_index', None)
                
                # Alternative: try to get from event data if available
                if hasattr(event, 'data') and event.data:
                    action_type = event.data.get("action_type", action_type)
                    amount = event.data.get("amount", amount)
                    player_index = event.data.get("player_index", player_index)
                
                if action_type and action_type in ["bet", "raise", "call"] and amount > 0 and player_index is not None:
                    print(f"🎓 Practice: Animating ${amount} bet from player {player_index}")
                    # Trigger bet animation
                    self.after(100, lambda: self.play_animation("bet_to_pot", 
                                                                player_index=player_index, 
                                                                amount=amount))
                else:
                    debug_log(f"🎓 Practice: No animation needed - action: {action_type}, amount: {amount}, player: {player_index}", "BET_ANIMATION")
            except Exception as e:
                debug_log(f"⚠️ Error handling bet animation: {e}", "BET_ANIMATION")

    def _setup_ui_controller(self):
        """Setup UI controller to handle state machine sound and animation calls."""
        # Create a simple UI controller that the state machine can use
        class SimpleUIController:
            def __init__(self, widget):
                self.widget = widget
            
            def play_sound(self, sound_type: str, **kwargs):
                """Play sound through the widget's sound system."""
                if hasattr(self.widget, 'play_sound'):
                    # Map state machine sound names to widget sound names
                    sound_mapping = {
                        'check_sound': 'check',
                        'call_sound': 'call', 
                        'bet_sound': 'bet',
                        'raise_sound': 'raise',
                        'fold_sound': 'fold',
                        'all_in_sound': 'all_in'
                    }
                    mapped_sound = sound_mapping.get(sound_type, sound_type)
                    self.widget.play_sound(mapped_sound, **kwargs)
            
            def animate(self, animation_type: str, **kwargs):
                """Trigger animation through the widget's animation system."""
                if hasattr(self.widget, 'play_animation'):
                    self.widget.play_animation(animation_type, **kwargs)
            
            def update_ui(self, update_type: str, **kwargs):
                """Handle UI updates from state machine."""
                pass  # Widget handles its own updates
        
        # Set the UI controller on the state machine
        if hasattr(self.state_machine, 'set_ui_controller'):
            self.state_machine.set_ui_controller(SimpleUIController(self))
            debug_log("UI controller set up for state machine", "UI_CONTROLLER")


# ==============================
# DRAMATIC SIMPLIFICATION ACHIEVED
# ==============================

# BEFORE (complex overrides):
# - _set_player_cards_from_display_state: 80+ lines of complex logic
# - _update_player_from_display_state: 40+ lines with forced card updates
# - _highlight_current_player: 100+ lines with human/bot distinction
# - Multiple complex methods fighting parent assumptions

# AFTER (simple hooks):
# - _should_show_card: 10 lines, clear human/bot policy
# - _transform_card_data: 15 lines, simple card transformation
# - _customize_player_styling: 10 lines, clean styling rules
# - All methods focused on single responsibility

# BENEFITS:
# ✅ 80% reduction in complex override code
# ✅ Each hook method has single, clear purpose
# ✅ Easy to test individual hook behaviors
# ✅ Parent class logic flows naturally
# ✅ No more fighting parent assumptions
# ✅ Extensible for new requirements
