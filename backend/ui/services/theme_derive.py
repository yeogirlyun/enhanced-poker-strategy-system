"""
Theme token derivation system for poker themes.
Converts base palette colors into comprehensive token sets for all UI elements.
"""

from typing import Dict, Any


def clamp(x: float) -> int:
    """Clamp value to valid RGB range [0, 255]."""
    return max(0, min(255, int(x)))


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    h = hex_color.strip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)


def rgb_to_hex(rgb_tuple: tuple[float, float, float]) -> str:
    """Convert RGB tuple to hex color."""
    return "#{:02X}{:02X}{:02X}".format(*map(clamp, rgb_tuple))


def mix(color_a: str, color_b: str, t: float) -> str:
    """Mix two hex colors with interpolation factor t (0.0 = color_a, 1.0 = color_b)."""
    ra, ga, ba = hex_to_rgb(color_a)
    rb, gb, bb = hex_to_rgb(color_b)
    return rgb_to_hex((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


def lighten(hex_color: str, t: float) -> str:
    """Lighten a hex color by factor t (0.0 = no change, 1.0 = white)."""
    return mix(hex_color, "#FFFFFF", t)


def darken(hex_color: str, t: float) -> str:
    """Darken a hex color by factor t (0.0 = no change, 1.0 = black)."""
    return mix(hex_color, "#000000", t)


def alpha_over(src: str, dst: str, alpha: float) -> str:
    """
    Simulate alpha blending of src color over dst color.
    alpha: 0.0 = fully transparent src (shows dst), 1.0 = fully opaque src
    """
    rs, gs, bs = hex_to_rgb(src)
    rd, gd, bd = hex_to_rgb(dst)
    return rgb_to_hex(
        (rd + (rs - rd) * alpha, gd + (gs - gd) * alpha, bd + (bs - bd) * alpha)
    )


def derive_tokens(palette: Dict[str, str]) -> Dict[str, str]:
    """
    Derive comprehensive token set from base palette.

    Args:
        palette: Base color palette with keys like felt, rail, metal, accent, etc.

    Returns:
        Dictionary of derived tokens for all UI elements
    """
    felt = palette["felt"]
    rail = palette["rail"]
    metal = palette["metal"]
    accent = palette["accent"]
    raise_color = palette["raise"]
    call_color = palette["call"]  # Used for future call-specific styling
    neutral = palette["neutral"]
    text = palette["text"]

    # Derive chip colors using sophisticated blending
    chip_face = alpha_over(lighten(felt, 0.18), neutral, 0.25)
    chip_edge = alpha_over(metal, felt, 0.25)
    chip_rim = alpha_over(metal, "#000000", 0.45)

    tokens = {
        # Table surface
        "table.felt": felt,
        "table.rail": rail,
        "table.edgeGlow": darken(felt, 0.6),
        "table.centerPattern": lighten(felt, 0.06),
        # Text hierarchy
        "text.primary": lighten(text, 0.10),
        "text.secondary": lighten(text, 0.35),
        "text.muted": lighten(text, 0.55),
        # Card faces and backs
        "card.face.bg": lighten(neutral, 0.85),
        "card.face.border": darken(neutral, 0.50),
        "card.pip.red": mix(raise_color, "#FF2A2A", 0.35),
        "card.pip.black": darken(neutral, 0.85),
        "card.back.bg": alpha_over(accent, felt, 0.35),
        "card.back.pattern": alpha_over(metal, accent, 0.25),
        "card.back.border": metal,
        # Board elements
        "board.slotBg": alpha_over(darken(felt, 0.45), felt, 0.80),
        "board.border": alpha_over(metal, felt, 0.85),
        "board.cardFaceFg": lighten(neutral, 0.85),
        "board.cardBack": alpha_over(accent, felt, 0.35),
        # Chip system (stack/bet/pot with theme awareness)
        "chip_face": chip_face,
        "chip_edge": chip_edge,
        "chip_rim": chip_rim,
        "chip_text": "#F8F7F4",
        # Bet chips (accent-themed)
        "bet_face": alpha_over(accent, chip_face, 0.60),
        "bet_edge": alpha_over(accent, chip_edge, 0.75),
        "bet_rim": alpha_over(metal, accent, 0.55),
        "bet_glow": alpha_over(metal, accent, 0.35),
        # Pot chips (metal-themed)
        "pot_face": alpha_over(lighten(metal, 0.20), chip_face, 0.70),
        "pot_edge": alpha_over(metal, "#000000", 0.15),
        "pot_rim": alpha_over(lighten(metal, 0.35), "#000000", 0.30),
        "pot_text": "#0B0B0E",
        "pot_glow": alpha_over(lighten(metal, 0.25), "#000000", 0.20),
        # Selection and highlighting
        "highlight": palette["highlight"],
        "highlight_text": palette["highlight_text"],
        "emphasis.text": palette["emphasis_text"],
        "emphasis.divider": metal,
        # Player seats and states
        "seat.bg.idle": alpha_over(darken(felt, 0.3), neutral, 0.15),
        "seat.bg.active": alpha_over(lighten(felt, 0.1), neutral, 0.20),
        "seat.ring": alpha_over(metal, felt, 0.40),
        "seat.accent": accent,
        "seat.highlight": alpha_over(lighten(metal, 0.15), felt, 0.30),
        "seat.shadow": darken(felt, 0.4),
        "seat.cornerAccent": metal,
        # Player nameplate
        "player.nameplate.bg": alpha_over(darken(felt, 0.2), neutral, 0.10),
        "player.nameplate.border": alpha_over(metal, felt, 0.50),
        "player.name": lighten(text, 0.05),
        # Action states and focus
        "a11y.focus": "#DAA520",  # Gold focus ring
        # Pot display
        "pot.badgeRing": lighten(metal, 0.15),
        "pot.bg": alpha_over(lighten(metal, 0.25), felt, 0.70),
        "pot.border": metal,
        # Button states
        "btn.secondary.border": alpha_over(metal, felt, 0.60),
        # Legacy compatibility tokens (for existing components)
        "bet.bg": alpha_over(accent, felt, 0.40),
        "bet.border": alpha_over(metal, accent, 0.60),
        "bet.text": lighten(metal, 0.20),
        "bet.active": raise_color,
    }

    return tokens


def resolve_token_references(
    config: Dict[str, Any], palette: Dict[str, str]
) -> Dict[str, Any]:
    """
    Resolve $token references in configuration using palette.

    Args:
        config: Configuration dict that may contain $token references
        palette: Base palette to resolve references from

    Returns:
        Configuration with all $token references resolved
    """

    def resolve_value(value):
        if isinstance(value, str) and value.startswith("$"):
            token_key = value[1:]  # Remove $ prefix
            if token_key in palette:
                return palette[token_key]
            else:
                print(f"⚠️ Unknown token reference: {value}")
                return value  # Return as-is if token not found
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item) for item in value]
        else:
            return value

    return resolve_value(config)


def get_player_state_style(
    defaults: Dict[str, Any], palette: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    """
    Get player state styling configuration with resolved token references.

    Args:
        defaults: Default configuration from theme pack
        palette: Base color palette

    Returns:
        Resolved state styling configuration
    """
    state_config = defaults.get("state", {})
    return resolve_token_references(state_config, palette)


def get_selection_style(
    defaults: Dict[str, Any], palette: Dict[str, str]
) -> Dict[str, str]:
    """Get selection highlighting style with resolved tokens."""
    selection_config = defaults.get("selection", {})
    return resolve_token_references(selection_config, palette)


def get_emphasis_bar_style(
    defaults: Dict[str, Any], palette: Dict[str, str]
) -> Dict[str, str]:
    """Get emphasis bar styling with resolved tokens."""
    emphasis_config = defaults.get("emphasis_bar", {})
    return resolve_token_references(emphasis_config, palette)


def get_chip_styles(
    defaults: Dict[str, Any], palette: Dict[str, str]
) -> Dict[str, Dict[str, str]]:
    """Get chip styling configurations with resolved tokens."""
    chip_config = defaults.get("chips", {})
    return resolve_token_references(chip_config, palette)
