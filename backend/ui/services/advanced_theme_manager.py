"""
Advanced Theme Manager with real-time color editing, hue adjustment, and theme customization.
Provides a comprehensive interface for theme creation, modification, and management.
"""

import json
import colorsys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class ColorAdjustment:
    """Represents a color adjustment with hue, saturation, and lightness deltas."""
    hue_shift: float = 0.0      # -180 to +180 degrees
    saturation_delta: float = 0.0  # -1.0 to +1.0
    lightness_delta: float = 0.0   # -1.0 to +1.0


class AdvancedThemeManager:
    """
    Advanced theme management system with real-time editing capabilities.
    
    Features:
    - Real-time color palette editing
    - Hue/saturation/lightness adjustments
    - Theme creation and saving
    - Import/export functionality
    - Robust fallback defaults
    - Live preview capabilities
    """
    
    def __init__(self, theme_file_path: Optional[str] = None):
        if theme_file_path is None:
            backend_dir = Path(__file__).parent.parent.parent
            theme_file_path = str(backend_dir / "data" / "poker_themes.json")
        
        self.theme_file_path = theme_file_path
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._defaults: Dict[str, Any] = {}
        self._current_theme_id: Optional[str] = None
        self._custom_themes: Dict[str, Dict[str, Any]] = {}
        self._unsaved_changes: Dict[str, Dict[str, Any]] = {}
        
        self.load_themes()
    
    def load_themes(self) -> bool:
        """Load themes from JSON file with fallback defaults."""
        try:
            with open(self.theme_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._defaults = data.get('defaults', {})
            themes_list = data.get('themes', [])
            
            # Convert themes list to dict by ID
            self._themes = {theme['id']: theme for theme in themes_list}
            
            print(f"✅ Loaded {len(self._themes)} themes from {self.theme_file_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to load themes: {e}")
            self._load_fallback_defaults()
            return False
    
    def _load_fallback_defaults(self):
        """Load robust fallback defaults when theme file is unavailable."""
        self._defaults = {
            "dimensions": {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }
        }
        
        # Create a basic fallback theme
        self._themes = {
            "forest-green-pro": {
                "id": "forest-green-pro",
                "name": "Forest Green Professional 🌿",
                "intro": "Classic casino green with dark wood rails—calm, familiar, and relentlessly focused.",
                "persona": "Doyle Brunson",
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
                    "emphasis_bg_top": "#314F3A",
                    "emphasis_bg_bottom": "#1E3A28",
                    "emphasis_border": "#A88433",
                    "emphasis_accent_text": "#D4AF37"
                }
            }
        }
        print("✅ Loaded fallback default theme")
    
    def get_theme_ids(self) -> List[str]:
        """Get list of all available theme IDs."""
        return list(self._themes.keys())
    
    def get_theme_names(self) -> List[str]:
        """Get list of all theme display names."""
        return [theme['name'] for theme in self._themes.values()]
    
    def get_theme_by_id(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme configuration by ID."""
        return self._themes.get(theme_id)
    
    def get_theme_by_name(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get theme configuration by display name."""
        for theme in self._themes.values():
            if theme.get('name') == theme_name:
                return theme
        return None
    
    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get currently selected theme."""
        if self._current_theme_id:
            return self.get_theme_by_id(self._current_theme_id)
        return None
    
    def set_current_theme(self, theme_id: str) -> bool:
        """Set the current theme by ID."""
        if theme_id in self._themes:
            self._current_theme_id = theme_id
            return True
        return False
    
    def get_palette(self, theme_id: Optional[str] = None) -> Dict[str, str]:
        """Get color palette for specified theme or current theme."""
        if theme_id is None:
            theme_id = self._current_theme_id
        
        if theme_id and theme_id in self._themes:
            return self._themes[theme_id].get('palette', {}).copy()
        
        # Return fallback palette
        return self._get_fallback_palette()
    
    def _get_fallback_palette(self) -> Dict[str, str]:
        """Get fallback color palette."""
        return {
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
            "emphasis_bg_top": "#314F3A",
            "emphasis_bg_bottom": "#1E3A28", 
            "emphasis_border": "#A88433",
            "emphasis_accent_text": "#D4AF37"
        }
    
    def update_color(self, theme_id: str, color_key: str, new_color: str) -> bool:
        """Update a specific color in a theme's palette."""
        if theme_id not in self._themes:
            return False
        
        # Store change in unsaved changes
        if theme_id not in self._unsaved_changes:
            self._unsaved_changes[theme_id] = {}
        
        self._unsaved_changes[theme_id][color_key] = new_color
        
        # Apply change immediately for live preview
        self._themes[theme_id]['palette'][color_key] = new_color
        return True
    
    def adjust_hue(self, theme_id: str, hue_shift_degrees: float) -> bool:
        """Adjust hue for all colors in a theme's palette."""
        if theme_id not in self._themes:
            return False
        
        palette = self._themes[theme_id]['palette']
        
        for color_key, hex_color in palette.items():
            if hex_color.startswith('#') and len(hex_color) == 7:
                new_color = self._adjust_color_hue(hex_color, hue_shift_degrees)
                self.update_color(theme_id, color_key, new_color)
        
        return True
    
    def adjust_saturation(self, theme_id: str, saturation_delta: float) -> bool:
        """Adjust saturation for all colors in a theme's palette."""
        if theme_id not in self._themes:
            return False
        
        palette = self._themes[theme_id]['palette']
        
        for color_key, hex_color in palette.items():
            if hex_color.startswith('#') and len(hex_color) == 7:
                new_color = self._adjust_color_saturation(hex_color, saturation_delta)
                self.update_color(theme_id, color_key, new_color)
        
        return True
    
    def adjust_lightness(self, theme_id: str, lightness_delta: float) -> bool:
        """Adjust lightness for all colors in a theme's palette."""
        if theme_id not in self._themes:
            return False
        
        palette = self._themes[theme_id]['palette']
        
        for color_key, hex_color in palette.items():
            if hex_color.startswith('#') and len(hex_color) == 7:
                new_color = self._adjust_color_lightness(hex_color, lightness_delta)
                self.update_color(theme_id, color_key, new_color)
        
        return True
    
    def _adjust_color_hue(self, hex_color: str, hue_shift_degrees: float) -> str:
        """Adjust the hue of a hex color."""
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Convert to HSL
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            
            # Adjust hue (wrap around)
            h = (h + hue_shift_degrees/360.0) % 1.0
            
            # Convert back to RGB
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            r, g, b = int(r*255), int(g*255), int(b*255)
            
            return f"#{r:02X}{g:02X}{b:02X}"
        except:
            return hex_color
    
    def _adjust_color_saturation(self, hex_color: str, saturation_delta: float) -> str:
        """Adjust the saturation of a hex color."""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            s = max(0.0, min(1.0, s + saturation_delta))
            
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            r, g, b = int(r*255), int(g*255), int(b*255)
            
            return f"#{r:02X}{g:02X}{b:02X}"
        except:
            return hex_color
    
    def _adjust_color_lightness(self, hex_color: str, lightness_delta: float) -> str:
        """Adjust the lightness of a hex color."""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            l = max(0.0, min(1.0, l + lightness_delta))
            
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            r, g, b = int(r*255), int(g*255), int(b*255)
            
            return f"#{r:02X}{g:02X}{b:02X}"
        except:
            return hex_color
    
    def create_theme(self, name: str, base_theme_id: Optional[str] = None) -> str:
        """Create a new custom theme, optionally based on an existing theme."""
        # Generate unique ID
        theme_id = name.lower().replace(' ', '-').replace('🌿', '').replace('🍷', '').replace('💎', '').replace('🌌', '').replace('❤️‍🔥', '').replace('🪸', '').replace('🌇', '').replace('✨', '').replace('🏛️', '').replace('🌊', '').replace('🔷', '').replace('🎨', '').replace('🕯️', '').replace('🖤', '').replace('🌅', '').replace('⚡', '').strip()
        
        # Ensure unique ID
        counter = 1
        original_id = theme_id
        while theme_id in self._themes:
            theme_id = f"{original_id}-{counter}"
            counter += 1
        
        # Create theme based on existing theme or defaults
        if base_theme_id and base_theme_id in self._themes:
            base_theme = self._themes[base_theme_id].copy()
            new_theme = {
                "id": theme_id,
                "name": name,
                "intro": f"Custom theme based on {base_theme.get('name', 'Unknown')}",
                "persona": "Custom",
                "palette": base_theme['palette'].copy()
            }
        else:
            new_theme = {
                "id": theme_id,
                "name": name,
                "intro": "Custom poker theme with distinctive character.",
                "persona": "Custom",
                "palette": self._get_fallback_palette()
            }
        
        self._themes[theme_id] = new_theme
        self._custom_themes[theme_id] = new_theme
        return theme_id
    
    def duplicate_theme(self, source_theme_id: str, new_name: str) -> Optional[str]:
        """Duplicate an existing theme with a new name."""
        if source_theme_id not in self._themes:
            return None
        
        return self.create_theme(new_name, source_theme_id)
    
    def delete_theme(self, theme_id: str) -> bool:
        """Delete a custom theme (cannot delete built-in themes)."""
        if theme_id in self._custom_themes:
            del self._custom_themes[theme_id]
            del self._themes[theme_id]
            if theme_id in self._unsaved_changes:
                del self._unsaved_changes[theme_id]
            return True
        return False
    
    def save_theme(self, theme_id: str) -> bool:
        """Save a theme's changes to the JSON file."""
        try:
            # Load current file data
            with open(self.theme_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update the theme in the data
            themes_list = data.get('themes', [])
            
            # Find and update existing theme or add new one
            theme_found = False
            for i, theme in enumerate(themes_list):
                if theme['id'] == theme_id:
                    themes_list[i] = self._themes[theme_id]
                    theme_found = True
                    break
            
            if not theme_found:
                # Add new theme
                themes_list.append(self._themes[theme_id])
            
            data['themes'] = themes_list
            
            # Save back to file
            with open(self.theme_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Clear unsaved changes for this theme
            if theme_id in self._unsaved_changes:
                del self._unsaved_changes[theme_id]
            
            print(f"✅ Saved theme '{theme_id}' to {self.theme_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save theme '{theme_id}': {e}")
            return False
    
    def has_unsaved_changes(self, theme_id: Optional[str] = None) -> bool:
        """Check if there are unsaved changes for a theme or any theme."""
        if theme_id:
            return theme_id in self._unsaved_changes
        return len(self._unsaved_changes) > 0
    
    def revert_changes(self, theme_id: str) -> bool:
        """Revert unsaved changes for a theme."""
        if theme_id in self._unsaved_changes:
            del self._unsaved_changes[theme_id]
            # Reload the theme from file
            self.load_themes()
            return True
        return False
    
    def export_theme(self, theme_id: str, export_path: str) -> bool:
        """Export a single theme to a JSON file."""
        if theme_id not in self._themes:
            return False
        
        try:
            export_data = {
                "version": "2.0",
                "themes": [self._themes[theme_id]]
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Exported theme '{theme_id}' to {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export theme '{theme_id}': {e}")
            return False
    
    def import_theme(self, import_path: str) -> List[str]:
        """Import themes from a JSON file. Returns list of imported theme IDs."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_themes = []
            themes_list = data.get('themes', [])
            
            for theme in themes_list:
                theme_id = theme.get('id')
                if theme_id:
                    # Handle name conflicts
                    original_id = theme_id
                    counter = 1
                    while theme_id in self._themes:
                        theme_id = f"{original_id}-imported-{counter}"
                        counter += 1
                    
                    theme['id'] = theme_id
                    self._themes[theme_id] = theme
                    self._custom_themes[theme_id] = theme
                    imported_themes.append(theme_id)
            
            print(f"✅ Imported {len(imported_themes)} themes from {import_path}")
            return imported_themes
            
        except Exception as e:
            print(f"❌ Failed to import themes from {import_path}: {e}")
            return []
    
    def get_color_info(self, hex_color: str) -> Dict[str, Any]:
        """Get detailed color information (HSL values, etc.)."""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            
            return {
                "hex": f"#{hex_color.upper()}",
                "rgb": (r, g, b),
                "hue": h * 360,
                "saturation": s * 100,
                "lightness": l * 100
            }
        except:
            return {"hex": "#000000", "rgb": (0, 0, 0), "hue": 0, "saturation": 0, "lightness": 0}
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors."""
        try:
            def luminance(hex_color):
                hex_color = hex_color.lstrip('#')
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                
                def gamma_correct(c):
                    c = c / 255.0
                    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                
                r, g, b = map(gamma_correct, (r, g, b))
                return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
            l1 = luminance(color1)
            l2 = luminance(color2)
            
            lighter = max(l1, l2)
            darker = min(l1, l2)
            
            return (lighter + 0.05) / (darker + 0.05)
        except:
            return 1.0
    
    def suggest_contrast_fix(self, bg_color: str, text_color: str, min_ratio: float = 4.5) -> Optional[str]:
        """Suggest a text color that meets contrast requirements against background."""
        current_ratio = self.calculate_contrast_ratio(bg_color, text_color)
        
        if current_ratio >= min_ratio:
            return None  # Already good
        
        # Try common high-contrast alternatives
        alternatives = ["#FFFFFF", "#F8F8F8", "#000000", "#0D0D0D"]
        
        for alt_color in alternatives:
            if self.calculate_contrast_ratio(bg_color, alt_color) >= min_ratio:
                return alt_color
        
        # If no standard alternative works, try adjusting lightness
        try:
            hex_color = text_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
            
            # Try making it much lighter or much darker
            for new_l in [0.95, 0.05, 0.85, 0.15]:
                r, g, b = colorsys.hls_to_rgb(h, new_l, s)
                r, g, b = int(r*255), int(g*255), int(b*255)
                suggested = f"#{r:02X}{g:02X}{b:02X}"
                
                if self.calculate_contrast_ratio(bg_color, suggested) >= min_ratio:
                    return suggested
        except:
            pass
        
        return "#FFFFFF"  # Ultimate fallback
    
    def reset_theme_to_default(self, theme_id: str) -> bool:
        """Reset a theme to its original default values."""
        if theme_id in self._unsaved_changes:
            del self._unsaved_changes[theme_id]
        
        # Reload from file to get original values
        self.load_themes()
        return theme_id in self._themes
    
    def get_theme_statistics(self) -> Dict[str, Any]:
        """Get statistics about the theme system."""
        return {
            "total_themes": len(self._themes),
            "custom_themes": len(self._custom_themes),
            "unsaved_changes": len(self._unsaved_changes),
            "current_theme": self._current_theme_id,
            "theme_file_path": self.theme_file_path
        }
