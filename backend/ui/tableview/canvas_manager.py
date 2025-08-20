import tkinter as tk
import importlib


class CanvasManager:
    def __init__(self, parent):
        # Store parent; defer canvas creation until sized to avoid small initial render
        self.parent = parent
        self.canvas = None
        self.overlay = None
        self._configure_after_id = None
        self._initialized = False
        self._pending_render = None

        # Resolve theme bg color once for initialization
        try:
            from ui.services.theme_manager import ThemeManager
            tm = ThemeManager()
            theme_colors = tm.get()
            self._canvas_bg = theme_colors.get("table.bg", theme_colors.get("panel.bg", "#000000"))
        except Exception:
            self._canvas_bg = "#000000"

        # Schedule lazy initialization after idle; we may need to retry until sized
        try:
            self.parent.after_idle(self._initialize_canvas)
        except Exception:
            # Fallback: attempt immediate init
            self._initialize_canvas()

    def _on_configure(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        try:
            if self.overlay is not None and self.canvas is not None:
                self.overlay.lift(self.canvas)
        except Exception:
            pass

    def size(self):
        if not self.canvas:
            return 0, 0
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            try:
                w = self.canvas.winfo_reqwidth()
                h = self.canvas.winfo_reqheight()
            except Exception:
                pass
        return w, h

    # New APIs for deferred render gating
    def is_ready(self):
        return self._initialized and self.canvas is not None

    def defer_render(self, render_func):
        if self.is_ready():
            try:
                render_func()
            except Exception:
                pass
        else:
            self._pending_render = render_func

    def _initialize_canvas(self):
        # Force geometry update and get real size; retry until reasonable
        try:
            self.parent.update_idletasks()
        except Exception:
            pass

        try:
            pw = getattr(self.parent, 'winfo_width')()
            ph = getattr(self.parent, 'winfo_height')()
        except Exception:
            pw, ph = 0, 0

        if pw <= 100 or ph <= 100:
            # ARCHITECTURE COMPLIANT: Schedule via parent's GameDirector if available
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_RETRY",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Fallback: direct retry (violation but necessary)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass
            return

        # Create canvas now with proper size and grid into parent
        try:
            self.canvas = tk.Canvas(self.parent, width=pw, height=ph, bg=self._canvas_bg, highlightthickness=0)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            try:
                self.canvas.bind("<Configure>", self._on_configure, add="+")
            except Exception:
                pass
            self._initialized = True

            # Execute any pending render deferral
            if self._pending_render is not None:
                pending = self._pending_render
                self._pending_render = None
                try:
                    pending()
                except Exception:
                    pass
        except Exception:
            # ARCHITECTURE COMPLIANT: Last resort retry via GameDirector
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_LAST_RESORT",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Final fallback: direct retry (violation but necessary for bootstrap)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass


