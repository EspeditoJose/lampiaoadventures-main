"""
Catita Entity (Objective at the end of the map).
Rendered at the finish line with an animated bouncing arrow pointing down at her head.
Allows player interaction with [E] key to complete the game and return to menu.
"""

import math
import pygame
from src.entities.base_entity import BaseEntity
from src.utils.asset_loader import AssetLoader

class Catita(BaseEntity):
    def __init__(self, x: float = 7150.0, y: float = 544.0):
        # 32x32 ground aligned box resting at y=544 (rect.bottom=576px)
        super().__init__(
            x=x, y=y, width=32, height=32,
            color=(255, 182, 193), label="CATITA",
            sprite_path="assets/sprites/catita.png"
        )
        self.surface = AssetLoader.load_image("assets/sprites/catita.png", (32, 32))
        self.arrow_timer = 0.0

    def is_player_near(self, player, distance: float = 60.0) -> bool:
        if not player or not player.is_active:
            return False
        return self.pos.distance_to(player.pos) <= distance

    def update(self, dt: float):
        self.arrow_timer += 6.0 * dt

    def render(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        screen_pos = camera.apply(self)
        screen.blit(self.surface, screen_pos)

        # Draw bouncing arrow pointing down at Catita
        bounce = math.sin(self.arrow_timer) * 4.0
        arrow_bottom_y = screen_pos.top - 6 + bounce
        arrow_center_x = screen_pos.centerx

        # Gold arrow pointing down
        p1 = (arrow_center_x, arrow_bottom_y)
        p2 = (arrow_center_x - 7, arrow_bottom_y - 12)
        p3 = (arrow_center_x + 7, arrow_bottom_y - 12)

        pygame.draw.polygon(screen, (255, 215, 0), [p1, p2, p3])
        pygame.draw.polygon(screen, (200, 50, 0), [p1, p2, p3], width=2)

        # Label above arrow
        font = pygame.font.SysFont("arial", 12, bold=True)
        txt = font.render("CATITA!", True, (255, 235, 100))
        t_rect = txt.get_rect(center=(arrow_center_x, arrow_bottom_y - 22))
        screen.blit(txt, t_rect)

    def render_prompt(self, screen: pygame.Surface, camera):
        if not self.is_active:
            return

        screen_pos = camera.apply(self)
        font = pygame.font.SysFont("arial", 12, bold=True)
        prompt_txt = font.render("[E] RESGATAR CATITA", True, (255, 215, 0))
        
        cx = screen_pos.centerx
        top_y = screen_pos.top - 48
        
        bg_rect = prompt_txt.get_rect(center=(cx, top_y))
        box_rect = bg_rect.inflate(16, 8)

        # Draw speech balloon box
        pygame.draw.rect(screen, (20, 20, 30), box_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
        
        # Draw balloon pointer tail pointing down to Catita
        tail_p1 = (cx - 6, box_rect.bottom)
        tail_p2 = (cx + 6, box_rect.bottom)
        tail_p3 = (cx, box_rect.bottom + 8)
        pygame.draw.polygon(screen, (20, 20, 30), [tail_p1, tail_p2, tail_p3])
        pygame.draw.polygon(screen, (255, 215, 0), [tail_p1, tail_p2, tail_p3], width=1)

        screen.blit(prompt_txt, bg_rect)
