#!/usr/bin/env python3
"""
Main GUI application for the Poker Strategy Development System.

REVISION HISTORY:
===============
Version 1.0 (2025-07-29) - Initial Version
- Created main application window with hand grid and tier management.
- Integrated hand grid and tier panel components.
Version 1.1 (2025-07-29) - Enhanced Font Controls
- Added general font size control system with Cmd+ menu.
- Improved default font sizes for better readability.
- Added font size controls for all GUI components.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui_models import StrategyData, THEME, GridSettings
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from dialogs import *

class PokerStrategyGUI:
    """
    Main GUI application for poker strategy development.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Poker Strategy Development")
        
        # Set window to 60% of screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.configure(bg=THEME["bg"])
        
        # Initialize strategy data
        self.strategy_data = StrategyData()
        self.strategy_data.load_default_tiers()
        
        # Font size control
        self.current_font_size_index = 6  # Start with "Giant" size (fills 75%+ of grid window)
        self.font_sizes = ["Small", "Medium", "Large", "Extra Large", "Huge", "Massive", "Giant", "Colossal"]
        
        self._setup_styles()
        self._setup_menu()
        self._setup_ui()
        self._bind_shortcuts()
        
        print(f"DEBUG: Main GUI initialized with font size: {self.font_sizes[self.current_font_size_index]}")

    def _setup_styles(self):
        """Setup the application styles."""
        style = ttk.Style(self.root)
        style.theme_use('clam')
        
        # Get current font configuration
        current_font_size = GridSettings.get_size_config(self.font_sizes[self.current_font_size_index])['font'][1]
        
        # Dark theme colors
        style.configure('.', background=THEME["bg"], foreground=THEME["fg"], 
                       font=(THEME["font_family"], current_font_size))
        
        # Dark theme styles
        style.configure('Dark.TFrame', background=THEME["bg_dark"])
        style.configure('Dark.TLabel', background=THEME["bg_dark"], foreground=THEME["fg"],
                       font=(THEME["font_family"], current_font_size))
        style.configure('Dark.TLabelframe', background=THEME["bg_dark"], bordercolor=THEME["bg_light"])
        style.configure('Dark.TLabelframe.Label', background=THEME["bg_dark"], foreground=THEME["fg"],
                       font=(THEME["font_family"], current_font_size))
        style.configure('Dark.TButton', background=THEME["bg_light"], foreground=THEME["fg"], 
                       borderwidth=1, font=(THEME["font_family"], current_font_size))
        style.map('Dark.TButton', background=[('active', THEME["accent"])])
        
        # Top area styles with dark sky blue background
        top_area_bg = "#1E3A5F"  # Dark sky blue
        top_area_fg = "#FFFFFF"   # White text for contrast
        top_area_border = "#2E5A8F"  # Slightly lighter border
        
        style.configure('TopArea.TFrame', background=top_area_bg)
        style.configure('TopArea.TLabel', background=top_area_bg, foreground=top_area_fg,
                       font=(THEME["font_family"], current_font_size))
        style.configure('TopArea.TLabelframe', background=top_area_bg, bordercolor=top_area_border)
        style.configure('TopArea.TLabelframe.Label', background=top_area_bg, foreground=top_area_fg,
                       font=(THEME["font_family"], current_font_size))
        style.configure('TopArea.TButton', background=top_area_border, foreground=top_area_fg, borderwidth=1,
                       font=(THEME["font_family"], current_font_size))
        style.map('TopArea.TButton', background=[('active', THEME["accent"])])

    def _setup_menu(self):
        """Setup the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Strategy", command=self._new_strategy)
        file_menu.add_command(label="Open Strategy", command=self._open_strategy)
        file_menu.add_command(label="Save Strategy", command=self._save_strategy)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Display", command=self._refresh_display)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear All Highlights", command=self._clear_all_highlights)
        tools_menu.add_command(label="Force Clear Highlights", command=self._force_clear_highlights)
        tools_menu.add_separator()
        tools_menu.add_command(label="Show Statistics", command=self._show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_ui(self):
        """Setup the main UI components with percentage-based sizing."""
        # Configure grid weights for percentage-based layout
        self.root.grid_rowconfigure(0, weight=20)  # Top area: 20%
        self.root.grid_rowconfigure(1, weight=80)  # Content area: 80%
        self.root.grid_columnconfigure(0, weight=60)  # Grid area: 60%
        self.root.grid_columnconfigure(1, weight=40)  # Tier area: 40%
        
        # TOP AREA: Menu and controls (20% of height)
        top_frame = ttk.LabelFrame(self.root, text="Application Controls", style='TopArea.TLabelframe')
        top_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        # Top row: Strategy and file controls
        strategy_row = ttk.Frame(top_frame, style='TopArea.TFrame')
        strategy_row.pack(fill=tk.X, padx=5, pady=2)
        
        # Create a centered container for all controls
        controls_container = ttk.Frame(strategy_row, style='TopArea.TFrame')
        controls_container.pack(expand=True, anchor=tk.CENTER)
        
        # Strategy file info
        ttk.Label(controls_container, text="Strategy:", style='TopArea.TLabel').pack(side=tk.LEFT, anchor=tk.CENTER)
        self.strategy_label = ttk.Label(controls_container, text="Default Strategy", style='TopArea.TLabel')
        self.strategy_label.pack(side=tk.LEFT, padx=5, anchor=tk.CENTER)
        
        # File operation buttons
        ttk.Button(controls_container, text="New", command=self._new_strategy, 
                  style='TopArea.TButton', width=8).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        ttk.Button(controls_container, text="Open", command=self._open_strategy, 
                  style='TopArea.TButton', width=8).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        ttk.Button(controls_container, text="Save", command=self._save_strategy, 
                  style='TopArea.TButton', width=8).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        
        # App font size controls
        ttk.Label(controls_container, text="App Font:", style='TopArea.TLabel').pack(side=tk.LEFT, padx=10, anchor=tk.CENTER)
        ttk.Button(controls_container, text="-", command=self._decrease_font_size, 
                  style='TopArea.TButton', width=4).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        
        self.font_size_label = ttk.Label(controls_container, 
                                       text=self.font_sizes[self.current_font_size_index], 
                                       style='TopArea.TLabel')
        self.font_size_label.pack(side=tk.LEFT, padx=5, anchor=tk.CENTER)
        
        ttk.Button(controls_container, text="+", command=self._increase_font_size, 
                  style='TopArea.TButton', width=4).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        
        # Grid control buttons
        ttk.Button(controls_container, text="Clear Highlights", 
                  command=self._clear_all_highlights, style='TopArea.TButton', width=12).pack(side=tk.LEFT, padx=10, anchor=tk.CENTER)
        ttk.Button(controls_container, text="Clear All", 
                  command=self._clear_all_highlights, style='TopArea.TButton', width=8).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        ttk.Button(controls_container, text="Force Clear", 
                  command=self._force_clear_highlights, style='TopArea.TButton', width=10).pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
        
        # LEFT AREA: Hand grid (60% width, 80% height)
        grid_frame = ttk.Frame(self.root, style='Dark.TFrame')
        grid_frame.grid(row=1, column=0, sticky='nsew', padx=(5, 2), pady=5)
        
        self.hand_grid = HandGridWidget(grid_frame, self.strategy_data, self._on_hand_click)
        
        # RIGHT AREA: Tiers/HS/Decision table panel (40% width, 80% height)
        right_panel_frame = ttk.Frame(self.root, style='Dark.TFrame')
        right_panel_frame.grid(row=1, column=1, sticky='nsew', padx=(2, 5), pady=5)
        
        self.tier_panel = TierPanel(right_panel_frame, self.strategy_data, 
                                   self._on_tier_data_change, self._on_tier_select)
        
        # Update strategy file display
        self._update_strategy_display()

    def _update_strategy_display(self):
        """Updates the strategy file display."""
        display_name = self.strategy_data.get_strategy_file_display_name()
        self.strategy_label.configure(text=display_name)

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        # Font size shortcuts
        self.root.bind('<Command-plus>', lambda e: self._increase_font_size())
        self.root.bind('<Command-minus>', lambda e: self._decrease_font_size())
        
        # Other shortcuts
        self.root.bind('<Command-r>', lambda e: self._refresh_display())
        self.root.bind('<Command-c>', lambda e: self._clear_all_highlights())
        self.root.bind('<Command-f>', lambda e: self._force_clear_highlights())

    def _increase_font_size(self):
        """Increase font size for all components."""
        if self.current_font_size_index < len(self.font_sizes) - 1:
            self.current_font_size_index += 1
            self._update_font_size()

    def _decrease_font_size(self):
        """Decrease font size for all components."""
        if self.current_font_size_index > 0:
            self.current_font_size_index -= 1
            self._update_font_size()

    def _update_font_size(self):
        """Update font size for all components."""
        new_size = self.font_sizes[self.current_font_size_index]
        
        print(f"DEBUG: Changing font size to '{new_size}' (index: {self.current_font_size_index})")
        
        # Update styles
        self._setup_styles()
        
        # Update font size label
        self.font_size_label.configure(text=new_size)
        
        # Update hand grid size to match app font size
        self.hand_grid.grid_size_index = self.current_font_size_index
        self.hand_grid._update_grid_state(grid_size=self.current_font_size_index)
        
        # Update tier panel fonts
        self._update_tier_panel_fonts()
        
        print(f"DEBUG: Font size changed to '{new_size}'")

    def _update_tier_panel_fonts(self):
        """Update fonts in the tier panel."""
        current_font_size = GridSettings.get_size_config(self.font_sizes[self.current_font_size_index])['font'][1]
        
        # Update tier panel fonts using the new method
        self.tier_panel.update_font_size(current_font_size)

    def _on_hand_click(self, hand: str, is_selected: bool):
        """Handle hand selection events."""
        print(f"DEBUG: Hand '{hand}' {'selected' if is_selected else 'deselected'}")

    def _on_tier_data_change(self):
        """Handle tier data changes."""
        print(f"DEBUG: Tier data changed")
        # Only update hand colors if no specific tier is selected
        if hasattr(self.hand_grid, '_current_tier_selection') and self.hand_grid._current_tier_selection is None:
            self.hand_grid.update_hand_colors()

    def _on_tier_select(self, selected_tiers):
        """Handle tier selection changes."""
        print(f"DEBUG: Tier selection changed - {len(selected_tiers)} tiers selected")
        self.hand_grid.highlight_tiers(selected_tiers)

    def _clear_all_highlights(self):
        """Clear all highlights."""
        print(f"DEBUG: Clearing all highlights")
        self.hand_grid.clear_all_highlights()

    def _force_clear_highlights(self):
        """Force clear all highlights."""
        print(f"DEBUG: Force clearing all highlights")
        self.hand_grid.force_clear_highlights()

    def _refresh_display(self):
        """Refresh the display."""
        print(f"DEBUG: Refreshing display")
        self.hand_grid._render_grid()

    def _show_statistics(self):
        """Show application statistics."""
        total_hands = self.tier_panel.get_total_hands_count()
        selected_hands = self.tier_panel.get_selected_hands_count()
        current_file = self.strategy_data.get_current_strategy_file()
        
        stats_text = f"Application Statistics:\n\n"
        stats_text += f"Current Strategy: {self.strategy_data.get_strategy_file_display_name()}\n"
        if current_file:
            stats_text += f"Strategy File: {current_file}\n"
        stats_text += f"Total Playable Hands: {total_hands}\n"
        stats_text += f"Currently Selected: {selected_hands}\n"
        stats_text += f"Available Tiers: {len(self.strategy_data.tiers)}\n"
        stats_text += f"Current Font Size: {self.font_sizes[self.current_font_size_index]}"
        
        messagebox.showinfo("Statistics", stats_text)

    def _new_strategy(self):
        """Create a new strategy."""
        if messagebox.askyesno("New Strategy", "Are you sure you want to create a new strategy? This will clear all current data."):
            self.strategy_data = StrategyData()
            self.strategy_data.load_default_tiers()
            self.hand_grid._render_grid()
            self.tier_panel._update_tier_list()
            self.tier_panel._update_counts()
            self._update_strategy_display()

    def _open_strategy(self):
        """Open a strategy file."""
        available_files = self.strategy_data.get_available_strategy_files()
        
        if not available_files:
            messagebox.showinfo("No Strategy Files", "No strategy files found in the current directory.")
            return
        
        # Create a simple file selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Open Strategy File")
        dialog.geometry("400x300")
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # File list
        listbox = tk.Listbox(dialog, bg=THEME["bg_dark"], fg=THEME["fg"], font=(THEME["font_family"], 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for file in available_files:
            listbox.insert(tk.END, file)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                filename = available_files[selection[0]]
                if self.strategy_data.load_strategy_from_file(filename):
                    self.hand_grid._render_grid()
                    self.tier_panel._update_tier_list()
                    self.tier_panel._update_counts()
                    self._update_strategy_display()
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Loaded strategy from '{filename}'")
                else:
                    messagebox.showerror("Error", f"Failed to load strategy from '{filename}'")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Load", command=load_selected, style='Dark.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel, style='Dark.TButton').pack(side=tk.RIGHT, padx=5)

    def _save_strategy(self):
        """Save the current strategy."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Save Strategy File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.strategy_data.save_strategy_to_file(filename):
                self._update_strategy_display()
                messagebox.showinfo("Success", f"Saved strategy to '{filename}'")
            else:
                messagebox.showerror("Error", f"Failed to save strategy to '{filename}'")

    def _show_about(self):
        """Show about dialog."""
        about_text = "Advanced Poker Strategy Development\n\n"
        about_text += "A comprehensive tool for developing and testing poker strategies.\n\n"
        about_text += "Features:\n"
        about_text += "• Hand strength tier management\n"
        about_text += "• Visual hand grid with tier highlighting\n"
        about_text += "• Font size controls\n"
        about_text += "• Multi-tier selection\n\n"
        about_text += "Version 1.1 - Enhanced Font Controls"
        
        messagebox.showinfo("About", about_text)

    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts_text = "Keyboard Shortcuts:\n\n"
        shortcuts_text += "Font Size Controls:\n"
        for i, size in enumerate(self.font_sizes[:8]):
            shortcuts_text += f"Cmd+{i+1}: {size}\n"
        shortcuts_text += "\nOther Controls:\n"
        shortcuts_text += "Cmd+R: Refresh Display\n"
        shortcuts_text += "Cmd+C: Clear All Highlights\n"
        shortcuts_text += "Cmd+F: Force Clear Highlights"
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    app = PokerStrategyGUI()
    app.run()

if __name__ == "__main__":
    main()