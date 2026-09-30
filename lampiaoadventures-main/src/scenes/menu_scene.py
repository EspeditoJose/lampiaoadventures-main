"""
Main Menu Scene.
Handles title screen display and transition to Cutscene / Level 1.
"""

import sys
import pygame
from src.scenes.base_scene import BaseScene
from src.ui.menu_ui import MenuUI
from src.core.audio_manager import AudioManager

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
        self.menu_ui = MenuUI(
            start_callback=self.start_game,
            quit_callback=self.quit_game
        )

    def on_enter(self, **kwargs):
        self.audio_manager.play_music("assets/audio/music/menu_theme.wav")

    def start_game(self):
        if self.scene_manager:
            # Transition to opening cutscene or direct level play
            self.scene_manager.change_scene("CUTSCENE", next_scene="LEVEL_1")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, events):
        self.menu_ui.handle_events(events)

    def update(self, dt: float):
        self.menu_ui.update(dt)

    def render(self, screen: pygame.Surface):
        self.menu_ui.render(screen)
