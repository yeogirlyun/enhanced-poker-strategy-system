#!/usr/bin/env python3
"""
Strategy Optimization Panel

Provides interface for optimizing poker strategies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from gui_models import StrategyData, THEME


class StrategyOptimizationPanel:
    """
    Panel for strategy optimization features.
    """

    def __init__(
        self,
        parent_frame,
        strategy_data: StrategyData,
        on_optimization_complete: Optional[Callable] = None,
    ):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_optimization_complete = on_optimization_complete
        self.current_font_size = 12


        self._setup_ui()

    def _setup_ui(self):
        """Sets up the strategy optimization UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(
            self.parent, 
            text="Strategy Optimization", 
            style="Dark.TLabelframe"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Optimization controls
        controls_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # Optimization type
        ttk.Label(
            controls_frame, 
            text="Optimization Type:", 
            style="Dark.TLabel"
        ).pack(anchor=tk.W, pady=5)

        self.optimization_type = tk.StringVar(value="hand_ranges")
        optimization_types = [
            ("Hand Ranges", "hand_ranges"),
            ("Bet Sizing", "bet_sizing"),
            ("Position Adjustments", "position_adjustments"),
            ("Full Strategy", "full_strategy")
        ]

        for text, value in optimization_types:
            ttk.Radiobutton(
                controls_frame,
                text=text,
                variable=self.optimization_type,
                value=value,
                style="Dark.TRadiobutton"
            ).pack(anchor=tk.W, pady=2)

        # Optimization parameters
        params_frame = ttk.LabelFrame(
            self.main_frame,
            text="Optimization Parameters",
            style="Dark.TLabelframe"
        )
        params_frame.pack(fill=tk.X, padx=10, pady=10)

        # Iterations
        ttk.Label(params_frame, text="Iterations:", style="Dark.TLabel").pack(
            anchor=tk.W, pady=5
        )
        self.iterations_var = tk.StringVar(value="1000")
        iterations_entry = ttk.Entry(
            params_frame, 
            textvariable=self.iterations_var,
            style="SkyBlue.TEntry"
        )
        iterations_entry.pack(fill=tk.X, padx=10, pady=5)

        # Target win rate
        ttk.Label(params_frame, text="Target Win Rate (%):", 
                 style="Dark.TLabel").pack(anchor=tk.W, pady=5)
        self.target_winrate_var = tk.StringVar(value="55")
        winrate_entry = ttk.Entry(
            params_frame,
            textvariable=self.target_winrate_var,
            style="SkyBlue.TEntry"
        )
        winrate_entry.pack(fill=tk.X, padx=10, pady=5)

        # Progress display
        progress_frame = ttk.LabelFrame(
            self.main_frame,
            text="Optimization Progress",
            style="Dark.TLabelframe"
        )
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.progress_text = tk.Text(
            progress_frame,
            height=10,
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Start Optimization",
            command=self._start_optimization,
            style="TopMenu.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Stop Optimization",
            command=self._stop_optimization,
            style="TopMenu.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Apply Results",
            command=self._apply_results,
            style="TopMenu.TButton"
        ).pack(side=tk.LEFT, padx=5)

    def _start_optimization(self):
        """Start the optimization process."""
        try:
            iterations = int(self.iterations_var.get())
            target_winrate = float(self.target_winrate_var.get())
            optimization_type = self.optimization_type.get()

            self._log_progress(f"Starting {optimization_type} optimization...")
            self._log_progress(f"Iterations: {iterations}")
            self._log_progress(f"Target win rate: {target_winrate}%")
            self._log_progress("Optimization in progress...")

            # Simulate optimization process
            self._simulate_optimization(iterations, target_winrate)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter: {e}")

    def _stop_optimization(self):
        """Stop the optimization process."""
        self._log_progress("Optimization stopped by user.")
        messagebox.showinfo("Stopped", "Optimization process stopped.")

    def _apply_results(self):
        """Apply optimization results to strategy."""
        self._log_progress("Applying optimization results...")
        messagebox.showinfo("Applied", "Optimization results applied to strategy.")

    def _simulate_optimization(self, iterations: int, target_winrate: float):
        """Simulate optimization process for demonstration."""
        import threading
        import time

        def optimization_thread():
            for i in range(1, 11):
                time.sleep(0.5)  # Simulate work
                progress = i * 10
                self._log_progress(f"Progress: {progress}%")
                
                if i == 5:
                    self._log_progress("Analyzing hand ranges...")
                elif i == 8:
                    self._log_progress("Adjusting bet sizing...")
                elif i == 10:
                    self._log_progress("Optimization complete!")
                    self._log_progress(f"Final win rate: {target_winrate + 2.5:.1f}%")
                    
                    if self.on_optimization_complete:
                        self.on_optimization_complete({
                            "win_rate": target_winrate + 2.5,
                            "improvement": 2.5
                        })

        # Run optimization in separate thread
        thread = threading.Thread(target=optimization_thread)
        thread.daemon = True
        thread.start()

    def _log_progress(self, message: str):
        """Log progress message to the text area."""
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)

    def update_font_size(self, font_size: int):
        """Update font size for all widgets."""
        self.current_font_size = font_size
        # Update font sizes for labels and text areas
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(font=("Arial", font_size))
            elif isinstance(widget, tk.Text):
                widget.configure(font=("Consolas", font_size)) 