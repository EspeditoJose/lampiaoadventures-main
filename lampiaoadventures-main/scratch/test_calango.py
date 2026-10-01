import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.entities.enemy import CalangoEnemy, ChaserEnemy
from src.entities.player import Player

calango = CalangoEnemy(100.0, 500.0)
player = Player(150.0, 500.0)

print("Calango label:", calango.label)
print("Patrol speed:", calango.patrol_speed)
print("Chase speed:", calango.chase_speed)
print("Chase frames loaded:", len(calango.chase_frames))

assert calango.patrol_speed == 1.2, f"Expected patrol_speed 1.2, got {calango.patrol_speed}"
assert calango.chase_speed == 2.2, f"Expected chase_speed 2.2, got {calango.chase_speed}"
assert len(calango.chase_frames) == 6, f"Expected 6 chase frames, got {len(calango.chase_frames)}"

# Test AI update and animation frame advancement
calango.update_ai(0.1, player, [])
print("State after player close:", calango.state)
print("Frame index:", calango.current_frame_idx)
assert calango.state == "CHASE", "Calango should chase player when close!"

# Test ChaserEnemy alias
alias_enemy = ChaserEnemy(200.0, 500.0)
assert isinstance(alias_enemy, CalangoEnemy), "ChaserEnemy must be an alias to CalangoEnemy!"

print("Calango enemy test passed 100% successfully!")
