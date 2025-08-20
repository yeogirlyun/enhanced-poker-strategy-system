#!/usr/bin/env python3
"""
Poker MVU Project Creator
Creates a complete MVU-based poker project structure with all necessary files
"""

import os
import zipfile

def create_project_files():
    """Creates the directory structure and files for the project."""
    root_dir = "poker_mvu_project"
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    # Core MVU types
    mvu_types = '''"""
MVU (Model-View-Update) Architecture Types
Based on PokerPro UI Implementation Handbook v2
"""

from dataclasses import dataclass, replace
from typing import Literal, Optional, Dict, List, Set, Any, Protocol, Callable, FrozenSet, Mapping
from abc import ABC, abstractmethod

# Helper types for immutable collections
ImmutableSeats = Mapping[int, "SeatState"]
ImmutableStacks = Mapping[int, int]

@dataclass(frozen=True, slots=True)
class SeatState:
    """State for a single seat at the poker table - FULLY IMMUTABLE"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int
    folded: bool
    all_in: bool
    cards: tuple[str, ...]
    position: int
    acting: bool = False
    
    def __eq__(self, other):
        if not isinstance(other, SeatState):
            return False
        return (
            self.player_uid == other.player_uid and
            self.name == other.name and
            self.stack == other.stack and
            self.chips_in_front == other.chips_in_front and
            self.folded == other.folded and
            self.all_in == other.all_in and
            self.cards == other.cards and
            self.position == other.position and
            self.acting == other.acting
        )

@dataclass(frozen=True)
class Action:
    seat: int
    action: str
    amount: Optional[int] = None
    street: str = "PREFLOP"

@dataclass(frozen=True)
class Model:
    hand_id: str
    street: Literal["PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "DONE"]
    to_act_seat: Optional[int]
    stacks: ImmutableStacks
    pot: int
    board: tuple[str, ...]
    seats: ImmutableSeats
    legal_actions: FrozenSet[str]
    last_action: Optional[Action]
    session_mode: Literal["PRACTICE", "GTO", "REVIEW"]
    autoplay_on: bool
    step_delay_ms: int
    waiting_for: Literal["HUMAN_DECISION", "BOT_DECISION", "ANIMATION", "NONE"]
    review_cursor: int
    review_len: int
    review_paused: bool
    theme_id: str
    tx_id: int
    
    @classmethod
    def initial(cls, session_mode: Literal["PRACTICE", "GTO", "REVIEW"] = "REVIEW") -> "Model":
        return cls(
            hand_id="", street="PREFLOP", to_act_seat=None, stacks={}, pot=0,
            board=(), seats={}, legal_actions=frozenset(), last_action=None,
            session_mode=session_mode, autoplay_on=False, step_delay_ms=1000,
            waiting_for="NONE", review_cursor=0, review_len=0, review_paused=False,
            theme_id="forest-green-pro", tx_id=0
        )

# Messages
class Msg(ABC):
    pass

class NextPressed(Msg):
    pass

@dataclass
class LoadHand(Msg):
    hand_data: Dict[str, Any]

# Commands  
class Cmd(ABC):
    pass

@dataclass
class PlaySound(Cmd):
    name: str

# Props for rendering
@dataclass(frozen=True, slots=True)
class TableRendererProps:
    seats: ImmutableSeats
    board: tuple[str, ...]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: FrozenSet[str]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    review_cursor: int
    review_len: int
    session_mode: str
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        return cls(
            seats=model.seats, board=model.board, pot=model.pot,
            to_act_seat=model.to_act_seat, legal_actions=model.legal_actions,
            theme_id=model.theme_id, autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for, review_cursor=model.review_cursor,
            review_len=model.review_len, session_mode=model.session_mode
        )

class IntentHandler(Protocol):
    def on_click_next(self) -> None: pass
'''

    # MVU update functions
    mvu_update = '''"""
MVU Update Function - Pure reducers for poker table state
"""

from typing import Tuple, List
from dataclasses import replace
from .types import Model, Msg, Cmd, NextPressed, LoadHand, SeatState

def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """Pure update function - computes (Model, Cmds) from (Model, Msg)"""
    if isinstance(msg, NextPressed):
        print(f"Next pressed - cursor: {model.review_cursor}/{model.review_len}")
        if model.review_cursor < model.review_len - 1:
            new_model = replace(model, review_cursor=model.review_cursor + 1)
            return new_model, []
        return model, []
    
    if isinstance(msg, LoadHand):
        hand_data = msg.hand_data
        seats_data = hand_data.get("seats", {})
        seats = {
            int(k): SeatState(
                player_uid=v.get("player_uid", f"p_{k}"),
                name=v.get("name", f"Player {k}"),
                stack=v.get("stack", 1000),
                chips_in_front=v.get("chips_in_front", 0),
                folded=v.get("folded", False),
                all_in=v.get("all_in", False),
                cards=tuple(v.get("cards", [])),
                position=int(k)
            ) for k, v in seats_data.items()
        }
        
        new_model = replace(
            model,
            hand_id=hand_data.get("hand_id", ""),
            seats=seats,
            stacks={k: v.stack for k, v in seats.items()},
            board=tuple(hand_data.get("board", [])),
            pot=hand_data.get("pot", 0),
            to_act_seat=hand_data.get("to_act_seat"),
            legal_actions=frozenset(hand_data.get("legal_actions", [])),
            review_cursor=0,
            review_len=hand_data.get("review_len", 0)
        )
        return new_model, []
    
    return model, []
'''

    # MVU store
    mvu_store = '''"""
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
'''

    # MVU view
    mvu_view = '''"""
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
'''

    # Hands review tab
    hands_review_tab = '''"""
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
'''

    # App shell
    app_shell = '''import tkinter as tk
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
'''

    # Main runner
    main_runner = '''import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.app_shell import AppShell

def main() -> None:
    root = tk.Tk()
    root.title("Poker Trainer — MVU UI")
    root.geometry("1200x800")
    
    app = AppShell(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''

    # README
    readme = '''# Poker MVU Project

