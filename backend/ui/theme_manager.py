"""
Theme Manager UI for live editing of poker themes.
Supports color picking, HSL nudging, preview, and save/import/export.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import colorsys
import copy
import json
import pathlib
from typing import Dict, Any, Optional, Callable

from .services.theme_loader_consolidated import (
    get_consolidated_theme_loader,
    load_themes,
    save_themes
)


def hex_to_rgbf(hex_color: str) -> tuple[float, float, float]:
    """Convert hex color to RGB float tuple (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def rgbf_to_hex(rgb: tuple[float, float, float]) -> str:
    """Convert RGB float tuple to hex color."""
    return '#%02X%02X%02X' % tuple(int(max(0, min(1, x)) * 255) for x in rgb)


def apply_hsl_nudge(hex_color: str, dh: float = 0.0, ds: float = 0.0, dl: float = 0.0) -> str:
    """
    Apply HSL nudges to a hex color.
    
    Args:
        hex_color: Input color in hex format
        dh: Hue delta (-0.5 to 0.5)
        ds: Saturation delta (-0.5 to 0.5) 
        dl: Lightness delta (-0.5 to 0.5)
        
    Returns:
        Modified color in hex format
    """
    try:
        r, g, b = hex_to_rgbf(hex_color)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        # Apply nudges with wrapping/clamping
        h = (h + dh) % 1.0
        s = max(0, min(1, s + ds))
        l = max(0, min(1, l + dl))
        
        R, G, B = colorsys.hls_to_rgb(h, l, s)
        return rgbf_to_hex((R, G, B))
        
    except Exception:
        # Return original color if conversion fails
        return hex_color


# Editable palette keys (all the important colors)
EDITABLE_KEYS = [
    # Core table colors
    "felt", "rail", "metal", "accent", "raise", "call", "neutral", "text",
    
    # Highlighting and selection
    "highlight", "highlight_text",
    
    # Emphasis bar colors  
    "emphasis_bg_top", "emphasis_bg_bottom", "emphasis_border", 
    "emphasis_text", "emphasis_accent_text",
    
    # Chip styling
    "chip_face", "chip_edge", "chip_rim", "chip_text",
    
    # Bet chip styling
    "bet_face", "bet_edge", "bet_rim", "bet_text", "bet_glow",
    
    # Pot chip styling
    "pot_face", "pot_edge", "pot_rim", "pot_text", "pot_glow"
]


class ThemeManager(tk.Toplevel):
    """Advanced Theme Manager with live preview and HSL nudging."""
    
    def __init__(self, master, on_theme_change: Optional[Callable] = None):
        """
        Initialize Theme Manager.
        
        Args:
            master: Parent window
            on_theme_change: Callback when theme is saved/changed
        """
        super().__init__(master)
        self.title("🎨 Theme Manager - Poker Pro Trainer")
        self.geometry("900x700")
        
        self.on_theme_change = on_theme_change
        
        # Load theme configuration (uses existing poker_themes.json as default)
        self.theme_loader = get_consolidated_theme_loader()
        self.config = self.theme_loader.load_themes()
        self.themes = self.config["themes"]
        self.current_index = 0
        self.working_theme = copy.deepcopy(self.themes[self.current_index])
        
        # HSL nudge values
        self.hue_var = tk.DoubleVar(value=0.0)
        self.sat_var = tk.DoubleVar(value=0.0) 
        self.light_var = tk.DoubleVar(value=0.0)
        
        # Setup UI
        self._create_ui()
        self._refresh_fields()
        
        # Make window modal
        self.transient(master)
        self.grab_set()
        
        # Center on parent
        self.geometry("+%d+%d" % (master.winfo_rootx() + 50, master.winfo_rooty() + 50))
        
    def _create_ui(self):
        """Create the Theme Manager UI."""
        # Main layout: left panel (themes) | right panel (editor)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Left panel - Theme list
        self._create_theme_list_panel()
        
        # Right panel - Editor
        self._create_editor_panel()
        
    def _create_theme_list_panel(self):
        """Create the theme list panel."""
        left_frame = ttk.LabelFrame(self, text="🎨 Available Themes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_frame.rowconfigure(0, weight=1)
        
        # Theme listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.theme_listbox = tk.Listbox(list_frame, width=25, font=("Inter", 11))
        self.theme_listbox.grid(row=0, column=0, sticky="nsew")
        self.theme_listbox.bind("<<ListboxSelect>>", self._on_theme_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.theme_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.theme_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate theme list
        for theme in self.themes:
            self.theme_listbox.insert(tk.END, theme["name"])
            
        # Select first theme
        self.theme_listbox.selection_set(0)
        
        # Theme info
        info_frame = ttk.LabelFrame(left_frame, text="Theme Info", padding=5)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info_frame.columnconfigure(0, weight=1)
        
        self.theme_intro_text = tk.Text(info_frame, height=4, wrap=tk.WORD, 
                                       font=("Georgia", 10), state="disabled")
        self.theme_intro_text.grid(row=0, column=0, sticky="ew")
        
    def _create_editor_panel(self):
        """Create the theme editor panel."""
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Theme name and basic info
        info_frame = ttk.LabelFrame(right_frame, text="Theme Details", padding=10)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(info_frame, text="ID:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        self.id_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.id_var).grid(row=1, column=1, sticky="ew", pady=(5, 0))
        
        # Color editor in scrollable frame
        canvas_frame = ttk.LabelFrame(right_frame, text="Color Palette", padding=5)
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Create scrollable canvas for color entries
        canvas = tk.Canvas(canvas_frame, height=300)
        scrollbar_v = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        
        canvas.configure(yscrollcommand=scrollbar_v.set)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Color entries
        self.color_entries = {}
        scrollable_frame.columnconfigure(1, weight=1)
        
        for i, key in enumerate(EDITABLE_KEYS):
            # Label
            ttk.Label(scrollable_frame, text=key.replace("_", " ").title() + ":").grid(
                row=i, column=0, sticky="w", padx=(5, 10), pady=2
            )
            
            # Color entry
            entry = ttk.Entry(scrollable_frame, width=10)
            entry.grid(row=i, column=1, sticky="ew", padx=(0, 5), pady=2)
            entry.bind("<KeyRelease>", lambda e, k=key: self._on_color_change(k))
            
            # Color picker button
            color_btn = tk.Button(scrollable_frame, text="🎨", width=3,
                                command=lambda k=key: self._pick_color(k))
            color_btn.grid(row=i, column=2, padx=(5, 5), pady=2)
            
            # Color preview
            preview = tk.Label(scrollable_frame, text="  ", width=4, relief="solid", borderwidth=1)
            preview.grid(row=i, column=3, padx=(0, 5), pady=2)
            
            self.color_entries[key] = {
                "entry": entry,
                "button": color_btn,
                "preview": preview
            }
        
        # Update scroll region when frame changes
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update canvas window width to match canvas
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
            
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # HSL nudge controls
        hsl_frame = ttk.LabelFrame(right_frame, text="Global HSL Adjustments", padding=10)
        hsl_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        hsl_frame.columnconfigure(1, weight=1)
        
        # Hue slider
        ttk.Label(hsl_frame, text="Hue:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        hue_scale = ttk.Scale(hsl_frame, from_=-0.5, to=0.5, orient="horizontal", 
                             variable=self.hue_var, length=200)
        hue_scale.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(hsl_frame, textvariable=self.hue_var).grid(row=0, column=2)
        
        # Saturation slider  
        ttk.Label(hsl_frame, text="Saturation:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        sat_scale = ttk.Scale(hsl_frame, from_=-0.5, to=0.5, orient="horizontal",
                             variable=self.sat_var, length=200)
        sat_scale.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(5, 0))
        ttk.Label(hsl_frame, textvariable=self.sat_var).grid(row=1, column=2, pady=(5, 0))
        
        # Lightness slider
        ttk.Label(hsl_frame, text="Lightness:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        light_scale = ttk.Scale(hsl_frame, from_=-0.5, to=0.5, orient="horizontal",
                               variable=self.light_var, length=200)
        light_scale.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(5, 0))
        ttk.Label(hsl_frame, textvariable=self.light_var).grid(row=2, column=2, pady=(5, 0))
        
        # Apply HSL button
        ttk.Button(hsl_frame, text="Apply HSL to All Colors", 
                  command=self._apply_hsl_to_palette).grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(action_frame, text="💾 Save", command=self._save_theme).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="💾 Save As...", command=self._save_as_theme).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🔄 Reset", command=self._reset_theme).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="📤 Export...", command=self._export_themes).pack(side="right", padx=(5, 0))
        ttk.Button(action_frame, text="📥 Import...", command=self._import_themes).pack(side="right", padx=5)
        
    def _on_theme_select(self, event=None):
        """Handle theme selection from list."""
        selection = self.theme_listbox.curselection()
        if not selection:
            return
            
        self.current_index = selection[0]
        self.working_theme = copy.deepcopy(self.themes[self.current_index])
        self._refresh_fields()
        
    def _refresh_fields(self):
        """Refresh all UI fields with current theme data."""
        theme = self.working_theme
        
        # Update theme info
        self.name_var.set(theme.get("name", ""))
        self.id_var.set(theme.get("id", ""))
        
        # Update theme intro text
        intro = theme.get("intro", "")
        persona = theme.get("persona", "")
        full_text = intro
        if persona:
            full_text += f"\n\n{persona}"
            
        self.theme_intro_text.config(state="normal")
        self.theme_intro_text.delete(1.0, tk.END)
        self.theme_intro_text.insert(1.0, full_text)
        self.theme_intro_text.config(state="disabled")
        
        # Update color fields
        palette = theme.get("palette", {})
        for key, widgets in self.color_entries.items():
            color = palette.get(key, "#FFFFFF")
            widgets["entry"].delete(0, tk.END)
            widgets["entry"].insert(0, color)
            
            # Update color preview
            try:
                widgets["preview"].config(bg=color)
                # Set text color for contrast
                r, g, b = hex_to_rgbf(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                text_color = "#000000" if brightness > 0.5 else "#FFFFFF"
                widgets["preview"].config(fg=text_color)
            except Exception:
                widgets["preview"].config(bg="#FFFFFF", fg="#000000")
                
        # Reset HSL sliders
        self.hue_var.set(0.0)
        self.sat_var.set(0.0)
        self.light_var.set(0.0)
        
    def _on_color_change(self, key: str):
        """Handle color entry change."""
        entry = self.color_entries[key]["entry"]
        color = entry.get()
        
        # Update working theme
        if "palette" not in self.working_theme:
            self.working_theme["palette"] = {}
        self.working_theme["palette"][key] = color
        
        # Update preview
        self._update_color_preview(key, color)
        
    def _update_color_preview(self, key: str, color: str):
        """Update color preview for a key."""
        try:
            preview = self.color_entries[key]["preview"]
            preview.config(bg=color)
            
            # Set text color for contrast
            r, g, b = hex_to_rgbf(color)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "#000000" if brightness > 0.5 else "#FFFFFF"
            preview.config(fg=text_color)
        except Exception:
            pass
            
    def _pick_color(self, key: str):
        """Open color picker for a key."""
        current_color = self.color_entries[key]["entry"].get()
        
        # Open color chooser
        rgb, hex_color = colorchooser.askcolor(
            color=current_color,
            title=f"Pick color for {key.replace('_', ' ').title()}"
        )
        
        if hex_color:
            # Update entry and working theme
            self.color_entries[key]["entry"].delete(0, tk.END)
            self.color_entries[key]["entry"].insert(0, hex_color.upper())
            
            if "palette" not in self.working_theme:
                self.working_theme["palette"] = {}
            self.working_theme["palette"][key] = hex_color.upper()
            
            # Update preview
            self._update_color_preview(key, hex_color)
            
    def _apply_hsl_to_palette(self):
        """Apply HSL nudges to all palette colors."""
        dh = self.hue_var.get()
        ds = self.sat_var.get() 
        dl = self.light_var.get()
        
        palette = self.working_theme.get("palette", {})
        
        for key in EDITABLE_KEYS:
            current_color = palette.get(key, "#FFFFFF")
            if current_color.startswith("#"):
                new_color = apply_hsl_nudge(current_color, dh, ds, dl)
                palette[key] = new_color
                
                # Update UI
                self.color_entries[key]["entry"].delete(0, tk.END)
                self.color_entries[key]["entry"].insert(0, new_color)
                self._update_color_preview(key, new_color)
                
        # Reset sliders
        self.hue_var.set(0.0)
        self.sat_var.set(0.0)
        self.light_var.set(0.0)
        
    def _save_theme(self):
        """Save current theme changes."""
        # Update theme with current field values
        self.working_theme["name"] = self.name_var.get()
        self.working_theme["id"] = self.id_var.get()
        
        # Update palette from entries
        if "palette" not in self.working_theme:
            self.working_theme["palette"] = {}
            
        for key, widgets in self.color_entries.items():
            self.working_theme["palette"][key] = widgets["entry"].get()
            
        # Update themes list
        self.themes[self.current_index] = self.working_theme
        
        # Save to current file (or default)
        if self.theme_loader.save_themes(self.config):
            current_file = self.theme_loader.get_current_file()
            file_name = current_file.name if current_file else "default themes"
            messagebox.showinfo("Theme Manager", f"Theme saved to {file_name}!")
            
            # Notify parent of theme change
            if self.on_theme_change:
                self.on_theme_change()
        else:
            messagebox.showerror("Theme Manager", "Failed to save theme.")
            
    def _save_as_theme(self):
        """Save as new theme."""
        name = self._prompt_for_text("New Theme Name", "Enter name for new theme:")
        if not name:
            return
            
        # Create new theme
        new_theme = copy.deepcopy(self.working_theme)
        new_theme["name"] = name
        new_theme["id"] = name.lower().replace(" ", "-").replace("_", "-")
        
        # Update palette from entries
        if "palette" not in new_theme:
            new_theme["palette"] = {}
            
        for key, widgets in self.color_entries.items():
            new_theme["palette"][key] = widgets["entry"].get()
            
        # Add to themes list
        self.themes.append(new_theme)
        self.theme_listbox.insert(tk.END, name)
        
        # Select new theme
        self.theme_listbox.selection_clear(0, tk.END)
        self.theme_listbox.selection_set(tk.END)
        self.current_index = len(self.themes) - 1
        
        # Save to current file
        if self.theme_loader.save_themes(self.config):
            messagebox.showinfo("Theme Manager", f"New theme '{name}' created successfully!")
        else:
            messagebox.showerror("Theme Manager", "Failed to save new theme.")
            
    def _reset_theme(self):
        """Reset theme to original state."""
        if messagebox.askyesno("Reset Theme", "Reset theme to original state? This will lose any unsaved changes."):
            # Reload from current file
            self.config = self.theme_loader.reload()
            self.themes = self.config["themes"]
            
            # Reset to current theme
            if self.current_index < len(self.themes):
                self.working_theme = copy.deepcopy(self.themes[self.current_index])
                self._refresh_fields()
            
    def _export_themes(self):
        """Export themes to JSON file."""
        current_file = self.theme_loader.get_current_file()
        initial_name = current_file.stem if current_file else "poker_themes"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialvalue=f"{initial_name}_export.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Themes"
        )
        
        if filename:
            if self.theme_loader.save_to_file(self.config, filename):
                messagebox.showinfo("Theme Manager", f"Themes exported to {filename}")
            else:
                messagebox.showerror("Theme Manager", "Export failed")
                
    def _import_themes(self):
        """Import themes from JSON file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Theme File"
        )
        
        if filename:
            try:
                # Load themes from selected file
                imported_config = self.theme_loader.load_from_file(filename)
                    
                # Validate structure
                if "themes" not in imported_config:
                    messagebox.showerror("Theme Manager", "Invalid theme file: missing 'themes' key")
                    return
                    
                # Replace current config
                self.config = imported_config
                self.themes = self.config["themes"]
                
                # Refresh theme list
                self.theme_listbox.delete(0, tk.END)
                for theme in self.themes:
                    self.theme_listbox.insert(tk.END, theme.get("name", "Unknown"))
                    
                # Select first theme
                if self.themes:
                    self.theme_listbox.selection_set(0)
                    self.current_index = 0
                    self.working_theme = copy.deepcopy(self.themes[0])
                    self._refresh_fields()
                
                file_name = pathlib.Path(filename).name    
                messagebox.showinfo("Theme Manager", f"Loaded {len(self.themes)} themes from {file_name}")
                
            except Exception as e:
                messagebox.showerror("Theme Manager", f"Failed to load theme file: {e}")
                
    def _prompt_for_text(self, title: str, prompt: str) -> Optional[str]:
        """Show a simple text input dialog."""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center on parent
        dialog.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width() // 2 - 150,
            self.winfo_rooty() + self.winfo_height() // 2 - 75
        ))
        
        result = {"value": None}
        
        # Prompt label
        ttk.Label(dialog, text=prompt).pack(pady=10)
        
        # Entry field
        entry_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=entry_var, width=30)
        entry.pack(pady=5)
        entry.focus_set()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def on_ok():
            result["value"] = entry_var.get().strip()
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
            
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)
        
        # Bind Enter key
        entry.bind("<Return>", lambda e: on_ok())
        
        # Wait for dialog to close
        self.wait_window(dialog)
        
        return result["value"] if result["value"] else None
