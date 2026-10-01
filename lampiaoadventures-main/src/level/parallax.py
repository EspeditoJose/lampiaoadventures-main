"""
Parallax Background System.
Provides multi-layered scrolling background layers scaled to virtual display height.
Layer 2 (back2.png) is rendered in the back, while Layer 1 (back1.png) is rendered in front of back2.
"""

import os
import pygame
from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT
from src.utils.asset_loader import AssetLoader

class ParallaxLayer:
    """Represents a single horizontal scrolling background layer."""
    def __init__(self, relative_path: str, scroll_ratio: float, height: int = VIRTUAL_HEIGHT):
        self.relative_path = relative_path
        self.scroll_ratio = scroll_ratio
        self.height = height

        # Load image using AssetLoader
        raw_surf = AssetLoader.load_image(relative_path, fallback_color=(200, 160, 100))
        
        # Scale to match virtual height while preserving aspect ratio
        orig_w, orig_h = raw_surf.get_size()
        if orig_h > 0:
            scale = height / float(orig_h)
            new_w = max(1, int(orig_w * scale))
        else:
            new_w = VIRTUAL_WIDTH

        if pygame.display.get_surface() is not None:
            try:
                raw_surf = raw_surf.convert_alpha()
            except Exception:
                pass

        self.surface = pygame.transform.smoothscale(raw_surf, (new_w, height))
        self.width = new_w

    def render(self, screen: pygame.Surface, camera_x: float, y_offset: int = 0):
        """Renders tiled layer with seamless horizontal scrolling based on camera_x."""
        if self.width <= 0:
            return

        # Calculate horizontal scroll offset
        start_x = -int((camera_x * self.scroll_ratio) % self.width)
        
        x = start_x
        while x < VIRTUAL_WIDTH:
            screen.blit(self.surface, (x, y_offset))
            x += self.width


class ParallaxBackground:
    """
    Manages dual-layer parallax scrolling.
    Renders back2.png behind back1.png.
    """
    def __init__(self, back2_path: str = "assets/sprites/back2.png", back1_path: str = "assets/sprites/back1.png"):
        # Layer 2 (far background / sky / mountains): scrolls slow in the back
        self.layer_back2 = ParallaxLayer(back2_path, scroll_ratio=0.20)
        
        # Layer 1 (foreground hills / dunes): scrolls faster, rendered in front of back2
        self.layer_back1 = ParallaxLayer(back1_path, scroll_ratio=0.45)

    def render(self, screen: pygame.Surface, camera_x: float):
        """Renders back2 first (far back), then back1 in front of back2."""
        # 1. Render back2 (behind)
        self.layer_back2.render(screen, camera_x)

        # 2. Render back1 (in front of back2)
        self.layer_back1.render(screen, camera_x)
