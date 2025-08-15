"""
GTO Simulation Panel

This module provides the main panel for GTO simulation where all players
are GTO bots. It includes session settings, game controls, and the poker
table display.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.flexible_poker_state_machine import GameConfig
from core.session_logger import SessionLogger
from core.gui_models import THEME, FONTS
from utils.sound_manager import SoundManager
from core.bot_session_state_machine import GTOBotSession
from ui.components.bot_session_widget import GTOSessionWidget


class GTOSimulationPanel(ttk.Frame):
    """
    Main panel for GTO simulation.
    
    This panel:
    - Provides session configuration (players, stack size, blinds)
    - Hosts the GTO poker game widget
    - Manages simulation session lifecycle
    - Shows learning insights and statistics
    """
    
    def __init__(self, parent, logger: Optional[SessionLogger] = None, **kwargs):
        """Initialize the GTO simulation panel."""
        super().__init__(parent, **kwargs)
        
        # Initialize attributes
        self.logger = logger
        self.gto_bot_session: Optional[GTOBotSession] = None
        self.gto_game_widget: Optional[GTOSessionWidget] = None
        
        # Session configuration
        self.num_players_var = tk.IntVar(value=6)
        self.initial_stack_var = tk.DoubleVar(value=1000.0)
        self.small_blind_var = tk.DoubleVar(value=5.0)
        self.big_blind_var = tk.DoubleVar(value=10.0)
        
        # Initialize GTO-specific attributes
        self.gto_bot_session = None
        self.gto_game_widget = None
        self.game_placeholder = None
        self.game_container = None
        self.session_active = False
        
        # Initialize sound manager for GTO simulation
        self.sound_manager = SoundManager(test_mode=False)
        
        # Initialize session statistics
        self.hands_played_var = tk.IntVar(value=0)
        self.total_decisions_var = tk.IntVar(value=0)
        self.avg_pot_size_var = tk.DoubleVar(value=0.0)
        
        # Font size control - will be set by main GUI
        self.current_font_size = 12  # Default, will be updated by update_font_size
        
        # Initialize UI
        self._setup_ui()
        
        # Log panel creation
        if self.logger:
            self.logger.log_system("INFO", "GTO_SIMULATION_PANEL", 
                                 "GTO Simulation Panel initialized")
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Configure grid weights for 70/30 split - use aggressive weights
        self.grid_rowconfigure(0, weight=10)  # Poker table area (70%)
        self.grid_rowconfigure(1, weight=1)   # Bottom control strip (30%)
        self.grid_columnconfigure(0, weight=1)

        # Top area: Poker table placeholder
        self._setup_poker_table_area()

        # Bottom area: Control strip
        self._setup_bottom_control_strip()
    
    def _setup_poker_table_area(self):
        """Setup the poker table area."""
        # Create a frame for the poker table
        table_frame = ttk.Frame(self)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 0))

        # Create game container for the game widget
        self.game_container = ttk.Frame(table_frame)
        self.game_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for table_frame
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Configure grid weights for the game container
        self.game_container.grid_rowconfigure(0, weight=1)
        self.game_container.grid_columnconfigure(0, weight=1)
        
        # Game area placeholder (will be replaced by GTO game widget)
        self.game_placeholder = ttk.Label(
            self.game_container, 
            text="Click 'Start Session' to begin GTO simulation",
            font=(FONTS["large"][0], self.current_font_size + 4, "bold"),
            foreground=THEME["text_secondary"]
        )
        self.game_placeholder.grid(row=0, column=0, sticky="nsew")

    def _setup_bottom_control_strip(self):
        """Setup the professional bottom control panel following practice session layout."""
        # Professional bottom panel with theme colors
        bottom_frame = tk.Frame(
            self, bg="#1E232A", relief="flat", bd=0  # Dark Slate background
        )
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # Add top border for separation
        separator = tk.Frame(bottom_frame, height=2, bg=THEME["border"])
        separator.pack(fill=tk.X, pady=(0, 0))  # Ultra-compact separator

        # Main panel content
        content_frame = tk.Frame(bottom_frame, relief="flat", bd=0)
        content_frame.pack(fill="both", expand=True, padx=16, pady=1)  # Minimal pady
        content_frame.configure(bg="#1E232A")

        # Configure grid weights for the three columns
        # New layout: Decision History (left), GTO Explanation (middle), Settings (right)
        content_frame.grid_columnconfigure(0, weight=3, minsize=300)  # Decision History (left)
        content_frame.grid_columnconfigure(1, weight=4, minsize=360)  # GTO Explanation (middle)
        content_frame.grid_columnconfigure(2, weight=2, minsize=160)  # Session Settings (right)
        content_frame.grid_rowconfigure(0, weight=1, minsize=15)  # Ultra-compact height

        # === LEFT: Decision History (with scrollbar) ===
        history_frame = tk.Frame(content_frame, bg="#1E232A")
        history_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=2)
        self._setup_decision_history_area(history_frame)

        # === MIDDLE: GTO Decision Explanation Area ===
        explanation_frame = tk.Frame(content_frame, bg="#1E232A")
        explanation_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=2)
        self._setup_gto_explanation_area(explanation_frame)

        # === RIGHT: Session Settings ===
        settings_frame = tk.Frame(content_frame, bg="#1E232A")
        settings_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=2)  # Further reduced padding
        self._setup_session_settings_area(settings_frame)
    
    def _setup_gto_explanation_area(self, parent):
        """Setup GTO decision explanation area."""
        # Title
        title_label = tk.Label(
            parent,
            text="GTO Decision Explanation",
            bg="#1E232A",
            fg="#EAECEE",
            font=(FONTS["header"][0], self.current_font_size + 2, "bold")
        )
        title_label.pack(pady=(0, 8))

        # Create container with rounded appearance
        explanation_container = tk.Frame(
            parent,
            bg="#2B3845",  # Muted Navy Gray background
            relief="flat",
            bd=1,
            highlightbackground="#3A4B5C",  # Subtle border
            highlightthickness=1,
        )
        explanation_container.pack(fill="both", expand=True, padx=6, pady=1)  # Minimal pady

        # GTO Decision Explanation text widget with professional styling
        self.gto_explanation_text = tk.Text(
            explanation_container,
            font=(FONTS["main"][0], self.current_font_size),
            bg="#2B3845",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            height=5,
            wrap="word",
            padx=8,
            pady=4,
            insertwidth=0,
            selectbackground="#4A90E2",
            selectforeground="#FFFFFF",
            highlightcolor="#4A90E2",
            highlightthickness=1,
        )
        self.gto_explanation_text.pack(fill="both", expand=True)

        # Configure text alignment and spacing
        self.gto_explanation_text.tag_configure("center", justify="center")
        self.gto_explanation_text.tag_configure("vpad", spacing1=4, spacing3=4)

        # Initialize with welcome message
        self._add_gto_explanation("Welcome to GTO Simulation! Start a session to begin.")
    
    def _setup_decision_history_area(self, parent):
        """Setup decision history area with vertical scrollbar and click-to-explain."""
        title_label = tk.Label(
            parent,
            text="Decision History",
            bg="#1E232A",
            fg="#EAECEE",
            font=(FONTS["header"][0], self.current_font_size + 2, "bold")
        )
        title_label.pack(pady=(0, 8))

        container = tk.Frame(parent, bg="#2B3845", relief="flat", bd=1,
                              highlightbackground="#3A4B5C", highlightthickness=1)
        container.pack(fill="both", expand=True, padx=6, pady=1)

        # Scrollbar + Listbox for actions
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
        self.decision_listbox = tk.Listbox(
            container,
            yscrollcommand=scrollbar.set,
            bg="#2B3845",
            fg="#FFFFFF",
            selectbackground="#4A90E2",
            selectforeground="#FFFFFF",
            font=(FONTS["main"][0], self.current_font_size),
            activestyle="none",
            relief="flat",
            bd=0,
        )
        scrollbar.config(command=self.decision_listbox.yview)
        self.decision_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,0), pady=4)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Map listbox indices to decision records
        self._decision_records = []
        self.decision_listbox.bind('<<ListboxSelect>>', self._on_history_select)

        # Start empty; enable when first record is added
        self.decision_listbox.delete(0, tk.END)
        self.decision_listbox.config(state=tk.DISABLED)
    
    def _setup_session_settings_area(self, parent):
        """Setup session settings area."""
        # Title
        title_label = tk.Label(
            parent,
            text="Session Settings",
            bg="#1E232A",
            fg="#EAECEE",
            font=(FONTS["header"][0], self.current_font_size + 2, "bold")
        )
        title_label.pack(pady=(0, 8))

        # Create container with rounded appearance
        settings_container = tk.Frame(
            parent,
            bg="#2B3845",  # Muted Navy Gray background
            relief="flat",
            bd=1,
            highlightbackground="#3A4B5C",  # Subtle border
            highlightthickness=1,
        )
        settings_container.pack(fill="both", expand=True, padx=6, pady=1)  # Minimal pady

        # Settings content frame
        settings_content = tk.Frame(settings_container, bg="#2B3845")
        settings_content.pack(fill="both", expand=True, padx=8, pady=2)  # Minimal pady

        # Players setting
        players_frame = tk.Frame(settings_content, bg="#2B3845")
        players_frame.pack(fill=tk.X, pady=(0, 6))  # Reduced pady from 8 to 6
        
        tk.Label(
            players_frame,
            text="Players:",
            bg="#2B3845",
            fg="#EAECEE",
            font=(FONTS["main"][0], self.current_font_size)
        ).pack(anchor=tk.W)
        
        players_spinbox = ttk.Spinbox(
            players_frame,
            from_=2, to=9,
            textvariable=self.num_players_var,
            width=8,
            style="SkyBlue.TSpinbox"
        )
        players_spinbox.pack(fill=tk.X)

        # Initial stack size
        stack_frame = tk.Frame(settings_content, bg="#2B3845")
        stack_frame.pack(fill=tk.X, pady=(0, 6))  # Reduced pady from 8 to 6
        
        tk.Label(
            stack_frame,
            text="Stack ($):",
            bg="#2B3845",
            fg="#EAECEE",
            font=(FONTS["main"][0], self.current_font_size)
        ).pack(anchor=tk.W)
        
        stack_spinbox = ttk.Spinbox(
            stack_frame,
            from_=100.0, to=10000.0,
            increment=100.0,
            textvariable=self.initial_stack_var,
            width=8,
            style="SkyBlue.TSpinbox"
        )
        stack_spinbox.pack(fill=tk.X)

        # Blinds
        blinds_frame = tk.Frame(settings_content, bg="#2B3845")
        blinds_frame.pack(fill=tk.X, pady=(0, 6))  # Reduced pady from 8 to 6
        
        tk.Label(
            blinds_frame,
            text="SB/BB ($):",
            bg="#2B3845",
            fg="#EAECEE",
            font=(FONTS["main"][0], self.current_font_size)
        ).pack(anchor=tk.W)
        
        blinds_inner = tk.Frame(blinds_frame, bg="#2B3845")
        blinds_inner.pack(fill=tk.X)
        
        sb_spinbox = ttk.Spinbox(
            blinds_inner,
            from_=1.0, to=100.0,
            increment=1.0,
            textvariable=self.small_blind_var,
            width=6,
            style="SkyBlue.TSpinbox"
        )
        sb_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            blinds_inner,
            text="/",
            bg="#2B3845",
            fg="#EAECEE",
            font=(FONTS["main"][0], self.current_font_size)
        ).pack(side=tk.LEFT, padx=2)
        
        bb_spinbox = ttk.Spinbox(
            blinds_inner,
            from_=2.0, to=200.0,
            increment=1.0,
            textvariable=self.big_blind_var,
            width=6,
            style="SkyBlue.TSpinbox"
        )
        bb_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action buttons
        buttons_frame = tk.Frame(settings_content, bg="#2B3845")
        buttons_frame.pack(fill=tk.X, pady=(12, 0))  # Reduced top pady from 16 to 12
        
        # Simplified button layout: 4 buttons in a row
        # 1. Start a Session (toggles to Stop Session when active)
        self.start_session_button = ttk.Button(
            buttons_frame,
            text="Start a Session",
            command=self._toggle_session,
            style="Primary.TButton"
        )
        self.start_session_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # 2. Next
        self.next_action_button = ttk.Button(
            buttons_frame,
            text="Next",
            command=self._next_action,
            style="Primary.TButton"
        )
        self.next_action_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # 3. Auto Play
        self.auto_play_button = ttk.Button(
            buttons_frame,
            text="Auto Play",
            command=self._auto_play,
            style="Primary.TButton"
        )
        self.auto_play_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # 4. New Hand
        self.new_hand_button = ttk.Button(
            buttons_frame,
            text="New Hand",
            command=self._start_new_hand,
            state=tk.DISABLED,
            style="Primary.TButton"
        )
        self.new_hand_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _update_button_states(self):
        """Update button states based on current game state."""
        if hasattr(self, 'session_active') and self.session_active:
            # Session is active - enable game control buttons
            self.next_action_button.config(state=tk.NORMAL)
            self.auto_play_button.config(state=tk.NORMAL)
            self.new_hand_button.config(state=tk.NORMAL)
            # Update start session button text
            self.start_session_button.config(text="Stop Session")
        else:
            # No active session - disable game control buttons
            self.next_action_button.config(state=tk.DISABLED)
            self.auto_play_button.config(state=tk.DISABLED)
            self.new_hand_button.config(state=tk.DISABLED)
            # Update start session button text
            self.start_session_button.config(text="Start a Session")
    
    def _check_hand_completion(self):
        """Check if the current hand is complete and update button states accordingly."""
        if not hasattr(self, 'gto_bot_session') or not self.gto_bot_session:
            return
            
        try:
            # Check if hand is complete
            if self.gto_state_machine.is_hand_complete():
                # Hand is complete - disable Next and Auto Play, enable New Hand
                self.next_action_button.config(state=tk.DISABLED)
                self.auto_play_button.config(state=tk.DISABLED)
                self.new_hand_button.config(state=tk.NORMAL)
                self._add_gto_explanation("🎯 Hand complete! Press 'New Hand' to continue.")
            else:
                # Hand is still in progress - enable Next and Auto Play
                self.next_action_button.config(state=tk.NORMAL)
                self.auto_play_button.config(state=tk.NORMAL)
                self.new_hand_button.config(state=tk.NORMAL)
                
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"Error checking hand completion: {e}")
    
    def _toggle_session(self):
        """Toggle between starting and stopping a session."""
        print("🔥 DEBUG: _toggle_session called!")
        if hasattr(self, 'logger'):
            self.logger.log_system("DEBUG", "GTO_SIMULATION_PANEL", "Toggle session button clicked")
        
        if not hasattr(self, 'session_active') or not self.session_active:
            print("🔥 DEBUG: Starting session...")
            self._start_session()
        else:
            print("🔥 DEBUG: Stopping session...")
            self._stop_session()
    
    def _start_session(self):
        """Start a new GTO simulation session."""
        print("🔥 DEBUG: _start_session method started")
        try:
            # Get settings from UI
            print("🔥 DEBUG: Getting UI settings...")
            num_players = int(self.num_players_var.get())
            initial_stack = float(self.initial_stack_var.get())
            small_blind = float(self.small_blind_var.get())
            big_blind = float(self.big_blind_var.get())
            print(f"🔥 DEBUG: Settings - players: {num_players}, stack: {initial_stack}, blinds: {small_blind}/{big_blind}")
            
            # Create game config
            print("🔥 DEBUG: Creating GameConfig...")
            from core.flexible_poker_state_machine import GameConfig
            config = GameConfig(
                num_players=num_players,
                starting_stack=initial_stack,
                small_blind=small_blind,
                big_blind=big_blind,
                test_mode=False
            )
            print("🔥 DEBUG: GameConfig created successfully")
            
            # Create unified GTO bot session
            print("🔥 DEBUG: Creating GTOBotSession...")
            from core.bot_session_state_machine import GTOBotSession
            self.gto_bot_session = GTOBotSession(config, mode="live")
            print("🔥 DEBUG: GTOBotSession created successfully")
            
            # Set sound manager
            print("🔥 DEBUG: Setting sound manager...")
            if hasattr(self, 'sound_manager'):
                self.gto_bot_session.set_sound_manager(self.sound_manager)
            print("🔥 DEBUG: Sound manager set successfully")
            
            # Create unified bot session widget
            print("🔥 DEBUG: Creating GTOSessionWidget...")
            from ui.components.bot_session_widget import GTOSessionWidget
            self.gto_game_widget = GTOSessionWidget(
                self.game_container,
                self.gto_bot_session
            )
            print("🔥 DEBUG: GTOSessionWidget created successfully")
            
            # Replace placeholder with actual poker table
            print("🔥 DEBUG: Replacing placeholder...")
            if self.game_placeholder:
                self.game_placeholder.grid_remove()
            self.gto_game_widget.grid(row=0, column=0, sticky="nsew")
            print("🔥 DEBUG: Widget gridded successfully")
            
            # Start the bot session
            print("🔥 DEBUG: Starting bot session...")
            success = self.gto_bot_session.start_session()
            print(f"🔥 DEBUG: Bot session start result: {success}")
            if success:
                print("🔥 DEBUG: Session started successfully, updating UI...")
                self.session_active = True
                self._update_button_states()
                self._add_gto_explanation("🎯 GTO Session started! Press 'Next' to begin the simulation.")
                print("🔥 DEBUG: Session active flag set and explanation added")
                
                # Update poker widget to show initial state
                if hasattr(self, 'gto_game_widget'):
                    print("🔥 DEBUG: Updating game widget display...")
                    self.gto_game_widget._update_display()
                    # Defer one more update so SB/BB chip displays position after canvas layout
                    try:
                        self.after(150, self.gto_game_widget._update_display)
                    except Exception:
                        pass
                    print("🔥 DEBUG: Game widget display updated")
                print("🔥 DEBUG: Session setup completed successfully!")
            else:
                print("🔥 DEBUG: Session start failed!")
                self._add_gto_explanation("❌ Failed to start GTO session. Please try again.")
                
        except Exception as e:
            self._add_gto_explanation(f"❌ Error starting session: {str(e)}")
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"Session start error: {e}")
    
    def _stop_session(self):
        """Stop the current GTO simulation session."""
        try:
            self.session_active = False
            self._update_button_states()
            self._add_gto_explanation("🛑 GTO Session stopped. Start a new session to continue.")
            
            # Remove poker widget and restore placeholder
            if hasattr(self, 'gto_game_widget') and self.gto_game_widget:
                self.gto_game_widget.grid_remove()
                self.gto_game_widget.destroy()
                self.gto_game_widget = None
            
            # Restore placeholder
            if self.game_placeholder:
                self.game_placeholder.grid(row=0, column=0, sticky="nsew")
            
            # Clear state machine
            if hasattr(self, 'gto_state_machine'):
                del self.gto_state_machine
                
        except Exception as e:
            self._add_gto_explanation(f"❌ Error stopping session: {str(e)}")
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"Session stop error: {e}")
    
    def _next_action(self):
        """Execute the next action in the GTO simulation using unified bot architecture."""
        print("🔥 DEBUG: _next_action called!")
        if hasattr(self, 'logger'):
            self.logger.log_system("DEBUG", "GTO_SIMULATION_PANEL", "Next action button clicked")
            
        if not hasattr(self, 'gto_bot_session') or not self.gto_bot_session:
            self._add_gto_explanation("❌ No active session. Please start a session first.")
            return
            
        try:
            # Execute next bot action using the unified session
            success = self.gto_game_widget.execute_next_action()
            
            if success:
                # Get the decision explanation from the bot session
                explanation = self.gto_bot_session.get_current_explanation()
                if explanation:
                    self._add_gto_explanation(f"🎯 {explanation}")
                
                # Update poker widget to show the action result  
                if hasattr(self, 'gto_game_widget'):
                    self.gto_game_widget._update_display()
                
                # Check if session is now complete
                if self.gto_bot_session.decision_engine.is_session_complete():
                    self._add_gto_explanation("✅ GTO simulation complete!")
                    self.session_active = False
                    self._update_button_states()
                
            else:
                self._add_gto_explanation("❌ Failed to execute action. Please try again.")
                
        except Exception as e:
            self._add_gto_explanation(f"❌ Error executing action: {str(e)}")
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"Action execution error: {e}")
    
    def _auto_play(self):
        """Automatically play through the entire hand."""
        if not hasattr(self, 'gto_bot_session') or not self.gto_bot_session:
            self._add_gto_explanation("❌ No active session. Please start a session first.")
            return
            
        try:
            self._add_gto_explanation("🚀 Auto-playing through the hand...")
            
            # Auto-play function that executes one action per call
            def auto_step():
                try:
                    if self.session_active and hasattr(self, 'gto_game_widget'):
                        success = self.gto_game_widget.execute_next_action()
                        
                        if success:
                            # Get explanation and update display
                            explanation = self.gto_bot_session.get_current_explanation()
                            if explanation:
                                self._add_gto_explanation(f"🎯 {explanation}")
                            
                            # Update display
                            self.gto_game_widget._update_display()
                            
                            # Check if session is complete
                            if not self.gto_bot_session.decision_engine.is_session_complete():
                                # Schedule next step after delay
                                self.after(800, auto_step)  # 800ms delay between actions
                            else:
                                self._add_gto_explanation("✅ Auto-play completed!")
                                self.session_active = False
                                self._update_button_states()
                        else:
                            self._add_gto_explanation("❌ Auto-play stopped due to error.")
                except Exception as e:
                    self._add_gto_explanation(f"❌ Auto-play error: {str(e)}")
            
            # Start auto-play
            auto_step()
            
            self._add_gto_explanation("✅ Auto-play complete!")
            
        except Exception as e:
            self._add_gto_explanation(f"❌ Error in auto-play: {str(e)}")
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"Auto-play error: {e}")
    
    def _start_new_hand(self):
        """Start a new hand within the current session."""
        if not hasattr(self, 'gto_bot_session') or not self.gto_bot_session:
            self._add_gto_explanation("❌ No active session. Please start a session first.")
            return
            
        try:
            # Reset the bot session for a new hand
            self.gto_bot_session.reset_session()
            success = self.gto_bot_session.start_session()
            
            if success:
                self._add_gto_explanation("🃏 New hand started! Press 'Next' to begin.")
                
                # Reactivate Next and Auto Play buttons for the new hand
                self.next_action_button.config(state=tk.NORMAL)
                self.auto_play_button.config(state=tk.NORMAL)
                self.new_hand_button.config(state=tk.NORMAL)
                
                # Update poker widget to show new hand
                if hasattr(self, 'gto_game_widget'):
                    self.gto_game_widget._update_display()
            else:
                self._add_gto_explanation("❌ Failed to start new hand. Please try again.")
                
        except Exception as e:
            self._add_gto_explanation(f"❌ Error starting new hand: {str(e)}")
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_system("ERROR", "GTO_SIMULATION_PANEL", f"New hand error: {e}")
    

    
    def _add_gto_explanation(self, message: str):
        """Add a message to the GTO explanation area."""
        if hasattr(self, "gto_explanation_text"):
            self.gto_explanation_text.config(state=tk.NORMAL)
            self.gto_explanation_text.delete(1.0, tk.END)
            self.gto_explanation_text.insert(tk.END, message)
            self.gto_explanation_text.config(state=tk.DISABLED)
            self.gto_explanation_text.see(tk.END)
    
    def _add_decision_record(self, record: dict):
        """Add a structured decision record to the history listbox and map it."""
        if not hasattr(self, 'decision_listbox'):
            return
        # Enable if this is the first insert
        if self.decision_listbox.cget('state') == tk.DISABLED:
            self.decision_listbox.config(state=tk.NORMAL)
            self.decision_listbox.delete(0, tk.END)
        action = getattr(record.get('action'), 'value', str(record.get('action'))).upper()
        amount = record.get('amount', 0.0)
        player = record.get('player_name', f"P{record.get('player_index', 0)+1}")
        position = record.get('position', '')
        street = record.get('street', '')
        if hasattr(street, 'value'):
            street = street.value
        line = f"{player} ({position}) - {action}"
        if amount and amount > 0:
            line += f" ${int(amount)}"
        if street:
            line += f" [{street}]"
        self.decision_listbox.insert(tk.END, line)
        self._decision_records.append(record)
        self.decision_listbox.see(tk.END)

    def _on_history_select(self, event=None):
        """When a history item is selected, show its detailed explanation."""
        if not hasattr(self, '_decision_records'):
            return
        try:
            sel = self.decision_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            if 0 <= idx < len(self._decision_records):
                explanation = self._decision_records[idx].get('explanation', '')
                self._add_gto_explanation(explanation or "")
        except Exception:
            pass
    
    def _add_game_message(self, message: str):
        """Add a message to the game message area."""
        if hasattr(self, "game_message_text"):
            self.game_message_text.config(state="normal")
            
            # Get current content and split into lines
            current_content = self.game_message_text.get("1.0", tk.END).strip()
            lines = current_content.split("\n") if current_content else []
            
            # Add new message
            lines.append(message)
            
            # Keep only the last 2 lines
            lines = lines[-2:]
            
            # Ensure we always have exactly 2 lines
            while len(lines) < 2:
                lines.insert(0, "")
            
            # Clear and set new content
            self.game_message_text.delete("1.0", tk.END)
            content = "\n".join(lines)
            self.game_message_text.insert("1.0", content)
            
            # Apply centering and vertical padding
            self.game_message_text.tag_add("center", "1.0", tk.END)
            self.game_message_text.tag_add("vpad", "1.0", tk.END)
            
            self.game_message_text.config(state="disabled")









    # Statistics display is now integrated into the session settings area






        

    
    def _create_settings_overlay(self):
        """Create a settings overlay panel on the top right."""
        # Create overlay frame
        overlay_frame = tk.Frame(self, bg="#1E232A", relief="flat", bd=1)
        overlay_frame.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Settings label frame
        settings_frame = ttk.LabelFrame(
            overlay_frame,
            text="Session Settings",
            padding=8,
            style="Dark.TLabelframe"
        )
        settings_frame.pack()
        
        # Number of players
        players_frame = ttk.Frame(settings_frame)
        players_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            players_frame,
            text="Players:",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        players_spinbox = ttk.Spinbox(
            players_frame,
            from_=2, to=9,
            textvariable=self.num_players_var,
            width=8,
            style="SkyBlue.TSpinbox"
        )
        players_spinbox.pack(fill=tk.X)
        
        # Initial stack size
        stack_frame = ttk.Frame(settings_frame)
        stack_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            stack_frame,
            text="Stack ($):",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        stack_spinbox = ttk.Spinbox(
            stack_frame,
            from_=100.0, to=10000.0,
            increment=100.0,
            textvariable=self.initial_stack_var,
            width=8,
            style="SkyBlue.TSpinbox"
        )
        stack_spinbox.pack(fill=tk.X)
        
        # Blinds
        blinds_frame = ttk.Frame(settings_frame)
        blinds_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            blinds_frame,
            text="SB/BB ($):",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        blinds_inner = ttk.Frame(blinds_frame)
        blinds_inner.pack(fill=tk.X)
        
        sb_spinbox = ttk.Spinbox(
            blinds_inner,
            from_=1.0, to=100.0,
            increment=1.0,
            textvariable=self.small_blind_var,
            width=6,
            style="SkyBlue.TSpinbox"
        )
        sb_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            blinds_inner,
            text="/",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(side=tk.LEFT, padx=2)
        
        bb_spinbox = ttk.Spinbox(
            blinds_inner,
            from_=2.0, to=200.0,
            increment=1.0,
            textvariable=self.big_blind_var,
            width=6,
            style="SkyBlue.TSpinbox"
        )
        bb_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    

    
    def _create_left_panel(self, parent):
        """Create the left panel with session settings and controls."""
        left_frame = ttk.LabelFrame(
            parent, 
            text="Session Settings", 
            padding=10,
            style="Dark.TLabelframe"
        )
        
        # Number of players
        players_frame = ttk.Frame(left_frame)
        players_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            players_frame, 
            text="Number of Players:",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        players_spinbox = ttk.Spinbox(
            players_frame, 
            from_=2, to=9, 
            textvariable=self.num_players_var, 
            width=10,
            style="SkyBlue.TSpinbox"
        )
        players_spinbox.pack(fill=tk.X, pady=(5, 0))
        
        # Initial stack size
        stack_frame = ttk.Frame(left_frame)
        stack_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            stack_frame, 
            text="Initial Stack Size ($):",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        stack_spinbox = ttk.Spinbox(
            stack_frame, 
            from_=100.0, to=10000.0, 
            increment=100.0, 
            textvariable=self.initial_stack_var, 
            width=10,
            style="SkyBlue.TSpinbox"
        )
        stack_spinbox.pack(fill=tk.X, pady=(5, 0))
        
        # Small blind
        sb_frame = ttk.Frame(left_frame)
        sb_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            sb_frame, 
            text="Small Blind ($):",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        sb_spinbox = ttk.Spinbox(
            sb_frame, 
            from_=1.0, to=100.0, 
            increment=1.0, 
            textvariable=self.small_blind_var, 
            width=10,
            style="SkyBlue.TSpinbox"
        )
        sb_spinbox.pack(fill=tk.X, pady=(5, 0))
        
        # Big blind
        bb_frame = ttk.Frame(left_frame)
        bb_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            bb_frame, 
            text="Big Blind ($):",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(anchor=tk.W)
        
        bb_spinbox = ttk.Spinbox(
            bb_frame, 
            from_=2.0, to=200.0, 
            increment=1.0, 
            textvariable=self.big_blind_var, 
            width=10,
            style="SkyBlue.TSpinbox"
        )
        bb_spinbox.pack(fill=tk.X, pady=(5, 0))
        
        # Control buttons
        controls_frame = ttk.Frame(left_frame)
        controls_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.start_session_button = ttk.Button(
            controls_frame, 
            text="Start Session", 
            command=self._start_session,
            style="Primary.TButton"
        )
        self.start_session_button.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_session_button = ttk.Button(
            controls_frame, 
            text="Stop Session", 
            command=self._stop_session, 
            state=tk.DISABLED,
            style="Primary.TButton"
        )
        self.stop_session_button.pack(fill=tk.X, pady=(0, 5))
        
        self.new_hand_button = ttk.Button(
            controls_frame, 
            text="New Hand", 
            command=self._start_new_hand, 
            state=tk.DISABLED,
            style="Primary.TButton"
        )
        self.new_hand_button.pack(fill=tk.X, pady=(0, 5))
        
        # Statistics
        stats_frame = ttk.LabelFrame(
            left_frame, 
            text="Session Statistics", 
            padding=10,
            style="Dark.TLabelframe"
        )
        stats_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Hands played
        hands_frame = ttk.Frame(stats_frame)
        hands_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(
            hands_frame, 
            text="Hands Played:",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(side=tk.LEFT)
        ttk.Label(
            hands_frame, 
            textvariable=self.hands_played_var,
            font=FONTS["main"],
            foreground=THEME["text_gold"]
        ).pack(side=tk.RIGHT)
        
        # Total decisions
        decisions_frame = ttk.Frame(stats_frame)
        decisions_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(
            decisions_frame, 
            text="Total Decisions:",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(side=tk.LEFT)
        ttk.Label(
            decisions_frame, 
            textvariable=self.total_decisions_var,
            font=FONTS["main"],
            foreground=THEME["text_gold"]
        ).pack(side=tk.RIGHT)
        
        # Average pot size
        pot_frame = ttk.Frame(stats_frame)
        pot_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(
            pot_frame, 
            text="Avg Pot Size:",
            font=FONTS["main"],
            foreground=THEME["text"]
        ).pack(side=tk.LEFT)
        ttk.Label(
            pot_frame, 
            textvariable=self.avg_pot_size_var,
            font=FONTS["main"],
            foreground=THEME["text_gold"]
        ).pack(side=tk.RIGHT)
        
        return left_frame
    
    def _create_right_panel(self, parent):
        """Create the right panel with the game area."""
        right_frame = ttk.LabelFrame(
            parent, 
            text="GTO Simulation Game", 
            padding=10,
            style="Dark.TLabelframe"
        )
        
        # Create a container frame for the game area
        self.game_container = ttk.Frame(right_frame)
        self.game_container.pack(expand=True, fill=tk.BOTH)
        
        # Configure grid geometry manager for the game container
        self.game_container.grid_columnconfigure(0, weight=1)
        self.game_container.grid_rowconfigure(0, weight=1)
        
        # Game area placeholder (will be replaced by GTO game widget)
        self.game_placeholder = ttk.Label(
            self.game_container, 
            text="Click 'Start Session' to begin GTO simulation",
            font=(FONTS["large"][0], self.current_font_size + 4, "bold"),
            foreground=THEME["text_secondary"]
        )
        self.game_placeholder.grid(row=0, column=0, sticky="nsew")
        
        return right_frame
    
    # Removed duplicate _add_gto_explanation method - defined earlier in file
    
    # Removed duplicate _add_game_message method - defined earlier in file
    

    

    
    # Removed duplicate _auto_play method - defined earlier in file
    
    def _pause_auto_play(self):
        """Pause auto-play."""
        # TODO: Implement pause functionality
        self._update_game_message("Auto-play not yet implemented")
    
    def _validate_settings(self) -> bool:
        """Validate the session settings."""
        num_players = self.num_players_var.get()
        initial_stack = self.initial_stack_var.get()
        small_blind = self.small_blind_var.get()
        big_blind = self.big_blind_var.get()
        
        if num_players < 2 or num_players > 9:
            messagebox.showerror("Invalid Settings", "Number of players must be between 2 and 9.")
            return False
        
        if initial_stack <= 0:
            messagebox.showerror("Invalid Settings", "Initial stack size must be positive.")
            return False
        
        if small_blind <= 0 or big_blind <= 0:
            messagebox.showerror("Invalid Settings", "Blind amounts must be positive.")
            return False
        
        if big_blind <= small_blind:
            messagebox.showerror("Invalid Settings", "Big blind must be greater than small blind.")
            return False
        
        if initial_stack < big_blind * 10:
            messagebox.showerror("Invalid Settings", 
                               "Initial stack should be at least 10x the big blind for realistic play.")
            return False
        
        return True
    
    def _get_game_parent(self):
        """Get the parent widget for the game area."""
        # Return the game container directly
        return self.game_container
    
    def _replace_game_placeholder(self):
        """Replace the game placeholder with the GTO game widget."""
        if self.game_placeholder and self.gto_game_widget:
            # Place the game widget in the game container using grid
            self.gto_game_widget.grid(row=0, column=0, sticky="nsew")
            
            # Hide the placeholder
            self.game_placeholder.grid_remove()
    
    def _restore_game_placeholder(self):
        """Restore the game placeholder."""
        if self.game_placeholder:
            self.game_placeholder.grid(row=0, column=0, sticky="nsew")
    
    def _update_game_message(self, message: str, message_type: str = "info"):
        """Update the game message area instead of showing popups."""
        self._add_gto_explanation(message)

    def _reset_statistics(self):
        """Reset session statistics."""
        self.hands_played_var.set(0)
        self.total_decisions_var.set(0)
        self.avg_pot_size_var.set(0.0)
    
    def update_statistics(self, decision_count: int, pot_size: float):
        """Update session statistics."""
        self.total_decisions_var.set(self.total_decisions_var.get() + decision_count)
        
        # Update average pot size
        hands_played = self.hands_played_var.get()
        if hands_played > 0:
            current_avg = self.avg_pot_size_var.get()
            new_avg = ((current_avg * (hands_played - 1)) + pot_size) / hands_played
            self.avg_pot_size_var.set(round(new_avg, 2))
    
    def get_session_summary(self) -> dict:
        """Get a summary of the current session."""
        return {
            'num_players': self.num_players_var.get(),
            'initial_stack': self.initial_stack_var.get(),
            'small_blind': self.small_blind_var.get(),
            'big_blind': self.big_blind_var.get(),
            'hands_played': self.hands_played_var.get(),
            'total_decisions': self.total_decisions_var.get(),
            'avg_pot_size': self.avg_pot_size_var.get(),
            'session_active': self.gto_state_machine is not None
        }
    
    def update_font_size(self, font_size: int):
        """Update font size for all text elements in the panel."""
        self.current_font_size = font_size
        
        # Update game message area font
        if hasattr(self, 'gto_explanation_text'):
            self.gto_explanation_text.configure(
                font=(FONTS["main"][0], font_size)
            )
        if hasattr(self, 'decision_history_text'):
            self.decision_history_text.configure(
                font=(FONTS["main"][0], font_size)
            )
        
        # Update statistics display fonts
        if hasattr(self, 'stats_frame'):
            for child in self.stats_frame.winfo_children():
                if isinstance(child, tk.Label):
                    if 'title' in str(child.cget('text')).lower():
                        # Title label
                        child.configure(
                            font=(FONTS["header"][0], font_size + 2, "bold")
                        )
                    else:
                        # Regular labels
                        child.configure(
                            font=(FONTS["small"][0], font_size - 2)
                        )
        
        # Update settings overlay fonts
        if hasattr(self, 'settings_frame'):
            for child in self.settings_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(
                        font=(FONTS["main"][0], font_size)
                    )
        
        # Update game placeholder font
        if hasattr(self, 'game_placeholder'):
            self.game_placeholder.configure(
                font=(FONTS["large"][0], font_size + 4, "bold")
            )
        
        # Update GTO game widget font if it exists
        if hasattr(self, 'gto_game_widget') and self.gto_game_widget:
            if hasattr(self.gto_game_widget, 'update_font_size'):
                self.gto_game_widget.update_font_size(font_size)
