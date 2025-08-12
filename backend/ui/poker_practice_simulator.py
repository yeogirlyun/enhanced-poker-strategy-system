#!/usr/bin/env python3
"""
Poker Practice Simulator - UI Only Version

This version removes all game logic and delegates to the state machine.
The simulator now only handles UI display and strategy analysis.
"""

import tkinter as tk
from tkinter import ttk
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.flexible_poker_state_machine import ActionType, PokerState
from core.gui_models import StrategyData, THEME


@dataclass
class DeviationLog:
    """Logs strategy deviations for analysis."""
    hand_id: str
    player_name: str
    position: str
    street: str
    action_taken: str
    strategy_action: str
    deviation_type: str
    pot_size: float
    stack_size: float
    board: List[str]
    player_cards: List[str]
    timestamp: float


class PokerPracticeSimulator:
    """Main poker practice simulator - UI only, delegates to state machine."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.deviation_logs: List[DeviationLog] = []
        self.session_stats = {
            "hands_played": 0,
            "deviations": 0,
            "correct_plays": 0,
            "total_pot_won": 0.0,
            "total_pot_lost": 0.0
        }
        
        # Use state machine for all game logic
        self.state_machine = ImprovedPokerStateMachine(
            num_players=6, 
            strategy_data=self.strategy_data
        )
        
    def log_deviation(self, player_name: str, action_taken: str, strategy_action: str, 
                      game_info: Dict[str, Any]) -> None:
        """Log strategy deviation for analysis."""
        deviation_log = DeviationLog(
            hand_id=f"hand_{self.session_stats['hands_played']}",
            player_name=player_name,
            position=game_info.get("position", ""),
            street=game_info.get("street", ""),
            action_taken=action_taken,
            strategy_action=strategy_action,
            deviation_type="action_mismatch" if action_taken != strategy_action else "bet_size",
            pot_size=game_info.get("pot", 0.0),
            stack_size=game_info.get("stack", 0.0),
            board=game_info.get("board", []),
            player_cards=game_info.get("cards", []),
            timestamp=time.time()
        )
        self.deviation_logs.append(deviation_log)
        self.session_stats["deviations"] += 1
    
    def get_feedback_message(self, deviation_log: DeviationLog) -> str:
        """Generate feedback message for a deviation."""
        if deviation_log.deviation_type == "action_mismatch":
            return f"Strategy suggests {deviation_log.strategy_action} but you chose {deviation_log.action_taken}"
        else:
            return f"Action correct but bet size may need adjustment"
    
    def play_hand(self, num_players: int = 6) -> Dict[str, Any]:
        """Play a hand using the state machine."""
        # Reset state machine for new hand
        self.state_machine.start_hand()
        
        # Get game info from state machine
        game_info = self.state_machine.get_game_info()
        
        # Update session stats
        self.session_stats["hands_played"] += 1
        
        # Return game info for UI display
        return {
            "game_info": game_info,
            "session_stats": self.session_stats,
            "deviation_logs": self.deviation_logs
        }
    
    def get_session_report(self) -> Dict[str, Any]:
        """Generate session report."""
        return {
            "hands_played": self.session_stats["hands_played"],
            "deviations": self.session_stats["deviations"],
            "correct_plays": self.session_stats["correct_plays"],
            "accuracy": (self.session_stats["correct_plays"] / max(1, self.session_stats["hands_played"])) * 100,
            "total_pot_won": self.session_stats["total_pot_won"],
            "total_pot_lost": self.session_stats["total_pot_lost"],
            "deviation_logs": self.deviation_logs
        }


class PracticeSimulatorGUI:
    """GUI for the poker practice simulator."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.simulator = PokerPracticeSimulator(strategy_data)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Poker Practice Simulator")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME["bg"])
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Main title
        title_label = ttk.Label(
            self.root,
            text="🎰 Poker Practice Simulator",
            font=(THEME["font_family"], 20, "bold"),
            foreground=THEME["accent"]
        )
        title_label.pack(pady=20)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Game Configuration", style="Dark.TLabelframe")
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Number of players
        ttk.Label(config_frame, text="Number of Players:").pack(side=tk.LEFT, padx=10)
        self.player_count_var = tk.StringVar(value="6")
        player_count_combo = ttk.Combobox(
            config_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8", "9"],
            width=10,
            state="readonly"
        )
        player_count_combo.pack(side=tk.LEFT, padx=10)
        
        # Start new hand button
        start_button = ttk.Button(
            config_frame,
            text="Start New Hand",
            command=self.start_new_hand,
            style="Accent.TButton"
        )
        start_button.pack(side=tk.RIGHT, padx=10)
        
        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Game state
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Game state display
        state_frame = ttk.LabelFrame(left_panel, text="Game State", style="Dark.TLabelframe")
        state_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.game_state_text = tk.Text(
            state_frame,
            height=15,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=(THEME["font_family"], 10),
            relief="flat",
            state=tk.DISABLED
        )
        self.game_state_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Action frame
        action_frame = ttk.LabelFrame(left_panel, text="Your Action", style="Dark.TLabelframe")
        action_frame.pack(fill=tk.X, pady=10)
        
        # Action buttons
        actions_frame = ttk.Frame(action_frame)
        actions_frame.pack(pady=10)
        
        self.action_var = tk.StringVar(value="check")
        actions = [
            ("Fold", "fold"),
            ("Check", "check"),
            ("Call", "call"),
            ("Bet", "bet"),
            ("Raise", "raise")
        ]
        
        for text, value in actions:
            ttk.Radiobutton(
                actions_frame,
                text=text,
                variable=self.action_var,
                value=value
            ).pack(side=tk.LEFT, padx=5)
        
        # Bet size entry
        ttk.Label(action_frame, text="Bet Size:").pack(pady=5)
        self.bet_size_var = tk.StringVar(value="0")
        bet_size_entry = ttk.Entry(action_frame, textvariable=self.bet_size_var)
        bet_size_entry.pack(pady=5)
        
        # Submit button
        submit_button = ttk.Button(
            action_frame,
            text="Submit Action",
            command=self.submit_action,
            style="Accent.TButton"
        )
        submit_button.pack(pady=10)
        
        # Right panel - Feedback and stats
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Feedback display
        feedback_frame = ttk.LabelFrame(right_panel, text="Strategy Feedback", style="Dark.TLabelframe")
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.feedback_text = tk.Text(
            feedback_frame,
            height=8,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=(THEME["font_family"], 10),
            relief="flat",
            state=tk.DISABLED
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stats display
        stats_frame = ttk.LabelFrame(right_panel, text="Session Statistics", style="Dark.TLabelframe")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=8,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=(THEME["font_family"], 10),
            relief="flat",
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def start_new_hand(self):
        """Start a new hand using the state machine."""
        num_players = int(self.player_count_var.get())
        
        # Use state machine to start new hand
        self.simulator.state_machine.start_hand()
        
        # Update displays
        self.update_game_display()
        self.update_stats_display()
    
    def submit_action(self):
        """Submit player action to state machine."""
        action_str = self.action_var.get()
        bet_size = float(self.bet_size_var.get())
        
        # Map action string to ActionType
        action_map = {
            "fold": ActionType.FOLD,
            "check": ActionType.CHECK,
            "call": ActionType.CALL,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE
        }
        action = action_map.get(action_str, ActionType.CHECK)
        
        # Get current player from state machine
        player = self.simulator.state_machine.get_action_player()
        if player and player.is_human:
            # Execute action through state machine
            self.simulator.state_machine.execute_action(player, action, bet_size)
            
            # Update displays
            self.update_game_display()
            self.update_feedback_display()
    
    def update_game_display(self):
        """Update game state display from state machine."""
        game_info = self.simulator.state_machine.get_game_info()
        
        self.game_state_text.config(state=tk.NORMAL)
        self.game_state_text.delete(1.0, tk.END)
        
        # Display game info from state machine
        display_text = f"State: {game_info.get('state', 'Unknown')}\n"
        display_text += f"Pot: ${game_info.get('pot', 0):.2f}\n"
        display_text += f"Current Bet: ${game_info.get('current_bet', 0):.2f}\n"
        display_text += f"Board: {game_info.get('board', [])}\n\n"
        
        # Display players
        players = game_info.get('players', [])
        for i, player in enumerate(players):
            display_text += f"Player {i+1}: {player.get('name', 'Unknown')}\n"
            display_text += f"  Stack: ${player.get('stack', 0):.2f}\n"
            display_text += f"  Bet: ${player.get('current_bet', 0):.2f}\n"
            display_text += f"  Active: {player.get('is_active', False)}\n\n"
        
        self.game_state_text.insert(1.0, display_text)
        self.game_state_text.config(state=tk.DISABLED)
    
    def update_feedback_display(self):
        """Update feedback display."""
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        
        # Get feedback from state machine game info
        game_info = self.simulator.state_machine.get_game_info()
        valid_actions = game_info.get('valid_actions', {})
        
        feedback = "Valid Actions:\n"
        for action, is_valid in valid_actions.items():
            if isinstance(is_valid, bool) and is_valid:
                feedback += f"✓ {action.title()}\n"
        
        self.feedback_text.insert(1.0, feedback)
        self.feedback_text.config(state=tk.DISABLED)
    
    def update_stats_display(self):
        """Update statistics display."""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Get session info from state machine
        session_info = self.simulator.state_machine.get_session_info()
        
        stats_text = f"Session Duration: {session_info.get('session_duration', 0):.1f}s\n"
        stats_text += f"Hands Played: {session_info.get('hands_played', 0)}\n"
        stats_text += f"Human Wins: {session_info.get('human_wins', 0)}\n"
        stats_text += f"Human Losses: {session_info.get('human_losses', 0)}\n"
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    app = PracticeSimulatorGUI(strategy_data)
    app.run() 