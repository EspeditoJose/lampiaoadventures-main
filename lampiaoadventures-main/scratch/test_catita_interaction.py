import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
screen = pygame.display.set_mode((640, 360))

from src.entities.catita import Catita
from src.entities.player import Player
from src.core.camera import Camera
from src.level.level_manager import LevelManager

# 1. Test Catita proximity check & prompt rendering
catita = Catita(7150.0, 512.0)
player = Player(7140.0, 512.0)
camera = Camera()

is_near = catita.is_player_near(player)
print("Is player near Catita:", is_near)
assert is_near, "Player should be near Catita when standing next to her!"

# Test prompt rendering without crash
catita.render_prompt(screen, camera)
print("Rendered Catita prompt successfully!")

# 2. Test LevelManager contains Catita at end of map
lm = LevelManager()
print("LevelManager catita pos:", (lm.catita.pos.x, lm.catita.pos.y))
assert lm.catita is not None, "LevelManager must contain Catita!"
assert lm.catita.pos.x > 7000, "Catita must be placed near end of map (>7000px)!"

print("Catita interaction & placement test passed 100% successfully!")
