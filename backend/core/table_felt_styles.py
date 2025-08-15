"""
Table Felt Styles for Casino-Grade Poker Tables

This module provides 10 distinct casino-grade poker table felt styles
with authentic colors, patterns, and textures for digital poker applications.
"""

from typing import Dict, List, Tuple


class TableScheme:
    """Represents a complete table color scheme with felt, rail, border, background, and texture."""

    def __init__(
        self,
        name: str,
        felt_color: str,
        rail_color: str,
        border_color: str,
        background_color: str,
        pattern: str,
        notes: str,
        texture_type: str = "solid",
        gradient_colors: List[str] = None,
        has_gold_inlay: bool = False,
        lighting_effect: str = "none",
    ):
        self.name = name
        self.felt_color = felt_color  # Main playing surface
        self.rail_color = rail_color  # Table edge/border
        self.border_color = border_color  # Outer border/trim
        self.background_color = background_color  # Area around table
        self.pattern = pattern
        self.notes = notes

        # Texture and lighting properties
        # "solid", "gradient", "suede", "diamond", "microfiber", "velvet", "satin"
        self.texture_type = texture_type
        self.gradient_colors = gradient_colors or [
            felt_color
        ]  # For gradient effects
        self.has_gold_inlay = has_gold_inlay  # Gold thread borders
        # "none", "vignette", "center_glow", "frosted_edge"
        self.lighting_effect = lighting_effect

        # Legacy compatibility
        self.hex_color = felt_color  # For backward compatibility
        self.rgb = self._hex_to_rgb(felt_color)

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def __str__(self):
        return f"{self.name} ({self.hex_color})"


