import sys
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.getcwd())

def test_tanajura_flying_entrance():
    pygame.init()
    pygame.display.set_mode((800, 600))

    from src.entities.enemy import TanajuraEnemy
    from src.entities.player import Player
    from src.level.tile import Tile

    print("--- 1. Testing Tanajura Enemy Spawn & Flying Entrance ---")
    target_y = 512.0
    tanajura = TanajuraEnemy(x=350, y=target_y, patrol_dist=100)
    player = Player(100, 520)

    assert tanajura.state == "FLYING_DESCENT", f"Expected FLYING_DESCENT state on spawn, got {tanajura.state}"
    assert tanajura.pos.y == target_y - 300.0, f"Expected spawn Y at top of screen ({target_y - 300.0}), got {tanajura.pos.y}"
    assert len(tanajura.fly_frames) == 3, f"Expected 3 flying frames, got {len(tanajura.fly_frames)}"
    assert tanajura.fly_anim_fps == 24.0, f"Expected fast wing flutter 24 FPS, got {tanajura.fly_anim_fps}"
    print("[PASS] Tanajura spawned high above screen in FLYING_DESCENT state with 24 FPS animation!")

    print("\n--- 2. Testing Flying Descent Animation & Movement ---")
    initial_y = tanajura.pos.y
    tanajura.update_ai(0.1, player, [])
    assert tanajura.pos.y > initial_y, f"Expected Y position to descend downward, got {tanajura.pos.y}"
    assert tanajura.state == "FLYING_DESCENT", f"Expected to stay in FLYING_DESCENT state until landing, got {tanajura.state}"
    print("[PASS] Tanajura flying downward smoothly!")

    print("\n--- 3. Testing Landing Transition to PATROL State ---")
    ground_tile = Tile(x=300, y=544, width=200, height=32, tile_type=Tile.TYPE_SOLID)
    
    # Simulate update steps until reaching ground
    for _ in range(100):
        if tanajura.state == "FLYING_DESCENT":
            tanajura.update_ai(0.1, player, [ground_tile])
        else:
            break

    assert tanajura.state == "PATROL", f"Expected PATROL state after landing, got {tanajura.state}"
    assert tanajura.pos.y <= target_y, f"Expected Y position landed at ground level, got {tanajura.pos.y}"
    print(f"[PASS] Tanajura landed on ground (y={tanajura.pos.y:.1f}) and transitioned to PATROL state!")

    print("\n--- 4. Testing Ground Walking Patrol after Landing ---")
    initial_x = tanajura.pos.x
    tanajura.update_ai(0.1, player, [ground_tile])
    assert tanajura.pos.x != initial_x, "Expected Tanajura to walk horizontally in PATROL state!"
    print("[PASS] Tanajura walking normally on ground after landing!")

    print("\nALL TANAJURA FLYING ENTRANCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_tanajura_flying_entrance()
