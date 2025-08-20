# EffectBus Patches - ARCHITECTURE COMPLIANT VERSION

**CRITICAL**: This patch removes threading violations and uses proper event-driven scheduling.

```python
# Sound durations in milliseconds for gating
EFFECT_DURATIONS = {
    # Core actions
    "BET": 200,
    "RAISE": 200,
    "CALL": 200,
    "CHECK": 150,
    "FOLD": 150,
    "ALL_IN": 300,
    
    # Blinds & chips
    "POST_BLIND": 150,
    "POST_SMALL_BLIND": 150, 
    "POST_BIG_BLIND": 150,
    "CHIP_BET": 200,
    "CHIP_COLLECT": 250,
    
    # Deals
    "DEAL_HOLE": 200,
    "DEAL_BOARD": 200,
    "DEAL_FLOP": 400,
    "DEAL_TURN": 200,
    "DEAL_RIVER": 200,
    
    # End of hand
    "SHOWDOWN": 500,
    "END_HAND": 500,
    "POT_SPLIT": 300
}

def play_effect(self, effect_type: str, data: Optional[Dict] = None) -> None:
    """Play a sound effect and trigger animation if applicable."""
    if not self.enabled:
        return
        
    if data is None:
        data = {}
        
    # Get effect duration for gating
    duration = EFFECT_DURATIONS.get(effect_type, 200)
    
    # Create unique effect ID
    effect_id = f"{effect_type}_{self.next_id}"
    self.next_id += 1
    
    # Create effect record
    effect = Effect(
        type=effect_type,
        id=effect_id,
        ms=duration,
        args=data
    )
    
    # Add to active effects
    self.effects.append(effect)
    
    # Play sound if available
    sound_file = self.sound_mapping.get(effect_type)
    if sound_file and self.sound:
        try:
            self.sound.play_sound(sound_file)
        except Exception as e:
            print(f"⚠️ Sound failed but continuing: {e}")
    
    # Publish animation event
    if self.event_bus:
        # Map actions to animations
        if effect_type in ["BET", "RAISE", "CALL", "POST_BLIND"]:
            self.event_bus.publish(
                "effect_bus:animate",
                {"name": "chips_to_pot", "data": data}
            )
        elif effect_type in ["SHOWDOWN", "END_HAND"]:
            self.event_bus.publish(
                "effect_bus:animate", 
                {"name": "pot_to_winner", "data": data}
            )
            # Show winner banner
            winner = data.get("winner", {})
            msg = f"{winner.get('name', 'Unknown')} wins {data.get('amount', 0)}"
            self.event_bus.publish(
                "effect_bus:banner_show",
                {"text": msg, "type": "success"}
            )
    
    # Notify director of gate
    if self.director:
        self.director.gate_start()
        
        # Schedule gate end via GameDirector - NO THREADING
        if hasattr(self.director, 'schedule'):
            self.director.schedule(duration, {
                "type": "EFFECT_COMPLETE",
                "effect_id": effect_id,
                "component": "effect_bus"
            })
        else:
            # Fallback: publish event for manual handling
            if self.event_bus:
                self.event_bus.publish("effect_bus:schedule_complete", {
                    "delay_ms": duration,
                    "effect_id": effect_id
                })
```

**Key Changes Made:**
1. ❌ **REMOVED**: `threading.Timer` usage (architecture violation)
2. ✅ **ADDED**: Event-driven scheduling via GameDirector
3. ✅ **MAINTAINED**: Single-threaded, event-driven architecture
4. ✅ **COMPLIANT**: All timing controlled by GameDirector
5. ✅ **SAFE**: No blocking operations or threading

**Architecture Compliance:**
- ✅ Single-threaded
- ✅ Event-driven only
- ✅ GameDirector controls timing
- ✅ No threading/timers for game logic
- ✅ All timing via coordinator
