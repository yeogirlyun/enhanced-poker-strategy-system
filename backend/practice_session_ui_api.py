#!/usr/bin/env python3
"""
Practice Session UI Module - API Client Version
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
import requests
import threading
from queue import Queue

from sound_manager import SoundManager
from gui_models import THEME, FONTS
from tooltips import ToolTip

# API Client for communicating with FastAPI backend
class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def new_game(self):
        response = requests.post(f"{self.base_url}/api/game/new")
        response.raise_for_status()
        return response.json()

    def post_action(self, session_id, action, size=0.0):
        payload = {"action": action, "size": size}
        response = requests.post(f"{self.base_url}/api/game/{session_id}/action", json=payload)
        response.raise_for_status()
        return response.json()

class PracticeSessionUI(ttk.Frame):
    """
    A graphical, interactive practice session tab that communicates with FastAPI backend.
    """
    
    def __init__(self, parent, strategy_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.strategy_data = strategy_data
        
        # Initialize API Client and Sound Manager
        self.api_client = ApiClient()
        self.session_id = None
        self.sfx = SoundManager()

        # --- NEW: Queue for thread-safe UI updates ---
        self.response_queue = Queue()

        # UI components
        self.num_players = 6
        self.player_seats = []
        self.community_card_labels = []
        self.human_action_controls = {}
        
        self._setup_ui()
        
        # --- NEW: Start a loop to process responses from the backend ---
        self.after(100, self._process_api_responses)

    def _setup_ui(self):
        """Sets up the UI layout with a responsive grid."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)

        # Main canvas for the poker table
        self.canvas = tk.Canvas(self, bg=THEME["primary_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Right-side panel for messages
        right_panel_frame = ttk.Frame(self)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame = ttk.LabelFrame(right_panel_frame, text="Game Messages", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        self.info_text = tk.Text(
            info_frame, 
            state=tk.DISABLED, 
            bg=THEME["secondary_bg"], 
            fg=THEME["text"], 
            relief="flat", 
            font=FONTS["small"]
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Human Action Controls (placed at the bottom)
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        self._create_human_action_controls(controls_frame)

        # Bind the resize event
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """Redraws all canvas elements when the window is resized."""
        self.canvas.delete("all")
        self._draw_table()
        self._draw_player_seats()
        self._draw_community_card_area()
        self._draw_pot_display()

    def _draw_table(self):
        """Draws the main poker table shape."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Main table oval
        table_width = min(width, height) * 0.8
        table_height = table_width * 0.6
        x1 = (width - table_width) / 2
        y1 = (height - table_height) / 2
        x2 = x1 + table_width
        y2 = y1 + table_height

        # Draw table with felt texture
        self.canvas.create_oval(x1, y1, x2, y2, fill="#0A6B3B", outline="#5C3A21", width=3)

    def _draw_player_seats(self):
        """Draws player seats around the table."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calculate table dimensions
        table_width = min(width, height) * 0.8
        table_height = table_width * 0.6
        table_center_x = width / 2
        table_center_y = height / 2
        
        # Player positions around the table
        positions = [
            (table_center_x, table_center_y - table_height/2 - 80),  # Top
            (table_center_x - table_width/2 - 100, table_center_y - table_height/2 - 40),  # Top-left
            (table_center_x - table_width/2 - 100, table_center_y + table_height/2 + 40),  # Bottom-left
            (table_center_x, table_center_y + table_height/2 + 80),  # Bottom
            (table_center_x + table_width/2 + 100, table_center_y + table_height/2 + 40),  # Bottom-right
            (table_center_x + table_width/2 + 100, table_center_y - table_height/2 - 40),  # Top-right
        ]
        
        positions_names = ["UTG", "UTG+1", "MP", "CO", "BTN", "SB"]
        
        self.player_seats = []
        for i, (x, y) in enumerate(positions):
            seat_widgets = self._create_player_seat_widget(x, y, f"Player {i+1}", positions_names[i], i)
            self.player_seats.append(seat_widgets)

    def _create_player_seat_widget(self, x, y, name, position, index):
        """Creates a player seat widget."""
        seat_frame = tk.Frame(self.canvas, bg=THEME["secondary_bg"], relief="raised", bd=2)
        self.canvas.create_window(x, y, window=seat_frame)
        
        name_label = tk.Label(seat_frame, text=name, font=FONTS["small"], bg=THEME["secondary_bg"], fg=THEME["text"])
        name_label.pack()
        
        info_frame = tk.Frame(seat_frame, bg=THEME["secondary_bg"])
        info_frame.pack()
        
        stack_label = tk.Label(info_frame, text="$100.00", font=FONTS["small"], bg=THEME["secondary_bg"], fg="yellow")
        stack_label.pack()
        
        bet_label = tk.Label(info_frame, text="", font=FONTS["small"], bg=THEME["secondary_bg"], fg="blue")
        bet_label.pack()
        
        cards_label = tk.Label(info_frame, text="🂠 🂠", font=FONTS["small"], bg=THEME["secondary_bg"], fg=THEME["text"])
        cards_label.pack()
        
        return {
            "frame": seat_frame,
            "name_label": name_label,
            "stack_label": stack_label,
            "bet_label": bet_label,
            "cards_label": cards_label
        }

    def _draw_community_card_area(self):
        """Draws the community card area."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Community card area
        card_area_x = width / 2
        card_area_y = height / 2 + 50
        
        # Create labels for community cards
        self.community_card_labels = []
        for i in range(5):
            card_label = tk.Label(
                self.canvas, 
                text="🂠", 
                font=FONTS["large"], 
                bg=THEME["primary_bg"], 
                fg=THEME["text"]
            )
            self.canvas.create_window(
                card_area_x - 120 + i * 60, 
                card_area_y, 
                window=card_label
            )
            self.community_card_labels.append(card_label)

    def _draw_pot_display(self):
        """Draws the pot display."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Pot label
        self.pot_label = tk.Label(
            self.canvas, 
            text="Pot: $0.00", 
            font=FONTS["medium"], 
            bg=THEME["primary_bg"], 
            fg="yellow"
        )
        self.canvas.create_window(width / 2, height / 2, window=self.pot_label)

    def _create_human_action_controls(self, parent_frame):
        """Creates the human action controls."""
        # Action buttons frame
        action_frame = ttk.Frame(parent_frame)
        action_frame.pack(side=tk.LEFT, padx=10)
        
        # Action buttons
        self.human_action_controls = {
            'fold': ttk.Button(action_frame, text="Fold", command=lambda: self._submit_human_action("fold")),
            'check': ttk.Button(action_frame, text="Check", command=lambda: self._submit_human_action("check")),
            'call': ttk.Button(action_frame, text="Call", command=lambda: self._submit_human_action("call")),
            'bet_raise': ttk.Button(action_frame, text="Bet/Raise", command=lambda: self._submit_human_action("bet"))
        }
        
        # Bet sizing frame
        self.sizing_frame = ttk.Frame(parent_frame)
        self.bet_size_var = tk.DoubleVar(value=10.0)
        self.bet_size_label = ttk.Label(self.sizing_frame, text="Bet Size: $10.00")
        self.bet_size_label.pack()
        
        self.bet_size_slider = ttk.Scale(
            self.sizing_frame, 
            from_=1, 
            to=100, 
            variable=self.bet_size_var, 
            orient=tk.HORIZONTAL,
            command=self._update_bet_size_label
        )
        self.bet_size_slider.pack(fill=tk.X)
        
        # Game control buttons
        game_control_frame = ttk.Frame(parent_frame)
        game_control_frame.pack(side=tk.RIGHT, padx=10)
        
        self.start_button = ttk.Button(
            game_control_frame, 
            text="🚀 Start New Hand", 
            command=self.start_new_hand
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(
            game_control_frame, 
            text="🔄 Reset Game", 
            command=self._reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def _update_bet_size_label(self, event=None):
        """Updates the bet size label."""
        self.bet_size_label.config(text=f"Bet Size: ${self.bet_size_var.get():.2f}")

    def _show_game_control_buttons(self):
        """Shows the game control buttons."""
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def _show_action_buttons(self):
        """Shows the action buttons."""
        for button in self.human_action_controls.values():
            button.pack(side=tk.LEFT, padx=2)

    def _toggle_action_controls(self, enable):
        """Enable or disable human action controls."""
        state = tk.NORMAL if enable else tk.DISABLED
        for control in self.human_action_controls.values():
            control.config(state=state)

    def _reset_game(self):
        """Resets the game."""
        self.session_id = None
        self._reset_ui_for_new_hand()
        self.add_game_message("🔄 Game reset. Click 'Start New Hand' to begin.")

    def _reset_ui_for_new_hand(self):
        """Resets the UI for a new hand."""
        # Clear community cards
        for label in self.community_card_labels:
            label.config(text="🂠")
        
        # Reset pot
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text="Pot: $0.00")
        
        # Clear player bets
        for seat in self.player_seats:
            seat["bet_label"].config(text="")
            seat["frame"].config(bg=THEME["secondary_bg"])
        
        # Hide action controls
        for control in self.human_action_controls.values():
            if hasattr(control, 'pack_forget'):
                control.pack_forget()
        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack_forget()

    def add_game_message(self, message):
        """Adds a message to the game log."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)

    def _process_api_responses(self):
        """Checks the queue for responses from the API and updates the UI."""
        try:
            while not self.response_queue.empty():
                response = self.response_queue.get_nowait()
                if "error" in response:
                    messagebox.showerror("API Error", response["error"])
                    self._toggle_action_controls(True)  # Re-enable controls on error
                else:
                    self._update_ui_from_state(response['game_state'])
        finally:
            # Schedule this method to run again
            self.after(100, self._process_api_responses)

    def _update_ui_from_state(self, game_state):
        """Updates the UI based on the game state from the API."""
        if not game_state:
            return

        # Update pot
        if hasattr(self, 'pot_label'):
            self.pot_label.config(text=f"Pot: ${game_state['pot']:.2f}")

        # Update community cards
        for i, label in enumerate(self.community_card_labels):
            if i < len(game_state['board']):
                label.config(text=self._format_card(game_state['board'][i]))
            else:
                label.config(text="🂠")

        # Update player info
        for i, seat in enumerate(self.player_seats):
            if i < len(game_state['players']):
                player_info = game_state['players'][i]
                
                seat["name_label"].config(text=player_info['name'])
                seat["stack_label"].config(text=f"${player_info['stack']:.2f}")
                
                if player_info['contributed'] > 0:
                    seat["bet_label"].config(text=f"💰 ${player_info['contributed']:.2f}")
                else:
                    seat["bet_label"].config(text="")
                
                # Show hole cards
                if player_info['hole_cards']:
                    cards_text = " ".join([self._format_card(card) for card in player_info['hole_cards']])
                    seat["cards_label"].config(text=cards_text)
                else:
                    seat["cards_label"].config(text="🂠 🂠")
                
                # Highlight current player
                if i == game_state.get('action_player', -1):
                    seat["frame"].config(bg=THEME["accent_primary"])
                else:
                    seat["frame"].config(bg=THEME["secondary_bg"])

        # Show action controls if it's human's turn
        if game_state.get('is_users_turn', False):
            self.prompt_human_action(game_state)
        else:
            self._toggle_action_controls(False)

    def _submit_human_action(self, action_str):
        """Submits the human's action to the backend in a separate thread."""
        if not self.session_id:
            self.add_game_message("❌ No active game session")
            return

        amount = 0
        if action_str in ["bet", "raise"]:
            amount = self.bet_size_var.get()
        
        self.add_game_message(f"▶️ You chose to {action_str.upper()}...")
        self._toggle_action_controls(False)  # Disable UI while waiting

        # Create and start a worker thread to make the API call
        thread = threading.Thread(
            target=self._worker_thread_post_action,
            args=(self.session_id, action_str, amount),
            daemon=True
        )
        thread.start()

    def _worker_thread_post_action(self, session_id, action, size):
        """This function runs in a separate thread to avoid blocking the UI."""
        try:
            response = self.api_client.post_action(session_id, action, size)
            self.response_queue.put(response)
        except requests.exceptions.RequestException as e:
            self.response_queue.put({"error": f"Connection to server failed: {e}"})

    def prompt_human_action(self, game_state):
        """Shows action controls for human player."""
        self._toggle_action_controls(True)
        
        # Show appropriate buttons based on game state
        to_call = game_state.get('to_call', 0)
        
        if to_call > 0:
            # There's a bet to call
            self.human_action_controls['call'].config(text=f"Call ${to_call:.2f}")
            self.human_action_controls['call'].pack(side=tk.LEFT, padx=2)
            self.human_action_controls['fold'].pack(side=tk.LEFT, padx=2)
            self.human_action_controls['bet_raise'].config(text="Raise")
            self.human_action_controls['bet_raise'].pack(side=tk.LEFT, padx=2)
        else:
            # No bet to call
            self.human_action_controls['check'].pack(side=tk.LEFT, padx=2)
            self.human_action_controls['bet_raise'].config(text="Bet")
            self.human_action_controls['bet_raise'].pack(side=tk.LEFT, padx=2)
        
        # Show bet sizing controls
        if hasattr(self, 'sizing_frame'):
            self.sizing_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def start_new_hand(self):
        """Starts a new hand by calling the backend API."""
        try:
            self.add_game_message("🎮 Starting new hand...")
            response = self.api_client.new_game()
            self.session_id = response['session_id']
            self._update_ui_from_state(response['game_state'])
            self.sfx.play("card_deal")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Could not connect to the backend server: {e}")

    def _format_card(self, card_str):
        """Formats a card string for display."""
        if not card_str or card_str == "**":
            return "🂠"
        
        rank = card_str[0]
        suit = card_str[1]
        
        # Convert suit to Unicode symbols
        suit_symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        suit_symbol = suit_symbols.get(suit, suit)
        
        return f"{rank}{suit_symbol}"

    def run(self):
        """Starts the UI."""
        self.mainloop() 