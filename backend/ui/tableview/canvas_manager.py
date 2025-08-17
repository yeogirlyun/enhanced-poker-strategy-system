import tkinter as tk
import importlib


class CanvasManager:
    def __init__(self, parent):
        # Resolve theme dynamically to avoid static import issues
        # Start with a neutral bg; components draw felt based on ThemeManager
        self.canvas = tk.Canvas(parent, bg="#000000", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # Optional overlay canvas for animations; safe default None
        self.overlay = None
        self._configure_after_id = None
        self.canvas.bind("<Configure>", self._on_configure, add="+")

    def _on_configure(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        try:
            if self.overlay is not None:
                self.overlay.lift(self.canvas)
        except Exception:
            pass

    def size(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # If canvas not sized yet, try to get requested size
        if w <= 1 or h <= 1:
            try:
                w = self.canvas.winfo_reqwidth()
                h = self.canvas.winfo_reqheight()
            except Exception:
                pass
                
        return w, h


