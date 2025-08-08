#!/usr/bin/env python3
"""
Redesigned Hands Review Panel

A modern two-pane interface for reviewing poker hands:
- Left pane: Hand selection and categorization
- Right pane: Interactive study and step-by-step simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from core.phh_converter import PracticeHandsPHHManager
from core.hands_database import ComprehensiveHandsDatabase, HandCategory


class HandSimulationEngine:
    """Engine for step-by-step hand simulation."""
    
    def __init__(self):
        self.current_hand = None
        self.current_step = 0
        self.simulation_steps = []
        self.hand_state = {}
        
    def load_hand(self, hand):
        """Load a hand for simulation."""
        self.current_hand = hand
        self.current_step = 0
        self.simulation_steps = self._generate_simulation_steps(hand)
        self.hand_state = self._initialize_hand_state(hand)
        
    def _initialize_hand_state(self, hand):
        """Initialize the hand state."""
        return {
            'street': 'preflop',
            'pot': 0,
            'board': [],
            'active_players': [p for p in hand.players if not p.get('folded_preflop', False)],
            'current_player': 0,
            'betting_round': 'preflop'
        }
    
    def _generate_simulation_steps(self, hand):
        """Generate simulation steps from hand data."""
        steps = []
        
        # Step 1: Deal hole cards
        steps.append({
            'type': 'deal_cards',
            'description': 'Dealing hole cards to players',
            'players': hand.players or []
        })
        
        # Step 2: Post blinds
        steps.append({
            'type': 'post_blinds',
            'description': 'Players post blinds',
            'action': 'Small and big blinds posted'
        })
        
        # Add more steps based on hand data
        # For now, we'll use a simplified simulation
        for street in ['preflop', 'flop', 'turn', 'river']:
            steps.append({
                'type': 'betting_round',
                'street': street,
                'description': f'{street.title()} betting round',
                'action': f'Players make decisions on {street}'
            })
            
        steps.append({
            'type': 'showdown',
            'description': 'Showdown and winner determination',
            'action': 'Hand concludes'
        })
        
        return steps
    
    def next_step(self):
        """Advance to the next simulation step."""
        if self.current_step < len(self.simulation_steps):
            step = self.simulation_steps[self.current_step]
            self.current_step += 1
            return step
        return None
    
    def previous_step(self):
        """Go back to the previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            return self.simulation_steps[self.current_step]
        return None
    
    def reset(self):
        """Reset simulation to the beginning."""
        self.current_step = 0
        if self.current_hand:
            self.hand_state = self._initialize_hand_state(self.current_hand)


class StudyAnalysisPanel:
    """Panel for hand analysis and study tools."""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.current_hand = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the study analysis interface."""
        # Analysis tabs
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Equity analysis tab
        equity_frame = ttk.Frame(notebook)
        notebook.add(equity_frame, text="🎯 Equity Analysis")
        
        self.equity_text = tk.Text(equity_frame, wrap=tk.WORD, height=8)
        self.equity_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Strategy analysis tab
        strategy_frame = ttk.Frame(notebook)
        notebook.add(strategy_frame, text="🧠 Strategy Notes")
        
        self.strategy_text = tk.Text(strategy_frame, wrap=tk.WORD, height=8)
        self.strategy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Key decisions tab
        decisions_frame = ttk.Frame(notebook)
        notebook.add(decisions_frame, text="🔑 Key Decisions")
        
        self.decisions_text = tk.Text(decisions_frame, wrap=tk.WORD, height=8)
        self.decisions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_hand_analysis(self, hand):
        """Load analysis for a specific hand."""
        self.current_hand = hand
        self._update_equity_analysis()
        self._update_strategy_analysis()
        self._update_decisions_analysis()
        
    def _update_equity_analysis(self):
        """Update equity analysis display."""
        if not self.current_hand:
            return
            
        analysis = f"""🎯 EQUITY ANALYSIS
{'='*40}

