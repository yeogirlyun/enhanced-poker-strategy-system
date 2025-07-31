#!/usr/bin/env python3
"""
Professional Poker Table GUI

A canvas-based poker table with professional graphics, animations, and sound effects.
Provides a realistic poker table experience with player seats, dealer button, and community cards.
"""

import tkinter as tk
from tkinter import ttk
import math
import time
from typing import List, Dict, Optional

from sound_manager import SoundManager


class ProfessionalPokerTableGUI:
    """
    A professional, canvas-based GUI for the poker game.
    Features a realistic poker table with animations and sound effects.
    """
    
    def __init__(self, strategy_data, num_players: int = 6):
        self.root = tk.Toplevel()
        self.root.title("Professional Poker Table")
        self.root.configure(bg="black")
        
        # Set window size and center it
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.strategy_data = strategy_data
        self.num_players = num_players
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Initialize poker engine
        try:
            from enhanced_poker_engine import EnhancedPokerEngine
            self.engine = EnhancedPokerEngine(strategy_data)
            self.engine_available = True
        except ImportError:
            print("⚠️  EnhancedPokerEngine not available. Using simulation mode.")
            self.engine_available = False
        
        # --- UI Elements ---
        self.canvas = tk.Canvas(
            self.root, 
            width=1100, 
            height=700, 
            bg="#015939", 
            highlightthickness=0
        )
        self.canvas.pack(pady=20, padx=20)
        
        # Game state
        self.player_seats = []
        self.community_card_labels = []
        self.dealer_button = None
        self.current_dealer = 0
        self.pot_amount = 0.0
        
        # Animation state
        self.animations = []
        
        self._draw_table()
        self._setup_player_seats()
        self._setup_community_card_area()
        self._setup_pot_display()
        self._setup_dealer_button()
        self._setup_controls()
        
        # Start with dealer at position 0
        self.move_dealer_button(0)

    def _draw_table(self):
        """Draws the main poker table shape with professional styling."""
        # Outer darker ellipse (table rim)
        self.canvas.create_oval(
            50, 50, 1050, 650, 
            fill="#013f28", 
            outline="#555555", 
            width=12
        )
        
        # Inner felt ellipse (playing surface)
        self.canvas.create_oval(
            62, 62, 1038, 638, 
            fill="#015939", 
            outline="#222222", 
            width=3
        )
        
        # Table center decoration
        self.canvas.create_oval(
            480, 320, 620, 380, 
            fill="#013f28", 
            outline="#222222", 
            width=2
        )
        
        # Add some professional details
        self.canvas.create_text(
            550, 350, 
            text="POKER", 
            fill="#4CAF50", 
            font=("Arial", 16, "bold")
        )

    def _setup_player_seats(self):
        """Creates and positions the player seats around the table."""
        center_x, center_y = 550, 350
        radius_x, radius_y = 420, 270
        
        # Position angles for 6 players (adjust for different numbers)
        angles = [
            math.pi * 1.5,    # Bottom center (seat 0)
            math.pi * 1.85,   # Bottom left (seat 1)
            math.pi * 0.15,   # Top left (seat 2)
            math.pi * 0.5,    # Top center (seat 3)
            math.pi * 0.85,   # Top right (seat 4)
            math.pi * 1.15,   # Bottom right (seat 5)
        ]
        
        for i in range(self.num_players):
            angle = angles[i] if i < len(angles) else (2 * math.pi / self.num_players) * i
            
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            self._create_player_seat(x, y, f"Player {i+1}", i)

    def _create_player_seat(self, x: float, y: float, name: str, player_index: int):
        """Creates the widgets for a single player seat."""
        # Create seat background
        seat_frame = tk.Frame(
            self.canvas, 
            bg="#222222", 
            bd=3, 
            relief="ridge",
            padx=10,
            pady=5
        )
        
        # Player name
        name_label = tk.Label(
            seat_frame, 
            text=name, 
            bg="#222222", 
            fg="white", 
            font=("Arial", 12, "bold")
        )
        name_label.pack(pady=(5, 2))
        
        # Stack amount
        stack_label = tk.Label(
            seat_frame, 
            text="$100.00", 
            bg="#222222", 
            fg="#4CAF50", 
            font=("Arial", 11, "bold")
        )
        stack_label.pack()
        
        # Player cards (placeholder)
        cards_label = tk.Label(
            seat_frame, 
            text="🂠 🂠", 
            bg="#222222", 
            fg="#CCCCCC", 
            font=("Arial", 24)
        )
        cards_label.pack(pady=5)
        
        # Action display
        action_label = tk.Label(
            seat_frame, 
            text="", 
            bg="#222222", 
            fg="yellow", 
            font=("Arial", 12, "italic")
        )
        action_label.pack(pady=(2, 5))
        
        # Bet amount
        bet_label = tk.Label(
            seat_frame, 
            text="", 
            bg="#222222", 
            fg="#FFD700", 
            font=("Arial", 10)
        )
        bet_label.pack()
        
        # Position the seat on canvas
        self.canvas.create_window(x, y, window=seat_frame)
        
        # Store seat information
        self.player_seats.append({
            "frame": seat_frame,
            "name": name_label,
            "stack": stack_label,
            "cards": cards_label,
            "action": action_label,
            "bet": bet_label,
            "index": player_index,
            "active": True,
            "stack_amount": 100.0,
            "current_bet": 0.0
        })

    def _setup_community_card_area(self):
        """Creates labels for the community cards."""
        card_positions = [
            (360, 350), (430, 350), (500, 350), (570, 350), (640, 350)
        ]
        
        for i, (x, y) in enumerate(card_positions):
            card_label = tk.Label(
                self.canvas, 
                text="", 
                bg="#015939", 
                fg="white", 
                font=("Arial", 28, "bold"), 
                bd=2, 
                relief="groove",
                width=3,
                height=2
            )
            self.canvas.create_window(x, y, window=card_label, width=60, height=90)
            self.community_card_labels.append(card_label)

    def _setup_pot_display(self):
        """Creates the text display for the pot."""
        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            bg="#013f28", 
            fg="yellow", 
            font=("Arial", 16, "bold"),
            bd=2,
            relief="raised",
            padx=10,
            pady=5
        )
        self.canvas.create_window(550, 480, window=self.pot_label)

    def _setup_dealer_button(self):
        """Creates the dealer button."""
        self.dealer_button_oval = None
        self.dealer_button_text = None

    def _setup_controls(self):
        """Setup control buttons."""
        control_frame = tk.Frame(self.root, bg="black")
        control_frame.pack(pady=10)
        
        # Action buttons
        tk.Button(
            control_frame, 
            text="Deal Cards", 
            command=self._deal_cards,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame, 
            text="Next Dealer", 
            command=self._next_dealer,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame, 
            text="Test Actions", 
            command=self._test_actions,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

    def move_dealer_button(self, player_index: int):
        """Moves the dealer button to the specified player."""
        if not 0 <= player_index < len(self.player_seats):
            return
            
        # Remove existing dealer button
        if self.dealer_button_oval:
            self.canvas.delete(self.dealer_button_oval)
        if self.dealer_button_text:
            self.canvas.delete(self.dealer_button_text)
        
        # Get player seat position
        seat_x, seat_y = self.canvas.coords(self.player_seats[player_index]["frame"])
        
        # Position button near the player
        button_x = seat_x + 60
        button_y = seat_y - 40
        
        # Create new dealer button
        self.dealer_button_oval = self.canvas.create_oval(
            button_x-15, button_y-15, 
            button_x+15, button_y+15, 
            fill="white", 
            outline="black", 
            width=2
        )
        self.dealer_button_text = self.canvas.create_text(
            button_x, button_y, 
            text="D", 
            font=("Arial", 14, "bold"),
            fill="black"
        )
        
        self.current_dealer = player_index
        self.sound_manager.play("button_move")

    def update_player_action(self, player_index: int, action_text: str, amount: Optional[float] = None):
        """Displays an action (like 'Call' or 'Bet') at a player's seat."""
        if not 0 <= player_index < len(self.player_seats):
            return
            
        action_label = self.player_seats[player_index]["action"]
        
        if amount:
            display_text = f"{action_text.upper()}\n${amount:.2f}"
        else:
            display_text = action_text.upper()
            
        action_label.config(text=display_text)
        
        # Play appropriate sound
        sound_map = {
            "call": "player_call",
            "bet": "chip_bet", 
            "raise": "chip_bet",
            "fold": "player_fold",
            "check": "player_check"
        }
        
        action_lower = action_text.lower()
        if action_lower in sound_map:
            self.sound_manager.play(sound_map[action_lower])
        
        # Fade-out animation
        def fade_out(alpha):
            if alpha > 0:
                # Create fade effect by changing foreground color
                intensity = int(alpha * 255)
                hex_color = f"#{intensity:02x}{intensity:02x}{0:02x}"
                action_label.config(fg=hex_color)
                self.root.after(50, fade_out, alpha - 0.05)
            else:
                action_label.config(text="")
                action_label.config(fg="yellow")  # Reset color

        # Start fade-out after 2 seconds
        self.root.after(2000, fade_out, 1.0)

    def update_player_bet(self, player_index: int, amount: float):
        """Updates a player's bet amount."""
        if not 0 <= player_index < len(self.player_seats):
            return
            
        bet_label = self.player_seats[player_index]["bet"]
        if amount > 0:
            bet_label.config(text=f"Bet: ${amount:.2f}")
        else:
            bet_label.config(text="")

    def update_pot(self, amount: float):
        """Updates the pot amount."""
        self.pot_amount = amount
        self.pot_label.config(text=f"Pot: ${amount:.2f}")

    def update_community_cards(self, cards: List[str]):
        """Updates the community cards display."""
        for i, card in enumerate(cards):
            if i < len(self.community_card_labels):
                self.community_card_labels[i].config(text=card)

    def _deal_cards(self):
        """Deal cards using the poker engine."""
        self.sound_manager.play("card_deal")
        
        if self.engine_available:
            try:
                # Use the poker engine to deal cards
                game_state = self.engine.deal_new_hand()
                
                # Update player cards
                for i, player in enumerate(game_state.players):
                    if i < len(self.player_seats):
                        cards = " ".join(player.cards) if player.cards else "🂠 🂠"
                        self.player_seats[i]["cards"].config(text=cards)
                
                # Update community cards
                if hasattr(game_state, 'community_cards') and game_state.community_cards:
                    self.update_community_cards(game_state.community_cards)
                
                print("🎴 Cards dealt using poker engine!")
                
            except Exception as e:
                print(f"⚠️  Error using poker engine: {e}")
                self._deal_cards_simulation()
        else:
            self._deal_cards_simulation()
    
    def _deal_cards_simulation(self):
        """Fallback simulation for dealing cards."""
        import random
        cards = ["Ah", "Ks", "Qd", "Jc", "Th", "9s", "8d", "7c", "6h", "5s"]
        for i in range(self.num_players):
            if i < len(self.player_seats):
                card1 = random.choice(cards)
                card2 = random.choice(cards)
                self.player_seats[i]["cards"].config(text=f"{card1} {card2}")
        print("🎴 Cards dealt (simulation mode)!")

    def _next_dealer(self):
        """Moves to the next dealer."""
        next_dealer = (self.current_dealer + 1) % self.num_players
        self.move_dealer_button(next_dealer)
        print(f"🎯 Dealer moved to Player {next_dealer + 1}")

    def _test_actions(self):
        """Test various player actions."""
        import random
        
        # Test random actions
        actions = ["Call", "Bet", "Raise", "Fold", "Check"]
        for i in range(self.num_players):
            action = random.choice(actions)
            amount = random.randint(10, 100) if action in ["Bet", "Raise"] else None
            self.update_player_action(i, action, amount)
            self.update_player_bet(i, amount if amount else 0)
        
        # Update pot
        self.update_pot(random.randint(50, 500))

    def run(self):
        """Run the poker table GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Test the poker table
    from gui_models import StrategyData
    
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    table = ProfessionalPokerTableGUI(strategy_data)
    table.run() 