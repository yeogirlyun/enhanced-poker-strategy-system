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
        
        # Control buttons (using TopMenu.TButton style for consistency)
        button_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Use TopMenu.TButton style for consistency with top menu, but maintain current size
        self.add_tier_btn = ttk.Button(button_frame, text="Add Tier", command=self._add_tier, 
                                      style='TopMenu.TButton', width=10)
        self.add_tier_btn.pack(side=tk.LEFT, padx=2)
        
        self.remove_tier_btn = ttk.Button(button_frame, text="Remove", command=self._remove_tier, 
                                         style='TopMenu.TButton', width=10)
        self.remove_tier_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_tier_btn = ttk.Button(button_frame, text="Edit", command=self._edit_tier, 
                                       style='TopMenu.TButton', width=10)
        self.edit_tier_btn.pack(side=tk.LEFT, padx=2)
        
        # Count display frame (compact)
        count_frame = ttk.LabelFrame(self.main_frame, text="Statistics", style='Dark.TLabelframe')
        count_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Total playable hands count (compact)
        self.total_hands_label = ttk.Label(count_frame, text="Total Playable Hands: 0", 
                                         style='Dark.TLabel')
        self.total_hands_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Selected hand frame
        self.selected_hand_frame = ttk.LabelFrame(self.main_frame, text="Selected Hand", style='Dark.TLabelframe')
        self.selected_hand_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Selected hand info
        self.selected_hand_label = ttk.Label(self.selected_hand_frame, text="Click a hand in the grid to edit its HS score", 
                                           style='Dark.TLabel')
        self.selected_hand_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # HS score editing frame
        self.hs_edit_frame = ttk.Frame(self.selected_hand_frame, style='Dark.TFrame')
        self.hs_edit_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.hs_edit_frame, text="HS Score:", style='Dark.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.hs_score_var = tk.StringVar()
        self.hs_score_entry = ttk.Entry(self.hs_edit_frame, textvariable=self.hs_score_var, 
                                      width=8, style="SkyBlue.TEntry")
        self.hs_score_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.update_hs_btn = ttk.Button(self.hs_edit_frame, text="Update HS", 
                                       command=self._update_hs_score, style='TopMenu.TButton')
        self.update_hs_btn.pack(side=tk.LEFT, padx=2)
        
        # Initially hide the HS editing controls
        self.selected_hand_frame.pack_forget()
        
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
        
        # Update button fonts to maintain current size (not 120% like top menu)
        button_font = (THEME["font_family"], font_size, 'bold')
        try:
            self.add_tier_btn.configure(font=button_font)
            self.remove_tier_btn.configure(font=button_font)
            self.edit_tier_btn.configure(font=button_font)
        except tk.TclError:
            # ttk widgets don't support direct font configuration
            pass
        

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
        

    def _on_listbox_select(self, event):
        """Handles tier listbox selection changes."""
        selection = self.tier_listbox.curselection()
        self.selected_tiers = []
        
        if selection:
            for index in selection:
                if index < len(self.strategy_data.tiers):
                    self.selected_tiers.append(self.strategy_data.tiers[index])
        
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
        """Opens dialog to add a new tier with auto-detection of hands and overlap prevention."""
        dialog = TierEditDialog(self.parent, "Add New Tier")
        if dialog.result:
            new_tier = HandStrengthTier(**dialog.result)
            
            # Check for overlapping HS ranges and resolve conflicts
            if self._has_overlapping_ranges(new_tier):
                if not self._resolve_overlapping_ranges(new_tier):
                    return  # User cancelled the operation
            
            # Auto-detect hands for the new tier based on HS range
            self._update_tier_hands_based_on_hs_range(new_tier)
            
            self.strategy_data.add_tier(new_tier)
            
            # Update strategy dictionary to include new tier
            self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
            
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
        """Opens dialog to edit the selected tier with enhanced hand management and overlap prevention."""
        selected_indices = self.tier_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Selection Error", "Please select exactly one tier to edit.")
            return
        
        index = selected_indices[0]
        tier_to_edit = self.strategy_data.tiers[index]
        
        dialog = TierEditDialog(self.parent, "Edit Tier", tier_to_edit)
        if dialog.result:
            # Store original values for comparison
            original_min_hs = tier_to_edit.min_hs
            original_max_hs = tier_to_edit.max_hs
            original_hands = tier_to_edit.hands.copy()
            
            # Create temporary tier to check for overlaps
            temp_tier = HandStrengthTier(
                name=dialog.result['name'],
                min_hs=dialog.result['min_hs'],
                max_hs=dialog.result['max_hs'],
                color=dialog.result['color'],
                hands=[]
            )
            
            # Check for overlapping HS ranges (excluding the current tier being edited)
            has_overlap = False
            overlapping_tiers = []
            for i, existing_tier in enumerate(self.strategy_data.tiers):
                if i != index:  # Skip the tier being edited
                    if (temp_tier.min_hs <= existing_tier.max_hs and 
                        temp_tier.max_hs >= existing_tier.min_hs):
                        has_overlap = True
                        overlapping_tiers.append(existing_tier)
            
            if has_overlap:
                # Show conflict dialog
                conflict_msg = f"HS range {temp_tier.min_hs}-{temp_tier.max_hs} overlaps with existing tiers:\n\n"
                for tier in overlapping_tiers:
                    conflict_msg += f"• {tier.name} (HS {tier.min_hs}-{tier.max_hs})\n"
                
                conflict_msg += "\nChoose an option:\n"
                conflict_msg += "• 'Auto-adjust': Automatically adjust the tier's range\n"
                conflict_msg += "• 'Cancel': Cancel editing the tier"
                
                choice = messagebox.askyesnocancel("HS Range Conflict", conflict_msg)
                
                if choice is None:  # Cancel
                    return
                elif choice:  # Auto-adjust
                    if not self._auto_adjust_range_for_edit(temp_tier, overlapping_tiers, index):
                        return  # User cancelled
                    # Update dialog result with adjusted values
                    dialog.result['min_hs'] = temp_tier.min_hs
                    dialog.result['max_hs'] = temp_tier.max_hs
            
            # Update basic properties
            tier_to_edit.name = dialog.result['name']
            tier_to_edit.min_hs = dialog.result['min_hs']
            tier_to_edit.max_hs = dialog.result['max_hs']
            tier_to_edit.color = dialog.result['color']
            
            # Handle hand management based on HS range changes
            if original_min_hs != tier_to_edit.min_hs or original_max_hs != tier_to_edit.max_hs:
                self._update_tier_hands_based_on_hs_range(tier_to_edit)
            
            # Update strategy dictionary to reflect changes
            self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
            
            self._update_tier_list()
            self._update_counts()
            if self.on_tier_change:
                self.on_tier_change()
            

    def _has_overlapping_ranges(self, new_tier: HandStrengthTier) -> bool:
        """Check if the new tier's HS range overlaps with existing tiers."""
        for existing_tier in self.strategy_data.tiers:
            # Check if ranges overlap
            if (new_tier.min_hs <= existing_tier.max_hs and 
                new_tier.max_hs >= existing_tier.min_hs):
                return True
        return False
    
    def _resolve_overlapping_ranges(self, new_tier: HandStrengthTier) -> bool:
        """Resolve overlapping HS ranges by adjusting the new tier's range."""
        overlapping_tiers = []
        for existing_tier in self.strategy_data.tiers:
            if (new_tier.min_hs <= existing_tier.max_hs and 
                new_tier.max_hs >= existing_tier.min_hs):
                overlapping_tiers.append(existing_tier)
        
        if not overlapping_tiers:
            return True
        
        # Show conflict dialog
        conflict_msg = f"HS range {new_tier.min_hs}-{new_tier.max_hs} overlaps with existing tiers:\n\n"
        for tier in overlapping_tiers:
            conflict_msg += f"• {tier.name} (HS {tier.min_hs}-{tier.max_hs})\n"
        
        conflict_msg += "\nChoose an option:\n"
        conflict_msg += "• 'Auto-adjust': Automatically adjust the new tier's range\n"
        conflict_msg += "• 'Cancel': Cancel adding the tier"
        
        choice = messagebox.askyesnocancel("HS Range Conflict", conflict_msg)
        
        if choice is None:  # Cancel
            return False
        elif choice:  # Auto-adjust
            return self._auto_adjust_range(new_tier, overlapping_tiers)
        else:  # Cancel
            return False
    
    def _auto_adjust_range(self, new_tier: HandStrengthTier, overlapping_tiers: List[HandStrengthTier]) -> bool:
        """Automatically adjust the new tier's HS range to avoid overlaps."""
        # Find the largest gap in HS ranges
        all_ranges = [(tier.min_hs, tier.max_hs) for tier in self.strategy_data.tiers]
        all_ranges.append((new_tier.min_hs, new_tier.max_hs))
        all_ranges.sort()
        
        # Find gaps between ranges
        gaps = []
        for i in range(len(all_ranges) - 1):
            current_max = all_ranges[i][1]
            next_min = all_ranges[i + 1][0]
            if next_min > current_max + 1:  # Gap exists
                gaps.append((current_max + 1, next_min - 1))
        
        if gaps:
            # Use the largest gap
            largest_gap = max(gaps, key=lambda x: x[1] - x[0])
            new_tier.min_hs = largest_gap[0]
            new_tier.max_hs = largest_gap[1]
            
            messagebox.showinfo("Range Adjusted", 
                              f"New tier range adjusted to HS {new_tier.min_hs}-{new_tier.max_hs}")
            return True
        else:
            # No gaps available, ask user to choose a different range
            messagebox.showerror("No Available Range", 
                               "No non-overlapping HS range available. Please choose a different range.")
            return False
    
    def _auto_adjust_range_for_edit(self, tier_to_edit: HandStrengthTier, overlapping_tiers: List[HandStrengthTier], edit_index: int) -> bool:
        """Automatically adjust the tier's HS range to avoid overlaps during editing."""
        # Create a list of ranges excluding the tier being edited
        all_ranges = []
        for i, tier in enumerate(self.strategy_data.tiers):
            if i != edit_index:  # Exclude the tier being edited
                all_ranges.append((tier.min_hs, tier.max_hs))
        
        # Add the new range to find gaps
        all_ranges.append((tier_to_edit.min_hs, tier_to_edit.max_hs))
        all_ranges.sort()
        
        # Find gaps between ranges
        gaps = []
        for i in range(len(all_ranges) - 1):
            current_max = all_ranges[i][1]
            next_min = all_ranges[i + 1][0]
            if next_min > current_max + 1:  # Gap exists
                gaps.append((current_max + 1, next_min - 1))
        
        if gaps:
            # Use the largest gap
            largest_gap = max(gaps, key=lambda x: x[1] - x[0])
            tier_to_edit.min_hs = largest_gap[0]
            tier_to_edit.max_hs = largest_gap[1]
            
            messagebox.showinfo("Range Adjusted", 
                              f"Tier range adjusted to HS {tier_to_edit.min_hs}-{tier_to_edit.max_hs}")
            return True
        else:
            # No gaps available, ask user to choose a different range
            messagebox.showerror("No Available Range", 
                               "No non-overlapping HS range available. Please choose a different range.")
            return False

    def _update_tier_hands_based_on_hs_range(self, tier: HandStrengthTier):
        """Updates tier hands based on HS range, auto-detecting if needed."""
        if not self.strategy_data.strategy_dict:
            return
        
        # Get all available hands and their HS scores
        hand_strength_table = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("preflop", {})
        if not hand_strength_table:
            return
        
        # Find hands that belong to this HS range
        matching_hands = []
        for hand, hs_score in hand_strength_table.items():
            if tier.min_hs <= hs_score <= tier.max_hs:
                matching_hands.append(hand)
        
        # Update tier hands
        tier.hands = sorted(matching_hands)
        

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
    
    def set_selected_hand(self, hand: str):
        """Sets the selected hand for HS score editing."""
        self.selected_hand = hand
        current_hs = self._get_hand_strength(hand) or 0
        self.hs_score_var.set(str(current_hs))
        self.selected_hand_label.config(text=f"Selected Hand: {hand} (Current HS: {current_hs})")
        self.selected_hand_frame.pack(fill=tk.X, padx=5, pady=3)
    
    def clear_selected_hand(self):
        """Clears the selected hand."""
        self.selected_hand = None
        self.hs_score_var.set("")
        self.selected_hand_label.config(text="Click a hand in the grid to edit its HS score")
        self.selected_hand_frame.pack_forget()
    
    def _update_hs_score(self):
        """Updates the HS score for the selected hand and auto-adjusts tier placement."""
        if not hasattr(self, 'selected_hand') or not self.selected_hand:
            return
        
        try:
            new_hs = int(self.hs_score_var.get())
            if new_hs < 0 or new_hs > 100:
                messagebox.showerror("Invalid HS Score", "HS score must be between 0 and 100")
                return
            
            # Update the strategy data
            if "hand_strength_tables" not in self.strategy_data.strategy_dict:
                self.strategy_data.strategy_dict["hand_strength_tables"] = {}
            if "preflop" not in self.strategy_data.strategy_dict["hand_strength_tables"]:
                self.strategy_data.strategy_dict["hand_strength_tables"]["preflop"] = {}
            
            self.strategy_data.strategy_dict["hand_strength_tables"]["preflop"][self.selected_hand] = new_hs
            
            # Auto-adjust tier placement
            self._auto_adjust_hand_to_tier(self.selected_hand, new_hs)
            
            # Update the display
            self.selected_hand_label.config(text=f"Selected Hand: {self.selected_hand} (Current HS: {new_hs})")
            
            # Notify the main app to update the grid
            if self.on_tier_change:
                self.on_tier_change()
                
            messagebox.showinfo("Success", f"HS score for {self.selected_hand} updated to {new_hs}")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for HS score")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update HS score: {e}")
    
    def _auto_adjust_hand_to_tier(self, hand: str, new_hs: int):
        """Automatically moves a hand to the correct tier based on its HS score."""
        # Remove hand from all tiers first
        for tier in self.strategy_data.tiers:
            if hand in tier.hands:
                tier.hands.remove(hand)
        
        # Find the correct tier for the new HS score
        target_tier = None
        for tier in self.strategy_data.tiers:
            if tier.min_hs <= new_hs <= tier.max_hs:
                target_tier = tier
                break
        
        # Add hand to the correct tier
        if target_tier:
            target_tier.hands.add(hand)  # Use add() for sets
        
        # Update tier list display
        self._update_tier_list()
        self._update_counts()