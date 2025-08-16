from typing import Any, Dict


class ServiceContainer:
    """
    Lightweight service registry with app-wide and session-scoped services.
    """

    def __init__(self) -> None:
        self.app_scope: Dict[str, Any] = {}
        self.session_scopes: Dict[str, Dict[str, Any]] = {}

    def provide_app(self, name: str, service: Any) -> None:
        self.app_scope[name] = service

    def get_app(self, name: str) -> Any:
        return self.app_scope[name]

    def provide_session(
        self, session_id: str, name: str, service: Any
    ) -> None:
        self.session_scopes.setdefault(session_id, {})[name] = service

    def get_session(self, session_id: str, name: str) -> Any:
        return self.session_scopes[session_id][name]

    def dispose_session(self, session_id: str) -> None:
        scope = self.session_scopes.pop(session_id, {})
        for service in scope.values():
            if hasattr(service, "dispose"):
                try:
                    service.dispose()
                except Exception:
                    # Best-effort cleanup
                    pass
