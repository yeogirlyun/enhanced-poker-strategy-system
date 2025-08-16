class TimerManager:
    """
    Centralized wrapper for Tkinter after() scheduling so timers can be
    cancelled on tab hide/unmount.
    """

    def __init__(self, tk_root) -> None:
        self.root = tk_root
        self._after_ids: set[str] = set()

    def after(self, ms: int, fn):
        after_id = self.root.after(ms, self._wrap(fn, after_id_ref=None))
        # Cannot capture after_id before it's created; store and best-effort
        # cleanup
        self._after_ids.add(after_id)
        return after_id

    def _wrap(self, fn, after_id_ref):
        def _inner():
            try:
                fn()
            finally:
                # Best-effort: we don't get the after_id here; callers may
                # remove manually; otherwise cancel_all will clear leftovers.
                pass
        return _inner

    def cancel(self, after_id) -> None:
        try:
            self.root.after_cancel(after_id)
        except Exception:
            pass
        finally:
            try:
                self._after_ids.remove(after_id)
            except KeyError:
                pass

    def cancel_all(self) -> None:
        for after_id in list(self._after_ids):
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass
        self._after_ids.clear()

    def dispose(self) -> None:
        self.cancel_all()
