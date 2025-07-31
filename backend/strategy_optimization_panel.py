#!/usr/bin/env python3
"""
Strategy Optimization Panel

Provides GUI interface for equity-based strategy optimization and GTO analysis.
Integrates with the equity decision engine and simple optimizer.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from gui_models import THEME
from equity_decision_engine import EquityDecisionEngine
from simple_optimizer import SimpleOptimizer


class StrategyOptimizationPanel:
    """
    GUI panel for strategy optimization with equity-based analysis.
    """
    
    def __init__(self, parent, strategy_data, on_optimization_complete):
        self.parent = parent
        self.strategy_data = strategy_data
        self.on_optimization_complete = on_optimization_complete
        
        # Initialize engines
        self.equity_engine = EquityDecisionEngine()
        self.optimizer = SimpleOptimizer()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the optimization panel UI."""
        # Main frame
        self.frame = ttk.Frame(self.parent, style="Dark.TFrame")
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text="🎯 Strategy Optimization", 
            style="Dark.TLabel",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Optimization methods frame
        methods_frame = ttk.LabelFrame(
            self.frame, 
            text="Optimization Methods", 
            style="Dark.TLabelframe"
        )
        methods_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Method selection
        self.method_var = tk.StringVar(value="advanced")
        methods = [
            ("Simple", "simple"),
            ("Quick", "quick"),
            ("Advanced (Equity-Based)", "advanced"),
            ("Random", "random"),
            ("Conservative", "conservative")
        ]
        
        for text, value in methods:
            ttk.Radiobutton(
                methods_frame,
                text=text,
                variable=self.method_var,
                value=value,
                style="Dark.TRadiobutton"
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Equity analysis frame
        equity_frame = ttk.LabelFrame(
            self.frame, 
            text="Equity Analysis", 
            style="Dark.TLabelframe"
        )
        equity_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Hand input
        hand_frame = ttk.Frame(equity_frame, style="Dark.TFrame")
        hand_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(hand_frame, text="Hand:", style="Dark.TLabel").pack(side=tk.LEFT)
        self.hand_entry = ttk.Entry(hand_frame, width=10, style="SkyBlue.TEntry")
        self.hand_entry.pack(side=tk.LEFT, padx=5)
        self.hand_entry.insert(0, "AhKs")
        
        # Board input
        board_frame = ttk.Frame(equity_frame, style="Dark.TFrame")
        board_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(board_frame, text="Board:", style="Dark.TLabel").pack(side=tk.LEFT)
        self.board_entry = ttk.Entry(board_frame, width=15, style="SkyBlue.TEntry")
        self.board_entry.pack(side=tk.LEFT, padx=5)
        self.board_entry.insert(0, "AhKsQd")
        
        # Position input
        pos_frame = ttk.Frame(equity_frame, style="Dark.TFrame")
        pos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pos_frame, text="Position:", style="Dark.TLabel").pack(side=tk.LEFT)
        self.pos_var = tk.StringVar(value="BTN")
        pos_combo = ttk.Combobox(
            pos_frame, 
            textvariable=self.pos_var,
            values=["UTG", "MP", "CO", "BTN", "SB", "BB"],
            width=8,
            style="SkyBlue.TCombobox"
        )
        pos_combo.pack(side=tk.LEFT, padx=5)
        
        # Game state inputs
        game_frame = ttk.Frame(equity_frame, style="Dark.TFrame")
        game_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(game_frame, text="Pot:", style="Dark.TLabel").pack(side=tk.LEFT)
        self.pot_entry = ttk.Entry(game_frame, width=8, style="SkyBlue.TEntry")
        self.pot_entry.pack(side=tk.LEFT, padx=5)
        self.pot_entry.insert(0, "100")
        
        ttk.Label(game_frame, text="To Call:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(10, 0))
        self.call_entry = ttk.Entry(game_frame, width=8, style="SkyBlue.TEntry")
        self.call_entry.pack(side=tk.LEFT, padx=5)
        self.call_entry.insert(0, "50")
        
        # Street selection
        street_frame = ttk.Frame(equity_frame, style="Dark.TFrame")
        street_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(street_frame, text="Street:", style="Dark.TLabel").pack(side=tk.LEFT)
        self.street_var = tk.StringVar(value="flop")
        street_combo = ttk.Combobox(
            street_frame,
            textvariable=self.street_var,
            values=["preflop", "flop", "turn", "river"],
            width=8,
            style="SkyBlue.TCombobox"
        )
        street_combo.pack(side=tk.LEFT, padx=5)
        
        # Analysis button
        analyze_btn = ttk.Button(
            equity_frame,
            text="🔍 Analyze Equity",
            command=self._analyze_equity,
            style="Dark.TButton"
        )
        analyze_btn.pack(pady=10)
        
        # Results display
        results_frame = ttk.LabelFrame(
            self.frame, 
            text="Analysis Results", 
            style="Dark.TLabelframe"
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_text = tk.Text(
            results_frame,
            height=8,
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            font=("Courier", 10),
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Optimization buttons
        optimize_frame = ttk.Frame(self.frame, style="Dark.TFrame")
        optimize_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            optimize_frame,
            text="⚡ Quick Optimize",
            command=self._quick_optimize,
            style="Dark.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            optimize_frame,
            text="🎯 Advanced Optimize",
            command=self._advanced_optimize,
            style="Dark.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            optimize_frame,
            text="🔄 Suggest Improvements",
            command=self._suggest_improvements,
            style="Dark.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def _analyze_equity(self):
        """Analyze equity for the current hand and situation."""
        try:
            hand = self.hand_entry.get().strip()
            board = self.board_entry.get().strip()
            position = self.pos_var.get()
            pot_size = float(self.pot_entry.get())
            to_call = float(self.call_entry.get())
            street = self.street_var.get()
            
            if not hand:
                messagebox.showerror("Error", "Please enter a valid hand")
                return
            
            # Get optimal action
            action, amount = self.equity_engine.get_optimal_action(
                hand, board, position, pot_size, to_call, street
            )
            
            # Generate equity report
            report = self.equity_engine.generate_equity_report(hand, board, position)
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            results = f"""🎯 EQUITY ANALYSIS RESULTS
{'='*50}

📊 Hand Analysis:
   Hand: {hand}
   Board: {board}
   Position: {position}
   Street: {street}
   Pot Size: ${pot_size:.2f}
   To Call: ${to_call:.2f}

📈 Equity Metrics:
   Raw Equity: {report['raw_equity']:.1%}
   Position Adjusted: {report['position_adjusted_equity']:.1%}
   Position Multiplier: {report['position_multiplier']:.2f}

🎯 Optimal Action:
   Action: {action.upper()}
   Amount: ${amount:.2f}

💡 Recommendations:
"""
            for rec in report['recommendations']:
                results += f"   • {rec}\n"
            
            results += f"""
🔍 GTO Analysis:
   • Value Bet Threshold: {self.equity_engine.VALUE_BET_THRESHOLD:.1%}
   • Bluff Threshold: {self.equity_engine.BLUFF_THRESHOLD:.1%}
   • Raise Threshold: {self.equity_engine.RAISE_THRESHOLD:.1%}
   • Call Margin: {self.equity_engine.CALL_THRESHOLD_MARGIN:.1%}
"""
            
            self.results_text.insert(1.0, results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")
    
    def _quick_optimize(self):
        """Run quick optimization."""
        try:
            result = self.optimizer.optimize_strategy(
                "optimized_modern_strategy.json",
                method="quick"
            )
            
            messagebox.showinfo(
                "Quick Optimization Complete",
                f"Optimization completed!\n\n"
                f"Performance: {result.performance_improvement}\n"
                f"Complexity: {result.complexity_rating}\n"
                f"Evaluations: {result.evaluations_performed}"
            )
            
            if self.on_optimization_complete:
                self.on_optimization_complete()
                
        except Exception as e:
            messagebox.showerror("Error", f"Quick optimization failed: {e}")
    
    def _advanced_optimize(self):
        """Run advanced equity-based optimization."""
        try:
            result = self.optimizer.optimize_strategy(
                "optimized_modern_strategy.json",
                method="advanced"
            )
            
            messagebox.showinfo(
                "Advanced Optimization Complete",
                f"Equity-based optimization completed!\n\n"
                f"Performance: {result.performance_improvement}\n"
                f"Complexity: {result.complexity_rating}\n"
                f"Method: {result.optimization_method}\n"
                f"Evaluations: {result.evaluations_performed}"
            )
            
            if self.on_optimization_complete:
                self.on_optimization_complete()
                
        except Exception as e:
            messagebox.showerror("Error", f"Advanced optimization failed: {e}")
    
    def _suggest_improvements(self):
        """Suggest strategy improvements based on equity analysis."""
        try:
            # Get current strategy
            current_strategy = self.strategy_data.strategy_dict
            
            # Apply equity-based improvements
            improved_strategy = self.equity_engine.suggest_strategy_improvements(current_strategy)
            
            # Show improvements
            improvements = self._analyze_improvements(current_strategy, improved_strategy)
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, improvements)
            
            messagebox.showinfo(
                "Improvements Suggested",
                "Strategy improvements have been analyzed and displayed in the results panel."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Improvement analysis failed: {e}")
    
    def _analyze_improvements(self, original: Dict, improved: Dict) -> str:
        """Analyze and format improvement suggestions."""
        analysis = f"""🔧 STRATEGY IMPROVEMENT ANALYSIS
{'='*50}

📊 Equity-Based Improvements Applied:

🎯 Postflop Threshold Adjustments:
"""
        
        if "postflop" in improved:
            for street in ["flop", "turn", "river"]:
                if street in improved["postflop"].get("pfa", {}):
                    analysis += f"\n   {street.upper()}:\n"
                    for pos in improved["postflop"]["pfa"][street]:
                        for ip_oop in improved["postflop"]["pfa"][street][pos]:
                            rule = improved["postflop"]["pfa"][street][pos][ip_oop]
                            if "val_thresh" in rule:
                                analysis += f"     {pos} ({ip_oop}): val_thresh = {rule['val_thresh']}\n"
        
        analysis += f"""
💡 Key Improvements:
   • Value betting thresholds adjusted for position
   • Logical gaps ensured between check/bet thresholds
   • Bet sizing optimized for equity principles
   • Street-specific adjustments applied

🎯 GTO Principles Applied:
   • Position-based equity adjustments
   • Pot odds integration
   • Balanced value/bluff ratios
   • Optimal bet sizing by street
"""
        
        return analysis
    
    def pack(self, **kwargs):
        """Pack the panel."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Unpack the panel."""
        self.frame.pack_forget()


if __name__ == "__main__":
    # Test the optimization panel
    root = tk.Tk()
    root.title("Strategy Optimization Panel Test")
    
    from gui_models import StrategyData
    
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    panel = StrategyOptimizationPanel(root, strategy_data, lambda: print("Optimization complete"))
    panel.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop() 