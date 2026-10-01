"""
Bullet Projectile Entity.
Small square projectile fired from player's gun muzzle in the aiming direction.
"""

import pygame

class Bullet:
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, damage: int = 25):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.size = 6  # 6x6 pixel square
        self.rect = pygame.Rect(int(x), int(y), self.size, self.size)
        self.damage = damage
        self.is_active = True
        self.lifetime = 1.2  # Max seconds before auto-destroying

    def update(self, dt: float, tiles: list, enemies: list = None):
        if not self.is_active:
            return

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
            return

        # Move projectile
        self.pos += self.vel
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        # Check collision with solid tiles
        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                self.is_active = False
                return

        # Check collision with enemies (Chaser, Tanajura, Vaca Mojada, etc.)
        if enemies:
            for enemy in enemies:
                if enemy.is_active and hasattr(enemy, 'get_hitbox'):
                    if self.rect.colliderect(enemy.get_hitbox()):
                        enemy.take_damage(self.damage)
                        self.is_active = False
                        return

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        screen_rect = camera.apply(self)
        # Draw bright square bullet with dark accent border
        pygame.draw.rect(screen, (255, 235, 100), screen_rect)
        pygame.draw.rect(screen, (180, 90, 0), screen_rect, width=1)
