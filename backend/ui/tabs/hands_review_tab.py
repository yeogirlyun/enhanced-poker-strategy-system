import tkinter as tk
from tkinter import ttk
import uuid
from typing import Dict, Any, Optional

# New UI Architecture imports
from ..state.actions import (
    SET_TABLE_DIM,
    SET_POT,
    SET_SEATS,
    SET_BOARD,
    SET_DEALER,
    SET_REVIEW_HANDS,
    SET_REVIEW_FILTER,
    SET_LOADED_HAND,
    SET_STUDY_MODE
)
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer
from ..services.hands_repository import HandsRepository, HandsFilter, StudyMode

# Legacy imports removed - now using config-driven theme system
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

# Core imports - fail fast if not available
USE_DEV_STUBS = False  # set True only in a test harness

try:
    from core.hand_model import Hand
    from core.hand_model_decision_engine import HandModelDecisionEngine
    from core.bot_session_state_machine import HandsReviewBotSession
    from core.flexible_poker_state_machine import GameConfig
    from core.session_logger import get_session_logger
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


class ConcreteHandModelDecisionEngine:
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
        # Two-column layout: Controls (20%) | Poker Table (80%)
        # Using 1:4 ratio for poker table emphasis
        self.grid_columnconfigure(0, weight=1)  # Library + Filters & Controls (20%)
        self.grid_columnconfigure(1, weight=4)  # Poker Table (80%)
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
        self.collection_var = tk.StringVar(value="All Hands")
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
            command=self._next_action,
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        self.auto_btn = SecondaryButton(
            controls_frame,
            text="Auto",
            command=self._toggle_auto,
            theme_manager=self.theme,
        )
        self.auto_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = SecondaryButton(
            controls_frame,
            text="Reset",
            command=self._reset_hand,
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
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass

        # Set up table rendering pipeline with themed canvas
        self.canvas_manager = CanvasManager(table_frame)

        # Apply table felt color to canvas
        try:
            self.canvas_manager.canvas.configure(
                bg=theme.get("table.felt", "#1E5B44"), highlightthickness=0
            )
        except Exception:
            pass
        self.layer_manager = LayerManager(
            self.canvas_manager.canvas, self.canvas_manager.overlay
        )

        # Create table components that read from the store
        self.table_components = [
            TableFelt(),  # Background
            Seats(),  # Player seats with cards, stacks, names
            Community(),  # Community cards
            BetDisplay(),  # Current bet amounts
            PotDisplay(),  # Pot amount display
            DealerButton(),  # Dealer button
            ActionIndicator(),  # Highlight acting player
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
                    self.store.dispatch({"type": SET_TABLE_DIM, "dim": (w, h)})

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
            self._handle_load_hand_event,
        )

    def _refresh_hands_list(self):
        """Refresh the hands list based on current filters."""
        filtered_hands = self.hands_repository.get_filtered_hands()

        # Dispatch to store
        self.store.dispatch({"type": SET_REVIEW_HANDS, "hands": filtered_hands})

        # Update UI
        self.hands_listbox.delete(0, tk.END)
        for hand in filtered_hands:
            hand_id = hand.get("hand_id", "Unknown")
            players_count = len(hand.get("players", []))
            pot_size = hand.get("pot_size", 0)
            display_text = f"{hand_id} | {players_count}p | ${pot_size}"
            self.hands_listbox.insert(tk.END, display_text)

        # Update collections
        collections = ["All Hands"] + list(
            self.hands_repository.get_collections().keys()
        )
        self.collection_combo["values"] = collections

        # Update status with workflow guidance
        stats = self.hands_repository.get_stats()
        self._update_status(
            f"📊 Library: {stats['total_hands']} total, {stats['filtered_hands']} filtered"
        )
        self._update_status(
            "👆 SELECT a hand from the list, then click 'LOAD HAND' to begin study"
        )

    def _on_theme_change(self):
        """Handle poker table theme change."""
        theme_name = self.theme_var.get()
        print(f"🎨 Switching to theme: {theme_name}")

        # Switch theme in the theme manager
        self.theme.set_profile(theme_name)

        # Update status to show theme change
        self._update_status(
            f"🎨 Switched to {theme_name} theme - New poker table colors applied!"
        )

        # Force UI refresh with new theme
        self._refresh_ui_colors()

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
        """Refresh all UI elements with new theme colors."""
        theme = self.theme.get_theme()

        # Update all themed elements
        try:
            # Update listbox colors with dynamic theme-specific selection highlight
            if hasattr(self, "hands_listbox"):
                # Get current theme name for dynamic highlighting
                current_theme_name = (
                    self.theme.current() or "Forest Green Professional 🌿"
                )
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
                ),  # Bold white text when highlighted
            )

            # Update theme radio buttons with theme-specific highlight colors
            self._style_theme_radio_buttons()

            # Update text areas
            for text_widget in [
                getattr(self, "details_text", None),
                getattr(self, "status_text", None),
            ]:
                if text_widget:
                    text_widget.configure(
                        bg=theme.get("panel.bg", "#111827"),
                        fg=theme.get("panel.fg", "#E5E7EB"),
                    )

            # Update load button
            if hasattr(self, "load_btn"):
                self.load_btn.configure(
                    bg=theme.get("btn.primaryBg", "#16A34A"),
                    fg=theme.get("btn.primaryFg", "#F8FAFC"),
                )

            # Update control buttons
            control_buttons = [
                getattr(self, btn, None)
                for btn in ["next_btn", "auto_btn", "reset_btn"]
            ]
            for btn in control_buttons:
                if btn:
                    btn.configure(
                        bg=theme.get("btn.secondaryBg", "#334155"),
                        fg=theme.get("btn.secondaryFg", "#E2E8F0"),
                    )

            # Update poker table canvas and force full re-render
            if hasattr(self, "canvas_manager") and self.canvas_manager.canvas:
                # Update canvas background
                self.canvas_manager.canvas.configure(
                    bg=theme.get("table.felt", "#1E5B44")
                )

                # Force poker table components to re-render with new theme
                if hasattr(self, "renderer_pipeline"):
                    try:
                        state = self.store.get_state()
                        self.renderer_pipeline.render_once(state)
                        print(
                            f"🎨 Poker table re-rendered with {self.theme_var.get()} theme colors"
                        )
                    except Exception as e:
                        print(f"⚠️  Error re-rendering poker table: {e}")

            # Update enhanced buttons to refresh their theme
            for btn_name in ["load_btn", "next_btn", "auto_btn", "reset_btn"]:
                if hasattr(self, btn_name):
                    btn = getattr(self, btn_name)
                    if hasattr(btn, "refresh_theme"):
                        btn.refresh_theme()

            # Update artistic theme intro panel colors
            if hasattr(self, "theme_intro_label"):
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
                hand_id = hand.get("hand_id", "Unknown")
                self._update_status(
                    f"✅ Selected: {hand_id} - Click 'LOAD HAND' to start study"
                )

    def _update_hand_details(self, hand_data: Dict[str, Any]):
        """Update the hand details display."""
        self.details_text.delete(1.0, tk.END)

        details = [
            f"Hand ID: {hand_data.get('hand_id', 'Unknown')}",
            f"Players: {len(hand_data.get('players', []))}",
            f"Stakes: ${hand_data.get('small_blind', 5)}/${hand_data.get('big_blind', 10)}",
            f"Pot: ${hand_data.get('pot_size', 0)}",
            "",
            "Players:",
        ]

        for i, player in enumerate(hand_data.get("players", [])):
            name = player.get("name", f"seat{i + 1}")
            stack = player.get("stack", 0)
            position = player.get("position", "Unknown")
            details.append(f"  {name} ({position}): ${stack}")

        community = hand_data.get("community_cards", [])
        if community:
            details.extend(["", f"Community: {', '.join(community)}"])

        self.details_text.insert(1.0, "\n".join(details))

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
            self.event_bus.topic(self.session_id, "review:load"), hand_data
        )

    def _handle_load_hand_event(self, hand_data):
        """Handle the review:load event."""
        try:
            hand_id = hand_data.get("hand_id", "Unknown")
            self._update_status(f"🔄 Loading hand {hand_id}...")

            # Session logging for debugging
            if hasattr(self, "session_logger") and self.session_logger:
                self.session_logger.log_system(
                    "INFO",
                    "HAND_LOADING",
                    f"Starting to load hand {hand_id}",
                    {
                        "hand_data_keys": list(hand_data.keys()),
                        "hand_data_size": len(str(hand_data)),
                    },
                )

            # Store hand data for reset functionality
            self.last_loaded_hand = hand_data

            # Convert to Hand object (following validation tester pattern)
            if (
                isinstance(hand_data, dict)
                and "metadata" in hand_data
                and "hand_id" in hand_data["metadata"]
            ):
                hand = Hand.from_dict(hand_data)
            else:
                self._update_status("❌ Invalid hand data format")
                return

            # Create decision engine
            decision_engine = ConcreteHandModelDecisionEngine(hand)

            # Create game config from hand metadata
            # Handle both 'players' and 'seats' data structures
            seats_data = hand_data.get("seats", [])
            players_data = hand_data.get(
                "players", seats_data
            )  # Fallback to seats if no players

            # Extract metadata from hand structure
            metadata = hand_data.get("metadata", {})
            small_blind = metadata.get("small_blind") or hand_data.get("small_blind", 5)
            big_blind = metadata.get("big_blind") or hand_data.get("big_blind", 10)

            # Get starting stack from seats data
            if seats_data:
                starting_stack = max(
                    [seat.get("starting_stack", 1000) for seat in seats_data],
                    default=1000,
                )
                num_players = len(seats_data)
            elif players_data:
                starting_stack = max(
                    [p.get("stack", 1000) for p in players_data], default=1000
                )
                num_players = len(players_data)
            else:
                # Fallback to metadata if available
                num_players = metadata.get("max_players", 2)
                starting_stack = 1000

            config = GameConfig(
                num_players=num_players,
                small_blind=small_blind,
                big_blind=big_blind,
                starting_stack=starting_stack,
            )

            # Create hands review session
            self.current_session = HandsReviewBotSession(
                config, session_logger=None, decision_engine=decision_engine
            )

            # Set preloaded hand data
            self.current_session.set_preloaded_hand_data({"hand_model": hand})

            # Connect FPSM adapter to get poker state updates
            if not self.fpsm_adapter:
                self.fpsm_adapter = FpsmEventAdapter(self.store)
            self.fpsm_adapter.attach(self.current_session)

            # Start the session
            success = self.current_session.start_session()

            # CRITICAL: Load the hand for review (posts blinds, sets up game state)
            if success:
                print(
                    "🎯 LOAD_HAND: Loading hand for review with proper initialization..."
                )

                # Convert seats data to players format expected by load_hand_for_review
                converted_hand_data = hand_data.copy()
                if "seats" in hand_data and "players" not in hand_data:
                    players_data = []
                    for seat in hand_data["seats"]:
                        player_data = {
                            "seat": seat.get("seat_no", 1),
                            "name": seat.get(
                                "display_name", f"Player{seat.get('seat_no', 1)}"
                            ),
                            "starting_stack": seat.get("starting_stack", 1000),
                            "stack": seat.get("starting_stack", 1000),
                            "hole_cards": [],  # Will be populated from metadata if available
                            "cards": [],
                        }

                        # Get hole cards from metadata if available
                        metadata = hand_data.get("metadata", {})
                        hole_cards = metadata.get("hole_cards", {})
                        seat_key = f"seat{seat.get('seat_no', 1)}"
                        if seat_key in hole_cards:
                            player_data["hole_cards"] = hole_cards[seat_key]
                            player_data["cards"] = hole_cards[seat_key]

                        players_data.append(player_data)

                    converted_hand_data["players"] = players_data

                # Also ensure table/button information is available
                if "table" not in converted_hand_data:
                    metadata = hand_data.get("metadata", {})
                    converted_hand_data["table"] = {
                        "button_seat": metadata.get("button_seat_no", 1)
                    }
                
                # Copy metadata to converted hand data so blind amounts are available
                if "metadata" in hand_data:
                    converted_hand_data["metadata"] = hand_data["metadata"]
                    print(f"🎯 LOAD_HAND: Copied metadata with blinds: SB=${hand_data['metadata'].get('small_blind', 'N/A')}, BB=${hand_data['metadata'].get('big_blind', 'N/A')}")
                
                # Convert actions from legendary hands format to expected format
                if "streets" in hand_data:
                    print("🎯 LOAD_HAND: Converting legendary hands actions format...")
                    actions_converted = {}
                    
                    # Map legendary hands street names to expected names
                    street_mapping = {
                        "PREFLOP": "preflop",
                        "FLOP": "flop", 
                        "TURN": "turn",
                        "RIVER": "river"
                    }
                    
                    for legendary_street, street_data in hand_data["streets"].items():
                        if legendary_street in street_mapping:
                            expected_street = street_mapping[legendary_street]
                            if "actions" in street_data:
                                # Convert action format
                                converted_actions = []
                                for action in street_data["actions"]:
                                    converted_action = {
                                        "action_type": action.get("action", "check").lower(),
                                        "amount": action.get("amount", 0.0),
                                        "player_seat": action.get("actor_uid", "seat1"),
                                        "street": expected_street
                                    }
                                    converted_actions.append(converted_action)
                                
                                actions_converted[expected_street] = converted_actions
                                print(f"   • {legendary_street} -> {expected_street}: {len(converted_actions)} actions")
                    
                    converted_hand_data["actions"] = actions_converted
                    print(f"🎯 LOAD_HAND: Converted {len(actions_converted)} streets with actions")
                else:
                    print("🎯 LOAD_HAND: No streets data found, using original actions if available")

                load_success = self.current_session.load_hand_for_review(
                    converted_hand_data
                )
                if not load_success:
                    print("❌ LOAD_HAND: Failed to load hand for review")
                    success = False
                else:
                    print(
                        "✅ LOAD_HAND: Hand loaded successfully with blinds and game state"
                    )
            if success:
                self.session_active = True

                # Update store with loaded hand and initial poker state
                self.store.dispatch({"type": SET_LOADED_HAND, "hand": hand_data})

                # Initialize poker table display state
                # Note: Hand data uses 'seats' not 'players'
                players_data = hand_data.get("seats", hand_data.get("players", []))
                seats_data = []

                # Session logging for players data debugging
                if hasattr(self, "session_logger") and self.session_logger:
                    self.session_logger.log_system(
                        "DEBUG",
                        "PLAYERS_DATA",
                        f"Players data extracted from hand",
                        {
                            "players_count": len(players_data),
                            "players_data": players_data,
                            "hand_data_players_key_exists": "players" in hand_data,
                            "all_hand_keys": list(hand_data.keys()),
                        },
                    )

                # Get hole cards from hand metadata
                hole_cards_data = {}
                if "metadata" in hand_data and "hole_cards" in hand_data["metadata"]:
                    hole_cards_data = hand_data["metadata"]["hole_cards"]
                    print(f"🃏 Found hole cards in metadata: {hole_cards_data}")
                    if hasattr(self, "session_logger") and self.session_logger:
                        self.session_logger.log_system(
                            "DEBUG",
                            "HOLE_CARDS",
                            f"Hole cards found in metadata",
                            {"hole_cards_data": hole_cards_data},
                        )
                else:
                    print(
                        f"🃏 No hole cards found in hand metadata. Keys: {list(hand_data.get('metadata', {}).keys())}"
                    )
                    if hasattr(self, "session_logger") and self.session_logger:
                        self.session_logger.log_system(
                            "WARNING",
                            "HOLE_CARDS",
                            f"No hole cards found in hand metadata",
                            {
                                "metadata_keys": list(
                                    hand_data.get("metadata", {}).keys()
                                )
                            },
                        )

                print(f"🃏 Players data: {players_data}")
                for i, p in enumerate(players_data):
                    # Get player UID for hole cards lookup - use the actual player_uid from seat data
                    player_uid = p.get("player_uid", f"seat{i + 1}")

                    # Try different UID formats for hole cards lookup
                    player_hole_cards = []
                    for uid_candidate in [
                        player_uid,
                        f"seat{i + 1}",
                        f"player_{i}",
                        p.get("display_name", ""),
                    ]:
                        if uid_candidate in hole_cards_data:
                            player_hole_cards = hole_cards_data[uid_candidate]
                            break

                    print(
                        f"🃏 Player {p.get('display_name', f'seat{i + 1}')} (UID: {player_uid}) cards: {player_hole_cards}"
                    )
                    print(
                        f"🃏 Available hole card UIDs: {list(hole_cards_data.keys())}"
                    )

                    # Session logging for each player
                    if hasattr(self, "session_logger") and self.session_logger:
                        self.session_logger.log_system(
                            "DEBUG",
                            "PLAYER_MAPPING",
                            f"Processing player {i}",
                            {
                                "player_data": p,
                                "player_uid": player_uid,
                                "hole_cards_found": len(player_hole_cards) > 0,
                                "hole_cards": player_hole_cards,
                            },
                        )

                    seat_data = {
                        "name": p.get("display_name", f"seat{i + 1}"),
                        "stack": p.get(
                            "starting_stack", 1000
                        ),  # Use starting_stack from hand data
                        "cards": player_hole_cards,  # Use hole cards from metadata
                        "position": p.get("position", ""),
                        "current_bet": 0,  # Will be updated by FPSM
                        "folded": False,  # Will be updated by FPSM
                        "all_in": False,  # Will be updated by FPSM
                        "acting": False,  # Will be set by FPSM updates
                        "active": True,  # Start as active
                    }
                    seats_data.append(seat_data)

                print(f"🃏 Final seats_data being dispatched: {seats_data}")
                self.store.dispatch({"type": SET_SEATS, "seats": seats_data})

                self.store.dispatch(
                    {"type": SET_POT, "amount": hand_data.get("pot_size", 0)}
                )

                # Initialize community cards (board)
                community_cards = hand_data.get("community_cards", [])
                if not community_cards and "board" in hand_data:
                    community_cards = hand_data["board"]
                print(f"🃏 Community cards: {community_cards}")

                self.store.dispatch({"type": SET_BOARD, "board": community_cards})

                self.store.dispatch(
                    {"type": SET_DEALER, "dealer": hand_data.get("dealer", 0)}
                )

                self._update_status(
                    f"✅ Hand {hand.metadata.hand_id} loaded! Hole cards visible. Click 'Next →' to advance."
                )

                # Force a table render
                self.after_idle(
                    lambda: self.renderer_pipeline.render_once(self.store.get_state())
                )
            else:
                self._update_status(f"❌ Failed to start hand session")

        except Exception as e:
            self._update_status(f"❌ Error loading hand: {e}")
            import traceback

            traceback.print_exc()

    # Removed duplicate method - using the more complete implementation below

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

    def _on_theme_change(self):
        """Handle theme change from radio buttons."""
        try:
            selected_theme = self.theme_var.get()
            if selected_theme:
                print(f"🎨 Theme changed to: {selected_theme}")

                # Set the theme using the theme manager
                self.theme.set_profile(selected_theme)

                # Update all UI colors including radio button styling
                self._refresh_ui_colors()

                # Update the theme introduction display
                self._show_theme_intro(selected_theme)

                # Force a table render with new theme
                if hasattr(self, "renderer_pipeline") and self.renderer_pipeline:
                    self.after_idle(
                        lambda: self.renderer_pipeline.render_once(
                            self.store.get_state()
                        )
                    )

        except Exception as e:
            print(f"⚠️ Theme change error: {e}")

    def _next_action(self):
        """Advance to the next action in the hand."""
        print("🎯 NEXT_ACTION: Button clicked!")

        # Debug session state
        print(f"🎯 NEXT_ACTION: session_active={self.session_active}")
        print(f"🎯 NEXT_ACTION: current_session={self.current_session}")

        if not self.session_active or not self.current_session:
            self._update_status(
                "⚠️ No hand loaded. Please select and load a hand first."
            )
            return

        try:
            # Debug session state
            print(f"🎯 NEXT_ACTION: Session type: {type(self.current_session)}")
            print(
                f"🎯 NEXT_ACTION: Session active: {getattr(self.current_session, 'session_active', 'N/A')}"
            )

            # Check if session is complete first
            if (
                hasattr(self.current_session, "decision_engine")
                and self.current_session.decision_engine.is_session_complete()
            ):
                self._update_status("🏁 Hand complete - no more actions")
                return

            # Execute next action through the session (using the correct method for hands review)
            print("🎯 NEXT_ACTION: Calling step_forward...")
            result = self.current_session.step_forward()
            print(f"🎯 NEXT_ACTION: Result: {result}")

            if result:
                # Get explanation if available
                explanation = getattr(
                    self.current_session,
                    "current_decision_explanation",
                    "Action executed",
                )
                self._update_status(f"▶️ {explanation}")

                # The FPSM adapter should automatically update the poker table display
                # Force a render to ensure UI is updated
                print("🎯 NEXT_ACTION: Forcing UI update...")
                self.after_idle(
                    lambda: self.renderer_pipeline.render_once(self.store.get_state())
                )
            else:
                self._update_status("🏁 Hand complete - no more actions")
        except Exception as e:
            self._update_status(f"❌ Error advancing hand: {e}")
            print(f"🎯 NEXT_ACTION: Exception: {e}")
            import traceback

            traceback.print_exc()

    def _toggle_auto(self):
        """Toggle auto-play mode."""
        if not self.session_active or not self.current_session:
            self._update_status(
                "⚠️ No hand loaded. Please select and load a hand first."
            )
            return

        try:
            # Simple auto-play implementation - repeatedly call next action
            if not hasattr(self, "auto_play_active"):
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
        if (
            not self.auto_play_active
            or not self.session_active
            or not self.current_session
        ):
            return

        try:
            # Check if session is complete
            if self.current_session.decision_engine.is_session_complete():
                self.auto_play_active = False
                self.auto_btn.configure(text="Auto")
                self._update_status("🏁 Hand complete - auto-play stopped")
                return

            # Execute next action
            result = self.current_session.step_forward()
            if result:
                # Force a render
                self.after_idle(
                    lambda: self.renderer_pipeline.render_once(self.store.get_state())
                )
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
            self._update_status(
                "⚠️ No hand loaded. Please select and load a hand first."
            )
            return

        try:
            # Reset the session
            if hasattr(self.current_session, "reset_session"):
                self.current_session.reset_session()
                self._update_status("🔄 Hand reset to beginning")

                # Force a render to show initial state
                self.after_idle(
                    lambda: self.renderer_pipeline.render_once(self.store.get_state())
                )
            else:
                # Fallback - reload the current hand
                self._update_status("🔄 Reloading hand...")
                if hasattr(self, "last_loaded_hand"):
                    self._handle_load_hand_event(self.last_loaded_hand)
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
        if self.fpsm_adapter:
            self.fpsm_adapter.detach()
        self.services.dispose_session(self.session_id)
