import tkinter as tk
from tkinter import ttk
import uuid
from typing import Dict, Any, Optional, List

# New UI Architecture imports
from ..state.actions import *
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer
from ..services.hands_repository import HandsRepository, HandsFilter, StudyMode
from ..services.fpsm_adapter import FpsmEventAdapter
from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager
from ..tableview.renderer_pipeline import RendererPipeline
from ..tableview.components.pot_display import PotDisplay
from ..tableview.components.seats import Seats
from ..tableview.components.community import Community
from ..tableview.components.table_felt import TableFelt
from ..tableview.components.dealer_button import DealerButton
from ..tableview.components.bet_display import BetDisplay
from ..tableview.components.action_indicator import ActionIndicator

# Import enhanced button components
try:
    from ..components.enhanced_button import PrimaryButton, SecondaryButton
except ImportError:
    # Fallback to basic buttons if enhanced buttons not available
    PrimaryButton = SecondaryButton = tk.Button

# Core imports with fallbacks
try:
    from ...core.hand_model import Hand
    from ...core.hand_model_decision_engine import HandModelDecisionEngine
    from ...core.bot_session_state_machine import HandsReviewBotSession
    from ...core.flexible_poker_state_machine import GameConfig
    from ...core.session_logger import get_session_logger
except ImportError:
    print("⚠️  Core modules not available - using fallbacks")
    class Hand:
        def __init__(self, data):
            if isinstance(data, dict):
                self.hand_id = data.get('hand_id', 'Unknown')
                self.players = data.get('players', [])
                self.pot_size = data.get('pot_size', 0)
                self.small_blind = data.get('small_blind', 5)
                self.big_blind = data.get('big_blind', 10)
                self.community_cards = data.get('community_cards', [])
                self.dealer = data.get('dealer', 0)
                self.__dict__.update(data)
        
        @classmethod
        def from_dict(cls, data): 
            return cls(data)
    class HandModelDecisionEngine:
        def __init__(self, hand): pass
        def is_session_complete(self): return False
    class HandsReviewBotSession:
        def __init__(self, config, decision_engine): 
            self.session_active = False
            self.decision_engine = decision_engine
        def start_session(self): return True
        def set_preloaded_hand_data(self, data): pass
        def execute_next_bot_action(self): return True
        def is_session_complete(self): return False
        def reset_session(self): pass
    class GameConfig:
        def __init__(self, **kwargs): pass
    def get_session_logger():
        class FallbackLogger:
            def log_system(self, *args, **kwargs): pass
        return FallbackLogger()


class ConcreteHandModelDecisionEngine:
    """Concrete wrapper for HandModelDecisionEngine."""
    
    def __init__(self, hand):
        self.hand = hand
        try:
            if HandModelDecisionEngine and hand:
                self._engine = HandModelDecisionEngine.__new__(HandModelDecisionEngine)
                self._engine.hand = hand
                if hasattr(self._engine, '_organize_actions_by_street'):
                    self._engine.actions_by_street = self._engine._organize_actions_by_street()
                self._engine.current_action_index = 0
                if hasattr(self._engine, '_get_betting_actions'):
                    self._engine.actions_for_replay = self._engine._get_betting_actions()
                    self._engine.total_actions = len(self._engine.actions_for_replay)
                else:
                    self._engine.actions_for_replay = []
                    self._engine.total_actions = 0
            else:
                self._engine = None
        except Exception as e:
            print(f"❌ Error initializing decision engine: {e}")
            self._engine = None
    
    def get_decision(self, player_index: int, game_state):
        if self._engine and hasattr(self._engine, 'get_decision'):
            return self._engine.get_decision(player_index, game_state)
        return {"action": "fold", "amount": 0, "explanation": "Default action", "confidence": 0.5}
    
    def is_session_complete(self):
        if self._engine and hasattr(self._engine, 'is_session_complete'):
            return self._engine.is_session_complete()
        return True
    
    def reset(self):
        if self._engine and hasattr(self._engine, 'reset'):
            self._engine.reset()
    
    def get_session_info(self):
        if self._engine and hasattr(self._engine, 'hand'):
            return {
                "hand_id": getattr(self._engine.hand, 'hand_id', 'Unknown'),
                "total_actions": getattr(self._engine, 'total_actions', 0),
                "current_action": getattr(self._engine, 'current_action_index', 0),
                "engine_type": "HandModelDecisionEngine"
            }
        return {
            "hand_id": "Unknown",
            "total_actions": 0,
            "current_action": 0,
            "engine_type": "Fallback"
        }


