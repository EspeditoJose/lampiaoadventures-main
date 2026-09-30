"""
Scene Manager.
State Machine handling transitions between scenes (Menu, Level, Cutscene).
"""

import pygame

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.current_scene_name = ""

    def register_scene(self, name: str, scene_instance):
        """Registers a scene instance in the manager."""
        self.scenes[name] = scene_instance
        scene_instance.scene_manager = self

    def change_scene(self, name: str, **kwargs):
        """Switches to named scene, executing exit/enter hooks."""
        if self.current_scene and hasattr(self.current_scene, 'on_exit'):
            self.current_scene.on_exit()

        if name in self.scenes:
            self.current_scene_name = name
            self.current_scene = self.scenes[name]
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter(**kwargs)
        else:
            print(f"[SceneManager] Error: Scene '{name}' not registered.")

    def handle_events(self, events):
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)

    def render(self, screen: pygame.Surface):
        if self.current_scene:
            self.current_scene.render(screen)
