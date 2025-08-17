from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes, build_theme_from_config, get_available_theme_names, get_theme_by_name, THEME_BASES
    from .theme_loader import get_theme_loader
    from .state_styler import get_state_styler, get_selection_styler, get_emphasis_bar_styler
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Theme ordering for 4×4 grid layout
THEME_ORDER = [
    # Row 1 – Classic Casino
    "Forest Green Professional", "Velvet Burgundy", "Obsidian Gold", "Imperial Jade",
    # Row 2 – Luxury Noir (Art-inspired)
    "Monet Noir", "Caravaggio Noir", "Klimt Royale", "Deco Luxe",
    # Row 3 – Nature & Light
    "Sunset Mirage", "Oceanic Blue", "Velour Crimson", "Golden Dusk",
    # Row 4 – Modern / Bold
    "Cyber Neon", "Stealth Graphite", "Royal Sapphire", "Midnight Aurora",
]

DEFAULT_THEME_NAME = "Forest Green Professional"  # Safe, iconic default

# Theme icons for enhanced picker
THEME_ICONS = {
    "Forest Green Professional": "🌿",
    "Velvet Burgundy": "🍷",
    "Obsidian Gold": "♠️",
    "Imperial Jade": "💎",
    "Monet Noir": "🎨",
    "Caravaggio Noir": "🕯️",
    "Klimt Royale": "✨",
    "Deco Luxe": "🏛️",
    "Sunset Mirage": "🌅",
    "Oceanic Blue": "🌊",
    "Velour Crimson": "♥️",
    "Golden Dusk": "🌇",
    "Cyber Neon": "⚡",
    "Stealth Graphite": "🖤",
    "Royal Sapphire": "🔷",
    "Midnight Aurora": "🌌",
}

