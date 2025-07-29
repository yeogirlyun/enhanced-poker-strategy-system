# filename: strategy_development_gui.py
"""
Advanced Poker Strategy Development GUI

A comprehensive graphical interface for poker strategy development that integrates:
- Visual hand strength tier management
- Decision table editing with real-time validation
- Integrated simulation and performance visualization
- Human-executable optimization interface
- Strategy comparison and analysis tools
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
from tkinter import Canvas, Scrollbar, Frame
import json
import os
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, List, Optional, Tuple
import colorsys
from datetime import datetime

# Import backend modules
try:
    from enhanced_simulation_engine import EnhancedSimulationEngine
    from human_executable_optimizer import HumanExecutableOptimizer, HSTier, OptimizationConstraints
    from simplified_optimizer_interface import StrategyOptimizerInterface
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("⚠️ Backend modules not available - GUI will run in demo mode")

class HandStrengthTier:
    """Represents a tier of hands with visual properties."""
    
    def __init__(self, name: str, min_hs: int, max_hs: int, color: str, hands: List[str] = None):
        self.name = name
        self.min_hs = min_hs
        self.max_hs = max_hs
        self.color = color
        self.hands = hands or []
        self.visible = True

class StrategyEditor:
    """Main strategy editing interface."""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.strategy = {}
        self.tiers = []
        self.selected_hands = set()
        self.hand_widgets = {}
        
        self.setup_ui()
        self.load_default_strategy()
    
    def setup_ui(self):
        """Setup the strategy editor interface."""
        
        # Main container with paned window for resizable sections
        self.paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Hand grid and tiers
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=2)
        
        # Right panel: Decision tables and controls
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=1)
        
        self.setup_hand_grid()
        self.setup_tier_panel()
        self.setup_decision_panel()
        self.setup_controls()
    
    def setup_hand_grid(self):
        """Setup the visual hand strength grid."""
        
        # Hand grid frame with size controls
        grid_frame = ttk.LabelFrame(self.left_frame, text="Hand Strength Grid")
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Grid controls frame
        controls_frame = ttk.Frame(grid_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Grid size controls with +/- buttons
        ttk.Label(controls_frame, text="Grid Size:").pack(side=tk.LEFT)
        
        size_frame = ttk.Frame(controls_frame)
        size_frame.pack(side=tk.LEFT, padx=5)
        
        self.grid_size_index = 1  # Start with Medium (index 1)
        self.grid_sizes = ["Small", "Medium", "Large", "Extra Large"]
        
        ttk.Button(size_frame, text="-", width=3, 
                  command=self.decrease_grid_size).pack(side=tk.LEFT)
        
        self.size_label = ttk.Label(size_frame, text="Medium", width=12, anchor="center",
                                   relief="sunken", borderwidth=1)
        self.size_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(size_frame, text="+", width=3, 
                  command=self.increase_grid_size).pack(side=tk.LEFT)
        
        ttk.Button(controls_frame, text="Refresh Colors", 
                  command=self.update_hand_colors).pack(side=tk.RIGHT, padx=5)
        
        # Create scrollable canvas for hand grid
        self.grid_canvas = Canvas(grid_frame, bg='white', height=400)
        scrollbar = Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.grid_canvas.yview)
        self.hand_frame = Frame(self.grid_canvas, bg='white')
        
        self.grid_canvas.configure(yscrollcommand=scrollbar.set)
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas_window = self.grid_canvas.create_window((0, 0), window=self.hand_frame, anchor='nw')
        
        # Generate hand grid
        self.create_hand_grid()
        
        # Update scroll region
        self.hand_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox('all'))
    
    def create_hand_grid(self):
        """Create the visual grid of poker hands."""
        
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # Get grid size settings
        size_settings = self.get_grid_size_settings()
        
        # Clear existing widgets
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        self.hand_widgets.clear()
        
        # Header row
        tk.Label(self.hand_frame, text="", width=size_settings['label_width'], 
                bg='lightgray', font=size_settings['font']).grid(row=0, column=0)
        for i, rank in enumerate(ranks):
            tk.Label(self.hand_frame, text=rank, width=size_settings['label_width'], 
                    bg='lightgray', font=size_settings['font']).grid(row=0, column=i+1)
        
        # Create hand buttons
        for i, rank1 in enumerate(ranks):
            # Row header
            tk.Label(self.hand_frame, text=rank1, width=size_settings['label_width'], 
                    bg='lightgray', font=size_settings['font']).grid(row=i+1, column=0)
            
            for j, rank2 in enumerate(ranks):
                # Fix hand naming convention - higher rank always first
                if i == j:  # Pocket pairs
                    hand = rank1 + rank2
                elif i < j:  # Suited hands (upper triangle)
                    hand = rank1 + rank2 + 's'
                else:  # Offsuit hands (lower triangle) - keep higher rank first
                    hand = rank2 + rank1 + 'o'
                
                # Create hand button with dynamic sizing
                btn = tk.Button(self.hand_frame, text=hand, 
                               width=size_settings['button_width'], 
                               height=size_settings['button_height'],
                               font=size_settings['font'], relief=tk.RAISED,
                               command=lambda h=hand: self.toggle_hand_selection(h))
                btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                
                self.hand_widgets[hand] = btn
                
                # Bind right-click for context menu
                btn.bind('<Button-3>', lambda e, h=hand: self.show_hand_menu(e, h))
    
    def increase_grid_size(self):
        """Increase grid size."""
        if self.grid_size_index < len(self.grid_sizes) - 1:
            self.grid_size_index += 1
            self.size_label.config(text=self.grid_sizes[self.grid_size_index])
            self.on_grid_size_change()
    
    def decrease_grid_size(self):
        """Decrease grid size."""
        if self.grid_size_index > 0:
            self.grid_size_index -= 1
            self.size_label.config(text=self.grid_sizes[self.grid_size_index])
            self.on_grid_size_change()
    
    def get_grid_size_settings(self):
        """Get grid size settings based on selected size."""
        size = self.grid_sizes[self.grid_size_index] if hasattr(self, 'grid_size_index') else "Medium"
        
        settings = {
            "Small": {
                'button_width': 3, 'button_height': 1, 'label_width': 2,
                'font': ('Arial', 8), 'canvas_height': 300
            },
            "Medium": {
                'button_width': 4, 'button_height': 2, 'label_width': 3,
                'font': ('Arial', 9), 'canvas_height': 400
            },
            "Large": {
                'button_width': 5, 'button_height': 2, 'label_width': 4,
                'font': ('Arial', 10), 'canvas_height': 500
            },
            "Extra Large": {
                'button_width': 6, 'button_height': 3, 'label_width': 5,
                'font': ('Arial', 12), 'canvas_height': 650
            }
        }
        
        return settings.get(size, settings["Medium"])
    
    def on_grid_size_change(self, event=None):
        """Handle grid size change."""
        settings = self.get_grid_size_settings()
        
        # Update canvas height
        self.grid_canvas.configure(height=settings['canvas_height'])
        
        # Recreate grid with new size
        self.create_hand_grid()
        
        # Update scroll region
        self.hand_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox('all'))
        
        # Reapply colors
        self.update_hand_colors()
    
    def setup_tier_panel(self):
        """Setup the tier management panel."""
        
        tier_frame = ttk.LabelFrame(self.left_frame, text="Hand Strength Tiers")
        tier_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tier controls
        controls_frame = ttk.Frame(tier_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Tier", 
                  command=self.add_tier).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Remove Tier", 
                  command=self.remove_tier).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Edit Tier", 
                  command=self.edit_tier).pack(side=tk.LEFT, padx=2)
        
        # Second row of controls
        controls_frame2 = ttk.Frame(tier_frame)
        controls_frame2.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(controls_frame2, text="Assign Selected", 
                  command=self.assign_selected_to_tier).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame2, text="Clear Selection", 
                  command=self.clear_hand_selection).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame2, text="Debug Info", 
                  command=self.print_debug_info).pack(side=tk.LEFT, padx=2)
        
        # Tier list
        self.tier_listbox = tk.Listbox(tier_frame, height=6, selectmode=tk.SINGLE)
        self.tier_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.tier_listbox.bind('<<ListboxSelect>>', self.on_tier_select)
        
        # Tier info
        self.tier_info_label = ttk.Label(tier_frame, text="Select a tier to view details")
        self.tier_info_label.pack(padx=5, pady=5)
    
    def assign_selected_to_tier(self):
        """Assign selected hands to the currently selected tier."""
        
        if not self.selected_hands:
            messagebox.showinfo("No Selection", "Please select hands first by clicking on them.")
            return
        
        selection = self.tier_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Tier Selected", "Please select a tier from the list.")
            return
        
        tier_index = selection[0]
        selected_tier = self.tiers[tier_index]
        
        # Remove selected hands from all other tiers
        for tier in self.tiers:
            for hand in list(self.selected_hands):
                if hand in tier.hands:
                    tier.hands.remove(hand)
        
        # Add selected hands to the target tier
        for hand in self.selected_hands:
            if hand not in selected_tier.hands:
                selected_tier.hands.append(hand)
        
        # Clear selection
        self.clear_hand_selection()
        
        # Update displays
        self.update_tier_display()
        self.update_hand_colors()
        
        messagebox.showinfo("Success", f"Assigned {len(self.selected_hands)} hands to {selected_tier.name}")
    
    def clear_hand_selection(self):
        """Clear all hand selections."""
        
        for hand in list(self.selected_hands):
            if hand in self.hand_widgets:
                self.hand_widgets[hand].configure(relief=tk.RAISED)
        
        self.selected_hands.clear()
    
    def print_debug_info(self):
        """Print debug information about hands and tiers."""
        
        print("\n" + "="*60)
        print("🔍 DEBUG INFO")
        print("="*60)
        
        print(f"📊 Grid Status:")
        print(f"   Total hand widgets: {len(self.hand_widgets)}")
        print(f"   Grid size: {self.grid_sizes[self.grid_size_index] if hasattr(self, 'grid_size_index') else 'Unknown'}")
        
        # Show a sample of available hands
        widget_hands = sorted(self.hand_widgets.keys())
        print(f"   Sample hands in grid: {widget_hands[:15]}...")
        
        print(f"\n🎯 Tier Status:")
        print(f"   Total tiers: {len(self.tiers)}")
        
        total_colored = 0
        for i, tier in enumerate(self.tiers):
            print(f"\n   Tier {i+1}: {tier.name}")
            print(f"      Color: {tier.color}")
            print(f"      HS Range: {tier.min_hs}-{tier.max_hs}")
            print(f"      Assigned hands ({len(tier.hands)}): {tier.hands}")
            
            # Check which hands are found/missing
            found_hands = []
            missing_hands = []
            
            for hand in tier.hands:
                if hand in self.hand_widgets:
                    found_hands.append(hand)
                    total_colored += 1
                else:
                    # Check alternatives
                    alt_hands = self._get_alternative_hand_formats(hand)
                    found_alt = False
                    for alt_hand in alt_hands:
                        if alt_hand in self.hand_widgets:
                            found_hands.append(f"{hand}→{alt_hand}")
                            found_alt = True
                            total_colored += 1
                            break
                    if not found_alt:
                        missing_hands.append(hand)
            
            if found_hands:
                print(f"      ✅ Found in grid: {found_hands}")
            if missing_hands:
                print(f"      ❌ Missing from grid: {missing_hands}")
        
        print(f"\n📈 Summary:")
        print(f"   Total hands that should be colored: {sum(len(tier.hands) for tier in self.tiers)}")
        print(f"   Total hands actually found: {total_colored}")
        print(f"   Selected hands: {len(self.selected_hands)} - {list(self.selected_hands)[:10]}")
        
        print("="*60)
        
        # Force a color refresh after debug
        print("🔄 Refreshing colors...")
        self.update_hand_colors()
    
    def setup_decision_panel(self):
        """Setup the decision table editing panel."""
        
        decision_frame = ttk.LabelFrame(self.right_frame, text="Decision Tables")
        decision_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook for different decision categories
        self.decision_notebook = ttk.Notebook(decision_frame)
        self.decision_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preflop tab
        preflop_frame = ttk.Frame(self.decision_notebook)
        self.decision_notebook.add(preflop_frame, text="Preflop")
        self.setup_preflop_panel(preflop_frame)
        
        # Postflop tab
        postflop_frame = ttk.Frame(self.decision_notebook)
        self.decision_notebook.add(postflop_frame, text="Postflop")
        self.setup_postflop_panel(postflop_frame)
    
    def setup_preflop_panel(self, parent):
        """Setup preflop decision editing."""
        
        # Opening ranges
        opening_frame = ttk.LabelFrame(parent, text="Opening Ranges")
        opening_frame.pack(fill=tk.X, padx=5, pady=5)
        
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB']
        self.opening_vars = {}
        
        for i, pos in enumerate(positions):
            row_frame = ttk.Frame(opening_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"{pos}:", width=6).pack(side=tk.LEFT)
            
            var = tk.StringVar(value="20")
            self.opening_vars[pos] = var
            
            spinbox = ttk.Spinbox(row_frame, from_=1, to=50, width=5, textvariable=var,
                                 command=lambda p=pos: self.update_opening_range(p))
            spinbox.pack(side=tk.LEFT, padx=5)
            
            tier_label = ttk.Label(row_frame, text="(Gold+)", foreground="gray")
            tier_label.pack(side=tk.LEFT, padx=5)
        
        # 3-bet ranges
        threbet_frame = ttk.LabelFrame(parent, text="3-Bet Ranges")
        threbet_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.threbet_vars = {}
        for pos in ['UTG', 'MP', 'CO', 'BTN']:
            row_frame = ttk.Frame(threbet_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"{pos}:", width=6).pack(side=tk.LEFT)
            
            var = tk.StringVar(value="30")
            self.threbet_vars[pos] = var
            
            spinbox = ttk.Spinbox(row_frame, from_=20, to=50, width=5, textvariable=var)
            spinbox.pack(side=tk.LEFT, padx=5)
    
    def setup_postflop_panel(self, parent):
        """Setup postflop decision editing."""
        
        # C-betting ranges
        cbet_frame = ttk.LabelFrame(parent, text="C-Betting Thresholds")
        cbet_frame.pack(fill=tk.X, padx=5, pady=5)
        
        streets = ['Flop', 'Turn', 'River']
        self.cbet_vars = {}
        
        for street in streets:
            street_frame = ttk.LabelFrame(cbet_frame, text=street)
            street_frame.pack(fill=tk.X, padx=5, pady=2)
            
            self.cbet_vars[street] = {}
            
            # Value bet threshold
            value_frame = ttk.Frame(street_frame)
            value_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(value_frame, text="Value Bet:", width=10).pack(side=tk.LEFT)
            var = tk.StringVar(value="25")
            self.cbet_vars[street]['value'] = var
            ttk.Spinbox(value_frame, from_=10, to=80, width=5, textvariable=var).pack(side=tk.LEFT, padx=5)
            
            # Check threshold
            check_frame = ttk.Frame(street_frame)
            check_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(check_frame, text="Check:", width=10).pack(side=tk.LEFT)
            var = tk.StringVar(value="15")
            self.cbet_vars[street]['check'] = var
            ttk.Spinbox(check_frame, from_=5, to=40, width=5, textvariable=var).pack(side=tk.LEFT, padx=5)
    
    def setup_controls(self):
        """Setup main control buttons."""
        
        control_frame = ttk.Frame(self.right_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Load Strategy", 
                  command=self.load_strategy).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Strategy", 
                  command=self.save_strategy).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Auto-Optimize", 
                  command=self.optimize_strategy).pack(side=tk.LEFT, padx=5)
    
    def load_default_strategy(self):
        """Load default tier configuration."""
        
        # Create default tiers with hands that match grid format
        self.tiers = [
            HandStrengthTier("Elite", 40, 50, "#FF0000", ["AA", "KK", "QQ", "AKs"]),
            HandStrengthTier("Premium", 30, 39, "#FF8800", ["JJ", "AKo", "AQs", "AJs", "KQs"]),
            HandStrengthTier("Gold", 20, 29, "#FFD700", ["TT", "99", "AQo", "AJo", "KJs", "QJs", "JTs"]),
            HandStrengthTier("Silver", 10, 19, "#C0C0C0", ["88", "77", "KJo", "QJo", "JTo", "A9s", "A8s"]),
            HandStrengthTier("Bronze", 1, 9, "#CD7F32", ["66", "55", "44", "33", "22", "A7s", "A6s", "A5s"])
        ]
        
        print("🎯 Loaded default strategy with 5 tiers")
        for tier in self.tiers:
            print(f"   {tier.name}: {len(tier.hands)} hands - {tier.hands}")
        
        self.update_tier_display()
        self.update_hand_colors()
    
    def toggle_hand_selection(self, hand: str):
        """Toggle hand selection for tier assignment."""
        
        if hand in self.selected_hands:
            self.selected_hands.remove(hand)
            self.hand_widgets[hand].configure(relief=tk.RAISED, borderwidth=2)
        else:
            self.selected_hands.add(hand)
            self.hand_widgets[hand].configure(relief=tk.SUNKEN, borderwidth=3)
        
        # Update status
        if self.selected_hands:
            count = len(self.selected_hands)
            sample_hands = list(self.selected_hands)[:5]
            display_text = f"{count} hands selected: {', '.join(sample_hands)}"
            if count > 5:
                display_text += f" + {count-5} more"
        else:
            display_text = "No hands selected"
        
        # Update tier info label to show selection
        self.tier_info_label.configure(text=display_text)
    
    def show_hand_menu(self, event, hand: str):
        """Show context menu for hand operations."""
        
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label=f"Assign {hand} to Tier", 
                        command=lambda: self.assign_hand_to_tier(hand))
        menu.add_command(label="Set Hand Strength", 
                        command=lambda: self.set_hand_strength(hand))
        menu.add_separator()
        menu.add_command(label="Hand Info", 
                        command=lambda: self.show_hand_info(hand))
        
        menu.post(event.x_root, event.y_root)
    
    def assign_hand_to_tier(self, hand: str):
        """Assign a hand to a specific tier."""
        
        # Create tier selection dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Assign {hand} to Tier")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text=f"Select tier for {hand}:").pack(pady=10)
        
        tier_var = tk.StringVar()
        for tier in self.tiers:
            ttk.Radiobutton(dialog, text=f"{tier.name} (HS {tier.min_hs}-{tier.max_hs})", 
                           variable=tier_var, value=tier.name).pack(anchor=tk.W, padx=20)
        
        def confirm():
            selected_tier = tier_var.get()
            if selected_tier:
                # Remove hand from all tiers
                for tier in self.tiers:
                    if hand in tier.hands:
                        tier.hands.remove(hand)
                
                # Add to selected tier
                for tier in self.tiers:
                    if tier.name == selected_tier:
                        tier.hands.append(hand)
                        break
                
                self.update_hand_colors()
                dialog.destroy()
        
        ttk.Button(dialog, text="Confirm", command=confirm).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def add_tier(self):
        """Add a new tier."""
        
        dialog = TierEditDialog(self.parent, "Add New Tier")
        if dialog.result:
            tier_data = dialog.result
            new_tier = HandStrengthTier(
                tier_data['name'],
                tier_data['min_hs'],
                tier_data['max_hs'],
                tier_data['color']
            )
            self.tiers.append(new_tier)
            self.update_tier_display()
    
    def remove_tier(self):
        """Remove selected tier."""
        
        selection = self.tier_listbox.curselection()
        if selection:
            index = selection[0]
            removed_tier = self.tiers.pop(index)
            messagebox.showinfo("Tier Removed", f"Removed tier: {removed_tier.name}")
            self.update_tier_display()
            self.update_hand_colors()
    
    def edit_tier(self):
        """Edit selected tier."""
        
        selection = self.tier_listbox.curselection()
        if selection:
            index = selection[0]
            tier = self.tiers[index]
            
            dialog = TierEditDialog(self.parent, "Edit Tier", tier)
            if dialog.result:
                tier_data = dialog.result
                tier.name = tier_data['name']
                tier.min_hs = tier_data['min_hs']
                tier.max_hs = tier_data['max_hs']
                tier.color = tier_data['color']
                
                self.update_tier_display()
                self.update_hand_colors()
    
    def update_tier_display(self):
        """Update the tier listbox display."""
        
        self.tier_listbox.delete(0, tk.END)
        for tier in self.tiers:
            display_text = f"{tier.name} (HS {tier.min_hs}-{tier.max_hs}) - {len(tier.hands)} hands"
            self.tier_listbox.insert(tk.END, display_text)
    
    def update_hand_colors(self):
        """Update hand button colors based on tier assignments."""
        
        # Reset all hands to default first
        for hand, widget in self.hand_widgets.items():
            widget.configure(bg='lightgray', borderwidth=2, relief=tk.RAISED)
        
        # Color hands by tier
        colored_count = 0
        for tier in self.tiers:
            for hand in tier.hands:
                if hand in self.hand_widgets:
                    self.hand_widgets[hand].configure(bg=tier.color)
                    colored_count += 1
                else:
                    # Try alternative hand formats
                    alt_hands = self._get_alternative_hand_formats(hand)
                    for alt_hand in alt_hands:
                        if alt_hand in self.hand_widgets:
                            self.hand_widgets[alt_hand].configure(bg=tier.color)
                            colored_count += 1
                            break
        
        print(f"✅ Colored {colored_count} hands across {len(self.tiers)} tiers")
        
        # Force update
        self.hand_frame.update_idletasks()
    
    def _get_alternative_hand_formats(self, hand):
        """Get alternative formats for a hand name."""
        alternatives = [hand]
        
        # Handle different formats
        if len(hand) == 2:  # Pocket pairs like "AA"
            alternatives.append(hand)
        elif len(hand) == 3:
            if hand.endswith('s'):  # Suited like "AKs"
                rank1, rank2 = hand[0], hand[1]
                alternatives.extend([
                    f"{rank1}{rank2}s",
                    f"{rank2}{rank1}s"  # Try reversed
                ])
            elif hand.endswith('o'):  # Offsuit like "AKo"
                rank1, rank2 = hand[0], hand[1]
                alternatives.extend([
                    f"{rank1}{rank2}o",
                    f"{rank2}{rank1}o"  # Try reversed
                ])
        
        return alternatives
    
    def on_tier_select(self, event):
        """Handle tier selection in listbox - FIXED VERSION."""
        
        selection = self.tier_listbox.curselection()
        if selection:
            index = selection[0]
            tier = self.tiers[index]
            
            info_text = f"📋 {tier.name} Tier Details:\n"
            info_text += f"HS Range: {tier.min_hs}-{tier.max_hs}\n"
            info_text += f"Color: {tier.color}\n"
            info_text += f"Total Hands: {len(tier.hands)}\n"
            
            if tier.hands:
                info_text += f"Hands: {', '.join(tier.hands[:15])}"
                if len(tier.hands) > 15:
                    info_text += f"\n+ {len(tier.hands) - 15} more hands"
            else:
                info_text += "No hands assigned to this tier"
            
            # Show selection status
            if self.selected_hands:
                info_text += f"\n\n✋ {len(self.selected_hands)} hands selected"
                info_text += f"\n💡 Click 'Assign Selected' to add them to {tier.name}"
            else:
                info_text += f"\n\n💡 Select hands in grid, then click 'Assign Selected'"
            
            self.tier_info_label.configure(text=info_text)
            
            # FIXED: Only highlight if this is a user-initiated selection (not programmatic)
            if event is not None:  # User clicked, so highlight
                self.highlight_tier_hands(tier)
    
    def highlight_tier_hands(self, tier):
        """Highlight hands belonging to a tier with visual feedback - FIXED VERSION."""
        
        # First ensure all colors are applied
        self.update_hand_colors()
        
        # Then add special highlighting to this tier's hands
        highlighted_count = 0
        highlighted_widgets = []  # Keep track of widgets to reset
        
        for hand in tier.hands:
            widget = None
            
            # Try to find the widget
            if hand in self.hand_widgets:
                widget = self.hand_widgets[hand]
            else:
                # Try alternative formats
                alt_hands = self._get_alternative_hand_formats(hand)
                for alt_hand in alt_hands:
                    if alt_hand in self.hand_widgets:
                        widget = self.hand_widgets[alt_hand]
                        break
            
            if widget:
                # Store original styling
                original_bg = widget.cget('bg')
                
                # Add thick border and slight relief change for visibility
                widget.configure(
                    borderwidth=4, 
                    relief=tk.RIDGE,
                    highlightbackground='yellow',
                    highlightthickness=2
                )
                highlighted_count += 1
                highlighted_widgets.append(widget)
        
        print(f"🔆 Highlighted {highlighted_count} hands for tier {tier.name}")
        
        # Update the info label to show what happened
        if highlighted_count > 0:
            temp_info = f"🔆 Highlighting {highlighted_count} hands in {tier.name} tier for 3 seconds..."
            
            # Store the current info text to restore it later
            current_info = self.tier_info_label.cget('text')
            
            # Show highlighting message
            self.tier_info_label.configure(text=temp_info)
            
            # FIXED: Reset highlighting and restore info without calling on_tier_select
            def reset_highlighting():
                try:
                    # Reset all highlighted widgets
                    for widget in highlighted_widgets:
                        widget.configure(
                            borderwidth=2, 
                            relief=tk.RAISED, 
                            highlightthickness=0
                        )
                    # Restore the original info text
                    self.tier_info_label.configure(text=current_info)
                except:
                    pass  # Widget might be destroyed
            
            # Schedule the reset after 3 seconds
            self.tier_info_label.after(3000, reset_highlighting)
    
    def update_opening_range(self, position: str):
        """Update opening range and display corresponding tier."""
        
        hs_value = int(self.opening_vars[position].get())
        tier_name = self.get_tier_for_hs(hs_value)
        
        # Update tier display (this would need proper implementation)
        print(f"Updated {position} opening to HS {hs_value} ({tier_name})")
    
    def get_tier_for_hs(self, hs_value: int) -> str:
        """Get tier name for given HS value."""
        
        for tier in self.tiers:
            if tier.min_hs <= hs_value <= tier.max_hs:
                return tier.name
        return "Unknown"
    
    def load_strategy(self):
        """Load strategy from file."""
        
        filename = filedialog.askopenfilename(
            title="Load Strategy",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.strategy = json.load(f)
                
                # Load hand strengths and update tiers
                self.load_strategy_data()
                messagebox.showinfo("Success", f"Loaded strategy from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load strategy: {e}")
    
    def save_strategy(self):
        """Save current strategy to file."""
        
        filename = filedialog.asksaveasfilename(
            title="Save Strategy",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Build strategy from current state
                strategy = self.build_strategy_from_ui()
                
                with open(filename, 'w') as f:
                    json.dump(strategy, f, indent=2)
                
                messagebox.showinfo("Success", f"Saved strategy to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save strategy: {e}")
    
    def optimize_strategy(self):
        """Run strategy optimization."""
        
        if not BACKEND_AVAILABLE:
            messagebox.showwarning("Backend Not Available", 
                                 "Optimization requires backend modules")
            return
        
        # Show optimization dialog
        OptimizationDialog(self.parent, self.tiers)
    
    def load_strategy_data(self):
        """Load strategy data into UI components."""
        
        # This would load preflop HS table and update tiers
        # Implementation depends on strategy file format
        pass
    
    def build_strategy_from_ui(self) -> Dict:
        """Build strategy dictionary from current UI state."""
        
        strategy = {
            "hand_strength_tables": {
                "preflop": {},
                "postflop": {}
            },
            "preflop": {
                "open_rules": {},
                "vs_raise": {}
            },
            "postflop": {
                "pfa": {},
                "caller": {}
            }
        }
        
        # Build preflop HS table from tiers
        for tier in self.tiers:
            for hand in tier.hands:
                # Assign HS value within tier range (simplified)
                strategy["hand_strength_tables"]["preflop"][hand] = tier.max_hs
        
        # Build opening rules
        for pos, var in self.opening_vars.items():
            strategy["preflop"]["open_rules"][pos] = {
                "threshold": int(var.get()),
                "sizing": 2.5
            }
        
        return strategy

class TierEditDialog:
    """Dialog for editing tier properties."""
    
    def __init__(self, parent, title: str, tier: HandStrengthTier = None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Form fields
        ttk.Label(self.dialog, text="Tier Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=tier.name if tier else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Min HS:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.min_hs_var = tk.StringVar(value=str(tier.min_hs) if tier else "1")
        ttk.Spinbox(self.dialog, from_=1, to=50, textvariable=self.min_hs_var, width=18).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Max HS:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.max_hs_var = tk.StringVar(value=str(tier.max_hs) if tier else "10")
        ttk.Spinbox(self.dialog, from_=1, to=50, textvariable=self.max_hs_var, width=18).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Color:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.color_var = tk.StringVar(value=tier.color if tier else "#FF0000")
        color_frame = ttk.Frame(self.dialog)
        color_frame.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Entry(color_frame, textvariable=self.color_var, width=10).pack(side=tk.LEFT)
        ttk.Button(color_frame, text="Choose", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        self.dialog.wait_window()
    
    def choose_color(self):
        """Open color chooser dialog."""
        
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=self.color_var.get())[1]
        if color:
            self.color_var.set(color)
    
    def ok_clicked(self):
        """Handle OK button click."""
        
        try:
            self.result = {
                'name': self.name_var.get(),
                'min_hs': int(self.min_hs_var.get()),
                'max_hs': int(self.max_hs_var.get()),
                'color': self.color_var.get()
            }
            
            # Validate
            if not self.result['name']:
                raise ValueError("Tier name cannot be empty")
            if self.result['min_hs'] >= self.result['max_hs']:
                raise ValueError("Min HS must be less than Max HS")
            
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()

class SimulationInterface:
    """Interface for running and visualizing simulations."""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.simulation_results = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup simulation interface."""
        
        # Control panel
        control_frame = ttk.LabelFrame(self.parent, text="Simulation Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Strategy selection
        strategy_frame = ttk.Frame(control_frame)
        strategy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(strategy_frame, text="Strategies to Compare:").pack(anchor=tk.W)
        
        self.strategy_listbox = tk.Listbox(strategy_frame, height=4, selectmode=tk.MULTIPLE)
        self.strategy_listbox.pack(fill=tk.X, pady=5)
        
        strategy_buttons = ttk.Frame(strategy_frame)
        strategy_buttons.pack(fill=tk.X)
        
        ttk.Button(strategy_buttons, text="Add Strategy", 
                  command=self.add_strategy).pack(side=tk.LEFT, padx=5)
        ttk.Button(strategy_buttons, text="Remove Strategy", 
                  command=self.remove_strategy).pack(side=tk.LEFT, padx=5)
        ttk.Button(strategy_buttons, text="Load Current", 
                  command=self.load_current_strategy).pack(side=tk.LEFT, padx=5)
        
        # Simulation parameters
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Hands per Run:").grid(row=0, column=0, sticky=tk.W)
        self.hands_var = tk.StringVar(value="10000")
        ttk.Spinbox(param_frame, from_=1000, to=100000, increment=1000,
                   textvariable=self.hands_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(param_frame, text="Number of Runs:").grid(row=1, column=0, sticky=tk.W)
        self.runs_var = tk.StringVar(value="5")
        ttk.Spinbox(param_frame, from_=1, to=20, 
                   textvariable=self.runs_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Run button
        ttk.Button(control_frame, text="Run Simulation", 
                  command=self.run_simulation).pack(pady=10)
        
        # Results visualization
        self.setup_results_panel()
    
    def setup_results_panel(self):
        """Setup results visualization panel."""
        
        results_frame = ttk.LabelFrame(self.parent, text="Simulation Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        
        # Performance comparison chart
        self.ax1 = self.fig.add_subplot(221)
        self.ax1.set_title("Win Rate Comparison")
        self.ax1.set_ylabel("bb/100")
        
        # Confidence intervals
        self.ax2 = self.fig.add_subplot(222)
        self.ax2.set_title("Confidence Intervals")
        self.ax2.set_ylabel("bb/100")
        
        # Variance analysis
        self.ax3 = self.fig.add_subplot(223)
        self.ax3.set_title("Variance Analysis")
        self.ax3.set_ylabel("Standard Deviation")
        
        # Hand distribution
        self.ax4 = self.fig.add_subplot(224)
        self.ax4.set_title("Performance by Position")
        self.ax4.set_ylabel("Win Rate")
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, results_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(results_frame, height=6, wrap=tk.WORD)
        self.status_text.pack(fill=tk.X, padx=5, pady=5)
    
    def add_strategy(self):
        """Add strategy file to comparison."""
        
        filename = filedialog.askopenfilename(
            title="Select Strategy File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            strategy_name = os.path.basename(filename)
            self.strategy_listbox.insert(tk.END, f"{strategy_name} ({filename})")
    
    def remove_strategy(self):
        """Remove selected strategy from comparison."""
        
        selection = self.strategy_listbox.curselection()
        if selection:
            self.strategy_listbox.delete(selection[0])
    
    def load_current_strategy(self):
        """Load currently edited strategy."""
        
        self.strategy_listbox.insert(tk.END, "Current Strategy (from editor)")
    
    def run_simulation(self):
        """Run the simulation with selected parameters."""
        
        if self.strategy_listbox.size() < 2:
            messagebox.showwarning("Insufficient Strategies", 
                                 "Please select at least 2 strategies to compare")
            return
        
        if not BACKEND_AVAILABLE:
            # Demo mode - generate fake results
            self.run_demo_simulation()
            return
        
        # Real simulation
        strategies = []
        for i in range(self.strategy_listbox.size()):
            item = self.strategy_listbox.get(i)
            if "Current Strategy" in item:
                # Save current strategy to temp file
                temp_file = "temp_current_strategy.json"
                # Implementation would save current strategy here
                strategies.append(temp_file)
            else:
                # Extract filename from listbox item
                filename = item.split("(")[1].rstrip(")")
                strategies.append(filename)
        
        # Run simulation in separate thread
        self.status_text.insert(tk.END, "Starting simulation...\n")
        
        thread = threading.Thread(target=self._run_simulation_thread, args=(strategies,))
        thread.daemon = True
        thread.start()
    
    def _run_simulation_thread(self, strategies):
        """Run simulation in background thread."""
        
        try:
            config = {
                'hands_per_run': int(self.hands_var.get()),
                'num_runs': int(self.runs_var.get()),
                'use_multiprocessing': True,
                'track_detailed_logs': True
            }
            
            engine = EnhancedSimulationEngine(strategies, config)
            results = engine.run_comprehensive_analysis()
            
            # Update UI in main thread
            self.parent.after(0, self._update_results, results)
            
        except Exception as e:
            self.parent.after(0, self._show_error, str(e))
    
    def _update_results(self, results):
        """Update results display with simulation results."""
        
        self.simulation_results = results
        
        # Clear previous plots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        # Extract data for plotting
        strategy_names = []
        win_rates = []
        ci_lower = []
        ci_upper = []
        variances = []
        
        for strategy_name, result in results['strategy_results'].items():
            name = os.path.basename(strategy_name).replace('.json', '')
            strategy_names.append(name)
            win_rates.append(result.win_rate_bb100)
            ci_lower.append(result.confidence_interval[0])
            ci_upper.append(result.confidence_interval[1])
            variances.append(result.variance)
        
        # Plot 1: Win Rate Comparison
        bars = self.ax1.bar(strategy_names, win_rates, 
                           color=['green' if wr > 0 else 'red' for wr in win_rates])
        self.ax1.set_title("Win Rate Comparison")
        self.ax1.set_ylabel("bb/100")
        self.ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add value labels on bars
        for bar, wr in zip(bars, win_rates):
            height = bar.get_height()
            self.ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                         f'{wr:.2f}', ha='center', va='bottom')
        
        # Plot 2: Confidence Intervals
        x_pos = range(len(strategy_names))
        self.ax2.errorbar(x_pos, win_rates, 
                         yerr=[np.array(win_rates) - np.array(ci_lower),
                               np.array(ci_upper) - np.array(win_rates)],
                         fmt='o', capsize=5)
        self.ax2.set_xticks(x_pos)
        self.ax2.set_xticklabels(strategy_names, rotation=45)
        self.ax2.set_title("95% Confidence Intervals")
        self.ax2.set_ylabel("bb/100")
        self.ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Plot 3: Variance Analysis
        self.ax3.bar(strategy_names, variances, color='orange', alpha=0.7)
        self.ax3.set_title("Variance Analysis")
        self.ax3.set_ylabel("Variance")
        
        # Plot 4: Position Performance (if available)
        if hasattr(list(results['strategy_results'].values())[0], 'position_performance'):
            # This would plot position-specific performance
            self.ax4.text(0.5, 0.5, "Position data\navailable", 
                         ha='center', va='center', transform=self.ax4.transAxes)
        else:
            self.ax4.text(0.5, 0.5, "Position data\nnot available", 
                         ha='center', va='center', transform=self.ax4.transAxes)
        
        self.ax4.set_title("Performance by Position")
        
        # Adjust layout and refresh
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Update status text
        self.status_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.status_text.insert(tk.END, "SIMULATION RESULTS:\n")
        
        for strategy_name, result in results['strategy_results'].items():
            name = os.path.basename(strategy_name)
            self.status_text.insert(tk.END, f"\n{name}:\n")
            self.status_text.insert(tk.END, f"  Win Rate: {result.win_rate_bb100:+.2f} bb/100\n")
            self.status_text.insert(tk.END, f"  95% CI: [{result.confidence_interval[0]:+.2f}, {result.confidence_interval[1]:+.2f}]\n")
            self.status_text.insert(tk.END, f"  Hands: {result.hands_played:,}\n")
        
        # Statistical significance
        if 'statistical_analysis' in results:
            self.status_text.insert(tk.END, "\nSTATISTICAL SIGNIFICANCE:\n")
            for comparison in results['statistical_analysis']['pairwise_comparisons']:
                if comparison.is_significant:
                    self.status_text.insert(tk.END, f"  ✅ Significant difference detected\n")
                    self.status_text.insert(tk.END, f"     {comparison.win_rate_difference:+.2f} bb/100 difference\n")
                else:
                    self.status_text.insert(tk.END, f"  ❓ No significant difference\n")
        
        self.status_text.insert(tk.END, "\nSimulation completed!\n")
        self.status_text.see(tk.END)
    
    def run_demo_simulation(self):
        """Run demo simulation with fake data."""
        
        # Generate fake results for demonstration
        strategies = []
        for i in range(self.strategy_listbox.size()):
            strategies.append(self.strategy_listbox.get(i).split(" ")[0])
        
        fake_results = {
            'strategy_results': {},
            'statistical_analysis': {
                'pairwise_comparisons': []
            }
        }
        
        for i, strategy in enumerate(strategies):
            # Generate realistic poker results
            base_wr = np.random.normal(0, 2)  # bb/100
            variance = np.random.uniform(15, 25)
            
            class FakeResult:
                def __init__(self, wr, var, hands):
                    self.win_rate_bb100 = wr
                    self.variance = var
                    self.hands_played = hands
                    self.confidence_interval = (wr - 1.5, wr + 1.5)
            
            fake_results['strategy_results'][strategy] = FakeResult(
                base_wr, variance, int(self.hands_var.get())
            )
        
        self._update_results(fake_results)
    
    def _show_error(self, error_msg):
        """Show error message in status text."""
        
        self.status_text.insert(tk.END, f"\nERROR: {error_msg}\n")
        self.status_text.see(tk.END)

class OptimizationDialog:
    """Dialog for running strategy optimization."""
    
    def __init__(self, parent, tiers):
        self.parent = parent
        self.tiers = tiers
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Strategy Optimization")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup optimization dialog UI."""
        
        # Optimization method
        method_frame = ttk.LabelFrame(self.dialog, text="Optimization Method")
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.method_var = tk.StringVar(value="standard")
        methods = [
            ("Quick (20 evaluations)", "quick"),
            ("Standard (50 evaluations)", "standard"),
            ("Thorough (100 evaluations)", "thorough")
        ]
        
        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, variable=self.method_var, 
                           value=value).pack(anchor=tk.W, padx=10, pady=2)
        
        # Complexity level
        complexity_frame = ttk.LabelFrame(self.dialog, text="Complexity Level")
        complexity_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.complexity_var = tk.StringVar(value="moderate")
        complexities = [
            ("Simple (Easy to learn)", "simple"),
            ("Moderate (Balanced)", "moderate"),
            ("Complex (Maximum performance)", "complex")
        ]
        
        for text, value in complexities:
            ttk.Radiobutton(complexity_frame, text=text, variable=self.complexity_var, 
                           value=value).pack(anchor=tk.W, padx=10, pady=2)
        
        # Progress area
        progress_frame = ttk.LabelFrame(self.dialog, text="Progress")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_text = tk.Text(progress_frame, height=8, wrap=tk.WORD)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Optimization", 
                                      command=self.start_optimization)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def start_optimization(self):
        """Start the optimization process."""
        
        if not BACKEND_AVAILABLE:
            self.progress_text.insert(tk.END, "❌ Backend not available - running demo\n")
            self.run_demo_optimization()
            return
        
        self.start_button.configure(state='disabled')
        self.progress_text.insert(tk.END, "🚀 Starting optimization...\n")
        
        # Run optimization in background thread
        thread = threading.Thread(target=self._run_optimization_thread)
        thread.daemon = True
        thread.start()
    
    def _run_optimization_thread(self):
        """Run optimization in background thread."""
        
        try:
            # Create tier configuration from current tiers
            tier_config = {}
            for tier in self.tiers:
                tier_config[tier.name] = {
                    'min_hs': tier.min_hs,
                    'max_hs': tier.max_hs
                }
            
            # Initialize optimizer interface
            interface = StrategyOptimizerInterface()
            interface.define_hs_tiers_from_strategy('baseline_strategy.json', tier_config)
            interface.set_simple_constraints(self.complexity_var.get())
            
            # Update progress
            self.dialog.after(0, self._update_progress, 10, "Initializing optimization...")
            
            # Run optimization
            result = interface.optimize_strategy(
                base_strategy_file='baseline_strategy.json',
                method=self.method_var.get(),
                output_prefix='gui_optimized'
            )
            
            # Update with results
            self.dialog.after(0, self._optimization_complete, result)
            
        except Exception as e:
            self.dialog.after(0, self._optimization_error, str(e))
    
    def _update_progress(self, progress, message):
        """Update progress display."""
        
        self.progress_var.set(progress)
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.see(tk.END)
    
    def _optimization_complete(self, result):
        """Handle optimization completion."""
        
        self.progress_var.set(100)
        self.progress_text.insert(tk.END, "\n" + "="*40 + "\n")
        self.progress_text.insert(tk.END, "🎉 OPTIMIZATION COMPLETE!\n")
        self.progress_text.insert(tk.END, f"Performance: {result['optimization_results']['final_performance']:+.2f} bb/100\n")
        self.progress_text.insert(tk.END, f"Readability: {result['optimization_results']['readability_score']:.1f}/100\n")
        self.progress_text.insert(tk.END, f"Complexity: {result['optimization_results']['complexity_rating']}\n")
        self.progress_text.insert(tk.END, f"Learning Time: ~{result['optimization_results']['learning_time_hours']:.1f} hours\n")
        self.progress_text.insert(tk.END, "\n📁 Files Created:\n")
        self.progress_text.insert(tk.END, f"Strategy: {result['files_created']['strategy_file']}\n")
        self.progress_text.insert(tk.END, f"Guide: {result['files_created']['guide_file']}\n")
        
        self.start_button.configure(state='normal', text='Optimization Complete')
    
    def _optimization_error(self, error_msg):
        """Handle optimization error."""
        
        self.progress_text.insert(tk.END, f"\n❌ OPTIMIZATION FAILED:\n{error_msg}\n")
        self.start_button.configure(state='normal')
    
    def run_demo_optimization(self):
        """Run demo optimization with fake progress."""
        
        import time
        
        def demo_progress():
            steps = [
                (10, "Analyzing tier configuration..."),
                (25, "Initializing search space..."),
                (40, "Running optimization iteration 1/5..."),
                (60, "Running optimization iteration 3/5..."),
                (85, "Running optimization iteration 5/5..."),
                (95, "Generating optimized strategy..."),
                (100, "Creating human-readable guide...")
            ]
            
            for progress, message in steps:
                self.dialog.after(0, self._update_progress, progress, message)
                time.sleep(1)
            
            # Fake results
            fake_result = {
                'optimization_results': {
                    'final_performance': 2.3,
                    'readability_score': 89.5,
                    'complexity_rating': 'MODERATE',
                    'learning_time_hours': 3.8
                },
                'files_created': {
                    'strategy_file': 'gui_optimized_strategy.json',
                    'guide_file': 'gui_optimized_guide.md'
                }
            }
            
            self.dialog.after(0, self._optimization_complete, fake_result)
        
        thread = threading.Thread(target=demo_progress)
        thread.daemon = True
        thread.start()

class PokerStrategyGUI:
    """Main application window."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Poker Strategy Development GUI")
        self.root.geometry("1400x900")
        
        # Set up the main interface
        self.setup_menu()
        self.setup_main_interface()
        
        # Initialize components
        self.strategy_editor = None
        self.simulation_interface = None
        
        self.show_startup_info()
    
    def setup_menu(self):
        """Setup the main menu bar."""
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Strategy", command=self.new_strategy)
        file_menu.add_command(label="Open Strategy", command=self.open_strategy)
        file_menu.add_command(label="Save Strategy", command=self.save_strategy)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Grid size submenu
        grid_size_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Grid Size", menu=grid_size_menu)
        
        grid_size_menu.add_command(label="Small", command=lambda: self.set_grid_size("Small"))
        grid_size_menu.add_command(label="Medium", command=lambda: self.set_grid_size("Medium"))
        grid_size_menu.add_command(label="Large", command=lambda: self.set_grid_size("Large"))
        grid_size_menu.add_command(label="Extra Large", command=lambda: self.set_grid_size("Extra Large"))
        
        view_menu.add_separator()
        view_menu.add_command(label="Refresh Hand Colors", command=self.refresh_hand_colors)
        view_menu.add_command(label="Clear Selection", command=self.clear_all_selections)
        view_menu.add_command(label="Debug Info", command=self.show_debug_info)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Optimize Strategy", command=self.optimize_strategy)
        tools_menu.add_command(label="Compare Strategies", command=self.compare_strategies)
        tools_menu.add_command(label="Generate Guide", command=self.generate_guide)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def set_grid_size(self, size):
        """Set grid size from menu."""
        if hasattr(self.strategy_editor, 'grid_sizes'):
            try:
                index = self.strategy_editor.grid_sizes.index(size)
                self.strategy_editor.grid_size_index = index
                self.strategy_editor.size_label.config(text=size)
                self.strategy_editor.on_grid_size_change()
            except ValueError:
                pass  # Size not found in list
    
    def refresh_hand_colors(self):
        """Refresh hand colors from menu."""
        if self.strategy_editor:
            self.strategy_editor.update_hand_colors()
    
    def clear_all_selections(self):
        """Clear all selections from menu."""
        if self.strategy_editor:
            self.strategy_editor.clear_hand_selection()
    
    def show_debug_info(self):
        """Show debug info from menu."""
        if self.strategy_editor:
            self.strategy_editor.print_debug_info()
    
    def setup_main_interface(self):
        """Setup the main tabbed interface."""
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Strategy Editor tab
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Strategy Editor")
        
        # Simulation tab
        self.simulation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_frame, text="Simulation & Testing")
        
        # Initialize interfaces
        self.strategy_editor = StrategyEditor(self.editor_frame)
        self.simulation_interface = SimulationInterface(self.simulation_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_startup_info(self):
        """Show startup information."""
        
        if BACKEND_AVAILABLE:
            self.status_bar.config(text="Backend loaded - Full functionality available")
        else:
            self.status_bar.config(text="Demo mode - Backend modules not available")
            messagebox.showinfo("Demo Mode", 
                               "Backend modules not available.\n"
                               "GUI running in demonstration mode.\n\n"
                               "To enable full functionality, ensure:\n"
                               "- enhanced_simulation_engine.py\n"
                               "- human_executable_optimizer.py\n"
                               "- simplified_optimizer_interface.py\n"
                               "are available in the same directory.")
    
    def new_strategy(self):
        """Create a new strategy."""
        self.strategy_editor.load_default_strategy()
        self.status_bar.config(text="New strategy created")
    
    def open_strategy(self):
        """Open an existing strategy."""
        self.strategy_editor.load_strategy()
    
    def save_strategy(self):
        """Save current strategy."""
        self.strategy_editor.save_strategy()
    
    def export_pdf(self):
        """Export strategy to PDF."""
        messagebox.showinfo("Export PDF", "PDF export functionality would be implemented here")
    
    def optimize_strategy(self):
        """Run strategy optimization."""
        self.strategy_editor.optimize_strategy()
    
    def compare_strategies(self):
        """Switch to simulation tab for strategy comparison."""
        self.notebook.select(self.simulation_frame)
    
    def generate_guide(self):
        """Generate human-readable strategy guide."""
        messagebox.showinfo("Generate Guide", "Guide generation functionality would be implemented here")
    
    def show_help(self):
        """Show help dialog."""
        
        help_text = """
Advanced Poker Strategy Development GUI

STRATEGY EDITOR:
• Click hands in the grid to select them
• Right-click hands for context menu options
• Use the tier panel to create and manage hand strength tiers
• Adjust decision tables using the right panel controls
• Use Auto-Optimize to find optimal decision thresholds

SIMULATION & TESTING:
• Add strategy files to compare multiple strategies
• Adjust simulation parameters (hands, runs)
• View results with confidence intervals and statistical analysis
• Visual charts show performance comparisons

TIPS:
• Start by organizing hands into tiers for easy memorization
• Use the optimization feature to find best decision tables
• Run simulations to validate strategy performance
• Export optimized strategies for real-world use
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """Show about dialog."""
        
        about_text = """
Advanced Poker Strategy Development GUI
Version 1.0

A comprehensive tool for developing, testing, and optimizing
poker strategies with human executability constraints.

Features:
• Visual hand strength tier management
• Decision table optimization
• Statistical simulation framework
• Human-executable strategy constraints
• Performance visualization and analysis

© 2025 - Advanced Hold'em Trainer Project
        """
        
        messagebox.showinfo("About", about_text)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

def main():
    """Main entry point for the GUI application."""
    
    try:
        app = PokerStrategyGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()