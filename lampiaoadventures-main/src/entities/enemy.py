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

class CalangoEnemy(Enemy):
    """
    Calango ground enemy. Replaces old Chaser block with full pixel art animation
    (assets/sprites/calango/calango-chasing.png: 6 frames, 48x48, colorkey 126,126,125).
    Patrols at 1.2 px/frame and chases player at 2.2 px/frame when detected.
    """
    def __init__(self, x: float, y: float, patrol_dist: float = 180.0, detection_radius: float = 240.0):
        super().__init__(
            x=x, y=y, width=48, height=48, hp=35, damage=20,
            color=COLOR_ENEMY_PATROL, label="CALANGO"
        )
        self.patrol_min_x = x - patrol_dist
        self.patrol_max_x = x + patrol_dist
        self.patrol_speed = 1.2   # Slower, natural crawling patrol speed
        self.chase_speed = 2.2    # Reduced, balanced chasing speed
        self.detection_radius = detection_radius
        self.direction = 1        # 1 for right, -1 for left

        # Load idle sprite (calango-idle.png: 48x48)
        self.idle_surf = AssetLoader.load_image(
            relative_path="assets/sprites/calango/calango-idle.png",
            size=(48, 48),
            fallback_color=COLOR_ENEMY_PATROL,
            label="CALANGO_IDLE"
        )

        # Load 6-frame 48x48 chasing spritesheet with colorkey (126, 126, 125)
        self.chase_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/calango/calango-chasing.png",
            frame_width=48, frame_height=48, num_frames=6,
            colorkey=(126, 126, 125), fallback_color=COLOR_ENEMY_CHASE, label_prefix="CALANGO_RUN"
        )

        self.current_frame_idx = 0.0
        self.anim_fps = 12.0
        self.surface = self.chase_frames[0] if self.chase_frames else self.idle_surf

    def update_ai(self, dt: float, player, tiles: list):
        if not self.is_active:
            return

        # Distance to player
        dist_to_player = self.pos.distance_to(player.pos)

        # State transition check
        if dist_to_player <= self.detection_radius and player.health > 0:
            self.state = "CHASE"
        else:
            self.state = "PATROL"

        # Execute state movement
        if self.state == "PATROL":
            self.vel.x = self.direction * self.patrol_speed
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
                self.vel.x = 0.0

        self.facing = "right" if self.direction == 1 else "left"

        # Animate sprite
        if abs(self.vel.x) > 0.1 and self.chase_frames:
            # Scale animation speed with movement velocity
            speed_factor = abs(self.vel.x) / self.chase_speed
            self.current_frame_idx += self.anim_fps * speed_factor * dt
            if self.current_frame_idx >= len(self.chase_frames):
                self.current_frame_idx %= len(self.chase_frames)
            self.surface = self.chase_frames[int(self.current_frame_idx)]
        else:
            self.surface = self.idle_surf

        # Apply horizontal movement & wall collision
        self.pos.x += self.vel.x
        self.update_rect()

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                    self.direction = -1
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                    self.direction = 1
                self.pos.x = float(self.rect.x)

        # Physics & gravity update
        super().update(dt, tiles)

        # Pit / Abyss detection probe: turn around if no ground ahead
        if self.is_grounded and tiles:
            probe_x = self.rect.left - 6 if self.direction == -1 else self.rect.right + 6
            probe_y = self.rect.bottom + 4
            probe_rect = pygame.Rect(probe_x, probe_y, 6, 12)
            has_ground_ahead = any(tile.is_solid and probe_rect.colliderect(tile.rect) for tile in tiles)
            if not has_ground_ahead:
                self.direction = -self.direction

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        screen_pos = camera.apply(self)

        # Raw sprite faces LEFT naturally. Flip horizontally when moving RIGHT (direction == 1).
        if self.direction == 1:
            flipped_surf = pygame.transform.flip(self.surface, True, False)
            screen.blit(flipped_surf, screen_pos)
        else:
            screen.blit(self.surface, screen_pos)

        # Draw alert exclamation mark above head if chasing
        if self.state == "CHASE":
            font = pygame.font.SysFont("arial", 14, bold=True)
            alert_txt = font.render("!", True, (255, 69, 0))
            screen.blit(alert_txt, (screen_pos.centerx - 4, screen_pos.top - 16))

# Alias ChaserEnemy to CalangoEnemy for backwards compatibility across tilemap and scene loaders
ChaserEnemy = CalangoEnemy


