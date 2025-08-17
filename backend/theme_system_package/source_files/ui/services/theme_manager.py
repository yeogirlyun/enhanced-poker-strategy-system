from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os


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
            # Prefer Emerald Noir as default
            if "Emerald Noir" in self._themes:
                self._current = "Emerald Noir"
                self._theme = dict(self._themes["Emerald Noir"])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
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
        
        CARBON_FIBER_ELITE = {
            # Table Scheme 3: Carbon Fiber Elite (#1C1C1C)
            "table.felt": "#1C1C1C",  # Carbon fiber black
            "table.rail": "#2F2F2F",  # Dark gray rail
            "table.railHighlight": "#4A4A4A",  # Light gray accents
            "table.edgeGlow": "#4A4A4A",  # Gray border
            "table.inlay": "#333333",  # Subtle inlay
            "table.center": "#252525",  # Center highlight
            "primary_bg": "#0A0A0A",  # Pure black
            "secondary_bg": "#1A1A1A",  # Dark gray
            "text_gold": "#00BFFF",  # Bright tech blue
            "border_active": "#00BFFF",
            # Left Column UI Panel Colors
            "panel.bg": "#141414",  # Dark carbon background
            "panel.fg": "#E0E0E0",  # Light gray text
            "panel.sectionTitle": "#00BFFF",  # Tech blue section titles
            "panel.border": "#4A4A4A",  # Gray border
            "btn.primaryBg": "#1565C0",  # Blue primary button (Load)
            "btn.primaryFg": "#F5F5F5",  # Light primary text
            "btn.secondaryBg": "#2A2A2A",  # Dark gray secondary buttons
            "btn.secondaryFg": "#E0E0E0",  # Light secondary text
            "a11y.focusRing": "#00BFFF",  # Tech blue focus ring
            # Enhanced Button State Colors
            "btn.default.bg": "#1565C0",  # Blue default button
            "btn.default.fg": "#F5F5F5",  # Light gray text
            "btn.hover.bg": "#1976D2",   # Lighter blue hover
            "btn.hover.fg": "#F5F5F5",   # Light gray text
            "btn.active.bg": "#1565C0",  # Darker blue active
            "btn.active.fg": "#00BFFF",  # Tech blue active text
            "btn.disabled.bg": "#2A2A2A", # Dark gray disabled
            "btn.disabled.fg": "#757575", # Medium gray text
            "board.slotBg": "#333333",
            "board.cardFaceFg": "#FFFFFF",
            "board.cardBack": "#404040",
            "board.border": "#4A4A4A",
            "pot.valueText": "#00BFFF",
            "chip_gold": "#00BFFF",
            "seat.bg.idle": "#2A2A2A",
            "seat.bg.active": "#3A3A3A",
            "seat.bg.acting": "#00BFFF",
            "player.name": "#E0E0E0",
            "player.stack": "#00BFFF",
            "dealer.buttonBg": "#00BFFF",
            "dealer.buttonFg": "#0A0A0A",
            "dealer.buttonBorder": "#0080CC",
            "pot.bg": "#333333",
            "pot.border": "#4A4A4A",
            "pot.label": "#00BFFF",
            "bet.bg": "#333333",
            "bet.border": "#4A4A4A",
            "bet.text": "#00BFFF",
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

        return {
            # Luxury LV Noir Collection
            "LV Noir": LV_NOIR,
            "Crimson Monogram": CRIMSON_MONOGRAM,
            "Obsidian Emerald": OBSIDIAN_EMERALD,
            # Original 3 themes
            "Emerald Noir": EMERALD_NOIR,
            "Royal Indigo": ROYAL_INDIGO,  
            "Crimson Gold": CRIMSON_GOLD,
            # 5 Professional Casino Table Schemes
            "PokerStars Classic Pro": POKERSTARS_CLASSIC_PRO,
            "WSOP Championship": WSOP_CHAMPIONSHIP,
            "Carbon Fiber Elite": CARBON_FIBER_ELITE,
            "Royal Casino Sapphire": ROYAL_CASINO_SAPPHIRE,
            "Emerald Professional": EMERALD_PROFESSIONAL,
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
        return list(self._themes.keys())

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

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub


