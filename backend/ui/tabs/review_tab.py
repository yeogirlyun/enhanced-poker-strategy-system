import tkinter as tk
from tkinter import ttk

from ..tabs.base_tab import BaseTab
from ..state.actions import SET_TABLE_DIM
from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager
from ..tableview.renderer_pipeline import RendererPipeline
from ..tableview.components.pot_display import PotDisplay
from ..tableview.components.table_felt import TableFelt
from ..tableview.components.seats import Seats
from ..tableview.components.community import Community
from ..tableview.components.dealer_button import DealerButton
from ..services.theme_manager import ThemeManager
from ..services.hands_repository import HandsRepository
from ..services.fpsm_adapter import FpsmEventAdapter
import importlib


class ReviewTab(BaseTab):
    def on_mount(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas_container = ttk.Frame(self)
        self.canvas_container.grid(row=0, column=0, sticky="nsew")
        self.canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_container.grid_columnconfigure(0, weight=1)

        self.cm = CanvasManager(self.canvas_container)
        self.lm = LayerManager(self.cm.canvas, self.cm.overlay)

        components = [
            TableFelt(),
            Seats(),
            DealerButton(),
            Community(),
            PotDisplay(),
        ]
        self.pipeline = RendererPipeline(self.cm, self.lm, components)

        def on_state_change(_state):
            self.pipeline.render_once(self.store.get_state())

        self._unsubs.append(self.store.subscribe(on_state_change))

        def push_dim():
            w, h = self.cm.size()
            if w > 1 and h > 1:
                self.store.dispatch({"type": SET_TABLE_DIM, "dim": (w, h)})

        # Bind size changes
        self.cm.canvas.bind("<Configure>", lambda e: push_dim(), add="+")

        # Simple theme profile switcher (temporary UI, menu-free)
        theme: ThemeManager = self.services.get_app("theme")
        profiles = theme.names()
        if profiles:
            switcher = ttk.Combobox(
                self,
                values=profiles,
                state="readonly",
                width=18,
            )
            try:
                switcher.set(theme.current_profile_name())
            except Exception:
                pass
            switcher.grid(row=1, column=0, sticky="e", padx=6, pady=4)

            def on_sel(_e=None):
                theme.set_profile(switcher.get())
                self.pipeline.render_once(self.store.get_state())

            switcher.bind("<<ComboboxSelected>>", on_sel)

        # Try to wire a real FPSM if available; otherwise fallback to demo
        self._fpsm_adapter = FpsmEventAdapter(self.store)
        wired = False
        try:
            mod = importlib.import_module(
                "backend.core.flexible_poker_state_machine"
            )
        except Exception:
            try:
                mod = importlib.import_module(
                    "core.flexible_poker_state_machine"
                )
            except Exception:
                mod = None
        if mod is not None:
            try:
                fsm = getattr(mod, "FlexiblePokerStateMachine")
                cfg = getattr(mod, "GameConfig")
                self._fpsm = fsm(cfg(num_players=6), mode="review")
                # ensure players list exists for count
                try:
                    self._fpsm._initialize_players()
                except Exception:
                    pass
                self._fpsm_adapter.attach(self._fpsm)
                try:
                    self._fpsm._emit_display_state_event()
                except Exception:
                    pass
                wired = True
            except Exception:
                wired = False
        if not wired:
            self.after(100, self._demo_snapshot)

        # Hands list for replay with filters
        repo = HandsRepository()
        srcs = repo.list_sources()
        ttk.Label(self, text="Source:").grid(row=2, column=0, sticky="w", padx=6)
        self._src_combo = ttk.Combobox(
            self,
            values=[disp for disp, _ in srcs] or ["(none)"],
            state="readonly",
            width=28,
        )
        if srcs:
            self._src_combo.set(srcs[0][0])
        self._src_combo.grid(row=3, column=0, sticky="w", padx=6, pady=(0, 4))

        ttk.Label(self, text="Search:").grid(row=4, column=0, sticky="w", padx=6)
        self._search = ttk.Entry(self, width=30)
        self._search.grid(row=5, column=0, sticky="w", padx=6, pady=(0, 6))

        ttk.Label(self, text="Hands:").grid(row=6, column=0, sticky="w", padx=6)
        self._hands_combo = ttk.Combobox(self, values=[], state="readonly", width=28)
        self._hands_combo.grid(row=7, column=0, sticky="w", padx=6, pady=2)
        self._hand_options = []

        def refresh_hands() -> None:
            base_path = None
            chosen = self._src_combo.get()
            for disp, path in srcs:
                if disp == chosen:
                    base_path = path
                    break
            options = repo.list_hands(base_path, self._search.get() or None)
            names = [name for name, _ in options]
            self._hand_options = options
            try:
                self._hands_combo.configure(values=names)
            except Exception:
                pass
            if names:
                self._hands_combo.set(names[0])
            else:
                self._hands_combo.set("")

        refresh_hands()

        def load_selected(_e=None):
            idx = self._hands_combo.current()
            if 0 <= idx < len(self._hand_options):
                path = self._hand_options[idx][1]
                snaps = repo.load_snapshots(path)
                if snaps:
                    # Apply sequentially first snapshot now
                    self._fpsm_adapter.apply_snapshot(snaps[0])
                    # Store for step navigation
                    self._snaps = snaps
                    self._snap_idx = 0
                    try:
                        updater = getattr(
                            self, "_update_play_buttons_state"
                        )
                        updater()
                    except Exception:
                        pass

        self._hands_combo.bind("<<ComboboxSelected>>", load_selected)
        self._src_combo.bind("<<ComboboxSelected>>", lambda _e=None: refresh_hands())
        self._search.bind("<KeyRelease>", lambda _e=None: refresh_hands())

            # Step controls and playback
            btns = ttk.Frame(self)
            btns.grid(row=8, column=0, sticky="w", padx=6, pady=(4, 8))

            def step(delta: int):
                snaps = getattr(self, "_snaps", None)
                if not snaps:
                    return
                i = getattr(self, "_snap_idx", 0) + delta
                i = max(0, min(len(snaps) - 1, i))
                self._snap_idx = i
                self._fpsm_adapter.apply_snapshot(snaps[i])

            prev_btn = ttk.Button(
                btns,
                text="◀ Prev",
                command=lambda: step(-1),
            )
            next_btn = ttk.Button(
                btns,
                text="Next ▶",
                command=lambda: step(1),
            )
            prev_btn.pack(side="left", padx=(0, 6))
            next_btn.pack(side="left")

            # Playback controls
            self._is_playing = False
            self._play_after_id = None
            self._speed_ms = 800

            def play():
                if self._is_playing:
                    return
                self._is_playing = True
                self._tick_play()

            def pause():
                self._is_playing = False
                try:
                    tm = self.services.get_session(self.session_id, "timers")
                    if self._play_after_id is not None:
                        tm.cancel(self._play_after_id)
                except Exception:
                    pass
                self._play_after_id = None

            play_btn = ttk.Button(btns, text="Play", command=play)
            pause_btn = ttk.Button(btns, text="Pause", command=pause)
            self._loop_var = tk.BooleanVar(value=False)
            loop_chk = ttk.Checkbutton(
                btns, text="Loop", variable=self._loop_var
            )
            play_btn.pack(side="left", padx=(12, 6))
            pause_btn.pack(side="left")
            loop_chk.pack(side="left", padx=(12, 0))

            ttk.Label(btns, text="Speed:").pack(side="left", padx=(12, 4))
            speed = ttk.Combobox(
                btns,
                values=["0.5x", "1x", "1.5x", "2x"],
                state="readonly",
                width=6,
            )
            speed.set("1x")
            speed.pack(side="left")

            def on_speed(_e=None):
                sel = speed.get()
                self._speed_ms = {
                    "0.5x": 1600,
                    "1x": 800,
                    "1.5x": 550,
                    "2x": 400,
                }.get(sel, 800)

            speed.bind("<<ComboboxSelected>>", on_speed)

            # Keyboard shortcuts
            def on_left(_e=None):
                step(-1)
                return "break"

            def on_right(_e=None):
                step(1)
                return "break"

            def on_space(_e=None):
                if self._is_playing:
                    pause()
                else:
                    play()
                return "break"

            self.bind("<Left>", on_left, add=True)
            self.bind("<Right>", on_right, add=True)
            self.bind("<space>", on_space, add=True)
            self._unsubs.append(lambda: self.unbind("<Left>"))
            self._unsubs.append(lambda: self.unbind("<Right>"))
            self._unsubs.append(lambda: self.unbind("<space>"))

            def _tick_play_inner():
                snaps = getattr(self, "_snaps", None)
                if not self._is_playing or not snaps:
                    return
                i = getattr(self, "_snap_idx", 0) + 1
                if i >= len(snaps):
                    if self._loop_var.get():
                        i = 0
                    else:
                        pause()
                        return
                self._snap_idx = i
                self._fpsm_adapter.apply_snapshot(snaps[i])
                try:
                    tm = self.services.get_session(self.session_id, "timers")
                    self._play_after_id = tm.after(
                        self._speed_ms, _tick_play_inner
                    )
                except Exception:
                    pass

            self._tick_play = _tick_play_inner

            def _update_buttons():
                has_snaps = bool(getattr(self, "_snaps", None))
                state = "normal" if has_snaps else "disabled"
                prev_btn.configure(state=state)
                next_btn.configure(state=state)
                play_btn.configure(state=state)
                pause_btn.configure(state=state)

            self._update_play_buttons_state = _update_buttons

    def _demo_snapshot(self):
        demo = {
            "pot": 120,
            "board": ["Ah", "7d", "2s"],
            "players": [{}, {}, {}, {}, {}, {}],
            "dealer_position": 2,
        }
        self._fpsm_adapter.apply_snapshot(demo)

    def on_show(self) -> None:
        self.pipeline.render_once(self.store.get_state())
