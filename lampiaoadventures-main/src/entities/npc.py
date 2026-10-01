"""
NPC Entity.
Provides friendly NPCs with floating interaction prompt indicator, animation controllers (IDLE/PRAY),
and dialogue completion handlers (player lock, blessing animation, and HP restoration).
"""

import math
import pygame
from config import COLOR_NPC, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader

class NPC(BaseEntity):
    def __init__(self, x: float, y: float, name: str = "Zé do Chapéu", dialogue_pages: list = None, label: str = "NPC", sprite_path: str = ""):
        path = sprite_path if sprite_path else f"assets/sprites/npcs/{name.lower().replace(' ', '_')}.png"
        
        super().__init__(
            x=x, y=y, width=56, height=56,
            color=COLOR_NPC, label=label,
            sprite_path=path
        )
        self.name = name
        self.dialogue_pages = dialogue_pages if dialogue_pages else [
            "Ôente, Lampião! A Catita foi levada pelos cabras do sertão!",
            "Cuidado com os cactos e os cangaceiros no caminho!",
            "Segure [SHIFT] para correr, mas fique de olho no fôlego!"
        ]
        self.interaction_radius = 80.0
        self.anim_timer = 0.0
        self.font = pygame.font.SysFont("arial", 13, bold=True)

        # Animated NPC configuration (e.g. Bemzedor)
        self.idle_frames = None
        self.pray_frames = None
        self.anim_state = "IDLE"
        self.current_frame_idx = 0.0
        self.idle_fps = 7.0
        self.pray_fps = 8.0  # 16 frames at 8 FPS = 2.0 seconds animation
        self.locked_player = None

        name_lower = name.lower()
        path_lower = path.lower()
        label_upper = label.upper()

        # Detect if this NPC is Bemzedor or uses bemzedor sprites
        if "bemzedor" in name_lower or "bemzedor" in path_lower or "padre" in name_lower or label_upper in ["BENZEDOR", "PADRE", "BEMZEDOR"]:
            self.idle_frames = AssetLoader.load_spritesheet(
                relative_path="assets/sprites/bemzedor/bemzedor-idle.png",
                frame_width=56, frame_height=56, num_frames=7,
                colorkey=(240, 157, 231), fallback_color=COLOR_NPC, label_prefix="BEMZEDOR_IDLE"
            )
            self.pray_frames = AssetLoader.load_spritesheet(
                relative_path="assets/sprites/bemzedor/bemzedor-pray.jpeg",
                frame_width=56, frame_height=56, num_frames=16,
                colorkey=(126, 126, 126), fallback_color=COLOR_NPC, label_prefix="BEMZEDOR_PRAY"
            )
            if self.idle_frames:
                self.surface = self.idle_frames[0]

    def update(self, dt: float, tiles: list, player=None):
        if not self.is_active:
            return
        self.anim_timer += dt

        # Update animation state machine if sprite frames are present
        if self.idle_frames:
            if self.anim_state == "PRAY" and self.pray_frames:
                self.current_frame_idx += self.pray_fps * dt
                if self.current_frame_idx >= len(self.pray_frames):
                    # End pray animation and unlock player
                    self.anim_state = "IDLE"
                    self.current_frame_idx = 0.0
                    if self.locked_player:
                        self.locked_player.unlock()
                        self.locked_player = None
                    self.surface = self.idle_frames[0]
                else:
                    frame_i = int(self.current_frame_idx)
                    self.surface = self.pray_frames[min(frame_i, len(self.pray_frames) - 1)]
            else:
                # IDLE state
                self.current_frame_idx += self.idle_fps * dt
                if self.current_frame_idx >= len(self.idle_frames):
                    self.current_frame_idx %= len(self.idle_frames)
                self.surface = self.idle_frames[int(self.current_frame_idx)]

    def on_dialogue_complete(self, player=None):
        """Called when NPC dialogue ends. Starts pray blessing, freezes player, and heals HP."""
        if self.pray_frames and player:
            self.anim_state = "PRAY"
            self.current_frame_idx = 0.0
            self.locked_player = player
            player.lock()
            
            # Heal player by ~35% of max health
            heal_amount = int(player.max_health * 0.35)
            player.heal(heal_amount)

    def is_player_near(self, player) -> bool:
        """Returns True if player is inside interaction radius."""
        return self.pos.distance_to(player.pos) <= self.interaction_radius

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        super().render(screen, camera)

    def render_prompt(self, screen: pygame.Surface, camera):
        """Renders floating 'Press [E] to talk' prompt above NPC if not in middle of pray animation."""
        if not self.is_active or self.anim_state == "PRAY":
            return

        screen_pos = camera.apply(self)
        
        # Subtle up/down bobbing animation
        bounce_offset = int(math.sin(self.anim_timer * 5.0) * 4.0)
        
        prompt_txt = self.font.render("[E] Falar", True, COLOR_STAMINA_YELLOW)
        shadow_txt = self.font.render("[E] Falar", True, COLOR_BLACK)
        
        rect = prompt_txt.get_rect(center=(screen_pos.centerx, screen_pos.top - 16 + bounce_offset))
        
        # Draw background pill
        bg_rect = rect.inflate(12, 6)
        pygame.draw.rect(screen, (30, 30, 35, 200), bg_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_STAMINA_YELLOW, bg_rect, width=1, border_radius=4)
        
        screen.blit(shadow_txt, (rect.x + 1, rect.y + 1))
        screen.blit(prompt_txt, rect)

