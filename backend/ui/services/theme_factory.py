"""
Theme Factory - Deterministic Token Generation
Builds complete theme token sets from minimal base color palettes
Now integrated with config-driven theme system
"""

from .theme_utils import lighten, darken, mix, alpha_over
from .theme_loader import get_theme_loader
from .theme_derive import (
    derive_tokens,
    get_player_state_style,
    get_selection_style,
    get_emphasis_bar_style,
    get_chip_styles,
)


def _get_emphasis_background(base):
    """Get emphasis background with painter-specific styling."""
    painter = base.get("painter", "classic")
    felt = base["felt"]
    accent = base["accent"]

    if painter == "impressionist":  # Monet Noir
        # Misty gradient: #253C4A → #0D1B1E
        return f"linear-gradient(180deg, {accent} 0%, {felt} 100%)"
    elif painter == "ornamental":  # Klimt Royale
        # Deep mahogany with gold tessellation
        return "linear-gradient(180deg, #6E0D0D 0%, #3D0606 100%)"
    elif painter == "gemstone":  # Imperial Jade
        # Jade gradient with mandala emboss
        return f"linear-gradient(180deg, {lighten(felt, 0.1)} 0%, {darken(felt, 0.2)} 100%)"
    elif painter == "geometric":  # Deco Luxe
        # Smoky indigo with art deco pattern
        return f"linear-gradient(180deg, {lighten(felt, 0.15)} 0%, {darken(felt, 0.1)} 100%)"
    else:
        # Classic gradient for other themes
        return f"linear-gradient(180deg, {lighten(felt, 0.2)} 0%, {darken(felt, 0.1)} 100%)"


def _get_emphasis_text_color(base):
    """Get emphasis text color optimized for readability."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return "#F5F7FA"  # Soft white for pastel glow
    elif painter == "ornamental":  # Klimt Royale
        return "#F4E2C9"  # Golden-ivory for luxury
    elif painter == "gemstone":  # Imperial Jade
        return "#E8E6E3"  # Pearl white for elegance
    elif painter == "geometric":  # Deco Luxe
        return "#F5F0E1"  # Cream white for sophistication
    else:
        return lighten(base["text"], 0.20)  # Enhanced contrast for others


def _get_emphasis_highlight(base):
    """Get emphasis highlight color for important words."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return "#E8A7C3"  # Pastel pink
    elif painter == "ornamental":  # Klimt Royale
        return "#C1121F"  # Blood crimson glow
    elif painter == "gemstone":  # Imperial Jade
        return "#C9A441"  # Antique gold
    elif painter == "geometric":  # Deco Luxe
        return "#B08D57"  # Polished brass
    else:
        return base["raise_"]  # Use theme's danger color


