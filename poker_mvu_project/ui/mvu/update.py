"""
MVU Update Function - Pure reducers for poker table state
"""

from typing import Tuple, List
from dataclasses import replace
from .types import Model, Msg, Cmd, NextPressed, LoadHand, SeatState

def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """Pure update function - computes (Model, Cmds) from (Model, Msg)"""
    if isinstance(msg, NextPressed):
        print(f"Next pressed - cursor: {model.review_cursor}/{model.review_len}")
        if model.review_cursor < model.review_len - 1:
            new_model = replace(model, review_cursor=model.review_cursor + 1)
            return new_model, []
        return model, []
    
    if isinstance(msg, LoadHand):
        hand_data = msg.hand_data
        seats_data = hand_data.get("seats", {})
        seats = {
            int(k): SeatState(
                player_uid=v.get("player_uid", f"p_{k}"),
                name=v.get("name", f"Player {k}"),
                stack=v.get("stack", 1000),
                chips_in_front=v.get("chips_in_front", 0),
                folded=v.get("folded", False),
                all_in=v.get("all_in", False),
                cards=tuple(v.get("cards", [])),
                position=int(k)
            ) for k, v in seats_data.items()
        }
        
        new_model = replace(
            model,
            hand_id=hand_data.get("hand_id", ""),
            seats=seats,
            stacks={k: v.stack for k, v in seats.items()},
            board=tuple(hand_data.get("board", [])),
            pot=hand_data.get("pot", 0),
            to_act_seat=hand_data.get("to_act_seat"),
            legal_actions=frozenset(hand_data.get("legal_actions", [])),
            review_cursor=0,
            review_len=hand_data.get("review_len", 0)
        )
        return new_model, []
    
    return model, []