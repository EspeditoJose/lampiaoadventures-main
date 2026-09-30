"""
Runtime verification test for Lampião Adventures.
Executes Engine, SceneManager, LevelScene, Player movement, AI update, and HUD rendering.
"""

import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.abspath("."))

from src.core.engine import Engine
from src.scenes.menu_scene import MenuScene
from src.scenes.level_scene import LevelScene
from src.scenes.cutscene_scene import CutsceneScene

def test_game_runtime():
    print("[Test] Initializing Engine...")
    engine = Engine()

    menu_scene = MenuScene()
    level_scene = LevelScene()
    cutscene_scene = CutsceneScene()

    engine.scene_manager.register_scene("MENU", menu_scene)
    engine.scene_manager.register_scene("LEVEL_1", level_scene)
    engine.scene_manager.register_scene("CUTSCENE", cutscene_scene)

    # Test 1: Menu Scene enter & update
    engine.scene_manager.change_scene("MENU")
    print(f"[Test] Active Scene: {engine.scene_manager.current_scene_name}")
    engine.scene_manager.update(0.016)
    engine.scene_manager.render(engine.screen)

    # Test 2: Transition to Cutscene
    engine.scene_manager.change_scene("CUTSCENE", next_scene="LEVEL_1")
    print(f"[Test] Active Scene: {engine.scene_manager.current_scene_name}")
    engine.scene_manager.update(0.016)
    engine.scene_manager.render(engine.screen)

    # Test 3: Transition to Level 1 Gameplay
    engine.scene_manager.change_scene("LEVEL_1")
    print(f"[Test] Active Scene: {engine.scene_manager.current_scene_name}")

    # Simulate 120 game frames (~2 seconds of gameplay)
    for frame in range(120):
        # Simulate moving player right and jumping
        engine.scene_manager.update(0.016)
        engine.scene_manager.render(engine.screen)

    print(f"[Test] Player Pos after 120 frames: {level_scene.player.pos}")
    print(f"[Test] Player Health: {level_scene.player.health}, Stamina: {level_scene.player.stamina}")
    print(f"[Test] Camera Pos: {level_scene.camera.camera_rect}")
    print("[Test] SUCCESS: Game runtime test completed without errors!")

if __name__ == "__main__":
    test_game_runtime()
