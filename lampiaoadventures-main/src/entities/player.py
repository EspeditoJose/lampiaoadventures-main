"""
Player Entity & Animation State Controller.
Handles physics, platforming controls, stamina sprint, health & invulnerability,
and robust animation state machine for IDLE (6f), RUN (5f), JUMP (5f trajectory), and SHOOT (7f).
"""

import pygame
from config import (
    COLOR_PLAYER, GRAVITY, MAX_FALL_SPEED, PLAYER_SPEED, PLAYER_SPRINT_SPEED,
    PLAYER_JUMP_FORCE, MAX_HEALTH, MAX_STAMINA, STAMINA_DRAIN, STAMINA_RECHARGE,
    KEY_LEFT, KEY_RIGHT, KEY_JUMP, KEY_SPRINT, KEY_INTERACT, KEY_SHOOT
)
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader
from src.core.audio_manager import AudioManager

class Player(BaseEntity):
    def __init__(self, x: float, y: float):
        # Ground-aligned 56x56 frame box
        super().__init__(
            x=x, y=y, width=56, height=56,
            color=COLOR_PLAYER, label="LAMPIÃO",
            sprite_path="assets/sprites/player/lampiaozito-idle.png"
        )
        self.health = MAX_HEALTH
        self.max_health = MAX_HEALTH

        self.stamina = MAX_STAMINA
        self.max_stamina = MAX_STAMINA
        self.is_sprinting = False
        self.is_exhausted = False

        self.coins_collected = 0
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 1.0  # seconds

        # Movement fine-tuning
        self.coyote_timer = 0.0
        self.coyote_time_max = 0.15
        self.jump_buffer = 0.0
        self.jump_buffer_max = 0.15

        self.audio_manager = AudioManager()
        self.interact_pressed = False
        self.shoot_timer = 0.0
        self.shoot_duration = 0.35  # seconds for shooting animation override

        # ----------------------------------------------------
        # ANIMATION SPRITE SHEETS & COLORKEYS
        # ----------------------------------------------------
        # 1. IDLE SHEET: 336x56 px (6 frames, 56x56, Magenta colorkey 227,119,218)
        self.idle_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/player/lampiaozito-idle.png",
            frame_width=56, frame_height=56, num_frames=6,
            colorkey=(227, 119, 218), fallback_color=COLOR_PLAYER, label_prefix="IDLE"
        )

        # 2. RUN CYCLE SHEET: 280x56 px (5 frames, 56x56, Gray colorkey 127,127,127)
        self.run_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/player/lampiaozito-runcycle.png",
            frame_width=56, frame_height=56, num_frames=5,
            colorkey=(127, 127, 127), fallback_color=COLOR_PLAYER, label_prefix="RUN"
        )

        # 3. JUMP SHEET: 280x56 px (5 frames, 56x56, Gray colorkey 127,127,127)
        self.jump_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/player/lampiaozito-jump.png",
            frame_width=56, frame_height=56, num_frames=5,
            colorkey=(127, 127, 127), fallback_color=COLOR_PLAYER, label_prefix="JUMP"
        )

        # 4. SHOOTING WALK SHEET: 392x56 px (7 frames, 56x56, Gray colorkey 126,126,126)
        self.shoot_frames = AssetLoader.load_spritesheet(
            relative_path="assets/sprites/player/lampiaozito-shooting-walk.png",
            frame_width=56, frame_height=56, num_frames=7,
            colorkey=(126, 126, 126), fallback_color=COLOR_PLAYER, label_prefix="SHOOT"
        )

        # Animation State Tracker
        self.anim_state = "IDLE"
        self.current_frame_idx = 0.0
        self.idle_anim_fps = 7.0
        self.run_anim_fps = 10.0
        self.shoot_anim_fps = 16.0

    def handle_input(self, events):
        """Processes key presses for jump buffer, interaction, and shooting trigger."""
        self.interact_pressed = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_JUMP:
                    self.jump_buffer = self.jump_buffer_max
                if event.key in KEY_INTERACT:
                    self.interact_pressed = True
                if event.key in KEY_SHOOT:
                    self.shoot_timer = self.shoot_duration
                    self.audio_manager.play_sfx("assets/audio/sfx/shoot.wav")

    def update(self, dt: float, tiles: list):
        if not self.is_active:
            return

        keys = pygame.key.get_pressed()

        # Update Timers
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.shoot_timer > 0:
            self.shoot_timer = max(0.0, self.shoot_timer - dt)

        # Sprint logic & Stamina Drain / Recharge
        sprint_requested = any(keys[k] for k in KEY_SPRINT)
        moving_horizontally = any(keys[k] for k in KEY_LEFT) or any(keys[k] for k in KEY_RIGHT)

        if sprint_requested and moving_horizontally and not self.is_exhausted and self.stamina > 0:
            self.is_sprinting = True
            self.stamina = max(0.0, self.stamina - STAMINA_DRAIN)
            if self.stamina <= 0:
                self.is_exhausted = True
                self.is_sprinting = False
        else:
            self.is_sprinting = False
            if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina, self.stamina + STAMINA_RECHARGE)
                if self.is_exhausted and self.stamina >= 25.0:
                    self.is_exhausted = False  # Recovered enough stamina to sprint again

        # Horizontal Movement Speed
        current_speed = PLAYER_SPRINT_SPEED if self.is_sprinting else PLAYER_SPEED

        # Direction Input
        self.vel.x = 0
        if any(keys[k] for k in KEY_LEFT):
            self.vel.x = -current_speed
            self.facing = "left"
        if any(keys[k] for k in KEY_RIGHT):
            self.vel.x = current_speed
            self.facing = "right"

        # Horizontal Position Update & Collision Resolution
        self.pos.x += self.vel.x
        self.update_rect()
        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                self.pos.x = self.rect.x

        # Gravity & Jump Timers
        if self.is_grounded:
            self.coyote_timer = self.coyote_time_max
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if self.jump_buffer > 0:
            self.jump_buffer = max(0.0, self.jump_buffer - dt)

        # Execute Jump if buffer and ground/coyote available
        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.vel.y = PLAYER_JUMP_FORCE
            self.is_grounded = False
            self.coyote_timer = 0
            self.jump_buffer = 0
            self.audio_manager.play_sfx("assets/audio/sfx/jump.wav")

        # Apply Gravity
        self.vel.y += GRAVITY
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

        # Vertical Position Update & Collision Resolution
        self.pos.y += self.vel.y
        self.update_rect()
        self.is_grounded = False

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.y > 0:  # Falling down onto surface
                    self.rect.bottom = tile.rect.top
                    self.pos.y = float(self.rect.y)
                    self.vel.y = 0.0
                    self.is_grounded = True
                elif self.vel.y < 0:  # Hitting ceiling
                    self.rect.top = tile.rect.bottom
                    self.pos.y = float(self.rect.y)
                    self.vel.y = 0.0

        # Ground Probe check (prevents 1-pixel sub-pixel boundary flickering)
        if not self.is_grounded and self.vel.y >= 0:
            probe_rect = self.rect.move(0, 2)
            for tile in tiles:
                if tile.is_solid and probe_rect.colliderect(tile.rect):
                    self.is_grounded = True
                    self.vel.y = 0.0
                    break

        # Update Animation Controller State Machine
        self._update_animation(dt)

    def _update_animation(self, dt: float):
        """
        Updates animation state machine:
        - SHOOT: Active when shoot_timer > 0 (overrides idle/run).
        - AIRBORNE / JUMP: Active when not self.is_grounded AND coyote_timer <= 0.
        - RUN: Active when grounded and moving horizontally (vel.x != 0).
        - IDLE: Active when grounded and stationary (vel.x == 0).
        """
        # 1. SHOOTING WALK STATE OVERRIDE (only when moving/walking)
        if self.shoot_timer > 0 and abs(self.vel.x) > 0.1:
            if self.anim_state != "SHOOT":
                self.anim_state = "SHOOT"
                self.current_frame_idx = 0.0

            self.current_frame_idx += self.shoot_anim_fps * dt
            if self.current_frame_idx >= len(self.shoot_frames):
                self.current_frame_idx %= len(self.shoot_frames)
            
            frame = self.shoot_frames[int(self.current_frame_idx)]

        # 2. AIRBORNE / JUMP STATE (only when truly off ground and coyote time expired)
        elif not self.is_grounded and self.coyote_timer <= 0:
            if self.anim_state != "JUMP":
                self.anim_state = "JUMP"

            # Map frame based on vertical trajectory vel.y
            if self.vel.y < -8.0:
                frame_idx = 0  # Fast upward impulse
            elif self.vel.y < -2.0:
                frame_idx = 1  # Rising curve
            elif self.vel.y <= 2.0:
                frame_idx = 2  # Jump apex / peak
            elif self.vel.y <= 8.0:
                frame_idx = 3  # Falling
            else:
                frame_idx = 4  # Fast descent / landing pre-touchdown

            frame = self.jump_frames[min(frame_idx, len(self.jump_frames) - 1)]

        # 3. RUNNING STATE
        elif abs(self.vel.x) > 0.1:
            if self.anim_state != "RUN":
                self.anim_state = "RUN"
                self.current_frame_idx = 0.0

            speed_ratio = abs(self.vel.x) / PLAYER_SPEED
            playback_fps = self.run_anim_fps * speed_ratio
            self.current_frame_idx += playback_fps * dt

            if self.current_frame_idx >= len(self.run_frames):
                self.current_frame_idx %= len(self.run_frames)

            frame = self.run_frames[int(self.current_frame_idx)]

        # 4. IDLE STATE
        else:
            if self.anim_state != "IDLE":
                self.anim_state = "IDLE"
                self.current_frame_idx = 0.0

            self.current_frame_idx += self.idle_anim_fps * dt
            if self.current_frame_idx >= len(self.idle_frames):
                self.current_frame_idx %= len(self.idle_frames)

            frame = self.idle_frames[int(self.current_frame_idx)]

        # Set active rendering surface
        self.surface = frame

    def take_damage(self, amount: int):
        """Reduces HP and applies invulnerability frames."""
        if self.invulnerable_timer <= 0 and self.health > 0:
            self.health = max(0, self.health - amount)
            self.invulnerable_timer = self.invulnerable_duration
            self.audio_manager.play_sfx("assets/audio/sfx/hurt.wav")
            # Slight recoil boost upwards
            self.vel.y = -6.0

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def render(self, screen: pygame.Surface, camera):
        """Render player with visual flicker during invulnerability and horizontal flipping."""
        if not self.is_active:
            return

        # Flicker effect when invulnerable
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 15) % 2 == 0:
                return

        screen_rect = camera.apply(self)

        # Apply horizontal flip when facing left
        if self.facing == "left":
            flipped_surf = pygame.transform.flip(self.surface, True, False)
            screen.blit(flipped_surf, screen_rect)
        else:
            screen.blit(self.surface, screen_rect)
