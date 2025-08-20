from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..table.state import PokerTableState
from ..table.geometry import pot_center, actor_seat_xy


@dataclass
class BaseSessionManager:
    store: Any
    ppsm: Any
    game_director: Any
    effect_bus: Any
    theme_manager: Any | None = None

    def build_state(self, game_info: Dict[str, Any]) -> PokerTableState:
        table = {"width": 0, "height": 0}
        seats = game_info.get("players", []) or game_info.get("seats", [])
        board = game_info.get("board", [])
        pot = {"amount": int(game_info.get("pot", 0))}
        dealer = {"position": game_info.get("dealer_position", 0)}
        action = {
            "current_player": game_info.get("action_player", -1),
            "action_type": None,
            "amount": 0,
        }
        return PokerTableState(
            table=table,
            seats=seats,
            board=board,
            pot=pot,
            dealer=dealer,
            action=action,
            animation={},
            effects=[],
        )

    def emit_chip_to_pot(
        self,
        display_state: Dict[str, Any],
        actor_uid: str,
        amount: int,
        canvas_size: tuple[int, int],
    ) -> Dict[str, Any]:
        w, h = canvas_size
        from_x, from_y = actor_seat_xy(display_state, actor_uid, w, h)
        to_x, to_y = pot_center(w, h)
        return {
            "type": "CHIP_TO_POT",
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
            "amount": int(amount or 0),
        }


class PracticeSessionManager(BaseSessionManager):
    def start(self) -> None:
        self.ppsm.start_hand()
        state = self.build_state(self.ppsm.get_game_info())
        self.store.dispatch({"type": "INIT_PRACTICE_TABLE", "table": state.__dict__})

    def handle_player_action(self, player_index: int, action: str, amount: int,
                             canvas_size: tuple[int, int]) -> None:
        # Execute through PPSM
        self.ppsm.execute_action(player_index, action, amount)
        game_info = self.ppsm.get_game_info()
        state = self.build_state(game_info)
        seats = state.seats
        actor_uid = (
            seats[player_index].get("player_uid", f"P{player_index}")
            if player_index < len(seats)
            else f"P{player_index}"
        )
        effect = self.emit_chip_to_pot(
            {"seats": seats}, actor_uid, amount, canvas_size
        )
        self.store.dispatch({
            "type": "UPDATE_PRACTICE_TABLE",
            "table": state.__dict__,
            "effects": [effect],
        })


class GTOSessionManager(BaseSessionManager):
    def __init__(self, store, ppsm, game_director, effect_bus, theme_manager=None, gto_engine: Optional[Any] = None):
        super().__init__(store, ppsm, game_director, effect_bus, theme_manager)
        self.gto_engine = gto_engine

    def start(self) -> None:
        self.ppsm.start_hand()
        state = self.build_state(self.ppsm.get_game_info())
        self.store.dispatch({"type": "INIT_GTO_TABLE", "table": state.__dict__})

    def request_advice(self) -> None:
        if not self.gto_engine:
            return
        advice = self.gto_engine.calculate_best_action(self.ppsm.get_game_info())
        self.store.dispatch({"type": "SHOW_GTO_ADVICE", "advice": advice})