# Theme introductions for live preview
THEME_INTROS = {
    "Forest Green Professional": "Classic casino green with dark wood rails—calm, familiar, and relentlessly focused.\nThe unshakable grinder, disciplined as Doyle Brunson with a stare that never blinks.",
    "Velvet Burgundy": "Wine-red felt and brass trim; a private salon after midnight, hushed and opulent.\nThe old-school aristocrat, smooth like Johnny Chan swirling tea instead of chips.",
    "Obsidian Gold": "Deep obsidian felt with golden filigree; a vault-like Monte Carlo table.\nThe strategist, calm and relentless as Erik Seidel, measuring every move with quiet precision.",
    "Imperial Jade": "Deep emerald with antique gold; stately and serene, a table that breathes confidence.\nThe regal commander, poised as Chip Reese playing only the finest spots.",
    "Monet Noir": "Moonlit indigos and silver glints—soft reflections like water at night.\nThe artist of variance, graceful as Patrik Antonius in a midnight cash game.",
    "Caravaggio Noir": "Chiaroscuro drama: black depths, crimson heat, and strokes of bright gold.\nThe fearless gladiator, theatrical as Tom Dwan in a high-stakes duel.",
    "Klimt Royale": "Obsidian field, ornamental gold, a whisper of emerald; decadent and celebratory.\nThe philosopher-queen, brilliant as Liv Boeree balancing intellect with elegance.",
    "Deco Luxe": "Champagne geometry on jet black—Art-Deco glamour with emerald accents.\nThe stylish innovator, cool as Vanessa Selbst breaking molds with precision.",
    "Sunset Mirage": "Amber to violet across the felt; the warmth of a desert dusk under velvet lights.\nThe desert legend, steady as Daniel Negreanu chatting his way through Vegas dusk.",
    "Oceanic Blue": "Midnight blues with turquoise spray—cool, refreshing, quietly modern.\nThe calm predator, patient like Erik Seidel drifting just beneath the surface.",
    "Velour Crimson": "Crimson velour sheen with mahogany rails; opulent, seductive, dangerous.\nThe fearless provocateur, intense as Phil Ivey locking eyes across a high-stakes duel.",
    "Golden Dusk": "Burnished amber over dark leather; cinematic nostalgia that never hurries.\nThe veteran closer, timeless as Barry Greenstein's measured wisdom under soft lights.",
    "Cyber Neon": "Electric teals and magentas on charcoal—arcade energy for fast grinders.\nThe online warrior, relentless as Fedor Holz clicking into destiny.",
    "Stealth Graphite": "Matte blacks and gunmetal edges; silent, aerodynamic focus.\nThe assassin, cold as Justin Bonomo narrowing eyes over darkened glass.",
    "Royal Sapphire": "Jewel-blue confidence with crisp trim—bold, polished, unmistakable.\nThe crowned champion, commanding as Phil Hellmuth in full regalia.",
    "Midnight Aurora": "Deep indigo washed with aurora greens and violets—expansive, weightless, rare.\nThe cosmic visionary, ethereal as Viktor \"Isildur1\" Blom chasing infinite hands.",
}


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
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
            elif "Emerald Noir" in self._themes:
                self._current = "Emerald Noir"
                self._theme = dict(self._themes["Emerald Noir"])
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
        # Three themes from the spec
        EMERALD_NOIR = {
            "table.felt": "#1B4D3A",  # Professional poker green from old UI
            "table.rail": "#2E4F76",  # Dark steel blue rail from old UI
            "table.edgeGlow": "#0B2F24",
            "table.inlay": "#C6A664",
            # Old UI professional colors
            "primary_bg": "#191C22",  # Dark charcoal
            "secondary_bg": "#2E3C54",  # Deep navy slate
            "text_gold": "#FFD700",  # Gold highlights
            "border_active": "#FFD700",  # Gold active border
            "board.slotBg": "#133C2E",
            "board.cardFaceFg": "#111317",
            "board.cardBack": "#1E293B",
            "board.border": "#0D1F18",
            "pot.badgeBg": "#0F766E",
            "pot.badgeFg": "#EDE9FE",
            "pot.valueText": "#F8FAFC",
            "pot.glow": "#14B8A6",
            "sidePot.badgeBg": "#075985",
            "sidePot.badgeFg": "#E2E8F0",
            "chip.primary": "#EAB308",
            "chip.secondary": "#9CA3AF",
            "chip.tertiary": "#34D399",
            "chip.quaternary": "#60A5FA",
            "chip.high": "#F43F5E",
            "bet.path": "#0EA5E9",
            "bet.splash": "#22D3EE",
            "bet.text": "#F8FAFC",
            "rake.indicator": "#F59E0B",
            "seat.bg.idle": "#0F172A",
            "seat.bg.active": "#1E293B",
            "seat.bg.acting": "#063970",
            "seat.bg.dealer": "#3F3F46",
            "seat.ring": "#334155",
            "seat.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "player.name": "#E2E8F0",
            "player.stack": "#FDE68A",
            "player.noteTag": "#93C5FD",
            "avatar.border": "#C7D2FE",
            "avatar.bg": "#0B1220",
            "action.fold": "#64748B",
            "action.check": "#A7F3D0",
            "action.call": "#34D399",
            "action.bet": "#F59E0B",
            "action.raise": "#FB7185",
            "action.allin": "#EF4444",
            "timer.arcBg": "#0B1220",
            "timer.arcFg": "#22D3EE",
            "dealer.buttonBg": "#FDE68A",
            "dealer.buttonFg": "#0B1220",
            "dealer.ring": "#EAB308",
            "dealer.buttonBorder": "#D97706",
            # Additional pot tokens
            "pot.bg": "#1E2937",
            "pot.border": "#374151",
            "pot.label": "#9CA3AF",
            # Bet display tokens
            "bet.bg": "#374151",
            "bet.border": "#6B7280",
            "bet.text": "#FFD700",
            "bet.active": "#DC2626",
            # Action indicator tokens
            "action.ring": "#10B981",
            "action.pulse": "#34D399",
            "action.text": "#FFFFFF",
            # Button states for Emerald Casino theme
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#E0E0E0",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#2D5A3D",
            "btn.hover.fg": "#FFD700",
            "btn.hover.shadow": "#2D5A3D",  # Remove alpha channel for Tkinter compatibility
            "btn.active.bg": "#008F4C",
            "btn.active.fg": "#FFD700",
            "btn.active.border": "#FFD700",
            "btn.active.shadow": "inset 0 2px 4px rgba(0,0,0,0.3)",
            "btn.disabled.bg": "#3A3A3A",
            "btn.disabled.fg": "#777777",
            # Legacy button tokens (backward compatibility)
            "btn.primaryBg": "#008F4C",
            "btn.primaryFg": "#FFD700",
            "btn.secondaryBg": "#1E1E1E",
            "btn.secondaryFg": "#E0E0E0",
            "btn.dangerBg": "#DC2626",
            "btn.dangerFg": "#FEF2F2",
            "btn.disabledBg": "#3A3A3A",
            "btn.disabledFg": "#777777",
            "btn.focusRing": "#22D3EE",
            "hud.bg": "#0B1220",
            "hud.fg": "#E2E8F0",
            "hud.border": "#1F2937",
            "hud.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "panel.bg": "#111827",
            "panel.fg": "#E5E7EB",
            "panel.border": "#1F2937",
            "panel.sectionTitle": "#C7D2FE",
            "msg.infoBg": "#0EA5E9",
            "msg.infoFg": "#06202C",
            "msg.successBg": "#10B981",
            "msg.successFg": "#062217",
            "msg.warnBg": "#F59E0B",
            "msg.warnFg": "#261A00",
            "msg.errorBg": "#EF4444",
            "msg.errorFg": "#2A0C0C",
            "grid.lines": "#0F172A",
            "grid.highlight": "#22D3EE",
            "a11y.focusRing": "#22D3EE",
            "a11y.highContrastText": "#FFFFFF",
            "a11y.link": "#93C5FD",
            "cardHighlight.win": "#16A34A",
            "cardHighlight.muck": "#64748B",
            "equity.barGood": "#34D399",
            "equity.barBad": "#F87171",
            "font.display": ("Inter", 28, "bold"),
            "font.h1": ("Inter", 20, "bold"),
            "font.h2": ("Inter", 16, "semibold"),
            "font.body": ("Inter", 13, "normal"),
            "font.mono": ("JetBrains Mono", 12, "normal"),
        }
        ROYAL_INDIGO = {
            "table.felt": "#243B53",
            "table.rail": "#111827",
            "table.edgeGlow": "#0B1322",
            "table.inlay": "#9CA3AF",
            "board.slotBg": "#1E293B",
            "board.cardFaceFg": "#0F172A",
            "board.cardBack": "#202A44",
            "board.border": "#0B1220",
            "pot.badgeBg": "#3B82F6",
            "pot.badgeFg": "#0B1220",
            "pot.valueText": "#F8FAFC",
            "pot.glow": "#60A5FA",
            "sidePot.badgeBg": "#64748B",
            "sidePot.badgeFg": "#F1F5F9",
            "chip.primary": "#F59E0B",
            "chip.secondary": "#94A3B8",
            "chip.tertiary": "#22C55E",
            "chip.quaternary": "#3B82F6",
            "chip.high": "#A78BFA",
            "bet.path": "#60A5FA",
            "bet.splash": "#93C5FD",
            "bet.text": "#0B1220",
            "rake.indicator": "#F59E0B",
            "seat.bg.idle": "#0B1220",
            "seat.bg.active": "#111827",
            "seat.bg.acting": "#1D4ED8",
            "seat.bg.dealer": "#334155",
            "seat.ring": "#475569",
            "seat.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "player.name": "#E5E7EB",
            "player.stack": "#FDE68A",
            "player.noteTag": "#A7F3D0",
            "avatar.border": "#93C5FD",
            "avatar.bg": "#0B1220",
            "action.fold": "#64748B",
            "action.check": "#86EFAC",
            "action.call": "#22C55E",
            "action.bet": "#F59E0B",
            "action.raise": "#C026D3",
            "action.allin": "#EF4444",
            "timer.arcBg": "#0B1220",
            "timer.arcFg": "#60A5FA",
            "dealer.buttonBg": "#F1F5F9",
            "dealer.buttonFg": "#0B1220",
            "dealer.ring": "#3B82F6",
            "dealer.buttonBorder": "#3B82F6",
            # Additional pot tokens
            "pot.bg": "#1E293B",
            "pot.border": "#475569",
            "pot.label": "#94A3B8",
            # Bet display tokens
            "bet.bg": "#475569",
            "bet.border": "#64748B",
            "bet.text": "#F1F5F9",
            "bet.active": "#DC2626",
            # Action indicator tokens  
            "action.ring": "#3B82F6",
            "action.pulse": "#60A5FA",
            "action.text": "#FFFFFF",
            # Button states for Midnight Blue theme  
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#D9D9D9",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#1D3557",
            "btn.hover.fg": "#D9D9D9",
            "btn.hover.shadow": "#1D3557",  # Remove alpha channel for Tkinter compatibility
            "btn.active.bg": "#0A192F",
            "btn.active.fg": "#D9D9D9",
            "btn.active.border": "#60A5FA",
            "btn.active.shadow": "inset 0 2px 4px rgba(0,0,0,0.3)",
            "btn.disabled.bg": "#444444",
            "btn.disabled.fg": "#777777",
            # Legacy button tokens (backward compatibility)
            "btn.primaryBg": "#0A192F",
            "btn.primaryFg": "#D9D9D9",
            "btn.secondaryBg": "#1E1E1E",
            "btn.secondaryFg": "#D9D9D9",
            "btn.dangerBg": "#B91C1C",
            "btn.dangerFg": "#FEE2E2",
            "btn.disabledBg": "#444444",
            "btn.disabledFg": "#777777",
            "btn.focusRing": "#60A5FA",
            "hud.bg": "#0B1220",
            "hud.fg": "#E2E8F0",
            "hud.border": "#1F2937",
            "hud.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "panel.bg": "#0F172A",
            "panel.fg": "#E5E7EB",
            "panel.border": "#1F2937",
            "panel.sectionTitle": "#93C5FD",
            "msg.infoBg": "#38BDF8",
            "msg.infoFg": "#05131B",
            "msg.successBg": "#22C55E",
            "msg.successFg": "#04150C",
            "msg.warnBg": "#F59E0B",
            "msg.warnFg": "#241700",
            "msg.errorBg": "#EF4444",
            "msg.errorFg": "#2A0C0C",
            "grid.lines": "#0F172A",
            "grid.highlight": "#60A5FA",
            "a11y.focusRing": "#60A5FA",
            "a11y.highContrastText": "#FFFFFF",
            "a11y.link": "#93C5FD",
            "cardHighlight.win": "#22C55E",
            "cardHighlight.muck": "#64748B",
            "equity.barGood": "#34D399",
            "equity.barBad": "#FB7185",
            "font.display": ("Inter", 28, "bold"),
            "font.h1": ("Inter", 20, "bold"),
            "font.h2": ("Inter", 16, "semibold"),
            "font.body": ("Inter", 13, "normal"),
            "font.mono": ("JetBrains Mono", 12, "normal"),
        }
        CRIMSON_GOLD = {
            "table.felt": "#3A0A0A",
            "table.rail": "#1F1B16",
            "table.edgeGlow": "#240808",
            "table.inlay": "#D4AF37",
            "board.slotBg": "#2B0F0F",
            "board.cardFaceFg": "#121212",
            "board.cardBack": "#271717",
            "board.border": "#1A1010",
            "pot.badgeBg": "#B45309",
            "pot.badgeFg": "#FFFBEA",
            "pot.valueText": "#FEF3C7",
            "pot.glow": "#F59E0B",
            "sidePot.badgeBg": "#7C2D12",
            "sidePot.badgeFg": "#FEEBC8",
            "chip.primary": "#F59E0B",
            "chip.secondary": "#9CA3AF",
            "chip.tertiary": "#10B981",
            "chip.quaternary": "#60A5FA",
            "chip.high": "#F43F5E",
            "bet.path": "#F59E0B",
            "bet.splash": "#FBBF24",
            "bet.text": "#1F1305",
            "rake.indicator": "#FFD166",
            "seat.bg.idle": "#140A0A",
            "seat.bg.active": "#1E1010",
            "seat.bg.acting": "#7F1D1D",
            "seat.bg.dealer": "#3B2F2F",
            "seat.ring": "#5B3A3A",
            "seat.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "player.name": "#FDE68A",
            "player.stack": "#FFF3BF",
            "player.noteTag": "#FBBF24",
            "avatar.border": "#D4AF37",
            "avatar.bg": "#120A0A",
            "action.fold": "#78716C",
            "action.check": "#FDE68A",
            "action.call": "#FDE68A",
            "action.bet": "#F59E0B",
            "action.raise": "#DC2626",
            "action.allin": "#EF4444",
            "timer.arcBg": "#120A0A",
            "timer.arcFg": "#F59E0B",
            "dealer.buttonBg": "#FDE68A",
            "dealer.buttonFg": "#1F1305",
            "dealer.ring": "#D4AF37",
            "dealer.buttonBorder": "#B45309",
            # Additional pot tokens
            "pot.bg": "#2B0F0F",
            "pot.border": "#531A1A",
            "pot.label": "#A78A5A",
            # Bet display tokens
            "bet.bg": "#531A1A",
            "bet.border": "#7C2D12",
            "bet.text": "#FDE68A",
            "bet.active": "#DC2626",
            # Action indicator tokens
            "action.ring": "#D4AF37",
            "action.pulse": "#F59E0B",
            "action.text": "#FFFFFF",
            # Button states for Burgundy Royale theme
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#E0E0E0",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#7A1C1C",
            "btn.hover.fg": "#E6C76E",
            "btn.hover.shadow": "#7A1C1C",  # Remove alpha channel for Tkinter compatibility
            "btn.active.bg": "#B22222",
            "btn.active.fg": "#FFD700",
            "btn.active.border": "#FFD700",
            "btn.active.shadow": "inset 0 2px 4px rgba(0,0,0,0.3)",
            "btn.disabled.bg": "#2B2B2B",
            "btn.disabled.fg": "#777777",
            # Legacy button tokens (backward compatibility)
            "btn.primaryBg": "#B22222",
            "btn.primaryFg": "#FFD700",
            "btn.secondaryBg": "#1E1E1E",
            "btn.secondaryFg": "#E0E0E0",
            "btn.dangerBg": "#B91C1C",
            "btn.dangerFg": "#FEE2E2",
            "btn.disabledBg": "#2B2B2B",
            "btn.disabledFg": "#777777",
            "btn.focusRing": "#F59E0B",
            "hud.bg": "#120A0A",
            "hud.fg": "#F5F5F4",
            "hud.border": "#292524",
            "hud.shadow": "#000000",  # Remove alpha channel for Tkinter compatibility
            "panel.bg": "#1A1010",
            "panel.fg": "#F5F5F4",
            "panel.border": "#292524",
            "panel.sectionTitle": "#FBBF24",
            "msg.infoBg": "#FCD34D",
            "msg.infoFg": "#2C2209",
            "msg.successBg": "#10B981",
            "msg.successFg": "#012117",
            "msg.warnBg": "#F59E0B",
            "msg.warnFg": "#241700",
            "msg.errorBg": "#DC2626",
            "msg.errorFg": "#2A0C0C",
            "grid.lines": "#291111",
            "grid.highlight": "#F59E0B",
            "a11y.focusRing": "#F59E0B",
            "a11y.highContrastText": "#FFFFFF",
            "a11y.link": "#FBBF24",
            "cardHighlight.win": "#F59E0B",
            "cardHighlight.muck": "#78716C",
            "equity.barGood": "#F59E0B",
            "equity.barBad": "#EF4444",
            "font.display": ("Cinzel", 28, "bold"),
            "font.h1": ("Cinzel", 20, "bold"),
            "font.h2": ("Inter", 16, "semibold"),
            "font.body": ("Inter", 13, "normal"),
            "font.mono": ("JetBrains Mono", 12, "normal"),
        }
        
        # Five Professional Casino Table Schemes (matching table_felt_styles.py)
        POKERSTARS_CLASSIC_PRO = {
            # Table Scheme 1: PokerStars Classic Pro (#1B4D3A)
            "table.felt": "#1B4D3A",  # Deep professional green (matches screenshot!)
            "table.rail": "#8B4513",  # Rich bronze/copper rail
            "table.railHighlight": "#DAA520",  # Gold accent lines
            "table.edgeGlow": "#2F4F4F",  # Dark slate border
            "table.inlay": "#1A3A2A",  # Subtle inner felt
            "table.center": "#154035",  # Center oval highlight
            "primary_bg": "#0A1A0A",  # Very dark green background
            "secondary_bg": "#1E3A2E",  # Medium green slate
            "text_gold": "#DAA520",  # Gold text
            "border_active": "#DAA520",  # Gold active border
            # Left Column UI Panel Colors
            "panel.bg": "#0F1419",  # Dark green panel background
            "panel.fg": "#E5E7EB",  # Light text
            "panel.sectionTitle": "#DAA520",  # Gold section titles
            "panel.border": "#2F4F4F",  # Dark border
            "btn.primaryBg": "#16A34A",  # Green primary button (Load)
            "btn.primaryFg": "#F8FAFC",  # White primary text
            "btn.secondaryBg": "#334155",  # Dark secondary buttons (Next/Auto/Reset)
            "btn.secondaryFg": "#E2E8F0",  # Light secondary text
            "a11y.focusRing": "#DAA520",  # Gold focus ring
            # Enhanced Button State Colors
            "btn.default.bg": "#16A34A",  # Green default button
            "btn.default.fg": "#F8FAFC",  # White text
            "btn.hover.bg": "#22C55E",   # Lighter green hover
            "btn.hover.fg": "#F8FAFC",   # White text
            "btn.active.bg": "#15803D",  # Darker green active
            "btn.active.fg": "#DAA520",  # Gold active text
            "btn.disabled.bg": "#374151", # Gray disabled
            "btn.disabled.fg": "#9CA3AF", # Light gray text
            "board.slotBg": "#0A2A1A",
            "board.cardFaceFg": "#FFFFFF",
            "board.cardBack": "#8B0000",  # Red card backs like screenshot
            "board.border": "#2F4F4F",
            "pot.valueText": "#DAA520",  # Gold pot text
            "chip_gold": "#DAA520",
            "seat.bg.idle": "#334155",  # Dark blue player pods like screenshot
            "seat.bg.active": "#475569",
            "seat.bg.acting": "#DAA520",  # Gold border for acting player
            "player.name": "#E5E7EB",
            "player.stack": "#DAA520",  # Gold stack text
            "dealer.buttonBg": "#DAA520",  # Gold dealer button
            "dealer.buttonFg": "#0A1A0A",
            "dealer.buttonBorder": "#B8860B",
            "pot.bg": "#1A3A2A",
            "pot.border": "#2F4F4F",
            "pot.label": "#DAA520",
            "bet.bg": "#1A3A2A",
            "bet.border": "#2F4F4F", 
            "bet.text": "#DAA520",
        }
        
        WSOP_CHAMPIONSHIP = {
            # Table Scheme 2: WSOP Championship Burgundy (#8B1538)
            "table.felt": "#8B1538",  # Championship burgundy
            "table.rail": "#DAA520",  # Gold rail
            "table.railHighlight": "#FFD700",  # Bright gold highlights
            "table.edgeGlow": "#FFD700",  # Gold border
            "table.inlay": "#7B0A28",  # Darker burgundy inlay
            "table.center": "#7B1340",  # Center accent
            "primary_bg": "#1A0A0A",  # Very dark background
            "secondary_bg": "#3A1A1A",  # Dark burgundy
            "text_gold": "#FFD700",  # Bright gold text
            # Left Column UI Panel Colors
            "panel.bg": "#2A0E0E",  # Dark burgundy panel background
            "panel.fg": "#F3E8FF",  # Light purple-tinted text
            "panel.sectionTitle": "#FFD700",  # Gold section titles
            "panel.border": "#7B0A28",  # Burgundy border
            "btn.primaryBg": "#DC2626",  # Red primary button (Load)
            "btn.primaryFg": "#FEF3C7",  # Cream primary text
            "btn.secondaryBg": "#4A1A2A",  # Dark burgundy secondary buttons
            "btn.secondaryFg": "#F9FAFB",  # Light secondary text
            "a11y.focusRing": "#FFD700",  # Gold focus ring
            # Enhanced Button State Colors
            "btn.default.bg": "#DC2626",  # Red default button
            "btn.default.fg": "#FEF3C7",  # Cream text
            "btn.hover.bg": "#EF4444",   # Lighter red hover
            "btn.hover.fg": "#FEF3C7",   # Cream text
            "btn.active.bg": "#B91C1C",  # Darker red active
            "btn.active.fg": "#FFD700",  # Gold active text
            "btn.disabled.bg": "#4A1A2A", # Dark burgundy disabled
            "btn.disabled.fg": "#9CA3AF", # Light gray text
            "border_active": "#FFD700",
            "board.slotBg": "#6B1030",
            "board.cardFaceFg": "#FFFFFF",
            "board.cardBack": "#8B0000",
            "board.border": "#FFD700",
            "pot.valueText": "#FFD700",
            "chip_gold": "#FFD700",
            "seat.bg.idle": "#4A1A2A",
            "seat.bg.active": "#5A2A3A",
            "seat.bg.acting": "#FFD700",
            "player.name": "#F5F5F5",
            "player.stack": "#FFD700",
            "dealer.buttonBg": "#FFD700",
            "dealer.buttonFg": "#1A0A0A",
            "dealer.buttonBorder": "#DAA520",
            "pot.bg": "#6B1030",
            "pot.border": "#FFD700",
            "pot.label": "#FFD700",
            "bet.bg": "#6B1030",
            "bet.border": "#FFD700",
            "bet.text": "#FFD700",
        }
        

        
        ROYAL_CASINO_SAPPHIRE = {
            # Table Scheme 4: Royal Casino Sapphire (#0F2A44)
            "table.felt": "#0F2A44",  # Deep sapphire blue
            "table.rail": "#1E3A5F",  # Medium blue rail
            "table.railHighlight": "#C0C0C0",  # Silver highlights
            "table.edgeGlow": "#C0C0C0",  # Silver border
            "table.inlay": "#1A3550",  # Subtle blue inlay
            "table.center": "#2A4A64",  # Center accent
            "primary_bg": "#050F1A",  # Very dark blue
            "secondary_bg": "#0A1F2A",  # Dark blue
            "text_gold": "#C0C0C0",  # Silver text
            "border_active": "#C0C0C0",
            # Left Column UI Panel Colors
            "panel.bg": "#0A1520",  # Dark sapphire panel background
            "panel.fg": "#E5E8EB",  # Light blue-tinted text
            "panel.sectionTitle": "#C0C0C0",  # Silver section titles
            "panel.border": "#1E3A5F",  # Blue border
            "btn.primaryBg": "#1976D2",  # Blue primary button (Load)
            "btn.primaryFg": "#F8FAFC",  # White primary text
            "btn.secondaryBg": "#1A3A50",  # Dark blue secondary buttons
            "btn.secondaryFg": "#E5E8EB",  # Light secondary text
            "a11y.focusRing": "#C0C0C0",  # Silver focus ring
            # Enhanced Button State Colors
            "btn.default.bg": "#1976D2",  # Blue default button
            "btn.default.fg": "#F8FAFC",  # White text
            "btn.hover.bg": "#2196F3",   # Lighter blue hover
            "btn.hover.fg": "#F8FAFC",   # White text
            "btn.active.bg": "#1565C0",  # Darker blue active
            "btn.active.fg": "#C0C0C0",  # Silver active text
            "btn.disabled.bg": "#1A3A50", # Dark blue disabled
            "btn.disabled.fg": "#9CA3AF", # Light gray text
            "board.slotBg": "#2A4060",
            "board.cardFaceFg": "#FFFFFF",
            "board.cardBack": "#4A6080",
            "board.border": "#C0C0C0",
            "pot.valueText": "#C0C0C0",
            "chip_gold": "#C0C0C0",
            "seat.bg.idle": "#1A3A50",
            "seat.bg.active": "#2A4A60",
            "seat.bg.acting": "#C0C0C0",
            "player.name": "#E5E8EB",
            "player.stack": "#C0C0C0",
            "dealer.buttonBg": "#C0C0C0",
            "dealer.buttonFg": "#050F1A",
            "dealer.buttonBorder": "#A0A0A0",
            "pot.bg": "#2A4060",
            "pot.border": "#C0C0C0",
            "pot.label": "#C0C0C0",
            "bet.bg": "#2A4060",
            "bet.border": "#C0C0C0",
            "bet.text": "#C0C0C0",
        }
        
        EMERALD_PROFESSIONAL = {
            # Table Scheme 5: Emerald Professional (#2E5D4A)
            "table.felt": "#2E5D4A",  # Traditional emerald green
            "table.rail": "#654321",  # Brown leather rail
            "table.railHighlight": "#228B22",  # Forest green accents
            "table.edgeGlow": "#228B22",  # Green border
            "table.inlay": "#3A6D5A",  # Lighter green inlay
            "table.center": "#4A7D6A",  # Center highlight
            "primary_bg": "#0F1F0F",  # Very dark green
            "secondary_bg": "#1F3F2F",  # Dark green
            "text_gold": "#228B22",  # Forest green text
            "border_active": "#228B22",
            # Left Column UI Panel Colors
            "panel.bg": "#0F1F15",  # Dark forest panel background
            "panel.fg": "#E0F0E0",  # Light green-tinted text
            "panel.sectionTitle": "#228B22",  # Forest green section titles
            "panel.border": "#3A6D5A",  # Green border
            "btn.primaryBg": "#22A049",  # Green primary button (Load)
            "btn.primaryFg": "#F0FFF0",  # Light green primary text
            "btn.secondaryBg": "#2A4A3A",  # Dark green secondary buttons
            "btn.secondaryFg": "#E0F0E0",  # Light secondary text
            "a11y.focusRing": "#228B22",  # Forest green focus ring
            # Enhanced Button State Colors
            "btn.default.bg": "#22A049",  # Green default button
            "btn.default.fg": "#F0FFF0",  # Light green text
            "btn.hover.bg": "#16A34A",   # Lighter green hover
            "btn.hover.fg": "#F0FFF0",   # Light green text
            "btn.active.bg": "#15803D",  # Darker green active
            "btn.active.fg": "#228B22",  # Forest green active text
            "btn.disabled.bg": "#2A4A3A", # Dark green disabled
            "btn.disabled.fg": "#9CA3AF", # Light gray text
            "board.slotBg": "#4A7D6A",
            "board.cardFaceFg": "#FFFFFF",
            "board.cardBack": "#8B0000",
            "board.border": "#228B22",
            "pot.valueText": "#228B22",
            "chip_gold": "#228B22",
            "seat.bg.idle": "#2A4A3A",
            "seat.bg.active": "#3A5A4A",
            "seat.bg.acting": "#228B22",
            "player.name": "#E0E8E0",
            "player.stack": "#228B22",
            "dealer.buttonBg": "#228B22",
            "dealer.buttonFg": "#0F1F0F",
            "dealer.buttonBorder": "#1E7B1E",
            "pot.bg": "#4A7D6A",
            "pot.border": "#228B22",
            "pot.label": "#228B22",
            "bet.bg": "#4A7D6A",
            "bet.border": "#228B22",
            "bet.text": "#228B22",
        }
        
        # Monet Noir - Midnight blue & misted green with antique light-gold accents
        MONET_NOIR = {
            # Surfaces (noir midnight + subtle brass)
            "table.felt": "#0F1A24",         # midnight teal/indigo
            "table.rail": "#0B0F14",         # charcoal black
            "table.inlay": "#C9B47A",        # antique light gold
            "table.edgeGlow": "#142330",     # soft rim glow
            "panel.bg": "#111417",
            "panel.border": "#1F2327",
            "panel.shadow": "#00000080",

            # Core text
            "text.primary":   "#F2EAD8",     # warm parchment
            "text.secondary": "#CFC6AF",
            "text.muted":     "#9BA5A8",

            # Pot & side pots
            "pot.badgeBg":    "#15212B",     # deep blue badge
            "pot.badgeRing":  "#C9B47A",
            "pot.valueText":  "#F6EFDD",
            "sidePot.badgeBg":"#1A2732",
            "sidePot.badgeFg":"#E7DECA",

            # Actions (cool/casino)
            "action.fold":  "#6E7781",
            "action.check": "#8EC7AF",
            "action.call":  "#1B8F6A",
            "action.bet":   "#C9B47A",
            "action.raise": "#A1536E",       # rose brass
            "action.allin": "#D46060",

            # Chips (muted jewel tones)
            "chip.primary":      "#C9B47A",
            "chip.secondary":    "#9BA5A8",
            "chip.tertiary":     "#78C2A4",
            "chip.quaternary":   "#6AA0D3",
            "chip.high":         "#C96C80",

            # Board/cards
            "board.slotBg":      "#0F1A24",
            "board.cardFaceFg":  "#0E141A",
            "board.cardBack":    "#162231",
            "board.border":      "#0A121A",

            # Button system (per-type, with full states)
            # PRIMARY = "gold on noir"
            "btn.primary.bg":        "#171D22",
            "btn.primary.fg":        "#F2EAD8",
            "btn.primary.border":    "#C9B47A",
            "btn.primary.hoverBg":   "#1E262C",
            "btn.primary.hoverFg":   "#FFF6E3",
            "btn.primary.hoverBorder":"#E3CD90",
            "btn.primary.activeBg":  "#26303A",
            "btn.primary.activeFg":  "#FFF9EC",
            "btn.primary.activeBorder":"#EAD89F",
            "btn.primary.disabledBg":"#1A1F24",
            "btn.primary.disabledFg":"#9BA5A8",
            "btn.primary.disabledBorder":"#242A30",

            # SECONDARY = "burgundy noir"
            "btn.secondary.bg":        "#1A1518",
            "btn.secondary.fg":        "#E8D9CF",
            "btn.secondary.border":    "#6E2B3E",
            "btn.secondary.hoverBg":   "#23191E",
            "btn.secondary.hoverFg":   "#F2E5DE",
            "btn.secondary.hoverBorder":"#8A3C56",
            "btn.secondary.activeBg":  "#2B1E25",
            "btn.secondary.activeFg":  "#F8EFEB",
            "btn.secondary.activeBorder":"#A04B6B",
            "btn.secondary.disabledBg":"#1D191C",
            "btn.secondary.disabledFg":"#9F9499",
            "btn.secondary.disabledBorder":"#262124",

            # DANGER = "crimson noir"
            "btn.danger.bg":        "#241416",
            "btn.danger.fg":        "#FBEDEF",
            "btn.danger.border":    "#9E3B49",
            "btn.danger.hoverBg":   "#2B171A",
            "btn.danger.hoverFg":   "#FFF3F5",
            "btn.danger.hoverBorder":"#B74859",
            "btn.danger.activeBg":  "#321A1F",
            "btn.danger.activeFg":  "#FFF6F8",
            "btn.danger.activeBorder":"#CC5366",
            "btn.danger.disabledBg":"#21191B",
            "btn.danger.disabledFg":"#9C8A8E",
            "btn.danger.disabledBorder":"#2A2022",

            # Focus & a11y
            "a11y.focus": "#E3CD90",
            "divider":    "#20262B",
            "grid.lines": "#182026",

            # Typography (fallbacks)
            "font.display": ("Inter", 28, "bold"),
            "font.h1":      ("Inter", 20, "semibold"),
            "font.h2":      ("Inter", 16, "semibold"),
            "font.body":    ("Inter", 13, "normal"),
            "font.mono":    ("JetBrains Mono", 12, "normal"),

            # Compatibility tokens for existing components
            "primary_bg": "#111417",
            "secondary_bg": "#1F2327",
            "text_gold": "#C9B47A",
            "border_active": "#C9B47A",
            "panel.fg": "#F2EAD8",
            "dealer.buttonBg": "#F2EAD8",
            "dealer.buttonFg": "#15212B",
            "dealer.buttonBorder": "#C9B47A",
            "seat.bg.idle": "#0B0F14",
            "seat.bg.active": "#15212B",
            "seat.bg.acting": "#1E262C",
            "player.name": "#CFC6AF",
            "player.stack": "#C9B47A",
            "table.railHighlight": "#C9B47A",
            "table.center": "#142330",
        }

        CARAVAGGIO_NOIR = {
            "table.felt": "#0B0C10", "table.rail": "#09090A", "table.inlay": "#B39B5E", "table.edgeGlow": "#161417",
            "panel.bg": "#0F1012", "panel.border": "#1B1B1E", "panel.shadow": "#00000099",
            "text.primary": "#EDECEC", "text.secondary": "#B7B7B7", "text.muted": "#8C8C8C",
            "pot.badgeBg": "#141316", "pot.badgeRing": "#D1B46A", "pot.valueText": "#FAF8F0",
            "sidePot.badgeBg": "#1A191C", "sidePot.badgeFg": "#EFE8D8",
            "action.fold": "#6E6A6A", "action.check": "#9CD6BE", "action.call": "#2AA37A",
            "action.bet": "#D1B46A", "action.raise": "#B63D3D", "action.allin": "#E24A4A",
            "chip.primary": "#D1B46A", "chip.secondary": "#9AA0A6", "chip.tertiary": "#6FC3A7",
            "chip.quaternary": "#6BA0D6", "chip.high": "#C45C6C",
            "board.slotBg": "#0E0F14", "board.cardFaceFg": "#101215", "board.cardBack": "#15161C", "board.border": "#0B0B0E",
            # Buttons (gold + crimson contrasts)
            "btn.primary.bg": "#171718", "btn.primary.fg": "#F5F2E9", "btn.primary.border": "#D1B46A",
            "btn.primary.hoverBg": "#1E1E20", "btn.primary.hoverFg": "#FFF8E8", "btn.primary.hoverBorder": "#E6CC8C",
            "btn.primary.activeBg": "#262629", "btn.primary.activeFg": "#FFFBF0", "btn.primary.activeBorder": "#EED99E",
            "btn.primary.disabledBg": "#1A1A1B", "btn.primary.disabledFg": "#9D9D9D", "btn.primary.disabledBorder": "#262627",
            "btn.secondary.bg": "#1A1415", "btn.secondary.fg": "#EFDFDF", "btn.secondary.border": "#6C2A2E",
            "btn.secondary.hoverBg": "#22191A", "btn.secondary.hoverFg": "#F8ECEC", "btn.secondary.hoverBorder": "#8C383E",
            "btn.secondary.activeBg": "#2A1E20", "btn.secondary.activeFg": "#FFF2F3", "btn.secondary.activeBorder": "#A6464D",
            "btn.secondary.disabledBg": "#20191A", "btn.secondary.disabledFg": "#A28E90", "btn.secondary.disabledBorder": "#282122",
            "btn.danger.bg": "#241416", "btn.danger.fg": "#FBEDEF", "btn.danger.border": "#9E3B49",
            "btn.danger.hoverBg": "#2B171A", "btn.danger.hoverFg": "#FFF3F5", "btn.danger.hoverBorder": "#B74859",
            "btn.danger.activeBg": "#321A1F", "btn.danger.activeFg": "#FFF6F8", "btn.danger.activeBorder": "#CC5366",
            "btn.danger.disabledBg": "#21191B", "btn.danger.disabledFg": "#9C8A8E", "btn.danger.disabledBorder": "#2A2022",
            "a11y.focus": "#E6CC8C", "divider": "#232325", "grid.lines": "#1A1A1C",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#0F1012", "secondary_bg": "#1B1B1E", "text_gold": "#D1B46A", "border_active": "#D1B46A",
            "panel.fg": "#EDECEC", "dealer.buttonBg": "#EDECEC", "dealer.buttonFg": "#141316", "dealer.buttonBorder": "#D1B46A",
            "seat.bg.idle": "#09090A", "seat.bg.active": "#141316", "seat.bg.acting": "#1E1E20",
            "player.name": "#B7B7B7", "player.stack": "#D1B46A", "table.railHighlight": "#D1B46A", "table.center": "#161417",
        }

        KLIMT_ROYALE = {
            "table.felt": "#121212", "table.rail": "#0E0D0B", "table.inlay": "#CFAF63", "table.edgeGlow": "#201B12",
            "panel.bg": "#14110F", "panel.border": "#262018", "panel.shadow": "#00000080",
            "text.primary": "#F9F3DD", "text.secondary": "#D3C7A2", "text.muted": "#A79977",
            "pot.badgeBg": "#1E1912", "pot.badgeRing": "#CFAF63", "pot.valueText": "#FFF6DD",
            "sidePot.badgeBg": "#241E15", "sidePot.badgeFg": "#F6E9C9",
            "action.fold": "#7A7361", "action.check": "#A9E2C7", "action.call": "#32B37A",
            "action.bet": "#CFAF63", "action.raise": "#B23B43", "action.allin": "#DE505A",
            "chip.primary": "#CFAF63", "chip.secondary": "#B1B5B8", "chip.tertiary": "#7ECDAF",
            "chip.quaternary": "#6DA8DA", "chip.high": "#C96B7A",
            "board.slotBg": "#16130E", "board.cardFaceFg": "#14110E", "board.cardBack": "#19150F", "board.border": "#0F0D0A",
            # Buttons (gold first)
            "btn.primary.bg": "#1A1916", "btn.primary.fg": "#FFF2D9", "btn.primary.border": "#CFAF63",
            "btn.primary.hoverBg": "#232119", "btn.primary.hoverFg": "#FFF7E6", "btn.primary.hoverBorder": "#E4C97D",
            "btn.primary.activeBg": "#2C281E", "btn.primary.activeFg": "#FFFBEF", "btn.primary.activeBorder": "#EED895",
            "btn.primary.disabledBg": "#1E1C18", "btn.primary.disabledFg": "#A3997D", "btn.primary.disabledBorder": "#27241E",
            "btn.secondary.bg": "#191516", "btn.secondary.fg": "#F2E4E4", "btn.secondary.border": "#6B2B36",
            "btn.secondary.hoverBg": "#21191B", "btn.secondary.hoverFg": "#F9EAEA", "btn.secondary.hoverBorder": "#873545",
            "btn.secondary.activeBg": "#2A1E21", "btn.secondary.activeFg": "#FFF1F1", "btn.secondary.activeBorder": "#A04052",
            "btn.secondary.disabledBg": "#1E191A", "btn.secondary.disabledFg": "#A79294", "btn.secondary.disabledBorder": "#272123",
            "btn.danger.bg": "#241416", "btn.danger.fg": "#FBEDEF", "btn.danger.border": "#9E3B49",
            "btn.danger.hoverBg": "#2B171A", "btn.danger.hoverFg": "#FFF3F5", "btn.danger.hoverBorder": "#B74859",
            "btn.danger.activeBg": "#321A1F", "btn.danger.activeFg": "#FFF6F8", "btn.danger.activeBorder": "#CC5366",
            "btn.danger.disabledBg": "#21191B", "btn.danger.disabledFg": "#9C8A8E", "btn.danger.disabledBorder": "#2A2022",
            "a11y.focus": "#E4C97D", "divider": "#2B251C", "grid.lines": "#1E1914",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#14110F", "secondary_bg": "#262018", "text_gold": "#CFAF63", "border_active": "#CFAF63",
            "panel.fg": "#F9F3DD", "dealer.buttonBg": "#F9F3DD", "dealer.buttonFg": "#1E1912", "dealer.buttonBorder": "#CFAF63",
            "seat.bg.idle": "#0E0D0B", "seat.bg.active": "#1E1912", "seat.bg.acting": "#232119",
            "player.name": "#D3C7A2", "player.stack": "#CFAF63", "table.railHighlight": "#CFAF63", "table.center": "#201B12",
        }

        WHISTLER_NOCTURNE = {
            "table.felt": "#0D1B2A", "table.rail": "#0B121B", "table.inlay": "#B7C1C8", "table.edgeGlow": "#142334",
            "panel.bg": "#0F1620", "panel.border": "#1B2736", "panel.shadow": "#00000080",
            "text.primary": "#F5F7FA", "text.secondary": "#C5D0DA", "text.muted": "#98A8B8",
            "pot.badgeBg": "#122130", "pot.badgeRing": "#B7C1C8", "pot.valueText": "#F8FAFC",
            "sidePot.badgeBg": "#162635", "sidePot.badgeFg": "#E6EDF3",
            "action.fold": "#718496", "action.check": "#98E0D0", "action.call": "#57C2B6",
            "action.bet": "#B7C1C8", "action.raise": "#6C94D2", "action.allin": "#6FB5E7",
            "chip.primary": "#B7C1C8", "chip.secondary": "#96A3AF", "chip.tertiary": "#7BD0BC",
            "chip.quaternary": "#6EA3D6", "chip.high": "#8EB7E4",
            "board.slotBg": "#0E1A28", "board.cardFaceFg": "#0C141C", "board.cardBack": "#122032", "board.border": "#0A141F",
            # Buttons (teal glow)
            "btn.primary.bg": "#14202A", "btn.primary.fg": "#F5F7FA", "btn.primary.border": "#B7C1C8",
            "btn.primary.hoverBg": "#182734", "btn.primary.hoverFg": "#FFFFFF", "btn.primary.hoverBorder": "#D0D9DF",
            "btn.primary.activeBg": "#1C2F3E", "btn.primary.activeFg": "#FFFFFF", "btn.primary.activeBorder": "#E1E8ED",
            "btn.primary.disabledBg": "#151F28", "btn.primary.disabledFg": "#A1B2C2", "btn.primary.disabledBorder": "#1D2834",
            "btn.secondary.bg": "#171A1E", "btn.secondary.fg": "#E8EDF4", "btn.secondary.border": "#32465E",
            "btn.secondary.hoverBg": "#1D2228", "btn.secondary.hoverFg": "#F2F6FA", "btn.secondary.hoverBorder": "#3E5570",
            "btn.secondary.activeBg": "#232B34", "btn.secondary.activeFg": "#FFFFFF", "btn.secondary.activeBorder": "#4A6280",
            "btn.secondary.disabledBg": "#191D22", "btn.secondary.disabledFg": "#A9B5C2", "btn.secondary.disabledBorder": "#212833",
            "btn.danger.bg": "#241416", "btn.danger.fg": "#FBEDEF", "btn.danger.border": "#9E3B49",
            "btn.danger.hoverBg": "#2B171A", "btn.danger.hoverFg": "#FFF3F5", "btn.danger.hoverBorder": "#B74859",
            "btn.danger.activeBg": "#321A1F", "btn.danger.activeFg": "#FFF6F8", "btn.danger.activeBorder": "#CC5366",
            "btn.danger.disabledBg": "#21191B", "btn.danger.disabledFg": "#9C8A8E", "btn.danger.disabledBorder": "#2A2022",
            "a11y.focus": "#D0D9DF", "divider": "#1C2733", "grid.lines": "#15202B",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#0F1620", "secondary_bg": "#1B2736", "text_gold": "#B7C1C8", "border_active": "#B7C1C8",
            "panel.fg": "#F5F7FA", "dealer.buttonBg": "#F5F7FA", "dealer.buttonFg": "#122130", "dealer.buttonBorder": "#B7C1C8",
            "seat.bg.idle": "#0B121B", "seat.bg.active": "#122130", "seat.bg.acting": "#182734",
            "player.name": "#C5D0DA", "player.stack": "#B7C1C8", "table.railHighlight": "#B7C1C8", "table.center": "#142334",
        }

        # Luxury LV Noir theme system
        LV_NOIR = {
            # Luxury LV-inspired palette - deep espresso + burgundy + antique gold
            "table.felt": "#2A120F",      # deep mahogany felt
            "table.rail": "#1B1612",      # dark leather rail
            "table.inlay": "#6B5B3E",     # aged brass inlay
            "table.edgeGlow": "#3B201A",  # subtle edge glow
            "table.railHighlight": "#C3A568", # antique gold highlight
            "table.center": "#3B201A",    # center accent
            
            # Core text system
            "text.primary": "#F3EAD7",    # warm parchment
            "text.secondary": "#C9BFA9",  # secondary text
            "text.muted": "#948B79",      # muted text
            "text_primary": "#F3EAD7",    # compatibility
            "text_secondary": "#C9BFA9",  # compatibility
            "text_gold": "#C3A568",       # antique gold text
            
            # Gold system
            "gold.base": "#C3A568",       # antique gold
            "gold.bright": "#E8C87B",     # bright gold
            "gold.dim": "#9E8756",        # dim gold
            
            # Burgundy system
            "burgundy.base": "#7E1D1D",   # burgundy base
            "burgundy.deep": "#4A0F12",   # deep burgundy
            "burgundy.bright": "#A22A2A", # bright burgundy
            
            # Emerald accent (sparingly)
            "emerald.base": "#0F6B4A",    # emerald base
            "emerald.bright": "#1FA97B",  # bright emerald
            
            # Steel blues (charts/HUD hints)
            "indigo.dim": "#263345",      # dim indigo
            "indigo.base": "#32465E",     # base indigo
            
            # Panels & backgrounds
            "panel.bg": "#141110",        # panel background
            "panel.fg": "#F3EAD7",        # panel foreground
            "panel.border": "#2A2622",    # panel border
            "panel.shadow": "#000000",    # panel shadow (no alpha for tkinter)
            "panel.sectionTitle": "#E8C87B", # section titles
            "primary_bg": "#141110",      # compatibility
            "secondary_bg": "#2A2622",    # compatibility
            "border_active": "#C3A568",   # active borders
            "border_inactive": "#2A2622",  # inactive borders
            
            # Pot badge & chips
            "pot.badgeBg": "#3A2D1E",     # pot badge background
            "pot.badgeRing": "#C3A568",   # pot badge ring
            "pot.valueText": "#F7ECD1",   # pot value text
            "pot.bg": "#3A2D1E",          # compatibility
            "pot.border": "#C3A568",      # compatibility
            "pot.label": "#C9BFA9",       # compatibility
            "chip.low": "#948B79",        # low value chips
            "chip.mid": "#C3A568",        # mid value chips
            "chip.high": "#B33E4B",       # high value chips
            "chip_gold": "#C3A568",       # compatibility
            
            # Actions
            "action.fold": "#70685B",     # fold action
            "action.check": "#8DC9AF",    # check action
            "action.call": "#1FA97B",     # call action
            "action.bet": "#D4972E",      # bet action
            "action.raise": "#CC3C52",    # raise action
            "action.allin": "#E43D3D",    # all-in action
            "action.ring": "#C3A568",     # compatibility
            "action.pulse": "#E8C87B",    # compatibility
            "action.text": "#F3EAD7",     # compatibility
            
            # Focus & accessibility
            "a11y.focus": "#E8C87B",      # focus indicator
            "a11y.warn": "#D4972E",       # warning color
            "a11y.error": "#E43D3D",      # error color
            "a11y.focusRing": "#E8C87B",  # compatibility
            
            # Dividers & grid
            "divider": "#2A2622",         # dividers
            "grid.lines": "#1E1B18",      # grid lines
            
            # Board & cards
            "board.slotBg": "#2A120F",    # card slot background
            "board.cardFaceFg": "#F3EAD7", # card face foreground
            "board.cardBack": "#7E1D1D",  # card back (burgundy)
            "board.border": "#6B5B3E",    # card border
            
            # Seats & players
            "seat.bg.idle": "#1B1612",    # idle seat background
            "seat.bg.active": "#2A2622",  # active seat background
            "seat.bg.acting": "#3A2D1E",  # acting seat background
            "player.name": "#C9BFA9",     # player name color
            "player.stack": "#C3A568",    # player stack color
            
            # Dealer button
            "dealer.buttonBg": "#F1E3B2", # dealer button background
            "dealer.buttonFg": "#3A2D1E", # dealer button foreground
            "dealer.buttonBorder": "#C3A568", # dealer button border
            
            # Bet display
            "bet.bg": "#3A2D1E",          # bet background
            "bet.border": "#C3A568",      # bet border
            "bet.text": "#F7ECD1",        # bet text
            "bet.active": "#E8C87B",      # active bet
            
            # Enhanced buttons - Primary (antique gold)
            "btn.default.bg": "#1E1A17",  # primary default background
            "btn.default.fg": "#F3EAD7",  # primary default foreground
            "btn.hover.bg": "#2A2521",    # primary hover background
            "btn.hover.fg": "#FFF3D9",    # primary hover foreground
            "btn.active.bg": "#3A2F24",   # primary active background
            "btn.active.fg": "#FFF7E6",   # primary active foreground
            "btn.disabled.bg": "#241F1C", # primary disabled background
            "btn.disabled.fg": "#948B79", # primary disabled foreground
            
            # Panel UI tokens
            "btn.primaryBg": "#1E1A17",   # compatibility
            "btn.primaryFg": "#F3EAD7",   # compatibility
            "btn.secondaryBg": "#1B1415", # secondary button background
            "btn.secondaryFg": "#EEDFCC", # secondary button foreground
        }
        
        CRIMSON_MONOGRAM = {
            # Crimson luxury variant - deeper reds with gold accents
            "table.felt": "#3B0E11",      # deep crimson felt
            "table.rail": "#1B1612",      # dark leather rail
            "table.inlay": "#6B5B3E",     # aged brass inlay
            "table.edgeGlow": "#4A1013",  # crimson edge glow
            "table.railHighlight": "#E8C87B", # bright gold highlight
            "table.center": "#4A1013",    # center accent
            
            "text.primary": "#F3EAD7",    # warm parchment
            "text.secondary": "#C9BFA9",  # secondary text
            "text.muted": "#948B79",      # muted text
            "text_primary": "#F3EAD7",    # compatibility
            "text_secondary": "#C9BFA9",  # compatibility
            "text_gold": "#E8C87B",       # bright gold text
            
            "gold.base": "#C3A568",       # antique gold
            "gold.bright": "#E8C87B",     # bright gold
            "gold.dim": "#9E8756",        # dim gold
            
            "burgundy.base": "#A22A2A",   # brighter burgundy
            "burgundy.deep": "#7E1D1D",   # deep burgundy
            "burgundy.bright": "#CC3C52", # bright burgundy
            
            "panel.bg": "#141110",        # panel background
            "panel.fg": "#F3EAD7",        # panel foreground
            "panel.border": "#4A1013",    # crimson panel border
            "primary_bg": "#141110",      # compatibility
            "secondary_bg": "#4A1013",    # compatibility
            "border_active": "#E8C87B",   # bright gold borders
            "border_inactive": "#4A1013",  # crimson borders
            
            "pot.badgeBg": "#4A1013",     # crimson pot badge background
            "pot.badgeRing": "#E8C87B",   # gold pot badge ring
            "pot.valueText": "#F7ECD1",   # pot value text
            "pot.bg": "#4A1013",          # crimson pot background
            "pot.border": "#E8C87B",      # gold pot border
            "pot.label": "#C9BFA9",       # pot label
            "chip_gold": "#E8C87B",       # bright gold chips
            
            "board.cardBack": "#A22A2A",  # brighter burgundy cards
            "board.border": "#6B5B3E",    # aged brass border
            "board.slotBg": "#3B0E11",    # crimson slot background
            "board.cardFaceFg": "#F3EAD7", # card face foreground
            
            "seat.bg.idle": "#1B1612",    # idle seat background
            "seat.bg.active": "#4A1013",  # active seat background
            "seat.bg.acting": "#6A1518",  # acting seat background
            "player.name": "#C9BFA9",     # player name color
            "player.stack": "#E8C87B",    # player stack color (bright gold)
            
            "dealer.buttonBg": "#F1E3B2", # dealer button background
            "dealer.buttonFg": "#3A2D1E", # dealer button foreground
            "dealer.buttonBorder": "#E8C87B", # bright gold border
            
            "btn.default.bg": "#2A1517",  # crimson button background
            "btn.default.fg": "#F3EAD7",  # button foreground
            "btn.hover.bg": "#3A1F22",    # crimson hover
            "btn.hover.fg": "#FFF3D9",    # hover foreground
            "btn.active.bg": "#4A252A",   # crimson active
            "btn.active.fg": "#FFF7E6",   # active foreground
            "btn.disabled.bg": "#241F1C", # disabled background
            "btn.disabled.fg": "#948B79", # disabled foreground
            
            "btn.primaryBg": "#2A1517",   # compatibility
            "btn.primaryFg": "#F3EAD7",   # compatibility
            "btn.secondaryBg": "#3A1F22", # secondary button background
            "btn.secondaryFg": "#EEDFCC", # secondary button foreground
        }
        
        OBSIDIAN_EMERALD = {
            # Obsidian luxury variant - deep blacks with emerald accents
            "table.felt": "#111A17",      # deep obsidian felt
            "table.rail": "#10100E",      # black rail
            "table.inlay": "#6B5B3E",     # aged brass inlay
            "table.edgeGlow": "#1A2B22",  # emerald edge glow
            "table.railHighlight": "#1FA97B", # emerald highlight
            "table.center": "#1A2B22",    # emerald center
            
            "text.primary": "#F3EAD7",    # warm parchment
            "text.secondary": "#C9BFA9",  # secondary text
            "text.muted": "#948B79",      # muted text
            "text_primary": "#F3EAD7",    # compatibility
            "text_secondary": "#C9BFA9",  # compatibility
            "text_gold": "#1FA97B",       # emerald text
            
            "gold.base": "#C3A568",       # antique gold (kept)
            "gold.bright": "#E8C87B",     # bright gold (kept)
            "emerald.base": "#0F6B4A",    # emerald base
            "emerald.bright": "#1FA97B",  # bright emerald
            
            "panel.bg": "#0D0F0E",        # obsidian panel background
            "panel.fg": "#F3EAD7",        # panel foreground
            "panel.border": "#1A2B22",    # emerald panel border
            "primary_bg": "#0D0F0E",      # compatibility
            "secondary_bg": "#1A2B22",    # compatibility
            "border_active": "#1FA97B",   # emerald borders
            "border_inactive": "#1A2B22",  # dark emerald borders
            
            "pot.badgeBg": "#1A2B22",     # emerald pot badge background
            "pot.badgeRing": "#1FA97B",   # emerald pot badge ring
            "pot.valueText": "#F7ECD1",   # pot value text
            "pot.bg": "#1A2B22",          # emerald pot background
            "pot.border": "#1FA97B",      # bright emerald border
            "pot.label": "#C9BFA9",       # pot label
            "chip_gold": "#1FA97B",       # emerald chips
            
            "board.cardBack": "#0F6B4A",  # emerald card backs
            "board.border": "#6B5B3E",    # aged brass border
            "board.slotBg": "#111A17",    # obsidian slot background
            "board.cardFaceFg": "#F3EAD7", # card face foreground
            
            "seat.bg.idle": "#10100E",    # idle seat background
            "seat.bg.active": "#1A2B22",  # active seat background
            "seat.bg.acting": "#2A3B2F",  # acting seat background
            "player.name": "#C9BFA9",     # player name color
            "player.stack": "#1FA97B",    # player stack color (emerald)
            
            "dealer.buttonBg": "#F1E3B2", # dealer button background
            "dealer.buttonFg": "#3A2D1E", # dealer button foreground
            "dealer.buttonBorder": "#1FA97B", # emerald border
            
            "btn.default.bg": "#151A17",  # obsidian button background
            "btn.default.fg": "#F3EAD7",  # button foreground
            "btn.hover.bg": "#1F2B24",    # emerald hover
            "btn.hover.fg": "#FFF3D9",    # hover foreground
            "btn.active.bg": "#2A3B2F",   # emerald active
            "btn.active.fg": "#FFF7E6",   # active foreground
            "btn.disabled.bg": "#1A1C1A", # disabled background
            "btn.disabled.fg": "#948B79", # disabled foreground
            
            "btn.primaryBg": "#151A17",   # compatibility
            "btn.primaryFg": "#F3EAD7",   # compatibility
            "btn.secondaryBg": "#1F2B24", # secondary button background
            "btn.secondaryFg": "#EEDFCC", # secondary button foreground
        }

        # V2 Overrides - Enhanced theme differentiation for distinct visual identity
        # Each painter theme now has clearly different hue families for instant recognition
        
        # Monet Noir V2 - indigo + teal + silver accents (cool palette)
        MONET_NOIR_V2_OVERRIDES = {
            # Panels & ambience (colder navy base)
            "panel.bg": "#0B1622",
            "panel.border": "#1A2A3A",
            # Buttons (cool teal + silver)
            "btn.primary.bg": "#0E7A6F",
            "btn.primary.fg": "#F0FAF7",
            "btn.primary.border": "#D7E2E8",   # silver
            "btn.primary.hoverBg": "#0A6A61",
            "btn.primary.hoverBorder": "#E6EEF1",
            "btn.primary.activeBg": "#095D55",
            "btn.primary.activeBorder": "#F1F5F7",
            "btn.secondary.bg": "#314C6E",  # slate blue
            "btn.secondary.fg": "#EAF0F6",
            "btn.secondary.border": "#B6C7D7",
            "btn.secondary.hoverBg": "#2A4261",
            "btn.secondary.activeBg": "#223953",
            # Pot badge (navy + silver ring)
            "pot.badgeBg": "#102536",
            "pot.badgeRing": "#C8D5DE",
            "pot.valueText": "#F4F8FB",
            # Tab/list accents (icy)
            "a11y.focus": "#CFE1EB",
            "divider": "#1C2A36",
            "grid.lines": "#14222E",
        }

        # Caravaggio Noir V2 - true black + crimson + gold (chiaroscuro)
        CARAVAGGIO_NOIR_V2_OVERRIDES = {
            # Panels & ambience (near-true black)
            "panel.bg": "#0A0A0C",
            "panel.border": "#1A1A1E",
            # Buttons (crimson + bright gold)
            "btn.primary.bg": "#B3122E",   # vivid crimson
            "btn.primary.fg": "#FFF7E6",
            "btn.primary.border": "#E1C16E",   # bright gold
            "btn.primary.hoverBg": "#9E0F28",
            "btn.primary.activeBg": "#8C0D23",
            "btn.secondary.bg": "#2A1416", # dark burgundy
            "btn.secondary.fg": "#F2E4E4",
            "btn.secondary.border": "#8C383E",
            "btn.secondary.hoverBg": "#33181B",
            "btn.secondary.activeBg": "#3B1B1F",
            # Pot badge (espresso + gold ring)
            "pot.badgeBg": "#121012",
            "pot.badgeRing": "#E1C16E",
            "pot.valueText": "#FFF9EE",
            # Tab/list accents (gold underline)
            "a11y.focus": "#EAD28B",
            "divider": "#242326",
            "grid.lines": "#1B1A1D",
        }

        # Klimt Royale V2 - warm obsidian + bright gold + emerald
        KLIMT_ROYALE_V2_OVERRIDES = {
            # Panels & ambience (warm obsidian)
            "panel.bg": "#17130E",
            "panel.border": "#2A2217",
            # Buttons (gold primary, emerald secondary)
            "btn.primary.bg": "#F4C430",   # rich gold
            "btn.primary.fg": "#1C1408",
            "btn.primary.border": "#E4C97D",
            "btn.primary.hoverBg": "#E6B623",
            "btn.primary.activeBg": "#D8AB1F",
            "btn.secondary.bg": "#166A3E", # emerald
            "btn.secondary.fg": "#E9F7F0",
            "btn.secondary.border": "#CFAF63",
            "btn.secondary.hoverBg": "#125C35",
            "btn.secondary.activeBg": "#0F4F2D",
            # Pot badge (brown-black + gold ring)
            "pot.badgeBg": "#1E1912",
            "pot.badgeRing": "#E4C97D",
            "pot.valueText": "#FFF4D9",
            # Tab/list accents (gold line + tiny emerald dot)
            "a11y.focus": "#F0D489",
            "divider": "#2C2418",
            "grid.lines": "#231C12",
        }

        # Enhanced chip and seat tokens for all painter themes
        PAINTER_CHIP_SEAT_TOKENS = {
            # Player seats (luxury pods)
            "seat.bg.idle": "#1E293B",
            "seat.bg.active": "#334155", 
            "seat.ring": "#475569",
            "seat.accent": "#64748B",
            "seat.highlight": "#475569",
            "seat.shadow": "#0F172A",
            "seat.cornerAccent": "#C8D5DE",
            
            # Chip colors (will be overridden per theme)
            "chip.luxury.bg": "#2D1B69",
            "chip.luxury.ring": "#FFD700",
            "chip.luxury.accent": "#E6E6FA",
            "chip.high.bg": "#8B0000",
            "chip.high.ring": "#FFD700", 
            "chip.high.accent": "#FFFFFF",
            "chip.medium.bg": "#006400",
            "chip.medium.ring": "#FFFFFF",
            "chip.medium.accent": "#90EE90",
            "chip.low.bg": "#4169E1",
            "chip.low.ring": "#FFFFFF",
            "chip.low.accent": "#ADD8E6",
            "chip.minimal.bg": "#FFFFFF",
            "chip.minimal.ring": "#000000",
            "chip.minimal.accent": "#D3D3D3",
            "chip.call.bg": "#6B7280",
            "chip.call.ring": "#9CA3AF",
            "chip.pattern": "#FFD700",
            "chip.text": "#FFFFFF",
            
            # Winner badge
            "winner.bg": "#1F2937",
            "winner.border": "#FFD700",
            "winner.accent": "#FEF3C7",
            "winner.text": "#FFFFFF",
            "winner.amount": "#FFD700",
            "winner.description": "#D1D5DB",
            "celebration.color": "#FFD700",
        }
        
        # Add chip and seat tokens to all painter themes
        MONET_NOIR.update(PAINTER_CHIP_SEAT_TOKENS)
        CARAVAGGIO_NOIR.update(PAINTER_CHIP_SEAT_TOKENS)
        KLIMT_ROYALE.update(PAINTER_CHIP_SEAT_TOKENS)
        WHISTLER_NOCTURNE.update(PAINTER_CHIP_SEAT_TOKENS)
        
        # Theme-specific chip color overrides
        MONET_CHIP_OVERRIDES = {
            "chip.luxury.bg": "#0E7A6F",     # Teal luxury chips
            "chip.luxury.ring": "#D7E2E8",   # Silver rings
            "chip.high.bg": "#1E40AF",       # Blue high value
            "chip.medium.bg": "#065F46",     # Dark teal medium
            "chip.pattern": "#C8D5DE",       # Silver pattern
        }
        
        CARAVAGGIO_CHIP_OVERRIDES = {
            "chip.luxury.bg": "#B3122E",     # Crimson luxury chips
            "chip.luxury.ring": "#E1C16E",   # Gold rings
            "chip.high.bg": "#8B0000",       # Dark red high value
            "chip.medium.bg": "#2A1416",     # Dark burgundy medium
            "chip.pattern": "#E1C16E",       # Gold pattern
        }
        
        KLIMT_CHIP_OVERRIDES = {
            "chip.luxury.bg": "#F4C430",     # Gold luxury chips
            "chip.luxury.ring": "#E4C97D",   # Light gold rings
            "chip.high.bg": "#166A3E",       # Emerald high value
            "chip.medium.bg": "#17130E",     # Obsidian medium
            "chip.pattern": "#E4C97D",       # Gold pattern
        }
        
        # Apply V2 overrides to enhance theme differentiation
        MONET_NOIR.update(MONET_NOIR_V2_OVERRIDES)
        MONET_NOIR.update(MONET_CHIP_OVERRIDES)
        
        CARAVAGGIO_NOIR.update(CARAVAGGIO_NOIR_V2_OVERRIDES)
        CARAVAGGIO_NOIR.update(CARAVAGGIO_CHIP_OVERRIDES)
        
        KLIMT_ROYALE.update(KLIMT_ROYALE_V2_OVERRIDES)
        KLIMT_ROYALE.update(KLIMT_CHIP_OVERRIDES)

        # --- Riviera Pastel (light / playful Monte Carlo) ---
        VELOUR_CRIMSON = {
            # Darker, seductive danger - differentiated from Velvet Burgundy
            "table.felt": "#6E0B14",   # deep crimson (darker, more dangerous)
            "table.rail": "#3B0A0F",   # black cherry rails
            "table.inlay": "#A41E34",  # garnet red trim
            "table.edgeGlow": "#5C1118",  # deeper crimson gradient
            "panel.bg": "#3B0A0F", "panel.border": "#5C1118", "panel.shadow": "#00000080",
            # Core text - antique ivory with crimson shadow
            "text.primary": "#F5E2C8", "text.secondary": "#E6D1B3", "text.muted": "#C7B299",
            # Pot - deep crimson with garnet accents
            "pot.badgeBg": "#3B0A0F", "pot.badgeRing": "#A41E34", "pot.valueText": "#F5E2C8",
            "sidePot.badgeBg": "#5C1118", "sidePot.badgeFg": "#F5E2C8",
            # Buttons - dangerous crimson with garnet accents
            "btn.primary.bg": "#5C1118", "btn.primary.fg": "#F5E2C8", "btn.primary.border": "#A41E34",
            "btn.primary.hoverBg": "#6E0B14", "btn.primary.hoverFg": "#F8E6D0", "btn.primary.hoverBorder": "#B8253F",
            "btn.primary.activeBg": "#7A1520", "btn.primary.activeFg": "#FBEBD8", "btn.primary.activeBorder": "#CC2C4A",
            "btn.primary.disabledBg": "#3B0A0F", "btn.primary.disabledFg": "#A08B7A", "btn.primary.disabledBorder": "#5C1118",
            
            "btn.secondary.bg": "#6E0B14", "btn.secondary.fg": "#E6D1B3", "btn.secondary.border": "#A41E34",
            "btn.secondary.hoverBg": "#7A1520", "btn.secondary.hoverFg": "#F0DCC0", "btn.secondary.hoverBorder": "#B8253F",
            "btn.secondary.activeBg": "#861F2C", "btn.secondary.activeFg": "#F5E2C8", "btn.secondary.activeBorder": "#CC2C4A",
            "btn.secondary.disabledBg": "#5C1118", "btn.secondary.disabledFg": "#A08B7A", "btn.secondary.disabledBorder": "#6E0B14",

            "btn.danger.bg": "#8A1A28", "btn.danger.fg": "#F5E2C8", "btn.danger.border": "#CC2C4A",
            "btn.danger.hoverBg": "#9E2030", "btn.danger.hoverFg": "#F8E6D0", "btn.danger.hoverBorder": "#E03555",
            "btn.danger.activeBg": "#B22638", "btn.danger.activeFg": "#FBEBD8", "btn.danger.activeBorder": "#F43F60",
            "btn.danger.disabledBg": "#5C1118", "btn.danger.disabledFg": "#A08B7A", "btn.danger.disabledBorder": "#6E0B14",

            # Actions / Chips - dangerous crimson themed
            "action.fold": "#A08B7A", "action.check": "#B8A090", "action.call": "#A41E34",
            "action.bet": "#CC2C4A", "action.raise": "#E03555", "action.allin": "#F43F60",
            "chip.primary": "#A41E34", "chip.secondary": "#A08B7A", "chip.tertiary": "#B8A090",
            "chip.quaternary": "#C7B299", "chip.high": "#CC2C4A",

            # Board - deep crimson tones
            "board.slotBg": "#2A0A0A", "board.cardFaceFg": "#FFDDDD", "board.cardBack": "#4B1E1E", "board.border": "#3D0C0C",

            # A11y / lines / fonts
            "a11y.focus": "#FF4444", "divider": "#5A2525", "grid.lines": "#4B1E1E",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#2A0A0A", "secondary_bg": "#4B1E1E", "text_gold": "#B22222", "border_active": "#B22222",
            "panel.fg": "#FFDDDD", "dealer.buttonBg": "#FFDDDD", "dealer.buttonFg": "#3D0C0C", "dealer.buttonBorder": "#B22222",
            "seat.bg.idle": "#4B1E1E", "seat.bg.active": "#2A0A0A", "seat.bg.acting": "#5A2525",
            "player.name": "#FFB8B8", "player.stack": "#B22222", "table.railHighlight": "#B22222", "table.center": "#660000",
        }

        # --- Deco Luxe (Art-Deco champagne + emerald on black) ---
        DECO_LUXE = {
            # Surfaces (dark, geometric-ready)
            "table.felt": "#0E0F11", "table.rail": "#0A0A0B", "table.inlay": "#D6C08F", "table.edgeGlow": "#1A1712",
            "panel.bg": "#0E0E0F",   "panel.border": "#211E19", "panel.shadow": "#00000099",
            # Core text
            "text.primary": "#F8F4EA", "text.secondary": "#D7CFBD", "text.muted": "#9B9486",
            # Pot (champagne ring)
            "pot.badgeBg": "#141315", "pot.badgeRing": "#D6C08F", "pot.valueText": "#FFF9EE",
            "sidePot.badgeBg": "#19181A", "sidePot.badgeFg": "#F2E9D7",

            # Buttons (champagne primary, emerald secondary, ruby danger)
            "btn.primary.bg": "#E1C78E", "btn.primary.fg": "#1A1410", "btn.primary.border": "#F0DDAF",
            "btn.primary.hoverBg": "#D7BC82", "btn.primary.activeBg": "#CFAF73",
            "btn.primary.hoverFg": "#120E0B", "btn.primary.activeFg": "#0E0B09",
            "btn.primary.hoverBorder": "#FAE9BE", "btn.primary.activeBorder": "#FFF0CB",

            "btn.secondary.bg": "#1A3E34", "btn.secondary.fg": "#EAF6F0", "btn.secondary.border": "#E1C78E",
            "btn.secondary.hoverBg": "#174133", "btn.secondary.activeBg": "#13382C",
            "btn.secondary.hoverFg": "#F8FFFB", "btn.secondary.activeFg": "#FFFFFF",
            "btn.secondary.hoverBorder": "#F0DDAF", "btn.secondary.activeBorder": "#FAE9BE",

            "btn.danger.bg": "#5B1922", "btn.danger.fg": "#FFEFEF", "btn.danger.border": "#E5A3AC",
            "btn.danger.hoverBg": "#6A1E28", "btn.danger.activeBg": "#77212C",
            "btn.danger.hoverFg": "#FFF7F8", "btn.danger.activeFg": "#FFFFFF",
            "btn.danger.hoverBorder": "#F2B8C0", "btn.danger.activeBorder": "#FFD3D8",

            # Actions / Chips
            "action.fold": "#6E6A6A", "action.check": "#9AD6C1", "action.call": "#2AA37A",
            "action.bet": "#E1C78E", "action.raise": "#B96C7B", "action.allin": "#D06B76",
            "chip.primary": "#E1C78E", "chip.secondary": "#A6A59F", "chip.tertiary": "#78C2A4",
            "chip.quaternary": "#6EA3D6", "chip.high": "#C96C80",

            # Board
            "board.slotBg": "#111214", "board.cardFaceFg": "#0F1012", "board.cardBack": "#131416", "board.border": "#0C0C0D",

            # A11y / lines / fonts
            "a11y.focus": "#F0DDAF", "divider": "#29251E", "grid.lines": "#1C1915",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
        }

        # Map existing themes to new names for THEME_ORDER compatibility
        # We'll create placeholder themes for missing ones
        FOREST_GREEN_PRO = EMERALD_NOIR  # Rename for consistency
        VELVET_BURGUNDY = CRIMSON_GOLD   # Use existing burgundy-like theme
        OBSIDIAN_GOLD = {
            # Minimalist, vault-like, elite - differentiated from Klimt Royale
            "table.felt": "#0A0A0A",   # obsidian black (minimalist)
            "table.rail": "#2C2C2C",   # dark iron rails
            "table.inlay": "#D4AF37",  # polished gold trim
            "table.edgeGlow": "#1A1A1A",  # subtle depth gradient
            "panel.bg": "#1A1A1A", "panel.border": "#2C2C2C", "panel.shadow": "#00000080",
            "text.primary": "#E6E6E6", "text.secondary": "#D0D0D0", "text.muted": "#B0B0B0",
            "pot.badgeBg": "#1A1A1A", "pot.badgeRing": "#D4AF37", "pot.valueText": "#E6E6E6",
            "sidePot.badgeBg": "#2C2C2C", "sidePot.badgeFg": "#E6E6E6",
            # Buttons: minimalist obsidian with polished gold accents
            "btn.primary.bg": "#2C2C2C", "btn.primary.fg": "#E6E6E6", "btn.primary.border": "#D4AF37",
            "btn.primary.hoverBg": "#3A3A3A", "btn.primary.hoverFg": "#F0F0F0", "btn.primary.hoverBorder": "#E6C878",
            "btn.primary.activeBg": "#484848", "btn.primary.activeFg": "#FFFFFF", "btn.primary.activeBorder": "#F0D98A",
            "btn.primary.disabledBg": "#1A1A1A", "btn.primary.disabledFg": "#808080", "btn.primary.disabledBorder": "#2C2C2C",
            "btn.secondary.bg": "#3A3A3A", "btn.secondary.fg": "#E0E0C0", "btn.secondary.border": "#DAA520",
            "btn.secondary.hoverBg": "#464646", "btn.secondary.hoverFg": "#F0F0D0", "btn.secondary.hoverBorder": "#E6B800",
            "btn.secondary.activeBg": "#525252", "btn.secondary.activeFg": "#FFFEF0", "btn.secondary.activeBorder": "#F2C500",
            "btn.secondary.disabledBg": "#2E2E2E", "btn.secondary.disabledFg": "#808070", "btn.secondary.disabledBorder": "#3A3A3A",
            "btn.danger.bg": "#4A1A1A", "btn.danger.fg": "#FFE4E1", "btn.danger.border": "#CD5C5C",
            "btn.danger.hoverBg": "#5A2525", "btn.danger.hoverFg": "#FFF0F0", "btn.danger.hoverBorder": "#DC7373",
            "btn.danger.activeBg": "#6A3030", "btn.danger.activeFg": "#FFFFFF", "btn.danger.activeBorder": "#EB8A8A",
            "btn.danger.disabledBg": "#2E2E2E", "btn.danger.disabledFg": "#808070", "btn.danger.disabledBorder": "#3A3A3A",
            "action.fold": "#808070", "action.check": "#90C090", "action.call": "#70A070",
            "action.bet": "#DAA520", "action.raise": "#E6B800", "action.allin": "#F2C500",
            "chip.primary": "#DAA520", "chip.secondary": "#B8B8A0", "chip.tertiary": "#90C090",
            "chip.quaternary": "#8090B0", "chip.high": "#E6B800",
            "board.slotBg": "#1A1A1A", "board.cardFaceFg": "#F5F5DC", "board.cardBack": "#2E2E2E", "board.border": "#0C0C0C",
            "a11y.focus": "#FFD700", "divider": "#3A3A3A", "grid.lines": "#2E2E2E",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#1A1A1A", "secondary_bg": "#2E2E2E", "text_gold": "#DAA520", "border_active": "#DAA520",
            "panel.fg": "#F5F5DC", "dealer.buttonBg": "#F5F5DC", "dealer.buttonFg": "#0C0C0C", "dealer.buttonBorder": "#DAA520",
            "seat.bg.idle": "#2E2E2E", "seat.bg.active": "#1A1A1A", "seat.bg.acting": "#3A3A3A",
            "player.name": "#E0E0C0", "player.stack": "#DAA520", "table.railHighlight": "#DAA520", "table.center": "#1A1A1A",
        }
        IMPERIAL_JADE = {**EMERALD_NOIR, "table.felt": "#2E5D4A"}  # Jade variant
        SUNSET_MIRAGE = {**CRIMSON_GOLD, "table.felt": "#FF6B35", "panel.bg": "#2A1810"}  # Orange sunset
        OCEANIC_BLUE = {
            # Rich sapphire ocean with turquoise accents
            "table.felt": "#0F2A44",   # deep sapphire blue, not pale
            "table.rail": "#0A1B2E",   # darker navy rail
            "table.inlay": "#4682B4",  # steel blue trim with sapphire undertone
            "table.edgeGlow": "#1C3A5F",
            "panel.bg": "#132B42", "panel.border": "#1E3A5F", "panel.shadow": "#00000080",
            "text.primary": "#E6F3FF", "text.secondary": "#B8D4F0", "text.muted": "#7BA3C7",
            "pot.badgeBg": "#1A3550", "pot.badgeRing": "#4682B4", "pot.valueText": "#E6F3FF",
            "sidePot.badgeBg": "#1F3D58", "sidePot.badgeFg": "#D0E7FF",
            # Buttons: ocean depth with sapphire accents
            "btn.primary.bg": "#1E4A6B", "btn.primary.fg": "#E6F3FF", "btn.primary.border": "#4682B4",
            "btn.primary.hoverBg": "#2A5A7F", "btn.primary.hoverFg": "#F0F8FF", "btn.primary.hoverBorder": "#5B9BD5",
            "btn.primary.activeBg": "#366B93", "btn.primary.activeFg": "#FFFFFF", "btn.primary.activeBorder": "#70B4E6",
            "btn.primary.disabledBg": "#1A2F42", "btn.primary.disabledFg": "#7BA3C7", "btn.primary.disabledBorder": "#2A4A65",
            "btn.secondary.bg": "#2A4A65", "btn.secondary.fg": "#D0E7FF", "btn.secondary.border": "#4682B4",
            "btn.secondary.hoverBg": "#355A7A", "btn.secondary.hoverFg": "#E0F0FF", "btn.secondary.hoverBorder": "#5B9BD5",
            "btn.secondary.activeBg": "#406B8F", "btn.secondary.activeFg": "#F0F8FF", "btn.secondary.activeBorder": "#70B4E6",
            "btn.secondary.disabledBg": "#1F3A55", "btn.secondary.disabledFg": "#7BA3C7", "btn.secondary.disabledBorder": "#2A4A65",
            "btn.danger.bg": "#4A1E2A", "btn.danger.fg": "#FFE4E1", "btn.danger.border": "#CD5C5C",
            "btn.danger.hoverBg": "#5A2A35", "btn.danger.hoverFg": "#FFF0F0", "btn.danger.hoverBorder": "#DC7373",
            "btn.danger.activeBg": "#6A3540", "btn.danger.activeFg": "#FFFFFF", "btn.danger.activeBorder": "#EB8A8A",
            "btn.danger.disabledBg": "#2A1F25", "btn.danger.disabledFg": "#7BA3C7", "btn.danger.disabledBorder": "#3A2F35",
            "action.fold": "#7BA3C7", "action.check": "#20B2AA", "action.call": "#4682B4",
            "action.bet": "#5B9BD5", "action.raise": "#4169E1", "action.allin": "#0000CD",
            "chip.primary": "#4682B4", "chip.secondary": "#7BA3C7", "chip.tertiary": "#20B2AA",
            "chip.quaternary": "#5B9BD5", "chip.high": "#4169E1",
            "board.slotBg": "#1A3550", "board.cardFaceFg": "#E6F3FF", "board.cardBack": "#1F3D58", "board.border": "#0F2A44",
            "a11y.focus": "#5B9BD5", "divider": "#1E3A5F", "grid.lines": "#1A3550",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#132B42", "secondary_bg": "#1E3A5F", "text_gold": "#4682B4", "border_active": "#4682B4",
            "panel.fg": "#E6F3FF", "dealer.buttonBg": "#E6F3FF", "dealer.buttonFg": "#0F2A44", "dealer.buttonBorder": "#4682B4",
            "seat.bg.idle": "#0A1B2E", "seat.bg.active": "#1A3550", "seat.bg.acting": "#1E4A6B",
            "player.name": "#B8D4F0", "player.stack": "#4682B4", "table.railHighlight": "#4682B4", "table.center": "#1C3A5F",
        }
        GOLDEN_DUSK = {
            # Cognac lounge refinement - differentiated from Sunset Mirage
            "table.felt": "#A3622B",   # burnished amber
            "table.rail": "#5C3A21",   # cognac leather rails
            "table.inlay": "#C18F65",  # brass glow trim
            "table.edgeGlow": "#8B5A3C",  # warm amber gradient
            "panel.bg": "#5C3A21", "panel.border": "#8B5A3C", "panel.shadow": "#00000080",
            # Core text - soft linen with cognac shadow
            "text.primary": "#F3E3D3", "text.secondary": "#E6D1B8", "text.muted": "#D4BF9E",
            # Pot - cognac with brass accents
            "pot.badgeBg": "#5C3A21", "pot.badgeRing": "#C18F65", "pot.valueText": "#F3E3D3",
            "sidePot.badgeBg": "#8B5A3C", "sidePot.badgeFg": "#F3E3D3",
            # Buttons: cognac leather with brass accents
            "btn.primary.bg": "#8B5A3C", "btn.primary.fg": "#F3E3D3", "btn.primary.border": "#C18F65",
            "btn.primary.hoverBg": "#A3622B", "btn.primary.hoverFg": "#F6E6D6", "btn.primary.hoverBorder": "#D4A373",
            "btn.primary.activeBg": "#BB6A33", "btn.primary.activeFg": "#F9E9D9", "btn.primary.activeBorder": "#E7B781",
            "btn.primary.disabledBg": "#5C3A21", "btn.primary.disabledFg": "#B8A890", "btn.primary.disabledBorder": "#8B5A3C",
            
            "btn.secondary.bg": "#A3622B", "btn.secondary.fg": "#E6D1B8", "btn.secondary.border": "#C18F65",
            "btn.secondary.hoverBg": "#BB6A33", "btn.secondary.hoverFg": "#F0DCC5", "btn.secondary.hoverBorder": "#D4A373",
            "btn.secondary.activeBg": "#D3723B", "btn.secondary.activeFg": "#F3E3D3", "btn.secondary.activeBorder": "#E7B781",
            "btn.secondary.disabledBg": "#8B5A3C", "btn.secondary.disabledFg": "#B8A890", "btn.secondary.disabledBorder": "#A3622B",

            "btn.danger.bg": "#A85A3A", "btn.danger.fg": "#F3E3D3", "btn.danger.border": "#D4734A",
            "btn.danger.hoverBg": "#C06242", "btn.danger.hoverFg": "#F6E6D6", "btn.danger.hoverBorder": "#E8855A",
            "btn.danger.activeBg": "#D86A4A", "btn.danger.activeFg": "#F9E9D9", "btn.danger.activeBorder": "#FC976A",
            "btn.danger.disabledBg": "#8B5A3C", "btn.danger.disabledFg": "#B8A890", "btn.danger.disabledBorder": "#A3622B",

            # Actions / Chips - cognac themed
            "action.fold": "#B8A890", "action.check": "#C8B8A0", "action.call": "#C18F65",
            "action.bet": "#D4A373", "action.raise": "#E7B781", "action.allin": "#FACB8F",
            "chip.primary": "#C18F65", "chip.secondary": "#B8A890", "chip.tertiary": "#C8B8A0",
            "chip.quaternary": "#D4BF9E", "chip.high": "#D4A373",

            # Board - warm cognac tones
            "board.slotBg": "#5C3A21", "board.cardFaceFg": "#F3E3D3", "board.cardBack": "#8B5A3C", "board.border": "#A3622B",

            # A11y / lines / fonts
            "a11y.focus": "#D4A373", "divider": "#8B5A3C", "grid.lines": "#A3622B",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#5C3A21", "secondary_bg": "#8B5A3C", "text_gold": "#C18F65", "border_active": "#C18F65",
            "panel.fg": "#F3E3D3", "dealer.buttonBg": "#F3E3D3", "dealer.buttonFg": "#5C3A21", "dealer.buttonBorder": "#C18F65",
            "seat.bg.idle": "#8B5A3C", "seat.bg.active": "#5C3A21", "seat.bg.acting": "#A3622B",
            "player.name": "#E6D1B8", "player.stack": "#C18F65", "table.railHighlight": "#C18F65", "table.center": "#8B5A3C",
        }
        CYBER_NEON = {
            # Deep cyberpunk base with controlled neon accents
            "table.felt": "#0A0A0F",   # near-black base for neon contrast
            "table.rail": "#050508",   # deeper black rail
            "table.inlay": "#00E6E6",  # toned-down cyan, not pure white-bright
            "table.edgeGlow": "#001A1A",
            "panel.bg": "#0D0D12", "panel.border": "#1A1A22", "panel.shadow": "#00000080",
            "text.primary": "#E0F8FF", "text.secondary": "#B0E0E6", "text.muted": "#708090",
            "pot.badgeBg": "#0F0F18", "pot.badgeRing": "#00E6E6", "pot.valueText": "#E0F8FF",
            "sidePot.badgeBg": "#12121A", "sidePot.badgeFg": "#B0E0E6",
            # Buttons: cyberpunk neon with controlled brightness
            "btn.primary.bg": "#001A1A", "btn.primary.fg": "#E0F8FF", "btn.primary.border": "#00E6E6",
            "btn.primary.hoverBg": "#002626", "btn.primary.hoverFg": "#F0FFFF", "btn.primary.hoverBorder": "#00FFFF",
            "btn.primary.activeBg": "#003333", "btn.primary.activeFg": "#FFFFFF", "btn.primary.activeBorder": "#33FFFF",
            "btn.primary.disabledBg": "#0F0F12", "btn.primary.disabledFg": "#708090", "btn.primary.disabledBorder": "#1A1A1F",
            "btn.secondary.bg": "#1A0A1A", "btn.secondary.fg": "#FFB6C1", "btn.secondary.border": "#FF1493",
            "btn.secondary.hoverBg": "#260F26", "btn.secondary.hoverFg": "#FFC0CB", "btn.secondary.hoverBorder": "#FF69B4",
            "btn.secondary.activeBg": "#331533", "btn.secondary.activeFg": "#FFCCCB", "btn.secondary.activeBorder": "#FF91A4",
            "btn.secondary.disabledBg": "#12101A", "btn.secondary.disabledFg": "#708090", "btn.secondary.disabledBorder": "#1F1A22",
            "btn.danger.bg": "#2A0A0A", "btn.danger.fg": "#FFE4E1", "btn.danger.border": "#FF4500",
            "btn.danger.hoverBg": "#330F0F", "btn.danger.hoverFg": "#FFF0F0", "btn.danger.hoverBorder": "#FF6347",
            "btn.danger.activeBg": "#401515", "btn.danger.activeFg": "#FFFFFF", "btn.danger.activeBorder": "#FF7F50",
            "btn.danger.disabledBg": "#1A1012", "btn.danger.disabledFg": "#708090", "btn.danger.disabledBorder": "#221A1F",
            "action.fold": "#708090", "action.check": "#00E6E6", "action.call": "#32CD32",
            "action.bet": "#FF1493", "action.raise": "#FF4500", "action.allin": "#FF0000",
            "chip.primary": "#00E6E6", "chip.secondary": "#708090", "chip.tertiary": "#32CD32",
            "chip.quaternary": "#FF1493", "chip.high": "#FF4500",
            "board.slotBg": "#0A0A0F", "board.cardFaceFg": "#E0F8FF", "board.cardBack": "#0F0F18", "board.border": "#001A1A",
            "a11y.focus": "#00FFFF", "divider": "#1A1A22", "grid.lines": "#0F0F18",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#0D0D12", "secondary_bg": "#1A1A22", "text_gold": "#00E6E6", "border_active": "#00E6E6",
            "panel.fg": "#E0F8FF", "dealer.buttonBg": "#E0F8FF", "dealer.buttonFg": "#0A0A0F", "dealer.buttonBorder": "#00E6E6",
            "seat.bg.idle": "#050508", "seat.bg.active": "#0F0F18", "seat.bg.acting": "#001A1A",
            "player.name": "#B0E0E6", "player.stack": "#00E6E6", "table.railHighlight": "#00E6E6", "table.center": "#0A0A0F",
        }
        STEALTH_GRAPHITE = {
            # Refined graphite with gunmetal accents for better contrast
            "table.felt": "#2A2A2A",   # refined charcoal, not flat grey
            "table.rail": "#1A1A1A",   # deeper black rail
            "table.inlay": "#708090",  # gunmetal trim for definition
            "table.edgeGlow": "#3A3A3A",
            "panel.bg": "#1E1E1E", "panel.border": "#2A2A2A", "panel.shadow": "#00000080",
            "text.primary": "#E8E8E8", "text.secondary": "#C0C0C0", "text.muted": "#808080",
            "pot.badgeBg": "#2A2A2A", "pot.badgeRing": "#708090", "pot.valueText": "#E8E8E8",
            "sidePot.badgeBg": "#323232", "sidePot.badgeFg": "#D0D0D0",
            # Buttons: stealth with subtle gunmetal accents
            "btn.primary.bg": "#3A3A3A", "btn.primary.fg": "#E8E8E8", "btn.primary.border": "#708090",
            "btn.primary.hoverBg": "#4A4A4A", "btn.primary.hoverFg": "#F0F0F0", "btn.primary.hoverBorder": "#8090A0",
            "btn.primary.activeBg": "#5A5A5A", "btn.primary.activeFg": "#FFFFFF", "btn.primary.activeBorder": "#90A0B0",
            "btn.primary.disabledBg": "#2A2A2A", "btn.primary.disabledFg": "#808080", "btn.primary.disabledBorder": "#3A3A3A",
            "btn.secondary.bg": "#404040", "btn.secondary.fg": "#D0D0D0", "btn.secondary.border": "#708090",
            "btn.secondary.hoverBg": "#505050", "btn.secondary.hoverFg": "#E0E0E0", "btn.secondary.hoverBorder": "#8090A0",
            "btn.secondary.activeBg": "#606060", "btn.secondary.activeFg": "#F0F0F0", "btn.secondary.activeBorder": "#90A0B0",
            "btn.secondary.disabledBg": "#323232", "btn.secondary.disabledFg": "#808080", "btn.secondary.disabledBorder": "#404040",
            "btn.danger.bg": "#4A2A2A", "btn.danger.fg": "#FFE4E1", "btn.danger.border": "#CD5C5C",
            "btn.danger.hoverBg": "#5A3535", "btn.danger.hoverFg": "#FFF0F0", "btn.danger.hoverBorder": "#DC7373",
            "btn.danger.activeBg": "#6A4040", "btn.danger.activeFg": "#FFFFFF", "btn.danger.activeBorder": "#EB8A8A",
            "btn.danger.disabledBg": "#2A2A2A", "btn.danger.disabledFg": "#808080", "btn.danger.disabledBorder": "#3A3A3A",
            "action.fold": "#808080", "action.check": "#90EE90", "action.call": "#87CEEB",
            "action.bet": "#DDA0DD", "action.raise": "#F0E68C", "action.allin": "#FF6347",
            "chip.primary": "#708090", "chip.secondary": "#808080", "chip.tertiary": "#90EE90",
            "chip.quaternary": "#87CEEB", "chip.high": "#DDA0DD",
            "board.slotBg": "#2A2A2A", "board.cardFaceFg": "#E8E8E8", "board.cardBack": "#323232", "board.border": "#1A1A1A",
            "a11y.focus": "#8090A0", "divider": "#3A3A3A", "grid.lines": "#2A2A2A",
            "font.display": ("Inter", 28, "bold"), "font.h1": ("Inter", 20, "semibold"),
            "font.h2": ("Inter", 16, "semibold"), "font.body": ("Inter", 13, "normal"), "font.mono": ("JetBrains Mono", 12, "normal"),
            # Compatibility tokens
            "primary_bg": "#1E1E1E", "secondary_bg": "#2A2A2A", "text_gold": "#708090", "border_active": "#708090",
            "panel.fg": "#E8E8E8", "dealer.buttonBg": "#E8E8E8", "dealer.buttonFg": "#2A2A2A", "dealer.buttonBorder": "#708090",
            "seat.bg.idle": "#1A1A1A", "seat.bg.active": "#2A2A2A", "seat.bg.acting": "#3A3A3A",
            "player.name": "#C0C0C0", "player.stack": "#708090", "table.railHighlight": "#708090", "table.center": "#3A3A3A",
        }
        ROYAL_SAPPHIRE = ROYAL_CASINO_SAPPHIRE  # Use existing sapphire
        MIDNIGHT_AURORA = {**EMERALD_NOIR, "table.felt": "#191970", "panel.bg": "#0F0F23"}  # Midnight blue

        return {
            # Row 1 – Classic Casino (following THEME_ORDER)
            "Forest Green Professional": FOREST_GREEN_PRO,
            "Velvet Burgundy": VELVET_BURGUNDY,
            "Obsidian Gold": OBSIDIAN_GOLD,
            "Imperial Jade": IMPERIAL_JADE,
            # Row 2 – Luxury Noir (Art-inspired)
            "Monet Noir": MONET_NOIR,
            "Caravaggio Noir": CARAVAGGIO_NOIR,
            "Klimt Royale": KLIMT_ROYALE,
            "Deco Luxe": DECO_LUXE,
            # Row 3 – Nature & Light
            "Sunset Mirage": SUNSET_MIRAGE,
            "Oceanic Blue": OCEANIC_BLUE,
            "Velour Crimson": VELOUR_CRIMSON,
            "Golden Dusk": GOLDEN_DUSK,
            # Row 4 – Modern / Bold
            "Cyber Neon": CYBER_NEON,
            "Stealth Graphite": STEALTH_GRAPHITE,
            "Royal Sapphire": ROYAL_SAPPHIRE,
            "Midnight Aurora": MIDNIGHT_AURORA,
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names in THEME_ORDER."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback to original method
        return [name for name in THEME_ORDER if name in self._themes]
    
    def register_in_order(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register themes following THEME_ORDER; silently skip names missing from packs."""
        for name in THEME_ORDER:
            if name in packs:
                self.register(name, packs[name])
    
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
                theme_config = loader.get_theme_by_id(self._current or "forest-green-pro")
                return theme_config.get("palette", {})
            except Exception:
                pass
            
            # Fallback to legacy system
            if self._current in THEME_BASES:
                return dict(THEME_BASES[self._current])
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID
            return self._current.lower().replace(" ", "-")
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

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub


