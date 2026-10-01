"""
Level Scene (Gameplay).
Integrates Player, LevelManager, Smooth Camera, HUD, and NPC Dialogue system scaled for virtual display.
"""

import pygame
from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW, KEY_PAUSE
from src.scenes.base_scene import BaseScene
from src.entities.player import Player
from src.level.level_manager import LevelManager
from src.core.camera import Camera
from src.ui.hud import HUD
from src.ui.dialogue_box import DialogueBox
from src.ui.splash_transition import SplashTransition
from src.core.audio_manager import AudioManager

from src.level.parallax import ParallaxBackground

class LevelScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
        self.hud = HUD()
        self.dialogue_box = DialogueBox()
        self.splash = SplashTransition()
        self.is_paused = False
        self.game_over = False

        self.font_overlay = pygame.font.SysFont("arial", 22, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 12)

    def on_enter(self, **kwargs):
        """Initializes fresh Level 1 state."""
        self.level_manager = LevelManager()
        spawn_x, spawn_y = self.level_manager.player_spawn
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(width=self.level_manager.level_width, height=self.level_manager.level_height)
        self.parallax = ParallaxBackground("assets/sprites/back2.png", "assets/sprites/back1.png")
        self.is_paused = False
        self.game_over = False
        self.audio_manager.play_music("assets/audio/mscFundo/fase1.wav", fade_ms=2000)

        # Trigger Produced By black splash transition before game starts!
        self.splash.trigger()

    def handle_events(self, events):
        if self.splash.is_active():
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE:
                    self.is_paused = not self.is_paused

                if self.game_over or self.level_manager.level_completed:
                    if event.key in [pygame.K_r, pygame.K_RETURN, pygame.K_SPACE]:
                        self.on_enter()
                    elif event.key == pygame.K_ESCAPE:
                        if self.scene_manager:
                            self.scene_manager.change_scene("MENU")

        if self.dialogue_box.is_active:
            self.dialogue_box.handle_events(events)
        elif not self.is_paused and not self.game_over:
            self.player.handle_input(events)

    def update(self, dt: float):
        if self.splash.is_active():
            self.splash.update(dt)
            return

        if self.is_paused or self.game_over:
            return

        if self.dialogue_box.is_active:
            self.dialogue_box.update(dt)
            return

        if self.player.health <= 0:
            self.game_over = True
            return

        if self.level_manager.level_completed:
            return

        all_enemies = list(self.level_manager.enemies)
        if self.level_manager.vaca_mojada:
            all_enemies.append(self.level_manager.vaca_mojada)

        self.player.update(dt, self.level_manager.solid_tiles, enemies=all_enemies)
        self.level_manager.update(dt, self.player, self.camera)
        self.camera.update(self.player.rect)

        # Check interaction with Catita at the end of the map ([E] key returns to menu)
        catita = self.level_manager.catita
        if catita and catita.is_player_near(self.player):
            if self.player.interact_pressed:
                self.player.interact_pressed = False
                self.audio_manager.fadeout_music(1000)
                if self.scene_manager:
                    self.scene_manager.change_scene("MENU")
                return

        for npc in self.level_manager.npcs:
            if npc.is_player_near(self.player):
                if self.player.interact_pressed:
                    is_jegue = npc.label in ["JEGUE", "ZE_CHAPEU"] or "jegue" in npc.name.lower() or "zé" in npc.name.lower()
                    if is_jegue:
                        # Fade in cutscene music when talking to Jegue
                        self.audio_manager.play_music("assets/audio/mscFundo/cutscene.mp3", fade_ms=1500)

                    def handle_dialogue_complete(target_npc=npc, was_jegue=is_jegue):
                        target_npc.on_dialogue_complete(self.player)
                        # Fade out cutscene music and fade in stage 1 music when completing dialogue with Jegue!
                        if was_jegue:
                            self.audio_manager.fadeout_music(1500)
                            self.audio_manager.play_music("assets/audio/mscFundo/fase1.wav", fade_ms=1500)
                            self.splash.trigger()

                    self.dialogue_box.start_dialogue(
                        speaker_name=npc.name,
                        pages=npc.dialogue_pages,
                        on_complete=handle_dialogue_complete,
                        portrait_label=npc.label
                    )
                    self.player.interact_pressed = False
                    break

    def render(self, screen: pygame.Surface):
        # Render Parallax Background (back2 behind, back1 in front of back2)
        self.parallax.render(screen, self.camera.camera_rect.x)

        self.level_manager.render(screen, self.camera)
        self.player.render(screen, self.camera)

        if not self.dialogue_box.is_active:
            for npc in self.level_manager.npcs:
                if npc.is_player_near(self.player):
                    npc.render_prompt(screen, self.camera)

            if self.level_manager.catita and self.level_manager.catita.is_player_near(self.player):
                self.level_manager.catita.render_prompt(screen, self.camera)

        self.hud.render(screen, self.player)

        if self.dialogue_box.is_active:
            self.dialogue_box.render(screen)

        if self.game_over:
            self._render_overlay(screen, "GAME OVER!", "Você tombou no sertão. Pressione [R] para Tentar Novamente ou [ESC] para Menu.")
        elif self.level_manager.level_completed:
            self._render_overlay(screen, "VILA FINAL ALCANÇADA!", f"Parabéns! Você resgatou a Catita com {self.player.coins_collected} moedas! Pressione [R] para Jogar Novamente.")
        elif self.is_paused:
            self._render_overlay(screen, "JOGO PAUSADO", "Pressione [ESC] ou [P] para Continuar.")

        # Render Splash Transition overlay if active (black screen with producedby.png fade in/out)
        if self.splash.is_active():
            self.splash.render(screen)

    def _render_overlay(self, screen: pygame.Surface, title: str, subtitle: str):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        screen.blit(overlay, (0, 0))

        title_txt = self.font_overlay.render(title, True, COLOR_STAMINA_YELLOW)
        t_rect = title_txt.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 15))
        screen.blit(title_txt, t_rect)

        sub_txt = self.font_sub.render(subtitle, True, COLOR_WHITE)
        s_rect = sub_txt.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 15))
        screen.blit(sub_txt, s_rect)
