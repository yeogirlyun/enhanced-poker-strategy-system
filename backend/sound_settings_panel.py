#!/usr/bin/env python3
"""
Sound Settings Panel for Enhanced Sound System

Provides a GUI panel for controlling the enhanced sound system with:
- Master volume control
- Category-specific volume controls
- Sound enable/disable toggle
- Sound quality indicators
"""

import tkinter as tk
from tkinter import ttk
from enhanced_sound_manager import sound_manager, SoundCategory
from gui_models import THEME

class SoundSettingsPanel:
    """Panel for controlling the enhanced sound system."""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.sound_manager = sound_manager
        self._setup_ui()
        self._update_displays()
    
    def _setup_ui(self):
        """Set up the sound settings UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(
            self.parent,
            text="🎵 Sound Settings",
            style="Dark.TLabelframe"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sound enable/disable
        enable_frame = ttk.Frame(self.main_frame)
        enable_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sound_enabled_var = tk.BooleanVar(value=self.sound_manager.sound_enabled)
        self.sound_checkbox = ttk.Checkbutton(
            enable_frame,
            text="Enable Sound Effects",
            variable=self.sound_enabled_var,
            command=self._toggle_sound,
            style="Dark.TCheckbutton"
        )
        self.sound_checkbox.pack(anchor=tk.W)
        
        # Master volume
        master_frame = ttk.LabelFrame(self.main_frame, text="Master Volume", padding=10)
        master_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.master_volume_var = tk.DoubleVar(value=self.sound_manager.master_volume)
        self.master_volume_scale = ttk.Scale(
            master_frame,
            from_=0.0,
            to=1.0,
            variable=self.master_volume_var,
            orient=tk.HORIZONTAL,
            command=self._update_master_volume
        )
        self.master_volume_scale.pack(fill=tk.X, pady=5)
        
        self.master_volume_label = ttk.Label(
            master_frame,
            text=f"Volume: {int(self.sound_manager.master_volume * 100)}%",
            style="Dark.TLabel"
        )
        self.master_volume_label.pack()
        
        # Category volumes
        category_frame = ttk.LabelFrame(self.main_frame, text="Category Volumes", padding=10)
        category_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.category_scales = {}
        self.category_labels = {}
        
        for category in SoundCategory:
            cat_frame = ttk.Frame(category_frame)
            cat_frame.pack(fill=tk.X, pady=2)
            
            # Category label
            ttk.Label(
                cat_frame,
                text=f"{category.value.title()}:",
                width=12,
                style="Dark.TLabel"
            ).pack(side=tk.LEFT)
            
            # Volume scale
            volume_var = tk.DoubleVar(value=self.sound_manager.category_volumes.get(category, 1.0))
            scale = ttk.Scale(
                cat_frame,
                from_=0.0,
                to=1.0,
                variable=volume_var,
                orient=tk.HORIZONTAL,
                command=lambda val, cat=category: self._update_category_volume(cat, val)
            )
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Volume label
            label = ttk.Label(
                cat_frame,
                text=f"{int(volume_var.get() * 100)}%",
                width=5,
                style="Dark.TLabel"
            )
            label.pack(side=tk.RIGHT)
            
            self.category_scales[category] = scale
            self.category_labels[category] = label
        
        # Sound quality info
        info_frame = ttk.LabelFrame(self.main_frame, text="Sound System Info", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(
            info_frame,
            height=6,
            bg=THEME["bg_dark"],
            fg=THEME["fg"],
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Test sounds button
        test_frame = ttk.Frame(self.main_frame)
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            test_frame,
            text="🎵 Test Sounds",
            command=self._test_sounds,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            test_frame,
            text="🔄 Reset to Defaults",
            command=self._reset_to_defaults,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def _toggle_sound(self):
        """Toggle sound on/off."""
        if self.sound_enabled_var.get():
            self.sound_manager.enable_sound()
        else:
            self.sound_manager.disable_sound()
        self._update_displays()
    
    def _update_master_volume(self, value):
        """Update master volume."""
        volume = float(value)
        self.sound_manager.set_master_volume(volume)
        self.master_volume_label.config(text=f"Volume: {int(volume * 100)}%")
        self._update_displays()
    
    def _update_category_volume(self, category: SoundCategory, value):
        """Update category volume."""
        volume = float(value)
        self.sound_manager.set_category_volume(category, volume)
        self.category_labels[category].config(text=f"{int(volume * 100)}%")
        self._update_displays()
    
    def _test_sounds(self):
        """Play test sounds for each category."""
        # Test UI sounds
        self.sound_manager.play("button_click")
        
        # Test game sounds
        self.sound_manager.play("chip_bet")
        
        # Test layered sounds
        self.sound_manager.play_layered_sound("big_win")
    
    def _reset_to_defaults(self):
        """Reset all sound settings to defaults."""
        # Reset master volume
        self.sound_manager.set_master_volume(0.8)
        self.master_volume_var.set(0.8)
        self.master_volume_scale.set(0.8)
        
        # Reset category volumes
        default_volumes = {
            SoundCategory.UI: 0.9,
            SoundCategory.GAME: 1.0,
            SoundCategory.AMBIENT: 0.6,
            SoundCategory.VOICE: 0.8,
            SoundCategory.MUSIC: 0.5
        }
        
        for category, volume in default_volumes.items():
            self.sound_manager.set_category_volume(category, volume)
            if category in self.category_scales:
                self.category_scales[category].set(volume)
                self.category_labels[category].config(text=f"{int(volume * 100)}%")
        
        # Enable sound
        self.sound_manager.enable_sound()
        self.sound_enabled_var.set(True)
        
        self._update_displays()
    
    def _update_displays(self):
        """Update all display elements."""
        # Update master volume display
        master_vol = self.sound_manager.master_volume
        self.master_volume_label.config(text=f"Volume: {int(master_vol * 100)}%")
        
        # Update category volume displays
        for category, label in self.category_labels.items():
            vol = self.sound_manager.category_volumes.get(category, 1.0)
            label.config(text=f"{int(vol * 100)}%")
        
        # Update info text
        self._update_info_text()
    
    def _update_info_text(self):
        """Update the sound system info display."""
        report = self.sound_manager.get_sound_quality_report()
        
        info_text = f"""Sound System Status:
• Total Sounds: {report['total_sounds']}
• Categories: {report['categories']}
• Layered Sounds: {report['layered_sounds']}
• Sound Enabled: {'Yes' if report['sound_enabled'] else 'No'}
• Pygame Available: {'Yes' if report['pygame_available'] else 'No'}
• Master Volume: {int(report['master_volume'] * 100)}%

Premium Features:
• {chr(10).join('• ' + feature for feature in report['premium_features'])}"""
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def update_font_size(self, font_size: int):
        """Update font sizes for all components."""
        font_config = (THEME["font_family"], font_size)
        monospace_font = ("Consolas", font_size)
        
        # Update labels
        self.master_volume_label.configure(font=font_config)
        for label in self.category_labels.values():
            label.configure(font=font_config)
        
        # Update info text
        self.info_text.configure(font=monospace_font)
        
        # Update checkbutton
        try:
            self.sound_checkbox.configure(font=font_config)
        except tk.TclError:
            pass  # ttk widgets don't support direct font configuration 