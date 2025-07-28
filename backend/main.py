# filename: main.py
"""
FastAPI Backend for the Advanced Hold'em Trainer

REVISION HISTORY:
================
Version 1.6 (2025-07-26) - File Corruption Fix
- FIXED: A SyntaxError caused by accidental pasting of HTML content into
  this Python file. Restored the file to its correct state.

Version 1.5 (2025-07-26) - Game Loop State Fix
- FIXED: A critical bug where the game would incorrectly prompt the user for
  action again after they had already called or checked.

Version 1.4 (2025-07-26) - Betting Round Logic Overhaul
- FIXED: A critical bug where the game would end prematurely after a raise.

Version 1.3 (2025-07-26) - Multi-Street Game Flow
- IMPLEMENTED: A proper, multi-street game flow engine.
"""

import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random
import json

# Add project root to path to allow module imports
sys.path.append('.')

# Import the refactored game logic components
from table import Table
from decision_engine import DecisionEngine
from enhanced_hand_evaluation import EnhancedHandEvaluator, PositionAdjustedEvaluator

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Game State Management ---
game_sessions: Dict[str, Any] = {}

def load_strategy():
    """Loads the strategy configuration from strategy.json."""
    try:
        with open('strategy.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("FATAL: strategy.json not found.")
        sys.exit(1)

STRATEGY = load_strategy()

class GameAction(BaseModel):
    """Defines the structure for a player's action received from the frontend."""
    action: str
    size: Optional[float] = 0.0

# --- API Endpoints ---

@app.post("/api/game/new")
def new_game():
    """Creates a new game session and returns the initial state."""
    session_id = f"session_{len(game_sessions)}"
    
    table = Table(num_players=6)
    decision_engine = DecisionEngine()
    
    game_sessions[session_id] = {
        "table": table,
        "decision_engine": decision_engine,
    }
    
    _start_new_hand(session_id)
    
    return {"session_id": session_id, "game_state": _get_sanitized_game_state(session_id)}

@app.post("/api/game/{session_id}/action")
def player_action(session_id: str, player_action: GameAction):
    """Processes an action from the user and advances the game state."""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")

    game = game_sessions[session_id]
    hand_state = game["hand_state"]
    user_player = game["table"].user_player

    if not user_player.is_active or not hand_state.get("waiting_for_user_action"):
        raise HTTPException(status_code=400, detail="Not user's turn to act")

    hand_state["waiting_for_user_action"] = False
    _execute_action(user_player, player_action.action, player_action.size, hand_state)

    _advance_game_state(session_id)

    return {"game_state": _get_sanitized_game_state(session_id)}


# --- Core Game Logic ---

def _start_new_hand(session_id: str):
    """Initializes a new hand."""
    game = game_sessions[session_id]
    table = game["table"]
    
    deck = [r + s for r in '23456789TJQKA' for s in 'cdhs']
    random.shuffle(deck)

    game["hand_state"] = {
        'pot': 0.0, 'board': [], 'to_call': 0.0, 'history': [], 
        'action_log': ["--- New Hand ---"], 'winner': None, 'street': 'preflop',
        'deck': deck, 'last_aggressor': None,
        'players_acted_this_street': set()
    }
    hand_state = game["hand_state"]
    
    table.move_dealer_button()

    for player in table.players:
        player.reset_for_hand()
        player.hole = [deck.pop(), deck.pop()]

    sb_player = table.get_player_at_position('SB')
    bb_player = table.get_player_at_position('BB')
    _execute_action(sb_player, "bet", 0.5, hand_state, is_blind=True)
    _execute_action(bb_player, "bet", 1.0, hand_state, is_blind=True)
    hand_state['last_aggressor'] = bb_player

    _advance_game_state(session_id)

def _advance_game_state(session_id: str):
    """The main orchestrator for the hand, advancing streets and betting rounds."""
    game = game_sessions[session_id]
    table = game["table"]
    hand_state = game["hand_state"]

    while True:
        if len(table.get_active_players()) <= 1:
            _handle_showdown(session_id)
            return

        is_user_turn = _run_betting_round(session_id)
        if is_user_turn:
            return

        streets = ['preflop', 'flop', 'turn', 'river']
        current_index = streets.index(hand_state['street'])
        
        if current_index >= len(streets) - 1:
            _handle_showdown(session_id)
            return

        next_street = streets[current_index + 1]
        hand_state.update({
            'street': next_street, 'to_call': 0, 'last_aggressor': None,
            'players_acted_this_street': set()
        })
        for p in table.players: p.contributed_this_street = 0
        
        hand_state['action_log'].append(f"--- {next_street.upper()} ---")
        deck = hand_state['deck']
        if next_street == 'flop':
            hand_state['board'].extend([deck.pop() for _ in range(3)])
        elif next_street in ['turn', 'river']:
            hand_state['board'].append(deck.pop())

def _run_betting_round(session_id: str) -> bool:
    """Manages a full betting round. Returns True if it's the user's turn."""
    game = game_sessions[session_id]
    table = game["table"]
    hand_state = game["hand_state"]
    street = hand_state['street']
    
    players_to_act = table.get_action_order(street)
    aggressor = hand_state.get('last_aggressor')
    
    if street != 'preflop' and aggressor is None and players_to_act:
        aggressor = players_to_act[-1] 

    while players_to_act:
        if len(table.get_active_players()) <= 1:
            return False

        player = players_to_act.pop(0)

        if not player.is_active:
            continue
        
        if player in hand_state['players_acted_this_street']:
            continue

        amount_to_call = max(0, hand_state['to_call'] - player.contributed_this_street)
        if player == aggressor and amount_to_call == 0:
            return False 

        if player.is_user:
            hand_state['action_log'].append(f"--- WAITING FOR YOUR ACTION ({player.current_position}) ---")
            hand_state["waiting_for_user_action"] = True
            return True
        
        game_state_for_bot = _build_player_game_state(player, street, hand_state)
        action, size = game["decision_engine"].get_optimal_action(game_state_for_bot, STRATEGY)
        action_reopened, new_aggressor = _execute_action(player, action, size, hand_state)

        if action_reopened:
            aggressor = new_aggressor
            hand_state['last_aggressor'] = new_aggressor
            players_to_act = [p for p in table.get_action_order(street) if p.is_active and p != new_aggressor]
            hand_state['players_acted_this_street'].clear()

    return False

def _execute_action(player, action, size, hand_state, is_blind=False):
    """Applies a player's action and returns if action was reopened."""
    amount_to_call = max(0, hand_state['to_call'] - player.contributed_this_street)
    actor_name = player.name
    log_message = ""
    action_reopened = False
    new_aggressor = None

    if action == 'fold':
        player.is_active = False
        log_message = f"{actor_name} ({player.current_position}) folds."
    elif action == 'check':
        log_message = f"{actor_name} ({player.current_position}) checks."
    elif action == 'call':
        amount = min(amount_to_call, player.stack)
        player.stack -= amount; player.contributed_this_street += amount; hand_state['pot'] += amount
        log_message = f"{actor_name} ({player.current_position}) calls {amount:.2f}."
    elif action in ['bet', 'raise']:
        amount = min(size, player.stack)
        player.stack -= amount; player.contributed_this_street += amount; hand_state['pot'] += amount
        hand_state['to_call'] = player.contributed_this_street
        action_word = "posts blind" if is_blind else "bets" if action == "bet" else "raises to"
        log_message = f"{actor_name} ({player.current_position}) {action_word} {amount:.2f}."
        action_reopened = True
        new_aggressor = player
    
    if not is_blind:
        hand_state['players_acted_this_street'].add(player)
    if log_message:
        hand_state['action_log'].append(log_message)
    return action_reopened, new_aggressor

def _handle_showdown(session_id: str):
    """Ends the hand and determines a winner."""
    game = game_sessions[session_id]
    hand_state = game["hand_state"]
    active_players = game["table"].get_active_players()
    
    if not active_players:
        hand_state['action_log'].append("Hand ended as all players folded.")
        return

    winner = active_players[0] # Simplified winner determination
    if len(active_players) == 1:
        hand_state['action_log'].append(f"{winner.name} ({winner.current_position}) wins uncontested pot.")
    else:
        hand_state['action_log'].append(f"--- Showdown ---")
        for p in active_players:
             hand_state['action_log'].append(f"{p.name} shows {' '.join(p.hole)}.")

    winner_message = f"{winner.name} wins the pot of {hand_state['pot']:.2f}!"
    hand_state['action_log'].append(winner_message)
    hand_state['winner'] = { 'name': winner.name, 'hand': ' '.join(winner.hole), 'pot': hand_state['pot'] }

def _build_player_game_state(player, street, hand_state):
    """Constructs the state dictionary for a player's decision."""
    return {
        'position': player.current_position, 'street': street,
        'history': hand_state['history'], 'pot': hand_state['pot'],
        'to_call': max(0, hand_state['to_call'] - player.contributed_this_street),
        'hole': player.hole, 'board': hand_state['board'],
    }

def _get_sanitized_game_state(session_id: str):
    """Prepares a version of the game state that is safe to send to the client."""
    game = game_sessions[session_id]
    table = game["table"]
    hand_state = game["hand_state"]
    user_player = table.user_player

    players_data = []
    for p in table.players:
        show_cards = p.is_user or (hand_state.get('winner') and p in table.get_active_players())
        players_data.append({
            "seat": p.seat_number, "name": p.name, "stack": p.stack,
            "position": p.current_position, "is_active": p.is_active,
            "is_user": p.is_user,
            "hole_cards": p.hole if show_cards else ["", ""],
            "contributed": p.contributed_this_street
        })

    return {
        "players": players_data, "pot": hand_state['pot'],
        "board": hand_state['board'],
        "to_call": max(0, hand_state['to_call'] - user_player.contributed_this_street),
        "is_users_turn": hand_state.get("waiting_for_user_action", False),
        "action_log": hand_state.get('action_log', []),
        "winner_info": hand_state.get('winner')
    }
