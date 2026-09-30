"""
Base Entity Abstract Class.
Common foundation for player, enemies, NPCs, and interactive objects.
"""

import pygame
from abc import ABC, abstractmethod
from src.utils.asset_loader import AssetLoader

class BaseEntity(ABC):
    def __init__(self, x: float, y: float, width: int, height: int, color: tuple = (200, 200, 200), label: str = "", sprite_path: str = ""):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(int(x), int(y), width, height)

        self.color = color
        self.label = label
        self.sprite_path = sprite_path
        self.facing = "right"
        self.is_active = True
        self.is_grounded = False

        # Load surface using AssetLoader (fallback automatically used if file missing)
        self.surface = AssetLoader.load_image(
            relative_path=self.sprite_path if self.sprite_path else f"assets/sprites/placeholder_{label.lower()}.png",
            size=(width, height),
            fallback_color=self.color,
            label=self.label
        )

    def update_rect(self):
        """Sync rect position with floating point position vector."""
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

    @abstractmethod
    def update(self, dt: float, tiles: list):
        """Update entity state and handle tile collisions."""
        pass

    def render(self, screen: pygame.Surface, camera):
        """Render entity surface offset by camera."""
        if not self.is_active:
            return
        
        screen_rect = camera.apply(self)
        
        # Flip sprite if facing left
        if self.facing == "left":
            flipped_surf = pygame.transform.flip(self.surface, True, False)
            screen.blit(flipped_surf, screen_rect)
        else:
            screen.blit(self.surface, screen_rect)

    def get_hitbox(self) -> pygame.Rect:
        return self.rect
