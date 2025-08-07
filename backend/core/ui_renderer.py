"""
UI Display Renderer for Poker State Machine

This module handles UI-ready display state generation and rendering logic
for the poker game interface.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import math

# Import shared types
from .types import GameState, Player, PokerState, ActionType


@dataclass
class DisplayState:
    """UI-ready display state with pre-computed visual data."""
    valid_actions: Dict[str, Dict[str, Any]]  # Button states and labels
    player_highlights: List[bool]  # Index-based list for highlighting
    card_visibilities: List[bool]  # Per-player: True if cards should be shown
    chip_representations: Dict[str, str]  # Chip symbols for stacks and pots
    layout_positions: Dict[str, Tuple[int, int]]  # UI positions
    community_cards: List[str]  # Current board cards (preserved during showdown)
    pot_amount: float  # Current pot amount
    current_bet: float  # Current bet amount
    action_player_index: int  # Index of current action player
    game_state: str  # Current game state string
    last_action_details: str  # Last action for UI feedback


class UIDisplayRenderer:
    """Handles UI-ready display state generation."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height

    def get_display_state(self, game_state: GameState, current_state: PokerState, 
                         action_player_index: int, last_action_details: str = "") -> DisplayState:
        """
        Generate UI-ready display state.
        
        Args:
            game_state: Current game state
            current_state: Current poker state
            action_player_index: Index of current action player
            last_action_details: Details of last action for UI feedback
            
        Returns:
            DisplayState object with all UI data
        """
        # Generate valid actions for each player
        valid_actions = self._generate_valid_actions(game_state, action_player_index)
        
        # Generate player highlights
        player_highlights = [i == action_player_index for i in range(len(game_state.players))]
        
        # Generate card visibilities
        card_visibilities = self._generate_card_visibilities(game_state, current_state)
        
        # Generate chip representations
        chip_representations = self._generate_chip_representations(game_state)
        
        # Generate layout positions
        layout_positions = self._compute_layout_positions(len(game_state.players))
        
        return DisplayState(
            valid_actions=valid_actions,
            player_highlights=player_highlights,
            card_visibilities=card_visibilities,
            chip_representations=chip_representations,
            layout_positions=layout_positions,
            community_cards=game_state.board.copy(),
            pot_amount=game_state.pot,
            current_bet=game_state.current_bet,
            action_player_index=action_player_index,
            game_state=current_state.value,
            last_action_details=last_action_details
        )

    def _generate_valid_actions(self, game_state: GameState, action_player_index: int) -> Dict[str, Dict[str, Any]]:
        """Generate valid actions for each player."""
        valid_actions = {}
        
        for i, player in enumerate(game_state.players):
            if not player.is_active:
                valid_actions[player.name] = {"fold": False, "check": False, "call": False, "bet": False, "raise": False}
                continue
            
            # Only show actions for current action player
            if i != action_player_index:
                valid_actions[player.name] = {"fold": False, "check": False, "call": False, "bet": False, "raise": False}
                continue
            
            # Calculate call amount
            call_amount = game_state.current_bet - player.current_bet
            
            # Determine valid actions
            actions = {
                "fold": True,  # Always available
                "check": call_amount == 0,
                "call": call_amount > 0 and call_amount <= player.stack,
                "bet": call_amount == 0 and player.stack > 0,
                "raise": call_amount > 0 and player.stack > call_amount
            }
            
            valid_actions[player.name] = actions
        
        return valid_actions

    def _generate_card_visibilities(self, game_state: GameState, current_state: PokerState) -> List[bool]:
        """Generate card visibility flags for each player."""
        visibilities = []
        
        for player in game_state.players:
            # Show cards if player is human or if we're in showdown/end_hand
            should_show = (player.is_human or 
                          current_state in [PokerState.SHOWDOWN, PokerState.END_HAND])
            visibilities.append(should_show)
        
        return visibilities

    def _generate_chip_representations(self, game_state: GameState) -> Dict[str, str]:
        """Generate chip symbol representations for stacks and pots."""
        representations = {}
        
        # Player stacks
        for player in game_state.players:
            representations[f"{player.name}_stack"] = self._get_chip_symbols(player.stack)
            if player.current_bet > 0:
                representations[f"{player.name}_bet"] = self._get_chip_symbols(player.current_bet)
        
        # Pot
        representations["pot"] = self._get_pot_chip_symbols(game_state.pot)
        
        return representations

    def _get_chip_symbols(self, amount: float) -> str:
        """Convert amount to chip symbol representation."""
        if amount <= 0:
            return ""
        
        # Simple chip representation
        chip_count = self._calculate_chip_count(amount)
        if chip_count <= 5:
            return "🟡" * chip_count
        elif chip_count <= 10:
            return "🟡" * 5 + "🔴" * (chip_count - 5)
        else:
            return "🟡" * 5 + "🔴" * 5 + "🟢" * (chip_count - 10)

    def _get_pot_chip_symbols(self, amount: float) -> str:
        """Convert pot amount to chip symbol representation."""
        if amount <= 0:
            return ""
        
        chip_count = self._calculate_pot_chip_count(amount)
        if chip_count <= 3:
            return "🟡" * chip_count
        elif chip_count <= 8:
            return "🟡" * 3 + "🔴" * (chip_count - 3)
        else:
            return "🟡" * 3 + "🔴" * 5 + "🟢" * (chip_count - 8)

    def _calculate_chip_count(self, amount: float) -> int:
        """Calculate number of chips to represent an amount."""
        if amount <= 0:
            return 0
        
        # Simple scaling: 1 chip per $1, max 20 chips
        chip_count = min(20, max(1, int(amount)))
        return chip_count

    def _calculate_pot_chip_count(self, amount: float) -> int:
        """Calculate number of chips to represent pot amount."""
        if amount <= 0:
            return 0
        
        # Pot chips scale differently: 1 chip per $2, max 15 chips
        chip_count = min(15, max(1, int(amount / 2)))
        return chip_count

    def _compute_layout_positions(self, num_players: int) -> Dict[str, Tuple[int, int]]:
        """
        Compute UI positions for players around the poker table.
        
        Args:
            num_players: Number of players in the game
            
        Returns:
            Dictionary mapping player names to (x, y) positions
        """
        positions = {}
        
        # Table dimensions
        table_width = self.width * 0.8
        table_height = self.height * 0.6
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Player positions around oval table
        for i in range(num_players):
            # Calculate angle for this player
            angle = (2 * math.pi * i) / num_players - math.pi / 2  # Start from top
            
            # Calculate position on oval
            radius_x = table_width / 2 * 0.8
            radius_y = table_height / 2 * 0.8
            
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            # Store position
            positions[f"Player {i+1}"] = (int(x), int(y))
        
        return positions

    def get_player_position_name(self, index: int, num_players: int) -> str:
        """Get position name for player index."""
        if num_players == 6:
            positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        elif num_players == 5:
            positions = ["BTN", "SB", "BB", "UTG", "MP"]
        elif num_players == 4:
            positions = ["BTN", "SB", "BB", "UTG"]
        else:
            positions = ["BTN", "SB", "BB"]
        
        return positions[index] if index < len(positions) else f"P{index}"

    def format_action_label(self, action: ActionType, amount: float) -> str:
        """Format action for UI display."""
        if action == ActionType.FOLD:
            return "Fold"
        elif action == ActionType.CHECK:
            return "Check"
        elif action == ActionType.CALL:
            return f"Call ${amount:.2f}"
        elif action == ActionType.BET:
            return f"Bet ${amount:.2f}"
        elif action == ActionType.RAISE:
            return f"Raise ${amount:.2f}"
        else:
            return str(action.value).title()

    def get_game_state_display_name(self, state: PokerState) -> str:
        """Get human-readable game state name."""
        state_names = {
            PokerState.START_HAND: "Starting Hand",
            PokerState.PREFLOP_BETTING: "Preflop Betting",
            PokerState.DEAL_FLOP: "Dealing Flop",
            PokerState.FLOP_BETTING: "Flop Betting",
            PokerState.DEAL_TURN: "Dealing Turn",
            PokerState.TURN_BETTING: "Turn Betting",
            PokerState.DEAL_RIVER: "Dealing River",
            PokerState.RIVER_BETTING: "River Betting",
            PokerState.SHOWDOWN: "Showdown",
            PokerState.END_HAND: "Hand Complete"
        }
        return state_names.get(state, state.value.replace("_", " ").title())
