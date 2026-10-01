"""
Verification test for NPC Bemzedor idle animation, pray blessing animation, player locking, and 35% health restoration.
"""

import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.abspath("."))

from src.entities.player import Player
from src.entities.npc import NPC
from src.scenes.level_scene import LevelScene

def test_bemzedor_mechanics():
    print("[Test] Initializing Pygame & LevelScene...")
    pygame.init()
    pygame.display.set_mode((1, 1))

    level_scene = LevelScene()
    level_scene.on_enter()

    player = level_scene.player
    
    # Find Bemzedor NPC
    bemzedor = None
    for npc in level_scene.level_manager.npcs:
        if "bemzedor" in npc.name.lower():
            bemzedor = npc
            break

    assert bemzedor is not None, "Bemzedor NPC not found in level!"
    print(f"[Test] Found NPC: {bemzedor.name} at pos {bemzedor.pos}")

    # Check 1: Idle Frames loaded
    assert bemzedor.idle_frames is not None, "Bemzedor idle frames failed to load!"
    assert len(bemzedor.idle_frames) == 7, f"Expected 7 idle frames, got {len(bemzedor.idle_frames)}"
    assert bemzedor.pray_frames is not None, "Bemzedor pray frames failed to load!"
    assert len(bemzedor.pray_frames) == 16, f"Expected 16 pray frames, got {len(bemzedor.pray_frames)}"
    print("[Test] Idle (7 frames) and Pray (16 frames) loaded successfully!")

    # Check 2: Player health damage before blessing
    player.health = 40  # 40/100 HP
    initial_health = player.health
    print(f"[Test] Initial Player Health: {initial_health}/{player.max_health}")

    # Check 3: Trigger dialogue completion callback
    bemzedor.on_dialogue_complete(player)

    assert player.is_locked == True, "Player should be locked during pray blessing!"
    expected_healed_hp = min(player.max_health, initial_health + int(player.max_health * 0.35))
    assert player.health == expected_healed_hp, f"Expected health {expected_healed_hp}, got {player.health}"
    assert bemzedor.anim_state == "PRAY", "NPC should be in PRAY anim state!"
    print(f"[Test] Player locked: {player.is_locked}, Healed Health: {player.health}/{player.max_health}")

    # Check 4: Simulate update loop while praying
    print("[Test] Simulating pray animation progression...")
    # Pray animation is 16 frames at 8 FPS = 2.0 seconds.
    # Advance by 1.0s (halfway)
    dt = 0.1
    for _ in range(10): # 1.0s
        bemzedor.update(dt, [], player)
        player.update(dt, [])

    assert bemzedor.anim_state == "PRAY", "NPC should still be praying halfway through!"
    assert player.is_locked == True, "Player should still be locked halfway through!"

    # Advance remaining 1.5s to finish animation
    for _ in range(15): # 1.5s
        bemzedor.update(dt, [], player)
        player.update(dt, [])

    # Check 5: Pray animation finished, player unlocked, NPC idle
    assert bemzedor.anim_state == "IDLE", f"NPC should return to IDLE, got {bemzedor.anim_state}"
    assert player.is_locked == False, "Player should be unlocked after pray animation completes!"
    print("[Test] Pray animation finished cleanly! Player unlocked, NPC returned to IDLE.")

    print("[Test] SUCCESS: All Bemzedor NPC mechanics verified!")

if __name__ == "__main__":
    test_bemzedor_mechanics()
