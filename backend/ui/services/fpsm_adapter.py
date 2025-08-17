from __future__ import annotations

from typing import Any, Dict, List, Callable


class FpsmEventAdapter:
    """
    Adapts FlexiblePokerStateMachine events to store actions expected by the
    new UI pipeline. It does not own timing or scheduling.
    """

    def __init__(self, store):
        self.store = store
        self._detach: Callable[[], None] | None = None

    # --- FPSM listener API ---
    def on_event(self, event: Any) -> None:  # matches EventListener
        try:
            if getattr(event, "event_type", "") == "display_state_update":
                data = (getattr(event, "data", {}) or {}).get("display_state", {})
                self._apply_display_state(data)
        except Exception:
            pass

    def attach(self, fsm: Any) -> None:
        if hasattr(fsm, "add_event_listener") and callable(fsm.add_event_listener):
            fsm.add_event_listener(self)

            def _rm() -> None:
                try:
                    fsm.remove_event_listener(self)
                except Exception:
                    pass

            self._detach = _rm

    def detach(self) -> None:
        if self._detach:
            try:
                self._detach()
            finally:
                self._detach = None

    # --- Direct mapping (for tests/demo) ---
    def apply_snapshot(self, snapshot: Dict[str, Any]) -> None:
        self._apply_display_state(snapshot)

    # --- Internal ---
    def _apply_display_state(self, ds: Dict[str, Any]) -> None:
        pot = int(ds.get("pot") or 0)
        board = ds.get("board") or []
        players: List[Dict[str, Any]] = ds.get("players") or []
        dealer = ds.get("dealer_position") or 0

        self.store.dispatch({"type": "SET_POT", "amount": pot})
        self.store.dispatch({"type": "SET_BOARD", "board": board})
        
        # Transform players data to seats format for UI
        seats_data = []
        for i, player in enumerate(players):
            seat_data = {
                "name": player.get("name", f"Player{i+1}"),
                "stack": player.get("stack", 1000),
                "cards": player.get("cards", []),
                "position": player.get("position", ""),
                "current_bet": player.get("current_bet", 0),
                "folded": player.get("has_folded", False),
                "all_in": player.get("stack", 1000) == 0,
                "acting": i == ds.get("action_player", -1),
                "active": player.get("is_active", True)
            }
            seats_data.append(seat_data)
        
        self.store.dispatch({"type": "SET_SEATS", "seats": seats_data})
        self.store.dispatch({"type": "SET_DEALER", "dealer": int(dealer)})


