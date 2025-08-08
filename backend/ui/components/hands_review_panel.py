#!/usr/bin/env python3
"""
Hands Review Panel

A comprehensive panel for reviewing poker hands including:
- Practice hands marked for review
- Legendary hands from the database
- Hand simulation and analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from tests.legendary_hands_manager import LegendaryHandsManager
from core.phh_converter import PracticeHandsPHHManager


class HandsReviewPanel(ttk.Frame):
    """Panel for reviewing poker hands."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.legendary_manager = None
        self.practice_hands = []
        self.practice_phh_files = []
        self.current_hand = None
        self.practice_phh_manager = PracticeHandsPHHManager()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Hands Review", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Practice Hands Tab
        self.practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.practice_frame, text="📚 Practice Hands")
        self.setup_practice_hands_tab()
        
        # Legendary Hands Tab
        self.legendary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.legendary_frame, text="🏆 Legendary Hands")
        self.setup_legendary_hands_tab()
    
    def setup_practice_hands_tab(self):
        """Setup the practice hands tab."""
        # Control frame
        control_frame = ttk.Frame(self.practice_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Practice Hands", 
                                command=self.refresh_practice_hands)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load PHH button
        load_phh_btn = ttk.Button(control_frame, text="📂 Load PHH Files", 
                                 command=self.load_practice_phh_files)
        load_phh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.practice_status_label = ttk.Label(control_frame, text="No practice hands found")
        self.practice_status_label.pack(side=tk.LEFT)
        
        # Hands list frame
        list_frame = ttk.Frame(self.practice_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hands list
        self.practice_hands_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.practice_hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        practice_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                          command=self.practice_hands_listbox.yview)
        practice_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.practice_hands_listbox.config(yscrollcommand=practice_scrollbar.set)
        
        # Bind selection event
        self.practice_hands_listbox.bind('<<ListboxSelect>>', self.on_practice_hand_select)
        
        # Hand details frame
        self.practice_details_frame = ttk.LabelFrame(self.practice_frame, text="Hand Details")
        self.practice_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Details text
        self.practice_details_text = tk.Text(self.practice_details_frame, 
                                           font=("Courier", 9), wrap=tk.WORD)
        self.practice_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_legendary_hands_tab(self):
        """Setup the legendary hands tab."""
        # Control frame
        control_frame = ttk.Frame(self.legendary_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Category selection
        ttk.Label(control_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(control_frame, textvariable=self.category_var, 
                                          state="readonly", width=20)
        self.category_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_select)
        
        # Load button
        load_btn = ttk.Button(control_frame, text="📂 Load Legendary Hands", 
                             command=self.load_legendary_hands)
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.legendary_status_label = ttk.Label(control_frame, text="Legendary hands not loaded")
        self.legendary_status_label.pack(side=tk.LEFT)
        
        # Hands list frame
        list_frame = ttk.Frame(self.legendary_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hands list
        self.legendary_hands_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.legendary_hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        legendary_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                           command=self.legendary_hands_listbox.yview)
        legendary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.legendary_hands_listbox.config(yscrollcommand=legendary_scrollbar.set)
        
        # Bind selection event
        self.legendary_hands_listbox.bind('<<ListboxSelect>>', self.on_legendary_hand_select)
        
        # Hand details frame
        self.legendary_details_frame = ttk.LabelFrame(self.legendary_frame, text="Hand Details")
        self.legendary_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Details text
        self.legendary_details_text = tk.Text(self.legendary_details_frame, 
                                            font=("Courier", 9), wrap=tk.WORD)
        self.legendary_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons frame
        action_frame = ttk.Frame(self.legendary_details_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Simulate button
        self.simulate_btn = ttk.Button(action_frame, text="🎮 Simulate Hand", 
                                      command=self.simulate_current_hand)
        self.simulate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Study button
        self.study_btn = ttk.Button(action_frame, text="📚 Study Hand", 
                                   command=self.study_current_hand)
        self.study_btn.pack(side=tk.LEFT)
    
    def load_data(self):
        """Load practice hands and legendary hands data."""
        self.load_practice_hands()
        self.load_practice_phh_files()
        self.load_legendary_hands()
    
    def load_practice_hands(self):
        """Load practice hands from logs."""
        try:
            # Look for practice hands in logs directory
            logs_dir = "logs"
            if os.path.exists(logs_dir):
                practice_hands = []
                
                # Scan for session logs that might contain practice hands
                for filename in os.listdir(logs_dir):
                    if filename.startswith("session_") and filename.endswith(".json"):
                        filepath = os.path.join(logs_dir, filename)
                        try:
                            with open(filepath, 'r') as f:
                                data = json.load(f)
                                
                                # Look for hands marked for review
                                if 'hands' in data:
                                    for hand in data['hands']:
                                        if hand.get('marked_for_review', False):
                                            hand['source_file'] = filename
                                            practice_hands.append(hand)
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")
                
                self.practice_hands = practice_hands
                self.update_practice_hands_list()
                
        except Exception as e:
            print(f"Error loading practice hands: {e}")
    
    def load_practice_phh_files(self):
        """Load practice hands from PHH format files."""
        try:
            # Get available PHH files
            self.practice_phh_files = self.practice_phh_manager.get_practice_hands_files()
            
            # Load metadata for hands in PHH files
            phh_hands = []
            for phh_file_info in self.practice_phh_files:
                if phh_file_info["metadata_file"]:
                    try:
                        with open(phh_file_info["metadata_file"], 'r') as f:
                            metadata = json.load(f)
                            
                            # Add each hand from the metadata
                            for hand in metadata.get("hands", []):
                                hand["source_type"] = "phh"
                                hand["phh_file"] = phh_file_info["phh_file"]
                                hand["session_date"] = phh_file_info["session_date"]
                                phh_hands.append(hand)
                    except Exception as e:
                        print(f"Error loading PHH metadata {phh_file_info['metadata_file']}: {e}")
            
            # Merge with existing practice hands
            self.practice_hands.extend(phh_hands)
            self.update_practice_hands_list()
            
            if phh_hands:
                current_status = self.practice_status_label.cget("text")
                phh_count = len(phh_hands)
                self.practice_status_label.config(
                    text=f"{current_status} + {phh_count} PHH hands"
                )
            
        except Exception as e:
            print(f"Error loading practice PHH files: {e}")
            self.practice_status_label.config(text=f"PHH Error: {str(e)}")
    
    def load_legendary_hands(self):
        """Load legendary hands from the database."""
        try:
            self.legendary_manager = LegendaryHandsManager()
            
            if self.legendary_manager.data:
                # Update category combo
                categories = self.legendary_manager.get_categories()
                self.category_combo['values'] = ['All Categories'] + categories
                self.category_combo.set('All Categories')
                
                # Update status
                total_hands = len(self.legendary_manager.hands)
                self.legendary_status_label.config(
                    text=f"Loaded {total_hands} legendary hands"
                )
                
                # Load all hands initially
                self.update_legendary_hands_list()
            else:
                self.legendary_status_label.config(text="Failed to load legendary hands")
                
        except Exception as e:
            print(f"Error loading legendary hands: {e}")
            self.legendary_status_label.config(text=f"Error: {str(e)}")
    
    def update_practice_hands_list(self):
        """Update the practice hands listbox."""
        self.practice_hands_listbox.delete(0, tk.END)
        
        if not self.practice_hands:
            self.practice_status_label.config(text="No practice hands found")
            return
        
        for i, hand in enumerate(self.practice_hands):
            # Create a display string for the hand
            hand_number = hand.get('hand_number', i + 1)
            
            # Handle different source types
            source_type = hand.get('source_type', 'json')
            if source_type == 'phh':
                # PHH hand display
                session_date = hand.get('session_date', 'Unknown')
                pot_size = hand.get('pot_size', 0)
                display_text = f"[PHH] Hand {hand_number} - ${pot_size:.2f} pot - {session_date}"
            else:
                # Original JSON hand display
                timestamp = hand.get('timestamp', 'Unknown')
                players = len(hand.get('players_involved', hand.get('players', [])))
                display_text = f"[JSON] Hand {hand_number} - {players} players - {timestamp}"
            
            self.practice_hands_listbox.insert(tk.END, display_text)
        
        self.practice_status_label.config(
            text=f"Found {len(self.practice_hands)} practice hands"
        )
    
    def update_legendary_hands_list(self, category=None):
        """Update the legendary hands listbox."""
        self.legendary_hands_listbox.delete(0, tk.END)
        
        if not self.legendary_manager or not self.legendary_manager.hands:
            return
        
        # Get hands for the selected category
        if category and category != 'All Categories':
            hands = self.legendary_manager.get_hands_by_category(category)
        else:
            hands = self.legendary_manager.hands
        
        for hand in hands:
            hand_id = hand.get('id', 'Unknown')
            name = hand.get('name', 'Unknown Hand')
            category = hand.get('category', 'Unknown')
            
            display_text = f"{hand_id} - {name} ({category})"
            self.legendary_hands_listbox.insert(tk.END, display_text)
    
    def on_practice_hand_select(self, event):
        """Handle practice hand selection."""
        selection = self.practice_hands_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.practice_hands):
                hand = self.practice_hands[index]
                self.display_practice_hand_details(hand)
    
    def on_legendary_hand_select(self, event):
        """Handle legendary hand selection."""
        selection = self.legendary_hands_listbox.curselection()
        if selection:
            index = selection[0]
            
            # Get the selected category
            category = self.category_var.get()
            if category == 'All Categories':
                hands = self.legendary_manager.hands
            else:
                hands = self.legendary_manager.get_hands_by_category(category)
            
            if index < len(hands):
                hand = hands[index]
                self.current_hand = hand
                self.display_legendary_hand_details(hand)
    
    def on_category_select(self, event):
        """Handle category selection."""
        category = self.category_var.get()
        self.update_legendary_hands_list(category)
    
    def display_practice_hand_details(self, hand):
        """Display practice hand details."""
        self.practice_details_text.delete(1.0, tk.END)
        
        source_type = hand.get('source_type', 'json')
        
        if source_type == 'phh':
            # Display PHH hand details
            details = f"""🎯 PRACTICE HAND DETAILS (PHH Format)
{'='*50}

📋 Hand Information:
   ID: {hand.get('id', 'Unknown')}
   Name: {hand.get('name', 'Unknown')}
   Category: {hand.get('category', 'Unknown')}
   Session Date: {hand.get('session_date', 'Unknown')}
   Hand Number: {hand.get('hand_number', 'Unknown')}
   Source: {hand.get('source', 'Unknown')}

💰 Pot Information:
   Final Pot: ${hand.get('pot_size', 0):.2f}
   Duration: {hand.get('duration_ms', 0)}ms

👥 Players Involved:
   {', '.join(hand.get('players_involved', []))}

📝 Description:
   {hand.get('description', 'No description available')}

🎓 Study Value:
   {hand.get('study_value', 'No study value specified')}

📚 Why Notable:
   {hand.get('why_notable', 'No specific context')}

📁 Files:
   PHH File: {hand.get('phh_file', 'Unknown')}
   Session ID: {hand.get('session_id', 'Unknown')}

🏁 Hand Status:
   Complete: {'✅' if hand.get('hand_complete', False) else '❌'}
   Streets Reached: {', '.join(hand.get('streets_reached', []))}
"""
        else:
            # Display original JSON hand details
            details = f"""🎯 PRACTICE HAND DETAILS (JSON Format)
{'='*50}

📋 Hand Information:
   Hand Number: {hand.get('hand_number', 'Unknown')}
   Timestamp: {hand.get('timestamp', 'Unknown')}
   Source File: {hand.get('source_file', 'Unknown')}
   Players: {len(hand.get('players', []))}

💰 Pot Information:
   Final Pot: ${hand.get('pot_size', 0):.2f}

👥 Players:
"""
            
            for player in hand.get('players', []):
                details += f"   {player.get('name', 'Unknown')}: ${player.get('stack', 0):.2f}\n"
            
            details += f"""
🎲 Actions:
"""
            
            # Display actions by street
            for street in ['preflop_actions', 'flop_actions', 'turn_actions', 'river_actions']:
                actions = hand.get(street, [])
                if actions:
                    details += f"\n{street.replace('_', ' ').title()}:\n"
                    for action in actions:
                        details += f"   {action}\n"
        
        self.practice_details_text.insert(1.0, details)
    
    def display_legendary_hand_details(self, hand):
        """Display legendary hand details."""
        self.legendary_details_text.delete(1.0, tk.END)
        
        details = f"""🏆 LEGENDARY HAND DETAILS
{'='*50}

📋 Basic Information:
   ID: {hand.get('id', 'Unknown')}
   Name: {hand.get('name', 'Unknown')}
   Category: {hand.get('category', 'Unknown')}
   Event: {hand.get('event', 'Unknown')}

📝 Description:
   {hand.get('description', 'No description available')}

👥 Players Involved:
   {', '.join(hand.get('players_involved', []))}

💰 Expected Results:
   Expected Winner: Player {hand.get('expected_winner_index', -1) + 1}
   Expected Pot: ${hand.get('expected_pot', 0):.2f}

📚 Study Value:
   {hand.get('study_value', 'No study value specified')}

⭐ Why Legendary:
   {hand.get('why_legendary', 'No legendary context provided')}

🎮 Setup:
   Players: {hand.get('setup', {}).get('num_players', 0)}
   Dealer: Position {hand.get('setup', {}).get('dealer_position', 0)}
   Blinds: ${hand.get('setup', {}).get('small_blind', 0)}/${hand.get('setup', {}).get('big_blind', 0)}

🃏 Player Cards:
"""
        
        setup = hand.get('setup', {})
        player_cards = setup.get('player_cards', [])
        player_stacks = setup.get('player_stacks', [])
        
        for i, (cards, stack) in enumerate(zip(player_cards, player_stacks)):
            details += f"   Player {i+1}: {cards} (Stack: ${stack:.2f})\n"
        
        details += f"""
🎲 Board: {hand.get('board', [])}

🎯 Actions ({len(hand.get('actions', []))} total):
"""
        
        for i, action in enumerate(hand.get('actions', [])[:15]):  # Show first 15 actions
            player_idx = action.get('player_index', 0) + 1
            action_type = action.get('action', 'UNKNOWN')
            amount = action.get('amount', 0)
            street = action.get('street', 'preflop')
            details += f"   {i+1:2d}. Player {player_idx} {action_type} ${amount:.1f} ({street})\n"
        
        if len(hand.get('actions', [])) > 15:
            details += f"   ... and {len(hand.get('actions', [])) - 15} more actions\n"
        
        self.legendary_details_text.insert(1.0, details)
    
    def refresh_practice_hands(self):
        """Refresh the practice hands list."""
        # Clear existing hands and reload
        self.practice_hands = []
        self.load_practice_hands()
        self.load_practice_phh_files()
    
    def simulate_current_hand(self):
        """Simulate the currently selected legendary hand."""
        if not self.current_hand:
            messagebox.showwarning("No Hand Selected", "Please select a legendary hand to simulate.")
            return
        
        try:
            result = self.legendary_manager.simulate_hand(self.current_hand, verbose=False)
            
            # Show simulation results
            result_text = f"""🎮 SIMULATION RESULTS
{'='*30}

Expected Winner: Player {result['expected_winner'] + 1}
Actual Winners: Players {[i+1 for i in result['actual_winners']]}

Expected Pot: ${result['expected_pot']:.2f}
Actual Pot: ${result['actual_pot']:.2f}

Success: {'✅' if result['success'] else '❌'}
"""
            
            messagebox.showinfo("Simulation Results", result_text)
            
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Error simulating hand: {str(e)}")
    
    def study_current_hand(self):
        """Open study mode for the current hand."""
        if not self.current_hand:
            messagebox.showwarning("No Hand Selected", "Please select a legendary hand to study.")
            return
        
        # For now, just show a message about study features
        study_text = f"""📚 STUDY MODE - {self.current_hand.get('name', 'Unknown Hand')}

This hand is perfect for studying:
- {self.current_hand.get('study_value', 'No specific study value')}

Key learning points:
- {self.current_hand.get('why_legendary', 'No specific context')}

Future study features will include:
- Equity evolution analysis
- Decision tree visualization
- Hand replay with pause/resume
- Strategy comparison tools
"""
        
        messagebox.showinfo("Study Mode", study_text)
