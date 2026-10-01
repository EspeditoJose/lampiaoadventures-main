"""
Splash Transition Overlay.
Displays a centered 'producedby.png' logo on a black screen with smooth fade-in (shade in),
display hold, and fade-out (shade out) transitions.
"""

import os
import pygame
from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT
from src.utils.asset_loader import AssetLoader

class SplashTransition:
    STATE_INACTIVE = "INACTIVE"
    STATE_FADE_IN = "FADE_IN"
    STATE_HOLD = "HOLD"
    STATE_FADE_OUT = "FADE_OUT"

    def __init__(self, logo_path: str = "assets/producedby.png"):
        self.state = SplashTransition.STATE_INACTIVE
        self.state_timer = 0.0
        self.fade_in_duration = 1.0   # seconds
        self.hold_duration = 1.2      # seconds
        self.fade_out_duration = 1.0  # seconds

        self.alpha = 0.0
        self.on_complete_callback = None

        # Load and scale logo to fit nicely centered on screen (180x180 px for virtual width 533x300)
        raw_logo = AssetLoader.load_image(
            relative_path=logo_path,
            size=(180, 180),
            fallback_color=(20, 20, 20),
            label="PRODUCED_BY"
        )
        try:
            self.logo_surface = raw_logo.convert_alpha() if pygame.display.get_surface() is not None else raw_logo
        except Exception:
            self.logo_surface = raw_logo

        self.logo_rect = self.logo_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))

    def trigger(self, on_complete=None):
        """Starts the splash screen transition cycle (Fade-in -> Hold -> Fade-out)."""
        self.state = SplashTransition.STATE_FADE_IN
        self.state_timer = 0.0
        self.alpha = 0.0
        self.on_complete_callback = on_complete

    def is_active(self) -> bool:
        return self.state != SplashTransition.STATE_INACTIVE

    def update(self, dt: float):
        if not self.is_active():
            return

        self.state_timer += dt

        if self.state == SplashTransition.STATE_FADE_IN:
            progress = min(1.0, self.state_timer / self.fade_in_duration)
            self.alpha = progress * 255.0

            if self.state_timer >= self.fade_in_duration:
                self.state = SplashTransition.STATE_HOLD
                self.state_timer = 0.0
                self.alpha = 255.0

        elif self.state == SplashTransition.STATE_HOLD:
            self.alpha = 255.0
            if self.state_timer >= self.hold_duration:
                self.state = SplashTransition.STATE_FADE_OUT
                self.state_timer = 0.0

        elif self.state == SplashTransition.STATE_FADE_OUT:
            progress = min(1.0, self.state_timer / self.fade_out_duration)
            self.alpha = (1.0 - progress) * 255.0

            if self.state_timer >= self.fade_out_duration:
                self.state = SplashTransition.STATE_INACTIVE
                self.alpha = 0.0
                if self.on_complete_callback:
                    callback = self.on_complete_callback
                    self.on_complete_callback = None
                    callback()

    def render(self, screen: pygame.Surface):
        if not self.is_active():
            return

        # 1. Fill solid black background
        screen.fill((0, 0, 0))

        # 2. Render centered logo with dynamic alpha transparency
        temp_logo = self.logo_surface.copy()
        temp_logo.set_alpha(int(self.alpha))
        screen.blit(temp_logo, self.logo_rect)
