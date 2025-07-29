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
        self.font_sizes = ["1", "2", "3", "4", "5", "6", "7", "8"]
        
        # Setup styles with initial button font (120% of default)
        initial_font_size = GridSettings.get_size_config(self.font_sizes[self.current_font_size_index])['font'][1]
        initial_button_font = ('Arial', int(initial_font_size * 1.2), 'bold')
        self._setup_styles(initial_button_font)
        self._setup_menu()
        self._setup_ui()
        self._bind_shortcuts()
        
        # Apply initial font size to all components
        self._apply_initial_font_size()
        
        print(f"DEBUG: Main GUI initialized with font size: {self.font_sizes[self.current_font_size_index]}")

    def _setup_styles(self, button_font=('Arial', 12, 'bold')):
        """Setup the application styles."""
        style = ttk.Style()
        style.theme_use('default')
        
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

        # Custom style for top menu buttons with light pink background and dynamic font
        style.configure('TopMenu.TButton',
                        background='#FFE4E1',  # Light pink background
                        foreground='#333',
                        borderwidth=3,
                        relief='raised',
                        focusthickness=3,
                        focuscolor='black',
                        font=button_font,
                        padding=8)
        style.map('TopMenu.TButton',
                  background=[('active', '#FFB6C1'), ('pressed', '#FFC0CB')],
                  relief=[('pressed', 'sunken'), ('active', 'raised')])

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

        tools_menu.add_separator()
        tools_menu.add_command(label="Show Statistics", command=self._show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_ui(self):
        """Setup the main UI components with percentage-based sizing."""
        # Configure grid weights for percentage-based layout
        self.root.grid_rowconfigure(0, weight=7)   # Top area: 7%
        self.root.grid_rowconfigure(1, weight=93)  # Content area: 93%
        self.root.grid_columnconfigure(0, weight=60)  # Grid area: 60%
        self.root.grid_columnconfigure(1, weight=40)  # Tier area: 40%
        
        # TOP AREA: Menu and controls (20% of height)
        top_frame = ttk.LabelFrame(self.root, text="Application Controls", style='TopArea.TLabelframe')
        top_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=2, pady=0)
        
        # Configure top_frame to center its content
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        
        # Create a centered container for all controls using grid
        controls_container = ttk.Frame(top_frame, style='TopArea.TFrame')
        controls_container.grid(row=0, column=0, sticky='nsew', padx=2, pady=0)
        
        # Configure the controls container for compact layout (50% of space)
        controls_container.grid_rowconfigure(0, weight=1)
        # Configure columns to take up only 50% of horizontal space
        for i in range(24):  # Double the number of columns
            controls_container.grid_columnconfigure(i, weight=1)
        controls_container.grid_columnconfigure(14, weight=1)
        
        # Strategy file info
        ttk.Label(controls_container, text="Strategy:", style='TopArea.TLabel').grid(row=0, column=2, padx=1, pady=0, sticky='nsew')
        self.strategy_label = ttk.Label(controls_container, text="Default Strategy", style='TopArea.TLabel')
        self.strategy_label.grid(row=0, column=3, padx=1, pady=0, sticky='nsew')
        
        # File operation buttons with 3D effects and dynamic font sizing
        button_font_size = max(8, int(GridSettings.get_size_config(self.font_sizes[self.current_font_size_index])['font'][1] * 1.2))
        button_font = ('Arial', button_font_size, 'bold')
        
        self.new_btn = ttk.Button(controls_container, text="New", command=self._new_strategy, style='TopMenu.TButton')
        self.new_btn.grid(row=0, column=4, padx=2, pady=2, sticky='nsew')
        
        self.open_btn = ttk.Button(controls_container, text="Open", command=self._open_strategy, style='TopMenu.TButton')
        self.open_btn.grid(row=0, column=5, padx=2, pady=2, sticky='nsew')
        
        self.save_btn = ttk.Button(controls_container, text="Save", command=self._save_strategy, style='TopMenu.TButton')
        self.save_btn.grid(row=0, column=6, padx=2, pady=2, sticky='nsew')
        
        # App font size controls
        ttk.Label(controls_container, text="App Font:", style='TopArea.TLabel').grid(row=0, column=8, padx=5, pady=0, sticky='nsew')
        
        # Decrease button with larger graphical symbol
        self.decrease_btn = ttk.Button(controls_container, text="−", command=self._decrease_font_size, style='TopMenu.TButton')
        self.decrease_btn.grid(row=0, column=9, padx=2, pady=2, sticky='nsew')
        
        # Font size label (center-aligned)
        self.font_size_label = ttk.Label(controls_container, 
                                       text=self.font_sizes[self.current_font_size_index], 
                                       style='TopArea.TLabel', anchor='center', font=('Arial', 12, 'bold'))
        self.font_size_label.grid(row=0, column=10, padx=3, pady=2, sticky='ew')
        
        # Increase button with larger graphical symbol
        self.increase_btn = ttk.Button(controls_container, text="+", command=self._increase_font_size, style='TopMenu.TButton')
        self.increase_btn.grid(row=0, column=11, padx=2, pady=2, sticky='nsew')
        
        # Grid control buttons with 3D effects
        self.clear_highlights_btn = ttk.Button(controls_container, text="Clear Highlights", command=self._clear_all_highlights, style='TopMenu.TButton')
        self.clear_highlights_btn.grid(row=0, column=13, padx=3, pady=2, sticky='nsew')
        
        self.clear_all_btn = ttk.Button(controls_container, text="Clear All", command=self._clear_all_highlights, style='TopMenu.TButton')
        self.clear_all_btn.grid(row=0, column=14, padx=2, pady=2, sticky='nsew')
        
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
        
        # Get current font configuration
        current_font_size = GridSettings.get_size_config(new_size)['font'][1]
        font_config = (THEME["font_family"], current_font_size)
        
        # Calculate button font size (120% of app font size)
        button_font_size = max(8, int(current_font_size * 1.2))
        button_font = ('Arial', button_font_size, 'bold')
        
        # Update styles with new button font
        self._setup_styles(button_font)
        
        # Update font size label
        self.font_size_label.configure(text=new_size)
        
        # Update top menu area fonts
        self._update_top_menu_fonts(font_config)
        
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
    
    def _update_top_menu_fonts(self, font_config):
        """Update fonts in the top menu area."""
        # Calculate button font size (120% of app font size)
        button_font_size = max(8, int(font_config[1] * 1.2))
        button_font = ('Arial', button_font_size, 'bold')
        
        # Update strategy label
        self.strategy_label.configure(font=font_config)
        
        # Update button fonts - use style configuration for ttk widgets
        if hasattr(self, 'new_btn'):
            try:
                self.new_btn.configure(font=button_font)
            except tk.TclError:
                # ttk widgets don't support direct font configuration
                pass
        if hasattr(self, 'open_btn'):
            try:
                self.open_btn.configure(font=button_font)
            except tk.TclError:
                pass
        if hasattr(self, 'save_btn'):
            try:
                self.save_btn.configure(font=button_font)
            except tk.TclError:
                pass
        if hasattr(self, 'decrease_btn'):
            try:
                self.decrease_btn.configure(font=button_font)
            except tk.TclError:
                pass
        if hasattr(self, 'increase_btn'):
            try:
                self.increase_btn.configure(font=button_font)
            except tk.TclError:
                pass
        if hasattr(self, 'clear_highlights_btn'):
            try:
                self.clear_highlights_btn.configure(font=button_font)
            except tk.TclError:
                pass
        if hasattr(self, 'clear_all_btn'):
            try:
                self.clear_all_btn.configure(font=button_font)
            except tk.TclError:
                pass
        
        # Update all ttk widgets in the top area to use the new font
        # This ensures consistency across all top menu components
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.grid_info()['row'] == 0:
                # This is the top frame, update all its children
                self._update_widget_fonts_recursive(widget, font_config)
    
    def _update_widget_fonts_recursive(self, parent, font_config):
        """Recursively update font for all widgets in the top menu area."""
        for child in parent.winfo_children():
            if isinstance(child, (ttk.Label, ttk.Button)):
                try:
                    child.configure(font=font_config)
                except tk.TclError:
                    # Some ttk widgets might not support font configuration
                    pass
            elif isinstance(child, ttk.Frame):
                self._update_widget_fonts_recursive(child, font_config)
    
    def _apply_initial_font_size(self):
        """Apply the initial font size to all components."""
        new_size = self.font_sizes[self.current_font_size_index]
        current_font_size = GridSettings.get_size_config(new_size)['font'][1]
        font_config = (THEME["font_family"], current_font_size)
        
        # Update top menu fonts
        self._update_top_menu_fonts(font_config)
        
        # Update tier panel fonts
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