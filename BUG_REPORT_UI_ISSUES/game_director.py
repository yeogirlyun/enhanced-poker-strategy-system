# Relevant source code from game_director.py

...existing code...

    def notify_sound_complete(self, event_data=None):
        """Called when sound effect completes."""
        if event_data is None:
            event_data = {}
        print(f"🎬 GameDirector: Sound complete: {event_data.get('id', 'unknown')}")
        self.gate_end()

    def notify_animation_complete(self, event_data=None):
        """Called when animation effect completes."""
        if event_data is None:
            event_data = {}
        print(f"🎬 GameDirector: Animation complete: {event_data.get('name', 'unknown')}")
        self.gate_end()

...existing code...
