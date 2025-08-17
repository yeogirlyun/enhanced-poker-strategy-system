"""
Consolidated theme loader with robust fallbacks and persistence.
Loads from single poker_themes_final_16.json with embedded defaults.
"""

import json
import pathlib
from typing import Dict, Any, Tuple, Optional

# Default theme file location (existing poker_themes.json)
DEFAULT_THEME_FILE = pathlib.Path(__file__).parent.parent.parent / "data" / "poker_themes.json"

# Embedded minimal fallback theme (single theme to ensure app boots)
EMBEDDED_FALLBACK = {
    "defaults": {
        "state_styling": {
            "active": {"glow_color": "$accent", "glow_intensity": 0.8},
            "folded": {"desaturation": 0.7, "opacity": 0.6},
            "winner": {"celebration_rings": 3, "shimmer_color": "$metal"},
            "showdown": {"spotlight_fade": 0.3},
            "all_in": {"flash_intensity": 0.9, "flash_color": "$raise"}
        },
        "selection_highlighting": {
            "treeview": {"selected_bg": "$highlight", "selected_fg": "$highlight_text"},
            "listbox": {"selected_bg": "$highlight", "selected_fg": "$highlight_text"}
        },
        "emphasis_bars": {
            "gradient": {"top": "$emphasis_bg_top", "bottom": "$emphasis_bg_bottom"},
            "border": "$emphasis_border",
            "text": "$emphasis_text",
            "accent_text": "$emphasis_accent_text"
        }
    },
    "themes": [
        {
            "id": "forest-green-pro",
            "name": "Forest Green Professional 🌿",
            "intro": "Classic casino elegance with deep forest tones and golden accents.",
            "persona": "Sophisticated. Timeless. The choice of discerning players.",
            "palette": {
                "felt": "#1B4D3A",
                "rail": "#2E4F76", 
                "metal": "#D4AF37",
                "accent": "#FFD700",
                "raise": "#DC2626",
                "call": "#2563EB",
                "neutral": "#6B7280",
                "text": "#F8FAFC",
                "highlight": "#D4AF37",
                "highlight_text": "#000000",
                "emphasis_bg_top": "#1B4D3A",
                "emphasis_bg_bottom": "#0F2A1F",
                "emphasis_border": "#D4AF37",
                "emphasis_text": "#F8FAFC",
                "emphasis_accent_text": "#FFD700",
                "chip_face": "#2E7D5A",
                "chip_edge": "#1B4D3A",
                "chip_rim": "#D4AF37",
                "chip_text": "#F8FAFC",
                "bet_face": "#DC2626",
                "bet_edge": "#991B1B",
                "bet_rim": "#FCA5A5",
                "bet_text": "#F8FAFC",
                "bet_glow": "#FEE2E2",
                "pot_face": "#D4AF37",
                "pot_edge": "#92400E",
                "pot_rim": "#FDE68A",
                "pot_text": "#000000",
                "pot_glow": "#FEF3C7"
            }
        }
    ]
}


class ConsolidatedThemeLoader:
    """Robust theme loader with fallbacks and user load/save capability."""
    
    def __init__(self):
        """Initialize with default theme file."""
        self._config: Optional[Dict[str, Any]] = None
        self._loaded = False
        self._current_file: Optional[pathlib.Path] = None
    
    def load_themes(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load theme configuration with robust fallbacks.
        
        Args:
            file_path: Optional specific file to load, otherwise uses default
        
        Load order:
        1. Specified file_path (if provided)
        2. Project's backend/data/poker_themes.json (default)
        3. Embedded fallback (single theme)
        
        Returns:
            Complete theme configuration dict
        """
        if not file_path and self._loaded and self._config:
            return self._config
            
        theme_file = None
        
        # Try specified file first
        if file_path:
            try:
                theme_file = pathlib.Path(file_path)
                if theme_file.exists():
                    config_text = theme_file.read_text(encoding="utf-8")
                    self._config = json.loads(config_text)
                    self._current_file = theme_file
                    print(f"✅ Loaded themes from specified file: {theme_file}")
                    self._loaded = True
                    return self._config
            except Exception as e:
                print(f"⚠️  Failed to load specified theme file: {e}")
        
        # Try default project theme file
        try:
            if DEFAULT_THEME_FILE.exists():
                config_text = DEFAULT_THEME_FILE.read_text(encoding="utf-8")
                self._config = json.loads(config_text)
                self._current_file = DEFAULT_THEME_FILE
                print(f"✅ Loaded themes from default file: {DEFAULT_THEME_FILE}")
                self._loaded = True
                return self._config
        except Exception as e:
            print(f"⚠️  Failed to load default theme file: {e}")
        
        # Ultimate fallback - embedded theme
        print("🔄 Using embedded fallback theme")
        self._config = EMBEDDED_FALLBACK
        self._current_file = None
        self._loaded = True
        return self._config
    
    def save_themes(self, config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
        """
        Save theme configuration to specified file or current file.
        
        Args:
            config: Complete theme configuration to save
            file_path: Optional file path to save to, otherwise uses current or default
            
        Returns:
            True if saved successfully
        """
        try:
            # Determine save location
            if file_path:
                save_file = pathlib.Path(file_path)
            elif self._current_file:
                save_file = self._current_file
            else:
                save_file = DEFAULT_THEME_FILE
            
            # Ensure directory exists
            save_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with nice formatting
            config_text = json.dumps(config, ensure_ascii=False, indent=2)
            save_file.write_text(config_text, encoding="utf-8")
            
            # Update cached config
            self._config = config
            self._current_file = save_file
            
            print(f"✅ Saved themes to: {save_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save themes: {e}")
            return False
    
    def get_theme_by_id(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID."""
        config = self.load_themes()
        themes = config.get("themes", [])
        
        for theme in themes:
            if theme.get("id") == theme_id:
                return theme
                
        return None
    
    def get_theme_list(self) -> list[Dict[str, str]]:
        """Get list of available themes with metadata."""
        config = self.load_themes()
        themes = config.get("themes", [])
        
        return [
            {
                "id": theme.get("id", "unknown"),
                "name": theme.get("name", "Unknown Theme"),
                "intro": theme.get("intro", "")
            }
            for theme in themes
        ]
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        config = self.load_themes()
        return config.get("defaults", {})
    
    def reload(self, file_path: Optional[str] = None):
        """Force reload from disk."""
        self._loaded = False
        self._config = None
        return self.load_themes(file_path)
    
    def get_current_file(self) -> Optional[pathlib.Path]:
        """Get currently loaded theme file path."""
        return self._current_file
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load themes from specific file."""
        return self.load_themes(file_path)
    
    def save_to_file(self, config: Dict[str, Any], file_path: str) -> bool:
        """Save themes to specific file."""
        return self.save_themes(config, file_path)


# Singleton instance
_theme_loader: Optional[ConsolidatedThemeLoader] = None


def get_consolidated_theme_loader() -> ConsolidatedThemeLoader:
    """Get singleton theme loader instance."""
    global _theme_loader
    if _theme_loader is None:
        _theme_loader = ConsolidatedThemeLoader()
    return _theme_loader


def load_themes() -> Dict[str, Any]:
    """Convenience function to load themes."""
    return get_consolidated_theme_loader().load_themes()


def save_themes(config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
    """Convenience function to save themes."""
    return get_consolidated_theme_loader().save_themes(config, file_path)
