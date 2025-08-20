import tkinter as tk
from tkinter import ttk
import uuid

from .services.event_bus import EventBus
from .services.service_container import ServiceContainer
from .services.timer_manager import TimerManager
from .services.theme_manager import ThemeManager
from .services.hands_repository import HandsRepository, StudyMode
from .state.store import Store
from .state.reducers import root_reducer
from .mvu.hands_review_integrated import MVUHandsReviewTabIntegrated
from .tabs.practice_session_tab import PracticeSessionTab
from .tabs.gto_session_tab import GTOSessionTab

from .menu_integration import add_theme_manager_to_menu


class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # Store root reference for menu integration
        self.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # app-scoped services
        self.services = ServiceContainer()
        self.services.provide_app("event_bus", EventBus())
        self.services.provide_app("theme", ThemeManager())
        self.services.provide_app("hands_repository", HandsRepository())
        
        # Create global GameDirector for action sequencing
        from .services.game_director import GameDirector
        game_director = GameDirector(event_bus=self.services.get_app("event_bus"))
        self.services.provide_app("game_director", game_director)
        
        # Create global EffectBus service for sound management
        from .services.effect_bus import EffectBus
        effect_bus = EffectBus(
            game_director=game_director,
            event_bus=self.services.get_app("event_bus")
        )
        self.services.provide_app("effect_bus", effect_bus)
        
        # Create architecture compliant hands review controller
        from .services.hands_review_event_controller import HandsReviewEventController
        
        # Initialize Store with initial state and reducer
        initial_state = {
            "table": {"dim": {"width": 800, "height": 600}},
            "seats": [],
            "board": [],
            "pot": {"amount": 0},
            "dealer": {},
            "review": {},
            "enhanced_rpgw": {},
            "event_bus": self.services.get_app("event_bus")
        }
        store = Store(initial_state, root_reducer)
        self.services.provide_app("store", store)
        
        hands_review_controller = HandsReviewEventController(
            event_bus=self.services.get_app("event_bus"),
            store=store,
            services=self.services
        )
        self.services.provide_app("hands_review_controller", hands_review_controller)
        
        # Subscribe to voice events to keep architecture event-driven
        def _on_voice(payload):
            try:
                action = (payload or {}).get("action")
                vm = getattr(effect_bus, "voice_manager", None)
                if not (vm and action):
                    return
                cfg = getattr(effect_bus, "config", {}) or {}
                voice_type = getattr(effect_bus, "voice_type", "")
                table = (cfg.get("voice_sounds", {}) or {}).get(voice_type, {})
                rel = table.get(action)
                if rel:
                    vm.play(rel)
            except Exception:
                pass
        self.services.get_app("event_bus").subscribe("effect_bus:voice", _on_voice)
        
        # Create shared store for poker game state (per architecture doc)
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": StudyMode.REPLAY.value,
                "collection": None
            }
        }
        self.services.provide_app("store", Store(initial_state, root_reducer))

        # Create menu system
        self._create_menu_system()
        
        # tabs (order: Practice, GTO, Hands Review - main product features only)
        self._add_tab("Practice Session", PracticeSessionTab)
        self._add_tab("GTO Session", GTOSessionTab)
        self._add_tab("Hands Review (MVU)", MVUHandsReviewTabIntegrated)
        # Bind global font size shortcuts (Cmd/Ctrl - and =)
        self._bind_font_shortcuts(root)

    def _add_tab(self, title: str, TabClass):
        session_id = str(uuid.uuid4())
        timers = TimerManager(self)
        self.services.provide_session(session_id, "timers", timers)

        # Update active tab in shared store
        store = self.services.get_app("store")
        store.dispatch({"type": "SET_ACTIVE_TAB", "name": title})
        
        # Create tab with services
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)
        
        # Call on_show if available
        if hasattr(tab, "on_show"):
            tab.on_show()

    def _create_menu_system(self):
        """Create the application menu system."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._increase_font(None))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._decrease_font(None))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=lambda: self._reset_font(None))
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme management
        settings_menu.add_command(label="Theme Editor", command=self._open_theme_editor)
        settings_menu.add_command(label="Sound Settings", command=self._open_sound_settings)
        settings_menu.add_separator()
        
        # Add Theme Manager to Settings menu using our integration helper
        add_theme_manager_to_menu(settings_menu, self.root, self._on_theme_changed)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _new_session(self):
        """Start a new session."""
        print("🔄 New session requested")
        # TODO: Implement session reset
        
    def _on_theme_changed(self):
        """Called when theme is changed via Theme Manager."""
        print("🎨 Theme changed - refreshing UI...")
        
        try:
            # Reload theme manager to get latest changes
            theme_manager = self.services.get_app("theme")
            if hasattr(theme_manager, 'reload'):
                theme_manager.reload()
            
            # Force rebuild themes to pick up any live changes
            try:
                from .services.theme_factory import build_all_themes
                themes = build_all_themes()
                # Register updated themes
                for name, tokens in themes.items():
                    theme_manager.register(name, tokens)
                print(f"🔄 Rebuilt and registered {len(themes)} themes")
            except Exception as e:
                print(f"⚠️ Theme rebuild warning: {e}")
            
            # Refresh all tabs with new theme
            for i in range(self.notebook.index("end")):
                try:
                    tab = self.notebook.nametowidget(self.notebook.tabs()[i])
                    
                    # Try multiple refresh methods
                    if hasattr(tab, '_refresh_ui_colors'):
                        tab._refresh_ui_colors()
                        print(f"✅ Refreshed tab {i} via _refresh_ui_colors")
                    elif hasattr(tab, 'refresh_theme'):
                        tab.refresh_theme()
                        print(f"✅ Refreshed tab {i} via refresh_theme")
                    elif hasattr(tab, '_on_theme_changed'):
                        tab._on_theme_changed()
                        print(f"✅ Refreshed tab {i} via _on_theme_changed")
                    else:
                        print(f"ℹ️ Tab {i} has no theme refresh method")
                        
                except Exception as e:
                    print(f"⚠️ Error refreshing tab {i}: {e}")
            
            print("✅ Live theme refresh completed")
            
        except Exception as e:
            print(f"❌ Theme refresh error: {e}")
            import traceback
            traceback.print_exc()
        
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Poker Pro Trainer",
            "Poker Pro Trainer\n\n"
            "Advanced poker training with luxury themes\n"
            "and professional game analysis.\n\n"
            "🎨 Theme Manager integrated\n"
            "🃏 16 luxury themes available\n"
            "📊 Comprehensive hand review\n"
            "🤖 AI-powered training"
        )

    def _bind_font_shortcuts(self, root):
        # macOS Command key bindings (Cmd - decreases, Cmd = increases)
        root.bind_all("<Command-minus>", self._decrease_font)
        root.bind_all("<Command-equal>", self._increase_font)  # This is Cmd = (increase)
        root.bind_all("<Command-0>", self._reset_font)
        
        # Additional symbols that might work
        root.bind_all("<Command-plus>", self._increase_font)   # Shift+= gives +
        
        # Numpad variants
        root.bind_all("<Command-KP_Subtract>", self._decrease_font)
        root.bind_all("<Command-KP_Add>", self._increase_font)
        
        # Windows/Linux Control variants  
        root.bind_all("<Control-minus>", self._decrease_font)
        root.bind_all("<Control-equal>", self._increase_font)
        root.bind_all("<Control-plus>", self._increase_font)
        root.bind_all("<Control-0>", self._reset_font)
        
        print("🔧 Font shortcuts bound successfully")

    def _set_global_font_scale(self, delta: int | None):
        print(f"🔧 Font scale called with delta: {delta}")
        theme: ThemeManager = self.services.get_app("theme")
        fonts = dict(theme.get_fonts())
        base = list(fonts.get("main", ("Arial", 20, "normal")))
        print(f"🔧 Current base font: {base}")
        
        if delta is None:
            new_base_size = 20  # Default 20px size for readability
        else:
            new_base_size = max(10, min(40, int(base[1]) + delta))
        
        print(f"🔧 New base size: {new_base_size}")
        
        # Scale all fonts proportionally from 20px base
        fonts["main"] = (base[0], new_base_size, base[2] if len(base) > 2 else "normal")
        fonts["pot_display"] = (base[0], new_base_size + 8, "bold")  # +8 for pot display
        fonts["bet_amount"] = (base[0], new_base_size + 4, "bold")   # +4 for bet amounts
        fonts["body"] = ("Consolas", max(new_base_size, 12))         # Same as main for body text
        fonts["small"] = ("Consolas", max(new_base_size - 4, 10))    # -4 for smaller text
        fonts["header"] = (base[0], max(new_base_size + 2, 14), "bold") # +2 for headers
        
        print(f"🔧 Updated fonts: {fonts}")
        theme.set_fonts(fonts)
        
        # Force all tabs to re-render with new fonts
        for idx in range(self.notebook.index("end")):
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[idx])
            if hasattr(tab_widget, "on_show"):
                tab_widget.on_show()
            # Also force font refresh if the widget has that method
            if hasattr(tab_widget, "_refresh_fonts"):
                tab_widget._refresh_fonts()
        print("🔧 Font scaling complete")

    def _increase_font(self, event=None):
        print("🔧 Increase font called!")
        self._set_global_font_scale(+1)

    def _decrease_font(self, event=None):
        print("🔧 Decrease font called!")
        self._set_global_font_scale(-1)

    def _reset_font(self, event=None):
        print("🔧 Reset font called!")
        self._set_global_font_scale(None)

    def _open_theme_editor(self):
        """Open the Theme Editor in a new window."""
        try:
            from .tabs.theme_editor_tab import ThemeEditorTab
            # Create a new toplevel window for the theme editor
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Theme Editor - Poker Pro Trainer")
            theme_window.geometry("900x700")
            theme_window.resizable(True, True)
            
            # Center the window on screen
            theme_window.update_idletasks()
            x = (theme_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (theme_window.winfo_screenheight() // 2) - (700 // 2)
            theme_window.geometry(f"900x700+{x}+{y}")
            
            # Create the theme editor tab in the new window
            theme_editor = ThemeEditorTab(theme_window, self.services)
            theme_editor.pack(fill=tk.BOTH, expand=True)
            
            print("🎨 Theme Editor opened in new window")
        except Exception as e:
            print(f"❌ Error opening Theme Editor: {e}")
            import traceback
            traceback.print_exc()

    def _open_sound_settings(self):
        """Open the Sound Settings in a new window."""
        try:
            from .tabs.sound_settings_tab import SoundSettingsTab
            # Create a new toplevel window for the sound settings
            sound_window = tk.Toplevel(self.root)
            sound_window.title("Sound Settings - Poker Pro Trainer")
            sound_window.geometry("1200x800")
            sound_window.resizable(True, True)
            
            # Center the window on screen
            sound_window.update_idletasks()
            x = (sound_window.winfo_screenwidth() // 2) - (1200 // 2)
            y = (sound_window.winfo_screenheight() // 2) - (800 // 2)
            sound_window.geometry(f"1200x800+{x}+{y}")
            
            # Create the sound settings tab in the new window
            sound_settings = SoundSettingsTab(sound_window, self.services)
            sound_settings.pack(fill=tk.BOTH, expand=True)
            
            print("🔊 Sound Settings opened in new window")
        except Exception as e:
            print(f"❌ Error opening Sound Settings: {e}")
            import traceback
            traceback.print_exc()


