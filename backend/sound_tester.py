#!/usr/bin/env python3
"""
Sound Tester & Configuration Tool for Poker Training System

This tool allows you to:
1. Browse and play any sound file in the sounds directory
2. Configure which sounds to use for different poker events
3. Save/load sound configuration files
4. Test the exact sound playback method used by the poker app
"""

import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import pygame
import threading

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sound_manager import SoundManager


class SoundTesterApp:
    """GUI application for testing and configuring poker sounds."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker Sound Tester & Configuration Tool")
        self.root.geometry("1000x700")
        
        # Initialize sound manager (same as poker app)
        self.sound_manager = SoundManager(test_mode=False)
        
        # Sound configuration
        self.sound_config = {}
        self.config_file = "backend/sounds/poker_sound_config.json"
        
        # Available poker events that need sounds
        self.poker_events = {
            "card_dealing": {
                "name": "Card Dealing",
                "description": "Sound when flop, turn, or river cards are dealt",
                "current": "card_deal.wav"
            },
            "card_shuffle": {
                "name": "Card Shuffle", 
                "description": "Sound when cards are shuffled",
                "current": "shuffle-cards-46455.mp3"
            },
            "chip_bet": {
                "name": "Chip Betting",
                "description": "Sound when chips are bet/raised",
                "current": "chip_bet.wav"
            },
            "chip_collect": {
                "name": "Chip Collection",
                "description": "Sound when pot is collected",
                "current": "pot_split.wav"
            },
            "player_action_check": {
                "name": "Player Check",
                "description": "Voice sound when player checks",
                "current": "player_check.wav"
            },
            "player_action_call": {
                "name": "Player Call",
                "description": "Voice sound when player calls",
                "current": "player_call.wav"
            },
            "player_action_bet": {
                "name": "Player Bet",
                "description": "Voice sound when player bets",
                "current": "player_bet.wav"
            },
            "player_action_raise": {
                "name": "Player Raise",
                "description": "Voice sound when player raises",
                "current": "player_raise.wav"
            },
            "player_action_fold": {
                "name": "Player Fold",
                "description": "Voice sound when player folds",
                "current": "player_fold.wav"
            },
            "player_action_all_in": {
                "name": "Player All-In",
                "description": "Voice sound when player goes all-in",
                "current": "player_all_in.wav"
            },
            "winner_announce": {
                "name": "Winner Announcement",
                "description": "Sound when winner is announced",
                "current": "winner_announce.wav"
            },
            "turn_notification": {
                "name": "Turn Notification",
                "description": "Sound to notify player's turn",
                "current": "turn_notify.wav"
            },
            "ui_click": {
                "name": "UI Click",
                "description": "Sound for button clicks",
                "current": "button_move.wav"
            }
        }
        
        # Setup GUI first
        self.setup_gui()
        
        # Load existing configuration
        self.load_config()
        
        # Populate sound files
        self.refresh_sound_files()
    
    def setup_gui(self):
        """Setup the GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Poker Sound Tester & Configuration Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Sound Files Browser
        files_frame = ttk.LabelFrame(main_frame, text="Available Sound Files", padding="10")
        files_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Sound files listbox with scrollbar
        files_list_frame = ttk.Frame(files_frame)
        files_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_listbox = tk.Listbox(files_list_frame, height=20, selectmode=tk.EXTENDED)
        files_scrollbar = ttk.Scrollbar(files_list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File action buttons frame
        file_buttons_frame = ttk.Frame(files_frame)
        file_buttons_frame.pack(pady=(10, 0), fill=tk.X)
        
        # Top row of buttons
        top_buttons = ttk.Frame(file_buttons_frame)
        top_buttons.pack(fill=tk.X)
        
        # Play button for selected file
        play_file_btn = ttk.Button(top_buttons, text="🔊 Play", 
                                  command=self.play_selected_file)
        play_file_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button for selected file
        delete_file_btn = ttk.Button(top_buttons, text="🗑️ Delete", 
                                    command=self.delete_selected_file)
        delete_file_btn.pack(side=tk.LEFT, padx=5)
        
        # File info button
        info_btn = ttk.Button(top_buttons, text="ℹ️ Info", 
                             command=self.show_file_info)
        info_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(top_buttons, text="🔄 Refresh", 
                               command=self.refresh_sound_files)
        refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bottom row of buttons
        bottom_buttons = ttk.Frame(file_buttons_frame)
        bottom_buttons.pack(fill=tk.X, pady=(5, 0))
        
        # Bulk delete button
        bulk_delete_btn = ttk.Button(bottom_buttons, text="🗑️ Delete Multiple", 
                                    command=self.bulk_delete_files)
        bulk_delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Select all button
        select_all_btn = ttk.Button(bottom_buttons, text="☑️ Select All", 
                                   command=self.select_all_files)
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Event Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Poker Event Sound Configuration", padding="10")
        config_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        config_frame.columnconfigure(0, weight=1)
        
        # Events treeview
        self.events_tree = ttk.Treeview(config_frame, columns=("current_sound",), height=15)
        self.events_tree.heading("#0", text="Poker Event")
        self.events_tree.heading("current_sound", text="Current Sound File")
        self.events_tree.column("#0", width=250)
        self.events_tree.column("current_sound", width=200)
        
        events_scrollbar = ttk.Scrollbar(config_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        events_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate events tree
        self.populate_events_tree()
        
        # Event configuration buttons
        event_buttons_frame = ttk.Frame(config_frame)
        event_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        play_event_btn = ttk.Button(event_buttons_frame, text="🔊 Play Event Sound", 
                                   command=self.play_event_sound)
        play_event_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        assign_btn = ttk.Button(event_buttons_frame, text="📝 Assign Selected File to Event", 
                               command=self.assign_sound_to_event)
        assign_btn.pack(side=tk.LEFT, padx=5)
        
        # Bottom panel - Configuration Management
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Configuration file management
        config_mgmt_frame = ttk.LabelFrame(bottom_frame, text="Configuration Management", padding="10")
        config_mgmt_frame.pack(fill=tk.X)
        
        config_buttons_frame = ttk.Frame(config_mgmt_frame)
        config_buttons_frame.pack()
        
        save_btn = ttk.Button(config_buttons_frame, text="💾 Save Configuration", 
                             command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = ttk.Button(config_buttons_frame, text="📂 Load Configuration", 
                             command=self.load_config_dialog)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(config_buttons_frame, text="🔄 Reset to Defaults", 
                              command=self.reset_to_defaults)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a sound file and poker event to configure")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def refresh_sound_files(self):
        """Refresh the list of available sound files."""
        self.files_listbox.delete(0, tk.END)
        
        sounds_dir = Path("backend/sounds")
        if not sounds_dir.exists():
            self.status_var.set("Error: sounds directory not found")
            return
        
        # Get all sound files recursively
        sound_extensions = {'.wav', '.mp3', '.ogg', '.flac'}
        sound_files = []
        
        for file_path in sounds_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in sound_extensions:
                # Store relative path from sounds directory
                relative_path = file_path.relative_to(sounds_dir)
                sound_files.append(str(relative_path))
        
        # Sort files
        sound_files.sort()
        
        # Add to listbox
        for file_path in sound_files:
            self.files_listbox.insert(tk.END, file_path)
        
        self.status_var.set(f"Found {len(sound_files)} sound files")
    
    def populate_events_tree(self):
        """Populate the events tree with poker events."""
        for event_id, event_info in self.poker_events.items():
            current_sound = self.sound_config.get(event_id, event_info["current"])
            self.events_tree.insert("", tk.END, iid=event_id, 
                                   text=f"{event_info['name']}\n{event_info['description']}", 
                                   values=(current_sound,))
    
    def play_selected_file(self):
        """Play the currently selected sound file."""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sound file to play")
            return
        
        file_path = self.files_listbox.get(selection[0])
        self.play_sound_file(file_path)
    
    def delete_selected_file(self):
        """Delete the currently selected sound file."""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sound file to delete")
            return
        
        file_path = self.files_listbox.get(selection[0])
        full_path = os.path.join("backend/sounds", file_path)
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to permanently delete this file?\n\n{file_path}\n\nThis action cannot be undone!",
            icon="warning"
        )
        
        if not result:
            return
        
        try:
            # Check if file exists
            if not os.path.exists(full_path):
                messagebox.showerror("File Not Found", f"File not found: {file_path}")
                self.refresh_sound_files()  # Refresh to remove stale entries
                return
            
            # Check if file is currently in use by any poker event
            file_in_use = []
            for event_id, event_info in self.poker_events.items():
                current_sound = self.sound_config.get(event_id, event_info["current"])
                if current_sound == file_path:
                    file_in_use.append(event_info["name"])
            
            # Warn if file is in use
            if file_in_use:
                warning_msg = f"Warning: This file is currently assigned to:\n\n"
                warning_msg += "\n".join(f"• {event}" for event in file_in_use)
                warning_msg += f"\n\nDeleting it will cause these events to have no sound. Continue?"
                
                if not messagebox.askyesno("File In Use", warning_msg, icon="warning"):
                    return
            
            # Delete the file
            os.remove(full_path)
            
            # Remove from listbox
            self.files_listbox.delete(selection[0])
            
            # Update status
            self.status_var.set(f"Deleted: {file_path}")
            
            # If file was in use, update the configuration
            if file_in_use:
                for event_id, event_info in self.poker_events.items():
                    current_sound = self.sound_config.get(event_id, event_info["current"])
                    if current_sound == file_path:
                        # Reset to default or remove from config
                        if event_id in self.sound_config:
                            del self.sound_config[event_id]
                
                # Refresh events tree to show changes
                self.refresh_events_tree()
                messagebox.showinfo("File Deleted", 
                                  f"File deleted successfully.\n\nThe following events have been reset to defaults:\n" + 
                                  "\n".join(f"• {event}" for event in file_in_use))
            else:
                messagebox.showinfo("File Deleted", f"File deleted successfully: {file_path}")
                
        except PermissionError:
            messagebox.showerror("Permission Error", 
                               f"Cannot delete file: Permission denied\n\n{file_path}\n\nThe file may be in use or you may not have permission to delete it.")
        except Exception as e:
            messagebox.showerror("Delete Error", 
                               f"Could not delete file: {file_path}\n\nError: {str(e)}")
            self.status_var.set(f"Error deleting {file_path}: {str(e)}")
    
    def show_file_info(self):
        """Show information about the selected sound file."""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sound file to view info")
            return
        
        file_path = self.files_listbox.get(selection[0])
        full_path = os.path.join("backend/sounds", file_path)
        
        try:
            if not os.path.exists(full_path):
                messagebox.showerror("File Not Found", f"File not found: {file_path}")
                return
            
            # Get file stats
            stat = os.stat(full_path)
            file_size = stat.st_size
            modified_time = time.ctime(stat.st_mtime)
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Check if file is in use
            used_by = []
            for event_id, event_info in self.poker_events.items():
                current_sound = self.sound_config.get(event_id, event_info["current"])
                if current_sound == file_path:
                    used_by.append(event_info["name"])
            
            # Create info message
            info_msg = f"File: {file_path}\n\n"
            info_msg += f"Size: {size_str}\n"
            info_msg += f"Modified: {modified_time}\n\n"
            
            if used_by:
                info_msg += f"Used by poker events:\n"
                info_msg += "\n".join(f"• {event}" for event in used_by)
            else:
                info_msg += "Not currently used by any poker events"
            
            messagebox.showinfo("File Information", info_msg)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get file info: {str(e)}")
    
    def bulk_delete_files(self):
        """Delete multiple selected sound files."""
        selections = self.files_listbox.curselection()
        if not selections:
            messagebox.showwarning("No Selection", "Please select one or more sound files to delete")
            return
        
        file_paths = [self.files_listbox.get(i) for i in selections]
        
        # Confirm bulk deletion
        if len(file_paths) == 1:
            self.delete_selected_file()  # Use single delete for one file
            return
        
        result = messagebox.askyesno(
            "Confirm Bulk Deletion", 
            f"Are you sure you want to permanently delete {len(file_paths)} files?\n\nThis action cannot be undone!",
            icon="warning"
        )
        
        if not result:
            return
        
        deleted_count = 0
        errors = []
        files_in_use = []
        
        for file_path in file_paths:
            full_path = os.path.join("backend/sounds", file_path)
            
            try:
                if not os.path.exists(full_path):
                    errors.append(f"{file_path}: File not found")
                    continue
                
                # Check if file is in use
                used_by = []
                for event_id, event_info in self.poker_events.items():
                    current_sound = self.sound_config.get(event_id, event_info["current"])
                    if current_sound == file_path:
                        used_by.append(event_info["name"])
                
                if used_by:
                    files_in_use.append((file_path, used_by))
                
                # Delete the file
                os.remove(full_path)
                deleted_count += 1
                
                # Remove from config if in use
                for event_id, event_info in self.poker_events.items():
                    current_sound = self.sound_config.get(event_id, event_info["current"])
                    if current_sound == file_path and event_id in self.sound_config:
                        del self.sound_config[event_id]
                
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        # Refresh the file list
        self.refresh_sound_files()
        
        # Refresh events tree if any files were in use
        if files_in_use:
            self.refresh_events_tree()
        
        # Show results
        result_msg = f"Bulk deletion completed:\n\n"
        result_msg += f"✅ Successfully deleted: {deleted_count} files\n"
        
        if errors:
            result_msg += f"❌ Errors: {len(errors)} files\n"
        
        if files_in_use:
            result_msg += f"⚠️ Files that were in use: {len(files_in_use)}\n"
            result_msg += "\nThese poker events have been reset to defaults:\n"
            for file_path, used_by in files_in_use:
                result_msg += f"\n{file_path}:\n"
                result_msg += "\n".join(f"  • {event}" for event in used_by)
        
        if errors:
            result_msg += f"\n\nErrors encountered:\n"
            result_msg += "\n".join(f"• {error}" for error in errors)
        
        messagebox.showinfo("Bulk Deletion Results", result_msg)
        self.status_var.set(f"Bulk delete: {deleted_count} deleted, {len(errors)} errors")
    
    def select_all_files(self):
        """Select all files in the listbox."""
        self.files_listbox.select_set(0, tk.END)
        count = self.files_listbox.size()
        self.status_var.set(f"Selected all {count} files")
    
    def play_event_sound(self):
        """Play the sound assigned to the selected event."""
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a poker event")
            return
        
        event_id = selection[0]
        sound_file = self.sound_config.get(event_id, self.poker_events[event_id]["current"])
        self.play_sound_file(sound_file)
    
    def play_sound_file(self, file_path):
        """Play a sound file using the same method as the poker app."""
        try:
            # Use the exact same method as SoundManager
            full_path = os.path.join("backend/sounds", file_path)
            
            if not os.path.exists(full_path):
                self.status_var.set(f"Error: File not found - {file_path}")
                return
            
            # Play using SoundManager (same as poker app)
            self.sound_manager.play(file_path)
            self.status_var.set(f"Playing: {file_path}")
            
        except Exception as e:
            self.status_var.set(f"Error playing {file_path}: {str(e)}")
            messagebox.showerror("Playback Error", f"Could not play {file_path}:\\n{str(e)}")
    
    def assign_sound_to_event(self):
        """Assign the selected sound file to the selected poker event."""
        # Get selected file
        file_selection = self.files_listbox.curselection()
        if not file_selection:
            messagebox.showwarning("No File Selected", "Please select a sound file first")
            return
        
        # Get selected event
        event_selection = self.events_tree.selection()
        if not event_selection:
            messagebox.showwarning("No Event Selected", "Please select a poker event")
            return
        
        file_path = self.files_listbox.get(file_selection[0])
        event_id = event_selection[0]
        
        # Update configuration
        self.sound_config[event_id] = file_path
        
        # Update tree display
        self.events_tree.item(event_id, values=(file_path,))
        
        event_name = self.poker_events[event_id]["name"]
        self.status_var.set(f"Assigned '{file_path}' to '{event_name}'")
    
    def save_config(self):
        """Save the current sound configuration to file."""
        try:
            config_data = {
                "poker_sound_events": self.sound_config,
                "metadata": {
                    "created_by": "Poker Sound Tester",
                    "version": "1.0",
                    "description": "Sound configuration for poker events"
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.status_var.set(f"Configuration saved to {self.config_file}")
            messagebox.showinfo("Saved", f"Sound configuration saved to {self.config_file}")
            
        except Exception as e:
            self.status_var.set(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Save Error", f"Could not save configuration:\\n{str(e)}")
    
    def load_config(self):
        """Load sound configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                self.sound_config = config_data.get("poker_sound_events", {})
                self.refresh_events_tree()
                self.status_var.set(f"Configuration loaded from {self.config_file}")
            else:
                # Use defaults
                self.sound_config = {}
                self.status_var.set("No configuration file found, using defaults")
                
        except Exception as e:
            self.status_var.set(f"Error loading configuration: {str(e)}")
            messagebox.showerror("Load Error", f"Could not load configuration:\\n{str(e)}")
    
    def load_config_dialog(self):
        """Load configuration from a selected file."""
        file_path = filedialog.askopenfilename(
            title="Load Sound Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                
                self.sound_config = config_data.get("poker_sound_events", {})
                self.refresh_events_tree()
                self.status_var.set(f"Configuration loaded from {file_path}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load configuration:\\n{str(e)}")
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        if messagebox.askyesno("Reset Configuration", 
                              "Are you sure you want to reset to default sound assignments?"):
            self.sound_config = {}
            self.refresh_events_tree()
            self.status_var.set("Configuration reset to defaults")
    
    def refresh_events_tree(self):
        """Refresh the events tree display."""
        for event_id in self.poker_events.keys():
            current_sound = self.sound_config.get(event_id, self.poker_events[event_id]["current"])
            self.events_tree.item(event_id, values=(current_sound,))
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print("🎵 Starting Poker Sound Tester...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    app = SoundTesterApp()
    app.run()
