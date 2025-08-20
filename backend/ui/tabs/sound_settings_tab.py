"""
Sound Settings Editor Tab - Advanced sound customization interface.
Provides sound file selection, volume control, and sound management for all poker events.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class SoundSettingsTab(ttk.Frame):
    """Advanced sound settings editor with file selection and preview capabilities."""
    
    def __init__(self, parent, services):
        super().__init__(parent)
        self.services = services
        
        # Sound configuration structure
        self.sound_categories = {
            "Player Actions": [
                "BET", "RAISE", "CALL", "CHECK", "FOLD", "ALL_IN"
            ],
            "Card Dealing": [
                "DEAL_HOLE", "DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"
            ],
            "Game Events": [
                "SHOWDOWN", "END_HAND", "HAND_START", "ROUND_START", "ROUND_END"
            ],
            "Blinds & Chips": [
                "POST_BLIND", "POST_SMALL_BLIND", "POST_BIG_BLIND",
                "CHIP_BET", "CHIP_COLLECT", "POT_RAKE", "POT_SPLIT"
            ],
            "UI & Notifications": [
                "TURN_NOTIFY", "BUTTON_MOVE", "ACTION_TIMEOUT"
            ]
        }
        
        # Current editing state
        self.current_config = {}
        self.original_config = {}
        self.sound_widgets: Dict[str, Dict[str, tk.Widget]] = {}
        
        # Configuration file path
        self.config_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'sounds', 'poker_sound_config.json'
        )
        
        self._setup_ui()
        self._load_sound_config()
        
        # Apply sound configuration to EffectBus if available
        self._apply_sound_config_to_effect_bus()
    
    def _apply_sound_config_to_effect_bus(self):
        """Apply current sound configuration to EffectBus if available."""
        try:
            effect_bus = None
            if hasattr(self, 'services') and hasattr(self.services, 'get_app'):
                effect_bus = self.services.get_app('effect_bus')
            elif isinstance(self.services, dict) and 'effect_bus' in self.services:
                effect_bus = self.services['effect_bus']
            if effect_bus and hasattr(effect_bus, 'reload_sound_config'):
                effect_bus.reload_sound_config()
                print("✅ EffectBus sound configuration applied on init")
            else:
                print("⚠️ EffectBus not available for init or reload method missing")
        except Exception as e:
            print(f"⚠️ Error applying sound config to EffectBus: {e}")
    
    def _reload_sounds(self):
        """Manually reload sound configuration and apply to EffectBus."""
        try:
            # Reload config from file
            self._load_sound_config()
            
            # Apply to EffectBus
            self._apply_sound_config_to_effect_bus()
            
            # Update info display
            self._update_config_info()
            
            messagebox.showinfo("Success", "Sound configuration reloaded successfully!")
            print("✅ Sound configuration manually reloaded")
            
        except Exception as e:
            print(f"⚠️ Error reloading sounds: {e}")
            messagebox.showerror("Error", f"Failed to reload sounds: {e}")
    
    def _setup_ui(self):
        """Setup the sound settings editor interface."""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Left panel
        self.grid_columnconfigure(1, weight=1)  # Right panel
        
        # Left Panel - Sound Management & Controls
        self._create_left_panel()
        
        # Right Panel - Sound Configuration Editor
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create left panel with sound management and controls."""
        left_frame = ttk.LabelFrame(self, text="Sound Management", padding=16)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        
        # Sound Configuration Info
        info_frame = ttk.LabelFrame(left_frame, text="Configuration Info", padding=16)
        info_frame.pack(fill="x", pady=(0, 16))
        
        self.config_info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, 
                                       font=("Inter", 16), state="disabled")
        self.config_info_text.pack(fill="x")
        
        # Sound Controls
        controls_frame = ttk.LabelFrame(left_frame, text="Sound Controls", padding=16)
        controls_frame.pack(fill="x", pady=(0, 16))
        
        # Control buttons - inherit theme font size
        ttk.Button(controls_frame, text="Load Config", 
                  command=self._load_sound_config, 
                  style="Accent.TButton").pack(fill="x", pady=8)
        ttk.Button(controls_frame, text="Save Config", 
                  command=self._save_sound_config,
                  style="Accent.TButton").pack(fill="x", pady=8)
        ttk.Button(controls_frame, text="Reset to Defaults", 
                  command=self._reset_to_defaults,
                  style="Accent.TButton").pack(fill="x", pady=8)
        ttk.Button(controls_frame, text="Test All Sounds", 
                  command=self._test_all_sounds,
                  style="Accent.TButton").pack(fill="x", pady=8)
        ttk.Button(controls_frame, text="Reload Sounds", 
                  command=self._reload_sounds,
                  style="Accent.TButton").pack(fill="x", pady=8)
        
        # Global Sound Settings
        global_frame = ttk.LabelFrame(left_frame, text="Global Settings", padding=16)
        global_frame.pack(fill="x", pady=(0, 16))
        
        # Master volume - 18px font size per design requirements
        ttk.Label(global_frame, text="Master Volume:", 
                 font=("Inter", 18, "bold")).pack(anchor="w", pady=(0, 8))
        self.master_volume_var = tk.DoubleVar(value=1.0)
        volume_scale = ttk.Scale(global_frame, from_=0.0, to=1.0, 
                                variable=self.master_volume_var,
                                orient="horizontal", command=self._on_master_volume_change)
        volume_scale.pack(fill="x", pady=(0, 16))
        
        # Enable/disable sounds - inherit theme font size
        self.sounds_enabled_var = tk.BooleanVar(value=True)
        sounds_check = ttk.Checkbutton(global_frame, text="Enable Sounds",
                                      variable=self.sounds_enabled_var,
                                      command=self._on_sounds_enabled_change)
        sounds_check.pack(anchor="w", pady=4)
        
        # Voice announcements - inherit theme font size
        self.voice_enabled_var = tk.BooleanVar(value=True)
        voice_check = ttk.Checkbutton(global_frame, text="Enable Voice", 
                                     variable=self.voice_enabled_var,
                                     command=self._on_voice_enabled_change)
        voice_check.pack(anchor="w", pady=4)
        
        # Voice type selection
        voice_type_frame = ttk.Frame(global_frame)
        voice_type_frame.pack(fill="x", pady=(8, 0))
        
        ttk.Label(voice_type_frame, text="Voice Type:", 
                 font=("Inter", 18)).pack(side="left", padx=(0, 16))
        
        self.voice_type_var = tk.StringVar(value="announcer_female")
        voice_types = [
            ("Announcer Female", "announcer_female"),
            ("Announcer Male", "announcer_male"),
            ("Dealer Female", "dealer_female"),
            ("Dealer Male", "dealer_male"),
            ("Hostess Female", "hostess_female"),
            ("Tournament Female", "tournament_female")
        ]
        
        voice_combo = ttk.Combobox(voice_type_frame, 
                                   textvariable=self.voice_type_var,
                                   values=[name for name, _ in voice_types],
                                   state="readonly",
                                   font=("Inter", 16),
                                   width=20)
        voice_combo.pack(side="left", padx=(0, 16))
        
        # Bind the combobox to update the actual value
        def on_voice_type_change(event):
            selected_name = self.voice_type_var.get()
            for name, value in voice_types:
                if name == selected_name:
                    self.voice_type_var.set(value)
                    break
        
        voice_combo.bind('<<ComboboxSelected>>', on_voice_type_change)
        
        # Sound directory
        dir_frame = ttk.LabelFrame(left_frame, text="Sound Directory", padding=16)
        dir_frame.pack(fill="x", pady=(0, 16))
        
        self.sound_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.sound_dir_var, 
                 state="readonly", font=("Inter", 16)).pack(fill="x", pady=(0, 16))
        ttk.Button(dir_frame, text="Browse Directory", 
                  command=self._browse_sound_directory,
                  style="Accent.TButton").pack(fill="x")
    
    def _create_right_panel(self):
        """Create right panel with sound configuration editor."""
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        
        # Create scrollable canvas for sound settings
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_columnconfigure(1, weight=0)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create sound configuration sections
        self._create_sound_sections(scrollable_frame)
    
    def _create_sound_sections(self, parent):
        """Create sections for each sound category."""
        # Create two equal frames for better organization
        left_categories_frame = ttk.Frame(parent)
        left_categories_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        right_categories_frame = ttk.Frame(parent)
        right_categories_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))
        
        # Split categories between the two frames
        categories = list(self.sound_categories.items())
        mid_point = len(categories) // 2
        
        left_categories = categories[:mid_point]
        right_categories = categories[mid_point:]
        
        # Create left frame categories
        for category, events in left_categories:
            self._create_category_section(left_categories_frame, category, events)
        
        # Create right frame categories
        for category, events in right_categories:
            self._create_category_section(right_categories_frame, category, events)
    
    def _create_category_section(self, parent, category, events):
        """Create a single category section with proper 4-column layout."""
        # Category header - 20px font size per design requirements
        category_frame = ttk.LabelFrame(parent, text=category, padding=16)
        category_frame.pack(fill="x", pady=(0, 16), padx=16)
        
        # Create header row with column labels
        header_frame = ttk.Frame(category_frame)
        header_frame.pack(fill="x", pady=(0, 8))
        
        # Column headers - 20px font size
        ttk.Label(header_frame, text="Event Name", font=("Inter", 18, "bold")).pack(side="left", padx=(0, 16))
        ttk.Label(header_frame, text="Current File", font=("Inter", 18, "bold")).pack(side="left", padx=(0, 16))
        ttk.Label(header_frame, text="Browse", font=("Inter", 18, "bold")).pack(side="left", padx=(0, 16))
        ttk.Label(header_frame, text="Test", font=("Inter", 18, "bold")).pack(side="left", padx=(0, 16))
        
        # Create events using pack layout for each row
        for event in events:
            # Create a frame for each event row
            event_frame = ttk.Frame(category_frame)
            event_frame.pack(fill="x", pady=4)
            
            # Event label - 18px font size
            ttk.Label(event_frame, text=f"{event}:", 
                     font=("Inter", 18)).pack(side="left", padx=(0, 16))
            
            # Sound file entry
            sound_var = tk.StringVar()
            sound_entry = ttk.Entry(event_frame, textvariable=sound_var, 
                                   width=25, state="readonly", font=("Inter", 16))
            sound_entry.pack(side="left", padx=(0, 16))
            
            # Browse button
            browse_btn = ttk.Button(event_frame, text="Browse", 
                                   command=lambda e=event, var=sound_var: 
                                   self._browse_sound_file(e, var),
                                   style="Accent.TButton")
            browse_btn.pack(side="left", padx=(0, 16))
            
            # Test button
            test_btn = ttk.Button(event_frame, text="Test", 
                                 command=lambda e=event: self._test_sound(e),
                                 style="Accent.TButton")
            test_btn.pack(side="left", padx=(0, 16))
            
            # Store widgets for later access
            if category not in self.sound_widgets:
                self.sound_widgets[category] = {}
            self.sound_widgets[category][event] = {
                'entry': sound_entry,
                'var': sound_var,
                'browse': browse_btn,
                'test': test_btn
            }
    
    def _load_sound_config(self):
        """Load sound configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.current_config = json.load(f)
                print(f"🔊 SoundSettingsTab: Loaded config from {self.config_file}")
            else:
                # Create default configuration
                self.current_config = self._create_default_config()
                print(f"🔊 SoundSettingsTab: Created default config")
            
            # Store original for comparison
            self.original_config = self.current_config.copy()
            
            # Update UI with loaded config
            self._update_ui_from_config()
            
            # Update info display
            self._update_config_info()
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error loading config: {e}")
            messagebox.showerror("Error", f"Failed to load sound configuration: {e}")
    
    def _create_default_config(self):
        """Create default sound configuration."""
        default_config = {
            "master_volume": 1.0,
            "sounds_enabled": True,
            "voice_enabled": True,
            "voice_type": "announcer_female",
            "sound_directory": os.path.join(
                os.path.dirname(__file__), '..', '..', 'sounds'
            ),
            "sounds": {}
        }
        
        # Add default sound mappings for all events
        for category, events in self.sound_categories.items():
            for event in events:
                # Map to common sound files
                if "BET" in event or "RAISE" in event:
                    default_config["sounds"][event] = "player_bet.wav"
                elif "CALL" in event:
                    default_config["sounds"][event] = "player_call.wav"
                elif "CHECK" in event:
                    default_config["sounds"][event] = "player_check.wav"
                elif "FOLD" in event:
                    default_config["sounds"][event] = "player_fold.wav"
                elif "DEAL" in event:
                    default_config["sounds"][event] = "card_deal.wav"
                elif "SHOWDOWN" in event or "END_HAND" in event:
                    default_config["sounds"][event] = "winner_announce.wav"
                elif "BLIND" in event or "CHIP" in event:
                    default_config["sounds"][event] = "chip_bet.wav"
                else:
                    default_config["sounds"][event] = "turn_notify.wav"
        
        return default_config
    
    def _update_ui_from_config(self):
        """Update UI widgets with loaded configuration."""
        try:
            # Update global settings
            self.master_volume_var.set(self.current_config.get("master_volume", 1.0))
            self.sounds_enabled_var.set(self.current_config.get("sounds_enabled", True))
            self.voice_enabled_var.set(self.current_config.get("voice_enabled", True))
            
            # Update voice type selection
            voice_type = self.current_config.get("voice_type", "announcer_female")
            # Find the display name for the voice type
            voice_types = [
                ("Announcer Female", "announcer_female"),
                ("Announcer Male", "announcer_male"),
                ("Dealer Female", "dealer_female"),
                ("Dealer Male", "dealer_male"),
                ("Hostess Female", "hostess_female"),
                ("Tournament Female", "tournament_female")
            ]
            for display_name, value in voice_types:
                if value == voice_type:
                    self.voice_type_var.set(display_name)
                    break
            
            self.sound_dir_var.set(self.current_config.get("sound_directory", ""))
            
            # Update sound file entries
            sounds = self.current_config.get("sounds", {})
            for category, events in self.sound_categories.items():
                for event in events:
                    if event in self.sound_widgets.get(category, {}):
                        widget = self.sound_widgets[category][event]
                        sound_file = sounds.get(event, "")
                        widget['var'].set(sound_file)
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating UI: {e}")
    
    def _update_config_info(self):
        """Update configuration info display."""
        try:
            config = self.current_config
            info_text = f"Configuration: {os.path.basename(self.config_file)}\n"
            info_text += f"Sound Directory: {config.get('sound_directory', 'Not set')}\n"
            info_text += f"Total Events: {len(config.get('sounds', {}))}\n"
            info_text += f"Master Volume: {config.get('master_volume', 1.0):.1f}\n"
            info_text += f"Sounds Enabled: {config.get('sounds_enabled', True)}\n"
            info_text += f"Voice Enabled: {config.get('voice_enabled', True)}\n"
            info_text += f"Voice Type: {config.get('voice_type', 'announcer_female')}"
            
            self.config_info_text.config(state="normal")
            self.config_info_text.delete(1.0, tk.END)
            self.config_info_text.insert(1.0, info_text)
            self.config_info_text.config(state="disabled")
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating info: {e}")
    
    def _save_sound_config(self):
        """Save current sound configuration to JSON file."""
        try:
            # Update config from UI
            self._update_config_from_ui()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(self.current_config, f, indent=2)
            
            # Update original config
            self.original_config = self.current_config.copy()
            
            print(f"🔊 SoundSettingsTab: Saved config to {self.config_file}")
            
            # Reload EffectBus configuration to pick up new sounds
            try:
                from ..services.effect_bus import EffectBus
                # Get the global EffectBus instance if available
                if hasattr(self, 'services') and 'effect_bus' in self.services:
                    effect_bus = self.services['effect_bus']
                    if hasattr(effect_bus, 'reload_sound_config'):
                        effect_bus.reload_sound_config()
                        print("✅ EffectBus sound configuration reloaded")
                    else:
                        print("⚠️ EffectBus reload method not available")
                else:
                    print("⚠️ EffectBus service not available for reload")
            except Exception as e:
                print(f"⚠️ Error reloading EffectBus: {e}")
            
            messagebox.showinfo("Success", "Sound configuration saved and reloaded successfully!")
            
            # Update info display
            self._update_config_info()
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save sound configuration: {e}")
    
    def _update_config_from_ui(self):
        """Update configuration from UI widget values."""
        try:
            # Update global settings
            self.current_config["master_volume"] = self.master_volume_var.get()
            self.current_config["sounds_enabled"] = self.sounds_enabled_var.get()
            self.current_config["voice_enabled"] = self.voice_enabled_var.get()
            
            # Update voice type
            voice_type = self.voice_type_var.get()
            # Convert display name back to config value
            voice_types = [
                ("Announcer Female", "announcer_female"),
                ("Announcer Male", "announcer_male"),
                ("Dealer Female", "dealer_female"),
                ("Dealer Male", "dealer_male"),
                ("Hostess Female", "hostess_female"),
                ("Tournament Female", "tournament_female")
            ]
            for display_name, value in voice_types:
                if display_name == voice_type:
                    self.current_config["voice_type"] = value
                    break
            
            self.current_config["sound_directory"] = self.sound_dir_var.get()
            
            # Update sound mappings
            if "sounds" not in self.current_config:
                self.current_config["sounds"] = {}
            
            for category, events in self.sound_categories.items():
                for event in events:
                    if event in self.sound_widgets.get(category, {}):
                        widget = self.sound_widgets[category][event]
                        sound_file = widget['var'].get()
                        self.current_config["sounds"][event] = sound_file
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating config from UI: {e}")
    
    def _reset_to_defaults(self):
        """Reset configuration to default values."""
        try:
            if messagebox.askyesno("Reset Configuration", 
                                 "Are you sure you want to reset to default values?"):
                self.current_config = self._create_default_config()
                self._update_ui_from_config()
                self._update_config_info()
                print(f"🔊 SoundSettingsTab: Reset to defaults")
                messagebox.showinfo("Success", "Configuration reset to defaults!")
                
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error resetting config: {e}")
            messagebox.showerror("Error", f"Failed to reset configuration: {e}")
    
    def _browse_sound_directory(self):
        """Browse for sound directory."""
        try:
            directory = filedialog.askdirectory(
                title="Select Sound Directory",
                initialdir=self.sound_dir_var.get() or os.getcwd()
            )
            if directory:
                self.sound_dir_var.set(directory)
                print(f"🔊 SoundSettingsTab: Selected sound directory: {directory}")
                
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error browsing directory: {e}")
    
    def _browse_sound_file(self, event, sound_var):
        """Browse for sound file for specific event."""
        try:
            # Get current sound directory
            sound_dir = self.sound_dir_var.get()
            if not sound_dir or not os.path.exists(sound_dir):
                sound_dir = os.getcwd()
            
            # Browse for sound file
            filename = filedialog.askopenfilename(
                title=f"Select sound file for {event}",
                initialdir=sound_dir,
                filetypes=[
                    ("Sound files", "*.wav *.mp3 *.ogg"),
                    ("WAV files", "*.wav"),
                    ("MP3 files", "*.mp3"),
                    ("OGG files", "*.ogg"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                # Store relative path if in sound directory, otherwise absolute
                if sound_dir and filename.startswith(sound_dir):
                    rel_path = os.path.relpath(filename, sound_dir)
                    sound_var.set(rel_path)
                else:
                    sound_var.set(filename)
                
                print(f"🔊 SoundSettingsTab: Selected sound for {event}: {filename}")
                
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error browsing sound file: {e}")
    
    def _test_sound(self, event):
        """Test sound for specific event."""
        try:
            # Get sound file from UI
            sound_file = None
            for category, events in self.sound_categories.items():
                if event in self.sound_widgets.get(category, {}):
                    sound_file = self.sound_widgets[category][event]['var'].get()
                    break
            
            if not sound_file:
                messagebox.showwarning("Warning", f"No sound file configured for {event}")
                return
            
            # Build full path
            sound_dir = self.sound_dir_var.get()
            if sound_dir and not os.path.isabs(sound_file):
                full_path = os.path.join(sound_dir, sound_file)
            else:
                full_path = sound_file
            
            if not os.path.exists(full_path):
                messagebox.showerror("Error", f"Sound file not found: {full_path}")
                return
            
            # Test sound playback
            self._play_test_sound(full_path)
            print(f"🔊 SoundSettingsTab: Testing sound for {event}: {full_path}")
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error testing sound: {e}")
            messagebox.showerror("Error", f"Failed to test sound: {e}")
    
    def _play_test_sound(self, sound_file):
        """Play test sound file."""
        try:
            import pygame
            if pygame.mixer.get_init():
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
                print(f"🔊 SoundSettingsTab: Playing test sound: {sound_file}")
            else:
                messagebox.showwarning("Warning", "Audio system not initialized")
                
        except ImportError:
            messagebox.showwarning("Warning", "Pygame not available for sound testing")
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error playing test sound: {e}")
            messagebox.showerror("Error", f"Failed to play sound: {e}")
    
    def _test_all_sounds(self):
        """Test all configured sounds."""
        try:
            # Get all configured sounds
            sounds_to_test = []
            for category, events in self.sound_categories.items():
                for event in events:
                    if event in self.sound_widgets.get(category, {}):
                        sound_file = self.sound_widgets[category][event]['var'].get()
                        if sound_file:
                            sound_dir = self.sound_dir_var.get()
                            if sound_dir and not os.path.isabs(sound_file):
                                full_path = os.path.join(sound_dir, sound_file)
                            else:
                                full_path = sound_file
                            
                            if os.path.exists(full_path):
                                sounds_to_test.append((event, full_path))
            
            if not sounds_to_test:
                messagebox.showinfo("Info", "No sounds configured to test")
                return
            
            # Test each sound with a small delay
            self._test_sounds_sequence(sounds_to_test)
            
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error testing all sounds: {e}")
            messagebox.showerror("Error", f"Failed to test sounds: {e}")
    
    def _test_sounds_sequence(self, sounds_to_test):
        """Test sounds in sequence with delays."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                messagebox.showwarning("Warning", "Audio system not initialized")
                return
            
            # Create a simple test sequence
            test_window = tk.Toplevel(self)
            test_window.title("Testing Sounds")
            test_window.geometry("300x200")
            
            progress_label = ttk.Label(test_window, text="Testing sounds...")
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(test_window, maximum=len(sounds_to_test))
            progress_bar.pack(fill="x", padx=20, pady=10)
            
            def play_next_sound(index=0):
                if index >= len(sounds_to_test):
                    test_window.destroy()
                    messagebox.showinfo("Complete", "Sound testing completed!")
                    return
                
                event, sound_file = sounds_to_test[index]
                progress_label.config(text=f"Testing: {event}")
                progress_bar["value"] = index + 1
                
                try:
                    sound = pygame.mixer.Sound(sound_file)
                    sound.play()
                    print(f"🔊 SoundSettingsTab: Testing {event}: {sound_file}")
                except Exception as e:
                    print(f"⚠️ SoundSettingsTab: Error testing {event}: {e}")
                
                # Schedule next sound after delay
                test_window.after(1000, lambda: play_next_sound(index + 1))
            
            # Start testing
            play_next_sound()
            
        except ImportError:
            messagebox.showwarning("Warning", "Pygame not available for sound testing")
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error in sound sequence: {e}")
    
    def _on_master_volume_change(self, value):
        """Handle master volume change."""
        try:
            volume = float(value)
            self.current_config["master_volume"] = volume
            print(f"🔊 SoundSettingsTab: Master volume changed to {volume}")
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating master volume: {e}")
    
    def _on_sounds_enabled_change(self):
        """Handle sounds enabled change."""
        try:
            enabled = self.sounds_enabled_var.get()
            self.current_config["sounds_enabled"] = enabled
            print(f"🔊 SoundSettingsTab: Sounds {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating sounds enabled: {e}")
    
    def _on_voice_enabled_change(self):
        """Handle voice enabled change."""
        try:
            enabled = self.voice_enabled_var.get()
            self.current_config["voice_enabled"] = enabled
            print(f"🔊 SoundSettingsTab: Voice {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error updating voice enabled: {e}")
    
    def get_sound_config(self):
        """Get current sound configuration for external use."""
        return self.current_config.copy()
    
    def apply_sound_config(self):
        """Apply current sound configuration to EffectBus."""
        try:
            if hasattr(self.services, 'effect_bus'):
                # Update EffectBus with new configuration
                effect_bus = self.services.effect_bus
                
                # Update sound mappings
                sounds = self.current_config.get("sounds", {})
                for event, sound_file in sounds.items():
                    if hasattr(effect_bus, 'sound_mapping'):
                        effect_bus.sound_mapping[event] = sound_file
                
                # Update global settings
                if hasattr(effect_bus, 'enabled'):
                    effect_bus.enabled = self.current_config.get("sounds_enabled", True)
                
                print(f"🔊 SoundSettingsTab: Applied sound config to EffectBus")
                
        except Exception as e:
            print(f"⚠️ SoundSettingsTab: Error applying config: {e}")
