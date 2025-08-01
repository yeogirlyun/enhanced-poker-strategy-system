#!/usr/bin/env python3
"""
Poker Trainer Backend - FastAPI Edition
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType
from gui_models import StrategyData

app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for game sessions (for simplicity)
sessions: Dict[str, ImprovedPokerStateMachine] = {}

class ActionRequest(BaseModel):
    action: str
    size: float = 0.0

@app.post("/api/game/new")
def new_game():
    """Creates a new game session."""
    strategy_data = StrategyData()
    strategy_data.load_strategy_from_file("modern_strategy.json")
    
    session_id = f"game_{len(sessions) + 1}"
    state_machine = ImprovedPokerStateMachine(num_players=6, strategy_data=strategy_data)
    sessions[session_id] = state_machine
    
    state_machine.start_hand()
    
    return {"session_id": session_id, "game_state": state_machine.get_game_info()}

@app.post("/api/game/{session_id}/action")
def post_action(session_id: str, request: ActionRequest):
    """Handles a player action and then runs all subsequent bot turns."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state_machine = sessions[session_id]
    player = state_machine.get_action_player()
    
    if not player or not player.is_human:
        raise HTTPException(status_code=400, detail="Not human player's turn")

    action_map = {
        "fold": ActionType.FOLD, "check": ActionType.CHECK, "call": ActionType.CALL, 
        "bet": ActionType.BET, "raise": ActionType.RAISE
    }
    action_type = action_map[request.action.upper()]
    
    # Execute the human's action
    state_machine.execute_action(player, action_type, request.size)
    
    # *** NEW: Automatically run bot turns until it's the human's turn again ***
    while True:
        current_player = state_machine.get_action_player()
        if not current_player or current_player.is_human or state_machine.get_current_state() in [state_machine.PokerState.END_HAND, state_machine.PokerState.SHOWDOWN]:
            break # Stop if it's the human's turn or the hand is over
        
        state_machine.execute_bot_action(current_player)

    return {"game_state": state_machine.get_game_info()}

@app.get("/api/game/{session_id}/state")
def get_state(session_id: str):
    """Gets the current game state for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"game_state": sessions[session_id].get_game_info()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 