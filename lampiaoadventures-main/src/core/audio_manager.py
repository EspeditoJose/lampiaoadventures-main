"""
Audio Manager.
Handles BGM streaming, SFX playback, and volume controls with safe fallbacks
if files or audio devices are missing.
"""

import pygame
import os
from src.utils.asset_loader import AssetLoader, DummySound

class AudioManager:
    """Singleton/Manager for handling game music and sound effects."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance._init_audio()
        return cls._instance

    def _init_audio(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.current_music_path = None
        self.mixer_available = pygame.mixer.get_init() is not None

    def play_music(self, relative_path: str, loop: int = -1, volume: float = None, fade_ms: int = 0):
        """Plays background music safely with optional fade-in."""
        if volume is not None:
            self.music_volume = volume

        if not self.mixer_available:
            return

        full_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(full_path):
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self.music_volume)
                if fade_ms > 0:
                    pygame.mixer.music.play(loop, fade_ms=fade_ms)
                else:
                    pygame.mixer.music.play(loop)
                self.current_music_path = relative_path
            except Exception as e:
                print(f"[AudioManager] Warning: Could not play music '{relative_path}': {e}")
        else:
            # Silence fallback
            pass

    def fadeout_music(self, ms: int = 1500):
        """Fades out current playing background music smoothly."""
        if self.mixer_available:
            try:
                pygame.mixer.music.fadeout(ms)
            except Exception:
                pass

    def stop_music(self):
        if self.mixer_available:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def play_sfx(self, relative_path: str, volume: float = None) -> object:
        """Plays a sound effect with fallback."""
        vol = volume if volume is not None else self.sfx_volume
        sound = AssetLoader.load_sound(relative_path)
        if not isinstance(sound, DummySound):
            sound.set_volume(vol)
            sound.play()
        return sound

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_available:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
