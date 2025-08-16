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
            "table.felt": "#1E5B44",
            "table.rail": "#3B2F2F",
            "table.edgeGlow": "#0B2F24",
            "table.inlay": "#C6A664",
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
            "seat.shadow": "#00000080",
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
            # Button states for Emerald Casino theme
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#E0E0E0",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#2D5A3D",
            "btn.hover.fg": "#FFD700",
            "btn.hover.shadow": "#2D5A3D66",
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
            "hud.shadow": "#00000080",
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
            "seat.shadow": "#00000088",
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
            # Button states for Midnight Blue theme  
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#D9D9D9",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#1D3557",
            "btn.hover.fg": "#D9D9D9",
            "btn.hover.shadow": "#1D355766",
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
            "hud.shadow": "#00000080",
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
            "seat.shadow": "#00000099",
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
            # Button states for Burgundy Royale theme
            "btn.default.bg": "#1E1E1E",
            "btn.default.fg": "#E0E0E0",
            "btn.default.border": "#A0A0A0",
            "btn.hover.bg": "#7A1C1C",
            "btn.hover.fg": "#E6C76E",
            "btn.hover.shadow": "#7A1C1C66",
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
            "hud.shadow": "#00000080",
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
        return {
            "Emerald Noir": EMERALD_NOIR,
            "Royal Indigo": ROYAL_INDIGO,
            "Crimson Gold": CRIMSON_GOLD,
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


