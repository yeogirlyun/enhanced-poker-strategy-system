# filename: tier_panel.py
"""
Tier Management Panel for Strategy Development GUI

Handles tier creation, editing, and management operations.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Refactored from the main GUI file to handle all tier-related UI.
- Manages the tier listbox, info panel, and tier modification buttons.
- Interacts with dialogs and notifies the main app of changes via callbacks.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Optional
from gui_models import StrategyData, HandStrengthTier, THEME
from dialogs import TierEditDialog

class TierPanel:
    """
    Manages the UI panel for listing and editing HandStrengthTiers.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Encapsulates the tier listbox, control buttons, and info label.
    - Uses callbacks to communicate user actions to the main application.
    """
    def __init__(self, parent_frame, strategy_data: StrategyData, on_tier_change: Callable, on_tier_select: Callable):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_tier_change = on_tier_change
        self.on_tier_select = on_tier_select

        self._setup_ui()
        self.update_tier_display()

    def _setup_ui(self):
        """Sets up the main frame, controls, listbox, and info label."""
        self.tier_frame = ttk.LabelFrame(self.parent, text="Hand Strength Tiers", style='Dark.TLabelframe')
        self.tier_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        
        self._setup_controls()
        self._setup_listbox()
        self._setup_info_label()

    def _setup_controls(self):
        """Setup tier control buttons."""
        controls_frame = ttk.Frame(self.tier_frame, style='Dark.TFrame')
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tier management buttons
        ttk.Button(controls_frame, text="Add Tier", 
                  command=self.add_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Remove Tier", 
                  command=self.remove_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Edit Tier", 
                  command=self.edit_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=2)

    def _setup_listbox(self):
        """Setup tier listbox."""
        self.tier_listbox = tk.Listbox(self.tier_frame, height=6, selectmode=tk.EXTENDED, 
                                       bg=THEME["bg_light"], fg=THEME["fg"],
                                       highlightthickness=0, borderwidth=1, relief=tk.FLAT, 
                                       selectbackground=THEME["accent"])
        self.tier_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.tier_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)

    def _setup_info_label(self):
        """Setup tier information label."""
        self.tier_info_label = ttk.Label(self.tier_frame, text="Select a tier to view details", 
                                        style='Dark.TLabel', wraplength=400)
        self.tier_info_label.pack(padx=5, pady=5, fill=tk.X)

    def update_tier_display(self):
        """Reloads the tier data from the model into the listbox."""
        selected_indices = self.tier_listbox.curselection()
        self.tier_listbox.delete(0, tk.END)
        for tier in self.strategy_data.tiers:
            display_text = f"{tier.name} (HS {tier.min_hs}-{tier.max_hs}) - {len(tier.hands)} hands"
            self.tier_listbox.insert(tk.END, display_text)
        
        # Restore selection if possible
        for index in selected_indices:
            if index < len(self.strategy_data.tiers):
                self.tier_listbox.select_set(index)

    def add_tier(self):
        """Opens the edit dialog to add a new tier."""
        dialog = TierEditDialog(self.parent, "Add New Tier")
        if dialog.result:
            new_tier = HandStrengthTier(**dialog.result)
            self.strategy_data.add_tier(new_tier)
            self.update_tier_display()
            self._notify_change()

    def remove_tier(self):
        """Removes all selected tiers from the data model."""
        selected_indices = sorted(list(self.tier_listbox.curselection()), reverse=True)
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select one or more tiers to remove.")
            return
        
        # Confirm deletion
        tier_names = [self.strategy_data.tiers[i].name for i in selected_indices]
        if not messagebox.askyesno("Confirm Deletion", 
                                  f"Delete {len(tier_names)} tier(s)?\n" + 
                                  "\n".join(tier_names)):
            return
        
        for index in selected_indices:
            self.strategy_data.remove_tier(index)
        
        self.update_tier_display()
        self._notify_change()

    def edit_tier(self):
        """Opens the edit dialog for a single selected tier."""
        selected_indices = self.tier_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one tier to edit.")
            return
        
        index = selected_indices[0]
        tier_to_edit = self.strategy_data.tiers[index]
        
        dialog = TierEditDialog(self.parent, "Edit Tier", tier_to_edit)
        if dialog.result:
            tier_to_edit.name = dialog.result['name']
            tier_to_edit.min_hs = dialog.result['min_hs']
            tier_to_edit.max_hs = dialog.result['max_hs']
            tier_to_edit.color = dialog.result['color']
            
            self.update_tier_display()
            self._notify_change()

    def _on_listbox_select(self, event):
        """Handle tier listbox selection."""
        selected_indices = self.tier_listbox.curselection()
        
        if len(selected_indices) > 1:
            # Multi-select - show summary and trigger highlighting
            selected_tiers = [self.strategy_data.tiers[i] for i in selected_indices]
            self._show_multi_tier_info(selected_tiers)
            
            if self.on_tier_select:
                self.on_tier_select(selected_tiers)
                
        elif len(selected_indices) == 1:
            # Single select - show detailed info
            index = selected_indices[0]
            if index < len(self.strategy_data.tiers):
                tier = self.strategy_data.tiers[index]
                self._show_single_tier_info(tier)
                
                if self.on_tier_select:
                    self.on_tier_select([tier])
        else:
            # No selection
            self.tier_info_label.configure(text="Select a tier to view details")
            if self.on_tier_select:
                self.on_tier_select([])

    def _show_single_tier_info(self, tier: HandStrengthTier):
        """Show information for a single tier."""
        info_text = f"📋 {tier.name} Tier Details:\n"
        info_text += f"HS Range: {tier.min_hs}-{tier.max_hs}\n"
        info_text += f"Total Hands: {len(tier.hands)}\n"
        
        if tier.hands:
            info_text += f"Hands: {', '.join(tier.hands[:15])}"
            if len(tier.hands) > 15:
                info_text += f"\n+ {len(tier.hands) - 15} more"
        
        self.tier_info_label.configure(text=info_text)

    def _show_multi_tier_info(self, tiers: List[HandStrengthTier]):
        """Show information for multiple selected tiers."""
        from gui_models import GridSettings
        
        info_lines = []
        total_hands = 0
        
        for i, tier in enumerate(tiers):
            highlight_color = GridSettings.HIGHLIGHT_COLORS[i % len(GridSettings.HIGHLIGHT_COLORS)]
            info_lines.append(f"Tier: {tier.name} ({len(tier.hands)} hands)")
            total_hands += len(tier.hands)
        
        summary_text = f"{len(tiers)} tiers selected ({total_hands} total hands).\n"
        summary_text += "\n".join(info_lines)
        self.tier_info_label.configure(text=summary_text)

    def get_selected_tiers(self) -> List[HandStrengthTier]:
        """Get currently selected tiers."""
        selected_indices = self.tier_listbox.curselection()
        return [self.strategy_data.tiers[i] for i in selected_indices 
                if i < len(self.strategy_data.tiers)]

    def _notify_change(self):
        """Notify parent of tier changes."""
        if self.on_tier_change:
            self.on_tier_change()