Hand: {self.current_hand.metadata.name}

📊 Pre-flop Equity:
• This analysis shows the theoretical winning chances for each player
• Based on hole cards and position

🃏 Hole Card Strength:
"""
        
        for i, player in enumerate(self.current_hand.players or []):
            name = player.get('name', f'Player {i+1}')
            cards = player.get('cards', [])
            folded = player.get('folded_preflop', False)
            
            if not folded and cards:
                # Simple hand strength analysis
                if len(cards) >= 2:
                    strength = self._analyze_hand_strength(cards[:2])
                    analysis += f"• {name}: {cards[:2]} - {strength}\n"
        
        analysis += """
🎲 Post-flop Equity:
• Equity changes dramatically with community cards
• Consider draws, made hands, and blockers

💡 Study Tips:
• Compare actual decisions with GTO recommendations
• Analyze bet sizing and frequency
• Consider opponent's likely range
"""
        
        self.equity_text.delete(1.0, tk.END)
        self.equity_text.insert(1.0, analysis)
        
    def _analyze_hand_strength(self, cards):
        """Analyze basic hand strength."""
        if len(cards) < 2:
            return "Unknown"
            
        # Simple hand strength analysis
        ranks = [card[0] for card in cards]
        suits = [card[1] for card in cards]
        
        if ranks[0] == ranks[1]:
            return f"Pocket pair ({ranks[0]}s) - Strong"
        elif suits[0] == suits[1]:
            return f"Suited cards - Moderate"
        elif abs(ord(ranks[0]) - ord(ranks[1])) <= 1:
            return "Connected cards - Moderate"
        else:
            return "Offsuit cards - Weak to Moderate"
            
    def _update_strategy_analysis(self):
        """Update strategy analysis display."""
        if not self.current_hand:
            return
            
        strategy = f"""🧠 STRATEGY ANALYSIS
{'='*40}

Hand: {self.current_hand.metadata.name}

🎯 Key Strategic Concepts:

📋 Position Analysis:
• Early position players should play tight ranges
• Late position allows for wider ranges and bluffs
• Button has significant advantage

💰 Pot Odds & Implied Odds:
• Calculate required equity for profitable calls
• Consider future betting rounds (implied odds)
• Factor in reverse implied odds for marginal hands

🎲 Board Texture:
• Dry boards favor strong hands and bluffs
• Wet boards require more caution with marginal hands
• Consider how board affects both ranges

🔄 Opponent Modeling:
• Tight players: Respect their aggression
• Loose players: Value bet wider, bluff less
• Aggressive players: Use their aggression against them

📈 Betting Strategy:
• Value bet for protection and value
• Bluff with blockers and backup equity
• Size bets based on board texture and opponent type

💡 Study Questions:
1. What's the optimal strategy for each position?
2. How does stack depth affect decisions?
3. What are the key decision points in this hand?
"""
        
        self.strategy_text.delete(1.0, tk.END)
        self.strategy_text.insert(1.0, strategy)
        
    def _update_decisions_analysis(self):
        """Update key decisions analysis."""
        if not self.current_hand:
            return
            
        decisions = f"""🔑 KEY DECISIONS ANALYSIS
{'='*40}

Hand: {self.current_hand.metadata.name}

🎯 Critical Decision Points:

This legendary hand showcases several important decision points:

1. 🃏 Pre-flop Action:
   • Opening ranges by position
   • 3-bet/4-bet decisions
   • Stack-to-pot ratio considerations

2. 🎲 Post-flop Play:
   • Continuation betting strategy
   • Check-raise frequencies
   • Bluff-to-value ratios

3. 💰 Sizing Decisions:
   • Bet sizing for value vs bluffs
   • All-in timing and ICM considerations
   • Pot geometry and stack depths

4. 🧠 Mental Game:
   • Pressure situations
   • Reading opponent tendencies
   • Variance and bankroll management

