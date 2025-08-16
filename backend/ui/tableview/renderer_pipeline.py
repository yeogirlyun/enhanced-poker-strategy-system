class RendererPipeline:
    def __init__(self, canvas_manager, layer_manager, components):
        self.cm = canvas_manager
        self.lm = layer_manager
        self.components = components

    def render_once(self, state):
        c = self.cm.canvas
        w, h = self.cm.size()
        if w <= 1 or h <= 1:
            return
        # Clear only non-pot layers to keep pot persistent between renders
        for tag in ["layer:felt", "layer:seats", "layer:community"]:
            try:
                c.delete(tag)
            except Exception:
                pass
        for component in self.components:
            component.render(state, self.cm, self.lm)
        self.lm.raise_to_policy()


