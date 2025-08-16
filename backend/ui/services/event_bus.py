from collections import defaultdict
from typing import Any, Callable, Dict, List


class EventBus:
    """
    Simple in-memory pub/sub event bus with string topics.

    Topics should be namespaced using a session identifier to prevent
    cross-talk between tabs/sessions.
    Example: f"{session_id}:ui:action".
    """

    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def topic(self, session_id: str, name: str) -> str:
        return f"{session_id}:{name}"

    def subscribe(
        self, topic: str, handler: Callable[[Any], None]
    ) -> Callable[[], None]:
        self._subs[topic].append(handler)

        def unsubscribe() -> None:
            try:
                self._subs[topic].remove(handler)
            except ValueError:
                pass

        return unsubscribe

    def publish(self, topic: str, payload: Any) -> None:
        # Copy list to avoid mutation during iteration
        for handler in list(self._subs.get(topic, [])):
            handler(payload)