🎓 Learning Objectives:
• Understand the reasoning behind each major decision
• Identify alternative lines and their EV
• Apply concepts to similar future situations

🔍 Analysis Tools:
• Use poker solvers for GTO comparisons
• Study population tendencies vs GTO
• Practice similar spots in your own game

💡 Reflection Questions:
1. What was the most critical decision in this hand?
2. How would different bet sizes change the outcome?
3. What can we learn about opponent's range and strategy?
"""
        
        self.decisions_text.delete(1.0, tk.END)
        self.decisions_text.insert(1.0, decisions)


class RedesignedHandsReviewPanel(ttk.Frame):
    """Redesigned hands review panel with two-pane layout."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.hands_database = ComprehensiveHandsDatabase()
        self.practice_phh_manager = PracticeHandsPHHManager()
        self.simulation_engine = HandSimulationEngine()
        
        # Data
        self.legendary_hands = []
        self.practice_hands = []
        self.current_hand = None
        self.current_mode = "simulation"  # "simulation" or "study"
        
        # Font configuration
        self.font_size = 16
        
        self.setup_ui()
        self.load_data()
        self.update_font_size(self.font_size)
        
        # Set initial mode
        self.set_mode("simulation")
        
    def setup_ui(self):
        """Setup the redesigned two-pane interface."""
        # Main container with horizontal split
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: Hand selection
        self.setup_left_pane(main_paned)
        
        # Right pane: Study/Simulation
        self.setup_right_pane(main_paned)
        
        # Set initial pane weights (30% left, 70% right)
        # Note: PanedWindow weights are set when adding panes, not on the widget itself
        
    def setup_left_pane(self, parent):
        """Setup the left pane for hand selection."""
        left_frame = ttk.Frame(parent)
        parent.add(left_frame, weight=30)
        
        # Title
        self.title_label = ttk.Label(left_frame, text="🎯 Hands Review")
        self.title_label.pack(pady=(0, 10))
        
        # Category selection
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="Legendary Hands")
        self.category_combo = ttk.Combobox(
            category_frame, 
            textvariable=self.category_var,
            values=["Legendary Hands", "Practice Hands"],
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Subcategory selection (for legendary hands)
        subcategory_frame = ttk.Frame(left_frame)
        subcategory_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(subcategory_frame, text="Filter:").pack(side=tk.LEFT)
        self.subcategory_var = tk.StringVar(value="All")
        self.subcategory_combo = ttk.Combobox(
            subcategory_frame,
            textvariable=self.subcategory_var,
            state="readonly",
            width=15
        )
        self.subcategory_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.subcategory_combo.bind('<<ComboboxSelected>>', self.on_subcategory_change)
        
        # Hands list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(list_frame, text="Select Hand to Review:").pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.hands_listbox = tk.Listbox(list_container)
        hands_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.hands_listbox.yview)
        self.hands_listbox.configure(yscrollcommand=hands_scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hands_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hands_listbox.bind('<<ListboxSelect>>', self.on_hand_select)
        
        # Hand info preview
        info_frame = ttk.LabelFrame(left_frame, text="Hand Info")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hand_info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        self.hand_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mode selection buttons (removed - duplicates with tab headers)
        
    def setup_right_pane(self, parent):
        """Setup the right pane for study/simulation."""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=70)
        
        # Mode-specific content
        self.right_notebook = ttk.Notebook(right_frame)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Simulation tab
        self.setup_simulation_tab()
        
        # Study tab
        self.setup_study_tab()
        
    def setup_simulation_tab(self):
        """Setup the simulation tab with embedded practice session."""
        sim_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(sim_frame, text="🎮 Hand Simulation")
        
        # Simulation controls at the top
        controls_frame = ttk.Frame(sim_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Control buttons
        self.start_simulation_btn = ttk.Button(controls_frame, text="▶ Start Simulation", command=self.start_hand_simulation)
        self.start_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_action_btn = ttk.Button(controls_frame, text="Next Action ▶", command=self.next_action, state="disabled")
        self.next_action_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.auto_play_btn = ttk.Button(controls_frame, text="🚀 Auto Play", command=self.toggle_auto_play, state="disabled")
        self.auto_play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_simulation_btn = ttk.Button(controls_frame, text="🔄 Reset", command=self.reset_hand_simulation)
        self.reset_simulation_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status indicator
        self.simulation_status_label = ttk.Label(controls_frame, text="Select a hand to simulate")
        self.simulation_status_label.pack(side=tk.RIGHT)
        
        # Practice session container
        self.practice_container = ttk.Frame(sim_frame)
        self.practice_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Initialize practice session (will be created when needed)
        self.practice_session = None
        self.poker_state_machine = None
        self.auto_play_active = False
        
        # Create placeholder message
        self.placeholder_label = ttk.Label(
            self.practice_container, 
            text="🎯 Select a legendary hand from the left pane\nand click 'Start Simulation' to begin!",
            justify=tk.CENTER
        )
        self.placeholder_label.pack(expand=True)
        
    def setup_study_tab(self):
        """Setup the study tab."""
        study_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(study_frame, text="📚 Hand Study")
        
        # Create study analysis panel
        self.study_panel = StudyAnalysisPanel(study_frame)
        self.study_panel.frame.pack(fill=tk.BOTH, expand=True)
        
    def load_data(self):
        """Load all hands data."""
        self.load_legendary_hands()
        self.load_practice_hands()
        self.update_hands_list()
        
    def load_legendary_hands(self):
        """Load legendary hands from database."""
        try:
            # Load all hands and get legendary category
            hands_by_category = self.hands_database.load_all_hands()
            self.legendary_hands = hands_by_category.get(HandCategory.LEGENDARY, [])
            print(f"✅ Loaded {len(self.legendary_hands)} legendary hands")
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            self.legendary_hands = []
            
    def load_practice_hands(self):
        """Load practice hands."""
        try:
            # Load practice hands (simplified for now)
            self.practice_hands = []
            print(f"✅ Loaded {len(self.practice_hands)} practice hands")
        except Exception as e:
            print(f"❌ Error loading practice hands: {e}")
            self.practice_hands = []
            
    def update_hands_list(self):
        """Update the hands list based on current category."""
        self.hands_listbox.delete(0, tk.END)
        
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        
        if category == "Legendary Hands":
            hands = self.legendary_hands
            if subcategory != "All":
                hands = [h for h in hands if h.metadata.subcategory == subcategory]
                
            # Update subcategory options
            subcategories = ["All"] + list(set(h.metadata.subcategory for h in self.legendary_hands if h.metadata.subcategory))
            self.subcategory_combo['values'] = subcategories
            
            for hand in hands:
                display_text = f"{hand.metadata.name}"
                if len(display_text) > 50:
                    display_text = display_text[:47] + "..."
                self.hands_listbox.insert(tk.END, display_text)
                
        elif category == "Practice Hands":
            self.subcategory_combo['values'] = ["All"]
            for i, hand in enumerate(self.practice_hands):
                self.hands_listbox.insert(tk.END, f"Practice Hand {i+1}")
                
    def on_category_change(self, event=None):
        """Handle category change."""
        self.update_hands_list()
        
    def on_subcategory_change(self, event=None):
        """Handle subcategory change."""
        self.update_hands_list()
        
    def on_hand_select(self, event=None):
        """Handle hand selection."""
        selection = self.hands_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        category = self.category_var.get()
        
        if category == "Legendary Hands":
            subcategory = self.subcategory_var.get()
            hands = self.legendary_hands
            if subcategory != "All":
                hands = [h for h in hands if h.metadata.subcategory == subcategory]
            
            if index < len(hands):
                self.current_hand = hands[index]
        elif category == "Practice Hands":
            if index < len(self.practice_hands):
                self.current_hand = self.practice_hands[index]
                
        if self.current_hand:
            self.update_hand_info()
            self.load_hand_for_simulation()
            self.study_panel.load_hand_analysis(self.current_hand)
            
    def update_hand_info(self):
        """Update the hand info preview."""
        if not self.current_hand:
            self.hand_info_text.delete(1.0, tk.END)
            return
            
        metadata = self.current_hand.metadata
        players = self.current_hand.players or []
        
        info = f"""🏆 {metadata.name}
        
📅 Date: {metadata.date or 'Unknown'}
💰 Pot: ${metadata.pot_size:.0f}
🎯 Category: {metadata.subcategory or 'Unknown'}

👥 Players ({len(players)}):
"""
        
        for i, player in enumerate(players[:4]):  # Show first 4 players
            name = player.get('name', f'Player {i+1}')
            position = player.get('position', '')
            folded = player.get('folded_preflop', False)
            status = " 🚫" if folded else " ✅"
            info += f"• {name} ({position}){status}\n"
            
        if len(players) > 4:
            info += f"... and {len(players) - 4} more players\n"
            
        self.hand_info_text.delete(1.0, tk.END)
        self.hand_info_text.insert(1.0, info)
        
    def load_hand_for_simulation(self):
        """Prepare hand for simulation (now handled by start_hand_simulation)."""
        # Update status to show hand is ready for simulation
        if self.current_hand:
            self.simulation_status_label.configure(text=f"Ready: {self.current_hand.metadata.name}")
            
    def set_mode(self, mode):
        """Set the current mode (simulation or study)."""
        self.current_mode = mode
        if mode == "simulation":
            self.right_notebook.select(0)
        else:
            self.right_notebook.select(1)
            
    def start_hand_simulation(self):
        """Start simulation of the selected legendary hand."""
        if not self.current_hand:
            messagebox.showwarning("No Hand", "Please select a hand first.")
            return
            
        try:
            # Import practice session components
            from ui.practice_session_ui import PracticeSessionUI
            from core.poker_state_machine import ImprovedPokerStateMachine
            
            # Clear previous session
            if self.practice_session:
                self.practice_session.destroy()
            
            # Hide placeholder
            self.placeholder_label.pack_forget()
            
            # Create practice session UI (it creates its own state machine)
            self.practice_session = PracticeSessionUI(
                self.practice_container, 
                strategy_data={}  # Use empty strategy for simulation
            )
            self.practice_session.pack(fill=tk.BOTH, expand=True)
            
            # Get the state machine from the practice session
            self.poker_state_machine = self.practice_session.state_machine
            
            # Setup the hand with legendary hand data
            self.setup_legendary_hand()
            
            # Update controls
            self.start_simulation_btn.configure(state="disabled")
            self.next_action_btn.configure(state="normal")
            self.auto_play_btn.configure(state="normal")
            self.simulation_status_label.configure(text=f"Simulating: {self.current_hand.metadata.name}")
            
            print(f"✅ Started simulation: {self.current_hand.metadata.name}")
            
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Failed to start simulation: {str(e)}")
            print(f"❌ Simulation start error: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_legendary_hand(self):
        """Setup the poker state machine with legendary hand data."""
        if not self.poker_state_machine or not self.current_hand:
            return
            
        try:
            print(f"🎯 Setting up legendary hand: {self.current_hand.metadata.name}")
            
            # Configure players based on hand data
            players = self.current_hand.players or []
            
            # Ensure we have 6 players
            while len(players) < 6:
                players.append({
                    'name': f'Folded Player {len(players) + 1}',
                    'cards': ['2c', '3d'],
                    'folded_preflop': True,
                    'position': f'Seat {len(players) + 1}',
                    'starting_stack_chips': 100000
                })
            
            # Start a new hand in the state machine
            self.poker_state_machine.start_hand()
            
            # Set up players with their specific cards from the legendary hand
            for i, player_data in enumerate(players[:6]):
                cards = player_data.get('cards', ['2c', '3d'])
                name = player_data.get('name', f'Player {i+1}')
                stack = player_data.get('starting_stack_chips', 100000)
                
                print(f"👤 Setting up player {i+1}: {name} with cards {cards}")
                
                # Get the actual player from the state machine
                if i < len(self.poker_state_machine.players):
                    player = self.poker_state_machine.players[i]
                    player.name = name
                    player.stack = stack
                    player.cards = cards.copy()  # Copy the cards
                    
                    # Mark as folded if specified
                    if player_data.get('folded_preflop', False):
                        player.has_folded = True
                        player.is_active = False
                        print(f"❌ Player {name} marked as folded")
                    else:
                        player.has_folded = False
                        player.is_active = True
                        print(f"✅ Player {name} is active")
            
            # Load the board cards if available
            if hasattr(self.current_hand, 'board') and self.current_hand.board:
                board_cards = []
                if 'flop' in self.current_hand.board:
                    board_cards.extend(self.current_hand.board['flop'])
                if 'turn' in self.current_hand.board:
                    board_cards.append(self.current_hand.board['turn'])
                if 'river' in self.current_hand.board:
                    board_cards.append(self.current_hand.board['river'])
                
                if board_cards:
                    print(f"🃏 Loading board cards: {board_cards}")
                    self.poker_state_machine.game_state.board = board_cards.copy()
            
            # Force a UI update
            if hasattr(self.practice_session, 'update_display'):
                self.practice_session.update_display()
                
            print(f"✅ Legendary hand setup complete: {self.current_hand.metadata.name}")
                
        except Exception as e:
            print(f"❌ Error setting up legendary hand: {e}")
            import traceback
            traceback.print_exc()
    
    def next_action(self):
        """Execute the next action in the simulation."""
        if not self.poker_state_machine:
            messagebox.showwarning("No Simulation", "Please start a simulation first.")
            return
            
        try:
            # Check if game is still active
            if hasattr(self.poker_state_machine, 'state'):
                if self.poker_state_machine.state == "game_over":
                    messagebox.showinfo("Game Complete", "Hand simulation finished!")
                    return
            
            # Get current player
            current_player = self.poker_state_machine.get_action_player()
            if not current_player:
                print("❌ No current player found")
                return
            
            # Use actual legendary hand actions if available
            action_type, amount = self._get_legendary_hand_action(current_player)
            
            # Execute the action using the correct method
            self.poker_state_machine.execute_action(current_player, action_type, amount)
            
            # Update the practice session display
            if self.practice_session and hasattr(self.practice_session, 'update_display'):
                self.practice_session.update_display()
            
            print(f"✅ Action executed: {current_player.name} -> {action_type.name} (${amount})")
                    
        except Exception as e:
            print(f"❌ Error in next action: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Simulation Error", f"Error advancing simulation: {str(e)}")
    
    def _get_legendary_hand_action(self, current_player):
        """Get the next action from the legendary hand data."""
        from core.poker_state_machine import ActionType
        
        # If we have legendary hand data with actions, use it
        if hasattr(self.current_hand, 'actions') and self.current_hand.actions:
            # Get current street
            current_street = self.poker_state_machine.game_state.street.lower()
            
            # Get actions for current street
            street_actions = self.current_hand.actions.get(current_street, [])
            
            # Find the next action for this player
            for action in street_actions:
                actor_index = action.get('actor', 0) - 1  # Convert to 0-based index
                if actor_index < len(self.poker_state_machine.players):
                    actor_player = self.poker_state_machine.players[actor_index]
                    if actor_player.name == current_player.name:
                        action_type_str = action.get('type', 'fold').upper()
                        amount = action.get('amount', 0)
                        
                        # Convert action type string to ActionType enum
                        if action_type_str == 'FOLD':
                            return ActionType.FOLD, 0
                        elif action_type_str == 'CALL':
                            return ActionType.CALL, amount
                        elif action_type_str == 'CHECK':
                            return ActionType.CHECK, 0
                        elif action_type_str == 'BET':
                            return ActionType.BET, amount
                        elif action_type_str == 'RAISE':
                            return ActionType.RAISE, amount
                        elif action_type_str == 'ALL-IN':
                            # ALL-IN is handled as a RAISE with the player's full stack
                            return ActionType.RAISE, amount
        
        # Fallback: Use smart action based on player and situation
        return self._get_smart_fallback_action(current_player)
    
    def _get_smart_fallback_action(self, current_player):
        """Get a smart fallback action when legendary hand data is not available."""
        from core.poker_state_machine import ActionType
        
        # Get main players from the current hand
        main_players = []
        if hasattr(self.current_hand, 'players') and self.current_hand.players:
            main_players = [p.get('name', '') for p in self.current_hand.players[:2]]
        
        # Determine action based on player position
        if current_player.name in main_players or current_player.name in ["Chris Moneymaker", "Sammy Farha", "Phil Ivey", "Tom Dwan"]:
            # Main players (from legendary hand) - usually call or raise
            if self.poker_state_machine.game_state.current_bet > current_player.current_bet:
                return ActionType.CALL, 0
            else:
                return ActionType.CHECK, 0
        else:
            # Other players fold
            return ActionType.FOLD, 0
    
    def toggle_auto_play(self):
        """Toggle automatic play mode."""
        self.auto_play_active = not self.auto_play_active
        
        if self.auto_play_active:
            self.auto_play_btn.configure(text="⏸ Pause")
            self.next_action_btn.configure(state="disabled")
            self.start_auto_play()
        else:
            self.auto_play_btn.configure(text="🚀 Auto Play")
            self.next_action_btn.configure(state="normal")
    
    def start_auto_play(self):
        """Start automatic play with delays."""
        if self.auto_play_active and self.poker_state_machine:
            self.next_action()
            # Schedule next action after delay
            self.after(2000, self.start_auto_play)  # 2 second delay
    
    def reset_hand_simulation(self):
        """Reset the current hand simulation."""
        try:
            # Clear the practice session
            if self.practice_session:
                self.practice_session.destroy()
                self.practice_session = None
            
            # Clear state machine
            self.poker_state_machine = None
            self.auto_play_active = False
            
            # Show placeholder
            self.placeholder_label.pack(expand=True)
            
            # Reset controls
            self.start_simulation_btn.configure(state="normal")
            self.next_action_btn.configure(state="disabled") 
            self.auto_play_btn.configure(state="disabled", text="🚀 Auto Play")
            self.simulation_status_label.configure(text="Select a hand to simulate")
            
            print("✅ Simulation reset")
            
        except Exception as e:
            print(f"❌ Error resetting simulation: {e}")
            import traceback
            traceback.print_exc()

        
    def update_font_size(self, new_size):
        """Update font size for all components."""
        self.font_size = new_size
        
        # Main title
        title_font = ("Arial", int(new_size * 1.2), "bold")
        self.title_label.config(font=title_font)
        
        # Text components
        text_font = ("Arial", int(new_size * 0.9))
        listbox_font = ("Arial", int(new_size * 0.8))
        
        self.hands_listbox.config(font=listbox_font)
        self.hand_info_text.config(font=text_font)
        
        # Update study panel fonts if it exists
        if hasattr(self, 'study_panel'):
            study_font = ("Arial", int(new_size * 0.8))
            self.study_panel.equity_text.config(font=study_font)
            self.study_panel.strategy_text.config(font=study_font)
            self.study_panel.decisions_text.config(font=study_font)
            
        # Update practice session fonts if it exists
        if hasattr(self, 'practice_session') and self.practice_session:
            if hasattr(self.practice_session, 'update_font_size'):
                self.practice_session.update_font_size(new_size)
