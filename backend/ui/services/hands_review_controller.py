"""
Hands Review Session Controller - Handles business logic for hands review
Follows the service layer pattern from the handbook.
"""

import time
from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig


class HandsReviewController:
    """
    Controller for Hands Review Session - handles PPSM interactions and state updates.
    Follows the handbook pattern: UI dispatches actions → Controller → PPSM → Store updates.
    """
    
    def __init__(self, event_bus, store, session_id: str):
        self.event_bus = event_bus
        self.store = store
        self.session_id = session_id
        self.ppsm = None
        self.hand_model = None
        self.flattened_actions = []
        self.current_step = 0
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            f"session:{self.session_id}:enhanced_rpgw:action_executed",
            self._handle_action_execution
        )
        self.event_bus.subscribe(
            f"session:{self.session_id}:load_review_hand",
            self._handle_load_review_hand
        )
        self.event_bus.subscribe(
            f"session:{self.session_id}:next_review_action",
            self._handle_next_action
        )
        self.event_bus.subscribe(
            f"session:{self.session_id}:prev_review_action",
            self._handle_prev_action
        )
        self.event_bus.subscribe(
            f"session:{self.session_id}:reset_review_hand",
            self._handle_reset_hand
        )
    
    def _handle_load_review_hand(self, event_data):
        """Handle loading a new hand for review."""
        hand_data = event_data.get('hand_data', {})
        
        # Initialize PPSM with hand data
        self._initialize_ppsm(hand_data)
        
        # Flatten hand actions for step-by-step replay
        self.flattened_actions = self._flatten_hand_actions(hand_data)
        
        # Update store with loaded hand
        self.store.dispatch({
            'type': 'LOAD_REVIEW_HAND',
            'hand_data': hand_data,
            'flattened_actions': self.flattened_actions
        })
        
        # Trigger feedback event
        self.event_bus.publish(
            f"session:{self.session_id}:enhanced_rpgw:feedback",
            {
                'type': 'hand_loaded',
                'hand_id': hand_data.get('hand_id', 'Unknown'),
                'total_actions': len(self.flattened_actions)
            }
        )
    
    def _handle_action_execution(self, event_data):
        """Handle action execution from Enhanced RPGW."""
        action = event_data.get('action')
        
        if not action or not self.ppsm:
            return
        
        try:
            # Execute action in PPSM
            ppsm_result = self._execute_ppsm_action(action)
            
            # Update store with PPSM results
            self.store.dispatch({
                'type': 'UPDATE_ENHANCED_RPGW_STATE',
                'updates': {
                    'ppsm_result': ppsm_result,
                    'last_executed_action': action,
                    'execution_timestamp': time.time(),
                    'current_street': self.ppsm.game_state.current_street,
                    'pot_amount': self.ppsm.game_state.displayed_pot(),
                    'seats': self._get_seats_state(),
                    'board': self._get_board_state(),
                    'dealer': self._get_dealer_state(),
                    'current_actor': self._get_current_actor(),
                    'legal_actions': self._get_legal_actions()
                }
            })
            
            # Trigger appropriate feedback
            self._trigger_action_feedback(action, ppsm_result)
            
        except Exception as e:
            # Log error and update store
            print(f"⚠️ Error executing action: {e}")
            self.store.dispatch({
                'type': 'UPDATE_ENHANCED_RPGW_STATE',
                'updates': {
                    'execution_status': 'error',
                    'error_message': str(e)
                }
            })
    
    def _handle_next_action(self, event_data):
        """Handle moving to next action."""
        if self.current_step < len(self.flattened_actions) - 1:
            self.current_step += 1
            action = self.flattened_actions[self.current_step]
            
            # Execute the action
            self.store.dispatch({
                'type': 'ENHANCED_RPGW_EXECUTE_ACTION',
                'action': action,
                'action_index': self.current_step
            })
    
    def _handle_prev_action(self, event_data):
        """Handle moving to previous action."""
        if self.current_step > 0:
            self.current_step -= 1
            
            # Reset PPSM and replay up to current step
            self._reset_and_replay_to_step(self.current_step)
    
    def _handle_reset_hand(self, event_data):
        """Handle resetting the hand."""
        self.current_step = 0
        self._reset_and_replay_to_step(0)
    
    def _initialize_ppsm(self, hand_data):
        """Initialize PPSM with hand data."""
        # Extract game configuration
        players = hand_data.get('players', [])
        small_blind = hand_data.get('small_blind', 5)
        big_blind = hand_data.get('big_blind', 10)
        
        # Create game config
        config = GameConfig(
            num_players=len(players),
            small_blind=small_blind,
            big_blind=big_blind,
            starting_stack=1000  # Default starting stack
        )
        
        # Initialize PPSM
        self.ppsm = PurePokerStateMachine(config)
        
        # Set up players (placeholder for PPSM integration)
        # This would need to be implemented in PPSM
        for i, player in enumerate(players):
            # Extract player info for PPSM setup
            player.get('player_uid', f'player_{i}')
            player.get('name', f'Player {i+1}')
            player.get('starting_stack', 1000)
    
    def _flatten_hand_actions(self, hand_data):
        """Flatten hand actions into chronological list."""
        flattened = []
        
        # Extract actions from each street
        streets = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
        
        for street in streets:
            if street in hand_data:
                street_data = hand_data[street]
                actions = street_data.get('actions', [])
                
                for action in actions:
                    # Ensure action has required fields
                    if 'type' in action and 'actor' in action:
                        flattened.append({
                            'type': action['type'],
                            'actor': action['actor'],
                            'street': street,
                            'amount': action.get('amount'),
                            'to_amount': action.get('to_amount'),
                            'note': action.get('note')
                        })
        
        return flattened
    
    def _execute_ppsm_action(self, action):
        """Execute action in PPSM."""
        if not self.ppsm:
            raise ValueError("PPSM not initialized")
        
        # Convert action to PPSM format
        ppsm_action = {
            'type': action['type'],
            'actor_uid': action['actor'],
            'street': action['street'],
            'to_amount': action.get('to_amount'),
            'note': action.get('note')
        }
        
        # Execute in PPSM (this would need to be implemented in PPSM)
        # For now, we'll return a placeholder result
        return {
            'success': True,
            'action': ppsm_action,
            'new_state': 'executed'
        }
    
    def _get_seats_state(self):
        """Get current seats state from PPSM."""
        if not self.ppsm:
            return []
        
        # This would extract seat state from PPSM
        # For now, return placeholder
        return []
    
    def _get_board_state(self):
        """Get current board state from PPSM."""
        if not self.ppsm:
            return []
        
        # This would extract board state from PPSM
        # For now, return placeholder
        return []
    
    def _get_dealer_state(self):
        """Get current dealer state from PPSM."""
        if not self.ppsm:
            return {'position': 0}
        
        # This would extract dealer state from PPSM
        # For now, return placeholder
        return {'position': 0}
    
    def _get_current_actor(self):
        """Get current actor from PPSM."""
        if not self.ppsm:
            return None
        
        # This would extract current actor from PPSM
        # For now, return placeholder
        return None
    
    def _get_legal_actions(self):
        """Get legal actions from PPSM."""
        if not self.ppsm:
            return []
        
        # This would extract legal actions from PPSM
        # For now, return placeholder
        return []
    
    def _reset_and_replay_to_step(self, target_step):
        """Reset PPSM and replay actions up to target step."""
        # Reset PPSM
        self._initialize_ppsm(self.hand_model or {})
        
        # Replay actions up to target step
        for i in range(target_step + 1):
            if i < len(self.flattened_actions):
                action = self.flattened_actions[i]
                self._execute_ppsm_action(action)
        
        # Update store
        self.store.dispatch({
            'type': 'SET_REVIEW_PROGRESS',
            'current_step': target_step,
            'total_steps': len(self.flattened_actions)
        })
    
    def _trigger_action_feedback(self, action, ppsm_result):
        """Trigger appropriate feedback events."""
        # Map action types to feedback types
        feedback_mapping = {
            'DEAL_HOLE': 'card_deal',
            'DEAL_BOARD': 'card_deal',
            'POST_BLIND': 'chip_bet',
            'BET': 'player_bet',
            'RAISE': 'player_bet',
            'CALL': 'player_call',
            'CHECK': 'player_check',
            'FOLD': 'player_fold',
            'END_HAND': 'hand_end'
        }
        
        feedback_type = feedback_mapping.get(action['type'], 'default')
        
        self.event_bus.publish(
            f"session:{self.session_id}:enhanced_rpgw:feedback",
            {
                'type': feedback_type,
                'action': action,
                'ppsm_result': ppsm_result
            }
        )
    
    def dispose(self):
        """Clean up resources."""
        self.ppsm = None
        self.hand_model = None
        self.flattened_actions = []
        self.current_step = 0
