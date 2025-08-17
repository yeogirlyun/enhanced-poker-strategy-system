class RendererPipeline:
    def __init__(self, canvas_manager, layer_manager, components):
        self.cm = canvas_manager
        self.lm = layer_manager
        self.components = components

    def render_once(self, state):
        c = self.cm.canvas
        w, h = self.cm.size()
        
        # If canvas is not sized yet, try to get a reasonable default size
        if w <= 1 or h <= 1:
            # Force canvas to update its geometry
            c.update_idletasks()
            w, h = self.cm.size()
            
            # If still no size, use a reasonable default
            if w <= 1 or h <= 1:
                w, h = 800, 600  # Default poker table size
                
        # Clear previous renders (except pot to avoid flickering)
        for tag in ["layer:felt", "layer:seats", "layer:community", "layer:bets", "layer:action", "layer:progress", "layer:info"]:
            try:
                c.delete(tag)
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


