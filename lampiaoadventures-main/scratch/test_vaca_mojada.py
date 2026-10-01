import sys
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.getcwd())

def test_vaca_mojada_fixed_flow():
    pygame.init()
    pygame.display.set_mode((800, 600))

    from config import VIRTUAL_WIDTH
    from src.entities.player import Player
    from src.entities.vaca_mojada import VacaMojada
    from src.level.tile import Tile
    from src.core.camera import Camera

    print("--- 1. Testing Vaca Mojada Rendering Direction ---")
    vaca = VacaMojada(x=2800, y=512, trigger_x=2700)
    camera = Camera()
    camera.camera_rect.x = 2600

    vaca.start_rush(camera, force_direction=-1, from_spawn=True)
    assert vaca.direction == -1, "Direction should be -1 for left movement"

    vaca.start_rush(camera, force_direction=1, from_spawn=True)
    assert vaca.direction == 1, "Direction should be 1 for right movement"
    print("[PASS] Vaca Mojada direction state correctly set for left (-1) and right (1) movement!")

    print("\n--- 2. Testing High Platform Filtering (No Landing on Elevated Platforms) ---")
    vaca = VacaMojada(x=2800, y=512, trigger_x=2700)
    vaca.state = VacaMojada.STATE_RUSHING
    vaca.direction = -1
    vaca.pos.x = 2800.0
    vaca.pos.y = 480.0
    vaca.update_rect()

    # High floating platform at y=480 (label PLAT_M)
    high_plat = Tile(x=2700, y=480, width=200, height=32, tile_type=Tile.TYPE_SOLID, label="PLAT_M")
    # Ground floor tile at y=544
    ground_floor = Tile(x=2700, y=544, width=200, height=32, tile_type=Tile.TYPE_SOLID, label="GRASS_M")

    player = Player(100, 520)
    # Update boss with floating platform and ground floor
    vaca.update_boss(0.1, player, camera, [high_plat, ground_floor])

    # Vaca should ignore high floating platform y=480 and land on ground floor y=544 (pos.y = 480.0, bottom = 544)
    assert vaca.rect.bottom == 544, f"Expected bottom at ground floor 544, got {vaca.rect.bottom}"
    print("[PASS] Vaca Mojada ignores high floating platforms and stays on ground floor (y=544)!")

    print("\n--- 3. Testing Abyss / Pit Fall Safety Recovery ---")
    vaca = VacaMojada(x=2800, y=512, trigger_x=2700)
    vaca.state = VacaMojada.STATE_RUSHING
    vaca.pos.y = 650.0  # Simulated abyss fall past 640px

    vaca.update_boss(0.1, player, camera, [])
    # Should automatically recover state to WAITING_RUSH with 7s timer so she never disappears permanently
    assert vaca.state == VacaMojada.STATE_WAITING_RUSH, f"Expected state WAITING_RUSH after abyss fall, got {vaca.state}"
    assert abs(vaca.cooldown_timer - 7.0) < 0.1, f"Expected 7.0s cooldown timer, got {vaca.cooldown_timer}"
    print("[PASS] Abyss pit fall automatically recovers Vaca Mojada to 7s cooldown timer!")

    print("\nALL VACA MOJADA BUG FIX TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_vaca_mojada_fixed_flow()
