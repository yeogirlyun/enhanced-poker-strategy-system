"""
Theme loader for config-driven poker theme system.
Loads theme packs from JSON and provides access to defaults and themes.
"""

import json
from typing import Dict, Any, Tuple, Optional
from pathlib import Path


class ThemeLoader:
    """Loads and manages poker theme configurations from JSON."""

    def __init__(self, theme_pack_path: Optional[str] = None):
        """Initialize theme loader with optional custom path."""
        if theme_pack_path is None:
            # Default to poker_themes.json in backend/data directory
            backend_dir = Path(__file__).parent.parent.parent
            theme_pack_path = str(backend_dir / "data" / "poker_themes.json")

        self.theme_pack_path = theme_pack_path
        self._defaults: Optional[Dict[str, Any]] = None
        self._themes: Optional[Dict[str, Dict[str, Any]]] = None
        self._loaded = False

    def load_theme_pack(self) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Load theme pack from JSON file.

        Returns:
            Tuple of (defaults, themes_dict) where:
            - defaults: Configuration defaults for states, selection, etc.
            - themes_dict: Dictionary mapping theme_id -> theme_config
        """
        if self._loaded and self._defaults is not None and self._themes is not None:
            return self._defaults, self._themes

        try:
            with open(self.theme_pack_path, "r", encoding="utf-8") as f:
                pack = json.load(f)

            self._defaults = pack.get("defaults", {})
            themes_list = pack.get("themes", [])
            self._themes = {theme["id"]: theme for theme in themes_list}
            self._loaded = True

            print(f"✅ Loaded {len(self._themes)} themes from {self.theme_pack_path}")
            return self._defaults, self._themes

        except FileNotFoundError:
            print(f"⚠️ Theme pack not found: {self.theme_pack_path}")
            return self._get_fallback_config()
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in theme pack: {e}")
            return self._get_fallback_config()
        except Exception as e:
            print(f"⚠️ Error loading theme pack: {e}")
            return self._get_fallback_config()

    def get_theme_by_id(self, theme_id: str) -> Dict[str, Any]:
        """Get a specific theme by ID with auto-generated emphasis tokens."""
        defaults, themes = self.load_theme_pack()
        
        theme_config = None
        if theme_id in themes:
            theme_config = themes[theme_id].copy()  # Make a copy to avoid modifying original
        else:
            # Fallback to first available theme
            if themes:
                fallback_id = list(themes.keys())[0]
                print(f"⚠️ Theme '{theme_id}' not found, using '{fallback_id}'")
                theme_config = themes[fallback_id].copy()
            else:
                # Ultimate fallback
                theme_config = self._get_fallback_theme()

        return theme_config

    def get_theme_list(self) -> list[Dict[str, str]]:
        """Get list of available themes with id and name."""
        defaults, themes = self.load_theme_pack()
        return [
            {"id": theme_id, "name": theme_config.get("name", theme_id)}
            for theme_id, theme_config in themes.items()
        ]

    def get_defaults(self) -> Dict[str, Any]:
        """Get configuration defaults."""
        defaults, _ = self.load_theme_pack()
        return defaults
    


    def _get_fallback_config(self) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Provide fallback configuration if JSON loading fails."""
        defaults = {
            "state": {
                "active": {
                    "glow": "#1DB954",
                    "shimmer": "#C9A34E",
                    "strength": 1.0,
                    "period_ms": 2000,
                },
                "folded": {"desaturate": 0.8, "opacity": 0.4},
                "winner": {
                    "glow": "#C9A34E",
                    "shimmer": "#1DB954",
                    "strength": 1.4,
                    "period_ms": 1500,
                    "particles": True,
                },
                "showdown": {
                    "spotlight": "#FFFFFF",
                    "spotlight_opacity": 0.18,
                    "duration_ms": 1500,
                },
                "allin": {
                    "glow": "#B63D3D",
                    "shimmer": "#C9A34E",
                    "strength": 1.2,
                    "flash_ms": 400,
                },
            },
            "selection": {"row_bg": "$highlight", "row_fg": "$highlight_text"},
            "emphasis_bar": {
                "bg_top": "#2D5A3D",
                "bg_bottom": "#4A3428",
                "text": "#F8E7C9",
                "accent_text": "#B63D3D",
                "divider": "#C9A34E",
                "texture": "velvet_8pct",
            },
            "chips": {
                "stack": {
                    "face": "#334155",
                    "edge": "#6B7280",
                    "rim": "#9CA3AF",
                    "text": "#F8F7F4",
                },
                "bet": {
                    "face": "#1DB954",
                    "edge": "#16A34A",
                    "rim": "#C9A34E",
                    "text": "#F8F7F4",
                    "glow": "#22C55E",
                },
                "pot": {
                    "face": "#D4AF37",
                    "edge": "#B8860B",
                    "rim": "#F59E0B",
                    "text": "#0B0B0E",
                    "glow": "#FCD34D",
                },
            },
        }

        themes = {"forest-green-pro": self._get_fallback_theme()}

        return defaults, themes

    def _get_fallback_theme(self) -> Dict[str, Any]:
        """Provide fallback theme if loading fails."""
        return {
            "id": "forest-green-pro",
            "name": "Forest Green Professional",
            "palette": {
                "felt": "#2D5A3D",
                "rail": "#4A3428",
                "metal": "#C9A34E",
                "accent": "#1DB954",
                "raise": "#B63D3D",
                "call": "#2AA37A",
                "neutral": "#9AA0A6",
                "text": "#EDECEC",
                "highlight": "#D4AF37",
                "highlight_text": "#0B0B0E",
                "emphasis_text": "#F8E7C9",
            },
        }
    
    def reload(self):
        """Force reload themes from file."""
        print("🔄 ThemeLoader: Forcing reload from file...")
        self._loaded = False
        self._defaults = None
        self._themes = None
        return self.load_theme_pack()


# Global instance for easy access
_theme_loader = None


def get_theme_loader() -> ThemeLoader:
    """Get the global theme loader instance."""
    global _theme_loader
    if _theme_loader is None:
        _theme_loader = ThemeLoader()
    return _theme_loader
