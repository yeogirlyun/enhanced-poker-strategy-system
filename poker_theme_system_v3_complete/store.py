from typing import Any, Callable, Dict, List

Reducer = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


class Store:
    """
    Minimal Redux-like store for UI state.
    """

    def __init__(
        self, initial_state: Dict[str, Any], reducer: Reducer
    ) -> None:
        self._state = initial_state
        self._reducer = reducer
        self._subs: List[Callable[[Dict[str, Any]], None]] = []

    def get_state(self) -> Dict[str, Any]:
        return self._state

    def dispatch(self, action: Dict[str, Any]) -> None:
        next_state = self._reducer(self._state, action)
        if next_state is not self._state:
            self._state = next_state
            for cb in list(self._subs):
                cb(self._state)

    def subscribe(
        self, cb: Callable[[Dict[str, Any]], None]
    ) -> Callable[[], None]:
        self._subs.append(cb)

        def unsub() -> None:
            try:
                self._subs.remove(cb)
            except ValueError:
                pass

        return unsub
