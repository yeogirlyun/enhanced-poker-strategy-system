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
        if self.voice_enabled and voice_action and hasattr(self, 'voice_manager') and self.voice_manager:
            try:
                print(f"🔊 DEBUG: Playing voice for action '{action_type}' -> '{voice_action}'")
                self.voice_manager.play_action_voice(voice_action.lower(), 0)
            except Exception as e:
                print(f"🔊 DEBUG: Voice playback failed: {e}")
        elif self.voice_enabled:
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
