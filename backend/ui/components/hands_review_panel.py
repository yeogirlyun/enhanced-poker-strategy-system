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

from core.phh_converter import PracticeHandsPHHManager
from core.hands_database import ComprehensiveHandsDatabase


class HandsReviewPanel(ttk.Frame):
    """Panel for reviewing poker hands."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.legendary_manager = None
        self.hands_database = ComprehensiveHandsDatabase()
        self.practice_hands = []
        self.practice_phh_files = []
        self.current_hand = None
        self.practice_phh_manager = PracticeHandsPHHManager()
        
        # Font configuration
        self.font_size = 16  # Default size, will be updated by main GUI
        
        self.setup_ui()
        self.load_data()
        
        # Apply initial font size
        self.update_font_size(self.font_size)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ttk.Label(main_frame, text="🎯 Hands Review")
        self.title_label.pack(pady=(0, 20))
        
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
        self.practice_hands_listbox = tk.Listbox(list_frame)
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
        self.practice_details_text = tk.Text(self.practice_details_frame, wrap=tk.WORD)
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
        self.legendary_hands_listbox = tk.Listbox(list_frame)
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
        self.legendary_details_text = tk.Text(self.legendary_details_frame, wrap=tk.WORD)
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
            # Load all hands and filter for legendary ones
            from core.hands_database import HandCategory
            
            legendary_hands_by_category = self.hands_database.get_hands_by_category()
            self.legendary_hands = legendary_hands_by_category.get(HandCategory.LEGENDARY, [])
            
            if self.legendary_hands:
                # Get available categories from legendary hands
                categories = list(set(hand.metadata.subcategory for hand in self.legendary_hands if hand.metadata.subcategory))
                self.category_combo['values'] = ['All Categories'] + categories
                self.category_combo.set('All Categories')
                
                # Update status
                total_hands = len(self.legendary_hands)
                self.legendary_status_label.config(
                    text=f"Loaded {total_hands} legendary hands"
                )
                
                # Load all hands initially
                self.update_legendary_hands_list()
            else:
                self.legendary_status_label.config(text="No legendary hands found")
                
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
        
        if not hasattr(self, 'legendary_hands') or not self.legendary_hands:
            return
        
        # Get hands for the selected category
        if category and category != 'All Categories':
            hands = [hand for hand in self.legendary_hands if hand.metadata.subcategory == category]
        else:
            hands = self.legendary_hands
        
        for hand in hands:
            hand_id = hand.metadata.hand_id or 'Unknown'
            name = hand.metadata.name or 'Unknown Hand'
            subcategory = hand.metadata.subcategory or 'Unknown'
            
            display_text = f"{hand_id} - {name} ({subcategory})"
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
                hands = self.legendary_hands
            else:
                hands = [hand for hand in self.legendary_hands if hand.metadata.subcategory == category]
            
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
        
        # Handle ParsedHand structure
        metadata = hand.metadata
        players = hand.players or []
        conversion_info = hand.raw_data.get('conversion_info', {})
        
        details = f"""🏆 LEGENDARY HAND DETAILS
{'='*50}

📋 Basic Information:
   ID: {metadata.hand_id or 'Unknown'}
   Name: {metadata.name or 'Unknown'}
   Category: {metadata.subcategory or 'Unknown'}
   Event: {metadata.event or 'Unknown'}

📝 Description:
   {metadata.description or 'No description available'}

👥 Players Involved:
   {', '.join(metadata.players_involved)}

💰 Hand Information:
   Pot Size: ${metadata.pot_size:.2f}
   Date: {metadata.date or 'Unknown'}

"""
        
        # Show conversion info if available
        if conversion_info:
            details += f"""🔄 Conversion Info:
   Original Players: {conversion_info.get('original_players', 0)}
   Converted to: {conversion_info.get('converted_players', 0)} players
   Folded Players: {conversion_info.get('folded_players', 0)}
   Method: {conversion_info.get('conversion_method', 'Unknown')}

"""
        
        details += "🃏 Player Setup:\n"
        
        for i, player in enumerate(players):
            name = player.get('name', f'Player {i+1}')
            position = player.get('position', f'Seat {i+1}')
            cards = player.get('cards', [])
            stack = player.get('starting_stack_chips', 100000)
            folded = player.get('folded_preflop', False)
            
            status = " (FOLDED PREFLOP)" if folded else ""
            cards_str = f"{cards}" if cards else "Hidden"
            
            details += f"   {i+1}. {name} ({position}): {cards_str} (Stack: ${stack:.0f}){status}\n"
        
        # Show raw data summary
        details += f"""
📊 Hand Data:
   Raw data keys: {list(hand.raw_data.keys())}
   
🎯 Actions:
   (Actions will be available when simulation system is fully integrated)
"""
        
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
            # Use new ParsedHand structure for simulation
            hand = self.current_hand
            metadata = hand.metadata
            players = hand.players or []
            conversion_info = hand.raw_data.get('conversion_info', {})
            
            # Basic simulation information
            result_text = f"""🎮 SIMULATION RESULTS
{'='*40}

🏆 Hand: {metadata.name}
📅 Date: {metadata.date or 'Unknown'}
💰 Pot Size: ${metadata.pot_size:.2f}

👥 Players ({len(players)} total):
"""
            
            for i, player in enumerate(players):
                name = player.get('name', f'Player {i+1}')
                position = player.get('position', f'Seat {i+1}')
                cards = player.get('cards', [])
                folded = player.get('folded_preflop', False)
                
                status = " 🚫 FOLDED" if folded else " ✅ ACTIVE"
                cards_str = f"{cards}" if cards else "Hidden"
                
                result_text += f"   {i+1}. {name} ({position}): {cards_str}{status}\n"
            
            if conversion_info:
                result_text += f"""
🔄 Conversion Applied:
   • Original: {conversion_info.get('original_players', 0)} players
   • Converted to: {conversion_info.get('converted_players', 0)} players
   • {conversion_info.get('folded_players', 0)} players folded preflop
"""
            
            result_text += """
🎯 Simulation Status:
   Hand successfully loaded and converted for 6-player format!
   
📝 Note: Full poker state machine simulation will be 
   available in the enhanced hands review panel.
"""
            
            messagebox.showinfo("Simulation Results", result_text)
            
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Error simulating hand: {str(e)}\n\nHand structure: {type(self.current_hand)}")
    
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
    
    def update_font_size(self, new_size: int):
        """Update font size for all components."""
        self.font_size = new_size
        
        # Main title (larger, bold)
        title_font = ("Arial", int(new_size * 1.2), "bold")
        self.title_label.config(font=title_font)
        
        # Listboxes
        listbox_font = ("Arial", int(new_size * 0.9))
        self.practice_hands_listbox.config(font=listbox_font)
        self.legendary_hands_listbox.config(font=listbox_font)
        
        # Details text areas (monospace for better readability)
        details_font = ("Courier", int(new_size * 0.8))
        self.practice_details_text.config(font=details_font)
        self.legendary_details_text.config(font=details_font)
