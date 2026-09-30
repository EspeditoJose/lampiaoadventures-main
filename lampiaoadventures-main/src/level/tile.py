"""
Tile Module.
Provides tiles for map geometry, hazards, collectibles, and animated background props.
"""

import math
import pygame
from config import COLOR_TILE, COLOR_TILE_BORDER, COLOR_HAZARD, COLOR_COLLECTIBLE, COLOR_PROP
from src.utils.asset_loader import AssetLoader

class Tile:
    TYPE_SOLID = "SOLID"
    TYPE_HAZARD = "HAZARD"
    TYPE_COLLECTIBLE = "COLLECTIBLE"
    TYPE_PROP = "PROP"

    def __init__(self, x: float, y: float, width: int = 40, height: int = 40, tile_type: str = TYPE_SOLID, label: str = "", sprite_path: str = ""):
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.tile_type = tile_type
        self.is_solid = (tile_type == Tile.TYPE_SOLID)
        self.is_hazard = (tile_type == Tile.TYPE_HAZARD)
        self.is_collectible = (tile_type == Tile.TYPE_COLLECTIBLE)
        self.is_active = True
        self.anim_timer = 0.0

        # Choose default colors based on tile type
        if tile_type == Tile.TYPE_SOLID:
            fallback_color = COLOR_TILE
            default_label = label if label else "DIRT"
        elif tile_type == Tile.TYPE_HAZARD:
            fallback_color = COLOR_HAZARD
            default_label = label if label else "SPIKE"
        elif tile_type == Tile.TYPE_COLLECTIBLE:
            fallback_color = COLOR_COLLECTIBLE
            default_label = label if label else "CATITA"
        else:
            fallback_color = COLOR_PROP
            default_label = label if label else "PROP"

        self.surface = AssetLoader.load_image(
            relative_path=sprite_path if sprite_path else f"assets/sprites/tiles/{default_label.lower()}.png",
            size=(width, height),
            fallback_color=fallback_color,
            label=default_label
        )

    def update(self, dt: float):
        """Update animation for collectibles or props."""
        self.anim_timer += dt

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        screen_rect = camera.apply(self.rect)
        
        # Only render if on-screen
        if not screen.get_rect().colliderect(screen_rect):
            return

        # Special bobbing effect for collectibles
        if self.is_collectible:
            bob_y = int(math.sin(self.anim_timer * 6.0) * 4.0)
            screen.blit(self.surface, (screen_rect.x, screen_rect.y + bob_y))
        else:
            screen.blit(self.surface, screen_rect)
