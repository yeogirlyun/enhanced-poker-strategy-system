#!/usr/bin/env python3
"""
Enhanced Hands Review Panel

A comprehensive redesigned panel for reviewing poker hands with:
- Three main categories: Legendary, Practice, Tagged/Important
- Advanced tagging and labeling system
- Hand simulation and replay capabilities
- Unified interface for all hand types
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from core.hands_database import (
    ComprehensiveHandsDatabase, HandCategory, ParsedHand, UserTaggedHandsManager
)
from core.gui_models import GridSettings


class HandSimulationPanel(ttk.Frame):
    """Panel for simulating and replaying hands."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_hand: Optional[ParsedHand] = None
        self.simulation_state = {
            'current_street': 'preflop',
            'action_index': 0,
            'is_playing': False
        }
        # Font configuration
        self.font_size = 16  # Default size, will be updated by main GUI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the simulation panel UI."""
        # Title
        self.title_label = ttk.Label(self, text="🎮 Hand Simulation & Analysis")
        self.title_label.pack(pady=(0, 10))
        
        # Hand info frame
        self.info_frame = ttk.LabelFrame(self, text="Hand Information")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.hand_title_label = ttk.Label(self.info_frame, text="No hand selected")
        self.hand_title_label.pack(pady=5)
        
        # Players and positions frame
        self.players_frame = ttk.LabelFrame(self, text="Players & Positions")
        self.players_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Board and actions frame
        self.board_frame = ttk.LabelFrame(self, text="Board & Actions")
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Board display
        board_display_frame = ttk.Frame(self.board_frame)
        board_display_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(board_display_frame, text="Board:").pack(side=tk.LEFT)
        self.board_label = ttk.Label(board_display_frame, text="")
        self.board_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Actions display
        self.actions_text = tk.Text(self.board_frame, height=8)
        actions_scrollbar = ttk.Scrollbar(self.board_frame, orient=tk.VERTICAL,
                                         command=self.actions_text.yview)
        self.actions_text.config(yscrollcommand=actions_scrollbar.set)
        
        self.actions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        actions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Control buttons frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.replay_btn = ttk.Button(controls_frame, text="▶️ Replay Hand",
                                    command=self.replay_hand)
        self.replay_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.step_btn = ttk.Button(controls_frame, text="⏭️ Step Forward",
                                  command=self.step_forward)
        self.step_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_btn = ttk.Button(controls_frame, text="🔄 Reset",
                                   command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Analysis button
        self.analyze_btn = ttk.Button(controls_frame, text="📊 Analyze",
                                     command=self.analyze_hand)
        self.analyze_btn.pack(side=tk.RIGHT)
        
        # Apply initial font size
        self.update_font_size(self.font_size)
    
    def update_font_size(self, new_size: int):
        """Update font size for all components."""
        self.font_size = new_size
        
        # Title (larger, bold)
        title_font = ("Arial", int(new_size * 1.2), "bold")
        self.title_label.config(font=title_font)
        
        # Hand title (medium, bold)
        hand_title_font = ("Arial", new_size, "bold") 
        self.hand_title_label.config(font=hand_title_font)
        
        # Board label (monospace, bold)
        board_font = ("Courier", new_size, "bold")
        self.board_label.config(font=board_font)
        
        # Actions text (monospace)
        actions_font = ("Courier", int(new_size * 0.9))
        self.actions_text.config(font=actions_font)
        
        # Update info label if it exists
        if hasattr(self, 'hand_info_label'):
            info_font = ("Arial", int(new_size * 0.9))
            self.hand_info_label.config(font=info_font)
    
    def load_hand(self, hand: ParsedHand):
        """Load a hand for simulation."""
        self.current_hand = hand
        self.reset_simulation()
        self.display_hand_info()
        self.display_players()
    
    def display_hand_info(self):
        """Display basic hand information."""
        if not self.current_hand:
            return
        
        hand = self.current_hand
        title = f"{hand.metadata.name}"
        if hand.metadata.event:
            title += f" ({hand.metadata.event})"
        
        self.hand_title_label.config(text=title)
        
        # Display pot size and other info
        pot_info = f"Pot: ${hand.metadata.pot_size:.2f}"
        if hand.metadata.date:
            pot_info += f" • Date: {hand.metadata.date}"
        
        # Create info label if it doesn't exist
        if not hasattr(self, 'hand_info_label'):
            self.hand_info_label = ttk.Label(self.info_frame, text="")
            self.hand_info_label.pack()
        
        self.hand_info_label.config(text=pot_info)
    
    def display_players(self):
        """Display player information."""
        # Clear existing player widgets
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        
        if not self.current_hand or not self.current_hand.players:
            ttk.Label(self.players_frame, text="Player information not available").pack()
            return
        
        # Create grid for players
        players_grid = ttk.Frame(self.players_frame)
        players_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Headers
        ttk.Label(players_grid, text="Seat", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, sticky=tk.W)
        ttk.Label(players_grid, text="Player", font=("Arial", 10, "bold")).grid(
            row=0, column=1, padx=5, sticky=tk.W)
        ttk.Label(players_grid, text="Stack", font=("Arial", 10, "bold")).grid(
            row=0, column=2, padx=5, sticky=tk.W)
        ttk.Label(players_grid, text="Cards", font=("Arial", 10, "bold")).grid(
            row=0, column=3, padx=5, sticky=tk.W)
        
        # Player rows
        for i, player in enumerate(self.current_hand.players[:6]):  # Limit to 6 players
            row = i + 1
            
            # Seat
            seat = player.get('seat', i + 1)
            ttk.Label(players_grid, text=str(seat)).grid(
                row=row, column=0, padx=5, sticky=tk.W)
            
            # Name
            name = player.get('name', f'Player {i+1}')
            ttk.Label(players_grid, text=name).grid(
                row=row, column=1, padx=5, sticky=tk.W)
            
            # Stack
            stack = player.get('starting_stack_chips', player.get('stack', 0))
            ttk.Label(players_grid, text=f"${stack:,.0f}").grid(
                row=row, column=2, padx=5, sticky=tk.W)
            
            # Cards
            cards = player.get('cards', [])
            if cards:
                cards_str = ' '.join(cards)
            else:
                cards_str = "Hidden"
            ttk.Label(players_grid, text=cards_str, font=("Courier", 10)).grid(
                row=row, column=3, padx=5, sticky=tk.W)
    
    def replay_hand(self):
        """Start replaying the hand."""
        if not self.current_hand:
            messagebox.showwarning("No Hand", "Please select a hand to replay.")
            return
        
        self.reset_simulation()
        self.simulation_state['is_playing'] = True
        self.display_initial_state()
    
    def step_forward(self):
        """Step forward one action in the simulation."""
        if not self.current_hand:
            return
        
        # This is a simplified version - would need more complex logic for full simulation
        actions = self.current_hand.actions
        current_street = self.simulation_state['current_street']
        
        if current_street in actions:
            street_actions = actions[current_street]
            action_index = self.simulation_state['action_index']
            
            if action_index < len(street_actions):
                action = street_actions[action_index]
                self.display_action(action, current_street)
                self.simulation_state['action_index'] += 1
            else:
                # Move to next street
                self.advance_street()
    
    def display_initial_state(self):
        """Display the initial state of the hand."""
        self.actions_text.delete(1.0, tk.END)
        self.actions_text.insert(tk.END, "🎯 Hand Starting...\n\n")
        
        # Display blinds
        if self.current_hand.game_info:
            game = self.current_hand.game_info
            if 'stakes' in game:
                stakes = game['stakes']
                self.actions_text.insert(tk.END, f"Stakes: {stakes}\n")
        
        self.actions_text.insert(tk.END, "Dealing hole cards...\n\n")
        self.board_label.config(text="[No community cards yet]")
    
    def display_action(self, action: Dict, street: str):
        """Display a single action."""
        if isinstance(action, dict):
            actor = action.get('actor', action.get('player', 'Unknown'))
            action_type = action.get('type', action.get('action', 'unknown'))
            amount = action.get('amount', action.get('to', 0))
            
            action_str = f"{actor}: {action_type.upper()}"
            if amount > 0:
                action_str += f" ${amount:,.0f}"
            
            self.actions_text.insert(tk.END, f"[{street.upper()}] {action_str}\n")
        else:
            self.actions_text.insert(tk.END, f"[{street.upper()}] {action}\n")
        
        # Scroll to bottom
        self.actions_text.see(tk.END)
    
    def advance_street(self):
        """Advance to the next street."""
        streets = ['preflop', 'flop', 'turn', 'river']
        current_index = streets.index(self.simulation_state['current_street'])
        
        if current_index < len(streets) - 1:
            next_street = streets[current_index + 1]
            self.simulation_state['current_street'] = next_street
            self.simulation_state['action_index'] = 0
            
            # Display board for this street
            self.display_board_for_street(next_street)
            self.actions_text.insert(tk.END, f"\n--- {next_street.upper()} ---\n")
        else:
            # Hand complete
            self.actions_text.insert(tk.END, "\n🏁 Hand Complete!\n")
            self.simulation_state['is_playing'] = False
    
    def display_board_for_street(self, street: str):
        """Display board cards for the given street."""
        board = self.current_hand.board
        
        if street == 'flop' and 'flop' in board:
            cards = board['flop'].get('cards', [])
            self.board_label.config(text=' '.join(cards))
        elif street == 'turn' and 'turn' in board:
            # Add turn card to existing flop
            flop_cards = board.get('flop', {}).get('cards', [])
            turn_card = board['turn'].get('card', '')
            all_cards = flop_cards + [turn_card] if turn_card else flop_cards
            self.board_label.config(text=' '.join(all_cards))
        elif street == 'river' and 'river' in board:
            # Add river card
            flop_cards = board.get('flop', {}).get('cards', [])
            turn_card = board.get('turn', {}).get('card', '')
            river_card = board['river'].get('card', '')
            all_cards = flop_cards + ([turn_card] if turn_card else []) + ([river_card] if river_card else [])
            self.board_label.config(text=' '.join(all_cards))
    
    def reset_simulation(self):
        """Reset the simulation to the beginning."""
        self.simulation_state = {
            'current_street': 'preflop',
            'action_index': 0,
            'is_playing': False
        }
        self.actions_text.delete(1.0, tk.END)
        self.board_label.config(text="")
    
    def analyze_hand(self):
        """Analyze the current hand."""
        if not self.current_hand:
            messagebox.showwarning("No Hand", "Please select a hand to analyze.")
            return
        
        # Create analysis window
        analysis_window = tk.Toplevel(self)
        analysis_window.title("Hand Analysis")
        analysis_window.geometry("600x400")
        
        # Analysis text
        analysis_text = tk.Text(analysis_window, wrap=tk.WORD, font=("Arial", 11))
        analysis_scrollbar = ttk.Scrollbar(analysis_window, orient=tk.VERTICAL,
                                          command=analysis_text.yview)
        analysis_text.config(yscrollcommand=analysis_scrollbar.set)
        
        analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Generate analysis
        analysis = self.generate_hand_analysis()
        analysis_text.insert(tk.END, analysis)
    
    def generate_hand_analysis(self) -> str:
        """Generate analysis text for the current hand."""
        if not self.current_hand:
            return "No hand selected for analysis."
        
        hand = self.current_hand
        analysis = f"""📊 HAND ANALYSIS
{'='*50}

🎯 Hand: {hand.metadata.name}
📂 Category: {hand.metadata.subcategory}
💰 Pot Size: ${hand.metadata.pot_size:.2f}
⭐ Difficulty: {hand.metadata.difficulty_rating}/5
📅 Date: {hand.metadata.date or 'Unknown'}

🎭 Players Involved:
{', '.join(hand.metadata.players_involved) or 'Players not specified'}

📝 Description:
{hand.metadata.description or 'No description available'}

🏷️ Tags:
{', '.join(hand.metadata.tags) if hand.metadata.tags else 'No tags'}

📚 Study Notes:
{hand.metadata.study_notes or 'No study notes available'}

📈 Learning Points:
• Analyze decision-making at each street
• Consider pot odds and implied odds
• Review position and stack sizes
• Evaluate betting patterns and sizing
• Compare actual play with GTO strategy

💡 Questions to Consider:
• What range should each player have at each street?
• Are the bet sizes optimal for the situation?
• How does position influence the decision-making?
• What are the key decision points in this hand?

🎯 Practice Suggestions:
• Replay this hand multiple times
• Try different decision paths
• Calculate pot odds at key decision points
• Consider how stack sizes affect play
"""

        if hand.metadata.last_reviewed:
            analysis += f"\n📅 Last Reviewed: {hand.metadata.last_reviewed}"
        
        return analysis


class EnhancedHandsReviewPanel(ttk.Frame):
    """Enhanced hands review panel with categorized view."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize database
        self.hands_db = ComprehensiveHandsDatabase()
        self.tags_manager = UserTaggedHandsManager()
        
        # UI state
        self.current_category = HandCategory.LEGENDARY
        self.current_hands: List[ParsedHand] = []
        self.selected_hand: Optional[ParsedHand] = None
        self.current_filter_tag = ""
        
        # Font configuration
        self.font_size = 16  # Default size, will be updated by main GUI
        
        self.setup_ui()
        self.load_all_hands()
    
    def setup_ui(self):
        """Setup the enhanced UI."""
        # Main container with horizontal split
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for categories and hands list
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel for hand simulation
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=2)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
        # Apply initial font size
        self.update_font_size(self.font_size)
    
    def setup_left_panel(self, parent):
        """Setup the left panel with categories and hands list."""
        # Title
        self.title_label = ttk.Label(parent, text="🎯 Hands Review Center")
        self.title_label.pack(pady=(0, 15))
        
        # Categories frame
        categories_frame = ttk.LabelFrame(parent, text="📂 Categories")
        categories_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Category buttons
        button_frame = ttk.Frame(categories_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.legendary_btn = ttk.Button(button_frame, text="🏆 Legendary Hands",
                                       command=lambda: self.switch_category(HandCategory.LEGENDARY))
        self.legendary_btn.pack(fill=tk.X, pady=2)
        
        self.practice_btn = ttk.Button(button_frame, text="📚 Practice Sessions",
                                      command=lambda: self.switch_category(HandCategory.PRACTICE))
        self.practice_btn.pack(fill=tk.X, pady=2)
        
        self.tagged_btn = ttk.Button(button_frame, text="🏷️ Tagged & Important",
                                    command=lambda: self.switch_category(HandCategory.TAGGED))
        self.tagged_btn.pack(fill=tk.X, pady=2)
        
        # Stats display
        self.stats_label = ttk.Label(categories_frame, text="")
        self.stats_label.pack(pady=5)
        
        # Search and filter frame
        filter_frame = ttk.LabelFrame(parent, text="🔍 Search & Filter")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search entry
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        search_btn = ttk.Button(search_frame, text="🔍", width=3,
                               command=self.perform_search)
        search_btn.pack(side=tk.RIGHT)
        
        # Tag filter
        tag_frame = ttk.Frame(filter_frame)
        tag_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(tag_frame, text="Tag:").pack(side=tk.LEFT)
        self.tag_filter_var = tk.StringVar()
        self.tag_filter_combo = ttk.Combobox(tag_frame, textvariable=self.tag_filter_var,
                                            state="readonly", width=15)
        self.tag_filter_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.tag_filter_combo.bind('<<ComboboxSelected>>', self.on_tag_filter_change)
        
        clear_filter_btn = ttk.Button(tag_frame, text="Clear", width=6,
                                     command=self.clear_filters)
        clear_filter_btn.pack(side=tk.RIGHT)
        
        # Hands list frame
        hands_frame = ttk.LabelFrame(parent, text="📋 Hands List")
        hands_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Hands listbox with scrollbar
        list_frame = ttk.Frame(hands_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.hands_listbox = tk.Listbox(list_frame)
        hands_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                       command=self.hands_listbox.yview)
        self.hands_listbox.config(yscrollcommand=hands_scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hands_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.hands_listbox.bind('<<ListboxSelect>>', self.on_hand_select)
        
        # Hand actions frame
        actions_frame = ttk.Frame(hands_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tag_hand_btn = ttk.Button(actions_frame, text="🏷️ Tag Hand",
                                      command=self.tag_selected_hand)
        self.tag_hand_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.favorite_btn = ttk.Button(actions_frame, text="⭐ Favorite",
                                      command=self.toggle_favorite)
        self.favorite_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(actions_frame, text="🔄 Refresh",
                                     command=self.refresh_hands)
        self.refresh_btn.pack(side=tk.RIGHT)
    
    def setup_right_panel(self, parent):
        """Setup the right panel with hand simulation."""
        self.simulation_panel = HandSimulationPanel(parent)
        self.simulation_panel.pack(fill=tk.BOTH, expand=True)
    
    def load_all_hands(self):
        """Load all hands from all sources."""
        try:
            # Load hands from database
            self.hands_by_category = self.hands_db.load_all_hands()
            
            # Update UI
            self.update_tag_filter_options()
            self.switch_category(self.current_category)
            self.update_stats_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hands: {str(e)}")
    
    def switch_category(self, category: HandCategory):
        """Switch to a different category."""
        self.current_category = category
        self.current_hands = self.hands_by_category.get(category, [])
        
        # Update button states
        self.update_category_button_states()
        
        # Clear filters and update list
        self.clear_filters()
        self.update_hands_list()
    
    def update_category_button_states(self):
        """Update the visual state of category buttons."""
        # Reset all buttons
        for btn in [self.legendary_btn, self.practice_btn, self.tagged_btn]:
            btn.state(['!pressed'])
        
        # Highlight current category
        if self.current_category == HandCategory.LEGENDARY:
            self.legendary_btn.state(['pressed'])
        elif self.current_category == HandCategory.PRACTICE:
            self.practice_btn.state(['pressed'])
        elif self.current_category == HandCategory.TAGGED:
            self.tagged_btn.state(['pressed'])
    
    def update_hands_list(self):
        """Update the hands listbox."""
        self.hands_listbox.delete(0, tk.END)
        
        if not self.current_hands:
            return
        
        for i, hand in enumerate(self.current_hands):
            # Create display string
            display_text = self.create_hand_display_text(hand)
            self.hands_listbox.insert(tk.END, display_text)
    
    def create_hand_display_text(self, hand: ParsedHand) -> str:
        """Create display text for a hand in the list."""
        # Base info
        name = hand.metadata.name
        pot = f"${hand.metadata.pot_size:.0f}" if hand.metadata.pot_size > 0 else ""
        
        # Category prefix
        if hand.metadata.category == HandCategory.LEGENDARY:
            prefix = "🏆"
        elif hand.metadata.category == HandCategory.PRACTICE:
            prefix = "📚"
        else:
            prefix = "🏷️"
        
        # Favorite indicator
        favorite = "⭐" if hand.metadata.is_favorite else ""
        
        # Difficulty
        difficulty = "●" * hand.metadata.difficulty_rating
        
        # Tags (first 2)
        tags = list(hand.metadata.tags)[:2]
        tag_str = f"[{', '.join(tags)}]" if tags else ""
        
        # Combine elements
        parts = [prefix, name]
        if pot:
            parts.append(pot)
        if favorite:
            parts.append(favorite)
        if difficulty:
            parts.append(difficulty)
        if tag_str:
            parts.append(tag_str)
        
        return " ".join(parts)
    
    def update_tag_filter_options(self):
        """Update the tag filter combobox options."""
        all_tags = self.tags_manager.get_all_tags()
        tag_options = ["All Tags"] + sorted(list(all_tags))
        self.tag_filter_combo['values'] = tag_options
        self.tag_filter_combo.set("All Tags")
    
    def update_stats_display(self):
        """Update the category statistics display."""
        stats = self.hands_db.get_category_stats()
        current_stats = stats.get(self.current_category.value, {})
        
        total = current_stats.get('total_hands', 0)
        favorites = current_stats.get('favorites', 0)
        avg_difficulty = current_stats.get('avg_difficulty', 0)
        
        stats_text = f"{total} hands • {favorites} favorites • Difficulty: {avg_difficulty:.1f}/5"
        self.stats_label.config(text=stats_text)
    
    def on_hand_select(self, event):
        """Handle hand selection."""
        selection = self.hands_listbox.curselection()
        if selection and self.current_hands:
            index = selection[0]
            if index < len(self.current_hands):
                self.selected_hand = self.current_hands[index]
                
                # Load hand in simulation panel
                self.simulation_panel.load_hand(self.selected_hand)
                
                # Mark as reviewed
                if self.selected_hand.metadata.id:
                    self.tags_manager.mark_reviewed(self.selected_hand.metadata.id)
    
    def on_search_change(self, event):
        """Handle search text change."""
        # Perform search with a small delay to avoid too many searches
        self.after(300, self.perform_search)
    
    def perform_search(self):
        """Perform search on current hands."""
        query = self.search_var.get().strip()
        
        if not query:
            self.current_hands = self.hands_by_category.get(self.current_category, [])
        else:
            self.current_hands = self.hands_db.search_hands(query, self.current_category)
        
        self.apply_tag_filter()
        self.update_hands_list()
    
    def on_tag_filter_change(self, event):
        """Handle tag filter change."""
        self.apply_tag_filter()
    
    def apply_tag_filter(self):
        """Apply tag filter to current hands."""
        tag = self.tag_filter_var.get()
        
        if not tag or tag == "All Tags":
            # No filtering
            return
        
        # Filter hands by tag
        filtered_hands = []
        for hand in self.current_hands:
            if tag in hand.metadata.tags:
                filtered_hands.append(hand)
        
        self.current_hands = filtered_hands
        self.update_hands_list()
    
    def clear_filters(self):
        """Clear all filters."""
        self.search_var.set("")
        self.tag_filter_var.set("All Tags")
        self.current_hands = self.hands_by_category.get(self.current_category, [])
        self.update_hands_list()
    
    def tag_selected_hand(self):
        """Tag the selected hand."""
        if not self.selected_hand:
            messagebox.showwarning("No Selection", "Please select a hand to tag.")
            return
        
        # Create tagging dialog
        self.show_tagging_dialog()
    
    def show_tagging_dialog(self):
        """Show the hand tagging dialog."""
        if not self.selected_hand:
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Tag Hand")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Hand info
        ttk.Label(dialog, text=f"Tagging: {self.selected_hand.metadata.name}",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Tags entry
        tag_frame = ttk.Frame(dialog)
        tag_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(tag_frame, text="Tags (comma-separated):").pack(anchor=tk.W)
        tag_entry = ttk.Entry(tag_frame, width=40)
        tag_entry.pack(fill=tk.X, pady=2)
        
        # Pre-fill existing tags
        existing_tags = ', '.join(self.selected_hand.metadata.tags)
        tag_entry.insert(0, existing_tags)
        
        # Notes
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        ttk.Label(notes_frame, text="Study Notes:").pack(anchor=tk.W)
        notes_text = tk.Text(notes_frame, height=6, wrap=tk.WORD)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Pre-fill existing notes
        notes_text.insert(tk.END, self.selected_hand.metadata.study_notes)
        
        # Options frame
        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Favorite checkbox
        favorite_var = tk.BooleanVar(value=self.selected_hand.metadata.is_favorite)
        favorite_check = ttk.Checkbutton(options_frame, text="Mark as Favorite",
                                        variable=favorite_var)
        favorite_check.pack(anchor=tk.W)
        
        # Difficulty scale
        ttk.Label(options_frame, text="Difficulty (1-5):").pack(anchor=tk.W, pady=(10, 2))
        difficulty_var = tk.IntVar(value=self.selected_hand.metadata.difficulty_rating)
        difficulty_scale = ttk.Scale(options_frame, from_=1, to=5, orient=tk.HORIZONTAL,
                                    variable=difficulty_var)
        difficulty_scale.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_tags():
            tags = [tag.strip() for tag in tag_entry.get().split(',') if tag.strip()]
            notes = notes_text.get(1.0, tk.END).strip()
            is_favorite = favorite_var.get()
            difficulty = int(difficulty_var.get())
            
            # Save tags
            self.tags_manager.tag_hand(
                self.selected_hand.metadata.id,
                tags, notes, is_favorite, difficulty
            )
            
            # Update hand metadata
            self.selected_hand.metadata.tags = set(tags)
            self.selected_hand.metadata.study_notes = notes
            self.selected_hand.metadata.is_favorite = is_favorite
            self.selected_hand.metadata.difficulty_rating = difficulty
            
            # Refresh UI
            self.update_tag_filter_options()
            self.update_hands_list()
            
            dialog.destroy()
            messagebox.showinfo("Success", "Hand tagged successfully!")
        
        ttk.Button(button_frame, text="Save", command=save_tags).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def toggle_favorite(self):
        """Toggle favorite status of selected hand."""
        if not self.selected_hand:
            messagebox.showwarning("No Selection", "Please select a hand to favorite.")
            return
        
        # Toggle favorite status
        current_favorite = self.selected_hand.metadata.is_favorite
        new_favorite = not current_favorite
        
        # Update tags manager
        existing_tags = list(self.selected_hand.metadata.tags)
        self.tags_manager.tag_hand(
            self.selected_hand.metadata.id,
            existing_tags,
            self.selected_hand.metadata.study_notes,
            new_favorite,
            self.selected_hand.metadata.difficulty_rating
        )
        
        # Update metadata
        self.selected_hand.metadata.is_favorite = new_favorite
        
        # Refresh display
        self.update_hands_list()
        
        status = "favorited" if new_favorite else "unfavorited"
        messagebox.showinfo("Success", f"Hand {status}!")
    
    def refresh_hands(self):
        """Refresh all hands data."""
        self.load_all_hands()
    
    def update_font_size(self, new_size: int):
        """Update font size for all components."""
        self.font_size = new_size
        
        # Main title (larger, bold)
        title_font = ("Arial", int(new_size * 1.2), "bold")
        self.title_label.config(font=title_font)
        
        # Stats label (smaller)
        stats_font = ("Arial", int(new_size * 0.8))
        self.stats_label.config(font=stats_font)
        
        # Hands listbox
        listbox_font = ("Arial", int(new_size * 0.9))
        self.hands_listbox.config(font=listbox_font)
        
        # Update simulation panel font size
        if hasattr(self, 'simulation_panel'):
            self.simulation_panel.update_font_size(new_size)