class HandsReviewTab(ttk.Frame):
    """Hands Review tab implementing the full PRD requirements."""
    
    def __init__(self, parent, services: ServiceContainer):
        super().__init__(parent)
        self.services = services
        self.session_id = f"hands_review_{uuid.uuid4().hex[:8]}"
        
        # Get app services
        self.event_bus: EventBus = services.get_app("event_bus")
        self.store: Store = services.get_app("store")
        self.theme = services.get_app("theme")
        self.hands_repository: HandsRepository = services.get_app("hands_repository")
        
        # Session state
        self.current_session: Optional[HandsReviewBotSession] = None
        self.session_active = False
        self.fpsm_adapter: Optional[FpsmEventAdapter] = None
        
        # Setup UI
        self.on_mount()
        
        # Subscribe to events and store changes
        self._setup_event_subscriptions()
        self.store.subscribe(self._on_store_change)
        
        # Initialize hands list
        self._refresh_hands_list()
    
    def on_mount(self):
        """Set up the tab layout per PRD design."""
        # Two-column layout: Controls (30%) | Poker Table (70%)
        self.grid_columnconfigure(0, weight=30)  # Library + Filters & Controls  
        self.grid_columnconfigure(1, weight=70)  # Poker Table (bigger)
        self.grid_rowconfigure(0, weight=1)
        
        # Create the two main sections
        self._create_combined_left_section()
        self._create_poker_table_section()
    
    def _create_combined_left_section(self):
        """Create the combined left section with hands library and controls."""
        # Get theme colors
        theme = self.theme.get_theme()
        
        # Main left frame
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2.5), pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=60)  # Hands library gets 60%
        left_frame.grid_rowconfigure(1, weight=40)  # Controls get 40%
        
        # Apply theme colors to main left frame
        try:
            left_frame.configure(background=theme.get("panel.bg", "#111827"))
        except Exception:
            pass
        
        # Create library section at top
        self._create_library_section_in_frame(left_frame)
        
        # Create filters/controls section at bottom
        self._create_filters_section_in_frame(left_frame)
    
    def _create_library_section_in_frame(self, parent):
        """Create the Library section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()
        
        library_frame = ttk.LabelFrame(parent, text="📚 Hands Library", padding=10)
        library_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 2.5))
        
        # Apply theme colors to the frame
        try:
            library_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE")
            )
        except Exception:
            pass  # Fallback to default colors if theming fails
        library_frame.grid_columnconfigure(0, weight=1)
        library_frame.grid_rowconfigure(3, weight=1)  # Hands list gets most space (shifted down due to theme selector)
        
        # Theme selector (at top) - 5 Professional Casino Schemes
        theme_frame = ttk.LabelFrame(library_frame, text="🎨 Professional Casino Themes", padding=5)
        theme_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(0, weight=1)
        
        theme_controls = ttk.Frame(theme_frame)
        theme_controls.grid(row=0, column=0, sticky="ew")
        
        current_theme = self.theme.current_profile_name()
        self.theme_var = tk.StringVar(value=current_theme)
        
        # All available themes from ThemeManager
        all_theme_names = self.theme.names()
        
        # Artistic theme introductions - evocative descriptions for premium UX
        self.THEME_INTROS = {
            # Noir Trio - Artistic Masters
            "Monet Noir": "Cool navy felt and silver trim, evoking moonlit reflections on water. Calm, luminous, and impressionistic in spirit.",
            "Caravaggio Noir": "Stark chiaroscuro: black depths cut by crimson and gold. Dramatic, baroque, for players who like high-contrast tension.",
            "Klimt Royale": "Obsidian and gold with emerald flourishes—luxurious, ornamental, decadent. Feels like sitting at a Viennese palace table.",
            "Whistler Nocturne": "Ethereal midnight blues with pewter accents. Atmospheric and contemplative, like a nocturne painted in shadows.",
            
            # Luxury LV Collection
            "LV Noir": "Deep mahogany felt with antique gold inlay. Timeless luxury with a whisper of Parisian elegance.",
            "Crimson Monogram": "Rich burgundy depths accented by warm gold. Opulent and sophisticated, like a private salon.",
            "Obsidian Emerald": "Dark obsidian base with emerald highlights. Mysterious and powerful, exuding quiet confidence.",
            
            # Classic Professional
            "Emerald Noir": "Classic poker green with dark steel rails. Professional and grounded, perfect for serious grinders.",
            "Royal Indigo": "Deep indigo felt with silver accents. Regal and composed, balancing tradition with modern sophistication.",
            "Crimson Gold": "Wine-dark felt with golden trim. Old-world luxury, the mood of gentlemen's clubs and vintage saloons.",
            
            # Tournament Championship
            "PokerStars Classic Pro": "Iconic tournament green with professional brown rails. The authentic feel of championship poker.",
            "WSOP Championship": "Bold burgundy felt with championship gold rails. The prestige and intensity of the World Series.",
            "Royal Casino Sapphire": "Jewel-like sapphire blues with subtle shimmer. Bright, confident, majestic—fit for royalty.",
            "Emerald Professional": "Rich emerald green with warm brown accents. Timeless casino elegance with professional polish."
        }
        
        # Create display names with emojis for better UX
        theme_display_map = {
            # Painter Collection
            "Monet Noir": "🌙 Monet Noir",
            "Caravaggio Noir": "🎨 Caravaggio Noir",
            "Klimt Royale": "👑 Klimt Royale", 
            "Whistler Nocturne": "🌊 Whistler Nocturne",
            # Luxury LV Collection
            "LV Noir": "💎 LV Noir", 
            "Crimson Monogram": "🏆 Crimson Monogram",
            "Obsidian Emerald": "⚫ Obsidian Emerald",
            # Original Collection
            "Emerald Noir": "🌟 Emerald Noir",
            "Royal Indigo": "🔵 Royal Indigo",
            "Crimson Gold": "🔴 Crimson Gold",
            # Professional Casino
            "PokerStars Classic Pro": "🟢 PokerStars Classic Pro",
            "WSOP Championship": "🏆 WSOP Championship", 
            "Royal Casino Sapphire": "💎 Royal Casino Sapphire",
            "Emerald Professional": "💚 Emerald Professional"
        }
        
        # Create radiobuttons for all themes (4 themes per row for better layout)
        for i, theme_name in enumerate(all_theme_names):
            display_name = theme_display_map.get(theme_name, f"🎨 {theme_name}")
            row = i // 4  # 4 themes per row
            col = i % 4
            radio_btn = ttk.Radiobutton(theme_controls, text=display_name, variable=self.theme_var,
                           value=theme_name, command=self._on_theme_change)
            radio_btn.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=2)
            
            # Bind hover events for artistic theme introductions
            radio_btn.bind("<Enter>", lambda e, theme=theme_name: self._show_theme_intro(theme))
            radio_btn.bind("<Leave>", lambda e: self._show_theme_intro(self.theme_var.get()))
        
        # Artistic Theme Info Panel - shows evocative descriptions (positioned AFTER theme controls)
        info_frame = ttk.Frame(theme_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Theme intro label with elegant styling
        fonts = self.theme.get_fonts()
        intro_font = fonts.get("body", ("Inter", 20, "italic"))
        self.theme_intro_label = tk.Text(info_frame, height=3, wrap=tk.WORD, 
                                        relief="flat", borderwidth=0, 
                                        font=intro_font,
                                        state="disabled", cursor="arrow")
        self.theme_intro_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Show current theme's introduction
        self._show_theme_intro(current_theme)
        
        # Library type selector
        type_frame = ttk.Frame(library_frame)
        type_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        type_frame.grid_columnconfigure(0, weight=1)
        
        self.library_type = tk.StringVar(value="legendary")
        ttk.Radiobutton(type_frame, text="🏆 Legendary", variable=self.library_type, 
                       value="legendary", command=self._on_library_type_change).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(type_frame, text="🤖 Bot Sessions", variable=self.library_type, 
                       value="bot", command=self._on_library_type_change).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(type_frame, text="📥 Imported", variable=self.library_type, 
                       value="imported", command=self._on_library_type_change).grid(row=0, column=2, sticky="w")
        
        # Collections dropdown
        collections_frame = ttk.Frame(library_frame)
        collections_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        collections_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(collections_frame, text="Collection:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.collection_var = tk.StringVar(value="All Hands")
        self.collection_combo = ttk.Combobox(collections_frame, textvariable=self.collection_var, state="readonly")
        self.collection_combo.grid(row=0, column=1, sticky="ew")
        self.collection_combo.bind("<<ComboboxSelected>>", self._on_collection_change)
        
        # Hands listbox
        hands_frame = ttk.Frame(library_frame)
        hands_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        hands_frame.grid_columnconfigure(0, weight=1)
        hands_frame.grid_rowconfigure(0, weight=1)
        
        # Get fonts from theme
        fonts = self.theme.get_fonts()
        body_font = fonts.get("body", ("Consolas", 20))
        
        self.hands_listbox = tk.Listbox(hands_frame, font=body_font, selectmode=tk.SINGLE)
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        self.hands_listbox.bind("<<ListboxSelect>>", self._on_hand_select)
        
        # Apply theme colors to listbox
        try:
            self.hands_listbox.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                selectbackground=theme.get("btn.primaryBg", "#16A34A"),
                selectforeground=theme.get("btn.primaryFg", "#F8FAFC"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE")
            )
        except Exception:
            pass
        
        scrollbar = ttk.Scrollbar(hands_frame, orient="vertical", command=self.hands_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Hand details text (smaller in the combined layout)
        details_frame = ttk.LabelFrame(library_frame, text="Hand Details", padding=5)
        details_frame.grid(row=5, column=0, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)
        
        small_font = fonts.get("small", ("Consolas", 16))
        self.details_text = tk.Text(details_frame, height=4, wrap=tk.WORD, font=small_font)  # Reduced height
        self.details_text.grid(row=0, column=0, sticky="ew")
        
        # Apply theme colors to details text
        try:
            self.details_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE")
            )
        except Exception:
            pass
        
    def _create_filters_section_in_frame(self, parent):
        """Create the Filters & Controls section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()
        
        filters_frame = ttk.LabelFrame(parent, text="🔍 Filters & Study Mode", padding=10)
        filters_frame.grid(row=1, column=0, sticky="nsew", pady=(2.5, 0))
        
        # Apply theme colors to the frame
        try:
            filters_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE")
            )
        except Exception:
            pass
        filters_frame.grid_columnconfigure(0, weight=1)
        
        # Study Mode selector
        study_frame = ttk.LabelFrame(filters_frame, text="Study Mode", padding=5)
        study_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.study_mode = tk.StringVar(value=StudyMode.REPLAY.value)
        ttk.Radiobutton(study_frame, text="🔄 Replay", variable=self.study_mode, 
                       value=StudyMode.REPLAY.value, command=self._on_study_mode_change).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(study_frame, text="📊 Solver Diff", variable=self.study_mode, 
                       value=StudyMode.SOLVER_DIFF.value, command=self._on_study_mode_change).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(study_frame, text="🧠 Recall Quiz", variable=self.study_mode, 
                       value=StudyMode.RECALL_QUIZ.value, command=self._on_study_mode_change).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(study_frame, text="❓ Explain Mistake", variable=self.study_mode, 
                       value=StudyMode.EXPLAIN_MISTAKE.value, command=self._on_study_mode_change).grid(row=3, column=0, sticky="w")
        
        # Filters section
        filter_frame = ttk.LabelFrame(filters_frame, text="Filters", padding=5)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # Position filter
        ttk.Label(filter_frame, text="Position:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.position_var = tk.StringVar(value="All")
        position_combo = ttk.Combobox(filter_frame, textvariable=self.position_var, 
                                    values=["All", "UTG", "MP", "CO", "BTN", "SB", "BB"], state="readonly", width=8)
        position_combo.grid(row=0, column=1, sticky="w", pady=2)
        
        # Stack depth filter
        ttk.Label(filter_frame, text="Stack Depth:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        stack_frame = ttk.Frame(filter_frame)
        stack_frame.grid(row=1, column=1, sticky="w", pady=2)
        self.min_stack = tk.StringVar(value="20")
        self.max_stack = tk.StringVar(value="200")
        ttk.Entry(stack_frame, textvariable=self.min_stack, width=5).grid(row=0, column=0)
        ttk.Label(stack_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(stack_frame, textvariable=self.max_stack, width=5).grid(row=0, column=2)
        ttk.Label(stack_frame, text=" BB").grid(row=0, column=3)
        
        # Pot type filter
        ttk.Label(filter_frame, text="Pot Type:").grid(row=2, column=0, sticky="w", padx=(0, 5))
        self.pot_type_var = tk.StringVar(value="All")
        pot_combo = ttk.Combobox(filter_frame, textvariable=self.pot_type_var,
                               values=["All", "SRP", "3BP", "4BP+"], state="readonly", width=8)
        pot_combo.grid(row=2, column=1, sticky="w", pady=2)
        
        # Search text
        ttk.Label(filter_frame, text="Search:").grid(row=3, column=0, sticky="w", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=3, column=1, sticky="ew", pady=2)
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        # Apply filters button
        ttk.Button(filter_frame, text="Apply Filters", command=self._apply_filters).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Action buttons
        actions_frame = ttk.LabelFrame(filters_frame, text="Actions", padding=5)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        actions_frame.grid_columnconfigure(0, weight=1)
        
        # Load button (main action) - Enhanced primary button
        self.load_btn = PrimaryButton(actions_frame, text="🔥 LOAD HAND", 
                                    command=self._load_selected_hand, 
                                    theme_manager=self.theme)
        self.load_btn.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Enhanced button handles its own styling
        
        # Playback controls
        controls_frame = ttk.Frame(actions_frame)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Enhanced buttons handle their own styling
        
        # Enhanced secondary buttons for controls
        self.next_btn = SecondaryButton(controls_frame, text="Next →", 
                                       command=self._next_action, 
                                       theme_manager=self.theme)
        self.next_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.auto_btn = SecondaryButton(controls_frame, text="Auto", 
                                       command=self._toggle_auto, 
                                       theme_manager=self.theme)
        self.auto_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = SecondaryButton(controls_frame, text="Reset", 
                                        command=self._reset_hand, 
                                        theme_manager=self.theme)
        self.reset_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Enhanced buttons handle their own styling
        
        # Status text
        status_frame = ttk.LabelFrame(filters_frame, text="Status", padding=5)
        status_frame.grid(row=3, column=0, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)
        
        fonts = self.theme.get_fonts()
        small_font = fonts.get("small", ("Consolas", 16))
        self.status_text = tk.Text(status_frame, height=6, wrap=tk.WORD, font=small_font)  # Reduced height
        self.status_text.grid(row=0, column=0, sticky="nsew")
        
        # Apply theme colors to status text
        try:
            self.status_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE")
            )
        except Exception:
            pass
        
    def _create_poker_table_section(self):
        """Create poker table using new UI architecture components (right column)."""
        # Get theme colors for poker table
        theme = self.theme.get_theme()
        
        table_frame = ttk.LabelFrame(self, text="♠️ Poker Table", padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(2.5, 5), pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Apply theme colors to table frame
        try:
            table_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE")
            )
        except Exception:
            pass
        
        # Set up table rendering pipeline with themed canvas
        self.canvas_manager = CanvasManager(table_frame)
        
        # Apply table felt color to canvas
        try:
            self.canvas_manager.canvas.configure(
                bg=theme.get("table.felt", "#1E5B44"),
                highlightthickness=0
            )
        except Exception:
            pass
        self.layer_manager = LayerManager(self.canvas_manager.canvas, self.canvas_manager.overlay)
        
        # Create table components that read from the store
        self.table_components = [
            TableFelt(),         # Background
            Seats(),             # Player seats with cards, stacks, names
            Community(),         # Community cards
            BetDisplay(),        # Current bet amounts
            PotDisplay(),        # Pot amount display
            DealerButton(),      # Dealer button
            ActionIndicator()    # Highlight acting player
        ]
        
        self.renderer_pipeline = RendererPipeline(
            self.canvas_manager, self.layer_manager, self.table_components
        )
        
        # Schedule initial render after the tab is fully set up
        self.after(100, self._initial_render)
    
    def _initial_render(self):
        """Render the poker table initially with default state."""
        try:
            # Force canvas to update its geometry first
            self.canvas_manager.canvas.update_idletasks()
            
            # Get current state or create empty state for initial render
            state = self.store.get_state()
            
            # Make sure we have basic table dimensions set
            if not state.get("table", {}).get("dim"):
                w, h = self.canvas_manager.size()
                if w > 1 and h > 1:
                    self.store.dispatch({
                        "type": SET_TABLE_DIM,
                        "dim": (w, h)
                    })
            
            # Render the table
            self.renderer_pipeline.render_once(self.store.get_state())
            print("🎲 Initial poker table render completed")
            
        except Exception as e:
            print(f"⚠️ Initial render error: {e}")
    
    def _setup_event_subscriptions(self):
        """Subscribe to relevant events."""
        # Subscribe to review:load events as per architecture doc
        self.event_bus.subscribe(
            self.event_bus.topic(self.session_id, "review:load"),
            self._handle_load_hand_event
        )
    
    def _refresh_hands_list(self):
        """Refresh the hands list based on current filters."""
        filtered_hands = self.hands_repository.get_filtered_hands()
        
        # Dispatch to store
        self.store.dispatch({
            "type": SET_REVIEW_HANDS,
            "hands": filtered_hands
        })
        
        # Update UI
        self.hands_listbox.delete(0, tk.END)
        for hand in filtered_hands:
            hand_id = hand.get('hand_id', 'Unknown')
            players_count = len(hand.get('players', []))
            pot_size = hand.get('pot_size', 0)
            display_text = f"{hand_id} | {players_count}p | ${pot_size}"
            self.hands_listbox.insert(tk.END, display_text)
        
        # Update collections
        collections = ["All Hands"] + list(self.hands_repository.get_collections().keys())
        self.collection_combo['values'] = collections
        
        # Update status with workflow guidance
        stats = self.hands_repository.get_stats()
        self._update_status(f"📊 Library: {stats['total_hands']} total, {stats['filtered_hands']} filtered")
        self._update_status("👆 SELECT a hand from the list, then click 'LOAD HAND' to begin study")
    
    def _on_theme_change(self):
        """Handle poker table theme change."""
        theme_name = self.theme_var.get()
        print(f"🎨 Switching to theme: {theme_name}")
        
        # Switch theme in the theme manager
        self.theme.set_profile(theme_name)
        
        # Update status to show theme change
        self._update_status(f"🎨 Switched to {theme_name} theme - New poker table colors applied!")
        
        # Force UI refresh with new theme
        self._refresh_ui_colors()
        
        # Update artistic theme introduction
        self._show_theme_intro(theme_name)
    
    def _show_theme_intro(self, theme_name):
        """Show artistic introduction for the selected theme."""
        intro_text = self.THEME_INTROS.get(theme_name, "A unique poker table theme with its own distinctive character.")
        
        # Update the intro label with elegant styling
        self.theme_intro_label.config(state="normal")
        self.theme_intro_label.delete(1.0, tk.END)
        self.theme_intro_label.insert(1.0, intro_text)
        self.theme_intro_label.config(state="disabled")
        
        # Apply theme colors to the intro panel
        theme = self.theme.get_theme()
        bg_color = theme.get("panel.bg", "#111827")
        fg_color = theme.get("text.secondary", "#9CA3AF")
        
        self.theme_intro_label.config(
            bg=bg_color,
            fg=fg_color,
            insertbackground=fg_color,
            selectbackground=theme.get("a11y.focus", "#6366F1"),
            selectforeground=theme.get("text.primary", "#F9FAFB")
        )
    
    def _refresh_ui_colors(self):
        """Refresh all UI elements with new theme colors."""
        theme = self.theme.get_theme()
        
        # Update all themed elements
        try:
            # Update listbox colors
            if hasattr(self, 'hands_listbox'):
                self.hands_listbox.configure(
                    bg=theme.get("panel.bg", "#111827"),
                    fg=theme.get("panel.fg", "#E5E7EB"),
                    selectbackground=theme.get("btn.primaryBg", "#16A34A"),
                    selectforeground=theme.get("btn.primaryFg", "#F8FAFC")
                )
            
            # Update text areas
            for text_widget in [getattr(self, 'details_text', None), getattr(self, 'status_text', None)]:
                if text_widget:
                    text_widget.configure(
                        bg=theme.get("panel.bg", "#111827"),
                        fg=theme.get("panel.fg", "#E5E7EB")
                    )
            
            # Update load button
            if hasattr(self, 'load_btn'):
                self.load_btn.configure(
                    bg=theme.get("btn.primaryBg", "#16A34A"),
                    fg=theme.get("btn.primaryFg", "#F8FAFC")
                )
            
            # Update control buttons
            control_buttons = [getattr(self, btn, None) for btn in ['next_btn', 'auto_btn', 'reset_btn']]
            for btn in control_buttons:
                if btn:
                    btn.configure(
                        bg=theme.get("btn.secondaryBg", "#334155"),
                        fg=theme.get("btn.secondaryFg", "#E2E8F0")
                    )
            
            # Update poker table canvas and force full re-render
            if hasattr(self, 'canvas_manager') and self.canvas_manager.canvas:
                # Update canvas background
                self.canvas_manager.canvas.configure(
                    bg=theme.get("table.felt", "#1E5B44")
                )
                
                # Force poker table components to re-render with new theme
                if hasattr(self, 'renderer_pipeline'):
                    try:
                        state = self.store.get_state()
                        self.renderer_pipeline.render_once(state)
                        print(f"🎨 Poker table re-rendered with {self.theme_var.get()} theme colors")
                    except Exception as e:
                        print(f"⚠️  Error re-rendering poker table: {e}")
            
            # Update enhanced buttons to refresh their theme
            for btn_name in ['load_btn', 'next_btn', 'auto_btn', 'reset_btn']:
                if hasattr(self, btn_name):
                    btn = getattr(self, btn_name)
                    if hasattr(btn, 'refresh_theme'):
                        btn.refresh_theme()
            
            # Update artistic theme intro panel colors
            if hasattr(self, 'theme_intro_label'):
                self._show_theme_intro(self.theme_var.get())
                
        except Exception as e:
            print(f"⚠️  Error refreshing UI colors: {e}")
    
    def _on_library_type_change(self):
        """Handle library type change."""
        library_type = self.library_type.get()
        # TODO: Filter by library type
        self._refresh_hands_list()
    
    def _on_collection_change(self, event=None):
        """Handle collection selection change."""
        collection = self.collection_var.get()
        if collection == "All Hands":
            self.hands_repository.set_filter(HandsFilter())  # Clear filter
        else:
            # TODO: Set filter for specific collection
            pass
        self._refresh_hands_list()
    
    def _on_hand_select(self, event):
        """Handle hand selection."""
        selection = self.hands_listbox.curselection()
        if selection:
            index = selection[0]
            filtered_hands = self.hands_repository.get_filtered_hands()
            if index < len(filtered_hands):
                hand = filtered_hands[index]
                self._update_hand_details(hand)
                # Show that hand is selected and ready to load
                hand_id = hand.get('hand_id', 'Unknown')
                self._update_status(f"✅ Selected: {hand_id} - Click 'LOAD HAND' to start study")
    
    def _update_hand_details(self, hand_data: Dict[str, Any]):
        """Update the hand details display."""
        self.details_text.delete(1.0, tk.END)
        
        details = [
            f"Hand ID: {hand_data.get('hand_id', 'Unknown')}",
            f"Players: {len(hand_data.get('players', []))}",
            f"Stakes: ${hand_data.get('small_blind', 5)}/${hand_data.get('big_blind', 10)}",
            f"Pot: ${hand_data.get('pot_size', 0)}",
            "",
            "Players:"
        ]
        
        for i, player in enumerate(hand_data.get('players', [])):
            name = player.get('name', f'seat{i+1}')
            stack = player.get('stack', 0)
            position = player.get('position', 'Unknown')
            details.append(f"  {name} ({position}): ${stack}")
        
        community = hand_data.get('community_cards', [])
        if community:
            details.extend(["", f"Community: {', '.join(community)}"])
        
        self.details_text.insert(1.0, '\n'.join(details))
    
    def _on_study_mode_change(self):
        """Handle study mode change."""
        mode = self.study_mode.get()
        self.store.dispatch({
            "type": SET_STUDY_MODE,
            "mode": mode
        })
        self._update_status(f"📚 Study mode: {mode}")
    
    def _apply_filters(self):
        """Apply current filter settings."""
        filter_criteria = HandsFilter()
        
        # Apply position filter
        if self.position_var.get() != "All":
            filter_criteria.positions = [self.position_var.get()]
        
        # Apply stack depth filter
        try:
            filter_criteria.min_stack_depth = int(self.min_stack.get()) if self.min_stack.get() else None
            filter_criteria.max_stack_depth = int(self.max_stack.get()) if self.max_stack.get() else None
        except ValueError:
            pass
        
        # Apply pot type filter
        if self.pot_type_var.get() != "All":
            filter_criteria.pot_type = self.pot_type_var.get()
        
        # Apply search text
        filter_criteria.search_text = self.search_var.get()
        
        # Set filter and refresh
        self.hands_repository.set_filter(filter_criteria)
        self.store.dispatch({
            "type": SET_REVIEW_FILTER,
            "filter": filter_criteria.__dict__
        })
        self._refresh_hands_list()
    
    def _load_selected_hand(self):
        """Load the selected hand for study."""
        selection = self.hands_listbox.curselection()
        if not selection:
            self._update_status("❌ Please select a hand to load")
            return
        
        index = selection[0]
        filtered_hands = self.hands_repository.get_filtered_hands()
        if index >= len(filtered_hands):
            return
        
        hand_data = filtered_hands[index]
        
        # Publish load event as per architecture doc
        self.event_bus.publish(
            self.event_bus.topic(self.session_id, "review:load"),
            hand_data
        )
    
    def _handle_load_hand_event(self, hand_data):
        """Handle the review:load event."""
        try:
            self._update_status(f"🔄 Loading hand {hand_data.get('hand_id', 'Unknown')}...")
            
            # Store hand data for reset functionality
            self.last_loaded_hand = hand_data
            
            # Convert to Hand object (following validation tester pattern)
            if isinstance(hand_data, dict) and 'hand_id' in hand_data:
                hand = Hand.from_dict(hand_data)
            else:
                self._update_status("❌ Invalid hand data format")
                return
                
            # Create decision engine
            decision_engine = ConcreteHandModelDecisionEngine(hand)
            
            # Create game config from hand metadata
            config = GameConfig(
                num_players=len(hand_data.get('players', [])),
                small_blind=hand_data.get('small_blind', 5),
                big_blind=hand_data.get('big_blind', 10),
                initial_stack=max([p.get('stack', 1000) for p in hand_data.get('players', [])], default=1000)
            )
            
            # Create hands review session
            self.current_session = HandsReviewBotSession(config, decision_engine)
            
            # Set preloaded hand data
            self.current_session.set_preloaded_hand_data({"hand_model": hand})
            
            # Connect FPSM adapter to get poker state updates
            if not self.fpsm_adapter:
                self.fpsm_adapter = FpsmEventAdapter(self.store)
            self.fpsm_adapter.attach(self.current_session)
            
            # Start the session
            success = self.current_session.start_session()
            if success:
                self.session_active = True
                
                # Update store with loaded hand and initial poker state
                self.store.dispatch({
                    "type": SET_LOADED_HAND,
                    "hand": hand_data
                })
                
                # Initialize poker table display state
                players_data = hand_data.get('players', [])
                seats_data = []
                for i, p in enumerate(players_data):
                    seat_data = {
                        "name": p.get('name', f'seat{i+1}'), 
                        "stack": p.get('stack', 0), 
                        "cards": p.get('cards', []), 
                        "position": p.get('position', ''),
                        "current_bet": p.get('current_bet', 0),
                        "folded": p.get('folded', False),
                        "all_in": p.get('all_in', False),
                        "acting": False,  # Will be set by FPSM updates
                        "active": not p.get('folded', False)
                    }
                    seats_data.append(seat_data)
                
                self.store.dispatch({
                    "type": SET_SEATS,
                    "seats": seats_data
                })
                
                self.store.dispatch({
                    "type": SET_POT,
                    "amount": hand_data.get('pot_size', 0)
                })
                
                if hand_data.get('community_cards'):
                    self.store.dispatch({
                        "type": SET_BOARD,
                        "board": hand_data.get('community_cards', [])
                    })
                
                self.store.dispatch({
                    "type": SET_DEALER,
                    "dealer": hand_data.get('dealer', 0)
                })
                
                self._update_status(f"✅ Hand {hand.hand_id} loaded! Hole cards visible. Click 'Next →' to advance.")
                
                # Force a table render
                self.after_idle(lambda: self.renderer_pipeline.render_once(self.store.get_state()))
            else:
                self._update_status(f"❌ Failed to start hand session")
                
        except Exception as e:
            self._update_status(f"❌ Error loading hand: {e}")
            import traceback
            traceback.print_exc()
    
    def _next_action(self):
        """Execute the next action in replay."""
        if not self.current_session or not self.session_active:
            self._update_status("⚠️  No active session. Please load a hand first.")
            return
            
        try:
            result = self.current_session.execute_next_bot_action()
            if result:
                action_info = result.get('explanation', 'Action executed')
                self._update_status(f"▶ {action_info}")
                
                if self.current_session.is_session_complete():
                    self._update_status("🏁 Hand replay completed!")
            else:
                self._update_status("🏁 Hand replay completed")
        except Exception as e:
            self._update_status(f"❌ Error executing action: {e}")
    
    def _toggle_auto(self):
        """Toggle automatic playback."""
        # TODO: Implement auto-play functionality
        self._update_status("⚠️  Auto-play not yet implemented")
    
    def _reset_hand(self):
        """Reset the current hand."""
        if not self.current_session:
            self._update_status("⚠️  No active session to reset")
            return
            
        try:
            self.current_session.reset_session()
            self.session_active = True
            self._update_status("🔄 Hand reset to beginning")
        except Exception as e:
            self._update_status(f"❌ Error resetting hand: {e}")
    
    def _update_status(self, message: str):
        """Update the status display."""
        self.status_text.insert(tk.END, f"\n{message}")
        self.status_text.see(tk.END)
    
    def _on_store_change(self, state):
        """Handle store state changes and re-render poker table."""
        # Trigger table re-render when store state changes
        self.after_idle(lambda: self.renderer_pipeline.render_once(state))
    
    def _refresh_fonts(self):
        """Refresh fonts after theme changes."""
        fonts = self.theme.get_fonts()
        
        # Update listbox font
        if hasattr(self, 'hands_listbox'):
            body_font = fonts.get("body", ("Consolas", 20))
            self.hands_listbox.configure(font=body_font)
        
        # Update text areas
        small_font = fonts.get("small", ("Consolas", 16))
        if hasattr(self, 'details_text'):
            self.details_text.configure(font=small_font)
        if hasattr(self, 'status_text'):
            self.status_text.configure(font=small_font)
        
        # Update theme intro label font
        if hasattr(self, 'theme_intro_label'):
            intro_font = fonts.get("body", ("Inter", 20, "italic"))
            self.theme_intro_label.configure(font=intro_font)
        
        # Update enhanced button themes (handles both fonts and colors)
        enhanced_buttons = []
        if hasattr(self, 'load_btn') and hasattr(self.load_btn, 'refresh_theme'): 
            enhanced_buttons.append(self.load_btn)
        if hasattr(self, 'next_btn') and hasattr(self.next_btn, 'refresh_theme'): 
            enhanced_buttons.append(self.next_btn)
        if hasattr(self, 'auto_btn') and hasattr(self.auto_btn, 'refresh_theme'): 
            enhanced_buttons.append(self.auto_btn)
        if hasattr(self, 'reset_btn') and hasattr(self.reset_btn, 'refresh_theme'): 
            enhanced_buttons.append(self.reset_btn)
        
        for btn in enhanced_buttons:
            btn.refresh_theme()
    
    def _next_action(self):
        """Advance to the next action in the hand."""
        if not self.session_active or not self.current_session:
            self._update_status("⚠️ No hand loaded. Please select and load a hand first.")
            return
            
        try:
            # Check if session is complete first
            if self.current_session.decision_engine.is_session_complete():
                self._update_status("🏁 Hand complete - no more actions")
                return
            
            # Execute next action through the session (using correct method name from validation tester)
            result = self.current_session.execute_next_bot_action()
            if result:
                self._update_status("▶️ Advanced to next action")
                # The FPSM adapter should automatically update the poker table display
                # Force a render to ensure UI is updated
                self.after_idle(lambda: self.renderer_pipeline.render_once(self.store.get_state()))
            else:
                self._update_status("🏁 Hand complete - no more actions")
        except Exception as e:
            self._update_status(f"❌ Error advancing hand: {e}")
    
    def _toggle_auto(self):
        """Toggle auto-play mode."""
        if not self.session_active or not self.current_session:
            self._update_status("⚠️ No hand loaded. Please select and load a hand first.")
            return
            
        try:
            # Simple auto-play implementation - repeatedly call next action
            if not hasattr(self, 'auto_play_active'):
                self.auto_play_active = False
            
            if not self.auto_play_active:
                # Enable auto-play
                self.auto_play_active = True
                self.auto_btn.configure(text="Pause")
                self._update_status("🤖 Auto-play enabled")
                self._auto_play_loop()
            else:
                # Disable auto-play
                self.auto_play_active = False
                self.auto_btn.configure(text="Auto")
                self._update_status("⏸️ Auto-play disabled")
        except Exception as e:
            self._update_status(f"❌ Error toggling auto-play: {e}")
    
    def _auto_play_loop(self):
        """Auto-play loop that advances actions automatically."""
        if not self.auto_play_active or not self.session_active or not self.current_session:
            return
            
        try:
            # Check if session is complete
            if self.current_session.decision_engine.is_session_complete():
                self.auto_play_active = False
                self.auto_btn.configure(text="Auto")
                self._update_status("🏁 Hand complete - auto-play stopped")
                return
            
            # Execute next action
            result = self.current_session.execute_next_bot_action()
            if result:
                # Force a render
                self.after_idle(lambda: self.renderer_pipeline.render_once(self.store.get_state()))
                # Schedule next action after 1 second
                self.after(1000, self._auto_play_loop)
            else:
                self.auto_play_active = False
                self.auto_btn.configure(text="Auto")
                self._update_status("🏁 Hand complete - auto-play stopped")
        except Exception as e:
            self.auto_play_active = False
            self.auto_btn.configure(text="Auto")
            self._update_status(f"❌ Auto-play error: {e}")
    
    def _reset_hand(self):
        """Reset the current hand to the beginning."""
        if not self.session_active or not self.current_session:
            self._update_status("⚠️ No hand loaded. Please select and load a hand first.")
            return
            
        try:
            # Reset the session
            if hasattr(self.current_session, 'reset_session'):
                self.current_session.reset_session()
                self._update_status("🔄 Hand reset to beginning")
                
                # Force a render to show initial state
                self.after_idle(lambda: self.renderer_pipeline.render_once(self.store.get_state()))
            else:
                # Fallback - reload the current hand
                self._update_status("🔄 Reloading hand...")
                if hasattr(self, 'last_loaded_hand'):
                    self._handle_load_hand_event(self.last_loaded_hand)
                else:
                    self._update_status("⚠️ No hand to reset")
        except Exception as e:
            self._update_status(f"❌ Error resetting hand: {e}")
    
    def on_show(self):
        """Called when tab is shown - refresh display."""
        if hasattr(self, 'renderer_pipeline'):
            state = self.store.get_state()
            self.renderer_pipeline.render_once(state)
    
    def dispose(self):
        """Clean up when tab is closed."""
        if self.fpsm_adapter:
            self.fpsm_adapter.detach()
        self.services.dispose_session(self.session_id)