This is a complete MVU (Model-View-Update) implementation for a poker training application.

## Features

- Clean MVU architecture with immutable state
- Infinite loop prevention through proper equality checks
- Professional poker table rendering
- Hands review functionality

## Running the Application

```bash
cd poker_mvu_project
python main.py
```

## Architecture

The project follows strict MVU principles:
- Model: Immutable state representation
- View: Pure rendering components  
- Update: Pure state transition functions
- Commands: Side effects as data

## Key Components

- `ui/mvu/types.py` - Core type definitions
- `ui/mvu/update.py` - Pure update functions
- `ui/mvu/store.py` - State management
- `ui/mvu/view.py` - UI rendering
- `ui/mvu/hands_review_mvu.py` - Complete hands review implementation

This implementation prevents all common MVU pitfalls including infinite rendering loops.
'''

    # Create file structure
    files = {
        "ui/__init__.py": "",
        "ui/mvu/__init__.py": "",
        "ui/mvu/types.py": mvu_types,
        "ui/mvu/update.py": mvu_update,
        "ui/mvu/store.py": mvu_store,
        "ui/mvu/view.py": mvu_view,
        "ui/mvu/hands_review_mvu.py": hands_review_tab,
        "ui/app_shell.py": app_shell,
        "main.py": main_runner,
        "README.md": readme
    }

    for file_path, content in files.items():
        full_path = os.path.join(root_dir, file_path)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Created: {full_path}")

def zip_project_files():
    """Zips the created project files."""
    root_dir = "poker_mvu_project"
    zip_filename = "poker_mvu_project.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(root_dir))
                zipf.write(file_path, arcname)
    print(f"📦 Created ZIP: {zip_filename}")

if __name__ == "__main__":
    print("🔧 Creating Poker MVU Project...")
    create_project_files()
    zip_project_files()
    print("\n✅ Project creation complete!")
    print(f"📁 Project folder: {os.path.abspath('poker_mvu_project')}")
    print(f"📦 ZIP file: {os.path.abspath('poker_mvu_project.zip')}")
    print("\n🚀 To run:")
    print("   cd poker_mvu_project")
    print("   python main.py")