import tkinter as tk
from tkinter import ttk
from .mvu.hands_review_mvu import MVUHandsReviewTab

class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.pack(fill="both", expand=True)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Mock services
        class MockServices:
            def get_app(self, name): return None
        
        self.services = MockServices()
        self._add_tab("Hands Review", MVUHandsReviewTab)

    def _add_tab(self, title: str, TabClass):
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)