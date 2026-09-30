"""
NPC Entity.
Provides friendly NPCs with floating interaction prompt indicator and dialogue script triggers.
"""

import math
import pygame
from config import COLOR_NPC, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW
from src.entities.base_entity import BaseEntity

class NPC(BaseEntity):
    def __init__(self, x: float, y: float, name: str = "Zé do Chapéu", dialogue_pages: list = None, label: str = "NPC"):
        super().__init__(
            x=x, y=y, width=40, height=56,
            color=COLOR_NPC, label=label,
            sprite_path=f"assets/sprites/npcs/{name.lower().replace(' ', '_')}.png"
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

    def update(self, dt: float, tiles: list):
        if not self.is_active:
            return
        self.anim_timer += dt

    def is_player_near(self, player) -> bool:
        """Returns True if player is inside interaction radius."""
        return self.pos.distance_to(player.pos) <= self.interaction_radius

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        super().render(screen, camera)

    def render_prompt(self, screen: pygame.Surface, camera):
        """Renders floating 'Press [E] to talk' prompt above NPC."""
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