class TableSchemeManager:
    """Manages complete table color schemes and provides switching functionality."""

    # Elite Professional Table Schemes (5 exceptional options) - Inspired by
    # PokerStars, WSOP, and premium casino software
    TABLE_SCHEMES = {
        1: TableScheme(
            name="PokerStars Classic Pro",
            felt_color="#1B4D3A",
            rail_color="#8B4513",
            border_color="#2F4F4F",
            background_color="#0A1A0A",
            pattern="Professional diamond weave with subtle card suit watermarks",
            notes="Inspired by PokerStars tournament tables - diamond pattern with embedded suit symbols for premium feel",
            texture_type="diamond_weave_pro",
            gradient_colors=["#1B4D3A", "#2A5D4A"],
            has_gold_inlay=True,
            lighting_effect="center_glow",
        ),
        2: TableScheme(
            name="WSOP Championship",
            felt_color="#8B1538",
            rail_color="#DAA520",
            border_color="#FFD700",
            background_color="#1A0A0A",
            pattern="Premium burgundy with gold accents and radial focus gradient",
            notes="World Series of Poker inspired - championship burgundy with gold trim and tournament lighting",
            texture_type="championship_luxury",
            gradient_colors=["#8B1538", "#9B2548", "#7B0A28"],
            has_gold_inlay=True,
            lighting_effect="tournament_spotlight",
        ),
        3: TableScheme(
            name="Carbon Fiber Elite",
            felt_color="#1C1C1C",
            rail_color="#2F2F2F",
            border_color="#4A4A4A",
            background_color="#0A0A0A",
            pattern="High-tech carbon fiber weave with subtle geometric patterns",
            notes="Modern high-stakes room - carbon fiber texture with geometric precision for tech-savvy players",
            texture_type="carbon_fiber_tech",
            gradient_colors=["#1C1C1C", "#2C2C2C"],
            lighting_effect="tech_glow",
        ),
        4: TableScheme(
            name="Royal Casino Sapphire",
            felt_color="#0F2A44",
            rail_color="#1E3A5F",
            border_color="#C0C0C0",
            background_color="#050F1A",
            pattern="Deep sapphire with silver accents and luxury crosshatch texture",
            notes="High-roller exclusive - deep blue with silver trim and luxury crosshatch for VIP experience",
            texture_type="luxury_crosshatch",
            gradient_colors=["#0F2A44", "#1F3A54", "#2F4A64"],
            has_gold_inlay=False,
            lighting_effect="vip_ambience",
        ),
        5: TableScheme(
            name="Emerald Professional",
            felt_color="#2E5D4A",
            rail_color="#654321",
            border_color="#228B22",
            background_color="#0F1F0F",
            pattern="Traditional emerald with modern speed cloth technology and suit symbol emboss",
            notes="Classic casino perfection - emerald green with speed cloth surface and subtle suit symbol embossing",
            texture_type="speed_cloth_pro",
            gradient_colors=["#2E5D4A", "#3E6D5A"],
            has_gold_inlay=False,
            lighting_effect="classic_vignette",
        ),
    }

    # Default scheme (PokerStars Classic Pro - professional diamond weave with
    # suit watermarks)
    DEFAULT_SCHEME_ID = 1

    def __init__(self):
        self.current_scheme_id = self.DEFAULT_SCHEME_ID

    def get_current_scheme(self) -> TableScheme:
        """Get the currently selected table scheme."""
        return self.TABLE_SCHEMES[self.current_scheme_id]

    def get_scheme_by_id(self, scheme_id: int) -> TableScheme:
        """Get a specific table scheme by ID."""
        if scheme_id in self.TABLE_SCHEMES:
            return self.TABLE_SCHEMES[scheme_id]
        return self.TABLE_SCHEMES[self.DEFAULT_SCHEME_ID]

    def set_scheme(self, scheme_id: int) -> bool:
        """Set the current table scheme. Returns True if successful."""
        if scheme_id in self.TABLE_SCHEMES:
            self.current_scheme_id = scheme_id
            return True
        return False

    def get_all_schemes(self) -> Dict[int, TableScheme]:
        """Get all available table schemes."""
        return self.TABLE_SCHEMES.copy()

    def get_scheme_names(self) -> List[str]:
        """Get a list of all scheme names for UI display."""
        return [scheme.name for scheme in self.TABLE_SCHEMES.values()]

    def get_current_felt_color(self) -> str:
        """Get the felt color of the current scheme."""
        return self.get_current_scheme().felt_color

    def get_current_rail_color(self) -> str:
        """Get the rail color of the current scheme."""
        return self.get_current_scheme().rail_color

    def get_current_border_color(self) -> str:
        """Get the border color of the current scheme."""
        return self.get_current_scheme().border_color

    def get_current_background_color(self) -> str:
        """Get the background color of the current scheme."""
        return self.get_current_scheme().background_color

    # Legacy compatibility methods
    def get_current_style(self) -> TableScheme:
        """Legacy compatibility - returns current scheme."""
        return self.get_current_scheme()

    def get_current_hex_color(self) -> str:
        """Legacy compatibility - returns felt color."""
        return self.get_current_felt_color()

    def set_style(self, style_id: int) -> bool:
        """Legacy compatibility - sets scheme."""
        return self.set_scheme(style_id)

    def get_all_styles(self) -> Dict[int, TableScheme]:
        """Legacy compatibility - returns all schemes."""
        return self.get_all_schemes()

    @property
    def current_style_id(self) -> int:
        """Legacy compatibility property."""
        return self.current_scheme_id

    def apply_scheme_to_widget(
        self, widget, element_type: str = "felt"
    ) -> None:
        """Apply the current scheme color to a Tkinter widget."""
        current_scheme = self.get_current_scheme()
        try:
            if hasattr(widget, "config"):
                if element_type == "felt":
                    widget.config(bg=current_scheme.felt_color)
                elif element_type == "rail":
                    widget.config(bg=current_scheme.rail_color)
                elif element_type == "border":
                    widget.config(bg=current_scheme.border_color)
                elif element_type == "background":
                    widget.config(bg=current_scheme.background_color)
        except Exception:
            pass  # Widget may not support background color

    def apply_style_to_widget(self, widget) -> None:
        """Legacy compatibility - apply felt color to widget."""
        self.apply_scheme_to_widget(widget, "felt")


# Global instance for easy access
scheme_manager = TableSchemeManager()

# Legacy compatibility
felt_manager = scheme_manager


def get_felt_manager() -> TableSchemeManager:
    """Get the global scheme manager instance (legacy compatibility)."""
    return scheme_manager


def get_scheme_manager() -> TableSchemeManager:
    """Get the global scheme manager instance."""
    return scheme_manager
