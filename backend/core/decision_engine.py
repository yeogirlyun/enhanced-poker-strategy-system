#!/usr/bin/env python3
"""
Decision Engine Interface for Unified Bot Sessions

This module provides an abstract base class for decision engines that can be
used in bot-only poker sessions. This allows GTO sessions and Hands Review
sessions to share the same underlying architecture while using different
decision sources.

Key principles:
- Clean interface separation between decision logic and game flow
- Reusable architecture for all bot-only sessions
- Consistent API for different decision sources
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from .poker_types import ActionType, Player


class DecisionEngine(ABC):
    """
    Abstract base class for poker decision engines.
    
    This interface allows different decision sources (GTO algorithms, 
    preloaded hand data, etc.) to be used interchangeably in bot sessions.
    """
    
    @abstractmethod
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the next action decision for a player.
        
        Args:
            player_index: Index of the player who needs to act
            game_state: Current game state information
            
        Returns:
            Dict containing:
                - action: ActionType (FOLD, CHECK, CALL, BET, RAISE)
                - amount: float (bet/raise amount, 0 for fold/check/call)
                - explanation: str (reasoning for the decision)
                - confidence: float (0-1, confidence in the decision)
        """
        pass
    
    @abstractmethod
    def is_session_complete(self) -> bool:
        """
        Check if this decision engine has reached the end of its decisions.
        
        Returns:
            True if no more decisions are available, False otherwise
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the decision engine to its initial state."""
        pass
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session state.
        
        Returns:
            Dict with session-specific information (progress, metadata, etc.)
        """
        return {}


class GTODecisionEngine(DecisionEngine):
    """
    Decision engine that uses GTO (Game Theory Optimal) strategies.
    
    This engine calculates optimal poker decisions based on game theory
    principles and provides explanations for educational purposes.
    """
    
    def __init__(self, num_players: int = 6):
        """Initialize the GTO decision engine."""
        # Temporarily disabled due to syntax errors in improved_gto_strategy
        # from .improved_gto_strategy import ImprovedGTOStrategy
        
        self.num_players = num_players
        self.gto_strategies = {}
        self.decision_count = 0
        
        # Initialize GTO strategies for each player position
        # Temporarily disabled due to syntax errors
        # for i in range(num_players):
        #     self.gto_strategies[i] = ImprovedGTOStrategy(num_players)
    
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get GTO-optimal decision for the given player and game state."""
        # Debug: Log decision request
        print(f"🎯 GTO_DECISION_REQUEST: Player {player_index}")
        print(f"🎯 GTO_DECISION_REQUEST: Game state type: {type(game_state)}")
        if isinstance(game_state, dict):
            print(f"🎯 GTO_DECISION_REQUEST: Game state keys: {list(game_state.keys())}")
            print(f"🎯 GTO_DECISION_REQUEST: Street: {game_state.get('street', 'unknown')}")
            print(f"🎯 GTO_DECISION_REQUEST: Players count: {len(game_state.get('players', []))}")
        
        if player_index not in self.gto_strategies:
            # Fallback for invalid player index
            print(f"🚨 GTO_DECISION_ERROR: Invalid player index {player_index}, available: {list(self.gto_strategies.keys())}")
            return {
                'action': ActionType.FOLD,
                'amount': 0.0,
                'explanation': f"Invalid player index {player_index}",
                'confidence': 0.0
            }
        
        strategy = self.gto_strategies[player_index]
        
        try:
            # Extract player and game state information
            players = game_state.get('players', [])
            if player_index >= len(players):
                raise IndexError(f"Player index {player_index} out of range")
            
            # Get player dict and convert to Player object
            player_dict = players[player_index]
            
            # Import Player class
            from .poker_types import Player
            
            # Create a proper Player object from the dictionary
            player = Player(
                name=player_dict.get('name', f'Player_{player_index}'),
                stack=player_dict.get('stack', 1000.0),
                position=self._get_position_name(player_index, len(players)),
                is_human=player_dict.get('is_human', False),
                is_active=not player_dict.get('has_folded', False),
                cards=player_dict.get('cards', []),
                current_bet=player_dict.get('current_bet', 0.0)
            )
            
            # Set additional attributes that might be useful
            player.index = player_index
            
            print(f"🎯 GTO_PLAYER_CREATED: {player.name} at {player.position} with cards {player.cards}")
            print(f"🎯 GTO_PLAYER_CREATED: Stack=${player.stack}, bet=${player.current_bet}")
            
            
            # Convert game_state dict to GameState object if needed
            if isinstance(game_state, dict):
                # Create a simple GameState-like object with required attributes
                class SimpleGameState:
                    def __init__(self, data):
                        self.players = data.get('players', [])
                        self.board = data.get('board', [])
                        self.pot = data.get('pot', 0.0)
                        self.current_bet = data.get('current_bet', 0.0)
                        self.street = data.get('street', 'preflop')
                        self.dealer_position = data.get('dealer_position', 0)
                        self.action_player = data.get('action_player', 0)
                
                game_state_obj = SimpleGameState(game_state)
            else:
                game_state_obj = game_state
            
            # Get GTO decision using the improved strategy engine
            print(f"🎯 GTO_STRATEGY_INPUT: Position={player.position}, Cards={player.cards}")
            print(f"🎯 GTO_STRATEGY_INPUT: Street={game_state_obj.street}, Current_bet={game_state_obj.current_bet}")
            print(f"🎯 GTO_STRATEGY_INPUT: Player_bet={player.current_bet}, Stack=${player.stack}")
            
            action, amount = strategy.get_gto_action(player, game_state_obj)
            
            print(f"🎯 GTO_STRATEGY_OUTPUT: Action={action}, Amount={amount}")
            
            
            self.decision_count += 1
            
            # Create explanation based on action and street
            street = game_state.get('street', 'preflop')
            explanation = self._generate_explanation(action, amount, street, player)
            
            # Return formatted decision
            return {
                'action': action,
                'amount': amount,
                'explanation': explanation,
                'confidence': 0.8,  # GTO decisions have high confidence
                'decision_number': self.decision_count
            }
            
        except Exception as e:
            # Debug: Log the actual error to understand what's failing
            print(f"🚨 GTO_ENGINE_ERROR: {str(e)}")
            print(f"🚨 GTO_ENGINE_ERROR: Exception type: {type(e).__name__}")
            print(f"🚨 GTO_ENGINE_ERROR: Player index: {player_index}")
            print(f"🚨 GTO_ENGINE_ERROR: Game state keys: {list(game_state.keys()) if isinstance(game_state, dict) else 'Not a dict'}")
            
            import traceback
            print(f"🚨 GTO_ENGINE_ERROR: Full traceback:\n{traceback.format_exc()}")
            
            # Fallback decision if strategy engine fails
            return {
                'action': ActionType.FOLD,
                'amount': 0.0,
                'explanation': f"GTO engine error: {str(e)}",
                'confidence': 0.0
            }
    
    def _generate_explanation(self, action: ActionType, amount: float, street: str, player) -> str:
        """Generate a human-readable explanation for the GTO decision."""
        position = getattr(player, 'position', 'Unknown')
        stack = getattr(player, 'stack', 0)
        cards = getattr(player, 'cards', [])
        
        # Basic action descriptions
        action_explanations = {
            ActionType.FOLD: f"GTO fold from {position} position. Hand doesn't meet minimum requirements for this spot.",
            ActionType.CHECK: f"GTO check from {position}. Controlling pot size with marginal hand strength.",
            ActionType.CALL: f"GTO call from {position}. Hand has sufficient equity to continue at current price.",
            ActionType.BET: f"GTO bet of ${amount:.0f} from {position}. Betting for value and/or protection.",
            ActionType.RAISE: f"GTO raise to ${amount:.0f} from {position}. Hand strength justifies aggressive action."
        }
        
        base_explanation = action_explanations.get(action, f"GTO {action.name.lower()} from {position}")
        
        # Add street-specific context
        if street == 'preflop':
            base_explanation += f" Based on modern {self.num_players}-max preflop ranges."
        elif street in ['flop', 'turn', 'river']:
            base_explanation += f" {street.capitalize()} play considering board texture and equity."
        
        return base_explanation
    
    def _get_position_name(self, player_index: int, num_players: int) -> str:
        """Convert player index to position name for different table sizes."""
        if num_players == 2:
            # Heads-up: SB and BB positions
            positions = ["SB", "BB"]
            return positions[player_index % 2]
        elif num_players == 6:
            positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
            return positions[player_index % 6]
        elif num_players == 9:
            positions = ["UTG", "UTG+1", "MP", "MP+1", "CO", "BTN", "SB", "BB", "UTG"]
            return positions[player_index % 9]
        else:
            # For other table sizes, use appropriate position names
            if num_players <= 3:
                # Small tables: SB, BB, BTN
                positions = ["SB", "BB", "BTN"]
                return positions[player_index % len(positions)]
            elif num_players <= 5:
                # Medium tables: UTG, MP, BTN, SB, BB
                positions = ["UTG", "MP", "BTN", "SB", "BB"]
                return positions[player_index % len(positions)]
            else:
                # Large tables: use generic position names
                return f"Pos_{player_index}"
    
    def is_session_complete(self) -> bool:
        """GTO sessions continue indefinitely until manually stopped."""
        return False
    
    def reset(self) -> None:
        """Reset the GTO decision engine."""
        self.decision_count = 0
        # GTO strategies don't need resetting as they're stateless
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get GTO session information."""
        return {
            'engine_type': 'GTO',
            'num_players': self.num_players,
            'decisions_made': self.decision_count,
            'strategies_loaded': len(self.gto_strategies)
        }


class PreloadedDecisionEngine(DecisionEngine):
    """
    Decision engine that uses preloaded hand data.
    
    This engine replays predetermined poker hands by following the exact
    sequence of actions from historical or generated hand data. Perfect
    for hands review, analysis, and educational purposes.
    """
    
    def __init__(self, hands_data: Dict[str, Any]):
        """
        Initialize the preloaded decision engine.
        
        Args:
            hands_data: Dictionary containing hand timeline and actions
        """
        print(f"🔥 PRELOADED_DEBUG: Initializing with hands_data keys: {list(hands_data.keys())}")
        self.hands_data = hands_data
        self.timeline = self._parse_timeline(hands_data)
        self.current_step = 0
        self.total_steps = len(self.timeline)
        print(f"🔥 PRELOADED_DEBUG: Parsed timeline length: {self.total_steps}")
        print(f"🔥 PRELOADED_DEBUG: Timeline: {self.timeline}")
        print(f"🔥 PRELOADED_DEBUG: is_session_complete() = {self.is_session_complete()}")
        
    def _parse_timeline(self, hands_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the hands data into a timeline of decisions.
        
        Args:
            hands_data: Raw hands data from JSON
            
        Returns:
            List of decision dictionaries in chronological order
        """
        timeline = []
        
        try:
            actions = hands_data.get('actions', [])
            print(f"🔥 PARSE_DEBUG: Found {len(actions)} actions to parse")
            print(f"🔥 PARSE_DEBUG: First few actions: {actions[:3] if actions else 'No actions'}")
            
            # Parse the flat actions array (GTO hands format)
            for i, action_data in enumerate(actions):
                print(f"🔥 PARSE_DEBUG: Processing action {i}: {action_data}")
                if isinstance(action_data, dict):
                    player_index = action_data.get('player_index', 0)
                    action_str = action_data.get('action', 'fold')
                    amount = action_data.get('amount', 0.0)
                    street = action_data.get('street', 'preflop')
                    explanation = action_data.get('explanation', f"Preloaded {action_str}")
                    
                    # Convert to decision format
                    decision = {
                        'player_index': int(player_index),
                        'action': self._parse_action_type(action_str),
                        'amount': float(amount),
                        'street': street,
                        'explanation': explanation,
                        'confidence': 1.0,  # Historical actions are "certain"
                        'original_data': action_data
                    }
                    
                    timeline.append(decision)
                    print(f"🔥 PARSE_DEBUG: Added decision to timeline: {decision}")
            
            print(f"🔥 PARSE_DEBUG: Final timeline has {len(timeline)} decisions")
            return timeline
            
        except Exception as e:
            # Return empty timeline if parsing fails
            print(f"Error parsing hands timeline: {e}")
            return []
    
    def _parse_action_type(self, action_str: str) -> ActionType:
        """Convert string action to ActionType enum."""
        action_mapping = {
            'fold': ActionType.FOLD,
            'check': ActionType.CHECK,
            'call': ActionType.CALL,
            'bet': ActionType.BET,
            'raise': ActionType.RAISE,
        }
        
        return action_mapping.get(action_str.lower(), ActionType.FOLD)
    
    def get_decision(self, player_index: int, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next preloaded decision from the timeline."""
        current_street = game_state.get('street', 'preflop')
        # Find the next decision that matches the current street
        matching_decision = None
        
        while self.current_step < self.total_steps:
            decision = self.timeline[self.current_step]
            decision_street = decision.get('street', 'preflop')
            
            if decision_street == current_street:
                matching_decision = decision.copy()
                self.current_step += 1
                break
            else:
                # Skip decisions that don't match current street
                self.current_step += 1
        
        if matching_decision is None:
            # No more decisions available for current street
            return {
                'action': ActionType.CHECK,  # Default to check if no action found
                'amount': 0.0,
                'explanation': f'No preloaded action for {current_street} street',
                'confidence': 0.0
            }
        
        # CRITICAL FIX: Update the decision to be for the current player
        # The preloaded actions are in chronological order, but we need to apply them
        # to whoever is the current action player in the recreated game state
        matching_decision['player_index'] = player_index
        matching_decision['explanation'] = f"[Preloaded] {matching_decision.get('explanation', 'Historical action')}"
        
        return matching_decision
    
    def is_session_complete(self) -> bool:
        """Check if all preloaded decisions have been used."""
        return self.current_step >= self.total_steps
    
    def reset(self) -> None:
        """Reset to the beginning of the hand timeline."""
        self.current_step = 0
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get preloaded session information."""
        return {
            'engine_type': 'Preloaded',
            'total_steps': self.total_steps,
            'current_step': self.current_step,
            'progress_percent': (self.current_step / max(1, self.total_steps)) * 100,
            'steps_remaining': max(0, self.total_steps - self.current_step)
        }
    
    def get_timeline_info(self) -> Dict[str, Any]:
        """Get detailed timeline information for debugging."""
        return {
            'timeline_length': len(self.timeline),
            'current_position': self.current_step,
            'next_action': self.timeline[self.current_step] if self.current_step < len(self.timeline) else None,
            'hands_data_keys': list(self.hands_data.keys()) if self.hands_data else []
        }
