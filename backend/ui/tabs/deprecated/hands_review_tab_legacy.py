import tkinter as tk
from tkinter import ttk
import uuid
import time
from typing import Optional

# New UI Architecture imports
from ..state.actions import (
    SET_REVIEW_HANDS,
    SET_REVIEW_FILTER,
    SET_STUDY_MODE
)
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer
from ..services.game_director import GameDirector
from ..services.effect_bus import EffectBus
from ..services.hands_repository import HandsRepository, HandsFilter, StudyMode
from ..services.hands_review_session_manager import HandsReviewSessionManager

# PPSM architecture - using HandsReviewSessionManager and PokerTableRenderer as per architecture guidelines

# Import enhanced button components
try:
    from ..components.enhanced_button import PrimaryButton, SecondaryButton
except ImportError:
    # Fallback to basic buttons if enhanced buttons not available
    PrimaryButton = SecondaryButton = tk.Button

# Import ActionBanner for visual feedback
try:
    from ..components.action_banner import ActionBanner
except ImportError:
    print("⚠️ ActionBanner not available, using fallback")
    ActionBanner = None

# Core imports - fail fast if not available
USE_DEV_STUBS = True  # Temporarily use stubs to fix console error

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from core.hand_model import Hand
    from core.hand_model_decision_engine import HandModelDecisionEngine
    # PPSM imports instead of FPSM
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    # HandsReviewBotSession removed - using PPSMHandsReviewBotSession below
    from core.session_logger import get_session_logger
            # Sound manager for poker table
    from utils.sound_manager import SoundManager
except ImportError as e:
    if not USE_DEV_STUBS:
        raise ImportError(f"Critical core modules not available: {e}. This will break hands review functionality.") from e
    print("⚠️ Using dev stubs due to import error:", e)
    
    # Minimal stubs for development only
    class Hand:
        def __init__(self, data):
            if isinstance(data, dict):
                self.hand_id = data.get("hand_id", "Unknown")
                self.players = data.get("players", [])
                self.pot_size = data.get("pot_size", 0)
                self.small_blind = data.get("small_blind", 5)
                self.big_blind = data.get("big_blind", 10)
                self.community_cards = data.get("community_cards", [])
                self.dealer = data.get("dealer", 0)
                self.__dict__.update(data)

        @classmethod
        def from_dict(cls, data):
            return cls(data)

    class HandModelDecisionEngine:
        def __init__(self, hand):
            pass

        def is_session_complete(self):
            return False

    class GameConfig:
        def __init__(self, **kwargs):
            pass

    def get_session_logger():
        class FallbackLogger:
            def log_system(self, *args, **kwargs):
                pass

        return FallbackLogger()


