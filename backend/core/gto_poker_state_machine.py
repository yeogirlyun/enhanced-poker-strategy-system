"""
GTO Poker State Machine

This module provides a poker state machine specifically designed for GTO simulation
where all players are GTO bots. It extends FlexiblePokerStateMachine to provide
pure bot vs bot gameplay with detailed GTO decision explanations.
"""

from typing import List, Dict, Any, Optional, Tuple
from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig
from .types import Player, ActionType
from .improved_gto_strategy import ImprovedGTOStrategy


class GTOPokerStateMachine(FlexiblePokerStateMachine):
    """
    GTO Poker State Machine for pure bot vs bot simulation.
    
    This state machine:
    - Handles only GTO bot players (no human players)
    - Provides detailed GTO decision explanations
    - Simulates realistic GTO gameplay
    - Tracks decision reasoning for educational purposes
    """
    
    def __init__(self, config: GameConfig, mode: str = "live"):
        """Initialize the GTO poker state machine."""
        super().__init__(config, mode)
        
        # GTO-specific attributes
        self.gto_strategies: Dict[int, ImprovedGTOStrategy] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.current_decision_explanation: str = ""
        
        # Sound manager for audio feedback
        self.sound_manager = None
 
        # Ensure dealing states auto-advance to betting rounds like practice session
        try:
            setattr(self.config, "auto_advance", True)
        except Exception:
            pass

        # Initialize GTO strategies for all players
        self._initialize_gto_strategies()
    
    def _initialize_gto_strategies(self):
        """Initialize GTO strategy engines for all players."""
        for i, player in enumerate(self.game_state.players):
            strategy = ImprovedGTOStrategy(self.config.num_players)
            self.gto_strategies[i] = strategy
    
    def start_new_hand(self) -> bool:
        """Start a new hand with all GTO bot players."""
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "GTO_SIMULATION", 
                "Starting new GTO simulation hand",
                {"num_players": self.config.num_players, 
                 "stack_size": self.config.starting_stack}
            )
        
        # Clear decision history for new hand
        self.decision_history.clear()
        self.current_decision_explanation = ""
        
        # Call parent method to set up the hand
        success = super().start_hand()
        
        if success:
            # Set up GTO bot players with proper names
            self._setup_gto_bot_players()
            
            # Log hand start
            if self.session_logger:
                self.session_logger.log_system(
                    "INFO", "GTO_SIMULATION",
                    f"GTO hand started: {len(self.game_state.players)} players, "
                    f"pot: ${self.game_state.pot}",
                    {"dealer": self.game_state.dealer_position}
                )
        
        return success
    
    def _setup_gto_bot_players(self):
        """Set up GTO bot players with proper names and positions."""
        gto_bot_names = [
            "GTO_Bot_Alpha", "GTO_Bot_Beta", "GTO_Bot_Gamma", "GTO_Bot_Delta",
            "GTO_Bot_Epsilon", "GTO_Bot_Zeta", "GTO_Bot_Eta", "GTO_Bot_Theta",
            "GTO_Bot_Iota", "GTO_Bot_Kappa", "GTO_Bot_Lambda", "GTO_Bot_Mu"
        ]
        
        for i, player in enumerate(self.game_state.players):
            # Assign GTO bot name
            player.name = gto_bot_names[i % len(gto_bot_names)]
            
            # Set position name
            player.position = self._get_position_name(i, self.config.num_players)
            
            # Reset player state for new hand
            player.cards = []
            player.current_bet = 0.0
            player.has_folded = False
            player.is_active = True
            player.is_all_in = False
    
    def _get_position_name(self, seat_index: int, num_players: int) -> str:
        """Get position name for a given seat index."""
        if num_players == 2:
            return "SB" if seat_index == 0 else "BB"
        elif num_players == 3:
            return ["BTN", "SB", "BB"][seat_index]
        elif num_players == 4:
            return ["BTN", "SB", "BB", "UTG"][seat_index]
        elif num_players == 5:
            return ["BTN", "SB", "BB", "UTG", "MP"][seat_index]
        elif num_players == 6:
            return ["BTN", "SB", "BB", "UTG", "MP", "CO"][seat_index]
        elif num_players == 7:
            return ["BTN", "SB", "BB", "UTG", "MP", "MP2", "CO"][seat_index]
        elif num_players == 8:
            return ["BTN", "SB", "BB", "UTG", "MP", "MP2", "MP3", "CO"][seat_index]
        elif num_players == 9:
            return ["BTN", "SB", "BB", "UTG", "MP", "MP2", "MP3", "MP4", "CO"][seat_index]
        else:
            return f"Seat_{seat_index}"
    
    def get_next_action(self) -> Optional[Dict[str, Any]]:
        """Get the next GTO bot action with detailed explanation."""
        # Ensure we have a valid action player index
        if self.action_player_index is None:
            return None
        if not (0 <= self.action_player_index < len(self.game_state.players)):
            return None
        
        player_index = self.action_player_index
        player = self.game_state.players[player_index]
        
        # Skip players who cannot act
        if player.has_folded or not player.is_active or player.is_all_in:
            return None
        
        # Get GTO decision with explanation
        action, amount, explanation = self._get_gto_decision(player_index)
        
        # Store decision in history
        decision_record = {
            'player_index': player_index,
            'player_name': player.name,
            'position': player.position,
            'street': self.game_state.street,
            'action': action.value,
            'amount': amount,
            'explanation': explanation,
            'player_stack': player.stack,
            'player_bet': player.current_bet
        }
        
        self.decision_history.append(decision_record)
        self.current_decision_explanation = explanation
        
        if self.session_logger:
            self.session_logger.log_system(
                "INFO", "GTO_SIMULATION",
                f"GTO decision: {player.name} ({player.position}) -> {action.value} ${amount}",
                {"explanation": explanation[:100] + "..." if len(explanation) > 100 else explanation}
            )
        
        return {
            'player_index': player_index,
            'player_name': player.name,
            'position': player.position,
            'action': action,
            'amount': amount,
            'explanation': explanation
        }
    
    def set_sound_manager(self, sound_manager):
        """Set the sound manager for audio feedback."""
        self.sound_manager = sound_manager
    
    def _play_action_sound(self, action: ActionType):
        """Play sound for the executed action."""
        if self.sound_manager:
            try:
                # Map action types to sound names
                sound_mapping = {
                    ActionType.FOLD: "player_action_fold",
                    ActionType.CHECK: "player_action_check", 
                    ActionType.CALL: "player_action_call",
                    ActionType.BET: "player_action_bet",
                    ActionType.RAISE: "player_action_raise",
                }
                
                sound_name = sound_mapping.get(action)
                if sound_name:
                    # Use the unified event-based sound entry point used across the app
                    if hasattr(self.sound_manager, "play_poker_event_sound"):
                        self.sound_manager.play_poker_event_sound(sound_name)
                    else:
                        # Fallback for older sound manager API
                        self.sound_manager.play(sound_name)
            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_system("ERROR", "GTO_SIMULATION", 
                                         f"Error playing sound: {e}")
 
    def get_display_state(self) -> dict:
        """Provide a display state structure compatible with the UI timing hooks.

        - Reveals all hole cards (educational GTO mode)
        - Highlights the current action player
        - Supplies simple layout positions
        """
        info = self.get_game_info()
        num_players = len(self.game_state.players)

        # Card visibilities: show all players' cards in GTO simulation
        info["card_visibilities"] = [True for _ in range(num_players)]

        # Player highlights: current action player
        highlights = []
        for i in range(num_players):
            highlights.append(i == self.action_player_index)
        info["player_highlights"] = highlights

        # Simple layout positions (seat index based)
        info["layout_positions"] = [{"seat": i, "position": i} for i in range(num_players)]

        return info

    def execute_action(self, player_index: int, action: ActionType, amount: float) -> bool:
        """Execute a GTO action for a specific player."""
        try:
            # Validate the action
            if player_index < 0 or player_index >= len(self.game_state.players):
                return False
            
            player = self.game_state.players[player_index]
            if player.has_folded or not player.is_active:
                return False
            
            # Execute the action using parent method (handles turn order, streets, board, pot, etc.)
            success = super().execute_action(player, action, amount)
            
            if success:
                # Play sound for the action
                self._play_action_sound(action)
             
            return success
             
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_SIMULATION", 
                                     f"Error executing action: {e}")
            return False
 
    def get_game_info(self) -> Dict[str, Any]:
        """Return display state but always reveal all players' hole cards for education."""
        info = super().get_game_info()
        try:
            # Reveal all hole cards (if dealt) for every player in GTO simulation
            for idx, p in enumerate(self.game_state.players):
                # If cards exist, show them; otherwise keep placeholders
                revealed = p.cards if p.cards else ["**", "**"]
                if idx < len(info.get("players", [])):
                    info["players"][idx]["cards"] = revealed
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_SIMULATION", f"Error revealing cards: {e}")
        return info

    def is_hand_complete(self) -> bool:
        """Check if the current hand is complete."""
        # Hand is complete if we're at showdown or all but one player folded
        active_players = [p for p in self.game_state.players if not p.has_folded]
        
        if len(active_players) <= 1:
            return True
        
        # Check if we're at the end of the river and action is complete
        if (self.game_state.street == "river" and 
            self._is_street_complete() and 
            not self.game_state.action_player):
            return True
        
        return False
    
    def _get_gto_decision(self, player_index: int) -> Tuple[ActionType, float, str]:
        """Get GTO decision for a player with detailed explanation."""
        player = self.game_state.players[player_index]
        strategy = self.gto_strategies[player_index]
        
        # Get basic action decision
        action, amount = strategy.get_gto_action(player, self.game_state)
        
        # Generate detailed explanation
        explanation = self._explain_gto_decision(player, action, amount, strategy)
        
        return action, amount, explanation
    
    def _explain_gto_decision(self, player: Player, action: ActionType, 
                             amount: float, strategy: ImprovedGTOStrategy) -> str:
        """Generate detailed explanation of GTO decision."""
        position = player.position
        street = self.game_state.street
        pot_size = self.game_state.pot
        current_bet = self.game_state.current_bet
        call_amount = current_bet - player.current_bet
        
        explanation_parts = []
        
        # Position context
        explanation_parts.append(f"{player.name} ({position}) is acting on {street}")
        
        # Hand strength context (if postflop)
        if street != "preflop" and player.cards:
            hand_strength = self._evaluate_hand_strength(player.cards, 
                                                       self.game_state.board)
            explanation_parts.append(f"Hand strength: {hand_strength}")
        
        # Action reasoning
        if action == ActionType.FOLD:
            if call_amount > 0:
                explanation_parts.append(
                    f"Folding to ${call_amount} bet (pot odds unfavorable)")
            else:
                explanation_parts.append("Folding weak hand in early position")
        
        elif action == ActionType.CHECK:
            if call_amount == 0:
                explanation_parts.append("Checking with no bet to call")
            else:
                explanation_parts.append("Checking behind (no value in betting)")
        
        elif action == ActionType.CALL:
            explanation_parts.append(f"Calling ${call_amount} with playable hand")
            if pot_size > 0:
                pot_odds = call_amount / (pot_size + call_amount)
                explanation_parts.append(f"Pot odds: {pot_odds:.1%}")
        
        elif action == ActionType.BET:
            explanation_parts.append(f"Betting ${amount} for value")
            if pot_size > 0:
                bet_sizing = amount / pot_size
                explanation_parts.append(f"Bet sizing: {bet_sizing:.1%} of pot")
        
        elif action == ActionType.RAISE:
            explanation_parts.append(
                f"Raising to ${amount} (${amount - call_amount} more to call)")
            if current_bet > 0:
                raise_sizing = amount / current_bet
                explanation_parts.append(f"Raise sizing: {raise_sizing:.1f}x the current bet")
        
        # Stack management
        if amount > 0:
            stack_usage = amount / player.stack
            explanation_parts.append(f"Stack usage: {stack_usage:.1%}")
        
        return " | ".join(explanation_parts)
    
    def _evaluate_hand_strength(self, hole_cards: List[str], 
                               board_cards: List[str]) -> str:
        """Evaluate hand strength for explanation purposes."""
        if not hole_cards or not board_cards:
            return "Unknown"
        
        # Simple hand strength evaluation
        all_cards = hole_cards + board_cards
        ranks = [card[0] for card in all_cards]
        suits = [card[1] for card in all_cards]
        
        # Check for pairs, trips, etc.
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        max_count = max(rank_counts.values())
        
        if max_count == 4:
            return "Four of a Kind"
        elif max_count == 3:
            return "Three of a Kind"
        elif max_count == 2:
            pair_count = sum(1 for count in rank_counts.values() if count == 2)
            if pair_count >= 2:
                return "Two Pair"
            else:
                return "One Pair"
        else:
            return "High Card"
    
    # Use parent street/board progression to leverage animations and bet graphics
    
    def get_current_decision_explanation(self) -> str:
        """Get the explanation for the current decision."""
        return self.current_decision_explanation
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get the complete decision history for the current hand."""
        return self.decision_history.copy()
    
    def get_game_summary(self) -> Dict[str, Any]:
        """Get a summary of the current game state."""
        return {
            'street': self.game_state.street,
            'pot': self.game_state.pot,
            'current_bet': self.game_state.current_bet,
            'dealer_position': self.game_state.dealer_position,
            'action_player': self.action_player_index,
            'players': [
                {
                    'name': p.name,
                    'position': p.position,
                    'stack': p.stack,
                    'bet': p.current_bet,
                    'folded': p.has_folded,
                    'cards': p.cards if self.game_state.street != "preflop" else ['**', '**']
                }
                for p in self.game_state.players
            ],
            'board_cards': self.game_state.board.copy() if self.game_state.board else [],
            'decision_count': len(self.decision_history)
        }
