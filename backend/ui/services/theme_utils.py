"""
Theme Utilities - Color Derivation Helpers
Provides deterministic color manipulation functions for consistent theming
"""

def clamp(x):
    """Clamp value to 0-255 range"""
    return max(0, min(255, int(x)))

def hex_to_rgb(h):
    """Convert hex color to RGB tuple"""
    h = h.strip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(t):
    """Convert RGB tuple to hex color"""
    return "#{:02X}{:02X}{:02X}".format(*map(clamp, t))

def mix(a, b, t):
    """Mix two hex colors with ratio t (0=a, 1=b)"""
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return rgb_to_hex((
        ra + (rb - ra) * t,
        ga + (gb - ga) * t,
        ba + (bb - ba) * t
    ))

def lighten(h, t):
    """Lighten hex color by ratio t (0=no change, 1=white)"""
    return mix(h, "#FFFFFF", t)

def darken(h, t):
    """Darken hex color by ratio t (0=no change, 1=black)"""
    return mix(h, "#000000", t)

def alpha_over(src, dst, a):
    """Simple alpha compositing: src over dst with alpha a (0..1)"""
    rs, gs, bs = hex_to_rgb(src)
    rd, gd, bd = hex_to_rgb(dst)
    return rgb_to_hex((
        rd + (rs - rd) * a,
        gd + (gs - gd) * a,
        bd + (bs - bd) * a
    ))

def adjust_saturation(h, factor):
    """Adjust saturation of hex color (factor: 0=grayscale, 1=normal, >1=more saturated)"""
    r, g, b = hex_to_rgb(h)
    # Convert to HSL-like adjustment
    gray = (r + g + b) / 3
    r = gray + (r - gray) * factor
    g = gray + (g - gray) * factor
    b = gray + (b - gray) * factor
    return rgb_to_hex((r, g, b))

def get_contrast_color(bg_hex, light_text="#FFFFFF", dark_text="#000000"):
    """Get appropriate text color for background (simple luminance check)"""
    r, g, b = hex_to_rgb(bg_hex)
    # Simple luminance calculation
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return dark_text if luminance > 0.5 else light_text

def ease_in_out_cubic(t):
    """Cubic ease-in-out function for smooth animations"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

def ease_color_transition(color_a, color_b, progress):
    """Smooth color transition with easing"""
    eased_progress = ease_in_out_cubic(progress)
    return mix(color_a, color_b, eased_progress)
