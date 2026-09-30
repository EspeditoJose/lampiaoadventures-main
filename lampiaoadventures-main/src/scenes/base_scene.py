"""
Base Scene Abstract Class.
Defines mandatory interface for all game scenes.
"""

import pygame
from abc import ABC, abstractmethod

class BaseScene(ABC):
    def __init__(self):
        self.scene_manager = None

    def on_enter(self, **kwargs):
        """Hook called when scene becomes active."""
        pass

    def on_exit(self):
        """Hook called when leaving scene."""
        pass

    @abstractmethod
    def handle_events(self, events):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        pass
