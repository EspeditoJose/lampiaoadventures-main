"""
Dialogue Box UI Component.
Modal dialogue renderer scaled for virtual resolution.
"""

import pygame
from config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_DIALOGUE_BG,
    COLOR_DIALOGUE_BORDER, COLOR_STAMINA_YELLOW, KEY_CONFIRM
)
from src.utils.asset_loader import AssetLoader

class DialogueBox:
    def __init__(self):
        self.is_active = False
        self.speaker_name = ""
        self.pages = []
        self.current_page_idx = 0
        
        self.full_text = ""
        self.displayed_text = ""
        self.char_idx = 0.0
        self.typewriter_speed = 35.0  # characters per second
        self.is_text_complete = False

        self.on_complete_callback = None
        self.portrait_surf = None

        self.font_speaker = pygame.font.SysFont("arial", 13, bold=True)
        self.font_text = pygame.font.SysFont("arial", 11)
        self.font_prompt = pygame.font.SysFont("arial", 9, italic=True)

        self.box_rect = pygame.Rect(20, VIRTUAL_HEIGHT - 85, VIRTUAL_WIDTH - 40, 75)

    def start_dialogue(self, speaker_name: str, pages: list, on_complete=None, portrait_label: str = ""):
        """Starts a dialogue sequence."""
        self.speaker_name = speaker_name
        self.pages = pages if pages else ["..."]
        self.current_page_idx = 0
        self.on_complete_callback = on_complete
        self.is_active = True
        
        lbl = portrait_label if portrait_label else speaker_name[:4].upper()
        self.portrait_surf = AssetLoader.load_image(
            relative_path=f"assets/sprites/portraits/{speaker_name.lower().replace(' ', '_')}.png",
            size=(50, 50),
            fallback_color=(46, 139, 87),
            label=lbl
        )
        self._load_current_page()

    def _load_current_page(self):
        if 0 <= self.current_page_idx < len(self.pages):
            self.full_text = self.pages[self.current_page_idx]
            self.displayed_text = ""
            self.char_idx = 0.0
            self.is_text_complete = False
        else:
            self.close()

    def advance(self):
        """Advance typewriter text or switch to next page."""
        if not self.is_text_complete:
            self.displayed_text = self.full_text
            self.char_idx = float(len(self.full_text))
            self.is_text_complete = True
        else:
            self.current_page_idx += 1
            if self.current_page_idx < len(self.pages):
                self._load_current_page()
            else:
                self.close()

    def close(self):
        self.is_active = False
        if self.on_complete_callback:
            cb = self.on_complete_callback
            self.on_complete_callback = None
            cb()

    def handle_events(self, events):
        if not self.is_active:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_CONFIRM:
                    self.advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.box_rect.collidepoint(event.pos):
                    self.advance()

    def update(self, dt: float):
        if not self.is_active or self.is_text_complete:
            return

        self.char_idx += self.typewriter_speed * dt
        int_idx = int(self.char_idx)
        if int_idx >= len(self.full_text):
            self.displayed_text = self.full_text
            self.is_text_complete = True
        else:
            self.displayed_text = self.full_text[:int_idx]

    def render(self, screen: pygame.Surface):
        if not self.is_active:
            return

        bg_surf = pygame.Surface((self.box_rect.width, self.box_rect.height), pygame.SRCALPHA)
        bg_surf.fill(COLOR_DIALOGUE_BG)
        screen.blit(bg_surf, self.box_rect.topleft)

        pygame.draw.rect(screen, COLOR_DIALOGUE_BORDER, self.box_rect, width=2, border_radius=6)

        if self.portrait_surf:
            p_rect = self.portrait_surf.get_rect(topleft=(self.box_rect.x + 12, self.box_rect.y + 12))
            screen.blit(self.portrait_surf, p_rect)
            pygame.draw.rect(screen, COLOR_DIALOGUE_BORDER, p_rect, width=1)

        name_x = self.box_rect.x + 72
        name_txt = self.font_speaker.render(self.speaker_name, True, COLOR_STAMINA_YELLOW)
        screen.blit(name_txt, (name_x, self.box_rect.y + 8))

        pygame.draw.line(screen, (100, 100, 100), (name_x, self.box_rect.y + 24), (self.box_rect.right - 12, self.box_rect.y + 24), 1)

        text_y = self.box_rect.y + 28
        words = self.displayed_text.split(" ")
        line = ""
        max_width = self.box_rect.width - 90

        for word in words:
            test_line = line + word + " "
            if self.font_text.size(test_line)[0] > max_width:
                line_surf = self.font_text.render(line, True, COLOR_WHITE)
                screen.blit(line_surf, (name_x, text_y))
                text_y += 14
                line = word + " "
            else:
                line = test_line

        if line:
            line_surf = self.font_text.render(line, True, COLOR_WHITE)
            screen.blit(line_surf, (name_x, text_y))

        prompt_str = "Pressione [ESPAÇO] ou [E] para continuar..." if self.is_text_complete else "..."
        prompt_txt = self.font_prompt.render(prompt_str, True, (200, 200, 200))
        prompt_rect = prompt_txt.get_rect(bottomright=(self.box_rect.right - 10, self.box_rect.bottom - 6))
        screen.blit(prompt_txt, prompt_rect)
