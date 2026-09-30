"""
HUD (Heads-Up Display) UI Component.
Displays Health Bar, Sprint Stamina Bar, and Collectible Counter scaled for virtual resolution.
"""

import pygame
from config import (
    COLOR_HEALTH_GREEN, COLOR_HEALTH_RED, COLOR_STAMINA_BLUE, COLOR_STAMINA_YELLOW,
    COLOR_WHITE, COLOR_BLACK, COLOR_DARK_GRAY, COLOR_DIALOGUE_BORDER, VIRTUAL_WIDTH
)

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 11, bold=True)
        self.small_font = pygame.font.SysFont("arial", 9, bold=True)

    def render(self, screen: pygame.Surface, player):
        """Renders HUD overlays at top of screen."""
        hud_bg = pygame.Rect(8, 8, 220, 58)
        
        # Background Panel
        panel_surf = pygame.Surface((hud_bg.width, hud_bg.height), pygame.SRCALPHA)
        panel_surf.fill((20, 20, 25, 210))
        screen.blit(panel_surf, hud_bg.topleft)
        pygame.draw.rect(screen, COLOR_DIALOGUE_BORDER, hud_bg, width=1, border_radius=4)

        # ----------------------------------------------------
        # 1. HEALTH BAR (Green/Red)
        # ----------------------------------------------------
        hp_ratio = max(0.0, min(1.0, player.health / player.max_health))
        bar_x, bar_y = 60, 14
        bar_w, bar_h = 155, 11

        lbl_hp = self.font.render("VIDA:", True, COLOR_WHITE)
        screen.blit(lbl_hp, (14, bar_y - 2))

        pygame.draw.rect(screen, COLOR_HEALTH_RED, (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        if hp_ratio > 0:
            pygame.draw.rect(screen, COLOR_HEALTH_GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=2)
        pygame.draw.rect(screen, COLOR_WHITE, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=2)

        hp_txt = self.small_font.render(f"{player.health}/{player.max_health}", True, COLOR_WHITE)
        txt_rect = hp_txt.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        screen.blit(hp_txt, txt_rect)

        # ----------------------------------------------------
        # 2. SPRINT STAMINA BAR (Blue/Yellow)
        # ----------------------------------------------------
        stamina_ratio = max(0.0, min(1.0, player.stamina / player.max_stamina))
        s_bar_y = 30

        lbl_stm = self.font.render("FÔLEGO:", True, COLOR_WHITE)
        screen.blit(lbl_stm, (14, s_bar_y - 2))

        pygame.draw.rect(screen, COLOR_DARK_GRAY, (bar_x, s_bar_y, bar_w, bar_h), border_radius=2)
        stamina_color = COLOR_STAMINA_YELLOW if player.is_exhausted else COLOR_STAMINA_BLUE
        if stamina_ratio > 0:
            pygame.draw.rect(screen, stamina_color, (bar_x, s_bar_y, int(bar_w * stamina_ratio), bar_h), border_radius=2)
        pygame.draw.rect(screen, COLOR_WHITE, (bar_x, s_bar_y, bar_w, bar_h), width=1, border_radius=2)

        stm_str = "EXAUSTO!" if player.is_exhausted else f"{int(player.stamina)}%"
        stm_txt = self.small_font.render(stm_str, True, COLOR_WHITE)
        stm_rect = stm_txt.get_rect(center=(bar_x + bar_w // 2, s_bar_y + bar_h // 2))
        screen.blit(stm_txt, stm_rect)

        # ----------------------------------------------------
        # 3. CATITAS / COINS COUNTER
        # ----------------------------------------------------
        coin_lbl = self.small_font.render(f"CATITAS COLETADAS: {player.coins_collected}", True, (255, 215, 0))
        screen.blit(coin_lbl, (14, 46))
