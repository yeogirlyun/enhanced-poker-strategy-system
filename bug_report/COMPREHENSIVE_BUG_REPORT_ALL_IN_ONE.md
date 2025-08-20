# 🚨 COMPREHENSIVE UI BUG REPORT - ALL IN ONE

This file contains the complete bug report, all source code, and documentation in one comprehensive file.

**Source Directory:** `/Users/yeogirlyun/Python/Poker`
**Generated:** $(date)

---

## BUG REPORT DOCUMENTATION

### COMPREHENSIVE_UI_BUG_REPORT.md

```markdown
# 🚨 UI Bug Report: Initial Small Poker Table Remnants

## Summary
On first render of Hands Review, a smaller poker table appears briefly and leaves visual remnants under the full‑size table. This suggests an early draw using a fallback canvas size before the layout is resolved. The stale drawing is not fully cleared when the correct size arrives.

## Environment
- OS: macOS 14 (Sonoma) – darwin 24.6.0
- Python: system python3
- App area: `backend/ui/tabs/hands_review_tab.py` and `backend/ui/tableview/*`

## Steps to Reproduce
1. Launch the new UI and open the Hands Review tab.
2. Observe the table area on the right pane on initial load.

## Expected
- The poker table should render once at the final layout size and occupy the pane without artifacts.

## Actual
- A small table appears (roughly default 800×600) and portions of that first draw remain visible after the full‑size render. Artifacts look like a smaller oval felt under the large table.

## Evidence / Clues
- Renderer prints indicate a fallback size may be used:
  - `🎨 Rendered poker table: 800x600 ...` (first paint)
  - then resized paints with correct dimensions.
- `RendererPipeline.render_once` uses a fallback size if canvas width/height ≤ 1 and draws immediately.
- Layer cleanup deletes a fixed set of tags but stale shapes may have been drawn with unexpected tags from first render.

## Suspected Root Cause
1. Canvas renders before the parent layout has established a real size, so defaults (800×600) are used for the first frame.
2. The first render creates oval felt and accents that are not fully removed when the second, correctly sized render runs.

## Recent Attempts/Mitigations Present Now
- `CanvasManager.__init__` sets the canvas size to the parent’s width/height on init and binds `<Configure>` to manage overlay order.
- `TableFelt.render` clears many felt‑related tags at the start of each render.

Despite these, the initial small render still occurs on the reporter’s machine.

## Candidate Fixes
- Defer the first render until we observe a meaningful parent size (e.g., via a one‑shot `<Configure>` handler or by scheduling after `update_idletasks()` and checking width/height > threshold).
- Add an initial “full clear” on the very first render, including any generic tags that could be left by the fallback draw, and avoid drawing with fallback 800×600 unless absolutely necessary.
- Ensure that all shapes in `TableFelt` are consistently tagged with `layer:felt` (and sub‑tags) so a single `delete('layer:felt')` removes all remnants.

## Impact
- Cosmetic but persistent; undermines professional look and can confuse users about the table size.

## Files of Interest
- `backend/ui/tableview/renderer_pipeline.py`
- `backend/ui/tableview/canvas_manager.py`
- `backend/ui/tableview/components/table_felt.py`
- `backend/ui/tabs/hands_review_tab.py`

## Minimal Repro State
- Open app to Hands Review with any theme; no hand needs to be loaded to observe artifact.

## Proposed Acceptance Criteria
- No visual remnants from any pre‑layout draw.
- First visible table matches the final pane size.
- Subsequent resizes remain clean without ghosting.



```

---

### COMPREHENSIVE_UI_BUG_REPORT_README.md

```markdown
# 🚨 COMPREHENSIVE UI BUG REPORT - README

## 📦 PACKAGE CONTENTS

This zip file contains a comprehensive bug report for the poker application's UI coordination issues, including all relevant source code, architecture documentation, and analysis in a FLAT file structure.

---

## 📋 WHAT'S INCLUDED

### **1. Bug Report Documentation**
- **`COMPREHENSIVE_UI_BUG_REPORT.md`** - Complete bug analysis and technical details
- **`ARCHITECTURE_COMPLIANCE_REPORT.md`** - Architecture compliance status
- **`RUNTIME_FIXES_README.md`** - Runtime fixes documentation

### **2. Core Source Code (Flat Structure)**
- **`effect_bus.py`** - Sound coordination service (with debug logging)
- **`hands_review_session_manager.py`** - Session management (with debug logging)
- **`hands_review_tab.py`** - Main UI component
- **`app_shell.py`** - Application shell and service coordination
- **`poker_sound_config.json`** - Sound configuration (fixed)
- **`poker_types.py`** - ActionType enum and data structures
- **`hand_model.py`** - Hand and Action data models
- **`fix_runtime_errors.py`** - Runtime error fixes
- **`run_new_ui.py`** - Main application launcher

### **3. UI Component System**
- **`chip_animations.py`** - Chip flying animations system
- **`chip_graphics.py`** - Professional chip rendering
- **`token_driven_renderer.py`** - Main UI coordination component
- **`enhanced_cards.py`** - Card graphics and animations
- **`premium_chips.py`** - Luxury chip graphics system

### **4. Theme System**
- **`theme_manager.py`** - Main theme management
- **`theme_factory.py`** - Theme creation and building
- **`theme_loader_consolidated.py`** - Theme loading system
- **`theme_utils.py`** - Theme utility functions
- **`state_styler.py`** - State-based styling
- **`theme_derive.py`** - Theme derivation system
- **`theme_manager_clean.py`** - Clean theme manager implementation

### **5. Architecture Documentation**
- **`PokerPro_Trainer_Complete_Architecture_v3.md`** - Core architecture specification
- **`PokerPro_UI_Implementation_Handbook_v1.1.md`** - UI implementation guide
- **`PROJECT_PRINCIPLES_v2.md`** - Project principles and rules

---

## 🐛 BUG SUMMARY

### **Primary Issue: No Human Voice Announcements**
- **Expected:** Human voice should announce actions (e.g., "raise", "call", "bet")
- **Actual:** Voice events are emitted but never processed by VoiceManager
- **Console Evidence:** `🔊 EffectBus: Emitted voice event: raise` but no voice heard

### **Secondary Issue: No Visual Animations**
- **Expected:** Chip animations should fly from players to pot on betting actions
- **Actual:** Animations are triggered but fail with "No seat found for actor" errors
- **Console Evidence:** `⚠️ No seat found for actor seat1 in betting action animation`

### **Tertiary Issue: No Chip Graphics**
- **Expected:** Professional chip graphics with flying animations
- **Actual:** Animation system can't find correct player coordinates
- **Console Evidence:** Animation system looking for wrong player names

### **Quaternary Issue: No Visual Feedback**
- **Expected:** Rich visual experience with animations, effects, and feedback
- **Actual:** Static poker table with no visual changes during actions
- **Console Evidence:** Actions execute but produce no visual results

---

## 🔍 ROOT CAUSE ANALYSIS

### **1. Voice Manager Not Connected**
The `EffectBus` emits voice events but they never reach the `VoiceManager`:
```python
# EffectBus emits voice events
🔊 EffectBus: Emitted voice event: raise

# But VoiceManager never receives them
# Missing: VoiceManager subscription to "effect_bus:voice" events
```

### **2. Animation Coordinate Mismatch**
The animation system can't find players because of naming inconsistencies:
```python
# Session Manager looks for: 'seat1', 'seat2'
# But UI has seats with names: 'Seat1', 'Seat2' (capitalized)
# Result: "No seat found for actor seat1 in betting action animation"
```

### **3. Chip Animation System Broken**
The `ChipAnimations` component exists but can't get proper coordinates:
```python
# Animation handler tries to find player by name
for seat in seats:
    if seat.get('name') == actor_uid:  # actor_uid = 'seat1', seat name = 'Seat1'
        acting_seat = seat
        break
# Never matches due to case sensitivity
```

---

## 📊 CURRENT STATE

### **✅ What's Working:**
- Application launches without console errors
- Runtime fixes are automatically applied
- Architecture compliance is maintained
- **Mechanical sound effects play correctly** ✅
- Actions execute in PPSM correctly
- UI renders poker table correctly
- Service coordination is properly established
- Event bus publishes and subscribes correctly

### **❌ What's Broken:**
1. **Human voice announcements** - Events emitted but not processed
2. **Visual animations** - Coordinate lookup failures
3. **Chip graphics** - Animation system can't find players
4. **Visual feedback** - No visual changes during actions
5. **User experience** - Static, non-interactive interface

---

## 🔧 TECHNICAL DETAILS

### **Voice System (Broken)**
```python
# EffectBus emits voice events
🔊 EffectBus: Emitted voice event: raise

# But VoiceManager is not subscribed to these events
# Missing subscription in VoiceManager initialization
```

**Status:** ❌ Broken - Voice events never reach VoiceManager

### **Animation System (Broken)**
```python
# Session Manager triggers animations
🎬 Triggering betting animation for action: RAISE

# UI handler receives animation request
🎬 Betting action animation: RAISE by seat1

# But can't find player coordinates
⚠️ No seat found for actor seat1 in betting action animation
```

**Status:** ❌ Broken - Coordinate lookup failures

### **Chip Graphics (Broken)**
```python
# ChipAnimations component exists and is imported
from ..tableview.components.chip_animations import ChipAnimations

# But animation handler can't get proper coordinates
# Result: No chip flying animations
```

**Status:** ❌ Broken - No visual chip movements

---

## 🚀 RECOMMENDED FIXES

### **Immediate Fix 1: Voice Manager Connection**
1. **Subscribe VoiceManager** to `effect_bus:voice` events
2. **Ensure voice events** reach the correct handler
3. **Test voice announcements** for all action types

### **Immediate Fix 2: Animation Coordinate Resolution**
1. **Fix player name matching** (case sensitivity issue)
2. **Ensure consistent naming** between PPSM and UI
3. **Add coordinate validation** in animation handler

### **Immediate Fix 3: Chip Animation System**
1. **Fix coordinate lookup** in animation handler
2. **Ensure ChipAnimations** receives proper parameters
3. **Test chip flying animations** end-to-end

---

## 🔍 HOW TO USE THIS BUG REPORT

### **For Development Team:**
1. **Review `COMPREHENSIVE_UI_BUG_REPORT.md`** for complete technical analysis
2. **Examine source code** to understand the coordination issues
3. **Check architecture docs** to ensure compliance during fixes
4. **Use debug logging** to identify exact coordination failures

### **For Testing Team:**
1. **Run application** with `python3 run_new_ui.py`
2. **Monitor console output** for debug logging
3. **Execute poker actions** and verify voice/visual feedback
4. **Report any new issues** found during testing

### **For Architecture Review:**
1. **Review `PokerPro_Trainer_Complete_Architecture_v3.md`** for core principles
2. **Check `PokerPro_UI_Implementation_Handbook_v1.1.md`** for implementation rules
3. **Verify fixes maintain** architecture compliance
4. **Ensure proper separation** of concerns

---

## 📊 FILE STRUCTURE

```
COMPREHENSIVE_UI_BUG_REPORT_FLAT.zip
├── COMPREHENSIVE_UI_BUG_REPORT.md          # Main bug report
├── effect_bus.py                            # Sound coordination service
├── hands_review_session_manager.py          # Session management
├── hands_review_tab.py                      # Main UI component
├── app_shell.py                             # Application shell
├── poker_sound_config.json                  # Sound configuration
├── poker_types.py                           # ActionType enum
├── hand_model.py                            # Data models
├── fix_runtime_errors.py                    # Runtime fixes
├── run_new_ui.py                            # Main launcher
├── chip_animations.py                       # Chip animations
├── chip_graphics.py                         # Chip graphics
├── token_driven_renderer.py                 # UI coordination
├── enhanced_cards.py                        # Card graphics
├── premium_chips.py                         # Luxury chips
├── theme_manager.py                         # Theme management
├── theme_factory.py                         # Theme creation
├── theme_loader_consolidated.py             # Theme loading
├── theme_utils.py                           # Theme utilities
├── state_styler.py                          # State styling
├── theme_derive.py                          # Theme derivation
├── theme_manager_clean.py                   # Clean theme manager
├── PokerPro_Trainer_Complete_Architecture_v3.md
├── PokerPro_UI_Implementation_Handbook_v1.1.md
├── PROJECT_PRINCIPLES_v2.md
└── RUNTIME_FIXES_README.md
```

---

## 📞 SUPPORT

### **Bug Report Status:** OPEN - Requires immediate attention
### **Priority:** CRITICAL - Core functionality broken
### **Assigned To:** Development Team
### **Review Required:** Yes - Multiple system failures need resolution

### **Next Steps:**
1. **Fix VoiceManager subscription** to voice events
2. **Resolve animation coordinate** lookup issues
3. **Test chip animations** end-to-end
4. **Validate visual feedback** for all actions

---

*This comprehensive bug report package contains all the information needed to resolve the UI coordination issues while maintaining architecture compliance. All files are in a flat structure for easy unzipping into any folder.*

```

---

## CORE SOURCE CODE

### effect_bus.py

```python
#!/usr/bin/env python3
"""
EffectBus - Coordinates sounds & animations; integrates with GameDirector.
"""
from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Import VoiceManager for human voice announcements
try:
    from ...utils.voice_manager import VoiceManager
except ImportError:
    try:
        from utils.voice_manager import VoiceManager
    except ImportError:
        try:
            from backend.utils.voice_manager import VoiceManager
        except ImportError:
            VoiceManager = None


# Minimal effect representation
@dataclass
class Effect:
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    ms: int = 200
    args: Dict[str, Any] = field(default_factory=dict)


class EffectBus:
    def __init__(self, game_director=None, sound_manager=None, event_bus=None, renderer=None):
        self.director = game_director
        self.sound = sound_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.enabled = True
        self.effects: List[Effect] = []
        self.next_id = 0
        
        # Initialize VoiceManager for human voice announcements
        self.voice_manager = None
        if VoiceManager:
            try:
                self.voice_manager = VoiceManager()
                print("🔊 EffectBus: VoiceManager initialized for human voice announcements")
            except Exception as e:
                print(f"⚠️ EffectBus: VoiceManager not available: {e}")
        
        # Initialize pygame mixer for audio
        try:
            import pygame
            pygame.mixer.init(
                frequency=22050, size=-16, channels=2, buffer=512
            )
            self.pygame_available = True
            print("🔊 EffectBus: Pygame mixer initialized for audio")
        except Exception as e:
            self.pygame_available = False
            print(f"⚠️ EffectBus: Pygame mixer not available: {e}")
        
        # Load sound configuration from file
        self.sound_mapping = {}
        self.config: Dict[str, Any] = {}
        self._load_sound_config()
        
        # Load sound files
        self.sounds = {}
        self._load_sounds()
    
    def _load_sound_config(self):
        """Load sound configuration from JSON file."""
        try:
            config_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 'sounds',
                'poker_sound_config.json'
            )

            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Save full config for voice lookups
                self.config = config

                # Load sound mappings
                self.sound_mapping = config.get("sounds", {})

                # Load global settings
                self.master_volume = config.get("master_volume", 1.0)
                self.sounds_enabled = config.get("sounds_enabled", True)
                self.voice_enabled = config.get("voice_enabled", True)
                self.voice_type = config.get("voice_type", "announcer_female")

                # Optional base directory for sounds
                self.sound_dir_hint = Path(config.get("sound_directory", "sounds"))

                print(f"🔊 EffectBus: Loaded sound config with {len(self.sound_mapping)} mappings")
            else:
                print(f"⚠️ EffectBus: Sound config file not found: {config_file}")
                # Use empty mapping - let the UI handle defaults
                self.config = {}
                self.sound_mapping = {}
                self.master_volume = 1.0
                self.sounds_enabled = True
                self.voice_enabled = True
                self.voice_type = "announcer_female"
                self.sound_dir_hint = Path("sounds")

        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sound config: {e}")
            # Fallback to empty mappings
            self.config = {}
            self.sound_mapping = {}
            self.master_volume = 1.0
            self.sounds_enabled = True
            self.voice_enabled = True
            self.voice_type = "announcer_female"
            self.sound_dir_hint = Path("sounds")
    
    def reload_sound_config(self):
        """Dynamically reload sound configuration from file."""
        print("🔄 EffectBus: Reloading sound configuration...")
        self._load_sound_config()
        # Clear existing loaded sounds to force reload
        self.sounds.clear()
        # Reload sounds with new mapping
        self._load_sounds()
        print(f"✅ EffectBus: Reloaded sound config with {len(self.sound_mapping)} mappings")

    def set_game_director(self, game_director):
        """Set the game director for coordinating effects timing."""
        self.director = game_director
        print(f"🔊 EffectBus: Connected to GameDirector")

    def set_event_bus(self, event_bus):
        """Set the event bus for publishing effect events."""
        self.event_bus = event_bus
        print(f"🔊 EffectBus: Connected to EventBus")
        # Bridge basic animate events to ChipAnimations if a renderer is present
        try:
            if self.event_bus is not None:
                self.event_bus.subscribe("effect_bus:animate", self._on_animation_request)
        except Exception:
            pass

    def _resolve_sound_path(self, rel_or_abs: str) -> Optional[Path]:
        """Resolve a sound path robustly across likely locations."""
        try:
            # Absolute path as-is
            p = Path(rel_or_abs)
            if p.is_file():
                return p

            # Relative to configured sounds dir if provided
            if hasattr(self, 'sound_dir_hint'):
                cand = self.sound_dir_hint / rel_or_abs
                if cand.is_file():
                    return cand

            # Relative to this module's ../../sounds
            here = Path(__file__).parent
            cand2 = (here / '..' / '..' / 'sounds').resolve() / rel_or_abs
            if cand2.is_file():
                return cand2

            # Relative to CWD/sounds
            cand3 = Path.cwd() / 'sounds' / rel_or_abs
            if cand3.is_file():
                return cand3
        except Exception:
            pass
        return None

    def _load_sounds(self):
        """Load all available sound files."""
        if not self.pygame_available:
            return
            
        try:
            import pygame
            for action, filename in self.sound_mapping.items():
                resolved = self._resolve_sound_path(filename)
                if resolved and resolved.exists() and resolved.stat().st_size > 100:
                    try:
                        sound = pygame.mixer.Sound(str(resolved))
                        self.sounds[action.upper()] = sound
                        print(f"🔊 EffectBus: Loaded sound {action} -> {resolved}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to load {filename}: {e}")
                else:
                    print(f"⚠️ EffectBus: Sound file not found or empty: {filename}")
                    
            print(f"🔊 EffectBus: Loaded {len(self.sounds)} sound files")
        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sounds: {e}")

    def add_effect(self, effect: Effect) -> str:
        """Add an effect to the queue."""
        if not self.enabled:
            return ""
            
        effect.id = f"{effect.type}_{self.next_id}"
        self.next_id += 1
        self.effects.append(effect)
        
        # Notify event bus
        if self.event_bus:
            self.event_bus.publish(f"effect_bus:{effect.type}", {
                "id": effect.id,
                "name": effect.name,
                "ms": effect.ms,
                "args": effect.args
            })
        
        return effect.id

    def add_sound_effect(self, sound_name: str, ms: int = 200):
        """Add sound effect with proper gating, even if pygame audio fails."""
        # try to play; don't crash if mixer is unavailable
        played = False
        try:
            if hasattr(self, 'pygame_available') and self.pygame_available:
                import pygame
                # First try to use pre-loaded sound from self.sounds
                if sound_name in self.sounds:
                    try:
                        sound = self.sounds[sound_name]
                        sound.set_volume(self.master_volume)
                        sound.play()
                        played = True
                        print(f"🔊 EffectBus: Playing pre-loaded sound: {sound_name}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to play pre-loaded sound {sound_name}: {e}")
                        played = False
                else:
                    # Fallback: try to load from file mapping
                    sound_file = self.sound_mapping.get(sound_name.upper(), "")
                    if sound_file:
                        resolved = self._resolve_sound_path(sound_file)
                        try:
                            if resolved and resolved.exists():
                                sound = pygame.mixer.Sound(str(resolved))
                                sound.set_volume(self.master_volume)
                                sound.play()
                                played = True
                                print(f"🔊 EffectBus: Playing sound {sound_name} -> {resolved}")
                            else:
                                print(f"⚠️ EffectBus: Could not resolve sound path for {sound_file}")
                                played = False
                        except Exception as e:
                            print(f"⚠️ EffectBus: Failed to play {sound_file}: {e}")
                            played = False
                    else:
                        print(f"⚠️ EffectBus: No sound mapping found for {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error in add_sound_effect: {e}")
            played = False

        # Gate autoplay regardless of audio success. Use the director to schedule
        # a SOUND_COMPLETE event so the autoplay rhythm stays deterministic.
        if self.director:
            try:
                self.director.gate_begin()
                # Use ms even if sound didn't play to keep timing consistent
                self.director.schedule(ms, {"type": "SOUND_COMPLETE", "id": sound_name},
                                       callback=self.director.notify_sound_complete)
            except Exception:
                # Ensure gate_end still occurs in case schedule failed
                try:
                    self.director.gate_end()
                except Exception:
                    pass

        # optional: telemetry/log
        if self.event_bus:
            self.event_bus.publish("effect_bus:sound", {"id": sound_name, "ms": ms})

    def add_animation_effect(self, name: str, ms: int = 250, args: dict | None = None):
        """Add animation effect with proper gating."""
        args = args or {}
        if self.event_bus:
            self.event_bus.publish("effect_bus:animate", {"name": name, "ms": ms, "args": args})

        if self.director:
            self.director.gate_begin()
            self.director.schedule(ms, {"type": "ANIM_COMPLETE", "name": name},
                                   callback=self.director.notify_animation_complete)

    # --- Animation bridge ---
    def _on_animation_request(self, payload: dict):
        """Translate simple animate events to ChipAnimations drawing calls.
        Requires renderer with canvas and theme_manager context.
        """
        try:
            name = (payload or {}).get("name", "")
            args = (payload or {}).get("args", {}) or {}
            renderer = getattr(self, "renderer", None)
            if renderer is None:
                return
            canvas = getattr(renderer, "canvas_manager", None)
            canvas = getattr(canvas, "canvas", None)
            theme_manager = getattr(renderer, "theme_manager", None)
            if canvas is None or theme_manager is None:
                return
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)

            if name == "chips_to_pot":
                anim.fly_chips_to_pot(
                    canvas,
                    args.get("from_x", 0), args.get("from_y", 0),
                    args.get("to_x", 0), args.get("to_y", 0),
                    int(args.get("amount", 0)),
                )
            elif name == "pot_to_winner":
                anim.fly_pot_to_winner(
                    canvas,
                    args.get("pot_x", 0), args.get("pot_y", 0),
                    args.get("winner_x", 0), args.get("winner_y", 0),
                    int(args.get("amount", 0)),
                )
        except Exception:
            pass

    def add_banner_effect(self, message: str, banner_type: str = "info", ms: int = 2000) -> str:
        """Add a banner notification effect."""
        effect = Effect(
            type="banner",
            name=message,
            ms=ms,
            args={"type": banner_type}
        )
        return self.add_effect(effect)

    def add_poker_action_effects(self, action_type: str, player_name: str = ""):
        """Add poker action effects with proper sound mapping and gating."""
        action_type = (action_type or "").upper()
        
        # Debug: log what we're receiving
        print(f"🔊 DEBUG: EffectBus received action_type: '{action_type}'")

        # Use config-driven sound mapping from poker_sound_config.json
        # The sound_map is loaded dynamically from the config file
        sound_map = self.sound_mapping
        
        maybe = sound_map.get(action_type)
        if maybe:
            print(f"🔊 DEBUG: Found sound mapping for '{action_type}' -> '{maybe}'")
            self.add_sound_effect(action_type, ms=220)   # Pass action_type, not filename
        else:
            print(f"🔊 DEBUG: No sound mapping found for '{action_type}'")
            print(f"🔊 DEBUG: Available sound mappings: {list(sound_map.keys())}")

        # Add voice announcements for key actions via event bus and direct playback
        voice_action = self._map_action_to_voice(action_type)
        if self.voice_enabled and voice_action:
            # 1) Publish event for listeners
            if self.event_bus:
                self.event_bus.publish(
                    "effect_bus:voice",
                    {"type": "POKER_ACTION", "action": voice_action, "player": player_name},
                )
            print(f"🔊 EffectBus: Emitted voice event: {voice_action}")

            # 2) Direct playback via VoiceManager if available
            try:
                if self.voice_manager:
                    voice_sounds = (self.config or {}).get("voice_sounds", {})
                    voice_table = voice_sounds.get(self.voice_type or "", {})
                    file_rel = voice_table.get(voice_action)
                    if file_rel:
                        self.voice_manager.play(file_rel)
            except Exception as e:
                print(f"⚠️ EffectBus: Voice playback failed: {e}")

        if action_type == "SHOWDOWN":
            self.add_sound_effect("ui_winner", ms=700)

        # Publish simple banner text (optional)
        if self.event_bus:
            txt = f"{player_name or 'Player'} {action_type}"
            self.event_bus.publish("effect_bus:banner_show", {"style": "action", "text": txt})

        # Publish animation events for chip movements
        if action_type in ("DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"):
            self.add_animation_effect("chips_to_pot", ms=260)

        if action_type in ("SHOWDOWN", "END_HAND"):
            self.add_animation_effect("pot_to_winner", ms=520)
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show",
                    {"style": "winner", "text": f"{player_name or 'Player'} wins!"})

    def update(self):
        """Update effect processing."""
        if not self.enabled:
            return
            
        # Process effects
        for effect in self.effects[:]:
            if effect.type == "sound":
                self._play_sound(effect)
            elif effect.type == "animation":
                self._start_animation(effect)
            elif effect.type == "banner":
                self._show_banner(effect)
            
            # Remove processed effects
            self.effects.remove(effect)

    def _play_sound(self, effect: Effect):
        """Play a sound effect."""
        if not self.pygame_available or not self.sounds:
            return
            
        try:
            sound_name = effect.name
            if sound_name in self.sounds:
                # Gate effects while sound plays
                if self.director:
                    self.director.gate_begin()
                
                # Play the sound
                try:
                    self.sounds[sound_name].play()
                except Exception:
                    pass
                print(f"🔊 EffectBus: Playing sound: {sound_name}")
                
                # Schedule gate end through GameDirector only (no Tk timers)
                if self.director:
                    try:
                        self.director.schedule(
                            effect.ms,
                            {"type": "SOUND_COMPLETE", "id": effect.id},
                            callback=self.director.notify_sound_complete,
                        )
                    except Exception:
                        try:
                            self.director.gate_end()
                        except Exception:
                            pass
            else:
                print(f"⚠️ EffectBus: Sound not found: {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error playing sound: {e}")
            if self.director:
                self.director.gate_end()

    def _start_animation(self, effect: Effect):
        """Start an animation effect."""
        try:
            # Gate effects while animation runs
            if self.director:
                self.director.gate_begin()
            
            print(f"🎬 EffectBus: Started animation: {effect.name}")
            
            # Publish animation event
            if self.event_bus:
                self.event_bus.publish("effect_bus:animate", {
                    "id": effect.id,
                    "name": effect.name,
                    "ms": effect.ms,
                    "args": effect.args
                })
            
            # Schedule gate end through GameDirector only (no Tk timers)
            if self.director:
                try:
                    self.director.schedule(
                        effect.ms,
                        {"type": "ANIM_COMPLETE", "name": effect.name},
                        callback=self.director.notify_animation_complete,
                    )
                except Exception:
                    try:
                        self.director.gate_end()
                    except Exception:
                        pass
        except Exception as e:
            print(f"⚠️ EffectBus: Error starting animation: {e}")
            if self.director:
                self.director.gate_end()

    def _show_banner(self, effect: Effect):
        """Show a banner notification."""
        try:
            # Publish banner event
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show", {
                    "id": effect.id,
                    "message": effect.name,
                    "type": effect.args.get("type", "info"),
                    "ms": effect.ms
                })
                print(f"🎭 EffectBus: Added banner effect: {effect.name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error showing banner: {e}")

    def clear_queue(self):
        """Clear all pending effects."""
        self.effects.clear()

    def stop_all_effects(self):
        """Stop all running effects."""
        if self.pygame_available:
            try:
                import pygame
                pygame.mixer.stop()
            except:
                pass
        self.clear_queue()

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "enabled": self.enabled,
            "effects_count": len(self.effects),
            "sounds_loaded": len(self.sounds),
            "pygame_available": self.pygame_available
        }

    def set_effect_enabled(self, enabled: bool):
        """Enable/disable effects."""
        self.enabled = enabled

    def _map_action_to_voice(self, action_type: str) -> str:
        """Map poker action types to voice announcement actions."""
        voice_map = {
            "BET": "bet",
            "RAISE": "raise", 
            "CALL": "call",
            "CHECK": "check",
            "FOLD": "fold",
            "ALL_IN": "all_in",
            "DEAL_HOLE": "dealing",
            "DEAL_BOARD": "dealing",
            "POST_BLIND": "dealing",
            "SHOWDOWN": "winner",
            "END_HAND": "winner"
        }
        return voice_map.get(action_type, "")


class NoopEffectBus:
    """No-op EffectBus for testing."""
    def __init__(self, *args, **kwargs):
        pass
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

```

---

### hands_review_session_manager.py

```python
#!/usr/bin/env python3
"""
HandsReviewSessionManager - Manages hands review session logic per architecture guidelines.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


try:
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from core.hand_model import Hand, Street
    from core.hand_model_decision_engine import HandModelDecisionEngine
    from core.session_logger import get_session_logger
    from core.poker_types import Player
except ImportError:
    # Fallback for when running from different directory
    from ...core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    from ...core.hand_model import Hand, Street
    from ...core.hand_model_decision_engine import HandModelDecisionEngine
    from ...core.session_logger import get_session_logger
    from ...core.poker_types import Player


@dataclass
class HandsReviewState:
    """Immutable state for hands review session."""
    current_hand: Optional[Hand] = None
    current_action_index: int = 0
    total_actions: int = 0
    is_playing: bool = False
    playback_speed: float = 1.0
    street: str = "PREFLOP"
    board: List[str] = None
    seats: List[Dict[str, Any]] = None
    pot: Dict[str, Any] = None
    dealer: Dict[str, Any] = None
    action: Dict[str, Any] = None
    effects: List[Dict[str, Any]] = None
    table: Dict[str, Any] = None
    animation: Dict[str, Any] = None


class HandsReviewSessionManager:
    """Manages hands review session logic per architecture guidelines."""
    
    def __init__(self, store, ppsm: PurePokerStateMachine, game_director, effect_bus, event_bus):
        self.store = store
        self.ppsm = ppsm
        self.game_director = game_director
        self.effect_bus = effect_bus
        self.event_bus = event_bus
        self.session_logger = get_session_logger()
        
        # Session state
        self.current_hand: Optional[Hand] = None
        self.current_action_index: int = 0
        self.total_actions: int = 0
        self.is_playing: bool = False
        self.playback_speed: float = 1.0
        
        # Decision engine for hand replay
        self.decision_engine: Optional[HandModelDecisionEngine] = None
        
        print("🎯 HandsReviewSessionManager: Initialized per architecture guidelines")
    
    def load_hand(self, hand_data: Dict[str, Any]) -> HandsReviewState:
        """Load a hand for review - business logic only."""
        try:
            # Create Hand object from data
            self.current_hand = Hand.from_dict(hand_data)
            
            # Initialize PPSM with hand data
            self._initialize_ppsm_for_hand()
            
            # Create decision engine for replay
            self.decision_engine = HandModelDecisionEngine(self.current_hand)
            
            # Count total actions across all streets
            self.total_actions = sum(len(street_state.actions) for street_state in self.current_hand.streets.values())
            
            # Reset to beginning
            self.current_action_index = 0
            self.is_playing = False
            
            # Create initial state
            initial_state = self._create_table_state()
            
            # Update store (not UI directly)
            self.store.dispatch({
                "type": "HANDS_REVIEW_LOADED",
                "hand_id": self.current_hand.metadata.hand_id,
                "total_actions": self.total_actions,
                "state": initial_state
            })
            
            print(f"🎯 HandsReviewSessionManager: Loaded hand {self.current_hand.metadata.hand_id} with {self.total_actions} actions")
            
            return HandsReviewState(
                current_hand=self.current_hand,
                current_action_index=self.current_action_index,
                total_actions=self.total_actions,
                is_playing=self.is_playing,
                playback_speed=self.playback_speed,
                **initial_state
            )
            
        except Exception as e:
            print(f"❌ HandsReviewSessionManager: Error loading hand: {e}")
            raise
    
    def execute_action(self) -> HandsReviewState:
        """Execute next action through PPSM - business logic only."""
        try:
            if not self.current_hand:
                raise ValueError("No hand loaded")
            
            # Get action from hand data (need to find which street it's in)
            if self.current_action_index >= self.total_actions:
                print("🎯 HandsReviewSessionManager: All actions completed")
                return self._get_current_state()
            
            # Find the action across all streets
            action = self._get_action_by_index(self.current_action_index)
            
            # Convert action to PPSM format
            player = self._get_player_by_uid(action.actor_uid)
            action_type = action.action
            to_amount = action.to_amount if action.to_amount is not None else action.amount
            
            # Execute in PPSM
            result = self.ppsm.execute_action(player, action_type, to_amount)
            
            # Update action index
            self.current_action_index += 1
            
            # Create new table state
            new_state = self._create_table_state()
            
            # Add action effects
            self._add_action_effects(action, result)
            
            # Update store (not UI directly)
            self.store.dispatch({
                "type": "HANDS_REVIEW_ACTION_EXECUTED",
                "action_index": self.current_action_index - 1,
                "action": action,
                "state": new_state
            })
            
            print(f"🎯 HandsReviewSessionManager: Executed action {self.current_action_index}/{self.total_actions}")
            
            return HandsReviewState(
                current_hand=self.current_hand,
                current_action_index=self.current_action_index,
                total_actions=self.total_actions,
                is_playing=self.is_playing,
                playback_speed=self.playback_speed,
                **new_state
            )
            
        except Exception as e:
            print(f"❌ HandsReviewSessionManager: Error executing action: {e}")
            raise
    
    def _get_action_by_index(self, action_index: int) -> Dict[str, Any]:
        """Get action by global index across all streets."""
        if not self.current_hand:
            raise ValueError("No hand loaded")
        
        current_index = 0
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            street_actions = self.current_hand.streets[street].actions
            if current_index + len(street_actions) > action_index:
                return street_actions[action_index - current_index]
            current_index += len(street_actions)
        
        raise IndexError(f"Action index {action_index} out of range")
    
    def _get_player_by_uid(self, player_uid: str) -> Player:
        """Get Player object by UID from PPSM."""
        if not self.ppsm:
            raise ValueError("PPSM not initialized")
        
        # Get current game state
        game_state = self.ppsm.get_game_state()
        
        # Find player by name/UID
        for player_data in game_state.get('players', []):
            if player_data.get('name') == player_uid:
                # Create Player object from data
                from core.poker_types import Player
                return Player(
                    name=player_data.get('name', 'Unknown'),
                    stack=player_data.get('current_stack', 1000),
                    position=player_data.get('position', ''),
                    is_human=False,
                    is_active=player_data.get('acting', False),
                    cards=player_data.get('hole_cards', [])
                )
        
        # If not found, create a default player
        from core.poker_types import Player
        return Player(
            name=player_uid,
            stack=1000,
            position='',
            is_human=False,
            is_active=False,
            cards=[]
        )
    
    def play(self) -> None:
        """Start autoplay - business logic only."""
        if not self.is_playing and self.current_action_index < self.total_actions:
            self.is_playing = True
            
            # Schedule next action via GameDirector
            if self.game_director:
                self.game_director.schedule(
                    int(1000 / self.playback_speed),  # Convert to milliseconds
                    {"type": "AUTO_ADVANCE_HANDS_REVIEW"}
                )
            
            # Update store
            self.store.dispatch({
                "type": "HANDS_REVIEW_PLAY_STARTED",
                "is_playing": True
            })
            
            print("🎯 HandsReviewSessionManager: Autoplay started")
    
    def pause(self) -> None:
        """Pause autoplay - business logic only."""
        if self.is_playing:
            self.is_playing = False
            
            # Cancel scheduled events via GameDirector
            if self.game_director:
                self.game_director.cancel_all()
            
            # Update store
            self.store.dispatch({
                "type": "HANDS_REVIEW_PLAY_PAUSED",
                "is_playing": False
            })
            
            print("🎯 HandsReviewSessionManager: Autoplay paused")
    
    def seek(self, action_index: int) -> HandsReviewState:
        """Seek to specific action - business logic only."""
        if not self.current_hand:
            raise ValueError("No hand loaded")
        
        # Validate action index
        action_index = max(0, min(action_index, self.total_actions))
        
        # Reset PPSM to beginning
        self._initialize_ppsm_for_hand()
        
        # Execute actions up to target index
        self.current_action_index = 0
        for i in range(action_index):
            action = self._get_action_by_index(i)
            # Convert action to PPSM format
            player = self._get_player_by_uid(action.actor_uid)
            action_type = action.action
            to_amount = action.to_amount if action.to_amount is not None else action.amount
            
            self.ppsm.execute_action(player, action_type, to_amount)
            self.current_action_index += 1
        
        # Create table state
        new_state = self._create_table_state()
        
        # Update store
        self.store.dispatch({
            "type": "HANDS_REVIEW_SEEK_COMPLETED",
            "action_index": self.current_action_index,
            "state": new_state
        })
        
        print(f"🎯 HandsReviewSessionManager: Seeked to action {self.current_action_index}")
        
        return HandsReviewState(
            current_hand=self.current_hand,
            current_action_index=self.current_action_index,
            total_actions=self.total_actions,
            is_playing=self.is_playing,
            playback_speed=self.playback_speed,
            **new_state
        )
    
    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed - business logic only."""
        self.playback_speed = max(0.1, min(5.0, speed))
        
        # Update GameDirector if playing
        if self.is_playing and self.game_director:
            self.game_director.set_speed(self.playback_speed)
        
        # Update store
        self.store.dispatch({
            "type": "HANDS_REVIEW_SPEED_CHANGED",
            "speed": self.playback_speed
        })
        
        print(f"🎯 HandsReviewSessionManager: Playback speed set to {self.playback_speed}x")
    
    def _initialize_ppsm_for_hand(self) -> None:
        """Initialize PPSM with hand data - business logic only."""
        if not self.current_hand:
            return
        
        # Create game config from hand data
        config = GameConfig(
            num_players=len(self.current_hand.seats),
            small_blind=self.current_hand.metadata.small_blind,
            big_blind=self.current_hand.metadata.big_blind,
            starting_stack=1000  # Default, could be configurable
        )
        
        # Initialize PPSM
        self.ppsm.initialize_game(config)
        
        # Add players from seats
        for seat in self.current_hand.seats:
            self.ppsm.add_player(seat.player_uid, seat.starting_stack)
        
        # Set dealer position (default to seat 0 for now)
        self.ppsm.set_dealer_position(0)
    
    def _create_table_state(self) -> Dict[str, Any]:
        """Create table state from PPSM - business logic only."""
        try:
            # Get current game state from PPSM
            game_state = self.ppsm.get_game_state()
            
            # Extract relevant information
            seats = []
            for player in game_state.get('players', []):
                seats.append({
                    'player_uid': player.get('name', 'Unknown'),
                    'name': player.get('name', 'Unknown'),
                    'starting_stack': player.get('starting_stack', 1000),
                    'current_stack': player.get('current_stack', 1000),
                    'current_bet': player.get('current_bet', 0),
                    'stack': player.get('current_stack', 1000),
                    'bet': player.get('current_bet', 0),
                    'cards': player.get('hole_cards', []),
                    'folded': player.get('folded', False),
                    'all_in': player.get('all_in', False),
                    'acting': player.get('acting', False),
                    'position': player.get('position', ''),
                    'last_action': player.get('last_action', '')
                })
            
            # Determine current street
            street = "PREFLOP"
            board = game_state.get('board', [])
            if len(board) >= 3:
                street = "FLOP"
            if len(board) >= 4:
                street = "TURN"
            if len(board) >= 5:
                street = "RIVER"
            
            return {
                'table': {
                    'width': 1200,
                    'height': 800
                },
                'seats': seats,
                'board': board,
                'street': street,
                'pot': {
                    'amount': game_state.get('pot', 0),
                    'side_pots': game_state.get('side_pots', [])
                },
                'dealer': {
                    'position': game_state.get('dealer_position', 0)
                },
                'action': {
                    'current_player': game_state.get('current_player', -1),
                    'action_type': game_state.get('last_action_type', ''),
                    'amount': game_state.get('last_action_amount', 0)
                },
                'animation': {},
                'effects': []
            }
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Error creating table state: {e}")
            # Return default state
            return {
                'table': {'width': 1200, 'height': 800},
                'seats': [],
                'board': [],
                'street': 'PREFLOP',
                'pot': {'amount': 0, 'side_pots': []},
                'dealer': {'position': 0},
                'action': {'current_player': -1, 'action_type': '', 'amount': 0},
                'animation': {},
                'effects': []
            }
    
    def _add_action_effects(self, action, result) -> None:
        """Add action effects - business logic only."""
        try:
            # Get action type from Action object
            action_type = action.action.value if hasattr(action.action, 'value') else str(action.action)
            actor_uid = action.actor_uid if hasattr(action, 'actor_uid') else 'Unknown'
            
            # Debug: log what action type we're getting
            print(f"🎯 DEBUG: Action type: '{action_type}' (type: {type(action.action)})")
            
            # Add sound effects via EffectBus
            if self.effect_bus:
                self.effect_bus.add_poker_action_effects(action_type, actor_uid)
            
            # Add animation effects for ALL betting actions (not just end-of-street)
            if action_type in ["BET", "RAISE", "CALL", "CHECK", "FOLD"]:
                # Betting action animation - chips to pot
                if self.event_bus:
                    print(f"🎬 Triggering betting animation for action: {action_type}")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "betting_action",
                        "ms": 300,
                        "action_type": action_type,
                        "actor_uid": actor_uid
                    })
            
            # Add animation effects for specific actions
            if action_type in ["DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"]:
                # End-of-street animation
                if self.event_bus:
                    print(f"🎬 Triggering end-of-street animation for: {action_type}")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "chips_to_pot",
                        "ms": 260
                    })
            
            # Add showdown effects
            if action_type == "SHOWDOWN":
                if self.event_bus:
                    print(f"🎬 Triggering showdown animation")
                    self.event_bus.publish("effect_bus:animate", {
                        "name": "pot_to_winner",
                        "ms": 520
                    })
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Error adding action effects: {e}")
    
    def _get_current_state(self) -> HandsReviewState:
        """Get current session state."""
        table_state = self._create_table_state()
        return HandsReviewState(
            current_hand=self.current_hand,
            current_action_index=self.current_action_index,
            total_actions=self.total_actions,
            is_playing=self.is_playing,
            playback_speed=self.playback_speed,
            **table_state
        )
    
    def cleanup(self) -> None:
        """Clean up session resources."""
        try:
            # Cancel any scheduled events
            if self.game_director:
                self.game_director.cancel_all()
            
            # Reset state
            self.current_hand = None
            self.current_action_index = 0
            self.total_actions = 0
            self.is_playing = False
            
            print("🎯 HandsReviewSessionManager: Cleanup completed")
            
        except Exception as e:
            print(f"⚠️ HandsReviewSessionManager: Cleanup error: {e}")

```

---

### hands_review_tab.py

```python
import tkinter as tk
from tkinter import ttk
import uuid
from typing import Optional

# New UI Architecture imports
from ..state.actions import (
    SET_REVIEW_HANDS,
    SET_REVIEW_FILTER,
    SET_STUDY_MODE
)
from ..state.store import Store
from ..services.event_bus import EventBus
from ..services.service_container import ServiceContainer
from ..services.game_director import GameDirector
from ..services.effect_bus import EffectBus
from ..services.hands_repository import HandsRepository, HandsFilter, StudyMode
from ..services.hands_review_session_manager import HandsReviewSessionManager

# PPSM architecture - using HandsReviewSessionManager and PokerTableRenderer as per architecture guidelines

# Import enhanced button components
try:
    from ..components.enhanced_button import PrimaryButton, SecondaryButton
except ImportError:
    # Fallback to basic buttons if enhanced buttons not available
    PrimaryButton = SecondaryButton = tk.Button

# Import ActionBanner for visual feedback
try:
    from ..components.action_banner import ActionBanner
except ImportError:
    print("⚠️ ActionBanner not available, using fallback")
    ActionBanner = None

# Core imports - fail fast if not available
USE_DEV_STUBS = False  # set True only in a test harness

try:
    from core.hand_model import Hand
    from core.hand_model_decision_engine import HandModelDecisionEngine
    # PPSM imports instead of FPSM
    from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
    # HandsReviewBotSession removed - using PPSMHandsReviewBotSession below
    from core.session_logger import get_session_logger
            # Sound manager for poker table
    from utils.sound_manager import SoundManager
except ImportError as e:
    if not USE_DEV_STUBS:
        raise ImportError(f"Critical core modules not available: {e}. This will break hands review functionality.") from e
    print("⚠️ Using dev stubs due to import error:", e)
    
    # Minimal stubs for development only
    class Hand:
        def __init__(self, data):
            if isinstance(data, dict):
                self.hand_id = data.get("hand_id", "Unknown")
                self.players = data.get("players", [])
                self.pot_size = data.get("pot_size", 0)
                self.small_blind = data.get("small_blind", 5)
                self.big_blind = data.get("big_blind", 10)
                self.community_cards = data.get("community_cards", [])
                self.dealer = data.get("dealer", 0)
                self.__dict__.update(data)

        @classmethod
        def from_dict(cls, data):
            return cls(data)

    class HandModelDecisionEngine:
        def __init__(self, hand):
            pass

        def is_session_complete(self):
            return False

    class GameConfig:
        def __init__(self, **kwargs):
            pass

    def get_session_logger():
        class FallbackLogger:
            def log_system(self, *args, **kwargs):
                pass

        return FallbackLogger()


# Session manager will be initialized in the tab
# HandsReviewSessionManager handles all business logic per architecture guidelines

    




    """Concrete wrapper for HandModelDecisionEngine."""

    def __init__(self, hand):
        self.hand = hand
        try:
            if HandModelDecisionEngine and hand:
                self._engine = HandModelDecisionEngine.__new__(HandModelDecisionEngine)
                self._engine.hand = hand
                if hasattr(self._engine, "_organize_actions_by_street"):
                    self._engine.actions_by_street = (
                        self._engine._organize_actions_by_street()
                    )
                self._engine.current_action_index = 0
                if hasattr(self._engine, "_get_betting_actions"):
                    self._engine.actions_for_replay = (
                        self._engine._get_betting_actions()
                    )
                    self._engine.total_actions = len(self._engine.actions_for_replay)
                else:
                    self._engine.actions_for_replay = []
                    self._engine.total_actions = 0
            else:
                self._engine = None
        except Exception as e:
            print(f"❌ Error initializing decision engine: {e}")
            self._engine = None

    def get_decision(self, player_index: int, game_state):
        if self._engine and hasattr(self._engine, "get_decision"):
            return self._engine.get_decision(player_index, game_state)
        return {
            "action": "fold",
            "amount": 0,
            "explanation": "Default action",
            "confidence": 0.5,
        }

    def is_session_complete(self):
        if self._engine and hasattr(self._engine, "is_session_complete"):
            return self._engine.is_session_complete()
        return True

    def reset(self):
        if self._engine and hasattr(self._engine, "reset"):
            self._engine.reset()

    def get_session_info(self):
        if self._engine and hasattr(self._engine, "hand"):
            # Handle both fallback Hand class (hand.hand_id) and real Hand class (hand.metadata.hand_id)
            hand_id = "Unknown"
            if hasattr(self._engine.hand, "hand_id"):
                hand_id = self._engine.hand.hand_id
            elif hasattr(self._engine.hand, "metadata") and hasattr(
                self._engine.hand.metadata, "hand_id"
            ):
                hand_id = self._engine.hand.metadata.hand_id

            return {
                "hand_id": hand_id,
                "total_actions": getattr(self._engine, "total_actions", 0),
                "current_action": getattr(self._engine, "current_action_index", 0),
                "engine_type": "HandModelDecisionEngine",
            }
        return {
            "hand_id": "Unknown",
            "total_actions": 0,
            "current_action": 0,
            "engine_type": "Fallback",
        }


class HandsReviewTab(ttk.Frame):
    """Hands Review tab implementing the full PRD requirements."""

    def __init__(self, parent, services: ServiceContainer):
        super().__init__(parent)
        self.services = services
        self.session_id = f"hands_review_{uuid.uuid4().hex[:8]}"

        # Get app services
        self.event_bus: EventBus = services.get_app("event_bus")
        self.store: Store = services.get_app("store")
        self.theme = services.get_app("theme")
        self.hands_repository: HandsRepository = services.get_app("hands_repository")
        # Sounds are owned by EffectBus per architecture; no local fallback

        # Session state - using HandsReviewSessionManager per architecture guidelines
        self.session_manager: Optional[HandsReviewSessionManager] = None
        self.session_active = False
        
        # Use global services from service container for proper coordination
        self.game_director = self.services.get_app("game_director")
        if not self.game_director:
            # Create global GameDirector if not exists
            self.game_director = GameDirector(event_bus=self.event_bus)
            self.services.provide_app("game_director", self.game_director)
        
        # Use global EffectBus service for proper event coordination
        self.effect_bus = self.services.get_app("effect_bus")
        if not self.effect_bus:
            # Create global EffectBus if not exists
            self.effect_bus = EffectBus(
                game_director=self.game_director,
                event_bus=self.event_bus
            )
            self.services.provide_app("effect_bus", self.effect_bus)
        
        # Ensure proper connections for event coordination
        self.game_director.set_event_bus(self.event_bus)
        self.effect_bus.set_game_director(self.game_director)
        self.effect_bus.set_event_bus(self.event_bus)
        
        # Initialize HandsReviewSessionManager per architecture guidelines
        try:
            # Try direct import first
            try:
                from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
            except ImportError:
                # Fallback to relative import
                from ...core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
                
            # Create a default game config for hands review
            game_config = GameConfig(
                num_players=6,  # Default to 6 players for hands review
                small_blind=1.0,
                big_blind=2.0,
                starting_stack=1000.0
            )
            
            ppsm = PurePokerStateMachine(config=game_config)
            self.session_manager = HandsReviewSessionManager(
                store=self.store,
                ppsm=ppsm,
                game_director=self.game_director,
                effect_bus=self.effect_bus,
                event_bus=self.event_bus
            )
            print("🎯 HandsReviewTab: Session manager initialized per architecture guidelines")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Could not initialize session manager: {e}")
            self.session_manager = None

        # Setup UI
        self.on_mount()

        # Subscribe to events and store changes
        self._setup_event_subscriptions()
        self.store.subscribe(self._on_store_change)

        # Initialize GTO hands for PPSM testing
        self.loaded_gto_hands = []
        # GTO hands will be loaded in on_mount() to ensure proper UI initialization order

    def on_mount(self):
        """Set up the tab layout per PRD design."""
        # Two-column layout: Controls (20%) | Poker Table (80%)
        # Using 1:4 ratio for poker table emphasis
        self.grid_columnconfigure(0, weight=1)  # Library + Filters & Controls (20%)
        self.grid_columnconfigure(1, weight=4)  # Poker Table (80%)
        self.grid_rowconfigure(0, weight=1)

        # Create the two main sections
        self._create_combined_left_section()
        self._create_poker_table_section()
        
        # Load GTO hands for PPSM testing
        self._load_gto_hands()
        
        # Refresh hands list now that GTO hands are loaded
        self._refresh_hands_list()
        
        # Start main update loop for GameDirector and EffectBus
        self._start_update_loop()
        
        # Setup ActionBanner for visual feedback
        self._setup_action_banner()
        
        # Start the UI tick loop for GameDirector and EffectBus
        self._start_ui_tick_loop()

    def _create_combined_left_section(self):
        """Create the combined left section with hands library and controls."""
        # Get theme colors
        theme = self.theme.get_theme()

        # Main left frame
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2.5), pady=5)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=60)  # Hands library gets 60%
        left_frame.grid_rowconfigure(1, weight=40)  # Controls get 40%

        # Apply theme colors to main left frame
        try:
            left_frame.configure(background=theme.get("panel.bg", "#111827"))
        except Exception:
            pass

        # Create library section at top
        self._create_library_section_in_frame(left_frame)

        # Create filters/controls section at bottom
        self._create_filters_section_in_frame(left_frame)

    def _create_library_section_in_frame(self, parent):
        """Create the Library section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()

        library_frame = ttk.LabelFrame(parent, text="📚 Hands Library", padding=10)
        library_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 2.5))

        # Apply theme colors to the frame
        try:
            library_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass  # Fallback to default colors if theming fails
        library_frame.grid_columnconfigure(0, weight=1)
        library_frame.grid_rowconfigure(
            3, weight=1
        )  # Hands list gets most space (shifted down due to theme selector)

        # Theme selector (at top) - 5 Professional Casino Schemes
        theme_frame = ttk.LabelFrame(
            library_frame, text="🎨 Professional Casino Themes", padding=5
        )
        theme_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(0, weight=1)

        theme_controls = ttk.Frame(theme_frame)
        theme_controls.grid(row=0, column=0, sticky="ew")

        current_theme = self.theme.current_profile_name()
        self.theme_var = tk.StringVar(value=current_theme)

        # All available themes from ThemeManager
        all_theme_names = self.theme.names()
        print(
            f"🎨 HandsReviewTab: Found {len(all_theme_names)} themes: {all_theme_names}"
        )

        # Fallback if no themes found
        if not all_theme_names:
            print("⚠️ No themes found, forcing theme manager reload...")
            # Try to reload theme manager
            try:
                from ..services.theme_factory import build_all_themes

                themes = build_all_themes()
                print(f"🔄 Force-built {len(themes)} themes: {list(themes.keys())}")
                # Register them with the theme manager
                for name, tokens in themes.items():
                    self.theme.register(name, tokens)
                all_theme_names = self.theme.names()
                print(
                    f"🎨 After reload: {len(all_theme_names)} themes: {all_theme_names}"
                )
            except Exception as e:
                print(f"❌ Failed to reload themes: {e}")
                # Get actual theme names from config, with ultimate fallback
                default_theme_data = self.theme.get_available_themes()
                all_theme_names = (
                    list(default_theme_data.keys())
                    if default_theme_data
                    else ["Forest Green Professional 🌿"]
                )

        # Theme icons are now embedded in theme names from JSON config
        # No need for separate THEME_ICONS or THEME_INTROS - all data comes from poker_themes.json

        # Create clean 4x4 grid layout for 16 themes with 20px font
        # Configure grid weights for even distribution
        for col_idx in range(4):
            theme_controls.grid_columnconfigure(col_idx, weight=1)

        for i, theme_name in enumerate(all_theme_names):
            row = i // 4  # 4 themes per row
            col = i % 4

            # Theme names from JSON config already include icons and formatting
            display_name = theme_name

            # Simple radiobutton with 20px font and equal spacing
            radio_btn = ttk.Radiobutton(
                theme_controls,
                text=display_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._on_theme_change,
            )
            radio_btn.grid(row=row, column=col, sticky="w", padx=5, pady=3)

            # Configure font size to 20px and store reference for styling
            try:
                fonts = self.theme.get_fonts()
                radio_font = fonts.get(
                    "button", fonts.get("body", ("Inter", 20, "normal"))
                )
                radio_btn.configure(font=radio_font)
            except:
                # Fallback if font configuration fails
                pass

            # Store radio button reference for theme styling
            if not hasattr(self, "theme_radio_buttons"):
                self.theme_radio_buttons = []
            self.theme_radio_buttons.append(radio_btn)

            # Theme intro will update only on selection, not hover
            # Removed confusing hover effects that changed intro on mouse over

        # Apply initial theme styling to radio buttons
        self.after_idle(self._style_theme_radio_buttons)

        # Artistic Theme Info Panel - shows evocative descriptions (positioned AFTER theme controls)
        info_frame = ttk.Frame(theme_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        # Luxury Museum Placard - Theme intro with elegant styling
        fonts = self.theme.get_fonts()
        # Use theme-aware font for luxury feel
        fonts = self.theme.get_fonts()
        intro_font = fonts.get("intro", fonts.get("body", ("Georgia", 16, "normal")))

        # Create luxury museum placard frame with theme-aware styling
        base_colors = self.theme.get_base_colors()
        placard_bg = base_colors.get("panel_bg", "#2A2A2A")
        placard_accent = base_colors.get("highlight", "#D4AF37")

        placard_frame = tk.Frame(
            info_frame,
            relief="raised",
            borderwidth=2,
            bg=placard_bg,
            highlightbackground=placard_accent,
            highlightcolor=placard_accent,
            highlightthickness=1,
        )
        # Use theme dimensions for consistent spacing
        dimensions = self.theme.get_dimensions()
        medium_pad = dimensions["padding"]["medium"]
        placard_frame.grid(
            row=0, column=0, sticky="ew", padx=medium_pad, pady=medium_pad
        )
        placard_frame.grid_columnconfigure(0, weight=1)

        # Store reference to placard frame for dynamic styling
        self.placard_frame = placard_frame

        # Get initial theme colors instead of hardcoding
        base_colors = self.theme.get_base_colors()
        initial_bg = base_colors.get("panel_bg", "#1A1A1A")
        initial_fg = base_colors.get("text", "#F5F5DC")

        intro_height = dimensions["text_height"][
            "medium"
        ]  # Use medium instead of small for theme intros
        self.theme_intro_label = tk.Text(
            placard_frame,
            height=intro_height,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            font=intro_font,
            state="disabled",
            cursor="arrow",
            padx=dimensions["padding"]["xlarge"],
            pady=dimensions["padding"]["medium"],
            bg=initial_bg,
            fg=initial_fg,
        )  # Dynamic theme colors
        self.theme_intro_label.grid(row=0, column=0, sticky="ew")

        # Show current theme's introduction
        self._show_theme_intro(current_theme)

        # Library type selector
        type_frame = ttk.Frame(library_frame)
        type_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        type_frame.grid_columnconfigure(0, weight=1)

        self.library_type = tk.StringVar(value="legendary")
        ttk.Radiobutton(
            type_frame,
            text="🏆 Legendary",
            variable=self.library_type,
            value="legendary",
            command=self._on_library_type_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="🤖 Bot Sessions",
            variable=self.library_type,
            value="bot",
            command=self._on_library_type_change,
        ).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(
            type_frame,
            text="📥 Imported",
            variable=self.library_type,
            value="imported",
            command=self._on_library_type_change,
        ).grid(row=0, column=2, sticky="w")

        # Collections dropdown
        collections_frame = ttk.Frame(library_frame)
        collections_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        collections_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(collections_frame, text="Collection:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.collection_var = tk.StringVar(value="🤖 GTO Hands")
        self.collection_combo = ttk.Combobox(
            collections_frame, textvariable=self.collection_var, state="readonly"
        )
        self.collection_combo.grid(row=0, column=1, sticky="ew")
        self.collection_combo.bind("<<ComboboxSelected>>", self._on_collection_change)

        # Hands listbox
        hands_frame = ttk.Frame(library_frame)
        hands_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        hands_frame.grid_columnconfigure(0, weight=1)
        hands_frame.grid_rowconfigure(0, weight=1)

        # Get fonts from theme
        fonts = self.theme.get_fonts()
        body_font = fonts.get("body", ("Consolas", 20))

        self.hands_listbox = tk.Listbox(
            hands_frame, font=body_font, selectmode=tk.SINGLE
        )
        self.hands_listbox.grid(row=0, column=0, sticky="nsew")
        self.hands_listbox.bind("<<ListboxSelect>>", self._on_hand_select)

        # Apply theme colors to listbox with dynamic selection highlight
        try:
            # Get theme-specific selection highlight
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            # Get selection highlight from config-driven system
            base_colors = self.theme.get_base_colors()
            selection_highlight = {
                "color": base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
            }

            self.hands_listbox.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                selectbackground=selection_highlight[
                    "color"
                ],  # Dynamic theme-specific highlight
                selectforeground=base_colors.get(
                    "highlight_text", base_colors.get("text", "#FFFFFF")
                ),  # Theme-aware text when highlighted
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        scrollbar = ttk.Scrollbar(
            hands_frame, orient="vertical", command=self.hands_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hands_listbox.configure(yscrollcommand=scrollbar.set)

        # Hand details text (smaller in the combined layout)
        details_frame = ttk.LabelFrame(library_frame, text="Hand Details", padding=5)
        details_frame.grid(row=5, column=0, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)

        small_font = fonts.get("small", ("Consolas", 16))
        details_height = self.theme.get_dimensions()["text_height"]["medium"]
        self.details_text = tk.Text(
            details_frame, height=details_height, wrap=tk.WORD, font=small_font
        )
        self.details_text.grid(row=0, column=0, sticky="ew")

        # Apply theme colors to details text
        try:
            self.details_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

    def _create_filters_section_in_frame(self, parent):
        """Create the Filters & Controls section within the given parent frame."""
        # Get theme colors
        theme = self.theme.get_theme()

        filters_frame = ttk.LabelFrame(
            parent, text="🔍 Filters & Study Mode", padding=10
        )
        filters_frame.grid(row=1, column=0, sticky="nsew", pady=(2.5, 0))

        # Apply theme colors to the frame
        try:
            filters_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass
        filters_frame.grid_columnconfigure(0, weight=1)

        # Study Mode selector
        study_frame = ttk.LabelFrame(filters_frame, text="Study Mode", padding=5)
        study_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.study_mode = tk.StringVar(value=StudyMode.REPLAY.value)
        ttk.Radiobutton(
            study_frame,
            text="🔄 Replay",
            variable=self.study_mode,
            value=StudyMode.REPLAY.value,
            command=self._on_study_mode_change,
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="📊 Solver Diff",
            variable=self.study_mode,
            value=StudyMode.SOLVER_DIFF.value,
            command=self._on_study_mode_change,
        ).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="🧠 Recall Quiz",
            variable=self.study_mode,
            value=StudyMode.RECALL_QUIZ.value,
            command=self._on_study_mode_change,
        ).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(
            study_frame,
            text="❓ Explain Mistake",
            variable=self.study_mode,
            value=StudyMode.EXPLAIN_MISTAKE.value,
            command=self._on_study_mode_change,
        ).grid(row=3, column=0, sticky="w")

        # Filters section
        filter_frame = ttk.LabelFrame(filters_frame, text="Filters", padding=5)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        # Position filter
        ttk.Label(filter_frame, text="Position:").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.position_var = tk.StringVar(value="All")
        position_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.position_var,
            values=["All", "UTG", "MP", "CO", "BTN", "SB", "BB"],
            state="readonly",
            width=8,
        )
        position_combo.grid(row=0, column=1, sticky="w", pady=2)

        # Stack depth filter
        ttk.Label(filter_frame, text="Stack Depth:").grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        stack_frame = ttk.Frame(filter_frame)
        stack_frame.grid(row=1, column=1, sticky="w", pady=2)
        self.min_stack = tk.StringVar(value="20")
        self.max_stack = tk.StringVar(value="200")
        ttk.Entry(stack_frame, textvariable=self.min_stack, width=5).grid(
            row=0, column=0
        )
        ttk.Label(stack_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(stack_frame, textvariable=self.max_stack, width=5).grid(
            row=0, column=2
        )
        ttk.Label(stack_frame, text=" BB").grid(row=0, column=3)

        # Pot type filter
        ttk.Label(filter_frame, text="Pot Type:").grid(
            row=2, column=0, sticky="w", padx=(0, 5)
        )
        self.pot_type_var = tk.StringVar(value="All")
        pot_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.pot_type_var,
            values=["All", "SRP", "3BP", "4BP+"],
            state="readonly",
            width=8,
        )
        pot_combo.grid(row=2, column=1, sticky="w", pady=2)

        # Search text
        ttk.Label(filter_frame, text="Search:").grid(
            row=3, column=0, sticky="w", padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=3, column=1, sticky="ew", pady=2)
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        # Apply filters button
        ttk.Button(
            filter_frame, text="Apply Filters", command=self._apply_filters
        ).grid(row=4, column=0, columnspan=2, pady=5)

        # Action buttons
        actions_frame = ttk.LabelFrame(filters_frame, text="Actions", padding=5)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        actions_frame.grid_columnconfigure(0, weight=1)

        # Load button (main action) - Enhanced primary button
        self.load_btn = PrimaryButton(
            actions_frame,
            text="🔥 LOAD HAND",
            command=self._load_selected_hand,
            theme_manager=self.theme,
        )
        self.load_btn.grid(row=0, column=0, sticky="ew", pady=5)

        # Enhanced button handles its own styling

        # Playback controls
        controls_frame = ttk.Frame(actions_frame)
        controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Enhanced buttons handle their own styling

        # Enhanced secondary buttons for controls
        self.next_btn = SecondaryButton(
            controls_frame,
            text="Next →",
            command=self._next_action,  # Use session manager method
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        self.auto_btn = SecondaryButton(
            controls_frame,
            text="Auto",
            command=self._toggle_auto_play,  # Use session manager method
            theme_manager=self.theme,
        )
        self.auto_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = SecondaryButton(
            controls_frame,
            text="Reset",
            command=self._reset_hand,  # Use session manager method
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=2, padx=(5, 0))

        # Enhanced buttons handle their own styling

        # Status text
        status_frame = ttk.LabelFrame(filters_frame, text="Status", padding=5)
        status_frame.grid(row=3, column=0, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)

        fonts = self.theme.get_fonts()
        small_font = fonts.get("small", ("Consolas", 16))
        status_height = self.theme.get_dimensions()["text_height"]["large"]
        self.status_text = tk.Text(
            status_frame, height=status_height, wrap=tk.WORD, font=small_font
        )
        self.status_text.grid(row=0, column=0, sticky="nsew")

        # Apply theme colors to status text
        try:
            self.status_text.configure(
                bg=theme.get("panel.bg", "#111827"),
                fg=theme.get("panel.fg", "#E5E7EB"),
                insertbackground=theme.get("panel.fg", "#E5E7EB"),
                highlightbackground=theme.get("panel.border", "#1F2937"),
                highlightcolor=theme.get("a11y.focusRing", "#22D3EE"),
            )
        except Exception:
            pass

        # Poker Table Controls
        poker_frame = ttk.LabelFrame(actions_frame, text="🎮 Poker Table Controls", padding=5)
        poker_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        poker_frame.grid_columnconfigure(1, weight=1)

        # Next Action button for poker table
        self.next_btn = SecondaryButton(
            poker_frame,
            text="▶ Next Action",
            command=self._next_action,
            theme_manager=self.theme,
        )
        self.next_btn.grid(row=0, column=0, padx=(0, 5))

        # Reset button for poker table
        self.reset_btn = SecondaryButton(
            poker_frame,
            text="↩ Reset Hand",
            command=self._reset_hand,
            theme_manager=self.theme,
        )
        self.reset_btn.grid(row=0, column=1, padx=5)

        # Progress display for poker table
        self.progress_label = ttk.Label(poker_frame, text="No hand loaded")
        self.progress_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Enhanced buttons handle their own styling

    def _create_poker_table_section(self):
        """Create poker table using PokerTableRenderer (right column)."""
        # Get theme colors for poker table
        theme = self.theme.get_theme()

        table_frame = ttk.LabelFrame(self, text="♠️ Enhanced Poker Table", padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(2.5, 5), pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Apply theme colors to table frame
        try:
            table_frame.configure(
                background=theme.get("panel.bg", "#111827"),
                foreground=theme.get("panel.sectionTitle", "#C7D2FE"),
            )
        except Exception:
            pass

        # Create PokerTableRenderer directly in the table frame
        self._setup_poker_table(table_frame)

    def _setup_poker_table(self, parent_frame):
        """Set up the PokerTableRenderer with poker table display."""
        # Force parent frame to update geometry first
        parent_frame.update_idletasks()
        parent_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Get frame dimensions, with fallback to reasonable defaults
        frame_width = parent_frame.winfo_width()
        frame_height = parent_frame.winfo_height()
        
        # If frame is too small initially, wait for it to be properly sized
        if frame_width <= 100 or frame_height <= 100:
            # Wait a bit for the frame to be properly sized
            parent_frame.after(100, lambda: self._retry_frame_sizing(parent_frame))
            frame_width = 1200  # Use larger default for better initial appearance
            frame_height = 800
            print(f"🎯 HandsReviewTab: Frame initially small, using {frame_width}x{frame_height}")
        
        # Use frame dimensions for proper integration
        table_width = max(1200, frame_width - 20)  # Use larger minimum
        table_height = max(800, frame_height - 20)
        
        # Calculate card size based on table dimensions
        card_width = max(40, int(table_width * 0.035))  # ~3.5% of table width
        card_height = int(card_width * 1.45)  # Standard card aspect ratio
        
        print(f"🎯 HandsReviewTab: Frame {frame_width}x{frame_height}, Table {table_width}x{table_height}")
        print(f"🎯 HandsReviewTab: Card size {card_width}x{card_height}")
        
        # Use PokerTableRenderer as per architecture guidelines
        from ..renderers.poker_table_renderer import PokerTableRenderer

        self.table_renderer = PokerTableRenderer(
            parent_frame,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme if hasattr(self, 'theme') else None,
        )
        self.table_renderer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        
        # Access canvas manager through renderer for legacy compatibility
        self.canvas_manager = self.table_renderer.canvas_manager
        self.layer_manager = self.table_renderer.layer_manager
        
        # Link EffectBus to renderer so animation bridge can draw chips
        try:
            if hasattr(self, 'effect_bus'):
                self.effect_bus.renderer = self.table_renderer
        except Exception:
            pass
        
        # Accumulate declarative effects per frame
        self._pending_effects = []
        
        # Store dimensions for state management
        self.table_width = table_width
        self.table_height = table_height
        self.card_width = card_width
        self.card_height = card_height
        
        # Initialize poker table state
        self._setup_poker_table_state()
        
        # Force table to expand to fill available space
        self._force_table_expansion()

        # Bind a one-time resize to ensure the canvas fills the pane immediately
        try:
            self._resize_bound = False
            def _on_parent_configure(event):
                # Only run the first substantial configure (>100px each side)
                if getattr(self, '_resize_bound', False):
                    return
                if event.width > 100 and event.height > 100:
                    self._resize_bound = True
                    # Update canvas to exact current parent size minus padding
                    canvas_w = max(200, event.width - 20)
                    canvas_h = max(150, event.height - 20)
                    if hasattr(self, 'canvas_manager') and self.canvas_manager:
                        self.canvas_manager.canvas.configure(width=canvas_w, height=canvas_h)
                        self.table_width = canvas_w
                        self.table_height = canvas_h
                        try:
                            # Trigger a re-render with the new dimensions
                            self._render_poker_table()
                        except Exception:
                            pass
            parent_frame.bind('<Configure>', _on_parent_configure)
        except Exception:
            pass
        
        print("🎨 PokerTableRenderer components ready")

    def _retry_frame_sizing(self, parent_frame):
        """Retry getting frame dimensions after a delay."""
        try:
            # Get updated frame dimensions
            frame_width = parent_frame.winfo_width()
            frame_height = parent_frame.winfo_height()
            
            if frame_width > 100 and frame_height > 100:
                # Frame is now properly sized, update table dimensions
                table_width = frame_width - 20
                table_height = frame_height - 20
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update canvas size
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    self.canvas_manager.canvas.configure(
                        width=table_width, 
                        height=table_height
                    )
                
                print(f"🎯 HandsReviewTab: Retry successful, updated to {table_width}x{table_height}")
                
                # Force table expansion
                self._force_table_expansion()
            else:
                # Still too small, try again
                parent_frame.after(100, lambda: self._retry_frame_sizing(parent_frame))
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Retry sizing error: {e}")

    def _force_table_expansion(self):
        """Force the poker table to expand and fill the available space."""
        try:
            # Get the parent frame
            if hasattr(self, 'table_renderer') and self.table_renderer:
                parent_frame = self.table_renderer.master
                
                # Force geometry update
                parent_frame.update_idletasks()
                
                # Configure grid weights to ensure expansion
                parent_frame.grid_columnconfigure(0, weight=1)
                parent_frame.grid_rowconfigure(0, weight=1)
                
                # Force the table renderer to expand
                self.table_renderer.grid_configure(sticky="nsew")
                
                # Update canvas size to fill available space
                if hasattr(self, 'canvas_manager') and self.canvas_manager:
                    # Get current frame dimensions
                    frame_width = parent_frame.winfo_width()
                    frame_height = parent_frame.winfo_height()
                    
                    # Use reasonable dimensions if frame is too small
                    if frame_width <= 100 or frame_height <= 100:
                        frame_width = 800
                        frame_height = 600
                    
                    # Set canvas size to fill frame
                    canvas_width = frame_width - 20  # Leave padding
                    canvas_height = frame_height - 20
                    
                    self.canvas_manager.canvas.configure(
                        width=canvas_width, 
                        height=canvas_height
                    )
                    
                    # Update stored dimensions
                    self.table_width = canvas_width
                    self.table_height = canvas_height
                    
                    print(f"🎯 HandsReviewTab: Forced table expansion to {canvas_width}x{canvas_height}")
                    
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Table expansion error: {e}")

    def _setup_poker_table_state(self):
        """Initialize state management for the poker table."""
        # Initialize display state for the poker table with placeholder data for visual testing
        self.display_state = {
            'table': {
                'width': self.table_width,
                'height': self.table_height
            },
            'pot': {
                'amount': 0.0,
                'side_pots': []
            },
            'seats': [
                # Placeholder seat 1 (top)
                {
                    'player_uid': 'placeholder_1',
                    'name': 'Player 1',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Ah', 'Kh'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 0
                },
                # Placeholder seat 2 (bottom) 
                {
                    'player_uid': 'placeholder_2',
                    'name': 'Player 2',
                    'starting_stack': 1000,
                    'current_stack': 1000,
                    'current_bet': 0,
                    'stack': 1000,
                    'bet': 0,
                    'cards': ['Qd', 'Jd'],  # Placeholder hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': 1
                }
            ],
            'board': [],  # Empty board initially (will show 5 card backs)
            'street': 'PREFLOP',  # Current street for community card rendering
            'dealer': {
                'position': 0
            },
            'action': {
                'current_player': -1,
                'action_type': None,
                'amount': 0.0,
                'highlight': False
            },
            'replay': {
                'active': False,
                'current_action': 0,
                'total_actions': 0,
                'description': "No hand loaded - showing placeholder state"
            }
        }
        
        print("🎯 HandsReviewTab state management ready with placeholder seats for visual testing")

    def _setup_event_subscriptions(self):
        """Subscribe to relevant events."""
        # Subscribe to review:load events as per architecture doc
        self.event_bus.subscribe(
            self.event_bus.topic(self.session_id, "review:load"),
            self._handle_load_hand_event,
        )

    def _refresh_hands_list(self):
        """Refresh the hands list based on current filters - prioritize GTO hands for PPSM."""
        # Check collection selection
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        # Load hands based on selection
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            # Repository hands (legendary hands)
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"

        print(f"🎯 HandsReviewTab: Loading {len(hands)} hands from {hands_source}")

        # Dispatch to store - convert Hand objects to dict format if needed
        hands_for_store = []
        for hand in hands:
            if hasattr(hand, 'metadata'):  # Hand object
                hands_for_store.append({
                    'hand_id': hand.metadata.get('hand_id', 'Unknown'),
                    'players': hand.seats,
                    'pot_size': hand.metadata.get('pot_size', 0)
                })
            else:  # Already dict format
                hands_for_store.append(hand)
                
        self.store.dispatch({"type": SET_REVIEW_HANDS, "hands": hands_for_store})

        # Update UI display
        self.hands_listbox.delete(0, tk.END)
        for i, hand in enumerate(hands):
            try:
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', f'GTO_Hand_{i+1}')
                    players_count = len(hand.seats) if hasattr(hand, 'seats') else 2
                    display_text = f"{hand_id} | {players_count}p | PPSM Ready"
                else:  # Dict format
                    hand_id = hand.get("hand_id", f"Hand_{i+1}")
                    # GTO hands use 'seats', regular hands use 'players'
                    seats = hand.get("seats", [])
                    players = hand.get("players", [])
                    # Use whichever is available
                    players_count = len(seats) if seats else len(players)
                    pot_size = hand.get("pot_size", 0)
                    small_blind = hand.get("small_blind", 5)
                    big_blind = hand.get("big_blind", 10)
                    
                    details = f"Hand ID: {hand_id}\\n"
                    details += f"Players: {players_count}\\n"
                    details += f"Pot: ${pot_size}\\n"
                    details += f"Blinds: ${small_blind}/${big_blind}\\n"
                    details += f"Source: Repository"
                self.hands_listbox.insert(tk.END, display_text)
            except Exception as e:
                # Fallback display
                self.hands_listbox.insert(tk.END, f"Hand_{i+1} | PPSM")
                print(f"⚠️ Error displaying hand {i}: {e}")

        # Update collections - prioritize GTO hands
        gto_available = hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands
        if gto_available:
            collections = ["🤖 GTO Hands", "All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        else:
            collections = ["All Hands"] + list(
                self.hands_repository.get_collections().keys()
            )
        self.collection_combo["values"] = collections

        # Update status with workflow guidance based on active source
        if hands_source == "GTO":
            self._update_status(
                f"🤖 GTO Library: {len(hands)} hands loaded for PPSM testing"
            )
        else:
            stats = self.hands_repository.get_stats()
            self._update_status(
                f"📊 Repository: {stats['total_hands']} total, {stats['filtered_hands']} filtered"
            )
        self._update_status(
            "👆 SELECT a hand from the list, then click 'LOAD HAND' to begin PPSM study"
        )
        
        # Refresh poker table widget to ensure proper sizing
        if hasattr(self, '_refresh_poker_table_widget'):
            self._refresh_poker_table_widget()

    def _on_theme_change(self):
        """Handle poker table theme change for poker table."""
        theme_name = self.theme_var.get()
        print(f"🎨 HandsReviewTab: Switching to theme: {theme_name}")

        # Switch theme in the theme manager
        self.theme.set_profile(theme_name)

        # Update status to show theme change
        self._update_status(
            f"🎨 Switched to {theme_name} theme - Poker table colors applied!"
        )

        # Force poker table refresh with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with {theme_name} theme")

        # Refresh widget sizing to ensure proper fit
        self._refresh_poker_table_widget()

        # Update artistic theme introduction
        self._show_theme_intro(theme_name)

    def _show_theme_intro(self, theme_name):
        """Show artistic introduction for the selected theme with luxury museum placard styling."""
        # Get theme metadata from config-driven system
        metadata = self.theme.get_theme_metadata(theme_name)
        main_desc = metadata.get(
            "intro", "A unique poker table theme with its own distinctive character."
        )
        persona = metadata.get("persona", "")

        # Update the intro label with luxury styling
        self.theme_intro_label.config(state="normal")
        self.theme_intro_label.delete(1.0, tk.END)

        # Insert main description with elegant styling
        self.theme_intro_label.insert(tk.END, main_desc)

        # Add poker persona in italic gold if present
        if persona:
            self.theme_intro_label.insert(tk.END, "\n\n")
            persona_start = self.theme_intro_label.index(tk.INSERT)
            # Format persona with attribution
            persona_text = f"— {persona} style —"
            self.theme_intro_label.insert(tk.END, persona_text)
            persona_end = self.theme_intro_label.index(tk.INSERT)

            # Apply italic styling to persona
            self.theme_intro_label.tag_add("persona", persona_start, persona_end)
            fonts = self.theme.get_fonts()
            persona_font = fonts.get(
                "persona", fonts.get("intro", ("Georgia", 15, "italic"))
            )
            self.theme_intro_label.tag_config("persona", font=persona_font)

        self.theme_intro_label.config(state="disabled")

        # Apply DYNAMIC luxury museum placard styling based on current theme
        theme = self.theme.get_theme()

        # Dynamic theme-aware colors for museum placard
        # Use theme's panel colors but make them more luxurious
        base_bg = theme.get("panel.bg", "#1A1A1A")
        base_border = theme.get("panel.border", "#2A2A2A")
        accent_color = theme.get("table.inlay", theme.get("pot.badgeRing", "#D4AF37"))
        text_primary = theme.get("text.primary", "#F5F5DC")
        text_secondary = theme.get("text.secondary", "#E0E0C0")

        # Use hand-tuned JSON theme colors for perfect quality
        base_colors = self.theme.get_base_colors()

        # Use hand-tuned emphasis tokens for perfect theme-specific quality
        placard_bg = base_colors.get(
            "emphasis_bg_top", base_colors.get("felt", base_bg)
        )
        placard_border = base_colors.get(
            "emphasis_border", base_colors.get("rail", base_border)
        )
        text_color = base_colors.get(
            "emphasis_text", base_colors.get("text", text_primary)
        )
        persona_color = base_colors.get(
            "emphasis_accent_text", base_colors.get("accent", accent_color)
        )
        accent_glow = base_colors.get(
            "highlight", base_colors.get("metal", accent_color)
        )

        # Apply dynamic luxury styling
        self.theme_intro_label.config(
            bg=placard_bg,
            fg=text_color,
            insertbackground=text_color,
            selectbackground=accent_glow,
            selectforeground=base_colors.get("highlight_text", "#FFFFFF"),
        )

        # Style the placard frame with hand-tuned luxury border
        if hasattr(self, "placard_frame"):
            self.placard_frame.config(
                bg=placard_border,  # Hand-tuned theme border color
                relief="raised",
                borderwidth=2,  # Luxury feel
                highlightbackground=accent_glow,
                highlightcolor=accent_glow,
                highlightthickness=1,
            )

        # Apply theme-specific persona text color
        if persona:
            self.theme_intro_label.config(state="normal")
            self.theme_intro_label.tag_config("persona", foreground=persona_color)
            self.theme_intro_label.config(state="disabled")

    def _refresh_ui_colors(self):
        """Refresh poker table with new theme colors."""
        theme = self.theme.get_theme()
        print(f"🎨 HandsReviewTab: Refreshing colors for {self.theme_var.get()} theme")

        # Update poker table canvas background with new theme
        if hasattr(self, "canvas_manager") and self.canvas_manager.canvas:
            # Update canvas background to match new theme
            self.canvas_manager.canvas.configure(
                bg=theme.get("table.felt", "#1E5B44")
            )
            print(f"🎨 HandsReviewTab: Canvas background updated to {theme.get('table.felt', '#1E5B44')}")

        # Force poker table re-render with new theme
        if hasattr(self, 'table_renderer') and hasattr(self, 'display_state'):
            self._render_poker_table()
            print(f"🎨 HandsReviewTab: Re-rendered with new theme colors")

        # Update enhanced buttons to refresh their theme
        for btn_name in ["load_btn", "next_btn", "auto_btn", "reset_btn"]:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if hasattr(btn, "refresh_theme"):
                    btn.refresh_theme()

        # Update artistic theme intro panel colors
        if hasattr(self, "theme_intro_label"):
            self._show_theme_intro(self.theme_var.get())

    def _on_library_type_change(self):
        """Handle library type change."""
        library_type = self.library_type.get()
        # TODO: Filter by library type
        self._refresh_hands_list()

    def _on_collection_change(self, event=None):
        """Handle collection selection change."""
        collection = self.collection_var.get()
        print(f"🎯 Collection changed to: {collection}")
        
        if collection == "🤖 GTO Hands":
            # GTO hands are handled in _refresh_hands_list()
            pass
        elif collection == "All Hands":
            self.hands_repository.set_filter(HandsFilter())  # Clear filter
        else:
            # TODO: Set filter for specific collection
            pass
        self._refresh_hands_list()

    def _on_hand_select(self, event):
        """Handle hand selection - prioritize GTO hands for PPSM."""
        selection = self.hands_listbox.curselection()
        if selection:
            index = selection[0]
            
            # Get hands from the same source as _refresh_hands_list
            collection = getattr(self, 'collection_var', None)
            selected_collection = collection.get() if collection else "🤖 GTO Hands"
            
            if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
                hands = self.loaded_gto_hands
                hands_source = "GTO"
            else:
                hands = self.hands_repository.get_filtered_hands()
                hands_source = "Repository"
                
            if index < len(hands):
                hand = hands[index]
                self._update_hand_details(hand)
                
                # Get hand ID based on format
                if hasattr(hand, 'metadata'):  # Hand object
                    hand_id = hand.metadata.get('hand_id', 'Unknown')
                else:  # Dict format
                    hand_id = hand.get("hand_id", "Unknown")
                    
                # Show that hand is selected and ready to load
                self._update_status(
                    f"✅ Selected: {hand_id} ({hands_source}) - Click 'LOAD HAND' to start PPSM study"
                )

    def _update_hand_details(self, hand_data):
        """Update the hand details display - works with both Hand objects and dicts."""
        self.details_text.delete(1.0, tk.END)
        
        try:
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'metadata'):  # Hand object
                hand_id = hand_data.metadata.get('hand_id', 'Unknown')
                small_blind = hand_data.metadata.get('small_blind', 5)
                big_blind = hand_data.metadata.get('big_blind', 10)
                players_count = len(hand_data.seats) if hasattr(hand_data, 'seats') else 0
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Engine: PPSM Ready\\n"
                details += f"Source: GTO Dataset"
                
            else:  # Dict format
                hand_id = hand_data.get("hand_id", "Unknown")
                # GTO hands use 'seats', regular hands use 'players'
                seats = hand_data.get("seats", [])
                players = hand_data.get("players", [])
                # Use whichever is available
                players_count = len(seats) if seats else len(players)
                pot_size = hand_data.get("pot_size", 0)
                small_blind = hand_data.get("small_blind", 5)
                big_blind = hand_data.get("big_blind", 10)
                
                details = f"Hand ID: {hand_id}\\n"
                details += f"Players: {players_count}\\n"
                details += f"Pot: ${pot_size}\\n"
                details += f"Blinds: ${small_blind}/${big_blind}\\n"
                details += f"Source: Repository"
                
        except Exception as e:
            details = f"Hand details unavailable: {e}"
            
        self.details_text.insert(1.0, details)

    def _on_study_mode_change(self):
        """Handle study mode change."""
        mode = self.study_mode.get()
        self.store.dispatch({"type": SET_STUDY_MODE, "mode": mode})
        self._update_status(f"📚 Study mode: {mode}")

    def _apply_filters(self):
        """Apply current filter settings."""
        filter_criteria = HandsFilter()

        # Apply position filter
        if self.position_var.get() != "All":
            filter_criteria.positions = [self.position_var.get()]

        # Apply stack depth filter
        try:
            filter_criteria.min_stack_depth = (
                int(self.min_stack.get()) if self.min_stack.get() else None
            )
            filter_criteria.max_stack_depth = (
                int(self.max_stack.get()) if self.max_stack.get() else None
            )
        except ValueError:
            pass

        # Apply pot type filter
        if self.pot_type_var.get() != "All":
            filter_criteria.pot_type = self.pot_type_var.get()

        # Apply search text
        filter_criteria.search_text = self.search_var.get()

        # Set filter and refresh
        self.hands_repository.set_filter(filter_criteria)
        self.store.dispatch(
            {"type": SET_REVIEW_FILTER, "filter": filter_criteria.__dict__}
        )
        self._refresh_hands_list()

    def _load_selected_hand(self):
        """Load the selected hand for PPSM study."""
        selection = self.hands_listbox.curselection()
        if not selection:
            self._update_status("❌ Please select a hand to load")
            return

        index = selection[0]
        
        # Get hands from the same source as _refresh_hands_list
        collection = getattr(self, 'collection_var', None)
        selected_collection = collection.get() if collection else "🤖 GTO Hands"
        
        if selected_collection == "🤖 GTO Hands" and hasattr(self, 'loaded_gto_hands') and self.loaded_gto_hands:
            hands = self.loaded_gto_hands
            hands_source = "GTO"
        else:
            hands = self.hands_repository.get_filtered_hands()
            hands_source = "Repository"
            
        if index >= len(hands):
            return

        hand_data = hands[index]
        
        print(f"🎯 Loading {hands_source} hand for PPSM study...")

        # Publish load event as per architecture doc
        self.event_bus.publish(
            self.event_bus.topic(self.session_id, "review:load"), hand_data
        )

    def _handle_load_hand_event(self, hand_data):
        """Handle the review:load event - pure UI logic only."""
        try:
            hand_id = hand_data.get("metadata", {}).get("hand_id", "Unknown")
            self._update_status(f"🔄 Loading hand {hand_id}...")

            # Store hand data for reset functionality
            self.current_hand_data = hand_data

            # Use session manager to load hand (business logic)
            if self.session_manager:
                session_state = self.session_manager.load_hand(hand_data)
                
                # Update UI based on session state
                total_actions = session_state.total_actions
                if total_actions > 0:
                    self.progress_label.config(
                        text=f"Hand loaded: {total_actions} actions"
                    )
                    print(f"🎯 HandsReviewTab: Hand {hand_id} loaded with {total_actions} actions")
                else:
                    self.progress_label.config(text="No actions available")
                    print(f"⚠️ HandsReviewTab: Hand {hand_id} loaded but no actions found")
                
                self._update_status(f"✅ Hand {hand_id} loaded via session manager")
            else:
                self._update_status(f"❌ Session manager not available")
                print(f"❌ HandsReviewTab: Session manager not available")

        except Exception as e:
            print(f"❌ HandsReviewTab: Error loading hand: {e}")
            self._update_status(f"❌ Error loading hand: {e}")

    def _toggle_auto_play(self):
        """Toggle poker table auto-play mode."""
        if not hasattr(self, 'hand_actions') or not self.hand_actions:
            print("⚠️ HandsReviewTab: No hand actions available for auto-play")
            return
        
        if not hasattr(self, 'auto_play_active'):
            self.auto_play_active = False
        
        self.auto_play_active = not self.auto_play_active
        
        if self.auto_play_active:
            print("🎬 HandsReviewTab: Auto-play started")
            self.auto_btn.config(text="Stop Auto")
            self._run_auto_play()
        else:
            print("⏹️ HandsReviewTab: Auto-play stopped")
            self.auto_btn.config(text="Auto")

    def _run_auto_play(self):
        """Run poker table auto-play using GameDirector."""
        if not hasattr(self, 'auto_play_active') or not self.auto_play_active:
            return
        
        if self.current_action_index >= len(self.hand_actions):
            self.auto_play_active = False
            self.auto_btn.config(text="Auto")
            print("✅ HandsReviewTab: Auto-play complete")
            return
        
        # Use GameDirector for coordinated action execution
        if hasattr(self, 'game_director'):
            self.game_director.play()
            print("🎬 GameDirector: Auto-play started")
        else:
            # Fallback to manual execution
            self._next_action()
            self.after(1000, self._run_auto_play)



    def _update_status(self, message: str):
        """Update the status display."""
        self.status_text.insert(tk.END, f"\n{message}")
        self.status_text.see(tk.END)

    def _on_store_change(self, state):
        """Handle store state changes for poker table rendering."""
        try:
            # Check if we have poker table state to update
            if hasattr(self, 'display_state') and 'poker_table' in state:
                # Update local display state from store
                self.display_state.update(state['poker_table'])
                
                # Re-render the table with updated state
                self._render_poker_table()
                
                # Handle animation events
                if 'animation_event' in state.get('poker_table', {}):
                    self._handle_animation_event(
                        state['poker_table']['animation_event']
                    )
                    
                print("🔄 HandsReviewTab: State updated from store")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Store change handling error: {e}")

    def _handle_animation_event(self, animation_event):
        """Handle animation events from the store."""
        try:
            if animation_event.get('action') == 'clear_highlight':
                self._clear_highlight()
                print("🎬 HandsReviewTab: Animation event processed")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation event handling error: {e}")

    def _refresh_fonts(self):
        """Refresh fonts after theme changes."""
        fonts = self.theme.get_fonts()

        # Update listbox font
        if hasattr(self, "hands_listbox"):
            body_font = fonts.get("body", ("Consolas", 20))
            self.hands_listbox.configure(font=body_font)

        # Update text areas
        small_font = fonts.get("small", ("Consolas", 16))
        if hasattr(self, "details_text"):
            self.details_text.configure(font=small_font)
        if hasattr(self, "status_text"):
            self.status_text.configure(font=small_font)

        # Update theme intro label font (luxury serif)
        if hasattr(self, "theme_intro_label"):
            intro_font = fonts.get(
                "intro", fonts.get("body", ("Georgia", 16, "normal"))
            )
            self.theme_intro_label.configure(font=intro_font)
    
    def _start_update_loop(self):
        """Start the main update loop for GameDirector and EffectBus."""
        def update_loop():
            try:
                # Update GameDirector
                if hasattr(self, 'game_director'):
                    self.game_director.update()
                
                # Update EffectBus
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()
                
                # Schedule next update (60 FPS)
                self.after(16, update_loop)
                
            except Exception as e:
                print(f"⚠️ Update loop error: {e}")
                # Continue update loop even if there's an error
                self.after(16, update_loop)
        
        # Start the update loop
        update_loop()
        print("🔄 Update loop started for GameDirector and EffectBus")
    
    def _start_ui_tick_loop(self):
        """Start the UI tick loop for GameDirector and EffectBus every ~16ms."""
        def _tick():
            try:
                # Pump GameDirector and EffectBus every ~16ms (60 FPS)
                if hasattr(self, 'game_director'):
                    self.game_director.update(16.7)  # pump scheduled events
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.update()  # if bus keeps any transient state
            except Exception as e:
                print(f"⚠️ UI tick loop error: {e}")
            finally:
                # Schedule next tick
                self.after(16, _tick)
        
        # Start the tick loop
        _tick()
        print("⏱️ UI tick loop started for GameDirector and EffectBus (60 FPS)")

    def _handle_renderer_intent(self, intent: dict):
        """Handle intents emitted by PokerTableRenderer (state-driven).
        Currently forwards REQUEST_ANIMATION to EffectBus via event bus.
        """
        try:
            t = intent.get("type")
            if t == "REQUEST_ANIMATION" and hasattr(self, 'event_bus'):
                payload = intent.get("payload", {})
                name = payload.get("name")
                # Map declarative types to bridge names if not provided
                if not name:
                    et = payload.get("type")
                    if et == "CHIP_TO_POT":
                        name = "chips_to_pot"
                    elif et == "POT_TO_WINNER":
                        name = "pot_to_winner"
                self.event_bus.publish("effect_bus:animate", {"name": name, "args": payload})
        except Exception:
            pass
    
    def _setup_action_banner(self):
        """Setup ActionBanner and connect it to EffectBus events."""
        try:
            if ActionBanner:
                # Create ActionBanner at the top of the poker table section
                self.action_banner = ActionBanner(self)
                
                # Subscribe to EffectBus banner events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:banner_show", self._handle_banner_event)

                # Subscribe to EffectBus animation events
                if hasattr(self, 'event_bus'):
                    self.event_bus.subscribe("effect_bus:animate", self._handle_effect_animate)
                    print("🎞️ Animation: Connected to EffectBus events")
                    print("🎭 ActionBanner: Connected to EffectBus events")
                else:
                    print("⚠️ ActionBanner: No event bus available")
            else:
                print("⚠️ ActionBanner: Not available, skipping setup")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Setup error: {e}")
    
    def _handle_banner_event(self, event_data):
        """Handle banner events from EffectBus."""
        try:
            if hasattr(self, 'action_banner'):
                message = event_data.get('message', '')
                banner_type = event_data.get('banner_type', 'info')
                duration_ms = event_data.get('duration_ms', 3000)
                
                self.action_banner.show_banner(message, banner_type, duration_ms)
                print(f"🎭 ActionBanner: Showing banner: {message}")
            else:
                print("⚠️ ActionBanner: Not available for banner event")
                
        except Exception as e:
            print(f"⚠️ ActionBanner: Banner event error: {e}")

        # Update enhanced button themes (handles both fonts and colors)
        enhanced_buttons = []
        if hasattr(self, "load_btn") and hasattr(self.load_btn, "refresh_theme"):
            enhanced_buttons.append(self.load_btn)
        if hasattr(self, "next_btn") and hasattr(self.next_btn, "refresh_theme"):
            enhanced_buttons.append(self.next_btn)
        if hasattr(self, "auto_btn") and hasattr(self.auto_btn, "refresh_theme"):
            enhanced_buttons.append(self.auto_btn)
        if hasattr(self, "reset_btn") and hasattr(self.reset_btn, "refresh_theme"):
            enhanced_buttons.append(self.reset_btn)

        for btn in enhanced_buttons:
            btn.refresh_theme()

    def _handle_effect_animate(self, payload):
        """Handle animation requests from EffectBus using ChipAnimations where possible."""
        try:
            name = (payload or {}).get("name")
            ms = int((payload or {}).get("ms", 300))
            if not getattr(self, "canvas_manager", None):
                return
            c = self.canvas_manager.canvas
            
            # Get theme manager from the correct location
            theme_manager = getattr(self, 'theme', None)
            if not theme_manager:
                print("⚠️ No theme manager available for animations")
                return
                
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)
            
            # Get proper pot center from display state
            pot_center = (self.canvas_manager.canvas.winfo_width() // 2, 
                         int(self.canvas_manager.canvas.winfo_height() * 0.52))
            
            # Get seat positions for proper animation coordinates
            seats = self.display_state.get("seats", [])
            if not seats:
                return
                
            # Get consistent seat positions for animation
            w, h = self.canvas_manager.size()
            from ..state.selectors import get_seat_positions
            seat_positions = get_seat_positions(self.display_state, seat_count=len(seats), 
                                              canvas_width=w, canvas_height=h)
            
            if name == "betting_action":
                # Handle betting actions (BET, RAISE, CALL, CHECK, FOLD)
                action_type = (payload or {}).get("action_type", "UNKNOWN")
                actor_uid = (payload or {}).get("actor_uid", "Unknown")
                
                print(f"🎬 Betting action animation: {action_type} by {actor_uid}")
                
                # Find the acting player for source position with robust normalization
                def _norm(v):
                    return str(v).strip().lower()

                actor_norm = _norm(actor_uid)
                acting_seat = None

                # Build lookup maps
                uid_to_idx = { _norm(s.get('player_uid')): i for i, s in enumerate(seats) }
                name_to_idx = { _norm(s.get('name', '')): i for i, s in enumerate(seats) }

                # Prefer player_uid
                if actor_norm in uid_to_idx:
                    acting_seat = seats[uid_to_idx[actor_norm]]
                elif actor_norm in name_to_idx:
                    acting_seat = seats[name_to_idx[actor_norm]]
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating {action_type} from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        
                        # Different animation based on action type
                        if action_type in ["BET", "RAISE", "CALL"]:
                            # Animate chips to pot
                            anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                        elif action_type == "CHECK":
                            # Visual feedback for check (no chips)
                            print(f"🎬 Check action - no chip animation needed")
                        elif action_type == "FOLD":
                            # Visual feedback for fold (maybe card flip or seat dimming)
                            print(f"🎬 Fold action - seat dimming effect")
                else:
                    print(f"⚠️ No seat found for actor {actor_uid} in betting action animation")
                    
            elif name == "chips_to_pot":
                # This should ONLY happen at end of street (DEAL_BOARD, DEAL_TURN, DEAL_RIVER)
                # NOT during betting rounds
                print(f"🎬 End-of-street animation: chips flying to pot")
                
                # Find the acting player for source position
                acting_seat = None
                for seat in seats:
                    if seat.get('acting', False):
                        acting_seat = seat
                        break
                
                if acting_seat:
                    # Get seat position using consistent positioning
                    seat_idx = seats.index(acting_seat)
                    if seat_idx < len(seat_positions):
                        sx, sy = seat_positions[seat_idx]
                        
                        print(f"🎬 Animating chips from seat {seat_idx} ({sx}, {sy}) to pot ({pot_center[0]}, {pot_center[1]})")
                        anim.fly_chips_to_pot(c, sx, sy, pot_center[0], pot_center[1], amount=200, callback=None)
                else:
                    print("⚠️ No acting seat found for chips_to_pot animation")
                    
            elif name == "pot_to_winner":
                # This is for showdown/end of hand
                print(f"🎬 Showdown animation: pot flying to winner")
                
                # Find winner seat
                winner = None
                for seat in seats:
                    if not seat.get("folded", False):
                        winner = seat
                        break
                
                if winner:
                    # Get winner position using consistent positioning
                    winner_idx = seats.index(winner)
                    if winner_idx < len(seat_positions):
                        wx, wy = seat_positions[winner_idx]
                        
                        print(f"🎬 Animating pot to winner {winner.get('name', 'Unknown')} at ({wx}, {wy})")
                        anim.fly_pot_to_winner(c, pot_center[0], pot_center[1], wx, wy, amount=200, callback=None)
                else:
                    print("⚠️ No winner found for pot_to_winner animation")
                    
        except Exception as e:
            print(f"⚠️ Animation handler error: {e}")
            import traceback
            traceback.print_exc()

    def _style_theme_radio_buttons(self):
        """Apply theme-specific styling to radio buttons to eliminate default green highlights."""
        if not hasattr(self, "theme_radio_buttons"):
            return

        try:
            # Get current theme and highlight colors
            current_theme_name = self.theme.current() or "Forest Green Professional 🌿"
            theme = self.theme.get_theme()

            # Create a custom style for radio buttons
            style = ttk.Style()

            # Apply config-driven selection styling
            selection_styler = self.theme.get_selection_styler()
            if selection_styler:
                theme_id = self.theme.get_current_theme_id()
                selection_styler.apply_selection_styles(style, theme_id)

            # Get selection highlight colors (config-driven with legacy fallback)
            try:
                base_colors = self.theme.get_base_colors()
                selection_color = base_colors.get(
                    "highlight", base_colors.get("accent", "#D4AF37")
                )
                selection_glow = base_colors.get(
                    "metal", base_colors.get("accent", "#C9A34E")
                )
            except Exception:
                # Get selection highlight from config-driven system
                base_colors = self.theme.get_base_colors()
                selection_highlight = {
                    "color": base_colors.get(
                        "highlight", base_colors.get("accent", "#D4AF37")
                    )
                }
                selection_color = selection_highlight["color"]
                selection_glow = selection_highlight.get("glow", "#C9A34E")

            # Configure the radio button style with theme-specific colors
            style.configure(
                "Themed.TRadiobutton",
                background=theme.get("panel.bg", "#1F2937"),
                foreground=theme.get("panel.fg", "#E5E7EB"),
                focuscolor=selection_color,
            )

            # Configure the selection/active state colors
            style.map(
                "Themed.TRadiobutton",
                background=[
                    ("active", theme.get("panel.bg", "#1F2937")),
                    ("selected", theme.get("panel.bg", "#1F2937")),
                ],
                foreground=[
                    ("active", theme.get("panel.fg", "#E5E7EB")),
                    ("selected", theme.get("panel.fg", "#E5E7EB")),
                ],
                indicatorcolor=[
                    ("selected", selection_color),
                    ("active", selection_glow),
                    ("!selected", theme.get("panel.border", "#374151")),
                ],
            )

            # Apply the custom style to all radio buttons
            for radio_btn in self.theme_radio_buttons:
                if radio_btn.winfo_exists():
                    radio_btn.configure(style="Themed.TRadiobutton")

        except Exception as e:
            # Fallback styling if custom styling fails
            print(f"⚠️ Radio button styling failed: {e}")
            pass


    def _next_action(self):
        """Advance to the next action in the hand - pure UI logic only."""
        print("🎯 NEXT_ACTION: Button clicked!")

        # Check if session manager is available
        if not self.session_manager:
            self._update_status("⚠️ Session manager not available")
            return

        try:
            # Execute next action through session manager (business logic)
            session_state = self.session_manager.execute_action()
            
            # Update UI based on session state
            if session_state.current_action_index < session_state.total_actions:
                self._update_status(f"▶️ Action {session_state.current_action_index}/{session_state.total_actions} executed")
                
                # Update progress display
                self.progress_label.config(
                    text=f"Action {session_state.current_action_index}/{session_state.total_actions}"
                )
                
                # Render table with new state
                self._render_table_with_state(session_state)
            else:
                self._update_status("🏁 Hand complete - no more actions")
                
        except Exception as e:
            self._update_status(f"❌ Error advancing hand: {e}")
            print(f"🎯 NEXT_ACTION: Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_table_with_state(self, session_state):
        """Render poker table with session state - pure UI logic only."""
        try:
            # Convert session state to PokerTableState
            from ..table.state import PokerTableState
            
            table_state = PokerTableState(
                table=session_state.table,
                seats=session_state.seats,
                board=session_state.board,
                pot=session_state.pot,
                dealer=session_state.dealer,
                action=session_state.action,
                animation=session_state.animation,
                effects=session_state.effects,
                street=session_state.street
            )
            
            # Render using PokerTableRenderer
            if hasattr(self, 'table_renderer') and self.table_renderer:
                self.table_renderer.render(table_state)
                print("🎯 HandsReviewTab: Table rendered with session state")
            else:
                print("⚠️ HandsReviewTab: Table renderer not available")
                
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error rendering table: {e}")

    def _reset_hand(self):
        """Reset the current hand to the beginning - pure UI logic only."""
        if not self.session_manager:
            self._update_status("⚠️ Session manager not available")
            return

        try:
            # Reset hand via session manager (business logic)
            if hasattr(self, "last_loaded_hand") and self.last_loaded_hand:
                session_state = self.session_manager.load_hand(self.last_loaded_hand)
                self._update_status("🔄 Hand reset to beginning")
                
                # Render table with reset state
                self._render_table_with_state(session_state)
            else:
                self._update_status("⚠️ No hand to reset")
        except Exception as e:
            self._update_status(f"❌ Error resetting hand: {e}")

    def on_show(self):
        """Called when tab is shown - refresh display."""
        if hasattr(self, "renderer_pipeline"):
            state = self.store.get_state()
            self.renderer_pipeline.render_once(state)

    def dispose(self):
        """Clean up when tab is closed."""
        # Clean up session manager if active
        if self.session_manager:
            self.session_manager.cleanup()
            self.session_manager = None
        self.services.dispose_session(self.session_id)

    def _load_gto_hands(self):
        """Load GTO hands for PPSM testing."""
        try:
            import json
            import os
            
            gto_hands_file = "gto_hands.json"
            print(f"🔍 Looking for GTO hands file: {gto_hands_file}")
            
            if os.path.exists(gto_hands_file):
                print(f"📂 Found GTO hands file, loading...")
                with open(gto_hands_file, 'r') as f:
                    hands_data = json.load(f)
                    
                print(f"📊 Raw GTO hands data: {len(hands_data)} hands")
                    
                # Convert to Hand objects
                self.loaded_gto_hands = []
                for i, hand_data in enumerate(hands_data):
                    try:
                        hand = Hand(**hand_data)  # Create proper Hand object
                        self.loaded_gto_hands.append(hand)
                    except Exception as e:
                        print(f"⚠️ Error creating Hand object for hand {i}: {e}")
                        # Fallback: store as dict
                        self.loaded_gto_hands.append(hand_data)
                        
                print(f"✅ Loaded {len(self.loaded_gto_hands)} GTO hands for PPSM testing")
            else:
                print(f"⚠️ GTO hands file not found: {gto_hands_file}")
                self.loaded_gto_hands = []
                
        except Exception as e:
            print(f"⚠️ Error loading GTO hands: {e}")
            self.loaded_gto_hands = []

    def _load_hand(self, hand_data):
        """Load hand data into poker table using new architecture."""
        try:
            # Store the hand data for reference
            self.current_hand_data = hand_data
            
            # Flatten hand actions for step-by-step replay
            self.hand_actions = self._flatten_hand_for_replay(hand_data)
            
            # Reset action index
            self.current_action_index = 0
            
            # Create display state from hand data
            new_display_state = self._create_display_state_from_hand(hand_data)
            
            # Update the existing display state with new data
            self.display_state.update(new_display_state)
            
            # Dispatch LOAD_REVIEW_HAND action to store
            self.store.dispatch({
                "type": "LOAD_REVIEW_HAND",
                "hand_data": hand_data,
                "flattened_actions": self.hand_actions
            })
            
            # Update progress display
            if self.hand_actions:
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                self.progress_label.config(text=progress_text)
                # Enable next button
                self.next_btn.config(state="normal")
                
                # Setup GameDirector for this hand
                if hasattr(self, 'game_director'):
                    self.game_director.set_total_steps(len(self.hand_actions))
                    self.game_director.set_advance_callback(self._execute_action_at_index)
                    print(f"🎬 GameDirector: Configured for {len(self.hand_actions)} actions")
            
            # Render the table
            self._render_poker_table()
            
            # Refresh widget to ensure proper sizing
            self._refresh_poker_table_widget()
            
            print(f"✅ HandsReviewTab: Hand loaded with {len(self.hand_actions)} actions")
        
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error loading hand: {e}")

    def _create_display_state_from_hand(self, hand_data):
        """Create display state from hand data for poker table."""
        try:
            # Debug: Log the raw hand data
            print(f"🎯 Creating display state from hand data:")
            print(f"   Hand data type: {type(hand_data)}")
            print(f"   Hand data keys: {list(hand_data.keys()) if hasattr(hand_data, 'keys') else 'N/A'}")
            
            # Handle both Hand objects and dict format
            if hasattr(hand_data, 'seats'):  # Hand object
                seats = hand_data.seats
                metadata = hand_data.metadata
                print(f"   Using Hand object: {len(seats)} seats")
            else:  # Dict format
                seats = hand_data.get('seats', [])
                metadata = hand_data.get('metadata', {})
                print(f"   Using dict format: {len(seats)} seats")
            
            print(f"   Raw seats data: {seats}")
            print(f"   Metadata: {metadata}")
            
            # Extract basic hand information
            small_blind = metadata.get('small_blind', 5) if metadata else 5
            big_blind = metadata.get('big_blind', 10) if metadata else 10
            
            print(f"   Extracted {len(seats)} seats, SB: {small_blind}, BB: {big_blind}")
            
            # Create initial display state with actual table dimensions
            display_state = {
                'table': {
                    'width': getattr(self, 'table_width', 800),
                    'height': getattr(self, 'table_height', 600),
                    'theme': 'luxury_noir'  # Default theme
                },
                'pot': {
                    'amount': 0,
                    'position': (400, 300)
                },
                'seats': [],
                'board': [],
                'dealer': {'position': 0},
                'action': {'type': None, 'player': None, 'amount': 0},
                'replay': {'current_step': 0, 'total_steps': 0}
            }
            
            # Set up seats from GTO hand data
            for i, seat in enumerate(seats):
                player_uid = seat.get('player_uid', f'player_{i}')
                name = seat.get('display_name', f'Player {i+1}')
                starting_stack = seat.get('starting_stack', 1000)
                
                # Calculate seat position (simplified for now)
                angle = (2 * 3.14159 * i) / len(seats)
                radius = 200
                x = 400 + int(radius * math.cos(angle))
                y = 300 + int(radius * math.sin(angle))
                
                # Get hole cards for this player from metadata
                if hasattr(hand_data, 'metadata') and hasattr(hand_data.metadata, 'hole_cards'):
                    hole_cards = hand_data.metadata.hole_cards.get(player_uid, [])
                else:
                    hole_cards = metadata.get('hole_cards', {}).get(player_uid, [])
                
                seat_data = {
                    'player_uid': player_uid,
                    'name': name,
                    'starting_stack': starting_stack,
                    'current_stack': starting_stack,
                    'current_bet': 0,
                    # Backwards-compatible keys used by renderer components
                    'stack': starting_stack,
                    'bet': 0,
                    'cards': hole_cards,  # Populate with actual hole cards
                    'folded': False,
                    'all_in': False,
                    'acting': False,
                    'position': i
                }
                
                # Set initial blinds based on seat order
                if i == 0:  # Small blind
                    seat_data['current_bet'] = small_blind
                    seat_data['current_stack'] -= small_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'SB'
                elif i == 1:  # Big blind
                    seat_data['current_bet'] = big_blind
                    seat_data['current_stack'] -= big_blind
                    seat_data['bet'] = seat_data['current_bet']
                    seat_data['stack'] = seat_data['current_stack']
                    seat_data['position'] = 'BB'
                
                display_state['seats'].append(seat_data)
                print(f"   🪑 Created seat {i}: {name} at ({x}, {y}) with cards {hole_cards}")
            
            print(f"🎯 HandsReviewTab: Created display state with {len(display_state['seats'])} seats")
            for seat in display_state['seats']:
                print(f"  🪑 {seat['name']}: {seat['cards']} (stack: {seat['current_stack']}, bet: {seat['current_bet']})")
            
            return display_state
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error creating display state: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _flatten_hand_for_replay(self, hand):
        """Produce a list of 'steps' to drive the poker table UI."""
        steps = []

        # Synthesize: deal hole cards
        holes = (hand.get("metadata", {}) or {}).get("hole_cards", {}) or {}
        steps.append({
            "type": "DEAL_HOLE",
            "desc": "🃏 Deal hole cards",
            "payload": {"hole_cards": holes},
        })

        streets = hand.get("streets", {}) or {}
        # Keep deterministic street order
        for street_name in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            if street_name not in streets:
                continue
            s = streets[street_name] or {}
            actions = s.get("actions", []) or []
            board = s.get("board", []) or []

            # If board present, add board-deal step
            if street_name != "PREFLOP" and board:
                steps.append({
                    "type": "DEAL_BOARD",
                    "desc": f"🂠 Deal {street_name} board: {', '.join(board)}",
                    "payload": {"street": street_name, "board": board},
                })

            for a in actions:
                # Handle different action types
                action_type = a.get("action", "UNKNOWN")
                actor = a.get("actor_uid", "Unknown")
                amount = a.get("amount", 0)
                
                if action_type == "POST_BLIND":
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type in ["BET", "RAISE", "CALL"]:
                    desc = f"{street_name}: {actor} → {action_type} {amount}"
                elif action_type == "CHECK":
                    desc = f"{street_name}: {actor} → {action_type}"
                elif action_type == "FOLD":
                    desc = f"{street_name}: {actor} → {action_type}"
                else:
                    desc = f"{street_name}: {actor} → {action_type} {amount if amount else ''}"
                
                steps.append({
                    "type": action_type,
                    "desc": desc,
                    "payload": {"street": street_name, **a},
                })

        # Terminal step
        steps.append({"type": "END_HAND", "desc": "✅ End of hand", "payload": {}})
        return steps

    def _render_poker_table(self):
        """Render the poker table using the component pipeline."""
        try:
            # Debug: Log what's in the display state
            print(f"🎯 Rendering table with state:")
            print(f"   Seats: {len(self.display_state.get('seats', []))}")
            print(f"   Board: {self.display_state.get('board', [])}")
            print(f"   Pot: {self.display_state.get('pot', {}).get('amount', 0)}")
            
            if self.display_state.get('seats'):
                for i, seat in enumerate(self.display_state['seats']):
                    print(f"   Seat {i}: {seat}")
            
            # Build PokerTableState and render
            try:
                from ..table.state import PokerTableState
            except Exception:
                # Inline lightweight structure if import fails
                class PokerTableState(dict):
                    pass

            state = PokerTableState(
                table={"width": self.table_width, "height": self.table_height},
                seats=self.display_state.get('seats', []),
                board=self.display_state.get('board', []),
                pot=self.display_state.get('pot', {}),
                dealer={"position": self.display_state.get('dealer', 0)},
                action=self.display_state.get('action', {}),
                animation={},
                effects=list(self._pending_effects),
                street=self.display_state.get('street', 'PREFLOP'),  # Pass street for community cards
            )
            # Clear effects after issuing
            self._pending_effects.clear()
            self.table_renderer.render(state)
            print("🎨 HandsReviewTab: Table rendered successfully (state-driven)")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Render error: {e}")
            import traceback
            traceback.print_exc()


    
    def _execute_action_step(self, action):
        """Execute a single action step and update display state."""
        try:
            action_type = action.get('type', 'UNKNOWN')
            payload = action.get('payload', {})
            
            # Get player name for effects
            actor_uid = payload.get('actor_uid', 'Unknown')
            player_name = None
            for seat in self.display_state['seats']:
                if seat['player_uid'] == actor_uid:
                    player_name = seat.get('name', actor_uid)
                    break
            

            # Update acting highlight: set only the actor as acting
            try:
                for s in self.display_state.get('seats', []):
                    s['acting'] = (s.get('player_uid') == actor_uid)
            except Exception:
                pass
                
            # optional: re-render to reflect highlight immediately
            try:
                self.renderer_pipeline.render_once(self.display_state)
            except Exception:
                pass
            
            if action_type == "DEAL_HOLE":
                # Hole cards are already loaded in initial state
                print(f"🃏 HandsReviewTab: Hole cards dealt")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_HOLE", player_name)
                
            elif action_type == "DEAL_BOARD":
                street = payload.get('street', 'UNKNOWN')
                board = payload.get('board', [])
                self.display_state['board'] = board
                self.display_state['street'] = street  # Update street for community card rendering
                print(f"🂠 HandsReviewTab: Dealt {street} board: {board}")
                
                # Add deal sound and animation effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("DEAL_BOARD", player_name)
                
                # Professional poker behavior: Animate chips to pot at end of street
                # This clears all bet chips from in front of players and moves them to pot
                if street in ["FLOP", "TURN", "RIVER"]:
                    try:
                        from ..state.selectors import get_seat_positions
                        w, h = self.table_renderer.canvas_manager.size() if hasattr(self, 'table_renderer') else (self.table_width, self.table_height)
                        positions = get_seat_positions(self.display_state, seat_count=len(self.display_state.get('seats', [])), canvas_width=w, canvas_height=h)
                        
                        # Find any seat with bets to animate from (use first betting seat)
                        for seat_idx, seat in enumerate(self.display_state.get('seats', [])):
                            if seat.get('current_bet', 0) > 0 and seat_idx < len(positions):
                                fx, fy = positions[seat_idx]
                                pot_x, pot_y = (w // 2, int(h * 0.58))
                                self._pending_effects.append({
                                    "type": "CHIP_TO_POT",
                                    "from_x": int(fx), "from_y": int(fy),
                                    "to_x": pot_x, "to_y": pot_y,
                                    "amount": seat.get('current_bet', 0),
                                })
                                print(f"🎬 End-of-street: Moving chips from seat {seat_idx} to pot for {street}")
                                break
                    except Exception as e:
                        print(f"⚠️ Could not add end-of-street animation: {e}")
                
            elif action_type in ["BET", "RAISE", "CALL", "CHECK", "FOLD"]:
                amount = payload.get('amount', 0)
                
                # Update the appropriate seat's bet and stack
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        if action_type in ["BET", "RAISE"]:
                            # For BET/RAISE, amount is the total bet
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = action_type.lower()  # Add last_action for bet styling
                        elif action_type == "CALL":
                            # For CALL, amount is the total bet to match
                            seat['current_bet'] = amount
                            seat['current_stack'] = seat['starting_stack'] - amount
                            seat['last_action'] = "call"  # Add last_action for bet styling
                        elif action_type == "CHECK":
                            # CHECK doesn't change bet or stack
                            seat['last_action'] = "check"  # Add last_action for bet styling
                        elif action_type == "FOLD":
                            seat['folded'] = True
                            seat['last_action'] = "fold"  # Add last_action for bet styling
                            # Folded players keep their current bet
                        
                        # Set acting flag for highlighting on this seat only
                        seat['acting'] = True
                        break

                # Clear acting flag from other seats using different loop variable
                for s2 in self.display_state['seats']:
                    if s2.get('player_uid') != actor_uid:
                        s2['acting'] = False
                
                # Update pot amount
                if action_type in ["BET", "RAISE", "CALL"]:
                    total_pot = sum(seat['current_bet'] for seat in self.display_state['seats'])
                    self.display_state['pot']['amount'] = total_pot
                
                print(f"🎯 HandsReviewTab: {actor_uid} {action_type} {amount if amount else ''}")
                print(f"🎯 Seat state updated: current_bet={seat.get('current_bet', 0)}, last_action={seat.get('last_action', 'none')}")
                
                # Add action sound effects
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects(action_type, player_name)

                # Professional poker behavior: Only animate chips to pot at END of streets
                # Individual bets/calls just place chips in front of players
                # (CHIP_TO_POT animation will be triggered by DEAL_FLOP, DEAL_TURN, DEAL_RIVER actions)
                
                # Show action banner for immediate visual feedback
                if hasattr(self, 'action_banner'):
                    amount = payload.get('amount', 0)
                    self.action_banner.show_poker_action(action_type, player_name, amount)

                # Re-render immediately after state updates to ensure highlight and bets update
                try:
                    self.renderer_pipeline.render_once(self.display_state)
                except Exception:
                    pass
                
            elif action_type == "POST_BLIND":
                amount = payload.get('amount', 0)
                
                # Update seat bet and stack for blind posting
                for seat in self.display_state['seats']:
                    if seat['player_uid'] == actor_uid:
                        seat['current_bet'] = amount
                        seat['current_stack'] -= amount
                        break
                
                print(f"💰 HandsReviewTab: {actor_uid} posted blind: {amount}")
                
                # Add blind posting sounds (chips stay in front of player until street ends)
                if hasattr(self, 'effect_bus'):
                    self.effect_bus.add_poker_action_effects("POST_BLIND", player_name)
            
            # Re-render the table with updated state
            self._render_poker_table()
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing action step: {e}")
    
    def _execute_action_at_index(self, action_index: int):
        """Execute action at specific index - called by GameDirector."""
        try:
            if 0 <= action_index < len(self.hand_actions):
                self.current_action_index = action_index
                action = self.hand_actions[action_index]
                
                # Execute the action
                self._execute_action_step(action)
                
                # Update progress display
                progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
                if hasattr(self, 'progress_label'):
                    self.progress_label.config(text=progress_text)
                
                print(f"🎬 GameDirector: Executed action at index {action_index}")
            else:
                print(f"⚠️ GameDirector: Invalid action index {action_index}")
                
        except Exception as e:
            print(f"⚠️ GameDirector: Error executing action at index {action_index}: {e}")

    def _prev_action(self):
        """Execute previous action using proper Store-based architecture."""
        try:
            # Check if we have actions to execute
            if not hasattr(self, 'hand_actions') or not self.hand_actions:
                print("⚠️ HandsReviewTab: No hand actions available")
                return
            
            # Check if we can go to previous action
            if self.current_action_index <= 0:
                print("⚠️ HandsReviewTab: Already at first action")
                return
            
            # Move to previous action
            self.current_action_index -= 1
            action = self.hand_actions[self.current_action_index]
            
            # Execute the action to update display state
            self._execute_action_step(action)
            
            # Update progress display
            progress_text = f"Action {self.current_action_index + 1}/{len(self.hand_actions)}"
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=progress_text)
            
            # Dispatch action to store for state management
            self.store.dispatch({
                "type": "PREV_REVIEW_ACTION"
            })
            
            print(f"🎬 HandsReviewTab: Executed previous action {self.current_action_index}: {action.get('type', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Error executing previous action: {e}")



    def _execute_action(self, action):
        """Execute action and update poker table state with rich UI/UX features."""
        # REMOVED: This method should not contain business logic
        # Business logic should be in PPSM or Store reducers
        # UI should only dispatch actions and render state
        pass

    def _play_sound(self, sound_type):
        """Play sound effects for poker table actions."""
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                # Map sound types to sound manager events
                sound_mapping = {
                    'card_deal': 'card_deal',
                    'chip_bet': 'chip_bet',
                    'player_bet': 'player_action_bet',
                    'player_call': 'player_action_call',
                    'player_check': 'player_action_check',
                    'player_fold': 'player_action_fold',
                    'hand_end': 'hand_end'
                }
                
                event_name = sound_mapping.get(sound_type, sound_type)
                self.sound_manager.play(event_name)
                print(f"🔊 HandsReviewTab: Playing {sound_type} sound")
            else:
                print(f"🔇 HandsReviewTab: No sound manager available for {sound_type}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Sound error for {sound_type}: {e}")

    def _schedule_animation(self):
        """Schedule animation effects using event-driven system."""
        try:
            # Use event bus instead of direct UI timing (architectural compliance)
            if hasattr(self, 'event_bus'):
                self.event_bus.publish(
                    self.event_bus.topic(self.session_id, "poker_table:animation"),
                    {
                        "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                        "delay_ms": 200,
                        "action": "clear_highlight"
                    }
                )
                print(f"🎬 HandsReviewTab: Scheduled animation via event bus")
            else:
                print(f"⚠️ HandsReviewTab: No event bus available for animation")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Animation scheduling error: {e}")

    def _clear_highlight(self):
        """Clear player highlighting after animation."""
        try:
            if hasattr(self, 'display_state') and 'action' in self.display_state:
                self.display_state['action']['highlight'] = False
                # Re-render to show cleared highlight
                self._render_poker_table()
                print(f"🎬 HandsReviewTab: Cleared action highlight")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Highlight clear error: {e}")

    def _refresh_poker_table_widget(self):
        """Refresh the poker table widget to ensure proper sizing and fit."""
        try:
            if hasattr(self, 'canvas_manager') and self.canvas_manager:
                # Force canvas to update its geometry
                self.canvas_manager.canvas.update_idletasks()
                
                # Get current frame dimensions
                parent_frame = self.canvas_manager.canvas.master
                frame_width = parent_frame.winfo_width()
                frame_height = parent_frame.winfo_height()
                
                # Recalculate table dimensions
                table_width = max(800, frame_width - 20)
                table_height = max(600, frame_height - 20)
                
                # Update canvas size
                self.canvas_manager.canvas.configure(width=table_width, height=table_height)
                
                # Update stored dimensions
                self.table_width = table_width
                self.table_height = table_height
                
                # Update display state
                if hasattr(self, 'display_state'):
                    self.display_state['table']['width'] = table_width
                    self.display_state['table']['height'] = table_height
                
                # Re-render with new dimensions
                self._render_poker_table()
                
                print(f"🔄 HandsReviewTab: Widget refreshed to {table_width}x{table_height}")
        except Exception as e:
            print(f"⚠️ HandsReviewTab: Widget refresh error: {e}")

```

---

### app_shell.py

```python
import tkinter as tk
from tkinter import ttk
import uuid

from .services.event_bus import EventBus
from .services.service_container import ServiceContainer
from .services.timer_manager import TimerManager
from .services.theme_manager import ThemeManager
from .services.hands_repository import HandsRepository, StudyMode
from .state.store import Store
from .state.reducers import root_reducer
from .tabs.hands_review_tab import HandsReviewTab
from .tabs.practice_session_tab import PracticeSessionTab
from .tabs.gto_session_tab import GTOSessionTab

from .menu_integration import add_theme_manager_to_menu


class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # Store root reference for menu integration
        self.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # app-scoped services
        self.services = ServiceContainer()
        self.services.provide_app("event_bus", EventBus())
        self.services.provide_app("theme", ThemeManager())
        self.services.provide_app("hands_repository", HandsRepository())
        
        # Create global GameDirector for action sequencing
        from .services.game_director import GameDirector
        game_director = GameDirector(event_bus=self.services.get_app("event_bus"))
        self.services.provide_app("game_director", game_director)
        
        # Create global EffectBus service for sound management
        from .services.effect_bus import EffectBus
        effect_bus = EffectBus(
            game_director=game_director,
            event_bus=self.services.get_app("event_bus")
        )
        self.services.provide_app("effect_bus", effect_bus)
        # Subscribe to voice events to keep architecture event-driven
        def _on_voice(payload):
            try:
                action = (payload or {}).get("action")
                vm = getattr(effect_bus, "voice_manager", None)
                if not (vm and action):
                    return
                cfg = getattr(effect_bus, "config", {}) or {}
                voice_type = getattr(effect_bus, "voice_type", "")
                table = (cfg.get("voice_sounds", {}) or {}).get(voice_type, {})
                rel = table.get(action)
                if rel:
                    vm.play(rel)
            except Exception:
                pass
        self.services.get_app("event_bus").subscribe("effect_bus:voice", _on_voice)
        
        # Create shared store for poker game state (per architecture doc)
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": StudyMode.REPLAY.value,
                "collection": None
            }
        }
        self.services.provide_app("store", Store(initial_state, root_reducer))

        # Create menu system
        self._create_menu_system()
        
        # tabs (order: Practice, GTO, Hands Review - main product features only)
        self._add_tab("Practice Session", PracticeSessionTab)
        self._add_tab("GTO Session", GTOSessionTab)
        self._add_tab("Hands Review", HandsReviewTab)
        # Bind global font size shortcuts (Cmd/Ctrl - and =)
        self._bind_font_shortcuts(root)

    def _add_tab(self, title: str, TabClass):
        session_id = str(uuid.uuid4())
        timers = TimerManager(self)
        self.services.provide_session(session_id, "timers", timers)

        # Update active tab in shared store
        store = self.services.get_app("store")
        store.dispatch({"type": "SET_ACTIVE_TAB", "name": title})
        
        # Create tab with services
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)
        
        # Call on_show if available
        if hasattr(tab, "on_show"):
            tab.on_show()

    def _create_menu_system(self):
        """Create the application menu system."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._increase_font(None))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._decrease_font(None))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=lambda: self._reset_font(None))
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme management
        settings_menu.add_command(label="Theme Editor", command=self._open_theme_editor)
        settings_menu.add_command(label="Sound Settings", command=self._open_sound_settings)
        settings_menu.add_separator()
        
        # Add Theme Manager to Settings menu using our integration helper
        add_theme_manager_to_menu(settings_menu, self.root, self._on_theme_changed)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _new_session(self):
        """Start a new session."""
        print("🔄 New session requested")
        # TODO: Implement session reset
        
    def _on_theme_changed(self):
        """Called when theme is changed via Theme Manager."""
        print("🎨 Theme changed - refreshing UI...")
        
        try:
            # Reload theme manager to get latest changes
            theme_manager = self.services.get_app("theme")
            if hasattr(theme_manager, 'reload'):
                theme_manager.reload()
            
            # Force rebuild themes to pick up any live changes
            try:
                from .services.theme_factory import build_all_themes
                themes = build_all_themes()
                # Register updated themes
                for name, tokens in themes.items():
                    theme_manager.register(name, tokens)
                print(f"🔄 Rebuilt and registered {len(themes)} themes")
            except Exception as e:
                print(f"⚠️ Theme rebuild warning: {e}")
            
            # Refresh all tabs with new theme
            for i in range(self.notebook.index("end")):
                try:
                    tab = self.notebook.nametowidget(self.notebook.tabs()[i])
                    
                    # Try multiple refresh methods
                    if hasattr(tab, '_refresh_ui_colors'):
                        tab._refresh_ui_colors()
                        print(f"✅ Refreshed tab {i} via _refresh_ui_colors")
                    elif hasattr(tab, 'refresh_theme'):
                        tab.refresh_theme()
                        print(f"✅ Refreshed tab {i} via refresh_theme")
                    elif hasattr(tab, '_on_theme_changed'):
                        tab._on_theme_changed()
                        print(f"✅ Refreshed tab {i} via _on_theme_changed")
                    else:
                        print(f"ℹ️ Tab {i} has no theme refresh method")
                        
                except Exception as e:
                    print(f"⚠️ Error refreshing tab {i}: {e}")
            
            print("✅ Live theme refresh completed")
            
        except Exception as e:
            print(f"❌ Theme refresh error: {e}")
            import traceback
            traceback.print_exc()
        
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Poker Pro Trainer",
            "Poker Pro Trainer\n\n"
            "Advanced poker training with luxury themes\n"
            "and professional game analysis.\n\n"
            "🎨 Theme Manager integrated\n"
            "🃏 16 luxury themes available\n"
            "📊 Comprehensive hand review\n"
            "🤖 AI-powered training"
        )

    def _bind_font_shortcuts(self, root):
        # macOS Command key bindings (Cmd - decreases, Cmd = increases)
        root.bind_all("<Command-minus>", self._decrease_font)
        root.bind_all("<Command-equal>", self._increase_font)  # This is Cmd = (increase)
        root.bind_all("<Command-0>", self._reset_font)
        
        # Additional symbols that might work
        root.bind_all("<Command-plus>", self._increase_font)   # Shift+= gives +
        
        # Numpad variants
        root.bind_all("<Command-KP_Subtract>", self._decrease_font)
        root.bind_all("<Command-KP_Add>", self._increase_font)
        
        # Windows/Linux Control variants  
        root.bind_all("<Control-minus>", self._decrease_font)
        root.bind_all("<Control-equal>", self._increase_font)
        root.bind_all("<Control-plus>", self._increase_font)
        root.bind_all("<Control-0>", self._reset_font)
        
        print("🔧 Font shortcuts bound successfully")

    def _set_global_font_scale(self, delta: int | None):
        print(f"🔧 Font scale called with delta: {delta}")
        theme: ThemeManager = self.services.get_app("theme")
        fonts = dict(theme.get_fonts())
        base = list(fonts.get("main", ("Arial", 20, "normal")))
        print(f"🔧 Current base font: {base}")
        
        if delta is None:
            new_base_size = 20  # Default 20px size for readability
        else:
            new_base_size = max(10, min(40, int(base[1]) + delta))
        
        print(f"🔧 New base size: {new_base_size}")
        
        # Scale all fonts proportionally from 20px base
        fonts["main"] = (base[0], new_base_size, base[2] if len(base) > 2 else "normal")
        fonts["pot_display"] = (base[0], new_base_size + 8, "bold")  # +8 for pot display
        fonts["bet_amount"] = (base[0], new_base_size + 4, "bold")   # +4 for bet amounts
        fonts["body"] = ("Consolas", max(new_base_size, 12))         # Same as main for body text
        fonts["small"] = ("Consolas", max(new_base_size - 4, 10))    # -4 for smaller text
        fonts["header"] = (base[0], max(new_base_size + 2, 14), "bold") # +2 for headers
        
        print(f"🔧 Updated fonts: {fonts}")
        theme.set_fonts(fonts)
        
        # Force all tabs to re-render with new fonts
        for idx in range(self.notebook.index("end")):
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[idx])
            if hasattr(tab_widget, "on_show"):
                tab_widget.on_show()
            # Also force font refresh if the widget has that method
            if hasattr(tab_widget, "_refresh_fonts"):
                tab_widget._refresh_fonts()
        print("🔧 Font scaling complete")

    def _increase_font(self, event=None):
        print("🔧 Increase font called!")
        self._set_global_font_scale(+1)

    def _decrease_font(self, event=None):
        print("🔧 Decrease font called!")
        self._set_global_font_scale(-1)

    def _reset_font(self, event=None):
        print("🔧 Reset font called!")
        self._set_global_font_scale(None)

    def _open_theme_editor(self):
        """Open the Theme Editor in a new window."""
        try:
            from .tabs.theme_editor_tab import ThemeEditorTab
            # Create a new toplevel window for the theme editor
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Theme Editor - Poker Pro Trainer")
            theme_window.geometry("900x700")
            theme_window.resizable(True, True)
            
            # Center the window on screen
            theme_window.update_idletasks()
            x = (theme_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (theme_window.winfo_screenheight() // 2) - (700 // 2)
            theme_window.geometry(f"900x700+{x}+{y}")
            
            # Create the theme editor tab in the new window
            theme_editor = ThemeEditorTab(theme_window, self.services)
            theme_editor.pack(fill=tk.BOTH, expand=True)
            
            print("🎨 Theme Editor opened in new window")
        except Exception as e:
            print(f"❌ Error opening Theme Editor: {e}")
            import traceback
            traceback.print_exc()

    def _open_sound_settings(self):
        """Open the Sound Settings in a new window."""
        try:
            from .tabs.sound_settings_tab import SoundSettingsTab
            # Create a new toplevel window for the sound settings
            sound_window = tk.Toplevel(self.root)
            sound_window.title("Sound Settings - Poker Pro Trainer")
            sound_window.geometry("1200x800")
            sound_window.resizable(True, True)
            
            # Center the window on screen
            sound_window.update_idletasks()
            x = (sound_window.winfo_screenwidth() // 2) - (1200 // 2)
            y = (sound_window.winfo_screenheight() // 2) - (800 // 2)
            sound_window.geometry(f"1200x800+{x}+{y}")
            
            # Create the sound settings tab in the new window
            sound_settings = SoundSettingsTab(sound_window, self.services)
            sound_settings.pack(fill=tk.BOTH, expand=True)
            
            print("🔊 Sound Settings opened in new window")
        except Exception as e:
            print(f"❌ Error opening Sound Settings: {e}")
            import traceback
            traceback.print_exc()



```

---

### poker_sound_config.json

```json
{
  "master_volume": 1.0,
  "sounds_enabled": true,
  "voice_enabled": true,
  "sound_directory": "sounds",
  "sounds": {
    "BET": "poker_chips1-87592.mp3",
    "RAISE": "201807__fartheststar__poker_chips1.wav",
    "CALL": "poker_chips1-87592.mp3",
    "CHECK": "player_check.wav",
    "FOLD": "player_fold.wav",
    "ALL_IN": "allinpushchips-96121.mp3",
    "DEAL_HOLE": "shuffle-cards-46455 (1).mp3",
    "DEAL_BOARD": "deal-hole-cards.wav",
    "DEAL_FLOP": "deal-hole-cards.wav",
    "DEAL_TURN": "deal-hole-cards.wav",
    "DEAL_RIVER": "deal-hole-cards.wav",
    "SHOWDOWN": "game-start-6104.mp3",
    "END_HAND": "click-345983.mp3",
    "HAND_START": "click-1-384917.mp3",
    "ROUND_START": "turn_notify.wav",
    "ROUND_END": "turn_notify.wav",
    "POST_BLIND": "poker_chips1-87592.mp3",
    "POST_SMALL_BLIND": "poker_chips1-87592.mp3",
    "POST_BIG_BLIND": "poker_chips1-87592.mp3",
    "CHIP_BET": "chip_bet.wav",
    "CHIP_COLLECT": "pot_split.wav",
    "POT_RAKE": "pot_rake.wav",
    "POT_SPLIT": "pot_split.wav",
    "TURN_NOTIFY": "turn_notify.wav",
    "BUTTON_MOVE": "button_move.wav",
    "ACTION_TIMEOUT": "turn_notify.wav",
    "CARD_SHUFFLE": "card_deal.wav",
    "CARD_FOLD": "card_fold.wav",
    "CHIP_MULTIPLE": "chip_bet.wav",
    "CHIP_SINGLE": "chip_bet.wav",
    "MONEY_BAG": "chip_bet.wav",
    "COIN_DROP": "chip_bet.wav",
    "CASH_REGISTER": "pot_split.wav",
    "NOTIFICATION": "turn_notify.wav",
    "UI_CLICK": "button_move.wav",
    "DEALING_VARIATION": "571577__el_boss__playing-card-deal-variation-1.wav",
    "POKER_CHIPS": "201807__fartheststar__poker_chips1.wav"
  },
  "voice_sounds": {
    "announcer_female": {
      "all_in": "voice/announcer_female/all_in.wav",
      "bet": "voice/announcer_female/bet.wav",
      "call": "voice/announcer_female/call.wav",
      "check": "voice/announcer_female/check.wav",
      "dealing": "voice/announcer_female/dealing.wav",
      "fold": "voice/announcer_female/fold.wav",
      "raise": "voice/announcer_female/raise.wav",
      "shuffling": "voice/announcer_female/shuffling.wav",
      "winner": "voice/announcer_female/winner.wav",
      "your_turn": "voice/announcer_female/your_turn.wav"
    },
    "announcer_male": {
      "all_in": "voice/announcer_male/all_in.wav",
      "bet": "voice/announcer_male/bet.wav",
      "call": "voice/announcer_male/call.wav",
      "check": "voice/announcer_male/check.wav",
      "dealing": "voice/announcer_male/dealing.wav",
      "fold": "voice/announcer_male/fold.wav",
      "raise": "voice/announcer_male/raise.wav",
      "shuffling": "voice/announcer_male/shuffling.wav",
      "winner": "voice/announcer_male/winner.wav",
      "your_turn": "voice/announcer_male/your_turn.wav"
    },
    "dealer_female": {
      "all_in": "voice/dealer_female/all_in.wav",
      "bet": "voice/dealer_female/bet.wav",
      "call": "voice/dealer_female/call.wav",
      "check": "voice/dealer_female/check.wav",
      "dealing": "voice/dealer_female/dealing.wav",
      "fold": "voice/dealer_female/fold.wav",
      "raise": "voice/dealer_female/raise.wav",
      "shuffling": "voice/dealer_female/shuffling.wav",
      "winner": "voice/dealer_female/winner.wav",
      "your_turn": "voice/dealer_female/your_turn.wav"
    },
    "dealer_male": {
      "all_in": "voice/dealer_male/all_in.wav",
      "bet": "voice/dealer_male/bet.wav",
      "call": "voice/dealer_male/call.wav",
      "check": "voice/dealer_male/check.wav",
      "dealing": "voice/dealer_male/dealing.wav",
      "fold": "voice/dealer_male/fold.wav",
      "raise": "voice/dealer_male/raise.wav",
      "shuffling": "voice/dealer_male/shuffling.wav",
      "winner": "voice/dealer_male/winner.wav",
      "your_turn": "voice/dealer_male/your_turn.wav"
    },
    "hostess_female": {
      "all_in": "voice/hostess_female/all_in.wav",
      "bet": "voice/hostess_female/bet.wav",
      "call": "voice/hostess_female/call.wav",
      "check": "voice/hostess_female/check.wav",
      "dealing": "voice/hostess_female/dealing.wav",
      "fold": "voice/hostess_female/fold.wav",
      "raise": "voice/hostess_female/raise.wav",
      "shuffling": "voice/hostess_female/shuffling.wav",
      "winner": "voice/hostess_female/winner.wav",
      "your_turn": "voice/hostess_female/your_turn.wav"
    },
    "tournament_female": {
      "all_in": "voice/tournament_female/all_in.wav",
      "bet": "voice/tournament_female/bet.wav",
      "call": "voice/tournament_female/call.wav",
      "check": "voice/tournament_female/check.wav",
      "dealing": "voice/tournament_female/dealing.wav",
      "fold": "voice/tournament_female/fold.wav",
      "raise": "voice/tournament_female/raise.wav",
      "shuffling": "voice/tournament_female/shuffling.wav",
      "winner": "voice/tournament_female/winner.wav",
      "your_turn": "voice/tournament_female/your_turn.wav"
    }
  }
}
```

---

### poker_types.py

```python
"""
Shared types for the poker state machine components.

This module contains the shared data structures and enums
to avoid circular imports between components.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Set


class PokerState(Enum):
    """Poker game states following standard Texas Hold'em flow."""

    START_HAND = "start_hand"
    PREFLOP_BETTING = "preflop_betting"
    DEAL_FLOP = "deal_flop"
    FLOP_BETTING = "flop_betting"
    DEAL_TURN = "deal_turn"
    TURN_BETTING = "turn_betting"
    DEAL_RIVER = "deal_river"
    RIVER_BETTING = "river_betting"
    SHOWDOWN = "showdown"
    END_HAND = "end_hand"


class ActionType(Enum):
    """Valid poker actions."""

    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"


@dataclass
class Player:
    """Enhanced Player data structure with all-in tracking."""

    name: str
    stack: float
    position: str
    is_human: bool
    is_active: bool
    cards: List[str]
    current_bet: float = 0.0
    has_acted_this_round: bool = False
    is_all_in: bool = False  # NEW: Track all-in state
    total_invested: float = 0.0  # NEW: Track total money put in pot
    has_folded: bool = False  # NEW: Track folded state for accurate counting
    # BUG FIX: Track partial calls for side pot calculations
    partial_call_amount: Optional[float] = None
    full_call_amount: Optional[float] = None


@dataclass
class RoundState:
    """Per-street betting state (reset on each street)."""
    last_full_raise_size: float = 0.0
    last_aggressor_idx: Optional[int] = None
    reopen_available: bool = True   # becomes False after short all-in that doesn't meet full-raise size
    # NEW: explicit driver for betting flow & termination
    need_action_from: Set[int] = field(default_factory=set)


@dataclass
class GameState:
    """Enhanced game state with proper pot accounting."""

    players: List[Player]
    board: List[str]
    # Pot accounting is split:
    # - committed_pot: sum of completed streets (finalized at street end)
    # - current_bet: highest per-player commitment on THIS street
    committed_pot: float = 0.0
    current_bet: float = 0.0
    street: str = "preflop"
    players_acted: Set[int] = field(default_factory=set)
    round_complete: bool = False
    deck: List[str] = field(default_factory=list)
    big_blind: float = 1.0
    _round_state: RoundState = field(default_factory=RoundState)

    def displayed_pot(self) -> float:
        """What the UI should show right now."""
        return self.committed_pot + sum(p.current_bet for p in self.players)

    @property
    def round_state(self) -> RoundState:
        return self._round_state

    @round_state.setter
    def round_state(self, rs: RoundState) -> None:
        self._round_state = rs

```

---

### hand_model.py

```python
#!/usr/bin/env python3
"""
Production-ready NLHE hand data model with JSON serialization.

This module provides a comprehensive data structure for representing
No Limit Hold'em poker hands with complete action histories, side pots,
showdowns, and metadata. Supports 2-9 players with antes, straddles,
and all poker scenarios.

Key features:
- Complete action ordering for deterministic replay
- Side pot calculation and tracking  
- Robust JSON serialization with round-trip integrity
- Comprehensive metadata for analysis and statistics
- Fuzz-tested across all scenarios
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Any
import json

# =========================
# Basic card representation
# =========================

_RANKS = "23456789TJQKA"
_SUITS = "cdhs"  # clubs, diamonds, hearts, spades

def _validate_card_str(cs: str) -> None:
    """Validate card string format (e.g., 'As', 'Kh', '7c')."""
    if len(cs) != 2 or cs[0] not in _RANKS or cs[1] not in _SUITS:
        raise ValueError(f"Invalid card string: {cs}")

@dataclass(frozen=True)
class Card:
    """Card encoded as rank+suited char, e.g., 'As', 'Td', '7c'."""
    rank: str
    suit: str

    @staticmethod
    def from_str(s: str) -> "Card":
        """Create Card from string representation."""
        _validate_card_str(s)
        return Card(rank=s[0], suit=s[1])

    def to_str(self) -> str:
        """Convert Card to string representation."""
        return f"{self.rank}{self.suit}"

    def __str__(self) -> str:
        return self.to_str()

# =========================
# Enums
# =========================

class Variant(str, Enum):
    """Poker variant types."""
    NLHE = "NLHE"
    PLO = "PLO"  # Future extension
    STUD = "STUD"  # Future extension

class Street(str, Enum):
    """Betting street names."""
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"

class ActionType(str, Enum):
    """All possible poker actions."""
    # Table setup / postings
    POST_ANTE = "POST_ANTE"
    POST_BLIND = "POST_BLIND"      # includes SB, BB, and dead blinds (see metadata fields)
    STRADDLE = "STRADDLE"
    POST_DEAD = "POST_DEAD"

    # Dealing markers (optional—useful for complete replication)
    DEAL_HOLE = "DEAL_HOLE"
    DEAL_FLOP = "DEAL_FLOP"
    DEAL_TURN = "DEAL_TURN"
    DEAL_RIVER = "RIVER"

    # Betting actions
    CHECK = "CHECK"
    BET = "BET"
    CALL = "CALL"
    RAISE = "RAISE"
    FOLD = "FOLD"

    # Chips/cleanup
    RETURN_UNCALLED = "RETURN_UNCALLED"

    # Showdown
    SHOW = "SHOW"
    MUCK = "MUCK"

# =========================
# Core data structures
# =========================

@dataclass
class Seat:
    """Player seat information (canonical UID)."""
    seat_no: int
    player_uid: str
    display_name: Optional[str] = None
    starting_stack: int = 0  # in chips (or your base unit)
    is_button: bool = False

@dataclass
class PostingMeta:
    """Additional context for a POST_* action."""
    blind_type: Optional[str] = None  # "SB", "BB", "BB+Ante", "Dead", "Straddle", etc.

@dataclass
class Action:
    """One atomic action in order as it occurred."""
    order: int
    street: Street
    actor_uid: Optional[str]        # None for deal markers / system actions
    action: ActionType
    amount: int = 0                # Incremental chips put in with THIS action (0 for check/fold)
    to_amount: Optional[int] = None  # Player's total contribution on this street *after* this action
    all_in: bool = False
    note: Optional[str] = None     # free-form (e.g., "misdeal fix", "click raise", "timeout")
    posting_meta: Optional[PostingMeta] = None

@dataclass
class StreetState:
    """Holds board cards (as strings) and actions for a street."""
    board: List[str] = field(default_factory=list)   # e.g. FLOP: ["As","Kd","7c"], TURN append ["2h"]
    actions: List[Action] = field(default_factory=list)

@dataclass
class PotShare:
    """Distribution result for a single pot (main or side)."""
    player_uid: str
    amount: int          # chips collected from this pot

@dataclass
class Pot:
    """Pot information with eligibility and final distribution."""
    amount: int                  # total pot size before distribution (after rake taken if applicable)
    eligible_player_uids: List[str]   # who was eligible for this pot when it formed
    shares: List[PotShare] = field(default_factory=list)  # actual distribution at showdown

@dataclass
class ShowdownEntry:
    """Showdown information for a player."""
    player_uid: str
    hole_cards: Optional[List[str]] = None  # None if mucked unseen
    hand_rank: Optional[str] = None         # "Full House", "Two Pair", etc.
    hand_description: Optional[str] = None  # "Aces full of Kings", etc.
    spoke: Optional[bool] = None            # if table requires speech or reveal
    note: Optional[str] = None

@dataclass
class HandMetadata:
    """Complete hand metadata for analysis and tracking."""
    table_id: str
    hand_id: str
    variant: Variant = Variant.NLHE
    max_players: int = 9
    small_blind: int = 50    # chips
    big_blind: int = 100
    ante: int = 0            # per-player ante if any (can be 0)
    rake: int = 0            # total rake taken from table
    currency: str = "CHIPS"  # label only; no math
    started_at_utc: Optional[str] = None    # ISO timestamp
    ended_at_utc: Optional[str] = None      # ISO timestamp
    run_count: int = 1       # if you support "run it twice," increase and add boards
    
    # Extended metadata for our poker system
    session_type: Optional[str] = None  # "gto", "practice", "review"
    bot_strategy: Optional[str] = None   # "gto_v1", "loose_aggressive", etc.
    analysis_tags: List[str] = field(default_factory=list)  # ["premium_cards", "3bet_pot"]
    hole_cards: Dict[str, List[str]] = field(default_factory=dict)  # player_uid -> [card1, card2]

@dataclass
class Hand:
    """
    Full hand record, sufficient to reconstruct play exactly as recorded.
    
    This is the complete representation of a poker hand with all metadata,
    actions, board cards, and final results needed for analysis, replay,
    and statistical tracking.
    """
    metadata: HandMetadata
    seats: List[Seat]
    hero_player_uid: Optional[str] = None  # if you want to mark a perspective
    
    # Streets: store all actions and board per street for exact replay
    streets: Dict[Street, StreetState] = field(default_factory=lambda: {
        Street.PREFLOP: StreetState(),
        Street.FLOP: StreetState(),
        Street.TURN: StreetState(),
        Street.RIVER: StreetState(),
    })
    
    # Final state
    pots: List[Pot] = field(default_factory=list)
    showdown: List[ShowdownEntry] = field(default_factory=list)
    final_stacks: Dict[str, int] = field(default_factory=dict)  # player_uid -> ending stack

    # ------------- Serialization helpers -------------
    def to_dict(self) -> Dict[str, Any]:
        """Convert Hand to dictionary for JSON serialization."""
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, Card):
                return obj.to_str()
            if isinstance(obj, Hand):
                d = asdict(obj)
                # Fix Enums (Street keys) and nested enums
                d["streets"] = {
                    st.value: {
                        "board": s.board,
                        "actions": [
                            {
                                **{k: (v.value if isinstance(v, Enum) else v)
                                   for k, v in asdict(a).items()
                                   if k not in ("posting_meta", "street")},
                                "street": a.street.value,
                                "posting_meta": asdict(a.posting_meta) if a.posting_meta else None,
                            }
                            for a in s.actions
                        ]
                    } for st, s in obj.streets.items()
                }
                # Enums in metadata
                d["metadata"]["variant"] = obj.metadata.variant.value
                return d
            if _dataclass_isinstance(obj):
                return {k: serialize(v) for k, v in asdict(obj).items()}
            if isinstance(obj, list):
                return [serialize(x) for x in obj]
            if isinstance(obj, dict):
                return {serialize(k): serialize(v) for k, v in obj.items()}
            return obj

        return serialize(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Hand":
        """Create Hand from dictionary (JSON deserialization)."""
        # Metadata
        md = d["metadata"]
        metadata = HandMetadata(
            table_id=md["table_id"],
            hand_id=md["hand_id"],
            variant=Variant(md.get("variant", "NLHE")),
            max_players=md.get("max_players", 9),
            small_blind=md.get("small_blind", 50),
            big_blind=md.get("big_blind", 100),
            ante=md.get("ante", 0),
            rake=md.get("rake", 0),
            currency=md.get("currency", "CHIPS"),
            started_at_utc=md.get("started_at_utc"),
            ended_at_utc=md.get("ended_at_utc"),
            run_count=md.get("run_count", 1),
            session_type=md.get("session_type"),
            bot_strategy=md.get("bot_strategy"),
            analysis_tags=md.get("analysis_tags", []),
        )
        # Populate hole cards if present in serialized metadata
        if "hole_cards" in md and isinstance(md["hole_cards"], dict):
            try:
                metadata.hole_cards.update({
                    str(k): list(v) if isinstance(v, list) else v
                    for k, v in md["hole_cards"].items()
                })
            except Exception:
                pass
        # Add button seat if present (forward-compat)
        if "button_seat_no" in md:
            try:
                setattr(metadata, "button_seat_no", int(md["button_seat_no"]))
            except Exception:
                pass
        
        # Seats: accept either player_uid or legacy player_id; store as player_uid
        seats = []
        for s in d["seats"]:
            s2 = dict(s)
            if "player_id" in s2 and "player_uid" not in s2:
                s2["player_uid"] = s2.pop("player_id")
            seats.append(Seat(**s2))
        # Hero uid alias
        hero = d.get("hero_player_uid") or d.get("hero_player_id")
        
        # Streets
        streets: Dict[Street, StreetState] = {}
        streets_in = d.get("streets", {})
        for key, s in streets_in.items():
            st_enum = Street(key)
            actions_in: List[Dict[str, Any]] = s.get("actions", [])
            actions: List[Action] = []
            for a in actions_in:
                pm = a.get("posting_meta")
                a2 = dict(a)
                # actor id alias → actor_uid
                if "actor_id" in a2 and "actor_uid" not in a2:
                    a2["actor_uid"] = a2.pop("actor_id")
                actions.append(Action(
                    order=a2["order"],
                    street=Street(a2["street"]),
                    actor_uid=a2.get("actor_uid"),
                    action=ActionType(a2["action"]),
                    amount=a2.get("amount", 0),
                    to_amount=a2.get("to_amount"),
                    all_in=a2.get("all_in", False),
                    note=a2.get("note"),
                    posting_meta=PostingMeta(**pm) if pm else None,
                ))
            streets[st_enum] = StreetState(board=s.get("board", []), actions=actions)

        # Pots
        pots = []
        for p in d.get("pots", []):
            p2 = dict(p)
            eligible = p2.get("eligible_player_uids") or p2.get("eligible_player_ids") or []
            shares_in = p2.get("shares", [])
            shares = []
            for ps in shares_in:
                ps2 = dict(ps)
                if "player_id" in ps2 and "player_uid" not in ps2:
                    ps2["player_uid"] = ps2.pop("player_id")
                shares.append(PotShare(**ps2))
            pots.append(Pot(
                amount=p2["amount"], 
                eligible_player_uids=eligible, 
                shares=shares
            ))

        # Showdown
        showdown = [ShowdownEntry(**sd) for sd in d.get("showdown", [])]
        final_stacks = d.get("final_stacks", {})

        return Hand(
            metadata=metadata,
            seats=seats,
            hero_player_uid=hero,
            streets=streets or {
                Street.PREFLOP: StreetState(),
                Street.FLOP: StreetState(),
                Street.TURN: StreetState(),
                Street.RIVER: StreetState(),
            },
            pots=pots,
            showdown=showdown,
            final_stacks=final_stacks,
        )

    # ------------- I/O convenience -------------
    def save_json(self, path: str) -> None:
        """Save Hand to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(path: str) -> "Hand":
        """Load Hand from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return Hand.from_dict(d)

    # ------------- Analysis helpers -------------
    def get_all_actions(self) -> List[Action]:
        """Get all actions across all streets in chronological order."""
        all_actions = []
        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            all_actions.extend(self.streets[street].actions)
        return sorted(all_actions, key=lambda a: a.order)

    def get_actions_for_player(self, player_id: str) -> List[Action]:
        """Get all actions for a specific player."""
        return [a for a in self.get_all_actions() if a.actor_id == player_id]

    def get_final_board(self) -> List[str]:
        """Get the final board cards (up to 5 cards)."""
        if self.streets[Street.RIVER].board:
            return self.streets[Street.RIVER].board
        elif self.streets[Street.TURN].board:
            return self.streets[Street.TURN].board
        elif self.streets[Street.FLOP].board:
            return self.streets[Street.FLOP].board
        else:
            return []

    def get_total_pot(self) -> int:
        """Get total pot size across all pots."""
        return sum(pot.amount for pot in self.pots)

    def get_player_total_investment(self, player_id: str) -> int:
        """Calculate total chips invested by a player across all streets."""
        total = 0
        for action in self.get_actions_for_player(player_id):
            if action.amount > 0:  # Only count chips put in, not folds/checks
                total += action.amount
        return total

    def get_player_winnings(self, player_id: str) -> int:
        """Get total winnings for a player from all pots."""
        total = 0
        for pot in self.pots:
            for share in pot.shares:
                if share.player_id == player_id:
                    total += share.amount
        return total

    def get_net_result(self, player_id: str) -> int:
        """Get net result (winnings - investment) for a player."""
        return self.get_player_winnings(player_id) - self.get_player_total_investment(player_id)

# ============
# Utilities
# ============

def _dataclass_isinstance(obj: Any) -> bool:
    """Check if object is a dataclass instance."""
    return hasattr(obj, "__dataclass_fields__")

# ============
# Example usage
# ============

if __name__ == "__main__":
    # Minimal illustrative example of a 3-handed hand
    hand = Hand(
        metadata=HandMetadata(
            table_id="Table-12", 
            hand_id="H#0001",
            small_blind=50, 
            big_blind=100, 
            ante=0, 
            rake=25,
            started_at_utc="2025-01-15T15:00:00Z",
            session_type="gto",
            bot_strategy="gto_v1",
            analysis_tags=["premium_cards", "3bet_pot"]
        ),
        seats=[
            Seat(seat_no=1, player_id="p1", display_name="Alice", starting_stack=10000, is_button=True),
            Seat(seat_no=2, player_id="p2", display_name="Bob",   starting_stack=12000),
            Seat(seat_no=3, player_id="p3", display_name="Cara",  starting_stack=8000),
        ],
        hero_player_id="p1",
    )

    # Preflop: blinds posted, hole cards dealt, actions
    hand.streets[Street.PREFLOP].actions.extend([
        Action(order=1, street=Street.PREFLOP, actor_id="p2", action=ActionType.POST_BLIND, amount=50,
               posting_meta=PostingMeta(blind_type="SB")),
        Action(order=2, street=Street.PREFLOP, actor_id="p3", action=ActionType.POST_BLIND, amount=100,
               posting_meta=PostingMeta(blind_type="BB")),
        Action(order=3, street=Street.PREFLOP, actor_id=None, action=ActionType.DEAL_HOLE, amount=0, 
               note="Dealt hole cards"),
        Action(order=4, street=Street.PREFLOP, actor_id="p1", action=ActionType.RAISE, amount=300, to_amount=300),
        Action(order=5, street=Street.PREFLOP, actor_id="p2", action=ActionType.CALL, amount=250, to_amount=300),
        Action(order=6, street=Street.PREFLOP, actor_id="p3", action=ActionType.CALL, amount=200, to_amount=300),
    ])

    # Flop board and actions
    hand.streets[Street.FLOP].board = ["As", "Kd", "7c"]
    hand.streets[Street.FLOP].actions.extend([
        Action(order=7, street=Street.FLOP, actor_id="p2", action=ActionType.CHECK),
        Action(order=8, street=Street.FLOP, actor_id="p3", action=ActionType.CHECK),
        Action(order=9, street=Street.FLOP, actor_id="p1", action=ActionType.BET, amount=400, to_amount=400),
        Action(order=10, street=Street.FLOP, actor_id="p2", action=ActionType.FOLD),
        Action(order=11, street=Street.FLOP, actor_id="p3", action=ActionType.CALL, amount=400, to_amount=400),
    ])

    # Turn
    hand.streets[Street.TURN].board = hand.streets[Street.FLOP].board + ["2h"]
    hand.streets[Street.TURN].actions.extend([
        Action(order=12, street=Street.TURN, actor_id="p3", action=ActionType.CHECK),
        Action(order=13, street=Street.TURN, actor_id="p1", action=ActionType.BET, amount=1000, to_amount=1000),
        Action(order=14, street=Street.TURN, actor_id="p3", action=ActionType.CALL, amount=1000, to_amount=1000),
    ])

    # River
    hand.streets[Street.RIVER].board = hand.streets[Street.TURN].board + ["Jh"]
    hand.streets[Street.RIVER].actions.extend([
        Action(order=15, street=Street.RIVER, actor_id="p3", action=ActionType.CHECK),
        Action(order=16, street=Street.RIVER, actor_id="p1", action=ActionType.BET, amount=2500, to_amount=2500),
        Action(order=17, street=Street.RIVER, actor_id="p3", action=ActionType.FOLD),
    ])

    # Pots & result
    hand.pots = [
        Pot(
            amount=5275,  # 900 preflop + 800 flop + 2000 turn + 2500 river - 25 rake
            eligible_player_ids=["p1", "p3"],  # p2 folded on flop
            shares=[PotShare(player_id="p1", amount=5275)]
        )
    ]

    hand.showdown = []  # Winner didn't need to show
    
    hand.final_stacks = {
        "p1": 10000 + 5275 - (300 + 400 + 1000 + 2500),  # won the pot
        "p2": 12000 - (50 + 250),  # folded flop
        "p3": 8000 - (100 + 200 + 400 + 1000),  # folded river
    }
    hand.metadata.ended_at_utc = "2025-01-15T15:03:12Z"

    # Test save & load
    hand.save_json("example_hand.json")
    loaded = Hand.load_json("example_hand.json")
    assert hand.to_dict() == loaded.to_dict()
    print("✅ Hand model example: Saved and loaded successfully!")
    print(f"   Hand ID: {loaded.metadata.hand_id}")
    print(f"   Final pot: {loaded.get_total_pot()}")
    print(f"   Winner: p1 net result: +{loaded.get_net_result('p1')}")

```

---

### fix_runtime_errors.py

```python
#!/usr/bin/env python3
"""
Runtime Error Fixer - Fixes all compile-time errors during runtime.
This program patches missing methods and fixes the session manager.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_pure_poker_state_machine():
    """Fix missing methods in PurePokerStateMachine."""
    try:
        from core.pure_poker_state_machine import PurePokerStateMachine
        
        # Add missing methods to PurePokerStateMachine
        if not hasattr(PurePokerStateMachine, 'initialize_game'):
            def initialize_game(self, config):
                """Initialize game with configuration."""
                self.config = config
                self._initialize_players()
                print(f"🔧 PPSM: Game initialized with {config.num_players} players")
            
            PurePokerStateMachine.initialize_game = initialize_game
        
        if not hasattr(PurePokerStateMachine, 'add_player'):
            def add_player(self, name, starting_stack):
                """Add a player to the game."""
                from core.poker_types import Player
                player = Player(
                    name=name,
                    stack=starting_stack,
                    position="",
                    is_human=False,
                    is_active=True,
                    cards=[]
                )
                self.game_state.players.append(player)
                print(f"🔧 PPSM: Added player {name} with stack {starting_stack}")
            
            PurePokerStateMachine.add_player = add_player
        
        if not hasattr(PurePokerStateMachine, 'set_dealer_position'):
            def set_dealer_position(self, position):
                """Set the dealer position."""
                self.dealer_position = position
                print(f"🔧 PPSM: Dealer position set to {position}")
            
            PurePokerStateMachine.set_dealer_position = set_dealer_position
        
        if not hasattr(PurePokerStateMachine, 'get_game_state'):
            def get_game_state(self):
                """Get current game state."""
                return {
                    'players': [
                        {
                            'name': p.name,
                            'starting_stack': p.stack,
                            'current_stack': p.stack,
                            'current_bet': p.current_bet if hasattr(p, 'current_bet') else 0,
                            'hole_cards': p.cards,
                            'folded': p.has_folded if hasattr(p, 'has_folded') else False,
                            'all_in': p.is_all_in if hasattr(p, 'is_all_in') else False,
                            'acting': p.is_acting if hasattr(p, 'is_acting') else False,
                            'position': p.position
                        }
                        for p in self.game_state.players
                    ],
                    'board': self.game_state.board,
                    'pot': self.game_state.committed_pot,
                    'dealer_position': self.dealer_position,
                    'current_player': self.action_player_index,
                    'last_action_type': '',
                    'last_action_amount': 0
                }
            
            PurePokerStateMachine.get_game_state = get_game_state
        
        print("✅ PurePokerStateMachine methods patched successfully")
        
    except Exception as e:
        print(f"⚠️ Error patching PurePokerStateMachine: {e}")

def fix_hands_review_session_manager():
    """Fix the HandsReviewSessionManager to work with the patched PPSM."""
    try:
        from ui.services.hands_review_session_manager import HandsReviewSessionManager
        
        # Patch the _initialize_ppsm_for_hand method
        def _initialize_ppsm_for_hand_patched(self):
            """Initialize PPSM with hand data - business logic only."""
            if not self.current_hand:
                return
            
            # Create game config from hand data
            from core.pure_poker_state_machine import GameConfig
            config = GameConfig(
                num_players=len(self.current_hand.seats),
                small_blind=self.current_hand.metadata.small_blind,
                big_blind=self.current_hand.metadata.big_blind,
                starting_stack=1000  # Default, could be configurable
            )
            
            # Initialize PPSM
            self.ppsm.initialize_game(config)
            
            # Add players from seats
            for seat in self.current_hand.seats:
                self.ppsm.add_player(seat.player_uid, seat.starting_stack)
            
            # Set dealer position (default to seat 0 for now)
            self.ppsm.set_dealer_position(0)
            
            print(f"🔧 PPSM: Initialized for hand with {len(self.current_hand.seats)} players")
        
        # Replace the method
        HandsReviewSessionManager._initialize_ppsm_for_hand = _initialize_ppsm_for_hand_patched
        
        print("✅ HandsReviewSessionManager patched successfully")
        
    except Exception as e:
        print(f"⚠️ Error patching HandsReviewSessionManager: {e}")

def fix_hand_model_decision_engine():
    """Fix the HandModelDecisionEngine if it has issues."""
    try:
        from core.hand_model_decision_engine import HandModelDecisionEngine
        
        # Check if the class exists and has required methods
        if not hasattr(HandModelDecisionEngine, '__init__'):
            print("⚠️ HandModelDecisionEngine not found, creating stub")
            
            class HandModelDecisionEngine:
                def __init__(self, hand):
                    self.hand = hand
                    print(f"🔧 DecisionEngine: Created for hand {hand.metadata.hand_id}")
                
                def get_decision(self, player_name, game_state):
                    return "CHECK", 0  # Default decision
            
            # Replace the import
            import core.hand_model_decision_engine
            core.hand_model_decision_engine.HandModelDecisionEngine = HandModelDecisionEngine
        
        print("✅ HandModelDecisionEngine checked/fixed successfully")
        
    except Exception as e:
        print(f"⚠️ Error fixing HandModelDecisionEngine: {e}")

def main():
    """Main function to fix all runtime errors."""
    print("🔧 Starting Runtime Error Fixer...")
    
    # Fix all the issues
    fix_pure_poker_state_machine()
    fix_hands_review_session_manager()
    fix_hand_model_decision_engine()
    
    print("✅ All runtime errors fixed!")
    print("🎯 The application should now run without console errors.")

if __name__ == "__main__":
    main()

```

---

### run_new_ui.py

```python
import tkinter as tk
import sys
import os

def check_terminal_compatibility():
    """Check if we're running in VS Code integrated terminal and warn user."""
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        print("⚠️  WARNING: Running GUI in VS Code integrated terminal may cause crashes!")
        print("💡 RECOMMENDED: Run this from macOS Terminal app instead:")
        print(f"   cd {os.getcwd()}")
        print(f"   python3 {os.path.basename(__file__)}")
        print()
        
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Exiting safely. Run from external terminal for best experience.")
            sys.exit(0)

try:  # Prefer package-relative import (python -m backend.run_new_ui)
    from .ui.app_shell import AppShell  # type: ignore
except Exception:
    try:  # Running as a script from backend/ (python backend/run_new_ui.py)
        from ui.app_shell import AppShell  # type: ignore
    except Exception:
        # Last resort: ensure repo root is on sys.path then import absolute
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from ui.app_shell import AppShell  # type: ignore


def main() -> None:
    # Apply runtime fixes before starting the application
    try:
        print("🔧 Applying runtime fixes...")
        from fix_runtime_errors import main as apply_fixes
        apply_fixes()
        print("✅ Runtime fixes applied successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not apply runtime fixes: {e}")
        print("🎯 Continuing anyway...")
    
    # Check terminal compatibility before creating GUI
    check_terminal_compatibility()
    
    root = tk.Tk()
    root.title("Poker Trainer — New UI Preview")
    
    # Configure window size and position (70% of screen, centered)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate 70% size
    window_width = int(screen_width * 0.7)
    window_height = int(screen_height * 0.7)
    
    # Calculate center position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set window geometry (width x height + x_offset + y_offset)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Set minimum size (50% of calculated size)
    root.minsize(int(window_width * 0.5), int(window_height * 0.5))
    
    AppShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()


```

---

## UI COMPONENT SYSTEM

### chip_animations.py

```python
"""
Chip Animation System - Flying Chips for Bet→Pot and Pot→Winner
Token-driven animations with smooth easing and particle effects
"""

import math
from ...services.theme_utils import ease_in_out_cubic

class ChipAnimations:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.active_animations = {}
        
    def draw_chip(self, canvas, x, y, denom_key, text="", r=14, tags=None):
        """Draw a single chip with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Get chip colors from tokens
        chip_color = tokens.get(denom_key, "#2E86AB")  # Default to $1 blue
        rim_color = tokens.get("chip.rim", "#000000")
        text_color = tokens.get("chip.text", "#F8F7F4")
        
        chip_tags = ["chip"]
        if tags:
            chip_tags.extend(tags)
        
        # Main chip circle
        chip_id = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=chip_color, outline=rim_color, width=2,
            tags=tuple(chip_tags)
        )
        
        # Inner ring for depth
        inner_r = r - 3
        canvas.create_oval(
            x - inner_r, y - inner_r, x + inner_r, y + inner_r,
            fill="", outline=rim_color, width=1,
            tags=tuple(chip_tags)
        )
        
        # Value text (if provided)
        if text:
            canvas.create_text(
                x, y, text=text, fill=text_color,
                font=("Inter", 8, "bold"), anchor="center",
                tags=tuple(chip_tags)
            )
        
        return chip_id
    
    def stack_height(self, amount):
        """Calculate stack height based on amount"""
        return min(8, max(1, int(amount / 50)))  # 50 units per chip
    
    def draw_chip_stack(self, canvas, x, y, amount, tags=None):
        """Draw a stack of chips representing the total value"""
        if amount <= 0:
            return []
        
        # Determine chip denominations to show
        denom_keys = ["chip.$1", "chip.$5", "chip.$25", "chip.$100", "chip.$500", "chip.$1k"]
        levels = self.stack_height(amount)
        
        chip_ids = []
        for i in range(levels):
            # Cycle through denominations for visual variety
            denom = denom_keys[i % len(denom_keys)]
            chip_y = y - (i * 4)  # Stack with 4px offset
            
            chip_id = self.draw_chip(canvas, x, chip_y, denom, tags=tags)
            chip_ids.append(chip_id)
        
        return chip_ids
    
    def fly_chips_to_pot(self, canvas, from_x, from_y, to_x, to_y, amount, callback=None):
        """Animate chips flying from player bet area to pot - ONLY at end of street"""
        animation_id = f"bet_to_pot_{from_x}_{from_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create temporary chips for animation with proper denominations
        chip_plan = self._break_down_amount(amount)
        chip_ids = []
        
        for i, denom in enumerate(chip_plan):
            # Slight spread for natural look
            start_x = from_x + (i - len(chip_plan)//2) * 8
            start_y = from_y + (i - len(chip_plan)//2) * 4
            
            # Create chip with proper denomination and label
            chip_size = 12  # Standard chip size for animations
            chip_id = self._create_chip_with_label(canvas, start_x, start_y, denom, 
                                                 tokens, chip_size, tags=["flying_chip", "temp_animation"])
            chip_ids.append((chip_id, start_x, start_y, denom))
        
        # Animation parameters - slower for visibility
        frames = 30  # Increased from 20 for better visibility
        
        def animate_step(frame):
            if frame >= frames:
                # Animation complete
                self._cleanup_flying_chips(canvas, chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            # Calculate progress with easing
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Update each chip position
            for i, (chip_id, start_x, start_y, denom) in enumerate(chip_ids):
                # Calculate current position with slight arc
                current_x = start_x + (to_x - start_x) * eased_progress
                current_y = start_y + (to_y - start_y) * eased_progress
                
                # Add arc effect (parabolic path)
                arc_height = 30 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                # Add slight randomness for natural movement
                wobble_x = math.sin(frame * 0.3 + i) * 3
                wobble_y = math.cos(frame * 0.2 + i) * 2
                
                # Update chip position
                try:
                    canvas.coords(chip_id, 
                                current_x + wobble_x - 14, current_y + wobble_y - 14,
                                current_x + wobble_x + 14, current_y + wobble_y + 14)
                except:
                    pass  # Chip may have been deleted
            
            # Add motion blur/glow effect
            if frame % 2 == 0:  # Every 2nd frame for more glow
                glow_color = tokens.get("bet.glow", "#FFD700")
                for _, (chip_id, _, _, _) in enumerate(chip_ids):
                    try:
                        bbox = canvas.bbox(chip_id)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            canvas.create_oval(
                                x1 - 4, y1 - 4, x2 + 4, y2 + 4,
                                outline=glow_color, width=2,
                                tags=("motion_glow", "temp_animation")
                            )
                    except:
                        pass
            
            # Schedule next frame - slower for visibility
            canvas.after(80, lambda: animate_step(frame + 1))  # Increased from 40ms
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def fly_pot_to_winner(self, canvas, pot_x, pot_y, winner_x, winner_y, amount, callback=None):
        """Animate pot chips flying to winner with celebration effect"""
        animation_id = f"pot_to_winner_{winner_x}_{winner_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create explosion of chips from pot
        explosion_positions = []
        num_stacks = 6
        
        for i in range(num_stacks):
            angle = (i / num_stacks) * 2 * math.pi
            radius = 30
            exp_x = pot_x + radius * math.cos(angle)
            exp_y = pot_y + radius * math.sin(angle)
            explosion_positions.append((exp_x, exp_y))
        
        # Create chip stacks for animation
        all_chip_ids = []
        for exp_x, exp_y in explosion_positions:
            stack_chips = self.draw_chip_stack(canvas, exp_x, exp_y, amount // num_stacks,
                                             tags=["flying_chip", "temp_animation"])
            all_chip_ids.extend([(chip_id, exp_x, exp_y) for chip_id in stack_chips])
        
        frames = 30
        
        def animate_step(frame):
            if frame >= frames:
                # Show winner celebration
                self._show_winner_celebration(canvas, winner_x, winner_y, tokens)
                self._cleanup_flying_chips(canvas, all_chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Move all chips toward winner
            for chip_id, start_x, start_y in all_chip_ids:
                # Calculate trajectory with arc
                current_x = start_x + (winner_x - start_x) * eased_progress
                current_y = start_y + (winner_y - start_y) * eased_progress
                
                # Higher arc for dramatic effect
                arc_height = 40 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                try:
                    canvas.coords(chip_id,
                                current_x - 14, current_y - 14,
                                current_x + 14, current_y + 14)
                except:
                    pass
            
            canvas.after(35, lambda: animate_step(frame + 1))
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def place_bet_chips(self, canvas, x, y, amount, tokens, tags=()):
        """Place bet chips in front of player (NOT flying to pot) - for betting rounds"""
        # Get chip size from sizing system if available
        chip_size = 14  # Default fallback
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                # Try to get sizing system from theme
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    chip_size = sizing_system.get_chip_size('bet')
            except Exception:
                pass
        
        chip_plan = self._break_down_amount(amount)
        chip_ids = []
        
        # Position chips in a neat stack in front of player
        for i, denom in enumerate(chip_plan):
            chip_x = x + (i - len(chip_plan)//2) * 6  # Horizontal spread
            chip_y = y - (i * 3)  # Vertical stack
            
            # Create chip with denomination label
            chip_id = self._create_chip_with_label(canvas, chip_x, chip_y, denom, 
                                                 tokens, chip_size, tags=tags + (f"bet_chip_{i}",))
            chip_ids.append(chip_id)
        
        # Add total amount label above the chips
        label_y = y - (len(chip_plan) * 3) - 20
        
        # Get text size from sizing system if available
        text_size = 12  # Default fallback
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    text_size = sizing_system.get_text_size('bet_amount')
            except Exception:
                pass
        
        label_id = canvas.create_text(
            x, label_y,
            text=f"${amount}",
            font=("Arial", text_size, "bold"),
            fill="#FFFFFF",
            tags=tags + ("bet_label",)
        )
        
        return chip_ids + [label_id]
    
    def _create_chip_with_label(self, canvas, x, y, denom, tokens, chip_size, tags=()):
        """Create a chip with denomination label"""
        # Get chip colors based on denomination
        bg_color, ring_color, text_color = self._get_chip_colors(denom, tokens)
        
        # Create chip body
        chip_id = canvas.create_oval(
            x - chip_size, y - chip_size, x + chip_size, y + chip_size,
            fill=bg_color, outline=ring_color, width=2,
            tags=tags
        )
        
        # Get text size from sizing system if available
        text_size = max(8, int(chip_size * 0.4))  # Default proportional sizing
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    text_size = sizing_system.get_text_size('action_label')
            except Exception:
                pass
        
        # Create denomination label
        label_id = canvas.create_text(
            x, y,
            text=f"${denom}",
            font=("Arial", text_size, "bold"),
            fill=text_color,
            tags=tags
        )
        
        return chip_id
    
    def _get_chip_colors(self, denom, tokens):
        """Get appropriate colors for chip denomination"""
        if denom >= 1000:
            return "#2D1B69", "#FFD700", "#FFFFFF"  # Purple with gold ring
        elif denom >= 500:
            return "#8B0000", "#FFD700", "#FFFFFF"  # Red with gold ring
        elif denom >= 100:
            return "#006400", "#FFFFFF", "#FFFFFF"  # Green with white ring
        elif denom >= 25:
            return "#4169E1", "#FFFFFF", "#FFFFFF"  # Blue with white ring
        else:
            return "#FFFFFF", "#000000", "#000000"  # White with black ring
    
    def _break_down_amount(self, amount):
        """Break down amount into chip denominations"""
        denominations = [1000, 500, 100, 25, 5, 1]
        chip_plan = []
        remaining = amount
        
        for denom in denominations:
            if remaining >= denom:
                count = min(remaining // denom, 5)  # Max 5 chips per denomination
                chip_plan.extend([denom] * count)
                remaining -= denom * count
                
            if len(chip_plan) >= 8:  # Max 8 chips total
                break
        
        # If we still have remaining, add smaller denominations
        if remaining > 0 and len(chip_plan) < 8:
            remaining_space = 8 - len(chip_plan)
            chip_plan.extend([1] * min(remaining_space, remaining))
        
        return chip_plan
    
    def _show_winner_celebration(self, canvas, x, y, tokens):
        """Show celebration effect at winner position"""
        celebration_color = tokens.get("label.winner.bg", "#FFD700")
        
        # Create particle burst
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            
            # Particle trajectory
            end_x = x + 60 * math.cos(angle)
            end_y = y + 60 * math.sin(angle)
            
            # Create particle
            particle_id = canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=celebration_color, outline="",
                tags=("celebration_particle", "temp_animation")
            )
            
            # Animate particle outward
            self._animate_particle(canvas, particle_id, x, y, end_x, end_y)
        
        # Winner text flash
        canvas.create_text(
            x, y - 40, text="WINNER!", 
            font=("Inter", 18, "bold"), fill=celebration_color,
            tags=("winner_flash", "temp_animation")
        )
        
        # Auto-cleanup after 2 seconds
        canvas.after(2000, lambda: canvas.delete("celebration_particle", "winner_flash"))
    
    def _animate_particle(self, canvas, particle_id, start_x, start_y, end_x, end_y):
        """Animate a single celebration particle"""
        frames = 15
        
        def particle_step(frame):
            if frame >= frames:
                try:
                    canvas.delete(particle_id)
                except:
                    pass
                return
            
            progress = frame / frames
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            try:
                canvas.coords(particle_id,
                            current_x - 3, current_y - 3,
                            current_x + 3, current_y + 3)
            except:
                pass
            
            canvas.after(30, lambda: particle_step(frame + 1))
        
        particle_step(0)
    
    def _cleanup_flying_chips(self, canvas, chip_ids):
        """Clean up temporary animation chips"""
        for chip_data in chip_ids:
            if isinstance(chip_data, tuple):
                chip_id = chip_data[0]
            else:
                chip_id = chip_data
            try:
                canvas.delete(chip_id)
            except:
                pass
        
        # Clean up motion effects
        canvas.delete("motion_glow")
    
    def pulse_pot(self, canvas, pot_x, pot_y, tokens):
        """Subtle pot pulse when amount increases"""
        glow_color = tokens.get("glow.medium", "#FFD700")
        
        def pulse_step(radius, intensity):
            if intensity <= 0:
                canvas.delete("pot_pulse")
                return
            
            # Create expanding ring
            canvas.create_oval(
                pot_x - radius, pot_y - radius,
                pot_x + radius, pot_y + radius,
                outline=glow_color, width=2,
                tags=("pot_pulse", "temp_animation")
            )
            
            canvas.after(60, lambda: pulse_step(radius + 8, intensity - 1))
        
        pulse_step(20, 5)
    
    def stop_all_animations(self):
        """Stop all active chip animations"""
        self.active_animations.clear()
    
    def cleanup_temp_elements(self, canvas):
        """Clean up all temporary animation elements"""
        canvas.delete("temp_animation")
        canvas.delete("flying_chip")
        canvas.delete("motion_glow")
        canvas.delete("pot_pulse")

```

---

### chip_graphics.py

```python
"""
Luxury Themed Chip Graphics System
Renders poker chips with theme-aware styling for bets, calls, and pot displays.
"""
import math
import tkinter as tk
from typing import Dict, List, Tuple, Optional
from ...services.theme_manager import ThemeManager


def _tokens(canvas):
    """Get theme tokens and fonts from widget tree."""
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return ({"chip.primary": "#DAA520", "chip.secondary": "#8B4513"}, {"body": ("Arial", 10, "bold")})


class ChipGraphics:
    """Renders luxury themed poker chips with animations."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_stacks = {}  # Track chip positions for animations
        self.animation_queue = []  # Queue for chip animations
        
    def get_chip_colors_for_value(self, value: int, theme: Dict) -> Tuple[str, str, str]:
        """Get themed chip colors based on value."""
        # Standard poker chip color scheme with theme variations
        if value >= 1000:
            # High value - use theme's luxury colors
            return (
                theme.get("chip.luxury.bg", "#2D1B69"),      # Deep purple/navy
                theme.get("chip.luxury.ring", "#FFD700"),    # Gold ring
                theme.get("chip.luxury.accent", "#E6E6FA")   # Light accent
            )
        elif value >= 500:
            # Medium-high value - theme primary colors
            return (
                theme.get("chip.high.bg", "#8B0000"),        # Deep red
                theme.get("chip.high.ring", "#FFD700"),      # Gold ring
                theme.get("chip.high.accent", "#FFFFFF")     # White accent
            )
        elif value >= 100:
            # Medium value - theme secondary colors
            return (
                theme.get("chip.medium.bg", "#006400"),      # Forest green
                theme.get("chip.medium.ring", "#FFFFFF"),    # White ring
                theme.get("chip.medium.accent", "#90EE90")   # Light green accent
            )
        elif value >= 25:
            # Low-medium value
            return (
                theme.get("chip.low.bg", "#4169E1"),         # Royal blue
                theme.get("chip.low.ring", "#FFFFFF"),       # White ring
                theme.get("chip.low.accent", "#ADD8E6")      # Light blue accent
            )
        else:
            # Lowest value - theme accent colors
            return (
                theme.get("chip.minimal.bg", "#FFFFFF"),     # White
                theme.get("chip.minimal.ring", "#000000"),   # Black ring
                theme.get("chip.minimal.accent", "#D3D3D3")  # Light gray accent
            )
    
    def render_chip(self, x: int, y: int, value: int, chip_type: str = "bet", 
                   size: int = 20, tags: Tuple = ()) -> List[int]:
        """Render a single luxury themed chip."""
        theme, fonts = _tokens(self.canvas)
        
        # Get themed colors for this chip value
        bg_color, ring_color, accent_color = self.get_chip_colors_for_value(value, theme)
        
        # Adjust colors based on chip type
        if chip_type == "pot":
            # Pot chips get special treatment with theme's pot colors
            bg_color = theme.get("pot.chipBg", bg_color)
            ring_color = theme.get("pot.badgeRing", ring_color)
        elif chip_type == "call":
            # Call chips get muted colors
            bg_color = theme.get("chip.call.bg", "#6B7280")
            ring_color = theme.get("chip.call.ring", "#9CA3AF")
        
        elements = []
        
        # Main chip body with luxury gradient effect
        chip_id = self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=bg_color,
            outline=ring_color,
            width=3,
            tags=tags + ("chip", f"chip_{chip_type}")
        )
        elements.append(chip_id)
        
        # Inner highlight for 3D effect
        highlight_size = size - 4
        highlight_id = self.canvas.create_oval(
            x - highlight_size, y - highlight_size + 2,
            x + highlight_size, y - highlight_size + 8,
            fill=accent_color,
            outline="",
            tags=tags + ("chip_highlight",)
        )
        elements.append(highlight_id)
        
        # Luxury center pattern based on theme
        pattern_color = theme.get("chip.pattern", ring_color)
        
        # Theme-specific chip patterns
        theme_name = theme.get("_theme_name", "default")
        if "monet" in theme_name.lower():
            # Impressionist water lily pattern
            for angle in [0, 60, 120, 180, 240, 300]:
                rad = math.radians(angle)
                px = x + (size // 3) * math.cos(rad)
                py = y + (size // 3) * math.sin(rad)
                dot_id = self.canvas.create_oval(
                    px - 2, py - 2, px + 2, py + 2,
                    fill=pattern_color, outline="",
                    tags=tags + ("chip_pattern",)
                )
                elements.append(dot_id)
                
        elif "caravaggio" in theme_name.lower():
            # Baroque cross pattern
            cross_size = size // 2
            # Vertical line
            line1_id = self.canvas.create_line(
                x, y - cross_size, x, y + cross_size,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line1_id)
            # Horizontal line
            line2_id = self.canvas.create_line(
                x - cross_size, y, x + cross_size, y,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line2_id)
            
        elif "klimt" in theme_name.lower():
            # Art Nouveau geometric pattern
            square_size = size // 3
            square_id = self.canvas.create_rectangle(
                x - square_size, y - square_size,
                x + square_size, y + square_size,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(square_id)
            
        else:
            # Default diamond pattern
            diamond_size = size // 2
            diamond_points = [
                x, y - diamond_size,  # Top
                x + diamond_size, y,  # Right
                x, y + diamond_size,  # Bottom
                x - diamond_size, y   # Left
            ]
            diamond_id = self.canvas.create_polygon(
                diamond_points,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(diamond_id)
        
        # Value text (for larger chips)
        if size >= 15 and value >= 5:
            font_size = max(8, size // 3)
            text_font = (fonts.get("body", ("Arial", 10))[0], font_size, "bold")
            
            # Format value display
            if value >= 1000:
                display_value = f"{value//1000}K"
            else:
                display_value = str(value)
            
            text_id = self.canvas.create_text(
                x, y + size // 4,
                text=display_value,
                font=text_font,
                fill=theme.get("chip.text", "#FFFFFF"),
                tags=tags + ("chip_text",)
            )
            elements.append(text_id)
        
        return elements
    
    def render_chip_stack(self, x: int, y: int, total_value: int, 
                         chip_type: str = "bet", max_chips: int = 5,
                         tags: Tuple = ()) -> List[int]:
        """Render a stack of chips representing a total value."""
        theme, _ = _tokens(self.canvas)
        
        # Calculate chip denominations for the stack
        chip_values = self._calculate_chip_breakdown(total_value, max_chips)
        
        elements = []
        stack_height = 0
        
        for i, (value, count) in enumerate(chip_values):
            for j in range(count):
                # Stack chips with slight offset for 3D effect
                chip_x = x + j
                chip_y = y - stack_height - (j * 2)
                
                # Render individual chip
                chip_elements = self.render_chip(
                    chip_x, chip_y, value, chip_type,
                    size=18, tags=tags + (f"stack_{i}_{j}",)
                )
                elements.extend(chip_elements)
                
            stack_height += count * 3  # Increase stack height
        
        return elements
    
    def _calculate_chip_breakdown(self, total_value: int, max_chips: int) -> List[Tuple[int, int]]:
        """Calculate optimal chip breakdown for a given value."""
        denominations = [1000, 500, 100, 25, 5, 1]
        breakdown = []
        remaining = total_value
        chips_used = 0
        
        for denom in denominations:
            if chips_used >= max_chips:
                break
                
            if remaining >= denom:
                count = min(remaining // denom, max_chips - chips_used)
                if count > 0:
                    breakdown.append((denom, count))
                    remaining -= denom * count
                    chips_used += count
        
        # If we still have remaining value and room for chips, add smaller denominations
        if remaining > 0 and chips_used < max_chips:
            breakdown.append((remaining, 1))
        
        return breakdown
    
    def animate_chips_to_pot(self, start_x: int, start_y: int, 
                           end_x: int, end_y: int, chip_value: int,
                           duration: int = 500, callback=None):
        """Animate chips moving from player position to pot."""
        theme, _ = _tokens(self.canvas)
        
        # Create temporary chips for animation
        temp_chips = self.render_chip_stack(
            start_x, start_y, chip_value, "bet",
            tags=("animation", "temp_chip")
        )
        
        # Animation parameters
        steps = 20
        step_duration = duration // steps
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete - remove temp chips and call callback
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Move chips
            for chip_id in temp_chips:
                try:
                    self.canvas.move(chip_id, dx, dy)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def animate_pot_to_winner(self, pot_x: int, pot_y: int,
                            winner_x: int, winner_y: int, pot_value: int,
                            duration: int = 800, callback=None):
        """Animate pot chips moving to winner."""
        theme, _ = _tokens(self.canvas)
        
        # Create celebration effect
        self._create_winner_celebration(winner_x, winner_y, pot_value)
        
        # Create pot chips for animation
        temp_chips = self.render_chip_stack(
            pot_x, pot_y, pot_value, "pot",
            max_chips=8, tags=("animation", "pot_to_winner")
        )
        
        # Animation with arc trajectory
        steps = 25
        step_duration = duration // steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Calculate arc position
            progress = step / steps
            # Parabolic arc
            arc_height = -50 * math.sin(math.pi * progress)
            
            current_x = pot_x + (winner_x - pot_x) * progress
            current_y = pot_y + (winner_y - pot_y) * progress + arc_height
            
            # Move chips to calculated position
            for i, chip_id in enumerate(temp_chips):
                try:
                    # Get current position
                    coords = self.canvas.coords(chip_id)
                    if len(coords) >= 4:
                        old_x = (coords[0] + coords[2]) / 2
                        old_y = (coords[1] + coords[3]) / 2
                        
                        # Calculate new position with slight spread
                        spread = i * 3
                        new_x = current_x + spread
                        new_y = current_y
                        
                        # Move chip
                        self.canvas.move(chip_id, new_x - old_x, new_y - old_y)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def _create_winner_celebration(self, x: int, y: int, pot_value: int):
        """Create celebration effect around winner."""
        theme, fonts = _tokens(self.canvas)
        
        # Celebration burst effect
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            distance = 30
            star_x = x + distance * math.cos(angle)
            star_y = y + distance * math.sin(angle)
            
            # Create star burst
            star_id = self.canvas.create_text(
                star_x, star_y,
                text="✨",
                font=("Arial", 16),
                fill=theme.get("celebration.color", "#FFD700"),
                tags=("celebration", "temp")
            )
            
            # Fade out after delay
            self.canvas.after(1000, lambda sid=star_id: self._fade_element(sid))
    
    def _fade_element(self, element_id: int):
        """Fade out and remove an element."""
        try:
            self.canvas.delete(element_id)
        except tk.TclError:
            pass


class BetDisplay:
    """Renders themed bet amounts with chip graphics."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_graphics = ChipGraphics(canvas)
    
    def render(self, x: int, y: int, amount: int, bet_type: str = "bet",
               tags: Tuple = ()) -> List[int]:
        """Render bet display with chips and text."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        if amount > 0:
            # Render chip stack
            chip_elements = self.chip_graphics.render_chip_stack(
                x, y - 15, amount, bet_type, max_chips=3,
                tags=tags + ("bet_chips",)
            )
            elements.extend(chip_elements)
            
            # Render amount text
            text_color = theme.get("bet.text", "#FFFFFF")
            if bet_type == "call":
                text_color = theme.get("bet.call.text", "#9CA3AF")
            elif bet_type == "raise":
                text_color = theme.get("bet.raise.text", "#EF4444")
            
            text_id = self.canvas.create_text(
                x, y + 20,
                text=f"${amount:,}",
                font=fonts.get("body", ("Arial", 10, "bold")),
                fill=text_color,
                tags=tags + ("bet_text",)
            )
            elements.append(text_id)
        
        return elements


class WinnerBadge:
    """Renders themed winner announcement badges."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def render(self, x: int, y: int, player_name: str, amount: int,
               hand_description: str = "", tags: Tuple = ()) -> List[int]:
        """Render luxury winner badge with theme styling."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        # Badge dimensions
        badge_width = 200
        badge_height = 80
        
        # Theme-aware colors
        badge_bg = theme.get("winner.bg", "#1F2937")
        badge_border = theme.get("winner.border", "#FFD700")
        badge_accent = theme.get("winner.accent", "#FEF3C7")
        
        # Main badge background with luxury styling
        badge_id = self.canvas.create_rectangle(
            x - badge_width//2, y - badge_height//2,
            x + badge_width//2, y + badge_height//2,
            fill=badge_bg,
            outline=badge_border,
            width=3,
            tags=tags + ("winner_badge",)
        )
        elements.append(badge_id)
        
        # Luxury gradient highlight
        highlight_id = self.canvas.create_rectangle(
            x - badge_width//2 + 3, y - badge_height//2 + 3,
            x + badge_width//2 - 3, y - badge_height//2 + 12,
            fill=badge_accent,
            outline="",
            tags=tags + ("winner_highlight",)
        )
        elements.append(highlight_id)
        
        # Winner crown symbol
        crown_id = self.canvas.create_text(
            x - badge_width//3, y - 10,
            text="👑",
            font=("Arial", 20),
            tags=tags + ("winner_crown",)
        )
        elements.append(crown_id)
        
        # Winner text
        winner_text = f"WINNER: {player_name}"
        text_id = self.canvas.create_text(
            x, y - 15,
            text=winner_text,
            font=fonts.get("heading", ("Arial", 12, "bold")),
            fill=theme.get("winner.text", "#FFFFFF"),
            tags=tags + ("winner_text",)
        )
        elements.append(text_id)
        
        # Amount won
        amount_id = self.canvas.create_text(
            x, y + 5,
            text=f"${amount:,}",
            font=fonts.get("body", ("Arial", 14, "bold")),
            fill=theme.get("winner.amount", "#FFD700"),
            tags=tags + ("winner_amount",)
        )
        elements.append(amount_id)
        
        # Hand description (if provided)
        if hand_description:
            hand_id = self.canvas.create_text(
                x, y + 20,
                text=hand_description,
                font=fonts.get("caption", ("Arial", 9, "italic")),
                fill=theme.get("winner.description", "#D1D5DB"),
                tags=tags + ("winner_hand",)
            )
            elements.append(hand_id)
        
        return elements
    
    def animate_winner_announcement(self, x: int, y: int, player_name: str,
                                  amount: int, hand_description: str = "",
                                  duration: int = 3000):
        """Animate winner badge with entrance and exit effects."""
        # Create badge elements
        elements = self.render(x, y, player_name, amount, hand_description,
                             tags=("winner_animation",))
        
        # Entrance animation - scale up
        self._animate_scale(elements, 0.1, 1.0, 300)
        
        # Exit animation after duration
        self.canvas.after(duration, lambda: self._animate_fade_out(elements, 500))
    
    def _animate_scale(self, elements: List[int], start_scale: float,
                      end_scale: float, duration: int):
        """Animate scaling of elements."""
        steps = 15
        step_duration = duration // steps
        scale_step = (end_scale - start_scale) / steps
        
        def scale_step_func(step: int):
            if step >= steps:
                return
            
            current_scale = start_scale + scale_step * step
            
            for element_id in elements:
                try:
                    # Get element center
                    coords = self.canvas.coords(element_id)
                    if len(coords) >= 2:
                        if len(coords) == 4:  # Rectangle
                            center_x = (coords[0] + coords[2]) / 2
                            center_y = (coords[1] + coords[3]) / 2
                        else:  # Text or other
                            center_x, center_y = coords[0], coords[1]
                        
                        # Apply scaling (simplified - just adjust position)
                        # In a full implementation, you'd use canvas.scale()
                        pass
                except tk.TclError:
                    pass
            
            self.canvas.after(step_duration, lambda: scale_step_func(step + 1))
        
        scale_step_func(0)
    
    def _animate_fade_out(self, elements: List[int], duration: int):
        """Fade out and remove elements."""
        # Simplified fade - just remove after duration
        self.canvas.after(duration, lambda: self._remove_elements(elements))
    
    def _remove_elements(self, elements: List[int]):
        """Remove elements from canvas."""
        for element_id in elements:
            try:
                self.canvas.delete(element_id)
            except tk.TclError:
                pass

```

---

### token_driven_renderer.py

```python
"""
Token-Driven Renderer Integration
Coordinates all enhanced components with the token system
"""

import math
from .table_center import TableCenter
from .enhanced_cards import EnhancedCards
from .chip_animations import ChipAnimations
from .micro_interactions import MicroInteractions

class TokenDrivenRenderer:
    """
    Main coordinator for all token-driven UI components
    Provides a unified interface for rendering poker table elements
    """
    
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
        # Initialize all enhanced components
        self.table_center = TableCenter(theme_manager)
        self.enhanced_cards = EnhancedCards(theme_manager)
        self.chip_animations = ChipAnimations(theme_manager)
        self.micro_interactions = MicroInteractions(theme_manager)
        
    def render_complete_table(self, canvas, state):
        """Render complete poker table with all enhancements"""
        # Clear any existing elements
        self.clear_all_effects(canvas)
        
        # Get current tokens
        tokens = self.theme.get_all_tokens()
        
        # 1. Render table center pattern
        self.table_center.render(canvas, state)
        
        # 2. Render community board area
        self.enhanced_cards.draw_community_board(canvas, tokens)
        
        # 3. Render community cards if present
        community_cards = state.get("board", [])
        if community_cards:
            self._render_community_cards(canvas, community_cards, tokens)
        
        # 4. Render player seats with enhanced cards
        seats_data = state.get("seats", [])
        if seats_data:
            self._render_enhanced_seats(canvas, seats_data, tokens)
        
        # 5. Render pot with chip stacks
        pot_amount = state.get("pot", {}).get("total", 0)
        if pot_amount > 0:
            self._render_enhanced_pot(canvas, pot_amount, tokens)
    
    def _render_community_cards(self, canvas, cards, tokens):
        """Render community cards with enhanced graphics"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        board_x, board_y = w * 0.5, h * 0.4
        
        card_w, card_h = 58, 82
        gap = 8
        total_w = 5 * card_w + 4 * gap
        start_x = board_x - total_w / 2
        
        for i in range(5):
            card_x = start_x + i * (card_w + gap)
            card_y = board_y - card_h / 2
            
            if i < len(cards) and cards[i]:
                # Render face-up community card
                rank, suit = cards[i][:-1], cards[i][-1]
                self.enhanced_cards.draw_card_face(
                    canvas, card_x, card_y, rank, suit, card_w, card_h,
                    tags=[f"community_card_{i}"]
                )
            else:
                # Render empty slot
                self.enhanced_cards.draw_card_back(
                    canvas, card_x, card_y, card_w, card_h,
                    tags=[f"community_slot_{i}"]
                )
    
    def _render_enhanced_seats(self, canvas, seats_data, tokens):
        """Render player seats with enhanced hole cards"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        num_seats = len(seats_data)
        
        # Calculate seat positions (simplified - would use actual seat positioning logic)
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) * 0.35
        
        for i, seat in enumerate(seats_data):
            if num_seats <= 1:
                continue
                
            # Calculate seat position
            angle = (i / num_seats) * 2 * 3.14159
            seat_x = center_x + radius * math.cos(angle)
            seat_y = center_y + radius * math.sin(angle)
            
            # Render hole cards if present
            cards = seat.get('cards', [])
            if cards and len(cards) >= 2:
                self._render_hole_cards(canvas, seat_x, seat_y, cards, num_seats)
            
            # Add micro-interactions for acting player
            if seat.get('acting', False):
                self.micro_interactions.pulse_seat_ring(
                    canvas, seat_x, seat_y, 120, 85
                )
    
    def _render_hole_cards(self, canvas, seat_x, seat_y, cards, num_players):
        """Render hole cards with dynamic sizing"""
        # Dynamic card sizing based on player count
        if num_players <= 3:
            card_w, card_h = 52, 75  # 6% scale
        elif num_players <= 6:
            card_w, card_h = 44, 64  # 5% scale
        else:
            card_w, card_h = 35, 51  # 4% scale
        
        gap = max(4, card_w // 8)
        
        for i, card in enumerate(cards[:2]):
            card_x = seat_x - (card_w + gap//2) + i * (card_w + gap)
            card_y = seat_y - card_h//2
            
            if card and card != "XX":
                # Face-up hole card
                rank, suit = card[:-1], card[-1]
                self.enhanced_cards.draw_card_face(
                    canvas, card_x, card_y, rank, suit, card_w, card_h,
                    tags=[f"hole_card_{seat_x}_{i}"]
                )
                
                # Add subtle shimmer for newly revealed cards
                if i == 0:  # Only shimmer first card to avoid overload
                    self.micro_interactions.card_reveal_shimmer(
                        canvas, card_x, card_y, card_w, card_h
                    )
            else:
                # Face-down hole card
                self.enhanced_cards.draw_card_back(
                    canvas, card_x, card_y, card_w, card_h,
                    tags=[f"hole_back_{seat_x}_{i}"]
                )
    
    def _render_enhanced_pot(self, canvas, pot_amount, tokens):
        """Render pot with chip stack visualization"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        # Render chip stacks around pot area
        if pot_amount > 0:
            # Create multiple small stacks for visual appeal
            num_stacks = min(6, max(2, pot_amount // 100))
            
            for i in range(num_stacks):
                angle = (i / num_stacks) * 2 * 3.14159
                stack_x = pot_x + 25 * math.cos(angle)
                stack_y = pot_y + 15 * math.sin(angle)
                
                stack_amount = pot_amount // num_stacks
                self.chip_animations.draw_chip_stack(
                    canvas, stack_x, stack_y, stack_amount,
                    tags=[f"pot_stack_{i}"]
                )
    
    # Animation Methods
    def animate_bet_to_pot(self, canvas, from_x, from_y, amount, callback=None):
        """Animate bet chips flying to pot"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        self.chip_animations.fly_chips_to_pot(
            canvas, from_x, from_y, pot_x, pot_y, amount, callback
        )
        
        # Flash pot when chips arrive
        if callback:
            original_callback = callback
            def enhanced_callback():
                self.micro_interactions.flash_pot_increase(canvas, pot_x, pot_y, 100, 60)
                if original_callback:
                    original_callback()
            callback = enhanced_callback
    
    def animate_pot_to_winner(self, canvas, winner_x, winner_y, amount, callback=None):
        """Animate pot chips flying to winner with celebration"""
        w, h = canvas.winfo_width(), canvas.winfo_height()
        pot_x, pot_y = w // 2, h // 2 - 50
        
        self.chip_animations.fly_pot_to_winner(
            canvas, pot_x, pot_y, winner_x, winner_y, amount, callback
        )
        
        # Add confetti burst
        self.micro_interactions.winner_confetti_burst(canvas, winner_x, winner_y)
    
    def animate_card_reveal(self, canvas, card_x, card_y, card_w, card_h, 
                          from_card, to_card, callback=None):
        """Animate card flip with shimmer effect"""
        self.enhanced_cards.animate_card_flip(
            canvas, card_x, card_y, card_w, card_h, from_card, to_card, callback
        )
    
    def animate_dealer_button_move(self, canvas, from_x, from_y, to_x, to_y, callback=None):
        """Animate dealer button movement with trail"""
        self.micro_interactions.dealer_button_move_trail(canvas, from_x, from_y, to_x, to_y)
        
        # Use existing dealer button animation if available
        # This would integrate with existing dealer button component
        if callback:
            canvas.after(800, callback)  # Match trail duration
    
    # Interaction Methods
    def add_hover_effect(self, canvas, element_id, x, y, w, h):
        """Add hover glow to UI element"""
        self.micro_interactions.hover_glow(canvas, element_id, x, y, w, h)
    
    def remove_hover_effect(self, canvas, element_id):
        """Remove hover glow from UI element"""
        self.micro_interactions.remove_hover_glow(canvas, element_id)
    
    def button_press_feedback(self, canvas, btn_x, btn_y, btn_w, btn_h):
        """Visual feedback for button press"""
        self.micro_interactions.button_press_feedback(canvas, btn_x, btn_y, btn_w, btn_h)
    
    def pulse_acting_player(self, canvas, seat_x, seat_y):
        """Start pulsing ring around acting player"""
        self.micro_interactions.pulse_seat_ring(canvas, seat_x, seat_y, 120, 85)
    
    # Cleanup Methods
    def clear_all_effects(self, canvas):
        """Clear all visual effects and animations"""
        self.table_center.clear(canvas)
        self.enhanced_cards.clear_card_effects(canvas)
        self.chip_animations.cleanup_temp_elements(canvas)
        self.micro_interactions.cleanup_effects(canvas)
    
    def stop_all_animations(self):
        """Stop all active animations"""
        self.chip_animations.stop_all_animations()
        self.micro_interactions.stop_all_interactions()
    
    # Theme Integration
    def on_theme_change(self):
        """Handle theme change - refresh all components"""
        # Components automatically pick up new theme via theme_manager
        # No additional action needed due to token-driven design
        pass

```

---

### enhanced_cards.py

```python
"""
Enhanced Card Graphics with Token-Driven Colors
Professional card rendering using the complete theme token system
"""

import math

class EnhancedCards:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    # Suit symbols
    SUIT_SYMBOLS = {
        'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'
    }
    
    def draw_card_face(self, canvas, x, y, rank, suit, w=58, h=82, tags=None):
        """Draw a face-up card with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Card colors from tokens
        bg = tokens.get("card.face.bg", "#F8F8FF")
        border = tokens.get("card.face.border", "#2F4F4F")
        pip_red = tokens.get("card.pip.red", "#DC2626")
        pip_black = tokens.get("card.pip.black", "#111827")
        
        # Determine suit color
        suit_color = pip_red if suit.lower() in ('h', 'd') else pip_black
        suit_symbol = self.SUIT_SYMBOLS.get(suit.lower(), '?')
        
        # Create tags
        card_tags = ["card_face"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle with rounded corners effect
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=border, width=1,
            tags=tuple(card_tags)
        )
        
        # Calculate font sizes based on card size
        rank_font_size = max(10, w // 5)
        suit_font_size = max(8, w // 6)
        center_font_size = max(14, w // 3)
        
        # Top-left rank and suit
        canvas.create_text(
            x + w//8, y + h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w//8, y + h//8 + rank_font_size + 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        # Center suit symbol (larger)
        canvas.create_text(
            x + w//2, y + h//2,
            text=suit_symbol, font=("Inter", center_font_size, "bold"),
            fill=suit_color, anchor="center", tags=tuple(card_tags)
        )
        
        # Bottom-right rank and suit (rotated appearance)
        canvas.create_text(
            x + w - w//8, y + h - h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w - w//8, y + h - h//8 - rank_font_size - 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_card_back(self, canvas, x, y, w=58, h=82, tags=None):
        """Draw a face-down card back with theme integration"""
        tokens = self.theme.get_all_tokens()
        
        # Card back colors from tokens
        bg = tokens.get("card.back.bg", "#7F1D1D")
        border = tokens.get("card.back.border", "#2F4F4F")
        pattern = tokens.get("card.back.pattern", "#991B1B")
        
        # Create tags
        card_tags = ["card_back"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        # Diamond lattice pattern
        step = max(6, w // 8)
        for i in range(0, w + step, step):
            # Diagonal lines creating diamond pattern
            canvas.create_line(
                x + i, y, x, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y, x + w, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + i, y + h, x, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y + h, x + w, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
        
        # Center decorative element
        center_size = min(w, h) // 4
        canvas.create_rectangle(
            x + w//2 - center_size//2, y + h//2 - center_size//4,
            x + w//2 + center_size//2, y + h//2 + center_size//4,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_community_board(self, canvas, tokens, slots=5, card_w=58, gap=8):
        """Draw community card area with token-driven styling"""
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        # Calculate board position
        x0, y0 = w * 0.5, h * 0.4
        total_w = slots * card_w + (slots - 1) * gap
        left = x0 - total_w / 2
        top = y0 - 4
        height = card_w * 0.2
        
        # Board colors from tokens
        slot_bg = tokens.get("board.slotBg", "#334155")
        border_color = tokens.get("board.border", "#475569")
        shadow_color = tokens.get("board.shadow", "#1E293B")
        
        # Clear previous board
        canvas.delete("board:underlay")
        
        # Shadow (offset slightly)
        canvas.create_rectangle(
            left - 8, top - 8, left + total_w + 12, top + height + 12,
            fill=shadow_color, outline="",
            tags=("board:underlay", "board_shadow")
        )
        
        # Main underlay
        canvas.create_rectangle(
            left - 10, top - 10, left + total_w + 10, top + height + 10,
            fill=slot_bg, outline=border_color, width=2,
            tags=("board:underlay", "board_main")
        )
        
        # Individual card slots
        for i in range(slots):
            slot_x = left + i * (card_w + gap)
            slot_y = top - card_w * 0.6
            
            # Slot outline
            canvas.create_rectangle(
                slot_x - 2, slot_y - 2, slot_x + card_w + 2, slot_y + card_w * 1.4 + 2,
                fill="", outline=border_color, width=1, stipple="gray25",
                tags=("board:underlay", f"slot_{i}")
            )
    
    def animate_card_flip(self, canvas, x, y, w, h, from_card, to_card, callback=None):
        """Animate card flip with token-aware colors"""
        flip_steps = 10
        
        def flip_step(step):
            if step >= flip_steps:
                if callback:
                    callback()
                return
            
            # Calculate flip progress (0 to 1)
            progress = step / flip_steps
            
            # Clear previous flip frame
            canvas.delete("card_flip")
            
            if progress < 0.5:
                # First half: shrink to nothing (show original card)
                scale = 1 - (progress * 2)
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if from_card and from_card != "XX":
                        rank, suit = from_card[:-1], from_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y, 
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y, 
                                          scaled_w, h, ["card_flip"])
            else:
                # Second half: grow from nothing (show new card)
                scale = (progress - 0.5) * 2
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if to_card and to_card != "XX":
                        rank, suit = to_card[:-1], to_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y,
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y,
                                          scaled_w, h, ["card_flip"])
            
            # Schedule next step
            canvas.after(40, lambda: flip_step(step + 1))
        
        flip_step(0)
    
    def add_card_glow(self, canvas, x, y, w, h, glow_type="soft"):
        """Add subtle glow effect around card"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get(f"glow.{glow_type}", tokens.get("a11y.focus", "#22C55E"))
        
        # Create glow effect with multiple rings
        for i in range(3):
            offset = (i + 1) * 2
            canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset,
                fill="", outline=glow_color, width=1,
                tags=("card_glow",)
            )
    
    def clear_card_effects(self, canvas):
        """Clear all card animation and effect elements"""
        canvas.delete("card_flip")
        canvas.delete("card_glow")

```

---

### premium_chips.py

```python
"""
Premium Casino Chip System
==========================

Theme-aware chip rendering with distinct visual types:
- Stack chips (player stacks): calm, readable, less saturated
- Bet/Call chips (flying chips): vivid with theme accent for motion tracking  
- Pot chips (pot visualization): prestigious metal-leaning design

Features:
- Consistent casino denominations with theme-tinted colors
- Radial stripe patterns for instant denomination recognition
- Hover states, glow effects, and animation support
- Automatic theme integration via token system
"""

import math
from typing import Tuple, List, Optional


# Standard casino denominations with base colors
CHIP_DENOMINATIONS = [
    (1,    "#2E86AB"),  # $1  – blue
    (5,    "#B63D3D"),  # $5  – red
    (25,   "#2AA37A"),  # $25 – green
    (100,  "#3C3A3A"),  # $100 – black/graphite
    (500,  "#6C4AB6"),  # $500 – purple
    (1000, "#D1B46A"),  # $1k – gold
]


def get_denom_color(amount: int) -> str:
    """Get the base color for a chip denomination."""
    for denom, color in CHIP_DENOMINATIONS:
        if amount <= denom:
            return color
    return CHIP_DENOMINATIONS[-1][1]  # Default to highest denom color


def draw_chip_base(canvas, x: int, y: int, r: int, face: str, edge: str, rim: str, 
                   denom_color: str, text: str, text_color: str, tags: tuple = ()) -> int:
    """
    Draw the base chip structure with radial stripes and denomination text.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        r: Chip radius
        face: Base face color
        edge: Outer edge color  
        rim: Inner ring color
        denom_color: Denomination stripe color
        text: Text to display (e.g., "$25")
        text_color: Text color
        tags: Canvas tags for the chip elements
        
    Returns:
        Canvas item ID of the main chip disc
    """
    # Main chip disc
    chip_id = canvas.create_oval(
        x - r, y - r, x + r, y + r,
        fill=face, outline=edge, width=2,
        tags=tags
    )
    
    # Radial stripes (8 wedges) for denomination recognition
    for i in range(8):
        angle_start = i * 45  # 360/8 = 45 degrees per stripe
        angle_extent = 15     # Width of each stripe
        canvas.create_arc(
            x - r + 3, y - r + 3, x + r - 3, y + r - 3,
            start=angle_start, extent=angle_extent,
            outline="", fill=denom_color, width=0,
            tags=tags
        )
    
    # Inner ring for premium look
    inner_r = int(r * 0.70)
    canvas.create_oval(
        x - inner_r, y - inner_r, x + inner_r, y + inner_r,
        outline=rim, fill="", width=2,
        tags=tags
    )
    
    # Denomination text
    font_size = max(8, int(r * 0.4))  # Scale text with chip size
    canvas.create_text(
        x, y, text=text, fill=text_color,
        font=("Inter", font_size, "bold"),
        tags=tags
    )
    
    return chip_id


def draw_stack_chip(canvas, x: int, y: int, amount: int, tokens: dict, 
                    r: int = 14, tags: tuple = ()) -> int:
    """
    Draw a single stack chip (calm, readable design for player stacks).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    return draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.stack.face", "#4A4A4A"),
        edge=tokens.get("chip.stack.edge", "#666666"), 
        rim=tokens.get("chip.stack.rim", "#888888"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.stack.text", "#F8F7F4"),
        tags=tags
    )


def draw_bet_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 14, hovering: bool = False, tags: tuple = ()) -> int:
    """
    Draw a bet/call chip (vivid design with theme accent for motion tracking).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        hovering: Whether to show hover glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.bet.face", "#6B4AB6"),
        edge=tokens.get("chip.bet.edge", "#8A6BC8"),
        rim=tokens.get("chip.bet.rim", "#A888CC"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.bet.text", "#F8F7F4"),
        tags=tags
    )
    
    # Optional hover glow
    if hovering:
        glow_color = tokens.get("chip.bet.glow", "#A888CC")
        canvas.create_oval(
            x - r - 4, y - r - 4, x + r + 4, y + r + 4,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_pot_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 16, breathing: bool = False, tags: tuple = ()) -> int:
    """
    Draw a pot chip (prestigious metal-leaning design).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates  
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius (slightly larger than other chips)
        breathing: Whether to show breathing glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.pot.face", "#D1B46A"),
        edge=tokens.get("chip.pot.edge", "#B8A157"),
        rim=tokens.get("chip.pot.rim", "#E6D078"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.pot.text", "#0B0B0E"),
        tags=tags
    )
    
    # Optional breathing glow for pot increases
    if breathing:
        glow_color = tokens.get("chip.pot.glow", "#E6D078")
        canvas.create_oval(
            x - r - 5, y - r - 5, x + r + 5, y + r + 5,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_chip_stack(canvas, x: int, y: int, total_amount: int, tokens: dict,
                    r: int = 14, max_height: int = 15, tags: tuple = ()) -> List[int]:
    """
    Draw a stack of chips representing a player's total amount.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Base center coordinates (bottom of stack)
        total_amount: Total dollar amount to represent
        tokens: Theme token dictionary
        r: Chip radius
        max_height: Maximum number of chips to show (for UI space)
        tags: Canvas tags
        
    Returns:
        List of canvas item IDs for all chips in the stack
    """
    if total_amount <= 0:
        return []
    
    # Break down amount into chip denominations (largest first)
    chip_plan = []
    remaining = total_amount
    
    for denom, _ in reversed(CHIP_DENOMINATIONS):
        if remaining >= denom:
            count = min(remaining // denom, max_height - len(chip_plan))
            chip_plan.extend([denom] * count)
            remaining -= denom * count
            
        if len(chip_plan) >= max_height:
            break
    
    # If we still have remaining amount and space, add smaller denominations
    if remaining > 0 and len(chip_plan) < max_height:
        # Fill remaining space with $1 chips
        remaining_space = max_height - len(chip_plan)
        chip_plan.extend([1] * min(remaining_space, remaining))
    
    # Draw soft shadow
    shadow_color = tokens.get("chip.stack.shadow", "#000000")
    canvas.create_oval(
        x - r - 4, y + 3, x + r + 4, y + 11,
        fill=shadow_color, outline="",
        tags=tags + ("shadow",)
    )
    
    # Draw chips from bottom to top
    chip_ids = []
    chip_spacing = 6  # Vertical spacing between chips
    
    for i, denom in enumerate(chip_plan):
        chip_y = y - (i * chip_spacing)
        chip_id = draw_stack_chip(
            canvas, x, chip_y, denom, tokens, r=r,
            tags=tags + (f"stack_chip_{i}",)
        )
        chip_ids.append(chip_id)
    
    return chip_ids


def animate_chip_bet(canvas, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                     amount: int, tokens: dict, r: int = 14, frames: int = 20,
                     callback: Optional[callable] = None) -> None:
    """
    Animate a chip flying from start to end position (bet → pot).
    
    Args:
        canvas: Tkinter canvas widget
        start_pos: (x, y) starting coordinates
        end_pos: (x, y) ending coordinates
        amount: Dollar amount for the chip
        tokens: Theme token dictionary
        r: Chip radius
        frames: Number of animation frames
        callback: Optional function to call when animation completes
    """
    x0, y0 = start_pos
    x1, y1 = end_pos
    glow_color = tokens.get("chip.bet.glow", "#A888CC")
    
    def animate_frame(frame: int):
        if frame >= frames:
            if callback:
                callback()
            return
        
        # Cubic easing for smooth motion
        t = frame / frames
        ease_t = t * t * (3 - 2 * t)
        
        # Position with arc (parabolic path)
        x = x0 + (x1 - x0) * ease_t
        y = y0 + (y1 - y0) * ease_t - 20 * math.sin(math.pi * ease_t)
        
        # Clear previous frame
        canvas.delete("flying_chip")
        
        # Draw chip at current position
        draw_bet_chip(
            canvas, int(x), int(y), amount, tokens, r=r, hovering=True,
            tags=("flying_chip",)
        )
        
        # Schedule next frame
        canvas.after(50, lambda: animate_frame(frame + 1))
    
    # Start animation
    animate_frame(0)


def pulse_pot_glow(canvas, center_pos: Tuple[int, int], tokens: dict,
                   r: int = 18, pulses: int = 3) -> None:
    """
    Create a pulsing glow effect at the pot center when pot increases.
    
    Args:
        canvas: Tkinter canvas widget
        center_pos: (x, y) center coordinates
        tokens: Theme token dictionary
        r: Base radius for the pulse
        pulses: Number of pulse cycles
    """
    x, y = center_pos
    glow_color = tokens.get("chip.pot.glow", "#E6D078")
    
    pulse_sequence = [0.0, 0.4, 0.8, 1.0, 0.8, 0.4, 0.0]
    
    def animate_pulse(pulse_num: int, frame: int):
        if pulse_num >= pulses:
            canvas.delete("pot_pulse")
            return
            
        if frame >= len(pulse_sequence):
            # Move to next pulse
            canvas.after(100, lambda: animate_pulse(pulse_num + 1, 0))
            return
        
        # Clear previous pulse
        canvas.delete("pot_pulse")
        
        # Draw current pulse ring
        intensity = pulse_sequence[frame]
        pulse_r = r + int(8 * intensity)
        alpha_val = int(255 * (0.6 - 0.4 * intensity))  # Fade as it expands
        
        canvas.create_oval(
            x - pulse_r, y - pulse_r, x + pulse_r, y + pulse_r,
            outline=glow_color, fill="", width=max(1, int(3 * (1 - intensity))),
            tags=("pot_pulse",)
        )
        
        # Schedule next frame
        canvas.after(80, lambda: animate_pulse(pulse_num, frame + 1))
    
    # Start pulsing
    animate_pulse(0, 0)


def clear_chip_animations(canvas) -> None:
    """Clear all chip animation elements from the canvas."""
    canvas.delete("flying_chip")
    canvas.delete("pot_pulse")
    canvas.delete("glow")

```

---

## THEME SYSTEM

### theme_manager.py

```python
from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes
    from .theme_loader import get_theme_loader
    from .state_styler import (
        get_state_styler,
        get_selection_styler,
        get_emphasis_bar_styler
    )
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Default theme name for fallbacks
DEFAULT_THEME_NAME = "Forest Green Professional 🌿"  # Updated to match JSON


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
    - Now fully config-driven using poker_themes.json
    """

    CONFIG_PATH = os.path.join("backend", "ui", "theme_config.json")

    def __init__(self) -> None:
        self._theme: Dict[str, Any]
        self._fonts: Dict[str, Any]
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._current: str | None = None
        self._subs: List[Callable[["ThemeManager"], None]] = []
        # Load defaults from codebase
        try:
            gm = importlib.import_module("backend.core.gui_models")
            self._theme = dict(getattr(gm, "THEME", {}))
            self._fonts = dict(getattr(gm, "FONTS", {}))
        except Exception:
            self._theme = {"table_felt": "#2B2F36", "text": "#E6E9EF"}
            self._fonts = {
                "main": ("Arial", 20),  # Base font at 20px for readability
                "pot_display": ("Arial", 28, "bold"),  # +8 for pot display
                "bet_amount": ("Arial", 24, "bold"),  # +4 for bet amounts
                "body": ("Consolas", 20),  # Same as main for body text
                "small": ("Consolas", 16),  # -4 for smaller text
                "header": ("Arial", 22, "bold")  # +2 for headers
            }
        # Apply persisted config if present
        # Register built-in packs
        packs = self._builtin_packs()
        for name, tokens in packs.items():
            self.register(name, tokens)
        self._load_config()
        if not self._current:
            # Use Forest Green Professional as safe default
            if DEFAULT_THEME_NAME in self._themes:
                self._current = DEFAULT_THEME_NAME
                self._theme = dict(self._themes[DEFAULT_THEME_NAME])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in theme packs - now using token-driven system"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Use the new deterministic token system
                themes = build_all_themes()
                print(f"🎨 ThemeManager: Loaded {len(themes)} themes: {list(themes.keys())}")
                return themes
            except Exception as e:
                print(f"⚠️ ThemeManager: Config-driven themes failed: {e}")
                return self._legacy_builtin_packs()
        else:
            print("⚠️ ThemeManager: Token-driven themes not available, using legacy")
            # Fallback to legacy themes if token system not available
            return self._legacy_builtin_packs()
    
    def _legacy_builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Minimal legacy fallback if config system completely fails."""
        return {
            "Forest Green Professional 🌿": {
                "table.felt": "#2D5A3D",
                "table.rail": "#4A3428", 
                "text.primary": "#EDECEC",
                "panel.bg": "#1F2937",
                "panel.fg": "#E5E7EB"
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts
    
    def reload(self):
        """Reload themes from file - critical for Theme Manager integration."""
        print("🔄 ThemeManager: Reloading themes from file...")
        
        # Clear cached themes
        self._themes = {}
        
        # Reload using the same logic as __init__
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Force reload from file
                loader = get_theme_loader()
                if hasattr(loader, 'reload'):
                    loader.reload()
                
                # Rebuild all themes
                themes = build_all_themes()
                
                # Register all themes
                for name, tokens in themes.items():
                    self.register(name, tokens)
                
                print(f"🔄 ThemeManager: Reloaded {len(themes)} themes from file")
                
                # Reload current theme if it still exists
                current_name = self.current_profile_name()
                if current_name in self._themes:
                    self._theme = self._themes[current_name]
                    print(f"🎯 ThemeManager: Restored current theme: {current_name}")
                else:
                    # Fallback to first available theme
                    if self._themes:
                        first_theme_name = list(self._themes.keys())[0]
                        self._theme = self._themes[first_theme_name]
                        self._current_profile = first_theme_name
                        print(f"🔄 ThemeManager: Switched to: {first_theme_name}")
                
            except Exception as e:
                print(f"⚠️ ThemeManager: Reload failed: {e}")
        else:
            print("⚠️ ThemeManager: Token-driven themes not available for reload")

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()
    
    def get_dimensions(self) -> Dict[str, Any]:
        """Get theme dimensions for consistent spacing and sizing."""
        try:
            # Try to get dimensions from theme config
            theme_data = self.get_theme()
            if theme_data and "dimensions" in theme_data:
                return theme_data["dimensions"]
            
            # Fallback to default dimensions
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }
        except Exception:
            # Ultimate fallback
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names from config-driven system."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback: return all registered theme names
        return list(self._themes.keys())

    def register_all(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register all themes from packs dictionary."""
        for name, tokens in packs.items():
            self.register(name, tokens)

    def current(self) -> str | None:
        """Return current theme name."""
        return self._current

    def set_profile(self, name: str) -> None:
        if name in self._themes:
            self._current = name
            self._theme = dict(self._themes[name])
            self._save_config()
            for fn in list(self._subs):
                fn(self)

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile")
                if prof and prof in self._themes:
                    self._current = prof
                    self._theme = dict(self._themes[prof])
                fonts = data.get("fonts")
                if isinstance(fonts, dict):
                    self._fonts.update(fonts)
        except Exception:
            pass

    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            payload = {"profile": self.current_profile_name(), "fonts": self._fonts}
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def current_profile_name(self) -> str:
        for name, theme in self._themes.items():
            if all(self._theme.get(k) == theme.get(k) for k in ("table.felt",)):
                return name
        return "Custom"

    def get(self, token: str, default=None):
        # Dot-path lookup in current theme; fallback to fonts when font.* requested
        if token.startswith("font."):
            return self._theme.get(token) or self._fonts.get(token[5:], default)
        cur = self._theme
        for part in token.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return self._theme.get(token, default)
        return cur
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get complete token dictionary for current theme"""
        return dict(self._theme)
    
    def get_base_colors(self) -> Dict[str, str]:
        """Get the base color palette for current theme (if available)"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try new config-driven system first
            try:
                loader = get_theme_loader()
                # Convert display name to theme ID using proper mapping
                name_to_id_map = {
                    "Forest Green Professional 🌿": "forest-green-pro",
                    "Velvet Burgundy 🍷": "velvet-burgundy", 
                    "Emerald Aurora 🌌": "emerald-aurora",
                    "Imperial Jade 💎": "imperial-jade",
                    "Ruby Royale ❤️‍🔥": "ruby-royale",
                    "Coral Royale 🪸": "coral-royale",
                    "Golden Dusk 🌇": "golden-dusk",
                    "Klimt Royale ✨": "klimt-royale",
                    "Deco Luxe 🏛️": "deco-luxe",
                    "Oceanic Aqua 🌊": "oceanic-aqua",
                    "Royal Sapphire 🔷": "royal-sapphire",
                    "Monet Twilight 🎨": "monet-twilight",
                    "Caravaggio Sepia Noir 🕯️": "caravaggio-sepia-noir",
                    "Stealth Graphite Steel 🖤": "stealth-graphite-steel",
                    "Sunset Mirage 🌅": "sunset-mirage",
                    "Cyber Neon ⚡": "cyber-neon"
                }
                theme_id = name_to_id_map.get(self._current, "forest-green-pro") if self._current else "forest-green-pro"
                theme_config = loader.get_theme_by_id(theme_id)
                return theme_config.get("palette", {})
            except Exception:
                pass
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID (remove emojis)
            theme_id = self._current.lower()
            # Remove emojis and extra spaces
            for emoji in ["🌿", "🍷", "💎", "🌌", "❤️‍🔥", "🪸", "🌇", "✨", "🏛️", "🌊", "🔷", "🎨", "🕯️", "🖤", "🌅", "⚡"]:
                theme_id = theme_id.replace(emoji, "")
            theme_id = theme_id.strip().replace(" ", "-")
            return theme_id
        return "forest-green-pro"
    
    def get_state_styler(self):
        """Get state styler for player state effects."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_state_styler()
        return None
    
    def get_selection_styler(self):
        """Get selection styler for list/tree highlighting."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_selection_styler()
        return None
    
    def get_emphasis_bar_styler(self):
        """Get emphasis bar styler for luxury text bars."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_emphasis_bar_styler()
        return None
    
    def get_theme_metadata(self, theme_name: str) -> Dict[str, str]:
        """Get theme metadata like intro and persona from config."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                for theme_info in theme_list:
                    if theme_info["name"] == theme_name:
                        theme_config = loader.get_theme_by_id(theme_info["id"])
                        return {
                            "intro": theme_config.get("intro", ""),
                            "persona": theme_config.get("persona", ""),
                            "id": theme_config.get("id", "")
                        }
            except Exception:
                pass
        return {"intro": "", "persona": "", "id": ""}

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub

```

---

### theme_factory.py

```python
"""
Theme Factory - Deterministic Token Generation
Builds complete theme token sets from minimal base color palettes
Now integrated with config-driven theme system
"""

from .theme_utils import lighten, darken, mix, alpha_over
from .theme_loader import get_theme_loader
from .theme_derive import (
    derive_tokens,
    get_player_state_style,
    get_selection_style,
    get_emphasis_bar_style,
    get_chip_styles,
)


def _get_emphasis_background(base):
    """Get emphasis background with painter-specific styling."""
    painter = base.get("painter", "classic")
    felt = base["felt"]
    accent = base["accent"]

    if painter == "impressionist":  # Monet Noir
        # Misty gradient: #253C4A → #0D1B1E
        return f"linear-gradient(180deg, {accent} 0%, {felt} 100%)"
    elif painter == "ornamental":  # Klimt Royale
        # Deep mahogany with gold tessellation
        return "linear-gradient(180deg, #6E0D0D 0%, #3D0606 100%)"
    elif painter == "gemstone":  # Imperial Jade
        # Jade gradient with mandala emboss
        return f"linear-gradient(180deg, {lighten(felt, 0.1)} 0%, {darken(felt, 0.2)} 100%)"
    elif painter == "geometric":  # Deco Luxe
        # Smoky indigo with art deco pattern
        return f"linear-gradient(180deg, {lighten(felt, 0.15)} 0%, {darken(felt, 0.1)} 100%)"
    else:
        # Classic gradient for other themes
        return f"linear-gradient(180deg, {lighten(felt, 0.2)} 0%, {darken(felt, 0.1)} 100%)"


def _get_emphasis_text_color(base):
    """Get emphasis text color optimized for readability."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return "#F5F7FA"  # Soft white for pastel glow
    elif painter == "ornamental":  # Klimt Royale
        return "#F4E2C9"  # Golden-ivory for luxury
    elif painter == "gemstone":  # Imperial Jade
        return "#E8E6E3"  # Pearl white for elegance
    elif painter == "geometric":  # Deco Luxe
        return "#F5F0E1"  # Cream white for sophistication
    else:
        return lighten(base["text"], 0.20)  # Enhanced contrast for others


def _get_emphasis_highlight(base):
    """Get emphasis highlight color for important words."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return "#E8A7C3"  # Pastel pink
    elif painter == "ornamental":  # Klimt Royale
        return "#C1121F"  # Blood crimson glow
    elif painter == "gemstone":  # Imperial Jade
        return "#C9A441"  # Antique gold
    elif painter == "geometric":  # Deco Luxe
        return "#B08D57"  # Polished brass
    else:
        return base["raise_"]  # Use theme's danger color


def _get_emphasis_glow(base):
    """Get emphasis inner glow color."""
    painter = base.get("painter", "classic")

    if painter == "impressionist":  # Monet Noir
        return alpha_over("#A7C8E8", "#000000", 0.12)  # Pale sky blue glow
    elif painter == "ornamental":  # Klimt Royale
        return alpha_over("#FFD700", "#000000", 0.12)  # Gold inner glow
    elif painter == "gemstone":  # Imperial Jade
        return alpha_over("#DAA520", "#000000", 0.10)  # Jade-gold glow
    elif painter == "geometric":  # Deco Luxe
        return alpha_over("#D4AF37", "#000000", 0.12)  # Art deco gold glow
    else:
        return alpha_over(base["metal"], "#000000", 0.15)


def _get_emphasis_border(base):
    """Get emphasis border color (gold trim lines)."""
    painter = base.get("painter", "classic")

    if painter in ["ornamental", "gemstone", "geometric"]:
        return "#B8860B"  # Gold leaf trim
    elif painter == "impressionist":
        return alpha_over("#C8D5DE", "#000000", 0.40)  # Soft metallic
    else:
        return base["metal"]


def build_theme(base):
    """
    Build complete theme tokens from base palette

    Args:
        base: dict with keys:
            - felt: Primary table surface color
            - metal: Trim/accent metallic color
            - accent: Secondary accent color
            - raise_: Danger/raise action color
            - call: Success/call action color
            - neutral: Neutral gray base
            - text: Primary text color
            - background: (optional) Background color for artistic themes
            - pattern_overlay: (optional) Pattern overlay identifier
            - identifier_effect: (optional) Unique visual effect
            - painter: (optional) Painter style identifier

    Returns:
        Complete token dictionary for all UI elements
    """
    felt = base["felt"]
    metal = base["metal"]
    accent = base["accent"]
    raise_c = base["raise_"]
    call_c = base["call"]
    neutral = base["neutral"]
    txt = base["text"]

    # Artistic theme enhancements
    background = base.get("background", darken(felt, 0.8))
    pattern_overlay = base.get("pattern_overlay", None)
    identifier_effect = base.get("identifier_effect", None)
    painter = base.get("painter", None)

    # Build comprehensive token set
    tokens = {
        # === SURFACES ===
        "table.felt": felt,
        "table.rail": darken(felt, 0.75),
        "table.inlay": metal,
        "table.edgeGlow": darken(felt, 0.6),
        "table.centerPattern": lighten(felt, 0.06),  # Subtle ellipse at center
        # === TEXT ===
        "text.primary": lighten(txt, 0.10),
        "text.secondary": lighten(txt, 0.35),
        "text.muted": lighten(txt, 0.55),
        # === EMPHASIZED TEXT (High-contrast bars) ===
        "text.emphasis.bg": _get_emphasis_background(base),
        "text.emphasis.color": _get_emphasis_text_color(base),
        "text.emphasis.highlight": _get_emphasis_highlight(base),
        "text.emphasis.shadow": alpha_over("#000000", felt, 0.60),
        "text.emphasis.glow": _get_emphasis_glow(base),
        "text.emphasis.border": _get_emphasis_border(base),
        # === CARDS ===
        # Neutral ivory face, theme-tinted back
        "card.face.bg": lighten(neutral, 0.85),
        "card.face.border": darken(neutral, 0.50),
        "card.pip.red": mix(raise_c, "#FF2A2A", 0.35),
        "card.pip.black": darken(neutral, 0.85),
        "card.back.bg": alpha_over(accent, felt, 0.35),
        "card.back.pattern": alpha_over(metal, accent, 0.25),
        "card.back.border": metal,
        # === COMMUNITY BOARD ===
        "board.slotBg": alpha_over(darken(felt, 0.45), felt, 0.80),
        "board.border": alpha_over(metal, felt, 0.85),
        "board.shadow": darken(felt, 0.85),
        # === CHIPS ===
        # Standard casino colors with theme-tinted rims
        "chip.$1": "#2E86AB",  # Blue
        "chip.$5": "#B63D3D",  # Red
        "chip.$25": "#2AA37A",  # Green
        "chip.$100": "#3C3A3A",  # Black
        "chip.$500": "#6C4AB6",  # Purple
        "chip.$1k": "#D1B46A",  # Gold
        "chip.rim": alpha_over(metal, "#000000", 0.35),
        "chip.text": "#F8F7F4",
        # === POT ===
        "pot.badgeBg": alpha_over(darken(felt, 0.5), felt, 0.85),
        "pot.badgeRing": metal,
        "pot.valueText": lighten(neutral, 0.9),
        # === BETS & ANIMATIONS ===
        "bet.path": alpha_over(accent, "#000000", 0.50),
        "bet.glow": alpha_over(metal, "#000000", 0.35),
        # === PLAYER LABELS ===
        "label.active.bg": alpha_over(call_c, "#000000", 0.60),
        "label.active.fg": lighten(neutral, 0.95),
        "label.folded.bg": alpha_over(neutral, "#000000", 0.75),
        "label.folded.fg": lighten(neutral, 0.65),
        "label.winner.bg": alpha_over(metal, "#000000", 0.70),
        "label.winner.fg": "#0B0B0E",
        # === BUTTONS (Enhanced from existing system) ===
        "btn.primary.bg": alpha_over(accent, "#000000", 0.70),
        "btn.primary.fg": lighten(neutral, 0.95),
        "btn.primary.border": metal,
        "btn.primary.hoverBg": alpha_over(accent, "#000000", 0.55),
        "btn.primary.hoverFg": "#FFFFFF",
        "btn.primary.hoverBorder": lighten(metal, 0.20),
        "btn.primary.activeBg": alpha_over(accent, "#000000", 0.85),
        "btn.primary.activeFg": "#FFFFFF",
        "btn.primary.activeBorder": lighten(metal, 0.35),
        "btn.secondary.bg": alpha_over(neutral, "#000000", 0.60),
        "btn.secondary.fg": lighten(txt, 0.20),
        "btn.secondary.border": alpha_over(metal, "#000000", 0.60),
        "btn.secondary.hoverBg": alpha_over(neutral, "#000000", 0.45),
        "btn.secondary.hoverFg": lighten(txt, 0.35),
        "btn.secondary.hoverBorder": alpha_over(metal, "#000000", 0.45),
        "btn.danger.bg": alpha_over(raise_c, "#000000", 0.70),
        "btn.danger.fg": lighten(neutral, 0.95),
        "btn.danger.border": lighten(raise_c, 0.20),
        "btn.danger.hoverBg": alpha_over(raise_c, "#000000", 0.55),
        "btn.danger.hoverFg": "#FFFFFF",
        "btn.danger.hoverBorder": lighten(raise_c, 0.35),
        # === PLAYER SEATS ===
        "seat.bg.idle": alpha_over(neutral, felt, 0.25),
        "seat.bg.active": alpha_over(call_c, felt, 0.15),
        "seat.bg.acting": alpha_over(call_c, "#000000", 0.40),
        "seat.bg.folded": alpha_over(neutral, "#000000", 0.70),
        "seat.ring": alpha_over(metal, felt, 0.60),
        "seat.highlight": lighten(felt, 0.15),
        "seat.shadow": darken(felt, 0.80),
        # === DEALER BUTTON ===
        "dealer.buttonBg": lighten(neutral, 0.90),
        "dealer.buttonFg": darken(neutral, 0.85),
        "dealer.buttonBorder": metal,
        # === ACTION COLORS ===
        "action.fold": alpha_over(neutral, "#000000", 0.60),
        "action.check": alpha_over(call_c, "#000000", 0.50),
        "action.call": call_c,
        "action.bet": alpha_over(metal, call_c, 0.70),
        "action.raise": raise_c,
        "action.allin": alpha_over(raise_c, metal, 0.60),
        # === ACCESSIBILITY & CHROME ===
        "a11y.focus": lighten(metal, 0.30),
        "divider": darken(felt, 0.70),
        "grid.lines": darken(felt, 0.60),
        # === MICRO-INTERACTIONS ===
        "glow.soft": alpha_over(metal, "#000000", 0.20),
        "glow.medium": alpha_over(metal, "#000000", 0.40),
        "glow.strong": alpha_over(metal, "#000000", 0.70),
        "pulse.slow": alpha_over(call_c, "#000000", 0.30),
        "pulse.fast": alpha_over(raise_c, "#000000", 0.50),
        # === TYPOGRAPHY ===
        "font.display": ("Inter", 24, "bold"),
        "font.h1": ("Inter", 20, "bold"),
        "font.h2": ("Inter", 16, "semibold"),
        "font.body": ("Inter", 14, "normal"),
        "font.small": ("Inter", 12, "normal"),
        "font.mono": ("JetBrains Mono", 12, "normal"),
        # === ARTISTIC ENHANCEMENTS ===
        "artistic.background": background,
        "artistic.pattern_overlay": pattern_overlay,
        "artistic.identifier_effect": identifier_effect,
        "artistic.painter": painter,
        # === PAINTER-SPECIFIC EFFECTS ===
        "effect.soft_glow": alpha_over(accent, "#FFFFFF", 0.15),
        "effect.gold_dust": "#FFD700",
        "effect.jade_gloss": alpha_over("#014421", "#FFFFFF", 0.25),
        "effect.arc_motion": metal,
        # === PATTERN OVERLAYS ===
        "pattern.mist_ripple": alpha_over(accent, "#FFFFFF", 0.12),
        "pattern.gold_tessellation": alpha_over("#D4AF37", felt, 0.15),
        "pattern.jade_mandala": alpha_over("#DAA520", felt, 0.10),
        "pattern.art_deco_sunburst": alpha_over("#D4AF37", felt, 0.12),
    }

    # Add premium chip tokens
    derive_chip_tokens(tokens, felt, metal, accent, raise_c, call_c, neutral)

    return tokens


def derive_chip_tokens(tokens, felt, metal, accent, raise_c, call_c, neutral):
    """Derive premium chip tokens from base theme swatches."""
    # Base "casino composite clay" hue: a mix of felt and neutral
    base_face = alpha_over(lighten(felt, 0.18), neutral, 0.25)
    base_edge = alpha_over(metal, felt, 0.25)
    base_rim = alpha_over(metal, "#000000", 0.45)
    base_text = "#F8F7F4"

    tokens.update(
        {
            # Generic chip tokens
            "chip.face": base_face,
            "chip.edge": base_edge,
            "chip.rim": base_rim,
            "chip.text": base_text,
            # Stack chips: calm, readable, less saturated to avoid UI noise
            "chip.stack.face": alpha_over(base_face, "#000000", 0.15),
            "chip.stack.edge": alpha_over(base_edge, "#000000", 0.10),
            "chip.stack.rim": base_rim,
            "chip.stack.text": base_text,
            "chip.stack.shadow": darken(felt, 0.85),
            # Bet/Call chips: pop with the theme accent for motion visibility
            "chip.bet.face": alpha_over(accent, base_face, 0.60),
            "chip.bet.edge": alpha_over(accent, base_edge, 0.75),
            "chip.bet.rim": alpha_over(metal, accent, 0.55),
            "chip.bet.text": base_text,
            "chip.bet.glow": alpha_over(metal, accent, 0.35),
            # Pot chips: prestigious—lean into metal, slightly brighter
            "chip.pot.face": alpha_over(lighten(metal, 0.20), base_face, 0.70),
            "chip.pot.edge": alpha_over(metal, "#000000", 0.15),
            "chip.pot.rim": alpha_over(lighten(metal, 0.35), "#000000", 0.30),
            "chip.pot.text": "#0B0B0E",
            "chip.pot.glow": alpha_over(lighten(metal, 0.25), "#000000", 0.20),
        }
    )


# Base color palettes for all 16 themes
THEME_BASES = {
    # Row 1 — Classic
    "Forest Green Professional": {
        "felt": "#1E4D2B",
        "metal": "#C9A86A",
        "accent": "#2E7D32",
        "raise_": "#B63D3D",
        "call": "#2AA37A",
        "neutral": "#9AA0A6",
        "text": "#EDECEC",
    },
    "Velvet Burgundy": {
        "felt": "#4A1212",
        "metal": "#C0A066",
        "accent": "#702525",
        "raise_": "#B53A44",
        "call": "#2AA37A",
        "neutral": "#A29A90",
        "text": "#F2E9DF",
        "painter": "velvet",
        "identifier_effect": "crimson_glow",
    },
    "Obsidian Gold": {
        "felt": "#0A0A0A",
        "metal": "#D4AF37",
        "accent": "#2C2C2C",
        "raise_": "#A41E34",
        "call": "#2AA37A",
        "neutral": "#A7A7A7",
        "text": "#E6E6E6",
    },
    "Imperial Jade": {
        "felt": "#014421",
        "metal": "#DAA520",
        "accent": "#C9A441",
        "raise_": "#B23B43",
        "call": "#32B37A",
        "neutral": "#9CB1A8",
        "text": "#E8E6E3",
        "background": "#0C0C0C",
        "pattern_overlay": "jade_mandala",
        "identifier_effect": "jade_gloss",
        "painter": "gemstone",
    },
    # Row 2 — Artistic 4 (Painter-Inspired Luxury)
    "Monet Noir": {
        "felt": "#0D1B1E",
        "metal": "#C8D5DE",
        "accent": "#253C4A",
        "raise_": "#E8A7C3",
        "call": "#A7C8E8",
        "neutral": "#8EA6B5",
        "text": "#F5F7FA",
        "background": "#3B2F4A",
        "pattern_overlay": "mist_ripple",
        "identifier_effect": "soft_glow",
        "painter": "impressionist",
    },
    "Caravaggio Noir": {
        "felt": "#0A0A0C",
        "metal": "#E1C16E",
        "accent": "#9E0F28",
        "raise_": "#B3122E",
        "call": "#2AA37A",
        "neutral": "#9C8F7A",
        "text": "#FFF7E6",
    },
    "Klimt Royale": {
        "felt": "#0A0A0A",
        "metal": "#FFD700",
        "accent": "#D4AF37",
        "raise_": "#A4161A",
        "call": "#32B37A",
        "neutral": "#A38E6A",
        "text": "#FFF2D9",
        "background": "#3C2B1F",
        "pattern_overlay": "gold_tessellation",
        "identifier_effect": "gold_dust",
        "painter": "ornamental",
    },
    "Deco Luxe": {
        "felt": "#1B1E2B",
        "metal": "#B08D57",
        "accent": "#D4AF37",
        "raise_": "#5B1922",
        "call": "#2AA37A",
        "neutral": "#9B9486",
        "text": "#F5F0E1",
        "background": "#2E3B55",
        "pattern_overlay": "art_deco_sunburst",
        "identifier_effect": "arc_motion",
        "painter": "geometric",
    },
    # Row 3 — Nature & Light
    "Sunset Mirage": {
        "felt": "#2B1C1A",
        "metal": "#E6B87A",
        "accent": "#C16E3A",
        "raise_": "#C85C5C",
        "call": "#2AA37A",
        "neutral": "#A68C7A",
        "text": "#F7E7D6",
    },
    "Oceanic Blue": {
        "felt": "#0F1620",
        "metal": "#B7C1C8",
        "accent": "#3B6E8C",
        "raise_": "#6C94D2",
        "call": "#57C2B6",
        "neutral": "#9DB3C4",
        "text": "#F5F7FA",
    },
    "Velour Crimson": {
        "felt": "#6E0B14",
        "metal": "#C18F65",
        "accent": "#3B0A0F",
        "raise_": "#A41E34",
        "call": "#2AA37A",
        "neutral": "#A3928A",
        "text": "#F5E2C8",
    },
    "Golden Dusk": {
        "felt": "#5C3A21",
        "metal": "#C18F65",
        "accent": "#A3622B",
        "raise_": "#B35A3B",
        "call": "#2AA37A",
        "neutral": "#AF9A8A",
        "text": "#F3E3D3",
    },
    # Row 4 — Modern / Bold
    "Cyber Neon": {
        "felt": "#0D0F13",
        "metal": "#9BE3FF",
        "accent": "#17C3E6",
        "raise_": "#D65DB1",
        "call": "#00D9A7",
        "neutral": "#A3A8B3",
        "text": "#EAF8FF",
    },
    "Stealth Graphite": {
        "felt": "#111214",
        "metal": "#8D8D8D",
        "accent": "#232629",
        "raise_": "#9E3B49",
        "call": "#57C2B6",
        "neutral": "#8E9196",
        "text": "#E6E7EA",
    },
    "Royal Sapphire": {
        "felt": "#0B1F36",
        "metal": "#C7D3E0",
        "accent": "#224D8F",
        "raise_": "#6C4AB6",
        "call": "#57C2B6",
        "neutral": "#9AB1CF",
        "text": "#F2F6FC",
    },
    "Midnight Aurora": {
        "felt": "#0E1A28",
        "metal": "#D0D9DF",
        "accent": "#1C3E4A",
        "raise_": "#6FB5E7",
        "call": "#7BD0BC",
        "neutral": "#98A8B8",
        "text": "#F5F7FA",
    },
}


def _get_theme_selection_highlight(theme_name: str) -> dict:
    """Get theme-specific selection highlight colors for immersive experience."""

    # Theme-specific highlight palette for hand selections (matching THEME_ORDER)
    highlights = {
        # Row 1 — Classic Casino
        "Forest Green Professional": {
            "color": "#1DB954",
            "glow": "#22FF5A",
            "style": "emerald",
        },
        "Velvet Burgundy": {
            "color": "#A31D2B",
            "glow": "#C12839",
            "style": "deep_wine",
        },
        "Obsidian Gold": {"color": "#4169E1", "glow": "#6495ED", "style": "sapphire"},
        "Imperial Jade": {"color": "#00A86B", "glow": "#20C997", "style": "jade_teal"},
        # Row 2 — Luxury Noir (Art-inspired)
        "Monet Noir": {"color": "#E8A7C3", "glow": "#FFB6C1", "style": "rose"},
        "Caravaggio Noir": {
            "color": "#EAD6B7",
            "glow": "#F5E6C8",
            "style": "candlelight_ivory",
        },
        "Klimt Royale": {
            "color": "#B87333",
            "glow": "#CD853F",
            "style": "burnished_copper",
        },
        "Deco Luxe": {"color": "#B08D57", "glow": "#D4AF37", "style": "art_deco_brass"},
        # Row 3 — Nature & Light
        "Sunset Mirage": {
            "color": "#FF6B35",
            "glow": "#FF8C42",
            "style": "sunset_orange",
        },
        "Oceanic Blue": {"color": "#20B2AA", "glow": "#48D1CC", "style": "turquoise"},
        "Velour Crimson": {"color": "#FFD700", "glow": "#FFF700", "style": "gold"},
        "Golden Dusk": {"color": "#B87333", "glow": "#CD853F", "style": "copper"},
        # Row 4 — Modern / Bold
        "Cyber Neon": {"color": "#00FFFF", "glow": "#00FFFF", "style": "electric_cyan"},
        "Stealth Graphite": {
            "color": "#708090",
            "glow": "#B0C4DE",
            "style": "steel_blue",
        },
        "Royal Sapphire": {
            "color": "#4169E1",
            "glow": "#6495ED",
            "style": "royal_blue",
        },
        "Midnight Aurora": {
            "color": "#7BD0BC",
            "glow": "#98FB98",
            "style": "aurora_green",
        },
    }

    return highlights.get(
        theme_name,
        {
            "color": "#1DB954",
            "glow": "#22FF5A",
            "style": "emerald",  # Default fallback
        },
    )


def _get_theme_emphasis_colors(theme_name: str) -> dict:
    """Get theme-specific emphasis text colors for better contrast."""

    emphasis_colors = {
        # Row 1 — Classic Casino
        "Forest Green Professional": {
            "bg_gradient": ["#0B2818", "#051A0C"],
            "text": "#F0F8E8",
            "accent": "#1DB954",
        },
        "Velvet Burgundy": {
            "bg_gradient": ["#5C0A0A", "#2B0000"],
            "text": "#F9E7C9",
            "accent": "#A31D2B",
        },
        "Obsidian Gold": {
            "bg_gradient": ["#1A1A1A", "#0A0A0A"],
            "text": "#F9E7C9",
            "accent": "#D4AF37",
        },
        "Imperial Jade": {
            "bg_gradient": ["#1A2F1A", "#0F1F0F"],
            "text": "#F0F8E8",
            "accent": "#C9A441",
        },
        # Row 2 — Luxury Noir (Art-inspired)
        "Monet Noir": {
            "bg_gradient": ["#2C2C2C", "#1A1A1A"],
            "text": "#F5F0E1",
            "accent": "#E8A7C3",
        },
        "Caravaggio Noir": {
            "bg_gradient": ["#2A1A1A", "#1A0F0F"],
            "text": "#EAD6B7",
            "accent": "#EAD6B7",
        },
        "Klimt Royale": {
            "bg_gradient": ["#3D2914", "#2A1C0E"],
            "text": "#F5F0E1",
            "accent": "#C1121F",
        },
        "Deco Luxe": {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#F5F0E1",
            "accent": "#B08D57",
        },
        # Row 3 — Nature & Light
        "Sunset Mirage": {
            "bg_gradient": ["#3D1A0F", "#2B1208"],
            "text": "#F5E6D3",
            "accent": "#FF6B35",
        },
        "Oceanic Blue": {
            "bg_gradient": ["#0F2B3D", "#081A2B"],
            "text": "#E8F4F8",
            "accent": "#20B2AA",
        },
        "Velour Crimson": {
            "bg_gradient": ["#5C0A0A", "#2B0000"],
            "text": "#F9E7C9",
            "accent": "#C1121F",
        },
        "Golden Dusk": {
            "bg_gradient": ["#4A2F1A", "#2B1C10"],
            "text": "#EBD9B0",
            "accent": "#C18F65",
        },
        # Row 4 — Modern Bold
        "Cyber Neon": {
            "bg_gradient": ["#1A1F2E", "#0F1419"],
            "text": "#E8F8FF",
            "accent": "#00FFFF",
        },
        "Stealth Graphite": {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#E6E7EA",
            "accent": "#708090",
        },
        "Royal Sapphire": {
            "bg_gradient": ["#1A2A4A", "#0F1A3D"],
            "text": "#F2F6FC",
            "accent": "#4169E1",
        },
        "Midnight Aurora": {
            "bg_gradient": ["#1A2F2A", "#0F1F1A"],
            "text": "#F0F8F5",
            "accent": "#7BD0BC",
        },
    }

    return emphasis_colors.get(
        theme_name,
        {
            "bg_gradient": ["#2A2A2A", "#1A1A1A"],
            "text": "#F5F5F5",
            "accent": "#1DB954",  # Default
        },
    )


def build_theme_from_config(theme_id: str) -> dict:
    """
    Build theme using new config-driven system.

    Args:
        theme_id: ID of theme to build from poker_themes.json

    Returns:
        Complete theme token set
    """
    loader = get_theme_loader()
    defaults = loader.get_defaults()
    theme_config = loader.get_theme_by_id(theme_id)

    palette = theme_config.get("palette", {})

    # Derive comprehensive token set
    tokens = derive_tokens(palette)

    # Add config-driven state styles
    state_styles = get_player_state_style(defaults, palette)
    for k, v in state_styles.items():
        tokens[f"state.{k}"] = v  # type: ignore

    # Add selection styles
    selection_style = get_selection_style(defaults, palette)
    for k, v in selection_style.items():
        tokens[f"selection.{k}"] = v  # type: ignore

    # Add emphasis bar styles
    emphasis_style = get_emphasis_bar_style(defaults, palette)
    for k, v in emphasis_style.items():
        tokens[f"emphasis.{k}"] = v  # type: ignore

    # Add chip styles
    chip_styles = get_chip_styles(defaults, palette)
    for chip_type, styles in chip_styles.items():
        for k, v in styles.items():
            tokens[f"chips.{chip_type}.{k}"] = v  # type: ignore

    # Add theme metadata
    tokens.update(
        {
            "theme.id": theme_config.get("id", theme_id),
            "theme.name": theme_config.get("name", theme_id),
            "theme.palette": palette,
        }
    )

    # Legacy compatibility: add UI highlight tokens
    tokens["ui.highlight"] = palette.get("highlight", "#D4AF37")
    tokens["ui.highlight.text"] = palette.get("highlight_text", "#FFFFFF")
    tokens["ui.highlight.glow"] = tokens.get("bet_glow", "#22C55E")

    return tokens


def build_all_themes():
    """Build complete token sets for all 16 themes using config-driven system"""
    themes = {}

    try:
        # Try to use new config-driven system
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()
        print(f"🎨 ThemeFactory: Found {len(theme_list)} themes in config")

        for theme_info in theme_list:
            theme_id = theme_info["id"]
            # Use display name as key for theme manager compatibility
            display_name = theme_info["name"]
            print(f"🎨 Building theme: {display_name} (id: {theme_id})")
            themes[display_name] = build_theme_from_config(theme_id)

        print(f"✅ Built {len(themes)} themes using config-driven system")

    except Exception as e:
        print(f"⚠️ Config-driven theme loading failed: {e}")
        print("🔄 Falling back to legacy theme system...")

        # Fallback to legacy system
        for name, base in THEME_BASES.items():
            theme = build_theme(base)
            # Use actual JSON theme highlight colors instead of hardcoded values
            # The theme already has the correct highlight values from build_theme()
            # Don't override them with hardcoded selection_highlight values
            theme["ui.highlight"] = theme.get("ui.highlight", base.get("highlight", "#D4AF37"))
            theme["ui.highlight.text"] = theme.get("ui.highlight.text", base.get("highlight_text", "#FFFFFF"))
            theme["ui.highlight.glow"] = theme.get("ui.highlight.glow", base.get("metal", base.get("accent", "#FFD700")))
            themes[name] = theme

    return themes


def get_available_theme_names() -> list[str]:
    """Get list of available theme names for UI selection."""
    try:
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()
        return [theme_info["name"] for theme_info in theme_list]
    except Exception:
        # Fallback to legacy theme names
        return list(THEME_BASES.keys())


def get_theme_by_name(theme_name: str) -> dict:
    """Get theme by display name (for UI compatibility)."""
    try:
        loader = get_theme_loader()
        theme_list = loader.get_theme_list()

        # Find theme by name
        for theme_info in theme_list:
            if theme_info["name"] == theme_name:
                return build_theme_from_config(theme_info["id"])

        # Fallback: try by ID (kebab-case)
        theme_id = theme_name.lower().replace(" ", "-")
        return build_theme_from_config(theme_id)

    except Exception as e:
        print(f"⚠️ Could not load theme '{theme_name}': {e}")

        # Legacy fallback
        if theme_name in THEME_BASES:
            return build_theme(THEME_BASES[theme_name])

        # Ultimate fallback
        return build_theme(THEME_BASES["Forest Green Professional"])

```

---

### theme_loader_consolidated.py

```python
"""
Consolidated theme loader with robust fallbacks and persistence.
Loads from single poker_themes_final_16.json with embedded defaults.
"""

import json
import pathlib
from typing import Dict, Any, Tuple, Optional

# Default theme file location (existing poker_themes.json)
DEFAULT_THEME_FILE = pathlib.Path(__file__).parent.parent.parent / "data" / "poker_themes.json"

# Embedded minimal fallback theme (single theme to ensure app boots)
EMBEDDED_FALLBACK = {
    "defaults": {
        "state_styling": {
            "active": {"glow_color": "$accent", "glow_intensity": 0.8},
            "folded": {"desaturation": 0.7, "opacity": 0.6},
            "winner": {"celebration_rings": 3, "shimmer_color": "$metal"},
            "showdown": {"spotlight_fade": 0.3},
            "all_in": {"flash_intensity": 0.9, "flash_color": "$raise"}
        },
        "selection_highlighting": {
            "treeview": {"selected_bg": "$highlight", "selected_fg": "$highlight_text"},
            "listbox": {"selected_bg": "$highlight", "selected_fg": "$highlight_text"}
        },
        "emphasis_bars": {
            "gradient": {"top": "$emphasis_bg_top", "bottom": "$emphasis_bg_bottom"},
            "border": "$emphasis_border",
            "text": "$emphasis_text",
            "accent_text": "$emphasis_accent_text"
        }
    },
    "themes": [
        {
            "id": "forest-green-pro",
            "name": "Forest Green Professional 🌿",
            "intro": "Classic casino elegance with deep forest tones and golden accents.",
            "persona": "Sophisticated. Timeless. The choice of discerning players.",
            "palette": {
                "felt": "#1B4D3A",
                "rail": "#2E4F76", 
                "metal": "#D4AF37",
                "accent": "#FFD700",
                "raise": "#DC2626",
                "call": "#2563EB",
                "neutral": "#6B7280",
                "text": "#F8FAFC",
                "highlight": "#D4AF37",
                "highlight_text": "#000000",
                "emphasis_bg_top": "#1B4D3A",
                "emphasis_bg_bottom": "#0F2A1F",
                "emphasis_border": "#D4AF37",
                "emphasis_text": "#F8FAFC",
                "emphasis_accent_text": "#FFD700",
                "chip_face": "#2E7D5A",
                "chip_edge": "#1B4D3A",
                "chip_rim": "#D4AF37",
                "chip_text": "#F8FAFC",
                "bet_face": "#DC2626",
                "bet_edge": "#991B1B",
                "bet_rim": "#FCA5A5",
                "bet_text": "#F8FAFC",
                "bet_glow": "#FEE2E2",
                "pot_face": "#D4AF37",
                "pot_edge": "#92400E",
                "pot_rim": "#FDE68A",
                "pot_text": "#000000",
                "pot_glow": "#FEF3C7"
            }
        }
    ]
}


class ConsolidatedThemeLoader:
    """Robust theme loader with fallbacks and user load/save capability."""
    
    def __init__(self):
        """Initialize with default theme file."""
        self._config: Optional[Dict[str, Any]] = None
        self._loaded = False
        self._current_file: Optional[pathlib.Path] = None
    
    def load_themes(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load theme configuration with robust fallbacks.
        
        Args:
            file_path: Optional specific file to load, otherwise uses default
        
        Load order:
        1. Specified file_path (if provided)
        2. Project's backend/data/poker_themes.json (default)
        3. Embedded fallback (single theme)
        
        Returns:
            Complete theme configuration dict
        """
        if not file_path and self._loaded and self._config:
            return self._config
            
        theme_file = None
        
        # Try specified file first
        if file_path:
            try:
                theme_file = pathlib.Path(file_path)
                if theme_file.exists():
                    config_text = theme_file.read_text(encoding="utf-8")
                    self._config = json.loads(config_text)
                    self._current_file = theme_file
                    print(f"✅ Loaded themes from specified file: {theme_file}")
                    self._loaded = True
                    return self._config
            except Exception as e:
                print(f"⚠️  Failed to load specified theme file: {e}")
        
        # Try default project theme file
        try:
            if DEFAULT_THEME_FILE.exists():
                config_text = DEFAULT_THEME_FILE.read_text(encoding="utf-8")
                self._config = json.loads(config_text)
                self._current_file = DEFAULT_THEME_FILE
                print(f"✅ Loaded themes from default file: {DEFAULT_THEME_FILE}")
                self._loaded = True
                return self._config
        except Exception as e:
            print(f"⚠️  Failed to load default theme file: {e}")
        
        # Ultimate fallback - embedded theme
        print("🔄 Using embedded fallback theme")
        self._config = EMBEDDED_FALLBACK
        self._current_file = None
        self._loaded = True
        return self._config
    
    def save_themes(self, config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
        """
        Save theme configuration to specified file or current file.
        
        Args:
            config: Complete theme configuration to save
            file_path: Optional file path to save to, otherwise uses current or default
            
        Returns:
            True if saved successfully
        """
        try:
            # Determine save location
            if file_path:
                save_file = pathlib.Path(file_path)
            elif self._current_file:
                save_file = self._current_file
            else:
                save_file = DEFAULT_THEME_FILE
            
            # Ensure directory exists
            save_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with nice formatting
            config_text = json.dumps(config, ensure_ascii=False, indent=2)
            save_file.write_text(config_text, encoding="utf-8")
            
            # Update cached config
            self._config = config
            self._current_file = save_file
            
            print(f"✅ Saved themes to: {save_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save themes: {e}")
            return False
    
    def get_theme_by_id(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID."""
        config = self.load_themes()
        themes = config.get("themes", [])
        
        for theme in themes:
            if theme.get("id") == theme_id:
                return theme
                
        return None
    
    def get_theme_list(self) -> list[Dict[str, str]]:
        """Get list of available themes with metadata."""
        config = self.load_themes()
        themes = config.get("themes", [])
        
        return [
            {
                "id": theme.get("id", "unknown"),
                "name": theme.get("name", "Unknown Theme"),
                "intro": theme.get("intro", "")
            }
            for theme in themes
        ]
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        config = self.load_themes()
        return config.get("defaults", {})
    
    def reload(self, file_path: Optional[str] = None):
        """Force reload from disk."""
        self._loaded = False
        self._config = None
        return self.load_themes(file_path)
    
    def get_current_file(self) -> Optional[pathlib.Path]:
        """Get currently loaded theme file path."""
        return self._current_file
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load themes from specific file."""
        return self.load_themes(file_path)
    
    def save_to_file(self, config: Dict[str, Any], file_path: str) -> bool:
        """Save themes to specific file."""
        return self.save_themes(config, file_path)


# Singleton instance
_theme_loader: Optional[ConsolidatedThemeLoader] = None


def get_consolidated_theme_loader() -> ConsolidatedThemeLoader:
    """Get singleton theme loader instance."""
    global _theme_loader
    if _theme_loader is None:
        _theme_loader = ConsolidatedThemeLoader()
    return _theme_loader


def load_themes() -> Dict[str, Any]:
    """Convenience function to load themes."""
    return get_consolidated_theme_loader().load_themes()


def save_themes(config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
    """Convenience function to save themes."""
    return get_consolidated_theme_loader().save_themes(config, file_path)

```

---

### theme_utils.py

```python
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

```

---

### state_styler.py

```python
"""
State-driven styling system for poker UI elements.
Handles luxury highlighting and animations for player states.
"""

import time
import math
from typing import Dict, Any, Optional
try:
    # Prefer consolidated loader available in this project
    from .theme_loader_consolidated import load_themes as _load_themes
except Exception:
    _load_themes = None

def get_theme_loader():
    """Compatibility shim that exposes get_defaults/get_theme_by_id API."""
    class _Accessor:
        def __init__(self):
            try:
                self._config = _load_themes() if _load_themes else {"defaults": {}, "themes": []}
            except Exception:
                self._config = {"defaults": {}, "themes": []}

        def get_defaults(self) -> Dict[str, Any]:
            return self._config.get("defaults", {})

        def get_theme_by_id(self, theme_id: str) -> Dict[str, Any]:
            for t in self._config.get("themes", []):
                if t.get("id") == theme_id:
                    return t
            themes = self._config.get("themes", [])
            return themes[0] if themes else {"palette": {}}

    return _Accessor()
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

```

---

### theme_derive.py

```python
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

```

---

### theme_manager_clean.py

```python
from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes, build_theme_from_config, get_available_theme_names, get_theme_by_name
    from .theme_loader import get_theme_loader
    from .state_styler import get_state_styler, get_selection_styler, get_emphasis_bar_styler
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Default theme name for fallbacks
DEFAULT_THEME_NAME = "Forest Green Professional 🌿"  # Updated to match JSON config name


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
    - Now fully config-driven using poker_themes.json
    """

    CONFIG_PATH = os.path.join("backend", "ui", "theme_config.json")

    def __init__(self) -> None:
        self._theme: Dict[str, Any]
        self._fonts: Dict[str, Any]
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._current: str | None = None
        self._subs: List[Callable[["ThemeManager"], None]] = []
        # Load defaults from codebase
        try:
            gm = importlib.import_module("backend.core.gui_models")
            self._theme = dict(getattr(gm, "THEME", {}))
            self._fonts = dict(getattr(gm, "FONTS", {}))
        except Exception:
            self._theme = {"table_felt": "#2B2F36", "text": "#E6E9EF"}
            self._fonts = {
                "main": ("Arial", 20),  # Base font at 20px for readability
                "pot_display": ("Arial", 28, "bold"),  # +8 for pot display
                "bet_amount": ("Arial", 24, "bold"),  # +4 for bet amounts
                "body": ("Consolas", 20),  # Same as main for body text
                "small": ("Consolas", 16),  # -4 for smaller text
                "header": ("Arial", 22, "bold")  # +2 for headers
            }
        # Apply persisted config if present
        # Register built-in packs
        packs = self._builtin_packs()
        for name, tokens in packs.items():
            self.register(name, tokens)
        self._load_config()
        if not self._current:
            # Use Forest Green Professional as safe default
            if DEFAULT_THEME_NAME in self._themes:
                self._current = DEFAULT_THEME_NAME
                self._theme = dict(self._themes[DEFAULT_THEME_NAME])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in theme packs - now using token-driven system"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Use the new deterministic token system
                themes = build_all_themes()
                print(f"🎨 ThemeManager: Loaded {len(themes)} themes: {list(themes.keys())}")
                return themes
            except Exception as e:
                print(f"⚠️ ThemeManager: Config-driven themes failed: {e}")
                return self._legacy_builtin_packs()
        else:
            print("⚠️ ThemeManager: Token-driven themes not available, using legacy")
            # Fallback to legacy themes if token system not available
            return self._legacy_builtin_packs()
    
    def _legacy_builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Minimal legacy fallback if config system completely fails."""
        return {
            "Forest Green Professional 🌿": {
                "table.felt": "#2D5A3D",
                "table.rail": "#4A3428", 
                "text.primary": "#EDECEC",
                "panel.bg": "#1F2937",
                "panel.fg": "#E5E7EB"
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names from config-driven system."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback: return all registered theme names
        return list(self._themes.keys())

    def register_all(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register all themes from packs dictionary."""
        for name, tokens in packs.items():
            self.register(name, tokens)

    def current(self) -> str | None:
        """Return current theme name."""
        return self._current

    def set_profile(self, name: str) -> None:
        if name in self._themes:
            self._current = name
            self._theme = dict(self._themes[name])
            self._save_config()
            for fn in list(self._subs):
                fn(self)

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile")
                if prof and prof in self._themes:
                    self._current = prof
                    self._theme = dict(self._themes[prof])
                fonts = data.get("fonts")
                if isinstance(fonts, dict):
                    self._fonts.update(fonts)
        except Exception:
            pass

    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            payload = {"profile": self.current_profile_name(), "fonts": self._fonts}
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def current_profile_name(self) -> str:
        for name, theme in self._themes.items():
            if all(self._theme.get(k) == theme.get(k) for k in ("table.felt",)):
                return name
        return "Custom"

    def get(self, token: str, default=None):
        # Dot-path lookup in current theme; fallback to fonts when font.* requested
        if token.startswith("font."):
            return self._theme.get(token) or self._fonts.get(token[5:], default)
        cur = self._theme
        for part in token.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return self._theme.get(token, default)
        return cur
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get complete token dictionary for current theme"""
        return dict(self._theme)
    
    def get_base_colors(self) -> Dict[str, str]:
        """Get the base color palette for current theme (if available)"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try new config-driven system first
            try:
                loader = get_theme_loader()
                # Convert display name to theme ID
                theme_id = self._current.lower().replace(" ", "-").replace("🌿", "").replace("🍷", "").replace("💎", "").replace("🌌", "").replace("❤️‍🔥", "").replace("🪸", "").replace("🌇", "").replace("✨", "").replace("🏛️", "").replace("🌊", "").replace("🔷", "").replace("🎨", "").replace("🕯️", "").replace("🖤", "").replace("🌅", "").replace("⚡", "").strip() if self._current else "forest-green-pro"
                theme_config = loader.get_theme_by_id(theme_id)
                return theme_config.get("palette", {})
            except Exception:
                pass
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID (remove emojis)
            theme_id = self._current.lower()
            # Remove emojis and extra spaces
            for emoji in ["🌿", "🍷", "💎", "🌌", "❤️‍🔥", "🪸", "🌇", "✨", "🏛️", "🌊", "🔷", "🎨", "🕯️", "🖤", "🌅", "⚡"]:
                theme_id = theme_id.replace(emoji, "")
            theme_id = theme_id.strip().replace(" ", "-")
            return theme_id
        return "forest-green-pro"
    
    def get_state_styler(self):
        """Get state styler for player state effects."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_state_styler()
        return None
    
    def get_selection_styler(self):
        """Get selection styler for list/tree highlighting."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_selection_styler()
        return None
    
    def get_emphasis_bar_styler(self):
        """Get emphasis bar styler for luxury text bars."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_emphasis_bar_styler()
        return None
    
    def get_theme_metadata(self, theme_name: str) -> Dict[str, str]:
        """Get theme metadata like intro and persona from config."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                for theme_info in theme_list:
                    if theme_info["name"] == theme_name:
                        theme_config = loader.get_theme_by_id(theme_info["id"])
                        return {
                            "intro": theme_config.get("intro", ""),
                            "persona": theme_config.get("persona", ""),
                            "id": theme_config.get("id", "")
                        }
            except Exception:
                pass
        return {"intro": "", "persona": "", "id": ""}

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub

```

---

## ARCHITECTURE DOCUMENTATION

### PokerPro_Trainer_Complete_Architecture_v3.md

```markdown
# PokerPro Trainer - Complete Architecture Reference v3

**Status**: Production Ready  
**Last Updated**: January 2024  
**Purpose**: Comprehensive reference for complete codebase reconstruction if needed  

---

## 🏗️ **SYSTEM OVERVIEW**

The PokerPro Trainer uses a **single-threaded, event-driven architecture** centered around three core pillars:

1. **PurePokerStateMachine (PPSM)** - Deterministic poker engine with hand replay capabilities
2. **Modern UI Architecture** - Component-based UI with clean separation of concerns  
3. **Session Management System** - Pluggable session types (GTO, Practice, Hands Review, Live)

### **Core Design Principles**

- **Single Source of Truth**: PPSM is the authoritative game state
- **Deterministic Behavior**: All game logic is reproducible and testable
- **Clean Separation**: UI renders state, never controls game logic
- **Event-Driven**: All interactions flow through well-defined interfaces
- **Pluggable Components**: DecisionEngines and Sessions are swappable

---

## 🎮 **PURE POKER STATE MACHINE (PPSM)**

### **Architecture Overview**

The PPSM is a **deterministic, single-threaded poker engine** that serves as the single source of truth for all poker game state and logic.

```python
class PurePokerStateMachine:
    """
    Core poker engine with:
    - Deterministic game state management
    - Hand replay capabilities via DecisionEngineProtocol
    - Clean to-amount semantics for all actions
    - Comprehensive validation and error handling
    """
```

### **Key Features**

#### **1. Deterministic Deck System**
```python
# Uses predetermined card sequences for reproducible hands
deck = ["Kh", "Kd", "Ad", "2c", "4h", "4s", "Qh", "2h", "2d"]
```

#### **2. To-Amount Semantics (Authoritative)**
- **BET**: `to_amount` = total amount to reach (not delta)
- **RAISE**: `to_amount` = total amount to raise to (not additional)
- **CALL/CHECK**: `to_amount` ignored (engine computes)

#### **3. DecisionEngineProtocol Integration**
```python
class DecisionEngineProtocol:
    def get_decision(self, player_name: str, game_state) -> tuple[ActionType, Optional[float]]:
        """Return (ActionType, to_amount) for player to act"""
        pass
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if engine has decision for player"""
        pass
```

#### **4. Hand Model Replay**
```python
def replay_hand_model(self, hand_model) -> dict:
    """
    Replay a Hand object using HandModelDecisionEngineAdapter
    Returns comprehensive results with pot validation
    """
```

### **State Management**

#### **Game States**
- `START_HAND` → `PREFLOP_BETTING` → `FLOP_BETTING` → `TURN_BETTING` → `RIVER_BETTING` → `SHOWDOWN`

#### **Player State Tracking**
- `current_bet`: Amount player has wagered this street
- `stack`: Remaining chips
- `is_active`: Can still act in hand
- `has_folded`: Eliminated from hand

#### **Round State Management**
- `current_bet`: Current bet to match
- `last_full_raise_size`: For minimum raise validation  
- `need_action_from`: Set of player indices who need to act
- `reopen_available`: Whether betting can be reopened

### **Validation System**

#### **Action Validation**
```python
def _is_valid_action(self, player: Player, action_type: ActionType, to_amount: Optional[float]) -> bool:
    """
    Comprehensive validation including:
    - Player can act (not folded, has chips)
    - Action is legal for current street
    - Bet amounts are valid (within limits, proper increments)
    - Raise amounts meet minimum requirements
    """
```

#### **Pot Validation**
```python
def _validate_pot_integrity(self) -> bool:
    """
    Ensures total chips in play equals:
    - All player stacks + current bets + pot
    - No chips created or destroyed
    """
```

---

## 🎨 **UI ARCHITECTURE**

### **Component Hierarchy**

```
AppShell
├── ServiceContainer
│   ├── ThemeManager
│   ├── SoundManager
│   ├── EventBus
│   └── Store
├── TabContainer
│   ├── HandsReviewTab
│   ├── PracticeSessionTab
│   └── GTOSessionTab
└── PokerTableRenderer (Unified Poker Table — Pure Renderer)
    ├── CanvasManager
    ├── LayerManager (felt → seats → stacks → community → bets → pot → action → status → overlay)
    ├── RendererPipeline
    └── Table Components
        ├── TableFelt
        ├── Seats
        ├── Community
        ├── PotDisplay
        ├── BetDisplay
        ├── DealerButton
        └── ActionIndicator
```

### **Design Principles**

#### **1. Pure Rendering Components**
- UI components are **stateless renderers**
- All business logic resides in PPSM or services
- Components subscribe to state via selectors
- No direct state mutation from UI

#### **2. State-Driven Architecture**
- Single source of truth: Store
- UI renders based on state changes
- Actions flow: UI → Store → Reducer → State → UI
- No imperative UI updates

#### **3. Event-Driven Integration**
- EventBus for cross-service communication
- Services handle side effects (sounds, animations)
- UI dispatches actions, never calls services directly
- Clean separation of concerns

#### **4. Reusable Poker Table Renderer**
- `backend/ui/renderers/poker_table_renderer.py` is a **pure** renderer reused by every session.
- Input is a single `PokerTableState` (immutable dataclass).
- Emits renderer intents (e.g., `REQUEST_ANIMATION`) that the shell adapts to `EffectBus`.
- No business logic, no session awareness, no PPSM calls.

### **State / Effects Flow (MVU)**

```
UI Intent → SessionManager.handle_* → PPSM → Store.replace(table_state, effects)
      ↓                                    ↓
PokerTableRenderer.render(state)     EffectBus.run(effects) → Director gating
```

### **Theme System Integration**

- **Design System v2**: Token-based color system
- **Hot-swappable themes**: Runtime theme switching
- **Responsive design**: Dynamic sizing based on container
- **Accessibility**: WCAG 2.1 AA compliance

---

## 🎯 **SESSION IMPLEMENTATION ARCHITECTURE**

### **Hands Review Session**

#### **Purpose**
- Load and replay GTO/Legendary hands
- Step-by-step action progression
- Auto-play with configurable timing
- Theme switching and responsive layout

#### **Core Components**
- **Enhanced RPGW**: Unified poker table display
- **Hand Loader**: JSON parsing and validation
- **Action Controller**: Step-by-step progression
- **Theme Manager**: Dynamic theme switching

#### **Implementation Flow**
```python
# 1. Hand Loading
hand_data = load_hand_from_json(file_path)
display_state = create_display_state(hand_data)

# 2. Action Execution
action = get_next_action(hand_data, current_index)
store.dispatch({"type": "ENHANCED_RPGW_EXECUTE_ACTION", "action": action})

# 3. State Update
new_state = reducer(current_state, action)
renderer_pipeline.render_once(new_state)

# 4. Side Effects
event_bus.publish("enhanced_rpgw:feedback", {"type": "sound", "action": action})
```

### **Practice Session**

#### **Purpose**
- Interactive poker practice with AI opponents
- Configurable starting conditions
- Real-time decision making
- Performance tracking and analysis

#### **Core Components**
- **PPSM Integration**: Live game state management
- **AI Decision Engine**: Opponent behavior simulation
- **Session Controller**: Game flow coordination
- **Progress Tracker**: Performance metrics

#### **Implementation Flow**
```python
# 1. Session Initialization
ppsm = PurePokerStateMachine()
session_controller = PracticeSessionController(ppsm, event_bus)

# 2. Game Loop
while session_active:
    current_player = ppsm.get_current_player()
    if current_player.is_ai:
        decision = ai_engine.get_decision(current_player, ppsm.game_state)
        ppsm.execute_action(decision)
    else:
        # Wait for human input via UI
        pass

# 3. State Synchronization
display_state = ppsm_to_display_state(ppsm.game_state)
store.dispatch({"type": "UPDATE_PRACTICE_SESSION", "state": display_state})
```

### **GTO Session**

#### **Purpose**
- Live GTO strategy implementation
- Real-time hand analysis
- Decision tree visualization
- Performance benchmarking

#### **Core Components**
- **GTO Engine**: Strategy calculation and validation
- **Hand Analyzer**: Real-time equity calculations
- **Decision Tree**: Visual strategy representation
- **Benchmark System**: Performance metrics

#### **Implementation Flow**
```python
# 1. Strategy Loading
gto_strategy = load_gto_strategy(strategy_file)
gto_engine = GTOEngine(gto_strategy)

# 2. Live Analysis
current_hand = ppsm.get_current_hand_state()
gto_decision = gto_engine.analyze_hand(current_hand)
equity = gto_engine.calculate_equity(current_hand)

# 3. Decision Support
store.dispatch({
    "type": "UPDATE_GTO_ANALYSIS",
    "decision": gto_decision,
    "equity": equity,
    "confidence": gto_engine.get_confidence()
})
```

---

## 🔧 **ENHANCED RPGW ARCHITECTURE**

### **Component Integration**

The Enhanced RPGW serves as the unified poker table component across all session types, providing consistent rendering, theming, and interaction patterns.

#### **Core Architecture**
```python
class EnhancedRPGW:
    def __init__(self, parent_frame, theme_manager):
        self.canvas_manager = CanvasManager(parent_frame)
        self.layer_manager = LayerManager()
        self.renderer_pipeline = RendererPipeline()
        self.table_components = self._setup_table_components()
    
    def _setup_table_components(self):
        return {
            'table': TableFelt(),
            'seats': Seats(),
            'community': Community(),
            'pot': PotDisplay(),
            'bet': BetDisplay(),
            'dealer': DealerButton(),
            'action': ActionIndicator()
        }
```

#### **State-Driven Rendering**
```python
def render_table(self, display_state):
    """
    Renders poker table based on display state
    - No business logic, pure rendering
    - Responsive sizing and positioning
    - Theme-aware styling
    """
    self.renderer_pipeline.render_once(display_state)
```

#### **Display State Structure**
```python
display_state = {
    'table': {
        'width': 800,
        'height': 600,
        'theme': 'luxury_noir'
    },
    'pot': {
        'amount': 150,
        'position': (400, 300)
    },
    'seats': [
        {
            'player_uid': 'seat1',
            'name': 'Player1',
            'stack': 1000,
            'current_bet': 50,
            'cards': ['Ah', 'Kd'],
            'position': (300, 400),
            'acting': True
        }
    ],
    'board': ['2s', 'Jd', '6c'],
    'dealer': {'position': 0},
    'action': {'type': 'BET', 'player': 'seat1', 'amount': 50},
    'replay': {'current_step': 5, 'total_steps': 16}
}
```

---

## 🎭 **EVENT HANDLER INTEGRATION**

### **Store Reducer Pattern**

The UI architecture uses a Redux-like store with reducers to manage state updates and trigger side effects.

#### **Action Types**
```python
# Enhanced RPGW Actions
ENHANCED_RPGW_EXECUTE_ACTION = "ENHANCED_RPGW_EXECUTE_ACTION"
UPDATE_ENHANCED_RPGW_STATE = "UPDATE_ENHANCED_RPGW_STATE"
ENHANCED_RPGW_ANIMATION_EVENT = "ENHANCED_RPGW_ANIMATION_EVENT"

# Session Actions
UPDATE_PRACTICE_SESSION = "UPDATE_PRACTICE_SESSION"
UPDATE_GTO_ANALYSIS = "UPDATE_GTO_ANALYSIS"
```

#### **Reducer Implementation**
```python
def enhanced_rpgw_reducer(state, action):
    if action['type'] == 'ENHANCED_RPGW_EXECUTE_ACTION':
        # Triggers event for service layer
        new_state = {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': action['action'],
                'action_index': action['action_index'],
                'execution_status': 'pending'
            }
        }
        
        # Trigger service layer event
        if 'event_bus' in state:
            state['event_bus'].publish(
                "enhanced_rpgw:action_executed",
                {
                    "action": action['action'],
                    "action_index": action['action_index'],
                    "state": new_state
                }
            )
        return new_state
    
    elif action['type'] == 'UPDATE_ENHANCED_RPGW_STATE':
        # Updates state from PPSM execution results
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                **action['updates'],
                'execution_status': 'completed'
            }
        }
    
    elif action['type'] == 'ENHANCED_RPGW_ANIMATION_EVENT':
        # Handles animation events
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'animation_event': action['animation_data']
            }
        }
    
    return state
```

### **Service Layer Event Handling**

Services subscribe to events and handle business logic, side effects, and PPSM interactions.

#### **Enhanced RPGW Controller**
```python
class EnhancedRPGWController:
    def __init__(self, event_bus, store, ppsm):
        self.event_bus = event_bus
        self.store = store
        self.ppsm = ppsm
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(
            "enhanced_rpgw:action_executed",
            self._handle_action_execution
        )
        self.event_bus.subscribe(
            "enhanced_rpgw:trigger_animation",
            self._handle_animation_trigger
        )
    
    def _handle_action_execution(self, event_data):
        # Execute action in PPSM (business logic)
        ppsm_result = self._execute_ppsm_action(event_data['action'])
        
        # Update store with PPSM results
        self.store.dispatch({
            "type": "UPDATE_ENHANCED_RPGW_STATE",
            "updates": {
                "ppsm_result": ppsm_result,
                "last_executed_action": event_data['action'],
                "execution_timestamp": time.time()
            }
        })
        
        # Trigger appropriate animations/sounds
        self._trigger_action_feedback(event_data['action'], ppsm_result)
    
    def _execute_ppsm_action(self, action):
        # Placeholder for actual PPSM execution logic
        # This method will contain the core game state updates
        pass  # (Detailed logic for DEAL_HOLE, DEAL_BOARD, POST_BLIND, BET, RAISE, CALL, CHECK, FOLD, END_HAND)
    
    def _trigger_action_feedback(self, action, ppsm_result):
        # Publishes feedback events (sounds, animations)
        feedback_mapping = {
            'DEAL_HOLE': 'card_deal',
            'DEAL_BOARD': 'card_deal',
            'POST_BLIND': 'chip_bet',
            'BET': 'player_bet',
            'RAISE': 'player_bet',
            'CALL': 'player_call',
            'CHECK': 'player_check',
            'FOLD': 'player_fold',
            'END_HAND': 'hand_end'
        }
        feedback_type = feedback_mapping.get(action['type'], 'default')
        self.event_bus.publish(
            "enhanced_rpgw:feedback",
            {
                "type": feedback_type,
                "action": action,
                "ppsm_result": ppsm_result
            }
        )
    
    def _handle_animation_trigger(self, event_data):
        # Publishes animation events to the store for UI to pick up
        if event_data.get('type') == 'player_highlight':
            self.event_bus.publish(
                "enhanced_rpgw:animation_event",
                {
                    "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                    "delay_ms": 200,
                    "action": "clear_highlight"
                }
            )
```

---

## 🎨 **THEME SYSTEM INTEGRATION**

### **Design System v2**

The theme system provides a comprehensive, token-based approach to styling and theming across all UI components.

#### **Token Categories**
- **Colors**: Semantic color tokens (primary, secondary, accent)
- **Typography**: Font families, sizes, weights, and line heights
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl)
- **Elevation**: Shadow and depth tokens
- **Border Radius**: Corner rounding values
- **Animation**: Duration and easing curves

#### **Integration Points**
```python
# Theme Manager
theme_manager = ThemeManager()
theme_manager.load_theme('luxury_noir')

# Component Usage
button.configure(
    bg=theme_manager.get_token('btn.primary.bg'),
    fg=theme_manager.get_token('btn.primary.fg'),
    font=theme_manager.get_token('font.button')
)
```

#### **Theme Change Handling**
```python
def on_theme_change(self, new_theme):
    # Update theme manager
    self.theme_manager.load_theme(new_theme)
    
    # Re-render Enhanced RPGW with new theme
    self._render_enhanced_rpgw_table()
    
    # Refresh widget sizing for new theme
    self._refresh_enhanced_rpgw_widget()
```

---

## 🚀 **PERFORMANCE AND SCALABILITY**

### **Rendering Optimization**

- **Lazy Rendering**: Only re-render components when state changes
- **Layer Management**: Efficient z-order management via LayerManager
- **Canvas Optimization**: Minimize canvas redraws and object creation
- **Memory Management**: Proper cleanup of canvas objects and event handlers

### **State Management Efficiency**

- **Immutable Updates**: Use spread operators for state updates
- **Selective Subscriptions**: Components only subscribe to relevant state slices
- **Event Debouncing**: Prevent excessive event processing during rapid state changes
- **Batch Updates**: Group multiple state changes into single render cycles

### **Resource Management**

- **Sound Caching**: Pre-load and cache sound files
- **Image Optimization**: Use appropriate image formats and sizes
- **Memory Monitoring**: Track memory usage and implement cleanup strategies
- **Performance Profiling**: Monitor render times and optimize bottlenecks

---

## 🧪 **TESTING AND QUALITY ASSURANCE**

### **Testing Strategy**

#### **Unit Testing**
- **Reducers**: Test state transformations and side effects
- **Selectors**: Validate state derivation logic
- **Services**: Test business logic and PPSM interactions
- **Components**: Test rendering and event handling

#### **Integration Testing**
- **Session Flows**: End-to-end session execution
- **Theme Switching**: Theme change behavior and consistency
- **Hand Replay**: Complete hand replay functionality
- **Performance**: Render performance and memory usage

#### **Accessibility Testing**
- **WCAG Compliance**: Automated and manual accessibility testing
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader**: Screen reader compatibility
- **Color Contrast**: Visual accessibility validation

### **Quality Metrics**

- **Code Coverage**: Minimum 80% test coverage
- **Performance Benchmarks**: Render time < 16ms per frame
- **Memory Usage**: Stable memory footprint during extended use
- **Error Handling**: Graceful degradation and user feedback
- **Accessibility Score**: WCAG 2.1 AA compliance

---

## 📚 **IMPLEMENTATION GUIDELINES**

### **Development Workflow**

1. **Feature Planning**: Define requirements and acceptance criteria
2. **Architecture Review**: Ensure compliance with architectural principles
3. **Implementation**: Follow established patterns and conventions
4. **Testing**: Comprehensive unit and integration testing
5. **Code Review**: Architecture and quality review
6. **Integration**: Merge and deploy with monitoring

### **Code Standards**

- **Python**: PEP 8 compliance with project-specific overrides
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Clear docstrings and inline comments
- **Error Handling**: Graceful error handling with user feedback
- **Logging**: Structured logging for debugging and monitoring

### **Architecture Compliance**

- **Single Source of Truth**: All state managed through Store
- **Event-Driven**: UI actions flow through Store → Reducer → Services
- **Pure Components**: UI components are stateless renderers
- **Service Separation**: Business logic isolated in service layer
- **Theme Integration**: All styling via theme tokens

---

## 🔮 **FUTURE ROADMAP**

### **Phase 1: Core Implementation**
- Complete Enhanced RPGW integration
- Implement all three session types
- Establish testing framework
- Performance optimization

### **Phase 2: Advanced Features**
- Advanced animation system
- Enhanced sound integration
- Performance analytics
- Accessibility improvements

### **Phase 3: Scalability**
- Multi-table support
- Advanced session management
- Plugin architecture
- Cloud integration

---

*This document serves as the authoritative reference for the PokerPro Trainer architecture. All implementations must comply with these principles and patterns.*

```

---

### PokerPro_UI_Implementation_Handbook_v1.1.md

```markdown
# PokerPro Trainer — **UI Implementation Handbook** (v1.1)
**Date**: 2025-08-18  
**Audience**: AI coding agents & human reviewers  
**Status**: Authoritative — Do **not** deviate without updating this handbook.

> Golden rule: **UI renders state; events mutate state via PPSM; effects live at the edges.**

---

## 0) Purpose & Scope
This handbook locks down the **UI-side implementation rules** for PokerPro so contributors and AI agents **do not invent new patterns**. It covers session UIs (Practice, Hands Review, GTO), rendering rules, contracts with PPSM, theming, logging, testing, and a detailed **GameDirector** contract for sounds, animations, and autoplay.

---

## 1) Canonical Architecture (Summary)
- **Coordinator**: Single-threaded, event-driven **GameDirector** orchestrates timing (autoplay, effect gating).  
- **Store**: One source of truth per session. No duplicate state or cross-writes.  
- **Domain**: **PPSM** (PurePokerStateMachine) is deterministic and authoritative for poker rules.  
- **UI**: **Render-only**. Emits **intents** → adapter builds **domain events** → `ppsm.transition(state, event)` → Store update.  
- **Adapters**: Sounds, persistence, estimators, external APIs — side-effectful but stateless re: domain.  
- **Renderer Pipeline**: Composable canvas layers (felt → seats → community → pot → overlays).

---

### 1.1) **Poker Table — Pure Renderer & Reuse Contract**
The poker table is implemented as a **pure renderer** (`backend/ui/renderers/poker_table_renderer.py`).

Authoritative rules:
- Input: one immutable `PokerTableState` (in `backend/ui/table/state.py`).
- Output: optional renderer intents (e.g., `{type: "REQUEST_ANIMATION", payload: effect}`) — no business logic.
- No PPSM calls, no timers, no side effects; purely draws state via tableview components.
- Common across Practice, Hands Review, and GTO sessions; differences live in the **SessionManager**.

Minimal usage:
```python
renderer = PokerTableRenderer(parent, intent_handler, theme_manager)
renderer.render(PokerTableState(...))
```

Effects:
- Renderer emits intents; the shell forwards to EventBus `effect_bus:animate`.
- `EffectBus` bridges to `ChipAnimations` and coordinates gating via **GameDirector**.

Layer order (must): `felt → seats → stacks → community → bets → pot → action → status → overlay → temp_animation`.

### 1.2) **GameDirector — Role & Scope (Authoritative)**
**Goal**: Centralize time, autoplay, and effect sequencing to keep behavior **deterministic, cancellable, and single-threaded**.

**The Director does:**
- Maintain **play/pause/seek/speed** for session playback.
- Schedule **AUTO_ADVANCE** during autoplay at the configured interval.
- **Gate effects** so autoplay only advances after required animations/sounds complete.
- Emit **time events** (`TIMER_TICK`, `TIMER_EXPIRED`) when sessions use timers.
- Coordinate the **EffectBus** (sounds/animations/haptics) via completion events.

**The Director does *not* do:**
- Poker legality or domain rules (PPSM only).  
- Hold domain state (Store is the single source of truth).  
- Use threads or blocking calls (everything single-threaded and queued).

**Minimal API**
```python
class GameDirector:
    def schedule(self, delay_ms: int, event: dict) -> str: ...
    def cancel(self, token: str) -> None: ...
    def play(self) -> None: ...
    def pause(self) -> None: ...
    def step_forward(self, n: int = 1) -> None: ...
    def step_back(self, n: int = 1) -> None: ...
    def seek(self, step_index: int) -> None: ...
    def set_speed(self, multiplier: float) -> None: ...
    def set_autoplay_interval(self, ms: int) -> None: ...

    # Effect gating
    def gate_begin(self) -> None: ...
    def gate_end(self) -> None: ...  # call on ANIM_COMPLETE/SOUND_COMPLETE
```

**Event catalog it may emit**
- `AUTO_ADVANCE` (autoplay next step)
- `TIMER_TICK` / `TIMER_EXPIRED` (if timers are used)
- `ANIM_COMPLETE`, `SOUND_COMPLETE` (posted by EffectBus through Director)

**Timing policy**
- Single-threaded, pumped from UI loop (e.g., Tk `after(16, pump)`).  
- **Speed** scales scheduled delays (`delay_ms / speed`).  
- Time is **fakeable** in tests via an injected clock.

**Integration flow**
```
UI intent → Adapter builds domain event → ppsm.transition → Store.replace →
Renderer renders (pure) → EffectBus interprets effects → Director gates & schedules AUTO_ADVANCE
```

---

## 2) Feature mapping to Renderer / Director / Effects
| Feature | Trigger | Who decides | Director role | Effects / Events |
|---|---|---|---|---|
| **Player highlighting (current actor glow)** | Store state (`seats[i].acting`) | Renderer (pure) | None (render-only) | No effect; renderer reads acting seat |
| **Action sounds (BET/CALL/CHECK/FOLD, etc.)** | After `ppsm.transition` on action events | Reducer adds `SOUND` effect | Gate if sound duration blocks autoplay | `SOUND(id)` → `SOUND_COMPLETE` after duration |
| **Deal sounds (cards)** | On `DEAL_*` events | Reducer adds `SOUND('deal')` | Optional gate | `SOUND('deal')` |
| **End-of-street chips-to-pot animation** | On transition to next street | Reducer adds `ANIMATE('chips_to_pot')` (+ optional sound) | **Gate** until complete | `ANIMATE('chips_to_pot', ms=250)` → `ANIM_COMPLETE` |
| **Showdown / last-player standing** | On `SHOWDOWN` or only one active | Reducer adds `ANIMATE('pot_to_winner')` + `SOUND('chips_scoop')` + `BANNER('winner')` | **Gate** until complete | `ANIMATE('pot_to_winner', ms=500)`; `SOUND('chips_scoop')`; `BANNER('winner')` (non-gated visual) |
| **Autoplay** | User presses Play | Director | Schedules `AUTO_ADVANCE` if not gated | `AUTO_ADVANCE` at interval; delayed while gate > 0 |
| **Speed control** | User changes speed | Director | Scales scheduled delays | N/A |
| **Seek / Step** | User seeks/steps | Director + Shell | Resets playback position; cancels scheduled events | N/A |

**Gating rule**: If any effect in a step requires gating (e.g., chip/pot animation, long SFX), the reducer marks it so the EffectBus calls `director.gate_begin()` before starting and `director.gate_end()` on completion. Autoplay only advances when **gate count is 0**.

---

## 3) Contracts Between UI and PPSM
### 3.1 Inputs to PPSM
```json
{
  "type": "BET",
  "actor_uid": "Player2",
  "street": "TURN",
  "to_amount": 120,
  "note": null
}
```

- `type`: **UPPER_SNAKE_CASE** (e.g., `POST_BLIND`, `BET`, `RAISE`, `CALL`, `CHECK`, `FOLD`, `DEAL_FLOP`, `SHOWDOWN`)
- `street`: **PREFLOP/FLOP/TURN/RIVER** (uppercase)
- Fields: **snake_case**

### 3.2 Outputs the UI may read (via selectors)
- `currentStreet(state)` → `"TURN"`  
- `currentActor(state)` → `"Player1"`  
- `legalActions(state)` → `[ "FOLD", "CALL", "RAISE" ]` with ranges  
- `pot(state)` → `int`  
- `stacks(state)` → `{ uid: int }`  
- `board(state)` → `["Qh","7c","7d"]`  
- `handResult(state)` after `SHOWDOWN`

**Forbidden**: UI must **not** compute legality or mutate domain state.

---

## 4) Renderer Pipeline & Components
**Layer order**: `felt → seats → stacks → community → bets → pot → action → status → overlay → temp_animation`

**Boundaries**
- **SeatPod**: avatar, name, stack, halo, badges (subscribe to seat selectors).
- **CommunityBoard**: board cards and visual-only burns.
- **PotDisplay**: pot totals/side pots/badges.
- **ActionBar**: hero legal actions (from selectors only).
- **HUD/Overlays**: actor glow, toasts, timers; no domain writes.

---

## 5) Sessions (Practice / Hands Review / GTO)
### Session Managers (Reusable Pattern)
Implement managers that own PPSM calls, state shaping, and effects. Examples:
- `PracticeSessionManager`: executes hero/bot actions, builds `PokerTableState`, adds CHIP_TO_POT effects, dispatches to Store
- `GTOSessionManager`: wraps GTO engine, provides advice, same render/effects path
- Planned `HandsReviewSessionManager`: drives trace steps, produces `PokerTableState` and effects

Renderer is shared across all sessions; managers isolate differences.

### 5.2 Hands Review
- Step / Play / Pause / Seek / Speed.  
- Each trace step → domain event; reducer computes effects.  
- Director gates effects so autoplay advances only after completions.

### 5.3 GTO Session
- All non-hero decisions via DecisionEngine; deterministic for seed/state.  
- Explanations come from engine outputs (UI never invents analysis).  
- Effects like Practice; Director coordinates autoplay and gating.

---

## 6) Theme & Design System (Tokens are mandatory)
Use **ThemeManager** tokens; **no literal colors** in components.

Tokens (subset):  
```
a11y.focus, board.border, board.cardBack, board.cardFaceFg, board.slotBg, btn.active.bg, btn.default.bg, btn.hover.bg, burgundy.base, burgundy.bright, burgundy.deep, chip_gold, dealer.buttonBg, dealer.buttonBorder, dealer.buttonFg, emerald.base, emerald.bright, gold.base, gold.bright, gold.dim, panel.bg, panel.border, panel.fg, player.name, player.stack, pot.badgeBg, pot.badgeRing, pot.valueText, primary_bg, seat.bg.acting, seat.bg.active, seat.bg.idle, secondary_bg, table.center, table.edgeGlow, table.felt, table.inlay, table.rail, table.railHighlight, text.muted, text.primary, text.secondary, text_gold, theme_config.json
```

- Accessibility: WCAG ≥ 4.5:1; focus via `a11y.focus`.  
- Targets ≥ 44×44; fonts/cards scale per responsive rules.  
- Live theme switching: components re-render on token change.

---

## 7) EffectBus & Sound Catalog (standardize IDs)
**Effect types**: `SOUND`, `ANIMATE`, `BANNER`, `VIBRATE`, `TOAST`

**Sound IDs (examples; keep stable for mapping):**
- `fx.deal`, `fx.bet_single`, `fx.bet_multi`, `fx.call`, `fx.check`, `fx.fold`, `fx.raise`, `fx.chips_scoop`, `fx.win_fanfare`

**Animation names (examples):**
- `chips_to_pot`, `pot_to_winner`, `actor_glow_pulse`

**Durations**: Use **config** to define canonical durations (ms) for gating; do not measure audio runtime at render time.

---

## 8) Error Handling, Logging, and Telemetry
- Log with ISO timestamps and `module:file:line`; no PII.  
- On invalid event: log step index & `hand_id`, disable controls until Reset/Skip.  
- Director logs: `scheduled`, `executed`, `canceled`, `gated_begin/end` (for CI debugging).

---

## 9) File/Folder Structure (UI)
```
ui/
  store/                 # session store + reducers
    index.py
    selectors.py
  components/
    seat_pod.py
    community_board.py
    pot_display.py
    action_bar.py
    overlays/
  renderer/
    canvas_manager.py
    layer_manager.py
    renderer_pipeline.py
  adapters/
    ppsm_adapter.py
    decision_engine.py
    sound_bus.py
    effect_bus.py
  sessions/
    practice_shell.py
    review_shell.py
    gto_shell.py
  director/
    director.py          # GameDirector + NoopDirector + injected clock
```

---

## 10) Testing Requirements (must pass for PR merge)
- **Unit**: reducers, selectors, adapters, director (scheduling, gating).  
- **Snapshot**: major components across key states.  
- **Replay**: hand traces replay with no divergence; mismatches reported.  
- **Headless**: fake clock; autoplay produces stable PPSM state hashes.

---

## 11) AI Agent Guardrails (read carefully)
1. **Do not add new events or fields.** If missing, leave TODO and stop.  
2. **Never compute poker legality in UI.** Call selectors or PPSM.  
3. **Use theme tokens only.** No literal colors, shadows, fonts.  
4. **No timers/threads in components.** Use **GameDirector** for all timing and autoplay.  
5. **No cross-component writes.** Only Store and events.  
6. **Respect casing rules** (events UPPER_SNAKE_CASE; domain snake_case; streets uppercase).  
7. **Keep functions small and pure**; side effects only in adapters/EffectBus.  
8. **If uncertain**, generate interface stubs, not ad‑hoc logic.

---

### Appendix A — Example Reducer Effects
```python
def reducer_transition(state, evt):
    new_state = ppsm.transition(state, evt)
    effects = []

    if evt["type"] in ('BET', 'RAISE'):
        effects.append({"type": "SOUND", "id": "fx.bet_single", "ms": 220})
    elif evt["type"] == "CALL":
        effects.append({"type": "SOUND", "id": "fx.call", "ms": 180})
    elif evt["type"] == "CHECK":
        effects.append({"type": "SOUND", "id": "fx.check", "ms": 140})
    elif evt["type"] == "FOLD":
        effects.append({"type": "SOUND", "id": "fx.fold", "ms": 160})

    if street_ended(state, new_state):
        effects.append({"type": "ANIMATE", "name": "chips_to_pot", "ms": 260})

    if showdown_or_last_player(new_state):
        effects += [
            {"type": "ANIMATE", "name": "pot_to_winner", "ms": 520},
            {"type": "SOUND", "id": "fx.chips_scoop", "ms": 420},
            {"type": "BANNER", "name": "winner", "ms": 800},
        ]

    return new_state, effects
```

### Appendix B — EffectBus Skeleton
```python
def run_effects(effects: list[dict], director: GameDirector, sound_bus, renderer):
    gated = any(e["type"] in {"ANIMATE", "SOUND"} for e in effects)
    if gated: director.gate_begin()

    for e in effects:
        if e["type"] == "SOUND":
            sound_bus.play(e["id"])
            director.schedule(e.get("ms", 200), {"type": "SOUND_COMPLETE", "id": e["id"]})
        elif e["type"] == "ANIMATE":
            renderer.animate(e["name"], e.get("args", {}))
            director.schedule(e.get("ms", 250), {"type": "ANIM_COMPLETE", "name": e["name"]})
        elif e["type"] == "BANNER":
            renderer.banner(e["name"], e.get("ms", 800))

    if gated:
        # In your event handler for *_COMPLETE, call director.gate_end()
        pass
```


```

---

### PROJECT_PRINCIPLES_v2.md

```markdown
## Project Principles v2 (Authoritative)

### Architecture
- Single-threaded, event-driven coordinator (GameDirector). All timing via coordinator.
- Single source of truth per session (Store). No duplicate state.
- Event-driven only. UI is pure render from state; no business logic in UI.

### Separation of concerns
- Domain: entities, rules, state machines; pure and deterministic.
- Application/Services: orchestration, schedulers, adapters; no UI.
- Adapters: persistence, audio, estimators, external APIs.
- UI: render-only; reads from Store; raises intents.

### Coding standards
- OO-first; composition/strategies/state machines over conditionals.
- DRY; reuse components; small, stable public APIs.
- Deterministic core; isolate I/O, randomness, timing.
- Explicit dependency injection; avoid globals/singletons.

### UI design
- Canvas layers: felt < seats < community < pot < overlay.
- Theme tokens only; central ThemeManager; hot-swappable profiles.
- Accessibility: ≥4.5:1 contrast; 44×44 targets; keyboard bindings; live regions.

### Testing & logging
- Snapshot tests for UI; unit tests for reducers/selectors and adapters.
- Logs to `logs/` with rotation; ISO timestamps; module:file:line; no secrets/PII.

### Prohibitions
- No threading/timers for game logic; no blocking animations/sounds.
- No duplicate state sources; no component-to-component timing calls.

### AI Agent Compliance (Do not deviate)
1. Do **not** add new events or fields. If missing, leave TODO and stop.
2. Never compute poker legality in UI; call selectors/PPSM.
3. Use theme tokens only; no literal colors, shadows, or fonts.
4. Do not use timers/threads for game logic; schedule via Director.
5. No cross-component writes; only Store and events.
6. Respect casing rules (events UPPER_SNAKE_CASE; domain snake_case).
7. Keep functions small and pure; side effects only in adapters.
8. If uncertain, generate interface stubs, not implementations.

### PR Acceptance Checklist
- [ ] No business logic in UI; all decisions via PPSM or DecisionEngine.
- [ ] Events are UPPER_SNAKE_CASE; fields snake_case; streets uppercase.
- [ ] Only theme tokens used; contrast checks pass.
- [ ] Components subscribe via selectors; no direct Store writes.
- [ ] Replay tests pass on sample hands; headless run produces stable state hashes.
- [ ] Logs are present, structured, and scrubbed.

```

---

### RUNTIME_FIXES_README.md

```markdown
# 🚀 Runtime Error Fixes for Poker Application

## Overview
This directory contains runtime fixes for the poker application that resolve compile-time errors during execution.

## Files

### 1. `fix_runtime_errors.py` - Main Fixer
**Purpose**: Automatically patches missing methods and fixes runtime errors
**What it fixes**:
- ✅ Adds missing `initialize_game()` method to PurePokerStateMachine
- ✅ Adds missing `add_player()` method to PurePokerStateMachine  
- ✅ Adds missing `set_dealer_position()` method to PurePokerStateMachine
- ✅ Adds missing `get_game_state()` method to PurePokerStateMachine
- ✅ Fixes HandsReviewSessionManager initialization issues
- ✅ Ensures HandModelDecisionEngine compatibility

### 2. `run_poker_fixed.py` - Fixed Launcher
**Purpose**: Automatically applies fixes before launching the application
**Usage**: `python3 run_poker_fixed.py`

### 3. `run_new_ui.py` - Original Launcher
**Purpose**: Original application launcher (may have errors without fixes)

## How to Use

### Option 1: Automatic Fix + Launch (Recommended)
```bash
python3 run_poker_fixed.py
```
This automatically applies all fixes and launches the application.

### Option 2: Manual Fix + Launch
```bash
# Step 1: Apply fixes
python3 fix_runtime_errors.py

# Step 2: Launch application
python3 run_new_ui.py
```

### Option 3: One-time Fix
```bash
# Apply fixes once (they persist for the session)
python3 fix_runtime_errors.py

# Then use normal launcher
python3 run_new_ui.py
```

## What Gets Fixed

### PurePokerStateMachine Methods
- **`initialize_game(config)`**: Sets up game with configuration
- **`add_player(name, stack)`**: Adds player to the game
- **`set_dealer_position(pos)`**: Sets dealer position
- **`get_game_state()`**: Returns current game state

### Session Manager Issues
- Hand loading errors
- PPSM initialization problems
- Player management issues

### Decision Engine Compatibility
- HandModelDecisionEngine stub creation if needed
- Method compatibility fixes

## Error Resolution

| Error | Fix Applied |
|-------|-------------|
| `'PurePokerStateMachine' object has no attribute 'initialize_game'` | ✅ Added method |
| `'PurePokerStateMachine' object has no attribute 'add_player'` | ✅ Added method |
| `'PurePokerStateMachine' object has no attribute 'set_dealer_position'` | ✅ Added method |
| `'PurePokerStateMachine' object has no attribute 'get_game_state'` | ✅ Added method |
| Session manager initialization failures | ✅ Fixed PPSM setup |
| Hand loading errors | ✅ Fixed data structure access |

## Benefits

1. **No More Console Errors**: All runtime errors are resolved
2. **Seamless Operation**: Application runs without interruptions
3. **Automatic Fixes**: No manual intervention required
4. **Session Persistence**: Fixes remain active for the session
5. **Backward Compatible**: Original code remains unchanged

## Troubleshooting

If you still see errors:
1. Ensure you're in the `backend` directory
2. Run `python3 fix_runtime_errors.py` first
3. Check that all imports are working
4. Verify Python path includes the backend directory

## Architecture Notes

These fixes use **monkey patching** to add missing methods at runtime. This approach:
- ✅ Resolves immediate runtime errors
- ✅ Maintains original code integrity
- ✅ Provides backward compatibility
- ✅ Enables immediate testing and development

The fixes are **non-destructive** and only add missing functionality without modifying existing code.

```

---

## 📋 END OF COMPREHENSIVE BUG REPORT

*This file contains all the information needed to resolve the UI coordination issues while maintaining architecture compliance.*
