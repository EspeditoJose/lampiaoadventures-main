"""
Main Menu UI Component for Lampião Adventures.
Renders background image, crisp black text with light outlines, image-based interactive buttons
from assets/botoes/ with accurate virtual mouse detection, smooth pulsing animation,
and auto-resolving/auto-resuming audio player for BGM/SFX from src/audio/.
"""

import math
import os
import sys
import pygame

# Detecta dinamicamente a pasta raiz do projeto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.config import (
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW,
        COLOR_SUN, COLOR_GROUND, COLOR_DIALOGUE_BORDER
    )
except ModuleNotFoundError:
    from config import (
        VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW,
        COLOR_SUN, COLOR_GROUND, COLOR_DIALOGUE_BORDER
    )


def find_audio_file(search_dirs: list, file_stem: str) -> str:
    """Procura recursivamente por um arquivo de áudio com o nome base em múltiplos diretórios."""
    for root_dir in search_dirs:
        if not os.path.exists(root_dir):
            continue
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                name_without_ext, ext = os.path.splitext(f)
                if name_without_ext.lower() == file_stem.lower() and ext.lower() in ['.mp3', '.wav', '.ogg']:
                    return os.path.join(dirpath, f)
    return None


def get_font(path: str, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """Carrega fonte customizada do projeto ou recorre à fonte do sistema caso o arquivo não exista."""
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError, TypeError):
        return pygame.font.SysFont("arial", size, bold=bold, italic=italic)


def render_crisp_text(font_2x: pygame.font.Font, text: str, color: tuple) -> pygame.Surface:
    """Renderiza o texto em resolução dupla e aplica smoothscale para evitar serrilhado no dimensionamento."""
    large_surf = font_2x.render(text, True, color)
    w, h = large_surf.get_size()
    return pygame.transform.smoothscale(large_surf, (max(1, w // 2), max(1, h // 2)))


class MenuButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action, img_name: str, sfx=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.sfx = sfx
        self.is_hovered = False

        # Carregamento da imagem do botão na pasta assets/botoes/
        self.raw_img = None
        self.img_normal = None

        botoes_dir = os.path.join(PROJECT_ROOT, "assets", "botoes")
        valid_exts = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

        for ext in valid_exts:
            img_path = os.path.join(botoes_dir, f"{img_name}{ext}")
            if os.path.exists(img_path):
                try:
                    self.raw_img = pygame.image.load(img_path).convert_alpha()
                    self.img_normal = pygame.transform.smoothscale(self.raw_img, (width, height))
                    print(f"[MenuButton] Imagem do botão '{img_name}' carregada com sucesso.")
                    break
                except Exception as e:
                    print(f"[MenuButton] Erro ao carregar {img_path}: {e}")

        # Fonte reserva para fallback vetorial
        font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "cangaco_font.ttf")
        self.font_2x = get_font(font_path, 26, bold=True)

    def trigger_action(self):
        """Reproduz o efeito sonoro, para a música de fundo se for iniciar, e aplica delays adequados."""
        is_iniciar = "INICIAR" in self.text.upper()
        is_sair = "SAIR" in self.text.upper()

        # Parar a música de fundo ao clicar em INICIAR
        if is_iniciar:
            try:
                pygame.mixer.music.stop()
                print("[MenuButton] Música de fundo parada ao iniciar o jogo.")
            except Exception as e:
                print(f"[MenuButton] Erro ao parar música de fundo: {e}")

        # Reprodução do efeito sonoro
        if self.sfx:
            try:
                channel = self.sfx.play()
                if is_sair:
                    if channel:
                        start_wait = pygame.time.get_ticks()
                        while channel.get_busy() and (pygame.time.get_ticks() - start_wait < 3000):
                            pygame.time.wait(10)
                    pygame.time.wait(500)  # Meio segundo extra para ouvir o SFX completo
                else:
                    pygame.time.wait(150)
            except Exception as e:
                print(f"[MenuButton] Erro ao reproduzir SFX: {e}")

        if self.action:
            self.action()

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, screen: pygame.Surface, anim_timer: float = 0.0):
        if self.raw_img and self.img_normal:
            if self.is_hovered:
                pulse_scale = 1.06 + 0.06 * math.sin(anim_timer * 7.0)
                pulse_w = max(1, int(self.rect.width * pulse_scale))
                pulse_h = max(1, int(self.rect.height * pulse_scale))

                scaled_img = pygame.transform.smoothscale(self.raw_img, (pulse_w, pulse_h))
                img_rect = scaled_img.get_rect(center=self.rect.center)
                screen.blit(scaled_img, img_rect)
            else:
                img_rect = self.img_normal.get_rect(center=self.rect.center)
                screen.blit(self.img_normal, img_rect)
        else:
            bg_color = (200, 100, 30) if self.is_hovered else (40, 40, 45)
            border_color = COLOR_STAMINA_YELLOW if self.is_hovered else (100, 100, 100)

            if self.is_hovered:
                pulse_scale = 1.06 + 0.06 * math.sin(anim_timer * 7.0)
                pulse_w = max(1, int(self.rect.width * pulse_scale))
                pulse_h = max(1, int(self.rect.height * pulse_scale))
                draw_rect = pygame.Rect(0, 0, pulse_w, pulse_h)
                draw_rect.center = self.rect.center
            else:
                draw_rect = self.rect

            shadow_rect = draw_rect.move(2, 2)
            pygame.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=4)
            pygame.draw.rect(screen, bg_color, draw_rect, border_radius=4)
            pygame.draw.rect(screen, border_color, draw_rect, width=2, border_radius=4)

            txt_color = COLOR_WHITE if self.is_hovered else (220, 220, 220)
            txt_surf = render_crisp_text(self.font_2x, self.text, txt_color)
            txt_rect = txt_surf.get_rect(center=draw_rect.center)
            screen.blit(txt_surf, txt_rect)


