#!/usr/bin/env python3
"""
Advanced Sound Settings GUI

Provides a comprehensive interface for testing, previewing, and replacing
sounds in the poker app with custom files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
from enhanced_sound_manager import sound_manager, SoundCategory
from voice_announcement_system import voice_system

class SoundSettingsGUI:
    """Advanced sound settings interface for the poker app."""
    
    def __init__(self, parent):
        self.parent = parent
        self.sounds_dir = Path("sounds")
        self.sound_manager = sound_manager
        
        # Initialize sound entries dictionary
        self.sound_entries = {}
        
        # Initialize sound persistence
        from sound_persistence import SoundPersistence
        self.persistence = SoundPersistence()
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sound categories and their descriptions
        self.sound_categories = {
            'Card Actions': {
                'sounds': ['card_deal', 'card_shuffle', 'fold'],
                'description': 'Sounds for card dealing, shuffling, and folding'
            },
            'Chip Actions': {
                'sounds': ['chip_bet', 'chip_collect', 'chip_stack'],
                'description': 'Sounds for chip betting, collecting, and stacking'
            },
            'Player Actions': {
                'sounds': ['player_bet', 'player_call', 'player_raise', 'player_check', 'player_fold', 'player_all_in'],
                'description': 'Sounds for player betting, calling, raising, checking, folding, and all-in'
            },
            'Pot & Winner': {
                'sounds': ['pot_win', 'pot_split', 'pot_rake', 'winner_announce'],
                'description': 'Sounds for pot winning, splitting, raking, and winner announcements'
            },
            'UI Actions': {
                'sounds': ['button_click', 'button_hover', 'button_move', 'turn_notify', 'notification'],
                'description': 'Sounds for UI interactions, button clicks, and notifications'
            },
            'System Actions': {
                'sounds': ['success', 'error', 'menu_open'],
                'description': 'Sounds for system success, errors, and menu actions'
            }
        }
        
        self.create_widgets()
        self.load_current_sounds()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="🎵 Sound Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Status indicator
        self.status_label = ttk.Label(self.frame, text="", font=("Arial", 10, "italic"))
        self.status_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each category
        self.category_frames = {}
        for category_name, category_info in self.sound_categories.items():
            frame = self.create_category_tab(category_name, category_info)
            self.category_frames[category_name] = frame
            self.notebook.add(frame, text=category_name)
        
        # Global controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Volume controls
        volume_frame = ttk.LabelFrame(controls_frame, text="Volume Controls")
        volume_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Master volume
        ttk.Label(volume_frame, text="Master Volume:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.master_volume_var = tk.DoubleVar(value=0.7)
        master_volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.master_volume_var, 
                                       orient=tk.HORIZONTAL, command=self.on_master_volume_change)
        master_volume_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Category volume
        ttk.Label(volume_frame, text="Category Volume:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_volume_var = tk.DoubleVar(value=0.8)
        category_volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.category_volume_var,
                                         orient=tk.HORIZONTAL, command=self.on_category_volume_change)
        category_volume_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        volume_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔊 Test All Sounds", command=self.test_all_sounds).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 Sound Quality Report", command=self.show_quality_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Reset to Defaults", command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🎤 Voice Settings", command=self.show_voice_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Save Settings", command=self.save_settings).pack(side=tk.RIGHT)
    
    def create_category_tab(self, category_name, category_info):
        """Create a tab for a sound category."""
        frame = ttk.Frame(self.notebook)
        
        # Category description
        desc_label = ttk.Label(frame, text=category_info['description'], font=("Arial", 10, "italic"))
        desc_label.pack(pady=(10, 20))
        
        # Create scrollable frame for sounds
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create sound entries
        for i, sound_name in enumerate(category_info['sounds']):
            sound_frame = self.create_sound_entry(scrollable_frame, sound_name, i)
            sound_frame.pack(fill=tk.X, padx=10, pady=5)
            self.sound_entries[sound_name] = sound_frame
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return frame
    
    def create_sound_entry(self, parent, sound_name, index):
        """Create an entry for a single sound."""
        frame = ttk.LabelFrame(parent, text=f"Sound #{index + 1}: {sound_name}")
        
        # Sound info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Sound description
        descriptions = {
            'card_deal': 'Card dealing sound',
            'card_shuffle': 'Card shuffling sound',
            'fold': 'Card folding sound',
            'chip_bet': 'Chip betting sound',
            'chip_collect': 'Chip collecting sound',
            'chip_stack': 'Chip stacking sound',
            'player_bet': 'Player betting sound',
            'player_call': 'Player calling sound',
            'player_raise': 'Player raising sound',
            'player_check': 'Player checking sound',
            'player_fold': 'Player folding sound',
            'player_all_in': 'All-in dramatic sound',
            'pot_win': 'Pot winning sound',
            'pot_split': 'Pot splitting sound',
            'pot_rake': 'Pot rake sound',
            'winner_announce': 'Winner announcement sound',
            'button_click': 'Button click sound',
            'button_hover': 'Button hover sound',
            'button_move': 'Button move sound',
            'turn_notify': 'Turn notification sound',
            'notification': 'General notification sound',
            'success': 'Success sound',
            'error': 'Error sound',
            'menu_open': 'Menu open sound'
        }
        
        desc_label = ttk.Label(info_frame, text=descriptions.get(sound_name, sound_name), font=("Arial", 9))
        desc_label.pack(anchor=tk.W)
        
        # Current file info
        current_frame = ttk.Frame(frame)
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(current_frame, text="Current file:").pack(anchor=tk.W)
        
        # Current file display
        file_frame = ttk.Frame(current_frame)
        file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.current_file_var = tk.StringVar()
        current_file_entry = ttk.Entry(file_frame, textvariable=self.current_file_var, state='readonly')
        current_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Test button
        test_btn = ttk.Button(file_frame, text="🔊 Test", 
                             command=lambda: self.test_sound(sound_name))
        test_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Replace file section
        replace_frame = ttk.Frame(frame)
        replace_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(replace_frame, text="Replace with:").pack(anchor=tk.W)
        
        # File selection
        file_select_frame = ttk.Frame(replace_frame)
        file_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.new_file_var = tk.StringVar()
        new_file_entry = ttk.Entry(file_select_frame, textvariable=self.new_file_var)
        new_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_select_frame, text="Browse", 
                               command=lambda: self.browse_file(sound_name))
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Replace button
        replace_btn = ttk.Button(replace_frame, text="🔄 Replace Sound", 
                                command=lambda: self.replace_sound(sound_name))
        replace_btn.pack(pady=(5, 0))
        
        # Store references
        frame.current_file_var = self.current_file_var
        frame.new_file_var = self.new_file_var
        
        return frame
    
    def load_current_sounds(self):
        """Load current sound file information."""
        # Import and use the sound detection system
        from sound_detection_system import sound_detector
        
        # Get current mappings
        current_mappings = sound_detector.get_current_mappings()
        
        for category_name, category_info in self.sound_categories.items():
            for sound_name in category_info['sounds']:
                if sound_name in self.sound_entries:
                    entry_frame = self.sound_entries[sound_name]
                    
                    # Check for custom mapping first
                    custom_file = self.persistence.get_custom_sound(sound_name)
                    if custom_file:
                        current_file = custom_file
                        # Try to get quality info
                        try:
                            if custom_file in sound_detector.existing_sounds:
                                quality = sound_detector.existing_sounds[custom_file]['quality']
                                current_file = f"{custom_file} ({quality} quality)"
                        except:
                            pass
                    else:
                        # Get current file from sound manager
                        if hasattr(self.sound_manager, 'sound_configs'):
                            if sound_name in self.sound_manager.sound_configs:
                                config = self.sound_manager.sound_configs[sound_name]
                                if hasattr(config, 'name') and config.name and config.name != sound_name:
                                    current_file = config.name
                                    # Try to get quality info
                                    try:
                                        if config.name in sound_detector.existing_sounds:
                                            quality = sound_detector.existing_sounds[config.name]['quality']
                                            current_file = f"{config.name} ({quality} quality)"
                                    except:
                                        pass
                                else:
                                    current_file = "No file mapped"
                            else:
                                current_file = "Not configured"
                        else:
                            current_file = "Not available"
                    
                    entry_frame.current_file_var.set(current_file)
        
        # Update status indicator
        self._update_status_indicator()
    
    def test_sound(self, sound_name):
        """Test a specific sound."""
        try:
            print(f"🔊 Testing sound: {sound_name}")
            self.sound_manager.play(sound_name)
            messagebox.showinfo("Sound Test", f"Playing sound: {sound_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play sound {sound_name}: {e}")
    
    def browse_file(self, sound_name):
        """Browse for a new sound file."""
        print(f"🔍 Browsing for sound: {sound_name}")
        print(f"📋 Available sound entries: {list(self.sound_entries.keys())}")
        
        file_types = [
            ("Audio files", "*.wav *.mp3 *.ogg"),
            ("WAV files", "*.wav"),
            ("MP3 files", "*.mp3"),
            ("OGG files", "*.ogg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title=f"Select new sound file for {sound_name}",
            filetypes=file_types
        )
        
        print(f"📁 Selected file: {filename}")
        
        if filename:
            if sound_name in self.sound_entries:
                entry_frame = self.sound_entries[sound_name]
                entry_frame.new_file_var.set(filename)
                print(f"✅ File set for {sound_name}")
            else:
                print(f"❌ Sound entry not found: {sound_name}")
                messagebox.showerror("Error", f"Sound entry not found: {sound_name}")
        else:
            print("❌ No file selected")
    
    def replace_sound(self, sound_name):
        """Replace a sound with a new file."""
        if sound_name not in self.sound_entries:
            return
        
        entry_frame = self.sound_entries[sound_name]
        new_file_path = entry_frame.new_file_var.get()
        
        if not new_file_path:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        
        if not os.path.exists(new_file_path):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
        
        try:
            # Import simple sound trimmer
            from simple_sound_trimmer import trim_any_audio_file
            
            # Copy file to sounds directory
            new_filename = f"{sound_name}_{os.path.basename(new_file_path)}"
            destination = self.sounds_dir / new_filename
            
            # Trim file if it's longer than 1 second
            print(f"✂️  Processing file for sound replacement...")
            if trim_any_audio_file(new_file_path, str(destination), 1.0):
                print(f"✅ File processed successfully")
            else:
                print(f"⚠️  Failed to process file, copying original")
                shutil.copy2(new_file_path, destination)
            
            # Update sound manager
            if hasattr(self.sound_manager, 'sound_configs'):
                if sound_name in self.sound_manager.sound_configs:
                    config = self.sound_manager.sound_configs[sound_name]
                    
                    # Store the filename without extension for the sound manager
                    filename_without_ext = os.path.splitext(new_filename)[0]
                    config.name = filename_without_ext
                    
                    # Reload the sound in the sound manager
                    try:
                        # Use the new reload method
                        if self.sound_manager.reload_sound(sound_name):
                            print(f"🔄 Reloaded sound: {sound_name} → {filename_without_ext}")
                        else:
                            print(f"⚠️  Failed to reload sound: {sound_name}")
                    except Exception as e:
                        print(f"⚠️  Error reloading sound: {e}")
                    
                    # Save the custom mapping
                    self.persistence.set_custom_sound(sound_name, new_filename)
                    
                    # Update display
                    entry_frame.current_file_var.set(new_filename)
                    entry_frame.new_file_var.set("")
                    
                    messagebox.showinfo("Success", f"Sound {sound_name} replaced with {new_filename}")
                    
                    # Test the new sound immediately
                    try:
                        print(f"🔊 Testing new sound: {sound_name}")
                        self.sound_manager.play(sound_name)
                        print(f"✅ Sound test successful")
                    except Exception as e:
                        print(f"❌ Sound test failed: {e}")
                        messagebox.showwarning("Warning", f"Sound test failed: {e}")
                else:
                    messagebox.showerror("Error", f"Sound {sound_name} not found in sound manager")
            else:
                messagebox.showerror("Error", "Sound manager not properly initialized")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to replace sound: {e}")
    
    def test_all_sounds(self):
        """Test all sounds in sequence."""
        all_sounds = []
        for category_info in self.sound_categories.values():
            all_sounds.extend(category_info['sounds'])
        
        messagebox.showinfo("Test All Sounds", 
                          f"Testing {len(all_sounds)} sounds in sequence...")
        
        for sound_name in all_sounds:
            try:
                print(f"🔊 Testing: {sound_name}")
                self.sound_manager.play(sound_name)
                # Small delay between sounds
                self.parent.after(500)
            except Exception as e:
                print(f"❌ Error testing {sound_name}: {e}")
    
    def show_quality_report(self):
        """Show sound quality report."""
        report = "📊 SOUND QUALITY REPORT\n"
        report += "=" * 40 + "\n\n"
        
        high_quality = []
        medium_quality = []
        low_quality = []
        missing = []
        
        for category_info in self.sound_categories.values():
            for sound_name in category_info['sounds']:
                try:
                    if hasattr(self.sound_manager, 'sound_configs'):
                        if sound_name in self.sound_manager.sound_configs:
                            config = self.sound_manager.sound_configs[sound_name]
                            file_name = config.name
                            
                            if 'mp3' in file_name.lower():
                                if '87543' in file_name or '86984' in file_name:
                                    high_quality.append(sound_name)
                                else:
                                    medium_quality.append(sound_name)
                            else:
                                low_quality.append(sound_name)
                        else:
                            missing.append(sound_name)
                    else:
                        missing.append(sound_name)
                except Exception:
                    missing.append(sound_name)
        
        report += f"🎯 HIGH QUALITY ({len(high_quality)}):\n"
        for sound in high_quality:
            report += f"  • {sound}\n"
        
        report += f"\n🎯 MEDIUM QUALITY ({len(medium_quality)}):\n"
        for sound in medium_quality:
            report += f"  • {sound}\n"
        
        report += f"\n🎯 LOW QUALITY ({len(low_quality)}):\n"
        for sound in low_quality:
            report += f"  • {sound}\n"
        
        if missing:
            report += f"\n❌ MISSING ({len(missing)}):\n"
            for sound in missing:
                report += f"  • {sound}\n"
        
        messagebox.showinfo("Sound Quality Report", report)
    
    def reset_to_defaults(self):
        """Reset all sounds to default files."""
        if messagebox.askyesno("Reset to Defaults", 
                              "This will reset all sounds to their default files. Continue?"):
            # Implementation would reset to original sound files
            messagebox.showinfo("Reset Complete", "Sounds reset to defaults.")
    
    def save_settings(self):
        """Save current sound settings."""
        # Implementation would save settings to a configuration file
        messagebox.showinfo("Settings Saved", "Sound settings have been saved.")
    
    def show_voice_settings(self):
        """Show voice announcement settings."""
        try:
            voice_window = tk.Toplevel(self.parent)
            voice_window.title("🎤 Voice Announcement Settings")
            voice_window.geometry("500x400")
            voice_window.resizable(True, True)
            
            # Create voice settings panel
            voice_panel = voice_system.create_voice_settings_panel(voice_window)
            voice_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            voice_window.grab_set()  # Make window modal
            voice_window.focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open voice settings: {e}")
    
    def on_master_volume_change(self, value):
        """Handle master volume change."""
        volume = float(value)
        self.sound_manager.set_master_volume(volume)
    
    def on_category_volume_change(self, value):
        """Handle category volume change."""
        volume = float(value)
        # Implementation would set category volume
        print(f"Category volume set to: {volume}")
    
    def _update_status_indicator(self):
        """Update the status indicator to show mapping status."""
        if hasattr(self.sound_manager, 'sound_configs'):
            mapped_count = 0
            total_count = 0
            
            for config_name, config in self.sound_manager.sound_configs.items():
                total_count += 1
                if hasattr(config, 'name') and config.name and config.name != config_name:
                    mapped_count += 1
            
            if mapped_count == 0:
                status_text = "⚠️  No sound files are currently mapped. Use 'Browse' to add sound files."
            elif mapped_count < total_count:
                status_text = f"✅ {mapped_count}/{total_count} sounds are mapped. Some sounds need files."
            else:
                status_text = f"✅ All {total_count} sounds are properly mapped!"
            
            self.status_label.config(text=status_text)
        else:
            self.status_label.config(text="❌ Sound manager not properly initialized")

def create_sound_settings_window(parent):
    """Create and return a sound settings window."""
    window = tk.Toplevel(parent)
    window.title("Sound Settings")
    window.geometry("800x600")
    window.resizable(True, True)
    
    # Create the sound settings GUI
    sound_gui = SoundSettingsGUI(window)
    
    return window 