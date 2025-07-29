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
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 600)  # Set minimum size to ensure buttons are visible

    def setup_form(self, tier: Optional[HandStrengthTier]):
        """Creates and lays out the form widgets."""
        main_frame = ttk.Frame(self.dialog, padding="15", style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name field
        ttk.Label(main_frame, text="Tier Name:", style='Dark.TLabel').pack(anchor="w", pady=(0, 5))
        # Ensure tier name is properly displayed - show current tier name or "New Tier" for new tiers
        tier_name = tier.name if tier and tier.name else "New Tier"
        self.name_var = tk.StringVar(value=tier_name)
        # Use regular tk.Entry with explicit colors for better visibility
        name_entry = tk.Entry(main_frame, textvariable=self.name_var, width=30,
                             bg='white', fg='black', relief=tk.SUNKEN, bd=2,
                             font=('Arial', 10))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        # Select all text for easy editing
        name_entry.select_range(0, tk.END)
        
        # HS range slider
        range_frame = ttk.LabelFrame(main_frame, text="Hand Strength Range (1-45)", padding="10")
        range_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Range slider container
        slider_frame = ttk.Frame(range_frame)
        slider_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Initialize range values
        initial_min = tier.min_hs if tier else 1
        initial_max = tier.max_hs if tier else 10
        
        # Create range slider using Scale widgets
        self.min_hs_var = tk.IntVar(value=initial_min)
        self.max_hs_var = tk.IntVar(value=initial_max)
        
        # Min HS slider
        min_frame = ttk.Frame(slider_frame)
        min_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(min_frame, text="Min HS:", width=8).pack(side=tk.LEFT)
        self.min_slider = tk.Scale(min_frame, from_=1, to=45, orient=tk.HORIZONTAL, 
                                  variable=self.min_hs_var, length=200, 
                                  bg=THEME["bg"], fg=THEME["fg"], 
                                  highlightbackground=THEME["bg"], highlightcolor=THEME["bg"])
        self.min_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.min_label = ttk.Label(min_frame, text=str(initial_min), width=4)
        self.min_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Max HS slider
        max_frame = ttk.Frame(slider_frame)
        max_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(max_frame, text="Max HS:", width=8).pack(side=tk.LEFT)
        self.max_slider = tk.Scale(max_frame, from_=1, to=45, orient=tk.HORIZONTAL, 
                                  variable=self.max_hs_var, length=200,
                                  bg=THEME["bg"], fg=THEME["fg"], 
                                  highlightbackground=THEME["bg"], highlightcolor=THEME["bg"])
        self.max_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.max_label = ttk.Label(max_frame, text=str(initial_max), width=4)
        self.max_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind slider updates to labels
        self.min_hs_var.trace('w', self._update_min_label)
        self.max_hs_var.trace('w', self._update_max_label)
        
        # Add helpful info about auto-detection
        info_label = ttk.Label(range_frame, text="Note: Hands will be auto-detected based on HS range", 
                              style='Dark.TLabel', foreground='#888888')
        info_label.pack(pady=(5, 0))
        
        # Color selection with preset options
        color_frame = ttk.LabelFrame(main_frame, text="Tier Color", padding="10")
        color_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Preset color buttons
        preset_frame = ttk.Frame(color_frame)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(preset_frame, text="Quick Colors:").pack(side=tk.LEFT)
        
        # Define preset colors
        preset_colors = [
            ("Red", "#FF4444"), ("Blue", "#4444FF"), ("Green", "#44FF44"),
            ("Orange", "#FF8844"), ("Purple", "#8844FF"), ("Yellow", "#FFFF44"),
            ("Pink", "#FF44FF"), ("Cyan", "#44FFFF"), ("Brown", "#884444")
        ]
        
        color_buttons_frame = ttk.Frame(preset_frame)
        color_buttons_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        for color_name, color_hex in preset_colors:
            # Use Label with binding for better color display on macOS
            color_swatch = tk.Label(color_buttons_frame, text="", width=3, height=1,
                                   bg=color_hex, relief=tk.RAISED, bd=2)
            color_swatch.pack(side=tk.LEFT, padx=1)
            color_swatch.bind('<Button-1>', lambda e, c=color_hex: self._set_color(c))
            # Add hover effect
            color_swatch.bind('<Enter>', lambda e, swatch=color_swatch: swatch.configure(relief=tk.SUNKEN))
            color_swatch.bind('<Leave>', lambda e, swatch=color_swatch: swatch.configure(relief=tk.RAISED))
        
        # Custom color section
        custom_frame = ttk.Frame(color_frame)
        custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.color_var = tk.StringVar(value=tier.color if tier else "#FF4444")
        
        # Custom color button - use system colors for better macOS compatibility
        custom_btn = tk.Button(custom_frame, text="Custom Color", command=self.choose_color,
                              bg='#f0f0f0', fg='black', relief=tk.RAISED, bd=3,
                              font=('Arial', 10, 'bold'), width=14, height=2)
        custom_btn.pack(side=tk.LEFT)
        
        # Color preview
        self.color_preview = tk.Label(custom_frame, text="", width=4, height=2,
                                     bg=self.color_var.get(), relief=tk.RAISED, borderwidth=2)
        self.color_preview.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons - make them more prominent and ensure they're visible
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 10))
        
        # Use regular tk.Button for better visibility with larger size - same style for both
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.cancel_clicked, bg='#f0f0f0', fg='black', relief=tk.RAISED, bd=3,
                              font=('Arial', 12, 'bold'), width=12, height=2)
        cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        ok_btn = tk.Button(button_frame, text="OK", 
                           command=self.ok_clicked, bg='#f0f0f0', fg='black', relief=tk.RAISED, bd=3,
                           font=('Arial', 12, 'bold'), width=12, height=2)
        ok_btn.pack(side=tk.RIGHT)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())

    def choose_color(self):
        """Open color chooser dialog."""
        try:
            # Store current focus to restore it after color selection
            current_focus = self.dialog.focus_get()
            
            color = colorchooser.askcolor(color=self.color_var.get())
            if color[1]:  # If user didn't cancel
                self.color_var.set(color[1])
                # Update the color preview immediately
                self.color_preview.configure(bg=color[1])
            
            # Restore focus to prevent interference with other fields
            if current_focus:
                current_focus.focus_set()
        except ImportError:
            messagebox.showinfo("Info", "Color chooser not available. Please enter hex color manually.")

    def _set_color(self, color_hex: str):
        """Set color from preset button."""
        self.color_var.set(color_hex)
        self.color_preview.configure(bg=color_hex)
        
    def _update_color_preview(self, *args):
        """Update color preview when color changes."""
        try:
            color = self.color_var.get().strip()
            if color.startswith('#') and len(color) == 7:
                self.color_preview.configure(bg=color)
            else:
                # Set to default red if invalid
                self.color_preview.configure(bg='#FF0000')
        except tk.TclError:
            # Set to default red if error
            self.color_preview.configure(bg='#FF0000')

    def _update_min_label(self, *args):
        """Update min HS label when slider changes."""
        try:
            value = self.min_hs_var.get()
            self.min_label.configure(text=str(value))
        except tk.TclError:
            pass

    def _update_max_label(self, *args):
        """Update max HS label when slider changes."""
        try:
            value = self.max_hs_var.get()
            self.max_label.configure(text=str(value))
        except tk.TclError:
            pass

    def ok_clicked(self):
        """Validates form data and closes the dialog."""
        try:
            name = self.name_var.get().strip()
            min_hs = self.min_hs_var.get()  # Now IntVar, no need for int() conversion
            max_hs = self.max_hs_var.get()  # Now IntVar, no need for int() conversion
            color = self.color_var.get().strip()
            
            # Validation
            if not name:
                messagebox.showerror("Error", "Please enter a tier name.", parent=self.dialog)
                return
            
            if min_hs >= max_hs:
                messagebox.showerror("Error", "Minimum HS must be less than Maximum HS.", parent=self.dialog)
                return
            
            if min_hs < 1 or max_hs > 45:
                messagebox.showerror("Error", "HS range must be between 1 and 45.", parent=self.dialog)
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Please enter valid values: {str(e)}", parent=self.dialog)

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