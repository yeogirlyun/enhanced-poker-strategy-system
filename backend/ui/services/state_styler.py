"""
State-driven styling system for poker UI elements.
Handles luxury highlighting and animations for player states.
"""

import time
import math
from typing import Dict, Any, Optional
from .theme_loader import get_theme_loader
from .theme_derive import get_player_state_style


class StateStyler:
    """Manages state-driven styling and animations for poker UI elements."""

    def __init__(self):
        self._active_animations = {}  # Track active animations
        self._last_update = time.time()

    def get_state_style(self, player_state: str, theme_id: str) -> Dict[str, Any]:
        """
        Get styling configuration for a player state.

        Args:
            player_state: State name (active, folded, winner, showdown, allin)
            theme_id: Current theme ID

        Returns:
            Style configuration with resolved colors and animation parameters
        """
        loader = get_theme_loader()
        defaults = loader.get_defaults()
        theme_config = loader.get_theme_by_id(theme_id)
        palette = theme_config.get("palette", {})

        state_styles = get_player_state_style(defaults, palette)
        return state_styles.get(player_state, {})

    def apply_player_state_styling(
        self,
        canvas,
        seat_idx: int,
        state: str,
        theme_id: str,
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
    ) -> None:
        """
        Apply state-specific styling to a player seat.

        Args:
            canvas: Tkinter canvas to draw on
            seat_idx: Seat index for element tagging
            state: Player state (active, folded, winner, showdown, allin)
            theme_id: Current theme ID
            x, y: Seat center coordinates
            pod_width, pod_height: Seat pod dimensions
        """
        style_config = self.get_state_style(state, theme_id)
        if not style_config:
            return

        current_time = time.time()

        if state == "active":
            self._apply_active_glow(
                canvas,
                seat_idx,
                style_config,
                x,
                y,
                pod_width,
                pod_height,
                current_time,
            )
        elif state == "folded":
            self._apply_folded_styling(
                canvas, seat_idx, style_config, x, y, pod_width, pod_height
            )
        elif state == "winner":
            self._apply_winner_effects(
                canvas,
                seat_idx,
                style_config,
                x,
                y,
                pod_width,
                pod_height,
                current_time,
            )
        elif state == "showdown":
            self._apply_showdown_spotlight(
                canvas,
                seat_idx,
                style_config,
                x,
                y,
                pod_width,
                pod_height,
                current_time,
            )
        elif state == "allin":
            self._apply_allin_flash(
                canvas,
                seat_idx,
                style_config,
                x,
                y,
                pod_width,
                pod_height,
                current_time,
            )

    def _apply_active_glow(
        self,
        canvas,
        seat_idx: int,
        config: Dict[str, Any],
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
        current_time: float,
    ) -> None:
        """Apply pulsing glow effect for active player."""
        glow_color = config.get("glow", "#1DB954")
        shimmer_color = config.get("shimmer", "#C9A34E")
        strength = config.get("strength", 1.0)
        period_ms = config.get("period_ms", 2000)

        # Calculate pulsing intensity
        period_s = period_ms / 1000.0
        pulse_phase = (current_time % period_s) / period_s
        pulse_intensity = (math.sin(pulse_phase * 2 * math.pi) + 1) / 2  # 0.0 to 1.0

        # Outer glow ring
        glow_radius = int(
            (pod_width + pod_height) / 4 + 10 * strength * pulse_intensity
        )
        canvas.create_oval(
            x - glow_radius,
            y - glow_radius,
            x + glow_radius,
            y + glow_radius,
            fill="",
            outline=glow_color,
            width=int(2 + strength * pulse_intensity),
            tags=("layer:effects", f"active_glow:{seat_idx}"),
        )

        # Inner shimmer highlight  
        shimmer_size = int(pod_width * 0.8)
        canvas.create_oval(
            x - shimmer_size // 2,
            y - shimmer_size // 2,
            x + shimmer_size // 2,
            y + shimmer_size // 2,
            fill="",
            outline=shimmer_color,
            width=1,
            tags=("layer:effects", f"active_shimmer:{seat_idx}"),
        )

    def _apply_folded_styling(
        self,
        canvas,
        seat_idx: int,
        config: Dict[str, Any],
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
    ) -> None:
        """Apply desaturated/faded styling for folded player."""
        opacity = config.get("opacity", 0.4)
        # Note: desaturate value available in config but not used in this implementation

        # Semi-transparent overlay to simulate reduced opacity
        overlay_color = "#000000"  # Dark overlay

        canvas.create_rectangle(
            x - pod_width // 2,
            y - pod_height // 2,
            x + pod_width // 2,
            y + pod_height // 2,
            fill=overlay_color,
            stipple="gray50",  # Stipple simulates transparency
            tags=("layer:effects", f"folded_overlay:{seat_idx}"),
        )

    def _apply_winner_effects(
        self,
        canvas,
        seat_idx: int,
        config: Dict[str, Any],
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
        current_time: float,
    ) -> None:
        """Apply celebration effects for winning player."""
        glow_color = config.get("glow", "#C9A34E")
        shimmer_color = config.get("shimmer", "#1DB954")
        strength = config.get("strength", 1.4)
        period_ms = config.get("period_ms", 1500)
        show_particles = config.get("particles", True)

        # Intense winner glow
        period_s = period_ms / 1000.0
        pulse_phase = (current_time % period_s) / period_s
        pulse_intensity = (math.sin(pulse_phase * 2 * math.pi) + 1) / 2

        # Multiple glow rings for intensity
        for ring in range(3):
            glow_radius = int(
                (pod_width + pod_height) / 4
                + (15 + ring * 8) * strength * pulse_intensity
            )
            canvas.create_oval(
                x - glow_radius,
                y - glow_radius,
                x + glow_radius,
                y + glow_radius,
                fill="",
                outline=glow_color,
                width=int(3 - ring),
                tags=("layer:effects", f"winner_glow_{ring}:{seat_idx}"),
            )

        # Shimmer burst effect
        if show_particles:
            for i in range(8):  # 8 shimmer rays
                angle = i * math.pi / 4
                ray_length = int(pod_width * 0.6 * pulse_intensity)
                end_x = x + int(ray_length * math.cos(angle))
                end_y = y + int(ray_length * math.sin(angle))

                canvas.create_line(
                    x,
                    y,
                    end_x,
                    end_y,
                    fill=shimmer_color,
                    width=2,
                    tags=("layer:effects", f"winner_ray_{i}:{seat_idx}"),
                )

    def _apply_showdown_spotlight(
        self,
        canvas,
        seat_idx: int,
        config: Dict[str, Any],
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
        current_time: float,
    ) -> None:
        """Apply spotlight effect during showdown."""
        spotlight_color = config.get("spotlight", "#FFFFFF")
        opacity = config.get("spotlight_opacity", 0.18)
        duration_ms = config.get("duration_ms", 1500)

        # Fade in/out spotlight effect
        duration_s = duration_ms / 1000.0
        phase = (current_time % duration_s) / duration_s

        # Fade in first half, fade out second half
        if phase < 0.5:
            alpha = phase * 2  # 0 to 1
        else:
            alpha = (1 - phase) * 2  # 1 to 0

        alpha *= opacity

        # Large spotlight circle
        spotlight_radius = int((pod_width + pod_height) / 2 + 20)
        canvas.create_oval(
            x - spotlight_radius,
            y - spotlight_radius,
            x + spotlight_radius,
            y + spotlight_radius,
            fill="",
            outline=spotlight_color,
            width=int(3 * alpha),
            tags=("layer:effects", f"showdown_spotlight:{seat_idx}"),
        )

    def _apply_allin_flash(
        self,
        canvas,
        seat_idx: int,
        config: Dict[str, Any],
        x: int,
        y: int,
        pod_width: int,
        pod_height: int,
        current_time: float,
    ) -> None:
        """Apply dramatic flash effect for all-in players."""
        glow_color = config.get("glow", "#B63D3D")
        shimmer_color = config.get("shimmer", "#C9A34E")
        strength = config.get("strength", 1.2)
        flash_ms = config.get("flash_ms", 400)

        # Fast flash cycle
        flash_s = flash_ms / 1000.0
        flash_phase = (current_time % flash_s) / flash_s

        # Sharp flash: bright at 0, dim at 0.5, bright at 1
        flash_intensity = abs(math.sin(flash_phase * math.pi)) * strength

        # Dramatic border flash
        flash_width = int(4 * flash_intensity)
        canvas.create_rectangle(
            x - pod_width // 2 - flash_width,
            y - pod_height // 2 - flash_width,
            x + pod_width // 2 + flash_width,
            y + pod_height // 2 + flash_width,
            fill="",
            outline=glow_color,
            width=flash_width,
            tags=("layer:effects", f"allin_flash:{seat_idx}"),
        )

        # Inner shimmer
        if flash_intensity > 0.5:
            canvas.create_rectangle(
                x - pod_width // 2 + 2,
                y - pod_height // 2 + 2,
                x + pod_width // 2 - 2,
                y + pod_height // 2 - 2,
                fill="",
                outline=shimmer_color,
                width=2,
                tags=("layer:effects", f"allin_shimmer:{seat_idx}"),
            )

    def clear_state_effects(self, canvas, seat_idx: int) -> None:
        """Clear all state effects for a seat."""
        effect_tags = [
            f"active_glow:{seat_idx}",
            f"active_shimmer:{seat_idx}",
            f"folded_overlay:{seat_idx}",
            f"winner_glow_0:{seat_idx}",
            f"winner_glow_1:{seat_idx}",
            f"winner_glow_2:{seat_idx}",
            f"winner_ray_0:{seat_idx}",
            f"winner_ray_1:{seat_idx}",
            f"winner_ray_2:{seat_idx}",
            f"winner_ray_3:{seat_idx}",
            f"winner_ray_4:{seat_idx}",
            f"winner_ray_5:{seat_idx}",
            f"winner_ray_6:{seat_idx}",
            f"winner_ray_7:{seat_idx}",
            f"showdown_spotlight:{seat_idx}",
            f"allin_flash:{seat_idx}",
            f"allin_shimmer:{seat_idx}",
        ]

        for tag in effect_tags:
            try:
                canvas.delete(tag)
            except Exception:
                pass

    def update_animations(self, canvas, seats_data: list, theme_id: str) -> None:
        """
        Update all animated state effects.
        Should be called regularly (e.g., every 50ms) for smooth animations.
        """

        for idx, seat in enumerate(seats_data):
            # Clear old effects first
            self.clear_state_effects(canvas, idx)

            # Determine player state
            player_state = self._determine_player_state(seat)
            if player_state and player_state != "idle":
                # Get seat position (simplified - should use actual layout)
                w = canvas.winfo_width()
                h = canvas.winfo_height()
                if w > 1 and h > 1:
                    # Calculate position (this should match seats.py logic)
                    cx, cy = w // 2, int(h * 0.52)
                    radius = int(min(w, h) * 0.36)
                    count = len(seats_data)

                    if count > 0:
                        theta = -math.pi / 2 + (2 * math.pi * idx) / count
                        x = cx + int(radius * math.cos(theta))
                        y = cy + int(radius * math.sin(theta))

                        pod_width = 110
                        pod_height = 80

                        self.apply_player_state_styling(
                            canvas,
                            idx,
                            player_state,
                            theme_id,
                            x,
                            y,
                            pod_width,
                            pod_height,
                        )

    def _determine_player_state(self, seat: Dict[str, Any]) -> Optional[str]:
        """Determine the primary state for styling purposes."""
        if seat.get("winner", False):
            return "winner"
        elif seat.get("showdown", False):
            return "showdown"
        elif seat.get("all_in", False):
            return "allin"
        elif seat.get("acting", False):
            return "active"
        elif seat.get("folded", False):
            return "folded"
        else:
            return "idle"


