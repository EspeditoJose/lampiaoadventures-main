"""
Game Engine.
Initializes Pygame subsystem, window display, game clock, virtual surface scaling, and main loop.
"""

import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, VIRTUAL_WIDTH, VIRTUAL_HEIGHT, RENDER_SCALE, FPS, TITLE, COLOR_BACKGROUND
from src.core.scene_manager import SceneManager
from src.core.audio_manager import AudioManager

class Engine:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[Engine] Warning: Could not initialize mixer: {e}")

        pygame.font.init()

        # Window Screen & Internal Virtual Screen for Zoom Scaling
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = FPS

        self.scene_manager = SceneManager()
        self.audio_manager = AudioManager()

    def run(self):
        """Main game loop."""
        self.running = True
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0

            raw_events = pygame.event.get()
            scaled_events = []

            for event in raw_events:
                if event.type == pygame.QUIT:
                    self.running = False

                # Scale mouse positions to virtual resolution
                if hasattr(event, 'pos'):
                    event_dict = event.__dict__.copy()
                    v_x = int(event.pos[0] / RENDER_SCALE)
                    v_y = int(event.pos[1] / RENDER_SCALE)
                    event_dict['pos'] = (v_x, v_y)
                    scaled_events.append(pygame.event.Event(event.type, event_dict))
                else:
                    scaled_events.append(event)

            # Delegate event handling, update, and rendering to active scene
            self.scene_manager.handle_events(scaled_events)
            self.scene_manager.update(dt)

            # Render to virtual screen
            self.virtual_screen.fill(COLOR_BACKGROUND)
            self.scene_manager.render(self.virtual_screen)

            # Upscale virtual screen to main window
            scaled_display = pygame.transform.scale(self.virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled_display, (0, 0))

            pygame.display.flip()

        self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()
