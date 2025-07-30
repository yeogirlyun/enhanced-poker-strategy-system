#!/usr/bin/env python3
"""
Professional Poker Table using Kivy

A state-of-the-art poker table with perfect centering, professional graphics,
and smooth animations for the ultimate poker experience.
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.metrics import dp

import math
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from enhanced_poker_engine import EnhancedPokerEngine, Player, GameState, Action, Position
from gui_models import StrategyData


class CardWidget(Widget):
    """Professional card widget with animations."""
    
    def __init__(self, rank="", suit="", face_up=True, **kwargs):
        super().__init__(**kwargs)
        self.rank = rank
        self.suit = suit
        self.face_up = face_up
        self.size_hint = (None, None)
        self.size = (dp(50), dp(70))
        
    def on_size(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Card background
            Color(1, 1, 1, 1) if self.face_up else Color(0.2, 0.2, 0.8, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Card border
            Color(0, 0, 0, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
            
            if self.face_up and self.rank and self.suit:
                # Card content
                suit_color = (1, 0, 0, 1) if self.suit in ['♥', '♦'] else (0, 0, 0, 1)
                Color(*suit_color)
                
                # Rank and suit
                label = Label(
                    text=f"{self.rank}{self.suit}",
                    pos=(self.x + self.width/2 - dp(15), self.y + self.height/2 - dp(10)),
                    size=(dp(30), dp(20)),
                    color=suit_color
                )
                label.texture_update()
                Rectangle(texture=label.texture, pos=label.pos, size=label.size)


class PlayerWidget(Widget):
    """Professional player widget with stack and position."""
    
    def __init__(self, name="", position="", stack=100, is_human=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.position = position
        self.stack = stack
        self.is_human = is_human
        self.cards = []
        self.size_hint = (None, None)
        self.size = (dp(80), dp(100))
        
    def on_size(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Player circle
            color = (1, 0.4, 0.4, 1) if self.is_human else (0.3, 0.8, 0.8, 1)
            Color(*color)
            Ellipse(pos=self.pos, size=self.size)
            
            # Player border
            Color(0, 0, 0, 1)
            Line(circle=(self.x + self.width/2, self.y + self.height/2, self.width/2), width=2)
            
            # Player name
            name_color = (1, 1, 1, 1)
            Color(*name_color)
            name_label = Label(
                text=self.name,
                pos=(self.x + self.width/2 - dp(20), self.y + self.height/2 + dp(10)),
                size=(dp(40), dp(20)),
                color=name_color
            )
            name_label.texture_update()
            Rectangle(texture=name_label.texture, pos=name_label.pos, size=name_label.size)
            
            # Position
            pos_label = Label(
                text=self.position,
                pos=(self.x + self.width/2 - dp(15), self.y + self.height/2 - dp(5)),
                size=(dp(30), dp(15)),
                color=name_color
            )
            pos_label.texture_update()
            Rectangle(texture=pos_label.texture, pos=pos_label.pos, size=pos_label.size)
            
            # Stack
            stack_label = Label(
                text=f"${self.stack:.0f}",
                pos=(self.x + self.width/2 - dp(20), self.y - dp(25)),
                size=(dp(40), dp(20)),
                color=name_color
            )
            stack_label.texture_update()
            Rectangle(texture=stack_label.texture, pos=stack_label.pos, size=stack_label.size)


class ActionButton(Button):
    """Professional action button with animations."""
    
    def __init__(self, text="", action_type="", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.action_type = action_type
        self.size_hint = (None, None)
        self.size = (dp(80), dp(40))
        
        # Set button colors based on action type
        if action_type == "fold":
            self.background_color = (0.8, 0.2, 0.2, 1)  # Red
        elif action_type == "check":
            self.background_color = (0.2, 0.6, 0.8, 1)  # Blue
        elif action_type == "bet":
            self.background_color = (0.2, 0.8, 0.2, 1)  # Green
        elif action_type == "raise":
            self.background_color = (0.8, 0.6, 0.2, 1)  # Orange
        else:
            self.background_color = (0.5, 0.5, 0.5, 1)  # Gray


class ProfessionalPokerTable(Widget):
    """Professional poker table with perfect centering."""
    
    def __init__(self, strategy_data: StrategyData, **kwargs):
        super().__init__(**kwargs)
        self.strategy_data = strategy_data
        self.engine = EnhancedPokerEngine(strategy_data)
        self.current_game_state = None
        
        # Table dimensions (perfect centering)
        self.table_color = (0.1, 0.4, 0.1, 1)  # Dark green felt
        self.border_color = (0.6, 0.4, 0.2, 1)  # Brown border
        self.pot_color = (1, 0.8, 0, 1)  # Gold pot
        
        # Player widgets
        self.player_widgets = []
        self.card_widgets = []
        
        # Action buttons
        self.action_buttons = []
        self._create_action_buttons()
        
        # Bind size changes
        self.bind(size=self._update_layout)
        
    def _create_action_buttons(self):
        """Create professional action buttons."""
        actions = [
            ("FOLD", "fold"),
            ("CHECK", "check"),
            ("CALL", "call"),
            ("BET", "bet"),
            ("RAISE", "raise")
        ]
        
        for text, action_type in actions:
            btn = ActionButton(text=text, action_type=action_type)
            btn.bind(on_press=lambda btn, action=action_type: self._on_action_pressed(action))
            self.action_buttons.append(btn)
            self.add_widget(btn)
    
    def _update_layout(self, *args):
        """Update layout with perfect centering."""
        # Calculate table dimensions
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.table_width = self.width * 0.75
        self.table_height = self.height * 0.65
        
        # Player radius
        self.player_radius = min(self.table_width, self.table_height) * 0.4
        
        # Update player positions
        self._update_player_positions()
        
        # Update action button positions
        self._update_action_buttons()
    
    def _update_player_positions(self):
        """Update player positions around the table."""
        if not self.player_widgets:
            return
            
        for i, player_widget in enumerate(self.player_widgets):
            # Calculate position around the table
            angle = (i * 2 * math.pi / len(self.player_widgets)) - math.pi / 2
            x = self.center_x + self.player_radius * math.cos(angle) - player_widget.width / 2
            y = self.center_y + self.player_radius * math.sin(angle) - player_widget.height / 2
            
            # Animate to new position
            anim = Animation(pos=(x, y), duration=0.3)
            anim.start(player_widget)
    
    def _update_action_buttons(self):
        """Update action button positions."""
        button_width = dp(80)
        button_height = dp(40)
        spacing = dp(10)
        total_width = len(self.action_buttons) * button_width + (len(self.action_buttons) - 1) * spacing
        start_x = self.center_x - total_width / 2
        
        for i, button in enumerate(self.action_buttons):
            x = start_x + i * (button_width + spacing)
            y = self.height * 0.1  # Bottom of screen
            button.pos = (x, y)
    
    def _on_action_pressed(self, action_type):
        """Handle action button press."""
        if not self.current_game_state:
            return
            
        # Find human player
        human_player = None
        for player in self.current_game_state.players:
            if player.is_human:
                human_player = player
                break
        
        if not human_player:
            return
        
        # Execute action
        action_map = {
            "fold": Action.FOLD,
            "check": Action.CHECK,
            "call": Action.CALL,
            "bet": Action.BET,
            "raise": Action.RAISE
        }
        
        action = action_map.get(action_type, Action.CHECK)
        self.engine.execute_action(human_player, action, 0, self.current_game_state)
        
        # Update display
        self._update_game_display()
    
    def start_new_hand(self, num_players=6):
        """Start a new hand with perfect centering."""
        # Clear previous widgets
        self._clear_widgets()
        
        # Create new hand
        result = self.engine.play_hand(num_players)
        self.current_game_state = self.engine.current_game_state
        
        # Create player widgets
        self._create_player_widgets()
        
        # Create card widgets
        self._create_card_widgets()
        
        # Update layout
        self._update_layout()
        
        # Animate cards dealing
        self._animate_card_dealing()
    
    def _clear_widgets(self):
        """Clear all game widgets."""
        for widget in self.player_widgets + self.card_widgets:
            self.remove_widget(widget)
        self.player_widgets.clear()
        self.card_widgets.clear()
    
    def _create_player_widgets(self):
        """Create professional player widgets."""
        if not self.current_game_state:
            return
            
        for i, player in enumerate(self.current_game_state.players):
            player_widget = PlayerWidget(
                name="You" if player.is_human else f"P{i+1}",
                position=player.position.value,
                stack=player.stack,
                is_human=player.is_human
            )
            self.player_widgets.append(player_widget)
            self.add_widget(player_widget)
    
    def _create_card_widgets(self):
        """Create professional card widgets."""
        if not self.current_game_state:
            return
            
        # Community cards
        for i, card in enumerate(self.current_game_state.board):
            card_widget = CardWidget(
                rank=card[0],
                suit=self._get_suit_symbol(card[1]),
                face_up=True
            )
            self.card_widgets.append(card_widget)
            self.add_widget(card_widget)
        
        # Player cards
        for i, player in enumerate(self.current_game_state.players):
            if player.cards:
                for j, card in enumerate(player.cards):
                    card_widget = CardWidget(
                        rank=card[0],
                        suit=self._get_suit_symbol(card[1]),
                        face_up=player.is_human or not player.is_active
                    )
                    self.card_widgets.append(card_widget)
                    self.add_widget(card_widget)
    
    def _get_suit_symbol(self, suit):
        """Convert suit to symbol."""
        suit_map = {
            'h': '♥',
            'd': '♦',
            'c': '♣',
            's': '♠'
        }
        return suit_map.get(suit, suit)
    
    def _animate_card_dealing(self):
        """Animate cards being dealt."""
        # Start cards off-screen
        for card_widget in self.card_widgets:
            card_widget.pos = (self.width + 100, self.height + 100)
        
        # Animate each card to its position
        for i, card_widget in enumerate(self.card_widgets):
            target_pos = self._get_card_position(i)
            anim = Animation(pos=target_pos, duration=0.5, delay=i * 0.1)
            anim.start(card_widget)
    
    def _get_card_position(self, card_index):
        """Get position for card widget."""
        # Community cards in center
        if card_index < 5:  # First 5 cards are community cards
            card_width = dp(50)
            spacing = dp(10)
            total_width = 5 * card_width + 4 * spacing
            start_x = self.center_x - total_width / 2
            x = start_x + card_index * (card_width + spacing)
            y = self.center_y - dp(35)
            return (x, y)
        
        # Player cards (simplified positioning)
        player_index = (card_index - 5) // 2
        card_in_player = (card_index - 5) % 2
        
        if player_index < len(self.player_widgets):
            player_widget = self.player_widgets[player_index]
            card_width = dp(50)
            spacing = dp(5)
            
            if card_in_player == 0:
                x = player_widget.x - card_width - spacing
            else:
                x = player_widget.x + player_widget.width + spacing
            
            y = player_widget.y + player_widget.height / 2 - dp(35)
            return (x, y)
        
        return (0, 0)
    
    def _update_game_display(self):
        """Update the game display."""
        # Update pot display
        if self.current_game_state:
            pot_text = f"Pot: ${self.current_game_state.pot:.0f}"
            # Update pot label (would need to be implemented)
    
    def on_size(self, *args):
        """Handle size changes with perfect centering."""
        self._update_layout()


class ProfessionalPokerApp(App):
    """Professional poker application."""
    
    def build(self):
        """Build the professional poker application."""
        # Load strategy
        strategy_data = StrategyData()
        strategy_data.load_strategy_from_file("modern_strategy.json")
        
        # Create main layout
        layout = FloatLayout()
        
        # Create poker table
        self.poker_table = ProfessionalPokerTable(strategy_data)
        layout.add_widget(self.poker_table)
        
        # Create control panel
        control_panel = self._create_control_panel()
        layout.add_widget(control_panel)
        
        # Start a hand
        Clock.schedule_once(lambda dt: self.poker_table.start_new_hand(6), 0.5)
        
        return layout
    
    def _create_control_panel(self):
        """Create professional control panel."""
        panel = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'x': 0, 'y': 0.9}
        )
        
        # Start hand button
        start_btn = Button(
            text="🎯 Start New Hand",
            size_hint=(0.2, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        start_btn.bind(on_press=self._start_new_hand)
        panel.add_widget(start_btn)
        
        # Player count
        player_count_btn = Button(
            text="Players: 6",
            size_hint=(0.15, 1),
            background_color=(0.8, 0.8, 0.8, 1)
        )
        panel.add_widget(player_count_btn)
        
        return panel
    
    def _start_new_hand(self, instance):
        """Start a new hand."""
        self.poker_table.start_new_hand(6)


if __name__ == "__main__":
    ProfessionalPokerApp().run() 