class SelectionStyler:
    """Handles selection highlighting for lists and trees."""

    def apply_selection_styles(self, ttk_style, theme_id: str) -> None:
        """Apply theme-driven selection styles to ttk widgets."""
        loader = get_theme_loader()
        theme_config = loader.get_theme_by_id(theme_id)
        palette = theme_config.get("palette", {})

        # Get derived tokens for background
        from .theme_derive import derive_tokens, darken

        tokens = derive_tokens(palette)

        # Configure Treeview with theme colors
        ttk_style.configure(
            "Treeview",
            background=darken(palette["felt"], 0.75),
            fieldbackground=darken(palette["felt"], 0.75),
            foreground=tokens["text.primary"],
        )

        # Selection highlighting
        selection_bg = palette.get("highlight", "#D4AF37")
        selection_fg = palette.get("highlight_text", "#FFFFFF")

        ttk_style.map(
            "Treeview",
            background=[("selected", selection_bg)],
            foreground=[("selected", selection_fg)],
        )


class EmphasisBarStyler:
    """Handles emphasis bar styling with theme-aware colors and textures."""

    def get_emphasis_bar_colors(self, theme_id: str) -> Dict[str, str]:
        """Get emphasis bar color configuration."""
        loader = get_theme_loader()
        defaults = loader.get_defaults()
        theme_config = loader.get_theme_by_id(theme_id)
        palette = theme_config.get("palette", {})

        emphasis_config = defaults.get("emphasis_bar", {})

        # Resolve token references
        from .theme_derive import resolve_token_references

        resolved_config = resolve_token_references(emphasis_config, palette)

        return {
            "bg_top": resolved_config.get("bg_top", palette["felt"]),
            "bg_bottom": resolved_config.get("bg_bottom", palette["rail"]),
            "text": resolved_config.get(
                "text", palette.get("emphasis_text", "#F8E7C9")
            ),
            "accent_text": resolved_config.get("accent_text", palette["raise"]),
            "divider": resolved_config.get("divider", palette["metal"]),
            "texture": resolved_config.get("texture", "velvet_8pct"),
        }

    def render_emphasis_bar(
        self,
        canvas,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        theme_id: str,
        accent_words: list = None,
    ) -> None:
        """
        Render a luxury emphasis bar with theme-aware styling.

        Args:
            canvas: Tkinter canvas
            x, y: Top-left position
            width, height: Bar dimensions
            text: Text to display
            theme_id: Current theme ID
            accent_words: List of words to highlight with accent color
        """
        colors = self.get_emphasis_bar_colors(theme_id)

        # Background gradient simulation (top to bottom)
        bg_top = colors["bg_top"]
        bg_bottom = colors["bg_bottom"]

        # Draw gradient using multiple rectangles
        gradient_steps = 10
        for i in range(gradient_steps):
            y_pos = y + (height * i) // gradient_steps
            step_height = height // gradient_steps

            # Interpolate between top and bottom colors
            from .theme_derive import mix

            t = i / (gradient_steps - 1)
            step_color = mix(bg_top, bg_bottom, t)

            canvas.create_rectangle(
                x,
                y_pos,
                x + width,
                y_pos + step_height,
                fill=step_color,
                outline="",
                tags=("layer:emphasis", "emphasis_bg"),
            )

        # Divider lines
        divider_color = colors["divider"]
        canvas.create_line(
            x,
            y,
            x + width,
            y,
            fill=divider_color,
            width=1,
            tags=("layer:emphasis", "emphasis_top_line"),
        )
        canvas.create_line(
            x,
            y + height,
            x + width,
            y + height,
            fill=divider_color,
            width=1,
            tags=("layer:emphasis", "emphasis_bottom_line"),
        )

        # Text rendering with accent highlighting
        text_color = colors["text"]
        accent_color = colors["accent_text"]

        if accent_words:
            # Split text and highlight accent words
            words = text.split()
            current_x = x + 10  # Left padding
            text_y = y + height // 2

            for word in words:
                color = (
                    accent_color
                    if word.lower() in [w.lower() for w in accent_words]
                    else text_color
                )
                canvas.create_text(
                    current_x,
                    text_y,
                    text=word,
                    anchor="w",
                    font=fonts.get("label", ("Arial", 12, "bold")),
                    fill=color,
                    tags=("layer:emphasis", "emphasis_text"),
                )
                # Approximate word width for spacing
                current_x += len(word) * 8 + 6  # Rough character width + space
        else:
            # Simple centered text
            canvas.create_text(
                x + width // 2,
                y + height // 2,
                text=text,
                font=("Arial", 12, "bold"),
                fill=text_color,
                tags=("layer:emphasis", "emphasis_text"),
            )


# Global instances
_state_styler = None
_selection_styler = None
_emphasis_bar_styler = None


def get_state_styler() -> StateStyler:
    """Get global state styler instance."""
    global _state_styler
    if _state_styler is None:
        _state_styler = StateStyler()
    return _state_styler


def get_selection_styler() -> SelectionStyler:
    """Get global selection styler instance."""
    global _selection_styler
    if _selection_styler is None:
        _selection_styler = SelectionStyler()
    return _selection_styler


def get_emphasis_bar_styler() -> EmphasisBarStyler:
    """Get global emphasis bar styler instance."""
    global _emphasis_bar_styler
    if _emphasis_bar_styler is None:
        _emphasis_bar_styler = EmphasisBarStyler()
    return _emphasis_bar_styler
