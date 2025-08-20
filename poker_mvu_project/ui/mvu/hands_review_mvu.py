"""
MVU-based Hands Review Tab
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
from .types import Model, TableRendererProps, LoadHand
from .store import MVUStore, MVUIntentHandler
from .view import MVUPokerTableRenderer

class MVUHandsReviewTab(ttk.Frame):
    def __init__(self, parent: tk.Widget, services: Any = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.services = services
        self.hands_data: List[Dict[str, Any]] = []
        self._setup_ui()
        self._initialize_mvu()
        self._load_hands_data()
    
    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew")
        
        self.hand_selector = ttk.Combobox(controls_frame, state="readonly")
        self.hand_selector.pack(side="left", padx=5)
        self.hand_selector.bind("<<ComboboxSelected>>", self._on_hand_selected)
    
    def _initialize_mvu(self) -> None:
        initial_model = Model.initial(session_mode="REVIEW")
        self.store = MVUStore(initial_model=initial_model)
        self.intent_handler = MVUIntentHandler(self.store)
        self.table_renderer = MVUPokerTableRenderer(self, intent_handler=self.intent_handler)
        self.table_renderer.grid(row=1, column=0, sticky="nsew")
        self.unsubscribe = self.store.subscribe(self._on_model_changed)

    def _load_hands_data(self) -> None:
        self.hands_data = self._create_sample_hands()
        self.hand_selector["values"] = [h["hand_id"] for h in self.hands_data]
        if self.hands_data:
            self.hand_selector.current(0)
            self._load_hand(0)

    def _on_hand_selected(self, event=None) -> None:
        self._load_hand(self.hand_selector.current())

    def _load_hand(self, index: int) -> None:
        if 0 <= index < len(self.hands_data):
            hand_data = self.hands_data[index]
            self.store.dispatch(LoadHand(hand_data=hand_data))
    
    def _on_model_changed(self, model: Model) -> None:
        if self.table_renderer:
            props = TableRendererProps.from_model(model)
            self.table_renderer.render(props)

    def _create_sample_hands(self) -> List[Dict[str, Any]]:
        return [
            {
                "hand_id": "SAMPLE_001",
                "seats": {
                    0: {"name": "Hero", "stack": 1000, "cards": ["As", "Kh"]},
                    1: {"name": "Villain", "stack": 1000, "cards": ["Qd", "Jc"]}
                },
                "pot": 60,
                "board": ["Ah", "Kd", "7s"],
                "to_act_seat": 0,
                "legal_actions": ["BET", "CHECK"],
                "review_len": 5
            },
            {
                "hand_id": "SAMPLE_002", 
                "seats": {
                    0: {"name": "Hero", "stack": 800, "cards": ["Qs", "Qh"]},
                    1: {"name": "Villain", "stack": 1200, "cards": ["Ac", "Kc"]},
                    2: {"name": "Fish", "stack": 500, "cards": ["7d", "2s"]}
                },
                "pot": 150,
                "board": ["Qc", "Jh", "Ts", "9d"],
                "to_act_seat": 1,
                "legal_actions": ["BET", "CHECK"],
                "review_len": 8
            }
        ]

    def dispose(self) -> None:
        if hasattr(self, 'unsubscribe'):
            self.unsubscribe()