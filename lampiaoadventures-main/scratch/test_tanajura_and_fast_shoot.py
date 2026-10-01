import sys
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.getcwd())

def test_tanajura_and_fast_shooting():
    pygame.init()
    pygame.display.set_mode((800, 600))

    from src.entities.player import Player
    from src.entities.enemy import TanajuraEnemy
    from src.level.level_manager import LevelManager

    print("[Test] Initializing Pygame...")

    # Test 1: Player Faster Shooting Cooldown & FPS
    player = Player(100, 520)
    assert player.shoot_cooldown == 0.22, f"Expected shoot_cooldown = 0.22s, got {player.shoot_cooldown}"
    assert player.shoot_anim_fps == 32.0, f"Expected shoot_anim_fps = 32.0, got {player.shoot_anim_fps}"
    print("[Test] Player faster shooting cadence configured: 0.22s cooldown (~4.5 shots/sec) & 32 FPS animation.")

    # Test 2: Tanajura Assets & Flying/Walking Frames
    tanajura = TanajuraEnemy(x=350, y=512, patrol_dist=100)
    assert tanajura.static_surf is not None, "Tanajura static surface failed to load!"
    assert len(tanajura.fly_frames) == 3, f"Expected 3 flying frames, got {len(tanajura.fly_frames)}"
    assert len(tanajura.walk_frames) == 4, f"Expected 4 walking frames, got {len(tanajura.walk_frames)}"
    print("[Test] Tanajura flying (3 frames) & walking (4 frames) animation loaded successfully!")

    # Test 3: Tanajura Entrance & Walking AI Update
    for _ in range(100):
        tanajura.update_ai(0.1, player, [])

    assert tanajura.state == "PATROL", "Tanajura should land and enter PATROL state!"
    assert tanajura.vel.x != 0, "Tanajura should be walking/patrolling after landing!"
    print("[Test] Tanajura flying entrance and walking AI updated successfully.")

    # Test 4: LevelManager spawn check (Tanajura at start of level)
    level_mgr = LevelManager()
    tanajura_found = any(isinstance(e, TanajuraEnemy) for e in level_mgr.enemies)
    assert tanajura_found, "Tanajura enemy should be present in Level 1!"

    print("[Test] SUCCESS: Tanajura Flying Entrance and Faster Shooting features verified without errors!")

if __name__ == "__main__":
    test_tanajura_and_fast_shooting()
