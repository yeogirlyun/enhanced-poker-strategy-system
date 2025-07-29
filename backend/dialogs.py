# filename: dialogs.py
"""
Dialog Windows for Strategy Development GUI

Contains all dialog windows for tier editing, file operations, etc.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created to consolidate all pop-up dialog windows into one module.
- Includes TierEditDialog, FileDialogs, and the AboutDialog.
- Promotes code reuse and separates dialog logic from main components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from typing import Optional, Dict, Any
from gui_models import HandStrengthTier, FileOperations, THEME

class TierEditDialog:
    """
    A modal dialog window for creating or editing a HandStrengthTier.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Provides a form for creating and editing HandStrengthTier objects.
    - Returns result dictionary upon successful completion.
    """
    def __init__(self, parent, title: str, tier: Optional[HandStrengthTier] = None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=THEME["bg"])
        
        # Center the dialog
        self._center_dialog()
        
        # Setup form
        self.setup_form(tier)
        
        # Make dialog modal
        self.dialog.wait_window()

    def _center_dialog(self):
        """Center dialog on screen."""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (280 // 2)
        self.dialog.geometry(f"350x280+{x}+{y}")

    def setup_form(self, tier: Optional[HandStrengthTier]):
        """Creates and lays out the form widgets."""
        main_frame = ttk.Frame(self.dialog, padding="15", style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(main_frame, text="Tier Name:", style='Dark.TLabel').pack(anchor="w", pady=(0, 5))
        self.name_var = tk.StringVar(value=tier.name if tier else "New Tier")
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        # HS range fields
        range_frame = ttk.LabelFrame(main_frame, text="Hand Strength Range", padding="10")
        range_frame.pack(fill=tk.X, pady=(0, 15))
        
        range_grid = ttk.Frame(range_frame)
        range_grid.pack()
        
        ttk.Label(range_grid, text="Minimum:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.min_hs_var = tk.StringVar(value=str(tier.min_hs) if tier else "1")
        ttk.Spinbox(range_grid, from_=1, to=50, textvariable=self.min_hs_var, 
                   width=8).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(range_grid, text="Maximum:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.max_hs_var = tk.StringVar(value=str(tier.max_hs) if tier else "10")
        ttk.Spinbox(range_grid, from_=1, to=50, textvariable=self.max_hs_var, 
                   width=8).grid(row=0, column=3)
        
        # Color selection
        color_frame = ttk.LabelFrame(main_frame, text="Color", padding="10")
        color_frame.pack(fill=tk.X, pady=(0, 15))
        
        color_grid = ttk.Frame(color_frame)
        color_grid.pack(fill=tk.X)
        
        self.color_var = tk.StringVar(value=tier.color if tier else "#808080")
        color_entry = ttk.Entry(color_grid, textvariable=self.color_var, width=12)
        color_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(color_grid, text="Choose", command=self.choose_color, style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Color preview
        self.color_preview = tk.Label(color_grid, text="   ", width=4, 
                                     bg=self.color_var.get(), relief=tk.RAISED, borderwidth=2)
        self.color_preview.pack(side=tk.LEFT)
        
        # Update preview when color changes
        self.color_var.trace('w', self._update_color_preview)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_clicked, style='Dark.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", 
                  command=self.ok_clicked, style='Dark.TButton').pack(side=tk.RIGHT)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())

    def choose_color(self):
        """Open color chooser dialog."""
        try:
            color = colorchooser.askcolor(color=self.color_var.get())
            if color[1]:  # If user didn't cancel
                self.color_var.set(color[1])
        except ImportError:
            messagebox.showinfo("Info", "Color chooser not available. Please enter hex color manually.")

    def _update_color_preview(self, *args):
        """Update color preview when color changes."""
        try:
            color = self.color_var.get()
            if color.startswith('#') and len(color) == 7:
                self.color_preview.configure(bg=color)
        except tk.TclError:
            pass  # Invalid color

    def ok_clicked(self):
        """Validates form data and closes the dialog."""
        try:
            name = self.name_var.get().strip()
            min_hs = int(self.min_hs_var.get())
            max_hs = int(self.max_hs_var.get())
            color = self.color_var.get().strip()
            
            # Validation
            if not name:
                messagebox.showerror("Error", "Please enter a tier name.", parent=self.dialog)
                return
            
            if min_hs >= max_hs:
                messagebox.showerror("Error", "Minimum HS must be less than Maximum HS.", parent=self.dialog)
                return
            
            if not self._is_valid_color(color):
                messagebox.showerror("Error", "Please enter a valid hex color (e.g., #FF0000).", parent=self.dialog)
                return
            
            self.result = {
                'name': name,
                'min_hs': min_hs,
                'max_hs': max_hs,
                'color': color
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.", parent=self.dialog)

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()

    def _is_valid_color(self, color: str) -> bool:
        """Check if color is valid hex format."""
        if not color.startswith('#') or len(color) != 7:
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

class FileDialog:
    """
    A static class to wrap file dialog functionality.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Provides static methods for opening and saving strategy files.
    """
    @staticmethod
    def load_strategy() -> Optional[Dict]:
        filename = filedialog.askopenfilename(title="Load Strategy", filetypes=[("JSON files", "*.json")])
        if filename:
            strategy = FileOperations.load_strategy(filename)
            if strategy:
                messagebox.showinfo("Success", f"Loaded strategy from {filename}")
                return strategy
            else:
                messagebox.showerror("Error", f"Failed to load strategy from {filename}")
        return None

    @staticmethod
    def save_strategy(strategy: Dict) -> bool:
        filename = filedialog.asksaveasfilename(title="Save Strategy", defaultextension=".json", 
                                              filetypes=[("JSON files", "*.json")])
        if filename:
            if FileOperations.save_strategy(strategy, filename):
                messagebox.showinfo("Success", f"Saved strategy to {filename}")
                return True
            else:
                messagebox.showerror("Error", f"Failed to save strategy to {filename}")
        return False

class AboutDialog:
    """
    The 'About' dialog window for the application.
    
    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - A simple, static dialog to display application info.
    """
    def __init__(self, parent):
        dialog = tk.Toplevel(parent)
        dialog.title("About Strategy Development GUI")
        dialog.geometry("450x350")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"450x350+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Poker Strategy Development GUI", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Version info
        info_text = """Version 2.0 - Modular Edition

A comprehensive tool for developing and testing poker strategies:

✓ Visual hand strength tier management
✓ Interactive decision table editing  
✓ Strategy simulation and testing
✓ Human-executable optimization
✓ Statistical analysis and validation
✓ Modular architecture for maintainability

Each module is focused and under 250 lines of code."""
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Close button
        ttk.Button(main_frame, text="Close", command=dialog.destroy).pack()