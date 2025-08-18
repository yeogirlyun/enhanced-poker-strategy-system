"""
Theme Editor Tab - Advanced theme customization interface.
Provides real-time color editing, hue adjustment, and theme management.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from typing import Dict, Any, Optional
from ui.services.advanced_theme_manager import AdvancedThemeManager


class ThemeEditorTab(ttk.Frame):
    """Advanced theme editor with real-time preview and color customization."""
    
    def __init__(self, parent, services):
        super().__init__(parent)
        self.services = services
        self.theme_manager = AdvancedThemeManager()
        
        # Current editing state
        self.current_theme_id: Optional[str] = None
        self.preview_mode = False
        self.color_widgets: Dict[str, Dict[str, tk.Widget]] = {}
        
        self._setup_ui()
        self._load_initial_theme()
    
    def _setup_ui(self):
        """Setup the theme editor interface."""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Left panel
        self.grid_columnconfigure(1, weight=1)  # Right panel
        
        # Left Panel - Theme Selection & Controls
        self._create_left_panel()
        
        # Right Panel - Color Editor
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create left panel with theme selection and management."""
        left_frame = ttk.LabelFrame(self, text="Theme Management", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        # Theme Selection
        ttk.Label(left_frame, text="Select Theme:").pack(anchor="w", pady=(0, 5))
        
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(left_frame, textvariable=self.theme_var, 
                                       state="readonly", width=30)
        self.theme_combo.pack(fill="x", pady=(0, 10))
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_select)
        
        # Theme Info Display
        info_frame = ttk.LabelFrame(left_frame, text="Theme Info", padding=5)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.theme_info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, 
                                      font=("Arial", 10), state="disabled")
        self.theme_info_text.pack(fill="x")
        
        # Theme Controls
        controls_frame = ttk.LabelFrame(left_frame, text="Theme Controls", padding=5)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Control buttons in grid
        ttk.Button(controls_frame, text="New Theme", 
                  command=self._create_new_theme).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(controls_frame, text="Duplicate", 
                  command=self._duplicate_theme).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(controls_frame, text="Save Changes", 
                  command=self._save_theme).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(controls_frame, text="Revert", 
                  command=self._revert_theme).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Global Adjustments
        global_frame = ttk.LabelFrame(left_frame, text="Global Adjustments", padding=5)
        global_frame.pack(fill="x", pady=(0, 10))
        
        # Hue adjustment
        ttk.Label(global_frame, text="Hue Shift:").pack(anchor="w")
        self.hue_var = tk.DoubleVar()
        hue_scale = ttk.Scale(global_frame, from_=-180, to=180, variable=self.hue_var,
                             orient="horizontal", command=self._on_hue_change)
        hue_scale.pack(fill="x", pady=(0, 5))
        
        # Saturation adjustment  
        ttk.Label(global_frame, text="Saturation:").pack(anchor="w")
        self.saturation_var = tk.DoubleVar()
        sat_scale = ttk.Scale(global_frame, from_=-0.5, to=0.5, variable=self.saturation_var,
                             orient="horizontal", command=self._on_saturation_change)
        sat_scale.pack(fill="x", pady=(0, 5))
        
        # Lightness adjustment
        ttk.Label(global_frame, text="Lightness:").pack(anchor="w")
        self.lightness_var = tk.DoubleVar()
        light_scale = ttk.Scale(global_frame, from_=-0.3, to=0.3, variable=self.lightness_var,
                               orient="horizontal", command=self._on_lightness_change)
        light_scale.pack(fill="x", pady=(0, 5))
        
        # Reset button
        ttk.Button(global_frame, text="Reset Adjustments", 
                  command=self._reset_adjustments).pack(fill="x", pady=(5, 0))
        
        # Import/Export
        io_frame = ttk.LabelFrame(left_frame, text="Import/Export", padding=5)
        io_frame.pack(fill="x")
        
        ttk.Button(io_frame, text="Import Theme", 
                  command=self._import_theme).pack(fill="x", pady=2)
        ttk.Button(io_frame, text="Export Theme", 
                  command=self._export_theme).pack(fill="x", pady=2)
    
    def _create_right_panel(self):
        """Create right panel with color editor."""
        right_frame = ttk.LabelFrame(self, text="Color Palette Editor", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        
        # Create scrollable frame for color controls
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.color_editor_frame = scrollable_frame
        
        # Color categories
        self._create_color_section("Core Colors", [
            ("felt", "Table Felt"),
            ("rail", "Table Rail"), 
            ("metal", "Metal Accents"),
            ("accent", "Accent Color"),
            ("raise", "Raise Color"),
            ("call", "Call Color")
        ])
        
        self._create_color_section("Text & Highlighting", [
            ("text", "Primary Text"),
            ("highlight", "Selection Highlight"),
            ("highlight_text", "Selection Text"),
            ("emphasis_text", "Emphasis Text")
        ])
        
        self._create_color_section("Emphasis Bar (Theme Intro)", [
            ("emphasis_bg_top", "Background Top"),
            ("emphasis_bg_bottom", "Background Bottom"),
            ("emphasis_border", "Border Color"),
            ("emphasis_accent_text", "Accent Text")
        ])
        
        self._create_color_section("Chips & Betting", [
            ("chip_face", "Chip Face"),
            ("bet_face", "Bet Chip Face"),
            ("pot_face", "Pot Chip Face"),
            ("neutral", "Neutral Color")
        ])
    
    def _create_color_section(self, section_name: str, color_items: list):
        """Create a section of color controls."""
        section_frame = ttk.LabelFrame(self.color_editor_frame, text=section_name, padding=5)
        section_frame.pack(fill="x", pady=5)
        
        for color_key, display_name in color_items:
            self._create_color_control(section_frame, color_key, display_name)
    
    def _create_color_control(self, parent, color_key: str, display_name: str):
        """Create a color control widget."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", pady=2)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Color preview box
        color_box = tk.Frame(control_frame, width=30, height=20, relief="solid", bd=1)
        color_box.grid(row=0, column=0, padx=(0, 5))
        
        # Color label
        ttk.Label(control_frame, text=display_name).grid(row=0, column=1, sticky="w")
        
        # Color value entry
        color_var = tk.StringVar()
        color_entry = ttk.Entry(control_frame, textvariable=color_var, width=10)
        color_entry.grid(row=0, column=2, padx=5)
        color_entry.bind("<Return>", lambda e: self._on_color_entry_change(color_key, color_var.get()))
        
        # Color picker button
        ttk.Button(control_frame, text="Pick", width=6,
                  command=lambda: self._pick_color(color_key)).grid(row=0, column=3, padx=(5, 0))
        
        # Contrast info (for text colors)
        if "text" in color_key.lower():
            contrast_label = ttk.Label(control_frame, text="", font=("Arial", 8))
            contrast_label.grid(row=0, column=4, padx=(10, 0))
            
            # Store references
            if color_key not in self.color_widgets:
                self.color_widgets[color_key] = {}
            self.color_widgets[color_key]["contrast_label"] = contrast_label
        
        # Store widget references
        if color_key not in self.color_widgets:
            self.color_widgets[color_key] = {}
        self.color_widgets[color_key].update({
            "color_box": color_box,
            "color_var": color_var,
            "color_entry": color_entry
        })
    
    def _load_initial_theme(self):
        """Load initial theme data."""
        theme_names = self.theme_manager.get_theme_names()
        self.theme_combo['values'] = theme_names
        
        if theme_names:
            self.theme_var.set(theme_names[0])
            self._on_theme_select()
    
    def _on_theme_select(self, event=None):
        """Handle theme selection."""
        theme_name = self.theme_var.get()
        theme = self.theme_manager.get_theme_by_name(theme_name)
        
        if theme:
            self.current_theme_id = theme['id']
            self._update_theme_info(theme)
            self._update_color_controls(theme['palette'])
            self._reset_adjustments()
    
    def _update_theme_info(self, theme: Dict[str, Any]):
        """Update theme information display."""
        self.theme_info_text.config(state="normal")
        self.theme_info_text.delete(1.0, tk.END)
        
        info_text = f"ID: {theme['id']}\\n"
        info_text += f"Intro: {theme.get('intro', 'No description')}\\n"
        info_text += f"Persona: {theme.get('persona', 'Unknown')}"
        
        self.theme_info_text.insert(1.0, info_text)
        self.theme_info_text.config(state="disabled")
    
    def _update_color_controls(self, palette: Dict[str, str]):
        """Update all color control widgets with palette values."""
        for color_key, widgets in self.color_widgets.items():
            color_value = palette.get(color_key, "#000000")
            
            # Update color box
            widgets["color_box"].config(bg=color_value)
            
            # Update entry
            widgets["color_var"].set(color_value)
            
            # Update contrast info if applicable
            if "contrast_label" in widgets:
                self._update_contrast_info(color_key, palette)
    
    def _update_contrast_info(self, text_color_key: str, palette: Dict[str, str]):
        """Update contrast information for text colors."""
        if text_color_key not in self.color_widgets:
            return
        
        widgets = self.color_widgets[text_color_key]
        if "contrast_label" not in widgets:
            return
        
        text_color = palette.get(text_color_key, "#FFFFFF")
        
        # Determine appropriate background color for contrast check
        bg_color = "#000000"  # Default
        if "emphasis" in text_color_key:
            bg_color = palette.get("emphasis_bg_top", palette.get("felt", "#000000"))
        elif text_color_key == "text":
            bg_color = palette.get("felt", "#000000")
        elif text_color_key == "highlight_text":
            bg_color = palette.get("highlight", "#000000")
        
        ratio = self.theme_manager.calculate_contrast_ratio(bg_color, text_color)
        
        # Format contrast info
        if ratio >= 7.0:
            status = "AAA"
            color = "green"
        elif ratio >= 4.5:
            status = "AA"
            color = "orange"
        else:
            status = "FAIL"
            color = "red"
        
        widgets["contrast_label"].config(
            text=f"{ratio:.1f}:1 ({status})",
            foreground=color
        )
    
    def _pick_color(self, color_key: str):
        """Open color picker for a specific color."""
        if not self.current_theme_id:
            return
        
        current_color = self.color_widgets[color_key]["color_var"].get()
        
        # Open color chooser
        color_result = colorchooser.askcolor(
            color=current_color,
            title=f"Choose {color_key.replace('_', ' ').title()} Color"
        )
        
        if color_result[1]:  # User selected a color
            new_color = color_result[1].upper()
            self._update_color(color_key, new_color)
    
    def _on_color_entry_change(self, color_key: str, new_color: str):
        """Handle manual color entry changes."""
        if new_color.startswith('#') and len(new_color) == 7:
            self._update_color(color_key, new_color.upper())
    
    def _update_color(self, color_key: str, new_color: str):
        """Update a color and refresh the UI."""
        if not self.current_theme_id:
            return
        
        # Update in theme manager
        self.theme_manager.update_color(self.current_theme_id, color_key, new_color)
        
        # Update UI widgets
        widgets = self.color_widgets[color_key]
        widgets["color_box"].config(bg=new_color)
        widgets["color_var"].set(new_color)
        
        # Update contrast info if applicable
        if "contrast_label" in widgets:
            palette = self.theme_manager.get_palette(self.current_theme_id)
            self._update_contrast_info(color_key, palette)
        
        # Trigger live preview if enabled
        if self.preview_mode:
            self._apply_preview()
    
    def _on_hue_change(self, value):
        """Handle global hue adjustment."""
        if not self.current_theme_id or not self.preview_mode:
            return
        
        hue_shift = float(value)
        self.theme_manager.adjust_hue(self.current_theme_id, hue_shift)
        self._refresh_all_color_controls()
    
    def _on_saturation_change(self, value):
        """Handle global saturation adjustment."""
        if not self.current_theme_id or not self.preview_mode:
            return
        
        sat_delta = float(value)
        self.theme_manager.adjust_saturation(self.current_theme_id, sat_delta)
        self._refresh_all_color_controls()
    
    def _on_lightness_change(self, value):
        """Handle global lightness adjustment."""
        if not self.current_theme_id or not self.preview_mode:
            return
        
        light_delta = float(value)
        self.theme_manager.adjust_lightness(self.current_theme_id, light_delta)
        self._refresh_all_color_controls()
    
    def _refresh_all_color_controls(self):
        """Refresh all color control widgets after global adjustments."""
        if self.current_theme_id:
            palette = self.theme_manager.get_palette(self.current_theme_id)
            self._update_color_controls(palette)
    
    def _reset_adjustments(self):
        """Reset global adjustment sliders."""
        self.hue_var.set(0)
        self.saturation_var.set(0)
        self.lightness_var.set(0)
    
    def _create_new_theme(self):
        """Create a new custom theme."""
        dialog = ThemeNameDialog(self, "Create New Theme")
        if dialog.result:
            name = dialog.result
            base_theme_id = self.current_theme_id
            
            new_theme_id = self.theme_manager.create_theme(name, base_theme_id)
            
            # Refresh theme list and select new theme
            self._refresh_theme_list()
            
            # Find and select the new theme
            theme_names = self.theme_manager.get_theme_names()
            for theme_name in theme_names:
                theme = self.theme_manager.get_theme_by_name(theme_name)
                if theme and theme['id'] == new_theme_id:
                    self.theme_var.set(theme_name)
                    self._on_theme_select()
                    break
    
    def _duplicate_theme(self):
        """Duplicate the current theme."""
        if not self.current_theme_id:
            return
        
        current_theme = self.theme_manager.get_theme_by_id(self.current_theme_id)
        if not current_theme:
            return
        
        dialog = ThemeNameDialog(self, f"Duplicate '{current_theme['name']}'")
        if dialog.result:
            name = dialog.result
            new_theme_id = self.theme_manager.duplicate_theme(self.current_theme_id, name)
            
            if new_theme_id:
                self._refresh_theme_list()
                # Select the new duplicated theme
                theme_names = self.theme_manager.get_theme_names()
                for theme_name in theme_names:
                    theme = self.theme_manager.get_theme_by_name(theme_name)
                    if theme and theme['id'] == new_theme_id:
                        self.theme_var.set(theme_name)
                        self._on_theme_select()
                        break
    
    def _save_theme(self):
        """Save current theme changes."""
        if not self.current_theme_id:
            return
        
        if self.theme_manager.save_theme(self.current_theme_id):
            messagebox.showinfo("Success", f"Theme saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save theme.")
    
    def _revert_theme(self):
        """Revert current theme to saved state."""
        if not self.current_theme_id:
            return
        
        if self.theme_manager.has_unsaved_changes(self.current_theme_id):
            result = messagebox.askyesno("Revert Changes", 
                                       "Are you sure you want to revert all unsaved changes?")
            if result:
                self.theme_manager.revert_changes(self.current_theme_id)
                self._on_theme_select()  # Refresh display
        else:
            messagebox.showinfo("No Changes", "No unsaved changes to revert.")
    
    def _import_theme(self):
        """Import theme from file."""
        file_path = filedialog.askopenfilename(
            title="Import Theme File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            imported_ids = self.theme_manager.import_theme(file_path)
            if imported_ids:
                self._refresh_theme_list()
                messagebox.showinfo("Success", f"Imported {len(imported_ids)} theme(s)!")
            else:
                messagebox.showerror("Error", "Failed to import theme file.")
    
    def _export_theme(self):
        """Export current theme to file."""
        if not self.current_theme_id:
            return
        
        current_theme = self.theme_manager.get_theme_by_id(self.current_theme_id)
        if not current_theme:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Theme",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialvalue=f"{current_theme['name'].replace(' ', '_')}.json"
        )
        
        if file_path:
            if self.theme_manager.export_theme(self.current_theme_id, file_path):
                messagebox.showinfo("Success", "Theme exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export theme.")
    
    def _refresh_theme_list(self):
        """Refresh the theme selection combobox."""
        theme_names = self.theme_manager.get_theme_names()
        self.theme_combo['values'] = theme_names
    
    def _apply_preview(self):
        """Apply current theme as preview (if preview mode is enabled)."""
        # This would integrate with the main theme system
        # For now, just update the display
        pass


class ThemeNameDialog:
    """Simple dialog for entering theme names."""
    
    def __init__(self, parent, title: str):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create UI
        ttk.Label(self.dialog, text="Theme Name:").pack(pady=10)
        
        self.name_var = tk.StringVar()
        entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side="left", padx=5)
        
        # Bind Enter key
        entry.bind("<Return>", lambda e: self._ok_clicked())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        """Handle OK button click."""
        name = self.name_var.get().strip()
        if name:
            self.result = name
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()
