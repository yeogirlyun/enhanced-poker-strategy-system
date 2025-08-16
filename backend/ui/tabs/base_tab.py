from tkinter import ttk
from typing import Callable, List


class BaseTab(ttk.Frame):
    def __init__(self, parent, session_id: str, services, store):
        super().__init__(parent)
        self.session_id = session_id
        self.services = services
        self.store = store
        self._unsubs: List[Callable[[], None]] = []

    def on_mount(self) -> None:
        pass

    def on_show(self) -> None:
        pass

    def on_hide(self) -> None:
        self._cleanup()

    def on_unmount(self) -> None:
        self._cleanup()

    def _cleanup(self) -> None:
        for unsub in self._unsubs:
            try:
                unsub()
            except Exception:
                pass
        self._unsubs.clear()
        try:
            timers = self.services.get_session(self.session_id, "timers")
            timers.cancel_all()
        except Exception:
            pass


