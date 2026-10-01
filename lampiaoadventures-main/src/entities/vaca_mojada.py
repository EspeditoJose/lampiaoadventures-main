"""
Vaca Mojada Boss Enemy / Environmental Hazard.
Spawns in the middle of the map, triggers a cinematic intro that locks player controls ("trava tudo"),
prepares slowly to run ("se prepara lentamente para correr"), and rushes across the ground.
From then on, periodically rushes across the screen every 7 seconds until the level ends.
"""

import math
import pygame
from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, GRAVITY, MAX_FALL_SPEED, COLOR_ENEMY_CHASE
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader
from src.core.audio_manager import AudioManager

class VacaMojada(BaseEntity):
    # State constants
    STATE_DORMANT = "DORMANT"
    STATE_INTRO_IDLE = "INTRO_IDLE"
    STATE_INTRO_START = "INTRO_START"
    STATE_WAITING_RUSH = "WAITING_RUSH"
    STATE_RUSHING = "RUSHING"

    def __init__(self, x: float = 2800.0, y: float = 512.0, trigger_x: float = 2700.0):
        # Ground-aligned 64x64 frame box
        super().__init__(
            x=x, y=y, width=64, height=64,
            color=COLOR_ENEMY_CHASE, label="VACA_MOJADA",
            sprite_path="assets/sprites/vaca-mojada/vaca-mojada.png"
        )
        self.spawn_pos = pygame.Vector2(x, y)
        self.trigger_x = trigger_x
        self.hp = 999  # Boss / persistent environmental hazard
        self.damage = 30
        self.rush_speed = 5.5  # Reduced & natural running speed (px/frame)
        self.run_anim_fps = 8.0 # Synced animation playback speed (frames/sec)
        self.direction = -1    # -1 for left, 1 for right
        self.state = VacaMojada.STATE_DORMANT

        # Timers
        self.state_timer = 0.0
        self.rush_cooldown = 7.0  # Rush across screen every 7 seconds
        self.cooldown_timer = 0.0
        self.current_frame_idx = 0.0
        self.locked_player = None

        self.audio_manager = AudioManager()

        # Load Spritesheets & Static Prep Image
        # 1. Idle: 6 frames, colorkey (32, 132, 212)
        self.idle_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/vaca-mojada/vaca-mojada-idle.png",
            frame_width=64, frame_height=64, num_frames=6,
            colorkey=(32, 132, 212), fallback_color=COLOR_ENEMY_CHASE, label_prefix="VACA_IDLE"
        )

        # 2. Preparing Image: static sprite vaca-mojada-idle-preparing.png (64x64, colorkey 127,127,127)
        self.prep_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/vaca-mojada/vaca-mojada-idle-preparing.png",
            frame_width=64, frame_height=64, num_frames=1,
            colorkey=(127, 127, 127), fallback_color=COLOR_ENEMY_CHASE, label_prefix="VACA_PREP"
        )
        self.prep_surface = self.prep_frames[0] if self.prep_frames else None

        # 3. Running: 7 frames, colorkey (127, 127, 127)
        self.run_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/vaca-mojada/vaca-mojada-running.png",
            frame_width=64, frame_height=64, num_frames=7,
            colorkey=(127, 127, 127), fallback_color=COLOR_ENEMY_CHASE, label_prefix="VACA_RUN"
        )

        if self.idle_frames:
            self.surface = self.idle_frames[0]

    def take_damage(self, amount: int):
        """Take damage method required for collision handling with player bullets."""
        self.hp -= amount
        if self.hp <= 0:
            self.is_active = False

    def update(self, dt: float, tiles: list = None, player=None, camera=None):
        """Standard BaseEntity update interface implementation."""
        self.update_boss(dt, player, camera, tiles if tiles is not None else [])

    def update_boss(self, dt: float, player=None, camera=None, tiles: list = None):
        if tiles is None:
            tiles = []

        # Filter tiles so Vaca Mojada ONLY collides with ground floor (y >= 544), excluding high floating platforms
        ground_tiles = [
            t for t in tiles
            if t.is_solid and 'PLAT' not in getattr(t, 'label', '') and t.rect.y >= 544
        ]

        # 1. Check trigger condition (player reaching mid-map)
        if self.state == VacaMojada.STATE_DORMANT:
            if player and player.pos.x >= self.trigger_x and player.health > 0:
                self.start_intro(player)
            return

        # 2. INTRO_IDLE State ("trava tudo")
        if self.state == VacaMojada.STATE_INTRO_IDLE:
            self.state_timer -= dt
            if self.idle_frames:
                self.current_frame_idx += 6.0 * dt
                if self.current_frame_idx >= len(self.idle_frames):
                    self.current_frame_idx %= len(self.idle_frames)
                self.surface = self.idle_frames[int(self.current_frame_idx)]

            if self.state_timer <= 0:
                self.state = VacaMojada.STATE_INTRO_START
                self.state_timer = 1.5  # Preparing phase duration (~1.5s)
                if self.prep_surface:
                    self.surface = self.prep_surface
                # Play moo SFX before starting to run!
                self.audio_manager.play_sfx("assets/audio/efeirossonoros/vaca_sfx.mp3")

        # 3. INTRO_START State (Preparing with static sprite vaca-mojada-idle-preparing.png)
        elif self.state == VacaMojada.STATE_INTRO_START:
            self.state_timer -= dt
            if self.prep_surface:
                self.surface = self.prep_surface

            if self.state_timer <= 0:
                if self.locked_player:
                    self.locked_player.unlock()
                    self.locked_player = None

                # Start first rush FROM SPAWN POSITION
                self.start_rush(camera, force_direction=-1, from_spawn=True)

        # 4. WAITING_RUSH State (Counting down 7 seconds)
        elif self.state == VacaMojada.STATE_WAITING_RUSH:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                cam_x = camera.camera_rect.x if (camera and hasattr(camera, 'camera_rect')) else (player.pos.x - 260 if player else 2000)
                cam_center = cam_x + (VIRTUAL_WIDTH // 2)
                direction = -1 if (player and player.pos.x < cam_center) else 1
                self.start_rush(camera, force_direction=direction, from_spawn=False)

        # 5. RUSHING State (Charging across screen)
        elif self.state == VacaMojada.STATE_RUSHING:
            if self.run_frames:
                self.current_frame_idx += self.run_anim_fps * dt
                if self.current_frame_idx >= len(self.run_frames):
                    self.current_frame_idx %= len(self.run_frames)
                self.surface = self.run_frames[int(self.current_frame_idx)]

            # Move horizontally & check for platform wall collisions on ground floor
            self.vel.x = self.direction * self.rush_speed
            self.pos.x += self.vel.x
            self.update_rect()

            for tile in ground_tiles:
                if tile.is_solid and self.rect.colliderect(tile.rect):
                    # Hit platform wall in front -> reverse direction instead of climbing
                    if self.direction > 0:
                        self.rect.right = tile.rect.left
                    elif self.direction < 0:
                        self.rect.left = tile.rect.right
                    self.pos.x = float(self.rect.x)
                    self.direction = -self.direction
                    break

            # Gravity & Vertical Ground Collision
            self.is_grounded = False
            self.vel.y += GRAVITY
            if self.vel.y > MAX_FALL_SPEED:
                self.vel.y = MAX_FALL_SPEED
            self.pos.y += self.vel.y
            self.update_rect()

            for tile in ground_tiles:
                if tile.is_solid and self.rect.colliderect(tile.rect):
                    if self.vel.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.pos.y = float(self.rect.y)
                        self.vel.y = 0.0
                        self.is_grounded = True

            # Ground probe to snap Y position when resting on solid top
            if not self.is_grounded and self.vel.y >= 0:
                probe_rect = self.rect.move(0, 2)
                for tile in ground_tiles:
                    if tile.is_solid and probe_rect.colliderect(tile.rect):
                        self.rect.bottom = tile.rect.top
                        self.pos.y = float(self.rect.y)
                        self.vel.y = 0.0
                        self.is_grounded = True
                        break

            # Safety check: if fell into an abyss pit below ground level (> 640px), recover automatically
            if self.pos.y > 640:
                self.state = VacaMojada.STATE_WAITING_RUSH
                self.cooldown_timer = self.rush_cooldown
                self.pos.y = 512.0
                return

            # Check for Pit / Hole ahead in direction of movement
            if self.is_grounded:
                probe_x = self.rect.left - 6 if self.direction == -1 else self.rect.right + 6
                probe_y = self.rect.bottom + 4
                probe_rect = pygame.Rect(probe_x, probe_y, 6, 12)

                has_ground_ahead = any(tile.is_solid and probe_rect.colliderect(tile.rect) for tile in ground_tiles)
                if not has_ground_ahead:
                    # Hole / pit ahead -> turn around to run off opposite side of screen
                    self.direction = -self.direction

            # Check collision with player
            if player and self.get_hitbox().colliderect(player.get_hitbox()):
                player.take_damage(self.damage)

            # Check if moved completely off screen
            cam_x = camera.camera_rect.x if (camera and hasattr(camera, 'camera_rect')) else (player.pos.x - 260 if player else 2000)
            cam_left = cam_x - 120
            cam_right = cam_x + VIRTUAL_WIDTH + 120

            if (self.direction == -1 and self.pos.x < cam_left) or (self.direction == 1 and self.pos.x > cam_right):
                # Disappear ("sumindo") and enter 7-second cooldown
                self.state = VacaMojada.STATE_WAITING_RUSH
                self.cooldown_timer = self.rush_cooldown

    def start_intro(self, player):
        """Triggers intro cutscene: locks player and displays idle -> preparing sprite."""
        self.state = VacaMojada.STATE_INTRO_IDLE
        self.state_timer = 1.8  # Idle for 1.8s
        self.current_frame_idx = 0.0
        self.locked_player = player
        player.lock()

    def start_rush(self, camera=None, force_direction: int = -1, from_spawn: bool = False):
        """Spawns Vaca Mojada either at spawn position or edge of screen, plays moo SFX, and rushes across ground."""
        self.state = VacaMojada.STATE_RUSHING
        self.direction = force_direction
        self.current_frame_idx = 0.0

        if from_spawn:
            self.pos.x = self.spawn_pos.x
            self.pos.y = self.spawn_pos.y
        else:
            cam_x = camera.camera_rect.x if (camera and hasattr(camera, 'camera_rect')) else 2000
            if self.direction == -1:
                self.pos.x = cam_x + VIRTUAL_WIDTH + 80
            else:
                self.pos.x = cam_x - 80
            self.pos.y = 512.0
            # Play moo SFX on each screen rush charge
            self.audio_manager.play_sfx("assets/audio/efeirossonoros/vaca_sfx.mp3")

        self.vel.y = 0.0
        self.update_rect()

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active or self.state == VacaMojada.STATE_DORMANT or self.state == VacaMojada.STATE_WAITING_RUSH:
            return

        screen_pos = camera.apply(self)

        # Raw sprite image (vaca-mojada-running.png, idle.png, prep.png) has head on the LEFT (x=10).
        # When moving RIGHT (direction == 1), flip horizontally so head points right.
        # When moving LEFT (direction == -1), do NOT flip so head points left.
        if self.direction == 1:
            flipped_surf = pygame.transform.flip(self.surface, True, False)
            screen.blit(flipped_surf, screen_pos)
        else:
            screen.blit(self.surface, screen_pos)

        # Show warning label above head during intro or rush
        if self.state in [VacaMojada.STATE_RUSHING, VacaMojada.STATE_INTRO_START, VacaMojada.STATE_INTRO_IDLE]:
            font = pygame.font.SysFont("arial", 12, bold=True)
            txt = font.render("VACA MOJADA!", True, (255, 69, 0))
            t_rect = txt.get_rect(center=(screen_pos.centerx, screen_pos.top - 12))
            screen.blit(txt, t_rect)
