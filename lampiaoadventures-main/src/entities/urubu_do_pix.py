"""
Urubu do Pix Flying Scene Entity.
Triggers after a delay of a few seconds, flying across the very top of the player's screen
playing "É o Pix!", and then permanently disappears.
"""

import pygame
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader
from src.core.audio_manager import AudioManager
from config import VIRTUAL_WIDTH

class UrubuDoPix(BaseEntity):
    def __init__(self, delay_seconds: float = 4.5, fly_speed: float = 160.0):
        # 32x32 frame box for flying Urubu at the top of the screen
        super().__init__(
            x=-500.0, y=20.0, width=32, height=32,
            color=(40, 40, 40), label="URUBU_PIX",
            sprite_path="assets/sprites/urubu-do-pix.png"
        )
        self.delay_timer = delay_seconds
        self.fly_speed = fly_speed
        self.audio_manager = AudioManager()

        # Timers and state
        self.current_frame_idx = 0.0
        self.anim_fps = 10.0
        self.is_triggered = False
        self.has_played_sound = False
        self.has_finished = False

        # Load 3-frame 32x32 spritesheet with colorkey (127, 127, 127)
        self.frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/urubu-do-pix.png",
            frame_width=32, frame_height=32, num_frames=3,
            colorkey=(127, 127, 127), fallback_color=(40, 40, 40), label_prefix="URUBU"
        )

        if self.frames:
            self.surface = self.frames[0]

    def update(self, dt: float, player=None, camera=None, level_width: float = 6000.0):
        if not self.is_active or self.has_finished:
            return

        # Countdown delay timer before spawning (wait a few seconds into the game)
        if not self.is_triggered:
            self.delay_timer -= dt
            if self.delay_timer <= 0:
                self.is_triggered = True
                cam_x = camera.camera_rect.x if (camera and hasattr(camera, 'camera_rect')) else (player.pos.x - 200 if player else 0)
                cam_y = camera.camera_rect.y if (camera and hasattr(camera, 'camera_rect')) else 350.0

                # Start at the top of the player's screen (y = cam_y + 20)
                self.pos.x = cam_x - 50.0
                self.pos.y = cam_y + 20.0
                self.update_rect()

                # Play "É o Pix!" sound effect ONCE when appearing
                self.audio_manager.play_sfx("assets/audio/efeirossonoros/eopix.mp3")
                self.has_played_sound = True
            return

        # Animate wing flapping
        if self.frames:
            self.current_frame_idx += self.anim_fps * dt
            if self.current_frame_idx >= len(self.frames):
                self.current_frame_idx %= len(self.frames)
            self.surface = self.frames[int(self.current_frame_idx)]

        # Move horizontally across the screen, locked to top of camera
        cam_x = camera.camera_rect.x if (camera and hasattr(camera, 'camera_rect')) else (self.pos.x - VIRTUAL_WIDTH)
        cam_y = camera.camera_rect.y if (camera and hasattr(camera, 'camera_rect')) else (self.pos.y - 20.0)

        self.pos.x += self.fly_speed * dt
        self.pos.y = cam_y + 20.0  # Always strictly at top of player's screen
        self.update_rect()

        # Check if crossed off screen right
        if self.pos.x > cam_x + VIRTUAL_WIDTH + 60:
            self.is_active = False
            self.has_finished = True

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active or self.has_finished or not self.is_triggered:
            return

        screen_pos = camera.apply(self)
        screen.blit(self.surface, screen_pos)
