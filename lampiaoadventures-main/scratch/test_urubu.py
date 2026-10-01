import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.entities.urubu_do_pix import UrubuDoPix
from src.entities.player import Player
from src.core.camera import Camera

urubu = UrubuDoPix(delay_seconds=2.0, fly_speed=500.0)
player = Player(150.0, 500.0)
camera = Camera()

print("Initial active:", urubu.is_active)
print("Initial triggered:", urubu.is_triggered)
print("Initial sound played:", urubu.has_played_sound)

# Update before delay
urubu.update(1.0, player, camera, level_width=500.0)
print("After 1s (before delay expiry), triggered:", urubu.is_triggered)

# Update past delay
urubu.update(1.5, player, camera, level_width=500.0)
print("After delay expiry, triggered:", urubu.is_triggered)
print("Sound played:", urubu.has_played_sound)

# Update several frames to simulate flight across screen
for _ in range(30):
    urubu.update(0.1, player, camera, level_width=500.0)

print("Finished:", urubu.has_finished)
print("Active after passing:", urubu.is_active)

assert urubu.has_played_sound, "Sound should have played!"
assert urubu.has_finished, "Urubu should have finished its single pass!"
assert not urubu.is_active, "Urubu should be inactive after passing!"

print("Urubu test passed successfully!")
