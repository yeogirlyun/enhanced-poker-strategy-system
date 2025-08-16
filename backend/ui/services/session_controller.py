from __future__ import annotations

from typing import Any, Callable, Dict


class SessionController:
    """
    Bridges an FPSM-like engine to the UI store by translating snapshots
    to store actions. The controller does not schedule time; GameDirector
    (out of scope here) would drive progression.
    """

    def __init__(self, session_id: str, services, store, fsm: Any):
        self.session_id = session_id
        self.services = services
        self.store = store
        self.fsm = fsm
        self._unsubs: list[Callable[[], None]] = []

    def start(self) -> None:
        # Subscribe to FSM updates if available
        if hasattr(self.fsm, "subscribe"):
            self._unsubs.append(
                self.fsm.subscribe("snapshot", self._on_snapshot)
            )

    def _on_snapshot(self, snapshot: Dict[str, Any]) -> None:
        # Expected snapshot fields: pot, seats, board, dealer
        if "pot" in snapshot:
            amt = int(snapshot.get("pot") or 0)
            self.store.dispatch({"type": "SET_POT", "amount": amt})
        if "seats" in snapshot:
            self.store.dispatch(
                {"type": "SET_SEATS", "seats": snapshot["seats"]}
            )
        if "board" in snapshot:
            self.store.dispatch(
                {"type": "SET_BOARD", "board": snapshot["board"]}
            )
        if "dealer" in snapshot:
            self.store.dispatch(
                {"type": "SET_DEALER", "dealer": snapshot["dealer"]}
            )

    def dispose(self) -> None:
        for u in self._unsubs:
            try:
                u()
            except Exception:
                pass
        self._unsubs.clear()