class MenuUI:
    def __init__(self, start_callback, quit_callback):
        self.start_callback = start_callback
        self.quit_callback = quit_callback

        # 1. Re-inicializa o mixer de áudio
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            print("[MenuUI] Sistema de áudio (Pygame Mixer) inicializado em 44.1kHz.")
        except Exception as e:
            print(f"[MenuUI] Erro ao inicializar mixer de áudio: {e}")

        # 2. Caminho da música de fundo e efeitos sonoros
        self.bgm_path = None
        self.sfx_iniciar = None
        self.sfx_sair = None

        self.init_audio()

        # 3. Carrega a imagem de fundo de assets/imagensFundo/
        self.bg_image = None
        folder = os.path.join(PROJECT_ROOT, "assets", "imagensFundo")
        possible_files = [
            "menuPrincipal.png",
            "menuPrincipal.jpg",
            "menuPrincipal.jpeg",
            "menuPrincipal.webp",
            "menuPrincipal.bmp"
        ]

        for filename in possible_files:
            img_path = os.path.join(folder, filename)
            if os.path.exists(img_path):
                try:
                    raw_bg = pygame.image.load(img_path).convert()
                    self.bg_image = pygame.transform.scale(raw_bg, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                    print(f"[MenuUI] Imagem de fundo carregada com sucesso: {filename}")
                    break
                except Exception as e:
                    print(f"[MenuUI] Erro ao carregar {img_path}: {e}")

        # 4. Inicialização das fontes
        font_path = os.path.join(PROJECT_ROOT, "assets", "fonts", "cangaco_font.ttf")
        self.font_subtitle_2x = get_font(font_path, 24, italic=True)
        self.font_footer_2x = get_font(font_path, 20)

        # 5. Criação dos Botões com imagens e efeitos sonoros
        btn_w, btn_h = 180, 34
        center_x = VIRTUAL_WIDTH // 2 - btn_w // 2

        self.buttons = [
            MenuButton(center_x, 145, btn_w, btn_h, "[1] INICIAR JOGO", start_callback, "iniciar", self.sfx_iniciar),
            MenuButton(center_x, 190, btn_w, btn_h, "[2] SAIR DO JOGO", quit_callback, "sair", self.sfx_sair)
        ]

        self.selected_idx = 0
        self.anim_timer = 0.0

    def init_audio(self):
        """Procura, carrega e ajusta os caminhos e volumes de áudio."""
        search_dirs = [
            os.path.join(PROJECT_ROOT, "src", "audio"),
            os.path.join(PROJECT_ROOT, "audio"),
            os.path.join(PROJECT_ROOT, "assets", "audio")
        ]

        # A) Caminho da Música de Fundo
        self.bgm_path = find_audio_file(search_dirs, "menuInicial")

        # B) SFX Iniciar (Volume: 1.0)
        sfx_iniciar_path = find_audio_file(search_dirs, "iniciar")
        if sfx_iniciar_path:
            try:
                self.sfx_iniciar = pygame.mixer.Sound(sfx_iniciar_path)
                self.sfx_iniciar.set_volume(1.0)
            except Exception as e:
                print(f"[MenuUI] Erro ao carregar SFX iniciar: {e}")

        # C) SFX Sair (Volume: 1.0)
        sfx_sair_path = find_audio_file(search_dirs, "sair")
        if sfx_sair_path:
            try:
                self.sfx_sair = pygame.mixer.Sound(sfx_sair_path)
                self.sfx_sair.set_volume(1.0)
            except Exception as e:
                print(f"[MenuUI] Erro ao carregar SFX sair: {e}")

        # Inicia a música de fundo
        self.play_bgm()

    def play_bgm(self):
        """Garante a reprodução da música de fundo caso não esteja tocando."""
        if self.bgm_path and not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                print(f"[MenuUI] Música de fundo iniciada: {self.bgm_path}")
            except Exception as e:
                print(f"[MenuUI] Erro ao reproduzir música de fundo: {e}")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.buttons:
                    if btn.is_hovered:
                        btn.trigger_action()

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_RETURN, pygame.K_SPACE]:
                    self.buttons[0].trigger_action()
                elif event.key in [pygame.K_2, pygame.K_ESCAPE]:
                    self.buttons[1].trigger_action()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_idx = (self.selected_idx - 1) % len(self.buttons)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_idx = (self.selected_idx + 1) % len(self.buttons)

    def update(self, dt: float):
        self.anim_timer += dt

        # Garante que ao estar no menu, a música de fundo continue/volte a tocar se esteve parada
        self.play_bgm()

        raw_mouse = pygame.mouse.get_pos()
        display_surf = pygame.display.get_surface()
        if display_surf and display_surf.get_width() > 0 and display_surf.get_height() > 0:
            dw, dh = display_surf.get_size()
            virtual_mouse = (
                raw_mouse[0] * (VIRTUAL_WIDTH / dw),
                raw_mouse[1] * (VIRTUAL_HEIGHT / dh)
            )
        else:
            virtual_mouse = raw_mouse

        mouse_over_any = False
        for i, btn in enumerate(self.buttons):
            btn.update(virtual_mouse)
            if btn.is_hovered:
                self.selected_idx = i
                mouse_over_any = True

        if not mouse_over_any:
            for i, btn in enumerate(self.buttons):
                btn.is_hovered = (i == self.selected_idx)

    def render(self, screen: pygame.Surface):
        # 1. Renderização do Fundo
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill((255, 218, 185))
            sun_y = int(90 + math.sin(self.anim_timer * 0.8) * 5)
            pygame.draw.circle(screen, COLOR_SUN, (VIRTUAL_WIDTH // 2, sun_y), 65)
            pygame.draw.rect(screen, COLOR_GROUND, (0, 240, VIRTUAL_WIDTH, 60))

        # 2. Subtítulo (Texto em PRETO com borda nítida clara)
        sub_text_str = "A Busca da Catita Perdida no Sertão"
        sub_txt = render_crisp_text(self.font_subtitle_2x, sub_text_str, COLOR_BLACK)
        sub_outline = render_crisp_text(self.font_subtitle_2x, sub_text_str, COLOR_WHITE)
        sub_rect = sub_txt.get_rect(center=(VIRTUAL_WIDTH // 2, 115))

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]:
            screen.blit(sub_outline, (sub_rect.x + dx, sub_rect.y + dy))
        screen.blit(sub_txt, sub_rect)

        # 3. Botões
        for btn in self.buttons:
            btn.render(screen, self.anim_timer)

        # 4. Rodapé Informativo (Texto em PRETO com borda nítida clara)
        footer_text_str = "Use MOUSE ou TECLAS [1] / [2] / [ENTER] para navegar"
        footer_txt = render_crisp_text(self.font_footer_2x, footer_text_str, COLOR_BLACK)
        footer_outline = render_crisp_text(self.font_footer_2x, footer_text_str, COLOR_WHITE)
        f_rect = footer_txt.get_rect(center=(VIRTUAL_WIDTH // 2, 282))

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]:
            screen.blit(footer_outline, (f_rect.x + dx, f_rect.y + dy))
        screen.blit(footer_txt, f_rect)