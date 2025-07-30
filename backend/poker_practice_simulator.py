#!/usr/bin/env python3
"""
Poker Practice Simulator

A comprehensive poker practice system where you play against AI bots
that follow the strategy perfectly, with deviation tracking and feedback.

Features:
- Up to 8 players (1 human + 7 AI bots)
- Real-time strategy deviation tracking
- Session logging and analysis
- Perfect AI bot play based on strategy
- Stack and pot tracking
- Detailed feedback system
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox
from gui_models import StrategyData, THEME
from hand_evaluator import evaluate_hand_strength


class Action(Enum):
    """Poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class Position(Enum):
    """Poker positions."""
    SB = "SB"
    BB = "BB"
    UTG = "UTG"
    MP = "MP"
    CO = "CO"
    BTN = "BTN"


@dataclass
class Player:
    """Represents a poker player."""
    name: str
    position: Position
    stack: float
    is_human: bool = False
    is_active: bool = True
    current_bet: float = 0.0
    cards: List[str] = field(default_factory=list)
    last_action: Optional[Action] = None
    last_bet_size: float = 0.0


@dataclass
class GameState:
    """Current game state."""
    players: List[Player]
    pot: float = 0.0
    current_bet: float = 0.0
    board: List[str] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)
    current_player_index: int = 0
    street: str = "preflop"  # preflop, flop, turn, river
    dealer_position: int = 0
    small_blind: float = 1.0
    big_blind: float = 2.0


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
    """Main poker practice simulator."""
    
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
        
        # Initialize deck
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.suits = ["h", "d", "c", "s"]  # hearts, diamonds, clubs, spades
        
    def create_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        deck = []
        for rank in self.ranks:
            for suit in self.suits:
                deck.append(f"{rank}{suit}")
        return deck
    
    def shuffle_deck(self, deck: List[str]) -> List[str]:
        """Shuffle the deck."""
        random.shuffle(deck)
        return deck
    
    def deal_cards(self, game_state: GameState) -> None:
        """Deal cards to all players."""
        deck = self.create_deck()
        deck = self.shuffle_deck(deck)
        game_state.deck = deck
        
        # Deal 2 cards to each player
        for player in game_state.players:
            if player.is_active:
                player.cards = [deck.pop(), deck.pop()]
    
    def deal_board(self, game_state: GameState, street: str) -> None:
        """Deal board cards for the current street."""
        if street == "flop" and len(game_state.board) == 0:
            # Deal 3 cards for flop
            for _ in range(3):
                game_state.board.append(game_state.deck.pop())
        elif street in ["turn", "river"] and len(game_state.board) < 5:
            # Deal 1 card for turn/river
            game_state.board.append(game_state.deck.pop())
    
    def get_position_for_player(self, player_index: int, dealer_pos: int, num_players: int) -> Position:
        """Get position for a player based on dealer position."""
        positions = [Position.SB, Position.BB, Position.UTG, Position.MP, Position.MP, Position.CO, Position.BTN]
        
        # Calculate relative position to dealer
        relative_pos = (player_index - dealer_pos) % num_players
        
        # Map to position (adjust for number of players)
        if num_players == 2:
            return Position.BB if relative_pos == 0 else Position.SB
        elif num_players == 3:
            positions = [Position.SB, Position.BB, Position.BTN]
        elif num_players == 4:
            positions = [Position.SB, Position.BB, Position.UTG, Position.BTN]
        elif num_players == 5:
            positions = [Position.SB, Position.BB, Position.UTG, Position.MP, Position.BTN]
        elif num_players == 6:
            positions = [Position.SB, Position.BB, Position.UTG, Position.MP, Position.CO, Position.BTN]
        
        return positions[relative_pos]
    
    def evaluate_hand_strength(self, cards: List[str], board: List[str]) -> float:
        """Evaluate hand strength using proper hand evaluator."""
        return evaluate_hand_strength(cards, board)
    
    def get_strategy_action(self, player: Player, game_state: GameState) -> Tuple[Action, float]:
        """Get the strategy-recommended action for a player."""
        if not player.cards:
            return Action.FOLD, 0.0
        
        # Get hand strength
        hs = self.evaluate_hand_strength(player.cards, game_state.board)
        
        # Get position
        pos = player.position.value
        
        if game_state.street == "preflop":
            # Use preflop strategy
            open_rules = self.strategy_data.strategy_dict.get("preflop", {}).get("open_rules", {})
            if pos in open_rules:
                threshold = open_rules[pos]["threshold"]
                if hs >= threshold:
                    return Action.RAISE, open_rules[pos]["sizing"]
                else:
                    return Action.FOLD, 0.0
            return Action.FOLD, 0.0
        
        else:
            # Use postflop strategy
            postflop = self.strategy_data.strategy_dict.get("postflop", {})
            if "pfa" in postflop and game_state.street in postflop["pfa"]:
                street_rules = postflop["pfa"][game_state.street]
                if pos in street_rules:
                    val_thresh = street_rules[pos]["val_thresh"]
                    check_thresh = street_rules[pos]["check_thresh"]
                    sizing = street_rules[pos]["sizing"]
                    
                    if hs >= val_thresh:
                        return Action.BET, sizing
                    elif hs >= check_thresh:
                        return Action.CHECK, 0.0
                    else:
                        return Action.FOLD, 0.0
            
            return Action.CHECK, 0.0
    
    def log_deviation(self, player: Player, action_taken: Action, strategy_action: Action, 
                      game_state: GameState) -> None:
        """Log a strategy deviation."""
        deviation_log = DeviationLog(
            hand_id=f"hand_{self.session_stats['hands_played']}",
            player_name=player.name,
            position=player.position.value,
            street=game_state.street,
            action_taken=action_taken.value,
            strategy_action=strategy_action.value,
            deviation_type="action_mismatch" if action_taken != strategy_action else "bet_size",
            pot_size=game_state.pot,
            stack_size=player.stack,
            board=game_state.board.copy(),
            player_cards=player.cards.copy(),
            timestamp=time.time()
        )
        self.deviation_logs.append(deviation_log)
        self.session_stats["deviations"] += 1
    
    def get_feedback_message(self, deviation_log: DeviationLog) -> str:
        """Generate feedback message for a deviation."""
        if deviation_log.deviation_type == "action_mismatch":
            return f"Strategy recommended {deviation_log.strategy_action}, but you chose {deviation_log.action_taken}"
        else:
            return f"Bet sizing deviation - strategy recommended different sizing"
    
    def play_hand(self, num_players: int = 6) -> Dict[str, Any]:
        """Play a complete hand."""
        # Initialize players
        players = []
        for i in range(num_players):
            is_human = i == 0  # First player is human
            player = Player(
                name=f"Player {i+1}" if not is_human else "You",
                position=Position.UTG,  # Will be set correctly
                stack=100.0,
                is_human=is_human
            )
            players.append(player)
        
        # Initialize game state
        game_state = GameState(
            players=players,
            small_blind=1.0,
            big_blind=2.0
        )
        
        # Set positions
        for i, player in enumerate(players):
            player.position = self.get_position_for_player(i, 0, num_players)
        
        # Deal cards
        self.deal_cards(game_state)
        
        # Play preflop
        self.play_street(game_state, "preflop")
        
        # Deal and play postflop streets
        for street in ["flop", "turn", "river"]:
            if len([p for p in players if p.is_active]) > 1:
                self.deal_board(game_state, street)
                game_state.street = street
                self.play_street(game_state, street)
        
        # Determine winner (simplified)
        winner = self.determine_winner(game_state)
        
        # Update stats
        self.session_stats["hands_played"] += 1
        if winner.is_human:
            self.session_stats["total_pot_won"] += game_state.pot
        else:
            self.session_stats["total_pot_lost"] += game_state.pot
        
        return {
            "winner": winner.name,
            "pot": game_state.pot,
            "deviations": len([log for log in self.deviation_logs if log.hand_id == f"hand_{self.session_stats['hands_played']-1}"])
        }
    
    def play_street(self, game_state: GameState, street: str) -> None:
        """Play a single street (preflop, flop, turn, river)."""
        # Reset betting for new street
        game_state.current_bet = 0.0
        for player in game_state.players:
            player.current_bet = 0.0
        
        # Play betting rounds
        active_players = [p for p in game_state.players if p.is_active]
        current_player_idx = 0
        
        while len(active_players) > 1:
            current_player = active_players[current_player_idx]
            
            if current_player.is_human:
                # Human player - get action from UI
                action, bet_size = self.get_human_action(current_player, game_state)
            else:
                # AI player - follow strategy perfectly
                action, bet_size = self.get_strategy_action(current_player, game_state)
            
            # Execute action
            self.execute_action(current_player, action, bet_size, game_state)
            
            # Log deviation if human player
            if current_player.is_human:
                strategy_action, strategy_bet = self.get_strategy_action(current_player, game_state)
                if action != strategy_action:
                    self.log_deviation(current_player, action, strategy_action, game_state)
            
            # Move to next player
            current_player_idx = (current_player_idx + 1) % len(active_players)
            
            # Check if betting round is complete
            if self.is_betting_round_complete(active_players):
                break
    
    def get_human_action(self, player: Player, game_state: GameState) -> Tuple[Action, float]:
        """Get action from human player (placeholder for UI integration)."""
        # This will be implemented with the UI
        # For now, return a default action
        return Action.CHECK, 0.0
    
    def execute_action(self, player: Player, action: Action, bet_size: float, game_state: GameState) -> None:
        """Execute a player's action."""
        if action == Action.FOLD:
            player.is_active = False
        elif action == Action.CHECK:
            pass  # No action needed
        elif action in [Action.CALL, Action.BET, Action.RAISE]:
            call_amount = game_state.current_bet - player.current_bet
            if action == Action.CALL:
                bet_amount = call_amount
            else:
                bet_amount = bet_size
            
            if bet_amount >= player.stack:
                bet_amount = player.stack
                action = Action.ALL_IN
            
            player.stack -= bet_amount
            player.current_bet += bet_amount
            game_state.pot += bet_amount
            game_state.current_bet = max(game_state.current_bet, player.current_bet)
        
        player.last_action = action
        player.last_bet_size = bet_size
    
    def is_betting_round_complete(self, active_players: List[Player]) -> bool:
        """Check if betting round is complete."""
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have bet the same amount
        bet_amounts = [p.current_bet for p in active_players]
        return len(set(bet_amounts)) == 1
    
    def determine_winner(self, game_state: GameState) -> Player:
        """Determine the winner (simplified)."""
        active_players = [p for p in game_state.players if p.is_active]
        if len(active_players) == 1:
            return active_players[0]
        
        # Simplified winner determination
        # In a real implementation, you'd use a proper hand evaluator
        return active_players[0]  # Placeholder
    
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
        self.current_game_state: Optional[GameState] = None
        
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
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly"
        )
        player_count_combo.pack(side=tk.LEFT, padx=10)
        
        # Start button
        start_button = ttk.Button(
            config_frame,
            text="Start New Hand",
            command=self.start_new_hand
        )
        start_button.pack(side=tk.RIGHT, padx=10)
        
        # Game area
        game_frame = ttk.Frame(self.root)
        game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Game state
        left_panel = ttk.Frame(game_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Game state display
        self.game_state_text = tk.Text(
            left_panel,
            height=15,
            width=50,
            font=("Consolas", 10),
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            state=tk.DISABLED
        )
        self.game_state_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Action controls and feedback
        right_panel = ttk.Frame(game_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Action frame
        action_frame = ttk.LabelFrame(right_panel, text="Your Action", style="Dark.TLabelframe")
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
            ).pack(anchor=tk.W, pady=2)
        
        # Bet size entry
        ttk.Label(action_frame, text="Bet Size:").pack(pady=5)
        self.bet_size_var = tk.StringVar(value="0")
        bet_size_entry = ttk.Entry(action_frame, textvariable=self.bet_size_var)
        bet_size_entry.pack(pady=5)
        
        # Submit action button
        submit_button = ttk.Button(
            action_frame,
            text="Submit Action",
            command=self.submit_action
        )
        submit_button.pack(pady=10)
        
        # Feedback frame
        feedback_frame = ttk.LabelFrame(right_panel, text="Strategy Feedback", style="Dark.TLabelframe")
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.feedback_text = tk.Text(
            feedback_frame,
            height=10,
            font=("Consolas", 9),
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            state=tk.DISABLED
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Session stats frame
        stats_frame = ttk.LabelFrame(right_panel, text="Session Statistics", style="Dark.TLabelframe")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=6,
            font=("Consolas", 9),
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def start_new_hand(self):
        """Start a new hand."""
        num_players = int(self.player_count_var.get())
        result = self.simulator.play_hand(num_players)
        
        # Update display
        self.update_game_display()
        self.update_stats_display()
        
        messagebox.showinfo("Hand Complete", f"Winner: {result['winner']}\nPot: ${result['pot']:.2f}\nDeviations: {result['deviations']}")
    
    def submit_action(self):
        """Submit human player action."""
        if not self.current_game_state:
            messagebox.showwarning("No Active Hand", "Please start a new hand first.")
            return
        
        # Get action from UI
        action_str = self.action_var.get()
        bet_size = float(self.bet_size_var.get())
        
        action_map = {
            "fold": Action.FOLD,
            "check": Action.CHECK,
            "call": Action.CALL,
            "bet": Action.BET,
            "raise": Action.RAISE
        }
        
        action = action_map.get(action_str, Action.CHECK)
        
        # Execute action
        human_player = next(p for p in self.current_game_state.players if p.is_human)
        self.simulator.execute_action(human_player, action, bet_size, self.current_game_state)
        
        # Update display
        self.update_game_display()
        self.update_feedback_display()
    
    def update_game_display(self):
        """Update the game state display."""
        if not self.current_game_state:
            return
        
        display_text = "🎰 GAME STATE\n"
        display_text += "=" * 50 + "\n\n"
        
        # Players
        display_text += "PLAYERS:\n"
        for player in self.current_game_state.players:
            status = "ACTIVE" if player.is_active else "FOLDED"
            display_text += f"{player.name} ({player.position.value}): ${player.stack:.2f} - {status}\n"
        
        display_text += f"\nPOT: ${self.current_game_state.pot:.2f}\n"
        display_text += f"STREET: {self.current_game_state.street.upper()}\n"
        
        if self.current_game_state.board:
            display_text += f"BOARD: {' '.join(self.current_game_state.board)}\n"
        
        # Human player cards
        human_player = next(p for p in self.current_game_state.players if p.is_human)
        if human_player.cards:
            display_text += f"YOUR CARDS: {' '.join(human_player.cards)}\n"
        
        self.game_state_text.config(state=tk.NORMAL)
        self.game_state_text.delete(1.0, tk.END)
        self.game_state_text.insert(1.0, display_text)
        self.game_state_text.config(state=tk.DISABLED)
    
    def update_feedback_display(self):
        """Update the feedback display."""
        if not self.simulator.deviation_logs:
            return
        
        # Get latest deviation
        latest_deviation = self.simulator.deviation_logs[-1]
        feedback = self.simulator.get_feedback_message(latest_deviation)
        
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.insert(1.0, f"📊 FEEDBACK\n{'='*30}\n\n{feedback}")
        self.feedback_text.config(state=tk.DISABLED)
    
    def update_stats_display(self):
        """Update the session statistics display."""
        report = self.simulator.get_session_report()
        
        stats_text = "📈 SESSION STATS\n"
        stats_text += "=" * 30 + "\n"
        stats_text += f"Hands Played: {report['hands_played']}\n"
        stats_text += f"Deviations: {report['deviations']}\n"
        stats_text += f"Accuracy: {report['accuracy']:.1f}%\n"
        stats_text += f"Pot Won: ${report['total_pot_won']:.2f}\n"
        stats_text += f"Pot Lost: ${report['total_pot_lost']:.2f}\n"
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Load strategy data
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    # Create and run simulator
    simulator_gui = PracticeSimulatorGUI(strategy_data)
    simulator_gui.run() 