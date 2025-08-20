from typing import Any, Dict
from .actions import (
    SET_TABLE_DIM, SET_POT, SET_SEATS, SET_BOARD, SET_ACTIVE_TAB, 
    SET_DEALER, SET_REVIEW_HANDS, SET_REVIEW_FILTER, SET_LOADED_HAND, 
    SET_STUDY_MODE, SET_REVIEW_COLLECTION, ENHANCED_RPGW_EXECUTE_ACTION, 
    UPDATE_ENHANCED_RPGW_STATE, ENHANCED_RPGW_ANIMATION_EVENT,
    LOAD_REVIEW_HAND, NEXT_REVIEW_ACTION, PREV_REVIEW_ACTION, 
    RESET_REVIEW_HAND, SET_REVIEW_PROGRESS, SET_REVIEW_STATUS,
    HANDS_REVIEW_NEXT_ACTION
)


def root_reducer(
    state: Dict[str, Any], action: Dict[str, Any]
) -> Dict[str, Any]:
    action_type = action.get("type")
    
    # Table/game state actions
    if action_type == SET_TABLE_DIM:
        table = state.get("table", {})
        return {**state, "table": {**table, "dim": action["dim"]}}
    if action_type == SET_POT:
        return {**state, "pot": {"amount": action["amount"]}}
    if action_type == SET_SEATS:
        return {**state, "seats": action["seats"]}
    if action_type == SET_BOARD:
        return {**state, "board": action["board"]}
    if action_type == SET_DEALER:
        return {**state, "dealer": action["dealer"]}
    if action_type == SET_ACTIVE_TAB:
        return {**state, "active_tab": action["name"]}
    
    # Review state actions
    if action_type == SET_REVIEW_HANDS:
        review = state.get("review", {})
        return {**state, "review": {**review, "hands": action["hands"]}}
    if action_type == SET_REVIEW_FILTER:
        review = state.get("review", {})
        return {**state, "review": {**review, "filter": action["filter"]}}
    if action_type == SET_LOADED_HAND:
        review = state.get("review", {})
        return {**state, "review": {**review, "loaded_hand": action["hand"]}}
    if action_type == SET_STUDY_MODE:
        review = state.get("review", {})
        return {**state, "review": {**review, "study_mode": action["mode"]}}
    if action_type == SET_REVIEW_COLLECTION:
        review = state.get("review", {})
        return {**state, "review": {**review, "collection": action["collection"]}}
    
    # Enhanced RPGW actions
    if action_type in [
        ENHANCED_RPGW_EXECUTE_ACTION, 
        UPDATE_ENHANCED_RPGW_STATE, 
        ENHANCED_RPGW_ANIMATION_EVENT
    ]:
        return enhanced_rpgw_reducer(state, action)
    
    # Hands Review Session specific actions
    if action_type == LOAD_REVIEW_HAND:
        return hands_review_reducer(state, action)
    if action_type == NEXT_REVIEW_ACTION:
        return hands_review_reducer(state, action)
    if action_type == PREV_REVIEW_ACTION:
        return hands_review_reducer(state, action)
    if action_type == RESET_REVIEW_HAND:
        return hands_review_reducer(state, action)
    if action_type == SET_REVIEW_PROGRESS:
        return hands_review_reducer(state, action)
    if action_type == SET_REVIEW_STATUS:
        return hands_review_reducer(state, action)
    if action_type == HANDS_REVIEW_NEXT_ACTION:
        return hands_review_reducer(state, action)
    
    return state


def enhanced_rpgw_reducer(state, action):
    """Reducer for Enhanced RPGW actions - maintains architectural compliance."""
    if action['type'] == ENHANCED_RPGW_EXECUTE_ACTION:
        # Extract action data
        game_action = action['action']
        action_index = action['action_index']
        
        # Create new state with action execution
        new_state = {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': game_action,
                'action_index': action_index,
                'execution_status': 'pending'
            }
        }
        
        # Trigger event for service layer
        if 'event_bus' in state:
            state['event_bus'].publish(
                "enhanced_rpgw:action_executed",
                {
                    "action": game_action,
                    "action_index": action_index,
                    "state": new_state
                }
            )
        
        return new_state
    
    elif action['type'] == UPDATE_ENHANCED_RPGW_STATE:
        # Update state from PPSM execution results
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                **action['updates'],
                'execution_status': 'completed'
            }
        }
    
    elif action['type'] == ENHANCED_RPGW_ANIMATION_EVENT:
        # Handle animation events
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'animation_event': action['animation_data']
            }
        }
    
    return state


def hands_review_reducer(state, action):
    """Reducer for Hands Review Session actions."""
    action_type = action.get('type')
    review = state.get('review', {})
    
    if action_type == LOAD_REVIEW_HAND:
        # Load a new hand for review
        hand_data = action.get('hand_data', {})
        flattened_actions = action.get('flattened_actions', [])
        
        return {
            **state,
            'review': {
                **review,
                'loaded_hand': hand_data,
                'flattened_actions': flattened_actions,
                'current_step': 0,
                'total_steps': len(flattened_actions),
                'status': 'loaded'
            },
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': None,
                'action_index': 0,
                'execution_status': 'idle'
            }
        }
    
    elif action_type == NEXT_REVIEW_ACTION:
        # Move to next action
        current_step = review.get('current_step', 0)
        total_steps = review.get('total_steps', 0)
        
        if current_step < total_steps - 1:
            new_step = current_step + 1
            return {
                **state,
                'review': {
                    **review,
                    'current_step': new_step,
                    'status': 'playing'
                }
            }
        return state
    
    elif action_type == PREV_REVIEW_ACTION:
        # Move to previous action
        current_step = review.get('current_step', 0)
        
        if current_step > 0:
            new_step = current_step - 1
            return {
                **state,
                'review': {
                    **review,
                    'current_step': new_step,
                    'status': 'playing'
                }
            }
        return state
    
    elif action_type == RESET_REVIEW_HAND:
        # Reset to beginning of hand
        return {
            **state,
            'review': {
                **review,
                'current_step': 0,
                'status': 'loaded'
            },
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': None,
                'action_index': 0,
                'execution_status': 'idle'
            }
        }
    
    elif action_type == SET_REVIEW_PROGRESS:
        # Set progress information
        return {
            **state,
            'review': {
                **review,
                'current_step': action.get('current_step', 0),
                'total_steps': action.get('total_steps', 0)
            }
        }
    
    elif action_type == SET_REVIEW_STATUS:
        # Set review status
        return {
            **state,
            'review': {
                **review,
                'status': action.get('status', 'idle')
            }
        }
    
    elif action_type == HANDS_REVIEW_NEXT_ACTION:
        # Architecture compliant: trigger service layer via event
        session_id = action.get('session_id')
        
        # Update state to show action is pending
        new_state = {
            **state,
            'review': {
                **review,
                'status': 'processing_action',
                'last_action_timestamp': action.get('timestamp', 0)
            }
        }
        
        # Trigger event for service layer to handle business logic
        event_bus = state.get('event_bus')
        if event_bus:
            event_bus.publish(
                "hands_review:next_action_requested",
                {
                    "session_id": session_id,
                    "timestamp": action.get('timestamp', 0),
                    "state": new_state
                }
            )
        
        return new_state
    
    return state