def _get_emphasis_glow(base):
    """Get emphasis inner glow color."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return alpha_over("#A7C8E8", "#000000", 0.12)  # Pale sky blue glow
    elif painter == "ornamental":  # Klimt Royale
        return alpha_over("#FFD700", "#000000", 0.12)  # Gold inner glow
    elif painter == "gemstone":  # Imperial Jade
        return alpha_over("#DAA520", "#000000", 0.10)  # Jade-gold glow
    elif painter == "geometric":  # Deco Luxe
        return alpha_over("#D4AF37", "#000000", 0.12)  # Art deco gold glow
    else:
        return alpha_over(base["metal"], "#000000", 0.15)


def _get_emphasis_border(base):
    """Get emphasis border color (gold trim lines)."""
    painter = base.get("painter", "classic")

    if painter in ["ornamental", "gemstone", "geometric"]:
        return "#B8860B"  # Gold leaf trim
    elif painter == "impressionist":
        return alpha_over("#C8D5DE", "#000000", 0.40)  # Soft metallic
    else:
        return base["metal"]


def build_theme(base):
    """
    Build complete theme tokens from base palette

    Args:
        base: dict with keys:
            - felt: Primary table surface color
            - metal: Trim/accent metallic color
            - accent: Secondary accent color
            - raise_: Danger/raise action color
            - call: Success/call action color
            - neutral: Neutral gray base
            - text: Primary text color
            - background: (optional) Background color for artistic themes
            - pattern_overlay: (optional) Pattern overlay identifier
            - identifier_effect: (optional) Unique visual effect
            - painter: (optional) Painter style identifier

    Returns:
        Complete token dictionary for all UI elements
    """
    felt = base["felt"]
    metal = base["metal"]
    accent = base["accent"]
    raise_c = base["raise_"]
    call_c = base["call"]
    neutral = base["neutral"]
    txt = base["text"]

    # Artistic theme enhancements
    background = base.get("background", darken(felt, 0.8))
    pattern_overlay = base.get("pattern_overlay", None)
    identifier_effect = base.get("identifier_effect", None)
    painter = base.get("painter", None)

    # Build comprehensive token set
    tokens = {
        # === SURFACES ===
        "table.felt": felt,
        "table.rail": darken(felt, 0.75),
        "table.inlay": metal,
        "table.edgeGlow": darken(felt, 0.6),
        "table.centerPattern": lighten(felt, 0.06),  # Subtle ellipse at center
        # === TEXT ===
        "text.primary": lighten(txt, 0.10),
        "text.secondary": lighten(txt, 0.35),
        "text.muted": lighten(txt, 0.55),
        # === EMPHASIZED TEXT (High-contrast bars) ===
        "text.emphasis.bg": _get_emphasis_background(base),
        "text.emphasis.color": _get_emphasis_text_color(base),
        "text.emphasis.highlight": _get_emphasis_highlight(base),
        "text.emphasis.shadow": alpha_over("#000000", felt, 0.60),
        "text.emphasis.glow": _get_emphasis_glow(base),
        "text.emphasis.border": _get_emphasis_border(base),
        # === CARDS ===
        # Neutral ivory face, theme-tinted back
        "card.face.bg": lighten(neutral, 0.85),
        "card.face.border": darken(neutral, 0.50),
        "card.pip.red": mix(raise_c, "#FF2A2A", 0.35),
        "card.pip.black": darken(neutral, 0.85),
        "card.back.bg": alpha_over(accent, felt, 0.35),
        "card.back.pattern": alpha_over(metal, accent, 0.25),
        "card.back.border": metal,
        # === COMMUNITY BOARD ===
        "board.slotBg": alpha_over(darken(felt, 0.45), felt, 0.80),
        "board.border": alpha_over(metal, felt, 0.85),
        "board.shadow": darken(felt, 0.85),
        # === CHIPS ===
        # Standard casino colors with theme-tinted rims
        "chip.$1": "#2E86AB",  # Blue
        "chip.$5": "#B63D3D",  # Red
        "chip.$25": "#2AA37A",  # Green
        "chip.$100": "#3C3A3A",  # Black
        "chip.$500": "#6C4AB6",  # Purple
        "chip.$1k": "#D1B46A",  # Gold
        "chip.rim": alpha_over(metal, "#000000", 0.35),
        "chip.text": "#F8F7F4",
        # === POT ===
        "pot.badgeBg": alpha_over(darken(felt, 0.5), felt, 0.85),
        "pot.badgeRing": metal,
        "pot.valueText": lighten(neutral, 0.9),
        # === BETS & ANIMATIONS ===
        "bet.path": alpha_over(accent, "#000000", 0.50),
        "bet.glow": alpha_over(metal, "#000000", 0.35),
        # === PLAYER LABELS ===
        "label.active.bg": alpha_over(call_c, "#000000", 0.60),
        "label.active.fg": lighten(neutral, 0.95),
        "label.folded.bg": alpha_over(neutral, "#000000", 0.75),
        "label.folded.fg": lighten(neutral, 0.65),
        "label.winner.bg": alpha_over(metal, "#000000", 0.70),
        "label.winner.fg": "#0B0B0E",
        # === BUTTONS (Enhanced from existing system) ===
        "btn.primary.bg": alpha_over(accent, "#000000", 0.70),
        "btn.primary.fg": lighten(neutral, 0.95),
        "btn.primary.border": metal,
        "btn.primary.hoverBg": alpha_over(accent, "#000000", 0.55),
        "btn.primary.hoverFg": "#FFFFFF",
        "btn.primary.hoverBorder": lighten(metal, 0.20),
        "btn.primary.activeBg": alpha_over(accent, "#000000", 0.85),
        "btn.primary.activeFg": "#FFFFFF",
        "btn.primary.activeBorder": lighten(metal, 0.35),
        "btn.secondary.bg": alpha_over(neutral, "#000000", 0.60),
        "btn.secondary.fg": lighten(txt, 0.20),
        "btn.secondary.border": alpha_over(metal, "#000000", 0.60),
        "btn.secondary.hoverBg": alpha_over(neutral, "#000000", 0.45),
        "btn.secondary.hoverFg": lighten(txt, 0.35),
        "btn.secondary.hoverBorder": alpha_over(metal, "#000000", 0.45),
        "btn.danger.bg": alpha_over(raise_c, "#000000", 0.70),
        "btn.danger.fg": lighten(neutral, 0.95),
        "btn.danger.border": lighten(raise_c, 0.20),
        "btn.danger.hoverBg": alpha_over(raise_c, "#000000", 0.55),
        "btn.danger.hoverFg": "#FFFFFF",
        "btn.danger.hoverBorder": lighten(raise_c, 0.35),
        # === PLAYER SEATS ===
        "seat.bg.idle": alpha_over(neutral, felt, 0.25),
        "seat.bg.active": alpha_over(call_c, felt, 0.15),
        "seat.bg.acting": alpha_over(call_c, "#000000", 0.40),
        "seat.bg.folded": alpha_over(neutral, "#000000", 0.70),
        "seat.ring": alpha_over(metal, felt, 0.60),
        "seat.highlight": lighten(felt, 0.15),
        "seat.shadow": darken(felt, 0.80),
        # === DEALER BUTTON ===
        "dealer.buttonBg": lighten(neutral, 0.90),
        "dealer.buttonFg": darken(neutral, 0.85),
        "dealer.buttonBorder": metal,
        # === ACTION COLORS ===
        "action.fold": alpha_over(neutral, "#000000", 0.60),
        "action.check": alpha_over(call_c, "#000000", 0.50),
        "action.call": call_c,
        "action.bet": alpha_over(metal, call_c, 0.70),
        "action.raise": raise_c,
        "action.allin": alpha_over(raise_c, metal, 0.60),
        # === ACCESSIBILITY & CHROME ===
        "a11y.focus": lighten(metal, 0.30),
        "divider": darken(felt, 0.70),
        "grid.lines": darken(felt, 0.60),
        # === MICRO-INTERACTIONS ===
        "glow.soft": alpha_over(metal, "#000000", 0.20),
        "glow.medium": alpha_over(metal, "#000000", 0.40),
        "glow.strong": alpha_over(metal, "#000000", 0.70),
        "pulse.slow": alpha_over(call_c, "#000000", 0.30),
        "pulse.fast": alpha_over(raise_c, "#000000", 0.50),
        # === TYPOGRAPHY ===
        "font.display": ("Inter", 24, "bold"),
        "font.h1": ("Inter", 20, "bold"),
        "font.h2": ("Inter", 16, "semibold"),
        "font.body": ("Inter", 14, "normal"),
        "font.small": ("Inter", 12, "normal"),
        "font.mono": ("JetBrains Mono", 12, "normal"),
        # === ARTISTIC ENHANCEMENTS ===
        "artistic.background": background,
        "artistic.pattern_overlay": pattern_overlay,
        "artistic.identifier_effect": identifier_effect,
        "artistic.painter": painter,
        # === PAINTER-SPECIFIC EFFECTS ===
        "effect.soft_glow": alpha_over(accent, "#FFFFFF", 0.15),
        "effect.gold_dust": "#FFD700",
        "effect.jade_gloss": alpha_over("#014421", "#FFFFFF", 0.25),
        "effect.arc_motion": metal,
        # === PATTERN OVERLAYS ===
        "pattern.mist_ripple": alpha_over(accent, "#FFFFFF", 0.12),
        "pattern.gold_tessellation": alpha_over("#D4AF37", felt, 0.15),
        "pattern.jade_mandala": alpha_over("#DAA520", felt, 0.10),
        "pattern.art_deco_sunburst": alpha_over("#D4AF37", felt, 0.12),
    }

    # Add premium chip tokens
    derive_chip_tokens(tokens, felt, metal, accent, raise_c, call_c, neutral)

    return tokens


def derive_chip_tokens(tokens, felt, metal, accent, raise_c, call_c, neutral):
    """Derive premium chip tokens from base theme swatches."""
    # Base "casino composite clay" hue: a mix of felt and neutral
    base_face = alpha_over(lighten(felt, 0.18), neutral, 0.25)
    base_edge = alpha_over(metal, felt, 0.25)
    base_rim = alpha_over(metal, "#000000", 0.45)
    base_text = "#F8F7F4"

    tokens.update(
        {
            # Generic chip tokens
            "chip.face": base_face,
            "chip.edge": base_edge,
            "chip.rim": base_rim,
            "chip.text": base_text,
            # Stack chips: calm, readable, less saturated to avoid UI noise
            "chip.stack.face": alpha_over(base_face, "#000000", 0.15),
            "chip.stack.edge": alpha_over(base_edge, "#000000", 0.10),
            "chip.stack.rim": base_rim,
            "chip.stack.text": base_text,
            "chip.stack.shadow": darken(felt, 0.85),
            # Bet/Call chips: pop with the theme accent for motion visibility
            "chip.bet.face": alpha_over(accent, base_face, 0.60),
            "chip.bet.edge": alpha_over(accent, base_edge, 0.75),
            "chip.bet.rim": alpha_over(metal, accent, 0.55),
            "chip.bet.text": base_text,
            "chip.bet.glow": alpha_over(metal, accent, 0.35),
            # Pot chips: prestigious—lean into metal, slightly brighter
            "chip.pot.face": alpha_over(lighten(metal, 0.20), base_face, 0.70),
            "chip.pot.edge": alpha_over(metal, "#000000", 0.15),
            "chip.pot.rim": alpha_over(lighten(metal, 0.35), "#000000", 0.30),
            "chip.pot.text": "#0B0B0E",
            "chip.pot.glow": alpha_over(lighten(metal, 0.25), "#000000", 0.20),
        }
    )


# Base color palettes for all 16 themes
THEME_BASES = {
    # Row 1 — Classic
    "Forest Green Professional": {
        "felt": "#1E4D2B",
        "metal": "#C9A86A",
        "accent": "#2E7D32",
        "raise_": "#B63D3D",
        "call": "#2AA37A",
        "neutral": "#9AA0A6",
        "text": "#EDECEC",
    },
    "Velvet Burgundy": {
        "felt": "#4A1212",
        "metal": "#C0A066",
        "accent": "#702525",
        "raise_": "#B53A44",
        "call": "#2AA37A",
        "neutral": "#A29A90",
        "text": "#F2E9DF",
        "painter": "velvet",
        "identifier_effect": "crimson_glow",
    },
    "Obsidian Gold": {
        "felt": "#0A0A0A",
        "metal": "#D4AF37",
        "accent": "#2C2C2C",
        "raise_": "#A41E34",
        "call": "#2AA37A",
        "neutral": "#A7A7A7",
        "text": "#E6E6E6",
    },
    "Imperial Jade": {
        "felt": "#014421",
        "metal": "#DAA520",
        "accent": "#C9A441",
        "raise_": "#B23B43",
        "call": "#32B37A",
        "neutral": "#9CB1A8",
        "text": "#E8E6E3",
        "background": "#0C0C0C",
        "pattern_overlay": "jade_mandala",
        "identifier_effect": "jade_gloss",
        "painter": "gemstone",
    },
    # Row 2 — Artistic 4 (Painter-Inspired Luxury)
    "Monet Noir": {
        "felt": "#0D1B1E",
        "metal": "#C8D5DE",
        "accent": "#253C4A",
        "raise_": "#E8A7C3",
        "call": "#A7C8E8",
        "neutral": "#8EA6B5",
        "text": "#F5F7FA",
        "background": "#3B2F4A",
        "pattern_overlay": "mist_ripple",
        "identifier_effect": "soft_glow",
        "painter": "impressionist",
    },
    "Caravaggio Noir": {
        "felt": "#0A0A0C",
        "metal": "#E1C16E",
        "accent": "#9E0F28",
        "raise_": "#B3122E",
        "call": "#2AA37A",
        "neutral": "#9C8F7A",
        "text": "#FFF7E6",
    },
    "Klimt Royale": {
        "felt": "#0A0A0A",
        "metal": "#FFD700",
        "accent": "#D4AF37",
        "raise_": "#A4161A",
        "call": "#32B37A",
        "neutral": "#A38E6A",
        "text": "#FFF2D9",
        "background": "#3C2B1F",
        "pattern_overlay": "gold_tessellation",
        "identifier_effect": "gold_dust",
        "painter": "ornamental",
    },
    "Deco Luxe": {
        "felt": "#1B1E2B",
        "metal": "#B08D57",
        "accent": "#D4AF37",
        "raise_": "#5B1922",
        "call": "#2AA37A",
        "neutral": "#9B9486",
        "text": "#F5F0E1",
        "background": "#2E3B55",
        "pattern_overlay": "art_deco_sunburst",
        "identifier_effect": "arc_motion",
        "painter": "geometric",
    },
    # Row 3 — Nature & Light
    "Sunset Mirage": {
        "felt": "#2B1C1A",
        "metal": "#E6B87A",
        "accent": "#C16E3A",
        "raise_": "#C85C5C",
        "call": "#2AA37A",
        "neutral": "#A68C7A",
        "text": "#F7E7D6",
    },
    "Oceanic Blue": {
        "felt": "#0F1620",
        "metal": "#B7C1C8",
        "accent": "#3B6E8C",
        "raise_": "#6C94D2",
        "call": "#57C2B6",
        "neutral": "#9DB3C4",
        "text": "#F5F7FA",
    },
    "Velour Crimson": {
        "felt": "#6E0B14",
        "metal": "#C18F65",
        "accent": "#3B0A0F",
        "raise_": "#A41E34",
        "call": "#2AA37A",
        "neutral": "#A3928A",
        "text": "#F5E2C8",
    },
    "Golden Dusk": {
        "felt": "#5C3A21",
        "metal": "#C18F65",
        "accent": "#A3622B",
        "raise_": "#B35A3B",
        "call": "#2AA37A",
        "neutral": "#AF9A8A",
        "text": "#F3E3D3",
    },
    # Row 4 — Modern / Bold
    "Cyber Neon": {
        "felt": "#0D0F13",
        "metal": "#9BE3FF",
        "accent": "#17C3E6",
        "raise_": "#D65DB1",
        "call": "#00D9A7",
        "neutral": "#A3A8B3",
        "text": "#EAF8FF",
    },
    "Stealth Graphite": {
        "felt": "#111214",
        "metal": "#8D8D8D",
        "accent": "#232629",
        "raise_": "#9E3B49",
        "call": "#57C2B6",
        "neutral": "#8E9196",
        "text": "#E6E7EA",
    },
    "Royal Sapphire": {
        "felt": "#0B1F36",
        "metal": "#C7D3E0",
        "accent": "#224D8F",
        "raise_": "#6C4AB6",
        "call": "#57C2B6",
        "neutral": "#9AB1CF",
        "text": "#F2F6FC",
    },
    "Midnight Aurora": {
        "felt": "#0E1A28",
        "metal": "#D0D9DF",
        "accent": "#1C3E4A",
        "raise_": "#6FB5E7",
        "call": "#7BD0BC",
        "neutral": "#98A8B8",
        "text": "#F5F7FA",
    },
}


def _get_theme_selection_highlight(theme_name: str) -> dict:
    """Get theme-specific selection highlight colors for immersive experience."""

    # Theme-specific highlight palette for hand selections (matching THEME_ORDER)
    highlights = {
        # Row 1 — Classic Casino
        "Forest Green Professional": {
            "color": "#1DB954",
            "glow": "#22FF5A",
            "style": "emerald",
        },
        "Velvet Burgundy": {
            "color": "#A31D2B",
            "glow": "#C12839",
            "style": "deep_wine",
        },
        "Obsidian Gold": {"color": "#4169E1", "glow": "#6495ED", "style": "sapphire"},
        "Imperial Jade": {"color": "#00A86B", "glow": "#20C997", "style": "jade_teal"},
        # Row 2 — Luxury Noir (Art-inspired)
        "Monet Noir": {"color": "#E8A7C3", "glow": "#FFB6C1", "style": "rose"},
        "Caravaggio Noir": {
            "color": "#EAD6B7",
            "glow": "#F5E6C8",
            "style": "candlelight_ivory",
        },
        "Klimt Royale": {
            "color": "#B87333",
            "glow": "#CD853F",
            "style": "burnished_copper",
        },
        "Deco Luxe": {"color": "#B08D57", "glow": "#D4AF37", "style": "art_deco_brass"},
        # Row 3 — Nature & Light
        "Sunset Mirage": {
            "color": "#FF6B35",
            "glow": "#FF8C42",
            "style": "sunset_orange",
        },
        "Oceanic Blue": {"color": "#20B2AA", "glow": "#48D1CC", "style": "turquoise"},
        "Velour Crimson": {"color": "#FFD700", "glow": "#FFF700", "style": "gold"},
        "Golden Dusk": {"color": "#B87333", "glow": "#CD853F", "style": "copper"},
        # Row 4 — Modern / Bold
        "Cyber Neon": {"color": "#00FFFF", "glow": "#00FFFF", "style": "electric_cyan"},
        "Stealth Graphite": {
            "color": "#708090",
            "glow": "#B0C4DE",
            "style": "steel_blue",
        },
        "Royal Sapphire": {
            "color": "#4169E1",
            "glow": "#6495ED",
            "style": "royal_blue",
        },
        "Midnight Aurora": {
            "color": "#7BD0BC",
            "glow": "#98FB98",
            "style": "aurora_green",
        },
    }

    return highlights.get(
        theme_name,
        {
            "color": "#1DB954",
            "glow": "#22FF5A",
            "style": "emerald",  # Default fallback
        },
    )


def _get_theme_emphasis_colors(theme_name: str) -> dict:
    """Get theme-specific emphasis text colors for better contrast."""

    emphasis_colors = {
        # Row 1 — Classic Casino
        "Forest Green Professional": {
            "bg_gradient": ["#0B2818", "#051A0C"],
            "text": "#F0F8E8",
            "accent": "#1DB954",
        },
        "Velvet Burgundy": {
            "bg_gradient": ["#5C0A0A", "#2B0000"],
            "text": "#F9E7C9",
            "accent": "#A31D2B",
        },
        "Obsidian Gold": {
            "bg_gradient": ["#1A1A1A", "#0A0A0A"],
            "text": "#F9E7C9",
            "accent": "#D4AF37",
        },
        "Imperial Jade": {
            "bg_gradient": ["#1A2F1A", "#0F1F0F"],
            "text": "#F0F8E8",
            "accent": "#C9A441",
        },
        # Row 2 — Luxury Noir (Art-inspired)
        "Monet Noir": {
            "bg_gradient": ["#2C2C2C", "#1A1A1A"],
            "text": "#F5F0E1",
            "accent": "#E8A7C3",
        },
        "Caravaggio Noir": {
            "bg_gradient": ["#2A1A1A", "#1A0F0F"],
            "text": "#EAD6B7",
            "accent": "#EAD6B7",
        },
        "Klimt Royale": {
            "bg_gradient": ["#3D2914", "#2A1C0E"],
            "text": "#F5F0E1",
            "accent": "#C1121F",
        },
        "Deco Luxe": {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#F5F0E1",
            "accent": "#B08D57",
        },
        # Row 3 — Nature & Light
        "Sunset Mirage": {
            "bg_gradient": ["#3D1A0F", "#2B1208"],
            "text": "#F5E6D3",
            "accent": "#FF6B35",
        },
        "Oceanic Blue": {
            "bg_gradient": ["#0F2B3D", "#081A2B"],
            "text": "#E8F4F8",
            "accent": "#20B2AA",
        },
        "Velour Crimson": {
            "bg_gradient": ["#5C0A0A", "#2B0000"],
            "text": "#F9E7C9",
            "accent": "#C1121F",
        },
        "Golden Dusk": {
            "bg_gradient": ["#4A2F1A", "#2B1C10"],
            "text": "#EBD9B0",
            "accent": "#C18F65",
        },
        # Row 4 — Modern Bold
        "Cyber Neon": {
            "bg_gradient": ["#1A1F2E", "#0F1419"],
            "text": "#E8F8FF",
            "accent": "#00FFFF",
        },
        "Stealth Graphite": {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#E6E7EA",
            "accent": "#708090",
        },
        "Royal Sapphire": {
            "bg_gradient": ["#1A2A4A", "#0F1A3D"],
            "text": "#F2F6FC",
            "accent": "#4169E1",
        },
        "Midnight Aurora": {
            "bg_gradient": ["#1A2F2A", "#0F1F1A"],
            "text": "#F0F8F5",
            "accent": "#7BD0BC",
        },
    }

    return emphasis_colors.get(
        theme_name,
        {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#F5F5F5",
            "accent": "#1DB954",  # Default
        },
    )


def build_theme_from_config(theme_id: str) -> dict:
    """
    Build theme using new config-driven system.

    Args:
        theme_id: ID of theme to build from poker_themes.json

    Returns:
        Complete theme token set
    """
    loader = get_theme_loader()
    defaults = loader.get_defaults()
    theme_config = loader.get_theme_by_id(theme_id)

    palette = theme_config.get("palette", {})

    # Derive comprehensive token set
    tokens = derive_tokens(palette)

    # Add config-driven state styles
    state_styles = get_player_state_style(defaults, palette)
    for k, v in state_styles.items():
        tokens[f"state.{k}"] = v  # type: ignore

    # Add selection styles
    selection_style = get_selection_style(defaults, palette)
    for k, v in selection_style.items():
        tokens[f"selection.{k}"] = v  # type: ignore

    # Add emphasis bar styles
    emphasis_style = get_emphasis_bar_style(defaults, palette)
    for k, v in emphasis_style.items():
        tokens[f"emphasis.{k}"] = v  # type: ignore

    # Add chip styles
    chip_styles = get_chip_styles(defaults, palette)
    for chip_type, styles in chip_styles.items():
        for k, v in styles.items():
            tokens[f"chips.{chip_type}.{k}"] = v  # type: ignore

    # Add theme metadata
    tokens.update(
        {
            "theme.id": theme_config.get("id", theme_id),
            "theme.name": theme_config.get("name", theme_id),
            "theme.palette": palette,
        }
    )

    # Legacy compatibility: add UI highlight tokens
    tokens["ui.highlight"] = palette.get("highlight", "#D4AF37")
    tokens["ui.highlight.text"] = palette.get("highlight_text", "#FFFFFF")
    tokens["ui.highlight.glow"] = tokens.get("bet_glow", "#22C55E")

    return tokens


def build_all_themes():
    """Build complete token sets for all 16 themes using config-driven system"""
    themes = {}

    try:
        # Try to use new config-driven system
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()
        print(f"🎨 ThemeFactory: Found {len(theme_list)} themes in config")

        for theme_info in theme_list:
            theme_id = theme_info["id"]
            # Use display name as key for theme manager compatibility
            display_name = theme_info["name"]
            print(f"🎨 Building theme: {display_name} (id: {theme_id})")
            themes[display_name] = build_theme_from_config(theme_id)

        print(f"✅ Built {len(themes)} themes using config-driven system")

    except Exception as e:
        print(f"⚠️ Config-driven theme loading failed: {e}")
        print("🔄 Falling back to legacy theme system...")

        # Fallback to legacy system
        for name, base in THEME_BASES.items():
            theme = build_theme(base)
            # Use actual JSON theme highlight colors instead of hardcoded values
            # The theme already has the correct highlight values from build_theme()
            # Don't override them with hardcoded selection_highlight values
            theme["ui.highlight"] = theme.get("ui.highlight", base.get("highlight", "#D4AF37"))
            theme["ui.highlight.text"] = theme.get("ui.highlight.text", base.get("highlight_text", "#FFFFFF"))
            theme["ui.highlight.glow"] = theme.get("ui.highlight.glow", base.get("metal", base.get("accent", "#FFD700")))
            themes[name] = theme

    return themes


def get_available_theme_names() -> list[str]:
    """Get list of available theme names for UI selection."""
    try:
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()
        return [theme_info["name"] for theme_info in theme_list]
    except Exception:
        # Fallback to legacy theme names
        return list(THEME_BASES.keys())


def get_theme_by_name(theme_name: str) -> dict:
    """Get theme by display name (for UI compatibility)."""
    try:
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()

        # Find theme by name
        for theme_info in theme_list:
            if theme_info["name"] == theme_name:
                return build_theme_from_config(theme_info["id"])

        # Fallback: try by ID (kebab-case)
        theme_id = theme_name.lower().replace(" ", "-")
        return build_theme_from_config(theme_id)

    except Exception as e:
        print(f"⚠️ Could not load theme '{theme_name}': {e}")

        # Legacy fallback
        if theme_name in THEME_BASES:
            return build_theme(THEME_BASES[theme_name])

        # Ultimate fallback
        return build_theme(THEME_BASES["Forest Green Professional"])
