"""
MVU Store - Manages Model state and executes Commands
"""

from typing import List, Callable, Optional, Any
import threading
from .types import Model, Msg, Cmd, IntentHandler, NextPressed, LoadHand
from .update import update

class MVUStore:
    def __init__(self, initial_model: Model):
        self.model = initial_model
        self.subscribers: List[Callable[[Model], None]] = []
        self._lock = threading.RLock()
    
    def subscribe(self, callback: Callable[[Model], None]) -> Callable[[], None]:
        with self._lock:
            self.subscribers.append(callback)
            callback(self.model)
            def unsubscribe():
                with self._lock:
                    if callback in self.subscribers:
                        self.subscribers.remove(callback)
            return unsubscribe
    
    def dispatch(self, msg: Msg) -> None:
        with self._lock:
            old_model = self.model
            new_model, commands = update(self.model, msg)
            
            if new_model != old_model:
                self.model = new_model
                for sub in self.subscribers[:]:
                    sub(new_model)

class MVUIntentHandler(IntentHandler):
    def __init__(self, store: MVUStore):
        self.store = store
    
    def on_click_next(self) -> None:
        self.store.dispatch(NextPressed())