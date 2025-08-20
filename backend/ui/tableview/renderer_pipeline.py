class RendererPipeline:
    def __init__(self, canvas_manager, layer_manager, components):
        self.cm = canvas_manager
        self.lm = layer_manager
        self.components = components

    def render_once(self, state, force=False):
        # Gate rendering until the canvas is created/sized to avoid small initial artifacts
        if not self.cm.is_ready() and not force:
            self.cm.defer_render(lambda: self.render_once(state, force=True))
            return

        c = self.cm.canvas
        if c is None:
            return

        w, h = self.cm.size()
        if w <= 100 or h <= 100:
            # Skip rendering on invalid size; a deferred render will occur on ready
            print(f"⚠️ Skipping render - invalid dimensions: {w}x{h}")
            return

        # Thorough clear to ensure no remnants from any previous pass
        try:
            c.delete("all")
        except Exception:
            pass

        # Render all components
        for component in self.components:
            try:
                component.render(state, self.cm, self.lm)
            except Exception as e:
                print(f"⚠️ Component {component.__class__.__name__} render error: {e}")

        # Apply layer ordering
        try:
            self.lm.raise_to_policy()
        except Exception as e:
            print(f"⚠️ Layer manager error: {e}")

        print(f"🎨 Rendered poker table: {w}x{h} with {len(self.components)} components")


