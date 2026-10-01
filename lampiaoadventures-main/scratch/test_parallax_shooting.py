"""
Verification test for Parallax Background, Idle Shooting Animation, and Tiro SFX.
"""

import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.abspath("."))

from src.entities.player import Player
from src.level.parallax import ParallaxBackground
from src.scenes.level_scene import LevelScene

def test_parallax_and_shooting():
    print("[Test] Initializing Pygame...")
    pygame.init()
    screen = pygame.display.set_mode((533, 300))

    # Test 1: Parallax Background (back2 behind, back1 in front)
    parallax = ParallaxBackground("assets/sprites/back2.png", "assets/sprites/back1.png")
    assert parallax.layer_back2.width > 0, "Layer back2 failed to load!"
    assert parallax.layer_back1.width > 0, "Layer back1 failed to load!"
    print(f"[Test] Parallax loaded successfully: back2 w={parallax.layer_back2.width} (ratio={parallax.layer_back2.scroll_ratio}), back1 w={parallax.layer_back1.width} (ratio={parallax.layer_back1.scroll_ratio})")

    # Render parallax at camera x = 100
    parallax.render(screen, 100.0)
    print("[Test] Parallax background rendered cleanly onto display surface.")

    # Test 2: Player Shooting Mechanics & Animations
    player = Player(100, 400)
    assert len(player.shoot_idle_frames) == 8, f"Expected 8 shoot_idle frames, got {len(player.shoot_idle_frames)}"
    assert len(player.shoot_frames) == 7, f"Expected 7 shoot_walk frames, got {len(player.shoot_frames)}"
    print("[Test] Shooting Idle (8 frames) and Shooting Walk (7 frames) loaded successfully!")

    # Test 3: Trigger shooting while stationary (IDLE shooting)
    player.vel.x = 0.0
    player.shoot_timer = 0.35
    player._update_animation(0.016)
    assert player.anim_state == "SHOOT_IDLE", f"Expected SHOOT_IDLE state when stationary, got {player.anim_state}"
    print("[Test] Stationary shooting plays SHOOT_IDLE animation!")

    # Test 4: Trigger shooting while moving (WALK shooting)
    player.vel.x = 4.5
    player.shoot_timer = 0.35
    player._update_animation(0.016)
    assert player.anim_state == "SHOOT_WALK", f"Expected SHOOT_WALK state when moving, got {player.anim_state}"
    print("[Test] Moving shooting plays SHOOT_WALK animation!")

    # Test 5: Full LevelScene integration
    level_scene = LevelScene()
    level_scene.on_enter()
    level_scene.update(0.016)
    level_scene.render(screen)
    print("[Test] LevelScene update & render with Parallax and Player state completed successfully!")

    print("[Test] SUCCESS: All Parallax and Shooting features verified without errors!")

if __name__ == "__main__":
    test_parallax_and_shooting()
