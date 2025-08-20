"""
MVU View - Pure rendering components
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from .types import TableRendererProps, IntentHandler

class MVUPokerTableRenderer(ttk.Frame):
    def __init__(self, parent: tk.Widget, intent_handler: Optional[IntentHandler] = None):
        super().__init__(parent)
        self.intent_handler = intent_handler or DummyIntentHandler()
        self.current_props: Optional[TableRendererProps] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, width=800, height=600, bg="#0D4F3C")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, sticky="ew")
        
        self.next_btn = ttk.Button(controls_frame, text="Next", 
                                 command=self.intent_handler.on_click_next)
        self.next_btn.pack(side="left")
        
        self.status_label = ttk.Label(controls_frame, text="Ready")
        self.status_label.pack(side="left")

    def render(self, props: TableRendererProps) -> None:
        if self.current_props == props:
            return
        
        self.current_props = props
        self._update_controls(props)
        self._render_table(props)
    
    def _update_controls(self, props: TableRendererProps) -> None:
        status_text = f"Review: {props.review_cursor}/{props.review_len}"
        if props.to_act_seat is not None:
            status_text += f" | Acting: Seat {props.to_act_seat}"
        self.status_label.config(text=status_text)
        
    def _render_table(self, props: TableRendererProps) -> None:
        self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width <= 1:
            width, height = 800, 600

        # Draw table
        self.canvas.create_oval(50, 50, width - 50, height - 50, 
                               fill="#0D4F3C", outline="#2D5016", width=3)
        self._draw_seats(props, width, height)
        self._draw_pot(props, width, height)

    def _draw_seats(self, props: TableRendererProps, width: int, height: int) -> None:
        import math
        center_x, center_y = width / 2, height / 2
        radius_x, radius_y = (width - 100) / 2, (height - 100) / 2
        
        for seat_num, seat_state in props.seats.items():
            angle = (seat_num / max(len(props.seats), 1)) * 2 * math.pi - math.pi / 2
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            color = "#FFD700" if seat_state.acting else "#8B4513"
            if seat_state.folded:
                color = "#696969"
            
            self.canvas.create_rectangle(x - 50, y - 25, x + 50, y + 25, fill=color)
            self.canvas.create_text(x, y - 10, text=seat_state.name, fill="white")
            self.canvas.create_text(x, y + 10, text=f"${seat_state.stack}", fill="white")

    def _draw_pot(self, props: TableRendererProps, width: int, height: int) -> None:
        center_x, center_y = width / 2, height / 2
        self.canvas.create_text(center_x, center_y, text=f"Pot: ${props.pot}", 
                               font=("Arial", 16, "bold"), fill="white")

class DummyIntentHandler:
    def on_click_next(self) -> None:
        print("Dummy: Next")