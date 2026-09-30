"""
Enemy Entities.
Provides base Enemy class and ChaserEnemy subclass with detection AI and state switching.
"""

import math
import pygame
from config import COLOR_ENEMY_PATROL, COLOR_ENEMY_CHASE, GRAVITY, MAX_FALL_SPEED, COLOR_WHITE, COLOR_BLACK
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader

class Enemy(BaseEntity):
    def __init__(self, x: float, y: float, width: int = 40, height: int = 40, hp: int = 30, damage: int = 20, color: tuple = COLOR_ENEMY_PATROL, label: str = "ENEMY"):
        super().__init__(
            x=x, y=y, width=width, height=height,
            color=color, label=label,
            sprite_path="assets/sprites/enemies/cangaceiro.png"
        )
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = 2.0
        self.state = "PATROL"

    def update(self, dt: float, tiles: list):
        """Base enemy physics and gravity update."""
        if not self.is_active:
            return

        # Apply Gravity
        self.vel.y += GRAVITY
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

        # Vertical Movement & Tile Collision
        self.pos.y += self.vel.y
        self.update_rect()
        self.is_grounded = False

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.is_grounded = True
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0
                self.pos.y = self.rect.y

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.is_active = False

class ChaserEnemy(Enemy):
    """
    Chaser enemy that patrols back and forth, and chases the player
    when the player enters its detection radius.
    """
    def __init__(self, x: float, y: float, patrol_dist: float = 200.0, detection_radius: float = 280.0):
        super().__init__(
            x=x, y=y, width=42, height=48, hp=40, damage=25,
            color=COLOR_ENEMY_PATROL, label="CANGACEIRO"
        )
        self.patrol_min_x = x - patrol_dist
        self.patrol_max_x = x + patrol_dist
        self.patrol_speed = 2.0
        self.chase_speed = 4.2
        self.detection_radius = detection_radius
        self.direction = 1  # 1 for right, -1 for left

        # Dynamic surface cache for chase state
        self.patrol_surf = self.surface
        self.chase_surf = AssetLoader.load_image(
            relative_path="assets/sprites/enemies/cangaceiro_chase.png",
            size=(self.width, self.height),
            fallback_color=COLOR_ENEMY_CHASE,
            label="CHASER!"
        )

    def update_ai(self, dt: float, player, tiles: list):
        if not self.is_active:
            return

        # Calculate distance to player
        dist_to_player = self.pos.distance_to(player.pos)

        # State Transition Check
        if dist_to_player <= self.detection_radius and player.health > 0:
            self.state = "CHASE"
            self.surface = self.chase_surf
        else:
            self.state = "PATROL"
            self.surface = self.patrol_surf

        # Execute State Logic
        if self.state == "PATROL":
            self.vel.x = self.direction * self.patrol_speed
            # Check patrol limits
            if self.pos.x >= self.patrol_max_x:
                self.direction = -1
            elif self.pos.x <= self.patrol_min_x:
                self.direction = 1

        elif self.state == "CHASE":
            if player.pos.x > self.pos.x + 5:
                self.vel.x = self.chase_speed
                self.direction = 1
            elif player.pos.x < self.pos.x - 5:
                self.vel.x = -self.chase_speed
                self.direction = -1
            else:
                self.vel.x = 0

        self.facing = "right" if self.direction == 1 else "left"

        # Apply Horizontal Movement & Wall Collision
        self.pos.x += self.vel.x
        self.update_rect()

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                    self.direction = -1  # Reverse direction on wall hit
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                    self.direction = 1
                self.pos.x = self.rect.x

        # Apply physics & gravity
        super().update(dt, tiles)

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return
        
        super().render(screen, camera)

        # Draw exclamation mark above head if in CHASE state
        if self.state == "CHASE":
            screen_pos = camera.apply(self)
            font = pygame.font.SysFont("arial", 16, bold=True)
            alert_txt = font.render("!", True, (255, 255, 0))
            screen.blit(alert_txt, (screen_pos.centerx - 4, screen_pos.top - 18))
