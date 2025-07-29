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
    A panel for managing hand strength tiers with improved count display.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to manage hand strength tiers.
    - Supports adding, removing, and editing tiers.
    Version 1.1 (2025-07-29) - Enhanced Count Display
    - Added total playable hands count display.
    - Added selected cards count when tiers are selected.
    - Improved visual feedback for tier selection.
    """
    
    def __init__(self, parent_frame, strategy_data: StrategyData, 
                 on_tier_change: Callable = None, on_tier_select: Callable = None):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_tier_change = on_tier_change
        self.on_tier_select = on_tier_select
        self.selected_tiers: List[HandStrengthTier] = []
        
        print(f"DEBUG: TierPanel initialized")
        
        self._setup_ui()
        self._update_tier_list()
        self._update_counts()

    def _setup_ui(self):
        """Sets up the tier management UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(self.parent, text="Tiers & Strategy Management", style='Dark.TLabelframe')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tier list frame
        list_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tier listbox with multi-select
        self.tier_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                      bg=THEME["bg_dark"], fg=THEME["fg"],
                                      font=(THEME["font_family"], THEME["font_size"]),
                                      height=15)  # Increased height for more space
        self.tier_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for tier list
        tier_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tier_listbox.yview)
        tier_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tier_listbox.configure(yscrollcommand=tier_scrollbar.set)
        
        # Bind selection event
        self.tier_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
        
        # Control buttons (compact layout)
        button_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Use smaller buttons for compact layout
        ttk.Button(button_frame, text="Add Tier", command=self._add_tier, 
                  style='Dark.TButton', width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove", command=self._remove_tier, 
                  style='Dark.TButton', width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Edit", command=self._edit_tier, 
                  style='Dark.TButton', width=10).pack(side=tk.LEFT, padx=2)
        
        # Count display frame (compact)
        count_frame = ttk.LabelFrame(self.main_frame, text="Statistics", style='Dark.TLabelframe')
        count_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Total playable hands count (compact)
        self.total_hands_label = ttk.Label(count_frame, text="Total Playable Hands: 0", 
                                         style='Dark.TLabel')
        self.total_hands_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Selected cards count (compact)
        self.selected_count_label = ttk.Label(count_frame, text="Selected Cards: 0", 
                                           style='Dark.TLabel')
        self.selected_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Tier details frame (more space for details)
        details_frame = ttk.LabelFrame(self.main_frame, text="Tier Details", style='Dark.TLabelframe')
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        self.tier_details_label = ttk.Label(details_frame, text="Select a tier to view details", 
                                          style='Dark.TLabel', wraplength=250)
        self.tier_details_label.pack(anchor=tk.NW, padx=5, pady=5, fill=tk.BOTH, expand=True)

    def update_font_size(self, font_size: int):
        """Update font size for all tier panel components."""
        font_config = (THEME["font_family"], font_size)
        
        # Update tier listbox font
        self.tier_listbox.configure(font=font_config)
        
        # Update label fonts
        self.total_hands_label.configure(font=font_config)
        self.selected_count_label.configure(font=font_config)
        self.tier_details_label.configure(font=font_config)
        
        print(f"DEBUG: Tier panel font size updated to {font_size}")

    def _update_tier_list(self):
        """Updates the tier listbox with current tiers."""
        self.tier_listbox.delete(0, tk.END)
        for tier in self.strategy_data.tiers:
            self.tier_listbox.insert(tk.END, f"{tier.name} (HS {tier.min_hs}-{tier.max_hs}) - {len(tier.hands)} hands")

    def _update_counts(self):
        """Updates the count displays."""
        # Calculate total playable hands across all tiers
        total_hands = sum(len(tier.hands) for tier in self.strategy_data.tiers)
        self.total_hands_label.configure(text=f"Total Playable Hands: {total_hands}")
        
        # Calculate selected cards count
        selected_hands = set()
        for tier in self.selected_tiers:
            selected_hands.update(tier.hands)
        
        self.selected_count_label.configure(text=f"Selected Cards: {len(selected_hands)}")
        
        print(f"DEBUG: Updated counts - Total: {total_hands}, Selected: {len(selected_hands)}")

    def _on_listbox_select(self, event):
        """Handles tier listbox selection changes."""
        selection = self.tier_listbox.curselection()
        self.selected_tiers = []
        
        if selection:
            for index in selection:
                if index < len(self.strategy_data.tiers):
                    self.selected_tiers.append(self.strategy_data.tiers[index])
        
        print(f"DEBUG: Tier selection changed - {len(self.selected_tiers)} tiers selected")
        for tier in self.selected_tiers:
            print(f"  DEBUG: Selected tier '{tier.name}' with {len(tier.hands)} hands: {tier.hands}")
        
        # Update counts
        self._update_counts()
        
        # Update tier details
        self._update_tier_details()
        
        # Notify parent of selection change
        if self.on_tier_select:
            self.on_tier_select(self.selected_tiers)

    def _update_tier_details(self):
        """Updates the tier details display with HS score information."""
        if len(self.selected_tiers) == 1:
            tier = self.selected_tiers[0]
            
            # Get HS scores for hands in this tier
            hand_hs_info = []
            for hand in sorted(tier.hands):
                hs_score = self._get_hand_strength(hand)
                if hs_score is not None:
                    hand_hs_info.append(f"{hand}({hs_score})")
                else:
                    hand_hs_info.append(hand)
            
            details_text = f"{tier.name} Tier Details:\n"
            details_text += f"HS Range: {tier.min_hs}-{tier.max_hs}\n"
            details_text += f"Total Hands: {len(tier.hands)}\n"
            details_text += f"Hands with HS: {', '.join(hand_hs_info)}"
            
        elif len(self.selected_tiers) > 1:
            total_hands = sum(len(tier.hands) for tier in self.selected_tiers)
            tier_names = [tier.name for tier in self.selected_tiers]
            
            # Get HS ranges for all selected tiers
            hs_ranges = []
            for tier in self.selected_tiers:
                hs_ranges.append(f"{tier.name}({tier.min_hs}-{tier.max_hs})")
            
            details_text = f"Multiple Tiers Selected:\n"
            details_text += f"Tiers: {', '.join(tier_names)}\n"
            details_text += f"HS Ranges: {', '.join(hs_ranges)}\n"
            details_text += f"Total Hands: {total_hands}"
        else:
            details_text = "Select a tier to view details"
        
        self.tier_details_label.configure(text=details_text)

    def _get_hand_strength(self, hand: str) -> Optional[int]:
        """Get the hand strength (HS) score for a given hand."""
        if not self.strategy_data.strategy_dict:
            return None
        
        # Get hand strength from strategy data
        hand_strength_table = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("preflop", {})
        return hand_strength_table.get(hand)

    def _add_tier(self):
        """Opens dialog to add a new tier."""
        dialog = TierEditDialog(self.parent, "Add New Tier")
        if dialog.result:
            new_tier = HandStrengthTier(**dialog.result)
            self.strategy_data.add_tier(new_tier)
            self._update_tier_list()
            self._update_counts()
            if self.on_tier_change:
                self.on_tier_change()

    def _remove_tier(self):
        """Removes the selected tier."""
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
        
        self._update_tier_list()
        self._update_counts()
        if self.on_tier_change:
            self.on_tier_change()

    def _edit_tier(self):
        """Opens dialog to edit the selected tier."""
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
            
            self._update_tier_list()
            self._update_counts()
            if self.on_tier_change:
                self.on_tier_change()

    def get_selected_tiers(self) -> List[HandStrengthTier]:
        """Returns the currently selected tiers."""
        return self.selected_tiers.copy()

    def get_total_hands_count(self) -> int:
        """Returns the total number of playable hands across all tiers."""
        return sum(len(tier.hands) for tier in self.strategy_data.tiers)

    def get_selected_hands_count(self) -> int:
        """Returns the number of hands in currently selected tiers."""
        selected_hands = set()
        for tier in self.selected_tiers:
            selected_hands.update(tier.hands)
        return len(selected_hands)