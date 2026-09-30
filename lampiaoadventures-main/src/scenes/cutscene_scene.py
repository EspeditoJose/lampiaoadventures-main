"""
Cutscene Scene Framework.
Plays intro/story cutscenes with animated props and sequential dialogue pages scaled for virtual resolution.
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
    from src.config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, KEY_CONFIRM
except ModuleNotFoundError:
    from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, KEY_CONFIRM

from src.scenes.base_scene import BaseScene
from src.ui.dialogue_box import DialogueBox
from src.utils.asset_loader import AssetLoader
from src.core.audio_manager import AudioManager


class CrispFont:
    """
    Wrapper de fonte em alta definição usando Supersampling (4x) e Smoothscale.
    Garante falas com legibilidade perfeita, bordas nítidas e zero desfoque.
    """
    def __init__(self, font_name: str = "arial", size: int = 10, bold: bool = True, italic: bool = False):
        self.scale_factor = 4
        self.base_size = size
        high_res_size = max(16, size * self.scale_factor)
        self.high_res_font = pygame.font.SysFont(font_name, high_res_size, bold=bold, italic=italic)

    def render(self, text: str, antialias: bool, color: tuple, background=None) -> pygame.Surface:
        if not text:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        high_res_surf = self.high_res_font.render(text, True, color, background)
        target_w = max(1, high_res_surf.get_width() // self.scale_factor)
        target_h = max(1, high_res_surf.get_height() // self.scale_factor)

        return pygame.transform.smoothscale(high_res_surf, (target_w, target_h))

    def size(self, text: str) -> tuple:
        w, h = self.high_res_font.size(text)
        return (max(1, w // self.scale_factor), max(1, h // self.scale_factor))

    def get_linesize(self) -> int:
        return max(1, self.high_res_font.get_linesize() // self.scale_factor)

    def get_height(self) -> int:
        return max(1, self.high_res_font.get_height() // self.scale_factor)

    def get_ascent(self) -> int:
        return max(1, self.high_res_font.get_ascent() // self.scale_factor)

    def get_descent(self) -> int:
        return max(1, self.high_res_font.get_descent() // self.scale_factor)


def find_asset_file(keyword: str, preferred_folders: list = None, valid_exts: list = None) -> str:
    """
    Busca recursivamente por qualquer arquivo cujo nome contenha a palavra-chave.
    """
    if valid_exts is None:
        valid_exts = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]

    if preferred_folders:
        for folder in preferred_folders:
            if not os.path.exists(folder):
                continue
            for root, _, files in os.walk(folder):
                for f in files:
                    name, ext = os.path.splitext(f)
                    if ext.lower() in valid_exts and keyword.lower() in name.lower():
                        return os.path.join(root, f)

    for root, _, files in os.walk(PROJECT_ROOT):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in valid_exts and keyword.lower() in name.lower():
                return os.path.join(root, f)

    return None


def find_audio_file(keyword: str, preferred_folders: list = None) -> str:
    """
    Busca recursivamente por arquivos de áudio (.mp3, .wav, .ogg).
    """
    return find_asset_file(keyword, preferred_folders, valid_exts=[".mp3", ".wav", ".ogg"])


def remove_white_background(surface: pygame.Surface, threshold: int = 240) -> pygame.Surface:
    """
    Remove o fundo branco para sprites que necessitarem.
    """
    surface = surface.convert_alpha()
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = surface.get_at((x, y))
            if r >= threshold and g >= threshold and b >= threshold:
                surface.set_at((x, y), (0, 0, 0, 0))
    return surface


def load_background_image(filename_stem: str, size: tuple = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)) -> pygame.Surface:
    """
    Carrega o plano de fundo do jogo.
    """
    preferred = [
        os.path.join(PROJECT_ROOT, "planosDeFundo"),
        os.path.join(PROJECT_ROOT, "assets", "planosDeFundo"),
        os.path.join(PROJECT_ROOT, "src", "planosDeFundo"),
        os.path.join(PROJECT_ROOT, "assets", "imagensFundo"),
    ]

    found_path = find_asset_file(filename_stem, preferred)

    if found_path:
        try:
            img = pygame.image.load(found_path).convert()
            scaled_img = pygame.transform.smoothscale(img, size)
            print(f"[Cutscene] Plano de fundo '{filename_stem}' carregado com sucesso de: {found_path}")
            return scaled_img
        except Exception as e:
            print(f"[Cutscene] Erro ao carregar plano de fundo {found_path}: {e}")

    fallback = pygame.Surface(size)
    fallback.fill((255, 160, 100))
    return fallback


def load_jumento_sprite(filename_stem: str, size: tuple = (320, 210)) -> pygame.Surface:
    """
    Carrega o sprite do jumento.
    """
    preferred = [
        os.path.join(PROJECT_ROOT, "src", "sprites", "jumento"),
        os.path.join(PROJECT_ROOT, "sprites", "jumento"),
        os.path.join(PROJECT_ROOT, "assets", "sprites", "jumento"),
    ]

    found_path = find_asset_file(filename_stem, preferred)

    if found_path:
        try:
            raw_img = pygame.image.load(found_path)
            clean_img = remove_white_background(raw_img, threshold=235)
            scaled_img = pygame.transform.scale(clean_img, size)
            return scaled_img
        except Exception as e:
            print(f"[Cutscene] Erro ao processar imagem {found_path}: {e}")

    fallback = pygame.Surface(size)
    fallback.fill((204, 119, 34))
    return fallback


def load_paredao_sprite(filename_stem: str = "paredao") -> pygame.Surface:
    """
    Carrega a imagem original do 'paredao' sem qualquer alteração no fundo.
    """
    preferred = [
        os.path.join(PROJECT_ROOT, "src", "sprites"),
        os.path.join(PROJECT_ROOT, "sprites"),
        os.path.join(PROJECT_ROOT, "assets", "sprites"),
    ]

    found_path = find_asset_file(filename_stem, preferred)

    if found_path:
        try:
            img = pygame.image.load(found_path).convert_alpha()
            print(f"[Cutscene] Retrato '{filename_stem}' carregado em estado original de: {found_path}")
            return img
        except Exception as e:
            print(f"[Cutscene] Erro ao carregar retrato {found_path}: {e}")

    return None


class CutsceneScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.dialogue_box = DialogueBox()
        self.audio_manager = AudioManager()
        self.next_scene = "LEVEL_1"
        self.anim_timer = 0.0

        # Carrega o efeito sonoro 'jum'
        self.jum_sfx = None
        preferred_sfx_folders = [
            os.path.join(PROJECT_ROOT, "src", "audio", "efeitosSonoros"),
            os.path.join(PROJECT_ROOT, "src", "audios", "efeitosSonoros"),
            os.path.join(PROJECT_ROOT, "audio", "efeitosSonoros"),
            os.path.join(PROJECT_ROOT, "audios", "efeitosSonoros"),
            os.path.join(PROJECT_ROOT, "efeitosSonoros"),
        ]
        jum_path = find_audio_file("jum", preferred_sfx_folders)
        if jum_path:
            try:
                self.jum_sfx = pygame.mixer.Sound(jum_path)
                print(f"[Cutscene] Efeito sonoro 'jum' carregado de: {jum_path}")
            except Exception as e:
                print(f"[Cutscene] Erro ao carregar efeito sonoro jum: {e}")

        # Busca do áudio de fundo da cutscene (mscFundo)
        preferred_music_folders = [
            os.path.join(PROJECT_ROOT, "src", "audio", "mscFundo"),
            os.path.join(PROJECT_ROOT, "src", "audios", "mscFundo"),
            os.path.join(PROJECT_ROOT, "audio", "mscFundo"),
            os.path.join(PROJECT_ROOT, "audios", "mscFundo"),
            os.path.join(PROJECT_ROOT, "mscFundo"),
        ]
        self.cutscene_music_path = find_audio_file("cutscene", preferred_music_folders)

        # Aplica fontes de alta resolução (HD Supersampling) nas falas da DialogueBox
        crisp_text_font = CrispFont("arial", 10, bold=True)
        crisp_speaker_font = CrispFont("arial", 11, bold=True)

        for attr in ['font', 'text_font', 'font_text', 'dialogue_font', 'font_dialogue', 'main_font']:
            if hasattr(self.dialogue_box, attr):
                setattr(self.dialogue_box, attr, crisp_text_font)

        for attr in ['speaker_font', 'font_speaker', 'title_font', 'name_font', 'header_font']:
            if hasattr(self.dialogue_box, attr):
                setattr(self.dialogue_box, attr, crisp_speaker_font)

        for key, value in list(self.dialogue_box.__dict__.items()):
            if isinstance(value, pygame.font.Font):
                if "speaker" in key.lower() or "title" in key.lower() or "name" in key.lower():
                    setattr(self.dialogue_box, key, crisp_speaker_font)
                else:
                    setattr(self.dialogue_box, key, crisp_text_font)

        self.font_skip = CrispFont("arial", 9, bold=False, italic=True)

        # Carrega o plano de fundo
        self.bg_surf = load_background_image("cutscene", size=(VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

        # Carrega os sprites do jumento
        self.jumento_frames = [
            load_jumento_sprite("jumento1", size=(320, 210)),
            load_jumento_sprite("jumento2", size=(320, 210))
        ]

        # Carrega a imagem intacta do paredão
        self.paredao_img = load_paredao_sprite("paredao")

    def on_enter(self, **kwargs):
        self.next_scene = kwargs.get("next_scene", "LEVEL_1")
        self.anim_timer = 0.0

        # Toca a música da cutscene em LOOP
        if self.cutscene_music_path and os.path.exists(self.cutscene_music_path):
            try:
                pygame.mixer.music.load(self.cutscene_music_path)
                pygame.mixer.music.play(-1)  # Loop infinito durante a cutscene
                print(f"[Cutscene] Trilha sonora tocando em loop: {self.cutscene_music_path}")
            except Exception as e:
                print(f"[Cutscene] Erro ao carregar/tocar áudio de fundo: {e}")

        # Toca o áudio 'jum' em LOOP juntamente com a música
        if self.jum_sfx:
            try:
                self.jum_sfx.play(-1)  # Loop infinito durante a cutscene
                print("[Cutscene] Áudio 'jum' tocando em loop simultâneo.")
            except Exception as e:
                print(f"[Cutscene] Erro ao tocar áudio jum em loop: {e}")

        intro_dialogues = [
            "Perto da casa do fi de chico lá na Caruaru, a bichinha 'Catita' tumouse fim!",
            "A cumadi fulorzinha deixou um moi de atrapaiada e mandacaru por todo cantu.",
            "Lampião abota seu chapé de coro, e cuma sua coragi é aprumada vai busca a Catita!",
            "te arruma que a proza no sertão vai ser pra lá de boa!"
        ]

        self.dialogue_box.start_dialogue(
            speaker_name="NARRADOR DO SERTÃO",
            pages=intro_dialogues,
            on_complete=self.finish_cutscene,
            portrait_label=""
        )

    def finish_cutscene(self):
        # Para a música e o efeito 'jum' imediatamente
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        if self.jum_sfx:
            try:
                self.jum_sfx.stop()
            except Exception:
                pass

        if self.scene_manager:
            self.scene_manager.change_scene(self.next_scene)

    def on_exit(self):
        # Garante que os áudios parem caso a cena mude por outro meio
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        if self.jum_sfx:
            try:
                self.jum_sfx.stop()
            except Exception:
                pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.finish_cutscene()
                    return

        self.dialogue_box.handle_events(events)

    def update(self, dt: float):
        self.anim_timer += dt
        self.dialogue_box.update(dt)

    def render(self, screen: pygame.Surface):
        # 1. Renderiza o fundo da cutscene
        screen.blit(self.bg_surf, (0, 0))

        # 2. Renderiza o jumento rebaixado
        frame_idx = int(self.anim_timer * 6.0) % len(self.jumento_frames)
        current_jumento = self.jumento_frames[frame_idx]

        center_x = (VIRTUAL_WIDTH // 2) - 20
        prop_y = int(138 + math.sin(self.anim_timer * 3.0) * 4.0)

        p_rect = current_jumento.get_rect(center=(center_x, prop_y))
        screen.blit(current_jumento, p_rect)

        # 3. Renderiza a instrução de Pular Cutscene em alta definição
        skip_txt = self.font_skip.render("Pressione [ESC] para Pular Cutscene", True, COLOR_WHITE)
        screen.blit(skip_txt, (VIRTUAL_WIDTH - 155, 10))

        # 4. Renderiza a caixa de diálogo base
        self.dialogue_box.render(screen)

        # 5. Posicionamento do 'paredao' deslocado para CIMA e para a DIREITA
        portrait_x = 34                    # Deslocado mais para a direita
        portrait_y = VIRTUAL_HEIGHT - 71   # Subido na vertical
        portrait_w = 46
        portrait_h = 46

        # Fundo de cobertura
        pygame.draw.rect(screen, (25, 20, 30), (portrait_x, portrait_y, portrait_w, portrait_h), border_radius=3)
        pygame.draw.rect(screen, (180, 140, 80), (portrait_x, portrait_y, portrait_w, portrait_h), width=1, border_radius=3)

        # Renderiza o paredão original perfeitamente enquadrado
        if self.paredao_img:
            scaled_paredao = pygame.transform.scale(self.paredao_img, (portrait_w - 4, portrait_h - 4))
            p_rect = scaled_paredao.get_rect(center=(portrait_x + portrait_w // 2, portrait_y + portrait_h // 2))
            screen.blit(scaled_paredao, p_rect)