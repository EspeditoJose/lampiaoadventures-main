"""
Asset Loader and Fallback Placeholder Renderer.
Provides seamless fallback for missing images and audio files using colored labeled shapes
and dummy audio objects so the game runs without external media assets.
"""

import os
import pygame
from config import COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_PLAYER, COLOR_ENEMY_PATROL, COLOR_NPC, COLOR_TILE

class DummySound:
    """Fallback silent sound class returned when audio files are missing or mixer is uninitialized."""
    def __init__(self, name=""):
        self.name = name

    def play(self, loops=0, maxtime=0, fade_ms=0):
        pass

    def stop(self):
        pass

    def set_volume(self, volume):
        pass

    def get_volume(self):
        return 0.0

class PlaceholderRenderer:
    """Generates clean colored rectangular surfaces with borders and labels when images are missing."""
    
    _font_cache = {}

    @classmethod
    def get_font(cls, size=14):
        if size not in cls._font_cache:
            if pygame.font.get_init():
                cls._font_cache[size] = pygame.font.SysFont("arial", size, bold=True)
            else:
                cls._font_cache[size] = None
        return cls._font_cache[size]

    @classmethod
    def create_placeholder_surface(cls, width: int, height: int, color: tuple, label: str = "", border_color: tuple = None) -> pygame.Surface:
        """Creates a styled placeholder surface with optional text label and border."""
        surf = pygame.Surface((max(width, 4), max(height, 4)), pygame.SRCALPHA)
        
        # Fill base color
        surf.fill(color)

        # Draw border
        b_color = border_color if border_color else (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        pygame.draw.rect(surf, b_color, surf.get_rect(), width=2)
        
        # Draw inner diagonal pattern/accent for visual flair
        if width > 16 and height > 16:
            pygame.draw.line(surf, b_color, (0, 0), (width, height), 1)
            pygame.draw.line(surf, b_color, (0, height), (width, 0), 1)

        # Render label text
        if label:
            font = cls.get_font(min(14, max(10, height // 3)))
            if font:
                text_surf = font.render(label, True, COLOR_WHITE)
                shadow_surf = font.render(label, True, COLOR_BLACK)
                text_rect = text_surf.get_rect(center=(width // 2, height // 2))
                surf.blit(shadow_surf, (text_rect.x + 1, text_rect.y + 1))
                surf.blit(text_surf, text_rect)

        return surf

class SpriteWrapper:
    """
    Wraps sprite rendering. Automatically uses placeholder if image file is not found.
    Allows changing asset path in future with zero logic rewrites.
    """
    def __init__(self, relative_path: str, fallback_size: tuple = (40, 40), fallback_color: tuple = COLOR_PLAYER, label: str = ""):
        self.relative_path = relative_path
        self.fallback_size = fallback_size
        self.fallback_color = fallback_color
        self.label = label
        self.surface = AssetLoader.load_image(relative_path, fallback_size, fallback_color, label)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def draw(self, target_surface: pygame.Surface, dest):
        target_surface.blit(self.surface, dest)

class AssetLoader:
    """Central asset manager with caching and fallback support."""
    _image_cache = {}
    _sound_cache = {}
    _spritesheet_cache = {}

    @classmethod
    def load_image(cls, relative_path: str, size: tuple = None, fallback_color: tuple = (200, 200, 200), label: str = "") -> pygame.Surface:
        """Loads image or generates placeholder surface if missing."""
        cache_key = (relative_path, size, fallback_color, label)
        if cache_key in cls._image_cache:
            return cls._image_cache[cache_key]

        full_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                surf = pygame.image.load(full_path)
                if pygame.display.get_surface() is not None:
                    surf = surf.convert_alpha()
                if size and size != surf.get_size():
                    surf = pygame.transform.smoothscale(surf, size)
                cls._image_cache[cache_key] = surf
                return surf
            except Exception as e:
                print(f"[AssetLoader] Warning: Failed to load image {full_path}: {e}. Using placeholder.")

        # Generate fallback placeholder
        width, height = size if size else (40, 40)
        display_label = label if label else os.path.basename(relative_path).split('.')[0].upper()
        surf = PlaceholderRenderer.create_placeholder_surface(width, height, fallback_color, display_label)
        cls._image_cache[cache_key] = surf
        return surf

    @classmethod
    def load_spritesheet(cls, relative_path: str, frame_width: int, frame_height: int, num_frames: int, colorkey: tuple = None, fallback_color: tuple = (200, 200, 200), label_prefix: str = "FRAME") -> list:
        """
        Loads a horizontal spritesheet, slices it into frame_width x frame_height frames,
        applies colorkey transparency if specified, and returns a list of Pygame Surfaces.
        Generates fallback placeholders if file is missing.
        """
        cache_key = (relative_path, frame_width, frame_height, num_frames, colorkey, fallback_color, label_prefix)
        if cache_key in cls._spritesheet_cache:
            return cls._spritesheet_cache[cache_key]

        full_path = os.path.join(os.getcwd(), relative_path)
        frames = []

        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                sheet = pygame.image.load(full_path)
                for i in range(num_frames):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    
                    frame_surf = pygame.Surface((frame_width, frame_height))
                    frame_surf.blit(sheet, (0, 0), frame_rect)

                    if colorkey is not None:
                        frame_surf.set_colorkey(colorkey)
                    
                    if pygame.display.get_surface() is not None:
                        try:
                            frame_surf = frame_surf.convert_alpha()
                        except Exception:
                            pass

                    frames.append(frame_surf)

                cls._spritesheet_cache[cache_key] = frames
                return frames
            except Exception as e:
                print(f"[AssetLoader] Warning: Failed to load spritesheet {full_path}: {e}. Using placeholders.")

        # Fallback placeholders for missing spritesheet
        for i in range(num_frames):
            display_label = f"{label_prefix}_{i}"
            frame_surf = PlaceholderRenderer.create_placeholder_surface(frame_width, frame_height, fallback_color, display_label)
            frames.append(frame_surf)

        cls._spritesheet_cache[cache_key] = frames
        return frames

    @classmethod
    def load_sound(cls, relative_path: str) -> object:
        """Loads sound or returns DummySound if missing/uninitialized."""
        if relative_path in cls._sound_cache:
            return cls._sound_cache[relative_path]

        if not pygame.mixer.get_init():
            dummy = DummySound(relative_path)
            cls._sound_cache[relative_path] = dummy
            return dummy

        full_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                cls._sound_cache[relative_path] = sound
                return sound
            except Exception as e:
                print(f"[AssetLoader] Warning: Failed to load sound {full_path}: {e}. Using DummySound.")

        dummy = DummySound(relative_path)
        cls._sound_cache[relative_path] = dummy
        return dummy
