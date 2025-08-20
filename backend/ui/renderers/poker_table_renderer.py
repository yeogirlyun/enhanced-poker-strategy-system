"""
Pure state-driven poker table renderer.
This component ONLY renders – no business logic, no state management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from tkinter import ttk

from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager
from ..tableview.renderer_pipeline import RendererPipeline
from ..tableview.components.table_felt import TableFelt
from ..tableview.components.seats import Seats
from ..tableview.components.community import Community
from ..tableview.components.pot_display import PotDisplay
from ..tableview.components.bet_display import BetDisplay
from ..tableview.components.dealer_button import DealerButton
from ..tableview.components.player_highlighting import PlayerHighlighting


from ..table.state import PokerTableState


class PokerTableRenderer(ttk.Frame):
    """
    Pure rendering component for poker table.
    Renders state, emits intents, no business logic.
    """

    def __init__(
        self,
        parent,
        intent_handler: Optional[Callable[[Dict[str, Any]], None]] = None,
        theme_manager: Any = None,
    ) -> None:
        super().__init__(parent)
        self.intent_handler = intent_handler or (lambda _: None)
        self.theme_manager = theme_manager

        self._setup_rendering_pipeline()
        self.current_state: Optional[PokerTableState] = None
        self.renderer = None  # Will be initialized when canvas is ready
        self._ready_callbacks = []  # Callbacks to call when renderer is ready

    def _setup_rendering_pipeline(self) -> None:
        # Create CanvasManager first; it will initialize canvas lazily
        self.canvas_manager = CanvasManager(self)

        # Prepare components
        self.components = [
            TableFelt(),
            Seats(),
            Community(),
            BetDisplay(),
            PotDisplay(),
            DealerButton(),
            PlayerHighlighting(),
        ]

        # LayerManager depends on a real canvas; set up when ready
        def _finalize_pipeline():
            try:
                print(f"🔧 PokerTableRenderer: Starting pipeline finalization...")
                print(f"🔧 PokerTableRenderer: Canvas: {self.canvas_manager.canvas}")
                print(f"🔧 PokerTableRenderer: Overlay: {self.canvas_manager.overlay}")
                
                self.layer_manager = LayerManager(
                    self.canvas_manager.canvas, self.canvas_manager.overlay
                )
                print(f"🔧 PokerTableRenderer: LayerManager created: {self.layer_manager}")
                
                self.renderer = RendererPipeline(
                    self.canvas_manager, self.layer_manager, self.components
                )
                print(f"🔧 PokerTableRenderer: Renderer created: {self.renderer is not None}")
                print(f"🔧 PokerTableRenderer: Renderer object: {self.renderer}")
                
                # Grid now that canvas exists
                try:
                    self.canvas_manager.canvas.grid(row=0, column=0, sticky="nsew")
                    print(f"🔧 PokerTableRenderer: Canvas gridded successfully")
                except Exception as grid_e:
                    print(f"⚠️ PokerTableRenderer: Canvas grid error: {grid_e}")
                    
                self.grid_columnconfigure(0, weight=1)
                self.grid_rowconfigure(0, weight=1)
                print("✅ PokerTableRenderer: Pipeline finalized successfully")
                print(f"🔍 PokerTableRenderer: Final renderer state: {hasattr(self, 'renderer')} / {self.renderer is not None}")
                
                # Notify any waiting callbacks that renderer is ready
                print(f"🔄 PokerTableRenderer: Processing {len(self._ready_callbacks)} ready callbacks")
                for i, callback in enumerate(self._ready_callbacks):
                    try:
                        print(f"🔄 PokerTableRenderer: Calling ready callback {i+1}")
                        callback()
                        print(f"✅ PokerTableRenderer: Ready callback {i+1} completed")
                    except Exception as cb_e:
                        print(f"⚠️ PokerTableRenderer: Ready callback {i+1} error: {cb_e}")
                        import traceback
                        traceback.print_exc()
                self._ready_callbacks.clear()
                print(f"🔄 PokerTableRenderer: All callbacks processed, renderer final check: {self.renderer is not None}")
                
            except Exception as e:
                print(f"⚠️ PokerTableRenderer finalize error: {e}")
                import traceback
                traceback.print_exc()
                # Initialize renderer to None to prevent AttributeError
                self.renderer = None

        if getattr(self.canvas_manager, 'is_ready', lambda: False)():
            _finalize_pipeline()
        else:
            # Defer until the canvas is created
            try:
                self.canvas_manager.defer_render(lambda: _finalize_pipeline())
            except Exception:
                pass

    def render(self, state: PokerTableState) -> None:
        if state != self.current_state:
            # Check if renderer is initialized
            has_attr = hasattr(self, 'renderer')
            is_not_none = has_attr and self.renderer is not None
            print(f"🔍 PokerTableRenderer: Render check - hasattr: {has_attr}, not None: {is_not_none}")
            
            if not has_attr or self.renderer is None:
                print("⚠️ PokerTableRenderer: Renderer not ready, deferring render")
                # Defer render until renderer is ready
                self._ready_callbacks.append(lambda: self.render(state))
                print(f"🔄 PokerTableRenderer: Render deferred via ready callback (callbacks: {len(self._ready_callbacks)})")
                return
            
            # Render table
            self.renderer.render_once(state.__dict__)
            # Process declarative effects
            self._process_effects(state.effects)
            self.current_state = state

    def _process_effects(self, effects: List[Dict[str, Any]]) -> None:
        """Emit intents for visual effects to be handled externally."""
        for effect in effects or []:
            et = effect.get("type")
            if et in {"CHIP_TO_POT", "POT_TO_WINNER", "HIGHLIGHT_PLAYER"}:
                # Pure visual effects handled here; acoustic handled by EffectBus
                self._emit_intent(
                    {"type": "REQUEST_ANIMATION", "payload": effect}
                )

    def _emit_intent(self, intent: Dict[str, Any]) -> None:
        try:
            self.intent_handler(intent)
        except Exception:
            pass


