from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes
    from .theme_loader import get_theme_loader
    from .state_styler import (
        get_state_styler,
        get_selection_styler,
        get_emphasis_bar_styler
    )
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Default theme name for fallbacks
DEFAULT_THEME_NAME = "Forest Green Professional 🌿"  # Updated to match JSON


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
    - Now fully config-driven using poker_themes.json
    """

    CONFIG_PATH = os.path.join("backend", "ui", "theme_config.json")

    def __init__(self) -> None:
        self._theme: Dict[str, Any]
        self._fonts: Dict[str, Any]
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._current: str | None = None
        self._subs: List[Callable[["ThemeManager"], None]] = []
        # Load defaults from codebase
        try:
            gm = importlib.import_module("backend.core.gui_models")
            self._theme = dict(getattr(gm, "THEME", {}))
            self._fonts = dict(getattr(gm, "FONTS", {}))
        except Exception:
            self._theme = {"table_felt": "#2B2F36", "text": "#E6E9EF"}
            self._fonts = {
                "main": ("Arial", 20),  # Base font at 20px for readability
                "pot_display": ("Arial", 28, "bold"),  # +8 for pot display
                "bet_amount": ("Arial", 24, "bold"),  # +4 for bet amounts
                "body": ("Consolas", 20),  # Same as main for body text
                "small": ("Consolas", 16),  # -4 for smaller text
                "header": ("Arial", 22, "bold")  # +2 for headers
            }
        # Apply persisted config if present
        # Register built-in packs
        packs = self._builtin_packs()
        for name, tokens in packs.items():
            self.register(name, tokens)
        self._load_config()
        if not self._current:
            # Use Forest Green Professional as safe default
            if DEFAULT_THEME_NAME in self._themes:
                self._current = DEFAULT_THEME_NAME
                self._theme = dict(self._themes[DEFAULT_THEME_NAME])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in theme packs - now using token-driven system"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Use the new deterministic token system
                themes = build_all_themes()
                print(f"🎨 ThemeManager: Loaded {len(themes)} themes: {list(themes.keys())}")
                return themes
            except Exception as e:
                print(f"⚠️ ThemeManager: Config-driven themes failed: {e}")
                return self._legacy_builtin_packs()
        else:
            print("⚠️ ThemeManager: Token-driven themes not available, using legacy")
            # Fallback to legacy themes if token system not available
            return self._legacy_builtin_packs()
    
    def _legacy_builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Minimal legacy fallback if config system completely fails."""
        return {
            "Forest Green Professional 🌿": {
                "table.felt": "#2D5A3D",
                "table.rail": "#4A3428", 
                "text.primary": "#EDECEC",
                "panel.bg": "#1F2937",
                "panel.fg": "#E5E7EB"
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()
    
    def get_dimensions(self) -> Dict[str, Any]:
        """Get theme dimensions for consistent spacing and sizing."""
        try:
            # Try to get dimensions from theme config
            theme_data = self.get_theme()
            if theme_data and "dimensions" in theme_data:
                return theme_data["dimensions"]
            
            # Fallback to default dimensions
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }
        except Exception:
            # Ultimate fallback
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names from config-driven system."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback: return all registered theme names
        return list(self._themes.keys())

    def register_all(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register all themes from packs dictionary."""
        for name, tokens in packs.items():
            self.register(name, tokens)

    def current(self) -> str | None:
        """Return current theme name."""
        return self._current

    def set_profile(self, name: str) -> None:
        if name in self._themes:
            self._current = name
            self._theme = dict(self._themes[name])
            self._save_config()
            for fn in list(self._subs):
                fn(self)

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile")
                if prof and prof in self._themes:
                    self._current = prof
                    self._theme = dict(self._themes[prof])
                fonts = data.get("fonts")
                if isinstance(fonts, dict):
                    self._fonts.update(fonts)
        except Exception:
            pass

    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            payload = {"profile": self.current_profile_name(), "fonts": self._fonts}
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def current_profile_name(self) -> str:
        for name, theme in self._themes.items():
            if all(self._theme.get(k) == theme.get(k) for k in ("table.felt",)):
                return name
        return "Custom"

    def get(self, token: str, default=None):
        # Dot-path lookup in current theme; fallback to fonts when font.* requested
        if token.startswith("font."):
            return self._theme.get(token) or self._fonts.get(token[5:], default)
        cur = self._theme
        for part in token.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return self._theme.get(token, default)
        return cur
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get complete token dictionary for current theme"""
        return dict(self._theme)
    
    def get_base_colors(self) -> Dict[str, str]:
        """Get the base color palette for current theme (if available)"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try new config-driven system first
            try:
                loader = get_theme_loader()
                # Convert display name to theme ID using proper mapping
                name_to_id_map = {
                    "Forest Green Professional 🌿": "forest-green-pro",
                    "Velvet Burgundy 🍷": "velvet-burgundy", 
                    "Emerald Aurora 🌌": "emerald-aurora",
                    "Imperial Jade 💎": "imperial-jade",
                    "Ruby Royale ❤️‍🔥": "ruby-royale",
                    "Coral Royale 🪸": "coral-royale",
                    "Golden Dusk 🌇": "golden-dusk",
                    "Klimt Royale ✨": "klimt-royale",
                    "Deco Luxe 🏛️": "deco-luxe",
                    "Oceanic Aqua 🌊": "oceanic-aqua",
                    "Royal Sapphire 🔷": "royal-sapphire",
                    "Monet Twilight 🎨": "monet-twilight",
                    "Caravaggio Sepia Noir 🕯️": "caravaggio-sepia-noir",
                    "Stealth Graphite Steel 🖤": "stealth-graphite-steel",
                    "Sunset Mirage 🌅": "sunset-mirage",
                    "Cyber Neon ⚡": "cyber-neon"
                }
                theme_id = name_to_id_map.get(self._current, "forest-green-pro") if self._current else "forest-green-pro"
                theme_config = loader.get_theme_by_id(theme_id)
                return theme_config.get("palette", {})
            except Exception:
                pass
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID (remove emojis)
            theme_id = self._current.lower()
            # Remove emojis and extra spaces
            for emoji in ["🌿", "🍷", "💎", "🌌", "❤️‍🔥", "🪸", "🌇", "✨", "🏛️", "🌊", "🔷", "🎨", "🕯️", "🖤", "🌅", "⚡"]:
                theme_id = theme_id.replace(emoji, "")
            theme_id = theme_id.strip().replace(" ", "-")
            return theme_id
        return "forest-green-pro"
    
    def get_state_styler(self):
        """Get state styler for player state effects."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_state_styler()
        return None
    
    def get_selection_styler(self):
        """Get selection styler for list/tree highlighting."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_selection_styler()
        return None
    
    def get_emphasis_bar_styler(self):
        """Get emphasis bar styler for luxury text bars."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_emphasis_bar_styler()
        return None
    
    def get_theme_metadata(self, theme_name: str) -> Dict[str, str]:
        """Get theme metadata like intro and persona from config."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                for theme_info in theme_list:
                    if theme_info["name"] == theme_name:
                        theme_config = loader.get_theme_by_id(theme_info["id"])
                        return {
                            "intro": theme_config.get("intro", ""),
                            "persona": theme_config.get("persona", ""),
                            "id": theme_config.get("id", "")
                        }
            except Exception:
                pass
        return {"intro": "", "persona": "", "id": ""}

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub
