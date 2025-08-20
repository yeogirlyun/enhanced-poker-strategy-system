class LayerManager:
    ORDER = [
        "layer:felt",
        "layer:seats",       # seat backgrounds and player names
        "layer:hole_cards",  # player hole cards (must be above seats)
        "layer:stacks",      # player stacks (must be above hole cards)
        "layer:community",   # community cards and card backs
        "layer:bets",        # bet/call chip stacks (must be above community)
        "layer:pot",         # pot chips and display
        "layer:action",      # acting highlight ring and labels
        "layer:status",      # folded/winner labels
        "layer:overlay",     # overlays and UI elements
        # transient animation/helper tags kept last so they stay visible
        "temp_animation", "flying_chip", "motion_glow", "pot_pulse",
    ]

    def __init__(self, canvas, overlay):
        self.canvas = canvas
        self.overlay = overlay

    def raise_to_policy(self) -> None:
        c = self.canvas
        for tag in self.ORDER:
            try:
                c.tag_raise(tag)
            except Exception:
                pass
        if self.overlay is not None:
            try:
                self.overlay.lift(self.canvas)
            except Exception:
                pass


