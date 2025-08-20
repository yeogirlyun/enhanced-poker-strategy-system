import tkinter as tk
from tkinter import ttk

from ..renderers.poker_table_renderer import PokerTableRenderer
from ..table.state import PokerTableState
from ..session.managers import PracticeSessionManager


class PracticeSessionTab(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.services = services
        self.store = services.get_app("store")
        self.event_bus = services.get_app("event_bus")
        self.theme = services.get_app("theme")

        # Renderer
        self.table_renderer = PokerTableRenderer(
            self,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme,
        )
        self.table_renderer.pack(fill="both", expand=True)

        # Connect EffectBus (if present) to renderer for animation bridge
        try:
            from ..services.effect_bus import EffectBus
            self.effect_bus = EffectBus(event_bus=self.event_bus)
            self.effect_bus.renderer = self.table_renderer
        except Exception:
            self.effect_bus = None

        # PPSM and manager
        self.ppsm = None
        try:
            # Add the backend directory to the path for imports
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
            
            # Create default game config for practice session
            config = GameConfig(
                num_players=2,
                small_blind=1.0,
                big_blind=2.0,
                starting_stack=200.0
            )
            self.ppsm = PurePokerStateMachine(config)
        except Exception as e:
            print(f"⚠️ PPSM import failed: {e}")
            self.ppsm = None

        from ..services.game_director import GameDirector
        self.game_director = GameDirector(event_bus=self.event_bus)

        self.manager = PracticeSessionManager(
            store=self.store,
            ppsm=self.ppsm,
            game_director=self.game_director,
            effect_bus=self.effect_bus,
            theme_manager=self.theme,
        )
        self.manager.start()

        # Subscribe store → renderer
        self.store.subscribe(self._on_store_change)

    def _on_store_change(self, state=None):
        state = state or self.store.get_state()
        table = state.get("table", {})
        if table:
            try:
                pts = PokerTableState(**table)
            except Exception:
                return
            self.table_renderer.render(pts)

    def _handle_renderer_intent(self, intent: dict):
        if intent.get("type") == "REQUEST_ANIMATION" and self.event_bus:
            payload = intent.get("payload", {})
            name = payload.get("name") or ("chips_to_pot" if payload.get("type") == "CHIP_TO_POT" else None)
            if name:
                self.event_bus.publish("effect_bus:animate", {"name": name, "args": payload})