class TanajuraEnemy(Enemy):
    """
    Tanajura enemy that spawns high above the screen flying downward fast (tanajura-flying.png, 3 frames),
    lands at its target ground position, and then patrols on foot using tanajura-walking.png (4 frames).
    """
    def __init__(self, x: float, y: float, patrol_dist: float = 120.0):
        target_y = y
        spawn_y = target_y - 300.0

        super().__init__(
            x=x, y=spawn_y, width=32, height=32, hp=20, damage=15,
            color=COLOR_ENEMY_PATROL, label="TANAJURA"
        )
        self.target_y = target_y
        self.patrol_min_x = x - patrol_dist
        self.patrol_max_x = x + patrol_dist
        self.patrol_speed = 2.2
        self.fly_descent_speed = 5.0
        self.direction = 1
        self.state = "FLYING_DESCENT"

        # Static sprite (tanajura.png)
        self.static_surf = AssetLoader.load_image(
            relative_path="assets/sprites/tanajura/tanajura.png",
            size=(32, 32),
            fallback_color=(139, 69, 19),
            label="TANAJURA"
        )

        # Flying animation (tanajura-flying.png: 3 frames, 32x32, fast wing flutter)
        self.fly_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/tanajura/tanajura-flying.png",
            frame_width=32, frame_height=32, num_frames=3,
            colorkey=(126, 126, 126), fallback_color=(139, 69, 19), label_prefix="TANAJURA_FLY"
        )

        # Walking animation (tanajura-walking.png: 4 frames, 32x32)
        self.walk_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/tanajura/tanajura-walking.png",
            frame_width=32, frame_height=32, num_frames=4,
            colorkey=(127, 127, 127), fallback_color=(139, 69, 19), label_prefix="TANAJURA_WALK"
        )

        self.current_frame_idx = 0.0
        self.fly_anim_fps = 24.0   # Fast flutter FPS for flying animation
        self.walk_anim_fps = 10.0  # Walking FPS
        self.surface = self.fly_frames[0] if self.fly_frames else self.static_surf

    def update_ai(self, dt: float, player, tiles: list):
        if not self.is_active:
            return

        # 1. FLYING_DESCENT State (spawns flying down from above)
        if self.state == "FLYING_DESCENT":
            if self.fly_frames:
                self.current_frame_idx += self.fly_anim_fps * dt
                if self.current_frame_idx >= len(self.fly_frames):
                    self.current_frame_idx %= len(self.fly_frames)
                self.surface = self.fly_frames[int(self.current_frame_idx)]

            # Move downward towards target_y
            self.pos.y += self.fly_descent_speed
            self.update_rect()

            landed = False
            if self.pos.y >= self.target_y:
                self.pos.y = self.target_y
                landed = True

            for tile in tiles:
                if tile.is_solid and self.rect.colliderect(tile.rect):
                    self.rect.bottom = tile.rect.top
                    self.pos.y = float(self.rect.y)
                    landed = True
                    break

            if landed:
                self.state = "PATROL"
                self.current_frame_idx = 0.0
                if self.walk_frames:
                    self.surface = self.walk_frames[0]
            return

        # 2. PATROL State (walking normally on ground)
        self.vel.x = self.direction * self.patrol_speed
        if self.pos.x >= self.patrol_max_x:
            self.direction = -1
        elif self.pos.x <= self.patrol_min_x:
            self.direction = 1

        self.facing = "right" if self.direction == 1 else "left"

        # Update walking animation frame
        if self.walk_frames and abs(self.vel.x) > 0.1:
            self.current_frame_idx += self.walk_anim_fps * dt
            if self.current_frame_idx >= len(self.walk_frames):
                self.current_frame_idx %= len(self.walk_frames)
            self.surface = self.walk_frames[int(self.current_frame_idx)]
        else:
            self.surface = self.static_surf

        # Apply Horizontal Movement & Wall Collision
        self.pos.x += self.vel.x
        self.update_rect()

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                    self.direction = -1
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                    self.direction = 1
                self.pos.x = self.rect.x

        # Physics & gravity
        super().update(dt, tiles)

        # Pit / Abyss detection probe: turn around if no ground ahead
        if self.is_grounded and tiles:
            probe_x = self.rect.left - 6 if self.direction == -1 else self.rect.right + 6
            probe_y = self.rect.bottom + 4
            probe_rect = pygame.Rect(probe_x, probe_y, 6, 12)
            has_ground_ahead = any(tile.is_solid and probe_rect.colliderect(tile.rect) for tile in tiles)
            if not has_ground_ahead:
                self.direction = -self.direction