# Session manager will be initialized in the tab
# HandsReviewSessionManager handles all business logic per architecture guidelines

    




    """Concrete wrapper for HandModelDecisionEngine."""

    def __init__(self, hand):
        self.hand = hand
        try:
            if HandModelDecisionEngine and hand:
                self._engine = HandModelDecisionEngine.__new__(HandModelDecisionEngine)
                self._engine.hand = hand
                if hasattr(self._engine, "_organize_actions_by_street"):
                    self._engine.actions_by_street = (
                        self._engine._organize_actions_by_street()
                    )
                self._engine.current_action_index = 0
                if hasattr(self._engine, "_get_betting_actions"):
                    self._engine.actions_for_replay = (
                        self._engine._get_betting_actions()
                    )
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
        if self._engine and hasattr(self._engine, "get_decision"):
            return self._engine.get_decision(player_index, game_state)
        return {
            "action": "fold",
            "amount": 0,
            "explanation": "Default action",
            "confidence": 0.5,
        }

    def is_session_complete(self):
        if self._engine and hasattr(self._engine, "is_session_complete"):
            return self._engine.is_session_complete()
        return True

    def reset(self):
        if self._engine and hasattr(self._engine, "reset"):
            self._engine.reset()

    def get_session_info(self):
        if self._engine and hasattr(self._engine, "hand"):
            # Handle both fallback Hand class (hand.hand_id) and real Hand class (hand.metadata.hand_id)
            hand_id = "Unknown"
            if hasattr(self._engine.hand, "hand_id"):
                hand_id = self._engine.hand.hand_id
            elif hasattr(self._engine.hand, "metadata") and hasattr(
                self._engine.hand.metadata, "hand_id"
            ):
                hand_id = self._engine.hand.metadata.hand_id

            return {
                "hand_id": hand_id,
                "total_actions": getattr(self._engine, "total_actions", 0),
                "current_action": getattr(self._engine, "current_action_index", 0),
                "engine_type": "HandModelDecisionEngine",
            }
        return {
            "hand_id": "Unknown",
            "total_actions": 0,
            "current_action": 0,
            "engine_type": "Fallback",
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
        # Sounds are owned by EffectBus per architecture; no local fallback

        # Session state - using HandsReviewSessionManager per architecture guidelines
        self.session_manager: Optional[HandsReviewSessionManager] = None
        self.session_active = False
        
        # Use global services from service container for proper coordination
        self.game_director = self.services.get_app("game_director")
        if not self.game_director:
            # Create global GameDirector if not exists
            self.game_director = GameDirector(event_bus=self.event_bus)
            self.services.provide_app("game_director", self.game_director)
        
        # Use global EffectBus service for proper event coordination
        self.effect_bus = self.services.get_app("effect_bus")
        if not self.effect_bus:
            # Create global EffectBus if not exists
            self.effect_bus = EffectBus(
                game_director=self.game_director,
                event_bus=self.event_bus
            )
            self.services.provide_app("effect_bus", self.effect_bus)
        
        # Ensure proper connections for event coordination
        self.game_director.set_event_bus(self.event_bus)
        self.effect_bus.set_game_director(self.game_director)
        self.effect_bus.set_event_bus(self.event_bus)
        
        # Initialize HandsReviewSessionManager per architecture guidelines
        try:
            # Try direct import first
            try:
                from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
            except ImportError:
                # Fallback to relative import
                from ...core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
                
            # Create a default game config for hands review
            game_config = GameConfig(
                num_players=6,  # Default to 6 players for hands review
                small_blind=1.0,
                big_blind=2.0,
                starting_stack=1000.0
            )
            
            ppsm = PurePokerStateMachine(config=game_config)
            self.session_manager = HandsReviewSessionManager(
                store=self.store,
                ppsm=ppsm,
                game_director=self.game_director,
                effect_bus=self.effect_bus,
                event_bus=self.event_bus
            )
            
            # ARCHITECTURE COMPLIANT: Register session with event controller
            try:
                hands_review_controller = self.services.get_app("hands_review_controller")
                if hands_review_controller:
                    self.event_bus.publish(
                        "hands_review:session_created",
                        {
                            "session_id": self.session_id,
                            "session_manager": self.session_manager
                        }
                    )
                    print(f"🎯 HandsReviewTab: Session {self.session_id} registered with event controller")
            except Exception as e:
                print(f"⚠️ HandsReviewTab: Failed to register session: {e}")
            print("🎯 HandsReviewTab: Session manager initialized per architecture guidelines")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Could not initialize session manager: {e}")
            self.session_manager = None

        # Setup UI
        self.on_mount()

        # Subscribe to events and store changes
        self._setup_event_subscriptions()
        self.store.subscribe(self._on_store_change)

        # Initialize GTO hands for PPSM testing
        self.loaded_gto_hands = []
        # GTO hands will be loaded in on_mount() to ensure proper UI initialization order

    def on_mount(self):
        """Set up the tab layout per PRD design."""
        # Two-column layout: Controls (20%) | Poker Table (80%)
        # Using 1:4 ratio for poker table emphasis
        self.grid_columnconfigure(0, weight=1)  # Library + Filters & Controls (20%)
        self.grid_columnconfigure(1, weight=4)  # Poker Table (80%)
        self.grid_rowconfigure(0, weight=1)

        # Create the two main sections
        self._create_combined_left_section()
        self._create_poker_table_section()
        
        # Load GTO hands for PPSM testing
        self._load_gto_hands()
        
        # Refresh hands list now that GTO hands are loaded
        self._refresh_hands_list()
        
        # Start main update loop for GameDirector and EffectBus
        self._start_update_loop()
        
        # Setup ActionBanner for visual feedback
        self._setup_action_banner()
        
        # Start the UI tick loop for GameDirector and EffectBus
        self._start_ui_tick_loop()

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
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass  # Fallback to default colors if theming fails
        library_frame.grid_columnconfigure(0, weight=1)
        library_frame.grid_rowconfigure(
            3, weight=1
        )  # Hands list gets most space (shifted down due to theme selector)

        # Theme selector (at top) - 5 Professional Casino Schemes
        theme_frame = ttk.LabelFrame(
            library_frame, text="🎨 Professional Casino Themes", padding=5
        )
        theme_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(0, weight=1)

        theme_controls = ttk.Frame(theme_frame)
        theme_controls.grid(row=0, column=0, sticky="ew")

        current_theme = self.theme.current_profile_name()
        self.theme_var = tk.StringVar(value=current_theme)

        # All available themes from ThemeManager
        all_theme_names = self.theme.names()
        print(
            f"🎨 HandsReviewTab: Found {len(all_theme_names)} themes: {all_theme_names}"
        )

        # Fallback if no themes found
        if not all_theme_names:
            print("⚠️ No themes found, forcing theme manager reload...")
            # Try to reload theme manager
            try:
                from ..services.theme_factory import build_all_themes

                themes = build_all_themes()
                print(f"🔄 Force-built {len(themes)} themes: {list(themes.keys())}")
                # Register them with the theme manager
                for name, tokens in themes.items():
                    self.theme.register(name, tokens)
                all_theme_names = self.theme.names()
                print(
                    f"🎨 After reload: {len(all_theme_names)} themes: {all_theme_names}"
                )
            except Exception as e:
                print(f"❌ Failed to reload themes: {e}")
                # Get actual theme names from config, with ultimate fallback
                default_theme_data = self.theme.get_available_themes()
                all_theme_names = (
                    list(default_theme_data.keys())
                    if default_theme_data
                    else ["Forest Green Professional 🌿"]
                )

        # Theme icons are now embedded in theme names from JSON config
        # No need for separate THEME_ICONS or THEME_INTROS - all data comes from poker_themes.json

        # Create clean 4x4 grid layout for 16 themes with 20px font
        # Configure grid weights for even distribution
        for col_idx in range(4):
            theme_controls.grid_columnconfigure(col_idx, weight=1)

        for i, theme_name in enumerate(all_theme_names):
            row = i // 4  # 4 themes per row
            col = i % 4

            # Theme names from JSON config already include icons and formatting
            display_name = theme_name

            # Simple radiobutton with 20px font and equal spacing
            radio_btn = ttk.Radiobutton(
                theme_controls,
                text=display_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._on_theme_change,
            )
            radio_btn.grid(row=row, column=col, sticky="w", padx=5, pady=3)

            # Configure font size to 20px and store reference for styling
            try:
                fonts = self.theme.get_fonts()
                radio_font = fonts.get(
                    "button", fonts.get("body", ("Inter", 20, "normal"))
                )
                radio_btn.configure(font=radio_font)
            except:
                # Fallback if font configuration fails
                pass

            # Store radio button reference for theme styling
            if not hasattr(self, "theme_radio_buttons"):
                self.theme_radio_buttons = []
            self.theme_radio_buttons.append(radio_btn)

            # Theme intro will update only on selection, not hover
            # Removed confusing hover effects that changed intro on mouse over

        # Apply initial theme styling to radio buttons
        self.after_idle(self._style_theme_radio_buttons)

        # Artistic Theme Info Panel - shows evocative descriptions (positioned AFTER theme controls)
        info_frame = ttk.Frame(theme_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        # Luxury Museum Placard - Theme intro with elegant styling
        fonts = self.theme.get_fonts()
        # Use theme-aware font for luxury feel
        fonts = self.theme.get_fonts()
        intro_font = fonts.get("intro", fonts.get("body", ("Georgia", 16, "normal")))

        # Create luxury museum placard frame with theme-aware styling
        base_colors = self.theme.get_base_colors()
        placard_bg = base_colors.get("panel_bg", "#2A2A2A")
        placard_accent = base_colors.get("highlight", "#D4AF37")

        placard_frame = tk.Frame(
            info_frame,
            relief="raised",
            borderwidth=2,
            bg=placard_bg,
            highlightbackground=placard_accent,
            highlightcolor=placard_accent,
            highlightthickness=1,
        )
        # Use theme dimensions for consistent spacing
        dimensions = self.theme.get_dimensions()
        medium_pad = dimensions["padding"]["medium"]
        placard_frame.grid(
            row=0, column=0, sticky="ew", padx=medium_pad, pady=medium_pad
        )
        placard_frame.grid_columnconfigure(0, weight=1)

        # Store reference to placard frame for dynamic styling
        self.placard_frame = placard_frame

        # Get initial theme colors instead of hardcoding
        base_colors = self.theme.get_base_colors()
        initial_bg = base_colors.get("panel_bg", "#1A1A1A")
        initial_fg = base_colors.get("text", "#F5F5DC")

        intro_height = dimensions["text_height"][
            "medium"
        ]  # Use medium instead of small for theme intros
        self.theme_intro_label = tk.Text(
            placard_frame,
            height=intro_height,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            font=intro_font,
            state="disabled",
            cursor="arrow",
            padx=dimensions["padding"]["xlarge"],
            pady=dimensions["padding"]["medium"],
            bg=initial_bg,
            fg=initial_fg,
        )  # Dynamic theme colors
        self.theme_intro_label.grid(row=0, column=0, sticky="ew")

        # Show current theme's introduction
        self._show_theme_intro(current_theme)

        # Library type selector
        type_frame = ttk.Frame(library_frame)
        type_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        type_frame.grid_columnconfigure(0, weight=1)

        self.library_type = tk.StringVar(value="legendary")
        ttk.Radiobutton(
            type_frame,
            text="🏆 Legendary",
            variable=self.library_type,
            value="legendary",
            command=self._on_library_type_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="🤖 Bot Sessions",
            variable=self.library_type,
            value="bot",
            command=self._on_library_type_change,
        ).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="📥 Imported",
            variable=self.library_type,
            value="imported",
            command=self._on_library_type_change,
        ).grid(row=0, column=2, sticky="w")

        # Collections dropdown
        collections_frame = ttk.Frame(library_frame)
        collections_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        collections_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(collections_frame, text="Collection:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.collection_var = tk.StringVar(value="🤖 GTO Hands")
        self.collection_combo = ttk.Combobox(
            collections_frame, textvariable=self.collection_var, state="readonly"
        )
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

        self.hands_listbox = tk.Listbox(
            hands_frame, font=body_font, selectmode=tk.SINGLE
        )
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        self.hands_listbox.bind("<<ListboxSelect>>", self._on_hand_select)

        # Apply theme colors to listbox with dynamic selection highlight
        try:
            # Get theme-specific selection highlight
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            # Get selection highlight from config-driven system
            base_colors = self.theme.get_base_colors()
            selection_highlight = {
                "color": base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
            }

            self.hands_listbox.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                selectbackground=selection_highlight[
                    "color"
                ],  # Dynamic theme-specific highlight
                selectforeground=base_colors.get(
                    "highlight_text", base_colors.get("text", "#FFFFFF")
                ),  # Theme-aware text when highlighted
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        scrollbar = ttk.Scrollbar(
            hands_frame, orient="vertical", command=self.hands_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.configure(yscrollcommand=scrollbar.set)

        # Hand details text (smaller in the combined layout)
        details_frame = ttk.LabelFrame(library_frame, text="Hand Details", padding=5)
        details_frame.grid(row=5, column=0, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)

        small_font = fonts.get("small", ("Consolas", 16))
        details_height = self.theme.get_dimensions()["text_height"]["medium"]
        self.details_text = tk.Text(
            details_frame, height=details_height, wrap=tk.WORD, font=small_font
        )
        self.details_text.grid(row=0, column=0, sticky="ew")

        # Apply theme colors to details text
        try:
            self.details_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

    def _create_filters_section_in_frame(self, parent):
        """Create the Filters & Controls section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()

        filters_frame = ttk.LabelFrame(
            parent, text="🔍 Filters & Study Mode", padding=10
        )
        filters_frame.grid(row=1, column=0, sticky="nsew", pady=(2.5, 0))

        # Apply theme colors to the frame
        try:
            filters_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass
        filters_frame.grid_columnconfigure(0, weight=1)

        # Study Mode selector
        study_frame = ttk.LabelFrame(filters_frame, text="Study Mode", padding=5)
        study_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.study_mode = tk.StringVar(value=StudyMode.REPLAY.value)
        ttk.Radiobutton(
            study_frame,
            text="🔄 Replay",
            variable=self.study_mode,
            value=StudyMode.REPLAY.value,
            command=self._on_study_mode_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="📊 Solver Diff",
            variable=self.study_mode,
            value=StudyMode.SOLVER_DIFF.value,
            command=self._on_study_mode_change,
        ).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="🧠 Recall Quiz",
            variable=self.study_mode,
            value=StudyMode.RECALL_QUIZ.value,
            command=self._on_study_mode_change,
        ).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="❓ Explain Mistake",
            variable=self.study_mode,
            value=StudyMode.EXPLAIN_MISTAKE.value,
            command=self._on_study_mode_change,
        ).grid(row=3, column=0, sticky="w")

        # Filters section
        filter_frame = ttk.LabelFrame(filters_frame, text="Filters", padding=5)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        # Position filter
        ttk.Label(filter_frame, text="Position:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.position_var = tk.StringVar(value="All")
        position_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.position_var,
            values=["All", "UTG", "MP", "CO", "BTN", "SB", "BB"],
            state="readonly",
            width=8,
        )
        position_combo.grid(row=0, column=1, sticky="w", pady=2)

        # Stack depth filter
        ttk.Label(filter_frame, text="Stack Depth:").grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        stack_frame = ttk.Frame(filter_frame)
        stack_frame.grid(row=1, column=1, sticky="w", pady=2)
        self.min_stack = tk.StringVar(value="20")
        self.max_stack = tk.StringVar(value="200")
        ttk.Entry(stack_frame, textvariable=self.min_stack, width=5).grid(
            row=0, column=0
        )
        ttk.Label(stack_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(stack_frame, textvariable=self.max_stack, width=5).grid(
            row=0, column=2
        )
        ttk.Label(stack_frame, text=" BB").grid(row=0, column=3)

        # Pot type filter
        ttk.Label(filter_frame, text="Pot Type:").grid(
            row=2, column=0, sticky="w", padx=(0, 5)
        )
        self.pot_type_var = tk.StringVar(value="All")
        pot_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.pot_type_var,
            values=["All", "SRP", "3BP", "4BP+"],
            state="readonly",
            width=8,
        )
        pot_combo.grid(row=2, column=1, sticky="w", pady=2)

        # Search text
        ttk.Label(filter_frame, text="Search:").grid(
            row=3, column=0, sticky="w", padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=3, column=1, sticky="ew", pady=2)
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        # Apply filters button
        ttk.Button(
            filter_frame, text="Apply Filters", command=self._apply_filters
        ).grid(row=4, column=0, columnspan=2, pady=5)

        # Action buttons
        actions_frame = ttk.LabelFrame(filters_frame, text="Actions", padding=5)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        actions_frame.grid_columnconfigure(0, weight=1)

        # Load button (main action) - Enhanced primary button
        self.load_btn = PrimaryButton(
            actions_frame,
            text="🔥 LOAD HAND",
            command=self._load_selected_hand,
            theme_manager=self.theme,
        )
        self.load_btn.grid(row=0, column=0, sticky="ew", pady=5)

        # Enhanced button handles its own styling

        # Playback controls
        controls_frame = ttk.Frame(actions_frame)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Enhanced buttons handle their own styling

        # Enhanced secondary buttons for controls
        self.next_btn = SecondaryButton(
            controls_frame,
            text="Next →",
            command=self._next_action,  # Use session manager method
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        self.auto_btn = SecondaryButton(
            controls_frame,
            text="Auto",
            command=self._toggle_auto_play,  # Use session manager method
            theme_manager=self.theme,
        )
        self.auto_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = SecondaryButton(
            controls_frame,
            text="Reset",
            command=self._reset_hand,  # Use session manager method
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=2, padx=(5, 0))

        # Enhanced buttons handle their own styling

        # Status text
        status_frame = ttk.LabelFrame(filters_frame, text="Status", padding=5)
        status_frame.grid(row=3, column=0, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)

        fonts = self.theme.get_fonts()
        small_font = fonts.get("small", ("Consolas", 16))
        status_height = self.theme.get_dimensions()["text_height"]["large"]
        self.status_text = tk.Text(
            status_frame, height=status_height, wrap=tk.WORD, font=small_font
        )
        self.status_text.grid(row=0, column=0, sticky="nsew")

        # Apply theme colors to status text
        try:
            self.status_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        # Poker Table Controls
        poker_frame = ttk.LabelFrame(actions_frame, text="🎮 Poker Table Controls", padding=5)
        poker_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        poker_frame.grid_columnconfigure(1, weight=1)

        # Next Action button for poker table
        self.next_btn = SecondaryButton(
            poker_frame,
            text="▶ Next Action",
            command=self._next_action,
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        # Reset button for poker table
        self.reset_btn = SecondaryButton(
            poker_frame,
            text="↩ Reset Hand",
            command=self._reset_hand,
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=1, padx=5)

        # Progress display for poker table
        self.progress_label = ttk.Label(poker_frame, text="No hand loaded")
        self.progress_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Enhanced buttons handle their own styling

    def _create_poker_table_section(self):
        """Create poker table using PokerTableRenderer (right column)."""
        # Get theme colors for poker table
        theme = self.theme.get_theme()

        table_frame = ttk.LabelFrame(self, text="♠️ Enhanced Poker Table", padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(2.5, 5), pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Apply theme colors to table frame
        try:
            table_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass

        # Create PokerTableRenderer directly in the table frame
        self._setup_poker_table(table_frame)
        
        print(f"🎯 HandsReviewTab: Table frame created and configured")
        print(f"   Frame size: {table_frame.winfo_width()}x{table_frame.winfo_height()}")
        print(f"   Table renderer created: {hasattr(self, 'table_renderer')}")

    def _setup_poker_table(self, parent_frame):
        """Set up the PokerTableRenderer with poker table display."""
        # Do not force early geometry; allow CanvasManager to handle readiness
        parent_frame.grid_propagate(False)
        frame_width = parent_frame.winfo_width()
        frame_height = parent_frame.winfo_height()
        table_width = max(1200, max(0, frame_width) - 20) if frame_width > 0 else 1200
        table_height = max(800, max(0, frame_height) - 20) if frame_height > 0 else 800
        
        # Calculate card size based on table dimensions
        card_width = max(40, int(table_width * 0.035))
        card_height = int(card_width * 1.45)
        
        print(f"🎯 HandsReviewTab: Initial frame {frame_width}x{frame_height}, desired table {table_width}x{table_height}")
        
        # Use PokerTableRenderer as per architecture guidelines
        from ..renderers.poker_table_renderer import PokerTableRenderer

        self.table_renderer = PokerTableRenderer(
            parent_frame,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme if hasattr(self, 'theme') else None,
        )
        self.table_renderer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        
        # Access canvas manager through renderer for legacy compatibility
        self.canvas_manager = self.table_renderer.canvas_manager
        # layer_manager may not be available immediately due to deferred initialization
        if hasattr(self.table_renderer, 'layer_manager'):
            self.layer_manager = self.table_renderer.layer_manager
        else:
            self.layer_manager = None
        
        # Link EffectBus to renderer so animation bridge can draw chips
        try:
            if hasattr(self, 'effect_bus'):
                self.effect_bus.renderer = self.table_renderer
        except Exception:
            pass
        
        # Accumulate declarative effects per frame
        self._pending_effects = []
        
        # Store dimensions for state management
        self.table_width = table_width
        self.table_height = table_height
        self.card_width = card_width
        self.card_height = card_height
        
        # Initialize poker table state
        self._setup_poker_table_state()
        
        # Force table to expand to fill available space
        self._force_table_expansion()

        # Bind a one-time resize to trigger first render when ready via CanvasManager
        try:
            self._resize_bound = False
            def _on_parent_configure(event):
                if getattr(self, '_resize_bound', False):
                    return
                if event.width > 100 and event.height > 100:
                    self._resize_bound = True
                    self.table_width = event.width - 20
                    self.table_height = event.height - 20
                    try:
                        self._render_poker_table()
                    except Exception:
                        pass
            parent_frame.bind('<Configure>', _on_parent_configure)
        except Exception:
            pass
        
        print("🎨 PokerTableRenderer components ready")

    def _retry_frame_sizing(self, parent_frame):
        """Retry getting frame dimensions after a delay."""
        try:
            # Get updated frame dimensions
            frame_width = parent_frame.winfo_width()
            frame_height = parent_frame.winfo_height()
            
            if frame_width > 100 and frame_height > 100:
                # Frame is now properly sized, update table dimensions
                table_width = frame_width - 20
                table_height = frame_height - 20
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update canvas size
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    self.canvas_manager.canvas.configure(
                        width=table_width, 
                        height=table_height
                    )
                
                print(f"🎯 HandsReviewTab: Retry successful, updated to {table_width}x{table_height}")
                
                # Force table expansion
                self._force_table_expansion()
            else:
                # Still too small, try again via GameDirector
                if hasattr(self, 'game_director') and self.game_director:
                    self.game_director.schedule(100, {
                        "type": "RETRY_FRAME_SIZING",
                        "callback": lambda: self._retry_frame_sizing(parent_frame)
                    })
                else:
                    # Fallback: use timing helper
                    if hasattr(self, 'timing_helper') and self.timing_helper:
                        self.timing_helper.schedule_event(
                            delay_ms=100,
                            timing_type="delayed_action",
                            callback=lambda: self._retry_frame_sizing(parent_frame),
                            component_name="hands_review_tab"
                        )
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Retry sizing error: {e}")

    def _force_table_expansion(self):
        """Force the poker table to expand and fill the available space."""
        try:
            # Get the parent frame
            if hasattr(self, 'table_renderer') and self.table_renderer:
                parent_frame = self.table_renderer.master
                
                # Force geometry update
                parent_frame.update_idletasks()
                
                # Configure grid weights to ensure expansion
                parent_frame.grid_columnconfigure(0, weight=1)
                parent_frame.grid_rowconfigure(0, weight=1)
                
                # Force the table renderer to expand
                self.table_renderer.grid_configure(sticky="nsew")
                
                # Update canvas size to fill available space
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    # Get current frame dimensions
                    frame_width = parent_frame.winfo_width()
                    frame_height = parent_frame.winfo_height()
                    
                    # Use reasonable dimensions if frame is too small
                    if frame_width <= 100 or frame_height <= 100:
                        frame_width = 800
                        frame_height = 600
                    
                    # Set canvas size to fill frame
                    canvas_width = frame_width - 20  # Leave padding
                    canvas_height = frame_height - 20
                    
                    self.canvas_manager.canvas.configure(
                        width=canvas_width, 
                        height=canvas_height
                    )
                    
                    # Update stored dimensions
                    self.table_width = canvas_width
                    self.table_height = canvas_height
                    
                    print(f"🎯 HandsReviewTab: Forced table expansion to {canvas_width}x{canvas_height}")
                    
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Table expansion error: {e}")

    def _setup_poker_table_state(self):
        """Initialize state management for the poker table."""
        # Initialize display state for the poker table with placeholder data for visual testing
        self.display_state = {
            'table': {
                'width': self.table_width,
                'height': self.table_height
            },
            'pot': {
                'amount': 0.0,
                'side_pots': []
            },
            'seats': [
                # Placeholder seat 1 (top)
                {
                    'player_uid': 'placeholder_1',
                    'name': 'Player 1',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Ah', 'Kh'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 0
                },
                # Placeholder seat 2 (bottom) 
                {
                    'player_uid': 'placeholder_2',
                    'name': 'Player 2',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Qd', 'Jd'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 1
                }
            ],
            'board': [],  # Empty board initially (will show 5 card backs)
            'street': 'PREFLOP',  # Current street for community card rendering
            'dealer': {
                'position': 0
            },
            'action': {
                'current_player': -1,
                'action_type': None,
                'amount': 0.0,
                'highlight': False
            },
            'replay': {
                'active': False,
                'current_action': 0,
                'total_actions': 0,
                'description': "No hand loaded - showing placeholder state"
            }
        }
        
        print("🎯 HandsReviewTab state management ready with placeholder seats for visual testing")

    def _setup_event_subscriptions(self):
        """Subscribe to relevant events."""
        # Subscribe to review:load events as per architecture doc
        self.event_bus.subscribe(
            self.event_bus.topic(self.session_id, "review:load"),
            self._handle_load_hand_event,
        )

    def _refresh_hands_list(self):
        """Refresh the hands list based on current filters - prioritize GTO hands for PPSM."""
        # Check collection selection
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        # Load hands based on selection
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            # Repository hands (legendary hands)
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"

        print(f"🎯 HandsReviewTab: Loading {len(hands)} hands from {hands_source}")

        # Dispatch to store - convert Hand objects to dict format if needed
        hands_for_store = []
        for hand in hands:
            if hasattr(hand, 'metadata'):  # Hand object
                hands_for_store.append({
                    'hand_id': hand.metadata.get('hand_id', 'Unknown'),
                    'players': hand.seats,
                    'pot_size': hand.metadata.get('pot_size', 0)
                })
            else:  # Already dict format
                hands_for_store.append(hand)
                
        self.store.dispatch({"type": SET_REVIEW_HANDS, "hands": hands_for_store})

        # Update UI display
        self.hands_listbox.delete(0, tk.END)
        for i, hand in enumerate(hands):
            try:
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', f'GTO_Hand_{i+1}')
                    players_count = len(hand.seats) if hasattr(hand, 'seats') else 2
                    display_text = f"{hand_id} | {players_count}p | PPSM Ready"
                else:  # Dict format
                    hand_id = hand.get("hand_id", f"Hand_{i+1}")
                    # GTO hands use 'seats', regular hands use 'players'
                    seats = hand.get("seats", [])
                    players = hand.get("players", [])
                    # Use whichever is available
                    players_count = len(seats) if seats else len(players)
                    pot_size = hand.get("pot_size", 0)
                    small_blind = hand.get("small_blind", 5)
                    big_blind = hand.get("big_blind", 10)
                    
                    details = f"Hand ID: {hand_id}\\n"
                    details += f"Players: {players_count}\\n"
                    details += f"Pot: ${pot_size}\\n"
                    details += f"Blinds: ${small_blind}/${big_blind}\\n"
                    details += f"Source: Repository"
                self.hands_listbox.insert(tk.END, display_text)
            except Exception as e:
                # Fallback display
                self.hands_listbox.insert(tk.END, f"Hand_{i+1} | PPSM")
                print(f"⚠️ Error displaying hand {i}: {e}")

        # Update collections - prioritize GTO hands
        gto_available = hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands
        if gto_available:
            collections = ["🤖 GTO Hands", "All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        else:
            collections = ["All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        self.collection_combo["values"] = collections

        # Update status with workflow guidance based on active source
        if hands_source == "GTO":
            self._update_status(
                f"🤖 GTO Library: {len(hands)} hands loaded for PPSM testing"
            )
        else:
            stats = self.hands_repository.get_stats()
            self._update_status(
                f"📊 Repository: {stats['total_hands']} total, {stats['filtered_hands']} filtered"
            )
        self._update_status(
            "👆 SELECT a hand from the list, then click 'LOAD HAND' to begin PPSM study"
        )
        
        # Refresh poker table widget to ensure proper sizing
        if hasattr(self, '_refresh_poker_table_widget'):
            self._refresh_poker_table_widget()

    def _on_theme_change(self):
        """Handle poker table theme change for poker table."""
        theme_name = self.theme_var.get()
        print(f"🎨 HandsReviewTab: Switching to theme: {theme_name}")

        # Switch theme in the theme manager
        self.theme.set_profile(theme_name)

        # Update status to show theme change
        self._update_status(
            f"🎨 Switched to {theme_name} theme - Poker table colors applied!"
        )

        # Force poker table refresh with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with {theme_name} theme")

        # Refresh widget sizing to ensure proper fit
        self._refresh_poker_table_widget()

        # Update artistic theme introduction
        self._show_theme_intro(theme_name)

    def _show_theme_intro(self, theme_name):
        """Show artistic introduction for the selected theme with luxury museum placard styling."""
        # Get theme metadata from config-driven system
        metadata = self.theme.get_theme_metadata(theme_name)
        main_desc = metadata.get(
            "intro", "A unique poker table theme with its own distinctive character."
        )
        persona = metadata.get("persona", "")

        # Update the intro label with luxury styling
        self.theme_intro_label.config(state="normal")
        self.theme_intro_label.delete(1.0, tk.END)

        # Insert main description with elegant styling
        self.theme_intro_label.insert(tk.END, main_desc)

        # Add poker persona in italic gold if present
        if persona:
            self.theme_intro_label.insert(tk.END, "\n\n")
            persona_start = self.theme_intro_label.index(tk.INSERT)
            # Format persona with attribution
            persona_text = f"— {persona} style —"
            self.theme_intro_label.insert(tk.END, persona_text)
            persona_end = self.theme_intro_label.index(tk.INSERT)

            # Apply italic styling to persona
            self.theme_intro_label.tag_add("persona", persona_start, persona_end)
            fonts = self.theme.get_fonts()
            persona_font = fonts.get(
                "persona", fonts.get("intro", ("Georgia", 15, "italic"))
            )
            self.theme_intro_label.tag_config("persona", font=persona_font)

        self.theme_intro_label.config(state="disabled")

        # Apply DYNAMIC luxury museum placard styling based on current theme
        theme = self.theme.get_theme()

        # Dynamic theme-aware colors for museum placard
        # Use theme's panel colors but make them more luxurious
        base_bg = theme.get("panel.bg", "#1A1A1A")
        base_border = theme.get("panel.border", "#2A2A2A")
        accent_color = theme.get("table.inlay", theme.get("pot.badgeRing", "#D4AF37"))
        text_primary = theme.get("text.primary", "#F5F5DC")
        text_secondary = theme.get("text.secondary", "#E0E0C0")

        # Use hand-tuned JSON theme colors for perfect quality
        base_colors = self.theme.get_base_colors()

        # Use hand-tuned emphasis tokens for perfect theme-specific quality
        placard_bg = base_colors.get(
            "emphasis_bg_top", base_colors.get("felt", base_bg)
        )
        placard_border = base_colors.get(
            "emphasis_border", base_colors.get("rail", base_border)
        )
        text_color = base_colors.get(
            "emphasis_text", base_colors.get("text", text_primary)
        )
        persona_color = base_colors.get(
            "emphasis_accent_text", base_colors.get("accent", accent_color)
        )
        accent_glow = base_colors.get(
            "highlight", base_colors.get("metal", accent_color)
        )

        # Apply dynamic luxury styling
        self.theme_intro_label.config(
            bg=placard_bg,
            fg=text_color,
            insertbackground=text_color,
            selectbackground=accent_glow,
            selectforeground=base_colors.get("highlight_text", "#FFFFFF"),
        )

        # Style the placard frame with hand-tuned luxury border
        if hasattr(self, "placard_frame"):
            self.placard_frame.config(
                bg=placard_border,  # Hand-tuned theme border color
                relief="raised",
                borderwidth=2,  # Luxury feel
                highlightbackground=accent_glow,
                highlightcolor=accent_glow,
                highlightthickness=1,
            )

        # Apply theme-specific persona text color
        if persona:
            self.theme_intro_label.config(state="normal")
            self.theme_intro_label.tag_config("persona", foreground=persona_color)
            self.theme_intro_label.config(state="disabled")

    def _refresh_ui_colors(self):
        """Refresh poker table with new theme colors."""
        theme = self.theme.get_theme()
        print(f"🎨 HandsReviewTab: Refreshing colors for {self.theme_var.get()} theme")

        # Update poker table canvas background with new theme
        if hasattr(self, "canvas_manager") and self.canvas_manager.canvas:
            # Update canvas background to match new theme
            self.canvas_manager.canvas.configure(
                bg=theme.get("table.felt", "#1E5B44")
            )
            print(f"🎨 HandsReviewTab: Canvas background updated to {theme.get('table.felt', '#1E5B44')}")

        # Force poker table re-render with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with new theme colors")

        # Update enhanced buttons to refresh their theme
        for btn_name in ["load_btn", "next_btn", "auto_btn", "reset_btn"]:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if hasattr(btn, "refresh_theme"):
                    btn.refresh_theme()

        # Update artistic theme intro panel colors
        if hasattr(self, "theme_intro_label"):
            self._show_theme_intro(self.theme_var.get())

    def _on_library_type_change(self):
        """Handle library type change."""
        library_type = self.library_type.get()
        # TODO: Filter by library type
        self._refresh_hands_list()

    def _on_collection_change(self, event=None):
        """Handle collection selection change."""
        collection = self.collection_var.get()
        print(f"🎯 Collection changed to: {collection}")
        
        if collection == "🤖 GTO Hands":
            # GTO hands are handled in _refresh_hands_list()
            pass
        elif collection == "All Hands":
            self.hands_repository.set_filter(HandsFilter())  # Clear filter
        else:
            # TODO: Set filter for specific collection
            pass
        self._refresh_hands_list()

    def _on_hand_select(self, event):
        """Handle hand selection - prioritize GTO hands for PPSM."""
        selection = self.hands_listbox.curselection()
        if selection:
            index = selection[0]
            
            # Get hands from the same source as _refresh_hands_list
            collection = getattr(self, 'collection_var', None)
            selected_collection = collection.get() if collection else "🤖 GTO Hands"
            
            if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
                hands = self.loaded_gto_hands
                hands_source = "GTO"
            else:
                hands = self.hands_repository.get_filtered_hands()
                hands_source = "Repository"
                
            if index < len(hands):
                hand = hands[index]
                self._update_hand_details(hand)
                
                # Get hand ID based on format
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', 'Unknown')
                else:  # Dict format
                    hand_id = hand.get("hand_id", "Unknown")
                    
                # Show that hand is selected and ready to load
                self._update_status(
                    f"✅ Selected: {hand_id} ({hands_source}) - Click 'LOAD HAND' to start PPSM study"
                )

    def _update_hand_details(self, hand_data):
        """Update the hand details display - works with both Hand objects and dicts."""
        self.details_text.delete(1.0, tk.END)
        
        try:
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'metadata'):  # Hand object
                hand_id = hand_data.metadata.get('hand_id', 'Unknown')
                small_blind = hand_data.metadata.get('small_blind', 5)
                big_blind = hand_data.metadata.get('big_blind', 10)
                players_count = len(hand_data.seats) if hasattr(hand_data, 'seats') else 0
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Engine: PPSM Ready\\n"
                details += f"Source: GTO Dataset"
                
            else:  # Dict format
                hand_id = hand_data.get("hand_id", "Unknown")
                # GTO hands use 'seats', regular hands use 'players'
                seats = hand_data.get("seats", [])
                players = hand_data.get("players", [])
                # Use whichever is available
                players_count = len(seats) if seats else len(players)
                pot_size = hand_data.get("pot_size", 0)
                small_blind = hand_data.get("small_blind", 5)
                big_blind = hand_data.get("big_blind", 10)
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Pot: ${pot_size}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Source: Repository"
                
        except Exception as e:
            details = f"Hand details unavailable: {e}"
            
        self.details_text.insert(1.0, details)

    def _on_study_mode_change(self):
        """Handle study mode change."""
        mode = self.study_mode.get()
        self.store.dispatch({"type": SET_STUDY_MODE, "mode": mode})
        self._update_status(f"📚 Study mode: {mode}")

    def _apply_filters(self):
        """Apply current filter settings."""
        filter_criteria = HandsFilter()

        # Apply position filter
        if self.position_var.get() != "All":
            filter_criteria.positions = [self.position_var.get()]

        # Apply stack depth filter
        try:
            filter_criteria.min_stack_depth = (
                int(self.min_stack.get()) if self.min_stack.get() else None
            )
            filter_criteria.max_stack_depth = (
                int(self.max_stack.get()) if self.max_stack.get() else None
            )
        except ValueError:
            pass

        # Apply pot type filter
        if self.pot_type_var.get() != "All":
            filter_criteria.pot_type = self.pot_type_var.get()

        # Apply search text
        filter_criteria.search_text = self.search_var.get()

        # Set filter and refresh
        self.hands_repository.set_filter(filter_criteria)
        self.store.dispatch(
            {"type": SET_REVIEW_FILTER, "filter": filter_criteria.__dict__}
        )
        self._refresh_hands_list()

    def _load_selected_hand(self):
        """Load the selected hand for PPSM study."""
        selection = self.hands_listbox.curselection()
        if not selection:
            self._update_status("❌ Please select a hand to load")
            return

        index = selection[0]
        
        # Get hands from the same source as _refresh_hands_list
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"
            
        if index >= len(hands):
            return

        hand_data = hands[index]
        
        print(f"🎯 Loading {hands_source} hand for PPSM study...")

        # Publish load event as per architecture doc
        self.event_bus.publish(
            self.event_bus.topic(self.session_id, "review:load"), hand_data
        )

    def _handle_load_hand_event(self, hand_data):
        """Handle the review:load event - pure UI logic only."""
        try:
            hand_id = hand_data.get("metadata", {}).get("hand_id", "Unknown")
            self._update_status(f"🔄 Loading hand {hand_id}...")

            # Store hand data for reset functionality
            self.current_hand_data = hand_data

            # Use session manager to load hand (business logic)
            if self.session_manager:
                session_state = self.session_manager.load_hand(hand_data)
                
                # Update UI based on session state
                total_actions = session_state.total_actions
                if total_actions > 0:
                    self.progress_label.config(
                        text=f"Hand loaded: {total_actions} actions"
                    )
                    print(f"🎯 HandsReviewTab: Hand {hand_id} loaded with {total_actions} actions")
                else:
                    self.progress_label.config(text="No actions available")
                    print(f"⚠️ HandsReviewTab: Hand {hand_id} loaded but no actions found")
                
                self._update_status(f"✅ Hand {hand_id} loaded via session manager")
            else:
                self._update_status(f"❌ Session manager not available")
                print(f"❌ HandsReviewTab: Session manager not available")

        except Exception as e:
            print(f"❌ HandsReviewTab: Error loading hand: {e}")
            self._update_status(f"❌ Error loading hand: {e}")

    def _toggle_auto_play(self):
        """Toggle poker table auto-play mode."""
        if not hasattr(self, 'hand_actions') or not self.hand_actions:
            print("⚠️ HandsReviewTab: No hand actions available for auto-play")
            return
        
        if not hasattr(self, 'auto_play_active'):
            self.auto_play_active = False
        
        self.auto_play_active = not self.auto_play_active
        
        if self.auto_play_active:
            print("🎬 HandsReviewTab: Auto-play started")
            self.auto_btn.config(text="Stop Auto")
            self._run_auto_play()
        else:
            print("⏹️ HandsReviewTab: Auto-play stopped")
            self.auto_btn.config(text="Auto")

    def _run_auto_play(self):
        """Run poker table auto-play using GameDirector."""
        if not hasattr(self, 'auto_play_active') or not self.auto_play_active:
            return
        
        if self.current_action_index >= len(self.hand_actions):
            self.auto_play_active = False
            self.auto_btn.config(text="Auto")
            print("✅ HandsReviewTab: Auto-play complete")
            return
        
        # Use GameDirector for coordinated action execution
        if hasattr(self, 'game_director'):
            self.game_director.play()
            print("🎬 GameDirector: Auto-play started")
        else:
            # ARCHITECTURE COMPLIANT: Use GameDirector for timing
            self._next_action()
            if hasattr(self, 'game_director') and self.game_director:
                self.game_director.schedule(1000, {
                    "type": "AUTO_PLAY_NEXT",
                    "callback": self._run_auto_play
                })
            else:
                print("⚠️ GameDirector not available for auto-play timing")



    def _update_status(self, message: str):
        """Update the status display."""
        self.status_text.insert(tk.END, f"\n{message}")
        self.status_text.see(tk.END)

    def _on_store_change(self, state):
        """Handle store state changes for poker table rendering."""
        try:
            # Check if we have poker table state to update
            if hasattr(self, 'display_state') and 'poker_table' in state:
                # Update local display state from store
                self.display_state.update(state['poker_table'])
                
                # Re-render the table with updated state
                self._render_poker_table()
                
                # Handle animation events
                if 'animation_event' in state.get('poker_table', {}):
                    self._handle_animation_event(
                        state['poker_table']['animation_event']
                    )
                    
                print("🔄 HandsReviewTab: State updated from store")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Store change handling error: {e}")

    def _handle_animation_event(self, animation_event):
        """Handle animation events from the store."""
        try:
            if animation_event.get('action') == 'clear_highlight':
                self._clear_highlight()
                print("🎬 HandsReviewTab: Animation event processed")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation event handling error: {e}")

    def _refresh_fonts(self):
        """Refresh fonts after theme changes."""
        fonts = self.theme.get_fonts()

        # Update listbox font
        if hasattr(self, "hands_listbox"):
            body_font = fonts.get("body", ("Consolas", 20))
            self.hands_listbox.configure(font=body_font)

        # Update text areas
        small_font = fonts.get("small", ("Consolas", 16))
        if hasattr(self, "details_text"):
            self.details_text.configure(font=small_font)
        if hasattr(self, "status_text"):
            self.status_text.configure(font=small_font)

        # Update theme intro label font (luxury serif)
        if hasattr(self, "theme_intro_label"):
            intro_font = fonts.get(
                "intro", fonts.get("body", ("Georgia", 16, "normal"))
            )
            self.theme_intro_label.configure(font=intro_font)
    
    def _start_update_loop(self):
        """Start the main update loop for GameDirector and EffectBus."""
        def update_loop():
            try:
                # Update GameDirector
                if hasattr(self, 'game_director'):
                    self.game_director.update()
                
                # Update EffectBus
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()
                
                # Schedule next update (60 FPS)
                self.after(16, update_loop)
                
            except Exception as e:
                print(f"⚠️ Update loop error: {e}")
                # Continue update loop even if there's an error
                self.after(16, update_loop)
        
        # Start the update loop
        update_loop()
        print("🔄 Update loop started for GameDirector and EffectBus")
    
    def _start_ui_tick_loop(self):
        """Start the UI tick loop for GameDirector and EffectBus every ~16ms."""
        def _tick():
            try:
                # Pump GameDirector and EffectBus every ~16ms (60 FPS)
                if hasattr(self, 'game_director'):
                    self.game_director.update(16.7)  # pump scheduled events
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()  # if bus keeps any transient state
            except Exception as e:
                print(f"⚠️ UI tick loop error: {e}")
            finally:
                # Schedule next tick
                self.after(16, _tick)
        
        # Start the tick loop
        _tick()
        print("⏱️ UI tick loop started for GameDirector and EffectBus (60 FPS)")

    def _handle_renderer_intent(self, intent: dict):
        """Handle intents emitted by PokerTableRenderer (state-driven).
        Currently forwards REQUEST_ANIMATION to EffectBus via event bus.
        """
        try:
            t = intent.get("type")
            if t == "REQUEST_ANIMATION" and hasattr(self, 'event_bus'):
                payload = intent.get("payload", {})
                name = payload.get("name")
                # Map declarative types to bridge names if not provided
                if not name:
                    et = payload.get("type")
                    if et == "CHIP_TO_POT":
                        name = "chips_to_pot"
                    elif et == "POT_TO_WINNER":
                        name = "pot_to_winner"
                self.event_bus.publish("effect_bus:animate", {"name": name, "args": payload})
        except Exception:
            pass
    
    def _setup_action_banner(self):
        """Setup ActionBanner and connect it to EffectBus events."""
        try:
            if ActionBanner:
                # Create ActionBanner at the top of the poker table section
                self.action_banner = ActionBanner(self)
                
                # Subscribe to EffectBus banner events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:banner_show", self._handle_banner_event)

                # Subscribe to EffectBus animation events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:animate", self._handle_effect_animate)
                    print("🎞️ Animation: Connected to EffectBus events")
                    print("🎭 ActionBanner: Connected to EffectBus events")
                else:
                    print("⚠️ ActionBanner: No event bus available")
            else:
                print("⚠️ ActionBanner: Not available, skipping setup")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Setup error: {e}")
    
    def _handle_banner_event(self, event_data):
        """Handle banner events from EffectBus."""
        try:
            if hasattr(self, 'action_banner'):
                message = event_data.get('message', '')
                banner_type = event_data.get('banner_type', 'info')
                duration_ms = event_data.get('duration_ms', 3000)
                
                self.action_banner.show_banner(message, banner_type, duration_ms)
                print(f"🎭 ActionBanner: Showing banner: {message}")
            else:
                print("⚠️ ActionBanner: Not available for banner event")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Banner event error: {e}")

        # Update enhanced button themes (handles both fonts and colors)
        enhanced_buttons = []
        if hasattr(self, "load_btn") and hasattr(self.load_btn, "refresh_theme"):
            enhanced_buttons.append(self.load_btn)
        if hasattr(self, "next_btn") and hasattr(self.next_btn, "refresh_theme"):
            enhanced_buttons.append(self.next_btn)
        if hasattr(self, "auto_btn") and hasattr(self.auto_btn, "refresh_theme"):
            enhanced_buttons.append(self.auto_btn)
        if hasattr(self, "reset_btn") and hasattr(self.reset_btn, "refresh_theme"):
            enhanced_buttons.append(self.reset_btn)

        for btn in enhanced_buttons:
            btn.refresh_theme()

    def _handle_effect_animate(self, payload):
        """Handle animation requests from EffectBus using ChipAnimations where possible."""
        try:
            name = (payload or {}).get("name")
            ms = int((payload or {}).get("ms", 300))
            if not getattr(self, "canvas_manager", None):
                return
            c = self.canvas_manager.canvas
            
            # Get theme manager from the correct location
            theme_manager = getattr(self, 'theme', None)
            if not theme_manager:
                print("⚠️ No theme manager available for animations")
                return
                
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)
            
            # Get proper pot center from display state
            pot_center = (self.canvas_manager.canvas.winfo_width() // 2, 
                         int(self.canvas_manager.canvas.winfo_height() * 0.52))
            
            # Get seat positions for proper animation coordinates
            seats = self.display_state.get("seats", [])
            if not seats:
                return
                
            # Get consistent seat positions for animation
            w, h = self.canvas_manager.size()
            from ..state.selectors import get_seat_positions
            seat_positions = get_seat_positions(self.display_state, seat_count=len(seats), 
                                              canvas_width=w, canvas_height=h)
            
            if name == "betting_action":
                # Handle betting actions (BET, RAISE, CALL, CHECK, FOLD)
                action_type = (payload or {}).get("action_type", "UNKNOWN")
                actor_uid = (payload or {}).get("actor_uid", "Unknown")
                
                print(f"🎬 Betting action animation: {action_type} by {actor_uid}")
                
                # Find the acting player for source position with robust normalization
                def _norm(v):
                    return str(v).strip().lower()

                actor_norm = _norm(actor_uid)
                acting_seat = None

                # Build lookup maps
                uid_to_idx = { _norm(s.get('player_uid')): i for i, s in enumerate(seats) }
                name_to_idx = { _norm(s.get('name', '')): i for i, s in enumerate(seats) }

                # Prefer player_uid
                if actor_norm in uid_to_idx:
                    acting_seat = seats[uid_to_idx[actor_norm]]
                elif actor_norm in name_to_idx:
                    acting_seat = seats[name_to_idx[actor_norm]]
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating {action_type} from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        
                        # Different animation based on action type
                        if action_type in ["BET", "RAISE", "CALL"]:
                            # Animate chips to pot
                            anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                        elif action_type == "CHECK":
                            # Visual feedback for check (no chips)
                            print(f"🎬 Check action - no chip animation needed")
                        elif action_type == "FOLD":
                            # Visual feedback for fold (maybe card flip or seat dimming)
                            print(f"🎬 Fold action - seat dimming effect")
                else:
                    print(f"⚠️ No seat found for actor {actor_uid} in betting action animation")
                    
            elif name == "chips_to_pot":
                # This should ONLY happen at end of street (DEAL_BOARD, DEAL_TURN, DEAL_RIVER)
                # NOT during betting rounds
                print(f"🎬 End-of-street animation: chips flying to pot")
                
                # Find the acting player for source position
                acting_seat = None
                for seat in seats:
                    if seat.get('acting', False):
                        acting_seat = seat
                        break
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating chips from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                else:
                    print("⚠️ No acting seat found for chips_to_pot animation")
                    
            elif name == "pot_to_winner":
                # This is for showdown/end of hand
                print(f"🎬 Showdown animation: pot flying to winner")
                
                # Find winner seat
                winner = None
                for seat in seats:
                    if not seat.get("folded", False):
                        winner = seat
                        break
                
                if winner:
                    # Get winner position using consistent positioning
                    winner_idx = seats.index(winner)
                    if winner_idx < len(seat_positions):
                        wx, wy = seat_positions[winner_idx]
                        
                        print(f"🎬 Animating pot to winner {winner.get('name', 'Unknown')} at ({wx}, {wy})")
                        anim.fly_pot_to_winner(c, pot_center[0], pot_center[1], wx, wy, amount=200, callback=None)
                else:
                    print("⚠️ No winner found for pot_to_winner animation")
                    
        except Exception as e:
            print(f"⚠️ Animation handler error: {e}")
            import traceback
            traceback.print_exc()

    def _style_theme_radio_buttons(self):
        """Apply theme-specific styling to radio buttons to eliminate default green highlights."""
        if not hasattr(self, "theme_radio_buttons"):
            return

        try:
            # Get current theme and highlight colors
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            theme = self.theme.get_theme()

            # Create a custom style for radio buttons
            style = ttk.Style()

            # Apply config-driven selection styling
            selection_styler = self.theme.get_selection_styler()
            if selection_styler:
                theme_id = self.theme.get_current_theme_id()
                selection_styler.apply_selection_styles(style, theme_id)

            # Get selection highlight colors (config-driven with legacy fallback)
            try:
                base_colors = self.theme.get_base_colors()
                selection_color = base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
                selection_glow = base_colors.get(
                    "metal", base_colors.get("accent", "#C9A34E")
                )
            except Exception:
                # Get selection highlight from config-driven system
                base_colors = self.theme.get_base_colors()
                selection_highlight = {
                    "color": base_colors.get(
                        "highlight", base_colors.get("accent", "#D4AF37")
                    )
                }
                selection_color = selection_highlight["color"]
                selection_glow = selection_highlight.get("glow", "#C9A34E")

            # Configure the radio button style with theme-specific colors
            style.configure(
                "Themed.TRadiobutton",
                background=theme.get("panel.bg", "#1F2937"),
                foreground=theme.get("panel.fg", "#E5E7EB"),
                focuscolor=selection_color,
            )

            # Configure the selection/active state colors
            style.map(
                "Themed.TRadiobutton",
                background=[
                    ("active", theme.get("panel.bg", "#1F2937")),
                    ("selected", theme.get("panel.bg", "#1F2937")),
                ],
                foreground=[
                    ("active", theme.get("panel.fg", "#E5E7EB")),
                    ("selected", theme.get("panel.fg", "#E5E7EB")),
                ],
                indicatorcolor=[
                    ("selected", selection_color),
                    ("active", selection_glow),
                    ("!selected", theme.get("panel.border", "#374151")),
                ],
            )

            # Apply the custom style to all radio buttons
            for radio_btn in self.theme_radio_buttons:
                if radio_btn.winfo_exists():
                    radio_btn.configure(style="Themed.TRadiobutton")

        except Exception as e:
            # Fallback styling if custom styling fails
            print(f"⚠️ Radio button styling failed: {e}")
            pass


    def _next_action(self):
        """Dispatch next action intent - pure UI logic only."""
        print("🎯 NEXT_ACTION: Button clicked!")

        # ARCHITECTURE COMPLIANT: Dispatch action to Store instead of direct service call
        try:
            self.store.dispatch({
                "type": "HANDS_REVIEW_NEXT_ACTION",
                "session_id": self.session_id,
                "timestamp": time.time()
            })
            print("🎯 NEXT_ACTION: Action dispatched to Store")
        except Exception as e:
            print(f"⚠️ NEXT_ACTION: Failed to dispatch action: {e}")
            self._update_status(f"❌ Error dispatching next action: {e}")
    
    def _render_table_with_state(self, session_state):
        """Render poker table with session state - pure UI logic only."""
        try:
            # Convert session state to PokerTableState
            from ..table.state import PokerTableState
            
            table_state = PokerTableState(
                table=session_state.table,
                seats=session_state.seats,
                board=session_state.board,
                pot=session_state.pot,
                dealer=session_state.dealer,
                action=session_state.action,
                animation=session_state.animation,
                effects=session_state.effects,
                street=session_state.street
            )
            
            # Render using PokerTableRenderer
            if hasattr(self, 'table_renderer') and self.table_renderer:
                self.table_renderer.render(table_state)
                print("🎯 HandsReviewTab: Table rendered with session state")
            else:
                print("⚠️ HandsReviewTab: Table renderer not available")
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error rendering table: {e}")

    def _reset_hand(self):
        """Reset the current hand to the beginning - pure UI logic only."""
        if not self.session_manager:
            self._update_status("⚠️ Session manager not available")
            return

        try:
            # Reset hand via session manager (business logic)
            if hasattr(self, "last_loaded_hand") and self.last_loaded_hand:
                session_state = self.session_manager.load_hand(self.last_loaded_hand)
                self._update_status("🔄 Hand reset to beginning")
                
                # Render table with reset state
                self._render_table_with_state(session_state)
            else:
                self._update_status("⚠️ No hand to reset")
        except Exception as e:
            self._update_status(f"❌ Error resetting hand: {e}")

    def on_show(self):
        """Called when tab is shown - refresh display."""
        if hasattr(self, "renderer_pipeline"):
            state = self.store.get_state()
            self.renderer_pipeline.render_once(state)

    def dispose(self):
        """Clean up when tab is closed."""
        # ARCHITECTURE COMPLIANT: Notify event controller of session disposal
        try:
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.publish(
                    "hands_review:session_disposed",
                    {"session_id": self.session_id}
                )
                print(f"🎯 HandsReviewTab: Session {self.session_id} disposal notified")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Failed to notify session disposal: {e}")
        
        # Clean up session manager if active
        if self.session_manager:
            self.session_manager.cleanup()
            self.session_manager = None
        self.services.dispose_session(self.session_id)

    def _load_gto_hands(self):
        """Load GTO hands for PPSM testing."""
        try:
            import json
            import os
            
            gto_hands_file = "gto_hands.json"
            print(f"🔍 Looking for GTO hands file: {gto_hands_file}")
            
            if os.path.exists(gto_hands_file):
                print(f"📂 Found GTO hands file, loading...")
                with open(gto_hands_file, 'r') as f:
                    hands_data = json.load(f)
                    
                print(f"📊 Raw GTO hands data: {len(hands_data)} hands")
                    
                # Convert to Hand objects
                self.loaded_gto_hands = []
                for i, hand_data in enumerate(hands_data):
                    try:
                        hand = Hand(**hand_data)  # Create proper Hand object
                        self.loaded_gto_hands.append(hand)
                    except Exception as e:
                        print(f"⚠️ Error creating Hand object for hand {i}: {e}")
                        # Fallback: store as dict
                        self.loaded_gto_hands.append(hand_data)
                        
                print(f"✅ Loaded {len(self.loaded_gto_hands)} GTO hands for PPSM testing")
            else:
                print(f"⚠️ GTO hands file not found: {gto_hands_file}")
                self.loaded_gto_hands = []
                
        except Exception as e:
            print(f"⚠️ Error loading GTO hands: {e}")
            self.loaded_gto_hands = []

    def _load_hand(self, hand_data):
        """Load hand data into poker table using new architecture."""
        try:
            # Store the hand data for reference
            self.current_hand_data = hand_data
            
            # Flatten hand actions for step-by-step replay
            self.hand_actions = self._flatten_hand_for_replay(hand_data)
            
            # Reset action index
            self.current_action_index = 0
            
            # Create display state from hand data
            new_display_state = self._create_display_state_from_hand(hand_data)
            
            # Update the existing display state with new data
            self.display_state.update(new_display_state)
            
            # Dispatch LOAD_REVIEW_HAND action to store
            self.store.dispatch({
                "type": "LOAD_REVIEW_HAND",
                "hand_data": hand_data,
                "flattened_actions": self.hand_actions
            })
            
            # Update progress display
            if self.hand_actions:
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                self.progress_label.config(text=progress_text)
                # Enable next button
                self.next_btn.config(state="normal")
                
                # Setup GameDirector for this hand
                if hasattr(self, 'game_director'):
                    self.game_director.set_total_steps(len(self.hand_actions))
                    self.game_director.set_advance_callback(self._execute_action_at_index)
                    print(f"🎬 GameDirector: Configured for {len(self.hand_actions)} actions")
            
            # Render the table
            self._render_poker_table()
            
            # Refresh widget to ensure proper sizing
            self._refresh_poker_table_widget()
            
            print(f"✅ HandsReviewTab: Hand loaded with {len(self.hand_actions)} actions")
        
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error loading hand: {e}")

    def _create_display_state_from_hand(self, hand_data):
        """Create display state from hand data for poker table."""
        try:
            # Debug: Log the raw hand data
            print(f"🎯 Creating display state from hand data:")
            print(f"   Hand data type: {type(hand_data)}")
            print(f"   Hand data keys: {list(hand_data.keys()) if hasattr(hand_data, 'keys') else 'N/A'}")
            
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'seats'):  # Hand object
                seats = hand_data.seats
                metadata = hand_data.metadata
                print(f"   Using Hand object: {len(seats)} seats")
            else:  # Dict format
                seats = hand_data.get('seats', [])
                metadata = hand_data.get('metadata', {})
                print(f"   Using dict format: {len(seats)} seats")
            
            print(f"   Raw seats data: {seats}")
            print(f"   Metadata: {metadata}")
            
            # Extract basic hand information
            small_blind = metadata.get('small_blind', 5) if metadata else 5
            big_blind = metadata.get('big_blind', 10) if metadata else 10
            
            print(f"   Extracted {len(seats)} seats, SB: {small_blind}, BB: {big_blind}")
            
            # Create initial display state with actual table dimensions
            display_state = {
                'table': {
                    'width': getattr(self, 'table_width', 800),
                    'height': getattr(self, 'table_height', 600),
                    'theme': 'luxury_noir'  # Default theme
                },
                'pot': {
                    'amount': 0,
                    'position': (400, 300)
                },
                'seats': [],
                'board': [],
                'dealer': {'position': 0},
                'action': {'type': None, 'player': None, 'amount': 0},
                'replay': {'current_step': 0, 'total_steps': 0}
            }
            
            # Set up seats from GTO hand data
            for i, seat in enumerate(seats):
                player_uid = seat.get('player_uid', f'player_{i}')
                name = seat.get('display_name', f'Player {i+1}')
                starting_stack = seat.get('starting_stack', 1000)
                
                # Calculate seat position (simplified for now)
                angle = (2 * 3.14159 * i) / len(seats)
                radius = 200
                x = 400 + int(radius * math.cos(angle))
                y = 300 + int(radius * math.sin(angle))
                
                # Get hole cards for this player from metadata
                if hasattr(hand_data, 'metadata') and hasattr(hand_data.metadata, 'hole_cards'):
                    hole_cards = hand_data.metadata.hole_cards.get(player_uid, [])
                else:
                    hole_cards = metadata.get('hole_cards', {}).get(player_uid, [])
                
                seat_data = {
                    'player_uid': player_uid,
                    'name': name,
                    'starting_stack': starting_stack,
                    'current_stack': starting_stack,
                    'current_bet': 0,
                    # Backwards-compatible keys used by renderer components
                    'stack': starting_stack,
                    'bet': 0,
                    'cards': hole_cards,  # Populate with actual hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': i
                }
                
                # Set initial blinds based on seat order
                if i == 0:  # Small blind
                    seat_data['current_bet'] = small_blind
                    seat_data['current_stack'] -= small_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'SB'
                elif i == 1:  # Big blind
                    seat_data['current_bet'] = big_blind
                    seat_data['current_stack'] -= big_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'BB'
                
                display_state['seats'].append(seat_data)
                print(f"   🪑 Created seat {i}: {name} at ({x}, {y}) with cards {hole_cards}")
            
            print(f"🎯 HandsReviewTab: Created display state with {len(display_state['seats'])} seats")
            for seat in display_state['seats']:
                print(f"  🪑 {seat['name']}: {seat['cards']} (stack: {seat['current_stack']}, bet: {seat['current_bet']})")
            
            return display_state
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error creating display state: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _flatten_hand_for_replay(self, hand):
        """Produce a list of 'steps' to drive the poker table UI."""
        steps = []

        # Synthesize: deal hole cards
        holes = (hand.get("metadata", {}) or {}).get("hole_cards", {}) or {}
        steps.append({
            "type": "DEAL_HOLE",
            "desc": "🃏 Deal hole cards",
            "payload": {"hole_cards": holes},
        })

        streets = hand.get("streets", {}) or {}
        # Keep deterministic street order
        for street_name in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            if street_name not in streets:
                continue
            s = streets[street_name] or {}
            actions = s.get("actions", []) or []
            board = s.get("board", []) or []

            # If board present, add board-deal step
            if street_name != "PREFLOP" and board:
                steps.append({
                    "type": "DEAL_BOARD",
                    "desc": f"🂠 Deal {street_name} board: {', '.join(board)}",
                    "payload": {"street": street_name, "board": board},
                })

            for a in actions:
                # Handle different action types
                action_type = a.get("action", "UNKNOWN")
                actor = a.get("actor_uid", "Unknown")
                amount = a.get("amount", 0)
                
                if action_type == "POST_BLIND":
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type in ["BET", "RAISE", "CALL"]:
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type == "CHECK":
                    desc = f"{street_name}: {actor} → {action_type}"
                elif action_type == "FOLD":
                    desc = f"{street_name}: {actor} → {action_type}"
                else:
                    desc = f"{street_name}: {actor} → {action_type} {amount if amount else ''}"
                
                steps.append({
                    "type": action_type,
                    "desc": desc,
                    "payload": {"street": street_name, **a},
                })

        # Terminal step
        steps.append({"type": "END_HAND", "desc": "✅ End of hand", "payload": {}})
        return steps

    def _render_poker_table(self):
        """Render the poker table using the component pipeline."""
        try:
            # Debug: Log what's in the display state
            print(f"🎯 Rendering table with state:")
            print(f"   Seats: {len(self.display_state.get('seats', []))}")
            print(f"   Board: {self.display_state.get('board', [])}")
            print(f"   Pot: {self.display_state.get('pot', {}).get('amount', 0)}")
            
            if self.display_state.get('seats'):
                for i, seat in enumerate(self.display_state['seats']):
                    print(f"   Seat {i}: {seat}")
            
            # Build PokerTableState and render
            try:
                from ..table.state import PokerTableState
            except Exception:
                # Inline lightweight structure if import fails
                class PokerTableState(dict):
                    pass

            state = PokerTableState(
                table={"width": self.table_width, "height": self.table_height},
                seats=self.display_state.get('seats', []),
                board=self.display_state.get('board', []),
                pot=self.display_state.get('pot', {}),
                dealer={"position": self.display_state.get('dealer', 0)},
                action=self.display_state.get('action', {}),
                animation={},
                effects=list(self._pending_effects),
                street=self.display_state.get('street', 'PREFLOP'),  # Pass street for community cards
            )
            # Clear effects after issuing
            self._pending_effects.clear()
            
            # Let PokerTableRenderer handle its own readiness checking and deferral
            print("🎯 HandsReviewTab: Attempting to render via PokerTableRenderer")
                
            self.table_renderer.render(state)
            print("🎨 HandsReviewTab: Table rendered successfully (state-driven)")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Render error: {e}")
            import traceback
            traceback.print_exc()


    
    def _execute_action_step(self, action):
        """Execute a single action step and update display state."""
        try:
            action_type = action.get('type', 'UNKNOWN')
            payload = action.get('payload', {})
            
            # Get player name for effects
            actor_uid = payload.get('actor_uid', 'Unknown')
            player_name = None
            for seat in self.display_state['seats']:
                if seat['player_uid'] == actor_uid:
                    player_name = seat.get('name', actor_uid)
                    break
            

            # Update acting highlight: set only the actor as acting
            try:
                for s in self.display_state.get('seats', []):
                    s['acting'] = (s.get('player_uid') == actor_uid)
            except Exception:
                pass
                
            # optional: re-render to reflect highlight immediately
            try:
                self.renderer_pipeline.render_once(self.display_state)
            except Exception:
                pass
            
            if action_type == "DEAL_HOLE":
                # Hole cards are already loaded in initial state
                print(f"🃏 HandsReviewTab: Hole cards dealt")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_HOLE", player_name)
                
            elif action_type == "DEAL_BOARD":
                street = payload.get('street', 'UNKNOWN')
                board = payload.get('board', [])
                self.display_state['board'] = board
                self.display_state['street'] = street  # Update street for community card rendering
                print(f"🂠 HandsReviewTab: Dealt {street} board: {board}")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_BOARD", player_name)
                
                # Professional poker behavior: Animate chips to pot at end of street
                # This clears all bet chips from in front of players and moves them to pot
                if street in ["FLOP", "TURN", "RIVER"]:
                    try:
                        from ..state.selectors import get_seat_positions
                        w, h = self.table_renderer.canvas_manager.size() if hasattr(self, 'table_renderer') else (self.table_width, self.table_height)
                        positions = get_seat_positions(self.display_state, seat_count=len(self.display_state.get('seats', [])), canvas_width=w, canvas_height=h)
                        
                        # Find any seat with bets to animate from (use first betting seat)
                        for seat_idx, seat in enumerate(self.display_state.get('seats', [])):
                            if seat.get('current_bet', 0) > 0 and seat_idx < len(positions):
                                fx, fy = positions[seat_idx]
                                pot_x, pot_y = (w // 2, int(h * 0.58))
                                self._pending_effects.append({
                                    "type": "CHIP_TO_POT",
                                    "from_x": int(fx), "from_y": int(fy),
                                    "to_x": pot_x, "to_y": pot_y,
                                    "amount": seat.get('current_bet', 0),
                                })
                                print(f"🎬 End-of-street: Moving chips from seat {seat_idx} to pot for {street}")
                                break
                    except Exception as e:
                        print(f"⚠️ Could not add end-of-street animation: {e}")
                
            elif action_type in ["BET", "RAISE", "CALL", "CHECK", "FOLD"]:
                amount = payload.get('amount', 0)
                
                # Update the appropriate seat's bet and stack
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        if action_type in ["BET", "RAISE"]:
                            # For BET/RAISE, amount is the total bet
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = action_type.lower()  # Add last_action for bet styling
                        elif action_type == "CALL":
                            # For CALL, amount is the total bet to match
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = "call"  # Add last_action for bet styling
                        elif action_type == "CHECK":
                            # CHECK doesn't change bet or stack
                            seat['last_action'] = "check"  # Add last_action for bet styling
                        elif action_type == "FOLD":
                            seat['folded'] = True
                            seat['last_action'] = "fold"  # Add last_action for bet styling
                            # Folded players keep their current bet
                        
                        # Set acting flag for highlighting on this seat only
                        seat['acting'] = True
                        break

                # Clear acting flag from other seats using different loop variable
                for s2 in self.display_state['seats']:
                    if s2.get('player_uid') != actor_uid:
                        s2['acting'] = False
                
                # Update pot amount
                if action_type in ["BET", "RAISE", "CALL"]:
                    total_pot = sum(seat['current_bet'] for seat in self.display_state['seats'])
                    self.display_state['pot']['amount'] = total_pot
                
                print(f"🎯 HandsReviewTab: {actor_uid} {action_type} {amount if amount else ''}")
                print(f"🎯 Seat state updated: current_bet={seat.get('current_bet', 0)}, last_action={seat.get('last_action', 'none')}")
                
                # Add action sound effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects(action_type, player_name)

                # Professional poker behavior: Only animate chips to pot at END of streets
                # Individual bets/calls just place chips in front of players
                # (CHIP_TO_POT animation will be triggered by DEAL_FLOP, DEAL_TURN, DEAL_RIVER actions)
                
                # Show action banner for immediate visual feedback
                if hasattr(self, 'action_banner'):
                    amount = payload.get('amount', 0)
                    self.action_banner.show_poker_action(action_type, player_name, amount)

                # Re-render immediately after state updates to ensure highlight and bets update
                try:
                    self.renderer_pipeline.render_once(self.display_state)
                except Exception:
                    pass
                
            elif action_type == "POST_BLIND":
                amount = payload.get('amount', 0)
                
                # Update seat bet and stack for blind posting
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        seat['current_bet'] = amount
                        seat['current_stack'] -= amount
                        break
                
                print(f"💰 HandsReviewTab: {actor_uid} posted blind: {amount}")
                
                # Add blind posting sounds (chips stay in front of player until street ends)
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("POST_BLIND", player_name)
            
            # Re-render the table with updated state
            self._render_poker_table()
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing action step: {e}")
    
    def _execute_action_at_index(self, action_index: int):
        """Execute action at specific index - called by GameDirector."""
        try:
            if 0 <= action_index < len(self.hand_actions):
                self.current_action_index = action_index
                action = self.hand_actions[action_index]
                
                # Execute the action
                self._execute_action_step(action)
                
                # Update progress display
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                if hasattr(self, 'progress_label'):
                    self.progress_label.config(text=progress_text)
                
                print(f"🎬 GameDirector: Executed action at index {action_index}")
            else:
                print(f"⚠️ GameDirector: Invalid action index {action_index}")
                
        except Exception as e:
            print(f"⚠️ GameDirector: Error executing action at index {action_index}: {e}")

    def _prev_action(self):
        """Execute previous action using proper Store-based architecture."""
        try:
            # Check if we have actions to execute
            if not hasattr(self, 'hand_actions') or not self.hand_actions:
                print("⚠️ HandsReviewTab: No hand actions available")
                return
            
            # Check if we can go to previous action
            if self.current_action_index <= 0:
                print("⚠️ HandsReviewTab: Already at first action")
                return
            
            # Move to previous action
            self.current_action_index -= 1
            action = self.hand_actions[self.current_action_index]
            
            # Execute the action to update display state
            self._execute_action_step(action)
            
            # Update progress display
            progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=progress_text)
            
            # Dispatch action to store for state management
            self.store.dispatch({
                "type": "PREV_REVIEW_ACTION"
            })
            
            print(f"🎬 HandsReviewTab: Executed previous action {self.current_action_index}: {action.get('type', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing previous action: {e}")



    def _execute_action(self, action):
        """Execute action and update poker table state with rich UI/UX features."""
        # REMOVED: This method should not contain business logic
        # Business logic should be in PPSM or Store reducers
        # UI should only dispatch actions and render state
        pass

    def _play_sound(self, sound_type):
        """Play sound effects for poker table actions."""
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                # Map sound types to sound manager events
                sound_mapping = {
                    'card_deal': 'card_deal',
                    'chip_bet': 'chip_bet',
                    'player_bet': 'player_action_bet',
                    'player_call': 'player_action_call',
                    'player_check': 'player_action_check',
                    'player_fold': 'player_action_fold',
                    'hand_end': 'hand_end'
                }
                
                event_name = sound_mapping.get(sound_type, sound_type)
                self.sound_manager.play(event_name)
                print(f"🔊 HandsReviewTab: Playing {sound_type} sound")
            else:
                print(f"🔇 HandsReviewTab: No sound manager available for {sound_type}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Sound error for {sound_type}: {e}")

    def _schedule_animation(self):
        """Schedule animation effects using event-driven system."""
        try:
            # Use event bus instead of direct UI timing (architectural compliance)
            if hasattr(self, 'event_bus'):
                self.event_bus.publish(
                    self.event_bus.topic(self.session_id, "poker_table:animation"),
                    {
                        "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                        "delay_ms": 200,
                        "action": "clear_highlight"
                    }
                )
                print(f"🎬 HandsReviewTab: Scheduled animation via event bus")
            else:
                print(f"⚠️ HandsReviewTab: No event bus available for animation")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation scheduling error: {e}")

    def _clear_highlight(self):
        """Clear player highlighting after animation."""
        try:
            if hasattr(self, 'display_state') and 'action' in self.display_state:
                self.display_state['action']['highlight'] = False
                # Re-render to show cleared highlight
                self._render_poker_table()
                print(f"🎬 HandsReviewTab: Cleared action highlight")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Highlight clear error: {e}")

    def _refresh_poker_table_widget(self):
        """Refresh the poker table widget to ensure proper sizing and fit."""
        try:
            if hasattr(self, 'canvas_manager') and self.canvas_manager:
                # Force canvas to update its geometry
                self.canvas_manager.canvas.update_idletasks()
                
                # Get current frame dimensions
                parent_frame = self.canvas_manager.canvas.master
                frame_width = parent_frame.winfo_width()
                frame_height = parent_frame.winfo_height()
                
                # Recalculate table dimensions
                table_width = max(800, frame_width - 20)
                table_height = max(600, frame_height - 20)
                
                # Update canvas size
                self.canvas_manager.canvas.configure(width=table_width, height=table_height)
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update display state
                if hasattr(self, 'display_state'):
                    self.display_state['table']['width'] = table_width
                    self.display_state['table']['height'] = table_height
                
                # Re-render with new dimensions
                self._render_poker_table()
                
                print(f"🔄 HandsReviewTab: Widget refreshed to {table_width}x{table_height}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Widget refresh error: {e}")
