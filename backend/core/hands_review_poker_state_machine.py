#!/usr/bin/env python3
"""
Hands Review Poker State Machine

A specialized state machine that inherits from FlexiblePokerStateMachine
and provides hands review specific functionality.

This state machine is designed for studying hands and provides:
- Always visible cards for educational purposes
- Enhanced replay and analysis capabilities
- Step-by-step hand progression
- Educational event generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .flexible_poker_state_machine import FlexiblePokerStateMachine, GameConfig, GameEvent, PokerState
from .types import ActionType, Player


class HandsReviewPokerStateMachine(FlexiblePokerStateMachine):
    """
    A specialized poker state machine for hands review and analysis.
    
    This state machine is specifically designed for studying hands and provides:
    - Always visible cards for educational analysis
    - Enhanced replay capabilities with step control
    - Educational event generation and analysis
    - Hand strength and decision analysis
    """
    
    def __init__(self, config: GameConfig, **kwargs):
        """Initialize the hands review poker state machine."""
        super().__init__(config, **kwargs)
        
        # Hands review specific properties
        self.review_mode = True
        self.current_hand_data = None
        self.replay_actions = []
        self.replay_index = 0
        self.analysis_data = {}
        
        print("🎯 HandsReviewPokerStateMachine initialized for educational analysis")
    
    def load_hand_for_review(self, hand_data: Dict[str, Any]):
        """Load a specific hand for review and analysis."""
        self.current_hand_data = hand_data
        self.replay_actions = hand_data.get('actions', [])
        self.replay_index = 0
        self.analysis_data = {}
        
        # Set up players with actual data
        if 'players' in hand_data:
            for i, player_data in enumerate(hand_data['players']):
                if i < len(self.game_state.players):
                    player = self.game_state.players[i]
                    player.name = player_data.get('name', f'Player {i+1}')
                    player.stack = player_data.get('stack', 100.0)
                    player.cards = player_data.get('cards', [])
                    player.position = player_data.get('position', i)
        
        # Set community cards if available
        if 'community_cards' in hand_data:
            self.game_state.community_cards = hand_data['community_cards']
        
        print(f"🎯 Loaded hand for review: {len(self.replay_actions)} actions to replay")
        
        # Emit hand loaded event
        self._emit_event(GameEvent(
            event_type="hand_loaded",
            data={
                'hand_id': hand_data.get('hand_id', 'unknown'),
                'num_actions': len(self.replay_actions),
                'num_players': len(hand_data.get('players', []))
            },
            timestamp=datetime.now()
        ))
    
    def step_forward(self) -> bool:
        """Step forward one action in the hand replay."""
        if self.replay_index >= len(self.replay_actions):
            print("🎯 End of hand reached")
            return False
        
        action_data = self.replay_actions[self.replay_index]
        self.replay_index += 1
        
        # Execute the historical action
        try:
            player_name = action_data.get('player_name', '')
            action_type = ActionType(action_data.get('action_type', 'fold'))
            amount = action_data.get('amount', 0.0)
            
            # Find player by name
            player = None
            for p in self.game_state.players:
                if p.name == player_name:
                    player = p
                    break
            
            if player:
                success = self.execute_action(player, action_type, amount)
                if success:
                    print(f"🎯 Replayed: {player_name} {action_type.value} ${amount}")
                    
                    # Emit step completed event with analysis
                    self._emit_event(GameEvent(
                        event_type="replay_step_completed",
                        data={
                            'step': self.replay_index,
                            'total_steps': len(self.replay_actions),
                            'action': {
                                'player': player_name,
                                'action': action_type.value,
                                'amount': amount
                            },
                            'analysis': self._analyze_action(player, action_type, amount)
                        },
                        timestamp=datetime.now()
                    ))
                    return True
                else:
                    print(f"🚫 Failed to replay: {player_name} {action_type.value} ${amount}")
            else:
                print(f"🚫 Player not found: {player_name}")
        
        except Exception as e:
            print(f"🚫 Error replaying action: {e}")
        
        return False
    
    def step_backward(self) -> bool:
        """Step backward one action in the hand replay."""
        if self.replay_index <= 0:
            print("🎯 Beginning of hand reached")
            return False
        
        self.replay_index -= 1
        
        # For now, just emit event - full backward replay would require state snapshots
        self._emit_event(GameEvent(
            event_type="replay_step_backward",
            data={
                'step': self.replay_index,
                'total_steps': len(self.replay_actions)
            },
            timestamp=datetime.now()
        ))
        
        print(f"🎯 Stepped backward to action {self.replay_index}")
        return True
    
    def get_display_state(self) -> Dict[str, Any]:
        """Get display state optimized for hands review."""
        base_state = super().get_game_info()
        
        # Enhance with hands review specific data
        review_state = {
            **base_state,
            'review_mode': True,
            'current_step': self.replay_index,
            'total_steps': len(self.replay_actions),
            'hand_analysis': self.analysis_data,
            'can_step_forward': self.replay_index < len(self.replay_actions),
            'can_step_backward': self.replay_index > 0,
        }
        
        # In hands review mode, always show all cards for educational purposes
        if 'players' in review_state:
            for i, player_info in enumerate(review_state['players']):
                if i < len(self.game_state.players):
                    actual_player = self.game_state.players[i]
                    if hasattr(actual_player, 'cards') and actual_player.cards:
                        # Always show actual cards in hands review
                        player_info['cards'] = actual_player.cards
                        player_info['cards_visible'] = True
        
        return review_state
    
    def _analyze_action(self, player: Player, action_type: ActionType, amount: float) -> Dict[str, Any]:
        """Analyze the educational value of an action."""
        analysis = {
            'position_analysis': self._analyze_position_play(player, action_type),
            'betting_analysis': self._analyze_betting_decision(action_type, amount),
            'hand_strength': self._estimate_hand_strength(player),
            'pot_odds': self._calculate_pot_odds(amount),
            'decision_quality': 'analyzing...'  # Placeholder for GTO analysis
        }
        
        return analysis
    
    def _analyze_position_play(self, player: Player, action_type: ActionType) -> str:
        """Analyze the positional aspects of the play."""
        # Simplified position analysis
        position_names = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB']
        pos_name = position_names[player.position] if player.position < len(position_names) else f'Pos{player.position}'
        
        if action_type in [ActionType.BET, ActionType.RAISE]:
            return f"Aggressive play from {pos_name} - shows strength"
        elif action_type == ActionType.CALL:
            return f"Calling from {pos_name} - drawing or medium strength"
        elif action_type == ActionType.CHECK:
            return f"Checking from {pos_name} - pot control or weak hand"
        else:
            return f"Folding from {pos_name} - weak hand or facing pressure"
    
    def _analyze_betting_decision(self, action_type: ActionType, amount: float) -> str:
        """Analyze the betting decision in context."""
        pot_size = self.game_state.pot
        
        if action_type in [ActionType.BET, ActionType.RAISE]:
            if amount < pot_size * 0.5:
                return "Small bet - value betting or bluffing with good odds"
            elif amount < pot_size:
                return "Medium bet - likely value betting or protection"
            else:
                return "Large bet - polarized range (very strong or bluff)"
        
        return "Passive action - pot control or weak holding"
    
    def _estimate_hand_strength(self, player: Player) -> str:
        """Provide a simplified hand strength estimate."""
        if not hasattr(player, 'cards') or not player.cards or len(player.cards) < 2:
            return "Unknown"
        
        # Very simplified hand strength analysis
        card1, card2 = player.cards[0], player.cards[1]
        
        if card1 and card2:
            # Extract ranks (simplified)
            try:
                rank1 = card1[0] if len(card1) >= 1 else ''
                rank2 = card2[0] if len(card2) >= 1 else ''
                
                high_cards = ['A', 'K', 'Q', 'J', 'T']
                
                if rank1 in high_cards and rank2 in high_cards:
                    return "Premium"
                elif rank1 in high_cards or rank2 in high_cards:
                    return "Medium"
                else:
                    return "Weak"
            except:
                return "Unknown"
        
        return "Unknown"
    
    def _calculate_pot_odds(self, call_amount: float) -> str:
        """Calculate pot odds for educational purposes."""
        if call_amount <= 0:
            return "N/A"
        
        pot_size = self.game_state.pot
        odds_ratio = pot_size / call_amount
        
        return f"{odds_ratio:.1f}:1"
    
    def reset_for_new_hand(self):
        """Reset the state machine for a new hand review."""
        super().reset_for_new_hand()
        self.current_hand_data = None
        self.replay_actions = []
        self.replay_index = 0
        self.analysis_data = {}
        
        print("🎯 Reset for new hand review")
    
    def get_educational_summary(self) -> Dict[str, Any]:
        """Get educational summary of the hand for learning purposes."""
        return {
            'hand_overview': {
                'total_actions': len(self.replay_actions),
                'current_position': self.replay_index,
                'completion_percentage': (self.replay_index / len(self.replay_actions) * 100) if self.replay_actions else 0
            },
            'key_decisions': self._identify_key_decisions(),
            'learning_points': self._generate_learning_points(),
            'suggested_analysis': self._suggest_further_analysis()
        }
    
    def _identify_key_decisions(self) -> List[str]:
        """Identify key decision points in the hand."""
        # Placeholder for identifying critical moments
        return [
            "Preflop action choice",
            "Flop continuation betting",
            "Turn decision facing aggression",
            "River value/bluff decision"
        ]
    
    def _generate_learning_points(self) -> List[str]:
        """Generate educational learning points."""
        return [
            "Consider position when making decisions",
            "Analyze pot odds for calling decisions",
            "Look for betting patterns and opponent tendencies",
            "Evaluate hand strength relative to board texture"
        ]
    
    def _suggest_further_analysis(self) -> List[str]:
        """Suggest areas for further study."""
        return [
            "Run equity analysis for key spots",
            "Compare with GTO solver recommendations",
            "Analyze opponent's likely range",
            "Study similar spots from database"
        ]
