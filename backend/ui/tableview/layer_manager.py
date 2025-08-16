class LayerManager:
    ORDER = [
        "layer:felt",
        "layer:seats",
        "layer:community",
        "layer:pot",
        "layer:overlay",
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


