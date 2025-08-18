from typing import Any, Dict
from .actions import *


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
    
    return state
